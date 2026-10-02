---
id: DOC-ASO-TISSUE-JOIN-AUDIT-20261002
title: Named ASO tissue-source join audit and no-change handoff
kind: memo
status: live
date: 2026-10-02
last_verified: 2026-10-02
purpose: Preserve a bounded existing-evidence audit and its explicit no-change endpoint.
scope: Two named gapmers' cached record, native-locus and tissue-source bindings.
audience: [maintainers, autonomous research agents]
---

The two named ASO sequences retain their existing record-to-locus and tissue-source bindings.
No current join or stored-list discrepancy was found. All six relevant source, output, instrument
and test blobs match the previously full-verified revision
3dc59c67654a4dfc5a6d0b842f12a732e6aeda89. The condition for a new verifier or scientific repair
was therefore not met, and this audit stops without changing the science.

| Sequence, 5′ to 3′ | Native junction | Legacy BLAST RID | Stored / reported near matches | Admitted record occurrences | Native loci |
|---|---|---|---:|---:|---:|
| GGGCATATCATCAAAC | EWSR1_e12__NR4A3_e3 | 7W03YWBN016 | 189 / 189 | 123 | 6 |
| GGGCATATCTTGTGTG | TAF15_e6__NR4A3_e3 | 7W0F8E93016 | 62 / 62 | 8 | 5 |

The audit reads the stored legacy `true_cleavage_risk` class. That label is a screening heuristic,
not measured RNase-H activity. All 131 admitted record occurrences carry plus-strand orientation
and zero stored gap mismatches. Their native deflines retain 11 distinct locus labels. The
matching stored/reported counts establish that these stored lists are not truncated relative
to their reported counts; this audit does not certify global BLAST database search sensitivity.

A separate read-only V8 projection checked native defline labels, exact sequence associations
in the existing cache/output, all 11 cached NCBI identities and 21 existing GTEx model/tissue
values. Every binding agreed. The 21 values are seven existing gene models at Liver, Kidney -
Cortex and Kidney - Medulla, using the cache's original column indices 35, 33 and 34. These are
direct source-to-existing-output comparisons; no expression estimation, statistics, alignment
rescoring or gap heuristic was rerun.

CA5BP1-CA5B remains separate from CA5B. The readthrough and LOC105370997, LOC105374140 and
LOC124907518 have no model in the retrieved GTEx cache and remain unreadable, with their original
reasons retained. Missing cached models are not zero expression, biological absence or safety.
The cached GTEx values describe genes in normal tissues; they do not establish a reagent's
cleavage, hazard, efficacy, therapeutic window or clinical readiness. The wider tissue artifact
covers additional registers and seams, so its aggregate record counts are not replaced by the
two-sequence counts above.

[audit-evidence.json](audit-evidence.json) pins all six exact historical/current Git blobs,
the original full receipt, both sequence/RID identities, every admitted hit index, native-locus
cache/output pointers, the 21 direct tissue bindings and unreadable states. Existing 25 test
functions were inspected, including stored-list truncation refusal and artifact reproduction.
They were not executed anew. The original
[full run 33933547339](https://github.com/trimcrae/Rare-cancers/actions/runs/33933547339) is reused
as historical validation at its exact unchanged source; this is not a new full-suite result.
Its receipt is preserved at
`research/release-candidates/PUB-ASO/2026-09-04/submission/repository-verification/full-preflight-receipt.json`,
Git blob c783a56fc1ae4e9b59df1fa5f37910f1d41971a2.

[Run 36961724473](https://github.com/trimcrae/Rare-cancers/actions/runs/36961724473),
job 110696664568, completed successfully at faf2ee8f9f196b04352bb9f5d0c61353186d8b5e.
Six operational Git blob bindings passed on CPython 3.11.16; normal preflight exited 0 with
PREFLIGHT OK (fast gates only (doc + artifact linters)); tracked status and diff stayed clean.
FAST took 164 seconds and the job took 217 seconds. No scientific suite was executed anew.
The original transcript and [validation-receipt.json](validation-receipt.json) bind exact
execution and review. Root independently checked the six current/historical source identities,
all 131 admitted indices and 11 native locus joins, the 21 cached tissue bindings and unreadable
states, then reviewed the question, method, finding, limitations and next step in this memo.
The evidence JSON retains its generation-time pending fields unchanged; completed review and
operational CI are recorded in the final receipt. No worker or job remains pending.
Only this operational footer, receipt and original log changed after the tested checkpoint.

Fresh base main is c784796fc7b510cb2de3c611b05d3cc035dec9e8. Ledger
79983403fd38d9ec5be3533bcf91b3af36c2657b was freshly read: 415 entries, no non-null owners.
The legacy driver remains disabled; existing sprint branches and unrelated open PRs were checked.
This isolated branch is not a legacy remote claim or scheduler cutover. Scientific generators,
existing results, frozen/deposited ASO files, preregistrations, seven exclusions, unresolved
specimen overlap/independence, review seats, queues/fleet owners and no-GPU/publication enforcers
are unchanged. No source acquisition, mutation dispatch, kernel, rescreen, broad paper review,
GPU/model API/paid compute, outreach, PR, main merge or publication occurred.

This is one completed scientific-selection audit with an explicit no-change outcome. It starts
no second audit. Reopen this join question only for a changed pinned input or an independently
demonstrated current join/completeness defect.

The next prioritized bounded task is the ASO patient-model junction identity gap for USZ20-EMC1
and USZ22-EMC2. Current emc-model-junction-evidence.json, Git blob
7d672031cc98ea1529303515001b803f360ff012, records no nucleotide-resolved junction or transcript
accession. First recheck ownership, completed outputs and authoritative cached-source fingerprints.
Proceed only if a changed source supplies an exact RT-PCR/Sanger junction sequence or the
FoundationOne HEME native NR4A3 transcript reference, or if a current source-to-model provenance
mismatch is independently demonstrated. Bind that new evidence to the pinned transcript/exon
model in one read-only compatibility audit. A transcript reference can clarify numbering without
establishing a nucleotide boundary; retain that distinction and any unresolved acceptor ambiguity.
Stop with an explicit missing-input/no-change result if no such input or defect exists. Do not
retry old failed supplements, infer junction sequence from exon labels, design new oligos, contact
model owners or edit protected manuscripts. This next task is recorded only; it has not started.

AI authorship: Codex AI assistant. Independent LLM review is distinct from human scientific
validation. No attached shell or managed runtime was available; model/effort IDs and subscription
usage are not exposed.
