#!/usr/bin/env python3
"""Ternary cooperativity FEP — Vast.ai lane (RUNG 2b: the 4 fs adoption test, and every ternary leg after it).

WHY THIS LANE EXISTS
--------------------
trimcrae's 2026-07-25 directive is that **all production GPU runs go on Vast**. Until now the ternary
cooperativity FEP had exactly two execution paths — `gpu-ternary-fep-gcp.yml` (the L4 lane valB_mini ran
on, pinned to a 1-GPU quota) and a dormant SageMaker one — plus a *script-shaped* Vast path buried in
`nrv04_vast_launch.py firm`, which rents one host, runs a 60-iteration timing probe, and has no
checkpoint/resume, no stage/pre-equil cache, no reap policy and no watchdog. None of that is a lane you
can put a 10-hour science leg on.

This module is that lane. It is deliberately modelled on `protfep_vast_launch.py`, whose selection, bid,
reap and blocked-machine policies were paid for in real money on 2026-07-24/25; where a policy already
exists there, this file imports it rather than writing a second copy that can disagree.

WHAT IT RUNS, AND WHY THE INVOCATION LOOKS LIKE THAT
---------------------------------------------------
One Vast instance == one alchemical leg, via `run_ternary_leg.sh` — the single-source-of-truth recipe.
This file must NEVER re-implement that invocation: a hand-copied duplicate is precisely what made the
last Vast ternary attempt run 16 λ-windows and NaN where the proven recipe uses 12.

The RUNG 2b question is whether ternary production is stable at **4 fs** instead of 2 fs. Iterations are
timestep-independent (OpenFE derives them as production_length / time_per_iteration, and `time_per_iteration`
is fixed), so 4 fs halves the force evaluations *in production*. It does NOT halve the leg: the warmup runs
at 1 fs and its iteration count is derived from the WARMUP integrator's dt, so a 1 ns equilibration is 1e6
steps at either production timestep. See `ternary_cost_model()` below — this is the reason the naive
"~$8.8 -> ~$4.4" halving is optimistic, and the reason this lane measures the two phases separately.

Three flags carry the experiment, all load-bearing:
  use_preequil (implicit here: this lane ALWAYS pre-equilibrates)  — 4 fs held in the runbook's §1c
        demonstration *only because* the physical complex was relaxed by plain MD first. Without it every
        prior attempt died at warmup iteration 1.
  timestep_fs=4.0 / warmup_timestep_fs=1.0                          — the thing under test.
  a dt-keyed commit prefix                                          — OpenFE refuses to resume a checkpoint
        whose protocol timestep differs ("Sampler in checkpoint does not match Protocol settings"), so a dt
        change MUST start clean. Keying the prefix by dt makes that structural rather than a flag someone
        has to remember; there is no `reset_commits` to forget.

CACHES (all S3, all keyed so a wrong-dt or wrong-seed artefact can never be silently reused)
  stagecache/     the RCSB fetch + SMARCA2 homology model + assembly (~15 min)
  preequilcache/  the relaxed complex.pdb + ligands.sdf (~10 min of GPU MD)
  commits/        the per-interval MultiState checkpoints (the science; written by the engine itself)
A preempted leg restores all three and resumes from its last committed iteration.

DE-CONFLICTION. Everything this lane writes lives under a `ternary-vast/` S3 prefix and a `tvast-` Vast
label, and it never touches GCS, so it cannot collide with the GCP ternary lane running concurrently in
another session.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend  # noqa: E402
# Pure policy helpers, imported rather than duplicated. `stall_minutes` and
# `_record_is_newer_than_instance` encode two lessons that cost real money on the protfep lane (a frozen
# image pull is only distinguishable from a queued one by how long the SAME status_msg has been showing;
# and a stale `failed` record in S3 will reap a freshly launched host if you do not check whose attempt
# wrote it). Re-deriving them here would mean two policies that can drift apart.
from protfep_vast_launch import (  # noqa: E402
    _record_is_newer_than_instance,
    stall_minutes,
)

REPO = "https://github.com/trimcrae/Rare-cancers"

# NOTE THE `or`, NOT `.get(key, default)`: CI passes an unset workflow input as an EMPTY STRING, which is
# a *set* variable, so a .get() default never fires. That hole once rented a 4090 whose result prefix
# resolved to `s3:///...` and which therefore produced nothing retrievable.
VAST_IMAGE = os.environ.get("TVAST_IMAGE") or "docker.io/triskit23/ternary-fep:latest"
DEFAULT_BUCKET = os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
RESULT_PREFIX = os.environ.get("TVAST_PREFIX") or "ternary-vast"
LABEL_PREFIX = "tvast"

# Backstops. The reap normally fires on "result in S3"; these bound the pathological cases.
MAX_INSTANCE_HOURS = float(os.environ.get("TVAST_MAX_INSTANCE_HOURS") or "22")
MAX_STOPPED_MIN = float(os.environ.get("TVAST_MAX_STOPPED_MIN") or "45")
MAX_FROZEN_MIN = float(os.environ.get("TVAST_MAX_FROZEN_MIN") or "20")

# HOST SPEC. Setup (openff `interchange` parameterising the ~146k-atom solvated hybrid) is CPU+RAM bound,
# and the GCP lane measured a 4x slowdown on a 16 GB / 4 vCPU box versus 32 GB / 8 vCPU — swapping, not
# GPU. Since this lane builds setup on the rented host (there is no S3 setup cache yet), under-specifying
# RAM buys a cheap host and then pays for it in GPU-idle minutes. min_cuda 13.0 is the repo's settled host
# filter: the baked env's PTX is CUDA-13-class and older drivers hit CUDA_ERROR_UNSUPPORTED_PTX_VERSION.
def resource_spec(gpu=None, disk_gb=None):
    """The host filter for a ternary leg. Kept a function so a caller (or a test) can vary the card
    without mutating a module-level singleton that another call already holds a reference to."""
    return ResourceSpec(
        gpu=gpu or os.environ.get("TVAST_GPU") or "rtx4090",
        min_vram_gb=int(os.environ.get("TVAST_VRAM") or "24"),
        vcpus=int(os.environ.get("TVAST_VCPUS") or "8"),
        ram_gb=int(os.environ.get("TVAST_RAM_GB") or "32"),
        disk_gb=int(disk_gb or os.environ.get("TVAST_DISK_GB") or "60"),
        min_cuda=float(os.environ.get("TVAST_MIN_CUDA") or "13.0"),
        interruptible=True,
    )


# =============================================================================================================
# unit planning — PURE (no network, no AWS); this is what the tests exercise
# =============================================================================================================
# A "unit" is one (leg, seed, direction) at one timestep pair. `probe` is the RUNG 2b stage-1 survival test;
# `edge` is stage 2, the full matched re-calibration edge.
#
# WHY THE PROBE USES A SHORT WARMUP. The question stage 1 asks is "does 4 fs production survive well past the
# 40 iterations the runbook demonstrated?", and warmup is 1 fs — it tests nothing about the production
# timestep while costing ~3.5 GPU-hours. Cutting it to 48 iterations reproduces exactly the warmup length of
# the runbook's §1c demonstration (48/48) and makes the probe a STRICTLY HARSHER test of 4 fs than the full
# leg: less equilibrated coordinates entering production. A pass therefore carries over; a fail is
# unambiguous. Stage 2 runs the full derived warmup, matched to the 2 fs run.
#
# WARMUP CHECKPOINT INTERVAL, and why it is per-mode rather than a constant. A checkpoint costs a reporter
# sync plus an ~25 MB .nc/.chk pair copied and PUT to S3, so its cost is fixed per commit while the MD
# between commits is `interval x seconds-per-iteration`. The GCP lane's 8 was chosen against a 2 fs
# warmup; at 4 fs the derived warmup is ~1600 iterations (n_steps per iteration halves, so covering the
# same 1 ns takes twice as many of them), and an interval of 8 would mean ~200 commits — plausibly a
# double-digit percentage of the leg spent committing. `edge` therefore uses 64 (1600/64 = 25 commits,
# first resumable snapshot ~8 min in, which is still far inside a preemption window). `probe` keeps 8,
# both because 48 iterations must stay a multiple of the interval and because a short interval is exactly
# what MEASURES the commit overhead — the probe is where that number comes from rather than a guess.
MODES = {
    "probe": {
        "prod_iters": "200", "warmup_iters": "48", "warmup_ckpt_iters": "8", "prod_ckpt_iters": "40",
        "max_runtime_s": 4 * 3600,
        "legs": [("calib_hi_to_lo__ternary_vhl", 0, "fwd")],
    },
    "edge": {
        "prod_iters": "", "warmup_iters": "",          # empty = full derived science length
        "warmup_ckpt_iters": "64", "prod_ckpt_iters": "40",
        "max_runtime_s": 20 * 3600,
        "legs": [("calib_hi_to_lo__ternary_vhl", 0, "fwd"),
                 ("calib_hi_to_lo__binary_vhl", 0, "fwd"),
                 ("calib_hi_to_lo__solvent", 0, "fwd")],
    },
    # A 12-iteration end-to-end shakeout: proves image + repo pull + stage + pre-equil + setup + commit-store
    # + upload on a real host for ~$0.15, before a real leg is paid for. Its dG is meaningless by construction.
    "smoke": {
        "prod_iters": "12", "warmup_iters": "8", "warmup_ckpt_iters": "8", "prod_ckpt_iters": "4",
        "max_runtime_s": 3 * 3600,
        "legs": [("calib_hi_to_lo__ternary_vhl", 0, "fwd")],
    },
}

DEFAULT_TIMESTEP_FS = "4.0"
DEFAULT_WARMUP_TIMESTEP_FS = "1.0"


def unit_id(leg_id, seed, direction, timestep_fs, warmup_timestep_fs, mode):
    """The identity of one unit of work. PURE.

    Everything downstream is keyed off this string — the S3 result prefix, the Vast label, the commit
    prefix, the watchdog entry — so it must contain every parameter that makes two runs scientifically
    different. The timestep is in it because an MD checkpoint is timestep-specific: OpenFE refuses to
    resume a checkpoint built at another dt, and a prefix that omitted dt would either crash on resume or,
    worse, be "fixed" by someone wiping it. The MODE is in it because probe and edge differ in iteration
    count, and a probe's 200-iteration production must never be mistaken for (or resumed into) a full leg.
    """
    dirsuf = "" if direction == "fwd" else f"_dir{direction}"
    return (f"{leg_id}_r{seed}{dirsuf}_dt{timestep_fs}fs_wu{warmup_timestep_fs}_{mode}")


def unit_label(uid):
    """Vast instance label. PURE. Vast caps labels at 60 chars and we match label->unit by re-deriving,
    never by parsing back — the protfep lane lost a reap to a lossy label that could not round-trip."""
    return f"{LABEL_PREFIX}-{uid}".replace("_", "-").replace(".", "p").lower()[:60]


def label_matches_unit(label, uid):
    """Does this instance label belong to this unit? PURE, and one-directional on purpose.

    A missed match is not cosmetic: `collect` reaps on it, so a failure to pair a finished leg with its
    host leaves a GPU billing until the runtime backstop hours later.
    """
    if not label or not uid:
        return False
    return str(label).strip().lower() == unit_label(uid)


def units_for(mode):
    """The (leg_id, seed, direction) tuples this mode runs. PURE."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {sorted(MODES)}")
    return list(MODES[mode]["legs"])


