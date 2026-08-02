# DeepTernary head-to-head — status and the one open defect (2026-08-02)

**Goal it serves:** a **positive ternary control** for the paper. The program has none in any form. This
run would supply one *at the generation stage*: a known-answer ternary test, run blind, that the workflow
passes. It would **not** supply a positive control for paralogue-selectivity *detection* — different stage,
harder claim, and the panel our co-folds fed returned a NULL whose bound is unchanged by any of this.

## Established and committed

| step | state |
|---|---|
| Blindness of the test cases | **verified** — 9DTY/9DTX absent from DeepTernary's disclosed exclusion set (`deepternary-leakage-check.json`) |
| Input sourcing from RCSB | **done** — 12 target-side + 12 E3-side candidates per arm |
| Input curation | **done** — SMARCA2: 9DU0 + 5NVX; SMARCA4: 5DKD + 5NVX |
| Fragment verification | **done** — SMARCA2 warhead overlap **1.000**, anchor 0.778 → READY; SMARCA4 warhead **0.417** → **REFUSED** below the 0.55 bar |
| Chain resolution | **done** — one copy of the E3, seeded from a single ligand instance |
| Blind input prep (6 files) | **done** |
| Prediction | ⛔ **BLOCKED — see below** |
| Scoring | not reached |

The incumbent to beat, read from `selcal-cofold-dockq.json`: our Boltz co-folds score DockQ **0.023–0.038**
on this arm's target↔VHL interface, fnat 0.000.

## The open defect — CONECT records

`predict_cpu.get_lig_coords` calls `Chem.MolFromPDBFile('unbound_lig1.pdb')` and gets `None`
(run 30752326235, `AttributeError: 'NoneType' object has no attribute 'GetConformer'`).

**Cause:** 9DU0 and 9DTY are **mmCIF-only** entries, so this lane converts them to PDB
(`selcal_deepternary_run.write_pdb`) for `deepternary_blind_prep`, which is PDB-only. mmCIF stores bonds in
`chem_comp_bond`, not as CONECT records, so the converter emits **coordinates without connectivity**.
RDKit's PDB reader infers protein bonds from residue templates but has no template for a novel HETATM like
`A1BB5`, so with no CONECT it produces an unsanitizable molecule and returns `None`.

⚠ This is a **format-plumbing defect, not a scientific one**, and it must not be read as "DeepTernary failed"
or as "the inputs were bad". The inputs passed verification: the warhead is a perfect substructure of the
degrader (21/21 heavy atoms).

**Two candidate fixes, neither attempted yet:**
1. Emit CONECT records in `write_pdb`, derived from the CCD `chem_comp_bond` table for HETATM residues
   (sourced, not distance-inferred — a distance guess would invent chemistry).
2. Have the ligand come from the CCD **ideal SDF** instead of the extracted PDB block, and transform it onto
   the extracted coordinates. Closer to what `build_degrader` already does for the full degrader.

(2) is likely cleaner and reuses existing code. Neither is a spend; both are CPU.

## What must not happen next

- **Do not lower the 0.55 fragment bar to let the SMARCA4 arm in.** Its refusal is an input-availability
  fact — no binary from the degrader's chemical series exists for SMARCA4 — and a score from an unrelated
  frame would measure our input error and be quoted as the generator's.
- **Do not quote DeepTernary's 0.62–0.83 figures as an expectation.** Those are on structures *inside* its
  exclusion set (`deepternary-leakage-check.json`); blind performance here is unmeasured.
- **Do not report an unrun arm as a zero.** Every module in this lane already refuses that; keep it.
