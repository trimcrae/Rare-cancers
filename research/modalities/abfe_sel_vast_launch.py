#!/usr/bin/env python3
"""CREBBP vs BRD4(1) / SGC-CBP30 selectivity ABFE — the **Vast.ai** launcher for the known-answer test.

WHAT THIS RUNS AND WHY IT IS THE HIGHEST-LEVERAGE THING IN THE PROGRAM
---------------------------------------------------------------------
`research/manuscripts/nr4a3-program-map.md` carries this as the single highest-leverage open item: the paper's
entire *binder* selectivity claim rests on one instrument — the independent-window ABFE engine in
`nr4a3_abfe.py` — and that instrument has never been shown to recover a KNOWN selectivity. Until it does,
every computed selectivity margin in the program is unfalsifiable.

The test is one ligand across two related proteins, with a real published answer:

    SGC-CBP30 : CREBBP Kd 21 nM (ITC) vs BRD4(1) ~850 nM  ->  ΔΔG_exp ≈ **-2.19 kcal/mol**

Both receptors crystallise HOLO with the SAME ligand (4NR7, 5BT4), so each pose is lifted from a real complex.
The full specification, citations and pass criterion live in `selectivity-benchmark.json` — this module owns
only HOW it is bought and run, never WHAT it is (CLAUDE.md rule 1).

WHY VAST, EXPLICITLY (trimcrae, 2026-08-02: **"NO SAGEMAKER. VAST IS THE FLAGSHIP."**)
--------------------------------------------------------------------------------------
`abfe_selectivity_cost.py` §1 argued this lane had to price on AWS because "there is NO Vast ABFE launcher"
and the engine's only submitter was `nr4a3_abfe_sagemaker.py`. **That was an argument from the absence of a
file, and CLAUDE.md §5 forbids it outright: engineering effort is free, so "we'd have to write it" is never a
cost.** This file is the missing launcher; the AWS-only framing it rested on is retired, and
`abfe_selectivity_cost.price_vast()` is now the lane's live figure.

⚠ THE DISTINCTION THAT KEEPS THIS SIMPLE: the objection is to SageMaker as the COMPUTE PROVIDER, not to S3 as
an OBJECT STORE. `object_store.py` is provider-agnostic on purpose, the four benchmark inputs are already
staged and verified in `s3://<bucket>/selectivity-benchmark/`, and re-staging them would be work that buys
nothing. So: **inputs pulled from S3, GPU work on Vast.**

THE STAGED LADDER (CLAUDE.md §6 — smoke -> one real leg -> fleet)
------------------------------------------------------------------
  smoke   -> 1 unit. The SOLVENT leg at a token iteration count. Cheapest possible proof of the whole chain:
             image pull, CUDA platform, the openff/AM1-BCC parameterisation of SGC-CBP30 (the riskiest step
             in the leg, and the one a CPU smoke cannot exercise), per-window checkpointing, S3 sync, resume,
             MBAR. Its ΔG is meaningless and its unit id carries a `-smoke` suffix that the reduce refuses to
             score.
  solvent -> 1 unit. The REAL shared solvent leg at full sampling. The cheap real leg required before a
             fleet, and it is genuinely cheap: ligand-in-water is ~a tenth of a complex leg.
  full    -> the fleet: `n_replicates` x {complex-crebbp, complex-brd4bd1, solvent}. Fanned out at once,
             because CLAUDE.md §6's litmus test answers NO — there is no result one complex leg could return
             that would make us not run the other. (The abort information already lives in `smoke`, which is
             a plumbing gate, and in the solvent leg, which is a real-leg gate.)

WHAT IS WIRED IN BECAUSE IT IS NOT OPTIONAL
-------------------------------------------
  * **`relaunch_market_gate`** on EVERY rental — cold unit, fleet unit and resume alike. A relaunch is a new
    purchase; the buy line is the ABSOLUTE `$0.006539/ns` (`inflight_usd_per_ns.APPROVED_USD_PER_NS`), and a
    hold quotes `board_depth` so a filter bug cannot masquerade as an expensive market.
  * **`ResourceSpec.max_usd_per_ns`** carried INTO `submit`, so the offer actually bought clears the same
    line the gate cleared — not a second board read beside it.
  * **`vast_idle_guard` from CI** — the host cannot stop its own billing. The EXIT trap and `autoteardown.py`
    stop the JOB, not the METER.
  * **No durable machine blacklist** (`vast_machine_blacklist.DURABLE_EXCLUSIONS_ENABLED = False`). A
    capacity refusal is bounded to the wave that learned it.
  * **Continuous checkpoint upload** (`aws s3 sync` every `SYNC_S`), so a preemption costs at most one sync
    interval and a resume re-enters the exact window it left.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import relaunch_market_gate as rmg  # noqa: E402
import vast_idle_guard as vig  # noqa: E402
import vast_stopped_resume_measure as _srm  # noqa: E402
from gpu_backend import (  # noqa: E402
    JobSpec, NoQualifyingOffer, ResourceSpec, _vast_request, get_backend, measured_min_cuda,
)
from inflight_usd_per_ns import APPROVED_USD_PER_NS  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
# NOTE THE `or`, NOT `.get(key, default)` — a blank CI input arrives as an EMPTY STRING, which IS set, so a
# `.get` default never fires. That hole once rented a real 4090 whose result prefix resolved to `s3:///…`.
VAST_IMAGE = os.environ.get("VAST_IMAGE") or "docker.io/triskit23/ternary-fep:latest"
RESULT_PREFIX = os.environ.get("ABFE_SEL_RESULT_PREFIX") or "abfe-sel-cbp30-vast"
INPUT_PREFIX = os.environ.get("ABFE_SEL_INPUT_PREFIX") or "selectivity-benchmark"
DEFAULT_BUCKET = os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
LABEL_PREFIX = "abfe-sel"
LANE = "abfe-sel-cbp30"

RECEPTORS = ("crebbp", "brd4bd1")
LIGAND_NAME = "sgc_cbp30"

# Runtime backstop: an instance up longer than this is destroyed even with no result, so a hung leg cannot
# bill indefinitely. A BACKSTOP, not the normal path — the normal path is "leg result in S3 -> destroy".
MAX_INSTANCE_HOURS = float(os.environ.get("ABFE_SEL_MAX_INSTANCE_HOURS") or "14")
# How long a box may sit `stopped` before the nudge is given up on. DERIVED from the measured resume
# distribution, not typed — one home in `vast_stopped_resume_measure.hold_minutes()`.
MAX_STOPPED_MIN = float(os.environ.get("ABFE_SEL_MAX_STOPPED_MIN") or _srm.hold_minutes(default=45))
# Same status_msg for this long while `cur_state=running` means the image pull has died rather than queued.
MAX_FROZEN_MIN = float(os.environ.get("ABFE_SEL_MAX_FROZEN_MIN") or "15")
SYNC_S = int(os.environ.get("ABFE_SEL_SYNC_S") or "180")

# A solvated bromodomain complex is small by this repo's standards — CREBBP is 116 residues / 971 heavy atoms
# and BRD4(1) 127 / 1062 (both measured off the staging job's own log), so with 1.2 nm padding the systems are
# tens of thousands of particles, not the ternary lane's 146k. Nothing here is VRAM- or host-RAM-bound, so a
# modest spec keeps the cheap offers in play instead of filtering the board down to expensive hosts —
# CLAUDE.md §6: when placement fails, suspect OUR FILTERS before the market.
#
# `min_cuda` is MEASURED for THIS image (`ternary-fep` -> 12.6, `image-cuda-requirements.json`), never
# inherited: `measured_min_cuda` returns the conservative fallback for an unprobed image, and inheriting
# another stack's floor is the same error as inheriting a Dockerfile's claim.
def resource_spec(max_usd_per_ns=None):
    """The lane's OWN ResourceSpec. A function, not a module constant, because `submit` mutates
    `exclude_machine_ids` per wave and a shared mutable default would leak one wave's refusals into the next —
    which is precisely the durable-blacklist behaviour CLAUDE.md §6 retired."""
    return ResourceSpec(
        gpu=os.environ.get("ABFE_SEL_GPU") or "rtx4090",
        min_vram_gb=int(os.environ.get("ABFE_SEL_VRAM") or "16"),
        vcpus=4, ram_gb=16, disk_gb=40, interruptible=True,
        min_cuda=measured_min_cuda(VAST_IMAGE),
        max_usd_per_ns=max_usd_per_ns)


# The onstart pipeline. `VastBackend._vast_onstart` exports the forwarded S3 credential and arms the crash-loop
# brake + the key-free EXIT trap before this runs.
#
# ⛔ NOTHING IS INSTALLED HERE, AND THAT IS THE POINT (CLAUDE.md §6 — never build an environment on a machine
# we are paying for). `triskit23/ternary-fep` already bakes openmm + openmmtools + pymbar (via openmmtools) +
# openmmforcefields + openff-toolkit + ambertools + pdbfixer + rdkit + awscli/boto3, which is the complete
# dependency set of `nr4a3_abfe.prepare_leg` and `run_window`. The image supplies the ENV; the repo tarball
# supplies the CODE, so a fix pushed after the bake is live without a re-bake.
_PIPELINE = r"""
set -o pipefail
export HOME=/root
export PATH=/opt/mamba/envs/rbfe/bin:$PATH
exec > >(tee /tmp/run.log) 2>&1
echo "[abfe-sel] $(date -u +%FT%TZ) start unit=$UNIT_ID leg=$ABFE_LEG receptor=$ABFE_RECEPTOR seed=$ABFE_SEED"
mark() { echo "$1 $(date -u +%FT%TZ)" | aws s3 cp - "$RESULT_S3/phase.txt" 2>/dev/null || true; \
         aws s3 cp /tmp/run.log "$RESULT_S3/run.log" 2>/dev/null || true; }