def commit_prefix(bucket, uid, prefix=None):
    """S3 prefix for this unit's MultiState commit store. PURE."""
    return f"s3://{bucket}/{(prefix or RESULT_PREFIX).rstrip('/')}/commits/{uid}"


def result_prefix_for(bucket, uid, prefix=None):
    """S3 prefix for this unit's artefacts (leg JSON, status, phase marker, log). PURE."""
    return f"s3://{bucket}/{(prefix or RESULT_PREFIX).rstrip('/')}/legs/{uid}"


# =============================================================================================================
# the on-host pipeline
# =============================================================================================================
# Structure: idempotency check -> repo -> stage (cached) -> pre-equilibrate (cached) -> overlay -> MD.
# Every phase writes a marker to S3 so an outside observer can tell WHICH phase is slow, which is the
# distinction that three separate silent stalls on the GCP ternary lane turned on.
_PIPELINE = r"""
set -o pipefail
export HOME=/root
export PATH=/opt/mamba/envs/rbfe/bin:$PATH
# The rbfe env carries no CA bundle for python SSL, so ternary_pdb_stage.py's RCSB fetch fails with
# CERTIFICATE_VERIFY_FAILED and silently yields an EMPTY ligands.sdf (root-caused on the first Vast firm
# run, 2026-07-23). Point SSL at the bundle the Dockerfile's apt ca-certificates installs.
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
exec > >(tee /tmp/run.log) 2>&1
echo "[tvast] $(date -u +%FT%TZ) start unit=$UNIT_ID leg=$LEG_ID seed=$SEED dir=$DIRECTION dt=${RBFE_TIMESTEP_FS}fs warmup_dt=${RBFE_WARMUP_TIMESTEP_FS}fs"

AWSC=$(command -v aws || echo /opt/mamba/envs/rbfe/bin/aws)
mark() { printf '%s %s\n' "$1" "$(date -u +%FT%TZ)" | $AWSC s3 cp - "$RESULT_S3/phase.txt" >/dev/null 2>&1 || true
         $AWSC s3 cp /tmp/run.log "$RESULT_S3/run.log" >/dev/null 2>&1 || true; }
# WHICH FAILURES ARE THE HOST'S FAULT, AND WHICH ARE OURS. This distinction decides whether the watchdog
# relaunches, so it has to be made here where the phase is known — not inferred later from a log.
#   cuda-probe  -> THIS HOST cannot run the job (no CUDA platform, wrong driver). Relaunching ELSEWHERE is
#                  exactly right, so leave no `leg.json`: the unit reads DIED and the launcher picks a
#                  different machine. Only a `status.json` breadcrumb is left, for a human reading the board.
#   anything else -> the code or the data failed, and it will fail identically on the next host. Write
#                  `leg.json` with status=failed so the watchdog's FAILED verdict fires and REFUSES to
#                  relaunch. Without this, a staging or pre-equil bug would buy a fresh rental per attempt,
#                  up to the daily cap, every one dying the same way.
fail() { echo "[tvast] FAILED at $1"
         printf '{"unit_id":"%s","status":"failed","phase":"%s","rc":1,"nan_seen":false,"utc":"%s","updated_utc":"%s"}\n' \
           "$UNIT_ID" "$1" "$(date -u +%FT%TZ)" "$(date -u +%FT%TZ)" > /tmp/status.json
         $AWSC s3 cp /tmp/status.json "$RESULT_S3/status.json" >/dev/null 2>&1 || true
         if [ "$1" != cuda-probe ]; then
           $AWSC s3 cp /tmp/status.json "$RESULT_S3/leg.json" >/dev/null 2>&1 || true
         else
           echo "[tvast] host-side failure ($1) — deliberately NOT writing leg.json so a relaunch picks a different machine"
         fi
         $AWSC s3 cp /tmp/run.log "$RESULT_S3/run.log" >/dev/null 2>&1 || true; exit 1; }
mark start

# PRESERVE THE PREVIOUS ATTEMPT'S LOG BEFORE OVERWRITING IT. `exec > >(tee /tmp/run.log)` starts a fresh
# file, and the sync loop then overwrites `$RESULT_S3/run.log` — so on a resume after preemption the only
# record of WHY the last attempt ended is destroyed by the attempt that replaces it. Lane 3's census of the
# NR-V04 panel is the cost of that pattern: three analysis defects were uncorrectable because nothing
# survived. Costs one S3 copy of a text file.
if $AWSC s3 ls "$RESULT_S3/run.log" >/dev/null 2>&1; then
  $AWSC s3 cp "$RESULT_S3/run.log" "$RESULT_S3/attempts/run-$(date -u +%Y%m%dT%H%M%SZ).log" >/dev/null 2>&1 \
    && echo "[tvast] archived the previous attempt's run.log under attempts/" || true
fi

# IDEMPOTENCY. Vast re-runs onstart when a container restarts, and CI may re-dispatch a unit whose leg
# already landed. Re-running would overwrite a finished result with a fresh (and, at a different commit
# generation, possibly worse) one. Checked BEFORE any GPU work.
if $AWSC s3 ls "$RESULT_S3/leg.json" >/dev/null 2>&1; then
  echo "[tvast] leg.json already in S3 -> nothing to do (awaiting CI reap)"; exit 0
fi

# CUDA REALITY CHECK, up front and fatal. OpenMM silently falling back to the CPU platform on a rented
# GPU is the worst possible outcome: it bills a 4090 to run ~200x slower and looks alive the whole time.
# OPENMM_REQUIRE_CUDA=1 makes the engine refuse, but by then we have already paid for stage + pre-equil.
python - <<'PYEOF' || fail cuda-probe
import openmm, os
plats = [openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())]
print("[tvast] openmm", openmm.__version__, "platforms", plats)
if "CUDA" not in plats:
    # A conda-pack/relocated env loses OpenMM's compiled-in plugin dir; pointing OPENMM_PLUGIN_DIR at this
    # env's plugins restores auto-load for BOTH our driver and OpenFE's internal getPlatformByName("CUDA").
    os.environ["OPENMM_PLUGIN_DIR"] = "/opt/mamba/envs/rbfe/lib/plugins"
    openmm.Platform.loadPluginsFromDirectory(os.environ["OPENMM_PLUGIN_DIR"])
    plats = [openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())]
    print("[tvast] after plugin reload:", plats)
raise SystemExit(0 if "CUDA" in plats else 3)
PYEOF
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true
# WHICH CARD actually ran, recorded into the result. This lane is the first ternary leg on Vast and its
# per-iteration rate is a deliverable; a rate with no card attached cannot be compared to the 4090/3090
# grid and is therefore not a measurement of anything.
export TVAST_GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)"

cd /root
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz || fail repo-pull
cd Rare-cancers-*/research/modalities || fail repo-pull
# WHICH CODE actually ran. The host pulls a codeload tarball, so there is no git sha on disk and the branch
# may have moved between dispatch and container start. A content hash of the two files that define the run
# is the only fingerprint that cannot lie.
export TVAST_CODE_SHA="$(cat run_ternary_leg.sh nr4a3_ternary_fep.py | sha256sum | cut -c1-12)"
echo "[tvast] recipe+engine sha256[:12]=$TVAST_CODE_SHA branch=$GIT_BRANCH image=$VAST_IMAGE_TAG"
mark cloned

export IN=/tmp/tin OUT=/tmp/tout
mkdir -p "$IN" "$OUT"

# --- continuous log/phase sync (every 2 min). The SCIENCE checkpoints do not go through here: the engine's
#     commit store writes them straight to S3 per interval. This loop exists so an outside monitor can read
#     the phase and the log tail of a live host without SSH, which is what makes the watchdog possible. ---
( while true; do sleep 120; $AWSC s3 cp /tmp/run.log "$RESULT_S3/run.log" >/dev/null 2>&1 || true; done ) &
SYNC_PID=$!

# --- STAGE (cached). RCSB fetch + SMARCA4->SMARCA2 homology model + assembly, ~15 min. Seed-keyed because
#     ternary_pdb_stage picks starting_model_index = seed % n_models, so seeds are DIFFERENT structures. ---
mark staging
if $AWSC s3 cp "$STAGE_CACHE" /tmp/stage.tar >/dev/null 2>&1 && tar -C "$IN" -xf /tmp/stage.tar 2>/dev/null; then
  echo "[tvast] stage cache HIT -> $STAGE_CACHE"
else
  echo "[tvast] stage cache MISS -> staging $LEG_ID from $TEMPLATE_PDB"
  SEED=$SEED python ternary_pdb_stage.py --leg-id "$LEG_ID" --template-pdb "$TEMPLATE_PDB" --out "$IN" || fail staging
  tar -C "$IN" -cf /tmp/stage.tar "$LEG_ID" && $AWSC s3 cp /tmp/stage.tar "$STAGE_CACHE" >/dev/null 2>&1 || true
fi
ls -la "$IN/$LEG_ID" || true

# --- PRE-EQUILIBRATION (cached). THE fix for the softcore warmup NaN (runbook 1c): relax the fully
#     interacting physical complex with plain MD before any alchemy. Deterministic given SEED, so a cache
#     hit is byte-identical to a fresh run. A solvent leg has no protein complex to relax, so it is
#     skipped there — and skipping is CORRECT, not a shortcut: the NaN mechanism is the softcore region in
#     a large rough assembly, which a ligand in a water box does not have. ---
if [ "$NEEDS_PREEQUIL" = "1" ]; then
  mark preequil
  if $AWSC s3 cp "$PE_CACHE" /tmp/pe.tar >/dev/null 2>&1 && tar -C "$IN/$LEG_ID" -xf /tmp/pe.tar 2>/dev/null; then
    echo "[tvast] pre-equil cache HIT -> $PE_CACHE (relaxed complex.pdb + ligands.sdf overlaid)"
  else
    echo "[tvast] pre-equil cache MISS -> running ternary_preequil.py (${PREEQUIL_NS} ns)"
    env LEG_ID="$LEG_ID" SEED="$SEED" CHARGE_METHOD="$CHARGE_METHOD" PREEQUIL_NS="$PREEQUIL_NS" \
        PREEQUIL_EXACT_FF=1 OPENMM_PLATFORM=CUDA OPENMM_REQUIRE_CUDA=1 \
        INPUT_DIR="$IN" OUTPUT_DIR="$OUT" python ternary_preequil.py || fail preequil
    cp "$OUT/$LEG_ID/complex.pdb" "$OUT/$LEG_ID/ligands.sdf" "$IN/$LEG_ID/" || fail preequil-overlay
    tar -C "$IN/$LEG_ID" -cf /tmp/pe.tar complex.pdb ligands.sdf \
      && $AWSC s3 cp /tmp/pe.tar "$PE_CACHE" >/dev/null 2>&1 || true
  fi
fi

# --- MD. `run_ternary_leg.sh` is the SINGLE SOURCE OF TRUTH for the recipe; this lane calls it and does not
#     re-implement it (a hand-copied duplicate is what made the last Vast ternary attempt run 16 windows and
#     NaN). SKIP_PREEQUIL=1 because we have already overlaid the relaxed structure above, with a cache.
#     `timeout` rather than autoteardown.py so the runtime cap kills the MD but still lets the final upload
#     below run — wrapping the driver in autoteardown races the poweroff against the deliverable. ---
mark md-running
set +e
timeout -k 120 "${MD_TIMEOUT_S}" env \
  IN="$IN" OUT="$OUT" LEG_ID="$LEG_ID" SEED="$SEED" DIRECTION="$DIRECTION" PY="$(command -v python)" \
  SKIP_PREEQUIL=1 CHARGE_METHOD="$CHARGE_METHOD" N_WINDOWS="$N_WINDOWS" \
  RBFE_TIMESTEP_FS="$RBFE_TIMESTEP_FS" RBFE_WARMUP_TIMESTEP_FS="$RBFE_WARMUP_TIMESTEP_FS" \
  RBFE_MIN_STEPS="$RBFE_MIN_STEPS" RBFE_WARMUP_ITERS="$RBFE_WARMUP_ITERS" RBFE_PROD_ITERS="$RBFE_PROD_ITERS" \
  RBFE_POSITIONS_WRITE_PS="$RBFE_POSITIONS_WRITE_PS" RBFE_VELOCITIES_WRITE_PS="$RBFE_VELOCITIES_WRITE_PS" \
  RBFE_SETUP_CACHE_S3="$RBFE_SETUP_CACHE_S3" SETUP_CACHE_VERSION="$SETUP_CACHE_VERSION" \
  RBFE_REQUIRE_PRIMED_SETUP="$RBFE_REQUIRE_PRIMED_SETUP" \
  RBFE_SPOT_SAFE=1 RBFE_SPOT_COMMIT_S3="$COMMIT_S3" \
  RBFE_WARMUP_CKPT_ITERS="$WARMUP_CKPT_ITERS" RBFE_PROD_CKPT_ITERS="$PROD_CKPT_ITERS" \
  bash run_ternary_leg.sh
export RC=$?      # EXPORTED: the summariser below reads it from the environment, and an unexported RC
                  # silently defaults to 1 there, marking a perfectly good leg `failed`.
# `set -e` is deliberately NOT restored. Everything from here on is the DELIVERABLE path — summarise the
# result, upload it, upload the log — and it must run to completion even when the MD failed. That is
# precisely the case where the log is the only thing worth having, and an -e abort would discard it.
kill $SYNC_PID 2>/dev/null || true
mark md-done
echo "[tvast] MD exit rc=$RC"

# --- DELIVERABLE. The engine writes leg_<leg>_<dir>_r<seed>.json into CKPT_DIR (= $OUT). Normalise it to a
#     single well-known key plus a status record, so `collect` and the watchdog have ONE thing to look for
#     and cannot be fooled by a partial upload. ---
LJ=$(ls "$OUT"/leg_*.json 2>/dev/null | head -1)
python - <<'PYEOF'
import json, os, re, glob
out = os.environ["OUT"]; uid = os.environ["UNIT_ID"]
lj = sorted(glob.glob(os.path.join(out, "leg_*.json")))
doc = {}
if lj:
    try:
        doc = json.load(open(lj[0]))
    except Exception as e:            # noqa: BLE001
        doc = {"_unreadable": repr(e)}
# Per-iteration wall time, straight from the driver's own [timing] lines. This lane is the FIRST ternary
# leg on Vast, and STRATEGY carries the ternary cost base as an 8G1Q rate being reused for NR4A — flagged
# as not transferable until a leg is timed. So the rate is a DELIVERABLE, not a log line, and it is
# recorded per phase because warmup (1 fs) and production (4 fs) have different step counts per iteration.
# PHASE IS TRACKED FROM THE DRIVER'S OWN TRANSITION LINES, not by keyword-sniffing the timing line.
# Warmup runs at 1 fs and production at the leg's dt, so they have DIFFERENT steps per iteration —
# ~2500 vs ~625 at 4 fs. Pooling them would report a meaningless average and would make the 4 fs
# speedup unmeasurable, which is the entire point of this run. `[timing]` also carries the phase
# TARGET (`at iteration 8/48`), captured so a reader can see how far each phase actually got.
timing = {"warmup": [], "production": []}
reached = {"warmup": [0, 0], "production": [0, 0]}
phase = "warmup"
try:
    for ln in open("/tmp/run.log", errors="replace"):
        if "[spot-driver]" in ln and ("PRODUCTION created" in ln or "resume PRODUCTION" in ln
                                      or "FRESH production" in ln):
            phase = "production"
        elif "[spot-driver]" in ln and ("WARMUP from iter" in ln or "RESUME warmup" in ln
                                        or "warmup FRESH" in ln):
            phase = "warmup"
        m = re.search(r"\[timing\]\s+(\d+)\s+iters in\s+([\d.]+)s\s*=\s*([\d.]+)\s*s/iter"
                      r".*?at iteration\s+(\d+)/(\d+)", ln)
        if m:
            timing[phase].append(float(m.group(3)))
            reached[phase] = [int(m.group(4)), int(m.group(5))]
except OSError:
    pass
def _stats(v):
    if not v:
        return None
    s = sorted(v)
    return {"n": len(s), "median_s_per_iter": s[len(s) // 2],
            "min_s_per_iter": s[0], "max_s_per_iter": s[-1],
            "mean_s_per_iter": round(sum(s) / len(s), 3)}
nan_seen = False
try:
    log = open("/tmp/run.log", errors="replace").read()
    nan_seen = ("SimulationNaNError" in log) or ("resulted in a NaN" in log)
except OSError:
    log = ""
rec = {
    "unit_id": uid,
    "leg_id": os.environ.get("LEG_ID"), "seed": int(os.environ.get("SEED", "0")),
    "direction": os.environ.get("DIRECTION"), "mode": os.environ.get("TVAST_MODE"),
    "timestep_fs": float(os.environ.get("RBFE_TIMESTEP_FS", "0") or 0),
    "warmup_timestep_fs": float(os.environ.get("RBFE_WARMUP_TIMESTEP_FS", "0") or 0),
    "n_windows": int(os.environ.get("N_WINDOWS", "12")),
    "charge_method": os.environ.get("CHARGE_METHOD"),
    "warmup_iters_requested": os.environ.get("RBFE_WARMUP_ITERS") or "derived",
    "prod_iters_requested": os.environ.get("RBFE_PROD_ITERS") or "derived",
    "rc": int(os.environ.get("RC", "1")),
    "nan_seen": nan_seen,
    "code_sha256": os.environ.get("TVAST_CODE_SHA"),
    "gpu": os.environ.get("TVAST_GPU_NAME"),
    "timing": {k: _stats(v) for k, v in timing.items()},
    "iters_reached": {k: {"iteration": v[0], "target": v[1]} for k, v in reached.items()},
    "dg_morph_kcal": doc.get("dg_morph_kcal"), "mbar_se_kcal": doc.get("mbar_se_kcal"),
    "protocol_hash": doc.get("protocol_hash"), "starting_model": doc.get("starting_model"),
    "engine_record": doc or None,
    "status": "done" if (doc.get("dg_morph_kcal") is not None and os.environ.get("RC") == "0") else "failed",
    "updated_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
}
if rec["status"] != "done":
    tail = [l for l in log.splitlines() if l.strip()][-40:]
    rec["log_tail"] = tail
json.dump(rec, open("/tmp/leg.json", "w"), indent=2)
print("TVAST_RESULT", json.dumps({k: rec[k] for k in
      ("unit_id", "status", "dg_morph_kcal", "mbar_se_kcal", "nan_seen", "timing", "rc")}))
PYEOF
[ -n "$LJ" ] && $AWSC s3 cp "$LJ" "$RESULT_S3/engine_leg.json" >/dev/null 2>&1 || true
$AWSC s3 cp /tmp/leg.json "$RESULT_S3/leg.json" || echo "[tvast] RESULT UPLOAD FAILED"
$AWSC s3 cp /tmp/run.log "$RESULT_S3/run.log" || true
mark done
echo "[tvast] $(date -u +%FT%TZ) EXIT rc=$RC"
exit $RC
"""


