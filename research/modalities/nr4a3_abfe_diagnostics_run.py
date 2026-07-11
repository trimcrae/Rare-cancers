#!/usr/bin/env python3
"""Driver: pull the ABFE reduced potentials from S3, run nr4a3_abfe_diagnostics, emit the SI diagnostics.

This is a **CPU, $0, in-GitHub-runner** job (no SageMaker, no GPU) — the reduced-potential jsonl for a full
complex+solvent pair is only ~10-15 MB, so the whole diagnostic is numpy+pymbar in the runner, exactly like
reduce-abfe-ci.yml. It:
  1. syncs each replicate tag's per-window jsonl + meta.json from s3://<bucket>/<tag>/ckpt/**   (jsonl+json only),
  2. computes per-leg overlap matrices / ESS tables / forward-reverse convergence, per-receptor ΔG_bind,
     the per-replicate summary + the ΔΔG contrasts, and the cross-check against the committed §4 numbers,
  3. writes results/nr4a3-abfe/diagnostics/ : overlap-matrix PNGs, convergence-trace PNGs, an ESS PNG,
     and nr4a3-abfe-diagnostics.json (ALL numbers) — which the workflow COMMITS to git (durability rule).

Env / CLI:
  TAGS         comma-sep replicate tags        (default "nr4a3-abfe,nr4a3-abfe-r2,nr4a3-abfe-r3" = r1,r2,r3)
  RECEPTORS    comma-sep receptors             (default "nr4a3,nr4a1,nr4a2")
  TARGET       selectivity reference receptor  (default "nr4a3")
  REGION       AWS region                      (default "us-east-2")
  TEMPERATURE_K                                (default 300)
  OUT_DIR      output directory                (default results/nr4a3-abfe/diagnostics)
  LOCAL_ROOT   if set, SKIP S3 and read already-synced dirs under LOCAL_ROOT/<tag>/ckpt/... (offline/testing)
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nr4a3_abfe_diagnostics as diag  # noqa: E402

TAGS = [t.strip() for t in os.environ.get("TAGS", "nr4a3-abfe,nr4a3-abfe-r2,nr4a3-abfe-r3").split(",") if t.strip()]
RECEPTORS = [r.strip() for r in os.environ.get("RECEPTORS", "nr4a3,nr4a1,nr4a2").split(",") if r.strip()]
TARGET = os.environ.get("TARGET", "nr4a3")
SOLVENT_TAG = os.environ.get("SOLVENT_TAG", "").strip()  # pull the shared solvent leg from this tag (empty = per-tag)
REGION = os.environ.get("REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-2"))
TEMPERATURE_K = float(os.environ.get("TEMPERATURE_K", "300"))
OUT_DIR = os.environ.get("OUT_DIR", os.path.join("results", "nr4a3-abfe", "diagnostics"))
LOCAL_ROOT = os.environ.get("LOCAL_ROOT", "").strip()


def tag_label(tag):
    """Replicate label from a tag: 'nr4a3-abfe' -> 'r1', 'nr4a3-abfe-r2' -> 'r2'."""
    suf = tag.rsplit("-", 1)[-1]
    return suf if (suf.startswith("r") and suf[1:].isdigit()) else "r1"


# --------------------------------------------------------------------------------------------------------------
# S3 sync (jsonl + json only) + leg-dir location
# --------------------------------------------------------------------------------------------------------------
def sync_prefix(bucket, prefix, dest):
    """Download every .jsonl/.json under an S3 prefix, preserving the relative path under dest. Returns count.
    (Skips the big .state.xml OpenMM checkpoints — the diagnostics only need the reduced-potential jsonl.)"""
    import boto3
    s3 = boto3.client("s3", region_name=REGION)
    os.makedirs(dest, exist_ok=True)
    n = 0
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for o in page.get("Contents", []):
            k = o["Key"]
            if not (k.endswith(".jsonl") or k.endswith(".json")):
                continue
            rel = k[len(prefix):]
            if not rel or k.endswith("/"):
                continue
            fp = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(fp) or ".", exist_ok=True)
            s3.download_file(bucket, k, fp)
            n += 1
    return n


def find_leg_dir(root):
    """The dir under `root` that holds window_00.jsonl (the checkpoint sync nests it as <r>/<leg>/)."""
    for w in sorted(glob.glob(os.path.join(root, "**", "window_00.jsonl"), recursive=True)):
        return os.path.dirname(w)
    # fall back to any window_*.jsonl (window 0 may be missing on a partial run)
    for w in sorted(glob.glob(os.path.join(root, "**", "window_*.jsonl"), recursive=True)):
        return os.path.dirname(w)
    return None


def read_ssc(leg_dir):
    """Boresch standard-state ΔG from a complex leg's meta.json (needed to combine into ΔG_bind)."""
    p = os.path.join(leg_dir or "", "meta.json")
    if leg_dir and os.path.exists(p):
        try:
            return json.load(open(p)).get("restraint_standard_state_dg")
        except Exception:  # noqa: BLE001
            return None
    return None


