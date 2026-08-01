# What would actually give us enough resolution to establish paralogue selectivity in-silico?

**A costed options paper. Nothing here is launched, nothing here is decided, and no preregistered criterion is
amended, proposed or re-scored.** trimcrae chooses; this document exists so that the choice is made against
derived numbers rather than intuitions.

Every figure below is **regenerated, never typed**:
[`selectivity_resolution_options.py`](./selectivity_resolution_options.py) →
[`selectivity-resolution-options.json`](./selectivity-resolution-options.json), which imports the **frozen
scorer** ([`nrv04_retro_gate.py`](./nrv04_retro_gate.py)) rather than re-implementing it, reads the landed panel
out of the **emitted verdict** ([`nrv04-retro-verdict.json`](./nrv04-retro-verdict.json)), and prices everything
through [`vast_cost_model`](./vast_cost_model.py) × the planning rate in
[`vast-ladder-repricing.json`](./vast-ladder-repricing.json). Regenerate with
`python3 research/modalities/selectivity_resolution_options.py`; tests in
[`tests/test_selectivity_resolution_options.py`](./tests/test_selectivity_resolution_options.py).

---

## If you read only this

1. **Two different problems, not one.** The **primary** contrast is **noise-limited** (its floor, 0.0179, is
   comfortably under α — nothing structural stopped it). The **NR4A1-vs-NR4A3 pairwise** is **structurally
   unresolvable** (floor 0.10 > α, so its power against *any* separation is zero). Fixing one does not touch
   the other.
2. **More replicates fixes neither.** They cannot move a reference set — demonstrated on the frozen scorer at
   **100 legs per model** — and the noise they *can* remove is capped at **19 %**. Do not buy B1/B2.
3. **The reallocation is free and strictly better.** The same six legs per arm spent as **6 models × 1
   replica** instead of 3 × 2 takes the pairwise floor from 0.05 to **0.0011** and raises power ~**1.5×**. The
   cost is auditability, not dollars.
4. **Resolution is affordable — and that is the trap.** A panel big enough to resolve the separation actually
   observed costs **~$49–$116** plan. It would buy a statistically significant sub-Ångström plateau difference
   on a readout with **no established link to degradation selectivity**, which prereg §6 forbids reporting as
   selectivity. Power is not what is missing.
5. **What is missing is a positive control**, and one is available for **$3.79**: run the same endpoint on a
   paralogue pair with a known answer and solved structures on **both** arms. That is the recommendation.
6. **Whole recommended sequence: $9.47 plan ($3.92–$23.85), no step over $50, serialized** because steps 1 and
   2 can each cancel what follows. If step 2 comes back null, the honest paper reports predicted selectivity as
   **unvalidated** — §4 writes that sentence in advance.

---

## 0 · Why this document exists

The NR-V04 retrospective (Arm E / R1) completed 16/16 and returned **DISCORDANT**. Its own verdict artifact is
the one home for the numbers; read it there. **The consequence that matters is not the tier — it is that the
retrospective WAS the positive control**, the one experiment meant to show that this workflow can detect
paralogue selectivity where the answer is already known. It did not resolve. So the program has **no
demonstrated positive control for selectivity detection**, and every selectivity claim in the paper is
correspondingly less warranted.

That is the problem this options paper is scoped to. It is not scoped to rescuing the retrospective, which
[AMENDMENT 4](./nr4a3-nrv04-retrospective-prereg.md) §4.4's integrity test forbids and which none of the
options below attempt.

---

## 1 · The binding constraint — verified, and the working hypothesis is **half right**

The hypothesis put to me was: *the limit is the size of the permutation reference set, which is set by the
number of models, so no amount of replicate sampling can fix it.* Re-derived rather than quoted:

**The replicate half is exactly right, and stronger than stated.** The minimum attainable one-sided p of an
exact permutation test is `1 / C(n_a + n_b, n_a)` — a property of the **design**, true whatever the data say.
The unit of independence is the co-fold **model** (prereg §4a), and `nrv04_retro_gate.model_level_values`
collapses legs to model means before the enumeration, so the reference set is a function of **model counts and
of nothing else**. Demonstrated on the frozen scorer, not argued: feeding it the landed model means at 2, 8, 20
and **100 legs per model** (16 → 800 legs) returns the *identical* reference sets (56 and 10) and the
*identical* p-values every time — `replicates_do_not_move_the_bound` in the artifact.

