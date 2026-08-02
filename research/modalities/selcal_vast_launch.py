#!/usr/bin/env python3
"""ENDPOINT-MD SENSITIVITY CONTROL — the Vast launcher, its price gate, its supervision and its collector.

One Vast instance per unit, exactly as the NR-V04 endpoint-MD lane runs: clone the repo, extract the pre-packed
conda MD env, stage the leg from its PINNED co-fold model in S3, run `nrv04_covalent_md` under the auto-teardown
wrapper, upload the leg JSON, self-destroy.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
WHAT IS REUSED, AND WHY IT IS REUSED RATHER THAN FORKED (CLAUDE.md rule 1)
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
  * `nrv04_vast_launch.endpoint_md_resources` / `buy_ceiling_usd_per_ns` / `VAST_IMAGE` / `MDENV_KEY` /
    `presign_env_tarball` — the endpoint-MD host profile and the binding per-offer buy line. A second spec
    would be a second chance to rent without a ceiling, which is exactly how that lane rented at any price
    until 2026-07-31.
  * `relaunch_market_gate` — the `$/ns` gate. Every rental this lane makes faces it: fan-out, single pilot,
    resume. *A relaunch is a NEW PURCHASE, not a continuation.*
  * `leg_failure_breaker` — the repeated-failure brake, counting HOST-WRITTEN attempt markers.
  * `nrv04_covalent_md` — the MD driver, verbatim. **That is the experiment**: a sensitivity control that ran
    a modified driver would calibrate a readout the program does not use.
  * `inflight_usd_per_ns` — the `$/ns` cell, so a row this lane prints is graded by the same rule as every
    other lane's.

WHAT IS NEW HERE is only the staging: the chain contract (`selcal_stage`), because a ~121-residue bromodomain
cannot be identified by the NR4A assembler's 254-residue rule.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
THE LADDER — cheapest-decisive-first, and the middle rung is not skippable
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
`dry` -> `stage_prep` -> `cofold` -> `cofold_collect` -> `stage_test` -> `smoke` -> `leg` -> `launch`.

⚠ `smoke` GREEN DOES NOT AUTHORISE `launch`. The smoke runs 500 steps with no equilibration and, more to the
point, exercises a different code path in the driver — it cannot catch an MD-environment fault. The single real
leg can, and has elsewhere: a `PYTHONPATH` leak once imported a base container's numpy 1.x into a numpy-2 env,
invisible to smoke. Nothing is wasted by the extra rung — per-unit checkpoints mean the fan-out resumes from
whatever the shakeout produced.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import selcal_panel as SP  # noqa: E402
from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend, s3_checkpoint_uri  # noqa: E402
from nrv04_vast_launch import (  # noqa: E402  — the endpoint-MD host profile and buy line, imported not forked
    MDENV_KEY, REPO, VAST_IMAGE, buy_ceiling_usd_per_ns, endpoint_md_resources, presign_env_tarball,
)

HERE = os.path.dirname(os.path.abspath(__file__))
BUCKET = os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
LANE = "selcal"

#: Minimum seconds between the watch loop's automatic `launch` re-placements. NOT politeness — a host rented
#: seconds ago is not yet on the account, so a shorter interval would see its unit as still needing one and
#: buy a second host for the same leg. 10 min is ~3 watch ticks, comfortably past the ~1-2 min a rental takes
#: to register, and far below the ~45 min a leg runs, so a real gap is never left standing for long.
_REPLACE_MIN_S = float(os.environ.get("SELCAL_REPLACE_MIN_S", "600"))

MARKET_READOUT = os.path.join(HERE, "selcal-market-hold.json")
GATE_RECORD = os.path.join(HERE, "selcal-gate-record.json")
PRICE_LEDGER = os.path.join(HERE, "selcal-price-ledger.json")
COLLECT_READOUT = os.path.join(HERE, "selcal-collect.json")
VERDICT_READOUT = os.path.join(HERE, "selcal-verdict.json")
COFOLD_CENSUS = os.path.join(HERE, "selcal-cofold-census.json")
STAGE_TEST_READOUT = os.path.join(HERE, "selcal-stage-test.json")
REAP_READOUT = os.path.join(HERE, "selcal-reap.json")
HANDLES = os.path.join(HERE, "selcal-handles.json")

#: The co-fold host's image and the pinned Boltz. Both imported from the lane that already proved them on
#: Vast, so a Boltz bump moves the two together instead of leaving this one on a version nobody re-validated.
from nrv04_vast_launch import BOLTZ_SPEC, COFOLD_IMAGE  # noqa: E402,E401


def exclude_machines():
    """Machine ids this dispatch must not rent, from `$SELCAL_EXCLUDE_MACHINES`.

    ★★ BOUNDED TO THE CALL, ON PURPOSE, AND IT IS NOT A BLACKLIST. CLAUDE.md §6 RETIRED the durable,
    cross-lane, never-ageing host set — not because any entry was wrong but because nothing could ever retire
    one, so it only ratcheted the board narrower. What it KEPT is the bounded form: an exclusion learned by a
    wave and discarded with it. This is that, made explicit for an operator who has just MEASURED a bad host:
    it lives in one dispatch's env, is recorded in that dispatch's gate record, and is gone on the next one.
    Re-learning a bad host costs one FREE failed submit; over-excluding costs capacity on every lane,
    silently.

    The measurement that motivated it (2026-08-01): three consecutive co-fold rentals — 46504822, 46507225,
    46507228 — all landed on machine 9427 and all were stopped by the host within ~4-11 min, one of them
    mid-way through downloading the Boltz weights with the MSA already complete in S3. The one rental on a
    different machine (46506726) ran normally until it was stopped deliberately."""
    raw = (os.environ.get("SELCAL_EXCLUDE_MACHINES") or "").replace(" ", "")
    return tuple(m for m in raw.split(",") if m)


def _utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _write(path, doc):
    try:
        with open(path, "w") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        return True
    except OSError as e:  # noqa: BLE001
        print("[selcal] readout not written to %s: %s" % (path, e), flush=True)
        return False


def _s3_list(s3, bucket, prefix, suffix=None, limit=None):
    keys, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if token:
            kw["ContinuationToken"] = token
        page = s3.list_objects_v2(**kw)
        for o in page.get("Contents") or []:
            if suffix and not o["Key"].endswith(suffix):
                continue
            keys.append(o["Key"])
            if limit and len(keys) >= limit:
                return keys
        if not page.get("IsTruncated"):
            return keys
        token = page.get("NextContinuationToken")


# =============================================================================================================
# the on-host pipelines
# =============================================================================================================
#: The MD leg. Structurally the NR-V04 endpoint-MD pipeline — same image, same pre-packed env, same driver,
#: same continuous log sync — with the staging block replaced, because this panel's chain identification is
#: contract-verified rather than residue-count-guessed.
#:
#: ★★ THE PHASE MARKER CARRIES THE HOST THAT WROTE IT. A marker that outlives its host reads as a fact about
#: the CURRENT rental and is not — that misreading has already cost this program a diagnosis. `$CONTAINER_ID`
#: and the attempt timestamp go into every mark, so `status` can say "this phase was written by the box that
#: is up now" or "this phase is a fossil from a dead attempt", instead of implying the first.
_MD_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
command -v curl >/dev/null 2>&1 || { apt-get update -q || true; apt-get install -y -q --no-install-recommends curl ca-certificates || true; }
if [ ! -x /opt/mamba/envs/md/bin/python ]; then
  mkdir -p /opt/mamba/envs/md
  curl -Ls "$ENV_TARBALL_URL" | tar xz -C /opt/mamba/envs/md
  /opt/mamba/envs/md/bin/conda-unpack || true
fi
export PATH=/opt/mamba/envs/md/bin:$PATH
PY=/opt/mamba/envs/md/bin/python
AWS=/opt/mamba/envs/md/bin/aws
_ATS=$(date -u +%Y%m%dT%H%M%SZ)
_HOST="instance=${CONTAINER_ID:-unknown} attempt=$_ATS"
mark() { echo "$1 $(date -u +%FT%TZ) $_HOST" | $AWS s3 cp - "$RESULT_S3/phase.txt" || echo "[mark] WARN could not write phase '$1'"; }
echo "preflight $(date -u +%FT%TZ) $_HOST" | $AWS s3 cp - "$RESULT_S3/phase.txt" || {
  echo "[preflight] FATAL cannot write to $RESULT_S3 — refusing to run an unmonitorable leg"; exit 4; }
exec > >(tee -a /tmp/run.log) 2>&1
( while true; do $AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true; sleep 45; done ) &
LOGSYNC_PID=$!
trap '$AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true' EXIT
# ARCHIVE THE PREVIOUS ATTEMPT'S LOG BEFORE THIS ONE OVERWRITES IT, then write the attempt marker the failure
# breaker counts. Separate prefixes on purpose: `count_attempts` counts OBJECTS under attempts/, so a second
# object per attempt there would fire the breaker at half its threshold.
$AWS s3 cp "$RESULT_S3/run.log" "$ATTEMPT_LOG_S3/run-$_ATS.log" --only-show-errors >/dev/null 2>&1 \
  && echo "[attempt] archived the previous attempt's run.log" \
  || echo "[attempt] no previous run.log (first attempt)"
echo "attempt $(date -u +%FT%TZ) instance=${CONTAINER_ID:-unknown}" | $AWS s3 cp - "$ATTEMPT_S3/run-$_ATS.log" \
  || echo "[attempt] WARN attempt marker not archived — the failure breaker will undercount"
mark env-ready
rm -rf Rare-cancers-*
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
mark cloned
mkdir -p /tmp/in /tmp/out /tmp/cofold /tmp/inputs
export INPUT_DIR=/tmp/in OUTPUT_DIR=/tmp/out CKPT_DIR=/tmp/out
# --- stage from the PINNED co-fold model + the chain CONTRACT built on CI --------------------------------
$AWS s3 cp "$COFOLD_INPUTS_S3" /tmp/inputs/ --recursive --only-show-errors
$AWS s3 cp "$COFOLD_PREFIX_S3" /tmp/cofold/ --recursive --exclude '*' --include '*_model_0.cif' --only-show-errors
export COFOLD_CIF=$(find /tmp/cofold -name '*_model_0.cif' | sort | head -1)
test -n "$COFOLD_CIF" || { echo "no co-fold CIF under $COFOLD_PREFIX_S3"; exit 3; }
# EXACTLY ONE. Two would mean the model-seed pin failed and the leg would silently start from an unknown
# model, corrupting the model-level means the verdict is computed from. Fail, never guess.
test "$(find /tmp/cofold -name '*_model_0.cif' | wc -l)" = 1 || { echo "expected exactly 1 co-fold CIF under the pinned prefix $COFOLD_PREFIX_S3"; exit 3; }
$PY -c "
import json, os, sys
sys.path.insert(0, '.')
import selcal_stage as ST
man = json.load(open('/tmp/inputs/cofold-inputs.json'))
contract = man['chain_contract'][os.environ['SELCAL_SYSTEM']]
res = ST.assemble_unit(os.environ['COFOLD_CIF'], os.environ['LEG_ID'], contract, os.environ['INPUT_DIR'],
                       reference_json='/tmp/inputs/selcal-reference-selectivity.json')
print('[stage]', json.dumps(res['chains'])[:400])
audit = ST.cofold_input_audit(os.path.join(res['out'], 'complex.pdb'))
json.dump(audit, open(os.path.join(res['out'], 'input_audit.json'), 'w'), indent=2)
print('[audit]', json.dumps(audit))
if not audit['ok']:
    raise SystemExit('[audit] REFUSING to run: ' + audit['why'])
"
$AWS s3 cp "$INPUT_DIR/$LEG_ID/input_audit.json" "$RESULT_S3/input_audit.json" --only-show-errors || true
$AWS s3 cp "$INPUT_DIR/$LEG_ID/chains.json" "$RESULT_S3/chains.json" --only-show-errors || true
mark staged
mark md-running
$PY autoteardown.py $PY nrv04_covalent_md.py
mark md-done
$AWS s3 cp /tmp/out/ "$RESULT_S3/" --recursive --exclude '*' --include 'leg_*.json' --only-show-errors
kill $LOGSYNC_PID 2>/dev/null || true
$AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors || true
mark uploaded
"""

# ★★ IT TALKS FROM THE FIRST SECOND, AND THAT IS A FIX, NOT A STYLE CHOICE (measured 2026-08-01, instance
# 46504822). The first version of this pipeline was SILENT until after `pip install` — apt redirected to
# /dev/null, pip on `--quiet` — so when the host went `cur_state: stopped` four minutes in, the container log
# held Vast's own provisioning and NOTHING of ours. That makes two very different stories indistinguishable:
# "the job never started" and "the job was three minutes into a pip install when the box was preempted". An
# absent reading is not a reading of absence (CLAUDE.md §4), and a pipeline that cannot be told apart from a
# dead one is a pipeline that costs a diagnostic every time it is interrupted.
#
# So: `awscli` is installed FIRST and on its own (seconds, not minutes), the S3 preflight mark happens
# immediately after it, and every subsequent stage echoes a timestamped line. The slow install — boltz plus
# the cuequivariance wheels — happens AFTER there is somewhere to report from.
_COFOLD_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
echo "[cofold] $(date -u +%FT%TZ) onstart begins on ${CONTAINER_ID:-unknown}"
apt-get update -q >/dev/null 2>&1 || true
apt-get install -y -q --no-install-recommends git curl ca-certificates >/dev/null 2>&1 || true
echo "[cofold] $(date -u +%FT%TZ) apt done; installing awscli (fast) so this host can REPORT before it works"
pip install --quiet awscli || { echo "[cofold] awscli install FAILED"; exit 3; }
AWS=$(command -v aws || echo /opt/conda/bin/aws)
_HOST0="instance=${CONTAINER_ID:-unknown}"
echo "boot $(date -u +%FT%TZ) $_HOST0" | $AWS s3 cp - "$RESULT_S3/phase.txt" || {
  echo "[cofold] FATAL cannot write to $RESULT_S3 — refusing to run an unmonitorable job"; exit 4; }
echo "[cofold] $(date -u +%FT%TZ) phase=boot written; installing $BOLTZ_SPEC (slow: torch wheels)"
pip install --quiet $BOLTZ_SPEC cuequivariance-torch cuequivariance-ops-torch-cu12 || \
  { echo "[cofold] boltz install FAILED"; echo "boltz-install-failed $(date -u +%FT%TZ) $_HOST0" | $AWS s3 cp - "$RESULT_S3/phase.txt" || true; exit 3; }
