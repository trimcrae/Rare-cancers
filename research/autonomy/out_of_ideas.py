#!/usr/bin/env python3
"""THE TERMINAL STATE A ROUTE CAN REACH WHILE BEING WORKED ON: **out of ideas** (AUT-PROP-035).

⛔⛔ THE FAILURE THIS EXISTS FOR IS THE OPPOSITE OF A STALL. A stalled row does nothing. This one is
busy: it is claimed, attempted, released, re-claimed, re-planned and re-attempted, and every attempt
ends without a single new measurement. Nothing about it looks frozen — `what` grows, the plan gets
sharper, the row reads livelier every cycle — and the route is finished all the same, because the
loop has stopped generating ideas that produce evidence. Nobody notices, because every instrument
this repository already had reads that row as healthy.

★★ HOW THIS DIFFERS FROM `stuck_clock.py`, IN ONE SENTENCE, WHICH IS THE THING TO READ IF YOU READ
NOTHING ELSE: **`stuck_clock` asks whether the row CHANGED and fires when nothing did;
`out_of_ideas` asks whether the changes AMOUNTED to a measurement and fires when repeated genuine
attempts did not** — so the two are not a strong and a weak version of one detector, they are
orthogonal, and the proof is that this module's clock is built out of exactly the fields
`stuck_clock` throws away.

  `stuck_clock.TOUCH_FIELDS` contains `attempts` and `owner`, argued there at length: a retry is not
  an advance, a lease is not work, and letting either move the advance clock rebuilds the bug. That
  is correct FOR THAT QUESTION. For THIS question those two fields are the only honest record of
  how many times automation tried, so they are promoted from noise to clock. Symmetrically,
  `stuck_clock.PROGRESS_FIELDS` contains `what` and `depends_on_evidence` — a rewritten plan really
  is an advance in what is known — and here they are demoted: a re-plan is precisely what ARIS's
  loop does after an EMPTY round, so counting it as improvement would make this detector
  unfireable by construction (every empty round ends in a re-plan).

  ⭐ BOTH DIRECTIONS OF DISAGREEMENT ARE REAL, WHICH IS WHY BOTH MODULES EXIST:
    · green here, terminal there — a row nobody has touched for 24 h. No attempts, so no empty
      rounds; `stuck_clock` is the detector that fires, and this one says `not_attempted`.
    · terminal here, green there — a row claimed by four seats in a day, `what` rewritten each
      time, no evidence path, no outcome, no resolution. `stuck_at` moves on every re-plan, so
      `stuck_clock` reports it fresh; this module reports four empty rounds.
  ⛔ NEITHER SUBSUMES THE OTHER AND NEITHER SHOULD BE DELETED IN FAVOUR OF THE OTHER. A future
  session tempted to merge them should note that the merge requires one field classification to
  serve two contradictory questions, and there isn't one.

★★ THE SOURCE, AND THE TWO-CLAUSE SHAPE. `research/method-watch-autonomy-prior-art-2.md` §3: "out of
ideas" is a NAMED terminal condition in every long-running autonomous-science loop surveyed.
  · A-Lab runs "until the target is obtained as the majority phase or all synthesis recipes
    available to the A-Lab are exhausted".
  · Polybot terminates "when the experiment exceeds two weeks or when the measured conductivity do
    not show further improvement" — **a wall-clock budget OR no further improvement**, the two-clause
    rule ported below.
  · ARIS runs a watchdog on EMPTY ITERATIONS: an empty round forces a re-plan, and FOUR empty rounds
    escalate to a human. That count is the threshold adapted here.

★ WHY THE BORROWED *COUNT* TRANSFERS WHERE A BORROWED *DURATION* DOES NOT. `stuck_clock` refused
Rucio's 14 days because a duration is denominated in the borrowing system's beat and Rucio's daemon
beats ~10^3 times inside its threshold while this loop beats 6 times inside its own. ARIS's four is
not a duration: it counts ATTEMPTS, and an attempt here and an attempt there are the same unit — one
full try that ended without a measurement. It survives a change of cadence unchanged, which is
exactly the property the Rucio number lacked. ⭐ AND THE LOCAL BRACKET AGREES, which is why it is
adopted rather than merely cited: `research-ledger.json` rows carry `retry_budget: 3`, so a terminal
verdict at 4 empty rounds can never fire before a row's own retry budget is spent. A threshold of 3
would collide with it; 4 is the first value that cannot.

⛔ WHERE THIS DELIBERATELY DEPARTS FROM POLYBOT, SAID PLAINLY RATHER THAN SMUGGLED. Polybot's
wall-clock clause is a budget on TOTAL EXPERIMENT DURATION — two weeks from the start, improving or
not. That clause cannot be ported verbatim: CLAUDE.md §5 defines this program as "long-lived on a
rising frontier", where a parked route means "revisit when capability X lands", so closing a route
for the offence of being old would contradict the operating regime the whole portfolio runs on.
The clause is therefore ported as a budget on **time since the last measured improvement**, which
keeps the thing Polybot's clause is FOR (a route cannot consume unbounded wall clock on the promise
of a result) and drops the thing this program rejects (age alone as a verdict).

★ AND ITS NUMBER IS READ, NOT TYPED (CLAUDE.md §1). `priority-weights.json:age_saturates_days.value`
is already pinned in committed state, and its recorded meaning is the meaning this clause needs
verbatim: the point at which "waiting is itself the finding", after which the queue's own
anti-starvation term stops rescuing the row — more waiting buys it nothing. Its clock there is time
since evidence last moved, which is the same semantic as this clause, taken from a self-typed date
rather than from git. So this module reads that constant and measures it honestly. ⭐ That the value
committed there is 14 days and Polybot's budget is two weeks is an ANCHOR that agrees, in the sense
`stuck_clock` uses the word — it is not the argument, and if the weight is re-tuned tomorrow this
clause moves with it and no line here needs editing.

⛔ COMPUTED FROM COMMITTED STATE, LIKE ITS COMPANION, AND FOR THE SAME REASON. Both clocks are
derived from the git history of `research-ledger.json` via `stuck_clock.ledger_versions`. Nothing
here writes to the ledger, and no field a session can type is read as evidence of anything —
`last_evidence_utc` in particular is ignored (CLAUDE.md §4: a populated field is not a measured one;
a session that is out of ideas can type a fresh date).

⛔⛔ IT FAILS CLOSED, AND THE FAILURE IS NAMED RATHER THAN SWALLOWED. There is NO code path from "I
could not measure this" to "this route is fine". Every route lands in exactly one of four verdicts —
`out_of_ideas`, `has_ideas`, `not_attempted`, `unmeasurable` — and `unmeasurable` counts as needing
attention, exits non-zero under `--fail-on-terminal`, and is never rendered like a pass. The
concrete cases: a shallow clone whose horizon is younger than the budget (the C1 reading is then a
lower bound BELOW the budget, which decides nothing); an unparseable ledger; a route whose rows
changed only in fields this module has never heard of. That last one is why an unrecognised field is
counted as NOT an improvement and reported by name: reading an unknown field as improvement would
silently clear the streak and hide the terminal state (quiet), while reading it as non-improvement
at worst names a route a human then looks at (loud).

Usage:
    python3 research/autonomy/out_of_ideas.py --check                 # per-route board
    python3 research/autonomy/out_of_ideas.py --check --rows          # per-ledger-row detail
    python3 research/autonomy/out_of_ideas.py --check --json
    python3 research/autonomy/out_of_ideas.py --check --fail-on-terminal   # exit 1 if any route
                                                    # is out_of_ideas OR unmeasurable-with-attempts
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import stuck_clock  # noqa: E402

LEDGER_PATH = stuck_clock.LEDGER_PATH
WEIGHTS_PATH = os.path.join("research", "autonomy", "priority-weights.json")

# --------------------------------------------------------------------------------------------
# What counts as a MEASURED IMPROVEMENT. One home for it, argued in the module docstring: this is
# the whole decision, and a reader and a writer must not be able to disagree about it (the
# AUT-PD-013 / AUT-PD-017 reader-writer mismatch family).
# --------------------------------------------------------------------------------------------

#: Fields whose arrival carries a MEASUREMENT — an observation, a committed artifact, or a recorded
#: result. Strictly narrower than `stuck_clock.PROGRESS_FIELDS`, and the difference is the point.
MEASUREMENT_FIELDS = frozenset({
    "evidence_paths",      # paths to committed artifacts: the strongest form here
    "outcome",
    "observed",
    "result",
    "blocked_evidence",    # CLAUDE.md §0: producing a block's evidence IS the measurement
    "closes_clause",       # a bar clause closed is a measured, checkable event
    "lesson",
})

#: Fields that change while a route re-plans and learns nothing new. Enumerated rather than left to
#: the `else` branch so that the disagreement with `stuck_clock` is explicit and greppable: the first
#: three are `PROGRESS_FIELDS` there, and demoting them is deliberate.
NON_MEASUREMENT_FIELDS = frozenset({
    "what",                  # the re-plan ARIS's empty round produces. Counting it defeats the rule.
    "depends_on_evidence",   # pointing at somebody else's evidence is not producing any
    "prerequisite_of",       # a structural finding about ordering, not a measurement
    "superseded_note",
    "last_evidence_utc",     # self-typed; §4
    "_block_cleared",
    "also_worth_fixing",
    "open_question_for_trimcrae",
    "why_not_fixed_here",
    "what_is_actually_lost",
    "why_the_restore_is_still_right",
    "CORRECTION",
    "_renamed_from",
    "_contested",
    "_claim_workers_why",
    "claim_workers",
    "evidence_paths_note",
    "_score_is_null_why",
    "process_defect",
    "requires_trimcrae",     # handled separately: an escalation, not an improvement (see below)
    "requires_trimcrae_why",
    "_requires_trimcrae_why",
})

#: Entering one of these is a RESOLUTION and is the strongest measurement a row can record: the work
#: is over and the row says how. `blocked` is included on the same reasoning `stuck_clock` gives —
#: the ranker's clamp turns an evidence-free `blocked` back into a queued re-test, so the state only
#: survives with evidence attached.
RESOLUTION_STATES = frozenset({"done", "abandoned", "superseded", "blocked"})

#: Every field this module has an opinion about. Anything else is `unclassified`: NOT an improvement
#: (the loud direction) and named in the report.
KNOWN_FIELDS = (MEASUREMENT_FIELDS | NON_MEASUREMENT_FIELDS
                | stuck_clock.PROGRESS_FIELDS | stuck_clock.TOUCH_FIELDS)

# --------------------------------------------------------------------------------------------
# The two clauses.
# --------------------------------------------------------------------------------------------

#: CLAUSE 2's threshold. ARIS's four empty rounds escalating to a human, adopted as a COUNT because a
#: count survives a change of cadence where a borrowed duration does not (module docstring), and
#: bracketed locally by `retry_budget: 3` — the first value that cannot fire before a row's own
#: retries are spent. ⚠ It is a number to be RE-MEASURED, not defended. The observation that would
#: settle it is the distribution of empty-round runs on rows that eventually DID produce a
#: measurement; with the ledger history censored at the shallow horizon that distribution is not yet
#: computable here, and this module says so rather than printing a young number for it.
EMPTY_ROUNDS_TO_HUMAN = 4

#: CLAUSE 1's fallback ONLY — the real value is read from `priority-weights.json`. Kept equal to the
#: committed weight so a missing weights file changes nothing silently; if they ever diverge the
#: weights file wins, which is the direction "one fact, one place" requires.
FALLBACK_BUDGET_DAYS = 14.0

#: Fallback for `claim_lease.periods`, read from the same file. Used only to decide when an
#: in-flight attempt has had its full allotted try (see `settled_attempts`).
FALLBACK_LEASE_PERIODS = 2

TERMINAL_STATE = "out_of_ideas"

#: The five verdicts. `unmeasurable` is not a kind of pass — see `needs_attention`; and
#: `no_open_rows` is kept SEPARATE from `has_ideas` rather than folded into it, because "this route
#: has no ledger work left" and "this route is still generating ideas that produce measurements" are
#: different readings and rendering them with the same word is how a board stops being read.
VERDICTS = ("out_of_ideas", "unmeasurable", "has_ideas", "not_attempted", "no_open_rows")


def _read_weights(repo: str = REPO) -> dict:
    try:
        with open(os.path.join(repo, WEIGHTS_PATH), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def budget_days(repo: str = REPO, weights: dict | None = None) -> float:
    """CLAUSE 1's budget, READ from `priority-weights.json:age_saturates_days.value`.

    ⛔ Never typed here. That weight is already pinned as the point where waiting stops buying
    anything, which is the exact semantic this clause needs; Polybot's two weeks is an anchor that
    agrees with the committed value, not the reason for it.
    """
    weights = _read_weights(repo) if weights is None else weights
    value = (weights.get("age_saturates_days") or {}).get("value")
    return float(value) if isinstance(value, (int, float)) and value > 0 else FALLBACK_BUDGET_DAYS


def lease_hours(repo: str = REPO, weights: dict | None = None,
                state_path: str | None = None) -> float:
    """How long one attempt is entitled to run before it counts as finished.

    `claim_lease.periods` x the loop's cycle interval — both read from their own files. An attempt
    still in flight inside its lease is NOT counted as an empty round: automation has not yet had
    the try it was granted, and counting it would fire the detector while the work is happening.
    """
    weights = _read_weights(repo) if weights is None else weights
    periods = (weights.get("claim_lease") or {}).get("periods")
    periods = periods if isinstance(periods, (int, float)) and periods > 0 else FALLBACK_LEASE_PERIODS
    path = state_path or os.path.join(repo, "research", "autonomy", "autonomy-state.json")
    return float(periods) * stuck_clock.cycle_interval_hours(path)


# --------------------------------------------------------------------------------------------
# Reading attempts and improvements out of the committed history.
# --------------------------------------------------------------------------------------------


def classify_measurement(field_name: str, before, after) -> str:
    """`"measurement"`, `"not_measurement"` or `"unclassified"` for one changed field.

    ⛔ THE THREE-WAY ANSWER IS LOAD-BEARING and `"unclassified"` is not folded into either at the
    call site — a field the ledger schema grows after this module was written must be COUNTED as a
    non-improvement and NAMED, never quietly decided.

    ⛔ AND AN EMPTIED FIELD IS NOT A MEASUREMENT. `outcome: "x" -> null` is a retraction; treating
    any change to a measurement field as an improvement would let deleting the evidence reset the
    streak, which is the same launder-your-own-failure shape Rucio's `stuck_at` refuses.
    """
    if field_name == "state":
        return "measurement" if after in RESOLUTION_STATES and before not in RESOLUTION_STATES \
            else "not_measurement"
    if field_name in MEASUREMENT_FIELDS:
        if after in (None, "", [], {}, ()):
            return "not_measurement"
        return "measurement" if before != after else "not_measurement"
    if field_name in KNOWN_FIELDS:
        return "not_measurement"
    return "unclassified"


def is_attempt_event(previous: dict, row: dict) -> bool:
    """Did automation START a fresh try on this row between these two committed versions?

    Two signals, and BOTH are `stuck_clock.TOUCH_FIELDS` — that is the whole inversion:
      · `owner` moved to a DIFFERENT non-empty session — a fresh claim, i.e. a try STARTING;
      · `attempts` increased — `priority.py:release_stale_claims` bumps it when a lease expires, so
        it is the loop's own count of tries that ended without the row closing.

    ⛔ AND THE SECOND SIGNAL IS SUPPRESSED WHEN IT ARRIVES WITH A RELEASE, WHICH IS NOT A DETAIL:
    `release_stale_claims` writes `owner -> None` and `attempts + 1` in the SAME commit, so the
    obvious implementation counts one try twice — once when it was claimed and once when it expired
    — and every threshold in this module is silently halved. Caught by
    `test_one_try_is_counted_once_however_it_is_committed`, which is why that test exists. A bump
    with no release (a retry inside a held claim, or a lease that expired without a claim ever
    reaching a committed version) is a try nobody counted at its start, and IS counted here.

    ⚠ At most one attempt event per committed version by construction (this returns a bool), so a
    version that both bumps `attempts` and re-claims counts once.
    """
    try:
        before = int(previous.get("attempts") or 0)
        after = int(row.get("attempts") or 0)
    except (TypeError, ValueError):
        before = after = 0
    owner_before = (previous.get("owner") or "").strip()
    owner_after = (row.get("owner") or "").strip()
    if owner_after and owner_after != owner_before:
        return True
    released = bool(owner_before) and not owner_after
    return after > before and not released


@dataclass
class RowHistory:
    """What the committed history says about one ledger row's attempts and measurements."""
    entry_id: str
    route: str | None = None
    state: str | None = None
    requires_trimcrae: bool = False
    first_seen: datetime.datetime | None = None
    censored: bool = False
    attempt_times: list = field(default_factory=list)
    improvement_times: list = field(default_factory=list)
    last_improvement_fields: set = field(default_factory=set)
    unclassified_fields: set = field(default_factory=set)

    def is_open(self) -> bool:
        return self.state not in stuck_clock.CLOSED_STATES

    @property
    def last_improvement(self) -> datetime.datetime | None:
        return max(self.improvement_times) if self.improvement_times else None


