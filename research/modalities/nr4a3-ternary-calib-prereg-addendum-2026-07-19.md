# valB_mini calibration — PREREGISTRATION FREEZE ADDENDUM (2026-07-19)

**Committed BEFORE any GPU fan-out**, per the external reviewer AI's *conditional protocol approval*
(2026-07-19). This addendum FREEZES the protocol changes the reviewer required as conditions of approval and
records exactly which code enforces each. It sits on top of
[`nr4a3-ternary-coop-prereg.md`](./nr4a3-ternary-coop-prereg.md) (the standing ternary prereg) and the frozen
calibration structures in [`wurz-calib-frozen.json`](./wurz-calib-frozen.json). Where this addendum and an
earlier rule differ, **this addendum governs** for the Wurz cmpd1→cmpd4 (SMARCA2–VHL) valB_mini calibration.

The reviewer's verdict: *"No fundamental objection to the pre-equilibration remedy or the
calib → NR-V04 → matrix ladder."* Approval is **conditional** on the eight items below, executed in the
frozen order. **Nothing in this addendum authorizes a spend by itself** — every GPU run is still presented at
its gate with a pinned cost and waits for an explicit go (RUNG discipline, CLAUDE.md).

---

## Execution order (frozen)

1. **Fix endpoint alignment + mapping** (condition 1) — *done, code + tests*.
2. **Freeze** force fields / equilibration / seeds / diagnostics / reducer formula / acceptance criteria
   (conditions 2–6) — *this addendum + code + tests*.
3. **One short exact-Hamiltonian endpoint smoke test per physical endpoint** (condition 2) — *GPU, first gated
   spend*.
4. **Inspect** the existing `.nc` + the new smoke for overlap / mixing / dG(t) (conditions 4, 8) — *CPU*.
5. **Fan out 3 replicates** of every calibration leg using ONLY the finalized protocol (condition 3) — *GPU*.
6. Apply the **PASS / BORDERLINE / FAIL** gate (condition 6).
7. **NR-V04 retrospective ONLY after** the calibration PASSes (condition 7).
8. **Prospective matrix ONLY after** an independent NR-V04 pass against NR-V04's own prereg (condition 7).

Steps 1–2 and 4 are $0 self-doable and are complete/ready; steps 3, 5 are the gated GPU spends.

---

## Condition 1 — endpoint alignment + explicit mapping *(FROZEN; enforced)*

- **Both calibration endpoints come from the SAME relaxed conformer.** ligA carries the pre-equilibration MD
  coordinates; ligB's **mapped (common-core) atoms are TRANSPLANTED exactly onto ligA's relaxed coordinates**
  using the FEP's own atom map (LOMAP element-change; rdFMCS fallback). Only the unmapped/dummy atoms are
  relaxed, with the core held fixed. The previous whole-molecule O3A overlay (which left mapped atoms
  displaced and produced OpenFE "mapped atom moved" warnings) is **removed**.
- **Programmatic verification before write** (`ternary_endpoint_align.verify_endpoints`), fail-loud in
  `ternary_preequil`: zero mapped-atom displacement; preserved connectivity / bond orders / formal charges /
  stereo tags; no 3D chirality inversion; net formal charge conserved A vs B; sane dummy bond lengths; no
  atom-atom clashes. Persisted to `endpoint_align_check.json`.
- **Enforcers:** [`ternary_endpoint_align.py`](./ternary_endpoint_align.py),
  [`ternary_preequil.py`](./ternary_preequil.py) `_write_relaxed`/`_endpoint_map_a2b`.
  **Tests:** [`tests/test_ternary_endpoint_align.py`](./tests/test_ternary_endpoint_align.py).
- The prior single-replicate **ΔG_morph = 47.28 ± 0.53** is treated as a **stability diagnostic, NOT a final
  replicate** (condition 8 audit below).

## Condition 2 — exact-Hamiltonian equilibration; pre-equil is a conditioner *(FROZEN; enforced)*

- The plain-MD pre-equilibration is **only a coordinate conditioner** (different relaxation FF, no alchemy). It
  does **not** sample the RBFE target ensemble and its output is **never** used as production data.
- Under the **exact RBFE Hamiltonian**, each λ-window runs: minimize (`minimization_steps`) → equilibrate for
  `equilibration_length` (**discarded from MBAR by construction**) → collect `production_length` for MBAR.
  `EQUILIBRATION_NS = 1.0` (> 0) IS the reviewer-required discarded unrestrained equilibration.
- **Force-field-switch discontinuity + physical-endpoint stability** are recorded under the exact Hamiltonian
  for **ligand A (λ=0) and ligand B (λ=1)**: min-energy relaxation after the FF switch (large drop = bad
  conditioner), no NaN, bounded ligand RMSD, bounded energy drift.
- The pre-equil conditioner is **excluded from protocol-equality** (a starting-coordinate choice, like the
  per-replica seed) — it does not change the Hamiltonian, so it does not enter `protocol_signature`.
- **Enforcers:** [`ternary_endpoint_stability.py`](./ternary_endpoint_stability.py) (pure core + GPU wrapper,
  invoked at step 3 as `MODE=endpoint_smoke`), [`nr4a3_ternary_fep.py`](./nr4a3_ternary_fep.py) `_protocol`
  (equilibration ladder documented). **Tests:**
  [`tests/test_ternary_endpoint_stability.py`](./tests/test_ternary_endpoint_stability.py).

## Condition 3 — replicate design + uncertainty *(FROZEN)*

- **≥ 3 independent complete-cycle replicates** (solvent + binary + ternary), differing by **seed AND initial
  velocities** (preferably decorrelated PE snapshots). Each replicate is one full cooperativity cycle.
- **Uncertainty = between-replicate sample SD** (t / bootstrap CI). The single-run **MBAR SE is NEVER
  substituted** for between-replicate uncertainty.
