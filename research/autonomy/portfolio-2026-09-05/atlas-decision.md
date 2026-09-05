---
id: DOC-ATLAS-PRIORITY-DECISION-20260905
title: Deprioritize the standalone EMC therapeutic-address atlas
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Decide whether current evidence supports continued standalone atlas development.
scope: Scientific priority decision; no target rejection, clinical claim or publication clearance.
audience: [maintainers, autonomous research agents]
---

# Decision

**Deprioritize the standalone, independently validated EMC therapeutic-address atlas for now.** Preserve the existing resource and verified audits, but stop further atlas analysis and manuscript development until a named evidence improvement changes its expected contribution. This supersedes its provisional first place in the earlier portfolio. No alternative paper is automatically declared feasible or ready.

The atlas was prioritized for a specific contribution: independent EMC tissue evidence, appropriate normal-tissue comparisons, and robust target-selection conclusions that would guide experimental validation. The completed feasibility audit and primary-source check do not establish that contribution. This is a comparative research judgement about the present program, not proof that no useful atlas can ever be built.

## Evidence behind the decision

- The [completed worker audit](../../modalities/atlas-independent-normal-feasibility.md) distinguishes twelve proposed contrasts. Different cohort accessions do not prove different patients; explicit overlap documentation remains absent from the audited material. This is unresolved overlap, not demonstrated duplication. A patient-level crosswalk is one possible resolution; credible independent recruitment/provenance or genotype evidence could also suffice. We do not impose an impossible requirement to prove universal absence of overlap.
- The primary GSE28866 matrix is actually retrievable. The coordinator downloaded and parsed all 36,048 peak rows, with numeric values in all four EMC and 27 normal-library columns. Missing per-library cache values are therefore **not** a reason to abandon the project. File hash, column identities and retrieval evidence are preserved in the [cycle record](../cycle-outcomes/20260905T133448Z-6bd43b913c/atlas-primary-matrix-availability.json).
- Its normal panel contains 17 adult libraries from five organs and ten fetal libraries. It does not provide a matched normal mesenchymal lineage comparison or broad adult organ coverage. Peak discovery was performed on pooled cancer libraries, and values were depth-scaled and square-root compressed. These facts limit interpretation as an unbiased normal-expression atlas or an absolute fold-change analysis. The [primary methods](https://link.springer.com/article/10.1186/gb-2012-13-8-r75) support these limits. The panel can still show expression in the sampled normal tissues; it cannot establish a therapeutic window.
- The independently rechecked [existing sensitivity result](../../modalities/surface-address-sensitivity.md) has **zero of eleven named addresses labelled stable-positive on both cached array platforms**. This is a finite deletion-sensitivity intersection, not a statistical test or biological veto. Comparator mixtures differ, and GSE4303 reference labels introduce an additional unresolved compatibility problem. Nevertheless, there is no already demonstrated robust cross-cohort lead to carry the proposed paper.
- The fourth cohort's supplied records lack a compatible normal arm. RNA measurements, even if expanded, cannot independently establish surface localization, accessibility or selective functional response. PRAME also requires peptide–HLA evidence rather than conventional surface-protein interpretation.

The combined problem is scientific strength, not download cost: further annotation and organ-stratified arithmetic could improve a descriptive resource, but currently offer an uncertain standalone advance over the existing sensitivity and tissue-marker literature. Removing the independent-validation claim and calling the remainder a finished atlas would change the proposed contribution to fit the available evidence. We will not do that.

## Reopening evidence and opportunity cost

Reconsider the atlas when evidence supplies a credible independent EMC validation cohort with compatible measurements, or orthogonal EMC tissue validation of a specific address together with a relevant normal-tissue comparison. Document recruitment/sample provenance sufficiently to bound overlap; do not demand a specific form of crosswalk if another valid source resolves it. A reproducible cross-cohort result with a clear experimental decision could also change the balance after the reference/annotation problems are resolved.

Do not commission more cache-readiness audits, indiscriminate expression reprocessing, or repeated paper reviews while these conditions remain unchanged. The next portfolio candidate is the externally measured fusion-junction oligonucleotide benchmark, whose paired knockdown/parent-sparing data gate remains unverified. Its higher current priority is conditional, not evidence of a successful benchmark. No new worker is launched by this decision.

## Completion evidence

The retry completed in 821.297 seconds. Coordinator checks independently verified all 220 source-pointer/file/value hashes, primary-matrix counts and adult-organ strata, array identifiers, the fourth-cohort alias discrepancy, and the sensitivity intersection. The generator's byte comparison passed in its frozen source context. The [collected cycle](../cycle-outcomes/20260905T133448Z-6bd43b913c/cycle.json) records bounded audit completion, not a completed paper. Normal settled preflight and integration are reported separately; no ultra submission pass was run because no paper is being submitted.
