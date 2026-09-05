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

⭐⭐ AND THAT IS THE CANONICAL PRIMITIVE, NOT A LOCAL TRICK (AUT-PROP-030, prior-art pass 2 §2).
**A lease is a lock with an expiry: it solves liveness and it cannot solve safety.** Expiry happens
on the lease service's clock, not inside the holder's execution, so a holder suspended past its own
expiry still believes it holds the lease — Kleppmann's GC-pause argument — and no amount of
clock-checking closes the gap. **Mutual exclusion is enforced at the RESOURCE or not at all:**
Chubby's *sequencer* (Burrows, OSDI 2006) makes the file server validate a lock generation number.
⭐ Our resource already implements it. A ref update IS a compare-and-swap and the commit SHA is an
unforgeable fencing token the remote already checks, so **a rejected push means "I LOST THE LEASE",
never "retry harder"** — and this module was hand-rolling a weaker primitive on top of a working one.

⛔⛔ WHAT THAT COST, MEASURED 2026-08-28 AGAINST A REAL BARE REMOTE AND TWO REAL WORKERS
(AUT-PROP-030). A rejected push undid its commit with `reset --soft` + `restore --staged`, which
UNSTAGES the claim and leaves it in the working tree. `git merge origin/main` then refuses —
verbatim: *"error: Your local changes to the following files would be overwritten by merge:
research/autonomy/research-ledger.json"* — so `integrate()` returned False and the caller was told
*"origin/main could not be merged without a conflict… resolve the merge yourself"*. There was no
conflict: the very next `git merge --abort` failed `fatal: There is no merge to abort (MERGE_HEAD
missing)`, and the identical merge on a clean tree returned 0. ⚠ THE CASE THIS BROKE IS THE ONLY
CASE THE MODULE EXISTS FOR — another worker claiming a DIFFERENT row moves the ledger, which is what
the stale claim edit blocks. The one scenario that still converged was the one with no contention on
the ledger at all.
★ THE SHAPE IS AUT-PD-033's, ONE LAYER DOWN. That defect refreshed the base pointer and never moved
HEAD; this one moved HEAD's pointer and never re-applied the WORK, because the work computed against
the dead base was still sitting in the tree blocking the integration. **In an optimistic-concurrency
loop the re-application is the loop body, not an optimisation** — a loop that refreshes its base and
resubmits the originally computed value cannot converge, and its non-convergence is structural.

⛔ AND THREE FAILURES WORE ONE FACE. `push()` returned a bool, so a push that could not REACH the
remote was indistinguishable from one the remote REFUSED: measured 2026-08-28 in the same session
against the same bare remote, a push whose `pushurl` named a missing repository
(`fatal: … does not appear to be a git repository`, rc=128) burned all three
attempts and reported *"every push was rejected even after merging origin/main"* — a network fault
described as contention, which is how a blip becomes a silent no-op. `fetch()` meanwhile ran with
`check=True` and escaped as a raw `CalledProcessError` traceback rather than a verdict.

⛔ WHAT THIS DOES NOT DO, because something else already does it: protect against a worker that claims
and then dies. That is the LEASE's job — `priority.py:release_stale_claims` ages an owner out by
`claimed_utc`, which is why the cycle contract insists the stamp is not optional. This module and
that one are the two halves: one stops two workers starting, the other stops one worker parking the
queue forever. ⚠ And per the finding above, that half is a LIVENESS device and can never be a safety
one; the push is what makes the safety claim, not the stamp.

⛔⛔ AND A CLAIM PUSHES THE BRANCH, NOT THE CLAIM (AUT-PD-160, measured on origin/main 2026-08-29).
`claim.py` run in a working tree holding the driver's unpushed commits carried ee17c39a2 to `main`
and created merges 005b837b8 and 818c472f0 on the spot. ⛔ THE OUTCOME WAS BENIGN AND THAT IS THE
DANGEROUS PART: every carried commit had passed its own preflight, so `main` was sound — but the
MERGE was a tree no gate ever saw, and nothing anywhere would have said so. It surfaced only because
the driver's own push was rejected moments later as redundant.
⭐ THE INVARIANT IS NARROWER THAN THE TWO THE ROW TRIED FIRST, AND BOTH OF THOSE WERE WRONG. It is
not "seats must not run this" — `research-loop` §2 step 4 already makes the claimant whoever spawns,
so the driver that told a seat otherwise was filing its own mistake as a rule conflict. And it is not
a refspec: `HEAD:main` had been in place since AUT-PD-029 and did not prevent this, because nothing
about `HEAD:main` limits what HEAD CONTAINS. It is: **this module must run where HEAD is origin/main
plus the claim**, which `commits_not_on_trunk()` checks once, before anything is touched.
⚠ ONE LIVE CONSEQUENCE, STATED RATHER THAN LEFT TO BE FOUND: with that door closed, `integrate()`
can only ever fast-forward, so `MERGE_CONFLICT` is unreachable through `claim()` in production. The
branch is kept — a caller supplying its own `Git` still reaches it — and its test now drives
`integrate()` directly rather than quietly guarding nothing.
⚠ AND `--check` STILL DOES NOT REPORT THIS, DELIBERATELY. Being ahead of the trunk is the ordinary
state of a driver mid-cycle; it is harmful only at the moment this module pushes, which is where the
refusal lives. `--check` reports the opposite failure — a claim the trunk cannot see.

