#!/usr/bin/env python3
"""
Vast interruptible bidding as an OPTIMIZATION problem: least $ per COMPLETED unit, subject to a wall-clock cap.

⚠ STATUS (2026-07-25): THIS MODULE IS ADVISORY AND IS NOT ON THE LAUNCH PATH. The live policy lives in
`vast_cost_model.py` and is imported by `gpu_backend`; see `research/compute/bid-strategy.md`. What survives
here that the cost model does not have: a hazard/quantile treatment and a synthetic backtest, useful if a
preemption ledger is ever collected. Read the rest of this docstring as the ANALYSIS THAT LED TO THE REWRITE,
not as a description of what runs.

THE PROBLEM WITH THE POLICY THIS ANALYSED. `gpu_backend._vast_bid_price` then bid `min_bid x 1.9` — one global
multiple of the market floor, for every job, on every host. That was a reasonable heuristic and it fixed a real
churn problem (the NR-V04 covalent tail), but as a *policy* it had four defects, three of which cost money on
every launch and none of which needed new data to fix:

  1. THE ON-DEMAND CAP IS DOCUMENTED BUT NOT ENFORCED. The docstring says "never above on-demand"; the code is
     `ref * 1.9` with no cap. Where `min_bid` is a large fraction of `dph_base`, x1.9 bids ABOVE on-demand — you
     then pay more than on-demand AND remain preemptible, which is strictly dominated. (The earlier cap was
     removed because it could fall BELOW min_bid and leave the box created-but-stopped. The fix is a cap
     CLAMPED to >= min_bid, not the absence of a cap.)
  2. WE RANK BY THE WRONG QUANTITY. Offers are ranked by `min_bid`, but we pay `1.9 x min_bid` and the job takes
     `work / throughput` hours — and measured host throughput varies ~6x (19-116 ns/day on the covalent panel).
     A host 2x faster at 1.3x the floor is far cheaper per completed leg. Ranking on the floor alone cannot see
     that.
  3. A SCALE-FREE MULTIPLE MISPRICES RISK. The premium x1.9 buys scales with the floor, but the HAZARD depends on
     where the bid sits in the local offer-price distribution, which is not a function of the floor. The same
     multiple over-insures in a thin market and under-insures in a thick one.
  4. ONE CONSTANT SERVES EVERY JOB. The right margin depends on what a preemption COSTS you, which is the image
     reload plus the work lost since the last checkpoint. A leg checkpointing every 40 iterations and a 6 ns
     endpoint-MD leg writing 500 frames do not have the same optimum.

THE MODEL. Let b = bid ($/hr), m = min_bid (floor), d = on-demand ($/hr), W = GPU-hours of real work on the
chosen host, R = hours lost per preemption (image reload + expected work since the last checkpoint), and
lambda(b) = preemption hazard (per hour). Each preemption adds R to the wall clock, so

    W_wall(b) = W / (1 - lambda(b) * R)          (valid while lambda*R < 1)
    C(b)      = b * W_wall(b)                    (on Vast you PAY YOUR BID)

Minimize C(b) over m <= b, subject to W_wall(b) <= W_max, and compare the best interruptible plan against the
on-demand alternative (cost d*W, zero preemption). That last comparison is the question the fixed multiple never
asks: for a short job on an expensive floor, on-demand can simply be cheaper.

THE HAZARD. You are preempted when someone outbids you, so the hazard is proportional to the arrival rate of
higher bidders. We estimate the bid distribution EMPIRICALLY AND FOR FREE from the offer list already returned by
the same query — no new API calls, no new data:

    lambda(b) = lambda_ref * (1 - F(b)) / (1 - F(m))     with F = empirical CDF of competing offer prices

so lambda(m) = lambda_ref by construction, and the bid's protection is measured in "fraction of the market I am
now above" rather than in an arbitrary multiple.

HONESTY — WHAT IS AND IS NOT MEASURED. The SHAPE above is a model. `lambda_ref` (the floor-hugging hazard) is a
PRIOR, not a measurement: the repo has qualitative evidence (floor-hugging churned the covalent tail; x1.9 held)
but no fitted survival data, because launches have never recorded time-to-preemption. So this module ships
`fit_lambda_ref` (MLE over exponential survival, censored at completion) and `LaunchRecord` — the shape of the
data that must be logged from now on — and every output carries `lambda_ref_is_prior: True` until real records
are supplied. Defects 1-3 above are fixed WITHOUT any calibration; only the fine-tuning of the margin needs it.

No claim is made here about any scientific result, and nothing in this module launches or spends anything.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, field, asdict

HERE = os.path.dirname(os.path.abspath(__file__))

# Floor-hugging preemption hazard, per hour, for an interruptible box bid AT the market floor.
# PRIOR, NOT MEASURED. Anchored on the one qualitative observation the repo has: at ~x1.5 the NR-V04 covalent
# tail legs made zero net progress across a ~40-min cycle, i.e. they were being preempted on roughly that
# timescale near the floor -> O(1) preemption/hour at the floor. Replace via fit_lambda_ref once records exist.
DEFAULT_LAMBDA_REF = 1.0

# Measured image reload after a preemption (~6 GiB baked CUDA image), hours. pricing.md section E.
DEFAULT_IMAGE_RELOAD_H = 20.0 / 60.0


# --- drift: a price distribution is NOT stationary, and stale data is worse than none ------------------------
DEFAULT_HALF_LIFE_H = 168.0          # 7 days: a month-old price should barely influence today's threshold
DEFAULT_STALENESS_LIMIT_H = 72.0     # beyond this the series is not describing the current market


def recency_weights(ages_h, half_life_h=DEFAULT_HALF_LIFE_H):
    """Exponential decay by sample age. The empirical-quantile machinery assumed an iid stationary market;
    real GPU spot prices drift, so old observations must fade rather than vote forever."""
    return [0.5 ** (max(0.0, a) / half_life_h) for a in ages_h]


def weighted_quantile(values, weights, q):
    """Weighted empirical quantile — the recency-aware replacement for a plain order statistic."""
    pairs = sorted((v, w) for v, w in zip(values, weights) if v and v > 0 and w > 0)
    if not pairs:
        return None
    total = sum(w for _, w in pairs)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= q * total:
            return v
    return pairs[-1][0]


def effective_n(weights):
    """Kish effective sample size: sum(w)^2 / sum(w^2). Downweighted-but-numerous stale samples must NOT be
    allowed to masquerade as a large fresh sample when deciding whether to leave the cold-start phase."""
    sw = sum(weights)
    sw2 = sum(w * w for w in weights)
    return (sw * sw / sw2) if sw2 > 0 else 0.0


def staleness_h(ages_h):
    return min(ages_h) if ages_h else None


# =============================================================================================================
# hazard
# =============================================================================================================
def empirical_cdf(prices, x):
    """Fraction of `prices` at or below x. The competing-bid distribution, taken from the offer list we already
    have in hand — so this costs nothing extra to compute."""
    prices = [p for p in prices if p is not None and p > 0]
    if not prices:
        return 0.0
    return sum(1 for p in prices if p <= x) / len(prices)


def hazard(bid, floor, market_prices, lambda_ref=DEFAULT_LAMBDA_REF):
    """Preemption hazard (per hour) at `bid`, normalised so hazard(floor) == lambda_ref.

    Monotone non-increasing in `bid` by construction, and exactly 0 once the bid is above every competing
    offer — the point at which nobody in this market can outbid you."""
    if bid < floor:
        return float("inf")          # below the floor the box never starts at all; treat as unusable
    above_floor = 1.0 - empirical_cdf(market_prices, floor)
    above_bid = 1.0 - empirical_cdf(market_prices, bid)
    if above_floor <= 0:
        return 0.0
    return lambda_ref * max(0.0, above_bid) / above_floor


def restart_overhead_h(image_reload_h=DEFAULT_IMAGE_RELOAD_H, checkpoint_interval_iters=0, sec_per_iter=0.0):
    """Hours lost per preemption = image reload + EXPECTED work lost since the last checkpoint (half an
    interval, uniformly). This is the term that makes the optimal margin JOB-SPECIFIC: tighten the checkpoint
    interval and a cheaper, riskier bid becomes optimal."""
    lost = 0.5 * max(0, checkpoint_interval_iters) * max(0.0, sec_per_iter) / 3600.0
    return max(0.0, image_reload_h) + lost


# =============================================================================================================
# cost / wall clock
# =============================================================================================================
def expected_wall_h(work_gpu_h, lam, restart_h):
    """W / (1 - lambda*R). Returns inf when lambda*R >= 1 — the regime where preemptions arrive faster than the
    job can recover from them and it never finishes. A policy that lands there is not 'cheap', it is broken."""
    drag = lam * restart_h
    if drag >= 1.0:
        return float("inf")
    return work_gpu_h / (1.0 - drag)


def plan_cost(bid, floor, market_prices, work_gpu_h, restart_h, lambda_ref=DEFAULT_LAMBDA_REF):
    """Expected ($, wall-hours) for running `work_gpu_h` of work at `bid`."""
    lam = hazard(bid, floor, market_prices, lambda_ref)
    wall = expected_wall_h(work_gpu_h, lam, restart_h)
    if not math.isfinite(wall):
        return float("inf"), float("inf"), lam
    return bid * wall, wall, lam


def optimal_bid(floor, on_demand, market_prices, work_gpu_h, restart_h,
                wall_max_h=None, lambda_ref=DEFAULT_LAMBDA_REF, n_grid=400):
    """Least-expected-cost interruptible bid subject to a wall-clock cap, and the on-demand comparison.

    Search range is [floor, max(market)] — bidding above every competing offer already gives hazard 0, so
    nothing above that can help. On-demand is evaluated as a genuine alternative (cost d*W, no preemption),
    not as a cap: for a short job on an expensive floor it can simply win, and the fixed-multiple policy has
    no way to notice."""
    if floor <= 0:
        return None
    hi = max([p for p in market_prices if p] + [floor]) if market_prices else floor * 3.0
    hi = max(hi, floor * 1.05)
    best = None
    for i in range(n_grid + 1):
        b = floor + (hi - floor) * i / n_grid
        cost, wall, lam = plan_cost(b, floor, market_prices, work_gpu_h, restart_h, lambda_ref)
        if not math.isfinite(cost):
            continue
        if wall_max_h is not None and wall > wall_max_h:
            continue
        if best is None or cost < best["cost_usd"]:
            best = {"bid_usd_per_h": round(b, 4), "cost_usd": cost, "wall_h": wall,
                    "hazard_per_h": lam, "multiple_of_floor": round(b / floor, 3)}
    od = None
    if on_demand and on_demand > 0:
        od = {"bid_usd_per_h": round(float(on_demand), 4), "cost_usd": float(on_demand) * work_gpu_h,
              "wall_h": work_gpu_h, "hazard_per_h": 0.0, "on_demand": True}
    if best is None:
        return {"feasible_interruptible": False, "on_demand": od,
                "verdict": ("No interruptible bid meets the wall-clock cap — either raise the cap, tighten "
                            "checkpointing to cut the restart overhead, or take on-demand.")}
    choice = best
    if od and od["cost_usd"] < best["cost_usd"] and (wall_max_h is None or od["wall_h"] <= wall_max_h):
        choice = dict(od)
    out = {"feasible_interruptible": True, "best_interruptible": _round(best), "on_demand": _round(od),
           "recommended": _round(choice), "lambda_ref_is_prior": True}
    out["verdict"] = ("on-demand is cheaper for this job" if choice.get("on_demand")
                      else f"interruptible at {choice['multiple_of_floor']}x floor")
    return out


def _round(d):
    if not d:
        return d
    return {k: (round(v, 4) if isinstance(v, float) and math.isfinite(v) else v) for k, v in d.items()}


# =============================================================================================================
# offer ranking — the second half of the problem
# =============================================================================================================
# THROUGHPUT — delegated to `vast_cost_model`, which is the single source of truth for benched cards.
#
# What was here before: `{"rtx4090": {35_000: 1549.0, 85_000: 669.0, 444_000: 175.6}, "rtx3090": {444_000: 72.5}}`.
# Every one of those numbers came from the 2026-07-24 23:08 grid, which was WITHDRAWN the same day — each leg
# was a single 0.9-4.5 s window, and it ranked an RTX 4080 SUPER above a 4090 and a "$0.0377/hr A10" (really a
# Quadro RTX 8000) as cheapest per ns. The validated re-run (3 x ~20 s independent timed blocks per leg,
# physics-checked, CV < 1.4%, with a rejection gate) put the 4090 at 755.36 ns/day, not 669 — a 13% error that
# survived here for a day because the number lived in two places and only one was corrected.
#
# HONEST LIMIT: the validated grid measured ONE system size (84,534 particles) for three cards. The old
# multi-size table implied we could interpolate throughput across system sizes; we cannot, on validated data.
# Ranking only needs the RATIO between cards, which is far more size-stable than the absolute rate, so the
# single-size table is sound for selection and must not be used to predict an absolute ns/day at another size.
import vast_cost_model as _vcm  # noqa: E402

MEASURED_NS_PER_DAY = {c.lower(): {84_534: v} for c, v in _vcm.MEASURED_NS_PER_DAY_84K.items()}


def throughput_scale(offer, atoms, reference="rtx4090"):
    """Relative throughput of an offer's GPU vs the reference card at this system size.

    Prefers the repo's MEASURED bench where the card is known; falls back to Vast's `dlperf` ratio, which is a
    generic DL score and a WEAK proxy for MD — flagged in the output rather than silently trusted."""
    card = _vcm.card_of(offer.get("gpu_name"))
    key = card.lower() if card else None
    ref_tab = MEASURED_NS_PER_DAY.get(str(reference).lower(), {})
    ref_ns = _interp(ref_tab, atoms)
    if key and key in MEASURED_NS_PER_DAY:
        ns = _interp(MEASURED_NS_PER_DAY[key], atoms)
        if ns and ref_ns:
            return ns / ref_ns, "measured_bench"
    dl = offer.get("dlperf")
    if dl:
        try:
            return max(0.05, float(dl) / 100.0), "dlperf_proxy_WEAK"
        except (TypeError, ValueError):
            pass
    return 1.0, "assumed_equal_UNKNOWN"


def _interp(table, atoms):
    """Log-log interpolation of ns/day vs system size; clamps outside the measured range."""
    if not table:
        return None
    pts = sorted(table.items())
    if len(pts) == 1 or atoms <= pts[0][0]:
        return pts[0][1]
    if atoms >= pts[-1][0]:
        return pts[-1][1]
    for (a0, n0), (a1, n1) in zip(pts, pts[1:]):
        if a0 <= atoms <= a1:
            t = (math.log(atoms) - math.log(a0)) / (math.log(a1) - math.log(a0))
            return math.exp(math.log(n0) + t * (math.log(n1) - math.log(n0)))
    return pts[-1][1]


def rank_offers(offers, work_gpu_h_reference, atoms, restart_h, wall_max_h=None,
                lambda_ref=DEFAULT_LAMBDA_REF, reference_card="rtx4090"):
    """Rank offers by EXPECTED $ PER COMPLETED UNIT, not by the market floor.

    `work_gpu_h_reference` is the job's GPU-hours on the reference card; each offer's own work is scaled by its
    measured/proxied throughput. This is where the ~6x host-throughput spread stops being invisible."""
    market = [float(o["min_bid"]) for o in offers if o.get("min_bid")]
    ranked = []
    for o in offers:
        floor = float(o.get("min_bid") or 0) or None
        if not floor:
            continue
        scale, basis = throughput_scale(o, atoms, reference_card)
        work = work_gpu_h_reference / max(scale, 1e-6)
        plan = optimal_bid(floor, float(o.get("dph_base") or o.get("dph_total") or 0) or None,
                           market, work, restart_h, wall_max_h, lambda_ref)
        if not plan or not plan.get("recommended"):
            continue
        rec = plan["recommended"]
        ranked.append({
            "offer_id": o.get("id"), "gpu": o.get("gpu_name"), "min_bid": round(floor, 4),
            "dph_base": o.get("dph_base"), "reliability2": o.get("reliability2"),
            "throughput_scale": round(scale, 3), "throughput_basis": basis,
            "work_gpu_h_here": round(work, 2),
            "recommended_bid": rec["bid_usd_per_h"], "expected_cost_usd": rec["cost_usd"],
            "expected_wall_h": rec["wall_h"], "on_demand_wins": bool(rec.get("on_demand")),
            "vs_current_policy": _compare_to_fixed_multiple(floor, market, work, restart_h, lambda_ref, o),
        })
    ranked.sort(key=lambda r: r["expected_cost_usd"])
    return ranked


def _compare_to_fixed_multiple(floor, market, work, restart_h, lambda_ref, offer, mult=1.9):
    """What a RETIRED `min_bid x mult` policy would cost on this offer, and whether it breaches on-demand.

    Kept as a comparison baseline only. The live policy is `vast_cost_model.recommended_bid` (floor + a
    staleness tick); x1.9/x1.5/x1.25 are all history, and none of them is what the launcher bids."""
    b = floor * mult
    cost, wall, lam = plan_cost(b, floor, market, work, restart_h, lambda_ref)
    d = None
    try:
        d = float(offer.get("dph_base") or offer.get("dph_total") or 0) or None
    except (TypeError, ValueError):
        d = None
    return {"policy_bid": round(b, 4),
            "policy_cost_usd": None if not math.isfinite(cost) else round(cost, 3),
            "policy_wall_h": None if not math.isfinite(wall) else round(wall, 2),
            "exceeds_on_demand": bool(d and b > d),
            "note": ("bids ABOVE on-demand while staying preemptible — strictly dominated"
                     if (d and b > d) else "")}


# =============================================================================================================
# RESERVATION PRICE — the decision we were missing: WHEN to launch, not just what to bid now
# =============================================================================================================
# The bid optimiser above answers "given that I launch into THIS market snapshot, what should I pay?" That is the
# wrong question for work that is not deadline-bound, which is nearly all of ours (the operating regime states
# outright that this is never a race). The right object is a RESERVATION PRICE: an absolute $/hr we are willing
# to pay for a GPU-hour, held fixed while the market moves, launching only when the market comes to us.
#
# The mechanism is already there and we were not using it: ON VAST, AN INTERRUPTIBLE BID IS A LIMIT ORDER. A
# standing bid at P* acquires the machine whenever the clearing price falls to P* and is preempted when it rises
# above. With per-unit checkpointing, that is not churn to be avoided — it IS the "wait for cheap capacity"
# strategy executing itself: the job advances during cheap periods and parks during expensive ones, and the cost
# per unit of WORK is bounded by P* no matter what the market does.
#
# So a fixed multiple of a floating floor is doubly wrong: it has no stable relationship to what a GPU-hour is
# worth to us, and it re-prices upward exactly when the market is most expensive — the moment we should be
# waiting, not paying.
#
# THE ONE CONSTRAINT ON GOING LOW. Bid too far down and you acquire, spend R hours reloading, run briefly, and
# lose the box — paying for reloads instead of science. From the model above the useful fraction of paid time is
# (1 - lambda*R), so P* must satisfy lambda(P*)*R <= max_churn_fraction. That links the reservation price to the
# JOB (via R) and is the legitimate core of what the x1.9 heuristic was groping at.

DEFAULT_MAX_CHURN_FRACTION = 0.2          # >=80% of paid time must be real work, not reload


def churn_floor_price(floor, market_prices, restart_h, lambda_ref=DEFAULT_LAMBDA_REF,
                      max_churn_fraction=DEFAULT_MAX_CHURN_FRACTION, n_grid=400):
    """Lowest bid at which the job still makes net progress: the smallest b with lambda(b)*R <= max_churn.

    Below this you are buying image reloads, not compute. Returns None if no bid in range qualifies (the job's
    restart overhead is too large for this market — tighten checkpointing or take on-demand)."""
    if floor <= 0 or restart_h <= 0:
        return floor
    hi = max([p for p in market_prices if p] + [floor]) if market_prices else floor * 3.0
    hi = max(hi, floor * 1.05)
    for i in range(n_grid + 1):
        b = floor + (hi - floor) * i / n_grid
        if hazard(b, floor, market_prices, lambda_ref) * restart_h <= max_churn_fraction:
            return round(b, 4)
    return None


def reservation_price(price_history, restart_h, target_quantile=0.25, market_prices=None,
                      floor=None, lambda_ref=DEFAULT_LAMBDA_REF,
                      max_churn_fraction=DEFAULT_MAX_CHURN_FRACTION):
    """The absolute $/hr to stand a bid at.

    Two forces, and P* is the larger of them:
      * WAIT FOR CHEAP — the `target_quantile` of the OBSERVED price history. With a long horizon and no
        deadline, aim at the cheap end of the distribution rather than at today's price.
      * DON'T CHURN — `churn_floor_price`, below which preemptions eat the run.

    `price_history` is a list of observed prices over TIME (many snapshots), not the offers in one snapshot —
    that distinction is the whole point. Returns the binding reason so the number is never a bare figure."""
    hist = sorted(p for p in (price_history or []) if p and p > 0)
    if not hist:
        return {"reservation_price": None, "binding": "no price history",
                "note": ("P* cannot be set from a single market snapshot — it needs the price distribution over "
                         "TIME. Start the sampler; until then there is no defensible target price.")}
    idx = min(len(hist) - 1, max(0, int(round(target_quantile * (len(hist) - 1)))))
    quantile_price = hist[idx]
    churn = None
    if market_prices and floor:
        churn = churn_floor_price(floor, market_prices, restart_h, lambda_ref, max_churn_fraction)
    if churn is None:
        return {"reservation_price": round(quantile_price, 4), "binding": "price_quantile",
                "quantile_price": round(quantile_price, 4), "churn_floor": None,
                "n_history": len(hist),
                "note": "No churn floor computed (no live snapshot supplied); quantile target only."}
    P = max(quantile_price, churn)
    return {"reservation_price": round(P, 4),
            "binding": "churn_floor" if churn > quantile_price else "price_quantile",
            "quantile_price": round(quantile_price, 4), "churn_floor": round(churn, 4),
            "n_history": len(hist),
            "note": ("P* is the larger of the cheap-end target and the no-churn floor. If the churn floor binds, "
                     "the job's restart overhead — not the market — is what is costing you; tighten "
                     "checkpointing before paying more.")}


def waiting_value(price_history, current_price, target_quantile=0.25):
    """What waiting is worth: the gap between today's price and the cheap end of the observed distribution,
    plus how often the market has actually been at or below that target.

    If `frac_at_or_below` is tiny, waiting is a long shot and the saving is not bankable; if it is a healthy
    fraction of samples, waiting is close to free money for work with no deadline."""
    hist = sorted(p for p in (price_history or []) if p and p > 0)
    if not hist or not current_price:
        return None
    idx = min(len(hist) - 1, max(0, int(round(target_quantile * (len(hist) - 1)))))
    target = hist[idx]
    frac = sum(1 for p in hist if p <= target) / len(hist)
    return {"current_price": round(current_price, 4), "target_price": round(target, 4),
            "saving_per_gpu_h": round(current_price - target, 4),
            "saving_pct": round(100.0 * (current_price - target) / current_price, 1) if current_price else None,
            "frac_of_samples_at_or_below_target": round(frac, 3),
            "n_history": len(hist),
            "note": ("A standing bid at the target IS the waiting mechanism — on Vast an interruptible bid is a "
                     "limit order. Waiting costs wall-clock, which for non-deadline work is close to free.")}


# =============================================================================================================
# ADAPTIVE RESERVATION PRICE — cold-start with zero knowledge, converging as the market is observed
# =============================================================================================================
# The static reservation price above needs a price history before it will answer. That is a real limitation, and
# the literature solves it. Three structural facts about OUR problem make the solution clean:
#
#   (i)  OBSERVING PRICES IS FREE AND NON-COMMITTAL. An offer query costs nothing and does not bind us. So there
#        is NO explore/exploit tradeoff on observation — the usual bandit difficulty is absent. We only need to
#        learn the price distribution F, and we can watch it as much as we like. (The one thing that DOES cost
#        real experimentation is the preemption hazard lambda, which you only learn by running; that is handled
#        separately, as a by-product of jobs we would run anyway — see fit_lambda_ref.)
#   (ii) THE WORK IS DIVISIBLE AND CHECKPOINTED. We are not choosing one launch instant; we are procuring
#        W GPU-hours over a horizon, buying whenever the price is acceptable. That makes this DIVISIBLE
#        PROCUREMENT UNDER A DEADLINE, not a one-shot stopping problem.
#   (iii) ON-DEMAND IS A HARD, KNOWN CEILING. We can always buy at `d`, so no price above `d` is ever accepted
#        and our downside is bounded. A *bounded* online search is exactly the setting with a clean
#        distribution-free answer.
#
# THE ACCEPTANCE QUANTILE IS THE DUTY CYCLE (the key derivation, and it is not a tuned parameter).
# To finish W GPU-hours in T remaining hours on `capacity` concurrent machines we must be running a fraction
#     rho = W / (T * capacity)
# of the time. With iid prices, accepting the cheapest rho-fraction of the distribution is exactly enough to
# meet the deadline and is the cheapest way to do it. So the target quantile IS the required duty cycle:
#     q_t = clamp(rho, 0, 1)
# Slack (small rho) => be picky. Behind schedule (rho -> 1) => accept anything up to on-demand. It falls out of
# the deadline, rather than being chosen.
#
# COLD START (zero observations). With no history but a known ceiling `d` and a lower bound `m`, the classic
# distribution-free reservation price for bounded online search (El-Yaniv, Fiat, Karp & Turpin) is the GEOMETRIC
# MEAN, P* = sqrt(m*d), which is worst-case optimal with competitive ratio sqrt(d/m). It needs no distribution at
# all — exactly the "start knowing nothing" regime.
#
# CONVERGENCE. Once observations accumulate we switch to the empirical quantile, but with a FINITE-SAMPLE
# PENALTY: a thin sample that happened to catch cheap prices would otherwise make us hold out for a price that
# does not exist. We therefore use an UPPER confidence bound on the q-quantile (normal approximation to the
# binomial order statistic), which starts conservative and tightens as n grows — so the hand-off from the
# distribution-free rule is smooth and never jumps the threshold upward.
#
# The final price is then clamped by the two hard constraints already established: never below the no-churn floor
# (job physics), never above on-demand (free ceiling).

MIN_OBS_FOR_EMPIRICAL = 12          # below this the empirical quantile is not trustworthy; use the cold-start rule
DEFAULT_QUANTILE_CONF_Z = 1.28      # ~90% one-sided UCB on the quantile rank


def duty_cycle(work_remaining_gpu_h, time_remaining_h, capacity=1):
    """rho = fraction of remaining wall-clock we must be RUNNING to finish on time. This is the acceptance
    quantile; see the derivation above. >=1 means the deadline can no longer be met by waiting at all."""
    if time_remaining_h is None or time_remaining_h <= 0 or capacity <= 0:
        return 1.0
    return max(0.0, work_remaining_gpu_h / (time_remaining_h * capacity))


def cold_start_price(lower_bound, on_demand):
    """Distribution-free reservation price for bounded online search: the geometric mean sqrt(m*d).
    Worst-case optimal (competitive ratio sqrt(d/m)) with NO knowledge of the price distribution."""
    if not on_demand or on_demand <= 0:
        return None
    m = max(1e-6, float(lower_bound or 0.0) or on_demand * 0.05)
    return round(math.sqrt(m * float(on_demand)), 4)


def ucb_quantile(observations, q, z=DEFAULT_QUANTILE_CONF_Z):
    """UPPER confidence bound on the q-quantile of the observed prices.

    Conservative direction on purpose: with few samples the point estimate can be biased low (we happened to
    watch during a cheap spell), and a too-low threshold means never buying. The UCB rank shrinks toward the
    plain empirical quantile as n grows."""
    xs = sorted(p for p in (observations or []) if p and p > 0)
    n = len(xs)
    if n == 0:
        return None
    q = min(1.0, max(0.0, q))
    pad = z * math.sqrt(max(q * (1.0 - q), 1e-9) / n)
    idx = int(math.ceil(min(1.0, q + pad) * n)) - 1
    return xs[max(0, min(n - 1, idx))]


def adaptive_reservation_price(observations, on_demand, work_remaining_gpu_h, time_remaining_h,
                               restart_h=0.0, market_prices=None, floor=None, capacity=1,
                               lambda_ref=DEFAULT_LAMBDA_REF,
                               max_churn_fraction=DEFAULT_MAX_CHURN_FRACTION,
                               min_obs=MIN_OBS_FOR_EMPIRICAL,
                               ages_h=None, half_life_h=DEFAULT_HALF_LIFE_H,
                               staleness_limit_h=DEFAULT_STALENESS_LIMIT_H):
    """The full policy: a standing limit price that works from zero knowledge and adapts as the market is seen.

    `ages_h` (hours since each observation) enables DRIFT HANDLING: observations decay with `half_life_h`, the
    empirical phase engages on the EFFECTIVE sample size rather than the raw count, and a series whose freshest
    point is older than `staleness_limit_h` is refused outright — falling back to the cold start rather than
    setting today's threshold from a market that no longer exists. Without `ages_h` the behaviour is unchanged,
    so existing callers keep working.

    Returns the price plus every intermediate quantity, because a bare number here is unauditable."""
    rho = duty_cycle(work_remaining_gpu_h, time_remaining_h, capacity)
    obs = [p for p in (observations or []) if p and p > 0]
    n = len(obs)
    m_hat = min(obs, default=None)

    weights, n_eff, stale, stale_h = None, float(n), False, None
    if ages_h is not None and len(ages_h) != len(observations or []):
        # Silently ignoring a mismatch would disable drift handling without a word — a safety feature that
        # vanishes quietly is worse than no safety feature. Caught by a unit test that passed mismatched lengths.
        raise ValueError(
            "ages_h has %d entries but observations has %d — refusing to silently drop drift handling"
            % (len(ages_h), len(observations or [])))
    if ages_h:
        pairs = [(p, a) for p, a in zip(observations, ages_h) if p and p > 0]
        if pairs:
            weights = recency_weights([a for _, a in pairs], half_life_h)
            n_eff = effective_n(weights)
            stale_h = staleness_h([a for _, a in pairs])
            stale = stale_h is not None and stale_h > staleness_limit_h

    if rho >= 1.0:
        econ, phase = (float(on_demand) if on_demand else None), "deadline_binding"
    elif stale:
        econ, phase = cold_start_price(m_hat, on_demand), "cold_start_STALE_HISTORY"
    elif n_eff < min_obs:
        econ, phase = cold_start_price(m_hat, on_demand), "cold_start_geometric_mean"
    elif weights:
        pairs = [(p, w) for p, w in zip(obs, weights)]
        pad = DEFAULT_QUANTILE_CONF_Z * math.sqrt(max(rho * (1.0 - rho), 1e-9) / max(n_eff, 1.0))
        econ = weighted_quantile([v for v, _ in pairs], [w for _, w in pairs], min(1.0, rho + pad))
        phase = "empirical_ucb_quantile_recency_weighted"
    else:
        econ, phase = ucb_quantile(observations, rho), "empirical_ucb_quantile"

    churn = None
    if market_prices and floor and restart_h:
        churn = churn_floor_price(floor, market_prices, restart_h, lambda_ref, max_churn_fraction)

    candidates = [c for c in (econ, churn) if c]
    price = max(candidates) if candidates else None
    capped = False
    if price and on_demand and price > float(on_demand):
        price, capped = float(on_demand), True

    return {
        "reservation_price": None if price is None else round(price, 4),
        "phase": phase,
        "duty_cycle_rho": round(rho, 4),
        "n_observations": n,
        "n_effective": round(n_eff, 2),
        "freshest_sample_age_h": (None if stale_h is None else round(stale_h, 2)),
        "history_stale": stale,
        "economic_price": econ,
        "churn_floor": churn,
        "binding": ("on_demand_cap" if capped else
                    ("churn_floor" if (churn and econ and churn > econ) else phase)),
        "lambda_ref_is_prior": lambda_ref == DEFAULT_LAMBDA_REF,
        "note": ("q = the DUTY CYCLE we must sustain to hit the deadline, so the threshold tightens with slack "
                 "and relaxes as the deadline nears. With <%d observations the cold-start rule sqrt(m*d) is "
                 "used — worst-case optimal with no distribution knowledge; past that, an upper-confidence "
                 "quantile that converges to the empirical one. Never below the no-churn floor, never above "
                 "on-demand." % min_obs),
    }


# =============================================================================================================
# calibration — the data we must start logging
# =============================================================================================================
@dataclass
class LaunchRecord:
    """One interruptible launch, as it must be logged from now on for lambda_ref to become a measurement.

    `hours_observed` is time from start to preemption (censored=False) or to completion/teardown by us
    (censored=True). Censored records still carry information and must not be discarded."""
    bid_usd_per_h: float
    min_bid_usd_per_h: float
    market_prices: list = field(default_factory=list)
    hours_observed: float = 0.0
    censored: bool = True
    gpu_name: str = ""
    tag: str = ""


def fit_lambda_ref(records, lo=1e-3, hi=50.0, iters=200):
    """MLE for `lambda_ref` under exponential survival with the hazard model above, honouring censoring.

    log L = sum_uncensored [ log lambda_i ] - sum_all [ lambda_i * t_i ],  lambda_i = lambda_ref * s_i
    with s_i the bid's market-position factor. Closed form: lambda_ref = n_events / sum(s_i * t_i).
    Returns None when there are no events — with zero observed preemptions the rate is unidentified from
    above, and saying so is more useful than returning a fabricated number."""
    events, denom = 0, 0.0
    for r in records:
        s_num = 1.0 - empirical_cdf(r.market_prices, r.bid_usd_per_h)
        s_den = 1.0 - empirical_cdf(r.market_prices, r.min_bid_usd_per_h)
        s = (s_num / s_den) if s_den > 0 else 0.0
        denom += s * max(0.0, r.hours_observed)
        if not r.censored:
            events += 1
    if events == 0 or denom <= 0:
        return {"lambda_ref": None, "n_events": events, "n_records": len(records),
                "note": ("No preemption events (or zero exposure) — lambda_ref is not identified from these "
                         "records. Keep the prior and keep logging; a run of censored records only puts an "
                         "UPPER bound on the hazard.")}
    lam = events / denom
    return {"lambda_ref": lam, "n_events": events, "n_records": len(records),
            "note": "MLE under exponential survival with censoring; replaces the prior."}


# =============================================================================================================
def _cli(argv=None):
    ap = argparse.ArgumentParser(description="Optimal Vast interruptible bid: least $/completed unit.")
    ap.add_argument("--offers-json", help="probe_offers dump (list of Vast offer dicts)")
    ap.add_argument("--work-gpu-h", type=float, required=True, help="GPU-hours of real work on the reference card")
    ap.add_argument("--atoms", type=int, default=146000, help="system size (particles) for the throughput prior")
    ap.add_argument("--ckpt-iters", type=int, default=40, help="checkpoint interval (iterations)")
    ap.add_argument("--sec-per-iter", type=float, default=16.0)
    ap.add_argument("--wall-max-h", type=float, default=None)
    ap.add_argument("--lambda-ref", type=float, default=DEFAULT_LAMBDA_REF)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--live", action="store_true",
                    help="pull LIVE offers via gpu_backend's existing read-only query (needs VAST_API_KEY; "
                         "no rent, no spend) instead of --offers-json")
    ap.add_argument("--gpu", default="rtx4090", help="--live: gpu_name substring filter")
    ap.add_argument("--gpu-sweep", default=None,
                    help="comma-separated gpu_name substrings to compare on $/ns (e.g. "
                         "'rtx4090,rtx3090,l4,a10,rtx4080,rtx3080,a4000'). Answers 'which card class should we "
                         "even be renting?', which a single --gpu query cannot.")
    ap.add_argument("--out", default=None, help="also write the full result JSON here")
    ap.add_argument("--sample-out", default=None,
                    help="append a market SNAPSHOT (one line of JSON) to this JSONL — the price time series "
                         "that a reservation price needs and that we have never collected")
    ap.add_argument("--history", default=None,
                    help="price-history JSONL from --sample-out; enables the reservation-price / waiting-value "
                         "read-out")
    ap.add_argument("--target-quantile", type=float, default=0.25)
    ap.add_argument("--crosscheck-ondemand", action="store_true",
                    help="run the same query as on-demand and compare per machine (read-only)")
    ap.add_argument("--crosscheck-limit", type=int, default=512,
                    help="offers to request per query type in --crosscheck-ondemand. The two types return "
                         "different pages, so the API default matched only ONE machine — far too thin to price "
                         "the interruptible discount off.")
    args = ap.parse_args(argv)

    R = restart_overhead_h(checkpoint_interval_iters=args.ckpt_iters, sec_per_iter=args.sec_per_iter)
    if args.gpu_sweep:
        print(json.dumps(gpu_class_sweep([g.strip() for g in args.gpu_sweep.split(",") if g.strip()],
                                         args.atoms, R), indent=1))
        return 0
    if args.crosscheck_ondemand:
        print(json.dumps(ondemand_crosscheck(args.gpu, limit=args.crosscheck_limit), indent=1))
        return 0
    if args.live:
        offers = _live_offers(args.gpu)
    elif args.offers_json:
        with open(args.offers_json) as f:
            offers = json.load(f)
        offers = offers.get("offers", offers) if isinstance(offers, dict) else offers
    else:
        print(json.dumps({"restart_overhead_h": round(R, 3),
                          "note": "pass --offers-json (a probe dump) or --live to rank real offers"}, indent=1))
        return 0
    floors = sorted(float(o["min_bid"]) for o in offers if o.get("min_bid"))
    if args.sample_out:
        _append_sample(args.sample_out, offers)
    ranked = rank_offers(offers, args.work_gpu_h, args.atoms, R, args.wall_max_h, args.lambda_ref)
    result = {"restart_overhead_h": round(R, 3), "n_offers": len(offers),
              "work_gpu_h_reference": args.work_gpu_h, "atoms": args.atoms,
              "lambda_ref": args.lambda_ref,
              "lambda_ref_is_prior": args.lambda_ref == DEFAULT_LAMBDA_REF,
              "ranked": ranked[:args.top], "saving_vs_current_policy": _saving_summary(ranked)}
    hist = _load_history(args.history) if args.history else []
    result["reservation_price"] = reservation_price(
        hist, R, target_quantile=args.target_quantile, market_prices=floors,
        floor=(floors[0] if floors else None), lambda_ref=args.lambda_ref)
    result["waiting_value"] = waiting_value(hist, floors[0] if floors else None, args.target_quantile)
    print(json.dumps(result, indent=1))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=1)
    return 0


def _append_sample(path, offers):
    """One line of JSON per market observation. Deliberately append-only and schema-light: the thing we need is
    a LONG series of cheapest-floor observations over time, and anything that makes sampling fragile defeats it."""
    floors = sorted(float(o["min_bid"]) for o in offers if o.get("min_bid"))
    rec = {"ts": _now_iso(), "source": os.environ.get("VBO_SAMPLE_SOURCE", "systematic"),
           "n_offers": len(offers), "min_floor": (floors[0] if floors else None),
           "median_floor": (floors[len(floors) // 2] if floors else None),
           "floors": floors[:20]}
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")


def _now_iso():
    """UTC timestamp. Wall-clock is read at SAMPLE time only, never inside a decision function, so every
    threshold computation stays deterministic and unit-testable."""
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _load_history(path, with_meta=False):
    """Cheapest floor from each past snapshot — the distribution a reservation price is set against."""
    out = []
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("min_floor"):
                out.append((float(r["min_floor"]), r.get("ts"), r.get("source", "unknown"))
                           if with_meta else float(r["min_floor"]))
    return out



def _live_offers(gpu_substr="rtx4090"):
    """Read-only live offer pull, reusing gpu_backend's EXISTING query (no rent, no spend, no new API surface)."""
    from gpu_backend import ResourceSpec, _vast_offer_query, _vast_request
    key = os.environ.get("VAST_API_KEY", "")
    if not key:
        raise SystemExit("VAST_API_KEY not set — --live needs it (read-only offer search, no spend).")
    res = ResourceSpec()
    q = _vast_offer_query(res)
    # EXACTLY the call nrv04_vast_launch.probe_offers makes (GET /search/asks/ with the query as a param).
    # An earlier version guessed `PUT /bundles/` and 4xx'd in CI — copy the known-working call, do not invent one.
    data = _vast_request("GET", "/search/asks/", key, params={"q": json.dumps(q)}) or {}
    offers = data.get("offers", data if isinstance(data, list) else [])
    if gpu_substr:
        g = gpu_substr.lower().replace(" ", "")
        offers = [o for o in offers if g in str(o.get("gpu_name", "")).lower().replace(" ", "")]
    return offers


