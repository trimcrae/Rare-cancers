#!/usr/bin/env python3
"""Two sessions cannot both claim one item (AUT-PD-021).

⛔⛔ THE INCIDENT, IN ONE LINE: `atr-single-slot-seat` claimed AUT-PROP-009 at 20:10:00Z and CYC-0025
claimed it at 20:15:00Z from state fetched before that lease landed. Both worked. The collision
surfaced as a merge conflict AFTER roughly twenty minutes of duplicated effort.

★ THE PROPERTY UNDER TEST IS NOT "the checker notices". It is that the decision is made against the
TRUNK and settled by the PUSH — the one operation here that is already atomic. A version of this that
reads the working tree, or that treats a rejected push as an error to report rather than as the race
being lost, has rebuilt the defect with a checker on top.

⛔ AND NO TEST HERE TOUCHES THE REAL REMOTE. A test that pushes is a test that changes the trunk, and
racing writers on the trunk is this module's entire subject.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import claim as C  # noqa: E402

ME = "CYC-0023-6be7fd5a"
THEM = "CYC-0025"
WHEN = "2026-08-27T20:35:00Z"


def _ledger(rows):
    return {"entries": [{"id": i, "owner": o, "claimed_utc": None, "state": "queued"}
                        for i, o in rows]}


class FakeGit:
    """A git that records what it was asked to do and never leaves the process.

    `push_results` is consumed one per push, so a test states the race it wants directly:
    `[False, True]` is "the first push lost, the second won".
    """

    def __init__(self, trunk_states, push_results):
        self.trunk_states = list(trunk_states)
        self.push_results = list(push_results)
        self.calls = []

    def fetch(self):
        self.calls.append("fetch")

    def trunk_ledger(self):
        self.calls.append("read-trunk")
        return self.trunk_states[0] if len(self.trunk_states) == 1 else self.trunk_states.pop(0)

    def commit_ledger(self, message):
        self.calls.append(f"commit:{message}")

    def push(self):
        ok = self.push_results.pop(0)
        self.calls.append(f"push:{'ok' if ok else 'rejected'}")
        return ok

    def undo_last_commit(self):
        self.calls.append("undo")


@pytest.fixture
def led(tmp_path):
    p = tmp_path / "research-ledger.json"
    p.write_text(json.dumps(_ledger([("AUT-X", None)])), encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------------------------
# The decision, and what it reads.
# ---------------------------------------------------------------------------------------------

def test_the_decision_is_made_against_the_trunk_not_the_working_tree(led):
    """⛔⛔ THE REGRESSION. The working tree says the row is free — that is the STALE READ that caused
    the incident, and it is exactly what CYC-0025 saw. The trunk says otherwise, and the trunk wins."""
    git = FakeGit([_ledger([("AUT-X", THEM)])], [])
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.YIELDED and THEM in why
    assert not any(c.startswith("push") for c in git.calls), (
        "it pushed a claim on a row the trunk already showed as taken")
    assert json.load(open(led, encoding="utf-8"))["entries"][0]["owner"] is None, (
        "the working ledger was mutated for a claim that yielded")


def test_a_row_that_is_not_on_the_trunk_is_never_claimable(led):
    """⚠ THE SUBTLE ONE. An id absent from the trunk was filed locally and never pushed, so a claim on
    it is invisible to every other session — a claim that protects nothing while looking like one.
    'Not found' and 'found and free' must not collapse into the same answer."""
    verdict, why = C.decide(_ledger([("AUT-OTHER", None)]), "AUT-X", ME)
    assert verdict == C.YIELDED and "never pushed" in why


def test_your_own_claim_on_the_trunk_is_not_a_conflict():
    verdict, _ = C.decide(_ledger([("AUT-X", ME)]), "AUT-X", ME)
    assert verdict == C.CLAIMED


# ---------------------------------------------------------------------------------------------
# ⭐ THE PUSH IS THE ARBITER. These are the tests that make this a mechanism and not a rule.
# ---------------------------------------------------------------------------------------------

def test_a_clean_push_takes_the_item(led):
    git = FakeGit([_ledger([("AUT-X", None)])], [True])
    verdict, _ = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.CLAIMED
    row = json.load(open(led, encoding="utf-8"))["entries"][0]
    assert (row["owner"], row["claimed_utc"], row["state"]) == (ME, WHEN, "in_progress")


def test_losing_the_push_race_yields_and_withdraws_the_claim(led):
    """⛔⛔ THE RACE ITSELF. The trunk was free when read; by the time the push landed, the other
    session had taken it. The push rejection IS that information, not an error to report."""
    git = FakeGit([_ledger([("AUT-X", None)]), _ledger([("AUT-X", THEM)])], [False])
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.YIELDED and THEM in why
    assert "undo" in git.calls, "the losing claim was left committed locally"
    assert git.calls.index("undo") < git.calls.index("read-trunk", git.calls.index("push:rejected")), (
        "it re-read the trunk BEFORE withdrawing its losing commit, so a retry would push a claim "
        "it had already conceded")


def test_a_rejection_that_was_somebody_elses_commit_retries_and_wins(led):
    """⚠ MOST REJECTIONS IN THIS REPOSITORY ARE NOT CONTENTION ON YOUR ROW. The autoscale ticks push
    several times an hour, so a rejected push usually means an unrelated commit landed. Treating
    every rejection as a lost race would make the loop yield items nobody else wanted."""
    git = FakeGit([_ledger([("AUT-X", None)])], [False, True])
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.CLAIMED and "attempt 2" in why


def test_endless_rejection_reports_rather_than_pretending_to_have_claimed(led):
    """⛔ THE ONE THAT MUST NOT SILENTLY SUCCEED. If every push is rejected the item is NOT claimed,
    and saying otherwise would dispatch a worker onto a row the trunk still shows as free — the exact
    harm, arrived at from the other direction."""
    git = FakeGit([_ledger([("AUT-X", None)])], [False] * C.MAX_ATTEMPTS)
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.RETRY
    assert "retrying will not fix it" in why


# ---------------------------------------------------------------------------------------------
# The window the author was standing in while writing this.
# ---------------------------------------------------------------------------------------------

def test_an_unpushed_claim_is_reported_as_protecting_nothing():
    """⚠ MEASURED ON THE AUTHOR'S OWN CLAIM, 2026-08-27: AUT-PROP-022 was claimed, a seat was
    dispatched, and the claim sat in an uncommitted merge for eight minutes while the trunk still
    showed the row unowned. That is not somebody else's mistake — it is what claiming in the working
    tree and committing later DOES."""
    trunk = _ledger([("AUT-X", None), ("AUT-Y", THEM)])
    working = _ledger([("AUT-X", ME), ("AUT-Y", THEM)])
    assert C.unpushed_claims(trunk, working) == [("AUT-X", ME)]


def test_a_claim_the_trunk_agrees_with_is_not_reported():
    """The positive control: without it the check above passes on a function that flags everything,
    and a check that cries wolf is one this repository has already lost the value of several times."""
    same = _ledger([("AUT-X", ME)])
    assert C.unpushed_claims(same, same) == []
