# STRATEGY — the NR4A3-selective degrader paper

> # ★ GOLD-STANDARD SINGLE SOURCE OF TRUTH FOR THE RESEARCH STRATEGY ★
> **This file is THE strategy** — the authoritative plan for the repo's #1 research program, the
> **NR4A3-selective degrader paper**, and what CLAUDE.md and README.md point to for "what's the plan / what's
> next / what does each step cost." If any other doc (the schedule JSON, a strategy note, a manuscript section, a
> commit message) conflicts with this file, **this file wins** — reconcile the other doc to it.
>
> **Keep it current:** when work lands, update the stage's `[ ]/[~]/[x]` status here AND the mirrored `status` in
> [degrader-paper-schedule.json](research/manuscripts/degrader-paper-schedule.json) (its milestone `id`s match the
> stage tags below one-for-one; that JSON is a machine MIRROR of this file, not a competing source).
>
> **Companion docs (detail only, subordinate to this file):**
> [research/compute/pricing.md](research/compute/pricing.md) — ★ PRICING single source of truth, every cost line
> linked to its justifying test · [reviewer verdict](research/manuscripts/nr4a3-degrader-reviewer-revisions-2026-07-15.md)
> (verbatim) · [ternary-first strategy note](research/manuscripts/nr4a3-degrader-strategy-ternary-first.md)
> (biological/chemotype rationale) · [the manuscript](research/manuscripts/nr4a3-degrader-paper.md) itself.

---

## Program and thesis

The goal is the **state of the art of what in-silico methods can do for an NR4A3-selective degrader** — a
complete, rigorous, honest computational characterization for extraskeletal myxoid chondrosarcoma (EMC, driven by
the **EWSR1::NR4A3** fusion), pursued with **no wet lab**. Every result is reported at its true weight; the
deliverable is a preprint + journal submission (ChemRxiv/JCIM) plus targeted outreach, not a ship-when-adequate
minimum. This program is ≈70–80% of repo effort; the broader EMC route portfolio (fusion-junction ASO and other
routes as support/backup) is context beneath it — see
[emc-treatment-strategy.md](research/manuscripts/emc-treatment-strategy.md) and [IDEAS.md](research/IDEAS.md).

**Thesis.** Paralogue selectivity, where achievable, emerges **jointly** from a modest binary warhead preference,
ternary cooperativity, and ubiquitination-compatible geometry — not from binary pocket selectivity alone. Close-
paralogue degrader selectivity is created at the **induced target–E3 interface** and differential lysine geometry
(as in BRD4-vs-BRD2/3, CDK6-vs-CDK4, p38 isoforms), never at the conserved warhead pocket, and in every landmark
case it was *discovered then rationalized by a solved ternary structure* — never predicted blind. There is no
validated prospective selectivity predictor in the field, and AKT1/2/3 is the cautionary null (isoforms too
homologous → only pan-degraders).

The program is therefore **orientation-first**: search for a relative target–E3 orientation that forms an
NR4A3-distinctive neo-interface *and* positions E2~Ub productively, prove it causally with reciprocal
target-surface mutation cycles, and **STOP before the flagship spend if no robust wedge survives** — publishing
the honest negative, itself a defensible novel result. The final deliverable is a **computationally prioritized,
structure-defined, retrosynthetically annotated candidate set with an identified causal selectivity mechanism —
degradation experimentally unvalidated.**

## Honest scope and language discipline (apply everywhere, including the manuscript)

Everything is **conditional on the hypothesized cmpd19 binary pose × the chosen receptor frame** — a *double*
conditionality; a wedge surviving only one poorly-supported pose is penalized or dropped. Right-size every claim:

- "selective hit" → **"predicted selective candidate"**; "NR4A3-selective" → **"predicted NR4A-paralogue-selective"**
- "does bind at all" → **"is compatible with the hypothesized conditional bound state"**
- "recovered degradation" → **"produced a surrogate score concordant with the reported outcome"**
- "synthesis-ready matrix" → **"a computationally prioritized, structure-defined, retrosynthetically annotated
  candidate matrix for synthesis and experimental testing"** (only earned once exact structures/stereochem,
  exit-vector chemistry, routes, building-block availability, and physicochemical assessment exist).
