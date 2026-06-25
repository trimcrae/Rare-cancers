# Metadynamics methods & reproducibility appendix (NR4A3 LBD cryptic-pocket opening)

Reproducibility note for the manuscript appendix. Everything here is enacted by code in this
repository — no step is manual. Software versions are pinned by the SageMaker job's conda recipe.

## Objective

Test whether the borderline-druggable orthosteric pocket of the NR4A3 ligand-binding domain (LBD)
— fpocket **Pocket 5**, druggability **0.495**, lining residues **406–534**, carrying all 7
NR4A3-vs-paralogue selectivity handles — transiently opens to a druggable state (fpocket
druggability ≥ 0.5). Well-tempered metadynamics drives the opening and yields the **free-energy
profile** F(Rg) (the cost of opening), a stronger statement than a single spontaneous event in plain
MD (10 ns unbiased MD showed only modest breathing, max +3.3 nm² SASA, no clear opening).

## System preparation (`nr4a3_metad.py::_build_fresh`)

- **Receptor:** AlphaFold2 model AF-Q92570 (resolved via the AFDB API, not a hard-coded version).
  The LBD is trimmed to residues 373–626.
- **Fixing:** PDBFixer adds missing heavy atoms and hydrogens at pH 7.0 (no missing-residue insertion).
- **Solvation:** TIP3P water, 1.0 nm padding, 0.15 M ionic strength, neutralised.
- **Force field:** `amber14-all.xml` + `amber14/tip3pfb.xml`.
- **System:** PME (1.0 nm cutoff), H-bond constraints, MonteCarlo barostat (1 bar, 310 K) — NPT.
- The base `System` (force field forces + barostat, **without** the PLUMED force) is serialized to
  `metad_system.xml` so a restart reconstructs it bit-identically.

## Collective variable & bias (`_plumed_script`)

- **CV:** radius of gyration (`GYRATION TYPE=RADIUS`) of the Cα atoms of residues
  406, 407, 410, 411, 412, 481, 484, 485, 531, 534 (Pocket-5 lining, incl. all selectivity handles).
- **Well-tempered metadynamics:** `SIGMA=0.03 nm`, `HEIGHT=1.0 kJ/mol`, `PACE=500` steps,
  `BIASFACTOR=10`, `TEMP=310 K`, grid `0.4–3.0 nm` (260 bins).
- **Walls** (keep the CV physical): `LOWER_WALLS AT=0.6`, `UPPER_WALLS AT=2.2`, `KAPPA=2000`.
- These parameters live in one place (the `METAD` dict) and are written into every run's manifest.

## Integration

- LangevinMiddleIntegrator, 310 K, 1 ps⁻¹ friction, 2 fs timestep.
- **CUDA platform is forced** (mixed precision); the job aborts rather than silently falling back to
  CPU.

## Pre-flight guards (fail-loud, before any production GPU time)

1. **CV identity check** — the residue identities of 406…534 are read from the AF2 model, and each
   selected Cα is asserted to carry the expected residue name in the solvated topology (normalising
   HID/HIE/HIP→HIS, CYX→CYS). Catches any residue-numbering/contiguity shift.
2. **Initial-Rg window check** — the CV's Rg after minimisation is logged and must lie inside the wall
   window [0.6, 2.2] nm (warns if within 5·SIGMA of a wall). Prevents a mis-scaled bias / clipped
   basin from wasting the run.

## Protocol per segment

Fresh run: minimise → NPT equilibration (200 ps) → biased production (`NS` ns). Resume: load
checkpoint → biased production (`NS` ns), skipping minimise/equilibrate.

## Checkpoint / restart (zero-waste, reproducible extension)

Every run writes a complete restart set, and a follow-on run continues from it so **N ns = a + b
segments is identical to one continuous N-ns run** (it only costs the additional segment):

| File | Role |
|------|------|
| `metad_system.xml` | serialized base System (deterministic reconstruction) |
| `nr4a3-lbd-solvated.pdb` | solvated topology + reference coordinates |
| `metad_checkpoint.chk` | OpenMM binary checkpoint (positions+velocities+box; fast resume) |
| `metad_state.xml` | portable serialized `State` (archival / cross-environment) |
| `HILLS` | PLUMED-deposited Gaussians = the accumulated bias |
| `COLVAR` | CV + bias vs time |
| `nr4a3-lbd-metad.dcd` | trajectory (appended across segments) |
| `fes.dat` | free energy vs Rg (`plumed sum_hills`) |
| `metad_manifest.json` | CV residues, metad params, cumulative ns, git ref + sha |

**How resume works.** The base `System` is rebuilt from `metad_system.xml`; PLUMED is re-attached with
the `RESTART` directive (it re-reads `HILLS` and keeps depositing, and appends to `COLVAR`); the
checkpoint restores the exact state. A `CheckpointReporter` also writes `metad_checkpoint.chk` every
100 ps during a run for crash safety.

**Reproducibility guard.** A resume is **refused** (the job aborts) if the CV residue list or any
metad parameter differs from the prior segment's manifest — the existing `HILLS` would be invalid for
new settings and would silently corrupt the free-energy surface. To change the CV/parameters you must
start a fresh run.

## How to run (GitHub Actions → SageMaker)

Workflow `gpu-metad-aws.yml` (`workflow_dispatch`) inputs:

- `ns` — nanoseconds for this segment (5–10 validation, 30–50 production).
- `git_ref` — repo ref the GPU job clones and runs (default `main`).
- `resume_from` — `""` fresh; `auto` to continue the latest run at the default S3 prefix
  (`s3://<bucket>/nr4a3-metad`); or an explicit `s3://…` prefix.
- `max_runtime`, `instance`, `region`.

Outputs (including the restart set) are uploaded to `s3://<bucket>/nr4a3-metad`. Example chain:
`ns=30, resume_from=""` → inspect `fes.dat` → if unconverged, `ns=30, resume_from=auto` to reach 60 ns
for the cost of the extra 30 ns.

## Software versions (pinned by the conda recipe)

`python=3.11`, conda-forge `openmm`, `pdbfixer`, `openmm-plumed`, `plumed`, with
`cuda-version=12.8` (matched to the ml.g5.xlarge driver; `CONDA_OVERRIDE_CUDA=12.8`). The exact
build strings and the git sha of the run are recorded in the job log and `metad_manifest.json`.
