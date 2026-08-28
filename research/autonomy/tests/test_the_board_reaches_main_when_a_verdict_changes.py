#!/usr/bin/env python3
"""⛔ THE HEALTH BOARD ON `main` WAS FROZEN BY THE STEP THAT DECIDES WHETHER TO COMMIT IT.

`autonomy-tick.yml` graded the loop with `health.py --write`, which REPLACES
`research/autonomy/health.json` with this run's board, and then asked a separate step
`health.py --commit-worthy` whether that board was worth committing. `--commit-worthy` recomputes the
board and compares it to the file at `--health` — which the write step had just overwritten. So it
compared the board against itself, answered "every verdict is unchanged", and the board reached the
trunk only through the keep-alive expiry path, never on a verdict change.

⚠ MEASURED 2026-08-28 in run 33200659155's own log, which carries both halves seconds apart:
`commit-worthy: True — a verdict changed` from `--write`, then `commit-worthy: False` from
`--commit-worthy`, on the same data. The cost was not cosmetic. The committed board read
`gates_green: NO-GATE-VERDICT / unmeasured` from 2026-08-26 onward while CI measured that row
correctly on every tick (`RED-BUT-FRESH`, `0 UNMEASURED`), and research-loop §1 sends every cycle to
that board before it starts. A cycle reading the trunk was told the loop could not see whether `main`
was green; the loop could see it, and had been saying so into a file nobody committed.

⭐ WHY THE FIX IS AT THE CALLER AND NOT A HEURISTIC INSIDE `--commit-worthy`. "Is the board on disk my
own output?" has no safe answer: a genuinely committed board ALSO carries `_commit_worthy: true`,
because that is precisely why it was committed. Trusting the stored flag whenever the surface matched
would commit an unchanged board on every tick — the 1,476-commits-in-24-h defect `commit_worthy()`
exists to prevent. So `--write` records its decision and `--stored-commit-worthy` obeys it.

WHAT THIS FILE GUARDS
  1. The trap is real and still behaves as described — `--commit-worthy` after `--write` on one path
     answers "unchanged" even when a verdict genuinely changed. Asserted so the fix cannot be
     "simplified" back by someone who reads the two flags as synonyms.
  2. `--stored-commit-worthy` returns the decision `--write` recorded.
  3. It still DECLINES an unchanged board, so the no-work-no-commit rule is intact.
  4. The wiring: the tick's publish step uses `--stored-commit-worthy` and not `--commit-worthy`.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PARENT))
HEALTH = os.path.join(PARENT, "health.py")
TICK = os.path.join(REPO, ".github", "workflows", "autonomy-tick.yml")

#: A synthetic verdict, so this test never touches the network. Its only job is to make one row's
#: verdict differ between two runs — which row, and what it says, is irrelevant here.
GREEN = {"ok": True, "red_since_utc": None, "ref": "tests.yml @ deadbeefcafe",
         "checked_utc": "2026-08-28T00:00:00Z", "detail": "synthetic verdict for a wiring test"}


def _run(*args):
    return subprocess.run([sys.executable, HEALTH, *args], cwd=REPO,
                          capture_output=True, text=True)


def _board(tmp_path, gates=None):
    """Write a board to a throwaway path and hand back (path, gates_path)."""
    board_path = tmp_path / "health.json"
    gates_path = tmp_path / "gates.json"
    args = ["--write", "--health", str(board_path)]
    if gates is not None:
        gates_path.write_text(json.dumps(gates), encoding="utf-8")
        args += ["--gates-verdict", str(gates_path)]
    out = _run(*args)
    assert out.returncode == 0, out.stderr
    return board_path, gates_path, out.stdout


def test_the_write_step_records_that_a_verdict_changed(tmp_path):
    """Baseline: a first board, then a board whose `gates_green` verdict differs. The second write
    must SAY a verdict changed — everything below is meaningless if this does not hold."""
    board_path, _, _ = _board(tmp_path)                      # no verdict -> gates_green unmeasured
    gates_path = tmp_path / "gates.json"
    gates_path.write_text(json.dumps(GREEN), encoding="utf-8")
    out = _run("--write", "--health", str(board_path), "--gates-verdict", str(gates_path))
    assert out.returncode == 0, out.stderr
    assert "commit-worthy: True" in out.stdout, out.stdout
    assert json.loads(board_path.read_text(encoding="utf-8"))["_commit_worthy"] is True


def test_commit_worthy_after_a_write_compares_the_board_against_itself(tmp_path):
    """⛔ THE DEFECT ITSELF, PINNED. This is the behaviour that froze the trunk's board, and it is
    asserted rather than fixed because the two flags are NOT synonyms: `--commit-worthy` is correct
    BEFORE a write and wrong after one. If someone ever makes this test fail by making
    `--commit-worthy` safe after a write, read the module docstring before deleting this — the
    obvious way to do that reintroduces the 1,476-commit defect."""
    board_path, gates_path, _ = _board(tmp_path)
    gates_path.write_text(json.dumps(GREEN), encoding="utf-8")
    wrote = _run("--write", "--health", str(board_path), "--gates-verdict", str(gates_path))
    assert "commit-worthy: True" in wrote.stdout, wrote.stdout

    after = _run("--commit-worthy", "--health", str(board_path), "--gates-verdict", str(gates_path))
    assert after.returncode == 10, (
        "the trap is gone or has changed shape; this test's whole subject is that `--commit-worthy` "
        "run after `--write` on the same path answers 'unchanged'. Output: %s" % after.stdout)
    assert "unchanged" in after.stdout


def test_stored_commit_worthy_obeys_the_decision_the_write_recorded(tmp_path):
    """★ THE FIX. Same sequence, same files — and the answer is the one `--write` actually reached."""
    board_path, gates_path, _ = _board(tmp_path)
    gates_path.write_text(json.dumps(GREEN), encoding="utf-8")
    _run("--write", "--health", str(board_path), "--gates-verdict", str(gates_path))

    stored = _run("--stored-commit-worthy", "--health", str(board_path))
    assert stored.returncode == 0, (
        "a verdict changed and --write said so, but the publish gate would still decline to commit "
        "the board. Output: %s" % stored.stdout)
    assert "True" in stored.stdout


def test_stored_commit_worthy_still_declines_an_unchanged_board(tmp_path):
    """⛔ THE NEGATIVE CONTROL, AND IT IS THE HALF THAT MATTERS MOST. A fix that always answered
    'commit' would pass the test above and re-create the 1,476-commits-in-24-h defect."""
    board_path, gates_path, _ = _board(tmp_path)
    gates_path.write_text(json.dumps(GREEN), encoding="utf-8")
    _run("--write", "--health", str(board_path), "--gates-verdict", str(gates_path))
    again = _run("--write", "--health", str(board_path), "--gates-verdict", str(gates_path))
    assert "commit-worthy: False" in again.stdout, again.stdout

    stored = _run("--stored-commit-worthy", "--health", str(board_path))
    assert stored.returncode == 10, (
        "an unchanged board would be committed on every tick. Output: %s" % stored.stdout)


def test_a_board_with_no_recorded_decision_is_declined_not_assumed(tmp_path):
    """An absent reading is not a reading of absence (CLAUDE.md §4). A board file that carries no
    `_commit_worthy` — hand-made, truncated, written by an older version — must not read as 'commit'."""
    board_path = tmp_path / "health.json"
    board_path.write_text(json.dumps({"conditions": []}), encoding="utf-8")
    stored = _run("--stored-commit-worthy", "--health", str(board_path))
    assert stored.returncode == 10, stored.stdout


def test_the_tick_publishes_on_the_recorded_decision_not_a_recomputed_one():
    """The wiring half. A correct flag nobody calls is the `stalls_are_named` defect one file over."""
    src = open(TICK, encoding="utf-8").read()
    publish = src.split("Publish the board", 1)
    assert len(publish) == 2, "the publish step was renamed; this guard is now pointing at nothing"
    step = publish[1]
    # ⛔ COMMENTS ARE STRIPPED BEFORE THE SECOND ASSERTION, AND THAT IS NOT A CONVENIENCE. This step
    # DELIBERATELY quotes `health.py --commit-worthy | tee log && commit` in prose, as the example of
    # a shape that commits unconditionally. A guard reading the raw text matches that sentence and
    # fails on a correctly-wired step — measured on this test's first run. What must be absent is the
    # flag on a line the runner EXECUTES, so only those lines are searched.
    executed = "\n".join(ln for ln in step.splitlines() if not ln.strip().startswith("#"))
    assert "--stored-commit-worthy" in executed, (
        "the publish step no longer asks for the RECORDED decision, so it is recomputing one against "
        "a file the grading step already overwrote — the defect this file documents")
    assert "--commit-worthy" not in executed.replace("--stored-commit-worthy", ""), (
        "the publish step runs `--commit-worthy` after the grading step's `--write`, which compares "
        "the board against itself and freezes the committed board")
