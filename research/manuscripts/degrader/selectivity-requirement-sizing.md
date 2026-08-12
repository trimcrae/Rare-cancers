---
id: DOC-SELECTIVITY-REQUIREMENT-SIZING
title: Sizing the selectivity requirement for the three routes that carry BLK-UNSIZED-REQUIREMENT
level: L3
kind: manuscript
status: live
canonical_for:
  - the stated selectivity requirement for RT-MONOVALENT, RT-TCIP and RT-ASYMMETRIC
  - the odds-product identity and which parts of the degrader margin derivation transfer to a non-degradation modality
  - the named missing inputs that block each half of those requirements from being given a number
purpose: >
  Write down the selectivity specification these three routes have never had, with its derivation and
  every assumption named, so that a future result can be shown to MEET or MISS it. Where the honest
  answer is a range or "this cannot be sized", say so and name the missing input.
scope: >
  A specification only. No molecule, no measurement, no ranking, no efficacy, potency, safety, dosing or
  clinical statement. Nothing here asserts that anything meets any requirement below.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-07
last_verified: unverified
---

# Sizing the selectivity requirement for the three routes that carry `BLK-UNSIZED-REQUIREMENT`

> **Role: a specification document.** `BLK-UNSIZED-REQUIREMENT` is held by three routes —
> [`RT-MONOVALENT`](../../../systems/views/L2-rt-monovalent.md), [`RT-TCIP`](../../../systems/views/L2-rt-tcip.md)
> and [`RT-ASYMMETRIC`](../../../systems/views/L2-rt-asymmetric.md) — and its
> `retired_by_action` is *"State the selectivity requirement the route would have to meet, with its
> basis."* This file is that statement. It discharges backlog item 5 of
> [`nr4a3-monovalent-pocket-route.md` §8](../occupancy/nr4a3-monovalent-pocket-route.md), which asked the roadmap
> for an antagonism-window number "**or** record explicitly that none exists".
>
> **$0.** No GPU, no rental, no dispatch, no purchase, nobody contacted. Every input is read from a
> committed artifact or document that already owns it; the only new content is algebra, stated in the
> open so any reader can recompute it.
>
> **Subordinate to [`nr4a3-program-map.md`](../nr4a3-program-map.md)**, which owns the plan, the gates,
> the requirement register and the degrader's own margin arithmetic. **No figure the roadmap owns is
> re-typed here** — this file points at them. Where the roadmap conflicts with this file, it wins.

---

## ⛔ 0 · Read this before anything else: what a sized requirement is, and what it is not

**A requirement is a specification. Sizing it says nothing whatsoever about whether any molecule, pose,
design or route meets it.** The blocker's own name is the warning this section exists to enforce:

> *"Nobody has stated how much selectivity the route would need, so 'the requirement is smaller' is not a
> claim this repo can make."*

Four statements bound everything below, and none of them is softened anywhere in this file.

1. ⛔ **Nothing here is evidence that any of these three routes is more feasible than it was yesterday.**
   Writing a specification down changes what can be checked, not what is true.
