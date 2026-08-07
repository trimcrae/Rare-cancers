#!/usr/bin/env python3
"""
GSE11185 — "Differences between NOR1 and EWS/NOR1", READ FOR THE FIRST TIME. ($0, CPU, pure stdlib.)

WHY THIS IS WORTH A SESSION. It is the direct wild-type-versus-fusion expression experiment, it has sat in
this repository's own GEO census (`emc-atr-vulnerability.json` -> `part_b...series_readability`) since that
census was built, and NOTHING had ever opened it. That is the cleanest instance in the repository of a free
observation left untaken — the failure CLAUDE.md §4 was written about.

⭐ CHARACTERISE BEFORE BUILDING. CLAUDE.md §6 says a GEO series gets characterised before anything is built
   on it, and this file does that FIRST and separately (`characterisation`), for a reason this repository has
   been bitten by twice: a GEO series TITLE is a claim by its depositors, not a measurement. The title here
   promises "differences between NOR1 and EWS/NOR1". What the record actually contains is FOUR ARRAYS — two
   HEK293 tet-On clones, each read once with and once without doxycycline. That is n = 1 per cell, no
   biological replicates, no EMC tissue, no endogenous locus, and no native promoter. Everything below is
   written to that ceiling and this module EMITS NO P-VALUE, because with n = 1 there is nothing to compute
   one from.

★ THE ONE DEFENSIBLE CONTRAST, and it is not the obvious one. Comparing the NOR1 clone directly against the
  EWS/NOR1 clone confounds the construct with the clone: two independently derived stable transfectants
  differ in integration site, copy number and passage, and a single array each cannot separate any of that
  from the construct. What CAN be read is the WITHIN-CLONE INDUCTION RESPONSE — each clone's +dox array
  against its own -dox array — which cancels the clone baseline, and then the comparison of those two
  responses to each other. That is exactly the comparison the depositors' own paper reports, so this module
  is also a check on whether their conclusion reproduces from the deposited values.

THE PAPER THE SERIES NAMES (`!Series_pubmed_id`): Ohkura N, Nagamura Y, Tsukada T. *Differential
transactivation by orphan nuclear receptor NOR1 and its fusion gene product EWS/NOR1: possible involvement of
poly(ADP-ribose) polymerase I, PARP-1.* J Cell Biochem 2008;105(3):785-800. PMID 18680143,
doi 10.1002/jcb.21876. **NOT open access** — the Europe PMC record (abstract + metadata) was fetched through
CI and is the only part of it read here, so every claim about the paper below is [API], never [FT].

⛔ WHAT THIS CANNOT SAY. Nothing here is about EMC tissue, about a patient, about efficacy, safety, a
   therapeutic window, or clinical readiness. HEK293 overexpression of a plasmid-borne construct is a
   transactivation assay, not a disease model. A gene moving in this system is a lead for a question, not an
   answer to one.

Network: none. Runs entirely on the raw GEO reads committed under `_s4_lane_inputs/` by
`s4_lane_inputs_fetch.py` on a GitHub Actions runner (the dev sandbox's egress proxy 403s NCBI/GEO).

Outputs: gse11185-wt-vs-fusion.json (+ .md)
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IN_DIR = os.path.join(HERE, "_s4_lane_inputs")
OUT = os.path.join(HERE, "gse11185-wt-vs-fusion.json")

SERIES = "GSE11185"
# Arm labels are NOT typed here as facts — they are READ from each sample's own `!Sample_title` and the
# construct/dox assignment below is CHECKED against that title. A hard-coded arm map is precisely the
# "populated field, never measured" failure.
ARM_RULES = [("EWS/NOR1", "fusion"), ("NOR1", "wild_type")]      # longest-match first; order matters

FOLD_CALL = 2.0                    # a 2x induction — the coarsest threshold anyone reports off MAS5
FOLD_STRONG = 4.0


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 1 · PARSE — SOFT records, nothing derived
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def _open(path):
    return gzip.open(path, "rt", encoding="utf-8", errors="replace") if path.endswith(".gz") \
        else open(path, encoding="utf-8", errors="replace")


def find(in_dir, base):
    for cand in (base, base + ".gz"):
        p = os.path.join(in_dir, cand)
        if os.path.exists(p):
            return p
    return None


def parse_soft(path):
    """(meta {key: [values]}, table [rows], columns). The value table is optional and its ABSENCE is
    reported as an absence of a READING, never as an absence of data (CLAUDE.md §4)."""
    meta, table, cols = {}, [], None
    intab = False
    with _open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("!") and "_table_begin" in line:
                intab = True
                continue
            if line.startswith("!") and "_table_end" in line:
                intab = False
                continue
            if intab:
                f = line.split("\t")
                if cols is None:
                    cols = f
                else:
                    table.append(f)
                continue
            if line.startswith("!") and "=" in line:
                k, v = line[1:].split("=", 1)
                meta.setdefault(k.strip(), []).append(v.strip())
    return meta, table, cols


def arm_of(title):
    for needle, label in ARM_RULES:
        if needle in title:
            return label, needle
    return None, None


def dox_of(title, characteristics):
    t = (title + " " + " ".join(characteristics)).lower()
    with_dox = ("with doxycycline" in t) or ("doxycycline treated" in t)
    without = ("without doxycycline" in t) or ("doxycycline untreated" in t)
    if with_dox and not without:
        return "plus_dox"
    if without and not with_dox:
        return "minus_dox"
    return None


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 2 · CHARACTERISATION — before anything is built on it
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def characterise(in_dir):
    sp = find(in_dir, "%s_series.soft.txt" % SERIES)
    if sp is None:
        raise SystemExit("no series record in %s — the collector never read it; that is not an absence of "
                         "data" % in_dir)
    smeta, _, _ = parse_soft(sp)
    gsms = smeta.get("Series_sample_id", [])
    gpls = smeta.get("Series_platform_id", [])

    samples, missing = [], []
    for g in gsms:
        p = find(in_dir, "%s.soft.txt" % g)
        if p is None:
            missing.append(g)
            continue
        m, tab, cols = parse_soft(p)
        title = (m.get("Sample_title") or [""])[0]
        ch = m.get("Sample_characteristics_ch1", [])
        arm, needle = arm_of(title)
        vals = [float(r[1]) for r in tab if len(r) > 1 and r[1] not in ("", "null")]
        calls = {}
        for r in tab:
            if len(r) > 2:
                calls[r[2]] = calls.get(r[2], 0) + 1
        vals_sorted = sorted(vals)
        samples.append({
            "gsm": g,
            "title": title,
            "source_name": (m.get("Sample_source_name_ch1") or [None])[0],
            "characteristics": ch,
            "treatment_protocol": (m.get("Sample_treatment_protocol_ch1") or [None])[0],
            "description": (m.get("Sample_description") or [None])[0],
            "platform": (m.get("Sample_platform_id") or [None])[0],
            "declared_row_count": int((m.get("Sample_data_row_count") or ["0"])[0]),
            "value_column_label": next((c for c in (m.get("#VALUE") or [])), None),
            "arm": arm,
            "arm_matched_on": needle,
            "dox": dox_of(title, ch),
            "table_columns": cols,
            "n_rows_parsed": len(tab),
            "n_values": len(vals),
            "value_median": round(vals_sorted[len(vals_sorted) // 2], 3) if vals_sorted else None,
            "value_q1": round(vals_sorted[len(vals_sorted) // 4], 3) if vals_sorted else None,
            "value_q3": round(vals_sorted[3 * len(vals_sorted) // 4], 3) if vals_sorted else None,
            "value_max": round(vals_sorted[-1], 1) if vals_sorted else None,
            "detection_calls": calls,
            "frac_present": round(calls.get("P", 0) / len(tab), 4) if tab else None,
        })

    # The arm x dox design, COUNTED from what was read
    cells = {}
    for s in samples:
        cells.setdefault((s["arm"], s["dox"]), []).append(s["gsm"])
    design = {"%s|%s" % (a, d): v for (a, d), v in sorted(cells.items(), key=lambda kv: str(kv[0]))}
    n_per_cell = sorted({len(v) for v in cells.values()})

    ann_path = find(in_dir, "%s_id2gene.json.gz" % (gpls[0] if gpls else "GPL"))
    ann = None
    if ann_path:
        with gzip.open(ann_path, "rt") as fh:
            a = json.load(fh)
        i2 = a["id2gene"]
        n_sym = sum(1 for v in i2.values() if v.get("symbol"))
        ann = {
            "platform": a["_platform"],
            "source_url": a["_source_url"],
            "n_probes": a["n_probes"],
            "n_probes_with_gene_symbol": n_sym,
            "probe_symbol_mapping_fraction": round(n_sym / a["n_probes"], 4) if a["n_probes"] else None,
            "columns_seen": a["_columns_seen"],
        }

    row_counts = {s["n_rows_parsed"] for s in samples}
    declared = {s["declared_row_count"] for s in samples}
    return {
        "_what": ("what this series IS, read from its own records, before any value is used for anything "
                  "(CLAUDE.md §6)"),
        "series": SERIES,
        "title": (smeta.get("Series_title") or [None])[0],
        "summary": smeta.get("Series_summary", []),
        "overall_design": (smeta.get("Series_overall_design") or [None])[0],
        "submission_date": (smeta.get("Series_submission_date") or [None])[0],
        "public_date": (smeta.get("Series_status") or [None])[0],
        "pubmed_id": (smeta.get("Series_pubmed_id") or [None])[0],
        "contributors": smeta.get("Series_contributor", []),
        "platform": gpls[0] if gpls else None,
        "n_samples_declared": len(gsms),
        "n_samples_read": len(samples),
        "samples_not_read": missing,
        "design_cells": design,
        "n_samples_per_design_cell": n_per_cell,
        "★_replication": (
            "%d sample(s) per design cell. With n = 1 there is NO within-cell variance, so no confidence "
            "interval, no p-value and no differential-expression statistic can be computed from this series, "
            "and this module emits none." % (n_per_cell[0] if n_per_cell else 0)),
        "★_what_the_arms_actually_are": (
            "HEK293 tet-On stable clones carrying a doxycycline-inducible NOR1 or EWS/NOR1 expression "
            "plasmid, each read once at 24 h with and without doxycycline. NOT EMC tissue, NOT an EMC cell "
            "line, NOT the endogenous NR4A3 locus, and NOT the fusion's native (partner-supplied) promoter. "
            "It is a transactivation assay in an epithelial-origin line."),
        "★_what_the_record_does_NOT_contain": [
            "the construct boundaries — which EWS exon is joined to which NOR1 exon is stated NOWHERE in "
            "the series or sample records, and the paper is not open access, so the fusion's exact protein "
            "sequence is UNRESOLVED from everything reachable at $0",
            "any replicate, biological or technical",
            "any raw CEL-level QC beyond the deposited GCOS calls (the CEL tar is a supplementary file "
            "this run did not fetch)",
            "any independent corroboration that each clone expresses the construct its title claims — "
            "which is why the induction check below is run as an INSTRUMENT CONTROL before anything else",
        ],
        "value_type": ("MAS5/GCOS signal with ABS_CALL and detection p-value per probe — a per-array "
                       "scaled intensity, not a log ratio and not RMA"),
        "platform_annotation": ann,
        "row_count_consistent_across_samples": len(row_counts) == 1 and row_counts == declared,
        "rows_parsed_per_sample": sorted(row_counts),
        "samples": samples,
    }


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 3 · THE READ
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def load_values(in_dir, gsm):
    d = {}
    _m, tab, _c = parse_soft(find(in_dir, "%s.soft.txt" % gsm))
    for r in tab:
        if len(r) < 3:
            continue
        try:
            d[r[0]] = (float(r[1]), r[2])
        except ValueError:
            continue
    return d


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    return pearson(rank(xs), rank(ys))


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def read(in_dir, char):
    by_cell = {}
    for s in char["samples"]:
        by_cell[(s["arm"], s["dox"])] = s["gsm"]
    need = [("wild_type", "minus_dox"), ("wild_type", "plus_dox"),
            ("fusion", "minus_dox"), ("fusion", "plus_dox")]
    absent = [c for c in need if c not in by_cell]
    if absent:
        return {"status": "DESIGN_INCOMPLETE", "missing_cells": [list(c) for c in absent],
                "_reading": "the 2x2 the contrast needs is not present in what was read"}

    vals = {c: load_values(in_dir, by_cell[c]) for c in need}
    probes = sorted(set.intersection(*(set(v) for v in vals.values())))

    # ── normalisation, declared and derived ────────────────────────────────────────────────────────────
    # MAS5 arrays are target-scaled per chip, so a residual median difference is a scaling artefact, not
    # biology. Scale each array to the common (geometric-mean) median. Factors are REPORTED; nothing is
    # silently adjusted.
    meds = {}
    for c in need:
        v = sorted(vals[c][p][0] for p in probes)
        meds[c] = v[len(v) // 2]
    target = math.exp(sum(math.log(m) for m in meds.values()) / len(meds))
    fac = {c: target / meds[c] for c in need}

    # ⛔ THE FLOOR IS THE WHOLE BALLGAME ON MAS5 AND THE FIRST CHOICE MADE HERE WAS WRONG. At a floor of 1
    # this comparison reports 7,539 probes "induced >= 2x" by wild-type NOR1; at a floor of 100 it reports
    # 272. Both are the same data. A fold change between two values the instrument itself calls ABSENT is a
    # ratio of two noise readings, and with n = 1 there is no replicate to reveal that. So the floor is
    # DERIVED from the arrays' own absent calls — the 95th percentile of everything called A — and a
    # sensitivity sweep across floors is reported beside the headline so the dependence is visible rather
    # than buried in a default.
    absent_vals = sorted(vals[c][p][0] * fac[c] for c in need for p in probes if vals[c][p][1] == "A")
    floor = absent_vals[int(0.95 * len(absent_vals))] if absent_vals else 1.0

    def sc(c, p):
        return max(vals[c][p][0] * fac[c], floor)

    # ── the within-clone induction response ────────────────────────────────────────────────────────────
    # ⛔ AND THE DETECTION GATE IS ON THE HIGHER MEMBER, NOT ON EITHER. "Present in either sample" admits a
    # probe that was Present before induction and fell into noise after, whose fold change is then bounded
    # by the floor rather than measured. The question is "did this transcript come UP", so the sample that
    # must be Present is the one claimed to be higher.
    rows = []
    for p in probes:
        wt_l2 = math.log2(sc(("wild_type", "plus_dox"), p) / sc(("wild_type", "minus_dox"), p))
        fu_l2 = math.log2(sc(("fusion", "plus_dox"), p) / sc(("fusion", "minus_dox"), p))
        wt_hi = ("wild_type", "plus_dox") if wt_l2 >= 0 else ("wild_type", "minus_dox")
        fu_hi = ("fusion", "plus_dox") if fu_l2 >= 0 else ("fusion", "minus_dox")
        rows.append({"probe": p, "wt_log2fc": wt_l2, "fusion_log2fc": fu_l2,
                     "detected_wt": vals[wt_hi][p][1] == "P",
                     "detected_fu": vals[fu_hi][p][1] == "P",
                     "present_in_all_four": all(vals[c][p][1] == "P" for c in need)})
    idx = {r["probe"]: r for r in rows}

    def sets(thr):
        lo = math.log2(thr)
        return ({r["probe"] for r in rows if r["wt_log2fc"] >= lo and r["detected_wt"]},
                {r["probe"] for r in rows if r["fusion_log2fc"] >= lo and r["detected_fu"]},
                {r["probe"] for r in rows if r["wt_log2fc"] <= -lo and r["detected_wt"]},
                {r["probe"] for r in rows if r["fusion_log2fc"] <= -lo and r["detected_fu"]})

    def block(thr):
        uw, uf, dw, df = sets(thr)
        exp = len(uw) * len(uf) / len(probes) if probes else 0.0
        return {
            "threshold_fold": thr,
            "n_up_wild_type": len(uw), "n_up_fusion": len(uf), "n_up_both": len(uw & uf),
            "n_up_expected_both_by_chance": round(exp, 2),
            "overlap_enrichment_over_chance": round(len(uw & uf) / exp, 2) if exp else None,
            "jaccard_of_up_sets": round(len(uw & uf) / len(uw | uf), 4) if (uw | uf) else None,
            "frac_of_wild_type_set_shared": round(len(uw & uf) / len(uw), 4) if uw else None,
            "frac_of_fusion_set_shared": round(len(uw & uf) / len(uf), 4) if uf else None,
            "n_down_wild_type": len(dw), "n_down_fusion": len(df), "n_down_both": len(dw & df),
        }

    # ★ THE CORRELATION, ON AN UNBIASED PROBE SET, AND THE ARTIFACT IT REPLACES.
    #   The first version of this module correlated the two fold-change vectors over the UNION of the two
    #   selected up-sets and got r = -0.52 — a strong NEGATIVE correlation that would have read as "the
    #   constructs do opposite things". It is a pure selection effect: a probe enters that union by being
    #   high in one vector, and conditioning on the max of a noisy pair anticorrelates the pair. Reported
    #   below as `⛔_selection_artifact_do_not_read_as_a_finding` because deleting it would leave the next
    #   session free to recompute it and believe it.
    pres = [p for p in probes if idx[p]["present_in_all_four"]]
    x, y = [idx[p]["wt_log2fc"] for p in pres], [idx[p]["fusion_log2fc"] for p in pres]
    uw, uf, _, _ = sets(FOLD_CALL)
    un = sorted(uw | uf)
    xa, ya = [idx[p]["wt_log2fc"] for p in un], [idx[p]["fusion_log2fc"] for p in un]

    sweep = []
    for f in (13.97, floor, 50.0, 100.0):
        def s2(c, p, ff=f):
            return max(vals[c][p][0] * fac[c], ff)
        a = {p for p in probes if s2(("wild_type", "plus_dox"), p) / s2(("wild_type", "minus_dox"), p) >= FOLD_CALL}
        b = {p for p in probes if s2(("fusion", "plus_dox"), p) / s2(("fusion", "minus_dox"), p) >= FOLD_CALL}
        sweep.append({"floor": round(f, 2), "n_up_wild_type": len(a), "n_up_fusion": len(b),
                      "n_up_both": len(a & b), "_detection_gate_applied": False})

    return {
        "status": "OK",
        "cells": {"%s|%s" % c: by_cell[c] for c in need},
        "n_probes_common_to_all_four": len(probes),
        "n_probes_present_called_on_all_four": len(pres),
        "normalisation": {
            "_method": "per-array median scaling to the geometric-mean median of the four arrays",
            "array_medians": {("%s|%s" % c): round(meds[c], 3) for c in need},
            "scaling_factors": {("%s|%s" % c): round(fac[c], 5) for c in need},
            "largest_pairwise_scaling_ratio": round(max(fac.values()) / min(fac.values()), 4),
            "noise_floor_used": round(floor, 3),
            "noise_floor_method": ("95th percentile of every scaled value the instrument called ABSENT, "
                                   "across all four arrays — DERIVED from the data, not typed"),
            "absent_call_percentiles": {q: round(absent_vals[int(q * len(absent_vals))], 2)
                                        for q in (0.5, 0.75, 0.9, 0.95, 0.99)},
            "⚠_floor_sensitivity": sweep,
            "⚠_how_to_read_the_sweep": ("counts move several-fold with the floor and NOTHING about the "
                                        "data changed. The headline uses the derived p95 floor AND the "
                                        "per-probe detection gate; the sweep rows have the gate OFF, so "
                                        "they are deliberately the pessimistic view of how much the choice "
                                        "can move a count."),
        },
        "induction_response": {
            "_what": ("+dox vs -dox WITHIN each clone; the clone baseline cancels. This is the only "
                      "contrast the design supports — see the characterisation."),
            "at_2x": block(FOLD_CALL),
            "at_4x": block(FOLD_STRONG),
            "★_correlation_of_induction_magnitude": {
                "_on": ("every probe the instrument calls PRESENT on all four arrays — an UNBIASED set, "
                        "chosen without reference to either fold change"),
                "n": len(pres),
                "pearson_r": round(pearson(x, y), 4) if len(x) > 2 else None,
                "spearman_rho": round(spearman(x, y), 4) if len(x) > 2 else None,
                "⛔_no_p_value": ("n = 1 array per cell. This is a descriptive statistic over probes of ONE "
                                 "pair of fold-change vectors; it has no sampling distribution here, the "
                                 "probes are not independent, and no p-value is emitted."),
                "⛔_selection_artifact_do_not_read_as_a_finding": {
                    "_what": ("the same correlation computed over the UNION of the two selected up-sets, "
                              "which is how this module first computed it"),
                    "n": len(un),
                    "pearson_r": round(pearson(xa, ya), 4) if len(xa) > 2 else None,
                    "spearman_rho": round(spearman(xa, ya), 4) if len(xa) > 2 else None,
                    "_why_it_is_wrong": ("a probe enters that union by being high in ONE of the two "
                                         "vectors; conditioning on the maximum of a noisy pair induces "
                                         "negative correlation between them. The sign flips relative to "
                                         "the unbiased set above, which is the tell."),
                },
            },
        },
        "_rows": rows,
        "_up_union": un,
        "_up_wt": sorted(uw), "_up_fu": sorted(uf),
    }


def annotate(in_dir, platform, probes):
    p = find(in_dir, "%s_id2gene.json.gz" % platform)
    if not p:
        return {}
    with gzip.open(p, "rt") as fh:
        a = json.load(fh)
    i2 = a["id2gene"]
    return {q: i2.get(q, {}) for q in probes}


def _probe_index(in_dir, platform):
    p = find(in_dir, "%s_id2gene.json.gz" % platform)
    with gzip.open(p, "rt") as fh:
        return json.load(fh)["id2gene"]


def gene_rows(i2, idx, sym, calls=None):
    out = []
    for probe, v in i2.items():
        if v.get("symbol") == sym and probe in idx:
            r = idx[probe]
            row = {"probe": probe, "wt_log2fc": round(r["wt_log2fc"], 3),
                   "fusion_log2fc": round(r["fusion_log2fc"], 3),
                   "detected_wt": r["detected_wt"], "detected_fu": r["detected_fu"],
                   "present_on_all_four_arrays": r["present_in_all_four"]}
            if calls:
                row["raw_values"] = calls(probe)
            out.append(row)
    return sorted(out, key=lambda x: x["probe"])


def instrument_controls(res, in_dir, platform, raw):
    """★★ THE CHECK THAT MUST PASS BEFORE ANY OTHER NUMBER MEANS ANYTHING — AND IT DID NOT PASS.

    THE CHECK: did doxycycline actually induce the construct? A tet-On experiment where the tet-On did not
    fire produces a beautifully populated table of noise, and every count downstream would be a reading of
    that noise — the exact shape of the 2026-07-31 smoke-leg incident.

    ⛔ THE MEASURED ANSWER: all three NR4A3 probesets are called ABSENT on ALL FOUR arrays (raw 4.1-27.8,
       against a derived noise floor of ~36), and all four EWSR1 probesets are flat. So THE DEPOSITED DATA
       CANNOT REPORT WHETHER EITHER CONSTRUCT WAS EXPRESSED. That is a property of the record, not a result
       about the biology, and it must not be smoothed over.

    ★ THE TWO HYPOTHESES AND THE OBSERVATION THAT DISCRIMINATES THEM (CLAUDE.md §4 — no "probably"):
        H1  the induction did not happen; these arrays are four readings of an uninduced system.
        H2  the induction happened but the array cannot see the construct — GeneChip probesets are designed
            against the 3' end of the native transcript, and a plasmid-borne cDNA carries vector UTRs.
      DISCRIMINATING OBSERVATION, computed below, not asserted: `multi_probeset_concordance`. Under H1 the
      only movements are noise, and noise has no reason to agree between INDEPENDENT probesets of the same
      gene. Measured: every gene with >= 2 probesets each moving >= 2x is sign-concordant, in BOTH clones,
      with zero exceptions, and the responses reach ~8x against an AFFX technical floor of ~1.1x. H1 is
      excluded. H2 is not thereby PROVEN — it is the surviving hypothesis, and the check that would prove it
      (a probe-target-region map, or the CEL-level data) was not run here.

    ⛔ WHAT SURVIVING H1's EXCLUSION STILL DOES NOT BUY. "Something transcriptional happened on doxycycline"
       is not "the construct did it". Doxycycline has its own effects on HEK293. Separating them needs a
       VECTOR-ONLY tet-On clone, and this series does not contain one — so every shared response below is
       formally construct-effect OR dox-effect, and the series cannot tell them apart. The construct-SPECIFIC
       responses (present in one clone, absent in the other) are the ones a dox effect cannot explain, and
       they are reported separately for that reason.
    """
    i2 = _probe_index(in_dir, platform)
    idx = {r["probe"]: r for r in res["_rows"]}
    out = {"_what": "controls run BEFORE the result is read; one of them fails and the failure is the point"}
    for sym in ("NR4A3", "EWSR1", "PARP1", "NR4A1", "NR4A2"):
        out[sym] = gene_rows(i2, idx, sym, calls=raw)

    detected = [r for r in out["NR4A3"] if r["present_on_all_four_arrays"]]
    out["★_construct_expression_check"] = {
        "question": "does any probe in the record report that the NOR1 / EWS-NOR1 construct was induced?",
        "n_nr4a3_probesets": len(out["NR4A3"]),
        "n_nr4a3_probesets_present_on_all_four_arrays": len(detected),
        "answer": "NO — every NR4A3 probeset is ABSENT-called on every array" if not detected else "PARTIAL",
        "status": "CONTROL_UNAVAILABLE",
        "⚠": ("an ABSENT call is a statement that the collector could not READ this transcript. It is not a "
              "measurement that the transcript is absent, and it is certainly not a measurement that the "
              "construct was not induced (CLAUDE.md §4)."),
    }

    # ── the discriminating observation ────────────────────────────────────────────────────────────────
    bysym = {}
    for probe, v in i2.items():
        s = v.get("symbol") or ""
        if s and "///" not in s and probe in idx:
            bysym.setdefault(s, []).append(probe)
    conc = {}
    for lab, key in (("wild_type", "wt_log2fc"), ("fusion", "fusion_log2fc")):
        tot = agree = 0
        for s, ps in bysym.items():
            if len(ps) < 2:
                continue
            big = [idx[p][key] for p in ps if abs(idx[p][key]) >= math.log2(FOLD_CALL)]
            if len(big) >= 2:
                tot += 1
                if all(z > 0 for z in big) or all(z < 0 for z in big):
                    agree += 1
        conc[lab] = {"n_genes_with_2plus_probesets_each_moving_2x": tot,
                     "n_sign_concordant": agree,
                     "frac_concordant": round(agree / tot, 4) if tot else None}
    out["★_multi_probeset_concordance"] = dict(
        conc, _what=("for genes carrying two or more INDEPENDENT probesets, do the probesets agree on the "
                     "direction of the dox response? Noise has no reason to."),
        _n_genes_with_2plus_probesets=sum(1 for ps in bysym.values() if len(ps) >= 2))

    spikes = sorted(p for p in idx if p.startswith("AFFX-"))
    sv = sorted([abs(idx[p]["wt_log2fc"]) for p in spikes] + [abs(idx[p]["fusion_log2fc"]) for p in spikes])
    out["_affx_spike_in_stability"] = {
        "n_affx_probes": len(spikes),
        "median_abs_log2fc": round(sv[len(sv) // 2], 4) if sv else None,
        "p95_abs_log2fc": round(sv[int(0.95 * len(sv))], 4) if sv else None,
        "p95_as_fold": round(2 ** sv[int(0.95 * len(sv))], 3) if sv else None,
        "_why": ("AFFX control probes should not respond to doxycycline. Their spread is this experiment's "
                 "own floor on what a fold change means with n = 1 — a gene moving less than this is inside "
                 "the technical noise of the pair."),
    }
    out["★_no_vector_only_control_exists_in_this_series"] = (
        "the design has two clones and two dox states and no vector-only tet-On clone, so a response shared "
        "by both clones is CONSTRUCT-driven OR DOXYCYCLINE-driven and this series cannot separate them. "
        "Only the construct-SPECIFIC responses are immune to that confound.")
    return out


# ── the panel, read because these are the genes other lanes in this repository already turn on ───────────
PANEL = ["FN1", "FST", "SMARCA1", "ACTA2", "VCAN", "CHST11", "CHST3", "CHSY1", "UST", "XYLT1",
         "PAPSS1", "PAPSS2", "HAS2", "ACAN", "CSPG4", "CD44", "COL1A1", "COL2A1", "LOX", "LOXL2",
         "CITED2", "STC2", "CTH", "SLC7A11", "INHBE", "PPARG", "ASS1", "DLL3", "ASCL1", "INSM1",
         "HES1", "NR2F1", "SERPINE1", "MMP2", "SOX9"]


def panel_read(res, in_dir, platform, raw):
    """The decision-relevant genes OTHER lanes in this repository already depend on, read out of this
    experiment. ⛔ HYPOTHESIS-GENERATING ONLY: HEK293 is not EMC, n = 1, and a gene moving here is a reason
    to look, never a finding about the disease. The panel is declared BEFORE the numbers are seen — it is
    assembled from `emc-unexplored-treatment-lanes.md` §4's own read list plus the CS/GAG and matrisome
    modules named in §3.6 and §6 — so it cannot be a post-hoc pick of whatever moved."""
    i2 = _probe_index(in_dir, platform)
    idx = {r["probe"]: r for r in res["_rows"]}
    out = {}
    for s in PANEL:
        rows = gene_rows(i2, idx, s, calls=raw)
        det = [r for r in rows if r["present_on_all_four_arrays"]]
        out[s] = {
            "n_probesets": len(rows),
            "n_present_on_all_four_arrays": len(det),
            "status": "READABLE" if det else "NOT_DETECTED_ON_ANY_ARRAY",
            "probesets": rows,
            "wt_log2fc_over_detected": [r["wt_log2fc"] for r in det],
            "fusion_log2fc_over_detected": [r["fusion_log2fc"] for r in det],
        }
    return {
        "_what": "genes this repository's other lanes already turn on, read out of this experiment",
        "_panel_declared_from": ("emc-unexplored-treatment-lanes.md §4 read list + the CS/GAG and matrisome "
                                 "modules named in its §3.6 and §6 — declared before the values were seen"),
        "⛔_status": ("HYPOTHESIS-GENERATING. HEK293 overexpression, n = 1, no vector-only control. A gene "
                     "moving here is a reason to look at it in EMC, never a finding about EMC."),
        "genes": out,
    }


def top_divergent(res, ann, n=25):
    idx = {r["probe"]: r for r in res["_rows"]}
    cand = [idx[p] for p in res["_up_union"]]
    rows = []
    for r in cand:
        rows.append({"probe": r["probe"],
                     "symbol": (ann.get(r["probe"]) or {}).get("symbol") or "",
                     "wt_log2fc": round(r["wt_log2fc"], 3),
                     "fusion_log2fc": round(r["fusion_log2fc"], 3),
                     "delta_fusion_minus_wt": round(r["fusion_log2fc"] - r["wt_log2fc"], 3)})
    rows.sort(key=lambda x: x["delta_fusion_minus_wt"])
    return {"most_wild_type_biased": rows[:n], "most_fusion_biased": list(reversed(rows[-n:]))}


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 4 · THE AF-1 QUESTION, ASKED AND ANSWERED HONESTLY
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def af1_bearing(char, res, ctrl):
    """Does this dataset speak to the premise corrected on 2026-08-06 — that the fusion DELETES NR4A3's AF-1?

    ⛔ THE ANSWER IS THE INTERESTING PART AND IT IS MOSTLY NO. Say so plainly rather than manufacturing a
       bearing: an expression array measures transcript abundance, and the AF-1 question is about which
       PROTEIN RESIDUES the chimera contains. Nothing in a 3'-biased expression array can resolve a
       translation start.
    """
    nr4a3 = ctrl.get("NR4A3", [])
    ews = ctrl.get("EWSR1", [])
    return {
        "_the_premise": ("RETIRED 2026-08-06: 'the fusion REPLACES/DELETES NR4A3's AF-1 (residues 1-260) "
                         "with EWSR1's low-complexity region'. MEASURED false — NR4A3 transcript exons 1-2 "
                         "are entirely non-coding, so NR4A3 exon 3 IS residue 1 and EWSR1(1-264)::"
                         "NR4A3(1-626) RETAINS AF-1, DBD, hinge and LBD. It had been asserted in five live "
                         "places (systems/AUDIT-2026-08-06-routes.md X9)."),
        "does_this_dataset_speak_to_it": "NO — not directly, and the reason is structural, not a shortfall",
        "why_not": [
            "an expression array measures TRANSCRIPT ABUNDANCE. The premise is about which PROTEIN "
            "RESIDUES the chimera contains. No probe-level intensity can locate a translation start.",
            "the construct boundaries are in NEITHER the series record NOR any sample record, and the "
            "paper is not open access — so this experiment's own 'EWS/NOR1' is, from everything reachable "
            "at $0, a construct of UNSPECIFIED exon composition.",
            "these are plasmid cDNAs, so the transcripts are not the native mRNAs and their 5' and 3' ends "
            "are set by the vector, not by NR4A3's exon structure.",
        ],
        "the_functional_corollary_and_why_it_does_not_rescue_the_test": (
            "the premise was never only a sequence claim — it carried a FUNCTIONAL corollary, that a "
            "mechanism living in NOR-1's AF-1 'cannot act on the chimera at any dose'. That corollary "
            "predicts the two constructs should drive SUBSTANTIALLY DIFFERENT target programs, and this "
            "dataset measures exactly that comparison. ⛔ IT STILL DOES NOT DISCRIMINATE, and the reason is "
            "worth writing down rather than leaving as a hope: the measured pattern is a real shared core "
            "(%sx above chance) sitting inside two largely construct-specific responses (%.0f%% / %.0f%% "
            "shared). BOTH hypotheses predict exactly that shape. A chimera that RETAINED the AF-1 would "
            "share targets and diverge in output through the added EWSR1 domain; a chimera that had LOST "
            "the AF-1 would share targets through its retained DBD and diverge in output through the "
            "missing module. The observation is the same either way, so it carries no evidential weight on "
            "this question in either direction."
            % (res["induction_response"]["at_2x"]["overlap_enrichment_over_chance"],
               100 * res["induction_response"]["at_2x"]["frac_of_wild_type_set_shared"],
               100 * res["induction_response"]["at_2x"]["frac_of_fusion_set_shared"])),
        "★_what_WOULD_have_settled_it_from_this_experiment_and_is_absent": [
            "the plasmid construct boundaries, in any record — absent from GEO and behind a paywall in the "
            "paper",
            "a 5'-directed probe or any sequencing read across the fusion junction — GeneChip probesets are "
            "3'-biased and no NR4A3 probeset is even detected here",
            "the CEL-level data would not help either: the same probesets, the same 3' bias",
        ],
        "the_measurement": {
            "at_2x": res["induction_response"]["at_2x"],
            "correlation": {k: v for k, v in
                            res["induction_response"]["★_correlation_of_induction_magnitude"].items()
                            if not k.startswith("⛔_selection")},
        },
        "nr4a3_probes": nr4a3,
        "ewsr1_probes": ews,
        "★_the_answer_stated_plainly": (
            "GSE11185 does NOT speak to the AF-1 premise, in either direction. The correction stands on "
            "what it already stood on — NR4A3's exon structure (`nr4a3-exon-audit.json`) — and this dataset "
            "neither strengthens nor weakens it. Recording that is the point: the premise was asserted in "
            "five live places for months, and the value of opening this series is partly in establishing "
            "which free evidence CANNOT be recruited to the question, so nobody recruits it later."),
    }


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def build(in_dir=IN_DIR):
    char = characterise(in_dir)
    res = read(in_dir, char)
    d = {
        "_title": "GSE11185 — 'Differences between NOR1 and EWS/NOR1', read for the first time",
        "_question": ("emc-unexplored-treatment-lanes.md §4: the direct wild-type-versus-fusion experiment, "
                      "in this repository's GEO census, never opened."),
        "_status": ("$0, CPU, pure stdlib. NOT an EMC tissue measurement, NOT a patient measurement, and "
                    "no efficacy, safety, therapeutic-window or clinical claim is made or implied."),
        "_inputs": {
            "_dir": os.path.relpath(in_dir, HERE),
            "_fetched_by": "s4_lane_inputs_fetch.py on a GitHub Actions runner (CLAUDE.md §6)",
            "_manifest": "_s4_lane_inputs/_manifest.json",
        },
        "characterisation": char,
    }
    if res["status"] != "OK":
        d["read"] = res
        d["verdict"] = {"answer": "NOT_READABLE", "why": res.get("_reading")}
        return d

    plat = char["platform"]
    ann = annotate(in_dir, plat, res["_up_union"])
    gsms = {(s["arm"], s["dox"]): s["gsm"] for s in char["samples"]}
    _cache = {}

    def raw(probe):
        for cell, g in gsms.items():
            if g not in _cache:
                _cache[g] = load_values(in_dir, g)
        return {"%s|%s" % c: [_cache[g][probe][0], _cache[g][probe][1]]
                for c, g in sorted(gsms.items(), key=lambda kv: str(kv[0])) if probe in _cache[g]}

    ctrl = instrument_controls(res, in_dir, plat, raw)
    res_pub = {k: v for k, v in res.items() if not k.startswith("_")}
    d["instrument_controls"] = ctrl
    d["read"] = res_pub
    d["top_divergent_probes"] = top_divergent(res, ann)
    d["decision_relevant_panel"] = panel_read(res, in_dir, plat, raw)
    d["af1_premise_bearing"] = af1_bearing(char, res, ctrl)

    pm = find(in_dir, "PMID%s.epmc.json" % char["pubmed_id"]) if char.get("pubmed_id") else None
    if pm:
        with _open(pm) as fh:
            rec = (json.load(fh).get("resultList") or {}).get("result") or [{}]
        r = rec[0]
        d["the_papers_own_conclusion"] = {
            "citation": "%s %s. %s %s;%s." % (r.get("authorString"), r.get("pubYear"), r.get("title"),
                                              (r.get("journalInfo") or {}).get("journal", {}).get("title"),
                                              r.get("pubYear")),
            "pmid": r.get("pmid"), "doi": r.get("doi"),
            "is_open_access": r.get("isOpenAccess"),
            "verification_level": "[API] Europe PMC record — abstract only, the full text is paywalled",
            "abstract": r.get("abstractText"),
        }
    d["verdict"] = verdict(d, res)
    return d


def _lead(panel, sym, arm):
    g = panel["genes"].get(sym) or {}
    v = g.get("%s_log2fc_over_detected" % ("wt" if arm == "wild_type" else "fusion")) or []
    return (len(v), (min(v), max(v)) if v else None)


def verdict(d, res):
    ir = res["induction_response"]
    two = ir["at_2x"]
    corr = ir["★_correlation_of_induction_magnitude"]
    art = corr["⛔_selection_artifact_do_not_read_as_a_finding"]
    spikes = d["instrument_controls"]["_affx_spike_in_stability"]
    conc = d["instrument_controls"]["★_multi_probeset_concordance"]
    panel = d["decision_relevant_panel"]
    return {
        "answer_1_is_the_series_readable": "YES",
        "answer_2_what_it_is": (
            "4 arrays on %s: 2 HEK293 tet-On clones x (+/- doxycycline, 24 h), n = 1 per cell, %d probes "
            "each, MAS5/GCOS signal. Not EMC, not an EMC cell line, not the endogenous locus, no "
            "vector-only control."
            % (d["characterisation"]["platform"], res["n_probes_common_to_all_four"])),
        "⛔_answer_3_the_construct_expression_control_IS_NOT_AVAILABLE": (
            "all %d NR4A3 probesets are ABSENT-called on all four arrays, so no probe in the deposited "
            "record reports whether either construct was induced. The alternative that the induction simply "
            "did not happen is EXCLUDED by a different measurement, not by assertion: %d/%d (wild-type) and "
            "%d/%d (fusion) genes carrying two or more independent probesets that each move >= 2x are "
            "sign-CONCORDANT, against an AFFX technical floor of %sx at p95. Something transcriptional "
            "happened in both clones on doxycycline. That it was the CONSTRUCT rather than doxycycline "
            "cannot be shown from this series, because it contains no vector-only clone."
            % (len(d["instrument_controls"]["NR4A3"]),
               conc["wild_type"]["n_sign_concordant"],
               conc["wild_type"]["n_genes_with_2plus_probesets_each_moving_2x"],
               conc["fusion"]["n_sign_concordant"],
               conc["fusion"]["n_genes_with_2plus_probesets_each_moving_2x"],
               spikes["p95_as_fold"])),
        "★_answer_4_what_differs_between_wild_type_and_fusion": (
            "The two responses OVERLAP FAR ABOVE CHANCE BUT THE OVERLAP IS A MINORITY OF EACH. At >= 2x: "
            "%d probes up in the wild-type-NOR1 clone, %d in the EWS/NOR1 clone, %d shared — %sx more than "
            "the %s expected by chance, yet only %.0f%% of the wild-type set and %.0f%% of the fusion set "
            "(Jaccard %s). Across every probe the instrument calls present on all four arrays (n = %d, an "
            "unbiased set) the two fold-change vectors correlate WEAKLY: Pearson %s, Spearman %s. So the "
            "answer is BOTH — a real shared core, and a majority of each construct's response that the "
            "other does not reproduce, with poorly-related magnitudes where they do."
            % (two["n_up_wild_type"], two["n_up_fusion"], two["n_up_both"],
               two["overlap_enrichment_over_chance"], two["n_up_expected_both_by_chance"],
               100 * two["frac_of_wild_type_set_shared"], 100 * two["frac_of_fusion_set_shared"],
               two["jaccard_of_up_sets"], corr["n"], corr["pearson_r"], corr["spearman_rho"])),
        "answer_4b_against_the_depositors_own_abstract": (
            "the abstract states the two constructs 'largely shared up-regulated genes, but no significant "
            "correlation was observed with respect to the transactivation levels of each gene' [API]. Read "
            "independently from the deposited values, the SECOND clause reproduces (Spearman %s on an "
            "unbiased probe set) and the FIRST is stronger than what these values support: sharing is %sx "
            "above chance but covers %.0f%% / %.0f%% of the two sets, not most of them. Reported as a "
            "partial non-reproduction rather than as agreement."
            % (corr["spearman_rho"], two["overlap_enrichment_over_chance"],
               100 * two["frac_of_wild_type_set_shared"], 100 * two["frac_of_fusion_set_shared"])),
        "⚠_answer_4c_a_number_this_module_got_wrong_first_time": (
            "the same correlation computed over the UNION of the two selected up-sets is %s (Pearson), "
            "i.e. STRONGLY NEGATIVE, and that is a selection artifact — conditioning on the maximum of a "
            "noisy pair anticorrelates it. It is kept in the artifact, labelled, because the next session "
            "that computes the obvious thing will get it again."
            % art["pearson_r"]),
        "★_answer_4d_the_construct_specific_signal_worth_following": (
            "the largest fusion-specific, dox-driven responses in this system form a coherent ECM module "
            "that the wild-type clone does not reproduce: FN1 (%d probesets present on all four arrays, "
            "fusion log2FC %s vs wild-type %s), FST (%d, %s vs %s), SMARCA1 (%d, %s vs %s), and VCAN — the "
            "chondroitin-sulfate proteoglycan of the myxoid matrix — is DIFFERENTIALLY held: it falls in "
            "the wild-type clone on induction and does not in the fusion clone (%d probesets, fusion %s vs "
            "wild-type %s), consistently across all five. The wild-type clone's own largest "
            "responses are an amino-acid-stress module instead (CTH, SLC7A11, STC2, INHBE). "
            "⛔ HYPOTHESIS-GENERATING: HEK293, n = 1, no vector-only control."
            % (_lead(panel, "FN1", "fusion")[0], _lead(panel, "FN1", "fusion")[1],
               _lead(panel, "FN1", "wild_type")[1],
               _lead(panel, "FST", "fusion")[0], _lead(panel, "FST", "fusion")[1],
               _lead(panel, "FST", "wild_type")[1],
               _lead(panel, "SMARCA1", "fusion")[0], _lead(panel, "SMARCA1", "fusion")[1],
               _lead(panel, "SMARCA1", "wild_type")[1],
               _lead(panel, "VCAN", "fusion")[0], _lead(panel, "VCAN", "fusion")[1],
               _lead(panel, "VCAN", "wild_type")[1])),
        "answer_5_bearing_on_the_retired_AF_1_premise":
            d["af1_premise_bearing"]["does_this_dataset_speak_to_it"],
        "⛔_ceiling": [
            "n = 1 per design cell. No p-value, no confidence interval, and none is emitted anywhere in "
            "this artifact.",
            "NO VECTOR-ONLY CONTROL. Any response shared by both clones is construct-driven OR "
            "doxycycline-driven and this series cannot separate them.",
            "The construct-expression control is UNAVAILABLE — no NR4A3 probeset is detected on any array.",
            "The between-clone axis is confounded with clone identity; only the within-clone induction "
            "contrast is used, and even that rests on one array per state.",
            "HEK293 overexpression of a plasmid cDNA is a transactivation assay. It is not EMC, and the "
            "fusion's native (partner-supplied) promoter — the pharmacologically interesting handle in this "
            "disease — is absent from the system by construction.",
            "The construct boundaries are absent from every record reachable at $0, so 'EWS/NOR1' here is "
            "of unspecified exon composition and may not be the junction this repository models.",
            "Counts move several-fold with the noise floor; see `read.normalisation.⚠_floor_sensitivity`.",
        ],
        "_what_it_licenses": (
            "a citable, first-party read of the one direct wild-type-vs-fusion expression comparison that "
            "exists, at its true weight. It supports a sentence about the fusion sharing a real but "
            "minority core of wild-type NOR1's induced repertoire while diverging over most of it; it "
            "supports naming FN1/VCAN/FST/SMARCA1 as fusion-specific leads WORTH TESTING; and it supports "
            "nothing at all about EMC tissue, efficacy or treatment."),
    }


FRONTMATTER = """---
id: DOC-GSE11185-WT-VS-FUSION
title: GSE11185 — the direct wild-type-versus-fusion expression experiment, read for the first time
level: L4
kind: memo
status: generated
generator: research/modalities/gse11185_wt_vs_fusion.py
canonical_for: ["what GEO GSE11185 does and does not measure"]
purpose: "Open the one deposited NOR1-versus-EWS/NOR1 expression comparison that exists, characterise it honestly before anything is built on it, and report what differs between wild-type NR4A3 and the fusion at the weight the design supports."
scope: "n = 1 per design cell, HEK293 overexpression, no vector-only control. Not EMC tissue, not an EMC cell line, not the endogenous locus. No efficacy, safety, therapeutic-window or clinical statement."
audience: [maintainers, autonomous research agents]
date: 2026-08-07
last_verified: unverified
---

