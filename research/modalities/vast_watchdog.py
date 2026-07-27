#!/usr/bin/env python3
"""Session-independent watchdog for ANY Vast job — a kind registry over one decision policy.

WHY THIS EXISTS, AND WHY IT IS NOT "ternary_vast_watchdog with more `if`s".
`ternary_vast_watchdog.py` closed the Vast monitoring gap for the RUNG 2b ternary legs and its classification
is right. Its ENTRY SCHEMA, though, is ternary-specific to the bone: `watch_entry(leg_id, seed, direction,
mode, timestep_fs, warmup_timestep_fs)`, a `unit_id` built from exactly those, and a relaunch that dispatches
the ternary launcher. Forcing a metadynamics MD leg into that schema would do one of two things, and both are
worse than no coverage:

  * invent relaunch parameters the leg was never launched with (the schema has nowhere to put `metad_ns`, so a
    relaunch would resume a 60 ns run and stop it at whatever the ternary defaults imply), or
  * track a progress scalar that measures nothing (a metad leg writes no OpenFE commit store at all, so the
    ternary census returns 0 forever and the leg reads as a permanent SETUP_STALL).

Monitoring that watches nothing is this repo's single most expensive defect class. A GCP watchdog sat
UNPARSEABLE for days, so its cron never fired and nobody noticed. A gating diagnostic returned success while
measuring nothing, seven separate ways. A collector read keys the driver never wrote and would have returned a
confident "inconclusive" on 24 perfect legs. So the generalisation here is deliberately narrow:

    ⛔ A JOB KIND THIS ENGINE DOES NOT GENUINELY UNDERSTAND IS REFUSED AT VALIDATION TIME, LOUDLY.

An entry cannot claim coverage it does not have. `watchdog_validate.validate(doc, known_kinds=set(KINDS))`
fails the pass on an entry naming a kind the running code does not implement, and each kind must supply a
result test, a MONOTONE progress scalar, a crash test and a faithful relaunch, or it does not get registered.

WHAT IS SHARED AND WHAT IS PER-KIND
  shared (watchdog_policy):  DONE / FAILED / RUNNING / SETUP_STALL / STALLED / DIED, "alive is not advancing",
                             only DIED relaunches, the per-UTC-day relaunch cap, refusing on an unparseable
                             counter. One implementation, imported — never a second copy that can disagree.
  per-kind:                  where the evidence comes from, what the scalar IS, the cold-start grace, and how
                             to re-dispatch EXACTLY what was launched.

THE SCALAR RULE, WHICH EVERY KIND MUST SATISFY
  RUNNING requires the scalar to have INCREASED since the previous tick. A rented Vast box can sit up with a
  dead container or an idle GPU and look perfectly healthy, so an instance existing is never progress. The
  scalar must therefore be (a) durable — in the object store, surviving the instance — and (b) MONOTONE across
  phase changes. Monotonicity is not a nicety: the paralogue MD job's natural scalar, simulated ns, RESETS TO
  ZERO at the metad -> release boundary, so a naive `done_ns` would read a healthy phase transition as a
  regression and stall-alert a perfectly good leg. Each kind therefore ranks its phases and returns
  rank * PHASE_STRIDE + progress-within-phase.

CAPACITY REFUSALS ARE NOT HANDLED HERE. `{"success": false, "error": "resources_unavailable"}` means that
machine's GPU is taken: destroy, exclude the machine id, pick another host — never wait, never raise the bid
(both were tried on 2026-07-25 and both failed). That policy already exists in each lane's launcher and ops
module and is DELEGATED to, so there is exactly one of it.

STATE LAYOUT (S3, under `_state_bucket`/`_state_prefix` from the watch list)
    watchdog/progress-<unit_id>.json      {"scalar": int, "stall": int, "utc": str, "verdict": str}
    watchdog/relaunch-<YYYYMMDD>-<unit_id>.json
    watchdog/heartbeat.json               {"utc": str, "entries": int, "verdicts": {...}}

NB a `schedule:` trigger only fires from the DEFAULT BRANCH, so .github/workflows/vast-watchdog.yml is inert
until merged to main.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import watchdog_validate as wdv  # noqa: E402
from gpu_backend import _vast_request  # noqa: E402
# `container_started_from_phase` lives in the shared policy module, not here: BOTH Vast lanes write
# their phase marker with the same `mark()` shell helper, so "did this box ever run" is one question
# with one answer, and a second copy is the thing this repo keeps paying for. Re-exported so callers
# and tests that reach for `vast_watchdog.container_started_from_phase` are unchanged.
from watchdog_policy import (  # noqa: E402,F401
    classify, container_started_from_phase, should_relaunch)

HERE = os.path.dirname(os.path.abspath(__file__))
WATCH_FILE = os.path.join(HERE, "vast-watch.json")
REPO_SLUG = os.environ.get("GITHUB_REPOSITORY", "trimcrae/Rare-cancers")

# Phase rank stride. Comfortably above any within-phase counter a kind produces (the paralogue MD kind's is
# milli-ns, so 60 ns -> 60_000), so rank always dominates and a phase advance can never read as a regression.
PHASE_STRIDE = 1_000_000


class Evidence:
    """Everything the shared policy needs about one unit, gathered by its kind. No verdicts here on purpose.

    `readable=False` means the kind could NOT determine progress this pass (an S3 listing failed, a phase
    marker was unparseable). That is emphatically not "zero progress": treating it as zero would manufacture a
    SETUP_STALL out of a network blip, so the engine SKIPS the entry and leaves the counters alone.
    """

    def __init__(self, *, has_result=False, has_failed_record=False, failed_detail="",
                 instance=None, instance_alive=False, instance_age_min=0.0,
                 scalar=0, scalar_label="", readable=True, note="", container_started=True):
        self.has_result = has_result
        self.has_failed_record = has_failed_record
        self.failed_detail = failed_detail
        self.instance = instance
        self.instance_alive = instance_alive
        self.instance_age_min = instance_age_min
        self.scalar = scalar
        self.scalar_label = scalar_label
        self.readable = readable
        self.note = note
        # Has the container ON THIS INSTANCE ever executed? Distinct from `scalar`, which is unit-scoped and
        # durable across hosts — see watchdog_policy.classify's `container_started` note. Defaults True so a
        # kind that cannot observe it is unchanged.
        self.container_started = container_started


def _s3():
    import boto3
    return boto3.client("s3")


def _read_json_key(bucket, key, default=None):
    try:
        return json.loads(_s3().get_object(Bucket=bucket, Key=key)["Body"].read().decode())
    except Exception:  # noqa: BLE001 — absent state is a legitimate first pass
        return default


def _write_json_key(bucket, key, doc):
    try:
        _s3().put_object(Bucket=bucket, Key=key, Body=json.dumps(doc, indent=2).encode())
        return True
    except Exception as e:  # noqa: BLE001
        print(f"::warning::watchdog state write failed for {key}: {type(e).__name__}: {e}")
        return False


def _key_exists(bucket, key):
    try:
        _s3().head_object(Bucket=bucket, Key=key)
        return True
    except Exception:  # noqa: BLE001
        return False


def _annotate(level, title, msg):
    print(f"::{level} title={title}::{msg}")


def instance_age_min(inst):
    try:
        return (time.time() - float(inst.get("start_date") or time.time())) / 60.0
    except (TypeError, ValueError):
        return 0.0


def container_diag(ev):
    """The one-line CONTAINER-SIDE diagnosis that belongs beside every stall alert.

    An alert that says only "frozen at leg-complex-running/260" sends a reader to look for a hung sampler, a
    NaN or a broken upload path. Vast's own `actual_status` and `status_msg` answer a prior question — is the
    container even running, and if not what is it doing — and they were sitting in the instance record the
    whole time the 2026-07-26 stall was being reported without them. The cost of not printing them was ~3 h
    of billed GPU and a human-equivalent having to go and read the docker layer messages by hand.
    """
    inst = ev.instance or {}
    if not inst:
        return "no instance record"
    msg = " ".join(str(inst.get("status_msg") or "").split())[:140]
    bits = [f"vast actual_status={inst.get('actual_status')!r}",
            f"cur_state={inst.get('cur_state')!r}",
            f"status_msg={msg!r}",
            f"gpu={inst.get('gpu_name')}",
            f"age={ev.instance_age_min:.0f}min"]
    if not ev.container_started:
        bits.append("⚠ THE CONTAINER ON THIS INSTANCE HAS NEVER RUN — the phase marker predates the rental, "
                    "so the frozen counter is its PREDECESSOR's last commit and no sampler is hung here. "
                    "status_msg above is what the box is actually doing (a docker layer line = image pull)")
    return "; ".join(bits)


# =============================================================================================================
# the in-flight interlock — the one thing a CRON watchdog needs that a single long-running watch does not
# =============================================================================================================
def workflow_runs_in_flight(workflow_file, repo=None):
    """(count, ok) of queued/in-progress runs of `workflow_file`. ok=False means the question was unanswerable.

    WHY A CRON WATCHDOG NEEDS THIS AND THE TERNARY ONE DOES NOT. The ternary lane has exactly one relaunch
    path — this watchdog. The paralogue lane already has its own long-running `watch` CI job that re-rents a
    dead leg, so two independent relaunchers exist for the same checkpoint prefix, and both would see the same
    hostless leg. Two hosts syncing the same S3 restart set is not a duplicated rental; it is an interleaved
    trajectory, i.e. a corrupted run that no error message announces. So a relaunch is only taken when the
    OWNING workflow has nothing in flight.

    FAIL-SAFE ON AN UNANSWERABLE QUESTION. If the API cannot be read we return ok=False and the engine refuses
    the relaunch. Refusing costs wall-clock on a leg that is already dead; guessing costs the run.

    Deliberately coarse — ANY in-flight run of that workflow blocks, not just its `watch` task. Distinguishing
    tasks needs a second API call per run and would trade a real corruption risk for a small latency win. The
    over-blocking is nearly free in practice: the other long task (`analyse`) only starts once every
    deliverable has landed, by which time these entries are DONE.
    """
    url = (f"https://api.github.com/repos/{repo or REPO_SLUG}/actions/workflows/"
           f"{workflow_file}/runs?per_page=30")
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "rare-cancers-vast-watchdog"})
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=30) as fh:
            doc = json.loads(fh.read().decode())
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"[interlock] could not read runs of {workflow_file}: {type(e).__name__}: {e}")
        return None, False
    live = [r for r in doc.get("workflow_runs", [])
            if r.get("status") in ("queued", "in_progress", "waiting", "requested", "pending")]
    return len(live), True


def relaunch_withheld(n_live, ok, owning):
    """(withhold?, reason). PURE — the fail-safe half of the interlock, separated so it is unit-testable.

    Withhold when the owning workflow has anything in flight, AND when the question could not be answered at
    all. Refusing to relaunch a leg that is already dead costs wall-clock; relaunching next to another
    relauncher costs the run.
    """
    if not ok:
        return True, (f"{owning} could not be queried, and that workflow re-rents dead legs itself — "
                      f"refusing to relaunch on an unanswerable question")
    if n_live:
        return True, f"{owning} has {n_live} run(s) in flight, and that workflow re-rents dead legs itself"
    return False, f"{owning} is idle — this watchdog is the only relauncher right now"


# =============================================================================================================
# KIND: ternary  — the RUNG 2b OpenFE legs. Registered so the engine genuinely covers this lane too; the
# SHIPPED generic watch list does not carry ternary entries, because ternary-vast-watchdog.yml already watches
# them and two relaunchers for one unit is the hazard above. tests/test_vast_watchdog.py asserts the two lists
# stay disjoint.
# =============================================================================================================
class TernaryKind:
    name = "ternary"
    label_prefix = "tvast"
    # Every parameter that keys the commit prefix, plus the branch. Identical to the ternary list's
    # `_prefix_keying_params` — same reason, same consequence if one is missing: the relaunch would resume a
    # DIFFERENT trajectory than the one being watched.
    required_keys = ("unit_id", "leg_id", "seed", "direction", "mode", "timestep_fs",
                     "warmup_timestep_fs", "git_branch", "max_relaunches_per_day", "enabled")
    setup_grace_min = 90.0     # stage -> pre-equil -> solvate/parameterise ~146k atoms -> minimise 12 replicas
    stall_ticks = 2            # a 40-iteration production commit is ~10 min of MD at 4 fs
    owning_workflow = None     # this watchdog IS the ternary relaunch path; nothing else to interlock against

    @staticmethod
    def preflight(entry):
        return []

    @staticmethod
    def probe(entry, insts):
        import ternary_vast_launch as tv
        uid = entry["unit_id"]
        rec = (tv.leg_records() or {}).get(uid) or {}
        inst = next((i for i in insts if tv.label_matches_unit(i.get("label"), uid)), None)
        phase, it, scalar = tv.committed_progress(uid)
        if scalar < 0:
            return Evidence(readable=False, note="commit store unlistable this pass")
        return Evidence(
            has_result=rec.get("status") == "done",
            has_failed_record=rec.get("status") == "failed",
            failed_detail=f"rc={rec.get('rc')} NaN_seen={rec.get('nan_seen')} at {rec.get('updated_utc')} "
                          f"tail={(rec.get('log_tail') or [])[-3:]}",
            instance=inst, instance_alive=inst is not None,
            instance_age_min=instance_age_min(inst) if inst else 0.0,
            scalar=scalar, scalar_label=(f"{phase}/{it}" if phase else "none (stage/pre-equil/minimise)"))

    @staticmethod
    def relaunch(entry, insts):
        import ternary_vast_launch as tv
        handles = tv.submit(mode=entry["mode"], timestep_fs=entry["timestep_fs"],
                            warmup_timestep_fs=entry["warmup_timestep_fs"],
                            legs=[(entry["leg_id"], entry["seed"], entry["direction"])])
        return handles[0] if handles else None


# =============================================================================================================
# KIND: paralogue_md — LANE 13's matched NR4A1 / NR4A2 metadynamics + release ensembles.
#
# WHY THIS KIND CAN BE SUPPORTED HONESTLY. Every question the policy asks has a real, already-written answer
# in the lane's own code, so nothing here is invented:
#   result   -> nr4a_paralogue_md_ops.result_key(name), the exact key the job uploads (reused, not re-derived)
#   progress -> phase.json {"phase", "extra": {"done_ns"}}, written by the job's 2-minute heartbeat thread
#   crash    -> the job marks metad_failed / release_failed / metad_stalled before returning non-zero
#   relaunch -> nr4a_paralogue_md_vast_launch.build_jobspec + the Vast backend, which is what the lane's own
#               relaunch_dead() calls; the checkpoint prefix is keyed by target+mode, so it RESUMES
#   instance -> the Vast label IS the JobSpec name, matched EXACTLY (see label_matches: a prefix match would
#               pair the real leg with its smoke leg)
# =============================================================================================================
class ParalogueMdKind:
    name = "paralogue_md"
    label_prefix = "nr4a-pdyn"
    # Nothing here is optional. build_jobspec() reads seed/segment_ns/image/bucket/result_prefix from the
    # ENVIRONMENT, so a relaunch that did not carry them would resume the right checkpoint and then run it
    # under different parameters — the "invents wrong relaunch parameters" failure this kind exists to avoid.
    # metad_ns / release_ns / n_rep do not key the checkpoint prefix, which is exactly why they must be
    # recorded: getting them wrong produces a silently SHORTER OR LONGER run under the same name.
    required_keys = ("kind", "unit_id", "target", "run_mode", "metad_ns", "release_ns", "n_rep",
                     "seed", "segment_ns", "image", "bucket", "result_prefix", "git_branch",
                     "owning_workflow", "max_relaunches_per_day", "enabled")
    # Cold start = multi-GB image pull + repo tarball + `aws s3 sync` of a resumed trajectory (a 60 ns metad
    # DCD at 141k atoms is ~2 GB) before the first phase marker. 90 min is past any healthy cold start; note
    # the window closes as soon as the job marks `metad`, which it does with done_ns=0 at the top of its loop.
    setup_grace_min = 90.0
    # The job's heartbeat republishes done_ns every 2 min, and the legs run ~5-6 ns/h, so any real tick
    # interval (the cron says */15 but GitHub throttles busy repos to ~55-65 min) sees a large advance. Two
    # frozen ticks is a genuine freeze, and it also absorbs the one non-advancing tick a resume can produce
    # (a preemption loses at most the 2-minute sync interval, ~0.19 ns, which the next tick recovers).
    stall_ticks = 2

    PHASE_RANK = {"resume_download": 0, "metad": 1, "release": 2, "package": 3, "done": 4}
    FAILED_PHASES = ("metad_failed", "release_failed", "metad_stalled")

    @staticmethod
    def preflight(entry):
        """Kind-specific refusals, beyond "are the keys present".

        THE SMOKE REFUSAL IS THE IMPORTANT ONE, and it is not hypothetical. At 8:28 PM ET on 2026-07-25 LANE
        13's own long-running watch died with
            ##[error]['nr4a-pdyn-nr4a2-smoke'] made no progress for 8 ticks (24 min)
        while both real legs were demonstrably advancing at 60-69 % GPU utilisation — because `leg_names()`
        synthesises a `-smoke` name per target whether or not a smoke leg was ever launched, and a leg that
        does not exist has a signature that can never change. A phantom entry took the monitoring down and
        left two billed legs unwatched. A smoke leg is a throwaway plumbing proof whose output must never even
        be collected, so this engine refuses to watch one at all rather than inherit that failure mode.
        """
        bad = []
        if str(entry.get("run_mode")) != "real":
            bad.append(f"run_mode={entry.get('run_mode')!r} — this kind watches REAL legs only. A smoke leg is "
                       f"a throwaway plumbing proof (its tarball must never be collected), and a smoke entry "
                       f"for a leg that was never launched is a phantom whose progress signature can never "
                       f"change — which is precisely what killed LANE 13's watch on 2026-07-25")
        if not str(entry.get("unit_id", "")).startswith(ParalogueMdKind.label_prefix):
            bad.append(f"unit_id={entry.get('unit_id')!r} is not a {ParalogueMdKind.label_prefix}-* leg name; "
                       f"the unit_id IS the Vast label and the S3 result prefix, so a mismatch watches nothing")
        return bad

    @staticmethod
    def label_matches(label, uid):
        """EXACT equality, never a prefix test. `nr4a-pdyn-nr4a1-smoke` startswith `nr4a-pdyn-nr4a1`, so a
        prefix match would pair the real leg with its smoke host and report a finished smoke as the real leg's
        instance. The lane already lost a `target_of()` to this exact string overlap."""
        return bool(label) and str(label).strip() == str(uid).strip()

    @staticmethod
    def _ops(entry):
        """Import the lane's own ops module with this entry's environment in place, then PROVE the constants
        it resolved match the entry. `RESULT_PREFIX` is read at module import time, so a module imported under
        a different environment would silently answer about a different S3 prefix — and a watchdog reading the
        wrong prefix is the "collector read keys the driver never wrote" bug with money attached."""
        os.environ["PDYN_RESULT_PREFIX"] = str(entry["result_prefix"])
        os.environ["VAST_CKPT_BUCKET"] = str(entry["bucket"])
        import nr4a_paralogue_md_ops as ops
        if ops.RESULT_PREFIX != str(entry["result_prefix"]):
            raise RuntimeError(
                f"nr4a_paralogue_md_ops resolved RESULT_PREFIX={ops.RESULT_PREFIX!r} but the watch entry says "
                f"{entry['result_prefix']!r}. The module was imported under a different environment, so every "
                f"key it computes is for the wrong run. Refusing.")
        return ops

    @staticmethod
    def score(ph):
        """phase.json -> (scalar, label, readable, failed, note). PURE, and the part that must be right.

        THE MONOTONICITY PROBLEM THIS SOLVES. `done_ns` is the job's own biased-ns counter, and it RESETS TO
        ZERO when the job moves from metadynamics to the unbiased release replicas — metad ends at 60 ns and
        release starts again from 0. A watchdog that used done_ns directly would read that healthy transition
        as a 60 ns regression, count it as no-advance, and stall-alert a perfectly good leg. So the phase is
        ranked and the scalar is rank * PHASE_STRIDE + milli-ns within the phase, which only ever increases.

        `readable=False` is returned rather than a number whenever the marker cannot be scored honestly — an
        unranked phase (the job gained a phase and this map was not updated) or an unparseable done_ns. Both
        would otherwise collapse to 0 and manufacture a SETUP_STALL out of a reporting change.
        """
        if ph is None:
            # No marker yet: the host is pulling the image / repo / checkpoint. Scalar 0 puts it inside the
            # cold-start grace, which is the correct reading — NOT "unreadable", which would skip the entry.
            return 0, "no phase marker yet (image pull / resume download)", True, False, ""
        phase = str(ph.get("phase") or "")
        extra = ph.get("extra") if isinstance(ph.get("extra"), dict) else {}
        if phase in ParalogueMdKind.FAILED_PHASES:
            return 0, phase, True, True, f"phase={phase} extra={extra} at {ph.get('utc')}"
        if phase not in ParalogueMdKind.PHASE_RANK:
            return 0, phase, False, False, (
                f"phase marker says {phase!r}, which this kind does not rank — the job gained a phase and "
                f"PHASE_RANK was not updated. Refusing to score it.")
        done_ns = extra.get("done_ns")
        try:
            within = int(round(float(done_ns) * 1000)) if done_ns is not None else 0
        except (TypeError, ValueError):
            return 0, phase, False, False, f"phase marker carries an unparseable done_ns={done_ns!r}"
        return (ParalogueMdKind.PHASE_RANK[phase] * PHASE_STRIDE + max(0, within),
                f"{phase}/{done_ns} ns", True, False, "")

    @staticmethod
    def probe(entry, insts):
        uid = entry["unit_id"]
        bucket = entry["bucket"]
        ops = ParalogueMdKind._ops(entry)
        has_result = _key_exists(bucket, ops.result_key(uid))

        # An `exited` container is NOT alive: it has stopped its own GPU billing and only CI can destroy the
        # instance, so it lingers in the listing. Counting it as alive would read a dead leg as RUNNING and
        # leave it hostless all night — which is the whole failure this watchdog exists to end.
        mine = [i for i in insts if ParalogueMdKind.label_matches(i.get("label"), uid)]
        inst = next((i for i in mine if i.get("actual_status") != "exited"), None)
        exited = next((i for i in mine if i.get("actual_status") == "exited"), None)
        note = ("an EXITED instance is still listed for this unit; the lane's own reap destroys it"
                if exited else "")

        ph = _read_json_key(bucket, f"{entry['result_prefix']}/{uid}/phase.json", default=None)
        scalar, label, readable, failed, why = ParalogueMdKind.score(ph)
        if not readable:
            return Evidence(has_result=has_result, readable=False, note=why)
        return Evidence(has_result=has_result, has_failed_record=failed, failed_detail=why,
                        instance=inst, instance_alive=inst is not None,
                        instance_age_min=instance_age_min(inst) if inst else 0.0,
                        scalar=scalar, scalar_label=label, note=note)

    @staticmethod
    def relaunch(entry, insts):
        """Re-rent this leg, resuming from its S3 checkpoint, with the parameters the entry records.

        Delegation, not reimplementation: this is the same build_jobspec + backend.submit pair the lane's own
        relaunch_dead() calls. The exclusion set is built the way the lane's watch builds it — every machine
        currently holding one of this fleet's instances — so a relaunch never lands back on a host that is
        already busy with (or has already refused) this fleet. Capacity refusals themselves are the launcher's
        policy: destroy, exclude, pick another host. Never wait, never raise the bid.
        """
        for k, v in (("PDYN_RESULT_PREFIX", entry["result_prefix"]), ("VAST_CKPT_BUCKET", entry["bucket"]),
                     ("VAST_IMAGE", entry["image"]), ("PDYN_SEED", str(entry["seed"])),
                     ("PDYN_SEGMENT_NS", str(entry["segment_ns"])), ("GIT_BRANCH", entry["git_branch"])):
            os.environ[k] = str(v)
        import nr4a_paralogue_md_vast_launch as L
        if L.VAST_IMAGE != str(entry["image"]) or L.RESULT_PREFIX != str(entry["result_prefix"]):
            raise RuntimeError(
                f"nr4a_paralogue_md_vast_launch resolved image={L.VAST_IMAGE!r} prefix={L.RESULT_PREFIX!r} but "
                f"the watch entry says image={entry['image']!r} prefix={entry['result_prefix']!r} — those are "
                f"read at import time, so this process would launch a different run under this leg's name.")
        excluded = {str(i["machine_id"]) for i in (insts or []) if i.get("machine_id")}
        excluded |= {x.strip() for x in str(entry.get("exclude_machines") or "").split(",") if x.strip()}
        spec = L.build_jobspec(str(entry["target"]).upper(), mode="real",
                               metad_ns=float(entry["metad_ns"]), release_ns=float(entry["release_ns"]),
                               n_rep=int(entry["n_rep"]), git_branch=str(entry["git_branch"]),
                               bucket=str(entry["bucket"]), exclude=tuple(sorted(excluded)))
        if spec.name != entry["unit_id"]:
            raise RuntimeError(f"relaunch would rent {spec.name!r} while the entry watches "
                               f"{entry['unit_id']!r} — the watch list and the launcher disagree about this "
                               f"leg's identity, so the relaunch would be invisible to the next pass.")
        from gpu_backend import get_backend
        h = get_backend("vast").submit(spec)
        return {"instance": h.job_id, "machine_id": h.extra.get("machine_id"), "bid": h.extra.get("bid")}


# =============================================================================================================
# KIND: step1_fanout — RUNG 4's cmpd19 congeneric RBFE map (tranche 1: 19 edges, charge-conserving leg,
# primary frame). One unit = one map edge = one rented GPU running BOTH alchemical legs and reducing them.
#
# WHY THIS KIND CAN BE SUPPORTED HONESTLY — every question the shared policy asks has a real answer already
# written in the lane's own code, so nothing here is invented:
#   result   -> congeneric_fanout.result_key(unit, prefix), the exact key the unit's reduce step uploads
#   progress -> congeneric_fanout_vast.committed_progress(), the spot commit store the SAMPLER writes
#   crash    -> the leg wrapper marks `leg-<L>-FAILED-rc<N>` / `leg-<L>-NORESULT` in phase.txt before exiting
#   relaunch -> congeneric_fanout_vast.build_jobspec + the Vast backend, i.e. exactly what mode_launch calls;
#               the checkpoint prefix is keyed by unit_id, so a relaunch RESUMES rather than restarting
#   instance -> the Vast label IS the JobSpec name, matched EXACTLY
#
# THE SCALAR IS COMPOSITE, and it has to be. The commit-store census alone is not monotone across a unit's
# lifetime for two independent reasons: (1) the iteration counter RESTARTS when the solvent leg begins after
# the complex leg finishes, and (2) it FREEZES, legitimately, while MBAR analysis runs at the end of each leg
# and again during the reduce. So the phase marker's rank is the high-order term and the census is the
# low-order one — phase advance can never read as a regression, and a frozen census inside a phase is still
# caught.
# =============================================================================================================
class Step1FanoutKind:
    name = "step1_fanout"
    label_prefix = "s1f-"
    required_keys = ("kind", "unit_id", "bucket", "result_prefix", "stage_prefix", "image", "n_windows",
                     "git_branch", "owning_workflow", "max_relaunches_per_day", "enabled")
    # Cold start is dominated by the ~6 GiB OpenFE image pull (documented 20-40 min on cheap 4090 hosts),
    # then the staged-pose download, solvate+parameterise of the ~35k-atom hybrid, and minimisation of 12
    # replicas — all before the first commit. Same 90 min the ternary kind uses; the system here is smaller
    # but the image pull, which dominates, is the same.
    setup_grace_min = 90.0
    # THREE, not two. At `RBFE_PROD_CKPT_ITERS=40` and ~13.6 s/iter a production commit lands every ~9 min,
    # so two ticks would normally be right — but this kind's scalar legitimately FREEZES during each leg's
    # MBAR analysis (12 windows) and during the reduce, with no phase change to mask it. A third tick keeps a
    # long analysis from alerting as a stall. It costs one extra tick of latency on a genuine freeze, and a
    # STALL only alerts (a relaunch would hang identically), so the trade is one-sided.
    stall_ticks = 3
    # EVERY OTHER RELAUNCHER OF THIS PREFIX, comma-separated — not just the first one that existed.
    # fusion-cpu-extras.yml's `launch`/`launch_confirm` mode re-rents any pending unit, and so does
    # step1-fanout-autoscale.yml's terminus-gated `launch` step (added 2026-07-26). Two hosts syncing one
    # commit store is an interleaved trajectory that nothing reports, so a relaunch is withheld while ANY of
    # them has anything in flight. It over-blocks (every monitor dispatch counts), and that is the correct
    # direction to be wrong in.
    #
    # ⚠ THE LIST IS THE WHOLE POINT AND IT WENT STALE ONCE ALREADY. This was the single string
    # "fusion-cpu-extras.yml" while step1-fanout-autoscale.yml was launching the same units, so the interlock
    # was asking about an unrelated workflow and would have answered "idle — I am the only relauncher" while
    # the autoscale tick was mid-launch. tests/test_vast_watchdog.py now DERIVES the required set from the
    # workflow files themselves, so adding a launcher without adding it here fails CI.
    owning_workflow = "fusion-cpu-extras.yml,step1-fanout-autoscale.yml"

    # phase.txt vocabulary, in order. Written by the per-instance pipeline's `mark` helper.
    PHASE_RANK = {"boot": 0, "staged": 1,
                  "leg-complex-running": 2, "leg-complex-done": 3,
                  "leg-solvent-running": 4, "leg-solvent-done": 5,
                  "reduce": 6, "done": 7}
    # Comfortably above any committed-iteration scalar (leg stride 1e7 + phase stride 1e6 + iterations), so
    # the phase rank always dominates.
    PHASE_MULT = 100_000_000

    @staticmethod
    def _failed(phase):
        return bool(phase) and ("FAILED" in phase or "NORESULT" in phase)

    @staticmethod
    def preflight(entry):
        bad = []
        uid = str(entry.get("unit_id", ""))
        try:
            import congeneric_fanout as cf
            known = {u["unit_id"] for u in cf.default_units()}
        except Exception as e:  # noqa: BLE001 — cannot enumerate: refuse rather than watch a guess
            return [f"could not enumerate tranche-1 units ({type(e).__name__}: {e}); refusing to claim cover"]
        if uid not in known:
            bad.append(f"unit_id={uid!r} is not a tranche-1 unit of the frozen map. The unit_id keys the S3 "
                       f"result AND the checkpoint prefix, so a mismatch watches (and would relaunch) "
                       f"nothing.")
        return bad

    @staticmethod
    def label_matches(label, uid):
        """The Vast label is `s1f-<idx>-<ligand_b>`, derived from the unit's position in the frozen map — it
        is NOT the unit_id. Derived here from the same enumeration the launcher uses, so the two cannot
        disagree about which box belongs to which edge."""
        import congeneric_fanout as cf
        units = cf.default_units()
        for i, u in enumerate(units):
            if u["unit_id"] == uid:
                return bool(label) and str(label).strip() == f"s1f-{i:02d}-{u['ligand_b']}"[:64]
        return False

    @staticmethod
    def _lane(entry):
        """Import the lane launcher with THIS entry's environment in place, then prove what it resolved.

        `BUCKET`, `RESULT_PREFIX`, `STAGE_PREFIX`, `FEP_IMAGE` and `N_WINDOWS` are all read at module import
        time in congeneric_fanout_vast, so a module imported under a different environment answers about a
        different run — every key it computes would be for the wrong prefix, and a relaunch would rent the
        wrong thing under this unit's name."""
        os.environ["VAST_CKPT_BUCKET"] = str(entry["bucket"])
        os.environ["RESULT_PREFIX"] = str(entry["result_prefix"])
        os.environ["STAGE_PREFIX"] = str(entry["stage_prefix"])
        os.environ["FEP_IMAGE"] = str(entry["image"])
        os.environ["N_WINDOWS"] = str(entry["n_windows"])
        import congeneric_fanout_vast as L
        mismatch = {k: (got, want) for k, got, want in
                    (("RESULT_PREFIX", L.RESULT_PREFIX, str(entry["result_prefix"])),
                     ("STAGE_PREFIX", L.STAGE_PREFIX, str(entry["stage_prefix"])),
                     ("FEP_IMAGE", L.FEP_IMAGE, str(entry["image"])),
                     ("BUCKET", L.BUCKET, str(entry["bucket"])),
                     ("N_WINDOWS", str(L.N_WINDOWS), str(entry["n_windows"])))
                    if got != want}
        if mismatch:
            raise RuntimeError(f"congeneric_fanout_vast was imported under a different environment: "
                               f"{mismatch}. Every key it computes would be for another run. Refusing.")
        return L

    @staticmethod
    def score(phase, census_scalar):
        """(scalar, label, readable, note). PURE — the composite-monotonicity argument, unit-testable.

        An UNRANKED phase returns readable=False rather than 0: the pipeline gained a marker this map does
        not know, and collapsing that to zero would manufacture a stall out of a reporting change."""
        if census_scalar < 0:
            return 0, "", False, "commit store unlistable this pass"
        if not phase:
            # No marker yet — the host is pulling the image. Scalar 0 is the CORRECT reading (it puts the
            # unit inside the cold-start grace), not "unreadable", which would skip the entry entirely.
            return 0, "no phase marker yet (image pull)", True, ""
        head = phase.split()[0]
        if Step1FanoutKind._failed(head):
            return 0, head, True, ""
        if head not in Step1FanoutKind.PHASE_RANK:
            return 0, head, False, (f"phase marker says {head!r}, which this kind does not rank — the "
                                    f"pipeline gained a phase and PHASE_RANK was not updated. Refusing.")
        return (Step1FanoutKind.PHASE_RANK[head] * Step1FanoutKind.PHASE_MULT + max(0, census_scalar),
                f"{head}/{census_scalar}", True, "")

    @staticmethod
    def probe(entry, insts):
        uid, bucket = entry["unit_id"], entry["bucket"]
        L = Step1FanoutKind._lane(entry)
        import congeneric_fanout as cf
        unit = next((u for u in cf.default_units() if u["unit_id"] == uid), None)
        if unit is None:
            return Evidence(readable=False, note=f"{uid} is not in the frozen map")
        has_result = _key_exists(bucket, cf.result_key(unit, str(entry["result_prefix"])))
        phase = L._get_text(L._s3(), bucket, f"{entry['result_prefix']}/{uid}/phase.txt")
        census, _detail = L.committed_progress(L._s3(), bucket, unit)
        scalar, label, readable, why = Step1FanoutKind.score(phase, census)
        if not readable:
            return Evidence(has_result=has_result, readable=False, note=why)

        # An `exited` container has already stopped its own GPU billing and only CI destroys the instance, so
        # it lingers in the listing. Counting it as alive reads a dead unit as RUNNING and leaves it hostless.
        mine = [i for i in insts if Step1FanoutKind.label_matches(i.get("label"), uid)]
        inst = next((i for i in mine if i.get("actual_status") != "exited"), None)
        note = "an EXITED instance is still listed for this unit; the lane's own collect reaps it" \
            if any(i.get("actual_status") == "exited" for i in mine) else ""
        return Evidence(has_result=has_result,
                        has_failed_record=Step1FanoutKind._failed(phase or ""),
                        failed_detail=f"phase.txt={phase!r} — the leg wrapper always ships its log to "
                                      f"{entry['result_prefix']}/{uid}/<leg>.log even on failure",
                        instance=inst, instance_alive=inst is not None,
                        instance_age_min=instance_age_min(inst) if inst else 0.0,
                        # The unit's scalar is durable and outlives its host; this bit is about the BOX. A
                        # resumed unit carries a non-zero scalar onto a fresh instance, which is precisely
                        # how a 2 h 57 min image pull reported itself as a frozen sampler on 2026-07-26.
                        container_started=container_started_from_phase(phase, inst),
                        scalar=scalar, scalar_label=label, note=note)

    @staticmethod
    def reap_exited(entry, insts):
        """Destroy any EXITED instance still listed for this unit. Returns a list of destroyed ids.

        ★ AN `exited` VAST INSTANCE IS NOT PROVABLY DEAD (LANE 21, 2026-07-26 — observed, not theorised).
        `probe` skips exited instances when deciding `instance_alive`, on the reasoning that an exited
        container has already stopped billing and merely lingers until CI reaps it. That reasoning has a hole:
        instance 45938720 read `actual_status="exited"` at 7:49 PM ET and its container was back up and
        re-marking `boot 2026-07-26T23:50:49Z` two minutes later, on the same instance id — running -> exited
        -> running. The container stdout carries both boot sequences, so this is the box's own record of it.

        A unit in that state reads DIED, and DIED relaunches. That is a SECOND host on one checkpoint prefix
        — precisely the interleaved-trajectory failure the owning_workflow interlock exists to prevent,
        arriving by a route the interlock does not cover (no workflow is in flight; the duplicate comes from
        the instance itself).

        So the relaunch destroys the ambiguous box FIRST. After a successful DELETE it cannot come back, and
        the replacement is provably the only writer. If the DELETE fails we do NOT relaunch — one host that
        might restart beats two that certainly conflict.
        """
        key = os.environ.get("VAST_API_KEY")
        if not key:
            return []
        uid = entry["unit_id"]
        gone = []
        for i in insts or []:
            if i.get("actual_status") != "exited" or not Step1FanoutKind.label_matches(i.get("label"), uid):
                continue
            _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
            gone.append(i.get("id"))
        return gone

    @staticmethod
    def quarantine(entry, inst):
        """Destroy an instance whose container never started, and refuse its machine for this lane. Returns
        a human-readable outcome, or "" if the kind declines / cannot act.

        THIS IS NOT A RELAUNCH, AND THAT SEPARATION IS THE WHOLE DESIGN. `should_relaunch` still authorises
        only DIED, because a STALLED unit relaunched is a hung sampler re-hung at full price. A box that has
        never executed its container is the other thing entirely — CLAUDE.md's Vast rule for a host that
        never starts: destroy it, exclude the machine, take another host. Quarantine performs only the first
        two. The unit then reads DIED on the NEXT pass and goes out through the existing capped,
        interlocked relaunch path, with the bad machine already in the exclusion set that path consults.
        Nothing new is authorised to spend; a provable non-scientific host failure is simply converted into
        the case the policy already knows how to handle.
        """
        key = os.environ.get("VAST_API_KEY")
        iid = (inst or {}).get("id")
        if not key or iid is None:
            return ""
        L = Step1FanoutKind._lane(entry)
        _vast_request("DELETE", f"/instances/{iid}/", key)
        out = f"destroyed instance {iid}"
        mid = (inst or {}).get("machine_id")
        if mid is not None and L._record_exclusion(
                L._s3(), str(entry["bucket"]), mid,
                f"container never started: {instance_age_min(inst):.0f} min from rental with no phase mark "
                f"of its own (instance {iid})"):
            out += f"; machine {mid} added to the lane exclusion set"
        return out

    @staticmethod
    def relaunch(entry, insts):
        """Re-rent this unit, resuming from its S3 commit store. Delegation, not reimplementation: the same
        build_jobspec + backend.submit pair mode_launch uses, with the same exclusion discipline (never land
        back on a machine already holding one of this fleet's instances, nor on one the lane has excluded)."""
        uid = entry["unit_id"]
        L = Step1FanoutKind._lane(entry)
        import congeneric_fanout as cf
        units = cf.default_units()
        idx = next(i for i, u in enumerate(units) if u["unit_id"] == uid)
        excluded = {str(i["machine_id"]) for i in (insts or []) if i.get("machine_id")}
        excluded |= set(L._load_excluded(L._s3(), str(entry["bucket"]))[0])
        excluded |= {x.strip() for x in str(entry.get("exclude_machines") or "").split(",") if x.strip()}
        spec = L.build_jobspec(units[idx], str(entry["git_branch"]), str(entry["bucket"]), idx,
                               exclude_machine_ids=tuple(sorted(excluded)))
        if not Step1FanoutKind.label_matches(spec.name, uid):
            raise RuntimeError(f"relaunch would rent {spec.name!r} while the entry watches {uid!r} — the "
                               f"watch list and the launcher disagree about this unit's identity, so the "
                               f"relaunch would be invisible to the next pass.")
        from gpu_backend import get_backend
        h = get_backend("vast").submit(spec)
        return {"instance": h.job_id, "machine_id": h.extra.get("machine_id"), "bid": h.extra.get("bid")}