# ★ VAST CAPS THE ONSTART SCRIPT AT 16,384 CHARACTERS, AND SAYS SO ONLY AT RENTAL TIME.
# Diagnosed 2026-07-25 from the API's own reply, not inferred: re-launching the probe after a preemption
# returned HTTP 400
#   {"success":false,"error":"invalid_args",
#    "msg":"error 400/3471: Invalid args: len(image) > 1024, or len(args) > 16384, or len(label) > 256"}
# The rendered onstart had reached 17,017 characters — over by 633 — because the pipeline had grown by three
# safety fixes since the launch that worked. Nothing in the code was wrong; it was simply too long, and the
# failure surfaces as a *submitted-nothing launch that reports success*, which is the worst possible shape:
# the job is green, the watch list is armed, and no GPU is running.
#
# THE FIX IS NOT TO WRITE FEWER COMMENTS. 6,122 of those characters were full-line comments — the part that
# explains why each step exists, which is exactly what this repo has repeatedly paid for losing. So the
# comments stay in the SOURCE and are stripped at RENDER: the annotated pipeline lives in the file, the
# host receives the executable subset. `#`-leading lines are comments in both bash and Python, so the same
# rule is safe inside the embedded heredocs.
MAX_ONSTART_CHARS = 16384


def _render_pipeline(body):
    """Strip full-line comments and blank runs from the shell body. PURE.

    Only lines whose FIRST non-space character is `#` are dropped, so an inline `#` inside a string or a
    command is never touched. Both languages in this script (bash, and the Python heredocs) treat such a
    line as a comment, so the executable meaning is unchanged.
    """
    out, blank = [], False
    for ln in body.splitlines():
        if ln.lstrip().startswith("#"):
            continue
        if not ln.strip():
            if blank:
                continue
            blank = True
        else:
            blank = False
        out.append(ln)
    return "\n".join(out)


