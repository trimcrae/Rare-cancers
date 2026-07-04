# Modern-stack ABFE — design (trimcrae decision, 2026-07-04)

**Decision:** go forward on a MODERN, MAINTAINED ABFE stack; retire Yank. (Yank kept only as a possible
cross-check *if* its current NR4A3 run happens to finish cleanly.) Drivers: (1) Yank is abandoned + a
crash/dependency gauntlet; (2) its monolithic HREX `.nc` is un-syncable on spot → poor checkpointing;
(3) we want **every-iteration checkpointing + convergence logging**, which Yank's architecture can't give.

## Architecture: INDEPENDENT λ-window ABFE (not HREX)
The whole point. HREX couples all windows into one big growing `.nc` (the Yank problem). Instead run **each
λ-window as its own independent OpenMM simulation**:
- **Per-iteration checkpoint** — each window saves a tiny OpenMM `State` (positions/velocities/box) every
  iteration to S3 → a spot kill loses **≤1 iteration** (~seconds), not 500–2500.
- **Trivially parallel + spot-friendly** — one SageMaker spot unit per (leg, window); no coupling, no barrier.
- **Per-iteration ΔG trace** — every iteration each window appends its reduced potentials `u(x; λ_j)` for all
  j; a reducer runs MBAR on the accumulated samples → **ΔG(iteration)** convergence curve, as fine as we want.
- Cost vs HREX: independent windows mix less efficiently than replica exchange, so may need more samples/window
  for the same precision — acceptable trade for checkpoint granularity + parallelism. (Optional later: add
  lightweight neighbor-swap *between* independent windows via a coordinator, if precision needs it.)

## Physics (compose TESTED primitives; own only the glue)
Double-decoupling ABFE, two legs:
- **Complex leg**: ligand in the pocket + protein + solvent, with a **Boresch orientational restraint**;
  alchemically turn OFF ligand–environment elec then sterics (soft-core). openmmtools `alchemy`
  (`AbsoluteAlchemicalFactory`, `AlchemicalState`) builds the alchemical system.
- **Solvent leg**: ligand alone in water; same elec→sterics decoupling. (Identical across receptors → cancels
  in ΔΔG.)
- **Boresch restraint + analytical standard-state correction**: openmmtools `RestraintState` /
  `restraints.Boresch` provides the restraint force + `restraint.get_standard_state_correction()`. This is the
  one correctness-critical piece — validate it (below).
- ΔG_bind = −[ΔG_complex(decouple) − ΔG_solvent(decouple)] + ΔG_restraint_standard_state  (double-decoupling).
- MBAR (pymbar ≥4) over each leg's per-window reduced potentials → per-leg ΔG + SE; combine for ΔG_bind.

## Modern env (clean deps — no Yank pins)
python 3.11, `openmm` (latest), `openmmtools` (latest maintained), `pymbar>=4`, `openmmforcefields` +
`openff-toolkit` (ligand params: GAFF2 or SMIRNOFF via `SystemGenerator`), `pdbfixer`, `mdtraj`. CUDA platform
(real GPU — no OpenCL fallback needed on a modern container). This drops EVERY Yank pin (py3.9 / libnetcdf<4.9
/ pymbar<4 / setuptools<81 / openmmtools=0.21.2). Pre-bake into an ECR image like `Dockerfile.sagemaker-fep`.

## SageMaker mapping (spot, per-window units)
- Fan out: one spot Training job per (receptor, leg, window). Each: build system → run MD → per-iteration
  checkpoint (small State → S3) + per-iteration reduced-potential log (small jsonl → S3).
- Resume: on (re)start, load the window's last State from S3 (its own small file) → resume that window only.
- Reduce: a separate job/step pulls all windows' logs → MBAR per leg → ΔG_bind + convergence trace →
  `plot_fep_convergence.py` (already multi-receptor). Per-iteration points, side-by-side receptors.

## Validation (before trusting any NR4A3 number)
1. **Restraint/standard-state correctness** — reproduce a KNOWN ABFE benchmark (host–guest, e.g. a
   SAMPL/CB7 guest, or a well-characterised protein–ligand) and match published ΔG within ~1 kcal/mol.
2. **Cross-check vs Yank** — if Yank's NR4A3 run finishes, the two engines should agree on ΔG_bind (a strong
   not-a-tool-artifact result). If Yank dies, rely on (1) alone.
3. Unit-test all pure glue (schedule, reduced-potential assembly, MBAR call, standard-state formula).

## Build order (incremental; each step testable)
1. `nr4a3_abfe.py` skeleton + pure-glue unit tests (λ schedule, u_kn assembly, standard-state formula). ← START
2. Single-window MD + checkpoint/resume + reduced-potential log (one leg, CPU smoke, then 1 GPU window).
3. MBAR reducer + per-iteration convergence trace → plot.
4. Full complex+solvent legs + Boresch restraint; validate on the host–guest benchmark.
5. SageMaker fan-out (spot, per-window, per-iteration checkpoint) + ECR image.
6. Run NR4A3/NR4A1/NR4A2 → ΔΔG (this is the real deliverable; supersedes the Yank attempt).

## Notes
- Independent-window design ALSO fixes the paralogue NaN differently: each window minimizes/equilibrates on its
  own; a bad initial contact fails ONE window (cheap, isolated) instead of aborting the whole experiment.
- This is the foundation for the "publish pipeline / other targets" platform ideas (IDEAS.md) — a clean,
  maintained, checkpoint-granular engine is what makes those tractable.