echo "[cofold] $(date -u +%FT%TZ) boltz installed"
_HOST="instance=${CONTAINER_ID:-unknown} attempt=$(date -u +%Y%m%dT%H%M%SZ)"
# ★★ A PER-HOST MARKER BESIDE THE SHARED ONE — AND IT IS WHAT MAKES THE REAP ATTRIBUTABLE (measured
# 2026-08-01). BOTH arms' co-fold hosts write to the SAME `$RESULT_S3`, so `phase.txt` is a single file the
# two of them overwrite in turn: at 11:04 AM ET it named 46508454, at 12:11 PM ET it named 46508511, and at
# no moment did it say anything about the OTHER host. A reaper reading only that file therefore has terminus
# evidence for at most one box and an ABSENT reading for the rest — and an absent reading is not a reading of
# absence (CLAUDE.md §4), so it cannot spare or condemn on it. `phase-$CONTAINER_ID.txt` is one small object
# per host that says, unambiguously, what THAT host last did. `reap_decision` reads it and nothing else for
# the host-reported-terminus branch.
mark() {
  _m="$1 $(date -u +%FT%TZ) $_HOST"
  echo "$_m" | $AWS s3 cp - "$RESULT_S3/phase.txt" || echo "[mark] WARN could not write phase '$1'"
  echo "$_m" | $AWS s3 cp - "$RESULT_S3/phase-${CONTAINER_ID:-unknown}.txt" || true
}
exec > >(tee -a /tmp/run.log) 2>&1
( while true; do $AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true; sleep 45; done ) &
LOGSYNC_PID=$!
mark deps-ready
nvidia-smi || true
free -g || true
# ★ THE TWO NUMBERS THAT DISCRIMINATE THE DEATHS SEEN ON 2026-08-01. Four hosts died between 4 and 14 min,
# three of them while Boltz was pulling its ~3 GB of CCD data and weights. That has two very different
# candidate causes — an outbid interruptible rental, or the volume filling — and they need opposite fixes.
# `df` is the observation that settles the disk half; the bid half is settled control-plane-side by
# `nrv04_vast_launch.instance_outbid`, which `--mode diag` now reports.
df -h / /root /tmp 2>/dev/null || true
rm -rf /tmp/repo
git clone -q {repo} /tmp/repo
git -C /tmp/repo checkout -q "$GIT_BRANCH" || true
mark cloned
export OUTPUT_DIR=/tmp/selcal_cofold_out SELCAL_INPUTS_DIR=/tmp/selcal_cofold_out/inputs
mkdir -p "$SELCAL_INPUTS_DIR"
$AWS s3 cp "$COFOLD_INPUTS_S3" "$SELCAL_INPUTS_DIR/" --recursive --only-show-errors
# ★★ CROSS-HOST RESUME — this is the checkpoint rule applied where it actually bites. Every completed
# (arm, seed) is already durable in S3; without this line a replacement host starts from an EMPTY output
# directory, so the runner's per-seed skip can never fire and a preemption costs the whole batch instead of
# the seed that was in flight. It also restores the MSA, which is the expensive part: `boltz_results_*/msa/`
# and `processed/` are written before inference, so a host that died during weight download hands its MSA to
# its successor rather than making it redo eight minutes of ColabFold queries.
# ⛔ AND IT IS SCOPED TO THIS HOST'S OWN ARM(S). A host restoring the WHOLE prefix pulls down the other arm's
# finished models, gives them fresh local mtimes, and its continuous sync then re-uploads them — churning a
# validated, banked set of co-folds that this rental was never asked to touch. The panel's models are the
# preregistered INPUTS of every MD leg; a set that silently becomes "fresh" is a set whose provenance nobody
# can state. `SELCAL_SYSTEMS` already scopes what this host COMPUTES; this scopes what it TOUCHES.
_SYNC_ARGS=(--exclude 'inputs/*' --exclude 'run.log' --exclude 'phase.txt' --exclude 'phase-*.txt')
if [ -n "${SELCAL_SYSTEMS:-}" ]; then
  _SYNC_ARGS+=(--exclude '*')
  for _s in $(echo "$SELCAL_SYSTEMS" | tr ',' ' '); do _SYNC_ARGS+=(--include "$_s/*"); done
fi
echo "[cofold] $(date -u +%FT%TZ) restore scope: ${_SYNC_ARGS[*]}"
$AWS s3 sync "$RESULT_S3/" "$OUTPUT_DIR/" "${_SYNC_ARGS[@]}" --only-show-errors || true
echo "[cofold] $(date -u +%FT%TZ) restored $(find "$OUTPUT_DIR" -name '*.cif' 2>/dev/null | wc -l) finished CIF(s) and $(find "$OUTPUT_DIR" -path '*/msa/*' 2>/dev/null | wc -l) MSA file(s) from S3"
# CONTINUOUS UPLOAD, per the standing rule: sync every 60 s so a preemption after prediction N leaves
# predictions 1..N durable rather than losing the batch.
( while true; do $AWS s3 sync "$OUTPUT_DIR" "$RESULT_S3/" "${_SYNC_ARGS[@]}" --only-show-errors || true; sleep 60; done ) &
SYNC_PID=$!
echo "[cofold] $(date -u +%FT%TZ) disk before inference:"; df -h / /root /tmp 2>/dev/null || true
# ★★ THE CCD/WEIGHTS CACHE IS RESTORED AND VERIFIED BEFORE INFERENCE (measured 2026-08-01). The restore
# itself happens inside `selcal_cofold_run.preflight_ccd`, which is also what VERIFIES it — the two must not
# be separated, because a cache that has been restored is not thereby known to be complete, and the smarca4
# arm died on exactly that assumption: `ValueError: CCD component CYS not found!`, six seeds, ~7 s each,
# rc=1, no models. The pipeline's job is only to say WHERE the cache lives and where it is banked.
export BOLTZ_CACHE=/tmp/boltz_cache
mkdir -p "$BOLTZ_CACHE"
mark predicting
cd /tmp/repo/research/modalities
set +e
# ⛔ NO `| tail`, AND `-u` IS NOT OPTIONAL. `python … | tail -400` buffers the ENTIRE run and prints nothing
# until the process exits, so a 1-hour job is invisible for an hour — measured 2026-08-01 on instance
# 46505536, where the streamed run.log sat frozen on the `free -g` output while the phase marker already said
# `predicting`. That is a manufactured stall: CLAUDE.md §4 says unexpected silence must be investigated, so a
# fake one burns a real diagnostic. `-u` unbuffers Python's own stdout for the same reason — a pipe makes it
# block-buffered, and the tee that feeds run.log IS a pipe.
python -u selcal_cofold_run.py 2>&1
RC=$?
set -e
kill $SYNC_PID 2>/dev/null || true
kill $LOGSYNC_PID 2>/dev/null || true
$AWS s3 sync "$OUTPUT_DIR" "$RESULT_S3/" "${_SYNC_ARGS[@]}" --only-show-errors || true
$AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors || true
mark "done rc=$RC"
exit $RC
"""


# =============================================================================================================
# job specs — PURE, so they are unit-tested with no creds
# =============================================================================================================
def cofold_inputs_s3(bucket=None, prefix=None):
    return "s3://%s/%s/inputs/" % (bucket or BUCKET, (prefix or SP.COFOLD_PREFIX).strip("/"))


def boltz_cache_s3(bucket=None, spec=None):
    """Where this lane banks the verified Boltz CCD + weights cache. PURE.

    Keyed on the pinned Boltz spec, slugified — `boltz==2.1.1` and a later release do not share a cache
    layout, and restoring one into the other is a way to MANUFACTURE the truncation this whole mechanism
    exists to prevent."""
    slug = "".join(c if c.isalnum() else "-" for c in (spec or BOLTZ_SPEC)).strip("-").lower()
    return "s3://%s/selcal-boltz-cache/%s/" % (bucket or BUCKET, slug)


def build_leg_jobspec(arm, model_seed, replica, mode, branch, bucket, env_tarball_url=None, exclude=(),
                      cofold_prefix=None):
    """PURE: the JobSpec for one sensitivity-control unit. No I/O."""
    name = SP.unit_name(arm, model_seed, replica)
    env = SP.leg_env(arm, model_seed, replica, mode=mode)
    env.update({
        "GIT_BRANCH": branch,
        "SELCAL_SYSTEM": arm.cofold_system,
        "COFOLD_PREFIX_S3": SP.cofold_prefix_s3(arm, bucket, model_seed, prefix=cofold_prefix),
        "COFOLD_INPUTS_S3": cofold_inputs_s3(bucket, cofold_prefix),
        "RESULT_S3": "s3://%s/%s/%s" % (bucket, SP.RESULT_PREFIX, name),
        # the breaker's evidence, in `leg_failure_breaker.count_attempts`' own glob — never a spelling of ours
        "ATTEMPT_S3": "s3://%s/%s/legs/%s/attempts" % (bucket, SP.RESULT_PREFIX, name),
        # a SEPARATE namespace: a second object under attempts/ would halve the breaker threshold silently
        "ATTEMPT_LOG_S3": "s3://%s/%s/legs/%s/attempt-logs" % (bucket, SP.RESULT_PREFIX, name),
        "CKPT_EVERY_FRAMES": os.environ.get("SELCAL_CKPT_EVERY_FRAMES", "25"),
    })
    if env_tarball_url:
        env["ENV_TARBALL_URL"] = env_tarball_url
    return JobSpec(
        name=name,
        command=["bash", "-lc", _MD_PIPELINE.replace("{repo}", REPO)],
        image=VAST_IMAGE,
        checkpoint_uri=s3_checkpoint_uri(name, bucket=bucket),
        resume=True,
        # ⛔ the binding buy line travels WITH the spec: `rank_offers_by_usd_per_ns` drops every offer above
        # the cap before selection sees it, including on every fallback after a capacity refusal. That is what
        # makes overpaying structurally impossible rather than procedurally discouraged.
        resources=endpoint_md_resources(max_usd_per_ns=buy_ceiling_usd_per_ns(), exclude=exclude),
        max_runtime_s=int(os.environ.get("SELCAL_MAX_RUNTIME_S", "43200")),
        env=env,
    )


def build_cofold_jobspec(branch, bucket, cofold_prefix=None, exclude=(), systems=None):
    """PURE: the JobSpec for ONE co-fold host. `systems` scopes it to a subset of the arms.

    ★ ONE HOST PER ARM. §6's litmus test — "is there a result this shard could return that would make me NOT
    run the rest?" — is NO for the two arms: the control needs both, and parallel costs the same GPU-dollars
    as serial, so serialising buys only wall-clock. Measured on the first attempt: ~11 min per (arm, seed)
    including a fresh MSA, i.e. ~2.2 h for 12 sequential predictions against ~1.1 h split two ways."""
    import dataclasses
    prefix = (cofold_prefix or SP.COFOLD_PREFIX).strip("/")
    # ⚠ DISK RAISED 80 -> 120 GB. Not a guess about the cause — a cheap removal of one of the two candidate
    # causes, so the next failure is diagnostic rather than ambiguous. The image, the pip tree, ~3 GB of
    # Boltz CCD + weights and twelve prediction directories all live on this volume, and disk costs cents.
    res = ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=64, disk_gb=120, interruptible=True,
                       max_usd_per_ns=buy_ceiling_usd_per_ns())
    if exclude:
        res = dataclasses.replace(res, exclude_machine_ids=tuple(str(m) for m in exclude))
    tag = "-".join(sorted(systems)) if systems else "all"
    return JobSpec(
        name="selcal-cofold-%s-%s" % (prefix, tag),
        command=["bash", "-lc", _COFOLD_PIPELINE.replace("{repo}", REPO)],
        image=COFOLD_IMAGE,
        checkpoint_uri="s3://%s/%s" % (bucket, prefix),
        # resume=False on the CHECKPOINT channel, but the RUNNER resumes per (system, seed) by inspecting its
        # own output dir — see selcal_cofold_run. The continuous sync is what makes a preemption cheap.
        resume=False,
        resources=res,
        max_runtime_s=int(os.environ.get("SELCAL_COFOLD_MAX_RUNTIME_S", "21600")),
        env={"GIT_BRANCH": branch, "RESULT_S3": "s3://%s/%s" % (bucket, prefix),
             "COFOLD_INPUTS_S3": cofold_inputs_s3(bucket, prefix),
             "BOLTZ_SPEC": BOLTZ_SPEC,
             # ★ THE CCD/WEIGHTS CACHE, KEYED ON THE PINNED BOLTZ SPEC AND *OUTSIDE* THE RUN PREFIX. Keyed on
             # the spec because a different Boltz has a different cache layout and restoring one into the
             # other would manufacture the very truncation this exists to prevent; outside the run prefix
             # because the co-fold prefix is deliberately FRESH per design freeze, and a cache that died with
             # each freeze would re-pull ~3 GB on every host of every future panel — during precisely the
             # window in which three of four hosts have died on this lane.
             "BOLTZ_CACHE_S3": boltz_cache_s3(bucket),
             "SELCAL_SEEDS": ",".join(str(s) for s in SP.COFOLD_MODEL_SEEDS),
             "SELCAL_SYSTEMS": ",".join(sorted(systems)) if systems else ""},
    )


# =============================================================================================================
# ★★ THE PRICE GATE — and a DURABLE record on EVERY tick, including the ticks with nothing to buy
# =============================================================================================================
def market_gate(n_hosts, bucket=None, offers=None, key=None, price=True, readout_path=None, res=None,
                what="fan-out"):
    """(hold, doc) — may this lane rent `n_hosts` right now? Reads the LIVE board unless `offers` is given.

    ⛔ A SILENT DECLINE IS INDISTINGUISHABLE FROM A BROKEN RE-PLACER. That cost a sibling lane 1 h 55 m of
    unnoticed outage: the gate's only call site sat behind `if todo`, so on every tick that declined to place
    anything the gate never ran and there was nothing to write — the visibility mechanism was structurally
    unreachable on exactly the path where a decline needed explaining. So this writes its snapshot on EVERY
    pass, and `price=False` records the evaluation WITHOUT reading the board when there is no purchase to
    price, saying so in `reason` rather than emitting a hold nobody caused.

    ⚠ THE SPEC HANDED HERE IS UNCAPPED ON PURPOSE. A gate must SEE the expensive offers to report how far
    above the line the board sits; the cap lives on the spec handed to `submit`. The two are the same number
    by construction — `buy_ceiling_usd_per_ns()`.

    ★ THE HOLD QUOTES BOARD DEPTH, because a hold on price and a hold caused by our own filters read
    identically otherwise, and their remedies are opposite (wait vs widen). `qualifying` far below
    `offers_returned` is a FILTER diagnosis wearing a price label."""
    import relaunch_market_gate as rmg
    bucket = bucket or BUCKET
    res = res if res is not None else endpoint_md_resources()      # UNCAPPED — see the docstring
    n_hosts = max(1, int(n_hosts))
    tier = ("bid (interruptible)" if res.interruptible else
            "on-demand (UNINTERRUPTIBLE — small and dear by construction; NOT the market the ladder is "
            "costed on)")
    doc = {"_what": "Whether the endpoint-MD sensitivity control may rent %d host(s) right now, priced in "
                    "$/ns." % n_hosts,
           "_rule": "CLAUDE.md §6 — a thin, expensive market is a reason to PAUSE, not to pay; and a "
                    "relaunch is a NEW PURCHASE, not a continuation.",
           "lane": LANE, "buying": what, "n_hosts": n_hosts, "utc": _utcnow(),
           "tier": tier, "interruptible": bool(res.interruptible),
           "buy_line_usd_per_ns": round(buy_ceiling_usd_per_ns(), 6)}
    if not price:
        doc.update({"priced": False, "hold": False, "best_usd_per_ns": None, "basis_usd_per_ns": None,
                    "ratio_vs_basis": None, "board_depth": None, "offers_priced": [],
                    "reason": "NOT PRICED — no unit needed a host this tick, so there was no purchase to "
                              "price. This is an EVALUATION, not a hold: nothing was refused and nothing "
                              "bought. Which units were skipped, and why, is in %s."
                              % os.path.basename(GATE_RECORD)})
        _write(readout_path or MARKET_READOUT, doc)
        print("[selcal-market] — NOT PRICED this tick. Tier that WOULD be priced: %s." % tier, flush=True)
        return False, doc
    if offers is None:
        try:
            from gpu_backend import _vast_offer_query
            api = key or os.environ.get("VAST_API_KEY")
            if not api:
                raise RuntimeError("no VAST_API_KEY — the board cannot be read")
            offers = (_vast_request("GET", "/search/asks/", api,
                                    params={"q": json.dumps(_vast_offer_query(res))}) or {}).get("offers", [])
        except Exception as e:  # noqa: BLE001 — an UNREADABLE market is not a cheap one. Refuse, and say why.
            offers, doc["board_error"] = None, "%s: %s" % (type(e).__name__, e)
    if offers is None:
        best, depth, rows = None, {"offers_returned": 0, "qualifying": 0, "priceable": 0,
                                   "needed": n_hosts, "used_for_mean": 0}, []
    else:
        best, depth, rows = rmg.price_offers(offers, res, n_hosts=n_hosts)
    hold, ratio, basis, reason = rmg.verdict(best)
    if doc.get("board_error"):
        reason = ("could not read the board (%s) — an unreadable market is not a cheap one, and this gate "
                  "exists precisely for the case where nobody is awake to check" % doc["board_error"])
    elif hold and depth["offers_returned"] and not depth["qualifying"]:
        # ⚠ NOT A PRICE HOLD, AND REPORTING IT AS ONE COSTS A SESSION. The board RETURNED offers and NONE
        # survived the filter: that is a spec/exclusion diagnosis, whose remedy (widen) is the opposite of a
        # price hold's (wait). The discriminating observation is right here, so it is stated rather than left
        # for someone to re-derive at 3 AM.
        reason = ("NOT A PRICE HOLD — the board returned %d offer(s) and NONE survived the ResourceSpec "
                  "filter. Either the spec is unsatisfiable on today's board or an exclusion set has "
                  "outgrown the market; re-pricing fixes neither. Review the spec before touching any "
                  "ceiling." % depth["offers_returned"])
        doc["hold_cause"] = "exclusions_or_spec_not_price"
    doc.update({"priced": True, "hold": hold, "reason": reason,
                "best_usd_per_ns": (round(best, 6) if best else None),
                "basis_usd_per_ns": round(basis, 6), "ratio_vs_basis": ratio,
                "board_depth": depth, "offers_priced": rows})
    _write(readout_path or MARKET_READOUT, doc)
    if hold:
        print("[selcal-market] ⛔ HELD — %s. NOTHING rented, nothing dropped, every checkpoint intact. "
              "Board: %s" % (reason, json.dumps(depth)), flush=True)
        print("::notice title=SELCAL HELD ON PRICE::%d host(s) refused — best achievable %sx the ladder "
              "basis against a buy line of $%s/ns. Snapshot: %s."
              % (n_hosts, ratio, doc["buy_line_usd_per_ns"], os.path.basename(MARKET_READOUT)), flush=True)
    else:
        print("[selcal-market] ✅ CLEAR — %s. Board: %s" % (reason, json.dumps(depth)), flush=True)
    return hold, doc


def _record_gate(decision, units, extra=None):
    """The durable PER-TICK record of what this lane decided and why.

    Separate from the market snapshot on purpose: that one answers *what did the board cost*, this one
    answers *which units did we buy, skip or refuse, and for which reason*. A decline that leaves only a
    market snapshot cannot be told from a tick that never reached the gate."""
    doc = {"_what": "Per-tick record of the sensitivity-control lane's placement decision. Written on EVERY "
                    "tick, buying or not — a silent decline is indistinguishable from a broken re-placer.",
           "lane": LANE, "utc": _utcnow(), "decision": decision, "units": units}
    doc.update(extra or {})
    _write(GATE_RECORD, doc)
    return doc


# =============================================================================================================
# the price ledger — written AT DESTROY, BEFORE the DELETE
# =============================================================================================================
def _ledger_load():
    if os.path.exists(PRICE_LEDGER):
        try:
            with open(PRICE_LEDGER) as fh:
                return json.load(fh)
        except (OSError, ValueError):
            pass
    return {"_what": "Every rental this lane made, priced from the instance record at the moment of "
                     "destruction.",
            "_why_at_destroy": "⛔ THE DELETE IS THE LAST MOMENT THE INSTANCE RECORD EXISTS. A rental that "
                               "billed and left no trace has already happened here (instance 46459452, "
                               "overnight): read `duration` and `dph_total` BEFORE the DELETE, or the cost "
                               "is unrecoverable.",
            "lane": LANE, "rentals": []}


#: How long THIS RENTAL has been alive, in seconds.
#: ⛔ NOT `instance["duration"]`. THAT FIELD IS THE HOST MACHINE'S UPTIME, and reading it as the rental's is a
#: measured, expensive mistake — `nrv04_vast_launch`'s ledger comment records a census where three hosts rented
#: 14/31/72 min earlier had `duration` reading 135 d / 1958 d / 30 d. This lane made exactly that error on its
#: first rental: instance 46504822 was alive ~8 minutes and the ledger row said 2,303,739,360 s and
#: **$117,708.76**. A spend ledger that can print a six-figure row for an eight-minute box is worse than no
#: ledger, because the number looks authoritative. The rental's own clock is `start_date` (epoch seconds), which
#: the same census verified against three known rental times.
#: SUPERSEDED, RETAINED: the `duration`-based row above, and its $117,708.7568. It is kept in the ledger's
#: `corrections` list rather than deleted (CLAUDE.md rule 1.2 — never silently drop a superseded number).
def rental_uptime_s(inst, now=None):
    """PURE: seconds this RENTAL has been alive, from `start_date`. None when it cannot be measured — and an
    absent reading is reported as one rather than defaulted to zero, which would silently price a real
    rental at $0."""
    try:
        sd = float(inst.get("start_date"))
    except (TypeError, ValueError):
        return None
    if sd <= 0:
        return None
    return max(0.0, (time.time() if now is None else float(now)) - sd)


def _ledger_record(inst, why):
    """Append one rental to the committed ledger. Called immediately BEFORE the destroy call."""
    led = _ledger_load()
    iid = str(inst.get("id"))
    dph = float(inst.get("dph_total") or 0.0)
    dur_s = rental_uptime_s(inst)
    gpu = inst.get("gpu_name")
    row = {"instance": iid, "label": inst.get("label"), "machine_id": inst.get("machine_id"),
           "gpu_name": gpu, "dph_total": round(dph, 5),
           "uptime_s": (round(dur_s, 1) if dur_s is not None else None),
           "uptime_source": "start_date (the RENTAL's clock) — never `duration`, which is the HOST's uptime",
           "billed_usd": (round(dph * dur_s / 3600.0, 4) if dur_s is not None else None),
           "billed_usd_absent_why": (None if dur_s is not None else
                                     "start_date unreadable on this record — the cost is UNKNOWN, not zero"),
           "is_bid": inst.get("is_bid"), "destroyed_utc": _utcnow(), "why": why}
    try:
        import inflight_usd_per_ns as IU
        import vast_cost_model as vcm
        row["usd_per_ns_cell"] = IU.row(gpu, dph, vcm.PLAN_USD_PER_REF_GPU_H if hasattr(vcm, "PLAN_USD_PER_REF_GPU_H")
                                        else _plan_rate(), stance=IU.PAYING,
                                        rate_basis=IU.RATE_FROM_INSTANCE,
                                        tier=IU.tier_of(inst.get("is_bid")))["cell"]
    except Exception as e:  # noqa: BLE001 — a ledger row must land even if the $/ns cell cannot be rendered
        row["usd_per_ns_cell"] = "unavailable (%s)" % type(e).__name__
    # A row REPLACED rather than appended keeps its predecessor: rule 1.2 forbids silently dropping a
    # superseded number, and a ledger is the last place to start.
    prior = [r for r in led.get("rentals", []) if r.get("instance") == iid]
    if prior:
        led.setdefault("corrections", []).extend(prior)
    led["rentals"] = [r for r in led.get("rentals", []) if r.get("instance") != iid] + [row]
    priced = [r for r in led["rentals"] if r.get("billed_usd") is not None]
    led["total_billed_usd"] = round(sum(r["billed_usd"] for r in priced), 4)
    led["n_rentals"] = len(led["rentals"])
    led["n_rentals_unpriced"] = len(led["rentals"]) - len(priced)
    _write(PRICE_LEDGER, led)
    print("[selcal-ledger] %s (%s) billed %s over %s at $%.4f/hr — recorded BEFORE the delete"
          % (iid, inst.get("label"),
             ("$%.4f" % row["billed_usd"]) if row["billed_usd"] is not None else "UNKNOWN",
             ("%.1f min" % (dur_s / 60.0)) if dur_s is not None else "an unmeasurable uptime", dph),
          flush=True)
    return row


def _plan_rate():
    """The ladder's planning rate per reference GPU-hour. READ from the committed reprice, never typed."""
    with open(os.path.join(HERE, "vast-ladder-repricing.json")) as fh:
        return json.load(fh)["plan_usd_per_reference_gpu_h"]


