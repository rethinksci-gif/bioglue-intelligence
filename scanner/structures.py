"""Render data/structures.yaml to theme-aware SVGs with RDKit (build-time only)."""
from __future__ import annotations

import re

from .config import DATA, ROOT, load

OUT = ROOT / "site" / "src" / "generated" / "structures"


def render() -> list[str]:
    from rdkit import Chem
    from rdkit.Chem.Draw import rdMolDraw2D

    OUT.mkdir(parents=True, exist_ok=True)
    done = []
    for m in load("structures"):
        mol = Chem.MolFromSmiles(m["smiles"])
        if mol is None:
            raise ValueError(f"{m['id']}: invalid SMILES")
        if m.get("inchikey") and Chem.MolToInchiKey(mol) != m["inchikey"]:
            raise ValueError(f"{m['id']}: InChIKey mismatch (stereochemistry changed?)")
        d = rdMolDraw2D.MolDraw2DSVG(320, 220)
        opts = d.drawOptions()
        opts.clearBackground = False
        opts.bondLineWidth = 2
        opts.padding = 0.12
        opts.fixedBondLength = 40  # same scale for every molecule
        opts.addStereoAnnotation = False
        d.DrawMolecule(mol)
        d.FinishDrawing()
        svg = d.GetDrawingText()
        svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
        svg = svg.replace("#000000", "currentColor").replace("#FFFFFF", "none")
        # Heteroatom colours that stay legible in both themes.
        svg = svg.replace("#FF0000", "var(--atom-o)").replace("#0000FF", "var(--atom-n)").replace("#00CC00", "var(--atom-cl)")
        svg = svg.replace("<svg ", f'<svg role="img" aria-label="{m["name"]} structure" ', 1)
        (OUT / f"{m['id']}.svg").write_text(svg)
        done.append(m["id"])
    return done
