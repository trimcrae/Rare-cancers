"""⛔⛔ THE REGISTER SCREEN'S SCOPE IS A PARTITION OF THE GRAPH. SILENCE ABOUT A PAPER FAILS HERE.

`lint_style.TARGETS` is this repository's stated ONE HOME for "is this a submission text", and
`lint_readability._targets` imports it precisely so the pair cannot drift. Both then read a list
somebody typed by hand, while `systems/graph/publications.json` is the source of truth for what a
publication endpoint IS. Measured 2026-08-28 at origin/main 170314393, the first time the two sets
were compared: 25 graph endpoints resolve to a `.md` on disk, 7 are in `TARGETS`, and 18 were in
neither `TARGETS` nor any record saying why not.

★★ WHY THAT IS A DEFECT AND NOT A PREFERENCE. `publish_bar.clause_7_readable_enough_to_review`
measures the outgoing document directly, so its SENTENCE-CEILING half fires for any endpoint. Its
CAUTION-FLOOR half — the one `lint_readability`'s docstring calls the failure mode that matters, a
paper buying readability by dropping a hedge — compares against `readability-baseline.json`, which
is written from `TARGETS`. For an endpoint absent from `TARGETS` the lookup returns None and the
clause returns PASS reading "no baseline pinned". A clause that cannot fail, reported as passing, in
the file whose docstring says an unreadable artifact is a FAILED clause and never a skipped one.
The failure is invisible until that one paper's bar is run, which is the moment it is least useful.

⛔ AND THE FIX IS NOT THE OBVIOUS ONE. Adding the 18 paths to `TARGETS` was measured before it was
rejected: `lint_style.lint_file` over them returns 2795 findings, 1170 from the degrader paper
alone, because several are internal program documents whose callout glyphs are correct for their
reader. That change reddens the commit loop on documents nobody is submitting, and a gate that reds
on true input is the gate somebody loosens. So what this file asserts is not that every endpoint is
screened. It asserts that every endpoint has been DECIDED about, in a committed record, with a
basis a machine can re-check.

★ THE SHAPE IS `test_the_census_reads_every_publication_endpoint.py`, and it is copied on purpose:
the class is asserted, and the one instance that prompted the work is asserted SEPARATELY, so that
dropping it takes a deliberate edit here rather than an edit to the graph somewhere else. That file
records the measured reason — 6 of 11 list-scoped fixes regressed at a sibling, 3 of them at a
sibling their own comment named.

⚠ NOTE ON THIS FILE'S OWN STRING LITERALS, for the same reason that file carries one:
`claim_coverage._test_patterns` harvests regex-shaped string literals out of any test module that
names a document and credits them to that document. This module names manuscripts by path. Literals
here therefore avoid parentheses, brackets and backslash escapes, which is the shape it harvests on.
"""
from __future__ import annotations

import io
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lint_style  # noqa: E402
import lint_readability  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))

FUSION_PARTNER = "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md"

#: The two decisions a row may record. `not_a_submission_text` is a decided exemption resting on the
#: graph's own venue; `unscreened_debt` is a recorded defect that carries a number and must fall.
DECIDED = "not_a_submission_text"
DEBT = "unscreened_debt"

#: A venue that aims a document at a reader outside this repository. CLAUDE.md section 6: a
#: submission is the only moment anything here reaches an outside reader.
OUTWARD_VENUES = {"preprint", "journal_submission"}


def endpoints() -> dict:
    """Every graph publication endpoint that resolves to a markdown file on disk, id by path.

    ⛔ DERIVED, NEVER TYPED. The whole finding is that a typed scope diverges from the record; a
    guard that typed its own expectation would reproduce the defect inside the instrument.
    """
    graph = json.load(io.open(os.path.join(REPO, "systems", "graph", "publications.json"),
                              encoding="utf-8"))
    out = {}
    for entry in graph:
        if entry.get("kind") != "publication":
            continue
        rel = (entry.get("document") or {}).get("file")
        if rel and rel.endswith(".md") and os.path.exists(os.path.join(REPO, rel)):
            out[rel] = entry
    return out


