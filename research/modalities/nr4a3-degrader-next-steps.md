# NR4A3 degrader — in-silico program state & how to run the warhead next (handoff)

**Single source of truth for resuming the degrader work from a fresh session.** Read this + the
manuscript ([`../manuscripts/nr4a3-degrader-paper.md`](../manuscripts/nr4a3-degrader-paper.md)) and the
pre-registration ([`nr4a3-druggability-prereg.md`](./nr4a3-druggability-prereg.md)) before launching
anything. Last updated 2026-06-26.

## TL;DR
The in-silico **druggability case is complete and positive** — Gates 0–3 pass. One **registered Gate-2
sub-check is still open**: confirming the 7 selectivity handles stay **pocket-facing** in the opened,
druggable frames (not splayed). That analysis is now **built and unit-tested**
(`nr4a3_handle_facing.py` + `handle_facing_geom.py`, dispatched by `handle-facing-aws.yml`) and is the
**cheap precondition to run before the warhead screen** — it validates the warhead's own handle-contact
scoring. After it, the **selective-warhead screen** (`gpu-warhead-aws.yml`) is **built and idle**, waiting
only for a go-ahead. Nothing is running; no GPU is active.

## Where the science landed (all committed to `main`)
| Result | Value | Source |
|--------|-------|--------|
| Static orthosteric druggability (AF2) | **0.495** (Pocket 5, res 406–534) | `nr4a3-structure-assessment.json` |
| Calibrated druggable threshold **D\*** | **0.53** (validated drug-bound NR band 0.53–0.68) | `gpu-calibration-aws.yml` → `nr4a3-calibration.json` |
| Model over-call? | **No** — NR4A2 model 0.801 ≈ 1OVL crystal 0.864; 0.495 is conservative | calibration |
| **Gate 2** opened-pocket druggability (30 ns) | **0.931** max; PASS | `gpu-mdpocket-aws.yml` on `nr4a3-metad` |
| **Gate 3** energetic accessibility | **PASS** — druggable (0.80) at CV Rg 0.717 nm for **0.76 kcal/mol** (the ~38 kcal/mol was the cost to the most-OPEN *edge*, not a druggable state) | F(Rg)-vs-druggability re-analysis |
| Selectivity handles (NR4A3 vs NR4A1/2) | **7**: L406, T407, T410, R412, I484, I531, L534 | `nr4a-selectivity.json` |

Full reconciliation + gate scoring + the disclosed Gate-0 deviation:
[`nr4a3-druggability-reconciliation.md`](./nr4a3-druggability-reconciliation.md).

**Indications (the degrader must be NR4A3-SELECTIVE):** lead = EMC + acinic cell carcinoma (AciCC,
NR4A3-overexpression-driven) + other NR4A3-fusion sarcomas. Immuno-oncology needs *pan*-NR4A (triple
degradation) → contingency only, NOT motivation. AML/HCC contraindication. Detail:
[`../manuscripts/nr4a3-degrader-broader-indications.md`](../manuscripts/nr4a3-degrader-broader-indications.md).

## STEP 0 (recommended first) — handle-facing confirmation (cheap, closes the registered Gate-2 clause)
**Pipeline (built, unit-tested, committed):** `nr4a3_handle_facing.py` + `handle_facing_geom.py` (pure,
8 passing tests in `tests/test_handle_facing_geom.py`) + `sagemaker_src/entry_handle_facing.py` +
`nr4a3_handle_facing_sagemaker.py` + `.github/workflows/handle-facing-aws.yml`.

**Why first:** the warhead screen ranks candidates partly by **handle-contact count**; if the 7 handles
do not stay pocket-facing in the opened/druggable frames, that score is meaningless. This is also the
unmet second clause of the pre-registered Gate-2 pass condition. It reuses the existing 30 ns trajectory
(no new GPU run), runs fpocket + pure geometry over ~25 frames (CPU, well under an hour, `wait=True` safe).

**To launch:** dispatch **`handle-facing-aws.yml`** on `main` (defaults fine): `input_prefix=nr4a3-metad`,
`dcd_name=nr4a3-lbd-metad.dcd`, `output_prefix=nr4a3-handle-facing`, `region=us-east-2`, `git_ref=main`.

**What it does / how to read it:** for sampled frames it finds the orthosteric pocket (same fpocket
mapping as `nr4a3_mdpocket.py`) and its druggability, takes the cavity centroid from that pocket's lining
CA atoms, and for each handle decides "pocket-facing" (CA→side-chain centroid has a positive component
along CA→cavity). Output `nr4a3-handle-facing/handle_facing_summary.json` reports, per handle, the
fraction of druggable frames it faces in, plus a **verdict**: CONFIRMED if a majority of druggable
(fpocket ≥ D\*=0.53) frames keep ≥ 4 of 7 handles facing in. **CONFIRMED → proceed to the warhead screen;
NOT CONFIRMED → the handle-based selectivity spec needs rework before docking (and Gate 2's second clause
fails, weakening the route).** Then update paper §2.2/§5, the reconciliation Gate-2 row, and this file.

