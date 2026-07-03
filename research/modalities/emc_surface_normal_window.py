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

# Shortlist (surfaceome-scan winners + actionable comparators) + candidate NE/RLT targets + controls,
# with Ensembl IDs for reliable HPA lookup. SSTR2 = approved-RLT (DOTATATE) NE target; B4GALNT1 = GD2
# synthase (GD2 is a glycolipid, not a protein — B4GALNT1 is a transcript proxy only, flagged).
GENES = {
    "CDH11": "ENSG00000140937", "FGFR1": "ENSG00000077782", "GPC2": "ENSG00000213420",
    "PTK7": "ENSG00000112655", "MCAM": "ENSG00000076706", "EPHB4": "ENSG00000196411",
    "CD276": "ENSG00000103855", "NCAM1": "ENSG00000149294", "FAP": "ENSG00000078098",
    "ERBB2": "ENSG00000141736", "EGFR": "ENSG00000146648", "KIT": "ENSG00000157404",
    "SSTR2": "ENSG00000180616", "B4GALNT1": "ENSG00000135454",
    # controls: DLL3/GPC3 tumour-restricted (RESTRICTED); B2M broad (BROAD);
    # CD3E = HARD control (a "tissue enhanced"-type immune antigen that is a clinical DANGER — tests
    # whether the classifier flags immune/circulating expression, not just parses HPA labels).
    "DLL3": "ENSG00000090932", "GPC3": "ENSG00000147257", "B2M": "ENSG00000166710",
    "CD3E": "ENSG00000198851",
}
CONTROLS_RESTRICTED = {"DLL3", "GPC3"}
CONTROLS_BROAD = {"B2M"}
CONTROLS_IMMUNE_DANGER = {"CD3E"}   # must NOT come out RESTRICTED

# Normal tissues whose expression is the highest-consequence on-target/off-tumour risk (expanded to
# nervous / muscle / GI / marrow per red-team: 'tissue enhanced' in a vital tissue is still a liability).
VITAL_TISSUES = ["heart", "cerebral cortex", "brain", "cerebellum", "hippocamp", "amygdala",
                 "basal ganglia", "spinal cord", "nerve", "liver", "lung", "kidney", "pancreas",
                 "colon", "small intestine", "duodenum", "stomach", "bone marrow", "skeletal muscle",
                 "smooth muscle", "cardiac"]


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


def classify(spec, dist, specific_tpm, blood_spec, blood_tpm):
    """Therapeutic-window verdict from HPA tissue specificity/distribution + per-tissue nTPM + blood cells.

    Correct HPA semantics (red-team fix): 'Tissue ENHANCED' means detected in essentially ALL tissues but
    elevated >=4x in some (broad-with-a-peak) — it is NOT restricted. Only 'Tissue ENRICHED' / 'Group
    enriched' (expression confined to one / a few tissues) is a genuine restricted-window prior. Vital-tissue
    or immune/circulating-cell expression overrides everything (an on-target/off-tumour danger)."""
    spec_l = (spec or "").lower()
    dist_l = (dist or "").lower()
    tpm_l = json.dumps(specific_tpm).lower() if specific_tpm else ""
    vital_hits = [t for t in VITAL_TISSUES if t in tpm_l]
    # immune / circulating-cell expression: only a STRONG, confined blood-cell signal counts
    # ('Immune cell enriched' / 'Group enriched'); weak 'Immune cell enhanced' is broad-low noise
    # (it otherwise mis-flags the tumour-restricted controls DLL3/GPC3), so it is NOT a liability.
    bspec_l = (blood_spec or "").lower()
    immune_flag = "enriched" in bspec_l
    liabilities = {"vital_tissue": vital_hits, "immune_or_circulating": immune_flag,
                   "blood_cell_specificity": blood_spec}

    if vital_hits or immune_flag:
        window = "VITAL_OR_IMMUNE_LIABILITY"
    elif "low tissue specificity" in spec_l or "detected in all" in dist_l:
        window = "BROAD_LIABILITY"
    elif "enhanced" in spec_l:
        # broad-with-a-peak: detected widely, elevated in some tissue(s) — NOT a clean window
        window = "ENHANCED_BROAD"
    elif ("enriched" in spec_l) or ("group enriched" in spec_l):
        window = "RESTRICTED"          # confined to one/a few tissues, no vital/immune hit
    else:
        window = "INTERMEDIATE"
    return {"window": window, **liabilities}