def test_the_graph_still_names_publication_endpoints_that_exist():
    """⛔ A GATE THAT COMPARED TWO EMPTY SETS WOULD BE GREEN AND WOULD ASSERT NOTHING."""
    found = endpoints()
    assert found, (
        "no publication endpoint in the systems graph resolves to a file on disk, so every "
        "assertion below compared against an empty set. Read the graph, not this failure message.")
    assert set(lint_style.TARGETS) & set(found), (
        "no element of lint_style.TARGETS is a publication endpoint on disk. Either the graph "
        "changed shape or TARGETS has drifted off the record entirely; both are bigger than the "
        "divergence this file was written for.")


def test_every_publication_endpoint_is_screened_or_recorded():
    """⛔⛔ THE CLASS. In TARGETS, or in the record, and never in neither.

    This is the assertion the repository did not have. A manuscript added to the graph tomorrow is
    unscreened by default and nothing said so; from here it makes this test red until somebody
    writes down which of the two it is and why.
    """
    found = endpoints()
    screened = set(lint_style.TARGETS)
    recorded = set(lint_style.UNSCREENED_ENDPOINT_DECISIONS)

    undecided = sorted(rel for rel in found if rel not in screened and rel not in recorded)
    assert not undecided, (
        "the systems graph calls these documents publication endpoints, lint_style.TARGETS does "
        "not screen them, and no row in lint_style.UNSCREENED_ENDPOINT_DECISIONS says why:\n  "
        + "\n  ".join(f"{found[rel]['id']}  {rel}" for rel in undecided)
        + "\n\nAn endpoint outside TARGETS is also outside lint_readability, outside "
          "readability-baseline.json, and therefore outside the caution half of publish_bar clause "
          "7, which returns PASS for it while measuring nothing. Add it to TARGETS if it is a "
          "submission text, or record the decision. Do NOT delete this expectation.")


def test_nothing_is_both_screened_and_recorded_as_unscreened():
    """⛔ A STALE ROW IS WORSE THAN A MISSING ONE — it describes a document that moved on.

    A path added to TARGETS whose exemption row survives leaves two records disagreeing, and the
    one a reader meets last wins. lint_style.py already carries a superseded comment recording
    exactly that failure: two comments in one gate described two different regimes.
    """
    both = sorted(set(lint_style.TARGETS) & set(lint_style.UNSCREENED_ENDPOINT_DECISIONS))
    assert not both, (
        "these paths are screened by TARGETS and simultaneously recorded as unscreened:\n  "
        + "\n  ".join(both)
        + "\n\nThe row has outlived its decision. Delete it: the document is screened now.")


@pytest.mark.parametrize("rel", sorted(lint_style.UNSCREENED_ENDPOINT_DECISIONS))
def test_each_recorded_decision_still_describes_a_real_endpoint(rel):
    """⛔ AN EXEMPTION FOR A FILE NOTHING MEASURES IS A ROW NOBODY CAN EVER DELETE.

    Every row must name a document that exists AND that the graph still calls a publication
    endpoint. A row for a file that has been deleted, renamed or demoted is excusing nothing and
    would sit here forever reading like a decision.
    """
    row = lint_style.UNSCREENED_ENDPOINT_DECISIONS[rel]
    assert os.path.exists(os.path.join(REPO, rel)), (
        f"{rel} is recorded as an unscreened publication endpoint and does not exist. If it was "
        "renamed, move the row; if it was deleted, delete the row.")
    found = endpoints()
    assert rel in found, (
        f"{rel} carries a decision row and the systems graph no longer calls it a publication "
        "endpoint on disk. The row is excusing a document nothing else treats as a paper, so it "
        "should go.")
    assert row.get("decision") in {DECIDED, DEBT}, (
        f"{rel} records decision {row.get('decision')!r}, which is neither {DECIDED!r} nor "
        f"{DEBT!r}. A third category is a place to hide a document; add one deliberately, in the "
        "record's own comment, or use one of the two.")
    why = row.get("why", "")
    assert isinstance(why, str) and len(why) >= 120, (
        f"the decision for {rel} does not say enough to be disagreed with. Record the venue, what "
        "the screen measures on the document today, and what would change the decision — or the "
        "row is indistinguishable from the silence this file exists to refuse.")