def ladder_cost(n_legs=None):
    """This panel's DERIVED cost. Never typed: it is `n_legs x the endpoint-MD reference GPU-hours x the
    ladder's planning rate`, the same arithmetic `selectivity_resolution_options.price_units` performs, so a
    ladder reprice moves it."""
    import selectivity_resolution_options as SRO
    n = len(SP.enumerate_units()) if n_legs is None else int(n_legs)
    rates = SRO.planning_rates()
    return SRO.price_units(n, SRO.ENDPOINT_MD_LEG_REF_GPU_H, rates)


# =============================================================================================================
# modes
# =============================================================================================================
def mode_manifest():
    man = SP.panel_manifest()
    man["derived_cost"] = ladder_cost()
    man["design_floor"] = __import__("selcal_gate").design_floor()
    print(json.dumps(man, indent=2, ensure_ascii=False))
    c = man["derived_cost"]
    print("\n[selcal] %d legs -> plan $%.2f (range $%.2f-$%.2f), DERIVED from vast-ladder-repricing.json x "
          "vast_cost_model.ENDPOINT_MD_REF_GPU_H_PER_LEG — never typed."
          % (man["n_units"], c["plan_usd"], c["range_usd"][0], c["range_usd"][1]), flush=True)
    return 0


def mode_dry():
    branch = os.environ.get("GIT_BRANCH", "main")
    arm = SP.ARMS[0]
    spec = build_leg_jobspec(arm, SP.COFOLD_MODEL_SEEDS[0], SP.MD_REPLICAS[0], "run", branch, BUCKET)
    print("[selcal-dry] leg %s: image=%s gpu=%s max_usd_per_ns=%s\n  cofold=%s\n  inputs=%s\n  result=%s"
          % (spec.name, spec.image, spec.resources.gpu, spec.resources.max_usd_per_ns,
             spec.env["COFOLD_PREFIX_S3"], spec.env["COFOLD_INPUTS_S3"], spec.env["RESULT_S3"]), flush=True)
    cs = build_cofold_jobspec(branch, BUCKET)
    print("[selcal-dry] cofold %s: image=%s gpu=%s ram=%sGB seeds=%s -> %s"
          % (cs.name, cs.image, cs.resources.gpu, cs.resources.ram_gb, cs.env["SELCAL_SEEDS"],
             cs.env["RESULT_S3"]), flush=True)
    c = ladder_cost()
    print("[selcal-dry] %d units, plan $%.2f (range $%.2f-$%.2f)"
          % (len(SP.enumerate_units()), c["plan_usd"], c["range_usd"][0], c["range_usd"][1]), flush=True)
    return 0


def mode_stage_prep(bucket=None, cofold_prefix=None):
    """$0 CPU on CI: resolve the constructs, write the Boltz YAMLs + the chain contract, upload to S3.

    ★ IT RUNS HERE AND NOT ON THE RENTED HOST for two reasons that both cost money otherwise: a UniProt or
    AlphaFold-DB hiccup would fail a job that is already billing, and the chain CONTRACT the assembler
    verifies against has to be in S3 anyway — every MD leg reads it."""
    import boto3
    import selcal_stage as ST
    bucket = bucket or BUCKET
    prefix = (cofold_prefix or SP.COFOLD_PREFIX).strip("/")
    out_dir = "/tmp/selcal_inputs"
    man = ST.build_cofold_inputs(out_dir)
    s3 = boto3.client("s3")
    up = []
    for fn in sorted(os.listdir(out_dir)):
        key = "%s/inputs/%s" % (prefix, fn)
        s3.upload_file(os.path.join(out_dir, fn), bucket, key)
        up.append(key)
    # the reference artifact travels WITH the inputs: the assembler reads the ligand SMILES out of it on the
    # host, and a host that fetched it from the repo tarball could silently get a different revision.
    ref = os.path.join(HERE, "selcal-reference-selectivity.json")
    if os.path.exists(ref):
        key = "%s/inputs/selcal-reference-selectivity.json" % prefix
        s3.upload_file(ref, bucket, key)
        up.append(key)
    else:
        raise SystemExit("[selcal-stage-prep] %s is missing — run the lane's `refs` mode first. The ligand "
                         "is never typed." % os.path.basename(ref))
    print("[selcal-stage-prep] uploaded %d input object(s) to s3://%s/%s/inputs/" % (len(up), bucket, prefix),
          flush=True)
    print(json.dumps({"uploaded": up, "ligand": man["ligand"],
                      "chain_contract": man["chain_contract"]}, indent=2))
    return 0


def mode_cofold_dry():
    spec = build_cofold_jobspec(os.environ.get("GIT_BRANCH", "main"), BUCKET)
    print("[selcal-cofold-dry] %s\n  image=%s gpu=%s ram=%sGB disk=%sGB max_usd_per_ns=%s\n  seeds=%s\n"
          "  inputs=%s\n  result=%s"
          % (spec.name, spec.image, spec.resources.gpu, spec.resources.ram_gb, spec.resources.disk_gb,
             spec.resources.max_usd_per_ns, spec.env["SELCAL_SEEDS"], spec.env["COFOLD_INPUTS_S3"],
             spec.env["RESULT_S3"]), flush=True)
    return 0


