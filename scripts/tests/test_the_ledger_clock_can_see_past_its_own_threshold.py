"""`dev-setup.sh` must deepen a shallow clone until the ledger's git-history clocks can see past it.

⛔⛔ THE DEFECT THIS ASSERTS AGAINST, MEASURED 2026-08-28 (AUT-PD-058). Every sandbox is handed a
SHALLOW clone. `stuck_clock.py` walks `git log --follow` over the ledger, so a row already present in
the oldest visible version is a right-censored LOWER BOUND — correct, and useless while that bound
sits below the clock's own 24 h threshold. In this sandbox the horizon was 3.2 h and 142 of 161 rows
were censored, so ZERO rows were terminal; the same ledger in a full clone gave three (AUT-010,
AUT-049, AUT-PROP-019). Two more modules read the same history with their own memories:
`learning_rate.py` (16 h) and `out_of_ideas.py` (336 h).

⛔ IT IS NOT COSMETIC. `handoff.py::terminal_ids()` reads the clock LIVE and fails OPEN, so a censored
verdict excludes nothing: the shallow run handed AUT-010 — the top-scoring row at 190.9 — to the
successor as ready work, while the full clone printed `⛔ EXCLUDED as stalled_needs_human` for exactly
those three.

⚠ CI WAS NEVER AFFECTED AND MUST NOT BE "FIXED" HERE. `autonomy-tick.yml` checks out at
`fetch-depth: 0`; its 18:45 UTC run that day published `STALLED-ROWS` naming real rows with
`0 UNMEASURED`. The censoring is a SESSION-path defect, which is why the repair lives in the session
setup script and why this guard is pointed at that script.

★ WHY MOST OF THIS IS A TEXT CHECK, AND WHERE IT IS NOT. Placement, the fail-open call site and the
"read every window, never type one" property are structural: visible in the source and invisible at
runtime on a healthy box. The guard's actual DECISION is not — so the last three tests build real
repositories, clone one shallow over `file://` (no network), and assert the function fires when it
must, moves the horizon when it fires, and stays silent when it must not.

⚠ WHAT THIS DOES NOT CATCH, stated here rather than discovered later:
  * whether the SessionStart hook still runs `dev-setup.sh`. That binding lives in
    `.claude/settings.json`, asserted by `systems/tests/test_hook_paths_are_cwd_independent.py`.
  * whether `--shallow-since` reaches back far enough on a ledger older than the fetched window. It
    is derived from the readers' own windows, so it tracks them; too short still leaves honest
    censored bounds rather than a wrong number, which is the direction that does not invent a finding.
  * a FOURTH reader of the history added later with a longer memory than these three. It needs its
    own line in `_ledger_history_need_hours` and its own assertion here — this is a one-of-a-set
    guard and it binds only to the set it names.
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUTONOMY = os.path.join(ROOT, "research", "autonomy")
DEV_SETUP = os.path.join(ROOT, "scripts", "dev-setup.sh")
STUCK_CLOCK = os.path.join(AUTONOMY, "stuck_clock.py")
FUNC = "_deepen_ledger_history"
NEED = "_ledger_history_need_hours"
EARLY_EXIT = 'if [ "${1:-}" = "--if-needed" ]; then'
# Every module `_ledger_history_need_hours` must consult, with the call that yields its window.
READERS = {
    "stuck_clock": "stuck_clock.stuck_threshold_hours()",
    "learning_rate": "learning_rate.window_hours()",
    "out_of_ideas": "out_of_ideas.budget_days()",
}


def _source(path=None):
    with open(path or DEV_SETUP, encoding="utf-8") as fh:
        return fh.read()


def _body(name, src=None):
    """The text of one shell function, from its `() {` to the closing brace in column 0."""
    src = src if src is not None else _source()
    start = src.index(f"{name}() {{")
    return src[start:src.index("\n}\n", start) + len("\n}\n")]


def _runnable(src=None):
    """Both functions plus the margin, as a standalone script the tests can execute."""
    src = src if src is not None else _source()
    margin = re.search(r"^LEDGER_HISTORY_MARGIN=(\d+)", src, re.M)
    assert margin, "LEDGER_HISTORY_MARGIN is gone; the window is no longer derived from the readers"
    return ("set -euo pipefail\n" + f"LEDGER_HISTORY_MARGIN={margin.group(1)}\n"
            + _body(NEED, src) + "\n" + _body(FUNC, src) + f"\n{FUNC}\n")


def _fixture_repo(tmp, ledger_rows, commit_stamp=None):
    """A repo carrying the real autonomy modules, so the readers' windows are the REAL ones."""
    repo = os.path.join(tmp, "src")
    os.makedirs(os.path.join(repo, "research", "autonomy"))
    subprocess.run(["git", "init", "--quiet", "-b", "main", repo], check=True, capture_output=True)
    for name in ("stuck_clock.py", "learning_rate.py", "out_of_ideas.py", "autonomy-state.json",
                 "priority-weights.json"):
        shutil.copy(os.path.join(AUTONOMY, name), os.path.join(repo, "research", "autonomy", name))
    with open(os.path.join(repo, "research", "autonomy", "research-ledger.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"entries": ledger_rows}, fh)
    return repo


def _git_env(**extra):
    return dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t",
                GIT_COMMITTER_EMAIL="t@x", **extra)


def _commit(repo, stamp):
    subprocess.run(["git", "-C", repo, "add", "-A"], check=True, capture_output=True,
                   env=_git_env())
    subprocess.run(["git", "-C", repo, "commit", "--quiet", "-m", f"at {stamp}"], check=True,
                   capture_output=True,
                   env=_git_env(GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp))


def _horizon_age_hours(repo):
    out = subprocess.run(["git", "-C", repo, "log", "--format=%ct", "--follow", "--",
                          "research/autonomy/research-ledger.json"],
                         check=True, capture_output=True, text=True, env=_git_env()).stdout
    return (int(time.time()) - int(out.strip().splitlines()[-1])) / 3600.0


def _need_hours(repo):
    """What `_ledger_history_need_hours` itself answers in this repo — never a number typed here.

    ⚠ THE FIXTURES ARE SIZED FROM IT, and that is not tidiness. The first cut put the old commit
    800 h back while the fetched window was 672 h, so the commit sat OUTSIDE the window the deepen
    asks for and the test failed against a correct implementation. A fixture built on a typed
    constant breaks the day a tuning weight moves.
    """
    script = os.path.join(repo, "..", "need.sh")
    with open(script, "w", encoding="utf-8") as fh:
        fh.write("set -euo pipefail\n" + _body(NEED) + f"\n{NEED}\n")
    out = subprocess.run(["bash", script], cwd=repo, capture_output=True, text=True,
                         env=_git_env())
    assert out.returncode == 0 and out.stdout.strip().isdigit(), (
        f"`{NEED}` did not answer a number in the fixture: {out.stdout!r} {out.stderr!r}"
    )
    return int(out.stdout.strip())


def _run_deepen(tmp, cwd):
    script = os.path.join(tmp, "fn.sh")
    with open(script, "w", encoding="utf-8") as fh:
        fh.write(_runnable())
    return subprocess.run(["bash", script], cwd=cwd, capture_output=True, text=True,
                          env=_git_env())


# ------------------------------------------------------------------------------------------------
# Structural: the properties that are invisible at runtime on a healthy box.
# ------------------------------------------------------------------------------------------------


def test_the_deepen_step_exists_at_all():
    """A guard whose subject has been deleted asserts nothing; say so instead of passing."""
    src = _source()
    assert f"{FUNC}() {{" in src, (
        f"{FUNC} is gone from dev-setup.sh. If the deepen moved, re-point this whole file at "
        f"wherever it went — deleting the guard leaves the session clocks censored and silent again."
    )
    # ⚠ ASSERTED AGAINST THE FUNCTION BODY, NOT THE FILE. The first cut looked for the flag anywhere
    # in dev-setup.sh and the surrounding comment block satisfied it, so swapping the real fetch for
    # `--unshallow` left this green. Prose about a fix is not the fix (found by mutation M6).
    assert "--shallow-since" in _body(FUNC, src), (
        "the deepen no longer uses `git fetch --shallow-since`. `--unshallow` also works and was "
        "measured at ~90x the bytes for an identical verdict; if it was swapped deliberately, "
        "record the measurement in dev-setup.sh and update this assertion."
    )


def test_the_deepen_runs_above_the_if_needed_early_exit():
    """⛔ THE ONE THIS FILE HAS ALREADY PAID FOR, ONE LAYER UP.

    The ghostscript step was first written BELOW the `--if-needed` early exit, so on a sandbox whose
    interpreters were already complete the probe printed "nothing to do" and the step never ran. The
    deepen has the same shape — the import probe knows nothing about git history — so it must sit
    above the exit and carry its own guard.
    """
    src = _source()
    assert src.count(EARLY_EXIT) == 1, "the --if-needed early exit moved or was duplicated"
    assert src.index(f"{FUNC}() {{") < src.index(EARLY_EXIT), (
        "the deepen function is DEFINED below the --if-needed early exit — on any sandbox whose "
        "interpreters already import everything it will never run, which is exactly how the "
        "ghostscript step failed."
    )
    call_at = src.index(f"\n{FUNC} ", src.index(f"{FUNC}() {{"))
    assert call_at < src.index(EARLY_EXIT), (
        "the deepen is DEFINED above the early exit but never CALLED above it. A defined-and-"
        "uncalled function is the unrun-ranker defect this repository has already paid for."
    )


def test_the_deepen_cannot_fail_the_session_hook():
    """A SessionStart hook that dies on a refused fetch costs a session; a censored clock costs a row.

    `dev-setup.sh` runs under `set -euo pipefail`, so every rung has to swallow its own failure: no
    network, a sibling seat holding `shallow.lock`, or a fork without `main` must all leave the
    clocks reporting honest lower bounds rather than aborting setup.
    """
    src = _source()
    call_at = src.index(f"\n{FUNC} ", src.index(f"{FUNC}() {{"))
    assert "|| true" in src[call_at:call_at + 80], (
        f"the call site `{FUNC}` is not guarded with `|| true` under `set -e`."
    )
    fetch_lines = [ln for ln in _body(FUNC, src).splitlines() if "--shallow-since" in ln]
    assert fetch_lines, "no fetch line found inside the deepen function"
    assert any("if git fetch" in ln or "||" in ln for ln in fetch_lines), (
        "the deepen's `git fetch` is not in a branch or `||` guard, so a refused fetch aborts "
        "dev-setup.sh under `set -e` and the SessionStart hook reports a failure instead of a "
        "shorter history."
    )


def test_every_window_is_read_from_its_own_home_and_none_is_typed():
    """⛔ CLAUDE.md §1, and the reason the margin could be dropped from 14 to 2.

    Three modules read this history and the clone must satisfy the LONGEST. Sizing off stuck_clock's
    threshold alone put the window at exactly `out_of_ideas`' budget — the longest-memory reader
    left sitting on the horizon's edge. Each window has one home; this asserts all three are read.
    """
    need = _body(NEED)
    for module, call in READERS.items():
        assert call in need, (
            f"`{NEED}` no longer reads {module}'s window via `{call}`. If that reader was removed, "
            f"remove it from READERS here too; if it was renamed, follow it. A typed number is a "
            f"second home for a fact that already has one and it drifts on the next tuning change."
        )
    deepen = _body(FUNC)
    assert f"{NEED}" in deepen, f"the deepen no longer calls `{NEED}` — the window is not derived"
    assert [ln for ln in deepen.splitlines() if "age_h" in ln and "need_h" in ln], (
        "the deepen no longer compares the visible horizon against the readers' window"
    )


def test_stuck_clock_points_at_the_script_that_actually_fixes_it():
    """The printed remedy is the only instruction most readers will ever see. It must be the cheap one."""
    src = _source(STUCK_CLOCK)
    printed = src[src.index('if report["shallow"]:'):]
    printed = printed[:printed.index("header =")]
    assert "dev-setup.sh" in printed, (
        "stuck_clock's shallow-clone note no longer names scripts/dev-setup.sh — a reader following "
        "it will reach for `git fetch --unshallow`, which is ~90x the bytes for the same verdict."
    )


# ------------------------------------------------------------------------------------------------
# Behavioural, offline. `file://` is a real git transport, so `--depth` and `--shallow-since` behave
# exactly as they do against origin; a plain path clone (hardlinks) would silently ignore them.
# ------------------------------------------------------------------------------------------------


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required to build the fixture")
def test_a_shallow_clone_is_actually_deepened_past_the_readers_window():
    with tempfile.TemporaryDirectory() as tmp:
        src_repo = _fixture_repo(tmp, [{"id": "OLD-1", "state": "queued", "score": 1}])
        now = int(time.time())
        need = _need_hours(src_repo)
        old_h = int(need * 1.2)          # past every reader's window, inside the fetched one
        _commit(src_repo, f"{now - old_h * 3600} +0000")
        with open(os.path.join(src_repo, "research", "autonomy", "research-ledger.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"entries": [{"id": "OLD-1", "state": "queued", "score": 1},
                                   {"id": "NEW-1", "state": "queued", "score": 1}]}, fh)
        _commit(src_repo, f"{now - 1 * 3600} +0000")       # 1 h back: inside it, the defect

        dest = os.path.join(tmp, "dest")
        subprocess.run(["git", "clone", "--quiet", "--depth", "1", f"file://{src_repo}", dest],
                       check=True, capture_output=True, env=_git_env())
        assert subprocess.run(["git", "-C", dest, "rev-parse", "--is-shallow-repository"],
                              capture_output=True, text=True).stdout.strip() == "true"

        before = _horizon_age_hours(dest)
        assert before < 24, f"fixture is wrong: the shallow horizon is already {before:.1f} h deep"
        run = _run_deepen(tmp, dest)
        assert run.returncode == 0, f"the deepen exited {run.returncode}: {run.stderr}"
        after = _horizon_age_hours(dest)
        assert after > need, (
            f"the deepen did not move the horizon past the readers' {need} h window: {before:.1f} h "
            f"-> {after:.1f} h. stdout={run.stdout!r} stderr={run.stderr!r}"
        )
        assert "deepening" in run.stdout, (
            f"the horizon moved but the step said nothing: {run.stdout!r}. A silent repair is one "
            f"nobody can tell ran."
        )


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required to build the fixture")
def test_a_clone_that_already_reaches_far_enough_is_left_alone():
    """A step that re-fetches when the bound is already conclusive is one someone deletes for noise."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _fixture_repo(tmp, [])
        _commit(repo, f"{int(time.time()) - int(_need_hours(repo) * 1.2) * 3600} +0000")
        run = _run_deepen(tmp, repo)
        assert run.returncode == 0, run.stderr
        assert "deepening" not in run.stdout, (
            f"a repository whose history already outruns every reader's window was deepened anyway. "
            f"stdout={run.stdout!r}"
        )


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required to build the fixture")
def test_a_full_clone_is_never_deepened_however_short_its_history():
    """⛔ THE `--is-shallow-repository` GUARD, WHICH THE AGE GUARD ALONE DOES NOT COVER.

    Added because mutation M4 — deleting the shallow check outright — SURVIVED the first version of
    this file: the sibling fixture's history was already older than the window, so the age guard
    short-circuited and the shallow guard was never doing the work. A repository whose ENTIRE history
    is younger than the window is the case that separates them, and CI is exactly that case whenever
    the ledger is young: `fetch-depth: 0` with nothing older to fetch. A deepen there is a network
    round trip that can buy nothing, every run, forever.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = _fixture_repo(tmp, [])
        _commit(repo, f"{int(time.time())} +0000")         # NOW: the age guard would happily fire
        assert subprocess.run(["git", "-C", repo, "rev-parse", "--is-shallow-repository"],
                              capture_output=True, text=True).stdout.strip() == "false"
        run = _run_deepen(tmp, repo)
        assert run.returncode == 0, run.stderr
        assert "deepening" not in run.stdout and "did not succeed" not in run.stdout, (
            f"a NON-shallow repository with a young history was deepened anyway — the "
            f"`--is-shallow-repository` guard is not binding. stdout={run.stdout!r}"
        )