def onstart_length(spec):
    """Characters Vast will actually receive for this spec, including the env exports and teardown trap.

    The check has to be on the RENDERED onstart, not on the pipeline: `_vast_onstart` prepends an `export`
    line per env var plus the self-destroy trap, which was ~1.9 kB on the probe. Measuring the pipeline
    alone would have passed at 15,136 characters while the real payload was 17,017.
    """
    from gpu_backend import _object_store_env, _vast_onstart
    from gpu_backend import VastBackend
    return len(_vast_onstart(spec, VastBackend().self_terminate_cmd(), extra_env=dict(_object_store_env())))


def build_jobspec(leg_id, seed=0, direction="fwd", mode="probe", timestep_fs=None,
                  warmup_timestep_fs=None, git_branch=None, bucket=None, prefix=None,
                  charge_method=None, n_windows=None, template_pdb=None, image=None):
    """PURE construction of one unit's JobSpec (no network, no AWS). Unit-tested."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {sorted(MODES)}")
    sizing = MODES[mode]
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    dt = str(timestep_fs or os.environ.get("TVAST_TIMESTEP_FS") or DEFAULT_TIMESTEP_FS)
    wdt = str(warmup_timestep_fs or os.environ.get("TVAST_WARMUP_TIMESTEP_FS") or DEFAULT_WARMUP_TIMESTEP_FS)
    branch = git_branch or os.environ.get("GIT_BRANCH") or "main"
    charge = charge_method or os.environ.get("CHARGE_METHOD") or "nagl"
    nwin = str(n_windows or os.environ.get("TVAST_N_WINDOWS") or "12")
    tpl = template_pdb or os.environ.get("TVAST_TEMPLATE_PDB") or "8G1Q"
    if not b or not p:
        raise ValueError(
            f"refusing to launch with an incomplete result location (bucket={b!r}, prefix={p!r}). A blank "
            f"CI input arrives as an EMPTY STRING, not unset, so a .get() default does not fire — that hole "
            f"once rented a 4090 whose uploads went to 's3:///...' and produced nothing retrievable.")
    uid = unit_id(leg_id, seed, direction, dt, wdt, mode)
    solvent = leg_id.endswith("__solvent")
    env = {
        # ★ THE PROGRESS LINES ARE BLOCK-BUFFERED WITHOUT THIS. Diagnosed on the stage-1 probe, 2026-07-25,
        # by differential rather than by guess: at 2:03 PM ET the S3 run.log carried every line printed with
        # `flush=True` (`[tfep] timestep=4.0 fs`, `[hmr-diag]`, `[spot-safe] commit store`) and NOT ONE line
        # from `rbfe_spot_driver`, which uses a bare `log=print` and contains zero `flush=True` (verified by
        # grep) — same process, same stdout, the only difference being the flush. Python block-buffers stdout
        # at ~8 KB when it is a pipe, and this pipeline pipes into `tee`.
        # Why it matters: `[timing] N iters in Ns = X s/iter` and `[barrier] committed checkpoint at
        # iteration N` are the driver's lines, i.e. exactly the progress signal an unproven pipeline is
        # monitored on. Buffered, they arrive in delayed bursts, so a monitor sees a frozen log during the
        # single riskiest window (warmup iteration 1, where every prior 4 fs attempt died) and cannot tell a
        # stall from a buffer. One env var fixes the whole class without touching a file the GCP lane runs.
        "PYTHONUNBUFFERED": "1",
        "TVAST_MODE": mode,
        "UNIT_ID": uid,
        "LEG_ID": leg_id,
        "SEED": str(seed),
        "DIRECTION": direction,
        "GIT_BRANCH": branch,
        "VAST_IMAGE_TAG": image or VAST_IMAGE,
        "RESULT_S3": result_prefix_for(b, uid, p),
        "COMMIT_S3": commit_prefix(b, uid, p),
        # Stage cache is seed-keyed: ternary_pdb_stage sets starting_model_index = seed % n_models, so two
        # seeds are genuinely different starting structures and sharing one cache would silently collapse
        # the replicate spread this program uses as its error bar.
        "STAGE_CACHE": f"s3://{b}/{p}/stagecache/{leg_id}__{tpl}__seed{seed}__v1.tar",
        # Pre-equil cache is keyed by seed AND charge AND length: all three change the relaxed coordinates.
        "PE_CACHE": f"s3://{b}/{p}/preequilcache/{leg_id}__seed{seed}__{charge}__ns{os.environ.get('TVAST_PREEQUIL_NS') or '0.5'}__v1.tar",
        "NEEDS_PREEQUIL": "0" if solvent else "1",
        "PREEQUIL_NS": os.environ.get("TVAST_PREEQUIL_NS") or "0.5",
        "TEMPLATE_PDB": tpl,
        "CHARGE_METHOD": charge,
        "N_WINDOWS": nwin,
        "RBFE_TIMESTEP_FS": dt,
        "RBFE_WARMUP_TIMESTEP_FS": wdt,
        # 5000, not the engine default 25000: the GCP lane measured 25000 steps spending ~20-60 min at ~0%
        # GPU across 12 replicas for NO NaN benefit (the NaN survives 25000 — see runbook 1b/1c).
        "RBFE_MIN_STEPS": os.environ.get("TVAST_MIN_STEPS") or "5000",
        # STRIDED HEAVY-ATOM TRAJECTORY — set explicitly here, not left to an engine default, because this is
        # the property that decides whether a leg can ever be re-analysed. The NR-V04 covalent panel's
        # read-only census found 72 objects across 19 units and ZERO trajectories, which made three known
        # analysis defects permanently uncorrectable and forced the panel to be re-run or abandoned. 50 ps is
        # a 20-iteration stride at the 2.5 ps time_per_iteration: ~50 MB over a full leg, against the ~112 MB
        # System XML this same driver already uploads. Velocities stay off — they double the size and no
        # geometric re-analysis needs them.
        "RBFE_POSITIONS_WRITE_PS": os.environ.get("TVAST_POSITIONS_WRITE_PS") or "50",
        "RBFE_VELOCITIES_WRITE_PS": os.environ.get("TVAST_VELOCITIES_WRITE_PS") or "",
        # S3 SETUP CACHE. Solvating + parameterising the ~146k-atom hybrid is ~6-15 min of GPU-idle time,
        # rebuilt on EVERY resume because it is the one expensive step that was not cached. Keyed by
        # (leg, direction, seed, charge, version); the built System is timestep-independent, so it is
        # deliberately NOT dt-keyed — but it IS pre-equilibration-dependent, hence the `pe` in the version.
        "RBFE_SETUP_CACHE_S3": f"s3://{b}/{p}/setupcache",
        "SETUP_CACHE_VERSION": os.environ.get("TVAST_SETUP_CACHE_VERSION") or "v1pe",
        # The engine FAILS FAST when a setup cache is configured but missing, to enforce the GCP lane's
        # CPU-prime-then-GPU process. This lane has no CPU prime for SETUP (only for stage), so the first
        # run of each leg must be allowed to build it — after which every resume restores it.
        "RBFE_REQUIRE_PRIMED_SETUP": "0",
        "RBFE_WARMUP_ITERS": sizing["warmup_iters"],
        "RBFE_PROD_ITERS": sizing["prod_iters"],
        # Checkpoint granularity == the maximum work a preemption can cost, traded against per-commit
        # overhead. Per-mode; see the note on MODES. The engine rounds each phase's target DOWN to a
        # multiple of its interval, so an interval larger than a short phase's target would silently
        # shorten the run — which is why probe and edge do not share one value.
        "WARMUP_CKPT_ITERS": os.environ.get("TVAST_WARMUP_CKPT_ITERS") or sizing["warmup_ckpt_iters"],
        "PROD_CKPT_ITERS": os.environ.get("TVAST_PROD_CKPT_ITERS") or sizing["prod_ckpt_iters"],
        # The MD's own cap, inside the instance runtime cap, so the deliverable upload still runs.
        "MD_TIMEOUT_S": str(int(sizing["max_runtime_s"] * 0.92)),
    }
    spec = JobSpec(
        name=unit_label(uid),
        command=["bash", "-lc", _render_pipeline(_PIPELINE.replace("{repo}", REPO))],
        image=image or VAST_IMAGE,
        checkpoint_uri=result_prefix_for(b, uid, p),
        resume=True,
        resources=resource_spec(),
        max_runtime_s=int(os.environ.get("TVAST_MAX_RUNTIME_S") or sizing["max_runtime_s"]),
        env=env,
    )
    # FAIL HERE, NOT AT THE RENTAL. Over the cap, Vast answers the create with a 400 and the launcher's
    # per-unit `except` turns it into a printed line inside a GREEN job — a launch that rents nothing and
    # reports success. Raising during construction makes it a build-time error a unit test can catch.
    try:
        n = onstart_length(spec)
    except Exception:  # noqa: BLE001 — no credentials in a pure/unit context; the length check is advisory
        n = None
    if n is not None and n > MAX_ONSTART_CHARS:
        raise ValueError(
            f"rendered onstart is {n} characters, over Vast's {MAX_ONSTART_CHARS} limit by "
            f"{n - MAX_ONSTART_CHARS}. Vast rejects the create with HTTP 400 'invalid_args', which the "
            f"launcher would otherwise report as a printed failure inside a green job. Shorten the "
            f"pipeline (comments are already stripped at render) or move a step into a repo script the "
            f"host runs after the clone.")
    return spec


# =============================================================================================================
# cost model — the arithmetic RUNG 2b is actually testing
# =============================================================================================================
def ternary_cost_model(s_per_iter_prod_2fs, warmup_iters=400, prod_iters=2000,
                       warmup_dt_fs=1.0, prod_dt_fs=2.0, time_per_iteration_ps=2.5):
    """Wall time for one ternary leg, and what changing the PRODUCTION timestep does to it. PURE.

    THE POINT, because the headline number in STRATEGY is optimistic. OpenFE derives an iteration count as
    `sim_length / timestep / n_steps_per_iteration`, and `n_steps_per_iteration = time_per_iteration / dt`.
    The two dt's cancel, so the ITERATION COUNT is timestep-independent — which is where "4 fs is exactly
    half the force evaluations" comes from. But that is only true of the phase whose dt actually changed.
    The warmup runs at 1 fs and its iteration count is derived from the WARMUP integrator, so a 1 ns
    equilibration costs 1e6 steps whether production is 2 fs or 4 fs. It does not shrink at all.

    So for the as-run protocol (1 ns warmup @1 fs + 5 ns production, 12 windows):
        2 fs: 1e6 + 2.5e6 = 3.5e6 steps/replica
        4 fs: 1e6 + 1.25e6 = 2.25e6 steps/replica     -> 1.56x, NOT 2x.
    Returns both so a caller reports the measured ratio rather than the assumed one.
    """
    steps_per_iter_prod = time_per_iteration_ps * 1000.0 / prod_dt_fs
    steps_per_iter_warm = time_per_iteration_ps * 1000.0 / warmup_dt_fs
    # wall time is proportional to force evaluations; calibrate the constant off the measured 2 fs rate
    s_per_step = s_per_iter_prod_2fs / (time_per_iteration_ps * 1000.0 / 2.0)
    warm_s = warmup_iters * steps_per_iter_warm * s_per_step
    prod_s = prod_iters * steps_per_iter_prod * s_per_step
    return {
        "warmup_h": warm_s / 3600.0, "production_h": prod_s / 3600.0,
        "leg_h": (warm_s + prod_s) / 3600.0,
        "steps_per_iter_production": steps_per_iter_prod,
        "steps_per_iter_warmup": steps_per_iter_warm,
    }


def speedup_2fs_to_4fs(warmup_iters=400, prod_iters=2000, warmup_dt_fs=1.0, time_per_iteration_ps=2.5):
    """Leg-level speedup of moving production 2 fs -> 4 fs, with the warmup held at its own dt. PURE."""
    a = ternary_cost_model(1.0, warmup_iters, prod_iters, warmup_dt_fs, 2.0, time_per_iteration_ps)
    b = ternary_cost_model(1.0, warmup_iters, prod_iters, warmup_dt_fs, 4.0, time_per_iteration_ps)
    return a["leg_h"] / b["leg_h"] if b["leg_h"] else None


# =============================================================================================================
# live operations (need credentials)
# =============================================================================================================
def _s3():
    import boto3
    return boto3.client("s3")


def _split_uri(uri):
    body = uri.split("://", 1)[1]
    bucket, _, key = body.partition("/")
    return bucket, key


def blocked_machine_ids(bucket=None, prefix=None):
    """Machines observed refusing starts with `resources_unavailable`. [] if unavailable.

    Recorded by collect() and consumed by submit() so a host that cannot schedule us stops winning
    selection. It is the availability term the $/ns ranking cannot express: a machine that never starts has
    infinite realised cost per ns yet reads as the cheapest offer on the board.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    try:
        st = json.loads(_s3().get_object(Bucket=b, Key=f"{p}/_lane_state.json")["Body"].read())
        return [str(m) for m in (st.get("_blocked_machines") or [])]
    except Exception:  # noqa: BLE001 — no state yet, or unreadable; exclude nothing
        return []


