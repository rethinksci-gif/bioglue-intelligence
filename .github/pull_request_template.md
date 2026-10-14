## What this changes

## Checklist
- [ ] New references have a DOI that resolves on Crossref (`python -m scanner verify-refs`)
- [ ] New molecules have a SMILES (and an InChIKey if stereochemistry matters)
- [ ] Facts in `data/quarters/` are verbatim quotes from a retained source
- [ ] `pytest -q` and `npm run build` (in `site/`) pass