# ★ ARCHIVE THE PREVIOUS ATTEMPT'S LOG BEFORE TRUNCATING IT. The count of `attempts/` keys IS the durable
# count of container starts, with the timestamp IN THE KEY — the channel `vast_idle_guard` uses to catch a
# crash-loop whose S3 still works. Without it a box that restarts every 20 s is invisible to the reaper.
aws s3 cp "$RESULT_S3/run.log" "$RESULT_S3/attempts/run-$(date -u +%Y%m%dT%H%M%SZ).log" 2>/dev/null || true
mark start
# IDEMPOTENCY: Vast re-runs onstart when a container restarts. A finished leg must not re-run.
if aws s3 cp "$RESULT_S3/leg_$UNIT_ID.json" - 2>/dev/null | grep -q '"status": "done"'; then
  echo "[abfe-sel] leg already done in S3 -> nothing to do (awaiting CI reap)"; exit 0
fi
mkdir -p /tmp/abfe_in /tmp/abfe_out
# --- the four STAGED inputs (already in S3; CLAUDE.md: do not re-stage what is verified present) ---
aws s3 sync "$INPUT_S3/" /tmp/abfe_in/ || { echo "[abfe-sel] input sync FAILED"; exit 3; }
ls -la /tmp/abfe_in
# --- RESUME: pull back EVERYTHING the sync loop wrote, not just the record. `_prepare_or_load_reference`
# reloads reference_system.xml so a resume does NOT rebuild the solvated system (a rebuild changes the
# particle count and invalidates every per-window checkpoint — the T4L incident), and run_window resumes at
# _last_logged_iter+1 from window_XX.state.xml. Pulling only the record would silently re-run finished windows.
aws s3 sync "$RESULT_S3/" /tmp/abfe_out/ --exclude 'attempts/*' --exclude 'run.log' --exclude 'phase.txt' \
    2>/dev/null || true
