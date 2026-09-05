"""A round's ROLL-UP is a synthesis of its seats, not a sixth seat — and the bar counted it as one.

⛔⛔ THE DEFECT (AUT-PD-193, filed 2026-08-31 by CYC-0090-d7df5340, reproduced 2026-09-01 before any
line of the fix was written). `publish_bar._seat_records` globs `{pub_id}-{sha}*.json`; a round's
roll-up is filed as `{pub_id}-{sha}.json`, which that glob matches with `*` EMPTY. Clause 1 then
sums `blockers` and `p1s` over every record the glob returned, roll-up included. Measured against
the records committed to `research/autonomy/review-seats/`:

    PUB-ASO-7a7f408258c8 (round 26): 6 records returned — 5 seats + 1 roll-up
        counted   2 blocker(s), 10 P1(s)
        true      1 blocker,     5 P1(s)

TWO OPPOSITE CONVENTIONS ARE ON DISK AND ONLY ONE IS CORRECT AGAINST THE CODE.
`PUB-ASO-b53290b37e71` (round 20) and `PUB-ASO-f9e5059912a5` (round 27) carry EMPTY tallies and cite
the round-7 PUB-FUSION-PARTNER precedent for it. `PUB-ASO-7a7f408258c8` (round 26) and
`PUB-ATR-c1bc934fec3c` carry a populated union, and round 26's `_role` states the opposite rationale
in words: "carries the union of their tallies, so a derivation over the seat glob counts each
finding exactly once." It does not; it counts each of them twice.

★ WHAT THE OVER-COUNT ACTUALLY REACHES, WHICH IS NOT THE OBVIOUS THING. Clause 1 refuses on ANY
blocker, so inflating a non-zero blocker count changes no verdict. The reachable failure is the
other direction: the clause also refuses a record that "under-reports its own seats"
(`len(blockers) < len(seat_blockers)`), and the DOUBLED total is what that comparison is made
against — so a round that keeps its record honestly is refused for under-reporting findings that
exist once. The over-count is also read as a WIDTH: `len(seats)` is the number of looks the
declaring round fielded, and a roll-up is not a look.

⛔ DIRECTION OF EVERY ASSERTION BELOW — this suite was written by a seat of a sprint that this same
bar is blocking, so `amendment_guard`'s invariant applies to it: a bar may not be loosened by the
cycle it blocks. Every case here asserts a REFUSAL the bar did not previously make, or a count that
is SMALLER than the one it previously used. Nothing here lets a paper past anything.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent.parent
AUTONOMY = REPO / "research" / "autonomy"
SEATS = AUTONOMY / "review-seats"

SHA = "e" * 40
OTHER = "d" * 40


@pytest.fixture()
def bar():
    spec = importlib.util.spec_from_file_location("autonomy_publish_bar_rollup",
                                                  AUTONOMY / "publish_bar.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seat(path, sha, *, blockers=(), p1s=(), blind=True, **extra):
    record = {"blind": blind, "reviewed_commit": sha,
              "blockers": list(blockers), "p1s": list(p1s)}
    record.update(extra)
    path.write_text(json.dumps(record))


def _stand_up(bar, tmp_path, monkeypatch, *, seats_at_sha, rollup=None, prior_widths=(),
              declared_blockers=(), declared_p1s=(), rounds=9, prior_rollup=False):
    """A round that clears clause 1 on every ground except the ones under test.

    `rollup` is None for no roll-up at all, or a dict of the tallies it carries.
    """
    hardening, seats = tmp_path / "h", tmp_path / "s"
    for d in (hardening, seats):
        d.mkdir(exist_ok=True)
    monkeypatch.setattr(bar, "HARDENING_DIR", hardening)
    monkeypatch.setattr(bar, "SEATS_DIR", seats)

    names = []
    for i in range(seats_at_sha):
        name = f"PUB-X-{SHA}-seat-{i}.json"
        _seat(seats / name, SHA)
        names.append(name)
    if rollup is not None:
        name = f"PUB-X-{SHA}.json"
        _seat(seats / name, SHA, blockers=rollup.get("blockers", ()), p1s=rollup.get("p1s", ()),
              _role="the canonical round record, merging the seats above")
        names.append(name)
    for r, width in enumerate(prior_widths):
        other = f"{r:040d}"
        for i in range(width):
            _seat(seats / f"PUB-X-{other}-seat-{i}.json", other)
        if prior_rollup:
            _seat(seats / f"PUB-X-{other}.json", other)

    (hardening / "PUB-X.json").write_text(json.dumps({
        "blockers": list(declared_blockers), "p1s": list(declared_p1s),
        "reviewed_commit": SHA, "seats": names, "last_round": rounds}))


# --------------------------------------------------------------------------- positive controls

def test_a_clean_round_with_an_empty_rollup_still_passes(bar, tmp_path, monkeypatch):
    """⭐ THE POSITIVE CONTROL FOR THE ROLL-UP CASE, AND IT COMES FIRST. Without it every refusal
    below would pass equally well on a clause broken into refusing everything, which is a different
    defect and not a safe one (`paper-hardening` §8b: a gate that reds on true input is worse than
    one that greens on false input, because the first thing anyone does is loosen it).

    This is the round-20 / round-27 convention: five seats carry the findings, the roll-up carries
    the narrative and empty tallies.
    """
    _stand_up(bar, tmp_path, monkeypatch, seats_at_sha=5, rollup={}, prior_widths=(5, 5))
    got = bar.clause_1_hardening_converged("PUB-X", SHA)
    assert got["ok"] is True, got
    assert "0 blockers across 5 blind seat(s)" in got["evidence"], (
        "the roll-up was counted as a sixth look; the round fielded five seats: "
        f"{got['evidence']}")


def test_a_clean_round_with_no_rollup_at_all_still_passes(bar, tmp_path, monkeypatch):
    """The other convention on disk — PUB-ASO-6127da1ac1a2 filed five seats and no roll-up. A round
    is not required to write one, so the fix may not make its absence a refusal."""
    _stand_up(bar, tmp_path, monkeypatch, seats_at_sha=5, rollup=None, prior_widths=(5, 5))
    got = bar.clause_1_hardening_converged("PUB-X", SHA)
    assert got["ok"] is True, got
    assert "0 blockers across 5 blind seat(s)" in got["evidence"], got


def test_prior_rollups_do_not_invent_an_extra_independent_reviewer(bar, tmp_path, monkeypatch):
    _stand_up(bar, tmp_path, monkeypatch, seats_at_sha=5, rollup={},
              prior_widths=(5, 5), prior_rollup=True)
    got = bar.clause_1_hardening_converged("PUB-X", SHA)
    assert got["ok"], got
    assert all(width == 5 for width in bar._look_history("PUB-X").values())


# --------------------------------------------------------------------------- the defect itself

def test_a_rollup_carrying_its_seats_findings_is_refused(bar, tmp_path, monkeypatch):
    """⛔ THE DOUBLE COUNT, AT THE COMMIT THAT WOULD BE POSTED.

    Five seats file one P1 each. The roll-up carries the union — five P1s — exactly as
    PUB-ASO-7a7f408258c8 does. The honest hardening record declares 5. Before the fix the clause
    summed 10 and refused the honest record for UNDER-REPORTING; a record that declared the doubled
    10 passed instead. Both readings are wrong and they are wrong in opposite directions, which is
    what makes this a miscount rather than a stricter bar.

    ★ THE FIX IS THE INPUT, NOT THE METER (`paper-hardening` §8.0a). The refusal names the
    convention: tallies live on the seat records, where each finding is counted once.
    """
    _stand_up(bar, tmp_path, monkeypatch, seats_at_sha=0, rollup={"p1s": [f"p{i}" for i in range(5)]},
              prior_widths=(), declared_p1s=[f"p{i}" for i in range(5)])
    # five real seats, one P1 each, plus the union-carrying roll-up
    seats = tmp_path / "s"
    hardening = tmp_path / "h"
    names = []
    for i in range(5):
        name = f"PUB-X-{SHA}-seat-{i}.json"
        _seat(seats / name, SHA, p1s=[f"p{i}"])
        names.append(name)
    names.append(f"PUB-X-{SHA}.json")
    (hardening / "PUB-X.json").write_text(json.dumps({
        "blockers": [], "p1s": [f"p{i}" for i in range(5)], "reviewed_commit": SHA,
        "seats": names, "last_round": 26}))

    got = bar.clause_1_hardening_converged("PUB-X", SHA)
    assert got["ok"] is False and got["verdict"] == bar.FAIL, got
    assert "carry their own `blockers`/`p1s`" in got["evidence"], got
    assert "counts each of them" in got["evidence"], got
    # ⛔ AND IT MUST NOT ARRIVE AS AN UNDER-REPORTING CHARGE. That message accuses the round of
    # hiding findings, sends the round-keeper to inflate its own record to 10, and cements the
    # double count as the convention.
    assert "under-reports" not in got["evidence"], (
        "the honest record was refused for under-reporting findings that exist once — that is the "
        f"reachable failure AUT-PD-193 names: {got['evidence']}")


def test_a_bare_record_standing_alone_is_the_rounds_one_look_and_keeps_its_tallies(
        bar, tmp_path, monkeypatch):
    """⛔⛔ THE NEAR-MISS THIS SEAT ACTUALLY MADE, KEPT AS A TEST RATHER THAN QUIETLY FIXED.

    The first version of the fix excluded `{pub}-{sha}.json` unconditionally. That is wrong, and it
    is wrong in the expensive direction: `clause_6_independent_adversarial_seat` reads EXACTLY that
    path, so the bare filename is the CANONICAL record of a round's adversarial seat, and rounds
    have been filed with nothing else — `PUB-FUSION-PARTNER-21bc8578b11a` carries 4 blockers and 9
    P1s with no `-seat-` sibling on disk. Excluding it made clause 1 refuse a round whose only
    record IS its seat, and deleted that round's findings from the tally.

    ⚠ IT WAS CAUGHT BY A POSITIVE CONTROL, WHICH IS WHAT POSITIVE CONTROLS ARE FOR:
    `systems/tests/test_autonomy_publish_bar.py::test_all_six_clauses_passing_is_what_it_takes`
    stands up its one blind seat at that path. `paper-hardening` §8b.1 — a gate that reds on true
    input is worse than one that greens on false input, because the first thing anyone does to it
    is loosen it, and here that would have meant deleting the whole fix.

    ★ SO THE RULE IS CONDITIONAL: the bare record is a ROLL-UP only when per-lens seat records sit
    beside it. Alone, it is the round's one look and its tallies are the only copy there is.
    """
    _stand_up(bar, tmp_path, monkeypatch, seats_at_sha=0, rollup={}, prior_widths=())
    got = bar.clause_1_hardening_converged("PUB-X", SHA)
    assert got["ok"] is True, (
        "a round whose only record is the canonical clause-6 record was refused for fielding no "
        f"seat — that record IS its seat: {got}")
    assert "0 blockers across 1 blind seat(s)" in got["evidence"], got


def test_a_lone_bare_records_findings_are_not_discarded(bar, tmp_path, monkeypatch):
    """The other half of the same near-miss. A lone bare record carrying a blocker must still
    refuse — dropping its tallies would turn a round that found a defect into a clean one, which is
    the silent-discard failure `paper-hardening` §8.0a warns about in this exact file."""
    _stand_up(bar, tmp_path, monkeypatch, seats_at_sha=0, rollup={"blockers": ["a real defect"]},
              prior_widths=(), declared_blockers=["a real defect"])
    got = bar.clause_1_hardening_converged("PUB-X", SHA)
    assert got["ok"] is False and got["verdict"] == bar.FAIL, got
    assert "1 blocker(s) open" in got["evidence"], got


def test_the_declaring_rounds_width_counts_seats_not_records(bar, tmp_path, monkeypatch):
    """⛔ THE WIDTH HALF. Five seats and a roll-up is FIVE looks, not six.

    The floor exists so that a round declaring convergence is not the loop's weakest look. Counting
    the roll-up on the declaring side lets a five-seat round clear a six-seat floor by filing one
    extra file — which is the optional-stopping failure the floor was written to forbid, reachable
    without running another seat.

    ⚠ DIRECTION: this counts the declaring round LOWER than before, so it refuses more. The
    symmetrical change — counting the earlier rounds in seats too — would count `widest` lower and
    refuse LESS, and is deliberately not made here; see the comment on the check itself.
    """
    _stand_up(bar, tmp_path, monkeypatch, seats_at_sha=5, rollup={}, prior_widths=(6,))
    got = bar.clause_1_hardening_converged("PUB-X", SHA)
    assert got["ok"] is False and got["verdict"] == bar.FAIL, got
    assert "5 blind seat(s) against 6" in got["evidence"], got
    assert "weakest look" in got["evidence"], got


# --------------------------------------------------------------------------- the discriminator

def test_the_discriminator_is_the_filename_because_the_keys_do_not_separate_the_two_shapes(bar):
    """★ MEASURED AGAINST THE RECORDS ON DISK, NOT CHOSEN.

    The two obvious alternatives both fail on committed evidence: roll-ups routinely carry a `seat`
    key (`PUB-ASO-b53290b37e71...json`'s reads "five blind seats - regression, arithmetic, ..."),
    and the four PUB-ATR seat files carry `lens` instead of `seat`. Only the filename separates
    them, and the filename is what the glob keys on.

    ⚠ AND A THIRD SHAPE ALREADY EXISTS: `...-round4-p1-rederivation.json` is blind, matches the
    glob, and is not a seat. A `startswith` predicate puts it on the right side of the line without
    anybody remembering to extend a list (`paper-hardening` §8b.2 — a fix bound to a LIST regresses
    at a sibling the fix did not name).
    """
    assert bar._is_seat_file("PUB-X", SHA, f"PUB-X-{SHA}-seat-regression.json") is True
    assert bar._is_seat_file("PUB-X", SHA, f"PUB-X-{SHA}.json") is False
    assert bar._is_seat_file("PUB-X", SHA, f"PUB-X-{SHA}-round4-p1-rederivation.json") is False
    # a seat record filed under ANOTHER commit is not this commit's seat
    assert bar._is_seat_file("PUB-X", SHA, f"PUB-X-{OTHER}-seat-regression.json") is False


@pytest.mark.skipif(not SEATS.is_dir(), reason="the committed seat records are not present")
def test_every_committed_rollup_is_separated_from_its_seats(bar):
    """The predicate is asserted against the real directory, because a predicate that is right on
    fixtures and wrong on the evidence would be the instrument reporting a false absence — the
    failure this repository keeps paying for (CLAUDE.md §4)."""
    rollups, seats = [], []
    for path in sorted(SEATS.glob("*.json")):
        record = json.loads(path.read_text())
        sha = record.get("reviewed_commit") or ""
        pub = path.name.split(f"-{sha}")[0] if sha and f"-{sha}" in path.name else None
        if pub is None:
            continue  # filed under a name that does not carry the commit it read; not this test's
        (seats if bar._is_seat_file(pub, sha, path.name) else rollups).append(path.name)
    assert seats, "no committed record was recognised as a seat — the predicate binds nothing"
    assert rollups, "no committed record was recognised as a roll-up — the predicate binds nothing"
    assert all("-seat-" in n for n in seats), seats
    assert not any("-seat-" in n for n in rollups), rollups
