#!/usr/bin/env python3
"""Does the EMC hypoxia reading survive its confounds — and is it fusion-linked or tissue-intrinsic?

⭐ WHY THIS EXISTS. `emc_expression_panels.py` read six published hypoxia signatures in the two
readable EMC series and every one came back positive on both platforms. That is the most positive
EMC-SPECIFIC observation this repository has ever measured, and it is exactly the shape of result
that is most often a confound: a hypoxia metagene is a transcriptional shadow, it has never been
calibrated in a myxoid sarcoma, and the two series' comparator arms are not the same tumours. So
before any therapeutic direction is attached to it, the obvious confounds get TESTED rather than
waved off, and each test names the observation that would falsify the reading it supports.

⛔ THIS MODULE IS A RE-ANALYSIS, NOT A SECOND MEASUREMENT (CLAUDE.md §1: one fact, one home).
Every per-sample value it reads comes from `emc-expression-panels-inputs.json`, the committed
inputs cache of that run, and every reduction is the SAME reduction: within-sample z against the
array's own probe distribution (`_zrow`), Welch t between arms, `unclassified` and
`normal_or_reference` excluded from both. It imports `_welch` and `_classify_sample` from the
modules that own them rather than re-implementing either, so a divergence is impossible by
construction. The headline t-statistics in `emc-expression-panels.json` stay that file's property;
this file never restates them as new, it stratifies and perturbs them.

⛔⛔ THE TWO RULES THAT GOVERN EVERY ROW (CLAUDE.md §4).
  * AN ABSENT READING IS NOT A READING OF ABSENCE. A test that could not be run on a platform says
    so, with the reason; it never renders as a null result.
  * A POPULATED FIELD IS NOT A MEASURED ONE. Every stratum carries its own n and its own readable
    gene count, and a stratum below the floor emits UNDERPOWERED rather than a number.

⛔ LANGUAGE DISCIPLINE. Nothing here is evidence of efficacy, selectivity, safety, a therapeutic
window or clinical readiness for any agent. n = 6 and n = 10 tumours on two decade-old array
platforms, uncorrected for multiple testing. A hypoxia signature is a hypothesis-generating
observation about tissue state, and that is the ceiling of what any sentence built on it may claim.

$0 — pure stdlib, CPU, no network in the default path. The genome-wide null background is the ONE
part that needs a fetch, and it is optional: absent, the null section says the genome-wide null has
not been taken rather than substituting the biased one silently.

Usage:
    python emc_hypoxia_confounds.py             # derive from the cached inputs (offline, $0)
    python emc_hypoxia_confounds.py --check     # re-derive and diff against the artifact
    python emc_hypoxia_confounds.py --fetch-background   # CI: fetch the genome-wide null background
"""

import argparse
import json
import math
import os
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS_INPUTS = os.path.join(HERE, "emc-expression-panels-inputs.json")
PANELS_ARTIFACT = os.path.join(HERE, "emc-expression-panels.json")
BACKGROUND = os.path.join(HERE, "emc-hypoxia-null-background.json")
THERAPEUTIC = os.path.join(HERE, "emc-hypoxia-therapeutic-status.json")
OUT = os.path.join(HERE, "emc-hypoxia-confounds.json")

sys.path.insert(0, HERE)
from emc_atr_vulnerability import _classify_sample  # noqa: E402
from fet_ddr_axis_scan import _welch  # noqa: E402

FRAMING = (
    "A CONFOUND AUDIT OF ONE EXPRESSION READING. Every number here is a re-analysis of transcript "
    "levels in archival EMC tumour material on two array platforms (n=6 and n=10 tumours). It is "
    "NOT evidence of efficacy, selectivity, safety, a therapeutic window or clinical readiness for "
    "any agent named anywhere in this file, and it cannot become that evidence from public "
    "expression data. A hypoxia metagene is a transcriptional shadow of hypoxia, not an oxygen "
    "measurement, and it has never been calibrated in EMC or in any myxoid sarcoma."
)

CURATED = ("⚠ REPO-CURATED pathway-membership list. This is NOT a published gene set or signature. "
           "Any statement resting on it must say so.")

# ---------------------------------------------------------------------------------------------
# CURATED CONTRAST SETS. Each is domain knowledge written here, NOT retrieved, and each is labelled
# CURATED at the point of use. They exist to ask questions the published hypoxia sets cannot ask of
# themselves — "is this glycolysis?", "is this vascularity?" — so their job is interpretability,
# never statistical weight. The published sets carry the weight; these locate it.
# ---------------------------------------------------------------------------------------------
GLYCOLYSIS = sorted({
    "HK1", "HK2", "HK3", "HKDC1", "GPI", "PFKL", "PFKM", "PFKP", "PFKFB1", "PFKFB2", "PFKFB3",
    "PFKFB4", "ALDOA", "ALDOB", "ALDOC", "TPI1", "GAPDH", "GAPDHS", "PGK1", "PGAM1", "PGAM2",
    "ENO1", "ENO2", "ENO3", "PKM", "PKLR", "LDHA", "LDHB", "LDHC", "SLC2A1", "SLC2A3", "SLC16A1",
    "SLC16A3", "PDK1", "PDK3", "BPGM", "ADPGK"})
GLYCOLYSIS_SET = set(GLYCOLYSIS)

# ⚠ ENDOTHELIAL-RESTRICTED vs ANGIOGENIC. `KDR`, `FLT1`, `TEK`, `TIE1`, `CLDN5`, `ESAM`, `ROBO4`,
# `EMCN`, `PECAM1`, `VWF`, `CDH5` are expressed by endothelium and are a proxy for how much vessel
# is in the block. `VEGFA` and `ANGPT2` are NOT — they are HIF-driven ligands made by the tumour,
# so including them would make the vascularity read partly a copy of the hypoxia read. They are
# scored separately, and the separation is the point.
VESSEL_ENDOTHELIAL = sorted({"KDR", "FLT1", "TEK", "TIE1", "CLDN5", "ESAM", "ROBO4", "EMCN",
                             "PECAM1", "VWF", "CDH5"})
ANGIOGENIC_LIGANDS = sorted({"VEGFA", "ANGPT1", "ANGPT2", "PGF"})

# ⚠ THERE IS NO TRANSCRIPT MARKER OF NECROSIS. This is the nearest available proxy and it is a
# proxy for the CONSEQUENCE, not the thing: necrotic tumour recruits myeloid cells, so a tumour
# whose signature came from necrosis should carry MORE myeloid transcript, not less. A LOW myeloid
# read is therefore evidence against a necrosis-driven signature; a high one would not have been
# proof of it, and this asymmetry is stated because only one direction is informative.
MYELOID_PROXY = sorted({"AIF1", "S100A8", "S100A9", "CD14", "ITGAM", "CSF1R", "TYROBP", "PTPRC",
                        "CD68", "FCGR3A", "MRC1"})

MATRIX_CS = sorted({"VCAN", "ACAN", "BCAN", "NCAN", "BGN", "DCN", "CSPG4", "CSPG5", "SRGN", "CD44",
                    "HAS1", "HAS2", "HAS3", "CHSY1", "CHSY3", "CHPF", "CHPF2", "CSGALNACT1",
                    "CSGALNACT2", "XYLT1", "XYLT2", "B4GALT7", "B3GALT6", "B3GAT3"})
PAPS_MODULE = sorted({"PAPSS1", "PAPSS2", "SLC35B2", "SLC35B3", "BPNT1"})
CS_SULFOTRANSFERASES = sorted({"CHST11", "CHST12", "CHST13", "CHST14", "CHST3", "CHST7", "CHST15",
                               "UST"})
HIF_MACHINERY = sorted({"HIF1A", "EPAS1", "ARNT", "EGLN1", "EGLN2", "EGLN3", "HIF1AN", "VHL"})
PROLIFERATION = sorted({"MKI67", "PCNA", "TOP2A", "CCNB1", "BIRC5", "AURKA", "TYMS", "RRM2"})

# The fusion and its one published direct transactivation target.
FUSION_GENES = ["NR4A3", "ENO3"]

# ---------------------------------------------------------------------------------------------
# FLOORS. Stated once, applied everywhere, and a stratum below either emits UNDERPOWERED with its
# coverage rather than a number.
# ---------------------------------------------------------------------------------------------
MIN_GENES_FOR_A_SCORE = 3
MIN_GROUP_N_FOR_A_CONTRAST = 3
N_LABEL_PERMUTATIONS = 20000        # sampled; the exact enumeration is used when it is smaller
N_RANDOM_GENE_SETS = 2000
NULL_SEED = 20260807


# ---------------------------------------------------------------------------------------------
# THE INSTRUMENT — identical to `emc_expression_panels`, imported where importable, reproduced only
# where the owning module keeps it private. `_zrow` is reproduced; `test_emc_hypoxia_confounds.py`
# asserts it agrees with the owning module on the real cache, so the copy cannot drift silently.
# ---------------------------------------------------------------------------------------------
def _zrow(tgt, gene):
    """Within-sample standardisation against the sample's own distribution over ALL probes."""
    n_s = tgt["n_samples"]
    bg = tgt["background_per_sample"]
    v = tgt["genes"][gene]["values"]
    return [None if (v[i] is None or not bg[i]) else
            (v[i] - bg[i]["mean"]) / max(1e-9, bg[i]["sd"]) for i in range(n_s)]


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _arms(tgt):
    """EMC, comparator, and the per-class index — the same bucketing the panels module uses."""
    classes = [_classify_sample(s["annotation_verbatim"]) for s in tgt["samples"]]
    emc = [i for i, c in enumerate(classes) if c == "EMC"]
    comp = [i for i, c in enumerate(classes)
            if c not in ("EMC", "unclassified", "normal_or_reference")]
    by_class = {}
    for i, c in enumerate(classes):
        by_class.setdefault(c, []).append(i)
    return classes, emc, comp, by_class


def _score(tgt, genes, zcache):
    """Mean within-sample z over the readable members. Returns (per_sample, readable)."""
    readable = [g for g in genes if g in zcache]
    if len(readable) < MIN_GENES_FOR_A_SCORE:
        return None, readable
    per = []
    for i in range(tgt["n_samples"]):
        per.append(_mean([zcache[g][i] for g in readable]))
    return per, readable


