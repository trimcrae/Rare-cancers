#!/usr/bin/env python3
"""IS THIS RENTED BOX DOING ANY USEFUL WORK? — the anti-idle verdict, in one pure function.

★ WHY THIS EXISTS (2026-07-27). Two 5a-KS ternary legs (Vast 45972721 / 45974679) lost their S3 credential
mid-run at 7:27 AM ET when an exposed key was rotated. The driver died on its first failed commit, Vast
restarted the onstart, staging failed again on the same dead key, and both containers sat in a ~13-30 s
crash-loop — `stage cache MISS` -> `FAILED at staging` -> `Killed` -> repeat — with `gpu_util: 0.0` on reads
28 minutes apart, **while still billing**. Both stayed `actual_status: running` throughout. The only thing
that would eventually have stopped them was a multi-hour runtime backstop.

★★ AND THE HOST CANNOT FIX THIS ITSELF. MEASURED, NOT ASSUMED. `gpu_backend._VAST_SELFSTOP` arms a bash EXIT
trap (`poweroff || shutdown -h now || kill -9 -1 || kill -9 1`) that CLAUDE.md §6 described as guaranteeing
no idle-GPU billing. Reproduced in a private PID namespace (`unshare -fp --mount-proc`, 2026-07-27), with a
child shell playing the onstart script exactly as Vast runs it:

    poweroff        -> "System has not been booted with systemd as init system (PID 1). Can't operate."
    shutdown -h now -> the same
    kill -9 1       -> returns SUCCESS, and PID 1 SURVIVES   (kernel SIGNAL_UNKILLABLE: a PID-namespace init
                       ignores any signal it has no handler for, and SIGKILL cannot be handled)
    kill -9 -1      -> kills every other process AND the caller, and PID 1 SURVIVES
                       (`man 2 kill`: pid == -1 sends to every permitted process "except for process 1")

So the chain kills the job and leaves the container up — which is precisely what "still `running`, GPU idle,
still billing" looked like. There is no unprivileged in-container action that ends a Vast rental, and
`kill -9 1` returning 0 is why the failure was silent. **Only the control plane (which holds VAST_API_KEY)
can stop the meter**, so the guarantee has to live HERE, outside the box, and CLAUDE.md §6 now says so.

=============================================================================================================
THE DISCRIMINATOR, AND THE FALSE POSITIVE THAT WOULD BE WORSE THAN THE BUG
=============================================================================================================
The tempting rule is "GPU idle for N minutes -> destroy". **That rule is wrong and this module never uses
it.** A ternary leg is legitimately at 0 % GPU for its whole cold start: repo pull, stage (~15 min), the
openff/interchange parameterisation of a ~146k-atom hybrid (CPU+RAM bound, tens of minutes), minimise.
Reaping that is a self-inflicted copy of the waste we are trying to stop — the same rental paid twice, plus
the setup thrown away. **So `gpu_util` here can only ever SAVE a box, never condemn one.** It appears in
exactly one clause, and that clause is checked LAST — after the log-silence test, because a busy GPU on a
host that can no longer write is not work, it is work being computed into a void.

★★ THAT IS NOT A DESIGN ASSERTION — IT IS A MEASURED FACT, AND HERE IS THE COUNTEREXAMPLE (step 1 fan-out,
12:34 PM ET 2026-07-27). Two boxes read **`gpu_util = 0.0`** in the SAME snapshot in which their units
committed real production sampling:

    s1f-13-cw_ms_free_acid   gpu_util 0.0   complex/production@360 -> @440   (+80 iterations)
    s1f-04-cw_ev_5ch2nh2     gpu_util 0.0   complex/production@280 -> @320   (+40 iterations)

Both were advancing at the 40-iteration production commit interval WHILE REPORTING ZERO GPU. Vast's
`gpu_util` is an instantaneous sample from host-side telemetry that can be stale or caught between kernels,
so **a 0.0 reading is not evidence of idleness on this lane — it is frequently no evidence at all.** Had the
tempting rule been in force, both of those boxes would have been destroyed mid-production and their sampling
thrown away.

⚠ SO DO NOT "IMPROVE" THIS MODULE BY MAKING IDLENESS CONDEMNING. The next reader will be tempted, because a
fleet-wide column of 0.0 looks damning at a glance. It is not. **The committed-iteration census is the only
trustworthy forward-motion signal on this lane**, and `progress_advanced` is checked before `gpu_util` for
exactly that reason — verified against this code path on the live shape above, where
`(gpu_util=0.0, progress_advanced=True)` returns WORKING and `(gpu_util=0.0, log_age_min=None,
progress_advanced=False)` returns UNKNOWN rather than WEDGED.

What condemns a box is the absence of any POSITIVE evidence of forward motion, and there are two channels,
each covering the other's blind spot. Both are durable (they live in the object store, not on the host) and
both are SELF-TIMESTAMPING, so a verdict needs one poll and no history:

  1. **LOG SILENCE.** `run_ternary_leg.sh` runs a sync loop that PUTs `/tmp/run.log` every 120 s, and `mark`
     PUTs it again at every phase change. During ANY legitimate phase — including the GPU-idle ones — that
     object's mtime advances every couple of minutes. A log older than `LOG_SILENCE_MIN` means the host has
     lost its write path or is wedged; either way it can no longer checkpoint, so whatever it is computing
     is already unrecoverable. **This is the channel that catches the 2026-07-27 dead-credential case**, in
     which the crash-loop wrote nothing at all.
  2. **RESTART CHURN.** Each container start truncates `/tmp/run.log` and archives the previous one to
     `attempts/run-<UTC>.log`, so the count of those keys IS a durable count of container starts, and the
     timestamp is IN THE KEY. A legitimate rental adds one. `CRASH_LOOP_STARTS` inside
     `CRASH_LOOP_WINDOW_MIN` is a crash-loop and nothing else. **This is the channel that catches a
     crash-loop whose S3 still works** — the shape that left seventeen 168-byte archived attempts on the
     first 5a-KS smoke (2026-07-26).

And one channel that overrides both, because measured work beats every inference about the box (the same
precedence `watchdog_policy.classify` already applies): **the committed progress scalar advanced.** If the
science moved, the box is working, whatever anything else says.

FAIL-SAFE DIRECTION. Every verdict this module can return either destroys a box or does nothing, so every
ambiguity resolves to doing nothing: no instance record, no unit mapping, an unreadable listing, a box too
young, a container that has not started -> UNKNOWN / COLD_START, and the caller leaves it alone. A guard
that can spend money by being wrong must be biased towards being useless rather than towards being wrong.

WHERE THE VERDICT IS ACTED ON. `ternary_vast_launch.collect` — one clause alongside the existing
result-in-S3 / recorded-failure / runtime-backstop reaps. It is deliberately NOT a cross-lane sweeper that
destroys instances it has no evidence about; a lane opts in by gathering the evidence its own artifacts
provide and calling `classify_idle`.
"""
from __future__ import annotations

