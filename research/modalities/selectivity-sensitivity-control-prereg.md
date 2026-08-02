# Pre-registration — the endpoint-MD **sensitivity control** (options paper D1)

**Written and committed BEFORE the first GPU leg.** A criterion written after the numbers arrive is not a
criterion; that is the whole reason this document exists and the reason it is dated by its commit rather than
by a line of prose. Every clause below is executable —
[`selcal_panel.PASS_CRITERION`](./selcal_panel.py) is its machine home, and
[`tests/test_selcal_panel.py`](./tests/test_selcal_panel.py) fails CI if a clause changes.

**Design:** [`selectivity-resolution-options.md`](./selectivity-resolution-options.md) §2-D, option **D1**.
That file is the design. It is not re-derived here and nothing here amends it.

> **⚠ AMENDED 2026-08-02 — see [AMENDMENT 1](#amendment-1--2026-08-02-measured-input-fault-smarca4-model-3)
> at the foot of this file.** One co-fold model (**SMARCA4 seed 3**) is excluded on a measured static input
> fault, under the clause §4 froze in advance. **NO CRITERION CLAUSE CHANGES.** The frozen design remains
> **24 legs**; the admissible panel is **22**, and both numbers are carried together everywhere they appear
> (`selcal_panel.panel_manifest` → `n_units` / `n_units_at_freeze`; `selcal-collect.json` → `expected` /
> `expected_at_freeze`) precisely so a completed 22-leg panel can never be read as the 24-leg one this
> document was frozen against.

---

## 0 · ⛔ What this is, and what it is not

> **This is an INSTRUMENT CALIBRATION. It is not a selectivity result.**

The NR-V04 retrospective returned tier **DISCORDANT, p = 0.3929** — a non-resolution. The consequence that
matters is not the tier. It is that **the retrospective *was* the positive control**, and the program therefore
has **no evidence that this workflow can detect paralogue selectivity at all.**

That gap cannot be closed on NR-V04 at any n. The system is **covalency-confounded**: the reactive Cys551 is
unique to NR4A1 (Leg 0, `nrv04-cys-conservation.json` — Tyr in NR4A2, Thr in NR4A3, no cysteine within ±5), so
warhead chemistry alone is *sufficient* to explain the reported selectivity and the non-covalent arm has **no
guaranteed true effect to detect**. More power on that panel buys resolution on a question that cannot answer
this one. The method calibrator that would — valB_full module 3, SMARCA2-vs-SMARCA4 — **has never been run**,
and every other control in the repo fails as a *sensitivity* control for its own reason: TYK2/valA validates
relative FEP **within one pocket**; valB_mini failed on sign; CRBN/lenalidomide is **pose recovery**; the decoy
nulls are **negative** controls, which bound false positives and by construction cannot establish sensitivity.

So this panel asks exactly one question:

> **Can the endpoint-MD readout detect a paralogue difference that is KNOWN, from a primary source, to be
> there?**

**A PASS licenses exactly one sentence** — *"run identically and without tuning on a known-selective paralogue
pair with solved structures on both arms, the ensemble endpoint workflow discriminated them"* — and **nothing
else**. It does **not** license any claim about NR4A1/2/3; any claim about degradation, efficacy, a therapeutic
window or clinical readiness; or any re-scoring of the NR-V04 retrospective, which is frozen.

**A FAIL is ambiguous** between *"the readout is blunt"* and *"this pair is hard"*. That is why the shape below
is chosen to be adequately powered **before** it runs, and why the failure sentence is written in advance
(§6).

⚠ **This is NOT valB_full module 3**, and must not be presented as a way around STRATEGY **Open decision 9**.
Module 3 is an *alchemical cooperativity* module behind the valB gate; this panel is the **endpoint-MD lane at
endpoint-MD prices** and **asserts no free energy** — the same argument the NR-V04 prereg's §9 RESOLUTION used
to run Arm E. If trimcrae judges that calibration-addendum condition 7 *does* reach an endpoint-MD control,
this panel falls.

---

## 1 · The system

| | |
|---|---|
| **Pair** | SMARCA2 (P51531) vs SMARCA4 (P51532), bromodomains |
| **E3 machinery** | VHL (P40337) + Elongin B (Q15370) + Elongin C (Q15369) — the VCB complex present in the deposited ternaries on **both** arms |
| **Ligand** | **PRT3789**, CCD **A1BB4**, co-folded onto **both real paralogue sequences** |
| **Structural inputs** | Boltz-2 co-folds, **6 diffusion seeds per arm**, one protocol, one process, one host |
| **Readout** | **E1** = `R1_interface.plateau_A` (Å), computed by [`nrv04_covalent_md`](./nrv04_covalent_md.py) **unchanged** |
| **Sampling** | 1 ns equilibration + 5 ns production, the canonical `md_settings` lengths — **identical** to the NR-V04 retrospective |

**Why both arms are co-folded rather than one being modelled.** Options-paper precondition 2 and STRATEGY Open
decision 9b: `smarca2_model.py` builds SMARCA2 by homology **mutation** from the 3.73 Å 8G1Q SMARCA4 chain, so
a model error would sit on **one arm only** — the asymmetry this control exists to avoid. Here each arm is
co-folded from its own UniProt sequence with the identical protocol, and the deposited ternaries are used to
**validate** the co-folds rather than to supply them.

**Why the constructs are the crystallographers'.** Quoted from Kofink et al. 2022's methods
(10.1038/s41467-022-33430-6): *"the bromodomains (BDs) of SMARCA2 (SMARCA2BD; **P51531-2, residues
1373-1493** …), SMARCA4 (SMARCA4BD; **P51532, residues 1448–1569** …)"*. Using the published construct is what
makes the two arms comparable to each other **and** to the deposited ternaries. ⚠ `P51531-2` is **isoform 2** —
fetching the canonical entry and slicing the same numbers would silently take a different span.

