# NR-V04 retrospective — PREREGISTRATION of the biological holdout (2026-07-24)

> **This is the SCIENTIFIC contract, not the run book.** For state of play, the exact dispatch commands, the
> cost ledger and the operational traps, read
> **[`nrv04-retrospective-handoff-2026-07-24.md`](./nrv04-retrospective-handoff-2026-07-24.md)**. Nothing in
> that file may relax anything frozen here.

**Committed BEFORE any retrospective leg runs.** This freezes — a priori, before any favourable number is
visible — the panel, the starting structures, the protocol, the primary endpoint, the statistical test, the
blinding, the extension rule, the verdict tiers, the honest-failure semantics, and the claim ceiling for the
**NR-V04 retrospective** (nr4a3-program-map.md RUNG 4, schedule id `nrv04_retrospective`).

It sits on top of:
- [`nr4a3-ternary-coop-prereg.md`](./nr4a3-ternary-coop-prereg.md) — the standing ternary prereg (§3d is the
  family-transfer bar this document implements; §6a is the controls list).
- [`nr4a3-ternary-calib-prereg-addendum-2026-07-19.md`](./nr4a3-ternary-calib-prereg-addendum-2026-07-19.md) —
  the valB calibration freeze, whose **condition 7** gates the *quantitative* arm of this retrospective.
- [`nr4a3-nrv04-covalent-feasibility-prereg.md`](./nr4a3-nrv04-covalent-feasibility-prereg.md) — the feasibility
  panel that ran first, and whose **Leg 0** result is the single most important input to this design.

Machine-readable frozen copy: [`nrv04-retrospective-prereg.json`](./nrv04-retrospective-prereg.json).
Enforced by [`nrv04_retro_panel.py`](./nrv04_retro_panel.py) (panel), [`nrv04_retro_blind.py`](./nrv04_retro_blind.py)
(blinding) and [`nrv04_retro_gate.py`](./nrv04_retro_gate.py) (scoring + verdict), with offline unit tests, so no
criterion can be re-decided post-hoc on a favourable result.

**Nothing in this document authorizes a spend by itself.** Every GPU stage is presented at its gate with a
pinned cost (§7).

---

## 0. The known answer, and the confound that reshapes the test

**Known answer (Wang 2024, `nrv04-ternary-benchmark.json` → `ground_truth`):** NR-V04 degraded **NR4A1** and
**spared NR4A2 and NR4A3**, with PLA/co-IP complex evidence and VHL/proteasome dependence. There is **no solved
NR-V04 ternary structure and no paralogue-resolved K_d, α or ΔG_coop** — so the holdout can only ever test
**directional concordance with a functional ordering**, never "recovery" of a measured quantity.

**The confound, and it is measured, not hypothetical.** The feasibility panel's Leg 0
(`nrv04-cys-conservation.json`, CI run 29923279236) established that the celastrol-reactive cysteine
**NR4A1 Cys551 is unique to NR4A1**: the aligned position is **Tyr in NR4A2** and **Thr in NR4A3**, and neither
paralogue has any cysteine within a ±5 window. Celastrol therefore **cannot form the covalent adduct on
NR4A2/NR4A3 at all**.

This changes what the retrospective is allowed to be. Running all three paralogues *non-covalently* and calling
a NR4A1 win "recovering NR-V04 selectivity" would be wrong, and running NR4A1 *covalently* against non-covalent
paralogues and calling it the same thing would be worse — the covalent restraint alone could produce the
ordering. So the panel is designed to **decompose** the phenotype rather than merely reproduce it:

| Contrast | What it isolates | Why it is the honest test |
|---|---|---|
| **R1** NR4A1 vs NR4A2 vs NR4A3, **all non-covalent** | ternary geometry / interface energetics with the warhead-reactivity confound **held off** | This is the only contrast that can tell us whether the *ternary workflow* discriminates NR4A paralogues — which is what a **prospective, non-covalent** NR4A3 degrader campaign would depend on. |
| **R2** NR4A1 covalent vs NR4A1 non-covalent | the covalency component of the phenotype | Quantifies how much of the NR-V04 result is warhead chemistry the non-covalent machinery cannot represent. |
| **R3** epimer arms (conditional) | whether any R1 ordering also appears with a VHL-**inactive** recruiter | If the ordering appears with the inactive epimer too, R1's ordering is not recruitment-specific. |

**Both outcomes of R1 are informative and are pre-committed in §5.** A null R1 is the *expected* result under the
warhead-reactivity explanation; it is not a method failure, and it must not be reported as one.

---

## 1. Scope: two arms, only one of which is authorized now

