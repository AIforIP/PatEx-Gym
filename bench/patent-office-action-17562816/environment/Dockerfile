FROM patex-codex-harness:latest

COPY workspace/input/ /workspace/input/

RUN mkdir -p /workspace/output /logs/agent /logs/gateway/raw /logs/gateway/trajectories /logs/verifier && chmod -R 777 /workspace /logs

WORKDIR /workspace
CMD ["/bin/bash"]