KINDS = {k.name: k for k in (TernaryKind, ParalogueMdKind, Step1FanoutKind)}


# =============================================================================================================
# watch-list I/O and the arming read-back
# =============================================================================================================
def load_watch(path=None):
    p = path or WATCH_FILE
    try:
        with open(p) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"watch": []}


def save_watch(doc, path=None):
    with open(path or WATCH_FILE, "w") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")


def enabled_entries(doc):
    """The entries this pass should act on. PURE. An absent/!dict/empty list is a legitimate no-op."""
    if not isinstance(doc, dict):
        return []
    return [w for w in (doc.get("watch") or []) if isinstance(w, dict) and w.get("enabled")]


def paralogue_entry(target, *, git_branch, metad_ns=60, release_ns=5, n_rep=3, seed="1", segment_ns="20",
                    image="docker.io/triskit23/nr4a-metad:latest",
                    bucket="sagemaker-us-east-2-646605541856", result_prefix="nr4a-paralogue-ensemble",
                    owning_workflow="gpu-nr4a-paralogue-md-vast.yml", exclude_machines="",
                    max_relaunches_per_day=6, enabled=True):
    """One paralogue_md watch entry. PURE, and the ONLY place a shipped entry may come from.

    The defaults are the values LANE 13 actually launched the live legs with, read out of its task file and
    workflow rather than assumed: metad_ns 60, release_ns 5, n_rep 3, and blank dispatch inputs for image and
    bucket so the launcher's own module defaults apply. tests/test_vast_watchdog.py asserts the SHIPPED JSON is
    byte-identical to what this builder produces, so the committed list cannot be hand-typed drift.
    """
    tgt = str(target).upper()
    return {
        "kind": "paralogue_md",
        "unit_id": f"nr4a-pdyn-{tgt.lower()}",
        "target": tgt,
        "run_mode": "real",
        "metad_ns": metad_ns,
        "release_ns": release_ns,
        "n_rep": n_rep,
        "seed": str(seed),
        "segment_ns": str(segment_ns),
        "image": image,
        "bucket": bucket,
        "result_prefix": result_prefix,
        "git_branch": git_branch,
        "owning_workflow": owning_workflow,
        "exclude_machines": exclude_machines,
        "max_relaunches_per_day": int(max_relaunches_per_day),
        "enabled": bool(enabled),
    }


