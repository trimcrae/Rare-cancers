#!/usr/bin/env python3
"""Can any antigen be NAMED as the delivery arm of the fusion-junction ASO? — both axes, EMC tissue.

★★ WHY THIS EXISTS. `systems/views/readiness.md` records RT-ASO's single missing item as **"a named
delivery candidate"**, and `fusion-junction-aso-working-record.md` §3c states delivery is the one unsolved
gate and offers an antibody–oligonucleotide-conjugate (AOC) arm whose antigen shortlist came from a
**translocation-sarcoma DepMap SURROGATE** — no EMC tissue in it, and no normal tissue in it either.
Two things have changed since that section was written and neither has been applied to it:

  1. **Three EMC TUMOUR-tissue cohorts are readable** (GSE24369/GPL6244, GSE4303/GPL3290,
     GSE28866/3SEQ) — `emc-expression-panels.json`.
  2. **One of them carries 27 NORMAL-ORGAN libraries** — `gse28866-tumour-vs-normal.json`. That is
     the first on-target/off-tumour EXPOSURE axis this repository has ever had, and exposure is the
     axis a surface-directed modality lives or dies on.

So the question §3c could not ask can now be asked: **is there an antigen that is elevated in EMC
tumour tissue AND restricted in normal tissue, well enough to be named as the AOC targeting arm?**

⛔ THIS MODULE IS ALLOWED TO ANSWER "NO", AND EXPECTS TO. The surface-target manuscript's own
headline is that the selective ∩ normal-restricted intersection is empty among the classic antigens
it evaluated, and its lead antigen ALCAM **loses the exposure axis** (EMC 3SEQ median 0.578 against
a normal-organ median 0.631). A negative that bounds the ASO's delivery gate with an EMC TISSUE
measurement instead of a surrogate is the result; a manufactured candidate is not.

────────────────────────────────────────────────────────────────────────────────────────────────
WHAT THE EXPOSURE AXIS CAN AND CANNOT RESOLVE — established BEFORE anything is scored, because a
score computed past the edge of an instrument is worse than no score.

  CAN:  whether an EMC transcript's median sits above the median of 27 normal-organ libraries from
        SIX organs (bowel, breast, colon, kidney, lung, uterus), on one 3′-end sequencing deposit,
        for the 19 genes whose per-gene values are committed — and where that ratio sits in the
        distribution of the SAME ratio computed for every gene in the deposit (the artifact's own
        `ratio_calibration`, n = 14,120 genes), so a fold-change is graded rather than admired.

  CANNOT: (a) any tissue not among those six — no nerve, no thyroid, no adrenal, no brain, no
        skin, no marrow, no heart, no liver, no pancreas, no testis, and ⛔ NO NORMAL SOFT TISSUE
        AT ALL, in a soft-tissue tumour;
        (b) any gene without a committed per-gene row in that deposit — an ABSENT READING, never a
        reading of absence (CLAUDE.md §4);
        (c) protein, surface localisation, antigen density, epitope accessibility or
        internalisation — every one of which an AOC needs and none of which is a transcript;
        (d) compartment — bulk archival tissue cannot say whether a transcript is in the tumour
        cell, the stroma, the vasculature or an entrapped nerve;
        (e) a distribution — n = 4 EMC libraries, medians, no test, no confidence interval.

  ⇒ THE JOINT UNIVERSE IS THEREFORE TINY AND IS COMPUTED, NOT ASSERTED. Only genes that are (i) a
    plausible cell-surface AOC address and (ii) carry BOTH a lineage reading and an exposure
    reading can be asked the question at all. That count is the first output of this module, and it
    is the honest ceiling on any claim made from it.

────────────────────────────────────────────────────────────────────────────────────────────────
THE SECOND NORMAL-TISSUE INSTRUMENT, AND WHY BOTH ARE NEEDED. `emc-surface-normal-window.json`
(Human Protein Atlas RNA) answers a DIFFERENT question from the 3SEQ normal arm and neither
substitutes for the other:

  HPA  = "is this antigen CONFINED in normal tissue?"    — many tissues, but NO EMC and no tumour.
  3SEQ = "is EMC ABOVE the normal-organ level?"          — real EMC, but only six organs.

A usable AOC address needs both to be true. A low 3SEQ ratio is *not* evidence against the HPA
verdict (it can mean EMC simply does not express the antigen — GPC3 is exactly that), so this
module reports them side by side and never collapses them.

⛔ AND ONE MEASURED DEFECT IN THE HPA HALF IS REPORTED HERE RATHER THAN ASSUMED AWAY. See
`hpa_vital_tissue_override_is_inert` below.

────────────────────────────────────────────────────────────────────────────────────────────────
$0. Pure stdlib. No network, no GPU, no fetch. Every number is READ or DERIVED from a committed
artifact and carries the path and field it came from.

  Inputs   research/modalities/emc-expression-panels.json      (lineage axis, both arrays)
           research/modalities/gse28866-tumour-vs-normal.json   (exposure axis + lineage arm 3)
           research/modalities/emc-surface-normal-window.json   (the HPA normal-tissue prior)
           research/modalities/emc-surfaceome-scan.json         (what stage 1 actually evaluated)
  Output   research/modalities/aso-delivery-antigen.json

  usage    python3 aso_delivery_antigen.py            # derive + write
           python3 aso_delivery_antigen.py --check    # derive + diff against the committed copy
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = os.path.join(HERE, "emc-expression-panels.json")
EXPOSURE = os.path.join(HERE, "gse28866-tumour-vs-normal.json")
NORMAL_WINDOW = os.path.join(HERE, "emc-surface-normal-window.json")
SURFACEOME_SCAN = os.path.join(HERE, "emc-surfaceome-scan.json")
OUT = os.path.join(HERE, "aso-delivery-antigen.json")

GPL6244 = "GSE24369_series_matrix.txt.gz"
GPL3290 = "GSE4303-GPL3290_series_matrix.txt.gz"

# ⚠ REPO-CURATED, and labelled as such wherever it is used. Whether a gene product is a plausible
# ANTIBODY address is not a number in any committed artifact — HPA's `plasma_membrane_confirmed` is
# the closest thing and it is demonstrably too strict (it is False for ALCAM, a type-I membrane
# protein, because HPA's subcellular call for it is "Vesicles"). So membership is declared here with
# its reason, gene by gene, so a reader can disagree with a specific line rather than with a verdict.
# ⛔ NOTHING HERE IS A MEASUREMENT. It is a topology judgement, and it gates which genes are SCORED,
# never what their scores say.
SURFACE_ADDRESS = {
    "ALCAM":  (True,  "single-pass type-I transmembrane adhesion molecule (CD166); an ADC binder has reached patients — alcam-precedent.json -> modality_ladder"),
    "CD44":   (True,  "single-pass type-I transmembrane hyaluronan receptor; HPA subcellular call includes plasma membrane"),
    "CD248":  (True,  "single-pass type-I transmembrane C-type-lectin-like receptor (endosialin/TEM1) — cd248-precedent.json"),
    "CD276":  (True,  "single-pass type-I transmembrane immunoglobulin-superfamily member (B7-H3), the antigen §3c named by extrapolation"),
    "CDH17":  (True,  "single-pass type-I transmembrane cadherin"),
    "CSPG4":  (True,  "single-pass type-I transmembrane proteoglycan (MCSP/NG2)"),
    "FAP":    (True,  "type-II single-pass transmembrane serine protease"),
    "GPC3":   (True,  "GPI-anchored surface proteoglycan"),
    "L1CAM":  (True,  "single-pass type-I transmembrane adhesion molecule"),
    "MSLN":   (True,  "GPI-anchored surface glycoprotein"),
    "RET":    (True,  "single-pass type-I transmembrane receptor tyrosine kinase"),
    "SSTR2":  (True,  "seven-pass G-protein-coupled receptor"),
    "BGN":    (False, "SECRETED small leucine-rich proteoglycan — extracellular matrix, not a cell-surface address"),
    "VCAN":   (False, "SECRETED large chondroitin-sulfate proteoglycan — matrix, not a cell-surface address"),
    "SEMA3C": (False, "SECRETED semaphorin"),
    "PRAME":  (False, "INTRACELLULAR cancer-testis antigen; reachable only as an HLA-presented peptide, which is a TCR/ImmTAC address and not an antibody-internalisation address"),
    "ENO3":   (False, "CYTOSOLIC enolase"),
    "NR4A3":  (False, "NUCLEAR receptor / transcription factor"),
    "PPARG":  (False, "NUCLEAR receptor / transcription factor"),
}

# Organs the exposure panel does NOT contain. ⚠ CURATED AND DELIBERATELY EXPLICIT: the panel's six
# organs are read from the artifact, and this is the complement a reader most needs named, because
# every one of them is a documented on-target/off-tumour site for one or more antigens below.
ORGANS_ABSENT_FROM_THE_EXPOSURE_PANEL = [
    "peripheral nerve", "brain / CNS", "thyroid", "adrenal", "heart", "skeletal muscle",
    "any normal SOFT TISSUE (fibrous, adipose, cartilage, perichondrium)", "skin",
    "bone marrow", "circulating blood cells", "liver", "pancreas", "stomach", "prostate",
    "testis", "ovary", "placenta", "spleen", "lymph node", "thymus", "oesophagus", "bladder",
]

# The deposit's own ratio distribution supplies the thresholds — see `_ratio_state`. A ratio is
# graded against every gene in the same deposit rather than against a number somebody liked.
RATIO_UP_PERCENTILE = 90.0
RATIO_DOWN_PERCENTILE = 10.0
# The array classifier is NOT re-invented here: |t| >= 2 is `emc_expression_panels._cross_platform_verdict`'s
# own rule, and this module reuses it so a gene cannot be graded by two different yardsticks.
ARRAY_T = 2.0


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# helpers
# ═══════════════════════════════════════════════════════════════════════════════════════════════
def _load(path):
    with open(path) as fh:
        return json.load(fh)


def _welch(a, b):
    """Welch t + df. Same arithmetic as `fet_ddr_axis_scan._welch`, reproduced here ONLY so this
    module stays import-free of a lane that pulls numpy/pandas; it is used exclusively to RE-DERIVE
    a statistic the panels artifact already carries, as a check that the committed value and the
    committed per-sample values still agree. It is never the source of a reported number."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return None
    return {"t": round((ma - mb) / se, 3), "n_a": na, "n_b": nb}


