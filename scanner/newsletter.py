"""Export a reviewed BIOGLUE newsletter build to public site data.

Only quotes, locators and source metadata are exported: full-text snapshots stay in the
private research workspace (copyright), and nothing here upgrades an item's review status."""
from __future__ import annotations

import json
from pathlib import Path

from .config import DATA

# Editorial route assignment for the 2026-Q3 records (technology_id -> routes).
ROUTES = {
    "BG-circular-c-lignin-thermoset": ["lignin"],
    "BG-bindethics-ecohesive": ["proteins"],
    "BG-resicare-5hmf": ["crosslinkers"],
    "BG-maap-acrylic-acid": ["acrylics"],
    "BG-pk-lignin-formaldehyde": ["lignin"],
    "BG-casein-beech": ["proteins"],
}
ROUTE_NOTES = {
    "BG-bindethics-ecohesive": "Route assigned editorially: the release names brewing by-products but does not disclose the binder chemistry.",
}
LABELS = {"country": "Geography", "milestone": "Milestone", "chemistry": "Chemistry", "binder": "Binder",
          "crosslinker": "Crosslinker", "feedstock": "Renewable basis", "fossil_remaining": "Fossil components",
          "application": "Application", "scale": "Demonstrated scale", "status": "Status", "capacity": "Capacity",
          "performance": "Performance", "manufacturing": "Manufacturing", "benchmark": "Incumbent comparison"}
MISSING = {"Not disclosed", "Not assessed", "Conflicting evidence"}
HOLDS = [
    {"id": "hold-lignin-zein", "routes": ["lignin", "proteins"], "title": "Lignin-zein debondable plywood adhesive",
     "date": "2026-06-24", "doi": "10.1039/d6gc02129h",
     "reason": "Author manuscript recovered, but veneer thickness (1.5 vs 1 mm) and dry spread (83 vs ~76 g/m²) differ between its sections; publisher version not yet compared."},
    {"id": "hold-casein-beech", "routes": ["proteins"], "title": "Casein adhesive on beech compared with PVAc",
     "date": "2026-08-16", "doi": "10.3390/f17080972",
     "reason": "Retained HTML was revised on 4 September, after the quarter cutoff; comparison withheld until the original August version is recovered."},
    {"id": "hold-pulp-residue", "routes": ["lignin"], "title": "Flame-retardant wood adhesive prepared from pulp mill residues",
     "date": None, "doi": "10.1039/d6gc02014c",
     "reason": "Repository access blocked (HTTP 403); only Crossref metadata retrieved, so no methods or results are reported."},
]


def export(evidence_path: Path, spec_path: Path, quarter: str) -> Path:
    data = json.loads(evidence_path.read_text())
    spec = json.loads(spec_path.read_text())
    sources = {s["id"]: s for s in data["sources"]}
    records = {e["id"]: e for e in data["evidence"]}
    items, used = [], set()
    for d in spec["editorial"]:
        if not d["selected"]:
            continue
        e = records[d["evidence_id"]]
        facts = []
        for key, label in LABELS.items():
            f = e[key]
            if f["value"] in MISSING:
                continue
            used.add(f["source_id"])
            ctx = {k: f[k] for k in ("unit", "conditions", "basis", "method", "comparator") if f[k] not in MISSING}
            if key == "capacity":
                ctx["status"] = e["capacity_kind"]
                ctx["product"] = e["capacity_product"]
            facts.append({"field": key, "label": label, "value": f["value"], "quote": f["quote"],
                          "source": f["source_id"], "locator": f["locator"], **ctx})
        missing = [label for key, label in LABELS.items() if e[key]["value"] in MISSING]
        items.append({
            "id": e["id"], "technology": e["technology_id"], "routes": ROUTES.get(e["technology_id"], []),
            "route_note": ROUTE_NOTES.get(e["technology_id"]),
            "headline": d["headline"], "organization": e["organization"], "date": e["milestone_date"],
            "date_basis": e["milestone_basis"], "evidence_type": e["evidence_type"], "confidence": e["confidence"],
            "what_changed": d["what_changed"], "why_it_matters": d["why_it_matters"], "limitation": d["limitation"],
            "next": e["next_milestone"], "uncertainty": e["uncertainty"], "scores": d["scores"],
            "facts": facts, "not_assessed": missing,
        })
    out = {
        "quarter": quarter, "status": spec["issue"]["status"], "version": spec["issue"]["version"],
        "review": "Evidence-checked research draft: every fact is a verbatim quote from a retained source snapshot. Not yet signed off by a technical reviewer.",
        "items": items, "holds": HOLDS,
        "sources": [{k: s[k] for k in ("id", "title", "url", "doi", "published", "version_date", "kind", "access")}
                    for sid, s in sources.items() if sid in used],
    }
    path = DATA / "quarters" / f"{quarter}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    return path
