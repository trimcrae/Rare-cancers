"""⛔⛔ A RECEIPT WHOSE CLOCK THE READER CANNOT SEE MUST NEVER PRODUCE A CONFIDENT `LATE`.

⚠ MEASURED 2026-09-02. `health.py:c_cycle_delivering` reported `LATE — the last receipt is 103.5 h
old against a 48.0 h deadline` for seven consecutive board runs. TWELVE receipts had been delivered
inside the window it called empty; the newest was 2.7 h old and on `origin/main`. The loop was fine
and the instrument was wrong.

THE MECHANISM, in one sentence: every receipt from CYC-0084 on carried `started_utc` and none of
`health.RECEIPT_TIME_KEYS`, so `_receipt_ts_raw` returned None for all fifteen, the
`(timestamp or "", filename)` sort put them at the FRONT of the list, and `receipts[-1]` resolved to
the newest receipt still using the OLD spelling — four days stale.

⭐ IT WAS OMISSION, NOT A REDESIGN, and that is why the fix is a governed field rather than a second
accepted spelling: `SKILL.md` had never named a receipt clock in any of its 25 versions, and the two
spellings INTERLEAVED within the same hours (CYC-0084-e2d78138 `utc` 09:20Z, CYC-0084-6b009680
`started_utc` 09:26Z) instead of switching over.

⛔ THE SECOND VICTIM IS THE POINT OF THE SHARED HELPER. `c_advancing_live_work` reads the same tail
and printed NOT-ADVANCING off CYC-0082/0083/0084 — all `route_advanced: none` — while the real
newest three were RT-ASO, none, RT-ASO, which is GREEN. One field name, two false reds.

⛔ AND THE GUARD MUST NOT LATCH, which is the trap the first draft of this fix walked into. "Any
clockless receipt anywhere -> unmeasured" would freeze both rows forever, because those fifteen
receipts are immutable committed history — precisely the failure that killed the loop on
2026-08-27 (`cycles_are_sized`). The guard is therefore scoped by CYCLE ORDINAL, a recency proxy
read from the id rather than the clock, and `test_the_guard_recovers_when_receipts_comply` is the
assertion that it lets go.
"""
from __future__ import annotations

import copy
import datetime
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUT = os.path.dirname(HERE)
sys.path.insert(0, AUT)

import contract_check   # noqa: E402
import health           # noqa: E402
import receipt_schema   # noqa: E402

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 9, 2, 16, 14, tzinfo=UTC)
INTERVAL_H = 24.0


def _r(n, *, ended=None, legacy=None, route="RT-ASO", suffix="seat"):
    """A receipt as `load_receipts` yields one: `_file`/`_path` attached, clock optional."""
    rid = f"CYC-{n:04d}-{suffix}"
    doc = {
        receipt_schema.CYCLE_ID_KEY: rid,
        receipt_schema.ROUTE_ADVANCED_KEY: route,
        receipt_schema.CCR_ID_KEY: "session_01ClockRegression",
        receipt_schema.BLOCK_KEY: {receipt_schema.WIDTH_KEY: 0},
        "_file": f"{rid}.json",
        "_path": f"/nowhere/{rid}.json",
    }
    if ended is not None:
        doc[receipt_schema.ENDED_KEY] = ended
    if legacy is not None:
        doc["utc"] = legacy
    return doc


def _sorted(receipts):
    """`load_receipts`' ordering, reproduced exactly — the sort IS half the defect."""
    return sorted(receipts, key=lambda r: (health._receipt_ts_raw(r) or "", r["_file"]))


# ── the defect itself ────────────────────────────────────────────────────────────────────────────

def test_a_stale_datable_receipt_is_not_aged_when_a_newer_one_is_undatable():
    """⛔ THE 2026-09-02 BOARD, RECONSTRUCTED. The exact shape that printed `LATE ... 103.5 h`."""
    receipts = _sorted([
        _r(83, legacy="2026-08-29T08:45:00Z", route="none"),
        _r(84, legacy="2026-08-29T08:45:00Z", route="none", suffix="e2d78138"),
        _r(90, suffix="d7df5340"),                       # started_utc only -> undatable
        _r(91, suffix="91c8e949"),                       # started_utc only -> undatable
    ])
    assert receipts[-1]["_file"] == "CYC-0084-e2d78138.json", "the sort must still put it here"

    row = health.c_cycle_delivering(receipts, [], INTERVAL_H, NOW)
    assert row["unmeasured"] is True, "an undatable newer receipt must not yield a measured verdict"
    assert row["ok"] is False
    assert row["verdict"] == "RECEIPT-TIME-UNREADABLE"
    assert "LATE" not in row["verdict"]
    assert row["payload"]["undatable_receipts"] == 2


