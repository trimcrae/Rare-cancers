#!/usr/bin/env python3
"""A REJECTED PUSH MEANS "I LOST THE LEASE", NOT "RETRY HARDER" (AUT-PROP-030).

⭐⭐ THE FINDING, AND IT IS NOT OURS. **A lease is a lock with an expiry: it solves liveness and it
cannot solve safety.** Expiry happens on the lease service's clock, not inside the holder's
execution, so a holder suspended past its own expiry still believes it holds the lease and no amount
of clock-checking closes the gap (Kleppmann's GC-pause argument). **Mutual exclusion is enforced at
the RESOURCE or not at all** — Chubby's *sequencer* (Burrows, OSDI 2006) makes the file server
validate a lock generation number. ⭐ Our resource already implements it: a git ref update IS a
compare-and-swap and the commit SHA is an unforgeable fencing token the remote already checks.

⛔⛔ AND NINE OF THE THIRTEEN CASES BELOW DRIVE A REAL GIT REPOSITORY — 18 tests once the classifier
table expands — BECAUSE THAT IS THE ONLY LEVEL AT WHICH THIS MODULE'S DEFECTS HAVE EVER BEEN
VISIBLE. Three for three:

  AUT-PD-029  `push origin main` pushed a LOCAL BRANCH BY NAME — nine tests, eight mutations and one
              successful first use, all in the single configuration that hid it (the author's branch
              happened to be called `main`).
  AUT-PD-033  the retry loop re-fetched without merging, so HEAD never moved and every attempt failed
              identically — found by USING the tool, not by testing it.
  AUT-PROP-030 (this file) the withdrawal unstaged the claim and LEFT IT IN THE WORKING TREE, so
              `git merge origin/main` refused outright and the loop reported a conflict that did not
              exist.

Every one was invisible to a suite driving a `FakeGit`. **A fake that never fails the way production
fails tests the code against itself.** So these build a bare repository in `tmp_path` and race two
real workers on it — never this repository's remote, which is what the sibling file's rule protects.

⚠ THE OTHER FOUR ARE NOT REAL-GIT AND EACH SAYS WHY IN ITS OWN DOCSTRING, BECAUSE THE MECHANISM THEY
GUARD IS NOT REACHABLE FROM A REAL RUN IN THIS SANDBOX: the push classifier is fed git's stderr
strings directly (a real remote here cannot be made to emit an authentication failure or a
pre-receive refusal on demand), and the locale pin is asserted on the environment dict handed to the
subprocess — a real run cannot see it, which was MEASURED, not assumed: dropping the pin passed all
thirty tests because this container carries only `C`, `C.utf8` and `POSIX` and no `git.mo`.

★ THE WORKERS HERE ARE ON A BRANCH NAMED `claude/worker-*`, NEVER `main`. That is deliberate and it
is AUT-PD-029's regression: a suite that only ever runs on `main` cannot see a refspec that pushes
the local branch by name.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import claim as C  # noqa: E402

ME = "CYC-0030-6be7fd5a"
THEM = "other-seat"
WHEN = "2026-08-28T01:00:00Z"


# =================================================================================================
# The real-git harness. Nothing here reaches the network: `origin` is a bare repo on disk.
# =================================================================================================

def _git(*args, cwd, check=True):
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {cwd}:\n{proc.stdout}\n{proc.stderr}")
    return proc


def _identify(repo, name):
    """⚠ A sandbox may have no global git identity and may have signing on. Pin both locally, or
    the harness fails for a reason that has nothing to do with what is under test."""
    for key, value in (("user.email", f"{name}@example.invalid"), ("user.name", name),
                       ("commit.gpgsign", "false"), ("core.hooksPath", "/dev/null")):
        _git("config", key, value, cwd=repo)
    # The production repository ignores the runner's shared runtime cache. Give
    # these minimal clones the same local exclusion so _clean still detects
    # unintended claim edits, while the shared OS lock can remain on disk.
    with open(os.path.join(repo, ".git", "info", "exclude"), "a", encoding="utf-8") as fh:
        fh.write("\n/.cache/research-runs/\n")


def _ledger_bytes(rows):
    return json.dumps({"entries": [{"id": i, "owner": o, "claimed_utc": None, "state": "queued"}
                                   for i, o in rows]}, indent=2) + "\n"


class World:
    """A bare `origin` plus as many real working clones as a test asks for."""

    def __init__(self, tmp_path, rows):
        self.root = tmp_path
        self.bare = os.path.join(tmp_path, "origin.git")
        _git("init", "-q", "--bare", "-b", "main", self.bare, cwd=tmp_path)
        seed = os.path.join(tmp_path, "seed")
        os.makedirs(seed)
        _git("init", "-q", "-b", "main", seed, cwd=tmp_path)
        _identify(seed, "seed")
        os.makedirs(os.path.join(seed, os.path.dirname(C.LEDGER_REL)), exist_ok=True)
        self._write(seed, _ledger_bytes(rows))
        _git("add", "-A", cwd=seed)
        _git("commit", "-qm", "seed", cwd=seed)
        _git("remote", "add", "origin", self.bare, cwd=seed)
        _git("push", "-q", "origin", "HEAD:main", cwd=seed)

    @staticmethod
    def _write(repo, text):
        with open(os.path.join(repo, C.LEDGER_REL), "w", encoding="utf-8") as fh:
            fh.write(text)

    def worker(self, name):
        """A clone on a branch that is NOT named `main` — AUT-PD-029's regression condition."""
        path = os.path.join(self.root, name)
        _git("clone", "-q", self.bare, path, cwd=self.root)
        _identify(path, name)
        _git("checkout", "-qb", f"claude/{name}", cwd=path)
        return path

    def ledger_path(self, repo):
        return os.path.join(repo, C.LEDGER_REL)

    def owners_on_trunk(self, repo):
        blob = _git("show", f"origin/main:{C.LEDGER_REL}", cwd=repo).stdout
        return {e["id"]: e["owner"] for e in json.loads(blob)["entries"]}

    def push_a_claim(self, name, entry_id, owner):
        """A second REAL worker takes a row and pushes it, exactly as the first one would."""
        repo = self.worker(name)
        path = self.ledger_path(repo)
        C.apply_claim(path, entry_id, owner, "2026-08-28T00:59:00Z")
        _git("add", C.LEDGER_REL, cwd=repo)
        _git("commit", "-qm", f"claim {entry_id} for {owner}", cwd=repo)
        _git("push", "-q", "origin", "HEAD:main", cwd=repo)
        return repo

    def push_an_unrelated_commit(self, name, filename="ci-tick.txt"):
        repo = self.worker(name)
        with open(os.path.join(repo, filename), "w", encoding="utf-8") as fh:
            fh.write("tick\n")
        _git("add", "-A", cwd=repo)
        _git("commit", "-qm", "ci tick", cwd=repo)
        _git("push", "-q", "origin", "HEAD:main", cwd=repo)
        return repo


