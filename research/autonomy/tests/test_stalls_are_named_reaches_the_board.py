#!/usr/bin/env python3
"""AUT-PROP-029, THE WIRING HALF. `stuck_clock.py`'s two-clock stall model was fully built and fully
tested (`test_stuck_clock_a_retry_is_not_an_advance.py`) with NOTHING calling it: no `health.py` board
condition read it, `handoff.py`'s ready-work selector did not exclude a terminal row, and no scheduled
job ever ran `--check`. A row could compute as `stalled_needs_human` today and the only way anyone
would see that is running the CLI by hand — the exact "an unrun ranker is not a ranker" shape AUT-PD-018
already cost this repository once.

This file guards the THREE surfaces that close that gap:
  1. `health.py`'s new `stalls_are_named` condition, which reports a caller-supplied stall verdict
     (health.py has no subprocess by design, so it cannot compute one itself — same shape as
     `gates_green`).
  2. `handoff.py`'s `terminal_ids()`/`top_items(..., exclude_ids=...)`, which keeps a terminal row out
     of what is HANDED to a successor session, without ever touching the ledger or the row's `state`.
  3. The wiring itself is present: `stalls_are_named` is in `CONDITION_ORDER`, reaches `build()`, has
     a declared `CONDITION_ON_RED`, and `health.py --stall-verdict` is a real CLI flag.

⚠ NEITHER `c_stalls_are_named` NOR `terminal_ids()` MAY BE ABLE TO WRITE THE LEDGER OR
`stalled_needs_human` INTO IT. That verdict is COMPUTED, never stored (`stuck_clock.py`'s own design
constraint) — this file never calls `apply_claim`, `ledger_io.write_ledger`, or opens the ledger for
writing, and asserts that a passing run leaves it untouched.
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)

import health as H          # noqa: E402
import handoff as HF        # noqa: E402
import stuck_clock as S     # noqa: E402

T0 = datetime.datetime(2026, 8, 20, 12, 0, tzinfo=datetime.timezone.utc)


# ══════════════════════════════════════════════════════ health.py: c_stalls_are_named, in isolation
def test_no_verdict_supplied_is_unmeasured_not_green():
    """The headline property this whole file exists for, applied to the new row: health.py has no
    subprocess, so with nothing supplied it must say IT DID NOT LOOK — never that nothing is stuck."""
    row = H.c_stalls_are_named(None, "no file")
    assert row["unmeasured"] is True and row["ok"] is False
    assert row["verdict"] == "NO-STALL-VERDICT"
    assert "--stall-verdict" in row["detail"], (
        "the detail must name the flag that settles it, or it is a question in a status's costume")


def test_a_malformed_verdict_is_unmeasured_not_green():
    """A file that parsed as JSON but carries no `rows` list is not a reading either — it is a
    different failure from 'absent', and both must land on the unmeasured side of the line."""
    row = H.c_stalls_are_named({"generated_utc": "2026-08-28T00:00:00Z"}, None)
    assert row["unmeasured"] is True
    assert row["verdict"] == "STALL-VERDICT-UNREADABLE"


def _stall(rows, shallow=False):
    return {"terminal_state": "stalled_needs_human", "shallow_clone": shallow,
            "history_horizon_utc": "2026-08-27 00:00", "rows": rows}


def test_zero_terminal_rows_is_green_and_names_the_count():
    stall = _stall([{"id": "AUT-1", "terminal": None}, {"id": "AUT-2", "terminal": None}])
    row = H.c_stalls_are_named(stall, None)
    assert row["ok"] is True and row["verdict"] == "NO-STALLED-ROWS"
    assert row["payload"]["open_rows"] == 2
    assert row["payload"].get("terminal_ids") is None, (
        "an all-None payload value is dropped by _row()'s own filter, so its absence here IS the "
        "expected shape — not a sign the field was never computed"
    )


def test_a_terminal_row_turns_it_red_and_names_the_row():
    """⛔⛔ THE POSITIVE CONTROL. Without this the whole condition could report NO-STALLED-ROWS on
    every board ever built and nothing here would catch it."""
    stall = _stall([
        {"id": "AUT-1", "terminal": None},
        {"id": "AUT-STUCK", "terminal": {"state": "stalled_needs_human", "since_utc": "2026-08-21T00:00:00Z",
                                         "why": "no substantive change in 100 h despite 3 attempt(s)."}},
    ])
    row = H.c_stalls_are_named(stall, None)
    assert row["needs_attention"] is True and row["unmeasured"] is False
    assert row["verdict"] == "STALLED-ROWS"
    assert "AUT-STUCK" in row["detail"] and "2026-08-21" in row["detail"]
    assert row["payload"]["terminal_ids"] == ["AUT-STUCK"]


def test_a_shallow_clone_note_is_carried_in_both_directions():
    """⚠ A shallow clone's absence of a terminal row is a censored reading, not a clean one — the
    module must say so whether the row it is currently reporting is green or red."""
    green = H.c_stalls_are_named(_stall([{"id": "AUT-1", "terminal": None}], shallow=True), None)
    assert "SHALLOW" in green["detail"].upper()
    red = H.c_stalls_are_named(_stall([
        {"id": "AUT-2", "terminal": {"state": "stalled_needs_human", "since_utc": "2026-08-21T00:00:00Z",
                                     "why": "x"}}], shallow=True), None)
    assert "SHALLOW" in red["detail"].upper()


def test_the_terminal_state_string_is_imported_not_retyped():
    """One fact, one place: `"stalled_needs_human"` is `stuck_clock.TERMINAL_STATE`'s string, and
    health.py must read it from there rather than agreeing with it only in prose (the AUT-PD-013
    shape, applied to a new pair of modules)."""
    stall = _stall([{"id": "AUT-1", "terminal": None}])
    del stall["terminal_state"]
    row = H.c_stalls_are_named(stall, None)
    assert S.TERMINAL_STATE in row["detail"]


# ══════════════════════════════════════════════ health.py: the condition is actually wired to the board
def test_stalls_are_named_is_in_condition_order_and_has_a_declared_on_red():
    assert "stalls_are_named" in H.CONDITION_ORDER
    assert H.CONDITION_ON_RED.get("stalls_are_named") == "advises", (
        "a red `stalls_are_named` must never stop the loop — automation already tried and stopped on "
        "this ONE row, and telling the same automation to try harder this cycle is the busy-retry "
        "loop stuck_clock exists to unmask, rebuilt one level up"
    )


def test_the_condition_is_actually_assembled_into_build():
    """⛔ THE MUTATION THIS FILE'S SIBLINGS ALL GUARD: a condition function that is correct, present
    and never called is the exact shape of the failure this whole ledger item is about."""
    src = open(os.path.join(PARENT, "health.py"), encoding="utf-8").read()
    assert "c_stalls_are_named(stall, stall_err)" in src, (
        "c_stalls_are_named is defined but not assembled into build()'s conditions list — it would "
        "never reach a board, which is precisely how stuck_clock.py went unused for a full cycle"
    )


def test_build_reports_stalls_are_named_end_to_end(tmp_path):
    """The condition reaches a real board built through the public `build()` entry point, not merely
    through the bare function — the same distinction `test_the_condition_is_actually_wired_into_the_board`
    makes for `cycles_are_sized`/`fanout_is_governed`."""
    root = tmp_path / "autonomy"
    (root / "receipts").mkdir(parents=True)
    (root / "research-ledger.json").write_text(json.dumps({"entries": [
        {"id": "AUT-LAB", "serves": {"route": "RT-LAB"}, "state": "queued",
         "retry_budget": 3, "score": 1.0}]}))
    (root / "autonomy-state.json").write_text(json.dumps({"cycle_interval_hours": 4}))
    stall_path = root / "stall.json"
    stall_path.write_text(json.dumps(_stall([
        {"id": "AUT-STUCK", "terminal": {"state": "stalled_needs_human", "since_utc": "2026-08-21T00:00:00Z",
                                         "why": "x"}}])))
    board = H.build(ledger_path=str(root / "research-ledger.json"),
                    state_path=str(root / "autonomy-state.json"),
                    receipts_dir=str(root / "receipts"),
                    authority_path=str(root / "publication-authority.json"),
                    stall_path=str(stall_path), health_path=str(root / "health.json"),
                    now=T0)
    rows = [c for c in board["conditions"] if c["key"] == "stalls_are_named"]
    assert len(rows) == 1
    assert rows[0]["verdict"] == "STALLED-ROWS"
    assert "stalls_are_named" in board["needs_attention"]
    assert "stalls_are_named" not in board["blocking"], (
        "an advisory red must never appear in `blocking` — that is research-loop §1's stop condition"
    )


def test_the_cli_carries_a_stall_verdict_flag():
    src = open(os.path.join(PARENT, "health.py"), encoding="utf-8").read()
    assert '"--stall-verdict"' in src
    assert "stall_path=a.stall_verdict" in src, (
        "the flag is parsed but never threaded into build() — it would report unmeasured forever, "
        "identically to a flag that was never added"
    )


# ══════════════════════════════════════════════════════ handoff.py: terminal_ids() / top_items()
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
def stuck_repo(tmp_path):
    """A real git repo with one ledger row touched-forever-without-advancing, exactly
    `test_stuck_clock_a_retry_is_not_an_advance.py`'s own fixture shape — this file does not re-argue
    stuck_clock's correctness, only that `handoff.py` actually calls it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q")
    ledger_name = "ledger.json"

    def _row(**kw):
        base = {"id": "AUT-X", "state": "queued", "owner": None, "claimed_utc": None,
                "attempts": 0, "score": 100.0, "what": "do the thing"}
        base.update(kw)
        return base

    def commit(rows, hours):
        when = T0 + datetime.timedelta(hours=hours)
        (repo / ledger_name).write_text(json.dumps({"entries": rows}))
        _run(repo, "add", ledger_name, when=when)
        _run(repo, "commit", "-q", "-m", f"+{hours}h", when=when)

    commit([_row()], 0)
    for i in range(1, 10):
        commit([_row(owner=f"seat-{i}" if i % 2 else None, attempts=i, score=100.0 + i)], i)

    return repo, ledger_name


