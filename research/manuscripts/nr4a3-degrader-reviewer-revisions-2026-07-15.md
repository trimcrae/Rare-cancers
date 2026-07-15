# NR4A3-degrader paper — external reviewer verdict (2026-07-15) — VERBATIM CAPTURE

**Do not re-litigate. This records the external reviewer-AI's decision so the revised plan is not second-guessed.**
The plan changes it mandates are operationalized in the ordered master plan
([degrader-paper-plan-v2-ordered.md](./degrader-paper-plan-v2-ordered.md)) and the machine calendar
([degrader-paper-schedule.json](./degrader-paper-schedule.json)). This file is the rationale of record.

## Decision: conditional approval with mandatory changes

The central thesis is reasonable — NR4A paralogue selectivity may emerge from the combined binary, ternary, and
ubiquitination steps rather than from a highly selective warhead alone. Strong precedent that ternary-complex
formation can generate paralogue selectivity, but also that ternary formation by itself is insufficient to
establish productive ubiquitination or degradation. The plan is unusually candid about negative results and
method limitations. **Do NOT launch full Step 1b (ABFE), Step 2 (NR-V04), or Step 3 (prospective) as originally
specified.** Five changes are necessary to make the eventual paper scientifically defensible.

### Mandatory change 1 — separate three kinds of validation
Step 1 and Step 2 were being asked to validate more than they can.
- **A. Implementation/accuracy control.** Add a compact PUBLIC RBFE accuracy benchmark using the exact container,
  protocol, force fields, water model, sampling length, and analysis code used for NR4A. Scope ~10–20
  transformations from 1–2 curated congeneric series with measured ΔΔG, experimentally supported poses, similar
  charge-state complexity, and preferably some receptor flexibility. Do NOT rerun a huge benchmark — OpenFE
  already reports a weighted pairwise RMSE ~1.7 kcal/mol over 58 public systems; our purpose is narrower
  (verify OUR implementation + modifications). Cycle closure, fwd/rev agreement, and MBAR overlap are
  precision/sampling diagnostics, NOT accuracy — even a perfectly closed cycle can be systematically wrong from
  force-field/pose/receptor-state error.
- **B. Target-specific precision experiment.** Keep Step 1 but describe it as *conditional relative free-energy
  calculations for a hypothesized cmpd19 binding mode within preselected open NR4A conformations.* cmpd19 has
  low-µM functional activity + cellular engagement but no direct affinity and no experimental pose. Step 1 tests
  whether the proposed model produces reproducible, receptor-sensitive hypotheses — not whether the binding
  model is correct.
- **C. Ternary-method known-answer control.** NR-V04 cannot be the only ternary validation case. Add ≥1 system
  with an experimental ternary structure, measured binary/ternary affinity or cooperativity, and a small
  analogue/linker series. VHL–BRD4 or VHL–SMARCA2 is suitable. NR-V04 then becomes a biological-selectivity
  holdout, not the method-calibration system.

### Mandatory change 2 — correct the cryptic-pocket thermodynamics (most important technical issue)
An ABFE in a pre-opened cryptic pocket is not the unconditional binding free energy; it is approximately the
conditional ΔG_bind|open. The observable adds the opening cost:
`ΔG_bind,obs ≈ ΔG_open + ΔG_bind|open`. Selectivity is affected too — each paralogue may have a different
pocket-opening penalty; comparing binding only in matched open receptors can miss or reverse overall paralogue
selectivity. Take one of two approaches: **(1, preferred)** integrate a converged, uncertainty-bearing ΔG_open
per paralogue; **(2, acceptable)** report all results as conditional on the selected open conformations and make
no unconditional-affinity claim. Consequences: pocket collapse in alchemical MD is not automatically a failed
calculation (may be evidence the state is unstable); restraint free-energy contributions must be included or the
result is conditional; **remove** the claim that under-sampled reorganization means "true binding is likely
stronger" (bias can go either way; preselecting a rare open state commonly omits a positive conformational
penalty); NMR conformers and release-MD frames without known equilibrium populations cannot be combined as
equally populated. Worst-conformer scores are robust-design heuristics, not thermodynamic ensemble averages —
use Boltzmann-weighted state integration where populations are estimable, else report sensitivity ranges and
robustness percentiles, not a synthetic "ensemble affinity."

