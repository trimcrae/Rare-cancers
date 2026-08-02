# Instruments that could carry a selectivity claim — the option queue

> **$0. No GPU, no rental, no dispatch.** Every figure here is read out of a committed artifact named beside
> it, or is an argument. Nothing here is a result about binding, reactivity, degradation, efficacy or safety.
>
> **★ ONE FACT, ONE PLACE.** This document is a *reader* for
> [`instrument-options.json`](./instrument-options.json), which carries the machine form of every ranking and
> every pointer. **The JSON is the home; this file carries the reasoning.** The one thing that lives *here* and
> not there is §2 — the double-difference analysis in full prose.
>
> **This file edits nothing it does not own.** [`nr4a3-program-map.md`](../manuscripts/nr4a3-program-map.md),
> `nr4a3_linker_design.py`, the linker library and `nr4a3-inverse-linker-design-2026-07-25.md` are held by other
> agents. Edits they need are specified verbatim in the JSON's `proposed_roadmap_edits` and summarised in §5.
>
> **⚠ NO KNOWN-ANSWER VALUE IS INVENTED.** Every candidate's known-answer test is in one of three states —
> `available` (a real system with a measured value already committed here, artifact named), `candidate_unverified`
> (a source *class* that plausibly holds one, settled by a named $0 precheck, **never cited before it runs**), or
> `none`. A `candidate_unverified` row is not evidence that a benchmark exists.

---

## 0 · The problem, stated as an instrument problem

The roadmap's [§3.2](../manuscripts/nr4a3-program-map.md#32--the-rv-coverage-matrix--where-the-holes-are) reads:
**5 requirements with no instrument, 5 more whose instrument has returned no usable answer, and 0 requirements
standing on an instrument validated in the regime the claim needs.**

That last clause is the whole thing. Three instruments *have* passed known-answer tests and none of them is in
the regime:

| | passed at | why it is not in the regime |
|---|---|---|
| `V6` | 0.61 kcal/mol, TYK2 `ejm_31→ejm_42` | relative FEP **within one pocket**, one charge model. One difference, not two; one protein, not two |
| `V10` | barnase–barstar Y29A, hot-spot scale | validated for seeing a **large** effect and for not inventing one where none exists. Its qualified set *brackets* the wedge and covers nothing at paralogue size |
| `V4` | — (no result, not authorized) | the right **question** in the wrong **currency**: an *absolute* ABFE difference, on an engine whose own absolute control `V7` misses by more than the entire margin |

So there are exactly two productive moves, and this queue contains both:

1. **Make the regime irrelevant** — instruments whose readout is categorical, geometric or populational, so no
   free-energy resolution is needed at all. The covalent axis and the unique-lysine axis already work this way.
   Candidates **C02–C13** extend that.
2. **Close the regime** — build the free-energy quantity that is *best conditioned* for a between-protein
   comparison, and buy it a known answer at that size. Candidates **C01** and **C14**.

---

## 1 · The queue, ranked

Full fields — what each measures, what it licenses, what it explicitly does not, its known-answer state, and its
cost — are in [`instrument-options.json`](./instrument-options.json) `candidates[]`. The short form:

| # | id | candidate | regime-immune? | known answer | cost | grade |
|---:|---|---|:--:|---|---|:--:|
| 1 | **C01** | **Ligand-side selectivity RBFE (ΔΔΔG) + its own paralogue-scale benchmark** | no — it *closes* the gap | ⚠ candidate; settled by two **$0** searches (C01a, C01b) | $0 to search · one edge-pair to run | **A+** |
| 2 | **C02** | **Decoy null for the CATEGORICAL axis** — unrelated paralogue pairs through the identical pipeline | ✅ | ✅ the null *is* the control (the move that refuted `V20`) | **$0** | **A** |
| 3 | **C03** | **Public chemoproteomics as the covalent axis's known-answer set** + a ligandability instrument | ✅ | ⚠ candidate; **$0** precheck | **$0** | **A** |
| 4 | **C04** | **Paralogue-matched cryptic-pocket druggability** — the harmonized detector on ensembles already on disk | ✅ | ✅ in-repo (the 8XTT experimental row) | **$0** | **A−** |
| 5 | **C05** | **`V18` known-answer precheck** — does a measured ubiquitination-site / lysine-mutant reference exist? | ✅ | ⚠ candidate; **$0** precheck | **$0** | **A−** |
| 6 | **C06** | **Point `V1` at rung `5b-T`'s rebuilt ternaries** | ✅ | ✅ **already passed** (Gln98→VHL Arg12, 2.88 Å) | **$0** | **A−** |
| 7 | **C07** | **Full-length / fusion-context unique-residue census** — the first instrument `R13` would have | ✅ | n/a — a read, not an inference | **$0** | **B+** |
| 8 | **C08** | **Complete `R14`** — the AR/MR check is 8/9 built and missing one target | ✅ | ✅ cognate-ligand self-control, never run | $0–cheap | **B+** |
| 9 | **C09** | **`R3`'s frame-level submission gate** — `V13`'s detector re-read per frame | ✅ | ✅ in-repo | **$0** | **B+** |
| 10 | **C10** | **Symmetric reciprocal-uniqueness + indel census**, all residue classes | ✅ | n/a — a read | **$0** | **B** |
| 11 | **C11** | **Steric-exclusion (volume) screen** at the divergent handles | ✅ (only at large size differences) | ⚠ candidate; **$0** precheck | **$0** | **B** |
| 12 | **C12** | **Thiol pKa / intrinsic nucleophilicity** for C397 | ✅ | ⚠ candidate; **$0** precheck | $0–cheap | **B** |
| 13 | **C13** | **Expression-context axis** — bounds the *consequence*, not the selectivity | ✅ | ✅ cross-dataset concordance | **$0** | **B−** |
| 14 | **C14** | **`barnase_barstar_W35F`** — the protein-side wedge benchmark for `V10` | no — it *closes* the gap | ✅ **available**, 1 of 7,085 SKEMPI rows, CI-verified to stage | priced, small | **B+** |
| 15 | **C15** | **Co-fold affinity head as a binary CLASSIFIER**, never a ranker | ✅ | ⚠ candidate; leakage hazard | cheap GPU | **C+** |
| 16 | **C16** | **ML-potential correction on the alchemical endpoints** | no | ✅ in kind | unpriced | **C** |

**Best identifiable option: C01**, and the reason is §2. **Best $0 option regardless of C01's outcome: C02.**
And **C04 and C09 are the same run** — the same detector over frames already committed — so whoever takes one
should take both.

---

## 2 · THE DOUBLE-DIFFERENCE ANALYSIS

*This section is the one thing that lives here rather than in the JSON, and it is the most consequential
technical question in the program. It has never been written down.*

### The question

`V6` passed a known-answer test at **0.61 kcal/mol** absolute error — but *within one pocket*. A ligand-side
double difference across two paralogues is built from the same machinery, and its binary and solvent legs
cancel exactly. **Does the cancellation make a between-protein comparison inherit `V6`'s validation?**

### The answer, in one line

**No.** The cancellation removes exactly the error classes `V6` also removes, and leaves standing exactly the
classes `V6` never measured. **But it buys three things worth more than the inheritance would have been:** a far
better-conditioned quantity than the ABFE difference `R7` currently rests on; first-order independence from
`R6`, the opening penalty nobody has computed; and a known-answer test that is *cheap and well-posed* instead of
expensive and unauthorized.

### 2.1 · The construction, and what cancels exactly

For a matched ligand pair `d₀ → d` and a protein `P`:

```
ΔΔG_bind(d₀→d | P)  =  ΔG_cplx,P(d₀→d)  −  ΔG_solv(d₀→d)
```

The between-protein double difference is

```
ΔΔΔG  ≡  ΔΔG_bind(d₀→d | NR4A3)  −  ΔΔG_bind(d₀→d | NR4A1)
      =  ΔG_cplx,3(d₀→d)  −  ΔG_cplx,1(d₀→d)
```

