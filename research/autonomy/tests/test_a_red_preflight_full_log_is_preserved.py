"""A red PREFLIGHT_FULL=1 log must land in PREFLIGHT_LOG_DIR even though no receipt is written.

⛔⛔ WHY THIS EXISTS, MEASURED 2026-08-28 (AUT-PROP-018, run 33190817704). `record_preflight()`
used to copy the log to `PREFLIGHT_LOG_DIR` only inside the success path, AFTER the `EXIT=0` check
— so a genuine red run hit `_refuse()` and returned before the log was ever written to the repo
tree. `publish_artifacts.sh` then found neither the receipt nor the log and printed "nothing to
stage", and the one diagnostic that would explain the failure was gone the moment the ephemeral
Actions runner was torn down. The workflow step's own comment claims this cannot happen ("the log
itself still lands on main either way") — the comment described the intended behaviour; the code
did not implement it. The only surviving copy that day was pulled back out of the raw Actions
console output through the API, after the fact.

The fix moves the copy to right after the log is confirmed to be a real FULL run against the
pinned sha (PINNED_SHA line matches, FULL_BANNER present) — before the EXIT= check, so the log is
preserved on every codepath that gets that far, red or green. Only the JSON *receipt* (a claim of
success) stays conditional on EXIT=0.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import record_bar_evidence  # noqa: E402

SHA = "a" * 40


def _write_log(path, lines):
    path.write_text("\n".join(lines) + "\n")


def test_a_red_run_still_preserves_its_log(tmp_path, monkeypatch):
    monkeypatch.setattr(record_bar_evidence, "PREFLIGHT_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(record_bar_evidence, "PREFLIGHT_DIR", tmp_path / "receipts")

    log = tmp_path / "run.log"
    _write_log(log, [
        f"PINNED_SHA={SHA}",
        record_bar_evidence.FULL_BANNER,
        "PREFLIGHT FAILED -- do not commit.",
        "EXIT=1",
    ])

    rc = record_bar_evidence.record_preflight(SHA, log)

    assert rc == 1, "a red run must still refuse to write a passing receipt"
    kept = record_bar_evidence.PREFLIGHT_LOG_DIR / f"{SHA}.log"
    assert kept.exists(), "the log must be preserved even though the run was red"
    assert kept.read_text() == log.read_text()
    receipt = record_bar_evidence.PREFLIGHT_DIR / f"{SHA}.json"
    assert not receipt.exists(), "a red run must never write a passing receipt"


def test_an_unterminated_run_still_preserves_its_log(tmp_path, monkeypatch):
    monkeypatch.setattr(record_bar_evidence, "PREFLIGHT_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(record_bar_evidence, "PREFLIGHT_DIR", tmp_path / "receipts")

    log = tmp_path / "run.log"
    _write_log(log, [
        f"PINNED_SHA={SHA}",
        record_bar_evidence.FULL_BANNER,
        "-- abandoned mid-run, no EXIT= marker --",
    ])

    rc = record_bar_evidence.record_preflight(SHA, log)

    assert rc == 1
    kept = record_bar_evidence.PREFLIGHT_LOG_DIR / f"{SHA}.log"
    assert kept.exists(), "an unterminated run is still diagnostic evidence and must be preserved"


def test_a_green_run_still_writes_both_log_and_receipt(tmp_path, monkeypatch):
    monkeypatch.setattr(record_bar_evidence, "PREFLIGHT_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(record_bar_evidence, "PREFLIGHT_DIR", tmp_path / "receipts")

    log = tmp_path / "run.log"
    _write_log(log, [
        f"PINNED_SHA={SHA}",
        record_bar_evidence.FULL_BANNER,
        "PREFLIGHT OK",
        "EXIT=0",
    ])

    rc = record_bar_evidence.record_preflight(SHA, log)

    assert rc == 0
    assert (record_bar_evidence.PREFLIGHT_LOG_DIR / f"{SHA}.log").exists()
    assert (record_bar_evidence.PREFLIGHT_DIR / f"{SHA}.json").exists()


def test_a_log_for_the_wrong_sha_is_never_preserved(tmp_path, monkeypatch):
    """The PINNED_SHA/FULL_BANNER checks gate whether this log is trustworthy AT ALL — those must
    still refuse outright, never touching PREFLIGHT_LOG_DIR, unlike the pass/fail checks below them.
    """
    monkeypatch.setattr(record_bar_evidence, "PREFLIGHT_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(record_bar_evidence, "PREFLIGHT_DIR", tmp_path / "receipts")

    log = tmp_path / "run.log"
    _write_log(log, [
        "PINNED_SHA=" + "b" * 40,
        record_bar_evidence.FULL_BANNER,
        "EXIT=0",
    ])

    rc = record_bar_evidence.record_preflight(SHA, log)

    assert rc == 1
    assert not (tmp_path / "logs").exists(), "a log for a different sha must not be kept as if it were this one's"
