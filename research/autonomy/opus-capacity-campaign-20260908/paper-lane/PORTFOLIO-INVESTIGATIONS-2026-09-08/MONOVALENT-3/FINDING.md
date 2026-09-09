---
id: DOC-PORTFOLIO-INVESTIGATION-MONOVALENT-3
title: "MONOVALENT-3 — the corridor closure is direction-robust across the clash sweep, but MONOVALENT-2's 'identical on all 60 cells' holds only at the two loosest cutoffs"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: MONOVALENT-3
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
proposal: FOLLOWTHROUGH-DISCOVERY P4 (rank 4)
---

# MONOVALENT-3 — clash-cutoff sweep of the experimental NR4A2 competitor closure

Worker lane under `SHARED-CONTRACT.md`. **Read-only outside this directory.** No `git add`, commit, push,
`scripts/preflight.sh`, subagent, network, GPU, paid compute, worktree or repo copy. Structures and
conformer trees read **in place**.
Model: **SELF-REPORT, NOT INDEPENDENTLY VERIFIED — `claude-opus-5`.**

Repo HEAD at execution: `1e35538daee86e1a34345340f7562d1e91147fa0` (the proposal was written at
`04a4e0ef…`; other lanes have committed since). Both declared input hashes re-verified at dispatch and
**MATCH**: `nr4a3_linker_covalent_reach.py` = `25e3949d215890736fff45aafc80cf315aefeb350c90b3e34b41889c2ca533ff`,
`nr4a3-linker-covalent-reach.json` = `d5ebc0a3db8d4cf2a9e8ea3827c02e4681fb733fbd9e3bb15f1bd7b6555e3320`.

## 1 · The question

> MONOVALENT-2 recomputed the corridor closure under ten **experimental** NR4A2 LBD chains at the
> **primary clash cutoff only** (3.0 Å). Closure survived on all 60 cells, while the "NR4A2 C534 closes
> 34 of 60" attribution softened to a per-chain range of 20–36. The cutoff dimension was untested.
> **Is that surviving closure a structural fact, or an artifact of the primary clash cutoff?**

Answered below on committed bytes, at $0, over the sweep the engine already declares:
`CLASH_SWEEP_A = (2.0, 2.6, 3.0, 3.4)` — `research/modalities/nr4a3_linker_covalent_reach.py` line 136,
**imported, never redefined, never adjusted.**

## 2 · Paper-level merit

The monovalent covalent axis is graded by a race between NR4A3 C397 and the first competitor cysteine in
the family. The engine's author declared the clash cutoff as *the one new parameter in the module* and
computed a whole sweep precisely so that no single value would be load-bearing — yet every downstream
sensitivity, MONOVALENT-2's included, has been run at one value of it. A robustness claim quoted from a
single cell of a two-dimensional space is not yet a robustness claim. Establishing which of the two
dimensions the verdict actually depends on decides how much weight the route's negative can bear, and how
a residue-level attribution may be quoted in prose. Patient relevance is **indirect and stated as such**:
this grades the evidentiary standing of an in-silico route.

**No efficacy, potency, selectivity, safety, therapeutic-window or clinical-readiness claim is made or
follows from anything here.** A geometric corridor result is never one of those.

## 3 · The exact evidence gap

MONOVALENT-2's own §5 limitation 4, verbatim: *"Corridor convention at **one** cutoff (3.0 Å); the
committed 2.0/2.6/3.0/3.4 sweep is not reproduced."* Its next-work item 2 names this exact task.

What made it runnable and is new here: the committed artifact **already carries all four cutoffs** for
every opened frame — `designed_frame.rows` (NR4A3, 70 rows) and `paralogue_control.opened.NR4A1.rows`
(60 rows) each publish `corridor_atoms` at `2.0 / 2.6 / 3.0 / 3.4`. So the whole non-NR4A2 half of every
cell is available at every cutoff from committed bytes, and only the ten experimental NR4A2 chains had to
be recomputed. Distinct from PUB-MONOVALENT (thiol SASA on the same chains) and from MONOVALENT-2 (one
cutoff): this is the **closure decision as a function of the clash rule**.

