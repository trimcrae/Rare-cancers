#!/usr/bin/env python3
"""The publish bar — the clauses that decide whether a paper may be posted unattended.

⚠ THE COUNT IS `len(CLAUSES)` AND IS DELIBERATELY NOT TYPED HERE OR ANYWHERE ELSE. It read
"six" in this docstring, in `record_bar_evidence.py`, in `publication-authority.json` (the
record of what trimcrae actually granted), in CLAUDE.md §3 and at four places in the
architecture doc — eight copies of one number, all correct on 2026-08-26 and all stale by
12:41 PM ET the next day, when `clause_7_readable_enough_to_review` landed in commit 648114f.
Nothing was under-enforced: `evaluate()` derives `n_clauses` from this list at runtime, so the
seventh clause was always checked. But the GRANT RECORD described a bar with one fewer clause
than the code applies, which is CLAUDE.md rule 1 ("a total is DERIVED, never typed") in the
one file where a reader is least able to check. Found 2026-08-27 by a survey seat reading this
file for an unrelated reason — no gate saw it, which is why one now does
(`tests/test_the_clause_count_is_never_typed.py`).

⛔⛔ READ THIS FIRST. On 2026-08-26 trimcrae granted a **bar-scoped** standing aiXiv authority
(architecture doc §6.3, decision D1): the loop may post ANY paper that clears this bar, rather than
a named list of papers. **That makes this file the permission.** Every weakness here is a paper
published under his name and ORCID that should not have been.

Two consequences, and they are the whole design:

    1. EVERY CLAUSE IS A BOOLEAN THIS SCRIPT COMPUTES FROM A COMMITTED ARTIFACT.
       A clause the loop grades for itself is not a clause — it is the loop deciding it may publish.

    2. FAIL CLOSED, ALWAYS. A missing artifact, an unreadable file, a crashed linter, a commit
       mismatch — every one of those is a FAILED clause, never a skipped one. CLAUDE.md §4: an
       absent reading is not a reading of absence. `UNVERIFIABLE` and `FAIL` both block the post;
       they are distinguished only so the loop knows whether to go get the evidence or give up.

⛔ AND THE BAR IS NOT SELF-AMENDABLE UNDER PRESSURE. Loosening a clause is a DECLARED change
(architecture §10.4) and may not be made by the cycle the clause just blocked. `amendment_guard.py`
enforces that; this file does not police itself.

USAGE
    python3 research/autonomy/publish_bar.py --paper PUB-ASO --sha <commit>
    python3 research/autonomy/publish_bar.py --paper PUB-ASO --sha <commit> --json
    python3 research/autonomy/publish_bar.py --all --sha <commit>

EXIT CODES
    0  every clause passed AND the authority file permits this act  -> the loop may post
    1  at least one clause failed or could not be verified          -> escalate, do not post
    2  usage error
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import os
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import deliverable_digest as _dd  # noqa: E402  (same directory, no package)
import posting_register as _pr  # noqa: E402  (same directory, no package)
REPO = HERE.parent.parent
GRAPH = REPO / "systems" / "graph"
MANUSCRIPTS = REPO / "research" / "manuscripts"

AUTHORITY_FILE = HERE / "publication-authority.json"
HARDENING_DIR = HERE / "hardening-state"
PREFLIGHT_DIR = HERE / "preflight-receipts"
SEATS_DIR = HERE / "review-seats"

PASS, FAIL, UNVERIFIABLE = "PASS", "FAIL", "UNVERIFIABLE"

#: ⛔ THE SPECIFIC BANNER. A scoped run's closing verdict advertises the flag
#: ("PREFLIGHT_FULL=1 before publishing."), so a naive substring test for PREFLIGHT_FULL=1 accepts
#: a log from the very run that is telling you it is not the publication run. Measured 2026-08-27
#: against both logs before this constant was written.
FULL_BANNER = "== pytest (modalities: FULL, PREFLIGHT_FULL=1) =="


def _clause(key: str, label: str, verdict: str, evidence: str) -> dict:
    return {
        "clause": key,
        "label": label,
        "verdict": verdict,
        "ok": verdict == PASS,
        "evidence": evidence,
    }


def _rel(path: pathlib.Path) -> str:
    """Repo-relative if we can, absolute if we cannot.

    ⚠ `Path.relative_to` RAISES for a path outside the repo, and this helper is only ever called
    from the fail-closed error path — so a naive `relative_to` here turns "the evidence is missing"
    into an uncaught exception, and an uncaught exception in a permission check is not a refusal,
    it is a crash whose meaning depends entirely on the caller. Caught by
    test_a_missing_authority_file_means_no_authority.
    """
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _read_json(path: pathlib.Path):
    """Any failure to read is a failure to verify. Never raises past the caller."""
    try:
        with path.open() as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, f"absent: {_rel(path)}"
    except Exception as exc:  # unreadable, malformed, permissions
        return None, f"unreadable: {_rel(path)} ({type(exc).__name__})"


def _working_tree_is(commit: str) -> bool:
    """Is the working tree EXACTLY `commit` — same HEAD, nothing uncommitted?

    ⛔ SEPARATED FROM `_tree_at` SO IT CAN BE TESTED (2026-09-02). Inlined, this decision was
    untestable by the one method that would catch a regression in it: a source mutation makes the
    working tree DIRTY, so a test asserting the clean-tree branch cannot fire while the mutant is in
    place, and the mutant survives for a reason that has nothing to do with coverage. As its own
    predicate it can be forced either way from a test, and `_tree_at`'s two branches are then both
    reachable on demand.
    ⚠ BOTH HALVES ARE LOAD-BEARING AND THE SECOND IS THE EASY ONE TO DROP. Same HEAD with
    uncommitted changes is NOT the sha — reading it would be the original defect wearing a check.
    """
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD"],
                          capture_output=True, text=True, cwd=str(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain"],
                           capture_output=True, text=True, cwd=str(REPO))
    if head.returncode != 0 or dirty.returncode != 0:
        return False
    return head.stdout.strip() == commit and not dirty.stdout.strip()


@contextlib.contextmanager
def _tree_at(sha: str):
    """Yield `(root, err)` where `root` is a directory holding the repository AS OF `sha`.

    ⛔⛔ WHY THIS EXISTS. Every clause takes `sha` and the bar's whole premise is that it grades the
    COMMIT that will be posted. Clauses 1, 2, 6 and 7 honour it — clause 7 already reads its
    document with `git show {sha}:{doc}`. ⚠ MEASURED 2026-09-02: clauses 3 and 4 did not. Clause 3
    read `REPO / doc` and clause 4 shelled `lint_citations.py` with no arguments, so both graded the
    WORKING TREE. A paper pinned at a reviewed commit could therefore be cleared by prose that only
    exists uncommitted in somebody's sandbox, or blocked by a defect that commit does not contain —
    and either way the verdict is about a tree no reader will ever see.

    ⭐ THE FAST PATH IS AN EQUALITY, NOT AN OPTIMISATION, and it is what makes this change a no-op in
    the normal case: when `HEAD` resolves to `sha` and the working tree is clean, the working tree IS
    the sha, so `REPO` is returned unchanged and clause 4 keeps its documented behaviour of also
    seeing untracked files (`lint_citations` passes `--others` deliberately, so a fabricated citation
    in a not-yet-`git add`ed draft is caught before the commit). Materialising a tree there would
    QUIETLY DROP that, which would be a loosening dressed as a correctness fix.

    ⛔ AND IT FAILS CLOSED. A sha that cannot be materialised yields `(None, why)`, and the caller
    returns UNVERIFIABLE. A bar that cannot read what it is grading has not passed it.
    """
    target = subprocess.run(["git", "rev-parse", "--verify", f"{sha}^{{commit}}"],
                            capture_output=True, text=True, cwd=str(REPO))
    if target.returncode != 0:
        yield None, f"{sha[:12]} does not resolve to a commit in this repository"
        return
    if _working_tree_is(target.stdout.strip()):
        yield REPO, None
        return

    tmp = tempfile.mkdtemp(prefix="publish-bar-tree-")
    checkout = os.path.join(tmp, "tree")
    added = subprocess.run(["git", "worktree", "add", "--detach", checkout, sha],
                           capture_output=True, text=True, cwd=str(REPO))
    if added.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        yield None, (f"could not materialise the tree at {sha[:12]} "
                     f"({(added.stderr or '').strip().splitlines()[-1:] or ['no detail']})")
        return
    try:
        yield pathlib.Path(checkout), None
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", checkout],
                       capture_output=True, text=True, cwd=str(REPO))
        shutil.rmtree(tmp, ignore_errors=True)
        subprocess.run(["git", "worktree", "prune"], capture_output=True, text=True, cwd=str(REPO))


def _endpoint(pub_id: str) -> dict | None:
    try:
        for record in json.loads((GRAPH / "publications.json").read_text()):
            if record.get("id") == pub_id:
                return record
    except Exception:
        return None
    return None


# -------------------------------------------------------------------- the clauses


#: ⛔ ONE DIGEST PER COMMIT, COMPUTED ONCE. `_covers` is called once per seat record per clause, and
#: each miss shells out to git for every file in the deliverable set. The cache is keyed by commit
#: and holds only what this process computed, so it cannot outlive a run or be seeded from a file.
_DIGEST_CACHE: dict[tuple[str, str], str | None] = {}


def _deliverable_digest_at(pub_id: str, sha: str) -> str | None:
    """The digest of the paper AS A READER RECEIVES IT at `sha`, or None if it cannot be built.

    ⛔ FAILS CLOSED, like every other reading in this file. `deliverable_digest` returns None when any
    member of the set is unreadable at that commit — a partial digest would cover less than it names,
    which is the too-loose half of the defect this replaces. None never compares equal to anything
    here, so an unbuildable digest refuses the clause rather than skipping the check.
    """
    key = (pub_id, sha)
    if key not in _DIGEST_CACHE:
        try:
            digest, _rows = _dd.deliverable_digest(pub_id, at=sha)
        except Exception:
            digest = None
        _DIGEST_CACHE[key] = digest
    return _DIGEST_CACHE[key]


def _covers(pub_id: str, reviewed_commit, sha: str) -> bool:
    """Did a review of `reviewed_commit` read the same paper that `sha` would publish?

    ⛔⛔ THIS REPLACES `reviewed_commit == sha`, AND THE REPLACEMENT IS A RE-ANCHORING RATHER THAN A
    RELAXATION — the distinction matters because `amendment_guard` exists to refuse the other kind.
    The sha was wrong in BOTH directions at once:

        too strict  it changes when nothing the review read changed, so a clean round is discarded
                    by a commit to a ledger header or a test-selector hash
        too loose   it never said WHAT was covered: a seat that read one file and a seat that read
                    forty record the identical string

    A digest over the deliverable set — the publication's own `document` from
    `systems/graph/publications.json` plus the files built from it, derived and never hand-listed —
    has both properties the sha lacked. It cannot stay equal when anything a reader receives changes,
    and it cannot be produced without naming exactly what went into it.

    ⚠ MEASURED, NOT ARGUED (AUT-PD-205-d7df5340, re-measured by CYC-0091-91c8e949 on 2026-09-02).
    Over the 104 commits between round 32's pin `4ae4e9929` and this change, PUB-ASO's deliverable
    digest held one value — `a6f7158552096aea…` — throughout. So the sha comparison discarded a
    clean five-seat round 104 times to track zero real changes, and every one of those discards cost
    another round.

    ⛔ AN EXACT SHA MATCH STILL PASSES, AND IT IS CHECKED FIRST. Nothing that cleared the old test
    fails the new one; the change only stops discarding reviews of bytes that did not move.
    """
    if not isinstance(reviewed_commit, str) or not reviewed_commit:
        return False
    if reviewed_commit == sha:
        return True
    here = _deliverable_digest_at(pub_id, sha)
    there = _deliverable_digest_at(pub_id, reviewed_commit)
    return here is not None and there is not None and here == there


def _rollup_covering(pub_id: str, sha: str, err: str) -> tuple[dict | None, str]:
    """The round roll-up filed at some OTHER commit that reviewed the same paper `sha` would publish.

    ⛔ A ROLL-UP ONLY — the bare `{pub_id}-{commit}.json`, never a `-seat-` file. Clause 6 asks for
    the round's canonical adversarial record, and widening it to any seat file would let a
    single-lens seat stand in for the round's own verdict.
    Multiple candidates require the current hardening record to select their accepted
    round. Without that explicit selection, ambiguity still refuses.
    """
    try:
        paths = sorted(SEATS_DIR.glob(f"{pub_id}-*.json"))
    except Exception:
        return None, err
    found = []
    for path in paths:
        if "-seat-" in path.name:
            continue
        record, _ = _read_json(path)
        if not isinstance(record, dict) or record.get("blind") is not True:
            continue
        if _covers(pub_id, record.get("reviewed_commit"), sha):
            found.append((path.name, record))
    if len(found) == 1:
        return found[0][1], err
    if len(found) > 1:
        # The hardening record already identifies the round whose evidence is accepted.
        # Reuse that explicit choice; do not let an unrelated commit make identical
        # artifacts ambiguous again. All clause-6 checks still run on the chosen record.
        hardening, _ = _read_json(HARDENING_DIR / f"{pub_id}.json")
        pinned = (hardening or {}).get("reviewed_commit")
        selected = [record for name, record in found
                    if record.get("reviewed_commit") == pinned
                    and name == f"{pub_id}-{pinned}.json"]
        if len(selected) == 1:
            return selected[0], err
        return None, (f"{len(found)} round roll-ups review the paper at {sha[:12]} "
                      f"({', '.join(sorted(n for n, _ in found))}) and this clause will not choose "
                      "between them")
    return None, err


def _seat_records(pub_id: str, sha: str) -> tuple[list[dict], list[str]]:
    """Every blind seat record in the repository that reviewed THIS paper at THIS commit.

    ⛔⛔ `sha` HERE IS THE ROUND'S OWN COMMIT, NOT THE COMMIT BEING POSTED, AND THE EXACT MATCH BELOW
    IS DELIBERATE. `_covers` decides which ROUND may speak for a posted commit; it must not decide
    which seats make up a round. Pooling every seat that ever read the same bytes was tried first and
    is wrong twice over: it merges rounds that are separate looks (PUB-ASO's digest
    `a6f7158552096aea…` covers rounds 31 AND 32, ten seats), and it makes the clause unsatisfiable,
    because a blocker filed by a superseded round can then only be cleared by changing the paper —
    even when the defect it names is in a file the paper does not ship. A round is the set of seats
    filed at one commit, and that is what this returns.

    ⛔ THIS IS THE FUNCTION THAT MAKES CLAUSE 1 A MEASUREMENT RATHER THAN A SELF-REPORT. Before it
    existed, the clause read `blockers` and `p1s` straight out of a file the loop writes for itself,
    so a four-key JSON object with two empty lists — no seat, no review, no reading of the paper at
    all — cleared the convergence clause of the publication permission. Verified 2026-08-27 by
    CYC-0015 against the then-current code, not argued: `{"blockers": [], "p1s": [],
    "reviewed_commit": sha, "last_round": 99}` returned PASS with the evidence line
    "round 99 on ec78ba94d0e9: 0 blockers, 0 P1s".
    """
    found, names = [], []
    try:
        paths = sorted(SEATS_DIR.glob(f"{pub_id}-{sha}*.json"))
    except Exception:
        return [], []
    for path in paths:
        record, _ = _read_json(path)
        if not isinstance(record, dict):
            continue
        if record.get("blind") is not True or record.get("reviewed_commit") != sha:
            continue
        found.append(record)
        names.append(path.name)
    return found, names


def _is_seat_file(pub_id: str, sha: str, name: str) -> bool:
    """Is this filename ONE INDEPENDENT LOOK, or the round's roll-up of several?

    ⛔⛔ THE DEFECT THIS NAMES (AUT-PD-193, filed 2026-08-31 by CYC-0090-d7df5340, reproduced
    2026-09-01 before this function was written). `_seat_records` globs `{pub_id}-{sha}*.json` and a
    round's roll-up is filed as `{pub_id}-{sha}.json`, which that glob matches with `*` EMPTY. So
    the roll-up was returned as a sixth seat, and clause 1 then summed `blockers`/`p1s` over every
    returned record. Measured on the records on disk at the time:

        PUB-ASO-7a7f408258c8 (round 26): glob returns 6 records (5 seats + 1 roll-up)
            counted  2 blocker(s), 10 P1(s)
            true     1 blocker,     5 P1(s)   <- the seats' own tallies

    because that roll-up's `_role` says in words that it "carries the union of their tallies, so a
    derivation over the seat glob counts each finding exactly once". Two opposite conventions are on
    disk: PUB-ASO-b53290b37e71 (round 20) and PUB-ASO-f9e5059912a5 (round 27) carry EMPTY tallies
    and cite the round-7 PUB-FUSION-PARTNER precedent for it; round 26 and PUB-ATR-c1bc934fec3c
    carry a populated union. Only the first convention is correct against this code.

    ★ THE DISCRIMINATOR IS THE FILENAME AND NOTHING ELSE, WHICH WAS MEASURED RATHER THAN CHOSEN.
    The obvious alternatives are both wrong on the records on disk: roll-ups routinely carry a
    `seat` key (PUB-ASO-b53290b37e71's reads "five blind seats - regression, arithmetic, ..."), and
    the PUB-ATR seat files carry `lens` instead of `seat`, so neither key separates the two shapes.
    The glob keys on the filename, so the filename is what has to answer for it.

    ⚠ AND A THIRD SHAPE ALREADY EXISTS IN THE DIRECTORY:
    `PUB-FUSION-PARTNER-69d8a6ac1c90-round4-p1-rederivation.json` is blind, matches the glob, and is
    not a seat. `startswith` puts it on the correct side without anyone extending a list — a list is
    a thing somebody must remember to extend, and the remembering is what fails
    (`paper-hardening` §8b.2).
    ⛔ `sha` HERE IS THE RECORD'S OWN `reviewed_commit`, NOT THE COMMIT BEING POSTED. Once records
    filed at an earlier commit can count (see `_covers`), a roll-up and a seat are still told apart
    by the filename — but by the filename each was FILED under. Passing the posted sha would classify
    every record from another commit as a roll-up, which silently empties `seat_only` and turns the
    width check below into a check on nothing.
    """
    return name.startswith(f"{pub_id}-{sha}-seat-")


def _look_history(pub_id: str) -> dict:
    """Every commit of this paper that a blind seat has reviewed, and how many seats reviewed it.

    ⛔ THIS EXISTS BECAUSE CONVERGENCE IS A REPEATED LOOK, NOT A SINGLE TEST, AND THE CLAUSE WAS
    READING IT AS A SINGLE TEST. `paper-hardening` runs rounds until one comes back with no blockers
    and no P1s, and then stops. That is optional stopping: the probability of a clean round arising
    from seats that happened to miss, rather than from a paper that is clean, rises with the number
    of rounds — Simmonds et al. 2017 (`research/method-watch-autonomy-prior-art-2.md` §4.3, PMID
    28935493), whose decision rule is the one that applies here. A round STATUS is a snapshot a
    reader knows may change, and needs no correction; a convergence verdict FEEDS A DECISION —
    posting, which for a paper with a DOI is not revisited — and so needs one.

    ⚠ IT IS NOT MONOTONE, WHICH IS THE WHOLE ARGUMENT, AND IT IS MEASURED RATHER THAN ASSERTED. The
    PUB-FUSION-PARTNER seat records on disk run 9 blockers over 2 seats, then 4 over 5, then TEN
    over 5, then 0 over 5 — the third round found more than the second, on text the second round's
    findings had just been applied to. Per-round findings therefore do not descend to a floor, so a
    zero is one draw from a noisy process and not a measurement of zero defects.

    ⛔ WHAT THIS CANNOT DO, SAID PLAINLY. A real alpha-spending boundary needs the seats' own
    miss rate, and nothing here measures it. No number is invented for it (CLAUDE.md §4); the two
    constraints the clause adds below are the ones that need no unknown parameter.

    ⛔ STILL KEYED BY COMMIT, AND DELIBERATELY SO EVEN THOUGH `_covers` KEYS BY DIGEST. Keying this
    by digest was tried and is a LOOSENING: two rounds that read identical bytes would collapse into
    one bucket, and since the declaring round is excluded from `priors`, a round declaring at those
    bytes would have every earlier look at them excluded along with itself — the width check would
    then compare against the remaining, older, narrower rounds. A round is a set of seats filed at
    one commit; this counts rounds, so it counts commits.
    """
    history = {}
    try:
        paths = sorted(SEATS_DIR.glob(f"{pub_id}-*.json"))
    except Exception:
        return {}
    for path in paths:
        record, _ = _read_json(path)
        if not isinstance(record, dict) or record.get("blind") is not True:
            continue
        seen = record.get("reviewed_commit")
        if isinstance(seen, str) and seen:
            history.setdefault(seen, []).append(path.name)
    # Compare independent looks with independent looks. A synthesis file did not
    # commission another reviewer. Keep a lone canonical record as its one seat,
    # matching the current-round discriminator without rewriting historical data.
    return {seen: (sum(_is_seat_file(pub_id, seen, name) for name in names)
                   or len(names)) for seen, names in history.items()}


def clause_1_hardening_converged(pub_id: str, sha: str) -> dict:
    """`paper-hardening`'s convergence test: no BLOCKERS, on THIS commit. P1s are reported, not gated.

    ⛔⛔ THE P1 HALF WAS REMOVED 2026-08-29 ON TRIMCRAE'S EXPLICIT DECISION, and it is a
    LOOSENING, so the reasoning is here rather than in a commit message.

    The two grades mean different things. A BLOCKER is text that is wrong now — a reader acting on
    the committed paper would be misled. A P1 is text that is CORRECT now but that an ordinary
    future edit would silently falsify, because nothing reads it. `paper-hardening` §8b argues at
    length that grading coverage gaps as blockers is wrong precisely because the count can never
    reach zero — there is always another unguarded sentence — so the number stops tracking paper
    defects and starts tracking instrument coverage. It then says, in terms, to report the two
    counts separately and never merge them.

    ⛔ THIS CLAUSE MERGED THEM. Requiring zero P1s made an unbounded quantity a publication
    gate, which is the same defect the skill diagnoses, one level up: closing a P1 ships a new
    guard, a new guard is new machinery, and the next round finds gaps in that. Measured on PUB-ASO,
    2026-08-29: round 18's three guard-coverage P1s were closed, the work was real, and not one of
    them was a wrong statement in the paper.

    ★ WHAT IS NOT LOST, AND IT IS THE OBJECTION THAT MATTERED. Round 13 found a blocker after
    round 12 came back clean, and all but two of its P1s were damage from round 12's OWN repairs —
    which is why the rule used to read "no blockers AND no P1s". That protection does not come from
    the P1 count and never did: it comes from `reviewed_commit == sha` below. The seats must have
    reviewed the exact commit being posted, so every repair is inside what they read. A round whose
    repairs have not been reviewed cannot satisfy this clause however few P1s it declares.

    ⚠ AND THE COUNTS ARE STILL LOAD-BEARING. The record must still declare its P1s, they must still
    not under-report the seats, and the passing evidence line PRINTS the open P1 count — so a paper
    clearing this clause with live coverage gaps says so, on the line that clears it. What changed
    is that the number no longer refuses; it informs.

    ⛔ AUTHORITY. `amendment_guard` forbids a bar being changed by the cycle it blocked, and this
    cycle WAS blocked by it. The change is therefore trimcrae's, taken 2026-08-29 after he put the
    question himself — "What severity is P1 supposed to represent? 'This number is true but not
    anchored' doesn't seem like it should be a blocker" — and then directed the fix. Declared in
    `amendments.jsonl`.

    Reviewing a pinned commit is the skill's own rule — round 13's seats hit working-tree drift
    mid-review. So a hardening record for a DIFFERENT commit does not clear this paper; it clears
    the paper as it was.

    ⛔⛔ AND CONVERGENCE IS DERIVED FROM THE SEATS, NEVER READ OFF THE RECORD (CYC-0015). This file's
    own design principle 1 says a clause the loop grades for itself is not a clause. Clauses 3-5 are
    computed — two linters and the graph. This one was not: it trusted the record's own arithmetic.
    So the record must now NAME the blind seats behind it, every named seat must exist and have
    reviewed this same commit, and the blocker/P1 tallies are taken from the SEATS. The record's own
    counts are still required (absent is not empty) and are used only to catch a record that
    disagrees with the evidence underneath it.
    """
    label = "hardening converged (no blockers on this commit; P1s reported)"
    record, err = _read_json(HARDENING_DIR / f"{pub_id}.json")
    if record is None:
        return _clause("hardening_converged", label, UNVERIFIABLE,
                       err + " — run a hardening round and record its result")
    blockers = record.get("blockers")
    p1s = record.get("p1s")
    if blockers is None or p1s is None:
        return _clause("hardening_converged", label, UNVERIFIABLE,
                       "record lacks `blockers` or `p1s` — absent is not empty")
    # ⛔ HOW MANY LOOKS PRODUCED THIS VERDICT IS PART OF THE VERDICT (2026-08-28, AUT-PROP-038).
    # `last_round` was read only into an f-string, so a record that never stated it still passed —
    # a convergence claim with no statement of how many rounds it took to arrive. Under §4.3's
    # decision rule that is the one number a reader needs to know whether the clean round is a
    # result or a draw. Absent is not empty, so an absent count is UNVERIFIABLE, not zero.
    rounds = record.get("last_round")
    if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds < 1:
        return _clause("hardening_converged", label, UNVERIFIABLE,
                       f"record states `last_round` as {record.get('last_round')!r} — a convergence "
                       "verdict has to say how many rounds produced it, because the rounds were "
                       "repeated until one came back clean")
    round_commit = record.get("reviewed_commit")
    if not _covers(pub_id, round_commit, sha):
        return _clause("hardening_converged", label, FAIL,
                       f"last round reviewed {round_commit!r}, whose deliverable digest is "
                       f"{str(_deliverable_digest_at(pub_id, str(round_commit)))[:16]!r} against "
                       f"{str(_deliverable_digest_at(pub_id, sha))[:16]!r} at {sha[:12]} — a review "
                       "of a different paper is not a review of this one")

    # ⛔ NO SEAT, NO CONVERGENCE. An empty round is not a converged round: absence of findings is
    # only evidence when somebody looked. CLAUDE.md §4.
    # ⭐ EVERY LOOKUP BELOW IS AGAINST `round_commit`, NEVER `sha`. The round that speaks for this
    # commit may have been filed at another one; once it has, its seats, its filenames and its place
    # in the round history are all facts about THAT commit.
    seats, seat_names = _seat_records(pub_id, round_commit)
    declared = record.get("seats")
    if not isinstance(declared, list) or not declared:
        return _clause("hardening_converged", label, FAIL,
                       "record names no `seats` — a convergence claim with no blind seat behind it "
                       "is the loop grading itself, not a clause")
    missing = [name for name in declared if name not in seat_names]
    if missing:
        return _clause("hardening_converged", label, FAIL,
                       f"record names seat(s) that are absent, not blind, or reviewed another "
                       f"commit: {', '.join(sorted(missing))}")
    if not seats:
        return _clause("hardening_converged", label, FAIL,
                       f"no blind seat record reviewed {str(round_commit)[:12]}")

    # ⛔⛔ A ROUND'S ROLL-UP IS NOT A LOOK, AND ITS TALLIES ARE NOT A SIXTH SEAT'S (AUT-PD-193).
    # `_is_seat_file` carries the measurement. What follows is one narrowed COUNT and two added
    # REFUSALS, and the direction of all three is the same: the count can only get smaller and the
    # refusals can only turn a PASS into a FAIL, never the reverse. That is what `amendment_guard`
    # requires of any change made while this clause is blocking papers, and this one was.
    # ⭐⭐ AND THE BARE `{pub}-{sha}.json` IS NOT ALWAYS A ROLL-UP — WHICH IS WHY THIS IS A
    # CONDITION AND NOT A FLAT EXCLUSION. `clause_6_independent_adversarial_seat` reads exactly
    # that path, so it is the CANONICAL record of a round's adversarial seat, and rounds have been
    # filed with nothing else: `PUB-FUSION-PARTNER-21bc8578b11a` carries 4 blockers and 9 P1s with
    # no `-seat-` sibling on disk. The file is a ROLL-UP only when per-lens seat records sit beside
    # it; alone, it IS the round's one look and its tallies are the round's tallies.
    # ⚠ MEASURED, NOT REASONED. The first version of this check excluded the bare record
    # unconditionally and was caught the same hour by the positive control in
    # `systems/tests/test_autonomy_publish_bar.py::test_all_six_clauses_passing_is_what_it_takes`,
    # whose one blind seat is filed at that very path — a gate that reds on true input, which
    # `paper-hardening` §8b.1 rates worse than one that greens on false input, because the first
    # thing anyone does to it is loosen it.
    seat_only = [rec for rec, name in zip(seats, seat_names)
                 if _is_seat_file(pub_id, round_commit, name)] or seats

    # ⛔ AN OPEN SEAT RECORD REFUSES THE ROUND (AUT-PROP-006). A seat writes its record as its FIRST
    # act — `seat_scratch.py --open-seat-record` — so a seat that dies leaves evidence instead of
    # nothing. That record is honest about being blind and about which commit it reads, so nothing
    # in the filters above excludes it, and a DEAD seat would otherwise be counted here as a look
    # that found nothing. It is the exact shape this file's header forbids: absence of findings is
    # evidence only when somebody finished looking. So an open record refuses, rather than counting.
    open_seats = [name for rec, name in zip(seats, seat_names)
                  if rec.get("status") == "open"]
    if open_seats:
        return _clause("hardening_converged", label, FAIL,
                       f"blind seat record(s) still open at {str(round_commit)[:12]}: "
                       f"{', '.join(sorted(open_seats))} — a seat that has not closed its own record "
                       "has not reported, and an unfinished look is not a clean one")

    # ⛔ THE ROLL-UP CARRIES NO TALLIES OF ITS OWN. This is the input-side fix AUT-PD-193 asks for,
    # and it is the one of the two options offered there that is a STRENGTHENING: refusing the
    # convention that corrupts the count, rather than subtracting the roll-up from the sum. The
    # subtraction is the tempting move and it is a LOOSENING — a roll-up is a SYNTHESIS, so it can
    # grade a blocker no single seat filed (`paper-hardening` §8.0a: the obvious fix "would silently
    # discard findings ... fix the input, never the meter"). Refusing here loses no finding: it says
    # where the finding must be recorded, on a seat record, where it is counted exactly once.
    # ⚠ ONLY WHERE THE RECORD IS ACTUALLY A ROLL-UP — i.e. where per-lens seat records exist beside
    # it. Where it stands alone it is the round's one seat and its tallies are the only copy there
    # is; refusing those would delete the round's findings rather than de-duplicate them.
    has_named_seats = any(_is_seat_file(pub_id, round_commit, name) for name in seat_names)
    loaded_rollups = [name for rec, name in zip(seats, seat_names)
                      if has_named_seats and not _is_seat_file(pub_id, round_commit, name)
                      and ((rec.get("blockers") or []) or (rec.get("p1s") or []))]
    if loaded_rollups:
        return _clause("hardening_converged", label, FAIL,
                       f"round roll-up(s) {', '.join(sorted(loaded_rollups))} carry their own "
                       "`blockers`/`p1s`. The tallies are summed over every record at this commit, "
                       "so a roll-up carrying the union of its seats' findings counts each of them "
                       "twice — and the doubled total is what the under-reporting check below "
                       "compares the record against, so a correct record is refused for "
                       "under-reporting findings that exist once. Tallies live on the seat records; "
                       "the roll-up carries the narrative")

    # The tallies that decide are the seats' own, not the record's.
    seat_blockers = [item for seat in seats for item in (seat.get("blockers") or [])]
    seat_p1s = [item for seat in seats for item in (seat.get("p1s") or [])]
    if len(blockers) < len(seat_blockers) or len(p1s) < len(seat_p1s):
        return _clause("hardening_converged", label, FAIL,
                       f"record under-reports its own seats: it declares {len(blockers)} blocker(s) "
                       f"and {len(p1s)} P1(s), the seats record {len(seat_blockers)} and "
                       f"{len(seat_p1s)}")
    # ⛔ BLOCKERS REFUSE. P1s DO NOT — see this function's docstring for why, and for whose
    # decision that was. The P1 count travels with the verdict either way.
    open_p1s = max(len(p1s), len(seat_p1s))
    if blockers or seat_blockers:
        return _clause("hardening_converged", label, FAIL,
                       f"{max(len(blockers), len(seat_blockers))} blocker(s) open at round "
                       f"{record.get('last_round')} ({open_p1s} P1(s) alongside, which do not "
                       "refuse this clause)")

    # Preserve the existing minimum independent-review width, using the same
    # seat discriminator for past and current rounds. The user-authorized
    # correction removes a known extra-seat demand caused by counting roll-ups.
    # Historical evidence remains untouched; fewer actual reviewers still fails.
    priors = {seen: k for seen, k in _look_history(pub_id).items() if seen != round_commit}
    widest = max(priors.values(), default=0)
    if len(seat_only) < widest:
        return _clause("hardening_converged", label, FAIL,
                       f"the round declaring convergence fielded {len(seat_only)} blind seat(s) against "
                       f"{widest} on the widest earlier round ({len(priors)} earlier round(s) have "
                       "seat records). Rounds are repeated until one comes back clean, so a clean "
                       "round narrower than the ones before it is the loop stopping on its weakest "
                       "look")
    # ⛔ THE OPEN P1 COUNT IS PART OF THE PASS, NOT A FOOTNOTE TO IT. This clause no longer refuses
    # on coverage gaps, so the line that clears the paper is the one place a reader is guaranteed to
    # see how many it is clearing with. A silent PASS would turn "reported, not gated" into
    # "ignored", which is the loosening this change is NOT.
    coverage = ("0 open P1s" if not open_p1s else
                f"{open_p1s} open P1(s) — coverage gaps, reported and not gating")
    return _clause("hardening_converged", label, PASS,
                   f"round {rounds} on {sha[:12]}: 0 blockers across {len(seat_only)} blind seat(s), "
                   f"{coverage}, and no earlier round on record fielded more "
                   f"({len(priors)} earlier round(s) with seat records, widest {widest})")


def clause_2_preflight_full_green(pub_id: str, sha: str) -> dict:
    """`repo-gates`: PREFLIGHT_FULL=1 is required before anything outward-facing, and this is one
    of the only four acts it is for. The receipt must name THIS commit — a green run against a
    different tree says nothing about the one being posted.

    ⛔ THE EXIT CODE IS RE-DERIVED FROM THE COMMITTED LOG, NOT READ OFF THE RECEIPT (CYC-0015).
    `{"mode": "FULL", "exit": 0, "sha": sha, "utc": "typed by hand"}` used to clear this clause, and
    that literal string is what the evidence line printed. The run's own output is now the artifact:
    the receipt names a committed log, the log must carry the FULL-mode banner preflight.sh prints
    and terminate in the `EXIT=` marker `repo-gates` requires, and the receipt's digest must match
    the log it names — so a receipt cannot be re-pointed at some other run's output.
    """
    label = "PREFLIGHT_FULL=1 green on the posted commit"
    record, err = _read_json(PREFLIGHT_DIR / f"{sha}.json")
    if record is None:
        return _clause("preflight_full_green", label, UNVERIFIABLE,
                       err + " — run PREFLIGHT_FULL=1 and record its exit code")
    if record.get("mode") != "FULL":
        return _clause("preflight_full_green", label, FAIL,
                       f"receipt records mode={record.get('mode')!r}; the scoped run does not "
                       "claim any test passes and cannot clear an outward-facing act")
    if record.get("exit") != 0:
        return _clause("preflight_full_green", label, FAIL, f"exit={record.get('exit')!r}")
    if record.get("sha") != sha:
        return _clause("preflight_full_green", label, FAIL,
                       f"receipt is for {record.get('sha')!r}, not {sha!r}")

    rel = str(record.get("log") or "").strip()
    if not rel:
        return _clause("preflight_full_green", label, FAIL,
                       "receipt names no `log` — an exit code nothing can re-derive is a typed "
                       "claim, not a gate result")
    log_path = REPO / rel
    try:
        text = log_path.read_text(errors="replace")
    except Exception as exc:
        return _clause("preflight_full_green", label, UNVERIFIABLE,
                       f"log {rel} is unreadable ({type(exc).__name__})")
    digest = hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()
    if record.get("log_sha256") != digest:
        return _clause("preflight_full_green", label, FAIL,
                       f"receipt's log_sha256 does not match {rel} — the receipt is not bound to "
                       "the run it names")
    if FULL_BANNER not in text:
        return _clause("preflight_full_green", label, FAIL,
                       f"{rel} carries no PREFLIGHT_FULL=1 banner; it is not a FULL run")
    markers = [line for line in text.splitlines() if line.startswith("EXIT=")]
    if not markers:
        return _clause("preflight_full_green", label, FAIL,
                       f"{rel} has no EXIT= marker — an unterminated log is an abandoned run, not "
                       "a green one")
    if markers[-1].strip() != "EXIT=0":
        return _clause("preflight_full_green", label, FAIL,
                       f"{rel} terminates in {markers[-1].strip()!r}")
    return _clause("preflight_full_green", label, PASS,
                   f"FULL run exit 0 on {sha[:12]} at {record.get('utc')}, re-derived from {rel}")


def clause_3_claim_ceiling_honoured(pub_id: str, sha: str) -> dict:
    """lint_claims R1-R5 over the paper itself. Claim STRENGTH — never imply proteome-wide
    selectivity, EMC efficacy, safety, a therapeutic window or clinical readiness."""
    endpoint = _endpoint(pub_id)
    doc = ((endpoint or {}).get("document") or {}).get("file")
    if not doc:
        return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                       UNVERIFIABLE, f"{pub_id} has no document.file in publications.json")
    # ⛔ READ AT `sha`, NOT IN THE WORKING TREE (2026-09-02). This was `path = REPO / doc`, so the
    # clause graded whatever happened to be on disk — see `_tree_at` for the whole diagnosis.
    with _tree_at(sha) as (root, err):
        if root is None:
            return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                           UNVERIFIABLE, err)
        path = root / doc
        if not path.exists():
            return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                           UNVERIFIABLE, f"document {doc} does not exist at {sha[:12]}")
        try:
            proc = subprocess.run(
                [sys.executable, str(root / "research" / "manuscripts" / "lint_claims.py"),
                 str(path)],
                capture_output=True, text=True, timeout=300, cwd=str(root),
            )
        except Exception as exc:
            return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                           UNVERIFIABLE, f"lint_claims did not run ({type(exc).__name__})")
        if proc.returncode != 0:
            tail = (proc.stdout or proc.stderr or "").strip().splitlines()
            return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                           FAIL, f"lint_claims exit {proc.returncode}: {tail[-1] if tail else '—'}")
        return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                       PASS, f"lint_claims clean over {doc} at {sha[:12]}")


def clause_4_identifiers_resolvable(pub_id: str, sha: str) -> dict:
    """lint_citations. Orthogonal to clause 3 and BOTH are required: a hedged sentence on a
    fabricated PMID passes the claim linter. That has happened here twice."""
    endpoint = _endpoint(pub_id)
    doc = ((endpoint or {}).get("document") or {}).get("file")
    if not doc:
        return _clause("identifiers_resolvable", "every identifier traces to a fetch or the ledger",
                       UNVERIFIABLE, f"{pub_id} has no readable document")
    # ⚠ lint_citations takes NO file arguments — it checks the whole tracked corpus and there is no
    # paper-scoped mode. Passing it a path makes argparse exit 2, which reads as a FAILED clause for
    # a paper that may be perfectly clean. That defect was live for one commit and is why this
    # comment exists: a clause that can never pass is as dangerous as one that always does, because
    # an unreachable bar is what invites someone to loosen it.
    #
    # Running it corpus-wide is the conservative reading and we keep it deliberately: an unresolved
    # identifier anywhere in the repository blocks every post until it is fixed.
    #
    # ⛔ AND THE CORPUS IS THE ONE AT `sha` (2026-09-02). `lint_citations` derives its ROOT from its
    # own file location and walks `git ls-files` from there, so running the copy in a materialised
    # tree scopes it to that commit with no new flag and no change to the linter. Running the
    # WORKING TREE's copy against a pinned corpus is not expressible without editing `lint_citations`,
    # and it is also the wrong direction to want: clause 2 already requires a green PREFLIGHT_FULL
    # run bound to this same sha, so the linter at that sha is itself gated. When the sha IS the
    # working tree, `_tree_at` hands back REPO and this is byte-for-byte the call it always made.
    with _tree_at(sha) as (root, err):
        if root is None:
            return _clause("identifiers_resolvable",
                           "every identifier traces to a fetch or the ledger", UNVERIFIABLE, err)
        if not (root / doc).exists():
            return _clause("identifiers_resolvable",
                           "every identifier traces to a fetch or the ledger", UNVERIFIABLE,
                           f"{pub_id}'s document {doc} does not exist at {sha[:12]}")
        try:
            proc = subprocess.run(
                [sys.executable, str(root / "research" / "manuscripts" / "lint_citations.py")],
                capture_output=True, text=True, timeout=600, cwd=str(root),
            )
        except Exception as exc:
            return _clause("identifiers_resolvable",
                           "every identifier traces to a fetch or the ledger", UNVERIFIABLE,
                           f"lint_citations did not run ({type(exc).__name__})")
        if proc.returncode != 0:
            tail = (proc.stdout or proc.stderr or "").strip().splitlines()
            return _clause("identifiers_resolvable",
                           "every identifier traces to a fetch or the ledger", FAIL,
                           f"lint_citations exit {proc.returncode}: {tail[-1] if tail else '—'} "
                           "(corpus-wide at the pinned sha; the defect need not be in this paper)")
        return _clause("identifiers_resolvable", "every identifier traces to a fetch or the ledger",
                       PASS, f"lint_citations clean corpus-wide at {sha[:12]}, covering {doc}")


def clause_5_endpoint_declared(pub_id: str, sha: str) -> dict:
    """The endpoint must exist as ONE falsifiable sentence the paper defends. CLAUDE.md §5: a route
    that cannot name its paper is an activity, not an option — and a paper that cannot name its
    claim is prose, not a result."""
    endpoint = _endpoint(pub_id)
    if endpoint is None:
        return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim",
                       UNVERIFIABLE, f"{pub_id} is not in systems/graph/publications.json")
    claim = (endpoint.get("what_it_would_claim") or "").strip()
    if len(claim) < 40:
        return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim", FAIL,
                       f"what_it_would_claim is empty or too thin to falsify ({len(claim)} chars)")
    doc = (endpoint.get("document") or {}).get("file")
    if not doc:
        return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim", FAIL,
                       f"endpoint names no document ({doc!r})")
    # ⛔ AT THE SHA, LIKE 3 AND 4 (2026-09-02). This was `(REPO / doc).exists()`, so the clause
    # answered PASS for a sha that does not exist at all — found by
    # `test_every_clause_that_takes_a_sha_actually_reads_at_it`, which was written for the other two
    # and caught a third. The one-of-a-pair shape: two clauses were named in the diagnosis and the
    # third looked identical from the outside.
    # ⚠ WHAT THIS STILL DOES NOT FIX, STATED RATHER THAN LEFT FOR A READER TO DISCOVER: `_endpoint`
    # reads `systems/graph/publications.json` from the WORKING TREE, here and in clauses 3, 4 and 7.
    # So `what_it_would_claim` above is the endpoint as it stands now, not as it stood at `sha`.
    # That is a separate change with a wider blast radius — every clause's endpoint lookup — and it
    # is named here so the next reader does not have to rediscover it.
    with _tree_at(sha) as (root, err):
        if root is None:
            return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim",
                           UNVERIFIABLE, err)
        if not (root / doc).exists():
            return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim",
                           FAIL, f"endpoint names a document absent at {sha[:12]} ({doc!r})")
    return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim", PASS,
                   f"{pub_id} claims: {claim[:90]}...")


def clause_7_readable_enough_to_review(pub_id: str, sha: str) -> dict:
    """No sentence in the outgoing document runs past the splitting ceiling, and the paper has not
    bought readability by dropping caution.

    ⚠ ADDED 2026-08-27 AT trimcrae'S REQUEST, after the ASO preprint's v1 went out: "A big issue with
    the preprint v1 is readability... We should make sure readability is a check for our automated
    EMC researchers before future preprint versions go out." Measured on that published text: mean
    sentence 28.4 words, seven sentences over 60, the longest 102 — the hardest-reading submission
    text in this repository.

    ⛔⛔ THIS CLAUSE DELIBERATELY DOES NOT GATE ON A SCORE, AND THAT IS THE WHOLE DESIGN. trimcrae, in
    the same breath: "Good prose is going to come from better writing style rather than metrics.
    Though the metrics could be a decent screening layer." A Flesch threshold as a bar clause is an
    instruction to this loop to write shorter sentences by any means available — and the cheapest
    means is deleting the difficult truth. So the clause fails on exactly two things, neither of
    which can be satisfied by making the paper say less:
      * a sentence past the ceiling, which is always worth SPLITTING, and splitting drops nothing;
      * a FALL in caution markers against the pinned baseline, which is the failure itself.
    Everything else the screen prints is advisory and reaches the author, not the gate.

    ⚠ It runs against the document AT THE PINNED SHA, like every other clause here — a bar that reads
    the working tree measures a paper nobody is publishing.
    """
    name, title = "readable_enough_to_review", "the outgoing text is readable and keeps its caution"
    endpoint = _endpoint(pub_id)
    if endpoint is None:
        return _clause(name, title, UNVERIFIABLE, f"{pub_id} is not in systems/graph/publications.json")
    doc = (endpoint.get("document") or {}).get("file")
    if not doc:
        return _clause(name, title, UNVERIFIABLE, f"{pub_id} names no document")

    import tempfile
    try:
        proc = subprocess.run(["git", "show", f"{sha}:{doc}"], capture_output=True,
                              timeout=120, cwd=str(REPO))
    except Exception as exc:
        return _clause(name, title, UNVERIFIABLE, f"git show failed ({type(exc).__name__})")
    if proc.returncode != 0:
        return _clause(name, title, UNVERIFIABLE, f"{doc} is not in the tree at {sha[:12]}")

    sys.path.insert(0, str(REPO / "research" / "manuscripts"))
    try:
        import lint_readability as LR
    except Exception as exc:  # pragma: no cover - import guard
        return _clause(name, title, UNVERIFIABLE, f"lint_readability did not import ({exc})")

    with tempfile.NamedTemporaryFile("wb", suffix=".md", delete=False) as fh:
        fh.write(proc.stdout)
        tmp = fh.name
    try:
        m = LR.measure(tmp)
    finally:
        os.unlink(tmp)
    if not m:
        return _clause(name, title, UNVERIFIABLE, f"no prose extracted from {doc} at {sha[:12]}")

    baseline = {}
    bl = REPO / "research" / "manuscripts" / "readability-baseline.json"
    if bl.exists():
        baseline = json.loads(bl.read_text(encoding="utf-8")).get("caution_per_1000w", {})
    was = baseline.get(doc)

    if m["over_ceiling"]:
        worst = [w for w in m["worst"] if w["words"] > LR.SENTENCE_CEILING]
        return _clause(name, title, FAIL,
                       f"{m['over_ceiling']} sentence(s) over {LR.SENTENCE_CEILING} words in {doc} "
                       f"(longest {m['max_len']}w at line {worst[0]['line']}). Split them — see the "
                       f"`scientific-writing` skill. Do NOT raise the ceiling and do NOT cut a clause "
                       f"to get under it.")
    if was is not None and m["caution_per_1000w"] < was:
        return _clause(name, title, FAIL,
                       f"caution fell {was} -> {m['caution_per_1000w']} markers per 1000 words in "
                       f"{doc}. A readability pass that costs a hedge, a null or a limitation has "
                       f"made the paper worse. Name what left, or re-pin deliberately.")
    return _clause(name, title, PASS,
                   f"{doc}: no sentence over {LR.SENTENCE_CEILING}w (longest {m['max_len']}w, mean "
                   f"{m['mean_len']}w, FKGL {m['flesch_kincaid_grade']}), caution "
                   f"{m['caution_per_1000w']}/1000w"
                   + (f" against a {was} baseline" if was is not None else " (no baseline pinned)")
                   + ". ⚠ This says nothing about whether the prose is CLEAR.")


def _document_digest(sha: str, doc: str) -> tuple[str | None, str | None]:
    """sha256 of the paper's text AS IT WAS at `sha`, read out of git rather than the working tree.

    A seat record is a claim about a document. Binding it to the bytes it read is the difference
    between "a seat says the claim is supported" and "a seat says the claim is supported, and here
    is the text it said it about".
    """
    try:
        proc = subprocess.run(["git", "show", f"{sha}:{doc}"], capture_output=True,
                              timeout=120, cwd=str(REPO))
    except Exception as exc:
        return None, f"git show failed ({type(exc).__name__})"
    if proc.returncode != 0:
        return None, f"{doc} is not in the tree at {sha[:12]}"
    return hashlib.sha256(proc.stdout).hexdigest(), None


def clause_6_independent_adversarial_seat(pub_id: str, sha: str) -> dict:
    """A blind seat, on the pinned commit, reporting the central claim supported by the COMMITTED
    artifacts. `paper-hardening`: refute by default, and a seat that saw the authoring context is
    not independent.

    ⛔ WHAT THIS CLAUSE CAN AND CANNOT PROVE (CYC-0015). It cannot prove a seat was sincere or that
    it was truly blind — those are properties of how the seat was RUN, and no file can carry them.
    What it can prove is that the record is attached to the exact text it claims to have reviewed,
    so the clause now demands the document's digest at the pinned commit. `{"blind": true,
    "reviewed_commit": sha, "verdict": "supported"}` used to clear it; that object names no paper,
    quotes no claim, and would clear the bar for a document it never opened.
    """
    label = "a blind adversarial seat finds the claim supported"
    # ⛔ THE CANONICAL PATH IS STILL `{pub}-{sha}.json` AND IS STILL TRIED FIRST. Only when this
    # commit has no round of its own does the search widen to a roll-up filed at another commit that
    # `_covers` says reviewed the same paper — and it is a SEARCH, not a fallback that lowers a bar:
    # every property this clause checks below is then checked against that record exactly as it
    # would have been against one filed here.
    record, err = _read_json(SEATS_DIR / f"{pub_id}-{sha}.json")
    if record is None:
        record, err = _rollup_covering(pub_id, sha, err)
    if record is None:
        return _clause("independent_adversarial_seat", label, UNVERIFIABLE,
                       err + " — run a blind seat on this commit")
    if not record.get("blind"):
        return _clause("independent_adversarial_seat", label, FAIL,
                       "seat was not blind; it is not independent evidence")
    if not _covers(pub_id, record.get("reviewed_commit"), sha):
        return _clause("independent_adversarial_seat", label, FAIL,
                       f"seat reviewed {record.get('reviewed_commit')!r}, which is a different paper "
                       f"from the one {sha[:12]} would publish")
    if record.get("verdict") != "supported":
        return _clause("independent_adversarial_seat", label, FAIL,
                       f"seat verdict: {record.get('verdict')!r}")
    if len(str(record.get("central_claim") or "").strip()) < 40:
        return _clause("independent_adversarial_seat", label, FAIL,
                       "seat states no `central_claim` it tested — a verdict with no claim under "
                       "it is not a review")
    endpoint = _endpoint(pub_id)
    doc = ((endpoint or {}).get("document") or {}).get("file")
    if not doc:
        return _clause("independent_adversarial_seat", label, UNVERIFIABLE,
                       f"{pub_id} has no document.file in publications.json")
    digest, why = _document_digest(sha, doc)
    if digest is None:
        return _clause("independent_adversarial_seat", label, UNVERIFIABLE, why)
    if record.get("document_sha256") != digest:
        return _clause("independent_adversarial_seat", label, FAIL,
                       f"seat carries no matching `document_sha256` for {doc} at {sha[:12]} — the "
                       "record is not bound to the text it reviewed")
    return _clause("independent_adversarial_seat", label, PASS,
                   f"blind seat on {sha[:12]}: supported, bound to {doc}")


def _renderer_registered_for(pub_id: str, sha: str, root: pathlib.Path) -> tuple[bool | None, str]:
    """Is there a `build_submission_pdf.PAPERS` entry that renders this publication's document, AS
    OF `sha`? `(None, why)` when it cannot be determined; otherwise `(bool, detail)`.

    ⛔ READ FROM THE MATERIALISED TREE, NOT THE LIVE MODULE. A paper registered in `PAPERS` after
    `sha` was posted would make a past post look retroactively sound, which is the same class of
    error `_tree_at` was built to close for clauses 3, 4 and 5.

    ⭐ DERIVED, NEVER A HAND-KEPT LIST OF WHICH PAPERS ARE BUILDABLE (CLAUDE.md §1). `PAPERS` values
    already carry the one fact this needs — `manuscript`, a path relative to `research/manuscripts/`
    — so the comparison is against that field itself, not a copy of it kept here.
    """
    endpoint = _endpoint(pub_id)
    doc = ((endpoint or {}).get("document") or {}).get("file")
    if not doc:
        return None, f"{pub_id} has no document.file in publications.json"
    script = root / "research" / "manuscripts" / "build_submission_pdf.py"
    if not script.exists():
        return None, f"build_submission_pdf.py does not exist at {sha[:12]}"
    probe = (
        "import importlib.util, json, sys\n"
        f"spec = importlib.util.spec_from_file_location('_probe_papers', {str(script)!r})\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(m)\n"
        "print(json.dumps([v.get('manuscript') for v in m.PAPERS.values()]))\n"
    )
    try:
        proc = subprocess.run([sys.executable, "-c", probe],
                              capture_output=True, text=True, timeout=60, cwd=str(root))
    except Exception as exc:
        return None, f"could not read build_submission_pdf.PAPERS ({type(exc).__name__})"
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return None, f"build_submission_pdf.py failed to import at {sha[:12]}: {tail[-1] if tail else '—'}"
    try:
        manuscripts = json.loads(proc.stdout.strip())
    except Exception:
        return None, "build_submission_pdf.PAPERS did not print valid JSON"
    prefix = "research/manuscripts/"
    if not doc.startswith(prefix):
        return False, f"{doc} is not under {prefix}, so no PAPERS entry names it"
    rel = doc[len(prefix):]
    return (rel in manuscripts), rel


def clause_8_deliverable_is_buildable(pub_id: str, sha: str) -> dict:
    """⛔⛔ THE CLAUSE THAT DID NOT EXIST WHEN `publish_bar` RETURNED MAY POST (7/7) FOR A PAPER WITH
    NO POSTABLE ARTIFACT (AUT-PD-213). Every other clause grades the MANUSCRIPT; `scripts/aixiv_review.py
    submit` requires `--pdf`, and nothing until now asked whether that PDF can be produced at all.
    `deliverable_digest`'s set is the manuscript alone when no rendering exists, so every earlier
    clause is fully satisfiable over a document nobody could ever post — the bar authorising an act
    it has no way to perform.

    ⛔ FAILS CLOSED, exactly like every other clause here: no document, no renderer script, an
    unregistered manuscript, or a crashed import are all FAIL/UNVERIFIABLE, never a silent pass.
    Registering a paper's typesetting in `build_submission_pdf.PAPERS` is a separate, per-paper
    decision (geometry, house style, journal vs. preprint layout) that this clause does not make —
    it only refuses to certify an artifact that cannot exist.
    """
    label = "the deliverable has a registered renderer"
    with _tree_at(sha) as (root, err):
        if root is None:
            return _clause("deliverable_is_buildable", label, UNVERIFIABLE, err)
        registered, detail = _renderer_registered_for(pub_id, sha, root)
        if registered is None:
            return _clause("deliverable_is_buildable", label, UNVERIFIABLE, detail)
        if not registered:
            return _clause("deliverable_is_buildable", label, FAIL,
                           f"no entry in build_submission_pdf.PAPERS builds {detail!r} at "
                           f"{sha[:12]} — the manuscript exists but nothing can render the artifact "
                           "a submit act needs; register it in PAPERS before this bar may pass")
        return _clause("deliverable_is_buildable", label, PASS,
                       f"build_submission_pdf.PAPERS builds {detail!r} at {sha[:12]}")


CLAUSES = (
    clause_1_hardening_converged,
    clause_2_preflight_full_green,
    clause_3_claim_ceiling_honoured,
    clause_4_identifiers_resolvable,
    clause_5_endpoint_declared,
    clause_6_independent_adversarial_seat,
    clause_7_readable_enough_to_review,
    clause_8_deliverable_is_buildable,
)


# ---------------------------------------------------------------- the authority check


def authority_permits(pub_id: str, venue: str, act: str) -> dict:
    """The grant is bar-scoped (D1), but it is still a grant with edges. This checks the edges.

    ⛔ `journal` is not a parameter and no bar reaches it. If this function ever returns True for a
    journal, the amendment that did it is the bug.
    """
    authority, err = _read_json(AUTHORITY_FILE)
    if authority is None:
        return {"ok": False, "why": err + " — no authority file means no authority"}
    if venue == "journal":
        return {"ok": False, "why": "journal submission always escalates (D4); no bar reaches it"}
    if venue != "aixiv":
        return {"ok": False, "why": f"venue {venue!r} was never granted — the grant is aiXiv only"}
    aixiv = authority.get("aixiv") or {}
    if not aixiv.get("standing_grant"):
        return {"ok": False, "why": "standing_grant is not true"}
    scope = aixiv.get("scope") or {}
    if act not in scope.get("acts", []):
        return {"ok": False, "why": f"act {act!r} is outside the granted scope"}
    # ⛔ THE DENY-LIST IS CHECKED BEFORE ANY POST, AND IT IS CHECKED HERE BECAUSE THIS IS THE ONE
    # FUNCTION EVERY OUTWARD PATH GOES THROUGH. trimcrae, 2026-08-27: "That's the only paper that
    # shouldn't auto ship to aiXiv." PUB-ASO lives on Qeios with a DOI and a version history he
    # controls; a second public home posted by the loop would fragment one work into two version
    # histories under his ORCID.
    # ⚠ RECORDED IS NOT ENFORCED. This repository has already paid for that exact gap once —
    # `subagent_width` was defined in JSON, asserted by one test, and read by NO code, so compliance
    # was luck (CLAUDE.md §1). An exclusion that lived only in publication-authority.json would be
    # the same shape: true, documented, and governing nothing.
    excluded = (scope.get("excluded_papers") or {}).get(pub_id)
    if excluded and act in (excluded.get("excluded_from") or []):
        return {"ok": False,
                "why": (f"{pub_id} is excluded from the aiXiv grant for {act!r} — "
                        f"{str(excluded.get('why'))[:160]}")}

    # ⛔⛔ THE VERSION CAP, WHICH THIS FILE DECLARED AND NEVER READ. `scope.max_versions_per_paper`
    # has been 3 since the grant was written, with the measurement beside it: eleven versions of
    # `aixiv.260822.000005` never moved its rating above 6 and it trended DOWN as the paper improved.
    # ⚠ MEASURED 2026-09-02, and it is the `subagent_width` shape a third time: `grep -rn
    # max_versions_per_paper` found the JSON that defines it, one architecture mention, and one test
    # asserting it is `>= 1`. NO CODE READ IT, and this function returned ok=True for
    # `new_version` on a paper carrying ELEVEN posted versions against a cap of three.
    # ⛔ IT GATES `submit` TOO, and that is not scope creep. The cap counts VERSIONS OF A PAPER, and
    # a second `submit` of an already-posted paper adds one exactly as `new_version` does. For a
    # paper with no postings the count is 0, so nothing about a first post changes.
    cap = scope.get("max_versions_per_paper")
    if not isinstance(cap, int) or isinstance(cap, bool) or cap < 1:
        return {"ok": False,
                "why": (f"`scope.max_versions_per_paper` is {cap!r}, not a positive integer, so the "
                        "version cap cannot be read — and a cap this function cannot establish is "
                        "not permission")}
    posted = _pr.versions_posted(pub_id)
    if not posted["ok"]:
        return {"ok": False,
                "why": (f"how many versions of {pub_id} are already on aiXiv cannot be established, "
                        f"so the cap of {cap} cannot be checked: {posted['why']}")}
    if posted["count"] >= cap:
        return {"ok": False,
                "why": (f"{pub_id} already carries {posted['count']} posted version(s) on aiXiv "
                        f"against `max_versions_per_paper` = {cap}. "
                        f"{str(scope.get('_max_versions_why'))[:200]}")}
    return {"ok": True,
            "why": (f"granted: {aixiv.get('granted_by')} — {posted['count']} of {cap} version(s) "
                    "used")}


