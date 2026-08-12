#!/usr/bin/env python3
"""Confound audit and sensitivity analysis for the EWSR1::NR4A3 transcriptional-output reading.

WHAT THIS IS. The manuscript `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md` reports
that the three genes with a DNA-binding assay against an NR4A3 chimera (SEMA3C, PPARG, ENO3) read
higher in EMC tumour tissue. Its own §4.1 lists four things that reading is equally consistent with
and states that nothing in these datasets removes the cell-of-origin or the myxoid-architecture
explanation. THIS MODULE TESTS THAT STATEMENT rather than conceding it, using only the cached
inputs the manuscript already depends on. Every test here is offline, CPU-only and $0.

WHAT IT IS NOT. Nothing here is evidence of efficacy, selectivity, safety, a therapeutic window or
clinical readiness for any agent, target or gene, and expression data cannot become that evidence.
No test here shows any gene being bound by any fusion protein; occupancy is not measured anywhere
in this repository and §3.10 of the manuscript records that no NR4A3-fusion cistrome was retrieved.

THE EIGHT READINGS
  1. comparator_composition   what the comparator arms ACTUALLY contain, read from the GEO sample
                              titles rather than from a bucket label -- including the myxoid
                              composition, the reference-pool split, and the excluded samples.
  2. muscle_admixture         ENO3 is muscle-specific beta-enolase and EMC arises in the thigh, so
                              "ENO3 is muscle contamination" is the obvious objection. The series
                              carries two pooled skeletal-muscle RNA samples, which turns the
                              objection into a measurable control.
  3. myxoid_restricted        the class-A contrast recomputed against myxoid-only and
                              non-myxoid-only comparator arms.
  4. reference_pool_matched   the GPL3290 contrast recomputed against the pool-matched comparators
                              only, because three of its six comparators use a different reference
                              pool from every EMC sample.
  5. per_stratum              the contrast against each comparator class separately, including
                              LGFMS alone -- itself FET-rearranged.
  6. covariate_adjusted       the contrast recomputed on residuals after regressing out a
                              matrix/vascular proxy, as a SENSITIVITY analysis, not a correction.
  7. minimum_detectable       what each set score would have had to reach to clear its own null,
                              so a flat set reads as a bounded negative rather than a shrug.
  8. within_emc_fusion_axis   within the EMC arm alone, does the gene track NR4A3 level? The only
                              axis in these data that speaks to fusion OUTPUT rather than to EMC
                              membership -- and it is weak, which is reported.

THE PROVENANCE RULE THAT GOVERNS THE COVARIATE PANEL. A proxy for "how much matrix is in this
tumour" must not be built from genes that were selected BECAUSE they are high in EMC. Every gene in
Filion Table 1/2 and in the Brenca axon-guidance lists was selected exactly that way, so adjusting
on one of them would remove EMC signal by construction and the analysis would prove nothing. The
panels below are therefore filtered against every gene the manuscript scores anywhere, and the
filter is ASSERTED at runtime (`_provenance_audit`) rather than trusted -- a first draft of this
module used VCAN and HAPLN1, both of which are in those EMC-derived lists, and it produced a
confidently wrong answer of the opposite sign.

REPRODUCTION
    python3 nr4a3_fusion_targets_confounds.py            # derive and write the artifact
    python3 nr4a3_fusion_targets_confounds.py --check    # re-derive and diff against the artifact
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS_INPUTS = os.path.join(HERE, "emc-expression-panels-inputs.json")
FUSION_INPUTS = os.path.join(HERE, "nr4a3-fusion-targets-inputs.json")
PRIMARY = os.path.join(HERE, "nr4a3-fusion-targets.json")
OUT = os.path.join(HERE, "nr4a3-fusion-targets-confounds.json")

sys.path.insert(0, HERE)
from emc_hypoxia_confounds import (  # noqa: E402
    MYXOID_STATUS, REFERENCE_TOKENS, _arms, _contrast, _mean, _pearson,
    _reference_token, _zrow,
)
from fet_ddr_axis_scan import _welch  # noqa: E402
# The exact two-sided label-permutation null the manuscript's §3.12 already uses, imported from the
# module that OWNS it so a stratified contrast is tested by the same instrument as a pooled one.
from nr4a3_fusion_targets_robustness import _label_permutation  # noqa: E402

MIN_GROUP_N_FOR_A_CONTRAST = 3
DECIMALS = 4

CLASS_A = ["ENO3", "PPARG", "SEMA3C"]
INSTRUMENT_CONTROLS = ["NR4A3", "PLAGL1", "SGK1"]

# ---------------------------------------------------------------------------------------------
# COVARIATE PANELS -- chosen by PROVENANCE, then filtered against everything the manuscript scores.
# These are structural/stromal genes with no claimed relationship to NR4A3. `_provenance_audit`
# refuses to run if any member turns out to be in a scored set, so the filter cannot rot silently.
# ---------------------------------------------------------------------------------------------
MATRIX_PANEL_CANDIDATES = [
    "BGN", "COL5A1", "COL5A2", "DCN", "FN1", "LUM", "MMP2", "POSTN", "SPP1", "TNC", "VIM",
]
VASCULAR_PANEL_CANDIDATES = ["ENG", "KDR", "TEK"]

# Muscle markers for reading 2. MYH7 is already a class-B row in the manuscript's own catalogue,
# which is what makes it usable here: its EMC reading is published in the paper and needs no new
# measurement. The rest are read if the platform carries them and skipped if it does not.
MUSCLE_MARKER_CANDIDATES = [
    "MYH7", "ACTA1", "CKM", "DES", "MYOG", "MYOD1", "TNNT1", "TNNT3", "TTN", "MYL1", "PYGM",
]

_STRUCTURAL_NOTE = (
    "A structural/stromal gene with no published relationship to NR4A3 or to any NR4A3 fusion, "
    "retained only if it appears in NO gene set this manuscript scores."
)


def _r(x, nd=DECIMALS):
    return None if x is None else round(x, nd)


# ---------------------------------------------------------------------------------------------
# PROVENANCE
# ---------------------------------------------------------------------------------------------
def _scored_gene_universe(primary):
    """Every gene the manuscript scores anywhere: set members, catalogue rows, per-gene reads."""
    used = set()
    for _, v in (primary.get("set_definitions") or {}).items():
        if isinstance(v, dict):
            for key in ("genes", "members", "symbols"):
                if isinstance(v.get(key), list):
                    used |= {g for g in v[key] if isinstance(g, str)}
    et = primary.get("evidence_table")
    rows = et if isinstance(et, list) else (et or {}).get("rows", [])
    used |= {r.get("gene") for r in rows if isinstance(r, dict) and r.get("gene")}
    used |= set((primary.get("gene_reads") or {}).keys())
    return used


def _provenance_audit(primary):
    """Refuse to build a covariate panel out of anything the manuscript scores.

    THIS IS A GUARD, NOT A REPORT. A proxy built from EMC-derived genes removes EMC signal by
    construction, so a contaminated panel does not produce a weaker result -- it produces a
    confidently wrong one."""
    scored = _scored_gene_universe(primary)
    audit = {
        "_what": "every candidate covariate gene checked against every gene the manuscript scores",
        "_why": ("a matrix proxy built from genes selected BECAUSE they are high in EMC would "
                 "remove EMC signal by construction. Filion Table 1/2 and the Brenca axon-guidance "
                 "lists were selected exactly that way."),
        "n_genes_scored_by_the_manuscript": len(scored),
        "rejected": {},
        "panels": {},
    }
    panels = {}
    for name, cands in (("matrix", MATRIX_PANEL_CANDIDATES),
                        ("vascular", VASCULAR_PANEL_CANDIDATES)):
        bad = sorted(g for g in cands if g in scored)
        if bad:
            audit["rejected"][name] = bad
        panels[name] = sorted(g for g in cands if g not in scored)
        audit["panels"][name] = {"members": panels[name], "n": len(panels[name]),
                                 "_selection": _STRUCTURAL_NOTE}
    if audit["rejected"]:
        raise SystemExit(
            "nr4a3_fusion_targets_confounds: a covariate panel contains a gene this manuscript "
            "scores, which would make the adjustment circular: "
            f"{json.dumps(audit['rejected'])}. Remove it or justify it explicitly.")
    return audit, panels


# ---------------------------------------------------------------------------------------------
# INSTRUMENT
# ---------------------------------------------------------------------------------------------
def _merge_gene_sources(primary_tgt, secondary_tgt, must_agree):
    """Union the two committed caches' gene tables so a gene missing from one is still readable.

    WHY THIS IS SAFE, AND WHY IT IS ASSERTED RATHER THAN ASSUMED. Both caches are parsed from the
    same GEO series matrix, so they carry the same samples in the same order and the same
    per-sample background. If either were false the merged z would silently mix two scales. Both
    are therefore compared element-wise before anything is merged. PLAGL1 -- the directional
    falsifier -- is readable only in the secondary cache, which is why this exists.

    THE PER-GENE GUARD IS SCOPED, AND THE SCOPE IS THE POINT. Every shared gene is compared and the
    disagreement census is REPORTED, but the merge is refused only when a gene THIS MODULE READS
    disagrees. Measured on the real caches: 1 of 997 shared genes on GPL6244 (ACAA1, mapped to two
    probes by one module and one by the other) and 0 of 887 on GPL3290; ENO3, PPARG, SEMA3C and
    NR4A3 agree to exactly 0.0 on both. A global refusal would block the merge over a gene no
    analysis here touches, and silently widening the tolerance instead would hide the day a gene
    that IS used starts to disagree."""
    if secondary_tgt is None:
        return primary_tgt, {"_status": "NO_SECONDARY_CACHE"}
    a = [s["gsm"] for s in primary_tgt["samples"]]
    b = [s["gsm"] for s in secondary_tgt["samples"]]
    if a != b:
        raise SystemExit("nr4a3_fusion_targets_confounds: the two caches disagree on sample "
                         "order; refusing to merge two different scales.")
    if primary_tgt.get("background_per_sample") != secondary_tgt.get("background_per_sample"):
        raise SystemExit("nr4a3_fusion_targets_confounds: the two caches disagree on the "
                         "per-sample background; refusing to merge two different scales.")
    pg = primary_tgt.get("genes") or {}
    sg = secondary_tgt.get("genes") or {}
    added = sorted(set(sg) - set(pg))
    shared = sorted(set(sg) & set(pg))
    disagree, worst_used = {}, 0.0
    for g in shared:
        za, zb = _zrow(primary_tgt, g), _zrow(secondary_tgt, g)
        w = max((abs(x - y) for x, y in zip(za, zb) if x is not None and y is not None), default=0.0)
        if w > 1e-9:
            disagree[g] = {
                "worst_abs_z_difference": _r(w, 6),
                "n_probes_primary_cache": pg[g].get("n_probes_mapping"),
                "n_probes_secondary_cache": sg[g].get("n_probes_mapping"),
                "_cause": ("the two modules map a different number of probes to this symbol, so "
                           "they average different probe sets."),
            }
        if g in must_agree:
            worst_used = max(worst_used, w)
    if worst_used > 1e-9:
        raise SystemExit("nr4a3_fusion_targets_confounds: the two caches produce different z for a "
                         f"gene this module reads (worst {worst_used:g}); refusing to merge.")
    merged = dict(primary_tgt)
    merged["genes"] = dict(pg)
    for g in added:
        merged["genes"][g] = sg[g]
    return merged, {
        "_what": ("gene tables unioned across the two committed caches so a gene absent from one "
                  "is still readable"),
        "n_from_primary_cache": len(pg), "n_added_from_secondary": len(added),
        "n_shared_genes_compared": len(shared),
        "n_shared_genes_disagreeing": len(disagree),
        "shared_genes_disagreeing": disagree,
        "worst_abs_z_difference_among_genes_this_module_reads": _r(worst_used, 12),
        "_guard": ("sample order and per-sample background must match exactly; every gene this "
                   "module reads must agree to 1e-9 or the merge is refused. Disagreements on "
                   "genes nothing here reads are recorded above rather than suppressed."),
    }


def _zcache(tgt, genes):
    return {g: _zrow(tgt, g) for g in genes if g in (tgt.get("genes") or {})}


def _panel_per_sample(tgt, members):
    """Mean within-sample z over the readable panel members, per sample."""
    z = _zcache(tgt, members)
    if len(z) < MIN_GROUP_N_FOR_A_CONTRAST:
        return None, sorted(z)
    per = [_mean([z[g][i] for g in z]) for i in range(tgt["n_samples"])]
    return per, sorted(z)


def _gene_contrast(zrow, a_idx, b_idx):
    """Welch contrast on one gene's z, EMC(a) vs comparator(b), floors respected."""
    return _contrast(zrow, a_idx, b_idx)


