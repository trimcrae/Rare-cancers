# NR4A3-degrader paper — MASTER ORDERED PLAN (v2, reviewer-revised 2026-07-15)

**This is the single human-readable source of truth for WHAT WE RUN, IN WHAT ORDER, AND WHAT'S NEXT.**
The machine calendar that the daily email projects is
[degrader-paper-schedule.json](./degrader-paper-schedule.json) — its milestone `id`s match the stage tags
below one-for-one. When work lands, update BOTH this file's stage status line and the JSON.

- **Supersedes:** the naive "three-step spine" (Step 1 RBFE → Step 2 NR-V04 → Step 3 prospective) captured in
  [nr4a3-degrader-strategy-ternary-first.md](./nr4a3-degrader-strategy-ternary-first.md). The *thesis* is
  unchanged (paralogue selectivity emerges jointly from binary × ternary × ubiquitination geometry); the
  *validation architecture and ordering* are revised per an external reviewer-AI verdict.
- **Reviewer verdict (verbatim capture, so it is not re-litigated):**
  [nr4a3-degrader-reviewer-revisions-2026-07-15.md](./nr4a3-degrader-reviewer-revisions-2026-07-15.md).
- **Verdict headline:** *conditional approval with five mandatory changes.* Proceed NOW with Step 0, the
  compact public accuracy benchmark, and the Step 1 pilot. **HOLD** full ABFE (Step 9) and all prospective
  ternary spend (Step 8) until the validation architecture below is in place.

---

## The five mandatory changes (what actually changed, in one place)

1. **Separate three DIFFERENT kinds of validation — never let one run stand in for another.**
   - **(A) Implementation/accuracy control** = a compact *public* RBFE benchmark (10–20 transformations, one or
     two curated congeneric series with **measured ΔΔG + supported poses**), run through the *exact* container /
     protocol / force field / water model / sampling length / analysis code used for NR4A. Cycle closure,
     fwd/rev agreement, and MBAR overlap are **precision/sampling diagnostics, NOT accuracy** — a perfectly
     closed cycle can be systematically wrong from force-field/pose/receptor-state error.
   - **(B) Target-specific PRECISION experiment** = our cmpd19 RBFE, correctly reframed as *conditional relative
     free energies for a hypothesized cmpd19 binding mode within preselected open NR4A conformers.* It tests
     whether the model gives reproducible, receptor-sensitive hypotheses — **not** whether the binding model is
     correct (cmpd19 has no measured affinity, no pose).
   - **(C) Ternary known-answer control** = at least one system with an **experimental ternary structure +
     measured binary/ternary affinity or cooperativity + a small analogue/linker series** (VHL–BRD4 or
     VHL–SMARCA2). NR-V04 is then a **biological-selectivity holdout, not the method-calibration system.**

2. **Correct the cryptic-pocket thermodynamics (the most important technical fix).** An affinity computed in a
   pre-opened cryptic pocket is the **conditional** quantity ΔG_bind|open, not the observable
   ΔG_bind,obs ≈ ΔG_open + ΔG_bind|open. Each paralogue can have a **different pocket-opening penalty**, so
   comparing binding only in matched open receptors can miss or REVERSE selectivity. Therefore either
   **(preferred)** integrate a converged, uncertainty-bearing **ΔG_open per paralogue**, or **(acceptable)**
   report everything as **explicitly conditional** on the chosen open states and make no unconditional-affinity
   claim. Consequences: pocket collapse in alchemical MD is **evidence the chosen state is unstable**, not an
   auto-fail; restraint free-energy contributions must be included or the result stays conditional; **delete**
   "under-sampling means true binding is likely stronger" (bias can go either way; preselecting a rare open
   state usually OMITS a positive conformational penalty); NMR conformers and release-MD frames **without known
   equilibrium populations cannot be pooled as equally populated.** Worst-conformer = robust-design heuristic
   only; use Boltzmann weighting where populations are estimable, else report sensitivity ranges — never a
   synthetic "ensemble affinity."

3. **Redesign the ABFE (Step 9).** T4L-L99A·benzene is an **implementation smoke test, not a transferable
   offset** — do not subtract a single-system error from an unrelated NR4A–indole calculation. Report raw ABFE;
   report the T4L discrepancy *separately*; do **not** call NR4A values "offset-corrected"; do not use T4L to
   justify one-sided bounds. ABFE does **not** prove cmpd19 "binds at all" — reframe as *is the hypothesized
   cmpd19 pose thermodynamically plausible under the modeled receptor-state and force-field assumptions?* As
   framed, **ABFE is not worth running yet** (interpretability, not cost) — keep it only *after* the public
   accuracy benchmark passes, the opening-state penalty is handled (or conditional interpretation accepted),
   multiple plausible poses are handled, and no T4L offset is applied. Spend that compute instead on
   independent RBFE replicas, the known-answer ternary benchmark, and receptor-state sampling. **Also:** Step 8
   cannot "consume the anchor ABFE per construct" — attaching exit vector + linker + recruiter alters the
   bound ensemble and binary affinity; free-cmpd19 ABFE ≠ each degrader's binary affinity.

