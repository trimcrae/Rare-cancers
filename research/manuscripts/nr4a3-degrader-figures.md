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
- *Message:* the pocket *breathes* to a geometrically druggable cavity at low apparent cost — a
  feasibility readout (biased ensemble; metastability pending the release run), not a calibrated affinity.

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

**Fig 6 — A *designed* selective warhead candidate (§2.5; matrix step 3).**
- (a) The de-novo funnel: DiffSBDD generation on the opened pocket → free-CPU screen (novelty →
  developability → 3-pocket docking → selectivity fingerprint → PROTAC handle) → MM-GBSA confirmation.
  Schematic of the two-GPU-run, free-CPU-middle pipeline.
- (b) The designed candidate: 2D structure + predicted binding pose in the opened NR4A3 pocket, annotated
  with the engageable handles it contacts. Asset: `nr4a3-denovo.json` ⚙️ + `docked_nr4a3.sdf` (after the
  screen). ⚙️ RDKit/PyMOL render.
- (c) Its selectivity bar: MM-GBSA ΔG into NR4A3 vs NR4A1/NR4A2 (the `confirmed_selective` verdict), beside
  its developability/PROTAC-assembly profile. Asset: `nr4a3-mmgbsa.json` (denovo run) ⚙️.
- **Caption must state:** the molecule is a **model-generated, novel** design hypothesis (ECFP Tanimoto
  ≤ 0.40 to any known NR4A active), docking is a screening prior, MM-GBSA is direction-only, the pocket is
  biased-MD-opened — not a validated warhead. *Message:* the design space yields a bona-fide selective
  candidate, the result the repurposing matrix could not provide.

## Tables

- **Table 1 — Calibration panel** (structure, type, max druggability, ligand-site druggability) from
  `nr4a3-calibration.json` ✅ + the reconciliation table.
- **Table 2 — Top matrix candidates**: label, ChEMBL id, dG into each opened pocket, margins, cell,
  engageable-handle + conserved contacts. From `nr4a3-matrix.json` ⚙️ (after the matrix run).
- **Table 3 — Pre-registered gates and outcomes** (Gate 0/0b/1/2/3/4, pass/fail, with the Gate-0 *and
  Gate-1* disclosed deviations — Gate 1 met only in the weaker basin-breathing sense; Gate 3 provisional)
  from `nr4a3-druggability-prereg.md` ✅.
- **Table 4 — The designed candidate** (label, novel SMILES, ECFP Tanimoto to nearest known active, dG into
  each opened pocket, MM-GBSA margins + verdict, QED/SAscore/PAINS, PROTAC handle) from `nr4a3-denovo.json`
  + the denovo `nr4a3-mmgbsa.json` ⚙️ (after the screen + confirmation). Flag: designed hypothesis, not a lead.

## Generation notes
- Plots that read committed JSON (Figs 1b, 3b; Tables 1,3) can render now; Figs 2,4 + Table 2 need the
  S3 ensemble/matrix outputs (regenerate plots in the analysis/matrix jobs and copy out, OR add a
  `render-figures` step that pulls the JSON).
- Keep every panel caption's claim within its data weight: AF2 = model; metad = biased MD ensemble;
  docking dG = triage prior (not affinity); MM-GBSA/FEP = the planned quantitative tier (not yet run).
