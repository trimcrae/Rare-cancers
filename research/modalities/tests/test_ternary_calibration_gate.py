"""Reviewer condition 6 (2026-07-19) — the three-tier FIXED-margin calibration gate (PASS/BORDERLINE/FAIL) on
the BETWEEN-REPLICATE cycle SD (condition 3), not the MBAR SE. Pure; no GPU."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_fep_reduce as red  # noqa: E402

TARGET = 0.944


def test_pass_tight_replicates_on_target():
    # three replicates near +0.944, tiny spread, diagnostics clean -> PASS
    g = red.calibration_gate([0.90, 0.95, 1.00], TARGET, diagnostics_ok=True)
    assert g["decision"] == "PASS", g
    assert g["correct_sign"] is True
    assert g["abs_error_kcal"] <= red.GATE_ABS_ERR_PASS
    assert g["cycle_sd_kcal"] <= red.GATE_CYCLE_SD_PASS
    assert "NR-V04" in g["authorizes"]


def test_fail_wrong_sign():
    g = red.calibration_gate([-0.8, -0.9, -1.0], TARGET, diagnostics_ok=True)
    assert g["decision"] == "FAIL"
    assert g["correct_sign"] is False
    assert "wrong sign" in g["reason"]


def test_fail_large_error():
    # correct sign but |mean − target| > 2.0  (mean ~3.5, err ~2.6)
    g = red.calibration_gate([3.4, 3.5, 3.6], TARGET, diagnostics_ok=True)
    assert g["decision"] == "FAIL"
    assert g["abs_error_kcal"] > red.GATE_ABS_ERR_FAIL


def test_fail_persistent_diagnostics():
    g = red.calibration_gate([0.9, 0.95, 1.0], TARGET, diagnostics_ok=False)
    assert g["decision"] == "FAIL"
    assert "diagnostics" in g["reason"]


def test_borderline_moderate_error_extends():
    # abs error in (1.0, 2.0] -> BORDERLINE / extend (mean ~2.4, err ~1.5); keep SD small so error is the trigger
    g = red.calibration_gate([2.40, 2.42, 2.44], TARGET, diagnostics_ok=True)
    assert g["decision"] == "BORDERLINE"
    assert g["adaptive_action"] == "extend_to_5_replicates"


def test_borderline_high_cycle_sd_extends():
    # on-target mean but cycle SD in (0.75, 1.0] -> BORDERLINE
    g = red.calibration_gate([0.0, 0.9, 1.9], TARGET, diagnostics_ok=True)
    assert 0.75 < g["cycle_sd_kcal"] <= 1.0
    assert g["decision"] == "BORDERLINE"


def test_fail_high_sd_after_extension():
    # SD > 1.0 and already extended (>=5) -> FAIL, not another extend
    g = red.calibration_gate([-0.5, 0.4, 1.3, 2.2, 0.9], TARGET, diagnostics_ok=True, extended=True)
    assert g["cycle_sd_kcal"] > 1.0
    assert g["decision"] == "FAIL"
    assert "AFTER extension" in g["reason"]


def test_indeterminate_too_few_replicates():
    g = red.calibration_gate([0.94], TARGET)
    assert g["decision"] == "INDETERMINATE"
    assert g["n_replicates"] == 1


def test_boundary_proximity_triggers_extend():
    # a would-be PASS but abs error sits within 0.5 of the 1.0 boundary (err ~0.6) -> extend (condition 3)
    g = red.calibration_gate([1.50, 1.55, 1.60], TARGET, diagnostics_ok=True)
    # mean ~1.55 -> abs_err ~0.61, within 0.5 of the 1.0 boundary, SD tiny
    assert g["decision"] == "BORDERLINE"
    assert "boundary" in g["reason"]


def test_uses_sample_sd_not_mbar_se():
    # the gate's cycle_sd must be the sample SD of the replicate list, independent of any MBAR SE
    vals = [0.7, 0.9, 1.1]
    g = red.calibration_gate(vals, TARGET, diagnostics_ok=True)
    assert abs(g["cycle_sd_kcal"] - red._sample_sd(vals)) < 1e-12
