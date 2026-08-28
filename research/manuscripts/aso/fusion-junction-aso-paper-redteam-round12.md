---
id: DOC-FUSION-JUNCTION-ASO-PAPER-REDTEAM-ROUND12
title: "Round-12 blind review of the fusion-junction ASO journal article — one real guard regression, in the tooling round 11 added, plus one process incident it exposed"
level: L3
kind: manuscript
status: live
canonical_for:
  - round 12 blind adversarial review of the ASO journal article
purpose: >
  Round 12 hardening of PUB-ASO — a confirmation pass on round 11's four guard/tooling fixes, per
  this series' own standard that a round which finds and fixes gaps does not get to certify nothing
  was found. Five blind seats reviewed the pinned commit. Zero blockers, zero P1s in the article's
  own prose. One real P1 found in round 11's own tooling (lint_style.py's HTML-comment exemption
  silently blinded the style gate over most citation-bearing prose), fixed and mutation-tested this
  round. Separately, and outside any seat's own finding: applying the driver's own fix for a stale
  generated artifact ran into a live mutation left by a concurrently-running seat and briefly
  committed a wrong value to research/manuscripts/submission-metrics.json, caught by seat 4 and
  corrected in the same cycle (process defect AUT-PD-047). Because round 12 itself found and fixed
  real things, it does NOT close publish_bar's hardening_converged clause — round 13, a confirmation
  pass on round 12's two fixes, is queued (AUT-PROP-041).
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence. Every sequence named is a research reagent for laboratory
  investigation only and must not be administered to any person or animal.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-28
last_verified: 2026-08-28
---

# Round 12 — blind adversarial review of the ASO journal article

**Subject.** `research/manuscripts/aso/fusion-junction-aso-journal-article.md` at pin
`9ae136502a831732d79ade7c62c356d14c9f000f`, unchanged since round 11 (AUT-PROP-039) landed — the
article's own prose was never touched by round 11 or round 12.

**Seats.** Five blind lenses, dispatched as parallel subagents (research-loop's session shape, no
`create_session` mechanism available in this scheduled-Routine context): regression against round
11's four guard/tooling fixes; arithmetic re-derived from the committed artifacts; statistics and
experimental design; citations, build and gate coverage; hostile referee. No seat saw another's
output, sibling-seat yield history, or this document while working.

---

## Result: the article's own prose is clean; one real regression in round 11's tooling

**Zero blockers, zero P1s in `fusion-junction-aso-journal-article.md` itself**, across all five
lenses — confirmed independently by seat 2's arithmetic re-derivation of every headline number
(including a real run of `aso_falsification_power.py`), seat 3's full statistical re-derivation of
the power/void-SD figures and overclaim scan, and seat 5's cover-to-cover hostile-referee read
(verdict: **accept**, zero findings).

- **Seat 1 (regression on round 11's four fixes).** Found one real defect, in the tooling, not the
  prose: `lint_style.py`'s round-11 HTML-comment exemption (added so a decorative glyph inside a
  non-rendered `<!-- ... -->` maintainer comment would not trip the gate) drops the **entire line**
  whenever a comment closes on the same line — not just the comment span. The article's citation
  markers (`<sup>N</sup><!--PMID:...-->`) sit mid-sentence on roughly two dozen lines across the
  article and SI, so real prose sharing those lines went uninspected by `lint_style.py`'s
  glyph/second-person/banned-phrase/fragment checks. Verified by mutation: inserting a decorative
  glyph and a second-person "your" into prose sharing a comment-bearing line passed clean; the
  identical mutation on a comment-free line was caught.
  ⚠ **Graded here as P1, not the BLOCKER seat 1 reported** — per this series' own §8.0 test, applied
  by the driver rather than taken from the seat's own heading: the article's actual committed prose
  on every affected line was independently re-read and is correct today (seats 2, 3 and 5 all read
  the same text and found nothing wrong in it); what was broken is a currently-armed gate silently
  not checking otherwise-correct prose, which is the guard-gap class §8.0 explicitly puts at P1
  ("every guard gap belongs here, however central the claim"), not a wrong statement in the shipped
  paper.
  **Fixed this round**: `lint_style.py`'s comment handling now strips only the `<!-- ... -->` span
  and continues checking whatever prose remains on the line (or the next line, for a comment that
  spans several), rather than dropping the whole line. Regression-tested:
  `research/modalities/tests/test_lint_style.py`, 7 cases, all failing against the pre-fix code and
  passing against the fix (asserted both directions before trusting the fix). No new false positive
  across `lint_style.py`'s full 14-file target corpus, including the article, SI, tables and
  references.
  Seat 1 verified the other three round-11 fixes hold with no regression: the ΔTm-floor binding test
  correctly re-derives from `junction-aso-thermo.json`; `aso_falsification_power.py`'s derivation is
  correctly bound by its test; `lint_claims.py` does not exempt HTML comments at all (the comment
  exemption is scoped to `lint_style.py` only), so a banned claim hidden in a comment would still be
  caught there.
