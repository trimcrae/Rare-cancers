#!/usr/bin/env python3
"""IC-4-A — IS THE CRYPTIC-POCKET CONTRAST ONE VERDICT OR TWO? A $0 RE-READ, NO NEW COMPUTE.

★★ WHY THIS EXISTS. `paralogue-pocket-contrast.json` reports ONE pooled verdict over BOTH paralogues:

    map_edits_required.verdict = "RANKED but replicate ranges OVERLAP"

built by `paralogue_pocket_contrast.build_map_edits` from a single conjunction —

    sep = r3[0] > r1[1] and r3[0] > r2[1]      # NR4A3's worst replicate beats EACH paralogue's best

— so one `and` collapses two independent questions into one flag. The two questions are not
interchangeable: [`systems/views/L2-rt-asymmetric.md`](../../systems/views/L2-rt-asymmetric.md)
(`RT-ASYMMETRIC`) holds that **NR4A1-sparing is MANDATORY and NR4A2-sparing is BEST-EFFORT**, and its route
record states that dropping the asymmetry "lets a symmetric restatement back in". A pooled OVERLAP verdict
is exactly such a restatement: it reports the best-effort axis's answer on the mandatory axis's behalf.

⛔ THIS MODULE ADDS NO DATA AND RE-RUNS NOTHING. No fpocket, no MD, no GPU, no rental. Every number is read
from a committed artifact (`_inputs`) and every derived statistic is exact enumeration in the stdlib. It
does not overwrite `paralogue-pocket-contrast.json`, which is a landed record.

★ AND IT WAS BUILT TO BE ABLE TO KILL ITS OWN LEAD. The interesting question is not "does the conjunction
split" — it does, arithmetically, and that is one line. It is whether a 3-vs-3 replicate comparison can
carry the word SEPARATED at all. So the module computes, in order: the exact permutation p-value AND the
best p-value the design can possibly return; the effect size; how anti-conservative the pooled Wilson
interval actually is (design effect, measured, not asserted); an exhaustive cluster bootstrap; and the
fragility of the separation against (a) one more replicate and (b) the CONTESTED `C2` cavity-selection
rule, whose replicate-level consequence is recoverable from `pocket-accepted-candidates.json` and had never
been read off it.

The claim ceilings of the source artifact travel with everything here and are re-emitted verbatim in
`_ceilings_inherited`: a conformational-selection RANKING only, never an exclusion; NOT `dG_open`; not
evidence of absence; and a paralogue row of 0 means "NR4A3's site did not open here", never "this protein
has no druggable cavity".

Usage
    python3 paralogue_pocket_asymmetric_read.py            # writes paralogue-pocket-asymmetric-read.json
    python3 paralogue_pocket_asymmetric_read.py --stdout   # print, write nothing
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

CONTRAST = os.path.join(HERE, "paralogue-pocket-contrast.json")
ACCEPTED = os.path.join(HERE, "pocket-accepted-candidates.json")
AUDIT = os.path.join(HERE, "r3-site-choice-audit.json")
OUT = os.path.join(HERE, "paralogue-pocket-asymmetric-read.json")

UNBIASED = ("release_rep0", "release_rep1", "release_rep2")
PARALOGUES = ("NR4A1", "NR4A2")
# RT-ASYMMETRIC's axis assignment. Read, never invented here — its one home is systems/graph, rendered at
# systems/views/L2-rt-asymmetric.md. Quoted so the reason a split verdict matters is legible in the artifact.
AXIS = {"NR4A1": "mandatory", "NR4A2": "best_effort"}


# ---------------------------------------------------------------------------------------------------------
# pure — exact statistics. No scipy in this sandbox and none needed: every test below is an enumeration.
# ---------------------------------------------------------------------------------------------------------
def midranks(values):
    """Ranks with ties averaged (mid-ranks). PURE."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def exact_ranksum(a, b):
    """Exact two-sample rank-sum (Wilcoxon–Mann–Whitney) by COMPLETE ENUMERATION of the C(n+m, n) label
    assignments, ties handled by mid-ranks. PURE.

    ★ It also returns `p_one_sided_floor` — the SMALLEST p this design can return, 1 / C(n+m, n). At
    n = m = 3 that is 0.05 exactly, so a 3-vs-3 comparison CANNOT produce evidence stronger than p = 0.05
    one-sided however cleanly the groups separate. Reporting the achieved p without its floor invites a
    reader to grade 0.05 as 'just significant' when it is in fact the design's ceiling."""
    n, m = len(a), len(b)
    pooled = list(a) + list(b)
    ranks = midranks(pooled)
    obs = sum(ranks[i] for i in range(n))
    idx = range(n + m)
    stats = [sum(ranks[i] for i in combo) for combo in itertools.combinations(idx, n)]
    total = len(stats)
    ge = sum(1 for s in stats if s >= obs - 1e-12)
    le = sum(1 for s in stats if s <= obs + 1e-12)
    p_hi = ge / total          # one-sided: a ranks HIGHER than b
    p_lo = le / total
    return {
        "n_a": n, "n_b": m,
        "rank_sum_a": obs,
        "n_permutations": total,
        "p_one_sided_a_greater": round(p_hi, 6),
        "p_one_sided_a_less": round(p_lo, 6),
        "p_two_sided": round(min(1.0, 2.0 * min(p_hi, p_lo)), 6),
        "p_one_sided_floor": round(1.0 / total, 6),
        "p_two_sided_floor": round(min(1.0, 2.0 / total), 6),
        "achieved_the_design_floor": abs(p_hi - 1.0 / total) < 1e-12,
    }


