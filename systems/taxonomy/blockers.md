---
id: DOC-TAX-BLOCKERS
title: Blocker taxonomy — why work stalls, typed
level: L0
kind: policy
status: live
canonical_for: [blocker_kind enum, blocker classification rules, the current blocker register mapping]
purpose: >
  Define the closed set of reasons work can be blocked, so that four different situations with four
  different remedies are never filed under one word.
scope: >
  The kinds and the classification rules. The blockers themselves live in systems/graph/blockers.json;
  this file owns the vocabulary, not the instances.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-05
last_verified: 2026-08-05
related: [DOC-TAX-TECHNOLOGY, DOC-ARCHITECTURE, DOC-CONVENTIONS]
---

# Blocker taxonomy

> **Role:** the one home of the `blocker_kind` vocabulary and the rules for choosing between kinds.
> Instances live in [`../graph/blockers.json`](../graph/blockers.json) and are rendered to
> [`../views/registers/blockers.md`](../views/registers/blockers.md).

---

## 1 · Why this is an enumerated field

A register that files *"the biology forbids this"* beside *"today's free-energy method cannot resolve it"*
under the single word **blocked** has destroyed the only information that decides what to do next. The first
is finished. The second is the most revivable situation there is, and is where most of this program's
failures actually sit.

This repository already learned that lesson once, on the closure side: routes carry an enumerated
`closure_kind` precisely so that a fact about a sequence is never filed with a limitation of an engine. The
blocker taxonomy is the same discipline applied to the *live* register rather than the closed one.

**The governing rule: never conflate.** Two blockers may look alike in their consequence — nothing moves —
and still require opposite responses. A `requires_wet_lab` blocker will not be retired by any amount of
compute. A `requires_better_simulation_accuracy` blocker will not be retired by more sampling. A
`requires_authorization` blocker is not waiting on nature at all.

---

## 2 · The kinds

Fourteen kinds in five groups. Every blocker carries **exactly one**. Where more than one seems to apply,
§3 gives the tie-break.

### Group A — the world is like that

| kind | means | what retires it | permanent? |
|---|---|---|---|
| `fundamental_biological_limit` | a fact about what the objects **are**. A residue the paralogues share cannot discriminate between them; a ligand whose mechanism lives in a domain the disease deletes cannot act. | nothing. A contradicting primary measurement of the same fact, if the "fact" turns out to be wrong. | **yes** |
| `scientific_uncertainty` | the question is genuinely open — not unmeasured for want of a tool, but *unformulated* or unresolved in the field. Includes an absent specification: nobody has stated how much of something the route would need. | reasoning, a specification decision, or a field-level result | no |

### Group B — we do not have the data

| kind | means | what retires it | permanent? |
|---|---|---|---|
| `insufficient_data` | the measurement exists as a category but not for this disease. EMC is nearly absent from public functional genomics; a class vulnerability has never been tested in an NR4A3 fusion. | a dataset landing — see `TECH-*` of category `biological_dataset` | no |
| `no_known_assay` | **no readout with power exists**, in silico or at the bench. Distinct from "we have not run it": two independent attempts, the second adequately powered, returning null is evidence the *readout* cannot resolve this system's effect size. | a different readout, or a different test system whose effect is large enough | no |

### Group C — the method is not good enough

| kind | means | what retires it | permanent? |
|---|---|---|---|
| `requires_better_simulation_accuracy` | the engine is **biased or wrong**, not slow. An absolute free-energy engine that misses a known answer by more than the entire margin it is used to compute does not get better with more sampling. | a method with a published known-answer validation in the same regime | no |
| `requires_gpu_scale_simulation` | the method is **sound but unaffordable at the needed scale** — more replicates, longer trajectories, a larger system. | cheaper compute, or a cheaper method of equal accuracy | no |
| `requires_better_structure_prediction` | the geometry cannot be built. Ternary assembly, induced complexes, observed rather than composed multi-protein geometry. | a structure predictor validated on that specific task | no |
| `requires_improved_ai_reasoning` | the bottleneck is planning, synthesis or judgement at a scale a human cannot sustain — not a physical simulation. | autonomous research agents, scientific foundation models | no |

⛔ **`requires_better_simulation_accuracy` and `requires_gpu_scale_simulation` are the pair most likely to be
conflated, and the confusion is expensive in the direction that costs money.** Reading an accuracy problem as
a scale problem produces a proposal to buy more GPU hours for a result that would still be wrong. The test:
*if this ran ten times longer with ten times the replicates, would the answer be trustworthy?* If yes, it is
scale. If the miss is systematic, it is accuracy.

