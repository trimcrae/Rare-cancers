"""Behavioral corruption checks for the independent mature-parent verifier.

All scientific inputs remain the committed acquisition. Temporary copies are deliberately corrupted
to prove that changed row sets, attributions, classifications and aggregates produce DISAGREES.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aso_independent_verification as verifier  # noqa: E402


@pytest.fixture
def screen4(tmp_path, monkeypatch):
    original = json.loads(Path(verifier.SCREEN4).read_text(encoding="utf-8"))
    path = tmp_path / "screen4.json"
    monkeypatch.setattr(verifier, "SCREEN4", str(path))

    def run_with(record):
        path.write_text(json.dumps(record), encoding="utf-8")
        return verifier.run()

    return original, run_with


def test_clean_inputs_preserve_the_existing_verification_artifact(screen4):
    record, run_with = screen4
    expected = json.loads(Path(verifier.OUT).read_text(encoding="utf-8"))
    assert run_with(record) == expected


def _corrupt_screen4(record, change):
    row = record["per_design"][0]
    if change == "duplicate":
        record["per_design"].append(copy.deepcopy(row))
    elif change == "extra":
        extra = copy.deepcopy(row)
        extra["junction"] = "SYNTHETIC_EXTRA_NOT_IN_ATLAS"
        record["per_design"].append(extra)
    elif change == "design_count":
        record["corpus"]["n_designs"] += 1
    elif change == "parent_count":
        record["corpus"]["which_parent_supplies_it"]["NR4A3"] += 1
    elif change == "margin_count":
        record["corpus"]["by_gap_specificity_margin"]["2"]["n_with_parent_duplex"] += 1
    elif change == "liability_flag":
        row["counts_as_liability"] = not row["counts_as_liability"]
    elif change == "wrong_parent":
        # This real row has a unique maximal 11-bp run in NR4A3, not TCF12.
        row["parent"] = "TCF12"
    elif change == "wrong_start":
        row["parent_start_0based"] = 0
    elif change == "row_margin":
        row["gap_specificity_margin"] = 3
    elif change == "wing":
        record["method"]["wing"] = 4
    elif change == "gap_positions":
        record["method"]["gap_positions_0based"] = [4, 11]
    else:
        raise AssertionError(f"unknown test corruption {change}")


@pytest.mark.parametrize(("change", "problem"), [
    ("duplicate", "duplicate screen-4 design"),
    ("extra", "screen-4 designs are absent from the atlas"),
    ("design_count", "corpus n_designs disagrees"),
    ("parent_count", "corpus which_parent_supplies_it disagrees"),
    ("margin_count", "corpus by_gap_specificity_margin disagrees"),
    ("liability_flag", "liability flag disagrees"),
    ("wrong_parent", "invalid parent witness"),
    ("wrong_start", "invalid parent witness"),
    ("row_margin", "gap-specificity margin disagrees"),
    ("wing", "recorded geometry differs"),
    ("gap_positions", "recorded geometry differs"),
])
def test_corrupted_screen4_is_rejected(screen4, change, problem):
    record, run_with = screen4
    _corrupt_screen4(record, change)
    result = run_with(record)
    assert result["verdict"] == "DISAGREES"
    assert any(problem in item for item in result["problems"]), result["problems"]


@pytest.mark.parametrize(("field", "value"), [("length", 18), ("wing", 4), ("gap", 8)])
def test_corrupted_atlas_geometry_is_rejected(tmp_path, monkeypatch, field, value):
    atlas = json.loads(Path(verifier.ATLAS).read_text(encoding="utf-8"))
    atlas["oligo_geometry"][field] = value
    path = tmp_path / "atlas.json"
    path.write_text(json.dumps(atlas), encoding="utf-8")
    monkeypatch.setattr(verifier, "ATLAS", str(path))
    result = verifier.run()
    assert result["verdict"] == "DISAGREES"
    assert any("atlas geometry differs" in item for item in result["problems"])


def test_a_different_parent_can_be_a_valid_tie():
    # A synthetic perfect duplex occurs in both parents; the recorded parent need not be the
    # independent traversal's first winner. Its own coordinate must reproduce the run.
    target = "ACGTACGTACGTACGT"
    parents = {"first": target, "second": "TT" + target + "AA"}
    assert verifier.longest_run_by_substring(target, parents) == (16, "first")
    row = {"parent": "second", "parent_start_0based": 2}
    assert verifier._parent_witness_matches(target, 16, row, parents)
    row["parent_start_0based"] = 1
    assert not verifier._parent_witness_matches(target, 16, row, parents)


@pytest.mark.parametrize(("parent", "start"), [
    ("absent", 0), ("present", -1), ("present", 1), ("present", True),
])
def test_parent_witness_requires_a_real_parent_and_full_window(parent, start):
    target = "ACGTACGTACGTACGT"
    row = {"parent": parent, "parent_start_0based": start}
    assert not verifier._parent_witness_matches(target, 16, row, {"present": target})


def test_zero_run_has_no_parent_witness():
    assert verifier._parent_witness_matches("A" * 16, 0,
                                            {"parent": None, "parent_start_0based": None}, {})
    assert not verifier._parent_witness_matches("A" * 16, 0,
                                                {"parent": "invented", "parent_start_0based": 0}, {})


def test_liability_tie_summaries_use_the_validated_recorded_parent():
    # Two parents can supply a maximal liable run. The released aggregate follows the recorded
    # witness rather than an arbitrary independent traversal winner.
    row = {"junction": "synthetic", "antisense_5to3": "T" * 16,
           "gap_specificity_margin": 1, "longest_parent_duplex_bp_through_gap": 16,
           "parent": "second", "parent_start_0based": 0, "counts_as_liability": True}
    record = {"per_design": [row], "corpus": {
        "n_designs": 1, "n_with_parent_duplex_through_gap": 1,
        "by_gap_specificity_margin": {"1": {"n_designs": 1, "n_with_parent_duplex": 1}},
        "which_parent_supplies_it": {"second": 1},
    }}
    assert verifier._parent_witness_matches("A" * 16, 16, row,
                                            {"first": "A" * 16, "second": "A" * 16})
    problems = []
    verifier._check_screen4_summaries(record, problems)
    assert problems == []


@pytest.mark.parametrize(("verdict", "current", "expected_code"), [
    ("AGREES", True, 0),
    ("DISAGREES", True, 1),
    ("AGREES", False, 1),
    ("DISAGREES", False, 1),
])
def test_check_requires_both_artifact_freshness_and_agreement(
        tmp_path, monkeypatch, verdict, current, expected_code):
    result = {"verdict": verdict, "n_problems": int(verdict != "AGREES")}
    path = tmp_path / "verification.json"
    contents = json.dumps(result, indent=1, sort_keys=False) + "\n" if current else "{}\n"
    path.write_text(contents, encoding="utf-8")
    monkeypatch.setattr(verifier, "OUT", str(path))
    monkeypatch.setattr(verifier, "run", lambda: result)
    assert verifier.main(["--check"]) == expected_code
    assert path.read_text(encoding="utf-8") == contents
