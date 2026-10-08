#!/bin/bash
set -euo pipefail
mkdir -p /logs/gateway/raw /logs/gateway/trajectories
export PYTHONPATH=/app
export GATEWAY_HOST="${GATEWAY_HOST:-127.0.0.1}"
export GATEWAY_PORT="${GATEWAY_PORT:-7000}"
export GATEWAY_LOG_DIR="${GATEWAY_LOG_DIR:-/logs/gateway}"
export GATEWAY_RAW_DIR="${GATEWAY_RAW_DIR:-/logs/gateway/raw}"
export GATEWAY_TRAJECTORY_DIR="${GATEWAY_TRAJECTORY_DIR:-/logs/gateway/trajectories}"
export REAL_BASE_URL="${REAL_BASE_URL:-https://openrouter.ai/api}"
export REAL_ENDPOINT="${REAL_ENDPOINT:-/v1/chat/completions}"
export REAL_API_KEY="${REAL_API_KEY:-${OPENROUTER_API_KEY:-${OPENAI_API_KEY:-}}}"
exec python3 -m gateway.main
