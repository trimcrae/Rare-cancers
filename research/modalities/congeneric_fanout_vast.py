#!/usr/bin/env python3
"""
STEP 1 FAN-OUT (RUNG 4) — Vast.ai launcher for the cmpd19 congeneric RBFE map, N-wide.

One Vast instance per UNIT (= one map edge at its charge-conserving microstate leg, on the primary NR4A3
frame). Each instance clones the repo, pulls the pre-staged common-mode poses from S3, runs BOTH alchemical
legs of its edge through the unchanged OpenFE engine (`nr4a3_rbfe.py`, MODE=splittest, spot-safe S3
checkpoint/resume), reduces them to ddG_bind, uploads `ddg.json`, and self-stops.

Vast rents INDEPENDENT hosts, so N units are genuinely N-wide with no shared-quota wall. `FANOUT_WIDTH` is
therefore a self-imposed cap on concurrent spend/blast-radius, not a provider quota — `launch` tops the fleet
UP to that width and is safe to re-run. The CI workflow sets it to the whole 19-unit tranche, because
parallel costs the same GPU-dollars as serial and a congeneric map has no result that would cancel the rest.

Modes (env flags, set by the CI workflow):
  PLAN=1      dry plan: which units, cost band, wave shape, what is deliberately excluded. No API calls.
  STAGE=1     run the RDKit pose staging (free CPU on the runner) + upload the staged tree to S3.
  PRECHECK=1  verify the staged tree is in S3 and every unit's two endpoints are present in it. No spend.
  LAUNCH=1    top the fleet up to FANOUT_WIDTH with the next not-yet-finished units.
  COLLECT=1   pull finished ddg.json's -> map result + cycle closure + ranking + REALISED SPEND; reap hosts.
  MONITOR=1   PROGRESS check: committed-iteration census per unit, GPU utilisation, the starved-host guard.
  DIAG=1      root-cause a failed unit: its S3 leg log + the container stdout pulled off the Vast instance.
  STOP=1      destroy every s1f-* instance (explicit cleanup; never touches other labels).

REPLICATES — `FANOUT_REPLICATE_EDGES` (comma-separated edge ids, or a CYCLE id such as `cycle_3carbonyl`) +
`FANOUT_REPLICATES=N` add N further INDEPENDENT draws of those edges to the lane's unit list. Each replicate
is a distinct unit (`<unit_id>__r<n>`) with its own result key, its own checkpoint prefix and `SEED=<n>` —
which `rbfe_spot_checkpoint` hashes into the resume fingerprint, so a replicate can never restore another
replicate's trajectory. Unset (the default) means the lane is exactly the 19-unit map, byte-for-byte. Preview
with `PLAN=1`; the arithmetic and the honesty caveats live in `congeneric_fanout.replicate_units`.

SELECTIVE LAUNCH — `FANOUT_ONLY` (comma-separated unit_id / ligand substrings) launches a NAMED subset. This
is the shakeout lever, and it exists because of an asymmetry: wave 1 proved this lane SAMPLES (three hosts at
95-99 % GPU on the real cmpd19/NR4A3 system), but 0 of 19 units has ever produced a ddG, so the TERMINUS —
reduce both legs, write ddg.json, upload — is unproven. Fanning 19 wide into an unproven terminus risks
paying 19x for zero results. One deliberately-chosen unit (the most-advanced checkpoint, i.e. the one closest
to the terminus) runs first; the rest go out together the moment it lands a ddG.

WHAT THE DRIVER NOW KEEPS IN S3, so that a CI run inherits what a previous CI run learned with no agent awake:
  <results>/_rentals.json            the rental ledger — bid x billed hours = REALISED spend
  <results>/_excluded_machines.json  machines this lane refuses to re-rent (capacity refusal / starvation)
  <results>/_progress_prev.json      last check's committed-iteration census, so "did it ADVANCE" is answerable
  <results>/_util_state.json         consecutive low-utilisation strikes per instance

COST DISCIPLINE. `LAUNCH` refuses to submit unless FANOUT_CONFIRM=1 is set, prints the DERIVED cost of exactly
what it is about to submit (never a hand-typed constant — see congeneric_fanout's cost block), and skips any
unit whose ddg.json is already in S3, so a re-dispatch after a preemption resumes rather than paying twice.
"""
from __future__ import annotations

import calendar
import contextlib
import dataclasses
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from congeneric_fanout import (  # noqa: E402
    PRIMARY_FRAME, PRIMARY_RECEPTOR, checkpoint_prefix, cost_estimate, cost_plan, cycle_closure,
    default_units, fanout_width, lane_units, plan, rank_by_ddg, replicate_units, requested_replicates,
    result_key, unit_env, wave_plan,
)
# The market guard's arithmetic is PURE and lives in the core module with the rest of the cost block, so it
# is unit-tested without a Vast key and cannot drift from the ladder figures it is derived from.
from congeneric_fanout import (  # noqa: E402
    basis_usd_per_ns as market_basis, market_verdict as cost_verdict)
import congeneric_fanout as _cf  # noqa: E402  place_units / unit_usd_per_ns_ceiling / the cost block
# The anti-idle POLICY is shared with the ternary lane and is not re-implemented here — this lane supplies
# only the evidence its own artifacts carry (`_idle_evidence`). One policy, two lanes; that is the whole
# reason the step 1 pipeline now emits the ternary lane's signal SHAPES rather than inventing its own.
import vast_idle_guard as _vig  # noqa: E402
# The IN-FLIGHT BOARD. This lane does not render a table of its own: it hands the facts its progress check
# ALREADY reads to the one renderer every lane shares, which is what stopped the board drifting in shape and
# losing columns. See `inflight_board.__doc__` for why the merged board is a separate file from the ternary
# lane's, and why a lane may never write another lane's rows.
import inflight_board as _ifb  # noqa: E402
from gpu_backend import (  # noqa: E402
    JobSpec, ResourceSpec, _vast_request, board_read_cache, get_backend, measured_min_cuda)

REPO = "https://github.com/trimcrae/Rare-cancers"
BUCKET = os.environ.get("VAST_CKPT_BUCKET", "")
STAGE_PREFIX = os.environ.get("STAGE_PREFIX", "nr4a3-step1-fanout/stage")
RESULT_PREFIX = os.environ.get("RESULT_PREFIX", "nr4a3-step1-fanout/results")
LABEL_PREFIX = "s1f-"
# Set True by `market_gate()` once it has actually taken a snapshot and decided. The interim belt in
# `mode_launch` refuses any multi-unit launch that reaches it with this still False.
_MARKET_GUARD_RAN = False
_MARKET_HOLD_ESCALATED = False
# Set True by `_write_map_guarded` when a tick's freshly-read `n_complete` is LOWER than the count already
# committed on disk. Measured 2026-08-27: a tick read the results prefix as holding zero ddg.json objects
# (10 other objects present, so the S3 call itself succeeded — this was not a masked credential exception)
# against a committed map that had stood at 18/19 complete, unchanged, for 4h41m. That reading silently
# overwrote $73.79 of already-realised, already-banked GPU results with an empty map — the exact
# single-slot-artifact hazard AUT-PROP-009 names for a sibling file. The guard below refuses that overwrite
# and escalates loudly instead, the same way `_MARKET_HOLD_ESCALATED` already does for a held-too-long market.
_ARTIFACT_REGRESSION_DETECTED = False
N_WINDOWS = int(os.environ.get("N_WINDOWS", "12"))

# The OpenFE image (openfe>=1.12 + ambertools/am1bcc + lomap/kartograf + OpenMM CUDA + awscli), built by the
# fusion-cpu-extras `fep_bake` task. Same image the firm RBFE probe measured ~3.6 GPU-h/complex-leg on.
FEP_IMAGE = os.environ.get("FEP_IMAGE") or "docker.io/triskit23/nr4a3fep:latest"

# 4090 is the $/ns winner at every system size we've benched (pricing.md section A). The RBFE hybrid box is
# ~35k atoms, so 24 GB VRAM is ample; host RAM matters for the CPU-bound setup unit.
# ⚠ `min_cuda` IS THIS IMAGE'S OWN MEASUREMENT, not the shared default. `FANOUT_RES` used to inherit
# `ResourceSpec`'s constant, so a floor probed on one stack would have silently become this lane's — the same
# error as trusting a Dockerfile line. `measured_min_cuda` returns the conservative fallback until
# `probe_image_cuda.py` has actually run inside `nr4a3fep`, so this can only ever narrow on evidence.
FANOUT_RES = ResourceSpec(gpu=os.environ.get("VAST_GPU_MODEL") or "rtx4090",
                          min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=80, interruptible=True,
                          min_cuda=measured_min_cuda(FEP_IMAGE))

# A unit is two legs (~5-6 GPU-h) plus boot/setup; the ceiling must clear a full unit plus a resume, and must
# NOT reap mid-leg (a real HREX complex leg runs ~3 h).
MAX_RUNTIME_S = int(os.environ.get("FANOUT_MAX_RUNTIME_S", str(14 * 3600)))
REAP_AGE_MIN = int(os.environ.get("FANOUT_REAP_AGE_MIN", str(15 * 60)))


# ---- the per-instance pipeline ----------------------------------------------------------------------------

_PREAMBLE = r"""
set -eo pipefail
# ★★ LIVENESS SIGNALS — THE TWO THINGS `vast_idle_guard` CONSUMES, IN ITS SHAPES (2026-07-27).
#
# WHY. `vast_idle_guard` is the ONLY thing that can stop a wedged rental's meter, because the host provably
# cannot stop its own (`kill -9 1` returns 0 and does nothing; see gpu_backend._VAST_SELFSTOP). It could not
# be wired to step 1 because step 1 emitted NEITHER signal it keys on: `phase.txt` moves only at phase
# BOUNDARIES, and the leg log was uploaded once, at leg END. Between those, a wedged box was
# indistinguishable from a healthy one — which is how 45996071 crash-looped on a dead credential for over an
# hour at $0.2497/hr with 0 % GPU while every existing guard passed it.
#
# The shapes below are LIFTED FROM `ternary_vast_launch._PIPELINE`, deliberately unchanged, so one guard
# reads one convention on both lanes rather than each lane inventing its own.
#
#   1. `$RESULT_S3/run.log`, re-PUT every S1F_SYNC_S seconds by the heartbeat below — DURING EVERY PHASE,
#      including the long CPU-only ones. That is the whole point: a step 1 complex leg is legitimately
#      GPU-idle for stage + openff parameterisation of a large hybrid + minimise, and the guard's WEDGED
#      clause fires on the absence of WRITES, never on an idle GPU. If the heartbeat stopped during a healthy
#      phase the guard would destroy a healthy leg — a self-inflicted copy of the incident it exists to
#      prevent — so the loop is written to be unkillable-by-accident: no `set -e` exposure, every command
#      `|| true`, and the S3 PUT refreshes the object's LastModified even when the phase writes NO new text
#      (the engine's stdout goes to /tmp/$L.log, so run.log is legitimately silent for hours; the guard reads
#      the object's mtime, not its content).
#   2. `$RESULT_S3/attempts/run-<UTC>.log`, archived at container start. The timestamp is IN THE KEY, so a
#      count of those keys is a durable count of container starts and needs no S3 metadata — that is the
#      channel that catches a crash-loop whose S3 still works.
#
# ⚠ ORDER, AND IT IS THE ONE THE TERNARY LANE PAID FOR: the archive must run BEFORE the first `mark`.
# `exec > >(tee /tmp/run.log)` TRUNCATES the local log, and `mark` uploads it — so marking first overwrites
# the previous attempt's S3 copy with a fresh stub, and the archive then dutifully copies the stub. That is
# how seventeen 168-byte attempts were archived on 2026-07-26 with the failing attempt's log lost.
exec > >(tee /tmp/run.log) 2>&1
export DEBIAN_FRONTEND=noninteractive
command -v curl >/dev/null 2>&1 || { apt-get update -q||true; apt-get install -y -q --no-install-recommends curl ca-certificates||true; }
export PATH=/opt/mamba/envs/rbfe/bin:$PATH
# conda-pack relocation breaks OpenMM's compiled-in plugin dir, so OpenFE's internal getPlatformByName("CUDA")
# fails with "no registered Platform called CUDA" (root-caused on the first firm run, 2026-07-23).
export OPENMM_PLUGIN_DIR=/opt/mamba/envs/rbfe/lib/plugins
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
PY=/opt/mamba/envs/rbfe/bin/python
AWS=/opt/mamba/envs/rbfe/bin/aws
command -v "$AWS" >/dev/null 2>&1 || AWS="$PY -m awscli"
mark() { echo "$1 $(date -u +%FT%TZ)" | $AWS s3 cp - "$RESULT_S3/phase.txt" 2>/dev/null || true
         $AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true; }

# --- container-start archive. Before the first `mark`, for the reason above. ---
if $AWS s3 ls "$RESULT_S3/run.log" >/dev/null 2>&1; then
  $AWS s3 cp "$RESULT_S3/run.log" "$RESULT_S3/attempts/run-$(date -u +%Y%m%dT%H%M%SZ).log" \
    --only-show-errors >/dev/null 2>&1 \
    && echo "[s1f] archived the previous attempt's run.log under attempts/" || true
fi

# --- THE HEARTBEAT, and the three independent ways it is guaranteed to die. ---
#
# ⚠⚠ A HEARTBEAT THAT OUTLIVES ITS JOB DOES NOT JUST LEAK A PROCESS — IT DEFEATS THE GUARD IT FEEDS. A loop
# still PUTting run.log after the job is gone keeps the object fresh forever, so the WEDGED clause never
# fires and the box bills until the 15 h age backstop. That is strictly WORSE than having no heartbeat, and
# with 18 units live it is the failure mode worth engineering against, so there are three nets and they fail
# in different ways:
#
#   (1) the pipeline's EXIT trap kills it. Covers a clean exit, a `set -e` abort, and a trapped signal.
#   (2) THE PARENT-DEATH POLL, which is the one that matters: a SIGKILL of the pipeline shell runs NO trap
#       (SIGKILL cannot be caught), and `Killed` is exactly what the 2026-07-27 crash-loop logged. The loop
#       therefore re-checks `kill -0 $parent` every tick and exits the moment the shell it belongs to is
#       gone — reparenting to init does not fool it, because it is polling the PID it was handed, not its
#       own parentage.
#   (3) a hard TTL slightly past the job's own `max_runtime_s`, so even a PID reused by an unrelated process
#       cannot keep it alive indefinitely.
#
# It also must NOT stop the onstart shell reaching its own EXIT trap. It cannot: bash does not wait on
# background jobs at exit, and `ct_selfstop`'s `kill -9 -1` reaps whatever is left. Both directions are
# tested by EXECUTION under `unshare -fp --mount-proc` (tests/test_step1_liveness.py), not by argument —
# reasoning about traps is what this repo has already been wrong about once.
s1f_heartbeat() {
  _p="$1"; _end=$(( $(date +%s) + ${S1F_SYNC_TTL_S:-54000} ))
  while kill -0 "$_p" 2>/dev/null && [ "$(date +%s)" -lt "$_end" ]; do
    sleep "${S1F_SYNC_S:-120}"
    $AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true
  done
}
s1f_heartbeat "$$" &
S1F_SYNC_PID=$!
# The trap does NOT `exit`, so the pipeline's real exit status is preserved. The final PUT is deliberate:
# it costs at most one LOG_SILENCE_MIN window of delayed condemnation, and ONLY in the case where the job
# actually returned — which the `result in S3` and terminal-state reap clauses already handle. In the case
# this guard exists for (a wedge or a crash-loop, where the job never returns) the trap never runs at all,
# the log goes silent on schedule, and the diagnostic is what the archive preserved.
s1f_stop_heartbeat() { _rc=$?
  kill "$S1F_SYNC_PID" 2>/dev/null || true
  $AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true
  return $_rc; }
trap s1f_stop_heartbeat EXIT
mark boot
$PY -c "import openfe,openmm;print('[s1f] openfe',openfe.__version__,'plats',[openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())])"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
export IN=/tmp/s1f_in OUT=/tmp/s1f_out
mkdir -p "$IN" "$OUT"
# Common-mode poses + receptor, staged once on CI (congeneric_pose_stage.py) — every unit reads the SAME tree,
# which is what makes the 19 ddG values mutually comparable.
$AWS s3 cp "s3://$BUCKET/$STAGE_PREFIX/" "$IN/" --recursive --only-show-errors
test -s "$IN/ligand/docked_$RECEPTOR.sdf" || { echo "[s1f] FATAL: staged ligand SDF missing"; exit 3; }
test -s "$IN/receptor/$RECEPTOR-opened.pdb" || { echo "[s1f] FATAL: staged receptor PDB missing"; exit 3; }
mark staged
"""

# One alchemical leg. Idempotent across dispatches: a leg whose JSON is already in S3 is downloaded, not rerun
# (so a preempted unit resumes at leg granularity), and the sampler itself resumes from its S3 commit store.
_LEG = r"""
run_leg() {
  L="$1"
  if $AWS s3 cp "$RESULT_S3/leg_${RECEPTOR}_${L}.json" "$OUT/leg_${RECEPTOR}_${L}.json" --only-show-errors 2>/dev/null; then
    echo "[s1f] leg $L already in S3 — idempotent skip"; return 0
  fi
  mark "leg-$L-running"
  # `set -e` + `pipefail` is DISARMED around the engine on purpose. Previously the leg ran as
  # `... | tee log`, so a non-zero exit aborted the function immediately and the `s3 cp` of the log never
  # ran — the diagnostic was discarded in exactly the case it was needed (observed on s1f-04, which exited
  # 10 min into its complex leg leaving nothing behind). Capture the rc, ALWAYS ship the log, then fail.
  set +e
  env MODE=splittest RBFE_TINY=0 OPENMM_REQUIRE_CUDA=1 \
      RBFE_SPOT_SAFE=1 RBFE_SPOT_COMMIT_S3="s3://$BUCKET/$CKPT_PREFIX/$L" \
      RBFE_WARMUP_CKPT_ITERS=20 RBFE_PROD_CKPT_ITERS=40 \
      RECEPTOR="$RECEPTOR" LEG="$L" LIGAND_A="$LIGAND_A" LIGAND_B="$LIGAND_B" N_WINDOWS="$N_WINDOWS" \
      INPUT_DIR="$IN" OUTPUT_DIR="$OUT" CKPT_DIR="$OUT" \
      $PY nr4a3_rbfe.py > "/tmp/$L.log" 2>&1
  rc=$?
  set -e
  tail -60 "/tmp/$L.log" || true
  $AWS s3 cp "/tmp/$L.log" "$RESULT_S3/$L.log" --only-show-errors || true
  if [ "$rc" -ne 0 ]; then
    echo "[s1f] leg $L FAILED rc=$rc (full log at $RESULT_S3/$L.log)"
    mark "leg-$L-FAILED-rc$rc"
    return 1
  fi
  test -s "$OUT/leg_${RECEPTOR}_${L}.json" || {
    echo "[s1f] leg $L exited 0 but produced no result JSON"; mark "leg-$L-NORESULT"; return 1; }
  $AWS s3 cp "$OUT/leg_${RECEPTOR}_${L}.json" "$RESULT_S3/leg_${RECEPTOR}_${L}.json" --only-show-errors
  mark "leg-$L-done"
}
run_leg complex
run_leg solvent
"""

# The reduce is done HERE, not via nr4a3_rbfe.py's MODE=reduce: that path annotates its output with the
# denovo_401 ABFE anchor (rbfe_edges.ANCHOR_401_ABFE), which is a DIFFERENT scaffold and meaningless for a
# cmpd19 congeneric edge. Writing ddG_bind ourselves keeps the provenance honest — the thermodynamic cycle is
# still rbfe_edges.ddg_bind (dG_complex - dG_solvent), just without a borrowed absolute anchor.
_REDUCE = r"""
mark reduce
$PY - <<'PYEOF'
import json, os
import rbfe_edges as rb
out, rec = os.environ["OUT"], os.environ["RECEPTOR"]
cx = json.load(open(f"{out}/leg_{rec}_complex.json"))
sol = json.load(open(f"{out}/leg_{rec}_solvent.json"))
ddg = rb.ddg_bind(cx["dg_morph_kcal"], sol["dg_morph_kcal"])
unc = (cx.get("unc_kcal", 0.0) ** 2 + sol.get("unc_kcal", 0.0) ** 2) ** 0.5
r = {
    "unit_id": os.environ["UNIT_ID"], "edge_id": os.environ["EDGE_ID"], "leg_id": os.environ["LEG_ID"],
    "receptor": rec, "frame": os.environ["FRAME"],
    # WHICH INDEPENDENT DRAW THIS IS. `collect` groups replicates by edge_id and the SD it reports is only
    # auditable if every ddG says which draw it came from. n=0 (the map's own single draw) records 0/None,
    # so every ddg.json this lane has already produced describes itself correctly under the new schema too.
    "replicate": int(os.environ.get("REPLICATE") or 0), "seed": os.environ.get("SEED") or None,
    "ligand_a": cx["ligand_a"], "ligand_b": cx["ligand_b"],
    "ddg_bind_kcal": round(ddg, 3), "ddg_bind_unc_kcal": round(unc, 3),
    "dg_complex_morph_kcal": cx["dg_morph_kcal"], "complex_unc_kcal": cx.get("unc_kcal"),
    "dg_solvent_morph_kcal": sol["dg_morph_kcal"], "solvent_unc_kcal": sol.get("unc_kcal"),
    "n_mapped_atoms": cx.get("n_mapped_atoms"), "n_windows": int(os.environ["N_WINDOWS"]),
    "engine": "OpenFE RelativeHybridTopologyProtocol, HREX + MBAR (nr4a3_rbfe.py, MODE=splittest)",
    "uncertainty_note": "within-run MBAR standard errors, propagated in quadrature, for ONE independent "
                        "draw. NOT a replicate SD: a replicate SD exists only for an edge this lane ran at "
                        "more than one replicate index (see `replicate`).",
    "claim_ceiling": "CONDITIONAL relative binding free energy for a HYPOTHESIZED cmpd19 pose in ONE modeled "
                     "opened NR4A3 conformer. Not an affinity, not a selectivity claim.",
}
json.dump(r, open(f"{out}/ddg.json", "w"), indent=2)
print("S1F_RESULT", json.dumps(r))
PYEOF
$AWS s3 cp "$OUT/ddg.json" "$RESULT_S3/ddg.json" --only-show-errors
mark done
"""


def unit_label(unit, idx):
    """The Vast label this unit's host carries. PURE, and the home the submit path uses.

    Spelled out at nine call sites before this existed, which is eight opportunities for the reap, the
    progress census and the board to disagree about which box belongs to which edge — and a monitor that
    attributes a reading to the wrong rental is the silent-success class this lane's guards exist to stop.
    """
    return f"{LABEL_PREFIX}{idx:02d}-{unit['ligand_b']}"[:64]


def build_jobspec(unit, branch, bucket, idx, exclude_machine_ids=()):
    """JobSpec for ONE fan-out unit (both alchemical legs + reduce on a single rented 4090).

    `exclude_machine_ids` is applied to a PER-JOB COPY of FANOUT_RES, never to the module-level object: the
    fleet loop widens the exclusion set as it goes (so 18 units land on 18 distinct hosts instead of stacking
    on the single cheapest one and contending for its GPU), and mutating a shared dataclass would make every
    already-built spec change under it."""
    import dataclasses
    label = unit_label(unit, idx)
    # The per-unit price ceiling travels WITH the spec, so the offer the launcher actually rents is bound by
    # the same number `market_gate` cleared on — see ResourceSpec.max_usd_per_ns. Without this the gate
    # prices one board and `submit` buys off another.
    res = dataclasses.replace(FANOUT_RES, exclude_machine_ids=tuple(sorted(str(m) for m in
                                                                          exclude_machine_ids)),
                              max_usd_per_ns=_cf.unit_usd_per_ns_ceiling())
    result_s3 = f"s3://{bucket}/{RESULT_PREFIX}/{unit['unit_id']}"
    ckpt = checkpoint_prefix(unit, RESULT_PREFIX)
    pipeline = (_PREAMBLE + _LEG + _REDUCE).replace("{repo}", REPO)
    env = {
        "GIT_BRANCH": branch, "BUCKET": bucket, "STAGE_PREFIX": STAGE_PREFIX,
        "RESULT_S3": result_s3, "CKPT_PREFIX": ckpt,
        "UNIT_ID": unit["unit_id"], "EDGE_ID": unit["edge_id"], "LEG_ID": unit["leg_id"],
        "FRAME": unit["frame"], "N_WINDOWS": str(N_WINDOWS),
        # SEED and RBFE_STRICT_PROVENANCE are emitted by `unit_env` ONLY for a replicate (n>=1), and their
        # ABSENCE at n=0 is load-bearing — `rbfe_spot_checkpoint` hashes SEED into the resume fingerprint,
        # where unset and "0" are DIFFERENT values. See `congeneric_fanout.unit_env`. `gpu_backend
        # ._vast_onstart` `export`s every key here, so the engine invoked further down `_LEG` inherits them
        # without the bash needing to name them.
        **{k: v for k, v in unit_env(unit, "complex", N_WINDOWS).items()
           if k in ("RECEPTOR", "LIGAND_A", "LIGAND_B", "SEED", "RBFE_STRICT_PROVENANCE")},
        # Likewise conditional, so a tranche-1 spec is byte-identical to the one this lane has been
        # submitting all along.
        **({"REPLICATE": str(unit["replicate"])} if unit.get("replicate") else {}),
    }
    return JobSpec(name=label, command=["bash", "-lc", pipeline], image=FEP_IMAGE,
                   checkpoint_uri=f"s3://{bucket}/{ckpt}", resume=True, resources=res,
                   max_runtime_s=MAX_RUNTIME_S, env=env)


# ---- S3 helpers -------------------------------------------------------------------------------------------

def _s3():
    import boto3
    return boto3.client("s3")


def _exists(s3, bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except Exception:  # noqa: BLE001
        return False


def _get_json(s3, bucket, key):
    try:
        return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except Exception:  # noqa: BLE001
        return None


def _get_text(s3, bucket, key):
    try:
        return s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8", "replace").strip()
    except Exception:  # noqa: BLE001
        return None


# The board's denominator lives at the TOP of a leg log and those logs are megabytes of sampler chatter, so
# it is read with a RANGE rather than a full GET. Not an optimisation: `mode_monitor` runs on every tick with
# up to 19 units, and pulling whole leg logs to find one startup line would make the progress check — the one
# step §6 says must be the LAST thing a tick loses — the slowest and most failure-prone part of it.
_LOG_HEAD_BYTES = int(os.environ.get("FANOUT_LOG_HEAD_BYTES", "65536"))


def _get_text_head(s3, bucket, key, nbytes=None):
    """The first `nbytes` of an object as text, or None. A missing object and an unreadable one are both None
    — the caller renders `—` and says which fact is missing, never a default."""
    try:
        body = s3.get_object(Bucket=bucket, Key=key,
                             Range=f"bytes=0-{int(nbytes or _LOG_HEAD_BYTES) - 1}")["Body"].read()
        return body.decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None


def _live_instances(key):
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    return [i for i in insts if (i.get("label") or "").startswith(LABEL_PREFIX)]


def _age_min(inst):
    """Minutes since WE rented this instance.

    Uses `start_date` (epoch seconds, the rental start), NOT `duration` — on a Vast instance object `duration`
    is the HOST MACHINE's uptime, which reads in the hundreds of thousands of minutes for a long-lived
    community host. The collect reaper is age-based, so reading `duration` as our age would have destroyed
    every instance in the fleet on the first collect. Caught on the first live monitor (age_min 209141 = 145
    days on a box we had just rented)."""
    import time
    start = inst.get("start_date")
    if not start:
        return 0
    try:
        return max(0, round((time.time() - float(start)) / 60))
    except (TypeError, ValueError):
        return 0


# Expected sampler throughput, from the MEASURED cmpd19/NR4A3 rate: three independent wave-1 hosts at
# 12.76 / 13.70 / 14.42 s per HREX iteration (all 12 windows advanced 2.5 ps) => ~250-282 iterations/hour.
EXPECTED_ITER_PER_H = 3600.0 / 13.6

# ---- the stuck-start (create/start race) condemnation thresholds --------------------------------------------
# Chosen ABOVE the documented image-pull window, not below it. A cheap 4090 host legitimately spends 20-40 min
# pulling the ~6 GiB image and shows `loading` throughout, so an age cut inside that band would reap healthy
# hosts. 45 min sits past the top of it, and the empty-`status_msg` signature already excludes a host that is
# genuinely pulling — the two conditions together are what make this safe. Measured cases that motivated the
# number: s1f-00 (53 min), s1f-08 (52 min) and s1f-16 (49 min), all stopped with an empty status_msg, all
# nudged every tick since 8:53 AM ET, none ever starting.
STUCK_START_MIN = float(os.environ.get("STUCK_START_MIN", "45"))
# Two consecutive checks, per CLAUDE.md §4 — one sample can be an API blip or a listing caught mid-transition,
# and this action destroys a rental and writes a permanent machine exclusion. Never set to 1.
STUCK_START_STRIKES = int(os.environ.get("STUCK_START_STRIKES", "2"))
# The BACKSTOP ceiling for a stopped box whose status_msg is NOT empty, so the empty-msg escalation above
# never sees it. Deliberately ~3x STUCK_START_MIN: a ~6 GiB image pull legitimately runs 20-40 min on a cheap
# host, and the empty-msg discriminator exists precisely to protect those, so this must sit far beyond any
# plausible pull. It says only "whatever the message claims, this box has not reached running in well over
# two hours". Without it a box reporting e.g. 'Successfully loaded <image>' is re-nudged forever with no
# ceiling — the same unbounded retry the strike system already fixed once, for the other signature.
STUCK_START_HARD_MIN = float(os.environ.get("STUCK_START_HARD_MIN", str(3 * 45)))


def stuck_start_min_for(double_booked):
    """The age floor before a stopped, empty-`status_msg` host starts taking strikes. DERIVED, not typed.

    ★ WHY A DOUBLE-BOOKED DUPLICATE WAITS A THIRD AS LONG. `STUCK_START_MIN` is not a general patience
    setting — it buys exactly ONE thing, protection for a cheap host legitimately spending 20-40 min pulling
    the ~6 GiB image. That protection is meaningless for a container placed on a machine whose GPU this lane
    already holds: it is not pulling slowly, it has nothing to pull onto. Measured 2026-07-27 — 0 of 7 such
    instances ever started, at ages from 9 to 44 minutes, while 8 of 10 single-booked ones did.

    The cost of waiting is not the rental, it is the SLOT: these held 8 of the lane's 19 places, so real
    units could not be placed while containers that can never run occupied the fleet.

    ⚠ WHAT IS *NOT* RELAXED: the two-consecutive-strike rule (§4) is untouched for both classes, because the
    thing it guards against — a single API blip or a listing caught mid-transition — is just as possible
    here, and this path destroys a rental. And the floor is a fraction of the ONE home for the number, so a
    change to `STUCK_START_MIN` moves both together instead of leaving a second copy to drift.
    """
    return STUCK_START_MIN / 3.0 if double_booked else STUCK_START_MIN


_STARTED_MACHINES_KEY_SUFFIX = "_started_machines.json"


def observed_started_machines(live):
    """machine_ids on which one of OUR containers has demonstrably executed, from this listing. PURE.

    A non-empty `status_msg` is the evidence: `'success, running docker.io/triskit23/nr4a3fep…'`, or an
    apt line from the image build. Whatever it says, the box got as far as running our image, which is the
    exact thing a "never starts" verdict denies."""
    return sorted({str(i.get("machine_id")) for i in (live or [])
                   if i.get("machine_id") is not None and (i.get("status_msg") or "").strip()})


def _load_started_machines(s3, bucket):
    doc = _get_json(s3, bucket, f"{RESULT_PREFIX}/{_STARTED_MACHINES_KEY_SUFFIX}") or {}
    return {str(m) for m in (doc.get("machine_ids") or [])}


def _save_started_machines(s3, bucket, ids):
    try:
        s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/{_STARTED_MACHINES_KEY_SUFFIX}",
                      Body=json.dumps({"_what": "Vast machine_ids observed RUNNING one of this lane's "
                                                "containers. A machine on this list can never be condemned "
                                                "as 'never starts' — see never_started_cohort.",
                                       "machine_ids": sorted(ids), "updated_utc": _utcnow()},
                                      indent=2).encode())
    except Exception as e:  # noqa: BLE001 — an optimisation that must never block a tick
        print(f"[s1f] started-machine set save failed: {e}")


