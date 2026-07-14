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
# A complex-morph leg runs its 12 λ-windows SERIALLY on one A10G (OpenFE execute_DAG has no intra-leg GPU
# fan-out), ~12 windows × 6 ns ≈ 15-25 GPU-h, so MAX_RUN must exceed that (the old 10 h killed complex legs
# mid-run). max_wait ≥ run + expected spot wait. For a SINGLE replicate the 3 complex legs run as 3 concurrent
# spot jobs → wall ≈ one leg. Window-sharding (fan a leg across GPUs, à la fep_sharding.py) is the right upgrade
# IF we escalate to a 3-replicate campaign; it's deferred here (single replicate, not worth the OpenFE-MBAR-
# combine re-engineering + shakeout risk).
# INCIDENT 2026-07-13: the congeneric pilot complex leg HIT the 30 h max_run (~6-7/12 windows done) — the
# "15-25 GPU-h" estimate above was ~2-3x optimistic; the leg actually paced ~4-5 h/window (iter times drifted
# 8s->40s, likely A10G spot-hardware variability), i.e. ~50-60 h for 12 windows. It was NOT a crash/interruption
# (a spot interrupt auto-resumes within max_wait; a max_run hit is terminal). Fix: size max_run to the OBSERVED
# slow pace so a single dispatch finishes even a slow 12-window leg (bills actual time, so no cost if it finishes
# early); checkpoint-per-window + the monitor's re-dispatch remain the belt-and-braces if it still stops.
MAX_RUN_H = float(os.environ.get("MAX_RUN_HOURS", "60"))          # fits a SLOW serial 12-window complex leg (obs. ~50-60 h)
MAX_WAIT_H = float(os.environ.get("MAX_WAIT_HOURS", "75"))        # run + generous spot capacity/auto-resume wait
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
UNIT_GPU_H = float(os.environ.get("UNIT_GPU_H", "2.0"))          # PLANNING ONLY — realistic A10G per-window
                                                                 # (~6 ns/window at ~80 ns/day + equil); the old
                                                                 # 0.5 under-quoted the edge ~4x. Calibrate on leg 1.


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
    if MODE not in ("plan", "ls", "jobs", "tracelog", "ckpt", "forensic", "stop", "stage") and not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set")

    if MODE == "stage":
        # Assemble the RBFE receptor prefix (<r>-opened.pdb + docked_<r>.sdf) from the congeneric DOCKING
        # output (the smina job already wrote nr4a3-opened.pdb + _pose_<lig>.sdf into its checkpoint). Pure
        # S3/boto3 in the GH runner — no SageMaker job, no GPU. Then MODE=smoke/run mount RECEPTOR_PREFIX.
        import boto3
        import sagemaker
        s3 = boto3.client("s3")
        bucket = sagemaker.Session().default_bucket()
        dock_prefix = os.environ.get("DOCK_PREFIX", "nr4a3-congeneric-dock/congeneric-pilot-ckpt").rstrip("/")
        dest = RECEPTOR_PREFIX.rstrip("/")
        receptor = RECEPTORS[0]
        keys = []
        tok = None
        while True:
            kw = {"Bucket": bucket, "Prefix": dock_prefix + "/"}
            if tok:
                kw["ContinuationToken"] = tok
            resp = s3.list_objects_v2(**kw)
            keys += [o["Key"] for o in resp.get("Contents", [])]
            if not resp.get("IsTruncated"):
                break
            tok = resp["NextContinuationToken"]
        print(f"[rbfe-stage] {len(keys)} objs under s3://{bucket}/{dock_prefix}/", flush=True)

        def _find(suffix):
            m = [k for k in keys if k.endswith(suffix)]
            return m[0] if m else None

        pdb_key = _find("nr4a3-opened.pdb") or _find("-opened.pdb")
        pose_a = _find(f"_pose_{LIGAND_A}.sdf")
        pose_b = _find(f"_pose_{LIGAND_B}.sdf")
        if not (pdb_key and pose_a and pose_b):
            print("[rbfe-stage] KEYS:", *keys, sep="\n  ")
            sys.exit(f"[rbfe-stage] missing inputs: pdb={pdb_key} poseA={pose_a} poseB={pose_b}")

        def _get(k):
            return s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode("utf-8", "replace")

        def _retitle(sdf_text, name):
            """Set each SDF record's title line (line 0 of the molblock) to `name` so the RBFE engine resolves
            the pose by _Name; also keeps the SMILES fallback. Returns record(s) + a trailing $$$$ delimiter."""
            out = []
            for blk in sdf_text.split("$$$$"):
                blk = blk.strip("\n")
                if not blk.strip():
                    continue
                lines = blk.split("\n")
                lines[0] = name
                out.append("\n".join(lines))
            return "".join(b + "\n$$$$\n" for b in out)

        docked = _retitle(_get(pose_a), LIGAND_A) + _retitle(_get(pose_b), LIGAND_B)
        s3.put_object(Bucket=bucket, Key=f"{dest}/docked_{receptor}.sdf", Body=docked.encode())
        s3.copy_object(Bucket=bucket, CopySource={"Bucket": bucket, "Key": pdb_key},
                       Key=f"{dest}/{receptor}-opened.pdb")
        print(f"[rbfe-stage] wrote s3://{bucket}/{dest}/{receptor}-opened.pdb + docked_{receptor}.sdf "
              f"(poses: {LIGAND_A}, {LIGAND_B}). Now dispatch MODE=smoke then run with "
              f"receptor_prefix={dest}.", flush=True)
        return

    if MODE == "tracelog":
        # Full CloudWatch traceback of a failed leg (FailureReason only carries the last line). RBFE_JOB=<name>
        # to target a specific job; otherwise the most recent Failed leg for the tag.
        import boto3
        sm = boto3.client("sagemaker")
        logs = boto3.client("logs")
        jobname = os.environ.get("RBFE_JOB", "").strip()
        if not jobname:
            r = sm.list_training_jobs(NameContains=TAG, MaxResults=8, SortBy="CreationTime",
                                      SortOrder="Descending")
            jobname = next((j["TrainingJobName"] for j in r.get("TrainingJobSummaries", [])
                            if j["TrainingJobStatus"] == "Failed"), "")
        print(f"[rbfe] TRACELOG for {jobname or '(none found)'}")
        if jobname:
            grp = "/aws/sagemaker/TrainingJobs"
            for st in logs.describe_log_streams(logGroupName=grp, logStreamNamePrefix=jobname,
                                                orderBy="LogStreamName").get("logStreams", []):
                ev = logs.get_log_events(logGroupName=grp, logStreamName=st["logStreamName"], limit=250,
                                         startFromHead=False)
                for e in ev.get("events", [])[-150:]:
                    print(e["message"].rstrip())
        return

    if MODE == "ckpt":
        # Dump the OpenFE checkpoint key layout so we can build a per-window progress metric. No spend.
        import boto3
        import sagemaker
        s3 = boto3.client("s3")
        bucket = sagemaker.Session().default_bucket()
        from collections import defaultdict
        keys = defaultdict(list)
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=f"{TAG}/ckpt/"):
            for o in page.get("Contents", []):
                rest = o["Key"].split(f"{TAG}/ckpt/", 1)[1]
                leg = rest.split("/", 1)[0]
                keys[leg].append(rest)
        for leg in sorted(keys):
            print(f"=== {leg}: {len(keys[leg])} keys")
            for k in keys[leg][:40]:
                print(f"    {k}")
        # cat the first real-time-analysis yaml + the completed leg json so we can parse them for progress
        for leg in sorted(keys):
            for k in keys[leg]:
                if k.endswith("simulation_real_time_analysis.yaml") or k.endswith(".json") and "leg_" in k:
                    try:
                        body = s3.get_object(Bucket=bucket, Key=f"{TAG}/ckpt/{k}")["Body"].read().decode(
                            "utf-8", "replace")
                        print(f"--- CONTENT {k}:\n{body[:1500]}")
                    except Exception as e:  # noqa: BLE001
                        print(f"    (read {k} failed: {e})")
                    break
        return

    if MODE == "forensic":
        # DEFINITIVE checkpoint forensic (answers: is the original production data still in S3, or did the resume
        # truncate/overwrite it — and is a full re-run actually necessary). For TAG's ckpt tree, report per-leg /
        # per-OpenFE-unit .nc file sizes + mtimes and the furthest production iteration actually preserved in each
        # simulation_real_time_analysis.yaml. Two things we're checking:
        #   (1) MULTIPLE OpenFE unit dirs per leg  -> the resume started a FRESH unit (new UUID from proto.create()),
        #       so the original run's .nc is ORPHANED-BUT-PRESENT in the older dir => recoverable without re-running.
        #   (2) ONE unit dir whose simulation.nc mtime is recent + small  -> it was overwritten => original lost.
        # The max "iteration:" across all yamls = the furthest production sampling that currently survives in S3.
        # Pure S3 read in the GH runner ($0). No SageMaker job, no GPU. (pyyaml-free: regex the iteration ints.)
        import re
        from collections import defaultdict

        import boto3
        import sagemaker
        s3 = boto3.client("s3")
        bucket = sagemaker.Session().default_bucket()
        prefix = f"{TAG}/ckpt/"
        objs = []
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
            for o in page.get("Contents", []):
                objs.append((o["Key"], o["Size"], o["LastModified"]))
        if not objs:
            print(f"[forensic] NO objects under s3://{bucket}/{prefix} (nothing checkpointed for this tag).")
            return
        print(f"[forensic] s3://{bucket}/{prefix}  ({len(objs)} objects)\n")

        def unit_of(rest):
            # the OpenFE shared unit dir (gufe names it 'shared_<ProtocolUnitKey>_attempt_<n>'); one per repeat.
            for comp in rest.split("/"):
                if comp.startswith(("shared_", "scratch_")) or "ProtocolUnit" in comp:
                    return comp
            parts = rest.split("/")
            return parts[1] if len(parts) > 2 else "(leg-root)"

        legs = defaultdict(list)
        for key, size, mt in objs:
            rest = key.split(prefix, 1)[1]
            legs[rest.split("/", 1)[0]].append((key, rest, size, mt))

        global_max_iter = {}
        for leg in sorted(legs):
            items = legs[leg]
            mts = [mt for _, _, _, mt in items]
            leg_mb = sum(s for _, _, s, _ in items) / 1e6
            print(f"=== LEG {leg}: {len(items)} objs, {leg_mb:.1f} MB, "
                  f"mtime {min(mts).strftime('%m-%d %H:%M')}Z .. {max(mts).strftime('%m-%d %H:%M')}Z")
            units = defaultdict(list)
            for key, rest, size, mt in items:
                units[unit_of(rest)].append((key, rest, size, mt))
            leg_max_iter = -1
            for u in sorted(units):
                ui = units[u]
                umts = [mt for *_, mt in ui]
                ncs = [(key, rest, s, mt) for key, rest, s, mt in ui if rest.endswith(".nc")]
                print(f"  -- unit {u}: {len(ui)} files, {sum(s for _, _, s, _ in ui)/1e6:.1f} MB, "
                      f".nc={len(ncs)} ({sum(s for _, _, s, _ in ncs)/1e6:.1f} MB), "
                      f"mtime {min(umts).strftime('%m-%d %H:%M')}Z..{max(umts).strftime('%m-%d %H:%M')}Z")
                for key, rest, s, mt in sorted(ncs, key=lambda x: x[1]):
                    print(f"       .nc {rest.split('/')[-1]:36s} {s/1e6:9.1f} MB  {mt.strftime('%m-%d %H:%M:%S')}Z")
                # furthest iteration preserved in this unit's real-time-analysis yaml(s)
                for key, rest, s, mt in ui:
                    if rest.endswith("real_time_analysis.yaml"):
                        try:
                            body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8", "replace")
                            iters = [int(x) for x in re.findall(r"iteration:\s*(\d+)", body)]
                            fes = re.findall(r"free_energy_in_kT:\s*([-\d.eE]+)", body)
                            mx = max(iters) if iters else -1
                            leg_max_iter = max(leg_max_iter, mx)
                            print(f"       yaml {rest.split('/')[-1]:35s} max_iter={mx}  "
                                  f"n_snapshots={len(iters)}  last_FE_kT={fes[-1] if fes else 'n/a'}  "
                                  f"{mt.strftime('%m-%d %H:%M:%S')}Z")
                        except Exception as e:  # noqa: BLE001
                            print(f"       yaml {rest.split('/')[-1]} read failed: {e}")
            global_max_iter[leg] = leg_max_iter
            nunits = len([u for u in units if u != "(leg-root)"])
            print(f"  >> {leg}: {nunits} OpenFE unit dir(s); furthest production iteration preserved = "
                  f"{leg_max_iter if leg_max_iter >= 0 else 'n/a (no yaml)'} / {N_ITER}\n")
        print("[forensic] READ:")
        for leg, mx in global_max_iter.items():
            print(f"  {leg}: furthest surviving iteration = {mx}. >1 unit dir => original run ORPHANED-but-present "
                  f"(recoverable); 1 unit dir with recent small .nc => overwritten (lost).")
        return

    if MODE == "jobs":
        # Track the fire-and-forget legs. list_training_jobs(NameContains=...) paginates flakily (returned 0/1/4
        # across identical calls), so BROAD-list then filter by tag in Python, AND print an S3 checkpoint census
        # (per-leg object count + last-write time) — the definitive liveness/progress signal (per-window ckpts).
        import boto3
        from collections import defaultdict
        sm = boto3.client("sagemaker")
        jobs = []
        try:
            resp = sm.list_training_jobs(MaxResults=80, SortBy="CreationTime", SortOrder="Descending")
            jobs = [(j["TrainingJobName"], j["TrainingJobStatus"]) for j in resp.get("TrainingJobSummaries", [])
                    if TAG in j["TrainingJobName"]]
        except Exception as e:  # noqa: BLE001
            print(f"[rbfe] job-list error: {e}")
        print(f"[rbfe] JOBS for tag={TAG}:")
        for name, status in jobs[:12]:
            reason = ""
            # For BOTH Failed and InProgress, describe → the FailureReason (Failed) OR the SecondaryStatus +
            # latest StatusMessage (InProgress). The secondary status is the ONLY way to tell a genuine spot-
            # capacity wait ("Starting" + "Insufficient capacity"/"preparing instances") from a job that already
            # has its instance and is Downloading the image or Training — don't assume "no logs" == capacity wait.
            if status in ("Failed", "InProgress"):
                try:
                    d = sm.describe_training_job(TrainingJobName=name)
                    if status == "Failed":
                        reason = (d.get("FailureReason", "") or "").replace("\n", " ")[-160:]
                    else:
                        sec = d.get("SecondaryStatus", "")
                        msg = ""
                        tr = d.get("SecondaryStatusTransitions", [])
                        if tr:
                            msg = (tr[-1].get("StatusMessage", "") or "").replace("\n", " ")[:120]
                        reason = f"[{sec}] {msg}"
                except Exception:  # noqa: BLE001
                    pass
            print(f"  {name:58s} {status:12s} {reason}")
        try:
            import sagemaker
            s3 = boto3.client("s3")
            bucket = sagemaker.Session().default_bucket()
            cnt, last = defaultdict(int), {}
            for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=f"{TAG}/ckpt/"):
                for o in page.get("Contents", []):
                    leg = o["Key"].split(f"{TAG}/ckpt/", 1)[1].split("/", 1)[0]
                    cnt[leg] += 1
                    if leg not in last or o["LastModified"] > last[leg]:
                        last[leg] = o["LastModified"]
            print(f"[rbfe] CKPT census s3://{bucket}/{TAG}/ckpt/ (liveness = recent last-write):")
            for leg in sorted(cnt):
                print(f"  {leg:16s} {cnt[leg]:4d} objs   last-write {last[leg].strftime('%m-%d %H:%M:%SZ')}")
            if not cnt:
                print("  (no checkpoint objects yet)")
        except Exception as e:  # noqa: BLE001
            print(f"[rbfe] ckpt-census error: {e}")
        return

    if MODE == "stop":
        # Kill the InProgress legs for this tag (e.g. the OpenCL-wedged complex legs) so they stop burning spot
        # before a re-dispatch with a platform fix. ONLY_LEGS filters which (by name substring); blank = all.
        import boto3
        sm = boto3.client("sagemaker")
        only = {x.strip() for x in os.environ.get("ONLY_LEGS", "").split(",") if x.strip()} or None
        resp = sm.list_training_jobs(MaxResults=80, SortBy="CreationTime", SortOrder="Descending")
        killed = 0
        for j in resp.get("TrainingJobSummaries", []):
            name, status = j["TrainingJobName"], j["TrainingJobStatus"]
            if TAG not in name or status != "InProgress":
                continue
            if only and not any(o in name for o in only):
                continue
            try:
                sm.stop_training_job(TrainingJobName=name)
                print(f"[rbfe] STOP requested: {name}")
                killed += 1
            except Exception as e:  # noqa: BLE001
                print(f"[rbfe] stop failed for {name}: {e}")
        print(f"[rbfe] {killed} InProgress job(s) sent Stop.")
        return

    legs = _legs()
    print(f"[rbfe] TAG={TAG} mode={MODE} edge={LIGAND_A}->{LIGAND_B} spot={SPOT} receptors={RECEPTORS}")
    print(f"[rbfe] legs: {[n for n, _r, _l in legs]}")
    print(f"[rbfe] COST {_cost_note()}")

    if MODE == "ls":
        # Fast diagnostic (runs on the CI runner, no SageMaker): list what the RBFE input prefixes actually
        # contain, so we can see the real S3 layout of the docked poses the engine mounts. No spend.
        import boto3
        import sagemaker  # default_bucket resolution matches the run path
        s3 = boto3.client("s3")
        bucket = sagemaker.Session().default_bucket()
        print(f"[rbfe] LS bucket={bucket}")
        for pfx in [RECEPTOR_PREFIX, "nr4a3-leadopt-species", "nr4a3-leadopt", "nr4a3-denovo-matrix-v2"]:
            print(f"=== s3://{bucket}/{pfx}/")
            paginator = s3.get_paginator("list_objects_v2")
            n = 0
            for page in paginator.paginate(Bucket=bucket, Prefix=f"{pfx}/"):
                for o in page.get("Contents", []):
                    k = o["Key"]
                    if k.endswith(".sdf") or k.endswith(".pdb") or k.endswith(".json"):
                        print(f"    {k}  ({o['Size']} B)")
                        n += 1
            if n == 0:
                print("    (no .sdf/.pdb/.json objects)")
        # dump docked_<r>.sdf record names (which ligand poses are actually in the RBFE input)
        try:
            import tempfile
            from rdkit import Chem
            for r in RECEPTORS:
                key = f"{RECEPTOR_PREFIX}/docked_{r}.sdf"
                tmp = os.path.join(tempfile.gettempdir(), f"docked_{r}.sdf")
                s3.download_file(bucket, key, tmp)
                names = [m.GetProp("_Name") for m in Chem.SDMolSupplier(tmp, removeHs=False)
                         if m is not None and m.HasProp("_Name")]
                hit = [x for x in names if x in ("ref_401", "denovo_401", "lo_m0_NCCO", "lo_m0_NCCO_gen")]
                print(f"=== records in {key}: n={len(names)} RBFE-relevant={hit}")
                print(f"    first10={names[:10]}")
        except Exception as e:  # noqa: BLE001
            print(f"[rbfe] record-name dump skipped: {e}")
        return

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

    if MODE == "cudaprobe":
        # Fast g5 diagnostic: does OpenMM's CUDA platform actually run on this image, or only OpenCL? Decides
        # whether the RBFE can leave the pathologically-slow OpenCL hybrid-Context path. No MD, no inputs needed.
        est = make_estimator("cudaprobe", {**common, "mode": "cudaprobe"})
        print("[rbfe] launching CUDA-probe spot job (env solve + nvidia-smi + OpenMM platform test, no MD)…")
        est.fit(wait=True, logs=True)
        print("[rbfe] CUDA-probe complete — see 'SELECTED PLATFORM =' above.")
        return

    if MODE == "smoke":
        est = make_estimator("smoke", {**common, "mode": "smoke"})
        # Smoke builds the COMPLEX hybrid topology (nr4a3/complex defaults), so it MUST mount the docked-pose
        # ligand SDF + the receptor PDB — the earlier no-input smoke failed with RDKit "Bad input file" because
        # /opt/ml/input was empty.
        inputs = {"ligand": TrainingInput(matrix), "receptor": TrainingInput(matrix)}
        print("[rbfe] launching SMOKE spot job (openfe env solve + mapping + hybrid-topology build, no MD)…")
        est.fit(inputs, wait=True, logs=True)
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
