#!/usr/bin/env python3
"""WORK LEDGER — every open item has an OWNER, or it has an ENTRY SAYING IT DOES NOT.

THE DEFECT THIS EXISTS TO CLOSE (trimcrae, 2026-07-27: *"We need a much better system to make sure things
don't silently stall. I feel like once an hour I catch something like that. Design something robust so I
don't have to keep poking it."*).

    ★★ WORK WITH NO OWNER IS INDISTINGUISHABLE FROM WORK IN PROGRESS.

That one sentence covers every instance from the day this was commissioned, and they are not a genre — they
are five separate mechanisms with one shared shape:

  1. The closure triangle sat IDLE ~3 h after `triangle-prime` succeeded. The lane that would have dispatched
     the next step ended its turn, and nothing picked it up. There was no live instance, so every liveness
     check read it as "nothing to watch".
  2. Two fan-out units drew rentals for ~6 h with ZERO committed iterations across 48 snapshots, on a board
     that was yielding 1-3 placeable hosts per tick — so those rentals were also displacing units that would
     have advanced.
  3. The placer ran GREEN for ~2 h placing nothing (a guard inverted on a null input); the fleet decayed
     18 -> 5 while every tick reported success.
  4. The valB ternary legs failed 6/6 across three cohorts before anybody noticed the pattern.
  5. ⚠ AND THE ONE THAT NAMES THE BUG EXACTLY: a row on the coordinator's IN FLIGHT board claimed an owner
     THAT HAD NEVER BEEN DISPATCHED. The board is prose written from memory, so it can assert anything —
     including an owner that does not exist. Nothing could have caught that, because nothing was checking
     the board against reality; the board WAS the record.

Failure 5 is why §4 of this module (the renderer) is load-bearing rather than cosmetic. The board is
GENERATED FROM THE LEDGER, so **if there is no ledger entry, no row can be rendered** — a claimed owner that
does not exist becomes unwritable rather than merely discouraged.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
WHY THE EXISTING WATCHERS DO NOT CLOSE IT (and are CONSUMED here, never duplicated)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
`fleet-supervision-alarm.yml` and `lane_staleness_watch.py` both key on LIVE COMPUTE. A lane with nothing
running reads to both as "nothing to watch" — which is precisely the triangle case, failure 1, the one
`lane_staleness_watch`'s own docstring flags as "THE ONE NOTHING DETECTS". `lane_staleness_watch` closed it
for the five lanes IT knows about, by naming them in a registry. This module asks the strictly larger
question: **is there anything, anywhere in the plan, that nobody is carrying?** Lanes are one of its inputs,
not its subject.

So `lane_staleness_watch.build_report` is CALLED here, and its verdicts become entries. Its thresholds are
IMPORTED, never re-typed (§1). Nothing about lane liveness is re-implemented.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
★★ WHAT IS SCANNED, AND WHAT IS KNOWINGLY NOT — the honest statement of this system's coverage
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
A CATEGORY WITH NO SCANNER IS INVISIBLE, and an invisible category looks exactly like a healthy one. So the
list below is not documentation of the implementation, it IS the coverage claim, and it is the first thing to
re-read when something stalls anyway. `SCANNERS` is the machine copy; `test_work_ledger.py` asserts the two
agree, so this list cannot rot away from the code.

SCANNED — a stall in one of these produces an entry:

  `plan_items`     `[ ]` / `[~]` / `[!]` items in the roadmap's ORDERED PLAN. Catches "the plan says to do
                   it and nobody is". An item with no gate text and no owner is the purest form of the
                   defect. `[!]` (result under correction) counts as OPEN: a verdict landed and stopped
                   standing, which is more decision-relevant than an item never started.
  `fanout_units`   Step-1 fan-out units whose COMMITTED-ITERATION count has not advanced. Failure 2. The
                   fingerprint is `committed_scalar` and nothing else — see the hazard list below for why
                   `phase`, `gpu_util` and `cur_state` are all excluded.
  `handoff`        A gate that said `dispatched` with no rental, dispatch or terminal record following it.
                   Failure 1's mechanism, caught at the seam rather than 3 h later: the launch ledger pairs
                   every `dispatched` with what it produced, and an UNPAIRED one is a hand-off that
                   evaporated.
  `rung_gates`     Rungs whose gate has NEVER RETURNED A VERDICT, walked on `degrader-paper-schedule.json`'s
                   real `depends_on` graph: every dependency satisfied and the milestone's own status still
                   `pending` or `under_correction` -> unblocked, and nobody carrying it. A rung with no
                   verdict is not a rung that failed; it is a rung nobody asked about. (Built first as a
                   NAME cross-check between the ladder and the plan; that version raised three false
                   positives on the real files, including the lane that was billing six hosts at the time,
                   and was replaced rather than tuned.)
  `lanes`          Every non-OK verdict from `lane_staleness_watch` (BILLING-NOT-ADVANCING, IDLE-UNEXPECTED,
                   HOLD-NOT-PRICE, TICK-NOT-MEASURING, UNKNOWN). Failures 1, 3 and 4 as that module grades
                   them. Its OK verdicts become entries too, as `advancing` / `held` / `done` — a healthy
                   lane still needs a row, or the board cannot render it.
  `self`           The ledger itself. See "IF THIS STOPS RUNNING" below.

NOT SCANNED — a stall in one of these is invisible to this module, and that is a choice, not an oversight:

  * ANYTHING WHOSE ONLY EVIDENCE IS IN S3 OR GCS. Same reason `lane_staleness_watch` refuses: a watcher
    holding the same credential as the thing it watches dies with it, and a dead credential is one of the
    failures being watched for (two 5a-KS legs, ~53 min at 0 % GPU on exactly that). Per-iteration ternary
    progress therefore cannot be seen here at all.
  * GCP VM LIVENESS, in either direction — provably not in git (CLAUDE.md §6: GCE refuses the in-VM
    self-delete, so a finished leg leaves a RUNNING VM; and an enabled watch entry may correspond to no VM).
  * WHETHER A RESULT IS SCIENTIFICALLY RIGHT. A wrong number that lands on schedule is indistinguishable
    here from a right one. This module measures whether work MOVED, never whether it moved correctly.
  * WORK THAT EXISTS ONLY IN AN AGENT'S HEAD OR IN A CHAT MESSAGE. ⚠ THIS IS THE LARGEST HOLE AND IT IS
    STRUCTURAL: if a decision was never written into the roadmap, a watch list or an artifact, there is
    nothing on disk to scan and this module will never know it was owed. The mitigation is not code — it is
    that an item recorded here is recorded FOREVER until its evidence lands, so the fix for "the ledger
    missed it" is to write it into the plan, once.
  * THE AGENT TASK LIST (`TaskCreate`/`TaskUpdate`). Not a committed artifact; it does not survive a session
    and cannot be read from CI.
  * THE MANUSCRIPT, REVIEWER LISTS, `method-watch.md`, `IDEAS.md` AND `emc-treatment-strategy.md` backlogs.
    Prose backlogs with no machine-readable completion signal — a scanner over them would produce entries
    that can never reach `done`, and an entry that can never close is noise that teaches people to skim the
    board. The roadmap's ORDERED PLAN is scanned precisely BECAUSE its checkboxes are a completion signal.
  * COST CORRECTNESS. Whether the ladder's numbers are right is `vast_cost_model.py`'s job and
    `lint_consistency.py`'s. This module only points at them.
  * THE NAME CORRESPONDENCE BETWEEN `vast-ladder-repricing.json`'s PRICED RUNGS AND THE SCHEDULE'S
    MILESTONE IDS. Three ladder rungs have no id-shaped counterpart (`5a-KS primary`,
    `5c ensemble refinement`, `local within-basin FEP`), so a rung could in principle be priced with no
    milestone at all and go unnoticed here. It is not checked because every fuzzy rule tried against the
    real files produced ONLY false positives, and a checker that cries wolf gets switched off within a day —
    which would cost more coverage than this gap does. Closing it properly means giving the ladder and the
    schedule a shared key, which is a change to those files, not to this one.
  * WHETHER THE ROADMAP'S PLAN MARKERS AGREE WITH THE SCHEDULE'S STATUSES. Both are scanned, neither is
    reconciled against the other, for the same reason: the join is prose-title to id.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
★★ AUTO-ASSIGN EVERYTHING, NEVER ESCALATE (trimcrae's ruling, 2026-07-27)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
The ledger dispatches the next action itself and does NOT surface stalls to him. He chose this knowing the
risk, and named it: *"a genuinely broken item could loop indefinitely and burn rentals while looking busy."*
Four engineered answers to that exact risk, each testable:

  1. ★ RETRIES ARE BOUNDED. `MAX_FRUITLESS_ATTEMPTS` automatic attempts that produce NO NEW EVIDENCE and the
     item becomes `blocked`, carrying the evidence of each failure, and STOPS BEING RETRIED. An attempt only
     counts as fruitless if the evidence fingerprint is unchanged since it was made — a dispatch that WORKED
     resets the budget, so a slow-but-live item is never blocked for being slow. `blocked` is permanent until
     something changes, and "something changes" is defined mechanically: the fingerprint moves, or a blocker
     clears. It is never a silent drop and never a loop.
  2. ★ ESCALATION-FREE IS NOT INVISIBLE. Every entry stays in `work-ledger.json` and on the generated board,
     `blocked` ones most loudly of all. "Never escalate" means do not interrupt him — NOT do not record. A
     blocked item that vanished from the board would be a worse defect than the one this replaces.
  3. ★ IT MAY NEVER BYPASS A SPEND GATE. Every dispatch goes through the lane's OWN existing path, behind the
     absolute buy line and the derived per-unit dollar ceiling
     (`congeneric_fanout.unit_ceiling_components`). This module names a workflow and nothing else: the
     dispatch allowlist REFUSES any input whose name is in the price vocabulary (`_FORBIDDEN_INPUT_TOKENS`),
     so it is structurally incapable of passing a bid, a ceiling or a ratio. It never raises a bid.
     ⚠ AND A PRICE HOLD IS A LEGITIMATE RESTING STATE, NOT A STALL. §6 — *"I'd rather pause until
     availability opens than pay double per ns"* — makes a hold a SUCCESS. A held entry gets no auto-action,
     accrues no attempts, and can never decay into `blocked`. Retrying a price hold would be this module
     spending money to defeat the guard that was saving it.
  4. ★ IT MAY NEVER TAKE A DESTRUCTIVE ACTION. No destroy, reap, condemn or blacklist. Those stay in the
     lanes' own `collect` paths, which read the start response that separates "outbid, restartable" from
     "GPU gone, destroy it". Asserted by AST in `test_work_ledger.py`, the same way `lane_staleness_watch`
     asserts report-only — a structural property, not a promise in a docstring.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
★★ IF THIS STOPS RUNNING (the question 5b asks, answered plainly)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
Then everything it watches goes quiet in exactly the way it exists to prevent, and — stated without hedging —
**A SUPERVISOR THAT HAS STOPPED CANNOT REPORT THAT IT STOPPED.** No amount of self-checking inside this
module fixes that; the detection has to be possible from OUTSIDE it, with nothing running.

So the artifact carries its own expiry. `work-ledger.json` is written with `_stale_after_utc` — a deadline
computed at write time from the cadence it expects. A reader who does nothing but open the file can compare
one field to the clock and know the ledger is dead. That is the whole mechanism, and it works because it
needs no process:

  * a human, or the next agent session, reading the file;
  * `self_check()` here, which any module may call on the committed doc;
  * `fleet_supervision_alarm.classify` — the SAME throttle-immune generation test the fleet uses — pointed at
    `work-ledger.json` and `step1-fanout-supervisor.yml`, because this artifact is exactly "a file the tick
    writes" and so is eligible for the strong test rather than an age threshold. Reused, not re-derived (§1).

⚠ AND THE HONEST WEAKNESS, STATED RATHER THAN ENGINEERED AROUND: the primary cadence is
`step1-fanout-supervisor.yml`'s self-chain, and a self-chain is a SINGLE POINT OF FAILURE — if a run dies
before it re-dispatches, the chain ends silently. That is mitigated by two INDEPENDENT triggers (the
`if: always()` tail of `step1-fanout-autoscale.yml`, which fires on a different chain, and a cold-start cron
which CLAUDE.md §6 says must never be relied on and is here only as a floor), and it is NOT eliminated. A
`schedule:` is not a cadence — measured delivery on this repo is 141-238 min against a `*/20` request — so
the cron is a backstop of last resort and says so.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
HAZARDS, ALL MEASURED 2026-07-27 — the reasons the signals here are the ones they are
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
⚠ `cur_state` IS NOT A LIVENESS SIGNAL and `exited` is routinely TRANSIENT — three instances read `exited`
  and were running again 21 min later. Host state is reported, never condemning.
⚠ `gpu_util` IS NOT DIAGNOSTIC — 0.0 on genuinely advancing hosts. Never read; asserted by AST.
⚠ ONLY THE COMMITTED-ITERATION CENSUS CONDEMNS. `phase` is excluded from every fingerprint even though it
  looks tempting, because it carries a timestamp that moves each tick — including on a unit that has been
  dead for hours. A fingerprint containing `phase` would mask the exact failure this scans for.
⚠ ARTIFACT AGE ALONE CANNOT WORK. An honest age threshold sits above ~240 min (measured delivery), while a
  real incident was 115 min stale and would have read FRESH throughout. Where a generation test is available
  it is used instead, via `fleet_supervision_alarm`; where it is not, the module says so in the entry rather
  than substituting a weaker check silently.
⚠ TIME CI FROM THE COMPLETED RECORD, NEVER A LIVE POLL. The jobs API reported a finished 3-minute step as
  `in_progress` for ~18 min. Nothing here polls a live run.
⚠ AN ERROR'S OWN EXPLANATION HAS BEEN WRONG THREE TIMES IN ONE DAY. Every state here is derived from a
  measurement, never from a message — and a field that could not be read is UNREADABLE, never a default. An
  unmeasured state rendered as a measured zero is this repo's most expensive defect class.

Usage:
    python3 work_ledger.py [--root DIR] [--ledger PATH] [--plan-doc PATH] [--schedule PATH]
                           [--now ISO8601Z] [--board] [--json OUT] [--write]
                           [--emit-dispatch PATH] [--no-api] [--strict]
Exit 0 always unless the ledger itself could not be built: this is a RECORD, and per the ruling above it does
not escalate. `--strict` fails the run when an entry is `blocked`, for a caller that wants that.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ⚠ THE ONLY TWO NON-STDLIB IMPORTS, AND BOTH ARE WATCHERS, NOT LANES. `lane_staleness_watch` imports only
# stdlib and `fleet_supervision_alarm`; `fleet_supervision_alarm` imports only stdlib. So the dependency
# property that matters is preserved transitively: THIS MODULE CANNOT DIE OF A FAULT IN A LANE IT WATCHES.
# That is not a style preference — on 2026-07-27 the 11:37 AM tick took its own progress check down because
# the check shared a dependency with the thing it was checking.
# Everything cost-related (`inflight_usd_per_ns`, `congeneric_fanout`, `vast_cost_model`) is imported LAZILY
# inside the renderer, so a fault in the cost model degrades ONE COLUMN of the board instead of erasing the
# ledger. `test_work_ledger.py` asserts by AST that those imports never move to module scope.
import fleet_supervision_alarm as fsa               # noqa: E402
import lane_staleness_watch as lsw                  # noqa: E402

ET = datetime.timezone(datetime.timedelta(hours=-4))  # EDT. CLAUDE.md §1: always US Eastern, 12-hour.

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LEDGER = os.path.join(HERE, "work-ledger.json")
#: ⚠ THE PLAN DOCUMENT MOVED (2026-08-02). `THE ORDERED PLAN` used to live in STRATEGY.md; the roadmap merge
#: physically moved it — heading string, bullet format and `###` rung sub-headings all unchanged — into
#: `nr4a3-program-map.md`, which is now the single document the program is steered by. STRATEGY.md keeps only
#: Appendix A and Appendix B. Pointing this at the old path is the silent failure `scan_plan_items` exists to
#: shout about: the scanner would report NOT SCANNED and the whole plan layer would vanish from the board.
DEFAULT_PLAN_DOC = os.path.join(HERE, "..", "manuscripts", "nr4a3-program-map.md")
DEFAULT_STRATEGY = DEFAULT_PLAN_DOC                # backwards-compatible alias; do not add a second path
#: The MACHINE MIRROR of the ORDERED PLAN. It carries `id`, `status` and `depends_on`, so
#: the "is this rung blocked" question is answerable exactly, against a real graph, with no name matching.
DEFAULT_SCHEDULE = os.path.join(HERE, "..", "manuscripts", "degrader-paper-schedule.json")
REPO = "trimcrae/Rare-cancers"

# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# thresholds
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⚠ NOTHING HERE RE-TYPES A THRESHOLD THAT ALREADY HAS A HOME (§1). The evidence windows for a lane belong to
# `lane_staleness_watch` and are IMPORTED; the supervision windows belong to `fleet_supervision_alarm` and are
# imported through it. The buy line and every dollar ceiling belong to `congeneric_fanout` /
# `inflight_usd_per_ns` and this module never states one — it names the gate and lets the gate decide.

#: How many automatic attempts may produce NO NEW EVIDENCE before an item is `blocked` and stops being retried.
#: ★ THE BASIS, so this is a measurement rather than a taste: the two dead fan-out units drew rentals for ~6 h.
#: At the supervisor's 8-minute cadence that is ~45 opportunities to notice. Three is enough to separate "the
#: dispatch did not take" (transient — a preemption, a capacity refusal, a lost run) from "this item is
#: broken", and it bounds the wasted rentals at THREE rather than FORTY-FIVE. Raising it re-opens exactly the
#: risk trimcrae named when he chose auto-assign; lowering it would block on ordinary spot churn, which §6
#: says to mention lightly and recover from, not to escalate.
MAX_FRUITLESS_ATTEMPTS = 3

#: How long after a dispatch we may still be waiting for the evidence it was supposed to produce, before that
#: attempt is graded fruitless. ★ MEASURED, from today's launch ledger: the gate->rental hand-offs ran
#: 0.7 to ~22 min (19:38:47Z dispatched -> 20:00:29Z launched being the slowest). 40 min is comfortably past
#: the worst observed hand-off, so a slow-but-working dispatch is never counted against the retry budget.
#: ⚠ It is NOT an artifact-age threshold and must not be compared to one: it starts at OUR dispatch, so
#: GitHub's scheduled-delivery gaps (141-238 min) do not enter it. Nothing here polls a live run to decide it.
DISPATCH_ACK_MIN = 40.0

#: The cadence this ledger EXPECTS to be run at, and the multiple of it after which the committed artifact
#: declares itself stale. ★ DERIVED FROM THE SUPERVISOR'S OWN SETTINGS, not chosen here:
#: `step1-fanout-supervisor.yml` runs an in-job loop at `tick_every_min` (default 8) and dispatches
#: `lane-staleness-watch.yml` — the workflow this module runs inside — every `watch_every_ticks` (default 2).
#: 8 x 2 = 16 min. It is NOT a `schedule:` interval and must not be compared to one: measured GitHub
#: scheduled delivery on this repo is 141-238 min, and a deadline built on that would be useless. If the
#: supervisor's inputs ever change, this becomes a slightly-LATE alarm, never a false one.
_SUPERVISOR_TICK_EVERY_MIN = 8.0
_WATCH_EVERY_TICKS = 2.0
EXPECTED_TICK_MIN = _SUPERVISOR_TICK_EVERY_MIN * _WATCH_EVERY_TICKS
#: 3 missed ticks. Small on purpose: this deadline is read by a human opening a file, so it must be tight
#: enough to be worth reading, and a false "stale" here costs nothing but a second look.
STALE_AFTER_TICKS = 3.0


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# states
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★ ONE STATE NAME, ONE MEANING. The precedent is `lane_staleness_watch`'s hold classification, where four
# different situations wearing one boolean was itself the bug: grading them all quiet loses a night, grading
# them all loud teaches the reader to ignore the alarm.
OPEN = "open"              # needs an owner or a dispatch; one may or may not be available
DISPATCHED = "dispatched"  # we asked; waiting for the evidence that asking produced something
ADVANCING = "advancing"    # evidence moved since the last scan. Nothing to do.
HELD = "held"              # a gate is legitimately refusing to buy. A RESTING STATE, not a stall. No retry.
BLOCKED = "blocked"        # retry budget spent, or an external blocker. Visible, permanent until it changes.
DONE = "done"              # the terminus landed.
UNREADABLE = "unreadable"  # the scanner could not read this item's state. NEVER graded as any of the above.

#: States that will never be auto-dispatched, each for a different reason, and the reasons must not merge.
_NO_DISPATCH = {
    HELD: "a price hold is a legitimate resting state under §6, not a stall — retrying it would spend money "
          "to defeat the guard that was saving it",
    BLOCKED: "the bounded-retry budget is spent or an external blocker is open; retrying is exactly the "
             "indefinite loop the auto-assign ruling was engineered against",
    DONE: "finished",
    ADVANCING: "evidence is moving; a dispatch would duplicate work that is already happening",
    DISPATCHED: "already dispatched and still inside the acknowledgement window",
    UNREADABLE: "this item's state could not be read, and dispatching on an unread state is how an "
                "unmeasured value becomes a purchase",
}


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the dispatch allowlist — the structural half of "may never bypass a spend gate"
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ THIS MODULE NAMES A WORKFLOW AND NOTHING ELSE. Every entry here routes through a lane's OWN launcher,
# which carries the §6 market gate; the ledger supplies no price, no bid, no ceiling and no ratio, so it is
# structurally incapable of loosening one. `gated_by` names the gate each path passes through, so a future
# workflow added without one is visibly wrong rather than quietly ungated.
DISPATCHABLE: dict[str, dict] = {
    "step1-fanout-autoscale.yml": {
        "what": "one supervision tick of the step-1 congeneric RBFE fan-out: collect, nudge, place",
        # EMPTY on purpose. The tick's defaults are the fleet's configured behaviour; every input this
        # workflow accepts (`fleet_branch`, `release_fanout`, `shakeout_unit`, `stuck_start_min`) changes
        # what the fleet DOES, and none of them is the ledger's to choose. Dispatching bare is the whole
        # claim: name the workflow, decide nothing.
        "allowed_inputs": set(),
        "gated_by": "congeneric_fanout.unit_ceiling_components (the per-unit dollar ceiling AND the absolute "
                    "buy line) inside the placer, plus relaunch_market_gate for every single-host rental",
    },
    "gpu-ternary-fep-vast.yml": {
        "what": "one $0 ternary GATE pass — it prices the board and either holds (committing the snapshot) "
                "or self-dispatches the launch",
        # ★★ ONLY `task`, AND ONLY EVER A $0 GATE VALUE (see `_LANE_ACTION`). `task` is a `type: choice`
        # whose options include both the $0 gates (`market-gate`, `triangle-gate`) and the tasks that
        # actually rent (`triangle` at ~$6.83 plan, `5aks` at ~$12). The ledger dispatches the GATE, never
        # the purchase — so the buy decision is made entirely by the lane's own §6 gate, on the board as it
        # stands at that moment, and this module's action costs $0 whatever the market is doing. That is the
        # strongest available form of "may never bypass a spend gate": it does not merely route through one,
        # it never asks for the spend at all.
        "allowed_inputs": {"task"},
        "gated_by": "ternary_vast_launch's $/ns market gate, which writes ternary-vast-market-hold.json / "
                    "valb-triangle-market-hold.json on EVERY pass so a decline is never silent",
    },
}

# ⚠ NOT DISPATCHABLE, AND DELIBERATELY SO: `lane-staleness-watch.yml`. That is the workflow this module RUNS
# INSIDE, so listing it would let a ledger entry dispatch the job that produced it — a self-sustaining loop
# that looks like healthy supervision and is really one run queueing the next for ever. It is also
# unnecessary: two independent dispatchers already reach it (see TICK_WORKFLOW). `fleet-supervision-alarm.yml`
# is likewise absent — it has its own trigger and nothing here needs to fire it.

# ⚠ ANY INPUT WHOSE NAME CONTAINS ONE OF THESE IS REFUSED, whatever the allowlist says. Defence in depth: the
# allowlist is data and could be edited carelessly, but a dispatch that carries a price is the one thing this
# module must never be able to do, so it is refused a second time on the value's own name.
_FORBIDDEN_INPUT_TOKENS = ("bid", "price", "usd", "ceiling", "ratio", "basis", "budget", "dph", "rate",
                           "max_", "spend", "cost", "per_ns")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# small helpers — every one of them tri-state, because ABSENT IS NEVER A LEGAL GOOD VALUE
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _et(ts: datetime.datetime | None) -> str | None:
    return ts.astimezone(ET).strftime("%-I:%M %p ET %b %-d, %Y") if ts else None


def _et_short(ts: datetime.datetime | None) -> str:
    return ts.astimezone(ET).strftime("%-I:%M %p ET") if ts else "ETA unknown"


def _z(ts: datetime.datetime | None) -> str | None:
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None


def _parse_z(s):
    """Reuse `lane_staleness_watch`'s parser rather than writing a second one that disagrees at the edges."""
    return lsw._parse_z(s)


