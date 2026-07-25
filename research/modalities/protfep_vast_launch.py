#!/usr/bin/env python3
"""5a-KS protein-mutation FEP — Vast.ai launcher for the known-answer qualification benchmark.

WHAT THIS RUNS AND WHY IT IS THE NEXT TEST
------------------------------------------
STRATEGY.md's ladder has exactly one rung that is not merely unpriced but *unscoped*: 5a-KS, the
reciprocal target-surface mutation wedge, which is simultaneously the program's designated causal
kill-switch AND the paper's primary causal result. Its engine was built on 2026-07-24 and has never
run. An engine that exists is not a rate, and until a known-answer benchmark says the engine works,
no number it produces may enter the manuscript and the rung cannot be priced.

This launcher runs that benchmark: alchemical point mutations at the barstar Y29 hot spot of the
barnase-barstar interface, whose binding ddG is among the most-measured numbers in the
protein-protein interaction literature. Both mutations are charge-conserving, so engine error is
not confounded with the PME finite-size artifact that a charge-changing mutation would introduce.

It is also cleanly PARALLEL to valB_mini: that lane is OpenFE ligand RBFE on GCP L4; this is perses
protein-mutation FEP on Vast 4090. Different engine, different provider, different rung — no shared
quota, no shared code path, no interference.

STAGED, CHEAPEST-DECISIVE-FIRST (the repo's pilot-one-leg-first rule)
--------------------------------------------------------------------
  smoke  -> 1 unit, the apo leg at 3 windows x 20 iterations. Proves image + perses build + sampler
            + MBAR + S3 upload end to end for ~$0.10. Its dG is meaningless and is labelled so.
  pilot  -> 2 units, both legs of Y29A at 1 replicate. This is the abort gate: if the engine cannot
            recover the canonical ~3.4 kcal/mol barstar hot spot, the wedge is not deliverable and
            the rest of the set is not worth renting a GPU for.
  full   -> the whole set (both mutations x both legs x n replicates), fanned out N-wide. Only run
            once the pilot says the engine sees the effect at all — at which point we would run
            every unit regardless of any single unit's result, so serialising further buys nothing.

Each unit is one Vast instance running one leg, checkpointing its .nc continuously to S3 and
self-destroying on exit. build_jobspec is PURE and unit-tested; submit() needs live credentials.
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import protfep_bench as bench  # noqa: E402
from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
# NOTE THE `or`, NOT `os.environ.get(key, default)`. CI passes optional workflow inputs as EMPTY
# STRINGS, and an empty string is a SET variable, so .get()'s default never fires. That is not
# hypothetical: the first smoke launch (2026-07-24, instance 45735820) rented a real 4090 and
# resolved its result prefix to `s3:///protfep-benchmark/...` — a bucket-less URI — so every upload
# would have failed silently behind `|| true` and the leg would have produced nothing retrievable.
# `or` treats empty-as-unset, which is what a blank CI input means.
VAST_IMAGE = os.environ.get("VAST_IMAGE") or "docker.io/triskit23/pmxfep:latest"
RESULT_PREFIX = os.environ.get("PROTFEP_RESULT_PREFIX") or "protfep-benchmark"
DEFAULT_BUCKET = os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
LABEL_PREFIX = "protfep-bench"
# Runtime backstop for the reap: an instance up longer than this is destroyed even if no
# result appeared, so a hung or crashed leg cannot bill indefinitely. It is a BACKSTOP, not
# the normal path — the normal path is "leg result in S3 -> destroy".
MAX_INSTANCE_HOURS = float(os.environ.get("PROTFEP_MAX_INSTANCE_HOURS") or "10")
# How long a box may sit at cur_state="stopped" before the nudge is given up on and it is destroyed.
# Sized off the observed failure: the complex leg's host sat stopped for 36 minutes with a frozen
# image pull, so the bound has to exceed a legitimate slow pull while still being far below the
# 10-hour runtime backstop. A stopped box bills storage only, so this is minutes of waste, not GPU-h.
MAX_STOPPED_MIN = float(os.environ.get("PROTFEP_MAX_STOPPED_MIN") or "45")

# A solvated barnase-barstar complex is ~30-35k atoms and the apo barstar leg ~15-20k — small
# systems by this repo's standards (the ternary hybrid is 146k). The 4090 is the measured $/ns
# winner at every size in gpu_md_bench, and at this size nothing is VRAM- or host-RAM-bound, so a
# modest host spec keeps the cheap 4090 offers in play instead of filtering down to the expensive
# high-demand hosts. min_cuda 13.0 is the repo's settled host filter: a newer driver runs older PTX
# fine, whereas an older driver hit CUDA_ERROR_UNSUPPORTED_PTX_VERSION on this stack twice before.
RES = ResourceSpec(gpu=os.environ.get("PROTFEP_GPU") or "rtx4090",
                   min_vram_gb=int(os.environ.get("PROTFEP_VRAM") or "24"),
                   vcpus=4, ram_gb=16, disk_gb=40, min_cuda=13.0, interruptible=True)

# The onstart pipeline. VastBackend._vast_onstart exports forwarded S3 creds + arms the key-free
# self-destroy EXIT trap. A background sync loop pushes the .nc + partial leg JSON to S3 every 3
# minutes, so a spot preemption leaves a resumable checkpoint rather than nothing — the standing
# checkpoint-continuously rule, which is what makes an interruptible bid safe to take.
_PIPELINE = r"""
set -o pipefail
export HOME=/root
export PATH=/opt/mamba/envs/pmxfep/bin:$PATH
exec > >(tee /tmp/run.log) 2>&1
echo "[protfep] $(date -u +%FT%TZ) start leg=$LEG_ID benchmark=$PROTFEP_BENCHMARK env=$PROTFEP_ENVIRONMENT"
mark() { echo "$1 $(date -u +%FT%TZ)" | aws s3 cp - "$RESULT_S3/phase.txt" 2>/dev/null || true; \
         aws s3 cp /tmp/run.log "$RESULT_S3/run.log" 2>/dev/null || true; }
