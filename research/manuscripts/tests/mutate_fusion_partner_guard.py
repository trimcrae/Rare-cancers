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

⭐ TWO GUARD MODULES SINCE 2026-08-28, RUN SEPARATELY, AND THE OUTPUT SAYS WHICH ONE FIRED.
The synthesis's claims have a QUANTITY half and a RELATION half, and each has its own guard. Running
them in one invocation would answer "something went red", which scores a mutation and cannot support
the claim this harness now has to support — that a given binding reaches a given site. Every result
line carries `[numbers]`, `[relations]` or `[numbers+relations]`.

⛔ AND IT CAN MEASURE UNCOMMITTED WORK, WHICH IT COULD NOT BEFORE. `--working-tree` copies the
uncommitted changes into the clone before measuring. Without it the clone is HEAD, and a guard
written in this session is measured in a tree that does not contain it: the quantity guard's own
docstring records that failure — 20 of 21 mutations "survived" for exactly that reason. The mode is
printed with the result, because "N of N caught" means something different in each.

Usage:  python3 research/manuscripts/tests/mutate_fusion_partner_guard.py [--keep] [--working-tree]
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
# ⛔ TWO DOCUMENTS SINCE ROUND 8, AND EACH MUTATION GOES TO WHICHEVER ONE HOLDS ITS ANCHOR.
# Round 8 moved the correction register out of the manuscript's Appendix A into its own file. This
# harness mutated ONE document, so 15 committed mutations — every appendix-anchored one — stopped
# landing the moment the register moved. ⭐ IT REPORTED THAT AS A HARNESS ERROR RATHER THAN AS 15
# CAUGHT MUTATIONS, which is the one behaviour that made this safe to find: a mutation that never
# lands reports exactly what a guard that never fires reports (paper-hardening §8b), and the whole
# reason this file asserts `anchor occurs exactly once` is to refuse that reading.
# The anchor is now resolved by the PROPERTY "the document that contains it", and exactly-once is
# asserted ACROSS BOTH documents, so the single-site invariant is unchanged and an anchor that
# became ambiguous by appearing in both would still be an error rather than a silent choice.
DOC = os.path.join("research", "manuscripts", "fusion-partner",
                   "emc-fusion-partner-stratification.md")
REGISTER = os.path.join("research", "manuscripts", "fusion-partner",
                        "emc-fusion-partner-correction-register.md")
# ⛔ TWO GUARD MODULES SINCE 2026-08-28, AND BOTH ARE RUN FOR EVERY MUTATION.
# The synthesis's claims split into a QUANTITY half and a RELATION half (`paper-hardening` §8a), and
# they are guarded by two files: the numbers guard, and
# `test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py`, which reads
# count-words, comparatives, superlatives and attributions. A harness that ran one of them would
# report every relation mutation as SURVIVED while the guard that catches it sat uncollected — a
# mutation that reaches no instrument reports exactly what an instrument that never fires reports.
# ⚠ Running both in ONE pytest invocation is a batch, and a batch red at baseline hides its members
# (`paper-hardening` §8b.1a). That is why the positive control below refuses to score anything at
# all unless the unmutated tree is green: there is no state in which a pre-existing failure in one
# module is silently charged to the other.
# ⭐ THREE GUARD MODULES SINCE 2026-08-29 (AUT-PD-147). The synthesis's claims have a QUANTITY half,
# a RELATION half and — measured by the ablation harness on 2026-08-28, and guarded by nothing until
# that item — a PROVENANCE half: `NR4A3` -> `NR4A7` in the endpoint declaration left every guard
# above green, because a gene symbol is neither a quantity nor a claim word. The identifier guard is
# run for every mutation for the same reason the other two are: a mutation that reaches no
# instrument reports exactly what an instrument that never fires reports.
TESTS = [os.path.join("research", "manuscripts", "tests", name) for name in (
    "test_fusion_partner_prose_matches_its_artifact.py",
    "test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py",
    "test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py",
)]

