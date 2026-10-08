#!/usr/bin/env python3
"""Run Codex non-interactively inside a Harbor patent task."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


WORKSPACE = Path(os.getenv("WORKSPACE", "/workspace"))
INPUT_DIR = WORKSPACE / "input"
OUTPUT_DIR = WORKSPACE / "output"
INSTRUCTION_FILE = Path(os.getenv("PATEX_INSTRUCTION_FILE", "/tmp/patex-task-instruction.md"))
TIMEOUT_SECONDS = int(
    os.environ.get("CODEX_INFERENCE_TIMEOUT", "").strip()
    or os.environ.get("AGENT_INFERENCE_TIMEOUT", "").strip()
    or "3600"
)
MAX_INTERACTION_TURNS = max(1, int(os.getenv("MAX_INTERACTION_TURNS", "50")))
SUPPORTED_REASONING_EFFORTS = {"minimal", "low", "medium", "high", "xhigh", "max"}
TURN_LIMIT_MARKER = Path("/logs/gateway/raw/interaction_turn_limit_reached.json")
DIRECT_TOOL_MODEL_CATALOGS = {
    "gpt-5.6-sol": Path(__file__).with_name("gpt-5.6-sol-direct-model-catalog.json"),
}


def enabled(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def effective_reasoning_effort(model: str, requested: str) -> str:
    """Use each model family's highest supported effort without changing intent."""
    normalized_model = model.strip().lower()
    if requested == "max" and normalized_model.startswith("deepseek/deepseek-v4-flash"):
        return "xhigh"
    return requested


def discover_patent_file() -> Path:
    configured = os.getenv("INPUT_PATENT_FILE", "").strip()
    if configured:
        path = Path(configured)
        return path if path.is_absolute() else INPUT_DIR / path
    candidates = [path for path in INPUT_DIR.glob("*.md") if path.name not in {"task.md", "instruction.md"}]
    return max(candidates, key=lambda path: path.stat().st_size) if candidates else INPUT_DIR / "patent.md"


def read(path: Path, limit: int = 120_000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:limit] + ("\n\n[TRUNCATED BY HARNESS]\n" if len(text) > limit else "")


def normalize_date(value: str) -> str:
    match = re.search(r"(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})", value or "")
    if not match:
        return ""
    year, month, day = map(int, match.groups())
    return f"{year:04d}-{month:02d}-{day:02d}"


def application_date(patent_file: Path) -> str:
    configured = normalize_date(os.getenv("APPLICATION_DATE", ""))
    if configured:
        return configured
    text = read(patent_file, 20_000)
    labels = "Application Date|Filing Date|申请日|提交日|申请日期"
    match = re.search(rf"(?:{labels})[:：\s-]*(\d{{4}}[-/.年]\d{{1,2}}[-/.月]\d{{1,2}})", text, re.I)
    return normalize_date(match.group(1)) if match else ""


def enabled_tools() -> list[str]:
    names: list[str] = []
    if enabled("TOOL_BM25", "true"):
        names.append("es_patent_bm25_search")
    if enabled("TOOL_BOOL_SEARCH", "true"):
        names.append("es_patent_bool_search")
    if enabled("TOOL_SEMANTIC_SEARCH", "false"):
        names.append("es_patent_semantic_search")
    if names:
        names.extend(["visit_patent_claims", "visit_patent_description"])
    paper_names = []
    if enabled("TOOL_PAPER_BM25", "true"):
        paper_names.append("es_paper_bm25_search")
    if enabled("TOOL_PAPER_BOOL_SEARCH", "true"):
        paper_names.append("es_paper_bool_search")
    if enabled("TOOL_PAPER_SEMANTIC_SEARCH", "false"):
        paper_names.append("es_paper_semantic_search")
    if paper_names:
        names.extend(paper_names + ["visit_paper"])
    return names


