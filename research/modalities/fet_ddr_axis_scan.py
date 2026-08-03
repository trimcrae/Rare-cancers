#!/usr/bin/env python3
"""
Is the ATR axis a SELECTIVE dependency of FET-fusion sarcomas — and is the ATM axis correspondingly
DISPENSABLE in them? A DepMap transfer prior for EMC.

WHY THIS EXISTS
---------------
Gorthi/Bailey and successors report that FET fusion oncoproteins (EWSR1::FLI1 and, explicitly,
EWSR1::ATF1 in clear cell sarcoma) impair ATM activation at double-strand breaks, leaving the
compensatory ATR axis load-bearing -> ATR inhibitors are synthetic lethal in FET-rearranged cancers
("FET fusion oncoproteins disrupt physiologic DNA repair and create a targetable opportunity for
ATR inhibitor therapy", biorxiv 2023.04.30.538578 / Cancer Res). EMC's three commonest 5' partners
- EWSR1, TAF15, FUS - are the three FET-family genes, so EMC is a FET-rearranged cancer by
construction. That makes ATR inhibition a CLASS hypothesis EMC inherits, with drugs already in
humans, and it needs no NR4A-paralogue selectivity at all.

THE TEST, AND WHY IT IS A DOUBLE PREDICTION (not one delta)
-----------------------------------------------------------
A single gene delta on one axis is a coin flip dressed up as evidence. The mechanism above predicts
BOTH directions at once, over two multi-gene axes:

    (i)  ATR axis  (ATR, ATRIP, CHEK1, TOPBP1, CLSPN, RPA1/2/3) -> MORE essential in FET lines
    (ii) ATM axis  (ATM, MDC1, NBN, MRE11A, RAD50, TP53BP1)     -> NOT more essential, and
                                                                   plausibly LESS, in FET lines
                                                                   (already functionally suppressed)

Only the conjunction is interesting. Either half alone is consistent with a lineage artefact.

WHAT THIS CANNOT DO - read before quoting any number
----------------------------------------------------
1. **CRISPR knockout is not inhibitor sensitivity.** ATR is a common-essential gene: a full KO
   removes the protein in every line, so Chronos measures "how much does this line mind losing ATR
   entirely", not "how much does this line mind ATR being partly inhibited". A synthetic-lethal
   window that a drug would exploit at sub-lethal occupancy can be invisible here, and a
   common-essential floor compresses exactly the differences we are looking for. This scan can
   therefore SUPPORT the hypothesis or fail to see it; it cannot refute it.
2. **EMC is n<=1 in DepMap** (ACH-001519 / H-EMC-SS, expression-only per this repo's own record).
   The script reports what CRISPR data that model actually has rather than assuming. Every FET
   number below is a transfer prior from OTHER FET sarcomas, never an EMC measurement.
3. **Subtype assignment is string matching on Oncotree labels**, not a fusion call. Lines are
   grouped by disease label; the label is reported with each group so the grouping is auditable.

Output: fet-ddr-axis-scan.json. Internet required (figshare/DepMap) -> runs in CI, not the sandbox.
"""

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fet-ddr-axis-scan.json")

sys.path.insert(0, HERE)
from depmap_sarcoma_dependency import (  # noqa: E402  (shares the release discovery + fetch)
    DEPENDENT_THRESHOLD,
    _download,
    _get,
    discover_depmap_files,
)

# --- the two axes, and what each gene is doing there ---------------------------------------------
ATR_AXIS = ["ATR", "ATRIP", "CHEK1", "TOPBP1", "CLSPN", "RPA1", "RPA2", "RPA3"]
ATM_AXIS = ["ATM", "MDC1", "NBN", "MRE11A", "MRE11", "RAD50", "TP53BP1"]
# Neighbouring DDR nodes that are drugged in the clinic; reported, not part of the double prediction.
OTHER_DDR = ["WEE1", "CHEK2", "PRKDC", "PARP1", "POLQ", "RAD51", "USP1", "PKMYT1"]
# Controls: a pan-essential floor, a known-dispensable gene, and the fusion context genes.
CONTEXT = ["POLR2A", "RPL5", "NR4A3", "EWSR1", "TAF15", "FUS", "FLI1", "ATF1", "DDIT3", "WT1"]