def committed_progress(uid, bucket=None, prefix=None):
    """(phase, iteration, monotonic_scalar) of the furthest COMMITTED iteration for this unit.

    This is the progress signal, and it is deliberately the commit store rather than "an instance exists".
    On Vast a rented box can sit up with a dead container or an idle GPU and look perfectly healthy; three
    separate silent stalls on the GCP ternary lane all presented as a live VM. The commit store is the only
    durable evidence that the SCIENCE advanced, and it survives the instance.

    The scalar orders production above warmup so a warmup->production transition can never read as a
    regression. Returns (None, 0, 0) when nothing is committed yet (setup / pre-equil / minimise).
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    base = f"{p}/commits/{uid}"
    best = {"warmup": 0, "production": 0}
    try:
        pag = _s3().get_paginator("list_objects_v2")
        for page in pag.paginate(Bucket=b, Prefix=f"{base}/"):
            for obj in page.get("Contents", []):
                m = re.search(r"/(warmup|production)/iter-(\d+)/", obj["Key"])
                if m:
                    best[m.group(1)] = max(best[m.group(1)], int(m.group(2)))
    except Exception as e:  # noqa: BLE001 — a listing failure must not be read as "no progress"
        print(f"[progress] could not list {base}: {type(e).__name__}: {e}")
        return (None, 0, -1)
    if best["production"]:
        return ("production", best["production"], 1_000_000 + best["production"])
    if best["warmup"]:
        return ("warmup", best["warmup"], best["warmup"])
    return (None, 0, 0)


def phase_and_log(uid, bucket=None, prefix=None, tail=8):
    """(phase_marker, age_minutes, log_tail_lines) for a unit, from S3. [] if not written yet.

    WHY THIS IS NOT OPTIONAL. The commit-store census (`committed_progress`) is the durable progress signal,
    but it reads ZERO for the whole cold start — stage, pre-equilibrate, solvate+parameterise, minimise —
    which is tens of minutes and is exactly where the GCP lane's three silent stalls lived (an am1bcc
    cold-cache wait at 0 % GPU, a 25000-step minimise, and a warmup NaN). Without the phase marker and the
    log tail, every one of those looks identical to a healthy leg that has simply not committed yet. The
    marker says WHICH phase; the age of the marker says whether that phase is moving.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    base = f"{p}/legs/{uid}"
    s3 = _s3()
    phase, age_min, lines, log_age = None, None, [], None
    try:
        o = s3.get_object(Bucket=b, Key=f"{base}/phase.txt")
        phase = o["Body"].read().decode(errors="replace").strip()
        age_min = (time.time() - o["LastModified"].timestamp()) / 60.0
    except Exception:  # noqa: BLE001 — not written yet (image still pulling)
        pass
    try:
        o = s3.get_object(Bucket=b, Key=f"{base}/run.log")
        log = o["Body"].read().decode(errors="replace")
        raw = [ln for ln in log.splitlines() if ln.strip()]
        # SURFACE THE DIAGNOSTIC LINES, not just the tail. The lines that answer "is this advancing and is it
        # healthy" — the per-chunk `[timing]`, the `[barrier] committed checkpoint at iteration N`, the
        # spot-driver's phase transitions and targets, and any NaN traceback — are emitted rarely and are
        # immediately buried by hundreds of openff/openmmtools INFO lines. A pure tail therefore shows the
        # noise and hides the signal, which is how a leg can look uninformative while its log says exactly
        # what is happening.
        keys = ("[timing]", "[barrier]", "[spot-driver]", "[tfep]", "NaN", "Traceback", "ERROR", "ABORT")
        hits = [ln for ln in raw if any(k in ln for k in keys)]
        lines = (hits[-tail:] + ["--- raw tail ---"] + raw[-4:]) if hits else raw[-tail:]
        # The openmmtools per-chunk progress line, which is the ONLY thing emitted between the driver's
        # (buffered) [timing] lines during a chunk. Pulled out separately so the compact summary can carry
        # it: "Iteration 3/8" is the difference between watching a live warmup and watching a frozen log.
        it_lines = [ln for ln in raw if "Iteration " in ln and "/" in ln]
        if it_lines:
            lines.append("LAST-ITER " + it_lines[-1].strip()[:80])
        # The log's OWN mtime, separately from the phase marker's. The marker is written only when the
        # phase CHANGES, so inside a long phase its age just grows and says nothing. The sync loop pushes
        # the log every 2 min, so a log older than ~4 min means the uploader stopped — which is a different
        # (and worse) fact than "this phase is taking a while", and the two are indistinguishable without it.
        log_age = (time.time() - o["LastModified"].timestamp()) / 60.0
    except Exception:  # noqa: BLE001
        pass
    return phase, age_min, lines, log_age


