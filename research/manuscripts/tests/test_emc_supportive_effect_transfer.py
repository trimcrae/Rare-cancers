"""Tests for the supportive-care effect-transfer arithmetic.

The gate under test is the one that would have caught the failure CLAUDE.md section 7
records: a PMID written from recollection, present in no committed source, passing
`lint_claims` twice because claim strength and citation provenance are orthogonal. Here
the check is mechanical -- the identifier either came back from a fetch or it did not --
so the tests are about it REFUSING, not about it permitting.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
MODULE = ROOT / "research/manuscripts/emc_supportive_effect_transfer.py"


def _load():
    spec = importlib.util.spec_from_file_location("emc_supportive_effect_transfer", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T = _load()


def _probe(pmids):
    return {"queries": {"q": {"hits": [{"pmid": p} for p in pmids]}},
            "oa_corpus": [], "terminal_events": []}


def _row(**kw):
    base = {"id": "IV-1", "intervention": "x", "mechanism": "m", "pmid": "12345678",
            "relative_effect_lo": 0.1, "relative_effect_hi": 0.3,
            "transferability": "distant"}
    base.update(kw)
    return base


# ---------------------------------------------------------------------------
# The anchor gate
# ---------------------------------------------------------------------------
def test_an_unanchored_pmid_is_refused():
    """The whole point. A PMID nobody fetched must stop the computation."""
    problems = T.check_anchors({"interventions": [_row(pmid="99999999")]},
                               _probe(["12345678"]))
    assert len(problems) == 1
    assert "does not appear anywhere in the retrieved probe artifact" in problems[0]
    assert "recollection" in problems[0]


def test_an_anchored_pmid_passes():
    assert T.check_anchors({"interventions": [_row(pmid="12345678")]},
                           _probe(["12345678"])) == []


def test_a_missing_or_malformed_pmid_is_refused_rather_than_skipped():
    for bad in (None, "", "n/a", "PMID12345678", "123"):
        problems = T.check_anchors({"interventions": [_row(pmid=bad)]}, _probe(["12345678"]))
        assert len(problems) == 1, f"{bad!r} slipped through"
        assert "cannot be anchored" in problems[0]


def test_an_unretrieved_row_claims_nothing_so_anchors_nothing():
    """Recording 'we did not find an effect size' must stay possible -- otherwise the
    honest state becomes the one the tooling forbids, and rows get invented to fill it."""
    row = _row(pmid=None, transferability="unretrieved")
    assert T.check_anchors({"interventions": [row]}, _probe([])) == []


def test_anchors_are_found_in_every_half_of_the_probe_artifact():
    probe = {"queries": {}, "oa_corpus": [{"pmid": "111111"}],
             "terminal_events": [{"pmid": "222222"}]}
    assert T.anchored_pmids(probe) == {"111111", "222222"}


# ---------------------------------------------------------------------------
# The arithmetic keeps its inputs visible
# ---------------------------------------------------------------------------
def test_the_band_reports_its_three_inputs_separately():
    """A single number formed from three uncertain factors hides all three."""
    b = T.band(0.40, 0.10, 0.30, "distant")
    assert b["attributable_fraction_of_deaths"] == 0.40
    assert b["relative_effect_range"] == [0.10, 0.30]
    assert b["transferability_multiplier_range"] == [0.20, 0.80]
    lo, hi = b["implied_share_of_deaths_averted_range"]
    assert lo == pytest.approx(0.40 * 0.10 * 0.20)
    assert hi == pytest.approx(0.40 * 0.30 * 0.80)


def test_a_speculative_transfer_can_reach_zero():
    """If no comparable population has been studied, 'no benefit' must remain inside the
    band. A floor above zero would assert the intervention works."""
    b = T.band(0.5, 0.2, 0.4, "speculative")
    assert b["implied_share_of_deaths_averted_range"][0] == 0.0


def test_an_unretrieved_transfer_is_pinned_to_zero_at_both_ends():
    b = T.band(0.5, 0.2, 0.4, "unretrieved")
    assert b["implied_share_of_deaths_averted_range"] == [0.0, 0.0]


def test_transferability_is_declared_not_computed():
    """Every level is a fixed, human-set range with a stated meaning. If one ever became a
    formula, a judgement would be wearing a measurement's clothes."""
    for level, (lo, hi, note) in T.TRANSFER.items():
        assert 0.0 <= lo <= hi <= 1.0, level
        assert len(note) > 20, level


def test_direct_transfer_is_the_only_level_that_does_not_shrink_an_effect():
    assert T.TRANSFER["direct"][0] == 1.0
    for level in ("close", "distant", "speculative", "unretrieved"):
        assert T.TRANSFER[level][0] < 1.0


# ---------------------------------------------------------------------------
# Refusing to run is a supported outcome, not a crash
# ---------------------------------------------------------------------------
def test_missing_inputs_exit_with_the_not_yet_code_rather_than_failing():
    """Before the retrieval has been read, 'nothing to compute' is the correct state and
    must be distinguishable from an error."""
    # ⛔ NOT A SKIP: both inputs are committed, so this branch is unreachable on a sound tree and a
    # skip would hide a broken one. Drive the "nothing to compute" path by pointing the module at
    # paths that do not exist, which is the state the exit code is FOR.
    # ⚠ UNDER ROOT, not /tmp: `main()` prints the path with `.relative_to(ROOT)`, so an absolute
    # temp path raises ValueError inside the branch this is trying to exercise.
    missing = T.ROOT / "research" / "manuscripts" / "a-path-that-does-not-exist.json"
    inputs, probe = T.INPUTS, T.PROBE
    T.INPUTS, T.PROBE = missing, missing
    try:
        assert T.main() == 2
    finally:
        T.INPUTS, T.PROBE = inputs, probe
