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

**Family:** [ST-CARE-DELIVERY](L1-st-care-delivery.md) · **state:** ○ ready · computed · confidence moderate · verified 2026-08-23

**Grade** (owned by [`systems/graph/routes.json`](../graph/routes.json)): ⭐ ANSWERED AT $0, AND THE CODE IS READ THREE WAYS RATHER THAN TWO. ICD-O-3 morphology 9231/3 is queried as extraskeletal myxoid chondrosarcoma by one SEER study (PMID 32856598), enumerated as a histological subtype of chondrosarcoma of BONE by another (PMID 31765367 — whose Methods state its myxoid bucket 'includes extraskeletal myxoid chondrosarcoma', so the merge is acknowledged, and whose 87/743 myxoid cases sit under a location variable with no soft-tissue category at all), and listed as an intracranial MESENCHYMAL/MENINGEAL tumour by a third registry's own grouping document (CBTRUS, PMC9290890). None misuses the code: a morphology code carries no topography. ⭐⭐ AND THE PHENOMENON IS MEASURED IN SEER PRACTICE, not merely permitted — a pan-soft-tissue SEER study (PMC9303001) had to exclude 1,668 bone-primary records from 115,800 retrieved on morphology (1.44%), and its Supplementary Table 1 prints 459 NON-BONE 9231 records for SEER 18, 2000-2018. SEER's own site/histology validation list (April 2022) lists 9231/3 under three BONE site groups and not under CONNECTIVE & SOFT TISSUE. ⛔ THE SIZE IS STILL NOT MEASURED, but it is now ONE precisely specified query rather than a research problem: SEER 18, 2000-2018, morphology 9231, no site restriction, divided by 459. ⛔ AND THE NAMING HALF IS WEAKER THAN THIS ROUTE ASSUMED — PMC7771031 already published it ('this tumor name has likely influenced local management patterns'), and the guideline check came back NEGATIVE at primary source — NCCN's Soft Tissue Sarcoma guideline lists extraskeletal myxoid chondrosarcoma among its histologies while its Bone Cancer guideline does not. ⭐⭐ SEPARATELY, PMID 31283732 is the one published SEER study that split chondrosarcoma by ICD-O TOPOGRAPHY, and it excluded '404 patients with extraskeletal myxoid chondrosarcoma because it is a misnomer to call it a real chondrosarcoma' while KEEPING 9231/3 on its included-morphology list — and its own Discussion concedes it could not rule out further EMC hiding among its 426 retained extraskeletal cases.

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

- The SIZE of the contamination. ⭐ NOW ONE QUERY, NOT A RESEARCH PROBLEM: SEER 18 registries, diagnosis years 2000-2018, ICD-O-3 morphology 9231, NO site restriction, divided by the 459 non-bone records PMC9303001's Supplementary Table 1 already publishes for exactly that registry set and window. ⛔ The two numbers already in hand (that 459 and PMID 32856598's 791 over 1973-2016) must NOT be divided — different windows, different registry coverage.
- CLOSED, WITH A COUNT: whether the indeterminate-diagnosis margin penalty holds in EMC specifically. It cannot be answered from PMID 39899751 — its Table 2 gives the final diagnoses of all 66 indeterminate patients and FOUR are EMC, against a margin contrast computed over 27 and 74 patients. Unanswerable from that source, in either direction.
- ANSWERED AT PRIMARY SOURCE, AND IT IS A NEGATIVE: whether treatment guidance imports conventional-chondrosarcoma reasoning for EMC. NCCN's own published topic indexes settle it — its Soft Tissue Sarcoma guideline (v5.2026) lists 'Extraskeletal myxoid chondrosarcoma' among its covered histologies, and its Bone Cancer guideline (v1.2027) covers only Bone Cancer, Chondrosarcoma, Chordoma, Ewing Sarcoma, Giant Cell Tumor of Bone and Osteosarcoma, listing EMC nowhere. Two independent EMC reviews agree and add ESMO. ⚠ The NCCN reading is of the topic INDEX, not the guideline text (PDFs are behind a login); the ESMO half is secondary, because those guidelines are not open access and returned a shim page or HTTP 403 to every route tried including a real browser. ⚠ And one clinical series asserts the opposite about PRACTICE rather than guidance (PMC7771031), unmeasured.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Run the one query that closes the size: SEER 18, 2000-2018, morphology 9231, no site restriction. Divide by 459. ⚠ Needs SEER Research base tier, which is measured as requiring an institutional email + application form + DUA (not a bare email), and SEER*Stat, which requires Microsoft Windows 10 or later — a machine this Linux-only project does not have. | ⛔ none built | **no** | BLK-REGISTRY-DUA |
| Read Table 1 of PMID 32856598, which its abstract implies prints the primary-site distribution of a 439-case 9231/3 cohort. ⚠ THIS IS NOT A DUA PROBLEM — it is a subscription PDF. Not in PMC, not open access, publisher PDF serves a JavaScript shim, DOI and article pages 403. | ⛔ none built | **no** | — |
| Upgrade both quoted Methods passages from the abstract to the full text | ⛔ none built | yes | — |