4. **Modify the NR-V04 control for CELASTROL COVALENCY.** Celastrol is reported to bind NR4A1 **covalently via
   C551**, so NR-V04 does **not** validate the noncovalent free-energy machinery used for cmpd19, and its
   observed selectivity may contain a large **target-engagement** component, not only ternary cooperativity.
   Add: a **preformed covalent celastrol–NR4A1 adduct model**; a noncovalent-vs-covalent **sensitivity
   analysis**; an **NR4A1 C551A / nonreactive-target control**; **warhead-only** and **active/inactive
   recruiter** controls; and **fixed, preregistered scoring rules** established on the *external* ternary
   benchmark (C). Never say the workflow "recovered degradation" — say *the preregistered computational
   surrogate was directionally concordant (or discordant) with the reported NR-V04 paralogue outcome.* One
   positive + two spared receptors is too few to validate a general degradation-ranking model.

5. **Constrain Step 8 to hypothesis PRIORITIZATION.** Replace the arbitrary scalar score
   `S_d = min_c ΔG_c − λSD − γC − ηL − ρU` (mixed units, tunable weights) with **staged gates + a Pareto
   front**: (1) binary plausibility → (2) ternary thermodynamic/ensemble → (3) linker strain → (4)
   ubiquitination geometry → (5) physicochemical/synthetic → (6) **Pareto selection across candidates that stay
   nondominated under plausible parameter settings**, with uncertainty on every axis. Interface buried-surface-
   area and interface frustration are **supporting descriptors, not universal ranking functions.** Model the
   **real biological object, EWSR1::NR4A3** (not an isolated LBD): add a fusion-context ensemble / domain-
   arrangement sensitivity analysis; lysines **outside** the LBD (hinge, DBD, fusion-partner); DNA/chromatin-
   bound vs unbound sensitivity where feasible; **public EMC VHL/CRBN expression** analysis; and **full
   CRL/E2~Ub geometry ensembles**, not one static arrangement. Ternary formation is necessary, not sufficient —
   productive lysine positioning is a distinct requirement.

**Language discipline (apply everywhere, incl. the manuscript at fold time):**
- "selective hit" → **"predicted selective candidate"**
- "NR4A3-selective" → **"predicted NR4A-paralogue-selective"**
- "does bind at all" → **"is compatible with the hypothesized conditional bound state"**
- "recovered degradation" → **"produced a surrogate score concordant with the reported outcome"**
- "synthesis-ready matrix" → **"a computationally prioritized, structure-defined and retrosynthetically
  annotated candidate matrix for synthesis and experimental testing"** (and "synthesis-ready" is only earned
  once exact structures/stereochem, exit-vector chemistry, routes, building-block availability, protecting-
  group logic, and basic physicochemical assessment exist).
- **Never imply** proteome-wide selectivity, EMC efficacy, safety, a therapeutic window, or clinical readiness.
  The parent cmpd19 functional study also reported transcriptional effects **including MYC induction**, so
  parent-warhead pharmacology is a **potential liability**, not evidence of antitumor benefit.
- **Fix the matrix arithmetic:** {2–3 warheads} × {2 exit vectors} × {VHL, CRBN} × {3 linkers} = **24–36**
  primary combinations *before* inactive stereoisomers and controls — NOT 6–12. The 6–12 deliverable requires a
  **preregistered cheap-screen downselection** that preserves warhead / exit-vector / ligase / linker diversity.

---

## THE ORDERED PLAN — this is "what's next", always read top-to-bottom

Stage status legend: `[ ]` pending · `[~]` in progress · `[x]` done. `∥` = may run in parallel (off critical path).

### `[~]` Step 0 — RBFE infra shakeout  *(id: step0_rbfe_mechanics · GPU)*
Get ONE OpenFE RBFE edge to complete end-to-end on managed-spot GPU with a sane ΔG. Not science yet — proves
the pipeline. Prerequisite for everything. **Currently running** (re-dispatched several times fixing an
`ExecuteUserScriptError`). **Done =** one edge completes end-to-end, sane ΔG.

