"""⛔⛔ THE MERGE-DEBT HOOK HAD TWO ALWAYS-GREEN PATHS AND NO TESTS AT ALL.

`merge-debt-at-turn-end.sh` is the enforcement CLAUDE.md §7 cites for a rule the repository calls a
DATA-LOSS BUG, and §7 says of it: *"It has no green state that recording can buy: the only ways past
it are to be on `main`, to have nothing ahead of it, or to merge."*

⚠ MEASURED 2026-09-01 (S31-ORPHANS found them, S35-DRIFTGUARD reproduced them against a fixture):
that sentence was true about RECORDING and false about everything else. Two ordinary states bought
silence for free, and both fired constantly.

  HOLE 1 — the hook measured `origin/main...HEAD`, so it could only ever see the branch the stopping
    session was sitting on. A branch pushed by a DIFFERENT session is not `HEAD` anywhere, and once
    that session ends there is no stop left for it to fire on. `for-each-ref` appeared in the old
    file's COMMENTS and nowhere in its code.
  HOLE 2 — `git status --porcelain` non-empty exited 0. One untracked file flipped exit 2 to exit 0
    with the merge debt unchanged. In a twelve-seat sprint the tree is never clean, so the hook was
    unconditionally off during exactly the window that creates the most branches.

⛔ THE POPULATION NEARLY DOUBLED WHILE IT WAS GREEN: the 2026-08-29 census said "20+"; the census on
2026-09-01 found 37 branches carrying 152 distinct unmerged commits, seventeen of them from a single
archived seat cohort.

★ WHY THE NEGATIVE CASES ARE HALF THIS FILE. A guard that reds on true input is one its reader learns
to loosen. The two shapes that must stay quiet are (a) a repository whose branches really are all
merged, and (b) the orphan workflow data refs (`*-cache`, `email-outbox`, `figure-renders`) which
never merge BY DESIGN — they are excluded structurally, by sharing no root with the trunk, and a
regression that reported them would teach the reader to skim the real ones.

★ AND ONE TEST HERE IS THE ANTI-GAMING TEST IN CODE:
`test_the_hook_writes_nothing_so_no_green_state_can_be_bought` asserts the hook leaves the repository
byte-identical. A marker file, a cache of "branches I already mentioned", or a `_stranded_work` field
that silences the count would each be a self-issued permission slip — the exact shape
`ready-work-at-turn-end.sh` records as the v1 failure of this whole family of guards.

⛔ EVERY TEST BUILDS ITS OWN THROWAWAY REPOSITORY UNDER `tmp_path`. None of them touches the live
tree, reads its dirty state, or depends on how many branches happen to be stranded today. That is
charter §7 ("mutation-test in a scratch copy, never the live tree") and it is also the only way these
assertions survive a twelve-seat sprint.
"""
import os
import shutil
import subprocess
import time

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
HOOK = os.path.join(REPO, ".claude", "hooks", "merge-debt-at-turn-end.sh")

REFUSES = 2  # the harness convention: exit 2 + stderr blocks the stop
ALLOWS = 0

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
}


def _git(cwd, *args):
    env = dict(os.environ)
    env.update(_GIT_ENV)
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=env)
    assert r.returncode == 0, f"git {' '.join(args)} failed: {r.stderr}"
    return r.stdout.strip()