def patent_search_tools(tools: list[str]) -> str:
    lines: list[str] = []
    if "es_patent_bm25_search" in tools:
        lines.append("- `es_patent_bm25_search`: BM25 patent retrieval over Level 1 candidate metadata.")
    if "es_patent_bool_search" in tools:
        lines.append("- `es_patent_bool_search`: advanced Elasticsearch query_string retrieval with AND/OR/NOT, grouping, phrases, field scoping, wildcards, fuzziness, and boosts.")
    if "es_patent_semantic_search" in tools:
        lines.append("- `es_patent_semantic_search`: BGE-M3 semantic patent retrieval over Level 1 candidate metadata when embeddings are configured.")
    return "\n".join(lines) if lines else "- No patent search tools are enabled."


def patent_visit_tools(tools: list[str]) -> str:
    if "visit_patent_claims" not in tools and "visit_patent_description" not in tools:
        return "- No patent visit tools are enabled."
    return "\n".join([
        "- `visit_patent_claims`: claim text for claim-level anticipation or obviousness mapping.",
        "- `visit_patent_description`: detailed disclosure when claims/abstract are insufficient; use offset/max_chars for long descriptions.",
    ])


def paper_search_tools(tools: list[str]) -> str:
    paper_lines: list[str] = []
    if "es_paper_bm25_search" in tools:
        paper_lines.append("- `es_paper_bm25_search`: BM25 literature retrieval returning stable IDs, metadata, and abstracts.")
    if "es_paper_bool_search" in tools:
        paper_lines.append("- `es_paper_bool_search`: Elasticsearch query_string literature retrieval with Boolean operators, phrases, grouping, field scoping, wildcards, fuzziness, and boosts.")
    if "es_paper_semantic_search" in tools:
        paper_lines.append("- `es_paper_semantic_search`: BGE-M3 semantic literature retrieval returning stable IDs, metadata, and abstracts.")
    if paper_lines:
        paper_lines.append("- `visit_paper`: final evidence visit for one selected paper by stable `paper_id`, returning comprehensive metadata and a pageable full-text window when available.")
        return "\n".join(paper_lines)
    return "- Paper search is disabled by configuration. Do not search for non-patent literature."


def render_common_instruction(tools: list[str]) -> str:
    return (
        read(INSTRUCTION_FILE, 40_000)
        .replace("{PATENT_SEARCH_TOOLS}", patent_search_tools(tools))
        .replace("{PATENT_VISIT_TOOLS}", patent_visit_tools(tools))
        .replace("{PAPER_SEARCH_TOOLS}", paper_search_tools(tools))
        .replace("{MAX_INTERACTION_TURNS}", str(MAX_INTERACTION_TURNS))
        .replace("{AGENT_INFERENCE_TIMEOUT}", str(TIMEOUT_SECONDS))
        .replace("{APPLICATION_DATE}", os.getenv("APPLICATION_DATE", ""))
    )


def toml_string(value: str) -> str:
    return json.dumps(value)


def direct_tool_model_catalog(model: str) -> Path | None:
    """Return an exact-version catalog override for Responses Lite models.

    Codex 0.151 advertises gpt-5.6-sol with ``use_responses_lite=true``, which
    moves tools into an ``additional_tools`` input item.  PatEx providers use
    the public Responses contract, so this catalog preserves the bundled model
    metadata while selecting standard top-level function tools.
    """
    return DIRECT_TOOL_MODEL_CATALOGS.get(model.strip().lower())


