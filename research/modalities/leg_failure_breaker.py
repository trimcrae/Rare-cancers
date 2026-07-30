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

★★ AND A UNIT WE EVICTED IS NOT A UNIT THAT FAILED (measured 2026-07-29, and it cost the r2 replicate a
permanent block). The count above answers "has this unit failed repeatedly?" by reading a `status=failed`
record and an attempt archive. Neither of those can tell whether the record is still the LAST WORD on the
unit — and on 2026-07-29 it was not. `calib_hi_to_lo__ternary_vhl_r2_dt4.0fs_wu1.0_edge_reps`:

  * was ADVANCING on its host (committed census warmup/384 -> warmup/576, log uploaded until 12:33 UTC);
  * at 12:37 UTC `collect` destroyed that host on `⛔ DESTROYED this pass (capacity refusal on machine
    29711; destroy: a qualifying replacement is on the board)` — a correct teardown under the conditional-
    teardown ruling, taken because the MARKET refused the host, not because the unit did anything wrong;
  * still carried a `status=failed` `leg.json` written by an EARLIER attempt. That the record was earlier is
    not an inference: `collect` only reaches its capacity-refusal branch when `crashed` is False, and
    `crashed` is `status == "failed" AND _record_is_newer_than_instance(record, instance)` — so the branch
    that destroyed the box had already established that the record predates the host it destroyed.

The breaker then read `status=failed` + 51 archived attempts and blocked the unit forever. The conditional
teardown had quietly become a poisoner: every unit it correctly evicted accrued a permanent block.

THE DISCRIMINATOR, AND WHY THE OTHER THREE ARE WORSE. The honest question is not "did it fail?" nor "has it
made progress?" but **"is the `failed` record still the NEWEST fact about this unit?"** Exactly two things
supersede it, and each is a timestamped, durable, unit-level fact:

  1. **A COMMIT WRITTEN AFTER IT.** The commit store is the only durable evidence that the SCIENCE advanced,
     and an object written after the record proves the unit ran, and worked, since that record was filed.
  2. **AN EVICTION WE RECORDED.** `record_eviction` is written by the teardown itself, which is the only
     place that knows the host was taken for a capacity refusal rather than surrendered by a dying leg.
     It covers the case (1) cannot: a unit evicted during staging, before it could commit anything.

