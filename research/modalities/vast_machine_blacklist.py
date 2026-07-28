#!/usr/bin/env python3
"""ONE cross-lane set of Vast machines that refuse to start — so each lane does not pay to rediscover them.

⚠ THE GAP THIS CLOSES (observed 2026-07-27 6:37 AM ET). The step 1 fan-out's 6:37 AM tick resumed its
shakeout unit onto **machine 46392** — a machine already sitting on the 5a-KS lane's "known to refuse starts"
list, alongside eight others. The fan-out's own exclusion set contained exactly one entry, `28164`. The two
lanes maintain SEPARATE blacklists and neither can see the other's.

That defeats the precise reason `ResourceSpec.exclude_machine_ids` exists: **a host that never starts has
infinite realised `$/ns`, which is invisible to `$/ns` ranking**, so without exclusion it keeps winning
selection and keeps failing. Per-lane lists mean every lane pays a rental to learn what another lane already
knows — and, worse, does so silently, because a refused start looks like ordinary spot churn.

★ WHAT IS SHARED, AND WHAT DELIBERATELY IS NOT. Only `scope="host"` exclusions cross lanes:

  * **`host`** — a property of the MACHINE, true for anybody: `resources_unavailable` on start, a container
    that never executes, a box that cannot be reached. Nothing about our workload enters the judgement, so it
    transfers without an argument.
  * **`lane`** — a property of the MACHINE *paired with this workload*: the fan-out's sustained-`gpu_util`
    shortfall against the card constant, for example. `pricing.md` A.1 WITHDREW the broad version of exactly
    that rule after a metadynamics leg's low utilisation turned out to be PLUMED's CPU-side bias, and the same
    host ran at 74 % on the very next unbiased phase. Sharing a lane-scoped verdict would re-adopt the
    withdrawn rule by the back door and discard good hosts for every other lane. So it stays local.

The cost of a false share is one host out of ~23 on a market whose floor is flat; the cost of not sharing is a
paid rental per lane per bad host. The asymmetry is why `host` shares and why the split is drawn here rather
than "share everything".

WRITES STAY WHERE THEY WERE. Each lane keeps owning its own list and its own history — this module only adds
a second, additive destination for host-scoped entries and a union on read. A failure to reach the shared set
NEVER blocks a launch: the lane falls back to exactly its previous behaviour.

⚠ KNOWN AND DELIBERATELY NOT SOLVED HERE: THE SET IS PERMANENT AND ONLY GROWS. A machine that refused a start
in July is still excluded in September even if its GPU freed up the next hour, and a union across lanes makes
that accumulate faster than a single lane's list did. Nothing here ages an entry out, because "how long is a
capacity refusal true for" is a question with no measurement behind it yet and a wrong TTL would silently
re-admit the hosts this exists to refuse. What IS done is to make the failure mode legible rather than
mysterious: `relaunch_market_gate.gate` detects "the board returned offers and none survived the filter while
N machines are excluded" and reports it as `hold_cause: exclusions_or_spec_not_price`, so an over-grown set
surfaces as itself instead of as an unaffordable market. Revisit with a measured re-test policy when the set
is large enough to matter against the ~23-host board.
"""
import json
import os
import time

# Deliberately NOT under any lane's result prefix. A shared fact stored inside one lane's tree acquires that
# lane's lifecycle — it gets archived, superseded or repointed when that lane moves on, and the other lanes
# lose it without noticing.
SHARED_KEY = os.environ.get("VAST_SHARED_BLACKLIST_KEY") or "vast-shared/_excluded_machines.json"

_WHAT = ("Vast machine_ids that FAIL TO START for anybody — capacity refusals and containers that never "
         "execute. Shared across every lane, because a host that never starts has infinite realised $/ns and "
         "is therefore invisible to $/ns ranking, so without exclusion it keeps winning selection. "
         "Lane-specific throughput judgements are NOT here: see vast_machine_blacklist.__doc__.")