@pytest.fixture
def world(tmp_path):
    return World(str(tmp_path), [("AUT-X", None), ("AUT-Y", None)])


def _clean(repo):
    return _git("status", "--porcelain", cwd=repo).stdout.strip()


def _trunk_is_merged(repo):
    return _git("merge-base", "--is-ancestor", "origin/main", "HEAD",
                cwd=repo, check=False).returncode == 0


# =================================================================================================
# ⛔⛔ THE REGRESSION. Measured against a real remote 2026-08-28, before the fix, verbatim:
#
#   git push -q origin HEAD:main        -> ! [rejected]  HEAD -> main (non-fast-forward)
#   git reset -q --soft HEAD~1          -> ok
#   git restore --staged <ledger>       -> ok        # UNSTAGED, still in the working tree
#   git merge --no-edit -q origin/main  -> error: Your local changes to the following files would be
#                                          overwritten by merge: research/autonomy/research-ledger.json
#   git merge --abort                   -> fatal: There is no merge to abort (MERGE_HEAD missing)
#
# …reported to the caller as "origin/main could not be merged without a conflict — resolve the merge
# yourself". There was no conflict: the identical merge on a clean tree returned 0.
# =================================================================================================

def test_a_worker_whose_base_moved_re_applies_its_claim_and_wins(world):
    """⛔⛔ THE CASE THIS MODULE EXISTS FOR, AND THE ONE THAT WAS BROKEN. Another worker claims a
    DIFFERENT row, which moves the ledger on the trunk. The correct response is to re-read the base,
    RE-APPLY the claim to the base just read, and push again — the optimistic-concurrency loop shape.

    ★ THE ASSERTION THAT CARRIES IT IS THE TRUNK HOLDING **BOTH** OWNERS. That is what proves the
    re-application landed on the fresh base rather than resubmitting a value computed against a base
    that no longer exists — a loop that resubmits the old value cannot converge, and cannot help
    overwriting the other worker if it ever does.
    """
    mine = world.worker("worker-a")
    git = C.Git(repo=mine)
    git.fetch()                                     # my base: both rows free
    world.push_a_claim("worker-b", "AUT-Y", THEM)   # the base moves under me

    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=world.ledger_path(mine))

    assert verdict == C.CLAIMED, (
        f"a worker whose base moved could not claim a free row: {verdict}: {why}. Before the fix "
        "this was SUSPENDED/RETRY, blaming a merge conflict that git had never started.")
    assert world.owners_on_trunk(mine) == {"AUT-X": ME, "AUT-Y": THEM}, (
        "the winning push did not carry BOTH claims. Either the claim was not re-applied to the "
        "freshly merged base, or it overwrote the other worker's row — the same harm from the "
        "other direction.")
    assert _clean(mine) == "", "the worker left the tree dirty after a successful claim"
    assert _trunk_is_merged(mine), "HEAD does not contain origin/main, so the push cannot have been "\
                                   "a fast-forward compare-and-swap"


