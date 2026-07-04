# FEP runbook — live state (2026-07-04)

## Goal
Converged selectivity **ΔΔG = ΔG_bind(NR4A3) − ΔG_bind(NR4A1/NR4A2)** for lead `denovo_401`.
Negative ΔΔG = NR4A3-selective (the paper's headline). Yank ABFE, one experiment per receptor.

## Where we are RIGHT NOW (updated ~13:40 UTC)
- **Bug 1 (numba):** openmmtools 0.21.2 numba `_mix_all_replicas_numba` crashed at ~iter 630 with
  `NumbaTypeError: Unsupported array type: numpy.ma.MaskedArray`. Fix = `replica_mixing_scheme: swap-neighbors`
  (pure-Python neighbor swap) + `online_analysis_interval: null` (disable online MBAR, likely masked-array src).
- **Bug 2 (schema, hit on g5):** `replica_mixing_scheme` is a ReplicaExchangeSampler CTOR arg, NOT a valid
  `options:` key — Yank died with `YamlParseError: found unknown parameter replica_mixing_scheme` in ~seconds
  (job nr4a3-fep-sn-0-...-11-16-46, wrote nothing → ckpt/0 empty). **Fix = configure sampler EXPLICITLY via
  `mcmc_moves:` + `samplers:` headers** (samplers schema is allow_unknown → ctor args pass through), reference
  via `experiments: sampler: sampler`. **VALIDATED FREE** via yank-env-check (ExperimentBuilder parse →
  `YAML_SCHEMA_OK`, only a no-OpenCL-platform error AFTER schema validation, expected on CPU). Commit 8b965ad.
  (Also fixed a yank-env-check silent no-op: `conda run python - <<EOF` doesn't forward stdin → validated
  nothing → false green. Now runs from a file + PASS-marker grep guard.)
- **NR4A3 validation run RE-DISPATCHED ~13:40 UTC:** `gpu-fep-aws.yml` mode=run, **tag `nr4a3-fep-sn`**
  (reused — prior prefix empty), only_receptors=nr4a3, phase=full, spot=1, git_ref=branch. Runs pilot(0→500)
  then prod(500→3000). ~25 min setup + ~12 h HREX @ ~12.8 s/iter on 1 A10G spot (once an instance is acquired).
- **THE GATE:** this run must sample **past iter 630** (old numba crash point) to prove the fix. Clock starts
  when an instance is acquired (spot capacity was intermittently out earlier today). Intermediate pilot ΔG at
  ~2 h (500 iters). Old superseded number: nr4a3-fep-trim pilot ΔG −10.5 ± 2.3 (swap-ALL, proves setup only).
- **Old banked number (do NOT confuse):** nr4a3-fep-trim/ckpt/0/nr4a3.json = pilot ΔG **−10.5 ± 2.3** from the
  swap-ALL run that then crashed. Proves setup+binding; does NOT prove the fix. Superseded by nr4a3-fep-sn.

## Monitoring
- Self-wake = **background bash `sleep` → re-invokes agent on exit** (CLAUDE.md verified pattern). Current
  timer: `bdga0are8` (~35 min → first setup/sampling check).
- To read job state: dispatch `fep-status-aws.yml` (inputs: `cw_job`=live CloudWatch yank tail,
  result-json cat, SecondaryStatusTransitions). Public GH API for run status (no auth).

## Next actions (in order)
1. ~35 min: confirm env built + LEaP done + HREX sampling started (catch env/OpenCL failure cheap).
   **Also pre-flight paralogue inputs:** list `s3://<bucket>/nr4a3-denovo-matrix-v2/` — confirm
   `nr4a1-opened.pdb`, `nr4a2-opened.pdb`, `docked_nr4a1.sdf`, `docked_nr4a2.sdf` exist (else fan-out fails).
2. ~2.7 h (gate): confirm nr4a3-fep-sn is **past iter 630**. If clean → step 3. If crash → diagnose (residual
   masked-array elsewhere; candidate: raise/disable `online_analysis_interval`).
3. Fan out paralogues: `gpu-fep-aws.yml` mode=run **tag=nr4a3-fep-sn** only_receptors=**nr4a1,nr4a2**
   phase=full spot=1 git_ref=branch. Canonical indices 1 & 2 → two parallel spot jobs (quota 8, fine).
4. ~13 h: all three at prod. `mode=reduce` (`report_fep.py`) → per-receptor ΔG + ΔΔG.
5. Merge branch → main; fold ΔΔG into nr4a3-degrader paper + preprint plan.

## Downstream pipeline — AUDITED SOUND (2026-07-04)
- Standard-state/Boresch correction: baked into each leg (`_parse_dg` reads `yank analyze` "Free energy of
  binding", which is Yank's fully-corrected ΔG). Nothing to add in reducer.
- `selectivity_ddg`: ΔΔG = ΔG(NR4A3) − ΔG(other), negative = selective. Correct sign.
- `combine_error`: quadrature sqrt(se1²+se2²), treats legs independent = CONSERVATIVE. (Shared ligand →
  identical solvent leg cancels in ΔΔG, so true error is if anything tighter. Honest/safe direction.)

## Working env pins (entry_fep.py conda create — do NOT change without a yank-env-check run)
python=3.9, yank, openmmtools=0.21.2, ocl-icd-system, openbabel, setuptools<81, libnetcdf<4.9, parmed, pymbar<4.
Isolation: `conda run -n fep` with PYTHONPATH="" (base-container numpy 1.x leak fix).
