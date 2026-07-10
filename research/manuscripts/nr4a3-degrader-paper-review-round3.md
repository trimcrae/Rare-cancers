# NR4A3 binder paper — Round-3 review response ledger

Tracking every point in the round-3 JCIM-style review (2026-07-10). Goal per trimcrae: **address
everything; no leftovers.** Status keys:

- **DONE** — fixed this round (commit noted) or already fixed and confirmed by the reviewer's own delta table.
- **EDIT** — manuscript/SI text change I execute in-session (no new compute).
- **COMPUTE** — gated on a simulation; in-flight or to-dispatch.
- **OWNER** — trimcrae action at submission (e.g. mint Zenodo DOI).

The reviewer's recommendation moved to *"major revision with a narrow, credible path to acceptance."*
Four decisive axes remain: (1) repaired ABFE survives overlap/protocol audit; (2) persistence-vs-accessibility
kept distinct everywhere; (3) 8XTT robustness survives a matched-frame null + precision analysis;
(4) reorganize so the central result (experimental-structure-informed dynamic pocket + conditional ABFE) is unmistakable.

---

## P0 — submission blockers

| # | Item | Comments | Status |
|---|------|----------|--------|
| P0.1 | Repair NR4A2 λ-overlap (min adj 0.003), re-reduce | 2 | COMPUTE — fold into 8XTT-seeded ABFE re-run (add λ near NR4A2 decoupling endpoint); gated on seed-MD (in progress) |
| P0.2 | ABFE protocol audit; rerun T4L at production-matched sampling if feasible | 4,5 | COMPUTE + EDIT (reword calibration/benchmark language now) |
| P0.3 | Identify exact ABFE stereoisomer unambiguously | 6 | EDIT — state compound/isomer ID, isomeric SMILES, stereocenters, protonation, coord path/hash; show both iso08 + as-generated if both run |
| P0.4 | Move ABFE to Results §2.7 + main ABFE figure (Fig 6) | 1 | EDIT — new §2.7; Fig 6 panels A–D (per-replicate ΔΔG NR4A3–NR4A1, –NR4A2, convergence traces, overlap incl. repaired NR4A2) |
| P0.5 | Reclassify Gate 3: persistence supported, equilibrium accessibility unresolved (3A/3B split) | 13,55 | EDIT |
| P0.6 | Global deletion of stale induced-fit/metastability/population/"not-bias-artifact" language | 12,14,17,18,50,+inconsist. list | EDIT |
| P0.7 | Remove ABFE absolute-engagement contradiction ("yields whether denovo_401 engages") | 3 | EDIT |
| P0.8 | Matched 8XTT-frame decoy null | 8,12 | COMPUTE — running (run 29092770899) |
| P0.9 | fpocket on all 3 release replicas (+ autocorr-aware descriptive CI) | 15,16 | COMPUTE — dispatching (gpu-mdpocket on release_rep1/rep2); EDIT to add per-replica table |
| P0.10 | Fix pocket-tracking Methods (matching algorithm, split/merge/no-match, score-0 policy, blinding) | 46 | EDIT |

## P1 — high-value strengthening

| # | Item | Comments | Status |
|---|------|----------|--------|
| P1.11 | AF2↔NMR vs NMR↔NMR RMSD decomposition | 8(§2.2) | COMPUTE (cheap) + EDIT |
| P1.12 | Score denovo_401 + decoys over all 20 8XTT conformers | 12 | COMPUTE |
| P1.13 | Do high-8XTT-fpocket scores correlate with local NMR coordinate dispersion | 13 | COMPUTE (cheap) |
| P1.14 | True contact-graph PocketMiner null | 14 | COMPUTE — have spatial-contiguous null; add contact-graph variant |
| P1.15 | Spatial/selection-aware divergence permutation | 19,20 | COMPUTE + EDIT (don't advertise a permutation test that doesn't exist yet) |
| P1.16 | Generation-matched null | 35,36 | COMPUTE — MM-GBSA resume running; reduce step after |
| P1.17 | 8XTT-started dynamics | — | COMPUTE — seed-MD in progress |
| P1.18 | ABFE component decomposition (ΔG_solv shared; per-receptor cplx + SSC; Boresch anchors) | 7 | EDIT (from SI §S7 data) |

## P2 — manuscript surgery

