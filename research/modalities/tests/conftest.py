import os
import sys

# Make the modalities scripts importable as top-level modules (fpocket_lib, etc.).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ★ NO TEST MAY WRITE A RENTAL RECEIPT INTO THE WORKING TREE (2026-07-27).
# `ternary_vast_launch.submit()` writes `ternary-vast-rental-receipt.json` on every path, including the
# failure paths several tests exercise with a mocked backend. Without this redirect the suite left a real
# receipt — carrying a MOCKED 403 and a fabricated rental — sitting in `research/modalities/`, ready to be
# committed by anyone running `git add -A`. A test that mutates the repo it is testing is exactly how a
# fabricated artifact reaches a public branch, and this repo's rules on price artifacts are strict.
import tempfile

import pytest


def pytest_configure(config):
    """★★ `committed_artifact` — A TEST OF DATA, NOT OF CODE, AND IT MUST NOT GATE GPU WORK (2026-07-28).

    A test marked this way asserts something about a MUTABLE FILE COMMITTED IN THE REPO rather than about
    the behaviour of a function. That is a legitimate and valuable thing to assert — the row loss it caught
    was real — but it fails for a completely different reason than a code test does: the code is fine and
    the artifact drifted. Mixing the two in one gating job is what took the whole ternary lane down for
    ~90 minutes when a launch job's ledger write evicted a pinned row: seven consecutive red runs, and
    market-gate, collect and launch all blocked behind a bookkeeping assertion.

    So the workflow runs `-m "not committed_artifact"` in the job every task depends on, and runs these in
    a separate job that depends on nothing — LOUD (a red job, an `::error` annotation) but not a gate.
    Registered here rather than in a pytest.ini so that `-m committed_artifact` cannot silently select
    nothing because of a typo: `--strict-markers` in the workflow makes an unknown marker an error.
    """
    config.addinivalue_line(
        "markers",
        "committed_artifact: asserts the content of a mutable file committed in the repo, not the "
        "behaviour of code. Loud when it fails, but never a gate on GPU operations.")


@pytest.fixture(autouse=True, scope="session")
def _isolate_ternary_rental_receipt():
    with tempfile.TemporaryDirectory() as d:
        os.environ["TVAST_RECEIPT_PATH"] = os.path.join(d, "ternary-vast-rental-receipt.json")
        yield
        os.environ.pop("TVAST_RECEIPT_PATH", None)


@pytest.fixture(autouse=True, scope="session")
def _isolate_inflight_board():
    """★ NOR MAY A TEST WRITE AN IN-FLIGHT BOARD INTO THE WORKING TREE (2026-07-31) — the same rule as the
    receipt above, for the same reason, found the same way.

    `congeneric_fanout_vast.mode_monitor` and `nrv04_vast_launch.retro_collect` publish their board fragment
    as the last act of a progress check, and `tests/test_monitor_survives_unreadable_board.py` drives that
    function against a MOCKED object store. Without this redirect the suite left
    `research/modalities/inflight-board.d/step1-fanout.json` in the tree, carrying invented unit ids and a
    fabricated `0 of 19 landed` note — a spend-reporting artifact assembled entirely from a mock, one
    `git add -A` away from a branch. Redirected here rather than guarded at each call site, so a THIRD lane
    wired to the board tomorrow inherits the protection instead of having to remember it.
    """
    with tempfile.TemporaryDirectory() as d:
        os.environ["INFLIGHT_BOARD_DIR"] = d
        yield
        os.environ.pop("INFLIGHT_BOARD_DIR", None)


