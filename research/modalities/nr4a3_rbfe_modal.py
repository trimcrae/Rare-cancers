#!/usr/bin/env python3
"""Modal GPU runner for the STEP-1 cmpd19 congeneric-RBFE PILOT (RUNG 2, step1_pilot_cmpd19).

Runs the SAME OpenFE RBFE engine the AWS/GCP lanes drive (nr4a3_rbfe.py) — the pilot edge
`e_zaienne_cmpd19__cw_ev_5nh2` (methyl 5-Br-indole-3-carboxylate → 5-NH2 analogue, a clean single-site
Br→NH2 perturbation, both endpoints in rbfe_edges.SMILES) on ONE nr4a3_design druggable frame — but on a
Modal serverless GPU so the ~$30 pilot burns Modal free credits instead of AWS. State (per-window checkpoints
+ leg results) lives in the existing S3 bucket (object_store bridge), so a container drop never loses work and
a re-invocation RESUMES.

Two modes (mirrors the GCP lane's tiny/real split):
  tiny  — MODE=splittest RBFE_TINY=1: setup → 2.5ps/10ps MD → analyze on the REAL cmpd19 complex edge. The
          plumbing shakeout: proves the openfe env solves on Modal, CUDA MD runs, the S3 stage resolves both
          poses + the receptor, and the LOMAP map + hybrid-topology build succeed. Minutes, ~$0.05.
  real  — MODE=splittest RBFE_TINY=0: full 5ns × N-window sampling, ONE leg per call (leg=complex|solvent),
          spot-safe S3 checkpoint/resume, idempotent-skip if the leg JSON is already in S3. leg=reduce
          combines both → ΔΔG_bind + the pilot abort-gate readout.

HONESTY: no ΔΔG/affinity/GPU-hour asserted here; the pilot asks only "can a congeneric RBFE converge on this
dynamic cryptic pocket without the pocket collapsing?" (rbfe_pilot.py). Inputs are staged from the congeneric
DOCKING output in S3; nothing is fabricated — a missing pose/receptor makes the stage exit loudly.

Driven by .github/workflows/modal-rbfe.yml (AWS creds → a Modal Secret; the smoke runs free on push).
"""
import os

import modal

app = modal.App("nr4a3-rbfe-pilot")

# openfe stack via micromamba (conda-forge CUDA openmm, driver-matched) — mirrors the GCP lane's 'rbfe' env so
# the two providers run byte-identical science. Modal caches this image build (the ~10-min solve runs once).
image = (
    modal.Image.micromamba(python_version="3.11")
    .micromamba_install(
        "openfe>=1.12", "pydantic>=2", "importlib_resources", "openff-toolkit",
        "ambertools>=23", "openmmforcefields", "openff-nagl", "openff-nagl-models",
        "cuda-version=12.6", "rdkit", "lomap2", "kartograf", "numpy", "scipy",
        "pyyaml", "netcdf4", "boto3", "git",
        channels=["conda-forge"],
    )
)

REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
BUCKET = os.environ.get("S3_BUCKET", "sagemaker-us-east-2-646605541856")
GIT_REF = os.environ.get("GIT_REF", "claude/rung-2-parallel-7asnpk")
# The congeneric docking output prefix (nr4a3-opened.pdb + _pose_<lig>.sdf); the step1 receptor + poses source.
DOCK_PREFIX = os.environ.get("DOCK_PREFIX", "nr4a3-congeneric-dock/congeneric-poses2-ckpt")
LIGAND_A = os.environ.get("LIGAND_A", "zaienne_cmpd19")   # 5-Br anchor
LIGAND_B = os.environ.get("LIGAND_B", "cw_ev_5nh2")       # 5-NH2 analogue
RECEPTOR = os.environ.get("RECEPTOR", "nr4a3")
CKPT_PREFIX = os.environ.get("CKPT_PREFIX", "nr4a3-step1-pilot-rbfe")

_aws = modal.Secret.from_dict({
    "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", ""),
    "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
    "AWS_DEFAULT_REGION": REGION,
})


