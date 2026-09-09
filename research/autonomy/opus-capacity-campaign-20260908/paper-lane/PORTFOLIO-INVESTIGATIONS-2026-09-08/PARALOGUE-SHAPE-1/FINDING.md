---
id: DOC-PORTFOLIO-INVESTIGATION-PARALOGUE-SHAPE-1
title: "PARALOGUE-SHAPE-1 — NR4A3's pocket does NOT visit conformational states the paralogues never visit; the distance matrix separates the three species perfectly, but for a static reason"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: PARALOGUE-SHAPE-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
proposal: DISCOVERY-2 proposal 5
---

# PARALOGUE-SHAPE-1 — per-frame pocket geometry, species against replica

Worker lane under `SHARED-CONTRACT.md`. Read-only outside this directory; the three conformer trees
(~98 MB) were read **in place** and never copied. No `git add`, commit, push, `preflight.sh`,
subagent, network, GPU, paid compute, worktree or repo copy. No install.
Model: **SELF-REPORT, NOT INDEPENDENTLY VERIFIED — `claude-opus-5`.**

⛔ **GEOMETRY ONLY.** Nothing below is, or supports, a selectivity, druggability, efficacy, safety,
therapeutic-window or clinical-readiness statement. Distances between backbone atoms are not any of
those things.

## 1 · The question

> **Does NR4A3's pocket visit conformational states the paralogues never do?**

Answered on the committed unbiased release conformers, at $0, with the unit of analysis being
**per-frame pocket geometry**: the 45 pairwise CA–CA distances among the 10 homologous Pocket-5
lining residues, plus the radius of gyration of those same 10 CA atoms.

## 2 · Paper-level merit

Every paralogue-contrast axis in this program so far has been read off a *chemical* per-residue
property (cysteine exposure) or a *detector score* (fpocket druggability). Both inherit the
detector's or the SASA routine's conventions. A pocket's **shape** is the thing those proxies are
standing in for, it is measurable directly from the same committed frames with no detector and no
free parameter, and — this is the part that carries the merit — **it is the axis on which a
"NR4A3 is different" claim is most likely to be trivially true and therefore most in need of a
control.** Establishing which half of an apparent species separation is constitutive sequence
difference and which half is dynamics decides how much weight *any* paralogue-contrast sentence in
this program can bear. Patient relevance is **indirect and stated as such**: this grades the
evidentiary standing of an in-silico contrast, and it is a negative result on the dynamic axis.

## 3 · The exact evidence gap, and the boundary against the two completed lanes

I read both named lanes first.

* **DEGRADER-2** scored, per frame, the **solvent accessibility of individual cysteines** (RSA from
  a Shrake–Rupley routine) and counted frame-level overlap between NR4A3's unique cysteines and the
  paralogue cysteines. Its unit is **one residue's chemical exposure**.
* **MONOVALENT-3** swept the **clash cutoff** (2.0 / 2.6 / 3.0 / 3.4 Å) over **corridor cells** in
  the linker-reach engine. Its unit is **a corridor occupancy under a steric parameter**.
* **IC-4 (`paralogue-pocket-contrast.json`)**, already committed, scores each frame with **fpocket
  druggability** against `d* = 0.53`. Its unit is **a detector's score**.

**The boundary I drew:** my unit is the **pocket's own internal geometry** — a 45-dimensional
distance matrix and a scalar Rg — computed from **CA atoms only**, with **no SASA, no probe radius,
no clash cutoff, no fpocket, no score and no threshold**. It is superposition-free (internal
distances are invariant), so no alignment convention enters either. Nothing in DEGRADER-2 or
MONOVALENT-3 is recomputed, reused or contradicted. The one thing shared with them is the *input
set* — the same committed `release_rep{0,1,2}` unbiased frames, the biased `metad` subsets excluded
exactly as the source excludes them.

The gap this fills: the species contrast had never been decomposed **species against replica**.
Every prior contrast pooled replicas or split them descriptively; none asked whether the
replica-to-replica spread within one species already accounts for the between-species spread.

## 4 · The bounded step taken

`paralogue_pocket_shape.py` (numpy only; stdlib PDB reader) walks
`results/nr4a1-pocket-ensemble`, `results/nr4a2-pocket-ensemble`,
`results/nr4a3-pocket-reharmonize` → `release_rep{0,1,2}/fp_*/frame.pdb`
= **25 frames × 3 replicas × 3 species = 225 frames**, and writes
`paralogue-pocket-shape.json` (+ a compact `per-frame-pocket-shape.json` table).

