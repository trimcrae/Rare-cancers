#!/usr/bin/env python3
"""WHAT WOULD ACTUALLY RESOLVE PARALOGUE SELECTIVITY IN-SILICO — the derivation behind
`selectivity-resolution-options.md`.

Nothing in the options memo is typed. This module DERIVES it:

  * the STRUCTURAL bound on each test (min attainable p = 1 / C(n_a + n_b, n_a)), which is a function of
    the number of MODELS and of nothing else;
  * the NOISE bound (power of the frozen decision rule against a true separation), against sigma_model
    measured from the landed panel rather than assumed;
  * the VARIANCE DECOMPOSITION that says how far replicates can ever get, and where they stop;
  * the DOLLARS, from `vast_cost_model`'s planning rate and reference-GPU-hour bases — the same path
    `vast-ladder-repricing.json` takes, so a ladder reprice moves these figures too.

⚠ WHAT THIS MODULE IS NOT. It is not a re-scoring of the NR-V04 retrospective, it proposes no amendment,
and it changes no preregistered criterion. `nrv04_retro_gate` is IMPORTED and called, never re-implemented,
so every p-value here is the frozen scorer's own. The landed panel is read from the EMITTED verdict
artifact, so this module cannot disagree with it.

★ THE TWO PROBLEMS ARE DIFFERENT AND EVERY OPTION MUST SAY WHICH IT SOLVES.

  (1) STRUCTURAL — a reference set too small to contain a p at or below alpha. The NR4A1-vs-NR4A3
      pairwise at n = 3 vs 2 enumerates C(5,3) = 10 arrangements, so its smallest attainable one-sided p
      is 0.10. No data can push it under 0.05. Replicates cannot touch it: the unit of independence is
      the co-fold MODEL (prereg 4a), and `exact_permutation_p` enumerates over MODEL-level values, so
      100 replicas per model leave the reference set at exactly 10 (`replicates_do_not_move_the_bound`).
      Only MODELS move it — or a statistic with a different reference set.

  (2) NOISE — a reference set that CAN reach alpha, on a test whose effect is small against its own
      spread. The primary contrast is here: at 3 vs 5 its minimum attainable p is 1/56 = 0.0179, well
      under alpha, so nothing structural stopped it. What stopped it is that the observed separation is
      a fraction of sigma_model. That is fixed by more models, less noise, or a better readout — and by
      nothing else.

A one-line summary a reader can check: **a bigger reference set is necessary but not sufficient.**
"""
from __future__ import annotations

import json
import math
import os
import random
from itertools import combinations

import nrv04_retro_gate as gate
import vast_cost_model as vcm

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICT_JSON = os.path.join(HERE, "nrv04-retro-verdict.json")
LADDER_JSON = os.path.join(HERE, "vast-ladder-repricing.json")

ALPHA = gate.ALPHA

#: Legs per co-fold model in the as-run panel (prereg 2b: MD_REPLICAS = velocity seeds 0 and 1).
AS_RUN_REPLICAS_PER_MODEL = 2

#: Co-fold GENERATION is not priced by the cost model — its one home is the "Co-fold / docking" basis in
#: `research/compute/pricing.md` section B, carried there as **ESTIMATED (~$0-50 for a batch), not measured**.
#: It is quoted here as an estimate and labelled as one; it is never summed into a derived total.
COFOLD_BATCH_USD_ESTIMATE = (0.0, 50.0)


# =============================================================================================================
# 1. THE STRUCTURAL BOUND — a function of MODEL counts, and of nothing else
# =============================================================================================================
def min_attainable_p(n_a, n_b):
    """Smallest one-sided p an exact permutation test on n_a vs n_b MODELS can ever return. PURE.

    The observed arrangement is included in the count (the frozen scorer's convention), so the floor is
    1 / C(n_a + n_b, n_a). This is a property of the DESIGN, not of the data — it holds whatever the
    values are, which is why an option that does not move it cannot rescue a test it has already blocked.
    """
    if n_a < 1 or n_b < 1:
        raise ValueError("both groups must be non-empty")
    return 1.0 / math.comb(n_a + n_b, n_a)


def reaches_alpha(n_a, n_b, alpha=ALPHA):
    """Can this DESIGN attain significance at all? PURE."""
    return min_attainable_p(n_a, n_b) <= alpha


def smallest_n_reaching_alpha(other_n, alpha=ALPHA, cap=40):
    """Fewest models in the first group so that the test can reach alpha at all, or None. PURE."""
    for n in range(1, cap + 1):
        if min_attainable_p(n, other_n) <= alpha:
            return n
    return None


def exact_size_bound(n_a, n_b, alpha=ALPHA):
    """The frozen rule's false-positive rate under exchangeability, EXACTLY and for free. PURE.

    Attainable p-values are k / C(n_a+n_b, n_a), so under the null P(p <= alpha) = floor(alpha*C)/C. The
    tier's other two conditions (right sign, below both) can only remove cases, so this is an upper bound
    on the CONCORDANT rate at delta = 0. It exists because a Monte-Carlo size estimate at a few hundred
    draws is noisy enough to look like a defect: at 1200 draws the n = 3 cell read 0.0625 against this
    bound's 0.0476, and 20,000 draws returned 0.0470 / 0.0475 / 0.0490 on three seeds. The analytic
    number settles that without spending simulations on it.
    """
    c = math.comb(n_a + n_b, n_a)
    return math.floor(alpha * c + 1e-12) / c


def paired_min_attainable_p(n_pairs):
    """Same question for a PAIRED (matched-model) design, whose reference set is the 2**n sign flips.

    Included because it is the one design change that BOTH cancels between-model structural variance and
    changes the reference set — and it changes it in the *unfavourable* direction at small n: 2**3 = 8
    gives a floor of 0.125, worse than the unpaired C(6,3) = 20. It only overtakes at n >= 5. PURE.
    """
    if n_pairs < 1:
        raise ValueError("n_pairs must be >= 1")
    return 1.0 / (2 ** n_pairs)


# =============================================================================================================
# 2. THE NOISE BOUND — power of the FROZEN rule, and the variance decomposition
# =============================================================================================================
def _p_less(a, b):
    """Exact one-sided permutation p, fast form. IDENTICAL to `gate.exact_permutation_p(a, b, 'less')['p']`.

    Why it is exact rather than an approximation: for fixed group sizes the statistic
    `mean(a) - mean(b) = S_a/n_a - (T - S_a)/n_b` is strictly increasing in the group-A sum S_a, because
    the pooled total T is permutation-invariant. So the p-value is a rank of subset SUMS — the same
    identity the criteria audit records as `rank_statistic`. `tests/test_selectivity_resolution_options.py`
    asserts zero deviation from the frozen scorer over random panels.
    """
    pooled = list(a) + list(b)
    obs = sum(a)
    n, k = len(pooled), len(a)
    hit = 0
    total = 0
    for pick in combinations(range(n), k):
        s = 0.0
        for i in pick:
            s += pooled[i]
        total += 1
        if s <= obs + 1e-12:
            hit += 1
    return hit / total


