from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import tomllib
except ImportError:  # Python 3.10 and earlier in development environments.
    import tomli as tomllib

from . import run


class CodexConfigTest(unittest.TestCase):
    def render_with_home(self, environment: dict[str, str]) -> tuple[dict, Path]:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, environment, clear=True
        ):
            home = Path(directory)
            run.write_codex_config(home, ["es_patent_bm25_search"])
            config = tomllib.loads((home / "config.toml").read_text(encoding="utf-8"))
            return config, home

    def render(self, environment: dict[str, str]) -> dict:
        config, _ = self.render_with_home(environment)
        return config

    def test_config_without_reasoning_effort_uses_provider_default(self) -> None:
        config = self.render({})
        self.assertNotIn("model_reasoning_effort", config)
        self.assertEqual(config["model_context_window"], 131072)

    def test_config_with_reasoning_effort_is_valid_and_explicit(self) -> None:
        config = self.render(
            {
                "AGENT_REASONING_EFFORT": "max",
                "CODEX_MODEL": "deepseek/deepseek-v4-flash-0731",
            }
        )
        self.assertEqual(config["model_reasoning_effort"], "xhigh")
        self.assertEqual(config["model_context_window"], 131072)

    def test_gpt_5_6_sol_uses_standard_responses_tool_catalog(self) -> None:
        config = self.render({"CODEX_MODEL": "gpt-5.6-sol"})
        catalog_path = Path(config["model_catalog_json"])
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["models"]), 1)
        model = catalog["models"][0]
        self.assertEqual(model["slug"], "gpt-5.6-sol")
        self.assertEqual(model["tool_mode"], "direct")
        self.assertIs(model["use_responses_lite"], False)
        self.assertTrue(model["model_messages"]["instructions_template"])

    def test_other_models_do_not_receive_catalog_override(self) -> None:
        config = self.render({"CODEX_MODEL": "qwen3.6-35b-a3b"})
        self.assertNotIn("model_catalog_json", config)


if __name__ == "__main__":
    unittest.main()
