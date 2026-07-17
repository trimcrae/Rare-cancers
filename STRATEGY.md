# STRATEGY — the overarching research plan (NR4A3-selective degrader paper)

> # ★ GOLD-STANDARD SINGLE SOURCE OF TRUTH FOR THE RESEARCH STRATEGY ★
> **This file is THE strategy.** It is the top-level, authoritative plan for the repo's #1 research program —
> the **NR4A3-selective degrader paper** — and it is what CLAUDE.md and README.md point to for "what's the plan /
> what's next / what does each step cost." If any other doc (the schedule JSON, the ternary-strategy note, the
> in-silico next-steps handoff, the route-portfolio capstone, an older manuscript section, a commit message)
> conflicts with this file, **this file wins** — reconcile the other doc to it.
>
> **Where this sits (scope).** The repo's primary focus is the NR4A3 degrader / computational method-development
> program (≈70–80% of effort); its full execution plan is below. The broader EMC treatment **route portfolio**
> (the degrader is #1 within it, plus the fusion-junction ASO and other routes as support/backup) is context
> beneath this file — see [emc-treatment-strategy.md](research/manuscripts/emc-treatment-strategy.md) (route
> ranking) and [research/IDEAS.md](research/IDEAS.md) (live route board). Those are subordinate to this file for
> the overarching plan.
>
> **Keep it current:** when work lands, update the stage's `[ ]/[~]/[x]` status here AND the mirrored `status` in
> [degrader-paper-schedule.json](research/manuscripts/degrader-paper-schedule.json) (its milestone `id`s match the
> stage tags below one-for-one; that JSON is the machine calendar the daily email projects — a MIRROR of this
> file, not a competing source).
>
> **Companion docs (detail only, subordinate to this file):**
> [nr4a3-degrader-reviewer-revisions-2026-07-15.md](research/manuscripts/nr4a3-degrader-reviewer-revisions-2026-07-15.md) (verbatim
> reviewer verdict) · [nr4a3-degrader-strategy-ternary-first.md](research/manuscripts/nr4a3-degrader-strategy-ternary-first.md)
> (biological/chemotype rationale) · [nr4a3-degrader-paper.md](research/manuscripts/nr4a3-degrader-paper.md) (the manuscript itself).

**This is the single human-readable source of truth for WHAT WE RUN, IN WHAT ORDER, AND WHAT'S NEXT.**
The machine calendar that the daily email projects is
[degrader-paper-schedule.json](research/manuscripts/degrader-paper-schedule.json) — its milestone `id`s match the stage tags
below one-for-one. When work lands, update BOTH this file's stage status line and the JSON.

- **Supersedes:** the naive "three-step spine" (Step 1 RBFE → Step 2 NR-V04 → Step 3 prospective) captured in
  [nr4a3-degrader-strategy-ternary-first.md](research/manuscripts/nr4a3-degrader-strategy-ternary-first.md). The *thesis* is
  unchanged (paralogue selectivity emerges jointly from binary × ternary × ubiquitination geometry); the
  *validation architecture and ordering* are revised per an external reviewer-AI verdict.
- **Reviewer verdict (verbatim capture, so it is not re-litigated):**
  [nr4a3-degrader-reviewer-revisions-2026-07-15.md](research/manuscripts/nr4a3-degrader-reviewer-revisions-2026-07-15.md).
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

## Method-validation rationale (why Val A is nearly free but Val B is load-bearing)

Two of the reviewer's mandated validations look similar ("benchmark the method on a known answer") but have
**opposite cost/necessity**, because of whether the method is standard-and-citeable or our own construction:

- **Val A (binary RBFE accuracy) — cheap, mostly a citation.** We run OpenFE's *standard* RelativeHybridTopology
  protocol, which OpenFE already benchmarked (~1.7 kcal/mol over 58 public systems). The only thing that had made
  it non-citeable was a self-inflicted deviation: the RBFE conda env shipped **without AmberTools**, so am1bcc
  charging failed and we fell back to the **NAGL** surrogate. **Root-caused + fixed 2026-07-15** (added
  `ambertools>=23`; `partial_charge_method="am1bcc"`, CPU-verifiable for ~$0). Now on the documented method, we
  **cite OpenFE** and run only a ~$0–15 build-consistency smoke. *(The same fix was propagated to the ternary
  engine `nr4a3_ternary_fep.py`, which had hardcoded NAGL — binary and ternary legs must share charges or the
  cooperativity cycle's cancellation breaks.)*
- **Val B (ternary cooperativity) — genuinely needed, but for PIPELINE-validation reasons, not method-novelty.**
  Our ternary method (`nr4a3_ternary_fep.py`) is a **cooperativity cycle we wired up**:
  `ΔΔG_coop = ternary_morph − binary_morph`, reusing OpenFE's validated per-leg machinery.
  **CORRECTION (2026-07-17), replacing an earlier overstatement ("no published benchmark exercises this
  protocol → there is nothing to cite"):** the *general approach* is NOT novel and IS citeable. All-atom
  alchemical ternary-cooperativity free-energy calculations — the same `ΔΔG_coop = ternary − binary`
  thermodynamic cycle, including the VHL–BRD4/MZ1 known-answer system and even paralogue-selectivity
  applications — are an active published area (2022–2025): coarse-grained alchemical cooperativity on
  BRD4^BD2–VHL/MZ1 (Chen et al., *J. Phys. Chem. B* 2023), combined protein+ligand *pathway-independent* FEP for
  molecular-glue cooperativity / paralogue selectivity (*JCTC* 2025, `10.1021/acs.jctc.5c00064`; and *JCTC* 2025
  `10.1021/acs.jctc.5c00736`), endpoint (MM/GBSA-type) PROTAC cooperativity (*JCIM* 2024,
  `10.1021/acs.jcim.4c01227`), and FEP+cofolding molecular-glue optimization (ChemRxiv 2025). **So this cannot be
  positioned as "first ternary selectivity in silico," and the paper MUST cite and benchmark against this prior
  art** (it also gives us ready known-answer systems and expected error bars to borrow). What genuinely *cannot*
  be cited away is **the accuracy validation of OUR specific pipeline** — you never certify your own container /
  force field / charge model / ternary wiring by pointing at someone else's engine's benchmark (this is exactly
  the reviewer's Mandatory Change 1: run the compact PUBLIC known-answer control through the *exact* protocol you
  use for NR4A). OpenFE itself ships **no** ternary/PROTAC protocol (RBFE/ABFE for single-protein systems only),
  so an *open-source OpenFE-based* implementation + the honest NR4A-paralogue application is at most an
  **incremental** methods contribution, not a landmark — right-size the novelty claim accordingly.
  `ΔΔG_coop` is still the basis for the paper's central *biological* claim (selectivity from ternary
  cooperativity), and NR-V04 can't calibrate it (no solved ternary; celastrol is covalent, so it doesn't even
  exercise this noncovalent morph). The **only** way to know OUR cooperativity numbers mean anything is to run a
  known-answer PROTAC system (VHL–BRD4 / VHL–SMARCA2) through our pipeline ourselves.
  **Val B-mini (~$40–80) is therefore the highest-value dollar in the plan** — the cheapest possible gate on the
  ~$150–400 prospective matrix. Dropping Val B entirely = abandoning the quantitative ternary-selectivity claim.
  Keep Val B-mini; keep Val B-full conditional on it.

## SPENDING RULES (read before launching anything)

1. **NO PRE-AUTHORIZATION, NO PRE-STAGING.** Nothing is ever "launch-ready" or queued to auto-fire. **Every GPU
   run is presented at its gate** with (a) the prior step's result, (b) a pinned cost estimate (from realized
   GPU-h, not a guess), and (c) a wait for an explicit trimcrae "go." Only $0 CPU/CI work runs without a nod.
