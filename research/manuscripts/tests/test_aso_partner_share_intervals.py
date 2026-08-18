"""Every partner-share Wilson interval the manuscript prints must recompute from its own counts.

⛔ WHY. §4.1 prints the two partner-share Wilson intervals that the coverage figure does NOT
propagate, so a reader can see how much uncertainty is being held fixed. They are prose figures: no
artifact publishes them, because nothing downstream consumes them. That makes them the one class of
number in this paper with no generator behind it — and on 2026-08-17 a blind screen of the built PDF
found the *EWSR1* upper bound printed as 87.8% where 46/58 gives 87.7485%, which rounds to 87.7. The
*TAF15* interval beside it, 8.3845–26.9340% for 9/58, matched its printed 8.4–26.9% exactly, so the
method was right and one digit was wrong.

★ A NUMBER WITH NO GENERATOR NEEDS A TEST, or it has nothing holding it at all. This recomputes both
intervals from the cohort counts the paper itself states and asserts the printed strings, so the
same defect cannot return silently and a future edit to the counts fails here rather than in review.
"""
from __future__ import annotations

import math
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ARTICLE = os.path.join(os.path.abspath(os.path.join(HERE, "..")), "aso",
                       "fusion-junction-aso-research-article.md")

#: The 58-case molecularly confirmed cohort behind every coverage figure (PMID 36948401), and the
#: two partner counts §4.1 states. Kept here as the counts, never as the intervals: the point of the
#: test is that the intervals are DERIVED, so typing them on both sides would check nothing.
_COHORT_N = 58
_PARTNER_COUNTS = {"EWSR1": 46, "TAF15": 9}

#: 95%, two-sided.
_Z = 1.959963984540054


def _wilson(k, n, z=_Z):
    p = k / n
    denominator = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - half) / denominator * 100, (centre + half) / denominator * 100)


def _article():
    if not os.path.exists(ARTICLE):
        pytest.fail(f"the manuscript is missing: {ARTICLE}")
    return open(ARTICLE, encoding="utf-8").read()


TEXT = _article()

#: `67.2–87.7% for *EWSR1* and 8.4–26.9% for *TAF15*` — an en dash, as the manuscript sets it.
_INTERVAL = re.compile(r"(\d+\.\d)\s*[–-]\s*(\d+\.\d)\s*%\s*for\s*\*([A-Z0-9]+)\*")


def test_the_manuscript_still_prints_both_partner_share_intervals():
    found = {m.group(3) for m in _INTERVAL.finditer(TEXT)}
    assert set(_PARTNER_COUNTS) <= found, (
        f"§4.1 no longer prints an interval for {sorted(set(_PARTNER_COUNTS) - found)}; this test "
        "would then be asserting about nothing. If the sentence was deliberately removed, remove "
        "this test with it.")


@pytest.mark.parametrize("partner", sorted(_PARTNER_COUNTS))
def test_each_printed_interval_is_the_wilson_interval_for_its_own_counts(partner):
    printed = {m.group(3): (m.group(1), m.group(2)) for m in _INTERVAL.finditer(TEXT)}
    assert partner in printed, f"no interval printed for {partner}"
    lo, hi = _wilson(_PARTNER_COUNTS[partner], _COHORT_N)
    want = (f"{lo:.1f}", f"{hi:.1f}")
    assert printed[partner] == want, (
        f"{partner}: the manuscript prints {printed[partner][0]}–{printed[partner][1]}%, but the "
        f"Wilson 95% interval for {_PARTNER_COUNTS[partner]}/{_COHORT_N} is {lo:.4f}–{hi:.4f}%, "
        f"which rounds to {want[0]}–{want[1]}%")


def test_the_retired_upper_bound_does_not_reappear():
    """The specific misrounding, held by name as well as by recomputation."""
    assert not re.search(r"67\.2\s*[–-]\s*87\.8\s*%", TEXT), (
        "87.8% is back as the EWSR1 upper bound; 46/58 gives 87.7485%, which rounds to 87.7")