**Homology mapping, and the abort that guards it.** The lining set is NR4A3 Pocket-5
`[406, 407, 410, 411, 412, 481, 484, 485, 531, 534]` — `nr4a3_metad.py:50 REF_CV_RESIDUES`, the
same set `af2_static/pocket5_lining_residues.json` records with Jaccard 1.0. The paralogue
counterparts `[372, 373, 376, 377, 380, 450, 453, 454, 500, 503]` are the **alignment-derived**
ids each ensemble publishes in its own `release_summary.json → cv_residues`; local→UniProt offsets
are the committed values in `nr4a-paralogue-dynamics.json → construct` (NR4A3 372, NR4A1 347,
NR4A2 343). The script **re-reads the CA residue name at every mapped local id in every one of the
225 frames** and `SystemExit`s on any mismatch — a silently wrong offset cannot pass. All 225
matched (`HIS LEU GLY PRO ALA ARG TYR ARG VAL PHE` / `HIS VAL ASN PRO THR ARG TYR ARG ILE PHE` /
`LEU THR THR PRO ARG ARG ILE ARG ILE LEU`, the last independently confirmed against
`af2_static/fpocket_run/AF-Q92570.pdb`).

Each distance is standardised by the **pooled within-replica sd** (216 df) — a scale that is blind
to both species and replica means, so the standardisation cannot manufacture separation.

## 5 · Result — the answer is **NO**, and the headline separation is an artefact of the wrong question

### 5a · The absolute distance matrix separates the three species perfectly

`T` = (mean between-species replica-centroid distance) / (mean within-species replica-centroid
distance) = **3.6163** (24.0623 / 6.6539 sd units). Median per-distance `eta2_species` = **0.5645**
against median `eta2_replica(species)` = **0.0676**; species beats replica on **35 of 45**
distances. Three distances are almost purely species-determined (`406–412` 0.962, `407–412` 0.962,
`411–412` 0.953).

**Both required checks fire correctly.**

| check | result |
|---|---|
| **exact replica-block species-label permutation** (all 1680 assignments of the 9 replica blocks to 3 labelled groups; 280 distinct partitions) | observed `T` ranks **1 / 1680**; **p = 0.00357 = the exact floor `6/1680`** — i.e. permutation abolishes the separation entirely |
| frame-level label permutation (2000 draws) | p = 0.00050 — reported **only** for contrast and flagged in the artifact as **anti-conservative**, since frames within a replica are correlated |
| **within-species replica baseline** | between/within = **3.62**; the species contrast beats it |

So on absolute shape, species separation is real and permutation-abolished.

### 5b · But that separation is **static**, not "states visited"

Three different proteins with three different sequences have three different backbone geometries.
A separation in **absolute** lining-residue distances is a fact about the AF2 starting models, and
it answers "are the pockets shaped differently?", **not** "does NR4A3 *visit* states the paralogues
never visit?". The distance that carries the separation, `406–412`, spans the very insertion where
the three sequences differ (NR4A3 `L…R` vs NR4A1 `H…A` vs NR4A2 `H…T`). The nearest-neighbour test
run on absolute coordinates duly reports **100 % of NR4A3 frames beyond the paralogue
cross-replica p95** — a number that means only "NR4A3 is a different protein", and I record it as
such rather than as a result.

### 5c · On every axis that is actually comparable across species, they do **not** separate

| test | result | reading |
|---|---|---|
| **pocket Rg envelope** | NR4A3 spans **7.154 – 7.811 Å**; the paralogues span **6.785 – 8.491 Å**. **0 of 75** NR4A3 frames fall outside the paralogue range | NR4A3's pocket size is strictly **inside** the paralogue envelope — it visits no size the paralogues do not |
| **Rg variance decomposition** | `eta2_species` = **0.305** vs `eta2_replica(species)` = **0.299** | the within-species replica spread is **comparable** to the between-species spread. Per the pre-stated rule, **on this axis the species do not separate.** NR4A1's own three replicas mean 7.82 / 7.43 / 7.07 Å — a wider spread than the three species means 7.44 / 7.83 / 7.42 Å |
| **fluctuation-space nearest neighbour** (species mean shape removed) | NR4A3→paralogue median NN **5.66** vs the paralogue cross-replica NN median **5.686** (essentially identical) and p95 **11.46**; **0.0000** of NR4A3 frames beyond p95 | once the constitutive offset is removed, NR4A3's fluctuations sit **well inside** the paralogues' own replica-to-replica variation |
| **breathing amplitude** (mean frame distance to own replica centroid, sd units) | NR4A1 **7.670**, NR4A2 **5.359**, NR4A3 **5.612**; contrast `T` = 1.418, exact block **p = 0.03929** | NR4A3 is **intermediate, not extreme**. Such species effect as exists is driven by **NR4A1 exploring more**, not by NR4A3. This is not a NR4A3-uniqueness result under any reading |
| species-mean-removed `T` | 0.0000, p = 1.0 | **degenerate by construction** and labelled as such in the artifact; reported only to show the centring was applied, never as evidence |

