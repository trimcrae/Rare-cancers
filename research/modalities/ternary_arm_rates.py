#!/usr/bin/env python3
"""MEASURE the per-arm seconds-per-iteration this lane actually gets, and write the ONE HOME for it.

★★ WHY THIS SCRIPT EXISTS AND WHY THE NUMBERS ARE NOT TYPED INTO THE LAUNCHER (CLAUDE.md §1, §4).
`ternary_vast_launch.warmup_ckpt_iters_for` derives a per-arm checkpoint cadence, and the input to that
derivation is a MEASURED rate. A rate typed into a source file is a rate nobody can re-check and nobody
re-derives when the fleet moves to a different card, so this reads the rates off the legs' OWN records in S3
and writes `ternary-arm-iteration-rates.json`, which the launcher loads. Re-run it and the cadence follows.

★★ TWO COMPARISONS THIS FILE REFUSES TO MAKE, BOTH OF WHICH HAVE ALREADY BEEN MADE BY HAND IN THIS REPO:

  1. **A WARMUP rate against a PRODUCTION rate.** `pricing.md`'s "⚠ CORRECTION 2026-07-26" is exactly this
     error: an L4→4090 card ratio of "~2.06× (33 → 16 s/iter)" turned out to compare a 33.91 s/iter WARMUP
     figure against a 16 s/iter PRODUCTION median, and production-to-production the ratio is ~3.53×. So each
     phase is kept in its own column here and never pooled.
  2. **Rates at DIFFERENT PRODUCTION TIMESTEPS.** An "iteration" is `time_per_iteration / dt` MD steps, so a
     2 fs iteration is 1250 steps and a 4 fs iteration is 625 — a factor of two in wall time for the same
     physics (`ternary-4fs-vast-findings.md` §1/§2, and §2's closing line: "iterations are not comparable
     across protocols"). Rows are therefore grouped by `timestep_fs` and NEVER pooled across it.

★ WHAT A PRODUCTION MEDIAN IS ALLOWED TO SAY ABOUT THE WARMUP, which is what the checkpoint cadence needs.
The warmup integrator is built by overriding `.timestep` on a move whose `n_steps` was already fixed at the
PRODUCTION dt (`rbfe_spot_driver.py`, `warmup_integrator.timestep = ...`), so a warmup iteration and a
production iteration are the SAME number of force evaluations — `ternary-4fs-vast-findings.md` §4: "warmup and
production cost the same wall time per iteration here". A production median at dt X is therefore a legitimate
estimate of the warmup rate at dt X. The warmup column is still collected and reported, because that is the
direct measurement and it is the one to prefer when a leg has enough of it.

Read-only: it lists and GETs `leg.json` objects. It rents nothing, destroys nothing and touches no instance.
"""
import argparse
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ternary_vast_launch as tv  # noqa: E402


def _phase(rec, phase):
    t = (rec.get("timing") or {}).get(phase) or {}
    return t.get("median_s_per_iter"), t.get("n")


def rows_from_records(recs):
    """One row per unit that measured anything. PURE given `recs`."""
    out = []
    for uid, d in sorted(recs.items()):
        wmed, wn = _phase(d, "warmup")
        pmed, pn = _phase(d, "production")
        if wmed is None and pmed is None:
            continue
        out.append({
            "unit_id": uid,
            "leg_id": d.get("leg_id"),
            "arm": tv.arm_of_leg(d.get("leg_id") or uid),
            "mode": d.get("mode"),
            "status": d.get("status"),
            "timestep_fs": d.get("timestep_fs"),
            "warmup_timestep_fs": d.get("warmup_timestep_fs"),
            "gpu": d.get("gpu"),
            "n_particles": d.get("n_particles"),
            "warmup_median_s_per_iter": wmed, "warmup_n": wn,
            "production_median_s_per_iter": pmed, "production_n": pn,
            "recorded_utc": d.get("_s3_last_modified"),
        })
    return out