⭐ DECIDED, NOT BUILT (AUT-PROP-030's remaining open question): does any write path in this loop reach
the ledger WITHOUT going through the fencing check, the way Chubby's lock-delay covers a write path
that genuinely cannot check a sequencer? Audited every place this module writes: `apply_claim` only
ever writes into the WORKING TREE of a commit that has not yet been pushed, `withdraw_claim` only
restores those same bytes on a conceded attempt, and neither one is visible to any other worker — the
trunk, which is what every other session reads, moves only through `git.push()`'s compare-and-swap.
There is no second door: every mutation that could let two workers both succeed is gated by the one
push this module already treats as the fencing check. **So Chubby's lock-delay fallback does not
apply to this module and none was built** — adding one would be a mechanism for a gap that an audit,
not a guess, shows does not exist here. ⚠ THAT AUDIT IS SOUND AND ITS SENTENCE "there is no second
door" READS WIDER THAN IT WAS ARGUED — see AUT-PD-165 below. It asked only whether a write path could
let TWO WORKERS BOTH SUCCEED, which is a question about concurrency; the ledger's working-tree copy
was correctly cleared on that question and was a door onto a different harm entirely.
Re-open this only if a future write path is added that lands
on the trunk some way other than this module's own `git push`.

⛔⛔ AUT-PD-165: AUT-PD-160 SHUT THE COMMIT DOOR AND LEFT THE WORKING-TREE DOOR OPEN, AND IT IS THE
ONE A DRIVER WALKS THROUGH EVERY CYCLE. `commit_ledger` was `git add research/autonomy/research-
ledger.json` followed by `git commit`, and `git add` stages the file AS IT STANDS — so a claim made
while the ledger held UNCOMMITTED, UNGATED edits published those edits to `main` inside a commit whose
message reads `claim AUT-...`. `commits_not_on_trunk()` is blind to it by construction: nothing is
ahead of the trunk until that commit exists.
⚠ AND IT IS THE ORDINARY SHAPE RATHER THAN AN EDGE CASE, WHICH IS WHY IT RATES ITS OWN ROW. The cycle
contract edits the ledger at step 3 (`priority.py --write`) and again at step 9 (the write-back), and
claims at step 4; a driver taking a second item in one session is holding exactly this state. The
cycle that filed the row measured itself stopping to wait ~9 minutes for a gate rather than claim over
its own write-back.
⭐ THE FIX IS THE STRONGER OF THE TWO THE ROW OFFERED, AND IT IS STRUCTURAL RATHER THAN A CHECK: the
claim commit is built from the TRUNK's ledger plus the one claim (`claim_only_text` →
`stage_ledger_blob`, straight into the index by plumbing), so there is no longer any content it COULD
carry beyond the claim — AUT-PD-160's invariant made true instead of merely tested. The rejected
alternative was to refuse on any ledger diff touching another row; that reads the same evidence and
still leaves the driver unable to claim while holding a re-score, which is the state it is always in.
⚠ THE WORKING TREE IS STAMPED TOO, AND SKIPPING THAT WOULD HAVE BEEN A QUIETER BUG THAN THE ONE FIXED.
With only the commit stamped, the caller's ledger still says the row is free, so the driver's own next
commit REVERTS the lease it holds — and takes the `dispatch_log` entry `priority.py` scores on with it.
⛔ AND THE INDEX IS CHECKED AT ENTRY (`staged_paths`), because `git commit` commits the index: work the
caller had already staged rode along in the claim commit without the ledger being involved at all. The
precondition is now the whole of it — **HEAD is origin/main AND the index is HEAD.**
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER_REL = "research/autonomy/research-ledger.json"
LEDGER = os.path.join(HERE, "research-ledger.json")

# ⚠ sys.path, not a package import — see priority.py's identical comment; this directory is a
# flat set of scripts, not a package.
sys.path.insert(0, HERE)
import ledger_io  # noqa: E402
from local_ownership import Coordinator, Refused as OwnershipRefused  # noqa: E402
import priority  # noqa: E402 — AUT-PD-014: shares priority.py's evidence_fingerprint() so the
# fingerprint stamped HERE, at dispatch, and the one `fruitless_attempts_count()` reads back later
# are computed by the same function. `priority.py` has no import-time side effects (see its own
# module docstring; it only defines paths/functions), so this import is safe.

#: The verdicts. ⛔ EACH ONE EXISTS BECAUSE ITS CORRECT RESPONSE DIFFERS FROM EVERY OTHER'S.
#: TAKEN is internal (the trunk says the row is free); the other four are what a caller sees.
TAKEN, CLAIMED, YIELDED = "TAKEN", "CLAIMED", "YIELDED"
#: ⛔ NOTHING WAS DECIDED. The remote could not be reached, or refused the push for a reason that is
#: not the race. The claim is withdrawn and the tree is left as it was found. ⚠ IT IS THE ONE
#: VERDICT A PLAIN RETRY CAN ANSWER — *can*, not *will*: a transport blip clears on its own and a
#: refusing hook never does, and only git's own message tells them apart, which is why the report
#: quotes it verbatim instead of characterising it.
UNREACHABLE = "UNREACHABLE"
#: ⛔⛔ TERMINAL. AUTOMATION HAS STOPPED TRYING AND A HUMAN MUST CLEAR IT. Named for Rucio's
#: `RuleState.SUSPENDED` (prior-art pass 2 §2.1: *"a dated, explicit, terminal state meaning
#: automation has stopped trying, a human is required"*), and shaped like Slurm's automatic requeue,
#: which lands in a HELD state that an explicit release must clear so a retry loop cannot spin.
#: ⚠ IT REPLACED A VERDICT LITERALLY NAMED `RETRY`, which instructed the caller to do the thing that
#: had just failed three times. A name that prescribes the wrong response is not a status.
SUSPENDED = "SUSPENDED"

