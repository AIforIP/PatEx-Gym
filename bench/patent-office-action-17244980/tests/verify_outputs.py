#!/usr/bin/env python3
"""Harbor verifier for patent Office Action tasks.

Evaluation has two layers:
1. Outcome evaluation: final Office Action quality and reference correctness.
2. Trajectory evaluation: structured agent behavior from OpenAI-format gateway messages.

The scalar Harbor reward remains simple and numeric. Rich research metrics are saved
under /logs/verifier for later analysis/SFT data construction.
"""
from __future__ import annotations

import base64
import json
import os
import re
import ssl
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

WORKSPACE = Path(os.environ.get("WORKSPACE", "/workspace"))
OUTPUT_DIR = WORKSPACE / "output"
INPUT_DIR = WORKSPACE / "input"
LOG_DIR = Path(os.environ.get("VERIFIER_LOG_DIR", "/logs/verifier"))
AGENT_LOG_DIR = Path(os.environ.get("AGENT_LOG_DIR", "/logs/agent"))
GATEWAY_TRAJ_DIR = Path(os.environ.get("GATEWAY_TRAJECTORY_DIR", "/logs/gateway/trajectories"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

OA_PATH = OUTPUT_DIR / "office_action.md"
SEL_PATH = OUTPUT_DIR / "selected_references.md"
HARNESS = os.environ.get("HARNESS", "pi").strip().lower()
AGENT_LOG_PATH = AGENT_LOG_DIR / ("codex_inference.log" if HARNESS == "codex" else "pi_inference.log")
TEST_DIR = Path(__file__).resolve().parent

SEARCH_TOOLS = {"es_patent_bm25_search", "es_patent_bool_search", "es_patent_semantic_search"}
LEGACY_TOOL_ALIASES = dict()
PATENT_VISIT_TOOLS = {"visit_patent_claims", "visit_patent_description"}
PAPER_SEARCH_TOOLS = {"es_paper_bm25_search", "es_paper_bool_search", "es_paper_semantic_search"}
PAPER_VISIT_TOOLS = {"paper_visit", "visit_paper", "visit_paper_text", "paper_read"}
WRITE_TOOLS = {"write", "edit"}


def read(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:limit] if limit else text


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def normalize_date(value: object) -> str:
    match = re.search(r"(\d{4})[-/.?](\d{1,2})[-/.?](\d{1,2})", str(value or ""))
    if not match:
        return ""
    y, m, d = map(int, match.groups())
    return f"{y:04d}-{m:02d}-{d:02d}"


def detect_application_date() -> tuple[str, str]:
    configured = normalize_date(os.environ.get("APPLICATION_DATE", "").strip())
    if configured:
        return configured, "environment"
    patent_text = read(INPUT_DIR / "patent.md", limit=20000)
    match = re.search(
        r"^\s*-?\s*(?:Filing Date|Application Date|申请日|提交日|申请日期)\s*:\s*(.+?)\s*$",
        patent_text,
        re.I | re.M,
    )
    detected = normalize_date(match.group(1)) if match else ""
    return (detected, "patent.md") if detected else ("", "unavailable")


APP_DATE, APP_DATE_SOURCE = detect_application_date()


def extract_dates(text: str) -> list[str]:
    return [f"{int(y):04d}-{int(m):02d}-{int(d):02d}" for y, m, d in re.findall(r"(\d{4})[-/.?](\d{1,2})[-/.?](\d{1,2})", text)]


def extract_patent_ids(text: str) -> list[str]:
    patterns = [
        r"\bUS\s*\d{4,11}\s*[A-Z]\d?\b",
        r"\bUS\s*\d{7,11}\b",
        r"\bEP\s*\d{4,10}\s*[A-Z]\d?\b",
        r"\bWO\s*\d{4}\s*\d{4,8}\s*[A-Z]\d?\b",
        r"\bCN\s*\d{6,12}\s*[A-Z]\b",
        r"\bJP\s*\d{6,12}\s*[A-Z]\b",
        r"\bKR\s*\d{6,12}\s*[A-Z]\b",
        r"\b(?:JPH|JPS|TWM|USD|RU|ES|TR|SE|BR|FI|GB|CH|AU|DE|NO|CA|FR)\s*\d{4,14}\s*[A-Z]?\d?\b",
    ]
    seen: set[str] = set()
    refs: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.I):
            ref = re.sub(r"\s+", "", match.group(0)).upper()
            if ref not in seen:
                seen.add(ref)
                refs.append(ref)
    return refs


PAPER_ID_PREFIXES = ("doi", "arxiv", "pmid", "openreview", "jvet", "stanford", "usenix", "sha256")


def normalize_paper_reference(value: object) -> str:
    raw = str(value or "").strip().lower()
    raw = re.sub(r"^https?://(?:dx\.)?doi\.org/", "doi:", raw)
    raw = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "arxiv:", raw)
    raw = raw.strip(" \t\r\n`*_<>[]{}()\"'.,;")
    if re.fullmatch(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", raw):
        raw = f"doi:{raw}"
    if re.fullmatch(r"\d{4}\.\d{4,5}(?:v\d+)?", raw):
        raw = f"arxiv:{raw}"
    match = re.fullmatch(r"(" + "|".join(PAPER_ID_PREFIXES) + r")\s*:\s*(.+)", raw)
    if not match:
        return ""
    prefix, identifier = match.groups()
    identifier = re.sub(r"\s+", "", identifier).strip("`*_<>[]{}()\"'.,;")
    if prefix == "arxiv":
        identifier = re.sub(r"v\d+$", "", identifier)
    if prefix == "pmid":
        identifier = re.sub(r"\D", "", identifier)
    return f"{prefix}:{identifier}" if identifier else ""


def extract_paper_references(text: str) -> list[str]:
    patterns = (
        r"(?:https?://(?:dx\.)?doi\.org/|\bdoi\s*:\s*)10\.\d{4,9}/[-._;()/:A-Z0-9]+",
        r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+",
        r"(?:https?://arxiv\.org/(?:abs|pdf)/|\barxiv\s*:\s*)\d{4}\.\d{4,5}(?:v\d+)?",
        r"\bpmid\s*:\s*\d{5,10}\b",
        r"\b(?:openreview|jvet|stanford|usenix|sha256)\s*:\s*[-._:A-Z0-9]+",
    )
    found: set[str] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text or "", re.I):
            normalized = normalize_paper_reference(match.group(0))
            if normalized:
                found.add(normalized)
    return sorted(found)


def extract_paper_ids(text: str) -> list[str]:
    """Backward-compatible name for canonical paper-reference extraction."""
    return extract_paper_references(text)


def count_patterns(text: str, patterns: list[str]) -> int:
    return sum(len(re.findall(pattern, text, re.I)) for pattern in patterns)


def es_auth_header() -> str:
    user = os.environ.get("ES_USER", "")
    password = os.environ.get("ES_PASSWORD", "")
    token = f"{user}:{password}" if password else user
    return "Basic " + base64.b64encode(token.encode("utf-8")).decode("ascii")


