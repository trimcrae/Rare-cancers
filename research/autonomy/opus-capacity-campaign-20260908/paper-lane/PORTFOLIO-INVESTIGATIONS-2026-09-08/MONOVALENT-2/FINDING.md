---
id: DOC-PORTFOLIO-INVESTIGATION-MONOVALENT-2
title: "MONOVALENT-2 — the corridor closure survives experimental NR4A2 competitor geometry; the C534 attribution does not"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: MONOVALENT-2
---

# MONOVALENT-2 — portfolio investigation, second round

Worker lane under `SHARED-CONTRACT.md`. **Read-only outside this directory.** No `git add`, commit, push,
`scripts/preflight.sh`, subagent, network, GPU, paid compute, worktree or repo copy.
Model: **SELF-REPORT, NOT INDEPENDENTLY VERIFIED — `claude-opus-5`.**

## 1 · The question

> The committed covalent-reach artifact carries a **20-conformer experimental spread on the TARGET side**
> (8XTT, NR4A3 C397) and **a single modelled conformer on the COMPETITOR side** (one opened model per
> paralogue). The corridor tally that closes the chemoselectivity window reports **NR4A2 C534 as the
> first-arriving competitor in 34 of 60 cells**, with no error bar at all.
> **Substituting each of the ten committed experimental NR4A2 LBD chains through the same superposition and
> reach path: does the closure verdict change, and does the "C534 closes 34/60" attribution hold?**

Answered below, on committed bytes, at $0.

## 2 · Paper-level merit

The monovalent route's covalent axis is graded by a *race*: NR4A3 C397 against the first competitor
cysteine in the family. The published corridor tally states the winner of that race per cell as a single
integer. Whether such a tally is a measurement or a single-structure artifact decides how much weight the
route's negative can bear — and the artifact itself already accepts that principle on the target side, where
it spends a 20-conformer experimental ensemble. **The competitor side never got the same treatment**, and it
is the side the closure verdict is named after. Patient relevance is indirect and stated as such: this grades
the evidentiary standing of an in-silico route. **No efficacy, potency, selectivity, safety,
therapeutic-window or clinical claim is made or follows from anything here.**

Reconciled against `research/autonomy/portfolio-2026-09-05/recommendation.md`: that memo ranks NR4A3
degrader optimization **#5, defer**, with "no paid GPU or expanded docking campaign". This step obeys it —
**no new docking, no new sampling, no new structure prediction, no spend**: it re-uses committed coordinates
and the committed reach engine to attach an experimental error bar to a number the memo's own deferral
leaves standing.

## 3 · The exact evidence gap

* `research/modalities/nr4a3-linker-covalent-reach.json` →
  `★_family_wide_chemoselectivity_window._computed_on`, verbatim: *"the nr4a3-opened.pdb frame and the two
  superposed opened paralogue models — **single conformers, not ensembles**."*
* The same artifact's `experimental_ensemble_8xtt.reach_spread` gives min/median/max **atom counts** across
  20 experimental conformers — **for NR4A3 cysteines only**.
* Ten experimental **NR4A2** LBD chains are committed (`_s4_lane_inputs/1OVL.pdb.gz`, 6 chains;
  `7WNH.pdb.gz`, 4 chains) — established by the first-round PUB-MONOVALENT lane and **independently
  re-confirmed here**: all ten map to UniProt **P43354 at identity 1.000** and all ten resolve
  **C465, C475, C505, C534, C566**.

**Distinct from what is already done.** PUB-MONOVALENT (round 1) measured **thiol SASA exposure** on these
chains; this measures **corridor reach in backbone atoms and the closure decision**, a different quantity
from the same coordinates, and it is the quantity the tally is made of. It is not the E3-arm-free reach
enumeration, not `nr4a_af_crystal_rmsd.py` (Cα fold), not the apo-pose-recovery use of 1OVL/7WNH
(cross-docking pose recovery), not R1/R2/R3/R4, and not a new baseline review of the memo.
**No dependency data is touched**, so the SYNLETH result (EWSR1 pan-essential trap, selectivity +0.373,
`rest_frac_dependent` 0.915) and the DEP-THRESHOLD result (the threshold sweep is not computable from the
published artifact) are neither contradicted nor duplicated. No denied source (B1/B2/B4/B8/B9), no network
act of any kind.