def mode_cofold(bucket=None, cofold_prefix=None):
    """Rent ONE host and produce every structural input. Gated on $/ns like any other rental."""
    import boto3
    bucket = bucket or BUCKET
    prefix = (cofold_prefix or SP.COFOLD_PREFIX).strip("/")
    branch = os.environ.get("GIT_BRANCH", "main")
    s3 = boto3.client("s3")
    if not _s3_list(s3, bucket, "%s/inputs/" % prefix, limit=1):
        raise SystemExit("[selcal-cofold] no inputs under s3://%s/%s/inputs/ — run `stage_prep` first. A "
                         "co-fold host with no chain contract produces structures nothing can assemble."
                         % (bucket, prefix))
    done = _cofold_census(s3, bucket, prefix)
    if done["complete"]:
        print("[selcal-cofold] every (arm, seed) already has a CIF — nothing to rent. %s" % done["per_arm"],
              flush=True)
        _record_gate("nothing-to-buy", [], extra={"why": "co-folds already complete", "census": done})
        market_gate(1, bucket=bucket, price=False, what="co-fold")
        return 0
    import dataclasses
    # ONE HOST PER ARM THAT STILL NEEDS MODELS. A live host already covering an arm is not re-rented.
    live, _mine = _live_labels()
    need = sorted({a.cofold_system for a in SP.ARMS
                   if len(done["per_arm"].get(a.arm_id, [])) < len(SP.COFOLD_MODEL_SEEDS)})
    _excl = exclude_machines()
    if _excl:
        print("[selcal-cofold] this dispatch EXCLUDES machine(s) %s — a measured, call-bounded exception, "
              "not a durable blacklist (see `exclude_machines`)." % list(_excl), flush=True)
    specs = [build_cofold_jobspec(branch, bucket, prefix, systems=[sysname], exclude=_excl)
             for sysname in need]
    specs = [sp for sp in specs if sp.name not in live]
    if not specs:
        print("[selcal-cofold] every incomplete arm already has a live host — nothing to rent.", flush=True)
        _record_gate("nothing-to-buy", [], extra={"why": "a live host already covers each incomplete arm",
                                                  "census": done})
        market_gate(1, bucket=bucket, price=False, what="co-fold")
        return 0
    # UNCAPPED copy for the gate — a gate must SEE the expensive offers to report how far above the line the
    # board sits. The cap stays on the spec handed to `submit`, where it binds the offer actually bought.
    hold, _doc = market_gate(len(specs), bucket=bucket,
                             res=dataclasses.replace(specs[0].resources, max_usd_per_ns=None),
                             what="co-fold (%d arm host(s))" % len(specs))
    if hold:
        _record_gate("held-on-price", [sp.name for sp in specs],
                     extra={"why": "market gate held the co-fold rental"})
        return 0
    be = get_backend("vast")
    handles, refused, wave_refused = [], [], set()
    for spec in specs:
        if wave_refused:
            spec = dataclasses.replace(
                spec, resources=dataclasses.replace(spec.resources,
                                                    exclude_machine_ids=tuple(sorted(wave_refused))))
        try:
            h = be.submit(spec)
        except Exception as e:  # noqa: BLE001
            for ref in getattr(e, "refusals", ()) or ():
                mid = str((ref or {}).get("machine_id") or "").strip()
                if mid:
                    wave_refused.add(mid)
            refused.append(spec.name)
            print("[selcal-cofold] ⛔ %s NOT RENTED — %s: %s. If the board simply had nothing at or under "
                  "$%.6f/ns, this is the buy line doing its job: $0 spent."
                  % (spec.name, type(e).__name__, e, spec.resources.max_usd_per_ns), flush=True)
            continue
        print("[selcal-cofold] %s -> instance %s dph≈$%s/hr -> %s"
              % (spec.name, h.job_id, h.extra.get("dph"), spec.env["RESULT_S3"]), flush=True)
        handles.append({"unit": spec.name, "instance": h.job_id, "kind": "cofold", "utc": _utcnow(),
                        "systems": spec.env["SELCAL_SYSTEMS"]})
    if handles:
        _write(HANDLES, handles)
        # ★★ A RENTAL IS BORN UNSUPERVISED UNLESS SOMETHING ARMS THE WATCH — and on 2026-08-01 nothing did.
        # Two co-fold hosts were rented at 10:10 AM ET, the lane's census went silent at 11:04 AM ET, and the
        # first thing to notice the two idle boxes was an ACCOUNT-level alarm at 12:04 PM ET. CLAUDE.md §6:
        # a `schedule:` cron does not supervise a billing fleet, and while a fleet is billing supervision is
        # somebody's job. `cofold_watch` is a $0 supervision mode that reaps on every tick, so arming it here
        # does not breach `self_dispatch`'s rule that a renting rung stays a deliberate dispatch — it is the
        # watch that is armed automatically, never the purchase.
        if not self_dispatch("cofold_watch"):
            print("::error title=SELCAL CO-FOLD UNSUPERVISED::%d host(s) were just rented and the watch could "
                  "not be armed. Dispatch `cofold_watch` (or `stop`) by hand — nothing else will reap them."
                  % len(handles), flush=True)
    _record_gate("rented" if handles else "refused", [h["unit"] for h in handles],
                 extra={"refused": refused, "wave_refused_machines": sorted(wave_refused),
                        "excluded_machines_this_dispatch": list(_excl)})
    return 0 if handles else 1


def _cofold_census(s3, bucket, prefix):
    """Which (arm, seed) co-folds actually exist. MEASURED from S3 keys, never assumed."""
    per_arm, missing = {}, []
    for arm in SP.ARMS:
        got = []
        for seed in SP.COFOLD_MODEL_SEEDS:
            keys = _s3_list(s3, bucket, "%s/%s/seed_%d/" % (prefix, arm.cofold_system, seed),
                            suffix="_model_0.cif", limit=2)
            if len(keys) == 1:
                got.append(seed)
            else:
                missing.append({"arm": arm.arm_id, "seed": seed, "n_cif": len(keys),
                                "why": ("absent" if not keys else
                                        "MORE THAN ONE model_0 CIF under the pinned prefix — the seed pin "
                                        "failed and a leg would start from an unknown model")})
        per_arm[arm.arm_id] = got
    return {"prefix": prefix, "per_arm": per_arm, "missing": missing,
            "complete": not missing,
            "n_models_per_arm": {k: len(v) for k, v in per_arm.items()}}


def mode_cofold_collect(bucket=None, cofold_prefix=None):
    """A PROGRESS check on the co-fold host, not a liveness ping (CLAUDE.md §4).

    An unproven pipeline is checked every 3-6 min and every check must show that work MOVED: which phase the
    host is in, whether its GPU is busy, and how many predictions have actually landed. "An instance is up" is
    not evidence of work, and a census alone cannot tell a host that is mid-prediction from one that died
    twenty minutes ago."""
    import boto3
    bucket = bucket or BUCKET
    prefix = (cofold_prefix or SP.COFOLD_PREFIX).strip("/")
    s3 = boto3.client("s3")
    try:
        ph = s3.get_object(Bucket=bucket, Key="%s/phase.txt" % prefix)["Body"].read().decode(
            "utf-8", "replace").strip()
    except Exception as e:  # noqa: BLE001 — an ABSENT reading, reported as one
        ph = "(unreadable: %s)" % type(e).__name__
    try:
        raw = s3.get_object(Bucket=bucket, Key="%s/run.log" % prefix)["Body"].read()
        tail = raw.decode("utf-8", "replace").splitlines()[-25:]
    except Exception as e:  # noqa: BLE001
        tail = ["(run.log unreadable: %s — an absent reading is not a reading of absence)" % type(e).__name__]
    _live, mine = _live_labels()
    print("[selcal-cofold-progress] phase=%r" % ph, flush=True)
    for i in mine:
        _up = rental_uptime_s(i)
        print("[selcal-cofold-progress] instance %s status=%s gpu_util=%s dph=%s uptime=%s"
              % (i.get("id"), i.get("actual_status"), i.get("gpu_util"), i.get("dph_total"),
                 ("%.1f min" % (_up / 60.0)) if _up is not None else "unmeasurable"), flush=True)
    print("[selcal-cofold-progress] run.log tail:\n  " + "\n  ".join(tail), flush=True)
    # ★ THE WRITE SIGNAL — the only thing that discriminates a working host from a wedged one here.
    # CLAUDE.md §6: GPU idleness NEVER condemns a box; only a measured absence of WRITES does. Boltz spends
    # its first minutes on MSA-server queries, which are network-bound and legitimately leave the GPU at 0 %,
    # so "gpu_util 0.0" is not evidence of a stall. What IS evidence is nothing new landing in S3.
    objs = []
    try:
        page = s3.list_objects_v2(Bucket=bucket, Prefix="%s/" % prefix, MaxKeys=1000)
        objs = page.get("Contents") or []
    except Exception as e:  # noqa: BLE001
        print("[selcal-cofold-progress] could not list S3 (%s) — an absent reading" % type(e).__name__,
              flush=True)
    newest = max((o["LastModified"] for o in objs), default=None)
    cen = _cofold_census(s3, bucket, prefix)
    cen["phase"] = ph
    cen["log_tail"] = tail
    cen["n_s3_objects"] = len(objs)
    cen["newest_object_utc"] = newest.strftime("%Y-%m-%dT%H:%M:%SZ") if newest else None
    cen["newest_object_age_min"] = (round((time.time() - newest.timestamp()) / 60.0, 1) if newest else None)
    print("[selcal-cofold-progress] S3 under the prefix: %d object(s), newest %s (%s min old) — this is the "
          "WRITE signal, and it is what a stall verdict must rest on"
          % (len(objs), cen["newest_object_utc"], cen["newest_object_age_min"]), flush=True)
    # ⛔ `duration` is the HOST's uptime, not the rental's — see `rental_uptime_s`. This row printed 10,184 min
    # for a box two minutes old before it was fixed.
    cen["instances"] = [{"id": i.get("id"), "status": i.get("actual_status"), "gpu_util": i.get("gpu_util"),
                         "dph_total": i.get("dph_total"),
                         "uptime_min": (round(rental_uptime_s(i) / 60.0, 1)
                                        if rental_uptime_s(i) is not None else None)}
                        for i in mine]
    cen.update({"_what": "Which co-fold models exist for the sensitivity control, measured from S3.",
                "utc": _utcnow(), "bucket": bucket})
    _write(COFOLD_CENSUS, cen)
    # ⚠ THE BOARD REFRESHES ON THE $0 TICK TOO, not only inside a watch. Otherwise the lane's fragment goes
    # STALE whenever supervision is between windows — and a stale fragment is right at the moment nobody is
    # watching, wrong at the moment a $0 collect just measured the truth.
    _publish_board(s3, bucket, prefix, cen, mine)
    print(json.dumps(cen, indent=2))
    if not cen["complete"]:
        print("::notice title=SELCAL CO-FOLDS INCOMPLETE::%d (arm, seed) missing — %s"
              % (len(cen["missing"]), cen["n_models_per_arm"]), flush=True)
    return 0


def mode_stage_test(bucket=None, cofold_prefix=None):
    """$0: assemble a real leg from a real co-fold CIF, on a free runner, in the production image.

    This is the rung that catches a staging fault for free. It runs the SAME `assemble_unit` the host runs,
    against the SAME chain contract, and then runs the static input audit — so a broken co-fold is refused
    before it is ever put on a meter."""
    import boto3
    import selcal_stage as ST
    bucket = bucket or BUCKET
    prefix = (cofold_prefix or SP.COFOLD_PREFIX).strip("/")
    s3 = boto3.client("s3")
    os.makedirs("/tmp/selcal_inputs_dl", exist_ok=True)
    for key in _s3_list(s3, bucket, "%s/inputs/" % prefix):
        s3.download_file(bucket, key, os.path.join("/tmp/selcal_inputs_dl", os.path.basename(key)))
    with open("/tmp/selcal_inputs_dl/cofold-inputs.json") as fh:
        man = json.load(fh)
    out = {"_what": "Free-CI staging shakeout: assemble one leg per arm from a REAL co-fold CIF and audit the "
                    "input, before any GPU is rented.", "utc": _utcnow(), "prefix": prefix, "arms": []}
    for arm in SP.ARMS:
        seed = SP.COFOLD_MODEL_SEEDS[0]
        keys = _s3_list(s3, bucket, "%s/%s/seed_%d/" % (prefix, arm.cofold_system, seed),
                        suffix="_model_0.cif", limit=2)
        if len(keys) != 1:
            raise SystemExit("[selcal-stage-test] %s seed %d: expected exactly 1 co-fold CIF, found %d"
                             % (arm.arm_id, seed, len(keys)))
        local = "/tmp/selcal_%s.cif" % arm.cofold_system
        s3.download_file(bucket, keys[0], local)
        res = ST.assemble_unit(local, "%s__m%d" % (arm.arm_id, seed),
                               man["chain_contract"][arm.cofold_system], "/tmp/selcal_staged",
                               reference_json="/tmp/selcal_inputs_dl/selcal-reference-selectivity.json")
        cpdb = os.path.join(res["out"], "complex.pdb")
        n_atom = sum(1 for line in open(cpdb) if line.startswith(("ATOM", "HETATM")))
        audit = ST.cofold_input_audit(cpdb)
        out["arms"].append({"arm": arm.arm_id, "key": keys[0], "ligand_atoms": res["ligand_atoms"],
                            "complex_atoms": n_atom, "chains": res["chains"], "input_audit": audit})
        print("[selcal-stage-test] %s: %d ligand atoms, %d complex atoms, target=%s e3=%s, audit min_sep "
              "%.3f A -> %s" % (arm.arm_id, res["ligand_atoms"], n_atom, res["chains"]["target_chain"],
                                res["chains"]["e3_chains"], audit["min_heavy_atom_sep_A"],
                                "OK" if audit["ok"] else "REFUSED"), flush=True)
    # ★ THE ARMS MUST BE COMPARABLE. A paralogue that lost a chain, or picked up a different ligand, would
    # silently become a different experiment and the identical-protocol premise would fail invisibly.
    sizes = [a["complex_atoms"] for a in out["arms"]]
    ligs = {a["ligand_atoms"] for a in out["arms"]}
    out["arms_comparable"] = bool(max(sizes) <= 1.25 * min(sizes) and len(ligs) == 1)
    if not out["arms_comparable"]:
        _write(STAGE_TEST_READOUT, out)
        raise SystemExit("[selcal-stage-test] arms are NOT protocol-matched: complex atoms %s, ligand atoms "
                         "%s" % (sizes, sorted(ligs)))
    bad = [a["arm"] for a in out["arms"] if not a["input_audit"]["ok"]]
    out["audit_failures"] = bad
    _write(STAGE_TEST_READOUT, out)
    if bad:
        raise SystemExit("[selcal-stage-test] input audit REFUSED %s — see %s"
                         % (bad, os.path.basename(STAGE_TEST_READOUT)))
    print("[selcal-stage-test] ✅ both arms assemble, are protocol-matched (%s atoms, %s ligand atoms) and "
          "pass the static input audit." % (sizes, sorted(ligs)), flush=True)
    return 0


# =============================================================================================================
# renting MD legs
# =============================================================================================================
def _terminal_cur_states():
    """The `cur_state` values that mean this host is NOT covering its unit, however `actual_status` reads.

    ★★ MEASURED 2026-08-01, and it stalled the panel for 32 minutes. Seven hosts from the 6:05 PM wave sat at
    `actual_status='loading'` / `'created'` with **`cur_state='stopped'`** — they were rented and never
    started. `_live_labels` read only `actual_status`, so the launcher counted all seven as live and refused
    to re-place their units; the account reaper, which DOES read `cur_state`, destroyed exactly those seven
    at 6:39 PM as TERMINAL. Two control paths disagreeing about whether a host is alive is the bug: one was
    buying nothing because the unit looked covered, while the other was destroying the thing covering it.

    ⚠ ONE HOME (§1). The set is not re-typed here — `vast_account_reaper` derives it by AST from the lanes
    that define it, and is the module that ACTS on it. Deriving it a second time is how the two definitions
    drifted in the first place.

    ⚠ AND IT FAILS OPEN, NOT CLOSED, WHICH IS THE OPPOSITE OF THE REAPER'S CHOICE — deliberately. If the
    derivation is unavailable this returns EMPTY, so no host is demoted and the lane behaves exactly as it
    did before. The reaper fails closed because its error is DESTRUCTIVE; this predicate's error would be a
    duplicate rental, so the safe direction here is to under-demote. `stopped` can also mean OUTBID-PAUSED
    (see `vast_account_reaper`'s header), and a unit whose host resumes is re-covered on the next tick with
    nothing lost; `mode_launch` is idempotent and `_REPLACE_MIN_S` bounds how often it can act.
    """
    try:
        from vast_account_reaper import terminal_states_from_source
        states, _notes = terminal_states_from_source()
        return frozenset(s.lower() for s in states)
    except Exception as e:  # noqa: BLE001
        print("[selcal] WARN could not derive the terminal cur_state set (%s); no host will be demoted on "
              "cur_state this tick. This UNDER-reports dead hosts rather than over-reporting them." % e,
              flush=True)
        return frozenset()


def _live_labels_checked(key=None):
    """(READABLE, live-by-label, mine) — the same read as `_live_labels`, plus whether it succeeded.

    ★★ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4). `_live_labels` returns an empty list
    both when the account genuinely holds no host AND when the control plane did not answer, and those two
    are opposite instructions: one says "there is nothing to supervise, stop", the other says "you are blind,
    keep watching". A caller that cannot tell them apart will eventually act on the wrong one — and in
    `mode_cofold_watch` that meant a single Vast API blip could end supervision of a host that was still
    billing, silently, down a path that does not re-arm.

    Callers that only ever SKIP work on a live host (the launchers) are unharmed by the conflation and keep
    using the 2-tuple; only the supervision loop needs the third value."""
    try:
        live = _vast_request("GET", "/instances/", key or os.environ.get("VAST_API_KEY"),
                             params={"owner": "me"}).get("instances", [])
    except Exception as e:  # noqa: BLE001
        print("[selcal] WARN could not list live instances (%s); not skipping any. This is UNREADABLE, "
              "not empty — no caller may read it as 'nothing is billing'." % e, flush=True)
        return False, {}, []
    alive = ("running", "loading", "created", "scheduling", "starting")
    terminal = _terminal_cur_states()
    return (True,
            {i.get("label"): i for i in live
             if i.get("label") and (i.get("actual_status") or "") in alive
             and str(i.get("cur_state") or "").lower() not in terminal},
            [i for i in live if str(i.get("label") or "").startswith(SP.LABEL_PREFIX)])


