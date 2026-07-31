#!/usr/bin/env python3
"""WHICH OF OUR OWN FILTERS IS EATING THE BOARD — an offers-surviving count per filter, off ONE board read.

★★ THE QUESTION THIS ANSWERS, AND WHY IT IS NOT THE ONE `vast_board_census.py` ANSWERS (trimcrae, 2026-07-31:
*"If we're in a price spike we can wait that out, that's fine. But the floor being 2x over baseline would be
quite unusual. Make sure we aren't filtering too many options out."*).

The census asks "the board qualified — why could it not be PRICED?" (the answer is the benched-card table).
`vast_exclusion_census.py` asks "how much is the machine BLACKLIST costing?". Neither asks the third question:
of the hard filters in `ResourceSpec` — CUDA floor, VRAM, host RAM, cores, disk, reliability, the `min_ns_per_h`
card floor — **which one removes the most offers, and what does removing it do to the achievable `$/ns`?**
Until that is measured, a narrow board reads as a thin market, and the two call for opposite actions: a thin
market is waited out (CLAUDE.md §6), an over-tight filter is fixed.

★ WHY EVERY COUNT COMES OFF ONE READ. `/search/asks/` is a ROTATING SAMPLE — `gpu_backend._vast_request`
records the measurement: two identical reads 20 s apart share only ~174 machines and P(present, then absent)
= 0.245. So counting filter A against one read and filter B against another measures the sampler, not the
filter. This module therefore takes a SINGLE permissive read per tier and applies every filter client-side
to that same list. The absolute counts move between runs; the RATIOS between filters do not.

★ WHAT IT REPORTS PER FILTER, and why both numbers are needed:
  * `alone`      — offers surviving when ONLY this filter is applied. "How much of the board does this
                   predicate reach at all."
  * `leave_out`  — offers surviving the FULL spec with this one filter removed. The difference from `full`
                   is what the filter costs **on top of everything else**, which is the actionable number:
                   a filter that is redundant with another has a big `alone` loss and a zero `leave_out` gain.
  * `best_usd_per_ns` / `ratio_vs_basis` for the leave-one-out board — because width is not the point,
    PRICE is. A filter that removes 60 offers and does not move the achievable $/ns is not costing us money.

⛔ WHAT THIS DELIBERATELY DOES NOT DO. It never rents, never writes an exclusion set, and never changes a
filter. It prices `type: bid` and `type: on-demand` SEPARATELY and labels them, because conflating the two is
exactly the misreading that started this: the uninterruptible tier is small and dear by construction, and a
hold priced against it says nothing about the market the ladder is costed on. The buy line is untouched
throughout — this is about SEEING the whole board, never about paying more per ns.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vast_cost_model as _vcm  # noqa: E402


# =============================================================================================================
# the predicates — PURE, one per hard filter in the launcher, named the same
# =============================================================================================================
def _f(o, k, default=None):
    v = o.get(k, default)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _gpu_ram_gb(o):
    v = _f(o, "gpu_ram")
    return (v / 1024.0) if v else 0.0


def predicates(res):
    """{name: offer -> bool} for every hard filter the launcher applies, server-side or client-side.

    Mirrors `gpu_backend._vast_offer_query` (the server query) and `gpu_backend.rank_offers_by_usd_per_ns`
    (the client re-filter) rather than re-inventing thresholds: each entry reads its bound off the SAME
    `ResourceSpec`, so a spec change moves this measurement with it and cannot leave it quoting a stale floor.
    `cuda_max_good` is deliberately listed once even though it is applied TWICE in the launcher — the count of
    offers it removes is the same either way.
    """
    excl = {str(m) for m in (res.exclude_machine_ids or ())}
    return {
        "verified": lambda o: o.get("verified") is not False,
        "rentable": lambda o: o.get("rentable") is not False,
        "num_gpus_1": lambda o: int(o.get("num_gpus") or 1) == 1,
        "gpu_ram(min_vram_gb)": lambda o: _gpu_ram_gb(o) + 0.5 >= res.min_vram_gb,
        "cpu_ram(ram_gb)": lambda o: (_f(o, "cpu_ram") or 0) >= res.ram_gb * 1024,
        "cpu_cores(vcpus)": lambda o: (_f(o, "cpu_cores") or 0) >= res.vcpus,
        "disk_space(disk_gb)": lambda o: (_f(o, "disk_space") or 0) >= res.disk_gb,
        "reliability2": lambda o: (_f(o, "reliability2") or 0) >= res.min_reliability,
        "cuda_max_good(min_cuda)": lambda o: (_f(o, "cuda_max_good") or 0) >= res.min_cuda,
        "min_ns_per_h": (lambda o: True) if not res.min_ns_per_h else (
            lambda o: bool(_vcm.ns_per_hour(o.get("gpu_name")))
            and _vcm.ns_per_hour(o.get("gpu_name")) >= float(res.min_ns_per_h)),
        "exclude_machine_ids": lambda o: str(o.get("machine_id")) not in excl,
    }


def survivors(offers, preds, names):
    return [o for o in offers if all(preds[n](o) for n in names)]


# =============================================================================================================
# pricing a candidate board — DELEGATED, never re-derived (CLAUDE.md §1: one home for $/ns)
# =============================================================================================================
def price_board(offers, res, interruptible, n_units=1):
    """(best_mean_usd_per_ns, n_priceable, rows) for `offers`, using the SAME scorer the gate and the launcher
    use. Not a second opinion about price: `vast_cost_model.score_offer` is the one home, and a filter study
    that scored offers its own way could 'find' a saving that the launcher can never realise."""
    job = _vcm.JobProfile(disk_gb=max(40, res.disk_gb), min_vram_gb=res.min_vram_gb,
                          min_reliability=res.min_reliability, min_cuda=res.min_cuda)
    scored = []
    for o in offers:
        try:
            price = float(o.get("min_bid")) if (interruptible and o.get("min_bid") is not None) \
                else float(o.get("dph_total", o.get("dph_base", 1e9)))
        except (TypeError, ValueError):
            continue
        s = _vcm.score_offer(o, job, billed_usd_h=(None if interruptible else price))
        if s is None:
            continue
        scored.append((s.usd_per_ns, price, o))
    scored.sort(key=lambda t: (t[0], t[1]))
    take = scored[:max(1, int(n_units))]
    best = (sum(u for u, _p, _o in take) / len(take)) if take else None
    rows = [{"gpu": o.get("gpu_name"), "machine_id": o.get("machine_id"),
             "price_usd_h": round(p, 4), "usd_per_ns": round(u, 6)} for u, p, o in take]
    return best, len(scored), rows


def ablate(offers, res, interruptible, n_units=1, basis=None):
    """The whole study for one tier's board. PURE given `offers`."""
    preds = predicates(res)
    names = list(preds)
    basis = basis or _basis()
    full = survivors(offers, preds, names)
    fb, fp, frows = price_board(full, res, interruptible, n_units)
    out = {
        "tier": "bid (interruptible)" if interruptible else "on-demand (uninterruptible)",
        "offers_returned": len(offers),
        "full_spec": {"surviving": len(full), "priceable": fp,
                      "best_usd_per_ns": (round(fb, 6) if fb else None),
                      "ratio_vs_basis": (round(fb / basis, 3) if fb else None),
                      "rows": frows},
        "per_filter": [],
    }
    for n in names:
        alone = survivors(offers, preds, [n])
        loo = survivors(offers, preds, [x for x in names if x != n])
        lb, lp, _ = price_board(loo, res, interruptible, n_units)
        out["per_filter"].append({
            "filter": n,
            "bound": _bound_of(n, res),
            "alone_surviving": len(alone),
            "alone_removed": len(offers) - len(alone),
            "leave_out_surviving": len(loo),
            "leave_out_priceable": lp,
            # THE ACTIONABLE NUMBER: offers this filter removes ON TOP OF every other filter.
            "marginal_cost_offers": len(loo) - len(full),
            "leave_out_best_usd_per_ns": (round(lb, 6) if lb else None),
            "leave_out_ratio_vs_basis": (round(lb / basis, 3) if lb else None),
            # And what dropping it would buy, in the only currency that matters.
            "usd_per_ns_improvement_pct": (round(100.0 * (fb - lb) / fb, 1)
                                           if (fb and lb and fb > 0) else None),
            # ⚠ THE GAIN IS NOT ALWAYS A SAVING — see FILTER_CAVEATS.
            "caveat": FILTER_CAVEATS.get(n),
        })
    out["per_filter"].sort(key=lambda r: -r["marginal_cost_offers"])
    return out