- **Extend to 5 replicates** when: cycle SD > 0.75; one replicate is separated (outlier); a would-be pass/fail
  sits within 0.5 kcal/mol of a boundary; or the replicates settle into different interface states.
- **Enforcers:** `ternary_fep_reduce.per_replicate_ddg_coop` (pairs ternary/binary legs by seed → per-replicate
  ΔΔG_coop list; solvent cancels within each replicate), `calibration_gate` (sample-SD based; `extended` flag).

## Condition 4 — frozen per-leg convergence checks *(FROZEN; enforced)*

Per leg, all must pass (a persistent failure → gate FAIL): no NaN / constraint failure / dropped replicas;
**MBAR overlap matrix CONNECTED with no adjacent-state bottleneck** (not a naive universal scalar cutoff —
every neighbor link must clear the floor); sustained λ-exchange / replica mixing; **dG(t) plateau** (|full −
final-half| ≤ 0.5 and |Q3 − Q4| ≤ 0.5); forward/reverse BAR/FEP agree ≤ 1.0; stable ligand-core / interface
RMSD. OpenFE's overlap definition is respected — the requirement is **connectivity + no bottleneck**, not a
blanket cutoff.
- **Enforcers:** [`ternary_fep_convergence.py`](./ternary_fep_convergence.py)
  (`overlap_matrix_bottleneck`, `block_plateau`, mixing, forward/reverse, structural → `technical_failure`),
  folded into the gate via `ternary_fep_reduce._diagnostics_ok`. **Tests:**
  [`tests/test_ternary_convergence_pure.py`](./tests/test_ternary_convergence_pure.py).

## Condition 5 — reducer sign convention *(FROZEN; enforced)*

- The reducer returns **ΔΔG_coop = ΔG_alch,ternary − ΔG_alch,binary = −RT ln(α_B/α_A)** — the SAME quantity the
  frozen target defines (`−RT ln(α_4/α_1) = +0.944`, morph A=cmpd1/hi → B=cmpd4/lo). It is the **per-morph
  RELATIVE** cooperativity change, **not** a single compound's `dG_coop = −RT ln α`. For the hi→lo calibration
  it is **positive (+0.944)**, and the gate requires that positive sign.
- **Independent recompute** from raw K_D provided (`ternary_coop.ddg_coop_from_kd_pairs`); K_D uncertainties
  and experimental T carried through.
- **Enforcers:** [`ternary_coop.py`](./ternary_coop.py) (`ddg_coop`, `ddg_coop_from_kd_pairs`),
  [`ternary_fep_reduce.py`](./ternary_fep_reduce.py) (`_welch_satterthwaite` docstring). **Tests:**
  [`tests/test_ternary_coop_sign.py`](./tests/test_ternary_coop_sign.py).

## Condition 6 — FIXED accuracy gate (three-tier) *(FROZEN; enforced)*

Target **+0.944 kcal/mol** at 298.15 K. Verdict = `ternary_fep_reduce.calibration_gate` on the
per-replicate cycle values:

| Tier | Criteria |
|------|----------|
| **PASS** | all convergence diagnostics pass **AND** correct positive sign **AND** \|mean ΔΔG_calc − target\| ≤ **1.0** **AND** cycle SD ≤ **0.75** |
| **BORDERLINE** (extend to 5, do NOT advance) | abs error in (1.0, 2.0] **OR** cycle SD in (0.75, 1.0] **OR** within 0.5 of a pass/fail boundary |
| **FAIL** | wrong sign **OR** abs error > 2.0 **OR** cycle SD > 1.0 after extension **OR** persistent overlap/drift/structural failure |

This is a **FIXED accuracy margin, not "within replicate SD."** It supersedes both the retired ±1.0-band-alone
rule and the interim zero-exclusion-only rule (see `wurz-calib-frozen.json` → `decision_rule_valB_mini`), and
because PASS requires correct sign + small error + small SD + clean diagnostics **together**, it cannot pass
zero or a diverging replicate set. **Tests:**
[`tests/test_ternary_calibration_gate.py`](./tests/test_ternary_calibration_gate.py).

## Condition 7 — narrow interpretation *(FROZEN)*

A calibration **PASS validates**: pipeline plumbing, endpoint stability, cycle algebra, uncertainty
estimation, and **one known-answer** (the Wurz hi/lo SMARCA2–VHL cooperativity ordering). It does **NOT**
validate ternary-FEP physics broadly. **A PASS authorizes the NR-V04 retrospective ONLY.** The prospective
degrader matrix stays **blocked** until NR-V04 passes its **own** preregistered criteria. Language throughout:
*"predicted selective candidate"* — never efficacy / safety / therapeutic-window / clinical-readiness.

## Condition 8 — investigate (don't reject) the 47.28 leg *(audit; CPU step 4)*

The single-replicate ΔG_morph = 47.28 ± 0.53 is a **stability diagnostic**. Before/with the 3-replicate
fan-out we check: whether the magnitude is a bonded / charge / mapping-strain artifact; **A→B / B→A
antisymmetry** (a clean cycle has ΔG_morph(A→B) ≈ −ΔG_morph(B→A)); that the large binary and ternary legs
**cancel reproducibly** in ΔΔG_coop; and that replicate fluctuations are comparable across the ternary /
binary / solvent legs. The antisymmetry algebra is unit-tested
([`tests/test_ternary_coop_sign.py::test_antisymmetry_lo_to_hi_flips_sign`]); the energy-decomposition audit
runs on the committed `.nc` at step 4.

---

*Frozen 2026-07-19. Enforced by the modules and tests named above; `node scripts/validate.mjs` unaffected
(research-tree change). No criterion may be re-decided post-hoc on a favorable number.*
