---
id: DOC-OPUS-CAMPAIGN-HOLD-HLA
title: "Paper-specific hold — the HLA population-coverage manuscript"
level: L4
kind: memo
status: live
purpose: >
  Record the completed adverse independent final review of the HLA population-coverage manuscript,
  the six findings root accepts, and the exact conditions for reopening.
scope: >
  L4. A hold and its evidence. It repairs nothing, regenerates no figure, fetches no frequency data,
  and authorises no publication act.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# ⛔ PARK_CURRENT_POPULATION_COVERAGE_MANUSCRIPT — `neoantigen/hla-coverage-emc.md`

**The one required independent final review is COMPLETE and ADVERSE.** Root read it in full and
accepts all six findings within the report's stated evidence limits: **five P1 and one P2**.

⭐ **Absence of wet-lab validation is NOT the reason for this hold.** The decisive blockers are
**source provenance, the population quantity being estimated, and its uncertainty**.

- **Frozen manuscript:** `research/manuscripts/neoantigen/hla-coverage-emc.md` at
  `6cd29f876b11492e01f4e2ea10752e1bf0dbc4f4`, **47,368 bytes**, sha256
  `768398917208449a088c6d2aa9549d9162b4bbc9aa1c3584d13a55c1ac45af0c`.
- **Report:** 31,958 bytes, sha256 `eed64766bc372decbdea40584df54b68c3dcae20e3826308d80bbaa46d5331db`,
  completed `2026-09-08T18:13:03.660864Z`. Root independently verified the hash, read the verdict and
  completion record, **viewed the exact frozen PNG against the current curve JSON**, and checked the
  dynamic imports and the novelty filter named below.
- **The review:** `/root/hla_final_ultra`, `gpt-6-astra`, `ultra`, `fork_turns: none`. It describes
  independence from authoring **without claiming blindness to the supplied handoff**. ⛔ No backend
  attestation and no token measurement is asserted. All **33** frozen input copies matched their Git
  bytes in the completion record.

## The six accepted findings

**HLA-F1 · P1 · original source provenance is insufficient.** Mutable branch URLs, unretained
frequency and region snapshots, no upstream revision or retrieval date, and no auditable included
survey rows do not support the manuscript's "pinned and re-runnable" claim. ⚠ **Correct table readout
from committed JSON is not reproduction of the observations.** The twelve-file dependency handoff also
missed the reached dynamic imports of `junction_aso` and `fusion_breakpoints` and their retained
inputs — root read the actual imports. The current code's **52-allele default** and the cached
historical **34-allele A/B scan** must not be described as the same computation. ⛔ These are
frozen-scope findings, **not** a claim that originals are globally nonexistent or fabricated.

**HLA-F2 · P1 · the population interpretation and its uncertainty are not established.** Different
allele-specific blends of heterogeneous surveys have no justified target-population weights, no common
sampling panel and no verified overlap handling. Applying Hardy-Weinberg **after** pooling differs
from averaging modelled carriage **within** surveys. Transforming all lower and upper marginal Wilson
bounds does not establish a calibrated 95% interval for the multi-allele population union. Neither a
patient-event pooling policy nor complete allele presence proves conservative inference or comparable
sampling. ⚠ **The direction of total empirical bias and of the confidence-band miscalibration remains
UNKNOWN.**

**HLA-F3 · P1 · a bounded mathematical defect remains in the carrier model.** For two mutually
exclusive alleles at one locus under the stated diploid model, the probability of neither is
**`(1 − p − q)²`, not `(1 − p)²(1 − q)²`**; with all other assumptions held fixed the latter
understates the union. ⛔ The review's **0.332693 percentage-point** global difference is a
**diagnostic on retained rounded inputs** — not a corrected empirical coverage estimate, not a
direction for total real-world bias, and not a licence to call the current result conservative. A
caveat cannot make the implemented expression the claimed probability.

**HLA-F4 · P1 · the figure contradicts the current data.** Root viewed the exact 97,719-byte PNG,
sha256 `ff10a8bc438a55a52c968b5b0a522e65008474bd41925181f27e729440473609`: it shows **twenty** allele
positions, a global endpoint visually around **85%**, and Northern Europe above **90%**. The current
JSON holds **four** alleles and endpoints **30.40%** global and **61.10%** Northern Europe, with no
80/90/95% threshold reached. ⚠ The approximate visual readings are **not** recovered numerical data.
This is a substantive **wrong-result image**, not typography. ⛔ Preserve the original; replacing or
withdrawing the outgoing figure would be necessary in a later authorised revision and **does not
resolve F1 or F2**.