echo "[abfe-sel] restored $(ls /tmp/abfe_out/$UNIT_ID/window_*.jsonl 2>/dev/null | wc -l) window log(s)"
# --- repo code (public codeload tarball) ---
cd /root
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz || { echo "repo pull failed"; exit 3; }
cd Rare-cancers-*/research/modalities || exit 3
export ABFE_SEL_CODE_SHA256="$(sha256sum abfe_sel_leg.py | cut -c1-12)"
echo "[abfe-sel] driver abfe_sel_leg.py sha256[:12]=$ABFE_SEL_CODE_SHA256 branch=$GIT_BRANCH"
mark cloned
# --- CONTINUOUS checkpoint upload. `sync` (not `cp --recursive`) so only changed objects move: the current
# window's State.xml and its jsonl, not the whole leg every cycle.
( while true; do sleep $SYNC_S; \
    aws s3 sync /tmp/abfe_out/ "$RESULT_S3/" >/dev/null 2>&1 || true; \
    aws s3 cp /tmp/run.log "$RESULT_S3/run.log" >/dev/null 2>&1 || true; \
  done ) &
SYNC_PID=$!
mark md-running
INPUT_DIR=/tmp/abfe_in OUTPUT_DIR=/tmp/abfe_out python autoteardown.py \
    python abfe_sel_leg.py --unit-id "$UNIT_ID" --leg "$ABFE_LEG" --receptor "$ABFE_RECEPTOR" \
        --ligand-name "$ABFE_LIGAND" --seed "$ABFE_SEED" --n-iter "$ABFE_N_ITER" \
        --steps-per-iter "$ABFE_STEPS_PER_ITER"
RC=$?
kill $SYNC_PID 2>/dev/null || true
mark md-done
aws s3 sync /tmp/abfe_out/ "$RESULT_S3/" || echo "result upload failed"
mark done
echo "[abfe-sel] $(date -u +%FT%TZ) EXIT rc=$RC"
exit $RC
"""

# Sampling sizes per mode. The smoke's numbers are deliberately too small to mean anything scientifically — its
# ONLY job is to prove the chain end to end before a real leg is paid for.
MODES = {
    "smoke":   {"n_iter": 10,   "max_runtime_s": 5400,  "suffix": "-smoke"},
    "solvent": {"n_iter": None, "max_runtime_s": 21600, "suffix": ""},
    "full":    {"n_iter": None, "max_runtime_s": 50400, "suffix": ""},
}


def _plan():
    """The benchmark's OWN dispatch inputs — `selectivity-benchmark.json` owns them (rule 1)."""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "selectivity-benchmark.json")) as f:
        return json.load(f)


def default_n_iter():
    """Iterations per λ-window, READ from the benchmark spec rather than typed here."""
    return int(_plan()["abfe_plan"]["dispatch_inputs"]["n_iter"])