def exact_mean_permutation(a, b):
    """Exact permutation test on the DIFFERENCE OF MEANS — same 20 assignments, but it uses magnitudes
    rather than ranks, so a large gap can matter. PURE. Its p is floored at 1/C(n+m,n) for the same reason.
    """
    n, m = len(a), len(b)
    pooled = list(a) + list(b)
    obs = sum(a) / n - sum(b) / m
    total_sum = sum(pooled)
    diffs = []
    for combo in itertools.combinations(range(n + m), n):
        sa = sum(pooled[i] for i in combo)
        diffs.append(sa / n - (total_sum - sa) / m)
    total = len(diffs)
    ge = sum(1 for d in diffs if d >= obs - 1e-12)
    return {"observed_mean_difference": round(obs, 6),
            "n_permutations": total,
            "p_one_sided_a_greater": round(ge / total, 6),
            "p_one_sided_floor": round(1.0 / total, 6)}


def cliffs_delta(a, b):
    """Cliff's delta — the nonparametric effect size, (#a>b − #a<b) / (n·m). PURE.
    delta = 1.0 means every a exceeds every b, which is exactly the artifact's own 'worst beats best' rule.
    """
    gt = sum(1 for x in a for y in b if x > y)
    lt = sum(1 for x in a for y in b if x < y)
    n = len(a) * len(b)
    d = (gt - lt) / n
    return {"delta": round(d, 6), "n_pairs": n, "n_a_gt_b": gt, "n_a_lt_b": lt,
            "n_ties": n - gt - lt,
            "magnitude": ("negligible" if abs(d) < 0.147 else "small" if abs(d) < 0.33 else
                          "medium" if abs(d) < 0.474 else "large")}


def wilson(k, n, z=1.959963984540054):
    """Wilson score interval. PURE. Kept here so the design-effect-corrected interval below is computed by
    the SAME function as the uncorrected one — a corrected interval built by a different formula would not
    be comparable to the artifact's."""
    if n <= 0:
        return [None, None]
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def sample_variance(xs):
    """Unbiased (n−1) variance. PURE."""
    n = len(xs)
    if n < 2:
        return None
    mu = sum(xs) / n
    return sum((x - mu) ** 2 for x in xs) / (n - 1)


def design_effect(per_replicate_fracs, frames_per_replicate):
    """MEASURE how anti-conservative the pooled Wilson interval is, instead of asserting it. PURE.

    The source artifact states that the 75 pooled frames are 3 correlated replicas so Wilson is
    anti-conservative — correct, and never quantified. Here: deff = (observed between-replicate variance of
    the per-replicate fraction) / (the binomial variance those replicates would have if the frames inside
    them were independent), and n_eff = N / deff. deff < 1 is a real reading (three replicates can land
    closer together than independence predicts by chance) and is reported as measured, floored at 1.0 only
    for the CORRECTED INTERVAL, because widening is the conservative direction and narrowing below the
    binomial interval would be the anti-conservative one this correction exists to avoid."""
    p = sum(per_replicate_fracs) / len(per_replicate_fracs)
    obs = sample_variance(per_replicate_fracs)
    binom = p * (1 - p) / frames_per_replicate if 0 < p < 1 else None
    if obs is None or not binom:
        return {"design_effect": None, "note": "not computable at this p or n"}
    deff = obs / binom
    n_total = frames_per_replicate * len(per_replicate_fracs)
    deff_used = max(1.0, deff)
    return {
        "per_replicate_fracs": per_replicate_fracs,
        "pooled_fraction": round(p, 6),
        "observed_between_replicate_variance": round(obs, 8),
        "binomial_variance_if_frames_independent": round(binom, 8),
        "design_effect": round(deff, 4),
        "design_effect_used_for_correction": round(deff_used, 4),
        "n_frames_total": n_total,
        "effective_n": round(n_total / deff_used, 2),
        "wilson95_uncorrected": wilson(round(p * n_total), n_total),
        "wilson95_design_corrected": wilson(p * (n_total / deff_used), n_total / deff_used),
    }


