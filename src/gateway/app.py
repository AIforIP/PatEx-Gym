from __future__ import annotations

import asyncio
import html
import json
import os
import re
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import httpx

from .config import AppConfig, load_config
from .anthropic_compat import (
    anthropic_request_to_openai,
    openai_response_to_anthropic,
    openai_stream_to_anthropic_chunks,
)
from .logger import append_jsonl, configure_logging, write_json
from .model_io import save_model_io
from .models import RequestMeta, utc_now
from .proxy import forward_headers, forward_request, response_metadata
from .trajectory import update_trajectory


config: AppConfig = load_config()
log = configure_logging(config.gateway.log_dir)
app = FastAPI(title="Claude Code Gateway", version="2.0")
MAX_INTERACTION_TURNS = max(1, int(os.environ.get("MAX_INTERACTION_TURNS", "50")))
MODEL_MAX_OUTPUT_TOKENS = max(1, int(os.environ.get("MODEL_MAX_OUTPUT_TOKENS", "32768")))
AGENT_TEMPERATURE = 1
CHAT_REASONING_EFFORT_ENABLED = os.environ.get(
    "GATEWAY_CHAT_REASONING_EFFORT_ENABLED", "false"
).strip().lower() in {"1", "true", "yes", "on"}
CHAT_REASONING_HISTORY_MODE = os.environ.get(
    "GATEWAY_CHAT_REASONING_HISTORY_MODE", "auto"
).strip().lower()
if CHAT_REASONING_HISTORY_MODE not in {"auto", "preserve", "drop"}:
    raise RuntimeError(
        "GATEWAY_CHAT_REASONING_HISTORY_MODE must be auto, preserve, or drop"
    )
REASONING_MODE = os.environ.get("GATEWAY_REASONING_MODE", "replay").strip().lower()
if REASONING_MODE not in {"replay", "native_passthrough"}:
    raise RuntimeError(
        "GATEWAY_REASONING_MODE must be replay or native_passthrough"
    )
RESPONSES_UPSTREAM_MODE = os.environ.get("GATEWAY_RESPONSES_UPSTREAM_MODE", "responses").strip().lower()
if RESPONSES_UPSTREAM_MODE not in {"responses", "chat"}:
    raise RuntimeError("GATEWAY_RESPONSES_UPSTREAM_MODE must resolve to responses or chat before gateway startup")
TRANSIENT_400_MAX_RETRIES = max(
    0, int(os.environ.get("GATEWAY_TRANSIENT_400_MAX_RETRIES", "2"))
)
TRANSIENT_400_RETRY_BASE_SECONDS = max(
    0.0, float(os.environ.get("GATEWAY_TRANSIENT_400_RETRY_BASE_SECONDS", "1"))
)
CHAT_STREAM_USAGE_MODE = os.environ.get(
    "GATEWAY_CHAT_STREAM_USAGE", "auto"
).strip().lower()
if CHAT_STREAM_USAGE_MODE not in {"auto", "required", "disabled"}:
    raise RuntimeError(
        "GATEWAY_CHAT_STREAM_USAGE must be auto, required, or disabled"
    )
TOOL_CHOICE_OVERRIDE = os.environ.get(
    "GATEWAY_TOOL_CHOICE_OVERRIDE", ""
).strip().lower()
if TOOL_CHOICE_OVERRIDE not in {"", "auto", "required"}:
    raise RuntimeError(
        "GATEWAY_TOOL_CHOICE_OVERRIDE must be empty, auto, or required"
    )
PROVIDER_CONTEXT_WINDOW = max(
    0, int(os.environ.get("GATEWAY_PROVIDER_CONTEXT_WINDOW", "0"))
)
CONTEXT_SAFETY_MARGIN = max(
    0, int(os.environ.get("GATEWAY_CONTEXT_SAFETY_MARGIN", "16384"))
)
_interaction_turn_count = 0
_interaction_turn_lock = asyncio.Lock()
_request_interaction_turns: dict[str, int] = {}
_chat_stream_usage_capability: bool | None = None


def _native_reasoning_metadata(value: dict[str, Any]) -> dict[str, Any]:
    """Return non-sensitive metadata for one opaque native reasoning block."""
    opaque = value.get("encrypted_content")
    if opaque is None:
        opaque = value.get("signature")
    if opaque is None and value.get("type") == "redacted_thinking":
        opaque = value.get("data")
    length = len(opaque) if isinstance(opaque, (str, bytes, list, dict)) else 0
    return {
        "reasoning_type": "native",
        "reasoning_id": value.get("id") or value.get("item_id") or value.get("reasoning_id"),
        "opaque_state_present": opaque is not None,
        "opaque_state_length": length,
    }


def _native_reasoning_log_view(value: Any) -> Any:
    """Remove native reasoning payloads while retaining useful audit metadata.

    This helper is for persistence only. Provider-bound and client-bound values
    must never pass through it.
    """
    if isinstance(value, list):
        return [_native_reasoning_log_view(item) for item in value]
    if not isinstance(value, dict):
        return value

    block_type = value.get("type")
    if isinstance(block_type, str) and block_type.startswith("response.reasoning"):
        return _native_reasoning_metadata(value)
    if block_type in {"reasoning", "thinking", "redacted_thinking"}:
        return _native_reasoning_metadata(value)

    cleaned: dict[str, Any] = {}
    for key, item in value.items():
        if key in {"encrypted_content", "thinking", "signature"}:
            continue
        cleaned[key] = _native_reasoning_log_view(item)
    return cleaned


def _native_sse_log_view(chunks: list[bytes]) -> dict[str, Any]:
    """Build a metadata-only log projection without retaining raw SSE bytes."""
    events: list[Any] = []
    completed_response: Any = None
    for line in b"".join(chunks).decode("utf-8", errors="replace").splitlines():
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if not data or data == "[DONE]":
            continue
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            events.append({"event_type": "unparseable", "byte_length": len(data.encode())})
            continue
        sanitized = _native_reasoning_log_view(event)
        events.append(sanitized)
        if event.get("type") == "response.completed" and isinstance(event.get("response"), dict):
            completed_response = sanitized.get("response")
    return {"stream": True, "events": events, "response": completed_response}


def _json_or_raw(raw: bytes) -> Any:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw.decode("utf-8", errors="replace")}


def _standardize_output_limit(body: Any, field: str) -> tuple[Any, bytes]:
    """Return the exact provider-bound JSON with the configured output cap."""
    if not isinstance(body, dict):
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        return body, raw
    standardized = dict(body)
    for alias in ("max_tokens", "max_completion_tokens", "max_output_tokens"):
        if alias != field:
            standardized.pop(alias, None)
    standardized[field] = MODEL_MAX_OUTPUT_TOKENS
    return standardized, json.dumps(standardized, ensure_ascii=False).encode("utf-8")


def _standardize_agent_request(body: Any, output_limit_field: str) -> tuple[Any, bytes]:
    """Apply experiment-wide inference parameters to a provider-bound agent request."""
    standardized, _ = _standardize_output_limit(body, output_limit_field)
    if isinstance(standardized, dict):
        standardized["temperature"] = AGENT_TEMPERATURE
    return standardized, json.dumps(standardized, ensure_ascii=False).encode("utf-8")


_CODEX_TOOL_OUTPUT_METADATA_RE = re.compile(
    r"\A(?=(?:Chunk ID:|Wall time:|Process exited with code |Original token count:))"
    r"(?:Chunk ID:[^\n]*\n)?"
    r"(?:Wall time:[^\n]*\n)?"
    r"(?:Process exited with code [^\n]*\n)?"
    r"(?:Original token count:[^\n]*\n)?"
    r"(?:Final output:|Output:)\n?",
)


def _strip_codex_tool_output_metadata(value: Any) -> Any:
    """Keep only the actual result from Codex's function-call output wrapper."""
    if not isinstance(value, str):
        return value
    match = _CODEX_TOOL_OUTPUT_METADATA_RE.match(value)
    return value[match.end() :] if match else value


def _sanitize_responses_tool_outputs(body: Any) -> Any:
    """Remove Codex execution metadata before it enters the model context."""
    if not isinstance(body, dict) or not isinstance(body.get("input"), list):
        return body
    sanitized = dict(body)
    items: list[Any] = []
    for item in body["input"]:
        if isinstance(item, dict) and item.get("type") == "function_call_output":
            cleaned = dict(item)
            cleaned["output"] = _strip_codex_tool_output_metadata(item.get("output"))
            items.append(cleaned)
        else:
            items.append(item)
    sanitized["input"] = items
    return sanitized


def _flatten_responses_namespace_tools(body: Any) -> Any:
    """Expose namespaced MCP children as ordinary Responses function tools."""
    if not isinstance(body, dict) or not isinstance(body.get("tools"), list):
        return body
    flattened: list[Any] = []
    changed = False
    for tool in body["tools"]:
        if not isinstance(tool, dict) or tool.get("type") != "namespace":
            flattened.append(tool)
            continue
        changed = True
        flattened.extend(
            dict(child)
            for child in tool.get("tools") or []
            if isinstance(child, dict) and child.get("type") == "function"
        )
    if not changed:
        return body
    normalized = dict(body)
    normalized["tools"] = flattened
    return normalized


def _ensure_responses_tool_choice(body: Any) -> Any:
    """Default native Responses tool routing without changing explicit choices.

    Some Responses clients (notably PI) omit ``tool_choice`` even when tools
    are provided. Native providers expect an explicit automatic routing choice
    in that case. Empty tool lists are left untouched because sending
    ``tool_choice`` without tools is rejected by several providers.
    """
    if not isinstance(body, dict):
        return body
    tools = body.get("tools")
    if not isinstance(tools, list) or not tools or body.get("tool_choice") is not None:
        return body
    normalized = dict(body)
    normalized["tool_choice"] = TOOL_CHOICE_OVERRIDE or "auto"
    return normalized


