#!/usr/bin/env python3
"""Fan-out submitter for the MODERN independent-window ABFE (retires the Yank fleet in nr4a3_fep_sagemaker.py).

The ΔΔG deliverable needs 4 legs: complex(nr4a3), complex(nr4a1), complex(nr4a2), and ONE shared solvent leg
(ligand-only in water — identical across receptors, cancels in ΔΔG). Each leg is a SageMaker managed-**spot
Training** job running its 12 independent λ-windows, each per-iteration-checkpointed to S3 (spot-safe: ≤1 iter
lost on interruption). Spot draws on the 8-wide spot-Training quota (separate from the 1× on-demand g5), so all
4 legs run in parallel. Reduce with mode=reduce (CPU) → ΔG_bind per receptor → nr4a3_abfe.selectivity_ddg.

MODE (env MODE):
  plan  : DRY RUN — print the legs that WOULD launch + a cost note. No AWS spend.
  smoke : launch ONE tiny spot job (--mode smoke, no receptor) → validates the modern env solve + spot +
          checkpoint + resume path, and surfaces a spot-quota-0 (ResourceLimitExceeded) early.
  run   : launch the 4 leg jobs (or a subset via ONLY_LEGS). **Only on explicit trimcrae go-ahead.**
  reduce: launch a CPU reduce job per receptor (complex+solvent checkpoints as channels) → ΔG_bind json.

Resume: re-dispatch mode=run with the SAME tag → SageMaker downloads each leg's checkpoint prefix on start and
each window resumes from its last iteration. VALIDATE-FIRST rule (CLAUDE.md): shake out with mode=smoke, then
one real leg (ONLY_LEGS=solvent), before the full 4.
"""
import os
import sys

TAG = os.environ.get("ABFE_TAG", "nr4a3-abfe")
MODE = os.environ.get("MODE", "plan")
INSTANCE = os.environ.get("INSTANCE", "ml.g5.xlarge")
MAX_RUN_H = float(os.environ.get("MAX_RUN_HOURS", "12"))
MAX_WAIT_H = float(os.environ.get("MAX_WAIT_HOURS", "20"))
LIGAND = os.environ.get("ABFE_LIGAND", "denovo_401")
GIT_REF = os.environ.get("GIT_REF", "main")
SPOT = os.environ.get("SPOT", "1") == "1"
N_ITER = os.environ.get("ABFE_N_ITER", "1000")
STEPS_PER_ITER = os.environ.get("ABFE_STEPS_PER_ITER", "500")
RECEPTORS = [r.strip() for r in os.environ.get("ABFE_RECEPTORS", "nr4a3,nr4a1,nr4a2").split(",") if r.strip()]
RECEPTOR_PREFIX = os.environ.get("RECEPTOR_PREFIX", "nr4a3-denovo-matrix-v2")   # <r>-opened.pdb + docked_<r>.sdf
SPOT_HOURLY = float(os.environ.get("SPOT_HOURLY", "0.50"))
IMAGE_URI = os.environ.get("ABFE_IMAGE_URI", "").strip()                        # pre-baked modern ECR image
UNIT_GPU_H = float(os.environ.get("UNIT_GPU_H", "1.0"))                         # PLANNING ONLY / window (rough)


def _legs():
    """The leg jobs: one shared solvent + one complex per receptor. Each is (name, receptor, leg)."""
    legs = [("solvent", "shared", "solvent")]
    legs += [(f"complex-{r}", r, "complex") for r in RECEPTORS]
    return legs


def _cost_note():
    n = len(_legs())
    gpu_h = n * 12 * UNIT_GPU_H
    wall = 12 * UNIT_GPU_H                          # 12 windows serial per leg; legs parallel
    return (f"{n} legs × 12 windows × ~{UNIT_GPU_H:g} GPU-h ≈ {gpu_h:.0f} GPU-h; legs parallel on spot → "
            f"wall ~{wall:.0f} h; spot ≈ ${gpu_h * SPOT_HOURLY:.0f} (vs on-demand ${gpu_h * 1.4:.0f}). "
            f"NOTE: UNIT_GPU_H is a rough planning stub — a real ABFE window is not 1 GPU-h; calibrate on the "
            f"first leg's per-iteration wall time before trusting this.")


