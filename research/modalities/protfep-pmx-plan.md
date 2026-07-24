# 5a-KS wedge engine — the pmx + GROMACS route (decided 2026-07-24)

**Status: route confirmed available, driver not yet written.** This note exists so the build does not
have to re-derive what four free-CI probes already established.

## Why the engine changed

The 5a-KS wedge was implemented on **perses** (`nr4a3_protein_fep.py` + `protfep_run.py`) and the
benchmark lane was built and launched. The first real leg failed, and the failure is structural, not
a packaging detail:

```
PointMutationEngine.propose
  -> _construct_atom_map                                    topology_proposal.py:634
  -> PolymerProposalEngine.generate_oemol_from_pdb_template  :1179, :1180
  -> createOEMolFromSDF                                      :487
  -> oechem.oemolistream()                                   perses/utils/openeye.py:346
```

perses 0.10.3 builds the **old→new residue atom map** — which *is* the alchemical transformation — by
round-tripping each residue template through an OpenEye OEMol. OpenEye is commercial and
licence-gated. Free-CI probes confirmed `generate_oemol_from_pdb_template` has no conditional and no
RDKit alternative; perses' only RDKit-backed mapper (`rjmc/atom_mapping.py`) is the *ligand* mapper
and is not on this path. An import shim satisfies the import and correctly **refuses** the call.

trimcrae's decision (2026-07-24): **switch to pmx + GROMACS** rather than pursue a commercial licence,
descope the wedge, or fall back to the MM-GBSA proxy. pmx is the published, field-standard free engine
for exactly this quantity (Gapsys & de Groot), and "a second MD stack" is engineering — which is free
here — whereas a licence is not.

**Cost of establishing all of the above: ~$0.05 of Vast time**, plus free CI.

## What the probes established (so the build does not repeat them)

| Question | Answer | Gotcha that produced a FALSE negative first |
|---|---|---|
| Is pmx on conda-forge? | **No** — pip/GitHub only | — |
| Does pmx install on Python 3.11? | **Yes, from the `develop` branch** | The repo's DEFAULT branch is the legacy **Python 2** codebase: pip refuses it with `requires <3,>=2.7`. That reads as "pmx does not support modern Python" and is wrong. |
| Is there a CUDA-enabled GROMACS on conda-forge? | **Yes** — `gromacs=*=*cuda*` solves (165 packages, ~2 GB) | Solving on a GPU-less machine fails with `__cuda ... missing on the system`. That is the **virtual package**, not the build's absence. Needs `CONDA_OVERRIDE_CUDA` — including **at bake time**, since the image builder has no GPU either. |
| pmx submodules present | `alchemy`, `estimators`, `forcefield`, `gmx`, `model`, `mutdb`, `ligand_alchemy`, `analysis`, `scripts` | `pmx.scripts.workflows` does **not** exist on `develop`; it is not needed. |

## What carries over unchanged

Everything except the perses-specific build/sample layer is engine-agnostic and already tested:

- `protfep_bench.py` — RCSB staging, chain surgery, and the mutation-site check that **refuses** to
  stage if the residue at the site is not the one the benchmark names (it caught a chain-A/chain-D
  error); scoring; the qualification verdict.
- Reference values — **verified against SKEMPI 2.0** (Y29A 3.469 vs stored 3.4; Y29F corrected from a
  wrong-signed +0.5 to −0.13), with a checker that now fails any sign disagreement.
- `protfep_reduce.py` — ΔΔG from complex−apo, between-replicate SD, the verdict, and the per-leg
  **price** that finally makes this rung priceable.
- The Vast lane — launcher, label/leg-id matching, the reap, continuous S3 checkpointing.

The leg JSON schema is what couples them, so the pmx driver must emit the same keys
(`status`, `dg_kcal`, `gpu_hours`, `n_particles`, `s_per_iter`, `meta.benchmark`, `meta.environment`).

## What still has to be built

1. **`research/compute/Dockerfile.pmxfep`** — CUDA GROMACS from conda-forge (with
   `CONDA_OVERRIDE_CUDA` at build time), pmx from `git+https://github.com/deGrootLab/pmx.git@develop`,
   plus the usual awscli/boto3. Same bake-time sanity assertions as the perses image: fail the free
   build, not a paid host.
2. **`protfep_pmx.py`** — the driver: `pmx mutate` → hybrid structure, `pmx gentop` → hybrid topology,
   GROMACS equilibration, then λ-window FEP reduced with BAR. Equilibrium λ windows are preferred over
   pmx's non-equilibrium protocol for the first implementation: simpler control flow, and GROMACS
   `.cpt` files give natural per-window checkpoint/resume on a spot host.
3. **Checkpoint/resume shaped for GROMACS**, not openmmtools — the `.nc`-based resume in
   `protfep_run.py` does not transfer.
4. **The same staged ladder**: free CI build-test of the hybrid construction (CPU work — only the
   sampling needs a GPU) → smoke → pilot (the abort gate) → full set.

## Open question for the driver, worth settling deliberately

pmx's *published* protocol is **non-equilibrium** (fast-growth + Crooks/BAR), which is what its
benchmarks use and is generally cheaper. Equilibrium λ-window FEP is easier to drive and checkpoint.
Start equilibrium; if convergence is poor or the cost is unattractive, the non-equilibrium path is the
documented fallback and pmx has the estimators for both (`pmx.estimators`). Record whichever is used
in the leg JSON — the two are not interchangeable when quoting a number.