def _welch_ci(w, level=1.96):
    """A 95% CI on the difference in mean z.

    Reported because the manuscript currently gives point estimates and p-values only, and at
    n_EMC of 6 and 10 the width is the honest part of the reading. Uses the normal quantile rather
    than a t quantile: with no scipy in this lane a t quantile would have to be tabulated, and at
    df of 5-11 the normal is ANTI-conservative, so the interval is stated as approximate and the
    direction of its error is stated with it."""
    if not w or w.get("df") is None:
        return None
    se = abs(w["delta_a_minus_b"] / w["t"]) if w.get("t") else None
    if not se:
        return None
    return {"delta": w["delta_a_minus_b"],
            "approx_95_ci": [_r(w["delta_a_minus_b"] - level * se),
                             _r(w["delta_a_minus_b"] + level * se)],
            "se": _r(se),
            "_caveat": ("NORMAL-quantile interval, not a t interval. At df of 5-11 it is "
                        "ANTI-CONSERVATIVE -- the true interval is WIDER. Reported so the width "
                        "is visible at all; not to be quoted as an exact interval.")}


# ---------------------------------------------------------------------------------------------
# 1 -- COMPARATOR COMPOSITION
# ---------------------------------------------------------------------------------------------
def _comparator_composition(tgt, classes, emc, comp, by_class):
    titles = [s.get("title", "") for s in tgt["samples"]]
    out = {
        "_question": "What is actually in the comparator arm, read from the GEO sample titles?",
        "_why": ("the manuscript described one class as `fibrosarcoma`, which is the panels "
                 "module's internal bucket name. The GEO titles say `Myxofibrosarcoma`, and the "
                 "difference decides whether the comparator arm is myxoid -- which is the whole of "
                 "confound (b)."),
        "n_emc": len(emc), "n_comparator": len(comp), "classes": {},
    }
    n_myx = n_non = 0
    for cl, idx in sorted(by_class.items()):
        if cl in ("unclassified", "normal_or_reference"):
            continue
        seen = sorted({titles[i].rstrip("0123456789 ").strip() or titles[i] for i in idx})
        rec = {"n": len(idx), "geo_titles_verbatim": seen,
               "in_comparator_arm": cl != "EMC" and all(i in comp for i in idx)}
        rec.update(MYXOID_STATUS.get(cl, {"myxoid": None, "why": "NOT CLASSIFIED -- unknown, "
                                                                 "not false."}))
        out["classes"][cl] = rec
        if cl != "EMC" and rec["in_comparator_arm"]:
            if rec.get("myxoid") is True:
                n_myx += len(idx)
            elif rec.get("myxoid") is False:
                n_non += len(idx)
    out["comparator_myxoid_composition"] = {
        "n_myxoid": n_myx, "n_non_myxoid": n_non,
        "fraction_myxoid": _r(n_myx / max(1, n_myx + n_non), 3),
        "_reading": ("a comparator arm that is itself largely myxoid CONTROLS the myxoid-matrix "
                     "explanation by design; one that is not, does not."),
    }
    excluded = {c: len(i) for c, i in by_class.items()
                if c in ("unclassified", "normal_or_reference")}
    if excluded:
        ex_idx = [i for c, idx in by_class.items() if c in excluded for i in idx]
        out["excluded_from_both_arms"] = {
            "n_by_class": excluded,
            "geo_titles_verbatim": sorted({titles[i] for i in ex_idx}),
            "_why_it_matters": ("these samples are in neither arm and the manuscript did not say "
                                "what they are. On GPL6244 two of them are POOLED SKELETAL MUSCLE "
                                "RNA, which is not a nuisance -- it is the control that makes the "
                                "ENO3 muscle-admixture objection answerable."),
        }
    pools = {}
    for i, s in enumerate(tgt["samples"]):
        tok = _reference_token(s.get("annotation_verbatim", ""))
        if tok:
            pools.setdefault(tok, []).append(classes[i])
    if pools:
        out["reference_pools"] = {
            tok: {"n": len(v), "classes": dict(sorted({c: v.count(c) for c in set(v)}.items()))}
            for tok, v in sorted(pools.items())
        }
        out["reference_pools"]["_tokens"] = REFERENCE_TOKENS
        out["reference_pools"]["_why_it_matters"] = (
            "a two-colour value is a log-ratio against a reference pool. A sample ratioed against "
            "a DIFFERENT pool carries a per-gene offset that within-sample standardisation cannot "
            "remove, because standardisation removes the sample's mean and SD, not a per-gene "
            "shift. If the two arms are not pool-matched, some of the contrast is the pool.")
    return out


