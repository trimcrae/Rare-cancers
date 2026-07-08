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
- (c) Cell census + the three actionable sets (selective leads / **pan leads** / flagged anti-targets) — the
  **anti-target cell is empty** (no candidate engages NR4A1+NR4A3 sparing NR4A2), while the **pan-NR4A cell is
  populated (3 members, incl. an equipotent tri-paralogue engager)** — the seed of the CAR-T pole (Fig 6b).
  Read via `report-matrix-aws.yml`; pan readout collated in `nr4a3-pan-readout.json` ✅ (repo).
- *Message:* programmable, state-matched selectivity — the divergent-handle map as a demonstrated design axis.

**Fig 5 — De-novo design, the decoy specificity control, and multi-snapshot de-noising of a selective candidate (§2.5–§2.6; the result figure).**
> **Updated 2026-06-30 to match the current paper.** The earlier version made `denovo_15` the
> "MM-GBSA-confirmed selective" hero. That is **retracted**: the single-snapshot MM-GBSA verdict failed a
> decoy control (39 % of non-NR4A drugs score "selective"), so the figure must lead with the *control* and the
> the robust lead **`denovo_401`** (multi-snapshot-confirmed + species-resolved), not `denovo_15`. (The
> single-snapshot decoy-calibrated `denovo_111` was later **withdrawn** — its physiological cation reverses
> selectivity, pre-FEP species sweep — so denovo_401 is the sole robust lead.)
- (a) Funnel schematic: Step-0 druggable *release* receptor → DiffSBDD pocket-conditioned generation (lead-size
  constrained) → cheminformatics + developability gate + pose handle-contact triage → dock → single-snapshot
  MM-GBSA → **decoy-null calibration → multi-snapshot de-noising**. Schematic.
- (b) Generation quality scatter: SAscore vs QED of the ~200 generations, coloured by engageable-handle
  contacts. Asset: `nr4a3-denovo.png` ✅ / `nr4a3-denovo.json` ✅ (S3). ⚙️.
- (c) **Decoy specificity control (the load-bearing negative):** distribution of single-snapshot MM-GBSA
  NR4A3-margins for the 38 non-NR4A decoy drugs vs the de-novo set, marking the **95th-percentile decoy bar
  (+13.1 kcal/mol)** and the **39 % decoy `confirmed_selective` rate** — showing the raw verdict is non-specific
  and the de-novo set is *not enriched*. `denovo_111` (+15.7) is the one candidate above the bar. Asset:
  `nr4a3-decoy-mmgbsa` + `nr4a3-denovo-mmgbsa-dev` ✅ (S3, via `report-mmgbsa-aws.yml`). ⚙️ bar/strip.
- (d) **Multi-snapshot de-noising panel (§2.6):** single-snapshot vs multi-snapshot mean ± SD for the lead set
  — `denovo_393` collapses (+18.34 → −2.95 ± 3.65), negative control `denovo_924` stays non-selective, and
  **`denovo_401` holds (+12.83 ± 2.98, margin − SD = +9.85)**. Asset: `nr4a3-denovo-mmgbsa-v2-ms` /
  `-v3deep-ms` ✅ (S3, via `report-mmgbsa-aws.yml`). ⚙️ bar with error bars.
- (e) **Lead `denovo_401`** 2D structure (`COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`;
  MW 304, QED 0.80, SA 3.87, no structural alerts) in the NR4A3-release pocket, the engaged handles labelled.
  Asset: `nr4a3-denovo-v2` pose + receptor ✅ (S3, via `report-denovo-aws.yml`). ⚙️ render. **Caption:** the
  first multi-snapshot-confirmed NR4A3-selective candidate; still single-trajectory GB-implicit (non-FEP),
  unsynthesized. (`denovo_15` may appear in an SI panel **only** as the retracted artifact — annotate its
  liabilities: carbamic acid, 1,3-cyclopentadiene, imine, exocyclic alkene; no aromatic ring; SA 5.08 > the
  ≤4.5 cut — never as a lead.)
- (f) **Receptor-frame-dependence of the decoy-null result (the load-bearing honesty panel).** denovo_401's
  multi-snapshot margin vs a *same-tier* decoy null (n=38) in TWO receptor frames: it clears the whole null in the
  unbiased **release** design frame (+12.83 ± 2.98 vs 95th +6.69 / max +7.10) but does **not** clear in the biased
  **metad-opened** frame (+7.44 ± 4.18 vs 95th +17.70 / max +24.74, where random drugs like diphenhydramine +24.74
  also score "selective"). **Asset: `nr4a3-frame-decoynull.png` ✅ (committed; generator
  `nr4a3_frame_decoynull_figure.py`, values transcribed from §2.6).** **Caption:** the claim is a de-noised
  *foothold in the design frame*, not a frame-invariant specificity result; the null controls the scoring step,
  not the generative step.
