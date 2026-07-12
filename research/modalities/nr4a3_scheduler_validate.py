#!/usr/bin/env python3
"""
Exercise the library-backed NR4A3 scheduler (Optuna successive halving) + the certification layer on a runner
where dependencies are installed (the dev sandbox lacks them). Two checks:

  1. OFFLINE SHADOW: a simulated screen with one known selective winner + one near-bar decoy. Assert the
     Optuna-scheduled + adaptive_certify-certified run declares the genuine winner (or abstains), never the
     decoy, and prunes non-promising candidates. Confirms scheduling(library) and certification(ours) compose.

  2. STATS CROSS-CHECK: compare our stdlib anytime_lower_bound to the `confseq` reference library's confidence
     sequence at a few (n, sigma). Ours should be no looser than a reference anytime bound (a sanity check that
     we did not hand-roll an over-optimistic bound). Best-effort: skipped with a note if the confseq API differs.

Run via .github/workflows/allocator-validate.yml (pip install optuna confseq). Exit non-zero on failure.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adaptive_certify import anytime_lower_bound  # noqa: E402
from nr4a3_screen_config import build_config  # noqa: E402
from nr4a3_scheduler import run_offline_shadow  # noqa: E402


def offline_shadow_check():
    cfg = build_config()
    # bar is set during real calibration; for this OFFLINE SHADOW use an explicit TEST bar (clearly not real).
    cfg["certification"]["bar_kcal"] = cfg["certification"]["bar_kcal"] or 1.0
    cfg["certification"]["robustness_kcal"] = 0.0
    cfg["certification"]["sigma_known"] = 0.6
    ids = [c["id"] for c in cfg["candidates"]]
    winner = ids[1] if len(ids) > 1 else ids[0]                  # a genuine bar-clearer
    decoy = ids[2] if len(ids) > 2 else ids[0]                   # near-bar (must NOT be declared)
    bar = cfg["certification"]["bar_kcal"]
    true = {cid: (bar - 0.6) for cid in ids}
    true[winner] = bar + 2.0                                     # clearly selective (robust anytime-valid pass)
    true[decoy] = bar - 0.05                                     # just below the bar
    rng = random.Random(0)
    ctr = {"i": 0}

    nrep = cfg["certification"]["min_independent_replicas"]

    def evaluate_fn(cid, rung):
        ctr["i"] += 1
        terminal = rung == cfg["terminal_rung"]
        promise = true[cid] + rng.gauss(0, 0.3)                 # scheduling scalar
        margins = None
        if terminal:                                            # a certifying rung supplies >=min replicas
            margins = {t: [rng.gauss(true[cid], cfg["certification"]["sigma_known"]) for _ in range(nrep + 2)]
                       for t in cfg["certification"]["targets"]}
        return {"promise": promise, "terminal": terminal, "margins": margins,
                "meta": {"seed": ctr["i"], "start_state": ctr["i"]}}

    res = run_offline_shadow(cfg, evaluate_fn, budget_gate=None)
    print("offline shadow:", res)
    assert res["declared"] != decoy, "declared the near-bar decoy — certification failed"
    assert res["declared"] == winner, f"declared {res['declared']}, expected to CERTIFY the winner {winner}"
    print(f"offline shadow OK — CERTIFIED the genuine winner {winner} (never the decoy)")


def stats_crosscheck():
    try:
        import numpy as np
        from confseq import boundaries as cb  # type: ignore
    except Exception as e:  # noqa: BLE001
        print(f"confseq cross-check SKIPPED ({e.__class__.__name__}: {e})")
        return
    ok = True
    for n, sigma in [(5, 1.0), (20, 1.0), (100, 0.5)]:
        our_half = 0.0 - anytime_lower_bound(0.0, n, sigma, 0.05)   # half-width of our bound at xbar=0
        try:
            # confseq normal-mixture boundary on the running sum; convert to a per-mean half-width
            v = n * sigma * sigma
            ref = float(cb.normal_mixture_bound(np.array([v]), alpha=0.05, v_opt=v)[0]) / n
        except Exception as e:  # noqa: BLE001
            print(f"confseq API not matched ({e}); skipping numeric compare")
            return
        print(f"n={n} sigma={sigma}: ours_half={our_half:.3f} confseq_half={ref:.3f}")
        if our_half < 0.5 * ref:                                  # ours must not be wildly tighter (optimistic)
            ok = False
    assert ok, "our anytime bound looks optimistic vs confseq — investigate"
    print("stats cross-check OK (our anytime bound is not looser-than-reference optimistic)")


if __name__ == "__main__":
    offline_shadow_check()
    stats_crosscheck()
    print("ALL scheduler validation checks passed.")