### Mandatory change 3 — redesign Step 1b (ABFE)
Do NOT use T4L·benzene as a transferable offset correction. T4L-L99A·benzene is a good implementation smoke
test, but a single-system error cannot be subtracted from an unrelated NR4A–indole calculation as a generally
valid engine offset (T4L is rigid/artificial; NR4A3 is a flexible cryptic pocket with uncertain poses/state
populations). So: report raw ABFE; report the T4L discrepancy separately; do not call NR4A values
"offset-corrected"; do not use T4L to justify one-sided bounds. If an ABFE benchmark is needed, use several T4L
ligands or a small host–guest/standard ABFE panel, not benzene alone. **ABFE does not establish that cmpd19
"binds at all"** — it answers whether a ligand is favorable in the specified bound state/pose relative to
solution; a wrong pose or elsewhere-mediated activity means a converged ABFE does not prove physical binding.
Reframe as: *is the hypothesized cmpd19 pose thermodynamically plausible under the modeled receptor-state and
force-field assumptions?* **Budget:** as framed, Step 1b is not worth running despite the modest dollar cost —
the problem is interpretability. Keep it only after the public accuracy benchmark passes, the opening-state
penalty is incorporated (or conditional interpretation accepted), multiple plausible poses are handled, and no
T4L offset is applied; otherwise spend the compute on independent RBFE replicas, the known-answer ternary
benchmark, and receptor-state sampling. **Also:** Step 3 cannot "consume the anchor ABFE per construct" —
attaching exit vector, linker, and recruiter can alter the target-bound ensemble and binary affinity; free
cmpd19 ABFE is not automatically each degrader's binary affinity.

### Mandatory change 4 — modify the NR-V04 control (celastrol covalency)
NR-V04 is valuable biological evidence that family-selective NR4A degradation is possible (selective NR4A1
degradation, PLA/co-IP ternary evidence, VHL- and proteasome-dependent). But celastrol is reported to bind NR4A1
covalently via C551, so: (1) NR-V04 does not validate the same noncovalent free-energy machinery used for
cmpd19; (2) modeling only a noncovalent celastrol pose is mechanistically incomplete; (3) the recruiter epimer
tests the VHL arm, not target-arm covalency; (4) the observed selectivity could contain a major target-
engagement component, not ternary-cooperativity selectivity. Add controls: preformed covalent celastrol–NR4A1
adduct model; noncovalent-vs-covalent sensitivity analysis; NR4A1 C551A (or nonreactive-target) control;
warhead-only and active/inactive recruiter controls; fixed preregistered scoring rules established using the
external ternary benchmark. Do not say the workflow "recovered degradation" — say *the preregistered
computational surrogate was directionally concordant (or discordant) with the reported NR-V04 paralogue
degradation outcome.* One positive + two spared receptors is too few to validate a general degradation-ranking
model.

### Mandatory change 5 — constrain Step 3 to hypothesis prioritization
Physics-based ternary analysis is defensible for prioritizing hypotheses, not for claiming validated degrader
selectivity (current ternary methods generate observed arrangements but also many different structures; ternary
complexes are dynamic ensembles, not single poses). Replace the scalar score
`S_d = min_c ΔG_c − λSD − γC − ηL − ρU` (arbitrary weights, mixed units, retrospective-tuning risk) with staged
gates + Pareto: (1) binary plausibility; (2) ternary thermodynamic/ensemble; (3) linker-strain; (4)
ubiquitination-geometry; (5) physicochemical/synthetic; (6) Pareto-front selection across candidates nondominated
under plausible parameter settings, uncertainty on every axis. Interface buried surface area and interface
frustration are supporting descriptors, not universal ranking functions. **Model the real biological object,
EWSR1::NR4A3**, not an isolated NR4A3 LBD: the common fusion retains the complete NR4A3 sequence (LBD targeting
plausible) but the EWSR1 N-terminal domain may affect localization, chromatin association, accessibility, and the
reachable lysine landscape. Add: an EWSR1::NR4A3 fusion-context ensemble / domain-arrangement sensitivity
analysis; lysines outside the isolated LBD (hinge, DBD, fusion-partner regions); DNA/chromatin-bound vs unbound
sensitivity where feasible; public-data VHL/CRBN expression in EMC samples; full CRL/E2~Ub geometry ensembles
rather than a single static ubiquitination arrangement. Ternary formation is necessary but not sufficient;
productive substrate positioning and accessible lysines are distinct requirements.