#: What a push did, and ⛔ THE THREE ARE NOT INTERCHANGEABLE — collapsing them into a bool is the
#: defect recorded in this module's docstring.
PUSH_OK, PUSH_LOST, PUSH_FAILED = "ok", "lost", "failed"
#: What an integration did. `REFUSED` is git declining to merge over a dirty tree; `CONFLICT` is a
#: real content collision. ⛔ The old code reported the first as the second — and then tried to
#: `merge --abort` a merge that had never started.
MERGE_OK, MERGE_CONFLICT, MERGE_REFUSED = "ok", "conflict", "refused"

#: ⚠ BOUNDED, AND THE BOUND IS NOT ABOUT CONTENTION. A rejected push usually means an unrelated CI
#: commit landed, which is common in this repository — the autoscale ticks push several times an
#: hour. Three attempts covers that; more would mean something is wrong that retrying cannot fix.
#: ⛔ AND WHAT IS ON THE OTHER SIDE OF THE BOUND IS THE POINT. Exhausting it returns SUSPENDED, a
#: terminal state, not a suggestion to run the command again: two independently built systems agree
#: that automatic recovery must end somewhere a human has to act — Slurm's requeue lands in a HELD
#: state an explicit release must clear, and Rucio moves a rule that has sat stuck to `SUSPENDED`.
#: ⚠ THE VALUE ITSELF IS A TUNING CONSTANT AND IS NOT DEFENDED AS PRINCIPLED. Rucio's dead-worker
#: threshold — a different constant, quoted only for the principle — carries the comment
#: *"# 10 was chosen without any particular reason"*. What needs justifying is that the loop STOPS,
#: and that is what this constant buys. ⭐ It is deliberately pinned in ONE place: the suite asserts
#: the bound exists, is small and is honoured, and does NOT re-type the number (CLAUDE.md §1), which
#: is why raising it is a declared mutation survivor rather than a caught one.
MAX_ATTEMPTS = 3


class RemoteUnreachable(RuntimeError):
    """git could not talk to the remote at all. ⛔ NOT the same as the remote saying no."""


class HeadUnverifiable(RuntimeError):
    """git could not say what HEAD carries that `origin/main` does not.

    ⛔ NOT a benign "nothing extra". `fetch()` has just succeeded, so `origin/main` exists and this
    question is answerable; a failure here means the repository is in a shape this module cannot
    reason about, and CLAUDE.md §4 is explicit that an absent reading is not a reading of absence.
    """