def gather_dirs(bucket):
    """For each tag, return {tag: {'solvent': dir, 'complex-<r>': dir, ...}} of local leg dirs (after syncing
    from S3, or reading LOCAL_ROOT if set). Missing legs are omitted."""
    base = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "abfe-diag")
    out = {}
    for tag in TAGS:
        legs = {}
        for leg_key, prefix_sub in [("solvent", "solvent")] + [("complex-%s" % r, "complex-%s" % r) for r in RECEPTORS]:
            # The ligand-in-water solvent leg is receptor/conformer-independent, so a run that reuses a shared
            # solvent leg (e.g. the 8XTT-anchored complex legs reuse the base selectivity run's solvent) has no
            # solvent/ under its own tag. SOLVENT_TAG lets the solvent be pulled from that shared tag.
            src_tag = SOLVENT_TAG if (leg_key == "solvent" and SOLVENT_TAG) else tag
            if LOCAL_ROOT:
                root = os.path.join(LOCAL_ROOT, src_tag, "ckpt", prefix_sub)
            else:
                root = os.path.join(base, src_tag, prefix_sub)
                nsync = sync_prefix(bucket, "%s/ckpt/%s/" % (src_tag, prefix_sub), root)
                print("  [sync] %s/ckpt/%s/ -> %d files" % (src_tag, prefix_sub, nsync), flush=True)
            d = find_leg_dir(root)
            if d:
                legs[leg_key] = d
        if legs:
            out[tag] = legs
    return out


# --------------------------------------------------------------------------------------------------------------
# compute (offline-testable: takes located leg dirs, no S3)
# --------------------------------------------------------------------------------------------------------------
def _bind_convergence(cconv, sconv, ssc):
    """Combine two legs' forward/reverse ΔG traces into ΔG_bind(fraction) using combine_legs at matching
    fractions. Returns {forward:[{fraction,dg,se}], reverse:[...]} — the headline ΔG_bind convergence."""
    from nr4a3_abfe import combine_legs

    def _combine(cs, ss):
        sm = {p["fraction"]: p for p in ss}
        out = []
        for cp in cs:
            sp = sm.get(cp["fraction"]) or (ss[-1] if ss else None)
            if sp is None:
                continue
            dg, se = combine_legs(cp["dg"], cp["se"], sp["dg"], sp["se"], ssc)
            out.append({"fraction": cp["fraction"], "dg": dg, "se": se})
        return out
    return {"forward": _combine(cconv["forward"], sconv["forward"]),
            "reverse": _combine(cconv["reverse"], sconv["reverse"])}


