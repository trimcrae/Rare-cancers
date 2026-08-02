#!/usr/bin/env python3
"""5a-KS protein-mutation FEP — Vast.ai launcher for the known-answer qualification benchmark.

WHAT THIS RUNS AND WHY IT IS THE NEXT TEST
------------------------------------------
nr4a3-program-map.md's ladder has exactly one rung that is not merely unpriced but *unscoped*: 5a-KS, the
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
import vast_stopped_resume_measure as _srm  # noqa: E402
from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend, measured_min_cuda  # noqa: E402
# The measured-throughput helpers behind the 2026-07-24 $/ns selection work. Imported rather than
# re-derived so this lane's bid ceiling and the launcher's offer ranking can never disagree about
# what a card is worth — a second copy of the table is a second thing to forget to update.
from gpu_backend import (  # noqa: E402
    _vast_offer_query as gb_vast_offer_query,
    measured_ns_per_day as gb_measured_ns_per_day,
    offer_usd_per_ns as gb_offer_usd_per_ns,
)

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
# ★★ NOW DERIVED FROM A MEASUREMENT (2026-07-28). The original sizing argument — "the complex leg's host sat
# stopped for 36 minutes with a frozen image pull, so the bound has to exceed a legitimate slow pull" — is a
# LOWER bound from one incident and says nothing about where the upper bound belongs. The upper bound is a
# question about how often a stopped box comes back, and `vast_stopped_resume_measure` measured it across
# every committed revision of the fleet census: 15 of 55 never-started episodes resumed, Kaplan-Meier 34 %
# by 45 min and 61 % by 90 min, with resumes observed as late as 93.0 min. A stopped box bills storage only
# (~$0.011-0.022/hr depending on the disk), so waiting out that distribution costs cents while destroying
# early forfeits the staged disk. One home for the figure: `vast_stopped_resume_measure.hold_minutes()`.
MAX_STOPPED_MIN = float(os.environ.get("PROTFEP_MAX_STOPPED_MIN")
                        or _srm.hold_minutes(default=45))
# How long an instance may show the SAME status_msg while cur_state is running before its image pull
# is judged dead rather than queued. The apo leg's host pulled the same ~6 GiB image and started
# sampling well inside this; a docker layer legitimately waits a minute or two behind its peers.
MAX_FROZEN_MIN = float(os.environ.get("PROTFEP_MAX_FROZEN_MIN") or "15")

# A solvated barnase-barstar complex is ~30-35k atoms and the apo barstar leg ~15-20k — small
# systems by this repo's standards (the ternary hybrid is 146k). The 4090 is the measured $/ns
# winner at every size in gpu_md_bench, and at this size nothing is VRAM- or host-RAM-bound, so a
# modest host spec keeps the cheap 4090 offers in play instead of filtering down to the expensive
# high-demand hosts. min_cuda 13.0 is the repo's settled host filter: a newer driver runs older PTX
# fine, whereas an older driver hit CUDA_ERROR_UNSUPPORTED_PTX_VERSION on this stack twice before.
# ⚠ `min_cuda` IS THIS IMAGE'S OWN MEASUREMENT (2026-07-31). `probe_image_cuda.py` measured the TERNARY
# image at 12.6 — the `cuda-version=12.6` pin did take there — but this lane runs `pmxfep`, a different stack,
# and inheriting that number would be the same mistake as inheriting a Dockerfile's claim. Until the probe has
# run inside `pmxfep`, `measured_min_cuda` returns the conservative 13.0 this line used to type.
RES = ResourceSpec(gpu=os.environ.get("PROTFEP_GPU") or "rtx4090",
                   min_vram_gb=int(os.environ.get("PROTFEP_VRAM") or "24"),
                   vcpus=4, ram_gb=16, disk_gb=40, interruptible=True,
                   min_cuda=measured_min_cuda(VAST_IMAGE))

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


def stall_minutes(prev, iid, status_msg, now):
    """How long this instance has been showing this EXACT status_msg. Pure.

    collect() is stateless between CI runs, so it cannot tell "unchanged for six minutes" from
    "unchanged for an hour" — and that is the whole difference between a docker layer queued behind
    two others and a pull that has died. `prev` is the previous run's {iid: [msg, first_seen_epoch]}
    map; a changed message resets the clock. Returns (minutes, new_entry).
    """
    key = str(iid)
    old = (prev or {}).get(key)
    if not isinstance(old, (list, tuple)) or len(old) != 2:
        old = None                                   # e.g. the _blocked_machines bookkeeping entry
    if old and old[0] == status_msg:
        return (now - float(old[1])) / 60.0, [status_msg, float(old[1])]
    return 0.0, [status_msg, now]


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


def blocked_machine_ids(bucket=None, prefix=None):
    """Machines observed refusing starts with `resources_unavailable`. [] if unavailable.

    Recorded by collect() and consumed here so a host that cannot schedule us stops winning
    selection. It is the availability term the $/ns ranking has no way to express: a machine that
    never starts has infinite realised cost per ns, yet reads as the cheapest offer on the board.

    ⛔ RETIRED (trimcrae, 2026-07-31: "You've gotta just stop doing the blacklist. It seems like it only
    ever bites us in the ass and clearing it always makes things better."). Returns [] unless
    `VAST_DURABLE_EXCLUSIONS=1`; the switch and the evidence have one home, in `vast_machine_blacklist`.
    Bounded protection is unchanged: `submit`'s in-call capacity-refusal skip, and `used_machines` below.
    """
    try:
        import vast_machine_blacklist as _vmb0
        if not _vmb0.durable_enabled():
            return []
    except Exception:  # noqa: BLE001 — no module, no exclusions
        return []
    try:
        import boto3
    except ImportError:
        return []
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    try:
        st = json.loads(boto3.client("s3").get_object(
            Bucket=b, Key=f"{p}/_lane_state.json")["Body"].read())
        return [str(m) for m in (st.get("_blocked_machines") or [])]
    except Exception:  # noqa: BLE001 — no state yet, or unreadable; exclude nothing
        return []


def completed_leg_ids(bucket=None, prefix=None):
    """Leg ids whose result is already `done` in S3. Needs live AWS creds; [] if unavailable."""
    try:
        import boto3
    except ImportError:
        # LOUD, because this branch spends money. Degrading to "launch everything" is the right
        # failure direction — a listing problem must never block a real launch — but silently it
        # looks identical to "nothing was finished", and on 2026-07-25 it paid for a fresh 4090 to
        # rediscover that the apo leg had completed hours earlier. The caller's CI installs boto3
        # precisely so this line is never reached.
        print("[launch] WARNING: boto3 unavailable, cannot check which legs are already done — "
              "launching EVERY leg for this mode, including any that have already finished")
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
        # Hosts that refused a start with `resources_unavailable`. Excluded here rather than left to
        # the $/ns ranking, which cannot see availability and would keep re-picking the cheapest
        # machine that never runs us.
        bad = blocked_machine_ids()
        if bad:
            RES.exclude_machine_ids = tuple(bad)
            print(f"[launch] excluding {len(bad)} machine(s) known to refuse starts: {bad}")
        finished = set(completed_leg_ids())
        # AND legs that are already RUNNING. `finished` only covers legs whose result is in S3, so a
        # re-launch fired while a fleet was still working re-rented every in-flight leg: on
        # 2026-07-25 a 10-leg relaunch meant to replace 3 destroyed hosts re-rented all 10, putting
        # two instances on each live leg_id — same S3 key, same work, double the bill. A leg is
        # "already being worked" if it is done OR a lane instance is currently labelled for it.
        inflight = set()
        key = os.environ.get("VAST_API_KEY")
        if key:
            try:
                for i in _vast_request("GET", "/instances/", key).get("instances", []):
                    label = i.get("label") or ""
                    if not label.startswith(LABEL_PREFIX):
                        continue
                    for sp in specs:
                        if label_matches_leg(label, leg_id_for(sp, mode)):
                            inflight.add(leg_id_for(sp, mode))
            except Exception as e:  # noqa: BLE001 — never block a launch on a listing failure
                print(f"[launch] could not list live instances ({type(e).__name__}: {e}); "
                      "cannot skip in-flight legs, duplicates are possible")
        busy = finished | inflight
        keep = [s for s in specs if leg_id_for(s, mode) not in busy]
        skipped = [leg_id_for(s, mode) for s in specs if leg_id_for(s, mode) in finished]
        if skipped:
            print(f"[launch] skipping {len(skipped)} already-finished leg(s), no rental: {skipped}")
        if inflight:
            print(f"[launch] skipping {len(inflight)} leg(s) already running, no rental: "
                  f"{sorted(inflight)}")
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
    # ONE LEG PER MACHINE WITHIN A FLEET. Offers are per GPU slot, so selection happily picks the same
    # cheapest-$/ns machine for several legs — but a host advertising slots it cannot actually
    # schedule accepts every rental and then refuses every start. Observed 2026-07-25: machine 53989
    # took two legs of the same fleet and answered resources_unavailable for both, and machine 11892
    # a third. Spreading costs almost nothing (the market has ~23 hosts and the floor is flat) and
    # removes a failure mode that scales with fleet width. The exclusion is per-launch and additive
    # to the persistent blocked list, which stays in place.
    used_machines = set(RES.exclude_machine_ids or ())
    for j in jobspecs:
        try:
            RES.exclude_machine_ids = tuple(used_machines)
            h = backend.submit(j)
            mid = h.extra.get("machine_id")
            if mid is not None:
                used_machines.add(str(mid))
            print(f"[launch] {j.name}: instance={h.job_id} offer={h.extra.get('offer')} "
                  f"machine={mid} dph={h.extra.get('dph')}")
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

    # Previous run's status_msg-per-instance, so a frozen phase is measurable rather than eyeballed.
    # Kept in S3 because CI runners are ephemeral; a missing or unreadable file just resets the clock.
    prev_state, new_state = {}, {}
    blocked = set()
    try:
        prev_state = json.loads(s3.get_object(Bucket=b, Key=f"{p}/_lane_state.json")["Body"].read())
    except Exception:  # noqa: BLE001 — first run, or the object was pruned
        prev_state = {}

    # DEDUPE: at most one live instance per leg. A launch fired while a fleet was still working can
    # put two instances on one leg_id — they write the same S3 key, do the same work, and bill twice.
    # Keep the OLDEST (it has the most progress and its checkpoints are already in S3) and destroy
    # the rest. Done before the per-instance pass so a duplicate is not also nudged or rebid.
    if key and mine:
        by_leg = {}
        for i in mine:
            by_leg.setdefault(i.get("label") or "", []).append(i)
        for label, group in by_leg.items():
            if len(group) < 2:
                continue
            group.sort(key=lambda x: float(x.get("start_date") or 0))
            keep_inst, dupes = group[0], group[1:]
            print(f"  DUPLICATE {label}: {len(group)} instances; keeping {keep_inst.get('id')} "
                  f"(oldest), destroying {[d.get('id') for d in dupes]}")
            for d in dupes:
                try:
                    _vast_request("DELETE", f"/instances/{d.get('id')}/", key)
                except Exception as e:  # noqa: BLE001
                    print(f"    destroy {d.get('id')} failed: {e}")
            mine = [x for x in mine if x not in dupes]

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
            msg = str(i.get("status_msg") or "").strip()
            frozen_min, new_state[str(iid)] = stall_minutes(prev_state, iid, msg, time.time())
            if i.get("actual_status") != "running":
                print(f"      why: cur_state={i.get('cur_state')} intended={i.get('intended_status')} "
                      f"msg={msg[:200]!r} unchanged_for={frozen_min:.0f}min")
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
            elif (i.get("actual_status") != "running" and i.get("cur_state") == "running"
                  and frozen_min > MAX_FROZEN_MIN):
                # RUNNING at the control plane but stuck below it: same status_msg for this long
                # means the image pull has died rather than queued. Docker pulls a few layers at a
                # time, so a layer sitting at "Waiting" for a minute or two is normal and a changed
                # message resets the clock — but nothing legitimate holds one message this long on a
                # host advertising hundreds of Mbps. Re-renting costs a fresh pull; NOT re-renting
                # costs the same pull plus everything already burned waiting for it.
                print(f"    -> destroying {iid} (status frozen {frozen_min:.0f} min at {msg[:60]!r}; "
                      f"pull is dead, not queued)")
                try:
                    _vast_request("DELETE", f"/instances/{iid}/", key)
                except Exception as e:  # noqa: BLE001
                    print(f"    destroy failed: {e}")
            elif i.get("cur_state") == "stopped":
                # SELF-HEAL the create/start race, and TELL THE TWO CASES APART.
                #
                # Creating a Vast ask does not reliably launch the container — the start PUT can be
                # lost while Vast finishes the create, leaving a box that never runs, never bills GPU
                # and never produces anything (gpu_backend._ensure_running retries only ~48 s, which
                # is not always long enough). Re-issuing start is idempotent, so it is safe to retry.
                #
                # But a stopped box has a SECOND, completely different cause, and the two demand
                # opposite actions. Vast answers a start it cannot satisfy with HTTP 200 and
                # {"success": false, "error": "resources_unavailable", "msg": "...state change
                # queued."} — the machine has no free GPU and our start is QUEUED, not refused. That
                # is a capacity wait, and this repo's standing rule is to wait those out: a queued
                # instance bills storage only (instance.gpuCostPerHour is 0, confirmed in the record)
                # and starts on its own when a slot frees.
                #
                # The response body is the only thing that separates them, and discarding it is how
                # this lane got it backwards: an earlier version of this guard destroyed a host after
                # 45 stopped minutes as "nudge is not taking" when it was in fact waiting for
                # capacity — and would have destroyed every replacement for the same reason, since
                # the cause was never the host.
                err = None
                try:
                    resp = _vast_request("PUT", f"/instances/{iid}/", key, body={"state": "running"})
                    err = (resp or {}).get("error")
                    print(f"    -> NUDGED {iid}: cur_state=stopped, re-issued start; "
                          f"vast replied {str(resp)[:300]}")
                except Exception as e:  # noqa: BLE001
                    print(f"    nudge failed: {e}")
                if err == "resources_unavailable":
                    # NOT something to wait out on Vast. The AWS rule this lane first applied ("always
                    # wait out spot capacity") is written for a managed-spot POOL, where you have no
                    # host choice and waiting is the only move. Vast is not a pool: ~23 independently
                    # priced hosts are visible at once, and the 2026-07-24 reservation-price
                    # retraction settles it — "you do not wait for a price, you pick a host". The
                    # price history says the same from the other side: the floor is FLAT, so queueing
                    # behind one occupied machine buys nothing a different host would not give now.
                    #
                    # Bidding more does not help either — verified by doing it: raising this leg's bid
                    # 26% to its value ceiling left it queued exactly as before.
                    #
                    # So record the machine and move on. A host that refuses starts has infinite
                    # realised $/ns, which the $/ns ranking cannot see, so without this it keeps
                    # winning selection and keeps failing to start.
                    blocked.add(str(i.get("machine_id")))
                    print(f"    (machine {i.get('machine_id')} has no free GPU and no bid fixes it — "
                          f"recorded as blocked)")
                    print(f"    -> destroying {iid}: picking another host beats queueing on this one")
                    try:
                        _vast_request("DELETE", f"/instances/{iid}/", key)
                    except Exception as e:  # noqa: BLE001
                        print(f"    destroy failed: {e}")
                elif up_h * 60 > MAX_STOPPED_MIN:
                    # Not a capacity wait, and the nudge has not taken in this long. Destroy so the
                    # next dispatch rents a different box. The bound also stops the nudge becoming an
                    # unbounded restart loop, which would turn PAID the moment label_matches_leg
                    # failed to pair a done leg with its host: the reap would never fire, the
                    # container would exit on its idempotency check, go stopped, and be nudged again.
                    print(f"    -> destroying {iid} (stopped {up_h * 60:.0f} min, not a capacity "
                          f"wait; nudge is not taking)")
                    try:
                        _vast_request("DELETE", f"/instances/{iid}/", key)
                    except Exception as e:  # noqa: BLE001
                        print(f"    destroy failed: {e}")

    # Persist the status_msg clock for the next poll. Best-effort on purpose: failing to write a
    # monitoring aid must never fail a collect, and a lost file only costs one reset of the clock.
    try:
        # ★★ WAVE-SCOPED, NOT CUMULATIVE — the same correction the ternary lane took on 2026-07-27, applied
        # here because this list is the same shape and feeds the same reader. It was `prior | blocked`, a
        # union with every previous tick, so it only ever grew. The ONLY thing that adds to `blocked` is the
        # `resources_unavailable` branch above, i.e. the whole set is the PERISHABLE capacity class: "this
        # machine's GPU was busy on this tick", not a property of the host. Carrying that forward is what
        # made our own filter — not price — the binding constraint on placement across three lanes, and it
        # would have regrown this lane's contribution to the shared set within a day of the clear.
        # Re-testing is nearly free: a failed submit costs no rental and no billing.
        _prior_blocked = set((prev_state.get("_blocked_machines") or []) if isinstance(
            prev_state.get("_blocked_machines"), list) else [])   # read for the readout only; NOT re-persisted
        new_state["_blocked_machines"] = sorted(blocked)
        if _prior_blocked - blocked:
            print(f"[collect] {len(_prior_blocked - blocked)} machine(s) FORGOTTEN from the block list "
                  f"({sorted(_prior_blocked - blocked)}) — they refused on an earlier tick and are not "
                  f"refusing now, so they are selectable again. Capacity refusals bound a wave, not a lane.")
        s3.put_object(Bucket=b, Key=f"{p}/_lane_state.json",
                      Body=json.dumps(new_state, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[collect] could not persist lane state: {e}")
    return n_up, len(done)


def value_ceiling_bid(gpu_name, best_alt_usd_per_ns):
    """Highest $/hr at which THIS card still beats the best alternative on cost per ns of MD. Pure.

    This is the merged $/ns work applied to the bid rather than only to the offer choice. Selection
    already ranks hosts by `offer_usd_per_ns` — cost per unit of finished work, which is what actually
    decides spend — but the BID is then set by a fixed `min_bid x VAST_BID_FLOOR_MULT`, a constant that
    knows nothing about the card it is bidding on. So a slow card can be bid up past the point where a
    faster one would have been cheaper per ns, and nothing notices.

    The ceiling closes that: bid up to, but never past, the price at which we would rather have rented
    something else. Returns None for a card with no measured throughput — the same refusal
    `measured_ns_per_day` makes, because inventing a proxy throughput is what produced the retracted
    2026-07-24 rankings.
    """
    ns_per_day = gb_measured_ns_per_day(gpu_name)
    if not ns_per_day or not best_alt_usd_per_ns:
        return None
    return float(best_alt_usd_per_ns) * (ns_per_day / 24.0)


def best_alternative_usd_per_ns(offers, exclude_machine_id=None):
    """Cheapest $/ns available from any OTHER machine in this offer list. Pure.

    "Other" matters: an instance compared against its own machine's offer would price itself as its own
    alternative and the ceiling would collapse to the current bid.
    """
    best = None
    for o in offers:
        if exclude_machine_id is not None and str(o.get("machine_id")) == str(exclude_machine_id):
            continue
        if o.get("rentable") is False or int(o.get("num_gpus", 1) or 1) != 1:
            continue
        floor = o.get("min_bid")
        if floor is None:
            continue
        upn = gb_offer_usd_per_ns(o.get("gpu_name"), floor)
        if upn is not None and (best is None or upn < best):
            best = upn
    return best


def rebid(mult=None, dry_run=False):
    """Raise the bid on this lane's non-running instances, bounded by measured $/ns value.

    ⚠ READ THIS BEFORE REACHING FOR IT: **it does NOT unstick a queued leg.** This was built on the
    hypothesis that a `resources_unavailable` wait is an auction you can outbid. That hypothesis was
    tested on 2026-07-25 and FALSIFIED — the stuck leg's bid was raised 26% to its value ceiling and
    the instance stayed queued exactly as before. The right response to a queued start is to pick
    another host (see `collect`), not to bid more.

    That negative result independently corroborates what main's own bid policy asserts:
    `vast_cost_model.recommended_bid` deliberately bids the floor plus a staleness TICK rather than
    any multiple, on the reasoning that "the machines we rent are idle, so there is no incumbent bid
    to beat". Two separate lines of evidence now say the margin does not buy priority.

    SO WHAT IS IT STILL FOR? The value CEILING, which is the reusable part: if a bid is ever raised —
    by the escape hatch `VAST_BID_FLOOR_MULT`, or by a future policy that does buy retention — it
    must not be raised past the point where a faster card would have been cheaper per ns of finished
    MD. `value_ceiling_bid` is that bound and it is independent of why the bid moved.

    The question a fixed multiple cannot answer is how much more is still worth paying. This one can:
    bid up to the point where this card's cost per ns of finished MD equals the best alternative on the
    market right now, and no further. Past that ceiling we should be renting the other machine instead,
    which is precisely what `_select_cheapest_offer` would do on the next launch.

    Changing the bid in place beats destroy-and-relaunch: it keeps the instance, its disk and its place
    in the queue, and costs one API call.
    """
    key = os.environ["VAST_API_KEY"]
    target_mult = float(mult if mult is not None else os.environ.get("PROTFEP_REBID_MULT") or "1.9")
    insts = _vast_request("GET", "/instances/", key).get("instances", [])
    mine = [i for i in insts if (i.get("label") or "").startswith(LABEL_PREFIX)]
    if not mine:
        print("[rebid] no instances on this lane")
        return 0
    offers = []
    try:
        q = gb_vast_offer_query(RES)
        offers = _vast_request("GET", "/search/asks/", key,
                               params={"q": json.dumps(q)}).get("offers", [])
    except Exception as e:  # noqa: BLE001 — without a market we simply have no ceiling; say so
        print(f"[rebid] could not fetch offers ({type(e).__name__}: {e}); no value ceiling available")

    n = 0
    for i in mine:
        iid, gpu = i.get("id"), i.get("gpu_name")
        if i.get("actual_status") == "running" and i.get("cur_state") == "running":
            print(f"[rebid] {iid} ({gpu}) already running — left alone")
            continue
        floor = i.get("min_bid")
        if floor is None:
            print(f"[rebid] {iid}: no min_bid reported, skipping")
            continue
        floor = float(floor)
        wanted = floor * target_mult
        alt = best_alternative_usd_per_ns(offers, exclude_machine_id=i.get("machine_id"))
        ceiling = value_ceiling_bid(gpu, alt)
        # The on-demand price of the same machine remains a hard cap: paying more than simply buying
        # the box outright, while STILL being preemptible, is strictly dominated.
        od = i.get("dph_base_ondemand") or None
        bid = wanted
        why = f"{target_mult:g}x floor"
        if ceiling is not None and ceiling < bid:
            bid, why = ceiling, f"value ceiling vs best alternative ${alt:.6f}/ns"
        if od and float(od) < bid:
            bid, why = float(od), "on-demand cap"
        bid = round(max(bid, floor), 4)
        cur = gb_offer_usd_per_ns(gpu, bid)
        print(f"[rebid] {iid} ({gpu}) floor ${floor:.4f} -> bid ${bid:.4f} ({why})"
              + (f"; ${cur:.6f}/ns" if cur else "; $/ns unknown for this card"))
        if dry_run:
            continue
        try:
            resp = _vast_request("PUT", f"/instances/bid_price/{iid}/", key,
                                 body={"client_id": "me", "price": bid})
            print(f"          vast replied {str(resp)[:200]}")
            n += 1
        except Exception as e:  # noqa: BLE001
            print(f"          rebid failed: {e}")
    return n


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
    ap.add_argument("--rebid", action="store_true",
                    help="raise the bid on non-running lane instances, bounded by measured $/ns value")
    ap.add_argument("--rebid-mult", type=float, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if args.rebid:
        rebid(mult=args.rebid_mult, dry_run=args.dry_run)
    elif args.stop:
        stop_all()
    elif args.collect:
        collect()
    else:
        submit(mode=args.mode, n_replicas=args.n_replicas, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