| Arm | Quantity | Lane | Gate |
|---|---|---|---|
| **Arm E — ensemble endpoint MD** *(this document's subject)* | geometric/ensemble interface readouts (R1–R3 of `nrv04_readouts.py`). **No free energy.** | the proven Vast endpoint-MD lane that ran the 18-leg covalent panel (`nrv04_covalent_md.py`), measured ~$0.43/leg | authorized at §7 pricing; **not** gated on the valB free-energy calibration, because it asserts no free energy |
| **Arm F — alchemical ΔΔG_coop** | per-paralogue ΔΔG_coop via the binary↔ternary cycle (ternary prereg §1) | `run_ternary_leg.sh` / `nr4a3_ternary_fep.py` | **BLOCKED** by calibration addendum **condition 7** — runs only after the valB calibration PASSes. Not launched by this document. |

**This split is the load-bearing honesty of the design.** The valB calibration exists to license *free-energy*
claims; Arm E makes none, so it is not licensed by valB and does not need to be. What Arm E can buy is
correspondingly smaller, and §6 states exactly how small.

---

## 2. Frozen panel (Arm E)

### 2a. Starting structures — one source, verified before use
Every retrospective leg starts from a Boltz-2 co-fold in
`s3://sagemaker-us-east-2-646605541856/nrv04-descriptive-v4/`, inventoried on 2026-07-24 (CI run 30121409280,
`nrv04-cofold-discovery.json`; E3 identity audited in CI run 30122648680). Using **one** co-fold prefix for all
three paralogues is what makes the arms protocol-matched; the `nrv04-covalent-cofold/` and `nrv04-shakeout/`
NR4A1 structures are deliberately **not** mixed in.

> **⚠ SOURCE CHANGED 2026-07-24, BEFORE ANY LEG RAN.** The original plan was to reuse `nrv04-descriptive-v3`.
> The E3 identity audit (CI run 30122648680) measured its chain F at **255 residues = UniProt P62258, 14-3-3
> protein epsilon** — where Elongin B (Q15370, 118 residues) belongs. `nrv04_ternary.py` fetches the
> `ELONGIN_B` constant's sequence directly, and that constant was P62258 until the 2026-07-17 correction; those
> co-folds are dated 2026-07-11. They are not the VHL/EloB/EloC machinery and cannot support a ternary-
> recruitment readout, so the panel's source is the **regenerated `nrv04-descriptive-v4`**. The staging
> assembler independently rejects a 255-residue chain, so the contaminated source cannot be used by accident.
> Full record: [`nrv04-cofold-chain-forensics-2026-07-24.md`](./nrv04-cofold-chain-forensics-2026-07-24.md).

| system | co-fold models available | used here |
|---|---|---|
| `nr4a1` (NR-V04 + VHL/EloBC + NR4A1 LBD) | seeds 1, 2, 3 | **all 3** |
| `nr4a2` | seeds 1, 2, 3 | **all 3** |
| `nr4a3` | seeds 1, 2, 3 | **all 3** |
| `neg_inactive` (Hyp-epimer) | seeds 1, 2, 3 — **NR4A1 only** | R3 only (see §2d) |

### 2b. Legs — 24 GPU legs in the authorized stages
Unit = (arm × co-fold model × MD replica). **3 co-fold models × 2 MD replicas = 6 legs per arm.**

| stage | arm id | ligand | target | covalent | legs |
|---|---|---|---|---|---|
| **R1** (primary) | `retro_noncov_nr4a1` | NR-V04 active | NR4A1 | no | 6 |
| **R1** | `retro_noncov_nr4a2` | NR-V04 active | NR4A2 | no | 6 |
| **R1** | `retro_noncov_nr4a3` | NR-V04 active | NR4A3 | no | 6 |
| **R2** | `retro_cov_nr4a1` | NR-V04 active | NR4A1 | **yes** (C6→Cys551) | 6 |
| **R3** *(conditional, §5d)* | `retro_epi_nr4a{1,2,3}` | Hyp-epimer | each | no | 18 + 6 new co-folds |

The two MD replicas of a model differ by **velocity seed only** (0, 1); the co-fold model is the higher-level
independent unit, and §4 scores it as such.

**No covalent NR4A2/NR4A3 leg exists and none may be added** — Leg 0 showed there is no cysteine to bond to.
Modelling one would be fabricating chemistry.

### 2c. Protocol — identical across every arm, no paralogue gets bespoke treatment
Frozen to the canonical values in [`md_settings.py`](./md_settings.py) (the same settings the covalent
feasibility panel ran, so its legs remain a cross-check):

- 4 fs timestep, 3.0 amu HMR, HBonds constraints, rigid water, 300 K, 1.0 /ps friction
- amber14-all + amber14/tip3p, GAFF-2.11 small molecule, TIP3P, 0.9 nm cutoff
- ligand charges **NAGL**
- **1.0 ns equilibration + 5.0 ns production** per leg, ~10 ps frame cadence
- minimization → velocities at 300 K (seeded by replica) → chunked equilibration with a finite guard → production
- per-frame checkpointing to S3 (`CKPT_EVERY_FRAMES=50`), spot-preemption-safe resume

Any deviation on any single leg **voids that leg**, not the threshold.

### 2d. Controls (ternary prereg §6a)
- **Epimer (VHL-inactive) negative** — R3, conditional (§5d). Its NR4A1 co-folds already exist; NR4A2/NR4A3
  epimer co-folds must be generated first and that generation is itself a gated step.
- **Warhead-only / E3-ligand-only / C551A** — already run in the feasibility panel; **not repeated**. They are
  cited from there, and their cross-panel comparability is limited to the fact that the protocol is identical.
- **Identical analysis and stopping rules for NR4A1/2/3** — enforced mechanically: one code path, one threshold
  set, arms distinguished only by their input structure.

---

## 3. Endpoints (frozen)

All computed by the already-frozen kernels in [`nrv04_readouts.py`](./nrv04_readouts.py) — thresholds were fixed
before the feasibility panel ran and are **not** re-tuned here.

| id | quantity | kernel | role |
|---|---|---|---|
| **E1 (PRIMARY)** | interface-RMSD **plateau** (Å): mean RMSD of the E3∩target interface heavy atoms over the **final 50 %** of production frames, vs the starting interface | `interface_rmsd_stable().plateau_A` | continuous primary endpoint; **lower = more stable** |
| E2 | **stable fraction**: fraction of an arm's legs with plateau < **4.0 Å** | same, `.stable` | binary secondary (⚠ *the motivating observation — "recruiter_active 3/3 vs epimer 1/3 in the feasibility panel" — is **WITHDRAWN** as of 2026-07-24: that panel scored the Elongin C interface, not VHL↔NR4A1. The **endpoint and its 4.0 Å threshold are unchanged** — they were frozen before the panel ran and are not re-tuned here — but E2 no longer has a demonstrated discrimination behind it. See `nrv04-cofold-chain-forensics-2026-07-24.md`; note added 2026-07-25, no threshold touched.*) |
| E3 | mean interface contact count over production | `recruitment().mean_contacts` | secondary. **Known weak discriminator** — the feasibility panel showed co-fold seeds contact in all arms — so it is reported, never gating |
| E4 | Lys-Nζ presentation distance distribution | `lys_presentation()` | **descriptive only, never a gate** (ternary prereg §6.3: no distance cutoff quantitatively predicts degradation) |

**E1 is the primary endpoint and the only one the verdict of §5 turns on.** E2–E4 are reported alongside it in
every result, including when they disagree with E1.

---

## 4. Statistical analysis (frozen)

### 4a. The unit of independence is the CO-FOLD MODEL, not the leg
Two replicas of one co-fold model share a starting structure and are **not** independent. Every test therefore
operates on **model-level values** = the mean of a model's 2 replicas → **n = 3 per arm**.

### 4b. Primary test — one-sided exact permutation, pooled contrast
Statistic: `mean(E1 | NR4A1 non-covalent) − mean(E1 | NR4A2 ∪ NR4A3 non-covalent)`, on model-level values
(3 vs 6). Directional prediction registered here, before data: **negative** (NR4A1 more stable).
⚠ **The next two lines are SUPERSEDED by AMENDMENT 4 (2026-07-31)** — `nr4a3` seed 3 was excluded by
measured input fault, so n is **3 / 3 / 2**, the contrast is 3 vs 5, the reference distribution is
**C(8,3) = 56** and the minimum attainable one-sided p is **1/56 ≈ 0.0179** (still < α). The statistic,
its direction, its endpoint, α and the unit of independence are UNCHANGED; this pointer edits no
criterion, it only stops a retired count reading as current. Retained for the record:
Reference distribution: **exhaustive enumeration of all C(9,3) = 84 arrangements** of the 9 model-level values.
One-sided p, α = **0.05**. Minimum attainable p = 1/84 ≈ **0.012**.

### 4c. Secondary tests
- Pairwise NR4A1 vs NR4A2 and NR4A1 vs NR4A3: exact permutation over C(6,3) = 20 arrangements. **Registered
  limitation: the minimum attainable one-sided p is 0.05**, reachable only under perfect separation. These are
  reported as descriptive support, never as the verdict.
- **Leave-one-model-out (LOMO):** the sign of the primary statistic recomputed with each of the 9 models dropped
  in turn. "Survives LOMO" = the sign is unchanged in all 9 refits.
- **Covalency decomposition (R2):** `mean(E1 | NR4A1 covalent) − mean(E1 | NR4A1 non-covalent)`, reported with
  its LOMO range. No significance test is claimed on n = 3 vs 3.

### 4d. Extension rule (pre-registered, adaptive)
If the primary contrast has the **predicted sign** but **p ∈ (0.012, 0.05]** — i.e. the ordering is right but
n = 3 models cannot resolve it — generate **3 additional co-fold models per paralogue** and re-run R1 at n = 6
models/arm (C(18,6) = 18564 arrangements). This is the *only* pre-authorized extension, it is triggered by the
p-value alone, and it may not be invoked to rescue a **wrong-sign** result.

### 4e. Technical-failure handling
A leg that NaNs / blows up is re-run **once** from a fresh velocity seed. A second failure marks the leg
`technical_failure` and excludes it. If an arm loses **more than one** leg, that arm is reported
**underpowered** and the verdict is `INDETERMINATE` — a degraded arm may never be quietly compared against
intact ones.

### 4f. No interim analysis
The paralogue contrast is computed **once**, after all R1+R2 legs have landed. Per-leg convergence/liveness
monitoring is permitted (and required, per the tight-monitoring rule); **looking at the arm ordering before the
panel completes is not.**

---

## 5. Verdict (frozen tiers)

Computed by `nrv04_retro_gate.verdict()` from the leg JSONs. Let `d` = the primary statistic (§4b) and `p` its
one-sided permutation p-value.

| tier | criteria (all must hold) |
|---|---|
| **CONCORDANT** | `d < 0` (NR4A1 most stable) **AND** `p ≤ 0.05` **AND** NR4A1's model-level mean is below **both** NR4A2's and NR4A3's **AND** the sign survives LOMO (§4c) **AND** no arm is underpowered (§4e) |
| **WEAKLY CONCORDANT** | `d < 0` and NR4A1 below both paralogues, but `p > 0.05` **or** the sign fails LOMO |
| **DISCORDANT** | `d ≥ 0`, **or** a paralogue's mean is below NR4A1's with `p ≤ 0.05` in the reverse direction |
| **INDETERMINATE** | any arm underpowered (§4e), or a protocol deviation voided legs |

### 5a. What CONCORDANT licenses
Only this: the ensemble ternary workflow, run identically and without tuning on three paralogues, ordered them
**directionally concordantly** with the reported NR-V04 outcome, **with the covalent confound held off**. That
is the GO condition for RUNG 5 in nr4a3-program-map.md.

### 5b. What DISCORDANT means — and what it does NOT mean
Discordance does **not** falsify the ternary-first thesis. NR-V04's selectivity may arise (i) from the covalent
warhead chemistry alone — which Leg 0 shows is *sufficient* to explain it, since NR4A2/NR4A3 lack the cysteine
entirely — or (ii) downstream at ubiquitination rather than at ternary formation. It **does** mean the ensemble
ternary workflow has **not** demonstrated NR4A paralogue discrimination on this holdout, and it must not be
cited as authority for a prospective selectivity claim. The method's paralogue-discrimination authority then
rests **solely** on valB's public paralogue-discrimination module, and the manuscript must say so.

### 5c. The null result that is *expected*, not embarrassing
Because the reactive cysteine is unique to NR4A1, a **null R1 with a strong R2 covalency effect** is a coherent,
publishable answer: it localises NR-V04's selectivity to warhead reactivity. Registering this in advance is what
stops it being re-narrated later as a method failure or quietly dropped.

### 5d. R3 trigger
The epimer arms (and the 6 new co-folds they need) run **only if R1 returns CONCORDANT or WEAKLY CONCORDANT** —
there is nothing to control for if no ordering exists. This is an early-abort, not a de-scope.

---

## 6. Claim ceiling (language discipline)

**Permitted**, and only when the tier supports it:
> *"Run identically across NR4A1/2/3 without tuning, the ensemble ternary workflow was **directionally
> concordant/discordant** with the reported NR-V04 outcome."*

**Forbidden from any amount of this evidence** — these are hard, and the claim linter enforces the vocabulary:
- never a "recovery of degradation" framing; never "reproduced NR-V04 selectivity"; never "validated"
- no ΔΔG, α, cooperativity or affinity claim, and no **quantitative degradation** claim (Arm E computes none)
- no efficacy, safety, therapeutic-window or clinical-readiness language
- no promotion of any compound to "lead"

Standing provenance caveat, repeated in every result: the NR-V04 chemistry in-repo is an **"NR-V04-inspired
representative reconstruction"**, not a verified exact structural match (`chemical_identity.blocker` in
`nrv04-ternary-benchmark.json`); every protein atom comes from a real deposited structure or a recorded
prediction, and nothing is fabricated.

