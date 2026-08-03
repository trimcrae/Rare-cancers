# Known-answer pose recovery — the SITE question and the DOCKING question, separated

⛔ **GENERATED FILE — do not edit.** Every number here is rendered from [`apo-pose-recovery.json`](./apo-pose-recovery.json) by `apo_pose_recovery.render_markdown`, which owns none of them. Edit the module or re-run (`MODE=report`), never this file.

Pre-registered verdict, **unchanged by anything below**: **INCONCLUSIVE** — C1 FAILED: the protocol could not recover the pose even from the HOLO receptor (19.53 A > 2.00 A), so the primary result measures the docking protocol, not the apo->holo induced-fit gap. Pre-registered: this outcome is INCONCLUSIVE, not a failure of the apo pipeline.


## 1 · Q-DOCKING — given the correct site, does blind apo→holo docking recover the pose?

Arm: `C3_oracle_box_apo` (apo receptor, box on the crystallographic ligand). Control: `C1c_self_dock_holo_oracle_box`. Bands are the pre-registered 2.00 / 4.00 Å.


| pair | protein | ligand | apo RMSD (Å) | fnat | answer | ceiling (Å) | ceiling passed |
|---|---|---|---|---|---|---|---|
| 4RZF→4REF | NR4A1 / Nur77 | 3N0 | 3.489 | 0.778 | INCONCLUSIVE — the protocol ceiling itself missed (2.849 A), so this pair cannot grade the docking | 2.849 | False |
| 4RZF→4RE8 | NR4A1 / Nur77 | 3MJ | 3.572 | 0.643 | INCONCLUSIVE — the protocol ceiling itself missed (3.362 A), so this pair cannot grade the docking | 3.362 | False |
| 2QMV→9F7W | PPARG | 2OH | 6.133 | 0.500 | NOT RECOVERED | 0.637 | True |
| 2QMV→9V8H | PPARG | BRL | 8.957 | 0.188 | INCONCLUSIVE — the protocol ceiling itself missed (6.809 A), so this pair cannot grade the docking | 6.809 | False |
| 5G42→7NPC | RORC / RORgt | ULT | 13.212 | 0.045 | NOT RECOVERED | 0.275 | True |
| 5G42→6T4X | RORC / RORgt | L3E | 12.434 | 0.136 | NOT RECOVERED | 0.556 | True |

**3 of 6 pairs gradeable; 0 RECOVERED, 0 PARTIAL, 3 NOT RECOVERED.** a pair whose protocol ceiling (C1c) missed cannot grade the docking and is counted out, not averaged in — the same pre-registered rule C1 applies to the primary


## 2 · Q-SITE — does site selection put the ligand inside the box it draws?

Geometric endpoint, no docking in it. `SITE FOUND` iff the crystallographic ligand's centroid lies inside the box.


| pair | protein | NR4A3 aligned identity | pipeline (sequence) | structure transfer | fpocket top | interpretable |
|---|---|---|---|---|---|---|
| 4RZF→4REF | NR4A1 / Nur77 | 0.6000 | SITE MISSED | SITE MISSED | SITE FOUND | True |
| 4RZF→4RE8 | NR4A1 / Nur77 | 0.6000 | SITE MISSED | SITE MISSED | SITE FOUND | True |
| 2QMV→9F7W | PPARG | 0.2407 | SITE MISSED | SITE MISSED | SITE FOUND | False |
| 2QMV→9V8H | PPARG | 0.2407 | SITE MISSED | SITE MISSED | SITE FOUND | False |
| 5G42→7NPC | RORC / RORgt | 0.2727 | SITE MISSED | SITE MISSED | SITE FOUND | False |
| 5G42→6T4X | RORC / RORgt | 0.2727 | SITE MISSED | SITE MISSED | SITE FOUND | False |

**Over the 2 pair(s) that are evidence about the pipeline at all:** pipeline sequence transfer found the site on 0, the independent structural transfer on 0, fpocket's own top pocket on 2. counted over interpretable pairs only; every excluded pair carries the reason it was excluded in its `disqualifiers`


### Why pairs are excluded, and what the confound control says

