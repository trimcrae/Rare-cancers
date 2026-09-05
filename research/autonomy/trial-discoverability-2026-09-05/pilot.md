---
id: DOC-TRIAL-DISCOVERABILITY-PILOT-20260905
title: Fusion-defined sarcoma trial discoverability bounded pilot
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Decide whether the obtainable retrieval evidence supports a scientifically distinct paper.
scope: Three frozen diagnoses, one public registry snapshot, provisional diagnosis-level screening.
audience: [maintainers, autonomous research agents]
---

**Decision: no-go for developing this pilot into a distinct paper now.** A real diagnosis-name retrieval gap survives stronger ordinary search, but the clearest molecular-compatible examples are already recovered by parent-sarcoma search. The evidence does not yet establish a useful molecular-versus-hierarchy advantage or a validated diagnosis-level benchmark. This is a contribution decision, not a claim that the question is unanswerable or that molecular retrieval has no value.

The useful retained result is an auditable correction to the previous discovery claim, with reproducible search comparisons and hard negatives. It is not a trial-matching service, a clinical eligibility determination, or evidence of efficacy, safety, or patient benefit. No manuscript, preregistration, registry, queue, or publication state was changed.

The frozen selection and bounded source frame

[selection.json](selection.json) froze EMC, desmoplastic small round cell tumor (DSRCT), and synovial sarcoma (SS), their ordinary names and molecular terms at 16:29:46 UTC, before the first successful trial query at 16:30:32 UTC. The supplied historical EMC examples were known beforehand; this was purposive selection, not blinded sampling. EMC and DSRCT share an EWSR1-family retrieval route; SS supplies a different fusion family. Primary molecular provenance is [Agaram et al.](https://pubmed.ncbi.nlm.nih.gov/24746215/), [Ladanyi and Gerald](https://pubmed.ncbi.nlm.nih.gov/8187063/), and [Clark et al.](https://doi.org/10.1038/ng0894-502); archived records and a modern SS18::SSX primary-study search supplement the historical terminology. Spelling, plural, and acronym variants were explicit search choices, not a complete ontology. FET terms are intentionally broad candidate generators and do not imply every EMC has a FET fusion.

ClinicalTrials.gov API v2 reported version 2.0.5 and data timestamp 2026-09-04T09:00:06. All statuses and study types were retained. Every query followed page tokens to exhaustion, with unique-ID counts checked against reported totals. Raw payload bytes are retained losslessly in gzip, with original-byte SHA256, storage SHA256, URLs, timestamps and page tokens in each query manifest. See [sources](sources/) and [corpus-index.json](corpus-index.json).

There are **6,182 unique records** in the bounded union. Parent `sarcoma` BasicSearch returns 3,573 records in 36 pages; explicit eligibility search returns 4,061 in 41 pages; their union is 5,849. Additional comparator and historical-anchor records form the rest. This is a complete enumeration of these specified query results, **not an independent denominator of compatible trials**. Generic solid-tumor trials absent from every frozen query can be missed. No global recall, sensitivity, prevalence, or patient-level precision is estimated.

Search semantics materially change the interpretation

The primary [API search-area metadata](https://clinicaltrials.gov/api/v2/studies/search-areas) shows that ConditionSearch includes titles, keywords and MeSH terms as well as sponsor conditions. BasicSearch (`query.term`) does not list EligibilityCriteria; EligibilitySearch does. Therefore neither condition-field omission nor a failed BasicSearch alone establishes unfindability.

The [semantics amendment](search-semantics-amendment.json) added explicit eligibility searches symmetrically for the same frozen ordinary and molecular terms. A subsequent [sensitivity amendment](sensitivity-amendment.json) removed phrase quotes from the ordinary terms without changing the terms. Both original and amended results remain. Exact amendment timestamps and hashes are in [freeze-provenance.json](freeze-provenance.json). The first API request rejected an unsupported NCTId sort before returning trial data; the repaired requests use service ordering and checked pagination.

| Diagnosis | API condition | Ordinary BasicSearch | Ordinary eligibility | Ordinary union | Strong ordinary union including unquoted sensitivity | Molecular BasicSearch + eligibility | Molecular-only versus strong ordinary |
|---|---:|---:|---:|---:|---:|---:|---:|
| EMC | 28 | 316 | 55 | 359 | 374 | 41 | 38 |
| DSRCT | 63 | 77 | 82 | 118 | 132 | 65 | 55 |
| SS | 152 | 175 | 195 | 266 | 270 | 8 | 2 |

These are **retrieval counts, not compatible-trial counts**. Ambiguous EMC and gene abbreviations intentionally make the baseline/generator broad. Literal normalized phrase membership in sponsor conditions is separately computed in the bounded corpus (11 EMC, 38 DSRCT, 91 SS) and is not equated with API condition search. [corrected-comparison.json](corrected-comparison.json) and [sensitivity-results.json](sensitivity-results.json) retain all IDs and intersections. Of the final molecular-only records, 15 EMC, 16 DSRCT and 2 SS records have a posted status of RECRUITING, NOT_YET_RECRUITING or ENROLLING_BY_INVITATION; these are still mostly nonmatches or uncertain candidates. ACTIVE_NOT_RECRUITING is kept outside that current-search group.

What the criteria support

The worker screened diagnosis-bearing criteria excerpts for 74 records: the initial corrected molecular-only union plus the prespecified anchors. Selected positive and hard-negative records were additionally read in full. [evidence.json](evidence.json) gives a provisional disposition and rationale for every screened record; [review-packet.json](review-packet.json) supplies full criteria and exact page/JSON pointers. These are single-worker screening judgments awaiting coordinator verification, not a fully adjudicated gold standard.

| Record | Source-grounded finding | Consequence for the proposed paper |
|---|---|---|
| [LIFFT NCT05918640](https://clinicaltrials.gov/study/NCT05918640) | Phase1 requires a documented FET fusion in a recurrent/relapsed solid tumor. This supports an EWSR1/TAF15-fused EMC candidate; Phase2 is EWS-FLI1 Ewing-specific. | EMC remains absent from both strong ordinary searches but molecular and parent-sarcoma searches retrieve it. Diagnosis compatibility does not establish an open Phase1 slot. DSRCT is ordinary-findable and has a separate safety-gated exclusion. |
| [Elimusertib NCT05071209](https://clinicaltrials.gov/study/NCT05071209) | PartA/B1 permits EWS-fusion solid tumors and explicitly names EWS-WT1. | DSRCT molecular-versus-name gap survives sensitivity, but the record is ACTIVE_NOT_RECRUITING and parent-sarcoma-findable. This is a second diagnosis example, not a current enrollment opportunity. |
| [NCT06571734](https://clinicaltrials.gov/study/NCT06571734) | Cohort3 uses translocation-associated soft tissue sarcoma without enumerating the full class. | EMC/DSRCT class-level compatibility remains protocol-dependent. Parent search finds it; the frozen gene queries do not. Calling it a molecular-query success would be false. |
| [NCT04901702](https://clinicaltrials.gov/study/NCT04901702), [NCT06709495](https://clinicaltrials.gov/study/NCT06709495) | Broad Phase1 solid-tumor/sarcoma criteria coexist with molecular language in other cohorts. | Plausible EMC/DSRCT broad candidates are not fusion-defined admissions; parent search retrieves them. Stage and cohort restrictions must be preserved. |
| [NCT05135975](https://clinicaltrials.gov/study/NCT05135975) | Names desmoplastic small round **blue** cell tumor. | An apparent DSRCT molecular gain disappears with the unquoted ordinary sensitivity search. An incomplete synonym list is not a novel molecular-discovery mechanism. |
| [NCT05687136](https://clinicaltrials.gov/study/NCT05687136) | Lists SS18 among SWI/SNF mutations and requires PI approval of alterations. | The only oncology SS molecular-only result is unresolved: the record does not explicitly equate SS18::SSX with its mutation criterion. The other SS hit is Baker Gordon syndrome. Neither is a verified SS positive. |
| [NCT07092306](https://clinicaltrials.gov/study/NCT07092306), [NCT07620431](https://clinicaltrials.gov/study/NCT07620431) | Ewing-specific criteria exclude clear FET-non-ETS fusions; the first explicitly names EWSR1-WT1 among excluded examples. | Strong hard negatives for treating any FET/EWSR1 mention as compatible. |
| [PerVision NCT06094101](https://clinicaltrials.gov/study/NCT06094101), [NCT06239272](https://clinicaltrials.gov/study/NCT06239272) | PerVision restricts to rhabdomyosarcoma/Ewing/SS; NRSTS2021 names DSRCT in exclusions while EMC is listed in conditions. | A fusion-framed title is insufficient; ordinary eligibility retrieval can retrieve a named exclusion. |

Other retained examples include WT1 hematologic studies, imaging/spinal fusion, FUS-associated ALS, and observational/prescreening cohorts. Ewing-like class language and additional biomarker requirements remain uncertain rather than being forced into positive or negative labels. CARMA is a historical anchor outside the frozen parent/molecular retrieval frame, underscoring that the query union is not an exhaustive diagnosis-compatible denominator.

Distinct contribution and stop decision

[TrialGPT](https://doi.org/10.1038/s41467-024-53081-z) already evaluates retrieval, criterion reasoning and ranking. [MatchMiner](https://doi.org/10.1038/s41698-022-00312-5) already encodes genomic/clinical Boolean criteria and arm-level matching. [RareCure](https://doi.org/10.7759/cureus.109744) directly overlaps rare-sarcoma hierarchy expansion, but explicitly does **not** quantify its marginal retrieval contribution with module-level ablation. The September2026 [TrialGPT2.0 preprint](https://arxiv.org/abs/2609.01202) is additional, non-peer-reviewed context; its performance claims are not adopted. Exact primary pointers and assessment limits are in [prior-art.json](prior-art.json).

A benchmark comparing molecular, ordinary synonym and hierarchy retrieval could therefore still be distinct. This pilot does not supply the independent labels, whole-frame ascertainment, solid-tumor hierarchy comparator, or effort/false-positive evaluation needed to justify that paper. Its strongest molecular examples show no incremental set coverage over even the narrower parent-sarcoma control; this does not rule out a useful ranking or review-burden advantage, which was not measured. Repeating the original two-case omission story would not fill RareCure's evaluation gap.

**Reopen only with** a prespecified independently adjudicated diagnosis/cohort reference set spanning the broader solid-tumor frame, at least one demonstrable molecular-versus-hierarchy coverage or review-effort advantage, and validation that distinguishes fusion identity, target expression, explicit exclusion and cohort stage. Resolve SS18 mutation-versus-fusion and currently open cohort uncertainty through public protocol evidence where possible. Do not launch more queries merely to enlarge the union or turn unresolved labels into positives.

Reproduce with Python standard library: `retrieve.py --analyze` verifies saved query counts/hashes offline; `analyze.py` regenerates comparisons and source pointers; `curate.py` emits the explicitly recorded worker judgments; `verify.py` checks provenance and evidence references. Network refresh uses `retrieve.py` and `archive_sources.py`; completed registry queries are reused, so a new snapshot requires a separately named output copy. `compress_sources.py` is lossless storage compression, not text cleaning. No HTML stripping was applied to trial criteria. Validation passed for all 24 queries and 112 pages, frozen-selection provenance, set arithmetic, compressed and original hashes, and all 74 record pointers. The memo frontmatter also parsed with the required kind and audience. The normal repository preflight did not run because `bash` is unavailable in this Windows environment; this is not a green repository gate. See [validation.json](validation.json) and [run-record.json](run-record.json) for actual checks, elapsed time, limitations and process status. No commit or publication was made.
