#!/usr/bin/env python3
"""Dependency-free MCP server exposing the PI-Harness patent tool contract."""

from __future__ import annotations

import base64
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any


def enabled(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def integer(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


ES_HOST = os.getenv("ES_HOST", "").rstrip("/")
ES_USER = os.getenv("ES_USER", "")
ES_PASSWORD = os.getenv("ES_PASSWORD", "")
DEFAULT_INDEX = os.getenv("ES_INDEX_RETRIEVAL_POOL", "patex-patents-current")
INDICES = {
    "retrieval_pool": DEFAULT_INDEX,
    "patents": os.getenv("ES_INDEX_PATENTS", DEFAULT_INDEX),
}
PAPER_INDEX = os.getenv("ES_INDEX_PAPERS", "patex-papers-current")
SEMANTIC_INDEX = os.getenv("ES_SEMANTIC_INDEX", INDICES["patents"])
VECTOR_FIELD = os.getenv("ES_SEMANTIC_VECTOR_FIELD", "bge_m3_dense")
PAPER_SEMANTIC_INDEX = PAPER_INDEX
PAPER_VECTOR_FIELD = os.getenv("ES_PAPER_SEMANTIC_VECTOR_FIELD", VECTOR_FIELD)
EMBED_URL = os.getenv("ES_SEMANTIC_EMBED_URL") or os.getenv("ES_BGE_M3_EMBED_URL", "")
EMBED_MODEL = os.getenv("ES_SEMANTIC_EMBED_MODEL", "bge-m3")
EMBED_QUERY_PREFIX = os.getenv("ES_SEMANTIC_QUERY_PREFIX", "")


def normalize_date(value: Any) -> str:
    match = re.search(r"(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})", str(value or ""))
    if not match:
        return ""
    year, month, day = map(int, match.groups())
    return f"{year:04d}-{month:02d}-{day:02d}"


APPLICATION_DATE = normalize_date(os.getenv("APPLICATION_DATE", ""))
SSL_CONTEXT = ssl._create_unverified_context()
SOURCE_FIELDS = [
    "publication_number",
    "publication_date",
    "pub_date",
    "publicationDate",
    "title",
    "abstract",
    "ipc",
    "cpc",
    "inventors",
]
SEARCH_FIELDS = [
    "title^5",
    "abstract^4",
]
PAPER_SOURCE_FIELDS = [
    "paper_id", "canonical_id", "doi", "arxiv_id", "pmid", "title", "authors",
    "abstract", "publication_date", "publication_year", "venue", "journal", "keywords",
]
PAPER_SEARCH_FIELDS = [
    "title^6", "abstract^4",
]
PATENT_BOOL_FIELDS = {
    "title", "abstract", "ipc", "cpc", "publication_number",
    "publication_number_norm", "inventors", "publication_date",
}
PAPER_BOOL_FIELDS = {
    "title", "abstract", "keywords", "authors", "authors_text", "venue", "journal",
    "doi", "arxiv_id", "pmid", "publication_date", "publication_year",
}


def unsupported_query_fields(query: str, allowed: set[str]) -> list[str]:
    fields = {match.lower() for match in re.findall(r"(?<!\\)\b([A-Za-z_][A-Za-z0-9_.]*)\s*:", query)}
    return sorted(fields - allowed)


def auth_header() -> str:
    token = f"{ES_USER}:{ES_PASSWORD}" if ES_PASSWORD else ES_USER
    return "Basic " + base64.b64encode(token.encode()).decode()


def request_json(url: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = {"Authorization": auth_header()}
    data = None
    method = "GET"
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
        method = "POST"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {message[:1000]}") from exc


def es_search(index: str, body: dict[str, Any]) -> dict[str, Any]:
    if not ES_HOST:
        raise RuntimeError("ES_HOST is not configured")
    if not index:
        raise RuntimeError("Elasticsearch index is not configured")
    return request_json(f"{ES_HOST}/{index}/_search", body)


def es_mget(index: str, ids: list[str]) -> dict[str, Any]:
    if not ES_HOST:
        raise RuntimeError("ES_HOST is not configured")
    return request_json(
        f"{ES_HOST}/{index}/_mget",
        {"docs": [{"_id": doc_id, "_source": SOURCE_FIELDS} for doc_id in ids]},
    )


def cutoff_filter() -> list[dict[str, Any]]:
    if not APPLICATION_DATE:
        return []
    return [{"range": {"publication_date": {"lt": APPLICATION_DATE}}}]


def clamp(value: Any, default: int, maximum: int, minimum: int = 1) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def clean_hit(hit: dict[str, Any], rank: int) -> dict[str, Any]:
    source = hit.get("_source") or {}
    raw_inventors = source.get("inventors") or []
    if not isinstance(raw_inventors, list):
        raw_inventors = [raw_inventors]
    inventors = [str(value).strip() for value in raw_inventors if str(value).strip()]
    return {
        "rank": rank,
        "publication_number": source.get("publication_number", ""),
        "publication_date": normalize_date(
            source.get("publication_date") or source.get("pub_date") or source.get("publicationDate")
        ),
        "title": source.get("title", ""),
        "abstract": str(source.get("abstract") or "")[:1200],
        "ipc": source.get("ipc") or [],
        "cpc": source.get("cpc") or [],
        "inventors": inventors[:10],
        "inventor_count": len(inventors),
        "inventors_truncated": len(inventors) > 10,
        "score": round(float(hit["_score"]), 4) if isinstance(hit.get("_score"), (int, float)) else None,
    }


def render_results(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No results found."
    blocks = []
    for item in results:
        blocks.append(
            "\n".join(
                [
                    f"## {item['rank']}. {item['publication_number']} — {item['title']}",
                    f"Publication Date: {item['publication_date'] or 'N/A'}",
                    f"IPC: {', '.join(map(str, item['ipc']))}",
                    f"CPC: {', '.join(map(str, item['cpc']))}",
                    f"Inventors: {', '.join(item['inventors'])}"
                    + (
                        f" (+{item['inventor_count'] - 10} more; truncated)"
                        if item["inventors_truncated"]
                        else ""
                    ),
                    f"Score: {item['score']}",
                    "",
                    str(item["abstract"])[:2000],
                ]
            )
        )
    return "\n\n---\n\n".join(blocks)


def result(text: str, details: dict[str, Any], is_error: bool = False) -> dict[str, Any]:
    # Codex prioritizes structuredContent over content when both are present.
    # Search details happened to contain the result records, but visit details
    # contain only paging metadata, which hid the actual claims/description from
    # the model. Return the same plain-text evidence contract used by PI.
    value: dict[str, Any] = {"content": [{"type": "text", "text": text}]}
    if is_error:
        value["isError"] = True
    return value


def search_results(index: str, body: dict[str, Any]) -> list[dict[str, Any]]:
    data = es_search(index, body)
    hits = data.get("hits", {}).get("hits") or []
    cleaned = [clean_hit(hit, rank) for rank, hit in enumerate(hits, 1)]
    if APPLICATION_DATE:
        cleaned = [item for item in cleaned if item["publication_date"] < APPLICATION_DATE]
    return cleaned


def bm25(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query") or "").strip()
    if not query:
        return result("query is required", {"error": "query is required"}, True)
    corpus = str(params.get("corpus") or "retrieval_pool")
    if corpus not in INDICES:
        return result("invalid corpus", {"allowed": list(INDICES)}, True)
    size = clamp(params.get("size"), integer("BM25_SIZE_DEFAULT", 5), integer("BM25_SIZE_MAX", 20))
    body = {
        "query": {
            "bool": {
                "must": [{"multi_match": {"query": query, "fields": SEARCH_FIELDS, "type": "best_fields"}}],
                "filter": cutoff_filter(),
            }
        },
        "size": size,
        "_source": SOURCE_FIELDS,
    }
    results = search_results(INDICES[corpus], body)
    details = {"results": results, "application_date_cutoff": APPLICATION_DATE, "query": query, "corpus": corpus}
    return result(render_results(results), details)


def bool_search(params: dict[str, Any]) -> dict[str, Any]:
    allowed = {"query", "default_operator", "corpus", "size"}
    unexpected = sorted(set(params) - allowed)
    if unexpected:
        return result(
            "Unsupported parameters for query_string search.",
            {"error": "unsupported parameters", "parameters": unexpected},
            True,
        )
    query = str(params.get("query") or "").strip()
    if not query:
        return result("A query_string expression is required.", {"error": "missing query"}, True)
    if len(query) > 4000:
        return result("query exceeds 4000 characters.", {"error": "query too long"}, True)
    unsupported_fields = unsupported_query_fields(query, PATENT_BOOL_FIELDS)
    if unsupported_fields:
        return result(
            "The query uses fields that are not exposed by patent metadata search.",
            {"error": "unsupported fields", "fields": unsupported_fields, "allowed_fields": sorted(PATENT_BOOL_FIELDS)},
            True,
        )
    corpus = str(params.get("corpus") or "retrieval_pool")
    if corpus not in INDICES:
        return result("invalid corpus", {"allowed": list(INDICES)}, True)
    size = clamp(params.get("size"), integer("BOOL_SIZE_DEFAULT", 5), integer("BOOL_SIZE_MAX", 20))
    default_operator = str(params.get("default_operator") or "AND").upper()
    if default_operator not in {"AND", "OR"}:
        return result("default_operator must be AND or OR.", {"error": "invalid default_operator"}, True)

    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "query": query,
                            "fields": SEARCH_FIELDS,
                            "default_operator": default_operator,
                            "analyze_wildcard": True,
                            "allow_leading_wildcard": False,
                        }
                    }
                ],
                "filter": cutoff_filter(),
            }
        },
        "size": size,
        "_source": SOURCE_FIELDS,
    }
    results = search_results(INDICES[corpus], body)
    details = {
        "results": results,
        "query": query,
        "default_operator": default_operator,
        "application_date_cutoff": APPLICATION_DATE,
    }
    if not results:
        return result(
            "The advanced query_string expression executed successfully but returned zero results. "
            "Broaden it by removing a weak AND constraint, replacing synonyms with an OR group, "
            "or using a less restrictive fielded clause.",
            details,
        )
    return result(render_results(results), details)