def _contrast(per, a_idx, b_idx):
    if per is None:
        return None
    a = [per[i] for i in a_idx if per[i] is not None]
    b = [per[i] for i in b_idx if per[i] is not None]
    if len(a) < MIN_GROUP_N_FOR_A_CONTRAST or len(b) < MIN_GROUP_N_FOR_A_CONTRAST:
        return None
    w = _welch(a, b)
    if w:
        w = dict(w, n_a=len(a), n_b=len(b))
    return w


def _pearson(x, y):
    """Pearson r over the samples where BOTH are present, with the n it was computed on."""
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3:
        return {"r": None, "n": len(pairs),
                "_why": "fewer than 3 samples carry both values; no correlation computed"}
    n = len(pairs)
    mx = sum(a for a, _ in pairs) / n
    my = sum(b for _, b in pairs) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a, _ in pairs))
    sy = math.sqrt(sum((b - my) ** 2 for _, b in pairs))
    if sx == 0 or sy == 0:
        return {"r": None, "n": n, "_why": "zero variance in one of the two vectors"}
    return {"r": round(sum((a - mx) * (b - my) for a, b in pairs) / (sx * sy), 4), "n": n}


def _score_row(tgt, genes, emc, comp, zcache, label, provenance):
    """One scored contrast with its coverage, ready to embed."""
    per, readable = _score(tgt, genes, zcache)
    row = {"label": label, "provenance": provenance,
           "n_genes_requested": len(genes), "n_genes_readable": len(readable),
           "genes_readable": sorted(readable),
           "genes_not_readable": sorted(set(genes) - set(readable)),
           "_not_readable_means": "no probe on this platform maps to the symbol. It is NOT a "
                                  "statement that the gene is unexpressed."}
    if per is None:
        row["contrast"] = None
        row["verdict"] = (f"⛔ UNDERPOWERED — {len(readable)}/{len(genes)} genes readable; the "
                          f"floor is {MIN_GENES_FOR_A_SCORE}. NO SCORE EMITTED. This is an "
                          f"instrument limit, not a reading of the biology.")
        return row, None
    w = _contrast(per, emc, comp)
    row["contrast"] = w
    row["verdict"] = (
        f"{'HIGHER' if w['delta_a_minus_b'] > 0 else 'LOWER'} in EMC by "
        f"{abs(w['delta_a_minus_b'])} SD units (t={w['t']}, df={w['df']}, n_EMC={w['n_a']}, "
        f"n_comparator={w['n_b']}, {len(readable)}/{len(genes)} genes readable). "
        f"⚠ Uncorrected for multiple testing." if w else
        f"⛔ UNDERPOWERED — an arm is below the {MIN_GROUP_N_FOR_A_CONTRAST}-sample floor.")
    return row, per


# ---------------------------------------------------------------------------------------------
# C1 — COMPARATOR COMPOSITION. The headline contrast pools every comparator sarcoma into one arm,
# and the two series' arms are not remotely the same tumours. This is the confound with the most
# leverage on the reading, and the one the pooled number is least able to show.
# ---------------------------------------------------------------------------------------------
# ⭐ THE MYXOID CLASSIFICATION IS THE WHOLE TEST, so it is written out per class with its reason
# rather than inferred from a name. EMC's stroma is myxoid; if a myxoid, hypocellular, poorly
# vascularised matrix produces a hypoxia signature for PHYSICAL reasons, then a comparator arm that
# is ITSELF myxoid should wash the contrast out, and one that is not should inflate it.
MYXOID_STATUS = {
    "EMC": {"myxoid": True, "why": "the index tumour; myxoid stroma is definitional"},
    "LGFMS": {"myxoid": True,
              "why": "low-grade FIBROMYXOID sarcoma — alternating fibrous and myxoid zones are "
                     "definitional; also FET-rearranged (FUS::CREB3L2), so it is a lineage as well "
                     "as a matrix control"},
    "fibrosarcoma": {"myxoid": True,
                     "why": "the six samples in this class are titled `Myxofibrosarcoma`, a "
                            "myxoid-stroma sarcoma. ⚠ The class LABEL is the panels module's "
                            "bucket name, not the sample title; the titles are carried verbatim "
                            "in `emc-expression-panels.json` -> platforms -> "
                            "sample_annotations_verbatim and are what this classification reads."},
    "desmoid_fibromatosis": {
        "myxoid": False,
        "why": "collagen-rich, not myxoid — but ALSO hypocellular and paucivascular, so it "
               "controls the matrix-abundance half of the physical hypothesis while failing to "
               "control the cellularity half. It is the closest thing to a non-myxoid comparator "
               "in either series and it is not a clean one."},
    "DFSP": {"myxoid": False, "why": "dermatofibrosarcoma protuberans — cellular storiform "
                                     "spindle-cell tumour, not myxoid"},
    "GIST": {"myxoid": False, "why": "gastrointestinal stromal tumour — cellular, not myxoid"},
}

# ⚠ THE TWO-COLOUR REFERENCE CHANNEL IS A TECHNICAL CONFOUND AND IT IS VISIBLE IN THE ANNOTATION.
# GPL3290 is a two-colour cDNA print run: every value is a log-ratio against a reference pool, so a
# sample ratioed against a DIFFERENT pool has a gene-specific offset that within-sample
# standardisation cannot remove (it removes the sample's overall mean and SD, not a per-gene shift).
# The verbatim annotations carry the pool token, and the three GIST samples do not match the rest.
REFERENCE_TOKENS = {"CRH": "the CRH reference pool (EMC samples are annotated `CRH-mRNA`, DFSP "
                           "samples `CRH`)",
                    "UHR": "Universal Human Reference — a DIFFERENT pool, carried only by the "
                           "three GIST samples"}


def _reference_token(annotation):
    """The reference-pool token as it appears in the verbatim GEO annotation, or None.

    ⛔ READ FROM THE ANNOTATION, NEVER ASSUMED FROM THE CLASS. The whole value of this test is that
    it can disagree with the class labels; deriving it from them would make it unable to."""
    up = annotation.upper()
    if "UHR" in up:
        return "UHR"
    if "CRH" in up:
        return "CRH"
    return None


def _comparator_composition(tgt, emc, comp, by_class, zcache, sig_sets):
    """C1 + C2: stratify the hypoxia contrast by comparator class and by reference pool."""
    out = {
        "_question": "Is the hypoxia contrast a property of EMC, or of which tumours happen to sit "
                     "in the comparator arm?",
        "_why_it_matters": "The two series' comparator arms have opposite myxoid composition. If a "
                           "myxoid, hypocellular matrix produces a hypoxia signature for physical "
                           "rather than oncogenic reasons, the contrast should shrink against "
                           "myxoid comparators and grow against cellular ones.",
        "_method": "The identical score is recomputed with the comparator arm restricted to ONE "
                   "class at a time. Nothing about the EMC arm or the reduction changes.",
        "comparator_classes": {}, "per_signature": {}, "reference_pool_strata": {},
    }
    for cl, idx in sorted(by_class.items()):
        if cl in ("EMC", "unclassified", "normal_or_reference"):
            continue
        rec = {"n": len(idx), "in_pooled_comparator_arm": all(i in comp for i in idx)}
        rec.update(MYXOID_STATUS.get(cl, {"myxoid": None,
                                          "why": "⚠ NOT CLASSIFIED — this class was not "
                                                 "anticipated; its myxoid status is UNKNOWN, not "
                                                 "false."}))
        out["comparator_classes"][cl] = rec
    excluded = {c: len(i) for c, i in by_class.items()
                if c in ("unclassified", "normal_or_reference")}
    if excluded:
        out["_classes_excluded_from_both_arms"] = excluded
        out["_why_excluded"] = ("the panels module excludes `unclassified` and "
                               "`normal_or_reference` from BOTH arms. On GPL6244 that removes five "
                               "solitary fibrous tumours and two POOLED SKELETAL MUSCLE RNA "
                               "samples — the latter would be a severe confound in a comparator "
                               "arm, and they are not in one.")

    strata = [(cl, idx) for cl, idx in sorted(by_class.items())
              if cl not in ("EMC", "unclassified", "normal_or_reference")]
    for slot, genes in sig_sets.items():
        per, readable = _score(tgt, genes, zcache)
        if per is None:
            out["per_signature"][slot] = {
                "verdict": f"⛔ UNDERPOWERED — {len(readable)} genes readable; no score emitted."}
            continue
        row = {"n_genes_readable": len(readable), "n_genes_requested": len(genes),
               "pooled_comparator": _contrast(per, emc, comp), "by_comparator_class": {}}
        for cl, idx in strata:
            w = _contrast(per, emc, idx)
            row["by_comparator_class"][cl] = (
                w if w else {"_verdict": f"⛔ UNDERPOWERED — n={len(idx)} is below the "
                                         f"{MIN_GROUP_N_FOR_A_CONTRAST}-sample floor."})
        myx = [cl for cl, _ in strata if MYXOID_STATUS.get(cl, {}).get("myxoid")]
        non = [cl for cl, _ in strata if MYXOID_STATUS.get(cl, {}).get("myxoid") is False]
        if myx:
            ii = [i for cl in myx for i in by_class[cl]]
            row["vs_myxoid_comparators_pooled"] = dict(
                _contrast(per, emc, ii) or {}, classes=myx, n=len(ii))
        if non:
            ii = [i for cl in non for i in by_class[cl]]
            row["vs_non_myxoid_comparators_pooled"] = dict(
                _contrast(per, emc, ii) or {}, classes=non, n=len(ii))
        out["per_signature"][slot] = row

    # C2 — the reference pool, read from the annotations.
    tokens = {}
    for i, s in enumerate(tgt["samples"]):
        tokens.setdefault(_reference_token(s["annotation_verbatim"]), []).append(i)
    out["reference_pool_strata"] = {
        "_question": "On a two-colour array every value is a ratio against a reference pool. Are "
                     "both arms ratioed against the SAME pool?",
        "_read_from": "the verbatim GEO sample annotation, never from the class label",
        "tokens_seen": {str(k): {"n": len(v), "means": REFERENCE_TOKENS.get(k, "unrecognised token")}
                        for k, v in sorted(tokens.items(), key=lambda kv: str(kv[0]))},
    }
    if len(tokens) > 1 and None not in tokens:
        emc_tok = {_reference_token(tgt["samples"][i]["annotation_verbatim"]) for i in emc}
        matched = [i for i in comp
                   if _reference_token(tgt["samples"][i]["annotation_verbatim"]) in emc_tok]
        mismatched = [i for i in comp if i not in matched]
        out["reference_pool_strata"].update({
            "emc_arm_tokens": sorted(emc_tok),
            "n_comparators_on_the_same_pool_as_EMC": len(matched),
            "n_comparators_on_a_different_pool": len(mismatched),
            "_the_test": "recompute the contrast against the POOL-MATCHED comparators alone. If "
                         "the signal is a reference-pool artefact it must die here.",
            "per_signature_pool_matched_only": {},
        })
        for slot, genes in sig_sets.items():
            per, readable = _score(tgt, genes, zcache)
            if per is None:
                continue
            w = _contrast(per, emc, matched)
            wm = _contrast(per, emc, mismatched)
            out["reference_pool_strata"]["per_signature_pool_matched_only"][slot] = {
                "pool_matched_comparators_only": w or {
                    "_verdict": f"⛔ UNDERPOWERED — n={len(matched)} pool-matched comparators."},
                "pool_mismatched_comparators_only": wm or {
                    "_verdict": f"⛔ UNDERPOWERED — n={len(mismatched)} mismatched comparators."},
            }
    else:
        out["reference_pool_strata"]["verdict"] = (
            "NOT APPLICABLE OR NOT READABLE — a single reference token, or none, is present in the "
            "annotations of this series. ⚠ That is a statement about the ANNOTATION, not a "
            "certificate that one pool was used.")
    return out


