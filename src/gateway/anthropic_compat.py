from __future__ import annotations

import json
import uuid
from typing import Any


_OPENAI_REASONING_FIELDS = {"reasoning", "reasoning_content", "reasoning_text"}


def _reasoning_projection(message: dict[str, Any]) -> tuple[str, str]:
    """Return readable reasoning and an opaque replay signature for PI."""
    details = message.get("reasoning_details")
    detail_items = details if isinstance(details, list) else ([details] if isinstance(details, dict) else [])
    texts = [
        str(item.get("text"))
        for item in detail_items
        if isinstance(item, dict) and isinstance(item.get("text"), str) and item.get("text")
    ]
    if texts:
        return "".join(texts), json.dumps(detail_items, ensure_ascii=False, separators=(",", ":"))
    for field in ("reasoning_content", "reasoning", "reasoning_text"):
        value = message.get(field)
        if isinstance(value, str) and value:
            return value, field
    return "", ""


def _thinking_replay_fields(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    texts = [
        str(block.get("thinking"))
        for block in blocks
        if block.get("type") == "thinking" and isinstance(block.get("thinking"), str)
        and block.get("thinking")
    ]
    if not texts:
        return {}
    rendered = "\n".join(texts)
    for block in blocks:
        signature = block.get("signature")
        if not isinstance(signature, str) or not signature:
            continue
        if signature in _OPENAI_REASONING_FIELDS:
            return {signature: rendered}
        try:
            details = json.loads(signature)
        except json.JSONDecodeError:
            continue
        if isinstance(details, list):
            return {"reasoning_details": details}
    return {"reasoning_content": rendered}


def _text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            elif item.get("type") == "tool_result":
                parts.append(json.dumps(item, ensure_ascii=False))
        return "\n".join(part for part in parts if part)
    return "" if content is None else str(content)


def anthropic_request_to_openai(body: dict[str, Any], default_model: str | None = None) -> dict[str, Any]:
    messages: list[dict[str, Any]] = []
    system = body.get("system")
    if isinstance(system, str) and system.strip():
        messages.append({"role": "system", "content": system})
    elif isinstance(system, list):
        system_text = _text_from_content(system)
        if system_text:
            messages.append({"role": "system", "content": system_text})

    for message in body.get("messages", []):
        if not isinstance(message, dict):
            continue
        role = message.get("role", "user")
        content = message.get("content")
        if role == "assistant" and isinstance(content, list):
            tool_calls = []
            text_parts = []
            thinking_blocks = []
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "text":
                    text_parts.append(str(item.get("text", "")))
                elif item.get("type") in {"thinking", "redacted_thinking"}:
                    thinking_blocks.append(item)
                elif item.get("type") == "tool_use":
                    tool_calls.append(
                        {
                            "id": item.get("id") or f"call_{uuid.uuid4().hex[:12]}",
                            "type": "function",
                            "function": {
                                "name": item.get("name", "unknown"),
                                "arguments": json.dumps(item.get("input", {}), ensure_ascii=False),
                            },
                        }
                    )
            converted = {"role": "assistant", "content": "\n".join(text_parts) or None}
            if tool_calls:
                converted["tool_calls"] = tool_calls
            converted.update(_thinking_replay_fields(thinking_blocks))
            messages.append(converted)
            continue

        if role == "user" and isinstance(content, list):
            tool_results = [item for item in content if isinstance(item, dict) and item.get("type") == "tool_result"]
            if tool_results:
                for tool_result in tool_results:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_result.get("tool_use_id") or tool_result.get("tool_call_id"),
                            "content": _text_from_content(tool_result.get("content")),
                        }
                    )
                text = "\n".join(
                    str(item.get("text", ""))
                    for item in content
                    if isinstance(item, dict)
                    and item.get("type") == "text"
                    and item.get("text")
                )
                if text:
                    messages.append({"role": "user", "content": text})
                continue

            text = _text_from_content(content)
            if text:
                messages.append(
                    {"role": "user", "content": text}
                )
            continue

        messages.append({"role": role, "content": _text_from_content(content)})

    converted: dict[str, Any] = {
        "model": body.get("model") or default_model,
        "messages": messages,
    }
    for src, dst in {
        "max_tokens": "max_tokens",
        "temperature": "temperature",
        "top_p": "top_p",
        "stop_sequences": "stop",
        "stream": "stream",
    }.items():
        if src in body:
            converted[dst] = body[src]

    tools = body.get("tools")
    if isinstance(tools, list) and tools:
        converted["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": tool.get("name"),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
                },
            }
            for tool in tools
            if isinstance(tool, dict)
        ]
    if "tool_choice" in body:
        choice = body["tool_choice"]
        if isinstance(choice, dict) and choice.get("type") == "tool":
            converted["tool_choice"] = {"type": "function", "function": {"name": choice.get("name")}}
        elif isinstance(choice, dict) and choice.get("type") in {"auto", "any"}:
            converted["tool_choice"] = "auto"
        else:
            converted["tool_choice"] = choice
    return converted


