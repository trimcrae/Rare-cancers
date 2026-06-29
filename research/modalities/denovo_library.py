#!/usr/bin/env python3
"""Pure selection of the top de-novo candidates to push into the dock + MM-GBSA selectivity funnel.

The de-novo generation (nr4a3_denovo.py) emits nr4a3-denovo.json with a ranked `candidates` list (each
carrying smiles + denovo_promise + handle_contacts). The funnel (the matrix in candidate mode) only needs
the best few as a docking library. This is the pure picker — no RDKit/IO — so it is unit-tested directly.
"""


def top_candidates(denovo, top_n=20):
    """From a loaded nr4a3-denovo.json dict, return up to top_n VALID candidates as (label, id, smiles),
    ranked by denovo_promise (desc), deduplicated by SMILES. Skips invalid generations (promise None /
    error / no smiles). label and id are both the generation name (e.g. 'denovo_189') so downstream
    docking keys (which use the label) stay stable."""
    cands = [c for c in denovo.get("candidates", [])
             if c.get("denovo_promise") is not None and c.get("smiles") and "error" not in c]
    cands.sort(key=lambda c: (c["denovo_promise"], c.get("name", "")), reverse=True)
    out, seen = [], set()
    for c in cands:
        smi = c["smiles"]
        if smi in seen:
            continue
        seen.add(smi)
        name = c.get("name") or f"cand_{len(out)}"
        out.append((name, name, smi))
        if len(out) >= top_n:
            break
    return out
