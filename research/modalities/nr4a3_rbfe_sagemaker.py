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
# TIMEOUT PHILOSOPHY (rewritten 2026-07-14 after the forensic below): max_run is a RUNAWAY-COST BACKSTOP, NOT a
# schedule — it must sit FAR above the true worst-case runtime so it can only ever catch a genuine hang, never
# kill healthy work. You cannot turn it off: SageMaker requires MaxRuntimeInSeconds and DEFAULTS it to 24 h if
# unset — worse than any explicit value. It bills only ACTUAL training seconds, so a high ceiling costs $0 when
# the job finishes early. The REAL hang-guard is the per-window watchdog inside the entry (no-progress kill),
# NOT this number. A complex leg's observed worst case is ~46 h training (the furthest attempt billed ~30 h for
# 3250/5000 iters → ~46 h for 5000); 120 h gives ~2.5x headroom = non-binding. Sharding a leg across GPUs is a
# later upgrade (deferred: single replicate).
#
# ★ FORENSIC 2026-07-14 (mode=forensic on s3://.../nr4a3-congeneric-rbfe/ckpt/ — the DEFINITIVE record):
#   The complex-nr4a3 leg accumulated SEVEN separate OpenFE unit dirs (shared_...ProtocolUnit-<UUID>_attempt_0),
#   one per dispatch/spot-restart over 07-12..07-14. This proves TWO compounding bugs, NOT a slow-compute problem:
#     BUG A — the "resume" never resumes. Each run calls proto.create(), which mints a FRESH ProtocolUnit UUID →
#             a NEW shared dir → the job ignores every prior dir and restarts from iteration 0. 7 attempts, all
#             from scratch. This is why we kept seeing low iteration counters after a restart.
#     BUG B — the trajectory isn't durably uploaded. The furthest attempt (190a9cf1) reached iter 3250/5000 but
#             its dir holds ONLY db.json + hybrid_system.pdb + the progress yaml — .nc = 0 bytes in S3. The 3250
#             iters of actual MD are GONE (spot kill before the big simulation.nc flushed/uploaded). The only
#             complex .nc in S3 is the latest partial attempt's 6.5 MB (early). => the complex leg CANNOT be
#             resumed or MBAR-gathered; it must be RE-RUN. (The solvent leg finished clean: 5000/5000, leg json
#             written, ΔG=13.74 kcal — SAFE, not re-run.)
#   NEVER-AGAIN fixes (gate the re-run): (1) non-binding max_run [this change]; (2) per-window no-progress
#   watchdog = the real hang-guard; (3) deterministic DAG/unit identity + point openmmtools at the existing .nc so
#   a restart CONTINUES the same unit dir; (4) flush + continuously-upload simulation.nc so a spot kill loses ≤ one
#   checkpoint interval; (5) the pre-charge speedup shortens a leg enough to finish inside one spot allocation
#   (primary defense — if it never needs to resume, Bug A/B can't bite). Belt-and-braces, not any single lever.
MAX_RUN_H = float(os.environ.get("MAX_RUN_HOURS", "120"))         # NON-BINDING backstop (~2.5x the ~46 h worst case); bills actual time
MAX_WAIT_H = float(os.environ.get("MAX_WAIT_HOURS", "140"))       # ≥ max_run + generous spot capacity/auto-resume wait
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
    if MODE not in ("plan", "ls", "jobs", "tracelog", "ckpt", "forensic", "eta", "stop", "stage") and not role:
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

    if MODE == "eta":
        # RIGOROUS live ETA (trimcrae 2026-07-14: "track iteration progress + speed on each window, update ETAs as
        # you go"). Reads the running complex leg's openmmtools simulation_real_time_analysis.yaml from S3 (written
        # every analysis interval during PRODUCTION) and reports, from real data: current production iteration,
        # the per-snapshot seconds/iteration trend (each iteration propagates ALL 12 λ-windows/replicas + attempts
        # exchanges — so s/iter IS the per-window pace), ns/day, the running MBAR ΔG±SE (convergence), and a
        # self-computed absolute finish time = now + remaining_iters × recent_avg_s/iter (unambiguous UTC->ET, not
        # the engine's tz-ambiguous localtime field). Also compares pace to the first attempt (~20 s/iter avg) so
        # we can SEE it running faster. Before production starts (setup/solvate/minimize/equilibrate) there is no
        # yaml yet -> says so + points at tracelog for the live 'Equilibration iteration N/1000'. Pure S3 read ($0).
        import datetime
        import boto3
        import sagemaker
        import yaml as _yaml
        s3 = boto3.client("s3")
        bucket = sagemaker.Session().default_bucket()
        leg = (os.environ.get("ONLY_LEGS", "").split(",")[0].strip() or "complex-nr4a3")
        prefix = f"{TAG}/ckpt/{leg}/"
        yamls = []
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
            for o in page.get("Contents", []):
                if o["Key"].endswith("simulation_real_time_analysis.yaml"):
                    yamls.append((o["Key"], o["LastModified"]))
        print(f"[eta] leg={leg}  s3://{bucket}/{prefix}")
        if not yamls:
            print("[eta] no production real_time_analysis.yaml yet -> still in setup/solvation/minimization/"
                  "equilibration (openmmtools writes this file only once PRODUCTION starts). Use mode=tracelog to "
                  "see the live 'Equilibration iteration N/1000' or 'Iteration N/5000' counter.")
            return
        key, mt = max(yamls, key=lambda x: x[1])
        snaps = _yaml.safe_load(s3.get_object(Bucket=bucket, Key=key)["Body"].read()) or []
        snaps = [s for s in snaps if isinstance(s, dict) and "iteration" in s]
        if not snaps:
            print(f"[eta] yaml present but no parseable snapshots yet ({key}, written {mt.strftime('%H:%M:%S')}Z).")
            return
        last = snaps[-1]
        it = int(last["iteration"])
        pct = float(last.get("percent_complete") or 0.0)
        total = round(it / (pct / 100.0)) if pct else int(os.environ.get("ETA_TOTAL", "5000"))
        td = last.get("timing_data", {}) or {}
        avg = float(td.get("average_seconds_per_iteration") or 0.0)
        ns_day = td.get("ns_per_day")
        mb = last.get("mbar_analysis", {}) or {}
        fe, se = mb.get("free_energy_in_kT"), mb.get("standard_error_in_kT")
        # recent per-snapshot s/iter trend (the last ~10) so we SEE speed per window over time
        print(f"[eta] production {it}/{total} ({100*it/total:.1f}%)  |  MBAR ΔG={fe} ± {se} kT  |  yaml @ "
              f"{mt.strftime('%H:%M:%S')}Z")
        print("[eta] recent snapshots (iteration : seconds/iter : ns/day):")
        for s in snaps[-10:]:
            t = s.get("timing_data", {}) or {}
            print(f"        {int(s['iteration']):5d} : {float(t.get('iteration_seconds', 0)):6.1f}s : "
                  f"{float(t.get('ns_per_day', 0)):5.1f}")
        # rigorous absolute ETA: remaining production iters × recent avg s/iter, from UTC now -> ET (UTC-4), 12-hr.
        remaining = max(0, total - it)
        eta_s = remaining * avg if avg else 0
        now = datetime.datetime.utcnow()
        fin_et = (now + datetime.timedelta(seconds=eta_s)) - datetime.timedelta(hours=4)
        hrs = eta_s / 3600.0
        first_avg = 20.0  # first attempt's ~avg s/iter (2026-07-13 yaml) for a faster/slower comparison
        pace = ("FASTER" if avg and avg < first_avg else "slower" if avg else "n/a")
        print(f"[eta] recent avg = {avg:.1f} s/iter (first attempt ~{first_avg:.0f} s/iter -> {pace}); "
              f"ns/day = {ns_day}")
        print(f"[eta] remaining {remaining} prod iters × {avg:.1f}s = {hrs:.1f} h  ->  finish ~"
              f"{fin_et.strftime('%b-%d %-I:%M %p')} ET  (production phase only; equilibration already done)")
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

    # Pass the never-again knobs straight to the training container as env vars (entry_rbfe copies os.environ into
    # the conda subprocess, so nr4a3_rbfe.py reads them): RBFE_RESUME=1 activates the deterministic-DAG resume
    # (stable unit dirs across spot restarts), RBFE_STALL_MIN tunes the watchdog, RBFE_MIN_MAPPED* the map guard.
    env_pass = {k: os.environ[k] for k in
                ("RBFE_RESUME", "RBFE_STALL_MIN", "RBFE_MIN_MAPPED", "RBFE_MIN_MAPPED_FRAC") if os.environ.get(k)}

    def make_estimator(name, hp, instance=None, ckpt_name=None, spot=None, extra_env=None):
        use_spot = SPOT if spot is None else spot
        kw = dict(
            entry_point="entry_rbfe.py", source_dir=os.path.join(here, "sagemaker_src"),
            role=role, instance_count=1, instance_type=instance or INSTANCE, sagemaker_session=sess,
            base_job_name=f"{TAG}-{name}", use_spot_instances=use_spot,
            max_run=int(MAX_RUN_H * 3600), max_wait=int(MAX_WAIT_H * 3600) if use_spot else None,
            # ckpt_name lets the split's setup|simulate|analyze jobs SHARE one prefix (ckpt/<leg>/) so the sim
            # job downloads the setup job's serialized system + the analyze job reads the sim's .nc.
            checkpoint_s3_uri=f"s3://{bucket}/{TAG}/ckpt/{ckpt_name or name}/",
            checkpoint_local_path="/opt/ml/checkpoints", hyperparameters=hp)
        merged_env = {**env_pass, **(extra_env or {})}
        if merged_env:
            kw["environment"] = merged_env
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

    if MODE in ("setup", "simulate", "analyze"):
        # CPU-build / GPU-MD SPLIT (2026-07-14, trimcrae): run OpenFE 1.12's own 3 units as separate jobs so the
        # ~1 h single-threaded hybrid-system BUILD runs on CHEAP CPU (never on an idle GPU), only the MD on GPU.
        #   setup    -> CPU (on-demand: can't resume, but a cheap-CPU redo is trivial) -> serializes the system.
        #   simulate -> GPU SPOT (resumes from its own .nc via OpenFE _check_restart -> spot interruption safe).
        #   analyze  -> CPU (on-demand) -> MBAR -> leg_<r>_<leg>.json (reduce reads it, unchanged).
        # All three SHARE ckpt/<leg>/ (ckpt_name=name) so files flow setup->sim->analyze via the S3 checkpoint.
        cpu_inst = os.environ.get("CPU_INSTANCE", "ml.m5.2xlarge")   # 8 vCPU/32 GB — RAM for the solvated build
        inst = INSTANCE if MODE == "simulate" else cpu_inst
        spot = None if MODE == "simulate" else False                # sim=spot(resumes); setup/analyze=on-demand CPU
        launched = []
        for name, receptor, leg in legs:
            if only and name not in only and leg not in only and receptor not in only:
                continue
            # setup/analyze run on CPU boxes → force the CPU OpenMM platform (skip the CUDA/OpenCL probe).
            extra = {"RBFE_PLATFORM": "CPU"} if MODE != "simulate" else None
            est = make_estimator(f"{name}-{MODE}", {**common, "mode": MODE, "receptor": receptor, "leg": leg},
                                 instance=inst, ckpt_name=name, spot=spot, extra_env=extra)
            inputs = {"ligand": TrainingInput(matrix)}
            if leg == "complex":
                inputs["receptor"] = TrainingInput(matrix)
            est.fit(inputs, wait=False)
            launched.append(est.latest_training_job.name)
            print(f"[rbfe] launched {MODE} {name} ({leg}/{receptor}) on {inst} "
                  f"(spot={'default' if spot is None else spot}): {launched[-1]}  ckpt {TAG}/ckpt/{name}/")
        nxt = {"setup": "simulate", "simulate": "analyze", "analyze": "reduce"}[MODE]
        print(f"[rbfe] {len(launched)} {MODE} job(s) launched → when Complete, run MODE={nxt}. Jobs: {launched}")
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
