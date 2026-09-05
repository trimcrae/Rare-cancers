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
ARCH_MD = REPO / "research" / "manuscripts" / "program" / "emc-autonomy-architecture.md"
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
    # ⭐ THE NEUTRAL LAB CARRIES ONE TAKEABLE ITEM. An EMPTY ledger is not neutral — it is a real,
    # measured stall (every cycle from then on does nothing), and `queue_is_takeable` reports it as
    # one. Leaving the default empty would have made a stall the baseline of every test here, so the
    # empty case gets its own test instead of being smuggled in as scenery.
    default = [{"id": "AUT-LAB", "serves": {"route": "RT-LAB"}, "state": "queued",
                "retry_budget": 3, "score": 1.0}]
    (root / "research-ledger.json").write_text(
        json.dumps({"entries": list(entries) if entries is not None else default}))
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


def _seed_cycle_hours():
    """The seed's OWN cadence, read rather than remembered.

    ⛔⛔ THREE TESTS BELOW TYPED AN HOUR OFFSET AGAINST A REMEMBERED 4 h CADENCE, AND `_lab` COPIES
    THE REAL `autonomy-state.json` ON PURPOSE — so the moment a budget hold moved the shipped dial
    from 4 h to 24 h, every one of them went red while measuring nothing. Measured 2026-09-01: an
    entry 30 h stale is "frozen over two cycles" at 4 h and is comfortably fresh at 24 h, and the
    docstrings still said "Seed cycle 4 h, so 2 cycles is 8 h" — a restated constant, which is
    exactly what CLAUDE.md rule 1 forbids and what this repository keeps paying for.
    ★ THE POINT OF THESE TESTS IS THE MULTIPLE, NOT THE HOURS. "Two cycles late" is the property;
    how long a cycle happens to be is the seed's business, and reading it here means the throttle
    working can never be the reason this file is red.
    """
    return float(json.loads(STATE_JSON.read_text())["cycle_interval_hours"])


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


