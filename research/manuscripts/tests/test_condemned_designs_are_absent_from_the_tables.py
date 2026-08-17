"""The three condemned designs must stay out of the ordering tables, and the header must say so truly.

⛔ WHY. The generated tables file is the one document a laboratory prints and orders from, and its
research-use header is its safety notice. Until 2026-08-17 that header read: "Three of the sequences
below are named in the main text as designs NOT to be carried forward" — and **none of the three was
in the file**. A cold reader went looking for three unsafe rows, found none, and the nearest-looking
candidates were the two reagents the paper actually recommends at those same seams, one of which
(`CAGTGGGCTTCTGCTG`) differs from a condemned sequence (`CAGTGGGCTCTCCACG`) by a glance.

⚠ THE HEADER WAS WRONG IN THE SAFE DIRECTION AND THAT IS NOT A DEFENCE. Pointing at absent danger
teaches a reader to distrust the notice, and the same sentence would have been the only warning if a
condemned design ever DID reach a table. So both directions are pinned here:

  * the three sequences are absent from the tables — the substantive safety property; and
  * the header describes that absence rather than asserting a presence.

⭐ THE SEQUENCES ARE READ FROM THE MANUSCRIPT, NOT TYPED HERE. A guard holding its own copy of the
list would keep passing after §2.6 condemned a fourth design, which is the failure mode it exists to
prevent. §2.6 names them in one sentence, and that sentence is the source of truth.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASO = os.path.join(REPO, "research", "manuscripts", "aso")
PAPER = os.path.join(ASO, "fusion-junction-aso-research-article.md")
TABLES = os.path.join(ASO, "fusion-junction-aso-submission-tables.md")

#: The §2.6 sentence that condemns them, anchored on its verdict rather than on a section number.
_CONDEMNED_CLAUSE = "are named here as not to be carried forward"


def _flat(path):
    return " ".join(open(path, encoding="utf-8").read().split())


def _condemned_sequences():
    """The designs §2.6 names as not to be carried forward, read from the manuscript.

    The sentence runs "... All three are named here as not to be carried forward and are excluded
    from every best-design field above." Sequences in this manuscript are always written
    5′-XXXX-3′, so the window before that clause is scanned for that form.
    """
    txt = _flat(PAPER)
    i = txt.find(_CONDEMNED_CLAUSE)
    assert i != -1, (
        f"the clause {_CONDEMNED_CLAUSE!r} has left the manuscript. It is how this guard finds the "
        "condemned designs; re-anchor it on whatever sentence now condemns them rather than "
        "deleting this test.")
    window = txt[max(0, i - 1200):i]
    seqs = re.findall(r"5[′']-([ACGT]{12,25})-3[′']", window)
    # Deduplicate, order-preserving: the window also restates the seams, and a repeat is not a
    # fourth design.
    out = list(dict.fromkeys(seqs))
    assert len(out) >= 3, (
        f"expected at least three condemned designs in the sentence before {_CONDEMNED_CLAUSE!r}, "
        f"found {out}. If §2.6 was restructured, re-derive this window.")
    return out


def test_no_condemned_design_appears_in_the_ordering_tables():
    tables = _flat(TABLES)
    present = [s for s in _condemned_sequences() if s in tables]
    assert not present, (
        f"{len(present)} design(s) the main text condemns are printed in the ordering tables: "
        f"{present}. Each pairs its whole catalytic gap against the patient's own un-rearranged "
        "NR4A3 allele. Remove the row at the GENERATOR (research/manuscripts/submission_tables.py) "
        "— a table a laboratory orders from must not carry a sequence the paper says not to carry "
        "forward.")


def test_the_research_use_header_describes_the_absence_rather_than_asserting_a_presence():
    """The header must not send a reader hunting for rows that are not there.

    ⚠ ASSERTED ON THE PROPERTY, NOT ON THE WORDING. The check is that the header does not claim the
    condemned designs are "below"/"in these tables" while the test above proves they are not; any
    phrasing that states the absence passes.
    """
    tables = _flat(TABLES)
    # Case-folded: the header emphasises the negation in caps ("NOT to be carried forward"), and
    # whether that word is shouted is a style choice this guard has no business pinning.
    assert "not to be carried forward" in tables.lower(), (
        "the research-use header no longer mentions the condemned designs at all. The main text "
        "names three designs that must not be carried forward; the ordering document is where that "
        "matters most, so the header must still address them.")
    # ⚠ MATCHED ON THE CLAIM'S SHAPE, NOT ITS EXACT WORDING: any header saying the condemned
    # sequences are "below" or "in these tables" is the defect, however it is phrased.
    low = tables.lower()
    for claim in ("sequences below are named in the main text as designs not to be carried forward",
                  "designs not to be carried forward are in these tables",
                  "of the sequences in these tables are named in the main text as designs not to be"):
        assert claim not in low, (
            "the research-use header claims three condemned sequences are IN this file, and they "
            "are not — the companion test proves their absence. Pointing a reader at danger that is "
            "not there teaches them to distrust the one notice that would matter if it ever were.")
