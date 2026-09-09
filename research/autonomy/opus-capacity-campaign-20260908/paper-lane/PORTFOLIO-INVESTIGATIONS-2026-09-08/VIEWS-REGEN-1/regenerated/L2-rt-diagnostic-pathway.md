---
id: DOC-VIEW-RT-DIAGNOSTIC-PATHWAY
title: RT-DIAGNOSTIC-PATHWAY — The diagnosis itself — code contamination and a name that misleads
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does EMC's classification — the ICD-O code it shares and the tumour class its name implies — change what patients are counted and what they are given?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-DIAGNOSTIC-PATHWAY — The diagnosis itself — code contamination and a name that misleads

**Family:** [ST-CARE-DELIVERY](L1-st-care-delivery.md) · **state:** ✓ closed · computed · confidence moderate · verified 2026-08-23

**Grade** (owned by [`systems/graph/routes.json`](../graph/routes.json)): ⭐ ANSWERED AT $0, AND THE CODE IS READ THREE WAYS RATHER THAN TWO. ICD-O-3 morphology 9231/3 is queried as extraskeletal myxoid chondrosarcoma by one SEER study (PMID 32856598), enumerated as a histological subtype of chondrosarcoma of BONE by another (PMID 31765367 — whose Methods state its myxoid bucket 'includes extraskeletal myxoid chondrosarcoma', so the merge is acknowledged, and whose 87/743 myxoid cases sit under a location variable with no soft-tissue category at all), and listed as an intracranial MESENCHYMAL/MENINGEAL tumour by a third registry's own grouping document (CBTRUS, PMC9290890). None misuses the code: a morphology code carries no topography. ⭐⭐ AND THE PHENOMENON IS MEASURED IN SEER PRACTICE, not merely permitted — a pan-soft-tissue SEER study (PMC9303001) had to exclude 1,668 bone-primary records from 115,800 retrieved on morphology (1.44%), and its Supplementary Table 1 prints 459 NON-BONE 9231 records for SEER 18, 2000-2018. SEER's own site/histology validation list lists 9231/3 under three BONE site groups and not under CONNECTIVE & SOFT TISSUE — and that placement is NOT a recent revision: all sixteen published errata sheets covering every update to the list from 2001 to 2019 were read and none touches 9231/3. ⭐⭐⭐ AND THE SIZE IS NOW MEASURED, from ONE cohort that supplies both halves (PMID 31283732, SEER 18, 1988-2015): 404 extraskeletal 9231 excluded by name, 191 skeletal 9231 retained in its Table 1, so 191/595 = AT LEAST 32.1% OF A MORPHOLOGY-ONLY 9231/3 PULL HAS A BONE PRIMARY — about 37.5% adjusting the one bias whose direction is known, and both identified biases push it DOWN. The pre-registered negative did NOT fire: a small fraction would have retired this repository's caveat on SEER-derived EMC figures, and the fraction is not small. ⛔ AND THE NAMING HALF IS WEAKER THAN THIS ROUTE ASSUMED — PMC7771031 already published it ('this tumor name has likely influenced local management patterns'), and the guideline check came back NEGATIVE at primary source — NCCN's Soft Tissue Sarcoma guideline lists extraskeletal myxoid chondrosarcoma among its histologies while its Bone Cancer guideline does not. ⭐⭐ SEPARATELY, PMID 31283732 is the one published SEER study that split chondrosarcoma by ICD-O TOPOGRAPHY, and it excluded '404 patients with extraskeletal myxoid chondrosarcoma because it is a misnomer to call it a real chondrosarcoma' while KEEPING 9231/3 on its included-morphology list — and its own Discussion concedes it could not rule out further EMC hiding among its 426 retained extraskeletal cases.

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

