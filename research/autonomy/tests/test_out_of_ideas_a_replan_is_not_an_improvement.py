#!/usr/bin/env python3
"""THE ONE PROPERTY `out_of_ideas.py` EXISTS FOR, ASSERTED RATHER THAN DESCRIBED.

⛔ THE THREAT MODEL IS A ROUTE THAT NEVER STOPS THINKING AND NEVER PRODUCES A MEASUREMENT. Every
empty attempt ends the way ARIS says it ends — with a re-plan — and a re-plan is a real, substantive
edit to `what`. So the detector that already exists, `stuck_clock`, reads the row as advancing every
single time, correctly, because the plan really did change. The row can absorb attempts forever.

★ SO THE TESTS HERE ARE PAIRED WITH `test_stuck_clock_a_retry_is_not_an_advance.py` ON PURPOSE, AND
TWO OF THEM RUN BOTH MODULES OVER THE SAME FIXTURE. The invariant they defend is that the two
detectors DISAGREE in both directions on the histories they are each built for — if a future edit
ever makes one a strict refinement of the other, one of those two tests fails and the merge that
looked harmless is caught.

⚠ THE FIXTURES BUILD REAL GIT REPOSITORIES IN tmp_path, NOT MOCKS, for the reason the companion
suite gives: both readings are DERIVED from `git log`, and mocking git out would leave the
derivation itself untested. Commit timestamps are forced through GIT_AUTHOR_DATE/GIT_COMMITTER_DATE
so every assertion is about hours, deterministically.
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import out_of_ideas as O  # noqa: E402
import stuck_clock as S  # noqa: E402

T0 = datetime.datetime(2026, 8, 20, 12, 0, tzinfo=datetime.timezone.utc)
LEDGER = "ledger.json"
LEASE_H = 8.0            # `claim_lease.periods` 2 x a 4 h cycle, spelled out so the tests are exact
BUDGET_H = 14.0 * 24.0   # `age_saturates_days` 14 d, likewise


def _run(repo, *args, when=None):
    env = dict(os.environ)
    if when is not None:
        stamp = when.strftime("%Y-%m-%dT%H:%M:%S+0000")
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = stamp
    env.setdefault("GIT_AUTHOR_NAME", "test")
    env.setdefault("GIT_AUTHOR_EMAIL", "test@example.invalid")
    env.setdefault("GIT_COMMITTER_NAME", "test")
    env.setdefault("GIT_COMMITTER_EMAIL", "test@example.invalid")
    subprocess.run(["git", "-C", str(repo)] + list(args), check=True, env=env,
                   capture_output=True, text=True)


@pytest.fixture
def ledger_repo(tmp_path):
    """`commit(rows, hours_after_T0)` — append one committed version of a ledger."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q")

    def commit(rows, hours):
        when = T0 + datetime.timedelta(hours=hours)
        (repo / LEDGER).write_text(json.dumps({"entries": rows}, indent=2), encoding="utf-8")
        _run(repo, "add", LEDGER, when=when)
        _run(repo, "commit", "-q", "-m", f"+{hours}h", when=when)
        return when

    commit.repo = repo
    return commit


def _row(**kw):
    base = {"id": "AUT-X", "kind": "experiment", "state": "queued", "owner": None,
            "claimed_utc": None, "attempts": 0, "score": 100.0, "what": "try the thing",
            "serves": {"route": "RT-TEST"}, "blocked_by": None, "blocked_evidence": None,
            "last_evidence_utc": "2026-08-20", "requires_trimcrae": False, "retry_budget": 3}
    base.update(kw)
    return base


def _histories(fixture):
    return O.compute_histories(S.ledger_versions(str(fixture.repo), LEDGER))


def _verdict(fixture, now_hours, budget_h=BUDGET_H, lease_h=LEASE_H, route="RT-TEST"):
    histories = _histories(fixture)
    now = T0 + datetime.timedelta(hours=now_hours)
    rows = [h for h in histories.values() if h.route == route]
    return O.route_verdict(route, rows, now, budget_h, lease_h), histories, now


def _four_empty_attempts(fixture):
    """Four genuine tries, each ending in a re-plan and nothing else. The whole point."""
    fixture([_row()], 0)
    for i in range(1, 5):
        fixture([_row(owner=f"CYC-000{i}", claimed_utc=f"2026-08-2{i}T00:00:00Z", attempts=i,
                      score=100.0 + i, last_evidence_utc=f"2026-08-2{i}",
                      what=f"try the thing, attempt {i}: sharpen the plan, narrow the scope, "
                           f"re-read the source, and try again from a different angle")], i)


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE NEGATIVE CONTROL, AND THE ORTHOGONALITY PROOF.
# ---------------------------------------------------------------------------------------------