def _load_json(path: str) -> tuple[dict | None, str | None]:
    """`(doc, why_not)`. A missing OR corrupt file returns a REASON — never an empty document. The defect this
    closes is on the record: a swallowed S3 error once became 'realised $0.0, breached=False'."""
    if not os.path.exists(path):
        return None, f"{os.path.basename(path)}: not present"
    try:
        with open(path) as fh:
            doc = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        return None, f"{os.path.basename(path)}: unreadable ({type(e).__name__}: {e})"
    if not isinstance(doc, dict):
        return None, f"{os.path.basename(path)}: not a JSON object"
    return doc, None


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the entry — one open item
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
class Entry:
    """One open item, and everything needed to decide whether anybody is carrying it.

    ★ `evidence_fingerprint` IS THE LOAD-BEARING FIELD and the reason this module needs no separate history
    file. It is whatever value PROVES the item moved — a committed-iteration count, a gate verdict, a
    checkbox state. `last_evidence_utc` is when that value last CHANGED, not when it was last observed. Age
    the one against the other and you get "6 hours with zero committed iterations" without believing any
    field that claims to be a timestamp.

    ⚠ AND A FAILED WRITE-BACK CANNOT MANUFACTURE AN ALARM, which is the property that makes this safe to run
    from CI. If the commit-back fails the stored fingerprint stays old: either the real fingerprint has since
    moved, in which case it differs and the clock RESETS (under-reporting staleness), or it genuinely has not
    moved, in which case the growing age is correct. Both directions fail safe, and the safe direction is the
    quiet one.
    """

    __slots__ = ("id", "scanner", "what", "owner", "state", "evidence_fingerprint", "last_evidence_utc",
                 "last_evidence_what", "next_evidence_due_utc", "blocked_by", "attempts", "auto_action",
                 "auto_action_why_none", "hosts_points_at", "cost_points_at", "price_points_at", "board_group",
                 "first_seen_utc", "unreadable", "notes", "blocked_cause")

    def __init__(self, id: str, scanner: str, what: str, *, owner: str | None = None, state: str = OPEN,
                 evidence_fingerprint=None, last_evidence_utc: datetime.datetime | None = None,
                 last_evidence_what: str | None = None, blocked_by: list[str] | None = None,
                 auto_action: dict | None = None, auto_action_why_none: str | None = None,
                 hosts_points_at: str | None = None, cost_points_at: str | None = None,
                 price_points_at: str | None = None,
                 board_group: str | None = None, unreadable: dict | None = None,
                 notes: list[str] | None = None):
        self.id, self.scanner, self.what = id, scanner, what
        self.owner, self.state = owner, state
        self.evidence_fingerprint = evidence_fingerprint
        self.last_evidence_utc, self.last_evidence_what = last_evidence_utc, last_evidence_what
        self.next_evidence_due_utc: datetime.datetime | None = None
        self.blocked_by = list(blocked_by or [])
        self.attempts: list[dict] = []
        self.auto_action = auto_action
        # ⚠ NEVER SILENTLY NULL. "No action available" and "an action exists but this state forbids it" are
        # opposite facts, and a bare `null` renders them alike — the same absent-as-a-value defect that this
        # repo keeps paying for, applied to the field that decides whether work moves.
        self.auto_action_why_none = auto_action_why_none
        # ★★ WHICH BILLED HOSTS THIS ENTRY IS PART OF — a POINTER AT THE ARTIFACT'S OWN INSTANCE LIST,
        # never a host resolved per entry. MEASURED REASON: a fan-out `unit_id` names an edge by BOTH
        # endpoints (`e_cw_ev_5oh__cw_ev_5opropargyl__…`) while the launcher labels the box after ONE of
        # them, so two different units legitimately match the same label. Resolving per unit counted EIGHT
        # billed hosts against a `live_instances` of SIX — a board that over-reports what it is paying for is
        # worse than one that says it cannot tell. The instance list needs no matching and is exact.
        self.hosts_points_at, self.cost_points_at = hosts_points_at, cost_points_at
        # ★★ WHICH GATE SNAPSHOT MAY PRICE THIS ENTRY, and it is per-entry rather than global for the reason
        # `lane_staleness_watch` states about shared artifacts: reading one lane's snapshot for another
        # ATTRIBUTES ONE LANE'S HEALTH TO A LANE NOBODY MEASURED. Caught by running the first board — the
        # step-1 fan-out's `offers_priced` was pricing the closure triangle, the 5a-KS pair AND the plan
        # items, so three lanes displayed a refusal that had been computed for a fourth. An entry with no
        # snapshot of its own prices as `—`, never off a neighbour's.
        self.price_points_at = price_points_at
        # `blocked` has two causes and they are NOT the same fact: an external gate we were never going to
        # pass (correct, expected, and not evidence of anything wrong) against a SPENT RETRY BUDGET (the
        # auto-assign risk actually materialising). Rendering them alike is how a board full of correct
        # behaviour hides the one row that matters.
        self.blocked_cause: str | None = None
        self.board_group = board_group or scanner
        self.first_seen_utc: datetime.datetime | None = None
        self.unreadable = dict(unreadable or {})
        self.notes = list(notes or [])

    # ── the bounded-retry arithmetic, all in one place ──
    def fruitless_attempts(self) -> int:
        """How many consecutive attempts produced NO NEW EVIDENCE.

        ★ AN ATTEMPT IS ONLY FRUITLESS IF THE FINGERPRINT IT WAS MADE AGAINST IS STILL THE CURRENT ONE. A
        dispatch that worked resets the count to zero by construction, so a slow-but-live item can never be
        blocked for being slow — which is the failure mode that would make this system worse than nothing,
        because it would park real work and call it broken.
        """
        n = 0
        for a in reversed(self.attempts):
            if a.get("fingerprint_at_dispatch") != _fp(self.evidence_fingerprint):
                break                       # evidence moved after this attempt: everything older worked
            n += 1
        return n

    def as_dict(self) -> dict:
        return {
            "id": self.id, "scanner": self.scanner, "what": self.what,
            "owner": self.owner,
            "owner_note": None if self.owner else "UNOWNED — nothing is carrying this item; that is the "
                                                  "condition this ledger exists to make visible",
            "state": self.state,
            "evidence_fingerprint": _fp(self.evidence_fingerprint),
            "last_evidence_utc": _z(self.last_evidence_utc), "last_evidence_et": _et(self.last_evidence_utc),
            "last_evidence_what": self.last_evidence_what,
            "next_evidence_due_utc": _z(self.next_evidence_due_utc),
            "next_evidence_due_et": _et(self.next_evidence_due_utc),
            "blocked_by": self.blocked_by,
            "attempts": self.attempts,
            "n_fruitless_attempts": self.fruitless_attempts(),
            "retry_budget": MAX_FRUITLESS_ATTEMPTS,
            "auto_action": self.auto_action,
            "auto_action_why_none": self.auto_action_why_none,
            "hosts_points_at": self.hosts_points_at, "cost_points_at": self.cost_points_at,
            "price_points_at": self.price_points_at,
            "blocked_cause": self.blocked_cause,
            "board_group": self.board_group,
            "first_seen_utc": _z(self.first_seen_utc),
            "unreadable": self.unreadable or None,
            "notes": self.notes or None,
        }


