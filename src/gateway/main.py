from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn

from .app import app, config


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.gateway.host,
        port=config.gateway.port,
    )