### `[ ]` Validation A — compact PUBLIC RBFE accuracy benchmark  *(id: valA_rbfe_accuracy_benchmark · GPU)*
10–20 transformations from 1–2 curated congeneric series with **measured ΔΔG + supported poses + similar
charge-state complexity + some receptor flexibility**, through the EXACT NR4A container/protocol/FF/water/
sampling/analysis. Purpose: verify OUR implementation (target expectation ≈ OpenFE public weighted pairwise
RMSE ~1.7 kcal/mol over 58 systems — we are checking our build, not re-running that benchmark). **Gate:** Step 1
fan-out and any absolute-affinity work do not proceed unless this behaves adequately.

### `[ ]` Step 1 pilot — cmpd19 conditional RBFE, 1–2 edges  *(id: step1_pilot_cmpd19 · GPU · ∥ with Val A)*
Reframed: *conditional relative FE for a hypothesized cmpd19 binding mode within preselected open NR4A
conformers.* Run the 1–2 best-behaved edges with **independent replicas + pose/state sensitivity**. Tests
reproducibility + receptor-sensitivity of the model — NOT correctness of the pose. Early-abort if the pilot is
pathological.

### `[ ]` Validation B — known-answer NONCOVALENT ternary benchmark  *(id: valB_ternary_knownanswer · GPU · ∥)*
VHL–BRD4 or VHL–SMARCA2 series (experimental ternary structure + measured ternary affinity/cooperativity +
analogue/linker series). Calibrates the ternary method against ground truth and **fixes the preregistered
scoring rules**. **Gate:** the prospective matrix (Step 8) never runs unless this passes.

### `[ ]` NR-V04 feasibility — covalent parameterization + reduced control panel  *(id: nrv04_feasibility_covalent · GPU)*
Build the **covalent celastrol–NR4A1 (C551) adduct model**; noncovalent-vs-covalent sensitivity; NR4A1 **C551A**
control; warhead-only + active/inactive recruiter controls. This is the pilot-one-leg gate on the full NR-V04
retrospective — abort/adjust if covalency dominates or the reduced panel misbehaves.

### `[ ]` Step 1 fan-out — cmpd19 congeneric map, 8-wide  *(id: step1_fanout_cmpd19 · GPU)*
**Gate:** only if Validation A passed AND the Step 1 pilot behaved. Fan out the congeneric perturbation map
across druggable 8XTT conformers, release-derived NR4A3 conformers, matched NR4A1/NR4A2 open conformers, and
resolved microstates. Rank by worst conformer AND by receptor-effect-exceeds-conformer-effect — as **conditional**
hypotheses, with sensitivity ranges (no synthetic ensemble affinity).

### `[ ]` NR-V04 retrospective — preregistered biological-selectivity holdout  *(id: nrv04_retrospective · GPU)*
**Gate:** depends on Validation B + NR-V04 feasibility + Step 1 fan-out. Run the full NR4A1/2/3 ensembles through
the physics + ubiquitination pipeline **with NO tuning**, preregistered scoring, VHL-inactive epimer as negative
functional control. Report **directional concordance/discordance** with the known degraded-NR4A1 / spared-NR4A2·3
outcome — never "recovered degradation."

### `[ ]` Step 8 — prospective matrix (hypothesis prioritization only)  *(id: ternary_prospective_matrix · GPU)*
**Gate:** only if Validation B passed AND NR-V04 is at least directionally concordant. Enumerate {2–3 warheads}
× {2 exit vectors} × {VHL, CRBN} × {3 linkers} (**24–36**; downselect to ~6–12 by a preregistered cheap screen
preserving diversity). Select by **staged gates → Pareto front** (binary → ternary → linker strain →
ubiquitination geometry → physchem/synthetic), uncertainty on every axis. Model **EWSR1::NR4A3** in fusion
context; lysines beyond the LBD; DNA/chromatin sensitivity; full CRL/E2~Ub geometry ensembles. Deliverable =
predicted selective **candidates**, degradation experimentally unvalidated.

### `[ ]` Step 9 — OPTIONAL conditional ABFE  *(id: abfe_conditional · GPU · ∥ · EXPENSIVE — needs provider+budget nod)*
**HELD.** Only after Val A passes + opening-penalty handled (or conditional interpretation accepted) + multiple
poses handled + no T4L offset applied. Report **raw** ABFE as *pose-plausibility*, T4L discrepancy separately.
T4L·benzene (+ ideally several T4L ligands / a host–guest panel) = implementation smoke test only.