def test_terminal_ids_reads_a_real_stuck_row_from_git(stuck_repo):
    """⛔⛔ THE ACTUAL INTEGRATION. Everything above this line could pass with `terminal_ids()`
    returning an empty set unconditionally — this is the one test that proves it genuinely calls
    `stuck_clock.terminal_rows()` against real git history.

    The fixture is pinned to 2026-08-20, so `stuck_clock`'s own `datetime.now()` (the real wall clock,
    well past 2026) already clears the 24 h fallback threshold — no time freezing needed.
    """
    repo, ledger_name = stuck_repo
    report = S.open_row_clocks(repo=str(repo), path=ledger_name)
    ids = frozenset(c.entry_id for c, _ in S.terminal_rows(report))
    assert "AUT-X" in ids, "the fixture did not even produce a terminal row — nothing below is testing anything"

    got = HF.terminal_ids(repo=str(repo), path=ledger_name)
    assert "AUT-X" in got, "handoff.terminal_ids() did not read the same terminal row stuck_clock computes"


def test_terminal_ids_fails_open_on_a_bad_repo():
    """⛔⛔ THE DIRECTION THAT MATTERS MOST. A git failure must never hide real, takeable work — the
    exact CLAUDE.md §4 asymmetry ('an absent reading is not a reading of absence') applied to a queue."""
    assert HF.terminal_ids(repo="/definitely/not/a/repo/at/all", path="ledger.json") == frozenset()