# ---------------------------------------------------------------------------------------------
# 2 -- MUSCLE ADMIXTURE
# ---------------------------------------------------------------------------------------------
def _muscle_admixture(tgt, classes, emc, comp, by_class):
    """Is the ENO3 signal skeletal-muscle contamination?

    THE LOGIC. ENO3 is muscle-specific beta-enolase and EMC arises in the deep soft tissue of the
    thigh, so admixed skeletal muscle is the first thing a sarcoma reviewer will propose. The
    series carries two pooled skeletal-muscle RNA samples in neither arm, which fixes the scale:
    they show what a muscle-contaminated sample looks like on this platform. The discriminating
    observation is a marker that is MORE muscle-restricted than ENO3. If the EMC arm carried
    muscle, that marker would rise too."""
    mus_idx = [i for i, s in enumerate(tgt["samples"])
               if "skeletal muscle" in (s.get("title", "") + s.get("annotation_verbatim", "")).lower()]
    if not mus_idx:
        return {"_status": "NO_MUSCLE_REFERENCE_ON_THIS_PLATFORM",
                "_means": ("this series carries no skeletal-muscle sample, so the control is not "
                           "available here. That is an absent reading, NOT a reading that the "
                           "confound is absent.")}
    out = {
        "_question": "Is the ENO3 elevation in EMC explained by admixed skeletal muscle?",
        "_method": ("every gene scored on the within-array percentile of the sample's own probe "
                    "distribution, so the muscle samples and the tumours are on one scale. The "
                    "muscle samples are in NEITHER arm and no contrast uses them; they are a "
                    "reference point, not a comparator."),
        "n_muscle_reference_samples": len(mus_idx),
        "muscle_reference_titles": [tgt["samples"][i].get("title") for i in mus_idx],
        "genes": {},
    }
    have = tgt.get("genes") or {}
    for g in CLASS_A + [m for m in MUSCLE_MARKER_CANDIDATES if m in have]:
        if g not in have:
            continue
        pct = have[g].get("array_percentile")
        if not pct:
            continue
        row = {
            "muscle_reference_mean_percentile": _r(_mean([pct[i] for i in mus_idx]), 3),
            "emc_mean_percentile": _r(_mean([pct[i] for i in emc]), 3),
            "comparator_mean_percentile": _r(_mean([pct[i] for i in comp]), 3),
            "is_muscle_marker": g in MUSCLE_MARKER_CANDIDATES,
        }
        row["emc_minus_comparator"] = _r(
            (row["emc_mean_percentile"] or 0) - (row["comparator_mean_percentile"] or 0), 3)
        out["genes"][g] = row
    marks = {g: r for g, r in out["genes"].items() if r["is_muscle_marker"]}
    top = sorted(marks.items(), key=lambda kv: -(kv[1]["muscle_reference_mean_percentile"] or 0))
    out["_reading"] = {
        "muscle_markers_read": sorted(marks),
        "most_muscle_restricted_marker": top[0][0] if top else None,
        "_how_to_read": ("compare each muscle marker's muscle-reference percentile (how "
                         "muscle-specific it is on this platform) against its EMC-minus-comparator "
                         "delta (whether the EMC arm carries it). A marker that is near the top of "
                         "the muscle array and FLAT between the tumour arms is evidence the EMC "
                         "arm does not carry muscle."),
        "_ceiling": ("this bounds admixture of DIFFERENTIATED skeletal muscle. It does not "
                     "exclude a myogenic differentiation programme in the tumour itself, which "
                     "would move a marker without any contaminating tissue being present."),
    }
    return out