import calendar
import os
import re
import sys
import time

# ---------------------------------------------------------------------------------------------------------
# thresholds. Every one is a DURATION or a COUNT of durable events, never a tick count, for the reason
# `relaunch_market_gate` records: this repo's crons are throttled to roughly one run per workflow per hour,
# so "2 consecutive ticks" is not a knowable duration. A self-timestamping observation needs neither.
# ---------------------------------------------------------------------------------------------------------

# gpu_util at or above this is proof of GPU work. Only ever used to SAVE a box (see the module docstring);
# a low value never condemns one. 5 % rather than 0 % because the Vast field is a sampled average and a box
# between MD chunks can read a percent or two without being idle.
GPU_BUSY_PCT = float(os.environ.get("VAST_IDLE_GPU_BUSY_PCT") or "5")

# How long the run.log may go unwritten before the host is declared wedged. The sync loop PUTs every 2 min,
# so this is ~7 consecutive missed uploads — comfortably past a transient S3 blip, and 3.5x faster than the
# 45-min stopped-box backstop that is the tightest reap this lane had.
LOG_SILENCE_MIN = float(os.environ.get("VAST_IDLE_LOG_SILENCE_MIN") or "15")

# Container starts within CRASH_LOOP_WINDOW_MIN that mean "crash-loop, not a resume". A spot preemption plus
# the collect nudge can legitimately restart a container twice in a window; three is not a thing a healthy
# leg does, and the observed loop period was 13-30 s.
CRASH_LOOP_STARTS = int(os.environ.get("VAST_IDLE_CRASH_LOOP_STARTS") or "3")
CRASH_LOOP_WINDOW_MIN = float(os.environ.get("VAST_IDLE_CRASH_LOOP_WINDOW_MIN") or "15")

