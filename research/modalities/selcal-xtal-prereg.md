# Preregistration — the sensitivity control, re-run on deposited crystal copies

**Frozen 2026-08-02, before any leg of this panel ran.** Nothing below may be changed after a leg lands; an
amendment is an appended, dated, numbered block that states what changed and why, in the parent panel's
style. The scorer is `selcal_gate.verdict`, unchanged and imported.

---

## 1 · Why this panel exists, in one paragraph

`selcal_panel` asked the only question that can license a paralogue-selectivity claim from this program:
**given a pair whose selectivity is measured and whose structures are solved on both arms, can the endpoint
tell them apart?** It returned NULL on an adequately-powered design. That null was then found to be
uninterpretable: its twelve starting structures reproduce the degradation-target↔VHL interface at **DockQ
0.023–0.046, fnat 0.000**, which the displaced-native decoy ladder places at the **~32 Å** rung
([`selcal-dockq-decoy-scale.json`](./selcal-dockq-decoy-scale.json)) — the endpoint was never exercised on
the complexes whose selectivity was measured.

**9DTY and 9DTX ARE those complexes.** This panel runs the identical endpoint on the deposited crystals, so
no predicted coordinates enter anywhere in the chain.

## 2 · What is imported and therefore not restated

| quantity | one home |
|---|---|
| endpoint **E1** (interface-RMSD plateau, Å, mean over the final 50 % of production frames) | `nrv04_covalent_md` |
| sampling protocol (`PROD_NS`, `EQUIL_NS`), velocity replicas | `selcal_panel` |
| α, the one-sided statistic, the tier definitions, the scorer | `selcal_gate.verdict` |
| direction of effect | `selcal_panel.PREDICTED_MORE_STABLE_ARM` |
| the reference ligand, the two deposits, the arms | `selcal_panel.REFERENCE` / `.ARMS` |
| the permutation floor arithmetic | `selcal_gate.design_floor` |

`tests/test_selcal_xtal_stage.py` fails if any of them is re-declared in this lane.

## 3 · The hypothesis and its direction

PRT3789 degrades SMARCA2 (DC50 1 nM) and largely spares SMARCA4 (DC50 32 nM), and Kofink et al. 2022 locate
the difference at the VCB↔bromodomain interface E1 measures. **Predicted: the SMARCA2 arm plateaus LOWER
(more stable interface) than the SMARCA4 arm.** One-sided, in that direction, because a two-sided test on a
known-direction control discards the thing that makes it a control.

- **Arm A** = `selcal_smarca2` (9DTY) — predicted more stable.
- **Arm B** = `selcal_smarca4` (9DTX) — predicted less stable.
- Statistic: mean(A) − mean(B) over **copy means**, negative favouring the prediction.

## 4 · Unit of independence — the crystallographic COPY

A deposit's asymmetric unit holds several independent realisations of the same complex, each in a different
lattice environment. **The copy is the model**; velocity replicas collapse to copy means before the test,
exactly as the parent panel collapses replicas to co-fold-model means. The reference set is therefore
`C(n_A + n_B, n_A)` over copies, computed by `selcal_gate.design_floor`.

**Arms are matched at the smaller deposit's usable-copy count.** An unmatched design would compare unequal
evidence between the two arms and is not run.

## 5 · The powered-design condition, fixed before the census was read

⛔ **"Can reach α" is not "powered", and this panel requires the stronger one.** At 3 copies per arm the
floor is *exactly* 0.05: only the single most extreme arrangement of 20 could ever reject, so one tied or
mildly out-of-order copy makes the test unable to fire at all. The condition is therefore

> **minimum attainable one-sided p ≤ α / 3**

which makes the parent panel's own phrase — *"comfortably clear of alpha"* — executable. The smallest shape
that satisfies it is **4 copies per arm** (C(8,4) = 70, floor 0.0143). Implemented in
`selcal_xtal_stage.design_from_census`.

**If the census does not supply a powered design, this panel does not run**, and that is reported as a
property of the deposits — not as a null.

## 6 · Exclusions — by measured input fault only, keyed on the copy, before any outcome is known

1. **The degrader must bridge.** A copy is admitted only if its own degrader lies within
   `selcal_cofold_validate.FNAT_CONTACT_A` (5.0 Å) of **both** the target chain and the E3 chains. A deposit
   can resolve a copy's protein and leave its ligand unmodelled at that site; staging such a copy would run
   an **apo interface while recording as a ternary leg**, which is the shape of the smoke-leg incident
   (STRATEGY Appendix A 57).
2. **The static input audit** (`selcal_stage.cofold_input_audit`, closest heavy-atom pair between different
   residues ≥ 1.0 Å) applies unchanged.
3. **Chimeric copies are discarded, not scored** — the enumerator
   (`selcal_cofold_validate.target_anchored_assemblies`) carries its own chimera check and its own measured
   limit, and both are reused rather than re-derived.

No exclusion may reference an E1 value. Every refusal is published with the number that caused it.

## 7 · What each outcome licenses — written before the run

- **PASS** — Arm A plateaus lower than Arm B, one-sided, p < α. The endpoint discriminates a known,
  structurally-explained paralogue difference on correct inputs. **This is the positive control the program
  has never had**, and it is the precondition for treating any NR4A3 ternary readout as evidence. It does
  **not** make any NR4A3 prediction correct; it makes the instrument usable.
- **NULL / FAIL** — the endpoint cannot resolve that difference even when handed the deposited complexes.
  Then **no NR4A3 selectivity case can be justified with E1**, and the paper must say so in those words
  rather than continuing to describe the predictions as merely unvalidated.
- **WRONG DIRECTION** (Arm B lower, p < α on the reverse check) — scored and reported by the same gate; it is
  a failure of the readout, not evidence about the ligand.

## 8 · ⚠ What a PASS would still not establish

This panel tests the **readout**, not the workflow. A prospective NR4A3 campaign has no crystal, so its
starting structures come from the generation stage — which is separately measured and separately failing, at
**DockQ 0.023–0.046** on this very pair. **Both stages must work for a prospective selectivity claim.** A
pass here establishes at most one of them, and the paper must not let one stand in for the other.

## 9 · Provenance guards

- `PANEL = "selcal_xtal_control"` and `LABEL_PREFIX = "selxtal-"` are disjoint from the parent panel's, so no
  collector or reaper can cross lanes.
- Every leg record carries `MODEL_SOURCE = deposited_crystal_copy` and `CRYSTAL_COPY_ID` beside the
  `COFOLD_MODEL_SEED` the gate keys on, so a record's provenance is readable **from the record**.
- `selcal_xtal_panel.partition_legs` returns foreign records rather than dropping them: a foreign record here
  means a prefix collision, and a crystal record that failed to stamp its provenance is equally a reason to
  stop.