def main():
    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if MODE != "plan" and not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set")
    legs = _legs()
    print(f"[abfe] TAG={TAG} mode={MODE} spot={SPOT} instance={INSTANCE} receptors={RECEPTORS}")
    print(f"[abfe] legs: {[n for n, _r, _l in legs]}")
    print(f"[abfe] COST {_cost_note()}")

    if MODE == "plan":
        for name, receptor, leg in legs:
            print(f"  WOULD launch {TAG}-{name}: {leg} leg (receptor={receptor}), 12 windows, "
                  f"checkpoint s3://<bucket>/{TAG}/ckpt/{name}/")
        print("[abfe] plan only. Re-dispatch mode=smoke (validate) → ONLY_LEGS=solvent (one real leg) → run.")
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
            entry_point="entry_abfe.py", source_dir=os.path.join(here, "sagemaker_src"),
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

    common = {"git-ref": GIT_REF, "ligand-name": LIGAND, "n-iter": N_ITER,
              "steps-per-iter": STEPS_PER_ITER, "prebaked": "1" if IMAGE_URI else "0"}

    if MODE == "smoke":
        est = make_estimator("smoke", {**common, "mode": "smoke"})
        print("[abfe] launching SMOKE spot job (modern env + engine core loop, no receptor)…")
        est.fit(wait=True, logs=True)                 # wait → quota errors surface here
        print("[abfe] SMOKE complete — modern env solves; spot + checkpoint + resume path works.")
        return

    if MODE == "hydration":
        # ACCURACY GATE: hydration free energy of a small molecule (solvent leg only) vs a known value.
        name = os.environ.get("HYDRATION_NAME", "methane")
        est = make_estimator(f"hydration-{name}", {**common, "mode": "hydration",
                             "hydration-smiles": os.environ.get("HYDRATION_SMILES", "C"),
                             "hydration-name": name,
                             "hydration-known-dg": os.environ.get("HYDRATION_KNOWN_DG", "")})
        print(f"[abfe] launching HYDRATION accuracy-gate spot job ({name})…")
        est.fit(wait=False)
        print(f"[abfe] hydration job launched: {est.latest_training_job.name} — read "
              f"hydration_validation.json (model dir) or s3://{bucket}/{TAG}/ckpt/hydration-{name}/.")
        return

    only = {x.strip() for x in os.environ.get("ONLY_LEGS", "").split(",") if x.strip()} or None

    if MODE == "reduce":
        # one CPU reduce job per receptor: mount its complex ckpt + the shared solvent ckpt as channels.
        for receptor in RECEPTORS:
            if only and receptor not in only:
                continue
            est = make_estimator(f"reduce-{receptor}",
                                 {**common, "mode": "reduce", "receptor": receptor})
            est.fit({"complex": TrainingInput(f"s3://{bucket}/{TAG}/ckpt/complex-{receptor}/"),
                     "solvent": TrainingInput(f"s3://{bucket}/{TAG}/ckpt/solvent/")}, wait=False)
            print(f"[abfe] launched reduce-{receptor}: {est.latest_training_job.name}")
        print("[abfe] reduce jobs launched → ΔG_bind json per receptor in each job's model dir.")
        return

    # MODE == run : launch the leg jobs (bounded by spot quota; all 4 fit in the 8-wide quota).
    launched = []
    for name, receptor, leg in legs:
        if only and name not in only and leg not in only and receptor not in only:
            print(f"[abfe] skip {name} (not in ONLY_LEGS={sorted(only)})")
            continue
        hp = {**common, "mode": "run", "receptor": receptor, "leg": leg}
        est = make_estimator(name, hp)
        inputs = {"ligand": TrainingInput(matrix)}
        if leg == "complex":
            inputs["receptor"] = TrainingInput(matrix)
        try:
            est.fit(inputs, wait=False)               # wait=False → parallel legs
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "ResourceLimitExceeded" in msg or "quota" in msg.lower():
                print(f"[abfe] {name}: spot quota reached after {len(launched)} jobs ({e.__class__.__name__}). "
                      f"Re-dispatch mode=run later — resume picks up the rest.", flush=True)
                break
            raise
        launched.append(est.latest_training_job.name)
        print(f"[abfe] launched {name} ({leg}/{receptor}): {launched[-1]}")
    print(f"[abfe] {len(launched)} spot leg-jobs launched (parallel). When complete: MODE=reduce → ΔG_bind per "
          f"receptor, then nr4a3_abfe.selectivity_ddg for the headline ΔΔG. Jobs: {launched}")


if __name__ == "__main__":
    main()
