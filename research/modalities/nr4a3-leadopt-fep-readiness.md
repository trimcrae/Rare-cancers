# FEP-readiness dossier — lo_m0_NCCO (the better-than-401 lead), 2026-07-06

**Purpose.** Everything needed to fire the selectivity FEP on the scaffold-lead-opt winner the *moment* the
FEP GPUs are available — the candidate is de-risked through every cheap pre-FEP gate the program uses. Nothing
here needs GPU; the one gated action is the FEP itself.

## The candidate
**lo_m0_NCCO = denovo_401 + ortho-acetamido on the pendant phenyl.** Clean (no structural alerts), developable
(QED 0.71, SA 4.0, MW 361), **neutral at pH 7.4** (amide — no ionizable liability, unlike the withdrawn denovo_111).
- **Primary FEP species — `lo_m0_NCCO_gen`** (strongest binder): `COC[C@H](c1ccccc1NC(C)=O)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`
- **Co-species — `lo_m0_NCCO_iso01`** (most robustly selective): `COC[C@@H](c1ccccc1NC(C)=O)[C@@H]1CC[C@@H](CC(C)(C)[C@H](C)O)C1`
- Co-lead sibling (congeneric): **lo_m0_CC** (ortho-ethyl) — the RBFE partner.

## Why it's the lead (vs denovo_401), on the same cheap tiers
| tier | 401 (baseline) | lo_m0_NCCO | reads |
|------|----------------|------------|-------|
| multi-snapshot MM-GBSA ΔG3 (affinity), 2 independent seeds | −35.4 / −34.4 | **−41.0 / −40.1** | **~+5.5 kcal/mol tighter, reproducible** |
| selectivity margin ± SD | +13.2 / +10.9 | +16.9 / +11.0 (gen); +10.4 (iso01) | ≥ 401, run-dependent (preserved, not degraded) |
| decoy-null clearance (release, 95th +6.7) | clears | **clears decisively** | specificity-controlled |

**⚠ FRAMING UPDATE (2026-07-06, converged+calibrated 401 FEP merged from main):** the earlier "401 is a poor
binder" was an **engine-calibration artifact**. The converged r1 ABFE (n_iter=2000) + the T4-lysozyme·benzene
engine zero (a measured **+7.1 kcal/mol under-binding offset**, `nr4a3-abfe-calibration.json`) show 401 is
actually a **favourable, selective NR4A3 binder (~−4.5 kcal/mol offset-corrected; ΔΔG −6.9 vs NR4A1 / −5.5 vs
NR4A2)**, with both paralogues non-binding. So lo_m0_NCCO is not "a real binder to replace a non-binder" — it is
a genuine **lead-optimization**: an even *tighter* NR4A3 binder that stays selective (MM-GBSA ~+5 kcal/mol
tighter than 401). That is exactly what RBFE(401→lo_m0_NCCO) will quantify, offset-free.
The ortho-acetamido/ethyl decoration engages the divergent hydrophobic/H-bond handles (L406/T410/I484/L534).

## Pre-FEP de-risking — DONE (all cheap-tier this session)
1. **Species / stereochemistry** — 16 stereoisomers docked + top-6 multi-snapshot MM-GBSA
   (`nr4a3-leadopt-species` / `-species-mmgbsa-ms`). The dock-favoured iso03 **reversed** under de-noising
   (proves the tier discriminates); **gen** (−39.4, +9.2) and **iso01** (−36.5, +10.4 ± 3.25) are the robust
   selective species → the FEP subjects.
2. **Protonation** — acetamido is non-basic → **neutral is the sole physiological species** (asserted in
   `fep_species.py`). No protonation-reversal risk (the denovo_111 failure mode is absent).
3. **Winner's-curse** — independent-seed multi-snapshot replicate (`nr4a3-leadopt-mmgbsa-ms-rep2`): affinity
   gain reproduces (−40 vs −34); margin tempered from single-run inflation to "preserved". lo_m0_SNOO dropped
   (not reproducible) — the lead set is gen/iso01 (+ ethyl sibling).
4. **Receptor frame** — the FEP receptor is the **metastability-validated 0.74 release frame** (the
   best-held-druggable conformation, per the TARGET_RG ladder; 48% of unbiased frames druggable). Metadynamics
   (pocket opening) is already done for all 3 receptors and reused — it is a receptor property, not per-ligand.
5. **Metad-frame robustness** — species re-docked into the NR4A3 **metad-opened** conformer
   (`nr4a3-leadopt-species-metad`): selectivity is **release-frame-specific**, weaker in the promiscuous metad
   frame — the *same documented pattern as 401*, so no new liability.
