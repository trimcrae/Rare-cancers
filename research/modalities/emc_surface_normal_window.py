#!/usr/bin/env python3
"""
Normal-tissue therapeutic-window analysis for the EMC surface-antigen shortlist.

WHY (the crux of a surface-target paper). A surface antigen is only a usable ADC/CAR/TCE/RLT target if
it is expressed on the tumour but **restricted in normal tissue** — otherwise on-target/off-tumour
toxicity kills the therapeutic window. The surfaceome scan (emc_surfaceome_scan.py) ranks antigens by
EMC-*surrogate* tumour expression and selectivity vs other *cancer* lineages; it does NOT look at normal
tissue. This script adds the missing, decisive axis: for each shortlisted antigen, the **Human Protein
Atlas** RNA tissue specificity / distribution / per-tissue expression + subcellular location, classified
into a therapeutic-window verdict (tumour-restricted vs broadly expressed in vital normal tissue).

POSITIVE CONTROLS (self-validation). DLL3 and GPC3 are textbook *tumour-restricted* onco-fetal surface
antigens (approved/clinical ADC/TCE targets) and must classify as RESTRICTED; a housekeeping-broad
membrane gene (B2M) must classify as BROAD. If these don't fall out, distrust the classification.

HONEST BOUNDS. HPA RNA is a *normal-tissue* atlas (bulk); protein-level surface density and lesion-level
heterogeneity differ. 'Restricted' here is a window *prior*, not a safety guarantee. This analysis is
antigen-generic (not EMC-tumour-specific) — it characterises the antigen's normal-tissue liability, which
is exactly what pairs with the EMC-tumour expression from the scan.

Internet required (HPA) -> runs in CI. Output: emc-surface-normal-window.json
"""
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "emc-surface-normal-window.json")

# Shortlist (surfaceome-scan winners + actionable comparators) + controls, with Ensembl IDs for reliable
# HPA lookup. Controls: DLL3/GPC3 should be RESTRICTED; B2M should be BROAD.
GENES = {
    "CDH11": "ENSG00000140937", "FGFR1": "ENSG00000077782", "GPC2": "ENSG00000213420",
    "PTK7": "ENSG00000112655", "MCAM": "ENSG00000076706", "EPHB4": "ENSG00000196411",
    "CD276": "ENSG00000103855", "NCAM1": "ENSG00000149294", "FAP": "ENSG00000078098",
    "ERBB2": "ENSG00000141736", "EGFR": "ENSG00000146648", "KIT": "ENSG00000157404",
    # positive controls (tumour-restricted) + negative control (broad)
    "DLL3": "ENSG00000090932", "GPC3": "ENSG00000147257", "B2M": "ENSG00000166710",
}
CONTROLS_RESTRICTED = {"DLL3", "GPC3"}
CONTROLS_BROAD = {"B2M"}

# Normal tissues whose expression is the highest-consequence on-target/off-tumour risk.
VITAL_TISSUES = ["heart", "cerebral cortex", "brain", "cerebellum", "liver", "lung", "kidney",
                 "pancreas", "colon", "small intestine", "bone marrow"]


def _get_json(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0",
                                               "Accept": "application/json"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url[:70]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return None


def _field(rec, *keys):
    for k in keys:
        if k in rec and rec[k] not in (None, ""):
            return rec[k]
    return None


def classify(spec, dist, specific_tpm):
    """Therapeutic-window verdict from HPA tissue specificity/distribution + which tissues."""
    spec_l = (spec or "").lower()
    dist_l = (dist or "").lower()
    tpm_l = json.dumps(specific_tpm).lower() if specific_tpm else ""
    vital_hits = [t for t in VITAL_TISSUES if t in tpm_l]
    if "low tissue specificity" in spec_l or "detected in all" in dist_l:
        window = "BROAD_LIABILITY"
    elif any(w in spec_l for w in ("tissue enriched", "group enriched", "tissue enhanced")):
        window = "RESTRICTED" if not vital_hits else "RESTRICTED_BUT_VITAL_TISSUE"
    elif "detected in many" in dist_l:
        window = "INTERMEDIATE"
    else:
        window = "INTERMEDIATE"
    return {"window": window, "vital_tissue_expression": vital_hits}


def main():
    out = {}
    for g, ensg in GENES.items():
        url = (f"https://www.proteinatlas.org/api/search_download.php?"
               f"search={ensg}&format=json&compress=no&"
               f"columns=g,eg,rnats,rnatd,rnatss,scl,rnacs,rnacss")
        data = _get_json(url)
        rec = data[0] if isinstance(data, list) and data else None
        if not rec:
            out[g] = {"ensembl": ensg, "_status": "no HPA record"}
            time.sleep(0.3)
            continue
        spec = _field(rec, "RNA tissue specificity", "rnats")
        dist = _field(rec, "RNA tissue distribution", "rnatd")
        specific_tpm = _field(rec, "RNA tissue specific nTPM", "rnatss")
        subcell = _field(rec, "Subcellular location", "scl")
        cancer_spec = _field(rec, "RNA cancer specificity", "rnacs")
        cancer_tpm = _field(rec, "RNA cancer specific nTPM", "rnacss")
        verdict = classify(spec, dist, specific_tpm)
        out[g] = {
            "ensembl": ensg,
            "rna_tissue_specificity": spec,
            "rna_tissue_distribution": dist,
            "rna_tissue_specific_nTPM": specific_tpm,
            "subcellular_location": subcell,
            "plasma_membrane_confirmed": bool(subcell and "plasma membrane" in str(subcell).lower()),
            "rna_cancer_specificity": cancer_spec,
            "rna_cancer_specific_nTPM": cancer_tpm,
            **verdict,
        }
        print(f"  {g}: {verdict['window']} (spec={spec})", file=sys.stderr)
        time.sleep(0.3)

    # self-validation
    val = {
        "positive_controls_restricted": {c: out.get(c, {}).get("window") for c in CONTROLS_RESTRICTED},
        "negative_control_broad": {c: out.get(c, {}).get("window") for c in CONTROLS_BROAD},
        "_pass": ("DLL3/GPC3 should be RESTRICTED* and B2M BROAD_LIABILITY; if so the window "
                  "classification is trustworthy"),
    }
    restricted = [g for g, v in out.items()
                  if g not in CONTROLS_RESTRICTED | CONTROLS_BROAD
                  and v.get("window", "").startswith("RESTRICTED")]
    broad = [g for g, v in out.items()
             if g not in CONTROLS_RESTRICTED | CONTROLS_BROAD and v.get("window") == "BROAD_LIABILITY"]
    result = {
        "_note": ("Normal-tissue therapeutic-window analysis (Human Protein Atlas RNA) for the EMC "
                  "surface-antigen shortlist. RESTRICTED = tumour-restricted window prior (good target); "
                  "BROAD_LIABILITY = broadly expressed in normal tissue (on-target/off-tumour risk). "
                  "Pairs with EMC-tumour expression from emc_surfaceome_scan.py. HPA RNA is bulk "
                  "normal tissue; a window PRIOR, not a safety guarantee."),
        "source": "Human Protein Atlas (proteinatlas.org) RNA tissue + subcellular + cancer specificity",
        "vital_tissues_flagged": VITAL_TISSUES,
        "self_validation": val,
        "restricted_window_candidates": restricted,
        "broad_liability": broad,
        "antigens": out,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({"restricted": restricted, "broad": broad, "validation": val}, indent=2))


if __name__ == "__main__":
    main()