## Readiness — what this could become today

**`internal_note`**

Two things changed and they pull opposite ways. The coding argument got stronger and is now multi-registry and documented. The naming argument got weaker: it has prior art, and the guideline check came back negative. A paper should carry them at different weights rather than as one claim.

**Missing:**
- nothing to start on the CODING half — it is now three published readings, a registry edit rule, and a measured 1.44% base rate
- the SIZE, which is one query behind SEER access
- for the NAMING half: a way to say anything PMC7771031 has not already said

## Where this route ends — the paper

**[PUB-EMC-CLASSIFICATION](L3-publications.md)** — [One code, three diseases: what a registry cohort selected on ICD-O-3 morphology 9231/3 actually contains](../../research/manuscripts/care-delivery/emc-icdo-9231-classification.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The whole argument: one code read as two diseases, and a measured cost of diagnostic uncertainty.

**The paper would claim:** ICD-O-3 morphology code 9231/3 is read by published work as THREE mutually incompatible populations — extraskeletal myxoid chondrosarcoma of soft tissue (PMID 32856598), a histological subtype of chondrosarcoma of bone (PMID 31765367), and an intracranial mesenchymal/meningeal tumour (CBTRUS, PMC9290890) — because a morphology code carries no topography; SEER's own site/histology validation list takes the skeletal reading; and morphology-selected SEER sarcoma cohorts demonstrably contain bone primaries (PMC9303001 excluded 1,668 of 115,800, 1.44%). So registry-based EMC statistics carry a contamination whose size is unmeasured and is reducible to one specified query, which the paper states rather than answers.

**It is not written because:** ⭐ IT IS NOW DRAFTED — see `document`. Scope and title were decided by trimcrae on 2026-08-23: publish the CODING half without waiting for the magnitude, and demote the naming argument to a cited paragraph. The draft therefore states the contamination's size as an open, fully specified query rather than answering it. ⛔ THAT DECISION FIXED THE SCOPE AND THE TITLE. IT IS NOT AUTHORISATION TO POST, SUBMIT OR DEPOSIT — CLAUDE.md s3 requires trimcrae to name THIS paper for THAT act, per act, and he has not. Nothing has been posted anywhere. ⚠ TITLE HISTORY, recorded here because the file's frontmatter now owns the title and would otherwise carry no memory of the change: this endpoint read 'One code, two diseases: what registry-based extraskeletal myxoid chondrosarcoma cohorts actually contain' until 2026-08-23, when a third published reading of 9231/3 (CBTRUS, PMC9290890) made 'two' an understatement. Renamed on explicit instruction only. The paper was never posted under the old title, so no outside record carries it. ★ WHAT IS STILL MISSING, and it is one number rather than a programme: the topography split of a 9231/3 cohort. Two published routes would supply it, both named in the draft's section 6 — a single SEER frequency session (SEER 18, 2000-2018, morphology 9231, no site restriction, divided by the 459 non-bone records PMC9303001 already publishes), or Table 1 of PMID 32856598, which is a subscription PDF rather than a data-use-agreement problem.

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

## Best next action

Write the classification note around the CODING half, which needs nobody's cooperation: three published readings of one morphology code, SEER's own validation list taking the skeletal side, a bone-framed cohort that states it includes EMC and has no soft-tissue location category, and a 1.44% base rate for bone primaries in morphology-selected SEER sarcoma cohorts. Cite PMC7771031 for the naming half and position against it rather than restating it. Record the size as one specified query.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-CARE-DELIVERY-EVIDENCE](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against), [ART-ICDO-CONTAMINATION](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-CARE-DELIVERY](L1-st-care-delivery.md) · [← L0](L0-ecosystem.md)