def never_started_cohort(live, excluded=(), known_good=()):
    """Classify every STOPPED s1f-* host into the THREE classes that have three different remedies. PURE.

    ★★★ THE MEASUREMENT THAT FORCED A THIRD CLASS (2026-07-27, 3:44 PM ET). Eight of nineteen live hosts
        carried the never-started signature and the obvious reading — "the board is full of bad hosts" — was
        WRONG. Grouping them by `machine_id` for the first time showed the discriminating fact:

            hosts that were the ONLY s1f-* instance on their machine   started 8 of 10
            hosts placed on a machine this lane was ALREADY renting    started 0 of 7

        Zero of seven. A Vast machine rents out a fixed number of GPUs; a second container on a box whose
        GPU we already hold has none to take, so it sits `stopped` with an empty `status_msg` — the SAME
        signature as a genuine create/start race, arrived at by our own double-booking. So most of the
        "dead hosts" were self-inflicted, and five of the machines involved (19492, 31035, 31036, 53989,
        24573) were at that moment RUNNING this lane's work at 76-98 % GPU.

    ⚠⚠ WHICH IS WHY THE REMEDY MUST SPLIT. Host-scoped exclusion is PERMANENT and CROSS-LANE — nothing ages
       an entry out (`vast_machine_blacklist.__doc__`). Condemning the double-booked cohort as "never
       starts" would have published five healthy, cheap machines to every lane in the repo, for a fault
       that was ours. That is the exact failure that module names as the expensive direction of the trade.

      * **double-booked** — never started, and an OLDER s1f-* instance of ours sits on the same machine.
        DESTROY the duplicate (it is billing and can never run), and record NOTHING against the machine.
        The machine becomes selectable again by itself once our other instance ends.
      * **host fault** — never started, and it is the only/oldest thing we have on that machine. Nothing
        about our workload enters the judgement, so this is HOST-SCOPED: destroy and publish cross-lane.
        Leaving it is not neutral — a host that never starts has INFINITE realised `$/ns`, invisible to
        `$/ns` ranking, so it keeps winning selection and keeps failing (machine 1569 took ten relaunches).
      * **preempted** — stopped with a NON-empty `status_msg` (`'success, running <image>'`). The box RAN
        and exited; CLAUDE.md §6 calls this routine. Resume it, and never exclude its machine.

    ⚠⚠ `known_good` IS WHAT KEEPS THE VERDICT STABLE, and it was added because the verdict was NOT
       (observed within 7 minutes on 2026-07-27). Instance 46031788 was correctly `double_booked` behind
       our own 46031535 on machine 53989; the collect then reaped 46031535 for being terminal, 46031788
       became the oldest thing we had there, and the SAME instance re-classified as `host_fault` — one
       strike away from publishing 53989 cross-lane and permanently. Machine 53989 had by then RUN two of
       this lane's containers (both reached 94-99 % GPU before exiting), so the verdict would have been
       flatly contradicted by our own evidence.

       A classification that changes because the OTHER instance was cleaned up is not a classification of
       anything. `observed_started_machines` accumulates, in S3, every machine we have watched run one of
       our containers, and a machine on that list can never be a host fault — "it refuses to start" is not
       a claim that survives having started.

    ⚠ `machine_excluded_now` IS NOT "we rented an excluded machine". It compares against the exclusion set
      AS IT IS NOW, and the set grows — another lane can publish a machine minutes after we rented it (144071
      was published between the 3:39 and 3:44 PM ticks, which is corroboration of a host fault, not proof of
      a selector bug). The ONLY evidence that the set failed to reach the selector is the launcher's own
      `excluding N machine(s)` line printed in the readout of the wave that placed the host. Do not upgrade
      this field into that claim.
    """
    excl = {str(m) for m in (excluded or ())}
    # Union with THIS listing: a machine running our container right now is proven good even on the very
    # first pass, before the durable set has ever been written.
    good = {str(m) for m in (known_good or ())} | set(observed_started_machines(live))
    stopped = [i for i in (live or []) if (i.get("cur_state") or "") == "stopped"]
    # The OLDEST live instance on a machine is the incumbent; anything younger on the same machine is a
    # duplicate WE placed. Ages come from the same listing, so this is an ordering, not a clock comparison.
    oldest_on = {}
    for i in (live or []):
        mid = None if i.get("machine_id") is None else str(i.get("machine_id"))
        age = _age_min(i)
        if mid is None or age is None:
            continue
        if mid not in oldest_on or age > oldest_on[mid][0]:
            oldest_on[mid] = (age, i.get("id"))
    never, preempted = [], []
    for i in stopped:
        mid = None if i.get("machine_id") is None else str(i.get("machine_id"))
        row = {"instance": i.get("id"), "label": i.get("label"), "machine_id": mid,
               "gpu": i.get("gpu_name"), "age_min": _age_min(i),
               "status_msg": (i.get("status_msg") or "")[:120]}
        if (i.get("status_msg") or "").strip():
            preempted.append(row)
            continue
        incumbent = oldest_on.get(mid or "")
        row["double_booked_behind"] = (incumbent[1] if incumbent and incumbent[1] != i.get("id") else None)
        row["machine_has_run_our_container"] = mid in good
        if row["double_booked_behind"]:
            row["klass"] = "double_booked"
            row["remedy"] = "destroy the duplicate; the machine is NOT at fault and must NOT be excluded"
        elif mid in good:
            # Not a host fault, and not our double-booking either — the box has run our image before, so
            # whatever stopped it this time is not "it refuses to start". Destroy and re-price elsewhere;
            # claiming more than the evidence supports is what a permanent shared exclusion would do.
            row["klass"] = "stopped_on_a_proven_machine"
            row["remedy"] = ("destroy and let the market gate re-price it; this machine has RUN our "
                             "container, so it cannot be condemned as one that never starts")
        else:
            row["klass"] = "host_fault"
            row["remedy"] = "destroy and publish the machine HOST-scoped: it never executed our container"
        row["machine_excluded_now"] = mid in excl
        never.append(row)
    by_machine = {}
    for r in never:
        by_machine.setdefault(r["machine_id"] or "unknown", []).append(r["label"])
    host_fault = [r for r in never if r["klass"] == "host_fault"]
    proven = [r for r in never if r["klass"] == "stopped_on_a_proven_machine"]
    return {
        "never_started": never,
        "preempted": preempted,
        "never_started_by_machine": {k: sorted(v) for k, v in sorted(by_machine.items())},
        # The headline: how much of the never-started population is ONE box. 1 means N separate hosts;
        # >1 means one machine took several units down together.
        "max_units_on_one_machine": max([len(v) for v in by_machine.values()] or [0]),
        "n_never_started": len(never), "n_preempted": len(preempted),
        "n_double_booked": len(never) - len(host_fault) - len(proven), "n_host_fault": len(host_fault),
        "n_stopped_on_a_proven_machine": len(proven),
        # The ONLY machines that earn a permanent cross-lane exclusion.
        "host_fault_machines": sorted({r["machine_id"] for r in host_fault if r["machine_id"]}),
        # Machines we hold a never-started rental on that SOMEONE has since excluded. Corroboration, not
        # an accusation — see the docstring.
        "machines_excluded_since": sorted({r["machine_id"] for r in never if r.get("machine_excluded_now")}),
    }


def _iter_rate(prev_entry, scalar):
    """Realised committed-iterations/hour since the previous check, or None if not computable.

    ★ THIS, NOT `gpu_util`, IS THE THROUGHPUT SIGNAL THAT ACTUALLY BINDS. `$/ns` ranking is blind to a host
    slower than its card because it multiplies a CARD CONSTANT (pricing.md A.1), and the obvious fix —
    watching `gpu_util` — turns out to depend on a field the Vast payload does not always carry (observed
    None on instance 45936074 at 20 minutes in, under BOTH spellings, while the box was demonstrably up and
    advancing). A monitor whose only health signal can silently go absent is a monitor that watches nothing.

    The committed-iteration rate has neither weakness: it comes from OUR OWN object store rather than the
    provider's telemetry, and it measures the realised throughput of THIS workload rather than a proxy for it.
    A host at half the expected rate is half as good per dollar whatever its `gpu_util` says.

    Deliberately reports rather than acts. Any single interval can be depressed by a legitimate freeze — MBAR
    analysis at the end of a leg, a phase transition, a checkpoint sync — so a rate is evidence for the
    stall/starvation judgement, not the judgement itself."""
    if not prev_entry or scalar < 0:
        return None
    was, when = prev_entry.get("scalar"), prev_entry.get("utc")
    if was is None or when is None or scalar <= was:
        return None
    try:
        import datetime
        t0 = datetime.datetime.strptime(when, "%Y-%m-%dT%H:%M:%SZ")
        hours = (datetime.datetime.utcnow() - t0).total_seconds() / 3600.0
    except (TypeError, ValueError):
        return None
    if hours <= 0:
        return None
    return round((scalar - was) / hours)


def _arm_watchdog(unit_ids, branch):
    """Add a watch entry for each unit this launch actually rented, so nothing is billed unwatched.

    WHY THIS IS DONE BY THE LAUNCHER AND NOT BY HAND. The fan-out can now fire from a cron the moment the
    terminus is proven, with no agent awake — and an 18-unit wave that arms nothing would put eighteen billed
    GPUs beyond any monitoring. The launcher is the only thing that knows what it just rented, so it is the
    only thing that can arm correctly. Entries are built by `vast_watchdog.step1_fanout_entry`, never
    hand-shaped, and the pass is idempotent: re-launching a unit already in the list re-enables it rather than
    duplicating it (two entries for one unit means two relaunchers on one checkpoint prefix).

    Failure here is logged, never raised: an arming problem must not abort a launch that has already spent
    money, and the CI step that commits the file reports an unchanged file plainly.
    """
    try:
        import vast_watchdog as vw
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vast-watch.json")
        with open(path) as fh:
            doc = json.load(fh)
        by_uid = {e.get("unit_id"): e for e in doc.get("watch", [])}
        added, rearmed = [], []
        for uid in unit_ids:
            if uid in by_uid:
                by_uid[uid]["enabled"] = True
                by_uid[uid].pop("_disabled_why", None)
                rearmed.append(uid)
            else:
                doc["watch"].append(vw.step1_fanout_entry(uid, git_branch=branch))
                added.append(uid)
        with open(path, "w") as fh:
            json.dump(doc, fh, indent=2)
        print(f"[s1f] watchdog armed: +{len(added)} new, {len(rearmed)} re-enabled "
              f"({len(doc['watch'])} entries total)")
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] ⚠ COULD NOT ARM THE WATCHDOG ({type(e).__name__}: {e}) — the units above are running "
              f"UNWATCHED. Add them to vast-watch.json by hand.")


def _gpu_util(inst):
    """GPU utilisation %, or None if the host is not reporting it.

    READ BOTH SPELLINGS. The Vast instance payload carries the live figure as `gpu_util` on some responses and
    `cur_gpu_util` on others (`nrv04_vast_launch`'s field list names the latter). Reading only one silently
    yields None on the other, and a starved-host guard that always sees None is a guard that watches nothing —
    which is exactly the defect class this repo keeps paying for. Observed on instance 45936074 at 7 min in:
    `gpu_util` absent while the box was demonstrably up.

    None is NOT zero and must never be treated as an idle GPU: 'the host is not telling us' and 'the GPU is
    idle' are different facts, and only the second is evidence of a problem."""
    for k in ("gpu_util", "cur_gpu_util"):
        v = inst.get(k)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return None


def _require_bucket():
    if not BUCKET:
        raise SystemExit("[s1f] VAST_CKPT_BUCKET is required")
    return BUCKET


# ---- committed progress: the ONLY durable evidence that the science advanced -------------------------------
#
# WHY THIS EXISTS AND WHY IT IS NOT `phase.txt`. `phase.txt` says WHICH phase a unit reached; it says nothing
# about whether that phase is still moving. A rented Vast box can sit up with a wedged container, a dead
# sampler or an idle GPU and keep reporting `leg-complex-running` forever, which is precisely the "monitoring
# that watches nothing" failure this repo has paid for repeatedly. The spot commit store is written by the
# sampler itself every RBFE_WARMUP_CKPT_ITERS / RBFE_PROD_CKPT_ITERS iterations, survives the instance, and
# its iteration number only goes UP — so it is the progress scalar, and `phase.txt` is context around it.
#
# Layout, from rbfe_spot_checkpoint.S3CommitStore:
#     <ckpt_prefix>/<leg>/<phase>/iter-XXXXXXXX/<generation>/COMMITTED.json
# The scalar ranks production above warmup so the warmup->production transition can never read as a
# regression, and ranks the solvent leg above the complex leg for the same reason (a unit runs complex first,
# so its committed iteration count RESETS when the solvent leg starts).
_PHASE_RANK = {"warmup": 0, "production": 1}
_LEG_RANK = {"complex": 0, "solvent": 1}
_PHASE_STRIDE = 1_000_000
_LEG_STRIDE = 10_000_000


def committed_progress(s3, bucket, unit):
    """(scalar, detail) of the furthest committed iteration of this unit. scalar < 0 means UNREADABLE.

    `readable=False` is emphatically not "zero progress": treating a listing failure as zero manufactures a
    stall out of a network blip. Callers must skip, not act, on a negative scalar."""
    base = f"{checkpoint_prefix(unit, RESULT_PREFIX)}"
    best = {}
    try:
        pag = s3.get_paginator("list_objects_v2")
        for page in pag.paginate(Bucket=bucket, Prefix=f"{base}/"):
            for obj in page.get("Contents", []):
                # .../<leg>/<phase>/iter-XXXXXXXX/<generation>/COMMITTED.json
                rest = obj["Key"][len(base):].lstrip("/").split("/")
                if len(rest) < 3 or not rest[2].startswith("iter-"):
                    continue
                leg, phase = rest[0], rest[1]
                if leg not in _LEG_RANK or phase not in _PHASE_RANK:
                    continue
                try:
                    it = int(rest[2].split("iter-")[1])
                except (IndexError, ValueError):
                    continue
                k = (leg, phase)
                best[k] = max(best.get(k, 0), it)
    except Exception as e:  # noqa: BLE001
        return -1, f"commit store unlistable: {type(e).__name__}: {e}"
    if not best:
        return 0, "no commit yet (boot / stage / setup / minimise)"
    (leg, phase), it = max(best.items(),
                           key=lambda kv: (_LEG_RANK[kv[0][0]], _PHASE_RANK[kv[0][1]], kv[1]))
    scalar = _LEG_RANK[leg] * _LEG_STRIDE + _PHASE_RANK[phase] * _PHASE_STRIDE + it
    return scalar, f"{leg}/{phase}@{it}"


# ---- host exclusion: realised throughput fed back into selection -------------------------------------------
#
# `$/ns` ranking multiplies a CARD CONSTANT (vast_cost_model.MEASURED_NS_PER_DAY_84K), so it is structurally
# blind to a host that is slower than its card — a starved host scores as if healthy, wins selection, and
# keeps winning (pricing.md section A.1). Same blind spot as a host that never starts: infinite realised
# $/ns, invisible to the ranking, which is why `ResourceSpec.exclude_machine_ids` exists at all.
#
# The exclusion set therefore lives in S3, NOT in this process: a launch in one CI run must see what a
# monitor in a different CI run learned, with no agent awake in between.
#
# ⚠ SCOPE, and it is narrower than the rule pricing.md A.1 first proposed and then WITHDREW. Excluding on low
# `gpu_util` alone was wrong there because the low utilisation was PLUMED's CPU-side metadynamics bias, and
# the same host ran at 74 % on the very next (unbiased) phase — so it would have discarded a host that is
# perfectly good for every non-metadynamics leg. What survives is the narrower statement: for a workload with
# NO per-step host-side work, the card constant IS the throughput model, so a sustained shortfall against it
# is a real defect in the host. This lane is plain RBFE — no PLUMED, no bias, no per-step CPU coupling — so
# the narrow rule applies here and the withdrawn broad one is not being re-adopted.
_EXCLUDE_KEY = f"{RESULT_PREFIX}/_excluded_machines.json"
# Healthy hosts on this class of work sit ~70-95 %. 40 % is well below the healthy band and well above the
# ~0 % an idle box reports, so it separates "starved" from both "fine" and "not started".
STARVED_UTIL_PCT = float(os.environ.get("FANOUT_STARVED_UTIL_PCT", "40"))
# Two CONSECUTIVE observations, because a single sample can catch a checkpoint sync, an S3 upload or the gap
# between two chunks. One sample is noise; two spaced ticks is the host.
STARVED_TICKS = int(os.environ.get("FANOUT_STARVED_TICKS", "2"))
# Nothing is judged before the box has had time to pull a ~6 GiB image and build the hybrid system. Below
# this age a low utilisation is a cold start, not starvation.
STARVED_MIN_AGE_MIN = float(os.environ.get("FANOUT_STARVED_MIN_AGE_MIN", "75"))


# ---- rental ledger: realised spend, measured rather than reconstructed ------------------------------------
#
# WHY A LEDGER AND NOT `step1-fanout-handles.json`. That file is REWRITTEN by every launch, so a two-stage
# fan-out (one shakeout unit, then the remaining eighteen) loses the first stage's rental the moment the
# second one runs — and "what did this actually cost" then has to be reconstructed from memory, which is
# exactly how this lane's cost estimate came to be wrong by ~4x in the first place. The ledger is in S3,
# append-only, and carries the BID (what Vast charges, up to the on-demand cap) rather than `dph_total`, so
# realised spend is bid x billed-hours and not an inference from a rate card.
#
# Billed hours come from `_age_min`, refreshed on every progress check and frozen at reap. A preempted box
# that never comes back still has its last observed age, so its hours are counted, not lost.
_LEDGER_KEY = f"{RESULT_PREFIX}/_rentals.json"


def _load_ledger(s3, bucket):
    return _get_json(s3, bucket, _LEDGER_KEY) or {"_what": "every s1f-* rental: bid $/hr x observed billed "
                                                           "hours = realised spend for this lane",
                                                  "rentals": {}}


def load_ledger_strict(s3, bucket):
    """The rental ledger, or a raise. The SPEND CAP's reader — `_load_ledger` is unsafe for that job.

    ⚠⚠ AN UNREADABLE LEDGER MUST FAIL **CLOSED** (2026-07-27, caught while verifying the cap's live
    reading). `_get_json` returns `None` on ANY exception, so `_load_ledger` cannot tell "this lane has
    never rented anything" from "S3 refused the read". For every other caller that is harmless. For the
    spend cap it is the worst possible defect: a credential problem or an S3 blip would make realised
    spend read **$0**, the cap would report full headroom, and the lane would rent freely for exactly as
    long as the outage lasted. A gate that opens when its evidence disappears is worse than no gate,
    because it fails silently and only under stress.

    This was not hypothetical when it was found: an `InvalidAccessKeyId` on this very bucket produced a
    confident "realised $0.0, headroom $74.91, breached=False" — a fabricated all-clear. It is the same
    discipline the market guard already applies to an unreadable board ("an unreadable market is not a
    cheap one"), and the same InvalidAccessKeyId that already has its own launch pre-flight.

    A genuinely ABSENT object is not an error — a lane that has never rented has no ledger — so
    `NoSuchKey`/404 returns the empty doc. Everything else raises.
    """
    try:
        raw = s3.get_object(Bucket=bucket, Key=_LEDGER_KEY)["Body"].read()
    except Exception as e:  # noqa: BLE001
        code = getattr(getattr(e, "response", None), "get", lambda *_a: {})("Error", {}).get("Code", "")
        if code in ("NoSuchKey", "404", "NoSuchBucket") or e.__class__.__name__ == "NoSuchKey":
            return {"rentals": {}}
        raise RuntimeError(f"rental ledger unreadable ({type(e).__name__}: {str(e)[:200]}) — the spend "
                           f"cap has no evidence, so nothing may be rented") from e
    return json.loads(raw)