The solvent leg is **the same leg** — the same two molecules, the same water box, the same λ schedule — so it
drops out of the expression *before any number is computed*. In this repo's own vocabulary
([`valb_failure_propagation.error_algebra`](./valb_failure_propagation.py)) that is **ALGEBRAIC** cancellation
as opposed to **NUMERICAL**: exact, no residual, no added noise. The 5a-KS lane already depends on it — its
reducer **refuses** a binary leg rather than warning, for precisely this reason.

⚠ **One precondition has to be *enforced*, not assumed:** the same atom map, the same partial charges and the
same λ schedule on both arms. Otherwise the ligand and mapping error terms stop cancelling too. This repo
already knows how to enforce and *verify* that — `nr4a3_rbfe.strip_foreign_partial_charges`,
`assert_charge_consistency`, and the stored-`System` forensic in
[`charge-provenance-forensic.json`](./charge-provenance-forensic.json) that read identical alchemical charges
across arms rather than trusting a configuration line.

### 2.2 · The error decomposition — the whole answer is here

Write each computed leg as truth plus error, and split the error by **where it lives**:

```
ε_cplx,P  =  ε_lig  +  ε_map  +  ε_int,P  +  ε_samp,P  +  ε_prep,P
```

| term | what it is |
|---|---|
| `ε_lig` | ligand intramolecular force field + partial charges |
| `ε_map` | atom mapping, soft core, λ schedule |
| `ε_int,P` | ligand↔protein interaction terms, **in pocket P** |
| `ε_samp,P` | finite-sampling / convergence, **in pocket P** |
| `ε_prep,P` | starting conformer, protonation, restraints, box and finite size |

**What `V6` measured.** Its quantity is `ΔG_cplx,TYK2 − ΔG_solv`, so

```
err(V6)  =  ε_int,TYK2  +  (ε_samp,TYK2 − ε_samp,solv)  +  (ε_prep,TYK2 − ε_prep,solv)
```

with `ε_lig` and `ε_map` cancelling. **0.61 kcal/mol bounds *that* combination** — one edge, one protein, one
charge model, and crucially **protein-versus-WATER**. *(The 0.61 and its scope have one home: roadmap §3.1 row
`V6`, and RUNG 1 in the ordered plan.)*

**What the double difference's error is.**

```
err(ΔΔΔG)  =  (ε_int,3 − ε_int,1)  +  (ε_samp,3 − ε_samp,1)  +  (ε_prep,3 − ε_prep,1)
```

again with `ε_lig` and `ε_map` cancelling. This is **protein-versus-PROTEIN**.

**⇒ The two are different linear combinations of *disjoint* error terms. Not one term of `err(ΔΔΔG)` appears
anywhere in `err(V6)`.** Knowing `|ε_A − ε_B|` for one pair bounds nothing about `|ε_C − ε_D|` for a disjoint
pair. The only premise that would transfer it is *"the complex-leg error is a constant, protein-independent
offset"* — and that premise is:

1. **exactly the assumption a selectivity calculation exists to test**, so assuming it begs the question;
2. **inconsistent with how RBFE accuracy is actually reported** — as a distribution over systems, not a single
   offset. A published mean accuracy is a mean *over targets*; it is not a guarantee for any one of them, and a
   double difference is sensitive to precisely the target-to-target spread that the mean averages away;
3. **refuted locally, by this program's own data** — next.

### 2.3 · And the residual is not small *here* — three in-repo measurements

**(a) Within-lane leg reproducibility is already at the size of the effect.** The congeneric map's
`cycle_3carbonyl` triangle closes at **R = +1.307**, a tolerance violation, and an independent recomputation of
a single edge disagrees with the fan-out by **≈0.78 kcal/mol** — more than either stated uncertainty
(+1.84 ± 0.36 against +1.064 ± 0.118). Both are **within one protein**, so they are a *floor* on the per-leg
error, not a bound on the between-protein residual. A double difference is a difference of two such legs: if the
arms' errors are uncorrelated the residual is `~√2 ×` the leg error, and **nothing in this repo measures that
correlation.** *(Home: roadmap §9, paper §2.9.)*