**Answer to DISCOVERY-2 proposal 5: no.** In these ensembles NR4A3's pocket occupies a
constitutively different but **not** dynamically distinctive region of shape space. It visits no
pocket size outside the paralogue envelope, its shape fluctuations lie inside the paralogues' own
replica-to-replica variation, and it is not the paralogue with the largest conformational
excursion. **10 of 45** distances have more replica-within-species variance than species variance,
which is the direct measure of how much of this dataset's variation the replicas already own.

## 6 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `paralogue-pocket-shape.json` (17 KB) — the full 45-distance variance decomposition,
the separation statistic, both permutation tests, the replica baseline, the occupancy tests, the
centred-fluctuation control and the convergence block. `per-frame-pocket-shape.json` (32 KB) — per
frame Rg and the six highest-`eta2` distances, 225 rows, reusable. `paralogue_pocket_shape.py` —
the generator. Lane total **116 KB**, far under the 5 MiB budget; no scratch retained.

**Validation / baseline.** The two mandated falsifiers both ran and both can fail: the exact
replica-block permutation (§5a, reaches its floor for the absolute matrix and **fails to reach
significance for the dynamic contrasts in the direction that would support NR4A3 uniqueness**), and
the within-species replica-vs-replica baseline (§5c, which the Rg axis **does not** beat). The
homology mapping is guarded by a hard abort on residue-identity mismatch across all 225 frames.

**Provenance.** Inputs as named in §4, all committed, all read in place. Lining set and offsets are
taken from committed sources, never hand-transcribed. Repo HEAD at execution is recorded by the
parent; input trees unmodified.

**Limitations.**
1. **Resolution floor.** Following ASSESS-DEGRADER-2's finding that a per-frame geometric statistic
   moves under refinement and that a maximum-based ceiling grows with sampling, I state mine:
   with 25 frames per replica the **replica-centroid standard error is 0.20 pooled-within-replica
   sd per coordinate**. Any centroid difference below ~0.2 sd is **not resolved here**. I therefore
   use no maximum-based statistic as a headline — the Rg envelope in §5c is deliberately reported
   as a **containment** (0/75 outside), which sampling can only *break*, never manufacture.
2. **Convergence.** Halving the sampling deterministically (13 frames/replica) moves `T` 3.6163 →
   **3.6995** and leaves the exact permutation p at the same floor 0.00357. The headline is stable
   to a 2× sampling change; a 10× change is untested.
3. **5 ns per replica, 3 replicas.** Absence of a unique NR4A3 state at this sampling is **not**
   proof no such state exists. This is a negative on the available ensembles, nothing more.
4. **CA-only.** Side-chain rearrangement inside a fixed backbone is invisible to this measure.
   CA distances were chosen precisely so the three sequences are comparable; the cost is that a
   side-chain-only difference would not be seen.
5. The 10-residue lining set is inherited from the committed Pocket-5 definition; a different
   lining definition was not tested.
6. The biased `metad` frames are excluded (as the source excludes them), so nothing here speaks to
   the biased free-energy surface.

**Stop condition — met.** The question had a yes/no form and both mandated falsifiers were run;
the answer is no on the dynamic axis and trivially yes on the static one. **Stop.** I did not
proceed to a lining-set sensitivity sweep, an all-heavy-atom variant, or a metad-inclusive read —
each is a distinct question and none of them changes this answer.

**Next credible independent work (not run here):** the informative residual is §5c's breathing
amplitude — **NR4A1 explores ~1.4× more pocket shape space than either NR4A2 or NR4A3** (p =
0.0393, exact block permutation, and therefore weak at 9 blocks). If that survives more replicas it
is a statement about NR4A1, not NR4A3, and it would need its own lane.

## 7 · Executions

`checks/01-pocket-shape/` (exit 0) — first full run, absolute matrix only.
`checks/02-centred-control/` (exit 0) — adds the species-centred fluctuation control that produced §5b–c.
`checks/03-final/` (exit 0) — final run labelling the degenerate centred `T`.
No attempt failed; none is omitted.
