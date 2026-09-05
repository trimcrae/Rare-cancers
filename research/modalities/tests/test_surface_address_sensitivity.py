"""Behavioral edge cases and an independent Decimal audit of every result row."""
from collections import Counter
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path

import pytest

import surface_address_sensitivity as sensitivity


def synthetic(emc, classes, parent_delta=None):
    """Explicitly synthetic values used only inside behavioral tests."""
    rows = [{"gsm": f"E{i}", "class": "EMC", "z_vs_array": z} for i, z in enumerate(emc)]
    rows += [{"gsm": f"{c}{i}", "class": c, "z_vs_array": z}
             for c, values in classes.items() for i, z in enumerate(values)]
    return {"readable": True, "per_sample": rows,
            "welch_EMC_vs_comparator": {"delta_a_minus_b": parent_delta}}, {
                r["gsm"]: r["class"] for r in rows}


def test_histology_deletion_removes_whole_class_and_uses_sample_weights():
    record, roster = synthetic([2, 2], {"A": [0, 0, 0], "B": [4]})
    result = sensitivity.analyze_address(record, roster)
    assert result["baseline"]["delta"] == 1  # not class-weighted delta = 0
    rows = {r["deleted_id"]: r for r in result["leave_one_comparator_histology_out"]["rows"]}
    assert rows["A"]["delta"] == -2
    assert rows["A"]["deleted_gsms"] == ["A0", "A1", "A2"]
    assert rows["A"]["counts"]["comparator"]["available_n"] == 1
    assert rows["B"]["delta"] == 2
    assert result["status"] == "unstable"
    assert result["leave_one_comparator_histology_out"]["summary"]["sign_flip_ids"] == ["A"]


def test_emc_outlier_deletion_flips_sign():
    record, roster = synthetic([0, 4], {"A": [1], "B": [1]})
    result = sensitivity.analyze_address(record, roster)
    summary = result["leave_one_EMC_out"]["summary"]
    assert summary["min_delta"] == -1
    assert summary["max_delta"] == 3
    assert summary["sign_flip_ids"] == ["E1"]
    assert result["status"] == "unstable"


def test_reaching_exact_zero_is_a_change_but_not_an_opposite_sign_flip():
    record, roster = synthetic([0.1, 0.3], {"A": [0.1], "B": [0.1]})
    result = sensitivity.analyze_address(record, roster)
    summary = result["leave_one_EMC_out"]["summary"]
    assert summary["sign_flip_ids"] == []
    assert summary["sign_change_ids"] == ["E1"]
    assert summary["zero_delta_ids"] == ["E1"]
    assert result["status"] == "unstable"


def test_zero_baseline_has_no_direction_to_survive():
    record, roster = synthetic([0.1, 0.1], {"A": [0.1], "B": [0.1]})
    result = sensitivity.analyze_address(record, roster)
    assert result["status"] == "zero_baseline"
    assert result["leave_one_EMC_out"]["summary"]["strict_direction_survives_all"] is False


def test_stable_negative_is_preserved():
    record, roster = synthetic([-3, -2], {"A": [1, 2], "B": [4]})
    result = sensitivity.analyze_address(record, roster)
    assert result["status"] == "stable_negative"
    assert result["leave_one_comparator_histology_out"]["summary"]["strict_direction_survives_all"]


def test_null_and_absent_rows_are_not_zero_imputed_and_missing_deletion_is_a_noop():
    record, roster = synthetic([None, 2, 4], {"A": [None, 0], "B": [1]})
    roster["B_missing"] = "B"
    result = sensitivity.analyze_address(record, roster)
    assert result["baseline"]["delta"] == 2.5
    counts = result["baseline"]["counts"]
    assert counts["EMC"] == {"recorded_n": 3, "available_n": 2, "missing_n": 1}
    assert counts["comparator"] == {"recorded_n": 4, "available_n": 2, "missing_n": 2}
    missing = {r["gsm"]: r["missing_reason"] for r in result["source_samples"]}
    assert missing["A0"] == "missing_z_vs_array"
    assert missing["B_missing"] == "absent_per_sample_row"
    deletion = result["leave_one_EMC_out"]["rows"][0]
    assert deletion["deleted_id"] == "E0"
    assert deletion["deleted_available_n"] == 0
    assert deletion["delta"] == 2.5


def test_empty_arms_are_ineligible_and_never_vacuously_stable():
    record, roster = synthetic([3], {"A": [1, None]})
    result = sensitivity.analyze_address(record, roster)
    assert result["baseline"]["delta"] == 2
    assert result["status"] == "incomplete_deletions"
    for mode in ("leave_one_EMC_out", "leave_one_comparator_histology_out"):
        assert result[mode]["summary"]["strict_direction_survives_all"] is None
        assert result[mode]["summary"]["min_delta"] is None
        assert result[mode]["rows"][0]["ineligible_reason"] == "empty_available_arm_after_deletion"


