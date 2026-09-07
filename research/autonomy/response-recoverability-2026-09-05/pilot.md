---
id: DOC-RESPONSE-RECOVERABILITY-PILOT-20260905
title: Response recoverability pilot decision
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Decide whether source recoverability supports a distinct empirical methods prospect.
scope: Ten purposively selected trials; bounded development gate, not publication review.
audience: [maintainers, autonomous research agents]
---

**No-go for developing this prospect into a distinct empirical methods paper on the present evidence.** The pilot demonstrates defects in our corpus representation, but zero source-resolved reversals of an actual study decision and no distinct validated method. This does not establish that such errors never occur. It does not validate the existing 552-arm manuscript, repair its full corpus, or estimate reporting-error prevalence.

Selection was frozen in [selection.json](selection.json) before primary retrieval: ten distinct trials and 22 stored rows. Deterministic sequential strata cover the impossible enrollment total, repeated arm titles, smaller evaluable populations, a unit-risk title proxy, and four ordinary remaining records. All stored units say Participants. Original cache refs are absent and compact inputs lack original negative-screen identifiers; accrual-record IDs were not substituted. No sampling replacements were made.

All ten public registry records were retrieved. [evidence.json](evidence.json) supplies original/replayed counts, exact JSON pointers, population/time definitions, URLs, retrieval times and hashes. Replaying the existing `_cells_for_groups` function on the saved current records reproduces all 22 selected rows. This demonstrates current algorithm behavior, not historical cache byte identity. All selected last-update dates precede the original August 9 freeze, but the historical payloads remain unavailable.

| Trial | Source-grounded finding | Consequence and limit |
|---|---|---|
| [NCT00756509](https://clinicaltrials.gov/study/NCT00756509) | Enrollment 34 conflicts with both response denominator and participant flow 41; response categories sum to 41. | A source inconsistency, not percentage conversion. Do not force the denominator to 34. |
| [NCT00600340](https://clinicaltrials.gov/study/NCT00600340) | Eight rows are two arms across ITT/PP and confirmation analyses. Confirmed ITT includes 15/18 unevaluable patients omitted from four-cell sums. | Paclitaxel response is 125/285 for ITT versus 125/270 for the four-category subset. Both denominators have meanings; eight independent arms do not. |
| [NCT00858117](https://clinicaltrials.gov/study/NCT00858117) | Same 30 participants assessed physically and by CT: response 30/30 versus 21/30. | Legitimate assessment contrast, not two independent arms or an established erroneous study conclusion. |
| [NCT02440464](https://clinicaltrials.gov/study/NCT02440464) | Extractor overwrites baseline/time classes and omits sCR/VGPR, death and unevaluable categories. | Last-class ixazomib best response is 11/12, not the malformed four-cell 4/5. This corrects our representation, not the original trial's PFS conclusion. |
| [NCT00183820](https://clinicaltrials.gov/study/NCT00183820) | Outcome denominator 29 correctly excludes one stated inevaluable patient. Uploaded protocol conflicts on interim continuation rules. | Genuine document ambiguity, but missing stage-specific outcomes prevent adjudicating a stop/continue error. |

The other five records provide useful counterexamples: NCT00066222 explicitly restricts response to 68 eligible treated patients observed after treatment; NCT00298896's 47-person efficacy set matches its four cells; NCT00301067 explicitly pools dose cohorts into a 20-person response analysis; NCT00389805 gives phase-I response-evaluable groups of 15/12; NCT00601003's four cells match its 76-person outcome denominator. Enrollment gaps alone are not extraction errors. Population, assessment, phase and time labels remain necessary even when arithmetic agrees.

The GIST [amended protocol](https://cdn.clinicaltrials.gov/large-docs/09/NCT00756509/Prot_000.pdf), sections 10.4.2 and 10.6, defines CR+PR+SD as primary and gives a cutoff of 24 for planned n=39. Applying that cutoff to ORR would substitute a different endpoint; no source making that erroneous decision was found. Its response definition requires four-week CR/PR confirmation and SD after six weeks. The posted enrollment conflict remains unresolved.

The germ-cell [protocol](https://cdn.clinicaltrials.gov/large-docs/20/NCT00183820/Prot_SAP_000.pdf), printed pages 21–22, says continue after at least one response among ten in section 11.1 and at least three in section 11.2. Both pages were rendered and inspected. No rule was chosen by convenience. The document also ties further-study interpretation to an exact interval and 50%, but the stage-specific response sequence was not recovered.

For TURANDOT, the [primary publication abstract](https://pubmed.ncbi.nlm.nih.gov/27501767/) specifies overall-survival noninferiority against HR 1.33. Response corrections do not recompute that primary comparison. For myeloma, the [publication abstract](https://pubmed.ncbi.nlm.nih.gov/35840087/) identifies PFS as primary and inadequate efficacy assessment after early closure. No benefit is inferred from its post-transplant response categories. Elsewhere, scan intervals and outcome observation windows were not silently treated as minimum stable-disease duration or confirmation rules.

The focused novelty check also argues against promotion. [Perlmutter et al.](https://pubmed.ncbi.nlm.nih.gov/28011448/) already compared oncology protocols, registry outcomes and publications. [Grayling and Mander](https://pubmed.ncbi.nlm.nih.gov/34950839/) audited two-stage designs and reanalysed inference. [EXACT](https://pubmed.ncbi.nlm.nih.gov/30257185/) extracted registry numerical data and assessed reproduction of meta-analyses. A [numerical-result extraction benchmark](https://arxiv.org/abs/2405.01686v2) already tests complex outcomes across LLMs. These abstracts establish substantial overlap, not exhaustive absence of novelty. This pilot provides no new general method, independent annotated validation set, or comparator evaluation beyond our parser.

**One next question:** Can a specific independent trial supply a protocol/SAP, stage-resolved outcomes and a published decision that disagree because of response-definition or denominator handling, beyond our extractor and established reporting-audit methods? Reopen only with that concrete evidence lead; otherwise preserve these correction findings and deprioritize the paper prospect.

Worker: `01a07208-6465-7240-bbc9-c9b832c256da`, isolated worktree at base `0eb7bcb8bbce610f7ef0e7484ec49a8a9a19877c`; actual `gpt-6-astra` / `medium` independently confirmed by coordinator from turn context. Exact elapsed time and focused validation are recorded in evidence.json. No nested workers, paid services, installs, manuscript/registry edits, commits, publication, or continuing processes. Coordinator owns normal integration preflight and independent verification; worker checks are not full publication evidence.
