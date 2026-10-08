Act as a USPTO patent examiner and prepare an Office Action for the patent application provided in `/workspace/input/patent.md`, applying the relevant provisions of 35 U.S.C. in a formal, objective, and evidence-based manner.

## Available Retrieval Tools

Patent search tools:

{PATENT_SEARCH_TOOLS}

Patent visit tools:

{PATENT_VISIT_TOOLS}

Non-patent literature tools:

{PAPER_SEARCH_TOOLS}

## Retrieval Protocol

- Multiple complementary search tools are available. Select or combine them according to the claim language, retrieval objective, and quality of the returned candidates.
- Results of search tools are the metadata of patent application. They do not replace claims or description visits.
- `visit_patent_claims` provides a candidate patent's full claim language and claim dependencies.
- When claims or abstract information is insufficient, `visit_patent_description` can provide the detailed disclosure.
- Do not use curl, wget, Python, shell, or another network client to query Elasticsearch service directly.
- Use only references whose publication date is strictly earlier than the current application's filing/application date.
- Stop when you judge that the available evidence is sufficient to complete the examination. The examination budget is up to {MAX_INTERACTION_TURNS} model-interaction turns and {AGENT_INFERENCE_TIMEOUT} seconds of agent wall-clock time.

## Examination Rules

- Perform element-by-element factual mapping before deciding allowance or rejection.
- Apply only statutes that are supported by the record: 101, 102, 103, 112, and double patenting.
- A 102 rejection requires one reference to teach every limitation.
- A 103 rejection must map each limitation and state a clear motivation to combine.
- Cite only disclosures supported by the selected references or provided local inputs.
- Use natural USPTO-style prose and omit inapplicable statutory headings.

## Required Outputs

Write both files:

- `/workspace/output/office_action.md`
- `/workspace/output/selected_references.md`

`office_action.md` must start exactly with:

```text
DETAILED ACTION
```

Use only applicable sections from this list:

```text
OPENING STATEMENT
CLAIM REJECTIONS - 35 U.S.C. 101
CLAIM REJECTIONS - 35 U.S.C. 102
CLAIM REJECTIONS - 35 U.S.C. 103
CLAIM REJECTIONS - 35 U.S.C. 112(a)/(b)
DOUBLE PATENTING
REASONS FOR ALLOWANCE
CONCLUSION
```

## Selected References

`selected_references.md` is the evidence list for the final Office Action. Include only patent references and non-patent literature actually cited or relied upon in `office_action.md`.

Use exactly these level-2 headings. Write `None` when a section has no references.

```markdown
## Patent References

### USXXXXXXXXA1
- Publication Date:
- Role:
- Relevant Claims:
- Evidence:
- Used For: 102, 103

## Non-Patent Literature

### DOI/arXiv/PMID or Title
- Title:
- Authors:
- Year:
- Venue:
- Relevant Evidence:
- Used For:
```

Every entry in `selected_references.md` must also appear in `office_action.md`, and every patent or paper relied upon in `office_action.md` must be listed in `selected_references.md`.
