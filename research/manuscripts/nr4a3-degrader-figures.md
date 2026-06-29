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
  `nr4a3-calibration.json` ✅ + `nr4a3-structure-assessment.json` ✅. ⚙️ matplotlib bar. **Caption must
  flag** the opened-NR4A3 bar as a *biased-MD-frame, uncalibrated* readout (different weight from the
  *static* drug-bound bars) — e.g. plot it in a distinct hatch/colour with an explicit "(biased ensemble;
  not calibrated vs static)" label, so the figure does not imply a like-for-like beat of the drug-bound band.
- *Message:* static pocket sits just below the druggable band — concordant with "undruggable".

**Fig 2 — Metadynamics opens a druggable cryptic pocket (§2.2; Gates 2–3).**
- (a) F(Rg) free-energy profile from `fes.dat`, marking the druggable-at-Rg≈0.72, ~0.76 kcal/mol point.
  Asset: `nr4a3-metad/fes.dat` (S3) ⚙️. **Caption must state** the profile is *monotonic* (single closed
  basin, no separate opened minimum) and the frontier is under-converged — i.e. basin-internal breathing,
  not a two-state opening; mark the well-sampled vs under-converged regions of the curve.
- (b) Per-frame fpocket druggability vs CV Rg (the F(Rg)-vs-druggability correlation behind the Gate-3
  *provisional* read). Asset: `pocket_druggability.png` ✅ (regenerate from `pocket_analysis_summary.json`).
- (c) Closed (static AF2) vs opened (frame 300, 0.931) pocket surface render. Asset: `nr4a3-opened.pdb`
  (warhead output, S3) ⚙️.
- (d) **Unbiased release run (Gate 3 resolved).** Two-panel: (i) Rg trace of the 3 unbiased replicas
  seeded at the low-energy druggable frame, all holding ~0.74 nm for 5 ns (metastable, no collapse); (ii)
  per-frame fpocket on the unbiased release trajectory as a distribution, marking fraction ≥ D\*=0.53 = 0.20
  (~24 % druggable). Asset: `nr4a3-release/release_summary.json` + `nr4a3-release-pocket/` ✅ (S3). ⚙️.
  **Caption:** druggable on *unbiased* dynamics ~¼ of the time → induced-fit / conformational-selection
  cavity, **not** a bias artifact and **not** always-open.
- *Message:* the pocket *breathes* to a geometrically druggable cavity at low apparent cost, and an
  unbiased release run confirms that cavity is **metastable and druggable ~24 % of the time** — a
  thermally-real induced-fit site, not a calibrated affinity and not always-open.

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
  the assigned cell (NR4A3-only / pan / NR4A1+NR4A3 anti-target). Asset: `nr4a3-matrix.json` ✅ (S3;
  matrix run complete) + `nr4a3-matrix.png` ✅. ⚙️ matplotlib heatmap.
- (c) Cell census + the three actionable sets (selective leads / pan leads / flagged anti-targets) — the
  **anti-target cell is empty** (no candidate engages NR4A1+NR4A3 sparing NR4A2). Read via `report-matrix-aws.yml`.
- *Message:* programmable, state-matched selectivity — the divergent-handle map as a demonstrated design axis.

**Fig 5 — De-novo design and MM-GBSA confirmation of a selective warhead candidate (§2.5; the result figure).**
- (a) Funnel schematic: Step-0 druggable *release* receptor → DiffSBDD pocket-conditioned generation (lead-size
  constrained) → cheminformatics + pose handle-contact triage → dock into 3 state-matched pockets → MM-GBSA.
  Schematic.
- (b) Generation quality scatter: SAscore vs QED of the ~200 generations, coloured by engageable-handle
  contacts. Asset: `nr4a3-denovo.png` ✅ / `nr4a3-denovo.json` ✅ (S3). ⚙️.
