# E3 recruiter staging + ligandability downselect

*E3 recruiter staging + ligandability downselect — nr4a3-program-map.md RUNG 5a(c), 'E3 breadth, free at the search stage'*

> **Honest scope.** This is DESIGN PREP, not a validated result. Ligandability computed from one deposited holo structure is a hypothesis for testing: it says a published ligand occupies a pocket with a solvent-directed exit vector, nothing more.

## Decision

**Advanced (<= 2):** CRBN, VHL

| recruiter | class | PDB | res (A) | ligand | buried | exit clear (A) | cone | open15 | analogue | decision |
|---|---|---|---|---|---|---|---|---|---|---|
| VHL | CRL2 substrate receptor (BC-box) | 9GIO | 1.486 | 3JF | 0.6648 | 25.0 | 1.0 | 0.5156 | solved_ternary | **ADVANCE** |
| CRBN | CRL4 substrate receptor (DCAF) | 9CUO | 1.6 | A1A0J | 0.6338 | 25.0 | 1.0 | 0.5488 | solved_ternary | **ADVANCE** |
| BIRC2 | monomeric RING E3 (BIR/RING) | 4HY4 | 1.249 | 1BG | 0.5999 | 25.0 | 1.0 | 0.5098 | solved_ternary | **DROP** |
| DCAF1 | CRL4 substrate receptor (DCAF) | 9PLY | 1.4 | A1CI0 | 0.8341 | 25.0 | 0.8286 | 0.1797 | solved_ternary | **DROP** |
| DCAF15 | CRL4 substrate receptor (DCAF) | 6UD7 | 2.3 | EF6 | 0.6782 | 25.0 | 1.0 | 0.2168 | bivalent_binary | **DROP** |
| DCAF16 | CRL4 substrate receptor (DCAF) | 8G46 | 2.2 | YK3 | 0.3442 | 25.0 | 1.0 | 0.7363 | solved_ternary | **DROP** |
| KEAP1 | CRL3 substrate receptor (BTB-Kelch) | 8XGK | 1.32 | A1LVB | 0.8068 | 25.0 | 1.0 | 0.1465 | bivalent_binary | **DROP** |
| FEM1B | CRL2 substrate receptor (ankyrin) | 9PW8 | 2.8 | A1CLY | 0.8694 | 25.0 | 0.5429 | 0.0449 | handle_only | **DROP** |
| RNF114 | monomeric RING E3 | — | — | — | — | — | — | — | none | **DROP** |
| MDM2 | monomeric RING E3 (nutlin-recruited) | 6Q9L | 1.13 | HTZ | 0.6609 | 25.0 | 1.0 | 0.5137 | bivalent_binary | **DROP** |

**Measured with a partner protein removed** (no partner-free structure exists for these, so burial and the exit vector are measured against a site that may be partly formed BY the removed partner): DCAF15, DCAF16.


**Backfilled** (Pareto-dominated, retained as the second recruiter so the E3 is a controlled variable downstream rather than a confound): VHL.


## Dropped set — every recruiter not advanced, with the reason

*nr4a3-program-map.md: "a silent top-N reads as 'we covered everything'". Availability is **never** a reason here — all widened arms are broadly expressed (HPA, CI run 30125742542).*

- **DCAF16** — dropped at the *gate* stage. buried fraction of the primary ligand's solvent-accessible surface >= 0.50 — observed: 0.3442
- **RNF114** — dropped at the *gate* stage. at least one deposited structure containing the recruiter with a bound non-solvent, non-cryoprotectant ligand of >=10 heavy atoms, at resolution <=3.0 A (diffraction/EM) or by solution NMR — observed: no deposited structure of this protein at all (RCSB: None entries carrying the accession)
- **BIRC2** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by CRBN); axes {"linker_analogue_tier": 3, "exit_quality": 20.0, "orientation_openness": 0.5098, "neg_resolution": -1.249}
- **DCAF1** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by CRBN); axes {"linker_analogue_tier": 3, "exit_quality": 16.572, "orientation_openness": 0.1797, "neg_resolution": -1.4}
- **DCAF15** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by CRBN); axes {"linker_analogue_tier": 2, "exit_quality": 20.0, "orientation_openness": 0.2168, "neg_resolution": -2.3}
- **FEM1B** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by CRBN); axes {"linker_analogue_tier": 1, "exit_quality": 10.858, "orientation_openness": 0.0449, "neg_resolution": -2.8}
- **KEAP1** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by CRBN); axes {"linker_analogue_tier": 2, "exit_quality": 20.0, "orientation_openness": 0.1465, "neg_resolution": -1.32}
- **MDM2** — dropped at the *pareto* stage. passed all gates but is Pareto-dominated on ligandability + interface geometry (dominated by CRBN); axes {"linker_analogue_tier": 2, "exit_quality": 20.0, "orientation_openness": 0.5137, "neg_resolution": -1.13}

## Limits

- This is DESIGN PREP, not a validated result. Ligandability computed from one deposited holo structure is a hypothesis for testing: it says a published ligand occupies a pocket with a solvent-directed exit vector, nothing more.
- One conformer, one ligand copy, no protein flexibility, no linker sampling, no solvent model beyond an implicit 1.4 A probe. The exit vector bounds where a linker COULD leave; it does not show that any linker does leave.
- The 'linker-bearing analogue' tier is structural evidence from deposited entries, not a literature review, so it under-counts recruiters whose linker-bearing chemistry is published without a crystal structure.
- Interface geometry here is the OPEN SOLID ANGLE at the linker attachment point — the size of the orientation space available to a tethered target. Whether any orientation in it is favourable, and whether it discriminates NR4A3 from NR4A1/2, is the orientation-basin search's question, not this module's.
- fpocket druggability is computed on the deposited chains with the ligand removed; it is a pocket-shape score, not a measured affinity.
- Geometry is computed against the recruiter and its OWN CRL arm only; a bound neosubstrate, PROTAC target or crystallisation partner is removed from the occluder set, because it occupies the orientation space being measured. For a recruiter with no partner-free structure (a glue-type E3), that removal means burial and the exit vector are measured against a site that may be partly formed BY the removed partner — flagged per recruiter in geometry_frame.
- ★ The rule is deliberately BLIND to recruiter-intrinsic pharmacology, and that is a real omission, not a neutral one. Several ligandable E3s are ligandable precisely because their handle is a well-developed inhibitor of the E3's own function — recruiting MDM2 with a nutlin-class handle also inhibits MDM2, and recruiting KEAP1 perturbs the KEAP1-NRF2 axis. A recruiter can therefore win on ligandability and interface geometry while carrying an on-target liability this stage cannot see. Any recruiter advanced here must have that liability assessed from the literature before it is committed to, and it is an input to the next gate, not a footnote.
- No claim of efficacy, safety, therapeutic window, or clinical readiness is made or implied. 'Advanced' means 'carried into a computational search', never 'suitable for use'.
