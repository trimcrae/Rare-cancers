"""Every test path a workflow names must exist, resolved against that step's own working directory.

⛔ THE INCIDENT (measured 2026-08-07, while checking that `Q15`'s glue trigger was actually scanned).
`.github/workflows/method-watch-triggers.yml` ran `python3 -m pytest tests/test_trigger_board_filter.py`
from the repo root. **There is no top-level `tests/` directory in this repository** -- the file lives at
`research/modalities/tests/`. pytest exited "file or directory not found", the step went red, and every
step below it was SKIPPED, including the trigger scan itself. The last three green runs of that workflow
were all 2026-08-03; the scan had not run since.

⚠ THE FAILURE MODE IS THE FAIL-QUIET ONE, WHICH IS WHY A TEST AND NOT A CODE REVIEW. A trigger register
nobody is scanning is indistinguishable from a trigger register with nothing to report: the file still
lists 33 triggers, every query still builds, and `trigger_scan.py --dry-run` still runs clean. Only the
Actions history says the scan stopped. Same shape as `systems/parser_guard.py`'s reason for existing --
"a parser that finds nothing and exits 0" -- one layer up, at the level of whether the parser is invoked
at all.

⚠ IT MUST UNDERSTAND `cd` AND `working-directory:`, OR IT WOULD BE THE OPPOSITE BUG. Eight other
workflows name `tests/<file>.py` and are CORRECT, because their step first does `cd research/modalities`
or declares `working-directory: research/modalities`. A checker that flagged those would produce nine
false alarms around one real one, and would be turned off.
"""
from __future__ import annotations

import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")

STEP_START = re.compile(r"^\s*-\s+(name|uses|run):")
WORKDIR = re.compile(r"^\s*working-directory:\s*(.+?)\s*$")
CD = re.compile(r"^\s*cd\s+([\w./-]+)\s*$")
TEST_TOKEN = re.compile(r"(?<![\w./-])((?:[\w./-]*/)?tests?/[\w./-]*\.py|[\w./-]*test_[\w./-]*\.py)")


def _pytest_paths(body):
    """(line_no, token, cwd) for every test file a pytest invocation names. PURE.

    `cwd` is the step's `working-directory:` if it declares one, else the last bare `cd` seen inside the
    step's own `run:` block -- reset at each step boundary so one step's `cd` cannot leak into the next.
    """
    out = []
    lines = body.split("\n")
    step_wd = None
    run_cd = None
    for i, line in enumerate(lines):
        if STEP_START.match(line):
            step_wd = None
            run_cd = None
        m = WORKDIR.match(line)
        if m:
            step_wd = m.group(1).strip("\"'")
            continue
        m = CD.match(line)
        if m:
            run_cd = m.group(1)
            continue
        if "pytest" not in line:
            continue
        cwd = step_wd or run_cd or ""
        for tok in TEST_TOKEN.findall(line):
            if "${{" in tok or tok.startswith("-"):
                continue
            out.append((i + 1, tok, cwd))
    return out


def test_every_workflow_pytest_path_exists():
    missing = []
    checked = 0
    for wf in sorted(glob.glob(os.path.join(WORKFLOWS, "*.yml"))):
        body = open(wf, encoding="utf-8").read()
        for lineno, tok, cwd in _pytest_paths(body):
            checked += 1
            resolved = os.path.normpath(os.path.join(ROOT, cwd, tok))
            if not os.path.exists(resolved):
                missing.append("%s:%d names %r (cwd=%r) -> %s"
                               % (os.path.basename(wf), lineno, tok, cwd or ".",
                                  os.path.relpath(resolved, ROOT)))
    assert checked > 0, ("no pytest invocation was found in any workflow -- the extractor has broken, "
                        "and a checker that measures nothing is worse than no checker")
    assert not missing, (
        "these workflow steps name a test file that does not exist. pytest exits 'file or directory not "
        "found', the step goes RED, and every step below it is SKIPPED -- which is how the "
        "method-watch trigger scan silently stopped running for four days:\n  " + "\n  ".join(missing))


def test_the_extractor_understands_a_step_local_cd():
    """The positive half: a `cd research/modalities` step naming `tests/x.py` must NOT be flagged."""
    body = ("      - name: Offline unit tests\n"
            "        run: |\n"
            "          cd research/modalities\n"
            "          python -m pytest tests/test_map_edit_anchors.py -q\n")
    got = _pytest_paths(body)
    assert got == [(4, "tests/test_map_edit_anchors.py", "research/modalities")], got
    assert os.path.exists(os.path.join(ROOT, got[0][2], got[0][1]))


def test_the_extractor_understands_working_directory():
    body = ("      - name: Unit tests\n"
            "        working-directory: research/modalities\n"
            "        run: |\n"
            "          python -m pytest tests/test_map_edit_anchors.py -q\n")
    got = _pytest_paths(body)
    assert got and got[0][2] == "research/modalities", got


def test_a_cd_does_not_leak_across_a_step_boundary():
    """⛔ THE FALSE-NEGATIVE THIS GUARDS. If one step's `cd` leaked into the next, the very bug this file
    exists for would resolve against the wrong directory and pass."""
    body = ("      - name: first\n"
            "        run: |\n"
            "          cd research/modalities\n"
            "          python -m pytest tests/test_map_edit_anchors.py -q\n"
            "      - name: second\n"
            "        run: |\n"
            "          python3 -m pytest tests/test_trigger_board_filter.py -q\n")
    got = _pytest_paths(body)
    assert len(got) == 2, got
    assert got[1][2] == "", "the first step's cd leaked into the second"
    assert not os.path.exists(os.path.join(ROOT, got[1][1])), (
        "this is the exact broken invocation from method-watch-triggers.yml and it must not resolve")
