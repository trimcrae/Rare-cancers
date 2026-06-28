# NR4A3 degrader — in-silico program state & how to run the warhead next (handoff)

**Single source of truth for resuming the degrader work from a fresh session.** Read this + the
manuscript ([`../manuscripts/nr4a3-degrader-paper.md`](../manuscripts/nr4a3-degrader-paper.md)) and the
pre-registration ([`nr4a3-druggability-prereg.md`](./nr4a3-druggability-prereg.md)) before launching
anything. Last updated 2026-06-26.

## TL;DR
Druggability case is a **feasibility result, stated honestly** (see the red-team:
[`../manuscripts/nr4a3-degrader-paper-redteam.md`](../manuscripts/nr4a3-degrader-paper-redteam.md)).
**Gate 0/0b** pass; **Gate 2** (opened-pocket druggable + handle-facing) passes; **Gate 1** is met only in
the weaker *basin-breathing* sense (F(Rg) is **monotonic — no separate opened minimum**, so not the
pre-registered "minimum/shoulder, not just biased excursions"); **Gate 3** (energetic accessibility) is
**provisional** — the ~0.76 kcal/mol-to-druggable is read off the same under-converged biased F(Rg), and
the independent metastability test (unbiased **release run**, queued) is what would close it. So do **not**
restate "Gates 0–3 pass" without these qualifications. The 0.931/0.751 opened-frame druggability is the
**orthosteric Pocket-5** metric (commensurate with the static 0.495) but is a **biased-MD-frame peak over
frames** — report it as the fraction of opened frames ≥ D\*=0.53 (≥5% pre-reg bar, met) with 0.931 as the
peak, and not as a like-for-like beat of the *static* drug-bound band. (fpocket itself is standard and the
§2.1 panel already anchors it, so no bespoke negative control is needed.) Gate-2 handle-facing **CONFIRMED**
2026-06-26 (run 28249776934): mean **5.0/7** pocket-facing; engageable set **five — L406, T410, I484, I531,
L534**; T407/R412 splay out. *Selectivity asymmetry:* engageable **divergent** handles are **5 vs NR4A1 but
only 4 vs NR4A2** (I531 conserved with NR4A2). The **warhead screen ran** (run 28252182123): NR4A3-favoured
chemotypes, top margin ~+1.7 kcal/mol (e.g. CHEMBL1873475), 4/5 engageable handles — but these margins are
**confounded triage** (opened NR4A3 vs *static* paralogues; see below).

**STRATEGY (2026-06-26, user-directed): build a family-wide selectivity matrix.** Run the *same* 30 ns
metad on **NR4A1 + NR4A2** → state-matched opened-pocket ensembles for all three → dock one library into
each → per-candidate **selectivity fingerprint** (NR4A3-only / pan-NR4A / anti-target NR4A1+NR4A3). This
is simultaneously the rigor fix (kills the opened-vs-static confound) and the scope expansion (programmable
selectivity). **STATUS (2026-06-28):**
- **NR4A1 — DONE.** `nr4a1-metad` ensemble landed in S3 (full ~732 MB trajectory, `COMPLETE-SET: YES`,
  SageMaker job `Completed`). The first NR4A1 attempt was wasted by the 8 h `MaxRuntime` truncation; the
  rerun under the 20 h cap + continuous checkpointing completed cleanly.
- **NR4A2 — relaunched, expected complete.** Run **28303055273** (launched 2026-06-27 21:59,
  `target=NR4A2`, `MAX_RUNTIME=72000`, continuous checkpointing), confirmed past pre-flight; by elapsed
  time the SageMaker job has finished and its ensemble is persisted at `nr4a2-metad/`. Confirm via
  **`verify-aws.yml`** (`COMPLETE-SET: YES` + job `Completed`) before the matrix dispatch.
- **NEXT ACTION (the one pending step): dispatch `gpu-matrix-aws.yml` on `main`** (defaults fine) once
  `nr4a2-metad` is confirmed — this is the central deliverable (per-candidate selectivity fingerprint +
  Fig 4 heatmap). As of 2026-06-28 this is **blocked only on GitHub Actions access** (the GitHub MCP
  server was disconnected); all code is committed/tested and git-over-HTTPS works, so the launch is
  immediate once Actions dispatch is available again. Verify completion via S3 (`nr4a1-metad` /
  `nr4a2-metad` / `nr4a3-matrix`), not GitHub status (6 h-cap wrapper issue applies).

