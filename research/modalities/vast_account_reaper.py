#!/usr/bin/env python3
"""ONE CENTRAL THING THAT ACTUALLY DESTROYS HOSTS — keyed on the VAST ACCOUNT, not on any lane.

★★ WHY THIS EXISTS, and it is not a hypothetical: ON 2026-08-01 THE SAME FAILURE HAPPENED FOUR TIMES, IN FOUR
DIFFERENT LANES, THROUGH FOUR SEPARATE TEARDOWN IMPLEMENTATIONS. Every lane owns its own reap path, so every
lane owns its own reap BUGS, and a bug in any one of them leaves a box billing with nothing watching:

    ternary      `collect`'s destroy chain reaped a LIVE re-run because that unit's `leg.json` had said
                 `done` since five days earlier. Instance 46459452 was killed 2 min 23 s in, mid image-pull,
                 having executed not one line of the run script.
    NR-V04 retro `retro_reap` never fired at all, because the failure breaker's anchor could not advance.
    GCP          the reaper worked correctly and nothing ever relaunched, so the single GPU idled 8-15 h,
                 twice.
    selcal       `mode=reap` runs, exits SUCCESS, and destroys NEITHER a finished host NOR a terminal one.

Detection is already centralised and already works: `account_orphan_alarm.py` has been firing `ATTENTION`
unattended and re-driving its own census input (delivered gaps went 156 min -> ~15 min). **WHAT WAS MISSING IS
A CENTRAL THING THAT ACTS.** Four private teardown paths is four chances to be wrong; this is one path, with
one predicate, that no lane can break by breaking its own.

═════════════════════════════════════════════════════════════════════════════════════════════════════════════
THE DIVISION OF LABOUR, AND WHY IT IS NOT ONE MODULE
═════════════════════════════════════════════════════════════════════════════════════════════════════════════
    `account_orphan_alarm.py`   NOTICES. Report-only, pinned by AST, no credential, safe to run against a lane
                                whose semantics it does not understand — which is exactly why it can be
                                trusted everywhere.
    THIS MODULE                 ACTS. Narrow predicate, irreversible effect, ladders through a dry run,
                                carries the key.

Merging them would trade the alarm's universality for this module's blast radius, and the alarm is the thing
that has been working. The dependency runs ONE WAY — reaper imports alarm, never the reverse — so the detector
stays exactly as trustworthy as it was.

═════════════════════════════════════════════════════════════════════════════════════════════════════════════
THE TWO RULES. NOTHING ELSE MAY EVER BE ADDED WITHOUT THE SAME BURDEN OF PROOF.
═════════════════════════════════════════════════════════════════════════════════════════════════════════════
**RULE 1 — TERMINAL STATE, UNCONDITIONAL.** `exited` / `stopped` / `offline` / `error`. A terminal host is not
coming back: whatever it produced is already in the object store or was never written, so this rule CANNOT
LOSE WORK BY CONSTRUCTION — there is no work left to lose. It is the rule that would have caught the selcal
box that sat `exited` with zero models while its lane's `mode=reap` exited success.

⚠ THE TERMINAL SET IS **DERIVED BY AST FROM THE LANES THAT ALREADY DEFINE IT** (§1: one fact, one place). Two
definitions exist and neither can be imported (one is a FUNCTION-LOCAL, and importing a lane here would make
the reaper die whenever a lane does):

    congeneric_fanout_vast._TERMINAL       = ("exited", "offline", "error")     <- function-local
    nrv04_vast_launch._TERMINAL_STATES     = ("exited", "offline", "stopped")

So they are read out of the source. If they cannot be read, RULE 1 IS DISABLED and says so — an unreadable
definition is not an empty one (§4).

⚠ `created` IS NOT TERMINAL, and this is written down because an earlier draft had it and that draft would
have destroyed EVERY FRESH RENTAL — a reaper that reaps the healthiest event in the system. Neither repo
definition contains it; it is an EARLY lifecycle state. `test_created_is_never_terminal` pins it.

**RULE 2 — WORK BANKED AND NO REMAINING ROLE.** A host whose lane records its unit `done` AND whose output is
verifiably present in the object store. This is the rule that catches a host like selcal's 46508454, which
finished at 10:41 AM ET with its six models banked in S3 and then billed for another hour and a half.

⚠ VERIFY THE ARTIFACT, NEVER ELAPSED TIME, AND NEVER A POPULATED FIELD (§4b). "Done" is not believed from a
JSON field that a default could have filled in; the reaper LISTS the object store itself and reads the
`LastModified` the store reports. A census row saying `n_models: 6` is a claim; an object with an mtime is a
measurement.

═════════════════════════════════════════════════════════════════════════════════════════════════════════════
WHAT IT MUST NEVER DO. EACH OF THESE IS A REAL INCIDENT.
═════════════════════════════════════════════════════════════════════════════════════════════════════════════
⛔ **NEVER REAP ON `gpu_util`.** `vast_idle_guard`'s inviolable rule, and it is measured, not stylistic: BOTH
   selcal boxes read `gpu_util: 0.0` INCLUDING THE ONE THAT WAS WORKING CORRECTLY, and on 2026-07-27 two
   step-1 boxes read 0.0 in the same snapshot in which they committed real production sampling. The key is
   never read here at all and `test_gpu_util_is_never_read` walks the AST to keep it that way.

⛔ **NEVER REAP ON AGE.** A healthy fan-out leg legitimately runs for many hours. `uptime_h` and `start_date`
   ARE read — but only ever as the *reference point* for "is this record newer than this host", never as a
   condemning quantity. `test_age_alone_never_reaps` drives a 40-hour box through the predicate and requires
   SPARE.

⛔ **NEVER REAP ON A STALE OR UNREADABLE CENSUS.** Fail closed. An absent reading is not a reading of absence
   (§4), and the account census was measured 155 min stale earlier the same day — a window in which a naive
   check sees an empty fleet and a naive reaper would conclude there was nothing to do while two hosts billed.
   Worse for a REAPER than for an alarm: acting on a stale census means acting on a host that may have been
   replaced by a different rental since.

⛔ **NEVER TRUST A `done` RECORD OLDER THAN THE INSTANCE.** That is exactly what killed 46459452 mid
   image-pull. The predicate compares the record's stamp against the instance's `start_date`;
   `protfep_vast_launch._record_is_newer_than_instance` has existed for this since the protfep lane learned
   the same lesson, and was applied to `crashed` but NEVER to `finished`. Here it guards `finished`, which is
   the branch that actually destroys.

═════════════════════════════════════════════════════════════════════════════════════════════════════════════
LADDERED, BECAUSE DESTROYING IS IRREVERSIBLE
═════════════════════════════════════════════════════════════════════════════════════════════════════════════
1. `--dry-run` (THE DEFAULT) plans and commits an artifact showing what it WOULD destroy and the evidence for
   each. Nothing is called.
2. `--arm` is required to destroy, and dry-run stays permanently available — a reaper you cannot ask "what
   would you do" is one nobody can review before it acts.
3. **BILLED HOURS ARE RECORDED AT DESTROY, BEFORE THE DELETE.** That is the last moment the instance record
   exists; a rental that billed and left no trace has already happened in this repo. The ledger line is
   written and flushed BEFORE the API call, so a crash mid-destroy still leaves the evidence.

Usage:
    python3 vast_account_reaper.py [--root DIR] [--census PATH] [--json OUT] [--ledger OUT]
                                   [--arm] [--now ISO8601Z] [--census-stale-min N]
Exit 0 = the plan was produced (whether or not anything was reaped). Exit 1 = fail-closed, nothing graded.
Exit 2 = armed and at least one destroy call failed.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import json
import os
import re
import sys

import account_orphan_alarm as AOA

ET = datetime.timezone(datetime.timedelta(hours=-4))  # EDT. CLAUDE.md §1: US Eastern, 12-hour, always.

HERE = os.path.dirname(os.path.abspath(__file__))

# Re-exported so nothing here re-implements a time or JSON reader that already has a home (§1). These are the
# alarm's, and they are pure stdlib with no lane dependency.
parse_z = AOA.parse_z
load_json = AOA.load_json
_et = AOA._et
_z = AOA._z


# ── thresholds ───────────────────────────────────────────────────────────────────────────────────────────
#: How old the account census may be before the reaper refuses to act on it AT ALL.
#:
#: ⚠ IT IS TIGHTER THAN THE ALARM'S 45 MIN AND THAT ASYMMETRY IS DELIBERATE. The alarm's cost of acting on a
#: slightly stale census is a wrong sentence in a report; the reaper's is a destroyed host. A census older
#: than this may describe instances that no longer exist, or miss ones that now do — and an instance id is
#: reused by nothing, but a lane that relaunched in the gap would have its NEW box judged on its OLD box's
#: state. So: no reading, no action.
DEFAULT_CENSUS_STALE_MIN = 20.0

#: How far the census stamp may sit IN THE FUTURE before it stops being believable. Same reasoning as the
#: alarm's `DEFAULT_FUTURE_SKEW_MIN`, and the same failure it prevents: a negative age passes every staleness
#: comparison forever, so a skewed clock would silently make this module act on an arbitrarily old reading.
DEFAULT_FUTURE_SKEW_MIN = 5.0

#: The two lane modules that already define what "terminal" means. READ, never imported — see the header.
_TERMINAL_SOURCES = (
    ("congeneric_fanout_vast.py", "_TERMINAL"),
    ("nrv04_vast_launch.py", "_TERMINAL_STATES"),
)

#: Lifecycle states that are EARLY, not terminal. Held separately and asserted disjoint from the derived
#: terminal set, so a lane that ever mislabels one of these cannot turn this module into a shredder of fresh
#: rentals. `created` is here because an earlier draft of this very module had it in the terminal set.
EARLY_STATES = ("created", "loading", "starting", "scheduling")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# RULE 1's vocabulary — DERIVED FROM THE LANES THAT DEFINE IT, NOT TYPED HERE
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _tuple_of_str(node) -> tuple[str, ...] | None:
    """A literal tuple/list of plain strings -> that tuple. Anything else -> None. PURE."""
    if not isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return None
    out = []
    for e in node.elts:
        if not (isinstance(e, ast.Constant) and isinstance(e.value, str)):
            return None
        out.append(e.value)
    return tuple(out)


def terminal_states_from_source(root: str = HERE, sources=_TERMINAL_SOURCES
                                ) -> tuple[frozenset[str], list[str]]:
    """`(union_of_terminal_states, notes)` — read out of the lanes' own source. PURE apart from the file read.

    ★ WHY AST AND NOT `import`. `congeneric_fanout_vast._TERMINAL` is a FUNCTION-LOCAL — there is no attribute
    to import — and importing a lane at all would give this module the failure mode it exists to remove: the
    central reaper dying because one lane's module is broken is exactly "four private paths" with extra steps.
    An AST read needs neither the lane's imports nor its dependencies.

    ★ AND IT FAILS CLOSED. Anything unreadable returns what it COULD derive plus a note saying what it could
    not, and the caller disables RULE 1 when the derivation is incomplete. An empty set here must never render
    as "nothing is terminal" (§4).
    """
    union: set[str] = set()
    notes: list[str] = []
    for fname, want in sources:
        path = os.path.join(root, fname)
        try:
            with open(path) as fh:
                tree = ast.parse(fh.read(), filename=path)
        except (OSError, SyntaxError, ValueError) as e:
            notes.append(f"{fname}: unreadable ({type(e).__name__}: {e}) — its terminal states are NOT in "
                         f"this union, so RULE 1 is running on an incomplete definition")
            continue
        found = None
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and t.id == want:
                    got = _tuple_of_str(getattr(node, "value", None))
                    if got is not None:
                        found = got
        if found is None:
            notes.append(f"{fname}: no literal string tuple assigned to `{want}` — the definition moved or "
                         f"stopped being a literal, so it is NOT in this union")
            continue
        union |= {s.strip().lower() for s in found if isinstance(s, str) and s.strip()}
        notes.append(f"{fname}.{want} = {tuple(sorted(found))}")
    return frozenset(union), notes


def is_terminal(inst: dict, terminal: frozenset[str]) -> bool:
    """PURE. Is this instance in a terminal state, by EITHER status field?

    ★ EITHER, NOT BOTH. `account_orphan_alarm` learned the same thing: a half-terminal instance (one field
    moved, the other not yet) is still an instance the control plane has to clear, and requiring agreement
    would let it slip through. The cost of being wrong in this direction is zero — a terminal host has no work
    to lose.
    """
    if not terminal:
        return False
    a = str(inst.get("actual_status") or "").strip().lower()
    c = str(inst.get("cur_state") or "").strip().lower()
    return a in terminal or c in terminal


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# RULE 2's guard — THE ONE THAT WAS MISSING WHEN 46459452 DIED
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def record_is_newer_than_instance(record_epoch: float | None, inst: dict) -> tuple[bool, str]:
    """`(is_newer, why)` — did THIS host write that record? PURE.

    ★★ THIS IS THE 46459452 PREDICATE. On 2026-07-31 the ternary lane destroyed a live re-run 2 min 23 s in,
    mid image-pull, because `finished = uid in done` was true — that unit's `leg.json` had said `done` since
    the ORIGINAL smoke FIVE DAYS EARLIER. The identical guard already existed for `crashed`
    (`protfep_vast_launch._record_is_newer_than_instance`, added when the protfep lane learned the same lesson
    about stale FAILED records) and had never been applied to `finished`. Here it guards the branch that
    destroys, and there is no path to a RULE 2 reap that bypasses it.

    ⚠ EVERY AMBIGUITY RETURNS FALSE, i.e. SPARE. A missing stamp, an unparseable one, a missing `start_date`:
    none of them is evidence that the host finished, and the cost of not reaping is minutes of one box while
    the cost of reaping wrongly is an entire authorised experiment (measured: 46459452 produced no `[prune]`
    line, no manifest, no `run.log`, not even a `status.json` — every artifact byte-identical to "no rental
    ever happened").
    """
    started = inst.get("start_date")
    if record_epoch is None:
        return False, "the completion record carries no readable timestamp, so it cannot be attributed to any "\
                      "particular rental — SPARE (§4: an absent reading is not a reading of absence)"
    if started is None:
        return False, "the instance record carries no `start_date`, so 'did this host write that' cannot be "\
                      "answered — SPARE"
    try:
        started = float(started)
    except (TypeError, ValueError):
        return False, f"the instance's `start_date` is not a number ({inst.get('start_date')!r}) — SPARE"
    if record_epoch > started:
        return True, (f"the completion record is stamped {_et(_dt(record_epoch))}, AFTER this host started "
                      f"({_et(_dt(started))}) — so it is THIS rental's own record")
    return False, (f"the completion record is stamped {_et(_dt(record_epoch))}, which is BEFORE this host "
                   f"started ({_et(_dt(started))}) — it belongs to a PREVIOUS attempt, not this one. This is "
                   f"the 46459452 case: a live re-run destroyed 2 min into its image pull because a five-day-"
                   f"old `done` record was read as this host's. SPARE.")


def _dt(epoch: float | None) -> datetime.datetime | None:
    if epoch is None:
        return None
    try:
        return datetime.datetime.fromtimestamp(float(epoch), datetime.timezone.utc)
    except (TypeError, ValueError, OSError, OverflowError):
        return None


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# RULE 2 — "work banked and no remaining role", on evidence a lane cannot fake by accident
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ THE ATTRIBUTION PROBLEM IS THE WHOLE DIFFICULTY, AND IT IS WHY THIS DOES NOT MAP LABELS TO UNITS.
#
# Every lane's own reaper answers "is this host's unit done?" by decoding the Vast label back into a unit id.
# That decode is a LOSSY REVERSE MAPPING — `protfep_vast_launch.label_matches_leg`'s own docstring says
# "matching has to go leg_id -> label, never the reverse", because the label flattens underscores, lowercases
# and truncates to 60 chars — and getting it wrong is exactly the class of bug that has cost money here twice
# (protfep's smoke label never matched its leg id, so its crash-looping host billed unattended; ternary's
# `finished` matched a five-day-old record and destroyed a live re-run).
#
# A CENTRAL reaper must not re-implement eight lanes' worth of that decode. So it does not decode anything:
# it requires the completion record to NAME THE INSTANCE ID. That convention already exists in this repo and
# is not invented here —
#     nrv04's `_RETRO_ATTEMPT_MARKER` writes `attempt <UTC> instance=$CONTAINER_ID`
#       (`nrv04_vast_launch.retro_attempt_hosts` parses exactly this to count DISTINCT rentals),
#     the selcal phase marker writes `done rc=0 2026-08-01T14:41:08Z instance=46508454 attempt=…`
#       (`account_orphan_alarm` and `lane_staleness_watch` both already extract from it).
# — so attribution is EXACT rather than decoded, and a lane opts into RULE 2 by writing a marker it already
# knows how to write. A lane that does not is simply never reaped by RULE 2; it is still covered by RULE 1.
#
# ⚠ AND THE MARKER ALONE IS NOT ENOUGH. Four conditions, ALL required, any failure SPARES:
#   (a) the marker names THIS instance id                        -> exact attribution, no decode
#   (b) its phase token is terminal and its rc is 0              -> the host itself said it finished cleanly
#   (c) its stamp is NEWER than the instance's `start_date`      -> the 46459452 guard
#   (d) the OBJECT STORE, listed by this module, holds >= 1 object under the lane's output prefix whose
#       store-reported `LastModified` falls inside THIS rental's lifetime
#                                                                -> work is BANKED, measured not claimed
#
# ⚠ (d) IS DELIBERATELY SCOPED TO THE LANE PREFIX, NOT TO A UNIT SUB-PATH DERIVED FROM THE LABEL. Deriving
# that sub-path would reintroduce the lossy decode this design exists to avoid, and a broader prefix can only
# make (d) EASIER to pass — it never lets through a case that (a)+(b)+(c) had rejected. What (d) is actually
# guarding is "said done, banked nothing", and a lane-wide prefix catches that perfectly well.
#
# ⚠ AND (d) READS `LastModified` FROM THE STORE, NEVER A COUNT OUT OF A JSON FILE. §4b: a census row saying
# `n_models_per_arm: 6` is a CLAIM; an object with an mtime is a MEASUREMENT. 17 smoke legs once echoed
# `prod_ns: 5.0` from their ENV and a completeness count believed them.

#: `<phase> rc=<n> <ISO-Z> instance=<id> …` — the shared marker convention described above.
_PHASE_RE = re.compile(r"(?P<phase>[A-Za-z_][\w-]*)\s+rc=(?P<rc>-?\d+)\s+"
                       r"(?P<utc>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)\s+"
                       r"instance=(?P<instance>\S+)")

#: Phase tokens that mean "this container's run is over". NOT a synonym for "succeeded" — `rc` carries that.
DONE_PHASES = ("done", "finished", "complete", "completed")

#: One row per lane that has opted into RULE 2 by committing an instance-named completion marker.
#:
#: ⚠ AN EMPTY REGISTRY IS A CORRECT STATE, NOT A BROKEN ONE. RULE 2 then never fires and RULE 1 still covers
#: every lane. That is the intended failure direction for a rule that destroys: opting in is explicit.
#:
#: FIELDS
#:   lane          matches `account_orphan_alarm.ACCOUNT_LANES[*].key`, so the two readouts line up.
#:   record        repo-visible JSON artifact holding the marker. Committed, so this needs no S3 to READ the
#:                 marker — S3 is needed only for (d).
#:   marker_keys   keys to try, in order, for the marker string.
#:   output_uri    where this lane's outputs land, as `s3://bucket/prefix`. `{bucket}` is filled from
#:                 `VAST_CKPT_BUCKET`; `{…}` fields named `record:<key>` are filled from the record itself,
#:                 which is a LOCATION (verifying at a location is still a measurement) and never a claim
#:                 about how much work was done.
WORK_RECORDS: list[dict] = [
    {
        "lane": "selcal-cofold",
        "label_prefixes": ("selcal-",),
        "record": "selcal-cofold-census.json",
        "marker_keys": ("phase",),
        "output_uri": "s3://{bucket}/{record:prefix}",
        "why_registered": ("this lane's phase marker already carries `instance=<id>`, and it is the lane "
                           "whose host 46508454 finished at 10:41 AM ET with six models banked and then "
                           "billed for another hour and a half while its own `mode=reap` ran and exited "
                           "success."),
    },
]

DEFAULT_BUCKET_ENV = "VAST_CKPT_BUCKET"


def parse_phase_marker(text) -> tuple[dict | None, str]:
    """`(marker, why_not)` from a `done rc=0 <ISO-Z> instance=<id>` string. PURE, and NEVER guesses.

    A string that does not match returns None with a reason. Half-parsing it — taking the stamp but not the
    instance, say — would produce an attribution nobody measured, which is the defect §4b names."""
    if not isinstance(text, str) or not text.strip():
        return None, "the marker field is absent or not a string"
    m = _PHASE_RE.search(text)
    if not m:
        return None, (f"the marker does not carry the `<phase> rc=<n> <ISO-Z> instance=<id>` convention "
                      f"({text[:90]!r}) — without an instance id there is no exact attribution, and this "
                      f"module will not decode a Vast label back into a unit to get one")
    stamp = parse_z(m.group("utc"))
    if stamp is None:
        return None, f"the marker's timestamp {m.group('utc')!r} is unparseable"
    try:
        rc = int(m.group("rc"))
    except (TypeError, ValueError):
        return None, f"the marker's rc {m.group('rc')!r} is not an integer"
    return {"phase": m.group("phase").lower(), "rc": rc, "instance": m.group("instance"),
            "utc": _z(stamp), "et": _et(stamp), "epoch": stamp.timestamp()}, ""


def _spare(why: str, **kw) -> dict:
    d = {"banked": False, "why": why}
    d.update(kw)
    return d


def gather_banked_evidence(inst: dict, *, root: str = HERE, records=None, lister=None,
                           bucket: str | None = None) -> dict | None:
    """RULE 2's evidence for ONE instance, or None when no registered lane claims its label.

    `lister(uri) -> [(key, mtime_epoch)]` is injected so every branch is testable with no boto3, no
    credential and no network — the property that let the alarm's controls find real bugs before CI did.

    ★ FAIL CLOSED EVERYWHERE. Unreadable record, unmatched marker, wrong instance, non-zero rc, stale stamp,
    unlistable store: every one returns evidence that does NOT say `banked: True`, and `classify_instance`
    reaps only on `banked is True`.
    """
    records = WORK_RECORDS if records is None else records
    label = str(inst.get("label") or "")
    spec = None
    for r in records:
        if any(label.startswith(p) for p in r.get("label_prefixes") or ()):
            spec = r
            break
    if spec is None:
        return None

    ev: dict = {"lane": spec["lane"], "record": spec.get("record"), "banked": False}

    doc, err = load_json(os.path.join(root, spec["record"]))
    if doc is None:
        return _spare(f"RULE 2 needs this lane's completion record and it could not be read ({err}). An "
                      f"absent reading is not a reading of absence (§4) — SPARE.", **ev)

    marker, why = None, "no marker key was declared"
    for k in spec.get("marker_keys") or ():
        marker, why = parse_phase_marker(doc.get(k))
        if marker:
            break
    if not marker:
        return _spare(f"RULE 2 could not read an instance-named completion marker from "
                      f"{spec['record']}: {why} — SPARE.", **ev)
    ev["marker"] = marker

    # ── (a) EXACT ATTRIBUTION ────────────────────────────────────────────────────────────────────────────
    if str(marker["instance"]) != str(inst.get("id")):
        return _spare(f"the lane's latest completion marker names instance {marker['instance']}, not this "
                      f"one ({inst.get('id')}). A marker for a DIFFERENT rental is not evidence about this "
                      f"host, and this module will not decode a label into a unit to find a better one — "
                      f"SPARE.", **ev)

    # ── (b) TERMINAL PHASE, CLEAN EXIT ───────────────────────────────────────────────────────────────────
    if marker["phase"] not in DONE_PHASES:
        return _spare(f"the marker for this host reads phase={marker['phase']!r}, which is not a terminal "
                      f"phase ({DONE_PHASES}) — the run has not declared itself over. SPARE.", **ev)
    if marker["rc"] != 0:
        return _spare(f"the marker for this host reads rc={marker['rc']}, so the run ended in FAILURE. RULE 2 "
                      f"is 'work banked', and a failed run has banked nothing to justify a reap on those "
                      f"grounds. If the container is genuinely finished it will go terminal and RULE 1 clears "
                      f"it — which is the rule that cannot be wrong. SPARE.", **ev)

    # ── (c) THE 46459452 GUARD ───────────────────────────────────────────────────────────────────────────
    ours, attribution_why = record_is_newer_than_instance(marker["epoch"], inst)
    ev["attribution_why"] = attribution_why
    if not ours:
        return _spare(f"RULE 2 will not act on this record: {attribution_why}", **ev)

    # ── (d) WORK ACTUALLY BANKED — MEASURED FROM THE STORE ───────────────────────────────────────────────
    uri, uri_why = _output_uri(spec, doc, bucket)
    ev["output_uri"] = uri
    if not uri:
        return _spare(f"RULE 2 cannot verify banked output because this lane's output location could not be "
                      f"resolved ({uri_why}). Nothing is destroyed on an unverified claim — SPARE.", **ev)
    if lister is None:
        return _spare(f"RULE 2 is DISABLED for this run: no object-store lister is available, so 'work "
                      f"banked' cannot be MEASURED and would have to be taken from a JSON field. A populated "
                      f"field is not a measured one (§4b) — SPARE. RULE 1 is unaffected.",
                      **dict(ev, banked=None))
    try:
        objs = lister(uri)
    except Exception as e:                                        # noqa: BLE001 — could not ask != none found
        return _spare(f"RULE 2 could not list {uri} ({type(e).__name__}: {e}). 'I could not ask' is not 'the "
                      f"answer was none' (§4) — SPARE.", **dict(ev, banked=None))

    start = float(inst.get("start_date") or 0.0)
    end = marker["epoch"] + 900.0            # 15 min of slack for an upload finishing after the marker
    inside = [(k, m) for (k, m) in (objs or []) if m is not None and start <= float(m) <= end]
    ev["n_objects_under_prefix"] = len(objs or [])
    ev["n_objects_written_by_this_rental"] = len(inside)
    if not inside:
        return _spare(f"the host's marker says done rc=0, but the object store holds NO object under {uri} "
                      f"whose LastModified falls inside this rental's lifetime "
                      f"({_et(_dt(start))} .. {_et(_dt(end))}) — so nothing was banked and 'work banked' is "
                      f"not true. SPARE (RULE 1 still clears it once it goes terminal).", **ev)

    newest = max(inside, key=lambda t: t[1])
    ev["banked"] = True
    ev["newest_object"] = {"key": newest[0], "mtime_utc": _z(_dt(newest[1])), "mtime_et": _et(_dt(newest[1]))}
    ev["why"] = (f"marker `{marker['phase']} rc={marker['rc']}` names THIS instance ({marker['instance']}) at "
                 f"{marker['et']}, and {len(inside)} object(s) under {uri} carry a store-reported "
                 f"LastModified inside this rental's lifetime — newest {newest[0]} at "
                 f"{ev['newest_object']['mtime_et']}. The work is BANKED (measured from the store, not read "
                 f"out of a JSON field) and this host has no remaining role.")
    return ev


def _output_uri(spec: dict, doc: dict, bucket: str | None) -> tuple[str | None, str]:
    """PURE. Resolve the lane's declared `output_uri` template. `{bucket}` from env/arg, `{record:<key>}` from
    the record. A missing piece returns None WITH A REASON rather than a half-built URI — listing the wrong
    prefix would silently answer a different question."""
    tpl = spec.get("output_uri")
    if not tpl:
        return None, "the registry row declares no `output_uri`"
    b = bucket or os.environ.get(DEFAULT_BUCKET_ENV) or ""
    if "{bucket}" in tpl and not b:
        return None, f"no bucket: ${DEFAULT_BUCKET_ENV} is unset and none was passed"
    out = tpl.replace("{bucket}", b)
    for m in re.findall(r"\{record:([^}]+)\}", out):
        val = doc.get(m)
        if not isinstance(val, str) or not val.strip():
            return None, f"the record has no usable `{m}` to locate the outputs"
        out = out.replace("{record:%s}" % m, val.strip().strip("/"))
    return out.rstrip("/"), ""


def s3_lister(uri: str):
    """`[(key, mtime_epoch)]` under an `s3://bucket/prefix`. The ONLY object-store read in this module.

    ⚠ IT RETURNS `LastModified`, WHICH IS WHY IT IS NOT `object_store.ObjectStore.list` — that returns keys
    only, and a key without an mtime cannot answer "did THIS rental write it", which is the entire question
    RULE 2 (d) asks. Imported lazily so a plan, a dry run and every test run with no boto3."""
    import boto3
    body = uri.split("://", 1)[1] if "://" in uri else uri
    bucket, _, prefix = body.partition("/")
    cl = boto3.client("s3", endpoint_url=os.environ.get("OBJECT_STORE_ENDPOINT") or None,
                      region_name=os.environ.get("OBJECT_STORE_REGION") or os.environ.get(
                          "AWS_DEFAULT_REGION") or None)
    out = []
    for page in cl.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for o in page.get("Contents") or []:
            lm = o.get("LastModified")
            out.append((o["Key"], lm.timestamp() if lm is not None else None))
    return out


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the per-instance verdict — PURE over already-gathered evidence
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
REAP = "REAP"
SPARE = "SPARE"


def classify_instance(inst: dict, *, terminal: frozenset[str], banked=None) -> dict:
    """One census instance -> `{action, rule, why, ...}`. PURE.

    `banked` is RULE 2's already-gathered evidence for THIS instance, or None when none was gathered. It is an
    argument rather than something looked up here so that every branch is testable with no network, no object
    store and no filesystem — the property that let `account_orphan_alarm`'s controls find real bugs.

    ORDER IS THE ARGUMENT:
      1. RULE 1 first, because it is the rule that cannot be wrong. A terminal host has no work to lose, so no
         evidence gathered afterwards could change the answer.
      2. RULE 2 second, and only on positive, measured, correctly-attributed evidence.
      3. Everything else SPARES. There is no third rule and no default-reap path.
    """
    v: dict = {
        "instance": inst.get("id"),
        "machine_id": inst.get("machine_id"),
        "label": inst.get("label"),
        "gpu_name": inst.get("gpu_name"),
        "actual_status": inst.get("actual_status"),
        "cur_state": inst.get("cur_state"),
        # Quoted from the census, never recomputed (§1). These are what the ledger latches at destroy.
        "uptime_h": inst.get("uptime_h"),
        "dph_total": inst.get("dph_total"),
        "spend_so_far_usd": inst.get("spend_so_far_usd"),
        "start_date": inst.get("start_date"),
        "start_et": _et(_dt(inst.get("start_date"))),
    }

    # ── RULE 1 ──────────────────────────────────────────────────────────────────────────────────────────
    if is_terminal(inst, terminal):
        v["action"], v["rule"] = REAP, "RULE-1-TERMINAL"
        v["why"] = (
            f"actual_status={inst.get('actual_status')!r} cur_state={inst.get('cur_state')!r} is TERMINAL "
            f"(derived set: {sorted(terminal)}). A terminal host is not coming back, so anything it produced "
            f"is already in the object store or was never written — THIS RULE CANNOT LOSE WORK BY "
            f"CONSTRUCTION. It still appears in `GET /instances/`, and a host cannot end its own rental "
            f"(§6: only the control plane can), so it persists until something destroys it. Nothing did: the "
            f"owning lane's `mode=reap` ran, exited SUCCESS, and destroyed neither this nor a finished host.")
        return v

    # ── RULE 2 ──────────────────────────────────────────────────────────────────────────────────────────
    if banked and banked.get("banked") is True:
        v["action"], v["rule"] = REAP, "RULE-2-WORK-BANKED"
        v["evidence"] = banked
        v["why"] = (
            f"this host's unit is recorded DONE and its output is VERIFIED PRESENT in the object store: "
            f"{banked.get('why')}. The completion record was attributed to THIS rental by timestamp "
            f"({banked.get('attribution_why')}), which is the guard whose absence destroyed 46459452 "
            f"mid-image-pull. There is no remaining role for this box and it is billing.")
        return v

    # ── everything else ─────────────────────────────────────────────────────────────────────────────────
    v["action"], v["rule"] = SPARE, "NO-RULE-FIRED"
    if banked:
        v["evidence"] = banked
    v["why"] = (banked or {}).get("why") or (
        "not terminal, and no verified banked-work evidence attributes a completed unit to this rental. "
        "SPARED. ⚠ NOTE WHAT IS *NOT* A REASON TO REAP HERE: this box may read `gpu_util: 0.0` and may have "
        "been up for many hours, and NEITHER is evidence of anything — both selcal boxes read 0.0 including "
        "the one that was working, and a healthy fan-out leg legitimately runs for many hours. Only the two "
        "rules above may destroy.")
    return v


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the plan — PURE over an already-loaded census
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def build_plan(census: dict | None, census_err: str | None, now: datetime.datetime, *,
               terminal: frozenset[str], terminal_notes: list[str] | None = None,
               banked_by_instance: dict | None = None,
               census_stale_min: float = DEFAULT_CENSUS_STALE_MIN,
               future_skew_min: float = DEFAULT_FUTURE_SKEW_MIN,
               armed: bool = False) -> dict:
    """PURE. The whole reap plan from already-loaded state. NOTHING here calls an API or touches a lane.

    ★★ FAIL CLOSED BEFORE ANY INSTANCE IS GRADED. Four absences, all of which a naive reaper renders as "there
    is nothing to do", and every one of which is really "I do not know":

        census unreadable       -> NOTHING is planned. `reap` is null, not [].
        census stamp unreadable -> NOTHING is planned. An undateable census is not a fresh one.
        census stale            -> NOTHING is planned. It may describe hosts that no longer exist and miss
                                   ones that now do. Measured 155 min stale earlier today.
        census stamped ahead    -> NOTHING is planned. A negative age passes every staleness test forever.
        terminal set incomplete -> RULE 1 is DISABLED (not silently narrowed), and the plan says so.

    `reap`/`spare` are `null` on every fail-closed path and never `[]`, for the reason `_ungraded` records in
    the alarm: `[]` reads as "I looked and found none", which is the opposite fact.
    """
    plan: dict = {
        "_what": ("ACCOUNT-KEYED CENTRAL REAPER — the one thing in the repo that destroys Vast hosts on a "
                  "narrow, provably-safe predicate, keyed on the account so no lane's private teardown bug "
                  "can leave a box billing. RULE 1: terminal state, unconditional. RULE 2: unit recorded "
                  "done AND its output verified present in the object store, attributed to THIS rental by "
                  "timestamp. Nothing else may destroy."),
        "generated_utc": _z(now), "generated_et": _et(now),
        "mode": "ARMED" if armed else "DRY-RUN",
        "thresholds": {"census_stale_min": census_stale_min, "future_skew_min": future_skew_min},
        "terminal_states": sorted(terminal),
        "terminal_states_derived_from": list(terminal_notes or []),
        "never_reaps_on": ["gpu_util", "age/uptime", "a stale or unreadable census",
                           "a `done` record older than the instance"],
    }

    def _closed(verdict: str, detail: str) -> dict:
        plan["verdict"], plan["ok"], plan["graded"] = verdict, False, False
        plan["detail"] = detail
        plan["reap"] = None      # null, NEVER []. See the docstring: those are opposite facts.
        plan["spare"] = None
        plan["n_reap"] = None
        return plan

    if census is None:
        return _closed("CENSUS-UNKNOWN",
                       f"the account census could not be read ({census_err or 'unknown'}), so NOTHING is "
                       f"planned and NOTHING is destroyed. An absent reading is not a reading of absence "
                       f"(§4): 'I cannot see any instance' and 'there is no instance' are opposite facts, and "
                       f"for a REAPER the second one is not even the safe one — it means acting blind.")

    c_utc = parse_z(census.get("utc"))
    c_age = None if c_utc is None else (now - c_utc).total_seconds() / 60.0
    plan["census_utc"], plan["census_et"] = _z(c_utc), _et(c_utc)
    plan["census_age_min"] = round(c_age, 1) if c_age is not None else None
    plan["census_n_instances"] = census.get("n_instances")

    if c_utc is None:
        return _closed("CENSUS-UNKNOWN",
                       "the account census carries no parseable `utc`, so its age is unknown and it cannot be "
                       "evidence of what the account holds RIGHT NOW. An undateable census is not a fresh "
                       "one. NOTHING is planned.")
    if c_age is not None and c_age < -future_skew_min:
        return _closed("CENSUS-UNKNOWN",
                       f"the account census is stamped {_et(c_utc)}, {-c_age:.0f} min IN THE FUTURE "
                       f"(tolerance {future_skew_min:.0f} min). A future stamp is not a fresh census — it is "
                       f"an unbelievable reading, and a negative age would pass every staleness test forever, "
                       f"silently letting this module act on an arbitrarily old view. NOTHING is planned.")
    if c_age is not None and c_age >= census_stale_min:
        return _closed("CENSUS-STALE",
                       f"the account census is {c_age:.0f} min old (stamped {_et(c_utc)}; threshold "
                       f"{census_stale_min:.0f} min), so it is not treated as a weaker reading — it is not "
                       f"treated as a reading at all, and NOTHING is destroyed. Measured earlier today: it "
                       f"went 155 min stale, a window in which a naive check reads an empty fleet while two "
                       f"hosts bill. For a reaper the danger is sharper than for an alarm: a lane that "
                       f"relaunched inside the gap would have its NEW box judged on its OLD box's state.")

    insts = census.get("instances")
    if not isinstance(insts, list):
        return _closed("CENSUS-UNKNOWN",
                       "the account census has no `instances` list, so what the account holds is unknown. An "
                       "unparseable census is not an empty account. NOTHING is planned.")

    if not terminal:
        plan["rule_1_disabled"] = (
            "RULE 1 IS DISABLED: the terminal-state set could not be derived from the lanes that define it "
            f"({'; '.join(terminal_notes or ['no note'])}). It is NOT silently narrowed to nothing — an "
            "unreadable definition is not an empty one (§4), so the rule that would act on it does not run.")

    banked_by_instance = banked_by_instance or {}
    graded = []
    for inst in insts:
        if not isinstance(inst, dict):
            continue
        graded.append(classify_instance(inst, terminal=terminal,
                                        banked=banked_by_instance.get(str(inst.get("id")))))

    plan["graded"] = True
    plan["reap"] = [g for g in graded if g["action"] == REAP]
    plan["spare"] = [g for g in graded if g["action"] == SPARE]
    plan["n_reap"] = len(plan["reap"])
    plan["ok"] = True
    plan["verdict"] = "REAP" if plan["reap"] else "NOTHING-TO-REAP"
    plan["detail"] = (
        f"{len(graded)} instance(s) graded; {len(plan['reap'])} match a reap rule "
        f"({', '.join(sorted({g['rule'] for g in plan['reap']})) or 'none'}), {len(plan['spare'])} spared. "
        f"{'ARMED — these will be destroyed.' if armed else 'DRY-RUN — nothing will be destroyed.'}")
    return plan


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# execution — the ONLY impure, irreversible part
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _ledger_line(row: dict, now: datetime.datetime, *, mode: str, outcome: str, extra=None) -> dict:
    """One durable ledger record for a host we are about to destroy (or would).

    ★★ WRITTEN **BEFORE** THE DELETE, ALWAYS. The instance record is the only place billed hours exist, and it
    stops existing the moment the DELETE lands. A rental that billed and left no trace has already happened
    here, so the ordering is the whole point of the function: latch first, act second. The figures are the
    census's OWN (§1) — this module never recomputes a rate.
    """
    line = {
        "utc": _z(now), "et": _et(now), "mode": mode, "outcome": outcome,
        "instance": row.get("instance"), "machine_id": row.get("machine_id"), "label": row.get("label"),
        "gpu_name": row.get("gpu_name"), "rule": row.get("rule"),
        "actual_status": row.get("actual_status"), "cur_state": row.get("cur_state"),
        # BILLED-AT-DESTROY, quoted from the census row, latched here because after the DELETE there is
        # nothing left to read them from.
        "billed_hours_at_destroy": row.get("uptime_h"),
        "dph_total_at_destroy": row.get("dph_total"),
        "spend_so_far_usd_at_destroy": row.get("spend_so_far_usd"),
        "start_date": row.get("start_date"), "start_et": row.get("start_et"),
        "why": row.get("why"),
    }
    if extra:
        line.update(extra)
    return line


def append_ledger(path: str | None, line: dict) -> None:
    """Append one JSONL record and FLUSH + FSYNC IT. Never raises — a ledger failure must not stop a reap and
    must not be silent either; the caller surfaces `_ledger_error`.

    ⚠ THE FLUSH IS LOAD-BEARING. This is called immediately before an irreversible API call; a buffered line
    lost to a crash mid-destroy is exactly the "billed and left no trace" case the ledger exists to prevent.
    """
    if not path:
        return
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "a") as fh:
        fh.write(json.dumps(line, sort_keys=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def execute(plan: dict, now: datetime.datetime, *, armed: bool, ledger_path: str | None = None,
            destroy=None) -> dict:
    """Carry out the plan. `destroy(instance_id) -> None` is injected so every test drives the REAL control
    flow — including the ledger-before-delete ordering — with no network and no key.

    ⚠ A FAIL-CLOSED PLAN IS NEVER EXECUTED, whatever `armed` says. `graded` is checked here as well as in the
    caller, because the guarantee has to hold for anyone who imports this function.
    """
    out = {"mode": "ARMED" if armed else "DRY-RUN", "destroyed": [], "failed": [], "ledger": ledger_path}
    if not plan.get("graded"):
        out["skipped_why"] = (f"the plan is fail-closed ({plan.get('verdict')}), so nothing is executed. "
                              f"{plan.get('detail')}")
        return out
    for row in plan.get("reap") or []:
        iid = row.get("instance")
        if not armed:
            append_ledger(ledger_path, _ledger_line(row, now, mode="DRY-RUN", outcome="WOULD-DESTROY"))
            out["destroyed"].append({"instance": iid, "rule": row.get("rule"), "outcome": "WOULD-DESTROY"})
            continue
        # ── LATCH FIRST. The DELETE below is the last moment this instance record exists. ──
        append_ledger(ledger_path, _ledger_line(row, now, mode="ARMED", outcome="DESTROY-ATTEMPTED"))
        try:
            destroy(iid)
        except Exception as e:                                    # noqa: BLE001 — every failure is reported
            append_ledger(ledger_path, _ledger_line(row, now, mode="ARMED", outcome="DESTROY-FAILED",
                                                    extra={"error": f"{type(e).__name__}: {e}"}))
            out["failed"].append({"instance": iid, "rule": row.get("rule"),
                                  "error": f"{type(e).__name__}: {e}"})
            continue
        append_ledger(ledger_path, _ledger_line(row, now, mode="ARMED", outcome="DESTROYED"))
        out["destroyed"].append({"instance": iid, "rule": row.get("rule"), "outcome": "DESTROYED"})
    return out


def vast_destroy(instance_id) -> None:
    """DELETE /instances/<id>/ — the ONLY destructive call in this module, isolated so it is the only thing a
    test has to refuse to let happen. Imports `gpu_backend` lazily so that a plan, a dry run and every test
    can run with no key, no network and no boto3."""
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise RuntimeError("armed reap needs VAST_API_KEY — only the control plane can stop the meter (§6).")
    from gpu_backend import _vast_request
    _vast_request("DELETE", f"/instances/{instance_id}/", key)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# readout
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def render(plan: dict, result: dict | None = None) -> str:
    """Human readout. Times US Eastern 12-hour (§1) — `_et` is the only formatter used anywhere here."""
    L = [f"═══ ACCOUNT-KEYED CENTRAL REAPER — {plan.get('verdict')} [{plan.get('mode')}] ═══",
         f"as of {plan.get('generated_et')}"]
    if plan.get("census_et"):
        L.append(f"account census: {plan.get('census_n_instances')} instance(s), stamped "
                 f"{plan['census_et']} ({plan.get('census_age_min')} min old)")
    L.append(f"terminal set (derived): {plan.get('terminal_states')}")
    for n in plan.get("terminal_states_derived_from") or []:
        L.append(f"    from {n}")
    if plan.get("rule_1_disabled"):
        L.append(f"⚠ {plan['rule_1_disabled']}")
    if plan.get("rule_2_lanes") is not None:
        _r2 = plan["rule_2_lanes"] or "(none — RULE 2 is inert; RULE 1 covers every lane)"
        L.append(f"RULE 2 lanes registered: {_r2}")
    if plan.get("rule_2_disabled"):
        L.append(f"⚠ {plan['rule_2_disabled']}")
    L.append("")
    if not plan.get("graded"):
        L.append(f"⛔ FAIL-CLOSED — {plan.get('verdict')}: {plan.get('detail')}")
        L.append("   NOTHING WAS DESTROYED.")
        return "\n".join(L)
    for row in plan.get("reap") or []:
        L.append(f"☠ REAP   {row['instance']}  {row['gpu_name']}  "
                 f"{row['actual_status']}/{row['cur_state']}  {row['label']}")
        L.append(f"          rule={row['rule']}  uptime={row['uptime_h']}h  "
                 f"dph=${row['dph_total']}  billed=${row['spend_so_far_usd']}")
        L.append(f"          {row['why']}")
    for row in plan.get("spare") or []:
        L.append(f"  spare  {row['instance']}  {row['gpu_name']}  "
                 f"{row['actual_status']}/{row['cur_state']}  {row['label']}")
        L.append(f"          {row['why']}")
    L.append("")
    L.append(f"VERDICT: {plan.get('detail')}")
    if result:
        for d in result.get("destroyed") or []:
            L.append(f"   {d['outcome']}  {d['instance']}  ({d['rule']})")
        for f in result.get("failed") or []:
            L.append(f"   ⚠ DESTROY FAILED  {f['instance']}  ({f['rule']}): {f['error']}")
        if result.get("skipped_why"):
            L.append(f"   {result['skipped_why']}")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=HERE, help="repo dir holding the census and the lane sources")
    ap.add_argument("--census", default=None, help="path to ternary-vast-account-census.json")
    ap.add_argument("--json", dest="out", default=None, help="write the full plan here")
    ap.add_argument("--ledger", default=None, help="JSONL ledger; billed hours are latched here BEFORE any "
                                                   "DELETE, because that is the last moment they exist")
    ap.add_argument("--arm", action="store_true",
                    help="ACTUALLY DESTROY. Without this the reaper plans and reports and calls nothing.")
    ap.add_argument("--now", default=None, help="ISO8601Z override, for tests")
    ap.add_argument("--census-stale-min", type=float, default=DEFAULT_CENSUS_STALE_MIN)
    ap.add_argument("--future-skew-min", type=float, default=DEFAULT_FUTURE_SKEW_MIN)
    ap.add_argument("--no-object-store", action="store_true",
                    help="do not read the object store. RULE 2 then cannot MEASURE 'work banked' and is "
                         "disabled; RULE 1 is unaffected.")
    a = ap.parse_args(argv)

    now = parse_z(a.now) if a.now else datetime.datetime.now(datetime.timezone.utc)
    if now is None:
        print(f"[account-reaper] --now {a.now!r} is not ISO8601Z", file=sys.stderr)
        return 2

    census_path = a.census or os.path.join(a.root, "ternary-vast-account-census.json")
    census, census_err = load_json(census_path)
    terminal, notes = terminal_states_from_source(a.root)

    # ⚠ RULE 2's lister is resolved HERE, once, and passed in — so `build_plan` stays pure and every branch
    # of the predicate is reachable in a test with no boto3, no credential and no network.
    lister = None if a.no_object_store else s3_lister
    banked = {}
    if isinstance(census, dict) and isinstance(census.get("instances"), list):
        for inst in census["instances"]:
            if not isinstance(inst, dict):
                continue
            ev = gather_banked_evidence(inst, root=a.root, lister=lister)
            if ev is not None:
                banked[str(inst.get("id"))] = ev

    plan = build_plan(census, census_err, now, terminal=terminal, terminal_notes=notes,
                      banked_by_instance=banked,
                      census_stale_min=a.census_stale_min, future_skew_min=a.future_skew_min,
                      armed=a.arm)
    plan["rule_2_lanes"] = [r["lane"] for r in WORK_RECORDS]
    if lister is None:
        plan["rule_2_disabled"] = ("RULE 2 IS DISABLED for this run: --no-object-store, so 'work banked' "
                                   "could only be taken from a JSON field, and a populated field is not a "
                                   "measured one (§4b). RULE 1 is unaffected.")
    result = execute(plan, now, armed=a.arm, ledger_path=a.ledger, destroy=vast_destroy)
    plan["execution"] = result

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
        with open(a.out, "w") as fh:
            json.dump(plan, fh, indent=1, sort_keys=False)
            fh.write("\n")

    print(render(plan, result))
    if not plan.get("graded"):
        return 1
    return 2 if result.get("failed") else 0


if __name__ == "__main__":
    raise SystemExit(main())
