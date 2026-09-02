---
id: DOC-VIEW-RT-ENDPOINT-CHOICE
title: RT-ENDPOINT-CHOICE — Reframe the endpoint systemic-therapy trials are judged on
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is the objective-response rate a fit summary of a single-arm trial, and in which regime does it stop carrying information? Measured across trial arms in many diseases rather than in one.
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-ENDPOINT-CHOICE — Reframe the endpoint systemic-therapy trials are judged on

**Family:** [ST-DISSEMINATION](L1-st-dissemination.md) · **state:** ✓ ready · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/endpoint/response-endpoint-indolent-tumours.md`](../../research/manuscripts/endpoint/response-endpoint-indolent-tumours.md)): DELIVERABLE, complete. The manuscript exists, every figure in it is derived by a committed producer with a --check reproduction mode, and no measurement, spend, capability or third party gates it. Its ceiling is stated inside it: it is an argument about MEASUREMENT and cannot become evidence that any agent works.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_ENDPOINT_CHOICE["✓ RT-ENDPOINT-CHOICE"]:::fam
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

✓ Already cleared by this route: `BLK-NO-WET-LAB`.

## Scientific rationale

The failure of a response summary is a property of two measurable coordinates - the plausible response rate and the accruable sample size - rather than of any tumour type. Across 552 arms in 138 trials reporting a complete four-cell best-response table, the gap between disease control and objective response has a median of 39.4 percentage points. Of the conditions placed on the two axes, a group has a median response at or below the 5% null so no single-stage design is defined for them; among the rest, between 31.8% and 73.9% have a median trial smaller than such a design requires. That is a BOUND rather than a point estimate because the accrual axis pools completed trials with trials terminated for accrual, which are biased in opposite directions and whose mixing ratio is an artefact of two truncated queries. The zero-event boundary result was WITHDRAWN on the same check: its interval runs 0.0% to 47.8%, so it came entirely from trials that failed to accrue. Reporting is the binding constraint: of 2851 trials whose registry text names best overall response, 2715 (95.2%) post results without the four categories; over the whole pooled screen the figure is 4276 of 4414 records (96.9%), and the narrow denominator is reported because it is the stricter test rather than the larger number. Remedies already exist in four families across 12 disease domains, so the gap is diffusion rather than invention. Extraskeletal myxoid chondrosarcoma is the worked extreme at the 88.9th percentile of the cross-disease gap distribution. SUPERSEDED, RETAINED: this record previously framed the route as a question about 'an indolent ultra-rare sarcoma' and rested on the 47 patients and 36 discordant patients of the single-disease paper. That framing was retired on 2026-08-09 when the paper was generalised; the EMC figures are unchanged and are now one labelled point rather than the subject.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-ENDPOINT-ORR-DCR-REREAD` | the re-read itself - 552 arms in 138 trials with both endpoints on one denominator, the gap as a single proportion with an exact interval, and the reporting census that makes the gap's rarity measurable rather than asserted | `direct` |
| `ART-ENDPOINT-REGIME-MAP` | the two-coordinate map and its boundaries as level sets of the binomial, including the 16 conditions for which no single-stage design against a 5 percent null is defined at any size | `direct` |
| `ART-ENDPOINT-PRIOR-ART-AUDIT` | the necessity check that reframed the paper - four remedy families already endorsed across 12 disease domains, earliest 1998 - so the contribution is diffusion and placement rather than a new endpoint | `direct` |
| `ART-ENDPOINT-PLACEBO-CALIBRATION` | how little comparator evidence the corpus holds, and specifically that the low-response corner has almost none, which is what stops the paper claiming disease control is the right endpoint instead | `direct` |
| `ART-ENDPOINT-CORPUS` | the arm-level inclusion rule everything above is computed over, with no disease-level criterion anywhere in it | `direct` |
| `ART-EMC-ENDPOINT-DISCORDANCE` | the worked extreme: the EMC numbers that began this route, now one labelled point at the 88.9th percentile of the cross-disease distribution rather than the subject of the paper | `direct` |
| `ART-EMC-CLINICAL-REGISTRY` | the cited EMC clinical evidence base that worked example ultimately rests on, under the evidence contract enforced as a preflight gate | `direct` |

## Remaining unknowns