def _fp(v) -> str | None:
    """Fingerprints compare as strings, so `None` stays distinguishable from `0` and from `"0"`.

    ⚠ THIS MATTERS AND IS NOT PEDANTRY. A fan-out unit that has committed nothing yet legitimately carries
    `committed_scalar: null`, and a unit that has committed zero iterations carries `0`. Coercing either to
    the other is precisely the absent-as-a-legal-value defect: one means "not started", the other means
    "started and produced nothing", and only the second is a stall.
    """
    return None if v is None else str(v)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# SCANNERS — entries are CREATED BY THESE, never by hand
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ THIS IS THE PART THAT MAKES THE LEDGER ROBUST RATHER THAN ANOTHER THING TO REMEMBER. A hand-maintained
# ledger fails the same way the prose board failed: it records what somebody remembered to record. A scanned
# ledger records what is on disk, so the only way to hide work from it is to write the work down and then
# delete it.
#
# EVERY SCANNER IS PURE over already-loaded documents. All file I/O is in `gather()`. That is not tidiness —
# it is what lets `test_work_ledger.py` replay the day's real failures as literals and prove each one would
# have been caught, without a filesystem, a network or a credential.
#
# ⚠ A SCANNER THAT RAISES MUST NOT SILENTLY SHRINK THE BOARD. `gather` catches per-scanner and records the
# failure in `_scanners`, because a category that stopped being scanned looks exactly like a category with
# nothing in it — which is this module's own defect, turned on itself.

#: The machine copy of the coverage claim in the docstring. `test_work_ledger.py` asserts every scanner
#: registered here appears in the docstring's SCANNED list and vice versa, so the two cannot drift apart.
SCANNERS = ("plan_items", "fanout_units", "handoff", "rung_gates", "lanes", "self")

# `- **`[x]` ` — a bullet, bold, then the marker as an INLINE CODE SPAN. Verified against the plan's own
# legend line. ⚠ THE "SKIPPED" MARKER IS AN EN DASH (U+2013), NOT AN ASCII HYPHEN; matching only `-` would
# silently reclassify every skipped item as pending and fill the board with work nobody owes.
_PLAN_ITEM_RE = re.compile(r"^(\s*)-\s+\*\*`\[([ x~!–-])\]`\s*(.*)$")
_RUNG_RE = re.compile(r"^###\s+(.*)$")
_SECTION_RE = re.compile(r"^##\s+(.*)$")
_PLAN_HEADING = "THE ORDERED PLAN"

#: Markers whose work is OWED. `[x]` is done and `[–]` was deliberately skipped, so neither is open.
#: `[!]` is open in the most decision-relevant way there is: a result LANDED and its verdict does not stand.
_OPEN_MARKERS = {" ": "pending", "~": "in progress", "!": "result under correction"}

#: Phrases that mean an item is waiting on something this module cannot evaluate. ★ A PROSE GATE IS NOT
#: MACHINE-READABLE and this module does not pretend otherwise: an item naming one is recorded `blocked` WITH
#: THE GATE TEXT and is never auto-dispatched. That UNDER-dispatches, which is the safe direction for a system
#: that spends money — the cost of being wrong is a visible entry nobody actioned, against a rental nobody
#: authorised. It is also why `blocked_by` carries the gate's own words rather than a boolean: the entry has
#: to be actionable by a reader even though it was not actionable by the scanner.
_GATE_MARKERS = ("**gate:**", "**gates:**", "**go/no-go:**", "blocked by", "needs a go", "needs a budget",
                 "only if", "requires sign-off", "outward-facing")


def scan_plan_items(strategy_text: str | None, err: str | None) -> tuple[list[Entry], str]:
    """Unblocked `[ ]` / `[~]` / `[!]` items in the roadmap's ORDERED PLAN.

    ★ WHY THE ORDERED PLAN AND NOT THE OTHER BACKLOGS. Its checkboxes are a COMPLETION SIGNAL, so an entry
    raised from it can actually reach `done`. `IDEAS.md`, `method-watch.md` and the reviewer lists are prose
    with no such signal; scanning them would raise entries that can never close, and a board carrying
    permanent noise is a board people skim — which is how the prose board failed in the first place.

    ⚠ THE ITEM'S IDENTITY IS ITS TITLE, because the plan carries no IDs. That is a real weakness and it is
    stated rather than hidden: RE-TITLING AN ITEM MAKES A NEW ENTRY AND ABANDONS THE OLD ONE'S ATTEMPT
    HISTORY. It fails in the SAFE direction — a fresh entry with a fresh retry budget, never a silently
    dropped item — and the abandoned one disappears only once its marker reaches `[x]`.
    """
    if strategy_text is None:
        return [], f"NOT SCANNED — {err or 'the plan document is unreadable'}. The plan is invisible this run."
    lines = strategy_text.splitlines()
    # Bound the scan to the ORDERED PLAN section. Checklist markers appear elsewhere in a 200 kB+ document,
    # and a scanner that swept the whole file would raise entries from worked examples and appendices.
    start = next((i for i, ln in enumerate(lines)
                  if _SECTION_RE.match(ln) and _PLAN_HEADING in ln.upper()), None)
    if start is None:
        return [], (f"NOT SCANNED — no '## ... {_PLAN_HEADING} ...' heading found in the plan document. "
                    f"The plan scanner is REPORTING ITS OWN BLINDNESS rather than returning an empty list, "
                    f"which "
                    f"would be indistinguishable from a plan with nothing left to do.")
    end = next((i for i in range(start + 1, len(lines)) if _SECTION_RE.match(lines[i])), len(lines))

    out: list[Entry] = []
    rung = "(no rung heading yet)"
    rung_gated = False
    i = start + 1
    while i < end:
        ln = lines[i]
        m_rung = _RUNG_RE.match(ln)
        if m_rung:
            rung = m_rung.group(1).strip()
            # `*(only if Rung 1 = GO)*` in the heading gates every item beneath it.
            rung_gated = "only if" in rung.lower() or "gated" in rung.lower()
            i += 1
            continue
        m = _PLAN_ITEM_RE.match(ln)
        if not m:
            i += 1
            continue
        indent, marker, rest = m.group(1), m.group(2), m.group(3)
        # Gather the item's body: continuation lines up to the next item or heading. The gate lives in there.
        body = [rest]
        j = i + 1
        while j < end and not _PLAN_ITEM_RE.match(lines[j]) and not _RUNG_RE.match(lines[j]):
            body.append(lines[j])
            j += 1
        i = j
        if marker not in _OPEN_MARKERS:
            continue                              # `[x]` done, `[–]` deliberately skipped
        if indent:
            continue                              # a nested annotation, not a plan item of its own
        title = _plain(rest)[:150] or "(untitled plan item)"
        blob = "\n".join(body).lower()
        gates = [g for g in _GATE_MARKERS if g in blob]
        if rung_gated:
            gates.append(f"rung heading: {rung}")
        eid = "plan:" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:70]
        e = Entry(
            eid, "plan_items",
            f"[{rung.split('—')[0].strip()}] {title}",
            owner=None,
            state=BLOCKED if gates else OPEN,
            # ★ THE FINGERPRINT IS THE MARKER ITSELF. When the item moves `[ ]` -> `[~]` -> `[x]` the
            # fingerprint changes, which is exactly "this item produced new evidence" — and it means the
            # retry budget resets whenever the plan actually moves.
            evidence_fingerprint=marker,
            last_evidence_what=f"roadmap ORDERED PLAN marker `[{marker}]` ({_OPEN_MARKERS[marker]})",
            blocked_by=[f"gate text in the plan item: {g}" for g in gates],
            board_group="plan",
            cost_points_at=None,
            notes=[f"rung: {rung}"],
        )
        if gates:
            e.auto_action_why_none = (
                "this item names a gate in prose, and a prose gate is not machine-readable. It is recorded "
                "BLOCKED with the gate's own words so a reader can action it, and is never auto-dispatched — "
                "under-dispatching is the safe direction when the alternative is an unauthorised rental.")
        else:
            e.auto_action_why_none = (
                "no ORDERED PLAN item maps to a dispatchable workflow: the plan names science, not CI. This "
                "entry is recorded UNOWNED and stays on the board until its marker reaches `[x]` — the "
                "ledger does not invent a dispatch it cannot justify.")
        out.append(e)
    return out, (f"scanned nr4a3-program-map.md lines {start + 1}-{end} for `[ ]`/`[~]`/`[!]` items; "
                 f"`[x]` and `[–]` are not owed and are skipped")


