---
id: DOC-VIEW-RT-EARLY-PALLIATIVE
title: RT-EARLY-PALLIATIVE — Early specialist palliative care and structured symptom monitoring
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Do the non-antitumour interventions that have shown overall-survival benefit in randomised oncology trials transfer to a disease with this natural history?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-EARLY-PALLIATIVE — Early specialist palliative care and structured symptom monitoring

**Family:** [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) · **state:** ○ ready · concept · confidence low · verified 2026-09-04

**Grade** (owned by [`research/manuscripts/emc-mortality-mechanisms.md`](../../research/manuscripts/emc-mortality-mechanisms.md)): ⭑ Registered 2026-08-09 from trimcrae's mechanism-of-death question; the family this route sits in did not exist before that day.

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

This is the only route on the board whose class of intervention has randomised evidence of an overall-survival benefit in cancer at all. The trials were run in populations with far shorter survival than EMC's, which cuts both ways: a longer survivorship is a longer window for the intervention to act in, and it is also a population the trials never studied. The transfer is the whole question, and stating it as a transfer rather than as a result is the discipline this route needs. ⭑ TRIAL SET READ 2026-09-04 (AUT-219, fetch-literature.yml run 33823172816, Europe PMC, control PMID matched): the class's OS benefit is not a single trial's finding -- it REPLICATES across three independent randomised trials in three distinct populations/health systems. Temel et al. 2010 (EV-TEMEL-2010, US, metastatic NSCLC, n=151): median OS 11.6 vs 8.9 months, p=0.02. Allende et al. 2024/PACO (EV-PACO-2024, Mexico/LMIC, advanced NSCLC, n=146): median OS 18.1 vs 10.5 months, HR 1.5 [1.04-2.3], p=.030, benefit concentrated in patients with good baseline performance status/QoL. Chen et al. 2023 (EV-CHEN-2023-CEPC, China, NSCLC, n=140): HR 0.19 [0.04-0.85], p=0.029, favoring the intervention. A 2020 systematic review (EV-KOCHOVSKA-2020) shows the survival evidence base was thin at that point (2 studies, one of them a timing-within-palliative-care comparison rather than early-vs-none) -- the two subsequent RCTs materially strengthen the class-level finding. ⚠ EVERY ONE OF THESE THREE TRIALS IS NSCLC, MONTHS-SCALE SURVIVAL. EMC's natural history runs to decades. This route's central question -- does the effect transfer to a disease this indolent -- is answered by NONE of them; the trials establish the intervention class works in short-survival lung cancer, not that it works here. A search of this same 388-paper retrieved corpus for 'sarcoma' in any title returns exactly one hit, unrelated (visceral angiosarcoma epidemiology, not a palliative-care trial) -- consistent with, though not proof of, no sarcoma-specific trial existing.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `EV-TEMEL-2010` | The founding trial: median OS 11.6 vs 8.9 months (p=0.02) with early palliative care in metastatic NSCLC. | `class_inherited` |
| `EV-PACO-2024` | Independent replication in a different (Mexican/LMIC) population: median OS 18.1 vs 10.5 months, HR 1.5, p=.030. | `class_inherited` |
| `EV-CHEN-2023-CEPC` | A third independent replication, in China: HR 0.19 [0.04-0.85], p=0.029, favoring the intervention. | `class_inherited` |
| `EV-KOCHOVSKA-2020` | The evidence base was thin (2 studies) as of 2020, before the PACO and Chongqing replications -- context for how recently the class-level finding strengthened. | `class_inherited` |

## Remaining unknowns

- Whether an overall-survival effect measured in short-survival NSCLC populations transfers to a disease measured in decades, which no trial has tested -- confirmed still untested after reading all three RCTs above; each is NSCLC and none approaches EMC's natural history.
- Whether any such trial has ever enrolled a sarcoma population, let alone this histology. A title-level search of the 388-paper retrieved corpus found no sarcoma-specific palliative-care trial (one unrelated coincidental hit) -- suggestive, not exhaustive, since the search was title-only against one query's retrieval rather than a dedicated sarcoma-scoped search.
- What mechanism a survival effect would even act through here, given that the leading candidate mechanisms in the original trials were earlier symptom detection and less aggressive end-of-life chemotherapy.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A retrieved, cited set of the randomised trials in this class with their measured effect sizes and populations | ⛔ none built | yes | — |
| A trial in sarcoma or in this histology, which needs a clinical network | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Readiness — what this could become today

**`internal_note`**

The trial-literature half is now answered with three replicating RCTs, but the route's central transfer question -- does an NSCLC-measured effect apply to EMC's decade-scale natural history -- remains open by construction: no trial has tested it, and none can without a sarcoma-specific study this repository cannot run.

**Missing:**
- a dedicated sarcoma-scoped search to more rigorously confirm the absence noted above (item 2's remaining_unknowns), and the sarcoma-specific trial itself (required_validation item 2), blocked on BLK-NO-WET-LAB

## Where this route ends — the paper

**[PUB-MORTALITY-MECHANISM](L3-publications.md)** — [What kills patients with extraskeletal myxoid chondrosarcoma, and the survival available to tumour-directed therapy: a cause-of-death and relative-survival analysis of the published record](../../research/manuscripts/emc-mortality-mechanisms-paper.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The intervention arm of the paper: the only non-antitumour class with randomised survival evidence, and an honest account of how far it can be carried to this disease.

**The paper would claim:** In extraskeletal myxoid chondrosarcoma the published record does not state a mechanism for most recorded deaths; where it does, competing causes and second malignancies are the largest identifiable category and respiratory failure is not dominant. Between a fifth and a third of deaths after diagnosis are not attributed to the tumour -- a figure relative survival and registry cause attribution agree on despite sharing no input -- so the survival available to all antitumour therapy taken together is bounded at 6.7 percentage points in localised disease against 31.0 in metastatic disease.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The retrieval and reading are both done and $0; what remains (a sarcoma-specific trial) needs a clinical network this repository does not have, so the route's next state is writing up the transfer honestly, not further dispatch.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md), which is where these are asserted — a family limitation binds every route inside it.*

- The competing-mortality figure is arithmetic on published summary percentages from heterogeneous studies, not a competing-risks model, and most pairings cross populations.
- Every supportive-care effect size available to this family was measured in some other cancer; no EMC-specific supportive-care outcome data exists at all.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness, and a mechanism being common is not evidence that treating it changes survival.

## Best next action

CORRECTED 2026-09-04: the trial set is read (see supporting_evidence) -- three independent RCTs (US, Mexico, China) all show an OS benefit for early/combined palliative care in NSCLC. Next step is writing up PUB-MORTALITY-MECHANISM's intervention-arm section stating the class-level finding plainly and the transfer to EMC as explicitly unproven, not further retrieval.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 evidence:** [EV-CHEN-2023-CEPC](L5-evidence-base.md#evidence--the-literature-this-program-cites), [EV-KOCHOVSKA-2020](L5-evidence-base.md#evidence--the-literature-this-program-cites), [EV-PACO-2024](L5-evidence-base.md#evidence--the-literature-this-program-cites), [EV-TEMEL-2010](L5-evidence-base.md#evidence--the-literature-this-program-cites)

[← ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) · [← L0](L0-ecosystem.md)
