# Roadmap and improvement ideas

Patterns borrowed from well-run open knowledge repositories:

| Pattern | Seen in | Status here |
|---|---|---|
| Plain-text data as the single source of truth, site generated from it | [owid/etl](https://github.com/owid/etl), [protontypes/open-sustainable-technology](https://github.com/protontypes/open-sustainable-technology) | Done: `data/*.yaml` → Astro |
| Strict entry format plus CI validation | [sindresorhus/awesome](https://github.com/sindresorhus/awesome) (awesome-lint) | Done: pytest cross-references, InChIKey and Crossref DOI checks |
| Issue forms for contributions, contributor guide, citation file | [the-turing-way/the-turing-way](https://github.com/the-turing-way/the-turing-way) | Done: lead and correction forms, CONTRIBUTING, CITATION.cff |
| Open data downloads with licences | owid | Done: `/data/*.json`, BibTeX, CC BY 4.0 |
| Changelog and versioned releases with DOIs | many research repos (Zenodo integration) | Next |

## Next (high value, low effort)

1. **Zenodo DOI per quarterly release.** Tag `2026-Q3` once it is reviewed and let the Zenodo GitHub integration mint a citable DOI.
2. **Lead-to-evidence workflow.** Add a `promote` label on a lead issue that opens a pull request with a source snapshot stub and an extraction mapping. The existing evidence rules then gate it.
3. **Per-route RSS and change history.** Add a feed per route, plus a "what changed since last quarter" diff generated from `data/quarters/`.
4. **Benchmark tables with matched conditions.** Compare values only when product, test standard, pretreatment and comparator match (for example EN 314 class 1 plywood), and mark everything else "not comparable".
5. **Better coverage.** Add publisher journal RSS (Holzforschung, Eur. J. Wood Wood Prod., Int. J. Adhes. Adhes.), patent families (Lens.org or EPO OPS), and Chinese- and Portuguese-language trade press. Measure recall against a hand-built reference set each quarter.

## Later

- Interactive route × property radar (wet strength, press factor, cost, maturity), but only from evidence-checked values.
- Supplier and pilot-plant map with announced and actual capacity kept separate.
- Zotero group library synced to `references.yaml`.
- Optional DeepSeek-flash first-pass extraction of candidate facts. Code would still check every quote, and a human would approve before anything enters `data/quarters/`.

## Non-goals

- Automatic publication of unreviewed claims as evidence.
- Rankings that combine results measured under different conditions.