def compute_histories(versions: list, shallow: bool = False) -> dict:
    """Walk the committed ledger history once and record, per row, WHEN it was tried and WHEN a try
    produced a measurement.

    ⚠ Compared against the row's LAST SEEN state, not the previous version's, for the reason
    `stuck_clock.compute_clocks` gives: a row can vanish from one committed version and return
    unchanged, and treating the return as a creation would reset every count on it.
    """
    out: dict[str, RowHistory] = {}
    seen: dict[str, dict] = {}
    horizon_sha = versions[0].sha if versions else None
    for version in versions:
        for entry_id, row in version.rows.items():
            previous = seen.get(entry_id)
            if previous is None:
                out[entry_id] = RowHistory(
                    entry_id=entry_id,
                    route=(row.get("serves") or {}).get("route"),
                    state=row.get("state"),
                    requires_trimcrae=bool(row.get("requires_trimcrae")),
                    first_seen=version.when,
                    censored=bool(shallow and version.sha == horizon_sha),
                )
                seen[entry_id] = row
                continue

            history = out[entry_id]
            changed = [k for k in set(previous) | set(row) if previous.get(k) != row.get(k)]
            improved = False
            fields_now = set()
            for key in changed:
                verdict = classify_measurement(key, previous.get(key), row.get(key))
                if verdict == "unclassified":
                    history.unclassified_fields.add(key)
                elif verdict == "measurement":
                    improved = True
                    fields_now.add(key)
            if improved:
                history.improvement_times.append(version.when)
                history.last_improvement_fields = fields_now
            if is_attempt_event(previous, row):
                history.attempt_times.append(version.when)
            history.route = (row.get("serves") or {}).get("route")
            history.state = row.get("state")
            history.requires_trimcrae = bool(row.get("requires_trimcrae"))
            seen[entry_id] = row
    return out


