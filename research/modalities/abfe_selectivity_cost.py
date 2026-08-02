#!/usr/bin/env python3
"""THE PRICE OF THE CREBBP-vs-BRD4(1) SELECTIVITY ABFE BENCHMARK — derived, never typed.

`selectivity-benchmark.json` has been fully specified and staged since 2026-07-10 and has no `result` key,
because it is an ABFE job and the ABFE lane was UNPRICED: `vast_cost_model.LADDER_REFERENCE_GPU_H` covers the
OpenFE RBFE / ternary lanes only, so there was no rung to read a figure off. This module is that missing home,
and it is built the same way every ladder rung is — a MEASURED per-unit rate multiplied by a work count that
is read from the engine rather than remembered.

===============================================================================================================
1. WHY THIS IS PRICED ON AWS AND NOT AGAINST THE VAST LADDER  (state the provider — CLAUDE.md §6)
===============================================================================================================

CLAUDE.md §6 says production runs go on Vast. **This lane cannot, today, and the reason is structural rather
than a preference:**

  * There is NO Vast ABFE launcher. Every `*_vast_launch.py` in the repo drives a different lane (ternary,
    protfep, nrv04, selcal, bioemu, paralogue MD, congeneric fan-out). The ABFE engine's only submitter is
    `nr4a3_abfe_sagemaker.py`, and `abfe_plan.workflow` names `gpu-abfe-aws.yml`.
  * The ABFE has only ever run on `ml.g5.xlarge` — an NVIDIA **A10G**, which is deliberately ABSENT from
    `vast_cost_model.MEASURED_NS_PER_DAY_84K`. `card_of("A10G")` returns None BY DESIGN, so an A10G-hour
    cannot be converted into a reference-GPU-hour without inventing a card ratio — the exact "spec-sheet
    proxy" that the cost model records as having produced two retracted rankings.

**So `$/ref-GPU-h` and the §1 `$/ns` drift line are NOT DERIVABLE for this benchmark, and this module refuses
to fabricate them.** That is a real gap, not an oversight, and `usd_per_ns_as_billed()` below reports the
honest AWS-side figure instead, in units that are internally consistent but NOT comparable to the Vast board
(different card, different timestep, different protocol — see §3).

⚠ The §6 market gate (`relaunch_market_gate`) does not apply here either, and that is scope rather than
evasion: its whole subject is *renting a Vast host* — bids, offers, `resources_unavailable`, board depth. AWS
managed spot has no bid and no host selection, so there is nothing for it to gate.

===============================================================================================================
2. THE MEASURED BASIS  (read 2026-08-02 from SageMaker via `list_sagemaker.py MODE=abfe_rate`)
===============================================================================================================

The repo has already run this engine, at THIS EXACT PROTOCOL (12 λ-windows x n_iter=2000 x 500 steps), on
`ml.g5.xlarge` managed spot, twelve times. That is a measurement, not an extrapolation, and it is what the
benchmark is priced from.

★ ESTIMATOR: THE MEDIAN OVER THREE INDEPENDENT LEGS, mirroring `vast_bench_sweep.median_over_hosts`. The
`8xtt-r1/r2/r3` triplet is the right sample — three independent complete legs, same day, same tag family,
same protocol, spread of 8% — where the wider all-legs set is contaminated by RESUMES. A re-dispatch on an
existing tag does only the REMAINING iterations (`run_window` starts at `_last_logged_iter + 1`), so a
partial leg's billable time is real but is not a whole leg's work; taking the median of a clean triplet is
what keeps a resume from dragging the basis down.

⚠ THIS BASIS IS A ONE-SIDED OVER-ESTIMATE, WHICH IS THE SAFE DIRECTION. It is measured on the **NR4A3 LBD**
(~250 residues). The benchmark's receptors are **bromodomains**: CREBBP 116 residues / 971 heavy atoms and
BRD4(1) 127 / 1062, both measured off the staging job's own log. Both are smaller than the basis protein and
smaller than T4-lysozyme (164 residues), so the real legs can only be CHEAPER than this quote. The T4L leg is
carried below as the independent size-appropriate cross-check.
"""
from __future__ import annotations

import json
import os
import statistics

# --- the engine, so the work count is READ rather than remembered -------------------------------------------
import nr4a3_abfe

_HERE = os.path.dirname(os.path.abspath(__file__))