def write_codex_config(home: Path, tools: list[str]) -> None:
    base_url = os.getenv("CODEX_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    model = os.getenv("CODEX_MODEL", "deepseek/deepseek-v4-flash-0731")
    requested_effort = os.getenv("AGENT_REASONING_EFFORT", "").strip().lower()
    if requested_effort and requested_effort not in SUPPORTED_REASONING_EFFORTS:
        raise ValueError(
            "AGENT_REASONING_EFFORT must be one of: "
            + ", ".join(sorted(SUPPORTED_REASONING_EFFORTS))
        )
    reasoning_effort = effective_reasoning_effort(model, requested_effort) if requested_effort else ""
    reasoning_config = (
        f"model_reasoning_effort = {toml_string(reasoning_effort)}\n" if reasoning_effort else ""
    )
    catalog = direct_tool_model_catalog(model)
    if catalog is not None and not catalog.is_file():
        raise FileNotFoundError(f"Codex model catalog not found: {catalog}")
    catalog_config = (
        f"model_catalog_json = {toml_string(str(catalog.resolve()))}\n"
        if catalog is not None
        else ""
    )
    context_window = max(32768, int(os.getenv("CODEX_MODEL_CONTEXT_WINDOW", "131072")))
    auto_compact_limit = max(
        16384,
        min(context_window - 8192, int(os.getenv("CODEX_MODEL_AUTO_COMPACT_TOKEN_LIMIT", "110000"))),
    )
    server = Path("/app/patent_mcp.py")
    config = f"""
model = {toml_string(model)}
{reasoning_config}{catalog_config}model_context_window = {context_window}
model_auto_compact_token_limit = {auto_compact_limit}
model_provider = "harness"
approval_policy = "never"
sandbox_mode = "danger-full-access"
web_search = "disabled"
suppress_unstable_features_warning = true

[skills]
include_instructions = false

[skills.bundled]
enabled = false

[model_providers.harness]
name = "Harbor model provider"
base_url = {toml_string(base_url)}
env_key = "CODEX_API_KEY"
wire_api = "responses"
request_max_retries = 2
stream_max_retries = 2
stream_idle_timeout_ms = 120000

[mcp_servers.patent]
command = "python3"
args = [{toml_string(str(server))}]
required = true
startup_timeout_sec = 15
tool_timeout_sec = 90
enabled_tools = {json.dumps(tools)}
env_vars = {json.dumps([
    "APPLICATION_DATE",
    "ES_HOST",
    "ES_USER",
    "ES_PASSWORD",
    "ES_INDEX_PATENTS",
    "ES_INDEX_PAPERS",
    "ES_INDEX_RETRIEVAL_POOL",
    "ES_SEMANTIC_INDEX",
    "ES_SEMANTIC_VECTOR_FIELD",
    "ES_SEMANTIC_EMBED_URL",
    "ES_SEMANTIC_EMBED_MODEL",
    "ES_SEMANTIC_QUERY_PREFIX",
    "ES_PAPER_SEMANTIC_INDEX",
    "ES_PAPER_SEMANTIC_VECTOR_FIELD",
    "ES_BGE_M3_EMBED_URL",
    "TOOL_BM25",
    "TOOL_BOOL_SEARCH",
    "TOOL_SEMANTIC_SEARCH",
    "TOOL_PAPER_BM25",
    "TOOL_PAPER_BOOL_SEARCH",
    "TOOL_PAPER_SEMANTIC_SEARCH",
    "BM25_SIZE_DEFAULT",
    "BM25_SIZE_MAX",
    "BOOL_SIZE_DEFAULT",
    "BOOL_SIZE_MAX",
    "SEMANTIC_SIZE_DEFAULT",
    "SEMANTIC_SIZE_MAX",
    "SEMANTIC_NUM_CANDIDATES_DEFAULT",
    "SEMANTIC_NUM_CANDIDATES_MAX",
    "PAPER_SIZE_DEFAULT",
    "PAPER_SIZE_MAX",
])}

[features]
multi_agent = false
apps = false
browser_use = false
computer_use = false
goals = false
image_generation = false
plugins = false
plugin_sharing = false
remote_plugin = false
recommended_plugins = false
skill_search = false
skill_mcp_dependency_install = false
workspace_dependencies = false

[features.code_mode]
enabled = false
direct_only_tool_namespaces = ["patent"]

[features.non_prefixed_mcp_tool_names]
enabled = true
server_names = ["patent"]
""".strip()
    home.mkdir(parents=True, exist_ok=True)
    (home / "config.toml").write_text(config + "\n", encoding="utf-8")


def verify_mcp_registration(home: Path, tools: list[str]) -> None:
    """Fail before agent inference unless Codex and the MCP server agree on every tool."""
    env = os.environ.copy()
    env["CODEX_HOME"] = str(home)
    expected_version = os.getenv("CODEX_CLI_VERSION", "0.151.0").strip()
    version = subprocess.run(
        ["codex", "--version"],
        env=env,
        text=True,
        capture_output=True,
        timeout=20,
    )
    if version.returncode:
        raise RuntimeError(f"Codex version check failed: {version.stderr.strip()}")
    version_match = re.search(r"codex-cli\s+([^\s]+)", version.stdout)
    actual_version = version_match.group(1) if version_match else ""
    if actual_version != expected_version:
        raise RuntimeError(
            f"Codex CLI version mismatch: expected={expected_version} actual={actual_version or 'unknown'}"
        )
    print(f"[Codex Runner] Codex CLI version verified: {actual_version}", flush=True)
    configured = subprocess.run(
        ["codex", "mcp", "get", "patent", "--json"],
        env=env,
        text=True,
        capture_output=True,
        timeout=20,
    )
    if configured.returncode:
        raise RuntimeError(f"Codex MCP config check failed: {configured.stderr.strip()}")
    configured_tools = json.loads(configured.stdout).get("enabled_tools") or []
    if set(configured_tools) != set(tools):
        raise RuntimeError(
            f"Codex MCP enabled_tools mismatch: expected={sorted(tools)} "
            f"configured={sorted(configured_tools)}"
        )

    listed = subprocess.run(
        ["python3", "/app/patent_mcp.py"],
        input=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        + "\n",
        env=env,
        text=True,
        capture_output=True,
        timeout=20,
    )
    if listed.returncode:
        raise RuntimeError(f"Patent MCP tools/list failed: {listed.stderr.strip()}")
    response_line = next((line for line in listed.stdout.splitlines() if line.strip()), "")
    exposed_tools = [
        item.get("name")
        for item in (json.loads(response_line).get("result") or {}).get("tools") or []
    ]
    if set(exposed_tools) != set(tools):
        raise RuntimeError(
            f"Patent MCP tools/list mismatch: expected={sorted(tools)} exposed={sorted(exposed_tools)}"
        )
    print(f"[Codex Runner] MCP registration verified: {', '.join(tools)}", flush=True)


def prompt(patent_file: Path, cutoff: str, tools: list[str]) -> str:
    return f"""
You are a professional USPTO patent examiner. Follow the Harbor task instructions below, then complete the required files.

Enabled patent retrieval tools:
{patent_search_tools(tools)}

Enabled patent visit tools:
{patent_visit_tools(tools)}

Non-patent literature tools:
{paper_search_tools(tools)}

Inputs:
- Patent application: {patent_file}
- Application date and strict cutoff: {cutoff}

Harbor task instructions:
{render_common_instruction(tools)}

Current patent document:
{read(patent_file)}

The run has a hard limit of {MAX_INTERACTION_TURNS} model interactions. Complete and save both required output files before that limit is reached.

Write `{OUTPUT_DIR / 'office_action.md'}` and `{OUTPUT_DIR / 'selected_references.md'}` before finishing. The selected references file must contain only sources actually used in the Office Action, never the search history or unused candidates. Verify both files exist.
""".strip()


def fail(message: str, code: int) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / ".inference_failed").write_text(message.rstrip() + "\n", encoding="utf-8")
    print(f"[Codex Runner] {message}", flush=True)
    raise SystemExit(code)