## 4 · Gates — honoured in the order the proposal sets them

| gate | requirement | observed | verdict |
|---|---|---|---|
| **A** (before any experimental chain is read) | 300/300 committed modelled NR4A2 competitor atom counts reproduce end to end; hard **exit 2** otherwise | **300 / 300, 0 mismatches**, alignment identity 1.0000 | ✅ PASS |
| **B** | at the primary cutoff the sweep returns MONOVALENT-2's published tally **exactly** | **NR4A2 C534 = 34, NR4A1 C505 = 8, none = 18, over 60 cells** | ✅ PASS |

Two further controls, reported and not gating:

* The recomputed primary-cutoff cells equal the committed corridor cells with **0 field mismatches** over
  `target_atoms`, `window_lo`, `window_hi`, `width`, `closed_by`, `closed_at_atoms` × 60 cells.
* The recomputed modelled NR4A2 frame also reproduces the committed `NR4A2-opened` rows at the **other
  three** cutoffs: **300/300 at 2.0, 300/300 at 2.6, 300/300 at 3.0, 300/300 at 3.4**.
* Reach-rule invariant violations: **0 in all ten experimental frames.**

Had either gate failed, the failure would have been the result and the run would have stopped. It did not.

## 5 · Result — the answer is split, and one half is a negative

### 5.1 ✅ Direction is robust at every cutoff — the experimental chains only ever CLOSE

Across **4 cutoffs × 10 chains × 60 cells = 2 400 decisions**, the experimental substitution produced
**24 open/closed disagreements with the committed modelled competitor, and every single one of the 24 is
in the same direction: the experimental chain CLOSES a cell the modelled competitor leaves open.**
**Not once, at any cutoff, does an experimental chain open a window the committed model closes.** The
load-bearing negative — that the chemoselectivity window closes — is therefore not a cutoff artifact and
is never weakened by real competitor geometry.

### 5.2 ⚠ But "identical on all 60 cells" is a property of the two LOOSEST cutoffs only

MONOVALENT-2's headline was that the open/closed set is *identical* under all ten chains. That is exact
at the primary cutoff — and it is **not** a general fact:

| cutoff | committed open cells | experimental open cells (range over 10 chains) | cell×frame open/closed differences | set identical in every frame? |
|---|---|---|---|---|
| **2.0 Å** | 40 | **37–38** | **22** | ❌ **no** |
| **2.6 Å** | 42 | **41–42** | **2** | ❌ **no** |
| **3.0 Å** (primary) | 37 | 37–37 | **0** | ✅ yes |
| **3.4 Å** | 42 | 42–42 | **0** | ✅ yes |

**This is a real negative and is reported as one, not as robustness.** The identity MONOVALENT-2 measured
holds at 3.0 and 3.4 Å and fails at 2.6 and 2.0 Å.

Where it fails is narrow and legible. All 24 disagreements sit in **four** cells, and in every one of them
the committed model's window is **width 1** — the narrowest possible non-zero window — which the
experimental chain removes:

* `vhl|M3@term_a_exemplar|dab_branch` at 2.0 Å — committed width 1, **all ten** chains give width 0.
* `vhl|M4@term_a_exemplar|dab_branch` at 2.0 Å — committed width 1, **all ten** chains give width 0;
  at 2.6 Å two chains (1OVL_E, 7WNH_C) still give 0.
* `vhl|M3@term_a_exemplar|dap_branch` at 2.0 Å — one chain gives width 0.
* `vhl|M14@term_a_exemplar|aryl_direct` at 2.0 Å — one chain gives width 0, and its closer moves from
  NR4A1 C505 to NR4A2 C505.

So the disagreement is confined to one-atom windows at the tightest clash rule, and it resolves against
the route, not for it.