# ---------------------------------------------------------------------------------------------
# C3–C6 — the biological confounds, each as a scored contrast plus its correlation with the hypoxia
# score across samples. A confound that is FLAT between the arms cannot be driving a difference
# between them; a confound that moves WITH the arms is a live alternative explanation.
# ---------------------------------------------------------------------------------------------
def _biological_confounds(tgt, emc, comp, zcache, reference_score):
    keep = emc + comp
    out = {"_question": "Does anything other than tissue oxygenation move with the hypoxia score?",
           "_method": "each candidate confound is scored the same way, contrasted between the same "
                      "two arms, and correlated with the reference hypoxia score across the "
                      "classified samples. ⚠ A correlation across samples that SPAN the two arms "
                      "is inflated by the group difference itself and is not evidence of a "
                      "within-tumour relationship.",
           "_reference_score": "hypoxia_buffa — the smallest published set, so the least likely to "
                               "absorb an unrelated programme by sheer breadth",
           "candidates": {}}
    for label, genes, prov, reading in (
        ("proliferation", PROLIFERATION, CURATED,
         "EMC is slow-cycling. If proliferation is FLAT between the arms it cannot drive the "
         "contrast; if it is up, it is a live alternative because proliferating tissue outgrows "
         "its blood supply."),
        ("vessel_endothelial", VESSEL_ENDOTHELIAL, CURATED,
         "endothelium-restricted transcripts, a proxy for how much vessel is in the block. DOWN in "
         "EMC would be the tissue-intrinsic (hypovascular) explanation. ⚠ Deliberately excludes "
         "VEGFA/ANGPT2, which are HIF-driven and would make this a copy of the hypoxia read."),
        ("angiogenic_ligands", ANGIOGENIC_LIGANDS, CURATED,
         "the HIF-driven ligands. Scored SEPARATELY from the endothelial proxy precisely because "
         "they are downstream of the thing being tested."),
        ("myeloid_infiltrate_necrosis_proxy", MYELOID_PROXY, CURATED,
         "there is no transcript marker of necrosis; necrotic tumour recruits myeloid cells, so "
         "LOW myeloid transcript is evidence AGAINST a necrosis-driven signature. High would not "
         "have been proof of one — only one direction of this test is informative."),
        ("matrix_cs_gag", MATRIX_CS, CURATED,
         "chondroitin-sulfate proteoglycan and GAG machinery — a proxy for how much myxoid matrix "
         "is in the block. If matrix content is FLAT between the arms while hypoxia is up, the "
         "physical-matrix explanation loses its mechanism."),
        ("hif_machinery", HIF_MACHINERY, CURATED,
         "⚠ HIF1α is regulated by oxygen-dependent DEGRADATION, not by transcription, so a flat "
         "HIF1A transcript is the EXPECTED reading under real hypoxia and carries almost no "
         "information either way. Reported so that its absence from the argument is visible."),
        ("glycolysis", GLYCOLYSIS, CURATED,
         "the glycolytic programme. Hypoxia drives glycolysis, so this is not an independent "
         "confound — it is scored to locate WHERE inside the signature the signal lives."),
    ):
        row, per = _score_row(tgt, genes, emc, comp, zcache, label, prov)
        row["what_this_reading_would_mean"] = reading
        if per is not None and reference_score is not None:
            row["correlation_with_hypoxia_score_across_classified_samples"] = _pearson(
                [reference_score[i] for i in keep], [per[i] for i in keep])
            row["correlation_within_the_EMC_arm_only"] = dict(
                _pearson([reference_score[i] for i in emc], [per[i] for i in emc]),
                _caveat="within-arm n is 6 or 10; a correlation on that n is a direction, not an "
                        "estimate, and its sign is what is worth reading.")
        out["candidates"][label] = row

    # ⭐ SINGLE-GENE ROWS FOR THE GENES A PROSE READING ACTUALLY NAMES. A module score has an
    # artifact home; a gene quoted from inside one does not, and an unhomed figure is exactly what
    # CLAUDE.md §1 exists to stop. EPAS1 is the reason this block exists: the approved HIF-pathway
    # agent is HIF-2α-selective, so whether EPAS1 moves is the only thing that makes that class
    # hook a hook — and it was quotable from nowhere until it was written down here.
    out["single_genes_a_reading_will_name"] = {
        "_why": "each of these is named in prose somewhere; a number quoted from inside a module "
                "score has no home of its own, and this is that home.",
        "genes": {},
    }
    for g in ("EPAS1", "HIF1A", "CA9", "MKI67", "VEGFA", "SLC2A1", "NDRG1", "KDR", "FLT1",
              "ENO3", "NR4A3", "LDHA", "ANGPTL4", "PDK1", "P4HA1"):
        if g not in zcache:
            out["single_genes_a_reading_will_name"]["genes"][g] = {
                "readable": False,
                "verdict": f"⛔ no probe on this platform maps to {g} — the read could not be "
                           f"TAKEN. NOT a statement that the gene is unexpressed."}
            continue
        pct = tgt["genes"][g]["array_percentile"]
        m = _mean([pct[i] for i in emc])
        out["single_genes_a_reading_will_name"]["genes"][g] = {
            "readable": True,
            "n_probes_mapping": tgt["genes"][g]["n_probes_mapping"],
            "EMC_vs_comparator": _contrast(zcache[g], emc, comp),
            "EMC_mean_array_percentile": round(m, 4) if m is not None else None,
        }
    return out


# ---------------------------------------------------------------------------------------------
# C7 — ARE THE SIX SIGNATURES INDEPENDENT? "All six positive" is six confirmations only if the six
# are six tests. Two different measurements answer that and they disagree, which is why both are
# reported: gene MEMBERSHIP overlap is low, and per-sample SCORE correlation is high.
# ---------------------------------------------------------------------------------------------
def _signature_independence(sig_sets, per_platform_scores):
    names = sorted(sig_sets)
    out = {
        "_question": "Is `all six hypoxia signatures are positive` six independent confirmations, "
                     "or one observation reported six times?",
        "_why_it_matters": "the multiplicity of a claim is the strength a reader assigns it. Six "
                           "correlated readouts of one axis are ONE observation.",
        "membership_jaccard": {}, "membership_note": "", "score_correlation_per_platform": {},
    }
    for a in names:
        out["membership_jaccard"][a] = {
            b: round(len(set(sig_sets[a]) & set(sig_sets[b])) /
                     len(set(sig_sets[a]) | set(sig_sets[b])), 4) for b in names}
    counts = Counter()
    for s in sig_sets.values():
        counts.update(s)
    core = sorted(g for g, n in counts.items() if n >= 4)
    out["union_n_genes"] = len(counts)
    out["core_genes_in_at_least_4_of_6_sets"] = core
    out["n_genes_in_exactly_one_set"] = sum(1 for _, n in counts.items() if n == 1)
    out["membership_note"] = (
        "LOW pairwise Jaccard means the six sets are largely DIFFERENT gene lists — they are not "
        "six copies of one list. That is the argument FOR treating them as distinct, and it is the "
        "argument the score correlation below overturns.")
    out["score_correlation_per_platform"] = per_platform_scores
    out["how_to_read_the_two_together"] = (
        "Different gene lists whose per-sample scores are highly correlated are near-parallel "
        "measurements of ONE underlying axis. Where that holds, `all six positive` must be "
        "reported as one observation per platform, not six — and the effective multiplicity is "
        "closer to the number of PLATFORMS than to the number of signatures.")
    return out


