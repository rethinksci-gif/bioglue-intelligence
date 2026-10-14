"""CLI: python -m scanner {scan,structures,import-newsletter,verify-refs}"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA, load, model
from .quarters import current, window


def cmd_scan(args):
    from .llm import LLM
    from .sources import discover
    from .triage import triage

    quarter = args.quarter or current()
    start, end = window(quarter)
    end = min(end, datetime.now(timezone.utc).date())
    routes = load("routes")
    print(f"Scanning {quarter}: {start} to {end}")
    found = discover(routes, start, end)
    path = DATA / "candidates" / f"{quarter}.json"
    previous = {c["id"]: c for c in json.loads(path.read_text())["candidates"]} if path.exists() else {}
    fresh = [r for r in found if r["id"] not in previous or previous[r["id"]].get("route") == "untriaged"]
    print(f"{len(found)} discovered, {len(fresh)} new to triage")
    llm = LLM(budget=args.max_calls)
    judged = triage(fresh, routes, llm) if fresh else []
    merged = {**previous, **{c["id"]: c for c in judged}}
    cands = sorted(merged.values(), key=lambda c: (-c.get("relevance", 0), c["date"]))
    for c in cands:
        # Publisher abstracts are only needed until a record is triaged; do not republish them.
        if c.get("route") != "untriaged":
            c.pop("abstract", None)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "quarter": quarter, "window": [str(start), str(window(quarter)[1])], "scanned_through": str(end),
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "model": model(),
        "llm_calls": llm.calls, "usage": llm.usage,
        "note": "Machine-triaged discovery leads (DeepSeek flash). Not verified evidence: each needs primary-source review before it enters a quarterly issue.",
        "candidates": cands,
    }, indent=2, ensure_ascii=False) + "\n")
    print(f"{sum(c.get('shown', False) for c in cands)} shown / {len(cands)} total -> {path}; calls={llm.calls} usage={llm.usage}")


def cmd_structures(args):
    from .structures import render

    print("rendered:", ", ".join(render()))


def cmd_import(args):
    from .newsletter import export

    print(export(Path(args.evidence), Path(args.spec), args.quarter))


def _crossref_title(doi: str) -> str:
    """Polite-pool request with backoff on 429/5xx."""
    import time
    import urllib.error

    from .config import config
    from .sources import UA

    req = urllib.request.Request(f"https://api.crossref.org/works/{doi}?mailto={config()['scan']['mailto']}", headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)["message"]["title"][0]
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503) or attempt == 4:
                raise
            time.sleep(2 ** attempt * 2)
        finally:
            time.sleep(0.3)
    raise RuntimeError("unreachable")


def cmd_verify_refs(args):
    bad = 0
    for r in load("references"):
        if "doi" not in r:
            continue
        try:
            title = _crossref_title(r["doi"])
        except Exception as exc:
            print(f"FAIL {r['id']}: {exc}")
            bad += 1
            continue
        norm = lambda s: "".join(ch for ch in s.casefold() if ch.isalnum())
        ok = norm(r["title"])[:40] == norm(title)[:40]
        bad += not ok
        print(("ok  " if ok else "DIFF"), r["id"], "|", title[:90])
    sys.exit(1 if bad else 0)


def main():
    p = argparse.ArgumentParser(prog="scanner")
    sub = p.add_subparsers(required=True)
    s = sub.add_parser("scan", help="discover and triage leads for a quarter")
    s.add_argument("--quarter")
    s.add_argument("--max-calls", type=int)
    s.set_defaults(fn=cmd_scan)
    sub.add_parser("structures", help="render chemical structures to SVG").set_defaults(fn=cmd_structures)
    i = sub.add_parser("import-newsletter", help="export a newsletter build to public quarter data")
    i.add_argument("evidence"); i.add_argument("spec"); i.add_argument("--quarter", required=True)
    i.set_defaults(fn=cmd_import)
    sub.add_parser("verify-refs", help="re-check reference DOIs against Crossref").set_defaults(fn=cmd_verify_refs)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