### 5.3 ⚠ The open-cell count is NOT monotone in the cutoff

Committed open cells by cutoff: **40 → 42 → 37 → 42** for 2.0 → 2.6 → 3.0 → 3.4 Å. The corridor candidate
set is nested, so a larger cutoff can only lengthen or remove a corridor — but **both sides of the race
move**: the NR4A3 C397 target reach lengthens too (e.g. `vhl|M14@term_a_exemplar|aryl_direct`:
`target_atoms` 15 at 2.0/2.6 Å, 17 at 3.0/3.4 Å). The window is a difference of two lengthening
quantities, so it is not monotone. **Seven of 60 cells flip open/closed somewhere along the cutoff axis**
(five in the committed model itself, all at `vhl|M14@term_a_exemplar`; two more only under experimental
geometry). No single cutoff can be quoted as "the" verdict for those seven cells.

### 5.4 ⚠ The C534 attribution is softer under the cutoff axis than under geometry

Committed modelled tally of the closing residue, per cutoff:

| cutoff | NR4A2 C534 | NR4A1 C505 | other | none |
|---|---|---|---|---|
| 2.0 Å | **25** | 20 | NR4A2 C505 = 2 | 13 |
| 2.6 Å | **29** | 13 | NR4A2 C465 = 1 | 17 |
| 3.0 Å | **34** | 8 | — | 18 |
| 3.4 Å | **39** | 3 | — | 18 |

Crossing in the experimental chains as well, C534's closer count over the whole grid spans **15 to 36**
(per-chain minimum 15, at 1OVL_D and 3.4 Å; maximum 36). MONOVALENT-2 reported 20–36 at one cutoff; the
two-dimensional range is **15–36 against a published 34**. **The residue-level attribution is not a
measurement at all**: it is a joint function of the clash rule and the competitor conformer, and neither
dimension is pinned. The sentence "NR4A2 C534 … in 34 of the 60 bivalent corridor cells" should not be
quoted without both ranges. `NR4A1 C551` additionally appears as a closer in one experimental cell at
3.4 Å, a closer class MONOVALENT-2 never saw.

**⛔ NR4A1 caveat, un-error-barred and stated as such.** NR4A1 has **no experimental coordinates in this
checkout and none may be fetched** (no direct HTTP egress; proxy refuses CONNECT 403 / curl exit 56).
Every NR4A1-side reading above — including all 8→20 cells whose closer is NR4A1 C505, and the single
NR4A1 C551 cell — rests on **one modelled conformer** and carries **no error bar of any kind**. Nothing
here narrows that.

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `cutoff-sweep-closure.json` (591 KB): per-cell closure decision at each of the four
  cutoffs under each of the ten experimental chains and under the committed modelled competitor
  (`per_cell[].by_cutoff[cutoff].experimental.by_frame`), the corridor tally per cutoff
  (`tally_per_cutoff`), the exact open/closed set comparison per cutoff
  (`open_closed_set_vs_committed_per_cutoff`), and the cutoffs at which any decision flips (`flips`,
  and `per_cell[].flips`). Producer: `cutoff_sweep_closure.py`.
* **Validation / baseline** — Gate A 300/300 modelled competitor atom counts reproduced **before any
  experimental chain was read**, hard exit 2 armed; Gate B primary-cutoff tally 34/8/18 of 60 exactly,
  hard exit 3 armed; plus 0/360 field mismatches against the committed corridor cells and 300/300
  reproduction at each of the four cutoffs; 0 reach-rule invariant violations; alignment identity 1.000
  and core RMSD 1.52–1.97 Å on all ten chains.