2. **SPEND-GATED LADDER: cheap-decisive-first.** The plan is ordered so the *cheapest run that could kill the
   paper* comes first, and **each rung's bigger spend is unlocked only if the previous, cheaper rung's result
   looks promising.** We never pay for an expensive stage on a hypothesis a cheap stage could have falsified.
3. **GO/NO-GO after every priced rung.** Each rung below ends with an explicit GO / NO-GO test. NO-GO = stop or
   pivot; do not spend the next rung.
4. **Every step is priced** (spot $, honest range). Anchors: g5.xlarge spot ≈ $0.40–0.60/GPU-h; repo 3-receptor
   RBFE ≈ $18–60 spot; ABFE ≈ $80–200 spot. Ranges are wide until the Step-0 edge gives us a realized GPU-h/edge.

---

## THE ORDERED PLAN (spend-gated) — this is "what's next", always read top-to-bottom

Legend: `[ ]` pending · `[~]` in progress · `[x]` done. `∥` = parallelizable. **Price = est. spot $ for THAT step.**
"Cum." = cumulative spend if we've said GO at every gate up to and including this step (mid-range).

### RUNG 0 — free / already-running (do regardless; ~$0 new)

- **`[x]` Charge-model fix — put am1bcc back on the standard path** *(free engineering, CPU-verifiable)* — **Price: ~$0**
  Root cause of the earlier "am1bcc doesn't work" was simply that **the RBFE conda env shipped WITHOUT
  AmberTools** (`environment-rbfe.yml` had `openff-nagl` but no `ambertools`), so am1bcc's `antechamber`/`sqm`
  charging exit-1'd and we fell back to the NAGL surrogate — which is what *created* the whole Val A validation
  burden. **Fixed 2026-07-15:** added `ambertools>=23` to the env and set `partial_charge_method="am1bcc"`
  (`CHARGE_METHOD=nagl` env-override retained as fallback). Charging is CPU-only, so this is verifiable for ~$0
  on the next shakeout. **Effect: we're now on the documented am1bcc reference method, so we can CITE OpenFE's
  published validation instead of paying to re-derive it.**
