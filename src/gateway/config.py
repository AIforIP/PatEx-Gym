from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class GatewayConfig:
    host: str
    port: int
    log_dir: Path
    raw_dir: Path
    trajectory_dir: Path
    timeout_seconds: float


@dataclass(frozen=True)
class UpstreamConfig:
    base_url: str
    api_key: str
    model: str | None
    endpoint: str


@dataclass(frozen=True)
class AppConfig:
    gateway: GatewayConfig
    upstream: UpstreamConfig


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _env(name: str, default: Any = None) -> Any:
    value = os.getenv(name)
    return default if value in (None, "") else value


def load_config(path: str | Path | None = None) -> AppConfig:
    cfg_path = Path(path or _env("GATEWAY_CONFIG", ROOT / "configs" / "config.yaml"))
    data = _read_yaml(cfg_path)
    gateway = data.get("gateway", {})
    upstream = data.get("openai", data.get("upstream", {}))

    log_dir = Path(_env("GATEWAY_LOG_DIR", gateway.get("log_dir", ROOT / "logs")))
    raw_dir = Path(_env("GATEWAY_RAW_DIR", gateway.get("raw_dir", ROOT / "raw")))
    trajectory_dir = Path(_env("GATEWAY_TRAJECTORY_DIR", gateway.get("trajectory_dir", ROOT / "trajectories")))

    return AppConfig(
        gateway=GatewayConfig(
            host=str(_env("GATEWAY_HOST", gateway.get("host", "127.0.0.1"))),
            port=int(_env("GATEWAY_PORT", gateway.get("port", 8000))),
            log_dir=log_dir,
            raw_dir=raw_dir,
            trajectory_dir=trajectory_dir,
            timeout_seconds=float(_env("GATEWAY_TIMEOUT_SECONDS", gateway.get("timeout_seconds", 180))),
        ),
        upstream=UpstreamConfig(
            base_url=str(_env("REAL_BASE_URL", upstream.get("base_url", "https://api.openai.com"))).rstrip("/"),
            api_key=str(_env("REAL_API_KEY", upstream.get("api_key", ""))),
            model=_env("REAL_MODEL", upstream.get("model")),
            endpoint=str(_env("REAL_ENDPOINT", upstream.get("endpoint", "/v1/chat/completions"))),
        ),
    )