def intervals_overlap(i, j):
    """Do two intervals overlap? PURE. Reported because a design-corrected interval that STILL separates is
    a stronger statement than a rank test at its floor, and one that overlaps is a third independent way of
    saying the same caution."""
    if None in i or None in j:
        return {"overlap": None}
    lo = max(i[0], j[0])
    hi = min(i[1], j[1])
    return {"overlap": lo <= hi, "gap": round(lo - hi, 6) if lo > hi else 0.0,
            "overlap_width": round(hi - lo, 6) if lo <= hi else 0.0}


def holm(pvalues):
    """Holm–Bonferroni adjusted p-values. PURE.

    ⚠ WHY THIS IS HERE AND NOT OMITTED. Two paralogue comparisons were made. RT-ASYMMETRIC prespecifies
    which one is MANDATORY, but that is a statement about what the molecule must achieve, not a
    prespecified statistical hypothesis ordering — so a reader is entitled to the family-wise view, and at
    a design floor of 0.05 a family of two cannot clear 0.05 adjusted. Reporting the unadjusted p alone
    would let the design's ceiling be read as a result."""
    order = sorted(pvalues, key=lambda kv: kv[1])
    m = len(order)
    out, running = {}, 0.0
    for i, (k, p) in enumerate(order):
        adj = min(1.0, (m - i) * p)
        running = max(running, adj)
        out[k] = round(running, 6)
    return out


def cluster_bootstrap_difference(a, b):
    """EXHAUSTIVE cluster bootstrap on the difference of means, replicate = resampling unit. PURE.

    With 3 clusters per arm there are 3**3 = 27 equally likely resamples per arm and 729 pairs, so the
    bootstrap distribution is enumerated in full rather than sampled — no seed, no Monte-Carlo error, and
    nothing a re-run can change. ⚠ Its resolution is bounded BY THAT: 27 distinct resamples per arm cannot
    describe a tail finer than 1/729, and a bootstrap over 3 clusters is a weak instrument in general. It
    is reported because it answers a different question from the permutation test — how far the difference
    itself moves when replicates are re-drawn — not because it is stronger."""
    ra = [sum(c) / len(c) for c in itertools.product(a, repeat=len(a))]
    rb = [sum(c) / len(c) for c in itertools.product(b, repeat=len(b))]
    diffs = sorted(x - y for x in ra for y in rb)
    n = len(diffs)

    def q(f):
        return round(diffs[min(n - 1, max(0, int(round(f * (n - 1)))))], 6)
    return {"n_resamples": n, "n_distinct_per_arm": len(ra),
            "mean_difference": round(sum(diffs) / n, 6),
            "percentile95": [q(0.025), q(0.975)],
            "frac_of_resamples_with_difference_le_0": round(
                sum(1 for d in diffs if d <= 0) / n, 6)}


def t2_cdf(t):
    """CDF of Student-t with df = 2, in closed form: F(t) = 1/2 · (1 + t/sqrt(2 + t²)). PURE and exact —
    no scipy, no table, no approximation. df = 2 is exactly what n = 3 replicates gives."""
    return 0.5 * (1.0 + t / math.sqrt(2.0 + t * t))


def one_more_replicate_fragility(nr4a3_reps, paralogue_reps):
    """How much of this separation rests on there being only three replicates. PURE.

    Two readings, and the FIRST is the one to quote because it assumes nothing:
      * `margin` — NR4A3's worst replicate minus the paralogue's best — beside NR4A3's own replicate SD.
        A margin far smaller than the spread of the very quantity it is built from is fragile, and that is
        arithmetic, not a model.
      * `p_next_nr4a3_replicate_below_paralogue_max` — a NORMAL-MODEL t-predictive probability that a 4th
        NR4A3 replicate would land below the paralogue's observed best and break the rule. ⚠ MODEL-BASED,
        on 3 points, and a fraction is bounded in [0,1] while the model is not; it is an order-of-magnitude
        statement about fragility and must never be read as a calibrated probability."""
    n = len(nr4a3_reps)
    mu = sum(nr4a3_reps) / n
    sd = math.sqrt(sample_variance(nr4a3_reps))
    worst, best = min(nr4a3_reps), max(paralogue_reps)
    se_pred = sd * math.sqrt(1.0 + 1.0 / n)
    t = (best - mu) / se_pred if se_pred else None
    lo = mu - 4.302652729911275 * se_pred   # t(0.975, df=2), exact from t2_cdf
    hi = mu + 4.302652729911275 * se_pred
    return {
        "nr4a3_worst_replicate": worst,
        "paralogue_best_replicate": best,
        "margin": round(worst - best, 6),
        "nr4a3_replicate_sd": round(sd, 6),
        "margin_in_units_of_nr4a3_replicate_sd": (round((worst - best) / sd, 4) if sd else None),
        "p_next_nr4a3_replicate_below_paralogue_max": (round(t2_cdf(t), 4) if t is not None else None),
        "t_predictive95_for_a_4th_nr4a3_replicate": [round(lo, 4), round(hi, 4)],
        "⚠_predictive_interval_exceeds_the_unit_interval": bool(lo < 0.0 or hi > 1.0),
        "_model_note": "the predictive figures assume normality on 3 points; the margin-vs-SD ratio "
                       "assumes nothing and is the one to quote.",
    }


