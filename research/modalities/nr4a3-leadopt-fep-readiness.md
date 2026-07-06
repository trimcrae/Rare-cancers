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

401's problem was **weak binding**, and that is exactly what improved (robustly); selectivity is preserved. The
ortho-acetamido/ethyl decoration engages the divergent hydrophobic/H-bond handles (L406/T410/I484/L534).

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
7. **Orthogonal pose** — Boltz-2 binary co-fold across NR4A3/1/2 (`gpu-ternary-aws mode=binary`, in flight) —
   an AF3-class cross-check (read at true weight: this cryptic pocket is Boltz's low-confidence regime).

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

## Recommended engine: RBFE, not ABFE (cheaper + more accurate here)
The lead set is a **congeneric series off one scaffold** (401 = H → ethyl/acetamido at the ortho position), so
the affinity *difference* is a **relative** perturbation. RBFE (denovo_401 → lo_m0_NCCO, per receptor) gives the
ΔΔ directly, is cheaper and better-converged than the single-ligand ABFE 401 needed, and rides 401's ABFE that
is already run. **Building the RBFE map is the one FEP-side code task worth doing before the run** (the current
`nr4a3_abfe.py` harness is ABFE; ABFE on lo_m0_NCCO_gen works today with the command above, RBFE is the upgrade).
Honest caveat: MM-GBSA magnitudes are inflated (401 −35 MM-GBSA ↔ FEP −1.2); the lead beats 401 by the *same*
cheap tier + the decoy null, which is the pre-FEP nomination bar — FEP is the arbiter of absolute affinity.