ALL_GENES = sorted(set(ATR_AXIS) | set(ATM_AXIS) | set(OTHER_DDR) | set(CONTEXT))

# FET-rearranged sarcoma subtypes that DepMap actually carries, matched on Oncotree labels.
# Each entry: group label -> (regex-ish substring, the FET fusion it stands for).
FET_SUBTYPES = {
    "Ewing": ("ewing", "EWSR1::FLI1 / EWSR1::ERG"),
    "clear_cell_sarcoma": ("clear cell sarcoma", "EWSR1::ATF1"),
    "myxoid_liposarcoma": ("myxoid", "FUS::DDIT3 / EWSR1::DDIT3"),
    "DSRCT": ("desmoplastic small round", "EWSR1::WT1"),
    "EMC": ("extraskeletal myxoid chondrosarcoma", "EWSR1::NR4A3 (the disease itself)"),
}
# Non-FET sarcoma comparator subtypes (fusion-driven or not, but NOT FET-rearranged).
NON_FET_SARCOMA_SUBTYPES = {
    "synovial": ("synovial", "SS18::SSX"),
    "rhabdomyosarcoma": ("rhabdomyosarcoma", "PAX3::FOXO1 or fusion-negative"),
    "osteosarcoma": ("osteosarcoma", "complex karyotype"),
    "leiomyosarcoma": ("leiomyosarcoma", "complex karyotype"),
    "rhabdoid": ("rhabdoid", "SMARCB1 loss"),
    "chondrosarcoma": ("chondrosarcoma", "IDH1/2 (conventional)"),
}
EMC_MODEL_ID = "ACH-001519"  # H-EMC-SS, per this repo's IDEAS.md correction of 2026-07-03


def _label_col(model):
    for c in ("OncotreeSubtype", "OncotreePrimaryDisease", "lineage"):
        if c in model.columns:
            return c
    return model.columns[-1]


def _ids_matching(model, col, needle):
    hit = model[col].astype(str).str.contains(needle, case=False, na=False)
    return set(model.index[hit])


def _axis_stats(ge, ids, genes, label):
    """Mean gene effect over an axis, per line then averaged, plus the per-gene breakdown."""
    present = [g for g in genes if g in ge.columns]
    rows = ge.reindex([i for i in ge.index if i in ids])[present].dropna(how="all")
    if rows.empty or not present:
        return {"group": label, "n_lines": 0, "_status": "no lines or no genes in release"}
    per_line = rows.mean(axis=1)            # each line's mean over the axis
    per_gene = {g: round(float(rows[g].dropna().mean()), 4) for g in present
                if rows[g].notna().any()}
    return {
        "group": label,
        "n_lines": int(len(per_line)),
        "genes_used": present,
        "axis_mean_gene_effect": round(float(per_line.mean()), 4),
        "axis_sd_across_lines": round(float(per_line.std(ddof=1)), 4) if len(per_line) > 1 else None,
        "frac_lines_dependent_on_axis": round(float((per_line < DEPENDENT_THRESHOLD).mean()), 3),
        "per_gene_mean": per_gene,
    }


def _welch(a, b):
    """Welch t statistic + df for two small samples. No scipy in this lane; report t and df only,
    never a p-value we cannot compute exactly."""
    import math
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    if va == 0 and vb == 0:
        return None
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return None
    t = (ma - mb) / se
    num = (va / na + vb / nb) ** 2
    den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    return {"t": round(t, 3), "df": round(num / den, 1) if den else None,
            "mean_a": round(ma, 4), "mean_b": round(mb, 4),
            "delta_a_minus_b": round(ma - mb, 4)}