**But the hypothesis is wrong about which test is bound.** There are two tests and they fail for opposite
reasons:

| test | shape | arrangements | min attainable one-sided p | can it reach α = 0.05? | what is actually stopping it |
|---|---|---|---|---|---|
| **Primary** (NR4A1 vs NR4A2∪NR4A3) | 3 vs 5 models | 56 | **0.0179** | **YES** | ⚠ **NOISE.** Nothing structural stopped it — the design could have returned 0.0179. |
| **Pairwise NR4A1 vs NR4A3** | 3 vs 2 models | 10 | **0.10** | **NO** | ⚠ **STRUCTURE.** Bounded above α whatever the data. |
| Pairwise NR4A1 vs NR4A2 | 3 vs 3 models | 20 | 0.05 | only at *perfect* separation | both — the floor **equals** α |

**So they are two different problems, and an option that solves one is silent on the other.** Where a table
below says an option leaves NR4A1-vs-NR4A3 **structurally unresolvable**, that is the literal claim: its power
against *any* true separation, however large, is **zero** — `power_pairwise(3, 2, ·, δ)` returns 0.0 at
δ = 1 Å, 5 Å and 50 Å alike, and its exact size is 0.0 too (`floor(α × 10) / 10 = 0`). It cannot reject; it
also cannot be trusted to fail to reject. **`p = 0.70` on that comparison is not a null. It is a
non-measurement.**

### 1a · The noise half, measured from the landed panel

The registered leg-to-leg σ (`nrv04_retro_gate.MEASURED_LEG_SIGMA_A`) is measured between **velocity replicas
of one model** and is therefore not the quantity the test competes against. The relevant one — the pooled
**within-arm, model-level** SD — is derived here from the landed panel's own model means:

| quantity | value | source |
|---|---|---|
| σ_model (pooled within-arm, df 5) | **1.0278 Å** | derived, `landed_panel` |
| observed primary separation | 0.2825 Å = **0.275 σ** | verdict artifact |
| observed NR4A1−NR4A3 separation | 0.4124 Å = **0.401 σ** | verdict artifact |
| σ_between-models (replicate floor) | **0.8312 Å** | `variance_decomposition` |
| fraction of model-level variance replicates can remove | **34.6 %** | `variance_decomposition` |

That last row is the number that kills option B on its own: `σ_model² = σ_between² + σ_leg²/replicas`, so going
from 2 replicas to **infinitely many** takes σ_model from 1.0278 Å only as far as **0.8312 Å** — a 19 % noise
reduction, for unbounded money, and **zero** change to any reference set. *(Honesty: the two SDs are measured on
different panels and both carry large sampling error at these df; `variance_decomposition` refuses to return a
floor rather than a negative variance if they are ever inconsistent, and it currently does not.)*

### 1b · Power of the frozen rule at the as-run design — re-derived, and it is blunter than registered

⚠ **NOT A REGISTERED MDE, and deliberately not one.** [AMENDMENT 4 §4.3](./nr4a3-nrv04-retrospective-prereg.md)
declined to register a replacement and stated only the direction — *"optimistic for the NR4A3 arm at n = 2, so
power is lower than registered"*. This is a **design-planning** figure for choosing between options, computed
after the fact against the panel's own measured σ. It does not amend the prereg and must not be cited as
though it did. The criteria audit's power curve stays the registered 3-vs-6 one and says so.

P(the frozen rule returns CONCORDANT) at the as-run 3/3/2, σ = 1.0278 Å:

| true separation | 0.5 Å | 1.0 Å | 1.5 Å | 2.0 Å | 2.5 Å | 3.0 Å |
|---|---|---|---|---|---|---|
| power | 0.11 | 0.25 | 0.44 | 0.66 | 0.83 | 0.93 |

80 % power arrives around **2.5 Å**, against the ≈1.5–2.0 Å band registered on the smaller leg σ — the
direction AMENDMENT 4 §4.3 predicted, now with a number. Validity is intact: the exact false-positive rate of
the 3-vs-5 design is **2/56 = 0.0357**, computed from the p-lattice rather than simulated
(`exact_size_under_exchangeability`), and the simulation lands on exactly that. The test is valid; it is blunt.

*(Method note, because it looked like a defect first: a 1,200-draw Monte-Carlo read the balanced-n = 3 size as
0.0625 against an exact bound of 4/84 = 0.0476. Three 20,000-draw seeds returned 0.0470 / 0.0475 / 0.0490. It
was Monte-Carlo error, and the artifact now carries the exact lattice figure so nobody has to re-diagnose it.)*

