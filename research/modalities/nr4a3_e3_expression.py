#!/usr/bin/env python3
"""
Are the VHL and CRBN E3-ligase machineries available where EMC arises? (degrader-completeness, ledger E6;
informs the VHL-vs-CRBN recruiter choice — reviewer mandatory-change 5). CPU/DB only.

WHY. A degrader can only work in a cell that expresses the full CRL machinery it recruits. Our matrix keeps
BOTH ligase arms in scope (VHL and CRBN), so we check BOTH:
  - CRL2^VHL  : VHL (substrate receptor) + Elongin B (ELOB) + Elongin C (ELOC) + CUL2 + RBX1
  - CRL4^CRBN : CRBN (substrate receptor) + DDB1 + CUL4A/CUL4B + RBX1
If any component of an arm were tissue-restricted or absent from soft-tissue/mesenchymal contexts, a degrader
built on that arm would be dead on arrival regardless of a good ternary. This checks each machinery's
tissue-expression breadth (Human Protein Atlas) so the degrader premise is grounded, not assumed, AND so the
VHL-vs-CRBN choice is informed by where each arm's machinery is actually available. Runs in CI (internet;
proteinatlas.org is egress-blocked from the dev sandbox). Output: nr4a-e3-expression.json.

HONEST LIMITS. No EMC cell line is in HPA, so this is machinery-availability across general tissue (incl.
soft-tissue/mesenchymal), NOT EMC-specific proof. These are housekeeping-class ligase components; a tissue
restriction would be the surprise to catch. RNA tissue distribution ("detected in all/many") is a breadth
proxy, not an abundance or activity measurement.
"""

import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a-e3-expression.json")

# The two CRL arms our degrader matrix keeps in scope. Each = substrate receptor + the scaffold it assembles
# on to ubiquitinate the target. RBX1 (the RING box that recruits the E2) is shared by both cullin arms.
MACHINERIES = {
    "CRL2_VHL": {
        "_label": "CRL2^VHL (VHL recruiter arm)",
        "genes": {
            "VHL": "ENSG00000134086",     # substrate receptor the PROTAC recruits
            "ELOB": "ENSG00000103363",    # Elongin B (TCEB2) — adaptor
            "ELOC": "ENSG00000154582",    # Elongin C (TCEB1) — adaptor
            "CUL2": "ENSG00000108094",    # cullin scaffold
            "RBX1": "ENSG00000100387",    # RING box (E2 recruitment; shared with CRL4)
        },
    },
    "CRL4_CRBN": {
        "_label": "CRL4^CRBN (CRBN recruiter arm)",
        "genes": {
            "CRBN": "ENSG00000113851",    # substrate receptor the PROTAC recruits
            "DDB1": "ENSG00000167986",    # adaptor
            "CUL4A": "ENSG00000139842",   # cullin scaffold
            "CUL4B": "ENSG00000158290",   # cullin scaffold (paralogue)
            "RBX1": "ENSG00000100387",    # RING box (E2 recruitment; shared with CRL2)
        },
    },
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


def score_machinery(genes):
    rows = {g: hpa_expression(g, e) for g, e in genes.items()}
    have = [r for r in rows.values() if "rna_tissue_distribution" in r]
    all_broad = bool(have) and all(r.get("broadly_expressed") for r in have)
    complete = len(have) == len(genes)
    not_broad = [r["gene"] for r in have if not r.get("broadly_expressed")]
    return rows, {"all_broadly_expressed": all_broad, "record_complete": complete,
                  "components_not_broadly_expressed": not_broad}


def main():
    arms = {}
    for key, spec in MACHINERIES.items():
        rows, summary = score_machinery(spec["genes"])
        arms[key] = {"_label": spec["_label"], "components": rows, **summary}

    vhl_ok = arms["CRL2_VHL"]["all_broadly_expressed"]
    crbn_ok = arms["CRL4_CRBN"]["all_broadly_expressed"]
    if vhl_ok and crbn_ok:
        verdict = ("Both CRL2^VHL and CRL4^CRBN machineries broadly expressed — both recruiter arms are "
                   "grounded; the VHL-vs-CRBN choice is NOT constrained by machinery availability and should "
                   "be made on ternary/geometry/selectivity grounds.")
    elif vhl_ok or crbn_ok:
        avail, missing = ("VHL", "CRBN") if vhl_ok else ("CRBN", "VHL")
        verdict = (f"Only the {avail} arm's machinery is broadly expressed; the {missing} arm has "
                   f"components flagged not-broadly-expressed — prefer the {avail} recruiter, and re-check "
                   f"the flagged {missing} component(s) before committing to that arm.")
    else:
        verdict = ("Neither arm is cleanly broadly-expressed on this proxy — inspect the flagged components; "
                   "do not read machinery availability as settled either way.")

    result = {
        "_title": "CRL2^VHL vs CRL4^CRBN E3-machinery tissue expression (degrader-completeness E6; ligase-choice input)",
        "_note": "A degrader needs its full CRL arm (substrate receptor + adaptor(s) + cullin + RBX1) "
                 "co-expressed in the target cell. Both arms broadly expressed => machinery is available in "
                 "soft-tissue/mesenchymal contexts and neither arm is dead-on-arrival on availability grounds. "
                 "No EMC line is in HPA, so this is machinery-availability in general tissue, not EMC-specific "
                 "proof; RNA tissue distribution is a breadth proxy, not abundance/activity.",
        "source": "Human Protein Atlas (proteinatlas.org)",
        "arms": arms,
        "both_arms_broadly_expressed": bool(vhl_ok and crbn_ok),
        "verdict": verdict,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    for key, arm in arms.items():
        print(f"\n{arm['_label']}  all_broad={arm['all_broadly_expressed']} "
              f"complete={arm['record_complete']} not_broad={arm['components_not_broadly_expressed']}")
        for g, r in arm["components"].items():
            print(f"  {g:6s} dist={r.get('rna_tissue_distribution')!r} broad={r.get('broadly_expressed')}")
    print("\nverdict:", verdict)


if __name__ == "__main__":
    main()
