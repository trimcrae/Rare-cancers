#!/usr/bin/env python3
"""The three refuted interpretation claims may not come back in ANY document that makes them.

⛔ WHY THIS FILE IS SCOPED BY A PROPERTY AND NOT BY A LIST. On 2026-08-28 a claim audit
(`research/manuscripts/aso/fusion-junction-aso-claim-audit-verdicts.json`) refuted three
INTERPRETATION sentences in the journal article, each a bare universal the panel's own artifacts
contradict. Applying the refutations showed the defect had a sibling in the extended report:

  * `every design here is specific to the exon pair OR PAIRS it was tiled at — nine span more than
    one` had ALREADY been corrected in the extended report, while the journal article still read
    `every design here being specific to the exon pair it was tiled at`. The correction reached one
    document of the pair and not the other, and nothing noticed for as long as both shipped.
  * `a fusion-junction design's most plausible wild-type liability is its own parent … invisible to
    a screen that ranks candidates by global identity` was still standing in the extended report
    when the journal article's copy was corrected.

★★ A LIST IS A THING SOMEBODY MUST REMEMBER TO EXTEND, AND THE REMEMBERING IS WHAT FAILS. So the
scope here is *every shipped document that makes the claim*: a document is checked when its own text
raises the subject, which puts a document added tomorrow in scope without anybody naming it. The
SUBJECT patterns decide membership; the FORBIDDEN patterns decide the verdict.

⚠ AND THE FORBIDDEN SIDE IS A QUANTIFIER CLASS, NOT THE SENTENCE THAT WAS THERE.
`test_universal_claims_are_scoped_to_what_was_measured.py` records that five of its six sections
shipped as exact-string blacklists and that every contradiction they existed to stop could be
reinstated in synonyms with nothing turning red. Each pattern below matches the quantifier governing
the noun, and the synonym reinstatements are mutation-tested rather than left to inspection.

⚠ WHAT THIS FILE DOES NOT DO: it does not check that the corrected sentence is present or that its
numbers are right. That is
`research/manuscripts/tests/test_journal_article_numbers.py` for the journal article, which binds
both the counts and the narrowed wording. This file is the absence half, across the packet.
"""
import os
import re

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ASO = os.path.join(os.path.dirname(_HERE), "aso")

#: Every document this submission ships. Working records, review rounds and memos are absent on
#: purpose: they quote the refuted wording in order to discuss it, and a gate applied where it
#: cannot hold is a gate somebody loosens (CLAUDE.md §6).
SHIPPED = (
    "fusion-junction-aso-journal-article.md",
    "fusion-junction-aso-research-article.md",
    "fusion-junction-aso-supplementary-information.md",
    "fusion-junction-aso-submission-tables.md",
    "fusion-junction-aso-journal-tables.md",
    "fusion-junction-aso-cover-letter.md",
)

#: (claim, does this document raise the subject?, the quantifier class that may not govern it)
CLAIMS = (
    (
        "the parent liability's visibility to an ordinary off-target search",
        r"near-match|off-target search|alignment screen|global identity",
        # "never returns a parent", "returns no parent", "invisible … at any threshold"
        r"(?:never|not once|no(?:t a)? single)\s+(?:\w+\s+){0,3}returns?\s+(?:a|the|any)\s+parent"
        r"|returns?\s+no\s+parent"
        r"|cannot\s+return\s+(?:a|the|any)\s+parent"
        # ⚠ THRESHOLD AND CUT ONLY — NOT "setting". Search DEPTH is a different axis from the
        # identity threshold, and the depth claim is NOT refuted: the only field that would settle
        # it, `n_parent_or_intended_hits`, conflates parent hits with intended-target hits and so
        # bounds parent visibility from above. Matching "at any setting" made this guard red on a
        # sentence the evidence supports, which is the failure that gets a guard loosened.
        r"|invisible[^.]{0,80}\bat\s+(?:any|every|all|whatever)\s+(?:threshold|cut)"
        r"|\bat\s+(?:any|every|all|whatever)\s+threshold[^.]{0,60}invisible"
        r"|no\s+screen\s+(?:\w+\s+){0,3}(?:on\s+)?global\s+identity\s+can\s+see",
    ),
    (
        "how junction-specific the panel's designs are",
        r"exon pair|tiled at",
        r"\b(?:every|each|all|any)\s+designs?\s+(?:here\s+)?(?:being\s+|is\s+|are\s+|was\s+|were\s+)?"
        r"specific\s+to\s+(?:the|its|their)\s+exon\s+pair(?!\s+or\s+pairs)",
    ),
    (
        "which wild-type liability is the strongest",
        r"wild-type liability|its own parent",
        r"\b(?:most|more)\s+(?:plausible|likely|probable|credible)\b[^.]{0,40}\bliability"
        r"|\bliability[^.]{0,40}\b(?:most|more)\s+(?:plausible|likely|probable|credible)\b"
        r"|\b(?:strongest|principal|dominant|chief|foremost|greatest)\s+"
        r"(?:predicted\s+|wild-type\s+)?liability\s+is\s+its\s+own\s+parent",
    ),
)


def _flat(path):
    """⛔ THESE DOCUMENTS ARE HARD-WRAPPED, so almost every claim straddles a line break.

    A pattern matched against the raw file silently never fires — the failure mode where a guard
    reports a clean document because it could not read the sentence.
    """
    with open(path, encoding="utf-8") as fh:
        return re.sub(r"\s+", " ", fh.read())


@pytest.fixture(scope="module")
def documents():
    out = {}
    for name in SHIPPED:
        path = os.path.join(_ASO, name)
        assert os.path.exists(path), (
            f"{name} is named as a shipped document and is not on disk. A guard that quietly skips "
            "its subject is indistinguishable from one that passed.")
        out[name] = _flat(path)
    return out


@pytest.mark.parametrize("claim,subject,forbidden", CLAIMS,
                         ids=[c[0].split()[0] + "-" + c[0].split()[-1] for c in CLAIMS])
def test_no_shipped_document_restates_a_refuted_universal(documents, claim, subject, forbidden):
    """⛔ IF THIS FAILS, CHECK THE MEANING BEFORE THE REGEX.

    The named wording was refuted against this repository's own artifacts, and those artifacts have
    not changed. A sentence that has gone universal again looks exactly like a rewording, which is
    why the fix is almost never to loosen the pattern below.
    """
    raised = [name for name, text in documents.items() if re.search(subject, text, re.I)]
    assert raised, (
        f"no shipped document raises {claim} any more. Either the claim was dropped from the packet "
        "— in which case this guard should go with it — or the subject is now worded in a way these "
        "patterns cannot see, which is the same as no guard at all.")
    offenders = {}
    for name in raised:
        hit = re.search(forbidden, documents[name], re.I)
        if hit:
            offenders[name] = hit.group(0)
    assert not offenders, (
        f"{claim} has gone universal again in {len(offenders)} shipped document(s): "
        + "; ".join(f"{n}: {t!r}" for n, t in offenders.items())
        + ". That is the wording the 2026-08-28 claim audit refuted against the panel's own "
          "artifacts, and the artifacts have not changed.")