- The rate of spontaneous stabilisation after documented progression in untreated advanced EMC. It is unpublished, it is what would calibrate the disease-control reading, and no randomised no-treatment arm in an ultra-rare indolent sarcoma is a realistic ask.
- Whether the two European prospective cohorts share patients - the IMMUNOSARC II abstract records 6 of 23 with a prior antiangiogenic and no patient-level data is published, so the independence of the pooled interval cannot be sized.
- What the IMMUNOSARC II full paper would do to 23 of the 47 pooled patients; it does not exist, and the abstract carries two unreconciled arithmetic inconsistencies.
- Whether any journal would accept an endpoint-methodology argument in an ultra-rare disease as publishable on its own, given that its denominator is 47 patients worldwide.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| That the two endpoints are computed over the identical patient set - if they are not, the comparison is between populations and the route's central claim is void | ⛔ none built | yes | — |
| That the re-derived pooled proportions agree with the artifact that owns them, so the discordance figures are provably about the same object | ⛔ none built | yes | — |
| A comparator that would separate treatment effect from natural history in the disease-control reading - a randomised no-treatment arm, or an observational within-patient design such as growth-modulation index or time to next treatment  ⭐ ADJUDICATED 2026-09-02 (AUT-PD-116, seat s31-emc-data-blocks, applying S41). STILL BLOCKED, WRONG BLOCKER. A randomised no-treatment arm, a growth-modulation index or a time-to-next-treatment design is trial-design and clinical content, not a dependency screen. Checked rather than assumed: research/modalities/emc-ipd-survival.json reconstructs SINGLE-INTERVAL endpoints (`curve_schema.endpoint` = os \| dss \| pfs \| lrfs \| dmfs) and holds `printed_patient_level_data.n_rows: 2`; GMI and TTNT both need PAIRED SEQUENTIAL intervals per patient, which no reachable artifact carries. ⚠ AND ONE INCONSISTENCY SURVIVES THIS EDIT rather than being fixed by it: this route's `blockers_inherited` is `[]` while this entry carries a blocker. Substituting the blocker does not resolve that, and a route-level blocker list is a ranking input this reconciliation does not touch — it is filed, not silently corrected. Per-entry justification: research/autonomy/sprint-2026-09-01/S41-BLOCKED-ROUTE-AUDIT.md and S41-proposed-routes-patch.json. The rule this applies has one home: research/modalities/emc-fourth-cohort-route-readout.json → "⭐ the_rule_this_adjudication_applies". | ⛔ none built | **no** | BLK-NO-CURATED-CLINICAL-DATA |

## Blockers this route RETIRES

- **BLK-NO-WET-LAB** — No wet lab and no collaborator — an ask needs a self-interested taker before its size matters

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-ICI-TKI](L2-rt-ici-tki.md) | what is being asked about the same trials | — | RT-ICI-TKI cites those cohorts to size the CLINICAL landscape and is explicitly not this program's contribution; this route re-reads the same cohorts to ask whether the summary statistic the field quotes from them is fit for the disease. Same patients, different question, and neither answers the other's |
| [RT-METHODS-PAPER](L2-rt-methods-paper.md) | whose methods are under examination | — | the methods paper reports THIS program's own in-silico instruments failing their known-answer controls; this route reports a measurement convention in the published CLINICAL literature. Both are ST-DISSEMINATION deliverables and neither supplies the other's content |

## Readiness — what this could become today

**`journal_submission`**

## Where this route ends — the paper

**[PUB-ENDPOINT](L3-publications.md)** — [Objective response and disease control on identical patients: what the response summary discards across 552 trial arms](../../research/manuscripts/endpoint/response-endpoint-indolent-tumours.md)

`primary` · ◐ `drafted` · aimed at `journal_submission`

**This route contributes:** The whole paper: 552 arms re-read with both endpoints on one denominator, 44 conditions placed on the two coordinates that decide whether a response readout can work, the audit showing the remedy already exists in four families across 12 domains, and the limitations section that states the natural-history confound at full strength.