#: Each mutation is (label, anchor, mutated, binding_it_targets).
#:
#: `anchor` must occur EXACTLY ONCE in the document — that is what makes the mutation single-site,
#: and it is asserted rather than assumed. `mutated` replaces it. The point of every one of these is
#: that a human reader of the sentence would not notice, and the guard must.
MUTATIONS = [
    # ---- round 8: the derived falsification threshold, the moved spread, and the split register --
    # ⛔ EVERY ONE OF THESE TARGETS A BINDING WRITTEN OR RE-POINTED IN ROUND 8. The round moved the
    # correction register into its own document and derived §6 falsifier #5's threshold in the
    # generator; both are new surfaces, and an unmutated new surface is a coverage guess.
    ("6.5: the 7-cohort projection drifts one tenth",
     "still leaves the pooled point estimate at **31.8 %** and",
     "still leaves the pooled point estimate at **31.9 %** and",
     "§6 falsifier #5's two projected pooled points for a third cohort of 7 and of 8"),
    ("6.5: the 8-cohort projection drifts one tenth",
     "**31.8 %** and\n   **30.4 %**",
     "**31.8 %** and\n   **30.5 %**",
     "§6 falsifier #5's two projected pooled points for a third cohort of 7 and of 8"),
    ("6.5: the two projections are SWAPPED, leaving every digit on the page",
     "at **31.8 %** and\n   **30.4 %**",
     "at **30.4 %** and\n   **31.8 %**",
     "§6 falsifier #5's two projected pooled points for a third cohort of 7 and of 8"),
    # ---- round 10: the falsifier's INTEGER trio, which round 9 found unbound and unmutated -------
    # ⛔ THE PERCENTAGES BESIDE THEM WERE ALREADY COVERED BY THE FOUR MUTATIONS ABOVE, and that is
    # the point: this is the one-of-a-pair shape, so a mutation set that stops at the percentages
    # measures a guard that stops at the percentages.
    ("6.5: the further-zero-death-patients integer drifts by one",
     "**19 further TAF15 patients with zero deaths",
     "**18 further TAF15 patients with zero deaths",
     "§6 falsifier #5's derived reconciliation threshold — the further zero-death TAF15 patients "
     "required and the total denominator they would make, the two integers the percentage bindings "
     "above left unwatched"),
    ("6.5: the total-denominator integer drifts by one, leaving 19 correct beside it",
     "a total TAF15 denominator of 34**",
     "a total TAF15 denominator of 35**",
     "§6 falsifier #5's derived reconciliation threshold — the further zero-death TAF15 patients "
     "required and the total denominator they would make, the two integers the percentage bindings "
     "above left unwatched"),
    # ⭐ THE RELATION, NOT A DIGIT. Every number on the page stays correct and the sentence now
    # overstates how far out of reach the falsifier is — the direction that flatters this paper.
    ("6.5: the multiple of the pooled experience is overstated, every digit left correct",
     "denominator of 34**, more than twice the",
     "denominator of 34**, more than three times the",
     "the falsifier's multiple-of-the-pooled-experience relation"),
    # ---- round 10: §4.7's new bridge from Huang's 53 with follow-up to the pooled 50 -------------
    ("4.7: the bridging denominator drifts from the sum of the arms the pool uses",
     "53, the **50** that enter the pooled table",
     "53, the **51** that enter the pooled table",
     "§4.7's bridge from Huang's follow-up count to the denominator the pooled table actually uses"),
    ("6.5: the comparator upper bound drifts",
     "Wilson upper bound of **20.8 %**",
     "Wilson upper bound of **20.9 %**",
     "§6 falsifier #5's comparator upper bound, which is what the projection is measured against"),
    ("3.3: the Agaram TAF15 death count in the circularity argument drifts",
     "partly **produced by** its own 3/7 deaths",
     "partly **produced by** its own 3/8 deaths",
     "§3.3's restatement of the Agaram TAF15 death count inside the follow-up circularity argument"),
    ("3.3: the live comparator-arm spread drifts, at the site the removed 2.5 note used to cover",
     "comparator-arm spread is\n**22.4 points**",
     "comparator-arm spread is\n**22.5 points**",
     "§3.3's live statement of the local-recurrence comparator-arm spread — the site the removed "
     "§2.5 note used to be the only bound restatement of"),
    ("3.3: the per-arm follow-up pair is SWAPPED at the re-anchored site",
     "mean follow-up (21.7 vs 43.3 months) and Huang publishes",
     "mean follow-up (43.3 vs 21.7 months) and Huang publishes",
     "§3.3's per-arm mean follow-up, TAF15 first"),
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
    # ⛔ TWO MUTATIONS RETIRED IN ROUND 8, AND RETIRED IS NOT THE SAME AS DELETED — the reason is
    # recorded because a missing mutation is invisible and a removed one should have to argue for
    # itself. Both mutated §2.5's ⚠ note, which RESTATED the two widest spreads while recording why
    # that bullet had been corrected. Round 8 removed the note (a correction belongs in the register,
    # not inside the sentence it corrects). ⭐ NEITHER QUANTITY LOST COVERAGE, which is the only thing
    # that justifies retiring rather than re-pointing them: 53.9 is still mutated at its real home by
    # "3.1 row: the spread itself drifts", and 22.4 by "3.3: the live comparator-arm spread drifts",
    # which round 8 added precisely because that live site had never been mutated at all.

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
     # ⚠ ANCHOR REPAIRED IN ROUND 8, NOT RETIRED. The sentence still stands and its binding still
     # reads it; only the cross-reference changed, from `Appendix A4` to a link at the register the
     # row moved to. Repair when the claim survives the rewording — retire only when it does not.
     "register.md) A4 records its 80 % high-grade variant group",
     "register.md) A4 records its 85 % high-grade variant group",
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

    # ---- F.5 · the fold-change notation and the two figures promoted onto it (AUT-COV-001) -------
    # ⛔ WHY THIS EXISTS. `_CENSUS_STATS` gained a fifth alternative (a printed ×-fold) and two
    # DECLARED rows became BINDINGS against the GSE28866 artifact opened directly by this file.
    # Neither move is proven by being read; both are proven by breaking on purpose, the same standard
    # every binding above is held to.
    ("3.6: the SEMA3C-vs-normal-tissue fold-change drifts, vs-sarcoma left correct beside it",
     "**1.8× normal tissue and 1.7× other sarcomas**",
     "**1.9× normal tissue and 1.7× other sarcomas**",
     "the GSE28866 SEMA3C fold-change binding — the vs-normal-tissue half"),
    ("3.6: the SEMA3C-vs-other-sarcomas fold-change drifts, vs-normal-tissue left correct beside it",
     "**1.8× normal tissue and 1.7× other sarcomas**",
     "**1.8× normal tissue and 1.8× other sarcomas**",
     "the GSE28866 SEMA3C fold-change binding — the vs-other-sarcomas half"),
    ("3.6: the two SEMA3C fold-change ratios are SWAPPED, both digits still on the page",
     "**1.8× normal tissue and 1.7× other sarcomas**",
     "**1.7× normal tissue and 1.8× other sarcomas**",
     "the GSE28866 SEMA3C fold-change binding — both halves at once"),
    ("3.6: the GSE28866 EMC library count backing the ratio drifts",
     "n = 4 EMC libraries",
     "n = 5 EMC libraries",
     "the GSE28866 EMC library-count binding"),
    # ⭐ THE ONE MUTATION THAT TARGETS NO BINDING, FOR THE NEW NOTATION SPECIFICALLY. A fold-change
    # written into the prose with no artifact behind it is exactly what `_CENSUS_STATS`'s fifth
    # alternative exists to stop going unnoticed — same shape as the `n = 99` control above, for the
    # notation this cycle added rather than the one CYC-0013 added.
    ("census: an unbound fold-change is written into the prose",
     "The full inclusion table is §3.2.",
     "The full inclusion table is §3.2 (3.0× unbound).",
     "test_every_statistical_quantity_is_bound_or_declared — the fold-change alternative"),

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

    # =============================================================================================
    # R · THE RELATION HALF (2026-08-28, ledger AUT-PROP-012).
    #
    # ⛔⛔ NOT ONE OF THESE CHANGES A DIGIT ON THE PAGE except where the relation IS a digit. Round 6
    # measured the gap they close: one seat re-derived 140 printed quantities from the artifacts
    # with ZERO mismatches while five seats in the same tree found three blockers, and not one of
    # the three was a number — a cardinal written as the word "two", a comparative over the paper's
    # own pool, and an unsourced claim about what the field quotes. Every mutation below is one of
    # those three shapes, and the two guard modules are run SEPARATELY per mutation so the output
    # says which one caught it rather than only that something did.
    # ---- R.1 · count-words: a cardinal spelled out is still a count ------------------------------
    # ⭐ THE ROUND-6 BLOCKER ITSELF, RESTORED VERBATIM. §5 read this for three days: two series
    # asserted, one named in the parenthesis beside it, and the sentence contradicting itself.
    ("§5 claims bullet: the round-6 blocker restored — 'the one series' becomes 'either of the two'",
     "in the one series that\n  ran a multivariable model (Huang 2023), while the second",
     "in either of the two series that\n  ran a multivariable model (Huang 2023), while the second",
     "the count of series that ran a multivariable model, at the §5 site round 6 found"),
    # ⭐ THE ONE-OF-A-PAIR HALF. The same count at a different section: a repair that reached §5 and
    # stopped there is exactly how this claim survived three rounds of hand-enumerated fixes.
    ("§3.8: the same count drifts at a site four sections away from §5",
     "absorbed by tumour size in the\none series that ran a multivariable model (§3.4)",
     "absorbed by tumour size in the\ntwo series that ran a multivariable model (§3.4)",
     "the count of series that ran a multivariable model, at the §3.8 site"),
    ("§1.2: the outcome roster grows in the evidence table",
     "| **four** series test the partner against outcome",
     "| **five** series test the partner against outcome",
     "the count of series testing the partner against outcome"),
    ("§1.2: the sub-count publishing event counts drifts, leaving the roster count correct",
     "outcome and only **two** publish per-partner event counts",
     "outcome and only **three** publish per-partner event counts",
     "the count of outcome series publishing per-partner event counts"),
    ("§3.3: the count opening the results section drifts",
     "\n\n**Two** cohorts publish EMC outcome event counts by *NR4A3* partner. Agaram",
     "\n\n**Three** cohorts publish EMC outcome event counts by *NR4A3* partner. Agaram",
     "the count of cohorts publishing EMC outcome event counts"),
    ("§2.3a: the SAME count drifts where §2.3a quotes §3.3 — one of a pair",
     "§3.3's \"**Two** cohorts publish EMC outcome event\ncounts",
     "§3.3's \"**Three** cohorts publish EMC outcome event\ncounts",
     "the count of cohorts publishing EMC outcome event counts"),
    ("§5: the count in the endpoint sentence drifts",
     "death across the only two cohorts that publish event counts by partner",
     "death across the only three cohorts that publish event counts by partner",
     "the count of cohorts publishing event counts, as §2.3a and §5 state it"),
    ("§2.3a: the same count drifts where §2.3a quotes §5 — one of a pair again",
     "§5's \"the only two cohorts that publish event counts by partner\"",
     "§5's \"the only three cohorts that publish event counts by partner\"",
     "the count of cohorts publishing event counts, as §2.3a and §5 state it"),
    ("§5 claims bullet: the pooled-cohort count drifts beside a correct 7/15",
     "pooled over the two cohorts publishing\n  partner-stratified",
     "pooled over the four cohorts publishing\n  partner-stratified",
     "the count of cohorts publishing partner-stratified event counts"),
    ("§2.3a: the same count drifts in the exhaustiveness caveat that quotes it",
     "bullet's \"the two cohorts publishing partner-stratified event counts\"",
     "bullet's \"the three cohorts publishing partner-stratified event counts\"",
     "the count of cohorts publishing partner-stratified event counts"),
    # ⭐ THE COUNTS §3.4's REPAIRED OPENING RESTS ON. The retracted sentence put both series OUTSIDE
    # the pool; the replacement puts each inside a named one, so both roster sizes are load-bearing.
    ("§3.4: the outcome pool's size drifts where §3.4 places Huang 2023 inside it",
     "Huang 2023 is one of the two cohorts pooled in §3.3",
     "Huang 2023 is one of the three cohorts pooled in §3.3",
     "the size of the outcome pool as §3.4 states it"),
    ("§3.4: the prevalence pool's size drifts, leaving the outcome count correct beside it",
     "Paioli 2021 one of the four pooled in §3.5",
     "Paioli 2021 one of the five pooled in §3.5",
     "the size of the prevalence pool as §3.4 states it"),
    ("§3.5: the number of the paper's own references stating a general TAF15 share drifts",
     "The two sources in the reference list that give a general TAF15 share",
     "The three sources in the reference list that give a general TAF15 share",
     "the count of the paper's own references stating a general TAF15 share"),

    # ---- R.2 · comparatives and superlatives over this synthesis's own pool ----------------------
    # ⭐ A REAL PUBLISHED P FROM THE SAME COHORT, ON A DIFFERENT TEST. Nothing on the page becomes
    # invented; the sentence just quotes the wrong one of Huang's own results for the superlative it
    # asserts.
    ("§3.3: the largest metastasis-testing series is credited with Huang's STATUS p, not its "
     "metastasis p",
     "*directly* reports **P = .728** on its own",
     "*directly* reports **P = .047** on its own",
     "the superlative binding the largest metastasis-testing series to its own published p"),
    # ⭐ EVERY DIGIT ON THE PAGE STAYS CORRECT. Suemitsu 2025 is a real cohort of this synthesis; it
    # is simply not one the outcome analysis pools, which is the whole content of the sentence.
    ("§3.4: the series placed inside the outcome pool is one the artifact does not pool",
     "synthesis: Huang 2023 is one of the two cohorts pooled",
     "synthesis: Suemitsu 2025 is one of the two cohorts pooled",
     "the membership assertion §3.4's repaired opening rests on"),
    # ⭐⭐ ROUND 6's BLOCKER B2, RESTORED INTO THE SENTENCE IT WAS REMOVED FROM.
    ("§3.4: the retracted comparative is put back in front of the repaired opening",
     "Two series tested the partner as a prognostic factor against tumour size",
     "Two series, both larger than any cohort that could be pooled here, tested the partner as a "
     "prognostic factor against tumour size",
     "the forbid on comparisons against this synthesis's own pool — the named-series branch"),
    # ⭐ THE UNDECIDABLE BRANCH. Same claim, in a sentence naming nobody, which is the shape the
    # retracted sentence actually had: its two series were named in the NEXT sentence, so neither a
    # reader nor an instrument could settle it where it stood.
    ("§3.4: the same comparative in a sentence that names no series at all",
     "**Neither found the partner to carry the prognosis.**",
     "**Neither found the partner to carry the prognosis, and both are larger than any cohort that "
     "could be pooled here.**",
     "the forbid on comparisons against this synthesis's own pool — the undecidable branch"),
    ("§5: the pooled-cohort count inside the comparative that carries the defeater",
     "the larger of its own two cohorts declines to",
     "the larger of its own three cohorts declines to",
     "the comparative placing the defeater in the larger pooled cohort"),
    # ⭐ A UNIQUENESS CLAIM INVERTED WITH EVERY DIGIT INTACT. Agaram 2014 is a real cohort of this
    # synthesis and publishes no time-to-event metastasis analysis at all.
    ("§3.3: the only cohort treating metastasis as time-to-event becomes the wrong cohort",
     "Paioli 2021, the only cohort treating\nmetastasis as a **time-to-event**",
     "Agaram 2014, the only cohort treating\nmetastasis as a **time-to-event**",
     "the uniqueness claim about the time-to-event metastasis cohort"),

    # ---- R.3 · what the field says ---------------------------------------------------------------
    # ⭐⭐ ROUND 6's BLOCKER B3, RESTORED VERBATIM AT THE ABSTRACT SITE. No source for the quoting
    # practice has ever been held here, and the guard's licence is that absence.
    ("abstract: the external share is re-attributed to the field's quoting practice",
     "the ≈20 % this document's own cited sources state and sits below the",
     "the ≈20 % the field routinely quotes and sits below the",
     "the forbid on unsourced claims about the field's practice, plus the attribution binding"),
    ("§1.3: 'most-quoted' restored — the same class with no number in it at all",
     "state and placing the single referral-centre cohort above it",
     "state and placing the most-quoted single cohort above it",
     "the forbid on unsourced claims about the field's practice"),
    ("§3.8: 'usually attributed to' restored, both PMIDs left correct beside it",
     "(PMID 24703573) this\nrepository's own lane memo attached it to.**",
     "(PMID 24703573) it is\nusually attributed to.**",
     "the forbid on unsourced claims about the field's practice"),
    ("§5 claims bullet: the externally reported share drifts from the artifact's figure",
     "**contains** the ≈20 % this document's own cited sources state ([4], [12])",
     "**contains** the ≈21 % this document's own cited sources state ([4], [12])",
     "the external-share attribution binding — the percentage half"),
    # ⭐ THE MUTATION THAT ONLY THE RELATION GUARD CAN SEE. Reference [15] is a real reference of
    # this manuscript, so `lint_citations` is green and every number on the page is right; what
    # changes is WHICH of the paper's own sources is claimed to state the external share.
    ("§5 claims bullet: the external share is attributed to a different real reference",
     "own cited sources state ([4], [12])",
     "own cited sources state ([4], [15])",
     "the external-share attribution binding — the named-sources half"),
    # ---- AUT-PD-147, 2026-08-29: the PROVENANCE half — a gene symbol, not a number or a verb -----
    # ⛔⛔ THE FIRST OF THESE IS THE MEASURED DEFECT ITSELF, RESTORED VERBATIM. The ablation harness
    # perturbed the endpoint declaration's `NR4A3` to `NR4A7` on 2026-08-28 and every guard reading
    # this document stayed green — the two modules above, the three linters and the pooling check.
    # ⭐ AND THE REST ARE THE SAME CORRUPTION AT OTHER SITES, WHICH IS THE WHOLE POINT: the document
    # prints `NR4A3` 71 times, `TAF15` 100 and `EWSR1` 46, so a guard that asks "is the right symbol
    # in here anywhere" passes while one site is wrong. Every one of these changes exactly one.
    ("identifier: NR4A3 -> NR4A7 in the endpoint declaration (the defect AUT-PD-147 was filed on)",
     "*The NR4A3 5′ fusion partner is a candidate",
     "*The NR4A7 5′ fusion partner is a candidate",
     "the unattested-identifier check, at the one site the ablation harness perturbed"),
    ("identifier: NR4A3 -> NR4A7 at §7's ask, 38 lines and one section away from the endpoint",
     "Report the *NR4A3* partner alongside response",
     "Report the *NR4A7* partner alongside response",
     "the unattested-identifier check reaching a SECOND site of the same 71-occurrence symbol"),
    ("identifier: TAF15 -> TAF19 at one of its 100 sites",
     "and *TAF15* in a minority",
     "and *TAF19* in a minority",
     "the unattested-identifier check, single-site against the document's most-repeated symbol"),
    ("identifier: EWSR1 -> EWSR7 at one of its 46 sites",
     "partner is *EWSR1* in most cases",
     "partner is *EWSR7* in most cases",
     "the unattested-identifier check, single-site on the comparison's other arm"),
    # ⛔ AND THE REGISTER IS IN SCOPE TOO. A correction register states what this repository got
    # wrong; a wrong gene symbol inside a correction is still a wrong gene symbol, and the register
    # was as unguarded as the manuscript.
    ("identifier: TAF15 -> TAF19 in the correction register's row A3",
     "| A3 | TAF15::NR4A3 prevalence quoted as",
     "| A3 | TAF19::NR4A3 prevalence quoted as",
     "the unattested-identifier check reaching the second prose document of this synthesis"),
    # ⭐⭐ THE TWO BELOW LEAVE EVERY TOKEN ON THE PAGE ATTESTED, so the check above is green on both
    # and only the fusion-pair binding can see them. That is the attested-to-attested drift class the
    # identifier corpus is structurally blind to, closed inside the `::` construction by reading the
    # permitted pairs out of `emc-fusion-partner-pooling.json`.
    ("pair: EWSR1::NR4A3 written BACKWARDS at one site — both symbols still real and attested",
     "**Not** that EWSR1::NR4A3 patients should receive",
     "**Not** that NR4A3::EWSR1 patients should receive",
     "the fusion-pair check's ORDER half — a backwards pair names a different rearrangement"),
    ("pair: TAF15::NR4A3 -> TAF15::NR4A2, a real paralogue the corpus attests",
     "**Not** that TAF15::NR4A3 is an independent prognostic factor",
     "**Not** that TAF15::NR4A2 is an independent prognostic factor",
     "the fusion-pair check's 3'-partner half, which the identifier corpus cannot see"),
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


def _run_one(tree, test):
    """One guard module's verdict in `tree`: True = green.

    ⛔ A RETURN CODE ALONE IS NOT AN ANSWER. pytest exits 1 for a failing test, for a collection
    error, and (via `-m`) for not being installed at all. So the verdict is accepted only when the
    output carries a pytest summary naming passed and/or failed tests; anything else is raised as an
    unusable run rather than reported as red.
    """
    if not PYTEST:
        raise SystemExit("no `pytest` on PATH — this harness cannot run and will not guess.")
    r = subprocess.run([PYTEST, test, "-q", "--no-header", "-x"],
                       cwd=tree, capture_output=True, text=True)
    out = r.stdout + r.stderr
    if not re.search(r"\d+ (?:passed|failed|error)", out):
        raise SystemExit(f"{os.path.basename(test)} could not run in {tree} (exit "
                         f"{r.returncode}); no pytest summary in the output, so this is not a "
                         f"verdict:\n{out[-3000:]}")
    return r.returncode == 0


def _run_guard(tree):
    """Which guard modules go RED in `tree` — the empty set means the tree is green.

    ⛔⛔ EACH MODULE IS RUN ON ITS OWN, AND THE REASON IS `paper-hardening` §8b.1a: an instrument
    that reports `state(group)` and then reasons about a member of that group can manufacture a
    finding that looks real. Running both guards in one pytest invocation would answer "something
    went red", which is enough to score a mutation and NOT enough to say which binding reached it —
    and "the relation guard caught this" is precisely the claim this harness exists to support now
    that there are two modules. The cost is one extra interpreter start per mutation; the benefit is
    that every line of the output below names the guard that fired.
    """
    return [t for t in TESTS if not _run_one(tree, t)]


def _overlay_working_tree(tree):
    """Copy every uncommitted change into the clone, and say exactly what was copied.

    ⛔⛔ WHY THIS EXISTS — THE HARNESS ONCE MEASURED THE WRONG GUARD AND SAID SO ITSELF. The
    quantity guard's docstring records it: run before its new bindings were committed, 20 of 21
    mutations SURVIVED, because the worktree is built from HEAD and HEAD did not contain them. That
    reading was correct about the tree it measured and worthless as evidence about the work in hand,
    and the only way out was to commit first — i.e. to commit a guard whose coverage was still a
    guess.

    ★ SO THE CLONE IS STILL A CLONE. `git worktree add` gives a genuine separate checkout with no
    shared inode (`paper-hardening` §8b.1: ablate a copy, never the working tree, and `cp -al` is
    not isolation); this only copies the uncommitted files into it, by `git status --porcelain`,
    without touching the real repository's index. ⛔ It is NOT the default, and the mode is printed
    with the result, because "N of N caught" means something different in each mode.
    """
    st = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"],
                        cwd=REPO, check=True, capture_output=True, text=True).stdout
    copied, removed = [], []
    entries = [e for e in st.split("\0") if e]
    i = 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        code, path = entry[:2], entry[3:]
        if code[0] == "R":            # rename: the next NUL-separated field is the source path
            i += 1
        src = os.path.join(REPO, path)
        dst = os.path.join(tree, path)
        if os.path.isdir(src):        # an untracked directory is reported as one entry
            for root, _dirs, files in os.walk(src):
                for f in files:
                    s = os.path.join(root, f)
                    d = os.path.join(tree, os.path.relpath(s, REPO))
                    os.makedirs(os.path.dirname(d), exist_ok=True)
                    shutil.copy2(s, d)
                    copied.append(os.path.relpath(s, REPO))
            continue
        if not os.path.exists(src):   # deleted in the working tree
            if os.path.exists(dst):
                os.remove(dst)
                removed.append(path)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(path)
    print(f"⚠ WORKING-TREE MODE: {len(copied)} uncommitted file(s) copied into the clone"
          f"{f', {len(removed)} removed' if removed else ''}. This measures the tree you are about "
          f"to commit, NOT HEAD.")
    for p in sorted(copied):
        print(f"    + {p}")
    return copied


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="leave the worktree in place for inspection")
    ap.add_argument("--working-tree", action="store_true",
                    help="overlay uncommitted changes onto the clone before measuring, so a guard "
                         "can be mutation-tested BEFORE it is committed")
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="fp-mutate-")
    tree = os.path.join(tmp, "wt")
    subprocess.run(["git", "worktree", "add", "--detach", tree, "HEAD"],
                   cwd=REPO, check=True, capture_output=True)
    if args.working_tree:
        _overlay_working_tree(tree)
    docs = [os.path.join(tree, DOC), os.path.join(tree, REGISTER)]
    try:
        pristine = {d: io.open(d, encoding="utf-8").read() for d in docs}
        base_digest = {d: _digest(d) for d in docs}

        # ⛔ THE POSITIVE CONTROL RUNS FIRST. A harness that reports every mutation caught while the
        # unmutated tree is ALSO red has measured nothing at all.
        red = _run_guard(tree)
        if red:
            raise SystemExit(
                "POSITIVE CONTROL FAILED: "
                + ", ".join(os.path.basename(t) for t in red)
                + " is red on an unmutated tree, so no mutation result below would mean anything. "
                  "Fix that first.")
        print(f"positive control: GREEN on unmutated HEAD ({len(MUTATIONS)} mutations to run)\n")

        survived, errors = [], []
        for label, anchor, mutated, targets in MUTATIONS:
            total = sum(pristine[d].count(anchor) for d in docs)
            if total != 1:
                where = ", ".join(f"{os.path.relpath(d, tree)}×{pristine[d].count(anchor)}"
                                  for d in docs if pristine[d].count(anchor))
                errors.append(f"{label}: anchor occurs {total} times across the synthesis's prose "
                              f"documents, not once{' (' + where + ')' if where else ''} — the "
                              f"mutation is not single-site and its result would be unreadable")
                continue
            doc = next(d for d in docs if pristine[d].count(anchor) == 1)
            io.open(doc, "w", encoding="utf-8").write(pristine[doc].replace(anchor, mutated))
            if _digest(doc) == base_digest[doc]:
                errors.append(f"{label}: MUTATION DID NOT LAND (digest unchanged)")
                io.open(doc, "w", encoding="utf-8").write(pristine[doc])
                continue
            caught_by = _run_guard(tree)
            io.open(doc, "w", encoding="utf-8").write(pristine[doc])
            assert _digest(doc) == base_digest[doc], "failed to restore the worktree between mutations"
            # ⭐ THE VERDICT NAMES THE GUARD, not just the outcome. `numbers` is the quantity guard,
            # `relations` the one that reads count-words, comparatives, superlatives and
            # attributions; a mutation caught by `relations` alone is that binding's own evidence.
            short = {"test_fusion_partner_prose_matches_its_artifact.py": "numbers",
                     "test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py":
                         "relations",
                     "test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py":
                         "identifiers"}
            who = "+".join(short.get(os.path.basename(t), os.path.basename(t))
                           for t in caught_by)
            print(f"  {'⛔ SURVIVED' if not caught_by else '✅ caught  '}  "
                  f"[{who or '—':<17}]  {label}")
            if not caught_by:
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