mark start
# IDEMPOTENCY: Vast re-runs onstart if the container restarts. A finished leg must not re-run.
if aws s3 ls "$RESULT_S3/leg_$LEG_ID.json" >/dev/null 2>&1; then
  if aws s3 cp "$RESULT_S3/leg_$LEG_ID.json" - 2>/dev/null | grep -q '"status": "done"'; then
    echo "[protfep] leg already done in S3 -> nothing to do (awaiting CI reap)"; exit 0
  fi
fi
mkdir -p /tmp/protfep_in /tmp/protfep_out
# RESUME: pull back EVERYTHING the sync loop uploads, not just the leg JSON.
# A finished lambda window is recorded by its .xvg inside work_<leg>/, and run_windows skips any
# window whose .xvg is present — but only if the file is actually restored. Pulling only the JSON
# meant a preempted leg silently re-ran every completed window: the apo pilot leg was preempted at
# 14/16 windows, ~1 GPU-h that would have been paid for twice with nothing in the log to say why.
# hybrid.top + npt.gro come back too so build_system can skip the whole setup phase.
aws s3 cp "$RESULT_S3/" /tmp/protfep_out/ --recursive --exclude '*' \
    --include "leg_$LEG_ID.json" --include "work_$LEG_ID/*" 2>/dev/null || true