def openai_response_to_anthropic(response: dict[str, Any], request_body: dict[str, Any]) -> dict[str, Any]:
    choice = (response.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content: list[dict[str, Any]] = []
    reasoning, signature = _reasoning_projection(message)
    if reasoning:
        content.append({
            "type": "thinking",
            "thinking": reasoning,
            "signature": signature,
        })
    if message.get("content"):
        content.append({"type": "text", "text": str(message["content"])})
    for call in message.get("tool_calls") or []:
        fn = call.get("function") or {}
        raw_args = fn.get("arguments") or "{}"
        try:
            parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except json.JSONDecodeError:
            parsed_args = {"_raw": raw_args}
        content.append(
            {
                "type": "tool_use",
                "id": call.get("id") or f"call_{uuid.uuid4().hex[:12]}",
                "name": fn.get("name") or call.get("name", "unknown"),
                "input": parsed_args or {},
            }
        )
    finish_reason = choice.get("finish_reason")
    stop_reason = "tool_use" if finish_reason == "tool_calls" else "end_turn"
    usage = response.get("usage") or {}
    return {
        "id": response.get("id") or f"msg_{uuid.uuid4().hex}",
        "type": "message",
        "role": "assistant",
        "model": response.get("model") or request_body.get("model"),
        "content": content,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        },
    }


def sse_event(event: str, data: dict[str, Any]) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