**Nothing structural is typed.** Sequences are fetched from UniProt; the ligand SMILES comes from the RCSB
chemical component dictionary; the spans are quoted. [`selcal_stage.py`](./selcal_stage.py) raises rather than
falling back if any of those is unavailable — a co-fold built on a guessed structure is a fabricated
experiment, and it would be invisible downstream because every later step would run perfectly on the wrong
molecule.

---

## 2 · The reference — measured, primary-source, and honest about its limit

**Precondition 1** of the options paper: *a positive control needs a **measured, primary-source** selectivity
value*. Fetched, not remembered, by
[`selcal_reference_selectivity.py`](./selcal_reference_selectivity.py) →
[`selcal-reference-selectivity.json`](./selcal-reference-selectivity.json).

> **PRT3789 promoted selective degradation of SMARCA2 while sparing its highly homologous paralog, SMARCA4.**
> — *PRT3789 Is a First-in-Human SMARCA2-Selective Degrader That Induces Synthetic Lethality in SMARCA4-Mutated
> Cancers*, **Cancer Research** (2026), doi **10.1158/0008-5472.can-25-1141**

⚠ **The magnitude is NOT quoted, and that is deliberate.** The primary publication is not open access, so no
DC50 pair or fold window is transcribed. Secondary sources report ~40-fold; **that number is not used anywhere
in this panel.** AGENTS.md's rule binds: never fill a gap with a plausible number.

**Why direction-and-existence is sufficient here — and only here.** The criterion this control applies is
itself **categorical**: *does the readout separate the arms, in the predicted direction?* So the reference only
has to answer the same kind of question. STRATEGY **Open decision 7** (*the accuracy band may not be wider than
the signal being calibrated*) is satisfied because **neither side is a magnitude**. A *quantitative* calibration
of E1 against degradation is a different claim, is not licensed by this reference, and **is not attempted** —
E1 has **no established quantitative link to degradation selectivity at all** (options paper §1d(3)).

**Why a ternary-geometry readout is the right instrument for this pair.** Kofink et al. 2022 localise the
paralogue difference to a protein–protein interaction at the **VCB↔bromodomain interface** — which is exactly
the interface E1 measures:

> *"Represented are the key PPIs between VCB and SMARCA2BD/SMARCA4BD, highlighting the selectivity-inducing
> hydrogen bonding between Gln1469 of SMARCA2BD and VCB"* — Nat Commun 2022, PMC9551036

