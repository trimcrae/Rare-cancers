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

MARKET_READOUT = os.path.join(HERE, "selcal-market-hold.json")
GATE_RECORD = os.path.join(HERE, "selcal-gate-record.json")
PRICE_LEDGER = os.path.join(HERE, "selcal-price-ledger.json")
COLLECT_READOUT = os.path.join(HERE, "selcal-collect.json")
VERDICT_READOUT = os.path.join(HERE, "selcal-verdict.json")
COFOLD_CENSUS = os.path.join(HERE, "selcal-cofold-census.json")
STAGE_TEST_READOUT = os.path.join(HERE, "selcal-stage-test.json")
HANDLES = os.path.join(HERE, "selcal-handles.json")

#: The co-fold host's image and the pinned Boltz. Both imported from the lane that already proved them on
#: Vast, so a Boltz bump moves the two together instead of leaving this one on a version nobody re-validated.
from nrv04_vast_launch import BOLTZ_SPEC, COFOLD_IMAGE  # noqa: E402,E401


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

_COFOLD_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -q >/dev/null 2>&1 || true
apt-get install -y -q --no-install-recommends git curl ca-certificates >/dev/null 2>&1 || true
pip install --quiet awscli $BOLTZ_SPEC cuequivariance-torch cuequivariance-ops-torch-cu12 || \
  { echo "[cofold] pip install FAILED"; exit 3; }
AWS=$(command -v aws || echo /opt/conda/bin/aws)
_HOST="instance=${CONTAINER_ID:-unknown} attempt=$(date -u +%Y%m%dT%H%M%SZ)"
mark() { echo "$1 $(date -u +%FT%TZ) $_HOST" | $AWS s3 cp - "$RESULT_S3/phase.txt" || echo "[mark] WARN could not write phase '$1'"; }
echo "preflight $(date -u +%FT%TZ) $_HOST" | $AWS s3 cp - "$RESULT_S3/phase.txt" || {
  echo "[preflight] FATAL cannot write to $RESULT_S3 — refusing to run an unmonitorable job"; exit 4; }
