# NR-V04 covalent feasibility panel — preregistration & scoring freeze

**Rung:** `nrv04_feasibility_covalent` (STRATEGY.md RUNG 3). **Status:** BUILDING (no GPU run until this panel is
built + CI-validated end-to-end — trimcrae decision 2026-07-22: "build fully before any run").
**Provider when it runs:** Vast.ai (bid/interruptible, RTX-4090-class, per-leg S3 checkpoint).

This document is the **frozen** definition of the panel and its GO/NO-GO. It is written BEFORE any GPU leg runs
(reviewer condition 4 requires the scoring rules be fixed in advance). Once a leg has run, this file is
append-only for results; the criteria below do not move.

---

## 1. Why this panel exists (reviewer condition 4, STRATEGY.md:86-94)

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
- **Cost placeholder — NOT yet measured:** the `~$40–100` in STRATEGY.md is an estimate. The real number is
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

## Provenance / honesty
- Ligand chemistry is an **NR-V04-inspired representative reconstruction**, not an exact structural match
  (carried over from `nrv04-ternary-benchmark.json` `chemical_identity`). Stated in every result.
- Every atom of the E3/target scaffold is from a real deposited structure (8G1Q / RCSB); nothing fabricated.
- Verdicts are **directional concordance/discordance** with the reported NR-V04 outcome — never "recovered
  degradation," never an efficacy/affinity claim.
