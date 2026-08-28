"""The k8s probe split and the OTP/systemd restart bound, as guards — AUT-PROP-034.

⛔⛔ THE TWO PROPERTIES THIS FILE EXISTS FOR, AND NEITHER WAS CHECKABLE BEFORE IT.

1. **A READINESS-SHAPED CONDITION MUST NOT BE WIRED TO A RESTART-SHAPED RESPONSE.** Kubernetes' own
   probe documentation names this as the classic health-board bug: a dependency check inside LIVENESS
   means the dependency blips, every replica fails liveness at once, everything restarts, and the
   dependency faces a cold-start herd — *"incorrect implementation of liveness probes can lead to
   cascading failures."* `health.py` was a FLAT LIST of eleven conditions: nothing in it said whether
   a row's subject was the loop's own pulse or somebody else's server, so the bug could not be ruled
   out by reading the file. `CONDITION_AXIS` states it and this file checks it.

2. **NO SUPERVISOR MAY RETRY FOREVER IN SILENCE.** OTP's `intensity`/`period` and systemd's
   `StartLimitBurst`/`StartLimitIntervalSec` both bound repeated failure and hand it to a human;
   Kubernetes' CrashLoopBackOff is the counter-example, backing off forever and telling nobody.
   Verified by grep on 2026-08-28: no such counter existed anywhere in `research/autonomy/`. A red
   `blocks` row therefore produced "refuse, respawn, refuse" at the driver Routine's period,
   indefinitely, with no rung above another refusal.

⭐ THE TESTS ARE WRITTEN AGAINST THE BEHAVIOUR, NOT THE TABLE, WHEREVER THAT IS POSSIBLE. A guard
that only re-reads the constant it is guarding passes with the mechanism removed (`paper-hardening`
records seven one-of-a-pair defects found exactly that way), so the intensity tests drive real boards
through real consecutive runs and assert on what the board says.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import pathlib

import pytest

AUTONOMY = pathlib.Path(__file__).resolve().parent.parent
REPO = AUTONOMY.parent.parent
NOW = datetime.datetime(2026, 8, 28, 12, 0, 0, tzinfo=datetime.timezone.utc)


def _load(name):
    spec = importlib.util.spec_from_file_location(f"autonomy_{name}", AUTONOMY / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def health():
    return _load("health")


@pytest.fixture(scope="module")
def alarm():
    return _load("stall_alarm")


# ─────────────────────────────────────────────────────────────────────────────── fixture plumbing
def _lab(tmp_path, *, entries=None, receipts=(), authority=None, state=None):
    """A whole autonomy directory on disk, built in tmp — never the live tree, which the loop writes."""
    root = tmp_path / "autonomy"
    (root / "receipts").mkdir(parents=True, exist_ok=True)
    default_entries = [{"id": "AUT-LAB", "serves": {"route": "RT-LAB"}, "state": "queued",
                        "retry_budget": 3, "score": 1.0}]
    (root / "research-ledger.json").write_text(
        json.dumps({"entries": list(entries) if entries is not None else default_entries}))
    (root / "autonomy-state.json").write_text(json.dumps(
        state if state is not None else {"cycle_interval_hours": 4, "max_cycles_per_session": 2,
                                         "subagent_width": 5, "backoff_level": 0}))
    for i, r in enumerate(receipts):
        (root / "receipts" / f"CYC-2026-08-{20 + i:02d}T00-00Z.json").write_text(json.dumps(r))
    if authority is not None:
        (root / "publication-authority.json").write_text(json.dumps(authority))
    return {
        "ledger_path": str(root / "research-ledger.json"),
        "state_path": str(root / "autonomy-state.json"),
        "receipts_dir": str(root / "receipts"),
        "authority_path": str(root / "publication-authority.json"),
        "gates_path": None,
        "health_path": str(root / "health.json"),
    }


def _blocked_ledger():
    """A blocked row with no observation behind it -> `blocks_are_real` RED, whose on_red is
    `redirects`. The simplest reproducible red in a `RETRIED_ON_RED` class."""
    return [{"id": "AUT-X", "serves": {"route": "RT-X"}, "state": "blocked",
             "blocked_evidence": "", "retry_budget": 3, "score": 1.0}]


def _outward_receipt():
    """A receipt recording an outward act. With no authority file this is `authority_respected` RED,
    which is the one `blocks` row and the declared readiness exception."""
    return {"cycle_id": "CYC-OUT", "ended_utc": "2026-08-28T11:00:00Z", "route_advanced": "RT-X",
            "session_id": "s1", "subagents": {"max_concurrent": 1},
            "outward_acts": [{"venue": "journal", "act": "submission"}]}


def _run_n(health, lab, n, *, now=NOW):
    """Grade the board `n` times in a row, threading each board in as the next run's history.

    ⚠ THE HISTORY IS THREADED EXPLICITLY rather than left to the on-disk `health.json`, so these
    tests never depend on write ordering — but it is the SAME `merge()` path the real tick takes.
    """
    board = None
    for i in range(n):
        board = health.build(**lab, now=now + datetime.timedelta(hours=2 * i), previous=board)
    return board


def _cond(board, key):
    rows = [c for c in board["conditions"] if c["key"] == key]
    assert len(rows) == 1, f"expected exactly one {key} row, got {len(rows)}"
    return rows[0]


# ══════════════════════════════════════════════════ (a) the three axes, and the audit they encode ══
def test_every_condition_declares_which_axis_it_is_on(health):
    """A row with no axis is a row whose response class nobody chose. The k8s bug is exactly the
    unstated case, so an unstated case must fail here rather than be defaulted quietly."""
    assert set(health.CONDITION_AXIS) == set(health.CONDITION_ORDER), (
        "a condition exists with no declared axis (or vice versa) — the k8s failure mode cannot be "
        "ruled out by inspection of a flat list, which is the state this table replaced"
    )
    assert set(health.CONDITION_AXIS.values()) <= set(health.AXES)
    # ⛔ AND ALL THREE MUST BE IN USE. A "split" that in practice tags everything one way is a flat
    # list wearing a taxonomy, and it would pass every other assertion in this file.
    assert set(health.CONDITION_AXIS.values()) == set(health.AXES), (
        "one of liveness/readiness/progress is unused — a taxonomy nothing lands in is not a split"
    )


def test_no_readiness_row_may_stop_the_loop_undeclared(health):
    """⛔⛔ THE AUDIT, AS A PREDICATE. `blocks` is this repository's restart-shaped response: the cycle
    refuses to start, the session ends, and the driver Routine's next firing is a fresh session that
    reads the same board. Wiring a dependency reading to it is the k8s bug. It is permitted for
    exactly one row, for a reason k8s' rule does not model (an outward act under a human's name is
    irreversible), and that permission has to be WRITTEN DOWN with the row named."""
    for key, axis in health.CONDITION_AXIS.items():
        if axis != "readiness":
            continue
        if health.CONDITION_ON_RED[key] != "blocks":
            continue
        assert key in health.READINESS_MAY_BLOCK, (
            f"{key} reads a DEPENDENCY and its red stops the loop, with no declared exception. That "
            f"is the cascading-failure shape Kubernetes' probe docs name: a dependency blips and the "
            f"response is to respawn into it. Either retag it, move it off `blocks`, or declare why "
            f"continuing would compound irreversible harm."
        )
        assert len(health.READINESS_MAY_BLOCK[key].strip()) > 40, (
            f"{key}'s exception is declared but says nothing — a waiver with no reason is the "
            f"undeclared state with a tick-box in front of it"
        )


def test_the_declared_exception_is_not_stale(health):
    """A waiver that outlives the thing it waives is worse than none: it reads as scrutiny applied.
    Every row in READINESS_MAY_BLOCK must still BE readiness and still BE blocking."""
    for key in health.READINESS_MAY_BLOCK:
        assert key in health.CONDITION_ORDER, f"{key} is waived and is not a condition any more"
        assert health.CONDITION_AXIS[key] == "readiness", (
            f"{key} is no longer readiness-shaped; the exception is dead text and must be removed"
        )
        assert health.CONDITION_ON_RED[key] == "blocks", (
            f"{key} no longer blocks, so nothing is being excepted — delete the waiver"
        )


def test_a_waived_readiness_block_is_bounded_rather_than_merely_permitted(health):
    """★ THE HALF THAT MAKES THE EXCEPTION SURVIVABLE. Permission to refuse is permission to refuse
    FOREVER unless something counts. Every waived row must fall in a class the intensity counter
    actually counts — otherwise the waiver's own promise ("bounded by RESTART_INTENSITY") is a
    sentence rather than a mechanism."""
    for key in health.READINESS_MAY_BLOCK:
        assert health.CONDITION_ON_RED[key] in health.RETRIED_ON_RED, (
            f"{key} is waived on the promise that its refusals are counted, and its on_red class is "
            f"not one the counter counts"
        )


def test_the_board_stamps_an_axis_on_every_row(health, tmp_path):
    """The table means nothing if the artifact a reader opens does not carry it."""
    board = health.build(**_lab(tmp_path), now=NOW)
    for c in board["conditions"]:
        assert c.get("axis") in health.AXES, f"{c['key']} reached the board with axis {c.get('axis')!r}"


def test_an_unclassified_row_defaults_to_the_conservative_axis(health, tmp_path, monkeypatch):
    """⛔ MUTATION-SHAPED: remove a row's classification and the board must not describe it as
    self-only. `liveness` is the one axis whose prescribed response is a restart, so an unknown row
    must never land there by omission."""
    trimmed = dict(health.CONDITION_AXIS)
    trimmed.pop("gates_green")
    monkeypatch.setattr(health, "CONDITION_AXIS", trimmed)
    board = health.build(**_lab(tmp_path), now=NOW)
    assert _cond(board, "gates_green")["axis"] == "readiness", (
        "an unclassified condition defaulted to something other than the never-restart axis"
    )


def test_the_only_restart_equivalent_reads_blocking_and_nothing_else(health):
    """⭐ THE OTHER HALF OF THE AUDIT, AND IT IS ABOUT THE CONSUMER RATHER THAN THE BOARD. Tagging the
    rows is worthless if some caller respawns on a different signal. Two facts are asserted here
    because they are what make the (a) verdict true:
      - `--check`, the exit code `research-loop` §1 turns into "refuse to start", is computed from
        `blocking` alone — never from `needs_attention`, and never from an axis;
      - `handoff.py`, the module that builds a respawn prompt, does not read the board at all.
    """
    src = (AUTONOMY / "health.py").read_text()
    check = src[src.index("if a.check:"):src.index("if a.check_any:")]
    assert 'board.get("blocking")' in check and "needs_attention" not in check, (
        "--check no longer gates on `blocking` alone; every red would stop the loop again, which is "
        "the 2026-08-27 outage"
    )
    handoff_src = (AUTONOMY / "handoff.py").read_text()
    assert "health.json" not in handoff_src.replace("health.py", ""), (
        "handoff.py has started reading the health board. A respawn driven by a readiness row IS the "
        "cold-start herd; if this is deliberate it needs the same declared exception `blocks` has."
    )


# ═════════════════════════════════════════ (b) restart intensity — OTP/systemd, ported and bounded ══
def test_the_bound_is_the_prior_arts_number_and_says_so(health):
    """⛔ N MAY NOT BE INVENTED SILENTLY. systemd's `DefaultStartLimitBurst` is 5; OTP's default
    intensity is 1 per 5 s; Kubernetes never stops. The constant is systemd's, and the file has to
    carry the citation, because a tuning constant with no provenance is one somebody will move."""
    assert health.RESTART_INTENSITY == 5
    src = (AUTONOMY / "health.py").read_text()
    window = src[src.index("restart intensity — OTP and systemd"):src.index("RESTART_INTENSITY = 5")]
    # ⚠ EACH TOKEN IS A DEFAULT VALUE SOMEBODY ELSE DEFENDED, not merely the name of a mechanism. An
    # earlier version of this guard looked for "StartLimitBurst", which appears twice in the window,
    # so deleting the sentence that carries the NUMBER left the guard green.
    for token in ("DefaultStartLimitBurst", "1 restart per 5 seconds", "CrashLoopBackOff"):
        assert token in window, (
            f"the bound no longer cites {token!r} — a tuning constant whose provenance is gone is one "
            f"the next reader will move on taste"
        )


def test_a_red_run_counts_and_an_unmeasured_one_does_not(health, tmp_path):
    """⛔ THE COUNTER IS NARROWER THAN `consecutive_bad_runs` ON PURPOSE. That one counts unmeasured
    runs too, correctly, because "unmeasured for six runs" is worth seeing. Escalating on it would
    put a §3 interrupt in front of trimcrae for a reading nobody has taken — a different problem with
    a different fix."""
    board = _run_n(health, _lab(tmp_path, entries=_blocked_ledger()), 3)
    row = _cond(board, "blocks_are_real")
    assert row["needs_attention"] and row["consecutive_red_runs"] == 3

    unmeasured = _cond(_run_n(health, _lab(tmp_path), 3), "gates_green")
    assert unmeasured["unmeasured"] and unmeasured["consecutive_red_runs"] == 0, (
        "an unmeasured row is accruing a restart budget it can never legitimately spend"
    )
    assert unmeasured["consecutive_bad_runs"] == 3, (
        "the wider counter stopped counting unmeasured runs — that is stall_alarm's clock and it "
        "must keep seeing them"
    )


def test_a_red_run_after_unmeasured_ones_starts_its_own_count(health, tmp_path):
    """⛔ THE SEQUENCE THAT SEPARATES THE TWO COUNTERS, AND THE ONLY ONE THAT CAN. Four runs where the
    reading could not be taken, then one genuine red. `consecutive_bad_runs` is correctly 5 — that is
    stall_alarm's clock and "nobody could grade this all night" is worth mailing about. The restart
    budget must read 1: the loop has refused ONCE. Reading the wider counter here would fire a §3
    escalation on the first real failure after a quiet outage, which is both wrong and the fastest
    way to teach trimcrae to ignore the channel."""
    lab = _lab(tmp_path)
    verdict = tmp_path / "gates.json"
    verdict.write_text(json.dumps({"ok": False, "detail": "tests.yml concluded failure on main"}))

    board = None
    for i in range(4):                                    # no verdict file -> UNMEASURED
        board = health.build(**lab, now=NOW + datetime.timedelta(hours=2 * i), previous=board)
    assert _cond(board, "gates_green")["unmeasured"] is True, "the scenario did not reproduce"

    red = health.build(**{**lab, "gates_path": str(verdict)},
                       now=NOW + datetime.timedelta(hours=8), previous=board)
    row = _cond(red, "gates_green")
    assert row["needs_attention"] is True
    assert row["consecutive_bad_runs"] == 5, "the wide counter stopped seeing the unmeasured run(s)"
    assert row["consecutive_red_runs"] == 1, (
        "the restart budget inherited a count from runs in which nothing was measured — four "
        "unreadable runs and one refusal is not five refusals"
    )


def test_the_budget_is_spent_at_exactly_n_and_not_before(health, tmp_path):
    lab = _lab(tmp_path, entries=_blocked_ledger())
    n = health.RESTART_INTENSITY
    before = _cond(_run_n(health, lab, n - 1), "blocks_are_real")
    at = _cond(_run_n(health, lab, n), "blocks_are_real")
    assert before["intensity"]["exhausted"] is False, f"escalated at {n - 1} runs, one early"
    assert at["intensity"]["exhausted"] is True, f"still not escalating at {n} consecutive red runs"
    assert at["key"] in _run_n(health, lab, n)["escalations"]


def test_one_green_run_resets_the_budget(health, tmp_path):
    """⭐ CONSECUTIVENESS IS THE WINDOW, WHICH IS WHY THERE IS NO `period` PARAMETER. If a green run
    did not reset the count, the constant would need OTP's second parameter and would silently be
    counting "reds ever" instead."""
    bad, good = _lab(tmp_path / "bad", entries=_blocked_ledger()), _lab(tmp_path / "good")
    board = _run_n(health, bad, health.RESTART_INTENSITY)
    assert board["escalations"] == ["blocks_are_real"]
    healed = health.build(**good, now=NOW + datetime.timedelta(hours=99), previous=board)
    assert _cond(healed, "blocks_are_real")["consecutive_red_runs"] == 0
    assert healed["escalations"] == []


def test_an_advisory_row_never_escalates_however_long_it_is_red(health, tmp_path):
    """⛔ AN `advises` ROW IS RETRIED BY NOTHING, so it has no restart budget to spend. Counting one
    would be counting an event that does not occur — and it would hand trimcrae a §3 interrupt for a
    row `stall_alarm.py` already mails about, which is how a §3 escalation becomes background noise."""
    over = [{"cycle_id": f"CYC-{i}", "ended_utc": "2026-08-28T11:00:00Z", "route_advanced": "RT-X",
             "session_id": "one-session", "subagents": {"max_concurrent": 1}} for i in range(6)]
    lab = _lab(tmp_path, receipts=over)
    board = _run_n(health, lab, health.RESTART_INTENSITY + 3)
    row = _cond(board, "cycles_are_sized")
    assert row["needs_attention"] and row["on_red"] == "advises"
    assert row["intensity"]["counted"] is False
    assert row["intensity"]["exhausted"] is False
    assert board["escalations"] == [], (
        "an advisory red produced a §3 escalation — the loop is not retrying it, so there is nothing "
        "to have run out of"
    )


def test_the_one_blocking_row_escalates_rather_than_refusing_forever(health, tmp_path):
    """★ THE REGRESSION TEST FOR THE ACTUAL GAP. `authority_respected` is the single row that stops a
    cycle. Before this counter, the loop's answer to it was "refuse, and refuse again next firing",
    with nothing above it. Now the Nth refusal is a §3 escalation — and `--check` still returns 1, so
    the safety property is untouched."""
    lab = _lab(tmp_path, receipts=[_outward_receipt()])
    board = _run_n(health, lab, health.RESTART_INTENSITY)
    row = _cond(board, "authority_respected")
    assert row["needs_attention"] and row["on_red"] == "blocks" and row["axis"] == "readiness"
    assert "authority_respected" in board["blocking"], "the stop condition was weakened"
    assert "authority_respected" in board["escalations"]
    assert "ESCALATE TO TRIMCRAE" in row["intensity"]["why"]


def test_the_escalation_reaches_the_committed_board(health, tmp_path):
    """⛔⛔ THE UNRUN-GUARD TRAP, CLOSED. A row red for five runs carries the SAME verdict string every
    time, so a commit-worthiness test built from verdicts alone answers "nothing new to say" at the
    exact run the budget is spent — the board would compute the escalation and the committed copy
    would never carry it. That is `subagent_width` all over again (CLAUDE.md §1: a governed number no
    code read)."""
    lab = _lab(tmp_path, entries=_blocked_ledger())
    n = health.RESTART_INTENSITY
    before = _run_n(health, lab, n - 1)
    crossing = health.build(**lab, now=NOW + datetime.timedelta(hours=2 * n), previous=before)
    assert before["escalations"] == [] and crossing["escalations"] == ["blocks_are_real"]
    worth, why = health.commit_worthy(before, crossing, 4.0, NOW + datetime.timedelta(hours=2 * n))
    assert worth, f"the run that spends the restart budget was not worth committing — {why}"


def test_the_escalations_flag_is_a_different_gate_from_check(health, tmp_path, capsys):
    """Two questions, two exit codes. `--check` asks whether a cycle may start; `--escalations` asks
    whether a human must now be told. A blocking row answers yes to the first from run one and yes to
    the second only when the budget is spent."""
    lab = _lab(tmp_path, entries=_blocked_ledger())
    argv = ["--ledger", lab["ledger_path"], "--state", lab["state_path"],
            "--receipts", lab["receipts_dir"], "--authority", lab["authority_path"],
            "--health", lab["health_path"]]
    assert health.main(argv + ["--escalations"]) == 0     # red, but budget unspent
    assert health.main(argv + ["--check"]) == 0           # `blocks_are_real` redirects, never blocks
    board = _run_n(health, lab, health.RESTART_INTENSITY)
    pathlib.Path(lab["health_path"]).write_text(json.dumps(board))
    # ⚠ One more grading on top of the persisted history is the (N+1)th red run, still exhausted.
    assert health.main(argv + ["--escalations"]) == 1
    capsys.readouterr()


def test_the_render_says_it_out_loud(health, tmp_path):
    """A board whose escalation is only in JSON is a board that tells nobody: the tick prints
    `render()` into the step summary and that is what a human actually reads."""
    lab = _lab(tmp_path, entries=_blocked_ledger())
    quiet = health.render(health.build(**_lab(tmp_path / "ok"), now=NOW), NOW).splitlines()
    assert any("no condition has been retried past" in ln for ln in quiet)

    loud = health.render(_run_n(health, lab, health.RESTART_INTENSITY), NOW).splitlines()
    # ⛔ THE SUMMARY LINE SPECIFICALLY, NOT "the string appears somewhere". `render` also prints each
    # exhausted row's own `why`, which carries the same words — so a first version of this assertion
    # passed with the summary line gutted, and a mutation proved it. The whole point of the summary
    # is that a reader who scans the last lines of a step summary sees the escalation without
    # reading every row.
    summary = [ln for ln in loud if ln.startswith("[loop-health] ⛔ ESCALATE TO TRIMCRAE (§3)")]
    assert len(summary) == 1, (
        f"the board's escalation summary line is gone; render prints {loud[-3:]}"
    )
    assert "blocks_are_real" in summary[0]


# ═════════════════════════════════════════════════════════ the push channel actually carries it ══
def test_the_alarm_sends_the_escalation_even_inside_its_own_quiet_window(health, alarm, tmp_path):
    """⛔ THE WIRING, NOT THE INTENTION. `stall_alarm.py` suppresses a repeat for REPEAT_EVERY_RUNS
    (~a day). An escalation queued behind that suppression is an escalation that waits a day, so the
    crossing run sends once regardless — and exactly once, because the 1,476-commits-in-24-h lesson
    says an alarm that cries every tick gets muted."""
    lab = _lab(tmp_path, entries=_blocked_ledger())
    n = health.RESTART_INTENSITY
    # n runs of red: run 2 alarms, runs 3..n are inside the suppression window.
    boards = []
    prev = None
    for i in range(n):
        prev = health.build(**lab, now=NOW + datetime.timedelta(hours=2 * i), previous=prev)
        boards.append(prev)
    suppressed = alarm.decide(boards[n - 2])
    assert suppressed["send"] is False and "already alarmed" in suppressed["why"], (
        "the scenario did not reproduce — the run before the crossing one was not suppressed"
    )
    crossing = alarm.decide(boards[n - 1])
    assert crossing["send"] is True, "the escalation was swallowed by the ordinary repeat cadence"
    assert crossing["escalations"] == ["blocks_are_real"]
    assert "§3 ESCALATION" in crossing["subject"]
    assert "NOT ANOTHER CYCLE" in crossing["body"]


def test_the_escalation_does_not_then_mail_every_tick(health, alarm, tmp_path):
    """The other half: one mail outside the cadence, and only one. A sustained escalation must go
    back under rule 3, or the §3 channel becomes the thing everybody filters."""
    lab = _lab(tmp_path, entries=_blocked_ledger())
    board = _run_n(health, lab, health.RESTART_INTENSITY + 1)
    after = alarm.decide(board)
    assert after["send"] is False, (
        "the run AFTER the crossing one mailed again — a §3 escalation on every tick is the muted "
        "alarm this repository has already paid for"
    )


def test_an_ordinary_sustained_red_still_sends_the_ordinary_mail(health, alarm, tmp_path):
    """⚠ REGRESSION LENS. The escalation must not have replaced the alarm it sits above."""
    lab = _lab(tmp_path, entries=_blocked_ledger())
    board = _run_n(health, lab, 2)
    verdict = alarm.decide(board)
    assert verdict["send"] is True and verdict["escalations"] == []
    assert "§3 ESCALATION" not in verdict["subject"]
    assert "unhealthy for 2 checks" in verdict["subject"]