### `[ ]` ΔG_open per paralogue  *(id: dg_open_paralogue · GPU · ∥ · supporting, feeds selectivity + Step 9)*
Converged, uncertainty-bearing pocket-opening free energy per paralogue — the preferred fix for Mandatory
Change 2. If not run, ALL affinity/selectivity results must be stated as explicitly conditional.

### `[ ]` EMC E3-ligase expression analysis  *(id: emc_e3_expression · CPU · ∥ · cheap — route via CI runner)*
Public-data VHL and CRBN expression in EMC samples (informs ligase choice; supports the matrix). Free CPU.

### `[ ]` Pocket-tracking re-analysis  *(id: pocket_reanalysis · CPU · ∥ · cheap)*
Harmonized re-analysis to finalize the paper's Gate-2 druggability wording.

### `[ ]` Fold results into paper  *(id: fold_results · write)*
Single source = [nr4a3-degrader-paper.md](./nr4a3-degrader-paper.md) (+ SI). Apply ALL language discipline above;
QM/torsion validation at degrader linker junctions; physicochemical + retrosynthetic assessment of the final
matrix; re-render figures.

### `[ ]` Final red-team + review-response  *(id: final_redteam · write)*
Honest-weight every claim; medical-integrity check; reviewer-AI block before the outward-facing step.

### `[ ]` Post + submit  *(id: post_submit · submit · OUTWARD-FACING — needs trimcrae sign-off)*
Post ChemRxiv (CC-BY) = JCIM submission; send outreach emails. Finish line.

---

## Dependency spine (compact)

```
step0 ──► valA ───────────────┐
   │                          ▼
   ├──► step1_pilot ──► step1_fanout ──► nrv04_retrospective ──► ternary_prospective_matrix ──► fold ──► redteam ──► post
   │        (∥ valA)              ▲              ▲                        ▲
   ├──► valB ─────────────────────┼──────────────┘                        │  (valB also gates the matrix)
   ├──► nrv04_feasibility ────────┘                                        │
   ├──► dg_open_paralogue ∥ ───────────────► (feeds selectivity + abfe) ───┘
   ├──► abfe_conditional ∥  (HELD: needs valA + dg_open/conditional + budget nod)
   ├──► emc_e3_expression ∥ (cheap CPU)
   └──► pocket_reanalysis ∥ (cheap CPU)
```

## Estimated NEW GPU spend the reviewer changes add (spot, honest ranges)

These are the runs that did **not** exist in the pre-reviewer plan. Anchors: g5.xlarge spot ≈ $0.40–0.60/GPU-h;
repo's 3-receptor RBFE ≈ $18–60 spot; ABFE ≈ $80–200 spot.

| Stage | What's new | Assumptions | Est. spot $ |
|---|---|---|---|
| **Validation A** | public measured-ΔΔG RBFE benchmark | 10–20 edges × ~8–15 GPU-h/edge, exact pipeline, some receptor flexibility | **~$60–180** |
| **Validation B** | known-answer noncovalent ternary benchmark | larger ternary complexes (target+E3+ligand+linker), ~4–8 linker-series edges + cooperativity legs | **~$100–250** |
| **NR-V04 covalent feasibility** | covalent adduct + C551A + reduced controls | small control panel, reused geometry | **~$40–100** |
| _Supporting (optional):_ ΔG_open per paralogue | enhanced-sampling opening FE ×3 paralogues | preferred fix for conditional-affinity; can be deferred to "report conditional" | _~$120–300_ |

**Bottom line: the two mandatory *validation* benchmarks (A + B) add roughly ~$160–430 of new spot spend** (mid
estimate ≈ **$250–300**). Adding the covalent NR-V04 feasibility panel brings the reviewer-mandated new work to
**~$200–530**. The optional ΔG_open sampling (only if we want *unconditional* affinity rather than conditional
reporting) would add ~$120–300 on top. Ranges are wide because per-edge GPU-h depends on lambda count, sampling
length, and receptor flexibility — I'll pin a tighter number from the Step-0 edge's realized GPU-h before
launching each. No new fixed infra cost (same spot fleet). Note this is **new** spend but it also lets us
**retire** the old un-shelved ABFE-anchor spend (~$80–200) as a mandatory item — it's now HELD/optional.

**Right now:** Step 0 is running. The moment it completes clean, the next things to launch are **Validation A**
(public accuracy benchmark) and the **Step 1 pilot** (1–2 cmpd19 edges) — those two in parallel — plus the cheap
CPU supports (EMC E3 expression, pocket re-analysis) which need no GPU. **Validation B** and **NR-V04 covalent
feasibility** geometry prep can also start. **Do NOT** launch the ABFE or the prospective matrix until their
gates above are green.
