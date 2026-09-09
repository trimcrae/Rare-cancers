---
id: DOC-OPUS-CAMPAIGN-PENDING-DIFF-LEDGER-20260909
title: "Unapplied diffs awaiting a decision, 2026-09-09"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Every unapplied diff this campaign produced, with its real apply state

Twenty-six proposed diffs exist across the portfolio lanes. **None is applied**, except
`REPURPOSING-3-LEDGER/ledger-entries.diff`, which the parent applied at `1e35538da` to return the
citation gate to its inherited baseline. This ledger exists so the decision is readable in one place
instead of scattered across twenty-two lane directories, and so nobody applies two diffs that
silently conflict.

Every `apply_check` below is a real `git apply --check` exit code measured against the tree at
`b14a84259`. ⚠ `git apply --check` tests each patch against the CURRENT tree, not cumulatively, so a
row of zeros does **not** mean the set can be applied in any order. Where order matters it is stated.

## Applies cleanly, one target, no known conflict

| lane | target | apply | size |
|---|---|---|---|
| BIOMARKER-DEP-2 | `research/modalities/depmap_sarcoma_dependency.py` | 0 | +47 −1 |
| CLOSED-ROUTES-2 | `research/manuscripts/methods-record/closed-routes-negative-record.md` | 0 | +33 |
| IPD-SURVIVAL-3 | `research/modalities/km_risk_row_detect.py` | 0 | +9 |
| MORTALITY-3 | `research/manuscripts/emc-mortality-mechanisms-paper.md` | 0 | +29 −3 |
| NEOANTIGEN-6 | `research/modalities/fusion_breakpoints.py` | 0 | +99 |
| STRATEGY-ARCH-2 | `research/manuscripts/care-delivery/emc-trial-reachability.md` | 0 | +14 −1 |
| SURFACE-2 | `research/modalities/emc_surface_normal_window.py` | 0 | +35 −3 |
| PUB-HLA-COVERAGE | `research/manuscripts/neoantigen/hla-coverage-emc.md` | 0 | +14 −5 |

## Ordering and duplication hazards — read before applying any of these

**NEOANTIGEN-4 and NEOANTIGEN-5's `-01` are BYTE-IDENTICAL FILES** (`cmp -s` confirms). Both patch
`junction_proteome_novelty.py` with the same `PARENTS` accession fix. Applying both is a re-apply and
the second fails; NEOANTIGEN-6's `checks/11` hit exactly that, and its exit 1 is **not** a defect in
its own diff. Apply the `PARENTS` patch **once**, from either copy, then NEOANTIGEN-5's `-02`
(`tests/test_junction_proteome_novelty_parent_accession.py`, +116). NEOANTIGEN-6's zero-partner diff
touches a different file and is independent of both, applicable before or after.

**CARE-DELIVERY-3 SUPERSEDES AND SUBSUMES CARE-DELIVERY-2.** Both patch
`research/modalities/emc-surgical-quality.json` and both check clean in isolation. Apply **only**
CARE-DELIVERY-3 (+38 −5); applying CARE-DELIVERY-2 (+34 −5) first is explicitly wrong per its
successor's own instruction.

**HLA-COVERAGE-2 and HLA-COVERAGE-3 both patch `emc-vaccine-development-path.md`** — §2.3 and §8
respectively. HLA-COVERAGE-3 measured that they coexist (its `checks/05`, exit 0), so both may go in;
that is a measured result, not an assumption.

**The REPURPOSING chain does not apply — and my first diagnosis of why was WRONG.** All four of its
diffs return exit 1, and I wrote here that "the tree has moved since". ⛔ **THAT IS NOT WHAT THE TREE
SAYS.** REPURPOSING-4 re-measured and found all four fail identically, *before a single hunk is
examined*, with `No such file or directory` on a `/tmp/.../scratchpad/.../AFTER.md` path — because
each was produced by `diff -u <real file> <scratchpad AFTER file>`, so the `+++` header names a
scratchpad path that `git apply` then cannot find. I confirmed the headers myself. That is the same
class of defect as HLA-COVERAGE-2's exit 128: a hand-assembled patch envelope, **not** tree drift.

With only the two header lines rewritten — no hunk, no content byte — three of the four apply
cleanly against today's tree (7, 6 and 4 hunks, all exit 0). The fourth,
`PROPOSED-UNAPPLIED-rebased-onto-REPURPOSING-2.diff`, still exits 1, and that is **by design**: its
base is the post-sweep file, so hunks 2–6 reject on context containing REPURPOSING-2's added
sentences. A base mismatch, exactly as REPURPOSING-3 documented, not a conflict.

**Use REPURPOSING-4's rebased set**, which is generated with `difflib` rather than hand-assembled:
`REBASED-COMBINED-single-patch.diff` (10 hunks, +65 −20) checks exit 0 in tree and applies exit 0 on
a scratch copy. The two-step route is `REBASED-01` then `REBASED-02`, and **`REBASED-02` checking
exit 1 against the bare tree is EXPECTED** — its base is the post-`01` file. `APPLY-ORDER.md` in
that lane records this so nobody "fixes" patch 02 by dropping the sweep.

## Cannot apply — target missing

`PUB-CARE-DELIVERY`, `PUB-MONOVALENT` and `PUB-VACCINE-PATH` each return **exit 128**: the patch
names a path that does not exist in the tree. These are first-round proposals whose targets have
since moved or been superseded. They are not candidates until someone re-derives them.

## Diffs that patch ANOTHER LANE'S RECORDS — flagged, not recommended

BIOMARKER-DEP-3's two diffs check clean but their targets are **campaign lane records**, not
manuscripts or producers:
`biomarker-dep-2-span-correction.diff` edits BIOMARKER-DEP-2's own `FINDING.md`, generator and JSON;
`fisher-p-denominator-restatement.diff` edits PUB-BIOMARKER-DEP's.
Both corrections are substantively right — p is non-monotone in n, so the true envelope is
[0.083170, 0.088644] rather than the span BIOMARKER-DEP-2 stated and I relayed, and the denominator
assumption **is** recorded at `transfer_calibration.py:125–129` rather than being unrecorded. But
editing a completed lane's dated record in place is not the repository's correction convention: this
campaign's practice is a dated correction beside the original, preserving it. **Recommended
disposition: record the correction, do not rewrite the sibling's record.** The correction is already
carried in the commit that integrated BIOMARKER-DEP-3.

## Known downstream cost of one of them

MORTALITY-3's §4.2 diff, if applied, makes `research/manuscripts/claim-coverage.json` **stale**
against `claim_coverage.py`'s `STALE_HEADER` guard and the census/guard-corpus tests. MORTALITY-3
named this itself and did not regenerate. Whoever applies it owns that regeneration in the same
commit, and the guard must not be touched.

## What this ledger is not

It is not an admission, an approval, or a recommendation to apply anything. Several of these are
scope extensions to live manuscripts — CLOSED-ROUTES-2 files its rows under a **new §9A** rather than
into the existing table of seven, precisely because they are a different class of closure. Those are
the owner's call. This is a map of what exists and what would break, measured rather than assumed.