def _stage_inputs(bucket: str, dock_prefix: str, receptor: str, lig_a: str, lig_b: str, dest: str):
    """Assemble the RBFE input tree (dest/receptor/<r>-opened.pdb + dest/ligand/docked_<r>.sdf) from the S3
    docking output. Reuses the tested stage-mode contract; writes LOCAL files for the Modal run. Exits loudly
    (no fabrication) if a pose or the receptor is missing — the smoke surfaces the real S3 layout."""
    import glob as _g  # noqa: F401
    import boto3

    s3 = boto3.client("s3")
    keys, tok = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": dock_prefix.rstrip("/") + "/"}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        keys += [o["Key"] for o in r.get("Contents", [])]
        if not r.get("IsTruncated"):
            break
        tok = r["NextContinuationToken"]
    print(f"[stage] {len(keys)} objs under s3://{bucket}/{dock_prefix}/", flush=True)

    def _find(suffix):
        m = [k for k in keys if k.endswith(suffix)]
        return m[0] if m else None

    pdb_key = _find(f"{receptor}-opened.pdb") or _find("-opened.pdb")
    pose_a = _find(f"_pose_{lig_a}.sdf")
    pose_b = _find(f"_pose_{lig_b}.sdf")
    if not (pdb_key and pose_a and pose_b):
        print("[stage] KEYS:", *keys, sep="\n  ")
        raise SystemExit(f"[stage] missing inputs: pdb={pdb_key} poseA={pose_a} poseB={pose_b} "
                         f"(dock_prefix={dock_prefix}, ligands={lig_a},{lig_b})")

    def _get(k):
        return s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode("utf-8", "replace")

    os.makedirs(os.path.join(dest, "receptor"), exist_ok=True)
    os.makedirs(os.path.join(dest, "ligand"), exist_ok=True)
    with open(os.path.join(dest, "receptor", f"{receptor}-opened.pdb"), "w") as f:
        f.write(_get(pdb_key))

    # Combine the two docked poses into one SDF via RDKit (robust: raw-text $$$$ splicing produced a malformed
    # 2nd record — RDKit round-trips valid molblocks + sets the _Name the engine resolves by). Keep 3D coords.
    import io as _io

    from rdkit import Chem

    def _first_mol(sdf_text: str, name: str):
        supplier = Chem.ForwardSDMolSupplier(_io.BytesIO(sdf_text.encode()), sanitize=False, removeHs=False)
        for mol in supplier:
            if mol is not None:
                mol.SetProp("_Name", name)
                return mol
        raise SystemExit(f"[stage] RDKit could not read a molecule from pose SDF for {name}")

    out_sdf = os.path.join(dest, "ligand", f"docked_{receptor}.sdf")
    w = Chem.SDWriter(out_sdf)
    for pose_key, name in ((pose_a, lig_a), (pose_b, lig_b)):
        w.write(_first_mol(_get(pose_key), name))
    w.close()
    # confirm both records are present + named, so a staging defect fails HERE (loudly), not mid-RBFE
    names = [m.GetProp("_Name") for m in Chem.SDMolSupplier(out_sdf, sanitize=False) if m is not None]
    if lig_a not in names or lig_b not in names:
        raise SystemExit(f"[stage] combined SDF missing an endpoint: wrote {names}, need {lig_a},{lig_b}")
    print(f"[stage] staged receptor {pdb_key} + poses {names} -> {dest}", flush=True)


