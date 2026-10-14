"""Batch triage with DeepSeek flash. Code, not the model, decides what is shown:
quotes must occur verbatim in the record, route ids must exist, and low-relevance items are hidden."""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field

from .config import PROMPTS, config
from .llm import LLM, BudgetExceeded


class Judgement(BaseModel):
    id: str
    route: str
    relevance: float = Field(ge=0, le=1)
    signal: Literal["research", "scale-up", "supply", "policy", "market", "other"] = "other"
    application: str = "not stated"
    summary: str = ""
    quote: str = ""


class Batch(BaseModel):
    items: list[Judgement]


def _norm(text: str) -> str:
    return " ".join(text.split()).casefold()


def system_prompt(routes: list[dict]) -> str:
    listing = "\n".join(f"- {r['id']}: {r['name']} — {r['tagline']}" for r in routes)
    return (PROMPTS / "triage.md").read_text().replace("{{routes}}", listing)


def apply(record: dict, j: Judgement, route_ids: set[str]) -> dict:
    """Merge a model judgement into a record, enforcing the code-side checks."""
    source_text = record["title"] + " " + record.get("abstract", "")
    quote_ok = bool(j.quote) and _norm(j.quote) in _norm(source_text)
    route = j.route if j.route in route_ids else "none"
    flags = []
    if j.quote and not quote_ok:
        flags.append("quote-not-in-source")
    if not record.get("abstract"):
        flags.append("title-only")
    return {
        **record,
        "route": route,
        "relevance": round(j.relevance, 2),
        "signal": j.signal,
        "application": j.application[:80],
        "summary": j.summary[:300] if quote_ok else "",
        "quote": j.quote if quote_ok else "",
        "flags": flags,
        "shown": route != "none" and quote_ok and j.relevance >= config()["scan"]["min_relevance"],
    }


def triage(records: list[dict], routes: list[dict], llm: LLM, log=print) -> list[dict]:
    route_ids = {r["id"] for r in routes}
    system = system_prompt(routes)
    size = config()["llm"]["batch_size"]
    out = []
    for i in range(0, len(records), size):
        batch = records[i : i + size]
        payload = [{"id": r["id"], "title": r["title"], "abstract": r.get("abstract", "")[:2500],
                    "venue": r["venue"], "date": r["date"], "kind": r["kind"]} for r in batch]
        try:
            result = llm.json_call(system, json.dumps(payload, ensure_ascii=False), Batch, max_tokens=300 * len(batch))
        except BudgetExceeded as exc:
            log(f"  ! {exc}; {len(records) - i} records left untriaged")
            out.extend({**r, "route": "untriaged", "shown": False, "flags": ["budget"]} for r in records[i:])
            break
        by_id = {j.id: j for j in result.items}
        for r in batch:
            j = by_id.get(r["id"])
            out.append(apply(r, j, route_ids) if j else {**r, "route": "untriaged", "shown": False, "flags": ["missing-judgement"]})
        log(f"  triaged {min(i + size, len(records))}/{len(records)}")
    return out
