# Session handoff — NR4A3 degrader: matrix done, MM-GBSA verdict pending (2026-06-28)

**Paste this into a fresh session to resume.** Blocker for ending the last session: the GitHub MCP token
expired (re-auth needed). The AWS SageMaker job keeps running regardless — its result lands in S3.

## TL;DR — do this first
1. **Confirm GitHub Actions access** (the previous session died on an expired GitHub MCP token).
2. **Read the MM-GBSA result of run 7** (the OpenCL-fixed attempt #4): dispatch **`report-mmgbsa-aws.yml`**
   on `main` (inputs `region=us-east-2`, `output_prefix=nr4a3-mmgbsa`) and read its job log. It prints the
   verdict census, the ranked table, and — if it failed again — the distinct per-ligand `_errors`.
   - The underlying run was **`mmgbsa-aws.yml` run id 28330096446** (dispatched 2026-06-28 ~17:23 UTC,
     commit `cb3d95c`). Output → `s3://sagemaker-us-east-2-646605541856/nr4a3-mmgbsa/nr4a3-mmgbsa.json`.
   - Also grep the run-7 job log for the line **`[mmgbsa] OpenMM platform:`** — expect `OpenCL` (CUDA fails
     on this instance, see below).
3. **If run 7 produced real ΔG** (verdict census has confirmed_selective / reversed / weakened, not all
   `incomplete`): report the verdict — does the docking-level NR4A3-selectivity survive? In particular does
   **cytosporone B** come back **`reversed`** (expected: it's a known NR4A1 agonist). Then write the result
   into `nr4a3-matrix-result.md` + `nr4a3-degrader-next-steps.md` and this is DONE.
4. **If run 7 is still all-`incomplete`**: read the distinct `_errors` from the report, fix `mmgbsa_energy.py`,
   and — per the standing rule below — **ask before re-running** (cost popup).

## 🛑 STANDING RULE (trimcrae, 2026-06-28): ask before ANY new GPU run
Before dispatching anything that starts a `ml.g5.*`/GPU SageMaker instance (mmgbsa, metad, matrix, FEP,
release, ternary, warhead, calibration), present an **`AskUserQuestion` decision pop-up** (so the user gets
a notification) with a **cost estimate + payoff**, and let them choose. Read-only/CPU GitHub-Actions jobs
(`verify-aws`, `report-*`, `sagemaker-stop-aws`) are exempt. Rough cost (ml.g5.xlarge, us-east-2, ~$1.4/h,
billed on actual runtime): ~25 min job ≈ **$0.5–0.7**; 30 ns metad (~9–10 h) ≈ **$13–15**; selectivity FEP
(~1–3 weeks serial) ≈ **hundreds of $**. Full rule is in `nr4a3-degrader-next-steps.md` → infra gotchas.

## Git state
- Branch **`claude/nr4a3-selectivity-matrix-r2b323`**, and **`main`**, are in sync at **`cb3d95c`** (all work
  committed + pushed). Develop on that branch; merge to `main` as you go (user-authorized).
- Quota = **1 concurrent ml.g5.xlarge** — keep runs serial. After a `sagemaker-stop`, the slot takes
  **~15+ min** to free; a too-soon dispatch fails fast with `ResourceLimitExceeded` (that costs $0 — no
  instance starts).

## What's DONE this session
- **Family-wide selectivity MATRIX — COMPLETE** (`gpu-matrix-aws.yml` run 28319737517). Fig 4 deliverable.
  State-matched opened conformers docked: NR4A3 frame 300 (druggability 0.931), NR4A1 frame 524 (0.981),
  NR4A2 frame 125 (0.938). Output `s3://…/nr4a3-matrix/nr4a3-matrix.json` (+ opened PDBs, docked SDFs, Fig 4
  heatmap PNG). Re-read with `report-matrix-aws.yml`. **Result + FEP go/no-go memo: `nr4a3-matrix-result.md`.**
  - **Census (13 candidates):** NR4A3-only 4 · pan-NR4A 3 · none 3 · NR4A2+NR4A3 1 · NR4A2-only 1 ·
    NR4A1+NR4A2 1 · **NR4A1+NR4A3 anti-target = 0 (empty — nothing to design away from).**
  - **NR4A3-selective lead:** cytosporone B (dG3 −7.08, margins +1.42/+1.16). **Caveat: cytosporone B is a
    canonical NR4A1/Nur77 agonist (Zhan et al. Nat Chem Biol 2008)** — docking calling it NR4A3-selective is
    likely an artefact; 6/9 cell calls sit within docking noise. This is exactly what MM-GBSA is meant to test.
  - **pan-NR4A leads:** celastrol, CHEMBL1873475. (These are tool/repurposing compounds, not designed warheads.)
- **MM-GBSA endpoint-rescoring pipeline — BUILT + DEBUGGED** (single-snapshot 1-trajectory MM-GBSA; enthalpy
  + GBn2 implicit solvent; **no entropy, no ensemble average** — triage, NOT affinity). Reuses the matrix's
  docked poses (no re-dock, no MD). Files: `mmgbsa_select.py` (10 pure tests) · `mmgbsa_energy.py` (OpenMM +
  OpenFF/GAFF-2.11 + PDBFixer) · `nr4a3_mmgbsa.py` (driver; verdict = confirmed_selective / reversed /
  weakened / rescued vs the docking margin) · `report_mmgbsa.py` + `report-mmgbsa-aws.yml` (read-only S3
  reporter, surfaces verdict table + distinct per-ligand errors) · `sagemaker_src/entry_mmgbsa.py` ·
  `nr4a3_mmgbsa_sagemaker.py` · `.github/workflows/mmgbsa-aws.yml`.
  - **Four systematic bugs fixed across runs 1–4, each from the run's own error output:** (1) `nonbondedMethod`
    must go in `nonperiodic_forcefield_kwargs`, not `forcefield_kwargs`; (2) strip the periodic box (CRYST1
    from the solvated metad PDBs) so GB implicit solvent is non-periodic; (3) the CPU platform was the runtime
    bottleneck (a CPU run hit ~2h and was stopped) → use the GPU; (4) **CUDA fails on this instance with
    `CUDA_ERROR_UNSUPPORTED_PTX_VERSION`** (conda OpenMM built against newer CUDA than the A10G driver), so the
    platform helper now **validates** each platform with a tiny energy eval and falls back **CUDA → OpenCL →
    CPU** (commit `cb3d95c`). **Run 7 is the first run with this OpenCL fix — its result is what's pending.**
  - Tunables (env vars on the job): `MMGBSA_MIN_ITERS` (default 250). Output also includes `sysgen_cache.json`.

## Next tier after the MM-GBSA verdict (NOT started)
- **Selectivity FEP — DEFERRED** (the program's dominant GPU cost, ~1–3 weeks serial ≈ hundreds of $). Gate
  behind (i) the unbiased **release run** (`gpu-release-aws.yml`) confirming the opened pocket is metastable
  and (ii) a *bona fide* selective candidate worth the spend (de-novo design, matrix step 3). Rationale +
  go/no-go in `nr4a3-matrix-result.md`. Always flag FEP cost in the decision pop-up before launching.

## Key references / source of truth
- Program state + exact run instructions: **`research/modalities/nr4a3-degrader-next-steps.md`**
  (read its "Infra gotchas" section first).
- Matrix result + FEP go/no-go: **`research/modalities/nr4a3-matrix-result.md`**.
- S3 bucket: **`sagemaker-us-east-2-646605541856`** (region us-east-2). Prefixes: `nr4a3-metad`,
  `nr4a1-metad`, `nr4a2-metad`, `nr4a3-matrix`, `nr4a3-mmgbsa`.
- Medical-integrity rules (never fabricate data/citations) in `CLAUDE.md` / `AGENTS.md` apply.