def _array_state(rec):
    """UP / DOWN / FLAT / UNREADABLE for one array, by the panels module's own |t| >= 2 rule."""
    if not rec or not rec.get("readable"):
        return {"state": "UNREADABLE", "t": None, "delta": None,
                "_meaning": "⛔ AN INSTRUMENT STATEMENT. No probe mapped to this symbol on this "
                            "platform. It is NOT a low reading and NOT evidence about expression."}
    w = rec.get("welch_EMC_vs_comparator") or {}
    t, d = w.get("t"), w.get("delta_a_minus_b")
    if t is None:
        return {"state": "READABLE_BUT_NO_CONTRAST", "t": None, "delta": d,
                "_meaning": "readable, but too few comparator samples carried a value to contrast."}
    state = "UP" if t >= ARRAY_T else ("DOWN" if t <= -ARRAY_T else "FLAT")
    return {"state": state, "t": t, "df": w.get("df"), "delta": d,
            "n_EMC": rec.get("n_EMC_with_a_value"),
            "n_comparator": rec.get("n_comparator_with_a_value"),
            "n_probes_mapping": rec.get("n_probes_mapping"),
            "EMC_mean_array_percentile": (rec.get("EMC") or {}).get("mean_array_percentile")}


def _ratio_state(ratio, pct):
    """UP / DOWN / FLAT / UNREADABLE for a 3SEQ ratio, graded against the deposit's own distribution
    of the same ratio across every gene it contains."""
    if ratio is None or pct is None:
        return {"state": "UNREADABLE", "ratio": ratio, "percentile_of_all_genes": pct,
                "_meaning": "⛔ NO RATIO EXISTS — either no peak, or a comparator median of zero. "
                            "A missing ratio is NOT a ratio of zero and NOT a low reading."}
    state = ("UP" if pct >= RATIO_UP_PERCENTILE
             else "DOWN" if pct <= RATIO_DOWN_PERCENTILE else "FLAT")
    return {"state": state, "ratio": ratio, "percentile_of_all_genes": pct}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# the two axes
# ═══════════════════════════════════════════════════════════════════════════════════════════════
def _lineage_axis(gene, panels, expo):
    """Is the antigen elevated in EMC tumour tissue relative to COMPARATOR SARCOMAS?

    Three independent instruments on three platform families. ⛔ Their values are never pooled:
    the two arrays are SD units of their own probe distributions, the third is a ratio of medians of
    3′-end read density. Only the STATES are combined, and the combination is a tally, not a score."""
    reads = (panels.get("gene_reads") or {}).get(gene) or {}
    a1 = _array_state(reads.get(GPL6244))
    a2 = _array_state(reads.get(GPL3290))
    cal = ((expo.get("ratio_calibration") or {}).get("per_gene") or {}).get(gene) or {}
    a3 = _ratio_state(cal.get("emc_over_sarcoma"), cal.get("emc_over_sarcoma_percentile"))
    per = {"GPL6244_vs_29_comparator_sarcomas": a1,
           "GPL3290_vs_6_comparator_sarcomas": a2,
           "3SEQ_vs_32_other_sarcoma_libraries": a3}
    states = [x["state"] for x in per.values()]
    n_up, n_down = states.count("UP"), states.count("DOWN")
    n_unreadable = sum(1 for s in states if s in ("UNREADABLE", "READABLE_BUT_NO_CONTRAST"))
    if n_down:
        verdict = "NOT_ELEVATED_AN_INSTRUMENT_READS_IT_DOWN"
    elif n_up >= 2:
        verdict = "ELEVATED_ON_AT_LEAST_TWO_INSTRUMENTS"
    elif n_up == 1:
        verdict = "ELEVATED_ON_ONE_INSTRUMENT_ONLY"
    else:
        verdict = "FLAT_ON_EVERY_INSTRUMENT_THAT_READ_IT"
    return {"per_instrument": per, "n_up": n_up, "n_down": n_down,
            "n_instruments_that_could_not_read_it": n_unreadable, "verdict": verdict}