def test_four_attempts_that_only_ever_re_plan_are_out_of_ideas(ledger_repo):
    """Four real tries, four re-plans, zero measurements -> the terminal state, via C2 alone."""
    _four_empty_attempts(ledger_repo)
    verdict, _, _ = _verdict(ledger_repo, now_hours=24)
    assert verdict.verdict == O.TERMINAL_STATE, verdict.why
    assert verdict.empty_rounds == O.EMPTY_ROUNDS_TO_HUMAN
    assert verdict.clauses == {"c1_wall_clock": False, "c2_empty_rounds": True}, (
        "C2 must be able to fire ALONE. If C1 is carrying this case the wall-clock budget is too "
        "short and the event clause is untested.")
    assert verdict.needs_attention


def test_the_same_history_is_NOT_stuck_and_that_is_the_whole_point(ledger_repo):
    """⛔⛔ THE PAIRED ASSERTION. The identical fixture, read by `stuck_clock`, is FRESH: `what`
    changed on every commit, so the advance clock moved every time. A future edit that makes one
    module a refinement of the other breaks this test, which is what it is for."""
    _four_empty_attempts(ledger_repo)
    clocks = S.compute_clocks(S.ledger_versions(str(ledger_repo.repo), LEDGER))
    now = T0 + datetime.timedelta(hours=24)
    clock = clocks["AUT-X"]
    assert clock.stuck_at == T0 + datetime.timedelta(hours=4), (
        "the advance clock did not follow the re-plans — then this fixture is not the case "
        "out_of_ideas exists for")
    assert clock.terminal(now, 24.0, None) is None, (
        "stuck_clock called this row terminal. It must not: the row IS changing. If it does, the "
        "two modules have collapsed into one and the busy-but-fruitless case is unowned again.")
    verdict, _, _ = _verdict(ledger_repo, now_hours=24)
    assert verdict.verdict == O.TERMINAL_STATE


def test_a_frozen_row_is_stuck_but_NOT_out_of_ideas(ledger_repo):
    """⛔ THE DISAGREEMENT IN THE OTHER DIRECTION. One attempt, then silence. `stuck_clock` owns
    this; this module must say `not_attempted`-or-`has_ideas`, never claim the loop ran out of
    ideas on a route it tried once and abandoned."""
    ledger_repo([_row()], 0)
    ledger_repo([_row(owner="CYC-0001", claimed_utc="2026-08-21T00:00:00Z", attempts=1)], 1)
    clocks = S.compute_clocks(S.ledger_versions(str(ledger_repo.repo), LEDGER))
    now = T0 + datetime.timedelta(hours=40)
    assert clocks["AUT-X"].terminal(now, 24.0, None) is not None, (
        "the frozen row is not stuck — then this fixture is not the paired case")
    verdict, _, _ = _verdict(ledger_repo, now_hours=40)
    assert verdict.verdict != O.TERMINAL_STATE, verdict.why
    assert verdict.empty_rounds == 1


# ---------------------------------------------------------------------------------------------
# What resets the streak, and what must not.
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("field_name,value", [
    ("evidence_paths", ["research/data/thing.json"]),
    ("outcome", "the assay separates the paralogues at 3 kcal/mol"),
    ("observed", "no separation"),
    ("result", "null"),
    ("blocked_evidence", "GEO returns 403 at the proxy, log attached"),
    ("closes_clause", "CL-BAR-3"),
    ("lesson", "the control was the experiment"),
])
def test_a_measurement_resets_the_streak(ledger_repo, field_name, value):
    """Any real measurement on the fourth attempt takes the route back out of the terminal state."""
    _four_empty_attempts(ledger_repo)
    ledger_repo([_row(owner="CYC-0004", attempts=4, what="try the thing, attempt 4",
                      **{field_name: value})], 5)
    verdict, _, _ = _verdict(ledger_repo, now_hours=24)
    assert verdict.verdict != O.TERMINAL_STATE, (
        f"a new `{field_name}` did not count as a measurement: {verdict.why}")
    assert verdict.empty_rounds == 0


def test_a_resolution_is_the_strongest_measurement(ledger_repo):
    """`state -> done` closes the row. The route must not read terminal on the strength of the
    attempts that produced the answer."""
    _four_empty_attempts(ledger_repo)
    ledger_repo([_row(owner="CYC-0004", attempts=4, state="done")], 5)
    verdict, _, _ = _verdict(ledger_repo, now_hours=24)
    assert verdict.verdict == "no_open_rows", verdict.why
    assert not verdict.needs_attention


