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

★★ WHAT MAY PERSIST, AND WHAT MAY ONLY BOUND THE CURRENT WAVE (trimcrae, 2026-07-27: *"Clear out our
blacklist then and don't add anything back unless you have a real reason to."*). This is now enforced on
every route into every set, not just on the one that goes through `publish`:

  * A **`CLASS_HOST`** verdict — the container demonstrably failed to start, crash-looped, the image/driver
    is incompatible — is durable and may be stored permanently and shared.
  * A **`CLASS_CAPACITY`** refusal is a claim about a MOMENT. It bounds the CURRENT WAVE and is then
    forgotten. `publish` refuses it; `backfill` can no longer launder it (it must be given the ORIGINAL
    reason, so the classifier sees the real evidence); `ternary_vast_launch` writes its `_blocked_machines`
    wave-scoped rather than cumulatively; and `congeneric_fanout_vast._record_exclusion` keeps its capacity
    refusals in a run-scoped `capacity_wave` block that a later run does not read.

  Re-testing is what makes that safe and nearly free: a failed SUBMIT costs no rental and no billing, and a
  box that starts and then crash-loops is reaped by `vast_idle_guard` on measured write-silence within
  ~15 min. Cheap to re-learn, expensive to over-exclude.

⚠ STILL DELIBERATELY NOT SOLVED HERE: A **HOST-SCOPED** ENTRY IS PERMANENT AND NOTHING AGES IT OUT, because
"how long is a host verdict true for" has no measurement behind it and a guessed TTL would silently re-admit
the hosts this exists to refuse. The two things that do bound it are `withdraw` (positive contrary evidence:
we watched the machine run our container) and a deliberate operator `--clear`. What is also done is to make
the failure mode legible rather than mysterious: `relaunch_market_gate.gate` and
`congeneric_fanout_vast`'s placement record both detect "the board returned offers and none survived the
filter while N machines are excluded" and report it as `hold_cause: exclusions_or_spec_not_price`, so an
over-grown set surfaces as itself instead of as an unaffordable market.

SUPERSEDED, RETAINED: this docstring used to say *"THE SET IS PERMANENT AND ONLY GROWS"* of the whole set.
That was true of both classes when written, and it is what let 32 perishable refusals become permanent
cross-lane entries — 78 % of the 41 in `vast-blacklist-snapshot-before-clear.json`.
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


# A sentinel, not `None`: `backfill(..., why=None)` used to be legal and silently synthesised a reason, so
# `None` must stay distinguishable from "not passed" while that call shape is still out there in old branches.
_REQUIRED = object()

# ★ THE TWO DOC SHAPES A LANE'S OWN EXCLUSION LIST COMES IN, and knowing only one of them is what let the
# 2026-07-27 clear miss the list that mattered. `ternary_vast_launch` / `protfep_vast_launch` keep theirs at
# `{prefix}/_lane_state.json` under `_blocked_machines`; `congeneric_fanout_vast` keeps its own at
# `{prefix}/_excluded_machines.json` under `machine_ids`. The clear was pointed at
# `nr4a3-step1-fanout/results/_lane_state.json` — a key the fan-out has never written — so it reported
# success against a file that does not exist while the fan-out's real 41-machine list was untouched, and the
# very next tick filtered all 41 again. `clear_lane_state` now clears whichever field the doc actually has.
_LANE_LIST_FIELDS = ("_blocked_machines", "machine_ids")


# =============================================================================================================
# ⛔⛔ THE DURABLE EXCLUSION LIST IS RETIRED — OFF BY DEFAULT, AT THE READ PATH
#     (trimcrae, 2026-07-31: *"You've gotta just stop doing the blacklist. It seems like it only ever bites us
#     in the ass and clearing it always makes things better."*)
# =============================================================================================================
# THE EVIDENCE, so this is recorded rather than asserted:
#   * The cumulative version reached **33 lane-local + 41 shared** entries and made OUR OWN FILTER, not price,
#     the binding constraint on placement — 2 of 2 authorised units failed with `no rentable verified offer`
#     against a 189-offer board at healthy prices.
#   * `vast-blacklist-snapshot-before-clear.json` captured **41 machine ids** immediately before the
#     deliberate wipe of 2026-07-28, of which 32 were a single synthesised backfill reason.
#   * Every clear on record improved placement. Nothing on record shows the list paying for itself.
#
# THE COUNTER-ARGUMENT THIS FILE WAS BUILT ON — "a host that never starts has infinite realised $/ns, which is
# invisible to $/ns ranking, so without exclusion it keeps winning selection and keeps failing" — is REAL, and
# it is fully served by the IN-CALL retry skip in `gpu_backend.VastBackend.submit`: after a
# `resources_unavailable`, that call widens `exclude_machine_ids` on a COPY of the spec and re-selects, so the
# refusing machine cannot win again inside the placement that just met it. That skip is bounded to the call and
# dies with it. What has repeatedly starved the board is the DURABLE list, not the bounded one.
#
# ⚠ WHAT IS DELIBERATELY UNTOUCHED, because removing it would cause real harm:
#   * `used_machines` (`congeneric_fanout_vast`, `protfep_vast_launch`, `ternary_vast_launch`) — do not put two
#     legs of the same wave on one box. That is DOUBLE-RENT prevention, not exclusion.
#   * the in-call retry skip described above (`gpu_backend`).
#   * per-dispatch operator env hatches (`FANOUT_EXCLUDE_MACHINES`, `BENCH_EXCLUDE_MACHINES`) — explicit input
#     for one run, which nothing persists and nothing re-reads.
#
# ⚠ AND WHY THIS IS A SWITCH RATHER THAN A DELETION. No S3 object is deleted and no history is dropped: the
# writers stop, the readers return nothing, and `snapshot`/`lane_list_report`/`vast_exclusion_census` still
# read the stored artifact so the record and the census tooling stay legible. Setting
# `VAST_DURABLE_EXCLUSIONS=1` restores the previous behaviour exactly, which is what makes this reversible
# without an archaeology exercise if the evidence ever changes.
DURABLE_EXCLUSIONS_ENABLED = False        # the DEFAULT, and the one home of the decision

def durable_enabled():
    """Whether the durable exclusion list may be read or written, consulted AT CALL TIME.

    A function rather than a module constant because the constant would freeze at import, and the tests that
    pin the retired machinery (so it still works if the evidence ever changes) must be able to turn it on
    without reloading half the package. Env absent => the default above, i.e. OFF."""
    v = os.environ.get("VAST_DURABLE_EXCLUSIONS")
    if v is None:
        return DURABLE_EXCLUSIONS_ENABLED
    return str(v).strip().lower() in ("1", "true", "yes", "on")

_RETIRED_NOTE = ("the durable machine-exclusion list is RETIRED (trimcrae, 2026-07-31) — reads return nothing "
                 "and writes are refused; set VAST_DURABLE_EXCLUSIONS=1 to restore. Bounded protection is "
                 "unchanged: the in-call capacity-refusal skip in gpu_backend.submit, and used_machines.")


def _utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load(s3, bucket, key=None, force=False):
    """(sorted machine_ids, doc) from the shared set. ([], {}) on any failure — never raises.

    ⛔ RETURNS NO IDS WHILE THE DURABLE LIST IS RETIRED (see the block above). `force=True` reads the stored
    object anyway and is for the REPORTING paths only — `snapshot`, the exclusion census, the operator
    clear/retire commands — so the historical artifact stays readable while nothing consumes it for selection.

    An unreadable shared set must degrade to the lane's own list, not to a refusal: this is an OPTIMISATION
    (do not re-rent a known-bad host), and an optimisation that can block a launch is a liability."""
    if s3 is None or not bucket:
        return [], {}
    if not (force or durable_enabled()):
        return [], {}
    try:
        doc = json.loads(s3.get_object(Bucket=bucket, Key=key or SHARED_KEY)["Body"].read())
    except Exception:  # noqa: BLE001 — absent on the first ever call, and that is a legitimate state
        return [], {}
    return sorted({str(m) for m in (doc.get("machine_ids") or [])}), doc


def union(local_ids, s3=None, bucket=None, key=None):
    """The lane's own ids ∪ the shared host-scoped ids. Never raises; falls back to `local_ids`.

    ⛔ THE ONE FUNNEL BOTH DURABLE HOMES PASS THROUGH, which is why the retirement is enforced here: the
    ternary/protfep lanes reach it via `blocked_machine_ids`, the fan-out via `_load_excluded`. While the
    list is retired this returns `[]` — dropping the SHARED ids *and* the caller's own durable ids, because
    both are the thing being retired and honouring one of them would leave the starvation in place."""
    if not durable_enabled():
        return []
    shared, _ = load(s3, bucket, key)
    return sorted({str(m) for m in (local_ids or [])} | set(shared))


def publish(s3, bucket, machine_id, why, lane, key=None):
    """Add a HOST-SCOPED machine to the shared set. Returns True if it was newly added.

    ⛔ REFUSES WHILE THE LIST IS RETIRED — a read path that returns nothing but a write path that keeps
    growing the object is the worst of both, because the starvation returns silently the moment anyone flips
    the switch back on and inherits a set nobody reviewed.

    Callers pass `scope="host"` deliberately at each site; this function does not guess, because the whole
    value of the split is that somebody looked at the reason and decided it was about the machine."""
    if not durable_enabled():
        return False
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
    ids, doc = load(s3, bucket, key, force=True)
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


def backfill(s3, bucket, machine_ids, lane, why=_REQUIRED, key=None):
    """Promote a lane's ALREADY-KNOWN host-scoped ids into the shared set. Returns the ids newly added.

    ⛔⛔ `why` IS MANDATORY AND MUST BE THE **ORIGINAL RECORDED REASON** — THIS FUNCTION LAUNDERED THE
    CAPACITY CLASS INTO THE PERMANENT SET FOR A WHOLE NIGHT (measured 2026-07-28).

    `publish` refuses `CLASS_CAPACITY` outright, which is the guard that is supposed to make a perishable
    refusal un-permanentable. `backfill` walked straight around it. It defaulted `why` to the synthetic
    string *"backfilled from {lane}'s refuse-to-start list"* — which contains none of `_CAPACITY_MARKERS`,
    so `classify_reason` returned `CLASS_HOST` and `publish` accepted every id. The evidence is in this
    module's own committed history: **32 of the 41 entries in
    `vast-blacklist-snapshot-before-clear.json` are that exact synthetic string**, and the snapshot's own
    `history_entries_by_reason_class` files them as `{'host': 9, 'capacity': 32}` — the capacity count
    coming from re-classifying the ORIGINAL reasons, not from what `publish` saw at the time.

    It was not a one-off seeding, either. `ternary_vast_launch.blocked_machine_ids` called this on EVERY
    read of the exclusion list, from a `_blocked_machines` list that the same lane's own comment describes
    as *"the whole set is the PERISHABLE capacity class"*. So each tick re-promoted that tick's busy hosts
    into a permanent, cross-lane, never-expiring set — and clearing the shared set could not help, because
    the next tick refilled it. That caller is gone; this signature is what stops the next one.

    A caller that passes the reason it actually recorded gets the classifier it deserves: a capacity reason
    is refused by `publish` exactly as if it had been published directly, and a genuine host verdict goes
    through. A caller with no reason to pass has no evidence, and no evidence is not a backfill.

    ⚠ THE GAP THIS CLOSES, and it is the one that made the union look like it worked when it did not. `union`
    and `publish` are both FORWARD-only: a lane publishes a host at the moment it observes the refusal, and
    reads the union thereafter. Neither does anything about the hosts a lane condemned BEFORE the shared set
    existed — which on 2026-07-27 was the entire population that mattered: the 5a-KS lane knew nine machines,
    the fan-out knew one, and the shared key was empty. A fan-out reading `local ∪ shared` still could not see
    machine 46392, so the exact rental the union was written to prevent would have happened again.

    ★ SUPERSEDED, RETAINED FOR THE RECORD — the paragraph below was the argument that authorised the
    laundering, and it must not be quoted again: *"ONLY A LIST THAT IS HOST-SCOPED BY CONSTRUCTION MAY BE
    BACKFILLED. `ternary_vast_launch`'s `_blocked_machines` qualifies — every entry on it is a start
    refusal, which is a property of the machine."* It is wrong twice over. A start refusal is NOT a property
    of the machine — `classify_reason`'s own comment records `resources_unavailable` and the create/start
    race as claims about a MOMENT, and three machines condemned on that verdict (53989, 31035, 24573) had
    run this repo's container at 94-99 % GPU. And the list stopped qualifying under any reading when it was
    made wave-scoped: it now holds exactly the ids that refused on the CURRENT tick.

    The rest of the original note stands and is why the function still exists:
    The step 1 fan-out's own exclusion file does NOT qualify: it mixes those with the sustained-`gpu_util` verdict,
    which is a property of the machine PAIRED WITH THAT WORKLOAD and which `pricing.md` A.1 already withdrew
    the broad version of. Backfilling that one wholesale would re-adopt the withdrawn rule for every lane —
    so the caller passes the ids and owns the judgement, exactly as `publish` requires.

    `why` may be one string (the reason every id on this list was recorded for) or a `{machine_id: reason}`
    mapping when the caller kept them per-id. Either way it is the reason `publish` classifies.

    Best-effort and idempotent: already-shared ids are skipped, and any failure is reported and swallowed,
    because seeding an optimisation must never be able to stop a launch."""
    if why is _REQUIRED:
        raise TypeError(
            "backfill() requires `why` — the ORIGINAL recorded reason for each id, not a synthetic label. "
            "A synthetic label is what let 32 perishable capacity refusals into the permanent shared set: "
            "it classified as CLASS_HOST and walked around publish()'s capacity guard. If you do not have "
            "the reason, you do not have the evidence, and there is nothing to backfill.")
    added = []
    for mid in (machine_ids or []):
        w = why.get(str(mid)) if isinstance(why, dict) else why
        if not w:
            print(f"[blacklist] NOT backfilling machine {mid}: no recorded reason for it in `why`. An "
                  f"entry nobody can justify is exactly what a clear is for.", flush=True)
            continue
        if publish(s3, bucket, mid, w, lane, key):
            added.append(str(mid))
    return added


def clear_lane_state(s3, bucket, lane_state_key):
    """Empty one lane's OWN exclusion list, whichever of the two shapes it is in. Returns the ids removed.

    Both copies must go or the set re-federates from whichever survived: a lane's reader unions its local
    list with the shared one, so clearing only the shared set leaves that lane still excluding.

    ⚠⚠ AND "WHICHEVER SHAPE" IS NOT A CONVENIENCE — IT IS THE BUG THAT MADE THE 2026-07-27 CLEAR A NO-OP FOR
    THE ONE LANE THAT MATTERED. This function used to know only `_blocked_machines`, and the clear was
    pointed at `nr4a3-step1-fanout/results/_lane_state.json`. The fan-out has never written that key: its
    list lives at `.../results/_excluded_machines.json` under `machine_ids`. So the clear printed
    "no lane state — nothing to clear", the operator read 74 entries removed, and the fan-out's own 41
    machines survived untouched — which is exactly the count its next tick filtered, five minutes later.
    An absent key now reports as MISSING rather than as clean, because "nothing to clear" and "I was
    pointed at the wrong file" must not print the same.
    """
    try:
        st = json.loads(s3.get_object(Bucket=bucket, Key=lane_state_key)["Body"].read())
    except Exception as e:  # noqa: BLE001 — an absent lane state is already "nothing excluded"
        print(f"[blacklist] ⚠ {lane_state_key}: NO SUCH DOCUMENT ({type(e).__name__}). Nothing was cleared "
              f"here — if you expected a list at this key, you are pointed at the wrong one, and a lane's "
              f"real list has just survived a clear that reported success.", flush=True)
        return []
    fields = [f for f in _LANE_LIST_FIELDS if isinstance(st.get(f), list)]
    if not fields:
        print(f"[blacklist] ⚠ {lane_state_key}: holds none of {_LANE_LIST_FIELDS} — this is not an exclusion "
              f"list, so nothing was cleared. Check the key.", flush=True)
        return []
    ids = sorted({str(m) for f in fields for m in (st.get(f) or [])})
    if not ids:
        print(f"[blacklist] {lane_state_key}: already empty", flush=True)
        return []
    for f in fields:
        st[f] = []
    st["_blocked_machines_cleared_utc"] = _utcnow()
    s3.put_object(Bucket=bucket, Key=lane_state_key, Body=json.dumps(st, indent=2).encode())
    print(f"[blacklist] {lane_state_key}: cleared {len(ids)} machine(s) from {fields}", flush=True)
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
    ap.add_argument("--lane-list", action="append", default=None, metavar="KEY",
                    help="READ-ONLY: report what is on this lane's own exclusion list, and the reason class "
                         "of each entry. Repeatable. Runs before any clear, and never writes.")
    ap.add_argument("--project-retire", action="store_true",
                    help="READ-ONLY: print what the exclusion filter WOULD become after the retires. Zero "
                         "writes, zero host contact, $0 — the way to verify the fix without a placing tick.")
    ap.add_argument("--retire-perishable", action="store_true",
                    help="remove SHARED entries whose OWN recorded reason is a capacity refusal. Not a TTL "
                         "and not an overrule — the rule publish() already enforces, applied retroactively.")
    ap.add_argument("--force-snapshot", action="store_true",
                    help="overwrite an existing snapshot file. Destroys a record; there is no good reason.")
    ap.add_argument("--lane-state", action="append", default=None, metavar="KEY",
                    help="also clear this lane's own `_blocked_machines` (repeatable)")
    # ⚠ `sys.argv[1:]`, NOT `[]`. Passing an empty list here silently DISCARDS every command-line flag, so
    # `--snapshot` and `--clear` were never seen and the tool just ran its read-only print while reporting
    # success — a clear that did nothing, twice, and looked like it had worked both times (2026-07-27).
    import sys
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    bucket = a.bucket_opt or a.bucket or (os.environ.get("VAST_CKPT_BUCKET")
                                          or "sagemaker-us-east-2-646605541856")
    import boto3
    s3 = boto3.client("s3")

    # FIRST, and read-only. A clear is judged against what was there; printing it afterwards is too late,
    # and printing only the shared set is how a lane's own 41 machines survived a clear that reported 74.
    for k in (a.lane_list or []):
        rep = lane_list_report(s3, bucket, k)
        print(f"[blacklist] LANE LIST {k}: "
              + (f"{len(rep['machine_ids'])} machine(s) in {rep.get('fields_present')}, "
                 f"by reason class {rep['by_reason_class']}" if rep["exists"]
                 else f"⚠ ABSENT ({rep.get('error')}) — nothing here, which is NOT the same as clean"))
        print(json.dumps(rep, indent=2))

    if a.project_retire:
        proj = project_retire(s3, bucket, a.lane_list or [])
        print("[blacklist] PROJECTED RETIRE (read-only, nothing changed):")
        print(json.dumps(proj, indent=2))
        t = proj["_total_union"]
        print(f"[blacklist] the launcher filters on {t['before']} machine(s) today -> {t['after']} "
              f"after the retires ({t['before'] - t['after']} would be released)")

    if a.clear and not a.snapshot:
        print("::error::--clear requires --snapshot: never delete state you have not first written down")
        return 2

    if a.snapshot:
        # ⛔⛔ A SNAPSHOT MAY NEVER OVERWRITE A SNAPSHOT. `--snapshot` is the only record of what was excluded
        # and why, and `research/modalities/vast-blacklist-snapshot-before-clear.json` — the 41-machine
        # pre-clear record, the input to every later question about whether clearing was right — is a fixed
        # path this CLI writes by default. Re-running the tool with the same path AFTER a clear would replace
        # it with an empty set: the evidence destroyed by the very tool whose contract is "never delete state
        # you have not first written down". The workflow already date-stamps the read-only path; this refuses
        # the clobber at the source, so no caller anywhere can commit it, and `--force-snapshot` is the only
        # way past — deliberately awkward, because there is no good reason to take it.
        if os.path.exists(a.snapshot) and not a.force_snapshot:
            print(f"::error::{a.snapshot} already exists. A snapshot is a record, not a buffer — writing "
                  f"over one destroys the only copy of what was excluded and why. Use a dated path "
                  f"(vast-blacklist-snapshot-$(date -u +%Y-%m-%dT%H%MZ).json), or --force-snapshot if you "
                  f"genuinely mean to lose the existing record.")
            return 2
        snap = snapshot(s3, bucket)
        with open(a.snapshot, "w") as fh:
            json.dump(snap, fh, indent=2)
            fh.write("\n")
        print(f"[blacklist] snapshot -> {a.snapshot}: {snap['n_machine_ids']} machine(s), "
              f"by reason class {snap['history_entries_by_reason_class']}")
        # AFTER the snapshot, ALWAYS — the retire is a mutation, and the record of what was there must be
        # written down before anything is removed. Same discipline as `--clear` requiring `--snapshot`.
        if a.retire_perishable:
            retire_perishable(s3, bucket)
        if not a.clear:
            # RETURN, don't fall through to the read-only dump. Printing the whole set after writing it to a
            # file is pure noise, and it buried the git error of the very step that failed to commit it.
            return 0

    if a.clear:
        removed = clear_all(s3, bucket, a.clear)
        for k in (a.lane_state or []):
            removed += clear_lane_state(s3, bucket, k)
        print(f"[blacklist] TOTAL cleared: {len(removed)} entr(ies)")
        ids_after, _ = load(s3, bucket, force=True)
        print(f"[blacklist] shared set now holds {len(ids_after)} machine(s)")
        return 0

    ids, doc = load(s3, bucket, force=True)
    print(json.dumps({"bucket": bucket, "key": SHARED_KEY, "machine_ids": ids,
                      "history": doc.get("history") or []}, indent=2))
    return 0


def snapshot(s3, bucket, key=None):
    """The FULL current shared state, for committing before a clear. Read-only.

    Clearing without a record would destroy the only evidence of what was excluded and why — which is also
    the input to any later question about whether clearing was right. Never delete state you have not first
    written down somewhere durable.
    """
    ids, doc = load(s3, bucket, key, force=True)
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


def project_retire(s3, bucket, lane_keys=()):
    """READ-ONLY: what the exclusion filter WOULD be after the retires, without changing anything.

    ★ WHY A DRY RUN AND NOT "JUST RUN IT AND LOOK". The retire lives in the fan-out's launch tick, and a
    launch tick places units — so verifying the fix by running one costs GPU dollars, which is exactly what
    is not authorised here. This computes the same answer from the same functions over the live lists, with
    zero writes and zero contact with any host: one S3 GET per key.

    Returns `{key: {"before": n, "after": n, "would_retire": [...]}}` plus a `_total` row, because the number
    that actually gates placement is the UNION the launcher filters on, not any single list.
    """
    out, union_before, union_after = {}, set(), set()
    for k in (list(lane_keys) + [SHARED_KEY]):
        rep = lane_list_report(s3, bucket, k)
        if not rep["exists"]:
            out[k] = {"absent": True, "error": rep.get("error")}
            continue
        ids = set(rep["machine_ids"])
        # The shared set retires the capacity class only; a lane's own list also sheds entries carrying no
        # recorded reason at all. Both rules are the ones the live code applies — see `retire_perishable`
        # and `congeneric_fanout_vast.retire_perishable_exclusions`.
        drop = {m for m, v in rep["per_machine"].items() if v["class"] == CLASS_CAPACITY}
        if k != SHARED_KEY:
            drop |= {m for m, v in rep["per_machine"].items() if v["class"] == "unjustified"}
        out[k] = {"before": len(ids), "after": len(ids - drop), "would_retire": sorted(drop),
                  "by_reason_class": rep["by_reason_class"]}
        union_before |= ids
        union_after |= (ids - drop)
    out["_total_union"] = {"before": len(union_before), "after": len(union_after),
                           "_what": "the machine count the launcher actually filters on (local ∪ shared)"}
    return out


def retire_perishable(s3, bucket, key=None, lane="operator"):
    """Take out of the SHARED set every entry whose OWN recorded reason classifies as CLASS_CAPACITY.

    ⚠⚠ WHY THIS IS NEEDED EVEN THOUGH `publish` NOW REFUSES THAT CLASS. Because entries created BEFORE the
    guard, or created THROUGH it by `backfill`'s synthetic label, are still sitting there — and they are the
    majority. Measured live at 7:16 AM ET 2026-07-28, hours after the set was cleared to zero: the shared
    set held FOUR machines, and the history says three of them are perishable —

      * `8914`  — "backfilled from rung5a_ks's refuse-to-start list", filed `reason_class: host`, written at
                  11:15:26Z, **ninety seconds before the diagnostic ran**. That is the laundering caught in
                  the act: `ternary-vast/_lane_state.json` held exactly `["8914"]` at that moment, i.e. the
                  ternary lane's WAVE-SCOPED capacity refusal for the current tick, promoted to a permanent
                  cross-lane entry by the per-read backfill.
      * `46427`, `62866` — "never started: cur_state=stopped with an empty status_msg … (create/start race,
                  not an image pull)", both with `reason_class: None`, i.e. written by a pre-guard build of
                  this module that a lane branch was still running.
      * `28908` — "container never started: 163 min from rental with no phase mark of its own" — a genuine
                  host verdict, and it stays.

    ★ THIS IS NOT `withdraw`, AND IT IS NOT AN OVERRULE OF ANOTHER LANE. `withdraw(only_lane=True)` refuses
    to touch another lane's entry because that entry rests on evidence we cannot see. Here we ARE looking at
    their evidence — the reason they recorded — and applying the classification rule the set now enforces at
    its own door. The question answered is not "were they wrong?" but "could this entry be created today?",
    and for a capacity reason the answer is no, by their rule and ours. Nothing is retired for being old.

    Returns the retired ids. Idempotent.
    """
    ids, doc = load(s3, bucket, key, force=True)
    if not ids:
        return []
    hist = list(doc.get("history") or [])
    retire = []
    for mid in ids:
        rows = [h for h in hist if str(h.get("machine_id")) == mid and h.get("action") != "withdraw"]
        if rows and all(classify_reason(h.get("why")) == CLASS_CAPACITY for h in rows):
            retire.append(mid)
    if not retire:
        return []
    hist.append({"machine_id": None, "action": "retire_perishable", "lane": lane, "utc": _utcnow(),
                 "reason_class": "retire",
                 "why": f"RETIRED {len(retire)} entr(ies) whose own recorded reason classifies as "
                        f"CLASS_CAPACITY — a claim about a moment, which `publish` refuses at the door and "
                        f"which reached this set before the guard or through backfill's synthetic label.",
                 "retired_machine_ids": retire})
    try:
        s3.put_object(Bucket=bucket, Key=key or SHARED_KEY,
                      Body=json.dumps({"_what": _WHAT, "_scope": "host — fails to start for anybody",
                                       "machine_ids": sorted(set(ids) - set(retire)),
                                       "history": hist}, indent=2).encode())
    except Exception as e:  # noqa: BLE001 — a repair must never be able to stop a launch
        print(f"[blacklist] could not retire perishable shared entries: {type(e).__name__}: {e}", flush=True)
        return []
    print(f"[blacklist] ⚖ RETIRED {len(retire)} perishable entr(ies) from the SHARED set {retire} — their "
          f"own recorded reasons are capacity refusals. {len(set(ids) - set(retire))} host-scoped entr(ies) "
          f"remain.", flush=True)
    return retire


def lane_list_report(s3, bucket, lane_key):
    """READ-ONLY: what is on ONE lane's own exclusion list, and what class each entry's OWN reason is.

    ★ THE DIAGNOSTIC THE 2026-07-27 CLEAR DID NOT HAVE. That clear operated on the shared set plus three
    `--lane-state` keys and reported "74 entries cleared" — a number nobody could check against the lane
    that actually mattered, because one of the three keys did not exist and the tool said so in a line that
    read like "already clean". A per-lane readout makes "this key holds 41 machines" and "this key holds
    nothing because it is the wrong key" two different, unmistakable outputs.

    Classifies from each entry's ORIGINAL recorded reason, so the answer to "how much of this list is
    perishable?" comes from the evidence rather than from a guess. $0: one S3 GET.
    """
    out = {"key": lane_key, "exists": False, "machine_ids": [], "by_reason_class": {}, "per_machine": {},
           "unjustified": []}
    try:
        doc = json.loads(s3.get_object(Bucket=bucket, Key=lane_key)["Body"].read())
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {str(e)[:160]}"
        return out
    out["exists"] = True
    fields = [f for f in _LANE_LIST_FIELDS if isinstance(doc.get(f), list)]
    out["fields_present"] = fields
    ids = sorted({str(m) for f in fields for m in (doc.get(f) or [])})
    out["machine_ids"] = ids
    hist = list(doc.get("history") or [])
    for mid in ids:
        rows = [h for h in hist if str(h.get("machine_id")) == mid and h.get("action") != "withdraw"]
        if not rows:
            out["unjustified"].append(mid)
            cls = "unjustified"
        else:
            cls = (CLASS_CAPACITY if all(classify_reason(h.get("why")) == CLASS_CAPACITY for h in rows)
                   else CLASS_HOST)
        out["per_machine"][mid] = {"class": cls, "why": (rows[-1].get("why") if rows else None)}
        out["by_reason_class"][cls] = out["by_reason_class"].get(cls, 0) + 1
    return out


def clear_all(s3, bucket, why, lane="operator", key=None):
    """Empty the shared exclusion set, keeping the history as an audit trail. Returns the ids removed.

    The clear is itself appended to `history`, so the record shows an EVENT rather than a gap — a set that
    silently became empty is indistinguishable from one that was never written.
    """
    ids, doc = load(s3, bucket, key, force=True)
    hist = list(doc.get("history") or [])
    hist.append({"machine_id": None, "why": f"CLEARED {len(ids)} machine(s): {why}", "lane": lane,
                 "utc": _utcnow(), "reason_class": "clear", "cleared_machine_ids": ids})
    s3.put_object(Bucket=bucket, Key=key or SHARED_KEY,
                  Body=json.dumps({"_what": _WHAT, "_scope": "host — fails to start for anybody",
                                   "machine_ids": [], "history": hist}, indent=2).encode())
    print(f"[blacklist] CLEARED {len(ids)} machine(s) from the shared set: {why}", flush=True)
    return ids
if __name__ == "__main__":
    raise SystemExit(main())