## Revised execution order (reviewer's recommendation — adopted verbatim)
1. Step 0: infrastructure shakeout.
2. Validation A: compact public RBFE benchmark.
3. Step 1 pilot: one or two cmpd19-series edges, with replicas and pose/state sensitivity.
4. Validation B: known-answer noncovalent ternary benchmark.
5. NR-V04 feasibility: covalent parameterization and reduced control panel.
6. Step 1 fan-out: only if the public benchmark and pilot behave adequately.
7. NR-V04 retrospective: preregistered, no tuning.
8. Prospective matrix: only if the external ternary benchmark passes and NR-V04 is at least directionally concordant.
9. Optional ABFE: conditional, raw, clearly caveated.
10. Fold, red-team, submit.
Geometry generation for ternary systems may run in parallel, but expensive ternary free-energy work waits for
both the small-molecule (A) and known-answer ternary (B) controls.

## Direct answers to the six questions (condensed)
1. **Step 2 before Step 1?** No, not in full. Run a cheap NR-V04 feasibility pilot early, but do not run full
   Step 2 before validating the basic free-energy implementation. NR-V04 is covalent → cannot replace Step 1
   validation. Add an external noncovalent ternary benchmark before treating Step 2 as a gate.
2. **"Convergence = self-consistency, not experimental reproduction" sufficient?** Honest but not sufficient
   alone. Missing cmpd19 ΔΔG is not fatal if target results are presented as conditional hypotheses, but the
   paper needs a compact public measured-ΔΔG benchmark to establish the pipeline's expected accuracy.
3. **ABFE worth the expense?** Not under the present interpretation (does not prove binding, cannot omit the
   opening cost, cannot be corrected by a transferable single T4L offset). Retain only as a conditional
   pose-plausibility calculation after the higher-priority validation.
4. **Missing controls/techniques (highest value):** public RBFE measured-ΔΔG benchmark; experimental
   known-answer ternary benchmark; explicit pocket-opening free-energy contribution; covalent NR-V04 modeling +
   C551 control; targeted QM/torsion validation at degrader linker junctions; fusion-context and full
   ubiquitination-geometry sensitivity; public EMC VHL/CRBN expression analysis; physicochemical + retrosynthetic
   assessment of the final matrix. A generic ML degrader predictor is NOT needed.
5. **Physics-based ternary ranking defensible?** Yes as uncertainty-aware hypothesis prioritization; No as proof
   of selective degradation. Publishable-honest needs preregistration, external known-answer controls, ensemble
   reporting, no NR-V04 tuning, uncertainty propagation, and an explicit "degradation experimentally
   unvalidated" statement.
6. **"Synthesis-ready matrix" acceptable?** Not without qualification — use "a computationally prioritized,
   structure-defined and retrosynthetically annotated candidate matrix for synthesis and experimental testing."
   "Synthesis-ready" requires exact structures/stereochem, exit-vector chemistry, routes, building-block
   availability, protecting-group logic, and basic physicochemical assessment. Replace "selective hit" →
   "predicted selective candidate"; "NR4A3-selective" → "predicted NR4A-paralogue-selective"; "does bind at
   all" → "is compatible with the hypothesized conditional bound state"; "recovered degradation" → "produced a
   surrogate score concordant with the reported outcome." Do not imply proteome-wide selectivity, EMC efficacy,
   safety, therapeutic window, or clinical readiness. Parent cmpd19 also induces MYC transcriptionally → parent-
   warhead pharmacology is a potential liability, not evidence of benefit. Reconcile matrix arithmetic:
   2–3 × 2 × 2 × 3 = 24–36 primary combinations before controls, not 6–12 → specify a preregistered cheap-screen
   downselection preserving warhead/exit-vector/ligase/linker diversity.

**Bottom line:** proceed with Step 0, the compact public benchmark, and the Step 1 pilot; HOLD full ABFE and
prospective ternary spend until the validation architecture is in place.