- **Never imply** proteome-wide selectivity, EMC efficacy, safety, a therapeutic window, or clinical readiness.
  The parent cmpd19 study reported transcriptional effects **including MYC induction**, so parent-warhead
  pharmacology is a **potential liability**, not evidence of benefit.
- **Novelty is incremental, not landmark.** All-atom alchemical ternary-cooperativity FEP — the same
  `ΔΔG_coop = ternary − binary` cycle, including VHL–BRD4/MZ1 and paralogue-selectivity applications — is an
  active published area (Chen 2023; *JCTC* 2025 `10.1021/acs.jctc.5c00064` / `5c00736`; *JCIM* 2024
  `10.1021/acs.jcim.4c01227`). The paper must cite and benchmark against this prior art. An open-source
  OpenFE-based implementation + the honest NR4A application is an incremental methods contribution.

---

## Validation architecture (the five requirements)

These come from the external reviewer's conditional approval ([verbatim
verdict](research/manuscripts/nr4a3-degrader-reviewer-revisions-2026-07-15.md)) and govern what any result is
allowed to claim.

1. **Three DIFFERENT validations — never let one stand in for another.**
   - **(A) Accuracy control** — a compact *public* RBFE benchmark (measured ΔΔG + supported poses) through the
     *exact* container / protocol / force field / water model / sampling / analysis used for NR4A. Cycle closure,
     fwd/rev agreement, and MBAR overlap are **precision diagnostics, NOT accuracy** — a closed cycle can be
     systematically wrong.
   - **(B) Target-specific precision** — the cmpd19 RBFE, framed as *conditional relative free energies for a
     hypothesized cmpd19 mode within preselected open NR4A conformers.* It tests reproducibility and
     receptor-sensitivity, **not** binding-model correctness (cmpd19 has no measured affinity, no pose).
   - **(C) Ternary known-answer control** — a system with an experimental ternary structure + measured
     binary/ternary affinity/cooperativity + an analogue series (VHL–BRD4 or VHL–SMARCA2). **NR-V04 is a
     biological-selectivity holdout, not the method calibrator.**

2. **Cryptic-pocket thermodynamics are conditional.** An affinity computed in a pre-opened pocket is
   ΔG_bind|open, not the observable ΔG_bind,obs ≈ ΔG_open + ΔG_bind|open. Each paralogue can have a **different
   opening penalty**, so comparing binding only in matched open receptors can miss or REVERSE selectivity.
   Either integrate a converged **ΔG_open per paralogue**, or report everything **explicitly conditional** on the
   chosen open states. Pocket collapse in MD is *evidence the state is unstable*, not an auto-fail; restraint free
   energies must be included or the result stays conditional; **do not** claim "under-sampling means true binding
   is likely stronger" (bias runs both ways). Never pool conformers of unknown population as equally weighted;
   use Boltzmann weighting where estimable, else report sensitivity ranges — never a synthetic "ensemble affinity."

3. **ABFE is HELD and reframed.** T4L-L99A·benzene is an implementation smoke test, **not a transferable
   offset** — report raw ABFE, report the T4L discrepancy separately, apply no offset. ABFE does **not** prove
   cmpd19 "binds at all"; it only asks whether the hypothesized pose is thermodynamically plausible under the
   modeled assumptions. Not worth running until the accuracy benchmark passes, the opening penalty is handled,
   and multiple poses are treated. Step 8 cannot "consume the anchor ABFE per construct" — linker/recruiter
   attachment alters the bound ensemble, so free-cmpd19 ABFE ≠ each degrader's binary affinity.

4. **NR-V04 is covalent.** Celastrol binds NR4A1 **covalently via C551**, so NR-V04 does not validate the
   noncovalent machinery used for cmpd19, and its selectivity may be largely **target-engagement**, not ternary
   cooperativity. Model a **preformed covalent adduct**; add a **noncovalent-vs-covalent sensitivity analysis**,
   an **NR4A1 C551A / nonreactive control**, and **warhead-only + active/inactive recruiter** controls; use
   scoring rules preregistered on control (C). Report only **directional concordance** with the reported
   NR4A1-degraded / NR4A2·3-spared outcome — never "recovered degradation."

