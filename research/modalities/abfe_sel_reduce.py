#!/usr/bin/env python3
"""THE VERDICT: does the ABFE engine recover the KNOWN CREBBP-vs-BRD4(1) selectivity of SGC-CBP30?

Reads the per-unit window logs this lane synced to S3, MBAR-reduces each leg, combines them into ΔG_bind per
(replicate, receptor), differences them into a per-replicate ΔΔG, and reports the mean against the published
**ΔΔG_exp ≈ -2.19 kcal/mol** with a **REPLICATE-SD** error bar.

★★ REPLICATE SD, NOT MBAR SE — AND THE DIFFERENCE IS THE WHOLE POINT (CLAUDE.md §5, "ABFE standard:
converged fwd/rev + ~3 independent replicates + honest replicate-SD, not MBAR-SE error bars").
The MBAR asymptotic SE measures the precision of the ensemble that was *actually sampled*; it shrinks like
1/sqrt(N) whether or not the mean has equilibrated, so a leg stuck in one basin reports a beautifully tight
error bar around the wrong number. The SD across INDEPENDENT replicates — different Langevin noise streams,
different initial velocities, independently built systems — is the only estimator here that can see that
failure. Both are reported, and the MBAR SE is labelled as the thing it is so it cannot be quoted as the
uncertainty on the result.

★ WHY THE SOLVENT LEG DOES NOT CARRY THE ΔΔG, and why it is run anyway.
    ΔG_bind(R) = ΔG_dec(solvent) - ΔG_dec(complex,R) - SSC(R)
so the shared solvent term CANCELS EXACTLY in ΔΔG = ΔG_bind(crebbp) - ΔG_bind(brd4bd1), leaving
    ΔΔG = ΔG_dec(complex,brd4bd1) - ΔG_dec(complex,crebbp) - SSC(crebbp) + SSC(brd4bd1).
That cancellation is a feature of the design (`selectivity-benchmark.json` -> why_this_system) and it is why
this benchmark is cheap. The solvent leg is still run per replicate because the ABSOLUTE ΔG_bind values are
reported alongside the ΔΔG and are meaningless without it — but a solvent-leg failure degrades the absolute
numbers only, and this module says so rather than refusing to emit a verdict it can compute.

★ RUN THIS IN THE SAME IMAGE THAT PRODUCED THE SAMPLES (CLAUDE.md §6, parity). MBAR numbers can move with the
pymbar/openmmtools version, so an ad-hoc `pip install pymbar` in an analysis step is a silent protocol
deviation. The workflow runs it inside `triskit23/ternary-fep` with `research/modalities` mounted.
"""
from __future__ import annotations

import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(_HERE, "abfe-sel-cbp30-result.json")

RECEPTORS = ("crebbp", "brd4bd1")


def experimental():
    """The published answer — READ from `selectivity-benchmark.json`, which owns it (CLAUDE.md rule 1)."""
    with open(os.path.join(_HERE, "selectivity-benchmark.json")) as f:
        return json.load(f)["experimental_selectivity"]


# =============================================================================================================
# pure arithmetic — unit-testable without a single sample
# =============================================================================================================
def ddg_from_replicate(legs, seed):
    """ΔΔG and both ΔG_bind for ONE replicate, from {unit_id: {dg, se, ssc}}. PURE.

    `legs` entries are DECOUPLING free energies as `nr4a3_abfe.reduce_leg` returns them. Returns a dict, or
    None with a `missing` note when a required leg is absent — never a partial number wearing a full one's
    name (CLAUDE.md §4b).
    """
    import nr4a3_abfe
    need = [f"r{seed}-solvent"] + [f"r{seed}-complex-{r}" for r in RECEPTORS]
    missing = [u for u in need if u not in legs or legs[u].get("dg") is None]
    if missing:
        return {"seed": seed, "complete": False, "missing": missing}
    solv = legs[f"r{seed}-solvent"]
    out = {"seed": seed, "complete": True, "solvent_dg": solv["dg"], "solvent_se": solv["se"], "per_receptor": {}}
    for r in RECEPTORS:
        c = legs[f"r{seed}-complex-{r}"]
        dg, se = nr4a3_abfe.combine_legs(c["dg"], c["se"], solv["dg"], solv["se"], c["ssc"])
        out["per_receptor"][r] = {"dg_bind": dg, "mbar_se": se, "complex_dg": c["dg"],
                                  "complex_mbar_se": c["se"], "restraint_standard_state_dg": c["ssc"],
                                  "n_receptor_atoms": c.get("n_receptor_atoms")}
    a, b = out["per_receptor"][RECEPTORS[0]], out["per_receptor"][RECEPTORS[1]]
    out["ddg"] = a["dg_bind"] - b["dg_bind"]
    out["ddg_mbar_se"] = (a["mbar_se"] ** 2 + b["mbar_se"] ** 2) ** 0.5
    return out