### Group D — it needs a bench, a robot or a person

| kind | means | what retires it | permanent? |
|---|---|---|---|
| `requires_wet_lab` | only a physical experiment can answer it. Whether *anything* binds a pocket is the canonical case: no in-silico instrument serves it, and a negative would be as useful as a positive. | a collaborator, or an affordable automated lab | no |
| `requires_robotics` | the experiment is specified and the reagents exist, but execution needs automation to be affordable or reproducible at the needed throughput. | laboratory robotics reaching solo-affordable scope | no |
| `requires_lower_experimental_cost` | it could be run today and the price is the only obstacle. | falling assay or synthesis cost | no |
| `requires_external_collaboration` | it needs **access**, not money: a cell line whose repository excludes unaffiliated individuals by policy, a patient-derived model, an institutional account. | a self-interested collaborator, or a policy change | no |

⚠ **`requires_external_collaboration` and `requires_lower_experimental_cost` must not be merged.** Where a
repository excludes individuals by published policy rather than by price, no budget reaches it — and calling
that a cost problem invites the wrong plan.

### Group E — waiting on a decision, not on nature

| kind | means | what retires it | permanent? |
|---|---|---|---|
| `requires_authorization` | built, staged, and waiting for a person to say go. Nothing failed and nothing is missing. | a decision | no |
| `requires_budget` | authorised in principle, unaffordable in practice at today's prices. | budget, or a falling price | no |