_DSML_TOOL_CALLS_RE = re.compile(
    r"<｜DSML｜tool_calls>(?P<body>.*?)</｜DSML｜tool_calls>", re.DOTALL
)
_DSML_INVOKE_RE = re.compile(
    r'<｜DSML｜invoke\s+name="(?P<name>[^"]+)">(?P<body>.*?)</｜DSML｜invoke>', re.DOTALL
)
_DSML_PARAMETER_RE = re.compile(
    r'<｜DSML｜parameter\s+name="(?P<name>[^"]+)"\s+string="(?P<string>true|false)">'
    r"(?P<value>.*?)</｜DSML｜parameter>",
    re.DOTALL,
)


def _request_tool_aliases(request_body: Any) -> dict[str, str]:
    if not isinstance(request_body, dict):
        return {}
    aliases: dict[str, str] = {}
    for tool in request_body.get("tools") or []:
        if not isinstance(tool, dict):
            continue
        if tool.get("type") == "namespace" and isinstance(tool.get("tools"), list):
            namespace = tool.get("name")
            if isinstance(namespace, str) and namespace:
                for child in tool["tools"]:
                    if not isinstance(child, dict):
                        continue
                    child_name = child.get("name")
                    if isinstance(child_name, str) and child_name:
                        aliases[child_name] = child_name
                        aliases[f"{namespace}__{child_name}"] = child_name
            continue
        function = tool.get("function")
        name = function.get("name") if isinstance(function, dict) else tool.get("name")
        if isinstance(name, str) and name:
            aliases[name] = name
    return aliases


def _request_tool_namespaces(request_body: Any) -> dict[str, str]:
    """Map accepted names to their Responses API namespace, when present."""
    if not isinstance(request_body, dict):
        return {}
    namespaces: dict[str, str] = {}
    for tool in request_body.get("tools") or []:
        if not isinstance(tool, dict) or tool.get("type") != "namespace":
            continue
        namespace = tool.get("name")
        if not isinstance(namespace, str) or not namespace:
            continue
        for child in tool.get("tools") or []:
            if not isinstance(child, dict):
                continue
            child_name = child.get("name")
            if isinstance(child_name, str) and child_name:
                namespaces[child_name] = namespace
                namespaces[f"{namespace}__{child_name}"] = namespace
    return namespaces


def _request_tool_names(request_body: Any) -> set[str]:
    return set(_request_tool_aliases(request_body))


def _parse_dsml_parameter(value: str, is_string: bool) -> Any:
    decoded = html.unescape(value).strip()
    if is_string:
        return decoded
    try:
        return json.loads(decoded)
    except json.JSONDecodeError:
        return decoded


def _normalize_dsml_tool_calls(response_body: Any, request_body: Any) -> tuple[Any, bool]:
    """Convert DeepSeek textual DSML calls for the client, without changing wire evidence."""
    if not isinstance(response_body, dict):
        return response_body, False
    tool_aliases = _request_tool_aliases(request_body)
    if not tool_aliases:
        return response_body, False
    choices = response_body.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return response_body, False
    message = choices[0].get("message")
    if not isinstance(message, dict) or message.get("tool_calls"):
        return response_body, False
    content = message.get("content")
    if not isinstance(content, str):
        return response_body, False
    wrapper = _DSML_TOOL_CALLS_RE.search(content)
    if wrapper is None:
        return response_body, False

    calls: list[dict[str, Any]] = []
    for invocation in _DSML_INVOKE_RE.finditer(wrapper.group("body")):
        tool_name = html.unescape(invocation.group("name")).strip()
        if tool_name not in tool_aliases:
            return response_body, False
        tool_name = tool_aliases[tool_name]
        arguments: dict[str, Any] = {}
        for parameter in _DSML_PARAMETER_RE.finditer(invocation.group("body")):
            parameter_name = html.unescape(parameter.group("name")).strip()
            arguments[parameter_name] = _parse_dsml_parameter(
                parameter.group("value"), parameter.group("string") == "true"
            )
        calls.append(
            {
                "id": f"call_{uuid.uuid4().hex}",
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(arguments, ensure_ascii=False, separators=(",", ":")),
                },
            }
        )
    if not calls:
        return response_body, False

    normalized = dict(response_body)
    normalized_choices = list(choices)
    choice = dict(normalized_choices[0])
    normalized_message = dict(message)
    remaining_content = (content[: wrapper.start()] + content[wrapper.end() :]).strip()
    normalized_message["content"] = remaining_content or None
    normalized_message["tool_calls"] = calls
    choice["message"] = normalized_message
    choice["finish_reason"] = "tool_calls"
    normalized_choices[0] = choice
    normalized["choices"] = normalized_choices
    return normalized, True


def _normalize_responses_dsml_tool_calls(response_body: Any, request_body: Any) -> tuple[Any, bool]:
    """Convert textual DSML in a Responses API message into function_call items."""
    if not isinstance(response_body, dict):
        return response_body, False
    tool_aliases = _request_tool_aliases(request_body)
    tool_namespaces = _request_tool_namespaces(request_body)
    if not tool_aliases:
        return response_body, False
    output = response_body.get("output")
    if not isinstance(output, list):
        return response_body, False

    normalized_output: list[dict[str, Any]] = []
    transformed = False
    for item in output:
        if isinstance(item, dict) and item.get("type") == "function_call":
            original_name = item.get("name")
            if isinstance(original_name, str) and original_name in tool_aliases:
                normalized_item = dict(item)
                normalized_item["name"] = tool_aliases[original_name]
                namespace = tool_namespaces.get(original_name)
                if namespace:
                    normalized_item["namespace"] = namespace
                if normalized_item != item:
                    transformed = True
                normalized_output.append(normalized_item)
            else:
                normalized_output.append(item)
            continue
        if not isinstance(item, dict) or item.get("type") != "message":
            normalized_output.append(item)
            continue
        content_items = item.get("content")
        if not isinstance(content_items, list):
            normalized_output.append(item)
            continue
        rendered = _content_text(content_items)
        wrapper = _DSML_TOOL_CALLS_RE.search(rendered)
        if wrapper is None:
            normalized_output.append(item)
            continue

        calls: list[dict[str, Any]] = []
        for invocation in _DSML_INVOKE_RE.finditer(wrapper.group("body")):
            original_name = html.unescape(invocation.group("name")).strip()
            if original_name not in tool_aliases:
                return response_body, False
            tool_name = tool_aliases[original_name]
            arguments: dict[str, Any] = {}
            for parameter in _DSML_PARAMETER_RE.finditer(invocation.group("body")):
                parameter_name = html.unescape(parameter.group("name")).strip()
                arguments[parameter_name] = _parse_dsml_parameter(
                    parameter.group("value"), parameter.group("string") == "true"
                )
            call_id = f"call_{uuid.uuid4().hex}"
            call = {
                "id": f"fc_{uuid.uuid4().hex}",
                "type": "function_call",
                "status": "completed",
                "call_id": call_id,
                "name": tool_name,
                "arguments": json.dumps(arguments, ensure_ascii=False, separators=(",", ":")),
            }
            namespace = tool_namespaces.get(original_name)
            if namespace:
                call["namespace"] = namespace
            calls.append(call)
        if not calls:
            normalized_output.append(item)
            continue

        remaining = (rendered[: wrapper.start()] + rendered[wrapper.end() :]).strip()
        if remaining:
            normalized_item = dict(item)
            normalized_item["content"] = [{"type": "output_text", "text": remaining, "annotations": []}]
            normalized_output.append(normalized_item)
        normalized_output.extend(calls)
        transformed = True

    if not transformed:
        return response_body, False
    normalized = dict(response_body)
    normalized["output"] = normalized_output
    return normalized, True


def _responses_sse_from_completed(response_body: dict[str, Any]) -> list[bytes]:
    """Create a compact Responses SSE stream for a buffered normalized response."""
    chunks: list[bytes] = []
    sequence_number = 0

    def emit(event: dict[str, Any]) -> None:
        nonlocal sequence_number
        event["sequence_number"] = sequence_number
        sequence_number += 1
        chunks.append(("data: " + json.dumps(event, ensure_ascii=False) + "\n\n").encode("utf-8"))

    created = dict(response_body)
    created["status"] = "in_progress"
    created["output"] = []
    emit({"type": "response.created", "response": created})
    for output_index, item in enumerate(response_body.get("output") or []):
        if not isinstance(item, dict):
            continue
        added_item = dict(item)
        added_item["status"] = "in_progress"
        if item.get("type") == "function_call":
            added_item["arguments"] = ""
        elif item.get("type") == "reasoning":
            added_item["summary"] = []
        emit({"type": "response.output_item.added", "output_index": output_index, "item": added_item})
        if item.get("type") == "reasoning":
            for summary_index, part in enumerate(item.get("summary") or []):
                if not isinstance(part, dict) or not isinstance(part.get("text"), str):
                    continue
                empty_part = {**part, "text": ""}
                common = {
                    "output_index": output_index,
                    "item_id": item.get("id"),
                    "summary_index": summary_index,
                }
                emit({
                    "type": "response.reasoning_summary_part.added",
                    **common,
                    "part": empty_part,
                })
                emit({
                    "type": "response.reasoning_summary_text.delta",
                    **common,
                    "delta": part["text"],
                })
                emit({
                    "type": "response.reasoning_summary_text.done",
                    **common,
                    "text": part["text"],
                })
                emit({
                    "type": "response.reasoning_summary_part.done",
                    **common,
                    "part": part,
                })
        elif item.get("type") == "function_call":
            arguments = str(item.get("arguments") or "")
            emit(
                {
                    "type": "response.function_call_arguments.delta",
                    "output_index": output_index,
                    "item_id": item.get("id"),
                    "delta": arguments,
                }
            )
            emit(
                {
                    "type": "response.function_call_arguments.done",
                    "output_index": output_index,
                    "item_id": item.get("id"),
                    "arguments": arguments,
                }
            )
        emit({"type": "response.output_item.done", "output_index": output_index, "item": item})
    emit({"type": "response.completed", "response": response_body})
    chunks.append(b"data: [DONE]\n\n")
    return chunks