- **4RZF→4REF (NR4A1 / Nur77)** — BOTH an independent structural transfer and the pipeline's sequence transfer put NR4A3's Pocket-5 somewhere this ligand is not. The crystallographic answer is not in this receptor's Pocket-5-equivalent site, so 'the pipeline missed the site' is the benchmark's design and not a demonstrated defect
- **4RZF→4RE8 (NR4A1 / Nur77)** — BOTH an independent structural transfer and the pipeline's sequence transfer put NR4A3's Pocket-5 somewhere this ligand is not. The crystallographic answer is not in this receptor's Pocket-5-equivalent site, so 'the pipeline missed the site' is the benchmark's design and not a demonstrated defect
- **2QMV→9F7W (PPARG)** — BOTH an independent structural transfer and the pipeline's sequence transfer put NR4A3's Pocket-5 somewhere this ligand is not. The crystallographic answer is not in this receptor's Pocket-5-equivalent site, so 'the pipeline missed the site' is the benchmark's design and not a demonstrated defect
  - ⛔ OUT OF THE PIPELINE'S REGIME: P37231 is not one of the proteins the pipeline transfers Pocket-5 onto (nr4a3_warhead.PARALOGUES = ['P22736', 'P43354'], plus NR4A3's own 8XTT). The transfer ran here at 0.2407 aligned identity. Finding that an NR4A3 cryptic pocket does not land on this receptor's ligand site is close to expected and is NOT evidence that site selection is broken for NR4A3.
- **2QMV→9V8H (PPARG)** — BOTH an independent structural transfer and the pipeline's sequence transfer put NR4A3's Pocket-5 somewhere this ligand is not. The crystallographic answer is not in this receptor's Pocket-5-equivalent site, so 'the pipeline missed the site' is the benchmark's design and not a demonstrated defect
  - ⛔ OUT OF THE PIPELINE'S REGIME: P37231 is not one of the proteins the pipeline transfers Pocket-5 onto (nr4a3_warhead.PARALOGUES = ['P22736', 'P43354'], plus NR4A3's own 8XTT). The transfer ran here at 0.2407 aligned identity. Finding that an NR4A3 cryptic pocket does not land on this receptor's ligand site is close to expected and is NOT evidence that site selection is broken for NR4A3.
- **5G42→7NPC (RORC / RORgt)** — BOTH an independent structural transfer and the pipeline's sequence transfer put NR4A3's Pocket-5 somewhere this ligand is not. The crystallographic answer is not in this receptor's Pocket-5-equivalent site, so 'the pipeline missed the site' is the benchmark's design and not a demonstrated defect
  - ⛔ OUT OF THE PIPELINE'S REGIME: P51449 is not one of the proteins the pipeline transfers Pocket-5 onto (nr4a3_warhead.PARALOGUES = ['P22736', 'P43354'], plus NR4A3's own 8XTT). The transfer ran here at 0.2727 aligned identity. Finding that an NR4A3 cryptic pocket does not land on this receptor's ligand site is close to expected and is NOT evidence that site selection is broken for NR4A3.
  - ⛔ THE DEPOSITOR DECLARES THE LIGAND ALLOSTERIC (ROR(gamma)t ligand binding domain in complex with allosteric ligand FM156). An orthosteric site transfer cannot be graded against a ligand in a declared allosteric pocket.
- **5G42→6T4X (RORC / RORgt)** — BOTH an independent structural transfer and the pipeline's sequence transfer put NR4A3's Pocket-5 somewhere this ligand is not. The crystallographic answer is not in this receptor's Pocket-5-equivalent site, so 'the pipeline missed the site' is the benchmark's design and not a demonstrated defect
  - ⛔ OUT OF THE PIPELINE'S REGIME: P51449 is not one of the proteins the pipeline transfers Pocket-5 onto (nr4a3_warhead.PARALOGUES = ['P22736', 'P43354'], plus NR4A3's own 8XTT). The transfer ran here at 0.2727 aligned identity. Finding that an NR4A3 cryptic pocket does not land on this receptor's ligand site is close to expected and is NOT evidence that site selection is broken for NR4A3.
  - ⛔ THE DEPOSITOR DECLARES THE LIGAND ALLOSTERIC (ROR(gamma)t ligand binding domain in complex with 25-hydroxycholesterol and allosteric ligand FM26). An orthosteric site transfer cannot be graded against a ligand in a declared allosteric pocket.

## 3 · How hard a test is this panel? (the caveat, measured)

Apo→holo Cα movement **at the ligand site**. A pair below 1.00 Å is a re-dock with extra steps and cannot demonstrate apo→holo transfer.