def unit_id(leg, receptor, seed, mode="full"):
    """The id under which this unit checkpoints, labels its host and is reduced. PURE.

    ★ THE SEED IS IN THE PREFIX, AND THAT IS THE WHOLE REPLICATE FIX. `selectivity-benchmark.json` records
    the defect this avoids: the SageMaker prefix was `s3://<bucket>/<TAG>/ckpt/<leg>/` and carried NO seed,
    while `run_window` resumes at `_last_logged_iter + 1` — so a second seed under the same tag found every
    window already at n_iter, ran zero iterations, exited SUCCESSFULLY and re-emitted seed 0's samples under
    seed 1's label. A fabricated replicate, and the error would have been invisible in the artifact. Putting
    the seed in the unit id makes a replicate structurally incapable of colliding with another.
    """
    base = f"r{int(seed)}-{leg}" + (f"-{receptor}" if leg == "complex" else "")
    return base + MODES.get(mode, {}).get("suffix", "")


def units_for(mode, n_replicates=3, seeds=None):
    """The units this mode launches. PURE. Each is a dict the jobspec builder consumes."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {sorted(MODES)}")
    if mode == "smoke":
        return [{"leg": "solvent", "receptor": RECEPTORS[0], "seed": 0}]
    if mode == "solvent":
        return [{"leg": "solvent", "receptor": RECEPTORS[0], "seed": 0}]
    ss = list(seeds) if seeds is not None else list(range(int(n_replicates)))
    out = []
    for s in ss:
        for r in RECEPTORS:
            out.append({"leg": "complex", "receptor": r, "seed": s})
        out.append({"leg": "solvent", "receptor": RECEPTORS[0], "seed": s})
    return out


def unit_label(u, mode):
    """Vast instance label. Derived from the SAME id the jobspec uses — they diverged once on the 5a-KS lane
    and the reap could never match, so a finished leg's GPU kept billing."""
    return f"{LABEL_PREFIX}-{unit_id(u['leg'], u['receptor'], u['seed'], mode)}".replace("_", "-").lower()[:60]


def label_matches_unit(label, uid):
    """Does this Vast label belong to this unit? PURE, and matched id->label because the encoding is lossy."""
    if not label or not uid:
        return False
    return str(label).strip().lower() == f"{LABEL_PREFIX}-{uid}".replace("_", "-").lower()[:60]


def build_jobspec(u, mode="full", git_branch=None, bucket=None, result_prefix=None, n_iter=None,
                  max_usd_per_ns=None):
    """PURE construction of one unit's JobSpec (no network)."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}")
    sizing = MODES[mode]
    branch = git_branch or os.environ.get("GIT_BRANCH") or "main"
    b = bucket or DEFAULT_BUCKET
    prefix = (result_prefix or RESULT_PREFIX).rstrip("/")
    uid = unit_id(u["leg"], u["receptor"], u["seed"], mode)
    if not b or not prefix:
        raise ValueError(
            f"refusing to launch with an incomplete result location (bucket={b!r}, prefix={prefix!r}). A "
            f"blank CI input arrives as an EMPTY STRING, not as unset, so os.environ.get's default does not "
            f"fire — that exact hole rented a 4090 that would have uploaded to 's3:///…'.")
    iters = int(n_iter or sizing["n_iter"] or default_n_iter())
    result_s3 = f"s3://{b}/{prefix}/{uid}"
    env = {
        "MODE": mode,
        "UNIT_ID": uid,
        "ABFE_LEG": u["leg"],
        "ABFE_RECEPTOR": u["receptor"],
        "ABFE_SEED": str(int(u["seed"])),
        "ABFE_LIGAND": LIGAND_NAME,
        "ABFE_N_ITER": str(iters),
        "ABFE_STEPS_PER_ITER": os.environ.get("ABFE_SEL_STEPS_PER_ITER") or "500",
        "GIT_BRANCH": branch,
        "RESULT_S3": result_s3,
        "INPUT_S3": f"s3://{b}/{INPUT_PREFIX.rstrip('/')}",
        "SYNC_S": str(SYNC_S),
        # CUDA is REQUIRED — `nr4a3_abfe._select_platform` refuses a silent OpenCL fallback, which is right:
        # OpenCL is 1.3-2x slower, so accepting it would pay 4090 prices for 3090-class throughput and the
        # $/ns the gate cleared would be wrong by that factor with nothing in the record to say so.
        "OPENMM_REQUIRE_CUDA": "1",
    }
    return JobSpec(
        name=unit_label(u, mode),
        command=["bash", "-lc", _PIPELINE.replace("{repo}", REPO)],
        image=VAST_IMAGE,
        checkpoint_uri=result_s3,
        resume=True,
        resources=resource_spec(max_usd_per_ns=max_usd_per_ns),
        max_runtime_s=int(os.environ.get("ABFE_SEL_MAX_RUNTIME_S") or sizing["max_runtime_s"]),
        env=env,
    )


# =============================================================================================================
# what is already done / already running — checked BEFORE anything is rented
# =============================================================================================================
def _s3():
    import boto3
    return boto3.client("s3")


def leg_records(bucket=None, prefix=None):
    """{unit_id: record} for every `leg_*.json` under the lane prefix. {} if S3 is unreadable.

    ⚠ AN UNREADABLE LISTING IS NOT AN EMPTY ONE, and the difference spends money: degrading to "nothing is
    finished" launches every unit, including ones that completed hours ago. So the failure is LOUD."""
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    out = {}
    try:
        s3 = _s3()
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=b, Prefix=f"{p}/"):
            for obj in page.get("Contents", []):
                name = os.path.basename(obj["Key"])
                if not (name.startswith("leg_") and name.endswith(".json")):
                    continue
                try:
                    doc = json.loads(s3.get_object(Bucket=b, Key=obj["Key"])["Body"].read().decode())
                except Exception as e:  # noqa: BLE001
                    print(f"[abfe-sel] unreadable {obj['Key']}: {e}")
                    continue
                doc["_s3_last_modified"] = obj["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ")
                out[doc.get("unit_id") or name] = doc
    except Exception as e:  # noqa: BLE001
        print(f"[abfe-sel] WARNING: could not list leg records ({type(e).__name__}: {e}) — cannot tell which "
              f"units are finished. Launching would risk re-buying completed work, so this is reported, not "
              f"swallowed.")
        return {}
    return out