- **`[x]` Step 0 — RBFE infra shakeout** *(step0_rbfe_mechanics · GPU)* — **DONE 2026-07-16 · realized ~$1–2 spot**
  **PASSED.** One OpenFE RBFE edge (the shared solvent morph denovo_401→lo_m0_NCCO_gen) ran end-to-end via the
  spot-safe split (setup CPU → simulate GPU-spot → analyze MBAR) and returned a converged
  **ΔG_morph = −48.75 ± 0.57 kcal/mol** (MBAR). Confirmed: (1) **am1bcc charging succeeds on real hardware**
  (leg reached MD); (2) the **spot-safe warmup→production→commit/restore driver** (main `f5f9bbb`,
  `RBFE_SPOT_SAFE=1`) is **GPU-validated on our real edge** — closes the "GPU spot smoke" item left open in the
  infra-gotchas doc; live S3 commits observed during production. Realized wall: solvent GPU leg ~1 h on
  g5.xlarge spot (spot-acquire + env + charging + ~40 min MD) + cheap CPU setup/analyze. Bug fixed en route: the
  legacy welded `mode=run` path is NOT resume-safe (no uploader) — switched to the split; also a self-inflicted
  stop/setup name-substring race (`only_legs=solvent` matched `…-solvent-setup-…`) → re-run on a fresh `…-v2` tag.
  **GO/NO-GO:** one edge finished clean → **GO** to Rung 1.
- **`[ ]` EMC E3-ligase expression analysis** *(emc_e3_expression · CPU/CI)* — **Price: ~$0**
  Public VHL/CRBN expression in EMC samples; informs VHL-vs-CRBN choice. Free — just do it (route fetch via CI).
- **`[ ]` Pocket-tracking re-analysis** *(pocket_reanalysis · CPU)* — **Price: ~$0**
  Finalize the paper's Gate-2 druggability wording. Free — just do it.

### RUNG 1 — cheap reference-reproduction smoke *(now mostly a citation, not a paid benchmark)*

- **`[x]` Validation A — reference-reproduction smoke + cite OpenFE** *(valA_mini · GPU)* — **Price: ~$0–15 · Cum. ~$15**
  **✅ DONE 2026-07-17 — PASS/GO.** Ran the full 5 ns × 12-window RBFE on the public TYK2 `ejm31→ejm42` edge
  (both legs) on a **GCP L4 (CUDA), spot-safe**: **ΔΔG_bind = +0.366 vs ΔΔG_exp = −0.24 kcal/mol → abs err
  0.61 kcal/mol**, inside the 2.0 kcal/mol tolerance → **GO**. Our OpenFE container reproduces a known ΔΔG, so
  the build is sound (kill-switch cleared → proceed to Rung 2). It also proved the GCS checkpoint/resume path
  end-to-end (survived ~9 spot preemptions overnight with zero lost work). Result: `.../valA-tyk2/results/ddg_nr4a3.json`.
  **Reduced from a paid benchmark to a near-free smoke** now that the charge-model fix (RUNG 0) puts us on the
  standard **am1bcc** method. Because we run the documented OpenFE reference protocol, we **cite OpenFE's
  published ~1.7 kcal/mol accuracy** for the method and only run a minimal **1–2 public known-answer edge** to
  confirm OUR container build reproduces a known ΔΔG (charging verify is CPU/$0; the confirming MD edge is ~$5–15).
  **This does NOT touch NR4A** — it's a build-consistency check.
  **GO/NO-GO:** the 1–2 edges land near the known ΔΔG → build is sound, GO to Rung 2. Off → the container build
  has a real bug; fix it before spending further. *(If am1bcc charging ever fails on a specific ligand, fall back
  to NAGL via `CHARGE_METHOD=nagl` — in that case Val A reverts to the paid ~$25 NAGL-validation benchmark.)*
  **GO/NO-GO (legacy NAGL path):** if forced onto NAGL and its edges track measured ΔΔG within ~1.5–2 kcal/mol →
  GO. If wildly off → **NO-GO: fix the charge model, or the quantitative approach can't support a defensible
  paper** (do NOT
  spend on cmpd19/ternary/matrix; pivot to qualitative/structural). A bad paper dies here for ~$25.