### 1c · ★ The finding that reframes the question: **resolution is affordable, and that is the problem**

If the true paralogue difference really is the size this panel measured, how much would resolving it cost?
Derived (normal approximation, labelled as one, and a **lower** bound on what the exact rule needs — see
`price_of_resolving_the_OBSERVED_effect` and its `normal_approximation_cross_check`):

| target | models/arm for 80 % power | legs | plan $ | range $ |
|---|---|---|---|---|
| NR4A1-vs-NR4A3 at the observed 0.4124 Å | **77** | 308 | **$48.58** | $20.10 – $122.45 |
| primary contrast at the observed 0.2825 Å | **123** | 738 | **$116.40** | $48.19 – $293.41 |

*(Both rows are lower bounds twice over: the normal approximation is optimistic against the exact discrete
rule, measured — at the δ it calls "80 % power", the exact permutation test actually delivers **0.64 / 0.67 /
0.72 / 0.74** at n = 3 / 4 / 5 / 6. So the real n is larger and the real cost higher; the point survives.)*

**"We cannot afford the resolution" is therefore FALSE and must not be written.** What those dollars buy is a
statistically resolved *sub-Ångström difference in an interface-RMSD plateau* — and the prereg's own claim
ceiling (§6) permits only **directional concordance** from that endpoint, because **no quantitative link
between the E1 plateau and degradation selectivity has ever been established**. Buying resolution on an
uncalibrated readout buys a precise number nobody can interpret.

That is the whole argument for the recommended sequence: **the missing thing is calibration of the readout, not
statistical power.**

---

## 2 · The options

