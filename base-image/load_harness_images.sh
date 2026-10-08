#!/usr/bin/env bash
set -euo pipefail
zstd -dc base-image/patex-codex-harness-amd64.tar.zst | docker load