### RUNG 2 — cheap precision + cheap probes *(only if Rung 1 = GO)*

- **`[ ]` Step 1 pilot — cmpd19 conditional RBFE, 1–2 edges** *(step1_pilot_cmpd19 · GPU · ∥)* — **Price: ~$15–40 · Cum. ~$50**
  Conditional relative FE for a hypothesized cmpd19 mode in preselected open conformers; replicas + pose/state
  sensitivity. Tests reproducibility + receptor-sensitivity, NOT pose correctness.
  **GO/NO-GO:** reproducible, receptor-sensitive, pocket doesn't collapse → GO. Pathological/irreproducible → the
  cmpd19 anchor is too fragile to build on; reconsider before any fan-out.
- **`[~]` Validation B-mini — PROTAC 2 → cis-PROTAC 2 known-answer ternary edge** *(valB_mini · GPU · ∥)* — **Price: ~$40–80 · Cum. ~$110**
  **REDESIGNED 2026-07-17 (reviewer verdict — full record: [research/manuscripts/valB-reviewer-decision-2026-07-17.md](./research/manuscripts/valB-reviewer-decision-2026-07-17.md)).**
  The original hi→lo SMARCA2–VHL panel edge is **not congeneric** (P1↔P5 = 32 perturbed heavy atoms; the whole
  same-assay panel 32–47), and a wide RCSB search found **no clean same-assay congeneric both-α edge** in the
  public record. Approved substitute: **PROTAC 2 → cis-PROTAC 2** (Farnaby 2019 SMARCA2–VHL; same-assay TR-FRET
  **α = 18 → 1.0**; a single-stereocenter VHL 4-hydroxyproline trans→cis; staged from **6HAX**), preregistered
  **ΔΔG_exp = −RT·ln(1/18) = +1.71 kcal/mol**. Built: `ternary-calib-epimer-frozen.json` +
  `ternary_pdb_stage.py` + `gpu-ternary-fep-gcp.yml` (GCP L4). **GO/NO-GO:** positive sign, CI excludes 0,
  within 1.0 of +1.71, repeats + fwd/rev agree ~0.5, overlap/sampling pass → **GO to valB_full**. Wrong sign /
  err > 1.0 / restraint-dependent → NO-GO. CI-includes-0 / hysteresis / cis non-representable → **Indeterminate
  (NOT a pass)**. **Mandatory cis-endpoint diagnostics** (ligand RMSD, VHL contact occupancy, restraint
  work/sensitivity); a pass from forcibly retaining the active pose is **not** a pass. **valB_mini gates
  valB_full only — it does NOT authorize the NR4A matrix.** Until valB_full passes, **NR4A ternary scores are
  EXPLORATORY** (no validated-ranking claim; keep binary/ternary separable; don't present the matrix as
  validated). **valB_full** must add ≥1 **all-binding graded** congeneric edge (reviewer preflight: Wurz et al.
  1→4, α 12.8→2.6 ≈ +0.94 kcal/mol) before any productive-complex ranking claim.
  - **Readiness + cost anatomy (assessed 2026-07-17).** Unlike valA_mini (which collapsed to a ~$0–15 *smoke*
    because it runs OpenFE's standard, already-published RBFE protocol → we cite OpenFE and just confirm the
    build), **valB_mini is a real known-answer test** — it exercises the bespoke `ΔΔG_coop = ternary − binary`
    cooperativity cycle that "cannot be cited away" (see the Val B rationale above), so it CANNOT shrink to a
    build-confirmation. The harness is **BUILT + unit-tested** (`nr4a3_ternary_fep.py` + `entry_ternary_fep.py` +
    `nr4a3_ternary_fep_sagemaker.py` fan-out submitter + `ternary_fep_reduce.py` cooperativity cycle +
    `gpu-ternary-fep-aws.yml`; 100+ tests pass) **but has NEVER run on GPU.** A "mini like Val A" = **one
    hi→lo cooperativity edge** on a public crystallographic PROTAC — recommended **SMARCA2–VHL P1→P5** (α 93→0.6,
    both crystallographic 9HYN/9HYP, same TR-FRET assay → cleanest Δα; MZ1–BRD4^BD2–VHL α=18 / PDB 5T35 is the
    alternative) — checking ΔΔG_coop recovers the measured Δα, exactly parallel to valA_mini's one TYK2 edge.
    True sequence + cost: (1) freeze the edge + stage crystal structures (**free CI**, per
    `ternary-calib-pair-draft.md` — needs an RCSB ligand-chemistry fetch to confirm hi→lo is mappable, P1→P4
    fallback documented); (2) a **~$1–2 GPU smoke** = the *first-ever* GPU run of the ternary assembly/hybrid-
    topology build (Step 0 did this for binary RBFE; ternary is unsmoked); (3) the **~$40–80 real mini edge**.
    Caveats: the submitter's `unit_gpu_h` is a **STUB** (the smoke/first leg calibrates it; the full frozen
    16-window × 3-replica bundle forecasts ~$288 → that is **Val B-full**, not mini); and the ternary harness is
    **AWS-SageMaker-wired only** (valA_mini ran on a **GCP L4**) → run valB_mini on AWS spot (harness ready) or
    port to the GCP lane first. **STATUS: HELD (trimcrae, 2026-07-17) — no spend, no CI prep launched.** Ready to
    launch on an explicit go.

