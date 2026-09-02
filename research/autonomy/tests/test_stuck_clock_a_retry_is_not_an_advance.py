#!/usr/bin/env python3
"""THE ONE PROPERTY `stuck_clock.py` EXISTS FOR, ASSERTED RATHER THAN DESCRIBED.

⛔ THE THREAT MODEL IS NOT "the clock is off by an hour". It is that a stall detector can be talked
out of its own finding by the busiest possible row. Every write the loop makes to a stuck item —
claim it, expire the lease, bump `attempts`, re-score it, re-type `last_evidence_utc` — is a write,
and a detector that reads "was this row modified?" answers YES to all of them and reports the deadest
row in the ledger as the liveliest. That is the measured shape of AUT-PD-034 (a seat died on its
first message and held its item for 2 h 36 m while its status read `running`) and of the six stale
leases that made `continuity.py` report "5 workers AT CAPACITY" with one worker alive.

★ SO EVERY TEST HERE IS A CASE WHERE ACTIVITY MUST NOT BUY FRESHNESS. The invariant: `updated_at`
moves for anything; `stuck_at` moves only for a change that alters what is KNOWN about the work. A
future edit that lets a claim, a re-score, a retry or a re-typed date move `stuck_at` has rebuilt the
field this module was built to replace, and one of these tests will fail.

⚠ THE FIXTURES BUILD REAL GIT REPOSITORIES IN tmp_path, NOT MOCKS. Both clocks are DERIVED from
`git log` — mocking git out would leave the derivation itself untested, which is the only part that
could be wrong. Commit timestamps are forced through GIT_AUTHOR_DATE/GIT_COMMITTER_DATE so every
assertion here is about hours, deterministically.
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

import stuck_clock as S  # noqa: E402

#: ⛔⛔ THE THRESHOLD THESE FIXTURES ARE GRADED AGAINST, PINNED HERE RATHER THAN READ OFF THE LIVE
#: GOVERNOR. Every fixture below builds a row exactly 100 h old and then asserts terminal / not
#: terminal against it, so the verdicts are only meaningful relative to a KNOWN threshold — and
#: `stuck_clock.stuck_threshold_hours()` called with no argument reads
#: `research/autonomy/autonomy-state.json`, a file the budget governor moves.
#:
#: ⚠ MEASURED 2026-08-29, and it is the failure this constant exists to stop: a budget hold took
#: `cycle_interval_hours` from 4 to 24, the derived threshold went 24 h -> 144 h, and
#: `test_a_row_touched_forever_without_advancing_is_stuck` went red — a 100 h row is not terminal
#: against a 144 h bar. Nothing about the DETECTOR had changed. Worse, the three sibling assertions
#: that read `is None` would have gone the other way and passed MORE easily at every widening, which
#: is the silent direction: a unit test that gets weaker when a config file moves is not testing the
#: unit.
#:
#: ⛔ 24.0 IS THE TIGHTEST THRESHOLD THIS REPOSITORY HAS RUN (6 cycles x the 4 h cadence), so pinning
#: it here makes all four assertions bind harder than reading the live file ever did.
#: ⛔ AND THE GOVERNOR-READING CONTRACT IS NOT WEAKENED BY THIS, IT IS JUST TESTED WHERE IT BELONGS:
#: `test_the_threshold_is_read_from_the_governor_not_typed` owns it, passes its own `state_path`, is
#: hermetic already, and is deliberately left untouched. It is also the test that ARGUES the
#: threshold SHOULD widen with the cadence — "a hard-coded 24 would silently stop tracking a loop
#: that moved to an 8 h cadence under backoff" — so this constant must never be pushed back into
#: `stuck_clock.py` as a cap.
THRESHOLD_H = 24.0

T0 = datetime.datetime(2026, 8, 20, 12, 0, tzinfo=datetime.timezone.utc)
LEDGER = "ledger.json"


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
    base = {"id": "AUT-X", "state": "queued", "owner": None, "claimed_utc": None,
            "attempts": 0, "score": 100.0, "what": "do the thing", "blocked_by": None,
            "blocked_evidence": None, "last_evidence_utc": "2026-08-20"}
    base.update(kw)
    return base


def _clocks(commit_fixture, now_hours=100):
    versions = S.ledger_versions(str(commit_fixture.repo), LEDGER)
    clocks = S.compute_clocks(versions)
    return clocks, T0 + datetime.timedelta(hours=now_hours)


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE NEGATIVE CONTROL. This is the whole point of the module: maximal activity, zero advance.
# ---------------------------------------------------------------------------------------------

def test_a_row_touched_forever_without_advancing_is_stuck(ledger_repo):
    """⛔⛔ THE BUG THIS REPLACES, VERBATIM. Ten commits, each a real write to the row — claimed,
    lease expired, retried, re-scored, evidence date re-typed — and not one of them says anything new
    about the work. `updated_at` reaches the last commit; `stuck_at` must not have moved off the
    first. A detector that reads only the first clock calls this row the freshest in the ledger.
    """
    ledger_repo([_row()], 0)
    for i in range(1, 10):
        ledger_repo([_row(owner=f"seat-{i}" if i % 2 else None,
                          claimed_utc=f"2026-08-2{i % 9}T00:00:00Z",
                          attempts=i,
                          score=100.0 + i,
                          last_evidence_utc=f"2026-08-2{i % 9}")], i)

    clocks, now = _clocks(ledger_repo)
    clock = clocks["AUT-X"]
    assert clock.updated_at == T0 + datetime.timedelta(hours=9), (
        "the touch clock did not follow the last write — then it is not a touch clock")
    assert clock.stuck_at == T0, (
        "nine claims, retries and re-scores moved the ADVANCE clock. That is the failure the module "
        "exists to detect, rebuilt inside the module.")
    assert clock.stuck_hours(now) == pytest.approx(100.0)
    verdict = clock.terminal(now, THRESHOLD_H)
    assert verdict and verdict["state"] == S.TERMINAL_STATE, (
        "a row untouched by progress for 100 h was not declared terminal")
    assert verdict["since_utc"].startswith("2026-08-21"), (
        "the terminal verdict is not dated from when the threshold was crossed, so it reads as an "
        "opinion rather than an observation")


# ---------------------------------------------------------------------------------------------
# The positive control. Without it the suite would pass on a module that calls everything stuck.
# ---------------------------------------------------------------------------------------------

def test_a_row_that_genuinely_advanced_is_not_stuck(ledger_repo):
    """★ THE POSITIVE CONTROL. Same shape, same noise, but one commit records a real finding — the
    evidence behind a block. Both clocks must land on it and the row must not be terminal."""
    ledger_repo([_row()], 0)
    ledger_repo([_row(owner="seat-1", claimed_utc="2026-08-20T13:00:00Z")], 1)
    ledger_repo([_row(owner="seat-1", claimed_utc="2026-08-20T13:00:00Z",
                      blocked_evidence="the GEO series has no matched normals; measured, not "
                                       "assumed")], 98)

    clocks, now = _clocks(ledger_repo)
    clock = clocks["AUT-X"]
    assert clock.stuck_at == T0 + datetime.timedelta(hours=98), (
        "recording block evidence did not count as an advance. CLAUDE.md §0: producing the evidence "
        "IS the work, and priority.py already stands the item down for it")
    assert clock.updated_at == clock.stuck_at
    assert clock.stuck_hours(now) == pytest.approx(2.0)
    assert clock.terminal(now, THRESHOLD_H) is None, (
        "a row that advanced two hours ago was declared stalled")


@pytest.mark.parametrize("field,value", [
    ("what", "✅ DONE — the sweep found three junctions"),
    ("blocked_by", ["AUT-999"]),
    ("blocked_evidence", "measured: the workflow writes to a branch main never sees"),
    ("depends_on_evidence", "patch sha256 3cd4c8a5…"),
    ("requires_trimcrae", True),
    ("prerequisite_of", "AUT-PROP-002"),
])
def test_each_progress_field_moves_the_advance_clock(ledger_repo, field, value):
    """★ THE OTHER HALF OF THE POSITIVE CONTROL, ONE FIELD AT A TIME. A suite that only ever
    exercises one progress field measures nothing about the rest of the set — the defect found by
    mutation on `continuity.OPEN_STATES` and pinned in that file."""
    ledger_repo([_row()], 0)
    ledger_repo([_row(**{field: value})], 50)
    clocks, now = _clocks(ledger_repo)
    assert clocks["AUT-X"].stuck_at == T0 + datetime.timedelta(hours=50), (
        f"a change to {field!r} did not count as progress")


# ---------------------------------------------------------------------------------------------
# ⛔ A RE-SCORE AND A RE-CLAIM. Named in AUT-PROP-029 as the two that must never clear the clock.
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("field,value,why", [
    ("score", 187.5, "a re-score is arithmetic over systems/graph; nobody looked at the work"),
    ("score_inputs", {"live": 1}, "the same, one level down — re-derived on every --write"),
    ("_score_basis", "inherited from AUT-PROP-002", "prose about the arithmetic, not about the work"),
    ("owner", "CYC-0031-abcd", "a claim is a LEASE, not work — AUT-PD-034 held one for 2 h 36 m"),
    ("claimed_utc", "2026-08-21T09:00:00Z", "the timestamp of that lease, not of any finding"),
    ("attempts", 3, "the retry counter; Rucio's whole rule is that a retry leaves stuck_at alone"),
    ("last_evidence_utc", "2026-08-28", "the SELF-TYPED field this module replaces"),
    ("lease_released", "claim by CYC-0031 released after 8.1 h", "bookkeeping about an expiry"),
    ("cost_class", "cheap", "re-derived from the graph"),
])
def test_touching_a_row_does_not_clear_the_clock(ledger_repo, field, value, why):
    """⛔ ONE ROW PER FIELD, BECAUSE THE FAILURE IS PER FIELD. Each of these is a real write the loop
    makes to rows nobody is advancing. Any one of them moving `stuck_at` restores the exact defect:
    a stalled session can clear the alarm on itself by doing bookkeeping.
    """
    ledger_repo([_row()], 0)
    ledger_repo([_row(**{field: value})], 50)
    clocks, now = _clocks(ledger_repo)
    clock = clocks["AUT-X"]
    assert clock.updated_at == T0 + datetime.timedelta(hours=50), (
        f"{field} changed and the TOUCH clock did not move — the row would read as never modified")
    assert clock.stuck_at == T0, f"{field} cleared the advance clock: {why}"


def test_the_busy_retry_loop_is_the_case_the_brief_got_wrong(ledger_repo):
    """⛔⛔ PINNED DELIBERATELY, BECAUSE AUT-PROP-029 LISTS `attempts` AS A CANDIDATE FOR PROGRESS
    AND IT IS THE ONE FIELD THAT MOST CERTAINLY IS NOT.

    `priority.py:release_stale_claims` increments `attempts` every time a lease expires. If that
    counted as an advance, a row would look healthier in exact proportion to how often the automation
    failed on it — the busy retry loop that Rucio's `stuck_at` exists to unmask, reproduced. Six
    failed attempts here must leave the clock exactly where it started.
    """
    ledger_repo([_row()], 0)
    for i in range(1, 7):
        ledger_repo([_row(attempts=i, state="in_progress" if i % 2 else "queued",
                          owner=f"seat-{i}" if i % 2 else None)], i * 4)
    clocks, now = _clocks(ledger_repo)
    assert clocks["AUT-X"].stuck_at == T0
    assert S.classify_change("attempts", 1, 2) == "touch", (
        "`attempts` was reclassified as progress. Read the module docstring before changing this: "
        "it is the retry counter, and crediting it inverts the detector.")
    assert clocks["AUT-X"].tried is True, (
        "six recorded attempts did not mark the row as TRIED — then the terminal state would never "
        "fire on the rows automation actually worked on")


@pytest.mark.parametrize("before,after,expected", [
    ("queued", "in_progress", "touch"),
    ("in_progress", "queued", "touch"),
    ("queued", "running", "touch"),
    ("queued", "done", "progress"),
    ("in_progress", "blocked", "progress"),
    ("queued", "abandoned", "progress"),
    ("queued", "superseded", "progress"),
])
def test_only_a_resolution_state_counts(before, after, expected):
    """⛔ `queued -> in_progress` IS A CLAIM WEARING A STATE FIELD, and `in_progress -> queued` is a
    lease expiring. A row can oscillate between them all week without anybody learning anything, and
    on this ledger it has: AUT-PROP-012 went queued -> in_progress -> queued while its holder was
    dead. Only entry to a state that RESOLVES something is an advance."""
    assert S.classify_change("state", before, after) == expected


# ---------------------------------------------------------------------------------------------
# The terminal state, and the two ways it must refuse to fire.
# ---------------------------------------------------------------------------------------------

def test_a_row_nobody_ever_tried_is_starved_not_stalled(ledger_repo):
    """⛔ THE CRY-WOLF GUARD. The queue holds ~100 open rows and the loop takes one per cycle, so
    most rows are old simply because nothing has reached them. Declaring them all
    `stalled_needs_human` would produce exactly the flood this repository has already paid for —
    1,476 commits from a supervisor with nothing to supervise, and every alarm after it muted.
    Terminal means AUTOMATION TRIED AND STOPPED, so it requires a recorded attempt or a claim.
    """
    ledger_repo([_row()], 0)
    clocks, now = _clocks(ledger_repo)
    clock = clocks["AUT-X"]
    assert clock.tried is False
    assert clock.stuck_hours(now) == pytest.approx(100.0)
    assert clock.terminal(now, THRESHOLD_H) is None, (
        "a row nothing has ever attempted was declared terminal")


def test_a_finished_row_has_no_stall_clock(ledger_repo):
    ledger_repo([_row(owner="seat-1", attempts=1)], 0)
    ledger_repo([_row(state="done", what="✅ DONE", owner=None, attempts=1)], 1)
    clocks, now = _clocks(ledger_repo)
    assert clocks["AUT-X"].is_open() is False
    assert clocks["AUT-X"].terminal(now, THRESHOLD_H) is None


def test_the_threshold_is_read_from_the_governor_not_typed(tmp_path):
    """📏 CLAUDE.md §1, one fact one place. The cycle interval belongs to `autonomy-state.json`; this
    module multiplies it and states the multiplier. A hard-coded 24 would silently stop tracking a
    loop that moved to an 8 h cadence under backoff — the exact moment stall detection matters most.
    """
    state = tmp_path / "autonomy-state.json"
    state.write_text(json.dumps({"cycle_interval_hours": 8}), encoding="utf-8")
    assert S.stuck_threshold_hours(str(state)) == 8 * S.STUCK_AFTER_CYCLES
    missing = tmp_path / "gone.json"
    assert S.stuck_threshold_hours(str(missing)) == (
        S.FALLBACK_CYCLE_INTERVAL_HOURS * S.STUCK_AFTER_CYCLES), (
        "an unreadable governor file must fall back to the documented interval, not to zero — a "
        "zero threshold declares the entire queue terminal")


# ---------------------------------------------------------------------------------------------
# ⛔ THE HISTORY HORIZON. A lower bound is not a measurement, and this repository is a shallow clone.
# ---------------------------------------------------------------------------------------------

def _versions(*specs):
    return [S.Version(sha=f"sha{i}", when=T0 + datetime.timedelta(hours=h), rows={r["id"]: r for r in rows})
            for i, (h, rows) in enumerate(specs)]


def test_a_row_at_the_shallow_horizon_is_a_lower_bound_not_a_number():
    """⛔⛔ MEASURED IN THIS WORKTREE: `git rev-parse --is-shallow-repository` is true, 206 commits,
    all one day old, and the oldest one LOOKS like the commit that created the ledger. Every row
    present in it may be far older than git can say. Reporting that horizon age as the stall age
    would be a populated field that is not a measured one (CLAUDE.md §4) — and it would understate,
    which is the silent direction.
    """
    versions = _versions((0, [_row(owner="seat-1", attempts=1)]))
    deep = S.compute_clocks(versions, shallow=False)["AUT-X"]
    shallow = S.compute_clocks(versions, shallow=True)["AUT-X"]
    assert deep.censored is False and shallow.censored is True

    now = T0 + datetime.timedelta(hours=100)
    horizon = T0
    assert deep.terminal(now, 24.0, horizon) is not None
    assert shallow.terminal(now, 24.0, horizon) is not None, (
        "a censored row whose LOWER BOUND already exceeds the threshold was not declared. The bound "
        "is conclusive in that direction — refusing there loses every genuinely old row")

    near = T0 + datetime.timedelta(hours=12)
    assert shallow.terminal(near, 24.0, horizon) is None, (
        "a censored row was declared terminal on 12 h of visible history against a 24 h threshold — "
        "that is a verdict on data git does not have")
    assert shallow.terminal(near, 24.0, None) is None, (
        "with no readable horizon the censored row must not be judged at all")


def test_a_censored_row_whose_bound_predates_the_horizon_gets_no_verdict():
    """⛔⛔ WRITTEN BECAUSE A MUTATION SURVIVED, AND THE SURVIVOR WAS RIGHT (M5, 2026-08-28).

    The first version of `terminal()` re-compared the HORIZON'S age against the threshold for every
    censored row. Deleting that comparison outright left all 38 tests green — because
    `compute_clocks` stamps a censored row's `stuck_at` from the horizon, so the two ages are the
    same number and the second check could never fire. Dead code in the one branch that decides
    whether a verdict may be issued at all.

    ★ What the horizon is genuinely needed for is the INVARIANT: a censored row's bound must BE the
    horizon. A future censoring rule that marks a row whose `stuck_at` is older than the horizon
    hands this function a bound it never reasoned about, and it must refuse rather than issue a
    verdict on it. Same for a horizon it cannot read.
    """
    inconsistent = S.Clocks(entry_id="AUT-X", state="queued", tried=True, censored=True,
                            stuck_at=T0 - datetime.timedelta(hours=10),
                            updated_at=T0, created_at=T0 - datetime.timedelta(hours=10))
    now = T0 + datetime.timedelta(hours=100)
    assert inconsistent.terminal(now, 24.0, T0) is None, (
        "a censored row whose bound predates the horizon was judged anyway — the bound is not the "
        "one the censoring reasoning rests on")
    assert inconsistent.terminal(now, 24.0, None) is None
    consistent = S.Clocks(entry_id="AUT-X", state="queued", tried=True, censored=True,
                          stuck_at=T0, updated_at=T0, created_at=T0)
    assert consistent.terminal(now, 24.0, T0) is not None, (
        "the positive control: a well-formed censored bound past the threshold IS conclusive, and "
        "refusing there would lose every genuinely old row")


def test_an_advance_inside_the_window_is_exact_again():
    """★ THE RECOVERY PATH. Censoring is a property of NOT HAVING SEEN the advance. The moment one is
    observed inside the window the row is exactly measured, and must stop being flagged as a bound."""
    versions = _versions((0, [_row()]), (10, [_row(what="found the junction")]))
    clock = S.compute_clocks(versions, shallow=True)["AUT-X"]
    assert clock.censored is False
    assert clock.stuck_at == T0 + datetime.timedelta(hours=10)


# ---------------------------------------------------------------------------------------------
# Schema drift. The ledger grew three new fields in a single day.
# ---------------------------------------------------------------------------------------------

def test_a_field_this_module_has_never_seen_is_named_and_buys_nothing(ledger_repo):
    """⛔ THE ASYMMETRY, ASSERTED. An unknown field defaulting to PROGRESS would clear the clock
    silently and hide the stall; defaulting to TOUCH at worst names a row somebody looks at. The
    ledger grew `_contested`, `_block_cleared` and `_lease_released` in one day, so this is not
    hypothetical drift.
    """
    ledger_repo([_row()], 0)
    ledger_repo([_row(_freshly_invented_field="whatever a future session decides to record")], 50)
    clocks, now = _clocks(ledger_repo)
    clock = clocks["AUT-X"]
    assert clock.stuck_at == T0, "an unrecognised field cleared the advance clock"
    assert "_freshly_invented_field" in clock.unclassified_fields, (
        "the unknown field was swallowed. Then the split rots invisibly, which is how the reader and "
        "the writer drifted apart in AUT-PD-013")
    assert S.classify_change("_freshly_invented_field", None, 1) == "unclassified", (
        "unclassified was folded into touch at the classifier level, so nothing can report drift")


def test_a_row_that_vanishes_and_returns_unchanged_keeps_its_clock(ledger_repo):
    """⚠ A committed version can be missing a row — a concurrent regeneration, a mid-rebase file,
    a half-written ledger. Treating the return as a creation would reset the clock on exactly the
    rows a chaotic day touched most, which is the silent direction again."""
    ledger_repo([_row(id="AUT-X"), _row(id="AUT-Y")], 0)
    ledger_repo([_row(id="AUT-Y")], 10)
    ledger_repo([_row(id="AUT-X"), _row(id="AUT-Y")], 20)
    clocks, now = _clocks(ledger_repo)
    assert clocks["AUT-X"].stuck_at == T0, (
        "a row that disappeared for one commit and came back identical had its clock reset")


def test_repointing_a_row_at_another_route_is_flagged_as_an_identity_change(ledger_repo):
    """⛔ AUT-PROP-014 AND AUT-PROP-015 EACH NAMED TWO DIFFERENT ROUTES OVER THIS LEDGER'S HISTORY —
    the id-collision incidents `ids.py` was built for. Both clocks key on the id, so a row that
    changes what it is about must say so; otherwise one item's history silently vouches for another.
    """
    ledger_repo([_row(serves={"route": "RT-ASO"})], 0)
    ledger_repo([_row(serves={"route": "RT-ATR-ASSESS"})], 50)
    clocks, now = _clocks(ledger_repo)
    clock = clocks["AUT-X"]
    assert clock.identity_changed is True
    assert clock.stuck_at == T0 + datetime.timedelta(hours=50), (
        "re-pointing a row at a different route is a decision somebody made; it is not bookkeeping")


def test_a_publication_field_change_alone_is_not_a_route_change(ledger_repo):
    """⚠ The other direction, and it costs a false alarm if wrong: `serves` is re-derived from the
    graph, so its publication/strategy members move without anybody touching the work."""
    ledger_repo([_row(serves={"route": "RT-ASO", "publication": None})], 0)
    ledger_repo([_row(serves={"route": "RT-ASO", "publication": "PUB-ASO"})], 50)
    clocks, now = _clocks(ledger_repo)
    assert clocks["AUT-X"].identity_changed is False
    assert clocks["AUT-X"].stuck_at == T0


# ---------------------------------------------------------------------------------------------
# The derivation itself.
# ---------------------------------------------------------------------------------------------

def test_both_clocks_come_from_git_and_nothing_is_written_back(ledger_repo):
    """⛔⛔ THE DESIGN CONSTRAINT, GUARDED. The ledger already HAS a self-reported progress field —
    `last_evidence_utc`, typed by whoever edits the row. If `stuck_at` became another such field, a
    stalled session could clear its own alarm by typing a date. Two things must stay true: the field
    is classified as TOUCH, and this module never writes to the ledger at all.
    """
    assert "last_evidence_utc" in S.TOUCH_FIELDS
    assert "last_evidence_utc" not in S.PROGRESS_FIELDS
    source = open(os.path.join(os.path.dirname(HERE), "stuck_clock.py"), encoding="utf-8").read()
    for forbidden in ('"w"', "'w'", "json.dump(", "write_text("):
        assert forbidden not in source, (
            f"stuck_clock.py contains {forbidden} — this module derives, it does not record. A "
            "stuck clock that can be written is the field it replaced")

    ledger_repo([_row()], 0)
    before = (ledger_repo.repo / LEDGER).read_text(encoding="utf-8")
    S.open_row_clocks(repo=str(ledger_repo.repo), path=LEDGER)
    assert (ledger_repo.repo / LEDGER).read_text(encoding="utf-8") == before


def test_an_unparseable_version_is_skipped_not_read_as_an_empty_ledger(ledger_repo):
    """⚠ FAIL TOWARD PRESERVING THE STALL. A half-written commit that parses as no entries would look
    like every row being deleted and re-created, resetting every clock in the ledger at once."""
    ledger_repo([_row()], 0)
    (ledger_repo.repo / LEDGER).write_text("{not json at all", encoding="utf-8")
    _run(ledger_repo.repo, "add", LEDGER, when=T0 + datetime.timedelta(hours=5))
    _run(ledger_repo.repo, "commit", "-q", "-m", "broken", when=T0 + datetime.timedelta(hours=5))
    ledger_repo([_row()], 10)

    versions = S.ledger_versions(str(ledger_repo.repo), LEDGER)
    assert len(versions) == 2, "the unparseable version was not skipped"
    clocks = S.compute_clocks(versions)
    assert clocks["AUT-X"].stuck_at == T0


def test_the_report_sorts_by_how_long_a_row_has_been_stuck(ledger_repo, capsys):
    """The CLI contract AUT-PROP-029 asks for: rows ordered by how long they have been stuck, with
    the touch clock beside the advance clock so the gap between them is readable."""
    ledger_repo([_row(id="OLD", owner="s", attempts=1), _row(id="NEW", owner="s", attempts=1)], 0)
    ledger_repo([_row(id="OLD", owner="s", attempts=2),
                 _row(id="NEW", owner="s", attempts=1, what="advanced")], 50)

    report = S.open_row_clocks(repo=str(ledger_repo.repo), path=LEDGER,
                               now=T0 + datetime.timedelta(hours=60))
    assert [c.entry_id for c in report["rows"]] == ["OLD", "NEW"]
    assert S.main(["--check", "--repo", str(ledger_repo.repo), "--path", LEDGER]) == 0
    out = capsys.readouterr().out
    assert "OLD" in out and "NEW" in out
    assert out.index("OLD") < out.index("NEW"), "the report is not sorted longest-stuck first"


def test_the_report_prints_the_terminal_verdict_with_its_date(ledger_repo, capsys):
    """⛔ THE ONE BRANCH OF THE REPORT THAT MATTERS, AND NOTHING REACHED IT UNTIL THIS TEST.

    Every other CLI test above ends with no terminal row, so the whole rendering path for a verdict —
    the flag, its date, the count line and the non-zero exit — was written and never executed. That
    is the shape this repository has paid for three times over: the selector's own contract, the
    loop's instruments, and `subagent_width`, each a guard that ran nowhere. A stall report that
    crashes or prints nothing on the first genuinely stuck row is worse than no report.

    ⚠ THE DATE IS PART OF THE ASSERTION. AUT-PROP-029 asks for a terminal state that is "dated and
    explicit" precisely so it cannot be confused with a row quietly reading UNKNOWN.
    """
    ledger_repo([_row(id="AUT-STUCK", owner="seat-1", attempts=1)], 0)
    ledger_repo([_row(id="AUT-STUCK", owner=None, attempts=2)], 1)

    assert S.main(["--check", "--repo", str(ledger_repo.repo), "--path", LEDGER]) == 0, (
        "--check reports; it does not gate. Only --fail-on-terminal may exit non-zero")
    out = capsys.readouterr().out
    assert S.TERMINAL_STATE in out and "since 2026-08-21" in out, (
        "the terminal row printed without naming the state or the date it crossed the threshold")
    assert f"1 {S.TERMINAL_STATE}" in out, "the count line did not report the terminal row"

    assert S.main(["--check", "--repo", str(ledger_repo.repo), "--path", LEDGER,
                   "--fail-on-terminal"]) == 1, (
        "--fail-on-terminal did not exit 1 on a terminal row, so no caller could ever gate on it")
    capsys.readouterr()
    assert S.main(["--check", "--json", "--repo", str(ledger_repo.repo), "--path", LEDGER,
                   "--fail-on-terminal"]) == 1
    payload = json.loads(capsys.readouterr().out)
    verdict = payload["rows"][0]["terminal"]
    assert verdict["state"] == S.TERMINAL_STATE and verdict["since_utc"].startswith("2026-08-21")
    assert "attempt" in verdict["why"], (
        "the machine-readable verdict does not say what it is a verdict about")


def test_the_empty_report_does_not_read_as_a_green_tick(ledger_repo, capsys):
    """★ THE SAME PROPERTY `continuity.py` v2 EXISTS FOR. 'No row is terminal' is a reading, and on a
    shallow clone it can mean 'git cannot see far enough back'. It must never be phrased as approval.
    """
    ledger_repo([_row(what="fresh")], 0)
    S.main(["--check", "--repo", str(ledger_repo.repo), "--path", LEDGER])
    out = capsys.readouterr().out
    assert "✅" not in out and "all clear" not in out
    assert "a reading, not a green tick" in out


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE VERDICT MUST STATE THE EVIDENCE IT WAS GATED ON, NOT A DIFFERENT FIELD (2026-09-02).
#
# `Clocks.terminal` refuses a verdict on `not self.tried` and never reads `attempts`. For three
# months the sentence it printed named ONLY `attempts`, so a row two seats had claimed and released
# without advancing rendered as "despite 0 recorded attempt(s)" — which reads as *nobody tried*,
# the exact reading the `tried` gate exists to refuse.
#
# ⚠ MEASURED, not hypothesised. AUT-011, AUT-007, AUT-008, AUT-045 and AUT-016 were claimed by
# SEAT-s4-ba841eee / SEAT-s5-ba841eee at 2026-08-28 22:44–22:45 UTC and released with `owner: null`
# at 23:59:53 having advanced nothing; `attempts` stayed 0 because only a LEASE EXPIRY bumps it
# (priority-weights.json `claim_lease.periods` = 2), not a clean claim-and-release. Receipt
# CYC-0091-1a2c0a85 recorded the resulting confusion verbatim — "each queued, 0 recorded attempts
# ... despite being marked `tried`" — and a later reader took those rows as evidence that this
# module MANUFACTURES human-blocked rows out of untouched ones. It does not: the classification was
# correct and only the sentence was wrong.
# ---------------------------------------------------------------------------------------------

def test_a_row_tried_only_by_a_claim_does_not_render_as_untried():
    """⛔ THE REGRESSION, STATED AS THE STRING A READER ACTUALLY SEES.

    A row claimed once and released clean is `tried` with `attempts == 0`. The verdict must say a
    seat took it. It must NOT contain a phrase that reads as nobody having tried.
    """
    claimed = _row(owner="SEAT-s5", state="in_progress")
    released = _row(owner=None, state="queued")
    clocks = S.compute_clocks(_versions((0, [_row()]), (1, [claimed]), (2, [released])))
    clock = clocks["AUT-X"]
    assert clock.tried is True and clock.attempts == 0, (
        "fixture drift: this test is only meaningful for a row that is tried with zero attempts")
    assert clock.claims == 1, "a claim edge was not counted"

    verdict = clock.terminal(T0 + datetime.timedelta(hours=200), threshold_h=24.0)
    assert verdict is not None, "a tried row past the threshold must still be terminal"
    why = verdict["why"]
    assert "0 recorded attempt" not in why, (
        "the verdict says '0 recorded attempt(s)' about a row it declared terminal BECAUSE it was "
        "tried — the one field `terminal()` does not gate on, printed as if it were the reason:\n"
        f"  {why}")
    assert "claim(s) by an automated seat" in why, (
        f"the verdict does not name the evidence it was actually gated on:\n  {why}")


def test_a_claim_is_counted_once_per_claim_and_not_once_per_commit():
    """⛔ AN EDGE, NOT A LEVEL. `owner` stays set for a whole lease, so counting the level would
    report one claim as many and turn a re-scored row into a busy one."""
    held = _row(owner="SEAT-s5", state="in_progress")
    clocks = S.compute_clocks(_versions(
        (0, [_row()]), (1, [held]), (2, [held]), (3, [held]),
        (4, [_row(owner=None)]), (5, [_row(owner="SEAT-s9", state="in_progress")])))
    assert clocks["AUT-X"].claims == 2, (
        "two distinct claims spanning five commits must count 2, not the number of commits they span")


def test_a_retried_row_still_reports_its_retries():
    """★ THE FIX MUST NOT DROP INFORMATION. A retry count is real; it simply stopped being the only
    thing printed."""
    clocks = S.compute_clocks(_versions((0, [_row()]), (1, [_row(attempts=3)])))
    verdict = clocks["AUT-X"].terminal(T0 + datetime.timedelta(hours=200), threshold_h=24.0)
    assert "3 recorded attempt(s)" in verdict["why"], verdict["why"]


def test_no_terminal_verdict_anywhere_can_read_as_untried():
    """⛔ THE CLASS, ASSERTED SEPARATELY FROM THE INSTANCE (`paper-hardening`'s one-of-a-pair rule).
    Whatever combination of claims and attempts produced a verdict, the sentence may never contain a
    zero count as its whole justification."""
    for claims, attempts in ((1, 0), (0, 1), (2, 3), (5, 0), (0, 9)):
        phrase = S._tried_via(claims, attempts)
        assert "0 " not in phrase and phrase, (
            f"claims={claims} attempts={attempts} rendered a zero count: {phrase!r}")
    fallback = S._tried_via(0, 0)
    assert "should not have been declared terminal" in fallback, (
        "an untried row is unreachable through terminal(), but if a future edit lets one through "
        "the message must say so rather than invent a count")


def test_a_row_already_held_in_the_oldest_visible_version_counts_that_claim():
    """⛔ THE MUTATION THAT SURVIVED THE FIRST PASS (M3, 2026-09-02), AND IT IS THE SHALLOW-CLONE CASE.

    `compute_clocks` seeds a row the first time it appears. On a shallow clone that first appearance
    is the horizon, and a row can already be HELD there — the claim that reached it happened before
    git can see. Seeding `claims=0` in that branch loses it silently, and the row then renders as
    though only its retries had ever touched it, which is the same false reading in a rarer shape.
    Every other test here starts from an unclaimed row, so none of them covers this line.
    """
    clocks = S.compute_clocks(_versions(
        (0, [_row(owner="SEAT-held-at-horizon", state="in_progress")]),
        (1, [_row(owner=None)])), shallow=True)
    clock = clocks["AUT-X"]
    assert clock.tried is True and clock.attempts == 0
    assert clock.claims == 1, (
        "a row already held in the oldest version git can see was seeded with no claim, so its "
        "verdict would name no evidence at all")