# ★★ A FILTER'S `$/ns` "SAVING" IS COMPUTED ON **TABLE** THROUGHPUT, WHICH CANNOT SEE SETUP TIME.
# That makes the gain column systematically WRONG for any filter that exists to protect a CPU-side phase —
# and one of them does. Recorded here rather than in a message, because the ablation's own numbers are what
# somebody will read when they propose relaxing a floor.
FILTER_CAVEATS = {
    "cpu_ram(ram_gb)": (
        "⛔ DO NOT RELAX. The gain shown is an ARTEFACT of a metric blind to setup. `ternary-rbfe-runbook.md` "
        "§2 root-caused, by serial console, setup varying 8 min <-> 30 min on 'the same machine': the "
        "provisioner had silently fallen back to a 4 vCPU / 16 GB box, and openff `interchange` "
        "parameterising a ~146k-atom system is CPU+RAM bound, so 16 GB swaps and runs ~4x slower. Same GPU, "
        "so MD — and therefore every $/ns in this table — is UNAFFECTED. A ~4x setup penalty on a cold start "
        "of tens of minutes, against a ~1.00 h median session, converts a rental that banks into one that "
        "does not. This floor is doing real work."),
    "cuda_max_good(min_cuda)": (
        "MEASURED, and already acted on: `probe_image_cuda.py` read the baked image's own libnvrtc and the "
        "ternary lane's floor moved 13.0 -> 12.6 (image-cuda-requirements.json). An image that has NOT been "
        "probed keeps the conservative default."),
    "min_ns_per_h": (
        "A card floor is a SPEED preference, not a cost one. The 5a-KS floor was reverted on the fan-out's "
        "208-rental ledger (3090-class held a 1.50 h median vs 1.65 h for 4090/5090-class); the triangle "
        "keeps its own on a direct observation. One home: ternary_vast_launch.MODE_MIN_NS_PER_H."),
}


