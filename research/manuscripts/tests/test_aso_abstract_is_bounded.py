"""The ASO abstract has a length bound of its own, and it is this paper's rather than another's.

⛔ WHY THIS EXISTS. Until 2026-08-19 the ASO abstract had NO word guard. Its length was twice
"verified" against `ABSTRACT_WORD_LIMIT = 305` in `test_endpoint_manuscript_figures.py` — a constant
that is JNCI's structured-abstract limit, applied to a DIFFERENT manuscript
(`endpoint/response-endpoint-indolent-tumours.md`). That test reads its own `PAPER` and never opens
this one, so it passed no matter what this abstract did, and prose was trimmed out of this paper to
satisfy a constraint borrowed from another. A green test that does not read the file it is believed
to guard is worse than no test: it converts an unchecked property into a checked-looking one.

★ THE BOUND HERE IS THE DEPOSIT TARGET'S. bioRxiv sets no abstract word limit, so this is not a venue
constraint and must not be described as one. It is a drift bound: an abstract is the only part of the
paper most readers will read, and it has grown every time a reviewer asked for a qualification to be
carried into it. 380 leaves room for the qualifications this paper genuinely owes a reader — the
adopted-not-measured criterion, the by-construction share of the gap-length result, the unusable
candidate set — while failing if the abstract starts absorbing the Results.

⚠ IF A JOURNAL IS EVER TARGETED, replace this with that venue's limit and say which venue in the
constant's name. Do not silently raise this number to make an edit fit.
"""
from __future__ import annotations

import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
PAPER = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")

#: Not a venue limit — bioRxiv has none. A drift bound; see the module docstring.
#:
#: ⚠ RAISED 380 → 400 ON 2026-08-19, DELIBERATELY AND WITH THE REASON, WHICH IS WHAT THE DOCSTRING
#: ABOVE ASKS FOR. Four separate readers, working from four different briefs, each found the
#: abstract stating something the body qualifies, and each qualification was owed:
#:   · search depth moves the headline — six of nine "clean" designs are not clean at ten times
#:     the default ceiling, and the abstract said nothing about depth at all;
#:   · 87 of 190 is a rate over DESIGNS, while a laboratory picks one register at its own junction,
#:     where 35 of 38 junctions have a design that clears the screen;
#:   · every null rate quoted is computed at the ten-base-pair cut only, so the seven-base-pair
#:     reading printed beside them has no chance baseline;
#:   · the three condemned designs sit OUTSIDE the 38-junction panel and are passed by the
#:     mature-parent screen, which is what makes them interesting and was not said.
#: The abstract was trimmed by 25 words first — the pipeline sentence, the lead-reagent tail, the
#: chimera gloss and the depth clause all shortened — and 386 is what remains after that. This is
#: the bound doing its job (it forced the trim) rather than being loosened to avoid one. 400 is not
#: an invitation: the next reader asking for a fifth qualification should be answered by cutting
#: something, and if the abstract reaches 400 the question is which Result it has absorbed.
ABSTRACT_DRIFT_BOUND = 400


def _abstract():
    if not os.path.exists(PAPER):
        pytest.fail(f"the manuscript is missing: {PAPER}")
    text = open(PAPER, encoding="utf-8").read()
    assert "## Abstract" in text, "the abstract heading has moved; re-anchor this guard"
    body = text.split("## Abstract", 1)[1].split("\n---\n", 1)[0]
    return [w for w in re.sub(r"\*", "", body).split() if w.strip()]


def test_the_abstract_reads_this_paper_and_is_bounded():
    """⚠ The first assertion is the one that failed to exist before: that we opened THIS file."""
    words = _abstract()
    assert 150 < len(words), (
        f"the abstract is only {len(words)} words — either it has been gutted or this guard is "
        "reading the wrong file, which is the exact defect it was written for")
    assert len(words) <= ABSTRACT_DRIFT_BOUND, (
        f"the abstract is {len(words)} words against a drift bound of {ABSTRACT_DRIFT_BOUND}. This "
        "is not a venue limit — bioRxiv sets none — so the question is whether the abstract is "
        "absorbing the Results. Trim it, or raise the bound deliberately and say why here.")


def test_the_abstract_carries_the_qualifications_the_results_attach():
    """The front matter must not state the headline more flatly than the Results support.

    Each clause below was added because a reader found the abstract stating a result the body
    qualifies. They are asserted so a later trim for length cannot quietly drop the qualification
    and keep the number.
    """
    body = " ".join(_abstract())
    for needle, why in [
        ("adopted, not measured",
         "the ten-base-pair cut is a choice, and at seven base pairs the count is 175 of 190"),
        ("175 of 190",
         "the other end of the cited range is the reason 'nearly half' is the conservative reading"),
        ("partly by",
         "part of the gap-length quieting is guaranteed by a fixed mismatch budget, not measured"),
        ("survive every screen",
         "the designs that survive every screen sit at no reported patient breakpoint, so the named "
         "leads carry loads by necessity — an abstract naming only the leads misleads about that"),
    ]:
        assert needle in body, f"the abstract dropped {needle!r}: {why}"
