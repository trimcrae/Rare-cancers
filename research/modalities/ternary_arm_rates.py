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


# =============================================================================================================
# ★★ THE SYSTEM-SIZE AXIS — the third thing that may never be pooled (trimcrae-approved, 2026-07-31)
# =============================================================================================================
# `_never_pool` covered timestep and phase. It did NOT cover SYSTEM SIZE, and the 4 fs ternary rate was
# therefore a median over legs spanning 141,458-147,788 particles with a 7.9-31.8 s/iter spread — a number
# that describes no single assembly. A cadence derived from it is a cadence for a system nobody ran.
#
# ⚠ THE TOLERANCE IS RELATIVE AND EXPLICIT, NOT A ROUNDING. Fixed-width bins put 141,458 and 147,788 (4.5 %
# apart, the same staged complex re-solvated) in different buckets while merging genuinely different systems
# at the bin edges. Greedy clustering at a stated relative tolerance says what it means: "these legs are the
# same system to within TOL".
SYSTEM_SIZE_TOL = 0.15


def system_buckets(values, tol=SYSTEM_SIZE_TOL):
    """[(label, [values])] clustering particle counts that are the same system to within `tol`. PURE.

    Greedy over sorted values: a value joins the open cluster while it is within `tol` of that cluster's
    RUNNING MEDIAN, else it opens a new one. Labelled by the cluster median in thousands, so a label is a
    fact about the members rather than a bin boundary nobody chose."""
    vals = sorted(float(v) for v in values if v)
    out = []
    cur = []
    for v in vals:
        if cur and abs(v - statistics.median(cur)) / statistics.median(cur) > tol:
            out.append(cur)
            cur = []
        cur.append(v)
    if cur:
        out.append(cur)
    return [("%dk" % round(statistics.median(c) / 1000.0), c) for c in out]


def bucket_label_for(n_particles, buckets):
    """Which bucket a leg belongs to, or None when the leg recorded no particle count. PURE.

    None is deliberate and is NOT folded into the nearest bucket: a leg with no recorded size cannot be shown
    to belong to any system, and guessing is how the pooled rate arose in the first place."""
    if not n_particles:
        return None
    for label, members in buckets:
        if abs(float(n_particles) - statistics.median(members)) / statistics.median(members) <= SYSTEM_SIZE_TOL:
            return label
    return None