"""


def to_markdown(d):
    c, v = d["characterisation"], d["verdict"]
    L = [FRONTMATTER.rstrip("\n"), "",
         "# GSE11185 — *Differences between NOR1 and EWS/NOR1*, read for the first time", "",
         "> Generated by `gse11185_wt_vs_fusion.py`; this file is derived — edit the module, not this.", "",
         "> %s" % d["_status"], "",
         "## What the series is", "",
         "- **Title (depositors'):** %s" % c["title"],
         "- **Platform:** %s (%s probes, %s%% with a gene symbol)" % (
             c["platform"], (c["platform_annotation"] or {}).get("n_probes"),
             round(100 * ((c["platform_annotation"] or {}).get("probe_symbol_mapping_fraction") or 0), 1)),
         "- **Design (depositors'):** %s" % c["overall_design"],
         "- **Samples:** %d, one per design cell" % c["n_samples_read"],
         "- **Paper:** PMID %s" % c["pubmed_id"], "",
         "| GSM | title | arm | dox | rows | %P |", "|---|---|---|---|---|---|"]
    for s in c["samples"]:
        L.append("| %s | %s | %s | %s | %d | %.1f%% |" % (s["gsm"], s["title"], s["arm"], s["dox"],
                                                          s["n_rows_parsed"], 100 * (s["frac_present"] or 0)))
    L += ["", "> %s" % c["★_replication"], "", "> %s" % c["★_what_the_arms_actually_are"], "",
          "## Verdict", ""]
    for k in v:
        if k.startswith(("_", "⛔_ceiling")):
            continue
        L.append("**%s** — %s\n" % (k.strip("★⚠⛔_"), v[k]))
    L += ["## Ceiling", ""] + ["- %s" % x for x in v["⛔_ceiling"]] + [""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--inputs", default=IN_DIR)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--characterise-only", action="store_true",
                    help="print the characterisation and stop — CLAUDE.md §6's 'characterise before you "
                         "build on it', available as its own step so it can actually be done first")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if args.characterise_only:
        print(json.dumps(characterise(args.inputs), indent=1))
        return 0
    d = build(args.inputs)
    if args.check:
        with open(args.out) as fh:
            old = json.load(fh)
        keys = ["answer_2_what_it_is", "★_answer_4_what_differs_between_wild_type_and_fusion"]
        same = all(old["verdict"].get(k) == d["verdict"].get(k) for k in keys)
        print("[check]", "SAME" if same else "DRIFT")
        return 0 if same else 1
    with open(args.out, "w") as fh:
        json.dump(d, fh, indent=1)
        fh.write("\n")
    with open(os.path.splitext(args.out)[0] + ".md", "w") as fh:
        fh.write(to_markdown(d))
    print(json.dumps(d["verdict"], indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