def _live_labels(key=None):
    _readable, live, mine = _live_labels_checked(key)
    return live, mine


def _done_units(s3, bucket):
    """Units with a LANDED leg. A smoke record is NOT one — skipping on a smoke is how a 'finished' panel came
    to be 18 legs of 0.002 ns on a sibling lane (`selcal_panel.production_leg_check`)."""
    done, records = set(), {}
    for key in _s3_list(s3, bucket, "%s/" % SP.RESULT_PREFIX, suffix=".json"):
        base = os.path.basename(key)
        if not base.startswith("leg_"):
            continue
        unit = key.split("/")[1] if key.count("/") >= 2 else None
        try:
            rec = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
        except Exception:  # noqa: BLE001
            continue
        records[key] = rec
        ok, _why = SP.production_leg_check(rec)
        if ok and unit:
            done.add(unit)
    return done, records


def mode_launch(bucket=None, only=None, mode="run", pilot=False, cofold_prefix=None):
    """Rent MD legs. Idempotent: skips units with a LANDED leg in S3 or a live instance, so a re-dispatch
    RESUMES the killed ones without ever racing a checkpoint."""
    import boto3
    bucket = bucket or BUCKET
    branch = os.environ.get("GIT_BRANCH", "main")
    prefix = (cofold_prefix or SP.COFOLD_PREFIX).strip("/")
    s3 = boto3.client("s3")

    census = _cofold_census(s3, bucket, prefix)
    have = {arm_id: set(seeds) for arm_id, seeds in census["per_arm"].items()}
    skip_live, _mine = _live_labels()
    skip_done, _records = _done_units(s3, bucket)

    units = [(a, m, r) for a, m, r in SP.enumerate_units() if m in have.get(a.arm_id, set())]
    no_cofold = [SP.unit_name(a, m, r) for a, m, r in SP.enumerate_units()
                 if m not in have.get(a.arm_id, set())]
    if only:
        allowed = set(only)
        units = [(a, m, r) for a, m, r in units if SP.unit_name(a, m, r) in allowed]
    todo = [(a, m, r) for a, m, r in units
            if SP.unit_name(a, m, r) not in skip_done and SP.unit_name(a, m, r) not in skip_live]
    if pilot:
        # ⛔ ONE LEG, AND IT IS THE ONE WITH THE MOST ABORT INFORMATION. §6's litmus test — "is there a result
        # this shard could return that would make me NOT run the rest?" — is YES here, but not for a
        # scientific reason: a first real leg can return an ENVIRONMENT fault the smoke cannot see. So the
        # pilot is chosen for coverage of the staging path, i.e. the arm whose assembler contract has never
        # been exercised on a meter, and the fan-out waits on it.
        todo = todo[:1]

    if not todo:
        why = ("every unit already has a landed leg or a live host"
               if not no_cofold else
               "no unit is runnable: %d unit(s) have no co-fold model yet" % len(no_cofold))
        print("[selcal] nothing to rent — %s." % why, flush=True)
        _record_gate("nothing-to-buy", [], extra={"why": why, "units_without_cofold": no_cofold[:12],
                                                  "skipped_done": sorted(skip_done)[:24],
                                                  "skipped_live": sorted(skip_live)[:24]})
        market_gate(1, bucket=bucket, price=False, what="MD legs")
        return 0

    hold, _doc = market_gate(len(todo), bucket=bucket, what="MD legs (%d)" % len(todo))
    if hold:
        _record_gate("held-on-price", [SP.unit_name(a, m, r) for a, m, r in todo],
                     extra={"why": "market gate held; nothing rented, every checkpoint intact"})
        return 0

    env_url = presign_env_tarball(bucket)
    be = get_backend("vast")
    handles, refused, wave_refused = [], [], set()
    for arm, m, r in todo:
        spec = build_leg_jobspec(arm, m, r, mode, branch, bucket, env_tarball_url=env_url,
                                 exclude=tuple(sorted(wave_refused | set(exclude_machines()))),
                                 cofold_prefix=prefix)
        try:
            h = be.submit(spec)
        except Exception as e:  # noqa: BLE001 — one unit must not abort the rest
            # WHAT THIS UNIT LEARNED, HANDED TO THE NEXT. Bounded to this wave and discarded when the
            # function returns — not a blacklist (CLAUDE.md §6 retired those); re-learning a bad host costs
            # one FREE failed submit next wave, while over-excluding costs capacity on every lane, silently.
            for ref in getattr(e, "refusals", ()) or ():
                mid = str((ref or {}).get("machine_id") or "").strip()
                if mid:
                    wave_refused.add(mid)
            refused.append(spec.name)
            print("[selcal-submit] ⛔ %s NOT RENTED — %s: %s. If the board had nothing at or under "
                  "$%.6f/ns this is the buy line doing its job: $0 spent, checkpoint intact."
                  % (spec.name, type(e).__name__, e, spec.resources.max_usd_per_ns), flush=True)
            continue
        print("[selcal-submit] %s -> instance %s dph≈$%s/hr" % (spec.name, h.job_id, h.extra.get("dph")),
              flush=True)
        handles.append({"unit": spec.name, "arm": arm.arm_id, "model": m, "replica": r,
                        "instance": h.job_id, "utc": _utcnow()})
    if handles:
        _write(HANDLES, handles)
        # Same rule as the co-fold rental above: the MD legs' supervisor is armed by the thing that bought
        # them, because a fleet whose watch depends on an agent being awake is not supervised.
        if not self_dispatch("watch"):
            print("::error title=SELCAL LEGS UNSUPERVISED::%d MD host(s) were just rented and the watch could "
                  "not be armed. Dispatch `watch` (or `stop`) by hand — nothing else will reap them."
                  % len(handles), flush=True)
    _record_gate("rented" if handles else "refused",
                 [h["unit"] for h in handles],
                 extra={"refused": refused, "wave_refused_machines": sorted(wave_refused),
                        "units_without_cofold": no_cofold[:12], "mode": mode, "pilot": pilot})
    if todo and not handles:
        # ⛔ A LAUNCH THAT RENTED NOTHING MUST NOT REPORT SUCCESS — it looks identical to a completed fan-out
        # in the Actions list, which is the "holding silently" failure §6 names as worse than the problem.
        print("[selcal] ⛔ %d unit(s) were due and NONE was rented. Failing so this cannot read as a "
              "finished fan-out." % len(todo), flush=True)
        return 1
    return 0


# =============================================================================================================
# supervision, teardown and collection
# =============================================================================================================
def _phase(s3, bucket, unit):
    try:
        body = s3.get_object(Bucket=bucket, Key="%s/%s/phase.txt" % (SP.RESULT_PREFIX, unit))["Body"].read()
        return body.decode("utf-8", "replace").strip()
    except Exception:  # noqa: BLE001
        return ""


def mode_status(bucket=None):
    """A PROGRESS board, not a liveness ping. Every row says what phase the unit is in, WHICH HOST wrote that
    phase, and what the log's last line is — because "an instance is up" is not evidence of work."""
    import boto3
    bucket = bucket or BUCKET
    s3 = boto3.client("s3")
    live, mine = _live_labels()
    done, records = _done_units(s3, bucket)
    rows = []
    for a, m, r in SP.enumerate_units():
        unit = SP.unit_name(a, m, r)
        ph = _phase(s3, bucket, unit)
        inst = live.get(unit)
        # ★ A PHASE MARKER MUST BE ATTRIBUTABLE TO THE HOST THAT WROTE IT. A marker naming a dead instance
        # reads as a fact about the current rental and is not — so the row says which, instead of implying.
        attributable = bool(inst and str(inst.get("id")) and ("instance=%s" % inst.get("id")) in ph)
        rows.append({"unit": unit, "phase": ph or "(none)",
                     "phase_written_by_current_host": attributable if inst else None,
                     "live_instance": (inst or {}).get("id"),
                     "gpu_util": (inst or {}).get("gpu_util"),
                     "landed": unit in done})
    n_live = sum(1 for x in rows if x["live_instance"])
    print(json.dumps({"utc": _utcnow(), "landed": len(done), "expected": len(rows), "live_hosts": n_live,
                      "lane_instances": [{"id": i.get("id"), "label": i.get("label"),
                                          "status": i.get("actual_status"), "gpu_util": i.get("gpu_util"),
                                          "dph": i.get("dph_total")} for i in mine],
                      "rows": rows}, indent=2))
    return 0


#: ★ THE STATES AN INSTANCE NEVER WORKS AGAIN FROM. The union of the two sets already in this repo —
#: `nrv04_vast_launch._TERMINAL_STATES` ("exited", "offline", "stopped"), IMPORTED rather than re-typed, plus
#: `congeneric_fanout_vast`'s "error". The two disagreed before this lane existed and neither is importable
#: as one name, so the union is built here with both origins named rather than silently minted as a third,
#: differently-wrong copy (CLAUDE.md rule 1).
#: ⚠ A TERMINAL READING IS A READING OF *THIS INSTANT*, NOT A DURABLE FACT. Measured 2026-08-01: instance
#: 46508511 read `exited` at 11:04 AM ET and `running` at 12:01 PM ET — the container had restarted. So this
#: is evaluated against the instance record fetched by the reap itself, and NEVER against a status quoted from
#: a committed artifact, which is how the 12:01 PM reap came to be judged on a 57-minute-old `exited`.
def _terminal_states():
    from nrv04_vast_launch import _TERMINAL_STATES
    return tuple(sorted(set(_TERMINAL_STATES) | {"error"}))


def cofold_label_systems(label, prefix=None):
    """PURE: which co-fold ARM(S) a Vast label covers, or () when the label is not one of this lane's.

    ⛔ DERIVED FROM THE NAME-BUILDER, NEVER PARSED OUT OF THE STRING. The label is
    `selcal-cofold-selcal-smarca-cofold-v1-smarca2`: the co-fold PREFIX itself contains dashes, so a
    split-on-dash reader mis-assigns the arm — and a mis-assigned arm is a host reaped for work that is banked
    somewhere else. `build_cofold_jobspec` is the only thing that mints these names, so it is the only thing
    asked what one means."""
    out = {}
    for arm in SP.ARMS:
        out[build_cofold_jobspec("main", "b", prefix, systems=[arm.cofold_system]).name] = (arm.cofold_system,)
    out[build_cofold_jobspec("main", "b", prefix).name] = tuple(sorted(a.cofold_system for a in SP.ARMS))
    return out.get(str(label or ""), ())


def reap_decision(inst, done_units, cofold_complete_systems, s3_readable, host_phase="", stop_all=False,
                  prefix=None):
    """PURE: (reap, why) for ONE instance. No API call, no S3, no clock — so every branch is unit-tested.

    ⛔ THE BUG THIS REPLACES, measured on run 30707211425 (12:01 PM ET, `0 destroyed, 2 kept running` while
    two hosts billed at $0.184/hr): the predicate was

        landed = label in done or label.startswith("selcal-cofold")
        why    = ... "result landed in S3" if landed and label in done else ...

    and `landed and label in done` reduces to `label in done`, so the `or label.startswith("selcal-cofold")`
    disjunct was ALGEBRAICALLY DEAD — whenever it was the only true one, the conjunction's other operand was
    False. `done_units` comes from `_done_units`, which only ever holds MD LEG unit names parsed out of
    `leg_*.json` keys; a co-fold host's label cannot appear in it at any time, for any reason. So the reaper
    had no predicate that could EVER fire for a co-fold host, and it never consulted the co-fold census at
    all. Only `stop_all` and a terminal status could reach the DELETE.

    ⚠ NO BRANCH HERE MAY READ `gpu_util`, AND THAT IS INVIOLABLE (CLAUDE.md §6). Both hosts in the incident
    read `gpu_util: 0.0` — INCLUDING the one that had just produced all six of its models — so GPU idleness
    cannot distinguish a finished box from a working one, and it never condemns a box. Only banked work, a
    host-written terminus, or a terminal state does. `tests/test_selcal_launch.py` fails if `gpu_util`ever
    appears in this function.

    The four reasons, each meaning something different in the readout:
      * `operator stop_all`   — a human/`stop` dispatch asked for everything.
      * `terminal state`      — Vast still LISTS and BILLS an `exited`/`stopped`/`offline`/`error` box; it is
                                not coming back. Evidence: the instance record itself, so this branch survives
                                an S3 outage, which is exactly when a box must not be left billing.
      * `work banked, no remaining role` — its own arm/unit is COMPLETE in S3. Keeping it buys nothing: it
                                cannot contribute to another arm, because `SELCAL_SYSTEMS` scoped it to its
                                own at launch.
      * `host reported its terminus` — this host's OWN phase marker says `done rc=…`. The co-fold pipeline
                                writes that and then `exit $RC`, so the process tree is over whatever the rc.
                                This is the case that catches a host whose work FAILED: nothing is banked, so
                                the branch above cannot fire, and the box would otherwise bill forever.

    `s3_readable=False` (the census could not be read) DISABLES the two S3-derived branches entirely — an
    absent reading is not a reading of absence, and the remedy for an unreadable census is to read it again,
    not to destroy hosts on the strength of not knowing. The terminal branch is unaffected on purpose: its
    evidence never came from S3."""
    label = str(inst.get("label") or "")
    status = str(inst.get("actual_status") or "")
    iid = str(inst.get("id") or "")
    if stop_all:
        return True, "operator stop_all — every host this lane owns"
    if status in _terminal_states():
        return True, ("terminal state %r — Vast still lists and bills it and it is not coming back "
                      "(evidence: the instance record, not S3)" % status)
    systems = cofold_label_systems(label, prefix)
    if not s3_readable:
        return False, ("SPARED — the co-fold census could not be read, so nothing is reaped on banked work. "
                       "An absent reading is not a reading of absence; the terminal branch is unaffected and "
                       "this host is not in a terminal state (%r)." % status)
    if systems:
        short = [s for s in systems if s not in set(cofold_complete_systems or ())]
        if not short:
            return True, ("work banked, no remaining role — every model for arm(s) %s is measured in S3 and "
                          "this host was scoped to those arms at launch, so it cannot contribute to any "
                          "other" % ", ".join(systems))
    elif label in set(done_units or ()):
        return True, ("work banked, no remaining role — this unit's production-conforming leg record is in "
                      "S3 (selcal_panel.production_leg_check)")
    # ★ THE HOST'S OWN TERMINUS. It must NAME THIS INSTANCE: the two arms' co-fold hosts share one
    # `$RESULT_S3`, so the shared `phase.txt` describes whichever wrote last and says nothing about the other.
    # `phase-<id>.txt` is per host. A marker naming a DIFFERENT instance is a fossil and condemns nobody.
    ph = str(host_phase or "")
    if ph.startswith("done rc=") and iid and ("instance=%s" % iid) in ph:
        return True, ("host reported its terminus — its own phase marker reads %r, and the pipeline writes "
                      "that immediately before `exit`, so this container's work is over whatever the rc. "
                      "Nothing it can still produce is being bought." % ph[:90])
    if systems:
        return False, ("SPARED — arm(s) %s still owe models (%s complete) and this host has not reported a "
                       "terminus. Mid-work hosts are never reaped on idleness."
                       % (", ".join(systems), ", ".join(sorted(cofold_complete_systems or ())) or "none"))
    return False, ("SPARED — no landed leg in S3 and no host-written terminus for %s; status %r."
                   % (label or "(unlabelled)", status))


