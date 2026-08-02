# Known-answer pose recovery — the SITE question and the DOCKING question, separated

⛔ **GENERATED FILE — do not edit.** Every number here is rendered from [`apo-pose-recovery.json`](./apo-pose-recovery.json) by `apo_pose_recovery.render_markdown`, which owns none of them. Edit the module or re-run (`MODE=report`), never this file.

Pre-registered verdict, **unchanged by anything below**: **INCONCLUSIVE** — C1 FAILED: the protocol could not recover the pose even from the HOLO receptor (19.53 A > 2.00 A), so the primary result measures the docking protocol, not the apo->holo induced-fit gap. Pre-registered: this outcome is INCONCLUSIVE, not a failure of the apo pipeline.


⚠ **THIS ARTIFACT DOES NOT CONTAIN `site_vs_docking` or `induced_fit_panel`.** It predates the site/docking split, so the sections below are UNREAD, not empty. Re-run `MODE=run` to produce them; nothing here may be quoted as a measurement.


## 1 · Q-DOCKING — given the correct site, does blind apo→holo docking recover the pose?

Arm: `C3_oracle_box_apo` (apo receptor, box on the crystallographic ligand). Control: `C1c_self_dock_holo_oracle_box`. Bands are the pre-registered 2.00 / 4.00 Å.


| pair | protein | ligand | apo RMSD (Å) | fnat | answer | ceiling (Å) | ceiling passed |
|---|---|---|---|---|---|---|---|

**None of None pairs gradeable; None RECOVERED, None PARTIAL, None NOT RECOVERED.** 


## 2 · Q-SITE — does site selection put the ligand inside the box it draws?

Geometric endpoint, no docking in it. `SITE FOUND` iff the crystallographic ligand's centroid lies inside the box.


| pair | protein | NR4A3 aligned identity | pipeline (sequence) | structure transfer | fpocket top | interpretable |
|---|---|---|---|---|---|---|

**Over the None pair(s) that are evidence about the pipeline at all:** pipeline sequence transfer found the site on None, the independent structural transfer on None, fpocket's own top pocket on None. 


### Why pairs are excluded, and what the confound control says


## 3 · How hard a test is this panel? (the caveat, measured)

Apo→holo Cα movement **at the ligand site**. A pair below 0.00 Å is a re-dock with extra steps and cannot demonstrate apo→holo transfer.


| pair | protein | site Cα RMSD (Å) | global Cα RMSD (Å) | n site residues | large? |
|---|---|---|---|---|---|



⚠ 


## 4 · What the deposits themselves declare


| pair | engineered substitutions (holo) | any in the ligand's contact shell | ligand declared allosteric |
|---|---|---|---|
| 4RZF→4REF | UNREAD | UNREAD | no |
| 4RZF→4RE8 | UNREAD | UNREAD | no |
| 2QMV→9F7W | UNREAD | UNREAD | no |
| 2QMV→9V8H | UNREAD | UNREAD | no |
| 5G42→7NPC | UNREAD | UNREAD | no |
| 5G42→6T4X | UNREAD | UNREAD | no |

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

