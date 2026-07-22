"""Auto-stop-on-convergence gating for the RBFE production loop (2026-07-19): stop production once the committed
trajectory converges (connected overlap + dG(t) plateau), capped at the 5 ns production_length. Tests the pure
gating/guards — the live analyzer path needs openmmtools and is validated on GPU."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rbfe_spot_driver as drv  # noqa: E402


def test_autostop_disabled_by_default(monkeypatch):
    monkeypatch.delenv("RBFE_AUTOSTOP_CONVERGENCE", raising=False)
    assert drv._autostop_enabled() is False


def test_autostop_enabled_by_env(monkeypatch):
    monkeypatch.setenv("RBFE_AUTOSTOP_CONVERGENCE", "1")
    assert drv._autostop_enabled() is True
    monkeypatch.setenv("RBFE_AUTOSTOP_CONVERGENCE", "0")
    assert drv._autostop_enabled() is False


def test_converged_early_carries_iteration():
    e = drv._ConvergedEarly(320)
    assert e.iteration == 320
    assert "320" in str(e)


def test_live_converged_false_before_min_fraction(monkeypatch):
    # iteration below max(2*ci, prod_target*min_frac) must short-circuit to False WITHOUT touching openmmtools
    monkeypatch.setenv("RBFE_AUTOSTOP_MIN_FRAC", "0.4")
    logs = []
    # prod_target=1000, min_frac 0.4 -> threshold 400; iter 200 is below -> False, no analyzer built
    assert drv._live_converged(reporter=None, iteration=200, prod_target=1000, ci=40, log=logs.append) is False


def test_live_converged_min_iters_uses_2ci_floor(monkeypatch):
    # small target: floor is 2*ci, so a tiny prod_target*min_frac cannot let it fire before 2 checkpoints
    monkeypatch.setenv("RBFE_AUTOSTOP_MIN_FRAC", "0.0")
    # iter 40 with ci 40 -> below 2*ci(80) -> False before any analyzer work
    assert drv._live_converged(reporter=None, iteration=40, prod_target=100, ci=40, log=lambda *_: None) is False


def test_live_converged_above_threshold_degrades_to_false_without_openmmtools(monkeypatch):
    # above the min threshold it attempts the analyzer; openmmtools/None-reporter -> caught -> False (keep sampling)
    monkeypatch.setenv("RBFE_AUTOSTOP_MIN_FRAC", "0.4")
    logs = []
    out = drv._live_converged(reporter=None, iteration=800, prod_target=1000, ci=40, log=logs.append)
    assert out is False
    assert any("autostop" in m for m in logs)
