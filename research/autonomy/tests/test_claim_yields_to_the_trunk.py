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
⚠ THAT CONSTRAINT IS ABOUT *THIS* REPOSITORY'S REMOTE AND NOTHING ELSE, AND READING IT AS "use a
fake" COST THIS MODULE THREE DEFECTS. The real-remote half of the suite lives in
`test_a_lost_push_is_a_lost_lease.py`, which builds a bare repo in a tmp_path and races two real
workers on it. This file keeps the decision logic, where a fake is the right instrument.
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
    `[False, True]` is "the first push lost, the second won". A member may also be one of the
    module's own `PUSH_*` constants, which is how a test asks for the third outcome — a push that
    never reached the remote, which is NOT a lost race and must not be reported as one.
    """

    def __init__(self, trunk_states, push_results):
        self.trunk_states = list(trunk_states)
        self.push_results = list(push_results)
        self.calls = []
        self.last_push_error = "fake stderr"
        self.last_merge_error = "fake stderr"

    def fetch(self):
        self.calls.append("fetch")

    #: AUT-PD-160: what HEAD carries that origin/main does not. The default is the clean case — a
    #: worker whose only pending work IS the claim — so every pre-existing test keeps its meaning.
    #: A test that wants the refusal sets it, and a test that wants git itself to fail sets the
    #: exception. ⚠ A fake can only reach the DECISION here; the real-git half lives in
    #: `test_a_lost_push_is_a_lost_lease.py`, which is where all three of this module's shipped
    #: defects were actually visible.
    carried = ()
    carried_raises = None

    def commits_not_on_trunk(self):
        self.calls.append("head-vs-trunk")
        if self.carried_raises is not None:
            raise self.carried_raises
        return list(self.carried)

    def trunk_ledger(self):
        self.calls.append("read-trunk")
        return self.trunk_states[0] if len(self.trunk_states) == 1 else self.trunk_states.pop(0)

    #: AUT-PD-165: the index at entry, and what the claim commit is built from. The defaults are
    #: the clean case — nothing staged, and staging recorded rather than performed — so every
    #: pre-existing test keeps its meaning. ⚠ A fake reaches only the DECISION; that the committed
    #: BYTES are the trunk's rather than the tree's is a property only a real repository can show,
    #: and it is asserted in `test_a_lost_push_is_a_lost_lease.py`.
    staged = ()

    def staged_paths(self):
        self.calls.append("staged-vs-head")
        return list(self.staged)

    def stage_ledger_blob(self, text):
        self.calls.append("stage-trunk-blob")
        self.staged_text = text

    def commit_ledger(self, message):
        self.calls.append(f"commit:{message}")

    def push(self):
        result = self.push_results.pop(0)
        if result is True:
            result = C.PUSH_OK
        elif result is False:
            result = C.PUSH_LOST
        self.calls.append(f"push:{result}")
        return result

    def undo_last_commit(self):
        self.calls.append("undo")

    def integrate(self):
        self.calls.append("integrate")
        return self.integrate_result

    integrate_result = C.MERGE_OK


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

def test_the_push_targets_the_remote_ref_not_a_local_branch_name():
    """⛔⛔ AUT-PD-029, AND ANOTHER SESSION FOUND IT BECAUSE MINE COULD NOT.

    `git push origin main` pushes the LOCAL BRANCH LITERALLY NAMED `main`. On any session working
    from a differently-named branch — this repository's own convention is `claude/<name>` rebased
    onto origin/main — that branch is stale or absent, every push fails as a non-fast-forward, and
    this module degrades SILENTLY to reporting RETRY forever. It cannot arbitrate a claim at all,
    which is the one thing it exists to do.

    ★ THE TEST IS AS MUCH ABOUT HOW THIS WAS MISSED AS ABOUT THE REFSPEC. It worked for its author
    because the author's branch happened to be named `main`: the tool was exercised in the single
    configuration that hides the bug, and every other test here uses a FakeGit that never reaches
    a real refspec. So the assertion is on the argv itself, which is the part a fake cannot cover.
    """
    assert C.Git.PUSH_REFSPEC == ("push", "-q", "origin", "HEAD:main"), (
        "the push refspec no longer names HEAD. `origin main` pushes a local branch by NAME; "
        "`origin HEAD:main` is a compare-and-swap on the REMOTE ref whatever the local branch is "
        "called, which is what this module's docstring claims it does.")
    assert "main" not in C.Git.PUSH_REFSPEC[:-1], "a bare `main` refspec crept back into the argv"


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
    assert git.calls.index("undo") < git.calls.index("read-trunk", git.calls.index("push:lost")), (
        "it re-read the trunk BEFORE withdrawing its losing commit, so a retry would push a claim "
        "it had already conceded")
    assert json.load(open(led, encoding="utf-8"))["entries"][0]["owner"] is None, (
        "the conceded claim was left in the WORKING TREE. AUT-PROP-030: that stale write is what "
        "blocks the integration, and the loop then cannot converge — see the real-git suite.")


def test_a_rejection_that_was_somebody_elses_commit_retries_and_wins(led):
    """⚠ MOST REJECTIONS IN THIS REPOSITORY ARE NOT CONTENTION ON YOUR ROW. The autoscale ticks push
    several times an hour, so a rejected push usually means an unrelated commit landed. Treating
    every rejection as a lost race would make the loop yield items nobody else wanted."""
    git = FakeGit([_ledger([("AUT-X", None)])], [False, True])
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.CLAIMED and "attempt 2" in why


def test_a_rejected_push_integrates_the_remote_before_retrying(led):
    """⛔⛔ THE LOOP COULD NOT CONVERGE AND SAID SOMETHING ELSE (AUT-PD-033, found by USING it).

    A push is rejected when the remote has moved — and in this repository CI ticks push several
    times an hour, so that is the ORDINARY case, not contention. The first version re-fetched and
    re-decided but never INTEGRATED, so HEAD stayed behind and every retry was rejected for the
    identical reason as the first. It then reported "the remote is moving faster than this can
    commit", which is a comforting hypothesis for a loop that structurally could not succeed.

    ★ `fetch` updates the remote-tracking ref and changes NOTHING about HEAD. That distinction is
    the whole bug, and it is invisible unless the test asserts on the integration itself.
    """
    git = FakeGit([_ledger([("AUT-X", None)])], [False, True])
    verdict, _ = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.CLAIMED
    assert "integrate" in git.calls, (
        "the retry never merged origin/main, so the second push was rejected for the same reason "
        "as the first — a loop that cannot converge is worse than one that fails immediately")
    assert git.calls.index("integrate") < git.calls.index("push:ok"), (
        "it integrated AFTER the successful push, which is the wrong order and would not have "
        "helped the push it was meant to unblock")


def test_a_conflicting_integration_reports_rather_than_auto_resolving(led):
    """⚠ THE LEDGER IS THE FILE TWO SESSIONS COLLIDE ON, and a claim is not worth risking a wrong
    automatic resolution of it. Abort and say so; the human or the driver resolves it.

    ⭐ AMENDED BY AUT-PROP-030: the verdict is SUSPENDED, not RETRY. A merge a human has to resolve
    is not a thing to try again — it is automation stopping, which is the only honest name for it.
    """
    git = FakeGit([_ledger([("AUT-X", None)])], [False])
    git.integrate_result = C.MERGE_CONFLICT
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.SUSPENDED
    assert "conflict" in why and "resolve the merge yourself" in why


def test_endless_rejection_reports_rather_than_pretending_to_have_claimed(led):
    """⛔ THE ONE THAT MUST NOT SILENTLY SUCCEED. If every push is rejected the item is NOT claimed,
    and saying otherwise would dispatch a worker onto a row the trunk still shows as free — the exact
    harm, arrived at from the other direction."""
    git = FakeGit([_ledger([("AUT-X", None)])], [False] * C.MAX_ATTEMPTS)
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.SUSPENDED
    assert "even after merging origin/main" in why, (
        "the exhausted-retry message must say that integration was tried, or the next reader "
        "repeats the diagnosis this defect already produced once: 'the remote is moving too fast', "
        "for a loop that was simply never catching up")


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


# ---------------------------------------------------------------------------------------------
# ⛔⛔ FINISHED WORK IS NOT FREE WORK (AUT-PD-176).
#
# THE INCIDENT: `AUT-PD-145` was closed by `CYC-0083-381d0696` at 2026-08-29T08:25:54Z — the ratchet
# it asked for was on the trunk and its suite was green. At 11:47:29Z commit 5856839fe, a claim
# written by `claim.py` itself, flipped it `done -> in_progress` while LEAVING `closed_by` in place,
# and a worker session was dispatched to redo work that had landed 3.4 hours earlier.
#
# ★ THE PROPERTY UNDER TEST IS NOT "a closed row may never reopen". A census of all 348 trunk ledger
# commits found 40 `closed -> open` transitions, of which 37 are ordinary re-derivation; refusing
# those at the write would be an outage. It is the narrower and exactly-measured claim that a
# FINISHED row cannot be CLAIMED — three of the 40 carried a `closed_by`, and the one this module
# wrote is the one that stuck.
# ---------------------------------------------------------------------------------------------

def _closed(entry_id="AUT-X", owner=None, state="done", closed_by="CYC-0083-381d0696"):
    return {"entries": [{"id": entry_id, "owner": owner, "claimed_utc": None,
                         "state": state, "closed_by": closed_by}]}


def test_a_row_a_cycle_closed_is_never_claimable():
    """⛔ THE REGRESSION, IN THE SHAPE IT ACTUALLY LANDED IN."""
    verdict, why = C.decide(_closed(), "AUT-X", ME)
    assert verdict == C.YIELDED, "a finished row was offered as claimable work"
    assert "CYC-0083-381d0696" in why, "the refusal does not name the cycle that closed the row"


def test_a_finished_row_is_unclaimable_even_by_the_cycle_that_closed_it():
    """⛔⛔ THE ORDERING, WHICH IS THE HALF A GUARD WRITTEN LOWER DOWN WOULD HAVE MISSED.

    `decide()` answers CLAIMED for a row the trunk already shows as yours. A cycle that closed an
    item still holds it until step 9 releases the lease, so a guard placed after the ownership
    questions would hand a completed item straight back to its own closer and report CLAIMED —
    reopening it exactly as before, with the verdict that says nothing is wrong.
    """
    verdict, _ = C.decide(_closed(owner=ME), "AUT-X", ME)
    assert verdict == C.YIELDED, (
        "a finished row was handed back to the cycle that closed it, because the ownership test ran "
        "before the completion test")


def test_a_closed_state_with_no_closing_cycle_is_still_not_free():
    """⚠ A row can be finished before any cycle names itself in it, and `priority.py` already refuses
    to RANK such a row. No selector offers a closed row, so no legitimate claim can want one."""
    verdict, why = C.decide(_closed(closed_by=None), "AUT-X", ME)
    assert verdict == C.YIELDED and "done" in why


def test_the_closed_states_are_shared_with_the_ranker_and_not_re_typed_here():
    """⛔ CLAUDE.md §1 — one fact, one place. A second hand-typed copy of this set is how the two
    halves drift until a state the ranker skips is a state the claim path still offers."""
    import priority
    assert C.finished_by.__module__ == "claim"
    for state in priority.CLOSED_STATES:
        assert C.finished_by({"state": state}) is not None, (
            f"`{state}` is closed to the ranker but open to the claim path")


def test_an_ordinary_open_row_is_still_claimable():
    """⭐ THE POSITIVE CONTROL. Without it every assertion above passes on a `decide()` that yields to
    everything, which would stop the loop taking any work at all."""
    verdict, _ = C.decide(_closed(state="queued", closed_by=None), "AUT-X", ME)
    assert verdict == C.TAKEN


def test_the_claim_path_never_pushes_a_reopening(led):
    """⛔⛔ THE END-TO-END HALF, AND IT COVERS THE MUTATION `decide()` ALONE CANNOT.

    The reopening is written by `stamp_claim`, which sets `state = "in_progress"` unconditionally and
    has no idea what it is overwriting. What must be true is not merely that the verdict is YIELDED
    but that NOTHING WAS WRITTEN and NOTHING WAS PUSHED — the trunk's completion record survives.
    """
    git = FakeGit([_closed()], [])
    verdict, _ = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=led)
    assert verdict == C.YIELDED
    assert not any(c.startswith("push") for c in git.calls), (
        "it pushed a claim that reopens finished work")
    assert not any(c.startswith("commit") for c in git.calls), (
        "it committed a claim that reopens finished work")
    assert json.load(open(led, encoding="utf-8"))["entries"][0]["state"] == "queued", (
        "the working ledger was mutated for a claim that yielded")


def test_a_row_already_reopened_once_is_still_refused():
    """⛔⛔ THE ONE-OF-A-PAIR CASE, AND IT IS THE LIVE SHAPE OF THE INCIDENT RATHER THAN A HYPOTHETICAL.

    After the defect fires, the row on the trunk reads `state: in_progress` WITH `closed_by` still
    populated — that is exactly what `AUT-PD-145` looked like at 9d5b4defe. Every other test here
    pairs a closed `state` with a `closed_by`, so a guard reading only `state` passes all of them
    while leaving the resurrected row claimable forever: each fresh dispatch re-stamps it and it
    never heals. `closed_by` is the durable record, so it is read on its own and not merely as a
    label on a closed state.
    """
    verdict, why = C.decide(_closed(state="in_progress"), "AUT-X", ME)
    assert verdict == C.YIELDED, (
        "a row that had ALREADY been reopened by this defect was offered as claimable work — the "
        "guard is reading `state`, which the reopening overwrote, rather than `closed_by`, which it "
        "left behind")
    assert "CYC-0083-381d0696" in why
