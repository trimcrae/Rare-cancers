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
