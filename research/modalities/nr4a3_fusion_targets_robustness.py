#!/usr/bin/env python3
"""Robustness tests for the EWSR1::NR4A3 transcriptional-output reading.

WHY THIS MODULE EXISTS
======================
`nr4a3_fusion_targets.py` calibrates every contrast against a **size-matched empirical null**:
4,000 random gene sets of the same size, scored identically. That null controls the platform-wide
offset and set SIZE, and it is the right instrument for the question "is this set doing more than
an arbitrary set of the same size". But it has a stated and real limit, recorded as Limitation 9
of the manuscript:

    it does NOT control for gene-gene correlation inside a real pathway, which makes a coherent
    set's variance larger than a random set's. The empirical p is therefore ANTI-CONSERVATIVE for
    coherent sets and is a SCREEN, NOT A TEST.

This module supplies the complementary null that closes exactly that gap, plus three further
robustness axes. All four run OFFLINE from the same committed inputs cache. No fetch, no GPU, $0.

    1. SAMPLE-LABEL PERMUTATION (the fix for Limitation 9).
       Instead of permuting GENES (which destroys the correlation structure), permute the EMC /
       comparator LABELS over samples and rescore the REAL gene set every time. The gene-gene
       correlation structure is carried through untouched by construction, because the gene set is
       never resampled. This is the phenotype-permutation null, and it is the standard answer to
       exactly the criticism the gene-set null attracts.
       ⭐ AND HERE IT CAN BE EXACT RATHER THAN APPROXIMATE. The classified arms are 6-vs-29 on
       GPL6244 and 10-vs-6 on GPL3290, so the number of distinct label assignments is
       C(35,6) = 1,623,160 and C(16,10) = 8,008. Both are small enough to ENUMERATE COMPLETELY, so
       the p-value reported is an exact permutation p, not a sampled estimate. A small n is what
       bounds this paper everywhere else; it is the one place where it is an advantage.

    2. LEAVE-ONE-OUT JACKKNIFE over the EMC arm.
       With 6 and 10 EMC tumours the first question any reader asks is whether one tumour carries
       the result. Drop each EMC sample in turn, rescore, and report the full range and whether the
       sign ever flips.

    3. RANK-BASED RE-READ.
       The headline statistic is a within-array z against the array's own probe distribution, so it
       inherits that background model. Recomputing the same contrast on the WITHIN-ARRAY PERCENTILE
       (a rank, already carried per gene per sample in the inputs cache) asks whether the result is
       an artefact of z-scoring. A rank statistic cannot be moved by a few extreme probes.

    4. BENJAMINI-HOCHBERG FDR across the per-gene permutation p-values (manuscript Limitation 8,
       which records that the reported p-values are uncorrected).

⛔ WHAT THIS MODULE MAY NOT DO. It may not become a second home for any figure the manuscript
already reports. It RE-DERIVES the observed delta for every row and asserts it against the
committed artifact `nr4a3-fusion-targets.json`; if any row disagrees it REFUSES TO WRITE. The
observed deltas belong to that artifact. What is new here is only the four robustness columns.

⛔ AND IT MAY NOT RE-IMPLEMENT THE STATISTIC. Every scoring primitive is IMPORTED from
`nr4a3_fusion_targets.py` rather than copied, so the permutation is provably testing the same
quantity the paper reports. A re-implementation that drifted by one convention would produce a
confirmation of something that was never measured.

USAGE
    python3 nr4a3_fusion_targets_robustness.py           # derive offline, write the artifact
    python3 nr4a3_fusion_targets_robustness.py --check   # re-derive and diff against the artifact
"""

import argparse
import importlib.util
import itertools
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "nr4a3-fusion-targets-inputs.json")
MAIN_ARTIFACT = os.path.join(HERE, "nr4a3-fusion-targets.json")
OUT = os.path.join(HERE, "nr4a3-fusion-targets-robustness.json")

# Enumerate every label assignment when there are no more than this many; otherwise sample.
# C(35,6) = 1,623,160 and C(16,10) = 8,008, so both real platforms enumerate exactly.
EXACT_ENUMERATION_CEILING = 3_000_000
SAMPLED_DRAWS = 200_000
PERM_SEED = 20260807          # same seed discipline as the parent module

# Rows carried here. Genes first (the manuscript's positive result), then the sets whose
# interpretation depends most on the correlation structure the gene-set null cannot see.
CLASS_A_GENES = ["ENO3", "PPARG", "SEMA3C"]
CONTROL_GENES = ["NR4A3", "PLAGL1", "SGK1"]
SETS_TO_TEST = [
    "A_plus_B_all_dna_binding",
    "B_native_nr4a3_dna_binding_targets",
    "D_filion_table1_emc_vs_137_sarcomas",
    "PPARG_pparg_chip_chea",
    "PPARG_pparg_KO_UP_FALSIFIER",
    "PPARG_adipogenesis_process_proxy",
]


