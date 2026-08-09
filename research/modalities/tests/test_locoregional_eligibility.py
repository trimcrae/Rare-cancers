#!/usr/bin/env python3
"""The pooling rules the locoregional eligibility arithmetic rests on, exercised rather than asserted.

⭐ WHY THIS FILE IS SHORT AND SPECIFIC. Two of these rules are ones a reader would assume hold because
the code says so, and both would fail SILENTLY: a double-counting guard that never fires on today's
data returns the right answer for the wrong reason, and a Wilson interval that quietly degraded to a
normal approximation would still print a plausible-looking range. POLICY-evidence §2 is binding, so its
two load-bearing arithmetic claims are checked against values with known closed forms.
"""
from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import emc_locoregional_eligibility as loco  # noqa: E402


def _cohort(label, **kw):
    base = {"label": label, "pool": True, "sourceId": "s1"}
    base.update(kw)
    return base


def test_a_cohort_whose_inclusion_criterion_is_the_outcome_is_dropped_even_when_it_has_counts():
    """⛔ THE RULE THIS EXISTS FOR (POLICY-evidence §2.1.3), AND IT IS A NO-OP ON THE REAL REGISTRY.

    The metastatic-at-diagnosis cohort carries no metastasis counts today, so on live data the
    missing-field branch would exclude it whatever this rule did. That makes the guard untestable
    against the registry and exactly the shape of thing that rots unnoticed — so the counts are
    curated on here. A 100%-by-construction rate pooled into a metastasis estimate is the specific
    harm; without this test, adding that field to the registry later would silently inflate the pool.
    """
    cohorts = [
        _cohort("localised", criteria={"stage": "localized"}, metastasis={"events": 10, "denom": 100}),
        _cohort("metastatic at dx", criteria={"stage": "distant"},
                metastasis={"events": 29, "denom": 29}),
    ]
    r = loco.pool(cohorts, "metastasis")
    assert r["denom"] == 100, "the metastatic-at-diagnosis cohort was pooled into the metastasis rate"
    assert r["events"] == 10
    assert "metastatic at dx" in r["cohorts_excluded"]
    assert "§2.1.3" in r["cohorts_excluded"]["metastatic at dx"], (
        "excluded for the wrong reason — the structural rule must be what fires, not the "
        "missing-field branch, or the guard is untested wherever the field happens to be absent")


def test_the_same_cohort_is_not_dropped_from_an_outcome_that_is_not_its_inclusion_criterion():
    """The guard must be narrow. A metastatic-at-diagnosis cohort's DEATH rate is a real outcome."""
    cohorts = [_cohort("metastatic at dx", criteria={"stage": "distant"},
                       diseaseDeath={"events": 9, "denom": 29})]
    r = loco.pool(cohorts, "diseaseDeath")
    assert r["denom"] == 29 and r["events"] == 9


def test_pool_false_cohorts_never_enter_the_headline():
    cohorts = [
        _cohort("pooled", metastasis={"events": 5, "denom": 50}),
        _cohort("context", pool=False, contextReason="population-overlap",
                metastasis={"events": 40, "denom": 50}),
    ]
    r = loco.pool(cohorts, "metastasis")
    assert (r["events"], r["denom"]) == (5, 50)


def test_a_percentage_only_cohort_cannot_contribute_counts():
    """POLICY-evidence §2.1.2 — deriving counts from a published percentage invents data."""
    cohorts = [_cohort("pct only", metastasisPct=31.0)]
    r = loco.pool(cohorts, "metastasis")
    assert r["denom"] == 0


@pytest.mark.parametrize("ev,dn,lo,hi", [
    # Closed-form Wilson values, derived from the algebra rather than recalled.
    # ⚠ THE FIRST DRAFT OF THIS TABLE HELD 0.3085 AND 0.6915, WHICH ARE THE CLOPPER-PEARSON EXACT
    # BOUNDS FOR THE SAME COUNTS (0.05**(1/10) and its complement), NOT the Wilson ones. The test went
    # red and the implementation was right. Kept as a comment because the two intervals are routinely
    # quoted interchangeably and are not: at 10/10 they differ by three percentage points, and
    # POLICY-evidence §2.2 names Wilson specifically.
    (0, 10, 0.0, 0.2775),
    (10, 10, 0.7225, 1.0),
    (1, 2, 0.0945, 0.9055),
])
def test_wilson_matches_known_values_including_the_boundaries(ev, dn, lo, hi):
    """⚠ THE BOUNDARY CASES ARE THE POINT. §2.2 chose Wilson precisely because it behaves at 0% and
    100%, where a normal approximation returns an interval of zero width and reads as certainty."""
    _, got_lo, got_hi = loco.wilson(ev, dn)
    assert got_lo == pytest.approx(lo, abs=1e-4)
    assert got_hi == pytest.approx(hi, abs=1e-4)


def test_wilson_on_an_empty_denominator_returns_nothing_rather_than_dividing():
    assert loco.wilson(0, 0) == (None, None, None)


def test_every_quantity_the_endpoint_names_is_classified_and_the_negatives_say_what_would_supply_them():
    """⛔ THE GAP IS THE DELIVERABLE. A quantity recorded as uncomputable without naming what would
    supply it is a dead end wearing the costume of a finding."""
    for key, q in loco.QUANTITIES.items():
        assert q["computable"] in (True, False, "partially"), key
        assert q["wanted_by"] and q["why"], key
        if q["computable"] is not True:
            assert q["what_would_supply_it"], f"{key} is negative and names no way out"