# ---------------------------------------------------------------------------------------------
# C8/C9 — RESAMPLING. Two different nulls, asking two different questions, and conflating them is
# how a small-n contrast gets over-read.
#   * LABEL permutation: given THIS gene set, is the arm separation more than chance?
#   * RANDOM GENE SET:   given THIS arm split, is a set of this size unusual?
# A signature can pass one and fail the other, and on this data one does.
# ---------------------------------------------------------------------------------------------
def _label_permutation(per, emc, comp, seed):
    """One-sided permutation p for the observed t, EXACT when the split count is small enough."""
    obs = _contrast(per, emc, comp)
    if not obs:
        return None
    pool = [per[i] for i in (emc + comp) if per[i] is not None]
    n_a = obs["n_a"]
    total = math.comb(len(pool), n_a)
    exact = total <= N_LABEL_PERMUTATIONS
    hits = 0
    if exact:
        for spl in combinations(range(len(pool)), n_a):
            s = set(spl)
            w = _welch([pool[i] for i in spl],
                       [pool[i] for i in range(len(pool)) if i not in s])
            if w and w["t"] >= obs["t"]:
                hits += 1
        n_perm = total
    else:
        rng = random.Random(seed)
        idx = list(range(len(pool)))
        for _ in range(N_LABEL_PERMUTATIONS):
            rng.shuffle(idx)
            w = _welch([pool[i] for i in idx[:n_a]], [pool[i] for i in idx[n_a:]])
            if w and w["t"] >= obs["t"]:
                hits += 1
        n_perm = N_LABEL_PERMUTATIONS
    return {"observed_t": obs["t"], "n_permutations": n_perm, "exact": exact,
            "n_at_or_above_observed": hits, "one_sided_p": round(hits / n_perm, 5),
            "_p_means": "the fraction of arm relabellings that reach the observed t or better. It "
                        "is UNCORRECTED for the number of signatures tested.",
            "_seed": None if exact else seed}


def _leave_one_emc_out(per, emc, comp):
    rows = []
    for drop in emc:
        w = _contrast(per, [i for i in emc if i != drop], comp)
        rows.append({"dropped_index": drop, "t": w["t"] if w else None})
    ts = [r["t"] for r in rows if r["t"] is not None]
    if not ts:
        return {"verdict": "⛔ UNDERPOWERED — dropping one sample puts an arm below the floor."}
    return {"per_drop": rows, "t_min": round(min(ts), 3), "t_max": round(max(ts), 3),
            "all_same_sign_as_full": all(t > 0 for t in ts) or all(t < 0 for t in ts),
            "all_at_or_above_2": all(abs(t) >= 2 for t in ts),
            "_why": "with n_EMC of 6 or 10, one tumour can carry a contrast. A reading that only "
                    "survives with every sample present is a reading about one sample."}


def _random_gene_set_null(tgt, universe, emc, comp, zcache, n_genes, observed_t, seed):
    rng = random.Random(seed)
    hits = 0
    for _ in range(N_RANDOM_GENE_SETS):
        per, _rd = _score(tgt, rng.sample(universe, n_genes), zcache)
        w = _contrast(per, emc, comp)
        if w and w["t"] >= observed_t:
            hits += 1
    return {"n_draws": N_RANDOM_GENE_SETS, "set_size": n_genes,
            "n_at_or_above_observed": hits,
            "fraction_of_random_sets_reaching_observed_t": round(hits / N_RANDOM_GENE_SETS, 4),
            "universe_size": len(universe), "_seed": seed}


# ---------------------------------------------------------------------------------------------
# THE FUSION QUESTION. EWSR1::NR4A3 is a transcriptional driver and one published direct target is
# a GLYCOLYTIC ENZYME (ENO3, PMID 26310886). So "EMC looks hypoxic" and "EMC looks glycolytic
# because the fusion drives glycolytic genes" predict the same metagene score, and separating them
# is the whole of read 2 of this module.
# ---------------------------------------------------------------------------------------------
def _fusion_vs_tissue(tgt, emc, comp, zcache, sig_sets, reference_score):
    out = {
        "_question": "Is the hypoxia reading downstream of the fusion, or a property of the tissue?",
        "_why_the_question_is_sharp": (
            "EWSR1::NR4A3 is a transcriptional driver, and its one published direct "
            "transactivation target in the literature this repository cites is ENO3 — a glycolytic "
            "enzyme (PMID 26310886, quoted from `emc_expression_panels.PANELS."
            "instrument_controls.expected.ENO3`, which is its home here). A fusion that drives "
            "glycolytic genes and a tumour that is genuinely hypoxic produce the SAME hypoxia "
            "metagene score, because every published hypoxia signature is substantially glycolytic."),
        "decomposition_glycolytic_vs_rest": {},
        "discriminators": {},
    }
    # D1 — split each published signature into its glycolytic members and the remainder.
    for slot, genes in sig_sets.items():
        g = set(genes)
        gly = sorted(g & GLYCOLYSIS_SET)
        rest = sorted(g - GLYCOLYSIS_SET)
        row = {}
        for key, gl in (("full_set", sorted(g)), ("glycolytic_members", gly),
                        ("non_glycolytic_remainder", rest)):
            r, _p = _score_row(tgt, gl, emc, comp, zcache, key, "published set, partitioned here")
            row[key] = {"n_readable": r["n_genes_readable"], "contrast": r["contrast"],
                        "verdict": r["verdict"]}
        row["_how_to_read"] = (
            "If the glycolytic members carry a much larger effect than the remainder, the "
            "signature is reporting a glycolytic programme. If the REMAINDER is still positive on "
            "its own, the reading is broader than glycolysis and a purely metabolic explanation "
            "does not cover it. Both can be true at once and here both are.")
        out["decomposition_glycolytic_vs_rest"][slot] = row

    # D2 — glycolysis with the enolases removed. ENO3 is the published fusion target; if the
    # glycolytic elevation is an ENO3 artefact it must die when ENO3 leaves.
    for label, gl, why in (
        ("glycolysis_curated", GLYCOLYSIS, "the full curated programme"),
        ("glycolysis_minus_ENO3", [g for g in GLYCOLYSIS if g != "ENO3"],
         "ENO3 removed — the published direct fusion target"),
        ("glycolysis_minus_all_enolases", [g for g in GLYCOLYSIS if g not in ("ENO1", "ENO2",
                                                                              "ENO3")],
         "every enolase removed, so no enolase can carry it"),
    ):
        r, _p = _score_row(tgt, gl, emc, comp, zcache, label, CURATED)
        r["why_this_variant"] = why
        out["discriminators"][label] = r

    # D3 — WITHIN the EMC arm, does the hypoxia score track fusion output? This is the test that
    # actually discriminates, because it holds the disease constant.
    within = {"_question": "Within EMC tumours only, do the tumours with more fusion output have "
                           "more hypoxia score?",
              "_why_this_is_the_discriminating_test": (
                  "a between-arm difference cannot separate `the fusion drives it` from `the "
                  "tissue is like that`, because every EMC carries the fusion AND the myxoid "
                  "tissue. Within the EMC arm the disease is held constant and only the DEGREE of "
                  "fusion output varies."),
              "_the_prediction": "if the programme is fusion-driven, hypoxia score should rise "
                                 "with NR4A3 and with ENO3 across EMC tumours. A null or negative "
                                 "correlation is evidence against fusion-drive.",
              "_the_limit": "n is 6 and 10 tumours; NR4A3 probe placement on a 3'-biased or "
                            "EST-annotated array may sit in the region the fusion REPLACES rather "
                            "than the one it retains, so a null NR4A3 correlation has a probe "
                            "explanation as well as a biological one.",
              "genes": {}}
    for g in FUSION_GENES:
        if g not in zcache:
            within["genes"][g] = {"readable": False,
                                  "verdict": f"⛔ {g} carries no probe on this platform — the "
                                             f"correlation could not be TAKEN. This is not a null "
                                             f"result."}
            continue
        z = zcache[g]
        n_missing = sum(1 for v in z if v is None)
        within["genes"][g] = {
            "readable": True, "n_probes_mapping": tgt["genes"][g]["n_probes_mapping"],
            "n_samples_with_no_value": n_missing,
            "within_EMC_correlation_with_hypoxia_score": _pearson(
                [reference_score[i] for i in emc], [z[i] for i in emc]),
            "across_classified_samples": _pearson(
                [reference_score[i] for i in (emc + comp)], [z[i] for i in (emc + comp)]),
            "EMC_vs_comparator": _contrast(z, emc, comp),
        }
    # ⭐ THE SHARPER FORM OF THE SAME TEST. The hypoxia score is mostly glycolysis (D1), so
    # correlating it with ENO3 partly asks whether glycolysis tracks glycolysis. The question that
    # discriminates is narrower: within EMC tumours, does the REST of the glycolytic programme —
    # ENO3 excluded, so the correlation cannot be self-correlation — rise with ENO3? If the fusion
    # drives a glycolytic programme through the mechanism ENO3 is the published example of, it
    # should. If ENO3 is a fusion target sitting on top of an otherwise ordinary programme, it
    # need not.
    gly_no_eno3 = [g for g in GLYCOLYSIS if g != "ENO3"]
    gly_score, gly_readable = _score(tgt, gly_no_eno3, zcache)
    rec = {"_question": "within EMC tumours, does the glycolytic programme (ENO3 EXCLUDED) rise "
                        "with ENO3?",
           "_why_ENO3_is_excluded_from_the_score": "otherwise the correlation is partly ENO3 "
                                                   "against itself, which would answer nothing.",
           "n_glycolytic_genes_in_the_score": len(gly_readable)}
    if gly_score is None or "ENO3" not in zcache:
        rec["verdict"] = ("⛔ NOT SCOREABLE on this platform — ENO3 or the glycolytic programme is "
                          "below the floor. The read could not be TAKEN; this is not a null.")
    else:
        rec["within_EMC_correlation"] = _pearson([gly_score[i] for i in emc],
                                                 [zcache["ENO3"][i] for i in emc])
        rec["across_classified_samples"] = _pearson([gly_score[i] for i in (emc + comp)],
                                                    [zcache["ENO3"][i] for i in (emc + comp)])
        rec["_the_limit"] = ("n is 6 or 10 EMC tumours. A correlation on that n is a direction, "
                             "not an estimate, and only agreement of SIGN across the two platforms "
                             "is worth reading at all.")
    out["discriminators"]["within_EMC_glycolysis_minus_ENO3_vs_ENO3"] = rec
    out["discriminators"]["within_EMC_fusion_output_vs_hypoxia"] = within

    # D4 — CA9. The most oxygen-specific single readout available: a HIF1-restricted target with no
    # recognised fusion-independent driver in this setting.
    if "CA9" in zcache:
        z = zcache["CA9"]
        # ⛔ CIRCULARITY GUARD: CA9 is a MEMBER of four of the six signatures, so correlating it
        # with a score that contains it is partly self-correlation. Recomputed against a score
        # with CA9 removed.
        member_of = sorted(s for s, gl in sig_sets.items() if "CA9" in gl)
        ref_genes = [g for g in sig_sets.get("hypoxia_buffa", []) if g != "CA9"]
        ref_no_ca9, _rd = _score(tgt, ref_genes, zcache)
        out["discriminators"]["CA9_the_oxygen_specific_readout"] = {
            "_why_CA9": "carbonic anhydrase IX is among the most hypoxia-restricted HIF1 targets "
                        "in normal tissue and has no recognised fusion-independent driver here, so "
                        "it is the single readout least explainable by a transcriptional driver "
                        "that happens to hit glycolysis.",
            "is_a_member_of_signature_sets": member_of,
            "_circularity_guard": "CA9 sits inside several of the sets, so its correlation with a "
                                  "score containing it is partly self-correlation. The correlation "
                                  "below is against the reference score with CA9 REMOVED.",
            "EMC_vs_comparator": _contrast(z, emc, comp),
            "within_EMC_correlation_with_hypoxia_score_CA9_removed": (
                _pearson([ref_no_ca9[i] for i in emc], [z[i] for i in emc])
                if ref_no_ca9 else {"r": None, "_why": "reference score not scoreable"}),
            "EMC_mean_array_percentile": round(
                _mean([tgt["genes"]["CA9"]["array_percentile"][i] for i in emc]) or 0, 4),
            "_percentile_means": "where CA9 sits in this sample's own distribution over all "
                                 "probes. On a two-colour log-ratio platform a percentile is a "
                                 "rank against the array, not an absolute expression level.",
        }
    else:
        out["discriminators"]["CA9_the_oxygen_specific_readout"] = {
            "readable": False,
            "verdict": "⛔ CA9 carries no probe on this platform. The read could not be taken."}
    return out