def _save_ledger(s3, bucket, doc):
    try:
        s3.put_object(Bucket=bucket, Key=_LEDGER_KEY, Body=json.dumps(doc, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] ledger save failed: {e}")


def _utcnow():
    import datetime
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _et_now():
    """Now as US-Eastern 12-hour text. CLAUDE.md §1: the ONLY time format this repo reports in.

    Paired with `_utcnow` on purpose. The UTC stamp is what machines diff (`assert_progress_fresh`); this one
    is what a human reads at 3 AM without doing arithmetic, which is precisely the moment the arithmetic gets
    done wrong. Both go into every progress snapshot.
    """
    import datetime
    et = datetime.timezone(datetime.timedelta(hours=-4))          # EDT, as in step1_terminus_evidence.ET
    return datetime.datetime.now(datetime.timezone.utc).astimezone(et).strftime("%-I:%M %p ET %b %-d, %Y")


def ledger_cost(doc):
    """(total_usd, n_rentals, detail_rows). PURE, so the arithmetic is unit-testable.

    Uses the BID, falling back to `dph_total` only when no bid was recorded (an older entry). Missing rate or
    missing hours contribute 0 and are COUNTED as unpriced rather than silently dropped — an unpriced rental
    is a hole in the number, and a total that hides holes is worse than one that admits them."""
    total, rows, unpriced = 0.0, [], 0
    for iid, r in sorted((doc.get("rentals") or {}).items()):
        rate = r.get("bid") or r.get("dph")
        hours = (r.get("billed_min") or 0) / 60.0
        try:
            usd = float(rate) * hours
        except (TypeError, ValueError):
            usd, unpriced = 0.0, unpriced + 1
            rate = None
        total += usd
        rows.append({"instance": iid, "unit_id": r.get("unit_id"), "machine_id": r.get("machine_id"),
                     "rate_usd_h": rate, "billed_h": round(hours, 2), "usd": round(usd, 3)})
    return round(total, 2), len(rows), rows, unpriced


def ledger_cost_accrued(doc, live_ids=(), now_epoch=None, max_hours=None):
    """(total_usd, rows, n_accruing) — realised spend INCLUDING rentals not yet reconciled. PURE.

    ★★ WHY `ledger_cost` ALONE CANNOT BACK A SPEND CAP (2026-07-27, added with the cap itself).
    `billed_min` is written as **0** at launch and only becomes a real number when a later `collect`
    reconciles it against the instance's age. So a box rented by THIS tick contributes **$0** to
    `ledger_cost` until the next tick looks — and with placement self-replenishing under `always()`, the
    newly-rented units are exactly the ones a cap needs to see. A cap fed an undercounted total is worse
    than no cap at all, because it reads green while the lane is over: it converts a spend problem into a
    spend problem nobody is told about. The same undercount is why the rental ledger is now saved after
    EACH rental rather than after the wave — a mid-loop timeout used to leave rented boxes missing from
    realised spend entirely.

    THE RULE, and why it cannot run away in either direction:
      * a rental is OPEN if it has never been reconciled (`last_seen_utc` is None) or its instance is in
        `live_ids`. Open rentals accrue WALL-CLOCK from `launched_utc` to now, and the figure used is
        `max(recorded, accrued)` — never less than what was measured, never blind to what has not been.
      * a rental that has been reconciled and is no longer live is CLOSED: its `billed_min` was frozen
        before the reap (that freeze exists because a destroyed instance is unreadable afterwards), so it
        is authoritative and must NOT keep accruing. Without this a finished fleet would inflate forever
        and wedge the lane against its own ceiling.
      * accrual is capped at `max_hours` — the lane's own `MAX_RUNTIME_S`, derived, not typed. A rental
        whose box died without ever being reconciled would otherwise accrue without bound, and the failure
        mode of an unbounded over-count is a permanently-held lane, which §6 names as its own bug.

    Over-counting inside those bounds is the SAFE direction and is deliberate: a cap that errs must err
    toward holding, because holding is recoverable and an unnoticed overspend is not.
    """
    now = time.time() if now_epoch is None else now_epoch
    live = {str(i) for i in (live_ids or ())}
    cap_h = (MAX_RUNTIME_S / 3600.0) if max_hours is None else float(max_hours)
    total, rows, n_accruing = 0.0, [], 0
    for iid, r in sorted((doc.get("rentals") or {}).items()):
        rate = r.get("bid") or r.get("dph")
        recorded_h = (r.get("billed_min") or 0) / 60.0
        open_rental = (r.get("last_seen_utc") is None) or (str(iid) in live)
        accrued_h = 0.0
        if open_rental and r.get("launched_utc"):
            try:
                t0 = calendar.timegm(time.strptime(r["launched_utc"], "%Y-%m-%dT%H:%M:%SZ"))
                accrued_h = min(cap_h, max(0.0, (now - t0) / 3600.0))
            except (ValueError, TypeError):
                accrued_h = 0.0
        hours = max(recorded_h, accrued_h)
        try:
            usd = float(rate) * hours
        except (TypeError, ValueError):
            usd, rate = 0.0, None
        if open_rental and accrued_h > recorded_h:
            n_accruing += 1
        total += usd
        rows.append({"instance": iid, "unit_id": r.get("unit_id"), "rate_usd_h": rate,
                     "recorded_h": round(recorded_h, 2), "accrued_h": round(accrued_h, 2),
                     "open": open_rental, "usd": round(usd, 3)})
    return round(total, 2), rows, n_accruing


def spend_cap_state(ledger, live_ids=(), n_units=None, now_epoch=None):
    """(realised_usd, ceiling_usd, headroom_usd, breached, detail) — the lane's cumulative spend gate.

    ★★ WHY THIS EXISTS AT ALL (2026-07-27). Until now the ONLY thing gating this lane was the per-unit
    RATE line ($/ns). Realised spend was tracked and printed, and nothing ever refused on it. That gap was
    tolerable while the fleet was small and hand-placed; it stopped being tolerable the moment placement
    became self-replenishing under `always()`, because the lane will now keep re-renting to target width
    indefinitely and a rate check is passed *individually* by every cheap host. Fifteen hosts each
    comfortably under the line is precisely the shape that drains a budget while every row reads green —
    the rate line answers "is this a rate we will pay?", and nothing was answering "have we now spent the
    money that was authorised?"

    THE CEILING IS DERIVED, NEVER TYPED (CLAUDE.md rule 1). It is the authorised band top for the tranche —
    `congeneric_fanout.market_ceiling_usd(n_units)`, the same function the per-tick gate already prices
    against — so a ladder re-anchor moves the cap with it instead of leaving a stale constant behind. That
    figure already existed as the authorised band; this makes it BINDING rather than decorative.
    """
    n = len(default_units()) if n_units is None else int(n_units)
    ceiling = float(_cf.market_ceiling_usd(n))
    realised, rows, n_accruing = ledger_cost_accrued(ledger, live_ids=live_ids, now_epoch=now_epoch)
    return (realised, round(ceiling, 2), round(ceiling - realised, 2), realised >= ceiling,
            {"n_units_authorised": n, "n_rentals": len(rows), "n_accruing_unreconciled": n_accruing,
             "rows": rows})


# ---- the anti-idle guard: evidence gathering for `vast_idle_guard.classify_idle` ---------------------------
#
# The POLICY lives in `vast_idle_guard` and is shared with the ternary lane; only the EVIDENCE is lane-local,
# because only this lane knows where its own artifacts sit. `classify_idle` is pure, so everything below is
# "read one object, return a number or None", and every failure returns None — the guard treats None as
# "could not observe", never as "observed nothing", which is the difference between declining to act and
# manufacturing a condemnation.
_IDLE_PREV_KEY_SUFFIX = "_idle_prev.json"


def _log_age_min(s3, bucket, uid, now=None):
    """Minutes since this unit last PUT its `run.log`, or None if it never has / cannot be read.

    None is NOT "old". A missing run.log on a box whose container has started is genuinely no evidence, and
    `classify_idle` returns UNKNOWN for it rather than WEDGED."""
    import datetime
    try:
        h = s3.head_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/{uid}/run.log")
    except Exception:  # noqa: BLE001 — absent object or unreadable listing; both are "no evidence"
        return None
    lm = h.get("LastModified")
    if lm is None:
        return None
    now = datetime.datetime.now(datetime.timezone.utc) if now is None else now
    return max(0.0, (now - lm).total_seconds() / 60.0)


def _idle_evidence(s3, bucket, unit, inst, prev_scalar):
    """Everything `vast_idle_guard.classify_idle` needs about ONE live instance, gathered from this lane's
    own artifacts. Returns the kwargs dict, so the call site cannot quietly invent a field.

    ★ `progress_advanced` IS COMPARED AGAINST A GUARD-OWNED PREVIOUS CENSUS, NOT `_progress_prev.json`.
    That looked like a free reuse and is a trap: the autoscale tick runs monitor -> collect, and monitor
    OVERWRITES `_progress_prev.json` with the current census as its last act. Reading it here would compare
    this pass against itself, so `progress_advanced` would be False for every healthy leg in the fleet and
    the single clause that overrides every condemnation would be permanently disarmed — a guard that reaps
    working boxes. One owner, one file.
    """
    import watchdog_policy as wp
    uid = unit["unit_id"]
    scalar, _detail = committed_progress(s3, bucket, unit)
    phase = _get_text(s3, bucket, f"{RESULT_PREFIX}/{uid}/phase.txt")
    return {
        "instance_running": (inst.get("actual_status") or "") == "running",
        "container_started": wp.container_started_from_phase(phase, inst),
        "gpu_util": _gpu_util(inst),
        # A scalar of -1 means UNREADABLE, and an unreadable census must never read as "did not advance".
        "progress_advanced": (scalar >= 0 and prev_scalar is not None and scalar > prev_scalar),
        "log_age_min": _log_age_min(s3, bucket, uid),
        "start_ages_min": _vig.start_ages_min(s3, bucket, f"{RESULT_PREFIX}/{uid}/attempts/"),
        "instance_age_min": _age_min(inst),
    }, scalar


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ THE WAVE. A CAPACITY REFUSAL BOUNDS *THIS TICK* AND IS THEN FORGOTTEN (trimcrae, 2026-07-27: "don't add
# anything back unless you have a real reason to"; measured 2026-07-28).
#
# WHY THIS LANE NEEDED ITS OWN VERSION OF THE FIX, AND WHY THE 10:05 PM CLEAR DID NOT REACH IT. The shared
# set was emptied at 10:05 PM ET on 2026-07-27 and three `--lane-state` keys were cleared with it. This
# lane's list was NOT one of them: the clear was pointed at `nr4a3-step1-fanout/results/_lane_state.json`,
# a key `congeneric_fanout_vast` has never written — its list is `_EXCLUDE_KEY`,
# `nr4a3-step1-fanout/results/_excluded_machines.json`, under `machine_ids`. So `clear_lane_state` printed
# "no lane state — nothing to clear" and the fan-out's own 41 machines were untouched. The 10:10 PM tick,
# five minutes after a clear that reported 74 entries removed, filtered **41** machines. It then grew to
# 45 / 46 / 47 / 49 across the night while submits failed 1 / 2 / 4 / 2 with `no rentable verified offer`
# against a 158-offer board — our own filter, not the market.
#
# AND IT WOULD HAVE REGROWN EVEN IF THE CLEAR HAD REACHED IT, because `_record_exclusion` wrote EVERY reason
# into that permanent list. The stuck-start condemnation's reason — "cur_state=stopped with an empty
# status_msg … (create/start race, not an image pull)" — is `CLASS_CAPACITY` by
# `vast_machine_blacklist.classify_reason`, and the module records that verdict as one this repo has PROVEN
# WRONG: machines 53989, 31035 and 24573 were condemned on it and every one had run this lane's container at
# 94-99 % GPU. `publish` already refuses that class for the SHARED set. Nothing refused it here.
#
# WHAT REPLACES IT — the ternary lane's answer, in the shape this lane's storage takes. A capacity refusal
# goes into `capacity_wave`, tagged with the CI run that observed it. A different run does not read it. That
# is not a TTL and not an ageing policy — no duration is invented and nothing is dropped because it got old;
# the entry simply has no authority outside the wave whose observation produced it, exactly as
# `_blocked_machines` now has none outside the tick that wrote it. Within the tick it still does its job:
# the monitor condemns a busy host and the launch step, in the SAME run, does not try to rent it again.
#
# ⚠ WHY `GITHUB_RUN_ID` IS THE RIGHT WAVE KEY HERE. `step1-fanout-autoscale.yml` runs `MONITOR` and then
# `LAUNCH` as two steps of ONE job, so a refusal observed by the progress check binds the launch that
# follows it and nothing further. Off CI there is no run id, and then the capacity block is IGNORED — which
# is the safe direction: under-excluding costs one free failed submit, over-excluding costs capacity that
# compounds across lanes and nights.
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
def _wave_id():
    """The identity of the current wave. PURE-ish (reads env). "" when there is no wave (not on CI)."""
    return str(os.environ.get("FANOUT_WAVE_ID") or os.environ.get("GITHUB_RUN_ID") or "")


def wave_capacity_ids(doc, wave=None):
    """The capacity-refused machines that still bind, i.e. the ones THIS wave recorded. PURE.

    A block from another wave is not "expired" — it was never about anything but that wave.
    """
    cap = (doc or {}).get("capacity_wave") or {}
    w = _wave_id() if wave is None else str(wave or "")
    if not w or str(cap.get("wave") or "") != w:
        return set()
    return {str(m) for m in (cap.get("machine_ids") or [])}


def _load_excluded(s3, bucket):
    """This lane's DURABLE exclusions ∪ the SHARED cross-lane set ∪ THIS WAVE's capacity refusals.

    ⚠ THE UNION IS THE POINT (2026-07-27). Before it, this lane's set held exactly one machine while the 5a-KS
    lane knew nine — so the 6:37 AM tick resumed the shakeout onto machine 46392, which that lane had already
    condemned. A host that never starts has infinite realised $/ns and is invisible to $/ns ranking, so each
    lane was paying a rental to rediscover what the other already knew. See `vast_machine_blacklist` for what
    is shared (host-scoped only) and what deliberately is not.

    ⚠ AND THE THIRD TERM IS WAVE-SCOPED, NOT PERMANENT — see the block above. Returns `(ids, doc)` as before.

    ⛔⛔ SUPERSEDED 2026-07-31 (trimcrae: *"You've gotta just stop doing the blacklist. It seems like it only
    ever bites us in the ass and clearing it always makes things better."*). BOTH stored terms — this lane's
    durable `machine_ids` and the shared cross-lane set — are now dropped, and so is the wave block, because
    it lives inside the same retired object and a run-scoped set read from a durable artifact is exactly the
    thing that turned out to accumulate. The `doc` is still READ and still RETURNED, so `unit_condemnations`,
    the placement record and `vast_exclusion_census` keep working on the historical artifact; nothing
    consumes it for SELECTION. The switch and the evidence have one home, `vast_machine_blacklist`.

    What survives, and deliberately: `FANOUT_EXCLUDE_MACHINES`, an explicit per-dispatch operator input that
    nothing persists and nothing re-reads; `used_machines` at the fleet loop (double-rent prevention, not
    exclusion); and `gpu_backend.submit`'s in-call skip of a machine that just answered
    `resources_unavailable`, which is bounded to that placement call and dies with it.
    """
    doc = _get_json(s3, bucket, _EXCLUDE_KEY) or {}
    env = os.environ.get("FANOUT_EXCLUDE_MACHINES", "")
    ids = {m.strip() for m in env.split(",") if m.strip()}
    import vast_machine_blacklist as vmb
    if vmb.durable_enabled():
        ids |= {str(m) for m in (doc.get("machine_ids") or [])}
        ids |= wave_capacity_ids(doc)
    return (vmb.union(ids, s3, bucket) if vmb.durable_enabled() else sorted(ids)), doc


def unit_condemnations(doc, unit):
    """Distinct machines this UNIT has durably condemned, from the exclusion list's own history. PURE.

    Withdrawn and wave-scoped rows do not count — only entries that actually persist.
    """
    if not unit:
        return set()
    return {str(h.get("machine_id")) for h in ((doc or {}).get("history") or [])
            if h.get("unit") == unit and h.get("action") != "withdraw"
            and h.get("scope") != "wave" and h.get("machine_id") is not None}


def _record_exclusion(s3, bucket, machine_id, why, scope="lane", unit=None):
    """Record a machine this lane will not re-rent. `scope="host"` ALSO publishes it cross-lane.

    The default is `lane` on purpose: a verdict that mixes this workload with the machine (the starved-host
    rule below) must not be exported, because `pricing.md` A.1 withdrew exactly that reasoning once already.
    Only a failure that is about the MACHINE — it refuses starts, its container never executes — is shared.

    ★★ AND THE REASON IS CLASSIFIED AT THE DOOR. A `CLASS_CAPACITY` reason never reaches `machine_ids`, never
    reaches the shared set, and binds only the current wave — whatever `scope` the caller asked for, because
    `scope` says who a verdict is about and the CLASS says how long it is true for, and only one of those two
    questions was being asked here.

    ★★ AND A UNIT THAT HAS CONDEMNED THE LAST N MACHINES IS NOT EVIDENCE ABOUT MACHINES (2026-07-29).
    Measured by joining this lane's live exclusion list to the committed per-tick census: **15 durable
    machine exclusions were produced by 10 distinct units**, and the distribution is not flat —
    `s1f-13-cw_ms_free_acid` condemned 3 machines (138147-class instances 46031601 / 46081212 / 46004074),
    `s1f-03-cw_ev_5alkyne` condemned 3 (46060816 / 46071019 / 46041656), and `s1f-04-cw_ev_5ch2nh2` 2 —
    every one on the identical `gpu_util 0.0% for 2 checks` verdict. That is the same shape the ternary lane
    hit at far greater cost: two units re-rented across **35 and 49 separate hosts**.

    When one unit reports the same fault on host after host, the common factor is the UNIT. Blaming the
    machines converts a per-unit fault into a per-machine blacklist at a rate of one good host per attempt —
    which is a second, independent way for the filter to become the binding constraint on placement, and the
    one `leg_failure_breaker` does not cover (it stops the SPENDING on the 4th host; it does not un-blame the
    three already condemned, nor stop the blaming below its threshold).

    The threshold is `leg_failure_breaker.DEFAULT_THRESHOLD` — imported, not re-typed, because "how many
    distinct hosts before the unit is the suspect" is one question and must have one answer (rule 1).

    Returns True if the machine was newly recorded anywhere.

    ⛔⛔ RETIRED WITH THE LIST IT WRITES TO (trimcrae, 2026-07-31). A read path that returns nothing while the
    write path keeps growing the object is the worst of both worlds: the starvation would return silently the
    moment anyone flipped the switch back, inheriting a set nobody reviewed. So this now returns False without
    writing. Nothing else changes — the caller's own logging, the failure breaker and `vast_idle_guard` are
    untouched, and they are what actually stop money going to a bad host.
    """
    import vast_machine_blacklist as vmb
    if not vmb.durable_enabled():
        print(f"[s1f] NOT recording an exclusion for machine {machine_id} ({str(why)[:120]!r}): "
              f"{vmb._RETIRED_NOTE}", flush=True)
        return False
    ids, doc = _load_excluded(s3, bucket)
    mid = str(machine_id)
    perishable = vmb.classify_reason(why) == vmb.CLASS_CAPACITY

    if not perishable and unit:
        import leg_failure_breaker as _lfb
        prior = unit_condemnations(doc, unit) - {mid}
        if len(prior) >= _lfb.DEFAULT_THRESHOLD:
            print(f"[s1f] machine {mid} deliberately NOT excluded — unit {unit} has already condemned "
                  f"{len(prior)} distinct machine(s) ({sorted(prior)}) on its own verdicts. The common "
                  f"factor is the UNIT, not the hosts: a per-unit fault blaming a per-machine blacklist "
                  f"costs one good host per attempt. `breaker_decision` (this module) applies "
                  f"leg_failure_breaker's rule and stops buying the next host for this unit; nothing more "
                  f"is learned by retiring this one. Reason was: {why}")
            return False

    if scope == "host" and not perishable:
        vmb.publish(s3, bucket, mid, why, lane="step1_fanout")

    import datetime
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    hist = list(doc.get("history") or [])
    out = dict(doc)
    # ALWAYS present, even when empty: a reader (and `clear_lane_state`, which dispatches on which field the
    # doc actually has) must be able to tell "nothing durable is excluded" from "this is not that document".
    out["machine_ids"] = sorted({str(m) for m in (doc.get("machine_ids") or [])})
    out.setdefault("_what", "Vast machine_ids this lane refuses to re-rent. Realised throughput is not fed "
                            "back into $/ns ranking, so without this a bad host keeps winning selection "
                            "(pricing.md A.1). `machine_ids` is DURABLE; `capacity_wave` binds one tick.")

    if perishable:
        w = _wave_id()
        if not w:
            print(f"[s1f] machine {mid} NOT recorded: {why!r} is a CAPACITY refusal — a claim about a "
                  f"moment, not about the host — and there is no wave id to bind it to. It stays "
                  f"selectable; a re-test costs a free failed submit.")
            return False
        cap = out.get("capacity_wave") or {}
        cur = wave_capacity_ids(out, w)
        if mid in cur:
            return False
        out["capacity_wave"] = {"wave": w, "utc": now,
                                "_what": "capacity refusals observed by THIS CI run. Perishable: a later "
                                         "run does not read them. Not a TTL — see the WAVE block above.",
                                "machine_ids": sorted(cur | {mid}),
                                "why": {**(cap.get("why") or {}), mid: str(why)[:400]}}
        hist.append({"machine_id": mid, "why": why, "utc": now, "reason_class": vmb.CLASS_CAPACITY,
                     "scope": "wave", "wave": w, "unit": unit})
        print(f"[s1f] machine {mid} excluded for THIS WAVE ONLY (run {w}) — {why!r} is a capacity refusal, "
              f"a claim about a moment. It is selectable again on the next tick.")
    else:
        if mid in ids:
            return False
        out["machine_ids"] = sorted(set(doc.get("machine_ids") or []) | {mid})
        # ★ THE UNIT IS RECORDED, and that is what makes the guard above possible at all. Until now the
        # history said WHICH machine and WHY but never WHO — so "has this unit condemned three hosts?" was
        # unanswerable from the artifact and had to be reconstructed by joining the committed census.
        hist.append({"machine_id": mid, "why": why, "utc": now, "reason_class": vmb.CLASS_HOST,
                     "scope": scope, "unit": unit})

    out["history"] = hist
    try:
        s3.put_object(Bucket=bucket, Key=_EXCLUDE_KEY, Body=json.dumps(out, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] could not persist exclusion of machine {mid}: {e}")
        return False
    return True


def classify_durable_entries(doc):
    """Split this lane's DURABLE `machine_ids` by what their own recorded history says. PURE.

    Returns `{"host": [...], "capacity": [...], "unjustified": [...]}` — the third being ids on the list
    with no surviving history row at all, i.e. entries nobody can point at a reason for.
    """
    import vast_machine_blacklist as vmb
    hist = list((doc or {}).get("history") or [])
    out = {"host": [], "capacity": [], "unjustified": []}
    for mid in sorted({str(m) for m in ((doc or {}).get("machine_ids") or [])}):
        rows = [h for h in hist if str(h.get("machine_id")) == mid and h.get("action") != "withdraw"]
        if not rows:
            out["unjustified"].append(mid)
        elif all(vmb.classify_reason(h.get("why")) == vmb.CLASS_CAPACITY for h in rows):
            out["capacity"].append(mid)
        else:
            out["host"].append(mid)
    return out


def retire_perishable_exclusions(s3, bucket):
    """Take the PERISHABLE entries off this lane's durable list, judged on their OWN recorded reasons.

    ⚠⚠ WITHOUT THIS, THE FIX ABOVE FIXES NOTHING THAT IS ALREADY WRONG. Classifying at the door stops the
    NEXT capacity refusal becoming permanent; it does not touch the 49 already sitting in
    `_excluded_machines.json`, of which the recorded reasons say the large majority are exactly that class.
    Those are the entries that lost 1 / 2 / 4 / 2 authorised placements across the night of 2026-07-27 with
    `no rentable verified offer` against a 158-offer board. A fix that leaves them in place would ship a
    correct rule and an unchanged outcome.

    ★ THIS IS NOT A TTL AND NOT AN AGEING POLICY — the same line `withdraw_wrong_exclusions` draws. Nothing
    is retired for being old. An entry is retired because ITS OWN RECORDED REASON, re-read, is a claim about
    a moment (`vast_machine_blacklist.classify_reason` -> `CLASS_CAPACITY`) and this lane now stores that
    class wave-scoped. It is the retroactive application of the classification rule, not a clock.

    Entries with NO surviving reason are retired too, and counted separately in the log. trimcrae's rule is
    "don't add anything back unless you have a real reason to"; an entry nobody can name a reason for fails
    that test in the only direction that is cheap to be wrong in — re-discovering a genuinely bad host costs
    one FREE failed submit, while a wrong permanent entry is capacity lost across every lane and every night.

    Returns the retired ids. Idempotent: a second call finds nothing left to retire.
    """
    # The SHARED set gets the same treatment in the same breath — this lane reads `local ∪ shared`, so a
    # perishable entry over there filters our placements exactly as one of ours does, and on 2026-07-28
    # three of the shared set's four entries were that class. It is rule-application, not an overrule of
    # another lane's evidence; the argument is in `vast_machine_blacklist.retire_perishable.__doc__`.
    try:
        import vast_machine_blacklist as vmb
        vmb.retire_perishable(s3, bucket)
    except Exception as e:  # noqa: BLE001 — a repair must never be able to stop a launch
        print(f"[s1f] shared-set retire skipped: {type(e).__name__}: {e}")

    doc = _get_json(s3, bucket, _EXCLUDE_KEY) or {}
    if not (doc.get("machine_ids") or []):
        return []
    split = classify_durable_entries(doc)
    retire = sorted(set(split["capacity"]) | set(split["unjustified"]))
    if not retire:
        return []
    keep = sorted({str(m) for m in (doc.get("machine_ids") or [])} - set(retire))
    hist = list(doc.get("history") or [])
    hist.append({"machine_id": None, "action": "retire_perishable", "utc": _utcnow(),
                 "why": f"RETIRED {len(retire)} entr(ies) from the durable list: "
                        f"{len(split['capacity'])} whose own recorded reason classifies as CLASS_CAPACITY "
                        f"(a claim about a moment, now stored wave-scoped) and "
                        f"{len(split['unjustified'])} with no surviving reason at all.",
                 "retired_machine_ids": retire,
                 "retired_capacity": split["capacity"], "retired_unjustified": split["unjustified"]})
    try:
        s3.put_object(Bucket=bucket, Key=_EXCLUDE_KEY,
                      Body=json.dumps({**doc, "machine_ids": keep, "history": hist}, indent=2).encode())
    except Exception as e:  # noqa: BLE001 — this is a repair, and a repair must never fail a launch
        print(f"[s1f] could not retire perishable exclusions: {e}")
        return []
    print(f"[s1f] ⚖ RETIRED {len(retire)} perishable exclusion(s) from this lane's durable list "
          f"({len(split['capacity'])} capacity-class, {len(split['unjustified'])} with no recorded reason) "
          f"— {len(keep)} host-scoped entr(ies) remain: {keep}. A capacity refusal is a claim about a "
          f"moment; it now binds one wave. Retired: {retire}")
    return retire


def withdraw_wrong_exclusions(s3, bucket, proven_machines):
    """Remove machines from the exclusion sets that this lane condemned as "never starts" and has since been
    OBSERVED to run its container. Returns the withdrawn ids.

    ⚠⚠ WHY THIS HAD TO EXIST WITHIN AN HOUR OF THE SETS BEING UNIONED (2026-07-27). The condemnation verdict
    was unstable — a duplicate re-classified as a host fault the moment the reap removed the instance it was
    behind — and three machines that had run this lane's legs at 94-99 % GPU (53989, 31035, 24573) were
    condemned host-scoped, which is PERMANENT and CROSS-LANE. The consequence was immediate and measured:
    the very next tick excluded 38 machines against a 152-offer board and **4 of 5 authorised placements
    failed with `no rentable verified offer`**. The exclusion set, not the market, had become the binding
    constraint — precisely the "permanent and only grows" hazard `vast_machine_blacklist.__doc__` parks.

    ★ THIS IS NOT AN AGEING POLICY, AND MUST NEVER BECOME ONE. Nothing is withdrawn for being old; that
    question stays open for want of a measurement, and a guessed TTL would re-admit the hosts the set exists
    to refuse. A withdrawal needs POSITIVE CONTRARY EVIDENCE of the exact recorded claim: we watched the
    machine run our container. Entries recorded for any other reason (the lane-scoped throughput shortfall)
    are untouched, because start evidence does not contradict them.
    """
    import vast_machine_blacklist as vmb
    doc = _get_json(s3, bucket, _EXCLUDE_KEY) or {}
    ids = {str(m) for m in (doc.get("machine_ids") or [])}
    hist = list(doc.get("history") or [])
    withdrawn = []
    for mid in sorted({str(m) for m in (proven_machines or ())} & ids):
        rows = [h for h in hist if str(h.get("machine_id")) == mid and h.get("action") != "withdraw"]
        if rows and not any(vmb.is_never_started_reason(h.get("why")) for h in rows):
            continue                       # excluded for a reason that starting does not refute
        ids.discard(mid)
        hist.append({"machine_id": mid, "action": "withdraw",
                     "why": "WITHDRAWN: this machine has been observed RUNNING this lane's container, which "
                            "directly contradicts the never-starts verdict it was excluded on",
                     "utc": _utcnow()})
        withdrawn.append(mid)
        vmb.withdraw(s3, bucket, mid,
                     "observed running the step 1 fan-out's container after being condemned as never-starting",
                     lane="step1_fanout")
    if withdrawn:
        try:
            s3.put_object(Bucket=bucket, Key=_EXCLUDE_KEY,
                          Body=json.dumps({**doc, "machine_ids": sorted(ids), "history": hist},
                                          indent=2).encode())
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] could not persist the exclusion withdrawal: {e}")
            return []
        print(f"[s1f] ⚖ WITHDREW {len(withdrawn)} WRONG exclusion(s) {withdrawn}: each machine was "
              f"condemned as 'never starts' and has since been watched RUNNING this lane's container. An "
              f"over-grown set is not neutral — it reads as an unaffordable market and blocks placements.")
    return withdrawn


# ---- modes ------------------------------------------------------------------------------------------------

def mode_plan():
    _w = fanout_width()
    # `env=os.environ` so PLAN answers the question the operator actually asked — "what would a replicate
    # request for these edges produce?" — rather than always describing the bare map. A dry-run that cannot
    # be pointed at the thing about to be launched is not a dry run.
    p = plan(width=_w, env=os.environ)
    print(json.dumps(p, indent=2))
    print(f"\n[s1f] {p['n_units']} units, {_w}-wide -> {p['waves']['waves']} waves "
          f"(~{p['waves']['wall_clock_h_est']} h wall-clock), ${p['cost_usd_est'][0]}-{p['cost_usd_est'][1]}")
    rp = p.get("replicates")
    lane = lane_units()
    if rp:
        print(f"[s1f] + REPLICATES: {rp['n_units']} unit(s) over {len(rp['edges'])} edge(s) at indices "
              f"{rp['replicate_indices']} -> ${rp['cost_usd_est'][0]}-{rp['cost_usd_est'][1]} "
              f"(plan ${rp['cost_plan_usd']}). Lane total {len(lane)} units.")
        for uid in rp["units"]:
            print(f"[s1f]     {uid}   SEED={rp['seed_per_unit'][uid]}")
    # SELF-DESCRIBING, because this file is committed and a plan that does not say what it was asked is
    # indistinguishable from a plan for a different question.
    p["_generated_by"] = {
        "command": "PLAN=1 " + " ".join(f"{k}={os.environ[k]}" for k in
                                        ("FANOUT_REPLICATE_EDGES", "FANOUT_REPLICATES", "FANOUT_WIDTH")
                                        if os.environ.get(k)) + " python3 congeneric_fanout_vast.py",
        "spend": "$0 — PLAN makes no S3 call, no Vast call and rents nothing",
    }
    p["placement_dry_run"] = _plan_placement_dry_run(lane)
    with open("step1-fanout-plan.json", "w") as f:
        json.dump(p, f, indent=2)
    dr = p["placement_dry_run"]
    print(f"[s1f] dry run vs the last collected map: {dr['n_done']} done, {dr['n_blocked']} blocked, "
          f"{dr['n_would_place']} would be placed -> step1-fanout-plan.json")


def _plan_placement_dry_run(lane, map_path="step1-fanout-map.json"):
    """What LAUNCH would place, computed WITHOUT touching S3 or the Vast API. $0, rents nothing.

    ⚠ THE DONE-SET HERE IS THE LAST COLLECTED ARTIFACT, NOT S3. `mode_collect` writes
    `step1-fanout-map.json` from the real bucket, so this is a snapshot of S3 as of that tick and it is
    named as such in the output — the live authority is always the bucket. It is the right input for the
    question a dry run asks (would a replicate request be placed while the finished edges stay finished?)
    and the wrong input for anything that spends money, which is why nothing downstream of here does.

    The filter is `congeneric_fanout.pending_given`, the SAME function `_pending` returns from, so this
    cannot drift away from what the launcher would actually do."""
    here = os.path.dirname(os.path.abspath(__file__))
    src, done, blocked = None, set(), {}
    for cand in (map_path, os.path.join(here, map_path)):
        try:
            with open(cand) as fh:
                doc = json.load(fh)
            src, done = cand, {r["unit_id"] for r in doc.get("results", [])}
            blocked = doc.get("blocked_units") or {}
            break
        except Exception:  # noqa: BLE001 — no artifact is a legitimate state (a fresh checkout)
            continue
    would = _cf.pending_given(lane, done, blocked)
    n_done, n_blocked, _out = counts(lane, done, blocked)
    return {
        "_what": "Dry run: which units LAUNCH would place. No S3 call, no Vast call, no rental.",
        "_done_set_source": src or "NONE FOUND — every unit reads as unrun, which is a statement about "
                                   "this checkout, not about the bucket",
        "_authority": "s3://$VAST_CKPT_BUCKET/nr4a3-step1-fanout/results/<unit_id>/ddg.json is the live "
                      "authority; the artifact above is a snapshot of it from the last collect tick.",
        "n_lane_units": len(lane), "n_done": n_done, "n_blocked": n_blocked,
        "n_would_place": len(would),
        "done_units": sorted(done),
        "blocked_units": sorted(blocked),
        "would_place": [u["unit_id"] for u in would],
        "would_place_seeds": {u["unit_id"]: unit_env(u, "complex").get("SEED") for u in would},
    }


def mode_stage():
    """Free CPU: build the common-mode poses on the runner and upload them. Fails loudly on QC."""
    os.environ.setdefault("S3_BUCKET", _require_bucket())
    os.environ.setdefault("OUT_PREFIX", STAGE_PREFIX)
    import congeneric_pose_stage
    congeneric_pose_stage.main()


def mode_precheck():
    """No-spend gate: the staged tree exists in S3 and covers every endpoint of every unit."""
    bucket, s3 = _require_bucket(), _s3()
    qc = _get_json(s3, bucket, f"{STAGE_PREFIX}/stage_qc.json")
    if qc is None:
        raise SystemExit(f"[s1f] no stage_qc.json under s3://{bucket}/{STAGE_PREFIX}/ — run STAGE=1 first")
    # lane_units so a replicate request is precheck-ed too. Its endpoints are the same nodes as n=0's, so
    # this can never FAIL differently — but a precheck that silently ignores part of what LAUNCH will place
    # is a gate with a hole in it.
    units = lane_units()
    staged = {q["node"] for q in qc.get("qc", []) if q.get("status") == "ok"}
    needed = {u["ligand_a"] for u in units} | {u["ligand_b"] for u in units}
    missing = sorted(needed - staged)
    reval = [q["node"] for q in qc.get("qc", []) if q.get("needs_pose_revalidation")]
    for key in (f"{STAGE_PREFIX}/ligand/docked_{PRIMARY_RECEPTOR}.sdf",
                f"{STAGE_PREFIX}/receptor/{PRIMARY_RECEPTOR}-opened.pdb"):
        if not _exists(s3, bucket, key):
            raise SystemExit(f"[s1f] staged input missing: s3://{bucket}/{key}")
    print(f"[s1f] staged nodes OK: {len(staged)}/{len(needed)}  (method: {qc.get('_method', '?')[:80]}...)")
    print(f"[s1f] {'node':28s} {'status':10s} core rmsd    strain  soft severe  closest")
    for q in sorted(qc.get("qc", []), key=lambda x: x["node"]):
        print(f"[s1f] {q['node']:28s} {q['status']:10s} {str(q.get('core_atoms')):4s} "
              f"{str(q.get('core_rmsd_A')):8s} {str(q.get('core_geometry_strain_A')):7s} "
              f"{str(q.get('soft_contacts_lt_2.0A')):4s} {str(q.get('severe_clashes_lt_1.6A')):6s} "
              f"{q.get('closest_receptor_contact_A')}")
    strained = [q["node"] for q in qc.get("qc", []) if q.get("high_core_strain")]
    print(f"[s1f] high core strain (caveat on the edge, not blocking): {strained or 'none'}")
    print(f"[s1f] severe clash -> needs_pose_revalidation (caveat, not blocking): {reval or 'none'}")
    if missing:
        raise SystemExit(f"[s1f] PRECHECK FAIL — units reference unstaged nodes: {missing}")
    print("[s1f] PRECHECK OK — every unit's endpoints are staged from the common anchor pose")


_BLOCKED_KEY_SUFFIX = "_blocked_units.json"

# The ONE string a permanently-excluded unit is rendered with, everywhere. It deliberately does not look
# like a phase marker: `leg-complex-FAILED-rc1` is what a unit wears while it is about to be re-placed, and
# rendering an excluded edge the same way is what let one sit in the census overnight looking recoverable.
BLOCKED_PHASE = "BLOCKED-permanently-excluded"


def _load_blocked(s3, bucket):
    """Units this lane will NOT rent a host for, with the reason and the evidence. Durable, in S3.

    ★★ WHY THIS EXISTS (2026-07-27, s1f-09 cw_bio_nmethyl_amide). `_pending` meant "no ddg.json yet", and a
    unit that CANNOT produce one never leaves it — so every launch tick rented a fresh host, the leg aborted
    in minutes on the same defect, and the next tick rented another. It had already happened twice by the
    time it was diagnosed (12:55 and 13:12 ET). An unbounded loop of short rentals is not a large bill per
    attempt and is unbounded in time, which is the worst shape a spend can have.

    IN S3, NOT IN A PROCESS OR A CONSTANT, for the same reason the machine exclusion is: a fact learned by
    one CI run must bind the next one with no agent awake in between, and a code constant would not bind a
    tick running the previous commit.

    ⚠ A BLOCK IS NEVER SILENT. CLAUDE.md §6 names "holding silently" as a failure mode worse than the problem
    — a fleet that never launches must not look like one that finished. `_pending` prints every block it
    applies, `collect` writes them into the map artifact, and the entry carries `why` + `evidence` so the
    paper can state exactly which edges were not computed and on what grounds.
    """
    doc = _get_json(s3, bucket, f"{RESULT_PREFIX}/{_BLOCKED_KEY_SUFFIX}") or {}
    out = {k: v for k, v in (doc.get("units") or {}).items()}
    for uid in (u.strip() for u in os.environ.get("FANOUT_BLOCK_UNITS", "").split(",")):
        if uid:
            out.setdefault(uid, {"why": "FANOUT_BLOCK_UNITS env override", "evidence": None})
    return out


def counts(units, done_ids, blocked):
    """(n_done, n_blocked, n_outstanding) for a unit list. PURE — no S3, so the arithmetic is unit-tested.

    ★★ WHY THIS IS A FUNCTION AND NOT A SUBTRACTION. The launcher used the map size minus the pending
    set, which reads as obviously correct and is not: `_pending` filters out BOTH finished and blocked units, so
    the difference is "finished OR permanently excluded" and it was printed under the word `done`. On
    2026-07-28 the lane held nine ddG results and one blocked edge and its own readout said `done=10` — an
    edge that will never be computed rendering as a completed one, which is exactly the silent drop
    CLAUDE.md §6 forbids, and it made the artifact self-contradictory (10 done, 9 results, same file).

    ⚠ A blocked unit that ALSO has a result counts as DONE, not blocked. A result in hand is a result
    whatever list the unit is on, and the case is not hypothetical: a unit can be blocked after finishing,
    or unblocked and completed later. Ordering the tests this way is what keeps the three counts summing to
    len(units) with no unit in two buckets."""
    done_ids, blk = set(done_ids or ()), set(blocked or ())
    n_done = sum(1 for u in units if u["unit_id"] in done_ids)
    n_blocked = sum(1 for u in units if u["unit_id"] not in done_ids and u["unit_id"] in blk)
    return n_done, n_blocked, len(units) - n_done - n_blocked


def unit_phase(unit, blocked, has_result, phase_txt):
    """The ONE renderer of a unit's state, so every readout agrees. PURE.

    Precedence is deliberate and is the whole content of the function:
      a result       -> "done", even if the unit is also on the block list (a result in hand is a result);
      on the block   -> BLOCKED_PHASE, NOT the last phase marker it happened to leave behind;
      otherwise      -> whatever the phase marker says, or "not-started".

    The second clause is the fix. A blocked unit's `phase.txt` still holds the failure that got it blocked
    (`leg-complex-FAILED-rc1`), and every census, histogram and snapshot read that file directly — so a
    permanently-excluded edge rendered identically to one that had just crashed and was about to be
    re-placed. Overnight, that made a correctly-working guard look like an unattended failure."""
    if has_result:
        return "done"
    if unit["unit_id"] in set(blocked or ()):
        return BLOCKED_PHASE
    return (phase_txt or "not-started")


def computable_units(units, blocked):
    """The lane's honest DENOMINATOR: map edges minus the ones no host can ever compute. PURE.

    The map is 19 edges; what the fan-out can deliver is 19 minus the permanent exclusions, and that
    number has to be derived from the block map rather than typed, or it drifts the moment a block is added
    or lifted (CLAUDE.md rule 1)."""
    blk = set(blocked or ())
    return [u for u in units if u["unit_id"] not in blk]


_BREAKER_BASELINE_KEY_SUFFIX = "_breaker_baseline.json"


def _attempt_count(s3, bucket, unit_id):
    """How many container starts this unit has paid for, counted from its own archive in S3.

    Returns None when the listing fails. `leg_failure_breaker.decide` treats None as "not over the
    threshold", i.e. it FAILS OPEN — an unreadable bucket must not be able to halt a lane, and the worst
    case is one extra rental."""
    try:
        n, tok = 0, None
        while True:
            kw = {"Bucket": bucket, "Prefix": f"{RESULT_PREFIX}/{unit_id}/attempts/"}
            if tok:
                kw["ContinuationToken"] = tok
            page = s3.list_objects_v2(**kw)
            n += len(page.get("Contents", []) or [])
            if not page.get("IsTruncated"):
                return n
            tok = page.get("NextContinuationToken")
    except Exception as e:  # noqa: BLE001 — reported, never swallowed into a silent zero
        print(f"[s1f-breaker] could not count attempts for {unit_id}: {type(e).__name__}: {e}")
        return None


def _breaker_baselines(s3, bucket):
    """{unit_id: attempts already spent BEFORE the last time someone said the cause was fixed}.

    ★★ WHY A BASELINE AND NOT A DELETE (2026-07-29). `leg_failure_breaker.reset_for` re-arms a unit by
    DELETING its attempt archive, and for this lane that archive is the evidence — it is the only durable
    record that `cw_bio_primary_amide` was bought 25 times on 7 distinct cards, and that count is quoted in
    the manuscript and in the block reason. Destroying evidence to reset a counter is the wrong trade when
    an offset does the same job: the breaker counts attempts made SINCE the baseline, the archive stays
    whole, and the history a later reader needs is still there. Same principle as the append-only ledger —
    add a marker, never overwrite the record."""
    return dict(((_get_json(s3, bucket, f"{RESULT_PREFIX}/{_BREAKER_BASELINE_KEY_SUFFIX}") or {})
                 .get("units") or {}))


def breaker_decision(s3, bucket, unit, baselines=None):
    """Should this lane RENT for `unit`? The shared consecutive-failure rule, on step 1's own S3 layout.

    ★★ WHY THIS EXISTS AT ALL (2026-07-29). `leg_failure_breaker` was written for the ternary lane and this
    module referenced it in a comment — "See leg_failure_breaker, which stops buying the next host for this
    unit" — while never calling it. That sentence was false for this lane, and the gap is exactly what
    `cw_bio_primary_amide` fell through: 25 rentals, on 7 distinct card/driver combinations, every one dying
    at the same `LocalEnergyMinimizer` call, because nothing anywhere counted the attempts.

    The DECISION is `leg_failure_breaker.decide` — imported, not re-implemented — so the threshold and the
    wording have one home across both lanes (rule 1). Only the two lane-specific facts are supplied here:
    where the attempt archive lives, and how to read a status out of a `phase.txt` marker (this lane writes
    no `leg.json`).

    ⚠ IT ACTS AT THE MOMENT OF RENTING AND NOWHERE ELSE. Work already executing is never touched."""
    import leg_failure_breaker as lfb
    uid = unit["unit_id"]
    if _exists(s3, bucket, result_key(unit, RESULT_PREFIX)):
        return lfb.decide({"status": "done"}, 0)
    phase = (_get_text(s3, bucket, f"{RESULT_PREFIX}/{uid}/phase.txt") or "").strip()
    if not phase:
        # Never run. `decide` must let it run — a unit with no record has earned no suspicion.
        return lfb.decide(None, None)
    marker = phase.split()[0]
    status = "failed" if ("FAILED" in marker or "NORESULT" in marker) else "running"
    n = _attempt_count(s3, bucket, uid)
    base = int((baselines or {}).get(uid, 0) or 0)
    if n is not None:
        n = max(0, n - base)
    d = lfb.decide({"status": status, "phase": marker, "rc": marker.rsplit("-rc", 1)[-1]
                    if "-rc" in marker else None}, n)
    d["attempts_before_baseline"] = base
    return d


def _pending(s3, bucket, units, blocked=None):
    """Units with no ddg.json in S3 yet AND not blocked, in map order. Blocks are announced, never silent.

    The FILTER itself is `congeneric_fanout.pending_given` — pure, and therefore exercisable in a dry run
    against a known done-set. This function is the two S3 reads that supply its arguments plus the
    announcement of every block it applies."""
    blocked = _load_blocked(s3, bucket) if blocked is None else blocked
    done = {u["unit_id"] for u in units if _exists(s3, bucket, result_key(u, RESULT_PREFIX))}
    for u in units:
        if u["unit_id"] in done:
            continue
        b = blocked.get(u["unit_id"])
        if b:
            print(f"[s1f] BLOCKED, not launching {u['unit_id']}: {b.get('why')}"
                  + (f" (evidence: {b.get('evidence')})" if b.get("evidence") else ""))
    return _cf.pending_given(units, done, blocked)


_LAUNCH_LOG = []


def _lprint(msg):
    """print + retain, so the launch DECISION survives the CI log.

    monitor, collect and diag all write their readouts to committed files precisely because a GitHub job log
    is only readable from its tail and the tail is always runner boilerplate. `launch` was the one mode with
    no durable record — and it is the mode that spends money. It cost two diagnostic cycles on 2026-07-26 to
    answer "did the tick relaunch the preempted unit or not", a question the readout answers in one line."""
    print(msg, flush=True)
    _LAUNCH_LOG.append(str(msg))


def _write_launch_readout():
    try:
        with open("step1-fanout-launch-readout.txt", "w") as f:
            f.write("\n".join(_LAUNCH_LOG) + "\n")
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] could not write the launch readout: {e}")


_MARKET_HOLD_KEY_SUFFIX = "_market_hold.json"
# How long a hold may persist before it stops being a routine pause and becomes trimcrae's decision.
# ★ ELAPSED TIME, NOT A TICK COUNT, and that is deliberate: this repo's crons are throttled to roughly one
# run per workflow per hour whatever they ask for (measured 56-97 min for a */15), so "3 ticks" is not a
# knowable duration and a tick-based escalation would fire anywhere between 30 min and 5 hours.
MARKET_HOLD_ESCALATE_H = float(os.environ.get("FANOUT_MARKET_ESCALATE_H", "6"))

# ★★ THE SEVEN THINGS A TICK CAN DECIDE ABOUT PLACEMENT, and every one of them is written down.
#
# WHY THIS ENUM EXISTS (2026-07-27, 2:31 PM ET). `step1-fanout-market-hold.json` sat stamped 12:43 PM ET for
# 1 h 47 m while SEVEN autoscale ticks reported `success` and the fleet decayed 11 -> 5 with ten checkpointed
# units sitting hostless. Every one of those ticks was green. The artifact was stale because the ONLY writer
# of it was the price gate, and the price gate is reached only on the paths that get as far as pricing —
# so "we held on price", "there was nothing to place", "placement was switched off" and "the launch step
# never executed at all" were all indistinguishable from the outside. They are opposite facts.
#
# So the placement decision is now a NAMED value written on EVERY tick, and a stale `utc` can only ever mean
# the tick itself did not run. trimcrae's framing in §6: a hold is a correct outcome, a SILENT hold is the bug.
PLACEMENT_DECISIONS = {
    "placed":            "units were rented this tick",
    "price_hold":        "the $/ns gate refused some or all of them — snapshot attached",
    "nothing_pending":   "every unit has a ddg.json or is blocked; there is nothing left to place",
    "fleet_at_width":    "every pending unit already has a live instance, or the fleet is at FANOUT_WIDTH",
    "terminus_hold":     "reduce/commit/upload has never been observed, so the fan-out is not released yet",
    "credential_hold":   "the object-store credential a rental would be given cannot read the staged inputs",
    # ⚠ SUPERSEDED 2026-07-29 and retained: the tranche total no longer HOLDS placement (trimcrae: "the $75
    # ceiling was always an estimate, not a hard cap"). Kept registered because historical ledger rows carry
    # it and a reader must still be able to resolve what they meant. New breaches record
    # `over_tranche_estimate_advisory` instead.
    "spend_cap_hold":    "SUPERSEDED — the lane's REALISED cumulative spend reached its derived ceiling and "
                         "placement was HELD. That figure is now advisory; see "
                         "over_tranche_estimate_advisory. Historical rows only",
    "over_tranche_estimate_advisory":
                         "the lane's REALISED cumulative spend is past the derived TRANCHE ESTIMATE. "
                         "ADVISORY: an estimate of what the rung was expected to cost is not a spend "
                         "authorisation, so placement CONTINUED. Nothing here loosens a purchase gate — the "
                         "$/ns buy line and the per-launch band ceiling refuse independently and are "
                         "unchanged",
    "operator_hold":     "a person paused this lane; the hold file names who, when and why. Nothing is "
                         "rented until it is deleted — and reap, collect and supervision keep running",
    "placement_disabled": "this tick was asked to measure only — no placement was attempted",
    "cost_model_red":    "the unit-list / cost-model tests failed, so nothing may be rented",
    "breaker_hold":      "every remaining unit has failed on `leg_failure_breaker.DEFAULT_THRESHOLD` or "
                         "more separate rented hosts with nothing changing in between, so buying another "
                         "host tests nothing. NOT permanent and NOT a scientific exclusion: fix the cause, "
                         "then re-arm the unit (mode_block with FANOUT_UNBLOCK=1 records the current "
                         "attempt count as the new baseline)",
    "measurement_failed": "this tick's progress check or collect did not succeed, so the fleet was neither "
                          "measured nor reaped — adding hosts to it is the wrong direction",
    # ★ THE EIGHTH, ADDED 2026-07-28. Units cleared the price gate and STILL could not be placed, because
    # our own exclusion set had removed the board before ranking. It is the opposite fact from `price_hold`
    # and had no name, so for a night it wore that one's: 41 -> 49 excluded machines against a 158-offer
    # board, submits failing 1/2/4/2, and `step1-fanout-market-hold.json` reading as an ordinary market.
    "exclusions_hold":   "our own host-exclusion filter, not the market, is what stopped these units — the "
                         "board returned offers we would have bought and we had removed them first. Remedy "
                         "is to widen supply (withdraw a wrong exclusion), never to re-price",
}


def _write_market_hold(doc, s3=None, bucket=None):
    """The ONE writer of the placement record — S3 for durability, working tree for the commit step.

    Factored out of `market_gate` because being reachable only from the pricing path is exactly what made
    the artifact stale through seven green ticks. Every exit from `mode_launch` now goes through here.
    """
    if s3 is not None and bucket:
        try:
            s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/{_MARKET_HOLD_KEY_SUFFIX.lstrip('_')}",
                          Body=json.dumps(doc, indent=2).encode())
        except Exception as e:  # noqa: BLE001
            _lprint(f"[s1f] market-hold state not persisted: {e}")
    try:
        with open("step1-fanout-market-hold.json", "w") as fh:
            json.dump(doc, fh, indent=2)
    except Exception as e:  # noqa: BLE001
        _lprint(f"[s1f] market-hold readout not written: {e}")


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ "WE COULD NOT BUY" AND "WE WOULD NOT BUY" ARE OPPOSITE FACTS AND MUST NEVER PRINT THE SAME (trimcrae's
# §6 framing; measured on this lane 2026-07-27/28).
#
# `no rentable verified offer` is emitted BOTH when the market has nothing we can afford AND when our own
# filter ate the board before ranking. The remedies are opposite — wait for prices vs withdraw a wrong
# exclusion — and for a whole night this lane printed the second as the first: 41 -> 49 excluded machines
# against a 158-offer board at healthy prices, with the readout showing a price hold. `relaunch_market_gate`
# has named this `hold_cause: exclusions_or_spec_not_price` since 2026-07-27; the fan-out's placement record
# had no equivalent, so a reader of `step1-fanout-market-hold.json` could not see it without opening a log.
#
# THE DISCRIMINATOR IS THE SAME ONE THE RELAUNCH GATE USES, and it is an observation, not a heuristic: the
# board RETURNED offers and NONE survived the filter while N machines are excluded. Every placement record
# now carries the excluded count and ids unconditionally — so the number is visible on a healthy tick too,
# and a reader can watch it grow instead of discovering it at 49.
HOLD_CAUSE_EXCLUSIONS = "exclusions_or_spec_not_price"


def annotate_exclusions(doc, excluded, n_wave_held=0):
    """Stamp a placement record with what OUR OWN filter removed, and name the cause when it starved the
    board. PURE (mutates and returns `doc`).

    `n_wave_held` is the within-wave distinctness count (hosts we already hold or just rented) — it is not
    an exclusion and is reported separately, because conflating "we will not rent this machine" with "we are
    already ON this machine" is how a healthy 19-wide fan-out looks like an over-grown blacklist.
    """
    excl = sorted({str(m) for m in (excluded or ())})
    doc["n_excluded_machines"] = len(excl)
    doc["excluded_machine_ids"] = excl
    doc["n_wave_held_machines"] = int(n_wave_held)
    depth = doc.get("board_depth") or {}
    if excl and depth.get("offers_returned") and not depth.get("qualifying"):
        doc["hold_cause"] = HOLD_CAUSE_EXCLUSIONS
        doc["hold_cause_why"] = (
            f"NOT A PRICE HOLD — the board returned {depth['offers_returned']} offer(s) and NONE survived "
            f"the host filter while {len(excl)} machine(s) are excluded ({excl[:12]}). Either the exclusion "
            f"set has outgrown the market or the ResourceSpec is unsatisfiable; re-pricing will not fix "
            f"either. Review the exclusions (vast_machine_blacklist, "
            f"congeneric_fanout_vast.retire_perishable_exclusions) before touching the ceiling.")
        _lprint(f"[s1f] ⚠ {doc['hold_cause_why']}")
    return doc


def record_no_placement(decision, why, *, s3=None, bucket=None, key=None, n_withheld=0, excluded=()):
    """Write a refreshed placement record for a tick that rented nothing, and LOOK AT THE BOARD anyway.

    ★ THE BOARD READ IS THE POINT, not a decoration. The requirement this implements is *"refresh the market
    snapshot on EVERY tick even when nothing is placed, so a stale timestamp can never again mean 'we did not
    look'"*. If the reason for not placing is `nothing_pending`, the price of the board is irrelevant to THIS
    tick — but its freshness is the only thing that distinguishes a healthy quiet lane from a dead one, and
    that distinction is what cost 1 h 47 m of fleet decay. A failed board read is recorded as
    `board_unreadable`, never silently omitted: §6's fail-closed discipline says an unreadable market is not
    a cheap one, and here it is not an absent one either.

    The escalation clock is CLEARED on every one of these paths — not paused. Price is not what is stopping
    these units, so a clock that kept running would escalate the instant price became the binding gate, with
    a duration nobody could interpret. Same rule `market_gate` already applies when another gate is shut.
    """
    doc = {"_what": "Why the step 1 fan-out launched some, all or none of its units, priced per unit in "
                    "$/ns. Written on EVERY tick — including the ticks that rent nothing — because a stale "
                    "timestamp must only ever mean the tick did not run.",
           "_rule": "CLAUDE.md §6 — a thin, expensive market is a reason to PAUSE, not to pay. A hold is a "
                    "correct outcome; a SILENT hold is the bug.",
           "utc": _utcnow(), "decision": decision,
           "decision_why": why,
           "decision_meaning": PLACEMENT_DECISIONS.get(decision, "unrecognised decision code"),
           "held": decision not in ("placed", "nothing_pending", "fleet_at_width"),
           "n_withheld": int(n_withheld), "n_launching_now": 0, "n_held": int(n_withheld),
           "placed_usd_per_ns": [], "placed_x_basis": [],
           "spend_authorised_now_usd": 0.0, "ceiling_for_that_spend_usd": 0.0,
           "binding_gate": decision, "binding_gate_why": why,
           "binding_gate_scope": ("all %d withheld unit(s)" % int(n_withheld)) if n_withheld else None,
           # The clock is cleared, not paused — see the docstring.
           "price_blocks_every_unit": False, "first_held_utc": None, "held_hours": 0.0,
           "held_reason": why}
    try:
        basis = market_basis()
        _dollar_ceil, _rate_line, _eff, _which = _cf.unit_ceiling_components()
        doc.update({"basis_usd_per_ns": round(basis, 6),
                    "unit_usd_per_ns_ceiling": round(_eff, 6),
                    "unit_ceiling_x_basis": round(_eff / basis, 3),
                    "unit_dollar_ceiling_usd_per_ns": round(_dollar_ceil, 6),
                    "unit_rate_line_usd_per_ns": round(_rate_line, 6),
                    "which_ceiling_binds": _which})
    except Exception as e:  # noqa: BLE001
        doc["ceiling_unreadable"] = f"{type(e).__name__}: {e}"
    if key:
        try:
            _mean, depth, rows = market_snapshot(key, max(1, int(n_withheld) or 1), excluded)
            doc["board_depth"] = depth
            doc["offers_priced"] = rows
            doc["board_unreadable"] = None
        except Exception as e:  # noqa: BLE001
            doc["board_depth"], doc["offers_priced"] = None, []
            doc["board_unreadable"] = f"{type(e).__name__}: {e}"
            _lprint(f"[s1f] board snapshot unreadable this tick ({type(e).__name__}: {e}) — recorded as "
                    f"unreadable, NOT as absent.")
    annotate_exclusions(doc, excluded)
    _lprint(f"[s1f] PLACEMENT DECISION: {decision} — {why}")
    if doc.get("offers_priced"):
        best = doc["offers_priced"][0]
        _lprint(f"[s1f]   board looked at anyway: {doc['board_depth']['offers_returned']} offers, best "
                f"${best['usd_per_ns']:.6f}/ns on {best['gpu']} m{best['machine_id']}. Snapshot refreshed, "
                f"so a stale timestamp on this file can only mean the TICK did not run.")
    _write_market_hold(doc, s3, bucket)
    return doc


def market_snapshot(key, n_units, excluded=()):
    """(best_usd_per_ns, depth, rows) for a fleet of `n_units` from a LIVE Vast board read.

    `best_usd_per_ns` is the MEAN over the `n_units` cheapest qualifying offers, not the single best one —
    a fleet of 19 buys the 19 best offers, and pricing it off the one cheapest host would flatter a thin
    board exactly when the board being thin is the thing we are trying to detect. If fewer than `n_units`
    qualify, the mean is over what exists and `depth` records the shortfall, because a board that cannot
    fill the fleet is decision-relevant on its own even when its prices look fine.

    Ranking is delegated to `gpu_backend.rank_offers_by_usd_per_ns`, which is the same filter+score the
    renting path uses, so the guard cannot price a fleet the launcher would not actually buy."""
    from gpu_backend import _vast_offer_query, rank_offers_by_usd_per_ns
    res = FANOUT_RES
    if excluded:
        res = dataclasses.replace(res, exclude_machine_ids=tuple(str(m) for m in excluded))
    offers = _vast_request("GET", "/search/asks/", key,
                           params={"q": json.dumps(_vast_offer_query(res))}).get("offers", [])
    measured, capable = rank_offers_by_usd_per_ns(offers, res)
    take = measured[:max(1, int(n_units))]
    rows = [{"gpu": o.get("gpu_name"), "machine_id": o.get("machine_id"),
             "min_bid": p, "usd_per_ns": round(upn, 6)} for upn, p, o in take]
    depth = {"offers_returned": len(offers), "qualifying": len(capable), "priceable": len(measured),
             "needed": int(n_units), "used_for_mean": len(take)}
    best = (sum(r["usd_per_ns"] for r in rows) / len(rows)) if rows else None
    return best, depth, rows


def binding_gate(gates):
    """The FIRST gate that is refusing, or None if price is the only thing left. PURE -> unit-tested.

    `gates` is an ordered [(name, clear, why)] of every gate evaluated BEFORE price. Order matters only for
    which name is reported when several are shut; all of them appear in the readout regardless.
    """
    for name, clear, why in gates:
        if not clear:
            return name, why
    return None


def market_gate(n_withheld, bucket, s3, key, excluded=(), gates=()):
    """HOW MANY of `n_withheld` units may be rented right now. 0 = a full hold; n_withheld = launch all.

    ⛔ CLAUDE.md §6: *"A THIN, EXPENSIVE MARKET IS A REASON TO PAUSE, NOT TO PAY."* trimcrae, 2026-07-26:
    *"I'd rather pause until availability opens than pay double per ns."*

    ★★ AND IT PAUSES PER UNIT, NOT PER FLEET (trimcrae, 2026-07-27: *"The fanout fleet doesn't all have to
    run at the same time. If 5 GPUs are cheap enough and the rest aren't, only run 5."*). This used to take
    a MEAN over the N cheapest offers and hold all-or-nothing, which refused cheap capacity because
    expensive capacity existed beside it: on the board that prompted the change, offers at 1.71x and 1.77x
    basis were declined because three at 4.44x/4.63x/6.95x dragged the mean to 3.25x. §6 exists to stop us
    PAYING a bad rate, not to stop us TAKING a good one, and the mean was never the right statistic for an
    all-or-nothing decision. The placement arithmetic is `congeneric_fanout.place_units`, which also carries
    the proof that splitting is scientifically free and costs the ladder nothing.

    The exposure this exists for is not a single host — it is the 18-edge release, which fires AUTOMATICALLY
    on the shakeout unit's ddg.json. On the night the rule was written the board had thinned to 5 offers from
    a ~23 baseline at a $0.333/hr median floor, which prices this tranche at ~$87 against the $15-80 that was
    authorised. An automatic release into that market would have spent past its own authorisation with nobody
    choosing to.

    TWO FAILURE MODES THE RULE NAMES, both worse than the problem, and how each is answered here:
      * **A silent hold is indistinguishable from a finished fleet.** So every hold is written to the launch
        readout AND to `<results>/_market_hold.json` AND to a committed `step1-fanout-market-hold.json`, each
        carrying the snapshot that caused it. A reader at 3 AM gets the projected cost, the ceiling, the
        board depth and the offers that were priced — not "nothing to submit".
      * **A ceiling nobody can clear turns into an idle night.** The first hold records `first_held_utc`; once
        the hold has persisted past `MARKET_HOLD_ESCALATE_H` the readout stops being a notice and becomes a
        hard `::error::` that FAILS the job, which fires GitHub's own workflow-failure notification — the
        same session-independent alert path the watchdogs already rely on, so it reaches trimcrae with no
        agent awake. The guard never buys in on its own; the escalation hands him the decision.

    ★★ THE ESCALATION ONLY FIRES WHEN PRICE IS THE **BINDING** CONSTRAINT (2026-07-27, after this escalated
    "held 9.9 h on a bad market" while the TERMINUS was unmet — so the eighteen units could not have launched
    at any price, and the 9.9 h measured a window in which this gate was never what was stopping them).
    That is crying wolf, and it is the same class of error as the 4 AM escalation that read `first_held_utc`
    as a duration: an alert that fires on a hold price did not cause trains everyone to ignore the alerts
    that matter.

    So `gates` carries every gate evaluated BEFORE price, and:
      * if any of them is shut, this still HOLDS and still writes its snapshot — the price reading is real
        and worth recording — but it does NOT escalate, and it **clears `first_held_utc` so the clock is not
        merely paused but not running at all.** A clock that keeps ticking through a terminus block would
        escalate the instant the terminus cleared, with a duration nobody could interpret.
      * only when every other gate is CLEAR does the clock start, from that moment.
    The readout NAMES the binding gate either way, so a reader cannot repeat the misreading.

    ⚠ HOW THIS LANE ACTUALLY PRODUCED THE FALSE ALARM, because the shape matters: the terminus gate is
    applied only under `FANOUT_REQUIRE_PROVEN_TERMINUS=1`, which the autoscale tick sets and a manual
    `fanout_mode=launch` dispatch does not. The hold clock lives in S3 and is SHARED by both paths, so one
    dispatch that ignored the terminus poisoned the timer for the path that honours it. Passing the terminus
    in as a gate — computed from `done`, which the caller already has, at zero extra S3 cost — makes the
    clock independent of which entry point wrote it.

    `n_withheld` is the number of units this hold is actually REFUSING TO BUY, and it is deliberately
    neither of its two neighbours. Not `len(batch)`: that is slot-limited, so a narrow tick would price a
    slice and wave a tranche through a few units at a time — the salami the tranche-level test exists to
    stop. Not `len(pending)`: that counts units already rented and running, whose cost is already committed,
    which is how a 19-unit ceiling ($80.44) got quoted against an 18-unit hold ($76.21) and made the hold
    look worse than it was. It is the pending units with no live instance — the set that would go out if
    this gate said yes.
    """
    global _MARKET_GUARD_RAN
    hkey = f"{RESULT_PREFIX}/{_MARKET_HOLD_KEY_SUFFIX.lstrip('_')}"
    prev = _get_json(s3, bucket, hkey) or {}
    blocking = binding_gate(gates)
    try:
        _best_mean, depth, rows = market_snapshot(key, n_withheld, excluded)
    except Exception as e:  # noqa: BLE001
        # A board we could not READ is not a board we may assume is cheap. Same discipline as the watchdog's
        # "unreadable is not zero": refuse, and say the refusal was for lack of evidence.
        _MARKET_GUARD_RAN = True
        _lprint(f"[s1f] ⛔ MARKET GUARD COULD NOT READ THE BOARD ({type(e).__name__}: {e}) — HOLDING 0/"
                f"{n_withheld}. An unreadable market is not a cheap one, and this gate exists precisely for "
                f"the case where nobody is awake to check.")
        # Still write the record: an unreadable board is a DECISION, and the one thing that must never
        # happen is this file keeping yesterday's timestamp while the fleet drains.
        record_no_placement("price_hold", f"the Vast board could not be read ({type(e).__name__}: {e}) — "
                                          f"fail-closed, nothing rented",
                            s3=s3, bucket=bucket, key=None, n_withheld=n_withheld)
        return 0
    _MARKET_GUARD_RAN = True
    basis = market_basis()
    unit_ceiling = _cf.unit_usd_per_ns_ceiling()

    # PER-UNIT PLACEMENT. Each unit is judged on the offer it would actually occupy, one unit per offer
    # (two on one host contend for its GPU). `rows` is already ranked ascending by the SAME
    # rank_offers_by_usd_per_ns the renting path uses, so the gate cannot admit an offer the launcher
    # would not buy.
    ranked = [r["usd_per_ns"] for r in rows]
    n_place, placed, why_none = _cf.place_units(ranked, n_withheld, unit_ceiling)
    n_held = max(0, int(n_withheld) - n_place)
    spend_now = _cf.projected_tranche_usd(max(placed), n_place) if placed else 0.0
    ceiling_now = _cf.market_ceiling_usd(n_place) if n_place else 0.0

    _dollar_ceil, _rate_line, _eff_ceil, _which_binds = _cf.unit_ceiling_components()
    _lprint(f"[s1f] MARKET GUARD ($/ns per unit, CLAUDE.md §6): board {depth['offers_returned']} offers -> "
            f"{depth['qualifying']} qualifying, {depth['priceable']} priceable. A unit must clear BOTH the "
            f"dollar ceiling ${_dollar_ceil:.6f}/ns ({_dollar_ceil / basis:.2f}x, derived from "
            f"market_ceiling_usd(1) / reference_ns_per_unit) AND the "
            f"{_cf.drift_buy_line_x_basis():.2f}x drift line "
            f"${_rate_line:.6f}/ns — effective ${unit_ceiling:.6f}/ns "
            f"({unit_ceiling / basis:.2f}x), binding on the {_which_binds}. "
            f"(trimcrae 2026-07-27: a row that prints ⚠ DRIFT is a row we do not buy.)")
    # ★ THE LINE THE RULE ACTUALLY REQUIRES. §6 forbids both a silent hold and a silently dropped unit, and
    # a PARTIAL launch is where those are easiest to commit: a tick that launches 5 of 19 and says nothing
    # about the 14 is precisely the failure. So both halves are always printed, with the price the held
    # units are waiting for.
    _lprint(f"[s1f] PLACEMENT: {n_place} unit(s) LAUNCHING NOW, {n_held} HELD for a better board "
            f"(of {n_withheld} withheld this tick).")
    for u in placed:
        # ⚠ DRIFT is now UNREACHABLE on a placed unit — the drift line and the buy line are the same number
        # since trimcrae's ruling. Printed anyway: a guard that cannot report its own failure is how this
        # lane keeps finding things late.
        # ⚠ THE TEST IS THE ABSOLUTE RATE, NOT `>= 1.5x` (CLAUDE.md §1). Typed as a multiple, this printed
        # "⛔ DRIFT ABOVE THE BUY LINE — this must not happen" against a unit at 1.72x that the gate had
        # just CORRECTLY cleared (12:44 PM ET 2026-07-27, instance 46021708), because the basis moved under
        # the constant. A guard that cries wolf on its own passing rows is how a real refusal gets ignored.
        _lprint(f"[s1f]   launch @ ${u:.6f}/ns · {u / basis:.2f}x basis"
                + ("  ⛔ DRIFT ABOVE THE BUY LINE — this must not happen"
                   if u >= _cf.unit_rate_line_usd_per_ns() else ""))
    if n_held:
        _lprint(f"[s1f]   HELD {n_held} unit(s) on the {_which_binds}: waiting for an offer at or below "
                f"${unit_ceiling:.6f}/ns ({unit_ceiling / basis:.2f}x basis). "
                + (why_none or f"the board had only {n_place} offer(s) that cheap this pass.")
                + " They are NOT dropped — the pending set is recomputed from S3 every tick, so they go out "
                  "automatically as the board improves.")
    if n_place:
        _lprint(f"[s1f]   spend authorised THIS TICK: ${spend_now} against ${ceiling_now} — the ceiling for "
                f"the {n_place} unit(s) actually being BOUGHT, not for the notional full tranche.")

    _decision = "placed" if n_place else ("price_hold" if n_held else "nothing_pending")
    doc = {"_what": "Why the step 1 fan-out launched some, all or none of its units, priced per unit in "
                    "$/ns. Written on EVERY guard pass, because a silent hold is indistinguishable from a "
                    "finished fleet — and a partial launch that reports only what it launched is the same "
                    "failure wearing a better number.",
           "_rule": "CLAUDE.md §6 — a thin, expensive market is a reason to PAUSE, not to pay. Per-unit "
                    "since 2026-07-27 (trimcrae): if 5 GPUs are cheap enough and the rest are not, run 5.",
           "utc": _utcnow(), "decision": _decision,
           "decision_meaning": PLACEMENT_DECISIONS.get(_decision),
           "decision_why": (why_none if n_held else None),
           "held": (n_held > 0), "n_withheld": n_withheld,
           "n_launching_now": n_place, "n_held": n_held,
           "unit_usd_per_ns_ceiling": round(unit_ceiling, 6),
           "unit_ceiling_x_basis": round(unit_ceiling / basis, 3),
           "unit_dollar_ceiling_usd_per_ns": round(_dollar_ceil, 6),
           "unit_rate_line_usd_per_ns": round(_rate_line, 6),
           "which_ceiling_binds": _which_binds,
           "placed_usd_per_ns": [round(u, 6) for u in placed],
           "placed_x_basis": [round(u / basis, 2) for u in placed],
           "basis_usd_per_ns": round(basis, 6),
           "spend_authorised_now_usd": spend_now, "ceiling_for_that_spend_usd": ceiling_now,
           "held_reason": why_none,
           "board_depth": depth, "offers_priced": rows,
           "binding_gate": (blocking[0] if blocking else ("price" if n_held else None)),
           "binding_gate_why": (blocking[1] if blocking else None),
           # ★★ WHICH UNITS `binding_gate` IS TALKING ABOUT — added 2026-07-27 because without it the record
           # read as a flat self-contradiction. A snapshot carried `binding_gate: "price"` and
           # `price_is_binding: false` at the same instant, and no reader could tell that those two fields
           # were answering DIFFERENT QUESTIONS rather than disagreeing about one. They were: 2 of 9 units
           # had just been placed and 7 were withheld on price, so price was indeed what stopped the 7
           # (`binding_gate`) and was equally NOT stopping the fleet as a whole (the escalation test). Both
           # were correct; the naming was not. The scope says out loud how many units the verdict covers.
           "binding_gate_scope": (None if (blocking is None and not n_held) else
                                  ("all %d withheld unit(s)" % n_withheld if n_place == 0 else
                                   "%d of %d withheld unit(s) — the other %d were placed this tick"
                                   % (n_held, n_withheld, n_place)))}

    # ★★ THE HOLD CLOCK RUNS ONLY WHILE PRICE IS BLOCKING *EVERY* UNIT.
    #
    # Cleared — not paused — whenever another gate is shut, and whenever at least one unit could be placed.
    # With per-unit launching, the escalation condition is the strictly stronger thing that NOT ONE unit
    # could be bought; a tick that placed 3 of 18 is a market that works, just slowly, and escalating on it
    # would be the same cry-wolf in a new costume.
    #
    # ⚠ NAMED `price_blocks_every_unit`, NOT `price_is_binding` (2026-07-27). The old name asserted the same
    # English as `binding_gate: "price"` while meaning something strictly stronger, so a perfectly consistent
    # record — price binding on the 7 units it withheld, not binding on the fleet — read as the file
    # contradicting itself. Same value, same behaviour, a name that states the quantifier.
    # SUPERSEDED, retained for the record: the key `price_is_binding`.
    price_blocks_every_unit = (blocking is None) and n_place == 0 and n_held > 0
    doc["price_blocks_every_unit"] = price_blocks_every_unit
    _was = prev.get("price_blocks_every_unit", prev.get("price_is_binding"))
    doc["first_held_utc"] = (prev.get("first_held_utc") if (price_blocks_every_unit and _was)
                             else (_utcnow() if price_blocks_every_unit else None))

    held_h = 0.0
    if doc["first_held_utc"]:
        try:
            t0 = calendar.timegm(time.strptime(doc["first_held_utc"], "%Y-%m-%dT%H:%M:%SZ"))
            held_h = max(0.0, (time.time() - t0) / 3600.0)
        except (ValueError, TypeError):
            held_h = 0.0
    doc["held_hours"] = round(held_h, 2)

    if blocking:
        _lprint(f"[s1f] BINDING GATE: {blocking[0]} — {blocking[1]}. The price reading above is recorded but "
                f"is NOT what is stopping these units, so the price-escalation clock is NOT running.")

    # OUR OWN FILTER, ON THE RECORD, EVERY PASS — including the passes that place units. See
    # `annotate_exclusions`: the count is what turns "the market refused us" into "we refused the market".
    annotate_exclusions(doc, excluded)
    _write_market_hold(doc, s3, bucket)

    if price_blocks_every_unit and held_h >= MARKET_HOLD_ESCALATE_H:
        # The escalation. Not a decision the guard is allowed to make for him — a notification that one is
        # now needed. `::error::` also fails the job, which is what actually reaches a phone. Gated on
        # `price_blocks_every_unit` so it can only fire when every other gate is clear AND not one unit was
        # placeable: the 2026-07-27 false alarm escalated "held 9.9 h on a bad market" while the terminus
        # was unmet, i.e. during a window in which this gate was never what stopped anything.
        print(f"::error title=STEP1 FAN-OUT: NOT ONE UNIT PLACEABLE FOR {held_h:.1f} H::Every other gate is "
              f"clear and the $/ns guard still cannot place a SINGLE one of {n_withheld} unit(s) — for "
              f"{held_h:.1f} h (since {doc['first_held_utc']}). {why_none} The guard will NOT buy in on its "
              f"own: this needs a decision — wait longer, re-price the ladder against a changed market, or "
              f"authorise the higher spend. Snapshot: step1-fanout-market-hold.json.", flush=True)
        _lprint(f"[s1f] ESCALATED — price has been the BINDING constraint for {held_h:.1f} h "
                f"(> {MARKET_HOLD_ESCALATE_H:.0f} h) with zero units placeable. trimcrae's call now.")
        globals()["_MARKET_HOLD_ESCALATED"] = True
    return n_place


def object_store_preflight(bucket=None, prefix=None):
    """(ok, reason) — can the credential a RENTED HOST would be given actually read the staging prefix?

    Tested with `gpu_backend._object_store_env()` rather than with the CI process's own environment, and that
    distinction is the entire point: `_object_store_env` is the single place the forwarded credential is
    chosen (scoped `vast-leg-s3` when configured, else the broad CI key), so asking IT means this check can
    never drift from what the host receives. Testing `os.environ` instead would have passed happily on
    2026-07-27 while every rental crash-looped, because the RUNNER's key listed the same bucket fine minutes
    either side of the host's `InvalidAccessKeyId`.

    The probe mirrors the leg's own first command — the `$AWS s3 cp "s3://$BUCKET/$STAGE_PREFIX/" ...` in
    `_PREAMBLE` — as a `list_objects_v2` with `MaxKeys=1`, so a pass means the thing that actually failed now
    works, not merely that some S3 call succeeds. `KeyCount == 0` is a FAILURE: the credential authenticated
    but the staged tree is not there, and a leg would die on the `test -s` guard immediately after.

    PURE-ish: reads env + does one S3 GET. Never prints, logs or returns any part of a credential — the
    exposure incident this lane is already carrying began with a diagnostic that printed values it had not
    named (research/compute/credential-exposure-2026-07-27.md).
    """
    bucket = bucket or _require_bucket()
    prefix = (prefix or STAGE_PREFIX).strip("/")
    try:
        import boto3
        from gpu_backend import _object_store_env, object_store_cred_mode
    except Exception as e:  # noqa: BLE001
        return False, f"could not load the credential resolver: {type(e).__name__}: {e}"
    env = _object_store_env()
    mode = object_store_cred_mode()
    if not env.get("AWS_ACCESS_KEY_ID") or not env.get("AWS_SECRET_ACCESS_KEY"):
        return False, (f"no object-store credential would be forwarded at all (mode={mode}) — a host cannot "
                       f"read the staged inputs without one")
    try:
        cli = boto3.client(
            "s3",
            region_name=env.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_DEFAULT_REGION", "us-east-2"),
            aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
            aws_session_token=env.get("AWS_SESSION_TOKEN"),
        )
        r = cli.list_objects_v2(Bucket=bucket, Prefix=f"{prefix}/", MaxKeys=1)
    except Exception as e:  # noqa: BLE001
        # The error CODE is the actionable half and carries nothing secret; the message may echo a key id, so
        # only the code and the exception type are reported.
        code = ""
        try:
            code = e.response["Error"]["Code"]  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            code = type(e).__name__
        return False, (f"the {mode} credential was REJECTED by S3 ({code}) listing "
                       f"s3://{bucket}/{prefix}/ — this is the leg's first command, so every rental would "
                       f"crash-loop on it")
    if not r.get("KeyCount"):
        return False, (f"the {mode} credential works but s3://{bucket}/{prefix}/ is EMPTY — a leg would pass "
                       f"the copy and then die on its `test -s` staged-input guard")
    return True, f"the {mode} credential can read s3://{bucket}/{prefix}/ (the leg's first command)"


def _rented_usd_per_ns(handle):
    """(usd_per_ns, printable) for the offer a submit ACTUALLY took. None when the card is not benched.

    Priced off `dph_total` — the rate Vast bills, storage included — which is the same quantity
    `vast_cost_model.score_offer` feeds the gate, so the reported figure and the gate's are commensurable.
    It is deliberately NOT derived from the `dph≈`/`min_bid` quote: the rate forensics measured quotes as
    understating the true billed rate by 9.05 % / 12.94 % / 26.41 % (min/median/max) with NO constant offset,
    because the gap scales with each machine's own `storage_cost` — which varies ~4.5x across one board. A
    quote-derived multiple would make every unit look cheaper than it is.
    """
    import vast_cost_model as _vcm
    dph = handle.extra.get("dph")
    gpu = handle.extra.get("gpu_name") or handle.extra.get("gpu")
    nsh = _vcm.ns_per_hour(gpu) if gpu else None
    if not nsh or dph is None:
        return None, (f"$/ns UNKNOWN — {gpu or 'card'} is not in the throughput table, so this rental "
                      f"cannot be graded")
    upn = float(dph) / nsh
    basis = market_basis()
    ceiling = _cf.unit_usd_per_ns_ceiling()
    cell = f"${upn:.6f}/ns · {upn / basis:.2f}x basis"
    if upn > ceiling:
        cell += f"  ⛔ ABOVE THE ${ceiling:.6f}/ns CEILING THE GATE CLEARED — this must not happen"
    elif upn >= _cf.unit_rate_line_usd_per_ns():
        # ★ THE LINE IS THE ABSOLUTE RATE, NOT A TYPED MULTIPLE (CLAUDE.md §1, trimcrae 2026-07-27). This
        # read `upn / basis >= 1.5` — a multiple of a denominator that moved 22 % that same morning — so
        # after the re-anchoring it flagged everything from 1.50x upward while the approved line sat at
        # 1.92x. Same dollars per nanosecond, a much stricter rule than the one agreed.
        cell += f"  ⚠ DRIFT (≥ ${_cf.unit_rate_line_usd_per_ns():.6f}/ns)"
    return upn, cell


#: ★★ THE OPERATOR HOLD — the ONE lever that stands this lane down, whoever dispatches it.
#: Ported from `gcp_fanout_rep.OPERATOR_HOLD`, whose reasoning applies here verbatim and was written after
#: the GCP lane needed exactly this: **disabling a `schedule:` does NOT pause the lane.**
#: `step1-fanout-supervisor.yml` dispatches this workflow explicitly on its own tick, so a cron edit leaves
#: the lane placing and merely LOOKS like a pause. The hold therefore lives in the DECISION, not the trigger.
#:
#: ⚠ A COMMITTED ARTIFACT, deliberately, and not a code edit or a workflow-disable, so that (a) the reason
#: travels with it, (b) `git log` says who paused it and when, and (c) reap, collect and supervision keep
#: running — a paused lane must still tear down an idle host, or "paused" quietly becomes "billing
#: unwatched", which is this repository's most expensive recurring failure.
OPERATOR_HOLD = "step1-fanout-OPERATOR-HOLD.json"


def operator_hold(root=None):
    """The operator hold, or None. An UNREADABLE hold file HOLDS — the safe direction is not buying."""
    path = os.path.join(root or os.path.dirname(os.path.abspath(__file__)), OPERATOR_HOLD)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as e:  # noqa: BLE001
        return {"reason": f"the hold file exists but could not be parsed ({type(e).__name__}) — HOLDING, "
                          f"because an unreadable instruction to stop is not permission to spend"}
    return doc if isinstance(doc, dict) else {"reason": "hold file is not an object — HOLDING"}


def mode_launch():
    global _MARKET_GUARD_RAN
    bucket, s3 = _require_bucket(), _s3()

    # ⛔ THE OPERATOR HOLD OUTRANKS EVERYTHING BELOW, INCLUDING THE ESCALATED MARKET HOLD. Checked FIRST so a
    # stood-down lane says "a person paused this, for this reason" rather than reporting whatever it would
    # have said anyway — in a log the two look identical and mean opposite things. In particular it must
    # pre-empt `_MARKET_HOLD_ESCALATED`: "price has been the binding constraint for N h — trimcrae's call
    # now" is a REQUEST FOR A DECISION, and once the decision is made, continuing to ask is the alarm
    # fatigue this lane already paid for. A held lane is a correct, quiet outcome; it is not a failure.
    _hold = operator_hold()
    if _hold:
        record_no_placement(
            "operator_hold",
            f"⏸ STOOD DOWN BY OPERATOR — this lane will not rent a GPU until "
            f"{OPERATOR_HOLD} is deleted. Reason on record: {_hold.get('reason', '(none given)')}"
            + (f" · paused {_hold['paused_utc']}" if _hold.get("paused_utc") else "")
            + ". Banked work is untouched: the commit store is continuous, so a resume re-enters at the last "
              "COMMITTED checkpoint and nothing is lost by waiting.",
            s3=s3, bucket=bucket, key=None)
        _write_launch_readout()
        return 0

    key = os.environ.get("VAST_API_KEY")
    if not key:
        # Recorded before raising, like every other exit: a missing key is a REASON nothing was placed, and
        # an unrecorded reason is what made a two-hour outage look like a healthy quiet lane.
        record_no_placement("credential_hold", "VAST_API_KEY is not set in this environment — the board "
                                               "cannot be read and nothing can be rented",
                            s3=s3, bucket=bucket, key=None)
        raise SystemExit("[s1f] VAST_API_KEY required to launch")

    # ★★ THE PLACEMENT SWITCH LIVES HERE, NOT IN A WORKFLOW `if:` (2026-07-27, 2:31 PM ET). ★★
    #
    # THE INCIDENT, QUOTED FROM THE EVIDENCE. Between 12:44 PM and 2:31 PM ET, SEVEN autoscale ticks ran and
    # reported `success`; the fleet decayed 11 -> 5 while ten checkpointed units sat with no host, and
    # `step1-fanout-market-hold.json` never moved off 12:43 PM. The GitHub jobs API shows the cause on every
    # one of them, including the 2:09 PM SCHEDULE tick (run 30292476003):
    #     9  skipped  Gate on the fan-out unit tests (a broken unit list or cost model must never reach a GPU)
    #     10 skipped  Terminus-gated fan-out
    # while that same tick's own evidence step printed "✅ MET" for the terminus and
    # "OK — under the $0.006539/ns buy line (≈1.92× basis); a release would clear the price gate."
    # Nothing was wrong with the terminus, the price, the credential or the board. The LAUNCH STEP DID NOT RUN.
    #
    # THE MECHANISM. Both steps were guarded by `if: ${{ github.event.inputs.release_fanout != '0' }}`. A
    # `schedule:` event has NO `inputs` context, so that operand is `null`; GitHub Actions performs LOOSE
    # comparison and casts both sides to a number when the types differ, and `null` casts to `0`. The
    # condition is therefore `0 != 0` -> FALSE, and the step that spends money is skipped on exactly the
    # trigger that is supposed to be unattended. All three of the day's schedule ticks skipped it, 3 of 3;
    # the sibling expression `${{ github.event.inputs.fleet_branch || '...' }}` in the SAME run resolved
    # correctly to the fallback, which is the observation that discriminates: the inputs context was null and
    # `||` coped where `!=` did not.
    #
    # WHY THE REPAIR IS NOT "FIX THE EXPRESSION". A YAML `if:` decides in a language with implicit coercion,
    # leaves `skipped` as its only trace, and cannot write an artifact. The three states "held on price",
    # "nothing to place" and "placement switched off" all rendered as a green tick with no launch — which is
    # precisely why this ran for 1 h 47 m unnoticed. So the switch is READ here, as a string, with an
    # explicit default, and every outcome is NAMED and RECORDED by `record_no_placement`. The workflow's job
    # is now to hand the flag over, not to decide with it.
    _placement = (os.environ.get("FANOUT_PLACEMENT_ENABLED") or "1").strip()
    # The cost-model gate moved in here for the same reason: as a workflow `if:` it could only skip, and a
    # skip is invisible. Now a red cost model is a NAMED refusal in the artifact and still stops the renting.
    _cost_outcome = (os.environ.get("FANOUT_COST_MODEL_OUTCOME") or "success").strip()
    # ⚠ The launch step now runs under `always()` so the snapshot can never go stale — which means it also
    # runs when the progress check or the collect FAILED. Renting more hosts onto a fleet that was neither
    # measured nor reaped this tick is the wrong direction, so those outcomes gate placement too. The
    # snapshot is still written; only the buying is held.
    _upstream = {k: (os.environ.get(f"FANOUT_{k}_OUTCOME") or "success").strip()
                 for k in ("MEASURE", "COLLECT")}
    _upstream_bad = {k: v for k, v in _upstream.items() if v != "success"}

    # ★ `lane_units`, NOT `default_units` — the replicate axis has to be VISIBLE to placement or it does not
    # exist. `_pending` decides "pending" by the absence of a `result_key`, and `FANOUT_ONLY` filters the
    # PENDING set and hard-fails on an empty match, so a replicate missing from this list cannot be reached
    # by any lever: it is not held, it is invisible. With no replicate requested this is `default_units()`.
    units = lane_units()
    idx_of = {u["unit_id"]: i for i, u in enumerate(units)}
    _blocked = _load_blocked(s3, bucket)
    pending = _pending(s3, bucket, units, blocked=_blocked)
    # ★★ `done` USED TO BE THE MAP SIZE MINUS THE PENDING SET, WHICH COUNTED A BLOCK AS A FINISH
    # (2026-07-28). `_pending` drops finished units AND blocked ones, so the subtraction silently added the
    # permanently-excluded edge to the completion count: with nine ddG results and one block, the readout
    # said `done=10`. That is the exact failure CLAUDE.md §6 names — an edge that will never be computed
    # rendering as one that was — and it made the lane's own headline number unquotable, because "10 done"
    # and "9 results" were both in the same artifact. The three states are now counted separately and the
    # denominator that matters (`computable`) is derived, never typed.
    _done_ids = {u["unit_id"] for u in units if _exists(s3, bucket, result_key(u, RESULT_PREFIX))}
    done, n_blocked, _outstanding = counts(units, _done_ids, _blocked)
    computable = computable_units(units, _blocked)

    live = _live_instances(key)
    # ⚠ AN `exited` INSTANCE DOES NOT HOLD ITS UNIT'S SLOT. Vast teardown is two-layer: the container's EXIT
    # trap halts GPU billing key-free, but only CI can DESTROY the instance, so an exited box LINGERS in the
    # listing doing nothing. Counting it as occupying the unit would make every relaunch a silent no-op —
    # which is exactly what happened to the shakeout unit when it was preempted at 4:31 PM ET on 2026-07-26:
    # the container was gone, 260 committed iterations sat banked in S3, and the launcher would have reported
    # "nothing to submit" because the corpse still carried the label. This is the same lesson
    # vast_watchdog.ParalogueMdKind already encodes ("an `exited` container is NOT alive"); the fan-out
    # launcher simply did not have it yet.
    _TERMINAL = ("exited", "offline", "error")
    live_labels = {i.get("label") for i in live if (i.get("actual_status") or "") not in _TERMINAL}
    _dead = [i.get("label") for i in live if (i.get("actual_status") or "") in _TERMINAL]
    if _dead:
        _lprint(f"[s1f] {len(_dead)} instance(s) in a terminal state do NOT hold their unit's slot "
              f"(collect destroys them; their checkpoints are in S3 and a relaunch resumes): {_dead}")
    # a unit whose instance is already up is not re-submitted (idempotent top-up)
    todo = [u for u in pending if f"{LABEL_PREFIX}{idx_of[u['unit_id']]:02d}-{u['ligand_b']}"[:64]
            not in live_labels]

    # ★★ THE CONSECUTIVE-FAILURE BREAKER, WHICH THIS LANE REFERENCED AND NEVER CALLED (2026-07-29).
    # `_record_exclusion` below already points at `leg_failure_breaker` as the thing that "stops buying the
    # next host for this unit". It did not, here — nothing in this module called it — and
    # `cw_bio_primary_amide` fell straight through the gap: 25 rentals across 7 distinct card/driver
    # combinations, every one dying at the same `LocalEnergyMinimizer` call, because no code path anywhere
    # counted how many times we had already paid to watch it.
    #
    # ⚠ HELD IS NOT DROPPED, AND IT IS NOT BLOCKED EITHER. A held unit is printed with its count and its
    # reason, carried into the placement record, and re-armed by an explicit gesture once the cause is
    # fixed — the same shape as a price hold. CLAUDE.md §6 forbids the silent version of this.
    _baselines = _breaker_baselines(s3, bucket)
    _breaker_held = []
    _kept = []
    for u in todo:
        d = breaker_decision(s3, bucket, u, _baselines)
        if d.get("block"):
            _breaker_held.append((u, d))
            _lprint(f"[s1f] BREAKER HOLD, not renting {u['unit_id']}: {d['why']}")
        else:
            _kept.append(u)
    todo = _kept

    # ---- the two switches, each with a NAMED, RECORDED outcome ------------------------------------------
    # Both write the snapshot before returning, so the artifact's timestamp advances on every tick and can
    # only ever go stale by the tick itself not running. That is the whole repair.
    # ⚖ SELF-HEAL BEFORE READING. The classification rule is only half a fix while the entries it would have
    # refused are still sitting on the durable list from before it existed — and this lane's list was the one
    # the 2026-07-27 clear missed entirely (see the WAVE block above). Retiring is judged on each entry's OWN
    # recorded reason, is idempotent, and costs two S3 calls.
    retire_perishable_exclusions(s3, bucket)
    _excl_for_snapshot, _ = _load_excluded(s3, bucket)
    if _placement == "0":
        record_no_placement(
            "placement_disabled",
            f"FANOUT_PLACEMENT_ENABLED={_placement!r} — this tick was asked to measure, collect and reap "
            f"only. {len(todo)} unit(s) are pending with no live host and were NOT dropped; the next tick "
            f"with placement enabled sends them out.",
            s3=s3, bucket=bucket, key=key, n_withheld=len(todo), excluded=_excl_for_snapshot)
        _write_launch_readout()
        return
    if _upstream_bad:
        record_no_placement(
            "measurement_failed",
            f"upstream step outcome(s) {_upstream_bad!r} — the fleet was not measured and/or not reaped this "
            f"tick, so {len(todo)} pending unit(s) are held rather than rented onto an unmeasured fleet. "
            f"Nothing was dropped; the next healthy tick places them.",
            s3=s3, bucket=bucket, key=key, n_withheld=len(todo), excluded=_excl_for_snapshot)
        _write_launch_readout()
        return
    if _cost_outcome != "success":
        record_no_placement(
            "cost_model_red",
            f"the fan-out unit-list / cost-model tests came back {_cost_outcome!r} — a broken unit list or "
            f"cost model must never reach a GPU, so {len(todo)} pending unit(s) are held. Nothing was "
            f"dropped; fix the tests and the next tick places them.",
            s3=s3, bucket=bucket, key=key, n_withheld=len(todo), excluded=_excl_for_snapshot)
        print("::error title=STEP1 FAN-OUT: COST MODEL RED::the unit-list/cost-model tests failed, so no "
              "unit may be rented this tick. Snapshot: step1-fanout-market-hold.json", flush=True)
        _write_launch_readout()
        raise SystemExit(1)

    # ---- FANOUT_ONLY: launch a NAMED subset, not "the next N in map order" --------------------------------
    # THE SHAKEOUT RULE NEEDS THIS. 0 of 19 units of this lane has ever produced a ddG: sampling is proven
    # (three hosts at 95-99 % GPU on the real system in wave 1) but the TERMINUS — reduce both legs, write
    # ddg.json, upload it — is not. CLAUDE.md's litmus test says a congeneric map has no result that would
    # cancel the rest, so there is no SCIENTIFIC reason to serialise; but "a pipeline is unproven until you
    # have watched it reach its real success terminus at least once" still bites, and fanning 19 wide into an
    # unproven terminus risks paying 19x for zero results. So exactly ONE unit runs first, and it is chosen
    # DELIBERATELY (the most-advanced checkpoint, i.e. the one closest to the terminus, so the proof costs the
    # least wall-clock) rather than by map position. Without this flag "one unit" would mean unit 00.
    # Set by any gate below that NARROWS `todo` — (decision, why, n_withheld). Read by the empty-batch
    # readout, which otherwise re-derives a reason from slot arithmetic that was never the cause.
    _narrowed = None
    only = [t.strip() for t in (os.environ.get("FANOUT_ONLY") or "").split(",") if t.strip()]
    if only:
        matched = [u for u in todo if any(t in u["unit_id"] or t in u["ligand_b"] for t in only)]
        skipped = len(todo) - len(matched)
        _lprint(f"[s1f] FANOUT_ONLY={only!r} -> {len(matched)} of {len(todo)} pending units selected "
              f"({skipped} held back)")
        if not matched:
            raise SystemExit(f"[s1f] FANOUT_ONLY={only!r} matched no pending unit — refusing to launch "
                             f"something other than what was asked for")
        todo = matched

    # ---- the terminus gate --------------------------------------------------------------------------------
    # THE WHOLE POINT OF THE ONE-THEN-EIGHTEEN SHAPE, expressed as a machine condition rather than as an
    # agent remembering to come back. `FANOUT_REQUIRE_PROVEN_TERMINUS=1` refuses to submit until at least one
    # unit's ddg.json exists in S3 — i.e. until reduce->commit->upload has actually been observed once.
    #
    # WHY IT IS A GATE AND NOT A DECISION I MAKE LATER. A gate can be put on a cron, so the fan-out fires the
    # MINUTE the terminus is proven instead of the next time somebody looks. That is strictly more parallel
    # than waiting for a human or an agent, and strictly safer than launching early, which is the combination
    # the shakeout rule is actually asking for. Serialising costs wall-clock and buys nothing else.
    #
    # ⚠⚠ THE GATE HOLDS BACK THE FAN-OUT. IT MUST NEVER BLOCK THE SHAKEOUT UNIT'S OWN RESUME.
    # As first written it returned outright whenever no ddg.json existed — which is a DEADLOCK, and not a
    # theoretical one: the shakeout unit was preempted at 4:31 PM ET on 2026-07-26 with 260 iterations banked,
    # and a gate that refuses to launch anything until a ddg.json exists would never have restarted the one
    # unit whose entire job is to produce that ddg.json. The cron would have ticked all night launching
    # nothing. So while the terminus is unproven the gate NARROWS to the shakeout unit instead of returning:
    # the fifteen cold units stay held, and the unit that is already paid for keeps going.
    # ★ COMPUTED UNCONDITIONALLY, not inside the branch below, and at ZERO extra S3 cost — `done` already
    # counts the units whose ddg.json exists, because `pending` was built from exactly that test. The price
    # gate needs it as an INPUT (see `market_gate`'s `gates`): the terminus is enforced only under
    # FANOUT_REQUIRE_PROVEN_TERMINUS=1, which the autoscale tick sets and a manual `fanout_mode=launch`
    # dispatch does not — and the two share one hold clock in S3, so on 2026-07-27 a manual dispatch that
    # ignored the terminus escalated "held 9.9 h on a bad market" for a window in which price was never what
    # stopped anything. Passing it in makes the escalation independent of which entry point wrote the clock.
    terminus_proven = done > 0
    _terminus_why = ("at least one unit has a production ddg.json" if terminus_proven else
                     "no unit has a ddg.json — reduce/commit/upload has never been observed on this lane, so "
                     "these units cannot launch at ANY price")

    if os.environ.get("FANOUT_REQUIRE_PROVEN_TERMINUS") == "1":
        proven = [u["unit_id"] for u in units if _exists(s3, bucket, result_key(u, RESULT_PREFIX))]
        if proven:
            _lprint(f"[s1f] terminus PROVEN by {len(proven)} unit(s) ({proven[0]}) — fan-out released")
        else:
            shakeout = (os.environ.get("FANOUT_SHAKEOUT_UNIT") or "").strip()
            if not shakeout:
                _lprint("[s1f] TERMINUS NOT PROVEN and no FANOUT_SHAKEOUT_UNIT named — holding everything. "
                      "Set FANOUT_SHAKEOUT_UNIT so the gate can keep the shakeout unit alive while it holds "
                      "the other units back.")
                record_no_placement("terminus_hold", _terminus_why + ", and no FANOUT_SHAKEOUT_UNIT is named",
                                    s3=s3, bucket=bucket, key=key, n_withheld=len(todo),
                                    excluded=_excl_for_snapshot)
                _write_launch_readout()
                return
            keep = [u for u in todo if shakeout in u["unit_id"] or shakeout in u["ligand_b"]]
            _lprint(f"[s1f] TERMINUS NOT PROVEN — no unit has a ddg.json, so reduce/commit/upload has never "
                  f"been observed on this lane. Holding {len(todo) - len(keep)} unit(s); RESUMING the "
                  f"shakeout unit ({shakeout}) if it needs it: {len(keep)} to submit.")
            # ★★ REMEMBER *WHY* `todo` SHRANK, or the empty-batch readout below tells a lie (2026-07-27,
            # found while ramping). The narrowing here can empty `todo` outright — when the shakeout unit
            # already has a live host, `keep` is `[]` — and the empty-batch branch then had no way to know
            # that, so it fell through to its last `else` and recorded `fleet_at_width`, "all N pending
            # unit(s) already have a live instance", with `n_withheld=0`. Every clause of that is false: the
            # units are held by the TERMINUS, most of them have no host, and they are very much being
            # withheld. That is the same defect class as the seven green ticks — a tick that places nothing
            # and misnames the reason is only marginally better than one that says nothing at all, because
            # the wrong name sends the next reader to the wrong gate. So the reason travels with the
            # narrowing instead of being re-guessed downstream.
            _narrowed = ("terminus_hold",
                         _terminus_why + f" — the fan-out is narrowed to the shakeout unit "
                                         f"({shakeout}), which needs no new host this tick",
                         len(todo) - len(keep))
            todo = keep

    # Slots count only instances actually DOING something, for the same reason live_labels does: a fleet of
    # exited corpses would otherwise report zero free slots and silently launch nothing.
    _busy = [i for i in live if (i.get("actual_status") or "") not in _TERMINAL]
    WIDTH = fanout_width()
    slots = max(0, WIDTH - len(_busy))
    batch = todo[:slots]

    lo, hi = cost_estimate(len(batch))
    # The DENOMINATOR is the computable set, and the blocked edges are named on the same line rather than
    # folded into `done`. "9 of 18 computable, 1 permanently excluded" and "10 of 19 done" describe the
    # same lane and only one of them can be quoted in a paper.
    _blk_named = ", ".join(sorted(k.split("__")[1] for k in _blocked)) if _blocked else "none"
    _lprint(f"[s1f] map_edges={len(units)} computable={len(computable)} done={done} "
            f"blocked={n_blocked} ({_blk_named}) pending={len(pending)} live={len(live)} "
            f"free_slots={slots} -> submitting {len(batch)}")
    _lprint(f"[s1f] cost of THIS submission ({len(batch)} units): plan ${cost_plan(len(batch))} "
          f"(band ${lo}-{hi}) | whole remaining tranche ({len(pending)} units): "
          f"plan ${cost_plan(len(pending))} (band ${'-'.join(str(x) for x in cost_estimate(len(pending)))})")
    _lprint(f"[s1f] wave shape: {json.dumps(wave_plan(len(pending), WIDTH))}")
    for u in batch:
        _lprint(f"[s1f]   queue {u['unit_id']}  ({u['ligand_a']} -> {u['ligand_b']}, {u['edge_class']})")
    if not batch:
        _lprint("[s1f] nothing to submit (fleet already at width, or all units done)")
        # ⚠ THESE ARE DIFFERENT FACTS AND THE OLD ONE-LINER CONFLATED THEM. "All 19 edges are finished"
        # and "every free slot is taken" are opposite states of the lane — one means STOP, the other means
        # KEEP WATCHING — and for 1 h 47 m the readout said neither because it never got here at all.
        _n_withheld = 0
        if _narrowed:
            # An EARLIER gate emptied `todo`; it knows why and this branch does not. Checked FIRST, because
            # every test below is about slots and finished units and would answer confidently about the
            # wrong question. `n_withheld` is the count that gate held, not 0 — a held unit that reports
            # zero withheld is invisible in exactly the readout built to make holds visible.
            _dec, _why, _n_withheld = _narrowed
        elif _breaker_held and not [u for u in pending
                                    if u["unit_id"] not in {h["unit_id"] for h, _ in _breaker_held}
                                    and f"{LABEL_PREFIX}{idx_of[u['unit_id']]:02d}-{u['ligand_b']}"[:64]
                                    not in live_labels]:
            # Checked BEFORE `nothing_pending`, because a breaker hold is emphatically not "nothing left to
            # place" — it is a lane declining to buy, which is a different fact with a different remedy.
            _dec = "breaker_hold"
            _why = ("; ".join(f"{h['unit_id']}: {d['n_attempts']} attempt(s) on separate hosts "
                              f"(threshold {d['threshold']})" for h, d in _breaker_held)
                    + ". Fix the cause, then re-arm with FANOUT_UNBLOCK=1.")
            _n_withheld = len(_breaker_held)
        elif not pending:
            _dec, _why = "nothing_pending", ("every unit has a ddg.json in S3 or is on the blocked list — "
                                             "there is nothing left for this lane to place")
        elif slots <= 0:
            _dec, _why = "fleet_at_width", (f"{len(_busy)} live instance(s) against a DERIVED width of "
                                            f"{WIDTH} (fanout_width(): the map size, so the cap never binds "
                                            f"below what the lane may place) — no free slot. "
                                            f"{len(pending)} unit(s) still pending.")
        else:
            _dec, _why = "fleet_at_width", (f"all {len(pending)} pending unit(s) already have a live "
                                            f"instance; {slots} slot(s) free but nothing to put in them")
        record_no_placement(_dec, _why, s3=s3, bucket=bucket, key=key,
                            n_withheld=_n_withheld, excluded=_excl_for_snapshot)
        _write_launch_readout()
        return

    # ⛔ CREDENTIAL PRE-FLIGHT, BEFORE THE PRICE GATE — a rental that cannot read S3 is worthless at ANY
    # price, so this is the cheaper question and it is asked first.
    #
    # MEASURED, 2026-07-27 (this is not a hypothetical). Instance 45996071 was rented at 7:02 AM ET, resumed
    # the shakeout unit's complex leg to production@2000 and its solvent leg to production@200 — then from
    # ~7:50 AM ET every container restart died on the FIRST line of real work, the staging copy in
    # `_PREAMBLE`:
    #     fatal error: An error occurred (InvalidAccessKeyId) when calling the ListObjectsV2 operation:
    #     The AWS Access Key Id you provided does not exist in our records.
    #     Killed
    # boot -> openfe import -> nvidia-smi -> InvalidAccessKeyId -> Killed, on a ~15-60 s loop, for over an
    # hour, at $0.2497/hr on a 4090 with 0 % GPU utilisation and not one further committed iteration.
    #
    # WHY THE EXISTING GUARDS ALL MISSED IT, which is the reason this needs its own check rather than a
    # tweak to one of them:
    #   * the $/ns gate prices the BOARD. The host was cheap and healthy; the credential was the broken part.
    #   * the starved-host exclusion keys on realised throughput, which needs commits to compare — a host
    #     that never gets past `s3 cp` produces none, so it is invisible to the ranking (the same blind spot
    #     `exclude_machine_ids` exists for).
    #   * `phase.txt` still said `leg-solvent-running`, because the phase marker is only ever written FORWARD
    #     and nothing rewrites it when the container dies. The committed-iteration census is what caught it
    #     — flat across three consecutive ticks with an idle GPU (CLAUDE.md §4).
    #   * blacklisting the machine would have been the WRONG repair: the host is fine, and the next host
    #     would have crash-looped identically. The failure is not per-host, so a per-host remedy just pays
    #     the same bill somewhere else.
    #
    # WHAT THIS DOES AND DELIBERATELY DOES NOT DO. It asks the ONE question that decides whether a rental can
    # work: using EXACTLY the credential `gpu_backend._object_store_env()` would forward — scoped or
    # inherited, whichever is configured, so this cannot drift from what the host actually receives — can we
    # list the staging prefix the leg's first command reads? It does not inspect, name, print, repair or
    # rotate any credential; diagnosing an IAM key is not the launcher's job. It only refuses to BUY into one
    # that does not work, and says so with the error S3 returned.
    #
    # It HOLDS rather than fails: same discipline as the market gate, and for the same reason — a hold is
    # recoverable and visible, nothing is dropped, the commit store is untouched, and the next tick re-checks
    # and launches by itself the moment the credential works again.
    _preflight_ok, _preflight_why = True, "skipped (FANOUT_SKIP_CRED_PREFLIGHT=1)"
    if os.environ.get("FANOUT_SKIP_CRED_PREFLIGHT") != "1":
        ok, why = object_store_preflight()
        _preflight_ok, _preflight_why = ok, why
        _lprint(f"[s1f] CREDENTIAL PRE-FLIGHT: {'✅ CLEAR' if ok else '⛔ HELD'} — {why}")
        if not ok:
            _lprint(f"[s1f] ⛔ LAUNCH HELD ({len(batch)} unit(s)) — the object-store credential this rental "
                    f"would be given cannot read s3://{_require_bucket()}/{STAGE_PREFIX}/, which is the "
                    f"first thing every leg does. Renting would buy a container that boots, fails that copy "
                    f"and is Killed, on a loop, while billing. Nothing was rented and no unit was dropped; "
                    f"the checkpoints are untouched in S3 and the next tick re-checks automatically.")
            record_no_placement("credential_hold", why, s3=s3, bucket=bucket, key=key,
                                n_withheld=len(batch), excluded=_excl_for_snapshot)
            _write_launch_readout()
            return

    # ⛔⛔ THE CUMULATIVE SPEND CAP — THE GATE THIS LANE DID NOT HAVE (2026-07-27, added with the ramp).
    #
    # THE GAP, STATED PLAINLY. Every other guard in this function asks a question about ONE rental: is this
    # rate acceptable, can this host read S3, is this unit already running. Not one of them asks whether the
    # lane has spent the money it was authorised. Realised spend was measured and printed on every tick and
    # nothing ever refused on it. That was survivable while the fleet was small and hand-placed. It stopped
    # being survivable the moment placement became self-replenishing: the tick now re-rents to target width
    # on every pass, forever, and a per-unit rate line is passed *individually* by every cheap host. Fifteen
    # hosts each comfortably under $0.006539/ns is exactly the shape that drains a budget while every row in
    # the readout reads green — nothing was wrong with any single purchase, and the total was nobody's job.
    #
    # WHY IT SITS HERE: after the credential pre-flight, before the price gate. It costs no board read, so
    # it is the cheapest question; and it is a different QUESTION from price, not a stricter version of it.
    # Price asks "is this a rate we will pay at all"; this asks "is there authorised money left". Conflating
    # them is what CLAUDE.md §1 warns about — a refusal must NAME which ceiling it hit, because the remedies
    # are opposite: a price hold clears by itself when the board improves, and this one never does.
    #
    # ⚠ IT HOLDS. IT DOES NOT DESTROY. The gate acts at the MOMENT OF RENTING and has no reach over a live
    # host — the same boundary `relaunch_market_gate` keeps. Work already executing keeps executing and
    # keeps banking checkpoints; what stops is BUYING MORE. Killing running legs to save money would throw
    # away GPU-hours already paid for, which makes the overspend worse, not better.
    #
    # ⚠ AND IT IS SURFACED, NOT IDLED. §6 names a silent hold as worse than the problem, and a cap that
    # cannot be cleared by waiting is the case where that matters most: unlike a thin market, this will look
    # identical tomorrow. So when the cap binds with units still pending it raises a hard `::error::`, which
    # fails the job and fires GitHub's own notification — the same session-independent path the market
    # escalation uses. That is a decision for trimcrae: re-price the tranche, authorise more, or stop.
    #
    # ⚠ AND IT READS ITS LEDGER STRICTLY. `_load_ledger` swallows every S3 error into an empty doc, which
    # for a spend cap means an outage reports realised $0 and full headroom — a fabricated all-clear that
    # opens the gate exactly when evidence is missing. `load_ledger_strict` raises instead, and the raise
    # HOLDS. Same rule as the unreadable board.
    # `n_units=len(units)` is the LANE (map + any requested replicates), not the map — the ceiling is
    # `market_ceiling_usd(n)`, i.e. the authorised band top for n units of work, so it must count the work
    # actually authorised. With no replicate requested the two are the same number. Advisory either way:
    # the branch below warns and does not halt.
    try:
        _cap_realised, _cap_ceiling, _cap_headroom, _cap_breached, _cap_detail = spend_cap_state(
            load_ledger_strict(s3, bucket), live_ids=[i.get("id") for i in live], n_units=len(units))
    except Exception as e:  # noqa: BLE001
        _lprint(f"[s1f] ⛔ SPEND CAP HAS NO EVIDENCE ({type(e).__name__}: {e}) — HOLDING {len(batch)} "
                f"unit(s). An unreadable ledger is not a zero one. Nothing rented, nothing dropped, "
                f"nothing running touched; the next tick re-reads.")
        record_no_placement("spend_cap_hold",
                            f"the rental ledger could not be read ({type(e).__name__}: {str(e)[:200]}) — "
                            f"realised spend is unknown, so the cap fails CLOSED and {len(batch)} unit(s) "
                            f"are held rather than rented against evidence we do not have",
                            s3=s3, bucket=bucket, key=key, n_withheld=len(batch),
                            excluded=_excl_for_snapshot)
        _write_launch_readout()
        return
    _lprint(f"[s1f] SPEND CAP: realised ${_cap_realised} against a DERIVED ceiling of ${_cap_ceiling} "
            f"(market_ceiling_usd({_cap_detail['n_units_authorised']}) — the authorised band top, "
            f"regenerated from the cost model, never typed) -> ${_cap_headroom} headroom. "
            f"{_cap_detail['n_rentals']} rental(s) counted, of which "
            f"{_cap_detail['n_accruing_unreconciled']} are accruing wall-clock because no collect has "
            f"reconciled them yet (a cap that cannot see those reads green while the lane is over).")
    # ★★ THE TRANCHE FIGURE IS AN ESTIMATE, NOT A HARD CAP — IT WARNS, IT NO LONGER HALTS
    # (trimcrae, 2026-07-29: *"The $75 ceiling was always an estimate, not a hard cap. Don't worry about
    # that."*). This branch used to HOLD every pending unit on breach and demand a human decision. It does
    # not any more.
    #
    # ⚠ WHAT THIS DOES **NOT** LOOSEN, because the distinction is the whole point. The gates that refuse a
    # PURCHASE are untouched and still hard: the `$/ns` buy line (`inflight_usd_per_ns.APPROVED_USD_PER_NS`,
    # CLAUDE.md §1) and the per-launch band ceiling (`market_ceiling_usd`) both still REFUSE below. What is
    # now advisory is only the CUMULATIVE tranche total — a planning estimate for how much the whole rung was
    # expected to cost, which was never a spend authorisation.
    #
    # ⚠ AND THE HAZARD THIS BRANCH WAS BUILT FOR IS REAL, so it is still MEASURED and still LOUD rather than
    # deleted. Quoting its own docstring: *"Fifteen hosts each comfortably under the line is precisely the
    # shape that drains a budget while every row reads green — the rate line answers 'is this a rate we will
    # pay?', and nothing was answering 'have we now spent the money that was authorised?'"* That question is
    # still answered on every tick and still recorded; the answer simply no longer stops the lane.
    if _cap_breached:
        _lprint(f"[s1f] ⚠ OVER THE TRANCHE ESTIMATE — realised ${_cap_realised} >= ${_cap_ceiling} "
                f"(${abs(_cap_headroom)} over). CONTINUING: this figure is a planning estimate, not a spend "
                f"authorisation, and it does not gate placement. Every unit below is still priced against "
                f"the $/ns buy line and the per-launch ceiling, either of which will still refuse.")
        record_no_placement(
            "over_tranche_estimate_advisory",
            f"realised cumulative spend ${_cap_realised} is past the derived tranche estimate "
            f"${_cap_ceiling} for {_cap_detail['n_units_authorised']} units. ADVISORY ONLY — placement "
            f"continued; the per-purchase rate and band gates are unchanged and still binding.",
            s3=s3, bucket=bucket, key=key, n_withheld=0, excluded=_excl_for_snapshot)
        if pending:
            print(f"::warning title=STEP1 FAN-OUT: OVER THE TRANCHE ESTIMATE::realised ${_cap_realised} "
                  f"against a derived tranche estimate of ${_cap_ceiling}, {len(pending)} unit(s) pending. "
                  f"NOT a hold — the estimate does not gate placement (trimcrae, 2026-07-29). The $/ns buy "
                  f"line and the per-launch ceiling still refuse independently.", flush=True)

    # ⛔ THE $/ns MARKET GUARD (CLAUDE.md §6). EVERY launch must clear a price gate — fleet or single unit.
    #
    # Placed here, AFTER the batch is known and BEFORE `FANOUT_CONFIRM`, for two reasons. It needs the batch
    # size to know what it is pricing; and putting it before the confirm check means a DRY run exercises the
    # guard and prints its snapshot without renting anything, so the readout can be inspected on demand.
    #
    # ★★ WHY `len(batch) > 1` IS NO LONGER THE TEST (trimcrae, 2026-07-27: *"Why are there so many high $/ns
    # rows that are flagged but you're still paying for them?"*). The rule's original last line exempted "a
    # single unit already running", and this branch was where that exemption was cashed — so the shakeout
    # unit's resume passed through unpriced every time spot churn killed its host, and it was running at
    # **1.76x the ladder basis with `⚠ DRIFT` on the board** while the eighteen-edge fan-out at 2.05x was
    # correctly refused. The exemption was cut on the wrong axis: a RESUME ONTO A NEW HOST IS A NEW PURCHASE.
    # The right axis is "would waiting lose work?", and for a checkpointed unit it does not — the host is
    # already gone and the commit store is a durable S3 object. So both paths are gated, with the ceiling each
    # one deserves:
    #   * a FLEET buys a whole tranche at once, so it is measured against that tranche's authorised DOLLAR
    #     band (`market_hold` -> `congeneric_fanout.market_ceiling_usd`);
    #   * a SINGLE HOST re-enters a leg at an unknown fraction of its work, so a dollar projection would be
    #     the full unit's cost and meaningless. It is measured against the RATE instead — the drift line the
    #     board already prints (`relaunch_market_gate`, CLAUDE.md §1's 1.5x).
    _excluded_for_guard, _ = _load_excluded(s3, bucket)
    if os.environ.get("FANOUT_MARKET_OVERRIDE") == "1":
        _lprint("[s1f] ⚠ FANOUT_MARKET_OVERRIDE=1 — the $/ns guard is BYPASSED for this launch. That is a "
                "deliberate, recorded choice to spend outside the rung's authorised band.")
        _MARKET_GUARD_RAN = True
    elif len(batch) > 1:
        # PER-UNIT PLACEMENT (trimcrae, 2026-07-27): the gate returns HOW MANY units the board can take at a
        # rate inside the rung's authorisation, not an all-or-nothing verdict on a fleet mean. The batch is
        # truncated to that count; the remainder is not recorded anywhere as "dropped" because it does not
        # need to be — `pending` is recomputed from S3 on every tick, so a held unit is simply pending again
        # next tick and goes out the moment an offer clears for it.
        #
        # `gates` is what makes the price-escalation honest: the terminus is passed in so a hold caused by an
        # unmet terminus can never be reported, or escalated, as a hold caused by price.
        _n_allowed = market_gate(len(batch), bucket, s3, key, _excluded_for_guard,
                                 gates=(("terminus", terminus_proven, _terminus_why),
                                        ("credential pre-flight", _preflight_ok, _preflight_why)))
        batch = batch[:_n_allowed]
        if not batch:
            _lprint("[s1f] nothing rented this tick. No unit was dropped; the next tick re-prices.")
            _write_launch_readout()
            return
    else:
        import relaunch_market_gate as rmg
        _held, _gdoc = rmg.gate("step1_fanout", batch[0]["unit_id"], FANOUT_RES, key=key,
                                excluded=_excluded_for_guard, s3=s3, state_bucket=bucket,
                                state_prefix=RESULT_PREFIX)
        _MARKET_GUARD_RAN = True
        for _ln in (f"[s1f] SINGLE-HOST $/ns GATE: {'⛔ HELD' if _held else '✅ CLEAR'} — {_gdoc['reason']}",
                    f"[s1f]   board={json.dumps(_gdoc.get('board_depth'))} "
                    f"priced={json.dumps(_gdoc.get('offers_priced'))}"):
            _LAUNCH_LOG.append(_ln)
        if _held:
            _lprint("[s1f] Nothing was rented and no unit was dropped; the checkpoint is untouched in S3 and "
                    "the next scheduled tick re-checks.")
            # The single-host gate has its own artifact (`relaunch-market-hold.json`), but a reader watching
            # the fan-out watches THIS file — and if only the sibling moves, this one goes stale and once
            # again means nothing legible. Both are refreshed.
            record_no_placement("price_hold", f"single-host gate: {_gdoc['reason']}", s3=s3, bucket=bucket,
                                key=key, n_withheld=1, excluded=_excluded_for_guard)
            if _gdoc.get("escalated"):
                # A ceiling nobody can clear must become trimcrae's decision, not an idle night. Reuse the
                # lane's existing escalation flag rather than inventing a second exit path.
                globals()["_MARKET_HOLD_ESCALATED"] = True
            _write_launch_readout()
            return

    # BELT, not braces. If a future edit ever routes a batch past the block above, this refuses rather than
    # renting: by CLAUDE.md §6 a rental that has not consulted the market is a bug, and the safe failure is
    # to hold. Widened from `len(batch) > 1` with the exemption it was protecting.
    if batch and not _MARKET_GUARD_RAN:
        _lprint(f"[s1f] ⛔ LAUNCH HELD ({len(batch)} unit(s)) — the $/ns market guard did not run. "
                f"Refusing to rent what was never priced.")
        record_no_placement("price_hold", "the $/ns market guard did not run at all — refusing to rent what "
                                          "was never priced (belt guard)",
                            s3=s3, bucket=bucket, key=key, n_withheld=len(batch),
                            excluded=_excluded_for_guard)
        _write_launch_readout()
        return

    if os.environ.get("FANOUT_CONFIRM") != "1":
        _lprint("[s1f] DRY — set FANOUT_CONFIRM=1 to actually rent instances")
        # ⚠ OVERWRITE the gate's `decision: placed`. The gate ran and cleared these units, but a dry run
        # rents nothing — leaving "placed" in the artifact would report a purchase that never happened.
        record_no_placement("placement_disabled",
                            f"FANOUT_CONFIRM is not 1 — dry run. The $/ns gate cleared {len(batch)} unit(s) "
                            f"but nothing was rented.",
                            s3=s3, bucket=bucket, key=key, n_withheld=len(batch),
                            excluded=_excluded_for_guard)
        _write_launch_readout()
        return

    # Machines this lane has already learned are bad — a capacity refusal, or a sustained shortfall against
    # the card constant the ranking assumes. Read from S3 so a launch in one CI run inherits what a monitor in
    # a different CI run discovered, with no agent awake in between.
    excluded, _ = _load_excluded(s3, bucket)
    if excluded:
        _lprint(f"[s1f] excluding {len(excluded)} machine(s) from offer selection: {excluded}")

    backend, handles = get_backend("vast"), []
    _ledger = _load_ledger(s3, bucket)
    # Machines used by THIS wave are also excluded as we go, so an 18-wide fan-out lands on 18 distinct hosts
    # rather than stacking on the single cheapest one and contending for its GPU.
    #
    # ★★ AND MACHINES THIS LANE IS **ALREADY ON** ARE SEEDED IN — THE HALF THE WAVE-LOCAL SET MISSED
    #    (2026-07-27, found adjudicating the ramp's 10-unit placement).
    #
    # THE DEFECT, EXACTLY. `used_machines` started as a copy of the EXCLUSION set and grew only from THIS
    # process's own submissions, so it made a single wave land on distinct hosts and said nothing about the
    # hosts the lane was already renting. The ramp replaced one hand-placed unit per tick with a
    # self-replenishing tick that places to width, so waves now arrive minutes apart — 10 units went out in
    # two waves 4 minutes apart at 2:58 and 3:02 PM ET. Wave 2 began with a `used_machines` that had
    # forgotten every host wave 1 had just rented, and the board it read was substantially the same board,
    # with the same cheapest offers ranked first. Two units on one machine contend for one GPU; worse, when
    # that machine is bad it takes every unit on it down TOGETHER, which is the shape of a cohort of
    # simultaneous never-starts.
    #
    # WHY THE BOARD CACHE MAKES THIS SHARPER, NOT SAFER: within a wave the cache serves one snapshot to every
    # unit, so the ranking is identical for all of them and ONLY `exclude_machine_ids` separates them. That
    # is correct and tested — but it means the ordering is now deterministic across a wave AND across the
    # next wave taken within the TTL, so a forgetful seed does not merely risk a collision, it makes the same
    # top-ranked machine the first choice again.
    #
    # ⚠ THIS EXCLUDES NOTHING PERMANENTLY AND CONDEMNS NOTHING. These ids are not written to the exclusion
    # set — a machine we are happily running on is a GOOD machine, and it becomes selectable again the moment
    # its instance goes away. It is a within-fleet distinctness rule, not a verdict.
    used_machines = set(excluded)
    # ⚠⚠ DO NOT "FIX" THIS TO SKIP TERMINAL INSTANCES. IT WAS TRIED, ON EVIDENCE, AND THE EVIDENCE WAS
    #    WRONG (2026-07-27, 6:32 -> 6:53 PM ET). The tempting argument is that this seed contradicts
    #    `live_labels` a few hundred lines above, which deliberately does NOT let an `exited` instance hold
    #    its unit's slot — the 6:32 PM readout printed "3 instance(s) in a terminal state do NOT hold their
    #    unit's slot [s1f-01, s1f-03, s1f-04]" and then avoided their machines 43159/50143/28904 anyway.
    #    That looks exactly like 6c996cca ("the gate counted corpses as hosts"), and it is not.
    #
    #    WHAT THE MEASUREMENT SHOWED. All three of those "corpses" were `running` again 21 minutes later, at
    #    ages 114/112/45 min — and the committed-iteration census proves they never stopped WORKING: over
    #    that same window `cw_ev_5oh` advanced from warmup@380 through a phase transition to production@40,
    #    and `cw_ev_5alkyne` added 80 production iterations. A Vast instance reading `exited` is routinely a
    #    TRANSIENT status, not a dead container, which is precisely why the reaper below refuses to destroy
    #    on a single observation and demands two consecutive terminal ticks.
    #
    #    SO THE TWO RULES ARE ASKING DIFFERENT QUESTIONS AND ARE BOTH RIGHT:
    #      * SLOT      — "should I re-submit this unit?"  Being wrong is CHEAP: the work is checkpointed in
    #                    S3, re-submission is idempotent, and a needless relaunch costs one rental.
    #      * DISTINCT  — "is this machine's GPU free?"     Being wrong is EXPENSIVE: measured today, 0 of 7
    #                    double-booked instances ever started, against 8 of 10 single-booked ones — and here
    #                    the unit we would double-book onto is OUR OWN still-advancing leg.
    #    The asymmetry is the whole point. A machine is free when its instance LEAVES THE LISTING (CI has
    #    destroyed it), not when it briefly reports a terminal status.
    _already_on = {str(i.get("machine_id")) for i in live if i.get("machine_id") is not None}
    if _already_on:
        used_machines |= _already_on
        _lprint(f"[s1f] host distinctness: also avoiding {len(_already_on)} machine(s) this lane is ALREADY "
                f"renting ({sorted(_already_on)}) — a second unit on a machine we already hold contends for "
                f"one GPU, and shares that machine's fate if it is bad. A TERMINAL status does not free a "
                f"machine: `exited` is routinely transient and the leg is often still advancing.")
    # ★★ ONE BOARD READ FOR THE WHOLE WAVE — the change that makes the ramp raise concurrency and LOWER API
    # pressure at the same time (2026-07-27). Rationale and the safety argument: `gpu_backend
    # .board_read_cache`. In short, `submit` reads `/search/asks/` once per unit and
    # `_vast_ondemand_base_by_machine` reads it again, so placement cost 2 calls per unit — 37 in a burst at
    # this lane's full width, against a shared key that already answered an nginx HTML 403 to a FOUR-unit
    # launch today and rented 0/4. The per-unit exclusions that make the wave land on distinct hosts are
    # applied client-side, so every one of those reads was fetching identical rows.
    #
    # THE TTL IS DERIVED FROM THE MEASURED SUBMIT RATE, not picked. A submit takes ~37 s (timed from the
    # completed step records of runs 30296004080 and 30296390447 — see the ledger note below), so at full
    # width a wave spans ~11 min. A 180 s snapshot therefore expires ~4 times across it: the wave costs
    # ~4 board reads instead of ~36, and no unit is ever placed against a board older than 3 minutes. Both
    # halves matter — an unbounded cache would rent the whole fleet against one stale snapshot, and no cache
    # throttles the key exactly when the fleet gets wide.
    _board_ttl = float(os.environ.get("FANOUT_BOARD_CACHE_TTL_S", "180"))
    # ExitStack rather than a `with` block only so the loop below keeps its indentation and this diff stays
    # readable next to the other lane's edits in the same function; `close()` at the end of the wave does
    # exactly what leaving the block would. The cache is process-local and TTL-bounded, so even the path
    # where an exception escapes the loop cannot leak it past this process.
    _board_stack = contextlib.ExitStack()
    _board_stats = _board_stack.enter_context(board_read_cache(ttl_s=_board_ttl))
    _submit_starved = []          # units whose submit died on OUR filter, not on the market — see below
    for u in batch:
        spec = build_jobspec(u, os.environ.get("GIT_BRANCH", "main"), bucket, idx_of[u["unit_id"]],
                             exclude_machine_ids=used_machines)
        try:
            h = backend.submit(spec)
        except Exception as e:  # noqa: BLE001 — one host shortage must not abort the wave
            # Same `flush=True`-to-`_lprint` defect as the submit-success line below, and worse here: this
            # handler's entire job is to keep the wave going through a Vast capacity refusal
            # ({"success": false, "error": "resources_unavailable"}), which CLAUDE.md records as routine.
            # Raising TypeError from inside the except block turned "skip this host, try the next" into
            # "abort the whole wave", on the most-expected failure this launcher has.
            # ★ NAME WHICH SHORTAGE IT WAS (2026-07-27). "no rentable verified offer" is emitted both when
            # the MARKET has nothing and when OUR OWN filters have eaten everything, and the two have
            # opposite remedies — wait for the board vs. withdraw a wrong exclusion. Measured that evening:
            # 38 machines excluded against a 152-offer board lost 4 of 5 authorised placements, and every
            # one of them printed as if the market had refused us. `vast_machine_blacklist.__doc__` names
            # this exact confusion ("an over-grown set surfaces as an unaffordable market") as the reason
            # `relaunch_market_gate` reports `exclusions_or_spec_not_price`; the fan-out had no equivalent.
            _n_excl, _n_held = len(excluded), len(used_machines) - len(excluded)
            _why_short = ""
            if "no rentable verified offer" in str(e):
                _why_short = (f"  <-- NOT a capacity refusal: our own filter removed {len(used_machines)} "
                              f"machine(s) ({_n_excl} excluded + {_n_held} we already hold or just rented "
                              f"this wave) before ranking. Remedy is to widen supply (withdraw a wrong "
                              f"exclusion, or wait for the fleet to shrink), not to wait for prices.")
                # ★ AND IT GOES IN THE COMMITTED RECORD, NOT ONLY THE LOG (2026-07-28). This exact line was
                # printed on every failed submit through the night while `step1-fanout-market-hold.json`
                # showed an ordinary price reading — so the one artifact a reader opens said "the market",
                # and only the job log said "us". `hold_cause` is the same key `relaunch_market_gate`
                # already sets, so both lanes now answer this question with the same word.
                _submit_starved.append({"unit_id": u["unit_id"], "error": str(e)[:300]})
            _lprint(f"[s1f] SUBMIT FAILED {u['unit_id']}: {e}{_why_short}")
            continue
        # Print the FLOOR, the BID and the premium separately. The fan-out's cost estimate was built from a
        # single instance's realized $/hr with no visibility into how much of that was our own bid premium.
        # Making it visible at submit time is what stops the next estimate inheriting it silently — this is the
        # lane whose realized $0.35-0.39/hr was later mistaken for "the 4090 market" when it was really
        # x1.5 on a min_bid-ranked offer. Report the premium we ACTUALLY bid rather than a hardcoded multiple:
        # under the derived policy (floor + a staleness tick) it should now be a fraction of a cent.
        _dph = h.extra.get("dph")
        _floor = h.extra.get("min_bid")
        _bid = h.extra.get("bid")
        _prem = (f" (floor ${_floor}/hr -> bid ${_bid}/hr"
                 f"{f', +${round(float(_bid) - float(_floor), 4)}/hr premium' if _bid else ''})"
                 if _floor else "")
        _mid = h.extra.get("machine_id")
        if _mid is not None:
            used_machines.add(str(_mid))
        # ★ AND THE HOSTS THIS SUBMIT TRIED AND DESTROYED ON THE WAY (2026-07-29). `gpu_backend.submit` now
        # reads the start reply, so a host that answers `resources_unavailable` is destroyed and replaced
        # inside the same call instead of being handed back as a live rental (see `CapacityRefusedAtStart`).
        # Those machines are already $0, but the REST OF THIS WAVE should not walk straight back into them:
        # `used_machines` is precisely the wave-scoped "do not place here" set, and it dies with the wave —
        # which keeps this a claim about a moment, not the durable per-machine record trimcrae struck down.
        # This lane sees refusals too, and that is measured rather than assumed: `step1-fanout-map.json`
        # carries rentals billed 0.03 h and 0.05 h, i.e. boxes that never ran. A 19-wide fan-out simply
        # absorbs what a 2-unit lane cannot.
        for _r in (h.extra.get("start_refusals") or ()):
            used_machines.add(str(_r["machine_id"]))
        if h.extra.get("start_refusals"):
            _lprint("[s1f] %s: %d host(s) refused the start and were destroyed ($0 each) before this one "
                    "landed: %s — avoided for the rest of this wave."
                    % (spec.name, len(h.extra["start_refusals"]),
                       ", ".join(str(r["machine_id"]) for r in h.extra["start_refusals"])))
        # NO `flush=True` HERE. `_lprint` is not `print` — it flushes internally — and passing print's kwarg
        # to it raised TypeError on the FIRST SUCCESSFUL SUBMISSION, i.e. only ever on the money path.
        # Observed 2026-07-26 7:54 PM ET (autoscale run 30226203566): instance 45951628 was rented and the
        # process then died on this line, BEFORE the rental ledger entry, before `_save_ledger`, before
        # `_arm_watchdog` and before the launch readout. So the box billed while being absent from realised
        # spend and absent from the watch list. Fanned 19 wide it would have submitted exactly one unit per
        # tick, none of them ledgered or watched. tests/test_congeneric_fanout.py now binds every internal
        # call in this module against its callee's signature, statically, so this class cannot recur.
        # ★ REPORT THE $/ns OF THE OFFER ACTUALLY RENTED, not the one the gate cleared on (2026-07-27).
        # Those were never the same object — the gate reads one board, `submit` selects off another — so a
        # readout quoting the cleared figure describes a purchase that did not happen. `_rented_usd_per_ns`
        # prices the offer we got, and flags it against both lines: the §1 1.5x reporting line and the
        # binding per-unit ceiling. `⛔ ABOVE CEILING` should now be unreachable (ResourceSpec.max_usd_per_ns
        # makes it so) and is printed anyway, because a guard that cannot report its own failure is how this
        # lane keeps discovering things late.
        _upn, _cell = _rented_usd_per_ns(h)
        _lprint(f"[s1f] submitted {spec.name} -> instance {h.job_id} machine {_mid} "
                f"dph≈${_dph}/hr{_prem} | RENTED AT {_cell}")
        handles.append({"unit_id": u["unit_id"], "label": spec.name, "instance": h.job_id,
                        "machine_id": _mid, "dph": h.extra.get("dph"),
                        "min_bid": _floor, "bid": _bid})
        _ledger.setdefault("rentals", {})[str(h.job_id)] = {
            "unit_id": u["unit_id"], "label": spec.name, "machine_id": _mid,
            "bid": _bid, "min_bid": _floor, "dph": _dph, "billed_min": 0,
            "launched_utc": _utcnow(), "last_seen_utc": None}
        # ★★ SAVE AFTER **EACH** RENTAL, NOT AFTER THE LOOP (2026-07-27, measured). CLAUDE.md's checkpoint
        # rule — "checkpoint after each unit of work and upload as it is written; a default end-of-job
        # upload loses ALL partial work on a timeout" — applies to the RENTAL LEDGER exactly as it does to a
        # trajectory, and this loop was violating it.
        #
        # THE MEASUREMENT, AND THE MARGIN. A submit is not instant: Vast reports `intended=stopped` on a
        # fresh create and the backend polls up to 8 times before giving up, so a unit costs ~15-70 s.
        # Timed from the step boundaries of two consecutive ticks on 2026-07-27 — run 30296004080,
        # 18:58:10Z -> 19:01:22Z, and run 30296390447, 19:02:41Z -> 19:05:48Z — five submits each, i.e.
        # **~37 s per unit**. At the lane's `FANOUT_WIDTH` of 19 that projects to ~12 min inside ONE step,
        # against the job's `timeout-minutes: 25`. Not a comfortable margin: the poll is bounded by attempts,
        # not by time, so a wave where many hosts sit in `loading` runs at the slow end of that range.
        #
        # ⚠ AND DO NOT REPEAT THE MISREAD THAT PROMPTED THIS. The same step was first believed to have taken
        # **18 minutes**, from polling the jobs API while the run was live — that endpoint lags, reporting a
        # finished step as `in_progress` for many minutes. The real figure came from the step's own
        # `started_at`/`completed_at` after completion. Time a CI step from the completed record, never from
        # a live poll.
        #
        # If the loop ever does hit the timeout, every box rented so far bills while absent from the
        # realised-spend ledger and absent from the watch list — the 2026-07-26 instance-45951628 shape
        # reached by a different route. An extra S3 PUT per rental is free; a box that bills invisibly is not.
        _save_ledger(s3, bucket, _ledger)
        _arm_watchdog([u["unit_id"]], os.environ.get("GIT_BRANCH", "main"))
        _write_launch_readout()
    # MEASURED, not asserted (CLAUDE.md §4). If this ever reports ~0 saved calls on a multi-unit wave the
    # cache is not doing its job and the ramp is back to burst-reading the shared key once per unit.
    _board_stack.close()
    _lprint(f"[s1f] board-read cache over the wave: {_board_stats['hits']} hit(s), "
            f"{_board_stats['misses']} real read(s) — {_board_stats['saved_calls']} Vast "
            f"/search/asks/ call(s) NOT made against the shared key (TTL {_board_ttl:.0f}s).")
    if _submit_starved:
        # ⚠ THE RECORD MUST SAY "US", NOT "THE MARKET". Written AFTER the wave so it reflects the final
        # filter width, and it deliberately overwrites the pricing pass's record for this tick: the price
        # reading is true and was already acted on (these units CLEARED the gate — that is why they reached
        # submit), so the decision-relevant fact left standing is why the cleared units still did not land.
        _starved_doc = {
            "_what": "The step 1 fan-out cleared the price gate and then could not place units anyway, "
                     "because its OWN host filter had removed the board before ranking.",
            "_rule": "CLAUDE.md §6 — an exclusion-starved board must never be reported as a price hold.",
            "utc": _utcnow(), "decision": "exclusions_hold",
            "decision_meaning": PLACEMENT_DECISIONS["exclusions_hold"],
            "decision_why": (f"{len(_submit_starved)} unit(s) failed with `no rentable verified offer` "
                             f"AFTER clearing the $/ns gate, while our own filter removed "
                             f"{len(used_machines)} machine(s) ({len(excluded)} excluded + "
                             f"{len(used_machines) - len(excluded)} we already hold or just rented)."),
            "held": True, "n_withheld": len(_submit_starved), "n_launching_now": len(handles),
            "n_held": len(_submit_starved),
            "hold_cause": HOLD_CAUSE_EXCLUSIONS,
            "hold_cause_why": (f"Our own filter, not the market: {len(excluded)} machine(s) excluded and "
                               f"{len(used_machines) - len(excluded)} held by this wave. Remedy is to widen "
                               f"supply (withdraw a wrong exclusion — see "
                               f"congeneric_fanout_vast.retire_perishable_exclusions), not to wait for "
                               f"prices."),
            "starved_units": _submit_starved,
            "price_blocks_every_unit": False, "first_held_utc": None, "held_hours": 0.0,
            "binding_gate": "exclusions", "binding_gate_why": "our own host filter",
            "binding_gate_scope": f"{len(_submit_starved)} unit(s) that had already cleared price",
        }
        annotate_exclusions(_starved_doc, excluded, n_wave_held=len(used_machines) - len(excluded))
        _lprint(f"[s1f] ⚠ EXCLUSIONS HOLD: {_starved_doc['decision_why']} Recorded as "
                f"hold_cause={HOLD_CAUSE_EXCLUSIONS} — this is NOT a price hold.")
        _write_market_hold(_starved_doc, s3, bucket)
    with open("step1-fanout-handles.json", "w") as f:
        json.dump(handles, f, indent=2)
    # the label -> unit map, so a later collect/monitor can name instances without re-deriving the index
    try:
        _s3().put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_manifest.json",
                         Body=json.dumps({f"{LABEL_PREFIX}{i:02d}-{u['ligand_b']}"[:64]: u["unit_id"]
                                          for i, u in enumerate(units)}, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        _lprint(f"[s1f] manifest upload skipped: {e}")
    _write_launch_readout()


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE IN-FLIGHT BOARD — this lane's rows, handed to the renderer every lane shares
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⚠ NOTHING HERE RENDERS A TABLE. `inflight_board` owns the columns, the `—` discipline and the stall rule;
# this block only supplies the facts `mode_monitor` has already read. Building a second table here is the
# defect `inflight_board.__doc__` was written to end.
#
# ★ THE BOARD KEEPS ITS OWN POLL CENSUS, AND IT MUST. `_progress_prev.json` is OVERWRITTEN by this very
# function as its last act, so anything reading it back compares a pass against itself — the trap
# `_idle_evidence` documents. The board's counters live under their own key, written after they are read.
_BOARD_PREV_KEY = f"{RESULT_PREFIX}/_board_prev.json"

# The unit's four stages, in execution order. `committed_progress` already ranks them this way (complex
# before solvent, warmup before production) and the scalar's `detail` string names the current one, so this
# is the same ordering read back rather than a second opinion about it.
_BOARD_STAGES = (("complex", "warmup"), ("complex", "production"),
                 ("solvent", "warmup"), ("solvent", "production"))


def board_targets(s3, bucket, uid):
    """({leg: (warmup_target, prod_target)}, source_note) from THIS unit's own driver logs. Never typed.

    ⛔ WHERE THE DENOMINATOR ACTUALLY LIVES, AND WHY IT IS OFTEN ABSENT. `rbfe_spot_driver` prints
    `warmup_target=N … prod_target=M` at startup, computed from OpenFE settings this process has no MD stack
    to evaluate — so it must be PARSED, never recomputed (the same rule the ternary board follows). On this
    lane the engine's stdout goes to `/tmp/<leg>.log` and is uploaded to S3 only when the leg ENDS
    (`_LEG` captures `rc` and then always ships the log). So a unit on its FIRST leg legitimately has no
    target anywhere durable, and the honest board cell is `—` with that stated — not a number lifted from
    another edge, whose per-edge timestep (congeneric-edge-timestep-table.json: 2 fs vs 4 fs) can double the
    iteration count and would make the percentage confidently wrong.

    ★ WITHIN ONE UNIT the two legs DO share a target: the driver derives it from the protocol's equilibration
    and production lengths and the edge's timestep, none of which is leg-specific. So a landed complex log
    supplies the solvent leg's denominator too, and the row says that is where it came from.
    """
    found = {}
    for leg in ("complex", "solvent"):
        txt = _get_text_head(s3, bucket, f"{RESULT_PREFIX}/{uid}/{leg}.log")
        tg = _ifb.parse_targets(txt) if txt else None
        if tg:
            found[leg] = tg
    if not found:
        return {}, None
    src = sorted(found)[0]
    return ({leg: found.get(leg, found[src]) for leg in ("complex", "solvent")},
            src if len(found) < 2 else None)


def board_stage_plan(targets_by_leg):
    """[(stage_key, target), …] over the whole unit, or None when the denominator is unknown. PURE."""
    if not targets_by_leg:
        return None
    out = []
    for leg, phase in _BOARD_STAGES:
        tg = targets_by_leg.get(leg)
        if not tg:
            return None
        out.append((f"{leg}/{phase}", tg[0] if phase == "warmup" else tg[1]))
    return out


def board_stage_and_iter(detail):
    """('complex/production', 1200) from `committed_progress`'s detail string, or (None, 0). PURE."""
    if not detail or "@" not in detail:
        return None, 0
    stage, _, it = detail.partition("@")
    try:
        return stage, int(it)
    except ValueError:
        return stage, 0


def board_price_cell(inst, hold_doc):
    """The `$/ns` cell for one unit — PAYING when a host is billing, REFUSED when the gate declined.

    ★★ THE TWO MUST NEVER RENDER ALIKE (CLAUDE.md §1, trimcrae 2026-07-27: *"the $/ns column still shows
    several rows over 1.5×. Why? Are we not stopping those runs?"*). A unit with a live host is money going
    out at that host's billed rate. A unit with NO host on a tick whose recorded placement decision was a
    PRICE HOLD is the opposite outcome of the same guard: `$0` spent, and the multiple on the row is what we
    DECLINED. `inflight_usd_per_ns` owns both glyphs; this only decides which of the two facts is true here,
    from the artifact that already recorded it (`step1-fanout-market-hold.json`).
    """
    if inst is not None:
        return _ifb.usd_per_ns_cell(inst.get("gpu_name"), inst.get("dph_total"))
    if not hold_doc or not hold_doc.get("held"):
        return None
    offers = hold_doc.get("offers_priced") or []
    if not offers:
        return None
    best = offers[0]
    # The hold artifact records $/ns; `inflight_usd_per_ns.row` prices from $/hr, so the rate is converted
    # back through the SAME throughput table that produced it — no second arithmetic, and the round trip is
    # exact. ⚠ A ZERO ns/h WOULD MAKE THAT CONVERSION SILENTLY PRODUCE `$0.00000/ns · 0.00× basis`, which is
    # a fabricated figure wearing a refusal glyph. An unbenched card is unpriceable, so the cell is `—`.
    nsh = _vcm_ns_per_hour(best.get("gpu"))
    if not nsh or best.get("usd_per_ns") is None:
        return None
    return _ifb.usd_per_ns_cell(best.get("gpu"), float(best["usd_per_ns"]) * nsh,
                                stance="refused", rate_basis="offer")


def _vcm_ns_per_hour(gpu):
    """ns/h for a card, from the ONE throughput table. 0 when unbenched (the caller then renders `—`)."""
    try:
        import vast_cost_model as _vcm
        return _vcm.ns_per_hour(gpu) or 0.0
    except Exception:  # noqa: BLE001
        return 0.0


MARKET_HOLD_READOUT = "step1-fanout-market-hold.json"


def read_market_hold(path=None):
    """The tick's last recorded placement decision, or None. Its ONE home is the artifact `_write_market_hold`
    already commits, so the board and the launch readout can never disagree about whether price held."""
    try:
        with open(path or MARKET_HOLD_READOUT) as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001 — no record is not a hold; the $/ns cell is then `—`
        return None


def board_rows(s3, bucket, units, blocked, done_ids, obs, live, unreadable, prev_state, hold_doc=None):
    """This lane's rows for the in-flight board, plus the census to persist. Returns (rows, new_state).

    ⚠ A UNIT IS NEVER DROPPED FOR BEING UNMEASURABLE. An unknown `%` or ETA renders `—` with the WHY naming
    which fact was missing; omitting the row would make a unit we cannot measure look like one that does not
    exist. Only FINISHED and permanently-BLOCKED units are absent, and both are counted in the section note
    so the reader can see the denominator.
    """
    idx = {u["unit_id"]: i for i, u in enumerate(units)}
    by_label = {}
    for i in (live or ()):
        by_label[i.get("label") or ""] = i
    hold_doc = read_market_hold() if hold_doc is None else hold_doc
    census, rows = {}, []
    for u in units:
        uid = u["unit_id"]
        if uid in done_ids or uid in (blocked or {}):
            continue
        o = (obs or {}).get(uid) or {}
        stage, it = board_stage_and_iter(o.get("detail"))
        census[uid] = {"stage": stage, "iteration": (None if o.get("unreadable") else it),
                       "utc": _utcnow()}
        rows.append({"unit": u, "idx": idx[uid], "obs": o, "stage": stage, "iteration": it})
    new_state = _ifb.advance_counters(prev_state, census)
    out = []
    for r in rows:
        u, uid, o = r["unit"], r["unit"]["unit_id"], r["obs"]
        inst = by_label.get(unit_label(u, r["idx"]))
        try:
            targets, borrowed = board_targets(s3, bucket, uid)
            stages = board_stage_plan(targets)
            pct = _ifb.sequential_pct(stages, r["stage"], r["iteration"]) if stages else None
            rate = _ifb.measured_rate_per_h((prev_state or {}).get(uid), census.get(uid))
            remaining = _ifb.sequential_remaining(stages, r["stage"], r["iteration"]) if stages else None
            eta_s = (remaining / rate * 3600.0) if (remaining is not None and rate) else None
            # TWO reasons, kept apart on purpose, because conflating them is how a STALLED row ends up
            # wearing an explanation that denies it (the `pre_first_commit` and `guard_shielding` defects
            # the ternary board hit in production, one lane over):
            #   cell_why  — why a `%` or an ETA cell is `—`. True of a perfectly healthy leg.
            #   state_why — why this leg is NOT RUNNING. The only thing `state_of` may be handed as the
            #               justification for NO HOST / UNKNOWN / STALLED.
            cell_why = ""
            if o.get("unreadable"):
                cell_why = "commit store unlistable this tick — skipped, NOT counted as zero progress"
            elif stages is None:
                cell_why = ("no target yet: the driver prints `warmup_target=`/`prod_target=` into "
                            "/tmp/<leg>.log on the host and this lane uploads that log only when a leg ENDS, "
                            "so % and ETA are unknowable until this unit's first leg lands")
            elif rate is None:
                cell_why = ("no measured iteration rate across two board polls yet — ETA unknowable, "
                            "progress is real (committed %s)" % (o.get("detail") or "none"))
            elif borrowed:
                cell_why = ("targets from this unit's %s-leg driver log — both legs share them (same "
                            "protocol lengths, same per-edge timestep)" % borrowed)
            age_min = _age_min(inst) if inst is not None else None
            cold = age_min is not None and age_min < _vig.MIN_INSTANCE_AGE_MIN
            pre_first = (r["stage"] is None and age_min is not None
                         and age_min < _vig.SETUP_GRACE_MIN)
            no_adv = int((new_state.get(uid) or {}).get("no_advance_polls") or 0)
            # ADVANCEMENT, from two independent positive signals and never from the absence of one: the
            # census actually moved since the previous poll, or the guard's own GPU-busy rule says this box
            # is doing work. The second is load-bearing here — this lane commits every 20/40 iterations
            # (~5-10 min) while a supervising agent may poll every 3, so "no advance THIS poll" is the
            # ordinary state of a healthy leg. See `inflight_board.gpu_is_busy`.
            advanced = (_ifb.advanced_since_last_poll((prev_state or {}).get(uid), census.get(uid))
                        or _ifb.gpu_is_busy(_gpu_util(inst) if inst is not None else None))
            if inst is None and unreadable:
                state_why = ("host state UNKNOWN — the Vast instance list did not read this tick (%s), so "
                             "this is NOT a host death; the committed checkpoint (%s) is intact in S3"
                             % (unreadable, o.get("detail") or "none"))
            elif inst is None:
                state_why = ("no live host — the committed checkpoint (%s) is intact in S3; the next tick's "
                             "gate re-prices this unit" % (o.get("detail") or "none"))
            elif no_adv >= _ifb.STALL_POLLS:
                # `None` is "the host is not telling us", NOT an idle GPU — `_gpu_util`'s own rule, and the
                # two must not render alike because only the second is evidence of anything.
                _u = _gpu_util(inst)
                state_why = ("%d consecutive board polls with no committed advance; phase %s, GPU %s"
                             % (no_adv, o.get("phase") or "none",
                                "utilisation not reported by the host" if _u is None else "%.1f%%" % _u))
            else:
                state_why = cell_why
            state, swhy = _ifb.state_of(
                inst is not None, advanced, no_adv, bool(cold),
                why_not_running=state_why or None, pre_first_commit=bool(pre_first),
                host_list_readable=(not unreadable or inst is not None))
            price = board_price_cell(inst, hold_doc)
            eta_out = None if inst is None else eta_s
            out.append({"name": _short_unit_name(u), "pct": pct, "eta_s": eta_out, "usd_per_ns": price,
                        "state": state,
                        "why": swhy or (cell_why if (pct is None or eta_out is None) else "")})
        except Exception as e:  # noqa: BLE001
            # ⚠ PER ROW, NOT PER TABLE. A single row that cannot be built must not take the board with it —
            # the one tick where a leg genuinely misbehaves is the tick the board must still render.
            out.append({"name": _short_unit_name(u), "pct": None, "eta_s": None, "usd_per_ns": None,
                        "state": _ifb.UNKNOWN,
                        "why": "row could not be built: %s: %s" % (type(e).__name__, e)})
    return out, new_state


def _short_unit_name(unit):
    """A brief label for a fan-out unit: the ligand being perturbed TO, which is what names the edge."""
    b = str(unit.get("ligand_b") or unit.get("unit_id") or "?")
    rep = unit.get("replicate")
    return f"{b} r{rep}" if rep else b


def mode_monitor():
    """Tight-cadence PROGRESS check (not a liveness ping): per-unit phase + per-instance state, one line each."""
    bucket, s3 = _require_bucket(), _s3()
    # lane_units: a replicate that is billing must appear in the progress census like any other unit, or the
    # only fleet-wide readout of "is this host doing work" has a blind spot exactly where new work runs.
    units = lane_units()
    # ★★ A PERMANENTLY-EXCLUDED UNIT MUST NOT KEEP WEARING ITS LAST FAILURE (2026-07-28). Before this, a
    # blocked edge sat at `leg-complex-FAILED-rc1` in every census forever — the same string a unit that
    # just crashed and is about to be re-placed wears. Two opposite states, one label: one says "watch this,
    # it will resume", the other says "this will never resume and here is why". The block map is loaded
    # here so the census can say which, and so the blocked count in the snapshot comes from the artifact
    # that actually knows rather than from a subtraction.
    blocked = _load_blocked(s3, bucket)
    key = os.environ.get("VAST_API_KEY")
    # ⚠ THREE STATES, NOT TWO: N instances, ZERO instances, and COULD-NOT-ASK. Dropping the early `return`
    # here was right — the committed-iteration census below reads S3 and does not need the Vast key, so a
    # missing key should not cost us the progress check. But `live = []` then prints "live s1f-* instances: 0",
    # which reads as "nothing is billing" when it actually means "nothing was measured". Reporting an
    # unmeasured state as a measured zero is this repo's most expensive defect class, and a false zero on a
    # RENTAL board is the version of it that costs money. `_live_instances` returning None is likewise
    # "the API call failed", never "none".
    #
    # ★★ AND THE COULD-NOT-ASK STATE MUST BE *REACHABLE* — IT WAS DEAD CODE, AND THAT COST THE 1:21 PM TICK
    #    (2026-07-27, run 30288877243).
    #
    # WHAT HAPPENED. `_live_instances` does not return None on a failed read — it RAISES. So the handler
    # directly below, written for exactly "the API call failed", could only ever fire for a MISSING KEY. At
    # 1:21:48 PM ET a transient edge 403 (nginx HTML, not a Vast JSON error — see `gpu_backend._vast_request`)
    # outlived that function's 5-hop / ~30 s GET retry budget, the RuntimeError propagated out of
    # `mode_monitor`, and the step exited 1 at 1:22:20 PM. Because this is the FIRST step of the tick's watch
    # half, the freshness gate, the collect and the reap were all SKIPPED — so `step1-fanout-progress.json`
    # stayed stamped 12:42 PM while 11 rentals kept billing, and three stopped hosts went unadjudicated.
    #
    # WHY DEGRADING HERE IS THE CORRECT SAFETY DIRECTION, not a softening. This workflow's own stated
    # principle is that supervision must be the LAST thing a tick loses: monitoring rents nothing. The
    # fail-CLOSED rule ("never rent when you cannot see what you already hold") belongs to `mode_launch`,
    # which is untouched and still raises. Splitting them is the whole point — a read failure must not be
    # allowed to take down the watch on a fleet that is ALREADY BILLING.
    #
    # ⚠ AND IT MUST NOT PRETEND IT SAW ZERO. `live` degrades to `[]` only so the S3 census can proceed; the
    # blindness is recorded in `_vast_unreadable` and republished as `live_instances: null` in the snapshot,
    # never as 0. The stuck-start adjudication below is additionally hard-guarded off, so nothing is ever
    # destroyed on a blind read.
    live, unreadable = None, None
    if key:
        # ⛔ DO NOT "SIMPLIFY" THIS TRY AWAY — IT IS THE ONLY THING THAT MAKES THE `live is None` BRANCH BELOW
        #    REACHABLE WHEN THE API FAILS. `_live_instances` RAISES; it never returns None. Delete this catch
        #    and the handler below silently narrows to "no key configured", which is precisely the state this
        #    code was in during the 1:21 PM ET incident: a branch whose comment claimed to cover an API
        #    failure, which could not fire for one. Do not trust the handler's existence as proof the case is
        #    handled — the pairing IS the mechanism, and `tests/test_monitor_survives_unreadable_board.py`
        #    exercises it end-to-end rather than reading this prose back.
        try:
            live = _live_instances(key)
        except Exception as e:  # noqa: BLE001 — any read failure is the same "could not ask" state
            unreadable = f"{type(e).__name__}: {e}"[:300]
    # Reached in TWO ways, and they mean different things: no key (never asked) or the catch above (asked,
    # refused). Both are "could not ask"; neither is "asked and the answer was none".
    if live is None:
        print("[s1f] ⚠ live s1f-* instances: UNKNOWN — "
              + ("no VAST_API_KEY in this environment" if not key else
                 f"the instance list could not be read ({unreadable})")
              + ". This is NOT 'zero': any rental is unobserved here and could still be billing. "
                "The per-unit progress census below is unaffected — it reads S3.")
        if unreadable:
            print("::warning title=VAST INSTANCE LIST UNREADABLE::The progress census still ran (it reads "
                  "S3), but this tick could NOT see the rental board, so it reaped nothing and adjudicated "
                  "no stopped host. live_instances is recorded as null, not 0.")
        live = []
    else:
        print(f"[s1f] live s1f-* instances: {len(live)}")
    for i in live:
        # ★ `machine=` IS NOT DECORATION — IT IS THE FIELD THE NEVER-STARTED VERDICT IS MADE ON
        #   (2026-07-27, 3:28 PM ET). Five of fifteen hosts carried the never-started signature and the
        #   question that decides the remedy — "are these five DIFFERENT bad hosts, or ONE bad machine that
        #   won selection five times?" — could not be answered from any committed artifact, because neither
        #   this line nor the snapshot below carried the machine id. The two answers have opposite actions
        #   (five host-scoped exclusions vs one 1569-class machine that must be excluded once and will
        #   otherwise keep winning), so an adjudication that cannot distinguish them is not an adjudication.
        print(f"[s1f]   id={i.get('id')} label={i.get('label')} machine={i.get('machine_id')} "
              f"actual={i.get('actual_status')} "
              f"cur={i.get('cur_state')} dph=${i.get('dph_total')} gpu={i.get('gpu_name')} "
              f"util={_gpu_util(i)}% age_min={_age_min(i)} msg={(i.get('status_msg') or '')[:120]!r}")
    # ★ THE PROVEN-MACHINE SET, ACCUMULATED FIRST AND PERSISTED, because the evidence it holds is destroyed
    # by the very reap that runs later in this tick. A machine that has RUN one of our containers can never
    # be condemned as one that never starts, and without this the proof dies with the instance — see
    # `never_started_cohort`, `known_good`.
    _good = _load_started_machines(s3, bucket) | set(observed_started_machines(live))
    _save_started_machines(s3, bucket, _good)
    # ...and repair any exclusion this lane wrote that the same evidence now refutes. Runs BEFORE the
    # condemn block below, so a machine cannot be withdrawn and re-condemned inside one tick.
    withdraw_wrong_exclusions(s3, bucket, _good)

    # PROGRESS, not liveness. The committed-iteration census is the durable evidence the science advanced;
    # `phase.txt` and the leg JSONs are context around it. `prev` is the previous check's census, so this
    # block can answer "did it move SINCE LAST TIME" — which is the only question worth asking of a running
    # sampler, and the one a phase marker structurally cannot answer.
    prev = (_get_json(s3, bucket, f"{RESULT_PREFIX}/_progress_prev.json") or {})
    cur, n_done = {}, 0
    # What the IN-FLIGHT BOARD needs, captured from the reads this loop already performs rather than re-read
    # afterwards: a second pass over S3 would be a second set of observations, free to disagree with the
    # census printed above it (CLAUDE.md rule 1).
    board_obs, board_done = {}, set()
    for u in units:
        ddg = _get_json(s3, bucket, result_key(u, RESULT_PREFIX))
        if ddg:
            board_done.add(u["unit_id"])
            n_done += 1
            print(f"[s1f]   {u['unit_id']:56s} DONE ddG={ddg.get('ddg_bind_kcal')} "
                  f"± {ddg.get('ddg_bind_unc_kcal')}")
            continue
        if u["unit_id"] in blocked:
            # Not "still failing" and not quietly missing — excluded, with the reason on the line.
            print(f"[s1f]   {u['unit_id']:56s} {BLOCKED_PHASE:28s} "
                  f"{(blocked[u['unit_id']] or {}).get('why')}")
            continue
        phase = _get_text(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/phase.txt")
        legs = [L for L in ("complex", "solvent")
                if _exists(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/leg_{u['receptor']}_{L}.json")]
        scalar, detail = committed_progress(s3, bucket, u)
        was = (prev.get(u["unit_id"]) or {}).get("scalar")
        if scalar >= 0:
            cur[u["unit_id"]] = {"scalar": scalar, "detail": detail, "utc": _utcnow()}
        rate = _iter_rate(prev.get(u["unit_id"]), scalar)
        board_obs[u["unit_id"]] = {"phase": phase, "legs": legs, "detail": detail,
                                   "unreadable": scalar < 0}
        if scalar < 0:
            delta = "UNREADABLE (skipped, NOT counted as zero)"
        elif was is None:
            delta = "first census"
        elif scalar > was:
            delta = f"+{scalar - was} since last check" + (f", {rate} iter/h" if rate else "")
        elif phase and not phase.startswith(("boot", "staged")):
            delta = "NO ADVANCE since last check"
        else:
            delta = "no commit yet (cold start)"
        slow = (rate is not None and rate < 0.5 * EXPECTED_ITER_PER_H
                and (phase or "").startswith("leg-"))
        print(f"[s1f]   {u['unit_id']:56s} {phase or 'not-started':28s} legs_done={legs} "
              f"committed={detail} [{delta}]"
              + (f"  <-- {rate} iter/h is under half the measured {EXPECTED_ITER_PER_H:.0f}; "
                 f"if it holds across checks and is not an end-of-leg MBAR pause, this host is slower than "
                 f"its card and should be re-rented elsewhere" if slow else ""))
    # SELF-HEAL the create/start race before summarising. Creating a Vast ask does not reliably launch the
    # container: the start PUT can be lost while Vast is still finishing the create, leaving the box at
    # cur_state="stopped" forever, burning nothing but never running either (gpu_backend._ensure_running
    # documents the same race and retries only ~48 s at submit time, which is not always long enough).
    # Signature, seen on s1f-01: cur_state "stopped" AND an EMPTY status_msg — as opposed to the three
    # instances that were also "loading" but whose status_msg showed an image pull in progress.
    # Re-issuing the start is idempotent, so this runs on every progress check. A unit whose ddg.json is
    # already in S3 is never restarted — that box is finished, not stalled.
    #
    # ★★ AND THE NUDGE ESCALATES (2026-07-27). As first written this block re-issued the start forever, which
    # is the Vast rule inverted: CLAUDE.md §6 says a host that will not deliver means PICK ANOTHER HOST, do
    # not wait it out. Measured that morning: s1f-00, s1f-08 and s1f-16 sat cur_state="stopped" with an EMPTY
    # status_msg for 49-53 minutes, nudged on every tick, never starting. They burned no GPU meter — but they
    # HELD THEIR UNIT'S SLOT, so three of nineteen edges could not be rented anywhere else for the better part
    # of an hour while the operator watched a fleet that looked 18-wide and was really 15-wide. An unbounded
    # retry against a box that has already refused is indistinguishable from waiting it out, which is the
    # thing the rule forbids.
    #
    # So the nudge now keeps score. Two independent conditions must BOTH hold before a host is condemned:
    #   * the STUCK SIGNATURE — cur_state "stopped" with an empty status_msg. A host still pulling the ~6 GiB
    #     image is also "loading" but advertises the pull in status_msg, and pulls legitimately run 20-40 min
    #     on cheap hosts. Condemning on age alone would reap healthy slow pulls.
    #   * TWO CONSECUTIVE CHECKS past STUCK_START_MIN — §4's discipline, so a single unlucky sample (an API
    #     blip, a listing mid-transition) can never destroy a rental. Strikes live in S3 because each tick is
    #     a fresh process with no memory of the last one.
    # Only then: destroy AND exclude the machine, via the same durable exclusion `mode_reap` writes — a host
    # that never starts has infinite realised $/ns, so it is invisible to $/ns ranking and would otherwise
    # keep winning selection and keep failing. Freeing the slot lets the next tick re-price that unit through
    # the market gate, which is exactly where the buy decision belongs.
    # ⚠ `not unreadable` IS LOAD-BEARING, NOT BELT-AND-BRACES. On a blind read `live` is `[]`, so this loop
    # would iterate nothing and destroy nothing today — but that safety is INCIDENTAL, and the next person to
    # "helpfully" seed `live` from a cache or a previous snapshot would silently hand a destroy path a stale
    # instance list. Condemning a host is irreversible; it must require a read we actually got.
    if key and not unreadable:
        idx = {u["unit_id"]: i for i, u in enumerate(units)}
        label_to_unit = {f"{LABEL_PREFIX}{idx[u['unit_id']]:02d}-{u['ligand_b']}"[:64]: u for u in units}
        start_state = _get_json(s3, bucket, f"{RESULT_PREFIX}/_start_state.json") or {}
        new_start_state = {}
        # ★★ WHICH NEVER-STARTS ARE OURS. `never_started_cohort` separates a genuine host fault from a
        # DUPLICATE this lane placed on a machine it already holds — 7 of 8 on 2026-07-27 were the latter,
        # and their machines were running our work at 76-98 % GPU. Both are destroyed; only the host fault
        # earns the permanent, cross-lane exclusion. Computed once, outside the loop, because it needs the
        # WHOLE fleet to decide any single row.
        _cohort_now = never_started_cohort(live, (), _good)
        _dupes = {r["instance"] for r in _cohort_now["never_started"] if r["klass"] == "double_booked"}
        # Machines proven to run our container: destroyed like any other dead box, but NEVER condemned.
        _proven = {r["instance"] for r in _cohort_now["never_started"]
                   if r["klass"] == "stopped_on_a_proven_machine"}
        for i in live:
            u = label_to_unit.get(i.get("label") or "")
            if not u or i.get("cur_state") != "stopped":
                continue
            if _exists(s3, bucket, result_key(u, RESULT_PREFIX)):
                continue                       # finished, not stalled
            iid, age = str(i.get("id")), _age_min(i)
            # An empty status_msg is the discriminator against a legitimate in-progress image pull.
            stuck_sig = not (i.get("status_msg") or "").strip()
            # ★★ THE SECOND CEILING — BECAUSE THE FIRST ONE ONLY BOUNDS *ONE* SIGNATURE (2026-07-27, 12:38 PM
            # ET). The escalation above fixed an unbounded nudge, but only for boxes with an EMPTY
            # status_msg. A box stopped with a NON-empty message was still re-nudged on every tick forever
            # with no strike and no ceiling — the identical bug, one signature narrower. Found by
            # adjudicating `s1f-00-cw_ev_5nh2`: cur_state=stopped for 28 min carrying
            # `'Successfully loaded docker.io/triskit23/nr4a3fep:latest'`, which correctly dodges the
            # empty-msg test and therefore could never escalate no matter how long it sat.
            #
            # WHY A SEPARATE, MUCH LONGER NUMBER rather than relaxing the discriminator: the empty-msg test
            # earns its keep by protecting a genuine ~6 GiB image pull, which legitimately runs 20-40 min on
            # a cheap host. Weakening it would reap healthy slow starts — the exact false positive that is
            # worse than the bug. So the pull protection is untouched, and this only says: whatever the
            # message claims, a box that has NOT reached running well over two hours after rental is not
            # pulling an image.
            hard_stop = age is not None and age >= STUCK_START_HARD_MIN
            _floor = stuck_start_min_for(i.get("id") in _dupes)
            if (stuck_sig and age is not None and age >= _floor) or hard_stop:
                strikes = int((start_state.get(iid) or {}).get("strikes", 0)) + 1
                if strikes >= STUCK_START_STRIKES:
                    mid = i.get("machine_id")
                    # ⚠ THE TWO CASES GET DIFFERENT EXCLUSION SCOPES, ON PURPOSE. An empty status_msg is the
                    # unambiguous create/start race — the container never executed, which is host-scoped and
                    # safe to share with every lane. The hard backstop is weaker evidence: the box did
                    # something (it reported loading an image) and merely never finished, so it is recorded
                    # LANE-scoped only. Wrongly publishing a healthy host to the shared set permanently
                    # removes cheap supply for everybody — and the cheapest capacity on this board is
                    # exactly these 5090s — so the shared set stays reserved for the unambiguous signature.
                    if stuck_sig and i.get("id") in _proven:
                        # Destroyed like any other box that cannot make progress, but NOT condemned: this
                        # machine has demonstrably run our image, so "it never starts" is contradicted by
                        # our own record. The unit is re-priced through the market gate like any other.
                        why = (f"stopped with an empty status_msg for {age} min across {strikes} "
                               f"consecutive checks on machine {i.get('machine_id')} — but that machine has "
                               f"RUN this lane's container before, so this is NOT a never-starts verdict")
                        _scope = None
                    elif stuck_sig and i.get("id") in _dupes:
                        # ⚠⚠ DESTROY, EXCLUDE NOTHING. This container never executed because WE were already
                        # renting that machine's GPU, not because the machine refuses to start — measured
                        # 2026-07-27: 0 of 7 double-booked instances started, while 8 of 10 single-booked
                        # ones did. A host-scoped exclusion is permanent and cross-lane, so publishing these
                        # would have retired five machines that were running this lane's own legs at
                        # 76-98 % GPU. The fix for this class is in `mode_launch` (seed host-distinctness
                        # from the live fleet), never in the blacklist.
                        why = (f"DOUBLE-BOOKED: never started in {age} min across {strikes} consecutive "
                               f"checks because this lane already holds a GPU on machine "
                               f"{i.get('machine_id')} — self-inflicted, the machine is not at fault")
                        _scope = None
                    elif stuck_sig:
                        why = (f"never started: cur_state=stopped with an empty status_msg for {age} min "
                               f"across {strikes} consecutive checks (create/start race, not an image pull)")
                        _scope = "host"
                    else:
                        why = (f"never reached running in {age} min across {strikes} consecutive checks "
                               f"(hard backstop {STUCK_START_HARD_MIN:.0f} min) despite status_msg "
                               f"{(i.get('status_msg') or '')[:80]!r} — far past any image pull, but the box "
                               f"did report activity, so this is LANE-scoped and not shared")
                        _scope = "lane"
                    try:
                        _vast_request("DELETE", f"/instances/{iid}/", key)
                        print(f"[s1f] CONDEMNED {iid} ({i.get('label')}) — {why}. Destroyed; the unit's slot "
                              f"is freed and the next tick re-prices it through the market gate.")
                    except Exception as e:  # noqa: BLE001
                        # Do NOT record an exclusion for a box that may still exist — same discipline as
                        # mode_reap. Keep the strike so the next tick tries the destroy again.
                        print(f"[s1f] condemn {iid} failed: {e} — leaving the strike in place, will retry")
                        new_start_state[iid] = {"strikes": strikes, "age_min": age, "utc": _utcnow()}
                        continue
                    # ★★ HOST SCOPE, NOT LANE SCOPE (2026-07-27, after machine 1569 took TEN relaunches).
                    # "cur_state=stopped with an empty status_msg — the container never executed" is the
                    # textbook host-scoped verdict: `vast_machine_blacklist.__doc__` names "a container that
                    # never executes" as its own example of a fact that transfers without an argument.
                    # Nothing about THIS workload enters the judgement — the box did not get as far as our
                    # image. Left at the default `lane`, every other lane pays its own rental to rediscover
                    # the same dead host, which is the precise gap the shared set was created to close.
                    #
                    # WHAT THIS IS NOT: the starved-host rule below (sustained gpu_util shortfall) stays
                    # LANE-scoped, because pricing.md A.1 withdrew exactly that reasoning once — a
                    # metadynamics leg's low utilisation turned out to be PLUMED's CPU-side bias and the same
                    # host ran at 74 % on the next phase. A never-started box has no such ambiguity.
                    if _scope is None:
                        # The dead instance is gone and that is the WHOLE remedy. Writing anything against
                        # this machine would condemn a box on evidence that does not support it, and the
                        # shared set has no expiry — see the `_dupes` / `_proven` notes above.
                        print(f"[s1f] machine {mid} deliberately NOT excluded — {why}. It stays selectable "
                              f"and is re-priced by the market gate like any other offer.")
                    elif mid is not None and _record_exclusion(s3, bucket, mid, why, scope=_scope,
                                                              unit=i.get("label")):
                        print(f"[s1f] machine {mid} added to the lane exclusion set"
                              + (" AND published to the cross-lane shared set (host-scoped: it never "
                                 "started)" if _scope == "host" else
                                 " ONLY (lane-scoped: the hard backstop is weaker evidence than a never-"
                                 "executed container, so it is not shared)")
                              + f": {why}")
                    continue                   # condemned: drop its strike row entirely
                new_start_state[iid] = {"strikes": strikes, "age_min": age, "utc": _utcnow()}
                print(f"[s1f] STUCK-START strike {strikes}/{STUCK_START_STRIKES} on {iid} ({i.get('label')}) "
                      f"— stopped with an empty status_msg for {age} min (floor {_floor:.0f} min"
                      + (", DOUBLE-BOOKED: no image-pull to protect" if i.get("id") in _dupes else "")
                      + f"); condemned at {STUCK_START_STRIKES} strikes")
            try:
                _vast_request("PUT", f"/instances/{iid}/", key, body={"state": "running"})
                print(f"[s1f] NUDGED {iid} ({i.get('label')}) — cur_state=stopped, no result yet; "
                      f"re-issued start (msg={(i.get('status_msg') or '')[:60]!r})")
            except Exception as e:  # noqa: BLE001
                print(f"[s1f] nudge {iid} failed: {e}")
        try:
            s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_start_state.json",
                          Body=json.dumps(new_start_state, indent=2).encode())
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] stuck-start state save failed: {e}")

    # ---- billed hours + the starved-host guard ------------------------------------------------------------
    # Two jobs, one pass over the live fleet, because both need the same `age_min` / `gpu_util` sample.
    if key:
        ledger = _load_ledger(s3, bucket)
        util_state = _get_json(s3, bucket, f"{RESULT_PREFIX}/_util_state.json") or {}
        new_state = {}
        # Recomputed here rather than borrowed from the nudge block above: the backfill below needs it, and a
        # name that only exists because an earlier `if key:` block happened to run is a NameError waiting for
        # someone to move a block.
        _idx = {u["unit_id"]: n for n, u in enumerate(units)}
        label_to_unit = {f"{LABEL_PREFIX}{_idx[u['unit_id']]:02d}-{u['ligand_b']}"[:64]: u for u in units}
        for i in live:
            iid, age = str(i.get("id")), _age_min(i)
            row = (ledger.get("rentals") or {}).get(iid)
            if row is None:
                # ★ BACKFILL — A LIVE RENTAL MISSING FROM THE LEDGER IS BILLING INVISIBLY (2026-07-26).
                # The ledger row is written by `mode_launch` immediately after `backend.submit`, so anything
                # that kills the launcher between the two leaves a rented, running, BILLING host that
                # realised-spend arithmetic cannot see — and, because the update above is gated on the row
                # already existing, could never later see. That is not hypothetical: the `_lprint(...,
                # flush=True)` TypeError did exactly this to instance 45951628 at 7:54 PM ET.
                # `monitor` is the one mode that meets every live instance on every pass, so it is where the
                # ledger is reconciled against reality. Priced from the LIVE listing (dph is what Vast is
                # charging now), and flagged, because a backfilled row is a repair and its bid/floor
                # provenance is genuinely unknown — an honest gap beats a fabricated one.
                row = {"unit_id": (label_to_unit.get(i.get("label") or "") or {}).get("unit_id"),
                       "label": i.get("label"), "machine_id": i.get("machine_id"),
                       "bid": None, "min_bid": None, "dph": i.get("dph_total"), "billed_min": 0,
                       "launched_utc": None, "last_seen_utc": None,
                       "_backfilled": "not recorded at launch (launcher died between submit and ledger "
                                      "write); reconciled from the live Vast listing by monitor"}
                ledger.setdefault("rentals", {})[iid] = row
                print(f"[s1f] LEDGER BACKFILL: instance {iid} ({i.get('label')}) was billing at "
                      f"${i.get('dph_total')}/hr with no ledger row — realised spend was under-reporting "
                      f"it. Row created; bid/floor unknown for this rental.")
            if row is not None:
                # MAX, not last: a paused/preempted box can report a smaller age on resume, and billed
                # minutes only ever go up.
                row["billed_min"] = max(int(row.get("billed_min") or 0), int(age))
                row["last_seen_utc"] = _utcnow()
            util = _gpu_util(i)
            running = (i.get("actual_status") == "running")
            if util is None or not running or age < STARVED_MIN_AGE_MIN:
                continue
            strikes = int((util_state.get(iid) or {}).get("strikes", 0))
            if float(util) < STARVED_UTIL_PCT:
                strikes += 1
            else:
                strikes = 0
            new_state[iid] = {"strikes": strikes, "util": util, "utc": _utcnow()}
            if strikes < STARVED_TICKS:
                continue
            # STARVED. This lane is plain RBFE — no PLUMED, no per-step host-side work — so the card constant
            # the $/ns ranking uses IS the throughput model here, and a host sustaining <40 % against a
            # healthy 70-95 % is not doing the work we are paying for. (pricing.md A.1's WITHDRAWN broad rule
            # was "exclude any low-util machine"; it was withdrawn because a metadynamics leg is CPU-bound
            # and the same host ran at 74 % once the bias was gone. That escape does not exist for this
            # workload, which is why the narrow rule is applied here and only here.)
            mid = i.get("machine_id")
            print(f"[s1f] STARVED HOST: instance {iid} (machine {mid}, {i.get('label')}) held "
                  f"gpu_util={util}% < {STARVED_UTIL_PCT}% for {strikes} consecutive checks at age "
                  f"{age} min — destroying and excluding. Checkpoints are in S3; a relaunch resumes.")
            try:
                _vast_request("DELETE", f"/instances/{iid}/", key)
            except Exception as e:  # noqa: BLE001
                print(f"[s1f] destroy {iid} failed: {e}")
            # THE UNIT, passed so the starved-host verdict can be counted against its author. This is the
            # exact site the measurement indicted: 15 durable exclusions, 10 units, three of them condemning
            # 3 / 3 / 2 machines apiece on this identical wording.
            if mid is not None and _record_exclusion(s3, bucket, mid,
                                                     f"gpu_util {util}% for {strikes} checks on a plain-RBFE "
                                                     f"leg (healthy band 70-95%); instance {iid}",
                                                     unit=i.get("label")):
                print(f"[s1f] machine {mid} added to the lane exclusion set")
            new_state.pop(iid, None)
        _save_ledger(s3, bucket, ledger)
        try:
            s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_util_state.json",
                          Body=json.dumps(new_state, indent=2).encode())
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] util state save failed: {e}")

    # The census is written AFTER the guard, so "did it advance since last check" compares against the
    # previous CHECK and not against something this pass just wrote.
    try:
        s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_progress_prev.json",
                      Body=json.dumps(cur, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] progress census save failed: {e}")

    # Summary LAST: a CI log is read from its tail, and the per-instance detail above scrolls out of view.
    # This block is the tight-cadence progress check — instance states, GPU utilisation and the phase
    # histogram in one place, so "is it ADVANCING?" is answerable without paging back through the log.
    states, utils = {}, []
    for i in live:
        states[i.get("actual_status") or "?"] = states.get(i.get("actual_status") or "?", 0) + 1
        if _gpu_util(i) is not None:
            utils.append(_gpu_util(i))
    phases = {}
    for u in units:
        p = unit_phase(u, blocked,
                       has_result=_exists(s3, bucket, result_key(u, RESULT_PREFIX)),
                       phase_txt=_get_text(s3, bucket,
                                           f"{RESULT_PREFIX}/{u['unit_id']}/phase.txt")).split()[0]
        phases[p] = phases.get(p, 0) + 1
    _n_done, _n_blocked, _n_outstanding = counts(
        units, {u["unit_id"] for u in units if _exists(s3, bucket, result_key(u, RESULT_PREFIX))}, blocked)
    _computable = computable_units(units, blocked)
    print("[s1f] ---------------- SUMMARY ----------------")
    # The headline is against the COMPUTABLE denominator, with the exclusions named beside it — not folded
    # into either the numerator or the denominator, which are the two ways to make it unquotable.
    print(f"[s1f] units {_n_done}/{len(_computable)} computable complete "
          f"({len(units)} map edges, {_n_blocked} permanently excluded"
          + (f": {sorted(blocked)}" if blocked else "")
          + f") | {_n_outstanding} outstanding | live instances {len(live)} {states or '{}'}")
    print(f"[s1f] phases {phases}")
    print(f"[s1f] gpu_util across live instances: {utils or 'n/a'}"
          + ("  <-- all idle; if unchanged next check, that is a STALL, not slowness"
             if utils and not any(utils) else ""))

    # ★ THE STOPPED-HOST ADJUDICATION, PRINTED AND COMMITTED. `instance_states` above says "5 loading, 2
    # exited" and stops there — which is the reading that let a never-started cohort and two routine
    # preemptions sit in one bucket. This names which is which and, crucially, whether they share a machine.
    _excl_now, _ = _load_excluded(s3, bucket)
    cohort = never_started_cohort(live, _excl_now, _good)
    if cohort["n_never_started"] or cohort["n_preempted"]:
        print(f"[s1f] STOPPED-HOST ADJUDICATION: {cohort['n_host_fault']} host-fault "
              f"(never started, sole rental, machine never ran our image -> destroy + HOST-scoped "
              f"exclusion) | {cohort['n_double_booked']} DOUBLE-BOOKED (never started because we already "
              f"hold that machine's GPU -> destroy the duplicate, machine NOT at fault) | "
              f"{cohort['n_stopped_on_a_proven_machine']} stopped on a PROVEN machine (it has run our "
              f"container before -> destroy and re-price, never condemn) | "
              f"{cohort['n_preempted']} preempted (ran and exited -> resume, never exclude)")
        for r in cohort["never_started"]:
            print(f"[s1f]   {r['klass'].upper():14s} {r['instance']} ({r['label']}) machine "
                  f"{r['machine_id']} age {r['age_min']} min"
                  + (f" — BEHIND our own instance {r['double_booked_behind']} on the same machine"
                     if r["double_booked_behind"] else "")
                  + f" -> {r['remedy']}")
        for r in cohort["preempted"]:
            print(f"[s1f]   PREEMPTED      {r['instance']} ({r['label']}) machine {r['machine_id']} "
                  f"age {r['age_min']} min — resume, machine NOT excluded")
    if cohort["n_double_booked"]:
        # Not a market fact and not a host fact — a placement fact, and the only one of the three whose fix
        # is in our own code (`mode_launch` seeds host-distinctness from the live fleet).
        print(f"::warning title=STEP1 FAN-OUT: SELF-INFLICTED NEVER-STARTS::{cohort['n_double_booked']} of "
              f"{cohort['n_never_started']} never-started host(s) are duplicates this lane placed on a "
              f"machine it was already renting. Their machines are NOT bad and must not be excluded.")
    if cohort["machines_excluded_since"]:
        print(f"[s1f] note: machine(s) {cohort['machines_excluded_since']} carrying a never-started rental "
              f"of ours are in the exclusion set NOW. That is corroboration (another lane reached the same "
              f"verdict), NOT evidence the set failed to reach the selector — the launcher prints the set "
              f"it actually applied on every wave, and that readout is the only thing that can show a miss.")

    # Written to disk (and committed back to the branch by CI) because a GitHub job log is only readable from
    # its tail, and the tail is always the runner's own post-job boilerplate. A committed progress file is the
    # readout that survives, and it doubles as a timestamped trail of how the fleet advanced.
    snapshot = {
        # ⚠ WHERE IN THE TICK THIS WAS TAKEN, because it misled a reader (me) twice in one session. The
        # autoscale tick runs monitor -> collect -> launch, and `live` is fetched ONCE at the top of this
        # function, so this snapshot is a BEFORE picture: it cannot show instances this tick's launch went on
        # to create, instances its collect went on to reap, or the effect of the nudge below. Reading
        # "live_instances: 1" here and concluding "the launch did nothing" is exactly the wrong inference —
        # the launch had not run yet. A second snapshot after the launch would be more current but would
        # destroy the advance diff, since _progress_prev.json would be overwritten seconds after it was set.
        "_snapshot_point": "START of the tick — before this tick's collect, nudge and launch",
        # ★ WHEN, NOT JUST WHERE (2026-07-27). `_snapshot_point` says where in the tick this was taken and
        # said nothing about WHEN, so a reader holding this file could not distinguish "measured a moment ago"
        # from "measured 45 minutes ago and never refreshed". That is exactly what happened at 9:40 AM ET:
        # 18 GPUs were billing, the only readable artifact showed `0 of 19 units advanced`, and because the
        # file was UNDATABLE that single reading was compatible with both "normal cold start three minutes in"
        # and "fleet-wide stall". The fleet was in fact advancing fine. An evidence artifact that cannot be
        # dated cannot be graded, and an ungradable artifact is worse than none — it invites the wrong
        # inference with the confidence of a measurement. These two fields are what `assert_progress_fresh`
        # in the autoscale workflow gates on, so a tick that goes green without re-measuring now fails loudly.
        "_generated_utc": _utcnow(),
        "_generated_et": _et_now(),
        "n_units": len(units), "n_complete": n_done,
        # ★ THE HONEST DENOMINATOR, DERIVED (2026-07-28). `n_units` is the MAP; what this lane can ever
        # deliver is the map minus its permanent exclusions, and the difference has to be visible in the
        # artifact or every reader downstream re-derives it wrongly. `blocked_units` carries the reason and
        # the evidence with each id, so "18, not 19" is never a bare assertion.
        "n_computable": len(computable_units(units, blocked)),
        "n_blocked": len([u for u in units if u["unit_id"] in blocked
                          and not _exists(s3, bucket, result_key(u, RESULT_PREFIX))]),
        "blocked_units": blocked,
        # ★★ NULL, NOT ZERO — AND THE REASON LIVES HERE BECAUSE 0 IS A LEGAL GOOD VALUE AND null IS NOT.
        # This is the absent-vs-good-value collapse this repo has now hit five times. `0` is a REAL, correct
        # reading (a finished fleet with everything reaped is genuinely 0 live instances), so a reader — human
        # or code — has no way to tell a measured 0 from a fabricated one. There is no in-band value that can
        # carry "unmeasured", which is exactly why it must go out of band as null.
        # ⛔ Never "tidy" this to `len(live)`: above, `live` is degraded to `[]` on a blind read purely so the
        # S3 census can proceed, so `len(live)` would render a board we never saw as a confident zero — the
        # single most expensive shape of this bug, because a false zero on a RENTAL board reads as
        # "nothing is billing" and invites shutting off supervision on a fleet that is still charging.
        "live_instances": None if (unreadable or not key) else len(live),
        "_vast_unreadable": unreadable,
        "instance_states": states,
        "gpu_util": utils, "phases": phases,
        # status_msg is what distinguishes a host still PULLING the ~6 GiB image (documented ~20-40 min on
        # cheap 4090 hosts, and normal) from a container that is genuinely wedged — both show actual_status
        # "loading". Without it, "loading for 29 minutes" is unreadable either way.
        # ⚠ `machine_id` IS LOAD-BEARING HERE, NOT EXTRA DETAIL. Without it this artifact can report that
        # five hosts are dead and cannot report whether they are five machines or one — and those two
        # readings have opposite remedies. See `never_started_cohort`.
        "instances": [{"id": i.get("id"), "label": i.get("label"),
                       "machine_id": i.get("machine_id"), "status": i.get("actual_status"),
                       "cur_state": i.get("cur_state"), "status_msg": (i.get("status_msg") or "")[:200],
                       "gpu": i.get("gpu_name"), "gpu_util": _gpu_util(i),
                       "inet_down": i.get("inet_down"),
                       "dph": i.get("dph_total"), "age_min": _age_min(i)}
                      for i in live],
        # The adjudication itself, so the verdict survives in the committed trail rather than only in a CI
        # log's scrolled-off middle.
        "stopped_host_adjudication": cohort,
        "units": [{"unit_id": u["unit_id"],
                   "phase": unit_phase(
                       u, blocked,
                       has_result=_exists(s3, bucket, result_key(u, RESULT_PREFIX)),
                       phase_txt=_get_text(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/phase.txt")),
                   # The reason travels with the row. A reader holding only this file must be able to tell
                   # a permanently-excluded edge from a stalled one WITHOUT going to another artifact.
                   "blocked_why": (blocked.get(u["unit_id"]) or {}).get("why"),
                   # The committed-iteration census, carried into the artifact so the progress trail this
                   # file leaves is a record of ADVANCE and not just of phase labels.
                   "committed": (cur.get(u["unit_id"]) or {}).get("detail"),
                   "committed_scalar": (cur.get(u["unit_id"]) or {}).get("scalar"),
                   "committed_prev_scalar": (prev.get(u["unit_id"]) or {}).get("scalar"),
                   "ddg_bind_kcal": (_get_json(s3, bucket, result_key(u, RESULT_PREFIX)) or {})
                   .get("ddg_bind_kcal")}
                  for u in units],
        "realised_usd_so_far": ledger_cost(_load_ledger(s3, bucket))[0],
        "plan_usd_whole_tranche": cost_plan(len(units)),
    }
    with open("step1-fanout-progress.json", "w") as f:
        json.dump(snapshot, f, indent=2)
    print("[s1f] wrote step1-fanout-progress.json")

    # ── THE IN-FLIGHT BOARD ────────────────────────────────────────────────────────────────────────────
    # One row per unit, in the SAME renderer the ternary lane uses. Published as this lane's own fragment;
    # the merged all-lane board is then regenerated from every lane's fragment. This lane never writes
    # another lane's rows and never writes the ternary lane's file, which is the whole write-race
    # resolution — see `inflight_board.__doc__`.
    #
    # LAST, and inside a catch, on purpose: a board is a REPORT of the supervision this function performs,
    # and a reporting failure must never be able to take down the census, the guard or the reap above it.
    try:
        _prev_board = _get_json(s3, bucket, _BOARD_PREV_KEY) or {}
        _rows, _new_board_state = board_rows(
            s3, bucket, units, blocked, board_done, board_obs, live, unreadable, _prev_board)
        _note = ("%d of %d unit(s) landed; %d permanently excluded (rows below are the rest)."
                 % (n_done, len(units), len(blocked or {})))
        _frag, _board = _ifb.publish(_ifb.FANOUT, _rows, note=_note)
        # The counters are saved AFTER they are used, so "no advance since last time" compares this tick
        # against the previous TICK and never against something this tick just wrote.
        try:
            s3.put_object(Bucket=bucket, Key=_BOARD_PREV_KEY,
                          Body=json.dumps(_new_board_state, indent=2).encode())
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] board census save failed: {e}")
        print(f"[s1f] wrote {os.path.basename(_frag)} + {os.path.basename(_board)}")
        print()
        print("---- S1F-BOARD ----")
        print(_ifb.render(_rows), end="")
        print("---- END S1F-BOARD ----")
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] in-flight board not published ({type(e).__name__}: {e}) — the census above is "
              f"unaffected; the merged board will render this lane STALE rather than dropping it.")