def test_top_items_excludes_a_named_id_and_nothing_else():
    """Pure unit test, no git: `exclude_ids` is dependency-injected so `top_items()` stays testable
    without a git fixture for every caller."""
    ledger = {"entries": [
        {"id": "AUT-HIGH", "state": "queued", "retry_budget": 3, "score": 99.0},
        {"id": "AUT-STUCK", "state": "queued", "retry_budget": 3, "score": 90.0},
        {"id": "AUT-LOW", "state": "queued", "retry_budget": 3, "score": 1.0},
    ]}
    top = HF.top_items(ledger, exclude_ids=frozenset({"AUT-STUCK"}))
    assert [e["id"] for e in top] == ["AUT-HIGH", "AUT-LOW"]


def test_top_items_with_no_exclusion_is_unchanged():
    """The pre-AUT-PROP-029 caller (nothing passed) must see EXACTLY the old behaviour."""
    ledger = {"entries": [{"id": "AUT-A", "state": "queued", "retry_budget": 3, "score": 5.0}]}
    assert [e["id"] for e in HF.top_items(ledger)] == ["AUT-A"]


def test_exclusion_never_touches_the_ledger_dict_or_the_rows_state():
    """⛔⛔ THE CONSTRAINT stuck_clock.py's OWN DESIGN RESTS ON, CHECKED FROM THE OTHER SIDE. The
    verdict is computed, never stored — `top_items()` must filter a VIEW, never mutate the entry it is
    excluding, and never write `stalled_needs_human` (or anything else) onto `state`."""
    entry = {"id": "AUT-STUCK", "state": "queued", "retry_budget": 3, "score": 90.0}
    ledger = {"entries": [entry]}
    before = dict(entry)
    HF.top_items(ledger, exclude_ids=frozenset({"AUT-STUCK"}))
    assert entry == before, "top_items mutated the entry it excluded"
    assert entry["state"] == "queued", "a terminal exclusion must never write a state onto the ledger row"


