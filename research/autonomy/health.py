#!/usr/bin/env python3
"""LOOP HEALTH AS A COMMITTED FILE — the eleven conditions of
`research/manuscripts/program/emc-autonomy-architecture.md` §5.2 (plus `stalls_are_named`, ADDED
2026-08-28 for AUT-PROP-029 and not yet in that table — see CONDITION_ORDER), in the
`alarm-state.json` idiom.

★★ WHY THIS EXISTS. §5.1 already covers ARTIFACT correctness — every gate in `./scripts/preflight.sh`
checks whether what the loop wrote is true. Nothing checks whether the LOOP IS WORKING. Those are
different failures and conflating them is how a loop passes its own tests while producing nothing:
a cycle that fires, writes a tidy negative, commits green and advances no live route is *indexed as
success* by every gate this repository owns. The architecture's own summary of the risk (§0): the
largest failure mode is "a loop that runs forever, commits daily, and advances nothing".

★ THE IDIOM IS DELIBERATELY `alarm_state.py`'s, NOT A NEW ONE. Same three properties, for the same
reason — a supervisor that has stopped cannot report that it stopped:
  `_generated_utc` / `_stale_after_utc` / `_stale_after_means`  — the file carries its OWN expiry, so a
  reader who opens it can tell it is dead without running anything, without an API and without a clock
  but their own;
  per-condition `bad_since_utc` / `consecutive_bad_runs`  — "has this been red all night?" is the first
  question anyone opening the board will have, and a snapshot cannot answer it;
  `unmeasured` kept APART from `needs_attention`  — different problem, different fix.

⛔⛔ THE ONE RULE THIS FILE IS BUILT AROUND: **A CONDITION THAT COULD NOT BE MEASURED IS `unmeasured`,
NEVER `ok`.** CLAUDE.md §4: *an absent reading is not a reading of absence, and a populated field is not
a measured one.* Zero receipts does not mean the loop is delivering — it means nothing has reported.
An absent `publication-authority.json` does not mean authority was respected — it means there is
nothing to check acts against. A missing `route_advanced` field does not mean a route advanced.
Every one of those, graded the other way, produces a GREEN BOARD BUILT FROM MISSING DATA, which is
precisely the failure this repository has already paid for: env-echoed defaults once carried a
fabricated verdict all the way out, and a "FRESH-API-UNREADABLE" row graded as an outage produced the
2026-07-27 false alarm graded the other way. So `ok`, `unmeasured` and `needs_attention` are three
states here, constructed by three DIFFERENT functions (`_green` / `_unmeasured` / `_red`) rather than
by one function with a boolean, because a single constructor is one typo away from collapsing the
distinction — and `systems/tests/test_autonomy_health.py` mutation-tests exactly that collapse.

⭐ NO WORK, NO COMMIT — `fleet_armed.py`'s discipline, ported (measured cost of ignoring it: 1,476
commits in 24 h, 703 of which said in their own subject line that they did nothing). `commit_worthy()`
answers whether this board SAYS anything the committed one did not. ⛔ And it keeps the other half of
that lesson too: a board that stops refreshing must not read as a board that keeps saying "fine", so
the answer is also yes whenever the committed copy is about to age past its own staleness window.

WHAT IT NEVER DOES: no network, no model, no subprocess, no push channel of any kind. Pure stdlib and
deterministic — the same inputs give the same board, so a diff in `health.json` is a change in the LOOP,
never in the checker. It cannot fail a run either: `--write` and the default render always exit 0,
because a red run emails the repo owner and that is the push channel `alarm_state.py` exists to remove.
`--check` is the opt-in non-zero exit, for a caller that wants the gate.

Usage:
    python3 research/autonomy/health.py                 # the board, as a table
    python3 research/autonomy/health.py --write         # (re)write research/autonomy/health.json
    python3 research/autonomy/health.py --check         # exit 1 if any condition needs attention
    python3 research/autonomy/health.py --escalations   # exit 1 if a restart budget is spent (§3)
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import sys

ET = datetime.timezone(datetime.timedelta(hours=-4))  # EDT. CLAUDE.md §1: US Eastern, 12-hour, always.

HERE = os.path.dirname(os.path.abspath(__file__))

# ⛔ THE FAN-OUT KEY IS IMPORTED, NEVER SPELLED, AND THAT IS THE WHOLE OF AUT-PD-013's FIX. This file
# read `subagents.max_concurrent`; the receipts wrote `concurrent_max`, then `max_concurrent` again,
# then `launched` — three schemas in seventeen receipts — so the row guarding the width dial reported
# a FALSE ABSENCE for cycles whose fan-out was recorded plainly, under another name. A name agreed in
# prose between a writer and a reader is not agreed at all. `receipt_schema` owns it for both sides,
# and `scripts/preflight.sh` checks the writer against it at the commit.
# ⛔ THE HANDOFF KEY IS IMPORTED TOO, FOR THE SAME REASON (AUT-PD-017). This file used to re-derive
# `receipt.get("handoff", {}).get("child_session_id")` inline -- the name AND the traversal spelled
# a second time, agreed with `handoff.py` only by never being touched. `handoff.py` owns both sides
# of that read now (`CHILD_ID_FIELD` and `child_session_id_of`); this file calls the function.
# ⛔ `stuck_clock` IS IMPORTED TOO, AND ONLY FOR ITS ONE CONSTANT (`TERMINAL_STATE`) — NEVER FOR ITS
# FUNCTIONS (AUT-PROP-029, wiring it in). Importing a module only executes its top-level definitions;
# every one of stuck_clock's `git` calls lives inside a function body and none is invoked here, so
# this stays true to "no subprocess" below. What it buys is "one fact, one place" for the string
# `"stalled_needs_human"` — the same reason `receipt_schema.ROUTE_ADVANCED_KEY` is imported rather
# than retyped, and the same class of drift AUT-PD-013 found when a name agreed only in prose moved.
sys.path.insert(0, HERE)
import receipt_schema  # noqa: E402
import handoff  # noqa: E402
import stuck_clock  # noqa: E402
DEFAULT_LEDGER = os.path.join(HERE, "research-ledger.json")
DEFAULT_STATE = os.path.join(HERE, "autonomy-state.json")
DEFAULT_RECEIPTS = os.path.join(HERE, "receipts")
DEFAULT_HEALTH = os.path.join(HERE, "health.json")
DEFAULT_AUTHORITY = os.path.join(HERE, "publication-authority.json")

#: The TEN §5.2 conditions, in the order the architecture table lists them, PLUS `stalls_are_named`
#: (AUT-PROP-029, ADDED 2026-08-28, not yet in that table — the same shape `queue_is_takeable`,
#: `cycles_are_sized` and `fanout_is_governed` arrived through). Renaming or dropping one is a "free,
#: but DECLARED" edit under §10.4 — it changes what "doing well" MEANS — so it goes in the amendment
#: log, never silently.
CONDITION_ORDER = (
    "cycle_delivering",
    "advancing_live_work",
    "evidence_moving",
    "blocks_are_real",
    "queue_is_takeable",
    "scores_are_reachable",
    "cycles_are_sized",
    "fanout_is_governed",
    "budget_recovering",
    "gates_green",
    "authority_respected",
    "stalls_are_named",
)

#: ⛔⛔ WHAT A RED MEANS FOR THE LOOP — THE CONTRACT THAT WAS IMPLIED, NEVER STATED, AND BROKEN THE
#: HOUR IT WAS FIRST TESTED (2026-08-27). `research-loop` §1 says a cycle REFUSES TO START while any
#: §5.2 condition is red. Every condition written before that day happened to be one a cycle could
#: ACT on, so the rule worked by luck rather than by design. Then two conditions were added whose
#: subject is IMMUTABLE COMMITTED HISTORY — `cycles_are_sized` and `fanout_is_governed` both read
#: every receipt ever written — and no future cycle in any session could ever clear them.
#: MEASURED: the driver Routine fired, read a red board, refused to start, and pushed
#: "health check permanently red, needs your call". The loop was dead, permanently, and the author of
#: both conditions had looked at that red row a dozen times and called it working as intended.
#:
#: ⭐ SO THE CLASSIFICATION IS NOW EXPLICIT AND EVERY CONDITION MUST CARRY ONE:
#:   "blocks"    a cycle MUST NOT start. Continuing could compound real harm.
#:   "redirects" the cycle still runs — fixing this IS its work for this cycle.
#:   "advises"   report, escalate if it persists, but NEVER stop the loop. Anything a cycle cannot
#:               act on belongs here, and that includes every retrospective observation about what
#:               already happened.
#: ⛔ `--check` exits non-zero ONLY for a red `blocks` row. A red that stops a loop it cannot teach
#: to recover is not a safety feature; it is an outage with a virtuous name.
#: ⛔ HOW FAR BACK A RETROSPECTIVE CONDITION LOOKS, AND WHY IT MUST NOT BE "ALL OF HISTORY".
#: `cycles_are_sized` and `fanout_is_governed` judge receipts, and a receipt is immutable committed
#: history — so reading every receipt ever written makes the row LATCH: once true, true forever, with
#: no action in any future session able to clear it. Proven 2026-08-27 by simulation before the fix:
#: fifty consecutive well-behaved sessions left both rows red.
#: ⚠ A LATCHED ROW IS NOT MERELY USELESS, IT IS CORROSIVE — it is the muted alarm this repository has
#: already paid for once (every push channel stripped from lane-staleness-watch.yml after 1,476
#: commits in 24 h). A row that can never go green teaches every reader to skip it, and it takes the
#: rows that CAN go green down with it.
#: ⭐ So both look only at the most recent RECEIPT_WINDOW receipts. Good behaviour clears them; the
#: permanent record of what happened stays where it belongs, in the receipts themselves.
#: The window is > `max_cycles_per_session` on purpose: smaller and an overrun would scroll out of
#: view before anyone saw it.
RECEIPT_WINDOW = 6

#: ⛔ HOW EACH RECEIPT-READING CONDITION AVOIDS LATCHING — DECLARED, NOT INFERRED.
#: A first attempt at guarding this SCRAPED THIS FILE'S SOURCE for slicing patterns and got two of
#: four wrong: it accused `advancing_live_work` (which reads `receipts[-NO_ADVANCE_RUN:]`, a tail run)
#: and `authority_respected` (whose red is cleared by a human adding the grant) of being latched, and
#: nearly "fixed" two things that were never broken. A property a reader must infer from code shape is
#: a property nobody has actually stated. So each condition says how it recovers, here, once.
#:   "windowed"           reads only the last RECEIPT_WINDOW receipts
#:   "newest-run"         reads only a tail run, which the next receipt displaces
#:   "cleared-by:<path>"  a red is cleared by an edit to that file — the recovery path for the one
#:                        condition that BLOCKS, and it is deliberately a HUMAN's edit (§6.3: the loop
#:                        may never self-issue a grant)
RECEIPT_SCOPE = {
    "cycle_delivering": "newest-run",
    "advancing_live_work": "newest-run",
    "cycles_are_sized": "windowed",
    "fanout_is_governed": "windowed",
    "authority_respected": "cleared-by:research/autonomy/publication-authority.json",
}

CONDITION_ON_RED = {
    # A cycle that runs and writes a receipt IS the cure — blocking would be a death spiral.
    "cycle_delivering": "advises",
    "advancing_live_work": "advises",
    "evidence_moving": "advises",
    # A cycle can add the missing observation, release the stale claim, fix the trunk.
    "blocks_are_real": "redirects",
    "queue_is_takeable": "redirects",
    # ⛔⛔ "advises", AND THE ALTERNATIVE IS THE DEATH SPIRAL THIS TABLE'S OWN COMMENT NAMES.
    # `scores_are_reachable` counts OPEN rows the ranker cannot rank at all (AUT-PD-143). On the
    # ledger it was written against that is 66 rows, and 69 of the 84 unscorable rows serve
    # RT-AUTONOMY — which is not a route in systems/graph, so no pass can ever derive a floor for
    # them. "redirects" would hand every cycle from here the same unfixable errand instead of the
    # research; "blocks" would stop the loop on a condition no cycle can clear, which is precisely
    # what `cycles_are_sized` and `fanout_is_governed` did the day the loop died. The row is a
    # READING, and its response is to be seen.
    "scores_are_reachable": "advises",
    "gates_green": "redirects",
    # ⛔ RETROSPECTIVE. Their subject is receipts already committed; no cycle can undo one. These are
    # the two that killed the loop, and "advises" is the whole of that fix's first half.
    "cycles_are_sized": "advises",
    "fanout_is_governed": "advises",
    # The governor moves this on its own schedule; a cycle taking free items is the documented answer.
    "budget_recovering": "advises",
    # ⛔ THE ONE GENUINE STOP. An outward act with no grant behind it is the permission this loop may
    # never self-issue (§6.3), and another cycle could compound it. This is what "blocks" is for.
    "authority_respected": "blocks",
    # ⛔⛔ ALSO "advises", AND ARGUED RATHER THAN ASSUMED (AUT-PROP-029). stuck_clock's terminal
    # verdict means exactly one thing: automation retried this SPECIFIC row for
    # `stuck_clock.STUCK_AFTER_CYCLES` cycles and NOTHING it did advanced it — the row was claimed,
    # abandoned, re-queued and re-claimed while looking maximally alive. "redirects" would tell the
    # SAME automation to try harder THIS cycle, which is precisely the busy-retry loop the module
    # exists to unmask, rebuilt one level up. It is not a well-defined mechanical fix the way
    # `blocks_are_real` (add the missing $0 observation) or `queue_is_takeable` (release a stale
    # claim) are — stuck_clock's own docstring names three genuinely different human answers
    # (re-scope it, hand it to a different route, or close it), and choosing among them is exactly
    # the judgement call automation already failed to make across every one of those cycles. Nor can
    # it ever be "blocks": another cycle continuing does not compound harm on THIS row the way an
    # ungranted outward act does, and every OTHER row in the queue is untouched by it. So it is
    # retrospective in the sense `cycles_are_sized`/`fanout_is_governed` are, but its recovery is not
    # RECEIPT_WINDOW's: the verdict is a LIVE property of the ledger's CURRENT state (the moment any
    # row advances — a real `what`/`blocked_evidence`/`state` resolution — stuck_clock recomputes
    # `stuck_at` from that advance and the row falls out of `terminal_rows()` on its own run), never
    # an ever-growing window of immutable history, so it needs no windowing against latching.
    "stalls_are_named": "advises",
}

# ═══════════════════════════════════ the three axes, and the one bug they exist to make catchable ══
#: ⛔⛔ WHAT `CONDITION_ON_RED` DOES NOT SAY, AND WHY A SECOND TABLE IS NOT A DUPLICATE OF IT.
#: `CONDITION_ON_RED` records what a red DOES to the loop. It says nothing about what the row is a
#: reading OF, and those are different questions with different failure modes. Kubernetes' own probe
#: documentation names the one this table exists to make catchable by machine
#: (`research/method-watch-autonomy-prior-art-2.md` §2, the "health board" row):
#:
#:   liveness   SELF ONLY. A red means the thing is DEAD; the right response is a restart.
#:   readiness  SELF **PLUS DEPENDENCIES**. A red means route work away, and **NEVER restart** —
#:              restarting cannot repair a dependency, and doing it on every replica at once sends a
#:              cold-start herd at the very dependency that just blipped. k8s' words:
#:              *"incorrect implementation of liveness probes can lead to cascading failures."*
#:   progress   IS WORK ADVANCING. Neither probe covers it; a process can be alive and ready and
#:              moving nothing, which is this loop's largest failure mode (§0).
#:
#: ⭐ THE AXIS IS NOT COSMETIC — IT IS THE PREDICATE `test_a_dependency_red_never_restarts_the_loop`
#: RUNS. Before this table the k8s failure mode could not be ruled out by inspection: eleven rows in
#: a flat list, none saying whether its subject was the loop's own pulse or somebody else's server.
#:
#: ⛔ WHAT A "RESTART" IS IN THIS REPOSITORY, STATED SO THE GUARD MEANS SOMETHING. There is no
#: container to kill. The two restart-shaped responses are:
#:   1. a cycle REFUSING TO START (`research-loop` §1, driven by `--check` exit 1, which fires on a
#:      red `blocks` row and nothing else) — the session ends, and the driver Routine's next firing
#:      spins up a FRESH session, which is a respawn in everything but name;
#:   2. a session's automatic hand-off/respawn (`handoff.py` building a child-session prompt).
#: Neither reads `health.json` to decide to respawn, so (2) is not wired to any condition. (1) is,
#: and it is wired to exactly one row — see READINESS_MAY_BLOCK.
CONDITION_AXIS = {
    # LIVENESS — the loop's own pulse, with nothing external in the reading. "Did a fired cycle
    # write a receipt?" is answerable from this repository alone. ⚠ And note the restart this axis
    # would prescribe is the one thing nothing here can do: the driver Routine lives in claude.ai,
    # so `stall_alarm.py`'s mail is the whole response, which is why this row is `advises`.
    "cycle_delivering": "liveness",
    # PROGRESS — these ask whether, and how, work moved. None is a statement about being alive or
    # about a dependency being up.
    "advancing_live_work": "progress",     # routes advanced, or documentation drift
    "evidence_moving": "progress",         # in-flight work producing new evidence, not heartbeats
    "stalls_are_named": "progress",        # stuck_clock's advance clock: a row retried and not moved
    # ⚠ THESE TWO ARE THE AWKWARD ONES AND THE TAG IS ARGUED, NOT ASSUMED. `cycles_are_sized` and
    # `fanout_is_governed` grade the SHAPE of work already done — a session that ran nine cycles was
    # alive, was ready, and did advance things. So they are neither liveness (a red does not mean
    # dead) nor readiness (a red does not mean route away). The axis is chosen on the operational
    # question the three tags actually answer — *does a red mean restart, route away, or report?* —
    # and for both the answer is report. ⛔ Tagging either LIVENESS would be the k8s bug in its worst
    # form here: the prescribed response to an over-wide fan-out would be to respawn and fan out
    # again, which is the 107-agent incident rebuilt as a policy.
    "cycles_are_sized": "progress",
    "fanout_is_governed": "progress",
    # READINESS — every one of these reads something the loop does not control, and for every one
    # the correct response is to route work away rather than to restart into it.
    "blocks_are_real": "readiness",        # a ledger row that is not takeable as written
    "queue_is_takeable": "readiness",      # the classic readiness question: can I accept work at all
    # READINESS for the same reason as the row above it, and for a second one that row does not
    # have: whether an open ledger row can be ranked at all depends on `systems/graph` carrying its
    # route, which is a DEPENDENCY outside the queue. A red says route work away from those rows;
    # it never says the loop is dead.
    "scores_are_reachable": "readiness",
    "budget_recovering": "readiness",      # the ACCOUNT's rate limit — restarting into it is the herd
    "gates_green": "readiness",            # GitHub Actions' verdict on the trunk. A pure dependency.
    "authority_respected": "readiness",    # publication-authority.json, which only a HUMAN may edit
}

AXES = ("liveness", "readiness", "progress")

#: ⛔⛔ THE ONE DECLARED EXCEPTION, AND THE AUDIT ANSWER IT RECORDS.
#: `authority_respected` is READINESS-shaped — half its reading is a grant file the loop is forbidden
#: to write (§6.3) — and it is the single row wired to `blocks`, this repository's refuse-and-respawn
#: response. By k8s' rule that is the bug. It is nonetheless CORRECT here, and the reason is a
#: property k8s' rule does not model: **k8s forbids restarting on a dependency because restarting
#: cannot FIX it. It has nothing to say about a dependency whose red means CONTINUING DOES
#: IRREVERSIBLE HARM.** An outward act with no grant behind it is the one permission this loop may
#: never self-issue, and another cycle could compound it under trimcrae's name and ORCID.
#: ⭐ SO THE EXCEPTION IS KEPT AND BOUNDED RATHER THAN REMOVED — which is exactly what the prior
#: art's next primitive is for. A refusal that repeats forever is still the cold-start herd, just
#: slowed to the driver Routine's period: fire, read the red board, refuse, die, fire again. The
#: bound is RESTART_INTENSITY below, and this table is what makes it MANDATORY: a readiness row may
#: be `blocks` only if it is declared here AND its refusals are counted.
READINESS_MAY_BLOCK = {
    "authority_respected": (
        "continuing compounds an irreversible outward act taken under a human's name (CLAUDE.md §3, "
        "architecture §6.3), which is a harm k8s' never-restart-on-a-dependency rule does not model. "
        "Bounded by RESTART_INTENSITY: after that many consecutive refusals the loop stops refusing "
        "silently and escalates to trimcrae."
    ),
}

# ═══════════════════════════════════════════════════════ restart intensity — OTP and systemd, ported
#: ⛔⛔ NEITHER OTP NOR SYSTEMD NOR KUBERNETES LETS A SUPERVISED THING FAIL FOREVER IN SILENCE, AND
#: THIS LOOP DID. Before this constant, a red `blocks` row produced: the driver Routine fires, the
#: cycle runs `--check`, gets exit 1, writes a receipt saying so, and stops — every cycle period,
#: indefinitely, with no counter anywhere and no rung above "another refusal". Verified 2026-08-28 by
#: grep over the whole repository: `restart_intensity`, `StartLimitBurst` and `max_restarts` matched
#: nothing in `research/autonomy/` — only prose mentions of escalation, no computed bound.
#:
#: ⭐ N IS TAKEN FROM THE PRIOR ART, NOT INVENTED. Three systems, read at their own documentation:
#:   systemd   `StartLimitBurst=`/`StartLimitIntervalSec=`, defaulting to `DefaultStartLimitBurst=`
#:             = **5** in `systemd-system.conf` (with `DefaultStartLimitIntervalSec=10s`). Past the
#:             burst systemd stops trying and the unit sits failed until a human intervenes.
#:   OTP       `intensity`/`period`, defaulting to **1 restart per 5 seconds**: *"if more than MaxR
#:             restarts occur within MaxT seconds, the supervisor terminates all child processes and
#:             then itself."*
#:   k8s       CrashLoopBackOff — the COUNTER-EXAMPLE. It backs the retries off, never stops, and
#:             never tells anybody, which is the behaviour this constant exists to not have.
#: ⭐ **5, systemd's number.** OTP's 1 is the tighter bound and is wrong here: a single transient red
#: — a board graded against a half-written ledger, a mid-cycle read — would escalate, and this
#: repository has already paid the full price for an alarm that cries too often (every push channel
#: stripped out of `lane-staleness-watch.yml` after 1,476 commits in 24 h; a muted alarm is worse
#: than none, because it also carries the belief that somebody is watching). 5 sits between OTP's 1
#: and k8s' infinity, and it is a number somebody else already defended.
#: ⚠ AND THE PERIOD IS NOT A SECOND PARAMETER HERE, DELIBERATELY. OTP and systemd need one because
#: they count restarts in a sliding window; this counts CONSECUTIVE reds, and consecutiveness is
#: already a window — one green or one unmeasured run resets it to zero. Adding a period on top could
#: only let a genuine, unbroken outage age out of its own alarm.
RESTART_INTENSITY = 5

#: ⛔ WHAT THE COUNTER'S UNIT ACTUALLY IS — STATED, BECAUSE THE HONEST ANSWER IS NOT THE OBVIOUS ONE.
#: The unit is ONE GRADING OF THIS BOARD (`autonomy-tick.yml` running `health.py --write`), not one
#: research cycle. That is a deliberate choice between two clocks:
#:   the CYCLE clock is the literal reading of "consecutive dispatches", and it is unusable — a cycle
#:     that refuses is not guaranteed to leave a receipt at all, and the case that most needs this
#:     bound is exactly the one where the loop has stopped producing anything;
#:   the TICK clock keeps running when the loop is dead, which is the entire reason `stall_alarm.py`
#:     lives on it (a supervisor sharing a clock with what it supervises cannot report that the clock
#:     stopped).
#: ⚠ SO N RUNS IS NOT N HOURS AND MUST NEVER BE REPORTED AS IF IT WERE. The tick's cron is a REQUEST,
#: not a cadence — delivered gaps of 125-222 min against a `*/15` are recorded in this repository's
#: own workflow headers — so N runs is a LOWER BOUND in wall-clock terms. `bad_for_h` is the measured
#: age and travels beside the count everywhere the count is reported.
RESTART_INTENSITY_UNIT = "board runs (autonomy-tick gradings)"

#: Which `on_red` classes are being RETRIED, and so can exhaust an intensity budget. An `advises` row
#: is retried by nothing — no caller acts on it — so counting its "refusals" would be counting an
#: event that does not occur. Those rows are already covered by `stall_alarm.py`, which mails on any
#: sustained red at its own, lower threshold.
RETRIED_ON_RED = ("blocks", "redirects")

#: §5.2 thresholds. Each is the doc's number, in one place, named after the row it governs.
CYCLE_MISS_PERIODS = 2.0        # "no receipt within 2 expected cycle periods"
EVIDENCE_FROZEN_PERIODS = 2.0   # "running with last_evidence_utc unchanged over 2 cycles"
NO_ADVANCE_RUN = 3              # "3 consecutive receipts with route_advanced: none"
BACKOFF_GRACE_H = 24.0          # "backoff level > 0 for > 24 h"
GATES_RED_GRACE_H = 24.0        # "preflight red on main for > 24 h"

#: How many expected cycle periods before the BOARD declares itself dead. Same multiple, and same
#: reasoning, as `alarm_state.STALE_AFTER_TICKS`: a human reads this deadline, so it has to be tight
#: enough to be worth reading, and a false "stale" costs one second look.
STALE_AFTER_CYCLES = 3.0

#: ⚠ USED ONLY WHEN `autonomy-state.json` CANNOT BE READ, AND THE BOARD SAYS SO WHEN IT IS USED. It is
#: a fallback, not a setting — the cycle interval's one home is the state file (§9.2's start point).
#: A number that looks derived and is not is worse than an admitted guess (`alarm_state` idiom).
FALLBACK_CYCLE_INTERVAL_H = 4.0


# ═════════════════════════════════════════════════════════════════════════════════ time, read not typed
def _z(ts):
    return ts.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None


def _et(ts):
    if ts is None:
        return None
    local = ts.astimezone(ET)
    # Numeric fields keep the same unpadded display without POSIX-only %-I / %-d.
    return f"{local.hour % 12 or 12}:{local:%M %p ET %b} {local.day}, {local:%Y}"


def _parse_ts(s):
    """UTC datetime, or None. ⚠ None means UNREADABLE and every caller must treat it as unmeasured.

    Three shapes are accepted because three already exist in the tree: the `%Y-%m-%dT%H:%M:%SZ` stamp
    `alarm_state`/`work_ledger` write, an ISO-8601 stamp with an explicit offset, and the DATE-ONLY
    `last_evidence_utc` the seeded `research-ledger.json` actually carries ("2026-08-08"). A date-only
    value is read as midnight UTC, which is the earliest instant it can mean — the conservative
    direction for a staleness test, since it can only make an entry look older, never fresher.
    """
    if not isinstance(s, str) or not s.strip():
        return None
    raw = s.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(raw, fmt).replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            pass
    try:
        dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)


def _hours(later, earlier):
    return (later - earlier).total_seconds() / 3600.0


def _is_empty(v):
    """Empty in the sense `blocked_evidence` means it: nothing was OBSERVED and recorded."""
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, (list, tuple, dict, set)):
        return not v
    return False


# ═════════════════════════════════════════════════════════════════ the three verdict states, kept apart
def _row(key, label, source, verdict, *, ok, unmeasured, detail, payload=None):
    # ⛔ The invariant, asserted rather than commented: ok and unmeasured are mutually exclusive, and
    # `needs_attention` is the third state — a MEASURED failure. A row that is both is the collapse
    # this module exists to prevent, and it must die here rather than reach a reader as a green board.
    assert not (ok and unmeasured), f"{key}: a row cannot be both ok and unmeasured"
    return {
        "key": key,
        "label": label,
        "source": source,
        "verdict": verdict,
        "ok": bool(ok),
        "unmeasured": bool(unmeasured),
        "needs_attention": (not ok) and (not unmeasured),
        "detail": detail,
        "payload": {k: v for k, v in (payload or {}).items() if v not in (None, "")},
    }


def _green(key, label, source, verdict, detail, payload=None):
    """MEASURED, and fine. Reachable only when the reading was actually taken."""
    return _row(key, label, source, verdict, ok=True, unmeasured=False, detail=detail, payload=payload)


def _red(key, label, source, verdict, detail, payload=None):
    """MEASURED, and failing. This is the state that escalates (§7 trigger 4)."""
    return _row(key, label, source, verdict, ok=False, unmeasured=False, detail=detail, payload=payload)


def _unmeasured(key, label, source, verdict, detail, payload=None):
    """⛔ NOT MEASURABLE — the reading could not be taken. NOT `ok`, and NOT `needs_attention` either.

    Separate from both on purpose, because the FIX is different: a red condition needs the loop fixed,
    an unmeasured one needs the reading made possible first. Collapsing it into `ok` is the failure
    mode named in the module docstring; collapsing it into `needs_attention` is the 2026-07-27 false
    alarm. `detail` must always name WHAT WOULD SETTLE IT — an unmeasured row that does not say how to
    become measurable is an unanswered question wearing the costume of a status (CLAUDE.md §4).
    """
    return _row(key, label, source, verdict, ok=False, unmeasured=True, detail=detail, payload=payload)


# ═════════════════════════════════════════════════════════════════════════════════════════════ inputs
def _read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, f"{os.path.basename(path)} is absent"
    except (OSError, json.JSONDecodeError) as e:
        return None, f"{os.path.basename(path)} is unreadable: {type(e).__name__}: {e}"


def load_receipts(receipts_dir=DEFAULT_RECEIPTS):
    """Every `<cycle-id>.json` in §4.2 step 10's directory, oldest first, plus the unreadable ones.

    ⚠ ORDER IS PART OF THE MEASUREMENT — `advancing_live_work` asks about the LAST THREE — so it is
    made deterministic rather than left to the filesystem: sort on the receipt's own end stamp, ties
    and missing stamps broken by filename. Cycle ids are timestamped, so filename order is the same
    order in practice; it is the tiebreak, not the source of truth.

    ⛔ A receipt that will not parse is returned in `unreadable`, never dropped. A cycle whose receipt
    is corrupt is not a cycle that did not run, and silently skipping it would let a broken writer
    read as a quiet loop.
    """
    receipts, unreadable = [], []
    for path in sorted(glob.glob(os.path.join(receipts_dir, "*.json"))):
        doc, err = _read_json(path)
        if err or not isinstance(doc, dict):
            unreadable.append(err or f"{os.path.basename(path)} is not a JSON object")
            continue
        doc = dict(doc)
        doc["_path"] = path
        doc["_file"] = os.path.basename(path)
        receipts.append(doc)
    receipts.sort(key=lambda r: (_receipt_ts_raw(r) or "", r["_file"]))
    return receipts, unreadable


#: Receipt timestamp keys, in precedence order. ⚠ §4.2 step 10 names the receipt's CONTENT ("what was
#: taken, what changed, what it cost, what is now queued, and route_advanced") but not its field names,
#: so these are this module's choice and the writer must match one of them. File mtime is deliberately
#: NOT a fallback: a fresh `git clone` rewrites every mtime, which would make an ancient receipt look
#: like this minute's — a populated field that is not a measured one (CLAUDE.md §4).
#: ⛔ THE FIRST NAME IS IMPORTED, NEVER SPELLED (AUT-PD-013's lesson, applied to the clock after it
#: cost seven false-red board runs on 2026-09-02). `receipt_schema.ENDED_KEY` owns the name for the
#: writer and the reader both, and `receipt_schema.py --check` refuses the commit that lands a
#: governed receipt without it. The four that follow are LEGACY SPELLINGS, retained read-only so the
#: 98 receipts written before the constant existed can still be dated -- they are not alternatives a
#: new receipt may choose, and `contract_check.py` will not let the contract offer them.
RECEIPT_TIME_KEYS = (receipt_schema.ENDED_KEY, "finished_utc", "generated_utc", "cycle_ended_utc",
                     "utc")


def _receipt_ts_raw(receipt):
    for key in RECEIPT_TIME_KEYS:
        v = receipt.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _receipt_ts(receipt):
    return _parse_ts(_receipt_ts_raw(receipt))


def _receipt_ordinal(receipt):
    """`CYC-0084-e2d78138` -> 84, or None when the id yields no ordinal.

    ⭐ A recency proxy that survives a missing clock, which is the only reason it is used here: it
    is read from the id the writer allocates, so a receipt nobody can DATE can still be ORDERED.
    Prefers the `cycle_id` field and falls back to the filename, the same precedence
    `receipt_schema.audit` uses, so both graders answer for the same receipt.
    """
    rid = receipt.get(receipt_schema.CYCLE_ID_KEY)
    if not isinstance(rid, str) or not rid.strip():
        rid = receipt.get("_file", "").removesuffix(".json")
    return receipt_schema.cycle_number(rid)


def _undatable_at_or_above(receipts, floor_ordinal):
    """Receipts this module can neither DATE nor rule out as newer than `floor_ordinal`.

    ⛔⛔ THE ONE OBSERVATION BOTH RECEIPT-READING CONDITIONS NEED, AND NEITHER USED TO TAKE. Both
    `c_cycle_delivering` and `c_advancing_live_work` answer by reading the TAIL of a list sorted on
    `(timestamp or "", filename)`. A receipt carrying no readable clock sorts to the FRONT of that
    list, so it is not merely undated — it is INVISIBLE to every reader of the tail, and the tail
    then describes older receipts while looking exactly like the newest ones.
    ⚠ MEASURED 2026-09-02: fifteen receipts carried `started_utc` and none of RECEIPT_TIME_KEYS.
    `cycle_delivering` aged CYC-0084 (four days stale) and printed a confident `LATE ... 103.5 h`
    while CYC-0091 sat 2.7 h old; `advancing_live_work` read CYC-0082/0083/0084, all
    `route_advanced: none`, and printed NOT-ADVANCING — while the real newest three were RT-ASO,
    none, RT-ASO, which is not a run of three and is GREEN. One field name, two false reds, seven
    and twenty consecutive board runs respectively.
    ⭐ THE ORDINAL IS WHAT MAKES THIS NON-LATCHING. Grading on "any clockless receipt anywhere"
    would freeze both rows forever, because those fifteen are immutable committed history — the
    failure that killed the loop on 2026-08-27. An ordinal is a recency proxy read from the id
    rather than the clock, so the question stays narrow and answerable: could an undatable receipt
    be newer than the ones I am about to read? Once governed receipts carry `ended_utc` the readable
    ordinals climb past every clockless one and both rows recover unaided.
    ⛔ AN UNREADABLE ORDINAL COUNTS AS "COULD BE NEWER" on both sides. A receipt this module can
    neither date nor order is exactly the thing that must not be skipped in silence.

    ⛔⛔ AND THE OBVIOUS SHORTCUT — "just read `started_utc`, a start is never after an end, so it can
    only ever read PESSIMISTIC" — IS REFUSED, ON A MEASUREMENT THAT SAYS OTHERWISE. It is the first
    thing every reader of this row proposes, so the refutation lives here rather than in a commit
    message. `receipt_schema.ENDED_KEY`'s own comment argues it for the AGE; these are the two halves
    a reader has to check separately, because the two conditions do not compute the same kind of
    thing from the stamp.
      · `c_cycle_delivering` computes a MAGNITUDE, `now - ts`, and reds when it exceeds the deadline.
        Its direction argument would hold IF `started_utc <= ended_utc` held — an overstated age can
        only manufacture a false RED. ⚠ BUT THE PREMISE IS FALSE AND IT WAS MEASURED, TWICE
        INDEPENDENTLY (2026-09-02): over all 30 committed receipts carrying `started_utc`, against
        the author date of the commit that ADDED each one — the only delivery time this repository
        records — the lag is median +0.48 h, mean +0.76 h, max +7.97 h, and MIN −0.49 h, with THREE
        of the 30 NEGATIVE (CYC-0007 −0.20 h, CYC-0010 −0.32 h, CYC-0012 −0.49 h). A negative lag is
        a receipt whose typed start is LATER than its own delivery, so the age is UNDERSTATED and the
        row reads FRESHER than the truth. That is the manufactured-freshness direction, and the field
        is hand-typed, so the error has no bound to appeal to.
      · `c_advancing_live_work` computes an IDENTITY — which three receipts are the newest — and no
        direction argument reaches it AT ALL, even if the premise held. A lower-bound stamp depresses
        a receipt's sort position, so a genuinely newer receipt drops out of the tail and a genuinely
        older one drops in. Red flips to green whenever the displaced member is the non-`none` one:
        the window prints ADVANCING while the true newest three are all `none`. The measured +7.97 h
        outlier (CYC-0090-d7df5340) would sort ~8 h early against receipts spaced ~40 min apart —
        several positions, on a window three deep.
    ★ Guarded, not merely written: `test_started_utc_is_not_an_accepted_clock` and
    `test_the_sort_treats_a_missing_clock_as_the_OLDEST_not_the_NEWEST` both fail if `started_utc`
    is added to RECEIPT_TIME_KEYS (mutation-audited 2026-09-02, 5 mutations of this guard, 5 caught).
    """
    out = []
    for r in receipts:
        if _receipt_ts_raw(r) is not None:
            continue
        n = _receipt_ordinal(r)
        if floor_ordinal is None or n is None or n >= floor_ordinal:
            out.append(r["_file"])
    return out


def cycle_interval_hours(state):
    """`(hours, basis)` — the expected cycle period, READ from `autonomy-state.json`, never typed.

    Returns `(None, basis)` when it cannot be read, and every condition that needs a cycle period then
    goes unmeasured rather than borrowing the fallback: the fallback exists ONLY to date the board's
    own expiry (a board with no expiry is worse than one with an approximate one), not to manufacture a
    threshold a verdict would then rest on.
    """
    if not isinstance(state, dict):
        return None, ("⚠ NOT READ — autonomy-state.json was not readable, so the expected cycle period "
                      f"is UNKNOWN and this board's own expiry falls back to "
                      f"{FALLBACK_CYCLE_INTERVAL_H:g} h. Treat the deadline as approximate in BOTH "
                      f"directions until the state file is readable again.")
    v = state.get("cycle_interval_hours")
    if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
        return None, ("⚠ NOT READ — autonomy-state.json carries no positive `cycle_interval_hours` "
                      f"(saw {v!r}), so the expected cycle period is UNKNOWN and this board's own "
                      f"expiry falls back to {FALLBACK_CYCLE_INTERVAL_H:g} h.")
    return float(v), (f"read from autonomy-state.json `cycle_interval_hours` = {float(v):g} h, which is "
                      f"its one home (the governor writes it — architecture §9.2). Not typed here.")


# ══════════════════════════════════════════════════════════════════════════════ the seven §5.2 conditions
def c_cycle_delivering(receipts, unreadable, interval_h, now):
    """Red when no receipt within 2 expected cycle periods (§2.2 — a fired Routine is not a delivered one).

    ⛔ ZERO RECEIPTS IS `unmeasured`, NOT `ok`, AND IT IS THE HEADLINE CASE OF THIS WHOLE FILE. An empty
    receipts directory is consistent with "the loop has never run", "the loop runs and cannot write",
    and "the clock never fired" — three different failures, none of them health. Grading it green is
    how a loop that has never delivered anything reports that it is delivering.
    """
    key, label = "cycle_delivering", "is a fired cycle actually DELIVERING a receipt?"
    source = "research/autonomy/receipts/*.json + autonomy-state.json"
    if interval_h is None:
        return _unmeasured(key, label, source, "PERIOD-UNKNOWN",
                           "the expected cycle period is unreadable, so 'late' has no definition. "
                           "Settle it: give autonomy-state.json a positive `cycle_interval_hours`.",
                           {"receipts_seen": len(receipts)})
    if not receipts:
        return _unmeasured(key, label, source, "NO-RECEIPTS",
                           "NO receipt exists yet, so delivery has never been observed — this is NOT a "
                           "reading that the loop is fine, it is the absence of a reading (CLAUDE.md "
                           "§4). Settle it: let one cycle complete §4.2 step 10, or check whether the "
                           "clock is firing at all.",
                           {"receipts_seen": 0, "unreadable_receipts": len(unreadable) or None})
    latest = receipts[-1]
    ts = _receipt_ts(latest)
    if ts is None:
        return _unmeasured(key, label, source, "RECEIPT-TIME-UNREADABLE",
                           f"the most recent receipt ({latest['_file']}) carries none of "
                           f"{list(RECEIPT_TIME_KEYS)}, so its age cannot be taken. A receipt with no "
                           f"clock cannot testify to delivery.",
                           {"receipts_seen": len(receipts), "latest_receipt": latest["_file"]})
    # ⛔⛔ IS `latest` ACTUALLY THE NEWEST RECEIPT, OR ONLY THE NEWEST ONE THIS MODULE CAN DATE?
    # ⚠ MEASURED 2026-09-02, and it is the defect this guard exists for: 15 receipts carried
    # `started_utc` and none of RECEIPT_TIME_KEYS, so `_receipt_ts_raw` returned None for all of
    # them, the `(ts or "", file)` sort put them at the FRONT, and `receipts[-1]` resolved to
    # CYC-0084 — four days stale — while CYC-0091 sat 2.7 h old at the other end of the list. The
    # row reported a confident `LATE ... 103.5 h` for seven consecutive board runs. A stale receipt
    # aged in place of the real newest is a MEASUREMENT OF THE WRONG THING, not a slow loop.
    # ⭐ SCOPED BY CYCLE ORDINAL, AND THAT IS THE WHOLE DESIGN. "Any clockless receipt anywhere ->
    # unmeasured" would LATCH: those 15 are immutable committed history, so the row could never go
    # green again, which is exactly what killed `cycles_are_sized` on 2026-08-27 and with it the
    # loop. The ordinal is a recency proxy that does NOT depend on the clock, so the honest question
    # is narrow: could an undatable receipt be NEWER than the one being aged? Once governed receipts
    # carry `ended_utc` the readable ordinal climbs past every clockless one and the row recovers on
    # its own — the "newest-run" recovery RECEIPT_SCOPE already declares for this condition.
    # ⛔ An UNREADABLE ordinal counts as "could be newer". A receipt this module can neither date nor
    # order is precisely the thing that must not be silently skipped.
    shadowing = _undatable_at_or_above(receipts, _receipt_ordinal(latest))
    if shadowing:
        return _unmeasured(key, label, source, "RECEIPT-TIME-UNREADABLE",
                           f"{len(shadowing)} receipt(s) at or above the cycle ordinal of "
                           f"{latest['_file']} carry none of {list(RECEIPT_TIME_KEYS)}, so they "
                           f"cannot be dated and {latest['_file']} cannot be shown to be the newest "
                           f"— its age is not a reading of delivery. ⛔ The named receipts are "
                           f"COMMITTED HISTORY and back-filling them is NOT the fix: they are "
                           f"immutable, and grading history is what latched a row and killed the "
                           f"loop on 2026-08-27. Settle it: land ONE receipt at ordinal "
                           f"≥ CYC-{receipt_schema.FIRST_CLOCK_GOVERNED_CYCLE:04d} carrying "
                           f"`{receipt_schema.ENDED_KEY}` (research-loop §2 step 10) — the contract "
                           f"names it and `receipt_schema.py --check` enforces it, so its readable "
                           f"ordinal climbs past every clockless one and this row recovers unaided. "
                           f"Undatable: "
                           + ", ".join(shadowing[:6])
                           + (f" (+{len(shadowing) - 6} more)" if len(shadowing) > 6 else ""),
                           {"receipts_seen": len(receipts), "latest_receipt": latest["_file"],
                            "undatable_receipts": len(shadowing),
                            "unreadable_receipts": len(unreadable) or None})

    age_h = _hours(now, ts)
    deadline_h = CYCLE_MISS_PERIODS * interval_h
    payload = {"receipts_seen": len(receipts), "latest_receipt": latest["_file"],
               "latest_receipt_et": _et(ts), "age_h": round(age_h, 2),
               "deadline_h": round(deadline_h, 2), "unreadable_receipts": len(unreadable) or None}
    if age_h > deadline_h:
        return _red(key, label, source, "LATE",
                    f"the last receipt is {age_h:.1f} h old against a {deadline_h:.1f} h deadline "
                    f"({CYCLE_MISS_PERIODS:g} cycle periods of {interval_h:g} h). A Routine that fires "
                    f"and delivers nothing is indistinguishable from one that never fired — check the "
                    f"clock before assuming the cycle is slow.", payload)
    return _green(key, label, source, "DELIVERING",
                  f"the last receipt ({latest['_file']}) landed {age_h:.1f} h ago, inside the "
                  f"{deadline_h:.1f} h deadline.", payload)


def c_advancing_live_work(receipts, now):
    """Red on 3 consecutive receipts with `route_advanced: none` — CLAUDE.md §0's documentation drift.

    ⭐ This is the design's own honesty instrument (§4.2). Writing up a closed route always looks like
    progress and is always easier than the live one, so the loop is capable of running for months,
    committing daily, and advancing nothing — while every artifact gate stays green.

    ⛔ A MISSING `route_advanced` IS `unmeasured`, NOT `none` AND NOT `ok`. It is the field the whole
    condition rests on, and a writer that omits it is a broken writer, not a cycle that advanced
    nothing — nor one that did. Fewer than three receipts is likewise unmeasured: the condition is
    defined on a run of three and there is no shorter reading of it.
    """
    # ⛔ THE FIELD IS IMPORTED, NEVER SPELLED (AUT-PD-017, generalising AUT-PD-013's fix). It has
    # never drifted across 29 receipts, but the risk is the same shape: a receipt that misspelled it
    # would read as ROUTE-ADVANCED-ABSENT with no hint the value was sitting right there under
    # another name. `receipt_schema.ROUTE_ADVANCED_KEY` is the one place that names it, and
    # `receipt_schema.py --check` (wired into preflight) fails the commit for a governed receipt that
    # omits it, exactly as it already does for `subagents.max_concurrent`.
    key, label = "advancing_live_work", "are cycles moving LIVE routes, or just documenting?"
    source = f"research/autonomy/receipts/*.json `{receipt_schema.ROUTE_ADVANCED_KEY}`"
    if len(receipts) < NO_ADVANCE_RUN:
        return _unmeasured(key, label, source, "TOO-FEW-RECEIPTS",
                           f"{len(receipts)} receipt(s) exist and the condition is defined on a run of "
                           f"{NO_ADVANCE_RUN}. Not a verdict that the loop is advancing work — there is "
                           f"no verdict yet. Settle it: {NO_ADVANCE_RUN - len(receipts)} more cycle(s).",
                           {"receipts_seen": len(receipts)})
    window = receipts[-NO_ADVANCE_RUN:]

    # ⛔ IS THIS WINDOW THE NEWEST RUN, OR ONLY THE NEWEST DATABLE ONE? Same defect, same guard as
    # `c_cycle_delivering` — see `_undatable_at_or_above`. A run of three `none` is a finding about
    # the LAST three cycles; read off a tail that undatable receipts have fallen out of, it is a
    # finding about whichever three the sort happened to leave there.
    ordinals = [n for n in (_receipt_ordinal(r) for r in window) if n is not None]
    shadowing = _undatable_at_or_above(receipts, min(ordinals) if len(ordinals) == len(window) else None)
    if shadowing:
        return _unmeasured(key, label, source, "WINDOW-NOT-PROVABLY-NEWEST",
                           f"{len(shadowing)} receipt(s) carry no readable clock, so they sort ahead "
                           f"of this window and it cannot be shown to be the last {NO_ADVANCE_RUN} "
                           f"cycles. A run of `none` read off the wrong three receipts is an invented "
                           f"finding, and this condition is the loop's own honesty instrument. ⛔ The "
                           f"named receipts are COMMITTED HISTORY and back-filling them is NOT the "
                           f"fix. Settle it: land {NO_ADVANCE_RUN} receipts at ordinal "
                           f"≥ CYC-{receipt_schema.FIRST_CLOCK_GOVERNED_CYCLE:04d} carrying "
                           f"`{receipt_schema.ENDED_KEY}` (research-loop §2 step 10) — this window "
                           f"is {NO_ADVANCE_RUN} deep, so it needs {NO_ADVANCE_RUN} of them before "
                           f"the tail is provably the newest run. "
                           f"Undatable: " + ", ".join(shadowing[:6])
                           + (f" (+{len(shadowing) - 6} more)" if len(shadowing) > 6 else ""),
                           {"window": [r["_file"] for r in window],
                            "undatable_receipts": len(shadowing)})

    raw = [(r["_file"], receipt_schema.route_advanced_of(r)) for r in window]
    absent = [f for f, v in raw if v is None]
    if absent:
        return _unmeasured(key, label, source, "ROUTE-ADVANCED-ABSENT",
                           f"receipt(s) {absent} record no `{receipt_schema.ROUTE_ADVANCED_KEY}`, so "
                           f"what those cycles moved is unknown. §4.2 step 10 requires the route id or "
                           f"the literal 'none' — an omitted field is neither, and reading it as 'none' "
                           f"would invent a failure exactly as readily as reading it as ok would hide "
                           f"one.",
                           {"window": [f for f, _ in raw]})
    values = [v for _, v in raw]
    payload = {"window": [f for f, _ in raw], "route_advanced": values, "receipts_seen": len(receipts)}
    if all(v.lower() == "none" for v in values):
        return _red(key, label, source, "NOT-ADVANCING",
                    f"the last {NO_ADVANCE_RUN} receipts all record `route_advanced: none` — the loop is "
                    f"doing documentation, not research (CLAUDE.md §0). The fix is a live item off the "
                    f"top of the ledger, not a tidier negative.", payload)
    advanced = [v for v in values if v.lower() != "none"]
    return _green(key, label, source, "ADVANCING",
                  f"{len(advanced)} of the last {NO_ADVANCE_RUN} cycles moved a live route "
                  f"({', '.join(advanced)}).", payload)


def c_evidence_moving(entries, ledger_err, interval_h, now):
    """Red when a `running` entry's `last_evidence_utc` has not moved over 2 cycles.

    §4's unproven-pipeline rule as a board row: an item in flight must show MOVEMENT, and "no error
    yet" is not movement. ⛔ A running entry whose `last_evidence_utc` is unreadable is unmeasured, not
    fine — that is the field the reading is taken from.

    ⚠ Zero running entries IS a measurement, not an absence: the ledger was read and it says nothing is
    in flight, so nothing can be frozen. It is recorded as green with the vacuity stated in `detail`,
    because a reader must be able to tell "checked, nothing running" from "nothing checked".
    """
    key, label = "evidence_moving", "is work in flight producing new EVIDENCE, not just heartbeats?"
    source = "research/autonomy/research-ledger.json `state`/`last_evidence_utc`"
    if entries is None:
        return _unmeasured(key, label, source, "LEDGER-UNREADABLE", f"{ledger_err}.")
    if interval_h is None:
        return _unmeasured(key, label, source, "PERIOD-UNKNOWN",
                           "the expected cycle period is unreadable, so 'unchanged over 2 cycles' has "
                           "no definition. Settle it in autonomy-state.json.")
    running = [e for e in entries if str(e.get("state") or "").strip() == "running"]
    if not running:
        return _green(key, label, source, "NOTHING-RUNNING",
                      "the ledger was read and no entry is in state `running`, so no entry can be "
                      "frozen. Vacuously true, and stated as such: this row says the check ran, not "
                      "that the loop is busy — `cycle_delivering` is the row that says that.",
                      {"entries": len(entries), "running": 0})
    deadline_h = EVIDENCE_FROZEN_PERIODS * interval_h
    frozen, unreadable = [], []
    for e in running:
        ts = _parse_ts(e.get("last_evidence_utc"))
        if ts is None:
            unreadable.append(e.get("id"))
            continue
        age_h = _hours(now, ts)
        if age_h > deadline_h:
            frozen.append({"id": e.get("id"), "age_h": round(age_h, 2),
                           "last_evidence_utc": e.get("last_evidence_utc")})
    payload = {"entries": len(entries), "running": len(running), "deadline_h": round(deadline_h, 2),
               "frozen": frozen or None, "evidence_time_unreadable": unreadable or None}
    if frozen:
        return _red(key, label, source, "FROZEN",
                    f"{len(frozen)} running entr(ies) have not changed on evidence in over "
                    f"{deadline_h:.1f} h ({EVIDENCE_FROZEN_PERIODS:g} cycles): "
                    f"{[f['id'] for f in frozen]}. Twice frozen is a stall — diagnose it against the "
                    f"real log, never against the estimate (CLAUDE.md §4).", payload)
    if unreadable:
        return _unmeasured(key, label, source, "EVIDENCE-TIME-UNREADABLE",
                           f"running entr(ies) {unreadable} carry no readable `last_evidence_utc`, so "
                           f"whether they are moving cannot be read. Settle it: §4.2 step 9 requires "
                           f"the cycle to write back what it OBSERVED, with its stamp.", payload)
    return _green(key, label, source, "MOVING",
                  f"all {len(running)} running entr(ies) changed on evidence within {deadline_h:.1f} h.",
                  payload)


def c_blocks_are_real(entries, ledger_err):
    """Red on any `blocked` entry with empty `blocked_evidence` — CLAUDE.md §0.

    "Blocked" is a claim that needs evidence and it is usually wrong: most blocked rows in this repo
    were waiting on a $0 fetch, a regeneration or a staging step. `priority.py` re-emits a
    blocked-without-evidence ROUTE as a free `kind: fetch` check, so a row that is still sitting in
    state `blocked` with nothing recorded is either hand-added or written back by a cycle that skipped
    the observation — both are the same defect and both belong on the board.
    """
    key, label = "blocks_are_real", "does every BLOCKED row carry the observation that blocked it?"
    source = "research/autonomy/research-ledger.json `state`/`blocked_evidence`"
    if entries is None:
        return _unmeasured(key, label, source, "LEDGER-UNREADABLE", f"{ledger_err}.")
    blocked = [e for e in entries if str(e.get("state") or "").strip() == "blocked"]
    naked = [e.get("id") for e in blocked if _is_empty(e.get("blocked_evidence"))]
    payload = {"entries": len(entries), "blocked": len(blocked), "without_evidence": naked or None}
    if naked:
        return _red(key, label, source, "UNEVIDENCED-BLOCK",
                    f"{len(naked)} entr(ies) claim `blocked` with no recorded evidence: {naked}. "
                    f"Each is a $0 re-test away from being either a real block with a date on it or a "
                    f"live route nobody checked — CLAUDE.md §0.", payload)
    if not blocked:
        return _green(key, label, source, "NO-BLOCKS",
                      "the ledger was read and no entry is in state `blocked`.", payload)
    return _green(key, label, source, "EVIDENCED",
                  f"all {len(blocked)} blocked entr(ies) record what was observed to establish the block.",
                  payload)


def c_queue_is_takeable(entries, ledger_err):
    """⛔ THE STALL CONDITION. Is there ANY item a cycle could actually pick up right now?

    Every other condition here asks whether the loop is doing its work well. This one asks whether
    there is any work it CAN do — and a loop with nothing takeable does not crash, does not error and
    does not go quiet. It fires on schedule, re-scores, finds nothing, writes a receipt saying it did
    nothing, and repeats. From outside it is indistinguishable from a healthy loop on a slow week.

    A queue goes untakeable four ways, and all four have happened or nearly happened here:
      - every item CLAIMED by a cycle that died (fixed by the lease in priority.py, guarded here);
      - every item BLOCKED with evidence, so the penalty demotes them all and none is workable;
      - every item's retry budget spent;
      - the ledger emptied or unreadable.

    ⚠ It counts what a cycle would take, not what exists. An 81-entry ledger where all 81 are owned or
    blocked is an EMPTY queue, and reporting 81 would be the reassuring lie.
    """
    key = "queue_is_takeable"
    label = "is there any work a cycle could actually pick up?"
    source = "research/autonomy/research-ledger.json — unowned, unblocked, retry budget remaining"
    if entries is None:
        return _unmeasured(key, label, source, "LEDGER-UNREADABLE", f"{ledger_err}.")
    if not entries:
        return _red(key, label, source, "EMPTY-LEDGER",
                    "the ledger holds no entries at all, so every cycle from here does nothing. "
                    "Re-seed it: python3 research/autonomy/priority.py --write.")
    takeable = [
        e for e in entries
        if not e.get("owner")
        and str(e.get("state") or "queued") in {"queued", "blocked"}
        and int(e.get("retry_budget") or 0) > 0
        and e.get("score") is not None
    ]
    owned = [e.get("id") for e in entries if e.get("owner")]
    spent = [e.get("id") for e in entries if int(e.get("retry_budget") or 0) <= 0]
    payload = {"entries": len(entries), "takeable": len(takeable),
               "owned": owned or None, "retry_budget_spent": spent or None}
    if not takeable:
        return _red(key, label, source, "NOTHING-TAKEABLE",
                    f"{len(entries)} entr(ies) and NONE is takeable — "
                    f"{len(owned)} owned, {len(spent)} out of retry budget. Every cycle from here "
                    "will fire, find nothing, and write a receipt saying so. That is a stall wearing "
                    "the costume of a quiet week.", payload)
    return _green(key, label, source, "TAKEABLE",
                  f"{len(takeable)} of {len(entries)} entr(ies) are takeable now.", payload)


def c_scores_are_reachable(entries, ledger_err):
    """Red when an OPEN row carries no score, because nothing can ever offer it (AUT-PD-143).

    ⛔⛔ THIS IS THE ROW `queue_is_takeable` CANNOT SEE, AND THE TWO MUST BOTH EXIST. `queue_is_takeable`
    counts rows that ARE rankable and reports TAKEABLE off them, so the ledger could reach 100%
    unscored real work and that row would still print green on one derived entry. Measured
    2026-08-28: 104 of 277 entries carried no score, 74 of them open, and the board said TAKEABLE
    throughout. An absent score was being read as a reading of absence — CLAUDE.md §4, in the one
    file whose job is to notice exactly that.

    ⭐ WHAT IT MEASURES AFTER THE FIX, WHICH IS NOT THE SAME QUESTION. `priority.apply_route_inheritance`
    now gives an unscored row the floor of its own route, so the rows counted HERE are the RESIDUE:
    rows whose route has no derived sibling to inherit from, plus rows serving no route at all.
    ⛔ THE RESIDUE IS REPORTED, NEVER INVENTED. A number pulled from nowhere would rank the row and
    tell a reader it had been valued, which is worse than the invisibility it cures.

    ⚠ WHAT WOULD SETTLE A ROW, said plainly because an unmeasured-looking red that names no remedy is
    an unanswered question wearing the costume of a status: file the row with an explicit `score` and
    a `_score_basis` in prose (AUT-PD-143 itself did), or give its route a row in `systems/graph` so
    a floor exists to inherit. ⛔ DO NOT expect this to reach zero soon — most of the residue serves
    RT-AUTONOMY, which is not a route in the graph. That is why it is `advises`.
    """
    key = "scores_are_reachable"
    label = "can every OPEN row be ranked, or is some work invisible to the queue?"
    source = "research/autonomy/research-ledger.json — open rows carrying no `score`"
    if entries is None:
        return _unmeasured(key, label, source, "LEDGER-UNREADABLE", f"{ledger_err}.")
    # ⛔ THE CLOSED SET IS POINTED AT, NEVER RETYPED. `stuck_clock.CLOSED_STATES` is already imported
    # by this module and is already the home two other readers use (`learning_rate`, `out_of_ideas`);
    # a fifth literal here is the copy that drifts. AUT-PD-050 had just finished naming this exact
    # fact in priority.py for the same reason.
    open_rows = [e for e in entries
                 if str(e.get("state") or "queued") not in stuck_clock.CLOSED_STATES]
    unscored = [e for e in open_rows if e.get("score") is None]
    by_route = {}
    for e in unscored:
        by_route[str((e.get("serves") or {}).get("route"))] = \
            by_route.get(str((e.get("serves") or {}).get("route")), 0) + 1
    payload = {"open": len(open_rows), "unrankable": len(unscored),
               "by_route": dict(sorted(by_route.items(), key=lambda kv: -kv[1])) or None,
               "ids": [e.get("id") for e in unscored][:20] or None}
    if unscored:
        return _red(key, label, source, "UNRANKABLE-WORK",
                    f"{len(unscored)} of {len(open_rows)} open row(s) carry no score, so no cycle "
                    "can be offered them and no successor prompt will list them. Settle each: file "
                    "it with an explicit `score` and `_score_basis`, or give its route a row in "
                    "systems/graph so priority.apply_route_inheritance has a floor to inherit.",
                    payload)
    return _green(key, label, source, "ALL-RANKABLE",
                  f"every one of {len(open_rows)} open row(s) carries a score.", payload)


def c_cycles_are_sized(receipts, state, state_err):
    """Red when one session ran more cycles than the cap — the session-shape rule, MEASURED at last.

    ⛔⛔ THIS CONDITION EXISTS BECAUSE THE RULE IT ENFORCES FAILED IN THE WILD ON 2026-08-26, AND IT
    FAILED IN THE ONE WAY A WRITTEN RULE CAN FAIL COMPLETELY: it was never reached.
    `.claude/skills/research-loop/SKILL.md` §3 has always said a full hardening cycle is a SPAWNED
    session rather than more work in the current one. That rule lives in a SKILL, and a skill's rules
    bind only when the skill is loaded. Measured in the offending session's own transcript:
    `"name":"Skill"` appears ZERO times. The skill's description lists four load triggers and every
    one of them is a Routine firing a cycle — so on the INTERACTIVE path, where a human asks for
    research work directly, the rule was not weak, it was UNREACHABLE. That session ran CYC-0005 and
    CYC-0006 end to end, compacted 23 times, and reached a 7.6 MB transcript.

    ⭐ THE REPAIR IS TWO-SIDED AND THIS IS ONLY THE SECOND HALF. Reachability was fixed in CLAUDE.md,
    which loads every session including interactive ones, with a §6 tripwire pointing at the skill.
    But a rule nothing measures decays back into a suggestion — the lease and the stall alarm each
    have a suite and a workflow behind them, and §3 had nothing at all. This is that gate.

    ⚠ IT BOUNDS CYCLES, WHICH IS A PROXY FOR CONTEXT AND NOT CONTEXT ITSELF, and the limit is stated
    rather than hidden: one enormous single cycle passes this check. Nothing in this repository can
    read a context window, and receipts already carry `session_id`, so this is the measurement that
    exists rather than the one that would be ideal. An imperfect gate that fires beats a perfect one
    that does not.

    ⚠ A receipt with no readable `session_id` is UNMEASURED for that receipt, never counted as a
    fresh session — otherwise the absence of a field would read as evidence of good behaviour, which
    is CLAUDE.md §4's rule exactly.
    """
    # ⛔ WINDOWED, NEVER ALL OF HISTORY — see RECEIPT_WINDOW. Reading every receipt made this
    # row latch permanently and wedged the loop on 2026-08-27.
    receipts = list(receipts or [])[-RECEIPT_WINDOW:]
    key = "cycles_are_sized"
    label = "is each cycle getting a fresh context, or is one session doing all of them?"
    source = ("research/autonomy/receipts/*.json `session_id`, against "
              "autonomy-state.json `max_cycles_per_session`")
    if not isinstance(state, dict):
        return _unmeasured(key, label, source, "STATE-UNREADABLE",
                           f"{state_err or 'autonomy-state.json is unreadable'}, so the cap is "
                           "unknown and no verdict is possible.")
    cap = state.get("max_cycles_per_session")
    if not isinstance(cap, int) or cap < 1:
        return _unmeasured(key, label, source, "NO-CAP",
                           f"autonomy-state.json carries `max_cycles_per_session`={cap!r}, not a "
                           "positive integer, so there is nothing to check against.")
    if not receipts:
        return _unmeasured(key, label, source, "NO-RECEIPTS",
                           "no readable receipt carries a session_id yet.")

    counts, unstamped = {}, []
    for r in receipts:
        sid = r.get("session_id")
        cid = r.get("cycle_id") or "?"
        # A placeholder sentence is not an id. Anything without a plausible id token is unstamped.
        if not isinstance(sid, str) or not sid.strip() or sid.strip().lower().startswith("unknown"):
            unstamped.append(cid)
            continue
        counts.setdefault(sid.strip().split()[0], []).append(cid)

    # ⭐ AN OVER-CAP SESSION THAT HANDED OFF HAS OBEYED THE RULE — MEASURE THE ACTION, NOT THE COUNT.
    # Added 2026-08-27. The first version counted cycles and nothing else, so the only way to a green
    # row was to WAIT for the window to slide: the rule's remedy (start a successor session) moved
    # the row not at all. A condition that cannot be satisfied by doing the right thing teaches
    # nothing — it is a stopwatch, not a guard. `handoff.child_session_id` in any receipt of that
    # session is the evidence, and it is evidence only a real `create_session` call can produce.
    handed_off = {sid for sid, _ in counts.items()
                  for r in receipts
                  if (r.get("session_id") or "").strip().split()[:1] == [sid]
                  and handoff.child_session_id_of(r)}
    # ⛔⛔ A REFUSED HANDOFF IS NOT A SKIPPED ONE (AUT-PD-032, measured 2026-08-27). `create_session`
    # refuses at a lineage depth limit — "caller session is at lineage depth 8 (limit 8)" — so §3's
    # remedy is UNAVAILABLE at the end of a spawn chain, and the deeper the loop has run unattended
    # the more certainly it fails. The session that hit it built the prompt with handoff.py, made
    # the call, and was refused; grading that RED made this row exactly what the comment above warns
    # against — "a condition that cannot be satisfied by doing the right thing ... a stopwatch, not
    # a guard" — and no future cycle could clear it, which is the LATCHING shape RECEIPT_WINDOW was
    # added to fix, arriving through a different door.
    # ⚠ IT DOWNGRADES TO UNMEASURED, NEVER TO GREEN, AND THE DIFFERENCE IS THE POINT: no successor
    # exists, so the work did NOT continue in a fresh context. What is untrue is that the session
    # failed to try. Green would claim the rule was satisfied; red claims a defect that is not the
    # session's; unmeasured says the loop cannot be graded on this because the mechanism was gone.
    # ⛔ AND THE REFUSAL MUST BE RECORDED VERBATIM. An absent record stays RED — otherwise "I could
    # not" becomes a free pass claimable by any session that simply never tried.
    # ⭐⭐ A REFUSAL AND AN ABSENCE ARE TWO DIFFERENT FAILURES AND THIS ROW USED TO GRADE THEM
    # OPPOSITE WAYS (AUT-PD-059, measured 2026-08-28 against the two real receipts).
    # AUT-PD-032: `create_session` EXISTS, was called, and the platform refused it at a lineage-depth
    # ceiling — recorded verbatim under `handoff.refused_by`, and graded UNMEASURED right below.
    # AUT-PD-045: in a scheduled-Routine session `create_session` is NOT ON THE TOOL SURFACE AT ALL,
    # at depth 1, with no chain to have exhausted — recorded under `handoff.mechanism_unavailable`,
    # the field `session_cap.py` already honours as an earned reason such a session MAY STOP.
    # ⛔ THIS FILE READ ONLY THE FIRST FIELD, so the second shape fell through to RED: measured, a
    # receipt carrying a real `mechanism_unavailable` string scored SESSION-OVERLOADED-NO-HANDOFF.
    # Two modules therefore disagreed about the same receipt — `session_cap` told the session it had
    # earned the right to stop, and this row called stopping its defect — and the shape that took the
    # punitive reading is the MORE common launch for an unattended cycle, not an edge case.
    # ★ THE REMEDIES ARE DIFFERENT, WHICH IS THE WHOLE REASON TO SEPARATE THEM RATHER THAN WIDEN ONE
    # BRANCH: a depth refusal says start the successor nearer the root; an absence says spawning
    # cannot help from this launch shape at all and the driver Routine's next firing IS the successor.
    # A future session reading a merged verdict would retry something that cannot work, or abandon
    # something that would have.
    # ⚠ BOTH DOWNGRADE TO UNMEASURED AND NEITHER EVER REACHES GREEN. No successor exists in either
    # case, so the work did not continue in a fresh context; what is untrue is that the session chose
    # not to try. And an ABSENT record stays RED under both, which is the anti-gaming half: otherwise
    # "I could not" — in either flavour — becomes a free pass claimable by a session that never looked.
    # ⚠ THE ABSENCE EVIDENCE IS THE WEAKER OF THE TWO AND SAYS SO. A refusal quotes the platform; an
    # absence produces no words to quote, so its string is the session's own account of a check it
    # says it ran. That is a reason it can never buy green — not a reason to collapse it back to red.
    def _sessions_where(reader):
        return {sid for sid in counts
                for r in receipts
                if (r.get("session_id") or "").strip().split()[:1] == [sid] and reader(r)}

    def _first(sid, reader):
        return next((reader(r) for r in receipts
                     if (r.get("session_id") or "").strip().split()[:1] == [sid] and reader(r)), "")

    refused = _sessions_where(handoff.refusal_of)
    # ⛔ REFUSAL WINS A TIE. A session recording both fields made a call and got words back; that is
    # the stronger evidence, and classifying it as an absence would discard the platform's own answer.
    absent = _sessions_where(handoff.mechanism_unavailable_of) - refused
    over = {sid: cids for sid, cids in counts.items()
            if len(cids) > cap and sid not in handed_off}
    over_but_refused = {sid: cids for sid, cids in over.items() if sid in refused}
    over_but_absent = {sid: cids for sid, cids in over.items() if sid in absent}
    over = {sid: cids for sid, cids in over.items()
            if sid not in refused and sid not in absent}
    payload = {"cap": cap, "sessions": {k: len(v) for k, v in counts.items()},
               "unstamped_receipts": unstamped or None,
               "handed_off": sorted(handed_off) or None,
               "over_cap_but_handoff_refused": sorted(over_but_refused) or None,
               "over_cap_but_mechanism_absent": sorted(over_but_absent) or None,
               "worst": max((len(v) for v in counts.values()), default=0)}
    # ⚠ When both blocked shapes are present the verdict line can only name one, so it names the
    # refusal — the one carrying the platform's own words — and the detail carries the other's count.
    # The payload always carries both lists, so a machine reader is never routed through the prose.
    also = ""
    if over_but_refused and over_but_absent:
        also = (f" ⚠ A FURTHER {len(over_but_absent)} over-cap session(s) were blocked the OTHER way "
                "— no spawn mechanism on the tool surface at all, listed in the payload under "
                "`over_cap_but_mechanism_absent`. Different failure, different remedy; do not read "
                "this verdict as covering them.")
    if not over and over_but_refused:
        sid = sorted(over_but_refused)[0]
        why = _first(sid, handoff.refusal_of)
        return _unmeasured(key, label, source, "HANDOFF-REFUSED",
                           f"session {sid[:24]} ran {len(over_but_refused[sid])} cycles against a "
                           f"cap of {cap} and its handoff was REFUSED BY THE PLATFORM, verbatim: "
                           f"{why[:160]}. ⭐ It built the successor prompt and made the call; §3's "
                           "remedy does not exist at the end of a spawn chain. Not green — no "
                           "successor exists and the work did not continue in a fresh context. Not "
                           "red — that would be a defect no future cycle could clear. ⚠ The "
                           "scheduled driver Routine is the designed fallback here, and it is only "
                           "a fallback rather than a deferral BECAUSE the handoff was attempted "
                           "first. ★ REMEDY, AND IT IS NOT AN ABSENT MECHANISM'S: the tool exists "
                           "and works nearer the root, so the next successor should be started at a "
                           "shallower lineage rather than chained off this one." + also, payload)
    if not over and over_but_absent:
        sid = sorted(over_but_absent)[0]
        why = _first(sid, handoff.mechanism_unavailable_of)
        return _unmeasured(key, label, source, "HANDOFF-MECHANISM-ABSENT",
                           f"session {sid[:24]} ran {len(over_but_absent[sid])} cycles against a "
                           f"cap of {cap} and recorded NO SPAWN MECHANISM ON ITS TOOL SURFACE under "
                           f"`{handoff.UNAVAILABLE_FIELD}`: {why[:160]}. ⭐ THIS IS NOT THE DEPTH "
                           "REFUSAL (AUT-PD-032) AND THE DIFFERENCE DECIDES WHAT TO DO NEXT: nothing "
                           "was refused because nothing could be called, so starting a successor "
                           "nearer the root does not help and there is no chain to shorten. The "
                           "driver Routine's next firing is the successor, and for this launch shape "
                           "it is the ONLY one. ⚠ Not green — no successor exists and the work did "
                           "not continue in a fresh context. Not red — the platform withheld the "
                           "mechanism, so no future cycle in this launch shape could clear it by "
                           "behaving better. ⛔ And this evidence is weaker than a quoted refusal: an "
                           "absence leaves no platform words, so the string above is the session's "
                           "own account of the check it ran. An ABSENT record stays RED.", payload)
    if over:
        worst = max(over.items(), key=lambda kv: len(kv[1]))
        return _red(key, label, source, "SESSION-OVERLOADED-NO-HANDOFF",
                    f"session {worst[0][:24]} ran {len(worst[1])} cycles ({', '.join(worst[1])}) "
                    f"against a cap of {cap} AND STARTED NO SUCCESSOR. §3 of the cycle contract: a "
                    "full hardening cycle is a SPAWNED session, not more work in the current one. "
                    "Context is the resource that runs out silently — nothing announces it, and the "
                    "cycle that overruns it is the one that cannot tell. ⭐ THE REMEDY IS ONE ACT: "
                    "build the successor's prompt with `python3 research/autonomy/handoff.py --json` "
                    "and create the session, then record its id in this cycle's receipt under "
                    f"`{handoff.CHILD_ID_FIELD}`. A loop that needs a human to start its next session "
                    "is not automated; it just has a longer fuse.", payload)
    if not counts:
        return _unmeasured(key, label, source, "NONE-STAMPED",
                           f"{len(unstamped)} receipt(s) carry no usable session_id "
                           f"({', '.join(unstamped[:5])}), so nothing can be counted. An absent "
                           "stamp is not evidence of a fresh session.", payload)
    return _green(key, label, source, "SIZED",
                  f"{len(counts)} session(s), worst carries {payload['worst']} cycle(s) against a "
                  f"cap of {cap}.", payload)


def c_fanout_is_governed(receipts, state, state_err):
    """Red when a cycle dispatched more concurrent subagents than `subagent_width` allows.

    ⛔⛔ THIS DIAL WAS WIRED TO NOTHING, AND IT IS THE ONE THE ARCHITECTURE CALLS THE MOST IMPORTANT.
    Measured 2026-08-26: `grep -rn subagent_width` over the whole repository returned TWO hits — the
    JSON that defines it, and one test asserting its value is 5. No code read it, no cycle consulted
    it, and no receipt recorded what was actually dispatched. §9 records why that matters: a
    **107-agent fan-out hit the account weekly usage limit — 40 completed, 67 errored, and the
    synthesis step failed**, so the tool's returned result was a truncation artifact and the findings
    had to be recovered by hand from journal.jsonl. The architecture's own words: *width is the more
    important dial — the incident above was a WIDTH failure, not a depth one.*

    ⭐ AND IT WAS WORSE THAN THE SESSION-SHAPE RULE THIS REPOSITORY FIXED AN HOUR EARLIER. That rule
    at least existed as prose in a skill; this was a NUMBER IN A STATE FILE CONNECTED TO NO CODE PATH
    AT ALL — the purest form of a governed value that governs nothing.

    ⛔ THE UNIT HAD NEVER BEEN WRITTEN DOWN EITHER, WHICH IS WHY THIS WAS UNENFORCEABLE RATHER THAN
    MERELY UNENFORCED. A cap of "5" says nothing until you say five of what. It is CONCURRENT
    subagents — see autonomy-state.json's `_subagent_width_means`, which now carries the reasoning and
    the limit of what this dial does NOT govern (serial total).

    ⚠ THIS IS A RETROSPECTIVE GATE AND SAYS SO. Nothing here can intercept a dispatch; a health
    condition reads committed files after the fact. Its job is to make an overrun VISIBLE and
    attributable, exactly as `cycles_are_sized` does. The prevention half lives in CLAUDE.md, at the
    line that grants standing authorisation to spawn — which is where the number has to be readable,
    because that is the moment the decision is made.

    ⚠ A receipt with no `subagents` block is UNMEASURED, never green. Otherwise the cheapest way to a
    clean board is to stop recording dispatches, and a gate whose easiest defeat is omitting data is
    a gate that measures compliance with itself (CLAUDE.md §4).
    """
    # ⛔ WINDOWED, NEVER ALL OF HISTORY — see RECEIPT_WINDOW. Reading every receipt made this
    # row latch permanently and wedged the loop on 2026-08-27.
    receipts = list(receipts or [])[-RECEIPT_WINDOW:]
    key = "fanout_is_governed"
    label = "did any cycle fan out wider than the governed cap?"
    source = (f"receipts' `subagents.{receipt_schema.WIDTH_KEY}` (name owned by "
              "research/autonomy/receipt_schema.py), against autonomy-state.json `subagent_width`")
    if not isinstance(state, dict):
        return _unmeasured(key, label, source, "STATE-UNREADABLE",
                           f"{state_err or 'autonomy-state.json is unreadable'}, so the cap is "
                           "unknown and no verdict is possible.")
    cap = state.get("subagent_width")
    if not isinstance(cap, int) or cap < 1:
        return _unmeasured(key, label, source, "NO-CAP",
                           f"`subagent_width`={cap!r} is not a positive integer, so there is nothing "
                           "to check against.")

    measured, unrecorded, drifted = [], [], {}
    for r in receipts or []:
        cid = r.get("cycle_id") or "?"
        width = receipt_schema.width_of(r)
        if width is None:
            unrecorded.append(cid)
            # ⭐ NAME THE CAUSE, DO NOT JUST COUNT THE ABSENCE (CLAUDE.md §4). "records no dispatch"
            # was the sentence this row printed about receipts that recorded one under a drifted
            # key — an instrument reporting a false absence, wearing the costume of the restraint it
            # could not see. The drifted spelling IS the discriminating observation, so it is here.
            found = receipt_schema.drift_in(r)
            if found:
                drifted[cid] = found
        else:
            measured.append((cid, width))

    payload = {"cap": cap, "measured": dict(measured) or None,
               "receipts_not_recording_dispatch": unrecorded or None,
               "recorded_under_a_drifted_key": drifted or None,
               "worst": max((w for _, w in measured), default=None)}
    over = [(c, w) for c, w in measured if w > cap]
    if over:
        c, w = max(over, key=lambda cw: cw[1])
        return _red(key, label, source, "FANOUT-OVER-CAP",
                    f"{c} dispatched {w} concurrent subagents against a cap of {cap}. Width is the "
                    "dial §9 records as having failed catastrophically: a 107-agent fan-out lost 67 "
                    "agents and its synthesis to the weekly limit. Lower it, or move `backoff_level` "
                    "— never widen the cap to fit what was already spent.", payload)
    if not measured:
        drift_note = ""
        if drifted:
            drift_note = (" ⚠ " + ", ".join(f"{c} records {'/'.join(sorted(v))}"
                                            for c, v in list(drifted.items())[:3]) +
                          f" — a fan-out WAS recorded there, under a key this row does not read. "
                          f"`receipt_schema.DRIFTED_KEYS` says which are renames and which are a "
                          f"different quantity; `launched` is the serial total and is NOT the cap's "
                          f"unit.")
        return _unmeasured(key, label, source, "DISPATCH-NOT-RECORDED",
                           f"{len(unrecorded)} receipt(s) record no readable "
                           f"`subagents.{receipt_schema.WIDTH_KEY}` "
                           f"({', '.join(unrecorded[:5])}), so what was dispatched is unknown. An "
                           "absent record is not a record of restraint." + drift_note, payload)
    return _green(key, label, source, "WITHIN-CAP",
                  f"{len(measured)} cycle(s) recorded a fan-out; the widest was "
                  f"{payload['worst']} against a cap of {cap}.", payload)


#: ⛔⛔ THE DIALS A BUDGET HOLD CLAIMS, AND THE ONE PLACE THEY ARE CHECKED AGAINST WHAT IS LIVE.
#: Each key of `budget_hold.declared_posture` names a ceiling; the value beside it is the state-file
#: key that must not exceed it. Written as a table rather than four `if`s because the failure this
#: guards against is a posture key added to the JSON and quietly checked by nothing — the exact way
#: `subagent_width` governed nothing for a fortnight (CLAUDE.md §1). An unknown posture key is
#: therefore UNMEASURED and says so, never silently skipped.
HOLD_POSTURE_DIALS = {
    "max_cycle_interval_hours": ("cycle_interval_hours", "min"),
    "max_subagent_width": ("subagent_width", "max"),
    "max_items_per_cycle": ("items_per_cycle", "max"),
    "max_cycles_per_session": ("max_cycles_per_session", "max"),
}


def hold_posture_violations(state):
    """Which dials are LOOSER than the active hold declares — plus the posture keys nobody checks.

    Returns ``(violations, unknown_keys)``. ``violations`` is a list of
    ``(state_key, live_value, bound, sense)``. ``sense`` is ``"min"`` when the declared number is a
    FLOOR the live dial must meet or exceed (a cadence: 24 h means *at least* 24 h between cycles)
    and ``"max"`` when it is a CEILING the live dial must not exceed (a width, a count).

    ⚠ A dial that is absent or non-numeric counts as a VIOLATION, not as a pass. A hold whose
    posture cannot be read is a hold that is not in force, and the whole point of this function is
    that the softer reading — "nothing to check, therefore fine" — is how a guard becomes decorative.
    """
    hold = (state or {}).get("budget_hold") or {}
    posture = hold.get("declared_posture") or {}
    violations, unknown = [], []
    for pkey, bound in posture.items():
        if pkey.startswith("_"):
            continue
        dial = HOLD_POSTURE_DIALS.get(pkey)
        if dial is None:
            unknown.append(pkey)
            continue
        skey, sense = dial
        live = (state or {}).get(skey)
        if not isinstance(bound, (int, float)) or isinstance(bound, bool):
            unknown.append(pkey)
            continue
        if not isinstance(live, (int, float)) or isinstance(live, bool):
            violations.append((skey, live, bound, sense))
        elif (sense == "min" and live < bound) or (sense == "max" and live > bound):
            violations.append((skey, live, bound, sense))
    return violations, unknown


def c_budget_recovering(state, state_err, now):
    """Red when `backoff_level` has been > 0 for more than 24 h — §9's stuck-loop row.

    ⛔ A raised backoff with no `backoff_since_utc` is unmeasured: the level is readable, the DURATION
    is not, and the whole condition is a duration. The governor writes that stamp when it raises the
    level (§9.1 — it backs off on an OBSERVED signal, so it knows when it observed it).

    ⚠ Level 0 is a MEASURED green, not a vacuous one: the file exists and says the loop is not in
    backoff. That is a reading, and it is the difference between this row and an absent state file.
    """
    key, label = "budget_recovering", "is the budget governor RECOVERING, or stuck in backoff?"
    source = ("research/autonomy/autonomy-state.json `backoff_level`/`backoff_since_utc`, and "
              "`budget_hold` — a DELIBERATE hold is read separately from a stuck one")
    if not isinstance(state, dict):
        return _unmeasured(key, label, source, "STATE-UNREADABLE", f"{state_err}.")
    level = state.get("backoff_level")
    if not isinstance(level, int) or isinstance(level, bool) or level < 0:
        return _unmeasured(key, label, source, "LEVEL-UNREADABLE",
                           f"`backoff_level` is {level!r}, not a non-negative integer, so the budget "
                           f"posture cannot be read.")
    # ⛔⛔ AN ACTIVE HOLD IS CONSULTED AT LEVEL 0 TOO, AND UNTIL 2026-09-01 IT WAS NOT.
    # This returned NO-BACKOFF here unconditionally, BEFORE the hold was read — so a hold whose
    # `declared_posture` the live dials openly violated went completely unnoticed whenever
    # `backoff_level` happened to be 0. The comment fifty lines below says "THE HOLD MUST GOVERN THE
    # DIALS, OR IT IS DECORATION"; at level 0 it was decoration, by construction, in the one row
    # written to catch exactly that.
    # ⚠ FOUND BY WALKING INTO IT. The sprint of 2026-09-01 set a hold with a RAISED ceiling
    # (width 12, 4 h cadence) and `backoff_level: 0` — a hold that pins a ceiling rather than a
    # floor, which is a shape this row had never been given. Nine tests in
    # `test_a_cadence_nobody_enforces_is_not_a_cadence.py` went red at once, every one of them
    # building its fixture from the live state and mutating a single dial. They were right and the
    # code was wrong: they assert that loosening a dial past its declared bound is NOTICED, and it
    # was not being noticed at all.
    # ★ THE DIRECTION, STATED BECAUSE THIS IS A GOVERNED PATH: this makes the row check MORE, never
    # less. Level 0 with no active hold is still the same measured green it always was — that
    # reading is untouched. What changes is that level 0 WITH a hold now has to honour it.
    hold_at_zero = state.get("budget_hold") or {}
    if level == 0 and not (isinstance(hold_at_zero, dict) and hold_at_zero.get("active")):
        return _green(key, label, source, "NO-BACKOFF",
                      "the governor records backoff level 0 — the loop is running at full cadence and "
                      "width.", {"backoff_level": 0})
    if level == 0:
        violations, unknown = hold_posture_violations(state)
        review_after = _parse_ts(hold_at_zero.get("review_after_utc"))
        floor = hold_at_zero.get("floor_backoff_level")
        payload = {"backoff_level": 0, "budget_hold": {
            "reason": hold_at_zero.get("reason"), "floor_backoff_level": floor,
            "review_after_et": _et(review_after) if review_after
            else hold_at_zero.get("review_after_utc"),
            "posture_violations": [
                {"dial": k, "live": v, "bound": b, "sense": s} for k, v, b, s in violations] or None,
            "posture_keys_checked_by_nothing": unknown or None,
        }}
        if violations or unknown:
            bits = [f"`{k}`={v!r} against a declared {'floor' if s == 'min' else 'ceiling'} of {b}"
                    for k, v, b, s in violations]
            bits += [f"`declared_posture.{k}` is read by nothing in HOLD_POSTURE_DIALS"
                     for k in unknown]
            return _red(key, label, source, "HOLD-NOT-IN-FORCE",
                        f"a budget hold ({hold_at_zero.get('reason')!r}) is active but the live dials "
                        f"do not honour it: " + "; ".join(bits) + ". A hold that governs nothing is "
                        "`subagent_width` again — defined in JSON, asserted by one test, read by no "
                        "code for a fortnight. Set the dials, or drop the hold; never leave both.",
                        payload)
        if isinstance(floor, int) and not isinstance(floor, bool) and level < floor:
            return _red(key, label, source, "HOLD-FLOOR-BREACHED",
                        f"the hold pins `backoff_level` at {floor} or above and it reads {level}. A "
                        "clean cycle decrements the level (§9 property 3), so this is what that "
                        "decrement looks like when it runs through a hold it should have stopped at.",
                        payload)
        if review_after is not None and now >= review_after:
            return _red(key, label, source, "HOLD-NEEDS-A-FRESH-READING",
                        f"the hold's review stamp ({_et(review_after)}) has passed. ⛔ It expires into "
                        "a REVIEW, not into full cadence: take a fresh utilisation reading, write it "
                        "to `last_utilisation_report`, and only then lift or step the hold down one "
                        "level. A stamp passing is not evidence that the budget recovered.", payload)
        return _green(key, label, source, "BUDGET-HELD",
                      f"backoff is at level 0 under a deliberate hold "
                      f"({hold_at_zero.get('reason')!r}) that pins a CEILING rather than a floor, "
                      f"reviewable {_et(review_after) if review_after else '?'}. The dials honour it.",
                      payload)
    since = _parse_ts(state.get("backoff_since_utc"))
    if since is None:
        return _unmeasured(key, label, source, "BACKOFF-AGE-UNKNOWN",
                           f"backoff level is {level} but `backoff_since_utc` is absent or unreadable, "
                           f"so HOW LONG it has been raised is unknown — and the condition is entirely "
                           f"a duration. Settle it: the governor stamps `backoff_since_utc` in the same "
                           f"write that raises the level.", {"backoff_level": level})
    held_h = _hours(now, since)
    payload = {"backoff_level": level, "backoff_since_et": _et(since), "held_h": round(held_h, 2),
               "grace_h": BACKOFF_GRACE_H, "last_limit_flip": state.get("last_limit_flip")}
    # ⭐⭐ A DELIBERATE BUDGET HOLD IS NOT A STUCK LOOP, AND UNTIL 2026-08-29 THIS ROW COULD NOT TELL
    # THEM APART. Its whole condition is a DURATION, so a hold meant to last the rest of a weekly
    # window would have gone red at 24 h and stayed red for three days — a permanent red on a
    # governor that was working exactly as instructed. The discriminating observation is not the
    # duration; it is whether the state file carries a REASON and an EXPIRY beside the level.
    hold = state.get("budget_hold") or {}
    if isinstance(hold, dict) and hold.get("active"):
        review_after = _parse_ts(hold.get("review_after_utc"))
        floor = hold.get("floor_backoff_level")
        violations, unknown = hold_posture_violations(state)
        payload = dict(payload, budget_hold={
            "reason": hold.get("reason"), "floor_backoff_level": floor,
            "review_after_et": _et(review_after) if review_after else hold.get("review_after_utc"),
            "posture_violations": [
                {"dial": k, "live": v, "bound": b, "sense": s} for k, v, b, s in violations] or None,
            "posture_keys_checked_by_nothing": unknown or None,
        })
        # ⛔ THE HOLD MUST GOVERN THE DIALS, OR IT IS DECORATION. Checked BEFORE the expiry, because
        # a hold that was never in force does not become correct by also being current.
        if violations or unknown:
            bits = [f"`{k}`={v!r} against a declared {'floor' if s == 'min' else 'ceiling'} of {b}"
                    for k, v, b, s in violations]
            bits += [f"`declared_posture.{k}` is read by nothing in HOLD_POSTURE_DIALS" for k in unknown]
            return _red(key, label, source, "HOLD-NOT-IN-FORCE",
                        f"a budget hold ({hold.get('reason')!r}) is active but the live dials do not "
                        f"honour it: " + "; ".join(bits) + ". A hold that governs nothing is "
                        "`subagent_width` again — defined in JSON, asserted by one test, read by no "
                        "code for a fortnight. Set the dials, or drop the hold; never leave both.",
                        payload)
        if isinstance(floor, int) and not isinstance(floor, bool) and level < floor:
            return _red(key, label, source, "HOLD-FLOOR-BREACHED",
                        f"the hold pins `backoff_level` at {floor} or above and it reads {level}. A "
                        "clean cycle decrements the level (§9 property 3), so this is what that "
                        "decrement looks like when it runs through a hold it should have stopped at.",
                        payload)
        if review_after is not None and now >= review_after:
            return _red(key, label, source, "HOLD-NEEDS-A-FRESH-READING",
                        f"the hold's review stamp ({_et(review_after)}) has passed. ⛔ It expires into "
                        "a REVIEW, not into full cadence: take a fresh utilisation reading, write it "
                        "to `last_utilisation_report`, and only then lift or step the hold down one "
                        "level. A stamp passing is not evidence that the budget recovered.", payload)
        return _green(key, label, source, "BUDGET-HELD",
                      f"backoff is held at level {level} by a deliberate budget hold "
                      f"({hold.get('reason')!r}), reviewable {_et(review_after) if review_after else '?'}. "
                      f"The dials honour it. Held ≠ stuck: this is §9 property 4 doing its job, and the "
                      f"{BACKOFF_GRACE_H:g} h grace below is for a limit nobody chose.", payload)
    if held_h > BACKOFF_GRACE_H:
        return _red(key, label, source, "STUCK",
                    f"backoff has been at level {level} for {held_h:.1f} h (> {BACKOFF_GRACE_H:g} h). A "
                    f"limit that never clears is a stuck loop, not a busy one — §9.1 makes the reset a "
                    f"timestamp (`rate_limit_info.resetsAt`), so read it rather than waiting blind.",
                    payload)
    return _green(key, label, source, "BACKING-OFF",
                  f"backoff is at level {level}, raised {held_h:.1f} h ago and inside the "
                  f"{BACKOFF_GRACE_H:g} h grace — degrading, which is the design working (§9 property 4).",
                  payload)


def c_gates_green(gates, gates_err, now):
    """Red when preflight has been red on `main` for > 24 h — a red trunk stops every cycle at step 8.

    ⛔ THIS MODULE CANNOT MEASURE IT ITSELF and does not pretend to: the gate verdict lives in GitHub
    Actions, and this file is stdlib-only with no network by design (it must keep working when
    everything else has stopped). So the verdict is supplied as a FILE by the caller that does have the
    network — `autonomy-tick.yml`, the same shape `alarm_state.py` takes `--fleet-verdict` in. Absent
    file, absent reading: `unmeasured`, never green.

    ⚠ ONE ASYMMETRY, DELIBERATE. If the verdict says main is red RIGHT NOW but carries no
    `red_since_utc`, this reports RED rather than unmeasured. The failure itself was measured; only its
    age was not, and reporting a measured failure early is the fail-loud direction. That is the
    opposite call from `budget_recovering` above, where the LEVEL alone is not a failure at all.
    """
    key, label = "gates_green", "is `main` green, so a cycle can even commit?"
    source = "--gates-verdict (written by the workflow that can read Actions)"
    if not isinstance(gates, dict):
        return _unmeasured(key, label, source, "NO-GATE-VERDICT",
                           f"{gates_err or 'no gate verdict was supplied'}. This checker has no network "
                           f"by design, so it cannot read Actions itself. Settle it: have the tick "
                           f"workflow write {{\"ok\": bool, \"red_since_utc\": str|null, \"detail\": "
                           f"str}} and pass it with --gates-verdict.")
    ok = gates.get("ok")
    if not isinstance(ok, bool):
        return _unmeasured(key, label, source, "GATE-VERDICT-UNREADABLE",
                           f"the gate verdict carries `ok`={ok!r}, not a boolean, so it says nothing "
                           f"about the trunk.", {"raw": gates.get("detail")})
    if ok:
        return _green(key, label, source, "GREEN", gates.get("detail") or "the trunk is green.",
                      {"checked_et": gates.get("checked_et"), "ref": gates.get("ref")})
    since = _parse_ts(gates.get("red_since_utc"))
    detail = gates.get("detail") or "the trunk is red."
    if since is None:
        return _red(key, label, source, "RED",
                    f"{detail} How long it has been red is not recorded, so it is reported now rather "
                    f"than waiting out a {GATES_RED_GRACE_H:g} h deadline that cannot be measured — a "
                    f"red trunk stops every cycle at §4.2 step 8.", {"ref": gates.get("ref")})
    held_h = _hours(now, since)
    payload = {"red_since_et": _et(since), "held_h": round(held_h, 2), "grace_h": GATES_RED_GRACE_H,
               "ref": gates.get("ref")}
    if held_h > GATES_RED_GRACE_H:
        return _red(key, label, source, "RED-STUCK",
                    f"{detail} Red for {held_h:.1f} h (> {GATES_RED_GRACE_H:g} h) — every cycle since "
                    f"has been unable to commit.", payload)
    return _green(key, label, source, "RED-BUT-FRESH",
                  f"{detail} Red for {held_h:.1f} h, inside the {GATES_RED_GRACE_H:g} h grace — the "
                  f"next cycle is expected to fix it, and this row goes red if it does not.", payload)


def c_authority_respected(receipts, authority, authority_err):
    """Red on any outward act with no matching grant — §6.3, the one permission the loop cannot self-grant.

    An outward act is anything a receipt records under `outward_acts[]`: `{"venue": ..., "act": ...}`.
    A grant matches when `publication-authority.json` gives that venue `standing_grant: true` AND lists
    the act in `scope.acts`. `journal.standing_grant` is a constant false — not a parameter, not
    reachable by any bar — so a journal submission never matches and always shows here.

    ⛔ THE ABSENT-FILE CASE IS SPLIT, AND THE SPLIT IS THE POINT:
      no authority file AND no acts recorded  → `unmeasured`. There is nothing to check against, and no
        evidence the loop even logs acts. Green here would mean "we found no violations" when what
        happened is that nobody looked.
      no authority file BUT acts recorded     → RED, immediately. An outward act taken when no authority
        record exists at all is the exact failure CLAUDE.md §3 is written against, and its absence of a
        grant is not an absence of a reading — it is the reading.
    """
    key, label = "authority_respected", "did every OUTWARD act have a grant behind it?"
    source = "receipts `outward_acts[]` × research/autonomy/publication-authority.json"
    acts = []
    for r in receipts:
        for a in (r.get("outward_acts") or []):
            acts.append((r["_file"], a))
    have_authority = isinstance(authority, dict)
    if not have_authority and not acts:
        return _unmeasured(key, label, source, "NO-AUTHORITY-RECORD",
                           f"{authority_err or 'publication-authority.json is absent'}, and no receipt "
                           f"records an outward act. Nothing was checked, which is NOT the same as "
                           f"nothing being wrong: it is equally consistent with receipts that never log "
                           f"acts. Settle it: land §6.3's authority file (a rule change trimcrae makes, "
                           f"in the same commit as AGENTS.md and CLAUDE.md §3), and have receipts write "
                           f"`outward_acts[]` even when empty.",
                           {"receipts_seen": len(receipts)})
    ungranted = []
    for fname, act in acts:
        if not isinstance(act, dict):
            ungranted.append({"receipt": fname, "act": repr(act), "why": "act is not an object"})
            continue
        venue = str(act.get("venue") or act.get("target") or "").strip().lower()
        kind = str(act.get("act") or act.get("kind") or "").strip().lower()
        if not have_authority:
            ungranted.append({"receipt": fname, "venue": venue, "act": kind,
                              "why": "no authority file exists at all"})
            continue
        grant = authority.get(venue)
        if not isinstance(grant, dict) or grant.get("standing_grant") is not True:
            ungranted.append({"receipt": fname, "venue": venue, "act": kind,
                              "why": f"no standing grant for venue {venue!r}"})
            continue
        allowed = [str(x).strip().lower() for x in ((grant.get("scope") or {}).get("acts") or [])]
        if kind not in allowed:
            ungranted.append({"receipt": fname, "venue": venue, "act": kind,
                              "why": f"act {kind!r} is not in scope.acts {allowed}"})
    payload = {"acts_seen": len(acts), "ungranted": ungranted or None,
               "authority_file": "present" if have_authority else "absent"}
    if ungranted:
        return _red(key, label, source, "UNGRANTED-ACT",
                    f"{len(ungranted)} outward act(s) have no matching grant: {ungranted}. This is the "
                    f"one thing the loop may never grant itself (§6.3) — being blocked is not "
                    f"authorisation (CLAUDE.md §3).", payload)
    if not acts:
        return _green(key, label, source, "NO-OUTWARD-ACTS",
                      "the authority file is present and no receipt records an outward act, so nothing "
                      "went out unauthorised.", payload)
    return _green(key, label, source, "GRANTED",
                  f"all {len(acts)} outward act(s) match a standing grant in "
                  f"publication-authority.json.", payload)


def c_stalls_are_named(stall, stall_err):
    """Red when `stuck_clock.py` reports a ledger row `stalled_needs_human` — AUT-PROP-029, wired in.

    ⛔⛔ THE GAP THIS CLOSES. `research/autonomy/stuck_clock.py` derives two independent clocks per
    OPEN ledger row from git history — `updated_at` (any write) and `stuck_at` (only a change that
    advances what is KNOWN about the work) — and declares a row `stalled_needs_human` once it has been
    touched, claimed, retried and re-claimed for `stuck_clock.STUCK_AFTER_CYCLES` cycles with the
    advance clock never moving. It was fully built and fully tested (40 tests,
    `research/autonomy/tests/test_stuck_clock_a_retry_is_not_an_advance.py`) and NOTHING called it: no
    board condition read it, `priority.py`/`handoff.py` did not exclude a terminal row from ready work,
    and no scheduled job ran `--check`. A row could compute as terminal today and the only way anyone
    would ever see that is running the CLI by hand — an unrun guard, the exact shape `AUT-PD-018`
    already cost this repository once ("an unrun ranker is not a ranker").

    ⛔⛔ THIS MODULE CANNOT MEASURE IT ITSELF, FOR THE SAME REASON AS `gates_green`. stuck_clock's two
    clocks are derived by shelling out to `git log --follow` / `git show` on every committed version of
    the ledger, and this file is stdlib-only with NO SUBPROCESS BY DESIGN — it has to keep working when
    everything else has stopped, which is the only condition under which anyone actually opens it. So,
    exactly like the trunk's gate colour, the verdict is supplied as a FILE by a caller that CAN shell
    out: `python3 research/autonomy/stuck_clock.py --check --json > <path>`, run once a tick by
    `autonomy-tick.yml` on a FULL clone (`fetch-depth: 0`) — where stuck_clock's own shallow-clone
    censoring never even triggers, unlike in a dev sandbox's shallow worktree. Absent file, absent
    reading: `unmeasured`, never green — the same asymmetry `gates_green` already established, and for
    the identical reason: a guessed "probably nothing is stuck" is worse than admitting nobody looked.

    ⛔ ON_RED CLASSIFICATION: see the long comment beside `CONDITION_ON_RED["stalls_are_named"]` — it
    is `advises`, never `redirects` (the row is not a mechanical fix a cycle can perform) and never
    `blocks` (no other row is put at risk by the loop continuing).

    ⚠ THIS DOES NOT EXCLUDE A TERMINAL ROW FROM ANY READY-WORK TABLE. That is a SEPARATE decision,
    made in `handoff.py`'s `top_items()` (which now reads `stuck_clock.terminal_rows()` directly and
    fails OPEN — see its own docstring), so a computed verdict is never re-derived a second way in a
    second module (CLAUDE.md §1) and this board stays a PULL-only reporting surface.
    """
    key = "stalls_are_named"
    label = "has any row gone `stalled_needs_human` — automation stopped trying and it needs a human?"
    source = "stuck_clock.py --check --json (git history of research-ledger.json), via --stall-verdict"
    if not isinstance(stall, dict):
        return _unmeasured(key, label, source, "NO-STALL-VERDICT",
                           f"{stall_err or 'no stall verdict was supplied'}. This checker has no "
                           f"subprocess by design, so it cannot walk git history itself. Settle it: "
                           f"`python3 research/autonomy/stuck_clock.py --check --json > <path>` and "
                           f"pass it with --stall-verdict.")
    rows = stall.get("rows")
    if not isinstance(rows, list):
        return _unmeasured(key, label, source, "STALL-VERDICT-UNREADABLE",
                           "the stall verdict carries no readable `rows` list, so no row can be "
                           "judged.", {"raw_keys": sorted(stall.keys())})
    terminal_state = stall.get("terminal_state") or stuck_clock.TERMINAL_STATE
    terminal = [r for r in rows if isinstance(r, dict) and r.get("terminal")]
    shallow_note = (" ⚠ the clone was SHALLOW when this verdict was taken, so a censored row below "
                    "threshold is not yet decidable — absent from this list is not the same as clear"
                    if stall.get("shallow_clone") else "")
    payload = {
        "open_rows": len(rows),
        "terminal_ids": [r.get("id") for r in terminal] or None,
        "shallow_clone": stall.get("shallow_clone"),
        "history_horizon_utc": stall.get("history_horizon_utc"),
    }
    if terminal:
        names = ", ".join(f"{r.get('id')} (since {(r.get('terminal') or {}).get('since_utc')})"
                          for r in terminal)
        return _red(key, label, source, "STALLED-ROWS",
                    f"{len(terminal)} row(s) are `{terminal_state}`: {names}. Each is a human "
                    f"decision — re-scope it, hand it to a different route, or close it — not queued "
                    f"work for a cycle to keep retrying (stuck_clock.py: 'automation has stopped "
                    f"trying')." + shallow_note, payload)
    return _green(key, label, source, "NO-STALLED-ROWS",
                  f"the verdict was read and no open row is `{terminal_state}`." + shallow_note,
                  payload)


# ═════════════════════════════════════════════════════════════════════ merge with the committed board
def merge(previous, conditions, now):
    """Carry each condition's history forward. State lives IN the artifact — there is no side store.

    Lifted from `alarm_state.merge` and kept deliberately identical in shape, because the two boards
    are read by the same person in the same way. Three things survive a run: WHEN a condition first
    went bad, HOW MANY consecutive runs have seen it, and WHEN its verdict last changed.

    ⚠ `unmeasured` rows count as bad here — that is what makes "unmeasured for six runs" visible, which
    is a different and often worse story than "unmeasured once".

    ⛔ Unlike `alarm_state`, a condition CANNOT vanish: the seven keys are fixed by §5.2 and every run
    emits all seven, so there is no carry-over-a-missing-source case. A key going missing would be a
    code defect, and `test_autonomy_health.py` asserts all seven are present.
    """
    prev = {c["key"]: c for c in (previous or {}).get("conditions", []) if isinstance(c, dict)}
    for c in conditions:
        p = prev.get(c["key"], {})
        changed = p.get("verdict") != c["verdict"]
        c["last_seen_utc"] = _z(now)
        c["last_change_utc"] = _z(now) if changed or not p else p.get("last_change_utc")
        if c["ok"]:
            c["bad_since_utc"], c["consecutive_bad_runs"] = None, 0
        else:
            c["bad_since_utc"] = (_z(now) if (p.get("ok", True) or not p.get("bad_since_utc"))
                                  else p["bad_since_utc"])
            c["consecutive_bad_runs"] = 1 if p.get("ok", True) else int(p.get("consecutive_bad_runs", 0)) + 1
        # ⛔ A SECOND, NARROWER COUNTER — AND THE TWO ARE NOT REDUNDANT, THEY ANSWER DIFFERENT
        # QUESTIONS. `consecutive_bad_runs` counts NOT-OK runs and therefore counts `unmeasured` ones
        # too, which is what makes "unmeasured for six runs" visible; `stall_alarm.py` ages its mail
        # on it, correctly. RESTART_INTENSITY must not: four unmeasured runs followed by one red is
        # not five refusals, and escalating it as if it were would put a §3 interrupt in front of
        # trimcrae for a reading nobody has taken yet. The fix for an unmeasured row is to make the
        # reading possible, which is the distinction this whole module is built around.
        # ⚠ ONE EXPRESSION, AND THE FIRST DRAFT HAD TWO. It also re-checked the PREVIOUS row's state
        # before carrying the count forward — belt and braces that a mutation proved was neither: a
        # previous row that was ok or unmeasured already carries `consecutive_red_runs: 0`, so the
        # extra clause could not change any answer, and no test could be written that failed without
        # it. Unreachable defensive code reads like a mechanism and is not one.
        c["consecutive_red_runs"] = (0 if (c["ok"] or c["unmeasured"])
                                     else int(p.get("consecutive_red_runs", 0)) + 1)
        since = _parse_ts(c["bad_since_utc"] or "")
        c["bad_for_h"] = round(_hours(now, since), 2) if since else None
        c["bad_since_et"] = _et(since)
    return conditions


def intensity_of(condition):
    """The restart-intensity block for one already-merged condition row. Pure, no I/O.

    ⛔ THE ESCALATION IS DUE ON `>=`, NOT `>`. OTP escalates when *more than* MaxR restarts occur in
    the period, i.e. on the (MaxR+1)th; systemd stops *at* the burst. The half-open choice is
    arbitrary either way, so it is made explicitly here rather than left to whoever reads the
    comparison: the Nth consecutive red is the one that escalates, so N is the number of refusals
    trimcrae is asked to accept before he hears about it, which is the number the docstring above
    argues for.
    """
    runs = int(condition.get("consecutive_red_runs") or 0)
    on_red = condition.get("on_red")
    counted = on_red in RETRIED_ON_RED
    exhausted = bool(counted and condition.get("needs_attention") and runs >= RESTART_INTENSITY)
    if not counted:
        why = (f"`{on_red}` rows are retried by nothing, so there is no restart budget to spend — "
               f"a sustained red here is `stall_alarm.py`'s mail, not a §3 escalation")
    elif exhausted:
        why = (f"⛔ INTENSITY EXHAUSTED — red on {runs} consecutive {RESTART_INTENSITY_UNIT} against a "
               f"limit of {RESTART_INTENSITY}. The loop has been responding to this by refusing and "
               f"respawning, and that response has now demonstrably not fixed it. ESCALATE TO "
               f"TRIMCRAE under CLAUDE.md §3 instead of refusing again.")
    else:
        why = (f"red on {runs} of {RESTART_INTENSITY} {RESTART_INTENSITY_UNIT}; the loop may keep "
               f"responding on its own until the budget is spent")
    return {
        "axis": condition.get("axis"),
        "counter": "consecutive_red_runs",
        "unit": RESTART_INTENSITY_UNIT,
        "n": runs,
        "limit": RESTART_INTENSITY,
        "counted": counted,
        "exhausted": exhausted,
        # ⚠ The measured age travels with the count, always. N runs is a lower bound in wall-clock
        # terms because the tick's cron is a request rather than a cadence.
        "bad_for_h": condition.get("bad_for_h"),
        "why": why,
    }


def escalations_due(board):
    """The condition keys whose restart budget is spent. This is the §3 trigger, as a list.

    ⛔ A SEPARATE ANSWER FROM `blocking`, AND THE DIFFERENCE IS THE WHOLE POINT. `blocking` says *do
    not start a cycle*; this says *stop answering this with another automated refusal and put it in
    front of a human*. A row can be blocking for one run (normal, self-healing) and it can be
    blocking for fifty (an outage nobody has been told about). Only the second is an escalation.
    """
    return [c["key"] for c in board.get("conditions", [])
            if (c.get("intensity") or {}).get("exhausted")]


def commit_worthy(previous, board, interval_h, now):
    """`(bool, why)` — does this board SAY anything the committed one did not? `fleet_armed.py`'s rule.

    ⛔ NO WORK, NO COMMIT. Measured cost of ignoring it: 1,476 commits to `main` in 24 h, 703 of which
    said in their own subject line that they did nothing. A board whose seven verdicts are unchanged
    carries no information, and committing it re-times the file for nothing.

    ⭐ AND THE OTHER HALF OF THAT LESSON, WHICH IS THE HALF THAT GETS DROPPED: a checker that goes quiet
    must not read as a checker that keeps saying "fine". The committed board carries its own expiry, so
    it is refreshed whenever it is within one cycle period of that expiry — the keep-alive, exactly as
    `fleet_armed._census_lane_state` refreshes a published census before it ages out. It can therefore
    never be the reason the board looks dead.
    """
    if not isinstance(previous, dict) or not previous.get("conditions"):
        return True, "no committed board exists yet"
    def surface(b):
        # ⛔ `exhausted` IS PART OF THE SURFACE, AND LEAVING IT OUT WOULD HAVE MADE THE ESCALATION
        # UNREACHABLE. A row red for five runs carries the SAME verdict string on each of them, so a
        # surface built from verdicts alone is unchanged at the exact moment the restart budget is
        # spent — the board would say "escalate" and this function would answer "carries no
        # information the last one did not", and the committed copy would never say it. That is the
        # unrun-guard shape this repository has paid for repeatedly (AUT-PD-018, `subagent_width`).
        return sorted((c.get("key"), c.get("verdict"), bool(c.get("ok")), bool(c.get("unmeasured")),
                       bool((c.get("intensity") or {}).get("exhausted")))
                      for c in b.get("conditions", []))
    if surface(previous) != surface(board):
        return True, "a verdict changed"
    expiry = _parse_ts(previous.get("_stale_after_utc") or "")
    if expiry is None:
        return True, "the committed board has no readable expiry, so it cannot be trusted to stay alive"
    period = interval_h if interval_h is not None else FALLBACK_CYCLE_INTERVAL_H
    if now + datetime.timedelta(hours=period) >= expiry:
        return True, (f"keep-alive — the committed board expires {_et(expiry)}, inside one cycle period "
                      f"({period:g} h), and a frozen board must not read as a board that keeps saying fine")
    return False, ("every verdict is unchanged and the committed board is not near its expiry — this run "
                   "carries no information the last one did not")


def build(*, ledger_path=DEFAULT_LEDGER, state_path=DEFAULT_STATE, receipts_dir=DEFAULT_RECEIPTS,
          authority_path=DEFAULT_AUTHORITY, gates_path=None, stall_path=None,
          health_path=DEFAULT_HEALTH, now=None, previous=None):
    """The whole board. Pure function of the files it is pointed at plus `now` — no hidden inputs."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    ledger, ledger_err = _read_json(ledger_path)
    state, state_err = _read_json(state_path)
    authority, authority_err = _read_json(authority_path)
    gates, gates_err = (_read_json(gates_path) if gates_path else (None, None))
    # ⚠ SAME SHAPE AS `gates_path` ABOVE, FOR THE SAME REASON: this module has no subprocess, so a
    # verdict that requires one (stuck_clock's git walk) is a FILE this function only reads.
    stall, stall_err = (_read_json(stall_path) if stall_path else (None, None))
    receipts, unreadable = load_receipts(receipts_dir)
    entries = ledger.get("entries") if isinstance(ledger, dict) else None
    if entries is not None and not isinstance(entries, list):
        entries, ledger_err = None, f"{os.path.basename(ledger_path)} carries a non-list `entries`"
    if isinstance(ledger, dict) and entries is None and not ledger_err:
        ledger_err = f"{os.path.basename(ledger_path)} carries no `entries`"
    interval_h, interval_basis = cycle_interval_hours(state)

    conditions = [
        c_cycle_delivering(receipts, unreadable, interval_h, now),
        c_advancing_live_work(receipts, now),
        c_evidence_moving(entries, ledger_err, interval_h, now),
        c_blocks_are_real(entries, ledger_err),
        c_queue_is_takeable(entries, ledger_err),
        c_scores_are_reachable(entries, ledger_err),
        c_cycles_are_sized(receipts, state, state_err),
        c_fanout_is_governed(receipts, state, state_err),
        c_budget_recovering(state, state_err, now),
        c_gates_green(gates, gates_err, now),
        c_authority_respected(receipts, authority, authority_err),
        c_stalls_are_named(stall, stall_err),
    ]
    if previous is None:
        previous, _ = _read_json(health_path)
    conditions = merge(previous, conditions, now)
    # ⚠ Stamped from ONE table rather than passed through ten constructors: a classification threaded
    # through every call site is a list somebody must remember to extend, and this file has already
    # paid for that shape twice today.
    for c in conditions:
        c["on_red"] = CONDITION_ON_RED.get(c["key"], "blocks")
        # ⚠ SAME ONE-TABLE STAMPING AS `on_red`, FOR THE SAME REASON. And the default is the axis
        # whose response is the most conservative available: an unclassified row must never be
        # readable as "self-only, safe to restart into".
        c["axis"] = CONDITION_AXIS.get(c["key"], "readiness")
        c["intensity"] = intensity_of(c)
    blocking = [c["key"] for c in conditions if c["needs_attention"]
                and c.get("on_red") == "blocks"]

    period = interval_h if interval_h is not None else FALLBACK_CYCLE_INTERVAL_H
    stale_after = now + datetime.timedelta(hours=STALE_AFTER_CYCLES * period)
    attention = [c["key"] for c in conditions if c["needs_attention"]]
    unmeasured_keys = [c["key"] for c in conditions if c["unmeasured"]]
    board = {
        "_what": "THE AUTONOMY LOOP'S HEALTH BOARD, AS A FILE. The CONDITION_ORDER conditions (see "
                 "that constant for the current count and any DECLARED additions), when each was "
                 "measured, how long it has been that way, and when this file should be considered "
                 "dead. Written by research/autonomy/health.py.",
        "_read_this_when": "you want to know whether the unattended research loop is WORKING — not "
                           "whether what it wrote is correct, which every preflight gate already covers "
                           "(§5.1). A loop can be perfectly correct and advance nothing.",
        "_owner": "research/manuscripts/program/emc-autonomy-architecture.md#52--loop-health--new-and-it-"
                  "is-what-never-check-in-actually-requires",
        "_this_channel_is_PULL_ONLY": "nothing here sends, opens an issue, comments, or fails a run. §7 "
                                      "trigger 4 is the ONE push, and it is the caller's act, not this "
                                      "file's: a condition red past its deadline earns a "
                                      "PushNotification and a line in the Friday digest, nothing else.",
        "_generated_utc": _z(now), "_generated_et": _et(now),
        "_cycle_interval_h": interval_h,
        "_stale_window_basis": interval_basis,
        "_stale_after_utc": _z(stale_after), "_stale_after_et": _et(stale_after),
        "_stale_after_means": (
            f"IF THE CLOCK IS PAST THIS AND THIS FILE HAS NOT CHANGED, NOTHING IS CHECKING THE LOOP and "
            f"every verdict below is a memory, not a measurement. The deadline is written INTO the "
            f"artifact because a checker that has stopped cannot report that it stopped — it needs no "
            f"process, no API and no clock but yours. {STALE_AFTER_CYCLES:g} missed cycles at "
            f"{period:g} h. Restart it: `gh workflow run autonomy-tick.yml --ref main`."),
        "ok": not attention,
        "_ok_means": (
            "no condition is FAILING. ⛔ IT DOES NOT MEAN EVERY CONDITION WAS MEASURED — read "
            "`fully_measured` and `unmeasured` beside it. `ok: true, fully_measured: false` is the "
            "honest shape of a loop nobody can yet grade, and it is NOT a healthy loop."),
        "fully_measured": not unmeasured_keys,
        "n_conditions": len(conditions),
        "needs_attention": attention,
        # ⛔ THE ROWS THAT ACTUALLY STOP A CYCLE — a strict subset of `needs_attention`, and the only
        # thing `--check` gates on. See CONDITION_ON_RED for why the two are not the same thing.
        "blocking": blocking,
        "_blocking_means": (
            "research-loop §1's stop condition. A red row that is NOT here is reported and escalated "
            "but must never stop the loop, because a cycle cannot act on it. On 2026-08-27 the "
            "distinction did not exist, every red stopped the loop, and two retrospective conditions "
            "about immutable committed history wedged it permanently."),
        # ⛔ THE RESTART-INTENSITY ANSWER: rows the loop has now retried past its budget. Empty is the
        # normal state and is not the same as `blocking` being empty — see `escalations_due`.
        "escalations": [],                                  # filled below; the board must exist first
        "_escalations_means": (
            f"⛔ A §3 ESCALATION IS DUE. Each key here has been RED on {RESTART_INTENSITY} or more "
            f"consecutive {RESTART_INTENSITY_UNIT} while the loop's only response was to refuse or "
            f"redirect — OTP's `intensity`/`period` and systemd's `StartLimitBurst`, ported: neither "
            f"lets a supervised thing fail forever in silence, and before this counter existed this "
            f"loop did. The correct next act is NOT another cycle and NOT another refusal; it is a "
            f"CLAUDE.md §3 block put to trimcrae. `stall_alarm.py` mails it from the Actions clock, "
            f"and `research-loop` §1 makes a cycle that reads it produce the block rather than a "
            f"twelfth identical receipt. ⚠ The count is in board runs, not hours — read `bad_for_h` "
            f"beside it for the measured age."),
        "_restart_intensity": RESTART_INTENSITY,
        "unmeasured": unmeasured_keys,
        "_unmeasured_means": (
            "⛔ A VERDICT THAT COULD NOT BE REACHED — NOT a condition that is fine. It is listed apart "
            "from needs_attention because the fix is different: make the reading possible first. "
            "CLAUDE.md §4: an absent reading is not a reading of absence. Anything that grades an "
            "unmeasured condition as green has manufactured a green board out of missing data."),
        "conditions": sorted(conditions, key=lambda c: (c["ok"], CONDITION_ORDER.index(c["key"]))),
    }
    board["escalations"] = escalations_due(board)
    if unreadable:
        board["_receipts_unreadable"] = unreadable
        board["_receipts_unreadable_means"] = (
            "a receipt file exists and would not parse. It is NOT counted as a delivered cycle and NOT "
            "silently skipped — a corrupt receipt is a broken writer, not a quiet loop.")
    worth, why = commit_worthy(previous, board, interval_h, now)
    board["_commit_worthy"] = worth
    board["_commit_worthy_why"] = why
    board["_commit_worthy_means"] = (
        "fleet_armed.py's discipline: the caller COMMITS this file only when this is true. A board "
        "whose verdicts are unchanged carries no information (measured cost of ignoring that: 1,476 "
        "commits in 24 h, 703 of them non-events), and the keep-alive clause makes sure a live checker "
        "can never be the reason the board looks dead.")
    return board


