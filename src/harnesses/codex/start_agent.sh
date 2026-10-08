#!/bin/bash
set -euo pipefail

mkdir -p /workspace/output /logs/agent /logs/gateway/raw /logs/gateway/trajectories /logs/pi_sessions /logs/verifier
GATEWAY_PID=""
cleanup() {
  if [ -n "$GATEWAY_PID" ]; then kill "$GATEWAY_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT
export ES_HOST="${ES_HOST:-http://patex-search:9200}"
export ES_INDEX_PATENTS="${ES_INDEX_PATENTS:-patex-patents-current}"
export ES_INDEX_PAPERS="${ES_INDEX_PAPERS:-patex-papers-current}"
export ES_INDEX_RETRIEVAL_POOL="${ES_INDEX_RETRIEVAL_POOL:-$ES_INDEX_PATENTS}"
export ES_SEMANTIC_INDEX="${ES_SEMANTIC_INDEX:-$ES_INDEX_PATENTS}"
export ES_PAPER_SEMANTIC_INDEX="$ES_INDEX_PAPERS"
export ES_PAPER_SEMANTIC_VECTOR_FIELD="${ES_PAPER_SEMANTIC_VECTOR_FIELD:-${ES_SEMANTIC_VECTOR_FIELD:-bge_m3_dense}}"
export ES_REQUIRED_INDICES="${ES_REQUIRED_INDICES:-$ES_INDEX_PATENTS}"
if [ "${TOOL_PAPER_BM25:-true}" = "true" ] || [ "${TOOL_PAPER_BOOL_SEARCH:-true}" = "true" ] || [ "${TOOL_PAPER_SEMANTIC_SEARCH:-false}" = "true" ]; then
  export ES_REQUIRED_INDICES="${ES_REQUIRED_INDICES},${ES_INDEX_PAPERS}"
fi
if [ "${TOOL_SEMANTIC_SEARCH:-false}" = "true" ] || [ "${TOOL_PAPER_SEMANTIC_SEARCH:-false}" = "true" ]; then
  export ES_BGE_M3_EMBED_URL="${ES_BGE_M3_EMBED_URL:-http://patex-embeddings:8000/v1/embeddings}"
fi
python3 /app/elasticsearch/check_ready.py
if [ -z "${ES_BGE_M3_EMBED_URL:-}" ]; then export TOOL_SEMANTIC_SEARCH=false TOOL_PAPER_SEMANTIC_SEARCH=false; fi
export CODEX_API_KEY="${CODEX_API_KEY:-${OPENROUTER_API_KEY:-${OPENAI_API_KEY:-}}}"
UPSTREAM_CODEX_BASE_URL="${CODEX_BASE_URL:-https://openrouter.ai/api/v1}"
UPSTREAM_CODEX_BASE_URL="${UPSTREAM_CODEX_BASE_URL%/}"
export REAL_BASE_URL="${UPSTREAM_CODEX_BASE_URL%/v1}"
export REAL_ENDPOINT="*"
export REAL_API_KEY="$CODEX_API_KEY"
export CODEX_BASE_URL="${CODEX_GATEWAY_BASE_URL:-http://127.0.0.1:7000/v1}"
configured_responses_mode="${GATEWAY_RESPONSES_UPSTREAM_MODE:-auto}"
export GATEWAY_RESPONSES_UPSTREAM_MODE="$(
  GATEWAY_RESPONSES_UPSTREAM_MODE="$configured_responses_mode" \
  MODEL_API_PROBE_BASE_URL="$UPSTREAM_CODEX_BASE_URL" \
  MODEL_API_PROBE_API_KEY="$CODEX_API_KEY" \
  MODEL_API_PROBE_MODEL="${CODEX_MODEL:-deepseek/deepseek-v4-flash-0731}" \
  python3 /app/gateway/check_upstream_api.py
)"

/app/start_gateway.sh > /logs/gateway/gateway_stdout.log 2>&1 &
GATEWAY_PID=$!
for i in $(seq 1 30); do
  if python3 - <<'PY'
import urllib.request
try:
    urllib.request.urlopen("http://127.0.0.1:7000/health", timeout=1)
except Exception:
    raise SystemExit(1)
PY
  then
    break
  fi
  sleep 1
  if [ "$i" = 30 ]; then
    echo "Codex gateway failed to start" >&2
    cat /logs/gateway/gateway_stdout.log >&2 || true
    exit 1
  fi
done

echo "[ENV CHECK] CODEX_API_KEY length: ${#CODEX_API_KEY}" | tee /logs/agent/env_check.log
echo "[ENV CHECK] CODEX_BASE_URL: ${CODEX_BASE_URL}" | tee -a /logs/agent/env_check.log
echo "[ENV CHECK] UPSTREAM_CODEX_BASE_URL: ${UPSTREAM_CODEX_BASE_URL}" | tee -a /logs/agent/env_check.log
echo "[ENV CHECK] Responses upstream mode: ${GATEWAY_RESPONSES_UPSTREAM_MODE} (pre-agent capability check; not an interaction turn)" | tee -a /logs/agent/env_check.log
echo "[ENV CHECK] Reasoning mode: ${GATEWAY_REASONING_MODE:-replay}" | tee -a /logs/agent/env_check.log
echo "[ENV CHECK] CODEX_MODEL: ${CODEX_MODEL:-deepseek/deepseek-v4-flash-0731}" | tee -a /logs/agent/env_check.log

python3 /app/run_codex.py 2>&1 | tee /logs/agent/codex_inference.log /logs/agent/pi_inference.log