5. **The prospective stage is hypothesis PRIORITIZATION, not scoring.** Replace any tunable scalar with **staged
   gates + a Pareto/constraint-satisfaction front** (binary plausibility → ternary thermodynamic/ensemble →
   linker strain → ubiquitination geometry → physicochemical → robust selection), with uncertainty on every
   axis. Model the **real biological object, EWSR1::NR4A3** (not an isolated LBD): fusion-context ensemble;
   lysines **outside** the LBD (hinge, DBD, fusion partner); public EMC VHL/CRBN expression; **full CRL/E2~Ub
   geometry ensembles**. Ternary formation is necessary, not sufficient — productive lysine positioning is a
   distinct requirement.

### Why Val A is nearly free but Val B is load-bearing

- **Val A (binary RBFE accuracy) — a citation, not a paid benchmark.** We run OpenFE's *standard*
  RelativeHybridTopology protocol, already benchmarked (~1.7 kcal/mol over 58 public systems). The only thing
  that had made it non-citeable was a self-inflicted deviation — the RBFE env shipped without AmberTools, so
  am1bcc charging failed and fell back to the NAGL surrogate. With AmberTools added and `am1bcc` restored (the
  same fix propagated to the ternary engine, so binary/ternary legs share charges and the cooperativity cycle's
  cancellation holds), we **cite OpenFE** and run only a ~$0–15 build-consistency smoke.