## 4 · Re-derivation of the numbers this lane relies on (done first, before anything was built on them)

| number relied on | source | re-derived here | verdict |
|---|---|---|---|
| corridor closer tally **NR4A2 C534 = 34**, **NR4A1 C505 = 8**, none = 18, over **60** cells | `★_family_wide_chemoselectivity_window.by_convention.corridor` | recounted from the artifact | **34 / 8 / 18 of 60 — exact match** |
| the modelled NR4A2 competitor atom counts the tally is built from | committed `all_competitors_atoms["NR4A2 C*"]` | recomputed end-to-end (parse → superpose → reach) by the imported engine | **300 of 300 quantities reproduce, 0 mismatches** |
| ten experimental NR4A2 chains resolving the five LBD cysteines | PUB-MONOVALENT round 1 | re-parsed and re-aligned independently | **confirmed: 10 chains, identity 1.000, all five cysteines present in every chain** |

**Had the 300-quantity baseline not reproduced, the script exits 2 and reports no sensitivity.** It exited 0.

## 5 · The bounded step taken — result

`nr4a2_experimental_competitor_reach.py` puts each of the ten experimental chains through
`BS.superpose_paralogue` into the NR4A3-opened frame and through `LCR.reach_one_frame` with the **same
placements, same anchors, same pendants, same corridor rule and the primary clash cutoff 3.0 Å**, then
re-runs `LCR.chemoselectivity_margin` per corridor cell with the NR4A2 competitor set replaced. NR4A3 and
NR4A1 competitor atoms and the C397 target atoms are taken **unchanged** from the committed artifact.

### ✅ The closure verdict is robust

**The open/closed set of the 60 corridor cells is IDENTICAL under all ten experimental chains.** The same
**37** cells carry a non-zero window and the same **23** carry width 0. **No cell that the committed model
closes is opened by any experimental chain, and none that it opens is closed.** Window widths move by at most
**−2 / +4** backbone atoms and never to zero. Superposition quality is normal throughout (core RMSD
**1.52–1.97 Å**, alignment identity **1.000** on all ten).

### ⚠ The "C534 closes 34 of 60" attribution is NOT robust

Per-frame corridor closer tally over the same 60 cells:

| frame | NR4A2 C534 | NR4A1 C505 | NR4A2 C505 | none | median C534 corridor atoms |
|---|---|---|---|---|---|
| committed model | **34** | 8 | 0 | 18 | 20.5 |
| 1OVL_A | 35 | 7 | 0 | 18 | 20 |
| 1OVL_B | 34 | 8 | 0 | 18 | 20 |
| 1OVL_C | 35 | 7 | 0 | 18 | 20 |
| **1OVL_D** | **20** | **21** | 1 | 18 | **22** |
| 1OVL_E | 32 | 9 | 1 | 18 | 21 |
| 1OVL_F | 35 | 7 | 0 | 18 | 20 |
| 7WNH_A | 36 | 6 | 0 | 18 | 20 |
| 7WNH_B | 33 | 9 | 0 | 18 | 20.5 |
| 7WNH_C | 36 | 6 | 0 | 18 | 20 |
| 7WNH_D | 33 | 9 | 0 | 18 | 20 |

* **The C534 count ranges 20–36 across ten experimental chains against a committed 34.** In **1OVL_D** the
  modal closer flips to **NR4A1 C505 (21 cells vs 20)** — a **two-atom** upward shift in C534's median
  corridor length is enough to lose it the race in 14 cells.
* **The closer identity changes in at least one frame in 16 of 60 cells.** Every change is a swap among
  **NR4A2 C534 ↔ NR4A1 C505** (and NR4A2 C505 once); **no new closer class appears.**
* Per-cell C534 corridor length varies **max−min = 1 to 4 backbone atoms (median 2)** across the ten chains;
  pooled over all cells and frames the count spans **12–42, median 22**.
* The four **7WNH** chains additionally carry the DBD (C263, C266, C272, C280, C283, C299, C305, C315, C318,
  C323), which the LBD-only model does not. Those cysteines were included as competitors and **never once
  became the closer** — so they do not confound the verdict, and their exclusion from the modelled frame
  costs the tally nothing at this cutoff.

