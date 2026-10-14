# Contributing

Thanks for helping keep this knowledge base accurate.

## Quick ways to help
- **Submit a lead**: [open a lead issue](../../issues/new?template=lead.yml) with the primary source.
- **Report a correction**: [open a correction issue](../../issues/new?template=correction.yml) with a supporting passage.

## Editing content
All site content is plain YAML/JSON under `data/`:

| File | What it holds |
|---|---|
| `routes.yaml` | Technology routes: overview, chemistry, applications, incumbent, maturity, challenges, scan queries |
| `structures.yaml` | Molecules (SMILES, optional InChIKey check, role, routes) |
| `challenges.yaml` | Cross-cutting challenges and the question to ask |
| `references.yaml` | Literature; every entry needs a DOI that resolves on Crossref |
| `glossary.yaml` | Terms, labels, standards |
| `quarters/*.json` | Evidence-checked items, exported from the research workspace — do not hand-edit |
| `candidates/*.json` | Machine-triaged leads written by the scanner — do not hand-edit |

## Evidence rules
1. Facts must be verbatim quotes from a primary source with a locator.
2. Keep supplier claims, announced capacity and laboratory results labelled as what they are.
3. No invented chemical structures: polymers are shown by a representative unit.
4. Missing data is written as missing, never filled with estimates.

## Local setup
```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev,structures]'
.venv/bin/pytest -q
.venv/bin/python -m scanner structures
cd site && npm ci && npm run dev
```
Running a scan needs `DEEPSEEK_API_KEY` in your environment: `python -m scanner scan --quarter 2026-Q4 --max-calls 20`.