def leg_records(bucket=None, prefix=None):
    """{unit_id: leg.json} for every unit that has written one."""
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    out = {}
    try:
        s3 = _s3()
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=b, Prefix=f"{p}/legs/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith("/leg.json"):
                    continue
                try:
                    d = json.loads(s3.get_object(Bucket=b, Key=obj["Key"])["Body"].read().decode())
                except Exception as e:  # noqa: BLE001
                    print(f"[collect] unreadable {obj['Key']}: {e}")
                    continue
                d["_s3_last_modified"] = obj["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ")
                out[d.get("unit_id") or obj["Key"]] = d
    except Exception as e:  # noqa: BLE001
        print(f"[collect] could not list leg records: {type(e).__name__}: {e}")
    return out


def submit(mode="probe", dry_run=False, timestep_fs=None, warmup_timestep_fs=None, legs=None):
    """Rent one instance per unit for this mode, skipping units already done or already running.

    SKIPPING HAPPENS BEFORE THE RENTAL. The on-host pipeline has an idempotency check, but it only runs
    after the image pull and repo clone, so a re-dispatch was renting a GPU for ~25 minutes just to
    discover the work was finished. The launcher has S3 access; the cheap check belongs here.
    """
    specs = [(l, s, d) for (l, s, d) in (legs or units_for(mode))]
    jobs = [build_jobspec(l, s, d, mode=mode, timestep_fs=timestep_fs,
                          warmup_timestep_fs=warmup_timestep_fs) for (l, s, d) in specs]
    if dry_run:
        print(json.dumps([{"name": j.name, "image": j.image, "max_runtime_s": j.max_runtime_s,
                           "env": j.env} for j in jobs], indent=2))
        return []

    done = {u for u, d in leg_records().items() if d.get("status") == "done"}
    inflight = set()
    key = os.environ.get("VAST_API_KEY")
    if key:
        try:
            for i in _vast_request("GET", "/instances/", key).get("instances", []):
                lab = i.get("label") or ""
                if not lab.startswith(LABEL_PREFIX):
                    continue
                for j in jobs:
                    if label_matches_unit(lab, j.env["UNIT_ID"]):
                        inflight.add(j.env["UNIT_ID"])
        except Exception as e:  # noqa: BLE001 — never block a launch on a listing failure
            print(f"[launch] could not list live instances ({type(e).__name__}: {e}); "
                  "cannot skip in-flight units, duplicates are possible")
    busy = done | inflight
    keep = [j for j in jobs if j.env["UNIT_ID"] not in busy]
    for j in jobs:
        if j.env["UNIT_ID"] in done:
            print(f"[launch] skipping (already done, no rental): {j.env['UNIT_ID']}")
        elif j.env["UNIT_ID"] in inflight:
            print(f"[launch] skipping (already running, no rental): {j.env['UNIT_ID']}")
    if not keep:
        print("[launch] every unit for this mode is already done or running — nothing to rent")
        return []

    bad = set(blocked_machine_ids())
    if bad:
        print(f"[launch] excluding {len(bad)} machine(s) known to refuse starts: {sorted(bad)}")
    backend = get_backend("vast")
    handles = []
    # ONE UNIT PER MACHINE. Offers are per GPU slot, so selection happily picks the same cheapest-$/ns
    # machine for several units — but a host advertising slots it cannot actually schedule accepts every
    # rental and then refuses every start (observed 2026-07-25: machine 53989 took two legs and answered
    # resources_unavailable for both). Spreading costs ~nothing: the market shows ~23 hosts and the floor
    # is flat day-to-day.
    used = set(bad)
    for j in keep:
        try:
            j.resources.exclude_machine_ids = tuple(used)
            h = backend.submit(j)
            mid = h.extra.get("machine_id")
            if mid is not None:
                used.add(str(mid))
            print(f"[launch] {j.name}: instance={h.job_id} machine={mid} "
                  f"floor=${h.extra.get('min_bid')} bid=${h.extra.get('bid')} dph=${h.extra.get('dph')}")
            handles.append({"unit_id": j.env["UNIT_ID"], "instance": h.job_id,
                            "machine_id": mid, "bid": h.extra.get("bid"), "dph": h.extra.get("dph")})
        except Exception as e:  # noqa: BLE001 — one unrentable unit must not abort the rest
            print(f"[launch] {j.name}: SUBMIT FAILED {type(e).__name__}: {e}")
    if handles:
        json.dump(handles, open("ternary-vast-handles.json", "w"), indent=2)
    print(f"[launch] {len(handles)}/{len(keep)} unit(s) submitted -> "
          f"s3://{DEFAULT_BUCKET}/{RESULT_PREFIX}/legs/")
    return handles


