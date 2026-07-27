#!/usr/bin/env python3
"""The Vast watchdog's DECISION POLICY, in one place, for every job kind.

WHY IT IS ITS OWN MODULE. It was written for the ternary lane and it was right — DONE / FAILED / RUNNING /
SETUP_STALL / STALLED / DIED, "alive is not advancing", only DIED relaunches, capped per UTC day. None of that
reasoning is ternary-specific: every clause takes the evidence as an ARGUMENT, so the only thing that made it
ternary was where the evidence came from. Generalising the watchdog to other Vast jobs therefore meant either
importing this policy or writing a second copy of it, and a second copy is exactly the thing this repo keeps
paying for — two monitors that can disagree about whether a leg is dead is worse than one monitor.

So `ternary_vast_watchdog` re-exports these names (its callers and tests are unchanged) and `vast_watchdog`
imports them for every other kind. There is one implementation.

WHAT A KIND SUPPLIES AND WHAT IT MUST NOT. A kind supplies EVIDENCE — does the result artifact exist, is an
instance alive, how old is it, what is the monotone progress scalar, is there a recorded crash — plus its own
`setup_grace_min` / `stall_ticks`, because a cold start is kind-specific (an OpenFE ternary leg solvates and
minimises a ~146k-atom hybrid; a metadynamics MD leg pulls a multi-GB image and re-syncs a trajectory). A kind
does NOT get to supply its own verdicts. That asymmetry is the point: a kind that cannot produce honest
evidence must be REFUSED at validation time, not given a private definition of "running".
"""

from __future__ import annotations

import os

# Grace before "zero progress" is called a stall rather than a slow start. Kind-specific in practice, so the
# engine passes it explicitly; these are the ternary lane's historical values and stay the defaults so that
# module's behaviour is unchanged by the move.
DEFAULT_SETUP_GRACE_MIN = float(os.environ.get("TVAST_SETUP_GRACE_MIN") or "90")
# Consecutive no-advance ticks before a frozen counter is a stall.
DEFAULT_STALL_TICKS = int(os.environ.get("TVAST_STALL_TICKS") or "2")


def classify(*, has_result, instance_alive, instance_age_min, progress_scalar, prev_scalar, prev_stall,
             has_failed_record=False, container_started=True,
             setup_grace_min=DEFAULT_SETUP_GRACE_MIN, stall_ticks=DEFAULT_STALL_TICKS):
    """The watchdog's verdict for one entry, and the new stall counter. PURE.

    Returns (verdict, new_stall) where verdict is one of:
        DONE          the result artifact exists — nothing to do
        FAILED        the leg RAN and recorded a failure — alert, do NOT relaunch
        RUNNING       an instance is up and the progress scalar ADVANCED this tick
        SETUP_STALL   an instance is up, has made NO progress at all, and is past the cold-start grace
        STALLED       an instance is up, has made some progress, and has not advanced for `stall_ticks`
        DIED          no result and no instance — relaunch

    Note what is NOT here: "an instance exists" never on its own yields RUNNING. That is the whole
    correction over a liveness ping, and it is why every kind must define a scalar that only a working
    GPU can move.

    And note why FAILED is separated from DIED, which is the difference between a preemption and a crash.
    A preempted host is killed mid-run and writes NO record, so it correctly reads DIED and resuming from
    the checkpoint is exactly right. A leg that RAN and recorded a failure — a warmup NaN, a metadynamics
    segment that returned non-zero — has a reason it failed, and relaunching it reproduces that reason.
    Collapsing the two would let one NaN buy a full-length rental per attempt, each dying the same way.
    A crash is a diagnosis job.

    ★ `container_started` — WHY A RESUMED UNIT COULD NOT REACH SETUP_STALL, AND WHY THAT COST ~3 h OF GPU
    (LANE 21, 2026-07-26). SETUP_STALL used to be gated on `progress_scalar <= 0`, i.e. on the UNIT never
    having progressed — but the scalar is durable in the object store and SURVIVES the host. So a unit that
    is resumed onto a fresh box after a preemption arrives carrying its predecessor's non-zero scalar, and
    from that moment the `<= 0` gate can never be true again for it. Its new box therefore reads STALLED
    however long its container takes to start, and STALLED deliberately does not act.

    That is exactly what happened: instance 45938720 sat in Vast `actual_status="loading"` for 2 h 57 min
    pulling the ~6 GiB OpenFE image while the watchdog reported `STALLED ... frozen at
    leg-complex-running/260`. The 260 was the PREVIOUS host's last commit; the new host had not executed one
    instruction. "Frozen sampler" and "container that never started" are opposite failures with opposite
    fixes, and the policy could not tell them apart because it was reading a UNIT-scoped scalar to answer an
    INSTANCE-scoped question.

    So the kind now supplies that instance-scoped bit separately, and it dominates the scalar: a live
    instance whose container has never run has made no progress ON THIS HOST no matter what the unit's
    durable counter says. Defaults to True, so any caller that does not (or cannot) answer keeps the old
    behaviour exactly — a kind that cannot observe container start must never manufacture a fault.
    """
    if has_result:
        return "DONE", 0
    if has_failed_record and not instance_alive:
        return "FAILED", 0
    if not instance_alive:
        return "DIED", 0
    advanced = progress_scalar > prev_scalar
    new_stall = 0 if advanced else int(prev_stall) + 1
    if advanced:
        # ★ MEASURED WORK BEATS EVERY INFERENCE ABOUT THE BOX, and this guard is here because the
        # `container_started` clause below can now trigger a DESTROY. `container_started` is derived from the
        # phase marker, and `mark` swallows its own upload failures (`| $AWS s3 cp - … || true`) — so one S3
        # hiccup at boot leaves the PREVIOUS host's marker in place while the new host samples perfectly
        # happily, because the sampler commits to the object store on a different path from `phase.txt`.
        # Without this line that box reads "container never started" at the grace boundary and gets reaped
        # mid-leg. A counter that went UP is direct evidence the GPU did the work; nothing inferred may
        # overrule it. (No behaviour change for any pre-existing caller: an advanced scalar is > 0 and resets
        # the stall counter, so every one of them already fell through to RUNNING here.)
        return "RUNNING", 0
    if not container_started:
        # No progress is POSSIBLE on this host yet, so the only question is whether it is still inside the
        # cold-start grace. Checked before the scalar, because the scalar is about the unit and this is
        # about the box we are paying for.
        if instance_age_min >= setup_grace_min:
            return "SETUP_STALL", new_stall
        return "RUNNING", new_stall
    if progress_scalar <= 0:
        if instance_age_min >= setup_grace_min:
            return "SETUP_STALL", new_stall
        return "RUNNING", new_stall
    if new_stall >= stall_ticks:
        return "STALLED", new_stall
    return "RUNNING", new_stall


def should_relaunch(verdict, count_today, cap):
    """Is a relaunch authorised? PURE.

    Only DIED relaunches. A STALL does NOT — a relaunch would hang the same way and pay for it again;
    a stall is a diagnosis job, not a retry job. That distinction is inherited from the GCP watchdog and it
    is the reason a stall annotation is an ::error:: rather than a silent re-dispatch.
    """
    if verdict != "DIED":
        return False, ("only a DIED entry relaunches; %s needs diagnosis, not a retry" % verdict)
    try:
        n, c = int(count_today), int(cap)
    except (TypeError, ValueError):
        return False, "unparseable relaunch counter or cap — refusing to relaunch blind"
    if n >= c:
        return False, f"relaunch cap reached ({n}/{c} today) — something is failing repeatedly"
    return True, f"attempt {n + 1}/{c} today"
