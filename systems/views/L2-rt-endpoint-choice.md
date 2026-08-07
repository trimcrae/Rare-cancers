---
id: DOC-VIEW-RT-ENDPOINT-CHOICE
title: RT-ENDPOINT-CHOICE — Reframe the endpoint advanced-EMC systemic therapy is judged on
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is the objective-response rate a fit summary of systemic-therapy outcomes in an indolent ultra-rare sarcoma, and what does the published record lose by using it?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-ENDPOINT-CHOICE — Reframe the endpoint advanced-EMC systemic therapy is judged on

**Family:** [ST-DISSEMINATION](L1-st-dissemination.md) · **state:** ✓ ready · computed · confidence moderate · verified 2026-08-07

**Grade** (owned by [`research/manuscripts/emc-response-endpoint-paper.md`](../../research/manuscripts/emc-response-endpoint-paper.md)): DELIVERABLE, complete. The manuscript exists, every figure in it is derived by a committed producer with a --check reproduction mode, and no measurement, spend, capability or third party gates it. Its ceiling is stated inside it: it is an argument about MEASUREMENT and cannot become evidence that any agent works.

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

EMC is indolent: this repository's own pooled reading of its outcome cohorts puts distant metastasis far above disease-specific death, over follow-up windows in which most patients are alive. An endpoint that records only tumour shrinkage therefore has almost no category to put this disease's observations into. Read over the identical 47 patients ever evaluated for response inside a prospective EMC trial, objective response is 12.8 percent and disease control is 89.4 percent - and the entire 76.6-point gap is 36 patients whose best response was stable disease. That gap is a fact about two endpoints on one dataset, not evidence about any drug, and the route's own strongest objection is that stable disease in an indolent tumour may be natural history. What survives that objection unaltered is the arithmetic: at the pooled response rate a 20-patient single-arm trial expects 2.6 responses and has a 6.5 percent chance of seeing none at all (29 percent at the interval's lower bound), so a zero in that regime is uninterpretable rather than negative. Alongside it sits a reporting finding with a trivial remedy - of the 9 published EMC systemic-therapy cohorts, 7 report extractable objective-response counts and 1 reports a 6-month progression-free count, so the endpoint the field's own trials migrated to is the one it reports least completely.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-EMC-ENDPOINT-DISCORDANCE` | the two endpoints computed over the identical 47-patient denominator, the 36 discordant stable-disease patients derived two independent ways, the reporting-completeness census, and the small-trial binomial arithmetic - all reproducible offline via --check | `direct` |
| `ART-EMC-CLINICAL-REGISTRY` | the cited EMC clinical evidence base the counts ultimately rest on, under the evidence contract enforced as a preflight gate | `direct` |

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
| A comparator that would separate treatment effect from natural history in the disease-control reading - a randomised no-treatment arm, or an observational within-patient design such as growth-modulation index or time to next treatment | ⛔ none built | **no** | BLK-NO-EMC-DATA |

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

**[PUB-ENDPOINT](L3-publications.md)** — [Objective response is the wrong endpoint for extraskeletal myxoid chondrosarcoma: the same 47 patients, read two ways](../../research/manuscripts/emc-response-endpoint-paper.md)

`primary` · ◐ `drafted` · aimed at `journal_submission`

**This route contributes:** The whole paper: the two endpoints on one denominator, the 36 discordant patients, the reporting-completeness census, the small-trial arithmetic, and the limitations section that states the natural-history confound at full strength.

**The paper would claim:** Summarising systemic therapy in an indolent ultra-rare sarcoma by its objective-response rate discards most of what its own trials recorded - over the identical 47 patients ever evaluated in a prospective EMC trial, response is 12.8 percent and disease control 89.4 percent, and the whole 76.6-point gap is 36 patients with stable disease - while at achievable sample sizes a response-rate readout returns a result that is uninterpretable rather than negative a substantial fraction of the time. It does NOT claim disease control is the right endpoint instead, and asserts no efficacy for any agent: the confound it cannot remove is that stable disease in an indolent tumour may be natural history, and it states that objection at full strength rather than deflecting it.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

Nothing gates it - no measurement, no spend, no capability, no third party. It was unwritten only because no route modelled it, and the argument's value is highest before the next EMC cohort reports, because its concrete ask is a four-cell best-response table that a trial in design can still print and a trial already published cannot.

| horizon | effect |
|---|---|
| Six months | Little. The IMMUNOSARC II full paper could land and would replace 23 of 47 pooled patients with peer-reviewed counts; the paper already brackets the numerical effect at 1.7 percentage points. |
| Two years | Small on the arithmetic, potentially large on the confound: an observational growth-rate or time-to-next-treatment analysis in a sarcoma registry would supply the within-patient comparator this literature lacks. |
| Cost trend | flat |
| Automation outlook | The derivation and its reproduction check are already automated. The judgement about what stable disease means in an indolent tumour is not, and is the part that carries the paper. |

## Claim ceiling — what this route may NOT be used to claim

- It is an argument about measurement. It asserts no efficacy, potency, dose, safety, therapeutic window or clinical readiness for any agent, and makes no treatment recommendation, including a negative one.
- It does not claim disease control is the correct endpoint instead. At 89.4 percent that endpoint is near its ceiling, it has no comparator in this disease, and an unknown share of the stable diseases would have been stable untreated.
- Every pooled denominator is under 60 patients worldwide, ever. One contributing cohort is 2 patients. The width of the intervals is a finding, not a provisional estimate awaiting a larger series.
- No randomised evidence exists for any systemic therapy in EMC; the one randomised dataset that touches the disease had a control arm containing no EMC patients at all.
- Best response is not duration. The route measures neither how long control lasted nor what any patient's outcome was.

*Inherited from [ST-DISSEMINATION](L1-st-dissemination.md), which is where these are asserted — a family limitation binds every route inside it.*

- A methods paper documents what was done and what failed. It makes no claim about whether any route would work.
- The failure record's value depends on it being complete and honest, including the results that went against the program's own thesis.

## Best next action

Review the manuscript for external posting. Nothing else in the route is unrun.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-EMC-ENDPOINT-DISCORDANCE](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-DISSEMINATION](L1-st-dissemination.md) · [← L0](L0-ecosystem.md)
