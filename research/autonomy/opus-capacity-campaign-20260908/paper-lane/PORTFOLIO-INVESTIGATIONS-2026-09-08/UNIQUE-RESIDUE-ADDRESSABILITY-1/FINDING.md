---
id: DOC-PORTFOLIO-INVESTIGATION-UNIQUE-RESIDUE-ADDRESSABILITY-1-20260909
title: "UNIQUE-RESIDUE-ADDRESSABILITY-1 — NR4A3's unique indel residues are a compact, terminus-proximal, pocket-remote patch: a decisive negative"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: UNIQUE-RESIDUE-ADDRESSABILITY-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
source: DISCOVERY-2 proposal 10
---

# UNIQUE-RESIDUE-ADDRESSABILITY-1

## 1 · The question

`nr4a-reciprocal-uniqueness-census.json` records 47 non-terminal indel runs in which NR4A3 carries a
segment a paralogue lacks, and states plainly that it "says nothing about whether that segment is
ordered, exposed, near the pocket, or usable by anything." **Are those unique indel residues
addressable geometry — exposed and clustered near the cryptic pocket — or are they buried and
scattered?** Answered on the committed NR4A3 conformer ensemble, with a uniqueness-label permutation
that must abolish anything found.

## 2 · Paper-level merit

The NR4A3 selectivity argument rests on residues NR4A1/NR4A2 do not have. Substitution-level
uniqueness has been worked hard (the committed handle map, PUB-DEGRADER, DEGRADER-2); **indel-level
uniqueness has never been given geometry at all**, and it is the stronger sequence claim — an absent
segment cannot be compensated by a conservative substitution. If those insertions were exposed and
pocket-adjacent they would be the most paralogue-discriminating surface in the fold. Establishing
that they are *not* closes a live prospect cheaply and stops it being re-proposed. It costs $0,
needs no new sampling, and it can only sharpen or correctly retire a claim.

## 3 · The exact evidence gap, and the boundary against neighbouring work

* **DEGRADER-2 / PUB-DEGRADER scored CYSTEINES** — three NR4A3-unique thiols, RSA only, no distance
  axis, no label null. **The boundary drawn here:** this lane scores **indel residues of every
  residue class**, adds the **pocket-distance** axis, and adds the **permutation null** none of the
  cysteine work ran. No cysteine statistic is recomputed, contradicted or reused.
* **PARALOGUE-SHAPE-1** is concurrently decomposing per-frame pocket *variance* on the same
  ensembles. **No variance decomposition appears here**; frames enter only as replicates of a
  per-residue mean, and the two artifacts do not overlap.
* **The census itself** annotates geometry on **one static opened conformer** and only for residues
  with a defined reactive atom. This lane uses **75 committed conformers** and **every** residue of
  the construct, so a null pool exists at all.
* Not re-opened: R1–R4, B1/B2/B4, MF1, P-ST, TCIP, FP, any free-energy construct, the deferred
  degrader-optimisation row of `portfolio-2026-09-05`. No network, no GPU, no docking, no structure
  prediction, no new sampling.

## 4 · The step taken

`unique_residue_addressability.py` (stdlib + `multiprocessing`, $0, read-only outside this
directory) re-imports the committed routines unchanged — `nr4a_differential_atlas.parse_pdb /
shrake_rupley / residue_rsa`, `nr4a3_basin_search.load_paralogue`,
`nr4a_paralogue_dynamics.construct_frame`, `nr4a_paralogue_unique_residues.CRYPTIC_POCKET_UNIPROT` —
over `results/nr4a3-pocket-reharmonize/release_rep{0,1,2}/*/frame.pdb` (**75 unbiased frames**; the
biased `metad` subset excluded as the source excludes it). For each of the **254** modelled residues
(UniProt 373–626, offset re-derived per frame from the model's own sequence: +372, homologous pocket
10/10) it records per-frame **RSA** and the **distance from the side-chain heavy-atom centroid to the
nearest cryptic-pocket heavy atom**. Every input is re-hashed at use (DISCOVERY-2 computed none).

### 4a · The first result is a census fact, before any statistic

Of the 47 non-terminal NR4A3-present indel runs, **almost all lie outside the modelled LBD**. Inside
UniProt 373–626 there are exactly **11 indel residues**: 380, 381, 382, 383, 385, 386, 387, 388, 390,
394 — one contiguous stretch — and 570. **Not one of them belongs to an alignment-robust run**; the
three robust NR4A3-present runs (48–49, 272–273, 276) are all outside the construct. So the entire
geometric read rests on the census's own *non-robust*, "ambiguous, not a finding" half, and the
robust indel set has **zero** structural coverage in any committed model. That is a limit on the
question, not a result about the protein.

### 4b · The geometry, and the check that had to be able to fail

| label set | n | mean RSA (null median) | p | mean d(pocket) Å (null median) | p | mean pairwise dist Å (null median) | p |
|---|---|---|---|---|---|---|---|
| indel residues (all) | 11 | 0.51 (0.30) | 0.0042 ↑ | **30.3 (15.6)** | 1.00 ↓ | **15.7 (28.9)** | 0.0005 ↓ |
| three-way indels | 4 | 0.39 (0.30) | 0.24 | 32.7 (15.2) | 1.00 ↓ | 7.1 (27.4) | 0.0005 ↓ |
| alignment-robust indels | **0** | — | — | — | — | — | — |
| unique-robust substitutions | 63 | 0.34 (0.30) | 0.13 | **13.4 (15.8)** | **0.0099** ↓ | 26.2 (29.1) | 0.06 |