def test_a_class_with_only_missing_values_is_still_deleted_and_reported():
    record, roster = synthetic([2, 3], {"A": [None], "B": [0]})
    result = sensitivity.analyze_address(record, roster)
    rows = result["leave_one_comparator_histology_out"]["rows"]
    assert rows[0]["deleted_id"] == "A"
    assert rows[0]["eligible"] and rows[0]["delta"] == 2.5
    assert rows[0]["deleted_available_n"] == 0
    assert not rows[1]["eligible"]
    assert result["status"] == "incomplete_deletions"


@pytest.mark.parametrize("record", [None, {"readable": False, "why_not_readable": "no mapped probe"}])
def test_unreadable_retains_all_deletion_rows_without_expression_inference(record):
    result = sensitivity.analyze_address(record, {"E0": "EMC", "E1": "EMC", "A0": "A", "B0": "B"})
    assert result["status"] == "unreadable"
    assert result["baseline"]["delta"] is None
    assert result["baseline"]["counts"]["EMC"]["missing_n"] == 2
    for mode in ("leave_one_EMC_out", "leave_one_comparator_histology_out"):
        assert len(result[mode]["rows"]) == 2
        assert all(not r["eligible"] and r["delta"] is None for r in result[mode]["rows"])


def test_all_missing_available_arm_is_unestimable():
    record, roster = synthetic([None, None], {"A": [1], "B": [2]})
    result = sensitivity.analyze_address(record, roster)
    assert result["readable"]
    assert result["status"] == "unestimable_baseline"
    assert result["parent_baseline_comparison"]["status"] == "not_comparable"


def test_parent_precision_preserves_disagreement_and_omitted_trailing_zeros():
    record, roster = synthetic([0.1, 0.1], {"A": [0], "B": [0]}, parent_delta=0.1001)
    result = sensitivity.analyze_address(record, roster)
    assert result["baseline"]["delta"] == 0.1
    assert result["parent_baseline_comparison"]["status"] == "disagreement"
    record["welch_EMC_vs_comparator"]["delta_a_minus_b"] = 0.1
    result = sensitivity.analyze_address(record, roster)
    assert result["parent_baseline_comparison"]["decimal_places"] == 4
    assert result["parent_baseline_comparison"]["status"] == "match"


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), "1.2", True])
def test_invalid_values_fail_with_input_problem(bad):
    record, roster = synthetic([bad, 1], {"A": [0], "B": [0]})
    with pytest.raises(sensitivity.InputError, match="finite number or null"):
        sensitivity.analyze_address(record, roster)


def test_duplicate_sample_ids_fail_instead_of_double_counting():
    record, roster = synthetic([1, 2], {"A": [0], "B": [0]})
    record["per_sample"].append(record["per_sample"][0])
    with pytest.raises(sensitivity.InputError, match="duplicate per_sample gsm"):
        sensitivity.analyze_address(record, roster)


def test_uncommitted_input_is_rejected(tmp_path, monkeypatch):
    path = tmp_path / sensitivity.PARENT
    path.parent.mkdir(parents=True)
    path.write_bytes(b"changed input")
    monkeypatch.setattr(sensitivity.subprocess, "check_output",
                        lambda args, **kw: "synthetic-revision\n" if args[1] == "rev-parse" else b"committed input")
    with pytest.raises(sensitivity.InputError, match="working input differs from committed input"):
        sensitivity.committed_inputs(tmp_path)


ROOT = Path(__file__).resolve().parents[3]
PARENT = json.loads((ROOT / sensitivity.PARENT).read_bytes())
RESULT = json.loads((ROOT / sensitivity.OUTPUT).read_bytes())
MEMBERS = PARENT["panels"]["surface_antigen"]["groups"]["route_named_addresses"]["genes_requested"]


def decimal_audit(rows, output):
    """Independent arithmetic: Decimal sums, direct filtering, no generator helpers."""
    def arm(items):
        available = [Decimal(str(r["z_vs_array"])) for r in items if r.get("z_vs_array") is not None]
        return available, {"recorded_n": len(items), "available_n": len(available),
                           "missing_n": len(items) - len(available)}
    a, ac = arm([r for r in rows if r["class"] == "EMC"])
    b, bc = arm([r for r in rows if r["class"] != "EMC"])
    classes = {c: arm([r for r in rows if r["class"] == c])[1]
               for c in {r["class"] for r in rows} - {"EMC"}}
    assert output["counts"] == {"EMC": ac, "comparator": bc, "comparator_classes": classes}
    with localcontext() as ctx:
        ctx.prec = 50
        ma = sum(a) / Decimal(len(a)) if a else None
        mb = sum(b) / Decimal(len(b)) if b else None
        delta = ma - mb if a and b else None
    for key, expected in (("mean_EMC", ma), ("mean_comparator", mb), ("delta", delta)):
        if expected is None:
            assert output[key] is None
        else:
            assert output[key] == pytest.approx(float(expected), rel=0, abs=1e-14)
    expected_sign = None if delta is None else (delta > 0) - (delta < 0)
    assert output["sign"] == expected_sign
    return delta, expected_sign