def _ids(request: Request, body: Any) -> RequestMeta:
    headers = request.headers
    session_id = (
        headers.get("x-session-id")
        or headers.get("x-claude-session-id")
        or headers.get("session_id")
    )
    if not session_id and isinstance(body, dict):
        session_id = body.get("session_id")
        metadata = body.get("metadata")
        if not session_id and isinstance(metadata, dict):
            session_id = metadata.get("session_id")
    session_id = session_id or "default"
    task_id = headers.get("x-task-id") or session_id
    request_id = headers.get("x-request-id") or uuid.uuid4().hex
    return RequestMeta(
        task_id=task_id,
        session_id=session_id,
        request_id=request_id,
        timestamp=utc_now(),
        method=request.method,
        path=str(request.url.path),
    )


def _record(
    meta: RequestMeta,
    request_body: Any,
    response_body: Any,
    status_code: int,
    latency_ms: float,
    *,
    retry_count: int = 0,
) -> dict[str, Any]:
    req = request_body if isinstance(request_body, dict) else {}
    resp_meta = response_metadata(response_body)
    return {
        "timestamp": meta.timestamp,
        "task_id": meta.task_id,
        "session_id": meta.session_id,
        "request_id": meta.request_id,
        "interaction_turn": _request_interaction_turns.get(meta.request_id),
        "max_interaction_turns": MAX_INTERACTION_TURNS,
        "method": meta.method,
        "path": meta.path,
        "status_code": status_code,
        "model": req.get("model") or config.upstream.model,
        "temperature": req.get("temperature"),
        "top_p": req.get("top_p"),
        "max_tokens": req.get("max_tokens"),
        "messages": req.get("messages", []),
        "tools": req.get("tools", []),
        "tool_choice": req.get("tool_choice"),
        "request": request_body,
        "response": response_body,
        "usage": resp_meta["usage"],
        "finish_reason": resp_meta["finish_reason"],
        "latency_ms": round(latency_ms, 3),
        "elapsed_time": round(latency_ms / 1000, 6),
        "retry_count": retry_count,
    }


def _record_exchange(
    meta: RequestMeta,
    request_body: Any,
    response_body: Any,
    status_code: int,
    latency_ms: float,
    *,
    wire_request: Any | None = None,
    wire_response: Any | None = None,
    retry_count: int = 0,
    native_reasoning: bool = False,
) -> None:
    exact_request = request_body if wire_request is None else wire_request
    exact_response = response_body if wire_response is None else wire_response
    if native_reasoning:
        request_body = _native_reasoning_log_view(request_body)
        response_body = _native_reasoning_log_view(response_body)
        exact_request = _native_reasoning_log_view(exact_request)
        exact_response = _native_reasoning_log_view(exact_response)
    request_path = config.gateway.raw_dir / f"{meta.request_id}_request.json"
    response_path = config.gateway.raw_dir / f"{meta.request_id}_response.json"
    write_json(request_path, exact_request)
    write_json(response_path, exact_response)
    record = _record(
        meta,
        request_body,
        response_body,
        status_code,
        latency_ms,
        retry_count=retry_count,
    )
    if native_reasoning:
        record["reasoning_capture"] = "metadata_only"
    append_jsonl(
        config.gateway.raw_dir / "raw_request_response.jsonl",
        {
            "timestamp": record["timestamp"],
            "task_id": record["task_id"],
            "session_id": record["session_id"],
            "request_id": record["request_id"],
            "model": record["model"],
            "path": record["path"],
            "status_code": record["status_code"],
            "usage": record["usage"],
            "latency_ms": record["latency_ms"],
            "retry_count": record["retry_count"],
            "request_file": request_path.name,
            "response_file": response_path.name,
        },
    )
    update_trajectory(config.gateway.trajectory_dir / f"{meta.session_id}.json", record)
    save_model_io(
        config.gateway.trajectory_dir.parent / "model_io",
        record,
        request_path,
        response_path,
    )


def _error_body(error_type: str, message: str) -> dict[str, Any]:
    return {"error": {"type": error_type, "message": message}}


async def _reserve_interaction_turn(
    meta: RequestMeta,
    request_body: Any,
    *,
    wire_request: Any | None = None,
    native_reasoning: bool = False,
) -> Response | None:
    """Allow at most MAX_INTERACTION_TURNS provider-bound model requests."""
    global _interaction_turn_count
    async with _interaction_turn_lock:
        attempted_turn = _interaction_turn_count + 1
        _request_interaction_turns[meta.request_id] = attempted_turn
        if attempted_turn <= MAX_INTERACTION_TURNS:
            _interaction_turn_count = attempted_turn
            return None

    message = (
        f"Maximum interaction turn limit reached ({MAX_INTERACTION_TURNS}). "
        "No additional model request was forwarded upstream."
    )
    response_body = _error_body("interaction_turn_limit_reached", message)
    _record_exchange(
        meta,
        request_body,
        response_body,
        429,
        0,
        wire_request=wire_request,
        native_reasoning=native_reasoning,
    )
    write_json(
        config.gateway.raw_dir / "interaction_turn_limit_reached.json",
        {
            "timestamp": utc_now(),
            "request_id": meta.request_id,
            "attempted_turn": attempted_turn,
            "max_interaction_turns": MAX_INTERACTION_TURNS,
            "message": message,
        },
    )
    log.warning("interaction turn limit reached: request=%s limit=%s", meta.request_id, MAX_INTERACTION_TURNS)
    return Response(
        content=json.dumps(response_body, ensure_ascii=False),
        status_code=429,
        headers={"x-patex-interaction-turn-limit": str(MAX_INTERACTION_TURNS)},
        media_type="application/json",
    )


def _stream_summary(chunks: list[bytes]) -> dict[str, Any]:
    raw_text = b"".join(chunks).decode("utf-8", errors="replace")
    events: list[Any] = []
    content: list[str] = []
    reasoning_content: list[str] = []
    reasoning_details: list[Any] = []
    tool_calls_by_index: dict[int, dict[str, Any]] = {}
    tool_call_deltas: list[Any] = []
    finish_reason = None
    usage = None
    for line in raw_text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if not data or data == "[DONE]":
            continue
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue
        events.append(event)
        usage = event.get("usage") or usage
        choices = event.get("choices")
        if not isinstance(choices, list) or not choices:
            continue
        choice = choices[0] if isinstance(choices[0], dict) else {}
        finish_reason = choice.get("finish_reason") or finish_reason
        delta = choice.get("delta") if isinstance(choice.get("delta"), dict) else {}
        if isinstance(delta.get("content"), str):
            content.append(delta["content"])
        has_direct_reasoning = False
        if isinstance(delta.get("reasoning_content"), str):
            reasoning_content.append(delta["reasoning_content"])
            has_direct_reasoning = True
        elif isinstance(delta.get("reasoning"), str):
            reasoning_content.append(delta["reasoning"])
            has_direct_reasoning = True
        if delta.get("reasoning_details") is not None:
            detail = delta.get("reasoning_details")
            details = detail if isinstance(detail, list) else [detail]
            reasoning_details.extend(details)
            if not has_direct_reasoning:
                for item in details:
                    if isinstance(item, dict) and isinstance(item.get("text"), str):
                        reasoning_content.append(item["text"])
        if delta.get("tool_calls"):
            tool_call_deltas.append(delta["tool_calls"])
            for call_delta in delta["tool_calls"]:
                if not isinstance(call_delta, dict):
                    continue
                index = int(call_delta.get("index", len(tool_calls_by_index)))
                current = tool_calls_by_index.setdefault(index, {"id": None, "type": "function", "function": {"name": "", "arguments": ""}})
                if call_delta.get("id"):
                    current["id"] = call_delta.get("id")
                if call_delta.get("type"):
                    current["type"] = call_delta.get("type")
                fn_delta = call_delta.get("function") if isinstance(call_delta.get("function"), dict) else {}
                if fn_delta.get("name"):
                    current["function"]["name"] += fn_delta.get("name")
                if fn_delta.get("arguments"):
                    current["function"]["arguments"] += fn_delta.get("arguments")
    message: dict[str, Any] = {"role": "assistant", "content": "".join(content) or None}
    if reasoning_content:
        message["reasoning_content"] = "".join(reasoning_content)
    if reasoning_details:
        message["reasoning_details"] = reasoning_details
    tool_calls = [tool_calls_by_index[i] for i in sorted(tool_calls_by_index)]
    if tool_calls:
        message["tool_calls"] = tool_calls
    return {
        "stream": True,
        "raw_sse": raw_text,
        "events": events,
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }
        ],
        "tool_call_deltas": tool_call_deltas,
        "usage": usage,
    }


def _chat_summary_to_sse(response_body: dict[str, Any]) -> list[bytes]:
    """Render a buffered normalized Chat Completions response as client-facing SSE."""
    choice = (response_body.get("choices") or [{}])[0]
    message = choice.get("message") if isinstance(choice, dict) else {}
    message = message if isinstance(message, dict) else {}
    delta: dict[str, Any] = {"role": message.get("role", "assistant")}
    if message.get("content") is not None:
        delta["content"] = message["content"]
    if message.get("reasoning_content") is not None:
        delta["reasoning_content"] = message["reasoning_content"]
    tool_calls = []
    for index, call in enumerate(message.get("tool_calls") or []):
        if not isinstance(call, dict):
            continue
        rendered = dict(call)
        rendered["index"] = index
        tool_calls.append(rendered)
    if tool_calls:
        delta["tool_calls"] = tool_calls
    base = {
        "id": response_body.get("id") or f"chatcmpl_{uuid.uuid4().hex}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": response_body.get("model"),
    }
    first = {**base, "choices": [{"index": 0, "delta": delta, "finish_reason": None}]}
    final = {
        **base,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": choice.get("finish_reason") or ("tool_calls" if tool_calls else "stop"),
            }
        ],
    }
    if response_body.get("usage") is not None:
        final["usage"] = response_body["usage"]
    return [
        f"data: {json.dumps(first, ensure_ascii=False)}\n\n".encode("utf-8"),
        f"data: {json.dumps(final, ensure_ascii=False)}\n\n".encode("utf-8"),
        b"data: [DONE]\n\n",
    ]


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            text = item.get("text") or item.get("input_text") or item.get("output_text")
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts)


