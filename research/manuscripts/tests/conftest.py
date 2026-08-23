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
