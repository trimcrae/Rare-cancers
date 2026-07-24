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
- **★ PROSPECTIVE STAGE RESTRUCTURED (2026-07-24, trimcrae decision).** The reviewer verdict and the five
  mandatory changes below are UNCHANGED and still govern validation. What changed is the *prospective stage
  itself*: the fixed molecule-first {warhead×exit×ligase×linker} matrix (old RUNG 5) is **replaced by an
  orientation-first inverse-design ladder with a hard causal kill-switch** — see the dedicated section
  **"★ PROSPECTIVE-STAGE RESTRUCTURING (2026-07-24)"** after the five mandatory changes, and the rewritten
  RUNG 4–5 in the ordered plan. Rationale: the matrix *verified* selectivity if it happened to be present but
  never *designed* for it; the new ladder searches for an NR4A3-discriminating ternary interface, proves it
  causally with reciprocal mutation cycles, and STOPS before the flagship spend if no robust wedge exists. This
  raises rigor/honesty and makes failure detectable; it does not (and no in-silico method can) make success more
  likely — it is a computational hypothesis-prioritization program, not a claim of degradation.

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
  *(2026-07-24: this molecule-first matrix is SUPERSEDED as the WORKFLOW by the orientation-first ladder in the
  next section. The 24–36 figure now bounds the VIRTUAL linker set produced by inverse design against a confirmed
  orientation basin, not a hand-built starting grid. The language rules above still apply verbatim.)*

---

## ★ PROSPECTIVE-STAGE RESTRUCTURING (2026-07-24) — orientation-first inverse design, not molecule-first screening

**What changed, and why.** Mandatory Change 5 fixed *how candidates are scored* (staged gates + Pareto, not a
tunable scalar) but left the workflow **molecule-first**: enumerate a fixed {warhead×exit×ligase×linker} matrix,
model each ternary, score it, and hope the Pareto front happens to contain a selective degrader. That is a
well-controlled lottery — it *verifies* selectivity if it is already present, but it never asks the actual design
question: *what relative target–E3 orientation would create an NR4A3-specific neo-interface that also positions
E2~Ub productively, and what linker chemistry can realize that orientation?* The prospective stage is therefore
reorganized **orientation-first**:

```
paralogue surface differences → selective interface BASINS → productive CRL geometry
    → linker requirements → candidate molecules
```

This single reordering removes blind linker guessing. It **preserves everything MC5 mandated** (Pareto/uncertainty,
EWSR1::NR4A3 fusion context, lysines beyond the LBD, full CRL/E2~Ub ensembles) and **strengthens** it with a causal
test and a hard kill-switch. Precedent grounding (deep literature scan, 2026-07-24): close-paralogue degrader
selectivity is created at the induced PPI surface + differential lysine geometry (BRD4-vs-BRD2/3 charge zipper;
CDK6-vs-CDK4; p38 isoforms flipped by linker/orientation alone), **not** at the conserved warhead pocket — and in
every landmark case it was *discovered then rationalized by a solved ternary structure*, never predicted blind.
There is no validated prospective selectivity predictor in the field, and AKT1/2/3 is the cautionary null (isoforms
too homologous → only pan-degraders). So this ladder is designed to *find and causally justify* a wedge if one
exists, and to *honestly report its absence* if one does not.

**The five load-bearing additions**

1. **A paralogue-differential surface atlas (free, CPU).** Model NR4A1/2/3 in a **MATCHED** ensemble — homologous
   starting frames, identical warhead-pose hypotheses, identical protonation/microstates, identical target–E3
   starting transforms, identical sampling, matched fusion-context scenarios — never three independently-built
   models that could accidentally hand NR4A3 a more favorable start. Map, per receptor state: nonconserved
   solvent-exposed residues; conservative substitutions with altered electrostatics/sterics; E3-reachable regions;
   residues stable across the open-pocket ensemble; lysines on LBD / hinge / DBD / fusion-partner **separately**;
   surfaces sensitive to plausible EWSR1::NR4A3 domain arrangements. Output = a discrimination **map**, not three
   receptor models. Do not assign fabricated equilibrium populations — treat states as explicit scenarios unless
   populations are defensibly estimable.

2. **Orientation-space search before real linkers (cheap → then confirmed).** For each ligase, place VHL/CRBN
   around the warhead-bound target with a flexible linker-reach restraint and sample many relative transforms.
   Ask only: *does any geometrically bridgeable E3 orientation form an interface that is favorable on NR4A3 and
   systematically weaker / frustrated on NR4A1 and NR4A2?* Evaluate every transform against all three paralogues
   with matched protocol. Filters: no severe target–E3 clashes; exit-vector separation chemically bridgeable;
   interface survives restrained relaxation; interface contacts paralogue-differential residues; compatible with
   ≥ part of the CRL/E2~Ub ensemble; an accessible lysine repeatedly enters a productive transfer region; not
   uniquely dependent on one receptor frame. Cluster survivors into **~3–8 orientation basins per ligase**, not
   hundreds of nominal poses.