def _host_phase(s3, bucket, prefix, instance_id):
    """This host's OWN co-fold phase marker, or "" when there is none.

    Falls back to the SHARED `phase.txt` only when that file names this very instance — the two arms
    overwrite it in turn, so it is evidence about at most one of them and a fossil for the rest."""
    for keyname in ("%s/phase-%s.txt" % (prefix, instance_id), "%s/phase.txt" % prefix):
        try:
            ph = s3.get_object(Bucket=bucket, Key=keyname)["Body"].read().decode("utf-8", "replace").strip()
        except Exception:  # noqa: BLE001 — an ABSENT marker is absent, not a terminus
            continue
        if ("instance=%s" % instance_id) in ph:
            return ph
    return ""


def mode_reap(bucket=None, stop_all=False, cofold_prefix=None):
    """Destroy this lane's finished / terminal hosts — recording the bill BEFORE the DELETE, and leaving a
    DURABLE record of what it reaped AND what it spared.

    ⛔ THE HOST CANNOT STOP ITS OWN BILLING; only the control plane can (CLAUDE.md §6, measured). The EXIT
    trap and `autoteardown.py` stop the JOB, not the METER, and a crash-looping container never returns at
    all — so the reap is this function's job, from CI, where the key lives.

    ★★ AND IT WRITES `selcal-reap.json` ON EVERY TICK, buying nothing included. A reap that only printed was
    how run 30707211425 could succeed, destroy nothing and leave no trace of the decision: the lane's census
    had been silent for 77 minutes and an ACCOUNT-level alarm, not this lane, is what noticed two idle hosts.
    A reaper with no artifact is indistinguishable from a reaper that never ran."""
    bucket = bucket or BUCKET
    prefix = (cofold_prefix or SP.COFOLD_PREFIX).strip("/")
    key = os.environ.get("VAST_API_KEY")
    _live, mine = _live_labels(key)
    import boto3
    s3 = boto3.client("s3")
    # ★ THE S3 READ IS FALLIBLE AND ITS FAILURE IS A DISTINCT STATE, not an empty result. `_done_units` and
    # `_cofold_census` both page S3; if that throws, "no unit is done" and "we could not find out" would
    # otherwise look identical — and the first of those is a reason to spare while the second is a reason to
    # go and read again.
    s3_readable, done, census = True, set(), None
    try:
        done, _records = _done_units(s3, bucket)
        census = _cofold_census(s3, bucket, prefix)
    except Exception as e:  # noqa: BLE001
        s3_readable = False
        print("[selcal-reap] ⚠ the S3 census is UNREADABLE (%s: %s) — nothing will be reaped on banked work. "
              "An absent reading is not a reading of absence. Terminal hosts are still destroyed, because "
              "their evidence is the instance record." % (type(e).__name__, e), flush=True)
    complete_systems = tuple(sorted(
        arm.cofold_system for arm in SP.ARMS
        if census and len(census["per_arm"].get(arm.arm_id, [])) >= len(SP.COFOLD_MODEL_SEEDS)))
    stopped, kept, failed = [], [], []
    for inst in mine:
        label, iid = str(inst.get("label") or ""), str(inst.get("id") or "")
        ph = _host_phase(s3, bucket, prefix, iid) if s3_readable else ""
        reap, why = reap_decision(inst, done, complete_systems, s3_readable, host_phase=ph,
                                  stop_all=stop_all, prefix=prefix)
        row = {"instance": iid, "label": label, "status": inst.get("actual_status"),
               "uptime_min": (round(rental_uptime_s(inst) / 60.0, 1)
                              if rental_uptime_s(inst) is not None else None),
               "dph_total": inst.get("dph_total"), "host_phase": ph or None, "why": why}
        if not reap:
            kept.append(row)
            print("[selcal-reap] SPARED %s (%s) — %s" % (iid, label, why), flush=True)
            continue
        # ⛔ LEDGER FIRST. The DELETE is the last moment this record exists; a rental that bills and leaves no
        # trace has already happened on this account (instance 46459452, overnight).
        _ledger_record(inst, why)
        try:
            _vast_request("DELETE", "/instances/%s/" % inst.get("id"), key, body={})
            stopped.append(row)
            print("[selcal-reap] DESTROYED %s (%s) — %s" % (iid, label, why), flush=True)
        except Exception as e:  # noqa: BLE001
            row["destroy_error"] = "%s: %s" % (type(e).__name__, e)
            failed.append(row)
            print("[selcal-reap] ⛔ WARN could not destroy %s: %s — IT IS STILL BILLING" % (iid, e), flush=True)
    doc = {"_what": "What the sensitivity-control lane's reaper destroyed, and what it SPARED and why. "
                    "Written on every tick, destroying nothing included — a reaper with no artifact is "
                    "indistinguishable from a reaper that never ran.",
           "_rule": "CLAUDE.md §6 — the host cannot stop its own billing, only the control plane can; and "
                    "GPU idleness NEVER condemns a box, only banked work / a host-written terminus / a "
                    "terminal state does.",
           "lane": LANE, "utc": _utcnow(), "stop_all": bool(stop_all), "cofold_prefix": prefix,
           "s3_census_readable": s3_readable,
           "cofold_arms_complete": list(complete_systems),
           "cofold_models_per_arm": (census or {}).get("n_models_per_arm"),
           "md_units_landed": sorted(done),
           "destroyed": stopped, "spared": kept, "destroy_failed": failed,
           "n_destroyed": len(stopped), "n_spared": len(kept), "n_destroy_failed": len(failed)}
    _write(REAP_READOUT, doc)
    print("[selcal-reap] %d destroyed, %d spared, %d destroy-failed. Arms complete in S3: %s. Readout: %s"
          % (len(stopped), len(kept), len(failed), list(complete_systems) or "none",
             os.path.basename(REAP_READOUT)), flush=True)
    if failed:
        print("::error title=SELCAL REAP COULD NOT DESTROY::%d host(s) were judged reapable and the DELETE "
              "failed — they are STILL BILLING. See %s."
              % (len(failed), os.path.basename(REAP_READOUT)), flush=True)
    return 0


#: The workflow this lane dispatches itself through. One home, so a rename cannot leave the chain firing at
#: a file that no longer exists.
WORKFLOW_FILE = "selectivity-control-vast.yml"


def self_dispatch(mode, inputs=None, ref=None):
    """Fire the next rung of this lane's own ladder, from inside a run. Best-effort; never raises.

    ★★ WHY THE CHAIN EXISTS, and it is a spend-safety mechanism rather than a convenience. A supervision job
    has a finite window; when it ends, the hosts it was watching do NOT stop — the host cannot stop its own
    billing, only the control plane can (CLAUDE.md §6, measured). So a watch that simply exits converts a
    supervised fleet into an unsupervised one at a predictable moment, which is exactly the unattended-rental
    leak this lane's ledger exists to make visible. Re-arming itself closes that. On COMPLETION it advances
    the ladder instead, so the free CI staging shakeout runs without waiting for an agent to be awake.

    ⚠ IT DISPATCHES, IT DOES NOT DECIDE. Every rung it can reach is either $0 or itself gated: `stage_test`
    rents nothing, and every rental still faces the market gate and the per-offer buy line."""
    import urllib.error
    import urllib.request
    tok = os.environ.get("GITHUB_TOKEN")
    if not tok:
        print("[selcal-chain] no GITHUB_TOKEN — cannot arm the next rung (%s). Dispatch it by hand." % mode,
              flush=True)
        return False
    body = json.dumps({"ref": ref or os.environ.get("GIT_BRANCH") or "main",
                       "inputs": dict({"mode": mode}, **(inputs or {}))}).encode()
    req = urllib.request.Request(
        "https://api.github.com/repos/trimcrae/Rare-cancers/actions/workflows/%s/dispatches" % WORKFLOW_FILE,
        data=body, method="POST",
        headers={"Authorization": "Bearer %s" % tok, "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json", "User-Agent": "selcal-lane"})
    try:
        urllib.request.urlopen(req, timeout=30)
        print("[selcal-chain] armed the next rung: mode=%s" % mode, flush=True)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print("[selcal-chain] could NOT arm mode=%s (%s) — say so rather than assume it fired" % (mode, e),
              flush=True)
        return False


def _tick_publish(paths, message, branch=None):
    """Commit + push these artifacts from INSIDE a long-running supervision loop. Never raises.

    ⛔ A LONG WATCH ONLY COMMITS WHEN IT ENDS, AND THAT IS THE STALENESS BUG WEARING A DIFFERENT HAT. The
    workflow's commit step is a separate step, so it runs only after this python process exits: a 58-minute
    watch that faithfully rewrites the census every 3 minutes still leaves the LANE's census frozen on `main`
    for 58 minutes — indistinguishable from the 77-minute silence on 2026-08-01 that this whole fix exists to
    end. Writing a file the outside world cannot see is not a heartbeat.

    ⚠ LAST WRITER WINS, exactly as the workflow's commit step does it, and for the same reason: these are
    regenerated snapshots with more than one writer, and merging two censuses taken at different instants
    produces a census that describes no instant. So: keep our bytes, reset to the remote, lay them back,
    commit, push. `git reset --hard` is safe here — this module is already imported, and a CI checkout has no
    other uncommitted work.

    ⛔⛔ AND IT MAY ONLY PUBLISH WHAT THIS PROCESS ACTUALLY WROTE (2026-08-02, measured twice in one night).
    Stamping every path it is handed is the OTHER way a publish reverts somebody, and it does not need a
    conflict to do it — a clean older copy applies onto a newer one silently:

        00:41:37Z  a `collect` tick measured S3 and published `landed: 17`
        00:42:44Z  THIS FUNCTION, inside a watch started at 23:05 whose checkout held `landed: 0`, stamped
                   it back to 0 with a five-hour-old timestamp

    and it had already done that once at 22:16:50Z, leaving the lane's official census reading ZERO for five
    hours while seventeen legs sat banked in S3. ⚠ THE WORKFLOW-LEVEL FIX DOES NOT REACH HERE: this is a
    python publisher inside a long-running loop, not a workflow step, so `publish_artifacts.sh` never sees
    it and `test_no_hand_rolled_publish` — which scans YAML — vouched for a lane it could not inspect.

    The rule is the same one, asked of the process rather than the job: is our copy DIFFERENT from the commit
    this checkout is on? If not, this run did not write it, and upstream's copy stays.

    Best-effort by construction: supervision must never die because a push raced."""
    import subprocess
    branch = branch or os.environ.get("GIT_BRANCH") or "main"
    root = os.path.dirname(os.path.dirname(HERE))

    def _g(*a):
        return subprocess.run(["git", "-C", root, *a], capture_output=True, text=True)

    base = (_g("rev-parse", "HEAD").stdout or "").strip()
    keep, skipped = {}, []
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p, "rb") as fh:
            mine = fh.read()
        # ⚠ FAILS OPEN. If the base cannot be read, or the file is not in it, PUBLISH — never silently drop
        # work on a bookkeeping failure. Only a proven byte-identical match declines.
        if base:
            rel = os.path.relpath(p, root)
            was = subprocess.run(["git", "-C", root, "show", "%s:%s" % (base, rel)],
                                 capture_output=True)
            if was.returncode == 0 and was.stdout == mine:
                skipped.append(rel)
                continue
        keep[p] = mine
    if skipped:
        # Say so: a path silently dropped from a publish looks exactly like the reverse bug.
        print("[selcal-tick-publish] unchanged since checkout, upstream's kept: %s" % ", ".join(skipped),
              flush=True)
    if not keep:
        # ⚠ STILL A HEARTBEAT. Every path was somebody else's; commit empty so the tick is still dated —
        # a healthy loop that happened to write nothing must not look like one that stopped.
        try:
            if _g("fetch", "origin", branch).returncode == 0:
                _g("reset", "--hard", "origin/%s" % branch)
                _g("-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com",
                   "commit", "--allow-empty", "-m", message)
                return _g("push", "origin", "HEAD:%s" % branch).returncode == 0
        except Exception:  # noqa: BLE001
            pass
        return False

    g = _g
    try:
        for attempt in range(3):
            if g("fetch", "origin", branch).returncode:
                return False
            g("reset", "--hard", "origin/%s" % branch)
            for p, b in keep.items():
                with open(p, "wb") as fh:
                    fh.write(b)
            g("add", *sorted(keep))
            g("-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com",
              "commit", "--allow-empty", "-m", message)
            if g("push", "origin", "HEAD:%s" % branch).returncode == 0:
                return True
            time.sleep(2 * (attempt + 1))
    except Exception as e:  # noqa: BLE001 — a failed heartbeat must not stop the supervision it reports on
        print("[selcal-tick-publish] could not publish (%s: %s) — the watch continues" % (type(e).__name__, e),
              flush=True)
    return False


def _publish_board(s3, bucket, prefix, census, hosts, landed=None, n_units=None):
    """Publish this lane's in-flight board fragment. Returns the paths to commit; NEVER raises.

    Separate from `_tick_publish` on purpose: the census is this lane's own record and the board is a
    SHARED, derived artifact, so a fault in the board renderer must not be able to stop the lane recording
    what it measured — and a supervision loop must never die of a reporting bug."""
    try:
        import selcal_board as B
        arrivals = B.cofold_arrivals(s3, bucket, prefix)
        # ⚠ `landed`/`n_units` ride along so the MD rows can carry a real `N/M landed` denominator. Left
        # as None they render UNKNOWN rather than 0 — an unmeasured count is not a count of zero (§4).
        frag, board = B.publish(census, arrivals, hosts=hosts, landed=landed, n_units=n_units)
        return [frag, board]
    except Exception as e:  # noqa: BLE001
        print("[selcal-board] could not publish the in-flight fragment (%s: %s) — the watch continues, and "
              "the board will render this lane STALE rather than absent" % (type(e).__name__, e), flush=True)
        return []