- **Val B (ternary cooperativity) — genuinely needed, for pipeline-validation.** The general approach is citeable
  (see prior art above), but you never certify your own container / force field / charge model / ternary wiring
  by pointing at someone else's engine's benchmark. NR-V04 cannot calibrate it (no solved ternary; celastrol is
  covalent, so it doesn't even exercise the noncovalent morph). The only way to know our cooperativity numbers
  mean anything is to run a known-answer PROTAC (VHL–BRD4 / VHL–SMARCA2) through our own pipeline. **Val B-mini is
  the highest-value dollar in the plan** — the cheapest gate on the entire prospective ladder.

---

## The prospective stage: orientation-first inverse design

The molecule-first approach — enumerate a fixed {warhead×exit×ligase×linker} matrix, model each ternary, score,
and hope the Pareto front contains a selective degrader — is a well-controlled lottery: it *verifies* selectivity
if already present but never asks the design question. The stage is reorganized **orientation-first**:

```
paralogue surface differences → selective interface BASINS → productive CRL geometry
    → linker requirements → candidate molecules
```

This removes blind linker guessing and preserves everything requirement 5 mandates (Pareto/uncertainty,
EWSR1::NR4A3 fusion context, lysines beyond the LBD, full CRL/E2~Ub ensembles). Five load-bearing pieces:

1. **A paralogue-differential surface atlas (free, CPU).** NR4A1/2/3 in a **matched** ensemble — homologous
   frames, identical pose hypotheses, protonation, target–E3 transforms, and sampling — mapping E3-reachable,
   solvent-exposed, divergent residues and lysines (LBD / hinge / DBD / fusion partner, separately). Output is a
   discrimination **map**, not three receptor models; states are explicit scenarios unless populations are
   defensibly estimable.
2. **Orientation-space search before real linkers.** For each ligase, sample many relative transforms of
   VHL/CRBN around the warhead-bound target under a flexible linker-reach restraint; keep only interfaces that are
   favorable on NR4A3 and systematically weaker/frustrated on NR4A1/2, bridgeable, clash-free, ensemble-compatible,
   and place an accessible lysine in a productive transfer region. Cluster into **~3–8 basins per ligase**.
3. **Wedges proven by reciprocal mutation cycles — the primary causal test.** For a target-surface mutation *m*,
   `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` (the binary leg subtracts mutation effects from the
   target–warhead complex, isolating the recruited-interface effect). A strong wedge shows a favorable NR4A3
   interface, **loss** on NR4A3→NR4A1/2 mutations, **partial gain** on reciprocal NR4A1/2→NR4A3 mutations,
   persistence across frames, and a recognizable steric/electrostatic/H-bond mechanism. This is far stronger than
   observing ΔG_ternary,3 < ΔG_ternary,1.
4. **Separate ACCESSIBILITY from STABILITY.** Estimate `P(B_k | d, s)` (can the linker reach and hold basin *k*?)
   separately from `ΔG_coop(d, B_k, s)` (is the orientation plausible?). A favorable basin the linker rarely
   accesses is irrelevant.
5. **Robust constraint-satisfaction selection.** A candidate advances only if it satisfies preregistered
   constraints across a required fraction of scenarios (binary non-destabilization; basin populated in replicated
   MD; NR4A3 advantage over **both** paralogues under perturbation; ≥1 NR4A3-specific contact survives
   counterfactual mutation; ubiquitin near an accessible NR4A3 lysine in a meaningful CRL-conformer fraction;
   credible unstrained linker). Rank by `P_d = P(all constraints hold)`, robust to dropping any one favorable
   scenario — this kills the best-of-N winner's-curse artifact a raw Pareto set still admits.

**The hard kill-switch — tiered, cheapest-decisive-first.** No causally-confirmed NR4A3 wedge ⇒ **STOP**: no
linker matrix, no ensemble refinement, no flagship spend; publish *"we mapped orientation space and no robust
NR4A3-discriminating, ubiquitination-compatible basin survives causal testing."* The *decision* to commit the
flagship is cheap, not a gate on the whole tail:

- **Tier 1 — atlas ($0 CPU):** no E3-reachable divergent surface ⇒ STOP for free.
- **Tier 2 — basin nomination ($0–50):** no basin even nominally discriminates NR4A3 ⇒ STOP cheaply. Cheap
  scoring has poor S/N for *small* differences, so it *nominates* — a gross absence of signal is an informative
  NO-GO, but it is not trusted to kill a real small wedge.
- **Tier 3 — pilot ONE alchemical mutation direction (~$5–10):** the single most-decisive leg first (3→1). No
  effect ⇒ STOP. The full reciprocal cycle (~$15–30) runs only on a passing pilot and is the paper's **primary
  causal RESULT**, not gate overhead.

---

## Spending rules

1. **No pre-authorization, no pre-staging.** Nothing is ever queued to auto-fire. Every GPU run is presented at
   its gate with (a) the prior step's result, (b) a pinned cost (from realized GPU-h, not a guess), and (c) a wait
   for an explicit trimcrae "go." Only $0 CPU/CI work runs without a nod.
2. **Spend-gated ladder, cheapest-decisive-first.** The cheapest run that could kill the paper comes first; each
   rung's bigger spend unlocks only if the previous, cheaper rung looks promising. Never pay for an expensive
   stage on a hypothesis a cheap stage could have falsified.
3. **GO/NO-GO after every priced rung.** Each rung ends with an explicit test; NO-GO = stop or pivot.
4. **Every step is priced bottom-up per edge** on measured Vast-4090 bases (below); pricing provenance lives in
   [pricing.md](research/compute/pricing.md).

## GPU economics (measured; full provenance in pricing.md)

**All production runs go on Vast — RTX 4090 (default) or RTX 3090 (fallback).** GCP L4 / SageMaker / Modal are
not the go-forward basis. Pick by **$/ns** (`$/hr ÷ (ns_per_day ÷ 24)`), never headline $/hr.

- **Card: the 4090 wins $/ns at every size** (measured `gpu_md_bench`: 4090 1549 / 669 / 175.6 ns/day at 35k /
  85k / 444k atoms; 3090 72.5 @444k = **2.42× slower** for only ~9% more $/hr). This includes the 466k covalent
  panel, refuting the a-priori "large system → 3090" rule (at ≤466k, OpenMM PME is still compute-bound, so the
  4090's ~2× compute swamps the ~8% bandwidth gap). A compute-bound alchemical edge on the 3090 costs roughly
  **~1.5–2× the 4090 $/edge**; use the 3090 only when 4090 capacity is short. VRAM is never the constraint
  (≥24 GB floor is ample).
- **Measured per-edge bases (Vast 4090):**
  - **RBFE binary edge** (complex+solvent, ~35k atoms) ≈ ~5–6 GPU-h ≈ **~$0.6–1.4**.
  - **Ternary cooperativity edge** (3-replica, ~146,509 particles, 16 windows) ≈ **~$3–6** (from the parallel
    real `valB_mini` on L4 ÷ a ~2.3× card ratio; the L4-on-demand lane it ran on bills ~10× higher, ~$37, which
    is *not* a go-forward cost). A direct Vast-4090 firm-ternary measurement was attempted but NaN's at warmup
    (softcore conditioning of the rough homology model — pre-equilibration got it from λ-state 0 to state 5 but
    not clean); the proven `valB_mini` lane remains the ternary source of record until that conditioning is
    ported to the Vast lane.
  - **Endpoint-MD leg** (~466k atoms) ≈ **~$0.45**.
- **Whole gated ladder ≈ ~$270 mid-range (~$150–450), GO at every gate** (optional/HELD ΔG_open + ABFE excluded,
  ~$200–500 more if invoked). The only real swing is the **ensemble-MD leg count** (5c + retrospective), not
  per-edge cost; card choice is the lever on GPU-h-heavy stages.

*Operational Vast setup (bid = `min_bid × 1.5` to hold the slot; pin OpenMM to CUDA 12.6; the OpenFE image
`triskit23/nr4a3fep:latest`; the `bench` / `firm` tooling in `nrv04_vast_launch.py`) is documented in
[pricing.md](research/compute/pricing.md) and `research/modalities/gpu_backend.py` — not repeated here.*

---

## THE ORDERED PLAN (spend-gated) — read top-to-bottom for "what's next"

Legend: `[ ]` pending · `[~]` in progress · `[x]` done · `[–]` skipped. `∥` = parallelizable. **Price** = spot $
for that step on Vast 4090; **Cum.** = running total if GO at every gate to here (mid-range).

### RUNG 0 — free / already done (~$0)

- **`[x]` Charge-model fix — am1bcc on the standard path** — **$0.** Added `ambertools>=23` +
  `partial_charge_method="am1bcc"` (NAGL retained as env-override fallback); propagated to the ternary engine so
  binary/ternary legs share charges. Puts us on the documented reference method → cite OpenFE.
- **`[x]` Step 0 — RBFE infra shakeout** — **~$1–2 · PASSED.** One OpenFE edge ran end-to-end via the spot-safe
  split and returned a converged **ΔG_morph = −48.75 ± 0.57 kcal/mol** (MBAR); am1bcc charging and the
  warmup→production→commit/restore driver are GPU-validated. **GO.**
- **`[x]` EMC E3-ligase expression** — **$0.** All 10 components of both CRL2^VHL and CRL4^CRBN are broadly
  expressed (HPA), so the VHL-vs-CRBN choice is **not** constrained by machinery availability — decide on
  geometry/selectivity. (No EMC line in HPA — general mesenchymal availability.)
- **`[x]` Pocket-tracking re-analysis** — **$0.** Harmonized detection folded into the paper's Gate-2 wording:
  8XTT 19/20 frames detected (3 ≥ D\*=0.53); release continuations druggable in 59% of frames pooled.

### RUNG 1 — reference-reproduction smoke (mostly a citation)

- **`[x]` Validation A-mini — build-consistency smoke + cite OpenFE** — **~$0 · Cum. ~$2 · PASS/GO.** The public
  TYK2 `ejm31→ejm42` edge (both legs, 5 ns × 12 windows) gave **ΔΔG_bind = +0.366 vs exp −0.24 → abs err 0.61
  kcal/mol**, inside the 2.0 tolerance. Our container reproduces a known ΔΔG on the standard am1bcc method → cite
  OpenFE's published ~1.7 kcal/mol accuracy. Does not touch NR4A. **GO to Rung 2.** *(If am1bcc is ever forced to
  NAGL for a ligand, Val A reverts to a paid ~$25 NAGL benchmark.)*

### RUNG 2 — cheap precision + cheap probes *(only if Rung 1 = GO)*

- **`[x]` Step 1 pilot — cmpd19 conditional RBFE** — **~$1–3 (1–2 RBFE edges) · Cum. ~$4.** First edge
  `zaienne_cmpd19 → cw_ev_5nh2` (5-Br→5-NH₂) converged: complex ΔG_morph −29.68 ± 0.24, solvent −31.52 ± 0.26 →
  **ΔΔG_bind = +1.84 kcal/mol** (the 5-NH₂ analogue ~1.8 kcal/mol weaker *in the modeled opened pocket*). Proves
  the congeneric-RBFE pipeline converges on the real NR4A3 system without pocket collapse — the pilot's crux is
  cleared. Reproducibility replicas + pose/state sensitivity are carried forward as **fan-out inputs** (they
  refine per-edge `n_windows` and the conditional caveat, and gate the fleet). This is statistical convergence on
  a *hypothesized* pose, **not** an accuracy claim.
- **`[~]` Validation B-mini — all-binding graded cooperativity edge** — **~$3–6 · Cum. ~$9.** The Wurz SMARCA2–VHL
  **cmpd 1→4** all-binding graded edge (α 12.8→2.6 ≈ +0.94 kcal/mol; both endpoints are productive binders — the
  cleanest first calibration). Exercises the bespoke `ΔΔG_coop = ternary − binary` cycle that cannot be cited
  away. **GO/NO-GO:** correct sign, CI excludes 0, within ~1.0 of the measured Δα, repeats + fwd/rev agree → GO to
  Val B-full. valB_mini gates valB_full only — it does **not** authorize the NR4A matrix; until valB_full passes,
  NR4A ternary scores are **exploratory**. *(In progress on GCP L4; a direct Vast-4090 timing run is hardening
  the per-edge cost. The cis-epimer PROTAC-2 edge is demoted to the negative-endpoint stress module of the cube
  below — a pass forced by holding an unstable pose is not a pass.)*

### RUNG 3 — expand the benchmarks *(only if Rung 2 probes look promising)*

- **`[–]` Validation A-full (10–20 edges) — SKIPPED · saves ~$50–140.** valA_mini reproduced the known ΔΔG cleanly
  on the standard am1bcc method, so a full re-derivation is redundant with OpenFE's published benchmark. Framing
  that must hold: cite OpenFE for accuracy; present valA_mini as a single-edge build-consistency confirmation, not
  a standalone benchmark. Re-open only if am1bcc is forced onto NAGL.
- **`[ ]` Validation B-full — component-calibration cube** — **~$20–60 · Cum. ~$49.** Four separately-calibrated
  modules, each with its own pass/fail (a failed module → qualitative-only; no blanket "validated"): (1) a second
  all-binding graded cooperativity edge; (2) ternary pose recovery (co-fold, ~$0); (3) paralogue discrimination on
  a public system (the direct analogue of the NR4A ask); (4) productive-vs-unproductive ubiquitination geometry
  (full-CRL MD). Plus the cis-epimer negative-endpoint stress module. **GATE:** the prospective ladder never runs
  unless the **cooperativity + paralogue-discrimination** modules pass.
- **`[x]` NR-V04 covalent feasibility panel — DONE (17/18)** — **~$8.** Covalent celastrol–NR4A1 (C551) adduct +
  C551A + noncov/cov sensitivity + warhead/recruiter controls; 18 legs (6 systems × 3 seeds), 6 ns each, ~466k
  atoms. **Result (feasibility + control-discrimination only, no selectivity/efficacy claim):** recruitment is a
  weak discriminator (co-fold seeds contact in all arms), so interface-RMSD stability is the readout —
  recruiter_active 3/3 stable vs epimer 1/3 (a discrimination the static co-fold could **not** produce); covalent
  NR4A1 2/3 = noncovalent 2/3 (covalency buys feasibility, not extra stability); C551A 1/3. Report directional
  concordance only. **GO** — covalency did not swamp the signal.

### RUNG 4 — warhead map, differential atlas, retrospective gate

- **`[ ]` Step 1 fan-out — cmpd19 congeneric map, 8-wide** — **~$12–26 (≈19 RBFE edges × ~$0.6–1.4) · Cum. ~$76.**
  Full congeneric map across conformer panels + matched paralogues + microstates, as conditional hypotheses with
  sensitivity ranges → the warhead + exit-vector inputs the inverse-design stage consumes. **Gate:** Val A
  satisfied (cite OpenFE) AND the Step 1 pilot behaved (with its replicas + pose/state sensitivity).
- **`[x]` NR4A differential surface atlas — DONE · $0 · GATE PASS/GO.** Matched Shrake–Rupley SASA + BLOSUM62
  alignment over NR4A{3,1,2} opened models → **46 differential-surface handles** (exposed × divergent ×
  character-changing), 15/15 LBD lysines exposed; per-residue identities reproduce the canonical map 148/148. A
  differential surface exists to steer an E3 against (distinct from the ~70% pocket hotspot), so the 5a
  orientation-basin search is warranted. *(Optional add-on: matched NR4A1/2 MD ensembles ~$10–40 to test which
  handles survive dynamics.)*
- **`[ ]` NR-V04 retrospective — preregistered holdout** — **~$25–55 (NR4A1/2/3 ternary ensembles; swing item,
  scales with ensemble-MD leg count) · Cum. ~$115.** Full ensembles through the pipeline, no tuning, epimer
  control; report directional concordance only. **Gate:** Val B-full + NR-V04 feasibility + Step 1 fan-out.
  **GO/NO-GO:** at least directionally concordant with the NR4A1-degraded / NR4A2·3-spared outcome → GO to the
  prospective ladder; discordant → the ladder is not justified, publish the honest negative.

### RUNG 5 — orientation-first prospective ladder *(the flagship, gated mid-ladder by the causal kill-switch)*

- **`[ ]` 5a · Orientation-basin search** — **~$0–50 (CPU $0 + optional MM-GBSA rescore) · Cum. ~$140.** Broad
  VHL/CRBN transform sampling; matched 3-paralogue scoring; cluster into ~3–8 basins/ligase; cheap counterfactual
  screen to nominate wedges.
- **`[ ]` 5a-KS · Wedge confirmation — ★ pilot-first KILL-SWITCH + causal RESULT** — **Decision ~$5–10 · full
  cycle if GO ~$15–30 · Cum. to decision ~$148.** Pilot ONE direction first (3→1 = one binary RBFE + one ternary
  edge). **No interface loss ⇒ STOP** — publish the honest causal negative, skip the ~$30–190 refinement tail.
  Loss ⇒ complete the full reciprocal cycle (add 3→2 + reciprocal 1/2→3) — the paper's primary causal RESULT.
- **`[ ]` 5b · Inverse linker design** — **~$0–20 (mostly $0 CPU) · Cum. ~$180.** For each confirmed basin, derive
  linker requirements (endpoint distance, exit-vector dihedral, strain, reach), enumerate a virtual library,
  filter by basin fidelity, annotate exact structures + synthetic feasibility → **~12–20 virtual constructs** (the
  "24–36" now bounds this virtual set, not a hand-built grid).
- **`[ ]` 5c · Explicit ternary-ensemble refinement** — **~$20–150 (endpoint MD, dozens–~200 legs; the largest
  single GPU spend and a swing item) · Cum. ~$250.** Replicated ternary + full CRL/E2~Ub MD across target states,
  linker conformers, and in-basin poses; matched NR4A1/2/3; separate accessibility from stability; robust
  constraint-satisfaction filtering → **~4–8 constructs** nondominated under scenario + model uncertainty.
- **`[ ]` 5d · Local ternary FEP** — **~$9–36 (3–6 ternary edges) · Cum. ~$272.** Alchemy **only** within a
  retained basin (both endpoints plausibly bound, modest congeneric change). Refines the matched final series →
  **~6–12** with ≥2 mechanistic wedges, ≥2 linker architectures, VHL/CRBN only where both survive, explicit
  negative controls. **Deliverable** = the prioritized, structure-defined, retrosynthetically annotated candidate
  set with an identified causal selectivity mechanism — degradation experimentally unvalidated.

### OPTIONAL / HELD — only if a specific claim needs them AND a budget nod is given

- **`[ ]` ΔG_open per paralogue** — **~$120–300.** Only to make affinity/selectivity *unconditional*; otherwise
  report conditional on the open state ($0, fully defensible).
- **`[ ]` Conditional ABFE (pose-plausibility)** — **~$80–200.** Raw values, T4L discrepancy separate, no offset,
  does not prove binding. Launch only with an explicit nod after everything above.

### RUNG 6 — write & ship (~$0)

- **`[ ]` Fold results into paper** — language discipline; QM/torsion validation at linker junctions;
  physicochemical + retrosynthetic assessment; re-render figures.
- **`[ ]` Final red-team + review-response.**
- **`[ ]` Post + submit** — OUTWARD-FACING, needs trimcrae sign-off.

---

## Spend summary — running total (measured Vast-4090 bases)

Every per-edge base is measured, so the ladder totals cleanly. **Whole gated ladder, GO at every gate, mid-range:
~$270 (range ~$150–450).** Optional/HELD (ΔG_open, ABFE) excluded (~$200–500 more). The only real swing is the
**ensemble-MD leg count** (5c + retrospective); the kill-switch stops most NO-GO paths under ~$150.

| Rung | GPU work | Step $ (mid) | Cum. |
|---|---|---|---|
| 0 · infra + free CPU (DONE) | step0 + emc_e3 + pocket | ~$2 | ~$2 |
| 1 · Val A smoke (DONE) | 1 public RBFE edge | ~$0 | ~$2 |
| 2 · pilot + Val B-mini | 1–2 RBFE edges + 1 ternary edge | ~$2 + ~$5 | ~$9 |
| 3 · Val B cube + NR-V04 feasibility (feas. DONE) | 2–3 ternary edges + CRL-MD; covalent panel | ~$40 + ~$8 | ~$57 |
| 4 · fan-out + atlas(DONE) + NR-V04 retro | ≈19 RBFE edges + NR4A1/2/3 ternary ensembles | ~$19 + ~$40 | ~$115 |
| 5a · basin + **KILL-SWITCH pilot** | basin($0–50) + one mutation direction | ~$5–60 | ~$148 |
| 5 (if GO) · cycle + linker + ensemble + local FEP | reciprocal cycle + ensemble MD + within-basin FEP | ~$45–215 | ~$272 |
| Optional ΔG_open / ABFE (HELD) | — | +$200–500 | *(excl.)* |

Notes: the restructuring buys **causal evidence** (mutation cycles + ensemble MD + local FEP) over
co-fold-and-score — higher information per dollar, not lower. A non-viable paper dies for ~$2 at Val A, or free at
the atlas (which passed). The kill-switch decision is ~$5–60; no wedge ⇒ stop with a publishable causal negative.

## Dependency spine

```
RUNG0  step0 [x] + emc_e3 [x] + pocket [x]                              (CPU/$0, done)
          │
RUNG1  valA_mini [x] ──[GO]──►                                         (cite OpenFE; Cum ~$2)
          │
RUNG2  step1_pilot [x] ∥ valB_mini [~]  ──[GO?]──►                     (Cum ~$9)
          │
RUNG3  valB_full cube + nrv04_feasibility [x]  ──[GO?]──►              (valA_full SKIPPED; Cum ~$57)
          │
RUNG4  step1_fanout ∥ atlas [x]($0) ──► nrv04_retrospective ──[concordant?]──►   (Cum ~$115)
          │
RUNG5  basin_search($0–50) ──► wedge PILOT leg(~$5–10) ──[★ cheap gate: WEDGE?]──►
          │      └── no loss ⇒ STOP: publish honest causal negative (no cycle, no tail)
          │      └── loss ⇒ full reciprocal cycle (~$15–30, the causal RESULT) + tail
          │
       inverse_linker($0) ──► ternary_ensemble_refine ──► local_ternary_fep   (Cum ~$272)
          │
RUNG6  fold ──► redteam ──► post/submit                                ($0)

OPTIONAL/HELD (explicit nod only): dg_open_paralogue, abfe_conditional
```

**Current front:** Rungs 0–1 done; the NR-V04 covalent feasibility panel and the NR4A differential surface atlas
are done; **valB_mini** is finishing (a direct Vast-4090 ternary timing run is hardening its per-edge cost).
Nothing with a GPU price launches without an explicit go. The next major decision is the **5a-KS causal
kill-switch** (~$5–60): a confirmed NR4A3 wedge unlocks the refinement tail; no wedge ⇒ stop and publish the
honest causal negative.