def ondemand_crosscheck(gpu_substr="rtx4090", limit=512):
    """DECISIVE CHECK on the premise behind 'x1.9 bids above on-demand'.

    In a bid-type search Vast returned `min_bid == dph_base` on every offer, which would mean the interruptible
    floor equals the on-demand price and the incumbent x1.9 is paying ~1.9x on-demand for a preemptible box.
    That is a big claim resting on `dph_base` being a genuine on-demand price rather than the API echoing the
    bid floor back for this query type. So: run the SAME query as ON-DEMAND, match by machine_id, and compare.
    If on-demand prices come back materially higher, the premise is FALSE and the claim must be withdrawn.

    IT WAS FALSE (measured 2026-07-24). `min_bid == dph_base` is a TAUTOLOGY OF THE QUERY TYPE, not a market
    fact: in a `type: "bid"` search Vast reports `dph_base` as your rate AT the minimum bid. Machine 26385
    priced on-demand compute at $0.4533/h against a $0.3733/h floor — an 18% interruptible discount — with an
    identical $0.003/h surcharge on both sides. The seven-card "no discount anywhere" table this function was
    written to test was seven restatements of the same identity; exact equality to six decimals across seven
    independently-owned hosts was the giveaway, since markets do not produce that and definitions do. Anything
    quoting `dph_base` from a bid-type query as an on-demand price is reporting the artifact.

    `gpu_substr` may be a comma-separated list; `limit` is raised well above the API default because the two
    query types return different offer pages, and the first run of the fixed comparison matched only ONE
    machine — too thin to price off.

    APPLES-TO-APPLES (fixed 2026-07-24). The first version of this check divided the on-demand `dph_total` by the
    interruptible `min_bid`, which mixes two different quantities: `dph_total` = `dph_base` + storage + estimated
    bandwidth, while `min_bid` is compute only. Its 1.14-2.17x spread was therefore mostly SURCHARGE, not an
    on-demand premium, and it cannot answer the question that actually decides the policy:

        is there a real spot DISCOUNT on the compute rate, or does interruptible buy the same rate as on-demand?

    So compare the two like-for-like terms separately per machine:
      * compute:   `on_demand.dph_base`  vs  `bid.min_bid`      -> `od_base_over_floor`  (the DISCOUNT, if any)
      * surcharge: `dph_total - dph_base` on each side          -> is it rental-type dependent?
    A surcharge that matches on both sides is charged whether you bid or buy, so it cancels out of the decision
    and the compute ratio alone settles it."""
    from gpu_backend import ResourceSpec, _vast_offer_query, _vast_request
    key = os.environ.get("VAST_API_KEY", "")
    if not key:
        raise SystemExit("VAST_API_KEY not set")
    wanted = [s.strip().lower().replace(" ", "") for s in (gpu_substr or "").split(",") if s.strip()]
    out = {}
    for label, interruptible in (("bid", True), ("on_demand", False)):
        spec = ResourceSpec(interruptible=interruptible)
        q = _vast_offer_query(spec)
        q["limit"] = int(limit)
        data = _vast_request("GET", "/search/asks/", key, params={"q": json.dumps(q)}) or {}
        offers = data.get("offers", [])
        if wanted:
            offers = [o for o in offers
                      if any(w in str(o.get("gpu_name", "")).lower().replace(" ", "") for w in wanted)]
        out[label] = {str(o.get("machine_id")): {
            "offer_id": o.get("id"), "min_bid": o.get("min_bid"), "dph_base": o.get("dph_base"),
            "dph_total": o.get("dph_total"), "gpu": o.get("gpu_name"),
            "storage_cost": o.get("storage_cost"), "inet_up_cost": o.get("inet_up_cost"),
            "inet_down_cost": o.get("inet_down_cost")} for o in offers}
    res = _crosscheck_compare(out["bid"], out["on_demand"])
    res.update({"n_bid_offers": len(out["bid"]), "n_ondemand_offers": len(out["on_demand"]),
                "limit": int(limit), "gpu_filter": wanted or None})
    return res


