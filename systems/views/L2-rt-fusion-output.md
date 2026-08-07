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

**Family:** [ST-DISSEMINATION](L1-st-dissemination.md) · **state:** ✓ active · validated_in_silico · confidence moderate · verified 2026-08-07

**Grade** (owned by [`research/manuscripts/nr4a3-fusion-transcriptional-output.md`](../../research/manuscripts/nr4a3-fusion-transcriptional-output.md#6--conclusion)): A measured, null-calibrated per-gene concordance result with an explicitly stated ceiling: all three genes carrying a DNA-binding assay against an NR4A3 chimera are positive-signed on both readable array platforms and in an independent third cohort, while the AGGREGATE target set does not clear its size-matched null on either array platform. The binding constraint is not sample size — it is that the class-A set is three genes wide and that no genome-wide chromatin experiment performed with an NR4A3 fusion was retrieved in 2,276 full-text documents across five committed corpora, which is a bounded statement about a search rather than a claim that none exists.

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
- Whether the class-A set is three genes wide because that is the biology or because nobody has looked. No genome-wide chromatin experiment performed with an NR4A3 chimera was retrieved in 2,276 full-text documents across five committed corpora, so the set's width is a fact about the retrieved literature and not yet a fact about the fusion.
- Whether sign concordance across six array readings and three genes means anything a coordinated programme would predict. Three individually EMC-associated genes predict the same pattern, and with three genes the two explanations are not separable.
- Whether the fusion-type mixture is attenuating a real signal or hiding a reversal. No readable series records which fusion each EMC sample carries, and Brenca et al. show EWSR1- and TAF15-translocated EMC differ transcriptionally, so every EMC arm here is a mixture of unknown composition.
- Whether the PPARγ activity reading is receptor output or adipogenic differentiation. The occupancy-derived arm and the adipogenesis process proxy are both set-specific UP on both platforms and share 44 genes (23% of the smaller set), and these data cannot separate them.
- Whether any of this holds at protein level. Every reading is transcript-level in bulk tissue, and SGK1 is the worked example of a gene whose published protein and transcript directions oppose.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The instrument must recover known published answers on these exact platforms before any set score is read — a positive control, a tumour-identity control, a directional falsifier with a published DOWN prediction, and a transcript/protein discordance control. ✅ DONE 2026-08-07, run 31200817686: all four agree on every platform where a contrast could be computed, `all_checks_pass: true`, zero disagreeing | V1 | yes | — |
| Any raw 'higher in EMC' contrast must be refused unless it clears a size-matched empirical null drawn from the same platform's own genes. ✅ DONE — 4,000 seeded draws per set per platform; the refusal fired on this route's own aggregate class-A+B set on both platforms and is reported rather than worked around | ⛔ none built | yes | — |
| An NBRE motif scan of the promoters of the genes that read high, against a matched background. Sequence work: needs no new data, no dispatch and no money. It cannot demonstrate binding, but a set of up-in-EMC genes with NO NBRE enrichment would be a real negative. NOT DONE | ⛔ none built | yes | — |
| An NR4A3 ChIP-seq peak set with the FUSION expressed, intersected with these expression reads: a gene up in EMC that carries a fusion-bound NBRE in its regulatory region is driven, and a gene up with no peak is correlated. ⛔ No such dataset was retrieved. The nearest available (Haller et al. 2019, PMID 30664630; processed data Zenodo doi 10.5281/zenodo.1483691, open) is NATIVE NR4A3 in acinic cell carcinoma, not a fusion — and given the measurement that native NR4A3 does not activate the PPARG promoter the fusion does, it answers a different question and must never be cited as answering this one | ⛔ none built | **no** | — |
| Fusion knockdown or degradation in a genuinely fusion-positive EMC model, with RNA-seq. No such experiment was retrieved in the corpora searched | ⛔ none built | **no** | BLK-NO-WET-LAB, BLK-NO-EMC-DATA |
| Fusion-type-stratified EMC expression data, so the EWSR1 and TAF15 arms can be read apart rather than as a mixture | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) | what is being asked of the PPARγ axis | — | RT-PPARG-DOWNSTREAM asks whether a PPARγ-directed AGENT could act on a downstream effector, and is held up by the unresolved DIRECTION of that intervention. This route asks only whether the receptor's target genes are co-ordinately elevated in EMC tissue against a size-matched null. It supplies an input to that route and answers none of its question: §3.9 of the manuscript states in terms that an activity reading says nothing about the direction of any pharmacological intervention. |
| [RT-METHODS-PAPER](L2-rt-methods-paper.md) | what the paper is a record OF | — | RT-METHODS-PAPER is a record of instruments that FAILED their known-answer controls, in the degrader program. This route's instrument PASSED all four of its known-answer controls and returned a positive per-gene reading. Both sit in ST-DISSEMINATION and they are the two halves of that family's thesis, not one route described twice. |
| [RT-DBD](L2-rt-dbd.md) | whether the DNA-binding domain is a TARGET or an EXPLANATION | — | RT-DBD asks whether the fusion's DNA-binding domain can be drugged and is closed. This route uses the fact that the DBD binds DNA to ask what it binds DNA NEAR, which is a measurement question that the closure of RT-DBD does not touch. |

## Readiness — what this could become today

**`preprint`**

The result is a per-gene sign-concordance reading over three genes in cohorts of 4, 6 and 10, with the aggregate refused by its own null and no occupancy evidence in EMC. That is honest preprint content and it is not a journal-submission argument: a reviewer's first question — 'is any of this the fusion?' — has no answer here, and the paper says so rather than working around it. What would raise it is a cistrome intersection, not more writing.

**Missing:**
- the NBRE promoter scan, which is free and unstarted
- a cistrome measured with an NR4A3 fusion expressed — an open, unclaimed experiment rather than an unfetched dataset

**Evidence required:**
- occupancy evidence in a fusion-expressing cell, for any gene named

## Where this route ends — the paper

**[PUB-FUSION-OUTPUT](L3-publications.md)** — [Published transcriptional targets of EWSR1::NR4A3 are elevated in extraskeletal myxoid chondrosarcoma tissue across three cohorts and three platforms: an evidence-typed, null-calibrated re-analysis](../../research/manuscripts/nr4a3-fusion-transcriptional-output.md)

`primary` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The whole paper: the evidence-typed catalogue of every published NR4A3 / NR4A3-fusion transcriptional target with the verbatim sentence per gene, the size-matched empirical null that makes any gene-set read on these platforms interpretable, the four instrument controls, the three-cohort per-gene concordance reading with its ceiling, and the measured absence of any retrieved NR4A3-fusion cistrome.

**The paper would claim:** Across a retrieved corpus of 2,276 full-text documents, the set of genes any NR4A3 chimera has been shown to physically bind and drive is three genes wide — and those three read higher in EMC tumour tissue than in comparator tumours in every one of six array readings and in an independent third cohort on an unrelated technology, while the AGGREGATE target set does not clear a size-matched empirical null on either readable array platform and the published EMC transcriptional phenotype does clear it, on both. Reading a gene set in these EMC series is uninterpretable without that null calibration. No genome-wide chromatin experiment performed with an NR4A3 fusion was retrieved in that corpus, so no gene named can yet be told apart from a gene that is merely associated with the disease.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The measurement has run, the instrument passed its known-answer controls, and the manuscript is drafted. The one remaining free step — the NBRE promoter scan — costs $0 and is startable as written. Nothing about this route gets cheaper or easier by waiting, and the thing that WOULD change it (a fusion cistrome) is somebody else's experiment, which is a reason to publish the reading rather than to sit on it.

| horizon | effect |
|---|---|
| Six months | Small, unless someone deposits a fusion cistrome. The two array series and the 3SEQ deposit are all decade-old public data and will not improve. |
| Two years | Potentially decisive, and in one direction only: a genome-wide chromatin experiment with an NR4A3 chimera would convert every per-gene concordance here into either a driven-gene claim or a correlation, and nothing else would. |
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

Run an NBRE motif scan over the promoter regions of the class-A and Filion-Table-1 genes against a size- and GC-matched background drawn from the same genome build, and record per-gene motif hits beside the existing per-gene deltas in `nr4a3-fusion-targets.json`. $0, sequence-only, no dispatch and no new data.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-FUS-T1](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

**L5 evidence:** [EV-FILION-2009](L5-evidence-base.md#evidence--the-literature-this-program-cites), [EV-PMC6766969](L5-evidence-base.md#evidence--the-literature-this-program-cites), [EV-SUBRAMANIAN-2005](L5-evidence-base.md#evidence--the-literature-this-program-cites)

[← ST-DISSEMINATION](L1-st-dissemination.md) · [← L0](L0-ecosystem.md)