# ---------------------------------------------------------------------------------------------
# 3-5 -- RESTRICTED COMPARATOR ARMS
# ---------------------------------------------------------------------------------------------
def _restricted_arms(tgt, classes, emc, comp, by_class):
    """The same contrast against sub-arms of the comparator. Nothing about EMC or the reduction
    changes, so any movement is attributable to who is in the comparator arm."""
    arms = {}
    myx = [i for i in comp if MYXOID_STATUS.get(classes[i], {}).get("myxoid") is True]
    non = [i for i in comp if MYXOID_STATUS.get(classes[i], {}).get("myxoid") is False]
    if len(myx) >= MIN_GROUP_N_FOR_A_CONTRAST:
        arms["myxoid_comparators_only"] = {
            "idx": myx, "n": len(myx),
            "_what": "comparator arm restricted to tumours whose stroma is itself myxoid."}
    if len(non) >= MIN_GROUP_N_FOR_A_CONTRAST:
        arms["non_myxoid_comparators_only"] = {
            "idx": non, "n": len(non),
            "_what": "comparator arm restricted to tumours whose stroma is not myxoid."}
    for cl, idx in sorted(by_class.items()):
        if cl in ("EMC", "unclassified", "normal_or_reference"):
            continue
        if len(idx) >= MIN_GROUP_N_FOR_A_CONTRAST and all(i in comp for i in idx):
            arms[f"class_{cl}_only"] = {
                "idx": idx, "n": len(idx),
                "_what": f"comparator arm restricted to the {cl} samples."}
    emc_tok = {_reference_token(tgt["samples"][i].get("annotation_verbatim", "")) for i in emc}
    emc_tok.discard(None)
    if len(emc_tok) == 1:
        tok = emc_tok.pop()
        matched = [i for i in comp
                   if _reference_token(tgt["samples"][i].get("annotation_verbatim", "")) == tok]
        if MIN_GROUP_N_FOR_A_CONTRAST <= len(matched) < len(comp):
            arms["reference_pool_matched_only"] = {
                "idx": matched, "n": len(matched), "reference_pool": tok,
                "_what": (f"comparator arm restricted to samples on the SAME reference pool as "
                          f"every EMC sample ({tok}). The excluded comparators are on a different "
                          f"pool, so part of their contrast is a per-gene pool offset that "
                          f"within-sample standardisation cannot remove.")}
    return arms