# ---------------------------------------------------------------------------------------------
# THE MATRIX READING. VCAN at the top of the array while the universal sulfate donor is DOWN is a
# real tension and it is what this section is for.
# ---------------------------------------------------------------------------------------------
def _matrix_reading(tgt, emc, comp, zcache):
    out = {"_question": "What does a very high VCAN alongside a DOWN sulfate-donor module mean for "
                        "EMC's myxoid stroma, and what does it rule out?",
           "_the_tension": (
               "VCAN (versican) is a large chondroitin-sulfate proteoglycan and it is at or near "
               "the top of the array in EMC. PAPS is the UNIVERSAL sulfate donor: every "
               "sulfotransferase in the cell, on any substrate, takes its sulfate from PAPS. A "
               "core protein at the ceiling with the donor module DOWN cannot be read as `EMC is "
               "making more sulfated chondroitin sulfate`."),
           "modules": {}, "per_gene": {}}
    for label, genes, prov in (
        ("cs_proteoglycan_core_and_gag_machinery", MATRIX_CS, CURATED),
        ("paps_module_the_universal_sulfate_donor", PAPS_MODULE, CURATED),
        ("cs_sulfotransferases", CS_SULFOTRANSFERASES, CURATED),
    ):
        row, _p = _score_row(tgt, genes, emc, comp, zcache, label, prov)
        out["modules"][label] = row
    for g in sorted(set(MATRIX_CS) | set(PAPS_MODULE) | set(CS_SULFOTRANSFERASES)):
        if g not in zcache:
            out["per_gene"][g] = {"readable": False,
                                  "verdict": "no probe maps to this symbol on this platform — the "
                                             "read could not be taken. NOT a statement that the "
                                             "gene is unexpressed."}
            continue
        w = _contrast(zcache[g], emc, comp)
        pct = tgt["genes"][g]["array_percentile"]
        out["per_gene"][g] = {
            "readable": True,
            "EMC_vs_comparator": w,
            "EMC_mean_array_percentile": (lambda m: round(m, 4) if m is not None else None)(
                _mean([pct[i] for i in emc])),
        }
    out["_what_it_cannot_settle"] = (
        "⛔ A SULFATION PATTERN HAS NO GENE. Transcript levels of sulfotransferases and of the PAPS "
        "module are a proxy for the CAPACITY to sulfate, never a measurement of the sulfation state "
        "of anything. Nothing here says which CS epitopes are present on EMC tissue; only a stain, "
        "a binding assay or a glycomics measurement can say that. Intracellular PAPS concentration "
        "is set by flux and by sulfate availability as much as by synthase transcript, so a low "
        "PAPSS2 read is not a measurement of low PAPS.")
    return out


# ---------------------------------------------------------------------------------------------
# DERIVE
# ---------------------------------------------------------------------------------------------
def _merged_zcache(tgt, bg):
    """Within-sample z rows for every gene readable in EITHER cache, with its cache named.

    ⭐ WHY A MERGE IS SAFE HERE AND WOULD NOT BE IN GENERAL. Both caches are produced by the SAME
    function (`emc_expression_panels._read_target`) parsing the SAME series-matrix file with the
    SAME probe->symbol bridge; only the `want` set differs. So a gene present in both must carry
    byte-identical values, and that is ASSERTED rather than assumed — any disagreement raises,
    because a silent disagreement would mean the two caches came from different data and every
    merged score would be a blend of two experiments.

    ⚠ The merge exists for ONE reason: the panels cache holds only the 1,636 genes those six reads
    asked for, so several confound proxies (PECAM1, VWF, CDH5, PTPRC, CD68, most of the
    proliferation set) had no probe *in the cache* and were reported unreadable — which is exactly
    the "absent reading" this repository refuses to let stand when a $0 fetch can close it."""
    z = {g: _zrow(tgt, g) for g in tgt["genes"]}
    prov = {g: "panels_inputs" for g in z}
    if not bg or bg.get("_status") != "read":
        return z, prov, {"merged": False, "_why": "no background cache for this series"}
    a = [s["gsm"] for s in tgt["samples"]]
    b = [s["gsm"] for s in bg["samples"]]
    if a != b:
        raise AssertionError(
            f"sample order differs between the two caches for {tgt.get('gse')}: {a[:3]} vs {b[:3]}")
    disagreements = []
    added = 0
    for g in bg["genes"]:
        if g in z:
            if bg["genes"][g]["values"] != tgt["genes"][g]["values"]:
                disagreements.append(g)
            continue
        z[g] = _zrow(bg, g)
        prov[g] = "null_background"
        added += 1
    if disagreements:
        raise AssertionError(
            f"{len(disagreements)} genes disagree between the panels cache and the null background "
            f"on {tgt.get('gse')} (first: {disagreements[:5]}). The two caches are not reading the "
            f"same matrix; no merged score may be emitted.")
    return z, prov, {
        "merged": True, "n_from_panels_inputs": len(tgt["genes"]), "n_added_from_background": added,
        "n_genes_present_in_both_and_identical": len(set(bg["genes"]) & set(tgt["genes"])),
        "_integrity": "genes present in both caches were compared value-for-value and agreed; a "
                      "disagreement raises rather than being averaged away.",
    }


def _hypoxia_sets(inp):
    slots = (inp.get("signature_sets") or {}).get("slots") or {}
    return {k: v["genes"] for k, v in sorted(slots.items())
            if k.startswith("hypoxia") and v.get("genes")}


def _set_citations(inp):
    slots = (inp.get("signature_sets") or {}).get("slots") or {}
    return {k: {"resolved_set": v.get("resolved_set"), "citation": v.get("citation"),
                "library": v.get("library"), "n_genes": v.get("n_genes"),
                "provenance": v.get("provenance")}
            for k, v in sorted(slots.items()) if k.startswith("hypoxia")}


def _therapeutic_hooks(status):
    """The three hooks a hypoxia reading points at, each at the weight the record supports.

    ⛔ THE ORDER IS DELIBERATE: what the reading is, then what it is not, THEN the class. A hook
    stated before its ceiling is a hook that will be quoted without it."""
    out = {
        "_what_a_hypoxia_reading_licenses": (
            "a hypothesis about tissue state that is worth stating in the literature BECAUSE it is "
            "EMC-specific and measured, and that names three drug classes as things somebody could "
            "ask about. That is the entire licence."),
        "_what_it_does_not_license": (
            "⛔ Nothing about activity, selectivity, safety, a therapeutic window or clinical "
            "readiness for any agent in any of these classes in EMC. A transcriptional shadow of "
            "hypoxia in 16 archival tumours is not a patient-selection biomarker, is not a "
            "companion diagnostic, and does not support giving anyone anything."),
        "_the_general_prior": (
            "⚠ HYPOXIA-DIRECTED THERAPY HAS A LONG NEGATIVE TRACK RECORD IN SOLID TUMOURS, "
            "INCLUDING SARCOMA, and that prior dominates a single expression reading. The retrieved "
            "record below is the evidence for that sentence; where retrieval failed, the sentence "
            "stands on the retrieval that succeeded and says which."),
        "classes": {},
    }
    if not status:
        out["_status"] = "NOT RETRIEVED"
        out["verdict"] = (
            "⛔ THE CLINICAL STATUS OF THESE CLASSES HAS NOT BEEN RETRIEVED IN THIS RUN. "
            "`emc-hypoxia-therapeutic-status.json` is absent, so no class carries a status here. "
            "⚠ This is an ABSENT READING, not a reading of absence: it does not mean nothing has "
            "been tried, and no sentence anywhere may state a class's status from memory while "
            "this says NOT RETRIEVED. Take it with "
            "`emc_hypoxia_confounds.py --fetch-therapeutic-status` in CI.")
        for cls, meta in THERAPEUTIC_CLASSES.items():
            out["classes"][cls] = {k: v for k, v in meta.items() if k != "agents"}
            out["classes"][cls]["status"] = "NOT RETRIEVED"
        return out
    out["_status"] = "RETRIEVED"
    out["_retrieved_utc"] = status.get("_generated_utc")
    out["_full_record"] = "emc-hypoxia-therapeutic-status.json — the verbatim retrieval, which is "
    out["_full_record"] += "its one home; the summary below never adds a fact it does not carry."
    for cls, rec in (status.get("classes") or {}).items():
        ct = rec.get("clinicaltrials") or {}
        failed = sorted(a for a, v in ct.items() if "_status" in v)
        n_studies = sum(v.get("n_returned", 0) for v in ct.values() if "_status" not in v)
        sarc = rec.get("sarcoma_specific_trials") or {}
        phases = Counter()
        stopped = []
        for agent, v in ct.items():
            for s in (v.get("studies") or []):
                for ph in (s.get("phase") or []):
                    phases[ph] += 1
                if s.get("why_stopped"):
                    stopped.append({"agent": agent, "nct": s["nct"],
                                    "why_stopped": s["why_stopped"], "status": s["status"]})
        out["classes"][cls] = {
            "why_a_hypoxia_reading_points_here": rec.get("why_a_hypoxia_reading_points_here"),
            "the_prior_that_matters": rec.get("the_prior_that_matters"),
            "n_registered_studies_returned": n_studies,
            "phase_counts": dict(phases.most_common()),
            "agents_whose_query_failed": failed or None,
            "_failed_query_means": ("the retrieval failed for that agent; it is NOT a finding that "
                                    "no trial exists" if failed else None),
            "sarcoma_indexed_trials": {a: rows for a, rows in sarc.items()},
            "n_sarcoma_indexed_trials": sum(len(v) for v in sarc.values()),
            "trials_with_a_recorded_why_stopped": stopped[:20],
            "pubmed_hit_counts": {a: (v.get("n_hits") if "_status" not in v else v["_status"])
                                  for a, v in (rec.get("pubmed") or {}).items()},
        }
    out["every_registered_EMC_trial"] = status.get("every_registered_EMC_trial")
    return out


