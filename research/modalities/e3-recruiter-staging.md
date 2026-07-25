# E3 recruiter staging + ligandability downselect

*E3 recruiter staging + ligandability downselect — STRATEGY.md RUNG 5a(c), 'E3 breadth, free at the search stage'*

> **Honest scope.** This is DESIGN PREP, not a validated result. Ligandability computed from one deposited holo structure is a hypothesis for testing: it says a published ligand occupies a pocket with a solvent-directed exit vector, nothing more.

## Decision

**Advanced (<= 2):** BIRC2, MDM2

| recruiter | class | PDB | res (A) | ligand | buried | exit clear (A) | cone | open15 | analogue | decision |
|---|---|---|---|---|---|---|---|---|---|---|
| VHL | CRL2 substrate receptor (BC-box) | 7Z76 | 1.32 | IFJ | 0.7673 | 25.0 | 1.0 | 0.1641 | solved_ternary | **DROP** |
| CRBN | CRL4 substrate receptor (DCAF) | 8RQC | 2.15 | QFC | 0.8432 | 25.0 | 1.0 | 0.2363 | solved_ternary | **DROP** |
| BIRC2 | monomeric RING E3 (BIR/RING) | 6W7O | 2.17 | TL7 | 0.7775 | 25.0 | 1.0 | 0.3027 | solved_ternary | **ADVANCE** |
| DCAF1 | CRL4 substrate receptor (DCAF) | 9NSO | 1.85 | A1B0Y | 0.864 | 25.0 | 0.5135 | 0.0742 | solved_ternary | **DROP** |
| DCAF15 | CRL4 substrate receptor (DCAF) | 8ROY | 3.1 | A1H18 | 0.5695 | 25.0 | 1.0 | 0.4297 | solved_ternary | **DROP** |
| DCAF16 | CRL4 substrate receptor (DCAF) | 8G46 | 2.2 | YK3 | 0.8919 | 0.0 | 0.0 | 0.0 | solved_ternary | **DROP** |
| KEAP1 | CRL3 substrate receptor (BTB-Kelch) | 9KVW | 1.44 | A1EHH | 0.6973 | 25.0 | 1.0 | 0.3828 | bivalent_binary | **DROP** |
| FEM1B | CRL2 substrate receptor (ankyrin) | 9PW8 | 2.8 | A1CLY | 0.8694 | 0.0 | 0.0 | 0.0 | handle_only | **DROP** |
| RNF114 | monomeric RING E3 | — | — | — | — | — | — | — | none | **DROP** |
| MDM2 | monomeric RING E3 (nutlin-recruited) | 6Q9L | 1.13 | HTZ | 0.6609 | 25.0 | 1.0 | 0.5137 | bivalent_binary | **ADVANCE** |

## Dropped set — every recruiter not advanced, with the reason

*STRATEGY.md: "a silent top-N reads as 'we covered everything'". Availability is **never** a reason here — all widened arms are broadly expressed (HPA, CI run 30125742542).*

- **DCAF15** — dropped at the *gate* stage. at least one deposited structure containing the recruiter with a bound non-solvent, non-cryoprotectant ligand of >=10 heavy atoms, at resolution <=3.0 A (diffraction/EM) or by solution NMR — observed: 8ROY @ 3.1 A (ELECTRON MICROSCOPY), ligand A1H18
- **DCAF16** — dropped at the *gate* stage. exit-vector clearance >= 8.0 A AND 30-degree cone openness >= 0.30 — observed: {'clearance_A': 0.0, 'cone_openness_30deg': 0.0}
- **FEM1B** — dropped at the *gate* stage. exit-vector clearance >= 8.0 A AND 30-degree cone openness >= 0.30 — observed: {'clearance_A': 0.0, 'cone_openness_30deg': 0.0}
- **RNF114** — dropped at the *gate* stage. at least one deposited structure containing the recruiter with a bound non-solvent, non-cryoprotectant ligand of >=10 heavy atoms, at resolution <=3.0 A (diffraction/EM) or by solution NMR — observed: no deposited entry with a usable (non-solvent, >=10 heavy atom) ligand
- **CRBN** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by BIRC2); axes {"linker_analogue_tier": 3, "exit_quality": 20.0, "orientation_openness": 0.2363, "neg_resolution": -2.15}
- **DCAF1** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by BIRC2); axes {"linker_analogue_tier": 3, "exit_quality": 10.27, "orientation_openness": 0.0742, "neg_resolution": -1.85}
- **KEAP1** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by MDM2); axes {"linker_analogue_tier": 2, "exit_quality": 20.0, "orientation_openness": 0.3828, "neg_resolution": -1.44}
- **VHL** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by BIRC2); axes {"linker_analogue_tier": 3, "exit_quality": 20.0, "orientation_openness": 0.1641, "neg_resolution": -1.32}

## Limits

- This is DESIGN PREP, not a validated result. Ligandability computed from one deposited holo structure is a hypothesis for testing: it says a published ligand occupies a pocket with a solvent-directed exit vector, nothing more.
- One conformer, one ligand copy, no protein flexibility, no linker sampling, no solvent model beyond an implicit 1.4 A probe. The exit vector bounds where a linker COULD leave; it does not show that any linker does leave.
- The 'linker-bearing analogue' tier is structural evidence from deposited entries, not a literature review, so it under-counts recruiters whose linker-bearing chemistry is published without a crystal structure.
- Interface geometry here is the OPEN SOLID ANGLE at the linker attachment point — the size of the orientation space available to a tethered target. Whether any orientation in it is favourable, and whether it discriminates NR4A3 from NR4A1/2, is the orientation-basin search's question, not this module's.
- fpocket druggability is computed on the deposited chains with the ligand removed; it is a pocket-shape score, not a measured affinity.
- No claim of efficacy, safety, therapeutic window, or clinical readiness is made or implied. 'Advanced' means 'carried into a computational search', never 'suitable for use'.
