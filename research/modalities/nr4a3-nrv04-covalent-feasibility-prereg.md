# NR-V04 covalent feasibility panel — preregistration & scoring freeze

**Rung:** `nrv04_feasibility_covalent` (nr4a3-program-map.md RUNG 3). **Status:** BUILDING (no GPU run until this panel is
built + CI-validated end-to-end — trimcrae decision 2026-07-22: "build fully before any run").
**Provider when it runs:** Vast.ai (bid/interruptible, RTX-4090-class, per-leg S3 checkpoint).

This document is the **frozen** definition of the panel and its GO/NO-GO. It is written BEFORE any GPU leg runs
(reviewer condition 4 requires the scoring rules be fixed in advance). Once a leg has run, this file is
append-only for results; the criteria below do not move.

> **⚠ AMENDED 2026-07-25 — see [AMENDMENT 1](#amendment-1--2026-07-25-dated-defect-fix-trimcrae-delegated) at
> the end of this file. The frozen text below is left UNEDITED so the original rule and the amendment can both
> be read.** In short: **R2** and frozen **criterion 3** are retired as gating criteria — R2 returned the same
> value (`frac_frames_in_contact = 1.0`) on **all 18** legs including both negative controls, so it had zero
> discriminating power and criterion 3 was therefore unsatisfiable, making the gate uninformative rather than
> conservative. `recruiter_epimer` is demoted (it runs as a full ternary, not the binary §3 specifies). A new
> **binding criterion A1 (input admissibility)** is added and **fails now**. ⚠ **A1's figures were CORRECTED by
> [AMENDMENT 2](#amendment-2--2026-07-25-same-day-as-amendment-1-corrects-it) the same day: the 8.99–16.39 Å it
> first quoted are distances to **C566**, not to the preregistered site **C551**, because the implementation
> took the *nearest* of the construct's six cysteines. At C551 the real figures are **28.46–39.11 Å across all
> 34 co-fold models**.** The verdict is unchanged and strengthened (at ~9 Å the gate was nearly passing; it now
> fails closed), §5 criterion 2 stays unevaluable, and AMENDMENT 2 additionally **retires the covalent legs**
> after the re-fold route was run and refuted. The panel remains **`[HELD]`** — neither amendment converts a
> NO-GO into a GO.

---

## 1. Why this panel exists (reviewer condition 4, roadmap → Validation architecture)

Celastrol — the warhead in NR-V04 (Wang 2024) — is reported to bind NR4A1 **covalently via Cys551** (Michael
addition of the thiol to celastrol's electrophilic quinone-methide A-ring). Consequences the panel must confront:

1. NR-V04's observed **NR4A1-selective** degradation (spares NR4A2/NR4A3) may be driven substantially by
   **covalent target engagement**, not only by ternary cooperativity. If the aligned cysteine is absent in
   NR4A2/NR4A3, celastrol simply cannot form the adduct on those paralogues — selectivity would then be a
   *warhead-reactivity* story that the noncovalent free-energy machinery used for cmpd19 does **not** capture.
2. Therefore NR-V04 does **not** validate the noncovalent FEP machinery, and using it as a noncovalent
   calibrator would be wrong.

**The feasibility question (frozen):** *Does covalency swamp the ternary signal, and does a reduced panel of
covalent/noncovalent/control systems behave sensibly?* → GO to the full NR-V04 retrospective (RUNG 4) only if
yes.

---

## 2. Modeling approach — and why it is endpoint-MD, NOT alchemical ΔΔG (frozen)

The panel uses **preformed-endpoint MD + preregistered interface/geometry readouts + a covalent-vs-noncovalent
sensitivity comparison** — it does **not** compute alchemical ΔΔG. Three hard reasons, each verified in the
current code:

- **(a) No covalent path in the wired FEP engine.** `nr4a3_ternary_fep.py` builds `ProteinComponent` and
  `SmallMoleculeComponent` as *separate* components (`_build_components`, `_chemical_systems`); OpenFE's
  `RelativeHybridTopologyProtocol` as wired has no protein–ligand covalent-bond topology. Alchemically morphing
  across a covalent bond is a research problem in its own right, out of scope for a *feasibility* gate.
- **(b) The recruiter edge aborts as a null map.** Active NR-V04 → its VHL-inactive epimer differ **only** by
  the (2S,4R)→(2S,4S) hydroxyproline stereocentre. `assert_constitutional_edge` hard-fails a stereo-only morph,
  so this comparison cannot be an alchemical edge; it must be two **separate endpoint** systems.
- **(c) Feasibility ≠ quantitative validation.** The full quantitative NR-V04 retrospective (converged ΔΔG,
  §3 prereg bars) is RUNG 4 and is *gated on this panel saying GO*. A feasibility gate needs only to show the
  systems assemble, MD is stable, covalency does not qualitatively flip the ternary readout, and the negative
  controls behave. Spending converged-FEP money before that gate is exactly what the reviewer warned against.

**How the covalent bond is modeled (frozen): a RESTRAINED-covalent approximation.** Celastrol is parameterized
as a normal OpenFF small molecule and the protein with its standard force field; the adduct is enforced by a
**stiff harmonic bond restraint** between celastrol's electrophilic C6 and Cys551-Sγ at the C–S covalent length
(~1.81 Å), plus the two flanking angle restraints, holding the Michael-adduct geometry throughout MD. This is the
standard *feasibility-level* covalent treatment: it captures the geometric/entropic consequence of the tether
(the warhead is locked at the site) for the interface-stability and recruitment-geometry readouts (R1–R3),
**without** re-deriving bespoke QM junction parameters. Honest limit: it does **not** reproduce the electronic
reorganization of the true covalent junction and therefore makes **no** affinity/ΔG claim — which is exactly why
this is a feasibility gate, not the quantitative retrospective. The `noncov_nr4a1` leg is identical minus the
restraint, so R4 isolates the effect of the tether itself.

**Honest limits stated up front:** endpoint MD + interface geometry is a *qualitative/semi-quantitative*
readout. It cannot rank affinities. Language throughout is **"directionally concordant / discordant with the
reported NR-V04 paralogue outcome"** — never "recovered degradation." One positive + two spared receptors is too
few to validate a general degradation-ranking model, and we never claim otherwise.

---

## 3. The panel legs (frozen systems)

Naming: `nrv04cov_<leg>`. E3 = VHL·EloB·EloC (from 8G1Q, the existing ternary template). Target LBD = NR4A1
(UniProt P22736) unless noted. "Covalent" = celastrol C6 bonded to the target Cys Sγ (preformed adduct);
"noncovalent" = same pose, no bond.

| # | Leg id | System | Modification | Role |
|---|--------|--------|--------------|------|
| 0 | `cys_conservation` | — (sequence, $0 CPU) | NR4A1/2/3 LBD alignment at NR4A1-Cys551 | **Decisive confound check:** is the reactive Cys present in NR4A2/NR4A3? If absent, covalent selectivity is a warhead-reactivity story, and the panel must say so. |
| 1 | `cov_nr4a1` | NR4A1 + VHL/EloBC + NR-V04 | celastrol **covalently** bonded to Cys551 | Primary covalent ternary model |
| 2 | `noncov_nr4a1` | NR4A1 + VHL/EloBC + NR-V04 | celastrol **noncovalent** (same pose, no bond) | Sensitivity partner of #1 |
| 3 | `cov_c551a` | NR4A1 **C551A** + VHL/EloBC + NR-V04 | bond impossible → run noncovalent | Control: covalent engagement removed; recruitment should weaken vs #1 |
| 4 | `warhead_only` | NR4A1 + VHL/EloBC + **free celastrol** | celastrol covalently bonded to Cys551, **no linker/recruiter** | Negative: no E3-binding moiety → **no** VHL recruitment even with the covalent bond |
| 5 | `recruiter_active` | VHL + NR-V04 (binary) and + NR4A1 (ternary) | active (2S,4R) recruiter | Positive recruiter control |
| 6 | `recruiter_epimer` | VHL + epimer-NR-V04 | inactive (2S,4S) recruiter | Negative: **no** VHL engagement (endpoint system, not a morph) |

Optional paralogue extension (run only if Leg 0 shows the Cys is conserved, i.e. covalency is *not* the whole
story): `cov_nr4a2`, `cov_nr4a3` — same covalent construct on NR4A2/NR4A3 LBDs. Held out of the minimal panel.

---

## 4. Preregistered readouts (frozen — computed identically on every leg)

Per leg: 3 independent replicas (SEED 0/1/2), ≥ `EQUIL_NS` discarded, `PROD_NS` analyzed. Metrics:

- **R1 — interface stability:** heavy-atom RMSD of the ternary PPI interface (E3∩target contact residues) vs the
  starting model, over production. Report mean ± replicate-SD. *Stable* = interface RMSD plateau < 4.0 Å and no
  dissociation (contact count does not decay to 0).
- **R2 — recruitment geometry:** buried surface area (BSA) + heavy-atom contact count across the E3↔target
  interface (4.5 Å), time-averaged. *Recruited* = BSA > 0 sustained over > 50% of production frames.
- **R3 — ubiquitination-compatible presentation:** min distance from any target-surface Lys Nζ to a defined
  E2~Ub catalytic proxy point on the VHL/CRL frame; report the distribution. (Geometry proxy only — no claim of
  transfer.)
- **R4 — covalent/noncovalent sensitivity (the crux):** Δ of (R1,R2,R3) between Leg 1 (cov) and Leg 2 (noncov).
  Small Δ with the same qualitative verdict ⇒ covalency does **not** swamp the ternary readout; large Δ that
  flips the verdict ⇒ it does.

All metrics are computed by the same frozen analysis function on the committed trajectories; thresholds above are
fixed now.

---

## 5. Frozen GO / NO-GO

**GO to the full NR-V04 retrospective (RUNG 4)** iff **all** hold:
1. **Assembles + stable:** every leg (1–6) builds and its MD runs without NaN/blowup; R1 stable on the NR4A1
   covalent and noncovalent legs.
2. **Covalency doesn't swamp:** Leg 1 (cov) and Leg 2 (noncov) give the **same qualitative recruitment verdict**
   (both recruited by R2), i.e. R4 does not flip the outcome. Covalency may *enhance* engagement; it must not be
   the *only* thing holding the ternary together.
3. **Controls behave:** `warhead_only` (Leg 4) shows **no** sustained recruitment (R2 ≈ 0) despite the covalent
   bond; `recruiter_epimer` (Leg 6) shows **no** VHL engagement; `cov_c551a` (Leg 3) shows **weaker** recruitment
   than Leg 1 (covalent engagement demonstrably contributes).
4. **Confound documented:** Leg 0 result is recorded and its implication for paralogue selectivity is stated
   explicitly in the write-up (whether NR4A1-selectivity is partly a warhead-reactivity effect the noncovalent
   machinery cannot see).

**NO-GO / escalate** if covalency qualitatively changes the ternary readout (R4 flips) — then NR-V04 cannot be
represented by the noncovalent workflow at feasibility level, and either the covalent modeling is escalated
(full covalent alchemy) or NR-V04 is demoted further as a calibrator. Either way the finding is reported
honestly, not buried.

---

## 6. Compute shape & cost (calibrate on leg 1; goal: "update the price as you find it")

- Legs 1–6 (+2 optional paralogue) endpoint MD, ~`PROD_NS` per replica × 3 replicas. Endpoint MD (no λ-window
  fan-out) is **much cheaper than the 16-window alchemical legs** — this is why the rung is priced ~$40–100 vs
  ~$255 for Val-B-full.
- **Independent (parallel on Vast):** every `(leg, seed)` system — one `submit()` each → N independent
  RTX-4090 bid instances. Leg 0 is $0 CPU/CI.
- **Dependent:** the sensitivity comparison (R4) and the panel verdict run after legs 1–6 land.
- **Cost placeholder — NOT yet measured:** the `~$40–100` in nr4a3-program-map.md is an estimate. The real number is
  calibrated on the **first real leg's** GPU-hours × the Vast 4090 bid rate (~$0.10–0.20/hr midpoint). This file
  and the schedule JSON's `cost_est_usd` are updated the moment that leg completes. **No Vast spend occurs until
  §7 CI validation passes.**

---

## 7. Build & validation gate (no Vast spend until green)

Before any paid GPU run, a **free-CI smoke** must prove the whole panel is runnable end-to-end:
1. Leg 0 (cysteine conservation) runs and is recorded ($0).
2. Every leg's system **assembles** (covalent adduct topology builds + parameterizes; C551A mutant stages; the
   warhead-only and recruiter-endpoint systems stage).
3. A **tiny MD** (minimize + a few hundred steps) runs on each assembled system without NaN, and the frozen R1–R4
   analysis functions execute on the tiny trajectory and emit the JSON schema.
Only when that CI smoke is green do we wire the Vast launcher and run the real legs.

---

## Results (append-only)

### Leg 0 — cysteine conservation (2026-07-22, `nrv04-cys-conservation.json`, CI run 29923279236)
- **NR4A1 residue 551 = Cys** (confirms the assumed covalent site is a cysteine).
- **NR4A2** aligned position 551 = **Tyr** (`LNRPN[Y]LSKLL`); **NR4A3** aligned position 579 = **Thr**
  (`QALEP[T]ESKVL`). Neither paralogue has a cysteine at the aligned position, and — hardening against
  global-alignment slop — **neither ±5 window contains any cysteine**.
- **Verdict (frozen §5-4):** the reactive Cys is **unique to NR4A1**. Celastrol cannot form the covalent adduct
  on NR4A2/NR4A3, so NR-V04's paralogue selectivity is **at least partly a warhead-reactivity effect** the
  noncovalent free-energy machinery cannot represent. **Consequences for the panel:** (i) this is now a
  *confirmed* confound, not a hypothetical — the covalent vs C551A vs warhead-only legs are the way we
  disentangle it; (ii) it reinforces nr4a3-program-map.md's demotion of NR-V04 to a biological holdout, not a noncovalent
  method calibrator; (iii) the optional `cov_nr4a2/cov_nr4a3` legs are **not** run in the minimal panel (celastrol
  can't bond there — there is nothing covalent to model).
- *Caveat:* global NW alignment of the full LBDs; the local ±5 windows (no nearby Cys in either paralogue) make
  the "unique to NR4A1" call robust to a few-residue misregistration. A structure-based recheck is a cheap future
  hardening if ever contested.

## Provenance / honesty
- Ligand chemistry is an **NR-V04-inspired representative reconstruction**, not an exact structural match
  (carried over from `nrv04-ternary-benchmark.json` `chemical_identity`). Stated in every result.
- Every atom of the E3/target scaffold is from a real deposited structure (8G1Q / RCSB); nothing fabricated.
- Verdicts are **directional concordance/discordance** with the reported NR-V04 outcome — never "recovered
  degradation," never an efficacy/affinity claim.

---

## AMENDMENT 1 — 2026-07-25 (dated defect-fix; trimcrae-delegated)

**Authority.** §Preamble freezes these criteria and nr4a3-program-map.md requires that amending a preregistered rule
after a failing result be "an explicit, dated, reviewer-approved defect-fix, not a quiet retune." trimcrae
delegated this decision on 2026-07-25. It is recorded here in full, with the frozen text above left **unedited**
so the original rule and this amendment can both be read.

**The standard applied.** A rule may be amended only if its *statistic is shown to lack discriminating power*,
demonstrated independently of whether we liked the answer it gave. "It returned an inconvenient verdict" is not
grounds. "It returns the same value regardless of the variable it exists to measure" is.

### Defect 1 — R2 has zero discriminating power (measured, not argued)

Frozen R2: *"Recruited = BSA > 0 sustained over > 50% of production frames."* This is a **presence** test, and
its value is fixed by the **co-folded starting structure** plus the absence of dissociation on a 6 ns timescale
— not by the variable each control isolates.

**Evidence:** across the panel's committed legs, `frac_frames_in_contact` takes **18 values and exactly one
distinct value: 1.0.** That includes `warhead_only` (no E3-binding moiety at all) and `recruiter_epimer` (the
inactive stereoisomer) — the two legs whose entire purpose is to read *lower* than the positives. A statistic
with **zero variance across the contrast cannot score the contrast.** Independently, the one leg ever run with
the *corrected* chain split also returns `recruited = true`, so this is not an artifact of the chain defect.

**Ruling: R2 is RETIRED as a GO criterion and demoted to a descriptive readout.** It may be reported; it may not
gate anything.

### Defect 2 — frozen criterion 3 is unsatisfiable, so the whole gate carried no information

Criterion 3 requires the negative controls to show *no* sustained recruitment under R2. Since R2 returns
"recruited" for every leg by construction, **criterion 3 can never be satisfied, so the frozen gate returns
NO-GO regardless of the science.** It would have said NO-GO for a beautifully-behaved NR-V04 ternary and for
complete garbage alike. That is not a conservative gate; it is an uninformative one.

**Ruling: criterion 3 is REMOVED from the GO condition,** because the statistic it depends on has been retired
and endpoint MD from a co-folded start at 6 ns provides no replacement capable of failing. Its scientific intent
is preserved by a stronger, earlier test — A1 below — which acts on the inputs rather than the output.

### Defect 3 — `recruiter_epimer` is not the control §3 specifies

§3 defines it as an *"endpoint system, not a morph"* and a **binary** VHL + epimer construct. As implemented it
runs as a **full ternary**. Moreover the epimer's inactivity is a *binding-affinity* fact about the VHL–recruiter
interaction, which a 6 ns MD launched from a co-folded pose cannot resolve in either direction.

**Ruling: `recruiter_epimer` is demoted to a descriptive sensitivity leg** and removed from the GO condition.
If it is ever to gate anything it must first be rebuilt as the binary system §3 actually specifies.

### NEW BINDING CRITERION A1 — input admissibility (this one can fail, and it does)

*No leg may be scored unless its starting structure instantiates the contrast it encodes.* For every leg
declared **covalent**, the celastrol electrophilic carbon must sit within bonding distance of the **target-chain**
Cys Sγ. A C–S single bond is ~1.8 Å; a preformed adduct that is not bonded is not a covalent model.

**Measured on the current co-folds, for $0, before any spend** (`nrv04-prespend-check.json`):

| leg | declared | nearest target-chain Cys Sγ | admissible |
|---|---|---|---|
| `cov_nr4a1` | covalent | **8.99 Å** | ✗ |
| `warhead_only` | covalent | **16.39 Å** | ✗ |

**Every covalent leg fails A1 by roughly 5–9×.** Boltz does not seat celastrol against an NR4A1 cysteine in any
co-fold currently in the bucket, so §5 criterion 2 — *"does covalency swamp the ternary signal"*, the panel's
stated crux — is **unevaluable on these inputs**, not merely unmeasured.

*Hypothesis this raises, flagged for the re-run rather than asserted:* the superseded observation that covalent
NR4A1 and noncovalent NR4A1 scored **identically (2/3 = 2/3)** is exactly what one predicts if the "covalent" leg
never carried a bond. That is consistent with A1 failing, and it is a prediction the amended panel can test. It
is **not** offered as an established mechanism here.

### What the panel may claim if re-run on admissible inputs

Interface persistence (**R1**) and covalent-vs-noncovalent sensitivity (**R4**), as **descriptive feasibility**,
reported as **directional concordance only**. It may **not** issue a recruitment verdict, and it may not be
cited as validating the noncovalent machinery — §1's conclusion that NR-V04 is a biological holdout rather than
a method calibrator is untouched by this amendment.

### Does this amendment rescue the failing result? NO — stated as the integrity test

1. **The committed panel's data is invalid for reasons no amendment touches:** the chain split was positional and
   scored Elongin C, and the inputs were contaminated (14-3-3 epsilon in place of Elongin B, source pinned at
   CA-Kabsch **RMSD 0.000 Å**). Those legs are unusable under the old rule and the new one alike.
2. **The amended gate leaves the panel exactly where the unamended gate left it — HELD.** A1 fails on every
   co-fold in the bucket. What changes is *why*: from "a gate that can never pass" to "inputs that do not
   instantiate the contrast." That distinction is the useful part, and it converts no NO-GO into a GO.

### Honest statement of what this LOOSENS

The old gate was **unpassable**; removing criterion 3 makes GO reachable where it previously was not. That is a
loosening and it is stated plainly rather than dressed as a tightening. The justification is not that the old
answer was unwelcome but that the old statistic had **no discriminating power**, shown from 18 legs of zero
variance. This is the same degenerate-gate class as valB_mini's calibration gate, which **admits the null**
(a method predicting no cooperativity change passes 22% of the time against 23% for a method that is exactly
right). One gate always fails, the other passes anything; both are defective for the same reason — the statistic
does not discriminate the hypothesis. A1 is added precisely so that the amended gate retains a criterion that
**can** fail, and it is binding immediately.

### Consequences

- **`nrv04_feasibility_covalent` stays `[HELD]`.** The re-run is not authorised by this amendment.
- **Unblocking it requires input work, not compute:** re-fold `neg_celastrol` / the covalent systems so the
  electrophile is seated against Cys551, or drop the covalent legs and re-scope the panel to what noncovalent
  endpoint MD can support — and say which was done.
- **A1 is retrospective in force:** any future covalent leg, in this panel or the NR-V04 retrospective, must
  record its staged Sγ distance and refuse to run if it fails. This is implemented in
  `nrv04_covalent_md` (`MAX_COVALENT_TETHER_A`, default 8.0 Å, override only with a recorded deviation).

---

## AMENDMENT 2 — 2026-07-25 (same day as AMENDMENT 1; corrects it)

**AMENDMENT 1's criterion A1 was measuring the wrong cysteine.** Its verdict is unchanged and in fact
strengthened; its **numbers were wrong** and are corrected here rather than quietly restated.

### The defect

A1 requires a covalent leg to stage its electrophile within bonding distance of "the target-chain Cys Sγ".
That was implemented via `_reactive_cys_by_geometry`, which returns the **nearest** target-chain cysteine.
The NR4A1 LBD construct has **six** (C465, C475, C505, C534, **C551**, C566), and the nearest is **C566** —
not C551, the residue this preregistration names as the covalent site throughout §1 and §3.

Construct arithmetic (P22736 = 598 aa, C-terminal 254-residue construct, offset **344**): co-fold residue
**207 = C551**, residue **222 = C566**. The panel's own legs record `reactive_cys = chain A resid 222`
throughout — i.e. every covalent leg resolved **C566**.

### Corrected measurements — at C551, across **all 34** co-fold models in the bucket

| system | nearest target Cys (what A1 measured) | **C551 Sγ → electrophile (what A1 MEANT)** |
|---|---|---|
| `cov_nr4a1` | C566 @ **8.99 Å** | **28.46 Å** |
| `warhead_only` | C566 @ **16.39 Å** | **36.43 Å** |
| best of 7 clean models | — | **28.42 Å** |
| worst | — | **39.11 Å** |

**Superseded, do not cite: the 8.99 Å and 16.39 Å figures in AMENDMENT 1.** They are C566 distances.
AMENDMENT 1 also said "any co-fold in the bucket", which rested on **one model per system**; it is now **all
34** (7 clean, 27 rejected as contaminated), and the conclusion holds across every one.

### Why this makes A1 *more* binding, not less

At ~9 Å the gate was **nearly passing** against an 8.0 Å limit. Had a co-fold placed celastrol 7 Å from C566,
**A1 would have PASSED while the actual covalent site sat ~28 Å away.** The gate could have admitted an
inadmissible input. It now fails closed at ~28 Å.

### Two further defects in the same root cause, both now fixed

1. **The covalent restraint would have been built onto C566** — the adduct would not have been at the
   preregistered site.
2. **`cov_c551a` was mutating C566.** The control named for removing C551 engagement **was not touching C551**,
   so it did not remove the engagement it exists to remove, and its result was uninterpretable as designed.

`_frozen_cys_by_construct` now **identifies** the site by construct arithmetic and verifies it is a Cys bearing
an Sγ, **failing closed**; geometry is demoted to a diagnostic that records any disagreement.

### RULING — the covalent legs are RETIRED, and the panel is re-scoped to noncovalent

The re-fold route was **run and refuted**, not argued away ($0.05 on Vast, 2 systems × 3 seeds):
- **Deleting the E3 makes seating worse** (33.6 / 36.6 / 44.7 Å free vs ~28 Å ternary) — the ternary
  arrangement is not the cause.
- **A steered co-fold honours its constraint and still fails**: an explicit `max_distance: 6.0` restraint to
  residue 207 moved the electrophile ~37 → ~15 Å and doubled warhead–target contacts, yet **Boltz never
  satisfied its own 6 Å bound on any of three seeds**, parking celastrol near the buried C505 instead.

No predictor produces the pose (7/7 clean models, 4 seeds, 3 prefixes, 2 providers, plus the refuted steered
probe) and **no deposited celastrol–NR4A1 structure constrains it**. The only remaining route is a
**hand-placed pose**, which would fix the *comparison* (cov vs noncov on the same construction) without
supplying the *evidence*. **This is a statement about the predictor, not about whether celastrol binds C551** —
the site is literature-anchored (Zhang et al., *Chem. Commun.* 2018, doi:10.1039/C8CC06140H, PMID 30376017:
celastrol positioned by specific noncovalent interactions adjacent to the C551 thiol, reversible covalent bond;
C551 is the most exposed of the six).

**Retiring them costs the panel little, because Leg 0 already did their job for $0:** the reactive cysteine is
**unique to NR4A1** (NR4A2 Tyr, NR4A3 Thr579), which is the covalent confound's actual content. And NR-V04 is
already demoted to a **biological holdout** with SMARCA2/4 as the method calibrator, so modelling a demoted
holdout's covalency inverts the ladder.

**A noncovalent-only panel is exactly what AMENDMENT 1 permits to be claimed** (interface persistence + a
covalent/noncovalent sensitivity statement is no longer available; R1 persistence and directional concordance
remain). The panel stays **`[HELD]`** — this amendment retires a leg set, it does not authorise a run.
