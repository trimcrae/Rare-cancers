# NR4A3 degrader paper — display items (figures + tables) plan

> **Role:** the figure/table plan for [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md). A results
> paper needs display items; this maps each result to a figure, lists the **data asset** that backs it
> (✅ exists / ⚙️ generate), and the generator. Render via `.github/workflows/render-figures.yml`. No
> figure may assert beyond its cited data (medical integrity); every panel states its weight (model/MD/
> docking-prior). Nothing here is fabricated — panels marked ⚙️ are to be plotted from committed JSON/MD.

## Figures

**Fig 1 — NR4A3's orthosteric pocket is borderline, calibrated not asserted (§2.1).**
- (a) AF2 NR4A3 LBD cartoon with Pocket-5 (res 406–534) + the 7 divergent handles highlighted.
  Asset: `AF-Q92570.pdb` (fetch) + `nr4a-selectivity.json`. ⚙️ PyMOL/NGL render.
- (b) Calibration bar chart: the validated drug-bound NR band (PPARγ 0.599, ERα 0.586, Nurr1-holo 0.677,
  Nur77-holo 0.529; D\*=0.53) vs **static NR4A3 0.495** vs **opened NR4A3 0.931**. Asset:
  `nr4a3-calibration.json` ✅ + `nr4a3-structure-assessment.json` ✅. ⚙️ matplotlib bar.
- *Message:* static pocket sits just below the druggable band — concordant with "undruggable".

**Fig 2 — Metadynamics opens a druggable cryptic pocket (§2.2; Gates 2–3).**
- (a) F(Rg) free-energy profile from `fes.dat` (closed basin → opened), marking the druggable-at-Rg≈0.72,
  ~0.76 kcal/mol point. Asset: `nr4a3-metad/fes.dat` (S3) ⚙️.
- (b) Per-frame fpocket druggability vs CV Rg (the F(Rg)-vs-druggability correlation that resolves Gate 3).
  Asset: `pocket_druggability.png` ✅ (regenerate from `pocket_analysis_summary.json`).
- (c) Closed (static AF2) vs opened (frame 300, 0.931) pocket surface render. Asset: `nr4a3-opened.pdb`
  (warhead output, S3) ⚙️.
- *Message:* the thermally-populated ensemble is robustly druggable at negligible cost.

**Fig 3 — Selectivity handles and the handle-facing confirmation (§2.3).**
- (a) The 7 divergent Pocket-5 residues mapped on the opened pocket, the 5 engageable ones highlighted.
  Asset: `nr4a-selectivity.json` ✅ + `nr4a3-opened.pdb`. ⚙️ render.
- (b) Per-handle pocket-facing fraction in the druggable frames (the CONFIRMED Gate-2 sub-check: L406/T410/
  I484/I531/L534 ≥0.875; T407 0.0, R412 0.25). Asset: `handle_facing.png` ✅ / `handle_facing_summary.json`.
- *Message:* 5 of 7 handles are realistically engageable — measured, not assumed.

**Fig 4 — The family-wide selectivity matrix (§2.4; the paper's distinctive contribution).**
- (a) Schematic: the *same* cryptic-pocket metadynamics on NR4A1/NR4A2/NR4A3 → three state-matched opened
  ensembles → one library docked into each.
- (b) Matrix heatmap: candidates (rows) × {NR4A3, NR4A1, NR4A2} opened-pocket dG (columns), annotated with
  the assigned cell (NR4A3-only / pan / NR4A1+NR4A3 anti-target). Asset: `nr4a3-matrix.json` ⚙️ (after the
  matrix run). ⚙️ matplotlib heatmap.
- (c) Cell census + the three actionable sets (selective leads / pan leads / flagged anti-targets).
- *Message:* programmable, state-matched selectivity — the divergent-handle map as a demonstrated design axis.

**Fig 5 — Indication matrix + degrader schematic (§3) [optional/overview].**
- Lead (NR4A3-only → EMC/AciCC) / second mode (pan → ex-vivo immuno) / anti-target (NR4A1+NR4A3 → AML,
  design away), with the degrader/E3 ternary cartoon. Schematic, no new data.

## Tables

- **Table 1 — Calibration panel** (structure, type, max druggability, ligand-site druggability) from
  `nr4a3-calibration.json` ✅ + the reconciliation table.
- **Table 2 — Top matrix candidates**: label, ChEMBL id, dG into each opened pocket, margins, cell,
  engageable-handle + conserved contacts. From `nr4a3-matrix.json` ⚙️ (after the matrix run).
- **Table 3 — Pre-registered gates and outcomes** (Gate 0/0b/1/2/3/4, pass/fail, with the Gate-0
  deviation) from `nr4a3-druggability-prereg.md` ✅.

## Generation notes
- Plots that read committed JSON (Figs 1b, 3b; Tables 1,3) can render now; Figs 2,4 + Table 2 need the
  S3 ensemble/matrix outputs (regenerate plots in the analysis/matrix jobs and copy out, OR add a
  `render-figures` step that pulls the JSON).
- Keep every panel caption's claim within its data weight: AF2 = model; metad = biased MD ensemble;
  docking dG = triage prior (not affinity); MM-GBSA/FEP = the planned quantitative tier (not yet run).