**The paper would claim:** An objective-response summary discards a large, measurable share of what a trial observed, and returns nothing at all in almost half of reported arms. Across 552 arms in 138 trials carrying a complete four-cell best-response table, the gap between disease control and objective response has a median of 39.4 percentage points (IQR 20.0-54.3), is identically the stable-disease proportion so each value carries an exact Wilson interval, holds in every constructible stratum (27.2-43.6), and reaches 50 points or more in 194 arms. 251 of 552 arms (45.5%) record zero objective responses, tracking the binomial at the corpus median rate, so an uninformative readout is largely a function of arm size rather than of the agent. Reporting is the binding constraint: of 2851 trials whose registry text names best overall response, 2715 (95.2%) post results without the four categories. Between 31.8% and 73.9% of conditions with a defined comparison have a median trial too small for an exact single-stage design; that is a BOUND rather than a point estimate because the accrual axis pools two populations biased in opposite directions. Remedies exist in four families across 12 disease domains, 7 with a consensus guideline and 5 on a single trial precedent, so the gap is diffusion rather than invention. Extraskeletal myxoid chondrosarcoma is the worked extreme at the 88.9th percentile, a weaker claim about that disease and a stronger one about endpoints. WITHDRAWN 2026-08-09: the zero-event-contour result and its named disease list, which came entirely from trials terminated for failure to accrue. It asserts no efficacy, safety or clinical readiness for any agent.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

Nothing gates it - no measurement, no spend, no capability, no third party. It was unwritten only because no route modelled it, and its concrete ask is a four-cell best-response table that a trial in design can still print and a trial already published cannot, so the argument's value falls with every cohort that reports without one.

| horizon | effect |
|---|---|
| Six months | Little on the argument. The corpus grows as studies post results, and a re-extraction would move the counts without moving the shape; the EMC worked example would gain peer-reviewed counts for part of its pooled denominator if the IMMUNOSARC II full paper lands. |
| Two years | Small on the arithmetic, potentially large on the confound: prospective active-surveillance cohorts in indolent tumours are now reporting untreated response and regression rates, and enough of them would supply the comparator the interventional record does not contain. |
| Cost trend | flat |
| Automation outlook | The derivation and its reproduction check are already automated. The judgement about what stable disease means in an indolent tumour is not, and is the part that carries the paper. |

## Claim ceiling — what this route may NOT be used to claim

- It is an argument about measurement. It asserts no efficacy, potency, dose, safety, therapeutic window or clinical readiness for any agent, and makes no treatment recommendation, including a negative one.
- It does not claim disease control is the correct endpoint instead. That endpoint sits near its ceiling in exactly the regime where it is proposed, and the corpus holds almost no control arm in that regime with which to calibrate it - which is the finding, not a gap awaiting one more query.
- The corpus is not a random sample: only arms posting a complete four-cell table appear, 552 among the arms of 4414 screened studies. The paper bounds the size of what is missing and states the bias argument in both directions without settling it.
- Condition strings are registry strings. One disease may appear under several spellings and a broad string may absorb several diseases; the coarsening is directional and points toward this paper's own conclusion, which is why the phase-restricted sensitivity is reported.
- A condition coordinate is two medians over a heterogeneous set of trials, and accrual records what a trial achieved rather than what a disease could accrue.
- Posted results carry neither the response criterion version nor the imaging interval nor whether review was central, so disease-control rates measured on different schedules cannot be separated here.
- The remedy audit reports what a frozen query set returned. A disease absent from it may have an endorsed alternative these queries did not reach.
- Best response is not duration, and nothing here shows that a different endpoint would have produced a better treatment decision in any trial.

*Inherited from [ST-DISSEMINATION](L1-st-dissemination.md), which is where these are asserted — a family limitation binds every route inside it.*

- A methods paper documents what was done and what failed. It makes no claim about whether any route would work.
- The failure record's value depends on it being complete and honest, including the results that went against the program's own thesis.

## Best next action

Review the manuscript for external posting to medRxiv. Nothing else in the route is unrun.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-EMC-ENDPOINT-DISCORDANCE](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against), [ART-ENDPOINT-CORPUS](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against), [ART-ENDPOINT-ORR-DCR-REREAD](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against), [ART-ENDPOINT-PLACEBO-CALIBRATION](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against), [ART-ENDPOINT-PRIOR-ART-AUDIT](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against), [ART-ENDPOINT-REGIME-MAP](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-DISSEMINATION](L1-st-dissemination.md) · [← L0](L0-ecosystem.md)