echo "[protfep] restored $(ls /tmp/protfep_out/work_$LEG_ID/*.xvg 2>/dev/null | wc -l) finished window(s)"
ls -la /tmp/protfep_out || true
# --- repo code (public codeload tarball) ---
cd /root
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz || { echo "repo pull failed"; exit 3; }
cd Rare-cancers-*/research/modalities || exit 3
# WHICH CODE actually ran. The host pulls a codeload TARBALL of the branch head, so there is no git
# sha on disk and the branch may have moved between dispatch and container start. A content hash of
# the driver is the only fingerprint that cannot lie, and without it a `failed` record in S3 is
# ambiguous between "the fix does not work" and "this is the pre-fix attempt's record" — which is
# exactly the ambiguity that cost a diagnostic round trip on the complex leg.
export PROTFEP_CODE_SHA256="$(sha256sum protfep_pmx.py | cut -c1-12)"
echo "[protfep] driver protfep_pmx.py sha256[:12]=$PROTFEP_CODE_SHA256 branch=$GIT_BRANCH"
mark cloned
# --- continuous checkpoint upload (every 3 min) so a preemption never loses the leg ---
( while true; do sleep 180; \
    aws s3 cp /tmp/protfep_out/ "$RESULT_S3/" --recursive --exclude '*' \
        --include "leg_$LEG_ID.json" --include "work_$LEG_ID/*.xvg" \
        --include "work_$LEG_ID/hybrid.top" --include "work_$LEG_ID/npt.gro" >/dev/null 2>&1 || true; \
    aws s3 cp /tmp/run.log "$RESULT_S3/run.log" >/dev/null 2>&1 || true; \
  done ) &
SYNC_PID=$!
mark md-running
INPUT_DIR=/tmp/protfep_in OUTPUT_DIR=/tmp/protfep_out python autoteardown.py \
    python protfep_pmx.py --benchmark "$PROTFEP_BENCHMARK" --environment "$PROTFEP_ENVIRONMENT" \
        --replicate "$PROTFEP_REPLICATE" --leg-id "$LEG_ID" ${PROTFEP_N_STATES_ARG}
RC=$?
kill $SYNC_PID 2>/dev/null || true
mark md-done
# --- final upload: the leg JSON (the deliverable) + the trajectory checkpoint + the log ---
aws s3 cp /tmp/protfep_out/ "$RESULT_S3/" --recursive --exclude '*' \
    --include "leg_$LEG_ID.json" --include "work_$LEG_ID/*.xvg" \
    --include "work_$LEG_ID/hybrid.top" --include "work_$LEG_ID/npt.gro" || echo "result upload failed"
