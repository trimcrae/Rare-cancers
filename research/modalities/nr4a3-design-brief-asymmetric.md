---
id: DOC-NR4A3-DESIGN-BRIEF-ASYMMETRIC
title: Q16 — the NR4A3 design brief, restated asymmetrically in its harder measured form
level: L4
kind: memo
status: generated
generator: research/modalities/design_brief_asymmetric.py
canonical_for: []
purpose: "State the selectivity brief as hard vs NR4A1 and hard-but-lower-priority vs NR4A2, both molecular, with each clause carrying its own measured sensitivity."
scope: A design TARGET assembled from committed readings. No free energy, no margin, no ratio, no window; no binding, degradation, selectivity, efficacy or safety statement.
audience: [maintainers, autonomous research agents]
date: 2026-08-07
last_verified: unverified
---

# Q16 — the design brief, restated ASYMMETRICALLY in its harder measured form

**Status.** A DESIGN TARGET assembled from committed readings. $0 CPU, pure stdlib, no new compute. No free energy, no margin, no ratio, no window. Nothing here is a claim about binding, reactivity, degradation, proteome-wide selectivity, efficacy, safety, a therapeutic window or clinical readiness.

## ★ The brief

> ### HARD vs NR4A1; HARD-BUT-LOWER-PRIORITY vs NR4A2. BOTH MOLECULAR.

### `B1` · NR4A1 — HARD

Spare NR4A1. The bound is a NAMED ANTI-TARGET GENOTYPE — the combined Nr4a1-/-;Nr4a3-/- mouse (postnatal lethality, complete penetrance), which is precisely the pair a non-selective NR4A3 degrader RECONSTITUTES. Single nulls do not do it.

**Why it outranks `B2`.** it is a combination genotype a molecule can create, not a developmental loss no molecule delivers.

**Instrument reading.** `SEPARATED at replicate granularity`

⚠ **Sensitivity.** this is the MANDATORY axis and its separation does NOT survive the contested C2 rule (RANKED but replicate ranges OVERLAP under the alternative ordering), the design-effect-corrected Wilson intervals OVERLAP, and the exact test sits at its design FLOOR. Carry the asymmetry; do not carry the word SEPARATED.

### `B2` · NR4A2 — HARD BUT LOWER PRIORITY

Spare NR4A2. ⛔ NOT a soft constraint: complete germline Nr4a2 loss produces neonatal lethality, complete penetrance (MP:0011087), primary-cited to PMID 9092472 / 9608532 across 3 independent null alleles, so there is a FLOOR under how much sparing is required and it is evidenced rather than precautionary. It ranks BELOW NR4A1 only because NR4A1's bound is a combination genotype a degrader reconstitutes, while this one is complete developmental loss, which no degrader delivers.

**Instrument reading.** `RANKED but replicate ranges OVERLAP`