# =============================================================================================================
# MEASURED INPUTS — every one carries the job that produced it (CLAUDE.md §4b: a populated field is not a
# measured one, so nothing here is a default that could be mistaken for an observation).
# =============================================================================================================
# billable hours per COMPLETE complex leg, 12 windows x 2000 iters, ml.g5.xlarge managed spot.
COMPLEX_LEG_BILLABLE_H = {
    "nr4a3-abfe-8xtt-r1-complex-nr4a3-2026-07-10-14-28-04": 2.908,
    "nr4a3-abfe-8xtt-r2-complex-nr4a3-2026-07-10-14-45-07": 2.943,
    "nr4a3-abfe-8xtt-r3-complex-nr4a3-2026-07-10-14-45-04": 3.372,
}
# The wider population, for the RANGE only. Includes resumes (the sub-1 h rows), which is why the point
# estimate above uses the clean triplet instead.
COMPLEX_LEG_BILLABLE_H_ALL = [0.484, 0.746, 1.632, 2.160, 2.572, 2.908, 2.943, 3.372, 3.391, 3.663, 3.868,
                              4.975]
# the shared ligand-in-water leg, same protocol
SOLVENT_LEG_BILLABLE_H = {
    "nr4a3-abfe-solvent-2026-07-05-14-39-49-147": 0.101,
    "nr4a3-abfe-r3-solvent-2026-07-06-10-53-36-015": 0.137,
    "nr4a3-abfe-r2-solvent-2026-07-05-12-27-52-876": 0.618,
}
# gross training hours for the same clean triplet — this, not billable, is what sets WALL CLOCK: managed spot
# bills a fraction of the hours but the job still occupies the wall clock it occupies.
COMPLEX_LEG_TRAINING_H = {
    "nr4a3-abfe-8xtt-r1-complex-nr4a3-2026-07-10-14-28-04": 8.661,
    "nr4a3-abfe-8xtt-r2-complex-nr4a3-2026-07-10-14-45-07": 8.771,
    "nr4a3-abfe-8xtt-r3-complex-nr4a3-2026-07-10-14-45-04": 8.601,
}
# T4-lysozyme L99A + benzene — the SIZE-APPROPRIATE cross-check, 164 residues against the bromodomains' 116
# and 127. Ran at n_iter=1000, so it is scaled below rather than used directly.
T4L_COMPLEX_BILLABLE_H_AT_1000 = 0.732     # abfe-t4l-complex-t4l-2026-07-06-03-04-17-724

# --- the price of an hour -----------------------------------------------------------------------------------
# ★ THE ONE THING MOST EASILY GOT WRONG HERE, AND THE REPO ALREADY DOCUMENTS IT. Managed spot delivers its
# discount as FEWER BILLED HOURS, NOT A LOWER RATE: you are billed for `BillableTimeInSeconds` at (about) the
# on-demand meter, and `BillableTimeInSeconds` already excludes the compute AWS reclaimed. So the cost of a leg
# is `billable_h x the SpotTraining meter rate` — and multiplying billable hours by a "spot rate" applies the
# discount TWICE. One home for the semantics and for this rate: `nr4a3-degrader-next-steps.md` -> "HOW
# MANAGED-SPOT BILLING ACTUALLY WORKS".
#
# CROSS-CHECKED AGAINST A REAL BILL, which is why this is a measurement and not a quoted list price: the
# 2026-07 Ohio bill's SpotTraining line was $102 for 72.6 billable hours = $1.405/h, against the $1.4084 meter.
USD_PER_BILLABLE_H_G5_XLARGE = 1.4084

# ⚠ REGISTERED CORRECTION, NOT A SILENT FIX (CLAUDE.md §1.2). `nr4a3-abfe-calibration.json` records
# `spot_cost_usd` 0.24 (hydration) and 0.10 (T4L). Both are too LOW because they apply a ~$0.40 "spot rate" to
# hours that are ALREADY the discounted number — the precise trap next-steps.md warns about. Recomputed on the
# same jobs' own billable time: hydration 0.608 h -> $0.86 (was 0.24), T4L 0.979 h -> $1.38 (was 0.10). The
# ABFE dispatcher's `SPOT_HOURLY = 0.50` planning stub has the same defect and is superseded by the constant
# above. Nothing downstream of this module used those figures; they are corrected here so they are not requoted.
SUPERSEDED_CALIBRATION_COSTS = {"hydration_gate": 0.24, "binding_gate": 0.10, "SPOT_HOURLY_stub": 0.50}