def test_the_push_is_a_compare_and_swap_that_rejects_the_stale_writer(world):
    """⭐⭐ THE FENCING TOKEN, DEMONSTRATED RATHER THAN DESCRIBED. Both workers read the SAME base and
    both decide the row is free. The loser is not stopped by a lease, a clock or a rule about who
    yields — it is stopped by the remote refusing a ref update whose parent is no longer the tip.

    ★ THE RACE IS INJECTED AT THE ONLY POINT WHERE IT MATTERS: between this worker's decision and
    its push. A fake cannot place it there, because a fake has no ref to move.
    """
    mine = world.worker("worker-a")
    raced = {}

    class RacingGit(C.Git):
        def commit_ledger(self, message):
            super().commit_ledger(message)
            if not raced:                       # exactly once, on the first attempt
                raced["repo"] = world.push_a_claim("worker-b", "AUT-X", THEM)

    git = RacingGit(repo=mine)
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=world.ledger_path(mine))

    assert raced, "the race never fired, so this test proved nothing"
    assert verdict == C.YIELDED and THEM in why, (
        f"the stale writer did not lose the lease: {verdict}: {why}")
    assert world.owners_on_trunk(mine)["AUT-X"] == THEM, (
        "the loser's claim reached the trunk anyway — two workers on one row, which is the whole "
        "incident this module was built for")
    assert _clean(mine) == "", (
        "the conceded claim was left in the working tree. An unpushed claim protects nothing and "
        "this one would also block the next integration.")
    assert "claim AUT-X" not in _git("log", "--oneline", "-5", cwd=mine).stdout, (
        "the losing claim commit is still in local history and would be pushed by the next push")


def test_the_refspec_reaches_the_remote_ref_from_a_branch_not_named_main(world):
    """⛔⛔ AUT-PD-029 AT THE LEVEL IT WAS ACTUALLY VISIBLE. The sibling suite asserts on the argv,
    which is as far as a fake can reach. This runs the push from `claude/worker-a` — a branch whose
    name is not `main` and which does not exist on the remote — and checks the remote ref moved."""
    mine = world.worker("worker-a")
    assert _git("rev-parse", "--abbrev-ref", "HEAD", cwd=mine).stdout.strip() != "main", (
        "the harness put the worker on `main`, which is the one configuration that hides this bug")
    before = _git("rev-parse", "origin/main", cwd=mine).stdout.strip()

    verdict, _ = C.claim("AUT-X", ME, WHEN, git=C.Git(repo=mine),
                         ledger_path=world.ledger_path(mine))

    assert verdict == C.CLAIMED
    _git("fetch", "-q", "origin", "main", cwd=mine)
    assert _git("rev-parse", "origin/main", cwd=mine).stdout.strip() != before, (
        "origin/main did not move, so the push targeted something other than the remote ref")
    assert world.owners_on_trunk(mine)["AUT-X"] == ME


# =================================================================================================
# ⛔ "I LOST THE LEASE" AND "I COULD NOT REACH THE REMOTE" ARE DIFFERENT FAILURES.
# Collapsing them is how a network blip becomes a silent no-op.
# =================================================================================================

def test_a_push_that_cannot_reach_the_remote_is_not_a_lost_lease(world):
    """⛔⛔ MEASURED BEFORE THE FIX, WITH REAL GIT: with `pushurl` aimed at a missing repository, the
    push failed rc=128 (`fatal: … does not appear to be a git repository`), `push()` returned the
    same `False` a rejection returns, the loop burned all three attempts and reported *"every push
    was rejected even after merging origin/main each time"* — a transport fault described as
    contention on the row. Nothing was wrong with the row and nothing was wrong with the race."""
    mine = world.worker("worker-a")
    _git("config", "remote.origin.pushurl", os.path.join(world.root, "gone.git"), cwd=mine)

    verdict, why = C.claim("AUT-X", ME, WHEN, git=C.Git(repo=mine),
                           ledger_path=world.ledger_path(mine))

    assert verdict == C.UNREACHABLE, (
        f"an unreachable remote was reported as {verdict}. YIELDED would concede a row nobody took; "
        "SUSPENDED would send a human to look at a race that never happened.")
    assert "gone.git" in why or "does not appear to be a git repository" in why, (
        "the report characterised the failure instead of quoting git. Only git's own stderr "
        "separates a DNS failure from a refusing hook, and this module cannot infer which it was.")
    assert _clean(mine) == "", "an undecided claim was left in the working tree"
    assert "claim AUT-X" not in _git("log", "--oneline", "-5", cwd=mine).stdout, (
        "an undecided claim was left committed locally, where the next push would carry it")


def test_an_unreachable_fetch_is_a_verdict_not_a_traceback(world):
    """⚠ BEFORE THE FIX THIS ESCAPED AS `CalledProcessError` FROM `fetch(check=True)`. A caller that
    cannot reach the remote has learned nothing about the row; that is an answer, not a crash."""
    mine = world.worker("worker-a")
    _git("config", "remote.origin.url", os.path.join(world.root, "gone.git"), cwd=mine)

    verdict, why = C.claim("AUT-X", ME, WHEN, git=C.Git(repo=mine),
                           ledger_path=world.ledger_path(mine))

    assert verdict == C.UNREACHABLE and "nothing was decided" in why
    assert _clean(mine) == ""