def _reasoning_text(message: Any) -> str:
    """Return one readable reasoning projection without duplicating deltas."""
    if not isinstance(message, dict):
        return ""
    for key in ("reasoning_content", "reasoning", "reasoning_text"):
        value = message.get(key)
        if isinstance(value, str) and value.strip():
            return value

    texts: list[str] = []

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            text = value.get("text")
            if isinstance(text, str) and text:
                texts.append(text)
                return
            for key in ("content", "summary"):
                collect(value.get(key))
        elif isinstance(value, list):
            for item in value:
                collect(item)

    collect(message.get("reasoning_details"))
    return "".join(texts)


def _should_preserve_chat_reasoning(model: Any) -> bool:
    if CHAT_REASONING_HISTORY_MODE == "preserve":
        return True
    if CHAT_REASONING_HISTORY_MODE == "drop":
        return False
    # These reasoning-capable Chat model families either require historical
    # reasoning alongside tool calls (Kimi) or expose it for multi-turn replay.
    # Unknown providers remain conservative and can opt in with ``preserve``.
    if not isinstance(model, str):
        return False
    normalized = model.casefold()
    return any(family in normalized for family in ("kimi", "deepseek", "qwen"))


def _prepare_chat_reasoning_history(body: Any) -> Any:
    """Populate provider-bound assistant reasoning for compatible Chat APIs."""
    if not isinstance(body, dict) or not _should_preserve_chat_reasoning(body.get("model")):
        return body
    if not isinstance(body.get("messages"), list):
        return body
    prepared = dict(body)
    messages: list[Any] = []
    for message in body["messages"]:
        if not isinstance(message, dict) or message.get("role") != "assistant":
            messages.append(message)
            continue
        cleaned = dict(message)
        reasoning = _reasoning_text(message)
        if reasoning:
            cleaned["reasoning_content"] = reasoning
        messages.append(cleaned)
    prepared["messages"] = messages
    return prepared


def _responses_input_messages(body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    messages: list[dict[str, Any]] = []
    instructions = body.get("instructions")
    if instructions:
        messages.append({"role": "system", "content": _content_text(instructions)})
    value = body.get("input")
    if isinstance(value, str):
        messages.append({"role": "user", "content": value})
        return messages
    if not isinstance(value, list):
        return messages
    pending_assistant: dict[str, Any] | None = None

    def assistant() -> dict[str, Any]:
        nonlocal pending_assistant
        if pending_assistant is None:
            pending_assistant = {"role": "assistant", "content": None}
        return pending_assistant

    def flush_assistant() -> None:
        nonlocal pending_assistant
        if pending_assistant is not None:
            messages.append(pending_assistant)
            pending_assistant = None

    for item in value:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type == "reasoning":
            rendered = _content_text(item.get("summary") or item.get("content"))
            current = assistant()
            if rendered:
                existing = current.get("reasoning_content")
                current["reasoning_content"] = "\n".join(filter(None, [existing, rendered]))
            current.setdefault("reasoning_details", []).append(item)
        elif item_type == "function_call":
            assistant().setdefault("tool_calls", []).append(
                {
                    "id": item.get("call_id") or item.get("id"),
                    "type": "function",
                    "function": {"name": item.get("name"), "arguments": item.get("arguments", "")},
                }
            )
        elif item_type == "function_call_output":
            flush_assistant()
            output = item.get("output")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": item.get("call_id"),
                    "content": _content_text(output)
                    or (output if isinstance(output, str) else json.dumps(output, ensure_ascii=False)),
                }
            )
        elif item.get("role"):
            role = item.get("role")
            if role == "assistant":
                rendered = _content_text(item.get("content"))
                current = assistant()
                if rendered:
                    existing = current.get("content")
                    current["content"] = "\n".join(filter(None, [existing, rendered]))
            else:
                flush_assistant()
                messages.append({"role": role, "content": _content_text(item.get("content"))})
    flush_assistant()
    return messages


def _responses_request_to_chat(body: Any) -> dict[str, Any]:
    """Translate the Responses subset used by Codex into Chat Completions."""
    if not isinstance(body, dict):
        return {}
    translated: dict[str, Any] = {
        "model": body.get("model"),
        "messages": _chat_compatible_messages(
            _responses_input_messages(body),
            preserve_reasoning_content=_should_preserve_chat_reasoning(body.get("model")),
        ),
    }
    for key in ("stream", "temperature", "top_p", "parallel_tool_calls"):
        if key in body:
            translated[key] = body[key]
    if body.get("stream") is True and (
        CHAT_STREAM_USAGE_MODE == "required"
        or (
            CHAT_STREAM_USAGE_MODE == "auto"
            and _chat_stream_usage_capability is not False
        )
    ):
        translated["stream_options"] = {"include_usage": True}
    reasoning = body.get("reasoning")
    if (
        CHAT_REASONING_EFFORT_ENABLED
        and isinstance(reasoning, dict)
        and isinstance(reasoning.get("effort"), str)
    ):
        translated["reasoning_effort"] = reasoning["effort"]
    if "max_output_tokens" in body:
        translated["max_tokens"] = body["max_output_tokens"]

    tools: list[dict[str, Any]] = []
    for tool in body.get("tools") or []:
        if not isinstance(tool, dict):
            continue
        candidates = tool.get("tools") or [] if tool.get("type") == "namespace" else [tool]
        for candidate in candidates:
            if not isinstance(candidate, dict) or candidate.get("type") != "function":
                continue
            function = {
                key: candidate[key]
                for key in ("name", "description", "parameters", "strict")
                if key in candidate
            }
            tools.append({"type": "function", "function": function})
    if tools:
        translated["tools"] = tools

        tool_choice = body.get("tool_choice")
        if isinstance(tool_choice, dict) and tool_choice.get("type") == "function":
            name = tool_choice.get("name")
            translated["tool_choice"] = {
                "type": "function",
                "function": {"name": name},
            }
        elif tool_choice is not None:
            translated["tool_choice"] = tool_choice
        else:
            translated["tool_choice"] = TOOL_CHOICE_OVERRIDE or "auto"
    return {key: value for key, value in translated.items() if value is not None}


def _responses_usage_from_chat(chat_body: Any) -> dict[str, int] | None:
    """Translate complete, trustworthy Chat token accounting to Responses."""
    if not isinstance(chat_body, dict):
        return None
    usage = chat_body.get("usage")
    if not isinstance(usage, dict):
        return None

    input_tokens = usage.get("prompt_tokens")
    output_tokens = usage.get("completion_tokens")
    total_tokens = usage.get("total_tokens")
    if type(input_tokens) is not int or input_tokens < 0:
        return None
    if type(output_tokens) is not int or output_tokens < 0:
        return None
    if type(total_tokens) is not int or total_tokens < 0:
        total_tokens = input_tokens + output_tokens
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def _is_unsupported_stream_options_400(
    status_code: int, chunks: list[bytes]
) -> bool:
    """Recognize only pre-stream 400s that explicitly reject stream_options."""
    if status_code != 400:
        return False
    text = b"".join(chunks).decode("utf-8", errors="replace").strip()
    if any(line.lstrip().startswith("data:") for line in text.splitlines()):
        return False
    try:
        body = json.loads(text)
    except json.JSONDecodeError:
        return False
    rendered = json.dumps(body, ensure_ascii=False).lower()
    return "stream_options" in rendered and any(
        marker in rendered
        for marker in (
            "unknown field",
            "unknown parameter",
            "unsupported",
            "not supported",
            "unrecognized",
            "extra inputs",
            "unexpected",
        )
    )


def _context_budget_status(
    usage: dict[str, int] | None,
) -> dict[str, int | bool] | None:
    """Evaluate the configured provider context invariant from real usage."""
    if usage is None or PROVIDER_CONTEXT_WINDOW <= 0:
        return None
    projected_tokens = usage["input_tokens"] + MODEL_MAX_OUTPUT_TOKENS
    safe_limit = max(0, PROVIDER_CONTEXT_WINDOW - CONTEXT_SAFETY_MARGIN)
    return {
        "input_tokens": usage["input_tokens"],
        "max_output_tokens": MODEL_MAX_OUTPUT_TOKENS,
        "context_window": PROVIDER_CONTEXT_WINDOW,
        "safety_margin": CONTEXT_SAFETY_MARGIN,
        "projected_tokens": projected_tokens,
        "safe_limit": safe_limit,
        "within_budget": projected_tokens < safe_limit,
    }


def _log_context_budget(
    usage: dict[str, int] | None, *, request_id: str, model: Any
) -> None:
    """Warn when reported input plus reserved output approaches a known limit."""
    budget = _context_budget_status(usage)
    if budget is not None and not budget["within_budget"]:
        log.warning(
            "provider context budget reached: request=%s model=%s "
            "input_tokens=%s max_output_tokens=%s context_window=%s "
            "safety_margin=%s projected_tokens=%s",
            request_id,
            model,
            budget["input_tokens"],
            budget["max_output_tokens"],
            budget["context_window"],
            budget["safety_margin"],
            budget["projected_tokens"],
        )