def evaluate(pub_id: str, sha: str, venue: str = "aixiv", act: str = "submit") -> dict:
    clauses = [fn(pub_id, sha) for fn in CLAUSES]
    grant = authority_permits(pub_id, venue, act)
    all_clauses_pass = all(c["ok"] for c in clauses)
    return {
        "paper": pub_id,
        "commit": sha,
        "venue": venue,
        "act": act,
        "clauses": clauses,
        "authority": grant,
        "may_post": bool(all_clauses_pass and grant["ok"]),
        "n_passed": sum(1 for c in clauses if c["ok"]),
        "n_clauses": len(clauses),
        "_fail_closed": (
            "UNVERIFIABLE and FAIL both block. They differ only in what to do next: go get the "
            "evidence, or stop. Neither is ever treated as a pass."
        ),
    }


def _render(result: dict) -> str:
    lines = [f"{result['paper']} @ {result['commit'][:12]} -> "
             f"{'MAY POST' if result['may_post'] else 'BLOCKED'} "
             f"({result['n_passed']}/{result['n_clauses']} clauses)"]
    for clause in result["clauses"]:
        mark = "OK  " if clause["ok"] else ("FAIL" if clause["verdict"] == FAIL else "????")
        lines.append(f"  [{mark}] {clause['label']}")
        lines.append(f"         {clause['evidence']}")
    lines.append(f"  authority: {'OK' if result['authority']['ok'] else 'NO'} — "
                 f"{result['authority']['why']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--paper", help="publication endpoint id, e.g. PUB-ASO")
    parser.add_argument("--all", action="store_true", help="evaluate every endpoint")
    parser.add_argument("--sha", required=True, help="the commit being posted")
    parser.add_argument("--venue", default="aixiv", choices=["aixiv", "journal"])
    parser.add_argument("--act", default="submit", choices=["submit", "new_version"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.all:
        ids = [p["id"] for p in json.loads((GRAPH / "publications.json").read_text())]
    elif args.paper:
        ids = [args.paper]
    else:
        parser.error("give --paper or --all")

    results = [evaluate(i, args.sha, args.venue, args.act) for i in ids]
    if args.json:
        print(json.dumps(results if args.all else results[0], indent=2))
    else:
        print("\n\n".join(_render(r) for r in results))
    return 0 if all(r["may_post"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