def variance_decomposition(sigma_model_level, sigma_leg, replicas_per_model=AS_RUN_REPLICAS_PER_MODEL):
    """Split the observed MODEL-level spread into a between-model part and a replicate part. PURE.

    A model-level value is the mean of `replicas_per_model` legs, so
        sigma_model_level^2 = sigma_between^2 + sigma_leg^2 / replicas
    and therefore the FLOOR that infinitely many replicates can ever reach is sigma_between.

    ⚠ This is the number that decides whether "more replicates" is worth anything at all, so it is
    reported with its own honesty flag: if sigma_leg^2/replicas exceeds the observed model-level
    variance the decomposition is INADMISSIBLE (the two SDs come from different panels — the leg SD is
    registered off the feasibility panel — and sampling error at these df is large), and the function
    says so instead of returning a negative variance.
    """
    var_total = sigma_model_level ** 2
    var_rep_component = (sigma_leg ** 2) / float(replicas_per_model)
    var_between = var_total - var_rep_component
    out = {
        "sigma_model_level_A": round(sigma_model_level, 4),
        "sigma_leg_A": round(sigma_leg, 4),
        "replicas_per_model": replicas_per_model,
        "variance_from_replicates": round(var_rep_component, 4),
        "variance_between_models": round(var_between, 4),
        "admissible": var_between > 0,
    }
    if var_between > 0:
        out["sigma_between_models_A"] = round(math.sqrt(var_between), 4)
        out["floor_at_infinite_replicates_A"] = round(math.sqrt(var_between), 4)
        out["fraction_of_model_level_variance_replicates_can_remove"] = round(var_rep_component / var_total, 4)
    else:
        out["sigma_between_models_A"] = None
        out["floor_at_infinite_replicates_A"] = None
        out["why_inadmissible"] = (
            "the registered leg sigma implies a replicate variance at or above the whole observed "
            "model-level variance. The two are measured on DIFFERENT panels (leg sigma off the "
            "feasibility panel, model-level spread off the landed retrospective) and both carry large "
            "sampling error at these df, so no between-model floor is claimed from them.")
    return out


def sigma_model_at_replicas(sigma_between, sigma_leg, replicas):
    """Model-level noise as a function of how many legs are averaged into each model. PURE."""
    return math.sqrt(sigma_between ** 2 + (sigma_leg ** 2) / float(replicas))


#: The exact enumeration is O(C(n, k)) per simulated panel, so a large design is not merely slow, it is
#: unrunnable (12 models/arm is C(36,12) ~ 1.3e9 arrangements PER SIMULATED PANEL). Rather than silently
#: substitute a sampled reference distribution — which would put an approximation inside a number the memo
#: reports as power — these functions return **None** past the cap and the artifact says so. The STRUCTURAL
#: bound is exact at every n and is never capped, which is deliberate: it is the load-bearing finding.
MAX_EXACT_ARRANGEMENTS = 20000
#: Total inner subset-sum evaluations allowed per power cell; simulations are traded against enumeration
#: size so a big design costs wall-clock, not silence.
POWER_WORK_BUDGET = 4_000_000


def _sims_for(arrangements, n_sims):
    return max(300, min(n_sims, int(POWER_WORK_BUDGET / max(1, arrangements))))


def power_primary(n1, n2, n3, sigma, delta, n_sims=2000, seed=11, alpha=ALPHA):
    """P(the FROZEN rule returns CONCORDANT) under Gaussian model-level noise.

    delta > 0 means NR4A1's true plateau is LOWER (more stable) by delta A — the registered direction.
    Replicates the frozen conjunction exactly: d < 0 AND NR4A1 below BOTH paralogue means AND p <= alpha
    (LOMO left that conjunction in AMENDMENT 3 defect 3 and is not applied here either).

    Returns None when the exact enumeration exceeds `MAX_EXACT_ARRANGEMENTS` — see that constant.
    """
    if min_attainable_p(n1, n2 + n3) > alpha:
        return 0.0
    arrangements = math.comb(n1 + n2 + n3, n1)
    if arrangements > MAX_EXACT_ARRANGEMENTS:
        return None
    n_sims = _sims_for(arrangements, n_sims)
    r = random.Random(seed)
    hits = 0
    for _ in range(n_sims):
        a = [r.gauss(-delta, sigma) for _ in range(n1)]
        b2 = [r.gauss(0.0, sigma) for _ in range(n2)]
        b3 = [r.gauss(0.0, sigma) for _ in range(n3)]
        pooled = b2 + b3
        ma = sum(a) / n1
        if ma - sum(pooled) / len(pooled) >= 0:
            continue
        if not (ma < sum(b2) / n2 and ma < sum(b3) / n3):
            continue
        if _p_less(a, pooled) <= alpha:
            hits += 1
    return hits / n_sims


def power_pairwise(n1, n3, sigma, delta, n_sims=2000, seed=13, alpha=ALPHA):
    """P(the NR4A1-vs-NR4A3 exact pairwise reaches alpha). Returns 0.0 when the design cannot reach it,
    and None when the exact enumeration is past `MAX_EXACT_ARRANGEMENTS`."""
    if min_attainable_p(n1, n3) > alpha:
        return 0.0
    arrangements = math.comb(n1 + n3, n1)
    if arrangements > MAX_EXACT_ARRANGEMENTS:
        return None
    n_sims = _sims_for(arrangements, n_sims)
    r = random.Random(seed)
    hits = 0
    for _ in range(n_sims):
        a = [r.gauss(-delta, sigma) for _ in range(n1)]
        b = [r.gauss(0.0, sigma) for _ in range(n3)]
        if _p_less(a, b) <= alpha:
            hits += 1
    return hits / n_sims


#: One-sided z at alpha = 0.05 and at 80 % power. Only used by the LARGE-n normal approximation below,
#: which exists because the exact enumeration is unrunnable there — never for a reported exact figure.
_Z_ALPHA_05 = 1.6449
_Z_POWER_80 = 0.8416


def n_models_for_power_normal(delta, sigma, contrast="pairwise", z_alpha=_Z_ALPHA_05, z_beta=_Z_POWER_80):
    """Models per arm for 80 % power, by the NORMAL approximation. LABELLED, because it is one.

    pairwise (n vs n):  Var(diff) = 2*sigma^2/n   -> n = 2 (z_a+z_b)^2 sigma^2 / delta^2
    primary  (n vs 2n): Var(diff) = 1.5*sigma^2/n -> n = 1.5 (z_a+z_b)^2 sigma^2 / delta^2

    ⚠ It is an approximation in the direction that matters: an exact permutation test on a discrete
    lattice is slightly LESS powerful than its normal counterpart, so these n are a LOWER bound on what
    the frozen rule would need. `power_primary` / `power_pairwise` are the exact figures wherever the
    enumeration is runnable, and `normal_approximation_cross_check` compares the two where they overlap.
    """
    k = {"pairwise": 2.0, "primary": 1.5}[contrast]
    return math.ceil(k * ((z_alpha + z_beta) ** 2) * (sigma ** 2) / (delta ** 2))