def _bound_of(name, res):
    return {
        "gpu_ram(min_vram_gb)": ">= %s GB" % res.min_vram_gb,
        "cpu_ram(ram_gb)": ">= %s GB" % res.ram_gb,
        "cpu_cores(vcpus)": ">= %s" % res.vcpus,
        "disk_space(disk_gb)": ">= %s GB" % res.disk_gb,
        "reliability2": ">= %s" % res.min_reliability,
        "cuda_max_good(min_cuda)": ">= %s" % res.min_cuda,
        "min_ns_per_h": (">= %s ns/h" % res.min_ns_per_h) if res.min_ns_per_h else "UNSET (no-op)",
        "exclude_machine_ids": "%d machine(s)" % len(res.exclude_machine_ids or ()),
    }.get(name, "-")


def cuda_sweep(offers, res, interruptible, n_units=1, values=(0.0, 12.0, 12.4, 12.6, 12.8, 13.0), basis=None):
    """The CUDA floor swept, with the rest of the spec held. The one filter whose bound is a CLAIM ABOUT OUR
    IMAGE rather than a resource requirement, so it is the one worth seeing as a curve: every other floor is
    a fact about the job, this one is a hypothesis about the container."""
    basis = basis or _basis()
    preds = predicates(res)
    others = [n for n in preds if n != "cuda_max_good(min_cuda)"]
    base = survivors(offers, preds, others)
    rows = []
    for v in values:
        keep = [o for o in base if (_f(o, "cuda_max_good") or 0) >= v]
        b, p, top = price_board(keep, res, interruptible, n_units)
        rows.append({"min_cuda": v, "surviving": len(keep), "priceable": p,
                     "best_usd_per_ns": (round(b, 6) if b else None),
                     "ratio_vs_basis": (round(b / basis, 3) if b else None),
                     "best_offer": (top[0] if top else None)})
    return rows