**(b) A concrete non-cancelling `ε_prep` has already occurred, on the double-difference lane itself.** 5a-KS's
reducer flags `n_particles` disagreeing across arms — NR4A1 ≈ 210k vs NR4A3 ≈ 148k, the solvated **box** rather
than the composition — so a size-dependent systematic **survives the subtraction**. The roadmap's own words:
*"size-dependent systematics do not cancel, which is the one thing a double difference is supposed to buy."*
*(Home: roadmap §RUNG 5a-KS LANDED, "Three limits"; the reduction itself is
[`nr4a3-5aks-reduction.json`](./nr4a3-5aks-reduction.json).)*

**(c) The pockets differ exactly where the residual lives.** 7 of the 10 Pocket-5 lining residues are
paralogue-divergent ([`nr4a-selectivity.json`](./nr4a-selectivity.json), `n_residues: 10`, `n_divergent: 7`).
`(ε_int,3 − ε_int,1)` **is** the force field's error on those seven differences; `(ε_samp,3 − ε_samp,1)` **is**
the difference in how well two *different* cryptic pockets are equilibrated — in a program where the opening
mechanism failed its own Gate-1 registration and Gate 3B is unresolved.

> **★ The structural point behind all three.** A double difference isolates the signal by cancelling everything
> the two proteins share — **and it isolates the error the same way.** Signal and residual live in the same
> place. The cancellation shrinks both, which is why it cannot be read as a free improvement in
> signal-to-noise, and why a within-pocket pass says nothing about it.

### 2.4 · What the cancellation *does* buy

**DD-1 · It is far better conditioned than the quantity `R7` currently rests on.**
`R7`'s margin is a difference of two **absolute** ABFEs. The absolute engine's own known-answer test `V7` misses
by ≈ +7.1 kcal/mol — larger than the entire margin it is used to compute — and `V9` holds every leg of that
block provisional on a soft-core-tail λ-overlap failure. *(Both have one home: roadmap §3.1 rows `V7` and
`V9`.)* `ΔΔΔG` **never forms an absolute number at all**: no
restraint free energy, no standard-state term, no absolute decoupling. Every error class that killed `V7` is
absent **by construction**, not by assumption.

**DD-2 · ⭑ `R6` — the per-paralogue opening penalty — drops out to FIRST ORDER, and I can find this stated
nowhere in the program.**
Validation requirement 2 warns that matched-open comparison *"can miss or REVERSE selectivity"*. That warning
bites on an **absolute** per-paralogue affinity, where `ΔG_bind,obs ≈ ΔG_open + ΔG_bind|open` and the two
paralogues' opening penalties differ. In a **relative** quantity the opening penalty is common to both ligands
of the matched pair and **cancels inside each protein**, before the between-protein subtraction is ever taken —
so `ΔΔΔG` is doubly free of it.

- **Condition, stated rather than assumed:** it cancels to the extent that `d` and `d₀` select the *same* open
  sub-state. For a matched pair differing by one small element — exactly what the causal design specifies — that
  is a good approximation. For two dissimilar molecules it is not, and the residual is the difference in the
  opening each ligand demands.
- **What it licenses:** a **causal / design** claim — *"this structural element contributes X kcal/mol more in
  NR4A3 than in NR4A1, with both receptors in their modelled open states"* — **without `R6`**.
- **What it does not license:** an **absolute selectivity** claim (*"this molecule is N-fold selective"*), which
  still needs `R6`. The statement stays explicitly conditional on the chosen open states of both paralogues.
- **Consequence for the plan:** `R6` blocks the **ABFE** route to `R7` and does **not** block a `ΔΔΔG` route to
  `R11`'s causal question. That is a real narrowing of the blocker set, and it is why this analysis is worth more
  than a yes/no.
