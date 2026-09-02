"""Clauses 1 and 6 identify a review by WHAT IT READ, not by WHEN it happened.

⛔⛔ WHY THIS FILE EXISTS, AND THE MEASUREMENT BEHIND IT. `publish_bar` used to ask
`record["reviewed_commit"] == sha`. That comparison was wrong in both directions at once:

    too strict  the sha moves when nothing the review read moved, so a clean round is discarded by
                a commit to a ledger header or a test-selector hash
    too loose   the sha never said WHAT was covered — a seat that read one file and a seat that
                read forty record the identical string

Measured on PUB-ASO, 2026-09-02 (AUT-PD-205-d7df5340, re-measured by CYC-0091-91c8e949): across the
104 commits between round 32's pin `4ae4e9929` and this change, the paper's deliverable digest held
ONE value. So the comparison discarded a clean five-seat round 104 times to track zero real changes,
and each discard cost another six-seat round.

★ THE REPLACEMENT IS A RE-ANCHORING, NOT A RELAXATION, AND THESE TESTS ARE WHERE THAT IS PROVED
RATHER THAN ASSERTED. Everything the sha test accepted, the digest test still accepts (an exact
match short-circuits); what it stops doing is discarding reviews of bytes that did not move. The
adversarial cases below are the ones that would make it a relaxation, and each asserts a refusal.

⛔ AND THE SECOND HALF OF THIS FILE GUARDS A REGRESSION THAT WAS WRITTEN AND CAUGHT DURING THE
CHANGE ITSELF. The first implementation widened seat lookup as well, so every seat that had ever
read the same bytes was pooled into one round. That is wrong twice: it merges rounds that are
separate looks — PUB-ASO's digest `a6f7158552096aea…` covers rounds 31 AND 32, ten seats between
them — and it makes the clause UNSATISFIABLE, because a blocker filed by a superseded round could
then be cleared only by changing the paper, even where the defect it names is in a file the paper
does not ship. `_covers` decides which ROUND may speak for a commit; it must never decide which
seats make up a round.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
AUTONOMY = REPO / "research" / "autonomy"

PAPER = "PUB-X"
POSTED = "a" * 40
ROUND = "b" * 40
OTHER = "c" * 40


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"autonomy_{name}", AUTONOMY / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def bar(monkeypatch):
    """A fresh module per test — `_DIGEST_CACHE` is process state and must not leak between cases."""
    module = _load("publish_bar")
    monkeypatch.setattr(module, "_DIGEST_CACHE", {})
    return module


def _digests(bar, mapping):
    """Seed the digest cache so no test in this file depends on git or on a real deliverable set.

    ⚠ SEEDING THE CACHE IS THE INJECTION POINT ON PURPOSE. Monkeypatching `_covers` itself would
    test nothing — the thing under test is the comparison it makes.
    """
    bar._DIGEST_CACHE.update({(PAPER, sha): digest for sha, digest in mapping.items()})


# ---------------------------------------------------------------- the re-anchoring itself


def test_a_review_of_the_same_bytes_at_another_commit_covers_this_one(bar):
    _digests(bar, {POSTED: "same", ROUND: "same"})
    assert bar._covers(PAPER, ROUND, POSTED) is True


def test_a_review_of_different_bytes_does_not_cover_this_one(bar):
    _digests(bar, {POSTED: "here", ROUND: "elsewhere"})
    assert bar._covers(PAPER, ROUND, POSTED) is False


def test_an_exact_commit_match_still_passes_without_consulting_any_digest(bar):
    """⛔ NOTHING THE OLD TEST ACCEPTED MAY NOW BE REFUSED. The cache is left EMPTY, so if this
    reached the digest path at all it would read None and fail closed."""
    assert bar._covers(PAPER, POSTED, POSTED) is True
    assert bar._DIGEST_CACHE == {}


@pytest.mark.parametrize("mapping", [
    {POSTED: None, ROUND: "same"},
    {POSTED: "same", ROUND: None},
    {POSTED: None, ROUND: None},
])
def test_a_digest_that_cannot_be_built_refuses_rather_than_matching(bar, mapping):
    """⛔ FAIL CLOSED. `deliverable_digest` returns None when any member of the set is unreadable,
    and two unreadable sets are not 'the same paper' — None == None must never clear a clause."""
    _digests(bar, mapping)
    assert bar._covers(PAPER, ROUND, POSTED) is False


@pytest.mark.parametrize("reviewed", [None, "", 17, [], {}])
def test_a_record_with_no_usable_reviewed_commit_is_refused(bar, reviewed):
    _digests(bar, {POSTED: "same"})
    assert bar._covers(PAPER, reviewed, POSTED) is False


# ------------------------------------------------- a round is the seats filed at ONE commit


def test_seat_records_bind_to_the_rounds_own_commit_and_do_not_pool_across_rounds(bar, tmp_path,
                                                                                 monkeypatch):
    """⛔ THE REGRESSION THIS FILE'S HEADER DESCRIBES, ASSERTED DIRECTLY.

    Two rounds, two commits, identical bytes. `_seat_records` must return only the round asked for.
    If it ever pools by digest again, the older round's blocker becomes permanently unclearable and
    the clause can never be satisfied.
    """
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path)
    _digests(bar, {POSTED: "same", ROUND: "same", OTHER: "same"})
    for sha, blockers in ((ROUND, []), (OTHER, [{"summary": "an older round's finding"}])):
        (tmp_path / f"{PAPER}-{sha}-seat-lens.json").write_text(json.dumps({
            "blind": True, "reviewed_commit": sha, "blockers": blockers, "p1s": []}))

    seats, names = bar._seat_records(PAPER, ROUND)
    assert names == [f"{PAPER}-{ROUND}-seat-lens.json"]
    assert [s["blockers"] for s in seats] == [[]]


def test_a_record_filed_under_this_rounds_name_but_reviewing_another_commit_is_refused(
        bar, tmp_path, monkeypatch):
    """⛔ THE FIELD BINDS, NOT ONLY THE FILENAME — AND THIS TEST EXISTS BECAUSE MUTATION TESTING
    SHOWED ITS SIBLING ABOVE COULD NOT SEE THE DIFFERENCE.

    `_seat_records` globs `{pub}-{sha}*.json` AND checks `reviewed_commit == sha`. Replacing that
    field check with `_covers` — the pooling regression — survived the sibling test, because there
    the two records also had different filenames and the glob alone excluded the intruder. So the
    test proved the glob and said nothing about the check.

    Here the filename matches this round's prefix and the record's own `reviewed_commit` names a
    DIFFERENT commit with an identical digest. Only the field check can refuse it, and it must:
    a record is a claim about what a reviewer read, and the filename is not that claim.
    """
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path)
    _digests(bar, {ROUND: "same", OTHER: "same"})
    (tmp_path / f"{PAPER}-{ROUND}-seat-lens.json").write_text(json.dumps({
        "blind": True, "reviewed_commit": OTHER, "blockers": [], "p1s": []}))

    seats, names = bar._seat_records(PAPER, ROUND)
    assert (seats, names) == ([], [])


def test_the_round_history_counts_rounds_and_therefore_counts_commits(bar, tmp_path, monkeypatch):
    """⛔ KEYING `_look_history` BY DIGEST IS A LOOSENING AND MUST STAY REFUSED.

    Two earlier rounds read identical bytes. Keyed by commit they are two rounds of one seat each;
    keyed by digest they collapse into a single bucket — and because the declaring round is excluded
    from `priors` by its own key, that collapse would drop BOTH earlier looks out of the comparison.
    """
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path)
    _digests(bar, {ROUND: "same", OTHER: "same"})
    for sha in (ROUND, OTHER):
        (tmp_path / f"{PAPER}-{sha}-seat-lens.json").write_text(json.dumps({
            "blind": True, "reviewed_commit": sha, "blockers": [], "p1s": []}))

    assert bar._look_history(PAPER) == {ROUND: 1, OTHER: 1}


# ---------------------------------------------------------------- clause 6's roll-up search


def test_clause_six_accepts_a_rollup_filed_at_another_commit_that_read_the_same_paper(bar, tmp_path,
                                                                                     monkeypatch):
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path)
    _digests(bar, {POSTED: "same", ROUND: "same"})
    (tmp_path / f"{PAPER}-{ROUND}.json").write_text(json.dumps({
        "blind": True, "reviewed_commit": ROUND, "blockers": [], "p1s": []}))

    found, _err = bar._rollup_covering(PAPER, POSTED, "absent")
    assert found is not None and found["reviewed_commit"] == ROUND


def test_clause_six_will_not_choose_between_two_rollups_that_both_cover(bar, tmp_path, monkeypatch):
    """⛔ AMBIGUITY REFUSES. Picking the first one sorted would make this function decide which
    review speaks for the paper, which is the judgement a clause may not make for itself."""
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path)
    _digests(bar, {POSTED: "same", ROUND: "same", OTHER: "same"})
    for sha in (ROUND, OTHER):
        (tmp_path / f"{PAPER}-{sha}.json").write_text(json.dumps({
            "blind": True, "reviewed_commit": sha, "blockers": [], "p1s": []}))

    found, err = bar._rollup_covering(PAPER, POSTED, "absent")
    assert found is None
    assert "will not choose" in err


def test_the_rollup_search_never_returns_a_single_lens_seat_file(bar, tmp_path, monkeypatch):
    """⛔ A ROLL-UP ONLY. Clause 6 asks for the round's canonical adversarial record; letting a
    `-seat-` file stand in would let one lens speak for the round's verdict."""
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path)
    _digests(bar, {POSTED: "same", ROUND: "same"})
    (tmp_path / f"{PAPER}-{ROUND}-seat-lens.json").write_text(json.dumps({
        "blind": True, "reviewed_commit": ROUND, "verdict": "supported"}))

    found, _err = bar._rollup_covering(PAPER, POSTED, "absent")
    assert found is None


def test_an_unblind_rollup_is_never_returned_however_well_it_covers(bar, tmp_path, monkeypatch):
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path)
    _digests(bar, {POSTED: "same", ROUND: "same"})
    (tmp_path / f"{PAPER}-{ROUND}.json").write_text(json.dumps({
        "blind": False, "reviewed_commit": ROUND, "verdict": "supported"}))

    found, _err = bar._rollup_covering(PAPER, POSTED, "absent")
    assert found is None
