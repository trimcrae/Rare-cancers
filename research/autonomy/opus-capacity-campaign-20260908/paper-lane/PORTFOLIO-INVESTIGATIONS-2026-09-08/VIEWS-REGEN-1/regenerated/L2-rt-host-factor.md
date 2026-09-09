---
id: DOC-VIEW-RT-HOST-FACTOR
title: RT-HOST-FACTOR — Treating modifiable host conditions as de-facto EMC survival therapy
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: If a common, independently treatable condition raises the chance of death after an EMC diagnosis, is the drug for that condition a de-facto EMC survival drug for the patients who have it?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-HOST-FACTOR — Treating modifiable host conditions as de-facto EMC survival therapy

**Family:** [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) · **state:** ○ ready · scoped · confidence low · verified 2026-09-04

**Grade** (owned by [`research/manuscripts/emc-mortality-mechanisms.md`](../../research/manuscripts/emc-mortality-mechanisms.md)): ⭑ Registered 2026-08-09 (trimcrae). The only route in the portfolio whose intervention already exists, is already approved, and needs no EMC-specific evidence to act.

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

The argument does not need obesity, smoking or hypertension to affect the sarcoma at all, and that is what makes it strong. Roughly two of every five deaths within a decade of an EMC diagnosis are not EMC deaths; in that compartment the patient is an ordinary person of their age and sex, the deaths are ordinary deaths, and general-population evidence applies with the weakest transfer assumption anywhere in this portfolio. ⭐ That inverts this programme's usual problem: every antitumour route here is blocked on EMC-specific evidence nobody can obtain without a wet lab, while this one is blocked on population evidence that already exists in abundance. The honest consequence also cuts the claim down -- acting on that compartment alone bounds the benefit to a modest number of percentage points, to a defined subgroup, and it is not a cancer treatment.

## Remaining unknowns

- The prevalence of every candidate host factor in an EMC population, which no EMC series records -- so every prevalence must be imported from a general population and is an assumption.
- Whether any host factor changes EMC-SPECIFIC mortality, which has never been measured in this disease and is only weakly and confoundedly addressed in sarcoma.
- Whether the measured associations survive the biases that routinely reverse their sign -- reverse causation, the obesity paradox, collider bias, immortal-time and healthy-user effects -- which is the difference between a defensible recommendation and a harmful one.
- Whether deliberately inducing weight loss is SAFE in this population, which the idea as posed assumes and which is not obvious: unintentional weight loss is itself an adverse prognostic sign in cancer, sarcopenia is a measured adverse prognostic factor in sarcoma, and a GLP-1 agonist reduces lean mass alongside fat. An intervention that improves compartment B while worsening compartment A would be invisible to any analysis that reported one blended number.
- Whether a host factor reaches EMC-specific mortality INDIRECTLY through treatment rather than through tumour biology -- surgical complication rates, radiotherapy planning and cytotoxic dosing are all body-habitus dependent -- which would place a real effect in compartment A by a mechanism the compartment-B argument does not cover.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A retrieved, cited set of effect sizes for each candidate factor on all-cause mortality, with the population each was measured in | ⛔ none built | yes | — |
| A bias assessment per factor, built from the causal-inference literature rather than asserted | ⛔ none built | yes | — |
| Host-factor prevalence and outcome data in an actual EMC cohort, which requires clinical records nobody here can reach | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Readiness — what this could become today

**`internal_note`**

The model is built and the retrieval is dispatched, but no effect size has been read yet, and this is precisely the route where writing a number from memory would produce a confident clinical recommendation with nothing behind it.

**Missing:**
- the retrieved effect sizes and the bias assessment they have to be read through

## Where this route ends — the paper

**[PUB-MORTALITY-MECHANISM](L3-publications.md)** — [What kills patients with extraskeletal myxoid chondrosarcoma, and the survival available to tumour-directed therapy: a cause-of-death and relative-survival analysis of the published record](../../research/manuscripts/emc-mortality-mechanisms-paper.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The constructive half of the paper: having bounded what antitumour therapy could achieve, name the interventions that act on the remainder and are already sitting in a pharmacy.

**The paper would claim:** In extraskeletal myxoid chondrosarcoma the published record does not state a mechanism for most recorded deaths; where it does, competing causes and second malignancies are the largest identifiable category and respiratory failure is not dominant. Between a fifth and a third of deaths after diagnosis are not attributed to the tumour -- a figure relative survival and registry cause attribution agree on despite sharing no input -- so the survival available to all antitumour therapy taken together is bounded at 6.7 percentage points in localised disease against 31.0 in metastatic disease.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The model has run on retrieved effect sizes; what remains free is a targeted re-query and the paper section. The EMC-cohort validation stays blocked on BLK-NO-EMC-DATA.

| horizon | effect |
|---|---|
| Six months | The GLP-1 outcome literature is expanding quickly, so the compartment-B evidence base is one of the few in this repository that improves without anyone here doing anything. |
| Cost trend | falling |

## Claim ceiling — what this route may NOT be used to claim

- This route can only ever act on the share of deaths that are not EMC deaths; it is not a cancer treatment and must never be presented as one.
- No EMC series records any host factor, so every prevalence and every effect here is transferred from another population and none is a measurement in this disease.
- Nothing in this route asserts efficacy, safety, a therapeutic window or clinical readiness, and nothing in it is advice for any individual patient.

*Inherited from [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md), which is where these are asserted — a family limitation binds every route inside it.*

- The competing-mortality figure is arithmetic on published summary percentages from heterogeneous studies, not a competing-risks model, and most pairings cross populations.
- Every supportive-care effect size available to this family was measured in some other cancer; no EMC-specific supportive-care outcome data exists at all.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness, and a mechanism being common is not evidence that treating it changes survival.

## Best next action

MODELLED 2026-09-04 (AUT-220): research/manuscripts/emc-host-factor-inputs.json carries four factors (obesity, smoking, statin-eligible cardiovascular risk, sarcopenia) with effect sizes transcribed from probe-anchored abstracts, and emc-host-factor-model.json is the run. Compartment B is modelled for three of them; every sarcoma-specific estimate (sarcopenia OS HR, statin PFS HR) is an association and is recorded at ZERO. Diabetes and hypertension are NOT entered -- the retrieval's top hits held no usable estimate. Next: (1) re-query the probe for those two and for the primary trials (the hits are 2025-2026 syntheses, not the landmark RCTs); (2) write the compartment-B band into PUB-MORTALITY-MECHANISM as its own bounded section, with the endpoint caveat on the statin row.

*Cost:* $0

[← ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) · [← L0](L0-ecosystem.md)
