from __future__ import annotations

import asyncio
import dataclasses
import json
import os
import shutil
import tempfile
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse


async def run() -> None:
    # Real experiments live under src/gateway/test_output. Unit tests must never
    # delete or mix synthetic fixtures into that evidence directory.
    base = Path(tempfile.mkdtemp(prefix="patex-gateway-tests-"))
    os.environ["GATEWAY_RAW_DIR"] = str(base / "raw")
    os.environ["GATEWAY_TRAJECTORY_DIR"] = str(base / "trajectories")
    os.environ["GATEWAY_LOG_DIR"] = str(base / "logs")
    os.environ["REAL_BASE_URL"] = "http://upstream.local"
    os.environ["REAL_API_KEY"] = "test-key"
    os.environ["MAX_INTERACTION_TURNS"] = "50"
    os.environ["MODEL_MAX_OUTPUT_TOKENS"] = "32768"
    os.environ["GATEWAY_CHAT_REASONING_EFFORT_ENABLED"] = "false"
    os.environ["GATEWAY_CHAT_REASONING_HISTORY_MODE"] = "auto"
    os.environ["GATEWAY_REASONING_MODE"] = "replay"
    os.environ["GATEWAY_TRANSIENT_400_MAX_RETRIES"] = "2"
    os.environ["GATEWAY_TRANSIENT_400_RETRY_BASE_SECONDS"] = "0"
    os.environ["GATEWAY_CHAT_STREAM_USAGE"] = "auto"
    os.environ["GATEWAY_PROVIDER_CONTEXT_WINDOW"] = "262144"
    os.environ["GATEWAY_CONTEXT_SAFETY_MARGIN"] = "16384"

    upstream = FastAPI()
    upstream_counts = {"chat": 0, "responses": 0, "messages": 0}
    observed_output_limits = {"chat": [], "responses": []}
    observed_output_limit_fields = {"chat": [], "responses": []}
    observed_temperatures = {"chat": [], "responses": []}
    observed_chat_bodies = []
    observed_chat_content_types = []
    observed_upstream_session_ids = []
    observed_responses_bodies = []
    observed_messages_bodies = []
    transient_attempts = {
        "plain_stream": 0,
        "deterministic": 0,
        "unsupported_stream_options": 0,
    }

    @upstream.post("/v1/chat/completions")
    async def completion(request: Request):
        upstream_counts["chat"] += 1
        observed_chat_content_types.append(request.headers.getlist("content-type"))
        observed_upstream_session_ids.append(request.headers.get("session_id"))
        if request.headers.get("session_id") is not None:
            return PlainTextResponse("Bad Request", status_code=400)
        body = await request.json()
        observed_chat_bodies.append(body)
        if body.get("model") == "kimi-strict-history-model":
            historical_tool_calls = [
                message for message in body.get("messages") or []
                if message.get("role") == "assistant" and message.get("tool_calls")
            ]
            if historical_tool_calls:
                if not historical_tool_calls[-1].get("reasoning_content"):
                    return JSONResponse(
                        {"error": {"message": "thinking is enabled but reasoning_content is missing"}},
                        status_code=400,
                    )
                strict_response = {
                    "id": "chatcmpl_strict_done",
                    "object": "chat.completion",
                    "choices": [{
                        "index": 0,
                        "message": {"role": "assistant", "content": "done"},
                        "finish_reason": "stop",
                    }],
                    "usage": {"prompt_tokens": 12, "completion_tokens": 1, "total_tokens": 13},
                }
            else:
                strict_response = {
                    "id": "chatcmpl_strict_tool",
                    "object": "chat.completion",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "reasoning_content": "Strict first-round reasoning.",
                            "reasoning_details": [{
                                "type": "reasoning.text",
                                "text": "Strict first-round reasoning.",
                                "index": 0,
                            }],
                            "tool_calls": [{
                                "id": "call_strict",
                                "type": "function",
                                "function": {
                                    "name": "read_file",
                                    "arguments": "{\"path\":\"test.txt\"}",
                                },
                            }],
                        },
                        "finish_reason": "tool_calls",
                    }],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14},
                }
            if body.get("stream"):
                from fastapi.responses import StreamingResponse

                async def strict_events():
                    message = strict_response["choices"][0]["message"]
                    initial_delta = {
                        key: message[key]
                        for key in ("role", "content", "reasoning_content", "reasoning_details", "tool_calls")
                        if key in message
                    }
                    yield (
                        "data: "
                        + json.dumps({"choices": [{"delta": initial_delta, "finish_reason": None}]})
                        + "\n\n"
                    ).encode()
                    yield (
                        "data: "
                        + json.dumps({
                            "choices": [{
                                "delta": {},
                                "finish_reason": strict_response["choices"][0]["finish_reason"],
                            }],
                            "usage": strict_response["usage"],
                        })
                        + "\n\n"
                    ).encode()
                    yield b"data: [DONE]\n\n"

                return StreamingResponse(strict_events(), media_type="text/event-stream")
            return strict_response
        if body.get("model") == "transient-plain-stream-model":
            transient_attempts["plain_stream"] += 1
            if transient_attempts["plain_stream"] == 1:
                return PlainTextResponse("Bad Request", status_code=400)
        if body.get("model") == "deterministic-400-model":
            transient_attempts["deterministic"] += 1
            return JSONResponse(
                {"error": {"message": "Unexpected message role"}},
                status_code=400,
            )
        if body.get("model") == "unsupported-stream-options-model":
            transient_attempts["unsupported_stream_options"] += 1
            if "stream_options" in body:
                return JSONResponse(
                    {
                        "error": {
                            "message": "Unsupported parameter: stream_options"
                        }
                    },
                    status_code=400,
                )
        if "reasoning" in body:
            return JSONResponse(
                {"error": {"message": "Responses-style reasoning is not allowed"}},
                status_code=400,
            )
        observed_temperatures["chat"].append(body.get("temperature"))
        observed_output_limits["chat"].append(body.get("max_tokens"))
        observed_output_limit_fields["chat"].append(
            {key for key in body if key in {"max_tokens", "max_completion_tokens", "max_output_tokens"}}
        )
        if body.get("model") == "dsml-tool-model":
            return {
                "id": "chatcmpl_dsml",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": (
                                '<｜DSML｜tool_calls><｜DSML｜invoke name="es_paper_bool_search">'
                                '<｜DSML｜parameter name="query" string="true">'
                                'authors:&quot;Yoshua Bengio&quot;</｜DSML｜parameter>'
                                '<｜DSML｜parameter name="size" string="false">1</｜DSML｜parameter>'
                                '</｜DSML｜invoke></｜DSML｜tool_calls>'
                            ),
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
            }
        if body.get("stream"):
            from fastapi.responses import StreamingResponse

            async def events():
                if body.get("model") == "dsml-stream-tool-model":
                    yield b'data: {"choices":[{"delta":{"role":"assistant","reasoning":"Use tool","reasoning_details":[{"type":"reasoning.text","text":"Use tool"}]},"finish_reason":null}]}\n\n'
                    for content_delta in (
                        '<｜DSML｜tool_calls><｜DSML｜invoke name="es_paper_bool_search">',
                        '<｜DSML｜parameter name="query" string="true">authors_text:"Yoshua Bengio"</｜DSML｜parameter>',
                        '<｜DSML｜parameter name="size" string="false">1</｜DSML｜parameter></｜DSML｜invoke></｜DSML｜tool_calls>',
                    ):
                        yield (
                            "data: "
                            + json.dumps(
                                {"choices": [{"delta": {"content": content_delta}, "finish_reason": None}]}
                            )
                            + "\n\n"
                        ).encode()
                    yield b'data: {"choices":[{"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":8,"total_tokens":18}}\n\n'
                    yield b"data: [DONE]\n\n"
                    return
                if body.get("model") == "anthropic-stream-tool-model":
                    yield b'data: {"choices":[{"delta":{"role":"assistant"},"finish_reason":null}]}\n\n'
                    yield b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_stream_tool","type":"function","function":{"name":"es_paper_bool_search","arguments":"{\\\"query\\\":"}}]},"finish_reason":null}]}\n\n'
                    yield b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"\\\"authors_text:\\\"Yoshua Bengio\\\"\\\",\\\"size\\\":1}"}}]},"finish_reason":null}]}\n\n'
                    yield b'data: {"choices":[{"delta":{},"finish_reason":"tool_calls"}],"usage":{"prompt_tokens":10,"completion_tokens":8,"total_tokens":18}}\n\n'
                    yield b"data: [DONE]\n\n"
                    return
                if body.get("model") == "missing-stream-usage-model":
                    yield b'data: {"choices":[{"delta":{"role":"assistant","content":"no usage"},"finish_reason":"stop"}]}\n\n'
                    yield b"data: [DONE]\n\n"
                    return
                yield b'data: {"choices":[{"delta":{"role":"assistant"},"finish_reason":null}]}\n\n'
                yield b'data: {"choices":[{"delta":{"content":"stream ok"},"finish_reason":null}]}\n\n'
                yield b'data: {"choices":[{"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":2,"completion_tokens":1,"total_tokens":3}}\n\n'
                yield b"data: [DONE]\n\n"

            return StreamingResponse(events(), media_type="text/event-stream")
        if body.get("tools"):
            message = {
                "role": "assistant",
                "content": None,
                "reasoning_content": "I should inspect the requested file.",
                "reasoning_details": [{"type": "reasoning.text", "text": "I should inspect the requested file."}],
                "tool_calls": [
                    {
                        "id": "call_test",
                        "type": "function",
                        "function": {"name": "read_file", "arguments": "{\"path\":\"test.txt\"}"},
                    }
                ],
            }
            finish = "tool_calls"
        else:
            message = {
                "role": "assistant",
                "content": "ok",
                "reasoning_content": "I can answer directly.",
                "reasoning_details": [{"type": "reasoning.text", "text": "I can answer directly."}],
            }
            finish = "stop"
        return {
            "id": "chatcmpl_test",
            "object": "chat.completion",
            "choices": [{"index": 0, "message": message, "finish_reason": finish}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
        }

    @upstream.post("/v1/responses")
    async def responses(request: Request):
        upstream_counts["responses"] += 1
        body = await request.json()
        observed_responses_bodies.append(body)
        observed_temperatures["responses"].append(body.get("temperature"))
        observed_output_limits["responses"].append(body.get("max_output_tokens"))
        observed_output_limit_fields["responses"].append(
            {key for key in body if key in {"max_tokens", "max_completion_tokens", "max_output_tokens"}}
        )
        completed = {
            "id": "resp_test",
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "responses ok"}],
                },
                {
                    "id": "rs_test",
                    "type": "reasoning",
                    "status": "completed",
                    "summary": [{"type": "summary_text", "text": "Checked the available evidence."}],
                    "encrypted_content": "opaque-provider-reasoning-state",
                },
                {
                    "id": "fc_test",
                    "type": "function_call",
                    "call_id": "call_codex_test",
                    "name": "es_patent_bm25_search",
                    "arguments": "{\"query\":\"test\"}",
                    "status": "completed",
                },
            ],
            "usage": {"input_tokens": 4, "output_tokens": 2, "total_tokens": 6},
        }
        if body.get("model") == "responses-dsml-model":
            completed["output"] = [
                {
                    "id": "msg_dsml_responses",
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": (
                                '<｜DSML｜tool_calls><｜DSML｜invoke name="patent__es_paper_bool_search">'
                                '<｜DSML｜parameter name="query" string="true">authors_text:&quot;Yoshua Bengio&quot;</｜DSML｜parameter>'
                                '<｜DSML｜parameter name="size" string="false">1</｜DSML｜parameter>'
                                '</｜DSML｜invoke></｜DSML｜tool_calls>'
                            ),
                        }
                    ],
                }
            ]
        elif body.get("model") == "responses-native-namespace-model":
            completed["output"] = [
                {
                    "id": "fc_native_namespace",
                    "type": "function_call",
                    "call_id": "call_native_namespace",
                    "name": "es_paper_semantic_search",
                    "arguments": "{\"query\":\"microfluidic droplets\"}",
                    "status": "completed",
                }
            ]
        if body.get("stream"):
            from fastapi.responses import StreamingResponse

            async def events():
                yield b'data: {"type":"response.output_text.delta","delta":"responses stream ok"}\n\n'
                yield ("data: " + json.dumps({"type": "response.completed", "response": completed}) + "\n\n").encode()

            return StreamingResponse(events(), media_type="text/event-stream")
        return completed

    @upstream.post("/v1/messages")
    async def native_messages(request: Request):
        upstream_counts["messages"] += 1
        body = await request.json()
        observed_messages_bodies.append(body)
        if body.get("stream"):
            from fastapi.responses import StreamingResponse

            async def native_message_events():
                events = [
                    {"type": "message_start", "message": {"id": "msg_native_stream", "type": "message", "role": "assistant", "content": []}},
                    {"type": "content_block_start", "index": 0, "content_block": {"type": "thinking", "thinking": "", "signature": ""}},
                    {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "claude-private-stream-thinking"}},
                    {"type": "content_block_delta", "index": 0, "delta": {"type": "signature_delta", "signature": "claude-private-stream-signature"}},
                    {"type": "content_block_stop", "index": 0},
                    {"type": "message_stop"},
                ]
                for event in events:
                    yield ("event: " + event["type"] + "\ndata: " + json.dumps(event) + "\n\n").encode()

            return StreamingResponse(native_message_events(), media_type="text/event-stream")
        return {
            "id": "msg_native_test",
            "type": "message",
            "role": "assistant",
            "model": body.get("model"),
            "content": [
                {
                    "type": "thinking",
                    "thinking": "claude-private-thinking-response",
                    "signature": "claude-private-signature-response",
                },
                {"type": "text", "text": "native messages ok"},
            ],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 4, "output_tokens": 2},
        }

    from . import app as gateway_app

    transport = httpx.ASGITransport(app=upstream)
    original = httpx.AsyncClient

    class RoutedClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    httpx.AsyncClient = RoutedClient
    try:
        app = gateway_app.app
        client = original(transport=httpx.ASGITransport(app=app), base_url="http://gateway.local")
        demos = json.loads(Path(__file__).with_name("demo_requests.json").read_text(encoding="utf-8"))
        for demo in demos:
            response = await client.post(
                "/v1/chat/completions",
                json=demo["body"],
                headers={"x-session-id": "demo_session", "x-task-id": "demo_task"},
            )
            assert response.status_code == 200, response.text

        # PI's session_id header is consumed for local trajectory grouping but
        # must never be leaked to an upstream that rejects unknown headers.
        pi_session_id = "01a05b50-1111-4222-8333-abcdefabcdef"
        response = await client.post(
            "/v1/chat/completions",
            json={"model": "pi-session-header-model", "messages": [{"role": "user", "content": "test"}]},
            headers={"session_id": pi_session_id},
        )
        assert response.status_code == 200, response.text
        assert observed_upstream_session_ids[-1] is None
        pi_session_trajectory = base / "trajectories" / f"{pi_session_id}.json"
        assert pi_session_trajectory.exists()
        assert json.loads(pi_session_trajectory.read_text(encoding="utf-8"))["session_id"] == pi_session_id
        response = await client.post(
            "/v1/chat/completions",
            json={
                "model": "gpt-4.1",
                "stream": True,
                "messages": [{"role": "user", "content": "stream"}],
            },
            headers={"x-session-id": "demo_session", "x-task-id": "demo_task"},
        )
        assert response.status_code == 200, response.text
        assert "stream ok" in response.text
        response = await client.post(
            "/v1/chat/completions",
            json={
                "model": "dsml-stream-tool-model",
                "stream": True,
                "messages": [{"role": "user", "content": "find the paper"}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "es_paper_bool_search",
                            "description": "Search papers",
                            "parameters": {"type": "object"},
                        },
                    }
                ],
            },
            headers={"x-session-id": "dsml_stream_session", "x-task-id": "dsml_stream_task"},
        )
        assert response.status_code == 200, response.text
        assert '"tool_calls"' in response.text
        assert "<｜DSML｜tool_calls>" not in response.text
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-5.2-codex",
                "instructions": "You are the exact Codex system instruction.",
                "input": [{"role": "user", "content": [{"type": "input_text", "text": "hello codex"}]}],
                "tools": [{"type": "function", "name": "es_patent_bm25_search", "parameters": {"type": "object"}}],
            },
            headers={"x-session-id": "codex_session", "x-task-id": "codex_task"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["output"][0]["content"][0]["text"] == "responses ok"
        response = await client.post(
            "/v1/responses",
            json={"model": "gpt-5.2-codex", "stream": True, "input": "stream codex"},
            headers={"x-session-id": "codex_session", "x-task-id": "codex_task"},
        )
        assert response.status_code == 200, response.text
        assert "responses stream ok" in response.text
        response = await client.post(
            "/v1/responses",
            json={
                "model": "responses-dsml-model",
                "stream": True,
                "input": "find a paper",
                "tools": [
                    {
                        "type": "namespace",
                        "name": "patent",
                        "description": "Patent and paper retrieval",
                        "tools": [
                            {"type": "function", "name": "es_paper_bool_search", "parameters": {"type": "object"}}
                        ],
                    }
                ],
            },
            headers={"x-session-id": "codex_dsml_session", "x-task-id": "codex_dsml_task"},
        )
        assert response.status_code == 200, response.text
        assert '"type": "function_call"' in response.text
        assert '"name": "es_paper_bool_search"' in response.text
        assert '"namespace": "patent"' in response.text
        assert "<｜DSML｜tool_calls>" not in response.text
        response = await client.post(
            "/v1/responses",
            json={
                "model": "responses-native-namespace-model",
                "stream": True,
                "input": "find a paper",
                "tools": [
                    {
                        "type": "namespace",
                        "name": "patent",
                        "tools": [
                            {"type": "function", "name": "es_paper_semantic_search", "parameters": {"type": "object"}}
                        ],
                    }
                ],
            },
            headers={"x-session-id": "codex_native_namespace_session", "x-task-id": "codex_task"},
        )
        assert response.status_code == 200, response.text
        assert '"name": "es_paper_semantic_search"' in response.text
        assert '"namespace": "patent"' in response.text
        native_namespace_wire = observed_responses_bodies[-1]
        assert [tool["name"] for tool in native_namespace_wire["tools"]] == [
            "es_paper_semantic_search"
        ]
        assert all(tool["type"] == "function" for tool in native_namespace_wire["tools"])
        assert native_namespace_wire["tool_choice"] == "auto"

        # Native Responses mode supplies automatic tool routing when PI omits
        # tool_choice, while preserving explicit choices and empty tool lists.
        assert gateway_app._ensure_responses_tool_choice(
            {"tools": [{"type": "function", "name": "search"}]}
        )["tool_choice"] == "auto"
        gateway_app.TOOL_CHOICE_OVERRIDE = "required"
        assert gateway_app._ensure_responses_tool_choice(
            {"tools": [{"type": "function", "name": "search"}]}
        )["tool_choice"] == "required"
        assert gateway_app._responses_request_to_chat(
            {"model": "override-model", "input": "search", "tools": [{"type": "function", "name": "search"}]}
        )["tool_choice"] == "required"
        gateway_app.TOOL_CHOICE_OVERRIDE = ""
        explicit_choice = {"tools": [{"type": "function", "name": "search"}], "tool_choice": "required"}
        assert gateway_app._ensure_responses_tool_choice(explicit_choice) is explicit_choice
        empty_tools = {"tools": []}
        assert "tool_choice" not in gateway_app._ensure_responses_tool_choice(empty_tools)

        # When environment preparation selected Chat fallback, a Responses
        # client request is translated once and still counts as one turn.
        gateway_app.RESPONSES_UPSTREAM_MODE = "chat"
        chat_before_fallback = upstream_counts["chat"]
        responses_before_fallback = upstream_counts["responses"]
        response = await client.post(
            "/v1/responses",
            json={
                "model": "chat-only-model",
                "instructions": "Use the available tools.",
                "input": [
                    {"role": "user", "content": [{"type": "input_text", "text": "inspect"}]},
                    {"type": "reasoning", "summary": [{"type": "summary_text", "text": "private summary"}]},
                    {"role": "assistant", "content": [{"type": "output_text", "text": "continuing"}]},
                    {"role": "user", "content": [{"type": "input_text", "text": "the patent"}]},
                ],
                "max_output_tokens": 512,
                "reasoning": {"effort": "xhigh", "summary": "auto"},
                "include": ["reasoning.encrypted_content"],
                "store": False,
                "prompt_cache_key": "responses-only-cache-key",
                "client_metadata": {"session_id": "responses-only-session"},
                "tools": [
                    {
                        "type": "namespace",
                        "name": "patent",
                        "tools": [
                            {
                                "type": "function",
                                "name": "read_file",
                                "description": "Read a file",
                                "parameters": {
                                    "type": "object",
                                    "properties": {"path": {"type": "string"}},
                                },
                            }
                        ],
                    }
                ],
            },
            headers={"x-session-id": "responses_chat_fallback", "x-task-id": "fallback_task"},
        )
        assert response.status_code == 200, response.text
        fallback_body = response.json()
        fallback_call = next(item for item in fallback_body["output"] if item["type"] == "function_call")
        assert fallback_call["name"] == "read_file"
        assert fallback_call["call_id"] == "call_test"
        assert fallback_call["namespace"] == "patent"
        fallback_wire = observed_chat_bodies[-1]
        assert "reasoning_effort" not in fallback_wire
        assert not ({"reasoning", "include", "store", "prompt_cache_key", "client_metadata"} & fallback_wire.keys())
        assert all("reasoning_details" not in message for message in fallback_wire["messages"])
        assert all("reasoning_content" not in message for message in fallback_wire["messages"])
        assert observed_chat_content_types[-1] == ["application/json"]
        assert upstream_counts["chat"] == chat_before_fallback + 1
        assert upstream_counts["responses"] == responses_before_fallback

        role_normalized = gateway_app._responses_request_to_chat(
            {
                "model": "siflow-chat-model",
                "instructions": "System policy.",
                "input": [
                    {"role": "developer", "content": "Task-specific policy."},
                    {"role": "user", "content": "First user fragment."},
                    {"role": "user", "content": "Second user fragment."},
                ],
                "reasoning": {"effort": "high"},
            }
        )
        assert [message["role"] for message in role_normalized["messages"]] == ["system", "user"]
        assert role_normalized["messages"][0]["content"] == "System policy.\n\nTask-specific policy."
        assert role_normalized["messages"][1]["content"] == "First user fragment.\n\nSecond user fragment."
        assert "reasoning_effort" not in role_normalized
        gateway_app.CHAT_REASONING_EFFORT_ENABLED = True
        assert gateway_app._responses_request_to_chat(
            {"model": "reasoning-chat-model", "input": "test", "reasoning": {"effort": "high"}}
        )["reasoning_effort"] == "high"
        gateway_app.CHAT_REASONING_EFFORT_ENABLED = False

        compact_translation = gateway_app._responses_request_to_chat(
            {
                "model": "GLM-5.3-FP8",
                "input": [{"role": "user", "content": "compact history"}],
                "tools": [],
                "tool_choice": "auto",
            }
        )
        assert "tools" not in compact_translation
        assert "tool_choice" not in compact_translation

        tool_translation = gateway_app._responses_request_to_chat(
            {
                "model": "GLM-5.3-FP8",
                "input": "search",
                "tools": [
                    {
                        "type": "function",
                        "name": "search_patents",
                        "parameters": {"type": "object", "properties": {}},
                    }
                ],
                "tool_choice": "auto",
            }
        )
        assert tool_translation["tools"]
        assert tool_translation["tool_choice"] == "auto"

        stream_translation = gateway_app._responses_request_to_chat(
            {"model": "stream-model", "stream": True, "input": "test"}
        )
        assert stream_translation["stream_options"] == {"include_usage": True}
        gateway_app._chat_stream_usage_capability = False
        assert "stream_options" not in gateway_app._responses_request_to_chat(
            {"model": "stream-model", "stream": True, "input": "test"}
        )
        gateway_app.CHAT_STREAM_USAGE_MODE = "required"
        assert gateway_app._responses_request_to_chat(
            {"model": "stream-model", "stream": True, "input": "test"}
        )["stream_options"] == {"include_usage": True}
        gateway_app.CHAT_STREAM_USAGE_MODE = "disabled"
        assert "stream_options" not in gateway_app._responses_request_to_chat(
            {"model": "stream-model", "stream": True, "input": "test"}
        )
        gateway_app.CHAT_STREAM_USAGE_MODE = "auto"
        gateway_app._chat_stream_usage_capability = None
        assert gateway_app._responses_usage_from_chat(
            {
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120,
                }
            }
        ) == {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120}
        assert gateway_app._responses_usage_from_chat(
            {"usage": {"prompt_tokens": 100, "completion_tokens": 20}}
        ) == {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120}
        for incomplete_usage in (
            {},
            {"usage": {"total_tokens": 120}},
            {"usage": {"prompt_tokens": 100, "total_tokens": 120}},
            {"usage": {"completion_tokens": 20, "total_tokens": 120}},
            {"usage": {"prompt_tokens": -1, "completion_tokens": 20}},
        ):
            assert gateway_app._responses_usage_from_chat(incomplete_usage) is None
            assert "usage" not in gateway_app._chat_response_to_responses(
                {"choices": [], **incomplete_usage}, {}
            )
        assert gateway_app._is_unsupported_stream_options_400(
            400,
            [b'{"error":{"message":"Unsupported parameter: stream_options"}}'],
        )
        assert not gateway_app._is_unsupported_stream_options_400(
            400, [b'{"error":{"message":"Unexpected message role"}}']
        )
        assert not gateway_app._is_unsupported_stream_options_400(
            400,
            [b'data: {"error":{"message":"Unsupported parameter: stream_options"}}\n\n'],
        )
        safe_budget = gateway_app._context_budget_status(
            {"input_tokens": 212991, "output_tokens": 1, "total_tokens": 212992}
        )
        exhausted_budget = gateway_app._context_budget_status(
            {"input_tokens": 212992, "output_tokens": 1, "total_tokens": 212993}
        )
        assert safe_budget is not None and safe_budget["within_budget"] is True
        assert exhausted_budget is not None and exhausted_budget["within_budget"] is False

        # A narrowly recognized transient 400 is retried internally before any
        # SSE bytes reach the agent. It remains one model-interaction turn and
        # one trajectory round, while a structured deterministic 400 is final.
        chat_before_retry = upstream_counts["chat"]
        turns_before_retry = gateway_app._interaction_turn_count
        response = await client.post(
            "/v1/responses",
            json={"model": "transient-plain-stream-model", "stream": True, "input": "retry once"},
            headers={"x-session-id": "transient_retry_session", "x-task-id": "fallback_task"},
        )
        assert response.status_code == 200, response.text
        assert "stream ok" in response.text
        assert transient_attempts["plain_stream"] == 2
        assert upstream_counts["chat"] == chat_before_retry + 2
        assert gateway_app._interaction_turn_count == turns_before_retry + 1

        # In auto mode, only an explicit pre-stream stream_options rejection
        # triggers one compatibility retry. The endpoint capability is cached.
        gateway_app._chat_stream_usage_capability = None
        response = await client.post(
            "/v1/responses",
            json={
                "model": "unsupported-stream-options-model",
                "stream": True,
                "input": "retry without stream options",
            },
            headers={"x-session-id": "stream_usage_fallback", "x-task-id": "fallback_task"},
        )
        assert response.status_code == 200, response.text
        assert transient_attempts["unsupported_stream_options"] == 2
        assert "stream_options" in observed_chat_bodies[-2]
        assert "stream_options" not in observed_chat_bodies[-1]
        response = await client.post(
            "/v1/responses",
            json={
                "model": "unsupported-stream-options-model",
                "stream": True,
                "input": "use cached capability",
            },
            headers={"x-session-id": "stream_usage_cached", "x-task-id": "fallback_task"},
        )
        assert response.status_code == 200, response.text
        assert transient_attempts["unsupported_stream_options"] == 3
        assert "stream_options" not in observed_chat_bodies[-1]

        # Missing usage is unknown, not zero. Auto/required mode fails clearly
        # rather than returning a fabricated Responses usage object to Codex.
        gateway_app._chat_stream_usage_capability = None
        response = await client.post(
            "/v1/responses",
            json={"model": "missing-stream-usage-model", "stream": True, "input": "test"},
            headers={"x-session-id": "stream_usage_missing", "x-task-id": "fallback_task"},
        )
        assert response.status_code == 502, response.text
        assert response.json()["error"]["type"] == "upstream_usage_missing"

        response = await client.post(
            "/v1/responses",
            json={"model": "deterministic-400-model", "input": "do not retry"},
            headers={"x-session-id": "deterministic_400_session", "x-task-id": "fallback_task"},
        )
        assert response.status_code == 400, response.text
        assert transient_attempts["deterministic"] == 1

        assert gateway_app._is_retryable_transient_400(400, [b"Bad Request"])
        assert gateway_app._is_retryable_transient_400(
            400,
            [
                b'{"error":{"message":"Received Model Group=qwen; '
                b'Available Model Group Fallbacks=None"}}'
            ],
        )
        assert not gateway_app._is_retryable_transient_400(
            400, [b'{"error":{"message":"Unexpected message role"}}']
        )
        assert not gateway_app._is_retryable_transient_400(401, [b"Bad Request"])

        chat_before_anthropic_stream = upstream_counts["chat"]
        response = await client.post(
            "/v1/responses",
            json={
                "model": "anthropic-stream-tool-model",
                "stream": True,
                "input": "find the paper",
                "tools": [
                    {
                        "type": "function",
                        "name": "es_paper_bool_search",
                        "parameters": {"type": "object"},
                    }
                ],
            },
            headers={"x-session-id": "responses_chat_fallback_stream", "x-task-id": "fallback_task"},
        )
        assert response.status_code == 200, response.text
        assert '"type": "response.completed"' in response.text
        assert '"name": "es_paper_bool_search"' in response.text
        assert upstream_counts["chat"] == chat_before_anthropic_stream + 1
        assert upstream_counts["responses"] == responses_before_fallback
        gateway_app.RESPONSES_UPSTREAM_MODE = "responses"

        # Codex path, closed-loop: the first converted Chat response is replayed
        # exactly as Responses output on round two. The strict mock rejects the
        # request unless reasoning_content reaches the provider-bound tool call.
        gateway_app.RESPONSES_UPSTREAM_MODE = "chat"
        first_codex = await client.post(
            "/v1/responses",
            json={
                "model": "kimi-strict-history-model",
                "stream": True,
                "input": [{"role": "user", "content": "inspect"}],
                "tools": [{"type": "function", "name": "read_file", "parameters": {"type": "object"}}],
            },
            headers={"x-session-id": "kimi_codex_history", "x-task-id": "fallback_task"},
        )
        assert first_codex.status_code == 200, first_codex.text
        first_codex_events = [
            json.loads(line[5:].strip())
            for line in first_codex.text.splitlines()
            if line.startswith("data:") and line[5:].strip() not in {"", "[DONE]"}
        ]
        first_codex_body = next(
            event["response"] for event in first_codex_events
            if event.get("type") == "response.completed"
        )
        assert any(event.get("type") == "response.reasoning_summary_text.delta" for event in first_codex_events)
        first_call = next(item for item in first_codex_body["output"] if item["type"] == "function_call")
        response = await client.post(
            "/v1/responses",
            json={
                "model": "kimi-strict-history-model",
                "stream": True,
                "input": [
                    {"role": "user", "content": "inspect"},
                    *first_codex_body["output"],
                    {
                        "type": "function_call_output",
                        "call_id": first_call["call_id"],
                        "output": "contents",
                    },
                ],
                "tools": [{"type": "function", "name": "read_file", "parameters": {"type": "object"}}],
            },
            headers={"x-session-id": "kimi_codex_history", "x-task-id": "fallback_task"},
        )
        assert response.status_code == 200, response.text
        second_codex_events = [
            json.loads(line[5:].strip())
            for line in response.text.splitlines()
            if line.startswith("data:") and line[5:].strip() not in {"", "[DONE]"}
        ]
        second_codex_body = next(
            event["response"] for event in second_codex_events
            if event.get("type") == "response.completed"
        )
        assert any(
            item.get("type") == "message"
            and item.get("content", [{}])[0].get("text") == "done"
            for item in second_codex_body["output"]
        )
        kimi_codex_wire = observed_chat_bodies[-1]
        kimi_codex_assistant = next(
            message
            for message in kimi_codex_wire["messages"]
            if message.get("role") == "assistant" and message.get("tool_calls")
        )
        assert kimi_codex_assistant["reasoning_content"] == "Strict first-round reasoning."

        # PI OpenAI-Completions path: PI preserves OpenRouter replay state in
        # reasoning_details but some strict backends require the readable
        # reasoning_content field as well. The gateway derives it without
        # dropping the signed/structured details.
        first_pi = await client.post(
            "/v1/chat/completions",
            json={
                "model": "kimi-strict-history-model",
                "messages": [{"role": "user", "content": "inspect"}],
                "tools": [{
                    "type": "function",
                    "function": {"name": "read_file", "parameters": {"type": "object"}},
                }],
            },
            headers={"x-session-id": "kimi_pi_history", "x-task-id": "pi_task"},
        )
        assert first_pi.status_code == 200, first_pi.text
        first_pi_message = first_pi.json()["choices"][0]["message"]
        pi_reasoning_details = first_pi_message["reasoning_details"]
        response = await client.post(
            "/v1/chat/completions",
            json={
                "model": "kimi-strict-history-model",
                "messages": [
                    {"role": "user", "content": "inspect"},
                    {
                        "role": "assistant",
                        "content": None,
                        "reasoning_content": "",
                        "reasoning_details": pi_reasoning_details,
                        "tool_calls": first_pi_message["tool_calls"],
                    },
                    {"role": "tool", "tool_call_id": "call_strict", "content": "contents"},
                ],
            },
            headers={"x-session-id": "kimi_pi_history", "x-task-id": "pi_task"},
        )
        assert response.status_code == 200, response.text
        kimi_pi_assistant = next(
            message
            for message in observed_chat_bodies[-1]["messages"]
            if message.get("role") == "assistant" and message.get("tool_calls")
        )
        assert kimi_pi_assistant["reasoning_content"] == "Strict first-round reasoning."
        assert kimi_pi_assistant["reasoning_details"] == pi_reasoning_details

        for known_model in ("kimi-k2.6", "deepseek-v4-flash", "qwen3.6-35b"):
            assert gateway_app._should_preserve_chat_reasoning(known_model)

        # Auto mode must remain conservative for other Chat backends. Operators
        # can explicitly select preserve after probing their provider.
        assert "reasoning_content" not in gateway_app._chat_compatible_messages(
            [{
                "role": "assistant",
                "content": None,
                "reasoning_content": "do not forward automatically",
                "tool_calls": [],
            }],
            preserve_reasoning_content=False,
        )[0]

        # Buffered Chat fallback must expose reasoning through the standard
        # Responses reasoning-summary event sequence consumed by Codex.
        reasoning_response = gateway_app._chat_response_to_responses(
            {
                "model": "kimi-k2.6",
                "choices": [{
                    "message": {"role": "assistant", "reasoning_content": "Complete reasoning."},
                    "finish_reason": "stop",
                }],
            },
            {"model": "kimi-k2.6"},
        )
        reasoning_sse = b"".join(
            gateway_app._responses_sse_from_completed(reasoning_response)
        ).decode("utf-8")
        assert '"type": "response.reasoning_summary_part.added"' in reasoning_sse
        assert '"type": "response.reasoning_summary_text.delta"' in reasoning_sse
        assert '"delta": "Complete reasoning."' in reasoning_sse
        assert '"type": "response.reasoning_summary_text.done"' in reasoning_sse
        assert '"type": "response.reasoning_summary_part.done"' in reasoning_sse
        gateway_app.RESPONSES_UPSTREAM_MODE = "responses"

        response = await client.post(
            "/v1/chat/completions",
            json={
                "model": "dsml-tool-model",
                "messages": [{"role": "user", "content": "find the paper"}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "es_paper_bool_search",
                            "description": "Search papers",
                            "parameters": {"type": "object"},
                        },
                    }
                ],
            },
            headers={"x-session-id": "dsml_session", "x-task-id": "dsml_task"},
        )
        assert response.status_code == 200, response.text
        dsml_message = response.json()["choices"][0]["message"]
        assert dsml_message["content"] is None
        assert dsml_message["tool_calls"][0]["function"]["name"] == "es_paper_bool_search"
        assert json.loads(dsml_message["tool_calls"][0]["function"]["arguments"]) == {
            "query": 'authors:"Yoshua Bengio"',
            "size": 1,
        }
        response = await client.post(
            "/v1/messages",
            json={
                "model": "anthropic/claude-sonnet-4.6",
                "system": "You are Claude Code.",
                "messages": [{"role": "user", "content": "Hello from Claude"}],
                "max_tokens": 128,
            },
            headers={"x-session-id": "anthropic_session", "x-task-id": "anthropic_task"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["type"] == "message"
        anthropic_thinking = next(block for block in data["content"] if block["type"] == "thinking")
        assert anthropic_thinking["thinking"] == "I can answer directly."
        assert next(block for block in data["content"] if block["type"] == "text")["text"] == "ok"
        response = await client.post(
            "/v1/messages",
            json={
                "model": "anthropic/claude-sonnet-4.6",
                "messages": [{"role": "user", "content": "Read test.txt"}],
                "max_tokens": 128,
                "tools": [
                    {
                        "name": "read_file",
                        "description": "Read a file",
                        "input_schema": {
                            "type": "object",
                            "properties": {"path": {"type": "string"}},
                            "required": ["path"],
                        },
                    }
                ],
            },
            headers={"x-session-id": "anthropic_session", "x-task-id": "anthropic_task"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        anthropic_tool = next(block for block in data["content"] if block["type"] == "tool_use")
        anthropic_tool_thinking = next(block for block in data["content"] if block["type"] == "thinking")
        assert anthropic_tool_thinking["thinking"] == "I should inspect the requested file."

        # PI Anthropic path must turn its saved thinking block back into the
        # structured Chat replay metadata on the next tool-result round.
        response = await client.post(
            "/v1/messages",
            json={
                "model": "anthropic/claude-sonnet-4.6",
                "messages": [
                    {"role": "user", "content": "Read test.txt"},
                    {
                        "role": "assistant",
                        "content": [anthropic_tool_thinking, anthropic_tool],
                    },
                    {
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": anthropic_tool["id"],
                            "content": "test contents",
                        }],
                    },
                ],
                "max_tokens": 128,
            },
            headers={"x-session-id": "anthropic_reasoning_replay", "x-task-id": "anthropic_task"},
        )
        assert response.status_code == 200, response.text
        anthropic_replay_assistant = next(
            message
            for message in observed_chat_bodies[-1]["messages"]
            if message.get("role") == "assistant" and message.get("tool_calls")
        )
        assert anthropic_replay_assistant["reasoning_details"][0]["text"] == (
            "I should inspect the requested file."
        )

        # Parallel Claude tool calls must remain two adjacent tool messages.
        # Folding multiple tool_result blocks into a user message makes native
        # Anthropic backends reject the next turn as an unmatched tool_use.
        parallel_tool_uses = [
            {"type": "tool_use", "id": "call_parallel_a", "name": "read_file", "input": {"path": "a.txt"}},
            {"type": "tool_use", "id": "call_parallel_b", "name": "read_file", "input": {"path": "b.txt"}},
        ]
        response = await client.post(
            "/v1/messages",
            json={
                "model": "anthropic/claude-sonnet-4.6",
                "messages": [
                    {"role": "user", "content": "Read both files"},
                    {"role": "assistant", "content": parallel_tool_uses},
                    {
                        "role": "user",
                        "content": [
                            {"type": "tool_result", "tool_use_id": "call_parallel_a", "content": "A"},
                            {"type": "tool_result", "tool_use_id": "call_parallel_b", "content": "B"},
                        ],
                    },
                ],
                "max_tokens": 128,
            },
            headers={"x-session-id": "anthropic_parallel_results", "x-task-id": "anthropic_task"},
        )
        assert response.status_code == 200, response.text
        parallel_wire_messages = observed_chat_bodies[-1]["messages"]
        assert [message["role"] for message in parallel_wire_messages[-3:]] == [
            "assistant", "tool", "tool"
        ]
        assert [message["tool_call_id"] for message in parallel_wire_messages[-2:]] == [
            "call_parallel_a", "call_parallel_b"
        ]
        assert [message["content"] for message in parallel_wire_messages[-2:]] == ["A", "B"]

        response = await client.post(
            "/v1/messages",
            json={
                "model": "dsml-tool-model",
                "messages": [{"role": "user", "content": "find the paper"}],
                "max_tokens": 128,
                "tools": [
                    {
                        "name": "es_paper_bool_search",
                        "description": "Search papers",
                        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
                    }
                ],
            },
            headers={"x-session-id": "anthropic_dsml_session", "x-task-id": "anthropic_dsml_task"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["stop_reason"] == "tool_use"
        assert data["content"][0]["type"] == "tool_use"
        assert data["content"][0]["name"] == "es_paper_bool_search"
        assert data["content"][0]["input"] == {"query": 'authors:"Yoshua Bengio"', "size": 1}
        response = await client.post(
            "/v1/messages",
            json={
                "model": "anthropic/claude-sonnet-4.6",
                "messages": [{"role": "user", "content": "stream"}],
                "max_tokens": 128,
                "stream": True,
            },
            headers={"x-session-id": "anthropic_session", "x-task-id": "anthropic_task"},
        )
        assert response.status_code == 200, response.text
        assert "message_start" in response.text
        assert "stream ok" in response.text
        response = await client.post(
            "/v1/messages",
            json={
                "model": "anthropic-stream-tool-model",
                "messages": [{"role": "user", "content": "find the paper"}],
                "max_tokens": 128,
                "stream": True,
                "tools": [
                    {
                        "name": "es_paper_bool_search",
                        "description": "Search papers",
                        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
                    }
                ],
            },
            headers={"x-session-id": "anthropic_stream_tool_session", "x-task-id": "anthropic_stream_tool_task"},
        )
        assert response.status_code == 200, response.text
        assert '"type": "tool_use"' in response.text
        assert '"type": "input_json_delta"' in response.text
        assert '"stop_reason": "tool_use"' in response.text
        response = await client.post(
            "/v1/messages",
            json={
                "model": "dsml-stream-tool-model",
                "messages": [{"role": "user", "content": "find the paper"}],
                "max_tokens": 128,
                "stream": True,
                "tools": [
                    {
                        "name": "es_paper_bool_search",
                        "description": "Search papers",
                        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
                    }
                ],
            },
            headers={"x-session-id": "anthropic_dsml_stream_session", "x-task-id": "anthropic_dsml_stream_task"},
        )
        assert response.status_code == 200, response.text
        assert '"type": "tool_use"' in response.text
        assert '"name": "es_paper_bool_search"' in response.text
        assert '"type": "thinking"' in response.text
        assert '"type": "thinking_delta"' in response.text
        assert '"thinking": "Use tool"' in response.text
        assert '"type": "signature_delta"' in response.text
        assert "<｜DSML｜tool_calls>" not in response.text

        # Native mode is selected explicitly by deployment configuration, not
        # by matching model names. Native state remains intact on the wire and
        # is replaced by metadata in every persisted artifact.
        gateway_app.REASONING_MODE = "native_passthrough"
        gateway_app.RESPONSES_UPSTREAM_MODE = "responses"
        native_gpt_input = {
            "id": "rs_input_native",
            "type": "reasoning",
            "status": "completed",
            "summary": [{"type": "summary_text", "text": "gpt-private-summary-input"}],
            "encrypted_content": "gpt-private-encrypted-input",
        }
        response = await client.post(
            "/v1/responses",
            json={
                "model": "configured-native-responses-model",
                "input": [{"role": "user", "content": "continue"}, native_gpt_input],
            },
            headers={
                "x-request-id": "native_gpt_passthrough",
                "x-session-id": "native_gpt_session",
                "x-task-id": "native_gpt_task",
            },
        )
        assert response.status_code == 200, response.text
        assert native_gpt_input in observed_responses_bodies[-1]["input"]
        native_gpt_output = next(
            item for item in response.json()["output"] if item.get("type") == "reasoning"
        )
        assert native_gpt_output["encrypted_content"] == "opaque-provider-reasoning-state"
        assert native_gpt_output["summary"][0]["text"] == "Checked the available evidence."
        response = await client.post(
            "/v1/responses",
            json={
                "model": "configured-native-responses-model",
                "stream": True,
                "input": [{"role": "user", "content": "stream"}, native_gpt_input],
            },
            headers={
                "x-request-id": "native_gpt_stream_passthrough",
                "x-session-id": "native_gpt_stream_session",
                "x-task-id": "native_gpt_task",
            },
        )
        assert response.status_code == 200, response.text
        assert "opaque-provider-reasoning-state" in response.text
        gpt_stream_artifacts = [
            base / "raw" / "native_gpt_stream_passthrough_request.json",
            base / "raw" / "native_gpt_stream_passthrough_client_request.json",
            base / "raw" / "native_gpt_stream_passthrough_response.json",
            base / "trajectories" / "native_gpt_stream_session.json",
            base / "trajectories" / "native_gpt_stream_session_messages.json",
        ]
        gpt_stream_artifacts.extend((base / "model_io").rglob("native_gpt_stream_passthrough.*"))
        assert "opaque-provider-reasoning-state" not in "\n".join(
            path.read_text(encoding="utf-8") for path in gpt_stream_artifacts if path.exists()
        )
        gpt_artifacts = [
            base / "raw" / "native_gpt_passthrough_request.json",
            base / "raw" / "native_gpt_passthrough_client_request.json",
            base / "raw" / "native_gpt_passthrough_response.json",
            base / "trajectories" / "native_gpt_session.json",
            base / "trajectories" / "native_gpt_session_messages.json",
        ]
        gpt_artifacts.extend((base / "model_io").rglob("native_gpt_passthrough.*"))
        gpt_log_text = "\n".join(
            path.read_text(encoding="utf-8") for path in gpt_artifacts if path.exists()
        )
        for secret in (
            "gpt-private-summary-input",
            "gpt-private-encrypted-input",
            "opaque-provider-reasoning-state",
            "Checked the available evidence.",
        ):
            assert secret not in gpt_log_text
        assert '"reasoning_type": "native"' in gpt_log_text
        assert '"reasoning_id": "rs_test"' in gpt_log_text

        original_config = gateway_app.config
        gateway_app.config = dataclasses.replace(
            gateway_app.config,
            upstream=dataclasses.replace(gateway_app.config.upstream, endpoint="*"),
        )
        native_claude_block = {
            "type": "thinking",
            "thinking": "claude-private-thinking-input",
            "signature": "claude-private-signature-input",
        }
        native_claude_tool = {
            "type": "tool_use",
            "id": "call_native_claude",
            "name": "read_file",
            "input": {"path": "test.txt"},
        }
        response = await client.post(
            "/v1/messages",
            json={
                "model": "configured-native-messages-model",
                "thinking": {"type": "adaptive"},
                "output_config": {"effort": "max"},
                "messages": [
                    {"role": "user", "content": "inspect"},
                    {"role": "assistant", "content": [native_claude_block, native_claude_tool]},
                    {
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": "call_native_claude",
                            "content": "contents",
                        }],
                    },
                ],
                "max_tokens": 128,
            },
            headers={
                "x-request-id": "native_claude_passthrough",
                "x-session-id": "native_claude_session",
                "x-task-id": "native_claude_task",
            },
        )
        assert response.status_code == 200, response.text
        native_claude_wire = observed_messages_bodies[-1]
        assert native_claude_wire["thinking"] == {"type": "adaptive"}
        assert native_claude_wire["output_config"] == {"effort": "max"}
        assert "temperature" not in native_claude_wire
        assert native_claude_wire["messages"][1]["content"] == [
            native_claude_block, native_claude_tool
        ]
        assert native_claude_wire["messages"][2]["content"] == [{
            "type": "tool_result",
            "tool_use_id": "call_native_claude",
            "content": "contents",
        }]
        response_thinking = response.json()["content"][0]
        assert response_thinking["thinking"] == "claude-private-thinking-response"
        assert response_thinking["signature"] == "claude-private-signature-response"
        response = await client.post(
            "/v1/messages",
            json={
                "model": "configured-native-messages-model",
                "stream": True,
                "messages": [{"role": "user", "content": "stream"}],
                "max_tokens": 128,
            },
            headers={
                "x-request-id": "native_claude_stream_passthrough",
                "x-session-id": "native_claude_stream_session",
                "x-task-id": "native_claude_task",
            },
        )
        gateway_app.config = original_config
        assert response.status_code == 200, response.text
        assert "claude-private-stream-thinking" in response.text
        assert "claude-private-stream-signature" in response.text
        claude_stream_artifacts = [
            base / "raw" / "native_claude_stream_passthrough_request.json",
            base / "raw" / "native_claude_stream_passthrough_response.json",
            base / "trajectories" / "native_claude_stream_session.json",
            base / "trajectories" / "native_claude_stream_session_messages.json",
        ]
        claude_stream_artifacts.extend((base / "model_io").rglob("native_claude_stream_passthrough.*"))
        claude_stream_log_text = "\n".join(
            path.read_text(encoding="utf-8") for path in claude_stream_artifacts if path.exists()
        )
        assert "claude-private-stream-thinking" not in claude_stream_log_text
        assert "claude-private-stream-signature" not in claude_stream_log_text
        claude_artifacts = [
            base / "raw" / "native_claude_passthrough_request.json",
            base / "raw" / "native_claude_passthrough_client_request.json",
            base / "raw" / "native_claude_passthrough_response.json",
            base / "trajectories" / "native_claude_session.json",
            base / "trajectories" / "native_claude_session_messages.json",
        ]
        claude_artifacts.extend((base / "model_io").rglob("native_claude_passthrough.*"))
        claude_log_text = "\n".join(
            path.read_text(encoding="utf-8") for path in claude_artifacts if path.exists()
        )
        for secret in (
            "claude-private-thinking-input",
            "claude-private-signature-input",
            "claude-private-thinking-response",
            "claude-private-signature-response",
        ):
            assert secret not in claude_log_text
        assert '"reasoning_type": "native"' in claude_log_text

        assert "private-delta" not in json.dumps(
            gateway_app._native_reasoning_log_view({
                "type": "response.reasoning_summary_text.delta",
                "item_id": "rs_stream",
                "delta": "private-delta",
            })
        )
        assert "private-thinking-delta" not in json.dumps(
            gateway_app._native_reasoning_log_view({
                "type": "content_block_delta",
                "delta": {"type": "thinking_delta", "thinking": "private-thinking-delta"},
            })
        )

        # Chat replay remains independent of native protocol passthrough.
        assert gateway_app._prepare_chat_reasoning_history({
            "model": "kimi-k2.6",
            "messages": [{
                "role": "assistant",
                "content": None,
                "reasoning_content": "chat-replay-remains-enabled",
                "tool_calls": [{"id": "call", "type": "function", "function": {"name": "f", "arguments": "{}"}}],
            }],
        })["messages"][0]["reasoning_content"] == "chat-replay-remains-enabled"
        gateway_app.REASONING_MODE = "replay"

        # The gateway counts provider-bound model requests, not local tool calls.
        # The request after the configured maximum must never reach upstream.
        gateway_app.MAX_INTERACTION_TURNS = 2
        gateway_app._interaction_turn_count = 0
        gateway_app._request_interaction_turns.clear()
        upstream_before_limit_test = upstream_counts["chat"]
        for expected_turn in (1, 2):
            response = await client.post(
                "/v1/chat/completions",
                json={"model": "test-model", "messages": [{"role": "user", "content": str(expected_turn)}]},
                headers={"x-session-id": "turn_limit_session", "x-task-id": "turn_limit_task"},
            )
            assert response.status_code == 200, response.text
        response = await client.post(
            "/v1/chat/completions",
            json={"model": "test-model", "messages": [{"role": "user", "content": "blocked"}]},
            headers={"x-session-id": "turn_limit_session", "x-task-id": "turn_limit_task"},
        )
        assert response.status_code == 429, response.text
        assert response.json()["error"]["type"] == "interaction_turn_limit_reached"
        assert response.headers["x-patex-interaction-turn-limit"] == "2"
        assert upstream_counts["chat"] == upstream_before_limit_test + 2

        gateway_app.MAX_INTERACTION_TURNS = 1
        gateway_app._interaction_turn_count = 0
        gateway_app._request_interaction_turns.clear()
        upstream_before_responses_limit_test = upstream_counts["responses"]
        response = await client.post(
            "/v1/responses",
            json={"model": "test-codex-model", "input": "allowed"},
            headers={"x-session-id": "codex_turn_limit_session", "x-task-id": "codex_turn_limit_task"},
        )
        assert response.status_code == 200, response.text
        response = await client.post(
            "/v1/responses",
            json={"model": "test-codex-model", "input": "blocked"},
            headers={"x-session-id": "codex_turn_limit_session", "x-task-id": "codex_turn_limit_task"},
        )
        assert response.status_code == 429, response.text
        assert response.json()["error"]["type"] == "interaction_turn_limit_reached"
        assert upstream_counts["responses"] == upstream_before_responses_limit_test + 1
        gateway_app.MAX_INTERACTION_TURNS = 50
        await client.aclose()
    finally:
        httpx.AsyncClient = original

    raw = base / "raw" / "raw_request_response.jsonl"
    trajectory = base / "trajectories" / "demo_session.json"
    assert raw.exists(), "raw_request_response.jsonl was not created"
    assert trajectory.exists(), "trajectory was not created"
    lines = raw.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 39, f"expected 39 raw records, got {len(lines)}"
    assert (base / "raw" / "interaction_turn_limit_reached.json").exists()
    traj = json.loads(trajectory.read_text(encoding="utf-8"))
    assert traj["round_count"] == 4
    assert traj["rounds"][1]["tools"], "tool schema was not recorded"
    assert traj["rounds"][1]["tool_calls"], "tool call was not recorded"
    assert traj["rounds"][1]["assistant"]["reasoning_content"] == "I should inspect the requested file."
    assert "reasoning_details" not in traj["rounds"][1]["assistant"]
    anthropic_trajectory = base / "trajectories" / "anthropic_session.json"
    assert anthropic_trajectory.exists(), "anthropic trajectory was not created"
    anthropic_traj = json.loads(anthropic_trajectory.read_text(encoding="utf-8"))
    assert anthropic_traj["round_count"] == 3
    assert anthropic_traj["rounds"][1]["tool_calls"], "anthropic tool_use was not recorded"
    codex_trajectory = base / "trajectories" / "codex_session.json"
    assert codex_trajectory.exists(), "Codex Responses trajectory was not created"
    codex_traj = json.loads(codex_trajectory.read_text(encoding="utf-8"))
    assert codex_traj["round_count"] == 2
    assert codex_traj["rounds"][0]["tools"], "Codex Responses tool schema was not recorded"
    assert codex_traj["rounds"][0]["assistant"]["reasoning_content"] == "Checked the available evidence."
    assert "reasoning_details" not in codex_traj["rounds"][0]["assistant"]
    assert codex_traj["rounds"][0]["assistant"]["tool_calls"][0]["id"] == "call_codex_test"
    assert codex_traj["rounds"][0]["messages"][0] == {
        "role": "system",
        "content": "You are the exact Codex system instruction.",
    }
    assert codex_traj["rounds"][0]["messages"][1]["content"] == "hello codex"
    transient_retry_traj = json.loads(
        (base / "trajectories" / "transient_retry_session.json").read_text(encoding="utf-8")
    )
    assert transient_retry_traj["round_count"] == 1
    assert transient_retry_traj["rounds"][0]["retry_count"] == 1
    codex_dsml_traj = json.loads(
        (base / "trajectories" / "codex_dsml_session.json").read_text(encoding="utf-8")
    )
    assert codex_dsml_traj["rounds"][0]["assistant"]["tool_calls"][0]["function"]["name"] == "es_paper_bool_search"
    dsml_trajectory = json.loads((base / "trajectories" / "dsml_session.json").read_text(encoding="utf-8"))
    dsml_call = dsml_trajectory["rounds"][0]["assistant"]["tool_calls"][0]
    assert dsml_call["function"]["name"] == "es_paper_bool_search"
    dsml_index = next(item for item in (json.loads(line) for line in lines) if item["session_id"] == "dsml_session")
    dsml_wire_response = json.loads((base / "raw" / dsml_index["response_file"]).read_text(encoding="utf-8"))
    assert "<｜DSML｜tool_calls>" in dsml_wire_response["choices"][0]["message"]["content"]
    assert "tool_calls" not in dsml_wire_response["choices"][0]["message"]
    dsml_stream_trajectory = json.loads(
        (base / "trajectories" / "dsml_stream_session.json").read_text(encoding="utf-8")
    )
    assert dsml_stream_trajectory["rounds"][0]["assistant"]["tool_calls"][0]["function"]["name"] == "es_paper_bool_search"
    assert dsml_stream_trajectory["rounds"][0]["assistant"]["reasoning_content"] == "Use tool"
    turn_limit_trajectory = json.loads((base / "trajectories" / "turn_limit_session.json").read_text(encoding="utf-8"))
    assert turn_limit_trajectory["round_count"] == 3
    assert turn_limit_trajectory["rounds"][-1]["status_code"] == 429
    assert turn_limit_trajectory["rounds"][-1]["interaction_turn"] == 3
    codex_turn_limit_trajectory = json.loads(
        (base / "trajectories" / "codex_turn_limit_session.json").read_text(encoding="utf-8")
    )
    assert codex_turn_limit_trajectory["round_count"] == 2
    assert codex_turn_limit_trajectory["rounds"][-1]["status_code"] == 429
    assert codex_turn_limit_trajectory["rounds"][-1]["interaction_turn"] == 2
    model_io = base / "model_io"
    codex_artifacts = sorted((model_io / "gpt-5.2-codex" / "codex_session").glob("*.json"))
    assert len(codex_artifacts) == 2, codex_artifacts
    codex_ios = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in codex_artifacts]
    codex_path, codex_io = next(
        (path, item)
        for path, item in codex_ios
        if "instructions" in json.loads((path.parent / item["wire_request_file"]).read_text(encoding="utf-8"))
    )
    codex_wire_request = json.loads((codex_path.parent / codex_io["wire_request_file"]).read_text(encoding="utf-8"))
    assert codex_wire_request["instructions"] == "You are the exact Codex system instruction."
    assert codex_wire_request["tools"][0]["name"] == "es_patent_bm25_search"
    transcript = (codex_path.parent / codex_io["canonical_transcript_file"]).read_text(encoding="utf-8")
    assert "<|instructions|>" in transcript
    assert "hello codex" in transcript
    assert "responses ok" in transcript
    assert "Checked the available evidence." in transcript
    assert "opaque-provider-reasoning-state" not in transcript
    assert "call_codex_test" in transcript
    assert "EXACT WIRE REQUEST JSON" not in transcript
    anthropic_artifacts = sorted(model_io.glob("anthropic_claude-sonnet-4.6/anthropic_session/*.json"))
    assert len(anthropic_artifacts) == 3, anthropic_artifacts
    anthropic_candidates = []
    for path in anthropic_artifacts:
        item = json.loads(path.read_text(encoding="utf-8"))
        wire = json.loads((path.parent / item["wire_request_file"]).read_text(encoding="utf-8"))
        anthropic_candidates.append((path, item, wire))
    anthropic_path, anthropic_io, anthropic_wire = next(
        candidate for candidate in anthropic_candidates if candidate[2].get("messages", [{}])[0].get("role") == "system"
    )
    assert anthropic_wire["messages"][0]["role"] == "system"
    assert anthropic_wire["messages"][0]["content"] == "You are Claude Code."
    assert "private server-side" in anthropic_io["notice"]
    raw_index = [json.loads(line) for line in lines]
    assert "request" not in raw_index[0] and "response" not in raw_index[0]
    assert raw_index[0]["request_file"].endswith("_request.json")
    demo_messages = json.loads((base / "trajectories" / "demo_session_messages.json").read_text(encoding="utf-8"))["messages"]
    assert any(message.get("tool_calls", [{}])[0].get("id") == "call_demo" for message in demo_messages if message.get("tool_calls"))
    assert any(message.get("reasoning_content") == "I should inspect the requested file." for message in demo_messages)
    assert all("reasoning_details" not in message for message in demo_messages)
    tool_result = next(message for message in demo_messages if message.get("role") == "tool")
    assert tool_result["tool_call_id"] == "call_demo" and tool_result["content"] == "test"
    codex_messages = json.loads((base / "trajectories" / "codex_session_messages.json").read_text(encoding="utf-8"))["messages"]
    assert [message["role"] for message in codex_messages[:3]] == ["system", "user", "assistant"]
    assert codex_messages[0]["content"] == "You are the exact Codex system instruction."
    codex_assistant = next(message for message in codex_messages if message.get("source") == "response")
    assert codex_assistant["reasoning_content"] == "Checked the available evidence."
    assert "reasoning_details" not in codex_assistant
    assert codex_assistant["tool_calls"][0]["function"]["name"] == "es_patent_bm25_search"
    for message in demo_messages + codex_messages:
        assert set(message).issuperset({"role", "source", "round_index", "message_index"})
    assert observed_output_limits["chat"] and set(observed_output_limits["chat"]) == {32768}
    assert observed_output_limits["responses"] and set(observed_output_limits["responses"]) == {32768}
    assert observed_output_limit_fields["chat"] and all(
        fields == {"max_tokens"} for fields in observed_output_limit_fields["chat"]
    )
    assert observed_output_limit_fields["responses"] and all(
        fields == {"max_output_tokens"} for fields in observed_output_limit_fields["responses"]
    )
    assert observed_temperatures["chat"] and set(observed_temperatures["chat"]) == {1}
    assert observed_temperatures["responses"] and set(observed_temperatures["responses"]) == {1}

    # A client normally replays the preceding assistant tool call without the
    # provider-only reasoning fields. Keep the richer response entry exactly
    # once instead of appending the replay as a duplicate assistant message.
    from .trajectory import build_messages_file

    replayed = build_messages_file(
        {
            "task_id": "dedupe-task",
            "session_id": "dedupe-session",
            "rounds": [
                {
                    "messages": [{"role": "user", "content": "search"}],
                    "assistant": {
                        "role": "assistant",
                        "content": None,
                        "reasoning_content": "I should search.",
                        "tool_calls": [
                            {
                                "id": "call_dedupe",
                                "type": "function",
                                "function": {"name": "es_patent_bm25_search", "arguments": "{\"query\":\"x\"}"},
                            }
                        ],
                    },
                },
                {
                    "messages": [
                        {"role": "user", "content": "search"},
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call_dedupe",
                                    "type": "function",
                                    "function": {"name": "es_patent_bm25_search", "arguments": "{\"query\":\"x\"}"},
                                }
                            ],
                        },
                        {"role": "tool", "tool_call_id": "call_dedupe", "content": "result"},
                    ],
                    "assistant": {"role": "assistant", "content": "done"},
                },
            ],
        }
    )["messages"]
    assert [message["role"] for message in replayed] == ["user", "assistant", "tool", "assistant"]
    assert replayed[1]["reasoning_content"] == "I should search."
    assert replayed[1]["tool_calls"][0]["id"] == "call_dedupe"

    # Responses API replay items belonging to one assistant turn must be
    # consolidated before trajectory prefix comparison. Otherwise the response
    # copy and its next-request replay duplicate every Codex tool call.
    from .app import _responses_input_messages

    responses_replay = _responses_input_messages(
        {
            "instructions": "system",
            "input": [
                {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "search"}]},
                {"type": "reasoning", "summary": [{"type": "summary_text", "text": "I should search."}]},
                {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Searching."}]},
                {"type": "function_call", "call_id": "call_responses", "name": "es_patent_bm25_search", "arguments": "{\"query\":\"x\"}"},
                {"type": "function_call_output", "call_id": "call_responses", "output": "result"},
            ],
        }
    )
    assert [message["role"] for message in responses_replay] == ["system", "user", "assistant", "tool"]
    assert responses_replay[2]["content"] == "Searching."
    assert responses_replay[2]["reasoning_content"] == "I should search."
    assert responses_replay[2]["tool_calls"][0]["id"] == "call_responses"
    responses_deduped = build_messages_file(
        {
            "task_id": "responses-dedupe-task",
            "session_id": "responses-dedupe-session",
            "rounds": [
                {
                    "messages": responses_replay[:2],
                    "assistant": responses_replay[2],
                },
                {
                    "messages": responses_replay,
                    "assistant": {"role": "assistant", "content": "done"},
                },
            ],
        }
    )["messages"]
    response_call_ids = [
        call["id"]
        for message in responses_deduped
        for call in message.get("tool_calls", [])
    ]
    assert response_call_ids == ["call_responses"]
    assert [message["role"] for message in responses_deduped] == ["system", "user", "assistant", "tool", "assistant"]

    from .app import _sanitize_responses_tool_outputs, _strip_codex_tool_output_metadata

    wrapped_shell_output = (
        "Chunk ID: 9e23f6\n"
        "Wall time: 0.0000 seconds\n"
        "Process exited with code 0\n"
        "Original token count: 3\n"
        "Output:\nactual shell output\n"
    )
    assert _strip_codex_tool_output_metadata(wrapped_shell_output) == "actual shell output\n"
    assert _strip_codex_tool_output_metadata(
        "Wall time: 0.0129 seconds\nOutput:\n{\"result\":true}"
    ) == '{"result":true}'
    assert _strip_codex_tool_output_metadata("ordinary tool output") == "ordinary tool output"
    sanitized_outputs = _sanitize_responses_tool_outputs(
        {
            "input": [
                {"type": "function_call_output", "call_id": "call_shell", "output": wrapped_shell_output},
                {"role": "user", "content": "Wall time: this is user-authored text"},
            ]
        }
    )
    assert sanitized_outputs["input"][0]["output"] == "actual shell output\n"
    assert sanitized_outputs["input"][1]["content"] == "Wall time: this is user-authored text"

    from .check_upstream_api import mode_for_status

    assert mode_for_status(200) == "responses"
    assert mode_for_status(201) == "responses"
    assert mode_for_status(400) == "chat"
    assert mode_for_status(401) == "chat"
    assert mode_for_status(404) == "chat"
    assert mode_for_status(429) == "chat"
    assert mode_for_status(503) == "chat"
    print("gateway tests passed")
    print(f"raw log: {raw}")
    print(f"trajectory: {trajectory}")
    shutil.rmtree(base)


if __name__ == "__main__":
    asyncio.run(run())
