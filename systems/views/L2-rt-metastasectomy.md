---
id: DOC-VIEW-RT-METASTASECTOMY
title: RT-METASTASECTOMY — Pulmonary metastasectomy as a decision rather than a modality
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: In a lung-metastasis-dominant indolent sarcoma, what should decide whether — and how often — metastases are resected?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-METASTASECTOMY — Pulmonary metastasectomy as a decision rather than a modality

**Family:** [ST-CARE-DELIVERY](L1-st-care-delivery.md) · **state:** ○ ready · concept · confidence low · verified 2026-08-26

**Grade** (owned by [`systems/graph/routes.json`](../graph/routes.json)): ⭐ THE FINDING IS AN ABSENCE, AND IT IS THE ROUTE'S JUSTIFICATION RATHER THAN AN OBSTACLE TO IT. A 554-record open-access corpus retrieved 2026-08-09 contains ZERO EMC records matching metastasectom*. EMC is indolent, lung-dominant and measured in decades — the profile for which pulmonary metastasectomy is standard sarcoma practice — and nobody has asked the question in this histology. ⚠ 'Not found in an open-access corpus' is not 'does not exist'; a closed-access series could.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_METASTASECTOMY["○ RT-METASTASECTOMY"]:::fam
  BLK_NO_CURATED_CLINICAL_DATA{{"BLK-NO-CURATED-CLINICAL-DATA — The clinical facts these r…"}}:::blk
  BLK_NO_CURATED_CLINICAL_DATA --> RT_METASTASECTOMY
  TECH_RECONSTRUCTED_IPD(["TECH-RECONSTRUCTED-IPD<br/>expected 2026H2"]):::tech
  TECH_RECONSTRUCTED_IPD -.-> BLK_NO_CURATED_CLINICAL_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

The census bundles metastasectomy into MOD-SURGERY and grades the row `in_clinical_use`, which is how a decision with real open questions — lesion count, disease-free-interval threshold, repeat versus first resection — became invisible as a research object. The portfolio has RT-LUNG-DIRECTED for perfusion, inhaled delivery and ablation, and nothing for resection.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CARE-DELIVERY-EVIDENCE` | the measured absence of any EMC metastasectomy record in a 554-record open-access corpus | `direct` |

## Remaining unknowns

- What the selection criteria should be -- lesion number, disease-free interval, doubling time. ⛔ LESION BURDEN IS NOW MEASURED ABSENT RATHER THAN UN-CURATED: no reachable series prints per-patient lesion counts (ART-SITE-CURATION), and time to metastasis is printed only as a median in one series (5.9 years) and nowhere per patient. So no oligometastatic threshold fraction can be stated from the open-access literature, and curating it further will not produce one.
- Whether EMC's lung metastases behave like the sarcoma metastases the metastasectomy evidence base was built on, which no series has assessed.
- How much of any observed metastasectomy benefit is selection of favourable biology rather than effect of the operation, which is the central criticism of the whole metastasectomy literature and is unresolved in every histology.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Curate metastatic site, lesion burden and time-to-metastasis from the open-access series, then size the eligible fraction | ⛔ none built | yes | — |
| A comparative analysis of resected versus unresected EMC lung metastases | ⛔ none built | **no** | BLK-NO-CURATED-CLINICAL-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-CURATED-CLINICAL-DATA** | `insufficient_data` | `TECH-RECONSTRUCTED-IPD` |

## Readiness — what this could become today

**`internal_note`**

The route now has an EMC-specific number where it had none: local therapy of metastases is already given to a substantial minority (8 of 29 in one series; 8 lung metastasectomies and 2 ablations in the other), so its premise is not hypothetical. But those are counts of what was DONE with no comparator and no outcome, and the selection criteria the route exists to inform need a per-patient lesion count that no reachable publication prints. ⚠ Superseded, retained: "The route has an argument and a measured absence, and no EMC-specific number of its own." It has numbers now; what it lacks is a comparator.

**Missing:**
- per-patient lesion counts, which no reachable publication prints -- the eligible fraction can be BOUNDED by lung-confinement but not SIZED by an oligometastatic criterion
- an outcome attached to the metastasectomies that were performed: both series print how many happened and neither prints what followed, so there is no comparator of any kind
- ⚠ Superseded, retained: "metastatic site and burden, which appear in free text rather than as curated data." Site is curated (ART-SITE-CURATION). Burden is not free text -- it is absent.

## Where this route ends — the paper

**[PUB-CARE-DELIVERY](L3-publications.md)** — *What decides survival in extraskeletal myxoid chondrosarcoma, and what the literature has been looking at instead* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** Plausibly the highest-yield survival intervention available in this disease today, and the one with no literature at all.

**The paper would claim:** In extraskeletal myxoid chondrosarcoma the determinants of survival that have been studied least are the ones that decide it most: the completeness of the first operation, whether the diagnosis was known before it, and whether follow-up outlasts a disease that recurs for decades.

**It is not written because:** Its four contributing routes are registered and their evidence is cited but not yet extracted. The paper needs the reconstructed survival dataset (RT-IPD-SURVIVAL) to say anything quantitative; without it, it is an argument with citations rather than a result.

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

⛔ Do NOT re-curate the open-access series for lesion burden -- it was looked for and is not printed. What is left is a judgement call: whether an EMC note saying 'local therapy of metastases is already standard for roughly a quarter of these patients, with no comparator anywhere in the literature' is worth writing as the route's honest endpoint. ⚠ Superseded, retained: "Curate metastatic site and lesion burden from the open-access EMC series and size the metastasectomy-eligible fraction." The site half is done; the burden half is impossible from print, so the fraction cannot be sized as asked.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-SITE-CURATION](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-CARE-DELIVERY](L1-st-care-delivery.md) · [← L0](L0-ecosystem.md)