def _plan():
    """The benchmark's OWN dispatch inputs, read from `selectivity-benchmark.json` (rule 1: it owns them)."""
    with open(os.path.join(_HERE, "selectivity-benchmark.json")) as f:
        return json.load(f)


def work_per_leg(n_iter=None, steps_per_iter=500, timestep_fs=2.0):
    """Nanoseconds of MD in ONE leg. DERIVED from the engine's own λ-schedule, never a typed 12.

    A leg runs `n_windows` INDEPENDENT λ-windows (`nr4a3_abfe.lambda_schedule`), each `n_iter` iterations of
    `steps_per_iter` steps at `timestep_fs`. Windows are serial WITHIN a leg (`run_shard` loops over them);
    legs are parallel across jobs."""
    if n_iter is None:
        n_iter = int(_plan()["abfe_plan"]["dispatch_inputs"]["n_iter"])
    nwin = nr4a3_abfe.n_windows()
    ns_per_window = n_iter * steps_per_iter * timestep_fs * 1e-6   # fs -> ns
    return {"n_windows": nwin, "n_iter": n_iter, "steps_per_iter": steps_per_iter,
            "timestep_fs": timestep_fs, "ns_per_window": ns_per_window,
            "ns_per_leg": nwin * ns_per_window}


def leg_counts():
    """The legs the plan actually buys: one complex leg per receptor + ONE shared solvent leg.

    Read from the plan's own `receptors`, so adding a receptor reprices itself. The shared solvent leg is the
    reason this benchmark is cheap and is also why it is a clean ΔΔG: it is identical across receptors and
    cancels EXACTLY in the difference."""
    recs = [r.strip() for r in _plan()["abfe_plan"]["dispatch_inputs"]["receptors"].split(",") if r.strip()]
    return {"receptors": recs, "n_complex_legs": len(recs), "n_solvent_legs": 1,
            "n_legs": len(recs) + 1}


def _med(d):
    return statistics.median(d.values() if isinstance(d, dict) else d)


def complete_complex_legs(n_iter=2000):
    """`COMPLEX_LEG_BILLABLE_H_ALL` with the RESUMES removed, by a physical rule rather than by eye.

    A re-dispatch on an existing tag runs only the REMAINING iterations, so its billable time is real but is
    not a whole leg's work. Left in, it poses as a very fast leg and drags the low end of the quoted range
    down to a figure nobody could actually buy — which is the same shape of error as a card borrowing a
    faster SKU's throughput.

    THE RULE: an NR4A3-LBD leg (~250 residues) cannot legitimately cost less than the SAME protocol on
    T4-lysozyme (164 residues), because it is the larger system. So anything below the T4L-scaled lower bound
    did not do a full leg's work. On the n_iter=2000 protocol that threshold is ~1.2 h, and it removes exactly
    the two sub-1 h rows. Stated as a bound, so it can be checked rather than trusted."""
    floor = t4l_scaled_complex_leg_h(n_iter)[0]
    return sorted(h for h in COMPLEX_LEG_BILLABLE_H_ALL if h >= floor)


def t4l_scaled_complex_leg_h(n_iter=2000):
    """The T4L leg scaled from n_iter=1000 to `n_iter`, as a size-appropriate LOWER cross-check.

    Returned as an INTERVAL because the split between one-off setup and per-iteration MD was not measured:
      * setup = 0     -> the whole 0.732 h is MD and doubles;
      * setup = 0.25 h -> only the remainder doubles.
    The truth is inside. Both ends are below the NR4A basis, which is the point being made."""
    f = n_iter / 1000.0
    return (T4L_COMPLEX_BILLABLE_H_AT_1000 - 0.25) * f + 0.25, T4L_COMPLEX_BILLABLE_H_AT_1000 * f


