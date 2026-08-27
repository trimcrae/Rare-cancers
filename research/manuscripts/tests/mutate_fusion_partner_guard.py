#!/usr/bin/env python3
"""Mutation-test the fusion-partner prose-vs-artifact guard: does each binding actually FIRE?

⛔⛔ WHY THIS EXISTS — A GUARD NOBODY MUTATED IS A GUARD NOBODY MEASURED.
`test_fusion_partner_prose_matches_its_artifact.py` carries a docstring reporting "36 of 36
mutations caught, 22 of them SINGLE-SITE" for the bindings written on 2026-08-26. That run was
ad hoc: no harness was committed, so the nine bindings CYC-0011 added on 2026-08-27 had no way to
inherit the same evidence, and the receipt for that cycle had to say in as many words that they were
designed and not proven. This file is that harness, committed, so the claim is re-runnable rather
than remembered.

★ WHAT A PASSING RUN PROVES, AND WHAT IT DOES NOT.
It proves that changing one number in the manuscript makes the guard RED — i.e. that the binding
reaches that site and compares something. It does NOT prove the binding compares the right thing:
a binding that captured a figure and compared it to itself would survive every mutation here. That
is what reading the binding is for. Coverage is measurable; correctness is read.

⛔ THE THREE FAILURE MODES THIS HARNESS IS BUILT AGAINST, each of which has cost this repository a
real round:

  1. A MUTATION THAT NEVER LANDED reports exactly what a guard that never fired reports — green.
     So every mutation is asserted APPLIED, by digest change and by occurrence count, BEFORE the
     gate's answer is read. A mutation whose anchor no longer matches the prose is an ERROR here,
     never a pass.
  2. A MULTI-SITE FIGURE hides a broken binding: corrupt "46.7 %" everywhere and something will
     notice, but the defect that actually happens is one site drifting. Every mutation below is
     therefore anchored to a UNIQUE surrounding construction and is asserted to change exactly one
     occurrence.
  3. AN ARM SWAP leaves every digit in the document correct and still inverts the claim. Two of
     these mutations swap arms rather than corrupt values, because §3.3's local-recurrence sentence
     exists specifically to say the two cohorts run in OPPOSITE directions.

⚠ IT RUNS IN A GIT WORKTREE, NEVER THE WORKING TREE. The prior ad hoc run used a `cp -al` clone and
recorded that the shared inode carried a mutation back into the real tree — it cost a restore. A
worktree is a genuine separate checkout, so there is no inode to share and no restore to get wrong.

Usage:  python3 research/manuscripts/tests/mutate_fusion_partner_guard.py [--keep]
Exit 0 iff the positive control is GREEN and every mutation is RED.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DOC = os.path.join("research", "manuscripts", "fusion-partner",
                   "emc-fusion-partner-stratification.md")
TEST = os.path.join("research", "manuscripts", "tests",
                    "test_fusion_partner_prose_matches_its_artifact.py")

#: Each mutation is (label, anchor, mutated, binding_it_targets).
#:
#: `anchor` must occur EXACTLY ONCE in the document — that is what makes the mutation single-site,
#: and it is asserted rather than assumed. `mutated` replaces it. The point of every one of these is
#: that a human reader of the sentence would not notice, and the guard must.
MUTATIONS = [
    # ---- §3.1's secondary row and the range round 4 was forced to print into it -----------------
    ("3.1 row: pazopanib arm rate drifts one tenth",
     "per cohort **21.1 %** (pazopanib, 4/19)",
     "per cohort **21.2 %** (pazopanib, 4/19)",
     "§3.1's secondary-analysis table row, whole"),
    ("3.1 row: pazopanib denominator drifts",
     "(pazopanib, 4/19) and **75.0 %**",
     "(pazopanib, 4/18) and **75.0 %**",
     "§3.1's secondary row per-cohort range"),
    ("3.1 row: sunitinib arm rate drifts",
     "and **75.0 %** (sunitinib, 6/8), spread",
     "and **75.5 %** (sunitinib, 6/8), spread",
     "§3.1's secondary row per-cohort range"),
    ("3.1 row: the spread itself drifts",
     "(sunitinib, 6/8), spread **53.9 pts**",
     "(sunitinib, 6/8), spread **53.8 pts**",
     "§3.1's secondary row per-cohort range"),
    ("3.1 row: ARM SWAP — every digit correct, the two cohorts exchanged",
     "per cohort **21.1 %** (pazopanib, 4/19) and **75.0 %** (sunitinib, 6/8)",
     "per cohort **75.0 %** (pazopanib, 6/8) and **21.1 %** (sunitinib, 4/19)",
     "§3.1's secondary row per-cohort range"),

    # ---- Appendix A22's restatement of the same figures -----------------------------------------
    ("A22: the restated pazopanib rate drifts from the table it registers",
     "secondary pool averaged 21.1 % (pazopanib, 4/19)",
     "secondary pool averaged 21.0 % (pazopanib, 4/19)",
     "A22's restatement of the secondary-pool spread"),
    ("A22: the restated spread drifts",
     "into 10/27 = 37.0 %, a **53.9-point** spread",
     "into 10/27 = 37.0 %, a **53.7-point** spread",
     "A22's restatement of the secondary-pool spread"),

    # ---- §3.3's local-recurrence direction flip, the eight-group construction -------------------
    ("3.3 local recurrence: Agaram TAF15 numerator drifts",
     "Agaram gives 2/7 = 28.6 % TAF15",
     "Agaram gives 3/7 = 28.6 % TAF15",
     "§3.3's local-recurrence per-cohort rates"),
    ("3.3 local recurrence: Agaram EWSR1 rate drifts",
     "against 1/16 = 6.2 %\nEWSR1; Huang",
     "against 1/16 = 6.3 %\nEWSR1; Huang",
     "§3.3's local-recurrence per-cohort rates"),
    ("3.3 local recurrence: Huang TAF15 rate drifts",
     "Huang gives 2/8 = 25.0 %",
     "Huang gives 2/8 = 25.5 %",
     "§3.3's local-recurrence per-cohort rates"),
    ("3.3 local recurrence: Huang EWSR1 denominator drifts",
     "against 12/42 = 28.6 %",
     "against 12/43 = 28.6 %",
     "§3.3's local-recurrence per-cohort rates"),
    ("3.3 local recurrence: ARM SWAP inside Huang — the direction flip inverted, digits intact",
     "Huang gives 2/8 = 25.0 % against 12/42 = 28.6 %",
     "Huang gives 12/42 = 28.6 % against 2/8 = 25.0 %",
     "§3.3's local-recurrence per-cohort rates"),
    ("A22: the local-recurrence comparator spread drifts",
     "against 28.6 % (Huang), **22.4 points**",
     "against 28.6 % (Huang), **22.5 points**",
     "A22's local-recurrence comparator spread"),

    # ---- §2.5's two named spreads --------------------------------------------------------------
    ("2.5: the secondary-pool spread drifts where the bullet names it",
     "the secondary TKI pool (spread 53.9 points)",
     "the secondary TKI pool (spread 53.6 points)",
     "§2.5's two named spreads"),
    ("2.5: the local-recurrence spread drifts where the bullet names it",
     "arm, 22.4 points). Two blind adversarial seats",
     "arm, 22.1 points). Two blind adversarial seats",
     "§2.5's two named spreads"),

    # ---- §3.5's Sjögren counterfactual, which is DERIVED and must not become typed --------------
    ("3.5: Sjögren's own TAF15 share drifts",
     "it sits above it.** Sjögren 2003 is 3/9 = **33.3 %** TAF15 at patient level, above\nAgaram",
     "it sits above it.** Sjögren 2003 is 3/9 = **33.5 %** TAF15 at patient level, above\nAgaram",
     "§3.5's Sjögren counterfactual"),
    ("A28: the pooled cohort Sjögren is said to exceed drifts",
     "TAF15 at patient level, above Agaram's 29.2 %",
     "TAF15 at patient level, above Agaram's 29.4 %",
     "§3.5's Sjögren counterfactual"),
    ("3.5: the counterfactual pool drifts",
     "Pooling it would give **31/163 = 19.0 %**",
     "Pooling it would give **31/163 = 19.1 %**",
     "the counterfactual pool, both sites"),
    ("A28: the counterfactual pool drifts at its SECOND site only",
     "pooling it would give **31/163 = 19.0 %** and widen",
     "pooling it would give **32/163 = 19.0 %** and widen",
     "the counterfactual pool, both sites"),

    # ---- A4's high-grade share, restated twice by round 4 ---------------------------------------
    ("4.1a: A4's high-grade share drifts at round 4's first restatement",
     "Appendix A4 records its 80 % high-grade variant group",
     "Appendix A4 records its 85 % high-grade variant group",
     "round 4's two restatements of A4's high-grade share"),
    ("A23: A4's high-grade share drifts at round 4's second restatement",
     "A4 records its 80 % high-grade variant group. And §4.9",
     "A4 records its 88 % high-grade variant group. And §4.9",
     "round 4's two restatements of A4's high-grade share"),

    # ---- the figure PROMOTED from a declaration to a binding ------------------------------------
    ("4.7a: Huang's 78 % — promoted from declared to bound, so it must now fire",
     'size >10 cm (78%, P = .025)"*), so the defeater',
     'size >10 cm (79%, P = .025)"*), so the defeater',
     "Huang 2023's own abstract sentence (78 %)"),
    ("A27: the same figure at its second site",
     'size >10 cm (78%, P = .025)"* — so the defeater',
     'size >10 cm (77%, P = .025)"* — so the defeater',
     "Huang 2023's own abstract sentence (78 %)"),
    ("4.7a: the published p beside it drifts",
     '(78%, P = .025)"*), so the defeater',
     '(78%, P = .026)"*), so the defeater',
     "Huang 2023's own abstract sentence (78 %)"),
]


def _digest(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


#: ⛔ RESOLVED, NOT ASSUMED. `sys.executable -m pytest` is NOT a safe runner here: pytest is
#: installed for a different interpreter, and `python3 -m pytest` answers "No module named pytest"
#: with EXIT CODE 1 — the same code a genuinely failing test returns. The first run of this harness
#: read that as "the guard is red on an unmutated tree" and stopped, which is the positive control
#: doing its job on the harness rather than on the guard. A missing runner must never be readable as
#: a test result.
PYTEST = shutil.which("pytest")


def _run_guard(tree):
    """The guard's verdict in `tree`: True = green.

    ⛔ A RETURN CODE ALONE IS NOT AN ANSWER. pytest exits 1 for a failing test, for a collection
    error, and (via `-m`) for not being installed at all. So the verdict is accepted only when the
    output carries a pytest summary naming passed and/or failed tests; anything else is raised as an
    unusable run rather than reported as red.
    """
    if not PYTEST:
        raise SystemExit("no `pytest` on PATH — this harness cannot run and will not guess.")
    r = subprocess.run([PYTEST, TEST, "-q", "--no-header", "-x"],
                       cwd=tree, capture_output=True, text=True)
    out = r.stdout + r.stderr
    if not re.search(r"\d+ (?:passed|failed|error)", out):
        raise SystemExit(f"the guard could not run in {tree} (exit {r.returncode}); no pytest "
                         f"summary in the output, so this is not a verdict:\n{out[-3000:]}")
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="leave the worktree in place for inspection")
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="fp-mutate-")
    tree = os.path.join(tmp, "wt")
    subprocess.run(["git", "worktree", "add", "--detach", tree, "HEAD"],
                   cwd=REPO, check=True, capture_output=True)
    doc = os.path.join(tree, DOC)
    try:
        pristine = io.open(doc, encoding="utf-8").read()
        base_digest = _digest(doc)

        # ⛔ THE POSITIVE CONTROL RUNS FIRST. A harness that reports every mutation caught while the
        # unmutated tree is ALSO red has measured nothing at all.
        if not _run_guard(tree):
            raise SystemExit("POSITIVE CONTROL FAILED: the guard is red on an unmutated tree, so no "
                             "mutation result below would mean anything. Fix that first.")
        print(f"positive control: GREEN on unmutated HEAD ({len(MUTATIONS)} mutations to run)\n")

        survived, errors = [], []
        for label, anchor, mutated, targets in MUTATIONS:
            n = pristine.count(anchor)
            if n != 1:
                errors.append(f"{label}: anchor occurs {n} times, not once — the mutation is not "
                              f"single-site and its result would be unreadable")
                continue
            io.open(doc, "w", encoding="utf-8").write(pristine.replace(anchor, mutated))
            if _digest(doc) == base_digest:
                errors.append(f"{label}: MUTATION DID NOT LAND (digest unchanged)")
                io.open(doc, "w", encoding="utf-8").write(pristine)
                continue
            green = _run_guard(tree)
            io.open(doc, "w", encoding="utf-8").write(pristine)
            assert _digest(doc) == base_digest, "failed to restore the worktree between mutations"
            print(f"  {'⛔ SURVIVED' if green else '✅ caught  '}  {label}")
            if green:
                survived.append(f"{label}  [targets: {targets}]")

        print()
        if errors:
            print("⛔ HARNESS ERRORS — these are not results, they are un-run mutations:")
            for e in errors:
                print(f"  {e}")
        if survived:
            print(f"⛔ {len(survived)} MUTATION(S) SURVIVED — a binding does not reach these sites:")
            for s in survived:
                print(f"  {s}")
        if errors or survived:
            return 1
        print(f"✅ {len(MUTATIONS)}/{len(MUTATIONS)} mutations caught, every one single-site, "
              f"positive control green.")
        return 0
    finally:
        if args.keep:
            print(f"\nworktree kept at {tree}")
        else:
            subprocess.run(["git", "worktree", "remove", "--force", tree],
                           cwd=REPO, capture_output=True)
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