@pytest.mark.parametrize("stderr,expected,why", [
    ("! [rejected]        HEAD -> main (non-fast-forward)", C.PUSH_LOST,
     "the ordinary lost compare-and-swap"),
    ("! [rejected]        HEAD -> main (fetch first)", C.PUSH_LOST,
     "git's other wording for the same loss"),
    ("fatal: 'x' does not appear to be a git repository", C.PUSH_FAILED, "transport"),
    ("fatal: Authentication failed", C.PUSH_FAILED, "credentials"),
    ("! [remote rejected] HEAD -> main (pre-receive hook declined)", C.PUSH_FAILED,
     "a policy refusal is not the race and no retry fixes it"),
    ("", C.PUSH_FAILED, "an unexplained failure"),
])
def test_push_classification_reads_gits_own_markers(monkeypatch, stderr, expected, why):
    """⛔ THE UNKNOWN CASE MUST FAIL TOWARDS `PUSH_FAILED`, AND THE DIRECTION IS THE WHOLE POINT.
    Mistaking a rejection for a transport fault costs one loud report and no claim. Mistaking a
    transport fault for a rejection spends the attempt budget and then blames the row — which is the
    measured behaviour this replaces."""
    git = C.Git(repo="/does/not/matter")
    monkeypatch.setattr(C.Git, "_run", lambda self, *a, **k: subprocess.CompletedProcess(
        a, 1, "", stderr))
    assert git.push() == expected, f"misclassified {why}: {stderr!r}"


def test_git_is_run_under_a_pinned_locale_so_its_messages_cannot_move(world, monkeypatch):
    """⛔ THE CLASSIFIERS ABOVE READ GIT'S ENGLISH. git translates porcelain output when built with
    NLS and given a locale, so under `LANG=fr_FR.UTF-8` a lost compare-and-swap would stop matching
    `non-fast-forward` and be reported as a transport fault — a race blamed on the network.

    ⛔⛔ AND THE ASSERTION IS ON THE ENVIRONMENT HANDED TO GIT, NOT ON A REAL RUN, BECAUSE A REAL RUN
    CANNOT SEE THIS AND THAT WAS MEASURED. Deleting the pin from `_run` SURVIVED the first mutation
    round with all thirty tests green — the mutant is behaviourally equivalent *in this container*,
    where `locale -a` offers only `C`, `C.utf8` and `POSIX` and there is no
    `/usr/share/locale/*/LC_MESSAGES/git.mo`, so git has no translation to emit however it is asked.
    ⚠ It is NOT equivalent anywhere with locales installed, which is every developer machine and most
    CI images. An assertion on the constant survived the same mutation for the matching reason: the
    mutant kept the constant and dropped its USE. So this reads the env dict actually passed to the
    subprocess, which is the one place the mechanism is visible from inside this sandbox.
    """
    mine = world.worker("worker-a")
    monkeypatch.setenv("LC_ALL", "fr_FR.UTF-8")
    monkeypatch.setenv("LANG", "fr_FR.UTF-8")
    seen = {}
    real = C.subprocess.run

    def capture(argv, **kw):
        seen.update(kw.get("env") or {})
        return real(argv, **kw)

    monkeypatch.setattr(C.subprocess, "run", capture)
    C.Git(repo=mine).fetch()

    assert seen, "no environment was passed to git at all, so it inherits the caller's locale"
    assert seen.get("LC_ALL") == "C" and seen.get("LANG") == "C", (
        f"git was run under LC_ALL={seen.get('LC_ALL')!r} LANG={seen.get('LANG')!r}. Translated "
        "output stops matching `non-fast-forward`, and every lost compare-and-swap is then reported "
        "as a transport fault — a race blamed on the network.")


def test_a_clean_push_is_never_read_as_a_failure(monkeypatch):
    """The positive control. Without it the classifier could return PUSH_FAILED for everything and
    every case above would still pass."""
    git = C.Git(repo="/does/not/matter")
    monkeypatch.setattr(C.Git, "_run", lambda self, *a, **k: subprocess.CompletedProcess(a, 0, "", ""))
    assert git.push() == C.PUSH_OK


# =================================================================================================
# ⛔ A BOUNDED LOOP THAT ENDS SOMEWHERE A HUMAN HAS TO ACT.
# =================================================================================================

def test_the_attempt_bound_is_a_named_constant_and_the_loop_honours_it():
    """⚠ Slurm requeues into a HELD state that an explicit release must clear; Rucio moves a rule
    that has sat stuck to `SUSPENDED`. Both are the same shape: automation stops, and it stops
    somewhere visible. The bound has to be a number somebody can find and change.

    ⚠ MUTATION SURVIVOR, DECLARED RATHER THAN HIDDEN: raising `MAX_ATTEMPTS` from 3 to 9 passes
    every test in this file, and that is NOT an equivalent mutation — the loop really would make
    nine attempts. It is left uncaught on purpose. Pinning the literal 3 here would put the same
    number in a second place (CLAUDE.md §1) and would freeze a tuning constant that is explicitly
    allowed to move — Rucio's equivalent carries the comment *"10 was chosen without any particular
    reason"*. What is guarded is what actually matters and what actually broke: that a bound EXISTS,
    that the loop honours it (asserted below by counting real attempts), that it is small enough to
    stop promptly, and that the far side of it is terminal. The residual risk is a future session
    retuning 3 → 10 unnoticed; unbounded is still caught.
    """
    assert isinstance(C.MAX_ATTEMPTS, int) and 1 <= C.MAX_ATTEMPTS <= 10, (
        "MAX_ATTEMPTS is not a small named integer bound any more")
    source = open(os.path.join(os.path.dirname(HERE), "claim.py"), encoding="utf-8").read()
    head = source.split("MAX_ATTEMPTS = ")[0]
    assert "SUSPENDED" in head[-1200:] and "Slurm" in head[-1200:], (
        "the bound's reasoning no longer sits beside it. A bound with no reason next to it is the "
        "first thing a future session raises when the loop is inconvenient.")