def collect(bucket=None, prefix=None, autostop=True):
    """Status board + PROGRESS check + anti-idle reap. Returns (n_instances_up, n_done).

    "Progress", not "liveness": for every live instance this prints the furthest committed iteration and
    compares it against the previous poll's, because an instance being up says nothing about whether the
    MD is advancing.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    s3 = _s3()
    recs = leg_records(b, p)
    done = {u: d for u, d in recs.items() if d.get("status") == "done"}
    other = {u: d for u, d in recs.items() if d.get("status") != "done"}

    key = os.environ.get("VAST_API_KEY")
    mine = []
    if key:
        try:
            mine = [i for i in _vast_request("GET", "/instances/", key).get("instances", [])
                    if (i.get("label") or "").startswith(LABEL_PREFIX)]
        except Exception as e:  # noqa: BLE001
            print(f"[collect] could not list instances: {type(e).__name__}: {e}")

    print(f"[collect] {len(done)} finished unit(s), {len(other)} other record(s), {len(mine)} instance(s) up")
    for u, d in sorted(done.items()):
        t = (d.get("timing") or {}).get("production") or {}
        print(f"  DONE  {u}: dG_morph = {d.get('dg_morph_kcal')} +/- {d.get('mbar_se_kcal')} kcal/mol "
              f"| NaN={d.get('nan_seen')} | prod {t.get('median_s_per_iter')} s/iter (n={t.get('n')})")
    for u, d in sorted(other.items()):
        print(f"  ....  {u}: status={d.get('status')} rc={d.get('rc')} NaN={d.get('nan_seen')} "
              f"updated={d.get('updated_utc')} s3_mtime={d.get('_s3_last_modified')}")
        for ln in (d.get("log_tail") or [])[-15:]:
            print(f"      T| {ln[:200]}")

    # previous poll's per-instance clocks + blocked machines
    prev_state = {}
    try:
        prev_state = json.loads(s3.get_object(Bucket=b, Key=f"{p}/_lane_state.json")["Body"].read())
    except Exception:  # noqa: BLE001 — first run
        prev_state = {}
    new_state, blocked = {}, set()

    # DEDUPE before anything else: two instances on one unit write the same S3 keys, do the same work and
    # bill twice. Keep the oldest (most progress, checkpoints already committed).
    if key and mine:
        by_label = {}
        for i in mine:
            by_label.setdefault(i.get("label") or "", []).append(i)
        for lab, group in by_label.items():
            if len(group) < 2:
                continue
            group.sort(key=lambda x: float(x.get("start_date") or 0))
            print(f"  DUPLICATE {lab}: {len(group)} instances; keeping {group[0].get('id')}, "
                  f"destroying {[g.get('id') for g in group[1:]]}")
            for d_ in group[1:]:
                try:
                    _vast_request("DELETE", f"/instances/{d_.get('id')}/", key)
                except Exception as e:  # noqa: BLE001
                    print(f"    destroy {d_.get('id')} failed: {e}")
            mine = [x for x in mine if x not in group[1:]]

    for i in mine:
        iid, lab = i.get("id"), i.get("label")
        uid = next((u for u in list(recs) + [j for j in _known_unit_ids()] if label_matches_unit(lab, u)), None)
        up_h = 0.0
        try:
            up_h = (time.time() - float(i.get("start_date") or time.time())) / 3600.0
        except (TypeError, ValueError):
            pass
        cost = up_h * float(i.get("dph_total") or 0)
        print(f"  vast {iid} ({lab}) {i.get('actual_status')} up={up_h:.2f}h "
              f"dph=${i.get('dph_total')} spent~${cost:.2f} gpu={i.get('gpu_name')}")

        # PROGRESS, not liveness.
        if uid:
            phase, it, scalar = committed_progress(uid, b, p)
            prev = (prev_state.get(f"prog:{uid}") or [0, 0])
            pprog = prev[0] if isinstance(prev, (list, tuple)) else 0
            pstall = prev[1] if isinstance(prev, (list, tuple)) and len(prev) > 1 else 0
            stall = 0 if scalar > pprog else int(pstall) + 1
            new_state[f"prog:{uid}"] = [scalar, stall]
            print(f"      committed: {phase or 'none yet'}"
                  f"{('/' + str(it)) if phase else ''}  scalar={scalar} prev={pprog} "
                  f"no-advance-polls={stall}")
            # The commit census is blind for the whole cold start, so pair it with the on-host phase
            # marker and log tail — that is what turns a liveness ping into a progress check.
            mark, mark_age, tail, log_age = phase_and_log(uid, b, p)
            print(f"      phase: {mark or '(no marker yet — image pull / container start)'}"
                  + (f"  (marker {mark_age:.0f} min old" if mark_age is not None else "  (")
                  + (f", log {log_age:.1f} min old" if log_age is not None else ", no log yet") + ")")
            for ln in tail:
                print(f"      | {ln[:170]}")

        msg = str(i.get("status_msg") or "").strip()
        frozen_min, new_state[str(iid)] = stall_minutes(prev_state, iid, msg, time.time())
        if i.get("actual_status") != "running":
            print(f"      why: cur_state={i.get('cur_state')} intended={i.get('intended_status')} "
                  f"msg={msg[:180]!r} unchanged_for={frozen_min:.0f}min")

        finished = uid in done
        crashed = bool(uid and uid in other and other[uid].get("status") == "failed"
                       and _record_is_newer_than_instance(other[uid], i))
        if autostop and (finished or crashed or up_h > MAX_INSTANCE_HOURS):
            why = ("unit done" if finished else
                   "unit FAILED — nothing left to produce" if crashed else "runtime backstop")
            print(f"    -> destroying {iid} ({why})")
            try:
                _vast_request("DELETE", f"/instances/{iid}/", key)
            except Exception as e:  # noqa: BLE001
                print(f"    destroy failed: {e}")
        elif (i.get("actual_status") != "running" and i.get("cur_state") == "running"
              and frozen_min > MAX_FROZEN_MIN):
            print(f"    -> destroying {iid} (status frozen {frozen_min:.0f} min at {msg[:60]!r}; "
                  f"the image pull is dead, not queued)")
            try:
                _vast_request("DELETE", f"/instances/{iid}/", key)
            except Exception as e:  # noqa: BLE001
                print(f"    destroy failed: {e}")
        elif i.get("cur_state") == "stopped":
            # A stopped box has two causes that demand OPPOSITE actions, and only the start response
            # separates them. Re-issue the start (idempotent) and read the reply.
            err = None
            try:
                resp = _vast_request("PUT", f"/instances/{iid}/", key, body={"state": "running"})
                err = (resp or {}).get("error")
                print(f"    -> NUDGED {iid}: cur_state=stopped; vast replied {str(resp)[:240]}")
            except Exception as e:  # noqa: BLE001
                print(f"    nudge failed: {e}")
            if err == "resources_unavailable":
                # NOT something to wait out. Vast is a market of ~23 independently priced hosts, not a
                # pool; the floor is flat day-to-day, so a different host today costs what this one will
                # cost tomorrow. Raising the bid was tested on 2026-07-25 (+26% to the value ceiling) and
                # changed nothing. Record the machine, destroy, pick another.
                blocked.add(str(i.get("machine_id")))
                print(f"    (machine {i.get('machine_id')} has no free GPU and no bid fixes it — blocked)")
                print(f"    -> destroying {iid}: picking another host beats queueing on this one")
                try:
                    _vast_request("DELETE", f"/instances/{iid}/", key)
                except Exception as e:  # noqa: BLE001
                    print(f"    destroy failed: {e}")
            elif up_h * 60 > MAX_STOPPED_MIN:
                print(f"    -> destroying {iid} (stopped {up_h * 60:.0f} min, not a capacity wait)")
                try:
                    _vast_request("DELETE", f"/instances/{iid}/", key)
                except Exception as e:  # noqa: BLE001
                    print(f"    destroy failed: {e}")

    # ONE COMPACT LINE PER UNIT, LAST. GitHub truncates a job log from the tail, and this board's per-instance
    # detail is long enough that on a busy poll the verdict scrolls out of a 25-line fetch — which is exactly
    # when a monitor most needs it. So repeat the decision-relevant facts in one grep-able line each.
    print("---- TVAST-SUMMARY ----")
    for u, d in sorted(recs.items()):
        t = (d.get("timing") or {}).get("production") or {}
        print(f"TVAST {u} status={d.get('status')} dG={d.get('dg_morph_kcal')} se={d.get('mbar_se_kcal')} "
              f"NaN={d.get('nan_seen')} prod_s_per_iter={t.get('median_s_per_iter')}")
    for i in mine:
        uid = next((u for u in list(recs) + _known_unit_ids() if label_matches_unit(i.get("label"), u)), None)
        ph, it, sc = committed_progress(uid, b, p) if uid else (None, 0, 0)
        # INSTANCE ID ON EVERY PROGRESS LINE. A progress reading is only worth anything if it is
        # attributable to the box you actually rented: a monitor that reports "advancing" from the wrong
        # job is the same silent-success class this lane's watchdog exists to prevent, and it is more
        # expensive here than elsewhere because the wrong reading leaves a billed GPU unwatched.
        print(f"TVAST {uid or i.get('label')} instance={i.get('id')} machine={i.get('machine_id')} "
              f"up={i.get('actual_status')} committed={ph or 'none'}/{it} "
              f"gpu={i.get('gpu_name')} dph=${i.get('dph_total')}")
    print("---- END TVAST-SUMMARY ----")

    try:
        prior = set(prev_state.get("_blocked_machines") or [])
        new_state["_blocked_machines"] = sorted(prior | blocked)
        # carry forward progress entries for units with no live instance, so the stall clock is not reset
        # by a preemption (which is exactly when you want to know how far it had got).
        for k, v in prev_state.items():
            new_state.setdefault(k, v)
        s3.put_object(Bucket=b, Key=f"{p}/_lane_state.json",
                      Body=json.dumps(new_state, indent=2).encode())
    except Exception as e:  # noqa: BLE001 — a monitoring aid must never fail a collect
        print(f"[collect] could not persist lane state: {e}")
    return len(mine), len(done)


def fetch_legs(dest, mode="edge", bucket=None, prefix=None, timestep_fs=None, warmup_timestep_fs=None):
    """Download this mode's engine leg JSONs into `dest` under the filenames the reducer expects.

    `ternary_fep_reduce._find_leg_files` globs `leg_<leg_id>_<direction>_r<seed>.json` under CKPT_DIR/INPUT_DIR,
    so the S3 objects (which live at `legs/<unit_id>/engine_leg.json`) have to be renamed back. Reconstructing
    the name from the unit's own parameters — rather than trusting whatever the object happened to be called —
    is what keeps a 4 fs leg from ever being reduced as if it were a 2 fs one.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    dt = str(timestep_fs or os.environ.get("TVAST_TIMESTEP_FS") or DEFAULT_TIMESTEP_FS)
    wdt = str(warmup_timestep_fs or os.environ.get("TVAST_WARMUP_TIMESTEP_FS") or DEFAULT_WARMUP_TIMESTEP_FS)
    os.makedirs(dest, exist_ok=True)
    s3 = _s3()
    got = {}
    for (leg, seed, direction) in units_for(mode):
        uid = unit_id(leg, seed, direction, dt, wdt, mode)
        name = f"leg_{leg}_{direction}_r{seed}.json"
        try:
            body = s3.get_object(Bucket=b, Key=f"{p}/legs/{uid}/engine_leg.json")["Body"].read()
        except Exception as e:  # noqa: BLE001
            print(f"[fetch-legs] MISSING {uid}: {type(e).__name__}")
            continue
        with open(os.path.join(dest, name), "wb") as fh:
            fh.write(body)
        d = json.loads(body.decode())
        got[leg] = d
        print(f"[fetch-legs] {name}: dG_morph={d.get('dg_morph_kcal')} +/- {d.get('mbar_se_kcal')} "
              f"(MBAR SE) protocol_hash={str(d.get('protocol_hash'))[:12]}")
    return got


