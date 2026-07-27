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
            row["best_usd_per_ns"] = round(min(upns), 6)
            row["median_usd_per_ns"] = round(st.median(upns), 6)
        else:
            bid = _vast_bid_price(cheap_off) or min(floors)
            s = _vcm.storage_usd_per_h(cheap_off.get("storage_cost"), job.disk_gb)
            be = breakeven_ns_per_day(target, bid, s, hazard_per_h=job.hazard_per_h,
                                      restart_h=job.restart_h, downtime_h=job.downtime_h)
            lab, mult = plausibility(be)
            row["breakeven_ns_per_day_vs_fleet_mean"] = (None if be is None else round(be, 1))
            row["breakeven_x_reference_card"] = mult
            row["verdict"] = lab
            # The same question asked against the ladder basis rather than today's achievable mean: a card that
            # clears THIS is one that would end the hold outright, not merely improve the mean.
            from congeneric_fanout import basis_usd_per_ns
            beb = breakeven_ns_per_day(basis_usd_per_ns(), bid, s, hazard_per_h=job.hazard_per_h,
                                       restart_h=job.restart_h, downtime_h=job.downtime_h)
            row["breakeven_ns_per_day_vs_ladder_basis"] = (None if beb is None else round(beb, 1))
            row["breakeven_x_reference_card_vs_basis"] = plausibility(beb)[1]
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
        # The whole point of the census: ranked by supply added, restricted to models the break-even says are
        # worth a bench. This is the bench shortlist, and nothing else in the repo should be inventing one.
        "bench_shortlist": [
            {"gpu_name": r["gpu_name"], "n_offers": r["n_offers"], "vram_gb": r["vram_gb"],
             "cheapest_all_in_usd_h": r["cheapest_all_in_usd_h"],
             "breakeven_ns_per_day": r.get("breakeven_ns_per_day_vs_fleet_mean"),
             "breakeven_x_reference_card": r.get("breakeven_x_reference_card"),
             "verdict": r.get("verdict")}
            for r in sorted((x for x in rows if not x["priceable"]), key=lambda x: -x["n_offers"])
            if str(r.get("verdict", "")).startswith("BENCH")
        ],
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
            statx = f"PRICEABLE as {r['benched_as']} — best $/ns {r.get('best_usd_per_ns')}"
        else:
            statx = (f"unpriceable — needs {r.get('breakeven_ns_per_day_vs_fleet_mean')} ns/day "
                     f"({r.get('breakeven_x_reference_card')}x ref) : {r.get('verdict')}")
        print(f"{r['gpu_name']:20s} {r['n_offers']:4d} {r['vram_gb']:5.0f} "
              f"{r['cheapest_all_in_usd_h']:11.4f} {r['median_all_in_usd_h']:9.4f}  {statx}")
    if doc["bench_shortlist"]:
        print("\n=== BENCH SHORTLIST (ranked by gradeable supply it would add) ===")
        for r in doc["bench_shortlist"]:
            print(f"  {r['gpu_name']:20s} +{r['n_offers']:3d} offers  @ ${r['cheapest_all_in_usd_h']:.4f}/hr  "
                  f"needs {r['breakeven_ns_per_day']} ns/day ({r['breakeven_x_reference_card']}x ref)")
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