def _contrast_across_arms(tgt, genes, emc, arms):
    have = tgt.get("genes") or {}
    out = {}
    for g in genes:
        if g not in have:
            out[g] = {"_status": "NOT_READABLE",
                      "_means": ("no probe on this platform maps to this symbol. NOT a statement "
                                 "that the gene is unexpressed.")}
            continue
        z = _zrow(tgt, g)
        row = {}
        for name, spec in arms.items():
            w = _gene_contrast(z, emc, spec["idx"])
            if not w:
                row[name] = {"_status": "BELOW_FLOOR", "n_comparator": spec["n"]}
                continue
            # The same exact two-sided label permutation the manuscript uses for its pooled
            # contrasts, so a stratified row carries the same kind of p as the row it qualifies.
            #
            # THE OBSERVED DELTA PASSED HERE MUST BE UNROUNDED. `_welch` rounds it to 4 decimals,
            # and the permutation counts labellings with |d| >= |observed|. When rounding pushes
            # the reported value ABOVE the true one (3.5154 against 3.515391...), the real
            # labelling fails its own test, is not counted, and the enumeration returns p = 0 --
            # which is impossible for an exact test that contains the observed labelling. Measured
            # on ENO3/GPL3290 before this was fixed.
            ea = [z[i] for i in emc if z[i] is not None]
            ba = [z[i] for i in spec["idx"] if z[i] is not None]
            observed_exact = math.fsum(ea) / len(ea) - math.fsum(ba) / len(ba)
            vals = ea + ba
            perm = _label_permutation(vals, len(ea), observed_exact)
            if perm and perm["p_two_sided"] < perm["smallest_p_this_design_can_report"]:
                raise SystemExit(
                    f"nr4a3_fusion_targets_confounds: exact permutation for {g}/{name} returned "
                    f"p={perm['p_two_sided']}, below the smallest p this design can report "
                    f"({perm['smallest_p_this_design_can_report']}). An exact enumeration contains "
                    "the observed labelling, so it can never do that -- the observed statistic and "
                    "the enumerated one are not the same quantity.")
            row[name] = {"n_comparator": spec["n"], "delta": w["delta_a_minus_b"],
                         "t": w["t"], "df": w["df"], "ci": _welch_ci(w),
                         "permutation": perm}
        out[g] = row
    return out