def settled_attempts(attempt_times: list, now: datetime.datetime, lease_h: float) -> list:
    """The attempts that have had their full allotted try.

    An attempt is settled once a LATER attempt exists — the try demonstrably ended — or the lease it
    was granted has expired. ⛔ THE SECOND CLAUSE IS THE CRY-WOLF GUARD: an attempt claimed twenty
    minutes ago has not failed to produce anything, it has not finished, and a detector that counts
    it fires loudest exactly while the work is happening.

    ⚠ THERE IS NO PER-ROW "THIS ROW RESOLVED, SO ITS LAST ATTEMPT IS SETTLED" CLAUSE, AND THE
    OMISSION IS DELIBERATE RATHER THAN MISSING. Attempts are pooled ACROSS a route's rows, so at
    this point there is no row to ask. What the surviving reading means is exactly right anyway:
    "something was tried on this route inside the last lease". A parameter for the row case was
    written and then removed — nothing could pass it, and a parameter no caller can reach is the
    dead code `stuck_clock` documents catching by mutation, not a spare hook.
    """
    if not attempt_times:
        return []
    ordered = sorted(attempt_times)
    settled = ordered[:-1]
    latest = ordered[-1]
    if (now - latest).total_seconds() / 3600.0 >= lease_h:
        settled = settled + [latest]
    return settled