def _basis():
    from congeneric_fanout import basis_usd_per_ns
    return basis_usd_per_ns()


# =============================================================================================================
# the RETIRED durable blacklist, priced as a counterfactual
# =============================================================================================================
def retired_blacklist_ids(paths=()):
    """The machine ids the DURABLE exclusion list held, read from the committed snapshots.

    ★ WHY THIS IS MEASURED RATHER THAN ASSERTED (trimcrae, 2026-07-31: *"You've gotta just stop doing the
    blacklist"*). The list is now inert at the read path, so `ResourceSpec.exclude_machine_ids` is empty and
    its ablation row would read `0 removed` — which is true and useless. The number that settles whether the
    removal was worth doing is the COUNTERFACTUAL: how much of TODAY's board those ids would have removed.
    Read from `vast-blacklist-snapshot-*.json` rather than S3 so the study runs with no AWS creds and is
    reproducible from the repo alone.
    """
    import glob
    if not paths:
        here = os.path.dirname(os.path.abspath(__file__))
        paths = sorted(glob.glob(os.path.join(here, "vast-blacklist-snapshot-*.json")))
    ids, seen = set(), []
    for p in paths:
        try:
            with open(p) as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        got = set()
        for holder in (d, d.get("shared") or {}, d.get("doc") or {}):
            if isinstance(holder, dict):
                got |= {str(m) for m in (holder.get("machine_ids") or [])}
        for lane in (d.get("lanes") or {}).values():
            if isinstance(lane, dict):
                got |= {str(m) for m in (lane.get("machine_ids") or [])}
                got |= {str(m) for m in (lane.get("_blocked_machines") or [])}
        if got:
            seen.append({"snapshot": os.path.basename(p), "n": len(got)})
            ids |= got
    return sorted(ids), seen


def blacklist_counterfactual(offers, res, interruptible, excluded_ids, n_units=1, basis=None):
    """What the retired durable list WOULD have cost on this board, all other filters held."""
    basis = basis or _basis()
    preds = predicates(res)
    keep = survivors(offers, preds, list(preds))
    ex = {str(m) for m in excluded_ids}
    after = [o for o in keep if str(o.get("machine_id")) not in ex]
    ab, ap, arows = price_board(after, res, interruptible, n_units)
    bb, bp, brows = price_board(keep, res, interruptible, n_units)
    return {
        "n_retired_ids": len(ex),
        "surviving_without_blacklist": len(keep), "priceable_without_blacklist": bp,
        "surviving_with_blacklist": len(after), "priceable_with_blacklist": ap,
        "offers_it_would_remove": len(keep) - len(after),
        "best_usd_per_ns_without": (round(bb, 6) if bb else None),
        "best_usd_per_ns_with": (round(ab, 6) if ab else None),
        "ratio_vs_basis_without": (round(bb / basis, 3) if bb else None),
        "ratio_vs_basis_with": (round(ab / basis, 3) if ab else None),
        "usd_per_ns_penalty_pct": (round(100.0 * (ab - bb) / bb, 1) if (ab and bb and bb > 0) else None),
        "best_offer_without": (brows[0] if brows else None),
        "best_offer_with": (arows[0] if arows else None),
    }