def test_there_is_no_verdict_that_tells_the_caller_to_retry():
    """⛔⛔ THE NAME WAS THE DEFECT. `RETRY` was returned for an exhausted loop and for a merge only a
    human can resolve — a status whose name prescribes the one response that cannot work. Every
    verdict here now names a distinct correct response, and the exit codes carry that to a shell."""
    assert not hasattr(C, "RETRY"), (
        "a verdict named RETRY is back. If the caller must do something before trying again, the "
        "verdict has to say so; if nothing was decided, that is UNREACHABLE.")
    assert set(C.EXIT_CODES) == {C.CLAIMED, C.YIELDED, C.UNREACHABLE, C.SUSPENDED}
    assert len(set(C.EXIT_CODES.values())) == 4, (
        "two verdicts share an exit code, so a shell cannot tell 'take the next item' from 'the "
        "network is down' from 'stop, a human is needed' — which is what exit 1 meant before")
    assert C.EXIT_CODES[C.CLAIMED] == 0


def test_an_exhausted_loop_ends_in_a_terminal_state_that_names_the_human(world):
    """The loop must stop, and the stop must say it is a stop. A real remote that keeps moving under
    every attempt is simulated by moving it under every attempt — with real commits, real pushes and
    a real rejection each time."""
    mine = world.worker("worker-a")
    ticks = {"n": 0}

    class AlwaysBehind(C.Git):
        def commit_ledger(self, message):
            super().commit_ledger(message)
            ticks["n"] += 1
            world.push_an_unrelated_commit(f"ci-{ticks['n']}", f"tick-{ticks['n']}.txt")

    verdict, why = C.claim("AUT-X", ME, WHEN, git=AlwaysBehind(repo=mine),
                           ledger_path=world.ledger_path(mine))

    assert ticks["n"] == C.MAX_ATTEMPTS, (
        f"the loop made {ticks['n']} attempts against a bound of {C.MAX_ATTEMPTS} — an unbounded "
        "retry loop is the thing this replaces")
    assert verdict == C.SUSPENDED
    assert "a human clears" in why and "not a row to retry" in why
    assert world.owners_on_trunk(mine)["AUT-X"] is None, (
        "an exhausted loop reported a stop and had still put a claim on the trunk")


# =================================================================================================
# ⭐ THE WITHDRAWAL. It restores BYTES, and the difference from `git checkout --` is somebody's work.
# =================================================================================================

def test_the_withdrawal_keeps_an_unrelated_local_edit_it_did_not_make(world):
    """⭐ `git checkout -- <ledger>` would restore from HEAD and silently delete a row a session had
    filed locally and not yet committed. Writing back the pre-claim snapshot cannot.

    ⚠ AND THE HONEST CONSEQUENCE IS ASSERTED TOO: with a genuinely dirty ledger, git refuses to merge
    and this stops with SUSPENDED — naming the refusal as a refusal. That is a human's problem and it
    is now named, which is precisely what the old message did not do.
    """
    mine = world.worker("worker-a")
    path = world.ledger_path(mine)
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    d["entries"].append({"id": "AUT-LOCAL", "owner": None, "claimed_utc": None, "state": "queued"})
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(d, indent=2) + "\n")
    before = hashlib.sha256(open(path, "rb").read()).hexdigest()

    git = C.Git(repo=mine)
    git.fetch()
    world.push_a_claim("worker-b", "AUT-Y", THEM)
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=path)

    assert hashlib.sha256(open(path, "rb").read()).hexdigest() == before, (
        "the withdrawal destroyed an uncommitted local edit it did not make. A session that files a "
        "new item and then claims one would lose the filing.")
    assert verdict == C.SUSPENDED
    assert "NOT a conflict" in why and "nothing to abort" in why, (
        "git's refusal to merge over a dirty tree was reported as a merge conflict again. It is not "
        "one: no merge starts, and the follow-up `merge --abort` returns `fatal: There is no merge "
        "to abort`. Sending a reader to resolve a collision that does not exist is the exact "
        "failure AUT-PROP-030 measured.")