# ═════════════════════════════════════════════════════════════════════════════════════════════ render
_GLYPH = {True: "✅", False: "⛔"}


def render(board, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    stale_after = _parse_ts(board.get("_stale_after_utc") or "")
    dead = stale_after is not None and now > stale_after
    lines = [
        f"[loop-health] generated {board.get('_generated_et')} · this file goes stale after "
        f"{board.get('_stale_after_et')}"
        + ("   ⛔ AND IT IS PAST THAT — NOTHING IS CHECKING THE LOOP" if dead else ""),
        f"[loop-health] cycle period: {board.get('_stale_window_basis')}",
        "[loop-health] PULL ONLY — nothing was sent, no issue opened, no run failed.",
    ]
    for c in board.get("conditions", []):
        glyph = "🔎" if c["unmeasured"] else _GLYPH[c["ok"]]
        age = (f" · bad for {c['bad_for_h']:.1f} h ({c['consecutive_bad_runs']} run(s))"
               if c.get("bad_for_h") else "")
        axis = f" [{c.get('axis', '?')[:4]}]"
        lines.append(f"[loop-health] {glyph} {c['key']:<21}{axis} {c['verdict']:<24} {c['label']}{age}")
        if not c["ok"]:
            lines.append(f"[loop-health]      {c['detail']}")
        if (c.get("intensity") or {}).get("exhausted"):
            lines.append(f"[loop-health]      {c['intensity']['why']}")
    att, unm = board.get("needs_attention", []), board.get("unmeasured", [])
    lines.append(f"[loop-health] {len(att)} need attention {att or ''} · {len(unm)} UNMEASURED "
                 f"{unm or ''} — unmeasured is not ok · {board.get('n_conditions')} condition(s)")
    esc = board.get("escalations", [])
    lines.append(
        f"[loop-health] ⛔ ESCALATE TO TRIMCRAE (§3) — restart intensity spent on {esc}"
        if esc else
        f"[loop-health] restart intensity: no condition has been retried past "
        f"{board.get('_restart_intensity', RESTART_INTENSITY)} consecutive red runs")
    lines.append(f"[loop-health] commit-worthy: {board.get('_commit_worthy')} — "
                 f"{board.get('_commit_worthy_why')}")
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════════════════════════ cli
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--state", default=DEFAULT_STATE)
    ap.add_argument("--receipts", default=DEFAULT_RECEIPTS)
    ap.add_argument("--authority", default=DEFAULT_AUTHORITY)
    ap.add_argument("--gates-verdict", default=None,
                    help="JSON written by the caller that CAN read Actions; absent = gates_green is "
                         "unmeasured, never green")
    ap.add_argument("--stall-verdict", default=None,
                    help="JSON from `stuck_clock.py --check --json`, written by a caller that CAN "
                         "shell out to git; absent = stalls_are_named is unmeasured, never green")
    ap.add_argument("--health", default=DEFAULT_HEALTH, help="the committed board; read for history")
    ap.add_argument("--write", action="store_true", help="persist the board (otherwise print only)")
    ap.add_argument("--commit-worthy", action="store_true",
                    help="exit 0 if this board says something the committed one did not, 10 if not. "
                         "For autonomy-tick.yml's no-work-no-commit step — 10 rather than 1 because "
                         "'nothing to say' is the rule working, not a failure")
    ap.add_argument("--stored-commit-worthy", action="store_true",
                    help="exit 0/10 on the `_commit_worthy` ALREADY RECORDED in --health, instead of "
                         "recomputing it. This is what a caller that has just run --write must use: "
                         "after --write the file is this run's own output, so --commit-worthy would "
                         "compare the board against itself and always answer 'unchanged'")
    ap.add_argument("--escalations", action="store_true",
                    help="exit 1 if any condition has been red past RESTART_INTENSITY consecutive "
                         "runs while the loop kept refusing or redirecting — the §3 trigger. A "
                         "SEPARATE question from --check: --check asks whether a cycle may start, "
                         "this asks whether a human must now be told")
    ap.add_argument("--check-any", action="store_true",
                    help="exit 1 if ANY condition is red, blocking or not (the pre-2026-08-27 "
                         "behaviour; not what a cycle's stop condition should use)")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any condition needs attention (unmeasured does NOT exit 1 — it is "
                         "not a failing loop, it is an unreadable one, and the fix is different)")
    a = ap.parse_args(argv)

    now = datetime.datetime.now(datetime.timezone.utc)
    board = build(ledger_path=a.ledger, state_path=a.state, receipts_dir=a.receipts,
                  authority_path=a.authority, gates_path=a.gates_verdict, stall_path=a.stall_verdict,
                  health_path=a.health, now=now)
    print(render(board, now))
    if a.write:
        with open(a.health, "w", encoding="utf-8") as fh:
            json.dump(board, fh, indent=2)
            fh.write("\n")
        print(f"[loop-health] wrote {a.health}")
    if a.stored_commit_worthy:
        # ⭐⭐ THE DECISION IS READ, NOT RECOMPUTED, AND THAT IS THE WHOLE POINT OF THIS FLAG.
        # `--write` computes `commit_worthy()` against the board that was on disk BEFORE it wrote,
        # i.e. the committed one, and stores the answer in `_commit_worthy`. That is the only moment
        # the comparison can be made, because writing destroys the thing being compared against.
        # ⛔ MEASURED 2026-08-28, and it had silently frozen the trunk's board. `autonomy-tick.yml`
        # ran `--write` and then `--commit-worthy` as a separate step on the same `--health` path.
        # The second invocation re-read the file the first had just overwritten, found it identical
        # to what it had just computed, and answered "every verdict is unchanged" — so the board was
        # committed only via the keep-alive expiry path, never on a verdict change. One tick's log
        # carries both lines: "commit-worthy: True — a verdict changed" from --write, then
        # "commit-worthy: False" from --commit-worthy, on the same data seconds apart. The trunk's
        # committed board therefore read `gates_green: NO-GATE-VERDICT / unmeasured` from
        # 2026-08-26 onward while CI was measuring that row correctly on every tick — and
        # research-loop §1 tells every cycle to read that board before it starts.
        # ⛔ AND THIS IS NOT FIXABLE BY GUESSING INSIDE `--commit-worthy`. "Is the board on disk my
        # own output?" has no safe answer: a genuinely committed board ALSO carries
        # `_commit_worthy: true`, because that is why it was committed. A heuristic that trusted the
        # stored flag whenever the surface matched would commit an unchanged board on every tick —
        # the 1,476-commits-in-24-h defect `commit_worthy` exists to prevent. So the ordering is
        # fixed at the CALLER, and this flag is how the caller obeys the decision already made.
        stored, _ = _read_json(a.health)
        worth = bool((stored or {}).get("_commit_worthy"))
        why = (stored or {}).get("_commit_worthy_why") or (
            "no `_commit_worthy` recorded in %s — nothing was written there by a --write run" % a.health)
        print(f"[loop-health] commit-worthy (as recorded by --write): {worth} — {why}")
        return 0 if worth else 10
    if a.commit_worthy:
        # ⛔⛔ NEVER CALL THIS AFTER `--write` ON THE SAME `--health` PATH — USE `--stored-commit-worthy`.
        # It compares the board it just computed against the file at `--health`, so once `--write` has
        # replaced that file the comparison is the board against itself and the answer is always
        # "unchanged". See the block above for the measurement; this flag is correct only BEFORE a write.
        # ⭐ Exposes `commit_worthy()` to a shell caller so `autonomy-tick.yml` obeys the no-work-no-commit
        # rule by ASKING this module rather than reimplementing its four-argument plumbing in YAML — a
        # second copy of that logic is exactly the drift `fleet_armed.py` was consolidated to end.
        # Exit 10, not 1: "nothing to say" is the rule working, and must not render like a failure.
        previous, _ = _read_json(a.health)
        state, _ = _read_json(a.state)
        interval_h, _ = cycle_interval_hours(state)
        worth, why = commit_worthy(previous or {}, board, interval_h, now)
        print(f"[loop-health] commit-worthy: {worth} — {why}")
        return 0 if worth else 10
    if a.escalations:
        # ⚠ INDEPENDENT of `--check` and `--check-any`, and placed BEFORE both on purpose — a caller
        # passing two gates gets the stronger statement, and a gate nested inside another is a gate
        # that silently never fires (the `--check-any` defect recorded below, found on its first run).
        return 1 if board.get("escalations") else 0
    if a.check:
        # ⚠ The ONLY non-zero path in this module. Everything else exits 0 on purpose: a red run is a
        # push channel (GitHub mails the repo owner), and reintroducing that is what alarm_state.py's
        # whole design removed. A caller that wants the gate asks for it.
        # ⛔ ONLY A RED `blocks` ROW STOPS A CYCLE — see CONDITION_ON_RED. Before 2026-08-27 this
        # returned 1 for ANY red, which let two retrospective conditions about immutable history
        # wedge the loop permanently. `--check-any` keeps the old behaviour for a caller that
        # genuinely wants "is anything red at all".
        return 1 if board.get("blocking") else 0
    if a.check_any:
        # ⚠ Handled INDEPENDENTLY of `--check`, not nested inside it. Nested, the flag did nothing
        # unless both were passed — a flag that reports while measuring nothing, caught on first run.
        return 1 if board["needs_attention"] else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