def _run_leg(mode: str, leg: str, tiny: bool, n_windows: int) -> str:
    """Clone the repo, stage inputs from S3, run one RBFE leg (or reduce) via nr4a3_rbfe.py, return the result
    line. Uploads leg/ddg JSON + spot checkpoints to S3 (resume-safe)."""
    import subprocess
    import sys

    import boto3

    s3 = boto3.client("s3")
    results_prefix = f"{CKPT_PREFIX}/results"
    leg_key = f"{results_prefix}/leg_{RECEPTOR}_{leg}.json"

    # idempotent cross-invocation skip: a completed real leg already in S3 is not recomputed
    if mode == "real" and leg in ("complex", "solvent"):
        try:
            s3.head_object(Bucket=BUCKET, Key=leg_key)
            print(f"[modal-rbfe] leg {leg} already in S3 — idempotent skip", flush=True)
            return f"RBFE_RESULT status=OK leg={leg} (idempotent-skip, already in S3)"
        except Exception:  # noqa: BLE001 — not present → run it
            pass

    subprocess.run(["git", "clone", "--depth", "1", "--branch", GIT_REF,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"
    in_dir, out_dir = "/tmp/rbfe_in", "/tmp/rbfe_out"
    os.makedirs(out_dir, exist_ok=True)

    env = os.environ.copy()
    env.update({
        "MODE": "reduce" if leg == "reduce" else "splittest",
        "RBFE_TINY": "1" if tiny else "0",
        "RECEPTOR": RECEPTOR, "LEG": leg, "LIGAND_A": LIGAND_A, "LIGAND_B": LIGAND_B,
        "N_WINDOWS": str(n_windows), "OPENMM_REQUIRE_CUDA": "0" if tiny else "1",
        "INPUT_DIR": in_dir, "OUTPUT_DIR": out_dir, "CKPT_DIR": out_dir,
        # ensure the conda env's bin is on PATH so openff-toolkit finds antechamber/sqm (am1bcc)
        "PATH": f"/opt/conda/bin:{env.get('PATH','')}",
    })
    if mode == "real":
        env["RBFE_SPOT_SAFE"] = "1"
        env["RBFE_SPOT_COMMIT_S3"] = f"s3://{BUCKET}/{CKPT_PREFIX}/{leg}"
        env["RBFE_WARMUP_CKPT_ITERS"] = "20"
        env["RBFE_PROD_CKPT_ITERS"] = "40"

    if leg != "reduce":
        _stage_inputs(BUCKET, DOCK_PREFIX, RECEPTOR, LIGAND_A, LIGAND_B, in_dir)
    else:
        # reduce: pull both leg JSONs from S3 into out_dir
        for L in ("complex", "solvent"):
            try:
                body = s3.get_object(Bucket=BUCKET, Key=f"{results_prefix}/leg_{RECEPTOR}_{L}.json")["Body"].read()
                with open(os.path.join(out_dir, f"leg_{RECEPTOR}_{L}.json"), "wb") as f:
                    f.write(body)
            except Exception as e:  # noqa: BLE001
                print(f"[reduce] MISSING leg {L} in S3: {e}", flush=True)

    print(f"[modal-rbfe] running mode={mode} leg={leg} tiny={tiny} A={LIGAND_A} B={LIGAND_B}", flush=True)
    r = subprocess.run([sys.executable, "nr4a3_rbfe.py"], cwd=work, env=env)
    print(f"[modal-rbfe] nr4a3_rbfe.py exit={r.returncode}", flush=True)

    # upload result JSONs to S3
    import json
    line = f"RBFE_RESULT status=NORESULT leg={leg} exit={r.returncode}"
    leg_json = os.path.join(out_dir, f"leg_{RECEPTOR}_{leg}.json")
    ddg_json = os.path.join(out_dir, f"ddg_{RECEPTOR}.json")
    if leg == "reduce" and os.path.exists(ddg_json):
        d = json.load(open(ddg_json))
        s3.upload_file(ddg_json, BUCKET, f"{results_prefix}/ddg_{RECEPTOR}.json")
        line = f"RBFE_RESULT status=OK reduce ddg_bind={d.get('ddg_bind_kcal')}"
    elif os.path.exists(leg_json):
        d = json.load(open(leg_json))
        if mode == "real":
            s3.upload_file(leg_json, BUCKET, leg_key)
        line = (f"RBFE_RESULT status=OK leg={d.get('leg')} dg_morph={d.get('dg_morph_kcal')} "
                f"unc={d.get('unc_kcal')} mapped={d.get('n_mapped_atoms')} via={d.get('via')}")
    smoke_json = os.path.join(out_dir, "smoke.json")
    if tiny and os.path.exists(smoke_json):
        line += " | smoke=" + json.dumps(json.load(open(smoke_json)))
    print(f"###RBFERESULT### {line} ###END###", flush=True)
    return line


@app.function(image=image, gpu="L4", secrets=[_aws], timeout=60 * 30)
def tiny_shakeout(leg: str = "complex", n_windows: int = 12) -> str:
    """FREE plumbing shakeout: setup → tiny MD → analyze on the real cmpd19 edge (RBFE_TINY=1)."""
    return _run_leg("tiny", leg, tiny=True, n_windows=n_windows)


@app.function(image=image, gpu="L4", secrets=[_aws], timeout=60 * 60 * 20)
def real_leg(leg: str = "complex", n_windows: int = 12) -> str:
    """The paid pilot: full-sampling RBFE, one leg, spot-safe S3 checkpoint/resume."""
    return _run_leg("real", leg, tiny=False, n_windows=n_windows)


@app.function(image=image, gpu=None, cpu=2, secrets=[_aws], timeout=60 * 20)
def reduce() -> str:
    """CPU reduce: combine complex+solvent legs → ΔΔG_bind + pilot readout."""
    return _run_leg("real", "reduce", tiny=False, n_windows=12)


@app.local_entrypoint()
def main(mode: str = "tiny", leg: str = "complex", n_windows: int = 12):
    """mode=tiny (free shakeout) | real (paid leg; leg=complex|solvent) | reduce."""
    if mode == "tiny":
        print("[modal-rbfe] tiny shakeout:", tiny_shakeout.remote(leg, n_windows))
    elif mode == "real":
        print(f"[modal-rbfe] real leg={leg}:", real_leg.remote(leg, n_windows))
    elif mode == "reduce":
        print("[modal-rbfe] reduce:", reduce.remote())
    else:
        raise SystemExit(f"unknown mode {mode}")
