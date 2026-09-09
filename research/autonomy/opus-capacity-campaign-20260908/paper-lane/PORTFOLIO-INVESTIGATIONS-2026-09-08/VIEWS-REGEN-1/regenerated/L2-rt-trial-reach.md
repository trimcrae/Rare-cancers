---
id: DOC-VIEW-RT-TRIAL-REACH
title: RT-TRIAL-REACH — Trial reachability and access pathways
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a patient with this disease actually reach the trials and the agents that a computational result would point them toward?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-TRIAL-REACH — Trial reachability and access pathways

**Family:** [ST-STRATEGY](L1-st-strategy.md) · **state:** ✓ ready · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`research/literature/fet-fusion-trial-eligibility-2026-08-07.json`](../../research/literature/fet-fusion-trial-eligibility-2026-08-07.json)): ⭐ THE MECHANISM IS REAL AND MEASURED, AND ITS SHARPEST FINDING IS AN ABSENCE (graded 2026-08-09 from a sweep that ran 2026-08-07). The route's premise is that a patient can be eligible for a trial that no histology search would ever surface, because eligibility is written on the fusion rather than the diagnosis — and that is now measured rather than argued: one recruiting trial is confirmed FET-fusion-family-defined with this disease absent from its listed conditions, and nine more are molecularly rather than histologically defined. ⛔ AND THE DRIVER GENE IS ABSENT FROM THE REGISTRY INDEX ENTIRELY: a registry-wide term search for it returns five studies of which NOT ONE is an oncology study — they are exercise physiology, spinal-cord injury, neck pain and a surgical series that mention the gene incidentally. No trial anywhere is indexed to this disease's driver. ✅ THE FOUR UNCONFIRMED CANDIDATES WERE ADJUDICATED 2026-08-09 by re-fetching each one's eligibility text: two admit and two refuse, and only one of the two that admit is an INTERVENTIONAL trial — the other enrols the patient into a real-world-evidence cohort and delivers no treatment, a distinction that must not be blurred in a reachability claim. ⛔ AND BOTH REFUSALS WOULD HAVE PASSED AN AUTOMATED SCREEN: one is titled for fusion-positive sarcoma and then restricts to three named histologies, and the other contains the exact adjective 'extra-skeletal' while meaning extraskeletal EWING. A keyword-built map would have carried both, and a map that sends a patient toward a trial that will refuse them is worse than no map. ⚠ Non-US registries are still not covered — the EU endpoint returns an authentication error.

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

Two findings meet here. A trial exists whose eligibility is defined by the fusion family this disease belongs to while its listed conditions do not name the disease, so no histology-based search reaches it — a reachability problem, and reachability is something a paper can fix. And the portfolio names publication as its endpoint everywhere while never registering the mechanism by which a published hypothesis becomes a treated patient, which leaves the chain from result to patient with a missing link nobody owns.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-FET-TRIAL-ELIGIBILITY` | one confirmed fusion-family-defined recruiting trial and nine molecularly-defined trials admit this disease while never listing it as a condition, and a registry-wide search for the driver gene returns no oncology study at all | `direct` |
| `ART-TRIAL-REACH-ADJUDICATION` | two of the four unconfirmed candidates admit this disease and only one of them is interventional, while both refusals would have passed a keyword screen — which is the argument for adjudicating eligibility text one trial at a time | `direct` |

## Remaining unknowns

- Whether the admitting trial's investigators read 'translocation-associated soft tissue sarcoma' as a general class or as the three histologies they listed — not determinable from the registry record, and exactly the question only a trial team can answer.
- Whether any of these trials would in practice accept a patient with this histology, which is each trial team's decision after their own review and not a registry fact.
- ◐ PARTLY CLOSED 2026-08-09. Four non-US registry endpoints were attempted and ONE answered: ISRCTN (UK) returned HTTP 200, EU CTIS returned 403 for the second time on a second date, ANZCTR returned 403, and jRCT failed the TLS handshake. A ClinicalTrials.gov positive control in the same run returned 200, so those are refusals by those endpoints and not a broken fetcher. ⚠ The WHO ICTRP attempt 404'd on a URL this repository guessed wrong — a defect here, not a finding about ICTRP, which remains genuinely uncovered. ⛔ A refusal is not an absence: nothing may be reported as though those registries had been searched and found empty.
- ⭐ AND THE ONE REGISTRY THAT ANSWERED INVERTED THE EXPECTED READING. It indexes no trial ABOUT this disease, but it holds one that names the disease by its exact full name in its eligibility criteria IN ORDER TO EXCLUDE IT. So where trials are indexed by histology this disease appears only as an exclusion, and where they are indexed molecularly it is admitted and never named — in neither case does a search of the diagnosis return a joinable trial. Caught by reading the full record; the titles alone said the opposite.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| ⛔ TAKEN 2026-08-07 — the registry sweep for eligibility criteria naming fusion families rather than histologies | ⛔ none built | yes | — |
| ⛔ TAKEN 2026-08-09 — per-trial eligibility-text adjudication of the four candidates the sweep could not confirm. Two admit, two refuse. | ⛔ none built | yes | — |
| Coverage of non-US registries, which need an authenticated endpoint | ⛔ none built | **no** | — |

## Readiness — what this could become today

**`internal_note`**

The finding is confirmed one trial at a time and its limits are stated. What remains is geographic coverage rather than validity.

**Missing:**
- non-US registry coverage, which needs an authenticated endpoint this programme does not have

## Where this route ends — the paper

**[PUB-STRATEGY-ARCH](L3-publications.md)** — [Eligible but unfindable — trials that admit an ultra-rare sarcoma while listing conditions that never name it](../../research/manuscripts/care-delivery/emc-trial-reachability.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** One of the variables a clinician actually controls in a cancer that will never have a randomised trial — when, in what order, and whether the patient can reach anything.

**The paper would claim:** For a cancer that will never have a randomised trial, the variables a clinician actually controls — when, in what order, and whether the patient can reach a trial at all — are treatable as research questions, and a portfolio whose every endpoint is a publication needs the step after publication registered as a route.  ⚠ THE DRAFTED PAPER COVERS THE REACHABILITY VARIABLE ONLY. The endpoint's claim spans three variables — scheduling, sequencing and reachability — and the other two are now graded as closed (RT-SCHEDULING definitional, RT-SEQUENCING instrument_limit). Their findings are real and publishable (four medians that cannot be pooled by contract, four PFS figures circulating attributed to agents that did not produce them, and a refusal to pool that is itself the result) but they are NOT in the drafted manuscript yet. ⛔ Recorded here rather than left for a reader to discover, because `drafted` on an endpoint whose paper covers one of its three routes would otherwise read as more finished than it is.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

This is the route with a live, actionable and entirely $0 output — a list of open trials a patient with this disease could be eligible for and would never find by searching their diagnosis.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-STRATEGY](L1-st-strategy.md), which is where these are asserted — a family limitation binds every route inside it.*

- Nothing in this family produces a new agent, so the ceiling of every route here is bounded by what the existing agents can do.
- Scheduling and sequencing questions are normally settled by randomised trials, and this disease will not have one — so every route here ends in a modelled or observational argument whose limits must travel with it.
- The reachability routes act on institutions rather than on biology, which is a domain where this program has no track record and where a wrong answer is not falsifiable by computation.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Best next action

Publish the eligibility map — this is the one route in the portfolio whose output could reach a patient without any new science, and its absence finding about the driver gene is a reportable fact about how the registry indexes rare disease.

*Cost:* $0

[← ST-STRATEGY](L1-st-strategy.md) · [← L0](L0-ecosystem.md)