def normal_approximation_cross_check(sigma, n_sims=2000, seed=29):
    """Where both are computable, does the normal approximation agree with the exact simulation?

    Reported rather than asserted: the memo uses the approximation only for n far past the exact cap, so
    a reader is owed the comparison at the n where both exist."""
    out = {}
    for n in (3, 4, 5, 6):
        delta_needed = math.sqrt(2.0 * ((_Z_ALPHA_05 + _Z_POWER_80) ** 2) * sigma ** 2 / n)
        exact = power_pairwise(n, n, sigma, delta_needed, n_sims=n_sims, seed=seed)
        out[f"n={n}"] = {"delta_the_approximation_calls_80pct_A": round(delta_needed, 3),
                         "exact_permutation_power_there": None if exact is None else round(exact, 4)}
    return out


def budget_allocation(total_legs_per_arm, sigma_between, sigma_leg, delta,
                      replicas_options=(1, 2, 4), n_sims=1200, seed=17, alpha=ALPHA):
    """★ THE ONE THAT CHANGES THE ANSWER: at a FIXED leg budget, how should legs be split between
    MODELS and REPLICATES?

    `total_legs_per_arm` legs buy `total_legs_per_arm / r` models at r replicas each. More replicates
    buy a quieter model-level value; more models buy a bigger reference set AND more n. Since the
    structural bound depends only on model count, r = 1 is the only allocation that can lift a pairwise
    out of the unresolvable region without buying a single extra leg.
    """
    out = {}
    for r in replicas_options:
        n_models = total_legs_per_arm // r
        if n_models < 2:
            continue
        sig = sigma_model_at_replicas(sigma_between, sigma_leg, r)
        pp = power_primary(n_models, n_models, n_models, sig, delta, n_sims=n_sims, seed=seed, alpha=alpha)
        qq = power_pairwise(n_models, n_models, sig, delta, n_sims=n_sims, seed=seed, alpha=alpha)
        out[f"{r}_replicas_x_{n_models}_models"] = {
            "replicas_per_model": r,
            "models_per_arm": n_models,
            "legs_per_arm": n_models * r,
            "sigma_model_A": round(sig, 4),
            "primary_min_attainable_p": round(min_attainable_p(n_models, 2 * n_models), 6),
            "pairwise_min_attainable_p": round(min_attainable_p(n_models, n_models), 6),
            "pairwise_can_reach_alpha": reaches_alpha(n_models, n_models, alpha),
            "power_primary": None if pp is None else round(pp, 4),
            "power_pairwise": None if qq is None else round(qq, 4),
        }
    return out


# =============================================================================================================
# 3. THE LANDED PANEL — read from the EMITTED verdict, never retyped
# =============================================================================================================
def landed_panel(path=VERDICT_JSON):
    """Model-level values, per-arm SDs and the pooled within-arm model-level SD, from the emitted verdict."""
    with open(path) as f:
        v = json.load(f)["verdict"]
    arms = {a: [ms[k] for k in sorted(ms, key=int)] for a, ms in v["model_level_means"].items()}
    groups = [arms[a] for a in sorted(arms)]
    ss = 0.0
    df = 0
    for g in groups:
        if len(g) < 2:
            continue
        m = sum(g) / len(g)
        ss += sum((x - m) ** 2 for x in g)
        df += len(g) - 1
    sigma_model = math.sqrt(ss / df) if df else None
    return {
        "source": os.path.basename(path),
        "model_level_values": arms,
        "models_per_arm": {a: len(g) for a, g in arms.items()},
        "pooled_within_arm_model_level_SD_A": round(sigma_model, 4) if sigma_model else None,
        "df": df,
        "_what_this_SD_is": (
            "the spread of MODEL-level values inside an arm — the noise the permutation test actually "
            "competes against. It is NOT the registered leg-to-leg sigma (0.855 A, "
            "`nrv04_retro_gate.MEASURED_LEG_SIGMA_A`), which is measured between velocity replicas of "
            "ONE model and is therefore a different and smaller quantity."),
        "observed_primary_stat_A": v["primary"]["stat"],
        "observed_pairwise_nr4a3_stat_A": v["pairwise_secondary"]["retro_noncov_nr4a3"]["stat"],
        "observed_pairwise_nr4a2_stat_A": v["pairwise_secondary"]["retro_noncov_nr4a2"]["stat"],
        "tier": v["tier"],
    }


def replicates_do_not_move_the_bound(path=VERDICT_JSON, replica_counts=(2, 8, 20, 100)):
    """Run the FROZEN scorer on the landed model means duplicated into 2 / 8 / 20 / 100 legs per model.

    The reference sets must be IDENTICAL across all of them. That is the evidence for the claim that no
    amount of replicate sampling can move a structural bound — it is a demonstration on the real scorer,
    not an argument about it."""
    with open(path) as f:
        v = json.load(f)["verdict"]
    means = {a: {int(k): val for k, val in ms.items()} for a, ms in v["model_level_means"].items()}
    out = {}
    for n_rep in replica_counts:
        legs = [{"arm_id": a, "cofold_model_seed": s, "e1_plateau_A": mu}
                for a, ms in means.items() for s, mu in ms.items() for _ in range(n_rep)]
        r = gate.verdict(legs)
        out[f"{n_rep}_replicas_per_model"] = {
            "n_legs": len(legs),
            "primary_n_arrangements": r["primary"]["n_arrangements"],
            "primary_min_attainable_p": round(r["primary"]["min_attainable_p"], 6),
            "pairwise_nr4a3_n_arrangements": r["pairwise_secondary"]["retro_noncov_nr4a3"]["n_arrangements"],
            "pairwise_nr4a3_min_attainable_p": round(
                r["pairwise_secondary"]["retro_noncov_nr4a3"]["min_attainable_p"], 6),
            "tier": r["tier"],
        }
    return out


# =============================================================================================================
# 4. COSTS — derived through `vast_cost_model`, never typed
# =============================================================================================================
def planning_rates(path=LADDER_JSON):
    """The plan / best / median $ per reference GPU-hour, from the committed ladder reprice.

    One home, per CLAUDE.md rule 1: `vast-ladder-repricing.json`, itself regenerated by
    `vast_cost_model._main` from a market snapshot. Nothing here re-derives a market rate."""
    with open(path) as f:
        d = json.load(f)
    lo, hi = d["range_usd_per_reference_gpu_h"]
    return {"plan_usd_per_reference_gpu_h": d["plan_usd_per_reference_gpu_h"],
            "best_usd_per_reference_gpu_h": lo, "median_usd_per_reference_gpu_h": hi,
            "source": os.path.basename(path)}


#: Reference GPU-hours per unit, taken from the cost model's own bases so a reprice moves these too.
ENDPOINT_MD_LEG_REF_GPU_H = vcm.ENDPOINT_MD_REF_GPU_H_PER_LEG
#: A 3-replica ternary EDGE is 6 legs (3 ternary + 3 binary; solvent is smaller and shared) at the
#: `valB_mini` basis, so the per-leg figure is that stage's reference GPU-hours divided by 6.
_VALB_MINI_KEY = "valB_mini (1 ternary edge, 3 replicas)"
TERNARY_LEG_REF_GPU_H = tuple(round(x / 6.0, 3) for x in vcm.LADDER_REFERENCE_GPU_H[_VALB_MINI_KEY])


#: Arm F is already a priced ladder stage. Its cost has ONE home and this module reads it rather than
#: deriving a second figure for the same work (CLAUDE.md rule 1).
_ARM_F_LADDER_KEY = "nrv04_retrospective (3 ternary legs + shared binary/solvent)"


