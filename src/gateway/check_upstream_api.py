#!/usr/bin/env python3
"""Select the upstream API used behind the local Responses-compatible gateway."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def mode_for_status(status: int) -> str:
    """Use Responses only after a successful, valid Responses request."""
    return "responses" if 200 <= status < 300 else "chat"


def main() -> int:
    configured = os.environ.get("GATEWAY_RESPONSES_UPSTREAM_MODE", "auto").strip().lower()
    if configured in {"responses", "chat"}:
        print(configured)
        return 0
    if configured != "auto":
        print("GATEWAY_RESPONSES_UPSTREAM_MODE must be auto, responses, or chat", file=sys.stderr)
        return 2

    base_url = os.environ.get("MODEL_API_PROBE_BASE_URL", "").rstrip("/")
    api_key = os.environ.get("MODEL_API_PROBE_API_KEY", "")
    model = os.environ.get("MODEL_API_PROBE_MODEL", "").strip()
    timeout = float(os.environ.get("MODEL_API_PROBE_TIMEOUT_SECONDS", "5"))
    if not base_url:
        print("MODEL_API_PROBE_BASE_URL is required", file=sys.stderr)
        return 2
    if not model:
        print("[Model API] no probe model configured; upstream_mode=chat", file=sys.stderr)
        print("chat")
        return 0
    payload = json.dumps(
        {
            "model": model,
            "input": "Reply with OK.",
            "max_output_tokens": 1,
            "stream": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/responses",
        data=payload,
        method="POST",
        headers={
            "content-type": "application/json",
            **({"authorization": f"Bearer {api_key}"} if api_key else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read(4096)
            status, body = response.status, ""
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read(4096).decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        print(
            f"[Model API] /v1/responses probe failed ({exc}); upstream_mode=chat",
            file=sys.stderr,
        )
        print("chat")
        return 0

    mode = mode_for_status(status)
    print(f"[Model API] /v1/responses probe status={status}; upstream_mode={mode}", file=sys.stderr)
    print(mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