class Git:
    """The git operations this needs, behind an interface so the decision logic can be tested.

    ⛔ NO TEST MAY PUSH TO THIS REPOSITORY'S REMOTE. A test that pushes changes the trunk, and racing
    writers on the trunk is this module's whole subject.
    ⭐ THAT IS NOT A LICENCE TO TEST ONLY AGAINST A FAKE, AND THE COST OF READING IT THAT WAY IS ON
    THE RECORD: every defect this module has had — the local-branch refspec (AUT-PD-029), the
    non-converging retry (AUT-PD-033) and the dirty-tree integration above — was invisible to a suite
    driving a `FakeGit`, and each surfaced the first time the code met a real remote that had moved.
    A fake that never fails the way production fails tests the code against itself. The suite now
    builds a real bare repository in a tmp_path and races two real workers on it.
    """

    def __init__(self, repo=REPO):
        self.repo = repo
        #: git's own stderr from the last push or merge, so a report can quote the cause rather
        #: than characterise it. ⚠ An absent reading is not a reading of absence (CLAUDE.md §4).
        self.last_push_error = ""
        self.last_merge_error = ""

    #: ⛔ THE CLASSIFIERS BELOW READ GIT'S OWN MESSAGES, SO THE MESSAGES MUST NOT MOVE UNDER THEM.
    #: git translates its porcelain output when built with NLS and given a locale, and a translated
    #: `non-fast-forward` would silently reclassify every lost compare-and-swap as a transport fault
    #: — the loud direction, but wrong, and it would be blamed on the network. Pinning the locale is
    #: cheaper than parsing in every language, and it is the same reason `--porcelain` exists.
    C_LOCALE = {"LC_ALL": "C", "LANG": "C", "LANGUAGE": ""}

    def _run(self, *args, check=True):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True,
                              text=True, check=check, env={**os.environ, **self.C_LOCALE})

    def fetch(self):
        """⛔ RAISES `RemoteUnreachable` RATHER THAN A `CalledProcessError` TRACEBACK.

        A caller that cannot reach the remote has not lost a race and has not claimed anything; it
        has learned nothing, and that is a verdict, not a crash.
        """
        proc = self._run("fetch", "-q", "origin", "main", check=False)
        if proc.returncode != 0:
            raise RemoteUnreachable((proc.stderr or "").strip() or
                                    f"git fetch exited {proc.returncode} with no message")

    def trunk_ledger(self) -> dict:
        return json.loads(self._run("show", f"origin/main:{LEDGER_REL}").stdout)

    def stage_ledger_blob(self, text: str) -> None:
        """Put `text` in the INDEX at `LEDGER_REL` WITHOUT writing the working tree (AUT-PD-165).

        ⛔⛔ THE `git add` THIS REPLACES IS THE WORKING-TREE DOOR. `git add <path>` stages the file
        AS IT STANDS, so a claim made while the ledger held the driver's UNCOMMITTED edits committed
        those edits and pushed them to `main` — ungated, inside a commit whose message says
        `claim AUT-...`. `commits_not_on_trunk()` cannot see it: there is nothing ahead of the trunk
        until this very commit creates it. ⚠ AND IT IS THE ORDINARY SHAPE, NOT AN EDGE CASE — the
        cycle contract edits the ledger at step 3 (`priority.py --write`) and step 9 (the
        write-back), and claims at step 4.
        ⭐ THE PLUMBING IS THE POINT, NOT AN OPTIMISATION. Writing the trunk's bytes into the
        WORKING TREE and calling `git add` would reach the same index and would, for the width of
        one function call, replace the driver's uncommitted work with content it did not write — and
        a container reclaimed in that window destroys it. `hash-object -w` + `update-index` never
        touches the tree, so there is no window to lose.
        ⚠ `--path` is passed so any clean filter configured for this path applies exactly as it
        would to a `git add`; the blob must be what git would have stored, not what we happened to
        hand it.
        """
        proc = subprocess.run(["git", "hash-object", "-w", "--path", LEDGER_REL, "--stdin"],
                              cwd=self.repo, input=text, capture_output=True, text=True,
                              check=True, env={**os.environ, **self.C_LOCALE})
        self._run("update-index", "--add", "--cacheinfo",
                  f"100644,{proc.stdout.strip()},{LEDGER_REL}")

    def staged_paths(self) -> list[str]:
        """Every path the INDEX holds differently from HEAD, staged by somebody other than us.

        ⛔ THE THIRD ENTRANCE, AND IT DOES NOT INVOLVE THE LEDGER AT ALL. `git commit` commits the
        INDEX, so anything the caller had already staged rides along in the claim commit and reaches
        `main` with no gate — the same harm as the two doors above, reached without touching the
        file this module owns. Read ONCE at entry, beside `commits_not_on_trunk()`, so the
        precondition is the whole of it: **HEAD is origin/main AND the index is HEAD**, and the only
        thing that can then be in the claim commit is what this module itself stages.
        """
        return [p for p in self._run("diff", "--cached", "--name-only", "HEAD").stdout.split() if p]

    def commit_ledger(self, message: str):
        """⛔ COMMITS THE INDEX, AND THE ABSENT `git add` IS THE FIX (AUT-PD-165) — see
        `stage_ledger_blob`, which is what put the claim there."""
        self._run("commit", "-q", "-m", message)

    def commits_not_on_trunk(self) -> list[str]:
        """`origin/main..HEAD` — every commit HEAD carries that the trunk does not, newest first.

        ⛔⛔ THIS IS THE READING THAT MAKES AUT-PD-160's INVARIANT CHECKABLE, AND IT IS DELIBERATELY
        ABOUT HEAD RATHER THAN ABOUT THE PUSH. `PUSH_REFSPEC` is already `HEAD:main` and that is
        correct (AUT-PD-029) — but nothing about `HEAD:main` limits what HEAD CONTAINS, which is
        the correction seat s1 made to the row: a refspec cannot fix this.
        ⚠ It is called ONCE, before the first attempt. After that `integrate()` legitimately puts a
        merge here, and the claim commit itself is one — so re-asking inside the loop would refuse
        this module's own work.
        """
        proc = self._run("rev-list", "origin/main..HEAD", check=False)
        if proc.returncode != 0:
            raise HeadUnverifiable((proc.stderr or "").strip() or
                                   f"git rev-list exited {proc.returncode} with no message")
        return [line for line in proc.stdout.split() if line]

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

    #: The two strings git prints when the compare-and-swap ITSELF failed — the remote ref was not
    #: where this worker thought. Anything else that goes wrong on a push is a different animal.
    LOST_MARKERS = ("non-fast-forward", "fetch first")

    def push(self) -> str:
        """`PUSH_OK` · `PUSH_LOST` (the CAS failed) · `PUSH_FAILED` (everything else).

        ⛔ THE UNKNOWN CASE FAILS TOWARDS `PUSH_FAILED`, AND THE DIRECTION IS DELIBERATE. Calling a
        real rejection `PUSH_FAILED` costs one loud report and no claim; calling an unreachable
        remote `PUSH_LOST` spends the whole attempt budget and then blames contention on the row —
        which is the measured behaviour this replaces, and it is how a blip becomes a silent no-op.
        """
        proc = self._run(*self.PUSH_REFSPEC, check=False)
        if proc.returncode == 0:
            return PUSH_OK
        self.last_push_error = (proc.stderr or "").strip()
        if any(marker in self.last_push_error for marker in self.LOST_MARKERS):
            return PUSH_LOST
        return PUSH_FAILED

    def integrate(self) -> str:
        """Merge origin/main into HEAD so a re-applied claim can actually be pushed.

        ⛔⛔ WITHOUT THIS THE RETRY LOOP CANNOT CONVERGE, AND IT LIED ABOUT WHY (AUT-PD-033, measured
        2026-08-27 by using the tool). A push is rejected when the remote has moved — in this
        repository the CI ticks push several times an hour, so that is the ORDINARY case, not
        contention. The loop re-fetched and re-decided, but never INTEGRATED, so HEAD stayed behind
        and every retry was rejected for the same reason as the first. It then reported "the remote
        is moving faster than this can commit", which is a comforting hypothesis for a loop that
        structurally could not succeed.
        ⚠ A CONFLICT HERE IS NOT SOMETHING TO RESOLVE AUTOMATICALLY. The ledger is the file two
        sessions collide on, and a claim is not worth risking a wrong auto-resolution: abort the
        merge and let the caller stop.
        ⛔ AND `REFUSED` IS A DIFFERENT ANSWER FROM `CONFLICT`. git declines outright — *"Your local
        changes to the following files would be overwritten by merge"* — when the working tree is
        dirty on a path the merge touches, and no merge ever starts, which is why the old code's
        unconditional `merge --abort` returned `fatal: There is no merge to abort`. Reporting that
        as a conflict sent every reader to resolve a collision that did not exist.
        """
        proc = self._run("merge", "--no-edit", "-q", "origin/main", check=False)
        if proc.returncode == 0:
            return MERGE_OK
        self.last_merge_error = (proc.stderr or "").strip()
        if "would be overwritten by merge" in self.last_merge_error:
            return MERGE_REFUSED
        self._run("merge", "--abort", check=False)
        return MERGE_CONFLICT

    def undo_last_commit(self):
        """⚠ `reset --soft`, NEVER `--hard`: a yield must not destroy anything else in the tree."""
        self._run("reset", "-q", "--soft", "HEAD~1")
        self._run("restore", "--staged", LEDGER_REL)