# ---------------------------------------------------------------------------------------------
# 6 -- COVARIATE-ADJUSTED SENSITIVITY
# ---------------------------------------------------------------------------------------------
def _covariate_adjusted(tgt, genes, emc, comp, panels):
    """Regress each gene's per-sample z on a covariate proxy and recontrast on the residuals.

    THIS IS A SENSITIVITY ANALYSIS, NOT A CORRECTION. Adjusting on a proxy that is itself
    downstream of the fusion would remove real signal, and no proxy here is known to be free of
    that. The reading it supports is comparative -- which genes move and which do not -- and its
    strongest internal check is that a covariate which does NOT differ between the arms should not
    move anything, which is testable on the second platform."""
    out = {
        "_question": ("does the class-A contrast survive removing a matrix or vascular content "
                      "axis that EMC and the comparator sarcomas differ on?"),
        "_method": ("ordinary least squares of the gene's within-sample z on the panel's "
                    "per-sample mean z, over the samples in either arm; the contrast is then "
                    "recomputed on the residuals. Same samples, same reduction, same floors."),
        "_this_is_a_sensitivity_analysis": (
            "NOT a correction, and the adjusted number is not 'the real effect'. If a panel gene "
            "is itself driven by the fusion the adjustment removes real signal (over-adjustment); "
            "if the proxy is a poor measure of tumour composition it removes little. Both are "
            "possible here and neither is measured."),
        "panels": {}, "genes": {},
    }
    have = tgt.get("genes") or {}
    idx_all = [i for i in emc + comp]
    proxies = {}
    for name, members in panels.items():
        per, readable = _panel_per_sample(tgt, members)
        rec = {"members_requested": members, "members_readable": readable,
               "n_readable": len(readable)}
        if per is None:
            rec["_status"] = "BELOW_FLOOR"
            out["panels"][name] = rec
            continue
        we = _contrast(per, emc, comp)
        rec["arm_separation"] = ({"delta": we["delta_a_minus_b"], "t": we["t"], "df": we["df"]}
                                 if we else None)
        rec["_how_to_read"] = (
            "if this panel barely separates the arms, adjusting on it CANNOT move a contrast, and "
            "an unchanged result on that platform is a null control for the method rather than "
            "evidence about the gene.")
        proxies[name] = per
        out["panels"][name] = rec
    for g in genes:
        if g not in have:
            out["genes"][g] = {"_status": "NOT_READABLE"}
            continue
        z = _zrow(tgt, g)
        raw = _gene_contrast(z, emc, comp)
        row = {"raw_delta": raw["delta_a_minus_b"] if raw else None, "adjusted": {}}
        for name, per in proxies.items():
            use = [i for i in idx_all if z[i] is not None and per[i] is not None]
            ie = [i for i in use if i in emc]
            ic = [i for i in use if i in comp]
            if len(ie) < MIN_GROUP_N_FOR_A_CONTRAST or len(ic) < MIN_GROUP_N_FOR_A_CONTRAST:
                row["adjusted"][name] = {"_status": "BELOW_FLOOR"}
                continue
            mx = _mean([per[i] for i in use])
            my = _mean([z[i] for i in use])
            sxx = sum((per[i] - mx) ** 2 for i in use)
            slope = (sum((per[i] - mx) * (z[i] - my) for i in use) / sxx) if sxx else 0.0
            resid = {i: z[i] - (my + slope * (per[i] - mx)) for i in use}
            rw = _welch([resid[i] for i in ie], [resid[i] for i in ic])
            adj = rw["delta_a_minus_b"] if rw else None
            row["adjusted"][name] = {
                "delta": adj, "t": rw["t"] if rw else None, "slope_on_proxy": _r(slope),
                "fraction_of_raw_retained": (
                    _r(adj / row["raw_delta"], 3)
                    if (adj is not None and row["raw_delta"]) else None),
                "r_gene_vs_proxy": _pearson([z[i] for i in use], [per[i] for i in use]).get("r"),
            }
        out["genes"][g] = row
    return out