def empty_streak(attempt_times: list, last_improvement, now: datetime.datetime,
                 lease_h: float) -> int:
    """CLAUSE 2's count: settled attempts made since the last measured improvement.

    ⭐ Expressed as "after the last improvement" rather than by walking rounds backwards, because
    the two are equivalent and this spelling has no attribution edge cases: an improvement
    committed in the same version that opens a new attempt is credited to the attempt that just
    ENDED (the strictly-greater comparison), which is both the semantically right reading and the
    stricter one.
    """
    settled = settled_attempts(attempt_times, now, lease_h)
    if last_improvement is None:
        return len(settled)
    return len([t for t in settled if t > last_improvement])


# --------------------------------------------------------------------------------------------
# The verdict.
# --------------------------------------------------------------------------------------------


@dataclass
class RouteVerdict:
    """One route's reading. `verdict` is one of `VERDICTS`; there is no boolean 'ok' on purpose."""
    route: str | None
    verdict: str
    why: str
    open_rows: list = field(default_factory=list)
    attempts_settled: int = 0
    empty_rounds: int = 0
    hours_since_improvement: float | None = None
    budget_hours: float = 0.0
    last_improvement_utc: str | None = None
    censored: bool = False
    clauses: dict = field(default_factory=dict)
    unclassified_fields: list = field(default_factory=list)

    @property
    def needs_attention(self) -> bool:
        """⛔ FAIL CLOSED. `unmeasurable` is not a pass — a route git cannot judge is not 'fine',
        and this is the ONE place that decides what a non-pass is, so no caller can re-decide it."""
        return self.verdict == TERMINAL_STATE or self.verdict == "unmeasurable"