@pytest.mark.parametrize("rel", sorted(lint_style.UNSCREENED_ENDPOINT_DECISIONS))
def test_each_decision_is_re_checked_against_the_venue_it_was_taken_against(rel):
    """⛔⛔ THE HALF THAT EXPIRES BY ITSELF. A venue change reopens the decision with no one asking.

    Every row names the target_venue the graph gave the document when the decision was taken. That
    is the whole basis of a not_a_submission_text row: the record, not this file, says the document
    is aimed at no outside reader. Re-reading it means a document re-aimed from internal_note to
    preprint goes red HERE, on the commit that re-aims it, rather than at the publish bar much
    later. It is the shape test_the_census_reads_every_publication_endpoint.py uses for the
    correction register: an exclusion defended by a comment is an exclusion nobody can falsify.
    """
    row = lint_style.UNSCREENED_ENDPOINT_DECISIONS[rel]
    entry = endpoints()[rel]
    was, now = row.get("venue_when_decided"), entry.get("target_venue")
    assert was == now, (
        f"{rel} was decided against target_venue {was!r} and the graph now says {now!r}. The "
        "decision rests on the venue, so it has to be re-taken rather than re-stamped: a document "
        "newly aimed at an outside reader belongs in TARGETS or in a debt row that says why not.")

    if row["decision"] == DECIDED:
        assert now not in OUTWARD_VENUES, (
            f"{rel} is exempted as not a submission text while the graph aims it at {now!r}, which "
            "is an outward venue. That is the exemption doing the one thing it must never do: "
            "taking a document that WILL reach an outside reader out of the register screen.")
    else:
        assert now in OUTWARD_VENUES, (
            f"{rel} is recorded as unscreened DEBT — a defect to clear before it goes out — while "
            f"the graph aims it at {now!r}, which reaches no outside reader. It is not a debt; it "
            "is an exemption, and it should be recorded as one so nobody works to clear it.")


@pytest.mark.parametrize(
    "rel", sorted(k for k, v in lint_style.UNSCREENED_ENDPOINT_DECISIONS.items()
                  if v["decision"] == DEBT))
def test_a_recorded_debt_may_fall_and_may_not_rise(rel):
    """⛔ AN UNSCREENED DOCUMENT MAY NOT GET WORSE WHILE IT WAITS, AND MAY NOT STAY WHEN IT IS CLEAN.

    Each debt row pins what lint_style.lint_file measured on the day it was filed. Re-measuring here
    is what stops the record becoming a permanent parking space: the count may FALL, which is a
    register pass in progress, and may not RISE, which is a document drifting further from the
    register with no instrument watching. It is the contract submission-residue-baseline.json
    already states in its own words, that the count is meant to fall.

    ★ AND ZERO FAILS TOO, which is the half that retires the row. A document the screen would pass
    is a document that belongs in TARGETS; leaving it recorded as unscreened is this defect again,
    one document smaller.
    """
    row = lint_style.UNSCREENED_ENDPOINT_DECISIONS[rel]
    was = row.get("findings_when_filed")
    assert isinstance(was, int) and was > 0, (
        f"the debt row for {rel} pins no finding count, so nothing holds it and nothing falsifies "
        "it. A debt without a number is an exemption with a longer sentence.")

    result = lint_style.lint_file(rel)
    assert result is not None, f"lint_style could not read {rel}"
    now = len(result["findings"])

    assert now > 0, (
        f"{rel} is recorded as unscreened debt and lint_style now finds NOTHING in it. The debt is "
        "paid: move the path into lint_style.TARGETS, delete this row, and re-pin "
        "readability-baseline.json with --write-baseline so that publish_bar clause 7's caution "
        "half has something to compare against for this paper.")
    assert now <= was, (
        f"{rel} was pinned at {was} findings and now measures {now}. An endpoint outside TARGETS is "
        "read by no register gate, so it can drift indefinitely and nothing notices; that is what "
        "this assertion is for. Fix the DOCUMENT. Lowering the pinned number to match is the edit "
        "this test exists to make visible.")


