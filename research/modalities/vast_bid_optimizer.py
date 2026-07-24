#!/usr/bin/env python3
"""
Vast interruptible bidding as an OPTIMIZATION problem: least $ per COMPLETED unit, subject to a wall-clock cap.

THE PROBLEM WITH THE CURRENT POLICY. `gpu_backend._vast_bid_price` bids `min_bid x 1.9` — one global multiple of
the market floor, for every job, on every host. That is a reasonable heuristic and it fixed a real churn problem
(the NR-V04 covalent tail), but as a *policy* it has four defects, three of which cost money on every launch and
none of which need new data to fix:

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
# Measured ns/day per card at three system sizes (gpu_md_bench, controlled single-host-per-point; pricing.md B).
# Used as a THROUGHPUT prior so ranking is by expected $/completed-unit rather than by the market floor.
MEASURED_NS_PER_DAY = {
    "rtx4090": {35_000: 1549.0, 85_000: 669.0, 444_000: 175.6},
    "rtx3090": {444_000: 72.5},
}


def throughput_scale(offer, atoms, reference="rtx4090"):
    """Relative throughput of an offer's GPU vs the reference card at this system size.

    Prefers the repo's MEASURED bench where the card is known; falls back to Vast's `dlperf` ratio, which is a
    generic DL score and a WEAK proxy for MD — flagged in the output rather than silently trusted."""
    name = str(offer.get("gpu_name", "")).lower().replace(" ", "").replace("_", "")
    key = "rtx4090" if "4090" in name else ("rtx3090" if "3090" in name else None)
    ref_tab = MEASURED_NS_PER_DAY.get(reference, {})
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
    """What the incumbent `min_bid x mult` policy would cost on this offer, and whether it breaches on-demand."""
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
    ap.add_argument("--out", default=None, help="also write the full result JSON here")
    args = ap.parse_args(argv)

    R = restart_overhead_h(checkpoint_interval_iters=args.ckpt_iters, sec_per_iter=args.sec_per_iter)
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
    ranked = rank_offers(offers, args.work_gpu_h, args.atoms, R, args.wall_max_h, args.lambda_ref)
    result = {"restart_overhead_h": round(R, 3), "n_offers": len(offers),
              "work_gpu_h_reference": args.work_gpu_h, "atoms": args.atoms,
              "lambda_ref": args.lambda_ref,
              "lambda_ref_is_prior": args.lambda_ref == DEFAULT_LAMBDA_REF,
              "ranked": ranked[:args.top], "saving_vs_current_policy": _saving_summary(ranked)}
    print(json.dumps(result, indent=1))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=1)
    return 0


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