def finish_for_turn_limit_scoring() -> bool:
    """Convert the gateway hard limit into a normal, scoreable Harbor termination."""
    if not TURN_LIMIT_MARKER.is_file():
        return False
    marker_copy = OUTPUT_DIR / ".interaction_turn_limit_reached.json"
    marker_copy.write_text(
        TURN_LIMIT_MARKER.read_text(encoding="utf-8", errors="replace"),
        encoding="utf-8",
    )
    (OUTPUT_DIR / ".inference_stopped").write_text(
        "maximum interaction turns reached; continue to verifier scoring\n",
        encoding="utf-8",
    )
    try:
        (OUTPUT_DIR / ".inference_failed").unlink()
    except FileNotFoundError:
        pass
    print(
        "[Codex Runner] Maximum interaction turns reached. "
        "Stopping normally so Harbor can score the existing outputs and trajectory.",
        flush=True,
    )
    return True


def finish_for_timeout_scoring() -> None:
    """Preserve partial outputs and let Harbor's verifier assign the score."""
    (OUTPUT_DIR / ".inference_timeout").write_text(
        f"wall-clock timeout reached after {TIMEOUT_SECONDS} seconds\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / ".inference_stopped").write_text(
        "wall-clock timeout reached; continue to verifier scoring\n",
        encoding="utf-8",
    )
    try:
        (OUTPUT_DIR / ".inference_failed").unlink()
    except FileNotFoundError:
        pass
    print(
        "[Codex Runner] Wall-clock timeout reached. "
        "Stopping normally so Harbor can score the existing outputs and trajectory.",
        flush=True,
    )