**HLA-F5 · P1 · novelty and biological claims exceed the actual tests.** Root read the novelty
filter: it excludes peptides present in **the two parental proteins**, not the entire human proteome.
Proteome-wide absence, a categorical weaker-T-cell-response claim, and broad commercial or biological
generalisations are unsupported by this analysis. ⭐ **No new sequence, proteome search or experiment
is needed merely to withdraw an overclaim.** ⛔ The reviewer investigated and dismissed the suggested
leading-N / wild-type-fragment objection — **do not revive it**.

**HLA-F6 · P2 · panel selection, regional comparisons and operational methods are incompletely
scoped.** The base result uses a best-per-peptide selection from **ten** class-I alleles, while the
retained expanded matrix also contains an **e7::e3 A\*30:02** prediction — so "single allele" cannot
describe all existing predictions. The **60.43–1.37%** headline mixes complete and partial allele
sets, and **14.04%** is the smallest stored value among the **thirteen** complete-set rows, not a
newly validated population estimate. Preserve the partial rows and UNKNOWN; describe base and expanded
panels **separately** without inventing a new e7::e3 coverage; report the actual retained rank and
affinity definitions and model versions, distinguishing **predicted presentation ranking from observed
presentation**.

## What remains supported, and closed

The **122 offline checks pass**, after an explicitly preserved reviewer-harness percent-format
correction; the original failed harness and results and the corrected run's original logs are
retained. ⚠ That confirms **table transcription and particular algebra and input relationships** — not
population representativeness, not nominal confidence coverage, and not predictor validity.

Still supported as artifact descriptions: the corrected e7::e3 maximum and CD4 minimum, the
three-incomplete / thirteen-complete rule, the four small survey bases, and the one qualifying
class-II allele in the retained 23-allele screen. The **1.78%** product already discloses its
mismatched antigen scopes, and ⛔ **no new same-junction computation is requested to repair a warning
that is already correct**. The construct description matches retained data and does **not** establish
biological activity. Current declarations and ethics wording exist, so **stale handoff gaps 6 and 9
are not current manuscript defects**. The historical source map has **242 lines / entries, not 242
independently verified numeric rows**. ⛔ No superseded anticorrelation, no earlier three-allele
class-II defect and no deleted-HW1-fragment investigation is reopened.

## Exact reopening conditions

For the **current population-coverage scope**: identifiable original source snapshots or exact
immutable upstream inputs with auditable included survey records; a defined target population with
defensible pooling, overlap, resolution and missingness handling and an uncertainty method; a
**locus-correct carrier model** with explicit residual-dependence assumptions; and the figure and all
panel, regional, novelty and biological claims aligned with that evidence. ⚠ **A newly acquired
versioned dataset would be a different analysis, not restoration of an unknown historical snapshot.**

A **different future technical audit** of the frozen outputs and their limitations is possible **only
after explicit root/author merit adjudication** of its reduced contribution. It would remove
human-population, eligibility and calibrated-confidence claims and treat the old percentages as
illustrative pipeline outputs. ⛔ **This is not an immediate rewrite assignment.** Clean style, more
generic tests, a new figure or another unchanged review cannot clear the core source and method hold.

⛔ **Not authorised now:** any new raw-frequency search, prediction, construct, biological experiment,
scientific producer run, figure rebuild, source re-audit, or same-paper polishing cycle.

## Boundary for the other neoantigen-adjacent papers

`BLK-ANTIGEN-COLD` stays intact as a separate experimental limitation. ⚠ It does **not** create an
automatic wet-lab prerequisite for a defensible narrower computational paper, and **this review clears
no real presentation, immunogenicity, efficacy or eligibility claim**. ⛔ Any other manuscript —
including the fusion-junction neoantigen paper and the vaccine development path — **must not silently
reuse the held population-coverage claims**, and must not repair this paper.

## What this hold is not

⛔ Not a retraction, not a publication act, and not a programme-wide blocker. It binds this paper, and
no user action follows from it.
