# valB (ternary known-answer benchmark) — reviewer decision + redesign, 2026-07-17

**Context.** valB is reviewer mandatory-change-1C: a KNOWN-ANSWER NONCOVALENT VHL ternary benchmark that
validates the paper's bespoke ΔΔG_coop cooperativity cycle (ΔΔG_coop = ΔΔG_alch,ternary − ΔΔG_alch,binary)
before it is trusted on NR4A. It is a GO/NO-GO gate on the flagship prospective matrix.

## What we found (free CI; RCSB + RDKit; artifacts on `modalities-cache`)

- The **original design** (morph a high-cooperativity SMARCA2–VHL degrader P1/9HYN α=93 → low P5/9HYP α=0.6)
  is **not congeneric**: 26–32 perturbed heavy atoms, 55% shared scaffold (different warhead cores). A full
  pairwise sweep of the same-assay panel (P1–P5 + MZ1) → every pair perturbs 32–47 atoms. No clean relative-FEP
  edge. (`ternary-calib-pair-frozen.json` → `panel_sweep`.)
- A **wide RCSB search** (all 142 VHL PDB entries; 65 carry a PROTAC-scale degrader; tight congeneric gate
  ≥75% shared, ≤12 perturbed) → the **only** congeneric *different-ligand* edge in the public record is
  **7Z76(IFJ) ↔ 9HYB(A1IYB)** (7 atoms). All other congeneric pairs are the SAME molecule re-crystallized.
  (`ternary-calib-congeneric-search.json`.) That one edge spans **two papers** (7Z76 = Kofink 2022;
  9HYB = Nat Commun 2025) → a cross-paper comparison; its Δα ≈ 0.4 kcal/mol (near the noise), so it is at best
  weak secondary corroboration, not the gate.

**Conclusion:** no clean, same-assay, congeneric, both-α-measured relative-FEP cooperativity edge exists where
*both* endpoints have public ternary crystal structures — my structural search over-constrained by requiring
both endpoints solved; RBFE needs only ONE template + a modeled congener.

## Reviewer verdict (conditional approval + required substitution)

**valB_mini = PROTAC 2 → cis-PROTAC 2** (SMARCA2–VHL), staged from **PDB 6HAX** (PROTAC 2's solved ternary).
- Same-assay, same-paper (Farnaby et al. 2019) TR-FRET pair: **α = 18 (active) → 1.0 (cis)** (~18×).
- A single-stereocenter congeneric edge (VHL 4-hydroxyproline trans→cis; abolishes VHL binding) — trivially
  mappable; runs on the existing active→epimer harness. ONE crystal template stages both endpoints.
- **Preregistered target:** ΔΔG_exp = −RT·ln(α_cis/α_active) = −RT·ln(1/18) = **+1.71 kcal/mol** at 298.15 K
  (active→cis). Superior to MZ1→cis-MZ1: not merely on/off, it supplies a measured ~18× contrast.
- Backup (if the cis endpoint proves non-representable): **ACBI1 → cis-ACBI1** (same 2019 table, α 30→1.0;
  2025 table 25±12→1.0). PROTAC 2 preferred because its active ternary endpoint = 6HAX exactly.

### Preregistered gates (valB_mini)
- **GO to valB_full:** positive sign; combined uncertainty excludes zero; estimate within 1.0 kcal/mol of
  +1.71; independent repeats AND fwd/rev agree within ~0.5 kcal/mol; overlap + sampling diagnostics pass.
- **NO-GO:** converged wrong sign, converged error > 1.0 kcal/mol, or strong restraint/initialization dependence.
- **INDETERMINATE (not a pass):** CI includes zero; unresolved hysteresis; or the cis endpoint cannot be
  represented as a defensible thermodynamic state.
- **cis-endpoint diagnostics are MANDATORY** (cis is a weak/non-binder): report ligand RMSD, VHL contact
  occupancy, restraint work + restraint sensitivity. A positive result produced only by forcibly retaining
  cis-PROTAC 2 in the active crystallographic pose is **not** a pass.

### Scope / ladder
- valB_mini **GATES spend on valB_full**; it does **NOT** by itself authorize the NR4A flagship matrix.
- **valB_full** must add ≥1 **all-binding graded congeneric edge** (both productive binders) before claiming the
  method ranks cooperativity among productive ternary complexes. Reviewer's preflight candidate: the same-assay
  **Wurz et al. SMARCA2–VHL series, compound 1→4 (α 12.8→2.6 ≈ +0.94 kcal/mol)**; a free preflight establishes
  mapper quality + staging (one template + a small congener; both endpoints need NOT be separately solved).

### Provisional claim restrictions (until valB_full passes) — apply in the manuscript
- Describe NR4A ternary scores as **exploratory / hypothesis-generating**.
- Do **not** claim validated quantitative cooperativity ranking or selective ternary stabilization.
- Keep **binary RBFE** conclusions separable from **ternary** conclusions.
- Do **not** spend on or present the flagship ternary matrix as validated.
- If valB_mini or the all-binding benchmark fails, permanently rescope the paper around binary affinity,
  structural plausibility, and explicitly unvalidated ternary hypotheses.

### Reviewer corrections to our analysis (recorded)
1. 7Z76 vs 9HYB is **same-assay-family (TR-FRET), not ITC-vs-TR-FRET** — principally a cross-*paper* issue.
   Same-paper provenance is not a hard requirement; comparable assay definition/constructs/α-calc is.
2. Requiring **both** RBFE endpoints to have public ternary structures is over-restrictive — one reliable bound
   template + a small congeneric perturbation is sufficient in principle (this is why PROTAC 2/cis-PROTAC 2 was
   missed by the structural-only search).

## Build status (2026-07-17)
Frozen (`ternary-calib-epimer-frozen.json`), harness wired (`ternary_coop_prep._morph_endpoints` →
`resolved_calib_epimer`, tests pass), 6HAX staging built + CPU-validated (`ternary_pdb_stage.py`; one clean
SMARCA2·VHL·EloB·EloC complex + matching PROTAC pose), GCP L4 ternary lane built
(`gpu-ternary-fep-gcp.yml`); GPU assembly smoke running. Next: real mini (mode=run, ~$40–80) → reduce vs +1.71.