- ⚠ **It is an ARGUMENT, not a measurement** — the same register the repo already uses for
  *"'not implicated' is an argument, not a measurement"*. It should be recorded as one.

**DD-3 · It makes a known-answer test in the right regime cheap and well-posed.**
`ΔΔΔG` needs **two complex legs plus one shared solvent leg** — the purchase shape of an RBFE edge pair, whose
basis has one home in [pricing.md](../compute/pricing.md) and the roadmap's *Per-edge bases* table. The ABFE
selectivity control needs **two full absolute calculations with restraints**. So the cheaper instrument is also
the one whose engine has passed something. **The program has been trying to buy its selectivity control in its
most expensive and least reliable currency.**

### 2.5 · The consequence — the missing instrument, named

Because the inheritance fails, `ΔΔΔG` needs **its own** known-answer test — and that test has an exactly
specifiable shape, which is more than any other instrument in this program has for the paralogue-scale regime:

> **A public pair of homologous proteins + a matched congeneric ligand pair + FOUR measured affinities + a
> structural basis on both arms, scored as `ΔΔΔG_calc` vs `ΔΔΔG_exp`.**

`V6` is the same machinery one difference lower. `V10` is the right **size** on the wrong **side** (protein
mutations), and its own wedge-sized candidate is unrun. `V4` is the right **question** in the wrong
**currency**. None of the three is a ligand-side, between-protein, ~1 kcal/mol known answer.

**Two searches settle whether such a system exists. Both are $0 and both route through CI.**

- **C01a — the ligand-side wedge-band scan.** The exact analogue of the SKEMPI scan that returned
  `barnase_barstar_W35F` from 7,085 rows. Query ChEMBL/BindingDB for compounds measured against **both** members
  of a paralogue pair; keep congeneric pairs whose selectivity **shift** sits in the ~0.5–2 kcal/mol band;
  cross-reference the PDB for holo structures on both arms. The ChEMBL REST API is already called from CI by
  [`nr4a3_dock.py`](./nr4a3_dock.py), so this is a pattern the repo already runs.
- **C01b — the CREBBP/BRD4 precheck.** The designated binary control already has **both arms as real holo
  crystals with the same ligand** (4NR7 / 5BT4; experimental ΔΔG ≈ 2.2 kcal/mol — one home
  [`selectivity-benchmark.json`](./selectivity-benchmark.json)). The only missing ingredient for a **relative**
  version is a congeneric analogue with measured affinity in *both* proteins. That is a ChEMBL lookup of exactly
  the [`pmx_mutation_reference`](./pmx_mutation_reference.py) shape: it returns either a reference or
  `STOP_NO_REFERENCE`, and **a refusal on evidence is a better outcome than a budget hold** — the pmx arm has
  already demonstrated that.

A negative control must ship with the benchmark: a matched pair expected to show **no** selectivity shift, so the
instrument has its own null. Open decision 7 binds it — *no accuracy band wider than the signal being calibrated,
and a stated null-rejection rate up front.*

### 2.6 · One scope constraint carries over intact

**`V6`'s validation covers the `am1bcc` BINARY lane only.** A PROTAC-sized ligand cannot be `am1bcc`-charged —
`sqm` ran **>85 min on a 166-atom recruiter without converging** — so a `ΔΔΔG` on a degrader runs NAGL. The
benchmark must therefore be run **in the lane it will be used in**, or the charge model pinned across benchmark
and application. Otherwise this repeats roadmap §3.4's exact error one lane over.

### 2.7 · What this analysis does **not** say

- It does **not** say `S = −0.1297 ± 0.3264` (RUNG 5a-KS, `V16`) is wrong. It says the reason `V16` has no
  calibrator is **structural**, not an oversight: a within-pocket pass cannot be transferred to a between-pocket
  quantity, so the calibrator has to be bought in the between-pocket currency.
- It does **not** say the ternary double difference and the binary one are the same instrument. 5a-KS's `S` is a
  **ternary** double difference on the **NAGL** lane; `C01` is a **binary** one on the **am1bcc** lane. They
  share the algebra and not the validation.