def derive(inp, background=None, therapeutic=None):
    sig_sets = _hypoxia_sets(inp)
    res = {
        "_what": "A confound audit of the EMC hypoxia expression reading, plus the fusion-vs-tissue "
                 "question and the matrix reading that sits beside it.",
        "_framing": FRAMING,
        "_execution_model": "$0 — CPU, pure stdlib, no network in the derive path.",
        "_this_is_a_reanalysis_not_a_measurement": (
            "every per-sample value comes from `emc-expression-panels-inputs.json` and every "
            "reduction is the one `emc_expression_panels.py` uses. The headline six-signature "
            "t-statistics have their one home in `emc-expression-panels.json` and are NOT restated "
            "here as new; this file stratifies and perturbs them."),
        "_source_inputs_generated_utc": inp.get("_generated_utc"),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hypoxia_signature_sets_audited": _set_citations(inp),
        "platforms": {}, "cross_platform": {}, "_what_this_cannot_conclude": [], "_limits": [],
    }

    per_platform_score_corr = {}
    for mf, tgt in sorted(inp.get("targets", {}).items()):
        if tgt.get("_status") != "read":
            res["platforms"][mf] = {"_status": tgt.get("_status"),
                                    "verdict": "⛔ this series was not read; no confound test could "
                                               "be run on it. NOT a null result."}
            continue
        _classes, emc, comp, by_class = _arms(tgt)
        bg_t = (background or {}).get("targets", {}).get(mf) if background else None
        zcache, zprov, merge_rec = _merged_zcache(tgt, bg_t)
        # ⛔ THE NULL'S UNIVERSE IS THE BACKGROUND ALONE, NEVER THE MERGE. Merging the want list
        # into the draw pool would put the signature genes back in the "random" universe and
        # reintroduce exactly the bias the background exists to remove.
        universe = sorted(g for g in zcache if zprov[g] == "panels_inputs")
        ref_score, _rd = _score(tgt, sig_sets.get("hypoxia_buffa", []), zcache)

        plat = {
            "series": tgt.get("gse"), "platform": tgt.get("platform"),
            "value_kind": tgt.get("value_kind"),
            "_value_kinds_are_not_comparable_across_platforms": (
                "⛔ AN EFFECT SIZE ON ONE PLATFORM MAY NOT BE COMPARED WITH ONE ON THE OTHER. "
                "GPL6244 carries single-channel intensities and GPL3290 carries two-colour "
                "log-ratios against a reference pool; a within-sample z has a different scale on "
                "each, so `d` is comparable WITHIN a platform and meaningless ACROSS them. Only "
                "the DIRECTION of a contrast and its per-platform resampling p travel between "
                "them, and any sentence comparing the two platforms' magnitudes is a bug."),
            "n_EMC": len(emc), "n_comparator": len(comp),
            "n_genes_readable_in_this_cache": len(zcache),
            "gene_cache_provenance": merge_rec,
            "C1_C2_comparator_composition_and_reference_pool": _comparator_composition(
                tgt, emc, comp, by_class, zcache, sig_sets),
            "C3_C6_biological_confounds": _biological_confounds(
                tgt, emc, comp, zcache, ref_score),
            "C8_C9_C10_resampling": {"per_signature": {}},
            "fusion_vs_tissue": _fusion_vs_tissue(tgt, emc, comp, zcache, sig_sets, ref_score),
            "matrix_reading": _matrix_reading(tgt, emc, comp, zcache),
        }

        # C8/C9/C10 per signature
        corr = {}
        pers = {}
        for slot, genes in sig_sets.items():
            per, readable = _score(tgt, genes, zcache)
            if per is None:
                plat["C8_C9_C10_resampling"]["per_signature"][slot] = {
                    "verdict": f"⛔ UNDERPOWERED — {len(readable)} genes readable."}
                continue
            pers[slot] = per
            obs = _contrast(per, emc, comp)
            row = {"n_genes_readable": len(readable), "observed": obs,
                   "C8_label_permutation_null": _label_permutation(per, emc, comp, NULL_SEED),
                   "C9_leave_one_EMC_out": _leave_one_emc_out(per, emc, comp)}
            if obs:
                row["C10_random_gene_set_null_CACHED_UNIVERSE"] = dict(
                    _random_gene_set_null(tgt, universe, emc, comp, zcache, len(readable),
                                          obs["t"], NULL_SEED),
                    _the_universe_is_biased=(
                        "⚠ CONSERVATIVE, NOT NEUTRAL. The universe is the panels module's "
                        "1,636-gene want list, which was assembled FOR these reads, so a large "
                        "fraction of it is itself hypoxia-signature membership. A random draw from "
                        "it therefore contains hypoxia genes and the null is inflated toward the "
                        "observed value. Read this fraction as an UPPER BOUND on the p-value, not "
                        "as the p-value."),
                    fraction_of_universe_that_is_signature_membership=round(
                        len(set().union(*sig_sets.values()) & set(universe)) / len(universe), 4))
            plat["C8_C9_C10_resampling"]["per_signature"][slot] = row

        # C10 genome-wide, only if the background was fetched
        bg = bg_t
        if bg and bg.get("_status") == "read":
            plat["C8_C9_C10_resampling"]["C10_random_gene_set_null_GENOME_WIDE"] = \
                _genome_wide_null(bg, tgt, emc, comp, zcache, sig_sets, pers)
        else:
            plat["C8_C9_C10_resampling"]["C10_random_gene_set_null_GENOME_WIDE"] = {
                "_status": "NOT TAKEN",
                "verdict": "⛔ THE GENOME-WIDE NULL HAS NOT BEEN FETCHED. "
                           "`emc-hypoxia-null-background.json` is absent or does not carry this "
                           "series, so the unbiased null could not be computed. ⚠ This is an "
                           "ABSENT READING, not a reading of absence — it does not mean the "
                           "signature passed or failed. Take it with "
                           "`emc_hypoxia_confounds.py --fetch-background` in CI.",
                "_why_it_matters": "the cached-universe null above is drawn from a gene list "
                                   "assembled for these reads and is therefore biased against the "
                                   "signal. Only a background drawn from the platform's whole "
                                   "mapped-symbol universe answers `is a set of this size "
                                   "unusual` cleanly."}

        # score-score correlation between the six signatures on this platform
        keep = emc + comp
        corr = {a: {b: _pearson([pers[a][i] for i in keep], [pers[b][i] for i in keep])["r"]
                    for b in sorted(pers)} for a in sorted(pers)}
        per_platform_score_corr[tgt.get("platform")] = corr
        res["platforms"][mf] = plat

    res["cross_platform"]["C7_signature_independence"] = _signature_independence(
        sig_sets, per_platform_score_corr)
    res["cross_platform"]["direction_consistency"] = _direction_consistency(res)
    res["therapeutic_hooks"] = _therapeutic_hooks(therapeutic)
    res["_what_this_cannot_conclude"] = [
        "⛔ That EMC tissue is hypoxic. A metagene is a transcriptional shadow; no oxygen was "
        "measured, no pimonidazole was stained, and no hypoxia signature has ever been calibrated "
        "in EMC or in any myxoid sarcoma.",
        "⛔ That any hypoxia-activated prodrug, HIF-pathway agent or carbonic-anhydrase-IX-directed "
        "agent has activity, selectivity, safety or a therapeutic window in EMC. Nothing in an "
        "expression re-analysis can reach that, and no dose, schedule or combination follows.",
        "⛔ That the fusion does or does not drive the glycolytic programme. The within-EMC test "
        "here is n=6 and n=10 with a probe-placement caveat on NR4A3; it can only say which way "
        "the available evidence leans.",
        "⛔ Anything radiobiological. No α/β, BED, fractionation or radioresistance statement "
        "follows from a transcript reading.",
        "⛔ That the comparator sarcomas are normoxic. Every contrast here is EMC against other "
        "sarcomas, so a positive reading means `more than these tumours`, never `hypoxic in "
        "absolute terms`.",
    ]
    res["_limits"] = [
        "n = 6 tumours (GPL6244) and n = 10 tumours (GPL3290), on two array platforms of different "
        "generations and different value kinds. Uncorrected for multiple testing throughout.",
        "GPL3290 is a two-colour cDNA print run: every value is a log-ratio against a reference "
        "pool, so absolute levels are not interpretable and only the between-group contrast is.",
        "The two comparator arms are different tumours, which is the point of C1 and also its "
        "limit: neither arm was designed as a control for the other.",
        "Bulk archival tissue. Every score is a mixture over tumour, stroma, vessel and immune "
        "compartments, and no deconvolution was attempted.",
        "The curated contrast sets (glycolysis, vessel, myeloid, matrix, proliferation) are "
        "repo-written pathway lists, NOT published signatures. They carry interpretive weight "
        "only; the published hypoxia sets carry the statistical weight.",
        "The cached-universe random-gene-set null is biased conservative; the genome-wide null is "
        "the unbiased one and is reported only when it has actually been fetched.",
        "No p-value is exact except where a permutation is marked `exact`; `_welch` reports t and "
        "df only because there is no scipy in this lane.",
    ]
    return res