def semantic_search(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query") or "").strip()
    if not query:
        return result("query is required", {"error": "query is required"}, True)
    if not EMBED_URL:
        return result("ES_BGE_M3_EMBED_URL is not configured", {"error": "embedding endpoint missing"}, True)
    payload = json.dumps({
        "input": EMBED_QUERY_PREFIX + query,
        "model": EMBED_MODEL,
        "encoding_format": "float",
    }).encode()
    request = urllib.request.Request(EMBED_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
        embedding_data = json.loads(response.read().decode())
    vector = (
        embedding_data.get("embedding")
        or embedding_data.get("vector")
        or ((embedding_data.get("data") or [{}])[0]).get("embedding")
        or ((embedding_data.get("embeddings") or [None])[0])
    )
    if not isinstance(vector, list) or not vector:
        return result("Embedding endpoint returned no vector", {"error": "invalid embedding response"}, True)
    if len(vector) != 1024:
        return result(
            f"Embedding endpoint returned {len(vector)} dimensions; expected 1024",
            {"error": "embedding dimension mismatch"},
            True,
        )
    size = clamp(params.get("size"), integer("SEMANTIC_SIZE_DEFAULT", 5), integer("SEMANTIC_SIZE_MAX", 20))
    candidates = clamp(
        params.get("num_candidates"),
        integer("SEMANTIC_NUM_CANDIDATES_DEFAULT", 200),
        integer("SEMANTIC_NUM_CANDIDATES_MAX", 2000),
        20,
    )
    # Domain-specific embeddings are stored in compact, source-disabled sidecar
    # indices.  Retrieve a larger candidate set there, hydrate metadata from the
    # canonical patent index by the shared publication-number document ID, then
    # apply the task's filing-date cutoff.  The default BGE-M3 path remains a
    # single filtered kNN query against the canonical index.
    sidecar = SEMANTIC_INDEX != INDICES["patents"]
    retrieval_size = min(candidates, max(size * 10, 100)) if sidecar else size
    filters = [] if sidecar else cutoff_filter()
    body = {
        "knn": {
            "field": VECTOR_FIELD,
            "query_vector": vector,
            "k": retrieval_size,
            "num_candidates": candidates,
            "filter": filters,
        },
        "size": retrieval_size,
        "_source": False if sidecar else SOURCE_FIELDS,
    }
    if sidecar:
        data = es_search(SEMANTIC_INDEX, body)
        vector_hits = data.get("hits", {}).get("hits") or []
        ids = [str(hit.get("_id") or "") for hit in vector_hits if hit.get("_id")]
        metadata = es_mget(INDICES["patents"], ids).get("docs") or []
        metadata_by_id = {
            str(doc.get("_id")): doc.get("_source") or {}
            for doc in metadata
            if doc.get("found") and doc.get("_id")
        }
        hydrated_hits = []
        for hit in vector_hits:
            source = metadata_by_id.get(str(hit.get("_id")))
            if source:
                hydrated_hits.append({**hit, "_source": source})
        results = [clean_hit(hit, rank) for rank, hit in enumerate(hydrated_hits, 1)]
        if APPLICATION_DATE:
            results = [item for item in results if item["publication_date"] < APPLICATION_DATE]
        results = results[:size]
        for rank, item in enumerate(results, 1):
            item["rank"] = rank
    else:
        results = search_results(SEMANTIC_INDEX, body)
    details = {
        "results": results,
        "query": query,
        "vector_field": VECTOR_FIELD,
        "application_date_cutoff": APPLICATION_DATE,
    }
    return result(render_results(results), details)


def clean_paper_hit(hit: dict[str, Any], rank: int) -> dict[str, Any]:
    source = hit.get("_source") or {}
    raw_authors = source.get("authors") or []
    if not isinstance(raw_authors, list):
        raw_authors = [raw_authors]
    authors = [str(value).strip() for value in raw_authors if str(value).strip()]
    return {
        "rank": rank,
        "paper_id": source.get("paper_id") or hit.get("_id") or "",
        "canonical_id": source.get("canonical_id") or "",
        "doi": source.get("doi") or "",
        "arxiv_id": source.get("arxiv_id") or "",
        "pmid": source.get("pmid") or "",
        "title": source.get("title") or "",
        "authors": authors[:10],
        "author_count": len(authors),
        "publication_date": normalize_date(source.get("publication_date")),
        "publication_year": source.get("publication_year"),
        "venue": source.get("venue") or source.get("journal") or "",
        "abstract": str(source.get("abstract") or "")[:1600],
        "score": hit.get("_score"),
    }


def render_paper_results(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No paper results found."
    blocks = []
    for item in results:
        authors = ", ".join(item["authors"]) or "N/A"
        if item["author_count"] > 10:
            authors += f" (+{item['author_count'] - 10} more; truncated)"
        blocks.append("\n".join([
            f"## {item['rank']}. {item['title'] or item['paper_id']} (score: {item['score']})",
            f"Paper ID: {item['paper_id'] or 'N/A'}",
            f"DOI: {item['doi'] or 'N/A'}",
            f"arXiv: {item['arxiv_id'] or 'N/A'}",
            f"PMID: {item['pmid'] or 'N/A'}",
            f"Publication Date: {item['publication_date'] or 'N/A'}",
            f"Venue: {item['venue'] or 'N/A'}",
            f"Authors: {authors}",
            "",
            item["abstract"] or "No abstract available",
        ]))
    return "\n\n---\n\n".join(blocks)


def paper_results(body: dict[str, Any]) -> list[dict[str, Any]]:
    data = es_search(PAPER_INDEX, body)
    hits = data.get("hits", {}).get("hits") or []
    results = [clean_paper_hit(hit, rank) for rank, hit in enumerate(hits, 1)]
    if APPLICATION_DATE:
        results = [item for item in results if item["publication_date"] and item["publication_date"] < APPLICATION_DATE]
    return results


def paper_bm25_search(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query") or "").strip()
    if not query:
        return result("Paper search requires a query.", {"error": "query is required"}, True)
    size = clamp(params.get("size"), integer("PAPER_SIZE_DEFAULT", 5), integer("PAPER_SIZE_MAX", 20))
    body = {
        "query": {"bool": {
            "must": [{"multi_match": {"query": query, "fields": PAPER_SEARCH_FIELDS, "type": "best_fields"}}],
            "filter": cutoff_filter(),
        }},
        "size": size,
        "_source": PAPER_SOURCE_FIELDS,
        "highlight": {"fields": {"title": {}, "abstract": {}}, "fragment_size": 240, "number_of_fragments": 2},
    }
    results = paper_results(body)
    return result(render_paper_results(results), {
        "query": query,
        "results": results,
        "index": PAPER_INDEX,
        "mode": "BM25",
        "application_date_cutoff": APPLICATION_DATE,
    })


def paper_bool_search(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query") or "").strip()
    if not query:
        return result("A query_string expression is required.", {"error": "missing query"}, True)
    if len(query) > 4000:
        return result("query exceeds 4000 characters.", {"error": "query too long"}, True)
    unsupported_fields = unsupported_query_fields(query, PAPER_BOOL_FIELDS)
    if unsupported_fields:
        return result(
            "The query uses fields that are not exposed by paper metadata search.",
            {"error": "unsupported fields", "fields": unsupported_fields, "allowed_fields": sorted(PAPER_BOOL_FIELDS)},
            True,
        )
    default_operator = str(params.get("default_operator") or "AND").upper()
    if default_operator not in {"AND", "OR"}:
        return result("default_operator must be AND or OR.", {"error": "invalid default_operator"}, True)
    size = clamp(params.get("size"), integer("PAPER_SIZE_DEFAULT", 5), integer("PAPER_SIZE_MAX", 20))
    body = {
        "query": {"bool": {
            "must": [{"query_string": {
                "query": query,
                "fields": PAPER_SEARCH_FIELDS,
                "default_operator": default_operator,
                "analyze_wildcard": True,
                "allow_leading_wildcard": False,
            }}],
            "filter": cutoff_filter(),
        }},
        "size": size,
        "_source": PAPER_SOURCE_FIELDS,
        "highlight": {"fields": {"title": {}, "abstract": {}}, "fragment_size": 240, "number_of_fragments": 2},
    }
    results = paper_results(body)
    text = render_paper_results(results)
    if not results:
        text = "The advanced paper query_string expression executed successfully but returned zero results."
    return result(text, {
        "query": query,
        "default_operator": default_operator,
        "results": results,
        "index": PAPER_INDEX,
        "mode": "query_string",
        "application_date_cutoff": APPLICATION_DATE,
    })


def query_embedding(query: str) -> list[float]:
    if not EMBED_URL:
        raise RuntimeError("ES_BGE_M3_EMBED_URL is not configured")
    payload = json.dumps({"input": query, "model": "bge-m3", "encoding_format": "float"}).encode()
    request = urllib.request.Request(EMBED_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
        data = json.loads(response.read().decode())
    vector = data.get("embedding") or data.get("vector") or ((data.get("data") or [{}])[0]).get("embedding") or ((data.get("embeddings") or [None])[0])
    if not isinstance(vector, list) or len(vector) != 1024:
        length = len(vector) if isinstance(vector, list) else 0
        raise RuntimeError(f"BGE-M3 returned {length} dimensions; expected 1024")
    return vector


def paper_semantic_search(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query") or "").strip()
    if not query:
        return result("query is required", {"error": "query is required"}, True)
    try:
        vector = query_embedding(query)
    except Exception as exc:
        return result(str(exc), {"error": str(exc)}, True)
    size = clamp(params.get("size"), integer("PAPER_SIZE_DEFAULT", 5), integer("PAPER_SIZE_MAX", 20))
    candidates = clamp(
        params.get("num_candidates"),
        integer("SEMANTIC_NUM_CANDIDATES_DEFAULT", 200),
        integer("SEMANTIC_NUM_CANDIDATES_MAX", 2000),
        20,
    )
    body = {
        "knn": {
            "field": PAPER_VECTOR_FIELD,
            "query_vector": vector,
            "k": size,
            "num_candidates": candidates,
            "filter": cutoff_filter(),
        },
        "size": size,
        "_source": PAPER_SOURCE_FIELDS,
    }
    try:
        data = es_search(PAPER_SEMANTIC_INDEX, body)
        hits = data.get("hits", {}).get("hits") or []
        results = [clean_paper_hit(hit, rank) for rank, hit in enumerate(hits, 1)]
        if APPLICATION_DATE:
            results = [item for item in results if item["publication_date"] and item["publication_date"] < APPLICATION_DATE]
    except Exception as exc:
        return result(
            f"BGE-M3 semantic paper search failed: {exc}",
            {"error": str(exc), "index": PAPER_SEMANTIC_INDEX, "vector_field": PAPER_VECTOR_FIELD},
            True,
        )
    return result(render_paper_results(results), {
        "query": query,
        "results": results,
        "index": PAPER_SEMANTIC_INDEX,
        "mode": "bge_m3_semantic",
        "vector_field": PAPER_VECTOR_FIELD,
        "application_date_cutoff": APPLICATION_DATE,
    })


def find_patent(params: dict[str, Any]) -> dict[str, Any] | None:
    publication = str(params.get("publication_number") or "").strip()
    patent_id = str(params.get("patent_id") or "").strip()
    should = []
    if publication:
        should.extend(
            [
                {"term": {"publication_number": publication}},
                {"term": {"publication_number_norm": re.sub(r"\s+", "", publication.lower())}},
            ]
        )
    if patent_id:
        should.append({"term": {"patent_id": patent_id}})
    if not should:
        return None
    body = {
        "query": {"bool": {"should": should, "minimum_should_match": 1, "filter": cutoff_filter()}},
        "size": 1,
        "_source": True,
    }
    hits = es_search(INDICES["patents"], body).get("hits", {}).get("hits") or []
    return (hits[0].get("_source") or {}) if hits else None


def visit(params: dict[str, Any], level: str) -> dict[str, Any]:
    patent = find_patent(params)
    if not patent:
        return result("Patent not found or blocked by the application-date cutoff.", {"level": level}, True)
    fields = {
        "claims": ["claims", "claim_text"],
        "description": ["description", "full_text", "specification"],
    }[level]
    raw: Any = ""
    for field in fields:
        if patent.get(field):
            raw = patent[field]
            break
    if isinstance(raw, (list, dict)):
        text = json.dumps(raw, ensure_ascii=False, indent=2)
    else:
        text = str(raw or "")
    offset = max(0, int(params.get("offset") or 0)) if level == "description" else 0
    default_chars = 10000 if level == "description" else 12000
    maximum = clamp(params.get("max_chars"), default_chars, 30000, 500)
    window = text[offset : offset + maximum]
    available = bool(text)
    details = {
        "level": level,
        "available": available,
        "returned_chars": len(window),
        "total_chars": len(text),
        "truncated": offset + len(window) < len(text),
    }
    if level == "description" and details["truncated"]:
        details["next_offset"] = offset + len(window)
    if not available:
        return result(f"{level.title()} text is unavailable for this patent.", details)
    return result(window, details)


def visit_paper(params: dict[str, Any]) -> dict[str, Any]:
    paper_id = str(params.get("paper_id") or "").strip()
    if not paper_id:
        return result("paper_id is required", {"error": "paper_id is required"}, True)
    normalized_doi = re.sub(r"^doi:", "", paper_id, flags=re.I)
    normalized_arxiv = re.sub(r"^arxiv:", "", paper_id, flags=re.I)
    body = {
        "query": {"bool": {
            "should": [
                {"ids": {"values": [paper_id]}}, {"term": {"paper_id": paper_id}},
                {"term": {"canonical_id": paper_id}}, {"term": {"doi": normalized_doi}},
                {"term": {"arxiv_id": normalized_arxiv}},
            ],
            "minimum_should_match": 1,
            "filter": cutoff_filter(),
        }},
        "size": 1,
        "_source": True,
    }
    hits = es_search(PAPER_INDEX, body).get("hits", {}).get("hits") or []
    if not hits:
        return result("Paper not found or blocked by the application-date cutoff.", {"paper_id": paper_id, "index": PAPER_INDEX, "application_date_cutoff": APPLICATION_DATE}, True)
    paper = hits[0].get("_source") or {}
    raw = str(paper.get("full_text") or paper.get("first_pages_text") or "")
    offset = max(0, int(params.get("offset") or 0))
    maximum = clamp(params.get("max_chars"), 10000, 30000, 500)
    window = raw[offset : offset + maximum]
    metadata = {
        key: paper.get(key) for key in (
            "paper_id", "canonical_id", "work_id", "version_id", "doi", "arxiv_id", "pmid", "title",
            "authors", "abstract", "publication_date", "publication_year", "venue", "journal", "volume",
            "issue", "pages", "open_access", "license", "pdf_available", "source_urls",
        )
    }
    text = "\n".join([
        f"# {paper.get('title') or paper_id}", f"Paper ID: {paper_id}",
        f"DOI: {paper.get('doi') or 'N/A'}", f"arXiv: {paper.get('arxiv_id') or 'N/A'}",
        f"Authors: {', '.join(map(str, paper.get('authors') or [])) or 'N/A'}",
        f"Publication: {paper.get('venue') or 'N/A'} ({paper.get('publication_year') or 'N/A'})",
        "", "## Abstract", str(paper.get("abstract") or "N/A"), "", "## Full Text Window",
        window or "Full text unavailable; metadata record is present.",
    ])
    details = {"paper": metadata, "index": PAPER_INDEX, "evidence_level": "full_text",
               "full_text_available": bool(raw), "offset": offset, "returned_chars": len(window),
               "total_chars": len(raw), "truncated": offset + len(window) < len(raw)}
    if details["truncated"]:
        details["next_offset"] = offset + len(window)
    return result(text, details)


SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Technical search query, for example 'lithium battery electrolyte', 'semiconductor packaging', 'neural network image classification', or Chinese patent keywords.",
        },
        "size": {
            "type": "integer",
            "minimum": 1,
            "maximum": integer("BM25_SIZE_MAX", 20),
            "description": f"Number of results to return. Default {integer('BM25_SIZE_DEFAULT', 5)}, maximum {integer('BM25_SIZE_MAX', 20)}.",
        },
        "corpus": {
            "anyOf": [
                {"type": "string", "const": "retrieval_pool"},
                {"type": "string", "const": "patents"},
            ],
            "default": "retrieval_pool",
            "description": "Patent metadata pool preset. retrieval_pool and patents currently resolve to the same stable patent alias.",
        },
    },
    "required": ["query"],
    "additionalProperties": False,
}
LOOKUP_PROPERTIES = {
    "publication_number": {"type": "string", "description": "Publication number from search results."},
    "patent_id": {"type": "string", "description": "Patent id when publication number is unavailable."},
    "max_chars": {"type": "integer", "minimum": 500, "maximum": 30000, "description": "Maximum returned characters. Default 12000, maximum 30000."},
}


def tool_definitions() -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    if enabled("TOOL_BM25", "true"):
        tools.append({"name": "es_patent_bm25_search", "description": "BM25-only patent retrieval over title and abstract. Returns Level 1 metadata (publication number, publication date, title, abstract, IPC/CPC, and inventors); claims and descriptions are available only through the visit tools. Elasticsearch DSL, sorting, highlighting, and the application-date cutoff are controlled by the tool.", "inputSchema": SEARCH_SCHEMA})
    if enabled("TOOL_BOOL_SEARCH", "true"):
        tools.append(
            {
                "name": "es_patent_bool_search",
                "description": "Search patent metadata using Elasticsearch query_string syntax. Unqualified terms search title and abstract; field-scoped clauses may target title, abstract, IPC/CPC, publication number, inventors, or publication date. Supports Boolean operators, phrases, grouping, wildcards, fuzziness, and boosting. Results are restricted to publications before the application date.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "minLength": 1, "maxLength": 4000, "description": "Elasticsearch query_string expression. Supports AND/OR/NOT, parentheses, quoted phrases, field scoping, wildcards, fuzziness, and boosts."},
                        "default_operator": {
                            "anyOf": [
                                {"type": "string", "const": "AND"},
                                {"type": "string", "const": "OR"},
                            ],
                            "default": "AND",
                            "description": "Operator used between unqualified terms. Default AND.",
                        },
                        "corpus": {
                            "anyOf": [
                                {"type": "string", "const": "retrieval_pool"},
                                {"type": "string", "const": "patents"},
                            ],
                            "default": "retrieval_pool",
                            "description": "Search level. Default retrieval_pool.",
                        },
                        "size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": integer("BOOL_SIZE_MAX", 20),
                            "description": f"Number of results. Default {integer('BOOL_SIZE_DEFAULT', 5)}, maximum {integer('BOOL_SIZE_MAX', 20)}.",
                        },
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            }
        )
    if enabled("TOOL_SEMANTIC_SEARCH", "false"):
        tools.append(
            {
                "name": "es_patent_semantic_search",
                "description": "Level 1 semantic patent retrieval using BGE-M3 embeddings. Returns Level 1 metadata (publication number, publication date, title, abstract, IPC/CPC, and inventors); claims and descriptions are available only through the visit tools.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural-language technical query for semantic retrieval."},
                        "size": {"type": "integer", "minimum": 1, "maximum": integer("SEMANTIC_SIZE_MAX", 20), "description": f"Number of results. Default {integer('SEMANTIC_SIZE_DEFAULT', 5)}, maximum {integer('SEMANTIC_SIZE_MAX', 20)}."},
                        "num_candidates": {"type": "integer", "minimum": 20, "maximum": integer("SEMANTIC_NUM_CANDIDATES_MAX", 2000), "description": f"Approximate vector-search candidate pool. Default {integer('SEMANTIC_NUM_CANDIDATES_DEFAULT', 200)}, maximum {integer('SEMANTIC_NUM_CANDIDATES_MAX', 2000)}."},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            }
        )
    if tools:
        for name, level, description in [
            ("visit_patent_claims", "claims", "Level 2 visit tool. Fetch the full claims text for one patent selected from Level 1 search results."),
            ("visit_patent_description", "description", "Level 3 visit tool. Fetch a window of the patent description. Use offset to continue reading long descriptions only when needed."),
        ]:
            properties = dict(LOOKUP_PROPERTIES)
            if level == "description":
                properties["offset"] = {"type": "integer", "minimum": 0, "description": "Character offset for paging through long descriptions. Default 0."}
                properties["max_chars"] = {"type": "integer", "minimum": 500, "maximum": 30000, "description": "Maximum returned characters. Default 10000, maximum 30000."}
            tools.append(
                {
                    "name": name,
                    "description": description,
                    "inputSchema": {"type": "object", "properties": properties, "additionalProperties": False},
                }
            )
    if enabled("TOOL_PAPER_BM25", "true"):
        tools.append({
            "name": "es_paper_bm25_search",
            "description": "BM25 literature retrieval over paper titles and abstracts. Returns stable paper_id values and Level 1 metadata. The tool enforces publication_date strictly before the current application's filing date.",
            "inputSchema": {"type": "object", "properties": {
                "query": {"type": "string", "minLength": 1, "description": "Technical literature query; include distinctive mechanisms, materials, methods, or known title/author terms."},
                "size": {"type": "integer", "minimum": 1, "maximum": integer("PAPER_SIZE_MAX", 20), "description": f"Number of candidates. Default {integer('PAPER_SIZE_DEFAULT', 5)}, maximum {integer('PAPER_SIZE_MAX', 20)}."},
            }, "required": ["query"], "additionalProperties": False},
        })
    if enabled("TOOL_PAPER_BOOL_SEARCH", "true"):
        tools.append({
            "name": "es_paper_bool_search",
            "description": "Search literature metadata using Elasticsearch query_string syntax. Unqualified terms search title and abstract; field-scoped clauses may use title:, abstract:, keywords:, authors:, authors_text:, venue:, journal:, doi:, arxiv_id:, pmid:, publication_date:, or publication_year:. For example, authors:\"Yoshua Bengio\". Supports Boolean operators, phrases, grouping, wildcards, fuzziness, and boosting. Results are restricted to publications before the application date.",
            "inputSchema": {"type": "object", "properties": {
                "query": {"type": "string", "minLength": 1, "maxLength": 4000, "description": "Elasticsearch query_string expression."},
                "default_operator": {
                    "anyOf": [
                        {"type": "string", "const": "AND"},
                        {"type": "string", "const": "OR"},
                    ],
                    "default": "AND",
                },
                "size": {"type": "integer", "minimum": 1, "maximum": integer("PAPER_SIZE_MAX", 20), "description": f"Number of results. Default {integer('PAPER_SIZE_DEFAULT', 5)}, maximum {integer('PAPER_SIZE_MAX', 20)}."},
            }, "required": ["query"], "additionalProperties": False},
        })
    if enabled("TOOL_PAPER_SEMANTIC_SEARCH", "false"):
        tools.append({
            "name": "es_paper_semantic_search",
            "description": "Level 1 semantic literature retrieval using BGE-M3 embeddings. Returns stable paper_id values, metadata, and abstracts. The application-date cutoff is enforced.",
            "inputSchema": {"type": "object", "properties": {
                "query": {"type": "string", "minLength": 1, "description": "Natural-language technical query for semantic literature retrieval."},
                "size": {"type": "integer", "minimum": 1, "maximum": integer("PAPER_SIZE_MAX", 20), "description": f"Number of results. Default {integer('PAPER_SIZE_DEFAULT', 5)}, maximum {integer('PAPER_SIZE_MAX', 20)}."},
                "num_candidates": {"type": "integer", "minimum": 20, "maximum": integer("SEMANTIC_NUM_CANDIDATES_MAX", 2000), "description": f"Approximate vector-search candidate pool. Default {integer('SEMANTIC_NUM_CANDIDATES_DEFAULT', 200)}, maximum {integer('SEMANTIC_NUM_CANDIDATES_MAX', 2000)}."},
            }, "required": ["query"], "additionalProperties": False},
        })
    if any([
        enabled("TOOL_PAPER_BM25", "true"),
        enabled("TOOL_PAPER_BOOL_SEARCH", "true"),
        enabled("TOOL_PAPER_SEMANTIC_SEARCH", "false"),
    ]):
        tools.append({
            "name": "visit_paper",
            "description": "Final-stage evidence visit after a paper search. Use a returned paper_id such as doi:10.1000/example, arxiv:2201.00680v1, or a curated source ID. Returns full text in pageable windows when available and explicitly reports when the corpus has metadata/abstract only. The strict application-date cutoff is enforced.",
            "inputSchema": {"type": "object", "properties": {
                "paper_id": {"type": "string", "minLength": 1, "description": "Exact stable paper_id returned by a paper search tool or another trusted source."},
                "offset": {"type": "integer", "minimum": 0, "description": "Character offset for paging through paper text. Default 0."},
                "max_chars": {"type": "integer", "minimum": 500, "maximum": 30000, "description": "Maximum returned text characters. Default 10000, maximum 30000."},
            }, "required": ["paper_id"], "additionalProperties": False},
        })
    return tools


CALLS = {
    "es_patent_bm25_search": bm25,
    "es_patent_bool_search": bool_search,
    "es_patent_semantic_search": semantic_search,
    "visit_patent_claims": lambda params: visit(params, "claims"),
    "visit_patent_description": lambda params: visit(params, "description"),
    "es_paper_bm25_search": paper_bm25_search,
    "es_paper_bool_search": paper_bool_search,
    "es_paper_semantic_search": paper_semantic_search,
    "visit_paper": visit_paper,
}


def respond(request_id: Any, value: dict[str, Any] | None = None, error: dict[str, Any] | None = None) -> None:
    message: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        message["error"] = error
    else:
        message["result"] = value or {}
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main() -> None:
    for line in sys.stdin:
        try:
            message = json.loads(line)
            method = message.get("method")
            request_id = message.get("id")
            if request_id is None:
                continue
            if method == "initialize":
                respond(
                    request_id,
                    {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "patent-harness", "version": "0.1.0"},
                    },
                )
            elif method == "tools/list":
                respond(request_id, {"tools": tool_definitions()})
            elif method == "tools/call":
                params = message.get("params") or {}
                name = params.get("name")
                arguments = params.get("arguments") or {}
                if name not in CALLS or name not in {tool["name"] for tool in tool_definitions()}:
                    respond(request_id, error={"code": -32601, "message": f"Unknown or disabled tool: {name}"})
                    continue
                try:
                    respond(request_id, CALLS[name](arguments))
                except Exception as exc:
                    print(f"[patent-mcp] {name}: {exc}", file=sys.stderr, flush=True)
                    respond(request_id, result(str(exc), {"error": str(exc)}, True))
            elif method == "ping":
                respond(request_id, {})
            else:
                respond(request_id, error={"code": -32601, "message": f"Method not found: {method}"})
        except Exception as exc:
            print(f"[patent-mcp] protocol error: {exc}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