def _load_parent():
    """Import the producing module so every primitive is the SAME code the manuscript ran."""
    spec = importlib.util.spec_from_file_location(
        "nr4a3_fusion_targets", os.path.join(HERE, "nr4a3_fusion_targets.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------------------------
# per-sample score vectors, built with the parent module's own primitives
# ------------------------------------------------------------------------------------------------
def _per_sample_z(m, tgt, genes):
    """Mean within-sample z over the readable members -- the parent module's set statistic."""
    have = tgt.get("genes") or {}
    readable = sorted({g for g in genes if g in have})
    if not readable:
        return None, []
    rows = [m._zrow(tgt, g) for g in readable]
    n_s = tgt["n_samples"]
    return [m._mean([r[i] for r in rows]) for i in range(n_s)], readable


def _per_sample_percentile(m, tgt, genes):
    """The same contrast on the WITHIN-ARRAY PERCENTILE instead of the z. Rank-based re-read."""
    have = tgt.get("genes") or {}
    readable = sorted({g for g in genes if g in have})
    if not readable:
        return None, []
    rows = [have[g].get("array_percentile") for g in readable]
    rows = [r for r in rows if r]
    if not rows:
        return None, []
    n_s = tgt["n_samples"]
    return [m._mean([r[i] for r in rows]) for i in range(n_s)], readable


def _delta(m, per_sample, emc, comp):
    a = [per_sample[i] for i in emc if per_sample[i] is not None]
    b = [per_sample[i] for i in comp if per_sample[i] is not None]
    if len(a) < m.MIN_GROUP_N_FOR_A_CONTRAST or len(b) < m.MIN_GROUP_N_FOR_A_CONTRAST:
        return None, len(a), len(b)
    return m._mean(a) - m._mean(b), len(a), len(b)


# ------------------------------------------------------------------------------------------------
# 1 - the sample-label permutation null (exact where the arms allow it)
# ------------------------------------------------------------------------------------------------
def _label_permutation(values, k, observed):
    """Exact two-sided permutation p over EMC/comparator label assignments.

    `values` are the per-sample scores of the classified samples with a readable score; `k` is the
    number of them that are really EMC. Every way of choosing k of the n samples is a null
    labelling, and the real one is among them -- which is what makes the p exact rather than
    smoothed. delta(S) = sum(S)/k - (T - sum(S))/(n-k), so each draw costs one sum of k floats.
    """
    n = len(values)
    if n - k < 1 or k < 1:
        return None
    total = math.fsum(values)
    obs_abs = abs(observed)
    tol = 1e-12                                   # float equality guard on the >= comparison
    n_total = math.comb(n, k)
    exact = n_total <= EXACT_ENUMERATION_CEILING

    at_least_as_extreme = 0
    considered = 0
    if exact:
        for combo in itertools.combinations(values, k):
            s = math.fsum(combo)
            d = s / k - (total - s) / (n - k)
            considered += 1
            if abs(d) >= obs_abs - tol:
                at_least_as_extreme += 1
        p = at_least_as_extreme / considered
    else:
        rng = random.Random(PERM_SEED)
        idx = list(range(n))
        for _ in range(SAMPLED_DRAWS):
            s = math.fsum(values[i] for i in rng.sample(idx, k))
            d = s / k - (total - s) / (n - k)
            considered += 1
            if abs(d) >= obs_abs - tol:
                at_least_as_extreme += 1
        # +1/+1 smoothing is correct for a SAMPLED null: it cannot report p = 0.
        p = (at_least_as_extreme + 1) / (considered + 1)

    return {
        "p_two_sided": round(p, 6),
        "exact": exact,
        "n_labellings_total": n_total,
        "n_labellings_considered": considered,
        "n_at_least_as_extreme": at_least_as_extreme,
        "smallest_p_this_design_can_report": round(1.0 / n_total, 8) if exact
        else round(1.0 / (considered + 1), 8),
        "_what_is_permuted": "the EMC / comparator LABEL over samples. The gene set is never "
                             "resampled, so gene-gene correlation is carried through untouched -- "
                             "which is the property the size-matched gene-set null does not have.",
    }


# ------------------------------------------------------------------------------------------------
# 2 - leave-one-out jackknife over the EMC arm
# ------------------------------------------------------------------------------------------------
def _jackknife(m, per_sample, emc, comp, observed):
    readable_emc = [i for i in emc if per_sample[i] is not None]
    if len(readable_emc) <= m.MIN_GROUP_N_FOR_A_CONTRAST:
        return {"computed": False,
                "why": "dropping one sample would take the EMC arm below the contrast floor."}
    out = []
    for drop in readable_emc:
        kept = [i for i in readable_emc if i != drop]
        d, _, _ = _delta(m, per_sample, kept, comp)
        if d is not None:
            out.append({"dropped_sample_index": drop, "delta": round(d, 4)})
    if not out:
        return {"computed": False, "why": "no leave-one-out contrast was computable."}
    deltas = [o["delta"] for o in out]
    same_sign = all((d > 0) == (observed > 0) for d in deltas)
    return {
        "computed": True,
        "n_leave_one_out_fits": len(out),
        "min_delta": min(deltas),
        "max_delta": max(deltas),
        "sign_holds_in_every_fit": same_sign,
        "per_fit": out,
        "_reading": ("the sign of the contrast survives dropping any single EMC tumour"
                     if same_sign else
                     "⛔ THE SIGN FLIPS when at least one EMC tumour is dropped -- the row is "
                     "carried by individual samples and must not be read as a group difference"),
    }


# ------------------------------------------------------------------------------------------------
# 4 - Benjamini-Hochberg
# ------------------------------------------------------------------------------------------------
def _bh_fdr(pairs):
    """pairs: [(key, p)] -> {key: q}. Standard BH step-up with monotonicity enforced."""
    live = [(k, p) for k, p in pairs if p is not None]
    if not live:
        return {}
    live.sort(key=lambda kp: kp[1])
    n = len(live)
    q = {}
    prev = 1.0
    for rank in range(n, 0, -1):
        k, p = live[rank - 1]
        val = min(prev, p * n / rank)
        q[k] = round(val, 6)
        prev = val
    return q


# ------------------------------------------------------------------------------------------------
# derive
# ------------------------------------------------------------------------------------------------
def _observed_from_artifact(art, kind, name, matrix_file):
    """The delta the manuscript reports, read from the artifact that OWNS it."""
    node = (art.get("gene_reads") if kind == "gene" else art.get("set_scores")) or {}
    row = node.get(name) or {}
    for series_key, series in row.items():
        if not isinstance(series, dict):
            continue
        if series.get("matrix_file") == matrix_file or series_key == matrix_file:
            nc = series.get("null_calibration") or {}
            if nc.get("observed_delta") is not None:
                return nc["observed_delta"], series_key
            # sets carry `score`; single genes carry `welch_EMC_vs_comparator`
            for holder in (series.get("score"), series.get("welch_EMC_vs_comparator")):
                if isinstance(holder, dict) and holder.get("delta_a_minus_b") is not None:
                    return holder["delta_a_minus_b"], series_key
    return None, None


def derive():
    m = _load_parent()
    inp = json.load(open(INPUTS))
    art = json.load(open(MAIN_ARTIFACT))
    set_defs = art.get("set_definitions") or {}

    rows = []
    parity_failures = []

    for matrix_file, tgt in inp["targets"].items():
        classes, emc, comp = m._group_indices(tgt["samples"])
        platform = tgt.get("platform")

        targets = [("gene", g, [g]) for g in CLASS_A_GENES + CONTROL_GENES]
        for sname in SETS_TO_TEST:
            spec = set_defs.get(sname) or {}
            genes = spec.get("genes") if isinstance(spec, dict) else spec
            if genes:
                targets.append(("set", sname, list(genes)))

        for kind, name, genes in targets:
            per_sample, readable = _per_sample_z(m, tgt, genes)
            if not per_sample or not readable:
                continue
            observed, n_a, n_b = _delta(m, per_sample, emc, comp)
            if observed is None:
                rows.append({"kind": kind, "name": name, "platform": platform,
                             "matrix_file": matrix_file, "computed": False,
                             "why": f"no contrast: n_EMC={n_a}, n_comparator={n_b}, floor is "
                                    f"{m.MIN_GROUP_N_FOR_A_CONTRAST}. An absent reading is not a "
                                    f"reading of absence."})
                continue

            # PARITY -- the observed delta must equal what the manuscript's artifact reports.
            reported, _ = _observed_from_artifact(art, kind, name, matrix_file)
            parity = None
            if reported is not None:
                parity = abs(round(observed, 4) - reported) < 5e-4
                if not parity:
                    parity_failures.append(
                        f"{kind}:{name}:{platform} re-derived {round(observed,4)} vs artifact "
                        f"{reported}")

            vals = [per_sample[i] for i in list(emc) + list(comp) if per_sample[i] is not None]
            k = len([i for i in emc if per_sample[i] is not None])
            perm = _label_permutation(vals, k, observed)
            jack = _jackknife(m, per_sample, emc, comp, observed)

            pct_per_sample, _ = _per_sample_percentile(m, tgt, genes)
            pct = None
            if pct_per_sample:
                pd_, _, _ = _delta(m, pct_per_sample, emc, comp)
                if pd_ is not None:
                    pvals = [pct_per_sample[i] for i in list(emc) + list(comp)
                             if pct_per_sample[i] is not None]
                    pk = len([i for i in emc if pct_per_sample[i] is not None])
                    pperm = _label_permutation(pvals, pk, pd_)
                    pct = {"delta_percentile_points": round(pd_, 4),
                           "same_sign_as_z": (pd_ > 0) == (observed > 0),
                           "p_two_sided": (pperm or {}).get("p_two_sided"),
                           "_units": "within-array percentile (0-1), NOT SD units; the magnitude "
                                     "is not comparable to the z delta, only the sign and the p."}

            rows.append({
                "kind": kind, "name": name, "platform": platform, "matrix_file": matrix_file,
                "computed": True,
                "n_genes_readable": len(readable),
                "n_emc": n_a, "n_comparator": n_b,
                "observed_delta_re_derived": round(observed, 4),
                "observed_delta_in_manuscript_artifact": reported,
                "parity_with_artifact": parity,
                "label_permutation": perm,
                "jackknife_leave_one_emc_out": jack,
                "rank_based_re_read": pct,
            })

    if parity_failures:
        print("⛔ PARITY FAILURE -- re-derived deltas disagree with the committed artifact:",
              file=sys.stderr)
        for f in parity_failures:
            print("   " + f, file=sys.stderr)
        print("REFUSING TO WRITE. The robustness columns would describe a different object than "
              "the manuscript reports.", file=sys.stderr)
        raise SystemExit(2)

    # BH across the per-gene permutation p-values, within each platform.
    fdr = {}
    for plat in sorted({r["platform"] for r in rows if r.get("computed")}):
        pairs = [(r["name"], (r["label_permutation"] or {}).get("p_two_sided"))
                 for r in rows
                 if r.get("computed") and r["platform"] == plat and r["kind"] == "gene"]
        fdr[plat] = _bh_fdr(pairs)
    for r in rows:
        if r.get("computed") and r["kind"] == "gene":
            r["bh_fdr_q_across_genes_on_this_platform"] = fdr.get(r["platform"], {}).get(r["name"])

    return {
        "_schema": "nr4a3-fusion-targets-robustness/1",
        "_generated_by": "research/modalities/nr4a3_fusion_targets_robustness.py",
        "_do_not_hand_edit": "Regenerate with `python3 research/modalities/"
                             "nr4a3_fusion_targets_robustness.py`. Every observed delta here is "
                             "asserted equal to research/modalities/nr4a3-fusion-targets.json, "
                             "which owns it; this file adds only the robustness columns.",
        "what_this_answers": {
            "limitation_9_gene_gene_correlation":
                "The manuscript's size-matched null permutes GENES, so it cannot see gene-gene "
                "correlation and is anti-conservative for coherent sets -- a screen, not a test. "
                "The label permutation here permutes SAMPLES and never resamples the gene set, so "
                "the correlation structure is preserved exactly. Where the arms are small enough "
                "the enumeration is COMPLETE and the p is exact.",
            "limitation_8_multiple_testing":
                "Benjamini-Hochberg q-values across the per-gene permutation p-values, per platform.",
            "small_n_fragility":
                "Leave-one-EMC-tumour-out jackknife: the full range of the contrast and whether "
                "the sign survives dropping any single tumour.",
            "z_scoring_dependence":
                "The same contrast recomputed on the within-array percentile (a rank), which no "
                "background model and no handful of extreme probes can move.",
        },
        "method": {
            "statistic": "identical to the manuscript's: mean within-sample z over readable "
                         "members, EMC minus comparator. Every primitive is IMPORTED from "
                         "nr4a3_fusion_targets.py rather than re-implemented.",
            "permutation": "two-sided over EMC/comparator label assignments; exhaustive when the "
                           "number of assignments is <= %d, otherwise %d seeded draws with +1/+1 "
                           "smoothing." % (EXACT_ENUMERATION_CEILING, SAMPLED_DRAWS),
            "seed": PERM_SEED,
            "cost": "$0 -- CPU only, offline, from the committed inputs cache. No fetch, no GPU.",
        },
        "rows": rows,
    }


def _canon(d):
    d = dict(d)
    d.pop("_generated_utc", None)
    return json.dumps(d, sort_keys=True, indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="Re-derive offline and diff against the committed artifact.")
    a = ap.parse_args(argv)
    if not os.path.exists(INPUTS):
        print(f"no inputs cache at {INPUTS}", file=sys.stderr)
        return 2
    got = derive()
    if a.check:
        if not os.path.exists(OUT):
            print(f"no artifact at {OUT} -- run without --check first", file=sys.stderr)
            return 2
        want = json.load(open(OUT))
        if _canon(got) == _canon(want):
            print("offline re-derive matches the artifact")
            return 0
        print("⛔ MISMATCH between the re-derived result and the committed artifact",
              file=sys.stderr)
        return 1
    with open(OUT, "w") as fh:
        json.dump(got, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
