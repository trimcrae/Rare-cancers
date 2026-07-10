# NR4A3 paper — Round-6 review response ledger (2026-07-10)

Reviewer verdict: **major revision, "close to a defensible submission state once a small number of
load-bearing analyses finish."** Single manuscript (`nr4a3-degrader-paper.md` + `-paper-SI.md`).

## ✅ ALL NON-GATED round-6 items DONE this session

**P0 factual errors (reviewer's newly-found):**
- **c6** — `denovo_401` "amide-bearing" was FALSE (SMILES has no N). → "no basic nitrogen (ether/aryl/tertiary-alcohol scaffold)".
- **c7** — `denovo_111` "physiologically dominant cation" unsupported by the rule-based SMARTS. → reframed everywhere as protonation-state *sensitivity*; "conservatively not advanced" (paper + SI).
- **c25** — ternary "within ubiquitin reach of CRBN" unsupported (no CRL4/E2~Ub). → "near the modeled CRBN-facing interface (closest Lys-Nζ to nearest CRBN heavy atom); CRBN-proximity proxy, not ubiquitin-transfer geometry" (paper + SI).
- **c53** — no §3 (jumped §2→§4). → Methods §3, Limitations §4, Falsification §5 (ascending-source renumber).

**Metad equivalent-state overclaims:** c8 (deleted "druggable geometry reachable across replicas"), c9 ("closed↔open"→"low-Rg↔high-Rg", "druggable window"→"reference Rg window"), c10 (event/crossing definition + thresholds flagged), c11 ("closed basin"→"single resolved minimum" ×3), c12 ("low-energy druggable frame"→"selected reference frame …low apparent free energy in the original single-profile analysis"), c17 ("rules out sub-ns collapse"→"no prompt sub-ns collapse observed"), c18 ("unbiased release frame"→"release-derived frame from a bias-free continuation"), c19 ("static structure understated the pocket"→"enhanced sampling generated cavity-bearing geometries not in the static AF2 snapshot").

**§2.1 8XTT framing (P0 c3/c4):** "independent of AF2 and MD"→"independent experimental conformers at the AF2-derived mapped site; a transfer test, not an AF2-independent site discovery"; "same fpocket pipeline"→"corresponding fpocket workflow (pinning is part of the harmonized rerun)"; **c5** 4/20 denominator clarified (score obtained for all 20 → 4/20 on both denominators).

**Pocket-identity (P0 c1/c2) — text acknowledgment:** Methods now states the REQUIRED CHANGE (score-free canonical-residue site definition + composite match gate + pinned fpocket) and the DEPENDENCY AUDIT (does the exact release frame used to *generate* denovo_401 still qualify) as the primary submission gate. *(The rerun itself is gated — below.)*

**Generative/ABFE/Falsification:** c15 (Gate 2 consistently "initially passed…provisional"), c16/54 (Abstract "druggability persists"→"geometric persistence…fractions await harmonized tracking"; "converged opening FE"→"common quantitative FE profile"), c20/21/22/24/26/27/28/29/31/32/33/34/35 (headings honest; lead→candidate; softened selective-engagement / programmable / handle-scarcity / cross-target-docking / ternary-adds-no-selectivity / stereochemistry / decoy-mechanism / de-noising-tier / single-draw / frame-artifact), c36 ("affinity-grade"→"higher-tier explicit-solvent FE test"), c37/46 (ΔΔG offset-invariance / "better-behaved" bounded to shared-solvent-leg cancellation), c41 ("validated equal"→"no resolved improvement"), c44 (hinge "justified"→"motivated; sensitivity not evaluated"), c45 (mutation-FEP softened), c51 (co-folding "regime where unreliable"→"low ligand-placement confidence; does not corroborate pose/ordering"), c52 (Falsification Gate 3B/Gate-4 §refs/metad-frame fixed).

**Editorial:** c47 (EMC-dependence + safety block moved to new SI §S9; one paragraph kept), c48/49/50 (stale Limitations caveats), c23 (6k screen already 1 sentence + SI §S1), c42/43 (Methods de-dup vs §2.8; duplicate dedup sentence removed), c57 (AI Acks shortened), c13 (metad 3B "bottom line first" — withdrawn estimate no longer leads), c40/c55 (method/software refs 37-52 added, verified; ref 35 title completed; ref 36 title genuinely unverifiable → identifier-only).

## ⛔ GATED on tonight's GPU fleet (the reviewer's decisive questions)
1. **Harmonized pocket rerun + pinned fpocket + score-free site definition** (P0 1/2, P1 11-14/16/18) → and the **downstream dependency audit** (does the generation receptor survive).
2. **NR4A2 λ-repair** (P0 6): old/new overlap + old/new ΔΔG.
3. **8XTT-anchored NR4A3 ABFE sensitivity** (P0 7).
4. **Production-matched T4L rerun** at 2 ns/window under the repaired λ schedule (c39/P1 23).
5. **Fig 2 → cross-replica F(Rg)/drift/minima** (c14/P1 15) and **Fig 1 → 8XTT-centered** (c44).
6. Matched 8XTT decoy null, all-20 harmonized analysis, AF2↔NMR RMSD decomposition, contact-graph PocketMiner null, selection-aware permutation, generation-matched null (P1 17-22).

## OWNER (submission-time)
Mint the Zenodo archive DOI (c56); ref 36 title.