def ladder_stage_cost(key, rates=None, path=LADDER_JSON):
    """A stage's cost READ from the repriced ladder, in `price_units`'s shape. Never re-derived here."""
    with open(path) as f:
        row = json.load(f)["ladder"][key]
    g_lo, g_hi = row["ref_gpu_h"]
    return {"n_units": 1, "ref_gpu_h_per_unit": [g_lo, g_hi],
            "ref_gpu_h_total": round((g_lo + g_hi) / 2.0, 2),
            "plan_usd": round(row["plan_usd"], 2),
            "range_usd": [round(row["range_usd"][0], 2), round(row["range_usd"][1], 2)],
            "_source": "%s -> ladder['%s']" % (os.path.basename(path), key)}


def price_units(n_units, ref_gpu_h_per_unit, rates=None):
    """Dollars for `n_units` units of `ref_gpu_h_per_unit` each. DERIVED — never a hand-sum."""
    rates = rates or planning_rates()
    if isinstance(ref_gpu_h_per_unit, (tuple, list)):
        g_lo, g_hi = float(ref_gpu_h_per_unit[0]), float(ref_gpu_h_per_unit[1])
    else:
        g_lo = g_hi = float(ref_gpu_h_per_unit)
    mid = (g_lo + g_hi) / 2.0
    return {
        "n_units": n_units,
        "ref_gpu_h_per_unit": [g_lo, g_hi] if g_lo != g_hi else g_lo,
        "ref_gpu_h_total": round(n_units * mid, 2),
        "plan_usd": round(n_units * mid * rates["plan_usd_per_reference_gpu_h"], 2),
        "range_usd": [round(n_units * g_lo * rates["best_usd_per_reference_gpu_h"], 2),
                      round(n_units * g_hi * rates["median_usd_per_reference_gpu_h"], 2)],
    }


def needs_review_gate(priced, threshold_usd=50.0):
    """CLAUDE.md section 3: does this option cross the >$50 reviewer-block threshold?

    Judged on the TOP of the range, not the plan figure — a stage whose bad case is $80 is a stage that
    can spend $80, and the gate exists for what can be spent."""
    return priced["range_usd"][1] > threshold_usd


# =============================================================================================================
# 5. THE OPTION BOARD
# =============================================================================================================
def _endpoint_md_option(label, legs, what_it_buys, what_it_cannot_buy, attacks, rates):
    p = price_units(legs, ENDPOINT_MD_LEG_REF_GPU_H, rates)
    return {"option": label, "engine": "endpoint MD (nrv04_covalent_md lane)", "gpu_legs": legs,
            "attacks": attacks, "buys": what_it_buys, "cannot_buy": what_it_cannot_buy,
            "cost": p, "crosses_50usd_review_gate": needs_review_gate(p)}