def _plain(s: str) -> str:
    """Markdown title -> something a human reads on one line. Cosmetic only; nothing decides on it."""
    s = re.sub(r"\*\*|`|\*", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def scan_fanout_units(progress: dict | None, err: str | None) -> tuple[list[Entry], str]:
    """Step-1 fan-out units, fingerprinted on the COMMITTED-ITERATION COUNT and nothing else.

    ⚠ WHY ONLY `committed_scalar`, when the artifact offers four other tempting fields:
      * `phase` carries a TIMESTAMP that moves every tick — including on a unit that has been dead for
        hours. Including it in the fingerprint would mask exactly the failure this scans for.
      * `gpu_util` is not diagnostic: 0.0 has been observed on genuinely advancing hosts, and `0.0` sits in
        this very artifact next to the census. Never read; asserted by AST.
      * `cur_state` is not a liveness signal, and `exited` is routinely transient — three instances read
        `exited` and were running again 21 min later.
      * `instances[].age_min` measures how long we have been PAYING, which is the cost of the failure, not
        evidence of the work.
    CLAUDE.md §6 states the rule this implements in one line: **only the committed-iteration census
    condemns.** Everything else here is reported and nothing else decides.

    `committed_prev_scalar` sits beside it and is deliberately NOT the signal either: it compares two
    ADJACENT ticks, and at an 8-minute cadence a healthy unit routinely commits nothing in one tick. Reading
    it as a stall would condemn the whole fleet every few minutes. The fingerprint ages across ALL ticks
    since the value last moved, which is the question — 6 hours, not 8 minutes.
    """
    if progress is None:
        return [], f"NOT SCANNED — {err or 'step1-fanout-progress.json unreadable'}"
    gen = _parse_z(progress.get("_generated_utc"))
    units = progress.get("units")
    if not isinstance(units, list):
        return [], "NOT SCANNED — `units` absent or not a list in step1-fanout-progress.json"

    out = []
    for u in units:
        if not isinstance(u, dict):
            continue
        uid = str(u.get("unit_id"))
        phase = str(u.get("phase") or "")
        scalar = u.get("committed_scalar")
        parts = uid.split("__")
        short = parts[1] if len(parts) > 1 else uid
        done = phase.startswith("done")
        failed = "FAILED" in phase
        e = Entry(
            f"fanout-unit:{uid}", "fanout_units",
            f"Step-1 fan-out unit {short[:44]} — {str(u.get('committed') or 'no commit yet')[:34]}",
            owner="step1-fanout-autoscale.yml",
            state=DONE if done else OPEN,
            evidence_fingerprint=scalar,
            last_evidence_utc=gen,
            last_evidence_what="step1-fanout-progress.json `units[].committed_scalar` "
                               "(the committed-iteration census — the only signal that condemns)",
            board_group="step1-fanout",
            cost_points_at="step1-fanout-progress.json:realised_usd_so_far",
            price_points_at="step1-fanout-market-hold.json",
            hosts_points_at="step1-fanout-progress.json:instances",
        )
        if failed:
            # ⚠ A FAILED PHASE IS NOT AUTOMATICALLY A BLOCKER. `FAILED-rc1` has been transient (a preemption
            # mid-write) and has been permanent (an unmappable edge). The scanner refuses to decide which:
            # it records the observation and lets the bounded-retry budget adjudicate, because that is the
            # mechanism that cannot loop forever either way. §4 — never diagnose from an error's own message.
            e.notes.append(f"phase reports {phase[:60]!r}; recorded as an OBSERVATION, not a diagnosis — "
                           f"an error's own explanation was wrong three times on 2026-07-27, so the retry "
                           f"budget adjudicates this, not the string")
        if gen is None:
            e.unreadable["last_evidence_utc"] = ("`_generated_utc` absent or unparseable — this unit's "
                                                 "evidence cannot be aged, so it is not graded")
            e.state = UNREADABLE
        out.append(e)
    return out, (f"scanned {len(out)} step-1 fan-out unit(s) on `committed_scalar` alone; `phase`, "
                 f"`gpu_util`, `cur_state` and `age_min` are read for annotation or not at all")


def scan_handoff(ledger: dict | None, err: str | None, now: datetime.datetime) -> tuple[list[Entry], str]:
    """A gate that said `dispatched` and produced NO rental, dispatch or terminal record after it.

    ★ THIS IS THE SEAM, AND IT IS THE ONE PLACE THE TRIANGLE FAILURE COULD HAVE BEEN CAUGHT EARLY. A
    hand-off has two ends: a gate decides to act, and something acts. `lane_staleness_watch` watches the far
    end and needs `idle_min` (45 min) of silence before it can speak. THIS watches the JOIN, and an
    unanswered dispatch is visible within `DISPATCH_ACK_MIN` of the gate firing — because the ledger already
    records both ends and nothing was comparing them.

    ⚠ NOT COVERED HERE, and covered elsewhere rather than twice: a lane whose last record was a SUCCESSFUL
    TERMINAL stage with no successor — the literal `triangle-prime` shape. That has no unanswered dispatch
    to find, because the dispatch was answered; what is missing is the NEXT one, which only the lane's own
    unfinished-work state can establish. `lane_staleness_watch` grades it IDLE-UNEXPECTED and this module
    consumes that verdict in `scan_lanes`. One question, one implementation (§1).
    """
    if ledger is None:
        return [], f"NOT SCANNED — {err or 'ternary-vast-launch-attempts.json unreadable'}"
    attempts = ledger.get("attempts")
    if not isinstance(attempts, list):
        return [], "NOT SCANNED — `attempts` absent or not a list"

    rows = []
    for a in attempts:
        if isinstance(a, dict) and _parse_z(a.get("utc")):
            rows.append((_parse_z(a["utc"]), a))
    rows.sort(key=lambda r: r[0])

    out = []
    for idx, (t, a) in enumerate(rows):
        if str(a.get("outcome") or "").lower() != "dispatched":
            continue
        task = _task_of(a)
        # Answered by ANY later record for the same task that is not another gate evaluation. A second gate
        # pass is not an answer — it is the same question asked again, which is what a stuck lane looks like.
        answered = next((b for _tb, b in rows[idx + 1:]
                         if _task_of(b) == task and not str(b.get("stage") or "").startswith("market-gate")),
                        None)
        if answered is not None:
            continue
        age = (now - t).total_seconds() / 60.0
        if age < DISPATCH_ACK_MIN:
            continue                     # still inside the window the measured hand-offs fit in
        out.append(Entry(
            f"handoff:{task}:{_z(t)}", "handoff",
            f"Hand-off never answered: the gate dispatched {task} at {_et_short(t)} and no rental, launch "
            f"or terminal record followed",
            owner=None,
            state=OPEN,
            # The fingerprint is the dispatch itself: it changes only when a NEW dispatch supersedes this
            # one, which is precisely the evidence that the hand-off finally took.
            evidence_fingerprint=_z(t),
            last_evidence_utc=t,
            last_evidence_what=f"ternary-vast-launch-attempts.json: stage={a.get('stage')!r} "
                               f"outcome='dispatched' reason={str(a.get('reason'))[:80]!r}",
            board_group="ternary",
            cost_points_at=None,
            notes=[f"unanswered for {age:.0f} min against a {DISPATCH_ACK_MIN:.0f} min acknowledgement "
                   f"window measured from today's real gate->rental hand-offs (0.7-22 min)"],
        ))
    return out, (f"paired every `dispatched` gate record in the launch ledger with what followed it; "
                 f"{len(out)} unanswered past {DISPATCH_ACK_MIN:.0f} min")


def _task_of(a: dict) -> str:
    """Which lane a launch-ledger row belongs to. `gpu-ternary-fep-vast.yml` serves the replicates, the
    triangle and 5a-KS, so a triangle record must never answer for the replicate lane's silence — the same
    attribution rule `lane_staleness_watch` applies to the shared gate snapshot."""
    blob = " ".join(str(a.get(k) or "") for k in ("reason", "stage", "outcome"))
    m = re.search(r"task=([a-z0-9_\-]+)", blob, re.I)
    return m.group(1).lower() if m else "(untagged)"


#: Milestone statuses that SATISFY a dependency. `skipped` counts: a deliberately-skipped step with a stated
#: saving is a decision that was MADE, and treating it as unmet would block everything behind it forever.
_DEP_SATISFIED = ("done", "skipped")
#: Statuses that mean the gate has returned nothing yet. `under_correction` is included on purpose and is the
#: most decision-relevant of the three: a verdict LANDED and then stopped standing, which is a rung with no
#: live verdict wearing the appearance of a finished one.
_NO_VERDICT = ("pending", "under_correction")


def scan_rung_gates(schedule: dict | None, err: str | None) -> tuple[list[Entry], str]:
    """Rungs whose gate has NEVER RETURNED A VERDICT, computed from the schedule's real dependency graph.

    ★★ WHY THE SCHEDULE JSON AND NOT THE LADDER, and this is a correction the first run forced. The obvious
    implementation cross-checks `vast-ladder-repricing.json`'s priced rungs against the roadmap's ORDERED
    PLAN titles — "a rung nobody claims". It was built that way, run against the real files, and RAISED THREE
    FALSE POSITIVES: the ladder is keyed in prose (`"step1_fanout (19 RBFE edges @ ~13.7 GPU-h)"`,
    `"5c ensemble refinement"`, `"local within-basin FEP"`) while the plan is keyed in prose of a DIFFERENT
    shape (`"Step 1 fan-out — cmpd19 congeneric map"`, `"5c · Explicit ternary-ensemble refinement"`), and no
    token rule bridges them without either missing real gaps or inventing them. It flagged `step1_fanout` —
    the lane that was billing six hosts at that moment — as work nobody claimed.

    **A guard that condemns correct behaviour gets switched off within a day**, so that implementation is
    gone rather than tuned. `degrader-paper-schedule.json` is the MACHINE MIRROR of the ORDERED PLAN
    (the roadmap's ORDERED PLAN names it as such) and it carries `id`, `status` and `depends_on` — a real dependency
    graph, with exact keys. The question becomes mechanical and needs no name matching at all:

        every dependency satisfied, and this milestone's own status still has no verdict
        -> UNBLOCKED AND NOBODY IS CARRYING IT.

    ⚠ WHAT IS THEREFORE NOT CHECKED, stated rather than quietly dropped: the NAME CORRESPONDENCE between the
    ladder's priced rungs and the schedule's milestone ids. Three ladder rungs have no id-shaped counterpart
    (`5a-KS primary`, `5c ensemble refinement`, `local within-basin FEP`), and on the real files a fuzzy
    match between the two produced only false positives. That gap is real and is listed in the module
    docstring's NOT SCANNED section, where a coverage hole belongs.
    """
    if schedule is None:
        return [], f"NOT SCANNED — {err or 'degrader-paper-schedule.json unreadable'}"
    ms = schedule.get("milestones")
    if not isinstance(ms, list):
        return [], "NOT SCANNED — `milestones` absent or not a list in degrader-paper-schedule.json"
    status = {m["id"]: str(m.get("status")) for m in ms if isinstance(m, dict) and m.get("id")}

    out = []
    for m in ms:
        if not isinstance(m, dict) or not m.get("id"):
            continue
        mid, st = str(m["id"]), str(m.get("status"))
        if st not in _NO_VERDICT:
            continue
        deps = [d for d in (m.get("depends_on") or []) if isinstance(d, str)]
        # ⚠ AN UNKNOWN DEPENDENCY IS NOT A SATISFIED ONE. A typo'd or deleted id would otherwise read as
        # "nothing blocking", which unblocks a milestone on the strength of a missing record — the
        # absent-as-a-legal-value defect, pointed at the dependency graph.
        unmet = [f"{d} is {status.get(d, 'NOT A MILESTONE IN THIS FILE')}"
                 for d in deps if status.get(d) not in _DEP_SATISFIED]
        e = Entry(
            f"rung:{mid}", "rung_gates",
            f"Rung/milestone {mid!r} — status {st!r}, gate has returned no verdict"
            + (" (a verdict LANDED and no longer stands)" if st == "under_correction" else ""),
            owner=None,
            state=BLOCKED if unmet else OPEN,
            # The fingerprint is the status plus the dependency states: it moves the moment the gate returns
            # anything OR a blocker clears, which is exactly when this entry stops being owed.
            evidence_fingerprint=st + "|" + ",".join(f"{d}={status.get(d)}" for d in sorted(deps)),
            last_evidence_what=f"degrader-paper-schedule.json milestone {mid!r} status={st!r}",
            blocked_by=unmet,
            board_group="plan",
            # Per §1 the dollars are POINTED AT, never copied.
            cost_points_at=None,
            notes=[f"title: {str(m.get('title'))[:120]}",
                   f"cost estimate on the milestone: {str(m.get('cost_est_usd'))[:60]} "
                   f"(the ladder owns the authoritative figure — vast-ladder-repricing.json)"],
            auto_action_why_none=(
                "a rung's gate is adjudicated by running the science and writing the verdict, not by a "
                "workflow this module may dispatch. Recorded UNOWNED and left visible — which is the whole "
                "point: an unblocked rung nobody is carrying is invisible everywhere else."),
        )
        out.append(e)
    return out, (f"walked {len(ms)} schedule milestone(s) on their real `depends_on` graph; "
                 f"{sum(1 for e in out if e.state == OPEN)} unblocked with no verdict, "
                 f"{sum(1 for e in out if e.state == BLOCKED)} genuinely waiting on a named dependency")


#: `lane_staleness_watch` verdict -> (our state, is this a resting state we must not retry).
#: ★ THE SECOND ELEMENT IS THE WHOLE POINT. A price hold and a stall are both "nothing is happening", and
#: §6 makes the first a SUCCESS — *"I'd rather pause until availability opens than pay double per ns."*
#: Mapping them to the same state would make this module spend money to defeat the guard that was saving it.
_LANE_VERDICT = {
    "ADVANCING":             (ADVANCING, False),
    "FINISHED":              (DONE, True),
    "TICKING":               (ADVANCING, False),
    "PARKED-PRICE-HOLD":     (HELD, True),
    "PARKED-GATE":           (HELD, True),
    "PARKED-BY-OPERATOR":    (HELD, True),
    "IDLE-WITHIN-GRACE":     (DISPATCHED, True),
    "BILLING-NOT-ADVANCING": (OPEN, False),
    "IDLE-UNEXPECTED":       (OPEN, False),
    "HOLD-NOT-PRICE":        (OPEN, False),
    "TICK-NOT-MEASURING":    (OPEN, False),
    "UNKNOWN":               (UNREADABLE, True),
}

#: Which workflow advances a lane. The ledger names a workflow and nothing else — the workflow carries the
#: gate. See `DISPATCHABLE` for the structural half of that guarantee.
# ⚠ CAN A LEDGER DISPATCH CANCEL LIVE WORK, OR DOUBLE-RENT? CHECKED, NOT ASSUMED (2026-07-27):
#   * `step1-fanout-autoscale.yml` sets `concurrency: {group: step1-fanout-autoscale,
#     cancel-in-progress: false}` — an extra dispatch QUEUES behind a running tick and can never cancel one.
#   * `gpu-ternary-fep-vast.yml` already fires on its own `cron: "17 * * * *"`, and its `resolve` step
#     defaults a scheduled run to `TASK=market-gate`. So the gate pass this module asks for is the SAME
#     action that lane already takes hourly on its own — inside the existing envelope, not a new class of
#     traffic. The launcher recomputes `units_needing_host` from the object store on every pass, so a
#     concurrent gate cannot place a unit that is already hosted.
#   * And the volume is bounded twice over regardless: DEDUPLICATED to one dispatch per (workflow, inputs)
#     per run, and capped per item by the retry budget.
_LANE_ACTION = {
    # The fan-out tick. Its placer holds the per-unit dollar ceiling and the buy line.
    "step1-fanout":      ("step1-fanout-autoscale.yml", {}),
    # ★ THE $0 GATES, NEVER THE PURCHASES. `market-gate` and `triangle-gate` are documented in the workflow
    # as "$0, price the legs and self-dispatch the launch the moment the board clears" — they either HOLD,
    # committing the market snapshot that §6 requires so a decline is never silent, or they dispatch the
    # buy themselves. Dispatching `triangle` (~$6.83 plan) or `5aks` (~$12) directly would put the ledger in
    # the position of asking for the spend, which is exactly what it must never do.
    "ternary-valb-reps": ("gpu-ternary-fep-vast.yml", {"task": "market-gate"}),
    "closure-triangle":  ("gpu-ternary-fep-vast.yml", {"task": "triangle-gate"}),
    # ⚠ `rung-5aks` IS ABSENT ON PURPOSE. Both its legs are PARKED with `_parked_why` and an explicit
    # `_re_enable_when` price condition, so they are `held` here and would never be dispatched anyway — but
    # leaving the lane out of this map means that stays true even if something re-enables the watch entries.
    # Re-arming a parked leg is a decision with a stated price condition attached; it is the lane's, not the
    # ledger's.
}


def scan_lanes(lane_report: dict | None, err: str | None) -> tuple[list[Entry], str]:
    """Every lane `lane_staleness_watch` grades — CONSUMED, never re-implemented.

    ⚠ ITS OK VERDICTS BECOME ENTRIES TOO, and that is not padding. The board is generated from the ledger, so
    a healthy lane with no entry would have no row — and a lane that silently left the board is the exact
    failure this replaces. `advancing` and `held` rows are how the board proves it is watching something.
    """
    if lane_report is None:
        return [], f"NOT SCANNED — {err or 'lane_staleness_watch could not be run'}"
    lanes = lane_report.get("lanes")
    if not isinstance(lanes, list):
        return [], "NOT SCANNED — lane_staleness_watch returned no `lanes` list"
    out = []
    for v in lanes:
        if not isinstance(v, dict):
            continue
        key, verdict = str(v.get("lane")), str(v.get("verdict"))
        st, resting = _LANE_VERDICT.get(verdict, (UNREADABLE, True))
        state = v.get("state") or {}
        wf, inputs = _LANE_ACTION.get(key, (None, None))
        # `tick_workflow` is what actually carries the lane. `_LANE_ACTION` is the narrower question of what
        # THIS module may dispatch, and a lane it may not dispatch is still owned by something.
        owner = wf or state.get("tick_workflow")
        e = Entry(
            f"lane:{key}", "lanes",
            f"{v.get('label') or key} — {verdict}",
            owner=owner,
            state=st,
            # ★ THE VERDICT IS THE FINGERPRINT. A lane that changes verdict has produced new evidence; a lane
            # stuck on BILLING-NOT-ADVANCING has not, and its retry budget therefore drains — which is what
            # bounds an automatic response to a lane that cannot be fixed by dispatching at it.
            evidence_fingerprint=f"{verdict}|{state.get('census') or ''}|{state.get('last_evidence_what')}",
            last_evidence_utc=_parse_z(state.get("last_evidence_utc")),
            last_evidence_what=state.get("last_evidence_what"),
            board_group=key,
            cost_points_at=("step1-fanout-progress.json:realised_usd_so_far" if key == "step1-fanout"
                            else "ternary-vast-market-hold.json:plan_usd" if key == "ternary-valb-reps"
                            else None),
            # ★ ITS OWN SNAPSHOT, NEVER A SIBLING'S. `ternary-vast-market-hold.json` is stamped with the
            # MODE it describes, so it prices the replicate lane and nothing else; the triangle writes its
            # own `valb-triangle-market-hold.json` (the `triangle-gate` task's `--gate` output). A lane with
            # no snapshot of its own prices as `—` and borrows nothing — reading a neighbour's would
            # attribute one lane's health to a lane nobody measured.
            price_points_at=("step1-fanout-market-hold.json" if key == "step1-fanout"
                             else "ternary-vast-market-hold.json" if key == "ternary-valb-reps"
                             else "valb-triangle-market-hold.json" if key == "closure-triangle"
                             else None),
            hosts_points_at=("step1-fanout-progress.json:instances" if key == "step1-fanout" else None),
            notes=[str(v.get("detail"))[:400]],
        )
        if verdict == "UNKNOWN":
            e.unreadable["lane_state"] = str(v.get("detail"))[:300]
        if resting:
            e.auto_action_why_none = _NO_DISPATCH.get(st, "resting state")
            if st == HELD:
                # Record the SNAPSHOT that proves the market was consulted. §6 forbids a silent decline, and
                # a hold with no snapshot is graded UNKNOWN upstream — so if we got HELD here, it has one.
                e.notes.append(f"resting on a gate, not stalled: {state.get('hold_reason') or ''}"[:300])
                e.notes.append(f"market snapshot: {state.get('hold_snapshot') or '(none recorded)'}")
        elif wf is None:
            e.auto_action_why_none = (
                f"lane {key!r} is carried by {owner or 'nothing this module can see'} but has no entry in "
                f"`_LANE_ACTION`, so this module does not know which dispatch advances it. Recorded with its "
                f"owner rather than dispatched at a guess — the GCP lane is quota-bound and us-central1-only, "
                f"and a blind dispatch at it would waste the single GPU the whole project shares.")
        else:
            e.auto_action = _action(wf, inputs, why=f"advance lane {key} out of {verdict}")
        out.append(e)
    return out, (f"consumed {len(out)} lane verdict(s) from lane_staleness_watch (its thresholds are "
                 f"imported, never re-typed); OK verdicts become rows so the board can prove it is watching")


def _action(workflow: str, inputs: dict | None, *, why: str) -> dict:
    """Build a dispatch, REFUSING anything the allowlist does not sanction.

    ★★ THE STRUCTURAL HALF OF "MAY NEVER BYPASS A SPEND GATE". Two independent refusals, because the
    allowlist is data and data gets edited carelessly:
      1. the workflow must be in `DISPATCHABLE`, and only its declared inputs may be passed;
      2. NO input name may contain a price-vocabulary token, whatever the allowlist says.
    A dispatch that carries a bid, a ceiling or a ratio is the one thing this module must be incapable of,
    so it is refused twice and raises rather than degrading — a silently-dropped input would leave a
    dispatch that looks sanctioned and is not.
    """
    spec = DISPATCHABLE.get(workflow)
    if spec is None:
        raise ValueError(f"{workflow!r} is not in DISPATCHABLE — the ledger may only dispatch workflows "
                         f"whose own path carries the §6 market gate")
    inputs = dict(inputs or {})
    for k in inputs:
        low = k.lower()
        if any(tok in low for tok in _FORBIDDEN_INPUT_TOKENS):
            raise ValueError(f"input {k!r} is in the price vocabulary: the ledger names a workflow and "
                             f"never a price. Raising a bid or moving a ceiling is not its to do.")
        if k not in spec["allowed_inputs"]:
            raise ValueError(f"input {k!r} is not declared for {workflow!r} in DISPATCHABLE")
    return {"kind": "workflow_dispatch", "workflow": workflow, "ref": "main", "inputs": inputs,
            "why": why, "gated_by": spec["gated_by"], "what": spec["what"]}


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# gathering — ALL file I/O lives here, so every scanner above stays pure and replayable
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def gather(root: str, strategy_path: str, schedule_path: str, now: datetime.datetime, *,
           use_api: bool = False,
           source_roots: dict[str, str] | None = None) -> tuple[list[Entry], list[dict]]:
    """Run every scanner. Returns `(entries, scanner_coverage)`.

    ⚠ A SCANNER THAT RAISES IS RECORDED, NOT SWALLOWED. A category that stopped being scanned looks exactly
    like a category with nothing in it — this module's own defect, turned on itself. So each scanner is
    caught individually and its failure lands in `_scanners` with the traceback's type and message, where the
    board renders it as a coverage gap rather than as silence.
    """
    cov: list[dict] = []
    entries: list[Entry] = []

    def run(name: str, fn):
        try:
            got, how = fn()
        except Exception as e:                      # noqa: BLE001 — a scanner fault must never hide a lane
            cov.append({"scanner": name, "ran": False, "found": 0, "error": f"{type(e).__name__}: {e}",
                        "how": "SCANNER FAILED — this whole category is UNSCANNED this run, which is not the "
                               "same as empty and must not be read as one"})
            return
        cov.append({"scanner": name, "ran": True, "found": len(got), "error": None, "how": how})
        entries.extend(got)

    try:
        with open(strategy_path, encoding="utf-8") as fh:
            strategy_text, strategy_err = fh.read(), None
    except OSError as e:
        strategy_text, strategy_err = None, f"{type(e).__name__}: {e}"

    run("plan_items", lambda: scan_plan_items(strategy_text, strategy_err))

    progress, perr = _load_json(os.path.join(root, "step1-fanout-progress.json"))
    run("fanout_units", lambda: scan_fanout_units(progress, perr))

    tledger, terr = _load_json(os.path.join(root, "ternary-vast-launch-attempts.json"))
    run("handoff", lambda: scan_handoff(tledger, terr, now))

    sched, serr = _load_json(schedule_path)
    run("rung_gates", lambda: scan_rung_gates(sched, serr))

    def _lanes():
        # ★ CONSUMED, NOT RE-IMPLEMENTED. `use_api=False` by default keeps this offline and deterministic;
        # the Actions-API half of that module is its own supervision check and has its own workflow.
        # ★ source_roots, NOT a bare root. The lanes do not all live on one branch (see
        # `lane_staleness_watch.gather`'s header). Handing the watcher one root here would make the
        # ledger inherit that blindness — and unlike the watcher, the ledger DISPATCHES, so a lane it
        # cannot see reads as unowned work and gets a gate task fired at it on every tick.
        rep, _states = lsw.build_report(root, now, use_api=use_api, source_roots=source_roots)
        return scan_lanes(rep, None)

    run("lanes", _lanes)
    return entries, cov


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# RECONCILIATION — where the bounded-retry rule lives, and the only place `blocked` is ever set from it
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _due_window_min(e: Entry) -> float | None:
    """When new evidence is owed. ⚠ EVERY VALUE HERE IS IMPORTED OR MEASURED — none is invented (§1).

    `plan_items` and `rung_gates` get NO window on purpose: they do not produce continuous evidence, so
    aging them would manufacture an overdue state out of a plan item that is simply not this week's work.
    They are `open`/`blocked` and VISIBLE, which is the correct treatment for something nobody is carrying.
    """
    if e.scanner == "fanout_units":
        return lsw.DEFAULT_ACTIVE_EVIDENCE_MIN     # imported: a lane with hosts up, silent
    if e.scanner == "handoff":
        return DISPATCH_ACK_MIN                    # measured from today's real gate->rental hand-offs
    if e.scanner == "lanes":
        return lsw.DEFAULT_IDLE_MIN                # imported: the closure-triangle window
    return None


def reconcile(prev_doc: dict | None, found: list[Entry], now: datetime.datetime) -> list[Entry]:
    """Merge this scan into the previous ledger, and apply the bounded-retry rule.

    ★★ THE RETRY RULE, STATED ONCE AND IMPLEMENTED ONCE:

        an attempt is FRUITLESS if the evidence fingerprint has not moved since it was made.
        MAX_FRUITLESS_ATTEMPTS consecutive fruitless attempts -> the item becomes `blocked`, carries the
        evidence of each failure, and IS NEVER RETRIED AGAIN until its fingerprint moves or a blocker clears.

    Three properties that make this safe to run unattended, each of which is a test:
      1. A DISPATCH THAT WORKED COSTS NOTHING. `Entry.fruitless_attempts` counts backwards and stops at the
         first attempt whose fingerprint differs from the current one, so any real progress resets the budget
         to zero. A slow-but-live item can never be blocked for being slow.
      2. `blocked` IS PERMANENT UNTIL SOMETHING CHANGES, AND "SOMETHING CHANGES" IS MECHANICAL — the
         fingerprint moves. Then the attempt history is fruitless no longer, the count falls to zero, and the
         item returns to `open` on its own. No human has to clear it, and nothing clears it by forgetting.
      3. A HELD ITEM CAN NEVER REACH `blocked`. Held entries are never dispatched, so they accrue no
         attempts, so the budget never drains. A §6 price hold that lasted a week would still be `held` on
         the seventh day — which is correct, because a hold is a success.

    ⚠ AND A FAILED WRITE-BACK CANNOT MANUFACTURE ONE EITHER. If the ledger could not be committed last run,
    `prev_doc` is old: the attempts it records are older than they should be, so the fingerprint has had MORE
    chance to move, so attempts read as SUCCESSFUL and the budget resets. The failure mode of a lost write is
    an item that is retried more, never one that is blocked without cause.
    """
    prev = {}
    for row in ((prev_doc or {}).get("entries") or []):
        if isinstance(row, dict) and row.get("id"):
            prev[row["id"]] = row

    out = []
    for e in found:
        old = prev.get(e.id)
        e.first_seen_utc = _parse_z((old or {}).get("first_seen_utc")) or now
        if old is not None:
            e.attempts = [a for a in (old.get("attempts") or []) if isinstance(a, dict)]
            if _fp(e.evidence_fingerprint) == old.get("evidence_fingerprint"):
                # ★ UNCHANGED: keep the ORIGINAL stamp. `last_evidence_utc` is when the value last CHANGED,
                # not when it was last observed — that distinction is what turns "we looked again and it is
                # still 380" into "this unit has committed nothing for six hours".
                kept = _parse_z(old.get("last_evidence_utc"))
                if kept is not None:
                    e.last_evidence_utc = kept
            else:
                # Moved. Prefer the artifact's own stamp when it has one; `now` is the honest fallback,
                # because all we can say is "it had changed by the time we looked".
                e.last_evidence_utc = e.last_evidence_utc or now
                if e.last_evidence_utc < (_parse_z(old.get("last_evidence_utc")) or e.last_evidence_utc):
                    e.last_evidence_utc = now
        else:
            e.last_evidence_utc = e.last_evidence_utc or now

        win = _due_window_min(e)
        if win is not None and e.last_evidence_utc is not None:
            e.next_evidence_due_utc = e.last_evidence_utc + datetime.timedelta(minutes=win)

        _apply_retry_budget(e, now)
        out.append(e)
    return out


def _apply_retry_budget(e: Entry, now: datetime.datetime) -> None:
    """Decide this entry's final state and whether it may be dispatched. The ONLY writer of `blocked`."""
    # 1. An external blocker outranks everything: it is not ours to retry past.
    if e.blocked_by and e.state not in (DONE, HELD):
        e.state, e.blocked_cause = BLOCKED, "external-gate"
        e.auto_action, e.auto_action_why_none = None, (
            e.auto_action_why_none or f"blocked by: {'; '.join(e.blocked_by)[:200]}")
        return
    # 2. Resting and terminal states are never retried, each for its own stated reason.
    if e.state in (HELD, DONE, UNREADABLE):
        e.auto_action = None
        e.auto_action_why_none = e.auto_action_why_none or _NO_DISPATCH[e.state]
        return
    # 3. The budget.
    n = e.fruitless_attempts()
    if n >= MAX_FRUITLESS_ATTEMPTS:
        e.state, e.blocked_cause = BLOCKED, "retry-budget-spent"
        e.blocked_by = e.blocked_by or [
            f"{n} automatic attempt(s) produced no new evidence (budget {MAX_FRUITLESS_ATTEMPTS}); the "
            f"evidence fingerprint has been {_fp(e.evidence_fingerprint)!r} since "
            f"{_et(e.last_evidence_utc)}"]
        e.auto_action = None
        e.auto_action_why_none = (
            f"RETRY BUDGET SPENT. Each of the last {n} attempts is recorded in `attempts` with the "
            f"fingerprint it was made against, so what was tried and what it produced is on the record. "
            f"This item is NOT retried again and is NOT dropped: it stays on the board as `blocked` until "
            f"its fingerprint moves, at which point the attempts stop counting as fruitless and it returns "
            f"to `open` by itself. {_NO_DISPATCH[BLOCKED]}")
        return
    # 4. Not yet due -> nothing owed, so nothing to dispatch. This is the branch that keeps the board quiet
    #    on healthy work: an advancing unit is simply inside its window.
    if e.next_evidence_due_utc is not None and now < e.next_evidence_due_utc:
        e.state = ADVANCING if e.state == OPEN else e.state
        e.auto_action = None
        e.auto_action_why_none = (f"evidence is not due until {_et(e.next_evidence_due_utc)}; nothing is "
                                  f"overdue, so there is nothing to dispatch")
        return
    if e.next_evidence_due_utc is None and e.scanner in ("fanout_units", "handoff", "lanes"):
        e.auto_action = None
        e.auto_action_why_none = ("this item has no readable evidence timestamp, so 'overdue' cannot be "
                                  "established — and dispatching on an unread state is how an unmeasured "
                                  "value becomes a purchase")
        return
    # 5. Overdue, budget remaining, and an action exists -> this is the one path that dispatches.
    if e.auto_action is None and e.scanner == "fanout_units":
        e.auto_action = _action("step1-fanout-autoscale.yml", {},
                                why=f"no committed iteration since {_et(e.last_evidence_utc)}")
    if e.auto_action is None and e.auto_action_why_none is None:
        e.auto_action_why_none = ("overdue, but no dispatchable workflow is declared for this scanner. "
                                  "Recorded UNOWNED rather than dispatched at a guess.")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the dispatch plan — what the WORKFLOW will execute. This module never shells out.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def dispatch_plan(entries: list[Entry], now: datetime.datetime) -> list[dict]:
    """Distinct dispatches, deduplicated by (workflow, inputs).

    ★ DEDUPLICATION IS NOT AN OPTIMISATION, IT IS THE DIFFERENCE BETWEEN A TICK AND A STORM. Nineteen stalled
    fan-out units all want the same `step1-fanout-autoscale.yml` tick; firing it nineteen times would queue
    nineteen runs against a `concurrency` group that serialises them, and the ledger would have manufactured
    an hour of backlog for itself. One dispatch, with `serves` naming every entry it answers for — and each
    of those entries records the attempt, so the retry budget still drains per-item.

    ⚠ THE ATTEMPT IS RECORDED AGAINST THE FINGERPRINT IT WAS MADE AGAINST. That is what makes the budget
    honest later: without it, "did this dispatch help?" would have to be inferred from a timestamp.
    """
    plan: dict[str, dict] = {}
    for e in entries:
        if not e.auto_action:
            continue
        a = e.auto_action
        key = a["workflow"] + "|" + json.dumps(a.get("inputs") or {}, sort_keys=True)
        row = plan.setdefault(key, {**a, "serves": [], "why_each": []})
        row["serves"].append(e.id)
        row["why_each"].append(f"{e.id}: {a.get('why')}")
        e.attempts.append({
            "utc": _z(now), "et": _et(now),
            "action": f"workflow_dispatch {a['workflow']} {json.dumps(a.get('inputs') or {})}",
            "fingerprint_at_dispatch": _fp(e.evidence_fingerprint),
            "why": a.get("why"),
            "gated_by": a.get("gated_by"),
            "result": "dispatch requested — the outcome is whether the fingerprint moves, not what the "
                      "dispatch returned. An error's own explanation has been wrong before; the census is "
                      "the only thing that adjudicates this.",
        })
    rows = list(plan.values())
    if len(rows) > MAX_DISPATCHES_PER_RUN:
        # Truncating is the SAFE direction and it is loud: the dropped rows keep their entries, keep their
        # recorded attempt, and come back next tick. Silently firing all of them is the one option that
        # cannot be undone.
        for extra in rows[MAX_DISPATCHES_PER_RUN:]:
            extra["capped"] = (f"NOT DISPATCHED this run: the plan exceeded MAX_DISPATCHES_PER_RUN="
                               f"{MAX_DISPATCHES_PER_RUN}. Its entries stay on the board and it is "
                               f"reconsidered next tick.")
        rows = rows[:MAX_DISPATCHES_PER_RUN] + [r for r in rows[MAX_DISPATCHES_PER_RUN:]]
    return rows


def executable(plan: list[dict]) -> list[dict]:
    """The rows the workflow may actually fire — everything the cap did not hold back."""
    return [r for r in plan if not r.get("capped")]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# SELF-SUPERVISION — see the docstring's "IF THIS STOPS RUNNING"
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def self_check(doc: dict | None, now: datetime.datetime, runs: list[dict] | None = None,
               fetch_error: str | None = None) -> dict:
    """Is the ledger itself still being run? Callable by ANY module on the committed artifact.

    Two independent answers, deliberately, because they fail differently:

      1. `_stale_after_utc` — a deadline the artifact WRITES INTO ITSELF. Needs no process, no API and no
         clock but the reader's. This is the answer that works when everything else has stopped, which is
         exactly the case that matters: a supervisor that has stopped cannot report that it stopped.
      2. `fleet_supervision_alarm.classify` — the SAME throttle-immune generation test the fleet uses: did
         the last COMPLETED run of the tick workflow advance this artifact's `_generated_utc` past its own
         start? Reused rather than re-derived (§1), and it is the stronger test because it cannot be fooled
         by a run that went green without measuring anything.

    ⚠ ARTIFACT AGE ALONE IS NOT USED AND COULD NOT WORK. An honest age threshold sits above ~240 min
    (measured GitHub delivery, 141-238 min gaps), while a real incident was 115 min stale and would have read
    FRESH throughout. `_stale_after_utc` is not an age threshold in that sense — it is a deadline against the
    cadence the SUPERVISOR CHAIN promises (a dispatched in-job loop, not a `schedule:`), which is why it can
    be tight where an age threshold cannot.
    """
    out: dict = {"now_et": _et(now)}
    if doc is None:
        out.update({"verdict": "NO-LEDGER", "ok": False,
                    "detail": "work-ledger.json is absent. Either it has never run, or it was deleted. "
                              "Absent is not 'nothing to do' — nothing can be said about any open item."})
        return out
    gen, stale_after = _parse_z(doc.get("_generated_utc")), _parse_z(doc.get("_stale_after_utc"))
    out["generated_et"], out["stale_after_et"] = _et(gen), _et(stale_after)
    if gen is None:
        out.update({"verdict": "UNREADABLE", "ok": False,
                    "detail": "`_generated_utc` is absent or unparseable, so the ledger cannot say when it "
                              "last ran. Not graded fresh — an unmeasured state rendered as a measured "
                              "value is this repo's most expensive defect class."})
        return out
    out["age_min"] = round((now - gen).total_seconds() / 60.0, 1)
    if stale_after is not None and now > stale_after:
        out.update({
            "verdict": "SUPERVISOR-CHAIN-BROKEN", "ok": False,
            "detail": (f"this ledger declared itself stale after {_et(stale_after)} and it is now "
                       f"{_et(now)} — {out['age_min']:.0f} min since it last ran, against an expected "
                       f"{EXPECTED_TICK_MIN:.0f} min cadence. THE SUPERVISOR CHAIN HAS STOPPED, and while it "
                       f"is stopped every open item below is unwatched in exactly the way this file exists "
                       f"to prevent. Restart it: `gh workflow run step1-fanout-supervisor.yml --ref main`.")})
    else:
        out.update({"verdict": "RUNNING", "ok": True,
                    "detail": (f"last run {out['age_min']:.0f} min ago; this artifact declares itself stale "
                               f"after {_et(stale_after)}, so a reader who opens the file can tell it is "
                               f"dead without running anything.")})
    # The stronger test, when the caller supplied run history.
    if runs is not None or fetch_error is not None:
        try:
            fsa.TICK_WORKFLOW = TICK_WORKFLOW
            g = fsa.classify({"_generated_utc": _z(gen)}, runs, now,
                             fsa.DEFAULT_STALE_MIN, fsa.DEFAULT_ABSENT_MIN, fetch_error=fetch_error)
            out["generation_test"] = {
                "verdict": g.get("verdict"), "ok": g.get("ok"), "detail": g.get("detail"),
                "workflow": TICK_WORKFLOW,
                "test": "did the last COMPLETED run advance this artifact's `_generated_utc` past its own "
                        "start — the throttle-immune question, imported from fleet_supervision_alarm rather "
                        "than answered a second time here",
            }
            if g.get("ok") is False and out["ok"]:
                out["ok"] = False
                out["verdict"] = "TICK-NOT-MEASURING"
                out["detail"] = (f"the ledger looks fresh, but the tick that writes it is not measuring: "
                                 f"[{g.get('verdict')}] {g.get('detail')}")
        except Exception as e:                      # noqa: BLE001
            out["generation_test"] = {"applicable": False, "why": f"{type(e).__name__}: {e}"}
    return out


#: ★ A HARD CEILING ON DISPATCHES PER RUN, on top of the deduplication. Deduplication bounds the plan by
#: the number of distinct (workflow, inputs) pairs, which is already small — but that bound depends on the
#: scanners behaving, and this one does not. It is the difference between "a scanner bug produced a wrong
#: entry" and "a scanner bug produced a queue nobody asked for". Set to the size of the allowlist: there is
#: no legitimate run in which every dispatchable workflow needs firing more than once.
MAX_DISPATCHES_PER_RUN = len(DISPATCHABLE)

#: The workflow whose completed runs must advance this artifact. It is the CROSS-LANE WATCH rather than the
#: fan-out tick, because that is the job this module runs inside — and it is reached by TWO INDEPENDENT
#: chains (the supervisor's in-job loop every `watch_every_ticks` ticks, and `step1-fanout-autoscale.yml`'s
#: `if: always()` tail, which fires even when the tick itself fails) plus an hourly cold-start cron that
#: CLAUDE.md §6 says must never be relied on and which is here only as a floor.
TICK_WORKFLOW = "lane-staleness-watch.yml"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE IN FLIGHT BOARD — GENERATED FROM THE LEDGER, in the CLAUDE.md §1 format
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ THIS IS THE LOAD-BEARING PIECE, and the reason is failure 5: a row on the prose board claimed an owner
# THAT HAD NEVER BEEN DISPATCHED. Prose written from memory can assert anything. Here the rows are a function
# of `entries`, so **IF THERE IS NO LEDGER ENTRY, NO ROW CAN BE RENDERED** — a fabricated owner is not
# discouraged, it is unwritable. And an entry only exists because a scanner found it on disk.
#
# ⚠ COSTS AND `$/ns` ARE DERIVED FROM THE EXISTING SOURCES AND NEVER TYPED (§1). The dollars come from the
# artifact the entry POINTS AT (`cost_points_at`), the `$/ns` cell from `inflight_usd_per_ns.row()` — which
# itself only formats what `vast_cost_model` computes. Nothing in this file states a price, a basis or a
# multiple, and `lint_derived_thresholds.py` would fail the build if it did.
#
# ⚠ AND NEVER OFF A LAUNCHER'S `dph≈` LINE. That figure is the market floor plus the disk line the SEARCH
# priced, so it reads LOW against the rate the instance is actually billed (measured: $0.17922 quoted against
# $0.20272 billed). Paying rows are priced from the INSTANCE record; a row priced from an offer says so, and
# `inflight_usd_per_ns` marks it a LOWER BOUND.

_BOARD_GLYPH = {ADVANCING: "🟢", DISPATCHED: "🚀", OPEN: "🟡", HELD: "⏸", BLOCKED: "⛔",
                DONE: "✅", UNREADABLE: "❓"}


def _read_pointer(root: str, pointer: str | None):
    """`"file.json:a|b"` -> the value, or `(None, why)`. NEVER a default: a cost that could not be read
    must render as unreadable, not as `$0` — a swallowed error once became 'realised $0.0, breached=False'.

    ⚠ THE SEPARATOR IS `|`, NOT `.`, AND THAT IS NOT COSMETIC. Ladder rungs are keyed by a descriptive
    string — `"step1_fanout (19 RBFE edges @ ~13.7 GPU-h)"` — so a dotted path splits inside `13.7` and the
    lookup fails on the one rung whose cost anybody wants. Found by running the board against the real
    artifact, which is the only way this class of bug is ever found."""
    if not pointer:
        return None, "no cost pointer on this entry"
    fname, _, path = pointer.partition(":")
    doc, err = _load_json(os.path.join(root, fname))
    if doc is None:
        return None, err
    cur = doc
    for part in path.split("|"):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None, f"{pointer}: key {part!r} absent"
    return cur, None


def _pricing():
    """`(inflight_usd_per_ns, planning_usd_per_ref_gpu_h, congeneric_fanout)` or `(None, None, why)`.

    ★ LAZY, AND THAT IS STRUCTURAL. These are the only modules here that reach into the lanes' own cost
    stack, so importing them at module scope would let a fault in the cost model take the whole ledger down —
    the shape that killed the 11:37 AM progress check on 2026-07-27. Imported inside the renderer, a fault
    degrades ONE COLUMN of the board and says so. `test_work_ledger.py` asserts by AST that they never move
    to module scope.
    """
    try:
        import inflight_usd_per_ns as iu
        import congeneric_fanout as cf
        import vast_cost_model as vcm
        # DERIVED, never typed: the ladder's planning rate per reference GPU-hour, reconstructed from the
        # basis the cost model publishes. If this ever disagrees with the cost model, the cost model is right.
        return iu, cf.basis_usd_per_ns() * vcm.REFERENCE_NS_PER_H, cf
    except Exception as e:                          # noqa: BLE001
        return None, None, f"{type(e).__name__}: {e}"


def _usd_per_ns_cell(entries: list[dict], root: str) -> str:
    """One `$/ns` cell for a board group. `—` when no GPU is involved; never a fabricated figure, and never
    a figure computed for a DIFFERENT lane.

    ⚠ THE ATTRIBUTION RULE IS THE FIRST THING HERE, because the first board written by this module broke it:
    the step-1 fan-out's `offers_priced` list priced the closure triangle, the 5a-KS pair and the plan items
    as well, so three lanes displayed a refusal that had been computed for a fourth. An entry prices only
    from the snapshot it NAMES in `price_points_at`; an entry naming none renders `—`.
    """
    hosts, host_src = _hosts_for(entries, root)
    # ★ THE REFUSED COUNT IS MEASURED FROM THE GATE'S OWN SNAPSHOT, NOT INFERRED FROM ENTRY STATE. The first
    # version keyed it on `state in (OPEN, BLOCKED, HELD)` and so rendered NOTHING for a fan-out whose gate
    # had withheld eleven units, because each of those units was individually inside its evidence window and
    # therefore `advancing`. Two different questions — "is this item producing evidence" and "did the gate
    # decline to buy for it" — and only the snapshot answers the second. §6 requires that a decline is never
    # silent, so reading it off a state we derived ourselves is exactly the wrong source.
    snaps = sorted({e["price_points_at"] for e in entries if e.get("price_points_at")})
    if not hosts and not snaps:
        return "—"
    iu, plan, cf_or_err = _pricing()
    if iu is None:
        return f"$/ns UNAVAILABLE — the cost model could not be imported ({cf_or_err})"

    cells = []
    if hosts:
        # ★ THE WORST HOST IS THE ONE THAT MATTERS. A group's cheapest host cannot show drift; its dearest
        # can, and §1's whole point is that drift must be catchable at a glance. Priced from the INSTANCE
        # record (our bid + the real volume's disk line), never from a launcher's `dph≈` offer quote, which
        # is systematically LOW — measured $0.17922 quoted against $0.20272 billed.
        worst, worst_row = None, None
        for h in hosts:
            try:
                r = iu.row(h.get("gpu"), h.get("dph"), plan, stance=iu.PAYING,
                           rate_basis=iu.RATE_FROM_INSTANCE)
            except Exception:                       # noqa: BLE001 — an unbenched card is not a board failure
                continue
            if r.get("usd_per_ns") is not None and (worst is None or r["usd_per_ns"] > worst):
                worst, worst_row = r["usd_per_ns"], r
        if worst_row:
            cells.append(worst_row["cell"]
                         + (f" (worst of {len(hosts)} billed host(s) in {host_src})" if len(hosts) > 1
                            else f" [{host_src}]"))
    for snap in snaps:
        # The REFUSED side, priced from THIS lane's own gate snapshot — the number we DECLINED. §1: a row we
        # are paying and a row the gate refused must never render alike.
        hold, herr = _load_json(os.path.join(root, snap))
        if hold is None:
            cells.append(f"$/ns for the declined side UNREADABLE ({herr}) — an unreadable gate snapshot is "
                         f"NOT a gate that declined nothing")
            continue
        # How many units the gate itself says it withheld. Absent -> the snapshot records no refusal.
        n = next((hold[k] for k in ("n_held", "n_withheld") if isinstance(hold.get(k), int)), 0)
        if not n and hold.get("hold") is True:
            n = len(hold.get("units_needing_host") or []) or 1
        if not n:
            continue
        # The two gate artifacts genuinely use different key names (`offers_priced`/`min_bid` in the step-1
        # readout against `offers`/`min_bid_usd_h` in the ternary gate). They are read EXPLICITLY rather
        # than probed, so a rename surfaces as unreadable instead of silently pricing nothing.
        offers, bid_key = hold.get("offers_priced"), "min_bid"
        if not isinstance(offers, list):
            offers, bid_key = hold.get("offers"), "min_bid_usd_h"
        best = None
        if isinstance(offers, list) and offers:
            best = min((x for x in offers if isinstance(x, dict) and x.get("usd_per_ns") is not None),
                       key=lambda x: x["usd_per_ns"], default=None)
        if best:
            try:
                r = iu.row(best.get("gpu"), best.get(bid_key), plan, stance=iu.REFUSED,
                           rate_basis=iu.RATE_FROM_OFFER)
                cells.append(f"{n} unit(s) the gate withheld [{snap}]: {r['cell']}")
                continue
            except Exception:                       # noqa: BLE001 — an unbenched card is not a board failure
                pass
        cells.append(f"{n} unit(s) the gate withheld — $0 spent; {snap} carries no priceable offer to quote")
    if cells:
        return " · ".join(cells)
    if snaps and not hosts:
        # It IS a GPU lane and it may well be billing — but its per-host record lives in the object store,
        # not in git, so there is nothing here to price. Saying so beats a `—` that reads as "no GPU".
        return ("$/ns NOT PRICEABLE FROM GIT — this lane's per-host record lives in the object store, and "
                "this module holds no credential for it by design (a watcher that shares a credential with "
                "what it watches dies with it)")
    return "—"


def _cost_cell(entries: list[dict], root: str) -> str:
    """The dollars, POINTED AT rather than typed. `$0` only when there is genuinely no compute."""
    ptrs = {e["cost_points_at"] for e in entries if e.get("cost_points_at")}
    if not ptrs:
        # ⚠ TWO DIFFERENT ZEROES. A plan item has no compute and never will; a GPU lane with nothing rented
        # is spending $0 RIGHT NOW and could be spending money in ten minutes. Rendering them with the same
        # cell is how a lane that quietly stopped reads like a milestone nobody scheduled.
        if any(e.get("price_points_at") or e.get("hosts_points_at") for e in entries):
            return "$0 right now (a compute lane with nothing rented — not the same as having no compute)"
        return "$0 (no compute — CI / analysis / a plan item or a rung)"
    out = []
    for ptr in sorted(ptrs):
        v, err = _read_pointer(root, ptr)
        label = ptr.split(":", 1)[0]
        if err:
            # ★★ "THE KEY IS MISSING" AND "THE GATE HAD NOTHING TO PRICE" ARE DIFFERENT FACTS, and only one
            # of them is a defect. CAUGHT ON THE REAL BOARD after a merge: the ternary gate writes TWO
            # shapes — a full priced snapshot when it evaluated a board, and a short `nothing_to_launch`
            # one when every unit was already done or hosted, which carries no `plan_usd` at all. A fixed
            # pointer cannot be right for both, so the SHAPE is read rather than assumed. Reporting the
            # short form as UNREADABLE would cry wolf on a gate doing exactly the right thing; reporting it
            # as `$0` with no explanation would hide a genuine schema break behind a plausible number.
            v2, _ = _read_pointer(root, f"{label}:nothing_to_launch")
            n2, _ = _read_pointer(root, f"{label}:n_units")
            if v2 is True or n2 == 0:
                out.append(f"$0 this pass — the gate had nothing to buy (`nothing_to_launch`) [{label}]")
            else:
                out.append(f"cost UNREADABLE ({err})")
        elif isinstance(v, list) and len(v) == 2:
            out.append(f"${float(v[0]):.2f}-${float(v[1]):.2f} [{label}]")
        else:
            out.append(f"${v} [{label}]")
    return " · ".join(out)


def _hosts_for(entries: list[dict], root: str) -> tuple[list[dict], str]:
    """The billed hosts a group is part of, read from the artifact the entries POINT AT.

    ⚠ `gpu_util` IS IN THIS LIST AND IS NEVER TOUCHED. 0.0 has been observed on genuinely advancing hosts,
    and `vast_idle_guard.py`'s one inviolable rule is that GPU idleness NEVER condemns a box. Only `gpu` and
    `dph` are read here, plus `age_min` for the ETA; `cur_state` is not read either, because `exited` is
    routinely transient — three instances read `exited` and were running again 21 min later.
    """
    ptrs = sorted({e["hosts_points_at"] for e in entries if e.get("hosts_points_at")})
    hosts, src = [], []
    for ptr in ptrs:
        v, err = _read_pointer(root, ptr)
        if isinstance(v, list):
            hosts.extend(h for h in v if isinstance(h, dict))
            src.append(ptr.split(":", 1)[0])
        elif err:
            src.append(f"{ptr} UNREADABLE ({err})")
    return hosts, ", ".join(src) if src else "no host artifact named"


def _eta_cell(entries: list[dict], root: str, now: datetime.datetime) -> str:
    """ETA in ET, 12-hour — or an EXPLICIT 'ETA unknown' naming why. §1 permits the second; it forbids
    silence, and it forbids a guess dressed as a measurement.

    ⚠ `now` IS PASSED IN, NOT READ FROM THE CLOCK. The first version called `datetime.now()` here while the
    rest of the run used the `--now` override, so a replay of a past incident produced ETAs against today —
    a board that cannot be replayed deterministically cannot be verified, and verification is the point.
    """
    # A plan item or a rung has no compute and therefore no ETA — and saying "ETA unknown" about a
    # milestone would read as a job whose finish nobody can predict. Different facts, different cells.
    if all(e.get("scanner") in ("plan_items", "rung_gates") for e in entries):
        return "— (no compute: a plan item or a rung, not a running job)"
    hosts, _src = _hosts_for(entries, root)
    if not hosts:
        return "ETA unknown — nothing in this group is on a host right now"
    iu, _plan, cf = _pricing()
    if iu is None or not hasattr(cf, "UNIT_GPU_H"):
        return "ETA unknown — the per-unit GPU-hour budget could not be read from the cost model"
    lo, hi = cf.UNIT_GPU_H                          # the ladder's own per-unit budget. Derived, not typed.
    mid_min = (lo + hi) / 2.0 * 60.0
    lefts = [mid_min - h["age_min"] for h in hosts if isinstance(h.get("age_min"), (int, float))]
    if not lefts:
        return "ETA unknown — no host age in step1-fanout-progress.json to run the budget against"
    first = now + datetime.timedelta(minutes=max(0.0, min(lefts)))
    last = now + datetime.timedelta(minutes=max(0.0, max(lefts)))
    return (f"{_et_short(first)} - {_et_short(last)} (ESTIMATE: the ladder's per-unit GPU-h budget less "
            f"each host's age — not a measurement)")


def render_board(doc: dict, root: str, now: datetime.datetime | None = None) -> str:
    """The IN FLIGHT board, in the §1 format — one line per item:
    **what · state · ETA in ET 12-hour · cost · `$/ns` against basis**.

    ⚠ Rows come ONLY from `doc["entries"]`. There is no argument by which a row can be added, so a claimed
    owner that was never dispatched cannot appear — which is failure 5, made unwritable rather than
    discouraged.

    ★ WHAT GETS ITS OWN LINE, AND WHY THE REST IS COUNTED. Three things are enumerated: an entry BLOCKED
    BECAUSE ITS RETRY BUDGET IS SPENT (the auto-assign risk actually materialising), an UNOWNED entry (the
    defect this exists to surface), and a scanner that did not run (a coverage gap). Everything else is
    counted. That is deliberate: 12 plan items correctly blocked behind their own stated gates are CORRECT
    BEHAVIOUR, and a board that enumerates twelve rows of correct behaviour buries the one row that is not.
    A guard that condemns correct behaviour gets switched off within a day.
    """
    now = now or _parse_z(doc.get("_generated_utc")) or datetime.datetime.now(datetime.timezone.utc)
    entries = [e for e in (doc.get("entries") or []) if isinstance(e, dict)]
    lines = [f"IN FLIGHT — GENERATED from work-ledger.json at {doc.get('_generated_et')} "
             f"(no ledger entry, no row)",
             f"  {len(entries)} ledger entr(ies): " + ", ".join(
                 f"{n} {s}" for s, n in sorted(_counts(entries).items()))]

    groups: dict[str, list[dict]] = {}
    for e in entries:
        groups.setdefault(str(e.get("board_group")), []).append(e)

    for gname in sorted(groups, key=lambda g: (g == "plan", g)):
        rows = groups[gname]
        live = [e for e in rows if e.get("state") != DONE]
        if not live:
            lines.append(f"  ✅ {gname:<20} all {len(rows)} entr(ies) done · no further ETA · $0 further · —")
            continue
        counts = _counts(live)
        state = max(counts, key=lambda st: (st == BLOCKED, st == OPEN, counts[st]))
        glyph = _BOARD_GLYPH.get(state, "?")
        what = (rows[0].get("what") or gname) if len(rows) == 1 else \
            f"{gname} — {len(live)} open entr(ies) (" + ", ".join(
                f"{n} {st}" for st, n in sorted(counts.items())) + ")"
        lines.append(f"  {glyph} {str(what)[:112]}")
        lines.append(f"       {state} · {_eta_cell(live, root, now)}")
        lines.append(f"       {_cost_cell(live, root)} · {_usd_per_ns_cell(live, root)}")

        spent = [e for e in live if e.get("blocked_cause") == "retry-budget-spent"]
        gated = [e for e in live if e.get("blocked_cause") == "external-gate"]
        unowned = [e for e in live if not e.get("owner") and e.get("blocked_cause") != "external-gate"]
        for e in spent:
            lines.append(f"       ⛔ BLOCKED — RETRY BUDGET SPENT — {str(e.get('what'))[:80]}")
            for b in (e.get("blocked_by") or [])[:2]:
                lines.append(f"            {str(b)[:112]}")
            lines.append(f"            {len(e.get('attempts') or [])} attempt(s) on record with the "
                         f"fingerprint each was made against. NOT retried again until that fingerprint "
                         f"moves; NOT dropped.")
        if gated:
            lines.append(f"       ⏸ {len(gated)} entr(ies) blocked behind a stated gate of their own "
                         f"(correct behaviour, counted not listed): "
                         + "; ".join(str(e.get("what"))[:44] for e in gated[:3])
                         + (" …" if len(gated) > 3 else ""))
        for e in unowned:
            lines.append(f"       🟡 UNOWNED — nothing is carrying this — {str(e.get('what'))[:80]}")

    s = doc.get("_self") or {}
    lines.append(f"  {'🟢' if s.get('ok') else '🔴'} work-ledger self-check · {s.get('verdict')} · — · $0 · —")
    lines.append(f"       {str(s.get('detail'))[:200]}")
    for c in (doc.get("_scanners") or []):
        if not c.get("ran"):
            lines.append(f"  ❓ SCANNER {c.get('scanner')} DID NOT RUN — {c.get('error')}. That category is "
                         f"UNSCANNED, which is NOT the same as empty.")
    for r in (doc.get("_dispatch_plan") or []):
        mark = "held back by the per-run cap" if r.get("capped") else "dispatching"
        lines.append(f"  🚀 {mark}: {r['workflow']} {json.dumps(r.get('inputs') or {})} for "
                     f"{len(r['serves'])} entr(ies) · gated by {str(r['gated_by'])[:60]}")
    return "\n".join(lines)


def _counts(entries: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for e in entries:
        out[str(e.get("state"))] = out.get(str(e.get("state")), 0) + 1
    return out


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# build + entry point
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def build(root: str, strategy_path: str, schedule_path: str, now: datetime.datetime, *,
          prev: dict | None = None, use_api: bool = False, runs: list[dict] | None = None,
          fetch_error: str | None = None, source_roots: dict[str, str] | None = None) -> dict:
    found, cov = gather(root, strategy_path, schedule_path, now, use_api=use_api,
                        source_roots=source_roots)
    entries = reconcile(prev, found, now)
    plan = dispatch_plan(entries, now)              # records an attempt on every entry it serves
    stale_after = now + datetime.timedelta(minutes=EXPECTED_TICK_MIN * STALE_AFTER_TICKS)
    doc = {
        "_what": "One entry per OPEN ITEM, created by SCANNERS and never by hand. Work with no owner is "
                 "indistinguishable from work in progress; this file is what makes the difference visible. "
                 "The IN FLIGHT board is GENERATED from it, so a row with no entry cannot be written.",
        "_read_this_when": "something stalled and you want to know whether anything was carrying it — or "
                           "when you are about to write an IN FLIGHT board and need the rows.",
        "_rules": {
            "auto_assign_never_escalate": "trimcrae, 2026-07-27. The ledger dispatches the next action "
                                          "itself and does not interrupt him. Everything stays recorded.",
            "bounded_retry": f"{MAX_FRUITLESS_ATTEMPTS} automatic attempts with no new evidence -> `blocked`, "
                             f"with the evidence of each failure, and never retried again until the "
                             f"fingerprint moves. Never a silent drop, never a loop.",
            "never_bypasses_a_spend_gate": "every dispatch names an existing workflow whose own path carries "
                                           "the §6 market gate; no price, bid, ceiling or ratio may be "
                                           "passed (DISPATCHABLE + _FORBIDDEN_INPUT_TOKENS).",
            "never_destructive": "no destroy, reap, condemn or blacklist — those stay in the lanes' own "
                                 "collect paths. Asserted by AST in tests/test_work_ledger.py.",
            "a_price_hold_is_not_a_stall": "§6 makes a hold a SUCCESS. Held entries get no action, accrue no "
                                           "attempts, and can never decay into `blocked`.",
        },
        "_generated_utc": _z(now), "_generated_et": _et(now),
        "_expected_tick_min": EXPECTED_TICK_MIN,
        "_tick_workflow": TICK_WORKFLOW,
        "_stale_after_utc": _z(stale_after), "_stale_after_et": _et(stale_after),
        "_stale_after_means": "IF THE CLOCK IS PAST THIS AND THIS FILE HAS NOT CHANGED, THE SUPERVISOR CHAIN "
                              "HAS STOPPED and every item below is unwatched. A supervisor that has stopped "
                              "cannot report that it stopped, so this deadline is written INTO the artifact: "
                              "a reader who does nothing but open the file can tell. Restart with "
                              "`gh workflow run step1-fanout-supervisor.yml --ref main`.",
        "_scanners": cov,
        "_scanner_coverage_is_the_claim": "a category with no scanner is invisible, and invisible looks "
                                          "exactly like healthy. What is and is NOT scanned is listed in "
                                          "work_ledger.py's module docstring; the SCANNERS tuple is the "
                                          "machine copy and the tests assert they agree.",
        "entries": [e.as_dict() for e in entries],
        "_dispatch_plan": plan,
        "_dispatch_plan_is_a_request": "this module NEVER shells out. The workflow executes these with "
                                       "`gh workflow run`; each names a workflow and no price.",
    }
    doc["n_by_state"] = _counts(doc["entries"])
    doc["blocked"] = [e["id"] for e in doc["entries"] if e["state"] == BLOCKED]
    doc["unowned"] = [e["id"] for e in doc["entries"] if not e["owner"] and e["state"] != DONE]
    doc["_self"] = self_check(doc, now, runs=runs, fetch_error=fetch_error)
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--source-root", action="append", default=None, metavar="SOURCE=DIR",
                    help="where a lane's artifacts actually live, e.g. `ternary=/tmp/roots/ternary`. "
                         "Passed straight through to lane_staleness_watch — see its gather() header for "
                         "why one root is not enough.")
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    # ⚠ `--strategy` is kept as an ALIAS, not a second setting: the plan moved out of STRATEGY.md into the
    # roadmap on 2026-08-02 and any caller still passing the old flag must land on the same document.
    ap.add_argument("--plan-doc", "--strategy", dest="strategy", default=DEFAULT_PLAN_DOC)
    ap.add_argument("--schedule", default=DEFAULT_SCHEDULE)
    ap.add_argument("--now", default=None, help="ISO8601Z override, for deterministic verification")
    ap.add_argument("--json", default=None)
    ap.add_argument("--board", action="store_true", help="print the IN FLIGHT board")
    ap.add_argument("--write", action="store_true", help="persist the ledger for the next run")
    ap.add_argument("--emit-dispatch", default=None,
                    help="write the dispatch plan for the workflow to execute with `gh workflow run`")
    ap.add_argument("--no-api", action="store_true", help="skip the Actions API (offline / unit runs)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any entry is blocked (for a caller that wants that; the default is a "
                         "RECORD, because the ruling is auto-assign and never escalate)")
    a = ap.parse_args(argv)

    now = _parse_z(a.now) if a.now else datetime.datetime.now(datetime.timezone.utc)
    if now is None:
        print(f"::error::--now {a.now!r} is not an ISO8601 Z timestamp", file=sys.stderr)
        return 2

    source_roots = {}
    for item in (a.source_root or []):
        if "=" not in item:
            print(f"::error::--source-root {item!r} must be SOURCE=DIR", file=sys.stderr)
            return 2
        name, _, path = item.partition("=")
        # Same refusal as lane_staleness_watch: a mapping that points nowhere reads as an empty directory,
        # every lane there looks like it has no evidence, and THIS module would dispatch against that.
        if not os.path.isdir(path):
            print(f"::error::--source-root {name}={path!r} is not a directory", file=sys.stderr)
            return 2
        source_roots[name.strip()] = path

    prev, _perr = _load_json(a.ledger)
    runs, ferr = (None, None)
    if not a.no_api:
        runs, ferr = fsa.fetch_runs(REPO, TICK_WORKFLOW)
    doc = build(a.root, a.strategy, a.schedule, now, prev=prev, use_api=False, runs=runs,
                fetch_error=ferr, source_roots=source_roots)

    print(f"[work-ledger] {len(doc['entries'])} entr(ies) at {doc['_generated_et']}: "
          + ", ".join(f"{n} {s}" for s, n in sorted(doc["n_by_state"].items())))
    for c in doc["_scanners"]:
        mark = "ok " if c["ran"] else "!! "
        print(f"[work-ledger]  {mark}{c['scanner']:<14} {c['found']:>3} — {c['error'] or c['how']}")
    for row in doc["_dispatch_plan"]:
        print(f"[work-ledger]  -> dispatch {row['workflow']} {json.dumps(row.get('inputs') or {})} "
              f"for {len(row['serves'])} entr(ies); gated by {row['gated_by'][:70]}")
    if not doc["_dispatch_plan"]:
        print("[work-ledger]  -> nothing to dispatch (everything is advancing, resting on a gate, done, "
              "or blocked with its budget spent)")
    for eid in doc["blocked"]:
        print(f"[work-ledger]  ⛔ BLOCKED {eid} — recorded, visible, and NOT retried again")
    print(f"[work-ledger] self-check: {doc['_self']['verdict']} — {doc['_self']['detail']}")

    if a.board:
        print()
        print(render_board(doc, a.root, now))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
    if a.emit_dispatch:
        with open(a.emit_dispatch, "w") as fh:
            json.dump(doc["_dispatch_plan"], fh, indent=2)
            fh.write("\n")
    if a.write:
        with open(a.ledger, "w") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
    if a.strict and doc["blocked"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