# ---------------------------------------------------------------------------------------------
# 7 -- MINIMUM DETECTABLE EFFECT
# ---------------------------------------------------------------------------------------------
def _minimum_detectable_effect(primary):
    """What a set score would have had to reach to clear its own size-matched null.

    WHY IT MATTERS. The manuscript's central negative is that the aggregate target set does not
    clear its null. A reader cannot tell from that whether the set is flat or the instrument is
    blunt. The null's own 97.5th percentile IS the threshold, so the distance to it is free, and it
    turns 'did not clear' into a bounded statement."""
    out = {
        "_what": ("for every set the manuscript scores, the delta required to clear the 95% band "
                  "of its own size-matched null, and how far the observed delta got."),
        "_why": ("a negative that does not say what it could have detected is not interpretable. "
                 "This is a DETECTABILITY threshold on this instrument at these arm sizes, not a "
                 "statistical power calculation -- no alternative hypothesis is assumed."),
        "sets": {},
    }
    for name, per_plat in sorted((primary.get("set_scores") or {}).items()):
        if not isinstance(per_plat, dict):
            continue
        rec = {}
        for plat, sc in sorted(per_plat.items()):
            if not isinstance(sc, dict):
                continue
            nc = sc.get("null_calibration") or {}
            if not nc.get("computed"):
                continue
            obs = nc.get("observed_delta")
            up, dn = nc.get("null_q975"), nc.get("null_q025")
            if obs is None or up is None or dn is None:
                continue
            thr = up if obs >= 0 else dn
            rec[plat] = {
                "set_size": nc.get("set_size"), "observed_delta": obs,
                "threshold_to_clear": thr,
                "fraction_of_threshold_reached": _r(abs(obs) / abs(thr), 3) if thr else None,
                "shortfall": _r(abs(thr) - abs(obs)) if thr else None,
                "cleared": abs(obs) > abs(thr),
                "null_95_band": [dn, up],
            }
        if rec:
            out["sets"][name] = rec
    return out


# ---------------------------------------------------------------------------------------------
# 8 -- WITHIN-EMC FUSION AXIS
# ---------------------------------------------------------------------------------------------
def _within_emc_fusion_axis(tgt, emc, genes):
    """Within the EMC arm alone, does the gene track NR4A3 level?

    WHY THIS IS THE ONLY AVAILABLE FUSION-OUTPUT AXIS. Every other contrast in the manuscript
    compares EMC with something else, so it can only ever say a gene is associated with EMC. Held
    within the EMC arm, disease membership is constant, and a gene the fusion drives should track
    the fusion's own transcript.

    WHY IT IS WEAK, STATED BEFORE THE NUMBER. n is 6 and 10. NR4A3 array signal is the 3' partner
    of a chimera under a foreign promoter, not the fusion transcript, and it is not a protein
    measurement. A correlation here is not evidence of driving and its absence is not evidence
    against; at this n the interval on r spans most of its range."""
    have = tgt.get("genes") or {}
    if "NR4A3" not in have or len(emc) < MIN_GROUP_N_FOR_A_CONTRAST:
        return {"_status": "NOT_COMPUTABLE",
                "_why": ("NR4A3 is not readable on this platform, or the EMC arm is below the "
                         "floor. An absent reading is not a reading of absence.")}
    nr = _zrow(tgt, "NR4A3")
    out = {"_n_emc": len(emc), "_anchor": "NR4A3 within-sample z, EMC samples only", "genes": {},
           "_ceiling": ("n of 6-10 with no multiplicity control. A single tumour moves r "
                        "substantially. This axis is reported because it is the only one in these "
                        "data that speaks to fusion output at all, NOT because it settles "
                        "anything.")}
    for g in genes:
        if g == "NR4A3" or g not in have:
            continue
        pr = _pearson([_zrow(tgt, g)[i] for i in emc], [nr[i] for i in emc])
        out["genes"][g] = pr
    return out


# ---------------------------------------------------------------------------------------------
# AGREEMENT GUARD
# ---------------------------------------------------------------------------------------------
def _agreement_guard(tgt, plat, emc, comp, primary):
    """Every delta re-derived here must equal the manuscript's committed primary artifact.

    Without this the module could be measuring a different quantity from the paper it is meant to
    bound, and every sensitivity reading would be uninterpretable."""
    rows, worst = {}, 0.0
    have = tgt.get("genes") or {}
    for g in CLASS_A + INSTRUMENT_CONTROLS:
        ref = ((primary.get("gene_reads") or {}).get(g) or {}).get(plat)
        if not ref or g not in have:
            continue
        committed = (ref.get("null_calibration") or {}).get("observed_delta")
        if committed is None:
            em, cm = (ref.get("EMC") or {}).get("mean_z"), (ref.get("comparator") or {}).get("mean_z")
            committed = None if em is None or cm is None else round(em - cm, 4)
        w = _gene_contrast(_zrow(tgt, g), emc, comp)
        if not w or committed is None:
            continue
        d = abs(w["delta_a_minus_b"] - committed)
        worst = max(worst, d)
        rows[g] = {"re_derived": w["delta_a_minus_b"], "committed": committed,
                   "abs_difference": _r(d, 6)}
    return {"_what": ("each gene's EMC-vs-comparator delta re-derived from the cached inputs and "
                      "compared with nr4a3-fusion-targets.json"),
            "n_rows_checked": len(rows), "worst_abs_difference": _r(worst, 6),
            "agrees": worst <= 5e-4, "per_gene": rows,
            "_tolerance": "5e-4 -- the committed artifact rounds deltas to 4 decimals."}


