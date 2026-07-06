#!/usr/bin/env python3
"""Fan-out submitter for the RELATIVE binding FEP (RBFE) — denovo_401 → lo_m0_NCCO, per receptor.

Mirrors nr4a3_abfe_sagemaker.py (same spot-Training + per-iteration-checkpoint + sharding plumbing) but the
legs are alchemical MORPH legs (A→B), not absolute-decoupling legs, and there is NO Boresch/standard-state
correction (both ligands share the pose → it cancels; the engine, OpenFE's RelativeHybridTopologyProtocol,
handles the hybrid topology + mapping). Deliverable: ΔΔG_bind(401→lo_m0_NCCO) per receptor →
rbfe_edges.selectivity_from_rbfe (anchored on 401's existing ABFE) + the anchor-free selectivity change.

Legs (rbfe_edges.rbfe_legs): ONE shared solvent-morph (A→B in water, cancels common-mode error) + one
complex-morph per receptor. Each leg = a managed-spot Training job of independent λ-windows, per-window
checkpointed to S3 (spot-safe). Spot draws on the 8-wide spot-Training quota.

MODE (env MODE): plan (dry-run, no spend) | smoke (one tiny spot job → validates the openfe env + spot +
checkpoint) | run (launch legs; on explicit go-ahead) | reduce (CPU → ΔΔG per receptor + selectivity).
VALIDATE-FIRST (CLAUDE.md): mode=smoke, then ONLY_LEGS=solvent (one real morph leg), then the full set.
"""
import os
import sys

import rbfe_edges as rb

TAG = os.environ.get("RBFE_TAG", "nr4a3-rbfe-401-nccogen")
MODE = os.environ.get("MODE", "plan")
INSTANCE = os.environ.get("INSTANCE", "ml.g5.xlarge")
MAX_RUN_H = float(os.environ.get("MAX_RUN_HOURS", "10"))          # RBFE morph legs are cheaper than ABFE
MAX_WAIT_H = float(os.environ.get("MAX_WAIT_HOURS", "18"))
LIGAND_A = os.environ.get("RBFE_LIGAND_A", rb.LIGAND_A)          # reference (401)
LIGAND_B = os.environ.get("RBFE_LIGAND_B", rb.LIGAND_B)          # lead (lo_m0_NCCO_gen)
GIT_REF = os.environ.get("GIT_REF", "main")
SPOT = os.environ.get("SPOT", "1") == "1"
N_ITER = os.environ.get("RBFE_N_ITER", "1000")
N_WINDOWS = os.environ.get("RBFE_N_WINDOWS", "12")               # λ-windows over the A→B morph
SEED = os.environ.get("RBFE_SEED", "0")
RECEPTORS = [r.strip() for r in os.environ.get("RBFE_RECEPTORS", "nr4a3,nr4a1,nr4a2").split(",") if r.strip()]
RECEPTOR_PREFIX = os.environ.get("RECEPTOR_PREFIX", "nr4a3-leadopt-species")   # <r>-opened.pdb + docked_<r>.sdf
SPOT_HOURLY = float(os.environ.get("SPOT_HOURLY", "0.50"))
IMAGE_URI = os.environ.get("RBFE_IMAGE_URI", "").strip()
UNIT_GPU_H = float(os.environ.get("UNIT_GPU_H", "0.5"))          # PLANNING ONLY (RBFE window < ABFE window)


def _legs():
    return rb.rbfe_legs(RECEPTORS)


def _cost_note():
    n = len(_legs())
    w = int(N_WINDOWS)
    gpu_h = n * w * UNIT_GPU_H
    return (f"{n} morph legs × {w} windows × ~{UNIT_GPU_H:g} GPU-h ≈ {gpu_h:.0f} GPU-h; legs parallel on spot → "
            f"wall ~{w * UNIT_GPU_H:.0f} h; spot ≈ ${gpu_h * SPOT_HOURLY:.0f}. RBFE is cheaper than ABFE (only "
            f"the ~4-atom acetamido morphs; the shared scaffold cancels). UNIT_GPU_H is a rough stub — "
            f"calibrate on the first leg before trusting the number.")


