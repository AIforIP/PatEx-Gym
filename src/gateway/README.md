# Pi Gateway

Transparent proxy for capturing and logging AI agent interactions. The client brings its own API configuration.

## Features

- Transparent proxy - preserves original request headers (Authorization, etc.)
- Request/response logging and trajectory tracking
- Per-model exact observable wire I/O and canonical readable transcripts
- Session-based conversation history
- Works with any OpenAI-compatible API

## Start

```bash
pip install -r requirements.txt
python -m src.gateway.main
```

## Configuration

Configure via environment variables or `src/gateway/configs/config.yaml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `GATEWAY_HOST` | Listen host | `127.0.0.1` |
| `GATEWAY_PORT` | Listen port | `8000` |
| `GATEWAY_LOG_DIR` | Log directory | `src/gateway/logs` |
| `GATEWAY_RAW_DIR` | Raw data directory | `src/gateway/raw` |
| `GATEWAY_TRAJECTORY_DIR` | Trajectory directory | `src/gateway/trajectories` |
| `GATEWAY_TIMEOUT_SECONDS` | Request timeout | `180` |
| `MAX_INTERACTION_TURNS` | Maximum provider-bound model requests per trial | `50` |
| `GATEWAY_CHAT_REASONING_EFFORT_ENABLED` | Forward optional `reasoning_effort` to Chat upstreams | `false` |

## Usage

Point your AI client to the gateway. The client includes its own API key:

```bash
# Example: use gateway as proxy
export OPENAI_BASE_URL="http://127.0.0.1:8000"
export OPENAI_API_KEY="sk-your-key"

# Your AI client sends requests with the API key in Authorization header
```

## Output Files

```
src/gateway/
├── raw/
│   ├── <request_id>_request.json
│   ├── <request_id>_response.json
│   ├── interaction_turn_limit_reached.json
│   └── raw_request_response.jsonl
├── trajectories/
│   ├── <session_id>.json
│   └── <session_id>_messages.json
├── model_io/
│   └── <model>/<session>/
│       ├── <request_id>.json
│       └── <request_id>.txt
└── logs/
    └── gateway.log
```

The raw request/response JSON files preserve the actual upstream payload visible at the
gateway boundary. The model-I/O JSON is a small manifest pointing to those files and their
SHA-256 digests. The OpenAI-format messages and TXT transcript retain reasoning content and
details, tools, tool calls/results, and assistant output in role order; the raw artifacts
remain authoritative for every provider-specific field. The transcript is not labeled as the remote provider's private
server-side tokenizer/chat-template output, because that layer is not exposed by the API.

## Testing

```bash
python -m src.gateway.tests
```