# ---------------------------------------------------------------------------------------------------------
# pure — the split verdict itself
# ---------------------------------------------------------------------------------------------------------
def pairwise_verdict(nr4a3_reps, para_reps, pooled3, pooledp):
    """The source artifact's OWN rule, applied to ONE paralogue instead of to the conjunction. PURE.

    ⚠ The rule is not re-tuned, re-derived or softened here — `worst beats best` is
    `paralogue_pocket_contrast.build_map_edits`'s `sep`, verbatim, with the `and` removed. That is the
    entire intervention. A rule loosened after seeing which paralogue fails would be the outcome-selection
    defect the harmonized rerun exists to remove."""
    sep = min(nr4a3_reps) > max(para_reps)
    ordered = pooled3 > pooledp
    return {
        "verdict": ("SEPARATED at replicate granularity" if sep else
                    "RANKED but replicate ranges OVERLAP" if ordered else
                    "NOT RANKED in NR4A3's favour"),
        "separated": sep,
        "ranked": ordered,
        "rule": "SEPARATED requires NR4A3's WORST release replicate to beat this paralogue's BEST — "
                "`paralogue_pocket_contrast.build_map_edits`'s `sep`, per paralogue rather than "
                "conjoined. The rule is unchanged; only its scope is.",
    }


# ---------------------------------------------------------------------------------------------------------
# impure — read committed artifacts
# ---------------------------------------------------------------------------------------------------------
def load(path):
    with open(path) as fh:
        return json.load(fh)


def replicate_fracs(contrast, species):
    """The three UNBIASED release replicate fractions, read from the contrast's own `replicate_spread`."""
    return list((contrast["contrast"][species]["replicate_spread"]["per_replicate_frac_ge_dstar"]))


def alternative_rule_replicate_fracs(accepted):
    """Replicate-level fractions under the CONTESTED `C2` cavity-selection axis — the ordering that would
    prefer the most druggable ACCEPTED cavity — recovered from `pocket-accepted-candidates.json`.

    ⛔ THIS IS A SENSITIVITY, NOT A RULE, AND NOT A PROPOSED RULE. `pocket_accepted_candidates.most_druggable`
    says so in its own docstring and `r3-site-choice-audit.json` says the frozen rule remains the rule. It is
    computed because `C2` is registered ⚠ CONTESTED in the roadmap's §3b.2, and because the audit measured
    its consequence at POOLED granularity only — while the verdict under test is a REPLICATE-granularity
    rule, which no committed artifact had ever evaluated under the alternative ordering.

    Denominator is `n_frames` (= n_propagated), matching the contrast's `frac_ge_among_propagated`: a frame
    where the detector ran and no cavity cleared the gate is a reading of 'did not open', not a refusal.
    `pocket-accepted-candidates.json` records `n_refusals: 0`, so the two denominators coincide here."""
    out = {}
    for row in accepted["summary"]:
        if row["ensemble"] not in UNBIASED:
            continue
        out.setdefault(row["species"], {})[row["ensemble"]] = {
            "frozen": row["n_ge_dstar_frozen"] / row["n_frames"],
            "most_druggable": row["n_ge_dstar_if_most_druggable"] / row["n_frames"],
            "n_frames": row["n_frames"],
        }
    return {sp: {"frozen": [out[sp][e]["frozen"] for e in UNBIASED],
                 "most_druggable": [out[sp][e]["most_druggable"] for e in UNBIASED],
                 "n_frames_per_replicate": [out[sp][e]["n_frames"] for e in UNBIASED]}
            for sp in out}


def recount_from_per_frame(accepted, d_star):
    """Independently re-derive the alternative-rule counts from `per_frame.accepted`, so the summary row is
    CHECKED rather than trusted (CLAUDE.md §4b: a populated field is not a measured one)."""
    counts = {}
    for f in accepted["per_frame"]:
        if f["ensemble"] not in UNBIASED:
            continue
        key = (f["species"], f["ensemble"])
        c = counts.setdefault(key, {"n_frames": 0, "most_druggable": 0})
        c["n_frames"] += 1
        acc = f.get("accepted") or []
        if acc and max((a.get("druggability") or 0.0) for a in acc) >= d_star:
            c["most_druggable"] += 1
    return {sp: [counts[(sp, e)]["most_druggable"] / counts[(sp, e)]["n_frames"] for e in UNBIASED]
            for sp in {k[0] for k in counts}}


