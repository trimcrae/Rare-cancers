---
id: DOC-OPUS-CAMPAIGN-CORRECTED-A-V2-NON-WARRANT-DEMONSTRATION
title: "CORRECTED-A v2 — demonstration that the renamed dropped-category flag is neither an eligibility warrant nor a numerator warrant"
level: L4
kind: verification
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# The renamed flag cannot be mistaken for an eligibility warrant or a numerator warrant

The flag renamed in this component is

    RESPONSE_ASSESSMENT_CATEGORY_TITLE_DROPPED_BY_PRODUCER      (101 rows, unchanged from v1)

It replaces v1's `RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER`, whose name and whose schema
sentence ("a category that reports **responders** under its own criteria set") asserted more than
the evidence supports.

## What the flag is, stated exactly

The flag is a **predicate over a verbatim title string**. It is set on a row when the old (job-1)
extraction dropped at least one source category whose title matches a response-assessment
vocabulary — `sCR`, `VGPR`, `CRh`, `CRi`, `CRu`, `CRmrd`, `nCR`, `MR`, `Non-CR/Non-PD`, molecular
response, `MRD`. Nothing else enters the computation: no count, no denominator, no criteria
document, no adjudication.

## Why the v1 name was wrong

⚠ A verbatim category title such as `Non-CR/Non-PD` **does not establish that the participants
counted under it meet an objective response definition.** `Non-CR/Non-PD` is an IMWG
response-assessment state defined for patients without measurable disease; whether it belongs in
any objective-response numerator is a criteria question, and **no cross-criteria numerator has been
adjudicated anywhere in this campaign.** Calling those 101 rows "lost responders" imported a
conclusion from a token.

## The demonstration (machine-checked, `corrected-a-v2-checks.json`)

| id | what it demonstrates | result |
|---|---|---|
| D4 | the flag is **exactly** the title-derived predicate: flag present ⇔ the dropped-title column is non-empty, 0 mismatches on 552 rows | PASS |
| D5 | **not an eligibility warrant.** `proportion_suitability` is a function of the blocking codes alone on 552/552 rows; the flag appears in **no** `unresolved_reason_codes` cell and is **not** in the blocking enumeration; flagged rows land in **both** suitability states (97 `NOT_REFUTED_BY_THIS_COMPONENT`, 4 `UNSUITABLE_FOR_PROPORTION`), so carrying the flag neither grants nor withholds anything | PASS |
| D6 | **not a numerator warrant.** No numerator / responder / rate / percent column exists (`rate_derived` is the column that *declares* no rate was derived, and it reads `NOT_DERIVED` on 552/552). The **would-be numerator** — the per-row sum of the flagged categories' values, range 0..19 — was computed and compared against every emitted column: **it equals none of them.** The sum exists nowhere in the artifact | PASS |
| D1 | the v1 identifier survives only inside `superseded_identifiers`, explicitly labelled as superseded, and appears in no data table, no summary count and no live schema slot | PASS |

## What is deliberately NOT here

- ⛔ **No responder class is retained**, narrower or otherwise. `schema.warrants.responder_class_retained.retained = false`. Because no responder class is asserted, none needs a source-bound definition — and none is inferred from a title or a token.
- ⛔ **No category is folded** into `CR`, `PR` or anything else. 123 verbatim titles, `folded = NO` on all of them, unchanged from v1.
- ⛔ **No numerator, rate, proportion, percentage or unique-patient total** is constructed anywhere.
- ⛔ The cross-criteria question — whether counts reported under RECIST, IMWG, Lugano, ELN and IWG-style criteria may ever share a numerator definition — remains **open and undecided**, exactly as v1 left it.

## Reading rule for downstream consumers

The flag answers one question only: *did the old extraction silently drop a response-assessment
category from this row's record?* It is a **completeness warning about the old extraction**. It is
not a statement about the patients, not a permission to include the row in anything, and not a
count that may be added to a numerator.