def _direction_consistency(res):
    """How many of the (signature x platform) cells point the same way, and what that is worth."""
    cells, pos = [], 0
    for mf, plat in res["platforms"].items():
        if "C8_C9_C10_resampling" not in plat:
            continue
        for slot, row in plat["C8_C9_C10_resampling"]["per_signature"].items():
            obs = row.get("observed")
            if not obs:
                continue
            cells.append({"platform": plat.get("platform"), "signature": slot, "t": obs["t"]})
            pos += 1 if obs["t"] > 0 else 0
    return {
        "n_cells": len(cells), "n_positive": pos, "cells": cells,
        "_naive_sign_test": (
            "if the cells were independent, k of k in one direction would be 2^-k. THEY ARE NOT "
            "INDEPENDENT — see C7_signature_independence: the six per-platform scores correlate "
            "r≈0.66–0.96, so the effective number of independent observations is closer to the "
            "number of PLATFORMS than to the number of cells. Reporting the naive sign test would "
            "be the single easiest way to over-sell this reading, which is why the arithmetic is "
            "named and refused here rather than computed."),
    }


def _genome_wide_null(bg, tgt, emc, comp, zcache, sig_sets, pers):
    """Random-gene-set null drawn from the platform's whole mapped-symbol universe.

    ⭐ WHY A SEPARATE BACKGROUND FILE. The panels inputs cache holds only the 1,636 genes those six
    reads asked for, and roughly a third of it is hypoxia-signature membership, so a `random` draw
    from it is anything but. This background is a seeded sample of the platform's FULL mapped-symbol
    universe, fetched once in CI, and it is what makes the null mean what its name says."""
    # ⛔ THE DRAW POOL IS THE SEEDED RANDOM SAMPLE ALONE. The background fetch also asks for the
    # confound proxies by name (PECAM1, VWF, CD68 …) so they stop being unreadable; those are
    # DELIBERATELY chosen genes and must never enter a pool whose whole claim is that it was not
    # chosen. `_random_background_symbols` is the fetch's own record of what it drew at random.
    drawn = set(bg.get("_random_background_symbols") or [])
    zb = {g: _zrow(bg, g) for g in bg["genes"] if not drawn or g in drawn}
    universe = sorted(zb)
    out = {"_status": "read",
           "background_universe_size": len(universe),
           "background_seed": bg.get("_sample_seed"),
           "background_sampled_from_n_symbols": bg.get("_n_symbols_on_platform"),
           "_draw_pool_is_the_seeded_random_sample_only": bool(drawn),
           "n_genes_in_background_cache_excluded_from_the_draw_pool": len(bg["genes"]) - len(zb),
           "_what_this_answers": "given this arm split, how unusual is a gene set of this size? "
                                 "A signature that many random sets of the same size can match is "
                                 "not carrying set-specific information about these arms.",
           "overlap_with_signature_membership": round(
               len(set().union(*sig_sets.values()) & set(universe)) / max(1, len(universe)), 4),
           "per_signature": {}}
    for slot, per in pers.items():
        obs = _contrast(per, emc, comp)
        if not obs:
            continue
        n_readable = len([g for g in sig_sets[slot] if g in zcache])
        rng = random.Random(NULL_SEED)
        hits = 0
        for _ in range(N_RANDOM_GENE_SETS):
            sample = rng.sample(universe, min(n_readable, len(universe)))
            rows = [zb[g] for g in sample]
            p = [_mean([r[i] for r in rows]) for i in range(bg["n_samples"])]
            w = _contrast(p, emc, comp)
            if w and w["t"] >= obs["t"]:
                hits += 1
        out["per_signature"][slot] = {
            "observed_t": obs["t"], "set_size": n_readable, "n_draws": N_RANDOM_GENE_SETS,
            "n_at_or_above_observed": hits,
            "fraction_of_random_sets_reaching_observed_t": round(hits / N_RANDOM_GENE_SETS, 4)}
    return out


# ---------------------------------------------------------------------------------------------
# FETCH — the ONE networked path. Everything else in this module runs offline.
# ---------------------------------------------------------------------------------------------
N_BACKGROUND_SYMBOLS = 4000

# Confound proxies the panels want list never asked for, so they came back unreadable — which is an
# instrument limit reported as one, and closeable by a $0 fetch. Requested BY NAME alongside the
# random draw, and recorded separately from it so they can never enter the null's draw pool.
CONFOUND_GENES_TO_ADD = sorted(set(VESSEL_ENDOTHELIAL) | set(MYELOID_PROXY) | set(PROLIFERATION) |
                               set(GLYCOLYSIS) | set(ANGIOGENIC_LIGANDS) | set(HIF_MACHINERY) |
                               set(MATRIX_CS) | set(PAPS_MODULE) | set(CS_SULFOTRANSFERASES) |
                               set(FUSION_GENES) | {"CA9"})