def rates_by_system(rows):
    """{timestep: {arm: {system_bucket: {...}}}} — the SAME estimator as `aggregate`, split by system size.

    Kept BESIDE `aggregate` rather than replacing it, deliberately. `arm_iteration_rates` has consumers whose
    behaviour must not change until a caller opts in by passing a size, and a silent re-keying of the live
    cadence table is exactly the kind of change that would be discovered by a leg failing to resume.
    """
    out = {}
    for r in rows:
        dt = r.get("timestep_fs")
        if dt is None:
            continue
        out.setdefault(f"{float(dt):.1f}", {}).setdefault(r["arm"], []).append(r)
    res = {}
    for dt, arms in sorted(out.items()):
        res[dt] = {}
        for arm, rs in sorted(arms.items()):
            buckets = system_buckets([r.get("n_particles") for r in rs])
            grouped = {}
            for r in rs:
                lb = bucket_label_for(r.get("n_particles"), buckets)
                grouped.setdefault(lb or "unrecorded", []).append(r)
            res[dt][arm] = {}
            for lb, group in sorted(grouped.items()):
                prod = [r["production_median_s_per_iter"] for r in group
                        if r.get("production_median_s_per_iter")]
                warm = [r["warmup_median_s_per_iter"] for r in group if r.get("warmup_median_s_per_iter")]
                use, src = (prod, "production") if prod else (warm, "warmup")
                if not use:
                    continue
                res[dt][arm][lb] = {
                    "s_per_iter": round(statistics.median(use), 3),
                    "source_phase": src, "n_legs": len(use),
                    "spread_s_per_iter": [round(min(use), 3), round(max(use), 3)],
                    "n_particles": sorted({r["n_particles"] for r in group if r.get("n_particles")}),
                    "units": [r["unit_id"] for r in group],
                    "gpus": sorted({r["gpu"] for r in group if r.get("gpu")}),
                }
    return res


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
            # PER-CARD, so a ratio between two arms can be re-checked WITHOUT the card mix in it. The lane
            # rents a mixed fleet (4080S / 4090 / 5090 all appear), and if one arm happened to be measured
            # on faster silicon than the other then an "arm ratio" would be partly a CARD ratio — the same
            # confound pricing.md's superseded ~2.06x fell into from the other direction.
            per_gpu = {}
            for r in rs:
                v = r.get(f"{src}_median_s_per_iter")
                if r.get("gpu") and v:
                    per_gpu.setdefault(r["gpu"], []).append(v)
            out[dt][arm] = {
                "s_per_iter": round(statistics.median(use), 3),
                "source_phase": src,
                "n_legs": len(use),
                "spread_s_per_iter": [round(min(use), 3), round(max(use), 3)],
                "units": [r["unit_id"] for r in rs],
                "gpus": sorted({r["gpu"] for r in rs if r.get("gpu")}),
                "by_gpu": {g: round(statistics.median(v), 3) for g, v in sorted(per_gpu.items())},
            }
            # ★ SAY WHEN THIS NUMBER DESCRIBES NO SINGLE ASSEMBLY. The rate stays pooled (consumers depend on
            # it), but a pooled rate that does not ADMIT it is the defect — a reader cannot tell a measured
            # system rate from a median across two.
            sizes = sorted({r["n_particles"] for r in rs if r.get("n_particles")})
            bks = system_buckets(sizes)
            out[dt][arm]["n_particles_spread"] = [sizes[0], sizes[-1]] if sizes else None
            out[dt][arm]["system_buckets"] = [lb for lb, _ in bks]
            out[dt][arm]["pooled_across_systems"] = len(bks) > 1
            out[dt][arm]["_system_warning"] = (
                None if len(bks) <= 1 else
                "POOLED ACROSS %d SYSTEM SIZES %s — this median describes no single assembly. Use "
                "`rates_by_system` for a per-system figure; see `_never_pool`." % (len(bks), [lb for lb, _ in bks]))
    return out


def phase_cross_check(rows):
    """warmup ÷ production on the legs that measured BOTH — the check on this file's one cross-phase step.

    ★ WHY IT IS WORTH RECORDING RATHER THAN ASSUMING. The cadence being derived governs the WARMUP phase,
    but the long timing series are in PRODUCTION, and the argument for using one for the other is structural:
    `rbfe_spot_driver` builds the warmup move by overriding `.timestep` on a move whose `n_steps` was already
    fixed at the PRODUCTION dt, so the two phases are the same number of force evaluations per iteration
    (`ternary-4fs-vast-findings.md` §4). A structural argument that is checkable should be checked. If this
    ratio ever comes back well ABOVE 1 the substitution is optimistic — a production rate would then
    UNDERSTATE the warmup seconds at risk — and the derivation should switch to warmup medians.
    """
    pairs = [(r["unit_id"], r["warmup_median_s_per_iter"] / r["production_median_s_per_iter"])
             for r in rows
             if r.get("warmup_median_s_per_iter") and r.get("production_median_s_per_iter")]
    if not pairs:
        return {"n": 0}
    vals = [v for _u, v in pairs]
    return {
        "n": len(vals),
        "median_warmup_over_production": round(statistics.median(vals), 3),
        "range": [round(min(vals), 3), round(max(vals), 3)],
        "per_unit": {u: round(v, 3) for u, v in pairs},
        "_reading": ("<= 1 means a production median OVERSTATES the seconds a warmup iteration costs, so "
                     "deriving the interval from production is conservative — it buys a FINER cadence than "
                     "strictly needed, erring toward less work at risk"),
    }