# A hard floor on instance age. Nothing is ever condemned inside this, whatever the evidence says, because a
# box that has just started may not have uploaded anything yet and `container_started` is itself derived
# from an object that may not have landed.
MIN_INSTANCE_AGE_MIN = float(os.environ.get("VAST_IDLE_MIN_AGE_MIN") or "15")

# When a `running` box that has never marked a phase stops being a slow start and becomes a wedge. NOT a new
# number: this is the repo's existing cold-start line, `watchdog_policy.DEFAULT_SETUP_GRACE_MIN`, imported
# rather than re-typed (CLAUDE.md §1 — one fact, one home). If that line moves, this moves with it.
try:
    from watchdog_policy import DEFAULT_SETUP_GRACE_MIN as SETUP_GRACE_MIN
except Exception:  # noqa: BLE001 — keep this module importable standalone (it is pure policy)
    SETUP_GRACE_MIN = float(os.environ.get("TVAST_SETUP_GRACE_MIN") or "90")

WORKING, COLD_START, CRASH_LOOP, WEDGED, UNKNOWN, WATCHING, UNIT_FAILED = (
    "WORKING", "COLD_START", "CRASH_LOOP", "WEDGED", "UNKNOWN", "WATCHING", "UNIT_FAILED")

# The ONLY two verdicts that spend nothing and stop a meter. Everything else leaves the box alone.
DESTROY_VERDICTS = (CRASH_LOOP, WEDGED, UNIT_FAILED)


def should_destroy(verdict) -> bool:
    """Is this verdict an instruction to destroy the instance? The caller must not invent its own rule."""
    return verdict in DESTROY_VERDICTS