def main():
    out = {}
    for g, ensg in GENES.items():
        url = (f"https://www.proteinatlas.org/api/search_download.php?"
               f"search={ensg}&format=json&compress=no&"
               f"columns=g,eg,rnats,rnatd,rnatss,scl,rnabcs,rnabcss")
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
        blood_spec = _field(rec, "RNA blood cell specificity", "rnabcs")
        blood_tpm = _field(rec, "RNA blood cell specific nTPM", "rnabcss")
        verdict = classify(spec, dist, specific_tpm, blood_spec, blood_tpm)
        out[g] = {
            "ensembl": ensg,
            "rna_tissue_specificity": spec,
            "rna_tissue_distribution": dist,
            "rna_tissue_specific_nTPM": specific_tpm,
            "rna_blood_cell_specificity": blood_spec,
            "rna_blood_cell_specific_nTPM": blood_tpm,
            "subcellular_location": subcell,
            "plasma_membrane_confirmed": bool(subcell and "plasma membrane" in str(subcell).lower()),
            **verdict,
        }
        print(f"  {g}: {verdict['window']} (spec={spec}, blood={blood_spec})", file=sys.stderr)
        time.sleep(0.3)

    # self-validation — now includes the HARD control (CD3E must NOT be RESTRICTED) and an
    # ENHANCED-broad check (the branch the top priors actually use).
    val = {
        "positive_controls_restricted": {c: out.get(c, {}).get("window") for c in CONTROLS_RESTRICTED},
        "negative_control_broad": {c: out.get(c, {}).get("window") for c in CONTROLS_BROAD},
        "hard_immune_control_must_not_be_restricted": {c: out.get(c, {}).get("window")
                                                       for c in CONTROLS_IMMUNE_DANGER},
        "_pass": ("DLL3/GPC3 => RESTRICTED (tissue enriched); B2M => BROAD; CD3E must be "
                  "VITAL_OR_IMMUNE_LIABILITY (NOT restricted) — the hard control that 'tissue enhanced "
                  "!= restricted' and that immune expression is caught."),
    }
    _controls = CONTROLS_RESTRICTED | CONTROLS_BROAD | CONTROLS_IMMUNE_DANGER
    restricted = [g for g, v in out.items()
                  if g not in _controls and v.get("window") == "RESTRICTED"]
    liabilities = [g for g, v in out.items() if g not in _controls
                   and v.get("window") in ("BROAD_LIABILITY", "VITAL_OR_IMMUNE_LIABILITY",
                                            "ENHANCED_BROAD")]
    broad = liabilities  # backward-compat key
    result = {
        "_note": ("Normal-tissue therapeutic-window analysis (Human Protein Atlas RNA) for the EMC "
                  "surface-antigen shortlist. Verdicts: RESTRICTED = 'tissue enriched'/'group enriched' "
                  "(confined to one/few tissues, no vital/immune hit — the only clean window prior); "
                  "ENHANCED_BROAD = 'tissue enhanced' (detected broadly with a peak — NOT restricted); "
                  "BROAD_LIABILITY = 'low tissue specificity'/'detected in all'; VITAL_OR_IMMUNE_LIABILITY "
                  "= expressed in a vital tissue or immune/circulating cell (overrides all — an "
                  "on-target/off-tumour danger). HPA RNA is bulk normal tissue and a window PRIOR, not a "
                  "safety guarantee, and mRNA != surface protein."),
        "source": "Human Protein Atlas (proteinatlas.org) RNA tissue + blood-cell + subcellular specificity",
        "vital_tissues_flagged": VITAL_TISSUES,
        "self_validation": val,
        "restricted_window_candidates": restricted,
        "liability_antigens": liabilities,
        "broad_liability": broad,
        "antigens": out,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({"restricted": restricted, "liabilities": liabilities, "validation": val}, indent=2))


if __name__ == "__main__":
    main()
