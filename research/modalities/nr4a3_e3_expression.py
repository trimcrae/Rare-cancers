#!/usr/bin/env python3
"""
Is the CRBN E3-ligase machinery available where EMC arises? (degrader-completeness, ledger E6). CPU/DB only.

WHY. A CRBN-recruiting degrader can only work in a cell that expresses the CRL4^CRBN machinery — CRBN itself
plus the scaffold it assembles on (DDB1, CUL4A/CUL4B, RBX1). If any were tissue-restricted or absent from
soft-tissue/mesenchymal contexts, the degrader would be dead on arrival regardless of a good ternary. This
checks the machinery's tissue-expression breadth (Human Protein Atlas), so the degrader premise is grounded,
not assumed. Runs in CI (internet). Output: nr4a-e3-expression.json.
"""

import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a-e3-expression.json")

# CRL4^CRBN machinery: the substrate receptor + the ligase scaffold it needs to ubiquitinate the target.
E3_MACHINERY = {
    "CRBN": "ENSG00000113851",     # substrate receptor the PROTAC recruits
    "DDB1": "ENSG00000167986",     # adaptor
    "CUL4A": "ENSG00000139842",    # cullin scaffold
    "CUL4B": "ENSG00000158290",    # cullin scaffold (paralogue)
    "RBX1": "ENSG00000100387",     # RING box (E2 recruitment)
}


def _get_json(url, timeout=60):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0",
                                                       "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i+1} {url[:70]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return None


def hpa_expression(gene, ensg):
    url = (f"https://www.proteinatlas.org/api/search_download.php?"
           f"search={ensg}&format=json&columns=g,gs,rnats,rnatd&compress=no")
    data = _get_json(url)
    rec = data[0] if isinstance(data, list) and data else None
    if not rec:
        return {"gene": gene, "ensembl": ensg, "_status": "no HPA record"}
    spec = rec.get("RNA tissue specificity") or rec.get("rnats")
    dist = rec.get("RNA tissue distribution") or rec.get("rnatd")
    broadly = isinstance(dist, str) and ("all" in dist.lower() or "many" in dist.lower())
    return {"gene": gene, "ensembl": ensg, "rna_tissue_specificity": spec,
            "rna_tissue_distribution": dist, "broadly_expressed": broadly}


def main():
    rows = {g: hpa_expression(g, e) for g, e in E3_MACHINERY.items()}
    all_broad = all(r.get("broadly_expressed") for r in rows.values())
    result = {
        "_title": "CRL4^CRBN E3-machinery tissue expression (degrader-completeness, ledger E6)",
        "_note": "A CRBN PROTAC needs CRBN + DDB1 + CUL4A/B + RBX1 co-expressed in the target cell. All "
                 "broadly ('detected in all/many') => the machinery is available in soft-tissue/mesenchymal "
                 "contexts and the degrader premise is grounded. These are housekeeping-class ligase "
                 "components; a tissue restriction would be the surprise to catch. No EMC line is in HPA, so "
                 "this is machinery-availability in general tissue, not EMC-specific proof.",
        "source": "Human Protein Atlas (proteinatlas.org)",
        "machinery": rows,
        "all_broadly_expressed": all_broad,
        "verdict": ("CRBN machinery broadly expressed — degrader premise grounded" if all_broad
                    else "check components flagged not-broadly-expressed"),
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({g: {"dist": r.get("rna_tissue_distribution"),
                          "broad": r.get("broadly_expressed")} for g, r in rows.items()}, indent=2))
    print("all broadly expressed:", all_broad)


if __name__ == "__main__":
    main()
