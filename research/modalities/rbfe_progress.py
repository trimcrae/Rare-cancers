#!/usr/bin/env python3
"""Live progress snapshot for the running OpenFE RBFE edge (401 -> lo_m0_NCCO).

Unlike the hand-rolled ABFE run (which appended per-iteration reduced potentials we could plot directly),
OpenFE writes its own artifacts per leg into s3://<bucket>/<tag>/ckpt/<leg>/shared/shared_<unit>_attempt_0/:
  - simulation_real_time_analysis.yaml  (written DURING the run — the live MBAR ΔG estimate + iteration)
  - forward_reverse_convergence.png     (OpenFE's own convergence diagnostic, at analysis time)
  - mbar_overlap_matrix.png / replica_exchange_matrix.png / ...
and, at leg completion, <leg>/leg_<receptor>_<leg>.json  (final ΔG_morph).

This script (run on the CI runner, has AWS creds) reads those, downloads OpenFE's convergence PNGs verbatim,
parses the real-time YAML for a live per-leg ΔG, renders a compact SUMMARY png (per-leg status + ΔG +
running ΔΔG_bind = ΔG_complex - ΔG_solvent per receptor), and writes everything to research/modalities/ for
the workflow to publish to the modalities-cache branch. No SageMaker, no MBAR here — just harvest + summarise,
so it updates meaningfully every hour even mid-run.
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

    state = {}  # leg -> dict(status, dg, unc, it, conv_png)
    for leg in LEGS:
        st = {"status": "not started", "dg": None, "unc": None, "it": None, "conv": None, "last": lastmod.get(leg)}
        ks = keys[leg]
        legjson = [k for k in ks if k.endswith(".json") and "/leg_" in k]
        if legjson:
            try:
                d = json.loads(s3.get_object(Bucket=bucket, Key=legjson[0])["Body"].read())
                st["status"], st["dg"], st["unc"] = "DONE", d.get("dg_morph_kcal"), d.get("unc_kcal")
            except Exception:
                pass
        # newest unit dir with real-time yaml / convergence png (mid-run live signal)
        yamls = sorted([k for k in ks if k.endswith("simulation_real_time_analysis.yaml")])
        if yamls:
            try:
                txt = s3.get_object(Bucket=bucket, Key=yamls[-1])["Body"].read().decode("utf-8", "replace")
                dg, it = _live_dg_from_yaml(txt)
                st["it"] = it
                if st["dg"] is None:
                    st["dg"] = dg
                if st["status"] != "DONE":
                    st["status"] = "running"
            except Exception:
                pass
        elif st["status"] != "DONE" and ks:
            st["status"] = "starting"          # unit dir exists (db.json/pdb) but no analysis yet
        convs = [k for k in ks if k.endswith("forward_reverse_convergence.png")]
        if convs:
            try:
                png = s3.get_object(Bucket=bucket, Key=sorted(convs)[-1])["Body"].read()
                out = os.path.join(OUTDIR, f"rbfe_conv_{leg}.png")
                open(out, "wb").write(png)
                st["conv"] = out
            except Exception:
                pass
        state[leg] = st
    print("progress:", {k: {kk: vv for kk, vv in v.items() if kk != "last"} for k, v in state.items()})

    # running ΔΔG_bind per receptor = ΔG_complex_morph − ΔG_solvent_morph (only where both ΔGs exist)
    sol = state["solvent"]["dg"]
    ddg = {}
    for r in ("nr4a3", "nr4a1", "nr4a2"):
        cx = state[f"complex-{r}"]["dg"]
        if sol is not None and cx is not None:
            ddg[r] = cx - sol

    # summary figure
    fig, ax = plt.subplots(figsize=(11, 4.2))
    COL = {"DONE": "#009E73", "running": "#0072B2", "starting": "#E69F00", "not started": "#bbb"}
    y = 0
    ylabels = []
    for leg in LEGS:
        st = state[leg]
        ax.barh(y, 1.0 if st["status"] == "DONE" else (0.5 if st["status"] == "running" else
                (0.15 if st["status"] == "starting" else 0.02)), color=COL[st["status"]], alpha=0.9)
        bits = [st["status"]]
        if st["dg"] is not None:
            bits.append(f"ΔG_morph={st['dg']:.2f}" + (f"±{st['unc']:.2f}" if st.get("unc") else "") + " kcal/mol")
        if st["it"] is not None:
            bits.append(f"iter {st['it']}")
        if st["last"] is not None:
            bits.append(f"last-write {st['last'].strftime('%H:%MZ')}")
        ax.text(1.03, y, "   ".join(bits), va="center", fontsize=8.5)
        ylabels.append(leg)
        y += 1
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels, fontsize=10)
    ax.set_xlim(0, 3.2)
    ax.invert_yaxis()
    ax.set_xticks([])
    ddg_txt = "  ".join(f"{r.upper()} ΔΔG={v:+.2f}" for r, v in ddg.items()) or "ΔΔG pending (need complex legs)"
    ax.set_title(f"RBFE 401→lo_m0_NCCO progress · {stamp}\nrunning ΔΔG_bind (kcal/mol): {ddg_txt}", fontsize=10)
    for spine in ("top", "right", "bottom"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, "rbfe_progress.png"), dpi=150, bbox_inches="tight")
    print("wrote", os.path.join(OUTDIR, "rbfe_progress.png"))
    print("harvested OpenFE convergence PNGs:", [state[l]["conv"] for l in LEGS if state[l]["conv"]])


if __name__ == "__main__":
    main()