def route_verdict(route: str | None, histories: list, now: datetime.datetime,
                  budget_h: float, lease_h: float) -> RouteVerdict:
    """The two-clause rule, applied to one route's pooled ledger rows.

    OUT OF IDEAS  <=>  the route has open rows, has had at least one SETTLED attempt, is not
    already a human's, and EITHER
        C1  time since the last measured improvement exceeds the budget, OR
        C2  `EMPTY_ROUNDS_TO_HUMAN` settled attempts have been made since it.

    ⭐ WHY BOTH CLAUSES, WHEN EITHER LOOKS SUFFICIENT — and this is the reason to port Polybot's OR
    rather than pick the better half. C2 is EVENT-driven and goes blind exactly when attempts stop
    being recorded: a seat that dies before `attempts` is bumped, or work done outside the ledger,
    leaves the counter at its old value forever and C2 can never reach four. C1 is TIME-driven and
    goes blind in the opposite case: many attempts crammed into a short window are four empty rounds
    long before any budget elapses. Neither dominates, so a route is out of ideas if either fires.
    """
    open_rows = [h for h in histories if h.is_open()]
    unclassified = sorted({f for h in histories for f in h.unclassified_fields})
    if not open_rows:
        return RouteVerdict(route=route, verdict="no_open_rows",
                            why="the route has no open ledger row. It is idle or finished, which is "
                                "a different reading from still having ideas — and this module has "
                                "no evidence either way, so it claims neither.",
                            unclassified_fields=unclassified)

    # ⛔ ATTEMPTS AND IMPROVEMENTS ARE POOLED OVER THE ROUTE'S WHOLE HISTORY, OPEN ROWS AND CLOSED
    # ONES ALIKE, AND THIS IS A CORRECTION TO THE OBVIOUS IMPLEMENTATION RATHER THAN A DETAIL.
    # Pooling only OPEN rows biases the reading hard toward the terminal verdict, because the
    # strongest measurement a row can record — a resolution — is exactly the event that CLOSES it.
    # A route whose rows keep finishing would then show zero improvements forever while being the
    # most productive route on the board. Measured on the live ledger before the fix: RT-AUTONOMY,
    # 26 open rows and 66 resolved ones repo-wide, reported no improvement at all.
    # ⚠ A route still needs an OPEN row to be a candidate at all (the branch above): a route with
    # nothing queued cannot be out of ideas, it has no ideas outstanding.
    attempts = [t for h in histories for t in h.attempt_times]
    improvements = [t for h in histories for t in h.improvement_times]
    last_improvement = max(improvements) if improvements else None
    settled = settled_attempts(attempts, now, lease_h)
    streak = empty_streak(attempts, last_improvement, now, lease_h)
    censored = any(h.censored for h in open_rows)

    baseline = last_improvement
    if baseline is None:
        firsts = [h.first_seen for h in histories if h.first_seen]
        baseline = min(firsts) if firsts else None
    hours = (now - baseline).total_seconds() / 3600.0 if baseline else None

    c1 = hours is not None and hours >= budget_h
    c2 = streak >= EMPTY_ROUNDS_TO_HUMAN
    common = dict(
        route=route, open_rows=[h.entry_id for h in open_rows], attempts_settled=len(settled),
        empty_rounds=streak, hours_since_improvement=None if hours is None else round(hours, 2),
        budget_hours=budget_h,
        last_improvement_utc=last_improvement.strftime("%Y-%m-%dT%H:%M:%SZ") if last_improvement
        else None,
        censored=censored, clauses={"c1_wall_clock": bool(c1), "c2_empty_rounds": bool(c2)},
        unclassified_fields=unclassified,
    )

    if baseline is None:
        return RouteVerdict(verdict="unmeasurable",
                            why="git shows no committed version of these rows, so neither clause has "
                                "an input. Not a green route — an unread one.", **common)
    if not settled:
        return RouteVerdict(verdict="not_attempted",
                            why=f"{len(open_rows)} open row(s) and no settled attempt on any of "
                                f"them. A route nobody has tried is STARVED, not out of ideas; the "
                                f"fix is to take the item, not to escalate it.", **common)
    if all(h.requires_trimcrae for h in open_rows):
        return RouteVerdict(verdict="has_ideas",
                            why="every open row is already flagged `requires_trimcrae`: the human "
                                "handover this condition recommends has already happened, so a "
                                "second escalation would be noise. Reported, not hidden.", **common)
    if c1 or c2:
        fired = [name for name, hit in (("C1 wall-clock budget", c1),
                                        ("C2 empty rounds", c2)) if hit]
        return RouteVerdict(
            verdict=TERMINAL_STATE,
            why=(f"{' and '.join(fired)}. {streak} settled attempt(s) since the last measured "
                 f"improvement ({common['last_improvement_utc'] or 'never'}), "
                 f"{hours:.0f} h against a {budget_h:.0f} h budget. Automation has run out of ideas "
                 f"on this route: a human decides whether it is re-scoped, handed over or closed."),
            **common)
    if censored and last_improvement is None:
        return RouteVerdict(
            verdict="unmeasurable",
            why=(f"no measured improvement inside the visible history, and the history is CENSORED "
                 f"(shallow clone): {hours:.0f} h is a LOWER BOUND below the {budget_h:.0f} h "
                 f"budget, so C1 decides nothing and C2 has seen only part of the run. Not fine — "
                 f"unread. Remedy: git fetch --unshallow"), **common)
    return RouteVerdict(verdict="has_ideas",
                        why=(f"{streak} empty round(s) of {EMPTY_ROUNDS_TO_HUMAN}, and the last "
                             f"measured improvement was {hours:.0f} h ago against a {budget_h:.0f} h "
                             f"budget."), **common)