_MAP_PATH = "step1-fanout-map.json"


def _write_map_guarded(out, s3, bucket):
    """Write `out` to `step1-fanout-map.json` (and its S3 mirror) UNLESS doing so would silently erase
    already-banked results — CLAUDE.md §4: an absent reading is not a reading of absence, and a completed
    result is exactly the kind of committed fact a live re-read must never be allowed to retract on its own
    say-so.

    ⛔ WHY THIS EXISTS. Measured 2026-08-27: a tick's S3 read came back with zero `ddg.json` objects under
    the results prefix while 10 other objects were still there — so the read was not a masked credential
    exception (`_get_json` returning None on ANY exception is a KNOWN separate hazard; this guard does not
    depend on distinguishing the two, because either way a completed count must never regress silently).
    The committed map had stood at 18/19 complete, unchanged, for 4h41m across dozens of prior ticks, then
    one tick overwrote it with 0/19 and nothing noticed for hours. That is the single-slot-artifact hazard
    AUT-PROP-009 already names for a sibling file, here with $73.79 of realised GPU spend as the stakes.

    A regression is `out["n_complete"] < on-disk n_complete`, read from the file THIS PROCESS is about to
    overwrite — never from a copy made earlier in the run, so a second collect in the same tick still sees
    the first collect's write. On a regression: the existing file is left untouched, the anomaly is written
    to a sibling alarm file (diffable, never silently retried away), and `_ARTIFACT_REGRESSION_DETECTED` is
    set so `main()` can fail the job loudly — the same escalation shape already used for a held-too-long
    market (`_MARKET_HOLD_ESCALATED`), because a false positive here (a real 18->3 loss, say) must reach a
    human exactly as fast as a real one.
    """
    existing_n_complete = None
    if os.path.exists(_MAP_PATH):
        try:
            with open(_MAP_PATH) as f:
                existing_n_complete = json.load(f).get("n_complete")
        except Exception as e:  # noqa: BLE001 — an unreadable existing file must not block a real write
            print(f"[s1f] could not read the existing {_MAP_PATH} to guard against regression "
                  f"({type(e).__name__}: {e}) — writing the new map anyway.")
    if (isinstance(existing_n_complete, int) and existing_n_complete > 0
            and out["n_complete"] < existing_n_complete):
        alarm = {
            "_what": "STEP 1 fan-out — a tick's re-read regressed n_complete and the write was REFUSED.",
            "utc": _utcnow(),
            "committed_n_complete": existing_n_complete,
            "this_ticks_n_complete": out["n_complete"],
            "action_taken": f"{_MAP_PATH} left UNCHANGED on disk; the S3 mirror was NOT overwritten either.",
            "what_to_check": "Was research/modalities/step1-fanout-map.json's results prefix genuinely "
                             "emptied in S3 (list the prefix directly), or was this one tick's read a fluke "
                             "(a transient AWS error, a credential or region change)? Do not clear this file "
                             "by re-running the tick — it will keep refusing until the real count recovers "
                             "or a human overwrites step1-fanout-map.json deliberately.",
        }
        print(f"::error::[s1f] REFUSING to overwrite {_MAP_PATH}: committed n_complete="
              f"{existing_n_complete}, this tick read n_complete={out['n_complete']}. See "
              f"step1-fanout-map-regression-alarm.json.")
        with open("step1-fanout-map-regression-alarm.json", "w") as f:
            json.dump(alarm, f, indent=2)
        globals()["_ARTIFACT_REGRESSION_DETECTED"] = True
        return
    with open(_MAP_PATH, "w") as f:
        json.dump(out, f, indent=2)
    s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_map.json", Body=json.dumps(out, indent=2).encode())