⚠ **Sensitivity.** this is the BEST-EFFORT axis and its replicate ranges OVERLAP even under the frozen rule — it is a RANKING with a stated effect size (Cliff's delta 0.777778), never a separation.

### `B3` · BOTH MOLECULAR — the exposure lever is withdrawn

Neither half may be discharged by tissue distribution. Across 51 tissues with all three paralogues quantified, NR4A2 and NR4A3 are co-expressed in 47, NR4A2 is dominant in 0 and unbuffered in 0. There is no tissue in which the anti-target is present and the target is not. ⇒ selectivity has to be MOLECULAR, and the residual is DISCLOSED rather than discharged.

⚠ **Sensitivity.** ⛔ THIS TABLE IS NOT EVIDENCE AGAINST A DOPAMINERGIC REQUIREMENT AND MAY NEVER BE QUOTED AS SUCH. A bulk tissue average dilutes the substantia nigra pars compacta — of order 10^5 neurons — to invisibility, so a low pooled nTPM in a brain region says nothing about it. What the table measures is exposure BREADTH: wherever NR4A2 is present above the cut, a non-sparing degrader would act on it.

**What would reopen it.** single-cell or region-resolved expression, and a CNS-exposure measurement for a real candidate molecule. Neither exists here.

### `B4` · THE CEILING ON ALL THREE

A germline knockout bounds DEVELOPMENTAL, COMPLETE, LIFELONG loss. A degrader is ADULT, TRANSIENT, INCOMPLETE loss of a protein, and no source read here measures that. So every genotype above sets a CEILING OF CONCERN, never an expected effect — and an absent knockout record is an absence of evidence, not evidence of tolerability.

⚠ **Sensitivity.** A germline mouse knockout bounds DEVELOPMENTAL, COMPLETE, LIFELONG loss of a gene. A degrader is an ADULT, TRANSIENT, INCOMPLETE loss of a protein, and no source read here measures that. So a KO phenotype -- lethal or not -- sets the ceiling of concern, never the expected effect of a molecule; and an absent KO record is an absence of evidence, not evidence of tolerability. This repo additionally holds no measured or predicted CNS-penetration datum for any NR4A candidate, so the exposure argument that would otherwise narrow the NR4A2 question is a property of a molecule that does not exist.

## ★ The asymmetry read — carried with its sensitivity, not as a word

**`lead_status`: LIVE BUT DEMOTED — the asymmetry is real, the word SEPARATED is not carryable**

| paralogue | axis | verdict under the frozen rule | survives the contested `C2` rule? | design-corrected Wilson intervals overlap? | Holm-adjusted one-sided *p* (floor 0.10) |
|---|---|---|---|---|---|
| NR4A1 | mandatory | SEPARATED at replicate granularity | False | True | 0.1 |
| NR4A2 | best_effort | RANKED but replicate ranges OVERLAP | False | True | 0.1 |

⛔ The pooled verdict this replaces was `RANKED but replicate ranges OVERLAP`, driven by **NR4A2**.

## The NR4A2 bound

- **Decision:** `BOUNDED`
- **The floor:** neonatal lethality, complete penetrance (`MP:0011087`), PMID 9092472 / 9608532, on 3 independent null alleles; 38 single-gene annotations
- **The exposure lever:** NR4A2 and NR4A3 co-express in 47 of 51 tissues; NR4A2 is DOMINANT in 0 and UNBUFFERED in 0. There is no tissue in which the anti-target is present and the target is not, so tissue distribution cannot separate them and the selectivity has to be MOLECULAR.

⚠ ⛔ THIS TABLE IS NOT EVIDENCE AGAINST A DOPAMINERGIC REQUIREMENT AND MAY NEVER BE QUOTED AS SUCH. A bulk tissue average dilutes the substantia nigra pars compacta — of order 10^5 neurons — to invisibility, so a low pooled nTPM in a brain region says nothing about it. What the table measures is exposure BREADTH: wherever NR4A2 is present above the cut, a non-sparing degrader would act on it.

## ⛔ Superseded, retained

- 'NR4A2 — a SOFT constraint … carry the residual as a DISCLOSED, UNSIZED EXPOSURE question' — the exposure half is withdrawn by measurement (47 of 51 tissues co-expressed, 0 dominant, 0 unbuffered), and the constraint is bounded rather than soft.
- 'NR4A2 — UNBOUNDED, in both directions' — bounded 2026-08-03 by MGI single-gene records.
- 'treat the residual as an exposure question rather than a chemistry one' — the lever the phrase hands off to does not exist.
- reporting the paralogue pocket contrast as ONE conjoined verdict — it is two, on two axes, with two different answers.
- the word SEPARATED, unqualified, on the NR4A1 axis — it does not survive the contested C2 rule and the artifact's own lead_status says so.

## ⛔ This brief contains no

- free energy
- ΔG_open or any opening penalty
- selectivity margin, ratio or window
- claim about binding, reactivity, degradation, proteome-wide selectivity, efficacy, safety, a therapeutic window or clinical readiness
- pose-, vector- or construct-specific statement

## ⛔ Pose marginalisation

**Rule.** no sentence in this brief may be re-specialised to a pose, a vector or a construct.

**Why it is statable today.** neither half is pose-conditional — the NR4A2 bound is registry and expression data, and the pocket contrast is a frame-fraction over unbiased ensembles rather than a docked pose. path-family-synthesis.md §4 records both source rows as inheriting NEITHER R3 NOR R5.

the pocket-contrast half is a RANKING on opening frequency. It is not a per-molecule claim and evidence of absence is not available at these ensemble sizes.