def _as_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def classify_idle(*, instance_running, container_started=True, gpu_util=None, progress_advanced=False,
                  log_age_min=None, log_unchanged_min=None, start_ages_min=None, instance_age_min=None,
                  gpu_busy_pct=None, log_silence_min=None, crash_loop_starts=None,
                  crash_loop_window_min=None, min_instance_age_min=None, setup_grace_min=None,
                  unit_failed=False):
    """Return (verdict, reason) for ONE live instance. PURE — no network, no clock, no I/O.

    Arguments are EVIDENCE, gathered by the lane that owns the artifacts:
      instance_running   the Vast record's actual_status == "running". Anything else is somebody else's
                         clause (the stopped-box nudge, the frozen-image-pull reap) and is left alone here.
      container_started  has THIS box's container ever executed? `watchdog_policy.container_started_from_phase`
                         answers it from the phase marker's own timestamp against the instance start_date.
      gpu_util           Vast's sampled GPU utilisation, percent. May be None. NEVER condemns (see docstring).
      progress_advanced  did the durable committed-iteration scalar go UP since the previous poll?
      log_age_min        minutes since the host last PUT its run.log, or None if it never has. ⚠ On a lane
                         whose entry script syncs the log from a background TIMER, this measures the sync
                         loop and NOT the leg — see condemnation 3.
      log_unchanged_min  minutes for which the run.log's CONTENT has been byte-identical across polls, or
                         None if unknown / not tracked. Unlike the mtime this cannot be advanced by a timer
                         re-PUTting the same bytes, which is what makes it the usable wedge signal.
      start_ages_min     minutes-ago of each recorded container start (from the `attempts/` archive keys),
                         or None if the listing could not be read. An empty LIST means "read it, nothing
                         there", which is a real observation; None means "could not read", which is not.
      instance_age_min   minutes since the instance was created.
      unit_failed        the LEG'S OWN record in the object store says `status: failed`, and the caller has
                         already verified that record is NEWER than this instance (protfep_vast_launch.
                         `_record_is_newer_than_instance`) so a stale failure cannot reap a fresh host. This
                         is a SELF-REPORT, not an inference — see the clause below for why it goes first.

    The order of the clauses is the argument. Positive evidence first, then the two ignorance guards, then
    the two condemnations — so nothing can be condemned on evidence that a later clause would have excused.
    """
    gpu_busy_pct = GPU_BUSY_PCT if gpu_busy_pct is None else gpu_busy_pct
    log_silence_min = LOG_SILENCE_MIN if log_silence_min is None else log_silence_min
    crash_loop_starts = CRASH_LOOP_STARTS if crash_loop_starts is None else crash_loop_starts
    crash_loop_window_min = CRASH_LOOP_WINDOW_MIN if crash_loop_window_min is None else crash_loop_window_min
    min_instance_age_min = MIN_INSTANCE_AGE_MIN if min_instance_age_min is None else min_instance_age_min
    setup_grace_min = SETUP_GRACE_MIN if setup_grace_min is None else setup_grace_min

    if not instance_running:
        return UNKNOWN, "instance is not `running`; the stopped/frozen clauses own this box, not the idle guard"

    # ---- the leg's own obituary, read BEFORE anything is inferred about the host. ----
    # ★★ A DEAD UNIT AND A WEDGED HOST HAVE THE SAME REMEDY AND OPPOSITE MEANINGS (2026-07-27, the valB
    # closure triangle). Both `calib_lo_to_lo2` legs exited rc=1 on a Python exception, uploaded leg.json and
    # run.log — the S3 PUTs are the LAST lines in the tail — and then stopped writing because there was
    # nothing left to write. Thirty-eight minutes later the silence clause below condemned them as
    # "the host has lost its write path", which the artifacts in the same readout flatly contradict: the
    # write path was the last thing that demonstrably WORKED. The destroy was right and the sentence was
    # wrong, and a reader chasing a fleet of dead credentials would have been chasing nothing.
    # So a unit that recorded its own failure gets its own verdict. It is first because every clause below
    # is an INFERENCE about a host from indirect evidence, and none of them may overwrite a self-report:
    # `progress_advanced` cannot be true for a leg that has exited (the scalar is durable and static), and
    # the cold-start floor must NOT hold a dead rental for another hour of grace it can never use.
    if unit_failed:
        return UNIT_FAILED, ("the leg's own record says status=failed — this host is not wedged, its unit is "
                             "DEAD, and no further billing on it can produce anything")

    # ---- the one absolute override: measured work. Nothing below may overrule a scalar that went UP. ----
    if progress_advanced:
        return WORKING, "the committed progress scalar advanced since the last poll — the GPU did work"

    age = _as_float(instance_age_min)
    if age is not None and age < min_instance_age_min:
        return COLD_START, (f"instance is {age:.0f} min old, under the {min_instance_age_min:g} min floor — "
                            "too young to have proved anything either way")

    # ---- a container that has never marked anything, on a box Vast already calls `running`. ----
    # ⚠ This clause exists because COLD_START used to be unbounded, and that was a hole big enough to hide
    # the whole incident in: if the object store is dead from the FIRST second of the rental, the phase
    # marker never lands, `container_started` reads False forever, and the guard politely does nothing while
    # the box crash-loops to the 22 h runtime backstop. Note it is safe against LANE 21's 2 h 57 min image
    # pull for a structural reason, not a lucky threshold: during a pull Vast reports `actual_status:
    # loading`, so the `instance_running` clause above has already excluded it. Once the status IS `running`
    # the marker is written within seconds of the container starting (`mark start` is the script's first
    # act), so 90 min of `running` with no marker is not a slow start.
    if not container_started:
        if age is not None and age >= setup_grace_min:
            return WEDGED, (f"instance has been `running` for {age:.0f} min (>= {setup_grace_min:g}) and has "
                            f"still never written a phase marker — its container cannot reach the object "
                            f"store at all, so it can neither stage nor checkpoint")
        return COLD_START, ("the container has not marked a phase yet — inside the cold-start grace, so the "
                            "SETUP_STALL clause owns this, not the idle guard")

    # ---- condemnation 1: restart churn. Unambiguous, and independent of whether the GPU ever ran. ----
    if start_ages_min is not None:
        recent = [a for a in (_as_float(x) for x in start_ages_min)
                  if a is not None and 0 <= a <= crash_loop_window_min]
        if len(recent) >= crash_loop_starts:
            return CRASH_LOOP, (f"{len(recent)} container starts in the last {crash_loop_window_min:g} min "
                                f"(>= {crash_loop_starts}) with no GPU work — the container is restarting "
                                f"into the same failure, not resuming")

    # ---- condemnation 2: the host has stopped writing. Catches the dead-credential wedge. ----
    # ★ AND IT IS CHECKED BEFORE `gpu_util`, WHICH IS THE ONE PLACE A BUSY GPU DOES NOT SAVE A BOX.
    # A host that cannot write cannot checkpoint, so a busy GPU here is not work — it is work being
    # computed into a void, and every iteration of it will be discarded at the next boundary anyway (the
    # driver aborts there, by design: see rbfe_spot_driver._commit). Letting a high `gpu_util` veto this
    # would keep exactly the wrong box alive. A HEALTHY leg never reaches this clause: it commits every
    # ~40 iterations, which is far inside one poll, so `progress_advanced` catches it above.
    silence = _as_float(log_age_min)
    if silence is not None and silence >= log_silence_min:
        return WEDGED, (f"run.log last written {silence:.0f} min ago (>= {log_silence_min:g}) with no "
                        f"committed progress — the host has lost its write path, so it cannot checkpoint "
                        f"and nothing it is doing can be recovered")

    # ---- condemnation 3: the host is still uploading, and uploading the SAME BYTES. ----
    # ★★ THE CLAUSE ABOVE IS VACUOUS ON THIS LANE, AND THAT WAS MEASURED, NOT SUSPECTED (2026-07-30).
    # `run_ternary_leg.sh` syncs run.log from a BACKGROUND TIMER every ~120 s, unconditionally. So its S3
    # mtime tracks the sync loop's health, never the leg's: `log_age_min` sits at ~2 min forever, the
    # 15-minute silence test can never be reached, and every wedge falls through to WATCHING — "quiet but
    # alive: run.log 2 min old", which is true and useless.
    # Host 46286994 wedged that morning INSIDE a checkpoint persist (commit-store generation fa5da1eb holds
    # simulation.nc and nothing else; _persist writes .nc -> .chk -> manifest). It then billed for 77
    # minutes at gpu_util 0.0 while the guard reported it healthy every poll, because the sync loop kept
    # PUTting an unchanged file.
    # Identical CONTENT is the honest signal, and it is exactly the "measured absence of writes" the module
    # docstring already requires before condemning anything — a re-PUT of unchanged bytes IS an absence of
    # writes. GPU idleness still condemns nothing: this clause needs no gpu_util at all.
    frozen = _as_float(log_unchanged_min)
    if frozen is not None and frozen >= log_silence_min:
        return WEDGED, (f"run.log has been re-uploaded with byte-identical content for {frozen:.0f} min "
                        f"(>= {log_silence_min:g}) and the committed scalar has not advanced — the sync "
                        f"loop is alive but the leg is not writing, so nothing is being produced to save")

    # ---- the GPU-busy reprieve, deliberately LAST. It can only ever save a box, never condemn one. ----
    util = _as_float(gpu_util)
    if util is not None and util >= gpu_busy_pct:
        return WORKING, f"gpu_util={util:g}% >= {gpu_busy_pct:g}% and the host is still writing — GPU busy"

    if silence is None:
        return UNKNOWN, ("the container has started but no run.log has ever been uploaded — no evidence to "
                         "judge on, so leaving it alone")

    # The reason NAMES which evidence is missing, because "quiet but alive" was the sentence this guard
    # printed over a wedged, billing host every three minutes for over an hour.
    _content = (f", content changing (last change {frozen:.0f} min ago)" if frozen is not None
                else ", CONTENT IDENTITY NOT TRACKED — the mtime alone cannot distinguish a writing host "
                     "from a timer re-uploading the same bytes")
    return WATCHING, (f"quiet but alive: run.log {silence:.0f} min old{_content}, GPU idle, no committed "
                      f"advance — consistent with a CPU-bound setup phase")