def test_a_real_content_conflict_is_reported_as_one_and_leaves_no_merge_in_progress(world):
    """The other side of the pair. A committed local change that genuinely collides with the trunk
    must be classified as a CONFLICT rather than as git's dirty-tree REFUSAL — and the merge must be
    aborted, so the worker's tree is left usable rather than half-merged.

    ⛔⛔ THIS TEST DROVE `claim()` UNTIL AUT-PD-160 (2026-08-29), AND IT CANNOT ANY MORE — WHICH IS A
    FACT ABOUT THE MODULE, NOT A SOFTENING OF THIS GUARD. `claim()` now refuses at the door when HEAD
    carries anything origin/main does not, and a committed local divergence is exactly that, so the
    conflict branch is no longer reachable THROUGH `claim()` in production. The classification it
    guards is still live code reached by `integrate()`, so this drives `integrate()` directly and
    keeps every assertion it made; the claim-level half is asserted below, on the same fixture, so
    the pair still fails if either behaviour regresses.
    ⭐ `integrate()`'s conflict branch is kept rather than deleted as unreachable: a caller supplying
    its own `Git` still reaches it (the sibling fake suite does), and removing a classifier because a
    new precondition happens to shadow it trades a named verdict for silence.
    """
    mine = world.worker("worker-a")
    path = world.ledger_path(mine)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_ledger_bytes([("AUT-X", None), ("AUT-Y", "local-divergence")]))
    _git("add", C.LEDGER_REL, cwd=mine)
    _git("commit", "-qm", "a local change to the same row", cwd=mine)

    git = C.Git(repo=mine)
    git.fetch()
    world.push_a_claim("worker-b", "AUT-Y", THEM)

    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=path)
    assert verdict == C.SUSPENDED and "HEAD carries" in why, (
        f"a tree holding a committed local divergence was allowed past the AUT-PD-160 door: "
        f"{verdict}: {why}")

    git.fetch()
    assert git.integrate() == C.MERGE_CONFLICT, (
        "a genuine content collision on the ledger was not classified as a conflict. Reporting it "
        "as git's dirty-tree REFUSAL sends a reader to stash a tree that is already clean.")
    assert not os.path.exists(os.path.join(mine, ".git", "MERGE_HEAD")), (
        "a conflicted merge was left in progress, so the worker's tree is wedged")
    assert _clean(mine) == "", "the aborted merge left the working tree dirty"


# =================================================================================================
# ⛔⛔ AUT-PD-160 — A CLAIM PUSHES THE BRANCH, NOT THE CLAIM.
#
# Measured on origin/main 2026-08-29 (CYC-0073-d4ccfde4). A `claim.py` run in a working tree that
# held the driver's unpushed commits carried ee17c39a2 to `main` and created merges 005b837b8 and
# 818c472f0 on the spot. ⛔ THE OUTCOME WAS BENIGN AND THAT IS THE DANGEROUS PART: each carried
# commit had passed its own preflight, so `main` was sound — but the MERGE was a tree no gate ever
# saw, and nothing anywhere would have said so. It surfaced only because the driver's own push was
# then rejected as redundant.
#
# ⭐ THE INVARIANT IS SEAT s1's, AND IT IS NARROWER THAN THE TWO THE ROW TRIED FIRST. Not "seats must
# not run claim.py" (research-loop §2 step 4 already makes the claimant whoever spawns) and not a
# refspec (`HEAD:main` had been in place since AUT-PD-029 and did not prevent this — nothing about
# `HEAD:main` limits what HEAD CONTAINS). It is: claim.py must run where HEAD is origin/main plus
# the claim. s1 measured that a DRIVER reproduces it identically, so this was never about seats.
# =================================================================================================

def test_a_claim_from_a_tree_holding_unpushed_work_refuses_instead_of_publishing_it(world):
    """⛔⛔ THE INCIDENT, REPLAYED. The worker holds one commit the trunk does not have; the row it
    wants is free and the push would succeed. It must refuse anyway.

    ★ THE ASSERTION THAT CARRIES IT IS THAT THE STRAY COMMIT IS NOT ON THE TRUNK. A verdict alone
    would not distinguish this from a refusal that happened after the push.
    """
    mine = world.worker("worker-a")
    with open(os.path.join(mine, "ungated.txt"), "w", encoding="utf-8") as fh:
        fh.write("work the driver has not pushed\n")
    _git("add", "-A", cwd=mine)
    _git("commit", "-qm", "driver work, gated locally, not yet pushed", cwd=mine)
    stray = _git("rev-parse", "HEAD", cwd=mine).stdout.strip()

    git = C.Git(repo=mine)
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=world.ledger_path(mine))

    assert verdict == C.SUSPENDED, f"the claim did not refuse: {verdict}: {why}"
    assert "HEAD carries" in why and stray[:9] in why, (
        f"the refusal does not name what HEAD is carrying, so the reader cannot act on it: {why}")
    assert "preflight" in why, (
        "the refusal states no remedy. push_guard.py's Refusal already establishes that the remedy "
        "is part of the refusal rather than a courtesy.")
    assert world.owners_on_trunk(mine)["AUT-X"] is None, (
        "the row was claimed on the trunk despite the refusal")
    assert _git("cat-file", "-e", stray, cwd=world.bare, check=False).returncode != 0, (
        "the stray commit reached the bare remote. That is the incident: a push publishes the "
        "BRANCH, and the merge git makes to do it is a tree no gate ever saw.")