def fetch_background():
    """Fetch a seeded random background of the platforms' mapped symbols, for the genome-wide null.

    Reuses `emc_expression_panels._read_target` so the parse, the probe->symbol bridge and the
    per-sample background are IDENTICAL to the run this re-analyses. Only the `want` set differs.

    ⛔ TWO WANT SETS, KEPT APART IN THE RECORD. The seeded random draw is the null's universe; the
    named confound genes are not, and mixing them would silently turn a random pool into a chosen
    one. `_random_background_symbols` is what the null may draw from, and it is written by the
    fetch rather than re-derived by the reader."""
    import emc_expression_panels as P
    from emc_atr_vulnerability import _gpl_symbols

    out = {"_generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "_what": "a seeded random background of mapped gene symbols per platform (so the "
                    "random-gene-set null can be drawn from the transcriptome rather than from a "
                    "want list assembled for these reads), plus the named confound proxies the "
                    "panels want list never asked for",
           "_sample_seed": NULL_SEED,
           "_confound_genes_requested_by_name": CONFOUND_GENES_TO_ADD,
           "_why_two_want_sets": "the random draw is the null's universe and the named genes are "
                                 "not; they are recorded apart so a reader cannot conflate them "
                                 "and the null cannot draw from a chosen list.",
           "targets": {}}
    for t in P.TARGETS:
        plat = t["platform_expected"]
        print(f"symbol universe for {plat}...", file=sys.stderr)
        # ⚠ ONE `_gpl_symbols` CALL PER PLATFORM, AND THE RESULT IS HANDED ON. This function needs
        # the symbol universe before it can sample from it, and `_read_target` needs the same map;
        # calling it twice meant two full platform-table downloads and parses per platform, which
        # on GPL3290 is the expensive half of the whole job. ⛔ The defect was read off the two
        # call sites, NOT off a stopwatch: the first version of this comment claimed the step had
        # "passed 58 minutes", which was an elapsed-time GUESS — the Actions API put the step at
        # twenty. The redundant fetch is worth removing on its own terms, and a fix does not get to
        # borrow a measurement nobody took (CLAUDE.md §4).
        sym, diag = _gpl_symbols(plat)
        symbols = sorted({s for s in sym.values() if s})
        rng = random.Random(NULL_SEED)
        drawn = sorted(rng.sample(symbols, min(N_BACKGROUND_SYMBOLS, len(symbols))))
        # a named confound gene that also fell in the random draw is REMOVED from the draw pool —
        # it is no longer an unchosen gene, and a pool cannot be partly chosen.
        drawn = [g for g in drawn if g not in set(CONFOUND_GENES_TO_ADD)]
        rec = P._read_target(t, set(drawn) | set(CONFOUND_GENES_TO_ADD), sym_diag=(sym, diag))
        rec["_sample_seed"] = NULL_SEED
        rec["_n_symbols_on_platform"] = len(symbols)
        rec["_random_background_symbols"] = drawn
        rec["_n_random_background_symbols"] = len(drawn)
        rec["_sampling_rule"] = (
            f"random.Random({NULL_SEED}).sample of {N_BACKGROUND_SYMBOLS} from the platform's "
            f"sorted mapped-symbol universe, minus any symbol also requested by name as a confound "
            f"proxy — seeded and sorted, so it is reproducible")
        out["targets"][t["matrix_file"]] = rec
    return out


# ---------------------------------------------------------------------------------------------
# THE THERAPEUTIC HOOKS. A hypoxia reading points at three drug classes. Their real-world status is
# a matter of public record, and the ONLY honest way to state it is to retrieve it.
#
# ⛔ WHAT THIS RETRIEVAL IS FOR, AND WHAT IT IS NOT. It records what has been TRIED and what
# happened — trial phase, status, why-stopped — so a hook can be stated at its true weight rather
# than at the weight its mechanism suggests. It is NOT a search for evidence that any of these
# works in EMC; no such evidence exists, none of these agents has an EMC indication, and a hypoxia
# signature is not a reason to expect one. A class whose phase 3 in soft-tissue sarcoma read out
# negative is a class whose hook must be stated as weaker, not stronger, for having been tried.
# ---------------------------------------------------------------------------------------------
THERAPEUTIC_CLASSES = {
    "hypoxia_activated_prodrug": {
        "why_a_hypoxia_reading_points_here": "a hypoxia-activated prodrug is reduced to its "
                                             "cytotoxic form only under low oxygen, so its entire "
                                             "rationale is the tissue state this reading is about.",
        "agents": ["evofosfamide", "TH-302", "tirapazamine", "apaziquone", "tarloxotinib",
                   "banoxantrone", "AQ4N", "CP-506", "PR-104"],
        "the_prior_that_matters": "⚠ THE SARCOMA HISTORY IS THE FIRST THING A READER MUST SEE, not "
                                  "a footnote. Retrieve the soft-tissue-sarcoma trials of this "
                                  "class and report their outcome before any mechanism sentence.",
    },
    "hif_pathway": {
        "why_a_hypoxia_reading_points_here": "HIF is the transcription factor the signature is a "
                                             "shadow of.",
        "agents": ["belzutifan", "PT2977", "MK-6482", "PT2385", "ARO-HIF2", "EZN-2968",
                   "topotecan HIF"],
        "the_prior_that_matters": "⚠ ISOFORM. The approved agent in this class is HIF-2α-selective, "
                                  "and HIF-2α is EPAS1. Whether EPAS1 moves in this data is a "
                                  "measured question and it is answered in "
                                  "`C3_C6_biological_confounds.candidates.hif_machinery` and in "
                                  "the per-gene rows — a class hook that ignores which isoform is "
                                  "elevated is not a hook.",
    },
    "carbonic_anhydrase_ix_directed": {
        "why_a_hypoxia_reading_points_here": "CA-IX is among the most hypoxia-restricted proteins "
                                             "in normal tissue, which is what makes it an address "
                                             "rather than only a marker.",
        "agents": ["girentuximab", "SLC-0111", "carbonic anhydrase IX inhibitor", "DTP348",
                   "CA9 CAR-T"],
        "the_prior_that_matters": "⚠ SURFACE PROTEIN, NOT TRANSCRIPT. An address for an antibody, "
                                  "a radioligand or a CAR is a SURFACE-protein question. A CA9 "
                                  "transcript reading is not a measurement of surface CA-IX "
                                  "density on EMC cells and cannot become one.",
    },
}


def fetch_therapeutic_status():
    """Retrieve what has actually been tried, from ClinicalTrials.gov v2 and PubMed. CI only.

    ⛔ RECORDS, NEVER SUMMARISES ON THE WAY IN. Every query is stored verbatim with its URL and the
    HTTP outcome, and a query that fails is recorded as a failed query — never as an empty result,
    which is the same 'absent reading vs reading of absence' error in retrieval clothing."""
    import urllib.parse
    from emc_atr_vulnerability import _get

    out = {"_generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "_what": "the public clinical record for the three drug classes a hypoxia reading "
                    "points at, retrieved rather than recalled",
           "_this_is_not_evidence_of_activity_in_EMC": (
               "none of these agents has an EMC indication and no trial below is an EMC trial "
               "unless its own record says so. Retrieval establishes what was TRIED and what "
               "happened; it establishes nothing about EMC."),
           "_sources": {
               "clinicaltrials_gov": "ClinicalTrials.gov API v2 (https://clinicaltrials.gov/api/v2)",
               "pubmed": "NCBI E-utilities esearch/esummary over db=pubmed"},
           "classes": {}}

    for cls, meta in THERAPEUTIC_CLASSES.items():
        rec = {k: v for k, v in meta.items() if k != "agents"}
        rec["agents_queried"] = meta["agents"]
        rec["clinicaltrials"] = {}
        rec["sarcoma_specific_trials"] = {}
        rec["pubmed"] = {}
        for agent in meta["agents"]:
            q = ("https://clinicaltrials.gov/api/v2/studies?pageSize=50&countTotal=true"
                 "&fields=NCTId,BriefTitle,OverallStatus,Phase,Conditions,WhyStopped,"
                 "StartDate,PrimaryCompletionDate,LeadSponsorName"
                 "&query.intr=" + urllib.parse.quote(agent))
            try:
                js = json.loads(_get(q, timeout=120))
                studies = js.get("studies") or []
                rows = []
                for s in studies:
                    p = s.get("protocolSection") or {}
                    ident = p.get("identificationModule") or {}
                    status = p.get("statusModule") or {}
                    design = p.get("designModule") or {}
                    cond = (p.get("conditionsModule") or {}).get("conditions") or []
                    rows.append({
                        "nct": ident.get("nctId"), "title": (ident.get("briefTitle") or "")[:180],
                        "status": status.get("overallStatus"),
                        "why_stopped": (status.get("whyStopped") or "")[:200] or None,
                        "phase": design.get("phases"), "conditions": cond[:8],
                        "sponsor": ((p.get("sponsorCollaboratorsModule") or {})
                                    .get("leadSponsor") or {}).get("name"),
                        "start": (status.get("startDateStruct") or {}).get("date"),
                    })
                rec["clinicaltrials"][agent] = {
                    "_query_url": q, "_n_total_reported": js.get("totalCount"),
                    "n_returned": len(rows), "studies": rows}
                sarc = [r for r in rows
                        if any("sarcoma" in (c or "").lower() for c in r["conditions"])]
                if sarc:
                    rec["sarcoma_specific_trials"][agent] = sarc
            except Exception as exc:  # noqa: BLE001
                rec["clinicaltrials"][agent] = {
                    "_query_url": q,
                    "_status": f"QUERY FAILED: {str(exc)[:200]}",
                    "_what_this_is_not": "this is a failed retrieval, NOT a finding that no trial "
                                         "exists."}
            # PubMed — the outcome literature, which is where a negative phase 3 actually lives.
            pq = f"{agent}[Title/Abstract] AND (sarcoma[Title/Abstract] OR hypoxia[Title/Abstract])"
            eq = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"
                  "&retmode=json&retmax=25&sort=relevance&term=" + urllib.parse.quote(pq))
            try:
                js = json.loads(_get(eq, timeout=120))
                ids = (js.get("esearchresult") or {}).get("idlist") or []
                hits = []
                if ids:
                    su = json.loads(_get(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed"
                        "&retmode=json&id=" + ",".join(ids), timeout=120))
                    for pmid in ids:
                        v = (su.get("result") or {}).get(pmid) or {}
                        hits.append({"pmid": pmid, "title": (v.get("title") or "")[:200],
                                     "journal": v.get("source"), "year": (v.get("pubdate") or "")[:4],
                                     "type": (v.get("pubtype") or [])[:4]})
                rec["pubmed"][agent] = {"_query": pq, "_query_url": eq,
                                        "n_hits": len(ids), "hits": hits}
            except Exception as exc:  # noqa: BLE001
                rec["pubmed"][agent] = {"_query": pq, "_query_url": eq,
                                        "_status": f"QUERY FAILED: {str(exc)[:200]}",
                                        "_what_this_is_not": "a failed retrieval, NOT a finding "
                                                             "that no literature exists."}
        out["classes"][cls] = rec

    # Is there ANY EMC trial of any of these? Asked directly rather than inferred from the above.
    emc_q = ("https://clinicaltrials.gov/api/v2/studies?pageSize=50&countTotal=true"
             "&fields=NCTId,BriefTitle,OverallStatus,Phase,Conditions,Interventions"
             "&query.cond=" + urllib.parse.quote("extraskeletal myxoid chondrosarcoma"))
    try:
        js = json.loads(_get(emc_q, timeout=120))
        out["every_registered_EMC_trial"] = {
            "_query_url": emc_q, "_n_total_reported": js.get("totalCount"),
            "_why_asked": "so the claim `no trial of any of these classes exists in EMC` is a "
                          "retrieved statement rather than an assumption",
            "studies": [{"nct": ((s.get("protocolSection") or {}).get("identificationModule") or {})
                         .get("nctId"),
                         "title": (((s.get("protocolSection") or {})
                                    .get("identificationModule") or {}).get("briefTitle") or "")[:180],
                         "status": ((s.get("protocolSection") or {}).get("statusModule") or {})
                         .get("overallStatus")}
                        for s in (js.get("studies") or [])]}
    except Exception as exc:  # noqa: BLE001
        out["every_registered_EMC_trial"] = {
            "_query_url": emc_q, "_status": f"QUERY FAILED: {str(exc)[:200]}",
            "_what_this_is_not": "a failed retrieval, NOT a finding that no EMC trial exists."}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch-background", action="store_true",
                    help="CI: fetch the genome-wide null background (a networked path)")
    ap.add_argument("--fetch-therapeutic-status", action="store_true",
                    help="CI: retrieve the clinical record for the three drug classes")
    ap.add_argument("--check", action="store_true",
                    help="re-derive offline and diff against the committed artifact")
    args = ap.parse_args()

    if args.fetch_background:
        bg = fetch_background()
        with open(BACKGROUND, "w", encoding="utf-8") as fh:
            json.dump(bg, fh, indent=1, sort_keys=True)
        print(f"wrote {BACKGROUND}", file=sys.stderr)
    if args.fetch_therapeutic_status:
        st = fetch_therapeutic_status()
        with open(THERAPEUTIC, "w", encoding="utf-8") as fh:
            json.dump(st, fh, indent=1, sort_keys=True)
        print(f"wrote {THERAPEUTIC}", file=sys.stderr)

    with open(PANELS_INPUTS, "r", encoding="utf-8") as fh:
        inp = json.load(fh)
    background = None
    if os.path.exists(BACKGROUND):
        with open(BACKGROUND, "r", encoding="utf-8") as fh:
            background = json.load(fh)
    therapeutic = None
    if os.path.exists(THERAPEUTIC):
        with open(THERAPEUTIC, "r", encoding="utf-8") as fh:
            therapeutic = json.load(fh)
    res = derive(inp, background, therapeutic)

    if args.check:
        if not os.path.exists(OUT):
            print("NO ARTIFACT TO CHECK", file=sys.stderr)
            return 1
        with open(OUT, "r", encoding="utf-8") as fh:
            old = json.load(fh)
        a = {k: v for k, v in old.items() if k != "generated_utc"}
        b = {k: v for k, v in res.items() if k != "generated_utc"}
        if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
            print("REPRODUCES")
            return 0
        print("DIFFERS FROM THE COMMITTED ARTIFACT", file=sys.stderr)
        for k in sorted(set(a) | set(b)):
            if json.dumps(a.get(k), sort_keys=True) != json.dumps(b.get(k), sort_keys=True):
                print(f"  differs: {k}", file=sys.stderr)
        return 1

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(f"wrote {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