---

## 7. Cost, staging and authorization

Per-leg cost is **MEASURED** (the 18-leg covalent panel, **~$0.43/leg** over a 15-leg S3 price ledger, on Vast RTX 3090 interruptible at `dph_total` ~$0.10–0.21/hr; ~$0.19 converted to a reference 4090 GPU-hour). *(Corrected 2026-07-25 from the ~$0.45 this line carried — the final ledger mean is $0.43.)*

| stage | legs | cost | status |
|---|---|---|---|
| **R1** matched non-covalent paralogue comparison | 18 | **~$8** | the decisive contrast — runs first |
| **R2** covalency decomposition (NR4A1) | 6 | **~$3** | runs with R1 (same fan-out) |
| **R3** epimer specificity control | 18 + 6 co-folds | **~$8 + co-fold** | **conditional on §5d** |
| **R1 extension** (if §4d fires) | +18 + 9 co-folds | **~$8 + co-fold** | conditional on the p-value alone |
| **Arm F** alchemical ΔΔG_coop | 3–4 ternary edges + shared binary/solvent | **~$45–110** | **BLOCKED** on the valB calibration PASS (addendum condition 7) |

**R1 + R2 ≈ $11 total**, inside the standing ≲$50 autonomy threshold, and it is the cheapest contrast that can
kill the whole retrospective. Everything above it is conditional. Provider: **Vast** (RTX 3090 preferred, 4090
fallback) — the lane the endpoint-MD price was measured on.