3. **Selectivity "wedges" proven by reciprocal mutation cycles — the primary causal test.** A basin counts only
   if it has an interpretable structural reason to prefer NR4A3. For a target-surface mutation *m*:
   `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` (the binary leg subtracts mutation effects arising from
   the target–warhead complex itself, isolating the recruited-interface effect). A strong wedge shows: favorable
   NR4A3 interface; **loss** of stability when NR4A3 residues are mutated to NR4A1/2 identities; **partial gain**
   on the reciprocal NR4A1/2→NR4A3 mutations; persistence across receptor/ligase frames; a recognizable steric /
   electrostatic / H-bond mechanism. This is causal computational evidence — far stronger than merely observing
   ΔG_ternary,3 < ΔG_ternary,1.

4. **Separate basin ACCESSIBILITY from basin STABILITY.** Never collapse a construct to one pose + one
   cooperativity number. Estimate `P(B_k | d, s)` (can the linker reach and hold basin *k* under scenario *s*?)
   **separately** from `ΔG_coop(d, B_k, s)` (is that orientation thermodynamically plausible?). A very favorable
   basin the linker almost never accesses is irrelevant — do not assume the lowest-energy modeled pose is occupied.

5. **Robust constraint-satisfaction selection, not Pareto-membership alone.** A candidate advances only if it
   satisfies preregistered constraints across a required fraction of scenarios: binary-pose non-destabilization;
   basin populated in replicated MD; NR4A3 interface advantage over **both** paralogues positive under
   receptor / pose / force-field perturbation; ≥1 NR4A3-specific contact survives counterfactual mutation; a
   meaningful fraction of full-CRL conformations place ubiquitin near an accessible NR4A3 lysine; linker not
   persistently strained + credible chemistry. Rank by `P_d = P(all constraints hold)`, robust to dropping any one
   favorable scenario — this kills the one-favorable-frame artifact that a raw Pareto set still admits (the
   best-of-N winner's-curse risk flagged repeatedly in this program).

**★ THE HARD KILL-SWITCH (the most valuable single addition).** **No causally-confirmed NR4A3 selectivity wedge
⇒ STOP. No linker matrix, no ensemble refinement, no flagship spend.** If NR4A1/2/3 interfaces are too similar to
support a wedge (the AKT1/2/3 outcome), the workflow *correctly returns "no wedge"* and we publish the honest
negative — *"we mapped orientation space and no robust NR4A3-discriminating, ubiquitination-compatible basin
survives causal testing."* That is a real, defensible, novel result, and it is reached **before** the expensive
stages, not after.

**Kill-switch structure — TIERED, cheapest-decisive-first (resolved 2026-07-24).** The kill-switch is tiered so the
*decision to commit the flagship* is cheap — **not** a $350 gate on a $500 tail (an earlier framing mislabeled the
expensive full mutation cycle as "the kill-switch"; corrected here):
- **Tier 1 — atlas ($0 CPU):** no E3-reachable paralogue-divergent surface ⇒ STOP for free.
- **Tier 2 — basin nomination ($0–50):** no basin even nominally discriminates NR4A3 (cheap counterfactual
  screen) ⇒ STOP cheaply. Cheap scoring has poor S/N for *small* differences (ternary docking scores correlate ~0
  with pose quality; ~97 % structure recovery within 10 Å but only ~50 % within 4 Å) — so it is used to *nominate*,
  and a *gross absence* of any nominal signal is still an informative NO-GO, but it is **not** trusted to kill a
  real small wedge.
- **Tier 3 — pilot ONE alchemical mutation direction (~$40–90):** the single most-decisive leg first (3→1, the
  direction most likely to show interface loss), per the repo's pilot-one-leg-before-fan-out rule. No effect ⇒
  STOP. This is the cheap *trustworthy* confirm — one alchemical data point, not the whole cycle.

So the decision to enter the ~$350–1000 flagship costs **~$40–140**, not $350. The **full reciprocal mutation
cycle** (add 3→2 + reciprocal 1/2→3; ~$100–350 total) is completed **only on a passing pilot**, and it is the
paper's **primary causal RESULT** — run because it is the deliverable, not as gate overhead. It still aborts the
~$250–750 refinement tail if the completed cycle disconfirms, but that is a bonus on top of the causal result, not
the reason to run it.

**Honest scope (must hold in the paper).** Everything remains **conditional on the hypothesized cmpd19 binary pose
× receptor frame** — a *double* conditionality; a wedge surviving only one poorly-supported pose is penalized or
dropped. GPU cost is **reallocated, not reduced**: the atlas / basin-search / inverse-linker steps are mostly free
CPU, but the mutation-cycle confirmation and the ensemble refinement are flagship-scale spends that keep the same
per-gate sign-off. The deliverable is a computationally prioritized, structure-defined, retrosynthetically
annotated candidate set with an *identified causal selectivity mechanism* — degradation experimentally unvalidated.

**Paper thesis (upgraded).** From *"a validated workflow ranked an NR4A degrader matrix"* to *"paralogue
selectivity, where achievable, is directed by steering the recruited ligase toward an NR4A3-distinctive
neo-interface; reciprocal target-surface mutation cycles, orientation-basin robustness, and full-CRL
ubiquitination geometry identify the causal mechanism — or honestly establish that no robust wedge exists."*

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
4. **Every step is priced** (honest range), on the CURRENT provider anchors (updated 2026-07-24 from live billing):
   - **MEASURED — Vast RTX 3090, endpoint MD, large assemblies (~150–470k atoms):** billed **~$0.10–0.16/hr**
     (`dph_total`; host storage/inet spread, not the bid, drives it), **~40–61 ns/day → ~$0.4–0.7 per 6 ns leg**
     (NR-V04 covalent panel, 6 completed legs 2026-07-23, firming toward the higher end). That realized panel is
     **~$10–11**, ~**10× under** its old $40–100 estimate — so every MD-bound line below is priced on this leg.
   - **MEASURED — alchemical RBFE complex leg ≈ 55 GPU-h** (~4.5 GPU-h/window × 12; pilot billing 2026-07-13) →
     **~$11 GCP-L4 / ~$18 AWS / ~$8–14 Vast-4090** per complex leg; a full binary edge (complex + solvent) ≈
     **~$12–20 on Vast 4090**.
   - **ESTIMATED — Vast RTX 4090, alchemical, ~$0.144/hr cheapest-eligible (probe 2026-07-22), ~$0.15–0.25/hr
     realized with the ×1.5 bid:** a full **3-replica ternary cooperativity edge ≈ ~$65–110** (vs ~$288 on AWS
     g5 — the same ~435 GPU-h at a ~2–3× cheaper rate). **NOT yet measured on Vast → PIN from the first ternary
     alchemical edge run there;** ternary/mutation-cycle lines below keep wide ranges until then.
   - **Pricing rule for a step:** endpoint MD → price on the measured 3090 leg; alchemical RBFE/FEP → price on the
     4090 edge. (Legacy anchors retired: g5.xlarge spot ≈ $0.40–0.60/GPU-h; the old "$18–60 RBFE / $80–200 ABFE"
     were AWS-priced and ~2–3× the Vast numbers now in use.)

---

## GPU / PROVIDER SELECTION (which card, which cloud, for which run)

Provider and GPU are **independent** choices, and the right GPU depends on the **workload**, not the provider —
OpenFE/RBFE runs on GCP *or* Vast, and so does endpoint MD. Always pick by **cost per nanosecond**
(`$/ns = ($/hr) ÷ (ns_per_day ÷ 24)`), never by headline $/hr and never by "biggest card."

**The one decision rule — where does the run sit on the memory-bandwidth ↔ compute axis:**
- **Bandwidth-bound** — LARGE systems (≳200k atoms) running PLAIN endpoint MD: throughput tracks memory
  bandwidth, so a cheap ex-flagship (RTX 3090, 936 GB/s) nearly matches a 4090 (1008 GB/s) at ~60% of the price
  → **3090 wins $/ns.** (This is the NR-V04 covalent panel: ~466k atoms.)
- **Compute-bound** — SMALLER systems (≲100k atoms) and/or ALCHEMICAL RBFE/FEP (HREX + softcore + λ-derivatives
  add per-step FLOPs): the higher-FLOP card pulls ahead → **4090 wins $/ns** (on GCP: L4, or L40S/L4 by quota).
  (This is cmpd19 binary RBFE and the ternary FEP — do NOT assume the panel's 3090 pick here.)
- **VRAM is almost never the constraint** — even a 466k-atom system needs <4 GB — so do NOT pay up for
  big-memory cards; choose on $/ns and just require ≥24 GB as a safe floor.

**Default recommendation by (workload × provider)** — a starting point, not a law; re-validate per new system:

| Workload | Vast | GCP |
|---|---|---|
| **Large endpoint MD** (NR-V04 covalent panel, ~466k atoms; bandwidth-bound) | **RTX 3090** — bid `min_bid×1.5` (~$0.08–0.11/hr GPU; was ×1.1 → $0.079 but preemption-churned), ~70% under a 4090 & under GCP L4 spot | L4 (quota'd) |
| **OpenFE RBFE / ternary FEP** (alchemical; smaller/compute-bound) | **RTX 4090** — compute matters here; cheapest eligible ~$0.144/hr (probe 2026-07-22) | **L4** (valA/valB ran here); L40S if available |
| Prep / co-fold assembly / analysis (CPU-bound) | run on **CI** (free), not a GPU | run on CI (free) |

**Vast bid + host policy** (`research/modalities/gpu_backend.py`; env-tunable via `VAST_BID_FLOOR_MULT`):
- **Bid = `min_bid × 1.5`** — a margin *above* the market floor so the box wins AND **holds** its slot. **Never cap
  the bid below `min_bid`** — a below-floor bid leaves the box *created-but-stopped* (measured 2026-07-23, a cheap
  3090 sat "loading" 13 min). On Vast you PAY YOUR BID; the multiplier trades a little $/hr for far fewer
  preemptions. **Raised 1.1→1.5 on 2026-07-23:** at `×1.1` the preemption-prone legs churned (a covalent leg sat at
  frame 100 for ~3 h, repeatedly re-bought + reloading), because the baked image is ~6 GiB and reloads in **~20 min**
  (not the "~3-min" once assumed) — so each preemption is expensive and a floor-hugging bid is *false economy*.
  Preemptions that still happen are absorbed by per-unit checkpoint + idempotent re-dispatch (resume, not restart).
- **PIN the env to `cuda-version=12.6` + filter `cuda_max_good ≥ 12.6`** — the *unpinned* env pulled a too-new
  CUDA-13+ OpenMM whose plugin PTX won't JIT on ANY host driver (`CUDA_ERROR_UNSUPPORTED_PTX_VERSION`; measured
  2026-07-23, even `cuda_max_good ≥ 13.0` hosts crashed). Chasing bleeding-edge-driver hosts is the wrong fix —
  control OUR build: pin OpenMM to CUDA 12.6 (PTX runs on any ≥12.6 driver = essentially all Vast hosts). Also
  filter `reliability2 ≥ 0.90`, require ≥24 GB VRAM, **rank
  offers by `min_bid`** (the true interruptible cost). `ResourceSpec.gpu` is per-run (override: `VAST_GPU_MODEL`)
  and falls back to any capable card if the preferred model is scarce.

**When a new workload/system appears, VALIDATE — don't assume.** Tooling: `nrv04_vast_launch` mode `probe_offers`
dumps the live per-card $/hr landscape; the endpoint-MD driver stamps `ns_per_day` into every result JSON. One
cheap smoke on two candidate cards ⇒ a real $/ns comparison. Re-pick per workload.

---

## THE ORDERED PLAN (spend-gated) — this is "what's next", always read top-to-bottom

Legend: `[ ]` pending · `[~]` in progress · `[x]` done · `[–]` skipped (not needed; rationale inline). `∥` = parallelizable. **Price = est. spot $ for THAT step.**
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
- **`[x]` EMC E3-ligase expression analysis** *(emc_e3_expression · CPU/CI)* — **DONE 2026-07-23 · ~$0**
  Extended the script from CRBN-only to **both** recruiter arms and ran it against HPA via CI
  (`nr4a-e3-expression.json`). **Result:** all 10 components of both CRL2^VHL (VHL/ELOB/ELOC/CUL2/RBX1) and
  CRL4^CRBN (CRBN/DDB1/CUL4A/B/RBX1) are "Detected in all" tissues → **both arms broadly expressed**, so the
  VHL-vs-CRBN choice is **NOT constrained by machinery availability** and should be made on
  ternary/geometry/selectivity grounds. Honest limit: no EMC line is in HPA → general soft-tissue/mesenchymal
  availability, not EMC-specific.
- **`[x]` Pocket-tracking re-analysis** *(pocket_reanalysis · CPU)* — **DONE 2026-07-23 · ~$0**
  Harmonized consolidated detection (`nr4a3-pocket-reharmonize-summary.json`, the pinned-fpocket + score-
  independent matcher rerun) folded into the paper's Gate-2 wording (§2.1): 8XTT **19/20 detected, 3 ≥ D\*=0.53**
  (was 4/20 pre-harmonized); release bias-free continuations druggable in **56/40/80 %** of frames per replica,
  **44/75 = 59 % pooled**. Replaced the two "await harmonized" placeholders with the actual both-denominator numbers.

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

- **`[x]` Step 1 pilot — cmpd19 conditional RBFE, 1–2 edges** *(step1_pilot_cmpd19 · GPU · ∥)* — **Price: ~$15–40 · Cum. ~$50**
  Conditional relative FE for a hypothesized cmpd19 mode in preselected open conformers; replicas + pose/state
  sensitivity. Tests reproducibility + receptor-sensitivity, NOT pose correctness.
  **GO/NO-GO:** reproducible, receptor-sensitive, pocket doesn't collapse → GO. Pathological/irreproducible → the
  cmpd19 anchor is too fragile to build on; reconsider before any fan-out.
  **FIRST EDGE RUN (2026-07-18):** `zaienne_cmpd19 → cw_ev_5nh2` (5-Br → 5-NH₂ indole) ran end-to-end and
  **converged** on Modal L4 (spot-safe checkpoint/resume): complex ΔG_morph = **−29.68 ± 0.24**, solvent
  = **−31.52 ± 0.26** → **ΔΔG_bind = +1.84 kcal/mol** (reducer 1.839; ±0.36 quadrature of leg MBAR SEs), i.e. the
  5-NH₂ analogue is predicted ~1.8 kcal/mol (~20×) **weaker** than cmpd19 *in the modeled opened pocket*. This
  proves the congeneric-RBFE **pipeline works end-to-end and converges** on the real NR4A3 system (both legs MBAR-
  converged, tight within-run SE), the plumbing half of the gate. **NOT YET DONE for the GO decision:** the
  result is a **single edge / single replicate / single opened-conformer**, so the reproducibility (replicas) and
  receptor-sensitivity (pose/state sweep) the GO/NO-GO requires are still pending. **Honest weight:** a
  *conditional* relative FE on a *hypothesized* cmpd19 pose (no solved structure, no measured affinity) —
  statistical convergence + self-consistency, **not** an experimental-accuracy claim (that is valA, the separate
  public benchmark). **CHECKED OFF:** the pilot's pre-registered crux — *can a congeneric RBFE converge on this
  dynamic cryptic pocket without the pocket collapsing?* — is **cleared** on the first edge. The reproducibility
  replicas + pose/state sensitivity sweep are carried forward as **inputs to the fan-out** (they refine per-edge
  `n_windows`/GPU-h and the conditional caveat; they do **not** reopen this box). The **valA accuracy gate** is
  independently satisfied (valA_mini clean on am1bcc → cite OpenFE; **valA_full skipped**), so that side of the
  fan-out gate is met — but RUNG 4 still requires the replicas + pose/state sensitivity above; checking this box
  does **not** by itself unlock the fleet.
- **`[~]` Validation B-mini — all-binding graded cooperativity edge (Wurz cmpd 1→4)** *(valB_mini · GPU · Vast 4090 / GCP-L4 · ∥)* — **Price: ~$40–80 · Cum. ~$85**
  **★ RECONCILED 2026-07-24 (all-binding-graded-first rule + schedule sync).** The mini is the **Wurz et al.
  SMARCA2–VHL cmpd 1→4 all-binding graded edge** (α 12.8→2.6 ≈ **+0.94 kcal/mol**; both endpoints are *productive
  binders*), which the schedule already carries as in-progress — this is the cleanest first quantitative
  calibration because neither endpoint is a deliberately-broken pose. The **PROTAC 2 → cis-PROTAC 2 epimer edge
  described below is DEMOTED to the negative-endpoint STRESS module of the Val B-full cube** (the cis epimer
  deliberately challenges VHL engagement, so it tests whether the pipeline correctly becomes *uncertain / rejects*
  an unstable, restraint-dependent endpoint — it is NOT the primary numerical calibrator; a pass forced by
  artificially holding the active pose is not a pass). The reviewer-decision record and epimer mechanics below
  remain valid **for that stress module**.
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

- **`[–]` Validation A-full — expand to 10–20 edges** *(valA_full · GPU · **SKIPPED 2026-07-18**)* — **Price: ~$50–140 (NOT spent) · saves ~$50–140**
  **SKIPPED — the skip condition was met.** valA_mini reproduced the known TYK2 ΔΔG cleanly (abs err 0.61 kcal/mol
  ≪ 2.0) on the **standard am1bcc** method (post RUNG-0 charge fix), NOT the NAGL surrogate. The original purpose
  of valA_full was to *characterize/repair a NAGL-introduced discrepancy* — that discrepancy no longer exists, so
  a full 10–20 edge re-derivation is **redundant with OpenFE's published ~1.7 kcal/mol benchmark** for this exact
  reference protocol. **Accuracy framing (must hold in the paper):** cite OpenFE's published benchmark for the
  am1bcc RelativeHybridTopology protocol; present valA_mini as a single-edge **build-consistency confirmation**
  (our container reproduces a known ΔΔG), NOT as a standalone accuracy benchmark. **Re-open ONLY if** am1bcc
  charging is later forced onto NAGL for some ligand (`CHARGE_METHOD=nagl`), in which case Val A reverts to the
  paid NAGL-validation benchmark. *(Prior GO/NO-GO if it had run: RMSE ≤ ~2 kcal/mol → GO.)*
- **`[ ]` Validation B-full — component-calibration cube (module-specific, no single "validated" verdict)** *(valB_full · GPU · Vast 4090 + 3090)* — **Price: ~$120–350 · Cum. ~$285**
  Replaces the monolithic "full series" with **four separately-calibrated modules**, each with its own uncertainty
  model + pass/fail; a failed module becomes **qualitative-only** and there is **no** blanket "the ternary pipeline
  is validated." Modules:
  1. **All-binding graded cooperativity** — *(already run as valB-mini: Wurz cmpd 1→4)*; Val B-full ADDS ≥1 more
     graded edge for coverage. *(4090 alchemical, ~$65–110/edge)*
  2. **Ternary pose recovery** — does the generator include the known orientation in its top-k, with calibrated
     confidence? *(co-fold, CI/cheap ~$0)*
  3. **Paralogue discrimination** — same degrader across closely related paralogues on a public system with a
     known differential (the direct analogue of the NR4A ask). *(4090 alchemical, ~$65–110)*
  4. **Productive-vs-unproductive ubiquitination geometry** — a full-CRL model separates ternary occupancy from
     Ub-transfer competence on a public system with mapped lysines. *(3090 MD, ~$10–40)*
  Plus the **cis-epimer negative-endpoint STRESS module** (demoted from valB-mini). **GATE:** the prospective
  ladder never runs unless the **cooperativity + paralogue-discrimination** modules pass (calibrated intervals,
  correct direction on held-out observations). *(Priced on Vast: the two alchemical edges dominate; MD/co-fold
  modules are cheap. Was ~$80–200 as a single AWS-priced series; the cube is broader but each module is real-card
  priced.)*
- **`[~]` NR-V04 covalent feasibility panel** *(nrv04_feasibility_covalent · GPU · Vast)* — **Price: MEASURED ~$0.37–0.71/leg (mean ~$0.6) → ~$10–11 for the 18-leg panel (was estimated $40–100 — ~an order of magnitude too high; superseded) · Cum. ~$256**
  Covalent celastrol–NR4A1 (C551) adduct + noncov/cov sensitivity + C551A + warhead/recruiter controls.
  18 legs (6 systems × 3 seeds), 6 ns each (1 ns equil + 5 ns prod), ~466k atoms.
  **MEASURED cost (2026-07-23, 6 completed legs, firming):** RTX 3090 on Vast, interruptible **bid `min_bid`×1.5**
  (raised from ×1.1 for preemption-hold); billed on `dph_total` ≈ **$0.10–0.16/hr** (bid + each host's storage/inet
  — this spread, not the bid, drives per-leg cost). A full 6 ns leg = ~2 h production (~40–61 ns/day) + load/equil;
  realized per-leg costs span **$0.37–0.71 (mean ~$0.6 over 6 legs, S3-persisted ledger firming toward the higher
  end as pricier hosts finish)** → **~$10–11 for the 18-leg panel.** Even at the high end this is ~an order of
  magnitude under the old $40–100. **Downstream Cum. figures shift down ~$55 accordingly.**
  **Real Vast infra that had to be fixed to complete this (all merged, root-caused from instance logs):** PTX host
  filter `cuda_max_good≥13.0` (the env's PTX is CUDA-13-class, so old-driver hosts crashed at build_system),
  429-throttled teardown, S3-persisted price ledger, idempotent skip-only-alive re-dispatch, auto-stop reap of
  terminal/duplicate instances, and the ×1.5 preemption-hold bid.
  **Pipeline PROVEN end-to-end** (first clean leg: no blow-up, R1 stable + R2 recruited), with checkpoint/resume
  (portable OpenMM state → S3 every 50 frames) + idempotent re-dispatch so a spot preemption resumes, not restarts.
  Covalent-pull blow-up (the stiff C6→Sγ restraint across the co-fold's ~7.4 Å gap) is handled by minimize +
  chunked-equil finite guards — `cov_nr4a1` reached production without diverging.
  **GO/NO-GO:** covalency doesn't swamp the signal and the reduced panel behaves → GO to the full NR-V04.

### RUNG 4 — warhead map, differential atlas, and the retrospective gate *(the science inputs to the prospective ladder)*

- **`[ ]` Step 1 fan-out — cmpd19 congeneric map, 8-wide** *(step1_fanout_cmpd19 · GPU · Vast 4090)* — **Price: ~$50–140 · Cum. ~$390**
  Full congeneric map across conformer panels + matched paralogues + microstates, as conditional hypotheses with
  sensitivity ranges — this produces the **warhead + exit-vector inputs** the inverse-design stage (5b) consumes.
  **Gate:** Val A accuracy satisfied (**valA_full SKIPPED — valA_mini clean on am1bcc → cite OpenFE**) AND the
  Step 1 pilot behaved. *(Priced on Vast 4090 alchemical RBFE, ~$12–20/edge; pin from the pilot's realized GPU-h.)*
- **`[x]` NR4A differential surface atlas** *(nr4a_differential_atlas · CPU · ∥)* — **DONE 2026-07-24 · $0 (in-sandbox CPU)**
  Built + ran the free analysis half: [`nr4a_differential_atlas.py`](research/modalities/nr4a_differential_atlas.py)
  (pure-stdlib Shrake–Rupley SASA + affine-gap BLOSUM62 alignment + character-change typing) over the matched
  `results/nr4a3-matrix/nr4a{3,1,2}-opened.pdb` models →
  [`nr4a3-differential-surface-atlas.json`](research/modalities/nr4a3-differential-surface-atlas.json) +
  [write-up](research/modalities/nr4a3-differential-surface-atlas.md) + 6 passing unit tests. **Validated:**
  per-residue paralogue identities reproduce the canonical `nr4a-selectivity.json` on **148/148** known residues
  (0 mismatch). **Result:** 254 residues, 137 exposed, 109 divergent (42.9 %), **46 differential-surface handles**
  (exposed × divergent × character-changing; 33 vs both paralogues), 15/15 LBD lysines exposed. Top handles: U576
  L→(G/N), U574 Q→(V/G), U412 R→(A/T, charge-lost vs both), U424 Q→(L/Y), U413 D→(K/S, charge-reversed).
  **★ GATE: PASS / GO** — a differential surface exists to steer an E3 against (distinct from the ~70 % pocket
  hotspot), so the RUNG-5a orientation-basin search is warranted. *(Optional add-on still open: matched NR4A1/2 MD
  ensembles, ~$10–40 Vast 3090, to test which handles survive dynamics — a handle is a hypothesis until the RUNG
  5a-KS reciprocal mutation cycle tests it causally.)*
- **`[ ]` NR-V04 retrospective — preregistered holdout** *(nrv04_retrospective · GPU · Vast 3090 MD + 4090 FEP)* — **Price: ~$60–150 · Cum. ~$500**
  Full NR4A1/2/3 ensembles through the pipeline, NO tuning, epimer control. Report **directional concordance**,
  never "recovered degradation." **Gate:** Val B-full + NR-V04 feasibility + Step 1 fan-out. **GO/NO-GO:** at least
  directionally concordant with the known NR4A1-degraded / NR4A2·3-spared outcome → GO to the prospective ladder.
  Discordant → **the ladder is not justified;** publish the honest negative. *(Revised down from ~$80–200: the MD
  bulk runs on Vast 3090 at the measured ~$0.4–0.7/leg — the NR-V04 covalent feasibility panel realized ~$0.6/leg,
  ~10× under its old estimate — with only a few alchemical/ubiquitination-geometry legs on 4090.)*

### RUNG 5 — orientation-first prospective ladder *(replaces the fixed 24–36 matrix; the flagship, now gated mid-ladder by the causal kill-switch)*

> Workflow: paralogue surface differences → selective interface **basins** → productive CRL geometry → linker
> requirements → molecules. Full detail + rationale: **"★ PROSPECTIVE-STAGE RESTRUCTURING (2026-07-24)"** above.

- **`[ ]` 5a · Orientation-basin search** *(orientation_basin_search · CPU + opt. Vast 3090 rescore · ∥)* — **Price: ~$0–50 · Cum. ~$525**
  Broad VHL/CRBN transform sampling (flexible linker-reach restraint); matched 3-paralogue interface scoring;
  cluster into **~3–8 basins/ligase**; cheap counterfactual residue screen to **nominate** wedges. Rigid-body
  sampling + coarse scoring + clustering is **$0 CPU**; optional MM-GBSA rescore of basin representatives ×
  paralogue on Vast 3090 ~$30–50.
- **`[ ]` 5a-KS · Wedge confirmation — ★ pilot-first KILL-SWITCH (cheap gate) + causal RESULT** *(selectivity_wedge_confirm · GPU · Vast 4090 alchemical)* — **Decision: ~$40–90 · full result if GO: ~$100–350 (est.) · Cum. to decision ~$590**
  **Pilot ONE direction first** (repo pilot-one-leg rule): the single most-decisive leg **3→1**
  (`ΔΔG_neo-interface = ΔG_mut^ternary − ΔG_mut^binary`), ~**$40–90** on Vast 4090.
  **★ CHEAP GO/NO-GO:** no interface loss on the pilot ⇒ **STOP** — with the free Tiers 1–2 (atlas + basin) the
  whole *decision* to enter the flagship costs **~$40–140**; publish the honest causal negative, run NO linker
  design / ensemble / local FEP (saves the ~$250–750 tail). Loss on the pilot ⇒ **complete the full reciprocal
  cycle** (add 3→2 + reciprocal 1/2→3, ~$100–350 total) — the paper's **primary causal RESULT** (run because it is
  the deliverable), which also aborts the tail if the completed cycle disconfirms.
  *(ESTIMATED — PIN with the first Vast ternary alchemical edge. This is **not** a $350 gate on a $500 tail: the
  *decision* is ~$40–140; the ~$100–350 full cycle is the causal deliverable, not gate overhead.)*
- **`[ ]` 5b · Inverse linker design** *(inverse_linker_design · CPU · ∥)* — **Price: ~$0–20 · Cum. ~$735**
  For each confirmed basin, derive linker requirements (endpoint-distance dist, exit-vector dihedral, attachment
  angles, flexibility, extension range, solvent path, surface avoidance, strain, motion tolerance); enumerate a
  large virtual linker library; filter by **basin fidelity** `F_{d,k}` (conformer closure + strain); keep linkers
  that realize **distinct** basins (orientation control, not atom count); annotate exact structures + synthetic
  feasibility → **~12–20 virtual constructs** (this is where the "24–36" arithmetic now lives — an upper bound on
  virtual constructs, not a hand-built grid). Mostly **$0 CPU**.
- **`[ ]` 5c · Explicit ternary-ensemble refinement** *(ternary_ensemble_refine · GPU · Vast 3090 endpoint MD)* — **Price: ~$100–250 · Cum. ~$910**
  ~12–20 → replicated ternary + full CRL/E2~Ub MD across target states, initial linker conformers and in-basin
  poses; matched NR4A1/2/3; interface-contact persistence; linker-strain distributions; basin retention; **separate
  accessibility from stability**; robust constraint-satisfaction filtering → **~4–8 constructs** nondominated under
  scenario + model uncertainty. *(Endpoint MD → Vast 3090 at the measured ~$0.4–0.7/leg; dozens-to-~200 legs.)*
- **`[ ]` 5d · Local ternary FEP** *(local_ternary_fep · GPU · Vast 4090 alchemical · ∥)* — **Price: ~$150–500 (est.) · Cum. ~$1,235**
  Alchemy **only** within a retained basin (both endpoints plausibly bound, modest congeneric linker change,
  acceptable hybrid topology, endpoint stability not restraint-created). Refines the matched final series; **NOT**
  used to compare unrelated linkers, ligases, or basins. ~3–6 cooperativity edges × ~$65–110 (3-replica, Vast
  4090). **Final set ~6–12** with ≥2 mechanistic wedges, ≥2 linker architectures, VHL and CRBN only where both
  survive, explicit negative controls, robust to reciprocal-mutation tests.
  **Deliverable** = a computationally prioritized, structure-defined, retrosynthetically annotated candidate set
  **with an identified causal selectivity mechanism** — degradation experimentally unvalidated.

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

| Checkpoint | What we've learned by here | Cumulative $ (mid, Vast-priced) |
|---|---|---|
| After Rung 1 (Val A smoke) | Does our am1bcc build reproduce a known ΔΔG? (charge-model fixed → cite OpenFE) | **~$12** |
| After Rung 2 (pilot + Val B-mini) | Is cmpd19 stable to build on? Does the all-binding graded ternary edge rank right? | **~$85** |
| After Rung 3 (Val B cube + NR-V04 feasibility) | Do the ternary modules calibrate? (valA_full SKIPPED — cite OpenFE) | **~$300** |
| After Rung 4 (fan-out + atlas + NR-V04 retro) | Warhead map + differential-surface atlas + NR-V04 concordance | **~$500** |
| **★ Rung 5a-KS — pilot-first wedge gate** | **Pilot ONE mutation direction; no interface loss ⇒ STOP + publish causal negative (marginal decision ≈ $40–140)** | **~$590 (decision)** |
| After Rung 5 full (basin→confirm→linker→refine→FEP) | The flagship candidate set + its causal mechanism | **~$1,235** |
| Optional ΔG_open / ABFE | unconditional affinity / pose-plausibility | +$200–500 |

**What the restructuring does to the price (honest):**
- **Full-go ceiling rises modestly — ~$1.2k mid (range ~$0.8–1.9k), vs the old ~$0.9k** — because the flagship now
  does genuinely more *physics* (causal reciprocal mutation cycles + ensemble MD + local FEP) instead of
  co-fold-and-score on a fixed matrix.
- **The live Vast pricing keeps that increase small.** On the old AWS anchors the restructured ladder would be
  ~$2–3k; the **measured** Vast 3090 endpoint-MD (~$0.4–0.7/leg, ~10× under the old MD estimates) plus the
  ~2–3×-cheaper Vast-4090 alchemical rate hold it near ~$1.2k. Every MD-bound line (atlas, NR-V04, ensemble
  refine) is now cheap; only the alchemical 4090 work (wedge cycles, local FEP, the Val B cube edges) carries real
  cost.
- **The kill-switch caps the *likely* spend — cheaply.** If no robust wedge (the real risk on homologous
  paralogues), the pilot mutation direction fails and we **stop at ~$590** — a **~$40–140 marginal decision** (free
  atlas + basin nomination + one pilot alchemical leg) on top of RUNG 4 — with a publishable causal negative, and
  saving the ~$250–750 refinement tail. This is **not** a $350 gate on a $500 tail.
- **The full reciprocal mutation cycle (~$100–350, est.)** — the one Vast price not yet measured on our card (pin
  it with the first Vast ternary edge) — is the paper's **primary causal RESULT**, completed only on a passing
  pilot. It is the deliverable, not gate overhead; treating it as "spend to decide to spend" was the earlier error.
- **Net:** we can still kill a non-viable paper for **~$25** (Val A) and get an honest *causal* negative for
  **~$725** (kill-switch); full program is **~$1.2k only if every gate — through the wedge confirmation — says GO.**
  Every launch still waits for an explicit go; nothing is pre-authorized.

## Dependency spine (compact)

```
RUNG0  step0 [x] + emc_e3 [x] + pocket_reanalysis [x]                     (CPU/$0, done)
          │
RUNG1  valA_mini [x] ──[GO]──►                                            (cheap kill-switch, ~$12)
          │
RUNG2  step1_pilot [x] ∥ valB_mini [~]  ──[GO?]──►                        (~$85; all-binding graded edge)
          │
RUNG3  valB_full cube + nrv04_feasibility [~]  ──[GO?]──►                 (~$300; valA_full SKIPPED — cite OpenFE)
          │
RUNG4  step1_fanout ∥ nr4a_differential_atlas($0) ──► nrv04_retrospective ──[concordant?]──►   (~$500)
          │
RUNG5  orientation_basin_search($0-50) ──► wedge PILOT leg($40-90) ──[★ cheap gate: WEDGE?]──►  (decide for ~$40-140)
          │        └── NO loss on pilot ⇒ STOP: publish honest causal negative (no full cycle, no tail)
          │        └── loss ⇒ complete full reciprocal cycle ($100-350, the causal RESULT) + tail
          │
       inverse_linker_design($0) ──► ternary_ensemble_refine ──► local_ternary_fep            (~$1,235; flagship tail)
          │
RUNG6  fold ──► redteam ──► post/submit                                   ($0)

OPTIONAL/HELD (only with an explicit nod): dg_open_paralogue, abfe_conditional
```

**Right now (2026-07-24):** Rungs 0–1 are done; Rung 2–3 are the live front — **valB_mini** (Wurz all-binding
graded edge) and the **NR-V04 covalent feasibility panel** are running on Vast (that panel is the source of the
measured 3090 pricing above). The next **$0 CPU work I'll build without asking is the NR4A differential surface
atlas** (RUNG 4) — free, warranted, and itself a cheap early NO-GO. **Nothing with a GPU price launches without an
explicit go.** The key upcoming decision is the **★ 5a-KS causal kill-switch (~$100–350 est.)**: a confirmed NR4A3
wedge unlocks the ~$500 flagship tail; no wedge ⇒ we stop and publish the honest causal negative.