def row_of(ledger: dict, entry_id: str):
    """The entry itself, or `None` when this ledger does not carry it.

    ⭐ SPLIT OUT FOR AUT-PD-176 so `decide()` can read fields other than `owner`. It used to be able
    to read exactly one, which is the whole defect that row records.
    """
    for e in ledger.get("entries", []):
        if e.get("id") == entry_id:
            return e
    return None


def owner_of(ledger: dict, entry_id: str):
    """`(found, owner)` — `found` is False when the id is not in this ledger at all.

    ⚠ THE TWO ARE DIFFERENT AND THE DIFFERENCE MATTERS. An id absent from the trunk is an item filed
    locally and not yet pushed; treating that as "free" would let a session claim a row nobody else
    can see, which is a claim that protects nothing.
    """
    e = row_of(ledger, entry_id)
    if e is None:
        return False, None
    return True, e.get("owner")


def finished_by(row: dict):
    """The cycle that recorded this row as FINISHED, or `None` while it is still open work.

    ⛔⛔ AUT-PD-176. A FINISHED ROW WAS INDISTINGUISHABLE FROM FREE WORK, BECAUSE `decide()` READ
    `owner` AND NOTHING ELSE — and `stamp_claim` then wrote `state = "in_progress"` unconditionally,
    so claiming a completed item SILENTLY REOPENED it. ⚠ Measured on origin/main 2026-08-29:
    `AUT-PD-145` was closed by `CYC-0083-381d0696` at 08:25:54Z, with `MAX_UNSCORED_OPEN` and its
    vacuity guard on the trunk and the suite green; at 11:47:29Z commit 5856839fe — a claim written
    by THIS module — flipped it `done -> in_progress` while leaving `closed_by` in place, and a
    whole worker session was then dispatched to redo work that had landed 3.4 hours earlier. The
    row's own completion record was the thing that proved the work was already done.

    ⛔ THE TWO SIGNALS ARE BOTH HERE, AND A CENSUS SAYS WHY NEITHER ALONE WOULD DO. Over all 348
    ledger commits on the trunk there are 40 `closed -> open` transitions, so a blanket "a closed row
    may never reopen" written at the WRITE — the shape R5 uses for the unscored population — would
    have refused 37 ordinary re-derivations and been an outage. Exactly THREE of the 40 carried a
    `closed_by`, which is the field a cycle sets when it deliberately closed the row against a
    receipt: `AUT-PD-143`, `AUT-PD-165` and `AUT-PD-145`. The first two were transient and healed
    back to `done` on their own; the third is the one this module wrote, and it is the one that
    stuck. ⭐ So the guard lives HERE, in the claim path, and not in `ledger_io.write_ledger`:
    re-deriving a closed row is routine, and CLAIMING one never is.
    ⚠ `state` is read as well as `closed_by` because a row can be finished before any cycle names
    itself in it, and `priority.py` already refuses to RANK such a row (`apply_age_factor`'s
    "the ranker starts recommending things that are already done"). No selector offers a closed row,
    so no legitimate claim can want one, and the broader half of this test costs nothing.

    ⭐ AND THE REMEDY FOR WORK THAT GENUINELY MUST BE REDONE IS A NEW ROW, WHICH IS THIS REPOSITORY'S
    OWN ESTABLISHED PATTERN AND NOT AN INVENTION HERE: `AUT-PD-145` exists precisely because
    `AUT-PD-050` landed in halves and the deferred half was filed as its own entry rather than by
    reopening the closed one.
    """
    if row.get("closed_by"):
        return str(row["closed_by"])
    state = row.get("state") or "queued"
    if state in priority.CLOSED_STATES:
        # ⚠ An honest description, not a cycle id: the row is finished and names no closer.
        return f"(state {state}; no closing cycle named)"
    return None


def resource_of(row: dict) -> str | None:
    """Paper/subsystem identity spans task ids, so a second row is not a new writer slot."""
    if row.get("resource"):
        return row["resource"]
    serves = row.get("serves") or {}
    paper = serves.get("publication") or serves.get("paper")
    return f"paper:{paper}" if paper else None


def legacy_handover_refusal(git):
    if not isinstance(git, Git):
        return None
    handover = git._run("show", "origin/main:research/autonomy/codex-handover.json", check=False)
    if handover.returncode == 0:
        try:
            disabled = json.loads(handover.stdout).get("legacy_driver", {}).get("status") == "disabled"
        except (ValueError, AttributeError):
            return "Remote coordinator handover is unreadable; reconcile it before legacy dispatch."
        if disabled:
            return "Remote handover disables the legacy driver; use the registered Codex coordinator."
    return None