⛔ **A `requires_authorization` blocker must never be recorded as low value.** The failure this repository
already made, more than once, is that an item which was *not authorised* got written down as *low priority*,
because the only column available for "not now" was the one that grades importance. The
[three orthogonal axes](../CONVENTIONS.md#3--three-orthogonal-axes) exist to stop that, and this kind is the
main reason they do.

---

## 3 · Choosing a kind

Apply in order; the first that fits, wins.

1. **Is it a fact about what the objects are?** → `fundamental_biological_limit`. **Permanent.** It may carry
   no technology dependency and must never appear on a watch list.
2. **Is it waiting on a person or a budget?** → `requires_authorization` / `requires_budget`. Check this
   early: a decision blocker misfiled as a method blocker looks like a research problem and gets researched.
3. **Would a physical experiment answer it?** → Group D. Then choose within the group by what is actually
   scarce: access (`requires_external_collaboration`), automation (`requires_robotics`), money
   (`requires_lower_experimental_cost`), or simply a bench (`requires_wet_lab`).
4. **Does the data exist somewhere, just not for EMC?** → `insufficient_data`.
5. **Does a readout with power exist at all?** → if not, `no_known_assay`.
6. **Is the method wrong, or merely expensive?** → `requires_better_simulation_accuracy` vs
   `requires_gpu_scale_simulation`, by the ten-times test above.
7. **Is the geometry the problem?** → `requires_better_structure_prediction`.
8. **Is the bottleneck planning and synthesis rather than physics?** → `requires_improved_ai_reasoning`.
9. **None of the above, and the question itself is open?** → `scientific_uncertainty`.

**A blocker that resists this ladder is usually two blockers.** Split it. Blockers are cheap; a compound
blocker that half of a portfolio inherits is not.

---

## 4 · Invariants

1. Exactly one `blocker_kind` per blocker.
2. Every blocker names its **owner** — the file that owns the statement — and the anchor resolves.
3. Every **non-permanent** blocker names at least one `TECH-*` that would retire it. A blocker with no route
   out is either permanent or under-analysed, and both need saying.
4. A **permanent** blocker carries **no** `TECH-*` and appears on **no** watch list.
5. Every blocker records `inherited_by[]` (routes it holds down) and `retired_by[]` (routes that answer it) —
   both derived from the route register, never typed.
6. `blocker_kind` may not be changed without an appendix line recording the previous kind and why it moved.
   A reclassification changes what the program watches for, so it is a decision, not a tidy-up.

---

## 5 · Fan-out is the portfolio's shape

A blocker on one route is a risk. A blocker on fifteen is the portfolio's shape, and the highest-leverage
thing to watch for. The register therefore orders by fan-out, and the generated view leads with it.

Two derived readings the view publishes, both of which are decision-relevant and neither of which any single
route can see:

- **Load-bearing blockers** — sorted by how many routes inherit them. The repo-wide rate-limiter is a data
  blocker, not a method one, and that only becomes visible when counted across all forty routes.
- **Retirement coverage** — for each blocker, which routes *answer* it. A route that retires a widely
  inherited blocker is the portfolio's hedge against that blocker, and is worth more than its own grade
  suggests.

---

## 6 · Mapping of the existing register

The sixteen blockers inherited from the route registry, with the kind each is assigned. Reclassifications
away from the obvious reading are annotated, because §4.6 requires the reasoning to travel with the change.

| blocker | kind | note |
|---|---|---|
| `BLK-NO-EMC-DATA` | `insufficient_data` | the repo-wide rate-limiter; highest fan-out in the portfolio |
| `BLK-NOT-FUSION-SELECTIVE` | `fundamental_biological_limit` | the LBD *is* wild-type NR4A3 sequence — a fact about the objects. **Permanent** |
| `BLK-PARALOGUE-DDG` | `requires_better_simulation_accuracy` | ⚠ **not** `requires_gpu_scale_simulation`. The engine misses a known absolute answer by more than the margin it is used to compute; more sampling does not fix a systematic miss |
| `BLK-R4-BINDS` | `requires_wet_lab` | no in-silico instrument can serve it; a negative is as useful as a positive |
| `BLK-NO-WET-LAB` | `requires_external_collaboration` | ⚠ **not** `requires_lower_experimental_cost` — the operating-regime blocker is a taker, not a price |
| `BLK-ANTIGEN-COLD` | `fundamental_biological_limit` | the tumour's immunogenicity; shared by every antigen-directed route |
| `BLK-TERNARY-GEOMETRY` | `requires_better_structure_prediction` | assembly, E3 choice, exit vector, ubiquitin transfer |
| `BLK-INDUCED-COMPLEX` | `requires_better_structure_prediction` | the same generation problem with a different second terminus |
| `BLK-DELIVERY` | `requires_future_technology` | oligonucleotide tumour delivery. ⚠ **Not** `requires_wet_lab`: an assay would not settle it. The honest bottleneck is that no validated way to deliver an oligo to a non-hepatic solid tumour exists at all, so there is nothing to assay yet |
| `BLK-VECTOR-DELIVERY` | `requires_future_technology` | gene-therapy payload into a solid tumour. Kept **separate** from the row above: they are different engineering problems with different candidate solutions, and merging them would let one arriving imply the other had |
| `BLK-CLASS-INHERITANCE` | `insufficient_data` | no NR4A3 fusion has been tested for the phenotype; it is the strength of a transfer argument |
| `BLK-ENDPOINT-MD` | `no_known_assay` | ⚠ two attempts, the second adequately powered, both null. The block is the readout's resolution against this system's effect size — **not** sample size, so it is not a scale blocker |
| `BLK-FUNCTIONAL-ACTIONABILITY` | `requires_wet_lab` | a functional cell assay nobody has run |
| `BLK-PARALOGUE-CONTROL` | `no_known_assay` | the available positive control passes for a confounded reason; no sample size and no better method fixes a confound in the system |
| `BLK-UNSIZED-REQUIREMENT` | `scientific_uncertainty` | an absent specification, not a measured shortfall — nobody has stated how much selectivity the route would need |
| `BLK-REACH-CATEGORICAL` | `scientific_uncertainty` | geometry at one opened frame; it can refute a route, it cannot license one |

⚠ **`requires_future_technology` is deliberately a fallback, not a first choice.** It is correct only when
the enabling thing does not exist in any form — as with tumour delivery of an oligonucleotide to a
non-hepatic solid tumour. Wherever a more specific kind fits, the specific kind is used, because
"requires future technology" is close to saying nothing.

### 6.1 · A gap this taxonomy exposes immediately

The register has **no blocker of kind `requires_authorization`**, yet the program's single highest-leverage
unrun item is built, staged, and waiting on a decision — nothing failed and nothing is missing. It has been
carried as an instrument with no result rather than as a blocker, which is why it does not appear in any
fan-out count and does not compete for attention with the method problems.

That is the taxonomy doing its job on its first pass: a decision blocker that was invisible because there was
no category for it. It is added in the graph build as `BLK-SELECTIVITY-CONTROL-UNAUTHORIZED`, kind
`requires_authorization`, and is expected to be the cheapest open blocker in the portfolio — it costs a
conversation, not a capability.