def test_the_fusion_partner_manuscript_is_recorded_rather_than_silently_unscreened():
    """⭐ THE INSTANCE, ASSERTED SEPARATELY FROM THE CLASS ABOVE.

    The class test stays green if the graph stops calling this paper an endpoint. This one says the
    specific document is accounted for, so removing it takes a deliberate edit here.

    It is the same manuscript test_the_census_reads_every_publication_endpoint.py was written for.
    Its docstring records that the paper was a live publication endpoint being hardened by blind
    review seats while the claim census did not list it at all. Measured here two days later: it was
    outside the register screen and outside readability-baseline.json for the whole of that
    hardening as well. One document, two instruments, the same defect, found separately — which is
    the argument for asserting the class above rather than fixing the instance.
    """
    assert FUSION_PARTNER in endpoints(), (
        "the fusion-partner stratification manuscript is no longer a publication endpoint on disk. "
        "That is a real change to re-take deliberately, not a reason to delete this test.")
    if FUSION_PARTNER in lint_style.TARGETS:
        # ⭐ THE DEBT WAS CLEARED AND THAT IS THE GOOD OUTCOME. Once the manuscript is screened,
        # the class test and the no-row-for-a-screened-file test hold it, and a decision row for
        # it would be the stale-row defect. So this branch is a pass, not a skip.
        return
    row = lint_style.UNSCREENED_ENDPOINT_DECISIONS.get(FUSION_PARTNER)
    assert row is not None, (
        "the fusion-partner manuscript is neither screened by lint_style.TARGETS nor recorded as a "
        "known-unscreened endpoint. It is the document this whole file was written about: a live "
        "endpoint hardened by four blind review rounds with no register instrument reading it.")
    assert row["decision"] == DEBT, (
        "the fusion-partner manuscript is recorded as not a submission text. The graph aims it at "
        "a preprint, so it reaches an outside reader and the register applies to it; it is a debt "
        "to clear, not a document to exempt.")


def test_the_readability_screen_covers_exactly_what_the_style_screen_screens():
    """⛔ THE PAIR THAT MUST NOT DRIFT, ASSERTED RATHER THAN TRUSTED TO AN IMPORT.

    lint_readability._targets imports lint_style.TARGETS so the two screens cannot diverge, and the
    comment above that import says so. This asserts the invariant instead of the mechanism: a future
    edit that gives lint_readability its own list would satisfy the comment and break the property,
    which is the one-of-a-pair defect this repository has now paid for eight times.

    ⚠ It also fixes WHY the divergence recorded in this file reaches the publish bar. Because the
    readability screen's scope IS the style screen's scope, an endpoint absent from TARGETS is
    absent from both, and therefore has no pinned caution baseline for clause 7 to compare against.
    """
    screened = [t for t in lint_style.TARGETS
                if os.path.exists(os.path.join(REPO, t))]
    assert lint_readability._targets([]) == screened, (
        "the readability screen's default scope is no longer lint_style.TARGETS filtered to files "
        "that exist. The two screens now disagree about what a submission text is, which is the "
        "drift the import was written to prevent.")


def test_the_caution_baseline_covers_every_screened_document():
    """⛔ THE CLAUSE-7 CONSEQUENCE, ASSERTED WHERE IT CAN BE SEEN.

    publish_bar clause 7 fails a paper whose caution markers FALL against readability-baseline.json.
    A screened document missing from that file gets `was is None`, and the clause returns PASS
    saying "no baseline pinned" — passing on a check it did not make.

    ⚠ THIS IS DELIBERATELY SCOPED TO TARGETS AND NOT TO THE GRAPH. The 15 debt rows recorded in
    lint_style.UNSCREENED_ENDPOINT_DECISIONS have no baseline BY CONSTRUCTION, and pinning one for
    a document nobody has put through a register pass would manufacture a baseline from prose the
    screen has never read. The debt rows are the record that those papers are uncovered; this
    asserts that nothing which IS screened is uncovered by accident.
    """
    baseline = json.load(io.open(
        os.path.join(MANUSCRIPTS, "readability-baseline.json"), encoding="utf-8"))
    pinned = set(baseline.get("caution_per_1000w", {}))
    screened = {t for t in lint_style.TARGETS if os.path.exists(os.path.join(REPO, t))}
    missing = sorted(screened - pinned)
    assert not missing, (
        "these documents are screened by lint_style.TARGETS and carry no pinned caution baseline:\n"
        "  " + "\n  ".join(missing)
        + "\n\npublish_bar clause 7 will return PASS for each of them on the caution half while "
          "comparing against nothing. Re-pin with: python3 research/manuscripts/"
          "lint_readability.py --write-baseline, and say in the commit message what changed.")