def main() -> None:
    patent_file = discover_patent_file()
    cutoff = application_date(patent_file)
    if not patent_file.exists():
        fail(f"Patent input not found: {patent_file}", 2)
    if not cutoff:
        fail("APPLICATION_DATE is required and could not be detected from the patent input.", 2)
    if not os.getenv("CODEX_API_KEY", "").strip():
        fail("CODEX_API_KEY is required (the start script may derive it from OPENROUTER_API_KEY or OPENAI_API_KEY).", 2)

    os.environ["APPLICATION_DATE"] = cutoff
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in [
        ".inference_complete",
        ".inference_failed",
        ".inference_stopped",
        ".inference_timeout",
        ".interaction_turn_limit_reached.json",
        "office_action.md",
        "selected_references.md",
    ]:
        try:
            (OUTPUT_DIR / name).unlink()
        except FileNotFoundError:
            pass
    try:
        TURN_LIMIT_MARKER.unlink()
    except FileNotFoundError:
        pass

    tools = enabled_tools()
    codex_home = Path(os.getenv("CODEX_HOME", "/tmp/codex-home"))
    write_codex_config(codex_home, tools)
    try:
        verify_mcp_registration(codex_home, tools)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        fail(str(exc), 2)
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    last_message = Path("/logs/agent/codex_last_message.txt")
    command = [
        "codex",
        "exec",
        "--dangerously-bypass-approvals-and-sandbox",
        "--skip-git-repo-check",
        "--ephemeral",
        "--json",
        "--color",
        "never",
        "--output-last-message",
        str(last_message),
        "-C",
        str(WORKSPACE),
        "-",
    ]
    print(f"[Codex Runner] Input patent: {patent_file}", flush=True)
    print(f"[Codex Runner] Cutoff: publication_date < {cutoff}", flush=True)
    print(f"[Codex Runner] Patent tools: {', '.join(tools) or 'none'}", flush=True)
    print(f"[Codex Runner] Model: {os.getenv('CODEX_MODEL', 'deepseek/deepseek-v4-flash-0731')}", flush=True)
    requested_effort = os.getenv("AGENT_REASONING_EFFORT", "").strip().lower()
    effective_effort = (
        effective_reasoning_effort(
            os.getenv("CODEX_MODEL", "deepseek/deepseek-v4-flash-0731"), requested_effort
        )
        if requested_effort
        else "provider-default"
    )
    print(
        "[Codex Runner] Agent reasoning effort: "
        f"requested={requested_effort or 'unset'} effective={effective_effort}",
        flush=True,
    )
    print(f"[Codex Runner] Maximum interaction turns: {MAX_INTERACTION_TURNS}", flush=True)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True, env=env)
    assert process.stdin is not None
    try:
        process.stdin.write(prompt(patent_file, cutoff, tools))
        process.stdin.close()
    except BrokenPipeError:
        pass
    start = time.monotonic()
    timed_out = False
    while process.poll() is None:
        if TURN_LIMIT_MARKER.is_file():
            print("[Codex Runner] Turn-limit marker detected; terminating Codex.", flush=True)
            process.terminate()
            break
        if time.monotonic() - start >= TIMEOUT_SECONDS:
            timed_out = True
            process.terminate()
            break
        time.sleep(0.2)
    try:
        returncode = process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        returncode = process.wait()
    if finish_for_turn_limit_scoring():
        return
    if timed_out:
        finish_for_timeout_scoring()
        return
    if returncode:
        fail(f"Codex exited with code {returncode}.", returncode)

    missing = [name for name in ["office_action.md", "selected_references.md"] if not (OUTPUT_DIR / name).exists()]
    if missing:
        fail("Missing outputs: " + ", ".join(missing), 2)
    (OUTPUT_DIR / ".inference_complete").write_text("completed\n", encoding="utf-8")
    print("[Codex Runner] Office Action generation complete.", flush=True)


if __name__ == "__main__":
    main()