def decide(trunk: dict, entry_id: str, me: str) -> tuple[str, str]:
    """`(verdict, why)` from the TRUNK's copy — never the working tree's.

    The working tree is the stale read that caused the incident, so it is not an input here.
    """
    row = row_of(trunk, entry_id)
    if row is None:
        return YIELDED, (f"{entry_id} is not on the trunk. It was filed locally and never pushed, so "
                         "a claim on it is invisible to every other session — push the filing first.")
    # ⛔⛔ FINISHED WORK IS NOT FREE WORK — AUT-PD-176, and this test comes FIRST because it holds
    # however the `owner` field reads. A closed row is unclaimable by the cycle that closed it and by
    # everyone else alike, so returning here before the ownership questions is not an ordering
    # accident: "it is already yours" must not hand a completed item back to its own closer.
    closed = finished_by(row)
    if closed:
        return YIELDED, (
            f"{entry_id} is finished work — closed by {closed} — and claiming it would REOPEN it: "
            "the claim writes `state = in_progress` over the completion record. Take the next item. "
            "If the work genuinely must be redone, file a NEW row for it rather than reopening this "
            "one, the way AUT-PD-145 was filed for the deferred half of AUT-PD-050.")
    resource = resource_of(row)
    for other in trunk.get("entries", []):
        if (resource and other.get("id") != entry_id and other.get("owner")
                and not finished_by(other) and resource_of(other) == resource):
            return YIELDED, f"{resource} is already held through {other['id']} by {other['owner']}"
    owner = row.get("owner")
    if owner and owner != me:
        return YIELDED, f"{entry_id} is already held by {owner}"
    if owner == me:
        return CLAIMED, f"{entry_id} is already yours on the trunk"
    return TAKEN, f"{entry_id} is free on the trunk"


def stamp_claim(ledger: dict, entry_id: str, me: str, when: str) -> bool:
    """Mark `entry_id` as held by `me` in an in-memory ledger. `False` if the row is not there.

    ⭐ SPLIT OUT FOR AUT-PD-165 SO ONE STAMP SERVES TWO DESTINATIONS, AND THE TWO ARE DELIBERATELY
    DIFFERENT LEDGERS. The COMMIT gets the trunk's ledger with this stamp and nothing else
    (`claim_only_text`); the WORKING TREE gets the caller's own ledger — whatever uncommitted work it
    holds — with the same stamp (`apply_claim`). ⛔ A version that stamps once and uses the result
    for both has chosen one of the two harms: commit the tree and it publishes ungated work; write
    the trunk's bytes to the tree and it deletes work the caller had not committed yet.
    """
    for e in ledger["entries"]:
        if e.get("id") == entry_id:
            e["owner"] = me
            e["claimed_utc"] = when
            e["state"] = "in_progress"
            # ⛔⛔ AUT-PD-014: stamp the evidence fingerprint THIS CLAIM IS DISPATCHED AGAINST, now,
            # before any work happens. This is the one moment the true "before" fingerprint is
            # knowable — computing it later (the next time some other module happens to notice the
            # claim) could capture the POST-work fingerprint instead and call a genuine advance
            # fruitless by construction. See priority.py's `evidence_fingerprint` /
            # `fruitless_attempts_count` for the read side of this field.
            e.setdefault("dispatch_log", []).append({
                "utc": when,
                "fingerprint_at_dispatch": priority.evidence_fingerprint(e),
            })
            return True
    return False


def apply_claim(ledger_path: str, entry_id: str, me: str, when: str) -> None:
    """Stamp the claim onto the ledger ON DISK — the caller's own copy, edits and all."""
    with open(ledger_path, encoding="utf-8") as fh:
        d = json.load(fh)
    if not stamp_claim(d, entry_id, me, when):
        raise KeyError(f"{entry_id} is not in {ledger_path}")
    # ⛔ AUT-PD-037: this used to type `indent=2, ensure_ascii=False` out by hand, which happened to
    # match the committed convention but proved nothing — `priority.py`'s own "generator" typed
    # different parameters right next to it. `ledger_io.write_ledger` is the one place that is pinned.
    ledger_io.write_ledger(ledger_path, d)


def claim_only_text(trunk: dict, entry_id: str, me: str, when: str) -> str:
    """The TRUNK's ledger with this one claim stamped on it, in the canonical serialization.

    ⛔⛔ THIS IS WHAT THE CLAIM COMMIT CONTAINS, AND ITS BASE IS THE TRUNK RATHER THAN THE TREE
    (AUT-PD-165). Built fresh inside every attempt, from the trunk that attempt just read, so the
    re-application invariant in `claim()`'s docstring holds for the committed bytes and not merely
    for the file on disk.
    ⚠ SERIALIZED WITH `dumps_ledger`, WHICH DOES NOT RUN admissibility's WRITE GATE — and it does not
    need to: `apply_claim` puts the identical one-row stamp through `write_ledger` on the same
    attempt, so the gate still sees this claim exactly once. What must never drift is the FORMAT, and
    that is why this calls `ledger_io` rather than `json.dumps` (AUT-PD-037).
    ⛔⛔ AND THE HEADER TOTALS ARE DERIVED HERE TOO (measured 2026-09-04, CYC-0104): a claim always
    moves a row between `queued` and `in_progress`, so `n_by_state` is stale in EVERY claim commit
    unless this function re-derives it. `write_ledger` (used by `apply_claim` for the on-disk copy)
    already does this via `ledger_schema.derive_headers`; this path serializes with `dumps_ledger`
    directly and was the one place in the claim flow that skipped it — so the commit `claim.py`
    pushes to `main` carried a stale header every single time, exactly the tests.yml failure
    CYC-0103 fixed on the PREVIOUS claim commit, reproduced immediately by the NEXT one (4db762d6).
    """
    import ledger_schema  # noqa: PLC0415 — see write_ledger's own note on why this is deferred

    d = copy.deepcopy(trunk)
    if not stamp_claim(d, entry_id, me, when):
        raise KeyError(f"{entry_id} is not on the trunk")
    ledger_schema.derive_headers(d)
    return ledger_io.dumps_ledger(d)