mark done
echo "[protfep] $(date -u +%FT%TZ) EXIT rc=$RC"
exit $RC
"""

# Sampling sizes per mode. The smoke's numbers are deliberately too small to mean anything
# scientifically — its ONLY job is to prove the chain runs end to end before a real leg is paid for,
# which is why its leg id carries a _smoke suffix that protfep_reduce refuses to score.
# `env` entries are merged into the instance environment and read by protfep_pmx's module constants.
MODES = {
    "smoke": {"n_states": 3, "max_runtime_s": 5400,
              "env": {"PMX_EQUIL_PS": "5", "PMX_PROD_PS": "20", "PMX_MIN_STEPS": "500",
                      "PMX_NVT_PS": "5", "PMX_NPT_PS": "5"}},
    "pilot": {"n_states": None, "max_runtime_s": 36000, "env": {}},
    "full": {"n_states": None, "max_runtime_s": 36000, "env": {}},
}


def units_for(mode, n_replicas=3, benchmarks=None):
    """The leg specs this mode should launch. Pure.

    smoke -> the single cheapest leg (apo, one replicate) of the pilot benchmark.
    pilot -> both legs of the pilot benchmark at one replicate: the abort gate.
    full  -> every leg of every benchmark at n_replicas.
    """
    if mode == "smoke":
        return [bench.leg_spec(bench.PILOT_BENCHMARK, "apo", 0)]
    if mode == "pilot":
        return [bench.leg_spec(bench.PILOT_BENCHMARK, env, 0) for env in ("complex", "apo")]
    if mode == "full":
        return bench.all_leg_specs(names=benchmarks, n_replicas=n_replicas)
    raise ValueError(f"unknown mode {mode!r}; expected one of {sorted(MODES)}")


def leg_id_for(spec, mode):
    """The LEG_ID this unit runs under. Pure. Single source for the id, used by BOTH the label and
    the jobspec — they diverged once and it broke the reap (see unit_label)."""
    return f"{spec['leg_id']}_smoke" if mode == "smoke" else spec["leg_id"]


def unit_label(spec, mode):
    """Vast instance label for one leg. Pure. Prefix lets the reap find every instance of this lane.

    MUST be derived from the same leg id the jobspec uses. It was not: smoke mode labelled the host
    `protfep-bench-smoke` while its LEG_ID was `<benchmark>__apo_r0_smoke`, so label_matches_leg
    could never match and collect's reap skipped the host entirely — the smoke leg crashed, Vast
    re-ran onstart in a loop, and the GPU kept billing with nothing to produce.
    """
    return f"{LABEL_PREFIX}-{leg_id_for(spec, mode)}".replace("_", "-").lower()[:60]


def label_matches_leg(label, leg_id):
    """Does this Vast instance label belong to this leg's result? Pure.

    The label is a lossy encoding of the leg id (underscores flattened to dashes, lowercased, and
    truncated to Vast's 60-char limit), so matching has to go leg_id -> label, never the reverse.
    This is worth a named, tested function because a MISSED match is not a cosmetic bug: `collect`
    reaps an instance when its leg is done, so a match that fails leaves a finished leg's GPU billing
    until the runtime backstop fires hours later. Real money, silently.
    """
    if not label or not leg_id:
        return False
    label = str(label).strip().lower()
    encoded = f"{LABEL_PREFIX}-{str(leg_id)}".replace("_", "-").lower()[:60]
    return label == encoded


def _record_is_newer_than_instance(doc, instance):
    """Was this leg record written by the CURRENTLY running instance? Pure (given the inputs).

    Compares the record's `updated_utc` against the instance's start time. Returns False when either
    timestamp is missing or unparseable — the conservative direction, since the cost of not reaping
    is a host that self-destroys or hits the runtime backstop, while the cost of reaping wrongly is
    killing a leg that was about to do real work.
    """
    import calendar
    stamp = doc.get("updated_utc") or doc.get("started_utc")
    started = instance.get("start_date")
    if not stamp or started is None:
        return False
    try:
        rec_epoch = calendar.timegm(time.strptime(str(stamp), "%Y-%m-%dT%H:%M:%SZ"))
        return rec_epoch > float(started)
    except (ValueError, TypeError):
        return False


def build_jobspec(spec, mode="pilot", git_branch=None, bucket=None, result_prefix=None):
    """PURE construction of one leg's JobSpec (no network)."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}")
    sizing = MODES[mode]
    branch = git_branch or os.environ.get("GIT_BRANCH") or "main"
    b = bucket or DEFAULT_BUCKET
    prefix = result_prefix or RESULT_PREFIX
    leg_id = leg_id_for(spec, mode)
    if not b or not prefix:
        raise ValueError(
            f"refusing to launch with an incomplete result location (bucket={b!r}, prefix={prefix!r}). "
            f"A blank CI input arrives as an EMPTY STRING, not as unset, so os.environ.get's default "
            f"does not fire — this exact hole rented a 4090 that would have uploaded to 's3:///...' "
            f"and produced nothing retrievable.")
    result_s3 = f"s3://{b}/{prefix}/{leg_id}"
    env = {
        "MODE": mode,
        "LEG_ID": leg_id,
        "PROTFEP_BENCHMARK": spec["benchmark"],
        "PROTFEP_ENVIRONMENT": spec["environment"],
        "PROTFEP_REPLICATE": str(spec["replicate"]),
        "GIT_BRANCH": branch,
        "RESULT_S3": result_s3,
        "VAST_IMAGE_TAG": VAST_IMAGE,
        # Passed as pre-rendered CLI fragments so the pipeline stays a single fixed command string and
        # an unset size simply expands to nothing (i.e. the module default applies).
        "PROTFEP_N_STATES_ARG": (f"--n-states {sizing['n_states']}" if sizing["n_states"] else ""),
    }
    env.update(sizing.get("env") or {})
    return JobSpec(
        name=unit_label(spec, mode),
        command=["bash", "-lc", _PIPELINE.replace("{repo}", REPO)],
        image=VAST_IMAGE,
        checkpoint_uri=result_s3,
        resume=True,                      # per-leg .nc resume: a preempted leg continues, not restarts
        resources=RES,
        max_runtime_s=int(os.environ.get("PROTFEP_MAX_RUNTIME_S") or sizing["max_runtime_s"]),
        env=env,
    )


def completed_leg_ids(bucket=None, prefix=None):
    """Leg ids whose result is already `done` in S3. Needs live AWS creds; [] if unavailable."""
    try:
        import boto3
    except ImportError:
        return []
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    done = []
    try:
        s3 = boto3.client("s3")
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=b, Prefix=f"{p}/"):
            for obj in page.get("Contents", []):
                name = os.path.basename(obj["Key"])
                if not (name.startswith("leg_") and name.endswith(".json")):
                    continue
                doc = json.loads(s3.get_object(Bucket=b, Key=obj["Key"])["Body"].read().decode())
                if doc.get("status") == "done" and doc.get("leg_id"):
                    done.append(doc["leg_id"])
    except Exception as e:  # noqa: BLE001 — never let a listing failure block a launch
        print(f"[launch] could not list completed legs ({type(e).__name__}: {e}); launching all")
        return []
    return done