def test_build_names_the_excluded_row_rather_than_silently_dropping_it(monkeypatch):
    """⚠ `handoff.py`'s own design rule: a successor is told WHERE TO LOOK, never left to wonder why
    the top-scored row from a prior report vanished. Monkeypatch `terminal_ids` directly — this test
    is about `build()`'s wiring, not about stuck_clock's git walk, which the test above already
    covers."""
    ledger = {"entries": [
        {"id": "AUT-STUCK", "state": "queued", "retry_budget": 3, "score": 99.0, "kind": "experiment",
         "what": "the highest scorer, now stalled"},
        {"id": "AUT-NEXT", "state": "queued", "retry_budget": 3, "score": 5.0, "kind": "analysis",
         "what": "next in line"},
    ]}
    monkeypatch.setattr(HF, "terminal_ids", lambda *a, **k: frozenset({"AUT-STUCK"}))
    prompt = HF.build(reason="test", ledger=ledger, state={"max_cycles_per_session": 2})
    assert "AUT-NEXT" in prompt
    assert "EXCLUDED" in prompt and "AUT-STUCK" in prompt, (
        "the excluded row must be named, not silently absent from the queue section"
    )


def test_json_mode_also_applies_the_exclusion(monkeypatch, tmp_path, capsys):
    """`main()`'s `--json` branch calls `top_items()` a SECOND time, independently of `build()`, to
    pick the `focus` id for the session title — a fix bound to only one call site regresses at its
    sibling (`paper-hardening` §8b.2), and this is exactly that sibling."""
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps({"entries": [
        {"id": "AUT-STUCK", "state": "queued", "retry_budget": 3, "score": 99.0},
        {"id": "AUT-NEXT", "state": "queued", "retry_budget": 3, "score": 5.0},
    ]}))
    monkeypatch.setattr(HF, "LEDGER", ledger_path)
    monkeypatch.setattr(HF, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(HF, "terminal_ids", lambda *a, **k: frozenset({"AUT-STUCK"}))
    HF.main(["--json"])
    out = json.loads(capsys.readouterr().out)
    assert "AUT-NEXT" in out["title"], f"the excluded row was still picked as the focus: {out['title']}"