@pytest.mark.committed_artifact
@pytest.mark.parametrize("matrix,gene", [(m, g) for m in PARENT["platforms"] for g in MEMBERS])
def test_independent_arithmetic_for_every_address_platform_and_deletion(matrix, gene):
    original = PARENT["gene_reads"][gene][matrix]
    row = RESULT["platforms"][matrix]["addresses"][gene]
    roster = {s["gsm"]: s["class"] for g in MEMBERS
              for s in PARENT["gene_reads"][g][matrix].get("per_sample", [])}
    source = {s["gsm"]: s for s in original.get("per_sample", [])}
    samples = [{"gsm": gsm, "class": cls, "z_vs_array": source.get(gsm, {}).get("z_vs_array")}
               for gsm, cls in sorted(roster.items())]
    assert [{k: s[k] for k in ("gsm", "class", "z_vs_array")} for s in row["source_samples"]] == samples
    for sample in row["source_samples"]:
        expected_reason = ("platform_address_unreadable" if not original["readable"] else
                           "absent_per_sample_row" if sample["gsm"] not in source else
                           "missing_z_vs_array" if sample["z_vs_array"] is None else None)
        assert sample["missing_reason"] == expected_reason
    baseline, baseline_sign = decimal_audit(samples, row["baseline"])
    comparison = row["parent_baseline_comparison"]
    parent_delta = (original.get("welch_EMC_vs_comparator") or {}).get("delta_a_minus_b")
    assert comparison["parent_delta"] == parent_delta
    if baseline is not None:
        rounded = float(baseline.quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN))
        assert comparison["recomputed_at_parent_precision"] == rounded
        assert comparison["status"] == ("match" if rounded == parent_delta else "disagreement")
    else:
        assert comparison["status"] == "not_comparable"
    family_states = []
    any_changed = False
    for mode, key, ids in (
        ("leave_one_EMC_out", "gsm", sorted(gsm for gsm, cls in roster.items() if cls == "EMC")),
        ("leave_one_comparator_histology_out", "class", sorted(set(roster.values()) - {"EMC"})),
    ):
        deletions = row[mode]["rows"]
        assert [d["deleted_id"] for d in deletions] == ids
        values, flips, changes, zeros = [], [], [], []
        for deletion in deletions:
            item = deletion["deleted_id"]
            removed = [s for s in samples if s[key] == item]
            retained = [s for s in samples if s[key] != item]
            delta, delta_sign = decimal_audit(retained, deletion)
            assert deletion["deleted_gsms"] == [s["gsm"] for s in removed]
            assert deletion["deleted_available_n"] == sum(s["z_vs_array"] is not None for s in removed)
            assert deletion["eligible"] == (original["readable"] and delta is not None)
            if deletion["eligible"]:
                values.append(float(delta))
                flip = delta_sign * baseline_sign == -1
                change = delta_sign != baseline_sign
                assert deletion["sign_flip"] == flip
                assert deletion["sign_change"] == change
                if flip:
                    flips.append(item)
                if change:
                    changes.append(item)
                if delta_sign == 0:
                    zeros.append(item)
                assert deletion["ineligible_reason"] is None
            else:
                assert deletion["sign_flip"] is None and deletion["sign_change"] is None
                assert deletion["ineligible_reason"] == ("unreadable_address" if not original["readable"]
                                                           else "empty_available_arm_after_deletion")
        summary = row[mode]["summary"]
        assert summary["n_deletions"] == len(ids)
        assert summary["n_eligible"] == len(values)
        assert summary["n_ineligible"] == len(ids) - len(values)
        assert summary["min_delta"] == (min(values) if values else None)
        assert summary["max_delta"] == (max(values) if values else None)
        assert summary["sign_flip_ids"] == flips
        assert summary["sign_change_ids"] == changes
        assert summary["zero_delta_ids"] == zeros
        stable = (baseline_sign in (-1, 1) and not changes) if len(values) == len(ids) else None
        assert summary["strict_direction_survives_all"] == stable
        family_states.append(stable)
        any_changed |= bool(changes)
    expected_state = ("unreadable" if not original["readable"] else "unstable" if any_changed else
                      "stable_positive" if baseline_sign == 1 else "stable_negative")
    assert row["status"] == expected_state


@pytest.mark.committed_artifact
def test_result_covers_membership_platforms_and_preserves_input_hashes():
    assert RESULT["addresses"] == MEMBERS
    assert set(RESULT["platforms"]) == set(PARENT["platforms"])
    for platform in RESULT["platforms"].values():
        assert list(platform["addresses"]) == MEMBERS
    provenance = RESULT["provenance"]
    assert provenance["parent_source_path"] == sensitivity.PARENT
    assert provenance["parent_sha256"] == hashlib.sha256((ROOT / sensitivity.PARENT).read_bytes()).hexdigest()
    assert [r["path"] for r in provenance["inputs"]] == list(sensitivity.INPUTS)
    for source in provenance["inputs"]:
        assert source["sha256"] == hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest()