2. ⛔ **No paralogue-selectivity result in this repository is licensed by anything below.** Every such
   statement remains an **unvalidated prediction** under the claim-ceiling rule
   ([roadmap §2.3](../nr4a3-program-map.md#23--the-claim-ceiling-rule-stated-so-it-can-be-checked)):
   a requirement may never be claimed above the validation status of the instrument that would produce
   it, and **no instrument in [roadmap §3.1](../nr4a3-program-map.md#31--the-instrument-table) has
   returned a passing known-answer test for paralogue-scale selectivity detection.** That table owns the
   per-instrument verdicts and they are not restated here.
3. ⛔ **A requirement that comes out numerically smaller than the degrader's is not a reason to prefer a
   route.** The three reasons it cannot be read that way are given in [§2.3](#23--why-the-comparison-with-the-degraders-number-is-invalid-in-both-directions).
4. ✅ **"This cannot be sized, and here is the missing input" is a legitimate result of this exercise**,
   and it is what [§3.1](#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today),
   [§2.2](#22--what-cannot-be-sized-for-this-route-and-the-named-missing-inputs) and
   [§4.3](#43--req-asym-3--the-defect-a-scalar-creates-stated-so-it-can-be-checked) return. An unasked question converted
   into a stated open one with a named input is the retirement of an *absent specification*; it is not a
   measurement and it is not progress on the biology.

---

## 1 · The general form — and exactly which parts of the degrader derivation transfer

### 1.1 · The degrader's number, decomposed into parts that can be checked one at a time

The roadmap's
[MECHANISM-FIRST](../nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged)
section is the **one home** for the degradation-window margin, its resolvable counterpart and the measured
accuracy against it. **This file quotes none of those three numbers** — it decomposes the *derivation*
that produced the first, which is owned by
[`selectivity_margin_model.py`](../../modalities/selectivity_margin_model.py), and states per component
whether it survives the change of modality.

| # | component of the degrader derivation | transfers to `RT-MONOVALENT`? | transfers to `RT-TCIP`? |
|---|---|---|---|
| **D1** | **The window definition** — the best on-target effect reachable at any dose at which the anti-target stays at or below a ceiling, **both arms evaluated at the same dose** (`selectivity_margin_model.window`) | ✅ **yes.** It is a definition, not a physical assumption. A separation that needs a different dose per paralogue is not a separation | ✅ yes |
| **D2** | **A saturable equilibrium dose–response on both arms** | ✅ yes, in the form `θ = D/(D+K_d)` | ✅ yes, but on the *ternary* fraction rather than binary occupancy |
| **D3** | **The non-monotone (hook) dose–response of a bivalent**, inherited from the 1:1:1 solver (`andgate_degradation_model.ternary`, reused by `selectivity_margin_model.f_curve`) | ⛔ **no.** A monovalent occupier has one binding event and its occupancy is **monotone** in dose, so its window is bounded on one side only | ✅ yes — a TCIP is bivalent, so its window is bounded **above and below** and the requirement must be stated over a dose *range* |
| **D4** | **A cooperative ternary term `α`**, and the margin applied to it rather than to binary affinity | ⛔ **no.** No second protein at any stage | ✅ in form. Its magnitude is unknown for a transcriptional effector |
| **D5** | **Catalytic amplification** — `P_ss/P₀ = 1/(1 + κ·f·ε)` with `κ = k_ub_max/k_basal`, i.e. one ternary event commits a substrate and the effect integrates against protein turnover (`selectivity_margin_model.degradation`) | ⛔ **no, and this is the single largest break.** Occupancy has no turnover term to integrate against: the effect is whatever the occupied receptor does *while occupied* | ⚠ **unknown.** A recruited repressor may or may not amplify — see [§3.1](#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today) |
| **D6** | **Calibration of the on-target arm to a working degrader** (`calibrate_drive`, `on_target_dmax`), so a scenario in which nothing is degraded is not counted as selectivity | ⛔ **no.** There is no free amplification parameter to calibrate, so this step has no analogue | ⚠ no analogue that can be calibrated today, for the same reason as D5 |
| **D7** | **The 27-scenario grid** over warhead `K_d`, baseline `α` and on-target `D_max` (`SCENARIO_GRID`) that turns one answer into a median and a range | ⛔ **no.** Two of the three swept parameters do not exist for a monovalent occupier, so the monovalent requirement has a *different* set of free parameters and its spread is not comparable to the degrader's | ⛔ no, for the same reason |
| **D8** | **The categorical axes** — a paralogue that is structurally incapable rather than thermodynamically disfavoured (`categorical_axes`, `covalent_labelled_fraction`) | ✅ **yes**, and it is the covalent sub-form's whole basis — but the ubiquitination half (`unique_lysine`) does not, since there is nothing to ubiquitinate | ⚠ partly — the covalent half transfers, the lysine half does not |

⛔ **Consequence, stated so it cannot be walked back: D5, D6 and D7 are the load-bearing steps that produce
the degrader's number, and none of the three transfers to a molecule that only occupies. The roadmap's
degradation-window figure therefore MUST NOT be reused for `RT-MONOVALENT`, and is not reused here.**

### 1.2 · What does transfer: the window identity, in closed form

D1 and D2 alone determine the requirement, and they determine it *exactly*. Let

- `θ_i(D) = D / (D + K_i)` be the fraction of receptor *i* occupied at free concentration `D`,
- `A` = the required **on-target** proximal fraction, and `B` = the tolerated **anti-target** proximal
  fraction, both in the same units as `θ`,
- `ΔΔG = RT·ln(K_anti / K_on)` the free-energy difference favouring the on-target receptor.

A single dose `D` satisfies both arms iff

```
θ_on(D) ≥ A          ⇔   D ≥ K_on  · A/(1−A)
θ_anti(D) ≤ B        ⇔   D ≤ K_anti· B/(1−B)
```

and such a `D` exists iff

```
    K_anti / K_on  ≥  [ A/(1−A) ] · [ (1−B)/B ]                      (the odds-product identity)
⇔   ΔΔG            ≥  RT · ln{ [ A/(1−A) ] · [ (1−B)/B ] }
```

★ **The required selectivity fold is the product of the on-target odds and the anti-target inverse
odds.** Nothing else enters — no potency, no concentration, no receptor abundance, no rate. ⚠ **What is
eliminated is the DOSE `D`, not `K_on`** — `K_on` sits on the left-hand side, inside the molecule's own
`K_anti/K_on`. The two constraints bracket `D`, and requiring that bracket be non-empty removes `D`
entirely; that is why the *threshold* is a property of the specification pair `(A, B)` and of no molecule,
while the quantity tested against it is a property of the molecule and nothing else. *(Corrected on review:
this sentence read "`K_on` cancels", which would make the requirement dimensionally a bare number rather
than a free-energy difference and would leave the identity with nothing to test.)*

With `RT = 0.5925 kcal/mol` at 298.15 K (`selectivity_margin_model.RT`, not re-typed as a new constant):

| `A` \ `B` | 0.30 | 0.20 | 0.10 | 0.05 |
|---|---|---|---|---|
| **0.50** | 0.50 | 0.82 | 1.30 | 1.74 |
| **0.70** | 1.00 | 1.32 | 1.80 | 2.25 |
| **0.80** | 1.32 | **1.64** | 2.12 | 2.57 |
| **0.90** | 1.80 | 2.12 | 2.60 | 3.05 |
| **0.95** | 2.25 | 2.57 | 3.05 | 3.49 |

*(kcal/mol. Recompute with the formula above; this table is not read from any artifact and adds no
measurement. The bolded cell is the `(A, B)` pair the degrader model itself uses — `targets` includes 0.80
and `paralogue_ceiling` is 0.20 — reused here only so the two derivations are read at the same
specification point, never to license a comparison of the outputs; see
[§2.3](#23--why-the-comparison-with-the-degraders-number-is-invalid-in-both-directions).)*

**⚠ SENSITIVITY, WHICH IS THE POINT OF THE TABLE.** The requirement moves by `RT·ln(10) ≈ 1.36 kcal/mol`
per decade of change in *either* odds. A factor-of-ten error in the on-target target or in the anti-target
ceiling therefore moves the requirement by more than half its own value across this entire table.
**Neither odds has been measured for any route in this file.** That is not a caveat on the identity; it is
the whole reason the routes' requirements resolve to ranges and to named missing inputs rather than to
numbers.

### 1.3 · The assumptions the identity carries, each named so it can be attacked

| | assumption | what breaks if it is false |
|---|---|---|
| **A1** | Equilibrium, reversible, 1:1 binding on both arms, at one free-ligand concentration shared by both receptors | a covalent or slowly-reversible arm is **time-integrating**, not equilibrium, and the identity understates it — the same distinction `covalent_labelled_fraction` makes for the degrader |
| **A2** | `A` and `B` are stated in **proximal-quantity** space (occupancy, or ternary fraction), not in effect space | if they are read as effect fractions, the whole transfer-function problem of [§2.2](#22--what-cannot-be-sized-for-this-route-and-the-named-missing-inputs) is silently assumed away |
| **A3** | Free concentration equals nominal concentration at both receptors — no compartment, permeability, plasma-protein or tissue-distribution term | a real exposure difference between target and anti-target tissue would enter here. ⛔ For NR4A2 the roadmap has already closed that lever on evidence: 47 of 51 tissues co-express ([roadmap §2.4](../nr4a3-program-map.md#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically) → [`nr4a2-sparing-bound.json`](../../modalities/nr4a2-sparing-bound.json)), so the selectivity has to be molecular |
| **A4** | One anti-target at a time. The identity is per comparator | the two comparators are **not** one requirement — that is `RT-ASYMMETRIC`'s whole content, [§4](#4--rt-asymmetric--the-requirement-is-a-pair-and-a-scalar-is-a-defect-in-a-stated-direction) |
| **A5** | No receptor reserve on either side; effect is monotone in occupancy with no spare-receptor amplification | reserve on the **anti-target** lowers the usable `B` and raises the requirement; reserve on the **target** lowers `A` and lowers it. Unmeasured on both sides |
| **A6** | The comparator receptors are simultaneously present and equally accessible to the molecule | if not, the shared-dose premise of D1 fails and the "window" is an artifact of the arms being evaluated apart |

---

## 2 · `RT-MONOVALENT` — a molecule that only OCCUPIES the NR4A3 LBD

The route splits into two sub-forms that fail on opposite blockers; that split is
[the owner memo's §1](../occupancy/nr4a3-monovalent-pocket-route.md) and it organises this section too, because
**the two sub-forms need requirements of different KINDS, not different sizes.**

### 2.1 · Sub-form (a), non-covalent occupier — a ΔΔG threshold, stated as a PAIR

> **`REQ-MONO-1` — HARD, comparator NR4A1.**
> **Quantity:** `ΔΔG₁ = RT·ln(K_d,NR4A1 / K_d,NR4A3)` for the molecule against the two ligand-binding
> domains, both receptors at the same free concentration.
> **Threshold:** `ΔΔG₁ ≥ RT·ln{ [A/(1−A)] · [(1−B₁)/B₁] }`, with `A` the fractional LBD occupancy of the
> fusion required to move its LBD-borne output by the intended amount, and `B₁` the fractional NR4A1
> occupancy that may be tolerated.
> **Status:** the FORM is stated; the THRESHOLD is not a number, because `A` and `B₁` are unmeasured —
> [§2.2](#22--what-cannot-be-sized-for-this-route-and-the-named-missing-inputs).
> **Range over the plausible specification rectangle** `A ∈ [0.50, 0.95]`, `B₁ ∈ [0.05, 0.30]`:
> **0.50 – 3.49 kcal/mol** ([§1.2](#12--what-does-transfer-the-window-identity-in-closed-form)).

> **`REQ-MONO-2` — SOFT, comparator NR4A2.** The same quantity against NR4A2, **reported and disclosed,
> not gated.** Per [roadmap §2.4](../nr4a3-program-map.md#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically)
> NR4A2-sparing is best-effort; a molecule that misses `REQ-MONO-2` while meeting `REQ-MONO-1` carries a
> disclosed residual and is not rejected by it. ⛔ This is **not** a statement that NR4A2 engagement is
> acceptable — see [§4](#4--rt-asymmetric--the-requirement-is-a-pair-and-a-scalar-is-a-defect-in-a-stated-direction).

**Derivation:** [§1.2](#12--what-does-transfer-the-window-identity-in-closed-form), with D3–D7 dropped by
[§1.1](#11--the-degraders-number-decomposed-into-parts-that-can-be-checked-one-at-a-time). The occupancy
ratio at equilibrium is `exp(−ΔΔG/RT)`, which is the reduction the owner memo's
[§4.2](../occupancy/nr4a3-monovalent-pocket-route.md#4--effect-on-the-paralogue-requirement--reshapes-into-a-requirement-of-unquantified-size)
already states in words; this file supplies the threshold that words alone could not.

**Assumptions beyond A1–A6:** that the LBD is the site the molecule occupies on all three paralogues (the
Zaienne series' site is structurally undefined — owner memo §2.2 limit 1), and that a single `K_d` per
receptor is meaningful for a **cryptic** pocket whose population differs per paralogue (the roadmap's
MECHANISM-FIRST section records that each paralogue can carry a different opening penalty; if it does, the
effective `K_d` folds that penalty in and `ΔΔG₁` is not a pocket-interaction difference alone).

### 2.2 · What CANNOT be sized for this route, and the named missing inputs

**Neither `A` nor `B₁` can be given a value from anything this repository holds or can compute.** Both are
**transfer functions**, not free energies:

> **`MISSING-1` (sets `A`).** A dose–response relating **fractional occupancy of the NR4A3 LBD** to
> **fractional loss of the fusion's LBD-borne transcriptional output**, in a cell carrying EWSR1::NR4A3.
> ⛔ The owner memo's §2.3 states the underlying question — does repressing the LBD-borne component move
> the output of a protein whose other end is a strong, independently-acting activator — is **not
> answerable in silico** and is not served by the program's delegated dTAG test. So `MISSING-1` is a bench
> input, and it is the same input as this route's fourth blocker, `BLK-FUNCTIONAL-ACTIONABILITY`.

> **`MISSING-2` (sets `B₁`).** A dose–response relating **fractional occupancy of the NR4A1 LBD** to the
> phenotype the NR4A1 bound is about. ⛔ The bound this repository holds is a **combination germline
> genotype** ([roadmap §2.4](../nr4a3-program-map.md#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically)),
> and the roadmap's own standing rule is that a knockout bounds **developmental, complete, lifelong**
> loss and therefore sets a **ceiling of concern**, never the expected effect of a molecule. **A ceiling
> of concern cannot be inverted into a tolerated occupancy `B₁`** — that inversion is the step nobody has
> a basis for, and performing it would manufacture the number this document exists to refuse to
> manufacture.

⛔ **AND THE DIRECTION OF THE RESIDUAL IS NOT NEUTRAL.** By **A5**, receptor reserve on the anti-target
lowers the usable `B₁`, and by [§1.2](#12--what-does-transfer-the-window-identity-in-closed-form) each
decade it falls adds `≈1.36 kcal/mol`. Nothing bounds NR4A1's reserve, so **the requirement is bounded
below by the table and is not bounded above at all.** Quoting the bottom-left of the table would be
picking the most favourable unmeasured pair and calling it the specification.

### 2.3 · Why the comparison with the degrader's number is invalid, in BOTH directions

The 0.50–3.49 kcal/mol range **brackets** the roadmap's degradation-window figure rather than sitting under
it, so even the arithmetic does not support "smaller". But the comparison is invalid before that, for
three independent reasons:

1. ⛔ **Different measurand.** The degrader's margin is applied to the **induced-interface / cooperativity**
   arm (D4) — a difference between two *ternary* complexes. `ΔΔG₁` is a difference between two **binary
   LBD** affinities. These are different physical quantities, produced by different instruments with
   different validation status, and only coincidentally carry the same units.
2. ⛔ **Different spread, from different parameters.** The degrader's range comes from sweeping `K_d`, `α`
   and `D_max` (D7) at a fixed `(A, B)`. This range comes from sweeping `(A, B)` with no other free
   parameters at all. **Two ranges built by varying disjoint things are not comparable ranges.**
3. ⛔ **Different amplification.** The degrader's number already contains D5 — one binding event commits a
   substrate, and the effect integrates against turnover. The occupancy requirement contains no such step,
   which is precisely why it is expressible in closed form. A modality that gets its effect *for free*
   from catalysis and a modality that must hold the receptor to have any effect at all cannot be graded on
   one axis.

### 2.4 · Sub-form (b), covalent occupier at C397 — not a ΔΔG at all

The categorical axis is **set membership**, not a free-energy contest, so its requirement is a *predicate*
and a *time* statement rather than a threshold in kcal/mol.

> **`REQ-MONO-3` — HARD, comparator NR4A1; SOFT, comparator NR4A2.**
> **Quantity:** the exposure-integrated labelled fraction of each paralogue over the dosing interval,
> `L_i(t) = 1 − exp(−k_inact,i · θ_i · t)` — the kinetic form, because A1 fails for a covalent arm.
> **Threshold:** `L_NR4A1 ≤ B₁` over the interval, at the dose at which `L_NR4A3 ≥ A`.
> **The predicate that makes it categorical:** `k_inact,NR4A1 = 0` requires that **no** paralogue
> nucleophile is engaged at the design's own arm length — not merely that none sits at the *aligned*
> position.

⚠ **Three things this requirement must be read with, all owned elsewhere and none re-derived here.**

- ⛔ **The categorical axis is narrower than "the paralogues have no cysteine".** The roadmap's
  MECHANISM-FIRST section owns the narrowing: 16 of NR4A3's 20 cysteines are shared, each paralogue
  presents two inside the design gate, and what holds the axis up is **exposure, not absence**. So
  `REQ-MONO-3`'s predicate must be evaluated **at the arm length the design actually uses**, against the
  matched-construct reach measurement whose one home is
  [`nr4a-paralogue-dynamics.json`](../../modalities/nr4a-paralogue-dynamics.json) →
  `categorical_verdict.by_scope[*].by_linker_atoms`.
- ⛔ **It must be read on REACH-ONLY.** The exposure cutoff `C7` is recorded **KNOWN-DEFECTIVE** — it fails
  its own positive control — so a predicate evaluated on reach-and-exposure inherits a defect, and only
  the reach-only column stands. This is a constraint on how the requirement is checked, not a claim about
  what it returns.
- ⚠ **The route's own computed reading of this predicate is unfavourable, and that is a result about the
  route rather than about the requirement.** The owner memo's §3 records that removing the E3 arm closes
  the family-wide window in every cell that had one on the conservative convention. **Nothing in this
  document changes that reading**, and stating a requirement the route's own measurement already misses is
  the specification working correctly.

⭐ **Why the covalent sub-form needs a TIME statement and the non-covalent one does not.** A reversible
occupier's selectivity is `exp(−ΔΔG/RT)` and is the same at every moment. A covalent one accumulates: the
same instantaneous selectivity, held for longer, converts into a larger labelled fraction on both arms.
So `REQ-MONO-3` is not satisfiable by a ratio at a timepoint, and a design that reports one has reported
the wrong quantity. This is `selectivity_margin_model`'s own distinction between `covalent_capture` (the
equilibrium proxy, a lower bound) and `covalent_capture_KINETIC`, carried across to a modality with no E3.

---

## 3 · `RT-TCIP` — transcriptional chemically-induced proximity

This route carries **three** requirements, and they are not the same kind of object. Only one of them can
be sized today, and it is not the one the route board would expect.

### 3.1 · `REQ-TCIP-1` — the induced-interface floor — CANNOT BE SIZED TODAY

**The problem, in its sharpest form.** The reach enumeration's interface floor `min_contact_residues = 12`
is a **degrader-derived** parameter — the search's own comment is *"below this it is a tethered pair, not
an interface"*, and a PROTAC needs a cooperative target·E3 interface. Ablating the floor **inverts the
sign** of the route's headline size comparison. The three numbers and the ablation table have their one
home in [`nr4a3-tcip-route-memo.md` §4(b)](../../modalities/nr4a3-tcip-route-memo.md) →
[`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json) and are not restated here.

> **`REQ-TCIP-1` — the requirement's FORM, which is all that can be stated.**
> The induced complex must persist, at the fusion's occupied chromatin sites, for at least as long as the
> recruited effector needs to act there, at the local concentration that induced proximity achieves.
> **The quantity is a residence time (or an association constant) at a locus. A contact-residue count is a
> PROXY for it, and the proxy's calibration constant is a property of the recruited partner's mechanism.**
> **Status: UNSIZED. The degrader's calibration constant may not be inherited, and no other is available.**

⛔ **AND THE SIGN OF THE DIFFERENCE IS UNKNOWN, NOT SMALLER.** Two arguments run in opposite directions and
this repository can adjudicate neither:

- **It could be smaller.** A recruited repressor may act by nucleation and local concentration rather than
  by a single geometrically-productive catalytic event, and the effector's own endogenous partners can
  supply avidity that the induced interface does not have to.
- **It could be larger.** A transcriptional outcome must persist over the timescale of transcription at a
  chromatin locus and compete with the effector's endogenous engagements, whereas a single ubiquitin
  transfer is fast and, once made, the substrate is committed. A degrader's complex may be allowed to be
  short-lived in a way a transcriptional one is not.

**So `REQ-TCIP-1` is exactly the state `BLK-UNSIZED-REQUIREMENT` describes, and this document does not
change it — it states it as an open question with a named input instead of leaving it unasked.**

> **`MISSING-3` (sets `REQ-TCIP-1`).** For **any** chemically-induced transcriptional-proximity system, a
> relationship between a **characterised** induced interface — its size, its cooperativity, or the induced
> complex's residence time — and transcriptional output. A dose–response alone does not serve: it sizes
> the *molecule*, not the *interface*, and the floor is a statement about the interface.

### ★ The $0 observation that was available the whole time, and what it returned

Per CLAUDE.md §4 — a $0 observation is never "watching". The route's motivating source
`EV-EB-TCIP-2025` (`10.1021/jacs.5c05634`, PMC12851799) has a CI-fetched full text **already committed**,
on the `literature-cache` branch at `literature/emc-post-degrader-options/tcip_ewsfli1_jacs_pmc.txt`. It
was read here rather than assumed about.

**What the main text contains, measured by reading it:** the ternary complex is characterised
**functionally** — a TR-FRET association, a dose-dependent pulldown, competition by each free ligand, a
reporter and transcript dose–response, and a hook effect. **What it does not contain:** across the whole
committed body, **`cooperativ*` occurs 0 times, `linker` 0 times, `contact residue` 0 times, and the only
occurrence of `interface` is inside a reference title** (a 1998 PNAS entry on redesigning an FKBP-ligand
interface). There is no structure of the induced complex, no cooperativity factor and no interface
characterisation of any kind.

⇒ ⛔ **`MISSING-3` is not merely un-fetched: the route's own motivating paper does not contain it.** That
is a stronger and more useful statement than "we have not looked", and it moves the missing input out of
the literature-reading category and toward a bench.

⚠ **Three limits travel with that reading and must not be dropped.**
1. ⛔ **The citation gate is OPEN.** `verify-refs` does not carry this DOI
   ([`nr4a3-tcip-route-memo.md` §6](../../modalities/nr4a3-tcip-route-memo.md) owns that finding), so
   **no number from this source enters any artifact, result or requirement threshold here.** What is used
   above is an **absence in a committed text file**, which is a statement about what input exists, not a
   measurement entering a result.
2. ⚠ **The cache holds the main text; the Supporting Information is a separate document and is not in it.**
   So this is a reading of the main body only, and an interface characterisation sitting in the SI would
   not have been seen. Stated rather than glossed, because an absent reading is not a reading of absence.
3. ⚠ **The demonstrated system recruits to an `FKBP^F36V`-tagged fusion** — a chemical-genetic handle that
   is not present in human cells and not present in the NR4A paralogues. **It therefore speaks to no
   paralogue-selectivity requirement at all**, which is why `REQ-TCIP-3` below is untouched by it.

### 3.2 · `REQ-TCIP-2` — the BRACKET requirement, which CAN be stated and is checkable today

Because the sign inverts across the floor, and because the floor is unsized, a statement made at one floor
is a statement about **the inherited parameter**, not about a TCIP.

> **`REQ-TCIP-2` — HARD, and it gates publication rather than a molecule.**
> **Quantity:** every geometric statement this route publishes, evaluated at **both** the ablated floor
> (`min_contact_residues = 0`, pure steric) and the committed degrader-derived floor.
> **Threshold:** the statement may assert **only what holds at both**. A statement true at one floor and
> false at the other is reported as **floor-dependent**, with the floor named, and is not asserted.
> **Instrument:** the ablation already run — `nr4a3-tcip-reach.json`, whose module refuses to pick a floor.
> **Status: SIZED, and checkable today at $0.** It is the one half of `REQ-TCIP` that this document gives
> a threshold to.

⭐ **This is a real requirement, not a formatting rule.** It converts an unsized parameter from a hidden
assumption into a declared bracket, and it is falsifiable: any TCIP claim in this repository can be
inspected against it and shown to meet or miss it. The TCIP memo already states the practice
(*"the TCIP number must be reported at both floors, never at the inherited one alone"*); what was missing
was the statement that this **is** the route's requirement while `REQ-TCIP-1` has no number.

### 3.3 · `REQ-TCIP-3` — the paralogue requirement on the binder

> **`REQ-TCIP-3` — HARD, comparator NR4A1; SOFT, comparator NR4A2.**
> **Quantity:** the same odds-product identity as `REQ-MONO-1`, but on the **induced-complex fraction**
> rather than binary occupancy — so the difference that must be supplied is the sum of the binder's binary
> `ΔΔG` and any induced-interface `ΔΔG`, exactly as for a degrader.
> **Threshold:** `RT·ln{ [A/(1−A)] · [(1−B)/B] }`, with `A` and `B` in induced-complex-fraction space.
> **Status:** UNSIZED, and blocked by **`MISSING-3`** *in addition to* `MISSING-1`/`MISSING-2` — because
> whether `A` may be small depends on whether the effector amplifies (D5), which is `MISSING-3` again.
> **⚠ And the dose axis is bounded above:** by D3 the response is non-monotone, so the requirement is a
> statement about a dose **range**, and a molecule can miss it by being *too* concentrated.

⛔ **AND THE ANTI-TARGET EVENT IS A DIFFERENT EVENT, WHICH IS A RELOCATION AND NOT A REDUCTION.** A
degrader engaging NR4A1 removes NR4A1. A TCIP engaging NR4A1 **rewires** it — recruiting a transcriptional
effector to a receptor whose bound is a combination genotype about *loss*. **The severity of that event is
not bounded by the loss-of-function genotype at all**, so `B₁` for this route is not even the same `B₁`
as for `RT-MONOVALENT`, and `MISSING-2` does not serve it. This is the identical failure shape the owner
memo's §4 warns about for occupancy, one modality further out, and it means the honest reading of
`REQ-TCIP-3` is that its anti-target ceiling has **no candidate source at all**.

---

## 4 · `RT-ASYMMETRIC` — the requirement is a PAIR, and a scalar is a defect in a stated direction

This route *is* a statement about the requirement's shape, so its sizing statement is about **form**, and
that form is checkable without any of the missing inputs.

### 4.1 · `REQ-ASYM-1` — the specification is a pair, never a scalar

> **`REQ-ASYM-1` — HARD, and it applies to every selectivity requirement in the repository.**
> Any stated selectivity requirement is an ordered pair `(t₁, t₂)` — a **gating threshold** against NR4A1
> and a **reported, non-gating** quantity against NR4A2 — never one number with two comparators.
> **Checkable today:** a requirement written as *"selective over NR4A1/NR4A2"* misses it by construction.
> **Basis:** [roadmap §2.4](../nr4a3-program-map.md#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically),
> which owns the evidence for each half and is not restated here.

### 4.2 · `REQ-ASYM-2` — the two halves take different KINDS of bound, so they take different kinds of number

| half | kind of bound | what the specification looks like |
|---|---|---|
| **NR4A1 — HARD** | a **combination** genotype that a non-selective molecule reconstitutes | a **gate**: a threshold that a design must clear, and a design that misses it is rejected |
| **NR4A2 — SOFT** | **complete developmental** loss of a single gene | a **disclosed residual**: a quantity that is reported with every result and gates nothing |

⛔ **Neither kind of bound converts into a tolerated fraction.** Both are genotypes; a genotype bounds
developmental, complete, lifelong loss, and every requirement in this file needs an **adult, partial,
transient** ceiling. That conversion has no basis anywhere in this repository, and
[§4.3](#43--req-asym-3--the-defect-a-scalar-creates-stated-so-it-can-be-checked) names what it would take.

### 4.3 · `REQ-ASYM-3` — the defect a scalar creates, stated so it can be checked

For any single number `t` proposed as the symmetric requirement, and writing `t₁` for what the NR4A1 half
would need and `t₂` for what the NR4A2 half is worth:

- if `t < t₁` the specification **admits a design that misses the hard constraint** — the failure in the
  direction the program can least afford;
- if `t > t₂` it **rejects designs on the half that was never a gate** — a real cost in design freedom on
  the axis where the roadmap records the program has fewer discriminating handles.

**One of the two always holds unless `t₁ = t₂`, and nothing in this repository states that they are
equal.** So a scalar is not an approximation of the pair — it is an error whose *direction* is determined
by which side of `t₁` it falls on, and that is checkable the moment either half acquires a number.

> **`MISSING-4` (sets `B₂`, and with `MISSING-2` sets `B₁`).** A dose–response relating **partial, adult,
> transient** loss of NR4A1 (resp. NR4A2) function to a phenotype. ⛔ For NR4A2 the repository's own record
> is explicit that adult transient loss is **unbounded by any source read**, and the caveat that a germline
> knockout does not speak to that regime is carried in the artifact itself
> ([`nr4a2-sparing-bound.json`](../../modalities/nr4a2-sparing-bound.json) →
> `caveat_that_must_travel_with_any_result`). ⛔ **An absent bound means the liability could be larger, not
> smaller** — the roadmap's standing warning, and it applies to every unfilled `B` in this file.

---

## 5 · The requirement register, in one checkable table

Every row states a quantity, a comparator, a threshold or an explicit absence, and the claim ceiling that
[roadmap §2.3](../nr4a3-program-map.md#23--the-claim-ceiling-rule-stated-so-it-can-be-checked) puts on any
future result against it.

| id | route | comparator | quantity | threshold | blocked by | claim ceiling on any result |
|---|---|---|---|---|---|---|
| `REQ-MONO-1` | `RT-MONOVALENT` | NR4A1 — **HARD** | binary LBD `ΔΔG` | `RT·ln{[A/(1−A)]·[(1−B₁)/B₁]}` · **0.50–3.49 kcal/mol** over the plausible `(A, B₁)` rectangle, not bounded above | `MISSING-1`, `MISSING-2` | unvalidated prediction |
| `REQ-MONO-2` | `RT-MONOVALENT` | NR4A2 — **SOFT** | binary LBD `ΔΔG` | reported, not gated | `MISSING-1`, `MISSING-4` | unvalidated prediction |
| `REQ-MONO-3` | `RT-MONOVALENT` | NR4A1 HARD / NR4A2 SOFT | exposure-integrated labelled fraction | `L_paralogue ≤ B` over the dosing interval, evaluated **reach-only** at the design's own arm length | `MISSING-2`, and the `C7` defect for the exposure convention | unvalidated prediction |
| `REQ-TCIP-1` | `RT-TCIP` | — | induced-complex residence time at a locus (a contact count is its proxy) | ⛔ **none — UNSIZED, sign unknown** | `MISSING-3` | n/a — nothing may be asserted against it |
| `REQ-TCIP-2` | `RT-TCIP` | — | every geometric statement, at both floors | assert only what holds at **both**; otherwise report as floor-dependent | ✅ **nothing — checkable today at $0** | it is a reporting gate, not a scientific claim |
| `REQ-TCIP-3` | `RT-TCIP` | NR4A1 HARD / NR4A2 SOFT | induced-complex-fraction `ΔΔG`, over a bounded dose range | same identity, in induced-complex-fraction space | `MISSING-3`, plus **no candidate source at all** for its `B₁` ([§3.3](#33--req-tcip-3--the-paralogue-requirement-on-the-binder)) | unvalidated prediction |
| `REQ-ASYM-1` | `RT-ASYMMETRIC` | both | the specification's SHAPE | an ordered pair, never a scalar | ✅ **nothing — checkable today at $0** | a definitional decision, not a result |
| `REQ-ASYM-2` | `RT-ASYMMETRIC` | both | the KIND of each half's bound | gate for NR4A1, disclosed residual for NR4A2 | ✅ **nothing** | a definitional decision |
| `REQ-ASYM-3` | `RT-ASYMMETRIC` | both | the error a scalar introduces | one of two named directions always holds unless `t₁ = t₂` | `MISSING-2`, `MISSING-4` to instantiate | a definitional decision |

**Three of nine rows are checkable today at $0, and none of the three is a selectivity result.** The six
that would speak about a molecule are all ceilinged at *unvalidated prediction* by
[roadmap §2.3](../nr4a3-program-map.md#23--the-claim-ceiling-rule-stated-so-it-can-be-checked), and that
ceiling does not move because a threshold now exists to compare against.

---

## 6 · Graph edits — DESCRIBED, NOT APPLIED

`systems/graph/` and `systems/views/` are off limits to this lane. The exact JSON is given so a lane that
owns them can apply it without re-deriving anything.

### ⭐ The recommendation, and the reasoning behind it

**PARTIALLY RETIRE AND SPLIT — do not retire outright, do not leave as-is.** Three findings force it:

1. ✅ **The specification-absence half IS retired.** `retired_by_action` asked for the requirement to be
   stated with its basis, for each held route. That now exists: nine requirement rows, each with a
   quantity, a comparator, an asymmetry-correct pair form, and either a threshold or an explicit "cannot
   be sized" with a named input.
2. ⛔ **A real residual remains, and it is a DIFFERENT KIND of blocker.** The inputs `A`, `B₁`, `B₂` are
   dose–responses that only a bench produces (`MISSING-1`, `MISSING-2`, `MISSING-4`) — Group D on the
   taxonomy's ladder, not Group A. Leaving them filed as `scientific_uncertainty` files a bench problem as
   an open question, which is exactly the conflation
   [`systems/taxonomy/blockers.md`](../../../systems/taxonomy/blockers.md) §1 forbids.
3. ⛔ **`MISSING-3` has a different remedy from the other three, so per the taxonomy's own instruction
   (*"a blocker that resists this ladder is usually two blockers — split it"*) it becomes its own.** It is
   held by **one** route, its retirement is a field-level result rather than an EMC bench, and — per the
   `$0` reading in [§3.1](#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today) — the
   candidate literature source does not contain it.

⚠ **Two things a reviewer should check before applying:** `kind` changes require `kind_history` (schema),
and `blocker.schema.json` sets `additionalProperties: false` — the blocks below use only permitted
properties, and `permanent`, `inherited_by`, `retired_by` and `retired_by_technology` are DERIVED and are
deliberately absent.

### (a) `systems/graph/blockers.json` — RESTATE `BLK-UNSIZED-REQUIREMENT`

Replace the existing object with:

```json
{
  "id": "BLK-UNSIZED-REQUIREMENT",
  "name": "The selectivity requirement is now STATED for all three routes, and three of its inputs are unmeasured dose-responses that only a bench produces",
  "statement_about": "an unmeasured input to a specification that now exists — no longer an absent specification",
  "owner": {
    "file": "research/manuscripts/degrader/selectivity-requirement-sizing.md",
    "anchor": "#5--the-requirement-register-in-one-checkable-table"
  },
  "kind": "requires_wet_lab",
  "kind_history": [
    {
      "was": "scientific_uncertainty",
      "changed_on": "2026-08-07",
      "why": "The absent-specification half is retired: selectivity-requirement-sizing.md states the requirement for RT-MONOVALENT, RT-TCIP and RT-ASYMMETRIC as nine rows with quantity, comparator and asymmetry-correct pair form. What remains is not an open question but three unmeasured dose-responses — occupancy to fusion LBD-borne output (A), and occupancy to phenotype for NR4A1 and for NR4A2 (B1, B2) — which set the thresholds. Per taxonomy ladder step 3 a physical experiment answers those, so the kind is Group D. Filing a bench input as scientific_uncertainty files it as researchable, which is the conflation the taxonomy forbids. The TCIP interface floor was split out to BLK-TCIP-INTERFACE-FLOOR because its remedy differs."
    }
  ],
  "retired_by_action": "Obtain the three dose-responses named as MISSING-1, MISSING-2 and MISSING-4 in selectivity-requirement-sizing.md. Until then the thresholds stay as stated forms with an explicit range and no upper bound. ⛔ NOT retired by any computation: a genotype bounds developmental, complete, lifelong loss and cannot be inverted into an adult tolerated occupancy, and no in-silico instrument produces an occupancy-to-output transfer function.",
  "evidence": [
    "research/manuscripts/degrader/selectivity-requirement-sizing.md#22--what-cannot-be-sized-for-this-route-and-the-named-missing-inputs",
    "research/manuscripts/degrader/selectivity-requirement-sizing.md#43--req-asym-3--the-defect-a-scalar-creates-stated-so-it-can-be-checked",
    "research/modalities/nr4a2-sparing-bound.json"
  ]
}
```

### (b) `systems/graph/blockers.json` — ADD `BLK-TCIP-INTERFACE-FLOOR`

Append:

```json
{
  "id": "BLK-TCIP-INTERFACE-FLOOR",
  "name": "How much induced interface a transcriptional CIP needs is unsized, and the degrader-derived floor it inherits inverts the route's headline result when ablated",
  "statement_about": "a parameter inherited from a different modality, whose calibration constant is a property of the recruited partner's mechanism",
  "owner": {
    "file": "research/manuscripts/degrader/selectivity-requirement-sizing.md",
    "anchor": "#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today"
  },
  "kind": "insufficient_data",
  "retired_by_action": "Find, for ANY chemically-induced transcriptional-proximity system, a relationship between a CHARACTERISED induced interface (size, cooperativity, or induced-complex residence time) and transcriptional output — MISSING-3. ⛔ Measured 2026-08-07 at $0 by reading the committed full text of the route's own motivating source on the literature-cache branch: `cooperativ*` 0 occurrences, `linker` 0, `contact residue` 0, `interface` only inside a reference title, and no structure of the induced complex. That source characterises the ternary complex functionally and not structurally, so it does not supply the input. Supporting Information was not in the cache and is the one place left to look before this escalates to requires_wet_lab. Until then REQ-TCIP-2 (report at both floors, assert only what holds at both) is the route's operative requirement.",
  "evidence": [
    "research/modalities/nr4a3-tcip-route-memo.md#4---the-finding-the-size-penalty-is-a-degraders-interface-floor-not-steric-bulk",
    "research/modalities/nr4a3-tcip-reach.json",
    "research/manuscripts/degrader/selectivity-requirement-sizing.md#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today"
  ]
}
```

⚠ **The `$0` reading above is recorded under an OPEN citation gate.** `verify-refs` does not carry
`10.1021/jacs.5c05634`, so this text supplies **no number** to any artifact — it records only that a named
input is absent from a committed file, which is a statement about availability and not a measurement.

### (c) `systems/graph/routes.json` — `RT-TCIP`

```json
"blockers_inherited": [
  "BLK-INDUCED-COMPLEX",
  "BLK-NO-WET-LAB",
  "BLK-PARALOGUE-DDG",
  "BLK-R4-BINDS",
  "BLK-TCIP-INTERFACE-FLOOR",
  "BLK-UNSIZED-REQUIREMENT"
]
```

and replace the second and third `remaining_unknowns` entries with:

```json
"Which interface floor a transcriptional CIP actually requires. The committed floor (min_contact_residues=12) is a DEGRADER'S parameter, the result inverts across it, and the requirement is now STATED as a residence-time requirement whose calibration constant is unavailable (BLK-TCIP-INTERFACE-FLOOR; REQ-TCIP-1). Operative requirement meanwhile: report at both floors and assert only what holds at both (REQ-TCIP-2).",
"Whether the paralogue selectivity requirement is any smaller here. ⛔ It is now SIZED IN FORM and it is not smaller: REQ-TCIP-3 needs the same odds-product difference in induced-complex-fraction space, over a dose range bounded above by the hook, and its anti-target ceiling has NO candidate source at all — a TCIP engaging NR4A1 rewires it rather than removing it, so the loss-of-function genotype that bounds the degrader's anti-target event does not bound this one."
```

### (d) `systems/graph/routes.json` — `RT-MONOVALENT`

Replace the second `remaining_unknowns` entry and the `required_validation` row:

```json
"How much paralogue selectivity this route would need. ⭐ STATED 2026-08-07 (REQ-MONO-1/2/3, selectivity-requirement-sizing.md): a binary LBD ΔΔG against NR4A1 as a HARD gate and against NR4A2 as a disclosed residual, at RT·ln{[A/(1−A)]·[(1−B)/B]} — 0.50–3.49 kcal/mol over the plausible (A,B) rectangle and NOT bounded above, because the anti-target ceiling is unmeasured. ⛔ That range BRACKETS the degrader's figure rather than sitting under it, and the two are not comparable in any case; the covalent sub-form's requirement is a kinetic predicate rather than a ΔΔG at all."
```

```json
{
  "what": "A stated selectivity requirement this route would have to meet — ✅ DONE 2026-08-07, $0, research/manuscripts/degrader/selectivity-requirement-sizing.md §2. Stated as a pair (NR4A1 hard / NR4A2 soft) with the derivation and every assumption named. Its thresholds are forms with a range, not numbers, because the transfer functions that set A and B are unmeasured (MISSING-1, MISSING-2).",
  "feasible_today": true,
  "blocked_by": []
}
```

and in `readiness.missing`, replace `"a sized selectivity requirement"` with
`"the occupancy-to-output transfer functions that would turn the stated requirement into a number (MISSING-1, MISSING-2)"`.

⚠ **`next.best_next_action` and `timing.rationale` both currently say the requirement is what to write
next.** They should move on — the specification is written — but **what replaces them is a judgement about
this route's ordering that this lane does not own**, so no replacement text is proposed. Flagging it is
the edit.

### (e) `systems/graph/routes.json` — `RT-ASYMMETRIC`

Append to `remaining_unknowns`:

```json
"Whether the asymmetry has been given a CHECKABLE form rather than only a stated one. ⭐ Partly, 2026-08-07: REQ-ASYM-1/2/3 (selectivity-requirement-sizing.md §4) state that the specification is an ordered pair, that its two halves take different KINDS of bound, and that any scalar t errs in one of two named directions unless t1 = t2 — which is checkable the moment either half acquires a number. ⛔ Neither half has one: both bounds are genotypes, and a genotype bounds developmental, complete, lifelong loss and cannot be inverted into an adult tolerated occupancy (MISSING-2, MISSING-4)."
```

⚠ **The `next.best_next_action` already names the right next step (a narrow checker for retired symmetric
phrasings), and `REQ-ASYM-1` gives that checker its acceptance criterion.** No change proposed to it.

### (f) `systems/graph/publications.json` — a note, not an edit

This file is not claimed by any endpoint's `document.file`, and it should probably stay that way: it is a
specification the routes' own papers cite, not a paper. **But that means `lint_claims.py` does not pick it
up by default** — its publication-register glob only reaches documents an endpoint points at. It was run
explicitly against this file instead; a lane that wants standing coverage should add the path to
`DEFAULT_TARGETS` rather than invent an endpoint for it.

---

## 7 · Limits of this document

- ⛔ **No molecule is asserted to meet, approach or miss any requirement above.** No molecule exists in any
  of these three routes.
- ⛔ **No efficacy, potency, safety, dosing, tolerability or clinical-readiness statement is made or
  implied**, and none follows from anything above. `A` and `B` are specification parameters, not doses.
- ⛔ **Nothing here raises any selectivity claim.** Every paralogue-selectivity statement in this
  repository remains an unvalidated prediction, for the reason in
  [§0](#-0--read-this-before-anything-else-what-a-sized-requirement-is-and-what-it-is-not) item 2.
- ⚠ **The odds-product identity is algebra over an equilibrium model, not a measurement.** It inherits
  every assumption in [§1.3](#13--the-assumptions-the-identity-carries-each-named-so-it-can-be-attacked),
  and A1 is known to fail for the covalent sub-form, which is why that sub-form gets a kinetic predicate
  instead.
- ⚠ **The 0.50–3.49 kcal/mol range is a range over a SPECIFICATION rectangle, not over the biology.** It
  says what the requirement would be for each `(A, B)` pair; it does not say which pair is right, and
  nothing in this repository does.
- ⚠ **The `$0` literature reading in [§3.1](#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today)
  is of a main text only, under an open `verify-refs` gate**, and supplies no number to anything.
- ⚠ **This document does not re-rank the portfolio and owns no route grade.**
  [`emc-treatment-strategy.md`](../program/emc-treatment-strategy.md) and
  [`nr4a3-program-map.md`](../nr4a3-program-map.md) own those; where either differs, it wins.

---

## Sources

*Every figure this document depends on is read from the file that owns it. Nothing is re-derived and no
citation was generated here.*

| what | where it lives |
|---|---|
| the degradation-window margin, the resolvable difference and the measured accuracy against it | [roadmap MECHANISM-FIRST](../nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged) — **not re-typed here** |
| the derivation those figures come from, component by component ([§1.1](#11--the-degraders-number-decomposed-into-parts-that-can-be-checked-one-at-a-time)) | [`selectivity_margin_model.py`](../../modalities/selectivity_margin_model.py); the 1:1:1 solver it reuses is `andgate_degradation_model.ternary` |
| the NR4A1-hard / NR4A2-soft asymmetry, and the evidence under each half | [roadmap §2.4](../nr4a3-program-map.md#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically) → [`nr4a2-sparing-bound.json`](../../modalities/nr4a2-sparing-bound.json), [`nr4a1-sparing-axis.json`](../../modalities/nr4a1-sparing-axis.json) |
| the claim-ceiling rule and every instrument's verdict | [roadmap §2.3](../nr4a3-program-map.md#23--the-claim-ceiling-rule-stated-so-it-can-be-checked), [roadmap §3.1](../nr4a3-program-map.md#31--the-instrument-table) |
| the monovalent route, its two sub-forms, and the E3-arm-free reach result | [`nr4a3-monovalent-pocket-route.md`](../occupancy/nr4a3-monovalent-pocket-route.md) → [`nr4a3-monovalent-reach.json`](../../modalities/nr4a3-monovalent-reach.json) |
| the categorical axis's narrowing to exposure, and the matched-construct reach numbers | [roadmap MECHANISM-FIRST](../nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged) → [`nr4a-paralogue-dynamics.json`](../../modalities/nr4a-paralogue-dynamics.json) |
| the TCIP interface-floor ablation and its three ratios | [`nr4a3-tcip-route-memo.md` §4](../../modalities/nr4a3-tcip-route-memo.md) → [`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json) |
| the open `verify-refs` gate on `10.1021/jacs.5c05634`, and the cached full text | [`nr4a3-tcip-route-memo.md` §6](../../modalities/nr4a3-tcip-route-memo.md); `literature-cache` branch, `literature/emc-post-degrader-options/tcip_ewsfli1_jacs_pmc.txt` |
| the blocker taxonomy, its kind ladder and the split-a-compound-blocker rule | [`systems/taxonomy/blockers.md`](../../../systems/taxonomy/blockers.md) |

---

*Medical-integrity note: no clinical fact, statistic, citation or patient datum in this document is
fabricated. Every quantitative statement is either read from a named committed artifact, pointed at the
file that owns it, or produced by the algebra written out in
[§1.2](#12--what-does-transfer-the-window-identity-in-closed-form), which any reader can recompute.
Nothing here asserts activity in EMC, tolerability in a patient, or clinical applicability, and nothing
here asserts that any molecule meets any requirement it states.*