def test_a_route_is_credited_with_the_measurements_of_its_CLOSED_rows(ledger_repo):
    """⛔ THE BIAS THAT NEARLY SHIPPED. The strongest measurement a row can record is a resolution —
    which is exactly the event that removes it from the open set. Pooling only open rows would make
    the most productive route on the board read as producing nothing."""
    ledger_repo([_row(id="AUT-DONE"), _row(id="AUT-OPEN")], 0)
    for i in range(1, 5):
        ledger_repo([_row(id="AUT-DONE"),
                     _row(id="AUT-OPEN", owner=f"CYC-000{i}", attempts=i,
                          what=f"re-plan {i}")], i)
    ledger_repo([_row(id="AUT-DONE", state="done", outcome="measured, and here is the number"),
                 _row(id="AUT-OPEN", owner="CYC-0004", attempts=4, what="re-plan 4")], 5)
    verdict, _, _ = _verdict(ledger_repo, now_hours=24)
    assert verdict.open_rows == ["AUT-OPEN"]
    assert verdict.verdict != O.TERMINAL_STATE, (
        "the route's own resolved row produced a measurement and was not counted: " + verdict.why)


def test_a_re_plan_alone_never_resets_the_streak(ledger_repo):
    """`what` and `depends_on_evidence` are `stuck_clock.PROGRESS_FIELDS` and are demoted here. If
    either ever counts as improvement this detector can never fire, because an empty round ENDS in a
    re-plan by construction."""
    ledger_repo([_row()], 0)
    for i in range(1, 5):
        ledger_repo([_row(owner=f"CYC-000{i}", attempts=i, what=f"a completely new plan, take {i}",
                          depends_on_evidence=f"research/notes/{i}.md")], i)
    verdict, _, _ = _verdict(ledger_repo, now_hours=24)
    assert verdict.verdict == O.TERMINAL_STATE, verdict.why
    assert O.classify_measurement("what", "a", "b") == "not_measurement"
    assert O.classify_measurement("depends_on_evidence", "a", "b") == "not_measurement"


def test_deleting_the_evidence_is_not_an_improvement(ledger_repo):
    """⛔ A row cannot launder its own failure by EMPTYING a measurement field — the same asymmetry
    Rucio's `stuck_at` enforces, in the other module, for the other clock."""
    assert O.classify_measurement("outcome", "we measured it", None) == "not_measurement"
    assert O.classify_measurement("evidence_paths", ["a.json"], []) == "not_measurement"
    ledger_repo([_row(outcome="we measured it")], 0)
    for i in range(1, 5):
        ledger_repo([_row(owner=f"CYC-000{i}", attempts=i,
                          outcome="we measured it" if i < 4 else None)], i)
    verdict, _, _ = _verdict(ledger_repo, now_hours=24)
    assert verdict.verdict == O.TERMINAL_STATE, verdict.why


def test_a_field_nobody_classified_is_not_an_improvement_and_is_named(ledger_repo):
    """⛔ FAIL CLOSED ON SCHEMA DRIFT. Reading an unknown field as improvement would silently clear
    the streak and hide the terminal state; reading it as non-improvement at worst names a route a
    human then looks at. The report must carry the field's NAME so the drift is visible."""
    assert O.classify_measurement("some_field_invented_next_tuesday", None, "x") == "unclassified"
    ledger_repo([_row()], 0)
    for i in range(1, 5):
        ledger_repo([_row(owner=f"CYC-000{i}", attempts=i,
                          some_field_invented_next_tuesday=f"value {i}")], i)
    verdict, _, _ = _verdict(ledger_repo, now_hours=24)
    assert verdict.verdict == O.TERMINAL_STATE, verdict.why
    assert "some_field_invented_next_tuesday" in verdict.unclassified_fields


# ---------------------------------------------------------------------------------------------
# Counting attempts: what is a round, and when has it had its chance.
# ---------------------------------------------------------------------------------------------

def test_an_attempt_still_inside_its_lease_is_not_an_empty_round(ledger_repo):
    """⛔ THE CRY-WOLF GUARD. Work claimed twenty minutes ago has not failed to produce anything —
    it has not finished. Only attempts past one claim lease count."""
    _four_empty_attempts(ledger_repo)
    ledger_repo([_row(owner="CYC-0005", claimed_utc="2026-08-25T00:00:00Z", attempts=4,
                      what="attempt 5, in flight right now")], 20)
    verdict, _, _ = _verdict(ledger_repo, now_hours=22)   # 2 h into a claim, lease is 8 h
    assert verdict.empty_rounds == 4, (
        "the in-flight attempt was counted before its lease expired: " + verdict.why)
    later, _, _ = _verdict(ledger_repo, now_hours=30)     # 10 h in: the lease has expired
    assert later.empty_rounds == 5