def mode_collect():
    """Assemble the map result from finished units, run the internal-consistency checks, reap dead hosts."""
    bucket, s3 = _require_bucket(), _s3()
    # ★★ TWO UNIT LISTS, ON PURPOSE, AND THE SPLIT IS THE POINT.
    #   `units`      = the MAP (19). It is what the artifact's scope, n_units, cycle closure and ranking are
    #                  about, and it must not grow when a replicate is requested — `_scope` says 19 edges,
    #                  and a denominator that silently moved is the exact defect `n_computable` was added
    #                  to fix.
    #   `lane`       = everything this lane may have RENTED, replicates included. Reaping, labels and the
    #                  live-instance bookkeeping below run off THIS one: a replicate host whose label is not
    #                  in `label_of` is never recognised as finished and bills until the age backstop.
    # The order is shared (lane_units() == default_units() + replicates), so the 0..18 indices — and
    # therefore every existing label — are identical in both.
    units = default_units()
    lane = lane_units()
    results, ddg_by_edge = [], {}
    for u in units:
        r = _get_json(s3, bucket, result_key(u, RESULT_PREFIX))
        if not r:
            continue
        results.append(r)
        ddg_by_edge[u["edge_id"]] = r["ddg_bind_kcal"]
    # Replicate results are collected separately and DELIBERATELY kept out of `ddg_by_edge`: cycle closure
    # and the ranking are statements about one self-consistent set of draws, and letting an r2 value
    # overwrite the r0 one would silently re-base the published map on a different sample.
    rep_units = [u for u in lane if u.get("replicate")]
    rep_results = [r for r in (_get_json(s3, bucket, result_key(u, RESULT_PREFIX)) for u in rep_units) if r]

    closure = cycle_closure(ddg_by_edge)
    # Read ONCE and reused for the counts and for the artifact field, so the number and the list it is
    # derived from can never disagree inside a single file.
    _blocked_now = _load_blocked(s3, bucket)
    out = {
        "_what": "STEP 1 FAN-OUT — cmpd19 congeneric relative binding free-energy map (RUNG 4, tranche 1)",
        "_scope": "19 map edges at their charge-conserving microstate leg, on the PRIMARY nr4a3_design "
                  "druggable frame. Charge-changing microstate legs and the conformer/paralogue frame axis "
                  "are separate tranches and were NOT run — see congeneric_fanout.plan().",
        "_claim_ceiling": "CONDITIONAL relative free energies given a HYPOTHESIZED cmpd19 pose (no solved "
                          "NR4A3 cocrystal) in ONE modeled opened conformer, single replicate per edge. "
                          "NOT affinities, NOT a selectivity readout, NOT a sensitivity range. Accuracy is "
                          "not established here — it rests on valA_mini + OpenFE's published benchmark for "
                          "this protocol.",
        # ★ WAS THIS LANE TOUCHED BY THE CHARGE-INHERITANCE DEFECT? ASKED AND ANSWERED, IN THE MAP ITSELF.
        # The ternary lane's banked legs were found to have sampled on charges inherited from their
        # pre-equilibrated pose file (OpenFE prefers user-supplied charges over the configured
        # partial_charge_method, and nothing stripped them before 2026-07-28T00:54Z). `nr4a3_rbfe._sdf_mol`
        # is SHARED with this lane, so the same question lands on these ddG values — and it is settled by
        # the staged pose file rather than argued from the code. Written here rather than into the JSON
        # because every autoscale tick REWRITES that file; a note added to the artifact would survive until
        # the next tick and no longer.
        "_charge_provenance": "MEASURED CLEAN, 2026-07-29 ($0, gpu-ternary-fep-vast.yml "
                              "task=charge-provenance): this lane stages a DOCKED sdf, and "
                              "s3://…/nr4a3-step1-fanout/stage/ligand/docked_nr4a3.sdf carries 17 records "
                              "and ZERO `atom.dprop.PartialCharge` tags — there was never anything here to "
                              "inherit, so no result on this map is affected. NB this lane persists NO setup "
                              "cache, so that pose file is the only stored artifact that can answer it: "
                              "there is no hybrid System to fall back on. Evidence: "
                              "research/modalities/charge-provenance-forensic.json → fanout_exposure.",
        "n_units": len(units), "n_complete": len(results),
        # ★ AND THE DENOMINATOR A READER SHOULD ACTUALLY QUOTE (2026-07-28). `n_units` is the MAP; the map
        # minus its permanent exclusions is what this lane can ever deliver, and the manuscript cites THIS
        # file. Leaving the subtraction to the reader is how "1 of 19" and "two computed edges" ended up in
        # the same paragraph of §2.9. Derived from `blocked_units` below, never typed.
        "n_computable": len(computable_units(units, _blocked_now)),
        "n_blocked": len([u for u in units if u["unit_id"] in _blocked_now
                          and u["unit_id"] not in {r["unit_id"] for r in results}]),
        # ★ EDGES THAT WILL NEVER COMPLETE, NAMED WITH THEIR REASON. This lane already keeps the
        # charge-changing legs enumerable "so the paper can state exactly which species were NOT computed and
        # why"; a blocked edge is the same obligation. A map that is silently 18 of 19 is a map nobody can
        # grade.
        "blocked_units": _blocked_now,
        "results": sorted(results, key=lambda r: r["unit_id"]),
        "cycle_closure": closure,
        "cycle_closure_note": "Internal consistency only: a closed cycle does not make the map accurate, but "
                              "an open one means at least one of its edges is unconverged or mis-mapped and "
                              "its ddG must not be quoted.",
        "ranking": rank_by_ddg(ddg_by_edge),
        "ranking_note": "anchor-rooted edges only; more negative = predicted tighter than cmpd19 in this "
                        "modeled conformer, conditional on the pose hypothesis.",
        # ★ THE REPLICATE AXIS, REPORTED SEPARATELY FROM THE MAP IT DOES NOT REPLACE. Present only once a
        # replicate has actually been requested, so this key appearing at all means somebody asked for one.
        **({"replicates": {
            "_what": "Independent repeats of NAMED edges (congeneric_fanout.replicate_units). Each is its "
                     "own unit with its own SEED and its own checkpoint prefix, so no two draws share a "
                     "trajectory. These values are NOT folded into cycle_closure or ranking above — those "
                     "remain the n=0 draw set.",
            "n_requested": len(rep_units), "n_complete": len(rep_results),
            "units": [u["unit_id"] for u in rep_units],
            "results": sorted(rep_results, key=lambda r: r["unit_id"]),
            "per_edge": _cf.replicate_stats(results + rep_results),
            "sd_note": "sd_kcal is the SAMPLE SD across independent draws (n-1), None below n=2. It is the "
                       "quantity CLAUDE.md §5 asks for; the per-draw ddg_bind_unc_kcal is a within-run MBAR "
                       "SE and answers a different question. Do not quote one as the other.",
        }} if rep_units else {}),
    }
    _write_map_guarded(out, s3, bucket)
    print(json.dumps({k: v for k, v in out.items() if k != "results"}, indent=2))
    print(f"\n[s1f] {len(results)}/{len(units)} units complete -> step1-fanout-map.json")

    key = os.environ.get("VAST_API_KEY")
    # ⚠ FROM HERE DOWN THE SUBJECT IS RENTED HOSTS, NOT THE MAP — so every one of these is built over `lane`.
    # `label_of` is how a live instance is matched to the unit it is running and therefore how "its result is
    # in S3, destroy it" is decided. Built over the 19 map units only, a replicate's label would resolve to
    # None, the finished branch would never fire, and the box would bill on to the age backstop.
    finished = {r["unit_id"] for r in (results + rep_results)}
    idx_of = {u["unit_id"]: i for i, u in enumerate(lane)}
    label_of = {f"{LABEL_PREFIX}{idx_of[u['unit_id']]:02d}-{u['ligand_b']}"[:64]: u["unit_id"] for u in lane}
    ledger = _load_ledger(s3, bucket)
    # Consecutive-terminal-observation state, in S3 so one CI run inherits what the previous one saw.
    _terminal = _get_json(s3, bucket, f"{RESULT_PREFIX}/_terminal_state.json") or {}
    _terminal_next = {}
    # The guard's OWN previous census (see `_idle_evidence` for why it cannot share monitor's).
    _idle_prev = _get_json(s3, bucket, f"{RESULT_PREFIX}/{_IDLE_PREV_KEY_SUFFIX}") or {}
    _idle_next, _idle_rows = {}, []
    unit_by_label = {f"{LABEL_PREFIX}{idx_of[u['unit_id']]:02d}-{u['ligand_b']}"[:64]: u for u in lane}
    for i in (_live_instances(key) if key else []):
        lab, st = i.get("label"), (i.get("actual_status") or "")
        age_min = _age_min(i)
        # FREEZE billed minutes BEFORE the reap. After the DELETE the instance is unreadable, so an
        # unrecorded final age is lost forever and the realised-cost total silently under-reports.
        _row = (ledger.get("rentals") or {}).get(str(i.get("id")))
        if _row is not None:
            _row["billed_min"] = max(int(_row.get("billed_min") or 0), int(age_min))
            _row["last_seen_utc"] = _utcnow()
        why = None
        if label_of.get(lab) in finished:
            why = "result in S3"
        elif st in ("exited", "offline", "error"):
            # ⚠ A TRANSIENT `exited` IS NOT A FAILURE, and this reaper became dangerous the moment it moved
            # onto a 20-minute cron. s1f-04 read `exited` at 10 minutes in wave 1 and came back `running` on
            # its own (lane record section 8). Destroying on a single observation would throw away a host
            # that was about to recover — survivable, because the checkpoint resumes, but it costs a boot and
            # a fresh rental EVERY time it misfires, across a 19-host fleet, unattended, all night.
            #
            # So a terminal state must be seen on TWO CONSECUTIVE ticks before it is believed. The finished
            # case above is unaffected: a unit with its ddg.json in S3 is destroyed on sight, because there
            # the evidence is the result itself and not the instance's mood.
            seen = int((_terminal.get(str(i.get("id"))) or {}).get("ticks", 0)) + 1
            _terminal_next[str(i.get("id"))] = {"ticks": seen, "state": st, "utc": _utcnow()}
            if seen < 2:
                print(f"[s1f] {i.get('id')} ({lab}) reads {st} — first observation, NOT reaping. A transient "
                      f"`exited` recovered on its own in wave 1; two consecutive ticks are required.")
                continue
            why = f"terminal state {st} on {seen} consecutive checks"
        elif age_min > REAP_AGE_MIN:
            why = f"age {age_min} min > {REAP_AGE_MIN}"
        # ---- THE ANTI-IDLE GUARD. Reaction time from the 15 h age backstop above to ~15 min of silence. ----
        #
        # This clause is what 45996071 needed and did not have: it crash-looped on a dead credential for over
        # an hour at $0.2497/hr with 0 % GPU while `actual_status` stayed `running`, so neither the terminal
        # clause nor the age clause could see it. It is placed AFTER both on purpose — a box those clauses
        # already condemn does not need a second opinion, and the cheaper checks should not pay for this
        # one's S3 reads.
        #
        # ★ IT CAN ONLY EVER DESTROY, SO EVERY AMBIGUITY MUST RESOLVE TO DOING NOTHING, and it does: the
        # policy returns COLD_START / UNKNOWN / WATCHING for a young box, an unreadable listing, a container
        # that never marked a phase inside its grace, or a quiet-but-writing host — and `should_destroy` is
        # False for all of them. GPU idleness NEVER condemns; only a measured absence of WRITES does. That is
        # the inviolable rule, because a step 1 complex leg is legitimately at 0 % GPU for its whole stage +
        # parameterise + minimise cold start and reaping that would be a self-inflicted copy of the incident.
        elif unit_by_label.get(lab):
            try:
                ev, scalar = _idle_evidence(s3, bucket, unit_by_label[lab], i,
                                            (_idle_prev.get(lab) or {}).get("scalar"))
                verdict, reason = _vig.classify_idle(**ev)
                if scalar >= 0:
                    _idle_next[lab] = {"scalar": scalar, "utc": _utcnow()}
                _idle_rows.append({"instance": i.get("id"), "label": lab, "verdict": verdict,
                                   "why": reason, "evidence": ev})
                print(f"[s1f] idle-guard {i.get('id')} ({lab}): {verdict} — {reason}")
                if _vig.should_destroy(verdict):
                    why = f"idle guard: {verdict} — {reason}"
            except Exception as e:  # noqa: BLE001 — a guard that raises must not take the whole reap down
                print(f"[s1f] idle-guard evidence failed for {lab}: {type(e).__name__}: {e} — NOT reaping")
        if not why:
            continue
        try:
            _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
            print(f"[s1f] reaped {i.get('id')} ({lab}): {why}")
            if _row is not None:
                _row["reaped_utc"], _row["reaped_why"] = _utcnow(), why
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] reap {i.get('id')} failed: {e}")
    _save_ledger(s3, bucket, ledger)
    # Rewritten, not merged: an instance absent from this pass is gone or recovered, and either way its
    # streak is over. A streak that persisted across a recovery would reap a healthy host on its next blip.
    try:
        s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_terminal_state.json",
                      Body=json.dumps(_terminal_next, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] terminal-state save failed: {e}")
    # The guard's census is written AFTER every verdict, so "did it advance since last check" compares
    # against the previous CHECK and never against something this pass just wrote.
    try:
        s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/{_IDLE_PREV_KEY_SUFFIX}",
                      Body=json.dumps(_idle_next, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] idle-guard census save failed: {e}")
    # ★ A GUARD THAT REPORTS SUCCESS WHILE MEASURING NOTHING IS THE SHAPE THIS REPO KEEPS PAYING FOR, so the
    # readout says what it OBSERVED, not merely what it destroyed. `log_age_min: null` on every row means the
    # heartbeat is not landing and the WEDGED channel is silently disabled — visible here, rather than
    # discovered on the next expensive wedge.
    out["idle_guard"] = _idle_rows
    if _idle_rows and all(r["evidence"].get("log_age_min") is None for r in _idle_rows):
        print("[s1f] ⚠ idle guard: NOT ONE live unit has a readable run.log. The log-silence channel is "
              "measuring nothing — check that the pipeline's heartbeat is running before trusting any "
              "verdict above.")

    # ---- realised spend against the estimate -------------------------------------------------------------
    # Reported HERE, at collect, and written into the map artifact — not left to be reconstructed later. The
    # ~4x cost error this lane already made was possible precisely because the realised number lived only in
    # a memory of what a few instances had cost.
    total, n_rent, rows, unpriced = ledger_cost(ledger)
    plan_all, plan_run = cost_plan(len(units)), cost_plan(max(1, len(results)))
    print(f"\n[s1f] REALISED SPEND: ${total} over {n_rent} rental(s)"
          + (f"  ⚠ {unpriced} rental(s) carried no usable rate and contribute 0" if unpriced else ""))
    print(f"[s1f] against plan: whole 19-unit tranche ${plan_all}; "
          f"{len(results)} completed unit(s) would plan at ${plan_run}")
    for r in rows:
        print(f"[s1f]   {r['instance']:>12} {str(r['unit_id'])[:44]:44s} machine={r['machine_id']} "
              f"${r['rate_usd_h']}/hr x {r['billed_h']}h = ${r['usd']}")
    out["realised_usd"] = total
    out["realised_rentals"] = rows
    out["plan_usd_whole_tranche"] = plan_all
    out["cost_note"] = ("realised = recorded BID $/hr x observed billed hours (Vast charges the bid up to the "
                        "machine's on-demand price). Plan = vast_cost_model.LADDER_REFERENCE_GPU_H repriced "
                        "at the best-10-mean $/reference-GPU-hour from vast-ladder-repricing.json.")
    _write_map_guarded(out, s3, bucket)