| # | Item | Comments | Status |
|---|------|----------|--------|
| P2.19 | Put 8XTT first in Results (§2.1 reorder → 8XTT / AF2-working-model / enhanced sampling) | 8,9 | EDIT |
| P2.20 | Remove denovo_15/94/57/111 archaeology from main text → SI | 28,29,52 | EDIT |
| P2.21 | Move 6k screen fully to SI | 23 | EDIT |
| P2.22 | Move EMC addiction/safety essay to SI (keep 1 short para) | 49 | EDIT |
| P2.23 | Rewrite Methods into subsections 4.1–4.14 | 45 | EDIT |
| P2.24 | Replace Fig 4 family matrix with falsification-controlled funnel | 11,fig | EDIT (figure regen) |
| P2.25 | Add main ABFE figure (= P0.4 Fig 6) | 1 | EDIT |
| P2.26 | Rewrite Abstract → 3–4 concise sentences | 57 | EDIT |
| P2.27 | Shorten/retitle (≤12 words; reconsider "Opening"/"binder") | 56 | EDIT |
| P2.28 | Conventionalize references (strip annotations; complete entries incl. titles) | 59 | EDIT |
| P2.29 | Mint + cite the archive DOI | 60 | OWNER (submission) — package manifest EDIT now |
| P2.30 | Expand AI disclosure: exact models/dates, Acknowledgments stub, defensible validation wording, figures-AI statement | 61 | EDIT (model IDs deferred to archive per repo model-ID rule) |

## Figure 1 redesign (comment 11) — EDIT
8XTT ensemble at mapped site (A); fpocket strip/violin over all 20 conformers (B); AF2 static vs that
distribution (C); NR reference sites + D* line (D); AF2–8XTT pocket-local divergence (E). Demote the 0.931 max.

## The 24-item internal-inconsistency list — all EDIT (mapped to comments above)
1 "0.495 conservative" (9) · 2 "validated druggable band" (10) · 3 "population pending release" (12/14/50) ·
4 "induced-fit cavity" (12) · 5 "metastable" (12) · 6 "not a bias artifact" (12) · 7 "most divergent zone" (19) ·
8 Abstract "Fisher/permutation" must match a real test (20) · 9 "as NR4A1 agonism demands" (24) ·
10 "endpoint free energy decides" (25) · 11 "per-paralogue FEP Kd's feed" (26) · 12 "release-derived induced-fit" (12) ·
13 "all ~191 developable" (34) · 14 "single-snapshot margins carry SD" (39) · 15 S1 multi/single-snapshot (38) ·
16 "lead queued for FEP" (48) · 17 "calibrated on two known systems" (4) · 18 "ABFE tells whether engages" (3) ·
19 "FEP complete" vs pending repair (53) · 20 exact stereoisomer (6) · 21 "planned gating step" ternary (26/27) ·
22 "NR4A2 tox CNS-localized" (51) · 23 Caveat 6 = denovo_15 (52) · 24 §2.6→§4 renumber (47).

## Other specific rewordings — EDIT
- 21 alanine-scan = ligand-binding sensitivity, not receptor functional cost.
- 22 "spare NR4A1/NR4A3 myeloid tumour-suppressor" → spare NR4A1, avoid combined NR4A1+NR4A3 loss state.
- 23 "demonstrated, tunable design axis" → "suggests a tunable design axis".
- 30 "generation was clean" → "high validity and uniqueness".
- 31 asymmetric-setup "conservative" → "limitation of uncertain direction" (unless shown across library).
- 32 `confirmed_selective` label → "pipeline-classified …, subsequently shown non-specific".
- 33 38-decoy 95th pct → empirical percentile/rank + bootstrap + ECDF; "ranked above 37/38".
- 37 Fig 5 "only denovo_401 holds" → "after protonation resolution, only denovo_401 remains".
- 40 one neg control → "behaved in the expected direction".
- 41 margin−SD → prespecified advancement heuristic (frame-to-frame SD), not a CI.
- 42 "first multi-snapshot-confirmed" → "first candidate retaining an NR4A3-favoured endpoint margin through the multi-snapshot tier".
- 43 delete "de-bias" (rerun estimates seed sensitivity, not winner's-curse de-bias).
- 44 pKa methodology (tool/version, protomers, pop at pH 7.4, tautomer policy).
- 48 global stale-status sweep: queued/planned/next tier/remains the gate/in flight/follow-up/pending.
- 54 Gate 4 reporting interpretation (predicted NR4A3-favoured profile in silico, not physical binding).