exec > >(tee -a /tmp/run.log) 2>&1
( while true; do $AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true; sleep 45; done ) &
LOGSYNC_PID=$!
mark deps-ready
nvidia-smi || true
free -g || true
rm -rf /tmp/repo
git clone -q {repo} /tmp/repo
git -C /tmp/repo checkout -q "$GIT_BRANCH" || true
mark cloned
export OUTPUT_DIR=/tmp/selcal_cofold_out SELCAL_INPUTS_DIR=/tmp/selcal_cofold_out/inputs
mkdir -p "$SELCAL_INPUTS_DIR"
$AWS s3 cp "$COFOLD_INPUTS_S3" "$SELCAL_INPUTS_DIR/" --recursive --only-show-errors
# CONTINUOUS UPLOAD, per the standing rule: sync every 60 s so a preemption after prediction N leaves
# predictions 1..N durable rather than losing the batch.
( while true; do $AWS s3 sync "$OUTPUT_DIR" "$RESULT_S3/" --exclude 'inputs/*' --only-show-errors || true; sleep 60; done ) &
SYNC_PID=$!
mark predicting
cd /tmp/repo/research/modalities
set +e
python selcal_cofold_run.py 2>&1 | tail -400
RC=$?
set -e
kill $SYNC_PID 2>/dev/null || true
kill $LOGSYNC_PID 2>/dev/null || true
$AWS s3 sync "$OUTPUT_DIR" "$RESULT_S3/" --exclude 'inputs/*' --only-show-errors || true
$AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors || true
mark "done rc=$RC"
exit $RC
"""


# =============================================================================================================
# job specs — PURE, so they are unit-tested with no creds
# =============================================================================================================
def cofold_inputs_s3(bucket=None, prefix=None):
    return "s3://%s/%s/inputs/" % (bucket or BUCKET, (prefix or SP.COFOLD_PREFIX).strip("/"))


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


def build_cofold_jobspec(branch, bucket, cofold_prefix=None, exclude=()):
    """PURE: the JobSpec for the ONE co-fold host that produces every structural input."""
    import dataclasses
    prefix = (cofold_prefix or SP.COFOLD_PREFIX).strip("/")
    res = ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=64, disk_gb=80, interruptible=True,
                       max_usd_per_ns=buy_ceiling_usd_per_ns())
    if exclude:
        res = dataclasses.replace(res, exclude_machine_ids=tuple(str(m) for m in exclude))
    return JobSpec(
        name="selcal-cofold-%s" % prefix,
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
             "SELCAL_SEEDS": ",".join(str(s) for s in SP.COFOLD_MODEL_SEEDS)},
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


def _ledger_record(inst, why):
    """Append one rental to the committed ledger. Called immediately BEFORE the destroy call."""
    led = _ledger_load()
    iid = str(inst.get("id"))
    dph = float(inst.get("dph_total") or 0.0)
    dur_s = float(inst.get("duration") or 0.0)
    gpu = inst.get("gpu_name")
    row = {"instance": iid, "label": inst.get("label"), "machine_id": inst.get("machine_id"),
           "gpu_name": gpu, "dph_total": round(dph, 5), "duration_s": round(dur_s, 1),
           "billed_usd": round(dph * dur_s / 3600.0, 4), "is_bid": inst.get("is_bid"),
           "destroyed_utc": _utcnow(), "why": why}
    try:
        import inflight_usd_per_ns as IU
        import vast_cost_model as vcm
        row["usd_per_ns_cell"] = IU.row(gpu, dph, vcm.PLAN_USD_PER_REF_GPU_H if hasattr(vcm, "PLAN_USD_PER_REF_GPU_H")
                                        else _plan_rate(), stance=IU.PAYING,
                                        rate_basis=IU.RATE_FROM_INSTANCE,
                                        tier=IU.tier_of(inst.get("is_bid")))["cell"]
    except Exception as e:  # noqa: BLE001 — a ledger row must land even if the $/ns cell cannot be rendered
        row["usd_per_ns_cell"] = "unavailable (%s)" % type(e).__name__
    led["rentals"] = [r for r in led.get("rentals", []) if r.get("instance") != iid] + [row]
    led["total_billed_usd"] = round(sum(r.get("billed_usd") or 0.0 for r in led["rentals"]), 4)
    led["n_rentals"] = len(led["rentals"])
    _write(PRICE_LEDGER, led)
    print("[selcal-ledger] %s (%s) billed $%.4f over %.1f min at $%.4f/hr — recorded BEFORE the delete"
          % (iid, inst.get("label"), row["billed_usd"], dur_s / 60.0, dph), flush=True)
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
    spec = build_cofold_jobspec(branch, bucket, prefix)
    # UNCAPPED copy for the gate — a gate must SEE the expensive offers to report how far above the line the
    # board sits. The cap stays on the spec handed to `submit`, where it binds the offer actually bought.
    hold, _doc = market_gate(1, bucket=bucket,
                             res=dataclasses.replace(spec.resources, max_usd_per_ns=None),
                             what="co-fold")
    if hold:
        _record_gate("held-on-price", ["selcal-cofold"], extra={"why": "market gate held the co-fold rental"})
        return 0
    be = get_backend("vast")
    try:
        h = be.submit(spec)
    except Exception as e:  # noqa: BLE001
        _record_gate("refused", ["selcal-cofold"], extra={"why": "%s: %s" % (type(e).__name__, e)})
        print("[selcal-cofold] ⛔ NOT RENTED — %s: %s. If the board simply had nothing at or under "
              "$%.6f/ns, this is the buy line doing its job: $0 spent."
              % (type(e).__name__, e, spec.resources.max_usd_per_ns), flush=True)
        return 1
    print("[selcal-cofold] %s -> instance %s dph≈$%s/hr -> %s"
          % (spec.name, h.job_id, h.extra.get("dph"), spec.env["RESULT_S3"]), flush=True)
    _write(HANDLES, [{"unit": spec.name, "instance": h.job_id, "kind": "cofold", "utc": _utcnow()}])
    _record_gate("rented", [spec.name], extra={"instance": h.job_id})
    return 0


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
        print("[selcal-cofold-progress] instance %s status=%s gpu_util=%s dph=%s uptime=%.1f min"
              % (i.get("id"), i.get("actual_status"), i.get("gpu_util"), i.get("dph_total"),
                 float(i.get("duration") or 0) / 60.0), flush=True)
    print("[selcal-cofold-progress] run.log tail:\n  " + "\n  ".join(tail), flush=True)
    cen = _cofold_census(s3, bucket, prefix)
    cen["phase"] = ph
    cen["log_tail"] = tail
    cen["instances"] = [{"id": i.get("id"), "status": i.get("actual_status"), "gpu_util": i.get("gpu_util"),
                         "dph_total": i.get("dph_total"), "uptime_min": round(float(i.get("duration") or 0)/60, 1)}
                        for i in mine]
    cen.update({"_what": "Which co-fold models exist for the sensitivity control, measured from S3.",
                "utc": _utcnow(), "bucket": bucket})
    _write(COFOLD_CENSUS, cen)
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
def _live_labels(key=None):
    try:
        live = _vast_request("GET", "/instances/", key or os.environ.get("VAST_API_KEY"),
                             params={"owner": "me"}).get("instances", [])
    except Exception as e:  # noqa: BLE001
        print("[selcal] WARN could not list live instances (%s); not skipping any" % e, flush=True)
        return {}, []
    alive = ("running", "loading", "created", "scheduling", "starting")
    return ({i.get("label"): i for i in live
             if i.get("label") and (i.get("actual_status") or "") in alive},
            [i for i in live if str(i.get("label") or "").startswith(SP.LABEL_PREFIX)])


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
                                 exclude=tuple(sorted(wave_refused)), cofold_prefix=prefix)
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


def mode_reap(bucket=None, stop_all=False):
    """Destroy this lane's finished / terminal hosts — recording the bill BEFORE the DELETE.

    ⛔ THE HOST CANNOT STOP ITS OWN BILLING; only the control plane can (CLAUDE.md §6, measured). The EXIT
    trap and `autoteardown.py` stop the JOB, not the METER, and a crash-looping container never returns at
    all — so the reap is this function's job, from CI, where the key lives."""
    bucket = bucket or BUCKET
    key = os.environ.get("VAST_API_KEY")
    _live, mine = _live_labels(key)
    import boto3
    s3 = boto3.client("s3")
    done, _records = _done_units(s3, bucket)
    stopped, kept = [], []
    for inst in mine:
        label = str(inst.get("label") or "")
        status = (inst.get("actual_status") or "")
        landed = label in done or label.startswith("selcal-cofold")
        terminal = status in ("exited", "offline", "error")
        why = ("operator stop_all" if stop_all else
               "result landed in S3" if landed and label in done else
               "terminal status %s" % status if terminal else "")
        if not why:
            kept.append({"label": label, "status": status, "gpu_util": inst.get("gpu_util")})
            continue
        # ⛔ LEDGER FIRST. The DELETE is the last moment this record exists; a rental that bills and leaves no
        # trace has already happened on this account (instance 46459452, overnight).
        _ledger_record(inst, why)
        try:
            _vast_request("DELETE", "/instances/%s/" % inst.get("id"), key, body={})
            stopped.append(inst.get("id"))
            print("[selcal-reap] destroyed %s (%s) — %s" % (inst.get("id"), label, why), flush=True)
        except Exception as e:  # noqa: BLE001
            print("[selcal-reap] WARN could not destroy %s: %s" % (inst.get("id"), e), flush=True)
    print("[selcal-reap] %d destroyed, %d kept running: %s" % (len(stopped), len(kept), kept), flush=True)
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
            print("[selcal-watch] panel complete — reaping and exiting.", flush=True)
            mode_reap(bucket)
            return 0
        mode_reap(bucket)
        time.sleep(float(os.environ.get("SELCAL_WATCH_INTERVAL_S", "180")))
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
        v["tier_suppressed"] = v.pop("tier", None)
        v["tier"] = None
        v["suppression"] = ("The panel is incomplete (%d of %d units). The criterion forbids an interim "
                            "verdict: a tier read off a partial panel, on a run that can still be extended, "
                            "is the peeking defect. The evidence below is reported; the LABEL is withheld "
                            "until the panel is complete or an arm is definitively short."
                            % (len(done), len(expected)))
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


MODES = {
    "dry": lambda: mode_dry(),
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
