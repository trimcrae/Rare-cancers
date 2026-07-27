#!/usr/bin/env python3
"""CAN WE HARVEST A CARD'S THROUGHPUT FROM WORK WE HAVE ALREADY PAID FOR? — the evaluation, and what survives.

★ THE IDEA, WHICH IS A GOOD ONE AND WORTH THE $0 IT COSTS TO TEST. We rent GPUs every day. Every production
leg measures its own throughput as a side effect: the commit store records `iter-XXXXXXXX` boundaries with S3
timestamps, the instance record carries the GPU model, and `$/hr` is known. So a throughput observation might
be recoverable retrospectively and prospectively, for free, from rentals already bought — and a table that
grows on its own with every rental is strictly better than any one-off sweep.

This module implements the harvest, and reports what it can and cannot support. **The headline is that it
CANNOT fill `MEASURED_NS_PER_DAY_84K`, for three independent reasons, each measured rather than argued.**

===============================================================================================================
REASON 1 — THE SELECTION LOOP IS CLOSED. Harvesting is structurally blind to exactly the cards we need.
===============================================================================================================
    an unbenched card has no `$/ns`
      -> `gpu_backend.rank_offers_by_usd_per_ns` sorts it AFTER every benched offer
      -> `_select_cheapest_offer` returns `measured[0]` whenever anything benched qualifies
      -> we never rent it -> it never produces a log -> it stays unbenched

MEASURED, from the committed progress trail — and it is REGENERATED, never quoted from here, by `--census`:
at 2026-07-27 8:40 AM ET the trail held 114 instance-observations across 55 fan-out ticks (2026-07-24 onward)
containing exactly THREE distinct card models — RTX 4090, RTX 4080S, RTX 3090 — **every one of them already in
the table**, while `vast-board-census.json` lists 20+ models on the same board. The harvest can only ever
re-measure what we can already price. Nothing in the data is an accident: it is what the ranking is *for*.

===============================================================================================================
REASON 2 — A LEG RATE IS A DIFFERENT QUANTITY FROM THE BENCH, AND THE GAP IS LARGE
===============================================================================================================
The table is ns/day for ONE replica of an 84,534-particle plain-MD water box. A step-1 leg is an OpenFE
`RelativeHybridTopologyProtocol` HREX sampler: **12 lambda windows**, 2.5 ps per iteration per window, on the
cmpd19/NR4A3 hybrid complex, with per-iteration replica exchange (which evaluates every state's energy), MBAR
bookkeeping and checkpoint I/O.

Harvested here (RTX 4080S, instance 45951628, complex/production, a 3.4 h unbroken span at 86-100 % `gpu_util`,
quantization bound +/-14 %): **~165 iterations/hour**, i.e. ~119 ns/day of aggregate replica-time — which
`--rates` prints as a percentage of that card's benched constant, and it is **under a fifth of it**. That
shortfall is a property of the HREX protocol and the system (12 states' energies evaluated every iteration,
replica exchange, MBAR bookkeeping, checkpoint I/O), not of the card. Feeding it into the same column would not
be a noisy measurement of the table's quantity; it would be a different quantity wearing the same units.

===============================================================================================================
REASON 3 — THE RATIO ESCAPE HATCH IS REAL BUT UNPOPULATED, AND IT IS CONFOUNDED
===============================================================================================================
The one comparison that survives a system-size change is a RATIO: the same leg type, same phase, on two
different cards. System size, window count and protocol overhead all cancel, and a ratio is all the ranking
needs (`ns_day(X) = ns_day(reference) x rate(X)/rate(reference)`). `ratio_observations()` implements exactly
that and is the honest version of this idea.

Two things stop it from being the answer today:

  * **It is empty.** Across all 53 committed ticks there is not ONE (unit, leg, phase) that ran on two
    different cards — the terminus gate deliberately keeps a single unit alive, so cross-card pairs never
    arise. `--ratios` reports 0 pairs, and will report more as the fleet widens.
  * **It is confounded, in the direction that BUYS.** pricing.md A.1 measured four legs where realised ns/day
    tracked `gpu_util` rather than the card, with two RTX 4080S legs landing **1.8-3.0x below** what the
    benched card ratio predicts — root-caused to PLUMED's CPU-side bias on a weak host, i.e. the HOST, not the
    card. A harvested ratio therefore mixes card throughput with host quality, and if the reference-side
    observation happens to be the starved one the ratio comes out TOO HIGH — which would make a card look
    cheaper per ns than it is and lure a rental in. That is the one error direction the repo refuses.

===============================================================================================================
SO WHAT DOES SURVIVE, AND IS WORTH KEEPING
===============================================================================================================
1. **A LOWER BOUND, labelled as one.** Every confounder above (co-tenancy, weak host CPU, checkpoint I/O,
   startup, protocol overhead) can only make a realised rate LOWER than the card's capability. So a harvested
   figure bounds throughput from below, which is the bound you need to rule a card IN
   (`vast_board_census`'s rule-in/rule-out split). It is never a table entry.
2. **A FALSIFICATION MONITOR, for free, forever.** A lower bound that EXCEEDS the constant is a contradiction:
   it would mean the table understates the card. `falsifications()` checks every observation against the
   constant, on the RATIO axis where the comparison is legitimate, and says so if one ever fires.
3. **A COVERAGE CENSUS.** `--census` is the standing evidence for reason 1 — if a future board ever lands a
   production leg on an unbenched card, the census sees it the next tick and that card becomes harvestable.

Everything here reads the COMMITTED progress trail (`step1-fanout-progress.json` through git history), so it
needs no AWS key, no Vast key and no network: it costs nothing and can be re-run at any time.

    python3 throughput_harvest.py --census      # which cards have ever run a real leg
    python3 throughput_harvest.py --rates       # realised iteration rates per card (LOWER BOUNDS)
    python3 throughput_harvest.py --ratios      # cross-card pairs on the same (unit, leg, phase)
    python3 throughput_harvest.py --json out.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vast_cost_model as _vcm  # noqa: E402

PROGRESS_FILE = "research/modalities/step1-fanout-progress.json"

# The step-1 lane's protocol, imported in spirit from `nr4a3_rbfe.py` (12 windows; iterations are MC-move
# boundaries of 625 steps x 4 fs = 2.5 ps). Kept here as named constants so the conversion below is auditable
# rather than a magic number, and so a lane with a different window count can pass its own.
DEFAULT_N_WINDOWS = 12
PS_PER_ITERATION_PER_WINDOW = 2.5

# `congeneric_fanout_vast` encodes (leg, phase, iteration) into one monotone scalar. Decoding it here rather
# than importing keeps this module free of that lane's S3/Vast imports; the strides are asserted against the
# source in tests/test_throughput_harvest.py so they cannot drift apart silently.
_PHASE_STRIDE = 1_000_000
_LEG_STRIDE = 10_000_000
_LEG_NAMES = {0: "complex", 1: "solvent"}
_PHASE_NAMES = {0: "warmup", 1: "production"}

# A gap longer than this between two consecutive committed ticks breaks the chain: the fleet may have been
# stopped, relaunched or preempted inside it, and the instance list only tells us the endpoints.
MAX_GAP_H = 1.5

# ★★ THE QUANTIZATION BOUND — the defect that made this module's FIRST answer wrong, kept as the fix.
#
# The progress artifact records the FURTHEST COMMITTED iteration, and a leg commits only every 20 (warmup) or
# 40 (production) iterations. So a snapshot at time t observes a boundary that was crossed at some UNKNOWN
# earlier moment. Over a window containing few boundaries that unknown dominates:
#
#     observed rate = d_iter / dt        true elapsed for those d_iter can be up to dt + 2 x (stride / rate)
#
# i.e. the observed rate can OVERSTATE the true one, and the relative error is bounded by ~2 x stride / d_iter.
#
# MEASURED, and it is not a small effect — this module's FIRST answer was wrong because of it. Reading
# consecutive ticks pairwise gave an RTX 4090 warmup rate of 344.5 iter/h from a 0.06 h window containing
# exactly ONE 20-iteration boundary, against 139.5 iter/h over the same instance's full 0.72 h / 100-iteration
# span — a 2.5x inflation from commit granularity alone. That single number then "falsified" the benched
# RTX 4090 : RTX 4080 ratio, reporting a realised ratio ~46 % above what the table predicts. **A harvest that
# can manufacture a contradiction of the anchor table is worse than no harvest**, so rates are taken over the
# LONGEST unbroken span per (instance, leg, phase), every observation carries `quant_err`, and anything past
# MAX_QUANT_ERR is dropped rather than reported. With the fix the spurious falsification disappears.
MAX_QUANT_ERR = 0.25
MIN_SPAN_H = 0.25


# =============================================================================================================
# PURE — decode, attribute, and rate
# =============================================================================================================
def decode_scalar(scalar):
    """(leg, phase, iteration) from the committed-progress scalar. PURE."""
    try:
        s = int(scalar)
    except (TypeError, ValueError):
        return None, None, None
    if s < 0:
        return None, None, None
    leg = _LEG_NAMES.get(s // _LEG_STRIDE)
    phase = _PHASE_NAMES.get((s % _LEG_STRIDE) // _PHASE_STRIDE)
    return leg, phase, s % _PHASE_STRIDE


def unit_of_label(label, unit_ids):
    """The unit a Vast instance label belongs to, or None if it is ambiguous. PURE.

    Labels are `s1f-<idx>-<ligand_b>`; the ligand fragment is what identifies the unit. AMBIGUITY IS FATAL,
    not something to break ties on: attributing an interval to the wrong unit invents a rate out of two
    unrelated numbers, and there is no downstream check that would catch it."""
    lab = str(label or "")
    parts = lab.split("-", 2)
    frag = parts[2] if len(parts) >= 3 else lab
    if not frag:
        return None
    hits = [u for u in unit_ids if frag in u]
    return hits[0] if len(hits) == 1 else None


def _chains(snapshots):
    """PURE: [(key, [(t, iteration), ...])] — the unbroken observation chains in the trail.

    A chain is one (instance, card, unit, leg, phase) observed across consecutive snapshots with no gap longer
    than MAX_GAP_H and no phase change. Breaking on the phase matters: the iteration counter RESTARTS at each
    phase, so a span that straddles a boundary computes a difference between two unrelated counters."""
    seq = {}
    for t, d in snapshots:
        units = {u.get("unit_id"): u for u in d.get("units", [])}
        for i in d.get("instances", []):
            uid = unit_of_label(i.get("label"), units.keys())
            if uid is None:
                continue
            leg, phase, it = decode_scalar(units[uid].get("committed_scalar"))
            if leg is None or it is None:
                continue
            key = (i.get("id"), i.get("gpu"), uid, leg, phase)
            seq.setdefault(key, []).append((t, it, i))
    out = []
    for key, pts in seq.items():
        pts.sort(key=lambda p: p[0])
        chain = [pts[0]]
        for prev, cur in zip(pts, pts[1:]):
            if (cur[0] - prev[0]).total_seconds() / 3600.0 > MAX_GAP_H:
                out.append((key, chain))
                chain = [cur]
            else:
                chain.append(cur)
        out.append((key, chain))
    return out


def rate_observations(snapshots, n_windows=DEFAULT_N_WINDOWS, max_quant_err=MAX_QUANT_ERR):
    """PURE: realised per-card rates over the LONGEST unbroken span per (instance, leg, phase).

    Span-based, NOT pairwise, and that is the whole point — see the MAX_QUANT_ERR comment above. Each
    observation carries:

      * `stride`      — the commit granularity inferred from the chain's own smallest positive advance;
      * `quant_err`   — ~2 x stride / d_iter, the bound on how much the rate can be OVERSTATED by not knowing
                        when each committed boundary was actually crossed;
      * `iter_per_h`  — the rate, and `ns_per_day_at_leg_size`, explicitly named for the LEG's system because
                        it is NOT the table's quantity (module docstring, reason 2).

    Observations whose `quant_err` exceeds `max_quant_err` are dropped: a rate that could be 40 % high is not a
    lower bound on anything, and it is exactly what manufactured a false falsification of the table."""
    out = []
    for (iid, card, uid, leg, phase), chain in _chains(snapshots):
        if len(chain) < 2:
            continue
        t0, it0, _i0 = chain[0]
        t1, it1, i1 = chain[-1]
        dt_h = (t1 - t0).total_seconds() / 3600.0
        d_iter = it1 - it0
        if dt_h < MIN_SPAN_H or d_iter <= 0:
            continue
        strides = [b[1] - a[1] for a, b in zip(chain, chain[1:]) if b[1] > a[1]]
        stride = min(strides) if strides else d_iter
        quant = 2.0 * stride / float(d_iter)
        if quant > max_quant_err:
            continue
        iph = d_iter / dt_h
        utils = [p[2].get("gpu_util") for p in chain if p[2].get("gpu_util") is not None]
        out.append({
            "utc_start": t0.isoformat(), "utc_end": t1.isoformat(), "instance": iid, "card": card,
            "unit": uid, "leg": leg, "phase": phase, "span_h": round(dt_h, 3), "n_snapshots": len(chain),
            "d_iter": d_iter, "stride": stride, "quant_err": round(quant, 4),
            "iter_per_h": round(iph, 2),
            "ns_per_day_at_leg_size": round(iph * n_windows * PS_PER_ITERATION_PER_WINDOW * 24 / 1000.0, 2),
            "gpu_util_min": (min(utils) if utils else None), "gpu_util_max": (max(utils) if utils else None),
            "usd_per_h": i1.get("dph"),
            "_quantity": "AGGREGATE replica-ns/day for a 12-window HREX leg at the cmpd19/NR4A3 complex "
                         "size. NOT the 84,534-particle single-replica quantity in "
                         "MEASURED_NS_PER_DAY_84K, and not convertible to it without a benched ratio.",
        })
    return sorted(out, key=lambda o: (str(o["card"]), o["leg"], o["phase"], -o["iter_per_h"]))


def best_per_card(observations):
    """PURE: the LOWER BOUND per card — the best realised rate seen, since every confounder pushes down.

    The MAX, not the mean. A mean over hosts of differing quality estimates 'the typical host we happened to
    rent', which is not a property of the card; the max is the closest approach to the card's capability that
    the data can support, and it is still only a lower bound."""
    best = {}
    for o in observations:
        card = o.get("card")
        if not card:
            continue
        k = (card, o.get("leg"), o.get("phase"))
        if k not in best or o["iter_per_h"] > best[k]["iter_per_h"]:
            best[k] = o
    return best


def ratio_observations(observations):
    """PURE: cross-card pairs on the SAME (leg, phase) — the only comparison that survives a system-size change.

    Returns [(card_a, card_b, ratio, a_obs, b_obs)] with `ratio = rate(a)/rate(b)`, ordered so `b` is the
    benched reference when one of the two is. A ratio cancels particle count, window count and protocol
    overhead, so `ns_day(a) = ns_day(b) x ratio` is dimensionally legitimate — which is why this is the ONLY
    harvest path that could ever produce a table entry, and why it needs the pair to exist."""
    best = best_per_card(observations)
    by_lp = {}
    for (card, leg, phase), o in best.items():
        by_lp.setdefault((leg, phase), []).append((card, o))
    pairs = []
    for (leg, phase), rows in sorted(by_lp.items()):
        for i in range(len(rows)):
            for j in range(len(rows)):
                if i == j:
                    continue
                ca, oa = rows[i]
                cb, ob = rows[j]
                if _vcm.card_of(cb) is None or _vcm.card_of(ca) == _vcm.card_of(cb):
                    continue                       # b must be a card we can anchor on, and not the same card
                if ob["iter_per_h"] <= 0:
                    continue
                pairs.append({"leg": leg, "phase": phase, "card_a": ca, "card_b": cb,
                              "ratio": round(oa["iter_per_h"] / ob["iter_per_h"], 4),
                              "a": oa, "b": ob})
    return pairs


def falsifications(pairs):
    """PURE: harvested ratios that CONTRADICT the benched table.

    A realised ratio is confounded downward on BOTH sides, so it cannot be compared to the benched ratio in
    general. What it CAN do is falsify: if card A's realised rate exceeds card B's by more than the benched
    table says is possible, and B's observation is healthy, then the table understates A relative to B. Only
    that direction is reported — an under-shoot is the expected, uninformative case."""
    out = []
    for p in pairs:
        a_card, b_card = _vcm.card_of(p["card_a"]), _vcm.card_of(p["card_b"])
        if a_card is None or b_card is None:
            continue
        expected = _vcm.MEASURED_NS_PER_DAY_84K[a_card] / _vcm.MEASURED_NS_PER_DAY_84K[b_card]
        if p["ratio"] > expected * 1.10:
            out.append({**p, "expected_ratio": round(expected, 4),
                        "verdict": f"realised {p['card_a']}/{p['card_b']} = {p['ratio']:.3f} exceeds the "
                                   f"benched {expected:.3f} by >10% — the TABLE is the suspect, not the host"})
    return out


def coverage(observations, snapshots):
    """PURE: the standing evidence for the selection-loop argument."""
    cards = {}
    for _t, d in snapshots:
        for i in d.get("instances", []):
            c = i.get("gpu")
            if c:
                cards[c] = cards.get(c, 0) + 1
    rows = []
    for c, n in sorted(cards.items(), key=lambda kv: -kv[1]):
        prov, base, _note = _vcm.throughput_provenance(c)
        rows.append({"card": c, "instance_observations": n, "throughput_provenance": prov,
                     "resolves_to": base})
    return {"n_snapshots": len(snapshots),
            "n_instance_observations": sum(cards.values()),
            "distinct_cards": len(cards),
            "n_already_benched": sum(1 for r in rows if r["throughput_provenance"] != "unbenched"),
            "n_new_cards": sum(1 for r in rows if r["throughput_provenance"] == "unbenched"),
            "n_rate_intervals": len(observations),
            "cards": rows}


# =============================================================================================================
# the git-history reader — no keys, no network, $0
# =============================================================================================================
def _sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


def is_shallow():
    """True when this checkout has no history to read. PURE-ish (one git call).

    ⛔ WHY THIS IS NOT A DETAIL. `actions/checkout` clones at depth 1 by default, so in CI `git log` over the
    progress artifact returns NOTHING and every number here comes back zero — which reads exactly like
    'no production leg has ever run on an unbenched card', the very conclusion this module exists to support.
    A silent zero that agrees with your hypothesis is the worst possible failure. Observed 2026-07-27: the
    first CI run of the census reported 0 snapshots, 0 cards, 0 spans, and looked entirely plausible.
    The fix is `fetch-depth: 0` on the checkout; this function is the alarm for when it is missing."""
    return _sh("git rev-parse --is-shallow-repository").strip() == "true"


def load_snapshots(path=PROGRESS_FILE, all_refs=True):
    """Every committed version of the progress artifact, oldest first. Reads git only."""
    refs = "--all " if all_refs else ""
    log = _sh(f"git log --reverse {refs}--format='%H %cI' -- {path}").strip()
    if not log.strip() and is_shallow():
        raise RuntimeError(
            "SHALLOW CHECKOUT: git history is absent, so the harvest would report zero of everything and "
            "that zero would look like a finding. Re-run with `fetch-depth: 0` on actions/checkout.")
    out = []
    for line in log.split("\n"):
        if not line.strip():
            continue
        h, _, t = line.partition(" ")
        raw = _sh(f"git show {h}:{path}")
        if not raw.strip():
            continue
        try:
            out.append((datetime.fromisoformat(t.strip()), json.loads(raw)))
        except ValueError:
            continue
    out.sort(key=lambda x: x[0])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--rates", action="store_true")
    ap.add_argument("--ratios", action="store_true")
    ap.add_argument("--json", default=None)
    ap.add_argument("--progress-file", default=PROGRESS_FILE)
    a = ap.parse_args(argv)
    show_all = not (a.census or a.rates or a.ratios)

    snaps = load_snapshots(a.progress_file)
    obs = rate_observations(snaps)
    cov = coverage(obs, snaps)
    pairs = ratio_observations(obs)
    fals = falsifications(pairs)

    if a.census or show_all:
        print(f"=== COVERAGE CENSUS — {cov['n_snapshots']} committed snapshots, "
              f"{cov['n_instance_observations']} instance-observations ===")
        for r in cov["cards"]:
            print(f"  {r['card']:<14} n={r['instance_observations']:<4} "
                  f"{r['throughput_provenance']}"
                  + (f" -> {r['resolves_to']}" if r["resolves_to"] else ""))
        print(f"  distinct cards {cov['distinct_cards']}; already benched "
              f"{cov['n_already_benched']}; NEW {cov['n_new_cards']}")
        if cov["n_new_cards"] == 0:
            print("  ** THE SELECTION LOOP IS CLOSED: every card a production leg has ever landed on was "
                  "already in the table. Harvesting cannot widen it. **")

    if a.rates or show_all:
        print(f"\n=== REALISED RATES ({len(obs)} spans past the quantization gate) — "
              f"LOWER BOUNDS, never table entries ===")
        for (card, leg, phase), o in sorted(best_per_card(obs).items()):
            prov, base, _n = _vcm.throughput_provenance(card)
            tab = _vcm.MEASURED_NS_PER_DAY_84K.get(base or "")
            frac = "" if not tab else f"  = {o['ns_per_day_at_leg_size'] / tab * 100:.0f}% of the {base} " \
                                      f"constant ({tab} ns/day) — DIFFERENT QUANTITY, not a discrepancy"
            print(f"  {card:<14} {leg}/{phase:<11} best {o['iter_per_h']:.1f} iter/h "
                  f"(span {o['span_h']:.2f} h, {o['d_iter']} iters, +/-{o['quant_err'] * 100:.0f}% quant) -> "
                  f"{o['ns_per_day_at_leg_size']:.1f} aggregate ns/day at the leg's size{frac}")

    if a.ratios or show_all:
        print(f"\n=== CROSS-CARD RATIOS ({len(pairs)} pair(s)) — the only harvest path to a table entry ===")
        if not pairs:
            print("  none: no (leg, phase) has run on two different cards in the committed trail.")
            print("  The terminus gate keeps ONE unit alive, so cross-card pairs do not arise. This is the "
                  "reason a dedicated calibration rental (vast_bench_sweep.py) is the only route today.")
        for p in pairs:
            print(f"  {p['leg']}/{p['phase']}: {p['card_a']}/{p['card_b']} = {p['ratio']:.3f}")
        if fals:
            print("  ** FALSIFICATION — a harvested ratio contradicts the benched table: **")
            for f in fals:
                print("   " + f["verdict"])
        elif pairs:
            print("  no falsification: every harvested ratio is at or below what the table predicts, which is "
                  "the expected direction (realised <= capability).")

    if a.json:
        with open(a.json, "w") as f:
            json.dump({"coverage": cov, "observations": obs, "ratios": pairs,
                       "falsifications": fals,
                       "_claim_ceiling": "Realised rates are LOWER BOUNDS on card throughput for a 12-window "
                                         "HREX leg, not measurements of the 84,534-particle single-replica "
                                         "quantity in vast_cost_model.MEASURED_NS_PER_DAY_84K. Nothing here "
                                         "may enter that table."}, f, indent=2)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
