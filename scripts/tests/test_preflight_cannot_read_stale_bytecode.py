"""Preflight must judge the bytes it is about to commit, not a cached compilation of them.

⛔ WHY THIS EXISTS, MEASURED 2026-08-27. `./scripts/preflight.sh` reported

    2 failed, 211 passed
    FAILED research/autonomy/tests/...::test_an_undeclared_lease_counts_as_one_agent
    FAILED research/autonomy/tests/...::test_a_full_cap_is_a_real_stop_and_names_every_holder

against a working tree whose source could not produce either failure. `inspect.getsource` printed
the corrected function; the interpreter ran the previous one. The two files:

    research/autonomy/__pycache__/continuity.cpython-311.pyc   written 23:28:57.634
    research/autonomy/continuity.py                            written 23:28:57.840

and the .pyc's 16-byte header recorded source mtime 1787873337 / size 21219 — exactly the current
source's. CPython's default invalidation compares (mtime in WHOLE SECONDS, size). The edit landed
0.2 s later, inside the same second, and left the file the same number of bytes, so both fields
agreed and the stale bytecode was reused. Deleting the caches took the suite to `213 passed` with
no source change.

⛔ THE FAILURE WE GOT WAS THE CHEAP DIRECTION. A false red costs an hour of confusion. The same
mechanism produces a false GREEN — a guard executing the version of itself from before it was
broken — and that one has no symptom at all, which is the exact defect class preflight.sh's header
was written about ("a check that reports while measuring nothing actionable").

⛔ AND NO GATE CAN SEE IT. Every linter in the repository reads the SOURCE; the divergence lives
between the source and what the interpreter executes, so a green board is fully consistent with it.
That is why the guard is structural (preflight must isolate the cache) and behavioural (the
mechanism itself is reproduced below, deterministically, rather than described).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import textwrap

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREFLIGHT = os.path.join(REPO, "scripts", "preflight.sh")


@pytest.fixture(scope="module")
def script() -> str:
    with open(PREFLIGHT, encoding="utf-8") as fh:
        return fh.read()


def _uncommented(script: str) -> list[tuple[int, str]]:
    """(line number, text) for lines that are not wholly a comment.

    The incident above is written up at length in the script's own header, so a test that grepped
    the raw text would pass on the PROSE describing the fix after somebody deleted the fix.
    """
    out = []
    for i, line in enumerate(script.split("\n"), start=1):
        if line.lstrip().startswith("#"):
            continue
        out.append((i, line))
    return out


def test_preflight_exports_a_private_bytecode_cache(script):
    """⛔ The read side, not the write side. `PYTHONDONTWRITEBYTECODE=1` stops only THIS run from
    writing; a .pyc another process wrote a second ago is still read, which is precisely how the
    incident happened — the stale cache was written by an earlier run, not by preflight."""
    live = [text for _, text in _uncommented(script)]
    exported = [t for t in live if re.search(r"^\s*export\s+PYTHONPYCACHEPREFIX=", t)]
    assert exported, (
        "preflight.sh does not export PYTHONPYCACHEPREFIX, so every gate it runs may execute "
        "bytecode compiled from a previous version of the file it is judging"
    )
    assert any("PREFLIGHT_PYCACHE" in t for t in exported), (
        "PYTHONPYCACHEPREFIX is exported but not from the run's own directory"
    )
    assert any(re.search(r"PREFLIGHT_PYCACHE=.*mktemp -d", t) for t in live), (
        "the cache directory is not created fresh per run — a stable directory outside the tree "
        "keeps the same (mtime-second, size) collision, it merely moves it"
    )


def test_the_cache_is_isolated_before_any_gate_runs(script):
    """A cache isolated after gate 1 leaves gate 1 reading stale bytecode."""
    live = _uncommented(script)
    export_at = min(n for n, t in live if re.search(r"^\s*export\s+PYTHONPYCACHEPREFIX=", t))
    invocations = [n for n, t in live if re.search(r"\bpython3?\b|\bpytest\b", t)]
    assert invocations, "no python invocation found in preflight.sh — has the parser gone stale?"
    assert export_at < min(invocations), (
        f"PYTHONPYCACHEPREFIX is exported at line {export_at}, after the first python invocation "
        f"at line {min(invocations)}"
    )


def test_the_temporary_cache_is_removed(script):
    live = [t for _, t in _uncommented(script)]
    assert any("trap" in t and "PREFLIGHT_PYCACHE" in t for t in live), (
        "the per-run cache directory is never cleaned up, so every preflight leaks one"
    )


# ---------------------------------------------------------------------------------------------
# ⛔ THE MECHANISM ITSELF, REPRODUCED. Not a description of the 2026-08-27 incident — the same
# collision, forced deterministically with os.utime instead of raced against the wall clock.
# ---------------------------------------------------------------------------------------------

_V1 = "def answer():\n    return 'STALE'\n"
_V2 = "def answer():\n    return 'FRESH'\n"
assert len(_V1) == len(_V2), "the reproduction needs both versions to be the same byte length"


def _env(extra: dict | None = None) -> dict:
    """A child environment with the cache settings scrubbed, THEN whatever the test is testing.

    ⛔⛔ THE WRITE SIDE AND THE READ SIDE MUST BE SCRUBBED THE SAME WAY, AND THE FIRST VERSION OF
    THIS FILE SCRUBBED ONLY THE READ SIDE — so `_forge_the_collision` compiled v1 under the
    INHERITED environment. Standalone that is empty and the collision reproduced. Under
    `preflight.sh`, which now exports `PYTHONPYCACHEPREFIX`, the .pyc went to the prefix directory
    while the reader looked beside the module, found nothing, compiled fresh, and returned FRESH.
    ⭐ THE CONTROL IS WHAT FAILED, WHICH IS PRECISELY ITS JOB: `test_the_collision_really_does_hide_an_edit`
    went red the first time the guard ran inside the gate it guards, so a green board never had the
    chance to rest on a reproduction that had quietly stopped reproducing. Caught 2026-08-27 by the
    same preflight run this file was written for.
    """
    env = dict(os.environ)
    env.pop("PYTHONPYCACHEPREFIX", None)
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    env.update(extra or {})
    return env


def _forge_the_collision(tmpdir: str) -> str:
    """Write v1, compile it, overwrite with v2 at the SAME mtime and size. Returns the dir."""
    mod = os.path.join(tmpdir, "staleness_demo.py")
    with open(mod, "w", encoding="utf-8") as fh:
        fh.write(_V1)
    subprocess.run([sys.executable, "-c", "import staleness_demo"],
                   cwd=tmpdir, env=_env(), check=True)
    assert os.path.isdir(os.path.join(tmpdir, "__pycache__")), (
        "no bytecode was written beside the module, so there is nothing stale to read — the child "
        "environment is not scrubbed and this test would be measuring nothing")
    stat = os.stat(mod)
    with open(mod, "w", encoding="utf-8") as fh:
        fh.write(_V2)
    # The whole bug in one call: CPython compares whole seconds and size, and both now match.
    os.utime(mod, (stat.st_atime, stat.st_mtime))
    return tmpdir


def _ask(tmpdir: str, env_extra: dict | None = None) -> str:
    out = subprocess.run(
        [sys.executable, "-c", "import staleness_demo; print(staleness_demo.answer())"],
        cwd=tmpdir, env=_env(env_extra), capture_output=True, text=True, check=True)
    return out.stdout.strip()


def test_the_collision_really_does_hide_an_edit():
    """⚠ THE CONTROL. If this ever stops reproducing, the guard below is measuring nothing and the
    comment above is describing a bug that no longer exists — say so rather than deleting it."""
    with tempfile.TemporaryDirectory() as d:
        _forge_the_collision(d)
        assert _ask(d) == "STALE", (
            "CPython no longer reuses a .pyc whose recorded (mtime-second, size) match the source. "
            "If invalidation became hash-based by default, this whole guard is obsolete — verify "
            "that before removing it."
        )


def test_a_private_cache_directory_defeats_it():
    """The fix preflight applies, exercised against the reproduction rather than asserted."""
    with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as cache:
        _forge_the_collision(d)
        assert _ask(d, {"PYTHONPYCACHEPREFIX": cache}) == "FRESH"


def test_not_writing_bytecode_is_not_the_fix():
    """⛔ The tempting one-liner, shown to be insufficient. PYTHONDONTWRITEBYTECODE stops this
    process writing a cache; it does not stop it READING one somebody else wrote — which is the
    only direction that matters, because the stale .pyc is always from an earlier run."""
    with tempfile.TemporaryDirectory() as d:
        _forge_the_collision(d)
        assert _ask(d, {"PYTHONDONTWRITEBYTECODE": "1"}) == "STALE"