def build(bucket=None, prefix=None, recs=None, rows=None, n_records=None):
    """The artifact. `rows=` re-aggregates an EXISTING artifact's rows without touching S3, which is what
    makes the aggregation testable — and re-derivable — off a machine with no credentials."""
    if rows is None:
        recs = tv.leg_records(bucket, prefix) if recs is None else recs
        rows = rows_from_records(recs)
        n_records = len(recs)
    return {
        "_what": ("measured seconds-per-iteration per ARM per PRODUCTION TIMESTEP, read from each leg's own "
                  "leg.json timing block. The one home for `ternary_vast_launch.arm_iteration_rates()`; "
                  "regenerate with `python research/modalities/ternary_arm_rates.py --out <this file>`."),
        "_never_pool": ("across timestep_fs (a 2 fs iteration is 1250 MD steps, a 4 fs one 625), across "
                        "phase (pricing.md's superseded ~2.06x card ratio was a warmup/production mix-up), "
                        "or across SYSTEM SIZE (added 2026-07-31: the 4 fs ternary rate pooled legs spanning "
                        "141,458-147,788 particles with a 7.9-31.8 s/iter spread, so it described no single "
                        "assembly; `rates` keeps the pooled figure for existing consumers but now FLAGS it, "
                        "and `rates_by_system` is the split table)"),
        "generated_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
        "n_leg_records": n_records if n_records is not None else len(rows),
        "rates": aggregate(rows),
        "rates_by_system": rates_by_system(rows),
        "phase_cross_check": phase_cross_check(rows),
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
                         f"spread {a['spread_s_per_iter']}, by_gpu={a['by_gpu']}]")
    x = doc.get("phase_cross_check") or {}
    if x.get("n"):
        lines.append(f"---- warmup/production on the {x['n']} legs that measured both: "
                     f"median {x['median_warmup_over_production']} (range {x['range']}) ----")
    lines.append(render_cadence())
    return "\n".join(lines)


def render_cadence():
    """WHAT THE MEASUREMENT BUYS, in the unit that matters — SECONDS OF WORK AT RISK per arm.

    A rate table nobody converts into an exposure is a table nobody can grade: `16.6 s/iter` does not tell
    anyone whether a host reclaim costs this lane four minutes or twenty. This prints, per opted-in mode and
    per leg, the interval that was DERIVED, the exposure it buys, and the fraction of warmup wall-clock spent
    committing at that interval — the two halves of the trade-off, side by side. An arm with no measured rate
    prints `—` rather than a fabricated number.
    """
    out = ["---- DERIVED CHECKPOINT CADENCE (exposure = interval x s/iter = SECONDS AT RISK PER RECLAIM) ----"]
    for mode, sizing in tv.MODES.items():
        if not sizing.get("per_arm_ckpt"):
            continue
        dt, wdt = tv.resolve_timesteps(mode)
        out.append(f"  {mode} (dt={dt}fs, warmup target {tv.warmup_target_iters(dt, wdt)} iters, "
                   f"reference arm '{tv.CKPT_REFERENCE_ARM}' at ci={sizing['warmup_ckpt_iters']})")
        for leg in sorted({leg for (leg, _s, _d) in tv.units_for(mode)}):
            e = tv.ckpt_exposure_s(leg, mode)
            f = tv.ckpt_overhead_fraction(leg, mode)
            out.append(f"    {tv.arm_of_leg(leg):<8} {leg:<32} ci={tv.warmup_ckpt_iters_for(leg, mode):>4}  "
                       + (f"exposure={e:7.1f}s  commit overhead={f:5.2%}" if e else "exposure=—  overhead=—"))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None, help="write the JSON artifact here")
    ap.add_argument("--bucket", default=None)
    ap.add_argument("--prefix", default=None)
    ap.add_argument("--rebuild-from", default=None,
                    help="re-aggregate an existing artifact's `legs` rows instead of reading S3 — no "
                         "credentials needed, and it is how the aggregation is unit-tested")
    a = ap.parse_args(argv)
    if a.rebuild_from:
        prev = json.load(open(a.rebuild_from))
        doc = build(rows=prev["legs"], n_records=prev.get("n_leg_records"))
    else:
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
