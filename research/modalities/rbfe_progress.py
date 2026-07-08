#!/usr/bin/env python3
"""Live progress-bar snapshot for the running OpenFE RBFE edge (401 -> lo_m0_NCCO).

OpenFE writes its own artifacts per leg into s3://<bucket>/<tag>/ckpt/<leg>/shared/shared_<unit>_attempt_0/:
  - simulation_real_time_analysis.yaml  (written DURING the run — carries the live iteration count)
and, at leg completion, <leg>/leg_<receptor>_<leg>.json  (final leg result → leg is DONE).

This script (run on the CI runner, has AWS creds) reads those and renders a plain per-leg PROGRESS-BAR png:
each leg's bar = % of target production iterations (n_iter), plus its status + live iteration + last-write.
NO ΔG / ΔΔG numbers and NO convergence plot (trimcrae: progress bars only) — the ΔΔG_bind + selectivity
come from mode=reduce once the legs finish. No SageMaker, no MBAR here — just harvest + render, so it updates
meaningfully every hour even mid-run.
"""
import io
import json
import os
import datetime

import boto3

TAG = os.environ.get("RBFE_TAG", "nr4a3-rbfe-401-nccogen")
OUTDIR = os.environ.get("OUTDIR", "research/modalities")
LEGS = ["solvent", "complex-nr4a3", "complex-nr4a1", "complex-nr4a2"]
os.makedirs(OUTDIR, exist_ok=True)


def _bucket():
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    return f"sagemaker-{region}-{boto3.client('sts').get_caller_identity()['Account']}"


def _live_dg_from_yaml(text):
    """Best-effort extract (last iteration's) MBAR free energy (kcal/mol) + iteration from OpenFE's real-time
    analysis yaml. Schema varies by version, so walk the parsed structure for free-energy / iteration fields
    rather than assume exact keys. Returns (dg_kcal_or_None, iteration_or_None)."""
    try:
        import yaml
        doc = yaml.safe_load(text)
    except Exception:
        return None, None
    KT_KCAL = 0.5924  # kT at 298 K in kcal/mol (only used if the value is reported in kT)
    entries = doc if isinstance(doc, list) else [doc]
    dg = it = None
    for e in entries:  # take the LAST entry that carries a free energy
        if not isinstance(e, dict):
            continue
        flat = {}

        def _walk(d, pfx=""):
            for k, v in d.items():
                if isinstance(v, dict):
                    _walk(v, f"{pfx}{k}.")
                else:
                    flat[f"{pfx}{k}"] = v
        _walk(e)
        for k, v in flat.items():
            lk = k.lower()
            if "free_energy" in lk and isinstance(v, (int, float)):
                dg = float(v) * (KT_KCAL if "kt" in lk else 1.0)
            if ("iteration" in lk or lk.endswith("n_iterations")) and isinstance(v, (int, float)):
                it = int(v)
    return dg, it


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s3 = boto3.client("s3")
    bucket = _bucket()
    stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    keys = {leg: [] for leg in LEGS}
    lastmod = {}
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=f"{TAG}/ckpt/"):
        for o in page.get("Contents", []):
            rest = o["Key"].split(f"{TAG}/ckpt/", 1)[1]
            leg = rest.split("/", 1)[0]
            if leg in keys:
                keys[leg].append(o["Key"])
                lastmod[leg] = max(lastmod.get(leg, o["LastModified"]), o["LastModified"])

    target = int(os.environ.get("N_ITER", "1000"))  # target production iterations per leg (full bar)
    state = {}  # leg -> dict(status, it, pct, last)
    for leg in LEGS:
        st = {"status": "not started", "it": None, "pct": 0.0, "last": lastmod.get(leg)}
        ks = keys[leg]
        legjson = [k for k in ks if k.endswith(".json") and "/leg_" in k]
        if legjson:
            st["status"], st["pct"] = "DONE", 100.0     # final leg json exists → leg finished
        # newest unit dir's real-time yaml carries the live iteration count (mid-run progress signal)
        yamls = sorted([k for k in ks if k.endswith("simulation_real_time_analysis.yaml")])
        if yamls:
            try:
                txt = s3.get_object(Bucket=bucket, Key=yamls[-1])["Body"].read().decode("utf-8", "replace")
                _, it = _live_dg_from_yaml(txt)
                st["it"] = it
                if st["status"] != "DONE":
                    st["status"] = "running"
                    if it is not None:
                        st["pct"] = max(1.0, min(100.0, 100.0 * it / target))  # real % of target iterations
                    else:
                        st["pct"] = 5.0                 # running but no iteration reported yet
            except Exception:
                pass
        elif st["status"] != "DONE" and ks:
            st["status"] = "starting"                    # unit dir exists (db.json/pdb) but no analysis yet
            st["pct"] = 2.0
        state[leg] = st
    print("progress:", {k: {kk: vv for kk, vv in v.items() if kk != "last"} for k, v in state.items()})

    # progress-bar figure — per-leg % of target iterations, no ΔG / ΔΔG (trimcrae: bars only)
    fig, ax = plt.subplots(figsize=(11, 3.6))
    COL = {"DONE": "#009E73", "running": "#0072B2", "starting": "#E69F00", "not started": "#bbb"}
    y = 0
    ylabels = []
    for leg in LEGS:
        st = state[leg]
        ax.barh(y, st["pct"], color=COL[st["status"]], alpha=0.9)
        bits = [f"{st['pct']:.0f}%", st["status"]]
        if st["it"] is not None:
            bits.append(f"iter {st['it']}/{target}")
        if st["last"] is not None:
            bits.append(f"last-write {st['last'].strftime('%H:%MZ')}")
        ax.text(min(st["pct"] + 1.5, 101), y, "   ".join(bits), va="center", fontsize=8.5)
        ylabels.append(leg)
        y += 1
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels, fontsize=10)
    ax.set_xlim(0, 118)
    ax.invert_yaxis()
    ax.axvline(100, color="#666", ls="--", lw=1)
    ax.set_xlabel(f"leg progress — % of target production iterations (n_iter={target})")
    ax.set_title(f"RBFE 401→lo_m0_NCCO — leg progress · {stamp}", fontsize=11)
    ax.grid(axis="x", alpha=0.2)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, "rbfe_progress.png"), dpi=150, bbox_inches="tight")
    print("wrote", os.path.join(OUTDIR, "rbfe_progress.png"))


if __name__ == "__main__":
    main()