- (c) **MM-GBSA verdict panel:** the de-novo verdict census (confirmed_selective 3 · rescued 7 · weakened 1 ·
  confirmed_nonselective 9 · **reversed 0**) contrasted with the *repurposed*-library MM-GBSA (where the
  apparent lead cytosporone B **reverses**). Asset: `nr4a3-denovo-mmgbsa` + `nr4a3-mmgbsa` ✅ (S3, via
  `report-mmgbsa-aws.yml`). ⚙️ bar.
- (d) **Lead `denovo_15`** 2D structure (`C=C(CC1=CC=C(NC(=O)O)C1)[C@H]1C=C2C(=NC1)OC[C@H](C)[C@@H]2C`;
  QED 0.774, SA 5.08) in the NR4A3-release pocket, the 4 engaged handles labelled; MM-GBSA NR4A3-margin
  +10.7 kcal/mol (direction, not affinity). Asset: `nr4a3-denovo.sdf` (pose) + receptor ✅ (S3, via
  `report-denovo-aws.yml`). ⚙️ render.
- *Message:* a **designed** NR4A3-selective warhead candidate that survives *two* energy tiers with no
  reversal — the de-novo route succeeds where repurposed matter did not (screening-grade prediction; no
  wet lab; FEP/ternary ahead).

**Fig 6 — Indication matrix + degrader schematic (§3) [optional/overview].**
- Lead (NR4A3-only → EMC/AciCC) / second mode (pan → ex-vivo immuno) / anti-target (NR4A1+NR4A3 → AML,
  design away), with the degrader/E3 ternary cartoon. Schematic, no new data.

## Tables

- **Table 1 — Calibration panel** (structure, type, max druggability, ligand-site druggability) from
  `nr4a3-calibration.json` ✅ + the reconciliation table.
- **Table 2 — Top matrix candidates**: label, ChEMBL id, dG into each opened pocket, margins, cell,
  engageable-handle + conserved contacts. From `nr4a3-matrix.json` ✅ (matrix run complete; via
  `report-matrix-aws.yml`).
- **Table 3 — Pre-registered gates and outcomes** (Gate 0/0b/1/2/3/4, pass/fail, with the Gate-0 *and
  Gate-1* disclosed deviations — Gate 1 met only in the weaker basin-breathing sense; **Gate 3 now
  release-confirmed as an induced-fit cavity**, no longer provisional) from `nr4a3-druggability-prereg.md` ✅.
- **Table 4 — De-novo candidates funneled to MM-GBSA**: name, SMILES, QED, SAscore, engageable-handle
  contacts, docking cell, MM-GBSA NR4A3-margin, verdict — for the top-20 generations, spotlighting the 3
  *confirmed_selective* (denovo_15 / 94 / 57). From `nr4a3-denovo.json` + `nr4a3-denovo-mmgbsa` ✅ (S3, via
  `report-denovo-aws.yml`). Caption: MM-GBSA magnitudes inflated (direction, not affinity); screening-grade.

## Generation notes
- Plots that read committed JSON (Figs 1b, 3b; Tables 1,3) can render now; Figs 2,4,5 + Tables 2,4 read S3
  outputs that now **exist** (release, matrix, MM-GBSA, de-novo) — pull them via the `report-*-aws.yml`
  read-only jobs (matrix / mmgbsa / denovo) or add a `render-figures` step that fetches the JSON/PNG.
- Keep every panel caption's claim within its data weight: AF2 = model; metad = biased MD ensemble;
  unbiased release = thermally-real but induced-fit (~24 % druggable); docking dG = triage prior (not
  affinity); **MM-GBSA = run, but single-snapshot/no-entropy → read the verdict/direction, not the
  kcal/mol**; FEP = the defensible affinity tier, **not yet run**.
- **Before submission:** collate the `denovo_15` 2D depiction + its pose (Fig 5d) and Table 4 from the
  `report-denovo-aws.yml` output; the SMILES is `C=C(CC1=CC=C(NC(=O)O)C1)[C@H]1C=C2C(=NC1)OC[C@H](C)[C@@H]2C`.