def step1_fanout_entry(unit_id, *, git_branch, bucket="sagemaker-us-east-2-646605541856",
                       result_prefix="nr4a3-step1-fanout/results",
                       stage_prefix="nr4a3-step1-fanout/stage",
                       image="docker.io/triskit23/nr4a3fep:latest", n_windows=12,
                       owning_workflow=Step1FanoutKind.owning_workflow, exclude_machines="",
                       max_relaunches_per_day=6, enabled=True, why=""):
    """One step1_fanout watch entry. PURE, and the ONLY place a shipped entry may come from.

    The defaults are congeneric_fanout_vast's own module defaults, which is what the launcher runs with when
    the workflow passes nothing — so an entry built here relaunches the SAME job that was launched. They are
    recorded on the entry rather than left implicit because every one of them is read at module-import time:
    a relaunch under different values would resume the right checkpoint and then run it as a different
    calculation, silently.

    ⚠ An entry is added when its unit is actually LAUNCHED, never in advance. A step1_fanout entry for a unit
    that was never launched has no phase marker and no instance, so past the cold-start grace the engine
    classifies it DIED and relaunches it — the watch list would start renting GPUs nobody authorised.
    """
    e = {
        "kind": "step1_fanout",
        "unit_id": str(unit_id),
        "bucket": bucket,
        "result_prefix": result_prefix,
        "stage_prefix": stage_prefix,
        "image": image,
        "n_windows": int(n_windows),
        "git_branch": git_branch,
        "owning_workflow": owning_workflow,
        "exclude_machines": exclude_machines,
        "max_relaunches_per_day": int(max_relaunches_per_day),
        "enabled": bool(enabled),
    }
    if why:
        e["_why"] = why
    return e