6. **Induced fit / pose stability** — the multi-snapshot MM-GBSA runs short *ligand-bound* GB-MD and the pose
   held (consistent ΔG, SD ~4). The FEP complex-leg equilibration does the full explicit-solvent induced-fit
   relaxation (as decided for 401). *(Optional not-yet-run: a dedicated standalone explicit-solvent holo-MD +
   fpocket-over-trajectory to quantify hold-open; low marginal value over the above + FEP.)*
7. **Orthogonal pose** — Boltz-2 binary co-fold across NR4A3/1/2 (`gpu-ternary-aws mode=binary`, run 28800726169,
   DONE) — an AF3-class cross-check, read at true weight: this cryptic pocket is Boltz's low-confidence regime
   (as for 401, where pair-iptm was 0.23–0.32 and did not corroborate), so it is a consistency footnote, not
   decisive. **Bonus:** the reporter reconfirmed the **ternary-interface divergence** (NR4A3–CRBN interface = 33
   res; 8 divergent vs each paralogue; **pocket handles NOT at the interface**) → lo_m0_NCCO's *binder*
   selectivity × *ternary* selectivity is a genuine **multiplicative** budget for the degrader (linker toward
   the divergent E545/T563/Q570/S571/L576/E580/V588 patch).
8. **Induced-fit / hold-open holo-MD** — NOT run as a standalone (same call as 401): the multi-snapshot MM-GBSA
   already runs ligand-bound GB-MD (pose held), the metastability screen characterized the apo hold-open (0.74
   = best-held, druggable 48% of frames), and the FEP complex-leg does the full explicit-solvent induced-fit
   equilibration. A dedicated explicit-solvent holo-MD + fpocket-over-trajectory (to *quantify* whether
   lo_m0_NCCO stabilises the open pocket) is the one optional extra — low marginal value over the above.

## FEP-ready artifacts (already in S3)
- Receptors + docked ligand pose: `s3://<bucket>/nr4a3-leadopt-species/` → `nr4a3-opened.pdb` (release frame),
  `nr4a1-opened.pdb`, `nr4a2-opened.pdb`, `docked_{nr4a3,nr4a1,nr4a2}.sdf` (ligand record `lo_m0_NCCO_gen`).

## The exact FEP dispatch (fire when FEP GPUs + go-ahead are available)
Gated: (a) trimcrae go-ahead (standing FEP carve-out), (b) the ml.g5 **spot-training** quota/IAM for FEP, (c)
`mode=smoke` first (validates spot+checkpoint+env), then `mode=run`.
```
gpu-fep-aws.yml  mode=run  ligand=lo_m0_NCCO_gen  receptor_prefix=nr4a3-leadopt-species
                 tag=nr4a3-fep-leadopt-nccogen  n_windows=12  n_shards=<= spot quota  spot=1
                 max_wait_hours=20  max_run_hours=12  target_ddg=-1.0
# reduce (CPU) when legs finish:  gpu-fep-aws.yml mode=reduce tag=nr4a3-fep-leadopt-nccogen
```
Repeat with `ligand=lo_m0_NCCO_iso01` (co-species) if resolving the stereo/selectivity tradeoff at FEP grade.

## RBFE harness — BUILT (2026-07-06), ready to fire pending FEP-GPU + a smoke shakeout
Per trimcrae's choice (RBFE relative to 401, riding 401's existing ABFE), the harness is wired, reusing ALL the
ABFE spot/checkpoint/sharding/reduce plumbing; only the alchemical core is new and comes from OpenFE's
`RelativeHybridTopologyProtocol` (mapping + hybrid topology + relative λ + MBAR turnkey — no hand-rolled
soft-core, no Boresch/SSC since both ligands share the pose). Files:
- **`rbfe_edges.py`** (pure, **7/7 unit tests pass**) — edge/leg enumeration, ΔΔG cycle (`ΔΔG_bind = ΔG_complex_morph
  − ΔG_solvent_morph`), anchoring on 401's ABFE, selectivity + the **anchor-free** selectivity change. Atom-map
  sanity confirms the edge: **22 common atoms, 401 a perfect subgraph (0 unique), lo_m0_NCCO adds the 4-atom
  acetamido** → textbook single-edge morph.
- **`nr4a3_rbfe.py`** (OpenFE engine), **`nr4a3_rbfe_sagemaker.py`** (submitter; `mode=plan` validated locally),
  **`sagemaker_src/entry_rbfe.py`** + **`environment-rbfe.yml`** (openfe env), **`gpu-rbfe-aws.yml`** (plan/smoke/
  run/reduce; default plan).