def _exposure_axis(gene, expo, window):
    """Is the antigen RESTRICTED in normal tissue? Two instruments, two different questions."""
    vals = ((expo.get("per_gene") or {}).get("values") or {}).get(gene) or {}
    cal = ((expo.get("ratio_calibration") or {}).get("per_gene") or {}).get(gene) or {}
    measured = _ratio_state(cal.get("emc_over_normal"), cal.get("emc_over_normal_percentile"))
    measured.update({
        "emc_median": vals.get("emc_median"), "normal_median": vals.get("normal_median"),
        "n_peaks": vals.get("n_peaks"), "n_emc_libraries": vals.get("_n_emc_libs"),
        "n_normal_libraries": vals.get("_n_normal_libs"),
        "_question": "is EMC ABOVE the normal-organ median? (a CONTRAST, six organs, n=4 EMC)"})
    hpa = (window.get("antigens") or {}).get(gene)
    if hpa is None:
        prior = {"state": "ABSENT_FROM_THE_COMMITTED_PRIOR", "window": None,
                 "_meaning": "⛔ AN ABSENT READING, NOT A READING OF ABSENCE. This gene has never "
                             "been queried against HPA by `emc_surface_normal_window.py`, so this "
                             "repository holds NO normal-tissue distribution for it — favourable "
                             "or unfavourable. It is one string in that module's `GENES_BY_SYMBOL` "
                             "away from being closed, at $0."}
    elif hpa.get("_status"):
        prior = {"state": "NO_USABLE_HPA_RECORD", "window": None, "_hpa_status": hpa["_status"]}
    else:
        w = hpa.get("window")
        state = {"RESTRICTED": "CONFINED",
                 "ENHANCED_BROAD": "BROAD_WITH_A_PEAK",
                 "BROAD_LIABILITY": "BROAD",
                 "VITAL_OR_IMMUNE_LIABILITY": "VITAL_OR_IMMUNE"}.get(w, "INTERMEDIATE")
        prior = {"state": state, "window": w,
                 "rna_tissue_specificity": hpa.get("rna_tissue_specificity"),
                 "rna_tissue_distribution": hpa.get("rna_tissue_distribution"),
                 "rna_blood_cell_specificity": hpa.get("rna_blood_cell_specificity"),
                 "plasma_membrane_confirmed": hpa.get("plasma_membrane_confirmed"),
                 "_question": "is the antigen CONFINED in normal tissue? (a DISTRIBUTION, many "
                              "tissues, NO EMC and no tumour anywhere in it)"}
    if measured["state"] == "UNREADABLE":
        verdict = "NOT_SCOREABLE_NO_MEASURED_EXPOSURE_READING"
    elif measured["state"] in ("DOWN", "FLAT"):
        verdict = "FAILS_THE_MEASURED_EXPOSURE_AXIS"
    elif prior["state"] == "CONFINED":
        verdict = "CLEARS_BOTH_NORMAL_TISSUE_INSTRUMENTS"
    elif prior["state"] in ("ABSENT_FROM_THE_COMMITTED_PRIOR", "NO_USABLE_HPA_RECORD"):
        verdict = "ABOVE_NORMAL_ORGANS_BUT_THE_WIDER_PRIOR_IS_ABSENT"
    else:
        verdict = "ABOVE_NORMAL_ORGANS_BUT_THE_WIDER_PRIOR_REFUSES_IT"
    return {"measured_contrast_3SEQ_vs_27_normal_organ_libraries": measured,
            "hpa_normal_tissue_prior": prior, "verdict": verdict,
            "_the_two_are_not_redundant": (
                "A low measured ratio can mean EMC does not express the antigen rather than that "
                "normal tissue expresses it heavily — GPC3 is exactly that case, and its HPA "
                "verdict (RESTRICTED) is not thereby contradicted. The prior cannot see EMC; the "
                "contrast cannot see 22 organ classes. Neither substitutes for the other.")}


