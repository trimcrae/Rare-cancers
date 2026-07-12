# Layer-1 calibration hi/lo pair — DRAFT selection (not yet frozen)

**Status:** DRAFT recommendation for the `calib_hi_to_lo` pilot morph edge. **Nothing here is frozen and no
SMILES is fabricated.** `ternary_coop_prep._morph_endpoints` deliberately still returns
`status="pending_calib_pair_freeze"` for the calib legs (a tested honesty contract) — this doc is the curation
input that, once its ligand chemistry is primary-source-verified via a CI fetch, gets frozen into the prereg.

## What the pilot needs

The ternary pilot's calibration arm is a **single relative-alchemical edge** morphing a **high-cooperativity**
SMARCA2–VHL degrader into a **low-cooperativity** one, run in both the binary (VHL only) and ternary
(VHL+SMARCA2) environments. `ΔΔG_coop(hi→lo) = ΔΔG_alch,ternary − ΔΔG_alch,binary` must recover the **known
measured Δα(hi−lo)** within tolerance (prereg `retrospective_bar.vhl_panel`). The prereg preregisters this as a
**nonredundant** edge — no cycle-closure claim (JSON `frozen_manifest.cycle_closure_stance`).

## The verified panel to choose from (already primary-source-verified in the prereg)

From `nr4a3-ternary-coop-prereg.json → calibration.layer1_vhl_panel.candidate_systems` (Nat Commun 2025,
PMC12480974, Supplementary Table 1 — all `verified: true`, with solved PDBs):

| system | α (TR-FRET) | class | PDB |
|---|---|---|---|
| smarca2_p1 | **93** | strong cooperative | 9HYN |
| smarca2_p3 | 5.0 | cooperative | 9HYB |
| smarca2_p2 | 4.1 | cooperative | 7Z77 |
| smarca2_p4 | 1.3 | near-neutral | 9HYO |
| smarca2_p5 | **0.6** | weakly negative | 9HYP |

## Recommendation: **P1 (hi, α=93, 9HYN) → P5 (lo, α=0.6, 9HYP)**

- **Widest, most decision-relevant Δα** in the same assay/series: ~2.2 log-units. A wide spread is exactly what
  makes the *first* calibration edge achievable — we are asking the method to resolve a large, unambiguous
  cooperativity difference, not a fine one. If it cannot recover *this* gap, the method is not ready, and we
  learn that on one edge.
- **Both crystallographically characterized** (9HYN, 9HYP) → both the binary and ternary starting poses come
  from experimental structures, not a speculative co-fold, which de-risks the pose input for the calibration
  edge specifically.
- **Same assay + same series** → the Δα is a same-observable comparison (avoids the alpha_TR-FRET vs
  alpha_ITC heterogeneity flagged for the MZ1 system).

### The real tradeoff to resolve at freeze time (needs the actual ligand structures)

A P1→P5 morph is only a clean, low-variance RBFE edge if P1 and P5 are **congeneric** (shared scaffold; the
perturbation is a linker/exit-vector change LOMAP can map). The SMARCA2–VHL P1–P5 set is a linker/exit-vector
series, so this is *plausible* but **not verifiable without the ligand structures**. Two honest contingencies,
decided only after the CI fetch below returns the real chemistry:

1. **If P1↔P5 is a mappable congeneric edge** → use it (widest Δα, recommended).
2. **If P1↔P5 is too large a perturbation to map/converge** → fall back to the widest *congeneric* pair that
   still spans a real class difference (e.g. P1→P4, Δα 93→1.3; or a P2/P3→P5 edge), accepting a smaller Δα for
   a more tractable morph. Record the choice + rationale; do not force an unmappable edge.

## Freeze procedure (no fabrication — CI fetch, then commit)

1. **Fetch the bound-ligand chemistry** for 9HYN and 9HYP from RCSB via a CI runner (egress proxy blocks RCSB
   in-sandbox — same pattern as the Layer-1 dossier fetch on `fusion-cpu-extras.yml`): pull each entry's
   ligand instance → canonical SMILES + the ligand's coordinates (for the posed starting structure).
2. **RDKit-validate** each SMILES, confirm the shared VHL-ligand (VH032-class) + SMARCA2-warhead substructures,
   and compute the LOMAP/Kartograf mapping between the P1 and P5 ligands to **confirm congenericity** (decides
   contingency 1 vs 2 above).
3. **Freeze** the chosen hi/lo compound ids, PDB ids, SMILES (with provenance refs), and the measured Δα into
   `ternary_coop_prep` (resolve `calib_hi`/`calib_lo` endpoints) + the prereg JSON, and flip the calib legs'
   `_morph_endpoints` status from `pending_calib_pair_freeze` to `resolved` **only then**.
4. The staged calib starting structures (`calib_hi_to_lo__*/complex.pdb` + `ligands.sdf`) then come directly
   from the crystal structures 9HYN/9HYP (binary = VHL chains; ternary = VHL+SMARCA2), not a co-fold — a
   cleaner input than the NR-V04 arm.

## What is NOT blocked by this

The **NR-V04 family-transfer arm** (`nrv04_active_to_epimer__{binary_vhl,ternary_nr4a1}`) — the core
"can the method recover NR4A1-selectivity" test — does **not** depend on this freeze. Its endpoints resolve from
the existing NR-V04 benchmark chemistry (`nrv04_ternary`), so that arm can be staged + smoked first, with the
calibration arm added once the pair is frozen per the steps above.
