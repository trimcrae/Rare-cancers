---
id: DOC-USZ-JUNCTION-INPUT-AUDIT-20261002
title: USZ patient-model junction input check and missing-input handoff
kind: memo
status: live
date: 2026-10-02
last_verified: 2026-10-02
purpose: Record the bounded no-change endpoint for patient-model junction identity inputs.
scope: Existing USZ20-EMC1 and USZ22-EMC2 model record and its four cited cached sources.
audience: [maintainers, autonomous research agents]
---

The USZ patient-model junction question still lacks a qualifying new input. The existing model
evidence is unchanged, and all four cited cached source files match their original August 15
Git blobs. This entry check therefore stops without a compatibility computation or scientific
repair. It does not establish that no new information exists outside these committed inputs.

| Model | Reported assay exon labels | Nucleotide-resolved junction | Native assay NR4A3 transcript reference |
|---|---|---|---|
| USZ20-EMC1, RRID:CVCL_C6MX | EWSR1 exon 13 :: NR4A3 exon 2 | Unknown | Unknown |
| USZ22-EMC2, RRID:CVCL_C6MY | TAF15 exon 6 :: NR4A3 exon 2 | Unknown | Unknown |

These are the existing record's reported labels, not measured junction sequences. Both
Cellosaurus entries cite the same primary paper, PMID 36316541 / PMC9813045 /
DOI 10.1007/s13577-022-00818-x; registry reuse does not add independent corroboration.
Cached curated RefSeq NR4A3 models provide public annotation context. They are not the
FoundationOne HEME assay's native transcript reference and cannot resolve the patient junction.
A native transcript reference could clarify exon numbering while still leaving the nucleotide
boundary unknown. The acceptor ambiguity remains open.

[Input fingerprints](input-fingerprints.json) bind the current model record to the previously
known blob and each cited cached file to its original path commit. The two original retrieval
manifests provide historical URL/status metadata, not raw SHA256 receipts. This check compared
repository Git identities; it performed no new source retrieval or old scientific audit.
The prior supplementaryFiles response remains unanswered evidence. It was not retried, and an
empty historical response does not establish that a supplement or its junction information is absent.

The checked main base is 0a587508867813adf25cb711dd227ade08f5506f. The freshly read ledger
research/autonomy/research-ledger.json, blob 79983403fd38d9ec5be3533bcf91b3af36c2657b,
has 415 entries and no non-null owners at that point in time. Current guidance, handover,
main commits, open PRs and completed sprint refs were read before selection. This isolated branch
is not a legacy remote claim, scheduler cutover or shared-queue write.

Operational validation and independent source/method/prose review are pending at this checkpoint.
The branch workflow is limited to the exact model-record Git blob binding, normal default FAST
preflight and clean tracked status. No new scientific test suite, transcript reconstruction,
junction alignment, expression kernel, rescreen or oligo design is proposed.

The concrete next action is to obtain a qualifying authoritative exact RT-PCR/Sanger junction
read or the native FoundationOne HEME NR4A3 transcript reference through a separately authorized
changed input, or demonstrate a current provenance mismatch. Recheck owners and fingerprints
before one read-only new-input-to-pinned-transcript compatibility audit. Stop again if none is
available. Do not infer junction sequence from exon labels, repeat the old supplement attempt,
contact model owners or rewrite the protected manuscript. This cycle starts no second task.

Frozen/deposited ASO files, prior scientific outputs, preregistrations, seven exclusions,
unresolved CHRNA6 specimen overlap/independence, review seats, queues/fleet owners and no-GPU/
publication enforcers are unchanged. No GPU/model API/paid compute, outreach, PR, main merge or
publication occurred. The result establishes no activity, hazard, efficacy, safety or clinical claim.

AI authorship: Codex AI assistant. Independent LLM review is distinct from human scientific
validation. No attached shell or local cloud runtime was available; operational checks run on
GitHub Actions. Model/effort IDs and subscription usage are not exposed.