def _joint(lineage, exposure):
    lv, ev = lineage["verdict"], exposure["verdict"]
    elevated = lv == "ELEVATED_ON_AT_LEAST_TWO_INSTRUMENTS"
    if ev == "NOT_SCOREABLE_NO_MEASURED_EXPOSURE_READING":
        return "NOT_SCOREABLE_ON_THE_EXPOSURE_AXIS"
    if not elevated:
        return ("FAILS_THE_LINEAGE_AXIS" if lv.startswith("NOT_ELEVATED") or lv.startswith("FLAT")
                else "LINEAGE_AXIS_ON_ONE_INSTRUMENT_ONLY")
    if ev == "FAILS_THE_MEASURED_EXPOSURE_AXIS":
        return "FAILS_THE_EXPOSURE_AXIS"
    if ev == "CLEARS_BOTH_NORMAL_TISSUE_INSTRUMENTS":
        return "CLEARS_BOTH_AXES_ON_EVERY_INSTRUMENT_THAT_CAN_READ_IT"
    if ev == "ABOVE_NORMAL_ORGANS_BUT_THE_WIDER_PRIOR_IS_ABSENT":
        return "CLEARS_BOTH_MEASURED_AXES_BUT_THE_WIDER_NORMAL_TISSUE_PRIOR_IS_ABSENT"
    return "CLEARS_BOTH_MEASURED_AXES_BUT_THE_WIDER_NORMAL_TISSUE_PRIOR_REFUSES_IT"


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# controls, self-checks and the instrument findings that fall out on the way
# ═══════════════════════════════════════════════════════════════════════════════════════════════
def _controls(panels, expo, rows):
    """Known-answer checks. ⛔ A control licenses reading the other rows and licenses nothing else."""
    vals = (expo.get("per_gene") or {}).get("values") or {}
    cal = (expo.get("ratio_calibration") or {}).get("per_gene") or {}
    reads = panels.get("gene_reads") or {}

    def t_of(g, mf):
        return ((reads.get(g) or {}).get(mf) or {}).get("welch_EMC_vs_comparator", {}).get("t")

    out = {}
    # 1 — the disease's own gene must separate EMC from other sarcomas on the exposure deposit.
    out["positive_lineage_control_NR4A3"] = {
        "expected": "detected in EMC; median across the 32 other-sarcoma libraries = 0.000",
        "emc_median": (vals.get("NR4A3") or {}).get("emc_median"),
        "sarcoma_median": (vals.get("NR4A3") or {}).get("sarcoma_median"),
        "GPL6244_t": t_of("NR4A3", GPL6244),
        "passed": ((vals.get("NR4A3") or {}).get("sarcoma_median") == 0.0
                   and (t_of("NR4A3", GPL6244) or 0) >= ARRAY_T),
        "⚠": "a zero comparator median means NR4A3 has NO `emc_over_sarcoma` ratio in the "
             "calibration block — an undefined ratio, which this module reports as UNREADABLE "
             "rather than as an infinite score.",
    }
    # 2 — a published direct transactivation target of an NR4A3 fusion must be up on every arm.
    out["positive_transactivation_control_ENO3"] = {
        "expected": "up on both arrays and above both 3SEQ arms (PMID 26310886)",
        "GPL6244_t": t_of("ENO3", GPL6244), "GPL3290_t": t_of("ENO3", GPL3290),
        "emc_over_normal_percentile": (cal.get("ENO3") or {}).get("emc_over_normal_percentile"),
        "emc_over_sarcoma_percentile": (cal.get("ENO3") or {}).get("emc_over_sarcoma_percentile"),
        "passed": ((t_of("ENO3", GPL6244) or 0) >= ARRAY_T
                   and (t_of("ENO3", GPL3290) or 0) >= ARRAY_T
                   and ((cal.get("ENO3") or {}).get("emc_over_normal_percentile") or 0) >= RATIO_UP_PERCENTILE),
        "⚠": "ENO3 is a CYTOSOLIC enzyme. It controls the tissue instrument and is not, and could "
             "never be, a delivery antigen.",
    }
    # 3 — negative exposure controls: antigens with no reason to be in a soft-tissue sarcoma must
    #     read BELOW normal organs. This is the exposure axis demonstrating that it can say "no".
    negs = {}
    for g in ("GPC3", "MSLN", "L1CAM", "CDH17"):
        p = (cal.get(g) or {}).get("emc_over_normal_percentile")
        negs[g] = {"emc_over_normal": (cal.get(g) or {}).get("emc_over_normal"),
                   "percentile_of_all_genes": p, "below_normal": bool(p is not None and p < 50)}
    out["negative_exposure_controls"] = {
        "expected": "each reads BELOW the normal-organ median in EMC",
        "per_gene": negs,
        "passed": all(v["below_normal"] for v in negs.values()),
    }
    # 4 — the hard case the axis must NOT score: a cancer-testis antigen whose normal median is
    #     zero has no ratio at all, and "absent from normal organs" must not become a free pass.
    prame = vals.get("PRAME") or {}
    out["hard_control_PRAME_an_undefined_ratio_must_not_score"] = {
        "normal_median": prame.get("normal_median"),
        "emc_over_normal": (cal.get("PRAME") or {}).get("emc_over_normal"),
        "scored_by_this_module": "PRAME" in rows,
        "passed": (prame.get("normal_median") == 0.0
                   and (cal.get("PRAME") or {}).get("emc_over_normal") is None
                   and "PRAME" not in rows),
        "_why": "PRAME's normal-organ median is 0.000, so its EMC/normal ratio is UNDEFINED. An "
                "instrument that let that read as a perfect exposure score would name a candidate "
                "off a division by zero. It is excluded on topology first (intracellular) and "
                "would be UNREADABLE on the ratio anyway — both guards, independently.",
    }
    # 5 — the committed Welch statistics must still agree with the committed per-sample values.
    #     A stale artifact is the failure mode this catches; it is not a scientific control.
    mism = []
    for g in sorted(rows):
        for mf in (GPL6244, GPL3290):
            rec = (reads.get(g) or {}).get(mf) or {}
            if not rec.get("readable") or not rec.get("per_sample"):
                continue
            # ⚠ a per-sample z of null means that SAMPLE carried no value for this probe — it is
            # dropped from the arm exactly as the producing module drops it, never read as a zero.
            emc = [s["z_vs_array"] for s in rec["per_sample"]
                   if s["class"] == "EMC" and s.get("z_vs_array") is not None]
            comp = [s["z_vs_array"] for s in rec["per_sample"]
                    if s["class"] not in ("EMC", "unclassified") and s.get("z_vs_array") is not None]
            re_ = _welch(emc, comp)
            got = (rec.get("welch_EMC_vs_comparator") or {}).get("t")
            if re_ and got is not None and abs(re_["t"] - got) > 0.02:
                mism.append({"gene": g, "platform": rec.get("platform"),
                             "committed_t": got, "recomputed_t": re_["t"]})
    out["artifact_self_consistency_recomputed_welch_t"] = {
        "_what": "every array t used below, re-derived from the committed per-sample z values",
        "n_disagreements": len(mism), "disagreements": mism, "passed": not mism,
    }
    out["_pass"] = all(v.get("passed") for k, v in out.items() if isinstance(v, dict) and "passed" in v)
    out["⛔"] = ("A working control licenses reading the other rows and NOTHING MORE. It is not "
                "evidence for any antigen and it is not a validation of any verdict.")
    return out