def summarise(replicates, ddg_exp, tol=1.0):
    """The headline: mean ΔΔG, REPLICATE SD, and the pass verdict. PURE.

    `tol` is the quantitative band from `selectivity-benchmark.json`'s own pass_criterion (~1 kcal/mol); the
    DIRECTION test is the primary one and is reported separately, because a direction pass with a magnitude
    miss and a direction failure are entirely different findings about the instrument.
    """
    good = [r for r in replicates if r.get("complete")]
    vals = [r["ddg"] for r in good]
    if not vals:
        return {"n_replicates": 0, "verdict": "NO_RESULT",
                "reason": "no replicate has all three legs reduced; nothing to grade"}
    mean = statistics.fmean(vals)
    # ⚠ SAMPLE SD (n-1), and it is UNDEFINED for a single replicate rather than 0.0. Reporting 0.0 for n=1
    # would publish a perfect error bar for an unreplicated number — the exact shape of over-claim CLAUDE.md
    # §4b calls "a populated field that was never measured".
    sd = statistics.stdev(vals) if len(vals) > 1 else None
    direction_ok = mean < 0
    err = mean - float(ddg_exp)
    return {
        "n_replicates": len(vals),
        "ddg_per_replicate": {r["seed"]: round(r["ddg"], 3) for r in good},
        "ddg_calc_mean": round(mean, 3),
        "ddg_replicate_sd": (round(sd, 3) if sd is not None else None),
        "ddg_replicate_sd_note": ("REPLICATE SD across independent seeds — the honest error bar. The MBAR SE "
                                  "below measures only the precision of the sampled ensemble and is NOT the "
                                  "uncertainty on this result." if sd is not None else
                                  "UNDEFINED at n=1: a single replicate has no replicate SD, and reporting "
                                  "0.0 would be a fabricated error bar."),
        "ddg_mbar_se_mean": round(statistics.fmean([r["ddg_mbar_se"] for r in good]), 3),
        "ddg_exp": float(ddg_exp),
        "error_vs_exp": round(err, 3),
        "direction_recovered": bool(direction_ok),
        "within_tolerance": bool(abs(err) <= tol),
        "tolerance_kcal": tol,
        "verdict": ("PASS_QUANTITATIVE" if direction_ok and abs(err) <= tol else
                    "PASS_DIRECTION_ONLY" if direction_ok else "FAIL_DIRECTION"),
    }


# =============================================================================================================
# the S3 side
# =============================================================================================================
def fetch_units(bucket, prefix, work_dir, units=None):
    """Download every unit's window logs + meta.json into `work_dir/<unit>/`. Returns the unit ids seen."""
    import boto3
    s3 = boto3.client("s3")
    seen = set()
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=f"{prefix.rstrip('/')}/"):
        for obj in page.get("Contents", []):
            rel = obj["Key"][len(prefix.rstrip("/")) + 1:]
            parts = rel.split("/")
            if len(parts) != 2:
                continue
            uid, base = parts
            if uid.endswith("-smoke"):
                continue                       # the smoke's ΔG is meaningless BY CONSTRUCTION; never score it
            if units and uid not in units:
                continue
            if not (base.startswith("window_") and base.endswith(".jsonl")) and base != "meta.json":
                continue
            dest = os.path.join(work_dir, uid, base)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            s3.download_file(bucket, obj["Key"], dest)
            seen.add(uid)
    return sorted(seen)