def submit(mode="pilot", n_replicas=3, benchmarks=None, dry_run=False):
    """Rent one instance per leg for this mode, skipping legs already finished.

    SKIPPING HAPPENS BEFORE THE RENTAL, not on the host. The onstart has an idempotency check, but it
    only runs after the image pull and repo clone — so a re-dispatch was renting a GPU for ~25
    minutes just to have it discover the leg was done and exit. Observed at $0.15 a time on the apo
    leg. The launcher has S3 access, so the cheap check belongs here.
    """
    specs = units_for(mode, n_replicas=n_replicas, benchmarks=benchmarks)
    if not dry_run:
        finished = set(completed_leg_ids())
        keep = [s for s in specs if leg_id_for(s, mode) not in finished]
        skipped = [leg_id_for(s, mode) for s in specs if leg_id_for(s, mode) in finished]
        if skipped:
            print(f"[launch] skipping {len(skipped)} already-finished leg(s), no rental: {skipped}")
        specs = keep
        if not specs:
            print("[launch] every leg for this mode is already done — nothing to rent")
            return []
    print(f"[launch] mode={mode} units={len(specs)} image={VAST_IMAGE} gpu={RES.gpu}")
    jobspecs = [build_jobspec(s, mode=mode) for s in specs]
    if dry_run:
        print(json.dumps([{"name": j.name, "env": j.env, "max_runtime_s": j.max_runtime_s}
                          for j in jobspecs], indent=2))
        return []
    backend = get_backend("vast")
    handles = []
    for j in jobspecs:
        try:
            h = backend.submit(j)
            print(f"[launch] {j.name}: instance={h.job_id} offer={h.extra.get('offer')} "
                  f"dph={h.extra.get('dph')}")
            handles.append(h)
        except Exception as e:  # noqa: BLE001 — one unrentable unit must not abort the rest
            print(f"[launch] {j.name}: SUBMIT FAILED {type(e).__name__}: {e}")
    print(f"[launch] {len(handles)}/{len(jobspecs)} units submitted; results -> "
          f"s3://{DEFAULT_BUCKET}/{RESULT_PREFIX}/")
    return handles


