import json
from datetime import date

import yaml

from scanner.config import DATA, ROOT, load
from scanner.quarters import current, window
from scanner.triage import Judgement, apply

ROUTE_IDS = {r["id"] for r in load("routes")}


def test_quarter_windows():
    assert window("2026-Q1") == (date(2025, 12, 1), date(2026, 2, 28))
    assert window("2028-Q1")[1] == date(2028, 2, 29)
    assert window("2026-Q4") == (date(2026, 9, 1), date(2026, 11, 30))
    assert current(date(2026, 12, 3)) == "2027-Q1"
    assert current(date(2026, 10, 14)) == "2026-Q4"
    assert current(date(2026, 3, 1)) == "2026-Q2"


def rec(**kw):
    return {"id": "doi:x", "title": "Soy protein adhesive for plywood", "abstract": "We report a soy adhesive cured with PAE.", **kw}


def test_quote_must_be_verbatim():
    good = apply(rec(), Judgement(id="doi:x", route="proteins", relevance=0.9, summary="s", quote="soy adhesive cured with PAE"), ROUTE_IDS)
    assert good["shown"] and good["quote"]
    bad = apply(rec(), Judgement(id="doi:x", route="proteins", relevance=0.9, summary="s", quote="record wet strength"), ROUTE_IDS)
    assert not bad["shown"] and not bad["summary"] and "quote-not-in-source" in bad["flags"]


def test_unknown_route_and_low_relevance_hidden():
    assert not apply(rec(), Judgement(id="doi:x", route="magic", relevance=0.9, quote="soy adhesive"), ROUTE_IDS)["shown"]
    assert not apply(rec(), Judgement(id="doi:x", route="proteins", relevance=0.3, quote="soy adhesive"), ROUTE_IDS)["shown"]


def test_data_cross_references():
    refs = {r["id"] for r in load("references")}
    mols = {m["id"] for m in load("structures")}
    for r in load("routes"):
        assert set(r["refs"]) <= refs, r["id"]
        assert set(r["structures"]) <= mols, r["id"]
    for c in load("challenges"):
        assert set(c["routes"]) <= ROUTE_IDS
    for m in load("structures"):
        assert set(m["routes"]) <= ROUTE_IDS | {"incumbents"}


def test_published_data_has_no_full_text():
    for path in (DATA / "quarters").glob("*.json"):
        q = json.loads(path.read_text())
        assert all("text" not in s for s in q["sources"])
        for item in q["items"]:
            assert item["routes"] and set(item["routes"]) <= ROUTE_IDS
            assert all(f["value"] in f["quote"] for f in item["facts"])
    for path in (DATA / "candidates").glob("*.json"):
        for c in json.loads(path.read_text())["candidates"]:
            assert c.get("route") == "untriaged" or "abstract" not in c
            if c.get("shown"):
                assert c["route"] in ROUTE_IDS and c["quote"]


def test_flash_only():
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    assert cfg["llm"]["model"] == "deepseek-flash"
