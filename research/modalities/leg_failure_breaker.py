#!/usr/bin/env python3
"""Stop renting a host for a unit that has failed on the last N hosts in a row.

★ THE LOOP THIS CLOSES, measured 2026-07-29. `calib_hi_to_lo__ternary_vhl` r1 and r2 and all four
closure-triangle legs have been dying at `rc=1` in WARMUP, on host after host, since 2026-07-28. r2 died at
`warmup/320` on 2026-07-28 and again at `warmup/320` on 2026-07-29 — the same phase, on the same machine
(28164) — while the market gate cleared and re-rented on the 3:43 AM and 6:47 AM ET ticks. Each cycle buys a
GPU, dies within minutes, records `status=failed`, and is destroyed; the next tick buys another.

WHY NOTHING ALREADY STOPPED IT, and why the obvious fix is wrong. There IS a brake — the GCP watchdog refuses
to relaunch a unit carrying a failed record — but it guards the WATCHDOG path, not the market-gate/autoscale
path, and it is the market gate that has been buying. The on-host idempotency check deliberately does NOT
block on a failed record, and that decision is correct and must not be reverted: `run_ternary_leg.sh` says so
in as many words, because testing only for EXISTENCE meant that once a leg had failed, every re-dispatch after
the fix rented a host that exited "nothing to do" and reported green. **A failed record must never
permanently block its own retry** — otherwise no fix could ever be validated.

So the discriminator cannot be "has it failed?". It has to be "has it failed REPEATEDLY, with nothing having
changed?" — which is what a consecutive-failure count measures and a single record cannot. One failure is a
spot preemption, a bad host, a transient. Three in a row on three different hosts is a fault in the code or
the data, and buying a fourth host tests nothing.

WHERE THE COUNT COMES FROM — measured, not remembered. Every attempt archives its `run.log` under the unit's
`attempts/` prefix in S3 before the next one starts. That archive IS the count of times we have paid to run
this unit, it is written by the host rather than by any bookkeeping this module controls, and it survives
every restart. No new state file, and nothing to drift.

WHAT THIS IS NOT. It is not "silently dropping units" (CLAUDE.md §6 forbids that): a blocked unit is returned
to the caller with its count and its reason so the readout can show it, exactly like a price hold. It is not
permanent either — `reset_for(unit)` clears the archive once the cause is fixed, which is the same gesture
`supersede_failed_record` already provides for the record itself, and a `done` record clears it implicitly
because a done unit is never in `needed`.

IT DOES NOT TOUCH RUNNING WORK. Like the relaunch market gate, this acts only at the moment of RENTING.
"""
from __future__ import annotations

# Three, not two. One failure is noise (preemption, a bad host, a transient pull). Two on two hosts is
# suggestive but a single unlucky machine can still produce it — machine 28164 served two of these deaths.
# Three separate purchases that all died is no longer a story about hosts, and the fourth purchase buys no
# information. Deliberately NOT tunable per lane: a per-lane override is how a breaker gets quietly raised
# until it never trips.
DEFAULT_THRESHOLD = 3

BLOCK = "blocked: repeated failure on distinct hosts"
ALLOW_NO_RECORD = "allow: no leg record — a unit that has never run must be able to run"
ALLOW_DONE = "allow: the unit is done"
ALLOW_UNDER = "allow: failures so far are under the threshold"


def decide(record, n_attempts, threshold=DEFAULT_THRESHOLD):
    """Should we rent a host for this unit? PURE — no I/O, no clock.

    `record` is the unit's `leg.json` (or None if it has never written one); `n_attempts` is the measured
    count of archived attempts. Returns a dict carrying the verdict AND the evidence, because a block that
    cannot explain itself is indistinguishable from a lane that quietly stopped.
    """
    status = (record or {}).get("status")
    if record is None:
        verdict, block = ALLOW_NO_RECORD, False
    elif status == "done":
        verdict, block = ALLOW_DONE, False
    elif status != "failed":
        # Anything else (running, or a shape we do not recognise) is NOT evidence of a fault. Fail OPEN here
        # on purpose: this module exists to stop waste, and refusing to rent on an unrecognised status would
        # let one schema change silently halt the whole lane.
        verdict, block = ALLOW_UNDER, False
    elif n_attempts is not None and n_attempts >= threshold:
        verdict, block = BLOCK, True
    else:
        verdict, block = ALLOW_UNDER, False

    out = {"block": block, "verdict": verdict, "n_attempts": n_attempts, "threshold": threshold,
           "status": status}
    if block:
        out["why"] = (
            "this unit has failed on %d separate rented hosts (threshold %d) with no intervening success. "
            "The last record is status=failed at phase %r (rc=%s). Buying another host tests nothing — the "
            "repetition across distinct hosts is what makes this a code/data fault rather than a bad machine. "
            "NOT permanent: fix the cause, then clear the attempt archive (leg_failure_breaker.reset_for) or "
            "supersede the failed record, and the next tick rents normally."
            % (n_attempts, threshold, (record or {}).get("phase"), (record or {}).get("rc")))
    return out


def count_attempts(s3, bucket, prefix, unit_id):
    """How many archived attempts this unit has. Measured from S3, never remembered.

    Returns None when the listing fails — and `decide` treats None as "not over the threshold", i.e. it FAILS
    OPEN. That is the right direction here: an unreadable bucket must not be able to halt a lane, and the
    worst case is one more rental, whereas failing closed on a transient listing error could stall everything.
    (This is the opposite of the market gate's fail-CLOSED rule, and deliberately so: there, guessing wrong
    SPENDS money blind; here, guessing wrong merely fails to prevent one purchase.)
    """
    p = (prefix or "").rstrip("/")
    try:
        n = 0
        for page in s3.get_paginator("list_objects_v2").paginate(
                Bucket=bucket, Prefix=f"{p}/legs/{unit_id}/attempts/"):
            n += len(page.get("Contents", []) or [])
        return n
    except Exception as e:  # noqa: BLE001 — reported, never swallowed into a silent zero
        print(f"[breaker] could not count attempts for {unit_id}: {type(e).__name__}: {e}")
        return None


def reset_for(s3, bucket, prefix, unit_id):
    """Clear a unit's attempt archive so the breaker re-arms from zero. Call AFTER fixing the cause.

    Returns the number of objects deleted. Deliberately a separate, explicit gesture rather than something
    any tick can do: a breaker that resets itself is not a breaker.
    """
    p = (prefix or "").rstrip("/")
    keys = []
    for page in s3.get_paginator("list_objects_v2").paginate(
            Bucket=bucket, Prefix=f"{p}/legs/{unit_id}/attempts/"):
        keys.extend([{"Key": o["Key"]} for o in page.get("Contents", []) or []])
    for i in range(0, len(keys), 1000):
        s3.delete_objects(Bucket=bucket, Delete={"Objects": keys[i:i + 1000]})
    return len(keys)


def render(unit_id, d):
    """One operator line. A blocked unit must never render like a price hold — the money is not the point
    here, the repetition is — so it gets its own glyph and names the count (CLAUDE.md §1, one glyph one
    meaning)."""
    return ("    -> ⛔ NOT RENTING %s — %d consecutive failed hosts (threshold %d), $0 spent this tick. %s"
            % (unit_id, d.get("n_attempts") or 0, d.get("threshold"), d.get("why", "")))
