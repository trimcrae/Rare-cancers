---
id: DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND6
title: "Round-6 swarm review of the fusion-junction ASO submission — findings, dispositions and the ledger that was written after the fact"
level: L3
kind: manuscript
status: live
canonical_for:
  - the round-6 swarm review of the fusion-junction ASO submission manuscript
purpose: >
  Hold the sixth adversarial review of fusion-junction-aso-research-article.md, whose findings and
  dispositions existed only in the body of commit 0108074dd. The reason for existing is the one the
  round-5 ledger states: a review whose findings are applied but not recorded gets re-run from
  scratch and its wrong leads get re-raised.
scope: >
  Claims, arithmetic and register of the submission manuscript at the commit named in the body. No
  screen was re-run for this review; it reads committed artefacts only.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-16
last_verified: unverified
---
# Round-6 swarm review of the fusion-junction ASO submission

**Ledger written 2026-08-16, after the fact.** Round 6's findings and dispositions existed only in the
body of commit `0108074dd`. That is the failure this repository already named once — commit `e4a3a654c`,
*"a quote living in a commit"* — and it matters here for a specific reason: the round-5 ledger exists
so that **round 6 would not re-raise its wrong leads**. Round 6 leaving no ledger meant round 7 would
inherit nothing. This file is reconstructed from its primary sources, which are the commit body,
`research/manuscripts/tests/test_round6_fixes_landed.py`, and the diff itself. Where this ledger states
a count it is taken from those sources, not recalled.

- **Reviewed:** `research/manuscripts/aso/fusion-junction-aso-research-article.md` as revised by round 5.
- **Method:** nine independent reviewers, no cross-talk, refute-by-default verification. Same
  methodology as round 5, deliberately, so the two rounds are comparable.
- **Applied in:** `0108074dd`. **Merged in:** `dc1f440e9`.

---

## 1 · The finding that matters more than any individual defect

> **The review step converged. The application step did not, and nothing was checking it.**

Almost nothing round 6 found was a defect round 5 missed in text it reviewed and left alone. Nearly
everything it found was either **caused by round 5's own fixes**, or was **a fix reported as applied
that never landed**.

This inverts the natural reading of a round that returns a full page of blockers. The blockers were not
evidence that the reviewers were missing things. They were evidence that **an unverified apply step is
where defects enter**, and that six rounds of review had been pointed at the wrong half of the loop.

## 2 · Reported fixed, still broken

| # | defect | what actually happened |
|---|---|---|
| 6.1 | **The sign error in the margin/parent-DNA relation lived in five places** | Round 5 corrected the manuscript, added a regression guard **that watched only the manuscript**, and declared it closed. It survived in the artifact, in both generators, and in the generated tables markdown that `build_submission_pdf` bundles into the deposit. |
| 6.2 | A false load superlative | Reported closed in the round-5 commit body. Never touched. |
| 6.3 | A partner claim true only at the default search depth | Reported closed in the round-5 commit body. Never touched. |
| 6.4 | A citation defect | Applied in a way that **introduced a fresh false statement** about a citation, in the fix for a citation defect. |

⛔ The generalisable form: **fixing one copy of a fact is not fixing the fact.** A guard that watches one
of five homes reports green on a paper that still ships the defect.

## 3 · Defects the round-5 fixes themselves created

| # | defect |
|---|---|
| 6.5 | **The selectivity ratio was defined in the direction opposite to its own cut and its own estimators**, so a perfectly selective reagent scored as *falsifying* the ranking. |
| 6.6 | Its limit-of-quantification guard named the wrong term. |
| 6.7 | Its fallback estimator is bounded above by one over the fusion knockdown's complement, so **at the knockdown depth the paper's own cited precedent reports, it cannot reach the cut however selective the reagent is.** |
| 6.8 | Three replicates against that cut cannot falsify at all once the replicate SD of log selectivity exceeds about 0.65. |
| 6.9 | The optional contrast arm was said to move margin alone, while GC left the paper's own 40–60% window, gap-paired load fell 123 → 34, and its parent-paired nucleotides fell on the donor rather than on the transcript the readout measures. |
| 6.10 | A sentence promising no reagent is named at the *PGR* seam sat twenty-four lines above one naming it. |

All corrected in `0108074dd`, **in every home**, with the derived artifacts regenerated rather than
hand-edited.

## 4 · The two instruments this round produced

These outlast the findings, and are the reason round 6 was worth running even though its class-B count
was near zero.

**`research/manuscripts/tests/test_round6_fixes_landed.py`** asks the two questions the round-5 pass
never did: *did the corrected text arrive*, **and** *is the defective text gone from every home*. A
guard that asks only the first passes on a paper that still ships the defect.
⚠ **It caught itself first.** Its repository root resolved one directory short, so all fifteen checks
passed **by skipping** — the same fail-quiet shape it exists to catch. It now asserts its own path
resolution and fails rather than skips.

**`research/manuscripts/manuscript_inventory.py`** measures what an edit costs: every numeral,
oligonucleotide, PMID and scope-limiting construction, diffed against any git ref. Measured with it,
**rounds 5 and 6 together added 2,351 words and lost one incidental hedge and one incidental number.**

> Five review rounds ran on this paper and **every remit could only add.** Cutting was never unsafe —
> it was **unmeasured**, which is not the same thing. This instrument is what made the subsequent
> editorial pass a checkable operation rather than a brave one.

## 5 · Two guards were themselves holding defects in place

- One pinned *"the smaller half"* as required text where the counted quantity is the **larger**.
- The round-5 sign-error guard watched a single file.

Both corrected. ⚠ A substring-pinned guard is brittle in **both** directions: it can hold a defective
sentence in place, and it can report a protected sentence destroyed when the text merely gained italics.
Both failure modes have now occurred in this project.

## 6 · Declined, with reasons recorded rather than silently skipped

| finding | why declined |
|---|---|
| The junction-clustered interval | No artifact owns it; adding it would create an **unhomed number**, against rule 1. |
| The manifest's missing manuscript PDFs | Conflates the code-and-data archive with the bioRxiv upload. They are different deposits. |
| A `lint_claims` positive on ordinary English | A false positive that CI never sees; adopting it would train the linter to be ignored. |

## 7 · ⛔ WRONG LEADS — recorded so round 7 does not re-raise them

Round 5's wrong leads are in `fusion-junction-aso-paper-redteam-round5.md` §5 and remain closed. Round 6
added no reject-grade refutation of comparable weight to round 5's two.

⚠ **That absence is itself a result, and it was predicted in advance.** The round-6 pre-registration
recorded: *"Round 5's most valuable output was not a finding. It was two confident, precise,
well-evidenced findings being refuted… If round 6 produces nothing comparable, that is itself
informative."* It produced nothing comparable. The marginal review round is worth much less than the
first, because the first had a large unreviewed surface and the second did not.

## 8 · What this review did not do

- **No screen was re-run and no artifact regenerated for review purposes.**
- **It did not ask what the paper says twice.** Like every round before it, its remit could only add.
  The ~1,817 words of pure duplication later found by a structural read were invisible to nine
  independent reviewers reading forward, because **each copy is individually defensible where it sits.**
- It did not review the wet-lab ask as a document a laboratory would execute from; that gap is what
  the subsequent editorial pass and round 7 address.

## 9 · Gates

Nine gates pass. Two `lint_style` ERRORs in the application pass were introduced by the applier —
mid-sentence bold, repository register leaking into journal register — and **gate 5 caught them**.