def _crosscheck_compare(bid_map, od_map):
    """Pure comparison half of `ondemand_crosscheck`, split out so the verdict logic is unit-testable without a
    live API key. Both args map machine_id -> offer dict."""
    common = sorted(set(bid_map) & set(od_map))
    rows = []
    for mid in common:
        b, d = bid_map[mid], od_map[mid]
        floor, od_base = _num(b.get("min_bid")), _num(d.get("dph_base"))
        sur_b = (_num(b.get("dph_total")) or 0) - (_num(b.get("dph_base")) or 0)
        sur_d = (_num(d.get("dph_total")) or 0) - (_num(d.get("dph_base")) or 0)
        rows.append({
            "machine_id": mid, "gpu": b["gpu"],
            "bid_min_bid": floor, "bid_dph_base": _num(b.get("dph_base")),
            "ondemand_dph_base": od_base, "ondemand_dph_total": _num(d.get("dph_total")),
            # THE decision ratio: compute rate you'd pay on-demand / lowest compute rate a bid can win.
            "od_base_over_floor": (round(od_base / floor, 3) if (floor and od_base) else None),
            "surcharge_bid_usd_h": round(sur_b, 4), "surcharge_ondemand_usd_h": round(sur_d, 4),
            "surcharge_matches": abs(sur_b - sur_d) < 1e-6,
        })
    ratios = [r["od_base_over_floor"] for r in rows if r["od_base_over_floor"]]
    med = sorted(ratios)[len(ratios) // 2] if ratios else None
    sur_same = bool(rows) and all(r["surcharge_matches"] for r in rows)
    # The bid policy needs the DISTRIBUTION, not a point estimate: a median 1.2x built from hosts spanning
    # 1.0x-1.6x means the discount is a property of WHICH HOST you land on, and selection matters more than the
    # bid does. Broken out per card class for the same reason.
    per_gpu = {}
    for r in rows:
        if r["od_base_over_floor"]:
            per_gpu.setdefault(str(r["gpu"]), []).append(r["od_base_over_floor"])
    spread = {
        "n": len(ratios),
        "min": min(ratios) if ratios else None, "max": max(ratios) if ratios else None,
        "p25": _quantile(ratios, 0.25), "p75": _quantile(ratios, 0.75),
        "frac_hosts_with_no_discount": (round(sum(1 for x in ratios if x <= 1.02) / len(ratios), 3)
                                        if ratios else None),
        "per_gpu_median": {g: sorted(v)[len(v) // 2] for g, v in sorted(per_gpu.items())},
        "per_gpu_n": {g: len(v) for g, v in sorted(per_gpu.items())},
    }
    if not ratios:
        verdict = "no machines common to both queries — inconclusive, re-run"
    elif med <= 1.02:
        verdict = ("NO SPOT DISCOUNT: on-demand compute rate is %.3fx the interruptible floor, i.e. the same "
                   "number. Bidding cannot beat buying on price, so interruption risk is pure downside and "
                   "on-demand at the floor is the policy. Surcharge (storage+bandwidth) is %s across rental "
                   "types, so it cancels." % (med, "IDENTICAL" if sur_same else "DIFFERENT — inspect rows"))
    else:
        verdict = ("REAL SPOT DISCOUNT of %.0f%%: on-demand compute is %.2fx the interruptible floor, so bidding "
                   "CAN be cheaper and the interruption-cost trade-off must be re-solved (the on-demand-always "
                   "conclusion is withdrawn)." % (100.0 * (1 - 1 / med), med))
    return {"n_common_machines": len(common), "rows": rows,
            "median_od_base_over_floor": med, "discount_spread": spread,
            "surcharge_identical_across_rental_types": sur_same, "verdict": verdict}


def _quantile(vals, q):
    """Plain nearest-rank quantile on an unweighted sample. (`weighted_quantile` is the recency-weighted one used
    for price history; this is for describing a spread where every observation counts the same.)"""
    s = sorted(v for v in vals if v is not None)
    if not s:
        return None
    return s[min(len(s) - 1, max(0, int(round(q * (len(s) - 1)))))]


def _num(v):
    """Tolerant float. Defined here because `gpu_class_sweep` used it before it existed in this module — a
    NameError that only surfaced in CI, which is exactly why the sweep now has an offline test."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def gpu_class_sweep(gpu_substrings, atoms, restart_h):
    """Rank CARD CLASSES by $/ns — the question a single-card query cannot ask.

    The repo's card decision ("the 4090 wins $/ns at every size") rests on a bench that compared exactly TWO
    cards, 4090 vs 3090. L4 — which is what every completed science run has actually used — was never in the
    grid, and neither was anything else on the market. So the decision is under-determined, and a price analysis
    scoped to one card inherits that.

    Throughput is MEASURED where the bench covers the card and a clearly-labelled proxy otherwise, so the output
    is a list of candidates worth benching, NOT a verdict. Benching a new class costs cents via `bench_grid`."""
    out = []
    for g in gpu_substrings:
        try:
            offers = _live_offers(g)
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001
            out.append({"gpu": g, "error": str(e)[:200]})
            continue
        floors = sorted(float(o["min_bid"]) for o in offers if o.get("min_bid"))
        if not offers or not floors:
            out.append({"gpu": g, "n_offers": len(offers), "note": "no rentable offers matched"})
            continue
        rep = min(offers, key=lambda o: float(o.get("min_bid") or 1e9))
        scale, basis = throughput_scale(rep, atoms)
        ref_ns = _interp(MEASURED_NS_PER_DAY["rtx4090"], atoms)
        ns_day = (ref_ns or 0) * scale
        cheapest = floors[0]
        out.append({
            "gpu": g, "n_offers": len(offers),
            "cheapest_floor_usd_h": round(cheapest, 4),
            "median_floor_usd_h": round(floors[len(floors) // 2], 4),
            # NOT an on-demand price. `_live_offers` runs a `type: "bid"` query, in which Vast reports dph_base
            # as your rate AT the floor — so it equals min_bid by definition. Reporting it as "on_demand_usd_h"
            # is what produced the retracted "no spot discount on any card" claim. Only `ondemand_crosscheck`,
            # which actually issues an on-demand query, can price that; the real gap is ~1.2x (18% off) on the
            # one machine measured so far. Kept under an honest key so the artifact is visible, not silent.
            "bid_query_dph_base_usd_h_ARTIFACT_equals_floor": _num(rep.get("dph_base")),
            "throughput_scale_vs_4090": round(scale, 3), "throughput_basis": basis,
            "est_ns_per_day": round(ns_day, 1) if ns_day else None,
            "usd_per_ns": (round(cheapest / (ns_day / 24.0), 5) if ns_day else None),
        })
    ok = [r for r in out if r.get("usd_per_ns")]
    ok.sort(key=lambda r: r["usd_per_ns"])
    return {"atoms": atoms, "restart_overhead_h": round(restart_h, 3),
            "ranked_by_usd_per_ns": ok,
            "unusable": [r for r in out if not r.get("usd_per_ns")],
            "caveat": ("$/ns is the objective; $/hr is not. Throughput for any card marked "
                       "dlperf_proxy_WEAK or assumed_equal_UNKNOWN is NOT measured — treat those rows as "
                       "candidates to BENCH (cents via bench_grid), never as a decision."),
            "measured_cards": sorted(MEASURED_NS_PER_DAY)}


def _saving_summary(ranked):
    """Head-to-head against the incumbent min_bid x1.9 policy: what the best offer costs under each rule."""
    if not ranked:
        return None
    best = ranked[0]
    pol = best.get("vs_current_policy") or {}
    pc = pol.get("policy_cost_usd")
    ec = best.get("expected_cost_usd")
    # the incumbent also SELECTS differently: it ranks by min_bid, so it would take the cheapest-floor offer
    incumbent_pick = min(ranked, key=lambda r: r["min_bid"])
    ipc = (incumbent_pick.get("vs_current_policy") or {}).get("policy_cost_usd")
    out = {"optimizer_pick": {"offer_id": best.get("offer_id"), "gpu": best.get("gpu"),
                              "bid": best.get("recommended_bid"), "expected_cost_usd": ec},
           "incumbent_pick_min_bid_x1.9": {"offer_id": incumbent_pick.get("offer_id"),
                                           "gpu": incumbent_pick.get("gpu"),
                                           "bid": (incumbent_pick.get("vs_current_policy") or {}).get("policy_bid"),
                                           "expected_cost_usd": ipc},
           "same_offer_bid_only_saving_usd": (round(pc - ec, 3) if (pc is not None and ec is not None) else None),
           "end_to_end_saving_usd": (round(ipc - ec, 3) if (ipc is not None and ec is not None) else None)}
    if out["end_to_end_saving_usd"] is not None and ipc:
        out["end_to_end_saving_pct"] = round(100.0 * out["end_to_end_saving_usd"] / ipc, 1)
    out["n_offers_where_policy_exceeds_on_demand"] = sum(
        1 for r in ranked if (r.get("vs_current_policy") or {}).get("exceeds_on_demand"))
    return out


if __name__ == "__main__":
    sys.exit(_cli())
