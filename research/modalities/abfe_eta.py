#!/usr/bin/env python3
"""Pure ETA math for the ABFE progress snapshot (unit-tested; no AWS/matplotlib).

The abfe-progress snapshot counts, per leg, the total λ-window iterations completed so far (from the S3
window_NN.jsonl line counts) against the target total (n_windows × target_iters). Comparing two hourly
snapshots gives a burn rate (iterations/hour); the remaining iterations / rate is the ETA. This module keeps
that arithmetic pure so it can be tested, and the workflow imports it.
"""
from __future__ import annotations

import math


def per_interval_rate(iters_now, iters_prev, dt_hours):
    """Iterations/hour between two snapshots. Returns:
      - None  if we cannot measure (no prior snapshot, or non-positive elapsed time),
      - 0.0   if measured but no progress this interval (a spot restart / stall — real information),
      - >0    the positive burn rate."""
    if iters_prev is None or dt_hours is None or dt_hours <= 0:
        return None
    gained = iters_now - iters_prev
    if gained <= 0:
        return 0.0
    return gained / dt_hours


def hours_to_target(iters_now, target_total, rate_per_hour):
    """Hours until iters_now reaches target_total at rate_per_hour.
      - None  if the rate is unknown (first snapshot),
      - 0.0   if already at/over target,
      - inf   if the rate is 0 (no progress — can't estimate; flag as stalled/restarting),
      - >0    the estimated hours remaining."""
    if rate_per_hour is None:
        return None
    remaining = target_total - iters_now
    if remaining <= 0:
        return 0.0
    if rate_per_hour <= 0:
        return math.inf
    return remaining / rate_per_hour


def blend_rate(rate_now, rate_avg, w_now=0.5):
    """Optionally smooth the instantaneous hourly rate with a longer-run average (both iters/hour) so a single
    slow/fast hour (spot churn) doesn't whipsaw the ETA. Ignores None inputs; returns None if both are None."""
    rates = [(r, w) for r, w in ((rate_now, w_now), (rate_avg, 1.0 - w_now)) if r is not None]
    if not rates:
        return None
    tw = sum(w for _, w in rates)
    return sum(r * w for r, w in rates) / tw if tw else None


def fmt_hours(h):
    """Human ETA: 'n/a' (unknown), 'stalled' (inf), '<6 min' or 'X.Xh' / 'Yd Zh'."""
    if h is None:
        return "n/a"
    if h == math.inf:
        return "stalled"
    if h <= 0:
        return "done"
    if h < 0.1:
        return "<6 min"
    if h < 24:
        return f"{h:.1f}h"
    d = int(h // 24)
    return f"{d}d {h - 24 * d:.0f}h"