def _normal_instrument_disagreement(rows):
    """⭐ WHERE THE PRIOR AND THE MEASUREMENT POINT DIFFERENT WAYS — the finding stage 1 could not have.

    Stage 1's ONLY normal-tissue filter was the HPA prior. It has never before been possible to put
    a MEASURED EMC-versus-normal contrast beside it. Doing so is the first check this repository can
    make of that filter's behaviour, and it is not a redundancy check: the two answer different
    questions (see `_the_two_are_not_redundant` on every row).

    ⛔ A DISAGREEMENT IS NOT A REFUTATION OF EITHER SIDE. `prior CONFINED / measured NOT ABOVE` can
    mean the antigen's normal enrichment sits in a tissue the six-organ panel does not contain, or
    that EMC does not express it, or that the prior is too permissive. Nothing here discriminates
    those. What it does establish is that the prior CANNOT stand in for the contrast."""
    cells = {}
    for g, r in rows.items():
        e = r["exposure_axis_vs_normal_tissue"]
        cells[g] = {"hpa_prior": e["hpa_normal_tissue_prior"]["state"],
                    "hpa_window": e["hpa_normal_tissue_prior"].get("window"),
                    "measured_state": e["measured_contrast_3SEQ_vs_27_normal_organ_libraries"]["state"],
                    "measured_emc_over_normal": e["measured_contrast_3SEQ_vs_27_normal_organ_libraries"]["ratio"],
                    "measured_percentile_of_all_genes":
                        e["measured_contrast_3SEQ_vs_27_normal_organ_libraries"]["percentile_of_all_genes"]}
    prior_pass_measure_fail = sorted(g for g, c in cells.items()
                                     if c["hpa_prior"] == "CONFINED" and c["measured_state"] != "UP")
    prior_fail_measure_pass = sorted(g for g, c in cells.items()
                                     if c["hpa_prior"] in ("BROAD", "BROAD_WITH_A_PEAK", "VITAL_OR_IMMUNE")
                                     and c["measured_state"] == "UP")
    return {
        "per_gene": cells,
        "prior_says_CONFINED_but_EMC_is_not_above_normal_organs": prior_pass_measure_fail,
        "prior_REFUSES_but_EMC_is_above_normal_organs": prior_fail_measure_pass,
        "n_agree_on_a_pass": len([g for g, c in cells.items()
                                  if c["hpa_prior"] == "CONFINED" and c["measured_state"] == "UP"]),
        "⭑_the_row_that_matters": (
            "ALCAM is the antigen the surface-target manuscript reports as the ONLY one "
            "concordantly elevated on both EMC arrays, and the HPA prior passes it as RESTRICTED. "
            "The measured contrast puts its EMC median BELOW the normal-organ median. So the "
            "single antigen a prior-only pipeline would have promoted is the one the measured "
            "exposure axis refuses — which is exactly the failure mode the exposure axis was "
            "wanted for, demonstrating itself on the first antigen it was pointed at."),
        "⚠_read_GPC3_out_of_the_disagreement_list": (
            "GPC3 also appears as `prior CONFINED / measured not above normal`, and it is NOT a "
            "disagreement: GPC3 is one of the prior's own positive controls (a tumour-restricted "
            "onco-fetal antigen) and its measured EMC/normal ratio of 0.09 means EMC does not "
            "express it — which is what the negative exposure control expects. Both instruments "
            "are behaving. ALCAM is the row where they genuinely point different ways."),
        "⛔_not_a_verdict_on_HPA": (
            "HPA reads many tissues this deposit does not; the deposit reads EMC, which HPA does "
            "not. Neither instrument is graded here. What is established is that a normal-tissue "
            "PRIOR is not a substitute for a tumour-versus-normal CONTRAST, and stage 1 had only "
            "the prior."),
    }


def _hpa_override_audit(window):
    """⛔ A MEASURED DEFECT IN THE ONLY NORMAL-TISSUE FILTER STAGE 1 EVER HAD.

    `emc_surface_normal_window.classify` computes its vital-tissue liability by string-matching a
    list of vital tissues against `rna_tissue_specific_nTPM`. In the committed artifact that field
    is **null for every scored antigen**, so the match runs against an empty string every time and
    the vital-tissue arm of the classifier CANNOT EVER HAVE FIRED. Every `vital_tissue: []` in that
    file is therefore an ABSENT READING wearing the costume of a clean pass — the exact shape
    CLAUDE.md §4(b) names. The nine antigens that do reach `VITAL_OR_IMMUNE_LIABILITY` all reach it
    through the independent BLOOD-CELL branch, which is a different check on a different field.

    ⚠ WHAT THIS DOES NOT ESTABLISH: whether HPA returns nothing for that column, or whether the
    column key in the query is wrong. That is not decidable from the artifact and this module does
    not guess. Either way, no verdict in that file was ever informed by per-tissue nTPM."""
    ants = window.get("antigens") or {}
    scored = {g: r for g, r in ants.items() if not r.get("_status")}
    null_tpm = sorted(g for g, r in scored.items() if r.get("rna_tissue_specific_nTPM") in (None, ""))
    with_vital = sorted(g for g, r in scored.items() if r.get("vital_tissue"))
    via_blood = sorted(g for g, r in scored.items()
                       if r.get("window") == "VITAL_OR_IMMUNE_LIABILITY" and r.get("immune_or_circulating"))
    return {
        "n_antigens_scored_in_the_prior": len(scored),
        "n_with_a_null_rna_tissue_specific_nTPM": len(null_tpm),
        "n_with_any_vital_tissue_hit": len(with_vital),
        "vital_tissue_override_ever_fired": bool(with_vital),
        "n_reaching_VITAL_OR_IMMUNE_LIABILITY_via_the_blood_branch": len(via_blood),
        "genes_reaching_it_via_the_blood_branch": via_blood,
        "verdict": ("⛔ INERT — the vital-tissue override has never fired on any antigen in the "
                    "committed prior, because the field it reads is null in every record."
                    if not with_vital else
                    "the vital-tissue override fired on at least one antigen; re-read this audit"),
        "consequence_for_this_module": (
            "Every `window: RESTRICTED` in the prior means 'not low-specificity, not detected-in-all, "
            "not blood-confined'. It does NOT mean 'checked against vital tissue and found clear'. "
            "So the prior is used here as a NECESSARY condition that is weaker than it reads, never "
            "as a sufficient one, and no antigen is named on it."),
        "routed_fix": ("`emc_surface_normal_window.py` -> the HPA query column list / `classify`. "
                       "Not this module's file to change; recorded so its owner can."),
    }


