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
    ids, doc = load(s3, bucket, key)
    mid = str(machine_id)
    if mid in ids:
        return False
    hist = list(doc.get("history") or [])
    hist.append({"machine_id": mid, "why": str(why)[:400], "lane": lane, "utc": _utcnow()})
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


def main(argv=None):
    """`python vast_machine_blacklist.py [BUCKET]` — print the shared set. Read-only, $0."""
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    bucket = argv[0] if argv else (os.environ.get("VAST_CKPT_BUCKET")
                                   or "sagemaker-us-east-2-646605541856")
    import boto3
    ids, doc = load(boto3.client("s3"), bucket)
    print(json.dumps({"bucket": bucket, "key": SHARED_KEY, "machine_ids": ids,
                      "history": doc.get("history") or []}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