def build_options(rates=None, n_sims=1200):
    """Every option, its design consequence and its DERIVED cost. Returns a list of dicts.

    `n_sims` is accepted so a caller can trade fidelity for speed uniformly across the artifact; the option
    board itself reports DESIGN properties (reference sets, floors, costs), which are exact, and points at
    `power_primary` / `power_pairwise` for the simulated ones."""
    rates = rates or planning_rates()
    panel = landed_panel()
    n_now = panel["models_per_arm"]
    n1, n2, n3 = (n_now["retro_noncov_nr4a1"], n_now["retro_noncov_nr4a2"], n_now["retro_noncov_nr4a3"])

    opts = []

    # --- A. more MODELS, same readout ---------------------------------------------------------------
    for label, target in (("A1 restore NR4A3 to n = 3", 3), ("A2 balanced n = 6/arm", 6),
                          ("A3 balanced n = 10/arm", 10)):
        add = max(0, target - n1) + max(0, target - n2) + max(0, target - n3)
        legs = add * AS_RUN_REPLICAS_PER_MODEL
        o = _endpoint_md_option(
            label, legs,
            what_it_buys=("primary reference set C(%d,%d) = %d, min attainable p %.4f; "
                          "NR4A1-vs-NR4A3 pairwise C(%d,%d) = %d, min attainable p %.4f"
                          % (3 * target, target, math.comb(3 * target, target),
                             min_attainable_p(target, 2 * target),
                             2 * target, target, math.comb(2 * target, target),
                             min_attainable_p(target, target))),
            what_it_cannot_buy="nothing about the endpoint's effect-size-to-noise ratio",
            attacks="STRUCTURAL and NOISE (n enters both)", rates=rates)
        o["new_models"] = add
        o["design"] = {"models_per_arm": target,
                       "primary_min_attainable_p": round(min_attainable_p(target, 2 * target), 6),
                       "pairwise_min_attainable_p": round(min_attainable_p(target, target), 6),
                       "pairwise_can_reach_alpha": reaches_alpha(target, target)}
        o["cofold_generation_usd_ESTIMATE_not_derived"] = list(COFOLD_BATCH_USD_ESTIMATE)
        opts.append(o)

    # --- B. more REPLICATES, same models ------------------------------------------------------------
    for label, r_target in (("B1 4 replicas/model", 4), ("B2 6 replicas/model", 6)):
        legs = (n1 + n2 + n3) * (r_target - AS_RUN_REPLICAS_PER_MODEL)
        o = _endpoint_md_option(
            label, legs,
            what_it_buys="a quieter model-level value, bounded below by sigma_between (see "
                         "`variance_decomposition`)",
            what_it_cannot_buy="⛔ CANNOT move ANY reference set. NR4A1-vs-NR4A3 stays at C(5,3) = 10, "
                               "min attainable p 0.10 > alpha — structurally unresolvable at any replicate "
                               "count, which `replicates_do_not_move_the_bound` demonstrates on the frozen "
                               "scorer at 100 replicas/model",
            attacks="NOISE only", rates=rates)
        o["design"] = {"models_per_arm": [n1, n2, n3], "replicas_per_model": r_target,
                       "primary_min_attainable_p": round(min_attainable_p(n1, n2 + n3), 6),
                       "pairwise_min_attainable_p": round(min_attainable_p(n1, n3), 6),
                       "pairwise_can_reach_alpha": reaches_alpha(n1, n3)}
        opts.append(o)

    # --- C. a different READOUT ---------------------------------------------------------------------
    zero = {"n_units": 0, "ref_gpu_h_per_unit": 0.0, "ref_gpu_h_total": 0.0, "plan_usd": 0.0,
            "range_usd": [0.0, 0.0]}
    opts.append({
        "option": "C0 re-derive E2/E3/E4 signal-to-noise from the 16 LANDED legs",
        "engine": "CPU/CI only — no GPU", "gpu_legs": 0, "attacks": "NOISE (endpoint selection)",
        "buys": "the measured effect-size-to-noise of every already-computed endpoint, from data already "
                "bought. `nrv04_covalent_md` writes R1_interface / R2_recruitment / R3_lys into every leg "
                "JSON, and the frozen collector reads only R1 — so E2/E3/E4 exist for all 16 legs and have "
                "never been looked at.",
        "cannot_buy": "⛔ a RESULT. Choosing an endpoint on the same data that will then test it is "
                      "endpoint-shopping; this is a CALIBRATION input to a new preregistration, tested on "
                      "NEW models. It also cannot move any reference set.",
        "cost": zero, "crosses_50usd_review_gate": False,
        "precondition": "an S3 census must first confirm the 16 leg JSONs (and any analysis trajectories) "
                        "are present — an absent reading is not a reading of absence.",
    })
    # ⚠ NOT re-derived. Arm F ALREADY has a priced home — the ladder's own `nrv04_retrospective` row — and
    # deriving a second figure for the same stage is precisely the one-fact-one-place bug. Read it there.
    p_tern = ladder_stage_cost(_ARM_F_LADDER_KEY, rates)
    opts.append({
        "option": "C1 ternary ddG_coop (Arm F) as the readout",
        "engine": "ternary FEP lane (nr4a3_ternary_fep)", "gpu_legs": None,
        "cost_is_the_ladder_row": _ARM_F_LADDER_KEY,
        "attacks": "NOISE (a readout with a physical scale and a stated error bar)",
        "buys": "a free-energy quantity with replicate SDs, on the paralogue-panel identity (N ternary "
                "legs + one shared binary + one shared solvent, pricing.md B.0 identity 1)",
        "cannot_buy": "⛔ nothing structural — the same n models give the same reference set. AND it is "
                      "BLOCKED: prereg section 1 / calibration addendum condition 7 hold Arm F behind a "
                      "valB PASS, and valB module 1 returned NO (STRATEGY Open decision 9).",
        "cost": p_tern, "crosses_50usd_review_gate": needs_review_gate(p_tern),
        "blocked_by": "valB calibration condition 7 — not a spend decision, a preregistration one",
    })
    p_bsa = price_units(16, ENDPOINT_MD_LEG_REF_GPU_H, rates)
    opts.append({
        "option": "C2 buried-surface-area / full-sidechain contact readouts",
        "engine": "endpoint MD, re-run with TRAJ_ALL_HEAVY=1", "gpu_legs": 16,
        "attacks": "NOISE (endpoint selection)",
        "buys": "endpoints that need sidechain heavy atoms",
        "cannot_buy": "⛔ NOT re-derivable from what we hold. `md_analysis_traj.select_analysis_atoms` "
                      "persists CA + Cys SG + Lys NZ + non-polymer heavy atoms only, and says so — a BSA "
                      "or sidechain-contact readout therefore costs a FULL re-run of the panel, not an "
                      "analysis pass.",
        "cost": p_bsa, "crosses_50usd_review_gate": needs_review_gate(p_bsa)})

    # --- D. a different POSITIVE CONTROL ------------------------------------------------------------
    # 2 arms x 6 co-fold models x 2 velocity replicas — the smallest shape whose PAIRWISE reference set
    # is comfortably clear of alpha (C(12,6) = 924, floor 0.0011) while keeping the replicate structure
    # that makes an input-fault exclusion checkable.
    D_ARMS, D_MODELS, D_REPLICAS = 2, 6, 2
    d_legs = D_ARMS * D_MODELS * D_REPLICAS
    o = _endpoint_md_option(
        "D1 endpoint-MD positive control on SMARCA2-vs-SMARCA4 (same E1 readout, known-selective pair)",
        d_legs,
        what_it_buys="the thing that is actually missing: evidence that THIS readout can detect paralogue "
                     "selectivity where the answer is known. Structures are solved on BOTH arms "
                     "(s-calibrator-survey.json: SMARCA2 15 ternaries, SMARCA4 4), so neither arm is a "
                     "homology model — the asymmetry that makes 8G1Q a weak calibrator does not apply to a "
                     "structure-matched endpoint panel.",
        what_it_cannot_buy="⛔ nothing about NR4A. A pass licenses 'the readout can discriminate a known "
                           "paralogue pair'; it does NOT license a paralogue claim for NR4A3, and a FAIL "
                           "does not distinguish 'the readout is blunt' from 'this pair is hard'.",
        attacks="the MISSING POSITIVE CONTROL — neither of the two problems, and that is the point",
        rates=rates)
    o["note"] = ("distinct from valB_full module 3, which is an ALCHEMICAL cooperativity module behind the "
                 "valB gate. This is the endpoint-MD lane at endpoint-MD prices and asserts no free energy, "
                 "so condition 7 does not reach it — the same argument the prereg's section 9 RESOLUTION "
                 "used to run Arm E.")
    o["design"] = {"arms": D_ARMS, "models_per_arm": D_MODELS, "replicas_per_model": D_REPLICAS,
                   "pairwise_min_attainable_p": round(min_attainable_p(D_MODELS, D_MODELS), 6),
                   "pairwise_can_reach_alpha": reaches_alpha(D_MODELS, D_MODELS)}
    o["unresolved_and_it_must_be_preregistered"] = (
        "⚠ 'SYMMETRIC' in the survey means a deposited TERNARY EXISTS on each arm — it does NOT mean a "
        "matched-ligand crystal PAIR exists, and STRATEGY Open decision 9b measured why that matters: the "
        "ligand whose reference selectivity data we would calibrate against (Wurz compound 1) was "
        "co-crystallised ONLY with SMARCA4, and every deposited SMARCA2 ternary carries a DIFFERENT "
        "ligand. So the arms can be matched on ligand (one arm modelled) or matched on protein (ligand "
        "confounded with paralogue) — not both from crystals alone. An endpoint-MD panel escapes this only "
        "by CO-FOLDING one ligand onto both real paralogue sequences, using the deposited ternaries to "
        "validate each arm's co-fold rather than to supply it. That is a design decision, it is the same "
        "coupling decision 9b identified, and it belongs in the preregistration — not in a launch script.")
    o["existing_plumbing_and_its_limit"] = (
        "`smarca2_model.py` exists but builds SMARCA2 by homology MUTATION from the 3.73 A 8G1Q SMARCA4 "
        "chain — the asymmetric configuration this option is meant to avoid. New staging is therefore "
        "required. Engineering is free; the point is that it is not already built.")
    opts.append(o)
    o2 = _endpoint_md_option(
        "D2 endpoint-MD positive control on IKZF1-vs-IKZF3 (CRBN glue)", d_legs,
        what_it_buys="the only other structurally SYMMETRIC pair the $0 survey found (IKZF1 10 ternaries, "
                     "IKZF3 4), on a different E3 and a glue rather than a PROTAC",
        what_it_cannot_buy="⛔ the same limits as D1, plus: no primary-source selectivity value is in the "
                           "repo yet, and STRATEGY Open decision 7 binds — the accuracy band may not be "
                           "wider than the signal being calibrated.",
        attacks="the MISSING POSITIVE CONTROL (second, independent system)", rates=rates)
    opts.append(o2)

    # --- E. a different STATISTIC / DESIGN ----------------------------------------------------------
    opts.append({
        "option": "E1 PAIRED (matched-model) design + sign-flip permutation",
        "engine": "design change, no new engine", "gpu_legs": 0,
        "attacks": "NOISE (cancels between-model structural variance) — and CHANGES the reference set",
        "buys": "the dominant noise term cancels if models are matched across arms by construction",
        "cannot_buy": "⛔ at small n the reference set gets SMALLER, not bigger: 2**3 = 8 arrangements is a "
                      "floor of 0.125, WORSE than the unpaired C(6,3) = 20. It only overtakes at n >= 5.",
        "cost": zero, "crosses_50usd_review_gate": False,
        "paired_floor_by_n": {str(n): round(paired_min_attainable_p(n), 6) for n in range(3, 9)},
        "smallest_n_pairs_reaching_alpha": next(n for n in range(1, 20)
                                                if paired_min_attainable_p(n) <= ALPHA),
        "precondition": "the arms are NOT currently placement-matched (prereg section 2a/2c LIMITATION, "
                        "2026-07-31), so pairing must be built into the co-fold generation, not asserted "
                        "afterwards.",
    })
    opts.append({
        "option": "E2 REALLOCATE the same leg budget: 1 replica x more models",
        "engine": "design change, no new engine, no extra legs", "gpu_legs": 0,
        "attacks": "STRUCTURAL, at zero marginal GPU cost",
        "buys": "the same 16 legs bought 8 models at 2 replicas. At 1 replica they buy 16 models, and the "
                "reference set is a function of MODELS alone — so the pairwise leaves the unresolvable "
                "region without one extra GPU-hour. See `budget_allocation`.",
        "cannot_buy": "⛔ a quieter per-model value — each model-level value is then a single leg, so "
                      "sigma_model rises from sqrt(s_b^2 + s_leg^2/2) to sqrt(s_b^2 + s_leg^2). Whether the "
                      "n gain beats the noise loss is what `budget_allocation` computes; it is not free.",
        "cost": zero, "crosses_50usd_review_gate": False,
        "cofold_generation_usd_ESTIMATE_not_derived": list(COFOLD_BATCH_USD_ESTIMATE),
        "the_real_price_and_it_is_not_dollars": (
            "⚠ THE REPLICATE STRUCTURE IS WHAT MADE AMENDMENT 4's EXCLUSION CHECKABLE. Its section 4.2 "
            "discriminator was that BOTH replicas of nr4a3 seed_3 failed at the first production step "
            "while both replicas of every other co-fold produced frames — 'a thermostat seed cannot rescue "
            "two atoms at 0.181 A'. At one replica per model there is no sibling, so an input fault and a "
            "host-side death are no longer distinguishable from the run record, and every exclusion would "
            "have to rest on the staged-probe energy alone. That is a real loss of auditability bought "
            "with the statistical gain, and it must be preregistered as such, not discovered later."),
    })
    opts.append({
        "option": "E3 parametric test (mixed model / t) instead of exact permutation",
        "engine": "analysis change", "gpu_legs": 0,
        "attacks": "STRUCTURAL (a parametric p has no combinatorial floor)",
        "buys": "p is unbounded below, so no design is structurally unresolvable",
        "cannot_buy": "⛔ credibility, if adopted now. Swapping the test AFTER a failed result on the same "
                      "data is precisely the retune AMENDMENT 1's standard forbids, and n = 2-3 does not "
                      "support a normal approximation — which is WHY the prereg chose exact permutation. "
                      "Only admissible as a preregistered primary on a NEW panel, with its own "
                      "false-positive rate measured first.",
        "cost": zero, "crosses_50usd_review_gate": False,
    })

    # --- F. a new capability ------------------------------------------------------------------------
    opts.append({
        "option": "F1 a second co-fold ARCHITECTURE (DeepTernary / Protenix / IntFold) as a model source",
        "engine": "co-fold inference", "gpu_legs": 0,
        "attacks": "STRUCTURAL — more models, and more INDEPENDENT ones than re-seeding one generator",
        "buys": "models whose independence is architectural rather than a diffusion seed, which is the "
                "assumption prereg section 4a's unit of independence actually rests on",
        "cannot_buy": "⛔ any selectivity signal of its own — method-watch.md is explicit that generator "
                      "scores never rank selectivity, and DeepTernary is adopted as a conditional "
                      "GENERATOR only. It also cannot fix a blunt endpoint.",
        "cost": zero, "crosses_50usd_review_gate": False,
        "cofold_generation_usd_ESTIMATE_not_derived": list(COFOLD_BATCH_USD_ESTIMATE),
        "honest_not_yet": "no watched capability MEASURES paralogue selectivity. The method-watch row that "
                          "would change this answer — 'reliable structure-based generative + selectivity "
                          "scoring' — has NOT fired.",
    })
    return opts