- *Message:* the de-novo funnel's raw endpoint metric is **non-specific** (decoy control), but decoy-calibration
  plus multi-snapshot de-noising isolate a single robust candidate (`denovo_401`) — a screening-grade prediction,
  and one whose margin is **honestly receptor-frame-dependent** (panel f); no wet lab; FEP/ternary ahead.

**Fig 6 — The programmable NR4A selectivity axis: one cryptic pocket, two design poles (§3; the reframe's conceptual keystone).**
> **Promoted 2026-07-08 from optional overview to a keystone figure** for the family-druggability reframe
> ([`nr4a3-degrader-carT-and-family-druggability-framing.md`](./nr4a3-degrader-carT-and-family-druggability-framing.md)).
> It is now **data-backed at both poles**, not a pure schematic.
- (a) The axis: a horizontal "selectivity axis" from **NR4A3-selective** (engage the divergent handles;
  spare NR4A1/2) at one end to **pan-NR4A** (engage the conserved pocket residues 411/481/485; all three) at
  the other, with the AML **anti-target** (NR4A1+NR4A3) marked as a forbidden zone the matrix designs *away*
  from. One cryptic pocket, tuned by which residues the warhead engages.
- (b) **Both poles instantiated by real candidates from the SAME framework, retargeted** (the reframe's
  payoff): the selective pole → `denovo_401` (multi-snapshot-confirmed, decoy-null-cleared); the pan pole →
  the **conserved-core-designed campaign**, where ranking on residues 411/481/485 flips the docking census to
  pan-NR4A-dominant (**4/7 docked pan, 0 selective**) with the clean lead **`denovo_9`** (dG −7.69/−7.31/−7.40,
  within 0.4 kcal/mol across all three; 3/3 conserved-core; RDKit-clean). Show the census-flip selective↔pan as
  two mirrored bars. Asset: [`../modalities/nr4a3-pan-readout.json`](../modalities/nr4a3-pan-readout.json) ✅
  (repo; `pan_designed_campaign`). **Caption honesty:** docking-tier priors at both poles; no molecule
  synthesized. (The selective-run pan *by-catch* — `denovo_106`/`denovo_86`, liability-carrying — is the
  weaker prior version, optionally an SI panel.)
- (c) The two clinical destinations: selective → systemic NR4A3-driven cancers (EMC / AciCC / NR4A-sarcomas);
  pan → **ex-vivo, washable** CAR-T de-exhaustion (chemical NR4A triple-KO analogue; Chen 2019), with the
  degrader/E3 ternary cartoon and the "transient ex-vivo removes the systemic-toxicity bound" note.
- *Message:* a canonically "undruggable" receptor family reframed as a **programmable degradation target**
  spanning rare oncology and immunotherapy — the paper's strongest general claim (and its best pitch at JCIM).

## Tables

- **Table 1 — Calibration panel** (structure, type, max druggability, ligand-site druggability) from
  `nr4a3-calibration.json` ✅ + the reconciliation table.
- **Table 2 — Top matrix candidates**: label, ChEMBL id, dG into each opened pocket, margins, cell,
  engageable-handle + conserved contacts. From `nr4a3-matrix.json` ✅ (matrix run complete; via
  `report-matrix-aws.yml`).
- **Table 3 — Pre-registered gates and outcomes** (Gate 0/0b/1/2/3/4, pass/fail, with the Gate-0 *and
  Gate-1* disclosed deviations — Gate 1 met only in the weaker basin-breathing sense; **Gate 3 now
  release-confirmed as an induced-fit cavity**, no longer provisional) from `nr4a3-druggability-prereg.md` ✅.
- **Table 4 — De-novo candidates funneled to MM-GBSA, decoy bar, and multi-snapshot**: name, SMILES, QED,
  SAscore, engageable-handle contacts, docking cell, single-snapshot MM-GBSA NR4A3-margin, **above decoy null?
  (+13.1)**, **multi-snapshot mean ± SD**, verdict — spotlighting the decoy-calibrated foothold **`denovo_111`**
  and the multi-snapshot-confirmed lead **`denovo_401`** (and listing `denovo_15` only as the **retracted**
  single-snapshot artifact). From `nr4a3-denovo.json` + `nr4a3-denovo-mmgbsa*` + `nr4a3-decoy-mmgbsa` ✅ (S3, via
  `report-denovo-aws.yml` / `report-mmgbsa-aws.yml`). Caption: single-snapshot MM-GBSA is non-specific (decoy
  control); read decoy-calibrated + multi-snapshot, not raw margin; screening-grade.

## Production status — where each asset lives (2026-07-05)
Publication-readiness pass. **Legend:** ✅ repo = PNG committed under `research/modalities/`, regenerable now
(`python3 <script>`); 📦 S3 = already rendered, pull via the read-only `report-*-aws.yml` job (needs the SageMaker
account, not this repo's CI creds); ✍️ author = final structure render / journal-grade redraw (PyMOL/NGL), an
authors' production step per the note at the foot of this file.

| Display item | Status | Asset / generator |
|---|---|---|
| Fig 1a (pocket + handles render) | ✍️ author | AF-Q92570.pdb + `nr4a-selectivity.json` (repo) → PyMOL/NGL |
| Fig 1b (calibration bar) | 📦 S3 | `nr4a3-calibration.json` → bar; regenerable once JSON pulled |
| Fig 2a (F(Rg) profile) | ✅ repo | `nr4a3-metad-fes.png` / `nr4a3_metad_figure.py` |
| Fig 2b (druggability vs Rg) | 📦 S3 | `pocket_druggability.png` (S3) |
| Fig 2c (closed vs opened surface) | ✍️ author | `nr4a3-opened.pdb` (S3) → surface render |
| Fig 2d (release run: Rg trace + druggability dist) | 📦 S3 | `nr4a3-release/` + `nr4a3-release-pocket/` |
| Fig 3a (handles on opened pocket) | ✍️ author | `nr4a-selectivity.json` + `nr4a3-opened.pdb` → render |
| Fig 3b (per-handle facing fraction) | 📦 S3 | `handle_facing.png` (S3) |
| Fig 4b (family-wide matrix heatmap) | 📦 S3 | `nr4a3-matrix.png` (S3) |
| Fig 5b (generation quality scatter) | 📦 S3 | `nr4a3-denovo.png` (S3) |
| Fig 5c (decoy specificity control) | 📦 S3 | `nr4a3-decoy-mmgbsa` + `nr4a3-denovo-mmgbsa-dev` via `report-mmgbsa-aws.yml` |
| Fig 5d (multi-snapshot de-noising) | ✅ repo | `nr4a3-denoising.png` / `nr4a3_denoising_figure.py` |
| **Fig 5f (release-vs-metad frame-dependence)** | **✅ repo (NEW)** | `nr4a3-frame-decoynull.png` / `nr4a3_frame_decoynull_figure.py` |
| Fig 5e (lead 2D + pose) | ✍️ author | `nr4a3-denovo-v2` pose (S3) → RDKit 2D + pose render |
| Fig 6 (selectivity axis / two poles — keystone) | ✍️ author + ✅ repo data | `nr4a3-pan-readout.json` (repo, both poles) + `denovo_401`/`denovo_106`/`denovo_86` poses → axis schematic w/ real candidates |
| Table 1 (calibration panel) | 📦 S3 | `nr4a3-calibration.json` |
| Table 2 (top matrix candidates) | 📦 S3 | `nr4a3-matrix.json` via `report-matrix-aws.yml` |
| Table 3 (pre-registered gates) | ✅ repo | SI §2 (assembled from the reconciliation doc) |
| Table 4 (de-novo candidates + decoy bar + multi-snapshot) | 📦 S3 | `nr4a3-denovo*` / `nr4a3-decoy-mmgbsa` via `report-*-aws.yml` |

**Summary:** the two committed-data chart panels that read inline/committed values (Fig 2a, Fig 5d) and the new
frame-dependence panel (Fig 5f) render now from `research/modalities/`. The remaining chart panels are already
rendered in S3 (pull via `report-*-aws.yml`); the structure renders (Figs 1a, 2c, 3a, 5e) are the authors'
journal-grade production step. No panel is blocked on the running FEP.

## Generation notes
- Plots that read committed JSON (Figs 1b, 3b; Tables 1,3) can render now; Figs 2,4,5 + Tables 2,4 read S3
  outputs that now **exist** (release, matrix, MM-GBSA, de-novo) — pull them via the `report-*-aws.yml`
  read-only jobs (matrix / mmgbsa / denovo) or add a `render-figures` step that fetches the JSON/PNG.
- Keep every panel caption's claim within its data weight: AF2 = model; metad = biased MD ensemble;
  unbiased release = thermally-real but induced-fit (~24 % druggable); docking dG = triage prior (not
  affinity); **MM-GBSA = run, but single-snapshot/no-entropy → read the verdict/direction, not the
  kcal/mol**; FEP = the defensible affinity tier, **not yet run**.
- **Before submission:** collate the `denovo_401` 2D depiction + its pose (Fig 5e) and Table 4 from the
  `report-denovo-aws.yml` output; the lead SMILES is `COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`
  (`denovo_15`, SMILES `C=C(CC1=CC=C(NC(=O)O)C1)[C@H]1C=C2C(=NC1)OC[C@H](C)[C@@H]2C`, appears only as the
  retracted artifact). Also pull the decoy-control (Fig 5c) and multi-snapshot (Fig 5d) panels.
