#!/usr/bin/env python3
"""CLAIM A LEDGER ITEM SO THAT TWO SESSIONS CANNOT BOTH SUCCEED (AUT-PD-021).

⛔⛔ THE LEASE DID NOT PROTECT ANYTHING, MEASURED 2026-08-27 WITH TWO REAL WORKERS.
`atr-single-slot-seat` claimed AUT-PROP-009 at 20:10:00Z and was dispatched with an isolated
worktree. CYC-0025 claimed the SAME item at 20:15:00Z — from committed state it had fetched before
that lease landed — and finished first. Two workers, one item, roughly twenty minutes of duplicated
effort, and the collision surfaced only as a git merge conflict AFTER both had done the work.

⭐ THE DIAGNOSIS IS AUT-PROP-013's, ONE LEVEL UP. Id allocation collided because every session
derived `max(committed) + 1` from state it had already fetched. A claim collides for exactly the same
reason: it is READ-THEN-WRITE against a file another session may have advanced in between, so the
read is stale by construction. `research-loop` step 4 says *"commit that before doing any work"* —
and a local commit is not an arbiter, because two sessions can both make one and meet at the merge.

⭐⭐ SO THE ARBITER IS THE PUSH, THE ONE OPERATION HERE THAT IS ALREADY ATOMIC. `git push` is a
compare-and-swap on the remote ref: it succeeds only if the remote is still where you thought. That
is a real mutual-exclusion primitive rather than a rule about who yields — and AUT-PROP-013's finding
was precisely that a rule about yielding is NOT a mechanism, because the yielding session must first
NOTICE, and a session that pushes cleanly never does.

⚠ MEASURED WHILE WRITING THIS, ON THE AUTHOR'S OWN CLAIM: AUT-PROP-022 was claimed, a seat was
dispatched, and the claim then sat in an UNCOMMITTED merge for eight minutes while the trunk still
showed the row unowned. The window is not hypothetical and it is not somebody else's mistake — it is
the default behaviour of claiming in the working tree and committing later.

⛔ WHAT THIS DOES NOT DO, because something else already does it: protect against a worker that claims
and then dies. That is the LEASE's job — `priority.py:release_stale_claims` ages an owner out by
`claimed_utc`, which is why the cycle contract insists the stamp is not optional. This module and
that one are the two halves: one stops two workers starting, the other stops one worker parking the
queue forever.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER_REL = "research/autonomy/research-ledger.json"
LEDGER = os.path.join(HERE, "research-ledger.json")

TAKEN, CLAIMED, YIELDED, RETRY = "TAKEN", "CLAIMED", "YIELDED", "RETRY"

#: ⚠ BOUNDED, AND THE BOUND IS NOT ABOUT CONTENTION. A rejected push usually means an unrelated CI
#: commit landed, which is common in this repository — the autoscale ticks push several times an
#: hour. Three attempts covers that; more would mean something is wrong that retrying cannot fix.
MAX_ATTEMPTS = 3


class Git:
    """The git operations this needs, behind an interface so the decision logic can be tested.

    ⛔ THE TESTS MUST NEVER PUSH. A test that exercises the real remote is a test that changes the
    trunk, and this module's whole subject is two writers racing on it.
    """

    def __init__(self, repo=REPO):
        self.repo = repo

    def _run(self, *args, check=True):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True,
                              text=True, check=check)

    def fetch(self):
        self._run("fetch", "-q", "origin", "main")

    def trunk_ledger(self) -> dict:
        return json.loads(self._run("show", f"origin/main:{LEDGER_REL}").stdout)

    def commit_ledger(self, message: str):
        self._run("add", LEDGER_REL)
        self._run("commit", "-q", "-m", message)

    #: ⛔ `HEAD:main`, NEVER `main` (AUT-PD-029, found by another session 2026-08-27).
    #: `git push origin main` pushes whatever LOCAL BRANCH IS LITERALLY NAMED `main` — which is
    #: stale or unrelated on any session working from a differently-named branch, and this repo's
    #: own convention is `claude/<name>` rebased onto origin/main. There, every push failed as a
    #: non-fast-forward and this module degraded SILENTLY to reporting RETRY forever: it could not
    #: arbitrate a claim at all, and a seat fell back to the manual sequence while the tool built to
    #: make that race-safe took no part in it.
    #: ⭐ `HEAD:main` is a compare-and-swap on the REMOTE ref whatever the local branch is called,
    #: which is exactly what this module's docstring already claimed it was doing. It worked here
    #: only because the author's branch happened to be named `main` — the tool was tested in the one
    #: configuration that hid the bug.
    PUSH_REFSPEC = ("push", "-q", "origin", "HEAD:main")

    def push(self) -> bool:
        return self._run(*self.PUSH_REFSPEC, check=False).returncode == 0

    def undo_last_commit(self):
        """⚠ `reset --soft`, NEVER `--hard`: a yield must not destroy anything else in the tree."""
        self._run("reset", "-q", "--soft", "HEAD~1")
        self._run("restore", "--staged", LEDGER_REL)


def owner_of(ledger: dict, entry_id: str):
    """`(found, owner)` — `found` is False when the id is not in this ledger at all.

    ⚠ THE TWO ARE DIFFERENT AND THE DIFFERENCE MATTERS. An id absent from the trunk is an item filed
    locally and not yet pushed; treating that as "free" would let a session claim a row nobody else
    can see, which is a claim that protects nothing.
    """
    for e in ledger.get("entries", []):
        if e.get("id") == entry_id:
            return True, e.get("owner")
    return False, None


def decide(trunk: dict, entry_id: str, me: str) -> tuple[str, str]:
    """`(verdict, why)` from the TRUNK's copy — never the working tree's.

    The working tree is the stale read that caused the incident, so it is not an input here.
    """
    found, owner = owner_of(trunk, entry_id)
    if not found:
        return YIELDED, (f"{entry_id} is not on the trunk. It was filed locally and never pushed, so "
                         "a claim on it is invisible to every other session — push the filing first.")
    if owner and owner != me:
        return YIELDED, f"{entry_id} is already held by {owner}"
    if owner == me:
        return CLAIMED, f"{entry_id} is already yours on the trunk"
    return TAKEN, f"{entry_id} is free on the trunk"


def apply_claim(ledger_path: str, entry_id: str, me: str, when: str) -> None:
    with open(ledger_path, encoding="utf-8") as fh:
        d = json.load(fh)
    for e in d["entries"]:
        if e.get("id") == entry_id:
            e["owner"] = me
            e["claimed_utc"] = when
            e["state"] = "in_progress"
            break
    else:
        raise KeyError(f"{entry_id} is not in {ledger_path}")
    with open(ledger_path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")


def claim(entry_id: str, me: str, when: str, git: Git | None = None,
          ledger_path: str = LEDGER) -> tuple[str, str]:
    """Take `entry_id` for `me`, or yield to whoever already holds it. Returns `(verdict, why)`.

    ⭐ THE PUSH IS THE ARBITER AND THE LOOP BELOW IS THE WHOLE MECHANISM. Everything before it is an
    optimisation that makes the ordinary case — the other session claimed minutes ago and pushed —
    cost one fetch instead of a commit and a rejected push.
    """
    git = git or Git()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        git.fetch()
        verdict, why = decide(git.trunk_ledger(), entry_id, me)
        if verdict != TAKEN:
            return verdict, why

        apply_claim(ledger_path, entry_id, me, when)
        git.commit_ledger(f"claim {entry_id} for {me}")
        if git.push():
            return CLAIMED, f"{entry_id} claimed and pushed on attempt {attempt}"

        # ⛔ THE REJECTION IS INFORMATION, NOT AN ERROR. The remote moved between the read and the
        # write — which is the exact race — so the claim is withdrawn and the question re-asked
        # against what is now there. Undoing FIRST matters: retrying on top of a local commit that
        # lost the race would push a claim the loser already conceded.
        git.undo_last_commit()
        git.fetch()
        verdict, why = decide(git.trunk_ledger(), entry_id, me)
        if verdict == YIELDED:
            return YIELDED, f"{why} — the push race was lost, and the claim was withdrawn cleanly"
    return RETRY, (f"{entry_id} was still free after {MAX_ATTEMPTS} attempts but every push was "
                   "rejected. The remote is moving faster than this can commit; that is not "
                   "contention on this row and retrying will not fix it.")


def unpushed_claims(trunk: dict, working: dict) -> list[tuple[str, str]]:
    """`[(id, owner)]` held in the working tree but NOT visible on the trunk.

    ⛔ THIS IS THE CHECK THAT WOULD HAVE CAUGHT THE AUTHOR'S OWN WINDOW. A claim that has not been
    pushed protects nothing: every other session reads the trunk, and the trunk still says the row is
    free. Eight minutes of that was measured on AUT-PROP-022 while this very module was being written.
    """
    trunk_owner = {e.get("id"): e.get("owner") for e in trunk.get("entries", [])}
    out = []
    for e in working.get("entries", []):
        owner = e.get("owner")
        if owner and trunk_owner.get(e.get("id")) != owner:
            out.append((e.get("id"), owner))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--id", help="ledger id to claim")
    ap.add_argument("--me", help="the owner name to write (a cycle id, or a seat's name)")
    ap.add_argument("--utc", help="claimed_utc stamp, RFC3339")
    ap.add_argument("--check", action="store_true",
                    help="report claims held locally that the trunk cannot see")
    args = ap.parse_args(argv)

    git = Git()
    if args.check:
        git.fetch()
        with open(LEDGER, encoding="utf-8") as fh:
            working = json.load(fh)
        pending = unpushed_claims(git.trunk_ledger(), working)
        for eid, owner in pending:
            print(f"   UNPUSHED {eid} is held by {owner} locally and free on the trunk — every "
                  "other session can still take it")
        if pending:
            print("   ⛔ a claim that is not pushed protects nothing. Commit and push it now.")
            return 1
        print("   every local claim is visible on the trunk")
        return 0

    if not (args.id and args.me and args.utc):
        ap.error("--id, --me and --utc are required unless --check is given")
    verdict, why = claim(args.id, args.me, args.utc, git=git)
    print(f"{verdict}: {why}")
    return 0 if verdict in (CLAIMED,) else 1


if __name__ == "__main__":
    sys.exit(main())
