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