# =============================================================================================================
# ⛔⛔ THE VAST ACCOUNT IS STOOD DOWN IN THIS REPOSITORY, AND THAT IS A REAL STATE THESE TESTS MUST CONTROL FOR.
#
# `research/modalities/vast-RENTAL-HOLD.json` is committed (2026-08-26), and
# `gpu_backend.VastBackend.submit` refuses every rental while it exists. That is correct in production and
# fatal to a unit test whose whole subject is what `submit` DOES once it gets past the gate: eight tests
# across five files went red on the hold rather than on their own assertions.
#
# ⚠ WHY THIS IS A FIXTURE AND NOT AN ENV-VAR BYPASS IN `gpu_backend`. A spending gate with a documented
# "set this to skip me" switch is not a gate — a workflow could set it once and stand the account back up
# silently, which is the failure mode the hold exists to prevent. The neutralisation therefore lives HERE,
# in the test harness, where it cannot reach a runner: production has no conftest.
#
# ⚠ AND IT IS SCOPED TO THE MECHANICS, NOT TO THE GATE. `test_vast_account_rental_hold.py` binds the real
# `vast_rental_hold` at import time (`_real_hold`) so this fixture cannot reach it, and its submit-refusal
# test re-patches inside the test body. So the hold's OWN behaviour is still measured against the real
# function; only the lanes' rental mechanics are freed to run.
@pytest.fixture(autouse=True)
def _vast_rental_hold_neutralised_for_mechanics(monkeypatch):
    try:
        import gpu_backend
    except Exception:  # noqa: BLE001 — the modalities deps are absent in some sandboxes; nothing to neutralise
        return
    monkeypatch.setattr(gpu_backend, "vast_rental_hold", lambda root=None: None, raising=False)


# =============================================================================================================
# ⛔⛔ AND THE SAME IS TRUE OF THE NO-GPU BAN, WHICH IS A SECOND REAL STATE THESE TESTS MUST CONTROL FOR.
#
# trimcrae, 2026-09-02: "You shouldn't be doing any GPU runs as part of this automation." Recorded in
# `research/autonomy/autonomy-state.json -> gpu_spend_prohibited` and enforced by `research/autonomy/gpu_ban.py`
# at four call sites, three of which this suite exercises: `gpu_backend._vast_request`, every
# `Backend.submit`, and `sagemaker_submit.submit_spot`. Correct in production; fatal to a unit test whose
# subject is what a launcher DOES once it is past the gate.
#
# ⚠ ONE SEAM, NOT FOUR. Every call site holds a reference to the MODULE (`import gpu_ban as _gpu_ban`) and
# both entry points funnel through `gpu_ban.read_ban`, so patching that one function neutralises all of
# them — and there is no env-var bypass in `gpu_ban` itself, for the reason stated above: a spending gate
# with a documented "set this to skip me" switch is not a gate. This lives in the test harness, which no
# runner ever loads.
#
# ⚠ SCOPED TO THE MECHANICS, NOT TO THE GATE. `research/autonomy/tests/test_the_no_gpu_ban_is_enforced.py`
# binds the real `read_ban` at import (`_real_read_ban`) and is in a different suite with a different
# conftest, so the ban's OWN behaviour — including the reading of the committed state file — is never
# measured against this stub.
@pytest.fixture(autouse=True)
def _gpu_ban_neutralised_for_mechanics(monkeypatch):
    # ⚠ THE PATH IS INSERTED HERE RATHER THAN INHERITED. `gpu_backend` and `sagemaker_submit` both put
    # `research/autonomy` on `sys.path` when they import, so in practice the bare `import gpu_ban` below
    # already resolves by the time any fixture runs — but that makes this fixture's REACHABILITY a side
    # effect of somebody else's import, and its `except: return` would turn a broken assumption into a
    # SILENT no-op rather than an error. Measured 2026-09-02 with a positive control: disabling this
    # fixture reddens 9 tests across test_vast_start_refusal.py and test_gpu_backend.py, so it is
    # load-bearing and must not be allowed to fail quietly.
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                                      "..", "autonomy"))
    try:
        import gpu_ban
    except Exception:  # noqa: BLE001 — nothing imported the gate in this sandbox; nothing to neutralise
        return
    monkeypatch.setattr(
        gpu_ban, "read_ban",
        lambda state_path=None: {"refuses": False, "record": {"active": False}, "state_path": state_path,
                                 "why": "neutralised by the modalities test harness"},
        raising=False)


# ⛔⛔ NO TEST MAY WRITE TO A GIT-TRACKED FILE. The rule, its measurement (AUT-PD-186) and the fix a
# firing guard is asking for live in research/manuscripts/tests/tracked_tree_guard.py; this is the
# binding for this suite. One module, three suites — a second copy would be a second thing to drift.
import os  # noqa: E402
import sys  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "..", "manuscripts", "tests"))
import tracked_tree_guard  # noqa: E402

tracked_tree_guard.install(_HERE)


def pytest_sessionfinish(session, exitstatus):
    """The leak half of the tracked-tree guard — see `tracked_tree_guard.assert_tree_unchanged`."""
    tracked_tree_guard.assert_tree_unchanged()