def mode_cofold_watch(bucket=None, minutes=None, cofold_prefix=None):
    """Supervise the co-fold hosts from CI until every (arm, seed) has landed — then REAP them.

    ★★ THIS EXISTS BECAUSE A `schedule:` CRON DOES NOT SUPERVISE A BILLING FLEET (CLAUDE.md §6, measured: 25
    of the last 30 ticks on a sibling lane were manual dispatches). While a host is billing, supervision is
    somebody's job; making it a long-running CI job means it does not depend on an agent staying awake, and
    the REAP AT THE END is what stops a finished co-fold leaving two idle GPUs on the meter — the host cannot
    stop its own billing, only the control plane can.

    Every tick is a PROGRESS check: phase, GPU util, and the WRITE signal (new objects in S3), because GPU
    idleness never condemns a box — Boltz's MSA stage is legitimately network-bound."""
    import boto3
    bucket = bucket or BUCKET
    prefix = (cofold_prefix or SP.COFOLD_PREFIX).strip("/")
    s3 = boto3.client("s3")
    minutes = float(minutes or os.environ.get("WATCH_MINUTES") or 55)
    interval = float(os.environ.get("SELCAL_WATCH_INTERVAL_S", "180"))
    t_start = time.time()
    t_end = t_start + minutes * 60
    # ★★ A WATCH MAY NOT DECLARE "NO HOST" ON ITS FIRST LOOK. `mode_cofold` self-dispatches this watch the
    # moment it has submitted, and a dispatched run takes tens of seconds to reach python — but a Vast
    # instance is not necessarily LISTED the instant `submit` returns either. So the first ticks race the
    # rental, and a watch that exits on tick 1 hands a host that is about to appear to nobody. Two readable
    # observations AND a grace window: neither alone is evidence.
    grace_s = float(os.environ.get("SELCAL_WATCH_GRACE_S", "300"))
    prev_objs, stalls, no_host_strikes = None, 0, 0
    while time.time() < t_end:
        cen = _cofold_census(s3, bucket, prefix)
        try:
            page = s3.list_objects_v2(Bucket=bucket, Prefix="%s/" % prefix, MaxKeys=1000)
            objs = page.get("Contents") or []
        except Exception:  # noqa: BLE001
            objs = []
        newest = max((o["LastModified"] for o in objs), default=None)
        # ★★ REAP ON EVERY TICK, NOT ONLY AT COMPLETION — THIS IS THE SECOND HALF OF THE 2026-08-01 LEAK.
        # The reap below used to sit inside `if cen["complete"]`, so a fleet where ONE arm had finished and
        # the other had not kept BOTH hosts: the finished arm's box billed for 85+ minutes with all six of
        # its models already durable in S3, because the panel as a whole was incomplete. That is backwards —
        # a host scoped to a finished arm cannot contribute to the missing one, and `reap_decision` is what
        # says so per host instead of per panel. It runs BEFORE `mine` is read so the loop's own liveness
        # test sees the post-reap board rather than counting a box it has just destroyed.
        mode_reap(bucket, cofold_prefix=prefix)
        readable, _live, mine = _live_labels_checked()
        age_min = (round((time.time() - newest.timestamp()) / 60.0, 1) if newest else None)
        print("[selcal-cofold-watch] %s | models %s | %d S3 object(s), newest %s min old | hosts %s"
              % (time.strftime("%H:%M:%SZ", time.gmtime()), cen["n_models_per_arm"], len(objs), age_min,
                 [(i.get("id"), i.get("actual_status"), i.get("gpu_util")) for i in mine]), flush=True)
        # ⚠ THE LANE'S OWN STALENESS SIGNAL, WRITTEN EVERY TICK. Its census went silent for 77 minutes on
        # 2026-08-01 while two hosts billed, and an ACCOUNT-level alarm — not this lane — is what noticed. A
        # supervision loop that only prints leaves nothing a later reader can date.
        cen.update({"_what": "Which co-fold models exist for the sensitivity control, measured from S3.",
                    "utc": _utcnow(), "bucket": bucket, "written_by": "cofold_watch tick",
                    "n_s3_objects": len(objs),
                    "newest_object_utc": (newest.strftime("%Y-%m-%dT%H:%M:%SZ") if newest else None),
                    "newest_object_age_min": age_min,
                    "instances": [{"id": i.get("id"), "status": i.get("actual_status"),
                                   "gpu_util": i.get("gpu_util"), "dph_total": i.get("dph_total"),
                                   "uptime_min": (round(rental_uptime_s(i) / 60.0, 1)
                                                  if rental_uptime_s(i) is not None else None)}
                                  for i in mine]})
        _write(COFOLD_CENSUS, cen)
        # ★★ AND PUBLISHED, not merely written. The workflow's commit step runs only after this process
        # exits, so without this a 58-minute watch leaves the lane's census frozen on `main` for 58 minutes —
        # which is the 77-minute silence of 2026-08-01 with a different number on it.
        # ⚠ AND THE IN-FLIGHT BOARD, ON THE SAME TICK. A lane whose progress is not on the all-lane board has
        # no derived % and no derived ETA anywhere, and today that vacuum was filled with a prose estimate
        # quoted beside real numbers for six reports (`selcal_board`). Best-effort: a board write must never
        # end the supervision it describes.
        board_paths = _publish_board(s3, bucket, prefix, cen, mine)
        _tick_publish([COFOLD_CENSUS, REAP_READOUT, PRICE_LEDGER] + board_paths,
                      "selcal cofold_watch: supervision tick (models %s, %d host(s))"
                      % (cen["n_models_per_arm"], len(mine)))
        if cen["complete"]:
            print("[selcal-cofold-watch] ✅ every (arm, seed) has a co-fold — reaping the hosts.", flush=True)
            mode_reap(bucket, stop_all=True, cofold_prefix=prefix)
            # ⛔ AND VERIFY THE REAP BEFORE EXITING. "I asked the control plane to destroy them" is not
            # "they are destroyed", and this is the one exit path taken on the happy day — so a reap that
            # half-worked would leave a host billing at the exact moment supervision stops. Same rule as
            # everywhere else: check the thing only the real outcome can produce.
            left_readable, _l, left = _live_labels_checked()
            if left:
                print("[selcal-cofold-watch] ⚠ the panel is complete but %d host(s) survived the reap — "
                      "re-arming rather than exiting on top of a billing box." % len(left), flush=True)
                if not self_dispatch("cofold_watch", {"watch_minutes": str(int(minutes))}):
                    print("::error title=SELCAL SUPERVISION NOT RE-ARMED::the panel is complete, %d host(s) "
                          "survived the reap, and this watch could not dispatch its successor. Dispatch "
                          "`stop` by hand." % len(left), flush=True)
            elif not left_readable:
                print("[selcal-cofold-watch] ⚠ the reap ran but the control plane did not answer, so whether "
                      "any host survived is UNKNOWN — re-arming, because an unreadable board is not an empty "
                      "one (CLAUDE.md §4).", flush=True)
                self_dispatch("cofold_watch", {"watch_minutes": str(int(minutes))})
            # ADVANCE THE LADDER: `stage_test` is $0 and rents nothing, and it is the rung that catches a
            # staging fault for free before any MD host is bought.
            self_dispatch("stage_test")
            return 0
        # ★★ THE PATH THAT COST THE 2026-08-01 SUPERVISION GAP ITS DIAGNOSIS, AND IT WAS EXERCISED THAT DAY.
        # MEASURED, run 30710853581 job 91397937573: `MODE: cofold_watch`, `WATCH_MINUTES: 58`, and the
        # `Rent` step ran 17:41:12Z -> 17:44:17Z and FAILED — 3.1 minutes into a 58-minute window, with the
        # commit step succeeding. The only non-zero return reachable that early was this one; the re-arm
        # below was never REACHED, because it is lexically after the loop and this returned from inside it.
        # It used to read `if not mine: return 1` — an immediate, unconditional exit with NO re-arm, a few
        # lines above a docstring saying this function "re-arms itself". Both were true of DIFFERENT paths,
        # which is why reading the docstring instead of the code produced a wrong story. Two defects lived
        # here:
        #   (a) `mine` is empty when the API FAILS as well as when no host exists (§4), so one Vast blip
        #       ended supervision of a host that was still billing;
        #   (b) it fired on a single observation, so it also raced `mode_cofold`'s own rental.
        # Now: only a READABLE, REPEATED, post-grace absence counts, and the exit still says the lane needs a
        # re-launch — but `supervisor_resurrect.py` is what makes that recoverable without an agent, because
        # nothing INSIDE a loop can be responsible for the case where the loop is gone.
        if not mine and readable and (time.time() - t_start) > grace_s:
            no_host_strikes += 1
            if no_host_strikes >= 2:
                print("[selcal-cofold-watch] ⛔ no co-fold host is alive on two consecutive READABLE checks "
                      "and the set is incomplete — the lane needs a re-launch. Exiting so this cannot read "
                      "as a finished watch. Nothing is billing, so nothing is left unwatched.", flush=True)
                return 1
            print("[selcal-cofold-watch] no host on this check — one strike, not a verdict. A single "
                  "observation is not evidence a fleet is gone.", flush=True)
        elif not mine and not readable:
            print("[selcal-cofold-watch] ⚠ the control plane did not answer this tick, so 'no host' is "
                  "UNREADABLE, not empty — continuing to watch rather than exiting blind.", flush=True)
        else:
            no_host_strikes = 0
        # THE WRITE SIGNAL is what a stall verdict rests on, not gpu_util. Two consecutive ticks with no new
        # object AND nothing newer than the interval is a real absence of work.
        stalls = stalls + 1 if (prev_objs is not None and len(objs) == prev_objs
                                and (age_min or 0) * 60 > interval * 1.5) else 0
        prev_objs = len(objs)
        if stalls >= 2:
            print("::warning title=SELCAL CO-FOLD STALL::no new S3 object across two consecutive checks and "
                  "nothing written for %s min. This is a measured absence of WRITES, not GPU idleness."
                  % age_min, flush=True)
        time.sleep(interval)
    # ⛔ A WATCH THAT SIMPLY EXITS TURNS A SUPERVISED FLEET INTO AN UNSUPERVISED ONE. Re-arm.
    # ⚠ AND AN UNREADABLE BOARD RE-ARMS TOO. `_live_labels` alone cannot tell "no host" from "no answer", so
    # the window-elapsed exit had the same §4 hole as the early one: an API blip in this one call would end
    # the chain permanently while a host billed. Re-arming costs a $0 run that exits in ~30 s if there is
    # genuinely nothing to watch; not re-arming costs an unwatched meter.
    readable, _live, mine = _live_labels_checked()
    if not readable:
        print("[selcal-cofold-watch] ⚠ window elapsed and the control plane did not answer — re-arming, "
              "because an unreadable board is not an empty one.", flush=True)
        if not self_dispatch("cofold_watch", {"watch_minutes": str(int(minutes))}):
            print("::error title=SELCAL SUPERVISION NOT RE-ARMED::the window elapsed, the host board was "
                  "unreadable, and this watch could not dispatch its successor. Dispatch `cofold_watch` "
                  "(or `stop`) by hand.", flush=True)
            return 1
    elif mine:
        print("[selcal-cofold-watch] window elapsed with %d host(s) still billing — re-arming supervision "
              "rather than leaving them unwatched." % len(mine), flush=True)
        if not self_dispatch("cofold_watch", {"watch_minutes": str(int(minutes))}):
            print("::error title=SELCAL SUPERVISION NOT RE-ARMED::%d co-fold host(s) are billing and this "
                  "watch could not dispatch its successor. Dispatch `cofold_watch` (or `stop`) by hand."
                  % len(mine), flush=True)
            return 1
    else:
        print("[selcal-cofold-watch] window elapsed and no host is alive — nothing is billing.", flush=True)
    return 0