def test_the_undatable_receipts_are_named_not_merely_counted():
    """CLAUDE.md §4: an unmeasured row must name what would settle it, and on which files."""
    receipts = _sorted([_r(84, legacy="2026-08-29T08:45:00Z"), _r(91, suffix="91c8e949")])
    row = health.c_cycle_delivering(receipts, [], INTERVAL_H, NOW)
    assert "CYC-0091-91c8e949.json" in row["detail"]
    assert receipt_schema.ENDED_KEY in row["detail"]


def test_advancing_live_work_refuses_the_same_shadowed_window():
    """⛔ THE SECOND FALSE RED. The real newest three were RT-ASO/none/RT-ASO — not a run of three."""
    receipts = _sorted([
        _r(82, legacy="2026-08-29T08:00:00Z", route="none"),
        _r(83, legacy="2026-08-29T08:45:00Z", route="none"),
        _r(84, legacy="2026-08-29T08:45:00Z", route="none", suffix="e2d78138"),
        _r(90, route="RT-ASO", suffix="d7df5340"),
        _r(91, route="RT-ASO", suffix="91c8e949"),
    ])
    row = health.c_advancing_live_work(receipts, NOW)
    assert row["unmeasured"] is True, "a window that is not provably the newest run is not a finding"
    assert row["verdict"] == "WINDOW-NOT-PROVABLY-NEWEST"
    assert row["needs_attention"] is False, "an unreadable window must not be reported as documentation drift"


# ── the guard must let go ────────────────────────────────────────────────────────────────────────

def test_the_guard_recovers_when_receipts_comply():
    """⛔⛔ NON-LATCHING, AND THIS IS THE ASSERTION THAT MAKES THE DESIGN HONEST.

    The fifteen clockless receipts on the trunk can never be fixed — they are committed history. A
    guard keyed to their existence would be permanently red, which is the muted-alarm failure
    `health.py`'s own docstring records. Newer compliant receipts must clear both rows unaided.
    """
    old_clockless = [_r(n, suffix="legacy") for n in (74, 84, 90, 91)]
    fresh = [_r(94, ended="2026-09-02T15:00:00Z", route="RT-ASO"),
             _r(95, ended="2026-09-02T15:30:00Z", route="none"),
             _r(96, ended="2026-09-02T16:00:00Z", route="RT-EMC")]
    receipts = _sorted(old_clockless + fresh)

    deliver = health.c_cycle_delivering(receipts, [], INTERVAL_H, NOW)
    assert deliver["ok"] is True, f"still not green: {deliver['verdict']} — the guard latched"
    assert deliver["verdict"] == "DELIVERING"

    advancing = health.c_advancing_live_work(receipts, NOW)
    assert advancing["ok"] is True, f"still not green: {advancing['verdict']} — the guard latched"


def test_an_older_clockless_receipt_alone_does_not_shadow_a_newer_datable_one():
    """Only an ordinal at or above the one being read can shadow it. Below, it is just history."""
    receipts = _sorted([_r(74, suffix="legacy"), _r(94, ended="2026-09-02T15:00:00Z")])
    row = health.c_cycle_delivering(receipts, [], INTERVAL_H, NOW)
    assert row["ok"] is True, "a clockless receipt 20 ordinals back cannot be the newest"


def test_an_unorderable_receipt_counts_as_possibly_newer():
    """⛔ Neither datable nor orderable is the one case that must never be skipped in silence."""
    odd = _r(94, ended="2026-09-02T15:00:00Z")
    odd[receipt_schema.CYCLE_ID_KEY] = "not-a-cycle-id"
    odd["_file"] = "not-a-cycle-id.json"
    del odd[receipt_schema.ENDED_KEY]
    receipts = _sorted([_r(94, ended="2026-09-02T15:00:00Z"), odd])
    row = health.c_cycle_delivering(receipts, [], INTERVAL_H, NOW)
    assert row["unmeasured"] is True, "an unorderable clockless receipt must not be assumed old"


# ── a real LATE must still be reachable ──────────────────────────────────────────────────────────

