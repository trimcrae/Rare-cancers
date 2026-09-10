---
id: DOC-ATLAS-HOFVANDER-REPLICATION-AMENDMENT-20260906
title: Pre-outcome shared-histology replication extension
level: cross-cutting
kind: prereg
status: immutable
canonical_for: []
purpose: Freeze a source-supported same-histology replication axis before new target outcomes.
scope: Original GSE24369 biopsy arrays and overlap-reduced Hofvander tissue TPM.
audience: [autonomous research agents, external reviewers]
date: "2026-09-06"
last_verified: "2026-09-06"
related: [DOC-ATLAS-HOFVANDER-VALIDATION-20260906]
---

Coordinator authorized this source-driven extension before any new target values were opened. The original Hofvander question, estimands and allocation rule remain unchanged. Initial protocol/README bytes are preserved exactly in protocol.md.original.txt and README.md.original.txt; only schema-supported frontmatter was applied to the corresponding current Markdown files, with byte-identical scientific bodies verified in administrative-preservation.json. This administrative correction changes no selection or hypothesis.

## Original array source and scope

Primary GEO series https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE24369 and platform https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL6244. Exact original GSE24369 family SOFT gzip is20,240,336 bytes, SHA25698c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37. Original sample VALUE field is RMA log2 signal; source states RMA background correction, normalization and probe summarization in Expression Console. Read original SOFT sample-table values at full released precision after authorization, never the rounded legacy cache or samplewise-z summaries. Already published/previously used array evidence is retrospective; newly recovered Hofvander values remain held-out-to-us. Neither source was generated prospectively for this question.

All42 original array samples are frozen:6 EMC tumor biopsies (GSM600934–600939),17 LGFMS (GSM600940–600956),6 myxofibrosarcomas (GSM600957–600962),6 desmoids (GSM600928–600933),5 solitary fibrous tumors (GSM600963–600967),2 pooled skeletal-muscle RNAs (GSM600968–600969). Original labels correct a legacy-cache simplification of myxofibrosarcoma to fibrosarcoma and exclusion of solitary fibrous tumors. The normal pools are descriptive sample context only, not two individual healthy patients, a normal-organ atlas or evidence of organ safety. Their per-gene source values are retained separately without inferential comparisons.

All tumor specimens are described as tumor biopsy; primary versus recurrence/metastasis is not established in the available sample fields. Retain all biopsies symmetrically rather than fabricate a primary-lesion restriction. Do not claim lesion-matched cohorts. One biopsy accession is the available resampling/deletion unit; distinct patient identities and all cross-cohort overlap cannot be universally verified. The nine Hofvander EMC retain the original positive-overlap exclusions; probable independence remains qualified. This is cross-cohort rank-direction evidence, not proof of fully independent patient recruitment.

One exact uniquely assigned GPL6244 transcript cluster per gene is frozen from original annotation: CD2767984743,SSTR28009526,PRAME8074856,FAP8056257,CD2487949588,CSPG47990545,MSLN7992071,L1CAM8175871,GPC38175234,ALPP8049123,CDH178151795,CHRNA68150550. The machine-readable manifest keeps symbol and probe fields separate. Every assignment alternative maps to the same gene. No probe averaging/selection, alias expansion or abundance-driven filtering. Missing/duplicate sample-probe observations or nonfinite values produce a durable technical failure. Finite signed RMA log2 values are valid; no TPM-style nonnegative requirement applies to array log signal. Cohort-specific monotonic scaling leaves pair ranks unchanged; no cross-platform numerical expression comparison is made.

## Shared-histology comparison fixed before values

The PRIMARY replication anchor is LGFMS-specific probability of superiority A for each fixed gene, calculated separately from6 array EMC versus17 array LGFMS, and9 primary Hofvander EMC versus13 primary Hofvander LGFMS. Report Hofvander same-year A alongside its all9 marginal A under the original protocol, explicitly3 supported EMC for LGFMS. Do not compare the array LGFMS-only effect with the three-histology Hofvander composite.

SECONDARY contexts are myxofibrosarcoma, solitary fibrous tumor and desmoid, each separately named with its own A in each cohort. Hofvander original diagnoses/primary-lesion policy yield60 MFS,11 SFT,11 desmoids. The entire relevant Hofvander metadata is frozen in replication-manifest.json. No composite combines these histologies, no pooled array/TPM units and no missing-histology replacement. GSE4303 remains excluded from abundance replication because reference composition is not established; two-color ratios cannot silently become tissue abundance.

For each gene and shared histology, A=mean[I(EMC>comparator)+0.5I(tie)] at released precision. Report exact effect, patient/specimen counts, pair count, individual EMC placements, and leave-one-EMC-biopsy and leave-one-comparator-biopsy effects in each cohort. For Hofvander also report the original exact-year stratified estimate, unsupported/singleton strata and deletion reweighting. Patient deletion refers to available accession units and inherits the identity limitation above. No cross-cohort bootstrap pooling. This extension uses deletion ranges as descriptive sensitivity, not confidence intervals; the original Hofvander pointwise conditional bootstrap remains unchanged.

Compare signed deviation A−0.5 and effect size descriptively: both positive, both negative, opposed directions, or neutral/tied; show the sign of every deletion and whether direction changes. No new magnitude success cutoff, P value, multiplicity-selected subset or pass count is introduced. The original70% Hofvander allocation rule is neither weakened nor treated as a cross-cohort significance test. All11 address genes and separate CHRNA6 control are retained, including discordant, weak and negative evidence. A same-histology positive rank direction can strengthen a tissue-validation rationale; it cannot establish surface protein location, normal sparing or clinical efficacy.

## Execution and preservation

replication_metadata.py is metadata-only and pins raw original bytes and all42 sample/probe mappings. replication.py defaults to synthetic fixtures, accepts coordinator authorization only after matching all original four approved file hashes plus this amendment, replication-manifest.json, replication_metadata.py and replication.py. It checks all raw sources and metadata and the original completed result/source-value outputs before replication analysis. Initial Hofvander outputs remain separate under results/; replication outputs go to replication-results/. Target values must not be opened before the coordinator writes the new exact-hash authorization. Any future repair preserves these frozen bytes and appends a dated explanation.