def live_labels(key=None):
    """Labels of this lane's live Vast instances. () if the API is unreadable."""
    api = key or os.environ.get("VAST_API_KEY")
    if not api:
        return ()
    try:
        return tuple((i.get("label") or "") for i in
                     _vast_request("GET", "/instances/", api).get("instances", [])
                     if (i.get("label") or "").startswith(LABEL_PREFIX))
    except Exception as e:  # noqa: BLE001 — never block a launch on a listing failure, but SAY so
        print(f"[abfe-sel] could not list live instances ({type(e).__name__}: {e}); cannot skip in-flight "
              f"units, duplicates are possible")
        return ()


# =============================================================================================================
# submit
# =============================================================================================================
def submit(mode="solvent", n_replicates=3, seeds=None, dry_run=False, n_iter=None):
    """Rent one instance per unit for this mode, skipping units already done or already running.

    ★ EVERY RENTAL IS GATED, INCLUDING A COLD ONE. CLAUDE.md §6: a relaunch is a NEW PURCHASE, and the test is
    "would waiting actually lose work?" — for a checkpointed unit it would not. So `relaunch_market_gate.gate`
    runs per unit, on the LANE'S OWN ResourceSpec, and a hold prints its `board_depth` so a filter problem
    cannot be reported as an expensive market.

    ★ AND THE CLEARED PRICE IS MADE BINDING. The gate's board read and `submit`'s board read are two different
    objects; without `max_usd_per_ns` travelling with the spec, the gate could clear one host and the launcher
    buy a worse one after a capacity refusal — by definition worse than what was approved.
    """
    units = units_for(mode, n_replicates=n_replicates, seeds=seeds)
    if not dry_run:
        recs = leg_records()
        finished = {uid for uid, d in recs.items() if d.get("status") == "done"}
        labels = live_labels()
        inflight = {unit_id(u["leg"], u["receptor"], u["seed"], mode) for u in units
                    if any(label_matches_unit(l, unit_id(u["leg"], u["receptor"], u["seed"], mode))
                           for l in labels)}
        keep, skipped = [], []
        for u in units:
            uid = unit_id(u["leg"], u["receptor"], u["seed"], mode)
            if uid in finished:
                skipped.append((uid, "already done in S3"))
            elif uid in inflight:
                skipped.append((uid, "a host is already labelled for it"))
            else:
                keep.append(u)
        for uid, why in skipped:
            print(f"[abfe-sel] skipping {uid} — {why}; no rental")
        units = keep
        if not units:
            print("[abfe-sel] every unit for this mode is already done or running — nothing to rent")
            return []
    print(f"[abfe-sel] mode={mode} units={len(units)} image={VAST_IMAGE} "
          f"buy_line=${APPROVED_USD_PER_NS:.6f}/ns")
    if dry_run:
        specs = [build_jobspec(u, mode=mode, n_iter=n_iter) for u in units]
        print(json.dumps([{"name": j.name, "env": j.env, "max_runtime_s": j.max_runtime_s} for j in specs],
                         indent=2))
        return []

    backend = get_backend("vast")
    s3 = None
    try:
        s3 = _s3()
    except Exception:  # noqa: BLE001 — the gate degrades to no escalation clock and says so
        pass
    handles, held = [], []
    # ONE UNIT PER MACHINE WITHIN A WAVE. Offers are per GPU slot, so selection happily picks the same cheapest
    # host for several units — and a host advertising slots it cannot schedule accepts every rental and then
    # refuses every start. This set DIES WITH THE WAVE (CLAUDE.md §6: nothing that excludes a machine may
    # outlive the call that learned it).
    used_machines = set()
    for u in units:
        uid = unit_id(u["leg"], u["receptor"], u["seed"], mode)
        hold, doc = rmg.gate(LANE, uid, resource_spec(), excluded=sorted(used_machines),
                             s3=s3, state_bucket=DEFAULT_BUCKET, state_prefix=RESULT_PREFIX.rstrip("/"))
        if hold:
            held.append({"unit": uid, "ratio_vs_basis": doc.get("ratio_vs_basis"),
                         "board_depth": doc.get("board_depth"), "reason": doc.get("reason"),
                         "hold_cause": doc.get("hold_cause")})
            continue
        j = build_jobspec(u, mode=mode, n_iter=n_iter, max_usd_per_ns=APPROVED_USD_PER_NS)
        j.resources.exclude_machine_ids = tuple(used_machines)
        try:
            h = backend.submit(j)
            mid = h.extra.get("machine_id")
            if mid is not None:
                used_machines.add(str(mid))
            print(f"[abfe-sel] {j.name}: instance={h.job_id} offer={h.extra.get('offer')} machine={mid} "
                  f"dph≈{h.extra.get('dph')} (a QUOTE — the billed rate is read by vast_rate_forensics)")
            handles.append(h)
        except NoQualifyingOffer as e:
            # The MARKET had nothing this spec could buy at a rate we will pay. Not a fault: the work is
            # checkpointed, the ladder has no deadline, and the next tick re-checks.
            print(f"[abfe-sel] {j.name}: ⛔ NO BUYABLE OFFER — {e}")
            held.append({"unit": uid, "reason": str(e), "hold_cause": "no_qualifying_offer"})
        except Exception as e:  # noqa: BLE001 — one unrentable unit must not abort the rest
            print(f"[abfe-sel] {j.name}: SUBMIT FAILED {type(e).__name__}: {e}")
    print(f"[abfe-sel] {len(handles)}/{len(units)} unit(s) submitted; {len(held)} held. "
          f"results -> s3://{DEFAULT_BUCKET}/{RESULT_PREFIX}/")
    for h in held:
        # ⛔, never ⚠ — this is money we DECLINED, not money going out (CLAUDE.md §1).
        print(f"  ⛔ REFUSED {h['unit']} — $0 spent. {h.get('reason', '')[:220]}")
        if h.get("board_depth"):
            print(f"     board_depth: {json.dumps(h['board_depth'])}")
    return handles