def test_a_genuinely_late_loop_still_reds():
    """⛔ THE GUARD MUST NOT BECOME A BLANKET EXCUSE. Fixing a false red that hides a true one is
    not a fix. With every receipt datable, an old newest receipt is still `LATE`."""
    receipts = _sorted([_r(94, ended="2026-08-20T00:00:00Z"), _r(95, ended="2026-08-21T00:00:00Z")])
    row = health.c_cycle_delivering(receipts, [], INTERVAL_H, NOW)
    assert row["needs_attention"] is True and row["verdict"] == "LATE"
    assert row["unmeasured"] is False


def test_a_genuine_documentation_run_still_reds():
    receipts = _sorted([_r(n, ended=f"2026-09-02T1{i}:00:00Z", route="none")
                        for i, n in enumerate((94, 95, 96))])
    row = health.c_advancing_live_work(receipts, NOW)
    assert row["needs_attention"] is True and row["verdict"] == "NOT-ADVANCING"


# ── the name is owned in one place ───────────────────────────────────────────────────────────────

def test_health_imports_the_clock_name_rather_than_spelling_it():
    """⛔ THE FIFTH LOST FIELD NAME. The reader must not carry its own copy of the writer's spelling."""
    assert health.RECEIPT_TIME_KEYS[0] == receipt_schema.ENDED_KEY
    src = open(health.__file__, encoding="utf-8").read()
    decl = [ln for ln in src.split("\n") if ln.startswith("RECEIPT_TIME_KEYS")]
    assert decl and f'"{receipt_schema.ENDED_KEY}"' not in decl[0], (
        "RECEIPT_TIME_KEYS spells the governed clock name as a literal; import it instead")


def test_started_utc_is_not_an_accepted_clock():
    """⛔ ARGUED IN `receipt_schema.ENDED_KEY`'s comment: the start is `cadence.py`'s fact, and a
    start stamp dates the FIRING, which is the distinction this condition exists to draw."""
    assert "started_utc" not in health.RECEIPT_TIME_KEYS
    r = _r(94)
    r["started_utc"] = "2026-09-02T15:00:00Z"
    assert health._receipt_ts_raw(r) is None
    assert receipt_schema.ended_at_of(r) is None


# ── the enforcer ─────────────────────────────────────────────────────────────────────────────────

def test_a_governed_receipt_without_a_readable_clock_fails_the_gate():
    rid = f"CYC-{receipt_schema.FIRST_CLOCK_GOVERNED_CYCLE:04d}-gate"
    base = {receipt_schema.CYCLE_ID_KEY: rid,
            receipt_schema.ROUTE_ADVANCED_KEY: "none",
            receipt_schema.CCR_ID_KEY: "session_01ClockGate",
            receipt_schema.BLOCK_KEY: {receipt_schema.WIDTH_KEY: 0}}
    assert any(receipt_schema.ENDED_KEY in p
               for p in receipt_schema.problems(copy.deepcopy(base), f"{rid}.json"))

    ok = dict(base, **{receipt_schema.ENDED_KEY: "2026-09-02T15:13:00Z"})
    assert receipt_schema.problems(ok, f"{rid}.json") == []


@pytest.mark.parametrize("bad", ["", "   ", "tuesday", "2026-09-02", "2026-09-02T15:13:00",
                                 "2026-09-02T15:13:00+02:00", 1756825980, None, True])
def test_an_unparseable_or_non_utc_clock_is_no_clock(bad):
    """⛔ A clock the reader cannot parse is exactly as invisible as one that is absent."""
    assert receipt_schema.ended_at_of({receipt_schema.ENDED_KEY: bad}) is None


@pytest.mark.parametrize("good", ["2026-09-02T15:13:00Z", "2026-09-02T15:13:00+00:00",
                                  "2026-09-02T15:13:00.500Z"])
def test_a_well_formed_utc_clock_is_accepted(good):
    assert receipt_schema.ended_at_of({receipt_schema.ENDED_KEY: good}) == good


def test_receipts_below_the_cutoff_are_grandfathered():
    """⛔ Do NOT grade immutable history: that is what latched `cycles_are_sized`."""
    n = receipt_schema.FIRST_CLOCK_GOVERNED_CYCLE - 1
    rid = f"CYC-{n:04d}-old"
    old = {receipt_schema.CYCLE_ID_KEY: rid,
           receipt_schema.ROUTE_ADVANCED_KEY: "none",
           receipt_schema.CCR_ID_KEY: "session_01OldGrandfathered",
           receipt_schema.BLOCK_KEY: {receipt_schema.WIDTH_KEY: 0}}
    assert receipt_schema.problems(old, f"{rid}.json") == []


