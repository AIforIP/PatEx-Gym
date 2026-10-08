FROM patex-harness-base:latest

ARG CODEX_VERSION=0.151.0
RUN npm install -g "@openai/codex@${CODEX_VERSION}"
ENV CODEX_CLI_VERSION=${CODEX_VERSION}

WORKDIR /app
COPY src/gateway/ /app/gateway/
COPY src/gateway/start_gateway.sh /app/start_gateway.sh
COPY src/harnesses/codex/run.py /app/run_codex.py
COPY src/harnesses/codex/gpt-5.6-sol-direct-model-catalog.json /app/gpt-5.6-sol-direct-model-catalog.json
COPY src/harnesses/codex/patent_mcp.py /app/patent_mcp.py
COPY src/harnesses/codex/start_agent.sh /app/start_agent.sh
COPY src/harnesses/apply_patch.sh /usr/local/bin/apply_patch
COPY src/harnesses/test_apply_patch.sh /tmp/test_apply_patch.sh
COPY src/elasticsearch/check_ready.py /app/elasticsearch/check_ready.py

RUN chmod 0755 /usr/local/bin/apply_patch /tmp/test_apply_patch.sh \
    && /tmp/test_apply_patch.sh \
    && rm -f /tmp/test_apply_patch.sh \
    && chmod +x /app/run_codex.py /app/patent_mcp.py /app/start_gateway.sh /app/start_agent.sh \
    && mkdir -p /workspace/output /logs/agent /logs/gateway/raw \
       /logs/gateway/trajectories /logs/pi_sessions /logs/verifier \
    && chmod -R 777 /workspace /logs

ENV CODEX_HOME=/tmp/codex-home
WORKDIR /workspace
CMD ["/bin/bash"]