- It does **not** license reporting any existing `ΔΔΔG` or `S` as calibrated. **Open decision 13 stands.**

---

## 3 · The three findings that came out of checking rather than reasoning

Each of these is a $0 observation taken during this pass, and each changes a status the roadmap carries.

### 3.1 · The paralogue pocket ensembles already exist, and the detector has never been pointed at them

[`nr4a-paralogue-dynamics.json`](./nr4a-paralogue-dynamics.json) `ensemble_census` records
`results/nr4a1-pocket-ensemble` and `results/nr4a2-pocket-ensemble` as existing, each with **100 frames in
exactly NR4A3's subset structure** — `metad` 25 + `release_rep0/1/2` 25 each, 75 unbiased. Those frames are
**committed to this repo** (`git ls-files results` → 2,082 files).

And [`nr4a3-pocket-reharmonize-summary.json`](./nr4a3-pocket-reharmonize-summary.json) has **eight rows, and
every one of them is NR4A3** — `af2_static`, `calibration_nr4a3`, `8xtt_20conformers`, `metad_frames`,
`release_rep0/1/2`, `release_unbiased_pooled`.

⇒ **The paralogue-matched cryptic-pocket druggability contrast — the premise of the entire non-covalent route —
has never been computed, and the inputs for it are frame-matched and already on disk.** That is candidate
**C04**, and it is $0.

### 3.2 · `R14` is recorded as "no instrument" and is about 8/9ths built

- The **sequence screen has run**: [`nr4a-superfamily-selectivity.json`](./nr4a-superfamily-selectivity.json)
  screened 47 receptors and flagged exactly **NR3C2 (MR)** and **AR**.
- The **docking harness has run at scale**: SI §S1, a 9-target anti-target panel over ~6,000 marketed compounds.
- **AR is already a panel target** ([`antitarget_panel.json`](./antitarget_panel.json), 2AM9/testosterone).
- **`denovo_401` is already staged** as an anti-target candidate
  ([`nr4a3-antitarget-denovo401.json`](./nr4a3-antitarget-denovo401.json)).

⛔ What is actually missing is (a) **MR/NR3C2 is not in the panel**, and (b) the SI's *second* requirement — a
**cryptic-pocket-formation test** on AR/MR — has no instrument, and **C04 is exactly that instrument**. That is
candidate **C08**.

⚠ And the panel has an obvious self-control that appears never to have been run: does it rank each anti-target's
**own cognate ligand** correctly through the identical smina protocol? Those ligands are already named in the
panel file.

### 3.3 · "Requires chemoproteomics, which this program does not have" conflates a technique with a dataset

That phrase, or a near-variant, appears in at least six files — the paper (three places),
`nr4a3-inverse-linker-design-2026-07-25.md`, `nr4a3-orientation-basin-search-2026-07-25.md`,
`nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md`,
`nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md` and
`nr4a3-transfer-anchor-and-handle-risk-2026-07-25.md` — and it is the reason limit **L6** of the categorical
audit (*no thiol pKa, nucleophilicity, adduct stability or promiscuity anywhere*) has never been attacked.

**Chemoproteomics is a wet-lab technique; published chemoproteomics datasets are public data.** Using one is the
same move this repo already makes with **SKEMPI** (7,085 rows, protein mutations → `barnase_barstar_W35F`) and
with **ChEMBL** (affinities, already fetched from CI). Filing the axis as wet-lab-gated has been hiding an
available data axis on the program's **strongest surviving claim**.

⚠ **This is a reason to run a precheck, not a reason to assert coverage.** Whether any public dataset actually
contains NR4A3 C397 or NR4A1 C551 is **unverified**, and no source, dataset or value may be cited before a
`pmx_mutation_reference`-shaped precheck returns. That is candidate **C03**, and the precheck is $0.

---

## 4 · What is $0 and what needs money