def price(n_replicates=1, n_iter=None):
    """The benchmark's cost. Everything here is derived from the measured leg hours above.

    A replicate is a FULL re-run under its OWN TAG (see `replicate_tag_defect` below), so it costs the same
    as the first pass rather than a fraction of it."""
    w = work_per_leg(n_iter=n_iter)
    lc = leg_counts()
    cplx, solv = _med(COMPLEX_LEG_BILLABLE_H), _med(SOLVENT_LEG_BILLABLE_H)
    per_pass_h = lc["n_complex_legs"] * cplx + lc["n_solvent_legs"] * solv
    # the range spans COMPLETE legs only — a resume is not a cheap leg (see complete_complex_legs)
    complete = complete_complex_legs(w["n_iter"])
    lo_h = lc["n_complex_legs"] * min(complete) + min(SOLVENT_LEG_BILLABLE_H.values())
    hi_h = lc["n_complex_legs"] * max(complete) + max(SOLVENT_LEG_BILLABLE_H.values())
    t4l_lo, t4l_hi = t4l_scaled_complex_leg_h(w["n_iter"])
    r = USD_PER_BILLABLE_H_G5_XLARGE
    total_h = per_pass_h * n_replicates
    return {
        "n_replicates": n_replicates,
        "work": w, "legs": lc,
        "ns_per_leg": w["ns_per_leg"],
        "ns_per_pass": w["ns_per_leg"] * lc["n_legs"],
        "ns_total": w["ns_per_leg"] * lc["n_legs"] * n_replicates,
        "billable_h_per_complex_leg": cplx,
        "billable_h_per_solvent_leg": solv,
        "billable_h_per_pass": per_pass_h,
        "billable_h_total": total_h,
        "usd_per_billable_h": r,
        "usd": total_h * r,
        "usd_range": [lo_h * n_replicates * r, hi_h * n_replicates * r],
        "usd_t4l_scaled_likely": (lc["n_complex_legs"] * (t4l_lo + t4l_hi) / 2 + solv) * n_replicates * r,
        # wall clock: legs run in PARALLEL, windows serial within a leg, so the critical path is one complex
        # leg's gross TRAINING time. Replicates can also run in parallel (3 legs x 3 seeds = 9 > the 8-slot
        # spot cap, so a 3-replicate campaign is two waves).
        "wall_clock_h_per_wave": _med(COMPLEX_LEG_TRAINING_H),
        "usd_per_ns_as_billed": (total_h * r) / (w["ns_per_leg"] * lc["n_legs"] * n_replicates),
    }


def usd_per_ns_as_billed(n_replicates=1):
    """$ per nanosecond of ABFE sampling, AWS-side. NOT comparable to the Vast board's `$/ns` — see §1/§3."""
    return price(n_replicates=n_replicates)["usd_per_ns_as_billed"]


# =============================================================================================================
# 3. WHAT THIS NUMBER IS NOT
# =============================================================================================================
NOT_COMPARABLE_TO_LADDER_BASIS = (
    "`vast-ladder-repricing.json`'s $/ns is an INDEX: plain single-replica MD on an 84,534-particle water box "
    "at 4 fs with hydrogen-mass repartitioning, on an RTX 4090. An ABFE nanosecond here is none of those — "
    "12 alchemical λ-windows, 2 fs with NO HMR (`_explicit_generator` sets constraints=HBonds and leaves "
    "hydrogen mass at default), a full reduced-potential evaluation at every λ-state on every iteration, and "
    "an XML checkpoint written every iteration, on an A10G. The two numbers share a unit and measure "
    "different things, so the ratio between them is not a price comparison and must not be quoted as one."
)

# ★ THE DEFECT THIS PRICING WORK TURNED UP, recorded next to the price it changes (rule 1: one home).
replicate_tag_defect = (
    "`selectivity-benchmark.json` -> abfe_plan.replicates says to add seed=1,2 with the SAME TAG. THAT WOULD "
    "PRODUCE A FABRICATED REPLICATE, NOT A SECOND ONE. The checkpoint prefix is "
    "`s3://<bucket>/<TAG>/ckpt/<leg>/` (`nr4a3_abfe_sagemaker.make_estimator`) and carries NO SEED, while "
    "`nr4a3_abfe.run_window` resumes at `_last_logged_iter + 1`. Under a used tag every window is already at "
    "n_iter, so `for it in range(start, n_iter)` never executes: the job exits SUCCESSFULLY, having re-emitted "
    "seed 0's samples under seed 1's label. That is CLAUDE.md §4b exactly — a populated field that was never "
    "measured. Each replicate therefore needs its OWN tag, which is what the NR4A3 run actually did (tags "
    "`nr4a3-abfe`, `-r2`, `-r3`, `8xtt-r1/r2/r3`) and is why a replicate is priced at full cost here."
)