Costs are `reference GPU-hours × the planning rate` — the same derivation `vast-ladder-repricing.json` uses, so
a ladder reprice moves them. The only basis this document introduces is the **endpoint-MD leg = 1.38
ref-GPU-h** (`vast_cost_model.ENDPOINT_MD_REF_GPU_H_PER_LEG`, itself backed out of the covalent feasibility
panel's completed price ledger — see pricing.md §B). **C1 is not re-derived at all** — Arm F is an existing
ladder stage and its row is read from
the ladder, because deriving a second figure for the same work is the one-fact-one-place bug. Co-fold
*generation* is **not** derived either — its one home is pricing.md §B's `Co-fold / docking` basis, carried
there as **ESTIMATED ~$0–50 per batch**, and it is never summed into a derived total.

| # | option | legs | plan $ | range $ | >$50 gate | attacks |
|---|---|---|---|---|---|---|
| **A1** | restore NR4A3 to n = 3 models | 2 | **$0.32** | $0.13 – $0.80 | no | structural + noise |
| **A2** | balanced n = 6 models/arm | 20 | **$3.15** | $1.31 – $7.95 | no | structural + noise |
| **A3** | balanced n = 10 models/arm | 44 | **$6.94** | $2.87 – $17.49 | no | structural + noise |
| **B1** | 4 replicas/model (same 8 models) | 16 | **$2.52** | $1.04 – $6.36 | no | **noise only** |
| **B2** | 6 replicas/model (same 8 models) | 32 | **$5.05** | $2.09 – $12.72 | no | **noise only** |
| **C0** | re-derive E2/E3/E4 signal-to-noise from the **16 landed legs** | 0 | **$0** | $0 | no | readout selection |
| **C1** | ternary ΔΔG_coop (Arm F) as the readout | *ladder stage* | **$20.00** | $4.64 – **$72.60** | **YES** | readout — but **BLOCKED** |
| **C2** | buried-surface-area / sidechain-contact readouts | 16 | **$2.52** | $1.04 – $6.36 | no | readout (needs a re-run) |
| **D1** | endpoint-MD **positive control** on SMARCA2-vs-SMARCA4 | 24 | **$3.79** | $1.57 – $9.54 | no | **the missing control** |
| **D2** | endpoint-MD positive control on IKZF1-vs-IKZF3 | 24 | **$3.79** | $1.57 – $9.54 | no | the missing control |
| **E1** | paired (matched-model) design + sign-flip test | 0 | **$0** | $0 | no | noise + reference set |
| **E2** | **reallocate the same budget**: 1 replica × more models | 0 | **$0** | $0 | no | **structural, free** |
| **E3** | parametric test instead of exact permutation | 0 | **$0** | $0 | no | structural |
| **F1** | a second co-fold **architecture** as a model source | 0 | **$0** | $0 | no | structural |

Full per-option `buys` / `cannot_buy` text is in the artifact's `options[]`. The load-bearing parts:

### A — more MODELS *(structural **and** noise; the honest baseline)*
`n` enters both the reference set and the power, so this is the only lever that moves both. At n = 6/arm the
NR4A1-vs-NR4A3 pairwise floor drops from 0.10 to **0.0011** and primary power at a 1.5 Å true separation rises
from 0.44 to **0.89**. **It cannot buy** any change in the endpoint's effect-size-to-noise ratio: at n = 6 the
pairwise still has only **0.19** power against a 0.5 Å separation — and the separation this panel actually
observed is smaller than that. Add co-fold generation (estimate, above).

### B — more REPLICATES *(noise only — and barely)*
⛔ **Cannot move ANY reference set. NR4A1-vs-NR4A3 stays at C(5,3) = 10, min attainable p 0.10 > α —
structurally unresolvable at any replicate count**, which the frozen scorer demonstrates at 100 replicas/model.
And the noise it *can* buy is capped at a 19 % σ reduction (§1a). **This option should not be bought.**

### C — a different READOUT
- **C0 ($0) is the cheapest real information in this document.** `nrv04_covalent_md` writes
  `R1_interface`, `R2_recruitment` **and** `R3_lys` into every leg JSON, and the frozen collector reads only
  R1 — the criteria audit records E2 as *"computed_by_the_frozen_scorer? **NO** — STABLE_PLATEAU_A is imported
  and unused"*. So **three additional endpoints already exist for all 16 landed legs and have never been
  looked at.** Measuring their separation-to-noise costs one CI job.
  ⛔ It **cannot buy a result**: choosing an endpoint on the same data that will then test it is
  endpoint-shopping. It is a **calibration input to a new preregistration**, tested on new models.
  ⚠ **Precondition:** an S3 census must confirm those 16 leg JSONs (and the analysis trajectories) are
  actually present. An absent reading is not a reading of absence — one committed forensic listing shows
  `traj_*.f32` + `traj_*.traj.json` for the single unit it covers, and that is not evidence about the other 15.
- **What the persisted trajectories do and do not support.** `md_analysis_traj.select_analysis_atoms` persists
  **every protein CA, every Cys SG, every Lys NZ and every non-polymer heavy atom** — so contact-count series,
  rigid-body drift, alternative interface-RMSD definitions, ligand pose drift and Lys presentation are **$0
  re-derivations**. It does **not** persist sidechain heavy atoms, and says so. **Buried surface area and
  sidechain-contact lifetimes are therefore NOT re-derivable** — that is option **C2**, a full re-run with
  `TRAJ_ALL_HEAVY=1`, at the price of the panel.
- **C1 (ternary ΔΔG_coop) is blocked, not merely expensive.** Prereg §1 and calibration addendum condition 7
  hold Arm F behind a valB PASS, and valB module 1 returned **NO**; STRATEGY Open decision 9 (2026-07-30)
  decided *not* to amend that gate. Unblocking it is a preregistration decision, not a spend decision. Its
  range top ($72.60) also crosses the >$50 reviewer gate — the only option here that does.

### D — a different POSITIVE CONTROL *(the option that addresses the actual problem)*
The gap is not "the NR-V04 panel was too small". It is that **no experiment has ever shown this readout can
detect paralogue selectivity where the answer is known.** The `$0` S-calibrator survey
([`s-calibrator-survey.json`](./s-calibrator-survey.json)) screened ten paralogue pairs for a deposited
**ternary on both arms** and found exactly two symmetric ones: **SMARCA2/SMARCA4** (15 / 4 ternaries) and
**IKZF1/IKZF3** (10 / 4). Both avoid the configuration that weakens the incumbent alchemical calibrator — a
modelled arm opposite a real one.

- **This is NOT valB_full module 3.** That module is an *alchemical cooperativity* module behind the valB gate.
  D1 is the **endpoint-MD lane at endpoint-MD prices**, asserts **no free energy**, and is therefore outside
  what condition 7 licenses or withholds — the same argument the prereg's own
  [§9 RESOLUTION](./nr4a3-nrv04-retrospective-prereg.md) used to run Arm E. If trimcrae reads that argument as
  not carrying here, D1 falls and the sequence stops at step 1.
- ⛔ **What D1 cannot buy:** anything about NR4A. A pass licenses *"the readout discriminates a known
  paralogue pair"* — nothing more. And a **fail is ambiguous** between *"the readout is blunt"* and *"this
  pair is hard"*, which is why the shape below is chosen to be adequately powered before it runs.
- ⚠ **Open precondition 1 — the reference number.** A positive control needs a **measured, primary-source**
  selectivity value, and STRATEGY Open decision 7 binds: *the accuracy band may not be wider than the signal
  being calibrated*. The survey explicitly does **not** supply one (`selectivity_kcal: null`,
  `needs_primary_source_verification: true`) for either pair. That verification is a **$0 literature step and
  it must precede the spend**, because it decides whether the pair's true separation is inside this design's
  detectable range at all.
- ⚠ **Open precondition 2 — "SYMMETRIC" does not mean a matched-ligand crystal PAIR.** It means a deposited
  ternary exists on each arm. STRATEGY Open decision 9b measured why that distinction bites: the ligand whose
  reference data we would calibrate against was co-crystallised **only with SMARCA4**, and every deposited
  SMARCA2 ternary carries a **different ligand**. From crystals alone the arms can be matched on *ligand* (one
  arm modelled) or on *protein* (ligand confounded with paralogue), not both. An endpoint-MD panel escapes
  that only by **co-folding one ligand onto both real paralogue sequences** and using the deposited ternaries
  to *validate* each arm's co-fold rather than to supply it. That is a preregistration decision, not a launch
  flag. Related: `smarca2_model.py` exists but builds SMARCA2 by **homology mutation from the 3.73 Å 8G1Q
  SMARCA4 chain** — the very asymmetry this option exists to avoid — so new staging is required. Engineering
  is free; the point is that it is not already built.

### E — a different STATISTIC or DESIGN
- **★ E2 is the highest-value $0 finding here.** The as-run panel spent 6 legs per arm as **3 models × 2
  replicas**. Spending the *same six legs* as **6 models × 1 replica** changes the pairwise floor from **0.05
  to 0.0011** and, at a 1.0 Å true separation, raises power from **0.34 → 0.50** (primary) and **0.26 → 0.39**
  (pairwise) — because the n gain beats the noise loss (σ_model rises only 1.0278 → 1.1924 Å). **Same legs,
  same dollars.** ⚠ **The price is not money.** AMENDMENT 4 §4.2's exclusion was checkable *because* replicas
  exist: both replicas of nr4a3 seed_3 failed while both replicas of every other co-fold produced frames, and
  *"a thermostat seed cannot rescue two atoms at 0.181 Å"*. At one replica per model there is no sibling, so an
  input fault and a host-side death stop being distinguishable from the run record. That trade must be
  preregistered, not discovered.
- **E1 paired design:** cancels the dominant between-model variance, but its reference set is the 2ⁿ sign
  flips — **2³ = 8, a floor of 0.125, strictly worse than the unpaired C(6,3) = 20** — and it only overtakes at
  n ≥ 5. It also has a precondition: the arms are currently **protocol-matched but not placement-matched**
  (prereg §2a/§2c LIMITATION, 2026-07-31), so pairing must be built into co-fold generation.
- **E3 parametric test:** removes the combinatorial floor entirely. ⛔ **Not admissible now.** Swapping the
  test after a failed result, on the same data, is precisely the retune AMENDMENT 1's standard forbids — and
  n = 2–3 does not support a normal approximation, which is *why* the prereg chose exact permutation. Only as a
  preregistered primary on a new panel, with its own false-positive rate measured first.

### F — new capability from method-watch
**Honest "not yet".** No watched capability *measures* paralogue selectivity; the row that would change this
answer — *"reliable structure-based generative + selectivity scoring"* — has **not fired**. What *has* landed
is useful only as a **model source**: DeepTernary / Protenix / IntFold give co-folds whose independence is
*architectural* rather than a diffusion seed, which is closer to what prereg §4a's unit of independence
actually assumes. [method-watch.md](../method-watch.md) is explicit that generator scores never rank
selectivity, so F1 can enlarge a reference set and can do nothing else.

---

## 3 · Recommended sequence — serialized, because each step can cancel the next

CLAUDE.md §6's litmus test is *"is there a result this step could return that would make me NOT run the rest?"*
**Yes, twice.** So this is serial by decision value, not by physics.

| step | what | legs | plan $ | cum. range $ | could cancel the rest? |
|---|---|---|---|---|---|
| **1** | re-derive E2/E3/E4 separation-to-noise from the 16 landed legs, + the S3 census | 0 | **$0** | $0 | **yes** |
| **2** | positive control: the chosen readout on a known-selective, structure-matched pair — 2 arms × 6 models × 2 replicas | 24 | **$3.79** | $1.57 – $9.54 | **yes** |
| **3** | re-panel NR4A1/2/3 on the validated design, freshly preregistered — 3 arms × 6 models × 2 replicas | 36 | **$5.68** | $3.92 – $23.85 | no — runs **only if step 2 passes** |

**Total: $9.47 plan, range $3.92 – $23.85** (derived, `recommended_sequence`), plus the co-fold generation
estimate. **Inside the ≲$50 autonomy threshold at every step and in total.**

Why this order:
1. **Step 1 is free and can delete a whole branch.** If E1 is the best endpoint we already own and everything
   else is worse, the "different readout" option space collapses for $0. If a contact-based endpoint separates
   at 2–3× the effect-to-noise of E1, the entire design changes before a dollar is spent.
2. **Step 2 is the actual gap.** A null there — on a pair with a *known* answer, *solved structures on both
   arms* and a reference set with a 0.0011 floor — says the readout cannot detect paralogue selectivity at all.
   In that case step 3 is money spent to reproduce a failure, and the honest paper reports predicted
   selectivity as unvalidated.
3. **Step 3 only then**, freshly preregistered, with power and reference sets fixed before the data.

**Do NOT fan out.** Steps 2 and 3 are the same lane and the same price whether run in series or parallel, so
parallelism buys only wall-clock — and step 2 is precisely the result that could stop step 3 being bought.

Adopt **E2** *(reallocate replicas → models)* only as a preregistered choice inside step 3's design, with
§4.2's auditability loss written down; **B1/B2 should not be bought at all**; **C1** stays behind its gate;
**A3** is dominated by step 3 unless step 2 passes *and* the effect turns out large.

### Two cost facts that matter more than any of the above
- The retrospective's realised mean was **$0.0979/leg over 17 measured legs** with a **$1.57** projected panel
  total ([`nrv04-retro-price-forensics.json`](./nrv04-retro-price-forensics.json) → `ledger_summary`), against
  the $0.158/leg this planning rate derives — **the plan figure is the conservative one**.
- ⚠ **The same ledger records `leaked_usd` = $25.83 against $1.57 of compute.** On this lane the dominant
  cost has been *supervision*, not GPU-hours, and **no design choice in this document touches that.** Any of
  these options costs more in unattended rental than in science if the fleet is not watched.

---

## 4 · The legitimate alternative outcome, stated plainly

**"No achievable in-silico design resolves this, and the paper reports predicted selectivity as unvalidated"**
is a legitimate result and is better than an expensive design that still cannot reach α. On the evidence here
it is **not yet** the right call — step 1 is free, and step 2 is $3.79 for the positive control the program has
never had — but it becomes the right call the moment **step 2 returns a null**. It should be written that way
in advance, so it cannot later be re-narrated as a method failure:

> Run identically and without tuning on a known-selective paralogue pair with solved structures on both arms,
> at a design whose reference set can reach α, the ensemble endpoint workflow did not discriminate them. The
> workflow's paralogue-discrimination authority therefore rests on nothing this program has measured, and the
> NR4A3 selectivity predictions are reported as **unvalidated predictions**.

That is stronger science than a resolved sub-Ångström plateau difference on a readout with no established link
to degradation — which §1c shows is purchasable for ~$49–$116 and would still not license a selectivity claim
under prereg §6.

---

## 5 · What this document deliberately does not do

- **It launches nothing and spends nothing.** Every figure is derived from committed artifacts.
- **It amends no preregistration**, proposes no criterion change, and re-scores no landed leg. §1b's power
  figures are design-planning numbers, explicitly *not* a replacement MDE — AMENDMENT 4 §4.3 declined to
  register one and that stands.
- **It does not re-audit the verdict.** A separate thread owns folding the result into STRATEGY.md, the
  manuscript and the pricing of one power option; this file points at homes rather than restating them.
- **It asserts no selectivity, efficacy, cooperativity or degradation claim**, and nothing here licenses one.