- **Seat 2 (arithmetic).** No findings. Independently ran `aso_falsification_power.py` and matched
  the article's power/void-SD prose exactly; re-derived the ΔTm floor from `junction-aso-thermo.json`;
  cross-checked a dozen other headline figures (190/87/61, the null-ensemble rates, the coverage
  percentages, the junction-clearing counts by cut) against their producing artifacts, all exact.
- **Seat 3 (statistics and design).** No findings. Independently recomputed the power calculation and
  void-SD thresholds from a noncentral-t model and matched the article to stated precision; confirmed
  the Wilson-interval null comparison, the multiple-cuts comparison is appropriately not overclaimed,
  and the standing R1–R5 overclaim rule holds throughout.
- **Seat 4 (citations, build, gates).** No findings on the pinned commit itself: citation provenance
  clean (`lint_citations`/`lint_citation_types` both green), build-stamps all match the pinned
  source's sha256, and all four round-11 gate additions confirmed wired into `preflight.sh`/CI, not
  orphaned. Separately, and outside the pin: caught that the driver's own follow-up commit
  (`6e7d44e06`, regenerating `submission-metrics.json` to clear an unrelated stale-preflight failure)
  had captured a mutation-window contamination rather than real drift, and named the exact mechanism.
  Corrected in `3a53478a8`. Full account: process defect AUT-PD-047.
- **Seat 5 (hostile referee).** Verdict: **accept**. No BLOCKER, no P1, no internal contradiction, no
  LLM artifact, every cross-checkable number consistent. Read cover to cover as if for the first
  time despite eleven-plus prior rounds.

---

## Why this round does not close `hardening_converged`

Per this series' own standard (round 9 → round 10, round 11 → round 12): a round that finds and
fixes a real gap is not the round that gets to certify nothing was found, because the fixes
themselves are unreviewed. Round 12 found and fixed one real P1 (the `lint_style.py` regression)
and, separately, the driver's own process caused and then corrected one BLOCKER-grade artifact error
(`submission-metrics.json`, AUT-PD-047) inside the same cycle. Both are fixed and verified as of this
commit, but neither has been reviewed by a fresh blind seat. **Round 13 (AUT-PROP-041, queued)** is a
confirmation pass on these two fixes at whatever commit is final once nothing else is mid-flight
against the ASO family — the same shape as this round was for round 11.

## Process note: a subagent mutation-window incident, and its cascade

Mid-round, the driver caught an unstaged, unexpected two-token edit to the live tracked article file
that it had not made — a subagent (evidence points to seat 1) editing the live tree instead of the
scratch copy it was explicitly instructed to use. Caught only because the driver staged its own
unrelated fix by path rather than `git add -A`; reverted before any commit contained it. Separately,
minutes later, the driver's own regeneration of `submission-metrics.json` (fixing what looked like
ordinary stale-artifact drift) ran against the live tree during this same contamination window and
silently captured the mutated word count, landing a wrong value in commit `6e7d44e06` — caught two
commits later by seat 4's independent re-derivation against an isolated pinned-commit worktree, and
corrected in `3a53478a8`. Full root-cause and the generalisable lesson (verification-after-the-fact
worked; `git add -A` avoidance alone does not protect a live-tree-reading regeneration script run
concurrently with mutation-risk subagents): process defect **AUT-PD-047**.