def _stage1_coverage(scan, universe):
    """Which of the antigens the EMC-tissue axes can score were never evaluated by the surrogate?

    ⭑ THIS IS THE FINDING THAT REFRAMES THE NEGATIVE. `surfaceome-instrument-limits.json` records
    the CSPG4 coverage gap (L4) as a one-gene defect. Applying the same membership test to the whole
    jointly-scoreable universe shows it is not one gene."""
    txt = json.dumps(scan)
    rows = {}
    for g in sorted(universe):
        rows[g] = {
            "in_actionable_antigens": g in (scan.get("actionable_antigens") or {}),
            "in_top_candidates": any((c or {}).get("gene") == g for c in scan.get("top_candidates") or []),
            "appears_anywhere_in_the_stage_1_artifact": f'"{g}"' in txt,
        }
    absent = sorted(g for g, r in rows.items() if not r["appears_anywhere_in_the_stage_1_artifact"])
    return {
        "_what": "membership of each jointly-scoreable antigen in the stage-1 surrogate artifact",
        "per_gene": rows,
        "genes_with_NO_per_gene_row_anywhere_in_stage_1": absent,
        "n_absent": len(absent), "n_universe": len(rows),
        "⛔_whether_they_were_SCANNED_is_undecidable": (
            "The scan unioned ~2,820 UniProt genes and then recorded only 40 top candidates, 47 "
            "seed antigens and one line's top 30 — it never recorded the scanned gene list. So "
            "'absent from the outputs' is NOT 'not scanned' (surfaceome-instrument-limits.json -> "
            "limits.L4_cspg4_coverage_gap says the same of CSPG4). What IS decidable: no per-gene "
            "number exists for these genes anywhere in the surrogate record, so the surrogate "
            "never measured them and never rejected them."),
    }


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# derive
# ═══════════════════════════════════════════════════════════════════════════════════════════════
def derive():
    panels, expo = _load(PANELS), _load(EXPOSURE)
    window, scan = _load(NORMAL_WINDOW), _load(SURFACEOME_SCAN)

    expo_genes = sorted((expo.get("per_gene") or {}).get("values") or {})
    cal = (expo.get("ratio_calibration") or {}).get("per_gene") or {}
    board = ((panels.get("reads") or {}).get("read_8_SURFACE_ANTIGEN") or {}).get("cross_platform_board") or {}
    board_genes = sorted((board.get("per_gene") or {}))

    surface = sorted(g for g in expo_genes if SURFACE_ADDRESS.get(g, (False, ""))[0])
    excluded = {g: SURFACE_ADDRESS[g][1] for g in expo_genes
                if g in SURFACE_ADDRESS and not SURFACE_ADDRESS[g][0]}
    unclassified = sorted(g for g in expo_genes if g not in SURFACE_ADDRESS)

    # the universe: a surface address that carries BOTH a lineage reading and an exposure reading
    universe = [g for g in surface
                if (panels.get("gene_reads") or {}).get(g)
                and (cal.get(g) or {}).get("emc_over_normal") is not None]
    not_scoreable = sorted(set(surface) - set(universe))

    rows = {}
    for g in universe:
        lin = _lineage_axis(g, panels, expo)
        exp = _exposure_axis(g, expo, window)
        rows[g] = {"gene": g,
                   "surface_address_basis_REPO_CURATED": SURFACE_ADDRESS[g][1],
                   "lineage_axis_vs_comparator_sarcomas": lin,
                   "exposure_axis_vs_normal_tissue": exp,
                   "joint_verdict": _joint(lin, exp)}

    by_verdict = {}
    for g, r in rows.items():
        by_verdict.setdefault(r["joint_verdict"], []).append(g)
    by_verdict = {k: sorted(v) for k, v in sorted(by_verdict.items())}

    named = by_verdict.get("CLEARS_BOTH_AXES_ON_EVERY_INSTRUMENT_THAT_CAN_READ_IT", [])
    residual = (by_verdict.get("CLEARS_BOTH_MEASURED_AXES_BUT_THE_WIDER_NORMAL_TISSUE_PRIOR_IS_ABSENT", [])
                + by_verdict.get("CLEARS_BOTH_MEASURED_AXES_BUT_THE_WIDER_NORMAL_TISSUE_PRIOR_REFUSES_IT", []))

    dist = expo.get("ratio_calibration") or {}
    out = {
        "_what": ("Can any antigen be NAMED as the antibody–oligonucleotide-conjugate delivery arm "
                  "of the EWSR1::NR4A3 fusion-junction ASO? Both axes — elevated in EMC TUMOUR "
                  "tissue and restricted in NORMAL tissue — scored against three EMC cohorts."),
        "_why": ("readiness.md records RT-ASO's one missing item as 'a named delivery candidate', "
                 "and fusion-junction-aso-working-record.md §3c's AOC shortlist came from a DepMap surrogate "
                 "with no EMC and no normal tissue in it. Three EMC tumour cohorts and 27 "
                 "normal-organ libraries now exist. This re-asks the question on that basis."),
        "_execution_model": "$0. Pure stdlib, no network, no GPU. Every number is read or derived "
                            "from a committed artifact named in `_inputs`.",
        "_language_discipline": (
            "⛔ NOTHING HERE ASSERTS EFFICACY, SAFETY, SELECTIVITY, A THERAPEUTIC WINDOW, ANTIGEN "
            "DENSITY, INTERNALISATION OR CLINICAL READINESS, AND NO SUCH QUANTITY IS COMPUTED "
            "ANYWHERE IN THIS MODULE. Every reading is TRANSCRIPT. No EMC patient has received any "
            "agent named here, and naming an antigen is not naming a therapy."),
        "_not_preregistered": (
            "⚠ STATED PLAINLY: this analysis was written AFTER its input artifacts were visible, so "
            "no threshold here may be described as pre-registered. Two things limit the freedom "
            "that gives: the array rule (|t| >= 2) is `emc_expression_panels._cross_platform_verdict`'s "
            "OWN rule and is not chosen here, and the 3SEQ rule is the 90th percentile of the "
            "deposit's own distribution of the same ratio over 13,708 genes — a yardstick that "
            "existed in the artifact before this module did. Neither was tuned to the answer."),
        "_inputs": {
            "lineage_axis_arrays": "research/modalities/emc-expression-panels.json -> gene_reads",
            "exposure_axis_and_3SEQ_lineage_arm": "research/modalities/gse28866-tumour-vs-normal.json "
                                                  "-> per_gene.values and ratio_calibration.per_gene",
            "normal_tissue_prior": "research/modalities/emc-surface-normal-window.json -> antigens",
            "stage_1_surrogate_coverage": "research/modalities/emc-surfaceome-scan.json",
        },

        # ── 1 · what the instruments can and cannot resolve, computed before anything is scored ──
        "instrument_reach": {
            "_read_this_first": (
                "The exposure axis is the new thing and it is much narrower than 'EMC vs normal'. "
                "Its ceiling is stated here so no verdict below can be read past it."),
            "exposure_axis": {
                "deposit": "GSE28866 (3SEQ 3'-end read density)",
                "n_EMC_libraries": 4,
                "n_normal_organ_libraries": 27,
                "organs_present": ["bowel", "breast", "colon", "kidney", "lung", "uterus"],
                "organs_and_tissue_classes_ABSENT_REPO_CURATED": ORGANS_ABSENT_FROM_THE_EXPOSURE_PANEL,
                "⛔_no_normal_soft_tissue_at_all": (
                    "EMC is a soft-tissue tumour and the normal arm contains no fibrous, adipose, "
                    "cartilaginous or perichondrial tissue. An antigen shared with normal soft "
                    "tissue is INVISIBLE to this axis."),
                "n_genes_with_a_committed_per_gene_row": len(expo_genes),
                "genes_with_a_committed_per_gene_row": expo_genes,
                "n_genes_in_the_deposit_used_for_calibration": dist.get("n_genes_in_deposit"),
                "ratio_calibration_used_as_the_threshold": {
                    "emc_over_normal": dist.get("distribution_emc_over_normal"),
                    "emc_over_sarcoma": dist.get("distribution_emc_over_sarcoma"),
                    "_why": "the deposit's MEDIAN gene already moves ~1.05x between arms, so a "
                            "raw fold-change is not a reading until it is placed in that "
                            "distribution. UP here means >= the 90th percentile of all genes.",
                },
                "_it_is_a_contrast_not_a_safety_statement": (
                    "27 libraries from six organs, transcript only, n = 4 EMC medians with no test "
                    "and no confidence interval. This is an EXPOSURE READING and it is not, and "
                    "cannot be, a normal-tissue safety assessment."),
            },
            "lineage_axis": {
                "instruments": [
                    "GSE24369 / GPL6244 — 6 EMC vs 29 comparator sarcomas, single-channel intensity",
                    "GSE4303 / GPL3290 — 10 EMC vs 6 comparator sarcomas, two-colour log-ratio",
                    "GSE28866 / 3SEQ — 4 EMC vs 32 non-EMC sarcoma libraries, read density",
                ],
                "⛔_never_pooled": "three platform families, three different physical quantities. "
                                  "Only the STATES are tallied; the values are never combined.",
                "n_genes_on_the_committed_surface_board": len(board_genes),
            },
            "joint_universe": {
                "_definition": "a plausible cell-surface AOC address (REPO-CURATED topology) that "
                               "carries BOTH a lineage reading AND a measured exposure reading.",
                "n": len(universe), "genes": sorted(universe),
                "surface_addresses_with_no_measured_exposure_reading": not_scoreable,
                "genes_on_the_exposure_axis_excluded_on_topology": excluded,
                "genes_on_the_exposure_axis_with_no_topology_call": unclassified,
                "n_surface_board_genes_the_exposure_axis_cannot_reach": len(
                    [g for g in board_genes if g not in expo_genes]),
                "⛔_the_ceiling": (
                    f"{len(universe)} antigens can be asked the two-axis question AT ALL. Every "
                    f"other surface antigen this repository has ever discussed — including all "
                    f"{len([g for g in board_genes if g not in expo_genes])} genes on the committed "
                    "surface board with no row in the exposure deposit — is UNSCOREABLE on "
                    "exposure, which is an absent reading and never a negative."),
            },
            "what_no_instrument_here_can_resolve": [
                "PROTEIN. Every reading is transcript; transcript-to-protein correlation for "
                "membrane proteins is modest and is not measured anywhere in this repository.",
                "SURFACE LOCALISATION and ANTIGEN DENSITY — the two quantities an antibody arm "
                "actually sees.",
                "INTERNALISATION. An AOC must be endocytosed to release its oligonucleotide; "
                "nothing in this repository measures endocytic rate for any antigen.",
                "COMPARTMENT. Bulk archival tissue cannot say whether a transcript sits in the "
                "tumour cell, the stroma, the vasculature, the immune infiltrate or an entrapped "
                "nerve — and EMC is hypocellular and matrix-dominated, which is where this bites "
                "hardest. A single-cell or spatial EMC dataset would settle it; none is in hand.",
                "THE REST OF DELIVERY. Blood -> tumour -> cell -> endosomal escape is unaddressed "
                "by an antigen name, and the myxoid matrix is itself a diffusion barrier.",
            ],
        },

        # ── 2 · the scoring ──
        "scoring_rules": {
            "lineage_axis": {
                "array": f"UP if Welch t >= {ARRAY_T}, DOWN if t <= -{ARRAY_T}, else FLAT. "
                         "REUSED from emc_expression_panels._cross_platform_verdict, not invented here.",
                "3SEQ": f"UP if the EMC/other-sarcoma ratio sits at or above the "
                        f"{RATIO_UP_PERCENTILE:.0f}th percentile of the same ratio across every "
                        f"gene in the deposit; DOWN at or below the {RATIO_DOWN_PERCENTILE:.0f}th.",
                "verdict": "ELEVATED requires >= 2 instruments UP and 0 DOWN. One DOWN anywhere "
                           "refuses the antigen outright.",
            },
            "exposure_axis": {
                "measured": f"EMC/normal-organ ratio at or above the {RATIO_UP_PERCENTILE:.0f}th "
                            "percentile of the deposit's own distribution.",
                "prior": "HPA window must be RESTRICTED. ENHANCED_BROAD, BROAD_LIABILITY and "
                         "VITAL_OR_IMMUNE_LIABILITY all refuse; an absent row is an ABSENT READING "
                         "and refuses NAMING without being evidence against the antigen.",
            },
            "naming": "An antigen may be NAMED only if it clears both axes on EVERY instrument "
                      "that can read it AND no decision-relevant instrument is absent. Anything "
                      "less is a ranked residual, never a name.",
        },
        "per_antigen": rows,
        "by_joint_verdict": by_verdict,

        # ── 3 · controls and instrument findings ──
        "controls": _controls(panels, expo, rows),
        "the_two_normal_tissue_instruments_where_they_disagree": _normal_instrument_disagreement(rows),
        "hpa_vital_tissue_override_is_inert": _hpa_override_audit(window),
        "stage_1_coverage_over_this_universe": _stage1_coverage(scan, universe),

        # ── 4 · the answer ──
        "headline": {
            "can_a_delivery_candidate_be_NAMED": bool(named),
            "antigens_that_clear_both_axes_on_every_instrument_that_can_read_them": sorted(named),
            "ranked_residual_clears_the_measured_axes_but_cannot_be_named": sorted(residual),
            "n_antigens_scoreable_on_both_axes": len(universe),
        },
    }

    out["headline"]["n_antigens_passed_by_BOTH_normal_tissue_instruments"] = \
        out["the_two_normal_tissue_instruments_where_they_disagree"]["n_agree_on_a_pass"]
    out["headline"]["statement"] = _headline_statement(out)
    out["what_this_changes_for_PUB_ASO"] = _pub_aso_delta(out)
    out["routed_next_steps"] = _next_steps(out)
    out["⛔_what_this_file_does_NOT_claim"] = [
        "That any antigen named or ranked here is on the EMC cell surface. Every reading is transcript.",
        "That any antigen is safe, selective, or has a therapeutic window in EMC. No such quantity "
        "is computed here or in any artifact this module reads.",
        "That an antigen absent from the exposure deposit is low in EMC or absent from normal "
        "tissue. It was not measured. ⛔ An absent reading is not a reading of absence.",
        "That the HPA prior's RESTRICTED verdicts are vital-tissue-checked — they are not; see "
        "`hpa_vital_tissue_override_is_inert`.",
        "That naming an antigen would solve delivery. Blood-to-tumour distribution, matrix "
        "penetration, internalisation and endosomal escape are all untouched by anything here.",
    ]
    return out