def reduce_unit(unit_dir):
    """MBAR-reduce ONE leg from its downloaded logs -> {dg, se, ssc, ...}. `dg` is None if it cannot solve."""
    import nr4a3_abfe
    out = {"dg": None, "se": None, "ssc": None}
    meta_path = os.path.join(unit_dir, "meta.json")
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path))
        out["ssc"] = meta.get("restraint_standard_state_dg")
        out["leg"] = meta.get("leg")
        out["n_receptor_atoms"] = meta.get("n_receptor_atoms")
        out["lambda_schedule"] = meta.get("lambda_schedule")
        out["seed"] = meta.get("seed")
    try:
        dg, se = nr4a3_abfe.reduce_leg(unit_dir)
        out["dg"], out["se"] = dg, se
    except Exception as e:  # noqa: BLE001 — a leg that cannot solve is a REPORTED gap, never a silent zero
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def run(bucket=None, prefix=None, work_dir=None, out_path=None, seeds=None):
    import tempfile
    b = bucket or os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
    p = prefix or os.environ.get("ABFE_SEL_RESULT_PREFIX") or "abfe-sel-cbp30-vast"
    wd = work_dir or tempfile.mkdtemp(prefix="abfe-sel-")
    print(f"[reduce] pulling s3://{b}/{p}/ -> {wd}", flush=True)
    uids = fetch_units(b, p, wd)
    print(f"[reduce] {len(uids)} unit(s): {uids}", flush=True)
    legs = {}
    for uid in uids:
        legs[uid] = reduce_unit(os.path.join(wd, uid))
        d = legs[uid]
        print(f"[reduce] {uid}: decoupling ΔG = "
              + (f"{d['dg']:.3f} ± {d['se']:.3f} kcal/mol" if d["dg"] is not None
                 else f"UNSOLVED — {d.get('error')}"), flush=True)
    ss = seeds if seeds is not None else sorted({int(u.split("-")[0][1:]) for u in uids
                                                 if u.startswith("r") and u[1:2].isdigit()})
    reps = [ddg_from_replicate(legs, s) for s in ss]
    exp = experimental()
    summary = summarise(reps, exp["ddg_kcal_per_mol"])
    doc = {
        "_what": "Known-answer selectivity test of the independent-window ABFE engine: SGC-CBP30 across "
                 "CREBBP and BRD4(1). THE ONE HOME for this result.",
        "_generated_by": "research/modalities/abfe_sel_reduce.py",
        "_provider": "Vast.ai (rtx4090 tier), image triskit23/ternary-fep — checkpoints in S3 as an object "
                     "store only.",
        "_engine": "research/modalities/nr4a3_abfe.py (independent λ-windows + MBAR + Boresch SSC)",
        "_experimental": exp,
        "source": f"s3://{b}/{p}/",
        "units": legs,
        "replicates": reps,
        "summary": summary,
    }
    path = out_path or OUT_PATH
    with open(path, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    _print(doc)
    return doc


def _print(doc):
    s = doc["summary"]
    print("\n" + "=" * 96)
    print("CREBBP vs BRD4(1) / SGC-CBP30 — ABFE KNOWN-ANSWER SELECTIVITY TEST")
    print("=" * 96)
    for r in doc["replicates"]:
        if not r.get("complete"):
            print(f"  seed {r['seed']}: INCOMPLETE — missing {r.get('missing')}")
            continue
        pr = r["per_receptor"]
        print(f"  seed {r['seed']}: ΔG_bind(CREBBP) = {pr['crebbp']['dg_bind']:.2f}, "
              f"ΔG_bind(BRD4-1) = {pr['brd4bd1']['dg_bind']:.2f}  ->  ΔΔG = {r['ddg']:+.2f} kcal/mol")
    if s.get("n_replicates"):
        sd = s["ddg_replicate_sd"]
        print(f"\n  ΔΔG_calc = {s['ddg_calc_mean']:+.2f} "
              + (f"± {sd:.2f} (replicate SD, n={s['n_replicates']})" if sd is not None
                 else f"(n=1 — NO replicate SD; see the note)")
              + f"   vs   ΔΔG_exp = {s['ddg_exp']:+.2f} kcal/mol")
        print(f"  error {s['error_vs_exp']:+.2f} kcal/mol | direction recovered: {s['direction_recovered']} "
              f"| within ±{s['tolerance_kcal']:.1f}: {s['within_tolerance']}")
        print(f"  (MBAR SE mean {s['ddg_mbar_se_mean']:.2f} — precision of the sampled ensemble, NOT the "
              f"uncertainty on this result)")
    print(f"\n  VERDICT: {s['verdict']}" + (f" — {s.get('reason')}" if s.get("reason") else ""))
    print("=" * 96 + "\n")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    kw = {}
    for i, a in enumerate(argv):
        if a == "--bucket" and i + 1 < len(argv):
            kw["bucket"] = argv[i + 1]
        if a == "--prefix" and i + 1 < len(argv):
            kw["prefix"] = argv[i + 1]
        if a == "--out" and i + 1 < len(argv):
            kw["out_path"] = argv[i + 1]
    run(**kw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
