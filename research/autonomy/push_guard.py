#!/usr/bin/env python3
"""Refuse a push whose tip carries loop state a line-based merge silently corrupted (AUT-PD-144).

⛔⛔ THE DEFECT, MEASURED 2026-08-28. Two sessions filed `AUT-PD-140` four minutes apart.
CYC-0070-c84c64dd committed at e901ae619; CYC-0070-225452b4 had allocated the SAME id from state
fetched before that commit, REBASED onto it (`git rev-parse 170314393^` IS e901ae619 — these were
not divergent branches meeting at a merge) and pushed. The ledger's rows are separate array
elements, so the rebase produced NO CONFLICT AND NO MARKER, and a duplicate id reached `main`.

⛔ THE COST WAS TOTAL, NOT COSMETIC. `priority.py:merge` REFUSES a duplicated ledger
(`ValueError: duplicate ledger ids: AUT-PD-140`), and `python3 research/autonomy/priority.py --write`
is STEP 3 of the cycle contract — run before any item is taken. Every session crashed there, on
committed `main`, until the row was renamed by hand.

⭐ AND THE GUARD WAS ALREADY CORRECT. `tests/test_ids_cannot_collide.py::
test_the_committed_ledger_has_no_duplicate_ids` FAILS on that trunk (verified by stash: 1 failed,
10 passed), and it sits inside preflight's scope. ⛔ SO THIS IS NOT A MISSING GATE. It is a gap in
what "the tree you commit" means: CLAUDE.md §6 requires that the run you report green is the run
that saw the tree you commit, and an integration performed AT PUSH TIME creates a THIRD tree —
neither session's gated one — that nothing ever looks at. Every id in this loop derives from
`max(committed) + 1` (AUT-PROP-013), so an integration is PRECISELY when a collision becomes
possible and PRECISELY when nothing looks.

★ WHY THIS RUNS AT THE PUSH AND NOT ANYWHERE ELSE. A rule ("re-run preflight after a rebase") had
already failed twice in one day — CYC-0071 diagnosed the collision and renamed the row, and a
concurrent session shipped the identical diagnosis and the identical rename minutes apart. The
item's own finding is that the fix must be MECHANICAL rather than a rule. `git push` is the last
moment anything is still local and the first moment it is everyone's.

⚠ WHAT THIS IS NOT: A RE-GATE. Preflight takes ~75 s at its cheapest and ~10 minutes when gate 13
is slow; nothing that expensive can sit in front of every push and survive. This checks only the
invariants a LINE-BASED MERGE CANNOT SEE and that cost milliseconds, and it says so when it
refuses. The full gate is still `./scripts/preflight.sh`, and this never claims to replace it.

⚠ AND IT DELIBERATELY DOES NOT CHECK THE LEDGER'S DERIVED HEADERS. `n_by_state` on origin/main at
the time this was written read `in_progress: 1` against 3 entries actually in that state, because
`claim.py` mutates a row's state without re-deriving the counters and is right to — a claim must
land in one push. A guard that reds on that legitimately-stale field is a guard that gets switched
off (`paper-hardening` §8b.1), and `priority.py --write` re-derives them anyway.

EXIT CODES
    0  nothing refused (this includes every infrastructure failure — see `_fail_open`)
    1  REFUSED — a named invariant is violated in the tree being pushed
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter

#: The one file whose corruption stops every session at step 3 of the cycle contract. Checked on
#: every pushed tip regardless of what the push claims to change, because the harm this exists for
#: arrived in a push that changed exactly one row of it.
LEDGER = "research/autonomy/research-ledger.json"

#: Where the loop keeps machine-read state. Every one of these is JSON or JSON-lines, so a conflict
#: marker, a truncation or a half-applied merge makes the file UNREADABLE rather than merely wrong —
#: which is the failure the driver of CYC-0073 hit live on 2026-08-29, when `check_write` correctly
#: refused an on-disk ledger holding conflict markers as an unreadable baseline.
STATE_DIR = "research/autonomy/"

#: git's "this ref is being deleted" sentinel on the pre-push protocol line.
ZERO = "0" * 40


class Refusal(Exception):
    """A named invariant violated in a tree that was about to become everyone's."""

    def __init__(self, headline: str, remedy: str) -> None:
        super().__init__(headline)
        self.headline = headline
        #: ⭐ THE REMEDY IS PART OF THE REFUSAL, NOT A COURTESY. A sibling seat's mutation survived
        #: on 2026-08-29 because its guard refused correctly and returned the WRONG REMEDY, and
        #: the suite pinned only the verdict. Pin what the reader is told to do.
        self.remedy = remedy


def _git(repo: str, *args: str) -> str:
    """Run git and return stdout, raising `subprocess.CalledProcessError` on a non-zero exit."""
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True)
    return out.stdout.decode("utf-8", "replace")


