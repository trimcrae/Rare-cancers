#!/usr/bin/env python3
"""WHY 79 % OF A QUALIFYING VAST BOARD CANNOT BE PRICED — the census, and the break-even that decides the fix.

★ THE OBSERVATION THIS EXISTS FOR (2026-07-27 8:00 AM ET, `step1-fanout-market-hold.json`):

      offers_returned: 48 · qualifying: 48 · **priceable: 10** · needed: 19

Every one of those 48 offers passed the launcher's hard filters — VRAM, CUDA, RAM, cores, disk, reliability.
They were dropped at the very last step, in `rank_offers_by_usd_per_ns`, because `$/ns` needs a **benched**
`ns/h` and `vast_cost_model.MEASURED_NS_PER_DAY_84K` holds three entries (RTX 4090 / RTX 4080 / RTX 3090,
matching four marketed names once `RTX 4080S` and `RTX 3090 Ti` fold in). Everything else is UNKNOWN and is
correctly excluded rather than guessed at — the 2026-07-24 `dlperf`-proxy ranking was RETRACTED for exactly
that (`vast-gpu-class-sweep.json`, `throughput_basis: dlperf_proxy_WEAK`).

So the thinness is largely **self-imposed**: the fleet needs 19 units, can grade 10, and pays a mean dragged
by whatever tail the 10 contain. This module answers the only question that decides whether to do anything
about it — **what would widening the table actually buy?** — WITHOUT inventing a single throughput number.

===============================================================================================================
THE ONE IDEA: BREAK-EVEN ns/day
===============================================================================================================
We cannot say what an unbenched card's `$/ns` IS. We can say exactly what its throughput would have to be for
its cheapest offer to beat a number we already have:

    usd_per_ns(bid, storage, theta) <= target      <=>      theta >= theta_breakeven

Inverting `vast_cost_model.usd_per_ns` for `theta` (all other terms held at the same job profile the launcher
uses) gives a **falsifiable screening statistic**: an RTX PRO 4000 at a $0.053/hr floor needs only ~66 ns/day
to beat the board's best gradeable offer, and no 24 GB Blackwell card is that slow — so it is worth the few
cents of a bench. A card that would need 3,000 ns/day is not, and the census says so instead of hand-waving.

This is a **screen, not a value**. It never enters a ranking, never becomes a throughput, and nothing
downstream may read it as one; the only action it licenses is "spend cents benching this card".

===============================================================================================================
WHAT IS DELIBERATELY *NOT* HERE
===============================================================================================================
No `dlperf` proxy, no TFLOPS proxy, no "assume it's like a 4090". `--proxy-audit` exists purely to REFUTE that
route on the board's own data: it fits each candidate proxy on the benched cards leave-one-out and prints the
prediction error. Read the number before anyone proposes a derived ranking again.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vast_cost_model as _vcm  # noqa: E402


# =============================================================================================================
# the break-even inversion — PURE, and the only new arithmetic in this file
# =============================================================================================================
def breakeven_ns_per_h(target_usd_per_ns, compute_usd_h, storage_usd_h,
                       hazard_per_h=_vcm.DEFAULT_HAZARD_PER_H, restart_h=0.0,
                       downtime_h=_vcm.DEFAULT_DOWNTIME_H):
    """The ns/h at which this offer's `$/ns` equals `target`. PURE.

    Straight inversion of `vast_cost_model.usd_per_ns`, which is

        u = [ c + s*(1 + lam*D) ] / [ theta * (1 - lam*R) ]     =>     theta = [ c + s*(1+lam*D) ] / [ u*(1-lam*R) ]

    Deliberately expressed by re-deriving the SAME numerator the cost model uses rather than approximating it,
    so a change to the cost function cannot leave this screen quoting a stale relationship. Returns None when
    the target is not positive (nothing to beat) or the configuration is degenerate.
    """
    try:
        u = float(target_usd_per_ns)
    except (TypeError, ValueError):
        return None
    if u <= 0:
        return None
    lam = max(0.0, float(hazard_per_h))
    R, D = max(0.0, float(restart_h)), max(0.0, float(downtime_h))
    useful = 1.0 - lam * R
    if useful <= 0:
        return None
    numer = float(compute_usd_h) + float(storage_usd_h) * (1.0 + lam * D)
    return numer / (u * useful)


def breakeven_ns_per_day(target_usd_per_ns, compute_usd_h, storage_usd_h, **kw):
    """`breakeven_ns_per_h` in the units the bench and the throughput table speak (ns/day). PURE."""
    v = breakeven_ns_per_h(target_usd_per_ns, compute_usd_h, storage_usd_h, **kw)
    return None if v is None else v * 24.0


# =============================================================================================================
# ★★ RULE-OUT vs RULE-IN — they need OPPOSITE bounds, and conflating them is how a wrong number gets ranked
# =============================================================================================================
# trimcrae, 2026-07-27: *"What are the other GPU cards we don't have priced? Could they be reasonably
# competitive in $/ns or can we rule them out with heuristics?"*
#
#   * To rule a card **OUT** you need an UPPER bound on its ns/h. If even the most generous plausible
#     throughput leaves `price / ns_per_h` worse than what the fleet can already buy, the card is dead
#     whatever a benchmark would say — and establishing that costs **$0**.
#   * To rule a card **IN** you need a LOWER bound, which no spec sheet can honestly supply. That is where a
#     measurement is genuinely required, and it is the only thing the bench spend buys.
#
# So the sweep below is deliberately one-directional: it produces `RULED_OUT` and `CANNOT_RULE_OUT`, never
# `competitive`. Nothing here ever enters a ranking, and no card acquires a throughput from it.
#
# ⚠ THE BOUND IS ANCHORED ON THREE BENCHED CARDS, so it is weakest exactly where it matters most — on silicon
# FASTER than an RTX 4090 (RTX 5090, RTX PRO 6000, A100/H100/H200, L40S). Those are flagged as their own class
# and are NOT ruled out by extrapolation; they are the cards a short calibration run is actually for.
#
# HOW THE UPPER BOUND IS BUILT, and why each step errs generous:
#   1. Three candidate predictors (manufacturer FP32, manufacturer memory bandwidth, Vast's own `dlperf`),
#      each fitted as a one-parameter proportional law `ns_day = k*x` on ALL THREE benched cards.
#   2. Each predictor is inflated by `U_p`, its WORST leave-one-out UNDER-prediction ratio over those cards.
#      Under-prediction is the only direction that can wrongly exclude a good card, so that is the tail the
#      inflation is taken from.
#   3. The bound is the MAXIMUM over predictors, not the minimum and not an average — the most generous of
#      three disagreeing heuristics.
#   4. A further `RULE_OUT_MARGIN` is required on top before anything is declared dead, so a spec figure that
#      is wrong in the tight direction still cannot rule a card out.
# The result rules out only cards that are dead by a wide margin under the friendliest reading available.
#
# Manufacturer specs are SPECIFICATIONS, not measurements of MD throughput; they appear here solely to build a
# ceiling. `fp32` is omitted where the public figure is not something we can state with confidence (the
# Blackwell RTX PRO 4000/4500/5000 line), and the bandwidth predictor carries those alone — which is the
# generous direction, so the omission cannot wrongly rule a card out.
RULE_OUT_MARGIN = 1.25

CANDIDATE_SPECS = {
    # normalised gpu_name : (fp32 TFLOPS or None, memory bandwidth GB/s or None)
    "RTX5090":      (104.8, 1792.0),
    "RTX4090D":     (73.5, 1008.0),     # cut-down 4090 SKU — unbenched since 2026-07-27, see vast_cost_model
    "RTXPRO6000WS": (125.0, 1792.0),
    "RTXPRO6000S":  (125.0, 1792.0),    # server variant priced against the workstation figure = generous
    "RTXPRO5000":   (None, 1344.0),
    "RTXPRO4500":   (None, 896.0),
    "RTXPRO4000":   (None, 672.0),
    "A100SXM4":     (19.5, 2039.0),     # 80 GB HBM2e figure used for BOTH SXM4 SKUs = generous
    "A100PCIE":     (19.5, 1935.0),
    "A800PCIE":     (19.5, 1935.0),
    "H100SXM":      (67.0, 3350.0),
    "H100PCIE":     (51.0, 2000.0),
    "H100NVL":      (60.0, 3900.0),
    "H200":         (67.0, 4800.0),
    "H200NVL":      (60.0, 4800.0),
    "B200":         (80.0, 8000.0),
    "L40S":         (91.6, 864.0),
    "L40":          (90.5, 864.0),
    "RTX6000ADA":   (91.1, 960.0),
    "RTX5880ADA":   (69.3, 960.0),
    "RTX5000ADA":   (65.3, 576.0),
    "RTX4000ADA":   (26.7, 360.0),
    "RTXA6000":     (38.7, 768.0),
    "RTXA5000":     (27.8, 768.0),
    "TESLAV100":    (15.7, 900.0),
    "QRTX8000":     (16.3, 672.0),
    "TITANRTX":     (16.3, 672.0),
    "TESLAP100":    (9.5, 732.0),
    "TESLAP40":     (11.8, 346.0),
    "RTX3080":      (29.8, 760.0),
}

# The predictor value for each BENCHED card, i.e. the training set the laws are fitted on. Kept next to
# CANDIDATE_SPECS so a reader can see that the same quantity is being read for training and prediction.
_BENCHED_SPECS = {
    "RTX4090": (82.6, 1008.0),
    "RTX4080": (48.7, 716.8),
    "RTX3090": (35.6, 936.2),
}


def _fit_and_inflate(train):
    """(k, U) for `ns_day = k*x`: k fitted on all of `train`, U = worst LOO UNDER-prediction ratio. PURE.

    `train` is [(card, x, measured_ns_day)]. U is `max(measured/predicted)` over the leave-one-out fits and is
    therefore >= 1 whenever the law ever under-predicts; it is clamped at 1.0 so a law that never
    under-predicts is not allowed to SHRINK the bound. Returns (None, None) if the fit is degenerate."""
    den = sum(x * x for _c, x, _y in train)
    if den <= 0 or len(train) < 2:
        return None, None
    k = sum(x * y for _c, x, y in train) / den
    worst = 1.0
    for i in range(len(train)):
        rest = [t for j, t in enumerate(train) if j != i]
        d = sum(x * x for _c, x, _y in rest)
        if d <= 0:
            continue
        ki = sum(x * y for _c, x, y in rest) / d
        pred = ki * train[i][1]
        if pred > 0:
            worst = max(worst, train[i][2] / pred)
    return k, worst


def throughput_ceilings(dlperf_by_card=None):
    """{predictor: {'k':, 'U':, 'loo':}} — the fitted laws and their generosity inflation. PURE-ish."""
    dl = dlperf_by_card or {}
    out = {}
    for label, x_of in (("fp32_tflops", lambda c: _BENCHED_SPECS.get(c, (None, None))[0]),
                        ("mem_bandwidth_gb_s", lambda c: _BENCHED_SPECS.get(c, (None, None))[1]),
                        ("vast_dlperf", lambda c: dl.get(c))):
        train = [(c, x_of(c), y) for c, y in _vcm.MEASURED_NS_PER_DAY_84K.items() if x_of(c)]
        if len(train) < 2:
            continue
        k, u = _fit_and_inflate(train)
        if k is None:
            continue
        out[label] = {"k": k, "under_prediction_inflation": round(u, 4),
                      "loo": proxy_loo(train), "x_by_card": {c: x for c, x, _y in train}}
    return out


def upper_bound_ns_per_day(gpu_name, ceilings, dlperf=None):
    """The MOST GENEROUS defensible ceiling on this card's ns/day, and which predictor gave it. PURE.

    Returns (bound, detail) or (None, {}) when no predictor has an input for this card — in which case the
    card CANNOT be ruled out, because a missing spec is not evidence of slowness."""
    n = _vcm.normalise_gpu_name(gpu_name)
    fp32, bw = CANDIDATE_SPECS.get(n, (None, None))
    xs = {"fp32_tflops": fp32, "mem_bandwidth_gb_s": bw, "vast_dlperf": dlperf}
    best, best_point, detail = None, None, {}
    for label, c in ceilings.items():
        x = xs.get(label)
        if not x:
            continue
        point = c["k"] * float(x)                      # the law's own prediction, uninflated
        v = point * c["under_prediction_inflation"]    # ...made generous, which is what a rule-out needs
        detail[label] = round(v, 1)
        if best is None or v > best:
            best = v
        if best_point is None or point > best_point:
            best_point = point
    # `point_prediction` is reported ONLY so the "is this card faster than anything we have benched" question
    # can be asked of the laws' own estimate rather than of the inflated ceiling — every ceiling clears the
    # reference by construction, so flagging off the ceiling would mark the whole board as fast.
    if best_point is not None:
        detail["point_prediction"] = round(best_point, 1)
    return best, detail


def rule_out(breakeven_nsd, bound_nsd, margin=RULE_OUT_MARGIN):
    """('RULED_OUT'|'CANNOT_RULE_OUT', headroom) for one card. PURE.

    RULED_OUT requires the break-even to exceed the generous ceiling by a further `margin`, so a spec figure
    that is wrong in the tight direction still cannot kill a card. `headroom` is break-even / bound: below 1
    the card is comfortably alive, above `margin` it is dead."""
    if breakeven_nsd is None or not bound_nsd:
        return "CANNOT_RULE_OUT", None
    h = float(breakeven_nsd) / float(bound_nsd)
    return ("RULED_OUT" if h > margin else "CANNOT_RULE_OUT"), round(h, 3)


def plausibility(breakeven_nsd, reference_ns_per_day=None):
    """A LABEL for a break-even, expressed as a multiple of the reference card. PURE. Never a throughput.

    The reference card is the fastest thing we have ever benched, so a break-even ABOVE it means the candidate
    would have to beat our best measured card to be worth taking at this price — which is the honest way to say
    "do not bother" without asserting how fast the card is. Thresholds are coarse on purpose: this decides
    whether to spend ~$0.05 on a bench, and a false 'bench it' costs five cents while a false 'skip it' costs
    the whole widening.
    """
    ref = float(reference_ns_per_day or _vcm.MEASURED_NS_PER_DAY_84K[_vcm.REFERENCE_CARD])
    if breakeven_nsd is None or ref <= 0:
        return "unknown", None
    m = breakeven_nsd / ref
    if m <= 0.5:
        lab = "BENCH — clears at under half the reference card's measured rate"
    elif m <= 1.0:
        lab = "BENCH — clears below the reference card's measured rate"
    elif m <= 1.5:
        lab = "marginal — needs to beat the reference card"
    else:
        lab = "skip — would have to be far faster than anything we have benched"
    return lab, round(m, 3)


# =============================================================================================================
# the census
# =============================================================================================================
def _gb(offer):
    ram = float(offer.get("gpu_ram", 0) or 0)
    return ram / 1024.0 if ram > 1000 else ram


def census(offers, res, job=None, n_units=19, top_target=None):
    """Break a board down by GPU model: who is priceable, who is not, and what the missing ones would add. PURE.

    `offers` is a raw Vast `/search/asks/` list. The hard filter and the score are BOTH delegated to
    `gpu_backend.rank_offers_by_usd_per_ns` — the same call the renting path and the market guard make — so a
    census row cannot describe a board the launcher would not actually see.
    """
    from gpu_backend import rank_offers_by_usd_per_ns, _vast_bid_price

    measured, capable = rank_offers_by_usd_per_ns(offers, res)
    job = job or _vcm.JobProfile(disk_gb=max(40, res.disk_gb), min_vram_gb=res.min_vram_gb,
                                 min_reliability=res.min_reliability, min_cuda=res.min_cuda)
    upn_by_id = {id(o): u for u, _p, o in measured}

    # The target every unbenched model is screened against: what the fleet can achieve TODAY on the gradeable
    # part of the board. Screening against the single best offer would demand a card beat a lucky draw; the
    # fleet mean is what widening would actually displace.
    take = measured[:max(1, int(n_units))]
    fleet_mean = (sum(u for u, _p, _o in take) / len(take)) if take else None
    target = top_target if top_target is not None else fleet_mean

    groups = {}
    for _p, o in capable:
        groups.setdefault(str(o.get("gpu_name") or "?"), []).append(o)

    # Board-median `dlperf` per model: the one predictor input that comes from the board itself rather than a
    # spec sheet, so it exists for cards whose manufacturer figures we would otherwise have to guess at.
    dl_by_name, dl_by_card = {}, {}
    for name, offs in groups.items():
        vals = []
        for o in offs:
            try:
                v = float(o.get("dlperf") or 0)
            except (TypeError, ValueError):
                continue
            if v > 0:
                vals.append(v)
        if vals:
            dl_by_name[name] = st.median(vals)
            c = _vcm.card_of(name)
            if c and _vcm.throughput_provenance(name)[0] == "measured":
                dl_by_card[c] = st.median(vals)
    ceilings = throughput_ceilings(dl_by_card)

    rows = []
    for name, offs in groups.items():
        card = _vcm.card_of(name)
        floors, allin, upns = [], [], []
        for o in offs:
            try:
                floor = float(o.get("min_bid") or 0)
            except (TypeError, ValueError):
                continue
            if floor <= 0:
                continue
            bid = _vast_bid_price(o) or floor
            s = _vcm.storage_usd_per_h(o.get("storage_cost"), job.disk_gb)
            floors.append(floor)
            allin.append(bid + s)
            if id(o) in upn_by_id:
                upns.append(upn_by_id[id(o)])
        if not floors:
            continue
        i_cheap = min(range(len(allin)), key=lambda i: allin[i])
        cheap_off = offs[i_cheap]
        row = {
            "gpu_name": name,
            "n_offers": len(offs),
            "priceable": bool(card),
            "benched_as": card,
            "vram_gb": round(_gb(cheap_off), 1),
            "min_floor_usd_h": round(min(floors), 4),
            "median_floor_usd_h": round(st.median(floors), 4),
            "cheapest_all_in_usd_h": round(min(allin), 4),
            "median_all_in_usd_h": round(st.median(allin), 4),
        }
        if upns:
            prov, base, note = _vcm.throughput_provenance(name)
            row["best_usd_per_ns"] = round(min(upns), 6)
            row["median_usd_per_ns"] = round(st.median(upns), 6)
            # A priceable row must say WHERE its ns/h came from: a conservative alias is a one-sided derived
            # bound, and a reader who cannot tell it from a measurement is exactly the failure the alias
            # allow-list exists to prevent.
            row["throughput_provenance"] = prov
            row["throughput_base_card"] = base
            if prov != "measured":
                row["throughput_note"] = note
        else:
            bid = _vast_bid_price(cheap_off) or min(floors)
            s = _vcm.storage_usd_per_h(cheap_off.get("storage_cost"), job.disk_gb)
            be = breakeven_ns_per_day(target, bid, s, hazard_per_h=job.hazard_per_h,
                                      restart_h=job.restart_h, downtime_h=job.downtime_h)
            lab, mult = plausibility(be)
            row["breakeven_ns_per_day_vs_fleet_mean"] = (None if be is None else round(be, 1))
            row["breakeven_x_reference_card"] = mult
            row["plausibility"] = lab
            # The same question asked against the ladder basis rather than today's achievable mean: a card that
            # clears THIS is one that would end the hold outright, not merely improve the mean.
            from congeneric_fanout import basis_usd_per_ns
            beb = breakeven_ns_per_day(basis_usd_per_ns(), bid, s, hazard_per_h=job.hazard_per_h,
                                       restart_h=job.restart_h, downtime_h=job.downtime_h)
            row["breakeven_ns_per_day_vs_ladder_basis"] = (None if beb is None else round(beb, 1))
            row["breakeven_x_reference_card_vs_basis"] = plausibility(beb)[1]
            # --- the $0 rule-out sweep -------------------------------------------------------------------
            bound, detail = upper_bound_ns_per_day(name, ceilings, dl_by_name.get(name))
            verdict, headroom = rule_out(be, bound)
            row["upper_bound_ns_per_day"] = (None if bound is None else round(bound, 1))
            row["upper_bound_by_predictor"] = detail
            row["upper_bound_x_reference_card"] = (None if bound is None else
                                                   round(bound / _vcm.MEASURED_NS_PER_DAY_84K[
                                                       _vcm.REFERENCE_CARD], 2))
            row["headroom_breakeven_over_bound"] = headroom
            row["verdict"] = verdict
            # ⚠ The bound is anchored on three cards all SLOWER than or equal to the reference. A candidate
            # whose ceiling lands above the reference is being extrapolated, and that is precisely the class
            # a spec heuristic cannot settle — flagged so a rule-out there is never taken on trust.
            row["faster_than_reference_class"] = bool(
                detail.get("point_prediction", 0) > _vcm.MEASURED_NS_PER_DAY_84K[_vcm.REFERENCE_CARD])
            if bound is None:
                row["verdict_note"] = ("no predictor input for this model — a missing spec is not evidence of "
                                       "slowness, so it cannot be ruled out")
        rows.append(row)

    rows.sort(key=lambda r: (r["priceable"], -r["n_offers"]))
    n_price = sum(r["n_offers"] for r in rows if r["priceable"])
    n_unpriced = sum(r["n_offers"] for r in rows if not r["priceable"])
    return {
        "board_depth": {"offers_returned": len(offers), "qualifying": len(capable),
                        "priceable": len(measured), "needed": int(n_units),
                        "used_for_mean": len(take)},
        "fleet_mean_usd_per_ns": (round(fleet_mean, 6) if fleet_mean is not None else None),
        "screening_target_usd_per_ns": (round(target, 6) if target else None),
        "qualifying_offers_priceable": n_price,
        "qualifying_offers_unpriceable": n_unpriced,
        "unpriceable_fraction": (round(n_unpriced / max(1, n_price + n_unpriced), 3)),
        "by_gpu_model": rows,
        "throughput_ceilings": {k: {"k": round(v["k"], 5),
                                    "under_prediction_inflation": v["under_prediction_inflation"],
                                    "max_abs_loo_rel_err": v["loo"]["max_abs_rel_err"],
                                    "x_by_card": v["x_by_card"]}
                                for k, v in ceilings.items()},
        "rule_out_margin": RULE_OUT_MARGIN,
        # RULED OUT AT $0 — dead by a wide margin under the friendliest reading of three disagreeing
        # heuristics. No bench is warranted and no measurement would change the answer.
        "ruled_out": [
            {"gpu_name": r["gpu_name"], "n_offers": r["n_offers"],
             "cheapest_all_in_usd_h": r["cheapest_all_in_usd_h"],
             "breakeven_ns_per_day": r.get("breakeven_ns_per_day_vs_fleet_mean"),
             "upper_bound_ns_per_day": r.get("upper_bound_ns_per_day"),
             "headroom": r.get("headroom_breakeven_over_bound")}
            for r in sorted((x for x in rows if not x["priceable"] and x.get("verdict") == "RULED_OUT"),
                            key=lambda x: -x["n_offers"])],
        # CANNOT BE RULED OUT — the only list a bench spend may be aimed at, ranked by the gradeable supply
        # each would add. `faster_than_reference` marks the ones the bound is extrapolating on and therefore
        # cannot settle either way.
        "bench_shortlist": [
            {"gpu_name": r["gpu_name"], "n_offers": r["n_offers"], "vram_gb": r["vram_gb"],
             "cheapest_all_in_usd_h": r["cheapest_all_in_usd_h"],
             "breakeven_ns_per_day": r.get("breakeven_ns_per_day_vs_fleet_mean"),
             "breakeven_x_reference_card": r.get("breakeven_x_reference_card"),
             "upper_bound_ns_per_day": r.get("upper_bound_ns_per_day"),
             "headroom": r.get("headroom_breakeven_over_bound"),
             "faster_than_reference": r.get("faster_than_reference_class"),
             "plausibility": r.get("plausibility")}
            for r in sorted((x for x in rows if not x["priceable"] and x.get("verdict") != "RULED_OUT"),
                            key=lambda x: (x.get("headroom_breakeven_over_bound") or 9e9, -x["n_offers"]))],
    }


# =============================================================================================================
# --proxy-audit — the refutation, so nobody re-proposes a derived ranking without seeing the error
# =============================================================================================================
def proxy_loo(pairs):
    """Leave-one-out error of a one-parameter proportional fit `ns_day ~ k * x`. PURE.

    `pairs` is [(card, x, measured_ns_day)]. With n benched cards this fits k on n-1 of them and predicts the
    held-out one, which is the ONLY honest way to report a proxy's accuracy from a table this small. Returns
    per-card relative errors plus the worst and mean absolute relative error.
    """
    out = []
    for i, (card, _x, meas) in enumerate(pairs):
        rest = [p for j, p in enumerate(pairs) if j != i]
        if not rest or not pairs[i][1]:
            continue
        # least-squares k for y = k*x over the training cards
        num = sum(px * py for _c, px, py in rest)
        den = sum(px * px for _c, px, _py in rest)
        if den <= 0:
            continue
        k = num / den
        pred = k * pairs[i][1]
        out.append({"card": card, "measured_ns_day": round(meas, 2), "predicted_ns_day": round(pred, 2),
                    "rel_err": round((pred - meas) / meas, 4) if meas else None})
    errs = [abs(r["rel_err"]) for r in out if r["rel_err"] is not None]
    return {"per_card": out,
            "max_abs_rel_err": (round(max(errs), 4) if errs else None),
            "mean_abs_rel_err": (round(sum(errs) / len(errs), 4) if errs else None)}


# Public spec figures for the benched cards, used ONLY by the audit below to refute the proxy route. They are
# not throughputs and nothing may rank on them.
#   fp32_tflops / mem_bw_gb_s: manufacturer spec (NVIDIA product pages, boost clocks, GDDR6X/GDDR7 rates).
#   dlperf: Vast's own composite score, taken as the board median per model at audit time (see --offers).
_SPEC = {
    "RTX4090": {"fp32_tflops": 82.6, "mem_bw_gb_s": 1008.0},
    "RTX4080": {"fp32_tflops": 48.7, "mem_bw_gb_s": 716.8},   # 4080 SUPER: 52.2 TFLOPS / 736.3 GB/s
    "RTX3090": {"fp32_tflops": 35.6, "mem_bw_gb_s": 936.2},
}


def proxy_audit(offers=None):
    """Fit every candidate proxy on the benched cards leave-one-out and report the error. PURE-ish (reads
    `offers` only for the board-median `dlperf` per benched model)."""
    dl = {}
    if offers:
        buck = {}
        for o in offers:
            c = _vcm.card_of(o.get("gpu_name"))
            if c:
                try:
                    buck.setdefault(c, []).append(float(o.get("dlperf") or 0))
                except (TypeError, ValueError):
                    pass
        dl = {c: st.median([x for x in v if x > 0]) for c, v in buck.items() if any(x > 0 for x in v)}

    res = {}
    for label, getter in (("fp32_tflops", lambda c: _SPEC.get(c, {}).get("fp32_tflops")),
                          ("mem_bandwidth_gb_s", lambda c: _SPEC.get(c, {}).get("mem_bw_gb_s")),
                          ("vast_dlperf", lambda c: dl.get(c))):
        pairs = [(c, getter(c), v) for c, v in _vcm.MEASURED_NS_PER_DAY_84K.items() if getter(c)]
        if len(pairs) < 2:
            res[label] = {"error": "not enough benched cards carry this spec"}
            continue
        res[label] = proxy_loo(pairs)
        res[label]["x_by_card"] = {c: x for c, x, _y in pairs}
    res["_verdict_rule"] = ("A derived ns/day may only be used if its leave-one-out error is small enough that "
                            "a mis-ranking is impossible at the price spreads on the board. The board's best "
                            "and worst gradeable offers differ by ~4x in $/ns, so an error above ~15-20% can "
                            "invert a ranking and the route is dead.")
    return res


# =============================================================================================================
# CLI
# =============================================================================================================
def _live_offers(key, res):
    from gpu_backend import _vast_offer_query, _vast_request
    return _vast_request("GET", "/search/asks/", key,
                         params={"q": json.dumps(_vast_offer_query(res))}).get("offers", [])


def _main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offers", default="", help="raw offers JSON (vast_market_intel output or a bare list); "
                                                 "omitted => LIVE pull with VAST_API_KEY")
    ap.add_argument("--units", type=int, default=19, help="fleet size the screen is judged against")
    ap.add_argument("--proxy-audit", action="store_true", help="also run the derived-throughput refutation")
    ap.add_argument("--json-out", default="vast-board-census.json")
    a = ap.parse_args(argv)

    from congeneric_fanout_vast import FANOUT_RES
    if a.offers:
        blob = json.load(open(a.offers))
        offers = blob if isinstance(blob, list) else (blob.get("offers") or {})
        if isinstance(offers, dict):
            offers = offers.get("bid") or []
        src = a.offers
    else:
        key = os.environ.get("VAST_API_KEY")
        if not key:
            print("no VAST_API_KEY and no --offers: nothing to census", file=sys.stderr)
            return 2
        offers = _live_offers(key, FANOUT_RES)
        src = "live"

    doc = census(offers, FANOUT_RES, n_units=a.units)
    doc["_what"] = ("Why a qualifying Vast board cannot be priced, broken down by GPU model, with the "
                    "break-even ns/day each unbenched model would need to be worth benching. "
                    "A break-even is a SCREEN, never a throughput.")
    doc["source"] = src
    doc["utc"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())
    if a.proxy_audit:
        doc["proxy_audit"] = proxy_audit(offers)

    d = doc["board_depth"]
    print(f"=== BOARD: {d['offers_returned']} returned -> {d['qualifying']} qualifying -> "
          f"{d['priceable']} PRICEABLE (need {d['needed']}) ===")
    print(f"    unpriceable fraction of qualifying offers: {doc['unpriceable_fraction']:.1%} "
          f"({doc['qualifying_offers_unpriceable']} of "
          f"{doc['qualifying_offers_unpriceable'] + doc['qualifying_offers_priceable']})")
    print(f"    fleet mean $/ns over the {d['used_for_mean']} cheapest gradeable = {doc['fleet_mean_usd_per_ns']}")
    print(f"\n{'gpu_name':20s} {'n':>4} {'VRAM':>5} {'cheap $/hr':>11} {'med $/hr':>9}  status")
    for r in doc["by_gpu_model"]:
        if r["priceable"]:
            statx = (f"PRICEABLE as {r['benched_as']} [{r.get('throughput_provenance')}] — "
                     f"best $/ns {r.get('best_usd_per_ns')}")
        else:
            statx = (f"{r.get('verdict')} — needs {r.get('breakeven_ns_per_day_vs_fleet_mean')} ns/day, "
                     f"ceiling {r.get('upper_bound_ns_per_day')} (headroom "
                     f"{r.get('headroom_breakeven_over_bound')})"
                     + ("  ★faster-than-reference class" if r.get("faster_than_reference_class") else ""))
        print(f"{r['gpu_name']:20s} {r['n_offers']:4d} {r['vram_gb']:5.0f} "
              f"{r['cheapest_all_in_usd_h']:11.4f} {r['median_all_in_usd_h']:9.4f}  {statx}")
    if doc["ruled_out"]:
        n = sum(r["n_offers"] for r in doc["ruled_out"])
        print(f"\n=== RULED OUT AT $0 ({len(doc['ruled_out'])} models, {n} offers) — dead even at the most "
              f"generous ceiling three disagreeing heuristics can defend, x{doc['rule_out_margin']} margin ===")
        for r in doc["ruled_out"]:
            print(f"  {r['gpu_name']:20s} {r['n_offers']:3d} offers @ ${r['cheapest_all_in_usd_h']:.4f}/hr  "
                  f"needs {r['breakeven_ns_per_day']} ns/day vs a ceiling of {r['upper_bound_ns_per_day']} "
                  f"({r['headroom']}x too slow)")
    if doc["bench_shortlist"]:
        n = sum(r["n_offers"] for r in doc["bench_shortlist"])
        print(f"\n=== CANNOT BE RULED OUT ({len(doc['bench_shortlist'])} models, {n} offers) — a measurement "
              f"is the only thing that settles these ===")
        for r in doc["bench_shortlist"]:
            print(f"  {r['gpu_name']:20s} +{r['n_offers']:3d} offers  @ ${r['cheapest_all_in_usd_h']:.4f}/hr  "
                  f"needs {r['breakeven_ns_per_day']} ns/day ({r['breakeven_x_reference_card']}x ref), "
                  f"ceiling {r['upper_bound_ns_per_day']}"
                  + ("  ★faster-than-reference" if r.get("faster_than_reference") else ""))
    if a.proxy_audit:
        print("\n=== PROXY AUDIT (leave-one-out over the benched cards) ===")
        for k, v in doc["proxy_audit"].items():
            if k.startswith("_"):
                continue
            print(f"  {k:20s} max|rel err| = {v.get('max_abs_rel_err')}  mean = {v.get('mean_abs_rel_err')}")
            for p in v.get("per_card", []):
                print(f"      {p['card']:9s} measured {p['measured_ns_day']:8.2f}  "
                      f"predicted {p['predicted_ns_day']:8.2f}  err {p['rel_err']:+.1%}")

    if a.json_out:
        with open(a.json_out, "w") as f:
            json.dump(doc, f, indent=1)
        print(f"\nwrote {a.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
