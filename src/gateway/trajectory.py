from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .logger import write_json


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    texts.append(str(item.get("text", "")))
                elif item.get("type") == "tool_result":
                    texts.append(_content_text(item.get("content")))
        return "\n".join(t for t in texts if t)
    if content is None:
        return ""
    return str(content)


def _message_text(message: dict[str, Any]) -> str:
    return _content_text(message.get("content"))


def _json_arguments(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return "{}"
    return json.dumps(value, ensure_ascii=False)


def _openai_tool_call(call: dict[str, Any]) -> dict[str, Any]:
    fn = call.get("function") if isinstance(call.get("function"), dict) else {}
    return {
        "id": call.get("id") or call.get("tool_call_id"),
        "type": call.get("type", "function"),
        "function": {
            "name": fn.get("name") or call.get("name") or "unknown",
            "arguments": _json_arguments(fn.get("arguments") if "arguments" in fn else call.get("arguments")),
        },
    }


def _anthropic_tool_call(part: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": part.get("id") or part.get("tool_call_id") or part.get("tool_use_id"),
        "type": "function",
        "function": {
            "name": part.get("name") or "unknown",
            "arguments": _json_arguments(part.get("input") if "input" in part else part.get("arguments")),
        },
    }


def _copy_reasoning(src: dict[str, Any], dst: dict[str, Any]) -> None:
    # The normalized OpenAI-format trajectory has one readable reasoning field.
    # Provider-specific reasoning_details remain losslessly available in raw
    # request/response artifacts instead of being duplicated into every message.
    for key in ("reasoning_content", "reasoning"):
        if key in src and src.get(key) is not None:
            dst[key] = src.get(key)
    if "reasoning_content" not in dst:
        reasoning = src.get("reasoning")
        if isinstance(reasoning, str):
            dst["reasoning_content"] = reasoning
        elif isinstance(reasoning, dict):
            text = reasoning.get("content") or reasoning.get("text") or reasoning.get("summary")
            if text is not None:
                dst["reasoning_content"] = text
    if "reasoning_content" not in dst:
        texts: list[str] = []

        def collect(value: Any) -> None:
            if isinstance(value, dict):
                text = value.get("text")
                if isinstance(text, str) and text:
                    texts.append(text)
                for key in ("content", "summary"):
                    collect(value.get(key))
            elif isinstance(value, list):
                for item in value:
                    collect(item)

        collect(src.get("reasoning_details"))
        if texts:
            dst["reasoning_content"] = "".join(texts)


def _canonical_json_string(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.dumps(json.loads(value), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        return value


def _canonical_message(message: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in (
        "role",
        "content",
        "name",
        "tool_call_id",
        "reasoning_content",
        "reasoning",
        "refusal",
        "audio",
    ):
        if key in message:
            out[key] = message.get(key)
    if isinstance(message.get("tool_calls"), list):
        calls = []
        for call in message.get("tool_calls") or []:
            if not isinstance(call, dict):
                continue
            fn = call.get("function") if isinstance(call.get("function"), dict) else {}
            calls.append(
                {
                    "id": call.get("id"),
                    "type": call.get("type", "function"),
                    "function": {
                        "name": fn.get("name"),
                        "arguments": _canonical_json_string(fn.get("arguments")),
                    },
                }
            )
        out["tool_calls"] = calls
    return out


def _replay_identity(message: dict[str, Any]) -> dict[str, Any]:
    """Identify a message when a later request replays conversation history.

    Providers may return reasoning fields that clients intentionally omit when
    sending the assistant message back on the next request. Those fields must
    remain on the response-sourced trajectory entry, but their absence from the
    replay must not create a duplicate assistant/tool-call message.
    """
    out = _canonical_message(message)
    out.pop("reasoning_content", None)
    out.pop("reasoning", None)
    out.pop("reasoning_details", None)
    return out


def _canonical_prefix_equal(left: list[dict[str, Any]], right: list[dict[str, Any]], length: int) -> bool:
    return [_replay_identity(m) for m in left[:length]] == [_replay_identity(m) for m in right[:length]]


def normalize_openai_messages(messages: list[Any]) -> list[dict[str, Any]]:
    """Return an OpenAI-compatible message sequence without dropping fields.

    Assistant messages keep content, reasoning_content and tool_calls together.
    Tool results are represented as separate role=tool messages with tool_call_id.
    Anthropic-style content blocks are converted to equivalent OpenAI messages.
    """
    normalized: list[dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role", "user")
        content = message.get("content")

        if role == "assistant":
            anthropic_blocks = isinstance(content, list) and any(
                isinstance(part, dict) and part.get("type") == "tool_use" for part in content
            )
            rendered_content = _content_text(content) if anthropic_blocks else content
            out: dict[str, Any] = {"role": "assistant", "content": rendered_content}
            _copy_reasoning(message, out)
            # These are valid OpenAI assistant-message fields. Keep them in the
            # OpenAI-format trajectory instead of relying on the raw artifact.
            for key in ("name", "refusal", "audio"):
                if key in message:
                    out[key] = message.get(key)
            calls: list[dict[str, Any]] = []
            raw_calls = message.get("tool_calls")
            if isinstance(raw_calls, list):
                calls.extend(_openai_tool_call(call) for call in raw_calls if isinstance(call, dict))
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "tool_use":
                        calls.append(_anthropic_tool_call(part))
            if calls:
                out["tool_calls"] = calls
                if out.get("content") == "":
                    out["content"] = None
            normalized.append(out)
            continue

        if role == "tool":
            out = {
                "role": "tool",
                "tool_call_id": message.get("tool_call_id") or message.get("tool_use_id"),
                "content": content if isinstance(content, (str, list)) else _content_text(content),
            }
            if message.get("name") is not None:
                out["name"] = message.get("name")
            normalized.append(out)
            continue

        if role == "user" and isinstance(content, list):
            tool_results = [part for part in content if isinstance(part, dict) and part.get("type") == "tool_result"]
            text_parts = [part for part in content if isinstance(part, dict) and part.get("type") == "text"]
            for part in tool_results:
                normalized.append(
                    {
                        "role": "tool",
                        "tool_call_id": part.get("tool_use_id") or part.get("tool_call_id"),
                        "content": _content_text(part.get("content")),
                    }
                )
            text = _content_text(text_parts)
            if text:
                normalized.append({"role": "user", "content": text})
            elif not tool_results:
                normalized.append({"role": "user", "content": _content_text(content)})
            continue

        # Preserve OpenAI multimodal content arrays exactly. Anthropic
        # tool_result blocks are handled above and converted to role=tool.
        out = {"role": role, "content": content if isinstance(content, (str, list)) else _content_text(content)}
        _copy_reasoning(message, out)
        for key in ("name", "tool_call_id"):
            if key in message and message.get(key) is not None:
                out[key] = message.get(key)
        normalized.append(out)
    return normalized


def _normalize_request_message(message: dict[str, Any], round_index: int, message_index: int) -> list[dict[str, Any]]:
    entries = normalize_openai_messages([message])
    for entry in entries:
        entry["round_index"] = round_index
        entry["message_index"] = message_index
        entry["source"] = "request"
        entry["raw"] = message
    return entries


def extract_tool_results(messages: list[Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for idx, message in enumerate(messages):
        if not isinstance(message, dict):
            continue
        for normalized in normalize_openai_messages([message]):
            if normalized.get("role") == "tool":
                results.append(
                    {
                        "message_index": idx,
                        "tool_call_id": normalized.get("tool_call_id"),
                        "content": normalized.get("content"),
                        "is_error": message.get("is_error", False),
                    }
                )
    return results


def extract_response_message(response: dict[str, Any]) -> dict[str, Any] | None:
    openai_response = response.get("_openai_response") if isinstance(response.get("_openai_response"), dict) else None
    if openai_response is not None:
        response = openai_response
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        return message if isinstance(message, dict) else None
    if response.get("role") == "assistant":
        return response
    return None


def extract_tool_calls(response: dict[str, Any]) -> list[dict[str, Any]]:
    message = extract_response_message(response) or {}
    return [call for m in normalize_openai_messages([message]) for call in m.get("tool_calls", [])]


def build_messages_file(trajectory: dict[str, Any]) -> dict[str, Any]:
    messages: list[dict[str, Any]] = []
    seen_prefix: list[dict[str, Any]] = []
    for round_index, round_data in enumerate(trajectory.get("rounds", [])):
        request_messages = round_data.get("messages") if isinstance(round_data.get("messages"), list) else []
        normalized_request = normalize_openai_messages(request_messages)

        # Each chat completion request repeats conversation history. Append only
        # the newly added suffix so the exported file is a chronological SFT trace.
        start = min(len(seen_prefix), len(normalized_request))
        if not _canonical_prefix_equal(normalized_request, seen_prefix, start):
            start = 0
            while (
                start < len(normalized_request)
                and start < len(seen_prefix)
                and _replay_identity(normalized_request[start]) == _replay_identity(seen_prefix[start])
            ):
                start += 1
        for message_index, message in enumerate(normalized_request[start:], start):
            entry = dict(message)
            entry["round_index"] = round_index
            entry["message_index"] = message_index
            entry["source"] = "request"
            messages.append(entry)
        seen_prefix = normalized_request

        assistant = round_data.get("assistant")
        if isinstance(assistant, dict):
            for entry in normalize_openai_messages([assistant]):
                entry["round_index"] = round_index
                entry["message_index"] = len(request_messages)
                entry["source"] = "response"
                messages.append(entry)
                seen_prefix.append({k: v for k, v in entry.items() if k not in {"round_index", "message_index", "source"}})

    return {
        "format": "openai-chat-messages-v1",
        "task_id": trajectory.get("task_id"),
        "session_id": trajectory.get("session_id"),
        "started_at": trajectory.get("started_at"),
        "updated_at": trajectory.get("updated_at"),
        "round_count": trajectory.get("round_count", 0),
        "message_count": len(messages),
        "messages": messages,
    }


def build_round(record: dict[str, Any]) -> dict[str, Any]:
    request = record.get("request") if isinstance(record.get("request"), dict) else {}
    response = record.get("response") if isinstance(record.get("response"), dict) else {}
    messages = request.get("messages") if isinstance(request.get("messages"), list) else []
    normalized_messages = normalize_openai_messages(messages)
    assistant = extract_response_message(response)
    normalized_assistant = normalize_openai_messages([assistant])[0] if isinstance(assistant, dict) else None
    return {
        "request_id": record.get("request_id"),
        "timestamp": record.get("timestamp"),
        "status_code": record.get("status_code"),
        "interaction_turn": record.get("interaction_turn"),
        "max_interaction_turns": record.get("max_interaction_turns"),
        "latency_ms": record.get("latency_ms"),
        "retry_count": record.get("retry_count", 0),
        "model": record.get("model"),
        "temperature": record.get("temperature"),
        "top_p": record.get("top_p"),
        "max_tokens": record.get("max_tokens"),
        "messages": normalized_messages,
        "tools": request.get("tools", []),
        "tool_choice": request.get("tool_choice"),
        "tool_calls": extract_tool_calls(response),
        "tool_results": extract_tool_results(normalized_messages),
        "assistant": normalized_assistant,
        "usage": record.get("usage"),
        "finish_reason": record.get("finish_reason"),
    }


def update_trajectory(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    if path.exists():
        trajectory = json.loads(path.read_text(encoding="utf-8"))
    else:
        trajectory = {
            "task_id": record.get("task_id"),
            "session_id": record.get("session_id"),
            "started_at": record.get("timestamp"),
            "rounds": [],
        }
    trajectory["updated_at"] = record.get("timestamp")
    trajectory["rounds"].append(build_round(record))
    trajectory["round_count"] = len(trajectory["rounds"])
    write_json(path, trajectory)
    write_json(path.with_name(f"{path.stem}_messages.json"), build_messages_file(trajectory))
    return trajectory