# ---------------------------------------------------------------------------------------------------------
def build(contrast, accepted, audit):
    d_star = contrast["detector"]["d_star"]
    reps = {sp: replicate_fracs(contrast, sp) for sp in ("NR4A3",) + PARALOGUES}
    pooled = {sp: contrast["contrast"][sp]["unbiased_pooled"]["frac_ge_among_propagated"]
              for sp in ("NR4A3",) + PARALOGUES}
    counts = {sp: (contrast["contrast"][sp]["unbiased_pooled"]["n_ge_dstar"],
                   contrast["contrast"][sp]["unbiased_pooled"]["n_propagated"])
              for sp in ("NR4A3",) + PARALOGUES}

    alt = alternative_rule_replicate_fracs(accepted)
    alt_check = recount_from_per_frame(accepted, d_star)
    frozen_agrees = all(
        [round(v, 9) for v in alt[sp]["frozen"]] == [round(v, 9) for v in reps[sp]] for sp in reps)
    alt_agrees = all(
        [round(v, 9) for v in alt[sp]["most_druggable"]] == [round(v, 9) for v in alt_check[sp]]
        for sp in alt_check)

    per_paralogue = {}
    for p in PARALOGUES:
        v = pairwise_verdict(reps["NR4A3"], reps[p], pooled["NR4A3"], pooled[p])
        alt_reps3, alt_repsp = alt["NR4A3"]["most_druggable"], alt[p]["most_druggable"]
        alt_v = pairwise_verdict(alt_reps3, alt_repsp,
                                 sum(alt_reps3) / 3.0, sum(alt_repsp) / 3.0)
        per_paralogue[p] = {
            "rt_asymmetric_axis": AXIS[p],
            "nr4a3_replicates": reps["NR4A3"],
            "paralogue_replicates": reps[p],
            "pooled_frac_ge_dstar": {"NR4A3": pooled["NR4A3"], p: pooled[p]},
            "verdict_under_the_frozen_rule": v,
            "exact_ranksum_permutation": exact_ranksum(reps["NR4A3"], reps[p]),
            "exact_mean_permutation": exact_mean_permutation(reps["NR4A3"], reps[p]),
            "effect_size_cliffs_delta": cliffs_delta(reps["NR4A3"], reps[p]),
            "cluster_bootstrap": cluster_bootstrap_difference(reps["NR4A3"], reps[p]),
            "fragility_one_more_replicate": one_more_replicate_fragility(reps["NR4A3"], reps[p]),
            "sensitivity_to_the_contested_C2_rule": {
                "_what": "the SAME replicate-granularity rule, re-evaluated under the ordering that would "
                         "prefer the most druggable ACCEPTED cavity. `C2` is registered ⚠ CONTESTED in the "
                         "roadmap §3b.2 (the 10-residue site splits across two accepted cavities in the "
                         "generation frame: Jaccard 0.21, centroids 9.853 Å apart).",
                "_does_not_license": "a rule change, or quoting these fractions as the site. The frozen "
                                     "rule remains the rule; this measures what the choice costs.",
                "nr4a3_replicates": alt_reps3,
                "paralogue_replicates": alt_repsp,
                "verdict": alt_v,
                "margin": round(min(alt_reps3) - max(alt_repsp), 6),
                "exact_ranksum_permutation": exact_ranksum(alt_reps3, alt_repsp),
                "survives_the_rule_change": alt_v["separated"],
            },
        }

    # DERIVED from the rows, never typed — and required to be one number across every unbiased replicate of
    # every species, because a design effect computed against the wrong denominator is silently wrong.
    per_rep_n = sorted({r["n_propagated"] for r in contrast["rows"]
                        if r["ensemble"] in UNBIASED})
    if len(per_rep_n) != 1:
        raise SystemExit(f"⛔ unbiased replicates do not share a denominator: {per_rep_n} — the design "
                         "effect below would be computed against the wrong n. Refusing.")
    m_frames = per_rep_n[0]

    deff = {sp: design_effect(reps[sp], m_frames) for sp in ("NR4A3",) + PARALOGUES}
    for p in PARALOGUES:
        per_paralogue[p]["design_corrected_wilson_overlap"] = {
            "_what": "does the DESIGN-EFFECT-CORRECTED pooled interval still separate? A third, "
                     "independent reading of the same caution — it uses the pooled frames rather than "
                     "the replicate ranks, so it can disagree with the permutation test.",
            "NR4A3": deff["NR4A3"]["wilson95_design_corrected"],
            p: deff[p]["wilson95_design_corrected"],
            **intervals_overlap(deff["NR4A3"]["wilson95_design_corrected"],
                                deff[p]["wilson95_design_corrected"]),
            "uncorrected_would_have_said": intervals_overlap(
                deff["NR4A3"]["wilson95_uncorrected"], deff[p]["wilson95_uncorrected"]),
        }

    holm_adj = holm([(p, per_paralogue[p]["exact_ranksum_permutation"]["p_one_sided_a_greater"])
                     for p in PARALOGUES])
    for p in PARALOGUES:
        per_paralogue[p]["exact_ranksum_permutation"]["p_one_sided_holm_adjusted_over_2_paralogues"] = \
            holm_adj[p]

    mandatory = per_paralogue["NR4A1"]
    best_effort = per_paralogue["NR4A2"]
    split = (mandatory["verdict_under_the_frozen_rule"]["separated"] !=
             best_effort["verdict_under_the_frozen_rule"]["separated"])
    robust = mandatory["sensitivity_to_the_contested_C2_rule"]["survives_the_rule_change"]

    if split and robust:
        headline = ("ASYMMETRIC — SEPARATED on the mandatory axis, OVERLAPPING on the best-effort axis, "
                    "and the mandatory separation survives the contested C2 rule")
        status = "LIVE"
    elif split and not robust:
        headline = ("ASYMMETRIC AT THE FROZEN RULE, BUT THE MANDATORY SEPARATION DOES NOT SURVIVE THE "
                    "CONTESTED C2 RULE — report the split verdict, do NOT report SEPARATED unqualified")
        status = "LIVE BUT DEMOTED — the asymmetry is real, the word SEPARATED is not carryable"
    elif not split:
        headline = ("NOT ASYMMETRIC — both paralogues return the same verdict under the artifact's own "
                    "rule, so the pooled verdict hides nothing")
        status = "DEAD"
    else:
        headline = "INDETERMINATE"
        status = "INDETERMINATE"

    return {
        "_title": "IC-4-A — does the paralogue cryptic-pocket contrast carry ONE verdict or TWO? A $0 "
                  "re-read of committed artifacts, split along RT-ASYMMETRIC's mandatory / best-effort axes",
        "_status": "INSTRUMENT RE-READ. $0 CPU. No new compute of any kind. Nothing here is a claim about "
                   "binding, reactivity, degradation, selectivity in vivo, efficacy or safety.",
        "_what_this_measures": "Whether `paralogue-pocket-contrast.json`'s single pooled verdict is driven "
                               "by one paralogue rather than both, whether the per-paralogue reading "
                               "survives an honest small-n interrogation, and whether it survives the "
                               "contested `C2` cavity-selection rule.",
        "_adds_no_data": "Every input is a committed artifact. No fpocket run, no MD, no GPU, no rental. "
                         "The source artifact is NOT modified.",
        "_licenses": contrast.get("_licenses"),
        "_ceilings_inherited": {
            "_from": "research/modalities/paralogue-pocket-contrast.json -> _does_not_license",
            "_binding": "these travel with every statement in this file, unchanged and unweakened",
            "entries": contrast.get("_does_not_license"),
        },
        "_inputs": {
            "contrast": "research/modalities/paralogue-pocket-contrast.json",
            "accepted_candidates": "research/modalities/pocket-accepted-candidates.json",
            "site_choice_audit": "research/modalities/r3-site-choice-audit.json",
            "axis_assignment": "systems/views/L2-rt-asymmetric.md (generated from systems/graph)",
        },
        "_provenance_checks": {
            "_why": "CLAUDE.md §4: a populated field is not a measured one. Both inputs are re-derived "
                    "here rather than trusted, and a disagreement is a visible failure.",
            "frozen_replicate_fracs_agree_between_the_two_artifacts": frozen_agrees,
            "alternative_rule_summary_agrees_with_a_recount_from_per_frame": alt_agrees,
            "d_star_contrast": d_star,
            "d_star_accepted_candidates": accepted["d_star"],
            "d_star_agrees": d_star == accepted["d_star"],
            "match_params_agree": contrast["detector"]["match_params"] == accepted["match_params"],
            "n_refusals_contrast": contrast.get("n_refusals"),
            "n_refusals_accepted_candidates": accepted.get("n_refusals"),
            "status": ("ALL CHECKS PASS" if (frozen_agrees and alt_agrees and
                                             d_star == accepted["d_star"] and
                                             contrast["detector"]["match_params"] ==
                                             accepted["match_params"])
                       else "⛔ AN INPUT DISAGREES — do not read the verdict below until this is resolved"),
        },
        "_the_defect_in_the_source_verdict": {
            "source_verdict": contrast["map_edits_required"]["verdict"],
            "source_rule": contrast["map_edits_required"]["verdict_basis"]["rule"],
            "mechanism": "`paralogue_pocket_contrast.build_map_edits` computes "
                         "`sep = r3[0] > r1[1] and r3[0] > r2[1]` — ONE boolean over BOTH paralogues. The "
                         "conjunction is false as soon as either paralogue fails, and the emitted verdict "
                         "string names neither, so a reader cannot tell which one failed or whether both "
                         "did.",
            "why_it_matters": "RT-ASYMMETRIC holds NR4A1-sparing MANDATORY and NR4A2-sparing BEST-EFFORT, "
                              "and its route record states that dropping the asymmetry lets a symmetric "
                              "restatement back in. A conjoined verdict reports the best-effort axis's "
                              "answer on the mandatory axis's behalf.",
            "⚠_not_a_numerical_error": "no number in `paralogue-pocket-contrast.json` is wrong, and its "
                                       "rule is not loosened here. The reported numbers reproduce exactly; "
                                       "what is at issue is that one flag is emitted where the program's "
                                       "own route structure asks two questions.",
        },
        "per_paralogue": per_paralogue,
        "small_n_interrogation": {
            "_question": "does a 3-vs-3 'worst beats best' comparison support the word SEPARATED, or is it "
                         "an artifact of small n?",
            "n_replicates_per_species": 3,
            "frames_per_replicate": m_frames,
            "exact_test_design_ceiling": {
                "n_permutations": 20,
                "best_attainable_p_one_sided": 0.05,
                "best_attainable_p_two_sided": 0.1,
                "⚠": "at 3 vs 3 NO outcome can return p < 0.05 one-sided. 'worst beats best' IS complete "
                     "separation, so the artifact's rule fires exactly when the exact test hits its floor "
                     "— the rule is calibrated to the strongest evidence the design can produce, and it "
                     "CANNOT produce more. A p of 0.05 here must be read as 'the design's ceiling', never "
                     "as 'just significant'.",
            },
            "multiplicity": {
                "_what": "two paralogue comparisons were made from one dataset. Holm-adjusted one-sided "
                         "p-values are carried on each `exact_ranksum_permutation` block.",
                "holm_adjusted_one_sided": holm_adj,
                "⚠": "with a per-test FLOOR of 0.05 and a family of two, NO outcome of this design can "
                     "return a Holm-adjusted p below 0.10. So the NR4A1 result cannot clear α = 0.05 "
                     "family-wise, and the honest statement is a RANKING with a stated effect size, not "
                     "a significance claim.",
                "_direction_was_prespecified": "one-sided is defensible because Route A's premise fixes "
                                               "the direction (NR4A3 opens more) before the data. The "
                                               "TWO-SIDED floor is 0.10, so even the cleanest possible "
                                               "outcome fails a two-sided 0.05 at this n.",
            },
            "design_effect_measured": {
                "_why": "the source artifact asserts the pooled Wilson interval is anti-conservative "
                        "because the 75 frames are 3 correlated replicas. That is correct and was never "
                        "quantified; here it is measured per species.",
                "per_species": deff,
            },
        },
        "verdict": {
            "headline": headline,
            "lead_status": status,
            "mandatory_axis_NR4A1": mandatory["verdict_under_the_frozen_rule"]["verdict"],
            "best_effort_axis_NR4A2": best_effort["verdict_under_the_frozen_rule"]["verdict"],
            "pooled_verdict_it_replaces": contrast["map_edits_required"]["verdict"],
            "the_pooled_verdict_is_driven_by": (
                [p for p in PARALOGUES
                 if not per_paralogue[p]["verdict_under_the_frozen_rule"]["separated"]]),
            "⛔_what_this_still_does_not_license": [
                "an exclusion of NR4A1 — this is a RANKING on opening frequency and evidence of absence "
                "is not available at these ensemble sizes",
                "ΔG_open, or any free-energy statement. A detection fraction is not an opening penalty.",
                "reporting SEPARATED without the contested-`C2` sensitivity beside it",
                "any statement about binding, reactivity, degradation, selectivity in vivo, efficacy or "
                "safety",
            ],
        },
    }


