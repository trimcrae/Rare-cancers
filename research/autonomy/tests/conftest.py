"""Shared pytest configuration for the autonomy suite."""


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