### RUNG 3 — expand the benchmarks *(only if Rung 2 probes look promising)*

- **`[ ]` Validation A-full — expand to 10–20 edges** *(valA_full · GPU · CONDITIONAL — often skippable)* — **Price: ~$50–140 · Cum. ~$205**
  **Only run if valA_mini shows NAGL introduces error worth characterizing.** If valA_mini reproduces known ΔΔG
  cleanly, this is largely **redundant with OpenFE's published benchmark** — in that case **skip it**, cite
  OpenFE's ~1.7 kcal/mol for the reference protocol, and present valA_mini as confirming the NAGL substitution
  doesn't break accuracy (saves ~$50–140). Run the full set only to *characterize/repair* a charge-model
  discrepancy the mini surfaces. **GO/NO-GO (if run):** RMSE in a defensible band (~≤2 kcal/mol) → GO.
- **`[ ]` Validation B-full — full noncovalent ternary benchmark** *(valB_full · GPU)* — **Price: ~$80–200 · Cum. ~$345**
  Complete VHL–BRD4/SMARCA2 series; **fixes the preregistered ternary scoring rules.** **GATE:** the prospective
  matrix never runs unless this passes. **GO/NO-GO:** recovers known ternary cooperativity ranking → GO.
- **`[ ]` NR-V04 covalent feasibility panel** *(nrv04_feasibility_covalent · GPU)* — **Price: ~$40–100 · Cum. ~$410**
  Covalent celastrol–NR4A1 (C551) adduct + noncov/cov sensitivity + C551A + warhead/recruiter controls.
  **GO/NO-GO:** covalency doesn't swamp the signal and the reduced panel behaves → GO to the full NR-V04.

### RUNG 4 — the real science spends *(only after all benchmarks are green)*

- **`[ ]` Step 1 fan-out — cmpd19 congeneric map, 8-wide** *(step1_fanout_cmpd19 · GPU)* — **Price: ~$60–150 · Cum. ~$515**
  Full congeneric map across conformer panels + matched paralogues + microstates, as conditional hypotheses with
  sensitivity ranges. **Gate:** Val A-full passed AND Step 1 pilot behaved.
- **`[ ]` NR-V04 retrospective — preregistered holdout** *(nrv04_retrospective · GPU)* — **Price: ~$80–200 · Cum. ~$655**
  Full NR4A1/2/3 ensembles through the pipeline, NO tuning, epimer control. Report **directional concordance**,
  never "recovered degradation." **Gate:** Val B-full + NR-V04 feasibility + Step 1 fan-out.
  **GO/NO-GO:** at least directionally concordant with the known NR4A1-degraded / NR4A2·3-spared outcome → GO to
  the prospective matrix. Discordant → **the prospective matrix is not justified;** publish the honest negative.