def compute(dirs, temperature_K=TEMPERATURE_K):
    """Full diagnostics from located leg dirs {tag: {leg_key: dir}}. Returns the results dict written to JSON."""
    # K is detected PER-LEG from each checkpoint (a dense-λ REPAIR run has more windows than the default
    # schedule; a fixed global K crashed the validate gate). n_windows() is only a fallback.
    replicates = {}
    dg_bind_by_rep = {}
    K_seen = set()
    for tag, legs in dirs.items():
        rep = tag_label(tag)
        rep_out = {"tag": tag, "legs": {}, "receptors": {}}
        # load + diagnose each leg once
        we_cache, ssc_cache, K_cache = {}, {}, {}
        for leg_key, d in legs.items():
            we = diag.load_leg_we(d, K=None)          # auto-detect this leg's window count
            K = len(we) or diag.n_windows()
            K_cache[leg_key] = K
            K_seen.add(K)
            we_cache[leg_key] = we
            if leg_key.startswith("complex-"):
                ssc_cache[leg_key] = read_ssc(d)
            rep_out["legs"][leg_key] = {"dir": d, **diag.leg_diagnostics(we, temperature_K=temperature_K, K=K)}
        # per-receptor ΔG_bind + bind convergence (needs the shared solvent leg)
        swe = we_cache.get("solvent")
        for r in RECEPTORS:
            ck = "complex-%s" % r
            if ck not in we_cache or swe is None:
                continue
            ssc = ssc_cache.get(ck)
            if ssc is None:
                rep_out["receptors"][r] = {"error": "no restraint_standard_state_dg in complex meta.json"}
                continue
            # complex and solvent legs must share a window count for the combined ΔG_bind; use the complex
            # leg's detected K (solvent should match).
            K = K_cache.get(ck) or K_cache.get("solvent") or diag.n_windows()
            rb = diag.receptor_dg_bind(we_cache[ck], swe, ssc, temperature_K=temperature_K, K=K)
            if rb is None:
                rep_out["receptors"][r] = {"error": "insufficient samples in one leg"}
                continue
            bind_conv = _bind_convergence(rep_out["legs"][ck]["convergence"],
                                          rep_out["legs"]["solvent"]["convergence"], ssc)
            rep_out["receptors"][r] = {**rb, "bind_convergence": bind_conv}
            dg_bind_by_rep.setdefault(rep, {})[r] = rb["dg_bind"]
        replicates[tag] = rep_out

    summary = diag.per_replicate_summary(dg_bind_by_rep, target=TARGET) if dg_bind_by_rep else None
    check = diag.check_against_manuscript(summary) if summary else None
    return {
        "provenance": {"tags": TAGS, "receptors": RECEPTORS, "target": TARGET,
                       "solvent_tag": SOLVENT_TAG or None,
                       "temperature_K": temperature_K, "n_windows": sorted(K_seen) or [diag.n_windows()],
                       "engine": "research/modalities/nr4a3_abfe.py",
                       "diagnostics": "research/modalities/nr4a3_abfe_diagnostics.py",
                       "note": "Recomputed from the ABFE per-window reduced potentials (dedup-by-iteration, "
                               "same MBAR as the §4 reducer). Overlap/ESS via pymbar; ΔΔG offset-invariant."},
        "manuscript_s4": diag.MANUSCRIPT_S4,
        "per_replicate_dg_bind": dg_bind_by_rep,
        "summary": summary,
        "manuscript_consistency": check,
        "replicates": replicates,
    }