def _chat_compatible_messages(
    messages: list[dict[str, Any]], *, preserve_reasoning_content: bool = False
) -> list[dict[str, Any]]:
    """Render a conservative system/user/assistant/tool Chat message sequence."""
    compatible: list[dict[str, Any]] = []
    system_parts: list[str] = []
    for message in messages:
        if not isinstance(message, dict) or not isinstance(message.get("role"), str):
            continue
        role = message["role"]
        if role in {"system", "developer"}:
            content = _content_text(message.get("content"))
            if content:
                system_parts.append(content)
            continue
        if role not in {"user", "assistant", "tool"}:
            continue
        cleaned: dict[str, Any] = {"role": role}
        if "content" in message:
            cleaned["content"] = message["content"]
        if role == "assistant" and isinstance(message.get("tool_calls"), list):
            cleaned["tool_calls"] = message["tool_calls"]
        if role == "assistant" and preserve_reasoning_content:
            reasoning = _reasoning_text(message)
            if reasoning:
                cleaned["reasoning_content"] = reasoning
        if role == "tool" and message.get("tool_call_id") is not None:
            cleaned["tool_call_id"] = message["tool_call_id"]
        if isinstance(message.get("name"), str):
            cleaned["name"] = message["name"]
        if role == "user" and compatible and compatible[-1].get("role") == "user":
            previous = _content_text(compatible[-1].get("content"))
            current = _content_text(cleaned.get("content"))
            compatible[-1]["content"] = "\n\n".join(filter(None, [previous, current]))
            continue
        compatible.append(cleaned)
    if system_parts:
        compatible.insert(0, {"role": "system", "content": "\n\n".join(system_parts)})
    return compatible


def _chat_response_to_responses(chat: Any, request_body: Any) -> dict[str, Any]:
    """Render a completed Chat Completions response as a Responses response."""
    chat_body = chat if isinstance(chat, dict) else {}
    choice = (chat_body.get("choices") or [{}])[0]
    choice = choice if isinstance(choice, dict) else {}
    message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
    output: list[dict[str, Any]] = []

    reasoning_content = message.get("reasoning_content") or message.get("reasoning")
    if isinstance(reasoning_content, str) and reasoning_content:
        output.append(
            {
                "id": f"rs_{uuid.uuid4().hex}",
                "type": "reasoning",
                "status": "completed",
                "summary": [{"type": "summary_text", "text": reasoning_content}],
            }
        )

    content = _content_text(message.get("content"))
    if content:
        output.append(
            {
                "id": f"msg_{uuid.uuid4().hex}",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [{"type": "output_text", "text": content, "annotations": []}],
            }
        )

    for call in message.get("tool_calls") or []:
        if not isinstance(call, dict):
            continue
        function = call.get("function") if isinstance(call.get("function"), dict) else {}
        call_id = call.get("id") or f"call_{uuid.uuid4().hex}"
        output.append(
            {
                "id": f"fc_{uuid.uuid4().hex}",
                "type": "function_call",
                "status": "completed",
                "call_id": call_id,
                "name": function.get("name"),
                "arguments": function.get("arguments") or "{}",
            }
        )

    responses_usage = _responses_usage_from_chat(chat_body)
    request = request_body if isinstance(request_body, dict) else {}
    tool_namespaces = _request_tool_namespaces(request)
    for item in output:
        if item.get("type") == "function_call" and item.get("name") in tool_namespaces:
            item["namespace"] = tool_namespaces[item["name"]]
    response_body = {
        "id": f"resp_{uuid.uuid4().hex}",
        "object": "response",
        "created_at": int(time.time()),
        "status": "completed",
        "model": chat_body.get("model") or request.get("model"),
        "output": output,
        "parallel_tool_calls": request.get("parallel_tool_calls", True),
        "tool_choice": request.get("tool_choice", "auto"),
        "tools": request.get("tools", []),
        "error": None,
        "incomplete_details": None,
    }
    if responses_usage is not None:
        response_body["usage"] = responses_usage
    return response_body


def _responses_assistant_message(response: Any) -> dict[str, Any]:
    message: dict[str, Any] = {"role": "assistant", "content": None}
    text: list[str] = []
    reasoning: list[str] = []
    reasoning_details: list[dict[str, Any]] = []
    tool_calls: list[dict[str, Any]] = []
    if isinstance(response, dict):
        for item in response.get("output") or []:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "message":
                rendered = _content_text(item.get("content"))
                if rendered:
                    text.append(rendered)
            elif item.get("type") == "reasoning":
                reasoning_details.append(item)
                rendered = _content_text(item.get("summary") or item.get("content"))
                if rendered:
                    reasoning.append(rendered)
            elif item.get("type") == "function_call":
                tool_calls.append(
                    {
                        "id": item.get("call_id") or item.get("id"),
                        "type": "function",
                        "function": {"name": item.get("name"), "arguments": item.get("arguments", "")},
                    }
                )
    if text:
        message["content"] = "\n".join(text)
    if reasoning:
        message["reasoning_content"] = "\n".join(reasoning)
    if reasoning_details:
        # Preserve the complete Responses reasoning output item, including its
        # id/status/summary/encrypted_content fields when the provider returns
        # them. reasoning_content remains the convenient readable projection.
        message["reasoning_details"] = reasoning_details
    if tool_calls:
        message["tool_calls"] = tool_calls
    return message


def _responses_summary(response: Any, *, raw_sse: str | None = None, events: list[Any] | None = None) -> dict[str, Any]:
    response_body = response if isinstance(response, dict) else {}
    summary: dict[str, Any] = {
        "choices": [
            {
                "index": 0,
                "message": _responses_assistant_message(response_body),
                "finish_reason": response_body.get("status"),
            }
        ],
        "usage": response_body.get("usage"),
        "response": response,
    }
    if raw_sse is not None:
        summary.update({"stream": True, "raw_sse": raw_sse, "events": events or []})
    return summary