* **Provenance** — reach engine `research/modalities/nr4a3_linker_covalent_reach.py` imported
  **unmodified** (`reach_one_frame`, `paralogue_inclusive_window`, `chemoselectivity_margin`,
  `load_placements`, `spread`, `CLASH_SWEEP_A`, `CLASH_PRIMARY_A`); superposition
  `nr4a3_basin_search.superpose_paralogue` unmodified; numbering
  `nr4a3_covalent_handle_ensemble.pdb_to_uniprot_map` at identity ≥ 0.90; chain parser reused verbatim
  from `../MONOVALENT-2/nr4a2_experimental_competitor_reach.py`; NR4A3 and NR4A1 rows taken **unchanged
  at every cutoff** from `research/modalities/nr4a3-linker-covalent-reach.json`; structures
  `research/modalities/_s4_lane_inputs/{1OVL,7WNH}.pdb.gz` read in place, gzip-streamed, not copied.
  Runtime 57 s, single core, no network, no GPU, no paid API.
* **Limitations** — (1) 1OVL/7WNH are collapsed apo crystals and the modelled paralogue is biased open
  along a pocket CV; a systematic competitor-distance difference is expected and refutes neither.
  (2) Chains within one crystal are not independent; 1OVL contributes 6 and 7WNH 4. (3) Only the NR4A2
  competitor set varies — NR4A1 remains a single modelled conformer with no experimental coordinates
  obtainable here, so every NR4A1-side statement is un-error-barred. (4) The four cutoffs are not
  independent samples of a parameter distribution; they are the committed sweep, and the corridor
  candidate set is nested across them. (5) Geometry only — no thiol pKa, reactivity, adduct, potency,
  selectivity, safety, therapeutic window or clinical readiness is computed, claimed or implied.
* **Stop condition (met)** — stop when all four cutoffs × ten chains are decided, or on a reproduction
  gate firing. Both gates passed and all 2 400 decisions were computed. Stopped there: no further
  cutoffs were invented, no cutoff was adjusted, and NR4A1 was not substituted with a model.

## 7 · Honest outcome

**Not a new paper and no new endpoint claimed.** The answer to the question asked is **split, and must be
quoted split**:

* **The closure is direction-robust.** Real NR4A2 competitor geometry never opens a window the committed
  model closes, at any of the four cutoffs. That is a structural fact and it survives the cutoff axis.
* **MONOVALENT-2's stronger sentence is cutoff-dependent.** "The open/closed set is identical under all
  ten experimental chains" is true at 3.0 and 3.4 Å and **false at 2.6 and 2.0 Å**, where ten chains and
  then two chains close four width-1 cells the model leaves open. This is a **negative** against the
  generality of that sentence and is recorded as one.
* **The residue attribution does not survive at all.** 15–36 over the cutoff × conformer grid, against a
  published 34.

**No shared file is edited and no diff is proposed.** A future owner act could attach the 15–36 range and
the cutoff qualifier to the tally sentence; that is an owner decision, not a worker one.

**Next credible independent work, in order.** (1) Obtain NR4A1 LBD coordinates by an ordinary permitted
access and repeat this exact grid for NR4A1 C505/C551 — it is the residue that wins most of the swaps and
the only competitor still entirely un-error-barred; the script takes it unchanged. (2) Vary the NR4A3
**target** side over the committed 20-conformer 8XTT ensemble at all four cutoffs, closing the last
single-conformer assumption in the cell. (3) MONOVALENT-2's untouched item — the memo's backlog item 5,
the antagonism-window number.

## 8 · Checks

| dir | what | exit |
|---|---|---|
| `checks/01-cutoff-sweep-closure/` | the sweep itself, both gates armed | 0 |
| `checks/02-flip-characterisation/` | **failed attempt, preserved** — `FileNotFoundError`, one `dirname` too many in the artifact path | 1 |
| `checks/03-flip-characterisation-fixed/` | same summary with the path corrected | 0 |
| `checks/04-closing-competitor-detail/` | the four disagreeing cells, cutoff by cutoff | 0 |

No tracked file was written, no guard/floor/gate/matcher/pin/test was changed, no cutoff was adjusted, and
no exit code was fabricated (no pipes; `$?` captured directly).