# ---------------------------------------------------------------------------------------------
# DERIVE
# ---------------------------------------------------------------------------------------------
def derive():
    with open(PANELS_INPUTS) as fh:
        inp = json.load(fh)
    with open(PRIMARY) as fh:
        primary = json.load(fh)
    with open(FUSION_INPUTS) as fh:
        fusion_inp = json.load(fh)
    audit, panels = _provenance_audit(primary)
    res = {
        "_what": __doc__.strip().splitlines()[0],
        "_language_discipline": (
            "Nothing in this file is an efficacy, selectivity, safety, therapeutic-window or "
            "clinical-readiness claim for any agent, target or gene, and no such quantity is "
            "computed. No test here measures occupancy: nothing shows any gene being bound by any "
            "fusion protein."),
        "_inputs": {"expression": os.path.basename(PANELS_INPUTS),
                    "primary_artifact": os.path.basename(PRIMARY),
                    "_offline": ("both are committed caches; this module performs no network "
                                 "access and no GPU work.")},
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "provenance_audit": audit,
        "minimum_detectable_effect": _minimum_detectable_effect(primary),
        "platforms": {},
    }
    reads = set(CLASS_A) | set(INSTRUMENT_CONTROLS) | set(MUSCLE_MARKER_CANDIDATES)
    for members in panels.values():
        reads |= set(members)
    for plat, raw_tgt in sorted(inp["targets"].items()):
        tgt, merge = _merge_gene_sources(raw_tgt, (fusion_inp.get("targets") or {}).get(plat),
                                         reads)
        classes, emc, comp, by_class = _arms(tgt)
        arms = _restricted_arms(tgt, classes, emc, comp, by_class)
        genes = CLASS_A + INSTRUMENT_CONTROLS
        res["platforms"][plat] = {
            "platform": tgt.get("platform"),
            "gene_source_merge": merge,
            "n_samples": tgt["n_samples"], "n_emc": len(emc), "n_comparator": len(comp),
            "agreement_with_primary_artifact": _agreement_guard(tgt, plat, emc, comp, primary),
            "comparator_composition": _comparator_composition(tgt, classes, emc, comp, by_class),
            "muscle_admixture": _muscle_admixture(tgt, classes, emc, comp, by_class),
            "restricted_comparator_arms": {
                "_arms": {k: {kk: vv for kk, vv in v.items() if kk != "idx"}
                          for k, v in arms.items()},
                "per_gene": _contrast_across_arms(tgt, genes, emc, arms),
            },
            "covariate_adjusted": _covariate_adjusted(tgt, genes, emc, comp, panels),
            "within_emc_fusion_axis": _within_emc_fusion_axis(tgt, emc, genes),
        }
    bad = [p for p, v in res["platforms"].items()
           if not v["agreement_with_primary_artifact"]["agrees"]]
    if bad:
        raise SystemExit(
            "nr4a3_fusion_targets_confounds: re-derived deltas disagree with the committed primary "
            f"artifact on {bad}. REFUSING TO WRITE -- a sensitivity analysis of a different "
            "quantity from the one the paper reports is worse than none.")
    return res


def _strip_volatile(o):
    if isinstance(o, dict):
        return {k: _strip_volatile(v) for k, v in o.items() if k != "generated_utc"}
    if isinstance(o, list):
        return [_strip_volatile(v) for v in o]
    return o


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="re-derive and diff against the committed artifact; do not write")
    args = ap.parse_args()
    res = derive()
    if args.check:
        if not os.path.exists(OUT):
            print(f"confounds --check: {os.path.basename(OUT)} does not exist yet")
            return 1
        with open(OUT) as fh:
            have = json.load(fh)
        if _strip_volatile(have) == _strip_volatile(res):
            print(f"confounds --check: OK -- {os.path.basename(OUT)} is current")
            return 0
        print(f"confounds --check: DRIFT -- {os.path.basename(OUT)} disagrees with a fresh "
              f"derivation. Re-run without --check.")
        return 1
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    print(f"confounds: wrote {os.path.basename(OUT)}")
    for plat, v in sorted(res["platforms"].items()):
        g = v["agreement_with_primary_artifact"]
        print(f"  {plat:38s} EMC {v['n_emc']:2d} vs {v['n_comparator']:2d} | "
              f"agreement {g['n_rows_checked']} rows, worst |diff| {g['worst_abs_difference']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