# =============================================================================================================
# live read — ONE permissive query per tier
# =============================================================================================================
def permissive_query(interruptible, limit=3000):
    """As few server-side predicates as possible, so every filter can be counted client-side against the SAME
    list. `num_gpus` stays server-side only to keep multi-GPU rigs from swamping the page; it is still counted
    client-side, so its row is honest (it will read ~0 removed, which is the correct answer for a predicate
    the server already applied)."""
    return {"num_gpus": {"eq": 1}, "order": [["dph_total", "asc"]],
            "type": "bid" if interruptible else "on-demand", "limit": limit}


def live_offers(key, interruptible, limit=3000):
    from gpu_backend import _vast_request
    return _vast_request("GET", "/search/asks/", key, no_cache=True,
                         params={"q": json.dumps(permissive_query(interruptible, limit))}).get("offers", [])


# =============================================================================================================
# CLI
# =============================================================================================================
def _render(doc):
    L = []
    L.append("=" * 108)
    L.append("VAST FILTER ABLATION — how much board does each of OUR OWN filters remove?  (read-only, $0)")
    L.append("basis $/ns = %.6f   buy line = %.6f   n_units priced = %d"
             % (doc["basis_usd_per_ns"], doc["buy_line_usd_per_ns"], doc["n_units"]))
    L.append("=" * 108)
    for t in doc["tiers"]:
        f = t["full_spec"]
        L.append("")
        L.append("--- %s --- board read %d offers; FULL spec leaves %d (priceable %d), best %s/ns = %sx basis"
                 % (t["tier"], t["offers_returned"], f["surviving"], f["priceable"],
                    f["best_usd_per_ns"], f["ratio_vs_basis"]))
        L.append("    %-26s %-14s %8s %8s %10s  %s" %
                 ("filter", "bound", "alone", "LOO", "marginal", "LOO best $/ns (x basis)  gain%"))
        for r in t["per_filter"]:
            if r.get("caveat"):
                L.append("    " + "-" * 100)
            L.append("    %-26s %-14s %8d %8d %10d  %-12s %-8s %s"
                     % (r["filter"], r["bound"], r["alone_surviving"], r["leave_out_surviving"],
                        r["marginal_cost_offers"], r["leave_out_best_usd_per_ns"],
                        r["leave_out_ratio_vs_basis"],
                        ("+%s%%" % r["usd_per_ns_improvement_pct"]
                         if r["usd_per_ns_improvement_pct"] else "-")))
            if r.get("caveat"):
                for _ln in __import__("textwrap").wrap(r["caveat"], 96):
                    L.append("        " + _ln)
                L.append("    " + "-" * 100)
        bx = t.get("retired_blacklist")
        if bx:
            L.append("    RETIRED DURABLE BLACKLIST, counterfactual on THIS board (%d stored ids):"
                     % bx["n_retired_ids"])
            L.append("      offers surviving  WITHOUT it %4d (priceable %d, best %s = %sx basis)"
                     % (bx["surviving_without_blacklist"], bx["priceable_without_blacklist"],
                        bx["best_usd_per_ns_without"], bx["ratio_vs_basis_without"]))
            L.append("      offers surviving  WITH    it %4d (priceable %d, best %s = %sx basis)"
                     % (bx["surviving_with_blacklist"], bx["priceable_with_blacklist"],
                        bx["best_usd_per_ns_with"], bx["ratio_vs_basis_with"]))
            L.append("      it would remove %d offer(s); $/ns penalty %s"
                     % (bx["offers_it_would_remove"],
                        ("+%s%%" % bx["usd_per_ns_penalty_pct"]) if bx["usd_per_ns_penalty_pct"] else "none"))
        if t.get("cuda_sweep"):
            L.append("    CUDA floor swept (everything else held):")
            for r in t["cuda_sweep"]:
                bo = r.get("best_offer") or {}
                L.append("      min_cuda %-6s surviving %4d  priceable %4d  best %-10s %-7s  %s @ %s"
                         % (r["min_cuda"], r["surviving"], r["priceable"], r["best_usd_per_ns"],
                            ("%sx" % r["ratio_vs_basis"]), bo.get("gpu"), bo.get("price_usd_h")))
    L.append("")
    L.append("READ THIS THE RIGHT WAY: `marginal` is what the filter costs ON TOP OF the others, and `gain%` is")
    L.append("what dropping it would do to the achievable $/ns. A big `alone` loss with zero `marginal` is a")
    L.append("filter that is redundant, not a filter that is expensive. Nothing here changes a filter or a bid.")
    return "\n".join(L)


