"""`paper-hardening` stops at the first clean round, so clause 1 is an OPTIONAL-STOPPING verdict.

⛔ THE PROBLEM, AND WHY IT IS THE PERMISSION SYSTEM'S PROBLEM. Rounds are repeated until one comes
back with no blockers and no P1s, and then the loop stops. Every round is another chance for seats
that happened to miss to produce a clean result, so the probability that a clean round reflects
lucky seats rather than a clean paper RISES WITH THE NUMBER OF ROUNDS. Simmonds et al. 2017
(`research/method-watch-autonomy-prior-art-2.md` §4.3, PMID 28935493) measured exactly this shape
for living systematic reviews, and their decision rule is the one that applies: a status a reader
knows may change needs no correction; a verdict that FEEDS A DECISION does. Convergence feeds
posting, and a paper with a DOI is not un-posted.

⚠ AND THE PREMISE IS MEASURED HERE, NOT ASSUMED. The PUB-FUSION-PARTNER blind-seat records on disk
run 9 blockers over 2 seats, then 4 over 5, then TEN over 5, then 0 over 5 — the third round found
more than the second, on text the second round's findings had just been applied to. Per-round
findings do not descend to a floor, so a zero is one draw and not a measurement of zero.

★ WHAT IS ASSERTED HERE IS ONLY WHAT NEEDS NO UNKNOWN PARAMETER. A real alpha-spending boundary
needs the seats' miss rate and nothing measures it, so no number is invented for one (CLAUDE.md §4).
Two constraints survive that restriction:

  1. the verdict must STATE how many rounds produced it, and
  2. the round that declares convergence may not field fewer blind seats than the widest round
     before it — stopping on a thin round after several fat ones is optional stopping at its worst.

⛔ BOTH ARE STRENGTHENINGS AND CAN ONLY EVER BLOCK A POST. Written the other way round they would be
a loosening of the permission, which `amendment_guard.py` exists to refuse.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
AUTONOMY = REPO / "research" / "autonomy"


@pytest.fixture()
def bar():
    spec = importlib.util.spec_from_file_location("autonomy_publish_bar", AUTONOMY / "publish_bar.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _stand_up(bar, tmp_path, monkeypatch, *, rounds, this_width, prior_widths=()):
    """A paper that clears clause 1 on every OTHER ground, so only the new checks can fail it."""
    sha = "e" * 40
    hardening, seats = tmp_path / "h", tmp_path / "s"
    for d in (hardening, seats):
        d.mkdir(exist_ok=True)
    monkeypatch.setattr(bar, "HARDENING_DIR", hardening)
    monkeypatch.setattr(bar, "SEATS_DIR", seats)

    names = []
    for i in range(this_width):
        name = f"PUB-X-{sha}-seat-{i}.json"
        (seats / name).write_text(json.dumps({
            "blind": True, "reviewed_commit": sha, "blockers": [], "p1s": []}))
        names.append(name)
    #: Earlier rounds, each at its own commit. They are the "looks" that came before.
    for r, width in enumerate(prior_widths):
        other = f"{r:040d}"
        for i in range(width):
            (seats / f"PUB-X-{other}-seat-{i}.json").write_text(json.dumps({
                "blind": True, "reviewed_commit": other, "blockers": [], "p1s": []}))

    record = {"blockers": [], "p1s": [], "reviewed_commit": sha, "seats": names}
    if rounds is not None:
        record["last_round"] = rounds
    (hardening / "PUB-X.json").write_text(json.dumps(record))
    return sha


def test_a_converged_round_that_is_the_widest_yet_still_passes(bar, tmp_path, monkeypatch):
    """⭐ THE POSITIVE CONTROL, AND IT COMES FIRST. Without it the two refusals below would pass
    just as well on a clause that had been broken into refusing everything, which is a different
    defect and not a safe one."""
    sha = _stand_up(bar, tmp_path, monkeypatch, rounds=9, this_width=5, prior_widths=(2, 5, 5))
    got = bar.clause_1_hardening_converged("PUB-X", sha)
    assert got["ok"] is True, got
    assert "round 9" in got["evidence"]
    assert "3 earlier round(s)" in got["evidence"], (
        "the verdict has to carry how many looks preceded it, or a reader cannot tell a result "
        f"from a draw: {got['evidence']}")


def test_a_convergence_verdict_that_does_not_say_how_many_rounds_produced_it_is_unverifiable(
        bar, tmp_path, monkeypatch):
    """Absent is not empty. A record with no `last_round` used to pass, because the field was read
    only into an f-string — so the one number telling a reader how many chances the paper had to
    come back clean was optional."""
    sha = _stand_up(bar, tmp_path, monkeypatch, rounds=None, this_width=5, prior_widths=(5,))
    got = bar.clause_1_hardening_converged("PUB-X", sha)
    assert got["ok"] is False and got["verdict"] == bar.UNVERIFIABLE, got
    assert "how many rounds" in got["evidence"], got


def test_stopping_on_a_round_narrower_than_an_earlier_one_is_refused(bar, tmp_path, monkeypatch):
    """The failure this forbids is concrete: run five seats twice, get findings both times, run two
    seats the third time, get a clean sheet, and post. The clean sheet is then the weakest look of
    the three, chosen because it was clean."""
    sha = _stand_up(bar, tmp_path, monkeypatch, rounds=3, this_width=2, prior_widths=(5, 5))
    got = bar.clause_1_hardening_converged("PUB-X", sha)
    assert got["ok"] is False and got["verdict"] == bar.FAIL, got
    assert "weakest look" in got["evidence"], got
    assert "2 blind seat(s) against 5" in got["evidence"], got


def test_the_width_floor_counts_only_blind_seats(bar, tmp_path, monkeypatch):
    """A non-blind reviewer cannot raise the bar a later round has to clear, for the same reason it
    cannot clear the clause itself: it is not independent evidence."""
    sha = _stand_up(bar, tmp_path, monkeypatch, rounds=4, this_width=2, prior_widths=())
    other = "a" * 40
    for i in range(5):
        (tmp_path / "s" / f"PUB-X-{other}-seat-{i}.json").write_text(json.dumps({
            "blind": False, "reviewed_commit": other, "blockers": [], "p1s": []}))
    got = bar.clause_1_hardening_converged("PUB-X", sha)
    assert got["ok"] is True, (
        "five sighted reviewers were counted as a wider earlier look than two blind seats; only "
        f"blind seats are evidence here: {got}")


def test_the_look_history_is_keyed_by_the_commit_each_seat_actually_reviewed(bar, tmp_path,
                                                                            monkeypatch):
    """⛔ NOT BY THE FILENAME. The seat filename carries a commit and so does the record inside it,
    and they are two different claims — the glob is a convenience, the field is the evidence. A
    seat filed under one commit's name while reporting on another must count for the commit it
    read, or the width floor can be raised by seats that never looked at that text."""
    seats = tmp_path / "s"
    seats.mkdir()
    monkeypatch.setattr(bar, "SEATS_DIR", seats)
    (seats / f"PUB-X-{'b' * 40}-seat-0.json").write_text(json.dumps({
        "blind": True, "reviewed_commit": "c" * 40, "blockers": [], "p1s": []}))
    assert bar._look_history("PUB-X") == {"c" * 40: 1}
