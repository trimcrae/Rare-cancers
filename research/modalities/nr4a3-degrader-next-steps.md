# NR4A3 degrader — in-silico program state & how to run the warhead next (handoff)

**Single source of truth for resuming the degrader work from a fresh session.** Read this + the
manuscript ([`../manuscripts/nr4a3-degrader-paper.md`](../manuscripts/nr4a3-degrader-paper.md)) and the
pre-registration ([`nr4a3-druggability-prereg.md`](./nr4a3-druggability-prereg.md)) before launching
anything. Last updated 2026-06-26.

## TL;DR
Druggability case complete (Gates 0–3 pass, incl. the Gate-2 handle-facing sub-check, **CONFIRMED**
2026-06-26, run 28249776934: mean **5.0/7** handles pocket-facing; engageable set **five — L406, T410,
I484, I531, L534**; T407/R412 splay out). The **warhead screen ran** (run 28252182123): NR4A3-favoured
chemotypes, top margin ~+1.7 kcal/mol (e.g. CHEMBL1873475), 4/5 engageable handles — but these margins are
**confounded triage** (opened NR4A3 vs *static* paralogues; see below).

**STRATEGY (2026-06-26, user-directed): build a family-wide selectivity matrix.** Run the *same* 30 ns
metad on **NR4A1 + NR4A2** → state-matched opened-pocket ensembles for all three → dock one library into
each → per-candidate **selectivity fingerprint** (NR4A3-only / pan-NR4A / anti-target NR4A1+NR4A3). This
is simultaneously the rigor fix (kills the opened-vs-static confound) and the scope expansion (programmable
selectivity). **IN FLIGHT now:** `gpu-metad-aws.yml target=NR4A1` (run **28256669839**) and `target=NR4A2`
(run **28256671172**), 30 ns each, ml.g5.xlarge (~$18–23 total). Verify completion via S3
(`nr4a1-metad` / `nr4a2-metad`), not GitHub status (6 h-cap wrapper issue applies).

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

**Indications = a programmable matrix (see paper §3):** **lead** = NR4A3-selective → EMC + AciCC
(NR4A3-overexpression-driven) + other NR4A3-fusion sarcomas. **Second design mode** = *pan*-NR4A (triple
degradation) for ex-vivo/transient immuno-oncology (T-cell exhaustion; Chen 2019) — a distinct molecule,
not a contingency. **Anti-target** = NR4A1+NR4A3 (combined loss → AML; design *away* from). HCC/breast
also tumour-suppressive. Detail:
[`../manuscripts/nr4a3-degrader-broader-indications.md`](../manuscripts/nr4a3-degrader-broader-indications.md).

## STEP 0 — handle-facing confirmation — ✅ DONE (CONFIRMED 2026-06-26, run 28249776934)
**Result:** druggable frames 8/25 sampled (fpocket ≥ D\*=0.53); **mean 5.0/7 handles pocket-facing**;
87.5 % of druggable frames keep ≥4 facing → registered Gate-2 second clause **CONFIRMED**. Per-handle
fraction-facing in druggable frames: **L406 1.0, I531 1.0, L534 1.0, T410 0.875, I484 0.875** (the five
engageable handles) vs **T407 0.0, R412 0.25** (splay outward). Output:
`s3://sagemaker-us-east-2-646605541856/nr4a3-handle-facing/handle_facing_summary.json` (+ `handle_facing.png`).
Implication for the warhead screen: the realistic selectivity-handle set is five, not seven.

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

**Warhead screen — DONE (run 28252182123, 2026-06-26).** Top NR4A3-favoured: CHEMBL1873475
(dG_NR4A3 −8.34, margin +1.7, 4/5 handles), amodiaquine (−7.63, +1.53). **Caveat:** a first run silently
voided selectivity (paralogue docks failed on a residue-renumbering bug — the opened conformer is
renumbered 1..254, not the AF2 406..534); fixed by passing the opened conformer's actual resSeqs (`box_res`)
into `map_pocket_to_paralogue`, plus fail-loud guards (`selectivity_evaluated`, `paralogue_pocket_residues_mapped`).
These margins are still **opened-NR4A3-vs-STATIC-paralogue = confounded upper bounds** on selectivity —
the family metad (in flight) is the fix.