def main():
    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if MODE != "plan" and not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set")
    legs = _legs()
    print(f"[rbfe] TAG={TAG} mode={MODE} edge={LIGAND_A}->{LIGAND_B} spot={SPOT} receptors={RECEPTORS}")
    print(f"[rbfe] legs: {[n for n, _r, _l in legs]}")
    print(f"[rbfe] COST {_cost_note()}")

    if MODE == "plan":
        import json
        print("[rbfe] EDGE PLAN:", json.dumps(rb.edge_plan(LIGAND_A, LIGAND_B, RECEPTORS), indent=1))
        for name, receptor, leg in legs:
            print(f"  WOULD launch {TAG}-{name}: {leg}-morph leg (receptor={receptor}), {N_WINDOWS} windows, "
                  f"checkpoint s3://<bucket>/{TAG}/ckpt/{name}/")
        print("[rbfe] plan only. Re-dispatch mode=smoke (validate openfe env + spot) → ONLY_LEGS=solvent → run.")
        return

    import sagemaker
    from sagemaker.pytorch import PyTorch
    from sagemaker.inputs import TrainingInput
    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    matrix = f"s3://{bucket}/{RECEPTOR_PREFIX}/"

    def make_estimator(name, hp):
        kw = dict(
            entry_point="entry_rbfe.py", source_dir=os.path.join(here, "sagemaker_src"),
            role=role, instance_count=1, instance_type=INSTANCE, sagemaker_session=sess,
            base_job_name=f"{TAG}-{name}", use_spot_instances=SPOT,
            max_run=int(MAX_RUN_H * 3600), max_wait=int(MAX_WAIT_H * 3600) if SPOT else None,
            checkpoint_s3_uri=f"s3://{bucket}/{TAG}/ckpt/{name}/", checkpoint_local_path="/opt/ml/checkpoints",
            hyperparameters=hp)
        if IMAGE_URI:
            kw["image_uri"] = IMAGE_URI
        else:
            kw["framework_version"] = "2.3"
            kw["py_version"] = "py311"
        return PyTorch(**kw)

    common = {"git-ref": GIT_REF, "ligand-a": LIGAND_A, "ligand-b": LIGAND_B, "n-iter": N_ITER,
              "n-windows": N_WINDOWS, "seed": SEED, "prebaked": "1" if IMAGE_URI else "0"}

    if MODE == "smoke":
        est = make_estimator("smoke", {**common, "mode": "smoke"})
        print("[rbfe] launching SMOKE spot job (openfe env solve + mapping + hybrid-topology build, no MD)…")
        est.fit(wait=True, logs=True)
        print("[rbfe] SMOKE complete — openfe env solves; mapping + spot + checkpoint path works.")
        return

    only = {x.strip() for x in os.environ.get("ONLY_LEGS", "").split(",") if x.strip()} or None

    if MODE == "reduce":
        for receptor in RECEPTORS:
            if only and receptor not in only:
                continue
            est = make_estimator(f"reduce-{receptor}", {**common, "mode": "reduce", "receptor": receptor})
            est.fit({"complex": TrainingInput(f"s3://{bucket}/{TAG}/ckpt/complex-{receptor}/"),
                     "solvent": TrainingInput(f"s3://{bucket}/{TAG}/ckpt/solvent/")}, wait=False)
            print(f"[rbfe] launched reduce-{receptor}: {est.latest_training_job.name}")
        print("[rbfe] reduce jobs launched → ΔΔG_bind per receptor + rbfe_edges.selectivity_from_rbfe.")
        return

    # MODE == run
    launched = []
    for name, receptor, leg in legs:
        if only and name not in only and leg not in only and receptor not in only:
            print(f"[rbfe] skip {name} (not in ONLY_LEGS={sorted(only)})")
            continue
        est = make_estimator(name, {**common, "mode": "run", "receptor": receptor, "leg": leg})
        inputs = {"ligand": TrainingInput(matrix)}
        if leg == "complex":
            inputs["receptor"] = TrainingInput(matrix)
        try:
            est.fit(inputs, wait=False)
        except Exception as e:  # noqa: BLE001
            if "ResourceLimitExceeded" in str(e) or "quota" in str(e).lower():
                print(f"[rbfe] {name}: spot quota reached after {len(launched)} jobs. Re-dispatch mode=run — "
                      f"resume picks up the rest.", flush=True)
                break
            raise
        launched.append(est.latest_training_job.name)
        print(f"[rbfe] launched {name} ({leg}-morph/{receptor}): {launched[-1]}")
    print(f"[rbfe] {len(launched)} spot morph-leg jobs launched. When complete: MODE=reduce → ΔΔG per receptor "
          f"+ selectivity. Jobs: {launched}")


if __name__ == "__main__":
    main()