def test_without_the_head_check_the_claim_publishes_the_strays_it_was_asked_not_to(world):
    """⭐ THE MUTATION, AND IT IS SINGLE-SITE. Remove the one reading the refusal is built on and the
    incident reproduces exactly — which is what makes the guard above load-bearing rather than
    decorative (`paper-hardening`: seven one-of-a-pair defects were found precisely this way).

    ⚠ THE MUTATION IS APPLIED TO THIS TEST'S OWN `Git` INSTANCE, NEVER TO THE MODULE OR THE TREE. A
    mutation-testing seat that edits the live file is research-loop §3's measured incident — 13
    inverted claims reached origin/main inside a `git add -A` mutation window.
    """
    mine = world.worker("worker-a")
    with open(os.path.join(mine, "ungated.txt"), "w", encoding="utf-8") as fh:
        fh.write("work the driver has not pushed\n")
    _git("add", "-A", cwd=mine)
    _git("commit", "-qm", "driver work, gated locally, not yet pushed", cwd=mine)
    stray = _git("rev-parse", "HEAD", cwd=mine).stdout.strip()

    class BlindGit(C.Git):
        def commits_not_on_trunk(self):
            return []

    verdict, why = C.claim("AUT-X", ME, WHEN, git=BlindGit(repo=mine),
                           ledger_path=world.ledger_path(mine))

    assert verdict == C.CLAIMED, (
        f"the mutant did not even get as far as claiming, so this proves nothing about the guard: "
        f"{verdict}: {why}")
    assert _git("cat-file", "-e", stray, cwd=world.bare, check=False).returncode == 0, (
        "the mutant did NOT publish the stray commit, so the guard above is not what stops it and "
        "the real mechanism is somewhere this suite has not found")


def test_the_ordinary_claim_from_a_clean_checkout_still_lands(world):
    """⭐ THE OTHER HALF OF THE PAIR: the refusal must not cost the normal case. A worker whose only
    pending work IS the claim claims, and the push carries the ledger and nothing else."""
    mine = world.worker("worker-a")
    base = _git("rev-parse", "origin/main", cwd=mine).stdout.strip()

    verdict, why = C.claim("AUT-X", ME, WHEN, git=C.Git(repo=mine),
                           ledger_path=world.ledger_path(mine))

    assert verdict == C.CLAIMED, f"a clean checkout could not claim: {verdict}: {why}"
    assert world.owners_on_trunk(mine)["AUT-X"] == ME
    _git("fetch", "-q", "origin", "main", cwd=mine)
    touched = _git("diff", "--name-only", base, "origin/main", cwd=mine).stdout.split()
    assert touched == [C.LEDGER_REL], (
        f"the claim's push carried files beyond the ledger: {touched}")


def test_a_head_that_cannot_be_read_refuses_rather_than_pushing_blind(world):
    """⛔ THE UNKNOWN CASE FAILS CLOSED, AND THE DIRECTION IS THE WHOLE VALUE. `fetch()` has already
    succeeded when this reading is taken, so a failure here is not a transport fault a retry can
    answer — it is the precondition being unestablishable. Failing open would push whatever HEAD
    happens to hold, which is the incident this guard exists for.
    ⚠ SUSPENDED rather than UNREACHABLE for the same reason: UNREACHABLE means nothing was decided
    and a plain retry may answer it, and that would send the caller straight back into the blind push.
    """
    mine = world.worker("worker-a")

    class BrokenGit(C.Git):
        def commits_not_on_trunk(self):
            raise C.HeadUnverifiable("fatal: bad revision 'origin/main..HEAD'")

    verdict, why = C.claim("AUT-X", ME, WHEN, git=BrokenGit(repo=mine),
                           ledger_path=world.ledger_path(mine))

    assert verdict == C.SUSPENDED, f"an unreadable HEAD did not stop the claim: {verdict}: {why}"
    assert "bad revision" in why, "the refusal characterises git instead of quoting it"
    assert world.owners_on_trunk(mine)["AUT-X"] is None, "the row was claimed anyway"


def test_the_head_check_is_asked_once_so_the_modules_own_merge_cannot_trip_it(world):
    """⛔ THE ONE-OF-A-PAIR TRAP THIS GUARD HAS. `integrate()` legitimately puts a merge on HEAD, and
    the claim commit is itself a commit origin/main does not have — so a check re-asked inside the
    retry loop would refuse this module's own work on attempt 2 and the loop could never converge.

    ★ THE MEASUREMENT IS THE VERDICT, NOT THE CALL COUNT. This drives the real retry path (another
    worker moves the base), and a converging CLAIMED is only possible if the door was not re-checked.
    """
    mine = world.worker("worker-a")
    git = C.Git(repo=mine)
    git.fetch()
    world.push_a_claim("worker-b", "AUT-Y", THEM)   # the base moves under me

    asked = []
    real = git.commits_not_on_trunk

    def counting():
        asked.append(1)
        return real()

    git.commits_not_on_trunk = counting
    verdict, why = C.claim("AUT-X", ME, WHEN, git=git, ledger_path=world.ledger_path(mine))

    assert verdict == C.CLAIMED, (
        f"the retry path no longer converges — the door is being re-checked after this module's own "
        f"commit or merge: {verdict}: {why}")
    assert len(asked) == 1, f"the HEAD check was asked {len(asked)} times, not once"