# =============================================================================================================
# 6. THE RECOMMENDED SEQUENCE — serialized, because each step CAN cancel the next
# =============================================================================================================
#: Step 2's shape: 2 arms (the known-selective pair) x 6 co-fold models x 2 velocity replicas.
POSITIVE_CONTROL_SHAPE = {"arms": 2, "models_per_arm": 6, "replicas_per_model": 2}
#: Step 3's shape: 3 NR4A paralogues x 6 models x 2 replicas — the same design, on the real question.
NR4A_REPANEL_SHAPE = {"arms": 3, "models_per_arm": 6, "replicas_per_model": 2}


def _shape_legs(shape):
    return shape["arms"] * shape["models_per_arm"] * shape["replicas_per_model"]


def recommended_sequence(rates=None):
    """The cheapest-decisive-first sequence, with its cost DERIVED step by step and cumulatively.

    SERIALIZED on CLAUDE.md section 6's own litmus test — *"is there a result this step could return that
    would make me NOT run the rest?"* — and the answer is yes at every boundary, which is the whole reason
    this is a sequence rather than a fan-out:
      * step 1 returning "E1 is the best endpoint we have and its separation-to-noise is ~0.3 sigma"
        deletes the entire different-readout branch for $0;
      * step 2 returning a null on a KNOWN-selective, structure-matched pair at n = 6 models/arm says the
        readout cannot detect paralogue selectivity at all — in which case step 3 is money spent to
        reproduce a failure, and the honest paper reports predicted selectivity as UNVALIDATED.
    """
    rates = rates or planning_rates()
    steps = [
        {"step": 1, "name": "re-derive the endpoints we already own (E2/E3/E4) + an S3 census",
         "gpu_legs": 0, "cost": price_units(0, ENDPOINT_MD_LEG_REF_GPU_H, rates),
         "decides": "which readout the rest of the sequence uses, and whether any of them has a "
                    "separation-to-noise worth designing around",
         "could_cancel_the_rest": True},
        {"step": 2, "name": "positive control: the chosen readout on a known-selective, structure-matched "
                            "paralogue pair, at %(arms)d arms x %(models_per_arm)d models x "
                            "%(replicas_per_model)d replicas" % POSITIVE_CONTROL_SHAPE,
         "gpu_legs": _shape_legs(POSITIVE_CONTROL_SHAPE),
         "cost": price_units(_shape_legs(POSITIVE_CONTROL_SHAPE), ENDPOINT_MD_LEG_REF_GPU_H, rates),
         "decides": "whether this workflow can detect paralogue selectivity AT ALL where the answer is "
                    "known — the positive control the program does not currently have",
         "could_cancel_the_rest": True},
        {"step": 3, "name": "re-panel NR4A1/2/3 on the validated design, freshly preregistered, at "
                            "%(arms)d arms x %(models_per_arm)d models x %(replicas_per_model)d replicas"
                            % NR4A_REPANEL_SHAPE,
         "gpu_legs": _shape_legs(NR4A_REPANEL_SHAPE),
         "cost": price_units(_shape_legs(NR4A_REPANEL_SHAPE), ENDPOINT_MD_LEG_REF_GPU_H, rates),
         "decides": "the NR4A paralogue question itself, on a design whose power and reference sets were "
                    "fixed BEFORE the data",
         "could_cancel_the_rest": False,
         "runs_only_if": "step 2 PASSES. A null at step 2 makes step 3 uninterpretable, not merely weak."},
    ]
    cum = 0.0
    lo = hi = 0.0
    for s in steps:
        cum += s["cost"]["plan_usd"]
        lo += s["cost"]["range_usd"][0]
        hi += s["cost"]["range_usd"][1]
        s["cumulative_plan_usd"] = round(cum, 2)
        s["cumulative_range_usd"] = [round(lo, 2), round(hi, 2)]
    return {
        "_litmus": "CLAUDE.md section 6 — serialize ONLY when one result could cancel the rest. It can, "
                   "twice, so this is serial by decision value and not by physics.",
        "steps": steps,
        "total_plan_usd": round(cum, 2),
        "total_range_usd": [round(lo, 2), round(hi, 2)],
        "cofold_generation_usd_ESTIMATE_not_derived": list(COFOLD_BATCH_USD_ESTIMATE),
        "crosses_50usd_review_gate": hi > 50.0,
        "_measured_cross_check": (
            "the NR-V04 retrospective's own realised mean was $0.0979/leg over 17 measured legs with a "
            "$1.57 projected panel total (`nrv04-retro-price-forensics.json` -> ledger_summary), against "
            "the $%.3f/leg this planning rate derives. The plan figure is the CONSERVATIVE one. ⚠ That "
            "same ledger records $25.83 of LEAKED rental against $1.57 of compute — on this lane the "
            "dominant cost has been supervision, not GPU-hours, and no design change touches that."
            % (ENDPOINT_MD_LEG_REF_GPU_H * rates["plan_usd_per_reference_gpu_h"])),
    }


