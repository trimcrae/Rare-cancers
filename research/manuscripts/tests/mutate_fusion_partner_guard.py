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

    # =============================================================================================
    # THE STATISTICAL-NOTATION FAMILY (section F of the guard), added 2026-08-27 by CYC-0013.
    #
    # ⛔ THESE BINDINGS EXIST BECAUSE A CENSUS WAS BLIND, SO THEIR MUTATIONS MATTER MORE THAN MOST.
    # The first census read fractions and rates only; every figure below was inside the manuscript,
    # outside every instrument, and reported as fully covered. A binding written to close that gap
    # and never mutated would reproduce the exact state it was written to end.
    # =============================================================================================

    # ---- F.1 · cohort sizes ---------------------------------------------------------------------
    ("3.2: the sunitinib series size the two-case report is contained in drifts",
     "contained in the n = 10 series",
     "contained in the n = 11 series",
     "the sunitinib series size, at the row explaining what the two-case report is contained in"),
    ("3.2: Paioli's size drifts at the exclusion row",
     "Paioli 2021 (Italian Sarcoma Group), n = 67",
     "Paioli 2021 (Italian Sarcoma Group), n = 66",
     "Paioli's size at §3.2's exclusion row"),
    ("4.1a: Paioli's size drifts where the third independent test is named",
     "**Paioli 2021** (PMID 32572850, n = 67, Italian Sarcoma Group)",
     "**Paioli 2021** (PMID 32572850, n = 68, Italian Sarcoma Group)",
     "Paioli's size where §4.1a names the third independent test"),
    ("§6: Paioli's size drifts at the closed-full-text row",
     "DFS/DMFS p-values, n = 67",
     "DFS/DMFS p-values, n = 65",
     "Paioli's size at the closed-full-text row that says what is behind its p-values"),
    ("3.2: Llombart-Bosch's size drifts",
     "Bosch 2022 congress abstract (n = 31)",
     "Bosch 2022 congress abstract (n = 30)",
     "Llombart-Bosch's size at §3.2's exclusion row"),
    ("3.2: Klubíčková's size drifts",
     "čková 2022 congress abstract (n = 11)",
     "čková 2022 congress abstract (n = 12)",
     "Klubíčková's size at §3.2's exclusion row"),
    ("4.1a: Huang's size drifts where it is named the third failing series",
     "**Huang 2023** (PMID 36948401, n = 58, Taiwan)",
     "**Huang 2023** (PMID 36948401, n = 57, Taiwan)",
     "Huang's size where §4.1a names it the third series failing to establish the partner"),

    # ---- F.2 · published and post-hoc p-values ---------------------------------------------------
    ("4.7a: the metastasis predictor's p drifts at ONE of the two verbatim quotations",
     'metastasis at presentation (P = .032) remained prognostically independent"*;',
     'metastasis at presentation (P = .033) remained prognostically independent"*;',
     "Huang's two independent predictors, at the two sites that quote the source verbatim"),
    ("A27: the same predictor's p drifts at the OTHER quotation — the one-of-a-pair case",
     'metastasis at presentation (P = .032) remained prognostically independent"* and',
     'metastasis at presentation (P = .031) remained prognostically independent"* and',
     "Huang's two independent predictors, at the two sites that quote the source verbatim"),
    ("4.7a: ARM SWAP — both p-values present and correct, the two covariates exchanged",
     '*"only size >10 cm (P = .004) and\nmetastasis at presentation (P = .032) remained '
     'prognostically independent"*;',
     '*"only size >10 cm (P = .032) and\nmetastasis at presentation (P = .004) remained '
     'prognostically independent"*;',
     "Huang's two independent predictors, at the two sites that quote the source verbatim"),
    ("§5: the published three-way metastasis p drifts — the site carrying the whole negative",
     "directly reports P = .728. **That is a",
     "directly reports P = .729. **That is a",
     "Huang's published three-way metastasis p, at the §5 site that states the negative"),
    ("4.1a: Paioli's DMFS p drifts inside the three-value construction",
     "(p = 0.08) and DMFS (p = 0.09), in the same analysis where **size reaches p = 0.004**",
     "(p = 0.08) and DMFS (p = 0.10), in the same analysis where **size reaches p = 0.004**",
     "Paioli's three published p-values as §4.1a states them, in order"),
    ("4.1a: ARM SWAP — Paioli's DFS and DMFS p-values exchanged, both digits still on the page",
     "(p = 0.08) and DMFS (p = 0.09), in the same analysis where **size reaches p = 0.004**",
     "(p = 0.09) and DMFS (p = 0.08), in the same analysis where **size reaches p = 0.004**",
     "Paioli's three published p-values as §4.1a states them, in order"),
    ("A17: Paioli's size p drifts at the appendix restatement",
     "(DFS p = 0.08, DMFS p = 0.09) while size does (p = 0.004)",
     "(DFS p = 0.08, DMFS p = 0.09) while size does (p = 0.005)",
     "Paioli's same three p-values at the appendix restatement"),
    ("3.3: Paioli's DMFS p drifts at the time-to-event corroboration",
     "agrees that nothing is established: DMFS p = 0.09.",
     "agrees that nothing is established: DMFS p = 0.08.",
     "Paioli's DMFS p where §3.3 uses it as the time-to-event corroboration"),
    ("A: the pooled Fisher p drifts where the appendix records it becoming the headline",
     "§3.3's headline became p = 0.0034",
     "§3.3's headline became p = 0.0035",
     "the pooled Fisher p at the appendix site recording when it became the headline"),

    # ---- F.3 · measurements ----------------------------------------------------------------------
    ("Abstract: the size threshold drifts at ONE of its fifteen sites",
     "78 % of TAF15 tumours were > 10 cm. Local recurrence",
     "78 % of TAF15 tumours were > 12 cm. Local recurrence",
     "the size threshold, at every site that prints it"),
    ("4.7b: the threshold drifts inside a verbatim quotation of the source's factor list",
     'names five factors — *"Size >10 cm',
     'names five factors — *"Size >15 cm',
     "the size threshold, at every site that prints it"),
    ("A: the threshold drifts at the appendix restatement of the same factor list",
     'mes **five** factors — *"Size >10 cm',
     'mes **five** factors — *"Size >20 cm',
     "the size threshold, at every site that prints it"),
    ("4.11: Agaram's follow-up range drifts at the wrapped site",
     "follow-up range\n(2–99 months)",
     "follow-up range\n(2–98 months)",
     "Agaram's published follow-up range, at both sites establishing it publishes no accrual "
     "window"),
    ("A: Agaram's follow-up range drifts at the appendix site — one of a pair again",
     "only a follow-up range (2–99 months)",
     "only a follow-up range (3–99 months)",
     "Agaram's published follow-up range, at both sites establishing it publishes no accrual "
     "window"),

    # ---- F.4 · the census itself ------------------------------------------------------------------
    # ⭐ THE ONE MUTATION THAT TARGETS NO BINDING. It adds a statistical quantity that no binding
    # reads and no declaration covers, which is the defect the second census exists to catch — and
    # the only way to prove the census FIRES rather than merely passing.
    ("census: an unbound cohort size is written into the prose",
     "The full inclusion table is §3.2.",
     "The full inclusion table is §3.2 (n = 99).",
     "test_every_statistical_quantity_is_bound_or_declared"),

    # ---- G · THE IDENTIFIER CENSUS (2026-08-27) --------------------------------------------------
    # ⛔ EVERY ONE OF THESE LEAVES A REAL, ANCHORED, CORRECTLY-FORMATTED IDENTIFIER ON THE PAGE.
    # `lint_citations` is green on all ten — it asks whether an identifier appears in some tracked
    # JSON, which is provenance, and none of these invents one out of thin air except where noted.
    # What they break is ATTACHMENT: which paper the identifier is printed against.
    ("ref [8]: Huang's PMID replaced by Lenz's — both real, both anchored, the paper wrong",
     "*Mod Pathol* 2023;36:100161. PMID 36948401.",
     "*Mod Pathol* 2023;36:100161. PMID 36563884.",
     "the reference-entry and title identifier tests"),
    ("ref [9]: Paioli's DOI replaced by Brenca's",
     "*Ann Surg Oncol* 2021;28:1142–50. PMID 32572850. doi:10.1245/s10434-020-08737-7",
     "*Ann Surg Oncol* 2021;28:1142–50. PMID 32572850. doi:10.1002/path.5284",
     "the reference-entry and title identifier tests"),
    # ⭐ THE ONE THAT JUSTIFIES THE TITLE TEST EXISTING. Both identifiers in the entry become Davis
    # 2017's, so the entry stays INTERNALLY CONSISTENT and the grouping test cannot see it. Measured:
    # this fires the title test and nothing else.
    ("ref [11]: WHOLE-ENTRY SWAP — Brenca's entry carries Davis 2017's pair, internally consistent",
     "PMID 31020999 · PMC6766969. doi:10.1002/path.5284",
     "PMID 28423517 · PMC6766969. doi:10.18632/oncotarget.15568",
     "the title identifier test ONLY — the entry test cannot see this"),
    ("in-text: Agaram's PMID gains a digit, an identifier owned by nobody",
     "(Agaram 2014, PMID 24746215;",
     "(Agaram 2014, PMID 24746216;",
     "the identifier ownership census"),
    ("ref [4]: one digit of Stacchiotti 2020's DOI",
     "doi:10.3390/cancers12092703",
     "doi:10.3390/cancers12092704",
     "the identifier ownership census"),
    ("abstract: the trial registration drifts one digit",
     "phase 2 trial NCT02066285 (PMID 31331701)",
     "phase 2 trial NCT02066286 (PMID 31331701)",
     "the identifier ownership census"),
    # ⭐ A DECLARATION IS VALUE-SPECIFIC, NOT AN AMNESTY FOR A NOTATION. The erratum PMID is declared
    # not-pooled; change the digits and it is a different unowned identifier, and both the census and
    # the dead-declaration test must say so.
    ("ref [3]: the DECLARED erratum PMID becomes a different number",
     "e559, PMID 31579002)",
     "e559, PMID 31579003)",
     "the ownership census and the dead-declaration test"),
    ("3.2 ARM SWAP: Huang's bullet carries Paioli's PMID",
     "**Huang 2023** (PMID 36948401, n = 58, Taiwan)",
     "**Huang 2023** (PMID 32572850, n = 58, Taiwan)",
     "the name-attachment test"),
    ("3.2 ARM SWAP, the other arm: Paioli's bullet carries Huang's PMID",
     "**Paioli 2021** (PMID 32572850, n = 67",
     "**Paioli 2021** (PMID 36948401, n = 67",
     "the name-attachment test"),
    # ⭐ THE EXCLUSIVE EVIDENCE FOR THE NAME-ATTACHMENT TEST. The two arm swaps above also trip
    # bindings that happen to capture text around those bullets; this one fires the new test and
    # nothing else, which is what makes it evidence rather than a coincidence.
    ("3.7 table: Suemitsu's PMID and DOI both replaced by Bangerter's",
     "Suemitsu 2025 (MSK, n = 18, PMID 40828003, doi 10.1002/gcc.70076)",
     "Suemitsu 2025 (MSK, n = 18, PMID 36316541, doi 10.1007/s13577-022-00818-x)",
     "the name-attachment test"),
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