## Where the science landed (all committed to `main`)
| Result | Value | Source |
|--------|-------|--------|
| Static orthosteric druggability (AF2) | **0.495** (Pocket 5, res 406–534) | `nr4a3-structure-assessment.json` |
| Calibrated druggable threshold **D\*** | **0.53** (validated drug-bound NR band 0.53–0.68) | `gpu-calibration-aws.yml` → `nr4a3-calibration.json` |
| Model over-call? | **No** — NR4A2 model 0.801 ≈ 1OVL crystal 0.864; 0.495 is conservative | calibration |
| **Gate 1** cryptic *opening* (distinct opened basin) | **Weaker basin-breathing pass** — F(Rg) monotonic, no opened minimum/shoulder; not the literal pre-reg condition | `fes.dat` (sum_hills) |
| **Gate 2** opened-pocket druggability (30 ns) | **0.931** (orthosteric Pocket-5, *peak* over frames; report fraction ≥ D\* — ≥5% bar met; biased-MD); PASS | `gpu-mdpocket-aws.yml` on `nr4a3-metad` |
| **Gate 3** energetic accessibility | **PROVISIONAL** — druggable (0.80) at CV Rg 0.717 nm for **0.76 kcal/mol** read off the same under-converged biased F(Rg) (the ~38 kcal/mol was the cost to the most-OPEN *edge*); release run is the independent confirmation | F(Rg)-vs-druggability re-analysis |
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
- **SageMaker MaxRuntime must fit the run (incident 2026-06-27):** a 30 ns metad needs **~9-10 h of MD**
  at NR4A LBD speeds (~80 ns/day). The old **8 h** `MaxRuntime` default **killed NR4A2 (and a first NR4A1)
  before the script finished + uploaded → EMPTY S3 prefix, run wasted** (SageMaker uploads
  `ProcessingOutput` only on clean completion in EndOfJob mode). **Fixed:** default `MaxRuntime` raised to
  **20 h** (it's a CEILING — billed on actual runtime, so headroom is free), AND the restart set now
  streams to S3 in **`S3UploadMode="Continuous"`** (the metad writes checkpoint/HILLS/DCD/system/state to
  `OUTPUT_DIR`), so an interrupted run is **resumable from S3** (`resume_from=auto`) — verified live
  (checkpoint+HILLS+system+solvated in `nr4a1-metad/` mid-run). **Always confirm a run via S3
  (`verify-aws.yml`), not GitHub.**
- **GitHub 6 h job cap (separate, harmless):** the metad submitter uses `wait=True`, so the GitHub
  *wrapper* is cancelled at 6 h — but the SageMaker job **survives and finishes on AWS** to its MaxRuntime.
  Confirm via S3, not GitHub status. (Resume-chained <6 h segments are now possible via the continuous
  checkpoint set, if ever wanted; not needed with the 20 h ceiling.)
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
  - **2026-06-26 dispatch BLOCKED on GPU quota.** A dispatch (run 28269479539) failed in ~36 s with
    `ResourceLimitExceeded`: the account's **ml.g5.xlarge processing-job quota is 1 instance and it was
    already in use** (the in-flight family metad almost certainly holds the slot). Not a code bug — pure
    capacity contention. Re-dispatch once the slot frees, or raise the quota, or stop the occupant
    (`sagemaker-stop-aws.yml`). **GPU runs for the degrader are being driven from a separate thread as of
    2026-06-26**, so don't double-dispatch from here.

## Open items (not blockers for the warhead)
- [ ] **Report 0.931 as a distribution, not just a max (red-team F2).** The headline is the peak over 600
      frames (extreme value). In the writeup/figures lead with the *fraction of opened frames ≥ D\*=0.53*
      (pre-registered ≥5% bar, met) + the median of the druggable cluster, with 0.931 as the peak. (A
      bespoke fpocket negative control is **not** needed — fpocket druggability is standard and the §2.1
      panel, incl. the occluded 1OVL, already anchors it; the biased-vs-physical question is the release
      run's job, below.)
- [ ] **Release run = the Gate-3/Gate-1 closer.** Already queued (`gpu-release-aws.yml`); prioritize it,
      since it is now the gating evidence for "metastable druggable sub-state" vs "bias-induced strain."
- [x] Harden the metad submitter against interruption — DONE 2026-06-27: 20 h MaxRuntime ceiling +
      continuous S3 checkpoint upload (resumable). The 6 h GitHub-wrapper cancellation is now harmless.
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
