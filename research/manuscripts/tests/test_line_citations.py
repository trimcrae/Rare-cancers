"""⛔ A LINE-NUMBER CITATION IS A CLAIM, AND IT ROTS SILENTLY.

★ MEASURED 2026-08-06 by a verification read, not by CI. The roadmap cites the manuscript and the SI by
line number — `*"the quoted phrase"* (`:2200–2203`)` — and **every one of the 39 such citations was stale**,
by a systematic +16 to +35 lines into the paper and +15 to +35 into the SI. Not typos: the accumulated drift
of ordinary edits above each cited line.

⚠ NOTHING COULD HAVE CAUGHT IT BEFORE. A wrong line number is a well-formed reference — it points at a real
line, just not the one that says what the sentence claims it says. `check_links` validates that a FILE and
an ANCHOR exist; neither concept reaches inside a file to a line. So the failure mode is a citation that
looks checked, reads as precise, and vouches for a sentence it does not contain.

⭐ THE FIX IS THAT THE QUOTE MAKES IT DERIVABLE. Each citation follows the phrase it cites, so the true line
can be found by searching the target — which is what `line_citations.py` does, and what makes this a class
that can be closed rather than 39 separate corrections.

This test asserts only that no citation whose quote CAN be located points at the wrong line. It deliberately
does not require every citation to be resolvable: a paraphrase, or a sentence the paper has since rewritten,
is reported as UNRESOLVED and left alone, because repointing a citation at the nearest match is how one
comes to vouch for something it does not say.
"""
from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, MANUSCRIPTS)

import line_citations as lc  # noqa: E402


@pytest.fixture(scope="module")
def scanned():
    _, cites = lc.scan()
    return cites


def test_no_resolvable_line_citation_points_at_the_wrong_line(scanned):
    drifted = [c for c in scanned if c["true"] and c["true"] != c["cited"]]
    assert not drifted, (
        f"{len(drifted)} line citation(s) in the roadmap point at a line that does not contain the phrase "
        f"they quote:\n  "
        + "\n  ".join(f"{c['target']} `:{c['cited']}` should be :{c['true']} — {c['quote'][:70]!r}"
                      for c in drifted)
        + "\n⛔ Do NOT hand-edit these. Run `python3 research/manuscripts/line_citations.py --fix`, which "
          "derives each from the quote it sits beside."
    )


def test_the_checker_still_resolves_a_useful_share_of_them(scanned):
    """⭐ THE GUARD ON THE GUARD.

    The test above passes trivially if the checker resolves NOTHING — a normalisation change, a regex slip,
    or a rename of the target files would make every citation UNRESOLVED and the suite would go green while
    checking zero citations. That is the same "absent reading is not a reading of absence" failure the rest
    of this repository keeps paying for, in test form.

    The bound is deliberately loose: it asserts the checker is alive and discriminating, not a fixed count.
    """
    assert scanned, "no quoted line citations found at all — the scanner or the roadmap's format changed"
    resolved = [c for c in scanned if c["true"]]
    assert len(resolved) >= 10, (
        f"only {len(resolved)} of {len(scanned)} citations resolved to a line. The checker is not doing its "
        f"job — check `_norm`, `QUOTE` and the paper/SI paths before trusting a green run above."
    )