def collect(bucket=None, prefix=None, autostop=True):
    """Status board + anti-idle reap: list this lane's instances and the leg JSONs already in S3.

    Any instance whose leg has a `status: done` JSON in S3 is destroyed from CI (the API key stays on
    the trusted runner, never on a community host). Returns (n_up, n_done).
    """
    import boto3
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    s3 = boto3.client("s3")
    done, partial = {}, {}
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=b, Prefix=f"{p}/"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not os.path.basename(key).startswith("leg_") or not key.endswith(".json"):
                continue
            try:
                doc = json.loads(s3.get_object(Bucket=b, Key=key)["Body"].read().decode())
            except Exception as e:  # noqa: BLE001
                print(f"[collect] unreadable {key}: {e}")
                continue
            (done if doc.get("status") == "done" else partial)[doc.get("leg_id", key)] = doc
            doc["_s3_last_modified"] = obj["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ")

    # Phase markers + the tail of each leg's log. A status board that shows only finished JSONs is a
    # LIVENESS check ("the instance is up"), and this repo's rule for an unproven pipeline is that a
    # check must show the science ADVANCING — which phase it reached, and when. The three silent
    # failures on the ternary lane all looked alive.
    print("[collect] phase markers:")
    for page in paginator.paginate(Bucket=b, Prefix=f"{p}/"):
        for obj in page.get("Contents", []):
            if not obj["Key"].endswith("/phase.txt"):
                continue
            leg = obj["Key"].split("/")[-2]
            try:
                phase = s3.get_object(Bucket=b, Key=obj["Key"])["Body"].read().decode().strip()
            except Exception as e:  # noqa: BLE001
                phase = f"(unreadable: {e})"
            # AGE, not just a wall-clock stamp. "cloned at 23:28" tells you nothing on its own; "cloned
            # 47 min ago" is the stall signal. The previous version computed the age by subtracting a
            # timestamp from itself, so it was always 0.0 — and it was never printed, which is why an
            # apparently-live board could not distinguish a leg advancing from one frozen for an hour.
            age_min = (time.time() - obj["LastModified"].timestamp()) / 60
            print(f"    {leg}: {phase}  (marker written {obj['LastModified']:%H:%M:%S} UTC, "
                  f"{age_min:.0f} min ago)")
            log_key = obj["Key"].replace("/phase.txt", "/run.log")
            try:
                tail = s3.get_object(Bucket=b, Key=log_key)["Body"].read().decode(errors="replace")
                lines = [ln for ln in tail.strip().splitlines() if ln.strip()][-12:]
                for ln in lines:
                    print(f"      | {ln[:160]}")
            except Exception:  # noqa: BLE001 — the log may not exist yet
                print("      | (no run.log yet)")

    # Instances are fetched BEFORE the leg board so the board can say whether a `failed` record has
    # already been superseded by a newer host. Without that pairing every poll reprints a full
    # traceback for a failure that was fixed hours ago, which is how a monitoring log stops being
    # read. The reap below reuses this same list rather than querying twice.
    key = os.environ.get("VAST_API_KEY")
    mine = []
    if key:
        insts = _vast_request("GET", "/instances/", key).get("instances", [])
        mine = [i for i in insts if (i.get("label") or "").startswith(LABEL_PREFIX)]

    def _superseded(lid, doc):
        """Is this failure from an attempt older than the host currently working that leg? Pure."""
        for i in mine:
            if label_matches_leg(i.get("label"), lid) and not _record_is_newer_than_instance(doc, i):
                return True
        return False

    print(f"[collect] {len(done)} finished leg(s), {len(partial)} in progress")
    for lid, doc in sorted(done.items()):
        print(f"  DONE  {lid}: dG = {doc.get('dg_kcal'):.3f} +/- {doc.get('dg_mbar_se_kcal'):.3f} kcal/mol "
              f"({doc.get('gpu_hours')} GPU-h, {doc.get('n_particles')} particles)")
    for lid, doc in sorted(partial.items()):
        # Progress is reported in whatever unit the ENGINE advances in: openmmtools legs count
        # replica-exchange iterations, pmx/GROMACS legs count lambda windows. Printing the wrong
        # one showed "0/None iters" for a leg that was in fact four windows in and healthy — a
        # progress board that under-reports progress is worse than none, because it reads as a stall.
        if doc.get("windows_done") is not None or doc.get("n_states"):
            done_n, total_n, unit = doc.get("windows_done", 0), doc.get("n_states"), "windows"
        else:
            done_n, total_n, unit = doc.get("iterations_done", 0), doc.get("prod_iters_target"), "iters"
        print(f"  ....  {lid}: {doc.get('status')} {done_n}/{total_n} {unit}"
              + (f" — {doc.get('error')}" if doc.get("status") == "failed" else ""))
        # WHEN the record was written, always — not only on failure. Without it a `failed` record is
        # ambiguous between "the fix did not work" and "this is a stale record from the attempt before
        # the fix, still sitting in S3 because the new leg has not got far enough to overwrite it."
        # Those two readings call for opposite actions, and only the timestamp separates them. The
        # reap already reasons about this (_record_is_newer_than_instance); the board did not show it.
        print(f"        record: updated_utc={doc.get('updated_utc')} started_utc={doc.get('started_utc')} "
              f"s3_mtime={doc.get('_s3_last_modified')} driver={doc.get('driver_sha256')}")
        if doc.get("status") == "failed":
            if _superseded(lid, doc):
                # A failure older than the host now working this leg is history, not news. It stays
                # in S3 until the running attempt overwrites it, so reprinting its traceback on every
                # poll buries the live signal under a fixed bug. One line, and the timestamps above
                # are still there for anyone who wants to check the claim.
                print("      (stale: predates the host currently on this leg — traceback suppressed)")
                continue
            # Otherwise print the FULL traceback, not just the exception line. A one-line summary
            # tells you WHAT failed; only the traceback tells you WHERE, and on a rented host the
            # difference is another paid round trip. (This is what turned "No module named openeye"
            # from a guess about which import pulls it into a locatable frame.)
            print(f"      platform={doc.get('platform')} charge_method={doc.get('charge_method')} "
                  f"n_particles={doc.get('n_particles')}")
            for ln in str(doc.get("traceback", "(no traceback recorded)")).splitlines():
                print(f"      T| {ln[:200]}")

    n_up = len(mine)
    if key:
        for i in mine:
            label, iid = i.get("label"), i.get("id")
            up_h = 0.0
            try:
                import time as _t
                up_h = (_t.time() - float(i.get("start_date") or _t.time())) / 3600.0
            except (TypeError, ValueError):
                pass
            cost = up_h * float(i.get("dph_total") or 0)
            print(f"  vast {iid} ({label}) {i.get('actual_status')} up={up_h:.2f}h "
                  f"dph={i.get('dph_total')} spent~${cost:.2f}")
            # WHY it is in that state, when the state is not `running`. `loading` for thirty minutes
            # and `loading` for thirty seconds print identically otherwise, and the first is a paid
            # stall while the second is normal. Vast carries the reason in status_msg (image pull
            # progress, a disk-space refusal, a docker auth failure) and the host's own bandwidth
            # tells you whether a multi-GB pull at this size is plausible or the host is simply bad.
            if i.get("actual_status") != "running":
                print(f"      why: cur_state={i.get('cur_state')} intended={i.get('intended_status')} "
                      f"msg={str(i.get('status_msg') or '').strip()[:200]!r}")
                print(f"      host: inet_down={i.get('inet_down')}Mbps disk={i.get('disk_space')}GB "
                      f"image={str(i.get('image_uuid') or '')[-60:]}")
                # FULL record, on request. This is what identified the create/start race: the curated
                # fields above could not explain `intended=stopped` on a host nobody asked to stop,
                # and min_bid=0.24 vs our 0.3015 price — visible only in the full dump — is what ruled
                # out "outbid" and made the nudge the right action instead of a re-rent. Default OFF
                # because it buries the rest of the board; PROTFEP_FORENSIC=1 for the next mystery.
                if os.environ.get("PROTFEP_FORENSIC", "0") != "0":
                    for k in sorted(i):
                        v = str(i[k])
                        print(f"        . {k} = {v[:160]}")
            finished = any(label_matches_leg(label, k) for k in done)
            # Reap a FAILED leg's host too. The container normally exits and the key-free EXIT trap
            # halts billing on its own, but "normally" is doing real work in that sentence — a host
            # that keeps the container alive after a crash would otherwise bill until the runtime
            # backstop hours later, and a failed leg has nothing left to produce.
            # A `failed` record only justifies reaping if it belongs to THIS instance. A stale
            # failure from a previous attempt sits in S3 until the new leg overwrites it, which does
            # not happen until after the image pull and repo clone — so reaping on the record alone
            # destroys a freshly launched host that has not started yet. That is exactly what
            # happened to the complex leg: killed 25 minutes into its image pull, on the strength of
            # a failure from an attempt 90 minutes earlier.
            crashed = any(label_matches_leg(label, k) and _record_is_newer_than_instance(d, i)
                          for k, d in partial.items() if d.get("status") == "failed")
            if autostop and (finished or crashed or up_h > MAX_INSTANCE_HOURS):
                why = ("leg done" if finished else
                       "leg FAILED — nothing left to produce" if crashed else "runtime backstop")
                print(f"    -> destroying {iid} ({why})")
                try:
                    _vast_request("DELETE", f"/instances/{iid}/", key)
                except Exception as e:  # noqa: BLE001
                    print(f"    destroy failed: {e}")
            elif i.get("cur_state") == "stopped" and up_h * 60 > MAX_STOPPED_MIN:
                # A nudge that has not taken in this long is not going to. Destroy and let the next
                # dispatch rent a different box. Without this bound the nudge below is an unbounded
                # restart loop — and it would become a PAID one the moment label_matches_leg failed
                # to pair a done leg with its host, since the reap above would never fire and the
                # container would exit on its idempotency check, go stopped, and be nudged again.
                print(f"    -> destroying {iid} (stopped for {up_h * 60:.0f} min; nudge is not taking)")
                try:
                    _vast_request("DELETE", f"/instances/{iid}/", key)
                except Exception as e:  # noqa: BLE001
                    print(f"    destroy failed: {e}")
            elif i.get("cur_state") == "stopped":
                # SELF-HEAL the create/start race. Creating a Vast ask does not reliably launch the
                # container — the start PUT can be lost while Vast is still finishing the create,
                # leaving the box at cur_state="stopped" forever: never running, never billing GPU,
                # never producing anything. gpu_backend._ensure_running retries only ~48 s at submit
                # time, which is not always long enough. Diagnosed first on the congeneric s1f lane;
                # this lane hit the same thing on the complex leg, which sat stopped for 36 minutes
                # with its image pull frozen at "Waiting" and no layer ever downloading.
                #
                # Deliberately a WIDER trigger than s1f's (which also required an empty status_msg):
                # our box carried a non-empty one — a frozen snapshot of the moment the pull was
                # queued — so status_msg does not discriminate. `cur_state == "stopped"` after the
                # reap checks is enough: a finished or crashed leg was already destroyed above, and
                # an OUTBID instance carries intended_status == "running", so a nudge there is a
                # harmless no-op rather than a wrong action. Re-issuing start is idempotent.
                try:
                    _vast_request("PUT", f"/instances/{iid}/", key, body={"state": "running"})
                    print(f"    -> NUDGED {iid}: cur_state=stopped with no result yet, re-issued start")
                except Exception as e:  # noqa: BLE001
                    print(f"    nudge failed: {e}")
    return n_up, len(done)


def stop_all():
    """Destroy every instance of this lane (anti-idle backstop)."""
    key = os.environ["VAST_API_KEY"]
    insts = _vast_request("GET", "/instances/", key).get("instances", [])
    n = 0
    for i in insts:
        if (i.get("label") or "").startswith(LABEL_PREFIX):
            print(f"destroying {i.get('id')} ({i.get('label')})")
            try:
                _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
                n += 1
            except Exception as e:  # noqa: BLE001
                print(f"  failed: {e}")
    print(f"destroyed {n}")
    return n


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Launch the 5a-KS known-answer benchmark on Vast.ai")
    ap.add_argument("--mode", choices=sorted(MODES), default=os.environ.get("PROTFEP_MODE", "pilot"))
    ap.add_argument("--n-replicas", type=int, default=int(os.environ.get("PROTFEP_N_REPLICAS", "3")))
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--stop", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if args.stop:
        stop_all()
    elif args.collect:
        collect()
    else:
        submit(mode=args.mode, n_replicas=args.n_replicas, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