# ---------------------------------------------------------------------------------------------------------
# evidence gathering — the only impure part, kept separate so the policy above stays testable without S3
# ---------------------------------------------------------------------------------------------------------

# `run_ternary_leg.sh` archives the previous attempt's log as `attempts/run-<UTC>.log` as its FIRST act after
# the log is rotated, so the timestamp is in the key and needs no S3 metadata. Anchored with `run-` and a
# full 16-char stamp so an unrelated key under attempts/ cannot be misread as a container start.
_ATTEMPT_RE = re.compile(r"/run-(\d{8}T\d{6}Z)\.log$")


def start_ages_min(s3, bucket, attempts_prefix, now=None):
    """Minutes-ago of every recorded container start under `attempts_prefix`, or None if it cannot be read.

    None vs [] is load-bearing and is the whole reason this returns two different empty-ish things: [] says
    "the listing succeeded and there are no archived attempts", which is the normal first rental; None says
    "the listing failed", which must never be read as "no restarts" — that is how a listing outage would
    silently disable the crash-loop channel. `classify_idle` skips the clause entirely on None.
    """
    now = time.time() if now is None else now
    out = []
    try:
        pag = s3.get_paginator("list_objects_v2")
        for page in pag.paginate(Bucket=bucket, Prefix=attempts_prefix.lstrip("/")):
            for obj in page.get("Contents", []):
                m = _ATTEMPT_RE.search("/" + obj["Key"])
                if not m:
                    continue
                try:
                    t = calendar.timegm(time.strptime(m.group(1), "%Y%m%dT%H%M%SZ"))
                except (ValueError, TypeError):
                    continue
                out.append((now - t) / 60.0)
    except Exception as e:  # noqa: BLE001 — an unreadable listing is NOT evidence of no restarts
        print(f"[idle-guard] could not list {attempts_prefix}: {type(e).__name__}: {e}")
        return None
    return out


