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


@pytest.fixture(autouse=True, scope="session")
def _isolate_ternary_rental_receipt():
    with tempfile.TemporaryDirectory() as d:
        os.environ["TVAST_RECEIPT_PATH"] = os.path.join(d, "ternary-vast-rental-receipt.json")
        yield
        os.environ.pop("TVAST_RECEIPT_PATH", None)
