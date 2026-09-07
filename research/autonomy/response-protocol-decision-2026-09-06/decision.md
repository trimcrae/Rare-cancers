---
id: DOC-RESPONSE-PROTOCOL-DECISION-20260906
title: NCT00601003 protocol recovered but efficacy decisions remain unrecoverable
kind: memo
status: live
purpose: Resolve the named protocol-access dependency and assess whether saved aggregate results identify its actual efficacy decisions.
scope: One saved neuroblastoma and medulloblastoma trial record and its official protocol; no EMC treatment inference.
audience: [maintainers, external reviewers]
date: 2026-09-06
last_verified: 2026-09-06
---

The named protocol was accessible. The official ClinicalTrials.gov CDN returned the full
7,970,202-byte, 55-page version 9 document dated December 4, 2015. It contains the statistical
plan in section 6 (pages 17-19). Original bytes, HTTP metadata, machine extraction, relevant
page renders, and a frozen source-rule record are preserved here. The former pilot's
unretrieved-document state is repaired; it was not an insurmountable access barrier.

The source changes the interpretation of the denominator concern: analysis is explicitly
within three separate evaluable-patient strata, with accrual allowance for unevaluable
patients. It does not require all 112 enrolled patients as the response denominator.
Consequently, replacing 76 with 112 and declaring an efficacy reversal would be unsupported.

The saved results still cannot reproduce the protocol decisions. Section 6 requires
different stratum-specific rules and interim histories. The registry provides one pooled
group with 7 CR, 11 PR, 35 SD and 23 PD, totaling its stated outcome denominator of 76.
It provides no response population description, stratum-specific evaluable counts or
response counts, interim accrual-order outcomes, or statistical analyses. The outcome
object is at `/study/resultsSection/outcomeMeasuresModule/outcomeMeasures/1` in
`NCT00601003.saved.json`; full original saved bytes are retained.

| Required decision input | Source locator | Saved result |
|---|---|---|
| Three separate stratum analyses | Section 6.2, page 19 | One pooled OG000 response group |
| I: first 19 evaluable, continue only above 6 responses; final 39, reject above 16 | Sections 6.1, pages 17-18 | No stratum I counts or first-stage history |
| II: first 18 evaluable, continue only above 4 responses; final 33, reject above 10 | Section 6.1, page 18 | No stratum II counts or first-stage history |
| III: 21 evaluable and one-sided exact binomial test of p=0.05 at alpha=0.05 | Sections 6.1-6.2, pages 18-19 | No stratum III count or denominator |
| Best response during six cycles; central integrated response | Sections 6.1 and 13, pages 17, 29-33 | Integrated imaging/bone-marrow description exists, but time frame is two years and individual assessment timing is absent |

The saved outcome's radiological title is not evidence that it omits marrow or MIBG:
its description expressly includes CT/MRI, MIBG and bone marrow and specified PR conditions.
The source-only warning in the frozen extraction was conditional; inspecting the saved
description resolved that particular concern. We have not demonstrated endpoint miscoding.
The two-year versus six-cycle reporting windows cannot be reconciled from the aggregate
record alone, and their difference is not proof that investigators used a wrong window.

Participant flow reports 112 started, 76 completed and 36 not completed. Equality between
the completion count and outcome denominator is not an individual-level linkage. The
record does not establish that all completers, and only completers, were response evaluable.
The 110-person adverse-event denominator is another outcome-specific population, not a
replacement efficacy denominator. No failures were imputed and no pooled hypothesis test
or investigator decision was computed.

## Arithmetic and verification

`check_decision.py` verifies the original PDF and saved-record hashes, preserved rule-freeze
hash and chronology, extracts the actual response object, and checks count reconciliation.
It checks all 420 possible first-/second-stage count pairs for I and 304 for II, including
the boundary cases and the rule that a failed interim stage cannot become a final rejection.
Exact rational binomial arithmetic gives I type-I error 0.045499 and power 0.803623, and
II type-I error 0.045830 and power 0.801142, consistent with the source's rounded design
quantities. These are design properties, not measured treatment outcomes.

For III, the source-defined exact test implies rejection at 4 or more responses among
21 evaluable patients: null tail probabilities are 0.084918 at 3 and 0.018881 at 4.
This integer cutoff is calculated from the specified test, not an explicit quotation
from the protocol. There is no observed stratum III count to which it can be applied.

Original pages 15, 17-19 and 29-33 were rendered with Poppler and visually inspected.
This matters because PDF extraction inserts spaces inside words. Two source ambiguities
are retained in the frozen rule record: refractory-neuroblastoma stratum wording differs
between sections 4.2 and 6.1, and the overall-response section says both strata while
section 6 calls for three. No patient allocation was inferred from either ambiguity.

## Allocation result

Stop this route at the source checkpoint. It establishes a precise reporting dependency,
not a reconstructed efficacy decision or an EMC research contribution. To reproduce the
actual decisions would require each stratum's evaluability, response counts, stage ordering,
and timing under the applicable protocol version, or equivalent reported stratum analyses.
The saved record and this named protocol do not supply them. The protocol amendment was
written after accrual had begun; this source alone does not establish which enrolled
patients were governed by which earlier versions or whether the amended interim rule was
implemented. No decision reversal or investigator misconduct is demonstrated.

The check does not justify a manuscript, a broader inventory, or immediate trial-label
spending. It closes this specific unfinished source attempt with recoverable methods and
an unrecoverable actual decision. No other source retrieval or background process remains
running. Coordinator independent verification and integration are pending; no commit,
preflight, publication, outreach, or paid access was performed by this worker.
