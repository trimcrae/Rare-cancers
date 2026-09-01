"""⛔⛔ A ROW WHOSE ONLY OUTWARD ACT IS ONE A STANDING GRANT ALREADY PERMITS IS NOT A DECISION.

⚠ THIS FILE EXISTS BECAUSE THE RULE WAS WRITTEN TWICE IN PROSE AND BROKEN A THIRD TIME.
CLAUDE.md §3 has said since 2026-08-29 that "aiXiv PREPRINTS ARE NOT GATED ON TRIMCRAE, AND NEVER
HAVE BEEN", in a bullet added *because* a session had already misread it once. On 2026-09-01 a
session escalated AUT-073 ("publish the eligibility map") anyway. trimcrae, verbatim:

    "You don't need my permission to post to aixiv ever. That should be written into your rules.
     This was not a good use of escalation"

★ THE MECHANISM, WHICH IS THE PART WORTH KEEPING: `requires_trimcrae` was never computed. It was
hand-typed onto a row once, and `merge()`'s forward-compat `setdefault` loop then carried it across
every re-score for ever — so a judgement made in one session became a permanent property nothing
re-examined. The rule was not weak; it was unreachable, in exactly the way CLAUDE.md §1 records for
`subagent_width` (a governed number two documents asserted and no code read).

⛔ SO THE TESTS BELOW BIND THE DIRECTION, NOT JUST THE BEHAVIOUR. `_aixiv_grant_covers` may only
ever REMOVE a false escalation. Every test that could pass by making the loop escalate LESS has a
sibling asserting the case where it must still escalate — because a row wrongly cleared is a
decision that never gets made, and that is the expensive direction.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "research" / "autonomy"))

import priority  # noqa: E402


# --------------------------------------------------------------------------------------
# The venue test
# --------------------------------------------------------------------------------------

def test_a_preprint_endpoint_under_the_standing_grant_is_covered():
    assert priority._aixiv_grant_covers({"id": "PUB-ANYTHING", "target_venue": "preprint"}) is True


def test_a_journal_endpoint_is_never_covered():
    """⛔ D4: every journal submission still escalates immediately. The grant says "aiXiv only —
    no other venue, ever", so a venue the grant does not name is his by default and not by
    exception."""
    assert priority._aixiv_grant_covers(
        {"id": "PUB-X", "target_venue": "journal_submission"}) is False


def test_an_endpoint_with_no_venue_is_not_covered():
    """An absent reading is not a reading of absence (CLAUDE.md §4). No venue means the act is
    unknown, and an unknown act stays his."""
    assert priority._aixiv_grant_covers({"id": "PUB-X"}) is False
    assert priority._aixiv_grant_covers({"id": "PUB-X", "target_venue": None}) is False


def test_a_missing_endpoint_is_not_covered():
    assert priority._aixiv_grant_covers(None) is False
    assert priority._aixiv_grant_covers("PUB-X") is False


def test_the_excluded_paper_stays_his():
    """⛔ PUB-ASO is named in the grant's own deny-list, by trimcrae, 2026-08-27: "That's the only
    paper that shouldn't auto ship to aiXiv." It lives on Qeios under a DOI whose version history
    he controls. This test reads the LIVE authority file — if someone removes PUB-ASO from
    `excluded_papers`, this goes red, which is the point."""
    authority = json.loads((REPO / "research/autonomy/publication-authority.json").read_text())
    excluded = authority["aixiv"]["scope"]["excluded_papers"]
    assert "PUB-ASO" in excluded, (
        "PUB-ASO left the aiXiv deny-list. Re-widening that grant is not an amendment the loop may "
        "make — only trimcrae issues one.")
    assert priority._aixiv_grant_covers({"id": "PUB-ASO", "target_venue": "preprint"}) is False


def test_the_grant_being_switched_off_uncovers_everything(tmp_path, monkeypatch):
    """⛔ THE GRANT IS READ, NEVER REMEMBERED. If `standing_grant` is ever false, every row goes
    back to being his — the code must not carry a memory of a permission that was withdrawn."""
    fake = tmp_path / "authority.json"
    fake.write_text(json.dumps({"aixiv": {"standing_grant": False,
                                          "scope": {"excluded_papers": {}}}}))
    monkeypatch.setattr(priority, "AUTHORITY_FILE", fake)
    assert priority._aixiv_grant_covers({"id": "PUB-X", "target_venue": "preprint"}) is False


def test_an_unreadable_authority_file_fails_closed(tmp_path, monkeypatch):
    """Cannot read the grant -> cannot claim it covers anything."""
    monkeypatch.setattr(priority, "AUTHORITY_FILE", tmp_path / "does-not-exist.json")
    assert priority._aixiv_grant_covers({"id": "PUB-X", "target_venue": "preprint"}) is False

    broken = tmp_path / "broken.json"
    broken.write_text("{ not json")
    monkeypatch.setattr(priority, "AUTHORITY_FILE", broken)
    assert priority._aixiv_grant_covers({"id": "PUB-X", "target_venue": "preprint"}) is False


# --------------------------------------------------------------------------------------
# The second-act screen — the half that KEEPS escalations
# --------------------------------------------------------------------------------------

def test_a_row_that_also_names_outreach_is_not_cleared():
    """⚠ THE CASE THAT MADE THIS SCREEN NECESSARY, AND IT IS A REAL ROW. AUT-046 reads "Post the
    preprint and put the MTAP stain in front of a group holding EMC archival material." The venue
    test clears the posting half; the outreach half is under trimcrae's name and no grant reaches
    it. Clearing the row would delete a genuine decision on the strength of a venue field that
    describes only half of it."""
    assert priority._names_an_act_beyond_posting({
        "what": "Post the preprint and put the MTAP stain in front of a group holding EMC "
                "archival material."}) is True


@pytest.mark.parametrize("text", [
    "email the corresponding author",
    "Contact the registry maintainers",
    "approach a group holding archival material",
    "reach out to the consortium",
    "mint a Zenodo DOI for the archive",
    "cut a release",
    "post a new version to Qeios",
    "prepare the journal submission",
])
def test_every_second_act_verb_retains_the_escalation(text):
    assert priority._names_an_act_beyond_posting({"what": text}) is True


@pytest.mark.parametrize("text", [
    "Post the preprint at research/manuscripts/foo/bar.md",
    "Publish the assessment with the class-inheritance limit stated inside it",
    "Publish the eligibility map",
])
def test_a_posting_only_row_is_not_retained_by_the_screen(text):
    """⚠ THE SIBLING THAT STOPS THIS SCREEN FROM BEING VACUOUS. A regex tuned to keep everything
    would pass every test above and clear nothing, which is the state we started in."""
    assert priority._names_an_act_beyond_posting({"what": text}) is False


def test_the_screen_reads_the_why_fields_too():
    """The second act is often named in `requires_trimcrae_why` rather than in `what`."""
    assert priority._names_an_act_beyond_posting({
        "what": "Publish it.",
        "requires_trimcrae_why": "also needs an email to the collaborator"}) is True


# --------------------------------------------------------------------------------------
# End to end, against the committed graph
# --------------------------------------------------------------------------------------

def test_the_row_that_caused_this_is_no_longer_a_decision():
    """AUT-073 / PUB-STRATEGY-ARCH — the row escalated on 2026-09-01 and answered
    "This was not a good use of escalation"."""
    rows = {e["id"]: e for e in priority.build_entries()}
    assert rows["AUT-073"]["serves"]["publication"] == "PUB-STRATEGY-ARCH"
    assert rows["AUT-073"]["requires_trimcrae"] is False


def test_a_cleared_row_says_why_and_says_it_is_derived():
    rows = {e["id"]: e for e in priority.build_entries()}
    why = rows["AUT-073"]["_requires_trimcrae_why"]
    assert "DERIVED" in why and "PUB-STRATEGY-ARCH" in why


def test_clearing_is_written_explicitly_so_merge_cannot_resurrect_the_stale_value():
    """⛔ THE BUG THIS WHOLE CHANGE IS ABOUT. `merge()` ends with `entry.setdefault(key, value)`
    over every key of the previous row, so a key `build_entries` OMITS is refilled from the stale
    row. A cleared row must therefore carry the key with the literal value False — not None, and
    not absent — or the next re-score silently restores the escalation."""
    cleared = [e for e in priority.build_entries() if e.get("requires_trimcrae") is False]
    assert cleared, "nothing was cleared; the venue test or the graph changed"
    for e in cleared:
        assert "requires_trimcrae" in e
        assert e["requires_trimcrae"] is False


def test_a_real_row_with_a_second_act_is_not_cleared_end_to_end():
    """⛔⛔ THE TEST THE MUTATION RUN DEMANDED, AND THE ONE THIS FILE WAS MISSING.

    Mutation M4 — deleting `and not _names_an_act_beyond_posting(entry)` from `build_entries` —
    left the whole suite green, because every end-to-end assertion here was about AUT-073, which
    names only a posting act. The unit tests for the screen passed while the screen was wired out of
    the pipeline entirely: a guard tested in isolation and unreachable in production, which is the
    same one-of-a-pair shape `paper-hardening` records seven instances of.

    AUT-046 is the live row that discriminates: "Post the preprint and put the MTAP stain in front
    of a group holding EMC archival material." Its endpoint PUB-MTAP-PRMT5 is aimed at `preprint`,
    so the venue test alone WOULD clear it — and the outreach half is trimcrae's under §3, covered
    by no grant.
    """
    rows = {e["id"]: e for e in priority.build_entries()}
    row = rows["AUT-046"]
    assert row["serves"]["publication"] == "PUB-MTAP-PRMT5"
    assert priority._aixiv_grant_covers(
        {"id": "PUB-MTAP-PRMT5", "target_venue": "preprint"}) is True, (
        "the venue test no longer clears this endpoint, so this test has stopped discriminating "
        "— it would pass for the wrong reason")
    assert row.get("requires_trimcrae") is not False, (
        "AUT-046 was cleared by the standing-grant pass, but it names an outreach act no grant "
        "reaches. The second-act screen is disabled or has stopped matching this row.")


def test_no_row_is_ever_set_true_by_this_pass():
    """⛔ THE DIRECTION INVARIANT, AND IT IS THE ONE THAT MATTERS. This pass may only remove a false
    escalation. If it ever starts ASSERTING that something is trimcrae's, it has taken on a
    judgement `apply_requires_trimcrae`'s docstring says is unreachable at derive time — and it
    would be doing it from a venue field, which cannot support that claim."""
    assert not [e for e in priority.build_entries() if e.get("requires_trimcrae") is True]