(20 000 label permutations; pocket-lining residues excluded from both the labelled set and the null
pool; ↓ = one-sided toward *closer* / *more compact*.)

1. **The indel residues are spatially clustered — and that is the whole of the positive result.**
   They form one compact patch (mean pairwise 15.7 Å vs null 28.9 Å; the four three-way residues sit
   inside 7.1 Å of each other). This is unsurprising and near-tautological: they are a contiguous
   sequence run, and the circular-shift null shows any contiguous 11-residue run is compact.
2. **They are the opposite of pocket-proximal.** ~30 Å from the cryptic pocket, *farther* than random
   residues in every null tried (permutation p_closer = 1.00; chain-shift 0.94; terminus-matched
   0.96–0.97). Only residue **570** approaches the pocket (12.2 Å mean, 8.9 Å minimum) — and it is
   **buried** (mean RSA 0.17; RSA ≥ 0.25 in 7 % of frames). Exposure and proximity are **anti-
   correlated** across this set: no indel residue is both.
3. **The exposure signal is abolished by the controls, exactly as the check demanded.** The naive
   permutation calls them exposed (0.51 vs 0.30, p = 0.004), but a **run-structure-preserving
   circular-shift** null gives p = 0.11 and a **terminus-distance-matched** null gives p = 0.23
   (±5) / 0.32 (±10). The 11 residues sit 7–21 residues from the construct N-terminus; residues that
   close to a chain end are exposed whatever they are. **The exposure is a chain-end artefact of the
   construct, not a property of the indels**, and it is reported as a negative rather than rescued by
   sub-setting.
4. **A genuine contrast, in the other label set.** Unique-robust *substitution* positions are
   modestly but reproducibly **pocket-proximal** (13.4 Å vs 15.8 Å, permutation p = 0.0099; chain-
   shift p = 0.06) while being **no more exposed than random** (p = 0.13). The paralogue-
   discriminating geometry near this pocket is substitutional, not insertional — which is the axis
   the committed work already runs on.

**Answer: buried-or-remote and merely contiguous, not addressable.** The indel residues are neither
pocket-proximal nor independently exposed; the one that is close to the pocket is buried; and the
alignment-robust indels have no geometry in any committed structure at all.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `unique-residue-addressability.json` (~150 KB): per-residue RSA (mean/p10/median/
  p90/max, fraction of frames ≥ 0.25) and pocket distance (mean/median/p10/min) for all 254 modelled
  residues, with indel / substitution / pocket labels; five label tests each with a 20 000-draw
  permutation, a circular-shift randomisation and a spatial-clustering statistic; the terminus-
  matched control; the resolution floor; SHA-256 of the census, the sequence cache and all 75 frames.
* **Validation / baseline** — the required falsification check **ran and bit**: the label permutation
  removes the clustering claim's exposure half, and two independent nulls (contiguity-preserving,
  terminus-matched) agree. Construct offset and homologous pocket are re-derived per frame from the
  model's own sequence (+372, 10/10 pocket residues present, no approximation). All committed
  routines imported unchanged, none weakened.
* **Provenance** — census `nr4a-reciprocal-uniqueness-census.json`
  `sha256 2033ab9b996afd18eb9b95e8b288907c1aad23cdfb8daa0173b1bcc4d6bfda5b`, 512 443 B; sequence cache;
  75 `frame.pdb` conformers, each hashed. `$0`, offline, CPU, 4 workers, ~100 s.
* **Limitations** — (a) **geometry only**: exposure and proximity are **not** druggability,
  ligandability, selectivity, efficacy, safety or a therapeutic window, and nothing here supports
  such a claim; (b) one protein's LBD construct, so indels outside UniProt 373–626 — including
  **every alignment-robust one** — are simply unmeasured, and their consequence remains unknown, not
  zero; (c) the measured indels are non-robust census calls, i.e. alignment-ambiguous positions;
  (d) the pocket is one committed cryptic-pocket definition, not a search over cavities; (e) n = 11
  labelled residues, so the negative is a bound on effect size, not proof of no effect; (f) MD
  frames from one committed ensemble — sampling, force field and construct-boundary limits are
  inherited unexamined; (g) **resolution floor**: group-mean RSA is converged to ±0.001 at
  n_points = 96 (checked at 256 and 512), and per-residue *maxima* grow with sampling, so no
  conclusion here uses a maximum or an exact frame count.
* **Stop condition** — met. The question is answered in the negative on the available geometry, with
  the falsification check passed. **Do not re-run this on subsets to find a clustering fraction.**
  The only credible next work is a different dependency, not a re-analysis: the alignment-robust
  indel runs (48–49, 272–273, 276) lie outside every committed NR4A3 model, so they need a structure
  covering UniProt 400–650's N-terminal flank before the question can even be asked of them — and no
  such structure exists in this repository.

## 6 · Checks

`checks/01-smoke-one-frame`, `checks/02-full-run-npoints96` (the artifact),
`checks/03-terminus-matched-null`, `checks/04-quadrature-convergence` — each with `command.txt`,
`stdout.txt`, `stderr.txt`, `exit_code.txt`. All four exited 0; no attempt was discarded.