def main(argv):
    """Explain the policy, or classify one evidence blob given as JSON on stdin (for CI / ad-hoc checks)."""
    import json
    if len(argv) > 1 and argv[1] == "--explain":
        print("vast_idle_guard thresholds:")
        print(f"  GPU_BUSY_PCT           = {GPU_BUSY_PCT:g} %   (only ever SAVES a box; never condemns one)")
        print(f"  LOG_SILENCE_MIN        = {LOG_SILENCE_MIN:g} min")
        print(f"  CRASH_LOOP_STARTS      = {CRASH_LOOP_STARTS} starts in {CRASH_LOOP_WINDOW_MIN:g} min")
        print(f"  MIN_INSTANCE_AGE_MIN   = {MIN_INSTANCE_AGE_MIN:g} min (hard floor, nothing acts inside it)")
        print(f"  SETUP_GRACE_MIN        = {SETUP_GRACE_MIN:g} min (a `running` box with no phase marker; "
              f"imported from watchdog_policy)")
        print(f"  destroy verdicts       = {', '.join(DESTROY_VERDICTS)}")
        return 0
    ev = json.load(sys.stdin)
    verdict, why = classify_idle(**ev)
    print(json.dumps({"verdict": verdict, "destroy": should_destroy(verdict), "why": why}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
