from __future__ import annotations

import time
from typing import Any

import httpx

from .config import AppConfig


def upstream_url(config: AppConfig, path: str, query: str = "") -> str:
    endpoint = config.upstream.endpoint or f"/{path.lstrip('/')}"
    if endpoint == "*":
        endpoint = f"/{path.lstrip('/')}"
    url = f"{config.upstream.base_url}{endpoint if endpoint.startswith('/') else '/' + endpoint}"
    return f"{url}?{query}" if query else url


def forward_headers(headers: dict[str, str], api_key: str) -> dict[str, str]:
    # The inbound header mapping is normally lower-case (Starlette), while the
    # header we add below is title-case.  Exclude content-type explicitly so
    # HTTPX can never merge the two values into an invalid media type.
    excluded = {
        "host",
        "content-length",
        "content-type",
        "transfer-encoding",
        "connection",
        # PI uses this non-standard header for local session correlation.
        # Some OpenAI-compatible upstreams reject it deterministically.
        "session_id",
    }
    if api_key:
        excluded.add("authorization")
    out = {k: v for k, v in headers.items() if k.lower() not in excluded}
    out["Content-Type"] = "application/json"
    if api_key:
        out["Authorization"] = f"Bearer {api_key}"
    return out


async def forward_request(
    *,
    config: AppConfig,
    method: str,
    path: str,
    query: str = "",
    headers: dict[str, str],
    body: bytes,
) -> tuple[int, dict[str, str], bytes, float]:
    started = time.perf_counter()
    async with httpx.AsyncClient(timeout=config.gateway.timeout_seconds) as client:
        response = await client.request(
            method,
            upstream_url(config, path, query),
            headers=forward_headers(headers, config.upstream.api_key),
            content=body,
        )
    latency_ms = (time.perf_counter() - started) * 1000
    return response.status_code, dict(response.headers), response.content, latency_ms


def response_metadata(response_body: Any) -> dict[str, Any]:
    if not isinstance(response_body, dict):
        return {"usage": None, "finish_reason": None}
    choices = response_body.get("choices")
    finish_reason = None
    if isinstance(choices, list) and choices:
        first = choices[0] if isinstance(choices[0], dict) else {}
        finish_reason = first.get("finish_reason")
    return {
        "usage": response_body.get("usage"),
        "finish_reason": finish_reason or response_body.get("stop_reason"),
    }