def verify_armed(unit_ids, path=None):
    """Assert that every named unit is present AND enabled AND passes validation. Raises otherwise.

    WHY A SEPARATE READ-BACK. The failure this catches is not the arming misbehaving — it is the file being
    changed AFTERWARDS by something with no idea a leg was running. That happened on 2026-07-25: a launch job
    armed its probe and committed it, then a later edit to the same file rewrote `"watch"` to `[]` and pushed.
    The watchdog's only input then said there was nothing to watch, while a billed GPU leg ran unwatched — and
    it would have reported "idle" with a green tick. The config guard cannot catch that, because an EMPTY list
    is a legitimate state (nothing running) and must stay a no-op. Only something that knows which units are
    supposed to be covered can tell "nothing to watch" from "what I was watching went missing".
    """
    doc = load_watch(path)
    armed = {w.get("unit_id") for w in enabled_entries(doc)}
    missing = sorted(set(unit_ids) - armed)
    if missing:
        raise SystemExit(f"[verify-armed] THE WATCH LIST DOES NOT COVER {missing}. A leg may be billing with "
                         f"nothing watching it. Fix {path or WATCH_FILE} and commit before walking away.")
    problems = wdv.validate(doc, known_kinds=set(KINDS))
    if problems:
        raise SystemExit(f"[verify-armed] the watch list covers {sorted(unit_ids)} but does NOT validate: "
                         f"{problems}. An entry the guard rejects aborts every pass, so this is the same as "
                         f"not being watched at all.")
    print(f"[verify-armed] all {len(set(unit_ids))} unit(s) present, enabled and valid in "
          f"{os.path.basename(path or WATCH_FILE)}")
    return sorted(set(unit_ids))