def openai_stream_to_anthropic_chunks(lines: list[str], request_body: dict[str, Any]) -> tuple[list[bytes], dict[str, Any]]:
    message_id = f"msg_{uuid.uuid4().hex}"
    chunks = [
        sse_event(
            "message_start",
            {
                "type": "message_start",
                "message": {
                    "id": message_id,
                    "type": "message",
                    "role": "assistant",
                    "model": request_body.get("model"),
                    "content": [],
                    "stop_reason": None,
                    "stop_sequence": None,
                    "usage": {"input_tokens": 0, "output_tokens": 0},
                },
            },
        )
    ]
    text_parts: list[str] = []
    reasoning_parts: list[str] = []
    reasoning_details: list[dict[str, Any]] = []
    tool_calls: dict[int, dict[str, Any]] = {}
    usage = None
    finish_reason = None
    for line in lines:
        if not line.startswith("data:"):
            continue
        raw = line[5:].strip()
        if not raw or raw == "[DONE]":
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        usage = event.get("usage") or usage
        choices = event.get("choices")
        if not isinstance(choices, list) or not choices:
            continue
        choice = choices[0] if isinstance(choices[0], dict) else {}
        finish_reason = choice.get("finish_reason") or finish_reason
        delta = choice.get("delta") if isinstance(choice.get("delta"), dict) else {}
        text = delta.get("content")
        if isinstance(text, str) and text:
            text_parts.append(text)
        for field in ("reasoning_content", "reasoning", "reasoning_text"):
            reasoning = delta.get(field)
            if isinstance(reasoning, str) and reasoning:
                reasoning_parts.append(reasoning)
                break
        details = delta.get("reasoning_details")
        if isinstance(details, dict):
            reasoning_details.append(details)
        elif isinstance(details, list):
            reasoning_details.extend(item for item in details if isinstance(item, dict))
        for call_delta in delta.get("tool_calls") or []:
            if not isinstance(call_delta, dict):
                continue
            call_index = int(call_delta.get("index", 0))
            call = tool_calls.setdefault(
                call_index,
                {"id": "", "name": "", "arguments": ""},
            )
            if call_delta.get("id"):
                call["id"] = str(call_delta["id"])
            function = call_delta.get("function")
            if isinstance(function, dict):
                if function.get("name"):
                    call["name"] += str(function["name"])
                if function.get("arguments"):
                    call["arguments"] += str(function["arguments"])

    content: list[dict[str, Any]] = []
    block_index = 0
    if reasoning_parts or reasoning_details:
        reasoning = "".join(reasoning_parts)
        if not reasoning:
            reasoning = "".join(
                str(item.get("text"))
                for item in reasoning_details
                if isinstance(item.get("text"), str)
            )
        signature = (
            json.dumps(reasoning_details, ensure_ascii=False, separators=(",", ":"))
            if reasoning_details
            else "reasoning_content"
        )
        chunks.append(
            sse_event(
                "content_block_start",
                {
                    "type": "content_block_start",
                    "index": block_index,
                    "content_block": {"type": "thinking", "thinking": "", "signature": ""},
                },
            )
        )
        if reasoning:
            chunks.append(
                sse_event(
                    "content_block_delta",
                    {
                        "type": "content_block_delta",
                        "index": block_index,
                        "delta": {"type": "thinking_delta", "thinking": reasoning},
                    },
                )
            )
        chunks.append(
            sse_event(
                "content_block_delta",
                {
                    "type": "content_block_delta",
                    "index": block_index,
                    "delta": {"type": "signature_delta", "signature": signature},
                },
            )
        )
        chunks.append(sse_event("content_block_stop", {"type": "content_block_stop", "index": block_index}))
        content.append({"type": "thinking", "thinking": reasoning, "signature": signature})
        block_index += 1
    if text_parts:
        text = "".join(text_parts)
        chunks.append(
            sse_event(
                "content_block_start",
                {"type": "content_block_start", "index": block_index, "content_block": {"type": "text", "text": ""}},
            )
        )
        chunks.append(
            sse_event(
                "content_block_delta",
                {"type": "content_block_delta", "index": block_index, "delta": {"type": "text_delta", "text": text}},
            )
        )
        chunks.append(sse_event("content_block_stop", {"type": "content_block_stop", "index": block_index}))
        content.append({"type": "text", "text": text})
        block_index += 1

    for _, call in sorted(tool_calls.items()):
        call_id = call["id"] or f"call_{uuid.uuid4().hex[:12]}"
        call_name = call["name"] or "unknown"
        raw_arguments = call["arguments"] or "{}"
        try:
            parsed_arguments = json.loads(raw_arguments)
        except json.JSONDecodeError:
            parsed_arguments = {"_raw": raw_arguments}
        chunks.append(
            sse_event(
                "content_block_start",
                {
                    "type": "content_block_start",
                    "index": block_index,
                    "content_block": {"type": "tool_use", "id": call_id, "name": call_name, "input": {}},
                },
            )
        )
        chunks.append(
            sse_event(
                "content_block_delta",
                {
                    "type": "content_block_delta",
                    "index": block_index,
                    "delta": {"type": "input_json_delta", "partial_json": raw_arguments},
                },
            )
        )
        chunks.append(sse_event("content_block_stop", {"type": "content_block_stop", "index": block_index}))
        content.append(
            {"type": "tool_use", "id": call_id, "name": call_name, "input": parsed_arguments or {}}
        )
        block_index += 1

    stop_reason = "tool_use" if tool_calls or finish_reason == "tool_calls" else "end_turn"
    chunks.extend(
        [
            sse_event(
                "message_delta",
                {
                    "type": "message_delta",
                    "delta": {"stop_reason": stop_reason, "stop_sequence": None},
                    "usage": {"output_tokens": (usage or {}).get("completion_tokens", 0)},
                },
            ),
            sse_event("message_stop", {"type": "message_stop"}),
        ]
    )
    summary = {
        "id": message_id,
        "type": "message",
        "role": "assistant",
        "model": request_body.get("model"),
        "content": content,
        "stop_reason": stop_reason,
        "usage": {
            "input_tokens": (usage or {}).get("prompt_tokens", 0),
            "output_tokens": (usage or {}).get("completion_tokens", 0),
        },
    }
    return chunks, summary