def ddg_coop_identity(legs):
    """ΔΔG_coop from the legs in hand, by the identity the engine defines. PURE.

    `nr4a3_ternary_fep`'s own docstring: ΔΔG_coop = ΔΔG_alch,ternary − ΔΔG_alch,binary
    = (ternary − solvent) − (binary − solvent) = **ternary − binary**. The solvent leg cancels EXACTLY, so it
    is not needed for this number and its absence is not a gap. It is still run and reported, because each
    environment's ΔΔG is only a relative *binding* free energy with it.

    Computed here as well as by `ternary_fep_reduce` deliberately. The reducer's gating machinery had seven
    defects found in one day, every one of them reporting success while measuring nothing; a two-term
    subtraction that can be checked by eye is the right cross-check for a number this load-bearing.
    """
    tern = next((v for k, v in legs.items() if "__ternary" in k), None)
    bina = next((v for k, v in legs.items() if "__binary" in k), None)
    solv = next((v for k, v in legs.items() if k.endswith("__solvent")), None)
    if not tern or not bina:
        return {"ddg_coop_kcal": None,
                "reason": "need both a ternary and a binary leg; solvent cancels and is optional"}
    t, bn = tern.get("dg_morph_kcal"), bina.get("dg_morph_kcal")
    if t is None or bn is None:
        return {"ddg_coop_kcal": None, "reason": "a leg has no dg_morph_kcal"}
    ddg = float(t) - float(bn)
    big = max(abs(float(t)), abs(float(bn)))
    hashes = {k: v.get("protocol_hash") for k, v in legs.items()}
    return {
        "ddg_coop_kcal": ddg,
        "dg_ternary_kcal": float(t), "dg_binary_kcal": float(bn),
        "dg_solvent_kcal": (float(solv["dg_morph_kcal"]) if solv and solv.get("dg_morph_kcal") is not None
                            else None),
        # How much of each leg survives the subtraction. r0's was 0.0111 — the answer was 1.1 % of the
        # numbers being subtracted, which is why its systematic miss was ~33x its statistical error.
        "cancellation_ratio": (abs(ddg) / big) if big else None,
        "protocol_hashes": hashes,
        "protocol_hashes_consistent": len(set(v for v in hashes.values() if v)) <= 1,
    }


def _known_unit_ids():
    """Every unit id this module can currently launch — used to pair a live label with a unit before that
    unit has written any record. Without it a freshly launched host has no progress line at all, which is
    the exact window (setup / pre-equil) where a stall is most likely and least visible."""
    out = []
    for mode in MODES:
        for (l, s, d) in units_for(mode):
            for dt in (DEFAULT_TIMESTEP_FS, "2.0", "3.0"):
                out.append(unit_id(l, s, d, dt, DEFAULT_WARMUP_TIMESTEP_FS, mode))
    return out


def stop_all():
    """Destroy every instance of this lane (anti-idle backstop)."""
    key = os.environ["VAST_API_KEY"]
    n = 0
    for i in _vast_request("GET", "/instances/", key).get("instances", []):
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
    ap = argparse.ArgumentParser(description="Ternary cooperativity FEP on Vast.ai (RUNG 2b lane)")
    ap.add_argument("--mode", choices=sorted(MODES), default=os.environ.get("TVAST_MODE") or "probe")
    ap.add_argument("--timestep-fs", default=None)
    ap.add_argument("--warmup-timestep-fs", default=None)
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--stop", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fetch-legs", metavar="DIR",
                    help="download this mode's engine leg JSONs into DIR under the reducer's filenames, "
                         "then print the ΔΔG_coop identity as a cross-check")
    a = ap.parse_args(argv)
    if a.fetch_legs:
        legs = fetch_legs(a.fetch_legs, mode=a.mode, timestep_fs=a.timestep_fs,
                          warmup_timestep_fs=a.warmup_timestep_fs)
        print(json.dumps(ddg_coop_identity(legs), indent=2))
    elif a.stop:
        stop_all()
    elif a.collect:
        collect()
    else:
        submit(mode=a.mode, dry_run=a.dry_run, timestep_fs=a.timestep_fs,
               warmup_timestep_fs=a.warmup_timestep_fs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
