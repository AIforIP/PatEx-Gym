"""Harbor agent bridge for the selectable PatEx-Gym harness image."""

from pathlib import Path
from typing import override

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class PatExHarnessAgent(BaseAgent):
    """Pass Harbor's canonical instruction directly to the in-image harness."""

    SUPPORTS_WINDOWS = False

    @staticmethod
    @override
    def name() -> str:
        return "patex-harness"

    @override
    def version(self) -> str:
        return "1.0.0"

    @override
    async def setup(self, environment: BaseEnvironment) -> None:
        return None

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        del context
        host_instruction = Path(self.logs_dir) / "task_instruction.md"
        host_instruction.write_text(instruction, encoding="utf-8")
        container_instruction = "/tmp/patex-task-instruction.md"
        await environment.upload_file(host_instruction, container_instruction)
        result = await environment.exec(
            command="bash /app/start_agent.sh",
            env={"PATEX_INSTRUCTION_FILE": container_instruction},
        )
        if result.return_code != 0:
            limit_check = await environment.exec(
                command="test -f /logs/gateway/raw/interaction_turn_limit_reached.json",
            )
            if limit_check.return_code == 0:
                host_marker = Path(self.logs_dir) / "interaction_turn_limit_scoring.txt"
                host_marker.write_text(
                    "Agent stopped at MAX_INTERACTION_TURNS; Harbor verifier should score existing artifacts.\n",
                    encoding="utf-8",
                )
                return
            raise RuntimeError(f"PatEx harness exited with code {result.return_code}")