def test_one_try_is_counted_once_however_it_is_committed(ledger_repo):
    """A claim and the `attempts` bump that ends it are ONE try. Counting the release separately
    would double every round and halve the threshold silently."""
    ledger_repo([_row()], 0)
    ledger_repo([_row(owner="CYC-0001", claimed_utc="2026-08-21T00:00:00Z")], 1)
    ledger_repo([_row(owner=None, attempts=1)], 2)
    verdict, _, _ = _verdict(ledger_repo, now_hours=40)
    assert verdict.empty_rounds == 1, verdict.why


def test_a_re_score_is_not_an_attempt(ledger_repo):
    """`score` moves on rows nobody looked at. It must not manufacture rounds — that would reach the
    threshold on a queue that merely re-ranked itself four times."""
    ledger_repo([_row()], 0)
    for i in range(1, 6):
        ledger_repo([_row(score=100.0 + i, score_inputs={"age_factor": i / 10})], i)
    verdict, _, _ = _verdict(ledger_repo, now_hours=40)
    assert verdict.empty_rounds == 0
    assert verdict.verdict == "not_attempted", verdict.why


# ---------------------------------------------------------------------------------------------
# The two clauses, separately.
# ---------------------------------------------------------------------------------------------

def test_the_wall_clock_clause_fires_without_four_rounds(ledger_repo):
    """⛔ C1 EXISTS BECAUSE C2 GOES BLIND WHEN ATTEMPTS STOP BEING RECORDED. One recorded try, then
    a very long time and no measurement: the event counter can never reach four, and the route is
    out of ideas anyway."""
    ledger_repo([_row()], 0)
    ledger_repo([_row(owner="CYC-0001", attempts=1)], 1)
    verdict, _, _ = _verdict(ledger_repo, now_hours=BUDGET_H + 10)
    assert verdict.verdict == O.TERMINAL_STATE, verdict.why
    assert verdict.clauses == {"c1_wall_clock": True, "c2_empty_rounds": False}, (
        "C1 must be able to fire ALONE, or the wall-clock half of Polybot's rule is decoration.")


def test_neither_clause_fires_on_a_route_that_keeps_measuring(ledger_repo):
    """The positive control. A route producing evidence on every attempt is never terminal, however
    long it runs — which is the half of §5 that forbids closing a route for being old."""
    ledger_repo([_row()], 0)
    for i in range(1, 9):
        ledger_repo([_row(owner=f"CYC-000{i}", attempts=i,
                          evidence_paths=[f"research/data/run-{j}.json" for j in range(i + 1)])], i)
    verdict, _, _ = _verdict(ledger_repo, now_hours=200)
    assert verdict.verdict == "has_ideas", verdict.why
    assert verdict.empty_rounds == 0
    assert not verdict.needs_attention


def test_the_budget_is_read_from_the_weights_file_and_never_typed(ledger_repo, tmp_path):
    """⛔ ONE FACT, ONE PLACE. C1's number lives in `priority-weights.json:age_saturates_days`. If a
    future edit hard-codes it here, re-tuning the weight silently stops moving this clause."""
    repo = tmp_path / "weighted"
    (repo / "research" / "autonomy").mkdir(parents=True)
    (repo / "research" / "autonomy" / "priority-weights.json").write_text(
        json.dumps({"age_saturates_days": {"value": 3.0}, "claim_lease": {"periods": 5}}),
        encoding="utf-8")
    assert O.budget_days(str(repo)) == 3.0, "the budget was not read from the weights file"
    assert O.lease_hours(str(repo)) == 5.0 * O.stuck_clock.cycle_interval_hours(
        str(repo / "research" / "autonomy" / "autonomy-state.json"))
    real = O.budget_days(O.REPO)
    assert real > 0 and O.budget_days(str(tmp_path / "nothing-here")) == O.FALLBACK_BUDGET_DAYS