def withdraw_claim(ledger_path: str, before: str) -> None:
    """Put back the exact bytes that were in the ledger before this worker touched it.

    ⛔⛔ THIS IS THE HALF THAT WAS MISSING, AND IT IS WHAT MAKES THE LOOP AN OPTIMISTIC-CONCURRENCY
    LOOP RATHER THAN A LOOP THAT REFRESHES A POINTER. `undo_last_commit` unstages the claim and
    leaves it in the working tree; git then refuses to merge origin/main over it, so the base is
    never refreshed, the work is never re-applied, and every attempt fails for the identical reason.
    Measured verbatim 2026-08-28 — see the module docstring.
    ⭐ THE BYTES, NOT `git checkout --`. Restoring from HEAD would also discard any UNRELATED local
    edit to the ledger that was there before the claim — a session that filed a new item and had not
    committed it yet loses that filing. Writing back the snapshot is exactly as clean and cannot.
    ⚠ AND IF THAT PRE-EXISTING EDIT IS ITSELF WHAT BLOCKS THE MERGE, `integrate()` now says
    `MERGE_REFUSED` and the caller stops honestly. That is a human's problem and it is now named.
    """
    with open(ledger_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(before)


def _claim(entry_id: str, me: str, when: str, git: Git | None = None,
          ledger_path: str = LEDGER) -> tuple[str, str]:
    """Take `entry_id` for `me`, or yield to whoever already holds it. Returns `(verdict, why)`.

    ⭐ THE PUSH IS THE ARBITER AND THE LOOP BELOW IS THE WHOLE MECHANISM. Everything before it is an
    optimisation that makes the ordinary case — the other session claimed minutes ago and pushed —
    cost one fetch instead of a commit and a rejected push.

    ★★ THE LOOP BODY IS: READ THE BASE, APPLY THE WORK TO THE BASE JUST READ, SUBMIT. `apply_claim`
    is inside the loop and the withdrawal restores the pre-claim bytes, so each attempt writes its
    claim onto the ledger the merge has just delivered. ⛔ A version that hoists the application out,
    or that leaves the previous attempt's write in place, resubmits a value computed against a base
    that no longer exists — and cannot converge, ever, however many attempts it is given.
    """
    git = git or Git()
    with open(ledger_path, encoding="utf-8", newline="") as fh:
        before = fh.read()
    try:
        # ⛔⛔ AUT-PD-160: REFUSE BEFORE TOUCHING ANYTHING IF HEAD CARRIES WORK THE TRUNK DOES NOT.
        # `git push` publishes the BRANCH, not the claim. Measured on origin/main 2026-08-29: a
        # claim run in a working tree holding the driver's unpushed commits carried ee17c39a2 to
        # `main` and created merges 005b837b8 and 818c472f0 on the spot — a merge no gate ever saw,
        # and the outcome was BENIGN, which is the dangerous part: nothing anywhere would have said
        # so, and it surfaced only because the driver's own push was then rejected as redundant.
        # ⭐ THIS IS THE INVARIANT SEAT s1 ARRIVED AT AFTER TWO WRONGER ONES WERE DISCARDED. It is
        # not "seats must not claim" (research-loop §2 step 4 already says the claimant is whoever
        # spawns) and it is not a refspec (`HEAD:main` was already in place since AUT-PD-029 and did
        # not prevent this). It is: **claim.py must run where HEAD is origin/main plus the claim.**
        # ⚠ AND THE COMPLEMENT ALREADY EXISTS AND CANNOT COVER THIS. `--check` reports a claim the
        # trunk cannot SEE; this is the opposite failure — a push that carried more than it meant to.
        git.fetch()
        refused = legacy_handover_refusal(git)
        if refused:
            return SUSPENDED, refused
        carried = git.commits_not_on_trunk()
        if carried:
            return SUSPENDED, (
                f"{entry_id} was not claimed: HEAD carries {len(carried)} commit(s) that "
                f"origin/main does not ({carried[0][:9]}"
                f"{' and ' + str(len(carried) - 1) + ' more' if len(carried) > 1 else ''}), and a "
                "push publishes the BRANCH, not the claim — so claiming from here would land that "
                "work, plus any merge git makes to do it, on `main` without a gate having seen the "
                "tree that results. Push those commits yourself through ./scripts/preflight.sh "
                "first, or claim from a checkout of origin/main; then claim again.")
        # ⛔ AUT-PD-165's third entrance, and the cheapest of the three to shut. `git commit` commits
        # the INDEX, so anything already staged rides along in the claim commit — same harm, and it
        # never touches the ledger. Asked ONCE, here, for the same reason as the reading above: this
        # module stages the claim itself moments later, and re-asking inside the loop would refuse
        # its own work.
        staged = git.staged_paths()
        if staged:
            return SUSPENDED, (
                f"{entry_id} was not claimed: {len(staged)} path(s) are already staged in the index "
                f"({', '.join(staged[:4])}{', and more' if len(staged) > 4 else ''}), and `git "
                "commit` commits the INDEX — so the claim commit would carry that work to `main` "
                "with no gate having seen it. Commit it yourself through ./scripts/preflight.sh, or "
                "unstage it (`git restore --staged`); then claim again.")
        for attempt in range(1, MAX_ATTEMPTS + 1):
            git.fetch()
            refused = legacy_handover_refusal(git)
            if refused:
                return SUSPENDED, refused
            trunk = git.trunk_ledger()
            if isinstance(git, Git):
                from bounded_review import task_review_decision
                decision = task_review_decision(row_of(trunk, entry_id) or {}, repo=git.repo)
                if not decision["allowed"]:
                    return SUSPENDED, decision["reason"]
            verdict, why = decide(trunk, entry_id, me)
            if verdict != TAKEN:
                return verdict, why

            # ⛔⛔ TWO DESTINATIONS, TWO BASES — AUT-PD-165. The COMMIT gets the trunk plus this one
            # claim, so a push can carry nothing the caller had not already published; the WORKING
            # TREE gets the caller's own ledger plus the same claim, so the uncommitted work it was
            # holding survives AND its next commit does not revert the lease it now holds. Dropping
            # the second line publishes ungated work; dropping the first deletes it.
            apply_claim(ledger_path, entry_id, me, when)
            git.stage_ledger_blob(claim_only_text(trunk, entry_id, me, when))
            git.commit_ledger(f"claim {entry_id} for {me}")
            outcome = git.push()
            if outcome == PUSH_OK:
                return CLAIMED, f"{entry_id} claimed and pushed on attempt {attempt}"

            # ⛔ WITHDRAW FIRST, WHICHEVER WAY THE PUSH WENT. Leaving the losing commit in place
            # would let a retry push a claim this worker had already conceded.
            git.undo_last_commit()
            withdraw_claim(ledger_path, before)

            if outcome == PUSH_FAILED:
                # ⛔ NOT THE RACE, AND SAYING SO IS THE POINT. Nothing was decided about the row:
                # this worker does not hold it and has not conceded it. Quote git rather than
                # characterise it — the difference between a DNS failure and a refusing hook is
                # visible in the stderr and in nothing this module could infer.
                return UNREACHABLE, (
                    f"the push for {entry_id} did not reach the remote or was refused for a reason "
                    f"that is not the race, so nothing was decided and the claim was withdrawn. "
                    f"git said: {git.last_push_error or '(no message)'}")

            # ⛔ A LOST COMPARE-AND-SWAP IS INFORMATION, NOT AN ERROR. The remote moved between the
            # read and the write — the exact race — so the question is re-asked against what is now
            # there, and the answer may be that somebody else took the row.
            git.fetch()
            verdict, why = decide(git.trunk_ledger(), entry_id, me)
            if verdict == YIELDED:
                return YIELDED, f"{why} — the push race was lost, and the claim was withdrawn cleanly"
            # ⭐ INTEGRATE BEFORE RETRYING, or the next push is rejected for the identical reason.
            merged = git.integrate()
            if merged == MERGE_CONFLICT:
                return SUSPENDED, (
                    f"{entry_id} is still free, but origin/main conflicts with this branch. A claim "
                    "is not worth an automatic resolution on the file two sessions collide on — "
                    f"resolve the merge yourself, then claim again. git said: "
                    f"{git.last_merge_error or '(no message)'}")
            if merged == MERGE_REFUSED:
                return SUSPENDED, (
                    f"{entry_id} is still free, but git refused to merge origin/main over "
                    "uncommitted local changes — this is NOT a conflict and there is nothing to "
                    "abort. Commit or stash the working tree, then claim again. git said: "
                    f"{git.last_merge_error or '(no message)'}")
    except RemoteUnreachable as exc:
        return UNREACHABLE, (f"the remote could not be reached, so nothing was decided about "
                             f"{entry_id} and no claim was made. git said: {exc}")
    except HeadUnverifiable as exc:
        # ⛔ SUSPENDED, NOT UNREACHABLE, AND THE DIRECTION IS THE POINT. `fetch()` has already
        # succeeded here, so the remote is reachable and this is not a transport fault a retry can
        # answer: it is this module being unable to establish the precondition above. Failing open
        # would push whatever HEAD happens to hold, which is the whole incident.
        return SUSPENDED, (
            f"{entry_id} was not claimed: git could not report what HEAD carries beyond "
            f"origin/main, so the precondition that this push contains nothing but the claim could "
            f"not be established, and it is not safe to push blind. git said: {exc}")
    return SUSPENDED, (
        f"{entry_id} was still free after {MAX_ATTEMPTS} attempts and every push lost the "
        "compare-and-swap even after merging origin/main each time. Automation has stopped: this is "
        "not a row to retry, it is a row a human clears. Look at the push output directly.")


def claim(entry_id: str, me: str, when: str, git: Git | None = None,
          ledger_path: str = LEDGER) -> tuple[str, str]:
    """Serialize local legacy claims against the existing Codex coordinator lock.

    The remote push remains the arbiter for legacy clones. Its fetched handover
    disables new claims after cutover; pre-cutover writers must be drained first.
    """
    git = git or Git()
    if not isinstance(git, Git):  # Pure decision/retry test adapters have no clone.
        return _claim(entry_id, me, when, git, ledger_path)
    try:
        with Coordinator(git.repo) as ownership:
            if ownership.state.get("owner"):
                return SUSPENDED, f"Local Codex coordinator {ownership.state['owner']} owns this clone."
            return _claim(entry_id, me, when, git, ledger_path)
    except OwnershipRefused as exc:
        return SUSPENDED, str(exc)


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


#: ⛔ ONE EXIT CODE PER VERDICT, BECAUSE THE CORRECT RESPONSES DIFFER AND A SHELL CANNOT READ PROSE.
#: 1 was every failure before this; a caller could not tell "someone else has it, take the next item"
#: from "the network is down, nothing was decided" from "stop, a human is needed".
EXIT_CODES = {CLAIMED: 0, YIELDED: 1, UNREACHABLE: 2, SUSPENDED: 3}


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
        try:
            git.fetch()
        except RemoteUnreachable as exc:
            print(f"   UNREACHABLE the remote could not be reached, so no local claim could be "
                  f"checked against the trunk. git said: {exc}")
            return EXIT_CODES[UNREACHABLE]
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
    return EXIT_CODES[verdict]


if __name__ == "__main__":
    sys.exit(main())
