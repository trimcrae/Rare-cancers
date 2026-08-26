"""Guards on the autonomy loop's health board — research/autonomy/health.py.

This board is the only thing standing between "I never have to check in" and a loop that fires
forever, commits daily and advances nothing. Nothing else in the repository measures it:
`./scripts/preflight.sh` grades what the loop WROTE, and a cycle that writes a tidy negative and
commits green passes every one of those gates while the program stands still
(`research/manuscripts/program/emc-autonomy-architecture.md` §5.1 vs §5.2).

⛔⛔ THE PROPERTY THIS FILE EXISTS FOR, AND EVERY OTHER TEST HERE IS DOWNSTREAM OF IT:
**AN UNMEASURABLE CONDITION IS `unmeasured`, NEVER `ok`.** Zero receipts is not evidence the loop is
delivering; it is the absence of evidence either way. Grading it green produces A GREEN BOARD BUILT
FROM MISSING DATA, which is the failure this repository has already paid for — env-echoed defaults
once carried a fabricated verdict all the way out, and CLAUDE.md §4 records the rule that came of it:
*an absent reading is not a reading of absence, and a populated field is not a measured one.*

⚠ THE COLLAPSE IS ONE CHARACTER WIDE. `health.py` builds rows with three different constructors
(`_green` / `_red` / `_unmeasured`) precisely so that the collapse is a single-site edit — and
`test_the_unmeasured_state_is_load_bearing` performs exactly that edit and asserts the suite catches
it. A guard that still passes with its mechanism removed is guarding nothing (`paper-hardening`
records seven one-of-a-pair defects found this way).

⭐ EVERY FIXTURE IS BUILT IN A TMP DIR, NEVER READ OUT OF THE LIVE TREE. `research/autonomy/` is
written by the loop itself, so a test that asserted a verdict against the real ledger would go red on
an unrelated commit and send whoever gets it hunting in the wrong file — the clock-dependent-test
defect `fleet_armed.state`'s docstring records. The one test that does touch the real tree asserts
only SHAPE, never a verdict.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
HEALTH_PY = REPO / "research" / "autonomy" / "health.py"
STATE_JSON = REPO / "research" / "autonomy" / "autonomy-state.json"

NOW = datetime.datetime(2026, 8, 26, 12, 0, 0, tzinfo=datetime.timezone.utc)


def _import_health():
    spec = importlib.util.spec_from_file_location("autonomy_health", HEALTH_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def health():
    return _import_health()


# ────────────────────────────────────────────────────────────────────────────────── fixture plumbing
def _z(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _lab(tmp_path, *, entries=None, state="seed", receipts=(), authority=None, gates=None):
    """A whole autonomy directory on disk. Returns the kwargs `health.build` needs to read it.

    `state="seed"` uses the REAL committed `autonomy-state.json`, so these tests bind the shipped seed
    rather than a convenient copy of it — a seed that stopped carrying `cycle_interval_hours` would
    silently make three conditions unmeasurable, and that must fail here.
    """
    root = tmp_path / "autonomy"
    (root / "receipts").mkdir(parents=True)
    (root / "research-ledger.json").write_text(json.dumps({"entries": list(entries or [])}))
    if state == "seed":
        (root / "autonomy-state.json").write_text(STATE_JSON.read_text())
    elif state is not None:
        (root / "autonomy-state.json").write_text(json.dumps(state))
    for i, r in enumerate(receipts):
        name = r.get("_name") or f"CYC-2026-08-{20 + i:02d}T00-00Z"
        (root / "receipts" / f"{name}.json").write_text(
            json.dumps({k: v for k, v in r.items() if not k.startswith("_")}))
    if authority is not None:
        (root / "publication-authority.json").write_text(json.dumps(authority))
    gates_path = None
    if gates is not None:
        gates_path = root / "gates-verdict.json"
        gates_path.write_text(json.dumps(gates))
    return {
        "ledger_path": str(root / "research-ledger.json"),
        "state_path": str(root / "autonomy-state.json"),
        "receipts_dir": str(root / "receipts"),
        "authority_path": str(root / "publication-authority.json"),
        "gates_path": str(gates_path) if gates_path else None,
        "health_path": str(root / "health.json"),
        "now": NOW,
    }


def _cond(board, key):
    rows = [c for c in board["conditions"] if c["key"] == key]
    assert len(rows) == 1, f"expected exactly one {key} row, got {len(rows)}"
    return rows[0]


def _receipt(route_advanced="RT-X", hours_ago=1, **extra):
    doc = {"ended_utc": _z(NOW - datetime.timedelta(hours=hours_ago)), "cycle_id": "CYC"}
    if route_advanced is not ...:
        doc["route_advanced"] = route_advanced
    doc.update(extra)
    return doc


# ───────────────────────────────────────────────────────────────────────── the seven, and their shape
def test_all_seven_5_2_conditions_are_present(health, tmp_path):
    """§5.2's table is the contract. A condition that quietly stops being emitted is a dimension of
    failure nobody is watching any more — and it would look identical to a healthy board."""
    board = health.build(**_lab(tmp_path))
    assert [c["key"] for c in sorted(board["conditions"], key=lambda c: c["key"])] == sorted(
        health.CONDITION_ORDER)
    assert set(health.CONDITION_ORDER) == {
        "cycle_delivering", "advancing_live_work", "evidence_moving", "blocks_are_real",
        "budget_recovering", "gates_green", "authority_respected",
    }, "the condition set drifted from the architecture §5.2 table — that is a DECLARED change (§10.4)"
    assert board["n_conditions"] == 7


def test_every_row_carries_the_alarm_state_idiom(health, tmp_path):
    """The board is read by whoever reads `alarm-state.json`, in the same way. A row missing its
    history fields cannot answer 'has this been red all night?', which is the first question asked."""
    board = health.build(**_lab(tmp_path))
    for field in ("_generated_utc", "_generated_et", "_stale_after_utc", "_stale_after_means"):
        assert board.get(field), f"the board must carry {field} — it is how a reader tells it is dead"
    for c in board["conditions"]:
        for field in ("key", "label", "source", "verdict", "ok", "unmeasured", "needs_attention",
                      "bad_since_utc", "consecutive_bad_runs"):
            assert field in c, f"{c['key']} is missing {field}"
        assert not (c["ok"] and c["unmeasured"]), f"{c['key']} is both ok and unmeasured"
        assert c["needs_attention"] == ((not c["ok"]) and not c["unmeasured"])


# ─────────────────────────────────────────────── ⛔ the property: unmeasured is not ok, and it is real
def _assert_zero_receipts_is_not_silently_green(board):
    """The assertions of the headline guard, factored out SO A MUTATION CAN BE POINTED AT THEM.

    Called twice: once by the guard, once by the mutation test under `pytest.raises`. If breaking the
    unmeasured/ok distinction does not make these fail, the guard is decoration.
    """
    cond = board["conditions"]
    row = [c for c in cond if c["key"] == "cycle_delivering"][0]
    assert row["unmeasured"] is True, "zero receipts must be UNMEASURED — nothing has reported"
    assert row["ok"] is False, (
        "zero receipts was graded ok. A loop that has never delivered a receipt is not a loop that is "
        "delivering; this is a green board built from missing data (CLAUDE.md §4)")
    assert row["needs_attention"] is False, (
        "unmeasured is not a failing loop, it is an unreadable one, and the fix is different — "
        "merging the two is the 2026-07-27 false-alarm defect graded the other way")
    assert "cycle_delivering" in board["unmeasured"]
    assert "cycle_delivering" not in board["needs_attention"]
    assert board["fully_measured"] is False, (
        "the board claimed to be fully measured while a condition was unmeasured")


def test_zero_receipts_is_unmeasured_and_never_silently_green(health, tmp_path):
    board = health.build(**_lab(tmp_path, receipts=()))
    _assert_zero_receipts_is_not_silently_green(board)
    assert _cond(board, "cycle_delivering")["verdict"] == "NO-RECEIPTS"
    assert "absence of a reading" in _cond(board, "cycle_delivering")["detail"]


def test_the_unmeasured_state_is_load_bearing_and_not_merely_decorative(health, tmp_path, monkeypatch):
    """MUTATION TEST. Collapse `unmeasured` into `ok` — the single-site defect — and the guard above
    MUST fail. This is the whole reason the three constructors exist as separate functions.

    ⚠ The mutation is the plausible one, not a contrived one: `_unmeasured` and `_green` have the same
    signature, so one wrong name at one call site (or a well-meaning 'nothing is wrong yet, call it
    ok') produces exactly this board.
    """
    kwargs = _lab(tmp_path, receipts=())
    monkeypatch.setattr(health, "_unmeasured", health._green)
    mutated = health.build(**kwargs)

    assert _cond(mutated, "cycle_delivering")["ok"] is True, (
        "the mutation did not even take — `_unmeasured` is not the mechanism this board rests on, "
        "which means the guard below proves nothing")
    with pytest.raises(AssertionError):
        _assert_zero_receipts_is_not_silently_green(mutated)

    monkeypatch.undo()
    restored = health.build(**kwargs)
    _assert_zero_receipts_is_not_silently_green(restored)
    assert restored["fully_measured"] is False


def test_an_unmeasured_board_never_reports_itself_as_fully_measured(health, tmp_path):
    """`ok` means 'nothing is FAILING', which is not 'everything was checked'. A reader who conflates
    them reads an ungradeable loop as a healthy one, so the board says both, separately."""
    board = health.build(**_lab(tmp_path))
    assert board["ok"] is True and board["fully_measured"] is False
    assert "DOES NOT MEAN EVERY CONDITION WAS MEASURED" in board["_ok_means"]


# ────────────────────────────────────────────────────────── advancing_live_work — the honesty instrument
def test_three_consecutive_none_receipts_turns_advancing_live_work_red(health, tmp_path):
    """§5.2's documentation-drift row, and CLAUDE.md §0's central failure: writing up a closed route
    always looks like progress. Three cycles that moved nothing live is the design's own alarm."""
    receipts = [_receipt(route_advanced="none", hours_ago=h) for h in (9, 5, 1)]
    board = health.build(**_lab(tmp_path, receipts=receipts))
    row = _cond(board, "advancing_live_work")
    assert row["needs_attention"] is True, f"three `route_advanced: none` receipts read as {row['verdict']}"
    assert row["ok"] is False and row["unmeasured"] is False, "this is a MEASURED failure, not an absence"
    assert row["verdict"] == "NOT-ADVANCING"
    assert board["ok"] is False and "advancing_live_work" in board["needs_attention"]


def test_a_fourth_receipt_that_advanced_a_route_clears_it(health, tmp_path):
    """The pair. A condition that cannot go back to green is an alarm nobody will act on twice."""
    receipts = [_receipt(route_advanced="none", hours_ago=h) for h in (9, 5, 1)]
    receipts.append(_receipt(route_advanced="RT-PARTNER-STRAT", hours_ago=0))
    row = _cond(health.build(**_lab(tmp_path, receipts=receipts)), "advancing_live_work")
    assert row["ok"] is True and row["verdict"] == "ADVANCING"


def test_two_none_receipts_is_not_yet_a_verdict(health, tmp_path):
    """One-of-a-pair guard on the OTHER side: the condition is defined on a run of three, and two must
    not be reported as either a pass or a fail. Inventing a verdict early is the same defect as
    grading missing data green, pointed the opposite way."""
    receipts = [_receipt(route_advanced="none", hours_ago=h) for h in (5, 1)]
    row = _cond(health.build(**_lab(tmp_path, receipts=receipts)), "advancing_live_work")
    assert row["unmeasured"] is True and row["ok"] is False
    assert row["verdict"] == "TOO-FEW-RECEIPTS"


def test_a_receipt_with_no_route_advanced_field_is_unmeasured_not_none(health, tmp_path):
    """⛔ An omitted `route_advanced` is a broken WRITER, not a cycle that advanced nothing. Reading it
    as 'none' would invent a failure exactly as readily as reading it as ok would hide one."""
    receipts = [_receipt(route_advanced="none", hours_ago=9), _receipt(route_advanced="none", hours_ago=5),
                _receipt(route_advanced=..., hours_ago=1)]
    row = _cond(health.build(**_lab(tmp_path, receipts=receipts)), "advancing_live_work")
    assert row["unmeasured"] is True and row["ok"] is False
    assert row["verdict"] == "ROUTE-ADVANCED-ABSENT"


# ──────────────────────────────────────────────────────────────────────────────────── blocks_are_real
def test_a_blocked_entry_with_no_evidence_turns_blocks_are_real_red(health, tmp_path):
    """CLAUDE.md §0: 'blocked' is a claim that needs evidence and it is usually wrong. Most blocked
    rows in this repo were waiting on a $0 fetch, a regeneration or a staging step."""
    entries = [{"id": "AUT-001", "state": "blocked", "blocked_by": "BLK-9", "blocked_evidence": ""},
               {"id": "AUT-002", "state": "queued"}]
    row = _cond(health.build(**_lab(tmp_path, entries=entries)), "blocks_are_real")
    assert row["needs_attention"] is True and row["unmeasured"] is False
    assert row["verdict"] == "UNEVIDENCED-BLOCK"
    assert "AUT-001" in row["payload"]["without_evidence"]


def test_a_blocked_entry_that_carries_its_observation_is_green(health, tmp_path):
    """The pair: the row must distinguish a real block from an unchecked one, not just count blocks."""
    entries = [{"id": "AUT-001", "state": "blocked", "blocked_by": "BLK-9",
                "blocked_evidence": "2026-08-20: the vendor's quote page 403s at the egress proxy"}]
    row = _cond(health.build(**_lab(tmp_path, entries=entries)), "blocks_are_real")
    assert row["ok"] is True and row["verdict"] == "EVIDENCED"


def test_an_unreadable_ledger_is_unmeasured_not_green(health, tmp_path):
    """A ledger that will not parse means the blocked rows were never READ. Two conditions rest on it
    and both must say so rather than reporting an empty backlog as a clean one."""
    kwargs = _lab(tmp_path)
    pathlib.Path(kwargs["ledger_path"]).write_text("{not json")
    board = health.build(**kwargs)
    for key in ("blocks_are_real", "evidence_moving"):
        assert _cond(board, key)["unmeasured"] is True, f"{key} graded an unreadable ledger"
        assert _cond(board, key)["ok"] is False


# ───────────────────────────────────────────────────────────────────────────────────── evidence_moving
def test_a_running_entry_frozen_over_two_cycles_turns_evidence_moving_red(health, tmp_path):
    """§4's unproven-pipeline rule as a board row: an item in flight must show MOVEMENT, and 'no error
    yet' is not movement. The seed cycle is 4 h, so 2 cycles is 8 h."""
    entries = [{"id": "AUT-007", "state": "running",
                "last_evidence_utc": _z(NOW - datetime.timedelta(hours=30))}]
    row = _cond(health.build(**_lab(tmp_path, entries=entries)), "evidence_moving")
    assert row["needs_attention"] is True and row["verdict"] == "FROZEN"


def test_a_running_entry_with_no_evidence_stamp_is_unmeasured_not_red(health, tmp_path):
    """The field the reading is taken FROM is missing, so the reading was not taken. Calling it frozen
    would be a diagnosis with no diagnostic behind it (CLAUDE.md §4)."""
    entries = [{"id": "AUT-007", "state": "running", "last_evidence_utc": None}]
    row = _cond(health.build(**_lab(tmp_path, entries=entries)), "evidence_moving")
    assert row["unmeasured"] is True and row["ok"] is False
    assert row["verdict"] == "EVIDENCE-TIME-UNREADABLE"


# ───────────────────────────────────────────────────────────────────────────────────── the other three
def test_backoff_raised_with_no_start_stamp_is_unmeasured_not_ok(health, tmp_path):
    """§5.2's `budget_recovering` is entirely a DURATION ('> 0 for > 24 h'). The level is readable and
    the duration is not, so the condition cannot be graded — and a raised backoff is exactly when a
    green row would be most misleading."""
    state = {"backoff_level": 2, "cycle_interval_hours": 4}
    row = _cond(health.build(**_lab(tmp_path, state=state)), "budget_recovering")
    assert row["unmeasured"] is True and row["ok"] is False
    assert row["verdict"] == "BACKOFF-AGE-UNKNOWN"


def test_backoff_held_past_the_grace_is_red_and_a_fresh_one_is_not(health, tmp_path):
    """A limit that never clears is a stuck loop; a limit raised an hour ago is the design working
    (§9 property 4, degrade rather than stop). One threshold, both sides asserted."""
    stuck = {"backoff_level": 1, "cycle_interval_hours": 4,
             "backoff_since_utc": _z(NOW - datetime.timedelta(hours=30))}
    fresh = {"backoff_level": 1, "cycle_interval_hours": 4,
             "backoff_since_utc": _z(NOW - datetime.timedelta(hours=1))}
    assert _cond(health.build(**_lab(tmp_path / "a", state=stuck)), "budget_recovering")["verdict"] == "STUCK"
    row = _cond(health.build(**_lab(tmp_path / "b", state=fresh)), "budget_recovering")
    assert row["ok"] is True and row["verdict"] == "BACKING-OFF"


def test_gates_green_without_a_verdict_file_is_unmeasured(health, tmp_path):
    """This module has no network by design (it must keep working when everything else has stopped),
    so the trunk's colour is supplied by the caller that can read Actions. No verdict, no reading —
    and the detail must say what would settle it, or the row is a question in a status's costume."""
    row = _cond(health.build(**_lab(tmp_path)), "gates_green")
    assert row["unmeasured"] is True and row["ok"] is False
    assert "--gates-verdict" in row["detail"]


def test_an_outward_act_with_no_authority_record_is_red_not_unmeasured(health, tmp_path):
    """⛔ §6.3, the one permission the loop cannot grant itself. Here the absence IS the reading: an
    act was taken and no grant exists anywhere to cover it. Contrast the test below."""
    receipts = [_receipt(outward_acts=[{"venue": "aixiv", "act": "submit", "target": "PUB-X"}])]
    row = _cond(health.build(**_lab(tmp_path, receipts=receipts, authority=None)), "authority_respected")
    assert row["needs_attention"] is True and row["unmeasured"] is False
    assert row["verdict"] == "UNGRANTED-ACT"


def test_no_authority_file_and_no_acts_is_unmeasured_not_green(health, tmp_path):
    """Nothing was checked, which is not the same as nothing being wrong: it is equally consistent
    with receipts that never log their outward acts at all."""
    row = _cond(health.build(**_lab(tmp_path, receipts=[_receipt()], authority=None)),
                "authority_respected")
    assert row["unmeasured"] is True and row["ok"] is False
    assert row["verdict"] == "NO-AUTHORITY-RECORD"


def test_a_journal_submission_never_matches_a_grant(health, tmp_path):
    """`journal.standing_grant` is a constant false — not a parameter, not reachable by any bar (§6.2,
    decision D4). An aiXiv post under a standing grant passes; a journal submission cannot."""
    authority = {"aixiv": {"standing_grant": True, "scope": {"acts": ["submit", "new_version"]}},
                 "journal": {"standing_grant": False}}
    ok_row = _cond(health.build(**_lab(
        tmp_path / "a", receipts=[_receipt(outward_acts=[{"venue": "aixiv", "act": "submit"}])],
        authority=authority)), "authority_respected")
    assert ok_row["ok"] is True and ok_row["verdict"] == "GRANTED"
    bad_row = _cond(health.build(**_lab(
        tmp_path / "b", receipts=[_receipt(outward_acts=[{"venue": "journal", "act": "submit"}])],
        authority=authority)), "authority_respected")
    assert bad_row["needs_attention"] is True


def test_a_late_receipt_turns_cycle_delivering_red(health, tmp_path):
    """§2.2 — a fired Routine is not a delivered one. Seed cycle 4 h, deadline 2 periods = 8 h."""
    row = _cond(health.build(**_lab(tmp_path, receipts=[_receipt(hours_ago=20)])), "cycle_delivering")
    assert row["needs_attention"] is True and row["verdict"] == "LATE"


def test_a_receipt_with_no_readable_clock_is_unmeasured(health, tmp_path):
    """A receipt with no timestamp cannot testify to delivery. ⚠ File mtime is deliberately not a
    fallback: a fresh `git clone` rewrites every mtime, which would make an ancient receipt look like
    this minute's — a populated field that is not a measured one."""
    receipts = [{"cycle_id": "CYC-broken", "route_advanced": "RT-X"}]
    row = _cond(health.build(**_lab(tmp_path, receipts=receipts)), "cycle_delivering")
    assert row["unmeasured"] is True and row["verdict"] == "RECEIPT-TIME-UNREADABLE"


# ───────────────────────────────────────────────────────────── history, commit discipline, cli contract
def test_history_carries_forward_across_runs(health, tmp_path):
    """`bad_since_utc` / `consecutive_bad_runs` are what let a reader answer 'has this been red all
    night?'. State lives IN the artifact — there is no side store."""
    kwargs = _lab(tmp_path, receipts=[_receipt(route_advanced="none", hours_ago=h) for h in (9, 5, 1)])
    first = health.build(**kwargs, previous=None)
    assert _cond(first, "advancing_live_work")["consecutive_bad_runs"] == 1
    second = health.build(**kwargs, previous=first)
    row = _cond(second, "advancing_live_work")
    assert row["consecutive_bad_runs"] == 2
    assert row["bad_since_utc"] == _cond(first, "advancing_live_work")["bad_since_utc"], (
        "bad_since_utc moved on the second run — 'red for how long' would reset every tick")


def test_an_unchanged_board_is_not_worth_committing(health, tmp_path):
    """fleet_armed.py's discipline. Measured cost of ignoring it: 1,476 commits in 24 h, 703 of them
    saying in their own subject line that they did nothing."""
    kwargs = _lab(tmp_path)
    first = health.build(**kwargs, previous=None)
    assert first["_commit_worthy"] is True, "the first board is always worth committing"
    again = health.build(**kwargs, previous=first)
    assert again["_commit_worthy"] is False and "unchanged" in again["_commit_worthy_why"]


def test_a_board_near_its_own_expiry_is_committed_anyway(health, tmp_path):
    """The half of that lesson that gets dropped: a checker that goes quiet must not read as a checker
    that keeps saying 'fine'. The keep-alive means this file can never be the reason the board looks
    dead."""
    kwargs = _lab(tmp_path)
    first = health.build(**kwargs, previous=None)
    later = dict(kwargs, now=NOW + datetime.timedelta(hours=9))  # 3 cycles of 4 h = 12 h expiry
    assert health.build(**later, previous=first)["_commit_worthy"] is True


def test_a_changed_verdict_is_always_worth_committing(health, tmp_path):
    kwargs = _lab(tmp_path)
    first = health.build(**kwargs, previous=None)
    changed = _lab(tmp_path / "b", entries=[{"id": "AUT-1", "state": "blocked", "blocked_evidence": ""}])
    assert health.build(**changed, previous=first)["_commit_worthy"] is True


def test_check_exits_1_on_a_measured_failure_and_0_on_an_unmeasured_one(health, tmp_path, capsys):
    """The CLI contract, and it encodes the distinction: `--check` gates on FAILURE, not on
    unreadability. An unmeasured board must not wedge the caller into a permanent non-zero exit — the
    fix for it is to make the reading possible, which is a different action."""
    red = _lab(tmp_path / "a", receipts=[_receipt(route_advanced="none", hours_ago=h) for h in (9, 5, 1)])
    argv = ["--ledger", red["ledger_path"], "--state", red["state_path"], "--receipts",
            red["receipts_dir"], "--authority", red["authority_path"], "--health", red["health_path"]]
    assert health.main(argv + ["--check"]) == 1
    assert health.main(argv) == 0, "the default render must never fail a run — a red run is a push channel"

    quiet = _lab(tmp_path / "b")
    argv = ["--ledger", quiet["ledger_path"], "--state", quiet["state_path"], "--receipts",
            quiet["receipts_dir"], "--authority", quiet["authority_path"], "--health",
            quiet["health_path"]]
    assert health.main(argv + ["--check"]) == 0
    capsys.readouterr()


def test_write_persists_a_board_that_round_trips(health, tmp_path):
    kwargs = _lab(tmp_path)
    argv = ["--ledger", kwargs["ledger_path"], "--state", kwargs["state_path"], "--receipts",
            kwargs["receipts_dir"], "--authority", kwargs["authority_path"], "--health",
            kwargs["health_path"], "--write"]
    assert health.main(argv) == 0
    written = json.loads(pathlib.Path(kwargs["health_path"]).read_text())
    assert len(written["conditions"]) == 7 and written["_stale_after_means"]


def test_the_board_is_deterministic(health, tmp_path):
    """A cycle re-checks every time and the board is committed. Two runs that disagree make every diff
    unreadable — and would defeat `_commit_worthy` outright."""
    kwargs = _lab(tmp_path, receipts=[_receipt(hours_ago=1)],
                  entries=[{"id": "AUT-1", "state": "queued"}])
    assert json.dumps(health.build(**kwargs)) == json.dumps(health.build(**kwargs))


def test_no_dollar_figure_is_ever_written_into_the_board(health, tmp_path):
    """CLAUDE.md rule 1: research/compute/pricing.md owns every cost. A board that carries a price is
    a second home for it, and the two will disagree."""
    import re
    blob = json.dumps(health.build(**_lab(tmp_path))) + HEALTH_PY.read_text()
    prices = {m for m in re.findall(r"\$[0-9][0-9,.]*", blob)} - {"$0"}
    assert not prices, f"a dollar figure appears in the health board or its source: {sorted(prices)}"


def test_the_seed_state_admits_the_denominator_is_unknown(health):
    """§9.2 is explicit: the utilisation denominator is CALIBRATED from an observed window flip, and
    until one is seen the loop SAYS UNKNOWN rather than inventing one. A number here would put a
    fabricated denominator underneath every utilisation reading the controller ever takes."""
    state = json.loads(STATE_JSON.read_text())
    assert state["_schema"] == "emc-autonomy-state/1"
    assert state["utilisation_denominator"] is None and state["last_limit_flip"] is None
    assert "UNKNOWN" in state["_utilisation_denominator_means"]
    assert state["backoff_level"] == 0 and state["cycle_interval_hours"] == 4
    assert state["subagent_width"] == 5 and state["items_per_cycle"] == 1
    assert state["utilisation_target"] == 0.8 and state["last_cycle_id"] is None


def test_it_runs_against_the_real_repository_without_asserting_a_verdict(health):
    """⚠ SHAPE ONLY, ON PURPOSE. research/autonomy/ is written by the loop, so asserting a verdict here
    would make this suite go red on an unrelated commit — the clock-dependent-test defect recorded in
    fleet_armed.state's docstring. What is worth binding is that the real files still PARSE into a
    seven-row board."""
    board = health.build(now=NOW)
    assert len(board["conditions"]) == 7
    assert isinstance(board["ok"], bool) and isinstance(board["fully_measured"], bool)
    assert health.render(board, NOW).startswith("[loop-health]")