def mode_diag():
    """Root-cause a failed/exited unit: its S3 leg log if one was shipped, plus the container stdout pulled
    straight off the Vast instance (which survives even when the pipeline died before uploading anything).

    Output is ALSO written to step1-fanout-diag.txt and committed back to the branch: a job log is only
    readable from its tail, and a diagnostic dump is long enough that the part that matters never survives
    there. DIAG_UNIT selects a unit by substring (default: every LAUNCHED unit that has not finished)."""
    bucket, s3 = _require_bucket(), _s3()
    out_lines = []

    def emit(msg):
        print(msg, flush=True)
        out_lines.append(str(msg))

    key = os.environ.get("VAST_API_KEY")
    want = (os.environ.get("DIAG_UNIT") or "").strip()
    # Default scope is units that have actually BEEN launched (a phase marker in S3, or a live instance) and
    # are not finished. Without that, diag also reports every unit of the not-yet-launched later waves as
    # "gone", which buries the one unit that actually needs diagnosing.
    all_units = lane_units()
    idx_all = {u["unit_id"]: i for i, u in enumerate(all_units)}

    def _launched(u):
        lbl = f"{LABEL_PREFIX}{idx_all[u['unit_id']]:02d}-{u['ligand_b']}"[:64]
        return bool(_get_text(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/phase.txt")) or lbl in _labels_live

    _labels_live = {(i.get("label") or "") for i in (_live_instances(key) if key else [])}
    units = [u for u in all_units
             if (want in u["unit_id"] if want
                 else (_launched(u) and not _exists(s3, bucket, result_key(u, RESULT_PREFIX))))]
    if not units:
        emit("[s1f-diag] nothing to diagnose: no launched-and-unfinished unit "
             + ("matching DIAG_UNIT=" + want if want else "(later waves are not launched yet)"))
    live = {(i.get("label") or ""): i for i in (_live_instances(key) if key else [])}
    idx_of = idx_all

    for u in units:
        uid = u["unit_id"]
        label = f"{LABEL_PREFIX}{idx_of[uid]:02d}-{u['ligand_b']}"[:64]
        phase = _get_text(s3, bucket, f"{RESULT_PREFIX}/{uid}/phase.txt")
        # Every launched unit is dumped, not only the terminal ones. The container stdout carries the
        # per-iteration sampling RATE, which is the number the whole cost model rests on — and reading it off
        # ONE preempted host cannot distinguish a slow host from a systematically slow system. Bounded by the
        # launched set (<= FANOUT_WIDTH), so this stays cheap.
        emit(f"\n[s1f-diag] ===== {uid} (label {label}) phase={phase} "
             f"vast_status={live.get(label, {}).get('actual_status', 'gone')} =====")
        for leg in ("complex", "solvent"):
            txt = _get_text(s3, bucket, f"{RESULT_PREFIX}/{uid}/{leg}.log")
            if txt:
                emit(f"[s1f-diag] --- S3 {leg}.log (tail) ---\n{txt[-4000:]}")
        inst = live.get(label)
        if inst and key:
            from nrv04_vast_launch import _vast_instance_logs
            emit(f"[s1f-diag] --- Vast container stdout for instance {inst.get('id')} ---")
            emit(_vast_instance_logs(key, inst.get("id")))
        elif not inst:
            emit("[s1f-diag] instance is gone from Vast — container stdout unrecoverable; the S3 leg log "
                 "above is the only record (this is why the leg now uploads its log even on failure)")

    # ★★ THE ATTEMPT COUNT, NOT JUST THE LATEST ATTEMPT (2026-07-28). Everything above reports the CURRENT
    # state of one unit: the tail of the last leg log and the instance that is running now. That is exactly
    # the reading that let `cw_bio_primary_amide` be re-placed thirteen times — each dump showed one clean
    # NaN traceback and nothing about the twelve before it, so every look said "unlucky host" and none said
    # "this is the thirteenth". The per-attempt archive answers it for $0 and is appended here so the
    # diagnosis and its history arrive in the same artifact.
    try:
        import step1_nan_forensics as _nf
        # EVERY unit, not the diag's (deliberately narrow) scope: the comparison that matters is the
        # failing unit against the ones that REACHED A ddG, and those are exactly the units `diag` filters
        # out. A geometry band computed only over the units still in trouble compares nothing.
        _rows = _nf.collect(all_units)
        if _rows:
            emit("\n" + _nf.render(_rows, _nf.geometry_comparison(_rows)))
            with open("step1-nan-forensics.json", "w") as f:
                json.dump({"_what": "per-attempt forensics emitted by `diag`", "units": _rows,
                           "geometry_comparison": _nf.geometry_comparison(_rows)}, f, indent=2, default=str)
    except Exception as e:  # noqa: BLE001 — an evidence hook must never break the diagnostic it decorates
        emit(f"[s1f-diag] attempt forensics unavailable: {type(e).__name__}: {e}")

    with open("step1-fanout-diag.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    print(f"[s1f-diag] wrote step1-fanout-diag.txt ({len(out_lines)} blocks)")


def mode_block():
    """BLOCK a unit from ever being launched again, with a mandatory reason. Rents nothing, destroys nothing.

    THE DIFFERENCE FROM `reap`, which is the whole point: `reap` condemns a HOST — this machine is bad, rent
    another. `block` condemns a UNIT — no host will help, stop buying them. Applying the wrong one costs
    real money in opposite directions: reaping a host for a unit-level defect rents a fresh box to fail
    identically, and blocking a unit for a host-level defect abandons a perfectly good edge.

    The first user is `e_zaienne_cmpd19__cw_bio_nmethyl_amide__neutral__neutral`, whose complex leg aborts
    rc=1 on a provably-degenerate atom map that no available mapper can fix (LOMAP element_change=False 17,
    element_change=True 19, Kartograf 18, against a provable floor of 20; both LOMAP budgets identical at
    0.01 s, so the MCS timeout is measured NOT to be the mechanism — step1-map-diag.json). That is a fact
    about the mappers on that edge, not about any rented host, so it is a block and not a reap.

    UNBLOCKING IS DELIBERATE AND MANUAL (`FANOUT_UNBLOCK=1`): if a mapper ever reaches the floor for this
    edge, the block should be lifted by someone who has seen that measurement, not by a tick that forgot."""
    bucket, s3 = _require_bucket(), _s3()
    uid = (os.environ.get("BLOCK_UNIT") or "").strip()
    why = (os.environ.get("BLOCK_REASON") or "").strip()
    if not uid:
        raise SystemExit("[s1f] BLOCK_UNIT is required (a unit_id, or a substring matching exactly one)")
    known = [u["unit_id"] for u in lane_units()]
    # A SUBSTRING IS ACCEPTED ONLY WHEN IT IS UNAMBIGUOUS. The workflow's selector input is a substring
    # everywhere else, so demanding the full id here would be a trap; but resolving an ambiguous one to
    # "the first match" would block an edge nobody named. Exact match wins outright.
    if uid not in known:
        hits = [k for k in known if uid in k]
        if len(hits) != 1:
            raise SystemExit(f"[s1f] {uid!r} matches {len(hits)} fan-out units ({hits[:5]}); refusing to "
                             f"guess which edge to stop computing")
        print(f"[s1f] {uid!r} -> {hits[0]}")
        uid = hits[0]
    doc = _get_json(s3, bucket, f"{RESULT_PREFIX}/{_BLOCKED_KEY_SUFFIX}") or {"units": {}}
    doc.setdefault("units", {})
    if os.environ.get("FANOUT_UNBLOCK") == "1":
        removed = doc["units"].pop(uid, None)
        print(f"[s1f] unblocked {uid} (was: {removed})")
        # ★★ UNBLOCKING IS THE GESTURE THAT MEANS "THE CAUSE IS FIXED", SO IT RE-ARMS THE BREAKER TOO
        # (2026-07-29). Without this, lifting a block achieves nothing for any unit that has already burned
        # `leg_failure_breaker.DEFAULT_THRESHOLD` hosts: the launcher would simply hold it on the attempt
        # count instead, and the two guards would look like one broken one. The re-arm is an OFFSET, not a
        # delete — the archive is the evidence that this unit was bought 25 times, it is cited in the block
        # reason and in the manuscript, and a counter reset must not cost the record.
        _n_now = _attempt_count(s3, bucket, uid)
        if _n_now is None:
            print(f"[s1f] ⚠ could not read {uid}'s attempt archive, so the breaker baseline was NOT moved. "
                  f"The unblock stands, but the failure breaker may still hold this unit — re-run this "
                  f"mode once the bucket reads cleanly.")
        else:
            _bl = _get_json(s3, bucket, f"{RESULT_PREFIX}/{_BREAKER_BASELINE_KEY_SUFFIX}") or {}
            _bl.setdefault("units", {})
            # UNION, never overwrite: another lane tick may have re-armed a different unit between this
            # read and this write, and a whole-document replace would silently drop it.
            _bl["units"] = {**(_bl.get("units") or {}), uid: _n_now}
            _bl["_what"] = ("attempts already spent per unit at the moment someone declared its cause "
                            "fixed. `breaker_decision` counts only attempts made SINCE this baseline, so "
                            "the archive stays whole and the breaker still re-arms.")
            s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/{_BREAKER_BASELINE_KEY_SUFFIX}",
                          Body=json.dumps(_bl, indent=2).encode())
            print(f"[s1f] failure-breaker re-armed for {uid}: baseline set to {_n_now} archived attempt(s); "
                  f"only failures after this count towards the threshold. The archive is untouched.")
    else:
        if not why:
            raise SystemExit("[s1f] BLOCK_REASON is required — a block with no stated reason is an edge that "
                             "silently vanishes from the map, which is the failure mode this guards against")
        # ★ A REASON THAT IS OBVIOUSLY AN ATTEMPT TO UNBLOCK MUST NOT BLOCK (2026-07-29). The reason arrives
        # from the same workflow input in both directions, so "unblock" typed into it is unambiguous intent
        # — and taking it literally would re-block the unit AND overwrite its evidenced reason with the word
        # "unblock", losing the record. Refusing costs one re-dispatch; accepting costs the reason.
        if why.strip().lower() in ("unblock", "unblocked", "un-block", "clear", "lift"):
            raise SystemExit(f"[s1f] BLOCK_REASON={why!r} reads as a request to UNBLOCK, not as a reason to "
                             f"block. Refusing rather than overwriting {uid}'s recorded reason. To lift a "
                             f"block set FANOUT_UNBLOCK=1 (the workflow does this when the reason input is "
                             f"exactly 'unblock').")
        doc["units"][uid] = {"why": why, "evidence": os.environ.get("BLOCK_EVIDENCE") or None,
                             "utc": _utcnow()}
        print(f"[s1f] blocked {uid}: {why}")
    doc["_what"] = ("units this lane will NOT rent a host for. A block is about the UNIT (no host can help); "
                    "an exclusion in _excluded_machines.json is about the HOST. Both are durable in S3 so a "
                    "tick with no agent awake inherits them.")
    s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/{_BLOCKED_KEY_SUFFIX}",
                  Body=json.dumps(doc, indent=2).encode())
    print(json.dumps(doc, indent=2))
    return 0


def mode_stop():
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[s1f] VAST_API_KEY required to stop")
    live = _live_instances(key)
    print(f"[s1f] destroying {len(live)} s1f-* instances")
    for i in live:
        try:
            _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
            print(f"[s1f] destroyed {i.get('id')} ({i.get('label')})")
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] destroy {i.get('id')} failed: {e}")


