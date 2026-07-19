# Timestep & equilibration for alchemical FEP on ternary (PROTAC/molecular-glue) complexes — literature review

**Date:** 2026-07-19. **Question:** how does the field choose the MD timestep + equilibration for relative
binding / cooperativity FEP on large assembled ternary complexes (target + degrader + E3), for our
OpenFE / openmmtools-HREX / perses-hybrid / OpenMM + HMR(3 amu) + HBonds stack?

**Sourcing honesty:** OpenFE code defaults were read directly from the GitHub source. Most publisher/PMC/
ChemRxiv/arXiv/OpenFE-doc full texts were 403'd by the egress proxy, so several claims rest on WebSearch
snippets + abstracts (flagged inline). No source was fabricated.

## Bottom line
**Keep 4 fs as the *production* timestep; the ternary NaN is an equilibration / starting-structure problem, not
a production-timestep problem.** 4 fs with HMR≥3 amu + HBonds is the genuine field default (verified from OpenFE
source), and no published atomistic PROTAC/ternary FEP lowers the *production* dt because of assembly size — the
instability of big/rough assemblies is handled at the **prep/equilibration** stage. Fix the ternary NaN with:
1. **Plain-MD pre-equilibration of the assembled, fully-interacting complex** before the RBFE — OpenFE's *explicit*
   recommendation (`PlainMDProtocol`) for exactly this case; its RFE protocol does **no** restrained/annealed
   equilibration and **assumes the input is already stable**. A rough homology model fed straight into softcore
   λ-states is the documented failure mode.
2. **Staged, restrained, low-dt warmup** — the Desmond/FEP+ default recipe: Brownian dynamics ~10 K + heavy-atom
   position restraints at **1 fs**, heat, **release restraints while ramping dt to the production value**. (This is
   the fuller version of our current reduced-dt-only warmup.)
3. **`n_restart_attempts`** on the sampler move (perses NaN mitigation) — already on for us (~20 retries happened),
   so our NaN is *persistent*, i.e. it needs 1+2, not just retries.
4. **If NaNs localize to specific λ-states → it's the softcore, not the timestep**: add λ-windows near the
   endpoints and/or use a gentler/optimized softcore. Our calib NaN was at state 5 (a softcore window).

Do **not** permanently downgrade ternary production to 2 fs — but **do one 2 fs sensitivity replicate** on the
final edge (a 2025 cautionary preprint found up to ~3 kcal/mol bias at 4 fs with HMR+SHAKE in some systems).

## Key facts + citations
- **OpenFE defaults (verified in source, `OpenFreeEnergy/openfe`):** `IntegratorSettings.timestep = 4.0 fs`;
  `validate_timestep()` allows >2 fs **only** when `hydrogen_mass ≥ 3.0` amu; default `hydrogen_mass=3`,
  `constraints=HBonds`, `lambda_windows=11`, `sampler_method="repex"` (HREX), `minimization_steps=5000`,
  `softcore_alpha=0.85`. Files: `openmm_utils/settings_validation.py`, `omm_settings.py`,
  `openmm_rfe/equil_rfe_settings.py`.
- **HMR → 4 fs basis:** Hopkins, Le Grand, Walker, Roitberg, *JCTC* 2015, 11, 1864 (10.1021/ct5010406).
- **OpenFE RFE equilibration caveat (snippet-level, docs 403'd):** RFE guide — *"simple equilibration without
  positional restraints or temperature annealing… equilibrated directly under target conditions… requires input
  structures to be stable"*; remedy = pre-equilibrate with `PlainMDProtocol`; partners sometimes had to restart
  hard systems repeatedly.
- **perses NaN failure mode:** choderalab/perses **Issue #403** — *"Potential energy is NaN after 0 attempts…
  LangevinSplittingDynamicsMove"*; mitigation `move.n_restart_attempts≈5`, more minimization, dump system/state.
- **Reduced-dt restrained warmup is the FEP+ DEFAULT (not a trick):** Desmond/FEP+ 5-stage relaxation — 100 ps
  Brownian 10 K + restraints @ **1 fs** → NVT/NPT 10 K restraints → NPT 300 K → release → production @ RESPA+HMR.
  Gapsys et al., *Chem. Sci.* 2020, 11, 1140 (c9sc03754c); FEP+ sampling-protocol *Sci. Rep.* 2019
  (s41598-019-53133-1). (snippet-level)
- **Softcore ↔ instability (independent of C–H):** König & Gapsys et al., *JCTC* 2020, 16, 5551
  (10.1021/acs.jctc.0c00163); Lee, Allen, Giese, York et al., *JCTC* 2020, 16, 5512 (10.1021/acs.jctc.0c00237) —
  endpoint catastrophe / particle collapse / gradient-jump → large forces near λ-endpoints.
- **Best-practices review:** Mey, Allen, Bruce Macdonald, Chodera, Mobley et al., *LiveCoMS* 2020, 2(1), 18378
  (arXiv 2008.03067).
- **Atomistic ternary cooperativity FEP exemplar:** Feng, Schindler et al. (Schrödinger), *JCTC* 2025,
  10.1021/acs.jctc.5c00736 — standard FEP+ engine defaults (dt not confirmed; full text 403'd).
- **Cautionary minority view:** Jahanmahin … Lee, ChemRxiv 2025, 10.26434/chemrxiv-2025-jwkz1 — recommends ≤2 fs
  for HMR+SHAKE AFE (energy-drift/accuracy). Reason for a sensitivity check, not the consensus.

## What this means for our pipeline
- Our diagnosis (softcore-state warmup NaN on a rough SMARCA2 homology model; C–H already constrained) **matches
  OpenFE's documented failure mode exactly.** The lever is equilibration/prep, not production dt.
- **Highest-value fix = plain-MD pre-equilibration of the assembled ternary** (relax the homology model) before the
  RBFE — cheap, no new physics, OpenFE's own recommendation. Our current reduced-dt-warmup lever is directionally
  right but is the *weaker* (no-restraint, no-heating, no-preequil) form; if it isn't enough, add plain-MD
  pre-equil + a restrained/heated 1 fs → 4 fs staged warmup.
- Keep **4 fs production**; add **one 2 fs sensitivity replicate** on the final ternary edge for the record.
- If NaNs persist at specific λ-windows: more endpoint windows and/or gentler softcore (`softcore_alpha`), not a
  blanket dt cut.
