#!/usr/bin/env python3
"""Anti-target selectivity readout: is each survivor an NR4A-family ligand or a universal sticker?

Compares each drug's NR4A3 docking delta-G (from the 3-receptor screen) to its best (most favorable) off-target
delta-G across the panel (both smina, 24 Angstrom box, exhaustiveness 8 -> directly comparable). The key number
is the SELECTIVITY GAP = best_offtarget_dG - nr4a3_dG:
  gap >> 0  (off-targets bind WEAKER than NR4A3)  => NR4A-family-preferential (good)
  gap ~ 0 or < 0 (an off-target binds as well/better) => promiscuous lipophilic sticker (bad for a lead)
Also counts how many panel targets bind within 2 kcal of NR4A3, and flags PXR/HSA (the promiscuity sensors).

Env: ANTITARGET_PREFIX (default nr4a3-antitarget/<tag>-ckpt), NR4A_PREFIX (the 3-receptor dock summary prefix,
default nr4a3-repurpose-3recept-fm), NR4A_KEY (default nr4a3-3recept.json), AWS creds + AWS_DEFAULT_REGION.
"""
import json
import os
import sys


def _s3():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    return s3, bucket


def _get(s3, bucket, key):
    try:
        return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except Exception as e:  # noqa: BLE001
        print(f"  (could not read s3://{bucket}/{key}: {e})")
        return None


def _nr4a3_dG(rec):
    """Pull the NR4A3 smina dock dG from a 3-receptor dock record, tolerant of field naming."""
    for k in ("dG_NR4A3", "dg_NR4A3"):
        if rec.get(k) is not None:
            return rec[k]
    for k in ("dG_by_target", "dG", "dg"):
        v = rec.get(k)
        if isinstance(v, dict) and v.get("NR4A3") is not None:
            return v["NR4A3"]
    return None


def main():
    s3, bucket = _s3()
    at_prefix = os.environ.get("ANTITARGET_PREFIX", "nr4a3-antitarget/panel-ckpt")
    at = _get(s3, bucket, f"{at_prefix}/nr4a3-antitarget.json")
    if not at:
        sys.exit("no anti-target results")
    panel = at.get("panel", [])
    sensors = {"PXR", "HSA"}

    nr_prefix = os.environ.get("NR4A_PREFIX", "nr4a3-repurpose-3recept-fm")
    nr_key = os.environ.get("NR4A_KEY", "nr4a3-3recept.json")
    nr = _get(s3, bucket, f"{nr_prefix}/{nr_key}") or {}
    nr3 = {}
    for c in nr.get("candidates", []):
        lab = c.get("name") or c.get("label")
        if lab:
            g = _nr4a3_dG(c)
            if g is not None:
                nr3[lab] = g

    print(f"anti-target panel: {panel}")
    print(f"NR4A3 dock dG source: s3://{bucket}/{nr_prefix}/{nr_key} ({len(nr3)} drugs)\n")
    rows = []
    for c in at.get("candidates", []):
        lab = c["label"]
        dgs = {t: v for t, v in c.get("dG_by_target", {}).items() if v is not None}
        if not dgs:
            continue
        nr3dg = nr3.get(lab)
        best_off = min(dgs.values())
        best_off_t = min(dgs, key=lambda t: dgs[t])
        gap = (best_off - nr3dg) if nr3dg is not None else None
        within2 = sum(1 for v in dgs.values() if nr3dg is not None and v <= nr3dg + 2)
        sens = [t for t in dgs if t in sensors and nr3dg is not None and dgs[t] <= nr3dg + 2]
        rows.append({"lab": lab, "nr3": nr3dg, "best_off": best_off, "best_off_t": best_off_t,
                     "gap": gap, "within2": within2, "sensors": sens, "dgs": dgs})
    # most selective (largest positive gap) first; unknown-NR4A3 last
    rows.sort(key=lambda r: (r["gap"] is None, -(r["gap"] if r["gap"] is not None else 0)))

    print(f"{'drug':<16} {'NR4A3':>7} {'bestOff':>8} {'(which)':>9} {'gap':>6} {'#<=+2':>6} {'sensors':>9}  verdict")
    for r in rows:
        nr3 = f"{r['nr3']:>7.2f}" if r["nr3"] is not None else "    n/a"
        gap = f"{r['gap']:>+6.2f}" if r["gap"] is not None else "   n/a"
        if r["gap"] is None:
            verdict = "no NR4A3 ref"
        elif r["gap"] >= 2 and r["within2"] == 0:
            verdict = "family-selective"
        elif r["gap"] >= 2:
            verdict = f"selective-ish ({r['within2']} near)"
        elif r["gap"] > -1:
            verdict = "borderline/promiscuous"
        else:
            verdict = "PROMISCUOUS (off-target tighter)"
        print(f"{r['lab'][:16]:<16} {nr3} {r['best_off']:>8.2f} {r['best_off_t']:>9} {gap} "
              f"{r['within2']:>6} {','.join(r['sensors'])[:9]:>9}  {verdict}")
    print("\ngap = best_offtarget_dG - NR4A3_dG (kcal/mol; smina, same protocol). Docking dG noise is ~1-2 "
          "kcal, so treat |gap| < 2 as within noise. '#<=+2' = panel targets binding within 2 kcal of NR4A3; "
          "'sensors' = PXR/HSA (promiscuity flags) doing so. Screening-grade; not a substitute for a wet-lab "
          "selectivity panel.")


if __name__ == "__main__":
    main()