def emit(path=None, replicate_cases=(1, 2, 3)):
    """Regenerate the artifact. A TOTAL IS DERIVED, NEVER TYPED (CLAUDE.md §1.1)."""
    path = path or os.path.join(_HERE, "abfe-selectivity-benchmark-cost.json")
    out = {
        "_what": "Cost of the CREBBP-vs-BRD4(1) SGC-CBP30 selectivity ABFE benchmark "
                 "(research/modalities/selectivity-benchmark.json). THE ONE HOME for this figure.",
        "_generated_by": "research/modalities/abfe_selectivity_cost.py (python abfe_selectivity_cost.py)",
        "_provider": "AWS SageMaker managed spot, ml.g5.xlarge (A10G), us-east-2 — NOT Vast; see the module "
                     "docstring §1 for why this lane cannot use the Vast ladder basis.",
        "_basis": "MEASURED billable hours of this same engine at this same protocol (12 windows x 2000 iters "
                  "x 500 steps), read from SageMaker 2026-08-02 via list_sagemaker.py MODE=abfe_rate.",
        "_basis_is_an_upper_bound": "measured on the NR4A3 LBD (~250 residues); the benchmark's receptors are "
                                    "bromodomains (CREBBP 116 residues/971 heavy atoms, BRD4(1) 127/1062, both "
                                    "from the staging job's log), so the real legs can only be cheaper.",
        "_not_comparable_to_ladder_basis": NOT_COMPARABLE_TO_LADDER_BASIS,
        "_replicate_tag_defect": replicate_tag_defect,
        "_superseded_calibration_costs": SUPERSEDED_CALIBRATION_COSTS,
        "measured_inputs": {
            "complex_leg_billable_h_clean_triplet": COMPLEX_LEG_BILLABLE_H,
            "complex_leg_billable_h_all_at_2000": COMPLEX_LEG_BILLABLE_H_ALL,
            "solvent_leg_billable_h": SOLVENT_LEG_BILLABLE_H,
            "complex_leg_training_h_clean_triplet": COMPLEX_LEG_TRAINING_H,
            "t4l_complex_billable_h_at_1000": T4L_COMPLEX_BILLABLE_H_AT_1000,
            "usd_per_billable_h_g5_xlarge": USD_PER_BILLABLE_H_G5_XLARGE,
        },
        "cases": {f"{n}_replicate{'s' if n > 1 else ''}": price(n_replicates=n) for n in replicate_cases},
    }
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    return out


def _main():
    o = emit()
    print(f"CREBBP vs BRD4(1) selectivity ABFE — {o['_provider'].split(' —')[0]}")
    one = o["cases"]["1_replicate"]
    w = one["work"]
    print(f"\nWORK (derived from the engine's own schedule):")
    print(f"  {w['n_windows']} λ-windows x {w['n_iter']} iters x {w['steps_per_iter']} steps x "
          f"{w['timestep_fs']} fs = {w['ns_per_window']:.1f} ns/window")
    print(f"  ns per leg      {one['ns_per_leg']:.1f}")
    print(f"  legs per pass   {one['legs']['n_legs']}  "
          f"({one['legs']['n_complex_legs']} complex + 1 shared solvent) -> {one['ns_per_pass']:.0f} ns")
    print(f"\nMEASURED RATE  {one['billable_h_per_complex_leg']:.3f} billable-h per complex leg, "
          f"{one['billable_h_per_solvent_leg']:.3f} per solvent leg,  "
          f"${one['usd_per_billable_h']}/billable-h")
    print(f"\n{'case':22} {'billable-h':>11} {'USD':>9} {'range USD':>18} {'likely (T4L)':>13} {'$/ns':>10}")
    for k, c in o["cases"].items():
        print(f"  {k:20} {c['billable_h_total']:11.2f} {c['usd']:9.2f} "
              f"{c['usd_range'][0]:8.2f}-{c['usd_range'][1]:<9.2f} {c['usd_t4l_scaled_likely']:13.2f} "
              f"{c['usd_per_ns_as_billed']:10.4f}")
    print(f"\nWALL CLOCK  ~{one['wall_clock_h_per_wave']:.1f} h per wave (legs run in parallel; windows are "
          f"serial within a leg)")
    print("\nNOTE: the basis is measured on the NR4A3 LBD and the benchmark's bromodomains are smaller, so "
          "every figure above is a one-sided OVER-estimate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
