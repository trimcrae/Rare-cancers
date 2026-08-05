---
id: DOC-TAX-TECHNOLOGY
title: Technology-dependency taxonomy — what would unblock the work, and when
level: L0
kind: policy
status: live
canonical_for: [technology_category enum, forecast model, forecast basis rules, wait-equation method]
purpose: >
  Define technology dependencies as first-class objects — the things that, if they landed, would retire
  a blocker — and the scenario-based forecast model attached to each.
scope: >
  The vocabulary, the forecast model and the calibration rules. Instances live in
  systems/graph/technologies.json and systems/graph/forecasts.json.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-05
last_verified: 2026-08-05
related: [DOC-TAX-BLOCKERS, DOC-ARCHITECTURE, DOC-CONVENTIONS]
---

# Technology-dependency taxonomy

> **Role:** the one home of the `technology_category` vocabulary, the forecast model and the rules that
> keep a forecast distinguishable from a measurement. Instances live in
> [`../graph/technologies.json`](../graph/technologies.json) and
> [`../graph/forecasts.json`](../graph/forecasts.json).

---

## 1 · Why technology dependencies are first-class

This program's bottleneck is **methods, not ideas**. Several routes unlock the moment a specific capability
becomes usable, and several closed routes are closed only against today's tools. A repository that records
*"blocked"* without recording *what would unblock it* cannot be watched — it can only be re-derived, every
session, by reading prose.

The repository already had most of the raw material: a capability-to-action trigger table, a set of revival
triggers attached to closed routes, and a weekly literature scan searching for named capabilities. What it
did not have was the **object**. The triggers were strings in three files with three different schemas, no
confidence, no timeline, and no way to ask *"what is the highest-leverage thing to wait for, and when is it
plausibly arriving?"*

A `TECH-*` is that object. It sits between a blocker and a scan trigger:

```
BLK-*  ──retired by──▶  TECH-*  ──dated by──▶  FC-*
                          │
                          └──detected by──▶  TRG-*  (literature scan, weekly)
```

---

## 2 · Categories

| category | means | example of what would count |
|---|---|---|
| `structure_prediction` | building a geometry that cannot currently be built | a co-folder benchmarked on ternary **assembly** — inter-chain accuracy on post-training-horizon complexes — rather than on per-chain accuracy |
| `free_energy_method` | resolving an energy difference today's engines cannot | an alchemical or ML free-energy method with a published known-answer validation on cryptic or induced-fit pockets |
| `conformational_ensemble` | sampling states cheaply enough to be routine | a generative ensemble model validated against known cryptic pockets, recovering benchmark sites without GPU-days of biased sampling |
| `generative_design` | designing matter, not just scoring it | a prospective molecular-glue design method demonstrated on an interface outside its training set |
| `foundation_model_biology` | predicting cellular or organismal behaviour | a virtual-cell or perturbation model that predicts held-out knockdown phenotype |
| `autonomous_research_agent` | doing the reasoning and planning work itself | an agent that can carry a multi-month research thread with reliable provenance |
| `lab_automation` | executing physical experiments remotely | a cloud or robotic lab at solo-affordable per-experiment pricing with the assay scope this disease needs |
| `biological_dataset` | data that does not exist yet for this disease | a public EMC RNA-seq or proteomics deposit beyond the single existing model |
| `experimental_access` | access rather than capability | a patient-derived EMC model reachable by an unaffiliated researcher |
| `published_measurement` | one specific primary result landing | a report contradicting a published negative that currently closes a route |
| `compute_economics` | the same method, affordably | a sustained fall in cost per simulation-nanosecond |

⚠ **`experimental_access` is not a technology and is deliberately in this register anyway.** It behaves
exactly like one — it is external, it is watched for, it would retire named blockers, and it has a plausible
arrival — and the alternative is that the single highest-fan-out non-method dependency in the portfolio has
nowhere to live. Its `technology_category` says plainly that it is access.

---

## 3 · The object

```
TECH-<SLUG>
  name                     what has to exist
  category                 one of §2
  why_it_matters           what changes about the program if it lands
  unblocks                 { blockers[], routes[], requirements[], instruments[] }
  current_state            absent | early_signals | partially_landed | landed
  evidence[]               what the current_state assessment rests on
  confidence               high | moderate | low | unknown  (in the assessment, not the arrival)
  forecast                 → FC-*
  scan_trigger[]           → TRG-* in research/method-watch-triggers.json
  fan_out                  derived: how many routes + requirements it would reopen
```

⛔ **`scan_trigger` points; it does not copy.** The search queries have exactly one home —
`research/method-watch-triggers.json` — and this register references them by id. Three files owning three
halves of one mechanism is what the division of labour exists to prevent: this taxonomy owns *what a landed
capability changes*, the trigger file owns *how to search for it*, and the closure register owns *which
parked row it belongs to*.

### 3.1 · `partially_landed` is a real state and matters

A capability can arrive for one arm of what a route needs and not another. Open ternary-complex prediction
partially fired: tools now exist and one of them reaches high accuracy **when both binding sites are
given** — which is not the same problem as predicting the assembly from sequence alone. Recording that as
`landed` would licence claims the tool does not support; recording it as `absent` would waste the arm that
did arrive. The state is `partially_landed` and `evidence[]` says which half.

---

## 4 · The forecast model

Each `TECH-*` carries exactly one `FC-*`:

```
FC-<SLUG>
  tech_ref
  scenarios:
    conservative:  { date_band, rationale, confidence }
    expected:      { date_band, rationale, confidence }
    optimistic:    { date_band, rationale, confidence }
  expected_impact: transformative | large | moderate | marginal
  basis:           evidence_based | extrapolated | speculative
  what_would_move_this
  last_reviewed
```

### 4.1 · `basis` is mandatory, and it is the honesty mechanism

| basis | means | admissible support |
|---|---|---|
| `evidence_based` | something concrete already exists that dates this — a released tool, a published benchmark, a stated roadmap, a measured price trend | cite it in `evidence[]` |
| `extrapolated` | no direct evidence for *this* capability, but a defensible trend in an adjacent, well-measured one | name the trend and why it transfers |
| `speculative` | a reasoned guess with neither direct evidence nor a measured trend | say so; do not dress it up |

⛔ **An unlabelled forecast is indistinguishable from a measurement**, and this repository has already been
damaged by a plausible-looking record being trusted for provenance it did not have. The checker refuses a
forecast without a `basis` and without a `last_reviewed` date.

⚠ **`speculative` is legitimate and is not a failure.** The alternative to a labelled guess is not a better
number, it is silence — and silence about a two-year horizon defaults the program to a *conservative* answer
without ever saying so. A labelled speculation can be argued with; an omission cannot.

### 4.2 · Calibration rules

1. **Bands, not dates.** `date_band` is a half-year or year window (`2027H1`, `2028`), never a point. A
   point estimate on a technology arrival is false precision.
2. **The three scenarios must be genuinely different.** If conservative and optimistic land in the same
   window, either the capability is nearly here or the forecast has not been thought about. Both need saying.
3. **Do not default to conservative.** The brief is explicit and it is correct: capability in this field is
   on a steep, rising frontier, and a forecast that quietly assumes today's limits are next year's limits is
   as wrong as one that assumes everything arrives at once. The `expected` scenario is the honest central
   estimate, not the safe one.
4. **Distinguish the capability from its adoption.** A method that exists in a paper, a method that exists as
   usable open-source software, and a method that has been validated on *this* regime are three different
   arrival dates. `date_band` refers to the third, because that is the one that unblocks work here.
5. **A permanent blocker's technology is not forecastable and must not have one.** A fact about what the
   objects are is not waiting for anything.
6. **`expected_impact` grades what it changes here, not the field.** A capability can be a major advance
   generally and marginal for this program.
7. **Review dates go stale.** `last_reviewed` is enforced, and a forecast older than two quarters is flagged
   in the generated view rather than silently trusted.

### 4.3 · Guardrail

**A coming capability justifies waiting and re-running. It never licences claiming the result before the
method can support it.** This is the same rule the method watch has always carried, and it is the one that
keeps a forecast register from becoming a way to bank credit for work not done.

---

## 5 · The wait equation

Each route's `timing` block asks whether to start now, and the answer depends on the technology register:

```
timing: { recommendation, rationale, six_month_delta, two_year_delta,
          cost_trend, automation_outlook, revisit_trigger → TECH-* }
```

**Wait when** the dominant cost is falling fast; a `TECH-*` with `expected` arrival inside the horizon would
change the *method* rather than merely speed it; the work would have to be redone once it lands; or the
result would be uninterpretable with today's instruments anyway.

**Do not wait when** the work is `$0` and produces a durable input; the result would *retarget* the program
rather than extend it — a cheap decisive negative is worth more now than a better one later; the capability's
`basis` is `speculative` (do not defer real work against an unevidenced arrival); or the work is
publication, which does not get cheaper.

⚠ **Waiting has a cost this register must not hide.** Deferred work stops generating the evidence that tells
you whether the route was worth pursuing at all, and a portfolio where everything is waiting is
indistinguishable from one where nothing works. `recommendation: wait` requires a `revisit_trigger`, so every
wait is a monitored condition with an owner rather than an open-ended deferral.

---

## 6 · Seeding — what becomes a `TECH-*`, and what does not

The registry inherits twenty-two revival triggers. **They are not all technology dependencies**, and sorting
them is the first thing this taxonomy does:

| existing kind | n | becomes |
|---|---:|---|
| `external_capability` | 14 | **`TECH-*`** |
| `external_access` | 1 | **`TECH-*`**, category `experimental_access` |
| `external_data` | 1 | **`TECH-*`**, category `biological_dataset` |
| `external_measurement` | 1 | **`TECH-*`**, category `published_measurement` |
| `internal_work` | 4 | ⛔ **not a technology** — see below |
| `authorization` | 1 | ⛔ **not a technology** — becomes a blocker of kind `requires_authorization` |

⭐ **The four `internal_work` entries are the finding.** They sat on a list of things to *wait for*, and every
one of them is work this program can do itself, now, at no compute cost — regenerating a prediction against a
corrected index, running an enumeration whose machinery already exists, repairing a panel's preparation. On a
watch list they are invisible; as route `best_next_action` fields they are startable.

This is the same failure the repository has named elsewhere in a different costume: filing *"no instrument
exists"* together with *"the pieces exist and nobody assembled them"* under one word, which is how the cheap
one stays invisible. They move to `best_next_action` on their routes and appear on no watch list.

**The scan side stays where it is.** Twenty-eight scan triggers already carry their queries, their evidence
homes and their reopen sets in `research/method-watch-triggers.json`, run weekly. Each `TECH-*` references
the relevant `TRG-*` ids; neither file restates the other. Where a `TECH-*` has **no** `TRG-*`, the generated
view flags it — an unscanned dependency is a capability that could land without anyone noticing, and the
current registry has several.