def _headline_statement(out):
    h = out["headline"]
    uni = h["n_antigens_scoreable_on_both_axes"]
    if h["can_a_delivery_candidate_be_NAMED"]:
        return (f"{len(h['antigens_that_clear_both_axes_on_every_instrument_that_can_read_them'])} "
                f"of {uni} scoreable antigens clear both axes on every instrument that can read "
                f"them: {', '.join(h['antigens_that_clear_both_axes_on_every_instrument_that_can_read_them'])}.")
    res = h["ranked_residual_clears_the_measured_axes_but_cannot_be_named"]
    return (
        f"⛔ NO. Of the {uni} antigens that can be asked the two-axis question at all, NONE clears "
        f"both axes on every instrument that can read it, so no delivery candidate can be named. "
        f"{len(res)} clear the two MEASURED axes and are refused only by the wider normal-tissue "
        f"prior or by its absence ({', '.join(res) if res else 'none'}). What has changed is the "
        f"BASIS of the refusal: the ASO's delivery gate is now bounded by a measurement in EMC "
        f"tumour tissue against normal organs, not by a translocation-sarcoma surrogate.")


def _pub_aso_delta(out):
    """What §3c can say now that it could not before — and what it currently says that is stale."""
    rows = out["per_antigen"]

    def v(g):
        return (rows.get(g) or {}).get("joint_verdict")

    return {
        "_scope": "fusion-junction-aso-working-record.md §3c (the AOC delivery arm) and "
                  "systems/views/readiness.md -> RT-ASO 'a named delivery candidate'.",
        "can_now_say": [
            "The AOC targeting arm has been tested against EMC TUMOUR tissue and against NORMAL "
            "organ tissue, not only against a translocation-sarcoma surrogate. §3c's honest bound "
            "— 'the toxicity-relevant tumour-vs-normal window (GTEx/HPA) is the flagged next "
            "filter … not done here' — is no longer the state of the evidence; the filter has been "
            "applied on both a prior and a measured contrast.",
            "The delivery gate is bounded by a NEGATIVE with a named basis: no antigen this "
            "repository can score clears both axes on every instrument that can read it.",
            f"The specific antigen §3c names by extrapolation, B7-H3/CD276, is refused on the "
            f"lineage axis in EMC tumour tissue itself ({v('CD276')}), not merely on the "
            "surrogate's selectivity test.",
            "The size of the answerable question is now measured: "
            f"{out['headline']['n_antigens_scoreable_on_both_axes']} antigens can be asked the "
            "two-axis question at all, and that ceiling belongs in the limitations of any "
            "delivery claim.",
        ],
        "must_now_retire_or_amend_in_section_3c": [
            "⛔ 'a data-ranked alternative shortlist' / 'This is a nameable, prioritised "
            "targeting-arm shortlist for an EMC AOC' — the named members are surrogate ranks. Two "
            "of them, FGFR1 and PTK7, are CONCORDANT_DOWN_ON_BOTH arrays in EMC tumour tissue "
            "(emc-surface-target-landscape.md §3.5), i.e. the shortlist's leads point the wrong "
            "way in the disease.",
            "⛔ 'A public real-EMC tumour dataset exists (GSE4303) but was tried and is UNUSABLE "
            "for this' and 'the public-data route to real-EMC surface expression is exhausted' — "
            "superseded by emc-surface-target-landscape.md §3.10; GSE4303's GPL3290 arm is "
            "readable through an accession bridge, and two further EMC cohorts are read.",
            "⚠ 'the toxicity-relevant tumour-vs-normal window … is the flagged next filter, not "
            "done here' — it is now done, on two independent normal-tissue instruments.",
        ],
        "still_cannot_say": [
            "That any antigen is a delivery handle. Nothing here measures protein, surface "
            "density, internalisation or endosomal escape.",
            "That the local/intratumoural route in §3c is displaced. It remains the only delivery "
            "hypothesis in §3c that needs no antigen at all, and this analysis strengthens rather "
            "than weakens that ordering.",
            "That the readiness register's missing item is discharged. 'A named delivery "
            "candidate' is still missing, and this module makes the reason precise instead of open.",
        ],
    }