def _responses_stream_summary(chunks: list[bytes]) -> dict[str, Any]:
    raw_text = b"".join(chunks).decode("utf-8", errors="replace")
    events: list[Any] = []
    completed_response: dict[str, Any] | None = None
    output_text: list[str] = []
    reasoning_text: list[str] = []
    function_calls: dict[str, dict[str, Any]] = {}
    for line in raw_text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if not data or data == "[DONE]":
            continue
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue
        events.append(event)
        event_type = event.get("type")
        if event_type == "response.output_text.delta" and isinstance(event.get("delta"), str):
            output_text.append(event["delta"])
        if event_type in {"response.reasoning_summary_text.delta", "response.reasoning_text.delta"} and isinstance(
            event.get("delta"), str
        ):
            reasoning_text.append(event["delta"])
        item = event.get("item") if isinstance(event.get("item"), dict) else {}
        if item.get("type") == "function_call":
            key = str(item.get("call_id") or item.get("id") or len(function_calls))
            function_calls[key] = item
        if event_type == "response.completed" and isinstance(event.get("response"), dict):
            completed_response = event["response"]
    if completed_response is None:
        output: list[dict[str, Any]] = []
        if output_text:
            output.append({"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "".join(output_text)}]})
        if reasoning_text:
            output.insert(
                0,
                {
                    "type": "reasoning",
                    "summary": [{"type": "summary_text", "text": "".join(reasoning_text)}],
                },
            )
        output.extend(function_calls.values())
        completed_response = {"status": "completed", "output": output}
    return _responses_summary(completed_response, raw_sse=raw_text, events=events)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "listen": f"{config.gateway.host}:{config.gateway.port}",
        "upstream_base_url": config.upstream.base_url,
        "upstream_endpoint": config.upstream.endpoint,
        "raw_log": str(config.gateway.raw_dir / "raw_request_response.jsonl"),
        "trajectory_dir": str(config.gateway.trajectory_dir),
        "interaction_turns": _interaction_turn_count,
        "max_interaction_turns": MAX_INTERACTION_TURNS,
        "agent_temperature": AGENT_TEMPERATURE,
        "model_max_output_tokens": MODEL_MAX_OUTPUT_TOKENS,
        "responses_upstream_mode": RESPONSES_UPSTREAM_MODE,
        "reasoning_mode": REASONING_MODE,
        "chat_reasoning_effort_enabled": CHAT_REASONING_EFFORT_ENABLED,
        "chat_reasoning_history_mode": CHAT_REASONING_HISTORY_MODE,
        "chat_stream_usage_mode": CHAT_STREAM_USAGE_MODE,
        "chat_stream_usage_capability": _chat_stream_usage_capability,
        "provider_context_window": PROVIDER_CONTEXT_WINDOW or None,
        "context_safety_margin": CONTEXT_SAFETY_MARGIN,
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> Response:
    client_raw_request = await request.body()
    client_request_body = _json_or_raw(client_raw_request)
    request_body, _ = _standardize_agent_request(client_request_body, "max_tokens")
    request_body = _prepare_chat_reasoning_history(request_body)
    raw_request = json.dumps(request_body, ensure_ascii=False).encode("utf-8")
    meta = _ids(request, request_body)

    limit_response = await _reserve_interaction_turn(meta, request_body)
    if limit_response is not None:
        return limit_response

    request_path = config.gateway.raw_dir / f"{meta.request_id}_request.json"
    write_json(request_path, request_body)
    if client_request_body != request_body:
        write_json(config.gateway.raw_dir / f"{meta.request_id}_client_request.json", client_request_body)

    if isinstance(request_body, dict) and request_body.get("stream") is True:
        started = time.perf_counter()
        # Determine the endpoint - use "*" to mean original path
        endpoint = config.upstream.endpoint
        if endpoint == "*":
            endpoint = request.url.path
        upstream_url = f"{config.upstream.base_url}{endpoint if endpoint.startswith('/') else '/' + endpoint}"
        client = httpx.AsyncClient(timeout=config.gateway.timeout_seconds)
        try:
            upstream_request = client.build_request(
                request.method,
                upstream_url,
                headers={
                    **{
                        k: v
                        for k, v in dict(request.headers).items()
                        if k.lower() not in (
                            {"host", "content-length", "authorization"}
                            if config.upstream.api_key
                            else {"host", "content-length"}
                        )
                    },
                    **({"Authorization": f"Bearer {config.upstream.api_key}"} if config.upstream.api_key else {}),
                },
                content=raw_request,
            )
            upstream = await client.send(upstream_request, stream=True)
        except httpx.TimeoutException as exc:
            await client.aclose()
            latency_ms = (time.perf_counter() - started) * 1000
            response_body = _error_body("upstream_timeout", str(exc))
            _record_exchange(meta, request_body, response_body, 504, latency_ms)
            return Response(content=json.dumps(response_body, ensure_ascii=False), status_code=504, media_type="application/json")
        except httpx.RequestError as exc:
            await client.aclose()
            latency_ms = (time.perf_counter() - started) * 1000
            response_body = _error_body("upstream_request_error", str(exc))
            _record_exchange(meta, request_body, response_body, 502, latency_ms)
            return Response(content=json.dumps(response_body, ensure_ascii=False), status_code=502, media_type="application/json")
        chunks: list[bytes] = []
        buffer_tool_stream = bool(isinstance(request_body, dict) and request_body.get("tools"))

        async def body_iter():
            wire_response_body: dict[str, Any] | None = None
            response_body: dict[str, Any] | None = None
            try:
                async for chunk in upstream.aiter_bytes():
                    chunks.append(chunk)
                    if not buffer_tool_stream:
                        yield chunk
                wire_response_body = _stream_summary(chunks)
                response_body, response_transformed = _normalize_dsml_tool_calls(
                    wire_response_body, request_body
                )
                if buffer_tool_stream:
                    outgoing = (
                        _chat_summary_to_sse(response_body)
                        if response_transformed
                        else chunks
                    )
                    for chunk in outgoing:
                        yield chunk
            finally:
                await upstream.aclose()
                await client.aclose()
                latency_ms = (time.perf_counter() - started) * 1000
                wire_response_body = wire_response_body or _stream_summary(chunks)
                response_body = response_body or wire_response_body
                _record_exchange(
                    meta,
                    request_body,
                    response_body,
                    upstream.status_code,
                    latency_ms,
                    wire_response=wire_response_body,
                )
                log.info(
                    "%s %s stream status=%s session=%s request=%s latency=%.1fms",
                    request.method,
                    request.url.path,
                    upstream.status_code,
                    meta.session_id,
                    meta.request_id,
                    latency_ms,
                )

        return StreamingResponse(
            body_iter(),
            status_code=upstream.status_code,
            headers={k: v for k, v in dict(upstream.headers).items() if k.lower() not in {"content-length", "transfer-encoding"}},
            media_type=upstream.headers.get("content-type", "text/event-stream"),
        )

    started = time.perf_counter()
    try:
        query = f"?{request.url.query}" if request.url.query else ""
        async with httpx.AsyncClient(timeout=config.gateway.timeout_seconds) as client:
            upstream = await client.request(
                request.method,
                f"{config.upstream.base_url}{request.url.path}{query}",
                headers=forward_headers(dict(request.headers), config.upstream.api_key),
                content=raw_request,
            )
        status_code = upstream.status_code
        upstream_headers = dict(upstream.headers)
        raw_response = upstream.content
        latency_ms = (time.perf_counter() - started) * 1000
    except httpx.TimeoutException as exc:
        latency_ms = 0
        response_body = _error_body("upstream_timeout", str(exc))
        _record_exchange(meta, request_body, response_body, 504, latency_ms)
        return Response(content=json.dumps(response_body, ensure_ascii=False), status_code=504, media_type="application/json")
    except httpx.RequestError as exc:
        latency_ms = 0
        response_body = _error_body("upstream_request_error", str(exc))
        _record_exchange(meta, request_body, response_body, 502, latency_ms)
        return Response(content=json.dumps(response_body, ensure_ascii=False), status_code=502, media_type="application/json")
    wire_response_body = _json_or_raw(raw_response)
    response_body, response_transformed = _normalize_dsml_tool_calls(wire_response_body, request_body)
    _record_exchange(
        meta,
        request_body,
        response_body,
        status_code,
        latency_ms,
        wire_response=wire_response_body,
    )

    log.info(
        "%s %s status=%s session=%s request=%s latency=%.1fms",
        request.method,
        request.url.path,
        status_code,
        meta.session_id,
        meta.request_id,
        latency_ms,
    )

    passthrough_headers = {
        k: v
        for k, v in upstream_headers.items()
        if k.lower() not in {"content-encoding", "transfer-encoding", "content-length", "connection"}
    }
    client_response = (
        json.dumps(response_body, ensure_ascii=False).encode("utf-8")
        if response_transformed
        else raw_response
    )
    return Response(
        content=client_response,
        status_code=status_code,
        headers=passthrough_headers,
        media_type=upstream_headers.get("content-type", "application/json"),
    )


def _is_retryable_transient_400(status_code: int, chunks: list[bytes]) -> bool:
    """Recognize only known transient, pre-response Chat routing failures."""
    if status_code != 400:
        return False

    text = b"".join(chunks).decode("utf-8", errors="replace").strip()
    if text.lower() == "bad request":
        return True

    try:
        body = json.loads(text)
    except json.JSONDecodeError:
        return False
    error = body.get("error") if isinstance(body, dict) else None
    message = error.get("message", "") if isinstance(error, dict) else ""
    return (
        "Received Model Group=" in message
        and "Available Model Group Fallbacks=None" in message
    )


async def _responses_via_chat(
    request: Request,
    meta: RequestMeta,
    request_body: Any,
    record_request: dict[str, Any],
) -> Response:
    """Serve a Responses client through a Chat Completions-only upstream."""
    global _chat_stream_usage_capability
    chat_request = _responses_request_to_chat(request_body)
    raw_chat_request = json.dumps(chat_request, ensure_ascii=False).encode("utf-8")
    upstream_url = f"{config.upstream.base_url}/v1/chat/completions"
    headers = forward_headers(dict(request.headers), config.upstream.api_key)

    if chat_request.get("stream") is True:
        started = time.perf_counter()
        retry_count = 0
        stream_options_fallback_used = False
        while True:
            try:
                async with httpx.AsyncClient(timeout=config.gateway.timeout_seconds) as client:
                    async with client.stream(
                        "POST", upstream_url, headers=headers, content=raw_chat_request
                    ) as upstream:
                        status_code = upstream.status_code
                        chunks = [chunk async for chunk in upstream.aiter_bytes()]
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                status_code = 504 if isinstance(exc, httpx.TimeoutException) else 502
                response_body = _error_body("upstream_error", str(exc))
                _record_exchange(
                    meta,
                    record_request,
                    response_body,
                    status_code,
                    (time.perf_counter() - started) * 1000,
                    wire_request=chat_request,
                    retry_count=retry_count,
                )
                return Response(
                    content=json.dumps(response_body),
                    status_code=status_code,
                    media_type="application/json",
                )

            if (
                CHAT_STREAM_USAGE_MODE == "auto"
                and not stream_options_fallback_used
                and "stream_options" in chat_request
                and _is_unsupported_stream_options_400(status_code, chunks)
            ):
                _chat_stream_usage_capability = False
                stream_options_fallback_used = True
                retry_count += 1
                chat_request.pop("stream_options", None)
                raw_chat_request = json.dumps(
                    chat_request, ensure_ascii=False
                ).encode("utf-8")
                log.warning(
                    "upstream rejected stream_options; retrying once without it "
                    "and caching endpoint capability: request=%s",
                    meta.request_id,
                )
                continue
            if not _is_retryable_transient_400(status_code, chunks):
                break
            if retry_count >= TRANSIENT_400_MAX_RETRIES:
                break
            retry_count += 1
            delay = TRANSIENT_400_RETRY_BASE_SECONDS * (2 ** (retry_count - 1))
            log.warning(
                "retrying transient upstream 400 attempt=%s/%s session=%s request=%s delay=%.3fs",
                retry_count,
                TRANSIENT_400_MAX_RETRIES,
                meta.session_id,
                meta.request_id,
                delay,
            )
            if delay:
                await asyncio.sleep(delay)

        latency_ms = (time.perf_counter() - started) * 1000
        chat_summary = _stream_summary(chunks)
        if status_code >= 400:
            _record_exchange(
                meta,
                record_request,
                chat_summary,
                status_code,
                latency_ms,
                wire_request=chat_request,
                wire_response={"raw_sse": chat_summary.get("raw_sse", "")},
                retry_count=retry_count,
            )
            outgoing = chunks
        else:
            normalized_chat, _ = _normalize_dsml_tool_calls(chat_summary, chat_request)
            responses_usage = _responses_usage_from_chat(normalized_chat)
            if responses_usage is None and CHAT_STREAM_USAGE_MODE != "disabled":
                response_body = _error_body(
                    "upstream_usage_missing",
                    "Chat streaming response did not contain valid prompt_tokens "
                    "and completion_tokens; refusing to report fabricated zero usage.",
                )
                _record_exchange(
                    meta,
                    record_request,
                    response_body,
                    502,
                    latency_ms,
                    wire_request=chat_request,
                    wire_response={"raw_sse": chat_summary.get("raw_sse", "")},
                    retry_count=retry_count,
                )
                return Response(
                    content=json.dumps(response_body, ensure_ascii=False),
                    status_code=502,
                    media_type="application/json",
                )
            if responses_usage is not None:
                if CHAT_STREAM_USAGE_MODE == "auto" and not stream_options_fallback_used:
                    _chat_stream_usage_capability = True
                _log_context_budget(
                    responses_usage,
                    request_id=meta.request_id,
                    model=chat_request.get("model"),
                )
            response_body = _chat_response_to_responses(normalized_chat, request_body)
            response_body, _ = _normalize_responses_dsml_tool_calls(response_body, request_body)
            response_summary = _responses_summary(response_body)
            response_summary["usage_source"] = (
                "upstream" if responses_usage is not None else "unavailable"
            )
            _record_exchange(
                meta,
                record_request,
                response_summary,
                status_code,
                latency_ms,
                wire_request=chat_request,
                wire_response={"raw_sse": chat_summary.get("raw_sse", "")},
                retry_count=retry_count,
            )
            outgoing = _responses_sse_from_completed(response_body)

        async def body_iter():
            for chunk in outgoing:
                yield chunk

        return StreamingResponse(
            body_iter(),
            status_code=status_code,
            media_type="text/event-stream",
        )

    started = time.perf_counter()
    retry_count = 0
    while True:
        try:
            async with httpx.AsyncClient(timeout=config.gateway.timeout_seconds) as client:
                upstream = await client.post(upstream_url, headers=headers, content=raw_chat_request)
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            status_code = 504 if isinstance(exc, httpx.TimeoutException) else 502
            response_body = _error_body("upstream_error", str(exc))
            _record_exchange(
                meta,
                record_request,
                response_body,
                status_code,
                (time.perf_counter() - started) * 1000,
                wire_request=chat_request,
                retry_count=retry_count,
            )
            return Response(
                content=json.dumps(response_body),
                status_code=status_code,
                media_type="application/json",
            )

        if not _is_retryable_transient_400(upstream.status_code, [upstream.content]):
            break
        if retry_count >= TRANSIENT_400_MAX_RETRIES:
            break
        retry_count += 1
        delay = TRANSIENT_400_RETRY_BASE_SECONDS * (2 ** (retry_count - 1))
        log.warning(
            "retrying transient upstream 400 attempt=%s/%s session=%s request=%s delay=%.3fs",
            retry_count,
            TRANSIENT_400_MAX_RETRIES,
            meta.session_id,
            meta.request_id,
            delay,
        )
        if delay:
            await asyncio.sleep(delay)

    latency_ms = (time.perf_counter() - started) * 1000

    wire_response = _json_or_raw(upstream.content)
    if upstream.status_code >= 400:
        response_body = wire_response
        client_content = upstream.content
    else:
        normalized_chat, _ = _normalize_dsml_tool_calls(wire_response, chat_request)
        response_body = _chat_response_to_responses(normalized_chat, request_body)
        response_body, _ = _normalize_responses_dsml_tool_calls(response_body, request_body)
        client_content = json.dumps(response_body, ensure_ascii=False).encode("utf-8")
    _record_exchange(
        meta,
        record_request,
        _responses_summary(response_body) if upstream.status_code < 400 else response_body,
        upstream.status_code,
        latency_ms,
        wire_request=chat_request,
        wire_response=wire_response,
        retry_count=retry_count,
    )
    return Response(
        content=client_content,
        status_code=upstream.status_code,
        media_type="application/json",
    )


@app.post("/v1/responses")
async def responses_api(request: Request) -> Response:
    client_raw_request = await request.body()
    client_request_body = _json_or_raw(client_raw_request)
    request_body, _ = _standardize_agent_request(
        _sanitize_responses_tool_outputs(client_request_body), "max_output_tokens"
    )
    upstream_request_body = (
        request_body
        if RESPONSES_UPSTREAM_MODE == "chat"
        else _ensure_responses_tool_choice(
            _flatten_responses_namespace_tools(request_body)
        )
    )
    raw_upstream_request = json.dumps(upstream_request_body, ensure_ascii=False).encode("utf-8")
    meta = _ids(request, request_body)
    native_responses = (
        REASONING_MODE == "native_passthrough"
        and RESPONSES_UPSTREAM_MODE == "responses"
    )
    request_log_view = (
        _native_reasoning_log_view(upstream_request_body)
        if native_responses
        else upstream_request_body
    )
    write_json(config.gateway.raw_dir / f"{meta.request_id}_request.json", request_log_view)
    if client_request_body != upstream_request_body:
        write_json(
            config.gateway.raw_dir / f"{meta.request_id}_client_request.json",
            _native_reasoning_log_view(client_request_body)
            if native_responses
            else client_request_body,
        )
    record_request = (
        dict(request_log_view)
        if isinstance(request_log_view, dict)
        else {"request": request_log_view}
    )
    record_request["messages"] = _responses_input_messages(request_log_view)
    limit_response = await _reserve_interaction_turn(
        meta,
        record_request,
        wire_request=upstream_request_body,
        native_reasoning=native_responses,
    )
    if limit_response is not None:
        return limit_response

    if RESPONSES_UPSTREAM_MODE == "chat":
        return await _responses_via_chat(request, meta, request_body, record_request)

    if isinstance(request_body, dict) and request_body.get("stream") is True:
        started = time.perf_counter()
        upstream_url = f"{config.upstream.base_url}{request.url.path}"
        client = httpx.AsyncClient(timeout=config.gateway.timeout_seconds)
        try:
            upstream_request = client.build_request(
                request.method,
                upstream_url,
                headers=forward_headers(dict(request.headers), config.upstream.api_key),
                content=raw_upstream_request,
            )
            upstream = await client.send(upstream_request, stream=True)
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            await client.aclose()
            status_code = 504 if isinstance(exc, httpx.TimeoutException) else 502
            response_body = _error_body("upstream_error", str(exc))
            _record_exchange(
                meta, record_request, response_body, status_code, 0,
                wire_request=upstream_request_body,
                native_reasoning=native_responses,
            )
            return Response(content=json.dumps(response_body), status_code=status_code, media_type="application/json")
        chunks = [chunk async for chunk in upstream.aiter_bytes()]
        await upstream.aclose()
        await client.aclose()
        latency_ms = (time.perf_counter() - started) * 1000
        if native_responses:
            wire_summary = _native_sse_log_view(chunks)
            _record_exchange(
                meta,
                record_request,
                wire_summary,
                upstream.status_code,
                latency_ms,
                wire_request=upstream_request_body,
                wire_response=wire_summary,
                native_reasoning=True,
            )

            async def native_body_iter():
                for chunk in chunks:
                    yield chunk

            return StreamingResponse(
                native_body_iter(),
                status_code=upstream.status_code,
                headers={k: v for k, v in dict(upstream.headers).items() if k.lower() not in {"content-length", "transfer-encoding"}},
                media_type=upstream.headers.get("content-type", "text/event-stream"),
            )

        wire_summary = _responses_stream_summary(chunks)
        completed_response = wire_summary.get("response")
        normalized_response, response_transformed = _normalize_responses_dsml_tool_calls(
            completed_response, request_body
        )
        summary = (
            _responses_summary(
                normalized_response,
                raw_sse=wire_summary.get("raw_sse", ""),
                events=wire_summary.get("events", []),
            )
            if response_transformed
            else wire_summary
        )
        _record_exchange(
            meta,
            record_request,
            summary,
            upstream.status_code,
            latency_ms,
            wire_request=upstream_request_body,
            wire_response={"raw_sse": wire_summary.get("raw_sse", "")},
        )
        client_chunks = (
            _responses_sse_from_completed(normalized_response)
            if response_transformed and isinstance(normalized_response, dict)
            else chunks
        )

        async def body_iter():
            for chunk in client_chunks:
                yield chunk

        return StreamingResponse(
            body_iter(),
            status_code=upstream.status_code,
            headers={k: v for k, v in dict(upstream.headers).items() if k.lower() not in {"content-length", "transfer-encoding"}},
            media_type=upstream.headers.get("content-type", "text/event-stream"),
        )

    started = time.perf_counter()
    try:
        query = f"?{request.url.query}" if request.url.query else ""
        async with httpx.AsyncClient(timeout=config.gateway.timeout_seconds) as client:
            upstream = await client.request(
                request.method,
                f"{config.upstream.base_url}{request.url.path}{query}",
                headers=forward_headers(dict(request.headers), config.upstream.api_key),
                content=raw_upstream_request,
            )
        status_code = upstream.status_code
        upstream_headers = dict(upstream.headers)
        raw_response = upstream.content
        latency_ms = (time.perf_counter() - started) * 1000
    except (httpx.TimeoutException, httpx.RequestError) as exc:
        status_code = 504 if isinstance(exc, httpx.TimeoutException) else 502
        response_body = _error_body("upstream_error", str(exc))
        _record_exchange(
            meta, record_request, response_body, status_code, 0,
            wire_request=upstream_request_body,
            native_reasoning=native_responses,
        )
        return Response(content=json.dumps(response_body), status_code=status_code, media_type="application/json")
    wire_response_body = _json_or_raw(raw_response)
    if native_responses:
        response_log_view = _native_reasoning_log_view(wire_response_body)
        _record_exchange(
            meta,
            record_request,
            _responses_summary(response_log_view),
            status_code,
            latency_ms,
            wire_request=upstream_request_body,
            wire_response=response_log_view,
            native_reasoning=True,
        )
        return Response(
            content=raw_response,
            status_code=status_code,
            headers={k: v for k, v in upstream_headers.items() if k.lower() not in {"content-length", "transfer-encoding"}},
            media_type=upstream_headers.get("content-type", "application/json"),
        )
    response_body, response_transformed = _normalize_responses_dsml_tool_calls(
        wire_response_body, request_body
    )
    _record_exchange(
        meta,
        record_request,
        _responses_summary(response_body),
        status_code,
        latency_ms,
        wire_request=upstream_request_body,
        wire_response=wire_response_body,
    )
    return Response(
        content=(
            json.dumps(response_body, ensure_ascii=False).encode("utf-8")
            if response_transformed
            else raw_response
        ),
        status_code=status_code,
        headers={k: v for k, v in upstream_headers.items() if k.lower() not in {"content-length", "transfer-encoding"}},
        media_type=upstream_headers.get("content-type", "application/json"),
    )


def _native_messages_passthrough_enabled() -> bool:
    endpoint = config.upstream.endpoint.rstrip("/")
    return (
        REASONING_MODE == "native_passthrough"
        and (endpoint == "*" or endpoint.endswith("/messages"))
    )


async def _native_anthropic_messages(
    request: Request,
    meta: RequestMeta,
    request_body: dict[str, Any],
) -> Response:
    """Proxy Anthropic Messages without translating thinking/signature blocks."""
    # Native Anthropic model metadata decides whether sampling parameters are
    # legal (adaptive thinking rejects temperature). Keep thinking,
    # output_config, signatures, and all other protocol fields untouched.
    provider_body, raw_provider_body = _standardize_output_limit(
        request_body, "max_tokens"
    )
    record_request = _native_reasoning_log_view(provider_body)
    limit_response = await _reserve_interaction_turn(
        meta,
        record_request,
        wire_request=provider_body,
        native_reasoning=True,
    )
    if limit_response is not None:
        return limit_response

    endpoint = config.upstream.endpoint
    if endpoint == "*":
        endpoint = request.url.path
    upstream_url = f"{config.upstream.base_url}{endpoint if endpoint.startswith('/') else '/' + endpoint}"
    started = time.perf_counter()
    try:
        client = httpx.AsyncClient(timeout=config.gateway.timeout_seconds)
        upstream_request = client.build_request(
            request.method,
            upstream_url,
            headers=forward_headers(dict(request.headers), config.upstream.api_key),
            content=raw_provider_body,
        )
        upstream = await client.send(
            upstream_request, stream=bool(provider_body.get("stream"))
        )
    except (httpx.TimeoutException, httpx.RequestError) as exc:
        if "client" in locals():
            await client.aclose()
        status_code = 504 if isinstance(exc, httpx.TimeoutException) else 502
        response_body = _error_body("upstream_error", str(exc))
        _record_exchange(
            meta,
            record_request,
            response_body,
            status_code,
            (time.perf_counter() - started) * 1000,
            wire_request=provider_body,
            native_reasoning=True,
        )
        return Response(
            content=json.dumps(response_body),
            status_code=status_code,
            media_type="application/json",
        )

    if provider_body.get("stream"):
        chunks = [chunk async for chunk in upstream.aiter_bytes()]
        await upstream.aclose()
        await client.aclose()
        latency_ms = (time.perf_counter() - started) * 1000
        log_view = _native_sse_log_view(chunks)
        _record_exchange(
            meta,
            record_request,
            log_view,
            upstream.status_code,
            latency_ms,
            wire_request=provider_body,
            wire_response=log_view,
            native_reasoning=True,
        )

        async def body_iter():
            for chunk in chunks:
                yield chunk

        return StreamingResponse(
            body_iter(),
            status_code=upstream.status_code,
            headers={k: v for k, v in dict(upstream.headers).items() if k.lower() not in {"content-length", "transfer-encoding"}},
            media_type=upstream.headers.get("content-type", "text/event-stream"),
        )

    raw_response = await upstream.aread()
    await upstream.aclose()
    await client.aclose()
    latency_ms = (time.perf_counter() - started) * 1000
    response_body = _json_or_raw(raw_response)
    response_log_view = _native_reasoning_log_view(response_body)
    _record_exchange(
        meta,
        record_request,
        response_log_view,
        upstream.status_code,
        latency_ms,
        wire_request=provider_body,
        wire_response=response_log_view,
        native_reasoning=True,
    )
    return Response(
        content=raw_response,
        status_code=upstream.status_code,
        headers={k: v for k, v in dict(upstream.headers).items() if k.lower() not in {"content-length", "transfer-encoding"}},
        media_type=upstream.headers.get("content-type", "application/json"),
    )


@app.post("/v1/messages")
async def anthropic_messages(request: Request) -> Response:
    raw_request = await request.body()
    request_body = _json_or_raw(raw_request)
    meta = _ids(request, request_body)

    if not isinstance(request_body, dict):
        return Response(content=json.dumps({"error": "invalid JSON request"}), status_code=400, media_type="application/json")

    if _native_messages_passthrough_enabled():
        write_json(
            config.gateway.raw_dir / f"{meta.request_id}_client_request.json",
            _native_reasoning_log_view(request_body),
        )
        return await _native_anthropic_messages(request, meta, request_body)

    write_json(config.gateway.raw_dir / f"{meta.request_id}_client_request.json", request_body)

    openai_body = anthropic_request_to_openai(request_body, config.upstream.model)
    openai_body, _ = _standardize_agent_request(openai_body, "max_tokens")
    openai_body = _prepare_chat_reasoning_history(openai_body)
    record_request = dict(openai_body)
    record_request["_client_request"] = request_body
    record_request["_upstream_endpoint"] = config.upstream.endpoint
    limit_response = await _reserve_interaction_turn(meta, record_request, wire_request=openai_body)
    if limit_response is not None:
        return limit_response
    upstream_raw = json.dumps(openai_body, ensure_ascii=False).encode("utf-8")
    started = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=config.gateway.timeout_seconds) as client:
            upstream_request = client.build_request(
                request.method,
                f"{config.upstream.base_url}{config.upstream.endpoint}",
                headers=forward_headers(dict(request.headers), config.upstream.api_key),
                content=upstream_raw,
            )
            upstream = await client.send(upstream_request, stream=bool(openai_body.get("stream")))

            if openai_body.get("stream"):
                upstream_lines: list[str] = []
                async for line in upstream.aiter_lines():
                    upstream_lines.append(line)
                await upstream.aclose()
                latency_ms = (time.perf_counter() - started) * 1000
                wire_openai_summary = _stream_summary([("\n".join(upstream_lines)).encode("utf-8")])
                openai_summary, response_transformed = _normalize_dsml_tool_calls(
                    wire_openai_summary, openai_body
                )
                conversion_lines = upstream_lines
                if response_transformed:
                    conversion_lines = b"".join(_chat_summary_to_sse(openai_summary)).decode(
                        "utf-8", errors="replace"
                    ).splitlines()
                chunks, anthropic_response = openai_stream_to_anthropic_chunks(
                    conversion_lines, request_body
                )
                if isinstance(anthropic_response, dict):
                    anthropic_response["_openai_response"] = openai_summary
                _record_exchange(
                    meta,
                    record_request,
                    openai_summary,
                    upstream.status_code,
                    latency_ms,
                    wire_request=openai_body,
                    wire_response=wire_openai_summary,
                )
                log.info(
                    "%s /v1/messages stream status=%s session=%s request=%s latency=%.1fms",
                    request.method,
                    upstream.status_code,
                    meta.session_id,
                    meta.request_id,
                    latency_ms,
                )

                async def converted_iter():
                    for chunk in chunks:
                        yield chunk

                return StreamingResponse(converted_iter(), status_code=upstream.status_code, media_type="text/event-stream")

            raw_response = await upstream.aread()
            await upstream.aclose()
    except httpx.TimeoutException as exc:
        latency_ms = (time.perf_counter() - started) * 1000
        response_body = _error_body("upstream_timeout", str(exc))
        _record_exchange(meta, record_request, response_body, 504, latency_ms, wire_request=openai_body)
        return Response(content=json.dumps(response_body, ensure_ascii=False), status_code=504, media_type="application/json")
    except httpx.RequestError as exc:
        latency_ms = (time.perf_counter() - started) * 1000
        response_body = _error_body("upstream_request_error", str(exc))
        _record_exchange(meta, record_request, response_body, 502, latency_ms, wire_request=openai_body)
        return Response(content=json.dumps(response_body, ensure_ascii=False), status_code=502, media_type="application/json")

    latency_ms = (time.perf_counter() - started) * 1000
    wire_openai_response = _json_or_raw(raw_response)
    openai_response, _ = _normalize_dsml_tool_calls(wire_openai_response, openai_body)
    anthropic_response = (
        openai_response_to_anthropic(openai_response, request_body)
        if isinstance(openai_response, dict) and upstream.status_code < 400
        else openai_response
    )
    if isinstance(anthropic_response, dict):
        anthropic_response["_openai_response"] = openai_response
    _record_exchange(
        meta,
        record_request,
        openai_response,
        upstream.status_code,
        latency_ms,
        wire_request=openai_body,
        wire_response=wire_openai_response,
    )
    log.info(
        "%s /v1/messages status=%s session=%s request=%s latency=%.1fms",
        request.method,
        upstream.status_code,
        meta.session_id,
        meta.request_id,
        latency_ms,
    )
    return Response(
        content=json.dumps(anthropic_response, ensure_ascii=False).encode("utf-8"),
        status_code=upstream.status_code,
        media_type="application/json",
    )


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def generic_proxy(path: str, request: Request) -> Response:
    raw_request = await request.body()
    try:
        status_code, upstream_headers, raw_response, _ = await forward_request(
            config=config,
            method=request.method,
            path=request.url.path,
            query=request.url.query,
            headers=dict(request.headers),
            body=raw_request,
        )
    except httpx.TimeoutException as exc:
        response_body = _error_body("upstream_timeout", str(exc))
        return Response(content=json.dumps(response_body, ensure_ascii=False), status_code=504, media_type="application/json")
    except httpx.RequestError as exc:
        response_body = _error_body("upstream_request_error", str(exc))
        return Response(content=json.dumps(response_body, ensure_ascii=False), status_code=502, media_type="application/json")
    return Response(
        content=raw_response,
        status_code=status_code,
        headers={k: v for k, v in upstream_headers.items() if k.lower() not in {"content-length", "transfer-encoding"}},
        media_type=upstream_headers.get("content-type", "application/json"),
    )