That is a fact about **the pair and the VHL machinery**, not a claim about PRT3789.

**Why this ligand and not ACBI2**, which has better-documented numbers (1 nM vs 32 nM, >30-fold, open access):
ACBI2 has **no deposited structure at all** — its own paper deposits compounds 4/5/6/10 (7Z78 / 7Z6L / 7Z77 /
7Z76) — so its chemistry could only come from a vendor catalogue. PRT3789 has a **matched-ligand ternary on
both arms**: **9DTY** (SMARCA2, 3.19 Å) and **9DTX** (SMARCA4, 2.11 Å). Each arm's co-fold can therefore be
validated against a real structure of the very complex it models, which is precisely what precondition 2 asks
for.

**The matched non-selective comparator is named but not run.** ACBI1 (CCD 87A) degrades SMARCA2 at DC50 6 nM
and SMARCA4 at 11 nM (10.1038/s41589-019-0294-6) — the natural **negative** control for a follow-on. It is a
second 24-leg panel and a second spend, outside the authorised $3.79, and it is named here so that no later
reader concludes none was available.

---

## 3 · The design, and why this shape

**2 arms × 6 co-fold models × 2 velocity replicas = 24 legs.**

| property | value | why it is the binding one |
|---|---|---|
| unit of independence | the **co-fold model** | per-leg values are collapsed to model means before the permutation, so velocity replicas cannot inflate the reference set |
| reference set | **C(12,6) = 924** | derived by `selcal_gate.design_floor()`, never typed |
| minimum attainable one-sided *p* | **0.00108** | two orders of magnitude under α |
| the shape this replaces | NR-V04's NR4A1-vs-NR4A3 pairwise: **C(5,3) = 10, floor 0.10 > α** | its power against *any* separation was **zero**. `p = 0.70` there was **not a null; it was a non-measurement.** |

Replicates are kept (2 per model) even though they cannot move the reference set, for the reason AMENDMENT 4
recorded: **they are what makes an input-fault exclusion checkable.** At one replica per model there is no
sibling, so a bad structure and a host-side death stop being distinguishable from the run record.

---

## 4 · ★ THE PASS CRITERION — frozen before the run

**Statistic:** `mean(E1 | SMARCA2 arm) − mean(E1 | SMARCA4 arm)`, over **model-level means**.

**Test:** exact **one-sided** permutation test over all C(n_a+n_b, n_a) label assignments, observed arrangement
included. Implementation is `nrv04_retro_gate.exact_permutation_p` — **the same frozen scorer that produced the
NR-V04 verdict**, imported rather than re-implemented, because a control scored by a second implementation
would calibrate a statistic the program does not use.

**Direction:** `alternative = "less"`. The SMARCA2 arm is predicted to have the **lower** E1 plateau (the more
stable ternary interface), because the reference ligand is SMARCA2-selective and the pair's selectivity is
attributed to that interface. This is a **commitment**, not a convenience: a significant result in the other
direction is a **FAIL**, not a pass with a footnote.

**α = 0.05**, one-sided — the same α as the panel this control calibrates. A control judged at a looser α than
the experiment it calibrates is not a calibration.

### PASS requires **ALL** of:

1. **p ≤ 0.05** on the exact one-sided permutation test;
2. the observed statistic is **negative** (SMARCA2 lower / more stable) — the direction the primary source
   predicts;