| pair | protein | site Cα RMSD (Å) | global Cα RMSD (Å) | n site residues | large? |
|---|---|---|---|---|---|
| 4RZF→4REF | NR4A1 / Nur77 | 0.142 | 0.457 | 9 | no |
| 4RZF→4RE8 | NR4A1 / Nur77 | 0.172 | 0.227 | 14 | no |
| 2QMV→9F7W | PPARG | 3.862 | 3.383 | 12 | **yes** |
| 2QMV→9V8H | PPARG | 2.161 | 2.808 | 16 | **yes** |
| 5G42→7NPC | RORC / RORgt | 6.460 | 2.775 | 22 | **yes** |
| 5G42→6T4X | RORC / RORgt | 6.384 | 2.734 | 22 | **yes** |

4 of 6 pairs move at least 1.00 A of Ca at the ligand site, so the panel is not only near-rigid re-docks. Any pair below that line is a weak test of apo->holo transfer and must not be quoted as one.

⚠ the induced fit is measured AT THE NATIVE LIGAND SITE. Where a blind arm's box is somewhere else, the rearrangement that arm actually faced is not this number.


## 4 · What the deposits themselves declare


| pair | engineered substitutions (holo) | any in the ligand's contact shell | ligand declared allosteric |
|---|---|---|---|
| 4RZF→4REF | LEU118→TRP | no | no |
| 4RZF→4RE8 | none | no | no |
| 2QMV→9F7W | none | no | no |
| 2QMV→9V8H | none | no | no |
| 5G42→7NPC | none | no | **yes** |
| 5G42→6T4X | none | no | **yes** |

## 5 · What moved and what did not


**Unchanged (pre-registered)**

- PRIMARY endpoint: symmetry-corrected heavy-atom RMSD of the top pose from the APO receptor, through the pipeline's own site transfer, after site-Ca superposition. Bands 2.00 / 4.00 A.
- C1 (self-dock into holo through the pipeline's box) still makes a pair INCONCLUSIVE when it fails.
- C2 random-in-box null and its 0.05 power line.
- C3 oracle box remains a decomposition and never a headline.
- `verdict()` is unchanged: no added arm can turn a NOT RECOVERED into a pass.

**Added**

- Q-SITE: a GEOMETRIC site endpoint — SITE FOUND iff the crystallographic ligand's centroid lies inside the box the route drew. No docking in it, so it is deterministic.
- Q-DOCKING: the docking question asked with the site handed over (C3 arm) against its own ceiling control (C1c), so a docking answer never borrows the site arm's evidence.
- C4 structural transfer: NR4A3 Pocket-5 carried onto the same receptor a second time by CE structural superposition (Bio.PDB.cealign) instead of by BLOSUM62, plus its blind arm and its own self-dock control. This is the confound control: only two independent transfers can separate 'the alignment failed' from 'the ligand is not in the Pocket-5-equivalent site'.
- C5 declared facts read from the deposit: SEQADV engineered substitutions (and whether any is one of the ligand's own contact residues) and a holo-title allosteric declaration.
- A regime gate on the site question, computed from `nr4a3_warhead.PARALOGUES` rather than typed: a receptor the pipeline never transfers onto is not evidence about the pipeline's site step.
- LARGE_INDUCED_FIT_A = 1.00 A: a REPORTING band on the apo->holo site Ca RMSD, gating nothing.

**Corrected — superseded values retained (CLAUDE.md §1.2)**

- ``boxes.pipeline_box_fpocket_rank._reads`` — was: asserted 'the site the pipeline's Pocket-5 transfer selected IS a cavity on this receptor' whenever the transferred residues touched a pocket by even one residue — printed beside `n_shared_residues: 1` on the headline pair. Now: the rank is unchanged and still reported; the SENTENCE is conditioned on the share, and the share itself (`frac_transferred_residues_in_that_pocket`) is now emitted
- `PAIR_BUDGET_S / PANEL_BUDGET_S` — was: 420 s per pair / 2700 s per panel. Now: 900 s / 4500 s — a wall-clock hang-guard raised for the added arms. It can only decide whether an arm RUNS (recorded UNRUN if not), never what an arm returns.

⛔ This page claims nothing about NR4A3 selectivity, efficacy, safety or clinical readiness. It grades an instrument, not a molecule.