# =================================================================================================
# ⛔⛔ AUT-PD-165. THE WORKING-TREE DOOR. AUT-PD-160 shut the one HEAD walks through; this is the one
# the driver uses every cycle, because the cycle contract edits the ledger at step 3 and step 9 and
# claims at step 4.
# =================================================================================================


def test_a_claim_does_not_publish_the_uncommitted_ledger_edits_it_found(world):
    """⛔⛔ THE INCIDENT AUT-PD-165 NAMES. The worker's ledger holds an UNCOMMITTED, UNGATED edit —
    a row filed locally, exactly what `priority.py --write` and step 9's write-back leave behind.
    The row it wants is free and the push will succeed. The push must carry the claim and NOTHING
    ELSE.

    ★ THE ASSERTION THAT CARRIES IT IS ON THE TRUNK'S BYTES, NOT ON A VERDICT. `CLAIMED` is the
    correct verdict here and was the verdict before the fix too — the defect was never visible in
    what the caller was told.
    """
    mine = world.worker("worker-a")
    path = world.ledger_path(mine)
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    d["entries"].append({"id": "AUT-UNGATED", "owner": None, "claimed_utc": None,
                         "state": "queued"})
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(d, indent=2) + "\n")

    verdict, why = C.claim("AUT-X", ME, WHEN, git=C.Git(repo=mine), ledger_path=path)

    assert verdict == C.CLAIMED, f"the ordinary dirty-ledger claim no longer lands: {verdict}: {why}"
    trunk = json.loads(_git("show", f"origin/main:{C.LEDGER_REL}", cwd=mine).stdout)
    ids = [e["id"] for e in trunk["entries"]]
    assert "AUT-UNGATED" not in ids, (
        "the claim published the driver's uncommitted ledger edit to `main`. That is a tree no gate "
        "ever saw reaching the trunk through a claim — AUT-PD-160's harm through the other door.")
    assert {e["id"]: e["owner"] for e in trunk["entries"]}["AUT-X"] == ME

    with open(path, encoding="utf-8") as fh:
        after = json.load(fh)
    assert "AUT-UNGATED" in [e["id"] for e in after["entries"]], (
        "the claim destroyed the driver's uncommitted edit instead of publishing it. Keeping the "
        "work out of the COMMIT must not mean deleting it from the TREE.")
    assert {e["id"]: e["owner"] for e in after["entries"]}["AUT-X"] == ME, (
        "the working tree does not carry the claim, so the driver's own next commit would revert "
        "the lease it holds — and take the dispatch_log priority.py scores on with it.")


def test_without_the_trunk_blob_the_claim_publishes_the_edits_it_found(world):
    """⭐ THE MUTATION, SINGLE-SITE: stage the ledger from the TREE, which is what `git add` did.

    ⚠ APPLIED TO THIS TEST'S OWN `Git` SUBCLASS, NEVER TO THE MODULE OR THE TREE (research-loop §3:
    13 inverted claims reached origin/main inside a mutation window).
    """
    mine = world.worker("worker-a")
    path = world.ledger_path(mine)
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    d["entries"].append({"id": "AUT-UNGATED", "owner": None, "claimed_utc": None,
                         "state": "queued"})
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(d, indent=2) + "\n")

    class StagesFromTheTree(C.Git):
        def stage_ledger_blob(self, text):
            self._run("add", C.LEDGER_REL)

    verdict, why = C.claim("AUT-X", ME, WHEN, git=StagesFromTheTree(repo=mine), ledger_path=path)

    assert verdict == C.CLAIMED, (
        f"the mutant did not get as far as claiming, so this proves nothing: {verdict}: {why}")
    trunk = json.loads(_git("show", f"origin/main:{C.LEDGER_REL}", cwd=mine).stdout)
    assert "AUT-UNGATED" in [e["id"] for e in trunk["entries"]], (
        "the mutant did NOT publish the uncommitted edit, so staging from the trunk blob is not "
        "what stops it and the real mechanism is somewhere this suite has not found")


def test_a_claim_over_someone_elses_staged_work_refuses_instead_of_committing_it(world):
    """⛔ THE THIRD ENTRANCE, SHUT IN THE SAME PASS. `git commit` commits the INDEX, so anything the
    driver had already staged rides along in the claim commit — the identical harm, reached without
    touching the ledger at all. The precondition is now: HEAD is origin/main AND the index is HEAD.
    """
    mine = world.worker("worker-a")
    with open(os.path.join(mine, "staged.txt"), "w", encoding="utf-8") as fh:
        fh.write("staged, gated by nothing\n")
    _git("add", "staged.txt", cwd=mine)

    verdict, why = C.claim("AUT-X", ME, WHEN, git=C.Git(repo=mine),
                           ledger_path=world.ledger_path(mine))

    assert verdict == C.SUSPENDED, f"the claim did not refuse: {verdict}: {why}"
    assert "staged.txt" in why, (
        f"the refusal does not name what is staged, so the reader cannot act on it: {why}")
    assert world.owners_on_trunk(mine)["AUT-X"] is None, (
        "the row was claimed on the trunk despite the refusal")
    assert "staged.txt" not in _git("show", "--stat", "--oneline", "origin/main",
                                    cwd=mine).stdout, "the staged file reached the trunk"