# =============================================================================================================
# one pass
# =============================================================================================================
def tick(path=None, dry_run=False):
    """One watchdog pass over the enabled entries of a multi-kind watch list. Returns the alert count."""
    doc = load_watch(path)
    state_bucket = doc.get("_state_bucket") or "sagemaker-us-east-2-646605541856"
    state_prefix = (doc.get("_state_prefix") or "vast-watchdog").rstrip("/")

    # CONFIG GUARD FIRST, and it is what makes "cannot claim coverage it does not have" true rather than
    # aspirational: an entry naming an unimplemented kind, or missing a parameter its relaunch needs, aborts
    # the whole pass. It lives in a FILE, not inline in the workflow, because the last inline `python3 -c`
    # guard sat at column 0, dedented out of its `run: |` block, made the workflow invalid YAML — and a
    # `schedule:` cron on an unparseable file simply never fires. The guard against acting on bad config
    # stopped the watchdog running at all, silently, for days.
    problems = wdv.validate(doc, known_kinds=set(KINDS))
    for who, kind, missing in problems:
        _annotate("error", "VAST WATCHDOG CONFIG INVALID",
                  f"{who} kind={kind}: {'; '.join(missing)}. Refusing to act on ANY entry this pass.")
    if problems:
        return len(problems)

    entries = enabled_entries(doc)
    print(f"enabled watch entries: {len(entries)} (dry_run={dry_run})")

    # HEARTBEAT, read BEFORE it is written: the gap since the previous pass is the only in-band evidence that
    # the cron is actually firing at the cadence anybody believes it is. GitHub throttles schedules on busy
    # repos, so `*/15` really lands ~55-65 min apart — that is expected and is reported, not "fixed".
    hb_key = f"{state_prefix}/watchdog/heartbeat.json"
    prev_hb = _read_json_key(state_bucket, hb_key, {}) or {}
    gap = ""
    if prev_hb.get("epoch"):
        try:
            gap = f"{(time.time() - float(prev_hb['epoch'])) / 60.0:.0f} min since the previous pass"
        except (TypeError, ValueError):
            gap = "previous heartbeat unparseable"
    else:
        gap = "no previous heartbeat (first pass, or state was cleared)"
    _annotate("notice", "VAST WATCHDOG HEARTBEAT",
              f"pass at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} — {len(entries)} enabled "
              f"entr(ies) across kinds {sorted({e.get('kind') for e in entries})}; {gap}.")

    if not entries:
        _annotate("notice", "VAST WATCHDOG idle",
                  f"No enabled entries in {os.path.basename(path or WATCH_FILE)} — nothing to watch.")
        if not dry_run:
            _write_json_key(state_bucket, hb_key, {"epoch": int(time.time()), "entries": 0, "verdicts": {},
                                                   "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return 0

    key = os.environ.get("VAST_API_KEY")
    if not key:
        _annotate("error", "VAST WATCHDOG BLIND",
                  "VAST_API_KEY absent — cannot tell a live leg from a dead one; taking no action.")
        return 1
    try:
        all_insts = _vast_request("GET", "/instances/", key).get("instances", [])
    except Exception as e:  # noqa: BLE001
        # Without the instance list we cannot tell DIED from RUNNING, and guessing DIED would relaunch on top
        # of a live leg — two hosts writing one checkpoint prefix. Refuse the pass instead.
        _annotate("error", "VAST WATCHDOG BLIND",
                  f"could not list Vast instances ({type(e).__name__}: {e}) — refusing to act this pass "
                  f"rather than risk relaunching on top of a live leg.")
        return 1

    alerts = 0
    verdicts = {}
    day = time.strftime("%Y%m%d", time.gmtime())
    interlock_cache = {}
    for e in entries:
        uid = e["unit_id"]
        kind = KINDS[e["kind"]]
        print(f"=============== {uid}  [{kind.name}] ===============")
        bad = kind.preflight(e)
        if bad:
            alerts += 1
            verdicts[uid] = "REFUSED"
            _annotate("error", "VAST WATCHDOG ENTRY REFUSED",
                      f"{uid} — this engine will not watch it: {'; '.join(bad)}")
            continue
        insts = [i for i in all_insts if (i.get("label") or "").startswith(kind.label_prefix)]
        try:
            ev = kind.probe(e, insts)
        except Exception as ex:  # noqa: BLE001 — one entry must not abandon the others
            alerts += 1
            verdicts[uid] = "PROBE_FAILED"
            _annotate("error", "VAST WATCHDOG PROBE FAILED",
                      f"{uid} — the {kind.name} probe raised {type(ex).__name__}: {ex}. Taking no action on "
                      f"this entry; a probe that cannot answer must never be read as 'dead'.")
            continue
        if not ev.readable:
            verdicts[uid] = "UNREADABLE"
            _annotate("warning", "VAST WATCHDOG progress unreadable",
                      f"{uid} — {ev.note or 'progress could not be read this pass'}; leaving the counters "
                      f"alone. (An unreadable scalar is NOT zero progress.)")
            continue

        pkey = f"{state_prefix}/watchdog/progress-{uid}.json"
        prev = _read_json_key(state_bucket, pkey, {}) or {}
        verdict, stall = classify(
            has_result=ev.has_result, has_failed_record=ev.has_failed_record,
            instance_alive=ev.instance_alive, instance_age_min=ev.instance_age_min,
            container_started=ev.container_started,
            progress_scalar=ev.scalar, prev_scalar=int(prev.get("scalar") or 0),
            prev_stall=int(prev.get("stall") or 0),
            setup_grace_min=float(e.get("setup_grace_min") or kind.setup_grace_min),
            stall_ticks=int(e.get("stall_ticks") or kind.stall_ticks))
        verdicts[uid] = verdict
        iid = ev.instance.get("id") if ev.instance else None
        print(f"verdict={verdict} progress={ev.scalar_label} scalar={ev.scalar} prev={prev.get('scalar')} "
              f"stall={stall} instance={iid} age={ev.instance_age_min:.0f}min {ev.note}")
        if ev.instance_alive:
            print(f"  container: {container_diag(ev)}")
        if not dry_run:
            wrote = _write_json_key(state_bucket, pkey,
                                    {"scalar": ev.scalar, "stall": stall, "kind": kind.name,
                                     "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                     "phase": ev.scalar_label, "verdict": verdict})
            if not wrote:
                # THIS IS AN ALERT, NOT A WARNING. `prev_scalar` is the ONLY memory this watchdog has. If the
                # write keeps failing, every pass reads prev=0, every pass therefore sees "advanced", and the
                # stall detector can never fire again — the watchdog goes on reporting RUNNING forever while
                # measuring nothing. That is the exact defect class this whole file exists to prevent, so it
                # fails the job rather than leaving a ::warning:: nobody opens.
                alerts += 1
                _annotate("error", "VAST WATCHDOG STATE WRITE FAILED",
                          f"{uid} — could not persist progress state to s3://{state_bucket}/{pkey}. Without "
                          f"it prev_scalar is 0 on every pass, so EVERY tick reads as 'advanced' and the "
                          f"stall detector is silently disabled. Fix the credentials/bucket before trusting "
                          f"any RUNNING verdict from this watchdog.")

        if verdict == "DONE":
            _annotate("notice", "VAST WATCHDOG DONE",
                      f"{uid} — the result artifact is in S3. Set enabled=false for this entry.")
            continue
        if verdict == "FAILED":
            alerts += 1
            _annotate("error", "VAST WATCHDOG LEG FAILED",
                      f"{uid} — the leg RAN and recorded a failure ({ev.failed_detail}). NOT relaunching: it "
                      f"would fail the same way, and uncapped it would buy a full-length rental per attempt. "
                      f"Diagnose, then clear the record or disable the entry.")
            continue
        if verdict == "RUNNING":
            # ⚠ "RUNNING" with a container that has not started means STILL IN COLD START, not advancing —
            # say so, or the notice reads as progress that is not happening.
            _annotate("notice", "VAST WATCHDOG RUNNING",
                      (f"{uid} — instance {iid} is inside its cold-start grace and its container has NOT "
                       f"started yet, so nothing is sampling. {container_diag(ev)}. Leaving it alone until "
                       f"the grace expires."
                       if not ev.container_started else
                       f"{uid} — advancing at {ev.scalar_label} on instance {iid} "
                       f"({(ev.instance or {}).get('gpu_name')}, up {ev.instance_age_min:.0f} min, "
                       f"gpu_util={(ev.instance or {}).get('gpu_util')}). Leaving it alone."))
            continue
        if verdict == "SETUP_STALL":
            alerts += 1
            # THE ONE CASE THAT SELF-RECOVERS, because it is the one case where the diagnosis is already
            # complete and is not about the science. See Step1FanoutKind.quarantine for why this does not
            # weaken "only DIED relaunches".
            quarantined = ""
            if not ev.container_started and not dry_run and hasattr(kind, "quarantine"):
                try:
                    quarantined = kind.quarantine(e, ev.instance) or ""
                except Exception as ex:  # noqa: BLE001 — a failed reap must not abandon the other entries
                    quarantined = f"quarantine raised {type(ex).__name__}: {ex} — the box is STILL BILLING"
            _annotate("error", "VAST WATCHDOG SETUP STALL",
                      f"{uid} — instance {iid} up {ev.instance_age_min:.0f} min with NO progress at all "
                      f"(grace {e.get('setup_grace_min') or kind.setup_grace_min:.0f} min). Setup is hung, not "
                      f"slow. CONTAINER: {container_diag(ev)}. "
                      + (f"REAPED: {quarantined} — it had made no progress ON THIS HOST, so there is no "
                         f"sampler state to lose; the unit reads DIED next pass and the existing capped "
                         f"relaunch path re-rents it elsewhere."
                         if quarantined else
                         "NOT relaunching — a relaunch would hang the same way; check the image pull, the "
                         "checkpoint sync and GPU utilisation."))
            continue
        if verdict == "STALLED":
            alerts += 1
            _annotate("error", "VAST WATCHDOG STALLED",
                      f"{uid} — instance {iid} is up but progress has been frozen at {ev.scalar_label} for "
                      f"{stall} consecutive passes. The science is not advancing. NOT relaunching — diagnose "
                      f"before spending more. CONTAINER: {container_diag(ev)}. The container IS running and "
                      f"its counter is not moving, so the live hypotheses are a hung window, a swallowed "
                      f"exception/NaN, or a broken commit-upload path — read "
                      f"{e.get('result_prefix')}/{uid}/<leg>.log and the container stdout, not the box state.")
            continue

        # ---- DIED: no result, no instance. Relaunch, capped, and never against a second relauncher. --------
        # A prefix may have MORE THAN ONE other relauncher (step1_fanout has two), so `owning_workflow` is a
        # comma-separated list and EVERY name in it must be idle. Withhold on the first that is not: one
        # busy relauncher is enough to make a second host on this checkpoint prefix possible, and that is the
        # failure being prevented. A single name still parses as a one-element list, so nothing else changes.
        owning = e.get("owning_workflow") or getattr(kind, "owning_workflow", None)
        owners = [w.strip() for w in str(owning).split(",") if w.strip()] if owning else []
        withheld = False
        for own in owners:
            if own not in interlock_cache:
                interlock_cache[own] = workflow_runs_in_flight(own)
            n_live, ok = interlock_cache[own]
            withhold, why_interlock = relaunch_withheld(n_live, ok, own)
            if withhold:
                alerts += 1
                _annotate("error", "VAST WATCHDOG DIED — RELAUNCH WITHHELD",
                          f"{uid} — no result and no instance, but {why_interlock}. Two relaunchers on one "
                          f"checkpoint prefix means two hosts writing one restart set: an interleaved "
                          f"trajectory that nothing reports. Withholding; the relaunch will be taken on the "
                          f"next pass once that workflow is idle.")
                withheld = True
                break
            print(f"[interlock] {why_interlock}")
        if withheld:
            continue
        ckey = f"{state_prefix}/watchdog/relaunch-{day}-{uid}.json"
        cnt = int((_read_json_key(state_bucket, ckey, {}) or {}).get("count") or 0)
        ok, why = should_relaunch(verdict, cnt, e.get("max_relaunches_per_day", 6))
        if not ok:
            alerts += 1
            _annotate("error", "VAST WATCHDOG CAPPED",
                      f"{uid} — died again but {why}. NOT relaunching; needs a human.")
            continue
        if dry_run:
            _annotate("notice", "VAST WATCHDOG would-relaunch",
                      f"{uid} — died (no result, no instance), {why}. dry_run=1 so taking no action.")
            continue
        # An `exited` box for this unit is destroyed BEFORE the replacement is rented — it is not provably
        # dead until it is gone (Step1FanoutKind.reap_exited). A failure here withholds the relaunch rather
        # than risking two hosts on one checkpoint prefix.
        if hasattr(kind, "reap_exited"):
            try:
                for gone in kind.reap_exited(e, insts):
                    print(f"[reap] destroyed exited instance {gone} before relaunching {uid} — an exited "
                          f"Vast box has been observed coming back up, which would make two writers")
            except Exception as ex:  # noqa: BLE001
                alerts += 1
                _annotate("error", "VAST WATCHDOG RELAUNCH WITHHELD — COULD NOT REAP",
                          f"{uid} — an exited instance is still listed and destroying it raised "
                          f"{type(ex).__name__}: {ex}. NOT relaunching: an exited Vast box can come back "
                          f"(observed 2026-07-26 on 45938720), and a replacement alongside it would put two "
                          f"hosts on one checkpoint prefix.")
                continue
        print(f"relaunching {uid} ({why}) — resumes from its last checkpoint")
        try:
            h = kind.relaunch(e, insts)
            if h:
                _write_json_key(state_bucket, ckey, {"count": cnt + 1, "unit_id": uid,
                                                     "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                                          time.gmtime())})
                _annotate("notice", "VAST WATCHDOG RELAUNCHED",
                          f"{uid} — was dead (no result, no instance); rented instance {h.get('instance')} on "
                          f"machine {h.get('machine_id')}, {why}. Resumes from its last checkpoint.")
            else:
                alerts += 1
                _annotate("error", "VAST WATCHDOG RELAUNCH PRODUCED NOTHING",
                          f"{uid} — died and the relaunch rented no host (no rentable offer, or every "
                          f"candidate machine is excluded). Needs a human.")
        except Exception as ex:  # noqa: BLE001 — one entry must not abandon the others
            alerts += 1
            _annotate("error", "VAST WATCHDOG RELAUNCH FAILED",
                      f"{uid} — died AND the relaunch raised {type(ex).__name__}: {ex}. Needs a human.")

    if not dry_run:
        _write_json_key(state_bucket, hb_key,
                        {"epoch": int(time.time()), "entries": len(entries), "verdicts": verdicts,
                         "alerts": alerts, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    print(f"watchdog pass complete; {alerts} alert(s); verdicts={verdicts}")
    return alerts


def merge_branch_watch_list(branch, path=None, repo_root=None):
    """Fold a FLEET BRANCH's `vast-watch.json` into the checked-out (main) one. Returns a report string.

    ★★ THE ENGINE IS MAIN'S; THE WATCH LIST IS THE LAUNCHER'S (LANE 21, 2026-07-26).
    `_arm_watchdog` exists so that "an 18-unit wave that arms nothing would put eighteen billed GPUs beyond
    any monitoring" cannot happen — its own docstring. But it writes `vast-watch.json` inside a CI job whose
    commit step pushes to the FLEET BRANCH, while this workflow runs from a `schedule`, which only fires from
    the default branch, with a bare `actions/checkout` — so the tick reads MAIN's copy. The arming is real and
    lands somewhere the watchdog never looks. Tonight's single shakeout entry is on main only because a lane
    happened to merge; the eighteen that the terminus gate releases would not be, and would run unwatched at
    roughly $0.2/hr each for up to ~13.7 h.

    The split is the right one and is kept: the ENGINE must be main's reviewed code, because that is what
    makes it session-independent; the LIST is live operational state that only the launcher can write. So the
    list is fetched from where it is written and merged over main's.

    MERGE RULES, and why each is the safe direction:
      * union by unit_id, the BRANCH copy winning — it is the live writer, so its `enabled` and its
        parameters are the current ones;
      * an entry that exists only on main is KEPT, never dropped — main carries finished units flipped to
        `enabled: false` for the record, and other lanes' kinds;
      * ANY failure (branch absent, file absent, unparseable, not the expected shape) leaves the working-tree
        file byte-untouched and returns a warning. The fallback is therefore exactly today's behaviour, which
        is what makes this safe to put in front of a scheduled job whose documented worst failure is not
        running at all.
    The merged file still goes through `watchdog_validate` before anything acts on it, so a malformed branch
    list aborts the pass rather than steering it.
    """
    import subprocess
    path = path or WATCH_FILE
    root = repo_root or os.path.dirname(os.path.dirname(HERE))
    rel = os.path.relpath(path, root)
    branch = (branch or "").strip()
    if not branch:
        return "[watch-merge] no fleet branch given — using the checked-out list unchanged"
    try:
        # NO `--depth 1`. On the CI runner the checkout is already shallow and a plain fetch stays that
        # way, so the flag bought nothing there — but run in a full DEVELOPER clone (which the unit test
        # below does, deliberately, because a mocked git proves nothing about git) it WRITES .git/shallow and
        # silently truncates that clone's history. The next `git merge` in it then dies with "refusing to
        # merge unrelated histories". A diagnostic helper must not be able to damage the repo it is run in.
        subprocess.run(["git", "fetch", "origin", branch], cwd=root,
                       check=True, capture_output=True, timeout=180)
        raw = subprocess.run(["git", "show", f"origin/{branch}:{rel}"], cwd=root,
                             check=True, capture_output=True, timeout=60).stdout
        theirs = json.loads(raw.decode())
        assert isinstance(theirs.get("watch"), list)
    except Exception as e:  # noqa: BLE001
        return (f"[watch-merge] ⚠ could not read {rel} from origin/{branch} ({type(e).__name__}: {e}) — "
                f"using the checked-out list unchanged. Any unit armed only on that branch is UNWATCHED.")
    try:
        with open(path) as fh:
            ours = json.load(fh)
    except Exception as e:  # noqa: BLE001
        return f"[watch-merge] ⚠ could not read the checked-out {rel} ({type(e).__name__}: {e}) — no merge"
    mine = {e.get("unit_id"): e for e in ours.get("watch", [])}
    added, replaced = [], []
    for entry in theirs["watch"]:
        uid = entry.get("unit_id")
        if uid is None:
            continue
        if uid in mine:
            if mine[uid] != entry:
                replaced.append(uid)
            mine[uid] = entry
        else:
            mine[uid] = entry
            added.append(uid)
    if not added and not replaced:
        return f"[watch-merge] origin/{branch} agrees with the checked-out list ({len(mine)} entries)"
    ours["watch"] = list(mine.values())
    with open(path, "w") as fh:
        json.dump(ours, fh, indent=2)
    n_on = sum(1 for e in ours["watch"] if e.get("enabled"))
    return (f"[watch-merge] took the list from origin/{branch}: +{len(added)} new {added}, "
            f"{len(replaced)} updated {replaced}; {len(ours['watch'])} entries, {n_on} enabled")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Session-independent watchdog for any Vast job kind")
    ap.add_argument("--merge-branch-list", metavar="BRANCH", default=None,
                    help="fold that branch's vast-watch.json into the checked-out one before acting; any "
                         "failure leaves the checked-out list untouched")
    ap.add_argument("--tick", action="store_true", help="run one watchdog pass")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--watch-file", default=None)
    ap.add_argument("--kinds", action="store_true", help="list the job kinds this engine implements")
    ap.add_argument("--verify-armed", metavar="UNIT_IDS",
                    help="comma-separated unit_ids that MUST be present, enabled and valid; exit non-zero "
                         "otherwise. Run it after arming, and in CI.")
    ap.add_argument("--disable", metavar="UNIT_ID", help="set enabled=false for one entry")
    a = ap.parse_args(argv)
    if a.merge_branch_list:
        print(merge_branch_watch_list(a.merge_branch_list, a.watch_file))
        return 0
    if a.kinds:
        for n, k in sorted(KINDS.items()):
            print(f"{n}: label_prefix={k.label_prefix} grace={k.setup_grace_min:.0f}min "
                  f"stall_ticks={k.stall_ticks} required={list(k.required_keys)}")
        return 0
    if a.verify_armed:
        verify_armed([x.strip() for x in a.verify_armed.split(",") if x.strip()], a.watch_file)
        return 0
    if a.disable:
        doc = load_watch(a.watch_file)
        for w in doc.get("watch", []):
            if w.get("unit_id") == a.disable:
                w["enabled"] = False
        save_watch(doc, a.watch_file)
        print(f"[disable] {a.disable}")
        return 0
    alerts = tick(path=a.watch_file, dry_run=a.dry_run)
    # A non-zero exit makes GitHub send its own workflow-failure notification — the alert path that does not
    # depend on an agent, a session, or anyone thinking to open a log. RUNNING/DONE stay green.
    return 1 if alerts else 0


if __name__ == "__main__":
    raise SystemExit(main())