**FAMILY-WIDE MATRIX — build steps once `nr4a1-metad` + `nr4a2-metad` land in S3:**
1. **State-matched warhead matrix** — extend `nr4a3_warhead.py` to dock the library into each paralogue's
   OWN opened conformer (extracted from `nr4a1-metad`/`nr4a2-metad` like NR4A3's), not the static AF model.
   Output a per-candidate selectivity *fingerprint* across the three → partition into NR4A3-only / pan /
   NR4A1+NR4A3 anti-target cells. Also add a **conserved-residue contact score** + pan ranking, and **dedup**
   the candidate list (CHEMBL682 duplicated in run 28252182123).
   - **BUILT + LAUNCH-READY (2026-06-26):** classifier `selectivity_fingerprint.py` (7 tests) + driver
     `nr4a3_matrix.py` (mounts all three `*-metad` prefixes, extracts each opened conformer, docks the
     deduped library into all three, classifies via `classify()`, scores divergent-handle + conserved-CV
     contacts) + `sagemaker_src/entry_matrix.py` + `nr4a3_matrix_sagemaker.py` + `.github/workflows/gpu-matrix-aws.yml`.
     **To launch once all three `*-metad` ensembles are in S3:** dispatch `gpu-matrix-aws.yml` on `main`
     (defaults fine). Output `s3://<bucket>/nr4a3-matrix/nr4a3-matrix.json` = per-candidate cell + census +
     leads (nr4a3_selective / pan_nr4a / anti_targets).
2. **Endpoint free energy (the defensible margin)** — MM-GBSA + per-residue decomposition on the top cell
   leads in all three opened ensembles; selectivity FEP on the lead 1–3. Docking stays triage only.
3. **De-novo generative design** — `nr4a3_warhead.py::generate_denovo()` stub: wire DiffSBDD/Pocket2Mol,
   two campaigns (divergent-handle-conditioned = selective; conserved-conditioned = pan) to fill empty cells.
4. **Ternary complex per paralogue** — once a warhead SMILES exists, `nr4a3_ternary.py` / `gpu-ternary-aws.yml`
   for degradable-lysine geometry (degradation selectivity ≠ warhead-binding selectivity).
5. **Handle-facing confirmation** — done (Step 0); rerun on each paralogue's opened ensemble for symmetry.

## Infra gotchas a fresh session MUST know
- **metad is now multi-target:** `gpu-metad-aws.yml` takes `target=NR4A3|NR4A1|NR4A2` (+ optional
  `output_prefix`, default `<target>-metad`). Paralogue LBD trim + Pocket-5 CV residues are mapped to the
  NR4A3 reference by BLOSUM62 alignment at runtime (fail-loud + audit log + the initial-Rg pre-flight).
  One pipeline builds the whole family for the matrix.
- **GitHub 6 h job cap:** the metad submitter uses `wait=True`, so a **>6 h** SageMaker run gets its
  GitHub *wrapper* cancelled at 6 h — but the SageMaker job **survives and finishes on AWS** (the 30 ns
  did exactly this; confirm via S3 / a follow-on analysis, not the GitHub status). **OPEN FIX:** harden
  `nr4a3_metad_sagemaker.py` to resume-chained segments (<6 h each, via the checkpoint/restart) or
  fire-and-forget. Warhead/analysis/calibration jobs are < 6 h, so unaffected. **The NR4A1/NR4A2 runs
  in flight will hit this** — confirm via S3 `nr4a1-metad`/`nr4a2-metad`, not GitHub.
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
- **Release run (`nr4a3_md_release.py`) — startup crash FIXED 2026-06-26, pending a GPU validation run.**
  It was parked after failing early; the identifiable crash was an AF-model-fetch regression
  (`M._fetch_af_model()` signature) — now fixed + pinned to the NR4A3 reference CV/model (robust to the
  metad TARGET refactor), compiles + imports clean. It's orthogonal Gate-3 confirmation and **not needed**
  (Gate 3 already resolved), so it's queued for a *free* GPU slot behind the family metad, not a priority —
  but it's launch-ready (`gpu-release-aws.yml`). NOTE: not yet validated on GPU, so treat as "should run"
  until a clean run confirms it.

## Open items (not blockers for the warhead)
- [ ] Harden the metad submitter against the 6 h cap (segments / fire-and-forget).
- [x] Opened-frame handle-facing confirmation — **DONE** (CONFIRMED 2026-06-26, run 28249776934; mean
      5.0/7 handles facing, T407/R412 the exceptions). Result written into paper §2.2/§5 and the
      reconciliation Gate-2/3 rows.
- [x] Fix `nr4a3_md_release.py` startup crash (AF-fetch regression) — DONE; pending a GPU validation run
      for the orthogonal metastability confirmation (optional, not a blocker).
- [ ] (optional) Converged longer metad to put a precise number on the full free-energy profile.
- [x] Verify "[…to confirm]" reference locators — DONE 2026-06-26 via `verify-refs.yml` §7 (Crossref +
      Europe PMC): resolved PMC4535767 (Lanig, PLoS ONE 2015), Munoz-Tello (J Med Chem 2020), and
      corrected the NR4A3–MYB paper to Lee et al. 2020 (Cancers), not Haller. DOIs added to paper +
      reconciliation + broader-indications. Remaining: a few volume/page numbers from the primary record.