def route_reports(repo: str = REPO, path: str = LEDGER_PATH,
                  now: datetime.datetime | None = None) -> dict:
    """THE ONE CALL OTHER MODULES SHOULD USE. Returns every route's verdict plus the inputs."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    shallow = stuck_clock.is_shallow(repo)
    versions = stuck_clock.ledger_versions(repo, path)
    histories = compute_histories(versions, shallow=shallow)
    weights = _read_weights(repo)
    budget_h = budget_days(repo, weights) * 24.0
    lease_h = lease_hours(repo, weights,
                          os.path.join(repo, "research", "autonomy", "autonomy-state.json"))
    horizon = versions[0].when if versions else None

    by_route: dict = {}
    for history in histories.values():
        by_route.setdefault(history.route, []).append(history)
    verdicts = [route_verdict(route, rows, now, budget_h, lease_h)
                for route, rows in sorted(by_route.items(), key=lambda kv: (kv[0] or ""))]
    order = {name: i for i, name in enumerate(VERDICTS)}
    verdicts.sort(key=lambda v: (order.get(v.verdict, 9), -(v.empty_rounds or 0)))
    return {
        "now": now, "horizon": horizon, "shallow": shallow, "n_versions": len(versions),
        "budget_hours": budget_h, "lease_hours": lease_h,
        "empty_rounds_to_human": EMPTY_ROUNDS_TO_HUMAN,
        "histories": histories, "routes": verdicts,
    }


def terminal_routes(report: dict | None = None, **kwargs) -> list:
    """Every route automation should stop generating work for until a human has looked."""
    report = report or route_reports(**kwargs)
    return [v for v in report["routes"] if v.verdict == TERMINAL_STATE]


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="print the per-route board")
    parser.add_argument("--rows", action="store_true", help="also print per-ledger-row detail")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--path", default=LEDGER_PATH,
                        help="repo-relative ledger path (the CLI must be able to point at another "
                             "checkout, or nothing can test it against a known history)")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--fail-on-terminal", action="store_true",
                        help="exit 1 if any route is out_of_ideas OR unmeasurable")
    args = parser.parse_args(argv)

    report = route_reports(repo=args.repo, path=args.path)
    attention = [v for v in report["routes"] if v.needs_attention]

    if args.json:
        print(json.dumps({
            "generated_utc": report["now"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "history_horizon_utc": report["horizon"].strftime("%Y-%m-%dT%H:%M:%SZ")
            if report["horizon"] else None,
            "shallow_clone": report["shallow"],
            "terminal_state": TERMINAL_STATE,
            "empty_rounds_to_human": EMPTY_ROUNDS_TO_HUMAN,
            "budget_hours": report["budget_hours"],
            "lease_hours": report["lease_hours"],
            "routes": [{
                "route": v.route, "verdict": v.verdict, "why": v.why,
                "open_rows": v.open_rows, "attempts_settled": v.attempts_settled,
                "empty_rounds": v.empty_rounds,
                "hours_since_improvement": v.hours_since_improvement,
                "last_improvement_utc": v.last_improvement_utc,
                "censored": v.censored, "clauses": v.clauses,
                "unclassified_fields": v.unclassified_fields,
                "needs_attention": v.needs_attention,
            } for v in report["routes"]],
        }, indent=2))
        return 1 if (args.fail_on_terminal and attention) else 0

    print(f"   ledger history: {report['n_versions']} committed versions")
    print(f"   the two-clause rule: C1 no measured improvement in "
          f"{report['budget_hours'] / 24:.0f} d (read from priority-weights.json:"
          f"age_saturates_days)  OR  C2 {EMPTY_ROUNDS_TO_HUMAN} settled attempts since one "
          f"-> {TERMINAL_STATE}")
    print(f"   an attempt is settled after one claim lease ({report['lease_hours']:.0f} h)")
    if report["shallow"]:
        print("   ⛔ SHALLOW CLONE: routes with no improvement inside the visible history read "
              "`unmeasurable`, which is NOT a pass. Remedy: git fetch --unshallow")

    header = f"{'verdict':<14} {'empty':>5} {'since':>9}  {'route':<24} rows"
    print()
    print(header)
    print("-" * len(header))
    for v in report["routes"][:args.limit]:
        since = "—" if v.hours_since_improvement is None else f"{v.hours_since_improvement:.0f}h"
        mark = "⛔ " if v.verdict == TERMINAL_STATE else ("⚠ " if v.verdict == "unmeasurable" else "  ")
        print(f"{mark}{v.verdict:<12} {v.empty_rounds:>5} {since:>9}  {str(v.route):<24} "
              f"{len(v.open_rows)}")
    for v in report["routes"]:
        if v.needs_attention:
            print(f"\n   {v.route}: {v.why}")
            if v.unclassified_fields:
                print(f"      unclassified fields seen: {', '.join(v.unclassified_fields)}")

    if args.rows:
        print()
        print(f"{'row':<18} {'route':<22} {'attempts':>8} {'improvements':>13}  last improvement")
        for h in sorted(report["histories"].values(), key=lambda h: h.entry_id):
            if not h.is_open():
                continue
            last = h.last_improvement
            print(f"{h.entry_id:<18} {str(h.route):<22} {len(h.attempt_times):>8} "
                  f"{len(h.improvement_times):>13}  "
                  f"{last.strftime('%Y-%m-%d %H:%M') if last else '—'}")

    counts = {name: sum(1 for v in report["routes"] if v.verdict == name) for name in VERDICTS}
    print()
    print("   " + " · ".join(f"{n} {name}" for name, n in counts.items()))
    if not attention:
        print("   No route is out of ideas and none is unmeasurable. That is a reading of the "
              "committed history, not a green tick on the science.")
    return 1 if (args.fail_on_terminal and attention) else 0


if __name__ == "__main__":
    sys.exit(main())