def _main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offers-bid", default="", help="raw offers JSON for the bid tier (omit => live)")
    ap.add_argument("--offers-ondemand", default="", help="raw offers JSON for the on-demand tier")
    ap.add_argument("--units", type=int, default=1, help="fleet size the $/ns mean is taken over")
    ap.add_argument("--min-ns-per-h", type=float, default=None,
                    help="card floor to include in the FULL spec (default: read TVAST_MIN_NS_PER_H)")
    ap.add_argument("--lane", default="ternary", choices=["ternary", "fanout"],
                    help="whose ResourceSpec to ablate")
    ap.add_argument("--no-ondemand", action="store_true", help="skip the uninterruptible tier")
    ap.add_argument("--json-out", default="vast-filter-ablation.json")
    a = ap.parse_args(argv)

    if a.lane == "fanout":
        from congeneric_fanout_vast import FANOUT_RES as res
        import copy
        res = copy.copy(res)
    else:
        from ternary_vast_launch import resource_spec
        res = resource_spec()
    if a.min_ns_per_h is not None:
        res.min_ns_per_h = a.min_ns_per_h
    # The exclusion set is a REAL filter and belongs in the study, but it is lane state rather than policy, so
    # it is reported with its size and never silently folded into another row.
    basis = _basis()
    bl_ids, bl_src = retired_blacklist_ids()
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    import vast_machine_blacklist as _vmb
    doc = {"_what": __doc__.split("\n")[0],
           "durable_exclusions_enabled": _vmb.durable_enabled(),
           "retired_blacklist_ids": bl_ids, "retired_blacklist_sources": bl_src,
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "lane": a.lane, "n_units": a.units,
           "spec": {"gpu": res.gpu, "min_vram_gb": res.min_vram_gb, "vcpus": res.vcpus,
                    "ram_gb": res.ram_gb, "disk_gb": res.disk_gb,
                    "min_reliability": res.min_reliability, "min_cuda": res.min_cuda,
                    "min_ns_per_h": res.min_ns_per_h,
                    "n_excluded_machines": len(res.exclude_machine_ids or ())},
           "basis_usd_per_ns": round(basis, 6),
           "buy_line_usd_per_ns": APPROVED_USD_PER_NS,
           "tiers": []}

    key = os.environ.get("VAST_API_KEY")
    plan = [(True, a.offers_bid)] + ([] if a.no_ondemand else [(False, a.offers_ondemand)])
    for interruptible, path in plan:
        if path:
            blob = json.load(open(path))
            offers = blob if isinstance(blob, list) else (blob.get("offers") or [])
        elif key:
            offers = live_offers(key, interruptible)
        else:
            print("no VAST_API_KEY and no --offers-*: nothing to ablate", file=sys.stderr)
            return 2
        t = ablate(offers, res, interruptible, n_units=a.units, basis=basis)
        # The RETIRED durable list, priced as a counterfactual on this same board — the number that says
        # whether removing it bought anything, rather than an assertion that it did.
        t["retired_blacklist"] = blacklist_counterfactual(offers, res, interruptible, bl_ids,
                                                          n_units=a.units, basis=basis)
        # The CUDA sweep is the point of the exercise, so run it on the tier the ladder is actually costed on.
        if interruptible:
            t["cuda_sweep"] = cuda_sweep(offers, res, interruptible, n_units=a.units, basis=basis)
        doc["tiers"].append(t)

    print(_render(doc))
    if a.json_out:
        with open(a.json_out, "w") as fh:
            json.dump(doc, fh, indent=1)
        print("\nwrote %s" % a.json_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