def _utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load(s3, bucket, key=None):
    """(sorted machine_ids, doc) from the shared set. ([], {}) on any failure — never raises.

    An unreadable shared set must degrade to the lane's own list, not to a refusal: this is an OPTIMISATION
    (do not re-rent a known-bad host), and an optimisation that can block a launch is a liability."""
    if s3 is None or not bucket:
        return [], {}
    try:
        doc = json.loads(s3.get_object(Bucket=bucket, Key=key or SHARED_KEY)["Body"].read())
    except Exception:  # noqa: BLE001 — absent on the first ever call, and that is a legitimate state
        return [], {}
    return sorted({str(m) for m in (doc.get("machine_ids") or [])}), doc


def union(local_ids, s3=None, bucket=None, key=None):
    """The lane's own ids ∪ the shared host-scoped ids. Never raises; falls back to `local_ids`."""
    shared, _ = load(s3, bucket, key)
    return sorted({str(m) for m in (local_ids or [])} | set(shared))


def publish(s3, bucket, machine_id, why, lane, key=None):
    """Add a HOST-SCOPED machine to the shared set. Returns True if it was newly added.

    Callers pass `scope="host"` deliberately at each site; this function does not guess, because the whole
    value of the split is that somebody looked at the reason and decided it was about the machine."""
    if s3 is None or not bucket or machine_id is None:
        return False
    # ★ A CAPACITY REFUSAL IS NOT A REAL REASON FOR A PERMANENT ENTRY (trimcrae, 2026-07-27). It is the
    # class that grew this set to 48 and blocked 2 of 2 placements on a board where price was fine. The
    # caller still excludes the machine for the REST OF ITS CURRENT WAVE — that is a local decision and it
    # correctly stops one tick retrying the same busy host — but nothing about a moment goes in the shared,
    # permanent, cross-lane set.
    if classify_reason(why) == CLASS_CAPACITY:
        print(f"[blacklist] NOT publishing machine {machine_id}: {why!r} is a CAPACITY refusal — a claim "
              f"about a moment, not about the host. Excluded for this wave only.", flush=True)
        return False
    ids, doc = load(s3, bucket, key)
    mid = str(machine_id)
    if mid in ids:
        return False
    hist = list(doc.get("history") or [])
    hist.append({"machine_id": mid, "why": str(why)[:400], "lane": lane, "utc": _utcnow(),
                 "reason_class": classify_reason(why)})
    try:
        s3.put_object(Bucket=bucket, Key=key or SHARED_KEY,
                      Body=json.dumps({"_what": _WHAT, "_scope": "host — fails to start for anybody",
                                       "machine_ids": sorted(set(ids) | {mid}),
                                       "history": hist}, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[blacklist] could not publish machine {mid} to the shared set: {type(e).__name__}: {e}",
              flush=True)
        return False
    print(f"[blacklist] machine {mid} published to the SHARED cross-lane exclusion set by {lane}: {why}",
          flush=True)
    return True


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ REASON CLASSES — "don't add anything back unless you have a real reason" (trimcrae, 2026-07-27, 9:45 PM
# ET, on being shown that 48 excluded machines had blocked 2 of 2 authorised placements against a 189-offer
# board where price was fine).
#
# THE DISTINCTION THAT WAS MISSING, AND THAT GREW THE SET WITHOUT BOUND. Two very different claims were
# stored identically and kept forever:
#
#   CAPACITY  — `resources_unavailable` on start. A claim about a MOMENT: "this machine's GPU was taken at
#               8:12 PM." It is not a property of the host, it stops being true without anyone observing it,
#               and it is the class that accumulated. It is NOT a real reason for a permanent entry.
#   HOST      — the container demonstrably failed to start, crash-looped, or the image/driver is
#               incompatible. A claim that WOULD recur, about the machine itself. This is a real reason.
#
# Recording a moment as if it were a property is the whole bug: 48 permanent entries, of which the module's
# own history records at least three (53989, 31035, 24573) as provably WRONG — every one had run this repo's
# container at 94-99 % GPU.
#
# WHY THE ASYMMETRY MAKES THIS SAFE. Re-discovering a genuinely bad host is nearly free: a failed SUBMIT
# costs nothing — no rental, no billing. A host that starts and then crash-loops costs a little, and
# `vast_idle_guard` reaps it on measured write-silence within ~15 min. Against that, a wrong permanent entry
# is an unrecoverable capacity loss that compounds across lanes. Cheap to re-learn, expensive to over-exclude.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
CLASS_CAPACITY = "capacity"     # perishable — a moment, not a property. Never permanent.
CLASS_HOST = "host"             # durable — about the machine. May persist.

# Ordered: capacity is checked FIRST, because `resources_unavailable` also matches the never-started markers
# below and would otherwise be misfiled as a durable host verdict — which is precisely how it became one.
# ★ AND THE `create/start race` VERDICT IS PERISHABLE TOO — it is the one this repo has PROVEN WRONG.
# `vast_machine_blacklist`'s own history records the step 1 fan-out condemning machines 53989, 31035 and
# 24573 as "never starts" on exactly this verdict, and every one of them had demonstrably run this repo's
# container at 94-99 % GPU; the verdict flipped when an unrelated instance was reaped. A conclusion drawn
# from "cur_state=stopped with an empty status_msg across 2 checks" is about a MOMENT in the provider's
# scheduler, not about the machine — so it may bound the current wave and must not become permanent.
_CAPACITY_MARKERS = ("resources_unavailable", "no free gpu", "capacity",
                     "create/start race", "empty status_msg")


def classify_reason(why):
    """CLASS_CAPACITY or CLASS_HOST for a recorded reason. PURE.

    Default is CLASS_HOST only for reasons that positively look like start/run failures; anything
    unrecognised is also CLASS_HOST, because an unclassifiable reason is not evidence of perishability and
    silently treating it as capacity would drop an exclusion somebody meant to keep.
    """
    w = str(why or "").lower()
    if any(m in w for m in _CAPACITY_MARKERS):
        return CLASS_CAPACITY
    return CLASS_HOST


NEVER_STARTED_MARKERS = ("never started", "never executed", "never reached running",
                         "resources_unavailable", "refuse", "create/start race")


def is_never_started_reason(why):
    """Does this recorded reason say the machine FAILED TO START? PURE.

    The shared set's whole contract is "fails to start for anybody". A reason that says something else —
    a throughput shortfall, a lane-specific judgement — is not withdrawable on start evidence, because
    start evidence does not contradict it."""
    w = str(why or "").lower()
    return any(m in w for m in NEVER_STARTED_MARKERS)


def withdraw(s3, bucket, machine_id, why, lane, key=None, only_lane=True):
    """Remove a machine from the shared set because it has been OBSERVED to start. Returns True if removed.

    ⚠⚠ THE GAP THIS CLOSES, AND THE HARM THAT FORCED IT (2026-07-27, within one hour of the union going in).
    This module's own docstring flags that the set is PERMANENT AND ONLY GROWS, and parks the question of a
    re-test policy for want of a measurement. That is fine while entries are correct. It is not fine when an
    entry is WRONG: the step 1 fan-out condemned machines 53989, 31035 and 24573 as "never starts" on a
    verdict that flipped when an unrelated instance was reaped, and every one of them had demonstrably run
    that lane's container (94-99 % GPU). One tick later, 38 machines were excluded against a 152-offer board
    and **4 of 5 authorised placements failed with `no rentable verified offer`** — the exclusion set, not
    price, had become the binding constraint. An unremovable wrong entry is a permanent capacity loss.

    ★ THIS IS NOT A TTL AND IT IS NOT AN AGEING POLICY. Nothing is withdrawn because it is old — that is the
    question this module deliberately leaves open, and a guessed TTL would silently re-admit the hosts the
    set exists to refuse. A withdrawal requires POSITIVE CONTRARY EVIDENCE of exactly the claim recorded:
    the machine ran our container. "It refuses to start" is not a claim that survives having started.

    ⚠ `only_lane` (default True) restricts withdrawal to entries THIS lane published. Another lane's entry
    rests on evidence we cannot see, and overriding it from here would be the mirror of the bug above.
    """
    if s3 is None or not bucket or machine_id is None:
        return False
    ids, doc = load(s3, bucket, key)
    mid = str(machine_id)
    if mid not in ids:
        return False
    hist = list(doc.get("history") or [])
    mine = [h for h in hist if str(h.get("machine_id")) == mid]
    if only_lane and mine and not any(h.get("lane") == lane for h in mine):
        print(f"[blacklist] NOT withdrawing machine {mid}: it was published by "
              f"{sorted({h.get('lane') for h in mine})}, not by {lane}. Their evidence is not ours to "
              f"overrule.", flush=True)
        return False
    if mine and not any(is_never_started_reason(h.get("why")) for h in mine):
        print(f"[blacklist] NOT withdrawing machine {mid}: the recorded reason is not a failure-to-start "
              f"verdict, so evidence that it started does not contradict it.", flush=True)
        return False
    hist.append({"machine_id": mid, "why": f"WITHDRAWN: {why}", "lane": lane, "utc": _utcnow(),
                 "action": "withdraw"})
    try:
        s3.put_object(Bucket=bucket, Key=key or SHARED_KEY,
                      Body=json.dumps({"_what": _WHAT, "_scope": "host — fails to start for anybody",
                                       "machine_ids": sorted(set(ids) - {mid}),
                                       "history": hist}, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[blacklist] could not withdraw machine {mid}: {type(e).__name__}: {e}", flush=True)
        return False
    print(f"[blacklist] machine {mid} WITHDRAWN from the SHARED set by {lane}: {why}", flush=True)
    return True


def backfill(s3, bucket, machine_ids, lane, why=None, key=None):
    """Promote a lane's ALREADY-KNOWN host-scoped ids into the shared set. Returns the ids newly added.

    ⚠ THE GAP THIS CLOSES, and it is the one that made the union look like it worked when it did not. `union`
    and `publish` are both FORWARD-only: a lane publishes a host at the moment it observes the refusal, and
    reads the union thereafter. Neither does anything about the hosts a lane condemned BEFORE the shared set
    existed — which on 2026-07-27 was the entire population that mattered: the 5a-KS lane knew nine machines,
    the fan-out knew one, and the shared key was empty. A fan-out reading `local ∪ shared` still could not see
    machine 46392, so the exact rental the union was written to prevent would have happened again.

    ★ ONLY A LIST THAT IS HOST-SCOPED BY CONSTRUCTION MAY BE BACKFILLED. `ternary_vast_launch`'s
    `_blocked_machines` qualifies — every entry on it is a start refusal, which is a property of the machine.
    The step 1 fan-out's own exclusion file does NOT: it mixes those with the sustained-`gpu_util` verdict,
    which is a property of the machine PAIRED WITH THAT WORKLOAD and which `pricing.md` A.1 already withdrew
    the broad version of. Backfilling that one wholesale would re-adopt the withdrawn rule for every lane —
    so the caller passes the ids and owns the judgement, exactly as `publish` requires.

    Best-effort and idempotent: already-shared ids are skipped, and any failure is reported and swallowed,
    because seeding an optimisation must never be able to stop a launch."""
    added = []
    for mid in (machine_ids or []):
        if publish(s3, bucket, mid, why or f"backfilled from {lane}'s refuse-to-start list", lane, key):
            added.append(str(mid))
    return added


def clear_lane_state(s3, bucket, lane_state_key):
    """Empty one lane's OWN `_blocked_machines`. Returns the ids removed.

    Both copies must go or the set re-federates from whichever survived: `blocked_machine_ids()` unions the
    lane's local list with the shared one, so clearing only the shared set leaves the lane still excluding.
    """
    try:
        st = json.loads(s3.get_object(Bucket=bucket, Key=lane_state_key)["Body"].read())
    except Exception as e:  # noqa: BLE001 — an absent lane state is already "nothing excluded"
        print(f"[blacklist] {lane_state_key}: no lane state ({type(e).__name__}) — nothing to clear",
              flush=True)
        return []
    ids = [str(m) for m in (st.get("_blocked_machines") or [])]
    if not ids:
        print(f"[blacklist] {lane_state_key}: already empty", flush=True)
        return []
    st["_blocked_machines"] = []
    st["_blocked_machines_cleared_utc"] = _utcnow()
    s3.put_object(Bucket=bucket, Key=lane_state_key, Body=json.dumps(st, indent=2).encode())
    print(f"[blacklist] {lane_state_key}: cleared {len(ids)} machine(s)", flush=True)
    return ids


def main(argv=None):
    """Print the shared set, or snapshot-and-clear it.

      python vast_machine_blacklist.py [BUCKET]                       # print, read-only, $0
      python vast_machine_blacklist.py --snapshot PATH [--bucket B]   # write the full state to PATH
      python vast_machine_blacklist.py --clear "why" --snapshot PATH [--lane-state KEY ...]

    `--clear` REQUIRES `--snapshot`: emptying the set without first recording it destroys the only evidence
    of what was excluded and why.
    """
    import argparse
    ap = argparse.ArgumentParser(description="Shared Vast machine-exclusion set")
    ap.add_argument("bucket", nargs="?", default=None)
    ap.add_argument("--bucket", dest="bucket_opt", default=None)
    ap.add_argument("--snapshot", default=None, help="write the full current state here before any change")
    ap.add_argument("--clear", default=None, metavar="WHY", help="empty the shared set, recording WHY")
    ap.add_argument("--lane-state", action="append", default=None, metavar="KEY",
                    help="also clear this lane's own `_blocked_machines` (repeatable)")
    a = ap.parse_args([] if argv is None else argv)
    bucket = a.bucket_opt or a.bucket or (os.environ.get("VAST_CKPT_BUCKET")
                                          or "sagemaker-us-east-2-646605541856")
    import boto3
    s3 = boto3.client("s3")

    if a.clear and not a.snapshot:
        print("::error::--clear requires --snapshot: never delete state you have not first written down")
        return 2

    if a.snapshot:
        snap = snapshot(s3, bucket)
        with open(a.snapshot, "w") as fh:
            json.dump(snap, fh, indent=2)
            fh.write("\n")
        print(f"[blacklist] snapshot -> {a.snapshot}: {snap['n_machine_ids']} machine(s), "
              f"by reason class {snap['history_entries_by_reason_class']}")

    if a.clear:
        removed = clear_all(s3, bucket, a.clear)
        for k in (a.lane_state or []):
            removed += clear_lane_state(s3, bucket, k)
        print(f"[blacklist] TOTAL cleared: {len(removed)} entr(ies)")
        ids_after, _ = load(s3, bucket)
        print(f"[blacklist] shared set now holds {len(ids_after)} machine(s)")
        return 0

    ids, doc = load(s3, bucket)
    print(json.dumps({"bucket": bucket, "key": SHARED_KEY, "machine_ids": ids,
                      "history": doc.get("history") or []}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def snapshot(s3, bucket, key=None):
    """The FULL current shared state, for committing before a clear. Read-only.

    Clearing without a record would destroy the only evidence of what was excluded and why — which is also
    the input to any later question about whether clearing was right. Never delete state you have not first
    written down somewhere durable.
    """
    ids, doc = load(s3, bucket, key)
    hist = list(doc.get("history") or [])
    by_class = {}
    for h in hist:
        c = h.get("reason_class") or classify_reason(h.get("why"))
        by_class[c] = by_class.get(c, 0) + 1
    return {
        "_what": "Full shared Vast machine-exclusion state, captured immediately before a deliberate clear.",
        "utc": _utcnow(),
        "bucket": bucket, "key": key or SHARED_KEY,
        "n_machine_ids": len(ids), "machine_ids": ids,
        "history_entries_by_reason_class": by_class,
        "history": hist,
    }


def clear_all(s3, bucket, why, lane="operator", key=None):
    """Empty the shared exclusion set, keeping the history as an audit trail. Returns the ids removed.

    The clear is itself appended to `history`, so the record shows an EVENT rather than a gap — a set that
    silently became empty is indistinguishable from one that was never written.
    """
    ids, doc = load(s3, bucket, key)
    hist = list(doc.get("history") or [])
    hist.append({"machine_id": None, "why": f"CLEARED {len(ids)} machine(s): {why}", "lane": lane,
                 "utc": _utcnow(), "reason_class": "clear", "cleared_machine_ids": ids})
    s3.put_object(Bucket=bucket, Key=key or SHARED_KEY,
                  Body=json.dumps({"_what": _WHAT, "_scope": "host — fails to start for anybody",
                                   "machine_ids": [], "history": hist}, indent=2).encode())
    print(f"[blacklist] CLEARED {len(ids)} machine(s) from the shared set: {why}", flush=True)
    return ids