## THE NEXT STEP (after Step 0) — run the selective-warhead screen
**Pipeline (built, tested-compile, committed):** `nr4a3_warhead.py` + `sagemaker_src/entry_warhead.py`
+ `nr4a3_warhead_sagemaker.py` + `.github/workflows/gpu-warhead-aws.yml`.

**To launch (from a session with GitHub Actions access):** dispatch **`gpu-warhead-aws.yml`** on `main`
(defaults are fine): `input_prefix=nr4a3-metad`, `output_prefix=nr4a3-warhead`, `region=us-east-2`,
`git_ref=main`. It is CPU work (< 6 h), so the GitHub wrapper's `wait=True` is safe.

**What it does:** (1) extracts the most-druggable OPENED conformer from the 30 ns trajectory
(`s3://<bucket>/nr4a3-metad/nr4a3-lbd-metad.dcd`) — designs against the open 0.93 pocket, not the
collapsed static one; (2) maps Pocket-5 onto NR4A1 (P22736) / NR4A2 (P43354) by BLOSUM62 alignment to
box the homologous paralogue pockets; (3) docks candidate ligands (real ChEMBL NR4A actives via
`nr4a3_dock` helpers) into NR4A3-opened + NR4A1 + NR4A2 with smina; (4) scores per candidate:
`dG_NR4A3`, **selectivity margin** = min(dG_NR4A1, dG_NR4A2) − dG_NR4A3 (more positive = more
NR4A3-selective), and **handle-contact count**. Output → `s3://<bucket>/nr4a3-warhead/nr4a3-warhead.json`
(+ opened-conformer PDB + pose SDFs).

**How to read it:** rank by selectivity margin → NR4A3 potency → handle engagement. A good warhead lead
binds NR4A3-opened well, has a positive selectivity margin vs both paralogues, and contacts several of
the 7 handles. Remember: docking = screening prior, NOT affinity; this nominates chemotypes, not a lead.

**After the screen:**
1. **De-novo generative design** — `nr4a3_warhead.py::generate_denovo()` is a primed stub. Wire a
   structure-based generative model (DiffSBDD / Pocket2Mol / TargetDiff) conditioned on the opened
   conformer + GPU, set `DENOVO_MODEL`, to generate novel selective scaffolds (the screen only docks
   known matter).
2. **Ternary complex** — once a warhead SMILES exists, run the NR4A3–PROTAC–E3 ternary model
   (`nr4a3_ternary.py` / `gpu-ternary-aws.yml`) to score degradable-lysine geometry.
3. **Handle-facing confirmation** — now pulled forward to **Step 0 above** (run it *before* the warhead
   screen, since the screen's handle-contact score depends on it).

## Infra gotchas a fresh session MUST know
- **GitHub 6 h job cap:** the metad submitter uses `wait=True`, so a **>6 h** SageMaker run gets its
  GitHub *wrapper* cancelled at 6 h — but the SageMaker job **survives and finishes on AWS** (the 30 ns
  did exactly this; confirm via S3 / a follow-on analysis, not the GitHub status). **OPEN FIX:** harden
  `nr4a3_metad_sagemaker.py` to resume-chained segments (<6 h each, via the checkpoint/restart) or
  fire-and-forget. Warhead/analysis/calibration jobs are < 6 h, so unaffected.
- **Stopping GPU:** cancelling a GitHub run does NOT stop the SageMaker job. Use **`sagemaker-stop-aws.yml`**
  (`job_prefix=<base-name>`) which calls `StopProcessingJob`.
- **S3 layout (`s3://<default-bucket>/...`):** `nr4a3-metad` = 30 ns outputs (trajectory, `fes.dat`,
  HILLS/COLVAR, and the checkpoint/restart set `metad_system.xml` / `metad_checkpoint.chk` /
  `metad_state.xml` / `metad_manifest.json`); `nr4a3-calibration`; `nr4a3-metad-pocket-30ns` /
  `nr4a3-metad-fes2` = analyses; `nr4a3-handle-facing` = handle-facing output (after Step 0);
  `nr4a3-warhead` = warhead output (after you run it).
- **Extending the metad** (if ever needed for a converged F(Rg)): `gpu-metad-aws.yml` with
  `resume_from=auto` continues from the saved checkpoint — but only if CV/metad params are unchanged
  (the manifest guard enforces this).
- **Known-broken (abandoned):** `nr4a3_md_release.py` (unbiased release run) has a startup bug and
  failed early; it was only orthogonal Gate-3 confirmation and is **not needed** (Gate 3 already
  resolved). Fix only if that confirmation is later wanted.

## Open items (not blockers for the warhead)
- [ ] Harden the metad submitter against the 6 h cap (segments / fire-and-forget).
- [x] Opened-frame handle-facing confirmation — analysis **built + unit-tested** (`nr4a3_handle_facing.py`);
      **still needs dispatch** (`handle-facing-aws.yml`) + writing the result back into paper §2.2/§5 and
      the reconciliation Gate-2 row.
- [ ] (optional) Fix `nr4a3_md_release.py` for the orthogonal metastability confirmation.
- [ ] (optional) Converged longer metad to put a precise number on the full free-energy profile.
- [ ] Verify all "[…to confirm]" reference locators before manuscript submission (medical integrity).