def mode_watch(bucket=None, minutes=None):
    """The supervision job. A `schedule:` cron does NOT supervise a billing fleet (CLAUDE.md §6, measured:
    25 of the last 30 ticks on a sibling lane were manual dispatches), so supervision is a long-running job
    that makes a real PROGRESS check every 3 minutes and reaps what has finished."""
    import boto3
    bucket = bucket or BUCKET
    s3 = boto3.client("s3")
    minutes = float(minutes or os.environ.get("WATCH_MINUTES") or 55)
    t_end = time.time() + minutes * 60
    prev = {}
    stalls = {}
    last_replace = 0.0
    while time.time() < t_end:
        live, mine = _live_labels()
        done, _records = _done_units(s3, bucket)
        now = {}
        for inst in mine:
            label = str(inst.get("label") or "")
            ph = _phase(s3, bucket, label)
            util = inst.get("gpu_util")
            now[label] = (ph, util)
            moved = prev.get(label, (None, None))[0] != ph
            idle = (util is not None and float(util or 0) < 1.0)
            if not moved and idle:
                stalls[label] = stalls.get(label, 0) + 1
            else:
                stalls[label] = 0
            print("[selcal-watch] %s %s | phase=%r gpu_util=%s | phase_moved=%s strikes=%d"
                  % (time.strftime("%H:%M:%SZ", time.gmtime()), label, ph[:70], util, moved, stalls[label]),
                  flush=True)
            if stalls[label] >= 2:
                # Frozen phase + idle GPU across two consecutive checks. Say so loudly; the diagnosis is a
                # human/agent step, but an unnoticed stall is what this job exists to prevent.
                print("::warning title=SELCAL STALL::%s has not moved phase and its GPU has been idle across "
                      "two consecutive checks. Phase %r." % (label, ph[:120]), flush=True)
        prev = now
        print("[selcal-watch] landed %d/%d, live %d" % (len(done), len(SP.enumerate_units()), len(mine)),
              flush=True)
        if len(done) >= len(SP.enumerate_units()):
            # ★★ THE PANEL'S TERMINUS IS A VERDICT, NOT AN EMPTY HOST LIST (2026-08-01). This branch used to
            # reap and `return 0`, so the moment the 24th leg landed the lane went quiet with its criterion
            # UNSCORED — the whole point of the panel sitting in S3 waiting for somebody to notice and
            # dispatch `collect` by hand. That is the same "needs an agent awake" dependency CLAUDE.md §6
            # exists to remove, and it sits at the one place where noticing matters most.
            #
            # ⚠ REAP FIRST, SCORE SECOND. Only the control plane can stop the meter, and scoring is a pure
            # S3 read that cannot fail in a way worth holding billing for.
            #
            # ⛔ THIS IS NOT AN INTERIM ANALYSIS. `mode_collect` suppresses the tier unless `panel_complete`,
            # and this branch is reached only when every unit has a production-checked leg — the condition
            # the prereg's no-peeking rule (`PASS_CRITERION["no_interim_analysis"]`) names. Scoring here is
            # the criterion firing when it said it would, not a peek.
            print("[selcal-watch] panel complete — reaping, then SCORING the frozen criterion.", flush=True)
            mode_reap(bucket)
            try:
                mode_collect(bucket)
            except Exception as e:  # noqa: BLE001 — a scoring fault must not lose the reap or the readouts
                print("::error title=SELCAL PANEL UNSCORED::every unit landed but the verdict could not be "
                      "computed (%s: %s). The legs are safe in S3; dispatch `mode=collect` to score them."
                      % (type(e).__name__, e), flush=True)
            _tick_publish([REAP_READOUT, PRICE_LEDGER, COLLECT_READOUT, VERDICT_READOUT],
                          "selcal: PANEL COMPLETE — frozen criterion scored (CI)")
            return 0
        mode_reap(bucket)
        # ★★ REAPING WITHOUT RE-PLACING IS NOT SUPERVISION — IT IS A SLOW LEAK (2026-08-01).
        # This loop collected, reaped and published every 3 minutes and NEVER dispatched `launch`, so the
        # panel could only converge if every host banked its leg on the very first attempt. It does not: a
        # leg lands, the reaper destroys its host, and the unit is left with neither a result nor a host —
        # a permanent hole no tick could fill. Measured that evening: 24 of 24 units were covered at 6:13 PM,
        # and thirteen minutes later 8 had landed, 11 were live and **5 units had nothing at all**, with a
        # perfectly green watch ticking over them. An agent hand-dispatched `launch` three times to close
        # those gaps, which is precisely the dependency CLAUDE.md §6 says a fleet must not have.
        # ⚠ IT DISPATCHES, IT DOES NOT DECIDE — the same contract `self_dispatch` already carries. Every
        # rental it can cause still faces the market gate, the board-level $/ns hold and the per-offer buy
        # line on the spec, and `mode_launch` is idempotent (it skips units that are done or live), so the
        # worst case of a spurious dispatch is a $0 `nothing-to-buy` gate record.
        need = [SP.unit_name(a, m, r) for a, m, r in SP.enumerate_units()
                if SP.unit_name(a, m, r) not in done and SP.unit_name(a, m, r) not in live]
        if need and (time.time() - last_replace) >= _REPLACE_MIN_S:
            # ⚠ THE INTERVAL IS NOT POLITENESS, IT IS CORRECTNESS. A freshly rented host takes ~1-2 min to
            # appear on the account, and until it does this same computation still sees its unit as needing
            # one. Ticking every 3 minutes without this guard would re-rent the same units on the next pass,
            # i.e. pay twice for one leg — the opposite failure, and the expensive one.
            last_replace = time.time()
            print("[selcal-watch] %d unit(s) have neither a landed leg nor a live host (%s%s) — dispatching "
                  "`launch` to re-place them." % (len(need), ", ".join(need[:6]),
                                                  "…" if len(need) > 6 else ""), flush=True)
            if not self_dispatch("launch"):
                print("::error title=SELCAL GAP NOT RE-PLACED::%d unit(s) have no result and no host and the "
                      "`launch` dispatch failed. The panel cannot complete until one is dispatched by hand."
                      % len(need), flush=True)
        elif need:
            print("[selcal-watch] %d unit(s) awaiting re-placement; last dispatch %.1f min ago, holding "
                  "until %.0f min so a rental in flight is not double-bought."
                  % (len(need), (time.time() - last_replace) / 60.0, _REPLACE_MIN_S / 60.0), flush=True)
        # ★★ AND THE IN-FLIGHT BOARD, WHICH THIS LOOP DID NOT WRITE AT ALL (2026-08-01, ~6 min after the
        # lane's first MD host started billing). `mode_cofold_watch` publishes a board fragment on every
        # tick; this loop — the one that supervises the legs that COST LADDER DOLLARS — published only a
        # commit heartbeat. So the all-lane board carried this lane's 44-minute-old CO-FOLD rows, marked
        # STALE, while an MD leg ran underneath with no row of its own. A billing leg with no board row is
        # the exact failure the board exists to prevent, and it is how a prose ETA for this lane survived
        # six consecutive reports.
        try:
            _cen = _cofold_census(s3, bucket, SP.COFOLD_PREFIX.strip("/"))
        except Exception as _e:  # noqa: BLE001 — the co-fold rows degrade; the MD rows are the point here
            print("[selcal-watch] co-fold census unread for the board (%s) — its rows will say so" % _e,
                  flush=True)
            _cen = {}
        board_paths = _publish_board(s3, bucket, SP.COFOLD_PREFIX.strip("/"), _cen, mine,
                                     landed=len(done), n_units=len(SP.enumerate_units()))
        # Published per tick for the same reason as the co-fold watch: a heartbeat nobody outside the runner
        # can see is not a heartbeat.
        # ★★ RECOMPUTE COLLECT, DO NOT MERELY RE-PUBLISH IT (2026-08-02). This loop listed COLLECT_READOUT
        # in its publish set while never calling `mode_collect`, so every tick re-published whatever copy the
        # checkout happened to hold. That is harmless right up until something knocks the artifact backwards
        # — and something did: a `status` tick reverted it to `landed: 0` at 22:16:50Z, and because nothing
        # here recomputes it, the lane's official "what has landed" readout sat at ZERO for five hours while
        # SEVENTEEN legs were banked in S3. The publish guard now added upstream makes that WORSE, not
        # better, in this one spot: an unchanged file is correctly skipped, so a stale copy would never be
        # corrected by ticking. A file you publish is a file you must produce.
        #
        # ⛔ NOT AN INTERIM ANALYSIS. `mode_collect` SUPPRESSES the tier unless `panel_complete` — it writes
        # the evidence and withholds the label, which is exactly what the no-peeking rule requires. Running
        # it per tick keeps the census honest without ever emitting a verdict early.
        try:
            mode_collect(bucket)
        except Exception as e:  # noqa: BLE001 — a census fault must not end supervision of a billing fleet
            print("[selcal-watch] collect readout not refreshed this tick (%s: %s); the reap and board still "
                  "publish, and the terminus reads S3 directly rather than this file."
                  % (type(e).__name__, e), flush=True)
        _tick_publish([REAP_READOUT, PRICE_LEDGER, COLLECT_READOUT, VERDICT_READOUT] + board_paths,
                      "selcal watch: supervision tick (%d/%d landed, %d host(s))"
                      % (len(done), len(SP.enumerate_units()), len(mine)))
        time.sleep(float(os.environ.get("SELCAL_WATCH_INTERVAL_S", "180")))

    # ★★ THE WINDOW ENDING IS NOT THE WORK ENDING — RE-ARM (2026-08-01). Every early return above is a
    # TERMINUS (the panel completed); falling out of the loop is only this JOB's 55-minute clock expiring,
    # and the hosts it was watching do not stop when it does — the host cannot stop its own billing, only
    # the control plane can (CLAUDE.md §6, measured). `self_dispatch`'s own docstring states this rule —
    # "a watch that simply exits converts a supervised fleet into an unsupervised one at a predictable
    # moment" — and `mode_cofold_watch` obeys it in four places, while THIS loop, the one supervising the
    # legs that cost ladder dollars, simply returned 0. So at the end of every window the fleet became
    # unwatched until an agent noticed, which is the dependency §6 exists to remove.
    live, _mine = _live_labels()
    done, _records = _done_units(s3, bucket)
    left = [SP.unit_name(a, m, r) for a, m, r in SP.enumerate_units() if SP.unit_name(a, m, r) not in done]
    if not left:
        print("[selcal-watch] window closed with every unit landed — nothing left to supervise.", flush=True)
        return 0
    # ⚠ RE-ARM ON UNFINISHED WORK, NOT ON LIVE HOSTS. Those differ exactly when the panel has a gap and no
    # host in it — which is the state the re-placement above exists to fix and therefore the state that most
    # needs a next tick. Re-arming only when a host is live would stop supervision precisely when the lane
    # had stalled, and a stalled lane looks identical to a finished one from outside.
    print("[selcal-watch] window closed with %d unit(s) unfinished and %d host(s) live — re-arming."
          % (len(left), len(live)), flush=True)
    if not self_dispatch("watch"):
        print("::error title=SELCAL SUPERVISION ENDED::the watch window closed with %d unit(s) unfinished "
              "and %d host(s) still on the account, and the re-arm dispatch FAILED. Nothing is watching "
              "them: the host cannot stop its own billing. Dispatch `watch` (or `stop`) by hand."
              % (len(left), len(live)), flush=True)
    return 0


def mode_collect(bucket=None):
    """Pull every landed leg, SCORE it against the frozen criterion, and commit both readouts."""
    import boto3
    import selcal_gate as G
    bucket = bucket or BUCKET
    s3 = boto3.client("s3")
    done, records = _done_units(s3, bucket)
    legs = list(records.values())
    expected = [SP.unit_name(a, m, r) for a, m, r in SP.enumerate_units()]
    missing = [u for u in expected if u not in done]
    out = {"_what": "What the sensitivity-control panel has landed, measured from S3.",
           "utc": _utcnow(), "bucket": bucket, "prefix": SP.RESULT_PREFIX,
           "expected": len(expected), "landed": len(done), "missing": missing,
           "panel_complete": not missing,
           "records": sorted(records)}
    _write(COLLECT_READOUT, out)
    print("[selcal-collect] %d/%d units landed; %d missing" % (len(done), len(expected), len(missing)),
          flush=True)

    v = G.verdict(legs)
    v["utc"] = _utcnow()
    v["panel_complete"] = out["panel_complete"]
    if not out["panel_complete"]:
        # ⛔ NO INTERIM ANALYSIS. Peeking at a partial panel and stopping on a favourable p is the defect the
        # NR-V04 prereg's §4f exists to prevent, so the tier is SUPPRESSED — the evidence is still written,
        # because hiding it would be a different kind of dishonesty, but the label is withheld.
        # ⚠ ATOMIC, via the gate. The label and everything that discloses it are withheld together —
        # `next_step` states what a tier UNBLOCKS, which is the label in prose, and publishing it beside a
        # suppressed tier is the peek wearing a decision's clothes. One home: `suppress_for_incomplete_panel`.
        G.suppress_for_incomplete_panel(
            v, "The panel is incomplete (%d of %d units). The criterion forbids an interim verdict: a tier "
               "read off a partial panel, on a run that can still be extended, is the peeking defect. The "
               "evidence below is reported; the LABEL, and anything that discloses it, is withheld until the "
               "panel is complete or an arm is definitively short." % (len(done), len(expected)))
    _write(VERDICT_READOUT, v)
    print(G.render(v) if v.get("tier") else "[selcal-collect] verdict SUPPRESSED — %s" % v["suppression"],
          flush=True)
    return 0


def mode_gate_tick(bucket=None):
    """A $0 tick that PRICES the board and records the decision, whether or not anything is bought."""
    import boto3
    bucket = bucket or BUCKET
    s3 = boto3.client("s3")
    done, _records = _done_units(s3, bucket)
    live, _mine = _live_labels()
    expected = [SP.unit_name(a, m, r) for a, m, r in SP.enumerate_units()]
    need = [u for u in expected if u not in done and u not in live]
    if not need:
        _record_gate("nothing-to-buy", [], extra={"why": "every unit has a landed leg or a live host"})
        market_gate(1, bucket=bucket, price=False, what="MD legs")
        return 0
    hold, doc = market_gate(len(need), bucket=bucket, what="MD legs (%d)" % len(need))
    _record_gate("would-hold" if hold else "would-buy", need,
                 extra={"ratio_vs_basis": doc.get("ratio_vs_basis"),
                        "board_depth": doc.get("board_depth")})
    return 0


def mode_diag(bucket=None):
    """★ ROOT-CAUSE WITH A REAL DIAGNOSTIC (CLAUDE.md §4). Pull the CONTAINER's own stdout from Vast for every
    instance this lane owns, plus whatever S3 holds for it.

    A phase marker that was never written is an ABSENT READING, not a reading of absence: it says the host
    died before or during the step that writes the first mark, and it does NOT say which. The container log
    is the observation that discriminates."""
    import boto3
    from nrv04_vast_launch import _vast_instance_logs
    bucket = bucket or BUCKET
    key = os.environ.get("VAST_API_KEY")
    s3 = boto3.client("s3")
    try:
        insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    except Exception as e:  # noqa: BLE001
        print("[selcal-diag] could not list instances: %s" % e, flush=True)
        insts = []
    mine = [i for i in insts if str(i.get("label") or "").startswith(SP.LABEL_PREFIX)]
    if not mine:
        print("[selcal-diag] this lane owns no instances right now.", flush=True)
    for i in mine:
        print("=" * 100, flush=True)
        print("[selcal-diag] instance %s label=%s status=%s cur_state=%s gpu=%s gpu_util=%s dph=%s machine=%s"
              % (i.get("id"), i.get("label"), i.get("actual_status"), i.get("cur_state"), i.get("gpu_name"),
                 i.get("gpu_util"), i.get("dph_total"), i.get("machine_id")), flush=True)
        print("[selcal-diag] status_msg: %r" % (str(i.get("status_msg") or "")[:800]), flush=True)
        # ★ WAS IT OUTBID? The control-plane answer to "was this a spot preemption", imported rather than
        # re-derived — a lifetime of a few minutes is consistent with BOTH an outbid rental and a container
        # that died on its own, and only this field tells them apart.
        try:
            from nrv04_vast_launch import instance_outbid
            print("[selcal-diag] outbid check: %s" % (instance_outbid(i),), flush=True)
        except Exception as e:  # noqa: BLE001
            print("[selcal-diag] outbid check unavailable (%s) — an absent reading" % type(e).__name__,
                  flush=True)
        print("[selcal-diag] ---- CONTAINER LOG (Vast request_logs) ----", flush=True)
        print(_vast_instance_logs(key, i.get("id"), tail=400), flush=True)
    for pfx in (SP.COFOLD_PREFIX.strip("/"), SP.RESULT_PREFIX.strip("/")):
        keys = _s3_list(s3, bucket, "%s/" % pfx, limit=60)
        print("[selcal-diag] s3://%s/%s/ -> %d object(s): %s"
              % (bucket, pfx, len(keys), keys[:20]), flush=True)

    # ★★ THE BANKED LOG OF A LEG WHOSE HOST IS GONE — THE COMMONEST FORENSIC NEED, AND NEITHER `diag` NOR
    # `status` COVERED IT (2026-08-01). Both loops above iterate LIVE instances, so the moment a leg dies —
    # which is exactly when someone runs a diagnostic — this mode printed "this lane owns no instances right
    # now" and an object listing, and stopped. Measured on this lane's first MD leg: the listing showed
    # `attempts/run-20260801T193746Z.log` and `attempts/run-20260801T193835Z.log`, 49 s apart, i.e. restart
    # churn — and the one thing that says WHY was sitting in S3 unread, because nothing offered to read it.
    #
    # ⚠ `request_logs` CANNOT ANSWER THIS. The container is destroyed, so the control plane has no stdout to
    # return; S3 is the only surviving witness. An attempt log that does not exist is an ABSENT READING and
    # is reported as one — a leg can die before writing anything, and "no log" must not read as "no error".
    print("=" * 100, flush=True)
    print("[selcal-diag] ---- BANKED LOGS for units with NO live host (S3 is the only witness) ----",
          flush=True)
    live_units = {str(i.get("label") or "") for i in mine}
    try:
        with open(HANDLES) as _fh:
            _handles = json.load(_fh)
    except Exception:  # noqa: BLE001 — no handles file means nothing was ever rented, which is a fact
        _handles = []
    for h in (_handles if isinstance(_handles, list) else ()):
        unit = h.get("unit")
        if not unit or any(unit in lbl for lbl in live_units):
            continue
        base = "%s/%s" % (SP.RESULT_PREFIX.strip("/"), unit)
        attempts = _s3_list(s3, bucket, "%s/legs/%s/attempts/" % (SP.RESULT_PREFIX.strip("/"), unit),
                            limit=20)
        print("[selcal-diag] %s: rented %s on instance %s; %d attempt log(s) %s"
              % (unit, h.get("utc"), h.get("instance"), len(attempts),
                 "— MORE THAN ONE MEANS THE CONTAINER RESTARTED, which is a crash loop and not a "
                 "preemption" if len(attempts) > 1 else ""), flush=True)
        for k in ["%s/phase.txt" % base, "%s/run.log" % base] + attempts:
            try:
                body = s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode("utf-8", "replace")
            except Exception as e:  # noqa: BLE001
                print("  [%s] NOT READABLE (%s) — an absent reading, not evidence of a clean run"
                      % (k, type(e).__name__), flush=True)
                continue
            tail = body if len(body) < 4000 else "…\n" + body[-4000:]
            print("  ---- %s (%d bytes) ----\n%s" % (k, len(body), tail), flush=True)
    return 0


MODES = {
    "dry": lambda: mode_dry(),
    "diag": lambda: mode_diag(),
    "manifest": lambda: mode_manifest(),
    "stage_prep": lambda: mode_stage_prep(),
    "cofold_dry": lambda: mode_cofold_dry(),
    "cofold": lambda: mode_cofold(),
    "cofold_collect": lambda: mode_cofold_collect(),
    "stage_test": lambda: mode_stage_test(),
    "smoke": lambda: mode_launch(mode="smoke", pilot=True, only=_only()),
    "leg": lambda: mode_launch(mode="run", pilot=True, only=_only()),
    "launch": lambda: mode_launch(mode="run", pilot=False, only=_only()),
    "status": lambda: mode_status(),
    "watch": lambda: mode_watch(),
    "cofold_watch": lambda: mode_cofold_watch(),
    "collect": lambda: mode_collect(),
    "gate_tick": lambda: mode_gate_tick(),
    "reap": lambda: mode_reap(),
    "stop": lambda: mode_reap(stop_all=True),
}


def _only():
    raw = (os.environ.get("UNITS") or "").strip()
    return [u.strip() for u in raw.split(",") if u.strip()] or None


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Endpoint-MD sensitivity control — Vast lane.")
    ap.add_argument("--mode", default=os.environ.get("MODE", "dry"), choices=sorted(MODES))
    args = ap.parse_args(argv)
    return MODES[args.mode]()


if __name__ == "__main__":
    sys.exit(main())