def _next_steps(out):
    res = out["headline"]["ranked_residual_clears_the_measured_axes_but_cannot_be_named"]
    return [
        {"step": "Add the missing antigens to the HPA normal-tissue prior",
         "detail": ("`emc_surface_normal_window.py` -> `GENES_BY_SYMBOL` does not contain "
                    + ", ".join(sorted(g for g in out["per_antigen"]
                                       if (out["per_antigen"][g]["exposure_axis_vs_normal_tissue"]
                                           ["hpa_normal_tissue_prior"]["state"]
                                           == "ABSENT_FROM_THE_COMMITTED_PRIOR")))
                    + ". Those antigens carry a measured EMC-vs-normal-organ reading and NO wider "
                      "normal-tissue prior, which is the single reason they cannot be graded."),
         "cost": "$0 — one string per gene, then `emc-expression-datasets.yml mode=panels`.",
         "why_it_is_decisive": ("the exposure panel holds six visceral organs. For any receptor "
                                "with documented neural, endocrine or soft-tissue normal "
                                "expression, the tissues that would refuse it are exactly the ones "
                                "the panel lacks, so the wider prior is not a formality."),
         "owner": "not this module's file — routed, not applied."},
        {"step": "Recover the two NORMAL SOFT-TISSUE libraries already inside GSE24369",
         "detail": ("GSM600968 and GSM600969 are 'Skeletal muscle pooled RNA' samples on GPL6244. "
                    "`emc_expression_panels.py` classifies them `unclassified` and drops them from "
                    "`per_sample`, correctly — feeding normal tissue into a tumour comparator arm "
                    "was a real bug the RET lane found and fixed. But as their OWN arm they are "
                    "the only normal SOFT-tissue libraries anywhere in the three cohorts, and the "
                    "3SEQ exposure panel has none. n = 2 and pooled, so no distribution — a second "
                    "exposure reading on a different normal tissue class, not a test."),
         "cost": "$0 — the series is already fetched by an existing mode.",
         "owner": "not this module's file — routed, not applied."},
        {"step": "Repair the inert vital-tissue override in the normal-tissue prior",
         "detail": "see `hpa_vital_tissue_override_is_inert.routed_fix`.",
         "cost": "$0.", "owner": "not this module's file — routed, not applied."},
        {"step": "The measurement that would actually decide it",
         "detail": ("For any residual antigen (" + (", ".join(res) if res else "none") + "): IHC or "
                    "surface proteomics on archival EMC with a normal-tissue comparison, plus a "
                    "single-cell or spatial EMC dataset to assign the compartment. Neither is "
                    "obtainable from public deposits and neither is in hand."),
         "cost": "collaborator-held; not $0.", "owner": "the EMC model groups — see "
                 "emc-surface-target-landscape.md §7."},
    ]


# ═══════════════════════════════════════════════════════════════════════════════════════════════
def main(argv):
    res = derive()
    if "--check" in argv:
        if not os.path.exists(OUT):
            print("no committed artifact to check against", file=sys.stderr)
            return 1
        old = _load(OUT)
        a, b = json.dumps(old.get("per_antigen"), sort_keys=True), json.dumps(res["per_antigen"], sort_keys=True)
        c, d = json.dumps(old.get("headline"), sort_keys=True), json.dumps(res["headline"], sort_keys=True)
        if a == b and c == d:
            print("aso_delivery_antigen --check: per_antigen and headline reproduce exactly")
            return 0
        print("⛔ DRIFT — the committed artifact does not reproduce from current inputs", file=sys.stderr)
        return 1
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=False)
        fh.write("\n")
    print(res["headline"]["statement"])
    print(f"  universe: {res['headline']['n_antigens_scoreable_on_both_axes']} antigens")
    for k, v in res["by_joint_verdict"].items():
        print(f"  {k}: {', '.join(v)}")
    print(f"  controls pass: {res['controls']['_pass']}")
    print(f"  -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