This repository already noticed the edge of this and filed it as a one-line rejection — the IDH/ivosidenib row closed as a 'nominal name-match only ... worth one paragraph precisely because the name misleads clinicians into conventional-chondrosarcoma reasoning'. That observation is an instance of a general problem, not a curiosity: EMC is not cartilaginous, it shares a morphology code with a bone tumour, and both facts have consequences that reach a patient.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CARE-DELIVERY-EVIDENCE` | both sides of the ICD-O contradiction quoted from their own Methods sections, and the indeterminate-diagnosis margin penalty | `direct` |
| `ART-ICDO-CONTAMINATION` | the third reading of the code, the measured base rate of bone primaries in morphology-selected SEER sarcoma cohorts, the 459 non-bone 9231 count that specifies the closing query, the guideline-placement negative, and the prior art for the naming claim | `direct` |

## Remaining unknowns

- ✅ ANSWERED 2026-08-23: at least 32.1% of a morphology-only 9231/3 pull has a bone primary (191 skeletal / 595 total, PMID 31283732, SEER 18, 1988-2015), about 37.5% adjusted. Reported as a FLOOR because both identified biases push down. ⚠ One step is INFERRED rather than printed — that the 191 retained myxoid cases are all skeletal — because the source gives no site-by-histology cross-tab. ⛔ And it is an UPPER bound on non-EMC contamination, not the contamination: primary EMC of bone exists. What would still improve it: that cross-tab, the same query without the lymph-node-status requirement, and Table 1 of PMID 32856598 as independent replication.
- CLOSED, WITH A COUNT: whether the indeterminate-diagnosis margin penalty holds in EMC specifically. It cannot be answered from PMID 39899751 — its Table 2 gives the final diagnoses of all 66 indeterminate patients and FOUR are EMC, against a margin contrast computed over 27 and 74 patients. Unanswerable from that source, in either direction.
- ANSWERED AT PRIMARY SOURCE, AND IT IS A NEGATIVE: whether treatment guidance imports conventional-chondrosarcoma reasoning for EMC. NCCN's own published topic indexes settle it — its Soft Tissue Sarcoma guideline (v5.2026) lists 'Extraskeletal myxoid chondrosarcoma' among its covered histologies, and its Bone Cancer guideline (v1.2027) covers only Bone Cancer, Chondrosarcoma, Chordoma, Ewing Sarcoma, Giant Cell Tumor of Bone and Osteosarcoma, listing EMC nowhere. Two independent EMC reviews agree and add ESMO. ⚠ The NCCN reading is of the topic INDEX, not the guideline text (PDFs are behind a login); the ESMO half is secondary, because those guidelines are not open access and returned a shim page or HTTP 403 to every route tried including a real browser. ⚠ And one clinical series asserts the opposite about PRACTICE rather than guidance (PMC7771031), unmeasured.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Replicate the 32.1% over a different window and remove the inferred step: a SEER query cross-tabulating morphology 9231 against topography, with no lymph-node-status requirement. ⚠ NO LONGER THE ROUTE TO A FIRST ANSWER — the first answer is measured. Needs SEER Research base tier (institutional email + form + DUA) and SEER*Stat, which requires Microsoft Windows. | ⛔ none built | **no** | BLK-REGISTRY-DUA |
| Read Table 1 of PMID 32856598 as an INDEPENDENT REPLICATION over 1973-2016. ⚠ A subscription PDF, not a data-use-agreement problem. | ⛔ none built | **no** | — |
| Upgrade both quoted Methods passages from the abstract to the full text | ⛔ none built | yes | — |

## Readiness — what this could become today

**`internal_note`**

⛔ NOT A CAPABILITY LIMIT. The finding is measured and citable; what it lacks is a consequence, because three of the four checkable registry cohorts already apply the topography restriction this route would have recommended. Closed by trimcrae 2026-08-23.

**Missing:**
- nothing — the route is CLOSED. The measurement landed and the endpoint was closed as not-a-paper.

## Where this route ends — the paper

**[PUB-EMC-CLASSIFICATION](L3-publications.md)** — [One code, three diseases: what a registry cohort selected on ICD-O-3 morphology 9231/3 actually contains](../../research/manuscripts/care-delivery/emc-icdo-9231-classification.md)

`contributing` · ◐ `drafted` · aimed at `internal_note`

**This route contributes:** The whole argument: one code read as two diseases, and a measured cost of diagnostic uncertainty.

**The paper would claim:** ICD-O-3 morphology code 9231/3 is read by published work as THREE mutually incompatible populations — extraskeletal myxoid chondrosarcoma of soft tissue, a histological subtype of chondrosarcoma of bone, and an intracranial mesenchymal/meningeal tumour — because a morphology code carries no topography; SEER's own validation list has taken the skeletal reading unchanged since 2001; and the resulting contamination is MEASURED here for the first time. Of 595 records carrying 9231/3 in SEER 18 for 1988-2015, 404 had a soft-tissue and 191 a bone primary, so at least 32.1% of a morphology-only 9231/3 pull is bone — about 37.5% adjusted, with both identified biases pushing down. A cohort assembled by querying 9231/3 without a topography restriction, the standard construction in this literature, is not a soft-tissue cohort.

**It is not written because:** ⛔ IT WILL NOT BE. Closed 2026-08-23 on trimcrae's instruction: 'this is not a paper. Document what we have, merge to main, and drop it.' The draft survives as a findings NOTE at `document` — same content, no author block, no deposit declarations, no venue, and removed from the prose-style gate's submission-text list. ⚠ WHAT WOULD REOPEN IT, stated so the number alone does not: evidence that the largest and most-cited EMC registry series (PMID 32856598) did NOT restrict on topography. That is the only finding that would give the measurement a consequence, and it needs that paper's Methods section, which is behind a subscription. Nothing else found here supplies one. ⚠ AND AN OVERCLAIM WAS CORRECTED ON THE WAY OUT: the draft asserted that querying without a topography restriction is 'the standard construction in this literature'. That was not supported by the corpus this work assembled, and trimcrae caught it. The note now says the opposite, which is what closed the route.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

Every input is either committed or free to curate, and the work is $0.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-CARE-DELIVERY](L1-st-care-delivery.md), which is where these are asserted — a family limitation binds every route inside it.*

- Nothing in this family produces a new agent, so its ceiling is bounded by what the existing arsenal can do — and its floor is that the arsenal is already being used, so the gain is variance-reduction rather than a new option.
- Every route here ends in an observational or modelled argument. No randomised trial will ever settle a surgical-margin or surveillance-interval question in a disease this rare, so the limits of the design must travel with every claim.
- Reconstructed and registry data are re-expressions of published records, never new patients — they inherit every selection and publication bias of the series they came from and can correct none of it.
- Treatment associations in observational sarcoma data are dominated by confounding by indication, which runs in the direction that makes therapy look harmful; a route here that reports an unadjusted hazard has produced an artefact, not a result.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Closure

`premise_false` — 

## Best next action

⛔ NOTHING. CLOSED 2026-08-23 — 'this is not a paper. Document what we have, merge to main, and drop it.' The record is research/modalities/emc-icdo-contamination.json and the findings note beside it. ⚠ Do not reopen on the strength of the 32.1% alone: the number was never the problem. Reopen only on evidence that PMID 32856598 did not restrict on topography, which needs a subscription copy of its Methods.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-CARE-DELIVERY-EVIDENCE](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against), [ART-ICDO-CONTAMINATION](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-CARE-DELIVERY](L1-st-care-delivery.md) · [← L0](L0-ecosystem.md)
