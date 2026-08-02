"""The inventory of where every lane's starting geometry comes from — and the guard that keeps it honest.

The selcal co-folds were measured at DockQ 0.023-0.046 / fnat 0.000 on the interface under test by two
independent instruments, and nobody knew, because no lane in this repo had ever scored its starting
structures against a reference. This census is the list of places the same defect could still be hiding.

The single most important property it must have is that **it cannot be written from memory**. A census of
provenance assembled from recollection is precisely the "plausible record" this program keeps getting caught
by (CLAUDE.md §4b), and it would be worse than no census at all because it would read as an audit. So every
row names a file and a quote, the quote is read back from that file at build time, and a row whose quote no
longer matches is emitted as EVIDENCE_STALE rather than as a fact.

That guard has already earned its place: on the first run it caught a row quoting the NR-V04 PREREG's wording
against the BENCHMARK json, which does not contain it.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import structural_provenance_census as C  # noqa: E402


def test_every_row_verifies_its_quote_against_the_real_file():
    """The census must not be assertable from memory. If this fails, a lane was refactored and the row
    describing it is stale — re-derive it from the source rather than editing the quote to match."""
    doc = C.build()
    stale = [r["lane"] for r in doc["lanes"] if not r["evidence_verified"]]
    assert not stale, ("EVIDENCE_STALE rows — the quoted source no longer says what the census claims: %s"
                       % stale)
    assert doc["n_evidence_stale"] == 0


def test_a_wrong_quote_is_reported_stale_rather_than_as_a_fact():
    """The guard itself, exercised — because a verifier nobody has seen fail is not a verifier."""
    ok, detail = C._verify({"evidence": ("selcal_stage.py", "this sentence is definitely not in the file")})
    assert ok is False
    assert "EVIDENCE_STALE" in detail


def test_a_missing_file_is_a_refusal_not_a_pass():
    ok, detail = C._verify({"evidence": ("no_such_module_xyz.py", "anything")})
    assert ok is False and "file absent" in detail


def test_reflowed_whitespace_does_not_read_as_a_deleted_quote():
    """The census must break on a lane that CHANGED, not on one that was re-wrapped."""
    ok, _ = C._verify({"evidence": ("selcal_stage.py",
                                    "the   deposited\n\n ternaries are used to VALIDATE the co-folds")})
    assert ok is True


def test_the_census_grades_nothing_and_gates_nothing():
    doc = C.build()
    assert "NOTHING" in doc["_licenses"]
    assert "re-scores no leg" in doc["_licenses"]
    assert "blocks no launch" in doc["_licenses"]
    for forbidden in ("verdict", "tier", "pass", "fail"):
        assert forbidden not in {k.lower() for k in doc}


def test_the_two_failed_controls_are_recorded_as_having_DIFFERENT_causes():
    """selcal's inputs are PREDICTED and were measured wrong; valB's are DEPOSITED, so its wrong sign is not
    the same defect. Collapsing the two would be the most tempting wrong conclusion available."""
    doc = C.build()
    by_lane = {r["lane"]: r for r in doc["lanes"]}
    selcal = next(r for k, r in by_lane.items() if k.startswith("selcal"))
    valb = next(r for k, r in by_lane.items() if k.startswith("valB / ternary"))
    assert selcal["source_class"].startswith("PREDICTED")
    assert valb["source_class"].startswith("DEPOSITED")
    assert "DIFFERENT causes" in valb["finding"]


def test_lanes_with_no_possible_reference_are_named_as_unfalsifiable_not_as_clean():
    """⚠ THE ROW THAT MATTERS MOST. NR-V04 and 5a-KS stage PREDICTED ternaries with no deposited reference at
    all, so 'unchecked' there can never become 'checked' by this method. That must read as a LIMIT, never as
    a clean bill of health — an absent reading is not a reading of absence (CLAUDE.md §4)."""
    doc = C.build()
    assert set(doc["unfalsifiable_by_this_method"]) == {"NR-V04 retrospective (Arm E)",
                                                        "5a-KS (CRBN ternary FEP)"}
    for lane in doc["lanes"]:
        if lane["lane"] in doc["unfalsifiable_by_this_method"]:
            assert lane["validated_by"] is None
            assert "YES" in lane["could_a_wrong_input_hide_here"]
    assert "can never become" in doc["_the_uncomfortable_row"]


def test_the_one_checkable_unchecked_case_is_surfaced():
    doc = C.build()
    assert any("SMARCA2 arm" in lane for lane in doc["checkable_but_unchecked"])


def test_a_scoreable_row_carries_its_confound_rather_than_promising_a_clean_number():
    """valB's SMARCA2 arm CAN be scored, but 8G1Q and 9DTY carry different ligands and resolutions, so the
    number bounds model fidelity rather than measuring it. Promising a clean measurement here would be the
    overclaim; the row has to say so before anyone runs it."""
    doc = C.build()
    row = next(r for r in doc["lanes"] if "SMARCA2 arm" in r["lane"])
    assert "confound_if_scored" in row
    assert "conflates" in row["confound_if_scored"]
    assert "6HAX is the better comparator" in row["confound_if_scored"]


def test_the_committed_artifact_matches_a_fresh_build():
    """The artifact is committed rather than regenerated in CI, so it must not drift from the module."""
    path = C.OUT_JSON
    if not os.path.exists(path):
        pytest.skip("artifact not built yet")
    on_disk = json.load(open(path))
    fresh = C.build()
    assert on_disk["lanes"] == fresh["lanes"], "the committed census is stale — re-run the module"
