from __future__ import annotations

import json
import hashlib
import os
import re
from pathlib import Path
from typing import Any

from .logger import write_json
from .trajectory import extract_response_message, normalize_openai_messages


NOTICE = (
    "This captures the exact observable HTTP request/response at the model-provider "
    "boundary. canonical_transcript is a faithful readable projection; the referenced "
    "wire JSON files are the lossless record. It is "
    "not the provider's private server-side tokenizer/chat-template output."
)
NATIVE_REASONING_NOTICE = (
    "This captures the observable HTTP request/response at the model-provider "
    "boundary with native reasoning payloads replaced by non-sensitive metadata. "
    "The provider-bound and client-bound protocol values were passed through "
    "unchanged; encrypted_content, thinking, and signature are intentionally not "
    "persisted. canonical_transcript is a readable redacted projection."
)


def _safe(value: Any, fallback: str) -> str:
    rendered = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return rendered[:160] or fallback


def _pretty(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _render_message(message: dict[str, Any]) -> str:
    role = str(message.get("role") or "unknown")
    parts = [f"<|{role}|>"]
    if message.get("reasoning_content") is not None:
        parts.extend(["[reasoning_content]", _pretty(message.get("reasoning_content"))])
    if message.get("reasoning") is not None and message.get("reasoning_content") is None:
        parts.extend(["[reasoning]", _pretty(message.get("reasoning"))])
    if message.get("content") is not None:
        parts.append(_pretty(message.get("content")))
    if message.get("refusal") is not None:
        parts.extend(["[refusal]", _pretty(message.get("refusal"))])
    if message.get("audio") is not None:
        parts.extend(["[audio]", _pretty(message.get("audio"))])
    if message.get("tool_calls"):
        parts.extend(["[tool_calls]", _pretty(message.get("tool_calls"))])
    if message.get("tool_call_id"):
        parts.insert(1, f"[tool_call_id={message['tool_call_id']}]")
    return "\n".join(parts)


def canonical_transcript(request_body: Any, response_body: Any) -> str:
    request = request_body if isinstance(request_body, dict) else {"raw": request_body}
    messages = normalize_openai_messages(request.get("messages") or [])
    sections = ["=== CANONICAL MODEL INPUT ==="]
    if request.get("instructions") is not None:
        sections.extend(["<|instructions|>", _pretty(request.get("instructions"))])
    if request.get("tools"):
        sections.extend(["<|tools|>", _pretty(request.get("tools"))])
    if request.get("tool_choice") is not None:
        sections.extend(["<|tool_choice|>", _pretty(request.get("tool_choice"))])
    sections.extend(_render_message(message) for message in messages)
    if not messages and request.get("input") is not None:
        sections.extend(["<|input|>", _pretty(request.get("input"))])

    sections.append("=== CANONICAL MODEL OUTPUT ===")
    response = response_body if isinstance(response_body, dict) else {"raw": response_body}
    assistant = extract_response_message(response)
    if assistant:
        sections.append(_render_message(normalize_openai_messages([assistant])[0]))
    elif response.get("response") is not None:
        sections.extend(["<|response|>", _pretty(response.get("response"))])
    else:
        sections.extend(["<|response|>", _pretty(response_body)])
    return "\n\n".join(section for section in sections if section)


def save_model_io(
    root: Path,
    record: dict[str, Any],
    request_path: Path,
    response_path: Path,
) -> None:
    model = _safe(record.get("model"), "unknown-model")
    session = _safe(record.get("session_id"), "default")
    request_id = _safe(record.get("request_id"), "request")
    target = root / model / session
    notice = (
        NATIVE_REASONING_NOTICE
        if record.get("reasoning_capture") == "metadata_only"
        else NOTICE
    )
    transcript = canonical_transcript(record.get("request"), record.get("response"))
    request_ref = os.path.relpath(request_path, target)
    response_ref = os.path.relpath(response_path, target)
    artifact = {
        "format": "patex.model-io.v1",
        "notice": notice,
        "reasoning_capture": record.get("reasoning_capture", "full_wire"),
        "timestamp": record.get("timestamp"),
        "task_id": record.get("task_id"),
        "session_id": record.get("session_id"),
        "request_id": record.get("request_id"),
        "model": record.get("model"),
        "endpoint": record.get("path"),
        "status_code": record.get("status_code"),
        "wire_request_file": request_ref,
        "wire_response_file": response_ref,
        "wire_request_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest(),
        "wire_response_sha256": hashlib.sha256(response_path.read_bytes()).hexdigest(),
        "canonical_transcript_file": f"{request_id}.txt",
    }
    write_json(target / f"{request_id}.json", artifact)
    text = "\n".join(
        [
            "PatEx observable model I/O",
            f"model: {record.get('model')}",
            f"endpoint: {record.get('path')}",
            f"request_id: {record.get('request_id')}",
            f"notice: {notice}",
            f"wire_request: {request_ref}",
            f"wire_response: {response_ref}",
            "",
            transcript,
            "",
        ]
    )
    target.mkdir(parents=True, exist_ok=True)
    (target / f"{request_id}.txt").write_text(text, encoding="utf-8")
