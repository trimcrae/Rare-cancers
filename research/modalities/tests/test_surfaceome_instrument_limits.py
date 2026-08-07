"""The EMC surfaceome instrument's blind spots, asserted rather than described.

★★ WHY THESE ARE TESTS AND NOT A PARAGRAPH. `emc-unexplored-treatment-lanes.md` §0 records two
limits of `emc_surfaceome_scan.py` in prose: it cannot rank a glycan, and `CSPG4` is absent from its
seed. Prose cannot fail a build. The moment somebody adds `CSPG4` to `SEED_SURFACE` and re-runs the
scan — which is the correct fix and is one line — every document repeating the prose becomes wrong
and nothing notices. These tests make the transition LOUD in both directions: while the gap exists
they hold it fixed, and the day it is closed they fail and name the documents to update.

⚠ Marked `committed_artifact`: they assert the content of mutable committed files, not the behaviour
of code, so per conftest they are loud and never a gate on GPU work.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

LIMITS = os.path.join(HERE, "surfaceome-instrument-limits.json")
SCAN = os.path.join(HERE, "emc-surfaceome-scan.json")

pytestmark = pytest.mark.committed_artifact


def _limits():
    with open(LIMITS, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _scan():
    with open(SCAN, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_cspg4_is_absent_from_the_seed_and_the_seed_size_matches_the_artifact():
    """The coverage gap itself — and the size check is what proves the seed being read is the one
    that produced the artifact, rather than a seed edited since."""
    import emc_surfaceome_scan as scan_module

    assert "CSPG4" not in scan_module.SEED_SURFACE, (
        "CSPG4 is now in SEED_SURFACE. That is the RIGHT change — but the coverage gap it closes is "
        "asserted in emc-unexplored-treatment-lanes.md §0/§3.6, in the RT-FAP-RLT / surface-antigen "
        "prose, and in surfaceome-instrument-limits.json. Re-run emc_surfaceome_scan.py, re-run "
        "surfaceome_instrument_limits.py, and update those documents in the same commit."
    )
    assert len(scan_module.SEED_SURFACE) == _scan()["surfaceome_source"]["n_seed_unioned"], (
        "SEED_SURFACE has changed size since emc-surfaceome-scan.json was produced, so the artifact "
        "no longer reflects the seed. Re-run the scan."
    )


def test_cspg4_has_no_per_gene_number_in_any_committed_output():
    lim = _limits()["limits"]["L4_cspg4_coverage_gap"]
    assert lim["in_seed_surface"] is False
    assert not any(lim["reported_in"].values()), (
        "CSPG4 now carries a per-gene row in the scan artifact. Its absence is cited as a COVERAGE "
        "GAP; once a number exists the honest word is a RESULT, and every consumer must be re-read."
    )
    assert lim["in_emc_surface_normal_window"] is False


def test_the_scanned_gene_list_is_not_recorded_so_absence_stays_undecidable():
    """⛔ THE CLAIM THAT MUST NOT BE OVERSTATED.

    'CSPG4 is in no output' is measured. 'CSPG4 was never scanned' is NOT, because the artifact
    records the scanned set's SIZE and not its MEMBERS. This test pins the weaker, true claim so a
    later reader cannot quietly promote it, and fails the moment the scan starts recording the list
    — at which point the question becomes answerable and the wording should change.
    """
    scan = _scan()
    assert "scanned_genes" not in scan and "surfaceome_genes" not in scan
    lim = _limits()["limits"]["L4_cspg4_coverage_gap"]
    assert lim["was_it_scanned"] == "UNDECIDABLE"


def test_no_sulfation_machinery_gene_is_rankable_by_this_instrument():
    """The glycan limit, in the only form that can be measured: the enzymes that WRITE the epitope
    are excluded by the plasma-membrane filter, so no sulfation-code argument can come from here."""
    lim = _limits()["limits"]["L3_glycan_unrankable"]
    assert lim["sulfation_machinery_reported_anywhere"] == []
    assert lim["sulfation_machinery_in_seed"] == []
    # A backbone being present must never be read as the epitope being covered.
    assert "CD44" in lim["backbones_reported_anywhere"]
    assert "CSPG4" not in lim["backbones_reported_anywhere"]


def test_a_caf_only_antigen_reads_at_the_floor_while_a_shared_one_does_not():
    """⚠ THE LIMIT IS NARROWER THAN 'CANNOT SEE STROMA', AND THE NARROW VERSION IS THE TRUE ONE.

    LRRC15 and FAP are carried by the stromal compartment; CD248 and PDGFRB are transcribed by
    mesenchymal tumour cells too and come back SIGNIFICANT. If this test ever fails because CD248
    went non-significant, the fix is to re-read the scan, not to widen the claim.
    """
    lim = _limits()["limits"]["L2_stromal_floor_demonstrated"]
    assert lim["genes"]["LRRC15"]["class_frac_expressed"] == 0.0
    assert lim["genes"]["FAP"]["selectivity_significant"] is False
    counter = lim["counter_reading_that_narrows_the_limit"]["genes"]
    assert counter["CD248"]["selectivity_significant"] is True
    assert counter["PDGFRB"]["selectivity_significant"] is True


def test_the_scan_holds_no_emc_observation_of_fap():
    """RT-FAP-RLT's readiness gap survives, and for a second independent reason: the one 'myxoid'
    line is ACH-001519, whose EMC identity this repository retracted."""
    lim = _limits()["limits"]["L5_no_emc_fap_observation"]
    assert lim["n_myxoid_lines"] == 1
    assert any("ACH-001519" in name for name in lim["myxoid_lines_named"])
    note = (_scan()["emc_line_top_surface"] or {}).get("note", "")
    assert "NOT AN EMC READING" in note, (
        "the retraction note on the single myxoid-labelled DepMap line has changed. RT-FAP-RLT's "
        "'no measurement in EMC' rests on it."
    )
