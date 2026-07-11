"""Unit tests for job_progress_monitor — pure parsing of real captured log tails into progress/ETA/hang."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import job_progress_monitor as m  # noqa: E402

# --- Real BOLTZ (NR-V04 ternary) log lines captured 2026-07-11 from the running pilot -------------------------
BOLTZ_LOG = """
2026-07-11T14:30:00.0Z   running: boltz predict /opt/ml/processing/output/control-vhl-vh032.yaml --use_msa_server --out_dir /opt/ml/processing/output/control/seed_1 --no_kernels --seed 1
2026-07-11T14:31:10.0Z Predicting DataLoader 0: 100%|##########| 1/1 [03:39<00:00,  0.00it/s]Number of failed examples: 0
2026-07-11T14:31:20.0Z   running: boltz predict /opt/ml/processing/output/nr4a1-nrv04-ternary.yaml --use_msa_server --out_dir /opt/ml/processing/output/nr4a1/seed_1 --no_kernels --seed 1
2026-07-11T14:33:00.0Z Predicting DataLoader 0: 100%|##########| 1/1 [03:39<00:00,  0.00it/s]Number of failed examples: 0
2026-07-11T14:34:25.0Z   running: boltz predict /opt/ml/processing/output/nr4a1-nrv04-ternary.yaml --use_msa_server --out_dir /opt/ml/processing/output/nr4a1/seed_2 --no_kernels --seed 2
"""

# --- Real ABFE (nr4a3 spot g5) window-start lines ------------------------------------------------------------
ABFE_LOG = """
2026-07-11T14:12:00.0Z [abfe] built + cached reference system (207200 particles) — resume-safe
2026-07-11T14:14:00.0Z [abfe] nan-guard v2 active (window  5, seed 0)
2026-07-11T14:20:00.0Z [abfe] nan-guard v2 active (window  6, seed 0)
2026-07-11T14:26:00.0Z [abfe] nan-guard v2 active (window  7, seed 0)
"""

ABFE_DONE = ABFE_LOG + "2026-07-11T15:40:00.0Z [abfe] DG_BIND -9.312 ± 0.44 kcal/mol\n2026-07-11T15:40:01.0Z [abfe] SHARD_DONE leg=complex windows [0,16)\n"


# Real ABFE tail AS FETCHED THROUGH the GitHub Actions log API: each line has GitHub's ingest timestamp THEN
# the real CloudWatch event time (prepended by tail_cloudwatch.py) THEN the message.
ABFE_DOUBLE_TS = """
2026-07-11T14:44:30.322Z 2026-07-11T14:23:22Z [abfe] nan-guard v2 active (window 5, seed 0)
2026-07-11T14:44:30.324Z 2026-07-11T14:23:38Z [abfe] nan-guard v2 active (window 6, seed 0)
"""


def test_parse_ts_uses_real_event_time_not_github_ingest():
    # Must return the CloudWatch event time 14:23:38, NOT GitHub's ingest time 14:44:30.
    line = "2026-07-11T14:44:30.324Z 2026-07-11T14:23:38Z [abfe] nan-guard v2 active (window 6, seed 0)"
    assert m.parse_ts(line).strftime("%H:%M:%S") == "14:23:38"


def test_abfe_double_ts_end_to_end():
    cur = m.parse_abfe(ABFE_DOUBLE_TS)
    assert cur["index"] == 6
    assert cur["last_ts"] == "2026-07-11T14:23:38Z"   # real event time survived
    a = m.analyse(cur, now_iso="2026-07-11T14:44:30Z", hang_min=25.0)
    assert a["marker_age_min"] == 20.9                # 14:23:38 → 14:44:30 ≈ 20.9 min (not a hang at 25-min thr)
    assert a["hang"] is False


def test_detect_kind():
    assert m.detect_kind(BOLTZ_LOG) == "boltz"
    assert m.detect_kind(ABFE_LOG) == "abfe"
    assert m.detect_kind("nothing here") == "unknown"


def test_parse_boltz_current_member_and_counts():
    cur = m.parse_boltz(BOLTZ_LOG)
    assert cur["unit"] == "nr4a1-nrv04-ternary seed 2"
    assert cur["completed"] == 2          # control seed1 + nr4a1 seed1
    assert cur["started"] == 3
    assert cur["last_ts"] == "2026-07-11T14:34:25Z"
    assert cur["index"] == 2


def test_parse_abfe_highest_window():
    cur = m.parse_abfe(ABFE_LOG)
    assert cur["index"] == 7
    assert cur["unit"] == "window 7"
    assert cur["last_ts"] == "2026-07-11T14:26:00Z"
    assert cur["done"] is False


def test_parse_abfe_done():
    cur = m.parse_abfe(ABFE_DONE)
    assert cur["done"] is True
    assert cur["done_ts"] == "2026-07-11T15:40:01Z"


def test_abfe_rate_and_eta():
    prev = {"kind": "abfe", "index": 5, "last_ts": "2026-07-11T14:14:00Z", "done": False}
    cur = m.parse_abfe(ABFE_LOG)   # index 7 at 14:26 → 12 min for 2 windows = 6 min/window
    a = m.analyse(cur, prev=prev, total_units=16, now_iso="2026-07-11T14:27:00Z")
    assert a["min_per_unit"] == 6.0
    # 16 windows, current index 7 (0-based) → 16-7-1 = 8 remaining → 48 min ETA
    assert a["units_remaining"] == 8
    assert a["eta_min"] == 48.0
    assert a["hang"] is False


def test_hang_detection_when_marker_stale():
    cur = m.parse_abfe(ABFE_LOG)   # last marker 14:26
    a = m.analyse(cur, now_iso="2026-07-11T15:10:00Z", hang_min=25.0)  # 44 min later, no new window
    assert a["marker_age_min"] == 44.0
    assert a["hang"] is True


def test_no_hang_when_done_even_if_stale():
    cur = m.parse_abfe(ABFE_DONE)
    a = m.analyse(cur, now_iso="2026-07-11T18:00:00Z", hang_min=25.0)
    assert a["done"] is True
    assert a["hang"] is False       # a finished shard is never a hang


def test_et_conversion_is_eastern_12h():
    # 14:26 UTC = 10:26 AM ET (EDT, UTC-4)
    assert m._et("2026-07-11T14:26:00Z") == "10:26 AM ET"
    assert m._et("2026-07-11T00:05:00Z") == "8:05 PM ET"   # prior day evening
    assert m._et(None) == "—"


def test_sample_gap_recorded_when_index_stalls():
    # Real-timestamp regime: a stalled window keeps its true last_ts, so marker_age (now - last_ts) catches it.
    prev = {"kind": "abfe", "index": 7, "last_ts": "2026-07-11T14:26:00Z", "done": False}
    cur = m.parse_abfe(ABFE_LOG)   # still index 7, real last_ts frozen at 14:26
    a = m.analyse(cur, prev=prev, total_units=16, now_iso="2026-07-11T15:06:00Z", hang_min=25.0)
    assert a["min_per_unit"] is None       # no advance
    assert a["hang"] is True               # 40-min-old marker → hang via marker_age


def test_boltz_eta_across_samples():
    prev = {"kind": "boltz", "index": 0, "last_ts": "2026-07-11T14:31:10Z"}
    cur = m.parse_boltz(BOLTZ_LOG)   # index 2 at 14:34:25
    a = m.analyse(cur, prev=prev, total_units=6, now_iso="2026-07-11T14:35:00Z")
    assert a["min_per_unit"] is not None and a["min_per_unit"] > 0
    assert a["units_remaining"] == 3      # 6 - 2 - 1
    assert a["eta_min"] is not None


def test_intra_log_eta_without_prev():
    # A LONE snapshot (no --prev) still yields an ETA from the recent intra-log per-window rate.
    # ABFE_LOG: window 6 @ 14:20, window 7 @ 14:26 → 6 min/window; at window 7/16 → 8 remaining.
    cur = m.parse_abfe(ABFE_LOG)
    assert cur["intra_prev_index"] == 6 and cur["intra_prev_ts"] == "2026-07-11T14:20:00Z"
    a = m.analyse(cur, prev=None, total_units=16, now_iso="2026-07-11T14:29:00Z")
    assert a["recent_rate"] is True
    assert a["min_per_unit"] == 6.0
    assert a["units_remaining"] == 8        # 16 - 7 - 1
    assert a["eta_min"] == 48.0             # 8 * 6
    assert a["eta_et"] is not None


def test_explicit_prev_takes_precedence_over_intra_log():
    # When a real prior sample is supplied it should drive the rate (recent_rate stays False).
    prev = {"kind": "abfe", "index": 5, "last_ts": "2026-07-11T14:14:00Z"}
    cur = m.parse_abfe(ABFE_LOG)            # index 7 @ 14:26
    a = m.analyse(cur, prev=prev, total_units=16, now_iso="2026-07-11T14:29:00Z")
    assert a.get("recent_rate") is False
    assert a["min_per_unit"] == 6.0         # (14:26-14:14)/(7-5) = 12/2 = 6