def _blob(repo: str, rev: str, path: str) -> str | None:
    """The file's bytes at `rev`, or None when the tree does not contain it.

    ⛔ THE TWO ABSENCES ARE NOT THE SAME AND THIS IS WHERE THEY SEPARATE. A path missing from an old
    branch's tree is nothing to check; a path present and unreadable is the conflict-marker case.
    Collapsing them into one `except: return None` would make the second silently pass.
    """
    try:
        return _git(repo, "cat-file", "-p", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return None


def check_ledger(repo: str, rev: str) -> None:
    """The measured harm: a duplicated entry id, and an unparseable ledger.

    ⛔ REFUSED, NOT WARNED, and for the reason `test_ids_cannot_collide` already gives about the
    ranker: two different items under one identity make every receipt, claim and evidence pointer
    naming that id ambiguous, and the duplicate survives into the next cycle's queue.
    """
    raw = _blob(repo, rev, LEDGER)
    if raw is None:
        return                                    # a tree that predates the ledger; nothing to check
    try:
        entries = json.loads(raw)["entries"]
    except Exception as exc:
        raise Refusal(
            f"{LEDGER} does not parse at the commit being pushed: {exc}",
            "You are pushing a half-integrated file. Restore a valid baseline with "
            "`git checkout origin/main -- research/autonomy/research-ledger.json`, re-apply YOUR "
            "OBSERVATIONS only (a derived `score` must be re-derived by `priority.py --write`, "
            "never carried across an integration), commit, and re-run ./scripts/preflight.sh.")
    dupes = {i: n for i, n in Counter(
        e.get("id") for e in entries if isinstance(e, dict) and e.get("id")).items() if n > 1}
    if dupes:
        named = ", ".join(f"{i} used {n} times" for i, n in sorted(dupes.items()))
        raise Refusal(
            f"{LEDGER} carries a duplicated entry id at the commit being pushed: {named}",
            "Two sessions minted the same id from the same committed state — the AUT-PD-140 "
            "collision. Re-allocate YOUR row with `research/autonomy/ids.next_entry_id(prefix, "
            "entries)` over the INTEGRATED ledger, record `_renamed_from`/`_renamed_why`, and "
            "re-run ./scripts/preflight.sh on the integrated tree. Do not renumber the row that "
            "was already on the trunk.")


def check_state_files(repo: str, rev: str, base: str | None) -> None:
    """Every loop state file the push TOUCHES still parses.

    ⚠ SCOPED TO WHAT THIS PUSH CHANGED, ON PURPOSE. Checking all 131 JSON files under
    `research/autonomy/` on every push would mean one pre-existing broken file on the trunk bricks
    every push in the repository — a guard that cannot be pushed past is a guard that gets deleted,
    and the loop would have no channel left to fix it with. With no readable base (a brand-new
    branch), this checks nothing and `check_ledger` still runs unconditionally.
    """
    if base is None:
        return
    try:
        changed = _git(repo, "diff", "--name-only", "--diff-filter=d", base, rev).split("\n")
    except subprocess.CalledProcessError:
        return
    for path in changed:
        if not path.startswith(STATE_DIR) or not path.endswith((".json", ".jsonl")):
            continue
        raw = _blob(repo, rev, path)
        if raw is None:
            continue
        try:
            if path.endswith(".jsonl"):
                for n, line in enumerate(raw.splitlines(), 1):
                    if line.strip():
                        json.loads(line)
            else:
                json.loads(raw)
        except Exception as exc:
            raise Refusal(
                f"{path} does not parse at the commit being pushed: {exc}",
                "This is loop state that only a machine reads, so a half-applied merge in it is "
                "invisible until something crashes on it. Restore it from origin/main, re-apply "
                "your own change, and re-run ./scripts/preflight.sh on the integrated tree.")


def carried_merges(repo: str, rev: str, base: str | None) -> list[tuple[str, str, int]]:
    """Merge commits this push introduces, as (sha, subject, files-from-the-second-parent).

    ⚠ A NOTICE, NOT A GATE, AND THE DISTINCTION IS THE HONEST PART. Measured live on 2026-08-29
    (AUT-PD-154): a seat's `claim.py` run merged the driver's unpushed local `main` and published
    it, creating merge commit 818c472f0 — 22 files from its second parent, gated by nobody. The
    outcome was benign because each carried commit had its own green preflight, and that is the
    dangerous half: THERE WAS NO SIGNAL AT ALL, and the only reason anyone noticed was that the
    driver's own later push was rejected as already-merged.

    ⛔ THIS DOES NOT REFUSE, AND THAT IS A DECISION WITH A REASON RATHER THAN A SOFTENING. A hard
    "the tip must be a tree preflight recorded" rule needs preflight to record the tree it gated,
    and `claim.py` structurally CANNOT satisfy it — a claim must land in one push, before any gate,
    or it protects nothing (`research-loop` §2 step 4). Any such rule therefore needs a carve-out
    for the exact path that produced the incident, and the carve-out IS the hole. Closing that is
    AUT-PD-154's work, not this file's; what this file can do for free is turn "no signal at all"
    into a line the pushing session reads on its own terminal.
    """
    if base is None:
        return []
    try:
        shas = [s for s in _git(repo, "rev-list", "--merges", f"{base}..{rev}").split() if s]
    except subprocess.CalledProcessError:
        return []
    out = []
    for sha in shas:
        try:
            subject = _git(repo, "log", "-1", "--format=%s", sha).strip()
            n = len([p for p in _git(repo, "diff", "--name-only", f"{sha}^1", sha).split("\n") if p])
        except subprocess.CalledProcessError:
            continue
        out.append((sha[:9], subject, n))
    return out


def inspect(repo: str, rev: str, base: str | None) -> list[str]:
    """Run every check against one pushed tip. Returns the notice lines; raises `Refusal` to stop."""
    check_ledger(repo, rev)
    check_state_files(repo, rev, base)
    return [f"   ⚠ this push introduces merge {sha} ({n} files from its second parent): {subject}"
            for sha, subject, n in carried_merges(repo, rev, base)]


def _base(repo: str, rev: str, remote_sha: str | None) -> str | None:
    """What this push adds ON TOP OF. None when it cannot be established.

    ⛔ NONE IS A READING, NOT A FAILURE, AND THE CALLERS TREAT IT AS ONE. The pre-push protocol hands
    all-zeros for a branch the remote does not have yet; falling back to the merge-base with
    `origin/main` keeps the scoped checks useful for a seat's first branch push, and when even that
    is unresolvable the unconditional ledger check still runs. An absent base never turns a refusal
    into a pass.
    """
    if remote_sha and remote_sha != ZERO:
        return remote_sha
    for candidate in ("origin/main", "main"):
        try:
            return _git(repo, "merge-base", candidate, rev).strip() or None
        except subprocess.CalledProcessError:
            continue
    return None


def protocol_pairs(text: str) -> list[tuple[str, str | None, str]]:
    """Parse git's pre-push protocol into (pushed sha, remote sha, ref label).

    ⛔ A REF BEING DELETED CARRIES NO TREE, AND THE SKIP IS EXPLICIT RATHER THAN INCIDENTAL. git
    sends all-zeros for the local sha on `git push --delete`. Every downstream check would ALSO let
    it through — `cat-file`, `diff` and `rev-list` all fail on that sha and every one of them
    swallows the failure — so the behaviour is the same either way today.
    ⚠ THAT IS EXACTLY WHY THE SKIP LIVES HERE, IN A FUNCTION A TEST CAN SEE. Measured: deleting the
    skip inside `main()` was mutation M6 and it SURVIVED the whole suite, because a deletion passing
    for the RIGHT reason (nothing to check) and a deletion passing for the WRONG one (three
    unreadable-object errors in a row) are indistinguishable from the outside. The module's own
    docstring warns against collapsing those two absences; this is where that warning is enforced,
    and it stops a later, stricter `_blob` from silently starting to refuse `git push --delete`.
    """
    pairs: list[tuple[str, str | None, str]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        local_ref, local_sha, _remote_ref, remote_sha = parts[0], parts[1], parts[2], parts[3]
        if local_sha == ZERO:
            continue
        pairs.append((local_sha, remote_sha, local_ref))
    return pairs


def _fail_open(message: str) -> int:
    """Infrastructure broke. Say so loudly and let the push through.

    ⛔ FAIL OPEN ON THE MACHINERY, CLOSED ON THE INVARIANT — the same split `amendment_guard` makes
    between its classifier and its edits, for the opposite reason. This hook sits in front of EVERY
    push in the repository, including the one that would fix it. A bug here that blocks pushes
    leaves the loop with no channel to repair itself, and the harm it guards is one a preflight on
    the integrated tree still catches minutes later. ⚠ It is loud because a silent fail-open is
    indistinguishable from a pass, which is the shape CLAUDE.md §4 names.
    """
    print(f"⚠ push_guard could not run and did NOT check this push: {message}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="repository to inspect (default: cwd)")
    ap.add_argument("--rev", action="append", default=[],
                    help="check this rev instead of reading the pre-push protocol on stdin")
    ap.add_argument("--base", default=None, help="what --rev is being added on top of")
    args = ap.parse_args(argv)

    if args.rev:
        pairs = [(r, args.base, r) for r in args.rev]
    else:
        try:
            pairs = protocol_pairs(sys.stdin.read())
        except Exception as exc:
            return _fail_open(f"unreadable pre-push input: {exc}")

    if not pairs:
        return 0

    notices: list[str] = []
    for rev, remote_sha, label in pairs:
        try:
            base = _base(args.repo, rev, remote_sha)
            notices += inspect(args.repo, rev, base)
        except Refusal as ref:
            print("⛔ PUSH REFUSED by research/autonomy/push_guard.py (AUT-PD-144)", file=sys.stderr)
            print(f"   ref:    {label}", file=sys.stderr)
            print(f"   commit: {rev}", file=sys.stderr)
            print(f"   ⛔ {ref.headline}", file=sys.stderr)
            print(f"   ⭐ {ref.remedy}", file=sys.stderr)
            print("   ⚠ An integration done at push time creates a tree NO GATE EVER SAW. This "
                  "check is the cheap subset a line-based merge cannot see; it is NOT a preflight "
                  "and does not replace one.", file=sys.stderr)
            return 1
        except Exception as exc:                  # noqa: BLE001 — see `_fail_open`
            return _fail_open(f"{type(exc).__name__}: {exc}")
    for line in notices:
        print(line, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
