---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-MONOVALENT
title: "PUB-MONOVALENT investigation — the paralogue competitor cysteines have an experimental check, and it was never run"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: PUB-MONOVALENT
---

# PUB-MONOVALENT — portfolio investigation, 2026-09-08/09

Worker lane under `SHARED-CONTRACT.md`. **Read-only outside this directory.** No `git add`, no commit, no
push, no `scripts/preflight.sh`, no subagent, no network, no GPU, no paid compute, no worktree, no repo copy.
Model: **SELF-REPORT, NOT INDEPENDENTLY VERIFIED — `claude-opus-5`.**

## 1 · The question

> The covalent axis of the monovalent route is decided by whether **NR4A3 C397 is reached before a paralogue
> cysteine**. Every paralogue competitor reading comes from **one modelled, pocket-opened structure per
> paralogue**, and the owning artifact states that no experimental paralogue LBD input exists here.
> **Is that true — and does the modelled NR4A2 competitor-cysteine geometry that closes the window reproduce
> in experimental NR4A2 LBD coordinates?**

Answerable, and answered below on committed bytes at $0.

## 2 · Paper-level merit

The monovalent memo's headline negative (§3: **0 cells survive, 37 lost, 0 gained** on the conservative
corridor) and the roadmap's covalent-selectivity axis both rest on a **competitor tally**, not on C397 alone.
The memo names the competitors explicitly: **NR4A2 C534 is the first-arriving closer in 34 of the 60 bivalent
corridor cells**, NR4A1 C505 in 8, and NR4A1 C551 appears in 6 of 30 monovalent corridor cells. If those
competitor positions are model artifacts, the closure is a model artifact. **Nothing in this repository has
ever compared a paralogue cysteine to an experimental paralogue structure** — the existing AF-vs-crystal work
(`nr4a_af_crystal_rmsd.py`) is a **Cα fold and Pocket-5** check and touches no cysteine, and the noise bound
the bivalent lane quotes is **model-vs-model** (independently built paralogue models), never model-vs-experiment.
Patient relevance is indirect and stated as such: this grades an in-silico route's evidentiary standing, and
**no efficacy, selectivity, safety or therapeutic-window claim is made or follows from anything here.**

## 3 · The exact evidence gap, and what makes it distinct

`research/modalities/nr4a3-covalent-handle-ensemble.json` →
`comparison_validity.absent_input`, verbatim:

> *"There is no experimental NR4A1 or NR4A2 LBD ensemble in this repo, so the like-for-like ensemble
> comparison the question really wants CANNOT be made from what is here. That is a missing input, not a
> negative result."*

⭑ **Read as written that sentence is about an *ensemble*, and it is correct about ensembles. Read as it is
used — as the reason no experimental paralogue comparison is possible — it is wrong at this HEAD.** Committed
in the tree, offline, $0:

| input | content | resolves |
|---|---|---|
| `research/modalities/_s4_lane_inputs/1OVL.pdb.gz` | Nurr1/NR4A2 LBD X-ray, **6 protein chains**, DBREF UNP P43354 328–598 | Cys **465, 475, 505, 534, 566** in every chain |
| `research/modalities/_s4_lane_inputs/7WNH.pdb.gz` | NR4A2 + NBRE DNA X-ray, **4 protein chains**, UNP P43354 258–598 | the same five, in every chain |

**Ten independent experimental NR4A2 LBD chains**, resolving **exactly the competitor cysteine set** the
covalent lane uses — including **C534**, the dominant closer. **The validation existed and was never used.**

**Distinct from prior work in this lane.** Not the E3-arm-free reach enumeration (§3 of the memo, DONE, and
not re-run here). Not `R1`/`R4`, not the `R2` simulation, not the `R3` cohort. Not the `reactivity_weighted_rerun`
(refuted by its own null and not revived). Not the MV1 hardening round (prose corrections). Not `nr4a_af_crystal_rmsd.py`
(Cα fold, no cysteine, and its artifact `results/nr4a-af-crystal-rmsd/` is a different measurement). Not the
`apo-pose-recovery` / `apo-pose-site-in-regime` use of 1OVL/7WNH, which is **cross-docking pose recovery**, not
cysteine geometry. No denied source (B1/B2/B4) touched; no network act of any kind.

## 4 · The bounded step taken

`nr4a2_crystal_vs_model_cysteines.py` — heavy-atom-only Shrake–Rupley thiol exposure for the five NR4A2 LBD
cysteines, computed by **one code path** on both sides: the modelled `results/nr4a3-matrix/nr4a2-opened.pdb`
and each of the ten experimental chains, each chain measured in isolation and truncated to the model's own
UniProt span 344–598 so the occluder sets are comparable. Numbering is never assumed — every chain is mapped
to P43354 by the repo's own global alignment (identity **1.000** on all eleven structures).

### Result — the dominant closer is corroborated; the ordering below it is not

| NR4A2 Cys | model `sg_rel` (heavy) | experimental `sg_rel`, 10 chains (min / median / max) | model inside experimental range? |
|---|---|---|---|
| **534** — the closer in 34/60 bivalent corridor cells | **0.1394** | **0.0666 / 0.1167 / 0.1625** | ✅ **yes** |
| 465 | 0.0768 | 0.0067 / 0.0105 / 0.0940 | ✅ yes (at the top edge) |
| 475 | 0.0000 | 0.0072 / 0.0158 / 0.0407 | ⛔ **no** — model buries a thiol the crystals do not |
| 505 | 0.0018 | 0.0000 / 0.0017 / 0.0036 | ✅ yes |
| 566 | 0.0000 | 0.0000 / 0.0000 / 0.0035 | ✅ yes |