# --------------------------------------------------------------------------------------------------------------
# plots
# --------------------------------------------------------------------------------------------------------------
def render_plots(results, out_dir):
    """Overlap-matrix, convergence-trace and ESS PNGs per replicate. Returns the list of files written."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    written = []
    for tag, rep in results["replicates"].items():
        label = tag_label(tag)
        leg_keys = [k for k in (["complex-%s" % r for r in RECEPTORS] + ["solvent"]) if k in rep["legs"]]
        leg_keys = [k for k in leg_keys if not rep["legs"][k].get("empty")]
        if not leg_keys:
            continue

        # --- overlap heatmaps (one panel per leg) ---
        fig, axes = plt.subplots(1, len(leg_keys), figsize=(3.2 * len(leg_keys), 3.4), squeeze=False)
        for ax, lk in zip(axes[0], leg_keys):
            ov = np.array(rep["legs"][lk]["overlap_matrix"])
            im = ax.imshow(ov, cmap="viridis", vmin=0, vmax=max(0.3, ov.max()), origin="upper")
            madj = rep["legs"][lk]["min_adjacent_overlap"]
            ax.set_title("%s\nmin adj overlap %.3f" % (lk, madj if madj is not None else float("nan")), fontsize=8)
            ax.set_xlabel("λ state"); ax.set_ylabel("λ state")
            ax.set_xticks(range(ov.shape[0])); ax.set_yticks(range(ov.shape[0]))
            ax.tick_params(labelsize=6)
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.suptitle("denovo_401 ABFE — MBAR λ-overlap (%s / %s)" % (label, tag), fontsize=10)
        fig.tight_layout()
        p = os.path.join(out_dir, "overlap_%s.png" % tag)
        fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig); written.append(p)

        # --- forward/reverse ΔG_bind convergence (one line-pair per receptor) ---
        recs = [r for r in RECEPTORS if r in rep["receptors"] and "bind_convergence" in rep["receptors"][r]]
        if recs:
            fig, ax = plt.subplots(figsize=(6.5, 4.2))
            colors = {"nr4a3": "#0072B2", "nr4a1": "#D55E00", "nr4a2": "#009E73"}
            for r in recs:
                bc = rep["receptors"][r]["bind_convergence"]
                fx = [p["fraction"] for p in bc["forward"]]; fy = [p["dg"] for p in bc["forward"]]
                fe = [p["se"] for p in bc["forward"]]
                rx = [p["fraction"] for p in bc["reverse"]]; ry = [p["dg"] for p in bc["reverse"]]
                c = colors.get(r, "#888")
                ax.errorbar(fx, fy, yerr=fe, color=c, marker="o", ms=3, lw=1.3, capsize=2,
                            label="%s forward" % r.upper())
                ax.plot(rx, ry, color=c, marker="s", ms=3, lw=1.3, ls="--", alpha=0.7,
                        label="%s reverse" % r.upper())
            ax.set_xlabel("fraction of samples (forward = first f, reverse = last f)")
            ax.set_ylabel("ΔG_bind (kcal/mol, raw engine)")
            ax.set_title("denovo_401 ABFE — forward/reverse convergence (%s)" % label, fontsize=10)
            ax.grid(alpha=0.25); ax.legend(fontsize=7, ncol=len(recs))
            fig.tight_layout()
            p = os.path.join(out_dir, "convergence_%s.png" % tag)
            fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig); written.append(p)

        # --- ESS per window per leg ---
        fig, ax = plt.subplots(figsize=(7, 4))
        width = 0.8 / max(len(leg_keys), 1)
        for i, lk in enumerate(leg_keys):
            ess = rep["legs"][lk]["ess"]
            xs = np.arange(len(ess)) + i * width
            ax.bar(xs, [e["ess_autocorr"] for e in ess], width=width, label=lk, alpha=0.85)
        ax.set_xlabel("λ window"); ax.set_ylabel("autocorrelation ESS (N/g)")
        ax.set_title("denovo_401 ABFE — per-window effective sample size (%s)" % label, fontsize=10)
        ax.legend(fontsize=7); ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        p = os.path.join(out_dir, "ess_%s.png" % tag)
        fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig); written.append(p)
    return written


# --------------------------------------------------------------------------------------------------------------
def _print_summary(results):
    s = results.get("summary")
    if not s:
        print("[diag] no ΔG_bind computed (no complete complex+solvent legs found)."); return
    print("\n=== per-receptor ΔG_bind (raw engine, kcal/mol) ===")
    for rec, pr in s["per_receptor"].items():
        sd = ("± %.2f" % pr["sd"]) if pr["sd"] is not None else "(n<2)"
        print("  %-6s  %+.2f %s   (n=%d, reps: %s)" % (
            rec, pr["mean"], sd, pr["n"],
            ", ".join("%s=%+.2f" % (k, v) for k, v in pr["values"].items())))
    print("\n=== selectivity ΔΔG (ref = %s; negative ⇒ target-selective) ===" % s["target"])
    for other, dd in s["ddg"].items():
        sd = ("± %.2f" % dd["sd"]) if dd["sd"] is not None else "(n<2)"
        print("  ΔΔG(%s − %s) = %+.2f %s   unanimous=%s" % (
            s["target"], other, dd["mean"], sd, dd["direction_unanimous"]))
    chk = results.get("manuscript_consistency")
    if chk:
        print("\n=== consistency vs committed §4 (%s) ===" %
              ("CONSISTENT" if chk["consistent"] else "MISMATCH — FLAGGED"))
        for r in chk["rows"]:
            mark = "ok" if r["within_tol"] else "XX"
            got = "n/a" if r["recomputed"] is None else "%+.3f" % r["recomputed"]
            print("  [%s] %-22s recomputed %s  expected %+.3f  (Δ %s, tol %.2f)" % (
                mark, r["quantity"], got, r["expected"],
                "n/a" if r["delta"] is None else "%+.3f" % r["delta"], r["tol"]))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    bucket = ""
    if not LOCAL_ROOT:
        import boto3
        acct = boto3.client("sts", region_name=REGION).get_caller_identity()["Account"]
        bucket = "sagemaker-%s-%s" % (REGION, acct)
        print("[diag] bucket %s  tags %s  receptors %s" % (bucket, TAGS, RECEPTORS))
    dirs = gather_dirs(bucket)
    if not dirs:
        print("[diag] no leg dirs found for tags %s — nothing to do." % TAGS)
        sys.exit(1)
    results = compute(dirs)
    out_json = os.path.join(OUT_DIR, "nr4a3-abfe-diagnostics.json")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print("[diag] wrote %s" % out_json)
    try:
        pngs = render_plots(results, OUT_DIR)
        print("[diag] wrote %d PNGs: %s" % (len(pngs), [os.path.basename(p) for p in pngs]))
    except Exception as e:  # noqa: BLE001 — plotting must not lose the JSON
        print("[diag] plotting failed (JSON still written): %s" % e)
    _print_summary(results)


if __name__ == "__main__":
    main()
