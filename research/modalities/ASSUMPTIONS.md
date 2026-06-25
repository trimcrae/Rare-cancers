# Assumption audit — research/modalities compute scripts

Systematic sweep for *silent* assumptions (ones that produce a wrong-but-plausible result with no
error), prompted by a near-miss: an interim pocket-enumeration script produced a spurious "orthosteric
= 0.026" result (a wrong alpha-sphere count + a tentative file-index assumption), which was caught and
retracted in-session before it reached any manuscript number — the authoritative value is the original
Pocket 5 = 0.495, residues 406-534. Status legend:
**FIXED** (derived from data + unit-tested) · **GUARDED** (asserts/fails loud) · **AUDIT** (correct
only if the next real run's log is checked) · **RISK** (documented, not yet mitigated).

| # | Assumption | Where | If wrong → | Status |
|---|---|---|---|---|
| 1 | fpocket residue-file index == info.txt pocket number | was nr4a3_structure.py / nr4a_selectivity.py | wrong residues↔druggability (latent risk; convention happens to hold here, so original output was correct) | **FIXED** — `fpocket_lib.map_files_to_pockets` derives it from alpha-sphere fingerprints, asserts bijection, fails loud; regression test |
| 2 | solvated PDB keeps AF2 numbering (vs renumbered from 1) | nr4a3_mdpocket / nr4a3_metad | zero or wrong residues matched (already hit once) | **FIXED** — `residue_map.resolve_positions`, both schemes tested |
| 3 | PDB/PQR fixed-width columns (resSeq[22:26], xyz[30:54], name[12:16], resName[17:20], bfactor[60:66]) | all parsers | mis-parse on insertion codes / multi-char chains / nonstandard PDB | **GUARDED** for fpocket/AF inputs (standard format; tested in fpocket_lib). RISK for arbitrary PDBs |
| 4 | PLUMED atom index = OpenMM atom.index + 1 (1-based over system order) | nr4a3_metad `_cv_ca_plumed_indices` | CV biases the WRONG atoms, silently | **AUDIT** — metad logs the chosen CA indices; verify they map to CV residues 406…534 in the first real run. Needs an in-run assertion |
| 5 | Rg of the CV CA atoms falls in the wall/grid window (SIGMA 0.03, walls 0.6–2.2 nm, grid 0.4–3.0) | nr4a3_metad PLUMED | mis-scaled bias / walls clip the basin | **AUDIT** — log the initial Rg before committing GPU time; retune if outside |
| 6 | SASA baseline (frame 0) ≈ the static AF2 collapsed pocket | nr4a3_mdpocket | "opening vs static model" overstated — frame 0 is POST-equilibration | **FIXED (labelling)** — see commit; baseline relabelled as "first production frame", and a static-model reference is the correct comparator (flagged) |
| 7 | LBD trimmed contiguously from 373 (residue r at ordinal r−373) | nr4a3_md / nr4a3_metad / residue_map | ordinal shift if PDBFixer drops/adds a residue | **GUARDED** — resolver prefers resSeq; renumbered branch assumes contiguity. Add an n-residue assertion (TODO) |
| 8 | AFDB serves a stable model (fetch "current") | all AFDB fetchers | structure (hence pockets/MD) silently changes when AFDB updates the model | **RISK** — pin + log the resolved `pdbUrl` and a PDB checksum for reproducibility (TODO) |
| 9 | mdtraj `shrake_rupley(mode=residue)` column order == topology residue order | nr4a3_mdpocket | SASA attributed to wrong residues | **AUDIT** — true per mdtraj docs; not locally testable (no mdtraj). Verify residue labels in output |
| 10 | protein-residue name set `_AA` is complete (incl. HID/HIE/HIP/HSD/HSE) | nr4a3_metad | a residue excluded → ordinal shift in CV mapping | **GUARDED** — set includes Amber/CHARMM His names; assert matched-count == len(CV) already present |
| 11 | ChEMBL name→SMILES (limit=1) returns the intended compound | nr4a3_dock | docks the wrong molecule | **RISK** — record chembl_id (done) but verify identity |
| 12 | docking box (24³ Å on CA centroid) covers the pocket | nr4a3_dock | truncated search space | RISK — heuristic; inspect poses |
| 13 | single trajectory, no replicas/error bars | nr4a3_md / mdpocket | over-reading noise as signal | **RISK** — production should run replicas + report CIs |
| 14 | fpocket alpha-sphere coords match between vert.pqr and _out.pdb at 2-dp rounding | fpocket_lib mapping tie-break | tie-break fails → raises (does not mis-map) | **GUARDED** — fails loud by design |

## Cross-cutting rules (also in TESTING.md)
- Derive external-tool conventions from data; never assume. Fail loud on ambiguity.
- Pure parsing/mapping logic in unit-tested libs (`fpocket_lib`, `residue_map`); CI gates on green.
- Real runs must emit audit cross-checks (the `#4`, `#5`, `#8`, `#9` items above are only as safe as
  someone reading that log) — so every GPU job prints the load-bearing derived quantities.

## Open mitigations (prioritised TODO)
1. **#4 / #5 (metad):** add an in-run assertion that the CV CA atoms belong to the intended residues,
   and print the initial Rg, before the (long) production run. *Highest priority — load-bearing & untested.*
2. **#8:** log resolved `pdbUrl` + PDB sha256 in every AFDB-fetching job; consider pinning a version.
3. **#7 / #10:** assert protein-residue count == expected LBD length (254) after solvation.
4. **#6:** compute a proper static-model SASA baseline (from the pre-equilibration minimized structure).