3. the sign **survives leave-one-model-out**: every single-model refit keeps the same sign;
4. **at most 2 technical failures in each arm**
   (⚠ 2, not `nrv04_retro_gate`'s 1 — that constant governs an arm of 6 legs, this one an arm of 12. What is
   held constant is the **proportion**, not the integer; copying the integer across would silently make this
   panel's tolerance half as generous, i.e. a stricter rule arrived at by accident);
5. **at least 4 conforming co-fold models in each arm**, so that after any measured input-fault exclusion the
   reference set can still reach α (C(8,4) = 70, floor 0.0143).

### The other tiers

* **NULL** — the design is adequately powered (clauses 4 and 5 hold) and **p > 0.05**. This is a **real
  negative** and is reported as one. A significant p whose sign does **not** survive leave-one-model-out also
  lands here: a result carried by a single co-fold model is not a detection.
* **WRONG_SIGN** — **p ≤ 0.05 in the direction the reference contradicts**. Reported as a **fail of the
  control**, with the sign stated: a readout that separates a known pair *backwards* is worse than one that
  cannot separate it.
* **INDETERMINATE** — an arm is underpowered by technical failures, or fewer than 4 conforming models survive
  in an arm. **Nothing was measured. This is not a null.**

### No interim analysis

The tier is emitted **only** when the panel is complete or an arm is definitively short. Peeking at a partial
panel and stopping on a favourable p is the defect NR-V04 prereg §4f exists to prevent, so
`selcal_vast_launch.mode_collect` **suppresses the label** on an incomplete panel while still writing the
evidence — hiding the evidence would be a different kind of dishonesty.

### Exclusions

`selcal_panel.EXCLUDED_COFOLD_MODELS` is **empty at freeze** and may only gain an entry on a **measured static
input fault** proved by `selcal_stage.cofold_input_audit` **before** the leg is scored — the same standard
AMENDMENT 4 had to meet, and for the same reason: an exclusion is defensible when the fault is a property of
the *input*, provable before any MD is interpreted. **An exclusion justified by how a leg's E1 came out is the
retune this program forbids.**

> **⚠ NO LONGER EMPTY.** One entry was added 2026-08-02 under exactly this clause —
> [AMENDMENT 1](#amendment-1--2026-08-02-measured-input-fault-smarca4-model-3). The clause itself is
> unchanged; this is the clause *operating*, not the clause being widened.

---

## 5 · What is measured, and what is deliberately not

* **Endpoint MD only. No free energy is computed and none may be inferred.**
* No claim is made about NR4A1, NR4A2 or NR4A3.
* No claim is made about degradation, efficacy, cooperativity, a therapeutic window, or clinical readiness.
* No landed NR-V04 leg is re-scored and no NR-V04 criterion is amended.
* The E2–E4 endpoints (`R2_recruitment`, `R3_lys`) are **computed and reported** for every leg, because the
  driver writes them, but **only E1 is gated on**. Choosing an endpoint on the data that will then test it is
  endpoint-shopping.

---

## 6 · The failure sentence, written in advance

If the control returns **NULL** or **WRONG_SIGN**, this is what the paper says — written now, so it cannot
later be re-narrated as a method failure or quietly dropped:

> Run identically and without tuning on a known-selective paralogue pair with solved structures on both arms,
> at a design whose reference set can reach α, the ensemble endpoint workflow did not discriminate them. The
> workflow's paralogue-discrimination authority therefore rests on nothing this program has measured, and the
> NR4A3 selectivity predictions are reported as **unvalidated predictions**.

A fail does **not** distinguish *"the readout is blunt"* from *"this pair is hard"*, and must not be reported
as though it did.

---

## 7 · Spend

24 endpoint-MD legs. The cost is **DERIVED, never typed** — `n_legs × vast_cost_model.ENDPOINT_MD_REF_GPU_H_PER_LEG
× the planning rate in vast-ladder-repricing.json`, the same arithmetic
`selectivity_resolution_options.price_units` performs, regenerated by `selcal_vast_launch.ladder_cost()`. Co-fold
generation is a **separate, estimated** line ([pricing.md](../compute/pricing.md) §B, *Co-fold / docking*) and
is never summed into a derived total.

Every rental — fan-out, single pilot, resume, and the co-fold host — faces **both** ceilings: the rung's
authorised dollars and the §1 **rate line** (`inflight_usd_per_ns.APPROVED_USD_PER_NS`), whichever is lower,
and a refusal names which one it hit. A hold is never silent: the board-depth snapshot that caused it is
committed to `selcal-market-hold.json` and the per-tick decision to `selcal-gate-record.json`.

---

## AMENDMENT 1 — 2026-08-02 (measured input fault: SMARCA4 model 3)

**Nothing in §4 changes.** This amendment records one exclusion taken under the clause §4 froze in advance,
and — equally important — records the unit it **refused** to exclude, because that refusal is what shows the
exclusion was not shaped by what the panel had landed.

### What was measured

`selcal-smarca-cofold-v1/smarca4/seed_3` places two Boltz-placed heavy atoms in different chains **0.693 Å**
apart:

```
[audit] {"ok": false, "min_heavy_atom_sep_A": 0.693, "pair": ["A:LYS71:O", "E:SER38:O"],
         "threshold_A": 1.0, "n_heavy_atoms": 4499}
[audit] REFUSING to run: … the Lennard-Jones term diverges from geometry like this and minimization
        cannot escape it. This is a static INPUT fault, provable before any MD is interpreted.
```

`selcal_stage.cofold_input_audit` — the only instrument §4 licenses — refused on **every** attempt.

### The standard, and that it is met

| §4 requires | evidence |
|---|---|
| a **static** fault, provable **before** any MD is interpreted | the audit reads geometry from `complex.pdb` and refuses **before** minimisation. No endpoint value of any kind existed at the moment of refusal. |
| a property of the **input**, not of the rental | both replicas (`r0`, `r1`) refused with **byte-identical** numbers across **12 attempt logs on five distinct machines** (46539178, 46549246, 46553998, 46554862, 46555738). A host-specific fault cannot reproduce to the third decimal on five hosts. |
| the replicate structure makes the claim **testable** | both replicas of the bad co-fold died; **both replicas of every other landed model ran**. |
| **not** justified by outcome | no leg of model 3 ever integrated a femtosecond, so no E1 value for it exists to have been inconvenient. |

Evidence: container stdout via `--mode diag`, runs **30728025643** and **30728185356**.

### ★ The unit this amendment does NOT exclude — and why that matters more

`selcal-smarca4-m2-r0` was **also** unlanded and **also** billing at the moment this was written (275 min on
instance 46539144). Excluding what happens to be unfinished is outcome-shaped reasoning wearing an input
fault's clothes, so it was tested against the same standard **and failed it, in the exonerating direction** —
the same shape as AMENDMENT 4's §4.2 test on the NR-V04 lane:

1. **Its co-fold AUDITS CLEAN.** Same audit, same day, same container: `{"ok": true,
   "min_heavy_atom_sep_A": 1.2994}` — comfortably above the 1.00 Å floor.
2. **Its replica sibling LANDED.** `selcal-smarca4-m2-r1` produced a conforming production leg off the same
   co-fold model, which is direct evidence that model 2 is runnable.
3. **Its failure is elsewhere.** It reached `gpu_util: 0.0` *after* passing staging, i.e. a host-level
   failure, not a refusal.

So **model 2 stays in the panel and its missing replica is re-run.** An amendment that quietly took both
unfinished units would have left an arm of 4 and a much easier story; it is not available on the evidence.

### What the panel is now

| | at freeze | admissible |
|---|---|---|
| legs | 24 | **22** |
| models, SMARCA2 arm | 6 | 6 |
| models, SMARCA4 arm | 6 | **5** |

§4's reference-set clause is **satisfied, not merely survived**: both arms hold ≥ `MIN_MODELS_PER_ARM` (4),
and the exact one-sided permutation test now runs over **C(11, 6) = 462** label assignments, floor
*p* = **0.00216** — an order of magnitude below α = 0.05. The clause was written as *"at least 4 conforming
co-fold models in EACH arm … after any measured input-fault exclusion"*, i.e. this exact contingency was
anticipated before the run and the design was sized for it.

⚠ **The arms are now UNBALANCED (6 vs 5).** The criterion was written for a balanced design and its
reference-set clause is stated as a per-arm floor rather than as symmetry, so the exact test is unaffected —
it enumerates the arrangements that exist. The consequence is on **power**, not validity, and it is
**adverse**: an arm of 5 model-level means is less powerful than one of 6. That direction is stated here so a
NULL from this panel is read with it already on the record, rather than acquiring it afterwards.

### Not a re-roll

Re-running Boltz on seed 3 until it produces a clean structure was **not** done and is **not** available under
§4: re-drawing an input until it passes is selection on the input, and the seed list is frozen. The panel
shrinks; it is not repaired.
