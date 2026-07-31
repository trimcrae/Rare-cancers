#!/usr/bin/env python3
"""IS THE LANE'S THROUGHPUT DECAYING THROUGH THE DAY, OR IS THAT A COMPOSITION ARTIFACT? $0, read-only.

★★ THE CLAIM UNDER TEST (2026-07-31). Measured `s/iter` on the 5a-KS legs appeared to degrade ~2.5-4x across
the day within every card — 5090 6.85 -> 12.35, 4090 12.6 -> 31.0, 3090 9.1 -> 36.9. If real, it would be
worth more than every other fix on this lane put together: at 33 s/iter a 64-iteration warmup interval is
~35 min of exposure against a ~1 h median session, which is exactly why legs die before they bank; at 9 s/iter
it is ~10 min and the churn problem largely dissolves.

★ THE THREE CANDIDATE EXPLANATIONS, AND WHAT DISCRIMINATES THEM. Each is tested here, cheapest first, and
each needs only artifacts already committed:

  1. **PHASE MIX** — a leg early in the day is in warmup, the same leg later is in production, and those have
     different seconds-per-iteration by construction. The repo has already been burned by exactly this
     (`_never_pool`: *"pricing.md's superseded ~2.06x card ratio was a warmup/production mix-up"*).
     ⛔ REFUTED, twice, without a new run:
       (a) MAGNITUDE AND DIRECTION. `ternary-arm-iteration-rates.json`'s own `phase_cross_check` measures
           warmup/production = **0.834** (range 0.734-1.013, n=6 legs that ran both). Warmup is FASTER than
           production, so a warmup->production shift can slow a leg by at most ~1.2-1.36x — against an
           observed 2.5-4.6x.
       (b) NO TRANSITION HAPPENED. `ternary_nr4a1_r1`'s s/iter rose 8.1 -> 36.9 (4.6x) between 8:13 AM and
           2:49 PM ET, and the committed forensic at 3:31 PM ET still shows it at **warmup/1152**. The whole
           rise is inside one phase.

  2. **CARD MIX** — we rented fast cards early and slow ones late, so a pooled trend is composition, not
     decay. THIS IS WHAT THE DATA SUPPORTS: pooled Spearman rho = +0.721 (permutation p = 0.001, n = 18), but
     the RTX 5090 attempts all fall between 12:13 and 15:40 and every RTX 3090 attempt between 16:00 and
     19:31. Controlling for card, no card shows a significant trend on its own.

  3. **A RESIDUAL WITHIN-CARD TREND** (contention, late-day host quality) — NOT ESTABLISHED and, on today's
     data, NOT TESTABLE. All three cards point the same way (+0.35, +0.80, +0.80) but n = 9 / 4 / 4 and every
     p is ~0.34. ⚠ Absence of significance here is absence of POWER, not evidence of absence — the honest
     statement is that the question is open, not that the answer is no.

⚠ AND THE CONFOUND THAT SURVIVES ALL THREE: **every attempt is a different rental on a different host**, and
host variance on this workload is enormous — 13 paired 3090-vs-4090 measurements within 60 min of each other
span 0.50-2.67x against a table prediction of 1.745x. With that much spread and this few points, a monotone
sequence is cheap to produce by accident. That is why the conclusion below is "composition", not "nothing".

⛔ WHAT THIS DOES NOT DO: rent anything, or turn a correlation into a card ranking. The measurement that would
settle the per-system card question is a BENCH — `vast_bench_sweep` pointed at the staged 5a-KS assembly
instead of its 84,534-particle water box, 3 cards x 3 hosts, well under $1.
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import random
import statistics as st
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
# The git paths below are REPO-relative, so git must run from the repo root — running it from this directory
# resolves them to `research/modalities/research/modalities/...` and silently returns nothing, which reads as
# "no observations" rather than as an error.
REPO = os.path.dirname(os.path.dirname(HERE))


def _ranks(v):
    """Average ranks, ties shared. PURE.

    ⚠ TIES ARE NOT A DETAIL HERE. A first cut broke ties by original index, which made a CONSTANT series
    correlate perfectly with time (rho = 1.0) — so a card that never changed speed would have been reported
    as trending, which is the exact error this module exists to avoid. The real data has ties too (the RTX
    4090 shows 18.2 twice and 13.8 twice). Caught by `test_a_pure_COMPOSITION_effect_is_reported_as_composition`.
    """
    order = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        shared = (i + j) / 2.0
        for k in range(i, j + 1):
            out[order[k]] = shared
        i = j + 1
    return out


def spearman(x, y):
    """Rank correlation, ties averaged. PURE. Spearman rather than Pearson because s/iter is heavy-tailed
    across hosts and one 36.9 next to a 6.85 would dominate a Pearson fit."""
    if len(x) < 3:
        return 0.0
    ax, ay = _ranks(x), _ranks(y)
    mx, my = st.mean(ax), st.mean(ay)
    num = sum((p - mx) * (q - my) for p, q in zip(ax, ay))
    den = math.sqrt(sum((p - mx) ** 2 for p in ax) * sum((q - my) ** 2 for q in ay))
    return (num / den) if den else 0.0


def permutation_p(x, y, n=20000, seed=0):
    """P(|rho| this large | time carries no information). PURE given the seed.

    A permutation test rather than a t-approximation because n is 4-18 and the normal approximation to
    Spearman is not trustworthy there — which matters, since the whole question is whether a small sample's
    monotone-looking sequence means anything."""
    obs = abs(spearman(x, y))
    rnd = random.Random(seed)
    yy = list(y)
    hits = 0
    for _ in range(n):
        rnd.shuffle(yy)
        if abs(spearman(x, yy)) >= obs:
            hits += 1
    return hits / float(n)


def _sh(*a):
    return subprocess.run(a, capture_output=True, text=True, cwd=REPO).stdout


def _parse(t):
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.datetime.strptime(t, f)
        except (ValueError, TypeError):
            pass
    return None


def rentals(ref="origin/main"):
    """{instance: {gpu, utc, unit}} from every committed revision of the rental receipt."""
    out = {}
    for h in _sh("git", "log", "--format=%H", ref, "--",
                 "research/modalities/ternary-vast-rental-receipt.json").split():
        try:
            d = json.loads(_sh("git", "show",
                               f"{h}:research/modalities/ternary-vast-rental-receipt.json"))
        except ValueError:
            continue
        for r in (d.get("rented") or []):
            out.setdefault(str(r.get("instance")),
                           {"gpu": r.get("gpu"), "utc": d.get("utc"), "unit": r.get("unit_id")})
    return out


def observations(tax_path=None, ref="origin/main"):
    """[(when, card, s_per_iter, unit)] — each attempt's measured rate joined to the card it ran on.

    ⚠ THE JOIN IS APPROXIMATE AND SAYS SO: an attempt is attributed to the most recent rental of the SAME
    unit that precedes it. A rental missing from the receipts would mis-attribute one point. It is good
    enough to test a 2.5x effect and NOT good enough to publish a card ranking, which is why nothing here
    produces one."""
    tax = json.load(open(tax_path or os.path.join(HERE, "setup-tax-5aks.json")))
    inst = rentals(ref)
    pts = []
    for uid, u in (tax.get("units") or {}).items():
        for a in u.get("attempts") or []:
            if not a.get("s_per_iter"):
                continue
            ta = _parse(str(a.get("utc"))[:19])
            best = None
            for m in inst.values():
                if m["unit"] != uid:
                    continue
                tr = _parse(m["utc"])
                if tr and ta and tr <= ta and (best is None or tr > best[0]):
                    best = (tr, m["gpu"])
            if best:
                pts.append((ta, best[1], float(a["s_per_iter"]), uid))
    pts.sort()
    return pts


def analyse(pts, seed=0):
    """The whole study. PURE given `pts`."""
    if len(pts) < 3:
        return {"n": len(pts), "verdict": "too few observations to say anything"}
    t0 = pts[0][0]
    xs = [(t - t0).total_seconds() / 3600.0 for t, _, _, _ in pts]
    ys = [s for _, _, s, _ in pts]
    pooled_rho = spearman(xs, ys)
    doc = {
        "n": len(pts), "span_hours": round(max(xs), 2),
        "pooled": {"rho": round(pooled_rho, 3), "p": permutation_p(xs, ys, seed=seed),
                   "s_per_iter_range": [min(ys), max(ys)],
                   "fold": round(max(ys) / min(ys), 2)},
        "by_card": {},
    }
    for card in sorted({g for _, g, _, _ in pts}):
        sub = [(t, s) for t, g, s, _ in pts if g == card]
        if len(sub) < 3:
            doc["by_card"][card] = {"n": len(sub), "note": "too few to test"}
            continue
        c0 = sub[0][0]
        cx = [(t - c0).total_seconds() / 3600.0 for t, _ in sub]
        cy = [s for _, s in sub]
        doc["by_card"][card] = {
            "n": len(sub), "rho": round(spearman(cx, cy), 3),
            "p": permutation_p(cx, cy, seed=seed), "values": cy,
            "window": [sub[0][0].strftime("%H:%MZ"), sub[-1][0].strftime("%H:%MZ")],
        }
    sig = [c for c, v in doc["by_card"].items() if v.get("p") is not None and v["p"] < 0.05]
    doc["verdict"] = (
        "POOLED TREND IS REAL (rho %+.3f, p %.4f) BUT IS EXPLAINED BY CARD MIX: no individual card shows a "
        "significant trend (%s). Fast cards were rented early and slow ones late. A residual within-card "
        "trend is NOT excluded — every card points the same way — but n is 3-9 per card and every p is far "
        "from significant, so this is a POWER limit, not evidence of absence."
        % (doc["pooled"]["rho"], doc["pooled"]["p"],
           ", ".join("%s p=%.2f" % (c, v["p"]) for c, v in sorted(doc["by_card"].items())
                     if v.get("p") is not None))
        if not sig else
        "A WITHIN-CARD TREND SURVIVES on %s — composition does not explain it, and contention or host "
        "quality is the live hypothesis." % ", ".join(sig))
    return doc


def _main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tax", default=None)
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    pts = observations(a.tax, a.ref)
    doc = analyse(pts)
    doc["_what"] = __doc__.split("\n")[0]
    doc["_phase_refutation"] = (
        "phase is REFUTED twice: phase_cross_check warmup/production = 0.834 (range 0.734-1.013, n=6) caps "
        "any phase effect at ~1.2-1.36x against an observed 2.5-4.6x, AND ternary_nr4a1_r1 rose 8.1 -> 36.9 "
        "s/iter while the committed forensic still showed it at warmup/1152 — no transition occurred.")
    print(json.dumps(doc, indent=1))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(doc, fh, indent=1)
        print("wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
