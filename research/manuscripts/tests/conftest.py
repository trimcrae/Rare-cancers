"""Shared pytest configuration for the manuscripts test suite."""

def pytest_configure(config):
    """⭐ `committed_artifact` — same meaning as in `research/modalities/tests/conftest.py`: a test of
    a MUTABLE FILE COMMITTED IN THE REPO rather than of a function's behaviour. It fails for a
    different reason than a code test does — the code is fine and the artifact drifted — so the
    workflows that gate real work can exclude it with `-m "not committed_artifact"` and still be
    honest about what they checked. Registered here so the mark stops emitting
    PytestUnknownMarkWarning, which is how a real typo would hide.
    """
    config.addinivalue_line(
        "markers",
        "committed_artifact: asserts a committed artifact's contents, not a function's behaviour")


# ⛔⛔ NO TEST MAY WRITE TO A GIT-TRACKED FILE — installed here so it covers this whole suite
# whatever the entry point. The rule, its measurement and the fix a firing guard is asking for all
# live in `tracked_tree_guard`; this is only the binding.
import os  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tracked_tree_guard  # noqa: E402

tracked_tree_guard.install(os.path.dirname(os.path.abspath(__file__)))


def pytest_sessionfinish(session, exitstatus):
    """The leak half of the tracked-tree guard — see `tracked_tree_guard.assert_tree_unchanged`."""
    tracked_tree_guard.assert_tree_unchanged()
