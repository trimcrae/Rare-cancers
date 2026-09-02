---
id: DOC-VIEW-RT-FUSION-OUTPUT
title: RT-FUSION-OUTPUT — The fusion's transcriptional output, read in EMC tissue
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Do the genes an NR4A3 chimera is published to bind read higher in EMC tumour tissue than in comparator tumours — beyond what an arbitrary gene set of the same size achieves on the same platform?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-FUSION-OUTPUT — The fusion's transcriptional output, read in EMC tissue

**Family:** [ST-DISSEMINATION](L1-st-dissemination.md) · **state:** ✓ active · validated_in_silico · confidence moderate · verified 2026-08-08

**Grade** (owned by [`research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md`](../../research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md#6--conclusion)): THE RESULT IS AN INSTRUMENT, and the biology is its worked example. A size-matched empirical null drawn from a platform's own genes is the required calibration for any gene-set read on a small rare-tumour series: on GSE4303/GPL3290 almost every set anyone scores comes back higher in EMC, because a set's per-sample score is one draw from a distribution whose width depends on set SIZE and platform rather than biology (an arbitrary 19-gene set can print t=3.16 and be indistinguishable from random). It costs one seeded resampling and is not EMC-specific. Applied here it refuses this work's OWN aggregate — 39% and 88% of threshold — while the published EMC phenotype clears the same threshold 11.9-fold and 4.2-fold in the same run, so the instrument demonstrably reads the disease and not the set. Calibrated, the three class-A genes separate rather than reading alike: ENO3 survives exact label permutation on both array platforms after multiple-testing correction (q 0.0004 / 0.0006), every comparator stratum including the myxoid-matched and reference-pool-matched arms, the 98th percentile of 14,120 genes in the independent 3SEQ deposit, and a skeletal-muscle admixture control; PPARG's strongest reading is CIRCULAR (GSE4303 is the cohort that first published high PPARG in EMC) and what remains fails correction; SEMA3C survives nothing and reverses sign with the comparator (+1.66 vs LGFMS, -0.65 vs desmoid). ⚠ ENO3 was the PRE-DESIGNATED POSITIVE CONTROL, so its elevation is not an independent finding of this work, and the ordering rests on cohorts of 4, 6 and 10 — it demonstrates that the instrument discriminates, and is not settled biology. The binding constraint on the biology is not sample size: class A is three genes wide and no experiment has measured where an NR4A3 fusion binds, or what chromatin does, in EMC material — a bounded statement about what has been deposited under a label an archive indexes, not a claim that no such data exists anywhere. ⚠ RETRACTED AND NARROWED 2026-08-08: that ceiling previously read 'no genome-wide chromatin experiment performed with an NR4A3 fusion was retrieved in 2,276 full-text documents across five committed corpora', and a wider search across the primary sequence archives found one — GEO GSE243553 (PMID 39048711), a pooled single-cell ATAC screen in HEK293T whose 116-member library carries EWSR1-NR4A3, TAF15-NR4A3, TCF12-NR4A3 and TFG-NR4A3 with full-length wild-type NR4A3 and the reciprocal NR4A3-EWSR1 as controls. The corpus count was correct and is unchanged; the INFERENCE from it to an absence is what fails. GSE243553 is accessibility and not occupancy, HEK293T and not EMC, so the ceiling stands in the narrower form. ⭐ Sharpest form, comparative: the field performs this experiment routinely for the sibling fusions — ChIP-seq for EWSR1::WT1 and EWSR1::ATF1, ATAC-seq for EWSR1::FLI1 and FUS::DDIT3, ChIP-seq twice for HEY1::NCOA2 — and has never performed it on EMC material. Search record: research/manuscripts/fusion-output/nr4a3-cistrome-search-2026-08-08.md. MEASURED 2026-08-08: there is also no consensus to correct — the three genes are named in 3, 1 and 0 of 261 EMC review records, while the primary sources themselves are ordinary references of this literature (42-70% of their citations are EMC records; four to six EMC reviews each).

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

EMC is defined by an NR4A3 fusion, so the disease's central molecular hypothesis is that the chimera is a transcription factor with an aberrant output. Two questions are routinely conflated in the field's prose: which genes has anyone shown an NR4A3 chimera to physically BIND and drive, and which genes are HIGH in EMC tumours. The first is a mechanism claim and the second is an association that EMC's cell of origin, its myxoid architecture, or a generic matrix programme could produce on its own. Cataloguing the mechanism claims with their evidence type recorded per gene, and then reading them back in tumour tissue against an explicit calibration for what an arbitrary gene set does on the same platform, separates the two as far as public data allow — and states precisely where the separation stops.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `EV-PMC6766969` | SEMA3C as the single best-evidenced direct target of EWSR1::NR4A3 — a human cell background, the actual EWSR1 chimera, and a chromatin-binding assay (ChAP-qPCR); and the measurement that the TAF15 chimera does NOT retain that binding, which is half of why native-to-fusion transfer cannot be assumed | `direct` |
| `EV-FILION-2009` | PPARG as a fusion-transactivated promoter with a band-shift, a luciferase reporter and a single-nucleotide NBRE mutant behind it; the never-cited negative result in the same paper that native NR4A3 and NR4A3ΔC do NOT activate that promoter; and Table 1, whose 21 mappable genes replicate cross-platform and cross-cohort at p_emp 0.0005 on both readable series | `direct` |
| `EV-SUBRAMANIAN-2005` | the GSE4303 / GPL3290 cohort itself (10 EMC on a 42,000-spot two-colour cDNA platform), and — read from the fetched GEO series record rather than inferred from sample counts — the confirmed circularity of scoring Filion Table 2 on that platform, which is why only Table 1 is used as a replication test | `direct` |

## Remaining unknowns

- ⛔ THE CENTRAL ONE. Whether the fusion DRIVES any of the genes that read high in EMC. Every reading here is consistent with the fusion driving them and equally consistent with EMC's cell of origin expressing them, with EMC's myxoid hypocellular architecture against dense comparator sarcomas, or with the genes being generic matrix or proliferation genes. The size-matched null removes the platform offset and part of the generic-gene explanation and removes neither of the first two, and nothing available at $0 does.
- Whether the class-A set is three genes wide because that is the biology or because nobody has looked. Measured 2026-08-08 across GEO, SRA, BioProject, BioSample, ArrayExpress/BioStudies, ENA and ChIP-Atlas: nothing has been deposited on EMC material under any chromatin library strategy, so no experiment has measured where an NR4A3 fusion binds in EMC chromatin — while the same archives hold chromatin maps for EWSR1::WT1, EWSR1::ATF1, EWSR1::FLI1, FUS::DDIT3 and (twice) HEY1::NCOA2, and hold one accessibility screen carrying four NR4A3 fusions in HEK293T (GSE243553 — accessibility, not occupancy, and not EMC). The set's width is therefore a fact about what has been deposited under a label an archive indexes, and not yet a fact about the fusion.
- Whether sign concordance across six array readings and three genes means anything a coordinated programme would predict. Three individually EMC-associated genes predict the same pattern, and with three genes the two explanations are not separable.
- Whether the fusion-type mixture is attenuating a real signal or hiding a reversal. No readable series records which fusion each EMC sample carries, and Brenca et al. show EWSR1- and TAF15-translocated EMC differ transcriptionally, so every EMC arm here is a mixture of unknown composition.
- Whether the PPARγ activity reading is receptor output or adipogenic differentiation. The occupancy-derived arm and the adipogenesis process proxy are both set-specific UP on both platforms and share 44 genes (23% of the smaller set), and these data cannot separate them.
- Whether any of this holds at protein level. Every reading is transcript-level in bulk tissue, and SGK1 is the worked example of a gene whose published protein and transcript directions oppose.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The instrument must recover known published answers on these exact platforms before any set score is read — a positive control, a tumour-identity control, a directional falsifier with a published DOWN prediction, and a transcript/protein discordance control. ✅ DONE 2026-08-07, run 31200817686: all four agree on every platform where a contrast could be computed, `all_checks_pass: true`, zero disagreeing | V1 | yes | — |
| Any raw 'higher in EMC' contrast must be refused unless it clears a size-matched empirical null drawn from the same platform's own genes. ✅ DONE — 4,000 seeded draws per set per platform; the refusal fired on this route's own aggregate class-A+B set on both platforms and is reported rather than worked around | ⛔ none built | yes | — |
| An NBRE motif scan of the regulatory windows of the genes that read high, against a composition-matched background. Sequence work: no new data, no dispatch, no money. It cannot demonstrate binding, but a set of up-in-EMC genes with NO NBRE enrichment would be a real negative. DONE 2026-08-07 and reported as §3.10 of the manuscript: a -10kb/+15kb window fixed in advance, scanned on both strands with positional de-duplication, calibrated against a 2,000-shuffle dinucleotide-preserving null AND a 198-window GC-matched background panel. ENO3 carries 4 exact NBREs and clears both nulls (p 0.034 and 0.018); PPARG carries 3, which is what its composition predicts; SEMA3C carries none, and its one-mismatch count — the class Brenca et al. actually report — is also exactly what its composition predicts. A motif is not occupancy and the scan is reported as a prioritisation, never as a target-gene claim. | ⛔ none built | yes | — |
| An NR4A3 ChIP-seq peak set with the FUSION expressed, intersected with these expression reads: a gene up in EMC that carries a fusion-bound NBRE in its regulatory region is driven, and a gene up with no peak is correlated. ⛔ No such dataset was retrieved. The nearest available (Haller et al. 2019, PMID 30664630; processed data Zenodo doi 10.5281/zenodo.1483691, open) is NATIVE NR4A3 in acinic cell carcinoma, not a fusion — and given the measurement that native NR4A3 does not activate the PPARG promoter the fusion does, it answers a different question and must never be cited as answering this one | ⛔ none built | **no** | — |
| Fusion knockdown or degradation in a genuinely fusion-positive EMC model, with RNA-seq. No such experiment was retrieved in the corpora searched  ⭐ ADJUDICATED 2026-09-02 (AUT-PD-116, seat s31-emc-data-blocks). ⛔ BLK-NO-EMC-DATA IS CORRECT ON THIS ENTRY AND STAYS — a disagreement with S32's "wrong blocker" verdict, recorded rather than silently applied. Fusion knockdown or degradation in an EMC model read out by RNA-seq IS functional-genomics data, so a deposited EMC perturbation dataset would satisfy this entry without a lab, which is exactly the class the blocker's `retired_by_action` says would retire it. BLK-NO-WET-LAB holds it shut anyway, so keeping the blocker costs the route nothing. ⚠ THE RULE THIS APPLIES, THE FOURTH COHORT'S DESIGN AND LIMITS, AND THE PER-GENE COVERAGE ALL HAVE ONE HOME AND ARE NOT RESTATED HERE: research/modalities/emc-fourth-cohort-route-readout.json — its "⭐ the_rule_this_adjudication_applies" field, its cohort block, and per_route.RT-FUSION-OUTPUT. | ⛔ none built | **no** | BLK-NO-WET-LAB, BLK-NO-EMC-DATA |
| Fusion-type-stratified EMC expression data, so the EWSR1 and TAF15 arms can be read apart rather than as a mixture  ⭐ ADJUDICATED 2026-09-02 (AUT-PD-116, seat s31-emc-data-blocks). NOT ANSWERED, AND NO BLOCKER RECORD FITS IT — the residual is stated here instead of mis-filed, following the `BLK-NO-CURATED-CLINICAL-DATA` precedent in which two routes ended the same correction with no blocker at all. Neither array series carries a fusion-partner label: `sample_annotations_verbatim` contains EWSR1, TAF15 and "fusion" zero times in both. ⭐ NEW 2026-09-02 AND IT DOES NOT CLOSE THIS: the fourth cohort carries a per-run EWSR1 break-apart FISH call (`emc-fourth-cohort-quant.json → per_run.<run>.ewsr1_break_apart_fish`, 8 rearranged / 4 not). ⛔ A break-apart call is REARRANGED-VERSUS-NOT, not a partner identity — it does not separate an EWSR1 arm from a TAF15 arm, and an EWSR1-negative case is not thereby a TAF15 case. TAF15 has an assigned probe in that cohort; EWSR1 and NR4A3 do not. What this entry needs is a cohort with PARTNER calls. ⚠ THE RULE THIS APPLIES, THE FOURTH COHORT'S DESIGN AND LIMITS, AND THE PER-GENE COVERAGE ALL HAVE ONE HOME AND ARE NOT RESTATED HERE: research/modalities/emc-fourth-cohort-route-readout.json — its "⭐ the_rule_this_adjudication_applies" field, its cohort block, and per_route.RT-FUSION-OUTPUT. | ⛔ none built | **no** | — |

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) | what is being asked of the PPARγ axis | — | RT-PPARG-DOWNSTREAM asks whether a PPARγ-directed AGENT could act on a downstream effector, and is held up by the unresolved DIRECTION of that intervention. This route asks only whether the receptor's target genes are co-ordinately elevated in EMC tissue against a size-matched null. It supplies an input to that route and answers none of its question: §3.9 of the manuscript states in terms that an activity reading says nothing about the direction of any pharmacological intervention. |
| [RT-METHODS-PAPER](L2-rt-methods-paper.md) | what the paper is a record OF | — | RT-METHODS-PAPER is a record of instruments that FAILED their known-answer controls, in the degrader program. This route's instrument PASSED all four of its known-answer controls and returned a positive per-gene reading. Both sit in ST-DISSEMINATION and they are the two halves of that family's thesis, not one route described twice. |
| [RT-DBD](L2-rt-dbd.md) | whether the DNA-binding domain is a TARGET or an EXPLANATION | — | RT-DBD asks whether the fusion's DNA-binding domain can be drugged and is closed. This route uses the fact that the DBD binds DNA to ask what it binds DNA NEAR, which is a measurement question that the closure of RT-DBD does not touch. |

## Readiness — what this could become today

**`journal_submission`**

The reviewer's first question — 'is any of this the fusion?' — still has no answer, and the paper says so rather than working around it. What has changed is that the result is no longer a bare sign-concordance reading over three genes: the three are now ORDERED by how much independent support each carries, one of them (SEMA3C) is shown to be an artefact of comparator choice, another (PPARG) has its strongest cell graded circular, and the surviving gene has been put through a confound audit that names and tests the specific alternative explanations. That is a journal-submission argument about what the field's direct-target catalogue actually supports. Raising it further needs a cistrome intersection, which is somebody else's experiment.

## Where this route ends — the paper

**[PUB-FUSION-OUTPUT](L3-publications.md)** — [Almost every gene set reads higher in the index arm: a size-matched empirical null for small rare-tumour expression series, and what it leaves of the EWSR1::NR4A3 direct-target catalogue](../../research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md)

`primary` · ◐ `drafted` · aimed at `journal_submission`

**This route contributes:** The whole paper: the evidence-typed catalogue of every published NR4A3 / NR4A3-fusion transcriptional target with the verbatim sentence per gene, the size-matched empirical null that makes any gene-set read on these platforms interpretable, the four instrument controls, the three-cohort per-gene concordance reading with its ceiling, and the measured absence of any retrieved NR4A3-fusion cistrome.

**The paper would claim:** A gene-set read on a small rare-tumour expression series is uninterpretable until a size-matched random set drawn from the same platform's own genes has been scored beside it — and that calibration, which costs one seeded resampling and is not specific to any disease, refuses the very set this paper assembles. Applied to the EWSR1::NR4A3 direct-target catalogue (three genes across 2,276 retrieved full-text documents), the aggregate reaches 39% and 88% of its null threshold and does NOT clear, while the published EMC phenotype clears the same threshold 11.9-fold and 4.2-fold in the same run. Calibrated, the three genes separate rather than reading alike; the surviving gene is the pre-designated positive control and is therefore not an independent finding. No experiment has measured where an NR4A3 fusion binds, or what chromatin does, in EMC material — a negative the field's own habits sharpen, since it runs exactly that experiment for EWSR1::WT1, EWSR1::ATF1, EWSR1::FLI1, FUS::DDIT3 and (twice) HEY1::NCOA2 — so no gene named can yet be told apart from one merely associated with the disease, and the paper specifies the experiment that would settle it.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The measurement has run, the instrument passed its known-answer controls, and the manuscript is drafted. The one remaining free step — the NBRE promoter scan — costs $0 and is startable as written. Nothing about this route gets cheaper or easier by waiting, and the thing that WOULD change it (a fusion cistrome) is somebody else's experiment, which is a reason to publish the reading rather than to sit on it.

| horizon | effect |
|---|---|
| Six months | Small, unless someone deposits a fusion cistrome. The two array series and the 3SEQ deposit are all decade-old public data and will not improve. |
| Two years | Potentially decisive, and in one direction only: an occupancy map of an NR4A3 fusion in EMC chromatin would convert every per-gene concordance here into either a driven-gene claim or a correlation, and nothing else would. ⚠ Narrowed 2026-08-08 from 'a genome-wide chromatin experiment with an NR4A3 chimera'. One of those now exists — GSE243553, chromatin accessibility in HEK293T — and it converts nothing here, which is precisely why the delta has to name the cell type and the channel rather than the method. |
| Cost trend | flat |
| Automation outlook | Fully automatable as re-analysis — the null draw is seeded, the pipeline is stdlib-only and the whole run costs $0 on CI. What is not automatable is the judgement that three genes of sign concordance is weaker than a set result, which is the sentence the pre-registration failed to write in advance. |

## Claim ceiling — what this route may NOT be used to claim

- n = 4, 6 and 10 EMC tumours across the three cohorts. Nothing here survives being described as a distribution.
- The three cohorts are never pooled and must never be: 3SEQ 3'-end read density is not array intensity, and GPL6244 single-channel intensity is not GPL3290 two-colour log-ratio. The concordance is sign agreement across three independent measurements, which is weaker than a combined estimate.
- Transcript only. No protein abundance, no post-translational state, no subcellular localisation.
- No occupancy in EMC, and therefore no causal attribution to the fusion for any gene named.
- The normal-tissue arm is a six-organ visceral panel, not matched adjacent tissue, so it cannot separate EMC-specific from mesenchymal-lineage-specific.
- The empirical null controls the platform offset and set size, not gene-gene correlation within a real pathway, so its p is anti-conservative for coherent sets and is a screen rather than a test.
- Uncorrected for multiple testing.
- ⛔ Nothing here is an efficacy, selectivity, safety, therapeutic-window or clinical-readiness claim for any agent, target or gene, and expression data cannot become that evidence.

*Inherited from [ST-DISSEMINATION](L1-st-dissemination.md), which is where these are asserted — a family limitation binds every route inside it.*

- A methods paper documents what was done and what failed. It makes no claim about whether any route would work.
- The failure record's value depends on it being complete and honest, including the results that went against the program's own thesis.

## Best next action

Submit. The free in-silico work on this route is done: catalogue, null calibration, instrument controls, three cohorts, exact permutation tests, the confound audit and the motif scan have all run, and the remaining question (does the fusion BIND any of these genes in EMC) cannot be answered from expression or sequence data at any price. The residual steps are author-only submission furniture — ORCID, a Zenodo DOI at the submitted commit, and completing the gene-set-resource bibliographic identifiers.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-FUS-T1](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

**L5 evidence:** [EV-FILION-2009](L5-evidence-base.md#evidence--the-literature-this-program-cites), [EV-PMC6766969](L5-evidence-base.md#evidence--the-literature-this-program-cites), [EV-SUBRAMANIAN-2005](L5-evidence-base.md#evidence--the-literature-this-program-cites)

[← ST-DISSEMINATION](L1-st-dissemination.md) · [← L0](L0-ecosystem.md)