- **Dispatch:** `gpu-rbfe-aws.yml mode=run ligand_a=denovo_401 ligand_b=lo_m0_NCCO_gen receptor_prefix=nr4a3-leadopt-species`.
  **Validate-first:** `mode=smoke` (openfe env + mapping + hybrid-topology build, no MD) → `only_legs=solvent`
  (one real morph leg) → full fleet. **SHAKEOUT-PENDING** like every engine here: the OpenFE settings + env are
  first-pass; trust numbers only after the smoke + one-leg shakeout on a real FEP GPU. Also: the new workflow must
  be merged to `main` before it's API-dispatchable.

## Why RBFE, not ABFE (cheaper + more accurate here)
The lead set is a **congeneric series off one scaffold** (401 = H → ethyl/acetamido at the ortho position), so
the affinity *difference* is a **relative** perturbation. RBFE (denovo_401 → lo_m0_NCCO, per receptor) gives the
ΔΔ directly, is cheaper and better-converged than the single-ligand ABFE 401 needed, and rides 401's ABFE that
is already run. **Building the RBFE map is the one FEP-side code task worth doing before the run** (the current
`nr4a3_abfe.py` harness is ABFE; ABFE on lo_m0_NCCO_gen works today with the command above, RBFE is the upgrade).
Honest caveat: MM-GBSA magnitudes are not calibrated affinities (401's −35 MM-GBSA maps to a converged +
offset-corrected ABFE of ~−4.5 kcal/mol); the lead beats 401 by the *same* cheap tier + the decoy null, which
is the pre-FEP nomination bar — RBFE is the arbiter of *how much* tighter. Anchor note: RBFE's absolute for
lo_m0_NCCO rides 401's **offset-corrected** converged ABFE (rbfe_edges.ANCHOR_401_ABFE, updated 2026-07-06);
the RBFE ΔΔG and the selectivity *change* are offset-free and do not depend on the anchor at all.

## Role of `denovo_401`: affinity ANCHOR, not a disposable "pathfinder" (clarification, 2026-07-15)
**⚠ TRACK CONTEXT (2026-07-15) — read first.** This 401 lead-opt RBFE track is part of the now-**SHELVED
Track A** (de novo warhead / ABFE-validation). The **LIVE program is Track B**, whose primary quantitative RBFE
is the **Zaienne cmpd19 congeneric series** (`nr4a3-congeneric-rbfe-plan.md`; anchor = `zaienne_cmpd19`, a real
literature compound with functional NR4A3 engagement), and in which **`denovo_401` is a *side comparator only*.**
So the *flagship warhead RBFE is cmpd19-anchored, NOT 401-anchored.* Everything below is accurate **within the
401 track** (where 401 is that track's anchor), but do not read it as "401 anchors the live program." The
`nr4a3-rbfe-spotsmoke` / v3 runs use a **401 edge purely because its atom map is clean + already validated** — a
low-risk vehicle to shake out the spot-checkpoint *code*; the **first real science RBFE should be a cmpd19
congeneric edge**, not 401.

Two different senses of "first run" get conflated — keep them separate:
- **`denovo_401` = the affinity ANCHOR of the relative-FE network (load-bearing, stays central).** RBFE yields
  only a *difference* (ΔΔG) between two congeneric analogues; it cannot place any candidate on an absolute
  scale by itself. You anchor the whole network on ONE molecule whose absolute ΔG is pinned by an independent
  method — here `denovo_401`, whose offset-corrected converged **ABFE** (`rbfe_edges.ANCHOR_401_ABFE`,
  `nr4a3-abfe-calibration.json`) every RBFE edge rides. So 401 is **not** a scout that gets discarded once the
  bigger fan-out starts: as more candidate edges are added (e.g. `lo_m0_NCCO_iso01`, `lo_m0_CC`, and any future
  warheads), they all hang off — and are put on the same absolute scale by — the 401 ABFE anchor. Remove 401 and
  the network loses its absolute reference. (The ΔΔG and selectivity *change* are anchor-free; the absolute ΔG of
  every downstream candidate is not.)
- **`denovo_401` is a de novo BENCHMARK, not a synthesis lead.** It is a generated reference compound, not a
  molecule we would make. The leads are its congeneric derivatives (`lo_m0_NCCO` = 401 + ortho-acetamido, the
  "better-than-401 lead") and the parallel `zaienne_cmpd19` congeneric campaign
  (`nr4a3-congeneric-rbfe-plan.md`); 401 is the fixed baseline they are measured against.
- **The *pipeline* pathfinder is a SEPARATE notion (about infra, not about 401).** We run one edge first — the
  `401 → lo_m0_NCCO_gen` solvent/complex leg on a throwaway/pilot tag — to shake out the RBFE + spot-checkpoint
  machinery end-to-end before fanning out to the full edge set. That validates the *infrastructure*; it does
  **not** mean 401 is a throwaway molecule. (A tiny-iteration `nr4a3-rbfe-spotsmoke` run is purely a code test
  and its ΔG is discarded; the real 401-anchored edges are the science.)