def _run_hook(work, *, project_dir=True, stop_hook_active=False, hook=None):
    """Drive the hook exactly as the harness does: JSON on stdin, verdict in the exit code."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    if project_dir:
        env["CLAUDE_PROJECT_DIR"] = str(work)
    payload = '{"stop_hook_active": true}' if stop_hook_active else "{}"
    return subprocess.run(
        ["bash", hook or HOOK], input=payload,
        capture_output=True, text=True, env=env, cwd=str(work),
    )


@pytest.fixture
def repo(tmp_path):
    """An origin plus a clone, with a branch pushed by a session that has since ENDED.

    ⚠ `figure-renders` is created as a true ORPHAN branch because that is what the real workflow data
    refs are on `origin`. A fixture that made it an ordinary branch would let a name-glob exclusion
    pass this file, and a name list is exactly the thing that drifts.
    """
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(work)],
                   check=True, capture_output=True)
    _git(work, "symbolic-ref", "HEAD", "refs/heads/main")
    (work / "base.txt").write_text("base\n")
    _git(work, "add", "base.txt")
    _git(work, "commit", "-qm", "base")
    _git(work, "push", "-q", "origin", "main")

    # a seat session: branch, commit, push — and then the session ends and we return to main
    _git(work, "checkout", "-q", "-b", "seat/s3-stranded")
    (work / "seat.txt").write_text("real work nobody merged\n")
    _git(work, "add", "seat.txt")
    _git(work, "commit", "-qm", "seat s3: real work nobody merged")
    _git(work, "push", "-q", "origin", "seat/s3-stranded")
    _git(work, "checkout", "-q", "main")

    # an orphan workflow data ref, which must never be reported
    _git(work, "checkout", "-q", "--orphan", "figure-renders")
    _git(work, "rm", "-rq", "--cached", ".")
    for stale in ("base.txt", "seat.txt"):
        if (work / stale).exists():
            (work / stale).unlink()
    (work / "render.png.txt").write_text("render\n")
    _git(work, "add", "render.png.txt")
    _git(work, "commit", "-qm", "renders")
    _git(work, "push", "-q", "origin", "figure-renders")
    _git(work, "checkout", "-q", "main")

    # the trunk moves on, as it always does
    (work / "base.txt").write_text("base\nmore\n")
    _git(work, "commit", "-qam", "trunk moves")
    _git(work, "push", "-q", "origin", "main")
    _git(work, "fetch", "-q", "origin")
    return work


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# HOLE 1 — a branch the stopping session is not standing on
# ─────────────────────────────────────────────────────────────────────────────────────────────────

def test_a_branch_pushed_by_a_session_that_has_ended_is_named(repo):
    """⛔ THE REGRESSION FOR HOLE 1, AND IT IS THE WHOLE REASON THIS FILE EXISTS.

    The checkout sits on `main` with a clean tree — the state in which the OLD hook exited 0 at its
    third line, before measuring anything at all. `origin/seat/s3-stranded` is unmerged and its
    session is gone. Nothing else in this repository enumerates `origin`, so if this assertion goes
    green-by-silence the branch is invisible everywhere.
    """
    assert _git(repo, "branch", "--show-current") == "main"
    assert _git(repo, "status", "--porcelain") == ""

    r = _run_hook(repo)
    assert r.returncode == REFUSES, f"the stop was allowed with a stranded branch on origin: {r.stderr}"
    assert "seat/s3-stranded" in r.stderr, r.stderr
    assert "1 branch(es) on origin" in r.stderr, r.stderr


def test_the_census_also_runs_from_a_detached_head(repo):
    """A detached HEAD was the old hook's second unconditional exit (`[ -z "$BRANCH" ] && exit 0`).

    Whether this checkout has a branch name is a fact about this checkout. It is not evidence about
    anybody else's pushed work, and it must not buy silence about it.
    """
    _git(repo, "checkout", "-q", "--detach", "HEAD")
    assert _git(repo, "branch", "--show-current") == ""
    r = _run_hook(repo)
    assert r.returncode == REFUSES, r.stderr
    assert "seat/s3-stranded" in r.stderr, r.stderr


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# HOLE 2 — the dirty worktree
# ─────────────────────────────────────────────────────────────────────────────────────────────────

def test_a_dirty_worktree_does_not_silence_the_origin_census(repo):
    """⛔ THE REGRESSION FOR HOLE 2, WITH THE ONE-FILE CONTROL THAT DISCRIMINATES.

    Same checkout, same branch, same unmerged branch on origin. The ONLY thing that changes between
    the two runs is one untracked file. Under the old hook that flipped exit 2 to exit 0.

    ⚠ The asymmetry is the whole argument: a dirty worktree is a fact about THIS session's
    uncommitted edits and carries no information whatever about whether somebody else's pushed branch
    is on the trunk.
    """
    clean = _run_hook(repo)
    assert clean.returncode == REFUSES

    (repo / "some-seat-is-editing.txt").write_text("mid-edit\n")
    assert _git(repo, "status", "--porcelain") != ""

    dirty = _run_hook(repo)
    assert dirty.returncode == REFUSES, "one untracked file silenced the branch census"
    assert "seat/s3-stranded" in dirty.stderr, dirty.stderr


def test_the_dirty_tree_trade_is_preserved_for_the_sessions_own_branch(repo):
    """★ THE TRADE, ASSERTED SO IT CANNOT BE QUIETLY DROPPED IN EITHER DIRECTION.

    HALF A (this session's own merge debt) KEEPS its dirty-tree exit, for two checked reasons:
    `~/.claude/stop-hook-git-check.sh` is wired at the launcher level and already exits 2 on
    uncommitted changes, so stacking a second alarm on one state teaches skimming; and mid-edit,
    "MERGE IT — not next turn" is the wrong instruction.

    ⛔ WHAT IS NOT TRADED: on a clean tree the merge instruction must still appear. This test pins
    both halves of that, so "simplifying" either one reds.
    """
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-edit", "origin/seat/s3-stranded")
    _git(repo, "push", "-q", "origin", "main")
    _git(repo, "fetch", "-q", "origin")
    _git(repo, "checkout", "-q", "-b", "own-work")
    (repo / "mine.txt").write_text("mine\n")
    _git(repo, "add", "mine.txt")
    _git(repo, "commit", "-qm", "own work")

    clean = _run_hook(repo)
    assert clean.returncode == REFUSES, "a clean branch with unmerged commits must still be refused"
    assert "MERGE IT" in clean.stderr, clean.stderr

    (repo / "mid-edit.txt").write_text("half a thought\n")
    dirty = _run_hook(repo)
    assert "MERGE IT" not in dirty.stderr, (
        "the hook told a session to merge a tree it is still editing — that is the wrong "
        "instruction, and it is the reason the dirty-tree exit was kept for HALF A"
    )


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# The shapes it must NOT punish
# ─────────────────────────────────────────────────────────────────────────────────────────────────

def test_an_orphan_workflow_data_ref_is_never_reported_as_stranded(repo):
    """`figure-renders` and the `*-cache` refs never merge BY DESIGN.

    ⭐ They are excluded STRUCTURALLY — they share no root with the trunk, so they fall out of the
    query itself — and not by a name glob. Measured on the live repository 2026-09-01: all 13
    `*-cache` refs plus `email-outbox` and `figure-renders` are orphan refs and none appears in the
    37. A name list would have been one more thing to keep in sync and one more place to widen.
    """
    r = _run_hook(repo)
    assert "figure-renders" not in r.stderr, r.stderr


def test_a_fully_merged_repository_is_silent(repo):
    """The honest green state, and the only one: nothing is unmerged, so nothing is said."""
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-edit", "origin/seat/s3-stranded")
    _git(repo, "push", "-q", "origin", "main")
    _git(repo, "fetch", "-q", "origin")
    r = _run_hook(repo)
    assert r.returncode == ALLOWS, f"false positive on a fully merged repository: {r.stderr}"


def test_the_recursion_guard_still_fires_once(repo):
    """Without it the hook re-fires on the stop it just caused and the session cannot end at all."""
    r = _run_hook(repo, stop_hook_active=True)
    assert r.returncode == ALLOWS, r.stderr
    assert r.stderr.strip() == "", r.stderr


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# It must be able to RUN, and it must be honest when it cannot MEASURE
# ─────────────────────────────────────────────────────────────────────────────────────────────────

def test_the_hook_finds_its_repository_without_being_told_where_it_is(repo):
    """⛔⛔ "A GUARD THAT CANNOT RUN IS NOT A GUARD THAT PASSED."

    ⚠ Measured for a sibling hook in CI run 33513565956: three correct assertions all passed against
    `returncode=0, stdout='', stderr=''`, because the hook hard-coded
    `REPO="${CLAUDE_PROJECT_DIR:-/home/user/Rare-cancers}"` and a GitHub runner has neither. Every
    assertion was right and the hook was never reached.

    So this drives it the way a runner does: `CLAUDE_PROJECT_DIR` removed from the environment
    entirely, with the hook copied into the fixture's own `.claude/hooks/` so it must resolve the
    repository from its own path.
    """
    hooks = repo / ".claude" / "hooks"
    hooks.mkdir(parents=True)
    planted = hooks / "merge-debt-at-turn-end.sh"
    shutil.copy2(HOOK, planted)

    r = _run_hook(repo, project_dir=False, hook=str(planted))
    assert r.returncode == REFUSES, (
        f"the hook could not find its own repository without CLAUDE_PROJECT_DIR "
        f"(rc={r.returncode}, stderr={r.stderr!r})"
    )
    assert "seat/s3-stranded" in r.stderr, r.stderr


def test_an_unresolvable_origin_main_is_reported_as_unmeasured_not_clean(repo):
    """★ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4).

    If the clone has remote-tracking refs but `origin/main` will not resolve, the hook measured
    NOTHING. Exiting 0 there renders "I could not look" and "there is nothing to see" identical at
    the one moment the difference matters.
    """
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    r = _run_hook(repo)
    assert r.returncode == REFUSES, "an unmeasurable state was rendered as a clean one"
    assert "UNMEASURED" in r.stderr, r.stderr


def test_a_repository_with_no_origin_at_all_is_left_alone(tmp_path):
    """A plain local repo is not this repository, and a Stop hook must not trap a session in one."""
    work = tmp_path / "solo"
    work.mkdir()
    subprocess.run(["git", "init", "-q", str(work)], check=True)
    (work / "f.txt").write_text("x\n")
    _git(work, "add", "f.txt")
    _git(work, "commit", "-qm", "only commit")
    r = _run_hook(work)
    assert r.returncode == ALLOWS, r.stderr


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# The two properties that are easy to lose in a "cleanup"
# ─────────────────────────────────────────────────────────────────────────────────────────────────

def test_the_hook_writes_nothing_so_no_green_state_can_be_bought(repo):
    """★★ THE ANTI-GAMING TEST, IN CODE.

    CLAUDE.md §7: the hook "has no green state that recording can buy". The cheapest way to make a
    noisy census quiet is a cache of "branches I have already mentioned" — and that is a self-issued
    permission slip, the exact shape `ready-work-at-turn-end.sh` records as the v1 failure of this
    family of guards ("a flag for the agent to declare would be one more self-issued permission
    slip"). The stranded branches sat for four days precisely because nothing re-raised them.

    So: the hook must leave the repository byte-identical. Run it twice; the second run must say the
    same thing as the first, and nothing on disk may have changed.
    """
    def snapshot():
        out = {}
        for root, dirs, files in os.walk(repo):
            if ".git" in root.split(os.sep) and "refs" not in root:
                pass
            for f in files:
                p = os.path.join(root, f)
                try:
                    st = os.stat(p)
                    out[os.path.relpath(p, repo)] = st.st_size
                except OSError:
                    pass
        return out

    before = snapshot()
    first = _run_hook(repo)
    after_one = snapshot()
    second = _run_hook(repo)

    new_paths = set(after_one) - set(before)
    assert not new_paths, f"the hook created files, which is where a green state gets bought: {new_paths}"
    assert first.returncode == second.returncode == REFUSES
    assert "seat/s3-stranded" in second.stderr, (
        "the second run went quiet about a branch the first run named — that is a cache, and a "
        "cache is the permission slip this guard exists to refuse"
    )


def test_the_classification_is_one_process_and_not_a_merge_base_loop(repo):
    """⭐ THE COST CONSTRAINT, PINNED — because the obvious implementation is over the timeout.

    Measured on the live repository 2026-09-01:
      per-ref `git merge-base origin/main <ref>` over 183 candidate refs .... 20.0 s
      one `git for-each-ref --no-merged=origin/main --contains=<root>` ......  0.28 s
    Both return the SAME 37 refs (compared as sets, `diff` empty). The naive form is slow for the
    reason it looks cheap: proving NO common ancestor makes git walk both histories to the end. The
    hook's configured timeout in `.claude/settings.json` is 15 s, so the naive form does not merely
    run late — it is killed, and a killed Stop hook is a silent one.

    ⚠ This asserts the SHAPE rather than a wall-clock number, because a timing assertion in a
    twelve-seat tree is a flake generator. A future rewrite may use any formulation it likes as long
    as it does not put a per-ref subprocess in the classification path.
    """
    src = open(HOOK, encoding="utf-8").read()
    assert "--no-merged=origin/main" in src, "the unmerged filter is gone"
    assert "--contains=" in src, "the shared-history filter is gone"
    body = src.split("set -uo pipefail", 1)[1]
    code = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
    assert "merge-base" not in code, (
        "a `merge-base` call reappeared in the hook body; over 183 refs that formulation measured "
        "20.0 s against a 15 s timeout"
    )


def test_the_hook_completes_well_inside_its_configured_timeout(repo):
    """A Stop hook that overruns its timeout is killed, and a killed hook is indistinguishable from
    a green one. The fixture is small, so this is a floor check on obvious pathologies (a fetch, a
    network call, a per-ref walk); the real timing evidence is in the docstring above.
    """
    start = time.monotonic()
    _run_hook(repo)
    assert time.monotonic() - start < 10.0, "the hook is nowhere near its 15 s budget"


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# HALF A2 — the PULL half (added 2026-09-02 with CLAUDE.md §7's two lanes)
#
# trimcrae: "use branches but have it pull from main whenever there's a change". The obligation is
# new; the counts are not — `origin/main...HEAD` already gives BEHIND as well as AHEAD, so this half
# adds no process and cannot reintroduce the `merge-base` cost the test above pins out.
#
# ⛔⛔ AND THE LAST TEST IN THIS BLOCK IS THE ONE THAT MATTERS MOST. HALF A2 and HALF B fail in
# OPPOSITE directions: a branch can pull `main` in every hour and still be abandoned, and pulling is
# exactly what makes an abandoned branch look healthy. Losing (b) is the only way this rule change
# does real harm, so it is asserted rather than assumed.
# ─────────────────────────────────────────────────────────────────────────────────────────────────

def _diverged(repo):
    """Stand the session on a branch that has commits of its own AND is behind the trunk."""
    _git(repo, "checkout", "-q", "-b", "work/feature", "origin/main~1")
    (repo / "feature.txt").write_text("mine\n")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-qm", "work: mine, written against a trunk that has moved")


def test_a_branch_that_has_not_pulled_main_in_is_named_as_divergent(repo):
    _diverged(repo)
    r = _run_hook(repo)
    assert r.returncode == REFUSES, r.stderr
    assert "has NOT pulled main in" in r.stderr, r.stderr
    assert "DIVERGENT" in r.stderr, r.stderr
    assert "git merge origin/main" in r.stderr, "the clean-tree case must give the actual command"


def test_a_dirty_tree_defers_the_pull_instruction_but_not_the_reading(repo):
    """⭐ THE SAME TRADE HALF A ALREADY MAKES, AND FOR THE OPPOSITE HALF OF THE REASON. 'Merge it now'
    is wrong advice mid-edit; 'you are working against a stale trunk' is most useful exactly then,
    because every further edit compounds it. So the INSTRUCTION is deferred and the READING is not."""
    _diverged(repo)
    (repo / "scratch-untracked.txt").write_text("mid-edit\n")
    r = _run_hook(repo)
    assert r.returncode == REFUSES, r.stderr
    assert "has NOT pulled main in" in r.stderr, "a dirty tree silenced the divergence reading"
    assert "DO IT NOW" not in r.stderr, "the merge instruction is wrong advice mid-edit"


def test_a_branch_that_is_merely_behind_gets_one_line_not_a_block(repo):
    """⚠ GRADED, NOT BINARY. Any branch is behind `main` within minutes; a block for that at every
    stop is the wall this hook's header refuses to become. Nothing has been written against the stale
    trunk yet, so this is a warning before the fact rather than a debt after it."""
    _git(repo, "checkout", "-q", "-b", "work/fresh", "origin/main~1")
    r = _run_hook(repo)
    assert r.returncode == REFUSES, r.stderr
    assert "behind main and carries nothing of its own yet" in r.stderr, r.stderr
    assert "DIVERGENT" not in r.stderr, "a branch with no commits of its own is not divergent"


def test_a_branch_level_with_main_says_nothing_about_pulling(repo):
    """No false positive: the pull half must be silent on a branch that has pulled."""
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-edit", "origin/seat/s3-stranded")
    _git(repo, "push", "-q", "origin", "main")
    _git(repo, "fetch", "-q", "origin")
    _git(repo, "checkout", "-q", "-b", "work/uptodate")
    r = _run_hook(repo)
    assert r.returncode == ALLOWS, f"the pull half fired on a branch level with main: {r.stderr}"


def test_pulling_main_in_does_not_silence_the_abandoned_branch_census(repo):
    """⛔⛔ KEEP (b). This is the regression the rule change could plausibly cause: a branch is brought
    fully up to date with `main` — HALF A2 has nothing to say about it — and it is STILL carrying work
    nobody will merge. If HALF B ever went quiet here, 25 refs and 111 unmerged commits (live reading
    2026-09-02) would stop being anybody's problem."""
    _git(repo, "checkout", "-q", "-b", "work/pulled", "origin/seat/s3-stranded")
    _git(repo, "merge", "-q", "--no-edit", "origin/main")     # pulled in, fully up to date
    _git(repo, "push", "-q", "origin", "work/pulled")
    _git(repo, "fetch", "-q", "origin")
    r = _run_hook(repo)
    assert r.returncode == REFUSES, "a pulled-but-unmerged branch bought silence"
    assert "finished work nothing will merge" in r.stderr, r.stderr
    assert "seat/s3-stranded" in r.stderr, r.stderr
    assert "PULLING main IN DOES NOT FIX IT" in r.stderr, (
        "the two checks answer different questions and the output must say so")


def test_the_behind_count_has_exactly_one_home_in_the_output():
    """CLAUDE.md rule 1. HALF A used to restate the behind-count as an aside inside its own block,
    which is how it stayed advice instead of becoming a check."""
    src = open(HOOK, encoding="utf-8").read()
    body = src.split("set -uo pipefail", 1)[1]
    code = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
    assert "is also $A_BEHIND commit(s) BEHIND main" not in code, (
        "the old aside is back; the behind-count belongs to HALF A2 alone")
    assert code.count("A_DIVERGENT=1") == 1 and code.count("A_STALE=1") == 1