REJECTED, with the counterexample that rejects each:
  * **`committed > 0`** — the VALUE of the high-water mark carries no recency. Units genuinely dying at
    `proto.create` presented `committed=warmup/832` inherited from an older attempt. Known-bad; never use it.
  * **The phase marker (`phase.txt`) being fresh.** It is rewritten by EVERY attempt on its way in —
    `start`/`cloned`/`staging` — i.e. BEFORE the attempt dies. A container that crash-loops never returns, so
    it never writes a `leg.json` at all (CLAUDE.md §6), and its phase marker would then be permanently newer
    than the last failed record. That turns the discriminator true on every tick and restores the exact loop
    the breaker exists to break — the 84 rentals burned on `proto.create` deaths. It is the most dangerous
    candidate precisely because it LOOKS right in a diagnostic (r2's marker was 78 min old and plausible).
  * **`run.log` mtime.** The on-host sync loop pushes the log every ~2 min whether or not the science
    advances. That is liveness, not progress, and the same crash-loop argument applies.

WHAT THIS DOES NOT WEAKEN. A unit dying at `proto.create` writes its `leg.json` as the LAST act of the
attempt, commits nothing, and is destroyed on `unit FAILED — nothing left to produce` (never the capacity
branch, which is unreachable once `crashed` is True). So no commit and no eviction is newer than its record,
and it stays blocked. The protection is intact; only the eviction case is carved out.

SELF-LIMITING BY CONSTRUCTION. Superseding evidence buys exactly one more rental: if that rental dies and
writes a fresh `status=failed`, the record is once again the newest fact and the block re-applies at the same
count. Nothing is reset, no strike is forgiven, and `reset_for` remains the only way to clear the archive.
"""
from __future__ import annotations

import calendar
import time

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
ALLOW_SUPERSEDED = "allow: the failed record is no longer the newest fact about this unit"

# The two kinds of fact that can supersede a `status=failed` record. Named constants because they are
# written into the readout, the receipt and the diagnostic, and a typo'd kind is a silently unmatchable row.
KIND_COMMIT = "commit-after-record"
KIND_EVICTION = "evicted-after-record"

_TS = "%Y-%m-%dT%H:%M:%SZ"


def _epoch(stamp):
    """UTC ISO stamp -> epoch seconds, or None if absent/unparseable. PURE.

    None is the "we could not tell" answer, and every caller here treats it as NOT superseding — i.e. an
    unreadable timestamp leaves the block in place. That is the opposite direction to `count_attempts`'s
    fail-OPEN, and deliberately: failing open on the COUNT costs one rental, while failing open on
    SUPERSESSION would re-open the loop that burned 84.
    """
    if not stamp:
        return None
    try:
        return calendar.timegm(time.strptime(str(stamp), _TS))
    except (ValueError, TypeError):
        return None


def record_epoch(record):
    """When this `leg.json` was filed. PURE. `updated_utc` first, S3's own mtime as the fallback.

    The record's own stamp is preferred because it is written by the host at the moment of the verdict; the
    S3 mtime is a fallback for records written before that field existed. Both are UTC.
    """
    r = record or {}
    return _epoch(r.get("updated_utc")) or _epoch(r.get("started_utc")) or _epoch(r.get("_s3_last_modified"))


def record_predates_host(record, instance_start_epoch):
    """Was this `leg.json` filed BEFORE the host in front of us started? True / False / None (cannot tell).

    PURE. Three-valued on purpose: `protfep_vast_launch._record_is_newer_than_instance` collapses "older"
    and "unreadable" both to False, which is right for a teardown decision (do not reap on a guess) and
    WRONG for deciding whether to stamp an eviction — a unit whose record we cannot date must not be
    credited with an eviction it may not have had. Only an explicit True authorises that write.
    """
    rec = record_epoch(record)
    try:
        start = float(instance_start_epoch)
    except (TypeError, ValueError):
        return None
    if rec is None:
        return None
    return rec < start


def superseding_evidence(record, *, newest_commit_utc=None, eviction=None):
    """The newest durable fact about this unit that POSTDATES its failed record, or None. PURE.

    See the module docstring for why these two facts and no others. Both are compared by TIMESTAMP against
    the record; neither is trusted on its existence alone, which is what makes a stale eviction receipt or a
    frozen commit high-water mark harmless here.
    """
    at = record_epoch(record)
    if at is None:
        # We cannot date the record, so we cannot show anything is newer than it. Leave the block standing.
        return None
    best = None
    for kind, stamp, detail in (
            (KIND_COMMIT, newest_commit_utc, "the commit store advanced after the failed record was filed, "
                                             "so the unit ran and did real work since that record"),
            (KIND_EVICTION, (eviction or {}).get("utc"),
             "we destroyed this unit's host ourselves after the failed record was filed — "
             + str((eviction or {}).get("why") or "capacity refusal")),
    ):
        e = _epoch(stamp)
        if e is None or e <= at:
            continue
        if best is None or e > best["_epoch"]:
            best = {"kind": kind, "utc": stamp, "detail": detail, "_epoch": e,
                    "record_utc": time.strftime(_TS, time.gmtime(at))}
    if best is not None:
        best.pop("_epoch")
    return best


def decide(record, n_attempts, threshold=DEFAULT_THRESHOLD, superseding=None):
    """Should we rent a host for this unit? PURE — no I/O, no clock.

    `record` is the unit's `leg.json` (or None if it has never written one); `n_attempts` is the measured
    count of archived attempts; `superseding` is `superseding_evidence(...)`'s answer — the newest durable
    fact that POSTDATES the record, or None. Returns a dict carrying the verdict AND the evidence, because a
    block that cannot explain itself is indistinguishable from a lane that quietly stopped.

    ⚠ `superseding` NEVER LOWERS THE COUNT and never clears the archive. It answers a different question —
    "is that record still the last word?" — so a unit whose evidence goes stale blocks again at the same
    count on the very next tick. Forgiving a strike would be a real weakening; this is not one.
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
        # ★ THE ONE CARVE-OUT. Everything above is about WHAT the record says; this is about WHETHER it is
        # still current. A unit we evicted, or one that committed real work after the record was filed, is
        # not a unit sitting still under a reproducing fault.
        if superseding:
            verdict, block = ALLOW_SUPERSEDED, False
        else:
            verdict, block = BLOCK, True
    else:
        verdict, block = ALLOW_UNDER, False

    out = {"block": block, "verdict": verdict, "n_attempts": n_attempts, "threshold": threshold,
           "status": status}
    if superseding:
        out["superseded_by"] = superseding
    if block:
        out["why"] = (
            "this unit has failed on %d separate rented hosts (threshold %d) with no intervening success. "
            "The last record is status=failed at phase %r (rc=%s), and NOTHING durable has been written "
            "since it — no commit, and no eviction of ours. Buying another host tests nothing — the "
            "repetition across distinct hosts is what makes this a code/data fault rather than a bad "
            "machine. NOT permanent: fix the cause, then clear the attempt archive "
            "(leg_failure_breaker.reset_for) or supersede the failed record, and the next tick rents "
            "normally."
            % (n_attempts, threshold, (record or {}).get("phase"), (record or {}).get("rc")))
    elif verdict == ALLOW_SUPERSEDED:
        out["why"] = (
            "this unit carries status=failed and %s archived attempts, which WOULD block it (threshold %d) "
            "— but that record is no longer the newest fact about the unit: %s (%s at %s, record filed %s). "
            "We are renting because the failure is not the thing that stopped it. The strike count is "
            "UNCHANGED: if the next attempt files a fresh status=failed, this unit blocks again at the same "
            "count."
            % (n_attempts, threshold, superseding.get("detail"), superseding.get("kind"),
               superseding.get("utc"), superseding.get("record_utc")))
    return out


def count_attempts(s3, bucket, prefix, unit_id, since_utc=None):
    """How many archived attempts this unit has SINCE `since_utc`. Measured from S3, never remembered.

    ★★ `since_utc` EXISTS BECAUSE A LIFETIME COUNT IS NOT A FAILURE STREAK, AND THE DIFFERENCE BLOCKED A LEG
    THAT WAS 88 % DONE (measured 2026-07-30, 10:13 PM ET).

    WHAT HAPPENED. `calib_hi_to_lo__ternary_vhl_r2` — valB r2 — committed production/1760 of 2000 at
    02:05:13Z and its host aborted (rc=134) three seconds later at 02:05:16Z. The breaker refused to re-rent
    it, at `n_attempts=55` against a threshold of 3, and said:

        this unit has failed on 55 separate rented hosts (threshold 3) with no intervening success ...
        Buying another host tests nothing — the repetition across distinct hosts is what makes this a
        code/data fault rather than a bad machine.

    Both halves of that were false for this unit. There WAS an intervening success — hours of it, from
    warmup through 1760 production iterations. And the 55 are not repetitions of one fault: the archive
    holds the since-FIXED partial-charge defect (`attempts[26]`: *"ValueError: Some atoms in rdmol have
    partial charges, but others do not"*), which is precisely why later attempts got so much further.
    Buying another host would have tested a great deal — it resumes at 1760 and either finishes in 240
    iterations or reproduces the abort at a known point, which is the decisive experiment.

    THE CAUSE, stated exactly: this function counted every object under `attempts/` for all time, so the
    number it returns is "how many attempts has this unit EVER had", while `decide` reads it as "how many
    times has it failed in a row". Those agree only until a unit first succeeds. After that they diverge
    permanently, and a unit that has ever accumulated `threshold` attempts can never be retried again no
    matter how much work it completes in between — the breaker becomes a one-way latch.

    THE FIX IS A DIFFERENT DENOMINATOR, NOT A WEAKER RULE. An attempt archived BEFORE the newest commit
    cannot be part of the current failure streak: work landed after it, so whatever it failed at was
    survived. Counting only attempts newer than the last commit yields the consecutive-failure count
    `decide` always meant to read. The protection is untouched where it matters — a unit that genuinely
    aborts at the same place still reaches `threshold` consecutive post-commit failures and still blocks.

    `since_utc=None` preserves the old lifetime behaviour for a unit that has never committed anything,
    which is the case the breaker was originally written for and where the two counts coincide.

    Returns None when the listing fails — and `decide` treats None as "not over the threshold", i.e. it FAILS
    OPEN. That is the right direction here: an unreadable bucket must not be able to halt a lane, and the
    worst case is one more rental, whereas failing closed on a transient listing error could stall everything.
    (This is the opposite of the market gate's fail-CLOSED rule, and deliberately so: there, guessing wrong
    SPENDS money blind; here, guessing wrong merely fails to prevent one purchase.)
    """
    p = (prefix or "").rstrip("/")
    cutoff = _epoch(since_utc)
    try:
        n = 0
        for page in s3.get_paginator("list_objects_v2").paginate(
                Bucket=bucket, Prefix=f"{p}/legs/{unit_id}/attempts/"):
            for o in page.get("Contents", []) or []:
                if cutoff is None:
                    n += 1
                    continue
                lm = o.get("LastModified")
                # An attempt we cannot date is COUNTED. The streak is the thing that blocks a rental, and
                # silently dropping an undateable attempt would shorten it — i.e. guess in the direction of
                # buying another host. Undateable is rare; buying blind on a real fault is what costs.
                if lm is None or lm.timestamp() > cutoff:
                    n += 1
        return n
    except Exception as e:  # noqa: BLE001 — reported, never swallowed into a silent zero
        print(f"[breaker] could not count attempts for {unit_id}: {type(e).__name__}: {e}")
        return None


def newest_commit_utc(s3, bucket, prefix, unit_id):
    """When this unit last committed anything, as a UTC ISO stamp. None if it never has, or on a read error.

    ★ THE MTIME, NOT THE ITERATION NUMBER. `committed_progress` answers "how far did it get" and its answer
    is a high-water mark that survives every attempt — which is exactly why the VALUE is useless here (a unit
    dying at `proto.create` showed `warmup/832` inherited from an older attempt). The newest object's
    LastModified answers the different question this module needs: WHEN did work last land.

    None on failure, which `superseding_evidence` treats as "nothing supersedes the record" — i.e. the block
    stands. Deliberately the fail-CLOSED direction, opposite to `count_attempts`: see `_epoch`.
    """
    p = (prefix or "").rstrip("/")
    newest = None
    try:
        for page in s3.get_paginator("list_objects_v2").paginate(
                Bucket=bucket, Prefix=f"{p}/commits/{unit_id}/"):
            for o in page.get("Contents", []) or []:
                lm = o.get("LastModified")
                if lm is not None and (newest is None or lm > newest):
                    newest = lm
    except Exception as e:  # noqa: BLE001 — reported, never swallowed into a fabricated "yes it advanced"
        print(f"[breaker] could not date the commit store for {unit_id}: {type(e).__name__}: {e}")
        return None
    return newest.strftime(_TS) if newest is not None else None


def eviction_key(prefix, unit_id):
    """Where a unit's eviction receipt lives. One home for the key, so the writer and the reader cannot drift."""
    return f"{(prefix or '').rstrip('/')}/legs/{unit_id}/_evicted.json"


def read_eviction(s3, bucket, prefix, unit_id):
    """The last time WE took this unit's host away, and why. None if we never have (or on a read error)."""
    try:
        import json as _json
        return _json.loads(s3.get_object(Bucket=bucket, Key=eviction_key(prefix, unit_id))["Body"].read())
    except Exception:  # noqa: BLE001 — absent is the normal case, not an error worth printing every tick
        return None


def record_eviction(s3, bucket, prefix, unit_id, *, why, instance=None, machine_id=None, utc=None):
    """Write the receipt that says WE ended this unit's attempt, so the breaker does not read it as a failure.

    ⛔ THE CALLER MUST HAVE ESTABLISHED THAT THE UNIT DID NOT DIE ON THIS HOST. This function records a
    claim; it cannot check one. The teardown is the only place that knows — it reaches its capacity-refusal
    branch only when `crashed` is False — and it must additionally confirm `record_predates_host(...) is
    True` before calling, so a unit whose record cannot be dated is never credited with an eviction. Getting
    that wrong would hand a genuinely-dying unit a fresh rental every tick, which is the 84-rental loop.

    Overwrites rather than appends: only the MOST RECENT eviction can supersede a record, and a history here
    would be a second, drifting copy of the attempt archive.
    """
    import json as _json
    doc = {"_what": "the last time this lane destroyed this unit's host for a reason that was NOT the unit "
                    "failing — read by leg_failure_breaker so a correct teardown does not accrue a strike",
           "unit_id": unit_id, "utc": utc or time.strftime(_TS, time.gmtime()),
           "why": why, "instance": instance, "machine_id": machine_id}
    s3.put_object(Bucket=bucket, Key=eviction_key(prefix, unit_id),
                  Body=_json.dumps(doc, indent=2).encode())
    return doc


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
    meaning).

    ★ AND A BLOCK WE LIFTED MUST NOT RENDER LIKE A BLOCK WE APPLIED. Renting a unit that carries 51 strikes
    is a decision, not a non-event: if it printed nothing, "the breaker never fired" and "the breaker fired
    and was overridden by evidence" would be the same silence — the same complaint §1 makes about a refused
    row and a paid row sharing a glyph. `↻` is unused elsewhere in this repo, so it means this and nothing
    else.
    """
    if d.get("verdict") == ALLOW_SUPERSEDED:
        s = d.get("superseded_by") or {}
        return ("    -> ↻ RE-PLACING %s — its %s-strike block is SUPERSEDED by %s at %s (record filed %s); "
                "the strike count is unchanged. %s"
                % (unit_id, d.get("n_attempts"), s.get("kind"), s.get("utc"), s.get("record_utc"),
                   d.get("why", "")))
    return ("    -> ⛔ NOT RENTING %s — %d consecutive failed hosts (threshold %d), $0 spent this tick. %s"
            % (unit_id, d.get("n_attempts") or 0, d.get("threshold"), d.get("why", "")))
