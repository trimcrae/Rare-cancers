#!/usr/bin/env python3
"""Repurposing selectivity tier — plan the sharded MM-GBSA, then pool it into the two shortlists.

Two modes (env MODE):
  PLAN   : read the promoted top-N candidate JSON (s3://<bucket>/<PROMOTE_PREFIX>/nr4a3-denovo.json), split
           its labels into N_SHARDS groups, and print each group as a ready-to-paste CANDIDATE_FILTER string.
           Use these to fire N parallel spot-g5 MM-GBSA jobs (one per group) at once.
  REPORT : pool the per-shard MM-GBSA outputs (SHARD_PREFIXES, comma list) and emit the two deliverable
           shortlists — NR4A3-SELECTIVE (systemic EMC degrader) and PAN-NR4A (CAR-T) — with honest caveats.

MM-GBSA magnitudes are inflated (single-snapshot, no entropy) — trust verdict/direction, not kcal/mol.
Env: BUCKET (optional), AWS creds + AWS_DEFAULT_REGION.
  PLAN: PROMOTE_PREFIX (default nr4a3-repurpose-top), N_SHARDS (default 5).
  REPORT: SHARD_PREFIXES (comma), PAN_CUTOFF (default -6.0), PAN_MARGIN (default 3.0), TOP (default 30).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selectivity_calibration as sc  # noqa: E402


def _s3():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    return s3, bucket


def _get_json(s3, bucket, key):
    try:
        return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except Exception as e:  # noqa: BLE001
        print(f"  (could not read s3://{bucket}/{key}: {e})")
        return None


def plan():
    s3, bucket = _s3()
    prefix = os.environ.get("PROMOTE_PREFIX", "nr4a3-repurpose-top")
    n = int(os.environ.get("N_SHARDS", "5"))
    d = _get_json(s3, bucket, f"{prefix}/nr4a3-denovo.json")
    if not d:
        sys.exit(1)
    labels = [c["name"] for c in d.get("candidates", []) if c.get("name")]
    # Only the top-N the 3-receptor dock actually docked have poses to MM-GBSA (default 100, = the dock's
    # top_n). The promoted JSON is ranked best-first, so the docked set is labels[:limit].
    limit = int(os.environ.get("PLAN_LIMIT", "100"))
    labels = labels[:limit]
    print(f"partitioning top {len(labels)} docked candidates -> {n} shards\n")
    # round-robin so each shard spans the dG range (balanced work, not front-loaded).
    groups = [labels[i::n] for i in range(n)]
    for i, g in enumerate(groups):
        print(f"# shard {i} ({len(g)} drugs) — mmgbsa-aws.yml candidate_filter + output_prefix=nr4a3-repurpose-mmgbsa-s{i}")
        print(",".join(g))
        print()


def _cell(dg):
    """Coarse MM-GBSA cell from the three ΔG (favorable = engaged). Returns (engaged_set, min_margin)."""
    return {t: v for t, v in dg.items() if v is not None}


def report():
    s3, bucket = _s3()
    prefixes = [p.strip() for p in os.environ.get("SHARD_PREFIXES", "").split(",") if p.strip()]
    pan_cutoff = float(os.environ.get("PAN_CUTOFF", "-6.0"))
    pan_margin = float(os.environ.get("PAN_MARGIN", "3.0"))
    top = int(os.environ.get("TOP", "30"))
    rows = []
    for p in prefixes:
        d = _get_json(s3, bucket, f"{p}/nr4a3-mmgbsa.json")
        if d:
            rows.extend(d.get("candidates", []))
    print(f"pooled {len(rows)} MM-GBSA-scored drugs from {len(prefixes)} shard(s)\n")
    if not rows:
        return

    # MULTI-SNAPSHOT DE-NOISING view: if rows carry mm_min_margin_sd, the margin is an MD ensemble mean±SD.
    # Survivor = margin − SD > 0 (the selectivity margin is positive beyond its noise, as denovo_401 held at
    # +12.83 ± 2.98 → margin−SD +9.85); collapse = margin − SD ≤ 0 (as denovo_393 fell +18.34 → −2.95).
    ms_rows = [r for r in rows if r.get("mm_min_margin_sd") is not None and r.get("mm_min_margin") is not None]
    if ms_rows:
        for r in ms_rows:
            r["_msd"] = round(r["mm_min_margin"] - r["mm_min_margin_sd"], 2)
        ms_rows.sort(key=lambda r: -r["_msd"])
        print(f"=== MULTI-SNAPSHOT DE-NOISING ({len(ms_rows)}) — survivor = mean−SD > 0 ===")
        print(f"{'drug':<28} {'mean':>7} {'SD':>6} {'mean-SD':>8}  outcome")
        for r in ms_rows:
            lab = (r.get("drug") or r.get("label") or "")[:28]
            out = "SURVIVES" if r["_msd"] > 0 else "collapsed"
            print(f"{lab:<28} {r['mm_min_margin']:>7} {r['mm_min_margin_sd']:>6} {r['_msd']:>8}  {out}")
        print("(reference: denovo_401 held mean−SD +9.85; denovo_393 collapsed to −2.95 ± 3.65)\n")

    def dg(r, t):
        return (r.get("dG_mmgbsa") or {}).get(t)

    # ---- Decoy-calibrated readout (the ONLY honest selectivity call) ----------------------------------
    # The raw `confirmed_selective` verdict is non-specific: ~39% of non-NR4A decoys earn it (a systematic
    # NR4A3-frame bias), so `margin > 0` means nothing. A candidate is credibly selective only if its
    # NR4A3 margin sits in the extreme right tail of the DECOY null. Load a frame-matched decoy null if
    # given (DECOY_PREFIX = an MM-GBSA output prefix run through THIS funnel); else fall back to the
    # committed 2026-06-30 null (flag: not frame-matched to this screen).
    decoy_prefix = os.environ.get("DECOY_PREFIX", "").strip()
    decoy_margins, decoy_src = [], ""
    if decoy_prefix:
        dd = _get_json(s3, bucket, f"{decoy_prefix}/nr4a3-mmgbsa.json")
        if dd:
            decoy_margins = [c.get("mm_min_margin") for c in dd.get("candidates", [])
                             if c.get("mm_min_margin") is not None]
            decoy_src = f"frame-matched ({decoy_prefix}, n={len(decoy_margins)})"
    if not decoy_margins:
        decoy_margins = list(sc.DECOY_2026_06_30)
        decoy_src = (f"committed 2026-06-30 null (n={len(decoy_margins)}) — NOT frame-matched to this "
                     f"screen; provisional")
    q = float(os.environ.get("DECOY_Q", "95"))
    thr = sc.decoy_threshold(decoy_margins, q)
    cal = sc.rank_against_null(
        [{"label": (r.get("drug") or r.get("label") or ""), "margin": r.get("mm_min_margin"),
          "verdict": r.get("verdict"), "row": r} for r in rows if r.get("mm_min_margin") is not None],
        decoy_margins, q)
    above = [c for c in cal if c.get("above_null")]
    print(f"decoy null: {decoy_src}; {q:.0f}th-pct bar = {thr:+.2f} kcal/mol (decoy max "
          f"{max(decoy_margins):+.2f})")
    print(f"=== ABOVE-NULL — decoy-calibrated NR4A3-selective (margin > {thr:+.2f}) ({len(above)}) ===")
    print(f"{'drug':<28} {'margin':>7} {'p_decoy':>8}  {'ΔG3':>7} {'ΔG1':>7} {'ΔG2':>7}")
    for c in above[:top]:
        r = c["row"]
        print(f"{c['label'][:28]:<28} {c['margin']:>7.2f} {c['decoy_frac_above']:>8.3f}  "
              f"{str(dg(r,'NR4A3')):>7} {str(dg(r,'NR4A1')):>7} {str(dg(r,'NR4A2')):>7}")
    if not above:
        print("  (none clear the null — the screen is not enriched over decoys; raw verdicts below are noise)")
    print(f"\np_decoy = fraction of decoys scoring >= this margin (empirical p-value vs the null).\n"
          f"RAW verdict counts below are UNCALIBRATED (kept for reference only).\n")

    # NR4A3-selective: the driver's own verdict (mm margin > 0 AND survives vs docking), ranked by margin.
    sel = [r for r in rows if r.get("verdict") == "confirmed_selective"]
    sel.sort(key=lambda r: -(r.get("mm_min_margin") or -99))
    # Pan-NR4A: engages ALL THREE LBDs (all ΔG favorable past PAN_CUTOFF) and is NOT strongly selective
    # (|min margin| small) — the CAR-T-relevant class. Ranked by total engagement (sum of the 3 ΔG).
    pan = [r for r in rows
           if all(dg(r, t) is not None and dg(r, t) <= pan_cutoff for t in ("NR4A3", "NR4A1", "NR4A2"))
           and abs(r.get("mm_min_margin") or 99) <= pan_margin]
    pan.sort(key=lambda r: sum(dg(r, t) for t in ("NR4A3", "NR4A1", "NR4A2")))

    def show(title, rs):
        print(f"=== {title} ({len(rs)}) ===")
        print(f"{'drug':<28} {'ΔG3':>7} {'ΔG1':>7} {'ΔG2':>7} {'min-margin':>10}  verdict")
        for r in rs[:top]:
            lab = (r.get("drug") or r.get("label") or "")[:28]
            print(f"{lab:<28} {str(dg(r,'NR4A3')):>7} {str(dg(r,'NR4A1')):>7} {str(dg(r,'NR4A2')):>7} "
                  f"{str(r.get('mm_min_margin')):>10}  {r.get('verdict')}")
        print()

    show("NR4A3-SELECTIVE (RAW verdict — UNCALIBRATED, see above-null list for the real call)", sel)
    show("PAN-NR4A  (engages all three LBDs — CAR-T angle)", pan)
    print("CAVEATS: MM-GBSA magnitudes inflated (single-snapshot, no entropy) — trust direction/verdict, not")
    print("kcal/mol. The RAW `confirmed_selective` count is non-specific (~39% of decoys earn it); the")
    print("ABOVE-NULL list is the calibrated readout. kinase-inhibitor/polyphenol hits are promiscuity-prone.")


def main():
    if os.environ.get("MODE", "REPORT").upper() == "PLAN":
        plan()
    else:
        report()


if __name__ == "__main__":
    main()