**Reading.** *That* the window is closed is a measurement that survives experimental competitor geometry.
*Which* cysteine closes it is a single-structure attribution with a real spread, and the specific published
sentence "NR4A2 C534 … in 34 of the 60 bivalent corridor cells" should carry **20–36 across ten experimental
chains** wherever it is used to reason about which residue a design must avoid. This **strengthens** the
route's negative and **weakens** the residue-level attribution attached to it — the honest split, and it is
not a positive outcome for the route.

### Artifact · validation/baseline · provenance · limitations · stop condition

* **Artifact** — `nr4a2-experimental-competitor-reach.json` (per-cell, per-frame closure decisions,
  superposition diagnostics, spreads, summary) and `nr4a2_experimental_competitor_reach.py`.
* **Validation / baseline** — 300/300 committed modelled NR4A2 competitor atom counts reproduced by the same
  code path before any experimental chain was read; hard exit-2 gate if they had not. Corridor tally 34/8/18
  of 60 re-derived from the artifact. Ten chains re-aligned at identity 1.000.
* **Provenance** — reach engine `research/modalities/nr4a3_linker_covalent_reach.py`
  (`reach_one_frame`, `chemoselectivity_margin`, `load_placements`, `spread`) imported **unmodified**;
  superposition `nr4a3_basin_search.superpose_paralogue` **unmodified**; numbering
  `nr4a3_covalent_handle_ensemble.pdb_to_uniprot_map` at identity ≥ 0.90; sequences from committed
  `nr4a-sequences-cache.json`; structures `research/modalities/_s4_lane_inputs/{1OVL,7WNH}.pdb.gz` and
  `results/nr4a3-matrix/{nr4a3,nr4a2}-opened.pdb`; committed cells from
  `research/modalities/nr4a3-linker-covalent-reach.json`.
* **Limitations** — (1) 1OVL/7WNH are **collapsed apo** crystals and the modelled paralogue is biased open
  along a pocket CV; a systematic competitor-distance difference is expected and refutes neither structure.
  (2) Chains within one crystal are **not independent**; 1OVL contributes 6 and 7WNH 4, and the one
  tally-flipping frame is a single 1OVL chain. (3) Only the **NR4A2** competitor set varies — the NR4A3
  target reach, the NR4A3 conserved competitors and **all NR4A1 competitors remain single-conformer modelled
  readings**, and **NR4A1 has no experimental coordinates in this checkout at all**, so the NR4A1 C505 side
  of every swap above is itself un-error-barred. (4) Corridor convention at **one** cutoff (3.0 Å); the
  committed 2.0/2.6/3.0/3.4 sweep is not reproduced. (5) Geometry only — no thiol pKa, reactivity, adduct,
  potency, selectivity, safety, therapeutic window or clinical readiness is computed or implied.
* **Stop condition (met)** — stop when the closure decision has been recomputed under every committed
  experimental NR4A2 chain, or when the modelled baseline fails to reproduce. The baseline reproduced and all
  ten chains ran. **NR4A1 remains out of reach without a network fetch, which is outside worker authority;
  the lane stops there rather than substituting a model for a missing structure.**

## 6 · Honest outcome

**Not a new paper, and no new endpoint claimed.** This is a sensitivity the committed artifact does not have:
the competitor half of the decision quantity now carries an experimental spread, computed by the artifact's
own engine. The load-bearing negative (the window closes) got **harder to dismiss**; the residue-level
attribution attached to it got **softer**, with a digit-for-digit range. Both are preserved.

**No shared file is edited and no diff is proposed** — this lane's output is additive evidence, not a
correction to committed prose. A future owner act could attach the 20–36 range to the tally sentence; that is
an owner decision, not a worker one.

**Next credible independent work, in order:** (1) obtain NR4A1 LBD coordinates by an ordinary permitted
access and repeat this exact substitution for NR4A1 C505/C551 — the script takes it unchanged, and NR4A1
C505 is the residue that wins the swaps above; (2) repeat across the committed 2.0/2.6/3.4 cutoffs to
separate clash-rule sensitivity from structural sensitivity; (3) the first-round lane's untouched item — the
memo's backlog item 5, the antagonism-window number.