def build_map_edits(result):
    """Roadmap edits this result requires — DESCRIBED, NOT APPLIED, same convention and same helper as
    `paralogue_pocket_contrast.build_map_edits`: every `current_text` is READ out of the live map, so an
    anchor that has moved yields a visible refusal rather than a mis-targeted edit."""
    import map_edits as ME
    text = ME.load_map()
    v = result["verdict"]
    m = result["per_paralogue"]["NR4A1"]
    b = result["per_paralogue"]["NR4A2"]
    sens = m["sensitivity_to_the_contested_C2_rule"]
    art = "research/modalities/paralogue-pocket-asymmetric-read.json -> per_paralogue"

    line = (
        "\n★ **Paralogue-matched cryptic-pocket contrast — and it is ASYMMETRIC, which one pooled verdict "
        "had hidden.** Under the source artifact's OWN rule (NR4A3's worst release replicate beats the "
        "paralogue's best), applied per paralogue rather than conjoined: **vs `NR4A1` (RT-ASYMMETRIC's "
        "MANDATORY axis) — " + m["verdict_under_the_frozen_rule"]["verdict"] + "**, replicates " +
        str(m["nr4a3_replicates"]) + " vs " + str(m["paralogue_replicates"]) + "; **vs `NR4A2` "
        "(BEST-EFFORT) — " + b["verdict_under_the_frozen_rule"]["verdict"] + "**, " +
        str(b["paralogue_replicates"]) + ". The pooled *" +
        result["_the_defect_in_the_source_verdict"]["source_verdict"] + "* is driven by " +
        ", ".join(v["the_pooled_verdict_is_driven_by"]) + " alone — "
        "[`paralogue-pocket-asymmetric-read.json`](../modalities/paralogue-pocket-asymmetric-read.json). "
        "⚠ **Three ceilings travel with it and it may not be quoted without them:** at 3 vs 3 the exact "
        "permutation test's FLOOR is p = 0.05 one-sided, so the NR4A1 result sits AT the design's ceiling "
        "and cannot go past it; the margin is " + str(m["fragility_one_more_replicate"]["margin"]) +
        " against an NR4A3 replicate SD of " +
        str(m["fragility_one_more_replicate"]["nr4a3_replicate_sd"]) + "; and under the ⚠ CONTESTED `C2` "
        "ordering the separation " + ("SURVIVES" if sens["survives_the_rule_change"] else
                                      "does NOT survive (margin " + str(sens["margin"]) + ")") +
        ". ⚠ Still a CONFORMATIONAL-SELECTION ranking with no free energy in it — not `ΔG_open`, `R6` "
        "untouched, and never an exclusion.")

    entries = [
        ME.edit(text, "§8 Route A",
                "### Route A — a warhead engaging paralogue-divergent pocket handles",
                "Route A's premise is that the cryptic pocket is itself a paralogue discriminator. The "
                "measured contrast reports ONE pooled verdict over BOTH paralogues, and the program's own "
                "route structure (RT-ASYMMETRIC) does not treat them as one requirement: NR4A1-sparing is "
                "MANDATORY, NR4A2-sparing is BEST-EFFORT. Split along that axis the answers differ, and "
                "the pooled string names neither paralogue — so the mandatory axis's answer is currently "
                "unreadable from the map. ⚠ The split changes no number and loosens no rule; it removes "
                "one `and`.",
                art, ME.append_after_line(line)),
        ME.edit(text, "§8 Route A — the IC-4 pooled verdict, if it has since been applied",
                "★ **Paralogue-matched cryptic-pocket contrast — measured",
                "If the earlier IC-4 edit has landed, its verdict line carries the pooled "
                "'RANKED but replicate ranges OVERLAP' string, which is the symmetric restatement "
                "RT-ASYMMETRIC's route record calls a defect. It should be superseded in place rather "
                "than duplicated (rule 1), with the old string retained as superseded.",
                art, ME.append_to_line(
                    " ⚠ **Superseded, retained — the pooled verdict is ASYMMETRIC and this line reports "
                    "the best-effort axis's answer on the mandatory axis's behalf: see "
                    "[`paralogue-pocket-asymmetric-read.json`](../modalities/"
                    "paralogue-pocket-asymmetric-read.json).**")),
    ]
    return {
        "_what": "Roadmap edits this result requires. DESCRIBED, NOT APPLIED — this run does not touch "
                 "`nr4a3-program-map.md`, `systems/graph/` or `systems/views/`.",
        "_how_anchors_are_kept_live": "`current_text` is read out of the live map at generation time; a "
                                      "missing or ambiguous anchor yields a visible refusal instead of a "
                                      "mis-targeted edit.",
        "_target_section": "§8 Route A",
        "⛔_not_filed_in_section_6": "Nothing here closes or opens a route. A paralogue that opens less "
                                    "often is a RANKING, not an exclusion.",
        "entries": entries,
        "verification": ME.verify(entries, text),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--stdout", action="store_true", help="print, write nothing")
    args = ap.parse_args(argv)

    contrast, accepted, audit = load(CONTRAST), load(ACCEPTED), load(AUDIT)
    result = build(contrast, accepted, audit)
    result["map_edits_required"] = build_map_edits(result)
    result["_generated"] = {
        "generator": "research/modalities/paralogue_pocket_asymmetric_read.py",
        "reads_only": sorted(result["_inputs"].values()),
        "writes": os.path.relpath(args.out, REPO),
    }
    blob = json.dumps(result, indent=1, ensure_ascii=False)
    if args.stdout:
        print(blob)
        return 0
    with open(args.out, "w") as fh:
        fh.write(blob + "\n")
    print("wrote", args.out)
    print("VERDICT:", result["verdict"]["headline"])
    print("LEAD:", result["verdict"]["lead_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