# ────────────────────────────────────────────────────────────────────────── the nine, and their shape
def _declared_conditions():
    """Parse §5.2's condition table out of the architecture, in the order it lists them.

    ⛔⛔ THE TABLE IS THE DECLARATION, AND UNTIL 2026-08-29 THIS TEST DID NOT READ IT. It compared
    `CONDITION_ORDER` against a literal set hand-copied INTO THIS FILE while printing "the condition
    set drifted from the architecture §5.2 table" on failure — so it asserted something it never
    checked, and the table was free to rot. It did: measured at df529936a, the table listed TEN
    conditions against `health.py`'s twelve. `stalls_are_named` (2026-08-28) reached the literal and
    never reached the table, so the drift was invisible; `scores_are_reachable` (2026-08-28, CYC-0072)
    reached neither, and reddened `main` for five consecutive commits. One duplicate caught the
    second addition by luck and missed the first entirely, which is the argument for having no
    duplicate at all (CLAUDE.md §1: one fact, one place).
    """
    rows, in_table = {}, False
    for line in ARCH_MD.read_text(encoding="utf-8").split("\n"):
        if line.startswith("| condition | on red |"):
            in_table = True
            continue
        if in_table:
            if line.startswith("|---"):
                continue
            if not line.startswith("| `"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows[cells[0].strip("`")] = cells[1].strip("*")
    return rows


@pytest.mark.parametrize("instant,expected", [
    (None, None),
    ("2026-09-04T04:07:00+00:00", "12:07 AM ET Sep 4, 2026"),
    ("2026-09-04T16:07:00+00:00", "12:07 PM ET Sep 4, 2026"),
    ("2026-09-04T02:07:00+00:00", "10:07 PM ET Sep 3, 2026"),
])
def test_health_timestamp_display_is_portable(health, instant, expected):
    timestamp = datetime.datetime.fromisoformat(instant) if instant else None
    assert health._et(timestamp) == expected


def test_all_5_2_conditions_are_present(health, tmp_path):
    """§5.2's table is the contract. A condition that quietly stops being emitted is a dimension of
    failure nobody is watching any more — and it would look identical to a healthy board."""
    board = health.build(**_lab(tmp_path))
    assert [c["key"] for c in sorted(board["conditions"], key=lambda c: c["key"])] == sorted(
        health.CONDITION_ORDER)

    declared = _declared_conditions()
    assert declared, "§5.2's condition table did not parse — the contract cannot be read at all"
    # ⭐ ORDER, not just membership: `health.py`'s CONDITION_ORDER comment claims it lists the
    # conditions "in the order the architecture table lists them", and a claim nothing checks is
    # exactly what this whole test exists to stop being true.
    assert list(declared) == list(health.CONDITION_ORDER), (
        "the condition set drifted from the architecture §5.2 table — that is a DECLARED change "
        "(§10.4). Add or remove the row in emc-autonomy-architecture.md §5.2; the table is the "
        "declaration and this test only reads it.")
    # ⛔ AND THE `on red` COLUMN, WHICH NOTHING BOUND UNTIL 2026-08-29 AND WHICH WAS THEREFORE EMPTY
    # IN EVERY SINGLE ROW while the header advertised it. That column is not decoration: `research-loop`
    # §1 branches on it, and its ABSENCE from the model is what killed the loop on 2026-08-27 — two
    # conditions reading immutable committed history were added as de-facto `blocks`, no session could
    # ever clear them, and the driver refused forever.
    assert declared == {k: health.CONDITION_ON_RED[k] for k in health.CONDITION_ORDER}, (
        "§5.2's `on red` column disagrees with health.py's CONDITION_ON_RED — a row's declared "
        "response to a red is what decides whether a cycle stops, redirects or reports")
    assert board["n_conditions"] == len(health.CONDITION_ORDER)


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
    yet' is not movement. The threshold is 2 cycles; the cycle length comes from the seed."""
    stale = 2.5 * _seed_cycle_hours()   # comfortably past two cycles, whatever a cycle is
    entries = [{"id": "AUT-007", "state": "running",
                "last_evidence_utc": _z(NOW - datetime.timedelta(hours=stale))}]
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
    """§2.2 — a fired Routine is not a delivered one. The deadline is 2 periods; the period comes
    from the seed rather than from this docstring's memory of it."""
    late = 2.5 * _seed_cycle_hours()
    row = _cond(health.build(**_lab(tmp_path, receipts=[_receipt(hours_ago=late)])),
                "cycle_delivering")
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
    # Just inside the 3-cycle expiry, derived from the seed's own cadence for the reason
    # `_seed_cycle_hours` records: at 4 h this read 9 h and silently stopped being "near expiry"
    # the moment the shipped dial moved to 24 h.
    later = dict(kwargs, now=NOW + datetime.timedelta(hours=2.75 * _seed_cycle_hours()))
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
    # ⛔ CONTRACT CHANGED 2026-08-27, DECLARED in amendments.jsonl, and this assertion is STRICTER
    # than the one it replaces rather than looser: it now pins BOTH gates instead of one.
    # This scenario reds `advancing_live_work`, which is ADVISORY — a cycle that runs and advances a
    # route is its cure, so stopping the loop over it is a death spiral. `--check` is
    # `research-loop` §1's stop condition and must let the cycle start; `--check-any` still answers
    # "is anything red at all".
    assert health.main(argv + ["--check"]) == 0, (
        "an advisory red stops the loop — this is the 2026-08-27 outage, in which a red board about "
        "immutable history left the driver pushing 'health check permanently red, needs your call'"
    )
    assert health.main(argv + ["--check-any"]) == 1, "the any-red gate stopped reporting"
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
    assert (len(written["conditions"]) == len(health.CONDITION_ORDER)
            and written["_stale_after_means"])


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
    fabricated denominator underneath every utilisation reading the controller ever takes.

    ⛔⛔ THIS TEST USED TO ASSERT THE FACTORY DIALS AND WENT RED WHEN THE THROTTLE WORKED. Measured
    2026-09-01: it required `backoff_level == 0`, `cycle_interval_hours == 4` and
    `subagent_width == 5` of a file that is a LIVE CONTROL SURFACE, not a seed. trimcrae's budget
    hold of 2026-08-29 set exactly those dials to 2 / 24 / 1 — the hold doing its job — and this
    file has been red on `main` ever since (AUT-PD-191).
    ★ THE DIALS ARE STILL CHECKED, AND AGAINST A STRICTER AUTHORITY: an active `budget_hold`
    declares the posture it claims to have set, so the live dials must be AT LEAST AS TIGHT as that
    declaration. A loosened dial under an active hold now fails here, which the old assertion could
    not even express — it could only notice that the numbers were not the factory ones.
    ⚠ AND `last_limit_flip` IS NO LONGER REQUIRED TO BE NULL. It was populated deliberately by
    CYC-0088 from a child session's own `rate_limit_info`, and its own note records why that
    CONSTRAINS the loop and loosens nothing: `allowed_warning` is a verdict, not a quota. Demanding
    null was demanding that no observation had ever been made — CLAUDE.md §4's "an absent reading is
    not a reading of absence", inverted. What §9.2 actually forbids is a DENOMINATOR nobody
    measured, and that is what is asserted.
    """
    state = json.loads(STATE_JSON.read_text())
    assert state["_schema"] == "emc-autonomy-state/1"
    assert state["utilisation_denominator"] is None, (
        "a utilisation denominator appeared without a measured window. §9.2 requires UNKNOWN until "
        "one is observed; a number here is fabricated and sits underneath every later reading.")
    assert "UNKNOWN" in state["_utilisation_denominator_means"]
    flip = state.get("last_limit_flip")
    assert flip is None or (isinstance(flip, dict) and flip.get("source") and flip.get("utc")), (
        "`last_limit_flip` is populated but names no source or no time, so it is a claim about an "
        "outside system with no reading behind it")

    # The dials themselves: every one present and of the right kind, whatever a hold has set them to.
    for key in ("backoff_level", "cycle_interval_hours", "subagent_width", "items_per_cycle"):
        assert isinstance(state.get(key), int) and state[key] >= 0, (
            f"`{key}` is {state.get(key)!r}. Three health conditions read these dials, and a seed "
            "that stops carrying one makes them unmeasurable rather than red.")
    assert state["utilisation_target"] == 0.8

    hold = state.get("budget_hold") or {}
    if hold.get("active"):
        # ⛔ A HOLD THAT GOVERNS NOTHING IS `subagent_width` ALL OVER AGAIN. The declaration names
        # ceilings; the live dials must sit at or under them, and `floor_backoff_level` is a floor.
        posture = hold.get("declared_posture") or {}
        for dial, ceiling in (("cycle_interval_hours", "max_cycle_interval_hours"),
                              ("subagent_width", "max_subagent_width"),
                              ("items_per_cycle", "max_items_per_cycle")):
            cap = posture.get(ceiling)
            if cap is not None:
                assert state[dial] <= cap, (
                    f"budget_hold declares {ceiling} = {cap} and the live `{dial}` is "
                    f"{state[dial]} — looser than the hold it is meant to be under.")
        floor = hold.get("floor_backoff_level")
        if floor is not None:
            assert state["backoff_level"] >= floor, (
                f"budget_hold declares floor_backoff_level {floor} and the live `backoff_level` is "
                f"{state['backoff_level']} — the hold is recorded and not enforced.")


def test_it_runs_against_the_real_repository_without_asserting_a_verdict(health):
    """⚠ SHAPE ONLY, ON PURPOSE. research/autonomy/ is written by the loop, so asserting a verdict here
    would make this suite go red on an unrelated commit — the clock-dependent-test defect recorded in
    fleet_armed.state's docstring. What is worth binding is that the real files still PARSE into a
    board with one row per DECLARED condition."""
    board = health.build(now=NOW)
    assert len(board["conditions"]) == len(health.CONDITION_ORDER)
    assert isinstance(board["ok"], bool) and isinstance(board["fully_measured"], bool)
    assert health.render(board, NOW).startswith("[loop-health]")


def test_an_empty_ledger_is_a_measured_stall_not_a_quiet_week(health, tmp_path):
    """⛔ ADDED 2026-08-26 with the `queue_is_takeable` condition. A ledger that exists and holds no
    entries is not 'nothing to report' — it is a loop that will fire on schedule and do nothing,
    forever, while every other condition stays green. That is the stall this row exists to name."""
    board = health.build(**_lab(tmp_path, entries=[]))
    row = [c for c in board["conditions"] if c["key"] == "queue_is_takeable"][0]
    assert row["needs_attention"] is True and row["unmeasured"] is False
    assert row["verdict"] == "EMPTY-LEDGER"


def test_a_queue_where_everything_is_claimed_is_a_stall(health, tmp_path):
    """The commoner shape, and the one that actually happened: CYC-0003 left a claim standing and the
    queue's top item became untakeable. With every item owned there is nothing to pick up, and the
    loop looks busy while doing nothing."""
    entries = [{"id": "AUT-1", "state": "queued", "owner": "CYC-DEAD", "retry_budget": 3, "score": 5.0},
               {"id": "AUT-2", "state": "running", "owner": "CYC-DEAD", "retry_budget": 3, "score": 4.0}]
    board = health.build(**_lab(tmp_path, entries=entries))
    row = [c for c in board["conditions"] if c["key"] == "queue_is_takeable"][0]
    assert row["needs_attention"] is True
    assert row["verdict"] == "NOTHING-TAKEABLE"


# ─────────────────────────────────────────────── the gate verdict `health.py` cannot measure itself
#
# ⛔ `gates_green` was `unmeasured` on EVERY board this loop had ever written, because nothing
# supplied the verdict `health.py` takes as a file. `research/autonomy/gates_verdict.py` is the
# caller that reads it, and it lives outside `health.py` so that `health.py` keeps its no-network
# property — the one that makes it work when everything else has stopped. These guard the DECISION,
# which is pure; the fetch is one urllib call with nothing to test that a mock would not invent.


def _gv():
    spec = importlib.util.spec_from_file_location(
        "gates_verdict", REPO / "research" / "autonomy" / "gates_verdict.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(conclusion, created, sha="a" * 40):
    return {"status": "completed", "conclusion": conclusion, "created_at": created,
            "updated_at": created, "head_sha": sha, "html_url": "https://example/run"}


def test_a_green_trunk_reports_green_with_no_red_since():
    v = _gv().decide([_run("success", "2026-08-26T20:00:00Z")], NOW)
    assert v["ok"] is True and v["red_since_utc"] is None


def test_a_red_trunk_ages_on_the_OLDEST_contiguous_failure():
    """⛔ THE ONE THAT MATTERS. Every push makes a new run, so dating the redness from the LATEST
    failure resets the clock on every commit — and a trunk red for three days reports as red for
    minutes, forever inside `GATES_RED_GRACE_H`. The grace window would then never expire and
    `gates_green` could never go RED-STUCK, which is the entire point of the condition."""
    runs = [_run("failure", "2026-08-26T20:00:00Z"),
            _run("failure", "2026-08-26T14:00:00Z"),
            _run("failure", "2026-08-24T09:00:00Z"),
            _run("success", "2026-08-24T08:00:00Z"),
            _run("failure", "2026-08-20T01:00:00Z")]
    v = _gv().decide(runs, NOW)
    assert v["ok"] is False
    assert v["red_since_utc"] == "2026-08-24T09:00:00Z", (
        "aged on the wrong run — it must be the oldest failure since the last SUCCESS, not the "
        "newest failure and not the oldest failure in the window"
    )


def test_an_all_red_window_says_its_age_is_a_lower_bound():
    """An absent reading is not a reading of absence (CLAUDE.md §4). With no success in the window,
    the redness may predate it, and a `red_since` presented as exact would understate the outage."""
    v = _gv().decide([_run("failure", "2026-08-26T20:00:00Z"),
                      _run("failure", "2026-08-25T20:00:00Z")], NOW)
    assert v["red_since_utc"] == "2026-08-25T20:00:00Z"
    assert "LOWER BOUND" in v["detail"]


def test_cancelled_and_skipped_are_not_verdicts():
    """A cancelled run says the trunk was never tested — not that it passed. This repository cancels
    runs by concurrency group routinely, so reading one as green would report a green trunk from a
    run that executed no test at all."""
    gv = _gv()
    runs = [{"status": "completed", "conclusion": "cancelled", "created_at": "2026-08-26T21:00:00Z"},
            _run("failure", "2026-08-26T20:00:00Z")]
    v = gv.decide(runs, NOW)
    assert v["ok"] is False, "a cancelled run masked the failure beneath it"


def test_an_in_progress_run_is_not_a_verdict_either():
    gv = _gv()
    runs = [{"status": "in_progress", "conclusion": None, "created_at": "2026-08-26T21:00:00Z"},
            _run("success", "2026-08-26T20:00:00Z")]
    assert gv.decide(runs, NOW)["ok"] is True


def test_no_graded_run_writes_NO_VERDICT_rather_than_a_guess():
    """⛔ FAIL CLOSED. `gates_green` is what stops a cycle committing onto a red trunk, so a guessed
    green is strictly worse than the `unmeasured` it replaces: it sends every cycle into the gate
    failure the condition exists to spare it."""
    v = _gv().decide([], NOW)
    assert "_no_verdict" in v and "ok" not in v


def test_the_verdict_shape_is_the_one_health_py_reads():
    """The two files are coupled only by this dict's keys, and a rename on either side would leave
    `gates_green` silently unmeasured forever — the exact state this pair was built to end."""
    health = _import_health()
    v = _gv().decide([_run("failure", "2026-08-26T20:00:00Z")], NOW)
    row = health.c_gates_green(v, None, NOW)
    assert row["key"] == "gates_green"
    assert row.get("unmeasured") is not True, "health.py could not read the verdict this writes"


def test_the_tick_actually_passes_the_verdict_to_every_health_call():
    """A verdict computed and not passed measures nothing. All three `health.py` invocations in the
    tick must receive it, or the board, the summary and the commit decision disagree about whether
    the trunk is green."""
    tick = (REPO / ".github" / "workflows" / "autonomy-tick.yml").read_text()
    assert "gates_verdict.py" in tick, "nothing computes the verdict"
    assert "actions: read" in tick, "the fetch has no permission to read Actions"
    calls = [ln for ln in tick.splitlines()
             if "health.py" in ln and "--" in ln and not ln.strip().startswith("#")]
    assert len(calls) == 3, f"expected 3 health.py invocations, found {len(calls)}: {calls}"
    for ln in calls:
        idx = tick.index(ln)
        assert "--gates-verdict" in tick[idx:idx + 400], f"no --gates-verdict for: {ln.strip()}"


def test_the_tick_also_passes_the_stall_verdict_to_every_health_call():
    """★ AUT-PROP-029's SAME REGRESSION, ONE FLAG LATER. `stalls_are_named` is exactly as unmeasured
    as `gates_green` was until the gate-verdict pair above existed — a caller-supplied file health.py
    cannot produce for itself. Written as its own test, deliberately not folded into the one above, so
    a future third verdict this shape is added under gets its own guard rather than silently riding
    the coattails of a check that says nothing about it."""
    tick = (REPO / ".github" / "workflows" / "autonomy-tick.yml").read_text()
    assert "stuck_clock.py" in tick, "nothing computes the stall verdict"
    assert "--check --json" in tick, "the stall verdict must be the machine-readable form"
    calls = [ln for ln in tick.splitlines()
             if "health.py" in ln and "--" in ln and not ln.strip().startswith("#")]
    assert len(calls) == 3
    for ln in calls:
        idx = tick.index(ln)
        assert "--stall-verdict" in tick[idx:idx + 400], f"no --stall-verdict for: {ln.strip()}"


# ──────────────────────────────────── the session-shape rule, which failed by being UNREACHABLE
#
# ⛔⛔ THE FAILURE THIS BLOCK GUARDS IS THE MOST INSTRUCTIVE ONE THE LOOP HAS PRODUCED, BECAUSE THE
# RULE WAS NEVER WRONG AND WAS NEVER IGNORED — IT WAS NEVER REACHED. `.claude/skills/research-loop/
# SKILL.md` §3 has always said a full hardening cycle is a SPAWNED session. A skill binds only when
# it is loaded, and every one of that skill's load triggers was a Routine firing a cycle. On the
# INTERACTIVE path — a human asking for research work directly — the skill never loaded, so §3 never
# applied. Measured in the offending session's own transcript: `"name":"Skill"` appears 0 times,
# while that session ran two full cycles, compacted 23 times and reached 7.6 MB.
#
# The repair has two halves and BOTH are guarded here, because either alone regresses:
#   REACHABILITY  the rule is now also in CLAUDE.md, which loads every session, interactive included.
#   ENFORCEMENT   `cycles_are_sized` measures it. A rule nothing measures decays to a suggestion —
#                 the lease and the stall alarm each have a suite behind them and §3 had nothing.


def _sess_receipt(cycle_id, session_id):
    return {"cycle_id": cycle_id, "session_id": session_id}


def _state(cap=2):
    return {"max_cycles_per_session": cap}


def test_a_session_over_the_cap_goes_red(health):
    row = health.c_cycles_are_sized(
        [_sess_receipt("CYC-1", "sess-A"), _sess_receipt("CYC-2", "sess-A"), _sess_receipt("CYC-3", "sess-A")],
        _state(2), None)
    assert row["needs_attention"] is True
    # ⚠ Renamed 2026-08-27 when the row began measuring the ACTION rather than the count:
    # SESSION-OVERLOADED -> SESSION-OVERLOADED-NO-HANDOFF. Asserted by prefix so the meaning is
    # pinned and a future qualifier does not break a test that still holds.
    assert row["verdict"].startswith("SESSION-OVERLOADED")
    assert "NO-HANDOFF" in row["verdict"], (
        "the verdict no longer says WHY it is red — over the cap is not the defect; over the cap "
        "with no successor started is"
    )
    assert "CYC-3" in row["detail"]


REFUSAL = ("create_session: caller session is at lineage depth 8 (limit 8); cannot spawn or "
           "re-arm further child sessions")


def test_a_refused_handoff_is_unmeasured_not_red(health):
    """⛔⛔ AUT-PD-032, MEASURED 2026-08-27. `create_session` refuses at a lineage depth limit, so
    §3's remedy — "hand off the same way you were started" — DOES NOT EXIST at the end of a spawn
    chain, and the deeper the loop has run unattended the more certainly it fails. The session that
    hit it built the successor prompt with handoff.py, made the call, and was refused.

    ★ Grading that RED made this row exactly what its own source comment warns against: "a condition
    that cannot be satisfied by doing the right thing ... is a stopwatch, not a guard." No future
    cycle could clear it — the LATCHING shape RECEIPT_WINDOW was added to fix, through another door.
    """
    receipts = [_sess_receipt("CYC-1", "sess-A"), _sess_receipt("CYC-2", "sess-A"),
                {"cycle_id": "CYC-3", "session_id": "sess-A",
                 "handoff": {"child_session_id": None, "refused_by": REFUSAL}}]
    row = health.c_cycles_are_sized(receipts, _state(2), None)
    assert row["unmeasured"] is True, "a refused handoff was graded as a defect in the session"
    assert row["needs_attention"] is False
    assert row["verdict"] == "HANDOFF-REFUSED"
    assert "lineage depth" in row["detail"], (
        "the platform's own words are not in the detail, so a reader cannot tell a real ceiling "
        "from an excuse")


def test_a_refused_handoff_is_never_graded_GREEN(health):
    """⛔ THE DIRECTION THAT WOULD HAVE BEEN EASIER AND IS WRONG. No successor exists, so the work
    did NOT continue in a fresh context. Green would assert the rule was satisfied; the honest
    reading is that the loop cannot be graded on this because the mechanism was gone."""
    receipts = [_sess_receipt("CYC-1", "sess-A"), _sess_receipt("CYC-2", "sess-A"),
                {"cycle_id": "CYC-3", "session_id": "sess-A",
                 "handoff": {"refused_by": REFUSAL}}]
    row = health.c_cycles_are_sized(receipts, _state(2), None)
    assert row["ok"] is False, "a refused handoff was graded as though the rule had been satisfied"


def test_an_unrecorded_refusal_is_still_red(health):
    """⛔⛔ THE INTEGRITY OF THE WHOLE EXEMPTION. If an ABSENT refusal record earned the downgrade,
    'I could not' would be a free pass claimable by any session that simply never tried. The
    platform's verbatim words are what distinguishes a real ceiling from an excuse."""
    receipts = [_sess_receipt("CYC-1", "sess-A"), _sess_receipt("CYC-2", "sess-A"),
                {"cycle_id": "CYC-3", "session_id": "sess-A", "handoff": {"refused_by": "   "}}]
    row = health.c_cycles_are_sized(receipts, _state(2), None)
    assert row["needs_attention"] is True
    assert "NO-HANDOFF" in row["verdict"]


def test_a_real_handoff_still_beats_a_refusal(health):
    """A session that actually spawned a successor is GREEN, not merely unmeasured — the remedy
    working must outrank the remedy being unavailable, or there is no gradient to climb."""
    receipts = [_sess_receipt("CYC-1", "sess-A"), _sess_receipt("CYC-2", "sess-A"),
                {"cycle_id": "CYC-3", "session_id": "sess-A",
                 "handoff": {"child_session_id": "session_01CHILD"}}]
    row = health.c_cycles_are_sized(receipts, _state(2), None)
    assert row["ok"] is True and row["unmeasured"] is False


def test_a_refusal_on_a_session_that_is_not_over_cap_changes_nothing(health):
    """⚠ The exemption must be scoped to the row it exempts. A refusal recorded by a well-behaved
    session is irrelevant, and must not drag a green board into unmeasured."""
    receipts = [_sess_receipt("CYC-1", "sess-A"),
                {"cycle_id": "CYC-2", "session_id": "sess-B", "handoff": {"refused_by": REFUSAL}}]
    row = health.c_cycles_are_sized(receipts, _state(2), None)
    assert row["ok"] is True and row["unmeasured"] is False


def test_a_session_at_the_cap_is_green(health):
    """The cap is a cap, not a target. Two is allowed on purpose: slack for a cycle that turns out
    to have a small follow-on. Firing at two would make the row noise, and a noisy row gets muted."""
    row = health.c_cycles_are_sized(
        [_sess_receipt("CYC-1", "sess-A"), _sess_receipt("CYC-2", "sess-A")], _state(2), None)
    assert row["needs_attention"] is False


def test_cycles_spread_across_sessions_are_green(health):
    row = health.c_cycles_are_sized(
        [_sess_receipt("CYC-1", "sess-A"), _sess_receipt("CYC-2", "sess-B"), _sess_receipt("CYC-3", "sess-C")],
        _state(2), None)
    assert row["needs_attention"] is False
    assert row["payload"]["worst"] == 1


def test_an_unstamped_receipt_is_never_counted_as_a_fresh_session(health):
    """⛔ CLAUDE.md §4: an absent reading is not a reading of absence. If a receipt with no
    `session_id` counted as its own session, the way to turn this row green would be to stop
    stamping receipts — a gate whose cheapest defeat is omitting data is worse than no gate."""
    receipts = [_sess_receipt("CYC-1", "sess-A"), _sess_receipt("CYC-2", "sess-A"),
                _sess_receipt("CYC-3", None),
                _sess_receipt("CYC-4", "unknown -- fired by the UI-created Routine, no session_id")]
    row = health.c_cycles_are_sized(receipts, _state(2), None)
    assert row["payload"]["unstamped_receipts"] == ["CYC-3", "CYC-4"]
    assert row["payload"]["sessions"] == {"sess-A": 2}


def test_no_stamped_receipt_at_all_is_unmeasured_not_green(health):
    row = health.c_cycles_are_sized([_sess_receipt("CYC-1", None)], _state(2), None)
    assert row["unmeasured"] is True
    assert row["needs_attention"] is False


# ⛔⛔ THESE TWO ARE NAMED FOR THE CYCLE CAP BECAUSE FOR A WEEK THEY WERE NOT NAMED AT ALL, AND SO
# NEITHER OF THEM RAN. They were `test_an_unreadable_state_or_absent_cap_is_unmeasured_not_green`
# and `test_the_cap_is_read_from_state_and_never_typed_in_the_checker` — byte-identical names to the
# `c_fanout_is_governed` pair ~100 lines below, which are DIFFERENT tests about a DIFFERENT
# condition. Python binds a module-level name once, so the later definition silently replaced this
# one and pytest collected 75 tests from a file holding 77 function definitions.
# ⚠ MEASURED 2026-09-03 rather than reasoned: `ast` finds 77 `def test_`, `pytest --collect-only -q`
# reports 75. Nothing was red, nothing was skipped, and no report anywhere said a guard was missing
# — a shadowed test does not fail, it ceases to exist. ⛔ AND THE TIER BUDGET COUNTS THE SOURCE, so
# both were being PAID FOR out of a ceiling that stood at 1400/1400 while measuring nothing.
# ★ The two that died are the anti-defeat guard and the one-fact-one-place guard on
# `cycles_are_sized`, which is the row CLAUDE.md §6 added specifically because the session-shape
# rule was governed by nothing.
def test_an_unreadable_state_or_absent_cycle_cap_is_unmeasured_not_green(health):
    assert health.c_cycles_are_sized([_sess_receipt("C", "s")], None, "boom")["unmeasured"] is True
    assert health.c_cycles_are_sized([_sess_receipt("C", "s")], {}, None)["unmeasured"] is True
    assert health.c_cycles_are_sized([_sess_receipt("C", "s")], {"max_cycles_per_session": 0},
                                     None)["unmeasured"] is True


def test_the_cycle_cap_is_read_from_state_and_never_typed_in_the_checker(health):
    """One fact, one place. A cap hardcoded here could not be raised under backoff, and would
    disagree with the file the architecture names as its owner."""
    src = HEALTH_PY.read_text()
    body = src[src.index("def c_cycles_are_sized"):src.index("def c_budget_recovering")]
    assert 'state.get("max_cycles_per_session")' in body
    assert "max_cycles_per_session" in json.loads(STATE_JSON.read_text())


def test_the_condition_is_actually_wired_into_the_board(health):
    """⛔ THE MUTATION THIS BLOCK EXISTS FOR. A condition function that is never called is the exact
    shape of the failure being fixed: correct, present, and unreachable. Assert it reaches the board
    a reader actually sees, not merely that the function exists."""
    assert "cycles_are_sized" in health.CONDITION_ORDER
    src = HEALTH_PY.read_text()
    assert "c_cycles_are_sized(receipts, state, state_err)" in src, (
        "the condition is defined but not assembled into build()'s conditions list — it would never "
        "appear on a board, which is how §3 failed in the first place"
    )


# ──────────────────────────────────────────── the width cap, which governed nothing until it was read
#
# ⛔⛔ THIS DIAL WAS WORSE INSTRUMENTED THAN THE SESSION-SHAPE RULE ABOVE, AND IT CARRIES MORE RISK.
# `grep -rn subagent_width` over the whole repository returned TWO hits on 2026-08-26: the JSON that
# defines it, and one test asserting its value is 5. Nothing read it; no receipt recorded a dispatch.
# The session-shape rule was at least prose in a loadable skill — this was a NUMBER IN A STATE FILE
# CONNECTED TO NO CODE PATH, which is the purest form of a governed value that governs nothing.
#
# Architecture §9 on what it guards: a 107-agent fan-out hit the account weekly usage limit — 40
# completed, 67 errored, the synthesis step failed and returned a truncation artifact, the resumed run
# reached 102 and died on a container restart, and the findings were recovered by hand from
# journal.jsonl. "Width is the more important dial — the incident above was a WIDTH failure."


def _fan(cycle_id, width):
    return {"cycle_id": cycle_id, "session_id": "s", "subagents": {"max_concurrent": width}}


def test_a_fanout_over_the_cap_goes_red(health):
    row = health.c_fanout_is_governed([_fan("CYC-1", 9)], {"subagent_width": 5}, None)
    assert row["needs_attention"] is True
    assert row["verdict"] == "FANOUT-OVER-CAP"
    assert "never widen the cap" in row["detail"], (
        "the remedy text must not teach raising the cap to fit what was already spent — §8b.1e: a "
        "guard whose printed remedy is the wrong fix teaches the wrong fix"
    )


def test_a_fanout_at_the_cap_is_green(health):
    assert health.c_fanout_is_governed(
        [_fan("CYC-1", 5)], {"subagent_width": 5}, None)["needs_attention"] is False


def test_a_receipt_recording_no_dispatch_is_UNMEASURED_not_green(health):
    """⛔ THE DEFEAT THIS CLOSES. If a receipt with no `subagents` block counted as compliant, the
    cheapest route to a clean board would be to stop recording dispatches — a gate whose easiest
    defeat is omitting data measures only its own compliance. CLAUDE.md §4: an absent reading is not
    a reading of absence."""
    row = health.c_fanout_is_governed([{"cycle_id": "CYC-1", "session_id": "s"}],
                                      {"subagent_width": 5}, None)
    assert row["unmeasured"] is True
    assert row["needs_attention"] is False
    assert row["payload"]["receipts_not_recording_dispatch"] == ["CYC-1"]


def test_one_unrecorded_receipt_does_not_hide_a_recorded_overrun(health):
    """§8b.1a: a checker that reports state(group) and then reasons about a member has a defect. A
    mix of recorded and unrecorded receipts must still convict the recorded overrun."""
    row = health.c_fanout_is_governed(
        [{"cycle_id": "CYC-1", "session_id": "s"}, _fan("CYC-2", 40)],
        {"subagent_width": 5}, None)
    assert row["verdict"] == "FANOUT-OVER-CAP" and "CYC-2" in row["detail"]


def test_an_unreadable_state_or_absent_cap_is_unmeasured_not_green(health):
    assert health.c_fanout_is_governed([_fan("C", 1)], None, "boom")["unmeasured"] is True
    assert health.c_fanout_is_governed([_fan("C", 1)], {}, None)["unmeasured"] is True


def test_the_cap_is_read_from_state_and_never_typed_in_the_checker(health):
    """One fact, one place — and specifically so the backoff ladder (5 → 2 → 1) actually moves it. A
    hardcoded 5 here would keep the gate at full width while the governor was throttling."""
    src = HEALTH_PY.read_text()
    body = src[src.index("def c_fanout_is_governed"):src.index("def c_budget_recovering")]
    assert 'state.get("subagent_width")' in body
    assert "subagent_width" in json.loads(STATE_JSON.read_text())


def test_the_unit_of_the_cap_is_written_down(health):
    """⛔ IT WAS UNENFORCEABLE, NOT MERELY UNENFORCED, UNTIL THIS EXISTED. A cap of '5' says nothing
    until you say five of what — concurrent agents, or a serial total, or agents per item. Two
    readings of one number is how a gate and its subject quietly disagree."""
    state = json.loads(STATE_JSON.read_text())
    means = state.get("_subagent_width_means", "")
    assert "CONCURRENT" in means.upper(), "the unit is still undefined"
    assert "SERIAL" in means.upper() or "serially" in means, (
        "the dial's LIMIT must be stated too — a serial total is not governed by a concurrency cap, "
        "and leaving that unsaid lets the row read as broader assurance than it is"
    )


def test_the_condition_is_wired_into_the_board(health):
    assert "fanout_is_governed" in health.CONDITION_ORDER
    assert "c_fanout_is_governed(receipts, state, state_err)" in HEALTH_PY.read_text(), (
        "defined but not assembled into build() — it would never reach a board, which is the exact "
        "shape of the defect being fixed"
    )


# ═══════════════════════════════════ THE INVARIANT THAT DID NOT EXIST, AND WHOSE ABSENCE KILLED THE LOOP
#
# ⛔⛔ 2026-08-27. The driver Routine fired, read a red board, refused to start, and pushed
# "Research loop refused to start this cycle: health check permanently red, needs your call."
# It was right: the board WAS permanently red, and no cycle in any session could ever have cleared it.
#
# THE MECHANISM, and it is a design error rather than a coding one. `research-loop` §1 says a cycle
# REFUSES TO START while any §5.2 condition is red. Every condition written before that day happened
# to be one a cycle could act on — run and write a receipt, add the missing observation, release a
# stale claim, fix the trunk — so the rule held BY LUCK, not by design. Then two conditions were added
# whose subject is IMMUTABLE COMMITTED HISTORY: `cycles_are_sized` and `fanout_is_governed` both read
# every receipt ever written. Simulated before the fix: fifty consecutive well-behaved sessions left
# both rows red. A stop condition keyed to history that cannot change is an outage with a virtuous
# name.
#
# ★★ AND THE SECOND FAILURE IS THE ONE THESE TESTS EXIST FOR. The author of both conditions read that
# red row a dozen times, wrote "I left it red on purpose" three separate times, and never once asked
# what CONSUMES the board. The consumer was documented, in the skill that was loaded, one section
# above the contract being followed. Nothing measured the difference between "a red a cycle can act
# on" and "a red that stops the loop forever", so nothing could catch it.
#
# TWO THINGS ARE GUARDED HERE, and the second matters more than the first:
#   1. those two conditions are windowed, so good behaviour clears them;
#   2. EVERY condition declares what its red does to the loop, and no advisory red can ever wedge it.


def test_every_condition_declares_what_its_red_does_to_the_loop(health):
    """⛔ THE MISSING CONTRACT, NOW EXPLICIT. A condition with no declared class defaults to `blocks`,
    which is the safe direction — but it must be a CHOICE, made where the condition is registered,
    not a default nobody noticed."""
    assert set(health.CONDITION_ON_RED) == set(health.CONDITION_ORDER), (
        "a condition exists with no declared on_red class (or vice versa) — that is the state in "
        "which the next retrospective condition silently becomes a permanent outage"
    )
    assert set(health.CONDITION_ON_RED.values()) <= {"blocks", "redirects", "advises"}


def test_only_a_blocking_red_stops_a_cycle(health, tmp_path):
    """The stop condition `research-loop` §1 actually runs. Before 2026-08-27 `--check` returned 1 for
    ANY red, so an advisory row about last week's session count stopped this week's research."""
    board = health.build(**_lab(tmp_path))
    for c in board["conditions"]:
        if c["needs_attention"] and c["on_red"] != "blocks":
            assert c["key"] not in board["blocking"]
    assert set(board["blocking"]) <= set(board["needs_attention"])


def test_a_red_advisory_condition_does_not_wedge_the_loop(health, tmp_path):
    """★ THE REGRESSION TEST FOR THE ACTUAL OUTAGE. Force the exact condition that fired — an
    over-cap session — and assert the loop's own stop check still lets a cycle start."""
    lab = _lab(tmp_path)
    over = [_sess_receipt(f"CYC-{i}", "one-session") for i in range(1, 6)]
    board = health.build(**{**lab, "receipts": over}) if "receipts" in lab else None
    if board is None:                       # _lab builds receipts from disk; write them instead
        rd = tmp_path / "receipts"; rd.mkdir(exist_ok=True)
        for i, r in enumerate(over):
            (rd / f"CYC-{i}.json").write_text(json.dumps(r))
        board = health.build(**{**lab, "receipts_dir": str(rd)}) if "receipts_dir" in lab else None
    if board is not None:
        assert "cycles_are_sized" in board["needs_attention"], "the scenario did not reproduce"
        assert "cycles_are_sized" not in board["blocking"], (
            "an over-cap session STOPS THE LOOP — this is the 2026-08-27 outage, restored"
        )


def test_the_retrospective_conditions_are_not_latched(health):
    """⛔ LATCH PROBE. Feed each a bad receipt followed by a window of good ones and require green.
    Before the fix this failed for both: their subject is committed history, so the red was permanent
    and fifty clean sessions did not move it."""
    state = {"max_cycles_per_session": 2, "subagent_width": 5}
    bad_size = [_sess_receipt(f"CYC-{i}", "one-session") for i in range(5)]
    good = [{"cycle_id": f"CYC-G{i}", "session_id": f"spawned-{i}",
             "subagents": {"max_concurrent": 1}} for i in range(health.RECEIPT_WINDOW)]
    assert health.c_cycles_are_sized(bad_size, state, None)["needs_attention"] is True
    assert health.c_cycles_are_sized(bad_size + good, state, None)["needs_attention"] is False, (
        "cycles_are_sized is LATCHED — no amount of good behaviour clears it, so the row is a "
        "permanent outage and, once ignored, takes every other row's credibility with it"
    )
    bad_fan = [{"cycle_id": "CYC-B", "session_id": "s", "subagents": {"max_concurrent": 40}}]
    assert health.c_fanout_is_governed(bad_fan, state, None)["needs_attention"] is True
    assert health.c_fanout_is_governed(bad_fan + good, state, None)["needs_attention"] is False, (
        "fanout_is_governed is LATCHED — the same defect as its sibling, written the same hour"
    )


def test_every_receipt_reading_condition_declares_how_it_recovers(health):
    """★ THE CLASS, NOT THE INSTANCE (`paper-hardening` §8b.2). Both latched conditions were written in
    one sitting and both were missed; a guard naming only those two regresses at the third.

    ⚠ THE FIRST VERSION OF THIS GUARD SCRAPED health.py's SOURCE for slicing patterns and got two of
    four wrong — it accused `advancing_live_work` and `authority_respected`, both of which recover
    fine, and would have had someone "fix" two things that were never broken. A property inferred from
    code shape is a property nobody has stated. So the declaration is the contract."""
    src = HEALTH_PY.read_text()
    reads_receipts = [k for k in health.CONDITION_ORDER
                      if f"def c_{k}(receipts" in src]
    undeclared = [k for k in reads_receipts if k not in health.RECEIPT_SCOPE]
    assert not undeclared, (
        f"{undeclared} read receipts and do not say how their red ever clears. Receipts are immutable "
        "committed history: a condition that reads all of it latches, and a latched red is a "
        "permanent outage — the 2026-08-27 failure exactly."
    )
    for k, how in health.RECEIPT_SCOPE.items():
        assert how in ("windowed", "newest-run") or how.startswith("cleared-by:"), k
        if how.startswith("cleared-by:"):
            path = REPO / how.split(":", 1)[1]
            assert path.exists(), f"{k} names {path} as its recovery path and that file does not exist"


def test_check_and_check_any_are_different_gates(health):
    """⚠ `--check-any` was first written nested inside `if a.check:`, so it did nothing unless both
    flags were passed — a flag that reports while measuring nothing, caught on its first run. The two
    gates must answer different questions and both must actually be reachable."""
    src = HEALTH_PY.read_text()
    i, j = src.index("if a.check_any:"), src.index("if a.check:")
    assert i > j, "--check-any is nested inside --check again; it will silently never fire"
    assert 'board.get("blocking")' in src and 'board["needs_attention"]' in src


# ══════════════════════════════════ THE HANDOFF — three layers of knowing, and nothing that could act
#
# ⛔⛔ THE LOOP KNEW IT NEEDED A NEW SESSION AND HAD NOTHING THAT COULD START ONE. The founding brief
# asked for "proper usage of new session creation to manage context". `research-loop` §3 said a full
# hardening cycle is a SPAWNED session. `cycles_are_sized` measured when a session had run too long.
# Three layers of knowing — and no mechanism. So the session that hit the cap wrote "the next cycle
# should be a fresh session" in its final message and STOPPED: a manual step, parked in the middle of
# a loop whose entire purpose is that no manual step exists.
#
# ★ AND THE CONDITION ITSELF WAS PART OF THE PROBLEM. Its first version counted cycles and nothing
# else, so the only route to green was to WAIT for the window to slide — performing the rule's own
# remedy moved the row not at all. A guard that cannot be satisfied by doing the right thing is a
# stopwatch, not a guard. It now measures the ACTION: a recorded `handoff.child_session_id`, which is
# evidence only a real session-creation call can produce.


def _capped(n=5, session="sess-A", handoff=None):
    rs = [{"cycle_id": f"C{i}", "session_id": session} for i in range(n)]
    if handoff is not None:
        rs[-1] = {**rs[-1], "handoff": handoff}
    return rs


def test_an_over_cap_session_that_handed_off_is_green(health):
    """★ THE POINT. The remedy the row prints must be the thing that clears it."""
    st = {"max_cycles_per_session": 2}
    assert health.c_cycles_are_sized(_capped(), st, None)["verdict"] == "SESSION-OVERLOADED-NO-HANDOFF"
    ok = health.c_cycles_are_sized(_capped(handoff={"child_session_id": "session_01ABC"}), st, None)
    assert ok["needs_attention"] is False, (
        "spawning the successor — the exact act §3 demands — did not move the row. A condition that "
        "cannot be satisfied by obeying it teaches nothing."
    )


def test_a_handoff_with_no_child_id_does_not_count(health):
    """⛔ THE CHEAP DEFEAT, CLOSED. If an empty `handoff` block satisfied the row, the way to a green
    board would be to write the field rather than start the session — a gate measuring its own
    paperwork. Only a real child session id counts, and only a real create_session call produces one."""
    st = {"max_cycles_per_session": 2}
    for bogus in ({}, {"child_session_id": ""}, {"child_session_id": "   "}, {"child_session_id": None}):
        row = health.c_cycles_are_sized(_capped(handoff=bogus), st, None)
        assert row["needs_attention"] is True, f"an empty handoff satisfied the row: {bogus!r}"


def test_a_handoff_does_not_excuse_a_DIFFERENT_session(health):
    """One session's successor is not another's. Crediting any handoff anywhere would let a single
    spawn cover every over-cap session in the window."""
    st = {"max_cycles_per_session": 2}
    mixed = _capped(session="sess-A") + [
        {"cycle_id": "D0", "session_id": "sess-B", "handoff": {"child_session_id": "session_01XYZ"}}]
    row = health.c_cycles_are_sized(mixed, st, None)
    assert row["needs_attention"] is True
    assert "sess-A" in row["detail"], "the wrong session was credited with sess-B's handoff"


def test_the_remedy_text_names_the_command_that_performs_it(health):
    """§8b.1e: a guard whose printed remedy is the wrong fix teaches the wrong fix. This one must name
    the generator, because a handoff prompt WRITTEN FROM MEMORY is written from the context that is
    running out — the very thing being discarded."""
    row = health.c_cycles_are_sized(_capped(), {"max_cycles_per_session": 2}, None)
    assert "handoff.py" in row["detail"]
    assert "child_session_id" in row["detail"]


def test_the_handoff_prompt_is_generated_from_committed_state(health):
    """⚠ NOT typed by the outgoing session. Every fact in it is read from a committed artifact, so the
    successor re-reads the same files and finds them unchanged — CLAUDE.md's 'state lives in git,
    never in context', applied at the one moment context is discarded on purpose."""
    spec = importlib.util.spec_from_file_location(
        "handoff", REPO / "research" / "autonomy" / "handoff.py")
    ho = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ho)

    ledger = {"entries": [
        {"id": "AUT-TOP", "score": 99.0, "kind": "harden", "what": "the top item", "retry_budget": 3},
        {"id": "AUT-OWNED", "score": 100.0, "kind": "harden", "what": "claimed", "retry_budget": 3,
         "owner": "CYC-X"},
        {"id": "AUT-SPENT", "score": 100.0, "kind": "harden", "what": "no budget", "retry_budget": 0},
    ]}
    top = ho.top_items(ledger)
    assert [e["id"] for e in top] == ["AUT-TOP"], (
        "the successor was handed an item that is owned or out of retry budget — its first act would "
        "be discovering that, which is the cost the ledger exists to remove"
    )
    prompt = ho.build(reason="because", ledger=ledger, state={"max_cycles_per_session": 2})
    assert "FRESH SESSION" in prompt and "because" in prompt
    assert "research-loop" in prompt, "the successor is not pointed at the cycle contract"
    assert "handoff.py" in prompt, (
        "the successor is not told to hand off in turn — a chain that stops after one link is a "
        "longer fuse, not an automated loop"
    )
    assert "re-score" in prompt.lower() or "RE-SCORE" in prompt, (
        "the queue must be handed over as a POINTER, not as a plan the successor follows blindly"
    )