def test_the_cutoff_is_ahead_of_every_committed_receipt():
    """⛔ A cutoff at or below the newest receipt breaks the commit of a cycle already in flight."""
    r = receipt_schema.audit()
    newest = max((receipt_schema.cycle_number(rid) or 0) for rid in r["governed"])
    assert receipt_schema.FIRST_CLOCK_GOVERNED_CYCLE > newest, (
        f"cutoff {receipt_schema.FIRST_CLOCK_GOVERNED_CYCLE} would retroactively fail CYC-{newest:04d}")
    assert r["failures"] == [], f"the cutoff must not red the trunk: {r['failures']}"


def test_the_contract_names_the_clock():
    """Direction A and B of `contract_check`: the gate requires it, so step 10 must spell it."""
    assert contract_check.audit()["failures"] == []
    assert receipt_schema.ENDED_KEY in contract_check.names(contract_check.step_text())


# ── boundaries, each one a single-site mutation this file would otherwise miss ────────────────────

def test_a_clockless_receipt_at_the_SAME_ordinal_still_shadows():
    """⛔ THE BOUNDARY IS `>=`, NOT `>`, AND THE HISTORY IS THE REASON. CYC-0084 exists TWICE on the
    trunk: `CYC-0084-e2d78138` (`utc`, committed 09:20:46Z) and `CYC-0084-6b009680` (`started_utc`,
    committed 09:26:29Z) — two sessions, the same ordinal, six minutes apart. The undatable one is
    the NEWER. An off-by-one here reads the older twin as authoritative and the row goes confidently
    wrong on exactly the shape that produced the incident.
    """
    receipts = _sorted([_r(84, legacy="2026-08-29T08:45:00Z", suffix="e2d78138"),
                        _r(84, suffix="6b009680")])
    row = health.c_cycle_delivering(receipts, [], INTERVAL_H, NOW)
    assert row["unmeasured"] is True, "an equal-ordinal undatable receipt must still shadow"
    assert row["verdict"] == "RECEIPT-TIME-UNREADABLE"


def test_the_advancing_window_floor_is_its_OLDEST_ordinal():
    """⛔ The floor is `min(window)`, not `max`. A clockless receipt INSIDE the window's span is a
    receipt the window should have contained — reading from the newest edge would miss it."""
    receipts = _sorted([
        _r(82, legacy="2026-08-29T08:00:00Z", route="none"),
        _r(83, suffix="clockless"),                              # inside the window's span
        _r(84, legacy="2026-08-29T08:45:00Z", route="none"),
        _r(85, legacy="2026-08-29T09:00:00Z", route="none"),
    ])
    assert [r["_file"] for r in receipts[-3:]] == [
        "CYC-0082-seat.json", "CYC-0084-seat.json", "CYC-0085-seat.json"]
    row = health.c_advancing_live_work(receipts, NOW)
    assert row["unmeasured"] is True, "a clockless receipt inside the window's span must shadow it"


def test_an_unorderable_window_member_forces_the_widest_floor():
    """⛔ If the window itself cannot be ordered, no clockless receipt can be ruled out. Fail wide."""
    odd = _r(84, legacy="2026-08-29T08:45:00Z", route="none")
    odd[receipt_schema.CYCLE_ID_KEY] = "not-a-cycle-id"
    odd["_file"] = "not-a-cycle-id.json"
    receipts = _sorted([
        _r(1, suffix="ancient"),                                 # clockless, far below any window
        _r(82, legacy="2026-08-29T08:00:00Z", route="none"),
        _r(83, legacy="2026-08-29T08:30:00Z", route="none"),
        odd,
    ])
    row = health.c_advancing_live_work(receipts, NOW)
    assert row["unmeasured"] is True
    assert row["verdict"] == "WINDOW-NOT-PROVABLY-NEWEST"


def test_direction_a_actually_derives_the_clock_requirement():
    """⛔ ONE-OF-A-PAIR. Direction B (the `*_KEY` constant) alone would keep `test_the_contract_
    names_the_clock` green even if the fixture at the cutoff were deleted — and then nothing would
    check that the ENFORCER truly refuses a receipt without the field. Both halves are asserted."""
    required = contract_check.required_paths()
    assert (receipt_schema.ENDED_KEY,) in required, (
        "no fixture sits at or above FIRST_CLOCK_GOVERNED_CYCLE, so contract_check cannot see that "
        f"`{receipt_schema.ENDED_KEY}` is required at all")