**Validatable at $0 or near-$0 — known-answer test ALREADY available:** `C02` `C04` `C06` `C08` `C09` `C13`

**Validatable at $0 — but a $0 PRECHECK has to run first to establish the known answer:**
`C01` (via C01a/C01b) · `C03` · `C05` · `C11` · `C12` · `C15`

**No known-answer test needed, because it is a READ and not an inference:** `C07` `C10`

**Needs spend:**

| id | what | shape of the spend |
|---|---|---|
| **C14** | `barnase_barstar_W35F` | **priced** in [pricing.md](../compute/pricing.md), small, staged, CI-verified, **no outstanding authorization** — the only ready item that attacks the regime gap directly |
| **C01** (run) | the ΔΔΔG benchmark itself | one RBFE **edge pair** + a shared solvent leg — *after* its $0 search returns a system |
| **C15** | co-fold classifier | cheap GPU; the stack is already baked |
| **C16** | NNP correction | unpriced, and it targets a term that already cancels |

---

## 5 · Edits the roadmap needs — routed, not applied

Verbatim in [`instrument-options.json`](./instrument-options.json) → `proposed_roadmap_edits`. In brief:

1. **§3.1 / §3.4** — record the double-difference finding as an **instrument fact**: a ligand-side double
   difference does *not* inherit `V6`'s validation, and why. §3.4 exists to carry exactly this kind of scope fact
   about `V6`, and this is the largest one missing.
2. **§2.1 / §5 row `R6`, §8 Route A** — `R6` blocks the **absolute** route to `R7` and **not** the relative
   double-difference route to `R11`'s causal question. Mark it as an argument, with its stated condition.
3. **§10.1** — give rungs to C01a, C01b, C02, C03, C04, C05. Per §10.3's own lesson, *"a caveat with nowhere to
   go is how work gets silently dropped"* — every one of these currently exists only as a limit in a paper caveat
   or an audit's limits table.
4. **§2.2 row `R14`** — "no instrument" overstates the gap by about 8/9ths (§3.2 above).
5. **§3.1 row `V17` / §7 branch 1** — the failed positive control (NR4A1 Cys551) may be checkable against
   **measured** data; the standing "we don't have chemoproteomics" phrasing conflates technique with dataset.
6. **[method-watch.md](../method-watch.md)** — three trigger rows are missing, and together they are the watch
   for a fix to the program's *stated* bottleneck: **(a)** ligand-side selectivity FEP / ΔΔΔG methodology and
   benchmarks; **(b)** public cysteine-chemoproteomics releases; **(c)** ubiquitination-site mapping datasets for
   degraders. The watch currently has no row that would fire on an instrument able to carry a selectivity claim
   *without* a free-energy difference.

⚠ **Also observed, not diagnosed:** [`field-scan-log.md`](../field-scan-log.md) carries exactly **one** entry,
dated 2026-07-13 and described in the file itself as a manual catch-up baseline, while the weekly Routine's
documented behaviour is to append to it. The *mechanical* digest is healthy (`origin/method-watch-cache`,
`Method-watch digest 2026-07-31`). Whoever owns the watch should take the routine-level check — it is free.

---

## 6 · What this queue does not claim

- **No candidate here is a result.** Each is a proposal to *measure* something, and several may return
  `STOP_NO_REFERENCE`, which is a good outcome and not a failure.
- **No candidate here raises any claim ceiling.** Roadmap §2.3's rule is untouched: a requirement may never be
  claimed above the validation status of the instrument that produces it, and every instrument in this queue is
  at *proposed*.
- **Nothing here re-litigates a settled call.** In particular, the fusion-exclusive routes have their own settled
  body of work ([`fusion-selective-approaches-overview.md`](../manuscripts/fusion-selective-approaches-overview.md)
  and its five manuscripts, with a live deferred Level-1-vs-Level-2 decision). `C07` is an **instrument for
  `R13`**, not a proposal to change routes.
- **Nothing here implies proteome-wide selectivity, EMC efficacy, safety, a therapeutic window, or clinical
  readiness.**