def mode_reap():
    """CONDEMN a host: destroy the selected s1f-* instance(s) AND blacklist their machines for this lane.

    WHY THIS IS NOT `stop`. `stop` is cleanup — it destroys and says nothing about the machine, so the very
    next `launch` is free to rent the same box back. That is correct for "I am done spending" and wrong for
    "this host is bad", and the difference is the whole content of CLAUDE.md's Vast rule: a host that never
    starts (or never advances) has infinite realised $/ns, is therefore invisible to $/ns ranking, and
    without an explicit exclusion keeps winning selection and keeps failing. The lane already has the
    exclusion set and `launch` already consults it; what was missing was any way for an operator who has
    just diagnosed a bad host to put one in it. Only the starved-host guard could, and only for the single
    symptom it measures.

    WHAT THIS DOES NOT DO: relaunch. Reaping and re-renting are deliberately two dispatches so the exclusion
    is durable in S3 *before* anything picks a host, and so a reap can never be the thing that silently
    starts spending. Follow it with `launch_confirm`.

    SELECTOR IS MANDATORY. `stop`'s blank-means-everything default is a documented footgun on a shared
    account; a mode that also writes a permanent blacklist must not inherit it.
    """
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[s1f] VAST_API_KEY required to reap")
    want = (os.environ.get("DIAG_UNIT") or os.environ.get("FANOUT_ONLY") or "").strip()
    if not want:
        raise SystemExit("[s1f-reap] refusing a blank selector: name the instance id or a label substring. "
                         "Blank would condemn every host this lane is running and blacklist their machines.")
    why = (os.environ.get("REAP_REASON") or "").strip()
    if not why:
        raise SystemExit("[s1f-reap] REAP_REASON is required — an exclusion with no recorded cause is a "
                         "machine nobody can ever justify un-excluding.")
    bucket, s3 = _require_bucket(), _s3()
    live = _live_instances(key) or []
    sel = [i for i in live if want == str(i.get("id")) or want in (i.get("label") or "")]
    if not sel:
        print(f"[s1f-reap] nothing matches {want!r} among {[i.get('label') for i in live]} — no action")
        return
    for i in sel:
        iid, mid = i.get("id"), i.get("machine_id")
        try:
            _vast_request("DELETE", f"/instances/{iid}/", key)
            print(f"[s1f-reap] destroyed {iid} ({i.get('label')}) on machine {mid}")
        except Exception as e:  # noqa: BLE001
            print(f"[s1f-reap] destroy {iid} failed: {e} — NOT recording an exclusion for a box that may "
                  f"still be billing; fix the destroy first")
            continue
        if mid is None:
            print(f"[s1f-reap] {iid} has no machine_id in the listing — destroyed, but nothing to exclude")
        elif _record_exclusion(s3, bucket, mid, why, unit=i.get("label")):
            print(f"[s1f-reap] machine {mid} added to the lane exclusion set: {why}")
        else:
            print(f"[s1f-reap] machine {mid} was already excluded (or the write failed) — see the log above")
    print(f"[s1f-reap] reaped {len(sel)} instance(s). Re-rent with launch_confirm; the exclusion is in S3 "
          f"and binds it with no agent awake.")