### RUNG 5 — the flagship spend *(the single biggest spend; only after the go/no-go gate)*

- **`[ ]` Prospective matrix — hypothesis prioritization** *(ternary_prospective_matrix · GPU)* — **Price: ~$150–400 · Cum. ~$930**
  {2–3 warheads}×{2 exit vectors}×{VHL,CRBN}×{3 linkers} = **24–36** → preregistered cheap-screen downselect to
  ~6–12. Staged gates → Pareto front; EWSR1::NR4A3 fusion context; lysines beyond the LBD; full CRL/E2~Ub
  ensembles. Deliverable = predicted selective **candidates**, degradation experimentally unvalidated.

### OPTIONAL / HELD — only if a specific claim needs them AND a budget nod is given

- **`[ ]` ΔG_open per paralogue** *(dg_open_paralogue · GPU · ∥)* — **Price: ~$120–300**
  Only if we want *unconditional* affinity/selectivity instead of reporting conditional. Otherwise **skip** and
  report everything conditional on the open state (fully defensible, $0).
- **`[ ]` Conditional ABFE (pose-plausibility)** *(abfe_conditional · GPU · ∥)* — **Price: ~$80–200**
  HELD. Raw values, T4L discrepancy reported separately, no offset, does NOT prove "binds at all." Launch only if
  the pose-plausibility question is worth it after everything above, with an explicit nod.

### RUNG 6 — write & ship (~$0)

- **`[ ]` Fold results into paper** *(fold_results · write)* — **Price: ~$0** — apply all language discipline; add
  QM/torsion validation at linker junctions + physicochemical + retrosynthetic assessment; re-render figures.
- **`[ ]` Final red-team + review-response** *(final_redteam · write)* — **Price: ~$0**
- **`[ ]` Post + submit** *(post_submit · submit)* — **Price: ~$0** — OUTWARD-FACING, needs trimcrae sign-off.

---

## Spend summary

| Checkpoint | What we've learned by here | Cumulative spot $ (mid) |
|---|---|---|
| After Rung 1 (Val A smoke) | Does our am1bcc build reproduce a known ΔΔG? (charge-model fixed → cite OpenFE) | **~$15** |
| After Rung 2 (pilot + Val B-mini) | Is cmpd19 stable to build on? Does ternary move right? | **~$110** |
| After Rung 3 (full benchmarks) | Are both benchmarks publishable-defensible? | **~$345** |
| After Rung 4 (fan-out + NR-V04) | Real selectivity picture + NR-V04 concordance | **~$655** |
| After Rung 5 (matrix) | The flagship candidate matrix | **~$930** |
| Optional ΔG_open / ABFE | unconditional affinity / pose-plausibility | +$200–500 |

**The whole point:** we can kill a non-viable paper for **~$25**, and we never reach the ~$150–400 flagship
matrix spend until four cheaper gates (Val A-mini → pilot/Val B-mini → full benchmarks → NR-V04) have each said
"this is working." Full-program GPU is ~$0.9–1.5k *only if every gate says GO*. Every launch still waits for an
explicit go — nothing is pre-authorized.

## Dependency spine (compact)

```
RUNG0  step0 (running) + emc_e3 (CPU $0) + pocket_reanalysis (CPU $0)
          │
RUNG1  valA_mini  ──[GO?]──►                                   (cheap kill-switch, ~$25)
          │
RUNG2  step1_pilot ∥ valB_mini  ──[GO?]──►                     (~$110)
          │
RUNG3  valA_full + valB_full + nrv04_feasibility  ──[GO?]──►   (~$345)
          │
RUNG4  step1_fanout ──► nrv04_retrospective  ──[concordant?]──► (~$655)
          │
RUNG5  ternary_prospective_matrix                              (~$930; biggest single spend)
          │
RUNG6  fold ──► redteam ──► post/submit                        ($0)

OPTIONAL/HELD (only with an explicit nod): dg_open_paralogue, abfe_conditional
```

**Right now:** Step 0 is running (~$0 new). The only $0 work I'll do without asking is the two CPU supports
(EMC E3 expression, pocket re-analysis). **Nothing else launches without an explicit go** — when Step 0 finishes
clean I'll bring you Rung 1 (Val A-mini, ~$15–40) with a pinned cost from the Step-0 edge's realized GPU-h, and
we decide GO/NO-GO from its result before any further spend.
