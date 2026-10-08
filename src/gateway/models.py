from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class RequestMeta:
    task_id: str
    session_id: str
    request_id: str
    timestamp: str
    method: str
    path: str