# =============================================================================================================
# collect — status board + anti-idle reap
# =============================================================================================================
def _record_is_newer_than_instance(doc, instance):
    """Was this record written by the CURRENTLY running instance? PURE. False on any missing/unparseable
    timestamp — the conservative direction, because reaping wrongly kills a leg about to do real work."""
    import calendar
    stamp = doc.get("updated_utc") or doc.get("started_utc")
    started = instance.get("start_date")
    if not stamp or started is None:
        return False
    try:
        return calendar.timegm(time.strptime(str(stamp), "%Y-%m-%dT%H:%M:%SZ")) > float(started)
    except (ValueError, TypeError):
        return False


def stall_minutes(prev, iid, status_msg, now):
    """How long this instance has shown this EXACT status_msg. PURE. `collect` is stateless between CI runs,
    and that is the whole difference between a docker layer queued behind two others and a pull that died."""
    key = str(iid)
    old = (prev or {}).get(key)
    if not isinstance(old, (list, tuple)) or len(old) != 2:
        old = None
    if old and old[0] == status_msg:
        return (now - float(old[1])) / 60.0, [status_msg, float(old[1])]
    return 0.0, [status_msg, now]


def collect(bucket=None, prefix=None, autostop=True):
    """PROGRESS board + reap. Returns (n_up, n_done).

    ⚠ A PROGRESS CHECK, NOT A LIVENESS PING (CLAUDE.md §4). Every row prints the unit's iteration count AND
    whether it moved since the previous poll, because "the instance is up" is exactly what the three silent
    ternary failures all looked like.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    s3 = _s3()
    recs = leg_records(b, p)
    done = {k: v for k, v in recs.items() if v.get("status") == "done"}
    partial = {k: v for k, v in recs.items() if v.get("status") != "done"}

    prev_state = {}
    try:
        prev_state = json.loads(s3.get_object(Bucket=b, Key=f"{p}/_lane_state.json")["Body"].read())
    except Exception:  # noqa: BLE001 — first run, or pruned; a missing clock just resets it
        prev_state = {}
    new_state = {}

    key = os.environ.get("VAST_API_KEY")
    mine = []
    if key:
        try:
            mine = [i for i in _vast_request("GET", "/instances/", key).get("instances", [])
                    if (i.get("label") or "").startswith(LABEL_PREFIX)]
        except Exception as e:  # noqa: BLE001
            print(f"[abfe-sel] could not list instances: {type(e).__name__}: {e}")

    print(f"[abfe-sel] {len(done)} finished unit(s), {len(partial)} in progress, {len(mine)} host(s) up")
    for uid, d in sorted(done.items()):
        dg = d.get("decouple_dg_kcal")
        print(f"  DONE  {uid}: decoupling ΔG = "
              + (f"{dg:.3f} ± {d.get('decouple_mbar_se_kcal') or float('nan'):.3f} kcal/mol" if dg is not None
                 else "(MBAR deferred to the CI reduce)")
              + f"  [{d.get('iterations_done')} iters, {d.get('gpu_hours')} h, "
                f"{d.get('n_receptor_atoms')} rec + {d.get('n_ligand_atoms')} lig atoms]")
    for uid, d in sorted(partial.items()):
        prior = (prev_state.get(f"iters:{uid}") or [0])[0]
        now_it = int(d.get("iterations_done") or 0)
        new_state[f"iters:{uid}"] = [now_it, time.time()]
        arrow = "UP" if now_it > int(prior or 0) else "no-change"
        print(f"  ....  {uid}: {d.get('status')} phase={d.get('phase')} "
              f"{now_it}/{d.get('prod_iters_target')} iters ({arrow} since last poll, was {prior})"
              + (f" — {d.get('error')}" if d.get("status") == "failed" else ""))
        print(f"        record: updated_utc={d.get('updated_utc')} started_utc={d.get('started_utc')} "
              f"s3_mtime={d.get('_s3_last_modified')} driver={d.get('driver_sha256')}")
        if d.get("status") == "failed":
            superseded = any(label_matches_unit(i.get("label"), uid)
                             and not _record_is_newer_than_instance(d, i) for i in mine)
            if superseded:
                print("      (stale: predates the host currently on this unit — traceback suppressed)")
            else:
                for ln in str(d.get("traceback", "(none recorded)")).splitlines():
                    print(f"      T| {ln[:200]}")

    # phase markers + log tails — the science ADVANCING, not the box being up
    print("[abfe-sel] phase markers:")
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=b, Prefix=f"{p}/"):
        for obj in page.get("Contents", []):
            if not obj["Key"].endswith("/phase.txt"):
                continue
            uid = obj["Key"].split("/")[-2]
            try:
                phase = s3.get_object(Bucket=b, Key=obj["Key"])["Body"].read().decode().strip()
            except Exception as e:  # noqa: BLE001
                phase = f"(unreadable: {e})"
            age = (time.time() - obj["LastModified"].timestamp()) / 60
            print(f"    {uid}: {phase}  ({age:.0f} min ago)")
            try:
                tail = s3.get_object(Bucket=b, Key=f"{p}/{uid}/run.log")["Body"].read().decode(errors="replace")
                for ln in [x for x in tail.strip().splitlines() if x.strip()][-10:]:
                    print(f"      | {ln[:160]}")
            except Exception:  # noqa: BLE001
                print("      | (no run.log yet)")

    n_up = len(mine)
    blocked = set()
    if key:
        # DEDUPE first: two instances on one unit write the same keys, do the same work and bill twice.
        by_label = {}
        for i in mine:
            by_label.setdefault(i.get("label") or "", []).append(i)
        for label, group in by_label.items():
            if len(group) < 2:
                continue
            group.sort(key=lambda x: float(x.get("start_date") or 0))
            for d in group[1:]:
                print(f"  DUPLICATE {label}: destroying {d.get('id')} (keeping the oldest, {group[0].get('id')})")
                _destroy(d.get("id"), key)
            mine = [x for x in mine if x not in group[1:]]

        for i in mine:
            label, iid = i.get("label"), i.get("id")
            up_h = 0.0
            try:
                up_h = (time.time() - float(i.get("start_date") or time.time())) / 3600.0
            except (TypeError, ValueError):
                pass
            print(f"  vast {iid} ({label}) {i.get('actual_status')} up={up_h:.2f}h gpu={i.get('gpu_name')} "
                  f"dph={i.get('dph_total')} spent~${up_h * float(i.get('dph_total') or 0):.2f}")
            msg = str(i.get("status_msg") or "").strip()
            frozen_min, new_state[str(iid)] = stall_minutes(prev_state, iid, msg, time.time())
            if i.get("actual_status") != "running":
                print(f"      why: cur_state={i.get('cur_state')} intended={i.get('intended_status')} "
                      f"msg={msg[:180]!r} unchanged_for={frozen_min:.0f}min")

            uid = next((k for k in recs if label_matches_unit(label, k)), None)
            rec = recs.get(uid) or {}
            finished = uid in done
            crashed = (rec.get("status") == "failed" and _record_is_newer_than_instance(rec, i))
            advanced = int(rec.get("iterations_done") or 0) > int(
                (prev_state.get(f"iters:{uid}") or [0])[0] or 0)

            # ANTI-IDLE VERDICT. The host cannot stop its own billing — only the control plane can.
            # `gpu_util` can only ever SAVE a box here, never condemn one (vast_idle_guard's inviolable rule).
            idle_verdict, idle_why = vig.classify_idle(
                instance_running=(i.get("actual_status") == "running"),
                container_started=bool(rec),
                gpu_util=i.get("gpu_util"),
                progress_advanced=advanced,
                log_age_min=_log_age_min(s3, b, f"{p}/{uid}/run.log") if uid else None,
                start_ages_min=vig.start_ages_min(s3, b, f"{p}/{uid}/attempts/") if uid else None,
                instance_age_min=up_h * 60.0,
                unit_failed=crashed)
            print(f"      idle-guard: {idle_verdict} — {idle_why}")

            if not autostop:
                continue
            if finished or crashed or up_h > MAX_INSTANCE_HOURS:
                why = ("unit done" if finished else
                       "unit FAILED — nothing left to produce" if crashed else "runtime backstop")
                print(f"    -> destroying {iid} ({why})")
                _destroy(iid, key)
            elif vig.should_destroy(idle_verdict):
                print(f"    -> destroying {iid} (idle guard: {idle_verdict})")
                _destroy(iid, key)
            elif (i.get("actual_status") != "running" and i.get("cur_state") == "running"
                  and frozen_min > MAX_FROZEN_MIN):
                print(f"    -> destroying {iid} (status frozen {frozen_min:.0f} min at {msg[:60]!r}; the "
                      f"pull is dead, not queued)")
                _destroy(iid, key)
            elif i.get("cur_state") == "stopped":
                err = None
                try:
                    resp = _vast_request("PUT", f"/instances/{iid}/", key, body={"state": "running"})
                    err = (resp or {}).get("error")
                    print(f"    -> NUDGED {iid}: re-issued start; vast replied {str(resp)[:240]}")
                except Exception as e:  # noqa: BLE001
                    print(f"    nudge failed: {e}")
                if err == "resources_unavailable":
                    # CLAUDE.md §6: that machine's GPU is taken. Destroy and launch elsewhere — do not queue,
                    # do not raise the bid (a 26 % raise was tried and left it queued). The exclusion is
                    # bounded to this wave; nothing durable is written.
                    blocked.add(str(i.get("machine_id")))
                    print(f"    -> destroying {iid}: machine {i.get('machine_id')} has no free GPU and no bid "
                          f"fixes it; picking another host beats queueing")
                    _destroy(iid, key)
                elif up_h * 60 > MAX_STOPPED_MIN:
                    print(f"    -> destroying {iid} (stopped {up_h * 60:.0f} min, not a capacity wait)")
                    _destroy(iid, key)

    try:
        # WAVE-SCOPED, NEVER CUMULATIVE. The only thing that adds here is a capacity refusal, which is the
        # perishable class "this machine's GPU was busy on this tick" — not a property of the host.
        new_state["_blocked_machines_this_tick"] = sorted(blocked)
        s3.put_object(Bucket=b, Key=f"{p}/_lane_state.json",
                      Body=json.dumps(new_state, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[abfe-sel] could not persist lane state: {e}")
    return n_up, len(done)


def _log_age_min(s3, bucket, key):
    try:
        head = s3.head_object(Bucket=bucket, Key=key)
        return (time.time() - head["LastModified"].timestamp()) / 60.0
    except Exception:  # noqa: BLE001 — never written yet, or unreadable: None means "no reading", not "old"
        return None


def _destroy(iid, key):
    try:
        _vast_request("DELETE", f"/instances/{iid}/", key)
    except Exception as e:  # noqa: BLE001
        print(f"    destroy failed: {e}")


def stop_all():
    """Destroy every instance of this lane (anti-idle backstop)."""
    key = os.environ["VAST_API_KEY"]
    n = 0
    for i in _vast_request("GET", "/instances/", key).get("instances", []):
        if (i.get("label") or "").startswith(LABEL_PREFIX):
            print(f"destroying {i.get('id')} ({i.get('label')})")
            _destroy(i.get("id"), key)
            n += 1
    print(f"destroyed {n}")
    return n


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="CBP30 selectivity ABFE known-answer test on Vast.ai")
    ap.add_argument("--mode", choices=sorted(MODES), default=os.environ.get("ABFE_SEL_MODE", "solvent"))
    ap.add_argument("--n-replicates", type=int, default=int(os.environ.get("ABFE_SEL_N_REPLICATES", "3")))
    ap.add_argument("--seeds", default=None, help="comma-sep seeds to launch (overrides --n-replicates)")
    ap.add_argument("--n-iter", type=int, default=None)
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--stop", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    seeds = ([int(x) for x in a.seeds.split(",") if x.strip()] if a.seeds else None)
    if a.stop:
        stop_all()
    elif a.collect:
        collect()
    else:
        submit(mode=a.mode, n_replicates=a.n_replicates, seeds=seeds, dry_run=a.dry_run, n_iter=a.n_iter)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