def lookup_reference_dates(reference_ids: list[str]) -> dict[str, dict[str, Any]]:
    host = os.environ.get("ES_HOST", "").rstrip("/")
    index = os.environ.get("ES_INDEX_PATENTS") or os.environ.get("ES_INDEX_RETRIEVAL_POOL", "")
    if not host or not index or not reference_ids:
        return {}
    context = ssl._create_unverified_context()
    out: dict[str, dict[str, Any]] = {}
    for ref in reference_ids:
        normalized = ref.lower().replace(" ", "")
        body = {
            "query": {"bool": {"should": [{"term": {"publication_number_norm": normalized}}, {"term": {"publication_number": ref}}], "minimum_should_match": 1}},
            "size": 1,
            "_source": ["publication_number", "publication_number_norm", "publication_date", "pub_date", "publicationDate", "title"],
        }
        request = urllib.request.Request(
            f"{host}/{index}/_search",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": es_auth_header()},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=8, context=context) as response:
                data = json.loads(response.read().decode("utf-8", errors="replace"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            out[ref] = {"error": str(exc)}
            continue
        hit = (data.get("hits", {}).get("hits") or [None])[0]
        if not hit:
            out[ref] = {"error": "not found"}
            continue
        source = hit.get("_source") or {}
        pub_date = normalize_date(source.get("publication_date") or source.get("pub_date") or source.get("publicationDate"))
        out[ref] = {"publication_number": source.get("publication_number") or ref, "publication_date": pub_date or None, "title": source.get("title")}
    return out


def load_ground_truth() -> dict[str, list[str]]:
    verifier_gt = TEST_DIR / "ground_truth.json"
    if verifier_gt.is_file():
        try:
            data = json.loads(verifier_gt.read_text(encoding="utf-8", errors="replace"))
            patents = data.get("patent_references_gt") if isinstance(data, dict) else None
            papers = data.get("paper_references_gt") if isinstance(data, dict) else None
            if isinstance(patents, list) and isinstance(papers, list):
                return {"patents": sorted(set(extract_patent_ids("\n".join(map(str, patents))))),
                        "papers": sorted(set(map(str, papers)))}
        except json.JSONDecodeError:
            pass
    candidates = [
        INPUT_DIR / "ground_truth.json",
        INPUT_DIR / "gt.json",
        INPUT_DIR / "expected_references.json",
        INPUT_DIR / "references.json",
    ]
    data: Any = None
    for path in candidates:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
                break
            except json.JSONDecodeError:
                pass
    patents: list[str] = []
    papers: list[str] = []
    if isinstance(data, dict):
        for key in ("patents", "patent_references", "reference_patents", "gt_patents"):
            if isinstance(data.get(key), list):
                patents.extend(str(x) for x in data[key])
        for key in ("papers", "paper_references", "paper_references_gt", "npl", "gt_papers"):
            if isinstance(data.get(key), list):
                papers.extend(str(x) for x in data[key])
        for key in ("references", "gold_references"):
            if isinstance(data.get(key), list):
                for x in data[key]:
                    s = json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else str(x)
                    patents.extend(extract_patent_ids(s))
                    papers.extend(extract_paper_ids(s))
    text_files = [INPUT_DIR / "ground_truth.md", INPUT_DIR / "gt.md", INPUT_DIR / "expected_references.md"]
    for path in text_files:
        if path.exists():
            text = read(path)
            patents.extend(extract_patent_ids(text))
            papers.extend(extract_paper_ids(text))
    return {"patents": sorted(set(extract_patent_ids("\n".join(patents)) or [p.upper() for p in patents])), "papers": sorted(set(papers))}


JUDGE_DIMENSIONS = (
    "soundness",
    "clarity",
    "constructiveness",
    "completeness",
    "language_style",
)

DECISION_LABELS = {
    "non_final_rejection",
    "final_rejection",
    "notice_of_allowance",
    "ex_parte_quayle_action",
}
STATUTE_LABELS = ("101", "102", "103", "112", "double_patenting")


def normalize_decision_label(value: object) -> str | None:
    text = re.sub(r"[^a-z]+", "_", str(value or "").strip().lower()).strip("_")
    aliases = {
        "non_final_rejection": "non_final_rejection",
        "nonfinal_rejection": "non_final_rejection",
        "rejection": "non_final_rejection",
        "final_rejection": "final_rejection",
        "notice_of_allowance": "notice_of_allowance",
        "allowance": "notice_of_allowance",
        "allowed": "notice_of_allowance",
        "ex_parte_quayle": "ex_parte_quayle_action",
        "ex_parte_quayle_action": "ex_parte_quayle_action",
        "quayle": "ex_parte_quayle_action",
    }
    return aliases.get(text)


def normalize_statute_labels(values: object) -> list[str]:
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list):
        return []
    found: set[str] = set()
    for value in values:
        text = str(value or "")
        for section in ("101", "102", "103", "112"):
            if re.search(rf"(?<!\d){section}(?!\d)", text):
                found.add(section)
        if re.search(r"double\s+patent", text, re.I):
            found.add("double_patenting")
    return [label for label in STATUTE_LABELS if label in found]


def extract_explicit_decision(text: str) -> str | None:
    if re.search(r"\bex\s+parte\s+quayle\b", text, re.I):
        return "ex_parte_quayle_action"
    if re.search(r"\bnon[ -]?final\s+(?:office\s+action|rejection)\b", text, re.I):
        return "non_final_rejection"
    if re.search(r"(?im)^\s*final\s+action\s*$|\bthis\s+action\s+is\s+made\s+final\b|(?<!non[- ])\bfinal\s+(?:office\s+action|rejection)\b", text):
        return "final_rejection"
    if re.search(r"\bclaim\s+rejections?\b|\b(?:is|are|stands?)\s+rejected\s+under\b|\bclaims?\s+(?:stand\s+)?rejected\b", text, re.I):
        return "non_final_rejection"
    if extract_explicit_statutes(text):
        return "non_final_rejection"
    if re.search(r"\bnotice\s+of\s+allow(?:ance|ability)\b|\breasons?\s+for\s+allowance\b|\b(?:all\s+claims?|claims?\s+[\d,\-–— and]+)\s+(?:is|are)\s+allow(?:ed|able)\b", text, re.I):
        return "notice_of_allowance"
    return None


def extract_explicit_statutes(text: str) -> list[str]:
    found: set[str] = set()
    rejection_patterns = (
        r"claim\s+rejections?\s*[-—:]\s*35\s+U\.?S\.?C\.?\s*§?\s*(101|102|103|112)\b",
        r"\bclaims?\s+[\d,\-–— and]+\s+(?:is|are)\s+rejected\s+under\s+(?:pre[- ]?AIA\s+)?35\s+U\.?S\.?C\.?\s*§?\s*(101|102|103|112)\b",
    )
    for pattern in rejection_patterns:
        found.update(match.group(1) for match in re.finditer(pattern, text, re.I))
    for match in re.finditer(r"\bdouble\s+patenting\s+rejections?\b|\brejected\b[^.\n]{0,200}\bdouble\s+patenting\b", text, re.I):
        line_start = text.rfind("\n", 0, match.start()) + 1
        clause_prefix = text[line_start:match.start()]
        if not re.search(r"\b(?:no|not|without)\b", clause_prefix, re.I):
            found.add("double_patenting")
            break
    return [label for label in STATUTE_LABELS if label in found]

RECALL_PUBLICATION_PREFIXES = (
    "JPH", "JPS", "TWM", "USD",
    "US", "WO", "EP", "CN", "JP", "KR", "GB", "CH", "AU", "DE", "NO", "CA", "FR",
    "RU", "ES", "TR", "SE", "BR", "FI",
)


def normalize_recall_reference(value: object) -> str:
    raw = re.sub(r"[\s,./-]+", "", str(value or "").upper())
    if raw.startswith("APP"):
        digits = re.sub(r"\D", "", raw[3:])
        return f"APP{digits}" if digits else ""
    for prefix in RECALL_PUBLICATION_PREFIXES:
        if raw.startswith(prefix):
            rest = raw[len(prefix):]
            rest = re.sub(r"[A-Z]\d?$", "", rest)
            digits = re.sub(r"\D", "", rest)
            return f"{prefix}{digits}" if digits else ""
    return ""


def extract_recall_references(text: str) -> list[str]:
    found: set[str] = set()
    prefixes = "|".join(RECALL_PUBLICATION_PREFIXES)
    publication_pattern = re.compile(
        rf"\b(?:{prefixes})\s*[-/]?\s*\d[\d\s,/-]*\d(?:\s*[A-Z]\d?)?\b",
        re.I,
    )
    application_patterns = (
        re.compile(r"\bAPP\s*[-/]?\s*\d[\d\s,/-]*\d\b", re.I),
        re.compile(r"\bAPPLICATION(?:\s+(?:NO\.?|NUMBER))?\s*[:#]?\s*\d{2}\s*[/,]\s*\d{3}\s*,?\s*\d{3}\b", re.I),
    )
    for match in publication_pattern.finditer(text or ""):
        normalized = normalize_recall_reference(match.group(0))
        if normalized:
            found.add(normalized)
    for pattern in application_patterns:
        for match in pattern.finditer(text or ""):
            digits = re.sub(r"\D", "", match.group(0))
            if digits:
                found.add(f"APP{digits}")
    return sorted(found)


def trajectory_content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if content is None:
        return ""
    return json.dumps(content, ensure_ascii=False)


def _extract_json_object(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    fenced = re.search(r"```json\s*(.*?)\s*```", raw, re.I | re.S)
    if fenced:
        raw = fenced.group(1).strip()
    try:
        value = json.loads(raw)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for index, char in enumerate(raw):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(raw[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("judge response does not contain a valid JSON object")


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except ValueError:
        return default


def _bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_verifier_ground_truth() -> dict[str, Any]:
    path = TEST_DIR / "ground_truth.json"
    if not path.is_file():
        return {"error": f"missing verifier ground truth: {path}"}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        return {"error": f"invalid verifier ground truth: {exc}"}
    return data if isinstance(data, dict) else {"error": "verifier ground truth must be an object"}


def run_llm_judge(generated_text: str, ground_truth_text: str) -> dict[str, Any]:
    key = os.environ.get("JUDGE_OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("JUDGE_OPENAI_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    legacy_model = os.environ.get("JUDGE_MODEL", "deepseek/deepseek-v4-flash-0731").strip()
    configured_models = os.environ.get("JUDGE_MODELS", "").strip()
    if configured_models:
        models = [item.strip() for item in configured_models.split(",") if item.strip()]
    else:
        models = [
            os.environ.get(f"JUDGE_MODEL_{index}", legacy_model).strip() or legacy_model
            for index in (1, 2, 3)
        ]
    if len(models) != 3:
        return {
            "available": False,
            "error": f"exactly three judge models are required, got {len(models)}",
            "models": models,
            "aggregation": {"method": "per-dimension arithmetic mean", "required_judges": 3},
        }
    timeout = max(1, int(_float_env("JUDGE_TIMEOUT_SECONDS", 300)))
    max_tokens = max(1024, int(_float_env("JUDGE_MAX_TOKENS", 8192)))
    reasoning_max_tokens = max(1024, int(_float_env("JUDGE_REASONING_MAX_TOKENS", 2048)))
    prompt_path = TEST_DIR / "judge_prompt.json"
    if not key:
        return {"available": False, "error": "JUDGE_OPENAI_API_KEY is not configured", "models": models}
    if not prompt_path.is_file():
        return {"available": False, "error": f"missing judge prompt: {prompt_path}", "models": models}
    try:
        prompt = json.loads(prompt_path.read_text(encoding="utf-8"))
        system_prompt = str(prompt["system_prompt"])
        # Do not use str.format here: the prompt intentionally contains a JSON
        # response schema whose braces are literal model-visible text.
        user_prompt = str(prompt["user_prompt_template"])
        replacements = {
            "{ground_truth}": ground_truth_text,
            "{generated_text}": generated_text,
            "{response_target_section}": "",
            "{current_response_target}": "",
        }
        for placeholder, value in replacements.items():
            user_prompt = user_prompt.replace(placeholder, value)
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        return {"available": False, "error": f"invalid judge prompt: {exc}", "models": models}

    judge_results: list[dict[str, Any]] = []
    for judge_index, model in enumerate(models, start=1):
        attempts: list[dict[str, Any]] = []
        parsed: dict[str, Any] | None = None
        last_error = ""
        for attempt_number in (1, 2):
            effective_user_prompt = user_prompt
            if attempt_number == 2:
                effective_user_prompt += (
                    "\n\nReturn JSON only. Do not include any other text. Keep every justification concise "
                    "so the complete JSON object fits within the response limit."
                )
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": effective_user_prompt},
                ],
                "temperature": 0,
                "max_tokens": max_tokens,
                "reasoning": {"max_tokens": min(reasoning_max_tokens, max_tokens - 1), "exclude": True},
                "response_format": {"type": "json_object"},
            }
            request_record = {"endpoint": f"{base_url}/chat/completions", "payload": payload}
            stem = f"judge_{judge_index}_attempt_{attempt_number}"
            (LOG_DIR / f"{stem}_request.json").write_text(
                json.dumps(request_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            request = urllib.request.Request(
                request_record["endpoint"],
                data=json.dumps(payload).encode("utf-8"),
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    response_data = json.loads(response.read().decode("utf-8", errors="replace"))
                (LOG_DIR / f"{stem}_response.json").write_text(
                    json.dumps(response_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                content = response_data["choices"][0]["message"].get("content") or ""
                candidate = _extract_json_object(content)
                candidate_text = json.dumps(candidate, ensure_ascii=False).lower()
                if generated_text.strip() and re.search(
                    r"generated (?:office action|text|document).{0,80}(?:not provided|missing|absent)",
                    candidate_text,
                ):
                    raise ValueError("judge incorrectly reported that the generated Office Action was missing")
                candidate_scores = candidate.get("scores") if isinstance(candidate.get("scores"), dict) else {}
                missing_candidate_dimensions = [
                    name
                    for name in JUDGE_DIMENSIONS
                    if not (
                        isinstance(candidate_scores.get(name), (int, float))
                        and not isinstance(candidate_scores.get(name), bool)
                    )
                ]
                if missing_candidate_dimensions:
                    raise ValueError(
                        "judge JSON is missing numeric dimensions: "
                        + ", ".join(missing_candidate_dimensions)
                    )
                parsed = candidate
                attempts.append({"attempt": attempt_number, "status": "parsed"})
                break
            except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
                last_error = str(exc)
                attempts.append({"attempt": attempt_number, "status": "error", "error": last_error})

        raw_scores = parsed.get("scores") if parsed and isinstance(parsed.get("scores"), dict) else {}
        scores: dict[str, float] = {}
        missing: list[str] = []
        for name in JUDGE_DIMENSIONS:
            value = raw_scores.get(name)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                scores[name] = round(max(1.0, min(10.0, float(value))), 4)
            else:
                missing.append(name)
        judge_results.append({
            "judge_index": judge_index,
            "model": model,
            "available": not missing,
            "dimensions": scores,
            "missing_dimensions": missing,
            "normalized_score": round(sum(scores.values()) / (10.0 * len(JUDGE_DIMENSIONS)), 4) if not missing else None,
            "justification": parsed.get("justification", "") if parsed else "",
            "justification_details": parsed.get("justification_details", {}) if parsed else {},
            "attempts": attempts,
            "error": None if not missing else (last_error or "judge parsing failed"),
        })

    available_judges = [judge for judge in judge_results if judge["available"]]
    all_available = len(available_judges) == 3
    aggregate_scores = {
        name: round(sum(float(judge["dimensions"][name]) for judge in available_judges) / 3.0, 4)
        for name in JUDGE_DIMENSIONS
    } if all_available else {}
    normalized_score = (
        round(sum(aggregate_scores.values()) / (10.0 * len(JUDGE_DIMENSIONS)), 4)
        if all_available
        else None
    )
    return {
        "available": all_available,
        "models": models,
        "aggregation": {
            "method": "per-dimension arithmetic mean",
            "required_judges": 3,
            "available_judges": len(available_judges),
        },
        "dimensions": aggregate_scores,
        "normalized_score": normalized_score,
        "judges": judge_results,
    }


def run_label_judge(generated_text: str) -> dict[str, Any]:
    """Extract generated labels without exposing gold text or labels to the model."""
    key = os.environ.get("JUDGE_OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("JUDGE_OPENAI_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    fallback_model = os.environ.get("JUDGE_MODEL_1") or os.environ.get("JUDGE_MODEL", "deepseek/deepseek-v4-flash-0731")
    model = os.environ.get("LABEL_JUDGE_MODEL", fallback_model).strip()
    timeout = max(1, int(_float_env("LABEL_JUDGE_TIMEOUT_SECONDS", _float_env("JUDGE_TIMEOUT_SECONDS", 300))))
    max_tokens = max(256, int(_float_env("LABEL_JUDGE_MAX_TOKENS", 2048)))
    reasoning_max_tokens = max(0, int(_float_env("LABEL_JUDGE_REASONING_MAX_TOKENS", 0)))
    prompt_path = TEST_DIR / "label_judge_prompt.json"
    base_result = {"model": model, "gold_visible": False, "prompt_path": str(prompt_path)}
    if not key:
        return {**base_result, "available": False, "error": "JUDGE_OPENAI_API_KEY is not configured"}
    if not prompt_path.is_file():
        return {**base_result, "available": False, "error": f"missing label judge prompt: {prompt_path}"}
    try:
        prompt = json.loads(prompt_path.read_text(encoding="utf-8"))
        system_prompt = str(prompt["system_prompt"])
        user_prompt = str(prompt["user_prompt_template"]).replace("{generated_text}", generated_text)
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        return {**base_result, "available": False, "error": f"invalid label judge prompt: {exc}"}

    attempts: list[dict[str, Any]] = []
    last_error = ""
    for attempt_number in (1, 2):
        effective_prompt = user_prompt
        if attempt_number == 2:
            effective_prompt += "\n\nReturn one complete JSON object only."
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": effective_prompt},
            ],
            "temperature": 0,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        if reasoning_max_tokens:
            payload["reasoning"] = {
                "max_tokens": min(reasoning_max_tokens, max_tokens - 1),
                "exclude": True,
            }
        else:
            payload["reasoning"] = {"effort": "none", "exclude": True}
        request_record = {"endpoint": f"{base_url}/chat/completions", "payload": payload}
        stem = f"label_judge_attempt_{attempt_number}"
        (LOG_DIR / f"{stem}_request.json").write_text(
            json.dumps(request_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        request = urllib.request.Request(
            request_record["endpoint"],
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_data = json.loads(response.read().decode("utf-8", errors="replace"))
            (LOG_DIR / f"{stem}_response.json").write_text(
                json.dumps(response_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            content = response_data["choices"][0]["message"].get("content") or ""
            parsed = _extract_json_object(content)
            raw_decision = str(parsed.get("decision") or "").strip().lower()
            decision = normalize_decision_label(raw_decision)
            if decision is None and raw_decision != "undetermined":
                raise ValueError("invalid decision label")
            statutes = normalize_statute_labels(parsed.get("statutes"))
            attempts.append({"attempt": attempt_number, "status": "parsed"})
            return {
                **base_result,
                "available": True,
                "decision": decision,
                "decision_raw": raw_decision,
                "statutes": statutes,
                "evidence": str(parsed.get("evidence") or ""),
                "attempts": attempts,
            }
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
            last_error = str(exc)
            attempts.append({"attempt": attempt_number, "status": "error", "error": last_error})
    return {**base_result, "available": False, "error": last_error or "label judge parsing failed", "attempts": attempts}


def decision_and_statute_evaluation(oa_text: str, gt: dict[str, Any], label_judge: dict[str, Any]) -> dict[str, Any]:
    gold_decision = normalize_decision_label(gt.get("oa_type"))
    gold_statutes = normalize_statute_labels(gt.get("rejection_types"))
    if not oa_text.strip():
        return {
            "version": "decision-statute-v2",
            "completion_inclusion": False,
            "decision": {
                "available": gold_decision is not None,
                "accuracy": 0.0,
                "ground_truth": gold_decision,
                "predicted": None,
                "prediction_source": "missing_generated_office_action",
                "ground_truth_class": gold_decision,
            },
            "statutes": {
                "available": True,
                "accuracy": 0.0,
                "exact_match_accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "ground_truth": gold_statutes,
                "predicted": [],
                "hits": [],
                "missing": gold_statutes,
                "additional": [],
                "prediction_source": "missing_generated_office_action",
                "empty_ground_truth_policy": "missing generated output is scored as zero even when the gold statute set is empty",
            },
            "label_judge": label_judge if isinstance(label_judge, dict) else {},
        }
    explicit_decision = extract_explicit_decision(oa_text)
    explicit_statutes = extract_explicit_statutes(oa_text)
    judge_extraction = label_judge if isinstance(label_judge, dict) else {}

    predicted_decision = explicit_decision or normalize_decision_label(judge_extraction.get("decision"))
    if explicit_statutes:
        predicted_statutes = explicit_statutes
        statute_source = "deterministic_generated_text"
    elif predicted_decision in {"notice_of_allowance", "ex_parte_quayle_action"}:
        predicted_statutes = []
        statute_source = "deterministic_no_rejection_decision"
    else:
        predicted_statutes = normalize_statute_labels(judge_extraction.get("statutes"))
        statute_source = "generated_only_label_judge_fallback"

    decision_available = gold_decision is not None and predicted_decision is not None
    decision_accuracy = float(gold_decision == predicted_decision) if decision_available else None
    gold_set = set(gold_statutes)
    predicted_set = set(predicted_statutes)
    hits = gold_set & predicted_set
    statute_exact = float(gold_set == predicted_set)
    if not gold_set and not predicted_set:
        precision = recall = f1 = 1.0
    else:
        precision = len(hits) / len(predicted_set) if predicted_set else 0.0
        recall = len(hits) / len(gold_set) if gold_set else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "version": "decision-statute-v2",
        "completion_inclusion": False,
        "decision": {
            "available": decision_available,
            "accuracy": decision_accuracy,
            "ground_truth": gold_decision,
            "predicted": predicted_decision,
            "prediction_source": "deterministic_generated_text" if explicit_decision else "generated_only_label_judge_fallback",
            "ground_truth_class": gold_decision,
        },
        "statutes": {
            "available": True,
            "accuracy": statute_exact,
            "exact_match_accuracy": statute_exact,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "ground_truth": gold_statutes,
            "predicted": predicted_statutes,
            "hits": [label for label in STATUTE_LABELS if label in hits],
            "missing": [label for label in STATUTE_LABELS if label in gold_set - predicted_set],
            "additional": [label for label in STATUTE_LABELS if label in predicted_set - gold_set],
            "prediction_source": statute_source,
            "empty_ground_truth_policy": "an empty statute set is a meaningful no-rejection label and is scored",
        },
        "label_judge": judge_extraction,
    }


def reference_usage_metrics(
    reference_type: str,
    ground_truth: list[str],
    selected: list[str],
    office_action_cited: list[str],
) -> dict[str, Any]:
    plural = "patents" if reference_type == "patent" else "papers"
    gt_set = set(ground_truth)
    selected_set = set(selected)
    cited_set = set(office_action_cited)
    used_set = selected_set & cited_set
    hits = gt_set & used_set
    applicable = bool(gt_set)
    precision = round(len(hits) / len(used_set), 4) if applicable and used_set else (0.0 if applicable else None)
    recall = round(len(hits) / len(gt_set), 4) if applicable else None
    f1 = (
        round(2 * precision * recall / (precision + recall), 4)
        if applicable and precision + recall > 0
        else (0.0 if applicable else None)
    )
    return {
        "metric": f"ground_truth_office_action_usage_{reference_type}",
        "reference_type": reference_type,
        "completion_inclusion": False,
        "applicable": applicable,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        f"ground_truth_{plural}": sorted(gt_set),
        f"selected_{plural}": sorted(selected_set),
        f"office_action_cited_{plural}": sorted(cited_set),
        f"office_action_used_{plural}": sorted(used_set),
        "hits": sorted(hits),
        f"missing_ground_truth_{plural}": sorted(gt_set - used_set),
        f"additional_used_{plural}": sorted(used_set - gt_set),
        "selected_but_not_cited_in_office_action": sorted(selected_set - cited_set),
        "cited_in_office_action_but_not_selected": sorted(cited_set - selected_set),
        "selected_ground_truth_recall": round(len(gt_set & selected_set) / len(gt_set), 4) if applicable else None,
        "counts": {
            "ground_truth": len(gt_set),
            "selected": len(selected_set),
            "office_action_cited": len(cited_set),
            "office_action_used": len(used_set),
            "hits": len(hits),
        },
        "empty_ground_truth_policy": (
            None
            if applicable
            else f"not_applicable: the initial Office Action uses no {reference_type} reference; metrics are null, not 0 or 1"
        ),
    }


def format_evaluation(
    oa_text: str,
    sel_text: str,
    *,
    office_action_exists: bool,
    selected_references_exists: bool,
) -> dict[str, Any]:
    schema = selected_references_schema(sel_text) if selected_references_exists else {"valid": False}
    oa_structure = office_action_structure(oa_text)
    format_checks = {
        "office_action_present_and_nonempty": office_action_exists and bool(oa_text.strip()),
        "selected_references_present_and_nonempty": selected_references_exists and bool(sel_text.strip()),
        "detailed_action_section_present": oa_structure["has_detailed_action"],
        "conclusion_section_present": oa_structure["has_conclusion"],
        "selected_references_structure_parseable": bool(schema.get("valid")),
    }
    format_score = round(sum(bool(value) for value in format_checks.values()) / len(format_checks), 4)
    return {
        "score": format_score,
        "checks": format_checks,
        "office_action_structure": oa_structure,
        "selected_references_schema": schema,
    }


def completion_evaluation(oa_text: str, sel_text: str) -> dict[str, Any]:
    gt = load_verifier_ground_truth()
    format_result = format_evaluation(
        oa_text,
        sel_text,
        office_action_exists=OA_PATH.is_file(),
        selected_references_exists=SEL_PATH.is_file(),
    )

    gt_refs = sorted(
        {
            normalized
            for value in (gt.get("patent_references_gt") or [])
            if (normalized := normalize_recall_reference(value))
        }
    )
    selected_refs = extract_recall_references(sel_text)
    office_action_refs = extract_recall_references(oa_text)
    citation_metrics = reference_usage_metrics("patent", gt_refs, selected_refs, office_action_refs)

    gt_papers = sorted(
        {
            normalized
            for value in (gt.get("paper_references_gt") or [])
            if (normalized := normalize_paper_reference(value))
        }
    )
    selected_papers = extract_paper_references(sel_text)
    office_action_papers = extract_paper_references(oa_text)
    paper_citation_metrics = reference_usage_metrics(
        "paper", gt_papers, selected_papers, office_action_papers
    )

    has_generated_oa = OA_PATH.is_file()
    if has_generated_oa:
        judge = run_llm_judge(oa_text, str(gt.get("office_action_text") or ""))
        label_judge = run_label_judge(oa_text)
    else:
        judge = {
            "available": False,
            "normalized_score": None,
            "dimensions": {},
            "judges": [],
            "error": "generated office_action.md is missing; quality judges were not called",
        }
        label_judge = {
            "available": False,
            "gold_visible": False,
            "error": "generated office_action.md is missing; label judge was not called",
        }
    decision_statute_metrics = decision_and_statute_evaluation(oa_text, gt, label_judge)
    judge_score = judge.get("normalized_score") if isinstance(judge.get("normalized_score"), (int, float)) else 0.0
    configured_weights = {
        "format": max(0.0, _float_env("COMPLETION_FORMAT_WEIGHT", 0.10)),
        "llm_judge": max(0.0, _float_env("COMPLETION_JUDGE_WEIGHT", 0.50)),
    }
    weight_sum = sum(configured_weights.values()) or 1.0
    weights = {key: round(value / weight_sum, 6) for key, value in configured_weights.items()}
    score = 0.0 if not has_generated_oa else round(
        format_result["score"] * weights["format"]
        + float(judge_score) * weights["llm_judge"],
        4,
    )
    return {
        "version": "completion-v6",
        "status": "complete" if has_generated_oa and judge.get("available") and not gt.get("error") else "incomplete",
        "score": score,
        "weights": weights,
        "configured_weights": configured_weights,
        "format": format_result,
        "llm_judge": judge,
        "label_judge": label_judge,
        "decision_statute_metrics": decision_statute_metrics,
        "citation_metrics": citation_metrics,
        "paper_citation_metrics": paper_citation_metrics,
        "ground_truth": {
            "available": not bool(gt.get("error")),
            "error": gt.get("error"),
            "application_number": gt.get("application_number"),
            "oa_type": gt.get("oa_type"),
            "rejection_types": gt.get("rejection_types") or [],
        },
    }


def precision_recall(predicted: list[str], gold: list[str]) -> dict[str, Any]:
    pred_set = {p.upper() for p in predicted}
    gold_set = {g.upper() for g in gold}
    hits = sorted(pred_set & gold_set)
    return {
        "available": bool(gold_set),
        "predicted_count": len(pred_set),
        "gold_count": len(gold_set),
        "hit_count": len(hits),
        "hits": hits,
        "precision": round(len(hits) / len(pred_set), 4) if pred_set else (0.0 if gold_set else None),
        "recall": round(len(hits) / len(gold_set), 4) if gold_set else None,
        "x_reference_hit": bool(hits),
    }


SELECTED_SCHEMA_HEADINGS = [
    "Patent References",
    "Non-Patent Literature",
]


def _normalized_heading(line: str) -> str:
    value = re.sub(r"^\s*#{1,6}\s*", "", line.strip())
    value = value.rstrip(":").strip()
    value = value.strip("`*_ \t")
    value = value.rstrip(":").strip()
    return re.sub(r"\s+", " ", value).upper()


def office_action_structure(oa_text: str) -> dict[str, Any]:
    headings = {_normalized_heading(line) for line in oa_text.splitlines() if line.strip()}
    has_detailed_action = "DETAILED ACTION" in headings
    has_conclusion = "CONCLUSION" in headings
    return {
        "valid": has_detailed_action and has_conclusion,
        "has_detailed_action": has_detailed_action,
        "has_conclusion": has_conclusion,
    }


def selected_references_schema(sel_text: str) -> dict[str, Any]:
    heading_re = re.compile(
        r"^\s*(?:#{1,6}\s*)?(?:\*\*|__)?\s*"
        r"(Patent\s+References?|Non[- ]Patent\s+Literature(?:\s*\(NPL\))?)"
        r"\s*:?\s*(?:\*\*|__)?\s*:?\s*$",
        re.I | re.M,
    )
    matches = list(heading_re.finditer(sel_text))

    def canonical_heading(value: str) -> str:
        return "Patent References" if value.lower().startswith("patent") else "Non-Patent Literature"

    headings = [canonical_heading(m.group(1).strip()) for m in matches]
    heading_set = set(headings)
    missing = [h for h in SELECTED_SCHEMA_HEADINGS if h not in heading_set]

    sections: dict[str, str] = {}
    for i, match in enumerate(matches):
        name = canonical_heading(match.group(1).strip())
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(sel_text)
        sections[name] = sel_text[start:end].strip()

    patent_section = sections.get("Patent References", "")
    npl_section = sections.get("Non-Patent Literature", "")
    schema_patents = extract_patent_ids(patent_section)
    schema_papers = extract_paper_ids(npl_section)

    required_fields = {
        "Patent References": ["Publication Date", "Role", "Relevant Claims", "Evidence", "Used For"],
        "Non-Patent Literature": ["Title", "Authors", "Year", "Venue", "Relevant Evidence", "Used For"],
    }
    field_missing: dict[str, list[str]] = {}
    for section, fields in required_fields.items():
        body = sections.get(section, "")
        if re.fullmatch(r"\s*None\s*", body, re.I):
            continue
        absent = [field for field in fields if not re.search(rf"^-\s*{re.escape(field)}\s*:", body, re.I | re.M)]
        if absent:
            field_missing[section] = absent

    return {
        # Parsing requires the two top-level evidence buckets. Markdown level,
        # emphasis, capitalization, extra headings, and optional field omissions
        # remain diagnostics rather than hard format failures.
        "valid": bool(sel_text.strip()) and not missing,
        "headings_seen": headings,
        "missing_headings": missing,
        "unexpected_headings": [],
        "missing_fields": field_missing,
        "schema_patents": schema_patents,
        "schema_papers": schema_papers,
    }


def outcome_evaluation(oa_text: str, sel_text: str, log_text: str) -> dict[str, Any]:
    combined = oa_text + "\n" + sel_text
    office_action_exists = OA_PATH.exists()
    selected_refs_exists = SEL_PATH.exists()
    oa_structure = office_action_structure(oa_text)
    statutory_terms = {
        "has_101": bool(re.search(r"35\s+U\.S\.C\.\s*101|\b101\b", oa_text, re.I)),
        "has_102": bool(re.search(r"35\s+U\.S\.C\.\s*102|\b102\b", oa_text, re.I)),
        "has_103": bool(re.search(r"35\s+U\.S\.C\.\s*103|\b103\b", oa_text, re.I)),
        "has_112": bool(re.search(r"35\s+U\.S\.C\.\s*112|\b112\b", oa_text, re.I)),
        "has_allowance": bool(re.search(r"reasons? for allowance|allowable|allowed", oa_text, re.I)),
    }
    has_rejection_basis = any(statutory_terms.values()) or bool(re.search(r"rejection|rejected", oa_text, re.I))
    has_prior_art = bool(re.search(r"prior art|reference|publication|patent|CN\d|US\d|EP\d|WO\d", combined, re.I))
    has_claim_mapping = bool(re.search(r"claim\s*1|claim\s*2|claim\s*3|limitation|element|mapping", oa_text, re.I))
    has_motivation = bool(re.search(r"motivation|combine|combination|would have been motivated|motivation_to_combine", oa_text, re.I))
    mentions_cutoff = bool(APP_DATE and (APP_DATE in combined or APP_DATE in log_text or "publication_date <" in combined or "publication_date lt" in combined))
    no_direct_curl = not bool(re.search(r"curl\s+https?://|curl\s+-", combined, re.I))

    patent_refs = extract_patent_ids(oa_text)
    paper_refs = extract_paper_ids(oa_text)
    selected_schema = selected_references_schema(sel_text) if selected_refs_exists else {"valid": False, "schema_patents": [], "schema_papers": [], "missing_headings": SELECTED_SCHEMA_HEADINGS, "missing_fields": {}}
    selected_patent_refs = selected_schema["schema_patents"] or extract_patent_ids(sel_text)
    selected_paper_refs = selected_schema["schema_papers"] or extract_paper_ids(sel_text)
    unused_selected_patents = sorted(set(selected_patent_refs) - set(patent_refs))
    unlisted_used_patents = sorted(set(patent_refs) - set(selected_patent_refs))
    unused_selected_papers = sorted({p.lower() for p in selected_paper_refs} - {p.lower() for p in paper_refs})
    unlisted_used_papers = sorted({p.lower() for p in paper_refs} - {p.lower() for p in selected_paper_refs})
    selected_matches_office_action = not (
        unused_selected_patents or unlisted_used_patents or unused_selected_papers or unlisted_used_papers
    )
    pub_dates = extract_dates(sel_text)
    reported_future_dates = [date for date in pub_dates if APP_DATE and date >= APP_DATE]
    reference_date_lookup = lookup_reference_dates(patent_refs)
    resolved_reference_dates = {ref: info.get("publication_date") for ref, info in reference_date_lookup.items() if info.get("publication_date")}
    db_future_references = [{"reference_id": ref, "publication_date": date} for ref, date in resolved_reference_dates.items() if APP_DATE and date >= APP_DATE]
    unresolved_reference_ids = [ref for ref in patent_refs if ref not in resolved_reference_dates]
    has_es_lookup = bool(os.environ.get("ES_HOST") and (os.environ.get("ES_INDEX_PATENTS") or os.environ.get("ES_INDEX_RETRIEVAL_POOL")))
    cutoff_violations = bool(reported_future_dates or db_future_references or (has_es_lookup and unresolved_reference_ids))
    respects_time_cutoff = 1.0 if APP_DATE and not cutoff_violations else 0.0

    gt = load_ground_truth()
    patent_pr = precision_recall(patent_refs, gt["patents"])
    paper_pr = precision_recall(paper_refs, gt["papers"])

    selected_ref_count = len(set(selected_patent_refs + selected_paper_refs))
    has_reference_selection = (
        selected_refs_exists
        and bool(selected_schema.get("valid"))
        and selected_matches_office_action
        and (selected_ref_count > 0 or "none" in sel_text.lower())
    )
    format_checks = {
        "office_action_present_and_nonempty": office_action_exists and bool(oa_text.strip()),
        "selected_references_present_and_nonempty": selected_refs_exists and bool(sel_text.strip()),
        "detailed_action_section_present": oa_structure["has_detailed_action"],
        "conclusion_section_present": oa_structure["has_conclusion"],
        "selected_references_structure_parseable": bool(selected_schema.get("valid")),
    }
    format_score = sum(bool(value) for value in format_checks.values()) / len(format_checks)
    content_score = 0.22 * has_rejection_basis + 0.22 * has_prior_art + 0.22 * has_claim_mapping + 0.14 * has_motivation + 0.10 * has_reference_selection + 0.10 * respects_time_cutoff
    # Search and visit tools enforce the cutoff. Independently verify final
    # citations here; do not reward the model merely for stating the cutoff.
    cutoff_score = respects_time_cutoff
    score = round(clamp01(0.35 * format_score + 0.45 * content_score + 0.20 * cutoff_score), 4)
    return {
        "version": "outcome-v1",
        "score": score,
        "format_score": round(format_score, 4),
        "content_score": round(content_score, 4),
        "cutoff_score": round(cutoff_score, 4),
        "files": {"office_action_md": str(OA_PATH), "office_action_exists": office_action_exists, "selected_references_md": str(SEL_PATH), "selected_references_exists": selected_refs_exists},
        "format_checks": format_checks,
        "office_action_structure": oa_structure,
        "content_checks": {**statutory_terms, "has_rejection_basis": has_rejection_basis, "has_prior_art": has_prior_art, "has_claim_mapping": has_claim_mapping, "has_motivation_to_combine": has_motivation, "has_reference_selection": bool(has_reference_selection), "selected_reference_signal_count": selected_ref_count, "selected_references_schema_valid": bool(selected_schema.get("valid"))},
        "references": {"patents_cited": patent_refs, "papers_cited": paper_refs, "selected_patents": selected_patent_refs, "selected_papers": selected_paper_refs, "selected_references_match_office_action": selected_matches_office_action, "unused_selected_patents": unused_selected_patents, "unlisted_used_patents": unlisted_used_patents, "unused_selected_papers": unused_selected_papers, "unlisted_used_papers": unlisted_used_papers, "selected_references_schema": selected_schema, "patent_reference_precision_recall": patent_pr, "paper_reference_precision_recall": paper_pr},
        "time_checks": {"application_date": APP_DATE or None, "application_date_source": APP_DATE_SOURCE, "cutoff_verifiable": bool(APP_DATE), "mentions_cutoff_diagnostic_only": mentions_cutoff, "publication_dates_seen_in_selected_references": pub_dates[:50], "reported_publication_dates_on_or_after_application_date": reported_future_dates, "reference_ids_seen": patent_refs[:100], "database_publication_dates_by_reference": resolved_reference_dates, "database_references_on_or_after_application_date": db_future_references, "unresolved_reference_ids": unresolved_reference_ids, "respects_time_cutoff": bool(respects_time_cutoff)},
        "curl_check": {"no_direct_curl_usage_in_outputs": no_direct_curl},
    }


def load_trajectory_messages() -> tuple[list[dict[str, Any]], str | None]:
    candidates = sorted(GATEWAY_TRAJ_DIR.glob("*_messages.json")) if GATEWAY_TRAJ_DIR.exists() else []
    if not candidates:
        return [], None
    # Prefer default_messages.json, otherwise newest/largest candidate.
    default = [p for p in candidates if p.name == "default_messages.json"]
    path = default[0] if default else max(candidates, key=lambda p: p.stat().st_size)
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return [], str(path)
    messages = [m for m in data.get("messages", []) if isinstance(m, dict)]
    return messages, str(path)


def tool_name(call: dict[str, Any]) -> str:
    fn = call.get("function") if isinstance(call.get("function"), dict) else {}
    return str(fn.get("name") or call.get("name") or "unknown")


def tool_args(call: dict[str, Any]) -> Any:
    fn = call.get("function") if isinstance(call.get("function"), dict) else {}
    raw = fn.get("arguments") if "arguments" in fn else call.get("arguments")
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return raw or {}


def canonical_query(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("query", "q", "search_query"):
            if value.get(key):
                return re.sub(r"\s+", " ", str(value[key]).strip().lower())
        parts = []
        for key in ("must", "should", "must_not"):
            if value.get(key):
                v = value[key]
                parts.append(f"{key}:{'|'.join(map(str, v)) if isinstance(v, list) else v}")
        return re.sub(r"\s+", " ", " ".join(parts).strip().lower())
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def extract_publication_arg(args: Any) -> str:
    if isinstance(args, dict):
        for key in ("publication_number", "patent_number", "publicationNumber", "id"):
            if args.get(key):
                return re.sub(r"\s+", "", str(args[key]).upper())
    return ""


def extract_paper_arg(args: Any) -> str:
    if isinstance(args, dict):
        for key in ("paper_id", "paperId", "id", "doi", "arxiv_id", "pmid"):
            if args.get(key):
                value = str(args[key])
                if key == "doi" and not value.lower().startswith("doi:"):
                    value = f"doi:{value}"
                elif key == "arxiv_id" and not value.lower().startswith("arxiv:"):
                    value = f"arxiv:{value}"
                elif key == "pmid" and not value.lower().startswith("pmid:"):
                    value = f"pmid:{value}"
                return normalize_paper_reference(value)
    return ""


def trajectory_from_messages(messages: list[dict[str, Any]], log_text: str, path: str | None) -> dict[str, Any]:
    assistant = [m for m in messages if m.get("role") == "assistant"]
    tools = [m for m in messages if m.get("role") == "tool"]
    tool_events: list[dict[str, Any]] = []
    seen_tool_call_ids: set[str] = set()
    for idx, message in enumerate(messages):
        if message.get("role") != "assistant":
            continue
        for call in message.get("tool_calls") or []:
            if not isinstance(call, dict):
                continue
            call_id = str(call.get("id") or "")
            # Responses requests replay prior output items. The gateway normally
            # consolidates that replay, but legacy or partial trajectories may
            # still contain the same call twice.
            if call_id and call_id in seen_tool_call_ids:
                continue
            if call_id:
                seen_tool_call_ids.add(call_id)
            args = tool_args(call)
            name = tool_name(call)
            tool_events.append({"message_index": idx, "tool_call_id": call_id or None, "tool_name": name, "arguments": args, "query": canonical_query(args) if name in SEARCH_TOOLS | PAPER_SEARCH_TOOLS else "", "publication_number": extract_publication_arg(args), "paper_id": extract_paper_arg(args)})

    counts = Counter(e["tool_name"] for e in tool_events)
    queries = [e["query"] for e in tool_events if e.get("query")]
    duplicate_query_count = sum(c - 1 for c in Counter(queries).values() if c > 1)
    query_rewrite_count = max(0, len(set(queries)) - 1) if queries else 0
    visit_patents = [e["publication_number"] for e in tool_events if e["tool_name"] in PATENT_VISIT_TOOLS and e.get("publication_number")]
    visit_papers = [e["paper_id"] for e in tool_events if e["tool_name"] in PAPER_VISIT_TOOLS and e.get("paper_id")]
    duplicate_visit_count = sum(c - 1 for c in Counter(visit_patents).values() if c > 1)
    search_events = [e for e in tool_events if e["tool_name"] in SEARCH_TOOLS]
    gt_data = load_verifier_ground_truth()
    gt_set = {
        normalized
        for value in (gt_data.get("patent_references_gt") or [])
        if (normalized := normalize_recall_reference(value))
    }
    gt_paper_set = {
        normalized
        for value in (gt_data.get("paper_references_gt") or [])
        if (normalized := normalize_paper_reference(value))
    }
    call_names = {str(event.get("tool_call_id")): event["tool_name"] for event in tool_events}
    search_result_refs: set[str] = set()
    paper_search_result_refs: set[str] = set()
    first_gt = None
    first_paper_gt = None
    completed_search_results = 0
    completed_paper_search_results = 0
    for message_index, message in enumerate(messages):
        if message.get("role") != "tool":
            continue
        call_id = str(message.get("tool_call_id") or "")
        name = call_names.get(call_id, "")
        content_text = trajectory_content_text(message.get("content"))
        if name in SEARCH_TOOLS:
            completed_search_results += 1
            refs = set(extract_recall_references(content_text))
            search_result_refs.update(refs)
            hits_here = sorted(gt_set & refs)
            if hits_here and first_gt is None:
                first_gt = {
                    "message_index": message_index,
                    "tool_call_id": call_id,
                    "tool_name": name,
                    "searches_before_or_at_hit": completed_search_results,
                    "ground_truth_hits": hits_here,
                }
        elif name in PAPER_SEARCH_TOOLS:
            completed_paper_search_results += 1
            refs = set(extract_paper_references(content_text))
            paper_search_result_refs.update(refs)
            hits_here = sorted(gt_paper_set & refs)
            if hits_here and first_paper_gt is None:
                first_paper_gt = {
                    "message_index": message_index,
                    "tool_call_id": call_id,
                    "tool_name": name,
                    "searches_before_or_at_hit": completed_paper_search_results,
                    "ground_truth_hits": hits_here,
                }
    visited_ref_set = {
        normalized
        for value in visit_patents
        if (normalized := normalize_recall_reference(value))
    }
    selected_ref_set = set(extract_recall_references(read(SEL_PATH)))
    office_action_ref_set = set(extract_recall_references(read(OA_PATH)))
    used_ref_set = selected_ref_set & office_action_ref_set
    discovered_ref_set = search_result_refs | visited_ref_set
    visited_paper_set = set(visit_papers)
    selected_paper_set = set(extract_paper_references(read(SEL_PATH)))
    office_action_paper_set = set(extract_paper_references(read(OA_PATH)))
    used_paper_set = selected_paper_set & office_action_paper_set
    discovered_paper_set = paper_search_result_refs | visited_paper_set

    def funnel_stage(observed: set[str], ground_truth: set[str]) -> dict[str, Any]:
        hits = sorted(ground_truth & observed)
        return {
            "recall": round(len(hits) / len(ground_truth), 4) if ground_truth else None,
            "hits": hits,
            "missing": sorted(ground_truth - observed),
        }

    reference_funnel = {
        "metric_definition": {
            "trajectory_discovery_recall": "GT appeared in any search result OR was visited; independent metric, not scored",
            "oa_usage_recall": "GT cited in office_action.md AND listed in selected_references.md; independent metric, not scored",
        },
        "ground_truth_patents": sorted(gt_set),
        "search_returned": funnel_stage(search_result_refs, gt_set),
        "visited": funnel_stage(visited_ref_set, gt_set),
        "discovered": funnel_stage(discovered_ref_set, gt_set),
        "selected": funnel_stage(selected_ref_set, gt_set),
        "office_action_usage": funnel_stage(used_ref_set, gt_set),
        "first_search_hit": first_gt,
    }
    paper_reference_funnel = {
        "metric_definition": {
            "paper_trajectory_discovery_recall": "paper GT appeared in any paper search result OR was visited; independent metric, not scored",
            "paper_oa_usage_recall": "paper GT cited in office_action.md AND listed in selected_references.md; independent metric, not scored",
        },
        "ground_truth_papers": sorted(gt_paper_set),
        "search_returned": funnel_stage(paper_search_result_refs, gt_paper_set),
        "visited": funnel_stage(visited_paper_set, gt_paper_set),
        "discovered": funnel_stage(discovered_paper_set, gt_paper_set),
        "selected": funnel_stage(selected_paper_set, gt_paper_set),
        "office_action_usage": funnel_stage(used_paper_set, gt_paper_set),
        "first_search_hit": first_paper_gt,
    }

    total_searches = sum(counts[t] for t in SEARCH_TOOLS | PAPER_SEARCH_TOOLS)
    total_visits = sum(counts[t] for t in PATENT_VISIT_TOOLS)
    curl_attempts = count_patterns(log_text, [r"curl is blocked", r"blocked curl", r"\bcurl\b"])
    harness_started = ("Starting USPTO Office Action generation" in log_text or "[Codex Runner] Input patent:" in log_text or bool(messages))
    harness_completed = ("Office Action generation complete" in log_text or "examination is complete" in log_text.lower())
    node_crash = "markAsUncloneable" in log_text or "Node.js v20" in log_text
    repeated_error_count = count_patterns(log_text, [r"TypeError:", r"Traceback", r"Error:", r"failed", r"authentication"])
    loop_markers = count_patterns(log_text, [r"still running", r"retry", r"again", r"refine the query"])
    repeated_search_rate = round(duplicate_query_count / len(queries), 4) if queries else 0.0
    repeated_visit_rate = round(duplicate_visit_count / len(visit_patents), 4) if visit_patents else 0.0
    infinite_loop_risk = duplicate_query_count >= 5 or loop_markers >= 10 or repeated_search_rate > 0.6

    return {
        "version": "trajectory-statistics-v6",
        "scoring_weight": 0.0,
        "source": {"messages_path": path, "agent_log_path": str(AGENT_LOG_PATH)},
        "turns": {"total_messages": len(messages), "assistant_messages": len(assistant), "tool_result_messages": len(tools), "total_tool_calls": len(tool_events)},
        "tool_counts": dict(counts),
        "search_counts": {"total_searches": total_searches, "bm25_calls": counts["es_patent_bm25_search"], "bool_search_calls": counts["es_patent_bool_search"], "semantic_search_calls": counts["es_patent_semantic_search"], "paper_search_calls": sum(counts[t] for t in PAPER_SEARCH_TOOLS), "paper_bm25_calls": counts["es_paper_bm25_search"], "paper_bool_search_calls": counts["es_paper_bool_search"], "paper_semantic_search_calls": counts["es_paper_semantic_search"]},
        "visit_counts": {"patent_visits": total_visits, "claims_visits": counts["visit_patent_claims"], "description_visits": counts["visit_patent_description"], "paper_visits": sum(counts[t] for t in PAPER_VISIT_TOOLS)},
        "query_rewrite": {"queries": queries, "unique_queries": sorted(set(queries)), "query_count": len(queries), "unique_query_count": len(set(queries)), "query_rewrite_count": query_rewrite_count, "duplicate_query_count": duplicate_query_count, "repeated_search_rate": repeated_search_rate},
        "visits": {"visited_patents": visit_patents, "unique_visited_patents": sorted(set(visit_patents)), "visited_papers": visit_papers, "unique_visited_papers": sorted(set(visit_papers)), "duplicate_visit_count": duplicate_visit_count, "repeated_visit_rate": repeated_visit_rate},
        "ground_truth_reference_funnel": reference_funnel,
        "ground_truth_paper_funnel": paper_reference_funnel,
        "quality_flags": {"harness_started": harness_started, "harness_completed": harness_completed, "curl_attempts": curl_attempts, "repeated_error_count": repeated_error_count, "loop_markers": loop_markers, "infinite_loop_risk": infinite_loop_risk, "node_runtime_crash_detected": node_crash},
        "tool_events": tool_events,
    }


def trajectory_fallback_from_log(log_text: str) -> dict[str, Any]:
    tool_counts = {"es_patent_bm25_search": count_patterns(log_text, [r"\bes_patent_bm25_search\b", r"\bes_search\b", r"BM25 search"]), "es_patent_bool_search": count_patterns(log_text, [r"\bes_patent_bool_search\b", r"Structured bool search"]), "es_patent_semantic_search": count_patterns(log_text, [r"\bes_patent_semantic_search\b", r"semantic search"]), "bash": count_patterns(log_text, [r"\bbash\b", r"tool_call.*bash"]), "read": count_patterns(log_text, [r"\bread\b", r"/workspace/input"]), "write": count_patterns(log_text, [r"\bwrite\b", r"office_action\.md", r"selected_references\.md"]), "curl_attempts": count_patterns(log_text, [r"curl is blocked", r"blocked curl", r"\bcurl\b"])}
    query_lines = [line.strip()[:300] for line in log_text.splitlines() if re.search(r"es_patent_bm25_search|es_search|BM25|query", line, re.I)]
    duplicate_query_count = sum(count - 1 for count in Counter(query_lines).values() if count > 1)
    repeated_error_count = count_patterns(log_text, [r"TypeError:", r"Traceback", r"Error:", r"failed", r"authentication"])
    loop_markers = count_patterns(log_text, [r"still running", r"retry", r"again", r"refine the query"])
    infinite_loop_risk = duplicate_query_count >= 5 or loop_markers >= 10 or len(log_text) > 250000
    used_es = tool_counts["es_patent_bm25_search"] > 0 or "BM25 Elasticsearch Patent Search extension loaded" in log_text
    harness_started = "Starting USPTO Office Action generation" in log_text or "[Codex Runner] Input patent:" in log_text
    harness_completed = "Office Action generation complete" in log_text or "examination is complete" in log_text.lower()
    node_crash = "markAsUncloneable" in log_text or "Node.js v20" in log_text
    return {"version": "trajectory-statistics-v6-log-fallback", "scoring_weight": 0.0, "source": {"messages_path": None, "agent_log_path": str(AGENT_LOG_PATH)}, "tool_counts": tool_counts, "query_rewrite": {"duplicate_query_count": duplicate_query_count, "sample_query_lines": query_lines[:20]}, "quality_flags": {"harness_started": harness_started, "harness_completed": harness_completed, "used_es_patent_bm25_search_or_loaded_extension": used_es, "repeated_error_count": repeated_error_count, "loop_markers": loop_markers, "infinite_loop_risk": infinite_loop_risk, "node_runtime_crash_detected": node_crash}, "ground_truth_reference_funnel": {"available": False, "reason": "OpenAI-format messages unavailable"}, "ground_truth_paper_funnel": {"available": False, "reason": "OpenAI-format messages unavailable"}}


def trajectory_evaluation(log_text: str) -> dict[str, Any]:
    messages, path = load_trajectory_messages()
    if messages:
        return trajectory_from_messages(messages, log_text, path)
    return trajectory_fallback_from_log(log_text)


def main() -> int:
    oa_text = read(OA_PATH)
    sel_text = read(SEL_PATH)
    log_text = read(AGENT_LOG_PATH)
    completion = completion_evaluation(oa_text, sel_text)
    trajectory = trajectory_evaluation(log_text)
    reward = completion["score"]
    funnel = trajectory.get("ground_truth_reference_funnel", {})
    paper_funnel = trajectory.get("ground_truth_paper_funnel", {})
    retrieval_metrics = {
        "version": "retrieval-metrics-v4",
        "aggregation_policy": "none: every metric is reported independently",
        "completion_inclusion": False,
        "ground_truth_patents": completion["citation_metrics"]["ground_truth_patents"],
        "ground_truth_papers": completion["paper_citation_metrics"]["ground_truth_papers"],
        "trajectory_available": bool(trajectory.get("source", {}).get("messages_path")),
        "search_return_recall": funnel.get("search_returned", {}).get("recall"),
        "visit_recall": funnel.get("visited", {}).get("recall"),
        "trajectory_discovery_recall": funnel.get("discovered", {}).get("recall"),
        "selected_recall": funnel.get("selected", {}).get("recall"),
        "oa_usage_precision": completion["citation_metrics"]["precision"],
        "oa_usage_recall": completion["citation_metrics"]["recall"],
        "oa_usage_f1": completion["citation_metrics"]["f1"],
        "paper_search_return_recall": paper_funnel.get("search_returned", {}).get("recall"),
        "paper_visit_recall": paper_funnel.get("visited", {}).get("recall"),
        "paper_trajectory_discovery_recall": paper_funnel.get("discovered", {}).get("recall"),
        "paper_selected_recall": paper_funnel.get("selected", {}).get("recall"),
        "paper_oa_usage_precision": completion["paper_citation_metrics"]["precision"],
        "paper_oa_usage_recall": completion["paper_citation_metrics"]["recall"],
        "paper_oa_usage_f1": completion["paper_citation_metrics"]["f1"],
        "trajectory_funnel": funnel,
        "paper_trajectory_funnel": paper_funnel,
        "office_action_usage": completion["citation_metrics"],
        "paper_office_action_usage": completion["paper_citation_metrics"],
    }
    reward_summary = {
        "reward": reward,
        "completion_score": reward,
        "format_score": completion["format"]["score"],
        "judge_available": 1.0 if completion["llm_judge"].get("available") else 0.0,
        "label_judge_available": 1.0 if completion["label_judge"].get("available") else 0.0,
        "oa_usage_applicable": 1.0 if completion["citation_metrics"]["applicable"] else 0.0,
        "paper_oa_usage_applicable": 1.0 if completion["paper_citation_metrics"]["applicable"] else 0.0,
        "trajectory_available": 1.0 if retrieval_metrics["trajectory_available"] else 0.0,
        "trajectory_scoring_weight": 0.0,
    }
    decision_accuracy = completion["decision_statute_metrics"]["decision"].get("accuracy")
    statute_metrics = completion["decision_statute_metrics"]["statutes"]
    if isinstance(decision_accuracy, (int, float)) and not isinstance(decision_accuracy, bool):
        reward_summary["decision_accuracy"] = decision_accuracy
        decision_class = completion["decision_statute_metrics"]["decision"].get("ground_truth_class")
        if decision_class in DECISION_LABELS:
            reward_summary[f"decision_recall_{decision_class}"] = decision_accuracy
    for source_name, output_name in (
        ("accuracy", "statute_accuracy"),
        ("precision", "statute_precision"),
        ("recall", "statute_recall"),
        ("f1", "statute_f1"),
    ):
        value = statute_metrics.get(source_name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            reward_summary[output_name] = value
    judge_metric = completion["llm_judge"].get("normalized_score")
    if isinstance(judge_metric, (int, float)) and not isinstance(judge_metric, bool):
        reward_summary["llm_judge_score"] = judge_metric
    judge_dimensions = completion["llm_judge"].get("dimensions")
    if isinstance(judge_dimensions, dict) and all(
        isinstance(judge_dimensions.get(name), (int, float))
        and not isinstance(judge_dimensions.get(name), bool)
        for name in JUDGE_DIMENSIONS
    ):
        for name in JUDGE_DIMENSIONS:
            reward_summary[f"llm_judge_{name}_mean"] = judge_dimensions[name]
        reward_summary["llm_judge_overall_mean"] = round(
            sum(float(judge_dimensions[name]) for name in JUDGE_DIMENSIONS) / len(JUDGE_DIMENSIONS),
            4,
        )
    # Harbor rewards must contain numeric values only. Optional retrieval and
    # citation metrics are omitted when they are not applicable/observable;
    # their numeric applicability flags above distinguish that state from 0.
    for metric_name in (
        "search_return_recall",
        "visit_recall",
        "trajectory_discovery_recall",
        "selected_recall",
        "oa_usage_precision",
        "oa_usage_recall",
        "oa_usage_f1",
        "paper_search_return_recall",
        "paper_visit_recall",
        "paper_trajectory_discovery_recall",
        "paper_selected_recall",
        "paper_oa_usage_precision",
        "paper_oa_usage_recall",
        "paper_oa_usage_f1",
    ):
        metric_value = retrieval_metrics.get(metric_name)
        if isinstance(metric_value, (int, float)) and not isinstance(metric_value, bool):
            reward_summary[metric_name] = metric_value
    details = {
        "version": "evaluation-v6",
        "reward": reward,
        "completion_score": reward,
        "completion": completion,
        "retrieval_metrics": retrieval_metrics,
        "trajectory_statistics": trajectory,
        "scoring": {
            "reward_source": "completion_score_only",
            "independent_not_scored": [
                "decision_accuracy",
                "decision_class_recall_metrics",
                "statute_accuracy",
                "statute_precision",
                "statute_recall",
                "statute_f1",
                "search_return_recall",
                "visit_recall",
                "trajectory_discovery_recall",
                "selected_recall",
                "oa_usage_precision",
                "oa_usage_recall",
                "oa_usage_f1",
                "paper_search_return_recall",
                "paper_visit_recall",
                "paper_trajectory_discovery_recall",
                "paper_selected_recall",
                "paper_oa_usage_precision",
                "paper_oa_usage_recall",
                "paper_oa_usage_f1",
            ],
            "pass_threshold": None,
        },
        "saved_outputs": {
            "office_action_md": str(OA_PATH) if OA_PATH.exists() else None,
            "selected_references_md": str(SEL_PATH) if SEL_PATH.exists() else None,
            "agent_log": str(AGENT_LOG_PATH) if AGENT_LOG_PATH.exists() else None,
            "trajectory_messages": trajectory.get("source", {}).get("messages_path"),
        },
    }
    reports = {
        "reward.json": reward_summary,
        "evaluation_details.json": details,
        "completion_report.json": completion,
        "llm_judge_report.json": completion["llm_judge"],
        "label_judge_report.json": completion["label_judge"],
        "decision_statute_metrics_report.json": completion["decision_statute_metrics"],
        "citation_metrics_report.json": completion["citation_metrics"],
        "paper_citation_metrics_report.json": completion["paper_citation_metrics"],
        "retrieval_metrics_report.json": retrieval_metrics,
        "trajectory_report.json": trajectory,
    }
    for name, obj in reports.items():
        (LOG_DIR / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (LOG_DIR / "reward.txt").write_text(str(reward) + "\n", encoding="utf-8")
    human = [
        "# Patent Agent Evaluation v2 Report",
        "",
        f"Completion score: {reward}",
        f"Evaluation status: {completion['status']}",
        "Pass threshold: not defined",
        "",
        "## Completion components",
        f"- format: {completion['format']['score']}",
        f"- LLM judge: {completion['llm_judge'].get('normalized_score')}",
        f"- LLM judge dimension means: {completion['llm_judge'].get('dimensions')}",
        f"- LLM judge overall mean (1-10): {reward_summary.get('llm_judge_overall_mean')}",
        f"- Decision accuracy: {reward_summary.get('decision_accuracy')} (reported independently)",
        f"- Decision class-conditional metric: {completion['decision_statute_metrics']['decision'].get('ground_truth_class')}",
        f"- Statute exact-match accuracy: {reward_summary.get('statute_accuracy')} (reported independently)",
        f"- Statute precision / recall / F1: {reward_summary.get('statute_precision')} / {reward_summary.get('statute_recall')} / {reward_summary.get('statute_f1')}",
        f"- OA-usage GT precision: {completion['citation_metrics']['precision']}",
        f"- OA-usage GT recall: {completion['citation_metrics']['recall']} (reported independently)",
        f"- OA-usage GT F1: {completion['citation_metrics']['f1']}",
        f"- Paper OA-usage GT precision: {completion['paper_citation_metrics']['precision']}",
        f"- Paper OA-usage GT recall: {completion['paper_citation_metrics']['recall']} (reported independently)",
        f"- Paper OA-usage GT F1: {completion['paper_citation_metrics']['f1']}",
        f"- weights: {completion['weights']}",
        "- retrieval metrics are reported independently and do not affect completion/reward",
        "",
        "## Trajectory statistics (not scored)",
        f"- source: {trajectory.get('source', {}).get('messages_path') or trajectory.get('source', {}).get('agent_log_path')}",
        f"- total tool calls: {trajectory.get('turns', {}).get('total_tool_calls')}",
        f"- search counts: {trajectory.get('search_counts')}",
        f"- visit counts: {trajectory.get('visit_counts')}",
        f"- GT discovery recall: {trajectory.get('ground_truth_reference_funnel', {}).get('discovered', {}).get('recall')}",
        f"- Paper GT discovery recall: {trajectory.get('ground_truth_paper_funnel', {}).get('discovered', {}).get('recall')}",
        f"- query rewrite: {trajectory.get('query_rewrite')}",
        f"- quality flags: {trajectory.get('quality_flags')}",
    ]
    (LOG_DIR / "evaluation_report.md").write_text("\n".join(human) + "\n", encoding="utf-8")
    # Scores are measurements, not pass/fail gates. Infrastructure/parsing
    # failures are represented by completion.status=incomplete in the reports.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