def test_the_threshold_cannot_fire_before_a_rows_own_retry_budget_is_spent():
    """★ THE LOCAL BRACKET THAT PICKED 4 OVER ARIS'S NUMBER BEING MERELY CITED. Ledger rows carry
    `retry_budget: 3`; a terminal verdict at 3 would collide with the row's own retries."""
    budgets = {e.get("retry_budget") for e in json.load(
        open(os.path.join(O.REPO, "research", "autonomy", "research-ledger.json"),
             encoding="utf-8"))["entries"] if e.get("retry_budget") is not None}
    assert budgets, "no row carries a retry_budget — the bracket this threshold rests on is gone"
    assert O.EMPTY_ROUNDS_TO_HUMAN > max(budgets), (
        f"EMPTY_ROUNDS_TO_HUMAN={O.EMPTY_ROUNDS_TO_HUMAN} is not above the largest retry_budget "
        f"{max(budgets)}: the terminal verdict can now fire before a row has spent its own retries")


# ---------------------------------------------------------------------------------------------
# ⛔⛔ FAIL CLOSED. There must be no path from "could not measure" to "fine".
# ---------------------------------------------------------------------------------------------

def test_an_unmeasurable_route_is_not_fine(ledger_repo):
    """A censored history with no measurement inside it yields a LOWER BOUND below the budget, which
    decides nothing. That is `unmeasurable`, and `unmeasurable` needs attention."""
    ledger_repo([_row()], 0)
    ledger_repo([_row(owner="CYC-0001", attempts=1)], 1)
    versions = S.ledger_versions(str(ledger_repo.repo), LEDGER)
    histories = O.compute_histories(versions, shallow=True)
    now = T0 + datetime.timedelta(hours=40)
    verdict = O.route_verdict("RT-TEST", list(histories.values()), now, BUDGET_H, LEASE_H)
    assert verdict.verdict == "unmeasurable", verdict.why
    assert verdict.needs_attention, (
        "an unmeasurable route reported as not needing attention is the exact fail-open this "
        "module's docstring forbids")
    assert "unshallow" in verdict.why


def test_every_verdict_that_is_not_a_reading_needs_attention():
    """The fail-closed rule lives in ONE place — `RouteVerdict.needs_attention` — so a caller cannot
    re-decide it. Asserted over the whole closed set of verdicts."""
    for name in O.VERDICTS:
        verdict = O.RouteVerdict(route="RT-X", verdict=name, why="")
        assert verdict.needs_attention == (name in ("out_of_ideas", "unmeasurable")), name


def test_an_unreadable_history_never_reads_as_has_ideas(ledger_repo):
    """No committed versions at all -> `unmeasurable`, never a pass."""
    empty = O.route_verdict("RT-TEST", [O.RowHistory(entry_id="AUT-X", route="RT-TEST",
                                                     state="queued")],
                            T0, BUDGET_H, LEASE_H)
    assert empty.verdict == "unmeasurable", empty.why
    assert empty.needs_attention


def test_a_route_already_handed_to_a_human_is_not_escalated_twice(ledger_repo):
    """The escalation this condition recommends has already happened. Suppressed — and the
    suppression is REPORTED in `why`, not hidden."""
    ledger_repo([_row(requires_trimcrae=True)], 0)
    for i in range(1, 5):
        ledger_repo([_row(requires_trimcrae=True, owner=f"CYC-000{i}", attempts=i,
                          what=f"re-plan {i}")], i)
    verdict, _, _ = _verdict(ledger_repo, now_hours=24)
    assert verdict.verdict == "has_ideas"
    assert "requires_trimcrae" in verdict.why and "already happened" in verdict.why
    assert verdict.empty_rounds == O.EMPTY_ROUNDS_TO_HUMAN, (
        "the suppression must not also erase the count it suppressed — a reader has to be able to "
        "see what was refused")


def test_the_cli_exits_non_zero_on_a_terminal_route(ledger_repo, capsys):
    """The gate half: `--fail-on-terminal` must actually fail."""
    _four_empty_attempts(ledger_repo)
    code = O.main(["--check", "--json", "--repo", str(ledger_repo.repo), "--path", LEDGER,
                   "--fail-on-terminal"])
    payload = json.loads(capsys.readouterr().out)
    routes = {r["route"]: r for r in payload["routes"]}
    assert routes["RT-TEST"]["verdict"] in (O.TERMINAL_STATE, "unmeasurable")
    assert code == 1


def test_the_live_repository_reads_without_crashing():
    """A smoke test against the real ledger. It asserts no verdict — the point is that the module
    survives every field shape actually in the file, and that whatever it says, it says explicitly."""
    report = O.route_reports()
    assert report["routes"], "no routes read out of the live ledger"
    assert all(v.verdict in O.VERDICTS for v in report["routes"])
    assert all(v.why for v in report["routes"]), "a verdict with no stated reason is not a reading"