**Sequencing discipline:** pilot **one** leg to completion first (validate the paralogue staging on a structure
the assembler has never seen — NR4A2/NR4A3 co-folds have only ever been read by the co-fold reporter, never by
the MD assembler), then fan out the remaining 23. Once the pilot proves the lane, there is no short-circuit
value left in serializing, so the rest go **fully parallel**.

---

## 8. Blinding (and an honest statement of its limits)

- Leg outputs are written under **opaque arm tokens** (`nrv04_retro_blind.py`, deterministic salted map), so any
  manual inspection of results during the run is arm-blind.
- The **scoring is mechanical**: `nrv04_retro_gate.verdict()` consumes leg JSONs and emits the tier with no
  analyst discretion. It is committed, with unit tests, **before any leg runs** — git history is the proof.
- **Limitation, stated plainly:** this is a single-operator study, so blinding is **procedural, not adversarial**
  — the operator who generates the token map could in principle invert it. The real guarantee is not the
  blinding; it is that the criteria, thresholds, test, and code are frozen in git before the data exist. The
  blinding reduces incidental bias during monitoring; it does not make this a blinded trial, and the manuscript
  must not describe it as one.

---

## 9. Dependency honesty — what this holdout is running ahead of

nr4a3-program-map.md RUNG 4 lists `nrv04_retrospective` as gated on **valB_full + feasibility + step1_fanout**, and
calibration addendum condition 7 says the NR-V04 retrospective runs only after the calibration PASSes. As of
2026-07-24 **only the feasibility panel is complete**; valB is still the live front and step1_fanout has not run.

This document therefore **narrows** the retrospective rather than jumping its gate:
- The arm those gates govern — **Arm F, the free-energy arm** — is **not run** (§1). Condition 7 is respected as
  written.
- The arm that runs now — **Arm E** — asserts no free energy, so the calibration is not what would license it;
  its authority is bounded by §5a/§6 accordingly, and it is reported as an **ensemble-geometry holdout**, not as
  a validated cooperativity result.

If that narrowing is judged insufficient, the correct remedy is to hold Arm E until valB passes — not to run it
and describe it as more than it is.

---

*Frozen 2026-07-24, before any retrospective leg ran. Amendments must be dated additions to this file, never
silent edits to a criterion.*


---

## AMENDMENT 3 — 2026-07-25 (dated defect-fix; trimcrae-delegated, APPLIED)

**Authority.** §7's freeze and nr4a3-program-map.md's requirement that amending a preregistered rule be an explicit,
dated, reviewer-approved defect-fix. The frozen text above is left **unedited**.

