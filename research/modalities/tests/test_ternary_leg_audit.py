"""Reviewer condition 8 (2026-07-19) — the pure large-leg cancellation / antisymmetry audit for the 47.28-type
leg. No GPU; exercises cancellation_metrics (the .nc-independent algebra)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_fep_reduce as red  # noqa: E402


def test_large_legs_that_cancel_well_have_small_ratio():
    # two large legs (~47) whose difference (ΔΔG_coop) is small -> strong cancellation, low ratio
    m = red.cancellation_metrics(ternary_mean=47.28, ternary_sd=0.5, binary_mean=46.34, binary_sd=0.5)
    assert abs(m["ddg_coop_kcal"] - 0.94) < 1e-9
    assert m["max_leg_magnitude_kcal"] == 47.28
    assert m["cancellation_ratio"] < 0.03            # 0.94 / 47.28 ~ 0.02 -> well cancelled
    assert abs(m["leg_sd_quadrature_kcal"] - (0.5 ** 2 + 0.5 ** 2) ** 0.5) < 1e-9


def test_poor_cancellation_flagged_by_large_ratio():
    # ΔΔG_coop is a large fraction of the legs -> not a well-cancelled difference
    m = red.cancellation_metrics(ternary_mean=3.0, ternary_sd=0.4, binary_mean=-2.0, binary_sd=0.4)
    assert m["ddg_coop_kcal"] == 5.0
    assert m["cancellation_ratio"] > 1.0             # 5.0 / 3.0 > 1


def test_cancellation_handles_missing_sd():
    m = red.cancellation_metrics(47.0, None, 46.0, None)
    assert m["leg_sd_quadrature_kcal"] is None
    assert abs(m["ddg_coop_kcal"] - 1.0) < 1e-9


def test_zero_magnitude_ratio_none():
    m = red.cancellation_metrics(0.0, 0.1, 0.0, 0.1)
    assert m["cancellation_ratio"] is None


def test_audit_empty_when_no_legs(tmp_path, monkeypatch):
    # with no checkpoints present the audit is honest-empty
    monkeypatch.setenv("CKPT_DIR", str(tmp_path))
    monkeypatch.setenv("INPUT_DIR", str(tmp_path / "nope"))
    import importlib
    importlib.reload(red)
    a = red.leg_algebra_audit("calib_hi -> calib_lo")
    assert a["available"] is False
    assert a["cancellation"] is None
    # restore module default env for other tests
    importlib.reload(red)
