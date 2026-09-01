---
id: DOC-DEGRADER-METHODS-FAILURE-RECORD
title: "The failure record of a computation-only degrader program: what in-silico selectivity prediction could and could not establish"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: What is the honest, publishable content of a computation-only program's own failure record — which of its paralogue-selectivity claims did its instruments support, which did they not, and what is transferable to anyone else running a funnel like it?
scope: The degrader program's instrument register and the known-answer control that graded each instrument, plus the four-way outcome taxonomy the record depends on. It deliberately restates NO figure — every number has one home in a committed artifact and is cited rather than typed. It makes no claim about EMC treatment.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-06
last_verified: 2026-08-06
---
# The failure record of a computation-only degrader program: what in-silico selectivity prediction could and could not establish

> **Role: the DRAFT of the manuscript for publication endpoint `PUB-METHODS`, route `RT-METHODS-PAPER`.**
> The endpoint's working title and its one-sentence claim are owned by
> [`systems/graph/publications.json`](../../../systems/graph/publications.json) and rendered in
> [`systems/views/L3-publications.md`](../../../systems/views/L3-publications.md); this file is the prose that
> would fill them. **Subordinate to [`nr4a3-program-map.md`](../nr4a3-program-map.md)** — the roadmap owns the
> plan, the gates and every verdict, and where it and this draft differ on any of those, **the roadmap wins.**
>
> ⛔ **THIS DRAFT TYPES NO FIGURE, ON PURPOSE.** Every number in the record already has exactly one home
> (CLAUDE.md rule 1), and a manuscript draft is the single most likely place for a copy to go stale and then
> be quoted. So each finding below carries its **verdict word**, its **mechanism in one line**, and a
> **pointer to the artifact that owns its numbers**; [§9](#9--the-figure-bill--every-number-the-manuscript-must-pull-and-where-from)
> is the figure bill — field-by-field, artifact-by-artifact — that a typesetting pass reads to fill them in.
> A draft that carries the argument and cites the figures is assemblable; a draft that carries a second copy
> of the figures is a liability.
>
> ⚠ **THE FRAMING IS NOT DECIDED HERE.** [Roadmap §13](../nr4a3-program-map.md#13--the-deliverables-framing--an-open-question-with-a-register-and-no-decision)
> records the paper-framing question as OPEN and trimcrae's; [`paper-framing-options.md`](../program/paper-framing-options.md)
> §2.1 grades this framing (`P1`, the known-answer audit) as its recommendation. This draft is written **as
> `P1`** because that is what the endpoint asks for, and it **does not** settle `P1` against `P6`.
> Submission is outward-facing and therefore gated by CLAUDE.md §3 — see [§11](#11--venue-and-what-is-explicitly-not-decided-here).

---

## 0 · Status of this document

| | |
|---|---|
| endpoint | `PUB-METHODS` · route `RT-METHODS-PAPER` · strategy `ST-DISSEMINATION` |
| what blocks it | **nothing scientific.** `systems_check.py --check` emits `[B5] RT-METHODS-PAPER is ready and its endpoint PUB-METHODS is unwritten — nothing blocks this paper except writing it` |
| cost to finish | **$0.** No GPU, no rental, no bench. Every input is a committed artifact |
| what is genuinely missing | two items, both $0, both in [§10.3](#103--the-two-missing-inputs-both-0) |
| what only a wet lab could add | **nothing this paper's claim needs** — the one framing in the register of which that is true ([`paper-framing-options.md`](../program/paper-framing-options.md) §2.1) |

---

## 1 · Abstract (draft)

Computational drug-discovery programs report the funnels that worked. This paper reports one that did not, in
the form the field is short of: an **instrument-by-instrument audit**. Every method used to support a
paralogue-selectivity statement was first put to a test whose answer was already known. The results —
including the failures, the non-resolutions and the tests that were never run — are enumerated rather than
discarded. The worked system is the nuclear receptor NR4A3 and a hypothesised bivalent degrader against it;
the paper's subject is the **register**, not the target.

Of the instruments this program used, four recovered their known answer within a stated scope and sixteen are
carried as **disclosed failing** — the register's own word, which covers three materially different outcomes
that the paper's central methodological argument is written to separate. Three independent, preregistered
attempts at a **positive control for paralogue-selectivity detection** are reported: an alchemical ternary
cooperativity calibrator that recovered the **wrong sign**, an endpoint-MD sensitivity control that returned
a **null on an adequately-powered design**, and a biological retrospective that was **covalency-confounded**
and therefore could not have served at any sample size. None of the three succeeded, no fourth is staged, and
the direct consequence — stated here as it is stated in the program's own record — is that **every
paralogue-selectivity statement the program can make is an unvalidated prediction**.

Two further results give the audit its shape. First, a preregistered causal test returned its **registered
null**, and this paper argues at length that a preregistered null is **not** a fourth failure: conflating it
with the three above is a category error, and the distinction is structural rather than charitable. Second,
the program's **largest** retraction fell to a chain-ordering defect, a unit error and contaminated inputs —
**no known-answer test catches any of those**, and the panel had persisted no trajectory, so they were
correctable in principle and not in practice. The transferable prescription is therefore **two rules, not
one**: test every instrument against a known answer *and* persist the primary artifact. The second is the
more expensive rule and the one this program was missing.

⛔ This paper makes **no** claim of proteome-wide selectivity, **no** efficacy claim for extraskeletal myxoid
chondrosarcoma or any other disease, **no** safety or therapeutic-window claim, and asserts **no** clinical
readiness. Nothing here is a treatment candidate.

---

## 2 · The claim, stated once

> A computation-only program can state, with its instruments' known-answer controls attached, exactly which of
> its selectivity claims its methods were able to support and which they were not — and the disclosed failures
> are the transferable result.

That sentence is owned by [`systems/graph/publications.json`](../../../systems/graph/publications.json) →
`PUB-METHODS.what_it_would_claim` and is quoted here rather than restated in other words, so the endpoint and
the manuscript cannot drift apart.

**What the claim does NOT include, and it matters:** it is not a claim that in-silico selectivity prediction
does not work. It is a claim about **one** program's instruments, on **one** target family, run by **one**
author, and the honest generalisation is *"here is what happened when a full program was audited this way"*,
never *"this is what happens"* ([§10.1](#101--n--1-and-the-paper-must-say-so-in-the-abstract)).

---

## 3 · Why this is a paper and not a lab notebook

Three reasons, in the order a referee will want them.

**(a) The audit is complete, not selective.** Every instrument in the register carries the known-answer test
it was put to — or an explicit `⛔ none` where no such test exists — and the register is **generated from the
graph**, not hand-curated per paper
([`systems/views/registers/instruments.md`](../../../systems/views/registers/instruments.md), regenerated by
`systems/systems_check.py --write-views`). A reader can therefore check the denominator. The usual objection
to a negative methods paper — *"which failures did you leave out?"* — is answerable by construction here in a
way it is not for a retrospective write-up.

**(b) Each failure has a diagnosed mechanism, not just an outcome.** A wrong-sign calibrator whose miss is
localised to an endpoint-state error is a different contribution from "the calibration did not work"; an
adequately-powered null with a reference-set floor an order of magnitude under α is a different contribution
from "we saw nothing". [§4](#4---the-spine--four-outcomes-that-are-routinely-summed-into-one) and
[§6](#6--the-2026-08-03-sweep--three-instruments-assembled-and-graded-in-one-day) carry the mechanisms.

**(c) The field's negative-methods record is thin.** ⚠ **This is the one premise in the paper that this
repository cannot currently support with a measurement or a citation, and it is stated as a position rather
than a finding.** It is the program's standing view (CLAUDE.md §5: *"a definitional closure is a publishable
negative, and the field publishes almost none of them"*) and it is the stated rationale in
[`systems/graph/routes.json`](../../../systems/graph/routes.json) → `RT-METHODS-PAPER.rationale`. **Before
submission it needs either a cited bibliometric source or removal**; carried in
[§10.2](#102--the-one-premise-this-repository-cannot-support-today) so it cannot be forgotten. The argument
does not fall over without it — the audit stands on (a) and (b) — but the sentence must not be asserted as if
it had been measured.

---

## 4 · ⛔ THE SPINE — four outcomes that are routinely summed into one

**This is the section the paper exists to write, and getting it wrong would be worse than not writing it.**

Four results in this program are routinely confused with one another. **Three of the four are nulls of some
kind, and only two are failures.** Summing them into *"everything came back null"* is a category error, and
the program's own record says so in advance: without the distinction, *"a predictable null becomes a verdict
on the whole program through a category error"*.

⭐ **THE ONE HOME for the table below — including every figure it deliberately omits — is
[roadmap → ⛔ THE ONE HOME FOR "WHICH CONTROLS FAILED"](../nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language).**
This section states the *taxonomy* and the *argument*; it does not restate the verdicts' numbers.

| # | result | instrument | outcome word | why it has that word |
|---|---|---|---|---|
| 1 | **valB_mini** — the alchemical ternary cooperativity calibrator | `V5` | ❌ **CONTROL FAILED** | it recovered the **wrong sign** of a known cooperativity, in every preregistered replicate, at a multiple of the statistical uncertainty large enough that a sampling deficit is excluded. A failure of accuracy, not of precision |
| 2 | **selcal SMARCA2/4** — the endpoint-MD sensitivity control | `V11` | ❌ **CONTROL FAILED**, on an adequately-powered design | it did not detect a difference that is *known to exist and is published*, with no technical failures in either arm and a reference-set floor an order of magnitude below α. The design could have returned significance and did not |
| 3 | **NR-V04 retrospective** — the biological holdout | `V11` | ⚠ **NON-RESOLUTION**, and never a candidate control | it returned `DISCORDANT`. It is also **covalency-confounded** — the published selectivity is attributed to a covalent bond at a cysteine the other two paralogues lack — so a geometry readout would have passed for the wrong reason **at any sample size** |
| 4 | **RUNG 5a-KS** — the causal matched-pair kill switch | `V16` | ✅ **NOT A FAILURE — its PREREGISTERED null** | registered **in advance** as the LIKELY outcome and explicitly not a stop. It returned a **bound**, because its design condition was met |
| — | **apo pose recovery** — the blind-docking benchmark | `V3` | ⚠ **INCONCLUSIVE by its own preregistered rule** | the protocol's own ceiling missed, so the run measured the **site selection** rather than the docking. A test that cannot resolve is a third outcome and this one has been mis-read as a failure |

### 4.1 · Why #4 is not a failure, structurally rather than charitably

The distinction has to survive a hostile reading, so it is made on the instrument's construction and not on
intent.

The Tier-3 quantity `S` is an ordinary **non-covalent** alchemical double difference. **It models no bond in
either leg.** The paralogue claim the program actually rests on is *categorical* — a chemistry present in one
paralogue and absent in the others — so `S` is **structurally incapable of testing it**. What `S` can see is
the *marginal* wedge, whose expected magnitude was registered in advance as likely to be unresolvable at the
design's sampling. It came back as a **bound** rather than as a non-answer because its preregistered design
condition (seeds per arm) was met.

⛔ **And the honest half of the same paragraph:** `S ≈ 0` is uninformative *about the method*, because `V16`
**has no known-answer calibrator at all** and buying one is on nobody's rung. An uncalibrated instrument
returning zero cannot distinguish *"there is no wedge effect"* from *"this method cannot resolve the wedge
effect"*. The bound is reportable; the calibration is not, and the program's own ruling is that `S` may be
read as a bound and may **not** be reported as calibrated.

### 4.2 · What IS bad — and it is #1–#3 together, not #4

After **three** preregistered attempts there is **no working positive control for paralogue-selectivity
detection**, and **no fourth candidate is staged**. That, and not the preregistered null, is why every
paralogue-selectivity statement the program makes is an **unvalidated prediction** — a consequence written
into [`selectivity-resolution-options.md`](../../modalities/selectivity-resolution-options.md) §4 *before* the
deciding run, so it could not be re-narrated afterwards, and machine-carried by
`selcal_gate.NEXT_STEP_BY_TIER`.

⚠ **#1 and #2 are DIFFERENT INSTRUMENTS and neither invalidates the other's numbers.** One is alchemical
ternary FEP; the other is endpoint-MD interface stability. **They fail differently, too:** one gets a known
answer *backwards*, the other cannot see a known difference *at all*. Reading them as a single finding would
overstate both, which is the same category error one level down.

### 4.3 · What the SMARCA2/4 null does not license

Three bindings, all preregistered, all reproduced here because a methods paper that reports a null without
its limits is doing the thing this paper criticises:

1. ⛔ **It does not distinguish "the readout is blunt" from "this pair is hard."** The two bromodomains are
   highly similar and the published selectivity turns on a single hydrogen bond, so the null is consistent
   with both an insensitive endpoint and a genuinely narrow structural signal.
2. ⛔ **A third reading, measured afterwards, is worse for the instrument than either registered one.** Both
   registered readings assumed the simulated complexes were the complexes whose selectivity was published.
   Scored against the deposited ternaries the panel was designed around, the co-folds reproduce the internal
   E3 machinery well and the degradation-target↔E3 interface **not at all** — so the endpoint was never
   exercised on the complexes in question, and the failing stage is ternary **generation** rather than
   ranking. That makes the null **weaker** evidence about the readout, and it is **not** a route to reopening
   any selectivity statement.
3. ⛔ **The remediation is that there is none to buy.** The follow-on re-panel was **retired unrun**, because
   its own power section already showed it underpowered against the separations this program has measured. A
   gate that fails and returns "spend nothing further" is a legitimate outcome and is reported as one.

---

## 5 · The instrument register — every instrument beside the control that graded it

⭐ **ONE HOME.** The machine-readable register is
[`systems/views/registers/instruments.md`](../../../systems/views/registers/instruments.md), generated from
`systems/graph/*.json`; the **annotated** register — with each instrument's scope caveat in the words the
program fixed for it — is [roadmap §3.1](../nr4a3-program-map.md#31--the-instrument-table). This section
states the *architecture* of the register and does not copy either.

**The register's governing rule, and the paper's methodological thesis in one sentence:**

> An instrument that has never recovered a known answer **cannot support a claim, however good its output
> looks.** An instrument whose control **failed** and one that has **no control** are different facts — and
> **neither is support.**

Two corollaries the program had to learn and that a reader can take away directly:

- ⛔ **A `PASSES` means the instrument recovered *that* known answer. It never means the instrument supports
  the claim the register points it at.** The register carries a scope column for exactly this reason, and it
  is the verdict rather than a footnote: a structural descriptor that recovers one contact in one crystal
  pair has recovered one contact in one crystal pair.
- ⛔ **The claim-ceiling rule.** A requirement may never be claimed above the validation status of the
  weakest instrument that produces it. An instrument with no result sets the ceiling at *unvalidated
  prediction*; one that failed sets it lower ([roadmap §2.3](../nr4a3-program-map.md#23--the-claim-ceiling-rule-stated-so-it-can-be-checked)).

### 5.1 · The shape of the register, which is itself the result

The route record [`systems/graph/routes.json`](../../../systems/graph/routes.json) → `RT-METHODS-PAPER.instruments`
partitions the instruments this paper cites into two lists, and **the partition is the paper's headline
table**: **four** are cited as `support` (`V1`, `V6`, `V8`, `V10`) and **sixteen** as `disclosed_failing`
(`V3`, `V4`, `V5`, `V7`, `V9`, `V11`, `V12`, `V13`, `V14`, `V15`, `V16`, `V17`, `V19`, `V20`, `V21`, `V22`).

⚠ **`disclosed_failing` is one word covering at least four different facts, and §4's taxonomy is what
separates them.** The manuscript must render them separately or it will over-claim its own failure record:

| what the register means by `disclosed_failing` | examples | what it actually says |
|---|---|---|
| **a control that FAILED** | `V5`, `V7`, `V11`, `V12`, `V13`, `V17`, `V20`, `V21` | the instrument was put to a known answer and did not recover it |
| **a control that could not RESOLVE** | `V3` (INCONCLUSIVE by its own rule), `V15` (mixed nulls), `V19` (one arm ran, the decisive arm is unrun) | the test was run and returned a third outcome |
| **no control EXISTS** | `V9` (a self-check, not a known answer), `V14`, `V16`, `V22` | nothing has ever graded it, which is a hole and not a failure |
| **the control was never RUN** | `V4` — the *selectivity* free-energy known-answer test, built and staged with no result, never completed and not authorised | ⛔ the single most uncomfortable row in the register: the one test designed to grade selectivity free energy directly is the one that was never bought |

⭐ **Naming `V4` in the paper is not self-flagellation; it is the audit's integrity check.** A register that
listed only the tests that ran would be exactly the selective reporting the paper is written against.

### 5.2 · The four that passed, and what each one does not cover

The support column is short and every entry is narrow. Stating the narrowness in the paper is what makes the
failure list credible.

| id | what it recovered | ⛔ what that does **not** cover |
|---|---|---|
| `V1` | a published interface hydrogen bond, unaided, from two crystals | one contact in one pair. It grades no NR4A3 prediction, and it does not grade the endpoint readout `V11` |
| `V6` | a public relative-FEP benchmark, inside the field's accepted band | a **relative** quantity **within one pocket**, on **one charge model**. It is not a selectivity validation, and it does not transfer to the ternary or endpoint lanes, which run a different charge model |
| `V8` | a hydration free energy | a solvation smoke test. It says nothing about a protein site |
| `V10` | a published interface-mutation ΔΔG | a **large** effect. No benchmark in the register probes the regime that matters here — resolving a paralogue-scale difference between two closely related receptor states |

⛔ **The `V6` line is the one most likely to be misread by a reader and was misread inside the program.** The
published accuracy of the underlying protocol was established on one charge model; the ternary and endpoint
lanes run another, and the split is physically forced rather than sloppiness. **The accuracy control for that
second lane is `V5` — which failed.**

---

## 6 · The 2026-08-03 sweep — three instruments assembled and graded in one day

A methods paper benefits from showing the audit *running*, not only its accumulated output. On a single day,
**three instruments** were graded for the first time — one put to its own never-run self-control, one given
the independent comparator it had never had, one pointed at the receptor frame it had never been pointed at —
and a fourth, preregistered gate landed alongside them. **All four returned a negative**, and the three
instrument tests each ran at zero cost on free CPU. That is the practical argument of the whole paper:
**the audit is cheap, and the program had simply not been running it.** (The gate is an analysis over models
already held; it bought no new compute either.)

**(a) `V21`, the anti-target docking panel — fails its own cognate-ligand self-control.** Each panel receptor's
own crystallographic ligand was re-docked through the identical protocol and graded against the pose-recovery
criterion the program had already frozen elsewhere — **read from the existing module, not chosen for this
test**. A minority of receptors miss, and because every published clause built on this panel is a *maximum*
or an *every-survivor* statement over the whole panel, **one unreadable receptor changes all of them**: the
artifact grades `panel_readable: false`. ⛔ **This reaches print** — the affected clauses are in the
program's own SI. ⛔ **And the frozen rule holds:** a failing target may not be dropped, its box may not be
re-centred, and no band may be lowered. The repair that was attempted was a *receptor-completeness* repair
applied uniformly to passing and failing targets alike, and it did not restore readability.
One home: [`antitarget-selfcontrol.json`](../../modalities/antitarget-selfcontrol.json).

**(b) `V22` against `V3` — two pose methods with disjoint scoring disagree.** The primary docking instrument
had no independent comparator at all, which is why its INCONCLUSIVE could not be attributed. A
scoring-independent second method was run beside it, at the same boxes, graded by the same kernel. **No
system agrees within the recovery band**, and the disagreement decomposes as *same location, different
orientation* — a small centroid separation against an inter-method RMSD near the cost of turning the
molecule over. The requirement it serves is recorded `R5_resolved: false`, and the artifact's own sentence is
the honest one: the pose is **not attributable — and it is now attributable-to-nothing for a measured reason
rather than for the absence of a second opinion.**
⚠ **What this does not license, in the artifact's words:** not that the pose is wrong, not that either method
is wrong, and not that agreement would have meant correctness. Both methods are docking searches into a fixed
receptor, so a shared receptor-conformer error survives both — which is why the artifact also names the third
method (a generative co-fold committing coordinates) that would fail differently.
One home: [`pose-second-method.json`](../../modalities/pose-second-method.json).

**(c) The generation-frame druggability gate — `GATE_A_FAIL_BELOW_DSTAR`.** The *exact receptor frame the
de-novo campaign generated into* was scored under the harmonized detector and falls below the program's own
preregistered druggability threshold. The one-line reading, which is the transferable one:
**a candidate cannot be better than the pocket it was designed into.**
One home: [`r3-generation-frame-harmonized.json`](../../modalities/r3-generation-frame-harmonized.json) → `verdict`.

**(d) The same day, the ternary rebuild's preregistered three-arm gate returned `NO-GO`.** The
assembly-route ternaries do not discriminate the target from its paralogues: of the three registered arms,
the sequence-encoded arm passes, the reproducibility arm is INDETERMINATE with no column passing, and both
tether-geometry conventions fail. ⛔ Whatever it says is **structural** — no free energy is computed, and
nothing about affinity, degradation, efficacy or safety follows.
One home: [`nr4a3-5bt-gate.json`](../../modalities/nr4a3-5bt-gate.json) → `verdict` / `sentence`.

⭐ **The deepening of (d), two days later, is the strongest single negative in the record, and it is strong
because of the pairing.** The instrument used is `V1` — the one that **did** recover a published contact
unaided, from two crystals. Run over every model of the focus arm, it finds **no**
sequence-encoded discriminating contact in **any** of them. A descriptor that demonstrably can see a real
contact, pointed at our system, returns none. **That is a null with a working detector behind it, which is
exactly the configuration the other three positive-control attempts never reached.**
One home: [`nr4a3-5bt-signature.json`](../../modalities/nr4a3-5bt-signature.json) → `sentence_replicated`.

---

## 7 · What a computation-only program can and cannot establish about selectivity

The paper's second contribution is a **boundary**, drawn from this program's own experience rather than
argued from first principles.

### 7.1 · What it CAN do

1. **Grade its own instruments.** A known-answer test costs close to nothing and, in this program, **has
   never once been wasted**: every instrument put to one returned a *readable* verdict, and readable is the
   whole point. This is the surviving general lesson.
2. **Exclude a design class on evidence.** A screening-grade scoring margin was refuted as a selectivity
   verdict by pushing unrelated marketed drugs through the identical funnel and measuring the
   false-positive rate — a within-repo null that killed a headline. A signal smaller than its own noise is
   not recoverable by any downstream method.
3. **Bound an effect size.** A preregistered null that meets its design condition returns a *bound*, which is
   a quantitative statement and not an absence ([§4.1](#41--why-4-is-not-a-failure-structurally-rather-than-charitably)).
4. **Calibrate a screen against a measured background.** A categorical screen was, until recently, an
   enrichment over an *unmeasured* background — the exact shape that cost the program the result in (2).
   Pushing unrelated close paralogue pairs through the identical pipeline makes a zero gradeable.
   ⛔ With the caveat that travels with it: the program's headline residue falls outside one of the two
   preregistered scopes, and a preregistered window may **not** be widened after seeing what fell outside it.
5. **Refute a published method's claim from that method's own released data.** A benchmark's *unbound*
   protocol turned out to supply information the label implied it withheld, so the arms built on it were
   re-labelled and the positive control moved to an honestly-labelled in-set case. **This is a finding about
   the field's instrument, not about our target**, and it is the kind of content a methods venue exists for.

### 7.2 · What it CANNOT do — and the first item is permanent

1. ⛔ **Answer whether anything binds.** The requirement `R4` has **no in-silico instrument and never will**;
   a bench measurement is the only answer. Under a permanent no-wet-lab regime that is a **structural**
   limit, not a scheduling one, and every conditional statement in the program inherits it.
2. ⛔ **Supply the opening penalty.** Selectivity computed only in matched pre-opened pockets can **miss or
   reverse** the true ordering, because each paralogue may pay a different price to open. The program's
   defensible position is to report everything **explicitly conditional on the chosen open states**.
   ⚠ One narrowing, which the paper should carry because it is a real methodological point: the opening
   penalty cancels to first order inside a **relative** matched-pair quantity, so it blocks the absolute
   route and not the causal one — **an argument, and recorded as one, not a measurement.**
3. ⛔ **Convert a within-run precision diagnostic into accuracy.** A closed thermodynamic cycle, converged
   sampling and forward/reverse antisymmetry were all present in the calibrator that recovered the **wrong
   sign**. Under every named error class the closure statistic is identically zero, so the cycle returns
   clean whether or not the defect exists.
4. ⛔ **Test a categorical mechanism with a non-covalent double difference** ([§4.1](#41--why-4-is-not-a-failure-structurally-rather-than-charitably)).
5. ⛔ **Say anything proteome-wide.** The only off-target breadth this program holds is a ten-receptor panel,
   and that panel is currently unreadable ([§6](#6--the-2026-08-03-sweep--three-instruments-assembled-and-graded-in-one-day) (a)).
   ⛔ **No proteome-wide selectivity claim is made or implied anywhere in this paper.**

### 7.3 · One requirement-level lesson worth its own paragraph

The program stated its selectivity requirement **symmetrically** — *"selective over both paralogues"* — for
months, and the biology does not say that. One paralogue is constrained by a named anti-target genotype that a
non-selective degrader would reconstitute; the other is bounded in one direction and unbounded in the other.
⛔ **The asymmetry runs opposite to the way the program had been reading it**: it holds *more* discriminating
power against the paralogue whose sparing is evidence-mandatory and *less* against the one it has no bound on
in either direction. ⛔ **And an absent knockout phenotype is not a safe one** — *unbounded* means the
liability could be larger, not smaller. **Nothing here licenses degrading anything, and no safety statement
is made.** The transferable point is that **a requirement written as one clause with two comparators hid a
design target for months**, which is a cheap error for any program to repeat.
One home: [roadmap §2.4](../nr4a3-program-map.md#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically).

---

## 8 · The transferable content — what another group should take from this

This is the section that has to earn the paper. Each item is a general, checkable rule with an incident
behind it.

1. ⭐ **The prophylactic is TWO rules, not one.**
   **(a) Test every instrument against a known answer before believing it** — cheap, and it caught real
   defects here. **(b) PERSIST THE PRIMARY ARTIFACT.** ⛔ Rule (b) is the one this program was missing and
   it is the more expensive of the two: the **largest** retraction in the record fell to a **chain-ordering
   defect** (the wrong protein scored as the target), a **unit error**, and **contaminated inputs**. **No
   known-answer test catches any of those.** The panel persisted no trajectory, so a read-only census found
   objects and units and **zero trajectory files** — the defects were *"each correctable in principle and
   none correctable in practice."*
   ⚠ **Corollary, and it is the honest version:** *"every withdrawn claim came from an untested instrument"*
   is **refuted** by this program's own record, and it was believed here for a while. A known-answer test is
   **necessary and not sufficient**.
2. **A within-run MBAR standard error is not reproducibility.** Across independent replicates of the same
   calibrator the replicate SD ran several-fold larger than the per-leg MBAR SE. Quoting the latter as an
   uncertainty understates it by exactly that factor.
3. **Precision diagnostics are identically blind to endpoint-state error** ([§7.2](#72--what-it-cannot-do--and-the-first-item-is-permanent) item 3).
4. **Zero events is not a zero rate.** A generative-confound control manufactured no survivors in its
   scrambled arm — which **bounds** the manufactured rate by the rule of three at several times the real
   campaign's own rate, with a Fisher test at chance. The confound was **narrowed, not excluded**, and the
   artifact's earlier reading of a zero point estimate as a measured zero is retired in place.
5. **A positive control inside the model's training horizon is a harness check, not evidence of
   generalisation** — and it should be labelled memorisation-permitting **by construction**, in the sentence
   that reports it.
6. ⛔ **A populated field is not a measured one.** Smoke-mode legs echoed a production parameter and a filled
   result field **from their environment rather than from what ran**; a completeness count believed them and
   a frozen gate emitted a verdict on them that had to be withdrawn in full. **Check the thing only a real
   run can produce** — wall time, frame count, equilibration — never the thing a default can fill in. This
   is an infrastructure lesson and it belongs in a methods paper, because the failure mode is invisible to
   every scientific check in the pipeline.
7. **An absent reading is not a reading of absence.** A collector that cannot read a leg reports the same
   shape as a leg that is not moving, and the two demand opposite responses.
8. ⭐ **A failing instrument is a harder result to publish than a hole, and a more useful one.** A hole says
   nothing was built. A failing instrument says *this was built, this is the test it was put to, and this is
   what it returned* — which is what lets somebody else decide whether to build it again.

---

## 9 · The figure bill — every number the manuscript must pull, and where from

⛔ **Nothing in this table is copied into the prose above, and nothing in it may be.** This is the list a
typesetting pass reads. Every path was verified to exist on this branch on 2026-08-06.

| § | what the sentence needs | read from |
|---|---|---|
| Abstract, §4 | the four-way outcome table with all its figures | [roadmap → the scoreboard](../nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language), the ⛔ ONE HOME block |
| Abstract, §5.1 | instrument counts, control status per instrument | [`systems/views/registers/instruments.md`](../../../systems/views/registers/instruments.md); support/disclosed split from [`systems/graph/routes.json`](../../../systems/graph/routes.json) → `RT-METHODS-PAPER.instruments` |
| §4 row 1, §7.2, §8.2 | valB_mini ΔΔG_coop, target, replicate figures, replicate SD vs MBAR SE | [roadmap scoreboard](../nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language) rows `RUNG 2` and `RUNG 2 · replicates`; [`valb-triangle-reduction.json`](../../modalities/valb-triangle-reduction.json) |
| §4 row 1, §7.2 item 3 | the closure triangle's blindness result | [`valb-triangle-closure.json`](../../modalities/valb-triangle-closure.json) → `branch_A` |
| §4 row 2, §4.3 | tier, statistic, exact and mirrored *p*, reference-set size and floor, technical failures, admitted legs | [`selcal-verdict.json`](../../modalities/selcal-verdict.json) |
| §4.3 item 2 | co-fold vs crystal DockQ on internal machinery vs target interface | [`selcal-cofold-vs-crystal.json`](../../modalities/selcal-cofold-vs-crystal.json), [`selcal-cofold-dockq.json`](../../modalities/selcal-cofold-dockq.json) |
| §4.3 item 2, §8.5 | the in-horizon positive control and the displacement calibration ladder | [`selcal-deepternary-poscontrol.json`](../../modalities/selcal-deepternary-poscontrol.json), [`selcal-dockq-decoy-scale.json`](../../modalities/selcal-dockq-decoy-scale.json) |
| §4 row 3 | tier, *p*, arrangement count, min attainable *p*, per-arm means | [`nrv04-retro-verdict.json`](../../modalities/nrv04-retro-verdict.json) → `verdict`; secondaries in [`nrv04-retro-secondaries.json`](../../modalities/nrv04-retro-secondaries.json) |
| §4 row 3 | the covalent confound — which paralogues carry the cysteine | [`nrv04-cys-conservation.json`](../../modalities/nrv04-cys-conservation.json) |
| §4 row 4, §4.1 | `S`, its replicate SD, the resolvable-magnitude bound, per-arm means | [`nr4a3-5aks-reduction.json`](../../modalities/nr4a3-5aks-reduction.json) |
| §4 row 5, §6(b) | apo pose recovery bands, the self-dock control, the site-transfer counts | [`apo-pose-recovery.json`](../../modalities/apo-pose-recovery.json), [`apo-pose-site-in-regime.json`](../../modalities/apo-pose-site-in-regime.json) |
| §5.2 `V1` | the recovered contact and its distance | [`selcal-interface-signature.json`](../../modalities/selcal-interface-signature.json) |
| §5.2 `V6`/`V7`/`V8`/`V10` | benchmark values and errors | [roadmap §3.1](../nr4a3-program-map.md#31--the-instrument-table) rows `V6`, `V7`, `V8`, `V10` |
| §6(a) | per-receptor self-dock outcomes, blocking targets, `panel_readable`, the affected SI clauses | [`antitarget-selfcontrol.json`](../../modalities/antitarget-selfcontrol.json) → `selfcontrol`, `repair_delta`, `repair_rule` |
| §6(b) | inter-method RMSD and centroid separation, band counts, `R5_resolved` | [`pose-second-method.json`](../../modalities/pose-second-method.json) → `verdict`, `part_a` |
| §6(c) | harmonized druggability against `D*` | [`r3-generation-frame-harmonized.json`](../../modalities/r3-generation-frame-harmonized.json) → `verdict` |
| §6(d) | the three-arm gate sentence, arm-by-arm | [`nr4a3-5bt-gate.json`](../../modalities/nr4a3-5bt-gate.json) → `verdict`, `sentence` |
| §6(d) deepening | models scanned, discriminating contacts found, the validating contact behind the descriptor | [`nr4a3-5bt-signature.json`](../../modalities/nr4a3-5bt-signature.json) → `sentence_replicated`, `descriptor_validation` |
| §7.1 item 2 | the decoy false-positive rate and its replication at library scale | `DECOY_2026_06_30` in [`selectivity_calibration.py`](../../modalities/selectivity_calibration.py) — ⚠ **see [§10.3](#103--the-two-missing-inputs-both-0)** |
| §7.1 item 4 | the cross-system background and its two preregistered scopes | [`categorical-decoy-null.json`](../../modalities/categorical-decoy-null.json), [`categorical-decoy-null-lbd.json`](../../modalities/categorical-decoy-null-lbd.json) |
| §7.3 | the genotype evidence and the per-tissue overlap | [`nr4a2-sparing-bound.json`](../../modalities/nr4a2-sparing-bound.json), [`nr4a-safety-genetics.json`](../../modalities/nr4a-safety-genetics.json) |
| §8 item 4 | scrambled-objective arm counts, the rule-of-three bound, Fisher *p* | [roadmap scoreboard](../nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language), the deliverables table row |
| §8 item 1 | the retraction census — objects, units, trajectory files | [roadmap §3.3](../nr4a3-program-map.md#33--the-pattern--rewritten-because-the-version-this-page-carried-was-false) |
| §8 item 6 | the withdrawn frozen-gate verdict | [STRATEGY.md Appendix A](../../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 57; predicate `nrv04_retro_panel.production_leg_check` |
| Methods | the map-quality caveat on the congeneric map (the open cycle) | [`step1-fanout-map.json`](../../modalities/step1-fanout-map.json) → `cycle_closure` |
| Methods | environment parity between the two execution providers | [`ternary-env-parity.json`](../../modalities/ternary-env-parity.json) |

---

## 10 · Honest scope and limitations

### 10.1 · n = 1, and the paper must say so in the abstract

**One pipeline, one target family, one author.** The audit is complete *within* that scope and generalises no
further. The claim is *"here is what happened when a full program was audited this way"*, and the paper must
not slide into *"this is what happens"* — which is the exact grammatical drift the program's own language
linter exists to catch. **Every instrument verdict is a statement about this program's implementation of a
method, never about the method's published accuracy in other hands.**

### 10.2 · The one premise this repository cannot support today

The sentence *"the field publishes almost none of them"* ([§3](#3--why-this-is-a-paper-and-not-a-lab-notebook)(c))
is a position, not a measurement. **Before submission it needs a cited bibliometric source or it comes out.**
Nothing else in the paper depends on it.

### 10.3 · The two missing inputs, both $0

1. ⛔ **The decoy null's primary run output lives in object storage, not in a committed JSON.** The margins
   themselves are committed in `DECOY_2026_06_30` and the arithmetic redoes from them, but for the paper
   whose headline this is, the chain must be readable end-to-end from committed artifacts. **$0 CI.** This is
   the one item `RT-METHODS-PAPER.readiness.missing` names.
2. **A single committed instrument census** carrying every instrument with its test, result and scope, so the
   register is a table a referee can check rather than prose. **$0** — and
   [`systems/views/registers/instruments.md`](../../../systems/views/registers/instruments.md) is most of the
   way there already, being generated from the graph; what it lacks is the per-instrument *scope* column that
   [roadmap §3.1](../nr4a3-program-map.md#31--the-instrument-table) carries by hand.

### 10.4 · What this paper does not claim

- ⛔ **No** proteome-wide selectivity claim, and no claim of selectivity against anything outside the
  paralogue family and the ten-receptor panel — which is itself currently unreadable.
- ⛔ **No** efficacy claim for extraskeletal myxoid chondrosarcoma or any other disease. Nothing here is a
  treatment candidate and none of it is evidence of benefit.
- ⛔ **No** safety claim, **no** therapeutic-window claim, **no** assertion of clinical readiness.
- ⛔ **No** claim that any molecule discussed binds anything. `R4` is unanswered and cannot be answered
  in silico.
- ⚠ **Novelty is incremental.** Alchemical ternary-cooperativity free-energy calculation is an active
  published area and the paper must cite and benchmark against that prior art rather than out-claim it; the
  contribution here is the **audit** and the **failure record**, not the method.
- ⚠ Every quantity in the record is conditional on a hypothesised binary pose and a chosen receptor frame —
  a *double* conditionality that the manuscript states wherever it reports a number.

---

## 11 · Venue, and what is explicitly not decided here

**Venue.** A methods/assessment journal rather than a target journal; the register's recommendation and the
$0-to-author constraint are held in [`paper-framing-options.md`](../program/paper-framing-options.md) §2.1 and the
pre-post checklist in [`nr4a3-degrader-preprint-plan.md`](../degrader/nr4a3-degrader-preprint-plan.md). ⚠ **Fee routes
change — verify each venue's in writing at submission**, per the standing rule; do not name a secondary venue
outward-facing before that check.

**Not decided here, and not decidable by an agent:**

1. **The framing choice** (`P1` — this draft — against `P6`, the candidate paper) is registered as open and
   is trimcrae's ([roadmap §13](../nr4a3-program-map.md#13--the-deliverables-framing--an-open-question-with-a-register-and-no-decision)).
   ⛔ It is **not** a gate on any roadmap row, and nothing in this draft waits on it.
2. **Whether this becomes a separate manuscript or the reordering of the existing one.** The existing paper
   plus its SI is the degrader route's single deliverable, and `paper-framing-options.md` estimates a large
   fraction of it survives into this framing largely verbatim. **This draft is the argument and the
   assembly plan; it deliberately does not fork the manuscript**, because a parallel condensed draft has
   drifted out of sync and self-contradicted here before.
3. **Submission itself** — outward-facing and irreversible, therefore gated by CLAUDE.md §3.

---

## 12 · Provenance

The registers this draft is built from — none of whose contents it restates:

- [`nr4a3-program-map.md`](../nr4a3-program-map.md) — the scoreboard, the ⛔ ONE HOME control table, §2.2 the
  requirement holes, §2.3 the claim-ceiling rule, §2.4 the asymmetric requirement, §3.1 the annotated
  instrument table, §3.3 the corrected pattern, §3.4 the four instrument facts, §13 the framing question.
- [`systems/views/registers/instruments.md`](../../../systems/views/registers/instruments.md) — the generated
  instrument register and its `allocate` relation.
- [`systems/graph/routes.json`](../../../systems/graph/routes.json) `RT-METHODS-PAPER` ·
  [`systems/graph/publications.json`](../../../systems/graph/publications.json) `PUB-METHODS`.
- [`emc-post-degrader-options.md`](../program/emc-post-degrader-options.md) §4 route 3 — the ranking that puts this
  first, and the reason it was under-rated in the first ranking.
- [`paper-framing-options.md`](../program/paper-framing-options.md) §2.1 — the `P1` framing, its evidence table and
  its two missing inputs.
- Artifacts, each verified present on this branch 2026-08-06:
  [`selcal-verdict.json`](../../modalities/selcal-verdict.json) ·
  [`nrv04-retro-verdict.json`](../../modalities/nrv04-retro-verdict.json) ·
  [`nrv04-retro-secondaries.json`](../../modalities/nrv04-retro-secondaries.json) ·
  [`nr4a3-5aks-reduction.json`](../../modalities/nr4a3-5aks-reduction.json) ·
  [`antitarget-selfcontrol.json`](../../modalities/antitarget-selfcontrol.json) ·
  [`pose-second-method.json`](../../modalities/pose-second-method.json) ·
  [`r3-generation-frame-harmonized.json`](../../modalities/r3-generation-frame-harmonized.json) ·
  [`nr4a3-5bt-gate.json`](../../modalities/nr4a3-5bt-gate.json) ·
  [`nr4a3-5bt-signature.json`](../../modalities/nr4a3-5bt-signature.json) ·
  [`valb-triangle-closure.json`](../../modalities/valb-triangle-closure.json) ·
  [`selcal-cofold-vs-crystal.json`](../../modalities/selcal-cofold-vs-crystal.json) ·
  [`selcal-deepternary-poscontrol.json`](../../modalities/selcal-deepternary-poscontrol.json) ·
  [`step1-fanout-map.json`](../../modalities/step1-fanout-map.json) ·
  [`categorical-decoy-null.json`](../../modalities/categorical-decoy-null.json) ·
  [`categorical-decoy-null-lbd.json`](../../modalities/categorical-decoy-null-lbd.json) ·
  [`nr4a2-sparing-bound.json`](../../modalities/nr4a2-sparing-bound.json).

⛔ No statement in this draft asserts NR4A3 selectivity, EMC efficacy, safety, a therapeutic window or
clinical readiness. Every predicted quantity is labelled a prediction, and every instrument verdict is
reported at the scope its own known-answer control earned.