**Standard applied (AMENDMENT 1's):** a rule may be amended only if its statistic is shown to lack
discriminating power, demonstrated independently of whether we liked the answer it gave. All four findings
below were measured **before any retrospective leg ran**, so no result exists to have liked or disliked.

**Defect 1 — the R2 arm is unbuildable on every available input.** `retro_cov_nr4a1` declares the C6→Cys551
adduct. Measured at the preregistered site on the exact pinned models
(`nrv04-descriptive-v4/nr4a1/seed_{1,2,3}`): **34.42 / 29.87 / 39.11 Å**, against A1's 8.0 Å limit, so
`nrv04_covalent_md.build_system` raises. This is the same finding as covalent-panel AMENDMENT 2, on
independent models: no predictor in this pipeline — unconstrained, re-seeded, E3-free or steered — seats
celastrol against C551. It is also **blocking**: the raise happens before a leg JSON is written, so the 6
units never land, `panel_complete` stays False and §4f suppresses the R1 contrast permanently — leaving R2
in the panel does not merely cost an arm, it costs the primary result. **Ruling: R2 is RETIRED**, and with
it §5c's registered composite outcome. The
covalent confound is documented from **Leg 0** (sequence) and **Zhang 2018** (literature), never from a
simulation this program ran. The authorized panel becomes **R1 only, 18 legs** — *that count is
SUPERSEDED by AMENDMENT 4 (2026-07-31): 16 legs. This defect-1 ruling itself stands unchanged (R2 is
still retired); only the R1 leg count moved, because `nr4a3` seed 3 was later excluded by measured
input fault. Retained for the record.*

**Defect 2 — the §4d extension rule cannot fire in its stated case.** Attainable p-values are k/84. The
window (0.012, 0.05] contains exactly {0.0238, 0.0357, 0.0476}, all ≤ α and therefore already CONCORDANT;
the smallest attainable p above α is 0.0595, outside the window. **Ruling: the window becomes
`(0.05, 0.12]`** — the right-sign-but-unresolvable band the rule's own text describes, i.e. p ∈ {5…10}/84 —
and it remains triggerable by the p-value alone and unavailable to a wrong-sign result.

**Defect 3 — the LOMO clause is inert.** 228,543 configurations reached p ≤ α with the correct ordering;
zero failed LOMO. **Ruling: LOMO is retained as a REPORTED robustness diagnostic and removed from the
CONCORDANT tier's conjunction**, which it cannot affect. The WEAKLY_CONCORDANT branch predicated on it is
struck as unreachable.

**Defect 4 — no minimum detectable effect was registered, and §5c depends on one.** Measured leg-to-leg
σ = 0.855 Å; MDE at 80 % power = **1.5 Å (optimistic, σ_model = 0) to 2.0 Å**. **Ruling: the MDE is
registered**, and §5b/§5c are narrowed: a null R1 licenses *"the workflow did not resolve a paralogue
difference of the magnitude this design can detect (≥ ~1.5–2.0 Å in interface-RMSD plateau at n = 3
models/arm)"* and **may not** be reported as localising NR-V04's selectivity to warhead reactivity. That
localisation stands on Leg 0 and Zhang 2018 and is stated as such.

**Does this amendment rescue a failing result? NO — stated as the integrity test.**
1. **No result exists.** Not one retrospective leg has run; there is no outcome for any of this to flip.
   Every criterion changed here was assessed by enumeration or against the *sibling* panel's noise.
2. **None of the four can convert a fail into a pass.** Defect 1 **removes** an arm (strictly less evidence,
   strictly less spend). Defect 2 alters only whether *more data is generated* — `extension_triggered` is a
   separate field that `nrv04_retro_gate.verdict` never reads when assigning a tier; the corrected window
   fires on p > α, which is precisely the region that is **not** CONCORDANT, so it can only add work to
   ambiguous results, never promote one. Defect 3 removes a condition that has been shown incapable of ever
   being false when the others hold — the CONCORDANT set is **unchanged** by construction. Defect 4
   **restricts** what a null may claim.
3. **The primary contrast, its direction, its α, its endpoint, its threshold and its unit of independence
   are all untouched.**

**Honest statement of what this LOOSENS and what it TIGHTENS.** Defect 2 is a **loosening in form** — it
makes an extension reachable where it previously was not — but it buys no claim: an extension only ever adds
models and re-runs the same frozen test at larger n. Defects 1, 3 and 4 all **tighten**: one arm is deleted,
one tier condition is demoted to a diagnostic (removing a clause that could never bite is neutral to the
verdict and honest about the tier's real content), and the null's licensed claim is narrowed. Net: the
retrospective can claim **less** after this amendment than before it.

---

## §9 RESOLUTION — 2026-07-30 (dated addition; trimcrae go). Arm E RUNS. No criterion is amended.

**This is not an amendment.** §9 posed the question and named both remedies; it did not decide between them.
The decision is now taken and recorded here, which is what §9's own instruction ("dated additions to this file,
never silent edits to a criterion") asks for. **Every frozen criterion, the primary contrast, its direction, α,
endpoint, threshold and unit of independence are untouched.**

**What was decided.** Arm E — the matched non-covalent paralogue comparison, R1, 18 legs *(count SUPERSEDED by AMENDMENT 4, 2026-07-31: 16 legs)* — **runs**. Arm F, the
free-energy arm, **stays blocked** on the valB calibration PASS exactly as §7 and addendum condition 7 say. The
narrowing §9 describes is accepted as sufficient rather than the alternative it offered ("hold Arm E until valB
passes").

**Why, and the reasoning is §9's own.** The gates that nr4a3-program-map.md RUNG 4 listed govern a *free-energy*
quantity. Arm E asserts no free energy: it is an endpoint-MD geometric contrast reported in Ångström, with its
own registered MDE (leg-to-leg σ **0.855 Å**, 80 % power only at 1.5–2.0 Å) and its own claim ceiling of
**directional concordance only** (§5a/§6). A calibration of the ternary-FEP cooperativity lane is not what
would license it, and is not what its absence withholds. What has changed since 2026-07-24 is only the
factual premise §9 was written against: `step1_fanout` has since **completed**, and the feasibility panel has
been **WITHDRAWN** rather than merely delayed — so two of the three listed gates are no longer *pending*, they
are unreachable, and "held" had quietly become "abandoned without saying so".

**⚠ THE INTEGRITY TEST, STATED BECAUSE THIS IS THE SHAPE OF THE RETUNE THIS PROGRAM FORBIDS.** Loosening a gate
after a failing result is exactly what AMENDMENT 1's standard exists to prevent. It does not reach here, for a
reason that is checkable rather than rhetorical: **the retrospective has never run, so there is no result this
decision could have been motivated by disliking.** Nothing about the verdict this panel will return is known to
anyone at the time of writing. That is precisely the distinction from STRATEGY Open decision 9, where a real NO
existed on valB module 1 and the gate was correctly left standing.

**A HARD PRECONDITION, and it is met.** The shared driver (`nrv04_covalent_md`) had no trajectory reporter at
all until 2026-07-30 — it reduced in-loop and discarded positions, which is why the parent covalent panel's
three analysis defects cost a full re-run instead of a $0 re-derivation. `md_analysis_traj.py` is now wired into
it, persisting an analysis-atom trajectory (every CA, every Cys SG, every Lys NZ, every non-polymer heavy atom)
and mirroring it to S3 on the existing per-checkpoint hook. **Do not launch these 18 legs on a build that lacks
it**; the whole value of a holdout is that its result can be re-derived rather than re-bought.

**Sequencing is unchanged and still binding:** pilot **one** leg to completion first (§7), then fan out.

---

## §2a/§2c LIMITATION — 2026-07-31 (dated addition). The t = 0 starting-structure asymmetry. **No criterion is amended.**

**What this is, and what it deliberately is not.** The pre-spend audit
([`nrv04-retrospective-prespend-audit-2026-07-25.md`](./nrv04-retrospective-prespend-audit-2026-07-25.md) §4,
§6 gate 3) measured a starting-structure asymmetry across the R1 arms and asked for **either** a dated
registered limitation **or** a preregistered admissibility criterion on ligand placement. **The limitation is
what is registered here.** No new admissibility rule is invented, no model is excluded, no threshold is set,
and nothing about the panel, the endpoint, the direction, α or the unit of independence changes. Inventing a
placement criterion at this point would be a *new* preregistered gate written by the same hand that has seen
the starting structures — which is precisely the shape of decision this program refuses to make informally.

**The measurement, cited from its home rather than restated.** Every per-model figure lives in the audit's §4
table (warhead↔target and warhead↔E3 contact counts at 4.5 Å and minimum warhead–target distances, on all 9
pinned `nrv04-descriptive-v4` models, measured with the same kernels the assembler and driver use). Two facts
from it are load-bearing for how a result may be read:

1. **The asymmetry runs AGAINST the registered hypothesis direction.** The two **spared** paralogues begin
   with the warhead **more** engaged with their own target, and **less** draped over the E3, than the
   **degraded** paralogue does. The prereg predicts NR4A1 will be the *more stable* arm; the starting
   structures, if anything, favour the paralogues on the same axis.
2. **The designated pilot unit starts inside a hard clash.** `nrv04-descriptive-v4/nr4a2/seed_1` — the
   `retro_noncov_nr4a2` m1 leg that `retro_units_to_run()` pilots — carries a **1.05 Å** heavy-atom
   warhead–target overlap, well inside a covalent bond length. Minimization must resolve that clash, and that
   relaxation will dominate its early interface RMSD.

**Why §2a/§2c does not already cover it.** Those sections ground protocol-matching in "one co-fold prefix, one
code path". That is a statement about the **procedure**, and it is true. It is not a statement about the
**structures**, which are independent Boltz-2 diffusion outputs and are not matched to each other in ligand
placement. The arms are protocol-matched and *not* placement-matched, and until now only the first half was
written down.

**What this does to the interpretation, stated in both directions before the data exist.**

- **A NULL R1 is weakened as evidence about ternary geometry.** It was already bounded by the registered MDE
  (AMENDMENT 3 defect 4). It is now additionally confounded: a difference this design would have needed to
  detect could be masked by a t = 0 asymmetry pointing the other way. A null therefore licenses only what
  AMENDMENT 3 already permits — *"the workflow did not resolve a paralogue difference of the magnitude this
  design can detect"* — and may **not** be read as evidence that no such difference exists.
- **A POSITIVE (CONCORDANT) R1 is NOT explained away by this, and that asymmetry between the two cases is the
  point.** The starting structures are tilted **against** the registered direction, so a concordant result is
  obtained *despite* the tilt, not because of it. The honest weakening of a positive is different and
  narrower: because the arms differ in starting placement, a concordant result cannot be attributed to
  *ternary interface energetics alone* — relaxation from a different starting placement is an alternative
  mechanism for the same ordering, and any CONCORDANT report must say so. This does not license a stronger
  claim than §5a and §6 already allow; it adds a caveat to that claim.
- **The pilot leg's own E1 is expected to be atypical** and must not be used to form an impression of the arm
  ordering — which prereg §4f forbids in any case. Its purpose is to prove the staging path, not to preview a
  result.

**This is not a retune, on the same checkable test §9's resolution used.** No retrospective leg has run and no
outcome is known to anyone, so there is no result this limitation could have been written to accommodate. It
also only ever **subtracts**: every clause above narrows what a result may be reported as, and none widens it.

---

## AMENDMENT 4 — 2026-07-31 (dated defect-fix; trimcrae DECIDED, APPLIED). The panel becomes **16 of 18**.

**Authority.** §7's freeze and nr4a3-program-map.md's requirement that amending a preregistered rule be an explicit,
dated, approved defect-fix. The frozen text above is left **unedited**. Structure and standard follow
**AMENDMENT 3**, which retired R2 for this same failure mode and is recorded there as having cost the primary
result if left unfixed.

**Standard applied (AMENDMENT 1's):** a rule may be amended only if the defect is demonstrated independently
of whether we liked the answer it gave.

### 4.1 The defect: two units draw on a co-fold no host can run

`nrv04-descriptive-v4/nr4a3/seed_3` places two heavy atoms on the same point. Both units drawing on it —
**`nrv04retro-retro_noncov_nr4a3-m3-r0`** and **`nrv04retro-retro_noncov_nr4a3-m3-r1`** — are therefore
unrunnable, and while they remain enumerated `panel_complete` can never go true and **§4f suppresses the R1
contrast permanently**. This is AMENDMENT 3 defect 1's mechanism exactly, on a different input.

**The evidence, so a reader can CHECK the exclusion rather than trust it** (`nrv04_pe_stage_probe`, CI runs
30662210714 and 30663617181):

| construction stage | atoms | nr4a3 **seed 3** | nr4a3 seed 1 (control) | apart |
|---|---|---|---|---|
| `protein_after_pdbfixer` | 10,914 | **+2.109005036357692e+15** | +2.08e+05 | **10.0 decades** |
| `protein_plus_ligand` | 11,080 | +2.109005036360151e+15 | +2.17e+05 | 9.99 decades |
| `solvated` | ~316,000 | +2.108844375741770e+15 | −4.05e+06 | 8.72 decades |

- **Worst heavy-atom contact: `A:GLU13:O` / `A:LYS181:NZ` at 0.181 Å.** `NonbondedForce` carries the
  +2.109e15 kJ/mol; the bonded terms are unremarkable, so this is geometry, not connectivity.
- **Both clashing pairs under the cutoff are co-fold heavy atom vs co-fold heavy atom** — atoms Boltz placed,
  before our preparation touches the structure.
- **Ligand placement and `addSolvent` are EXONERATED.** Adding the ligand moves the energy by ~2,459 kJ/mol
  out of 2.1e15 (the 12th significant figure); solvation *decreases* it, and is the step that takes the
  system from ~11 k to ~320 k atoms. The divergence is fully formed before either runs.
- **The probe measures the real failure, not a lookalike:** its `solvated` figure reproduces the production
  leg's own recorded `pe_pre_min = +2.108844e+15` to **ten significant figures**.
- Consequence in the run: `blew_up=true`, `blow_phase="prod@frame0/5"`, `n_frames=0`, `prod_wall_s≈4.4 s`,
  `openmm.OpenMMException: Particle coordinate is NaN` — on every host, every time.

### 4.2 The exclusion is by MEASURED INPUT FAULT, not by outcome

This is the line that answers a selection-bias objection, and it is checkable:

1. **The fault is a static property of the input**, present in the built system *before minimization* and
   provable **before any MD is interpreted**. No endpoint, no E1 value, no arm contrast enters the decision.
2. **The replicate structure is what makes the claim testable.** §2b's `MD_REPLICAS` are *velocity seeds
   within a co-fold model* — r0 and r1 share a starting structure. **Both replicas of seed_3 failed at the
   first production step; both replicas of every other co-fold produced real production frames.** A
   thermostat seed cannot rescue two atoms at 0.181 Å, and a fault carried by an input hits every replica
   drawing on it. That asymmetry is the evidence, and it is the discriminator that distinguishes this case
   from the two nr4a2 units that were merely failing (§4.5).
3. **No result was seen, liked or disliked.** These units produced **zero frames** — there is no E1 for them,
   so there is nothing about their outcome to have been unwelcome.

### 4.3 What the panel becomes, and the statistical consequences (all of them)

**Authorized panel: R1 only, 3 arms, `nr4a1`/`nr4a2` models {1,2,3} and `nr4a3` models {1,2}, × 2 replicas =
16 legs.** Model-level n per arm: **3 / 3 / 2** (was 3 / 3 / 3). One home for the enumeration:
`nrv04_retro_panel.EXCLUDED_COFOLD_MODELS` + `enumerate_units`.

| frozen quantity | before | after | status |
|---|---|---|---|
| §4b primary contrast, direction, endpoint, α, unit of independence | — | — | **UNTOUCHED** |
| §4b reference distribution | C(9,3) = **84** | C(8,3) = **56** | mechanical consequence of n |
| §4b minimum attainable one-sided p | superseded: 1/84 ≈ **0.0119** | 1/56 ≈ **0.0179** | still **< α = 0.05** |
| §4c pairwise NR4A1 vs NR4A2 | C(6,3) = 20, min p 0.05 | unchanged | — |
| §4c pairwise NR4A1 vs NR4A3 | C(6,3) = 20, min p **0.05** | C(5,3) = 10, min p **0.10** | **can no longer attain α** |
| §4c LOMO refits | 9 | 8 | — |
| §4d extension window (0.05, 0.12] | reachable | reachable: p ∈ {0.0536, 0.0714, 0.0893, 0.1071} | **survives** |
| §5 verdict tiers, §6 claim ceiling | — | — | **UNTOUCHED** |

**Two consequences stated as losses, because that is what they are.** (a) The NR4A1-vs-NR4A3 pairwise was
already descriptive-only under §4c and now **cannot reach α at all**; it must be reported as such and never
as support for a verdict. (b) AMENDMENT 3 defect 4's registered MDE (≈1.5–2.0 Å at n = 3 models/arm) is
**optimistic for the NR4A3 arm at n = 2**, so power against a paralogue difference is *lower* than
registered. No new MDE is invented here — the honest statement is the direction, and a null R1 is
correspondingly weaker evidence than AMENDMENT 3 already allowed.

### 4.4 Does this amendment rescue a failing result? NO — stated as the integrity test

1. **The excluded units have no result to rescue.** Zero frames, zero endpoints.
2. **It cannot convert a fail into a pass.** It *removes* two legs and one model — strictly less evidence,
   strictly less power (min attainable p rises 0.0119 → 0.0179, one pairwise test loses the ability to reach
   α, and the MDE degrades). Every movement is in the direction of claiming **less**.
3. **The gate was not touched to make it pass.** `panel_complete` goes true because the enumeration honestly
   changed. `nrv04_retro_gate.verdict`, §4f's suppression rule and every threshold are unmodified;
   `retro_collect` additionally reports `panel_completable`, `reachable_units` and `quarantined_units` so an
   unreachable panel can never again read as a panel still in progress.
4. **The primary contrast, its direction, its α, its endpoint, its threshold and its unit of independence are
   all untouched** — as in AMENDMENT 3.

### 4.5 Live dependency — this exclusion may not be the last

Two further units, **`nrv04retro-retro_noncov_nr4a2-m2-r0`** and **`nrv04retro-retro_noncov_nr4a2-m3-r0`**,
have repeatedly failed to bank work and are **not** excluded here, because the same test that condemned
seed_3 exonerates their inputs: the staged probe finds no divergence (nr4a2 seed 2 reaches a **negative**
solvated energy, −3.85e6; nr4a2 seed 3 shows **zero** contacts under the clash cutoff), and each has a
**sibling replica on the same co-fold that landed or is running**. Their failures are therefore not input
faults.

**If either later fails on three genuinely distinct hosts, the reachable set drops again and that requires a
further amendment.** It is not pre-written here. The dependency is made visible so that a shrinking panel can
never happen silently: the distinct-host count is measured (`nrv04_vast_launch.retro_attempt_hosts`) rather
than inferred from an object count, and both units' status is recorded every tick in `nrv04-retro-gate.json`.

**Superseded, retained for the record: the 18-of-18 R1 panel** (AMENDMENT 3's "R1 only, 18 legs"), with
n = 3 models/arm, C(9,3) = 84 arrangements and a minimum attainable p of 1/84 ≈ 0.0119. Registered in
[`pinned-figures.json`](../manuscripts/pinned-figures.json).

---

## §4.5 DEPENDENCY — STATUS RECORD, 8:19 PM ET Fri 2026-07-31. ⚠ **NOT AN AMENDMENT: no frozen quantity moves.**

AMENDMENT 4 §4.5 named two units as a live dependency and required that any further shrinkage of the
reachable set be a further amendment, deliberately not pre-written. One of them —
**`nrv04retro-retro_noncov_nr4a2-m2-r0`** — then reached the trigger FACT: three attempt markers resolving
to three genuinely distinct hosts (`nrv04_vast_launch.retro_attempt_hosts`; hosts `46424247`, `46433424`,
`46435856`, `unreadable_markers: 0`). This section records what that turned out to be, because §4.5's whole
purpose is that a shrinking panel can never happen silently — and a panel that does **not** shrink must be
recorded for the same reason.

**No amendment follows. The authorized panel stays at 16 legs and every quantity in §4.3 is untouched.**
The trigger is a fact about SPEND — the failure breaker refusing to buy a fourth host — not a finding of
unrunnability, and AMENDMENT 4's own §4.2 standard is not met: an exclusion there is by **measured input
fault**, provable before any MD is interpreted, *never* by outcome. Excluding this unit would be exclusion by
outcome, which §4.2 forbids and §4.4 tests against. Three measurements, each from the unit's own artifacts:

1. **Its built system is PHYSICAL — the §4.2 test run in the exonerating direction, on this unit's own
   build rather than inferred from its sibling.** The `run.log` its third host (`46435856`) uploaded records
   `PE pre-min = −3.481e+06`, `post-min = −5.941e+06 kJ/mol` over **344,909 atoms**, and it got there
   normally: `built_…system.xml` (77.5 MB), `…solv.cif` (44.5 MB) and `…built.json` are all in S3, written
   2026-07-31 20:29:44–20:29:54 Z. Its replica sibling `…-m2-r1`, which **landed a conforming production
   leg** off the same co-fold, recorded `pe_post_min_kj = −5,951,528.8` — a 0.18 % difference. This is the
   opposite signature to the units §4.1 excluded, whose energy was positive and ~21 orders of magnitude off.
2. **The hosts did not refuse the work — they ran it, and then their CONTAINERS EXITED.** For `46433424` and
   `46435856` the supervision ticks record `actual_status=exited` followed by
   `[retro-reap] auto-stopped … — terminal-state`. `instance_outbid` excludes `exited` by construction, so
   these are not preemptions and not capacity refusals; the container ran and left, mid-run, with no
   traceback reaching S3. *(The third host's teardown predates the scanned tick window — that is an absent
   reading, not a reading of absence, and it is not counted as anything.)*
3. **That death is LANE-WIDE, not unit-specific.** Across 53 consecutive supervision ticks the same
   afternoon, **24 distinct instances were torn down as `terminal-state`, spread over 13 of the 16 units** —
   including `…-m2-r1`, the sibling that landed anyway, and units inside the 15 that have already landed.
   A failure shared by 13 units, 15 of which completed, is not evidence about this one.

**Why nothing was ever banked, which is what made the breaker fire.** Nothing on this lane is durable until
the first *production* checkpoint. Derived from the sibling's measured `prod_wall_s = 1774.9 s` for 5 ns
(`ns_per_day = 243.4`): the preregistered 1 ns equilibration is ≈5.9 min and the first 50-frame checkpoint a
further ≈3.0 min, so ≈9 min of MD must elapse before any state survives the host. Both evidenced exits fell
**inside equilibration**. So every attempt left zero durable state, the streak anchor could not advance, and
the count reached the threshold while the unit was behaving normally. ⚠ **`CKPT_EVERY_FRAMES` therefore
cannot help here** — there is no production frame yet to checkpoint — and the per-unit override opened for a
different unit must not be cargo-culted onto this one.

**What was done.** The breaker was re-armed by BASELINE (`retro_set_breaker_baseline`, 2026-08-01T00:19:23Z),
never by `leg_failure_breaker.reset_for`, so the attempt archive that carries all of the above is intact.
The re-arm is self-limiting by construction: it buys one more rental, and if that rental banks nothing the
streak grows from the same stamp and the block re-applies at the same count.

**What would change this conclusion.** A measured fault in this unit's *input* — the §4.2 standard, and the
only thing that can justify shrinking the panel. Repeated host-side terminations, however many, are not that;
they are a reason to keep buying carefully or to move tier, and if this unit ever becomes genuinely
unbuyable, that is a spend decision for trimcrae, not a preregistration finding.

One home for the evidence, regenerable and checkable rather than quoted:
[`nrv04-retro-unit-forensics.json`](./nrv04-retro-unit-forensics.json) (`nrv04_retro_unit_forensics.py`) and
[`nrv04-retro-host-history.json`](./nrv04-retro-host-history.json) (`nrv04_retro_host_history.py`).
