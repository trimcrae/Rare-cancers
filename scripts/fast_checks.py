#!/usr/bin/env python3
"""THE FAST SIX — the six fast document-and-registry checks, NAMED and EXECUTABLE. ($0, pure stdlib)

⛔ WHY THIS EXISTS (roadmap §10.1a `Q21`). The phrase *"the fast six"* was quoted as a VERIFICATION LINE
in `three-row-audit-2026-08-03.md` -- a row reading `| the fast six | **6/6 PASS** |` -- and the phrase
had **no definition anywhere in this repository**. Two days later `r3-site-choice-audit-2026-08-03.md`
recorded exactly that, in its own verification table: *"'the fast six' has no definition anywhere in this
repo ... Naming the six is a $0 fix somebody should make, because a verification line nobody can reproduce
is not a verification line."* Nobody made it. This is it.

⚠⚠ THE HONEST PART FIRST: THE ORIGINAL REFERENT IS NOT RECOVERABLE, AND THIS DOES NOT CLAIM TO BE IT.
The obvious guess -- "the six gates of `scripts/preflight.sh`" -- is **measurably wrong for the date the
phrase was used**. `preflight.sh`'s own comments date its growth: `systems_check` was "ADDED 2026-08-05"
and `emc_systems_map_check` "ADDED 2026-08-06", and the 2026-08-05 comment says the script "did not run
systems_check or parser_guard at all". So on **2026-08-03**, the day `| the fast six | 6/6 PASS |` was
written, preflight did not have six gates. Whatever set the author ran, it was not this one and it was
not preflight's. **That `6/6 PASS` therefore cannot be reproduced by anyone, including its author, and
must not be read as a pass of the set below.** Both audit documents now say so at the line itself.

★ SO THIS DEFINES THE PHRASE GOING FORWARD RATHER THAN RECONSTRUCTING IT, and it defines it by a
MEMBERSHIP RULE rather than by a list, so the number is checked instead of remembered:

    A member of the fast six is a check that
      (a) is stdlib-only Python -- no scientific dependency, so it runs anywhere including this sandbox;
      (b) completes in seconds over the WHOLE repository;
      (c) fails on an inconsistency BETWEEN DOCUMENTS, GRAPHS OR REGISTRIES -- not on a computation; and
      (d) is the kind of check a prose or JSON change must clear before it is committed.

⛔ AND THE EXCLUSIONS ARE STATED, BECAUSE AN UNSTATED EXCLUSION IS HOW A COUNT DRIFTS. Every fast checker
in the repository that is NOT a member is listed in `EXCLUDED` below with the clause it fails. A check
that satisfies (a)-(d) and is missing from `MEMBERS` is a bug in this file, and
`tests/test_fast_checks.py` is what makes that consequential: it fails if the count moves without this
file moving with it.

⭐ THE SET IS NOT `preflight.sh`, AND THE DIFFERENCE IS THE POINT -- BUT THE DIFFERENCE HAS NARROWED,
AND HALF OF WHAT THIS PARAGRAPH SAID IS NOW FALSE. It read that `lint_claims.py` is a member and is
**not** a preflight gate, quoting a CLAUDE.md §7 sentence -- *"`lint_claims.py` is NOT in preflight -- it
runs only in CI, so a green preflight does not mean the language rules passed."* -- that CLAUDE.md has
since retired. Measured 2026-08-28 against `scripts/preflight.sh`: `lint_claims.py` IS invoked, on lines
571 and 574, as its own gate. Preflight is no longer blind to the language rules, and this set no longer
closes that half of the gap.

⭐ WHAT IS STILL TRUE, AND IT IS WHY THE SET SURVIVES: `line_citations.py` IS STILL NOT A PREFLIGHT GATE.
It appears in `preflight.sh` exactly once, on line 701, INSIDE A COMMENT recounting a past incident --
zero invocations. A green preflight therefore still says nothing about drifted line citations, and this
set is what closes that. Preflight's `pytest` gate -- neither fast nor a document check -- is still not
in it. Run BOTH; neither contains the other.

⛔ AND THE STALENESS TRIPWIRE THAT CAUGHT THIS COULD NOT TELL RUNNING FROM MENTIONING, WHICH IS WHY IT
FIRED ON A HALF-TRUTH. `tests/test_fast_checks.py::test_the_two_checks_preflight_does_not_run_are_members`
tested the claim by substring over the WHOLE of `preflight.sh`, comments included, so the moment somebody
wrote a comment naming `line_citations.py` the guard announced that preflight now ran it. It does not, and
never did; `main` was red on that announcement. Presence is not provenance (CLAUDE.md §4), and a shell
comment is presence. The tripwire now reads INVOCATIONS -- non-comment lines only -- and it reads them
against `ALSO_A_PREFLIGHT_GATE` below rather than against this prose, so the fact has one home.

Usage:
    python3 scripts/fast_checks.py            # run all six, print N/6, exit non-zero on any failure
    python3 scripts/fast_checks.py --list     # print the definition and the members, run nothing
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: The six. `name` is what a verification line should say; `cmd` is what it means.
MEMBERS = (
    ("cross-document numeric consistency",
     ["python3", "research/manuscripts/lint_consistency.py"],
     "one fact, one place -- every pinned figure agrees across every file that carries it"),
    ("manuscript language discipline",
     ["python3", "research/manuscripts/lint_claims.py"],
     "R1-R5: no implied proteome-wide selectivity, efficacy, safety, window or clinical readiness. "
     "⚠ NOT a preflight gate -- this is the one CLAUDE.md §7 warns a green preflight does not cover"),
    ("roadmap line citations resolve",
     ["python3", "research/manuscripts/line_citations.py"],
     "a `:NNNN` citation into the paper still points at the sentence it quotes. ⚠ Also not in preflight; "
     "all 39 were measured stale on 2026-08-06"),
    ("EMC systems map invariants",
     ["python3", "research/manuscripts/emc_systems_map_check.py", "--check"],
     "disputed cell-line identities classified, claim artifacts not stubs, generated view not drifted -- "
     "one of the two MEDICAL-INTEGRITY checks"),
    ("systems model invariants + view drift",
     ["python3", "systems/systems_check.py", "--check"],
     "the other provenance check: no failing instrument cited as SUPPORT, no permanent blocker claiming a "
     "technology, no hand-edited generated view"),
    ("parser guard",
     ["python3", "systems/parser_guard.py"],
     "every registered parser can still FIND its input -- the guard against a scanner that succeeds while "
     "finding nothing"),
)

#: ⛔ EVERY OTHER FAST CHECKER IN THE REPO, AND THE CLAUSE IT FAILS. Enumerated so that "six" is a
#: consequence of the rule rather than a number somebody liked.
EXCLUDED = (
    ("scripts/validate-registry.mjs",
     "(a) -- Node, not stdlib Python. It IS covered: preflight gate 5 runs it, and it is the EMC clinical "
     "registry's evidence contract, so it is never skipped merely by being outside this set"),
    ("scripts/validate-research.mjs",
     "(a) -- Node. Validates research/hypotheses/candidates.json against METHODOLOGY.md"),
    ("research/modalities/lint_optional_input_guards.py",
     "(c)/(d) -- it parses workflow YAML and guards AUTOMATION shapes (a null `inputs` context switching a "
     "guard off), not documents. A prose change cannot break it"),
    ("research/modalities/lint_derived_thresholds.py",
     "(c)/(d) -- same: it guards a threshold typed as a multiple of a moving basis, in code"),
    ("pytest over research/modalities/tests",
     "(b) -- ~10 min in this sandbox, ~12 min in CI, and it needs numpy/rdkit/boto3, so it fails (a) too. "
     "It is preflight gate 6 and belongs there"),
    ("research/modalities/*_guard.py (abfe_xtag, artifact_stub, gcp_launch, stuck_run, vast_idle)",
     "(b)/(c) -- runtime guards over live jobs and object stores, not repository checks; several need "
     "credentials"),
)

EXPECTED_N = 6

#: ⛔ WHICH MEMBERS `scripts/preflight.sh` ALSO RUNS — DATA, NOT PROSE, BECAUSE THE PROSE WENT STALE AND
#: THE TEST THAT WATCHED IT COULD NOT TELL RUNNING FROM MENTIONING (2026-08-28; `main` red on the
#: difference). The value is whether preflight INVOKES the tool — whether it appears on a NON-COMMENT
#: line — never whether the string occurs in the file. `research/modalities/tests/test_fast_checks.py`
#: re-derives both sides from `preflight.sh` and fails naming whichever one moved, so this table and the
#: header paragraph above it cannot drift apart silently the way the header and reality just did.
#: ⭐ A `True` here does NOT retire the member: overlap is fine and the sets are allowed to intersect.
#: What it changes is the SET'S STATED REASON FOR EXISTING, which is the thing the tripwire guards.
ALSO_A_PREFLIGHT_GATE = {
    # invoked at preflight.sh:571 and :574 — added deliberately; see that gate's own comment for why.
    "lint_claims.py": True,
    # appears at preflight.sh:701 and ONLY there, inside a comment recounting an incident. Zero
    # invocations, so a green preflight still says nothing about drifted line citations.
    "line_citations.py": False,
}


def _run(cmd):
    t = time.time()
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, time.time() - t, (r.stdout or "") + (r.stderr or "")


def list_members():
    print("THE FAST SIX — %d fast document-and-registry checks" % len(MEMBERS))
    print()
    for i, (name, cmd, why) in enumerate(MEMBERS, 1):
        print("%d. %s" % (i, name))
        print("     %s" % " ".join(cmd))
        print("     %s" % why)
    print()
    print("EXCLUDED (fast checkers that are NOT members, and the clause each fails):")
    for path, why in EXCLUDED:
        print("  - %-72s %s" % (path, why))
    print()
    print("⚠ The 2026-08-03 `| the fast six | 6/6 PASS |` predates this definition and cannot be "
          "reproduced;\n  preflight did not have six gates on that date. See this file's header.")
    return 0


def main(argv):
    if "--list" in argv:
        return list_members()
    assert len(MEMBERS) == EXPECTED_N, (
        "the fast six has %d members. If a check was added or removed, change EXPECTED_N and the NAME in "
        "the same commit -- a set called 'six' with seven members is how a verification line stops meaning "
        "anything." % len(MEMBERS))
    failed = []
    for name, cmd, _why in MEMBERS:
        rc, secs, out = _run(cmd)
        print("%s %-42s %5.2fs  %s" % ("PASS" if rc == 0 else "FAIL", name, secs, " ".join(cmd)))
        if rc != 0:
            failed.append(name)
            tail = [l for l in out.strip().split("\n") if l.strip()][-6:]
            for l in tail:
                print("       | %s" % l[:200])
    print()
    print("the fast six: %d/%d PASS" % (len(MEMBERS) - len(failed), len(MEMBERS)))
    if failed:
        print("FAILED: %s" % ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
