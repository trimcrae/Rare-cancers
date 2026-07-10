"""Unit tests for abfe_eta (pure ETA math for the ABFE progress snapshot)."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import abfe_eta as e  # noqa: E402


def test_rate_none_without_prior_or_time():
    assert e.per_interval_rate(1000, None, 1.0) is None
    assert e.per_interval_rate(1000, 500, None) is None
    assert e.per_interval_rate(1000, 500, 0.0) is None


def test_rate_positive_and_zero():
    assert e.per_interval_rate(1500, 1000, 1.0) == pytest.approx(500.0)   # 500 iters in 1 h
    assert e.per_interval_rate(1000, 1200, 1.0) == 0.0                    # went backwards (reset) -> 0
    assert e.per_interval_rate(1000, 1000, 2.0) == 0.0                    # no gain -> 0


def test_hours_to_target():
    assert e.hours_to_target(1000, 2000, None) is None                   # unknown rate
    assert e.hours_to_target(2000, 2000, 500.0) == 0.0                    # already at target
    assert e.hours_to_target(2100, 2000, 500.0) == 0.0                    # over target
    assert e.hours_to_target(1000, 2000, 0.0) == math.inf                # stalled
    assert e.hours_to_target(1000, 2000, 500.0) == pytest.approx(2.0)    # 1000 left / 500 per h


def test_blend_rate():
    assert e.blend_rate(None, None) is None
    assert e.blend_rate(400.0, None) == pytest.approx(400.0)              # ignores missing avg
    assert e.blend_rate(None, 600.0) == pytest.approx(600.0)
    assert e.blend_rate(400.0, 600.0, w_now=0.5) == pytest.approx(500.0)  # equal blend


def test_fmt_hours():
    assert e.fmt_hours(None) == "n/a"
    assert e.fmt_hours(math.inf) == "stalled"
    assert e.fmt_hours(0.0) == "done"
    assert e.fmt_hours(0.05) == "<6 min"
    assert e.fmt_hours(3.25) == "3.2h"
    assert e.fmt_hours(30.0) == "1d 6h"