- ✅ **C534 is the most-exposed NR4A2 LBD thiol in the model and in all ten experimental chains alike**, and
  the modelled value sits inside the experimental spread. **The one competitor reading the corridor result
  actually leans on is not a model artifact.** This is a positive check on the memo's negative, and it makes
  that negative harder to dismiss rather than easier.
- ⚠ **The full rank order does NOT reproduce**: model `534 > 465 > 505 > 475 > 566`, experimental median
  `534 > 475 > 465 > 505 > 566`. The disagreement is entirely among the four near-buried thiols, whose whole
  spread (0.000–0.094) is **smaller than C534's single-structure experimental spread** — so it is a
  distinction inside noise, not a second finding. Reported, not promoted.
- ⭑ **The number this produces that did not exist before: C534's exposure varies 0.067→0.163 across ten
  experimental chains — a 2.4× range around a single modelled value that the committed artifact reports with
  no error bar at all.** Any future statement of the form "competitor X closes the window" inherits that
  spread.
- ⛔ **NR4A1 is not checkable here.** No experimental NR4A1 LBD coordinates are committed (`3V3E` is named in
  `nr4a_af_crystal_rmsd.py` but is fetched at CI time, not retained). So **NR4A1 C505 and the
  literature-anchored C551 remain model-only**, and C551's appearance in the monovalent corridor tally is
  still a tie-break with no distance and now also with no experimental check. That asymmetry is the honest
  state and is not repaired by anything in this lane.

### Baseline / validation

`replicate_check.py` — the lane's recomputation of the modelled structure is asserted against the committed
artifact's own heavy-atom columns before any crystal is read: **21 of 21 quantities MATCH** across all five
cysteines (`residue_sasa_heavy_A2`, `rsa_heavy`, `sg_sasa_heavy_A2`, `sg_sasa_isolated_A2`, `pdb_resnum`),
exit code 0. **Had it not matched, nothing above would be interpretable and the lane would have stopped.**

### Provenance

SASA from `research/modalities/nr4a_differential_atlas.py` via
`nr4a3_covalent_handle_ensemble.atom_sasa` (**unmodified, imported**); sequences from the committed
`research/modalities/nr4a-sequences-cache.json`; structures from `research/modalities/_s4_lane_inputs/`
and `results/nr4a3-matrix/`. Every execution attempt is in `checks/` with `command.txt`, `stdout.txt`,
`stderr.txt`, `exit_code.txt`.

### Limitations

1. ⛔ **This is not a pocket-state validation.** 1OVL and 7WNH are **collapsed apo** crystals; the model is
   biased open along a pocket CV. A burial difference at pocket-lining positions is **expected**, and none of
   the agreement above says the modelled open state is real.
2. ⛔ **NR4A2 only, one measurement only.** Nothing here validates NR4A1, the NR4A3 pose (`V3` INCONCLUSIVE,
   `V22` disagreeing at median 6.696 Å), the reach corridor, or any window count.
3. ⚠ Chains within one crystal are not independent; crystallographic packing, DNA and the DBD are absent from
   the isolated-chain measurement.
4. ⛔ **Exposure is not reactivity** — no thiol pKa, rate, adduct or chemoproteomic selectivity is computed.
5. ⛔ **No efficacy, potency, selectivity, safety, therapeutic-window or clinical claim** is made or implied.

### Stop condition (met)

Stop when the modelled-vs-experimental comparison is made for the one paralogue whose experimental
coordinates are committed, or when the replication baseline fails. The baseline passed and the comparison is
made. **NR4A1 is out of reach without a network fetch, which is outside worker authority — the lane stops
there rather than substituting a model for the missing structure.**

## 5 · Shared-file change, prepared and NOT applied

`PROPOSED-UNAPPLIED-absent-input-qualifier.diff` narrows `absent_input` in
`research/modalities/nr4a3_covalent_handle_ensemble.py` so it says what is true: no experimental paralogue
**ensemble**, but ten experimental NR4A2 LBD **chains** are committed and permit the single-structure check,
and NR4A1 has no experimental coordinates here at all. **It weakens no guard, gate, floor, matcher, pin or
test and changes no computed number.** It is an owner act and is left unapplied.

## 6 · Honest outcome

**Not a new paper.** `PUB-MONOVALENT` is `drafted` and this question lives inside it; a new label would not
make it a separate endpoint, and I decline to claim one. What this lane returns is a **first
model-vs-experiment check of the paralogue competitor cysteines**, a **corroboration of the single competitor
reading the corridor result depends on**, the **experimental spread that reading has never carried**, and a
**concrete provenance narrowing** — plus the preserved negative that **NR4A1's competitors, including the one
literature-anchored covalent site, remain unvalidated and unvalidatable from committed bytes.**

**Next credible independent work, in order:** (1) retrieve NR4A1 LBD coordinates (`3V3E`) by an ordinary
permitted access and repeat this measurement for C505 and C551 — the same script takes it unchanged;
(2) propagate C534's experimental spread into the corridor tally as a sensitivity, so "closed by C534" carries
a bound; (3) the memo's own backlog item 5 — obtain or explicitly record the absence of an antagonism-window
number — which this lane did not touch.