def aggregate(rows):
    """{timestep_fs: {arm: {...}}} — the median of the per-leg medians, per arm, PER TIMESTEP. PURE.

    ⚠ THE MEDIAN OF MEDIANS IS DELIBERATE, not laziness. Each leg contributes ONE number however long it ran,
    so a leg that survived 1200 iterations does not drown out one that survived 200 — the quantity being
    estimated is "what does an arm cost per iteration on the hosts this lane rents", and every rental is one
    draw from that market. Pooling raw iteration timings would weight by host survival time, which is the one
    variable the checkpoint cadence exists to be robust to.

    PRODUCTION is preferred over WARMUP where both exist, because production medians are the longer series
    (thousands of iterations against a few hundred) and the two phases are the same steps per iteration —
    see the module docstring. `source` records which was used, per arm, so it is never a guess.
    """
    by = {}
    for r in rows:
        dt = r.get("timestep_fs")
        if dt is None:
            continue
        by.setdefault(f"{float(dt):.1f}", {}).setdefault(r["arm"], []).append(r)
    out = {}
    for dt, arms in sorted(by.items()):
        out[dt] = {}
        for arm, rs in sorted(arms.items()):
            prod = [r["production_median_s_per_iter"] for r in rs
                    if r.get("production_median_s_per_iter")]
            warm = [r["warmup_median_s_per_iter"] for r in rs if r.get("warmup_median_s_per_iter")]
            use, src = (prod, "production") if prod else (warm, "warmup")
            if not use:
                continue
            out[dt][arm] = {
                "s_per_iter": round(statistics.median(use), 3),
                "source_phase": src,
                "n_legs": len(use),
                "spread_s_per_iter": [round(min(use), 3), round(max(use), 3)],
                "units": [r["unit_id"] for r in rs],
                "gpus": sorted({r["gpu"] for r in rs if r.get("gpu")}),
            }
    return out


def build(bucket=None, prefix=None, recs=None):
    recs = tv.leg_records(bucket, prefix) if recs is None else recs
    rows = rows_from_records(recs)
    return {
        "_what": ("measured seconds-per-iteration per ARM per PRODUCTION TIMESTEP, read from each leg's own "
                  "leg.json timing block. The one home for `ternary_vast_launch.ARM_ITERATION_RATES`; "
                  "regenerate with `python research/modalities/ternary_arm_rates.py --out <this file>`."),
        "_never_pool": ("across timestep_fs (a 2 fs iteration is 1250 MD steps, a 4 fs one 625) or across "
                        "phase (pricing.md's superseded ~2.06x card ratio was a warmup/production mix-up)"),
        "generated_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
        "n_leg_records": len(recs),
        "rates": aggregate(rows),
        "legs": rows,
    }


def render(doc):
    lines = [f"---- TERNARY ARM ITERATION RATES ({doc['n_leg_records']} leg records) ----"]
    for r in doc["legs"]:
        lines.append(
            f"  {r['unit_id']}\n"
            f"      arm={r['arm']} mode={r['mode']} status={r['status']} dt={r['timestep_fs']}fs "
            f"gpu={r['gpu']} n_particles={r['n_particles']}\n"
            f"      warmup median={r['warmup_median_s_per_iter']} s/iter (n={r['warmup_n']})  "
            f"production median={r['production_median_s_per_iter']} s/iter (n={r['production_n']})")
    lines.append("---- AGGREGATED, PER TIMESTEP (never pooled across dt) ----")
    for dt, arms in sorted(doc["rates"].items()):
        for arm, a in sorted(arms.items()):
            lines.append(f"  dt={dt}fs {arm:<8} {a['s_per_iter']:>7.3f} s/iter  "
                         f"[{a['source_phase']}, n_legs={a['n_legs']}, "
                         f"spread {a['spread_s_per_iter']}, gpus={a['gpus']}]")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None, help="write the JSON artifact here")
    ap.add_argument("--bucket", default=None)
    ap.add_argument("--prefix", default=None)
    a = ap.parse_args(argv)
    doc = build(a.bucket, a.prefix)
    print(render(doc))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(doc, fh, indent=2, sort_keys=False)
            fh.write("\n")
        print(f"[arm-rates] wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
