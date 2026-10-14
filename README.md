# BIOGLUE Intelligence

[![CI](https://github.com/rethinksci-gif/bioglue-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/rethinksci-gif/bioglue-intelligence/actions/workflows/ci.yml)
[![Site](https://img.shields.io/badge/site-live-2f6b4f)](https://rethinksci-gif.github.io/bioglue-intelligence/)
[![Content: CC BY 4.0](https://img.shields.io/badge/content-CC%20BY%204.0-lightgrey)](LICENSE-CONTENT.md)
[![Code: MIT](https://img.shields.io/badge/code-MIT-lightgrey)](LICENSE)

An open knowledge base and quarterly tracker for **bio-based and formaldehyde-free wood adhesives**: lignin, proteins, tannins, carbohydrates, polycarboxylic acids, renewable crosslinkers, NIPU and bio-based acrylics.

**→ https://rethinksci-gif.github.io/bioglue-intelligence/**

| Section | What you find |
|---|---|
| [Technology routes](https://rethinksci-gif.github.io/bioglue-intelligence/routes/) | Overview, bonding chemistry, structures, maturity, incumbent, challenges and a per-quarter track for each of 8 routes |
| [Chemistry](https://rethinksci-gif.github.io/bioglue-intelligence/chemistry/) | 21 representative molecules drawn from SMILES with RDKit (InChIKey-checked) |
| [Challenges](https://rethinksci-gif.github.io/bioglue-intelligence/challenges/) | Water resistance, press time, rheology, emissions, renewable accounting, cost, LCA, each with the question to ask |
| [Quarterly tracker](https://rethinksci-gif.github.io/bioglue-intelligence/tracker/) | Route × quarter matrix for 2026, with evidence-checked items and machine-triaged leads |
| [Literature](https://rethinksci-gif.github.io/bioglue-intelligence/references/) | Crossref-verified reviews and key papers; BibTeX export |
| [Open data](https://rethinksci-gif.github.io/bioglue-intelligence/data/) | JSON for everything on the site |

## Evidence levels

1. **Machine-triaged lead.** A Crossref or Google News record screened by **DeepSeek flash**. The code keeps the model's summary only if its quote appears verbatim in the title or abstract.
2. **Evidence-checked.** Every fact is a verbatim quote with a locator from a retained primary-source snapshot. Supplier claims and announced capacity are labelled as such.
3. **Technically reviewed.** Signed off by a named reviewer. No quarter has reached this level yet.

## How it works

```
data/*.yaml ──────────────┐
data/quarters/*.json ─────┼─► site/ (Astro + Pagefind) ─► GitHub Pages
data/candidates/*.json ◄──┘
        ▲
        └── scanner/ (monthly GitHub Action)
              Crossref + Google News ─► DeepSeek flash triage ─► code checks
```

- `scanner/`: discovery, triage and data builds (`python -m scanner {scan,structures,import-newsletter,verify-refs}`).
- `.github/workflows/scan.yml`: runs on the 1st of each month, commits new leads and redeploys the site. Requires the `DEEPSEEK_API_KEY` repository secret. Optional repository variables: `DEEPSEEK_MODEL` (default `deepseek-flash`) and `MAX_LLM_CALLS_PER_RUN` (default 80).
- `.github/workflows/ci.yml`: tests, structure rendering, site build and Crossref DOI verification.

A full quarter scan of about 360 discovery records used 45 flash calls.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Submit leads or corrections through the issue templates. Cite the knowledge base with [CITATION.cff](CITATION.cff).

*Not technical, safety or regulatory advice. Check the original standards and sources before acting.*