_MODES = [("PLAN", mode_plan), ("STAGE", mode_stage), ("PRECHECK", mode_precheck), ("LAUNCH", mode_launch),
          ("COLLECT", mode_collect), ("MONITOR", mode_monitor), ("DIAG", mode_diag), ("REAP", mode_reap),
          ("BLOCK", mode_block), ("STOP", mode_stop)]


def main():
    for flag, fn in _MODES:
        if os.environ.get(flag) == "1":
            rc = fn()
            # A HELD-TOO-LONG fan-out exits NON-ZERO on purpose. `::error::` alone is an annotation nobody
            # opens; a failed job is what fires GitHub's own workflow-failure notification, which is the
            # alert path that does not depend on an agent or a session. Only the ESCALATED hold does this —
            # a routine hold is a normal, expected outcome and stays green.
            if _MARKET_HOLD_ESCALATED:
                raise SystemExit(2)
            # Same shape, different trigger: `_write_map_guarded` refused to let a re-read regress
            # `n_complete` over already-banked results. That refusal must reach a human as fast as a real
            # loss would, so it fails the job rather than staying a quiet ::error:: annotation.
            if _ARTIFACT_REGRESSION_DETECTED:
                raise SystemExit(2)
            return rc
    return mode_plan()


if __name__ == "__main__":
    main()