def main():
    try:
        import pandas as pd
    except ImportError:
        json.dump({"_status": "pandas missing"}, open(OUT, "w"), indent=2)
        print("pandas missing", file=sys.stderr)
        return 0

    urls = discover_depmap_files()
    release = urls.get("release", "unknown")

    model = pd.read_csv(io.BytesIO(_get(urls["Model.csv"], timeout=180)))
    id_col = "ModelID" if "ModelID" in model.columns else model.columns[0]
    model = model.set_index(id_col)
    lin_col = "OncotreeLineage" if "OncotreeLineage" in model.columns else "lineage"
    lab_col = _label_col(model)

    crispr_path = _download(urls["CRISPRGeneEffect.csv"], timeout=900)
    cols = list(pd.read_csv(crispr_path, nrows=0).columns)
    idx_col = cols[0]
    keep = {c.split(" (")[0]: c for c in cols[1:] if c.split(" (")[0] in set(ALL_GENES)}
    ge = pd.read_csv(crispr_path, usecols=[idx_col] + list(keep.values()), index_col=0)
    ge.columns = [c.split(" (")[0] for c in ge.columns]

    sarcoma_ids = set(model.index[model[lin_col].isin(["Soft Tissue", "Bone"])])

    # ---- group membership, reported so the grouping is auditable ---------------------------------
    fet_groups, fet_ids = {}, set()
    for name, (needle, fusion) in FET_SUBTYPES.items():
        ids = _ids_matching(model, lab_col, needle) & set(ge.index)
        fet_groups[name] = {
            "oncotree_match": needle, "fusion": fusion,
            "n_with_crispr": len(ids),
            "labels_seen": sorted({str(model.loc[i, lab_col]) for i in ids})[:6],
        }
        fet_ids |= ids
    nonfet_groups, nonfet_ids = {}, set()
    for name, (needle, driver) in NON_FET_SARCOMA_SUBTYPES.items():
        ids = (_ids_matching(model, lab_col, needle) & set(ge.index) & sarcoma_ids) - fet_ids
        nonfet_groups[name] = {"oncotree_match": needle, "driver": driver,
                               "n_with_crispr": len(ids)}
        nonfet_ids |= ids
    other_sarcoma_ids = (sarcoma_ids & set(ge.index)) - fet_ids - nonfet_ids
    nonsarcoma_ids = set(ge.index) - sarcoma_ids

    # ---- the EMC line itself: does it have CRISPR data at all? (an open repo question, $0) --------
    emc = {"model_id": EMC_MODEL_ID,
           "in_model_metadata": bool(EMC_MODEL_ID in model.index),
           "has_crispr_gene_effect": bool(EMC_MODEL_ID in ge.index)}
    if emc["in_model_metadata"]:
        emc["oncotree_label"] = str(model.loc[EMC_MODEL_ID, lab_col])
        emc["lineage"] = str(model.loc[EMC_MODEL_ID, lin_col])
    if emc["has_crispr_gene_effect"]:
        emc["atr_axis_mean"] = round(float(ge.loc[EMC_MODEL_ID, [g for g in ATR_AXIS
                                                                if g in ge.columns]].mean()), 4)
        emc["atm_axis_mean"] = round(float(ge.loc[EMC_MODEL_ID, [g for g in ATM_AXIS
                                                                if g in ge.columns]].mean()), 4)

    # ---- the double prediction --------------------------------------------------------------------
    def per_line_axis(ids, genes):
        present = [g for g in genes if g in ge.columns]
        rows = ge.reindex([i for i in ge.index if i in ids])[present].dropna(how="all")
        return [float(v) for v in rows.mean(axis=1).dropna()]

    comparators = {
        "non_FET_sarcoma": nonfet_ids | other_sarcoma_ids,
        "all_non_sarcoma": nonsarcoma_ids,
    }
    axes = {"ATR_axis": ATR_AXIS, "ATM_axis": ATM_AXIS}
    double = {}
    for axis_name, genes in axes.items():
        fet_vals = per_line_axis(fet_ids, genes)
        double[axis_name] = {"FET": _axis_stats(ge, fet_ids, genes, "FET-rearranged sarcoma")}
        for comp_name, comp_ids in comparators.items():
            double[axis_name][comp_name] = _axis_stats(ge, comp_ids, genes, comp_name)
            double[axis_name][f"contrast_FET_vs_{comp_name}"] = _welch(
                fet_vals, per_line_axis(comp_ids, genes))

    # The conjunction, stated so it cannot be read selectively. NEGATIVE delta = more essential
    # in FET lines (gene effect is more negative when the gene is more essential).
    def _delta(axis, comp):
        c = double[axis].get(f"contrast_FET_vs_{comp}")
        return c["delta_a_minus_b"] if c else None

    verdict = {}
    for comp in comparators:
        d_atr, d_atm = _delta("ATR_axis", comp), _delta("ATM_axis", comp)
        if d_atr is None or d_atm is None:
            verdict[comp] = {"tier": "UNREADABLE", "why": "a contrast could not be computed"}
            continue
        atr_more = d_atr < 0
        atm_not_more = d_atm >= 0
        verdict[comp] = {
            "atr_axis_delta_FET_minus_comparator": d_atr,
            "atm_axis_delta_FET_minus_comparator": d_atm,
            "atr_axis_more_essential_in_FET": bool(atr_more),
            "atm_axis_not_more_essential_in_FET": bool(atm_not_more),
            "tier": ("BOTH_HALVES" if (atr_more and atm_not_more)
                     else "ATR_HALF_ONLY" if atr_more
                     else "ATM_HALF_ONLY" if atm_not_more
                     else "NEITHER"),
            "_reading": "BOTH_HALVES is the only tier that supports the mechanism. Any other tier "
                        "is consistent with a lineage artefact and must be reported as one. NOTE "
                        "the ceiling in the module docstring: a common-essential ATR compresses "
                        "exactly this contrast, so a null here is NOT a refutation.",
        }

    other_ddr = {g: {
        "FET_mean": (round(float(ge.reindex([i for i in ge.index if i in fet_ids])[g]
                                 .dropna().mean()), 4) if g in ge.columns else None),
        "non_FET_sarcoma_mean": (round(float(ge.reindex(
            [i for i in ge.index if i in (nonfet_ids | other_sarcoma_ids)])[g]
            .dropna().mean()), 4) if g in ge.columns else None),
    } for g in OTHER_DDR}

    context = {g: (round(float(ge[g].dropna().mean()), 4) if g in ge.columns else None)
               for g in CONTEXT}

    result = {
        "_what": "Does DepMap support the FET-fusion -> ATM-suppression -> ATR-axis-dependency "
                 "mechanism, as a transfer prior for EMC (EWSR1/TAF15/FUS::NR4A3)?",
        "_hypothesis_source": "FET fusion oncoproteins disrupt physiologic DNA repair and create a "
                              "targetable opportunity for ATR inhibitor therapy — biorxiv "
                              "10.1101/2023.04.30.538578 (PMID 37205599); clear cell sarcoma "
                              "(EWSR1::ATF1) is reported to share the FET-dependent ATRi synthetic "
                              "lethality, which is what makes this a CLASS claim EMC can inherit.",
        "_instrument_ceiling": "CRISPR knockout != inhibitor sensitivity. ATR is common-essential, "
                               "so this scan can SUPPORT the hypothesis or miss it; it cannot "
                               "refute it. Read with the module docstring's three limits.",
        "depmap_release": release,
        "n_models_with_crispr": int(ge.shape[0]),
        "genes_found": sorted(ge.columns),
        "genes_requested_but_absent": sorted(set(ALL_GENES) - set(ge.columns)),
        "dependent_threshold": DEPENDENT_THRESHOLD,
        "grouping": {
            "label_column_used": lab_col,
            "FET_rearranged": fet_groups,
            "n_FET_lines_total": len(fet_ids),
            "non_FET_sarcoma": nonfet_groups,
            "n_other_sarcoma_unclassified": len(other_sarcoma_ids),
            "n_non_sarcoma": len(nonsarcoma_ids),
        },
        "emc_line": emc,
        "double_prediction": double,
        "verdict": verdict,
        "other_druggable_ddr_nodes": other_ddr,
        "context_gene_panel_means": context,
        "_controls": {
            "POLR2A_should_be_strongly_negative_panel_wide": context.get("POLR2A"),
            "ATM_should_be_near_zero_panel_wide": context.get("ATM"),
            "_reading": "If POLR2A is not clearly essential or ATM is not near-neutral panel-wide, "
                        "the read is broken and nothing else here should be quoted.",
        },
    }

    json.dump(result, open(OUT, "w"), indent=2)
    print(json.dumps({k: result[k] for k in ("depmap_release", "verdict", "emc_line")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