# =============================================================================================================
# 7. THE FULL ARTIFACT
# =============================================================================================================
def build(n_sims=1200, seed=11):
    rates = planning_rates()
    panel = landed_panel()
    sig_obs = panel["pooled_within_arm_model_level_SD_A"]
    sig_leg = gate.MEASURED_LEG_SIGMA_A
    n_now = panel["models_per_arm"]
    n1 = n_now["retro_noncov_nr4a1"]
    n3 = n_now["retro_noncov_nr4a3"]
    n_pooled = n_now["retro_noncov_nr4a2"] + n3

    decomp = variance_decomposition(sig_obs, sig_leg)
    sig_between = decomp["sigma_between_models_A"] if decomp["admissible"] else 0.0

    deltas = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0]
    doc = {
        "_what": "derivation behind selectivity-resolution-options.md — what would resolve paralogue "
                 "selectivity in-silico, what it costs, and which of the two problems each option solves",
        "_scorer": "nrv04_retro_gate (frozen, imported not reimplemented)",
        "_costs_from": "vast_cost_model bases x vast-ladder-repricing.json planning rate",
        "_not_an_amendment": "no preregistered criterion is proposed, changed or re-scored here",
        "alpha": ALPHA,
        "landed_panel": panel,
        "planning_rates": rates,
        "ref_gpu_h_bases": {"endpoint_md_leg": ENDPOINT_MD_LEG_REF_GPU_H,
                            "ternary_leg": list(TERNARY_LEG_REF_GPU_H),
                            "_source": "vast_cost_model.ENDPOINT_MD_REF_GPU_H_PER_LEG and "
                                       "LADDER_REFERENCE_GPU_H['%s'] / 6 legs" % _VALB_MINI_KEY},
    }

    # --- which problem is which -------------------------------------------------------------------
    doc["binding_constraint"] = {
        "primary_contrast": {
            "shape": "%d vs %d models" % (n1, n_pooled),
            "n_arrangements": math.comb(n1 + n_pooled, n1),
            "min_attainable_p": round(min_attainable_p(n1, n_pooled), 6),
            "reaches_alpha": reaches_alpha(n1, n_pooled),
            "verdict": "NOISE-LIMITED, not structurally limited — the design CAN reach alpha",
        },
        "pairwise_nr4a1_vs_nr4a3": {
            "shape": "%d vs %d models" % (n1, n3),
            "n_arrangements": math.comb(n1 + n3, n1),
            "min_attainable_p": round(min_attainable_p(n1, n3), 6),
            "reaches_alpha": reaches_alpha(n1, n3),
            "verdict": "STRUCTURALLY UNRESOLVABLE — no data can produce a p at or below alpha",
            "smallest_n3_that_reaches_alpha_against_n1": smallest_n_reaching_alpha(n1),
        },
        "pairwise_nr4a1_vs_nr4a2": {
            "shape": "%d vs %d models" % (n1, n_now["retro_noncov_nr4a2"]),
            "min_attainable_p": round(min_attainable_p(n1, n_now["retro_noncov_nr4a2"]), 6),
            "reaches_alpha": reaches_alpha(n1, n_now["retro_noncov_nr4a2"]),
            "verdict": "reaches alpha only at PERFECT separation (floor == alpha exactly)",
        },
        "_the_distinction": "these are TWO problems. An option that fixes one is silent on the other, and "
                            "an option that raises primary power to 0.9 while leaving NR4A1-vs-NR4A3 at "
                            "C(5,3) leaves that comparison STRUCTURALLY UNRESOLVABLE, in those words.",
    }
    doc["replicates_do_not_move_the_bound"] = replicates_do_not_move_the_bound()
    doc["variance_decomposition"] = decomp
    doc["effect_to_noise"] = {
        "sigma_model_measured_A": sig_obs,
        "observed_primary_separation_A": abs(panel["observed_primary_stat_A"]),
        "observed_pairwise_nr4a3_separation_A": abs(panel["observed_pairwise_nr4a3_stat_A"]),
        "primary_separation_in_sigma": round(abs(panel["observed_primary_stat_A"]) / sig_obs, 3),
        "pairwise_separation_in_sigma": round(abs(panel["observed_pairwise_nr4a3_stat_A"]) / sig_obs, 3),
        "_reading": "n needed for a fixed power scales as (sigma/delta)^2, so an effect this small "
                    "relative to sigma is not reachable by any affordable n. The design question is "
                    "therefore about the READOUT and the CONTROL, not about buying more of this one.",
    }

    # --- structural bound tables -------------------------------------------------------------------
    doc["structural_bound_primary_by_n"] = {
        str(n): {"contrast": "%d vs %d" % (n, 2 * n), "n_arrangements": math.comb(3 * n, n),
                 "min_attainable_p": round(min_attainable_p(n, 2 * n), 6),
                 "reaches_alpha": reaches_alpha(n, 2 * n)} for n in range(2, 11)}
    doc["structural_bound_pairwise_by_n"] = {
        str(n): {"contrast": "%d vs %d" % (n, n), "n_arrangements": math.comb(2 * n, n),
                 "min_attainable_p": round(min_attainable_p(n, n), 6),
                 "reaches_alpha": reaches_alpha(n, n)} for n in range(2, 11)}
    doc["structural_bound_paired_by_n"] = {
        str(n): {"n_arrangements": 2 ** n, "min_attainable_p": round(paired_min_attainable_p(n), 6),
                 "reaches_alpha": paired_min_attainable_p(n) <= ALPHA} for n in range(3, 11)}

    # --- power ------------------------------------------------------------------------------------
    def _r(x):
        return None if x is None else round(x, 4)

    sigmas = {"measured_model_level": sig_obs, "registered_leg_sigma": sig_leg}
    doc["exact_size_under_exchangeability"] = {
        "_what": "P(p <= alpha) at delta = 0, computed exactly from the p-lattice rather than simulated. "
                 "An UPPER bound on the CONCORDANT rate, since the tier's other conditions only remove "
                 "cases. Read the delta=0 row of the power tables against THIS, not against alpha.",
        "as_run_primary_3_vs_5": round(exact_size_bound(n1, n_pooled), 6),
        "balanced_primary_by_n": {str(n): round(exact_size_bound(n, 2 * n), 6) for n in range(3, 7)},
        "pairwise_by_n": {str(n): round(exact_size_bound(n, n), 6) for n in range(2, 7)},
    }
    doc["power_primary"] = {"_none_means": "the exact enumeration exceeds MAX_EXACT_ARRANGEMENTS — no "
                                           "sampled substitute is reported in its place",
                            "_mc_error": "Monte-Carlo. SE ~ sqrt(p(1-p)/n_sims); n_sims is traded against "
                                         "enumeration size by `_sims_for`, so a large design is noisier. "
                                         "Compare the delta=0 row to `exact_size_under_exchangeability`."}
    doc["power_pairwise_nr4a1_vs_nr4a3"] = {"_none_means": doc["power_primary"]["_none_means"],
                                            "_mc_error": doc["power_primary"]["_mc_error"]}
    for lab, sig in sigmas.items():
        doc["power_primary"]["%s=%.4f | AS-RUN %d/%d/%d" % (lab, sig, n1, n_now["retro_noncov_nr4a2"], n3)] = {
            str(d): _r(power_primary(n1, n_now["retro_noncov_nr4a2"], n3, sig, d,
                                     n_sims=n_sims, seed=seed)) for d in deltas}
        for n in (3, 4, 5, 6):
            doc["power_primary"]["%s=%.4f | balanced n=%d" % (lab, sig, n)] = {
                str(d): _r(power_primary(n, n, n, sig, d, n_sims=n_sims, seed=seed)) for d in deltas}
            doc["power_pairwise_nr4a1_vs_nr4a3"]["%s=%.4f | n=%d" % (lab, sig, n)] = {
                str(d): _r(power_pairwise(n, n, sig, d, n_sims=n_sims, seed=seed)) for d in deltas}
        doc["power_pairwise_nr4a1_vs_nr4a3"]["%s=%.4f | AS-RUN %d vs %d" % (lab, sig, n1, n3)] = {
            str(d): _r(power_pairwise(n1, n3, sig, d, n_sims=n_sims, seed=seed)) for d in deltas}

    # --- budget allocation ------------------------------------------------------------------------
    if decomp["admissible"]:
        doc["budget_allocation_at_fixed_legs"] = {
            "_what": "the SAME legs, split differently between models and replicates. sigma_between is "
                     "held at the decomposition's estimate and sigma_leg at the registered value.",
            "_delta_A": 1.0,
            "6_legs_per_arm": budget_allocation(6, sig_between, sig_leg, 1.0, n_sims=n_sims),
            "8_legs_per_arm": budget_allocation(8, sig_between, sig_leg, 1.0, n_sims=n_sims),
        }
    else:
        doc["budget_allocation_at_fixed_legs"] = {
            "_skipped": "the variance decomposition is inadmissible (see `variance_decomposition`), so no "
                        "sigma_between is available to hold fixed. The STRUCTURAL half of the reallocation "
                        "argument does not depend on it and is in `structural_bound_pairwise_by_n`."}

    # --- ★ can the OBSERVED effect be bought at all, and for how much? -----------------------------
    obs_pair = abs(panel["observed_pairwise_nr4a3_stat_A"])
    obs_prim = abs(panel["observed_primary_stat_A"])
    n_pair = n_models_for_power_normal(obs_pair, sig_obs, "pairwise")
    n_prim = n_models_for_power_normal(obs_prim, sig_obs, "primary")
    doc["price_of_resolving_the_OBSERVED_effect"] = {
        "_what": "if the true paralogue difference is the size this panel measured, how many models per "
                 "arm would 80 % power need — and what would that cost? The answer is the one that "
                 "reframes the whole question.",
        "_method": "normal approximation (`n_models_for_power_normal`) because the exact enumeration is "
                   "unrunnable at this n; it is a LOWER bound on the exact requirement",
        "normal_approximation_cross_check": normal_approximation_cross_check(sig_obs, n_sims=n_sims),
        "pairwise_nr4a1_vs_nr4a3": {
            "observed_separation_A": round(obs_pair, 4),
            "models_per_arm_needed": n_pair,
            "legs_at_2_arms_x_2_replicas": 2 * n_pair * 2,
            "cost": price_units(2 * n_pair * 2, ENDPOINT_MD_LEG_REF_GPU_H, rates)},
        "primary_pooled": {
            "observed_separation_A": round(obs_prim, 4),
            "models_per_arm_needed": n_prim,
            "legs_at_3_arms_x_2_replicas": 3 * n_prim * 2,
            "cost": price_units(3 * n_prim * 2, ENDPOINT_MD_LEG_REF_GPU_H, rates)},
        "_the_finding": (
            "⚠ THIS IS AFFORDABLE, AND THAT IS THE PROBLEM. At endpoint-MD prices a panel large enough to "
            "resolve the separation actually observed costs low hundreds of dollars, not thousands — so "
            "'we cannot afford the resolution' is FALSE and must not be written. What the money would buy "
            "is a statistically resolved sub-Angstrom difference in an interface-RMSD plateau, and the "
            "prereg's own claim ceiling (section 6) permits only DIRECTIONAL CONCORDANCE from it: no "
            "quantitative link between that plateau and degradation selectivity has ever been "
            "established. Buying resolution on an uncalibrated readout buys a precise number nobody can "
            "interpret. That is why the recommended sequence spends its first dollars on a POSITIVE "
            "CONTROL rather than on n."),
    }

    doc["options"] = build_options(rates=rates, n_sims=n_sims)
    doc["recommended_sequence"] = recommended_sequence(rates)
    doc["total_if_every_option_ran"] = {
        "_warning": "NOT a plan and NOT a recommendation — the options are alternatives, and the memo "
                    "recommends a sequence, not the sum.",
        "plan_usd": round(sum(o["cost"]["plan_usd"] for o in doc["options"]), 2),
        "range_usd": [round(sum(o["cost"]["range_usd"][0] for o in doc["options"]), 2),
                      round(sum(o["cost"]["range_usd"][1] for o in doc["options"]), 2)],
    }
    return doc


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="derive the selectivity-resolution option board")
    ap.add_argument("--out", default=os.path.join(HERE, "selectivity-resolution-options.json"))
    ap.add_argument("--sims", type=int, default=1200)
    a = ap.parse_args(argv)
    doc = build(n_sims=a.sims)
    with open(a.out, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print("wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
