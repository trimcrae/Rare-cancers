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
> (biological/chemotype rationale) · [**ternary-selectivity strategy revision
> 2026-07-24**](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md) (the evidence and
> full reasoning behind the mechanism-first search and the six cost levers folded in below) ·
> [the manuscript](research/manuscripts/nr4a3-degrader-paper.md) itself.

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

**★ MECHANISM-FIRST (revised 2026-07-24 — supersedes "orientation-first" as the SEARCH ORDER; the thesis above
is unchanged).** Selectivity mechanisms are not interchangeable, and the program was pursuing the hardest one
exclusively. Two classes:

- **MARGINAL** — the paralogue is thermodynamically disfavoured. This is the induced-interface wedge. A useful
  degradation window needs **~2.0 kcal/mol** of true margin (median over 27 potency scenarios, range 1.75–2.25;
  [`selectivity_margin_model.py`](research/modalities/selectivity_margin_model.py)), against a best-case
  **resolvable** difference of **1.12 kcal/mol** (replicate SD 0.7, n = 3) and a method accuracy of ~1.7 kcal/mol
  RMSE — which does not even cover the NAGL ternary lane. Replicates shrink precision, not accuracy. **This axis
  is a confirmation tool operating near its limit, not a discovery tool.**
- **CATEGORICAL** — the paralogue is structurally *incapable*. NR4A3 carries reactive residues that BOTH
  paralogues lack, verified from full-length UniProt with two independent aligners
  ([`nr4a_paralogue_unique_residues.py`](research/modalities/nr4a_paralogue_unique_residues.py)):
  **C397** (NR4A1 N363 / NR4A2 S363; RSA 0.395, 10.9 Å from the cryptic pocket — exit-vector reach), C420, C559;
  and exposed unique lysines **K572** (RSA 0.879), **K518**, **K592**, all 11–16 Å from the pocket, the same band
  as the conserved ones — so an E3 can be steered onto a unique lysine instead of a shared one. At **zero**
  thermodynamic margin these give 0.82 (unique lysine) and 0.92 (covalent capture, time-integrating form) on the
  window metric where the interface-only null gives 0.185. **Precedent: the field's one demonstrated case of
  NR4A-family-selective degradation, NR-V04, is most parsimoniously explained by a paralogue-unique cysteine —
  NR4A1 Cys551, which NR4A3 lacks (T579).** That covalency remains a genuine confound for the retrospective
  (below); it is *also* the reciprocal handle this program should use.

The program is therefore **mechanism-first, then orientation**: rank basins by whether they place an electrophile
at an NR4A3-unique cysteine and whether their E2~Ub transfer zone covers a unique lysine rather than a conserved
one; use interface thermodynamics to **rank within** the surviving set, never to create selectivity on its own;
test causality with a matched-pair cycle; and **STOP before the flagship spend if no mechanism survives** —
publishing the honest negative, now stronger because it rules out three mechanisms instead of one. The final
deliverable is a **computationally prioritized, structure-defined, retrosynthetically annotated candidate set
with an identified causal selectivity mechanism — degradation experimentally unvalidated.**

*Checked and reported weak, not quietly dropped:* the EWSR1 moiety of the fusion contributes only **1 lysine**
(residues 1–264) or 2 (1–349) — the low-complexity domain is Lys-poor — so fusion-lysine-directed ubiquitination
is a thin handle and is **not** a design axis. It stays a modelling scenario only.

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

- **Val A (binary RBFE accuracy) — a citation, not a paid benchmark, FOR THE BINARY LANE ONLY.** We run OpenFE's
  *standard* RelativeHybridTopology protocol, already benchmarked (~1.7 kcal/mol over 58 public systems). The only
  thing that had made it non-citeable was a self-inflicted deviation — the RBFE env shipped without AmberTools, so
  am1bcc charging failed and fell back to the NAGL surrogate. With AmberTools added and `am1bcc` restored, the
  **binary RBFE lane** is on the documented reference method → we **cite OpenFE** and run only a ~$0–15
  build-consistency smoke (valA_mini, done).

  **⚠ The charge model is NOT shared across lanes — do not state that it is (corrected 2026-07-24).** An earlier
  version of this section claimed the am1bcc fix "propagated to the ternary engine, so binary/ternary legs share
  charges." That is **false as run.** The lanes split:

  | Lane | Charge model | Evidence |
  |---|---|---|
  | Binary RBFE (`nr4a3_rbfe.py`) | **am1bcc** | code default; valA_mini/step0/step1_pilot all ran am1bcc |
  | Ternary FEP (`nr4a3_ternary_fep.py`) | **NAGL** | `gpu-ternary-fep-gcp.yml:34,74` default `nagl`; live valB leg log 2026-07-24 shows `CHARGE_METHOD: nagl` |
  | Endpoint / covalent MD | **NAGL** | `md_settings.py:60` `CHARGE_METHOD = "nagl"` |

  The split is **physically forced, not sloppiness**: AM1-BCC via AmberTools `sqm` is intractable on PROTAC-sized
  ligands — measured 2026-07-22, `sqm` ran **>85 min on the 166-atom NR-V04 recruiter without converging**
  (`md_settings.py:53–60`). NAGL is an ML surrogate *for* am1bcc, so this is a defensible substitution, but it is a
  **different Hamiltonian** and must be handled explicitly:

  1. **ΔΔG_coop is SAFE.** Both morphs of the cooperativity cycle (`ternary − binary-of-the-same-PROTAC`) run
     inside the ternary lane at the same `CHARGE_METHOD`, so the charge model cancels. The cycle's cancellation
     argument holds *within* a lane — which is all it ever needed.
  2. **Any CROSS-LANE subtraction is NOT safe** — see the 5a-KS note in RUNG 5. A quantity built as
     `(ternary-lane leg) − (binary-lane leg)` mixes NAGL against am1bcc, and a charge-model difference is a real
     potential-energy-surface difference that does **not** cancel. Such cycles must pin one `CHARGE_METHOD` across
     **both** legs. (Timestep differs across lanes too — 2 fs ternary vs 4 fs+HMR binary — but HMR changes only
     masses, so that is a *sampling/precision* difference, not a bias in ΔG.)
  3. **Val A's citation does not cover the NAGL lanes.** OpenFE's published ~1.7 kcal/mol accuracy was measured on
     the am1bcc method; valA_mini reproduced a known ΔΔG on am1bcc. Neither transfers to a NAGL ternary lane. The
     accuracy control for the NAGL lane is **Val B** (its own known-answer PROTAC), which is exactly why Val B is
     load-bearing and why valA_full's "re-open if am1bcc is forced onto NAGL" trigger is satisfied *by Val B* and
     not by a separate paid NAGL binary benchmark. Say this in the paper; do not let a reader infer the OpenFE
     citation covers the ternary numbers.
- **Val B (ternary cooperativity) — genuinely needed, for pipeline-validation.** The general approach is citeable
  (see prior art above), but you never certify your own container / force field / charge model / ternary wiring
  by pointing at someone else's engine's benchmark. NR-V04 cannot calibrate it (no solved ternary; celastrol is
  covalent, so it doesn't even exercise the noncovalent morph). The only way to know our cooperativity numbers
  mean anything is to run a known-answer PROTAC (VHL–BRD4 / VHL–SMARCA2) through our own pipeline. **Val B-mini is
  the highest-value dollar in the plan** — the cheapest gate on the entire prospective ladder.

---

## The prospective stage: mechanism-first, then orientation-first inverse design

The molecule-first approach — enumerate a fixed {warhead×exit×ligase×linker} matrix, model each ternary, score,
and hope the Pareto front contains a selective degrader — is a well-controlled lottery: it *verifies* selectivity
if already present but never asks the design question. Orientation-first fixed that. Applying the same logic once
more (2026-07-24) puts the **mechanism** above the orientation, because the mechanism decides what the
orientation search is optimising:

```
paralogue-unique CHEMISTRY (nucleophile) + paralogue-unique GEOMETRY (lysine)
    → basins that exploit ONE of them → productive CRL geometry
    → interface thermodynamics used to RANK within the survivors
    → linker requirements → candidate molecules
```

This removes blind linker guessing and preserves everything requirement 5 mandates (Pareto/uncertainty,
EWSR1::NR4A3 fusion context, lysines beyond the LBD, full CRL/E2~Ub ensembles). Three additions to the basin
search, all **$0 CPU** (rationale and evidence: the [2026-07-24
revision](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md)):

- **(a) Electrophile-reach term** — does the basin's linker path pass within tethering distance of C397 / C420 /
  C559 at a geometry a mild electrophile could adopt? None of the three sits *inside* the pocket, so this is an
  electrophile on the **exit vector or the linker**, which in a degrader is architecturally free — the linker
  already leaves the pocket and travels 10–20 Å. **Prefer a REVERSIBLE-covalent handle** (cyanoacrylamide-type):
  an irreversible adduct makes the degrader stoichiometric and forfeits catalytic turnover, the property that
  makes PROTACs attractive. Electrophile promiscuity is an unresolved liability with no wet lab to check it, and
  must be reported alongside the parent warhead's MYC induction, not buried.
- **(b) Transfer-zone lysine-identity term** — which lysine does the modelled E2~Ub transfer zone cover? Score
  *unique-only* highest, *unique + conserved* next, *conserved-only* lowest. This is set membership, not energy.
  Honest limit: real degraders often ubiquitinate several lysines and lysine-less substrates can still be
  degraded (N-terminal / Ser / Thr / Cys ubiquitination), so this **raises the odds; it does not guarantee** the
  paralogue is spared.
- **(c) E3 breadth, free at the search stage** — widen beyond VHL/CRBN to the ligandable set with public
  ligand-bound structures (cIAP1/BIRC2, DCAF1, DCAF15, DCAF16, KEAP1, FEM1B, RNF114). Since basin search is CPU
  this costs ~nothing and multiplies the chance that *some* E3 surface complements NR4A3's differential surface.
  Extend the free `nr4a3_e3_expression.py` HPA analysis to the new candidates. **Downselect to ≤2 recruiters
  before any GPU leg, and log what was dropped** — a silent top-N reads as "we covered everything".
- **(d) Pose-marginalisation, free** — run the basin search over the warhead-**pose ensemble** and carry only
  basins that persist, reporting the surviving fraction. Sequence-level uniqueness of C397/K572 is
  pose-independent; only the *reach* estimate is conditional, which is a far smaller conditional surface than the
  stage currently carries.

Five load-bearing pieces:

1. **A paralogue-differential surface atlas (free, CPU).** NR4A1/2/3 in a **matched** ensemble — homologous
   frames, identical pose hypotheses, protonation, target–E3 transforms, and sampling — mapping E3-reachable,
   solvent-exposed, divergent residues and lysines (LBD / hinge / DBD / fusion partner, separately). Output is a
   discrimination **map**, not three receptor models; states are explicit scenarios unless populations are
   defensibly estimable.
2. **Orientation-space search before real linkers.** For each ligase, sample many relative transforms of
   VHL/CRBN around the warhead-bound target under a flexible linker-reach restraint; keep only interfaces that are
   favorable on NR4A3 and systematically weaker/frustrated on NR4A1/2, bridgeable, clash-free, ensemble-compatible,
   and place an accessible lysine in a productive transfer region. Cluster into **~3–8 basins per ligase**.
3. **Wedges proven by a matched-pair causal cycle — the primary causal test.**
   **★ PRIMARY (revised 2026-07-24): the LIGAND-side double difference, on the lane Val B calibrates.** For a
   candidate *d* and a matched control *d₀* differing only in the element that engages the wedge,
   `S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)`. Each term is an ordinary relative alchemical quantity
   *inside one protein*; the difference asks the **design** question — does this structural element create
   paralogue discrimination? It needs **no protein-mutation engine**, makes **no cross-lane subtraction**, and by
   the cancellation identity below needs **only ternary legs**. This is far stronger than observing
   ΔG_ternary,3 < ΔG_ternary,1.
   **CONFIRMATORY (was primary): the reciprocal PROTEIN-mutation cycle.** For a target-surface mutation *m*,
   `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` (the binary leg subtracts mutation effects from the
   target–warhead complex, isolating the recruited-interface effect). A strong wedge shows a favorable NR4A3
   interface, **loss** on NR4A3→NR4A1/2 mutations, **partial gain** on reciprocal NR4A1/2→NR4A3 mutations,
   persistence across frames, and a recognizable steric/electrostatic/H-bond mechanism. It stays on the plan and
   gives a second, independent causal line **if** its known-answer benchmark passes — but the paper's headline
   causal result is no longer hostage to a lane that has cost two engine rebuilds in one day (perses retired as
   OpenEye-gated → pmx + GROMACS), has never produced a leg, is still unpriced, and carries an unresolved
   cross-lane charge mismatch. **ADOPTED 2026-07-24 (trimcrae go).**
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

- **Tier 0 — categorical-axis screen ($0 CPU) — ★ NEW 2026-07-24, and it PASSED.** No paralogue-unique
  nucleophile within tether range AND no paralogue-unique exposed lysine ⇒ selectivity must come from the
  marginal axis alone, which §Thesis shows sits at the method's resolution limit ⇒ say so explicitly and expect
  a negative. **Result: GO on both axes** (C397 at 10.9 Å, exit-vector reach; K572/K518/K592 exposed) —
  `nr4a-paralogue-unique-residues.json`.
- **Tier 1 — atlas ($0 CPU):** no E3-reachable divergent surface ⇒ STOP for free. **PASSED** (46 handles).
- **Tier 2 — basin nomination ($0–50):** no basin exploits a categorical handle *and* none even nominally
  discriminates NR4A3 ⇒ STOP cheaply. Cheap scoring has poor S/N for *small* differences, so it *nominates* — a
  gross absence of signal is an informative NO-GO, but it is not trusted to kill a real small wedge. Note the
  asymmetry the new terms buy: "does this basin place an electrophile at C397 / cover K572?" is a **geometric**
  question cheap scoring answers reliably, unlike a ~1 kcal/mol energy difference.
- **Tier 3 — pilot ONE causal direction.** ★ Now the **ligand-side double difference** (`S` above): one matched
  pair, ternary legs in NR4A3 and NR4A1, **~$12 ($1.6–45)** on the priced ternary base with the cancellation identity
  applied. No discrimination ⇒ STOP. *(The protein-mutation pilot remains available as the confirmatory second
  line: **pmx + GROMACS** engine, benchmark staged and SKEMPI-referenced but no leg run, still **UNPRICED** —
  see RUNG 5a-KS.)*

> **⚠ Tier 3 HAD NO IMPLEMENTING ENGINE IN THIS REPO (established 2026-07-24; an engine was built the same day — see the RUNG 5a-KS entry).** Every price this
> plan has ever carried for the mutation legs (~$40–90 pilot, then ~$5–10 pilot / ~$15–30 cycle) rests on the
> assumption that a paralogue swap is priced as "a binary RBFE edge + a ternary edge, same OpenFE machinery."
> **It is not.** A 3→1 swap is a **protein-residue** mutation, and OpenFE's `RelativeHybridTopologyProtocol` —
> the only alchemical engine in this repo, driving both `nr4a3_rbfe.py` and `nr4a3_ternary_fep.py` — builds its
> hybrid topology from a **ligand-to-ligand atom mapping** (LOMAP/Kartograf). Every "mutation" in the alchemical
> code is a ligand substituent (`nr4a3_rbfe.py:221`; `rbfe_map.py:30,464`, guarded `single_site`). The repo's
> **only** protein-mutation path is `nr4a3_resistance_ddg.py:53` (PDBFixer `applyMutations`) scored by MM-GBSA
> endpoint ΔG — **not alchemical, and not the quantity `ΔΔG_neo-interface^m` is defined as.**
>
> **What this means for the plan, stated plainly: the paper's designated primary causal result currently cannot
> be computed, and the ladder's cheapest-looking decisive gate is actually its least-scoped step.** Before RUNG 5
> can be planned *or* priced, one $0 step must happen first: **scope a protein-mutation free-energy engine**
> (an OpenFE/perses-style residue transformation, a non-OpenFE alchemical tool, or an explicit decision to
> redefine the wedge in terms of a quantity the existing engines *can* produce), then measure one direction.
> Until that is done, treat Tier 3 as **unpriced and unscheduled** — not as a ~$10 gate.
> This is *in addition to* the charge-model prerequisite recorded in RUNG 5 below; the wedge has **two**
> independent blockers, and neither costs GPU dollars to clear.

---

## Spending rules

1. **No pre-authorization, no pre-staging.** Nothing is ever queued to auto-fire. Every GPU run is presented at
   its gate with (a) the prior step's result, (b) a pinned cost (from realized GPU-h, not a guess), and (c) a wait
   for an explicit trimcrae "go." Only $0 CPU/CI work runs without a nod.
2. **Spend-gated ladder, cheapest-decisive-first.** The cheapest run that could kill the paper comes first; each
   rung's bigger spend unlocks only if the previous, cheaper rung looks promising. Never pay for an expensive
   stage on a hypothesis a cheap stage could have falsified.
3. **GO/NO-GO after every priced rung.** Each rung ends with an explicit test; NO-GO = stop or pivot.
4. **Every *priceable* step is priced bottom-up per edge** on Vast-4090 bases (below); pricing provenance lives in
   [pricing.md](research/compute/pricing.md). **Two steps are NOT priceable and must not be carried at a fake
   number:** the 5a-KS mutation wedge and its reciprocal cycle, which have **no implementing engine in this repo**
   (see the 🛑 blocks at Tier 3 / RUNG 5a). A ladder rung with no engine is not a cheap rung — it is an unscoped one.

## GPU economics (mixed measured/projected; full provenance in pricing.md)

**All production runs go on Vast — RTX 4090 (default) or RTX 3090 (fallback).** GCP L4 / SageMaker / Modal are
not the go-forward basis. Pick by **$/ns** (`$/hr ÷ (ns_per_day ÷ 24)`), never headline $/hr.

- **⚠ THE CARD RULE IS RETIRED (2026-07-25): the card is not the decision — the OFFER is.** This bullet used to
  read *"the 4090 wins $/ns at every size (4090 1549 / 669 / 175.6 ns/day; 3090 72.5 @444k = 2.42× slower for
  only ~9% more $/hr)"*. Both halves fail. The numbers came from the **withdrawn** 2026-07-24 23:08 bench
  (single 0.9–4.5 s windows; it also ranked a 4080 SUPER above a 4090). The **validated** grid gives
  **4090 755.36 / 4080 703.51 / 3090 359.36 ns/day** @84,534 → **2.10×, not 2.42×**. And the cards do **not**
  cost within ~9% of each other: on the live board the cheapest 3090 floor is **$0.0147/hr** against
  **$0.1310** for the cheapest 4090 — **8.8×**, far more than covering 2.10× slower. **Rank live offers by
  all-in `$/ns`** (bid + storage ÷ measured throughput) and take whatever wins; the top 10 routinely contain
  both cards. VRAM is never the constraint (≥24 GB is ample). A 3090 does need **2.10× the wall clock**, so a
  leg with a hard continuity requirement is 2.10× more exposed on it — that is scaled and flagged per card,
  not ignored.
- **★ REALIZED RATE: $0.137 per reference (4090) GPU-hour** — best-10-offer planning rate on the live board;
  range $0.057 (best offer) to $0.309 (median). Against the **$0.35–0.39/hr `step1_fanout` actually paid**,
  that is **2.6–2.8×**. Best-to-median spread is **5.43×**, so *selection* is the dominant lever — worth
  several times the bid policy. Bid = the floor plus a staleness tick, capped at the machine's on-demand price;
  derivation, evidence and the four retired multipliers in
  [research/compute/bid-strategy.md](./research/compute/bid-strategy.md).
- **Per-edge bases (Vast 4090) — one extrapolated, one rate-measured, one converted; NONE is a completed edge on a 4090:**
  - **RBFE binary edge** (complex+solvent, ~35k atoms) ≈ **~13.7 ref GPU-h ≈ ~$1.9** at the measured
    $0.137/ref-GPU-h *(repriced 2026-07-25; the old "~5–6 GPU-h ≈ ~$0.6–1.4" used the TYK2 leg, and the real
    cmpd19/NR4A3 complex is ~2.6× heavier)*. *(Basis: a live-diagnosed
    per-iteration rate, ~5.2 s/iter × 2000 iters. A clean end-to-end ΔG was **not** captured on the timing run —
    both spot instances were preempted — so this is an extrapolated rate, not a completed-edge measurement.)*
  - **Ternary cooperativity edge** (3-replica, ~146k particles, **12** windows) ≈ **~$8.8 ($3.2–22)** —
    56–72 ref GPU-h at the measured $0.137/ref-GPU-h *(repriced 2026-07-25 from ~$10–16, which assumed a
    ~$0.15–0.25/hr host; it was ~$20–28 at the $0.35–0.39/hr actually realized)*. **⚠ RECONCILED 2026-07-24 — supersedes BOTH the ~$3–6
    and the ~$4–7 that preceded it, and each was low for the SAME reason.** The number now combines two things
    that were previously mixed up with each other:
    - **Rate — directly MEASURED on Vast 4090** (the firm ternary leg via `run_ternary_leg.sh`, 12 windows,
      self-staged 8G1Q, 146,284 particles): warmup cleared with no NaN and production held steady at **~14–18
      s/iter (median ~16)**. This replaces the spec-based card-ratio guess and is a real improvement.
    - **Leg length — CONFIRMED from the committed trajectory (forensic, GH run 30117943561).** Both prior
      estimates treated **~920 iterations as a full leg**. It is neither a leg nor 38 % of one — **920 = 23 x 40 is a
      CHECKPOINT BOUNDARY** at the interval-40 cadence, and the line it came from (`binary_vhl leg at iter 913/920`)
      was the **binary** arm. The forensic read of `calib_hi_to_lo__ternary_vhl` seed 0 reports
      `checkpoint_interval 40`, `analysis_last_iteration 1560`, `checkpoint_last_iteration 1560`, `TORN false`,
      12 generations — i.e. the ternary production target is **2000 iterations**, currently **1560 committed (~78 %)**.
      Consistent with the protocol constants: the protocol hardcodes 1 ns equilibration + 5 ns production at 2.5 ps/iteration = **400 + 2000 = 2400
      iterations** (`nr4a3_ternary_fep.py:343-344`, `nr4a3_rbfe.py:364-365`; the openmmtools `.chk` history
      `iters 0,20,…,2000` confirms the production count). Using 920 makes any leg cost **~2.6× low**.

    Arithmetic: 2400 × ~16 s ≈ **~10.7 4090-GPU-h/leg** → ×2 legs ×3 replicas ≈ **~64 GPU-h/edge** ≈ **~$8.8** at the measured $0.137/ref-GPU-h *(was ~$10–16 on a ~$0.15–0.25/hr assumption)*.
    **What the 4090 run DID settle:** the **L4→4090 card ratio is validated at ~2.06×** (33 → 16 s/iter). A ratio
    of rates is independent of the iteration count, so that conclusion survives the leg-length correction fully
    intact — the old "spec-based, never benchmarked" soft spot is now closed. **What is still unsettled:** the ternary leg stands at 1560/2000 production
    iterations, so no end-to-end DG has been produced on this lane yet; the leg LENGTH is no longer a projection. ΔG is not the cost basis
    (throughput is); the ΔG comes from the GCP valB production lane (ΔG_morph 47.28). The earlier warmup NaN was a
    **pre-fix 16-window fallback**, cleared by the 12-window lane. **Its cause has itself been corrected:** it is
    *not* an unconstrained alchemical C–H (that story and its first correction were both artifacts of a diagnostic
    counter that mistook alchemical nonbonded-exception pairs for X–H bonds) — the ligand C–H *are* constrained,
    and the real cause is the softcore region in a rough homology-built assembly. The fix that works is **plain-MD
    pre-equilibration** (`ternary_preequil.py`), not a smaller timestep; see `ternary-rbfe-runbook.md` §1b/§1c.
  - **Endpoint-MD leg** (~466k atoms) ≈ **~$0.19** (~1.38 ref GPU-h, backed out of the completed 18-leg
    covalent panel: ~$0.43/leg realized on a 3090 at ~$0.10–0.21/hr ÷ the 2.102× card ratio) *(repriced
    2026-07-25 from ~$0.45)* *(measured on a 3090 at ~$0.6, converted to 4090 by the same
    card ratio — inferred, not directly measured)*.
  - **Provider reality check (2026-07-24):** the ladder is *priced* in Vast-4090 dollars, but `valB_mini` is
    *actually running* on **GCP L4 on-demand** (`PROVISIONING: standard`), the lane this section calls not-go-forward
    and pricing.md bills at ~$37/edge. That is a deliberate, defensible use of the **expiring $292 GCP free trial**
    (window closes **2026-10-10**; Modal's $30/mo is already $27.54 spent and does not carry over) — free credit
    beats cheap cash. But it means **realized spend and ladder spend are two different ledgers**, and
    `credit-status.json` records GCP `spent: 8.0` from a **manual** source that has not been reconciled against
    today's ~8 dispatched L4 legs. Keep the Vast basis as the *planning* number, track GCP burn separately, and do
    not let "we spent ~$2 so far" imply the L4 lane was free.
- **Whole gated ladder ≈ ~$194 mid-range (~$46–544) for the PRICEABLE stages, GO at every gate.**
  **★ REPRICED 2026-07-25** onto the measured Vast policy (**$0.137 per reference-4090 GPU-hour**; best-10-offer
  planning rate, range $0.057–$0.309). *(Was ~$467 (~$249–685) — a **2.4× reduction**, all of it on the $/hr
  axis: the bid rule and the offer ranking were rebuilt from measurement, not the work estimates.)* Regenerate
  the per-stage table with `python research/modalities/vast_cost_model.py`; provenance in
  [research/compute/pricing.md](./research/compute/pricing.md), derivation in
  [research/compute/bid-strategy.md](./research/compute/bid-strategy.md). Excludes optional/HELD ΔG_open + ABFE
  (~$200–500 more if invoked) and the UNPRICED protein-mutation wedge.
  **⚠ THE GPU-HOUR AXIS IS UNCHANGED and keeps every uncertainty it had** — in particular the ternary base is a
  SMARCA2/VHL rate pricing NR4A ternaries, the same non-transferability that cost 2.6× on the binary lane. Swings, in
  order: the unpriced wedge, the **ensemble-MD leg count** (5c + retrospective), then the unverified ternary leg
  length; card choice is the lever on GPU-h-heavy stages.


### ★ Cost levers adopted 2026-07-24 (evidence in the [revision doc](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md))

1. **4 fs ternary production ≈ 2× cheaper per leg — PROPOSED, one paid step settles it.** `ternary-rbfe-runbook.md`
   §1c records that after plain-MD pre-equilibration the calib ternary leg ran **warmup 48/48 @1 fs → production
   40/40 @4 fs, zero NaN, ΔG_morph = 47.28 ± 0.53**, where every prior attempt died at warmup iteration 1.
   **⚠ VERIFIED AGAINST THE LIVE LANE, NOT THE DOC (2026-07-24 4:12 PM ET, GH run 30123894814 `mode=tail` reading
   the running VM `gcp-ternary-30112102294`) — the production lane is at 2 fs, not 4:**
   ```
   [tfep] timestep=2.0 fs, minimization_steps=5000 (NaN-robust start)
   [PROGRESS-SUMMARY] leg=calib_hi_to_lo__binary_vhl seed=0 src=live live_vms=1
     warmup_committed_iter=00000800 production_committed_iter=00001680 NaN_seen=no charge=nagl
     warmup_dt_override="WARMUP timestep overridden to 1.0 fs" reduced_dt_warn="none" nan_at=""
   ```
   So the as-run shape is **1 fs warmup → 2 fs production**. The 4 fs figure people remember is the runbook §1c
   *pre-equilibration demonstration* (40 production iterations on calib), **not** the lane that is running now:
   `gpu-ternary-fep-gcp.yml` defaults `timestep_fs: 2.0` and `use_preequil: 0`, and the 4 fs demonstration only
   held **because** pre-equilibration was on. Iterations are **timestep-independent** (2.5 ps/iter), so 4 fs is
   exactly half the force evaluations → **~$8.8/edge → ~$4.4/edge**. ⚠ The runbook requires validation and
   production at the **same** timestep and the 4 fs evidence is 40 production iterations, not 2000 — so the
   settling step is to **re-run the valB_mini calibration edge at 4 fs** (~$4.4), which simultaneously exercises
   the timestep over a full leg, supplies the matched-timestep calibration, and adds a reproducibility replicate.
2. **★ The binary and solvent legs cancel EXACTLY in any paralogue comparison — up to 2×.** `nr4a3_ternary_fep.py`
   defines `binary_<e3>` as **E3 machinery + PROTAC with NO target**, and solvent as ligand-in-water. Both are
   **paralogue-independent**, so for any morph:
   `ΔΔG_coop(P) − ΔΔG_coop(P′) = ΔG_ternary,P − ΔG_ternary,P′` **exactly.**
   A 3-paralogue comparison therefore needs **3 ternary legs + 1 shared binary + 1 shared solvent — NOT 3 edges.**
   `nrv04_retrospective` and valB_full module 3 were priced as "3–6 ternary *edges*", i.e. paying for the shared
   legs 3–6× over (18 legs vs 12, −33 %; 9 legs if only the selectivity contrast is needed, −50 %). **Never price
   a paralogue panel as N edges again.**
   **★ And the saving is LARGER than the leg count suggests, because the binary leg is not cheap.** pricing.md
   carried "conservative: the binary leg is a smaller box and should run faster" — the live log above **refutes
   that**: the `binary_vhl` leg ran at **~28.6–38.2 s/iter (median ≈33)** on L4, the *same* rate as the ternary
   leg's ~33 s/iter. A shared binary leg is a full-price leg being paid for once instead of N times.
3. **Sequential (anytime-valid) stopping instead of a fixed 3 replicas — ~20–25 %.** `adaptive_certify.py`
   (anytime-valid bounds, honest under repeated looks and data-dependent stopping) and `adaptive_allocator.py`
   are already built and unit-tested in this repo and are **not wired into the ternary ladder**. Run 2 replicas;
   add the 3rd only where the decision is not yet determined at the preregistered margin.
4. **Free gates lead.** `selectivity_wedge_confirm` depended on `valB_full` + `nrv04_retrospective` (~$43; repriced 2026-07-25 from ~$80–215)
   even though its validation needs are matched-pair, not cooperativity-cube. Decoupled — see the plan below.
5. **Ligand-side double difference replaces an unpriced protein-mutation campaign** as the primary causal test.
6. **E3 breadth is free at search, capped before GPU** (≤2 recruiters, dropped set logged).

*Operational Vast setup (bid = the market floor + a staleness tick, capped at on-demand — `× 1.5` is
retired, see bid-strategy.md; pin OpenMM to CUDA 12.6; the OpenFE image
`triskit23/nr4a3fep:latest`; the `bench` / `firm` tooling in `nrv04_vast_launch.py`) is documented in
[pricing.md](research/compute/pricing.md) and `research/modalities/gpu_backend.py` — not repeated here.*

---

## THE ORDERED PLAN (spend-gated) — read top-to-bottom for "what's next"

Legend: `[ ]` pending · `[~]` in progress · `[x]` done · `[–]` skipped. `∥` = parallelizable. **Price** = spot $
for that step on Vast 4090; **Cum.** = running total if GO at every gate to here (mid-range).

### RUNG 0 — free / already done (~$0)

- **`[x]` Charge-model fix — am1bcc on the BINARY path** — **$0.** Added `ambertools>=23` +
  `partial_charge_method="am1bcc"`; the **binary RBFE lane** is on the documented reference method → cite OpenFE.
  **The ternary and endpoint-MD lanes run NAGL** (am1bcc/sqm is intractable on PROTAC-sized ligands — >85 min
  non-converging on the 166-atom NR-V04 recruiter, 2026-07-22). This is a *lane split*, not a shared charge model
  — see "Why Val A is nearly free" above for what it does and does not permit.
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
  OpenFE's published ~1.7 kcal/mol accuracy. Does not touch NR4A. **GO to Rung 2.**
  *(**Scope, corrected 2026-07-24:** this covers the **am1bcc binary lane only**. The old rider "if am1bcc is ever
  forced to NAGL, Val A reverts to a paid ~$25 NAGL benchmark" has in fact **already fired** — every ternary and
  endpoint lane runs NAGL because sqm cannot charge PROTAC-sized ligands. Resolution: we do **not** buy a separate
  NAGL binary benchmark; **Val B is the NAGL lane's known-answer accuracy control**, and it is already on the
  ladder. What this costs us is the *citation*: OpenFE's accuracy number may not be quoted for any ternary result.)*

### RUNG 2 — cheap precision + cheap probes *(only if Rung 1 = GO)*

- **`[x]` Step 1 pilot — cmpd19 conditional RBFE** — **~$2.8 ($0.8–8.5; 1–2 RBFE edges) · Cum. ~$4.** First edge
  `zaienne_cmpd19 → cw_ev_5nh2` (5-Br→5-NH₂) converged: complex ΔG_morph −29.68 ± 0.24, solvent −31.52 ± 0.26 →
  **ΔΔG_bind = +1.84 kcal/mol** (the 5-NH₂ analogue ~1.8 kcal/mol weaker *in the modeled opened pocket*). Proves
  the congeneric-RBFE pipeline converges on the real NR4A3 system without pocket collapse — the pilot's crux is
  cleared. Reproducibility replicas + pose/state sensitivity are carried forward as **fan-out inputs** (they
  refine per-edge `n_windows` and the conditional caveat, and gate the fleet). This is statistical convergence on
  a *hypothesized* pose, **not** an accuracy claim.
- **`[~]` Validation B-mini — all-binding graded cooperativity edge** — **~$8.8 ($3.2–22) · Cum. ~$13.**
  *(Repriced 2026-07-25 from ~$10–16 onto the measured $0.137/ref-GPU-h; the 56–72 ref-GPU-h estimate is
  unchanged, itself reconciled 2026-07-24 from a MEASURED 4090 rate × the corrected 2400-iteration leg — was
  ~$3–6, then ~$4–7, both off a 38 %-complete leg.)* The Wurz SMARCA2–VHL
  **cmpd 1→4** all-binding graded edge (α 12.8→2.6 ≈ +0.94 kcal/mol; both endpoints are productive binders — the
  cleanest first calibration). Exercises the bespoke `ΔΔG_coop = ternary − binary` cycle that cannot be cited
  away. **GO/NO-GO (verbatim from the prereg in `degrader-paper-schedule.json`; the ±1.0 kcal/mol band was
  deliberately REMOVED on 2026-07-17 because a separation <1 kcal/mol makes a noisy positive point estimate
  INDETERMINATE — do not re-introduce it):** PASS requires **positive sign + CI excludes zero + no fwd/rev
  disagreement + no collapse/escape/restraint-dominated leg + broad consistency with the measured +0.94**.
  valB_mini gates valB_full only — it does **not** authorize the NR4A matrix; until valB_full passes, NR4A ternary
  scores are **exploratory**. *(In progress. The cis-epimer PROTAC-2 edge is demoted to the negative-endpoint
  stress module of the cube below — a pass forced by holding an unstable pose is not a pass.)*

  **As-run protocol (live leg log, run 30112102294, 2026-07-24 1:13 PM ET) — this is what the cost basis and the
  paper must describe, not the older 16-window/4 fs assumption:** `NWIN=12` λ-windows · `CHARGE_METHOD=nagl` ·
  `TIMESTEP_FS=2.0` (warmup 1.0 fs) · `TEMPLATE_PDB=8G1Q` · `PROVISIONING=standard` (GCP **L4 on-demand**).
  The 2 fs step is a *documented physics deviation*, not drift — but **the mechanism previously written here was
  wrong and is retracted (2026-07-24).** It is **not** "an alchemical C–H whose constraint changes between
  endpoints"; that story and its first correction ("the whole ligand's C–H are unconstrained") were **both**
  artifacts of a `[hmr-diag]` counter that mistook alchemical *nonbonded-exception pairs* for X–H bonds. A perses
  force-layout dump on 2026-07-19 showed **0 unconstrained valence X–H** on both the pilot and calib edges — the
  ligand C–H **are** constrained — and calib NaN'd at 4 fs anyway. The real cause is the **softcore alchemical
  region in a large, rough homology-built assembly**; there is **no static predictor**, the timestep is empirical,
  and the fix that actually worked is **plain-MD pre-equilibration** (`ternary_preequil.py`, `use_preequil=1` —
  calib then ran warmup 48/48 at 1 fs → production 40/40 at 4 fs, zero NaN). Authority: `ternary-rbfe-runbook.md`
  §1b/§1c. **Both this lane's deviations — (a) timestep, (b) NAGL charges vs the binary lane's AM1-BCC — are now
  registered in `md_settings.py`'s docstring** (done 2026-07-24; the lane had been deviating undeclared in the
  file whose entire purpose is to make undeclared deviations impossible).
  **Direct 4090 throughput (2026-07-24):** the firm ternary leg held **~14–18 s/iter (median ~16)**, ~2× the L4
  rate — which **validates the L4→4090 card ratio at ~2.06×** (count-independent) even though it does not change
  the leg length. ΔG_morph 47.28 comes from the GCP valB production lane; no Vast leg has completed end-to-end.


- **`[ ]` ★ NEW 2026-07-24 · Rung 2b — 4 fs adoption + matched re-calibration** — **~$4.4 ($1.6–11) · Cum. ~$17 · PROPOSED, needs a go.** *(Repriced 2026-07-25 from ~$5–8.)*
  **As-run baseline confirmed from the live lane, not the doc (run 30123894814, 4:12 PM ET): production is
  `timestep=2.0 fs` with `WARMUP timestep overridden to 1.0 fs`, `NaN_seen=no`** — so the "1 fs warmup + 4 fs
  production" shape people remember is the runbook §1c *pre-equilibration demonstration*, not this lane.
  **Exact invocation** (three flags, all load-bearing): `mode=preequil` once (cached), then
  `mode=run use_preequil=1 timestep_fs=4.0 warmup_timestep_fs=1.0 reset_commits=1`. `use_preequil=1` because 4 fs
  only held *with* pre-equilibration; `reset_commits=1` because OpenFE refuses to resume a checkpoint whose
  protocol timestep differs ("Sampler in checkpoint does not match Protocol settings"), so a dt change **starts
  clean** — this is a fresh edge, not a continuation, which is what the ~$4.4 already prices.
  One edge, three jobs: (a) exercises
  4 fs over a **full** 2000-iteration production leg (the existing evidence is 40 iterations); (b) supplies the
  **matched-timestep** calibration the runbook requires before any 4 fs production result may be quoted;
  (c) is an independent reproducibility replicate of the 2 fs ΔΔG_coop. **GO/NO-GO:** no NaN across the full leg
  AND ΔΔG_coop consistent with the 2 fs run within replicate SD → adopt 4 fs for every downstream ternary leg
  (≈2× cheaper, and the ladder has ≥6 of them, so it repays several times over). NaN or a shifted ΔΔG → stay at
  2 fs and carry the 2 fs cost base unchanged. *(Cheapest possible ordering: run it only once valB_mini's 2 fs
  result is in hand, so there is something to compare against.)*

### RUNG 3 — expand the benchmarks *(only if Rung 2 probes look promising)*

- **`[–]` Validation A-full (10–20 edges) — SKIPPED · saves ~$50–140.** valA_mini reproduced the known ΔΔG cleanly
  on the standard am1bcc method, so a full re-derivation is redundant with OpenFE's published benchmark. Framing
  that must hold: cite OpenFE for accuracy; present valA_mini as a single-edge build-consistency confirmation, not
  a standalone benchmark. Re-open only if am1bcc is forced onto NAGL.
- **`[ ]` Validation B-full — component-calibration cube** — **~$22.5 ($6–67) · Cum. ~$40.**
  *(Repriced 2026-07-25; the 112–216 ref-GPU-h estimate is unchanged, revised 2026-07-24 from ~$35–100 by cost
  levers 1+2; 2–3 ternary edges + the CRL-MD module.)* ★ **Module 3 (paralogue discrimination) now
  runs on SMARCA2-vs-SMARCA4, not NR-V04** — **ADOPTED 2026-07-24 (trimcrae go)**: a close paralogue pair with
  degrader-level selectivity, solved structures, a **non-covalent** mechanism, and — decisively — **already
  staged in this repo** (8G1Q, `smarca2_model.py`, the frozen Wurz calibration), so it is a marginal add-on to
  the lane valB_mini already runs rather than a new campaign. NR-V04's selectivity is, by the repo's own UniProt
  result, most plausibly **covalent target-engagement**, which makes it a weak calibrator for a noncovalent
  ternary pipeline — exactly why the reviewer demoted it to a biological holdout. It stays the holdout.
  Apply lever 2: the paralogue module needs **N ternary legs + 1 shared binary + 1 shared solvent**, not N edges.
  Four separately-calibrated
  modules, each with its own pass/fail (a failed module → qualitative-only; no blanket "validated"): (1) a second
  all-binding graded cooperativity edge; (2) ternary pose recovery (co-fold, ~$0); (3) paralogue discrimination on
  a public system (the direct analogue of the NR4A ask); (4) productive-vs-unproductive ubiquitination geometry
  (full-CRL MD). Plus the cis-epimer negative-endpoint stress module. **GATE:** the prospective ladder never runs
  unless the **cooperativity + paralogue-discrimination** modules pass.
- **`[!]` NR-V04 covalent feasibility panel — ⚠ RESULT UNDER CORRECTION; ITS **GO** DOES NOT STAND (2026-07-24)** —
  **~$8 (MEASURED as-run, 18 legs) · Cum. ~$48.** Covalent celastrol–NR4A1 (C551) adduct + C551A + noncov/cov sensitivity +
  warhead/recruiter controls; 18 legs (6 systems × 3 seeds), 6 ns each, ~466k atoms.
  **⚠ THE READOUTS DESCRIBE THE WRONG INTERFACE.** `nrv04_covalent_md._topology_indices` split E3 from target
  POSITIONALLY ("target = last sorted protein chain"), while the co-fold YAML builder writes the target FIRST
  (`proteins = [("A", lbd)] + e3`). The chains are A=254 (NR4A LBD), E=213 (VHL), F=118 (EloB), G=112 (EloC), so
  the rule selected **Elongin C** as the degradation target: R1/R2 measured the **EloC↔rest** interface and R3
  counted **Elongin C's** lysines, not NR4A1's. Proof from the panel's own committed legs — the reactive Cys,
  resolved independently by geometry and sitting on the NR4A1 LBD, is recorded on chain **A** in 12 of 14 legs
  while the positional rule pointed at **G** (CI run 30122828434). The arithmetic reproduces the reported numbers
  exactly; the *interface* is wrong.
  **Superseded numbers, retained for the record (do NOT cite):** recruiter_active 3/3 stable vs epimer 1/3;
  covalent NR4A1 2/3 = noncovalent 2/3; C551A 1/3.
  **Status:** the split is now identified-and-validated rather than guessed (`identify_chains` → `chains.json`,
  consumed by the driver; every leg records the split it used), and the corrected re-run of the 14 legs (~$6,
  Vast, into `nrv04-covalent-results-chainfix`) is built and **not yet launched**. Until it lands, this rung
  supplies **no GO** and must not be cited as one. Full evidence:
  [research/modalities/nrv04-cofold-chain-forensics-2026-07-24.md](research/modalities/nrv04-cofold-chain-forensics-2026-07-24.md).

### RUNG 4 — warhead map, differential atlas, retrospective gate

- **`[ ]` Step 1 fan-out — cmpd19 congeneric map, 8-wide** — **~$36 ($15–80; ≈19 RBFE edges × ~13.7 ref
  GPU-h at $0.137/ref-GPU-h) · Cum. ~$84.** ★ **REPRICED 2026-07-25 from ~$91–101.**
  The 2026-07-24 correction identified two compounding errors; **one has now been fixed at source and one has
  not, and the distinction matters:**
  - **Work (NOT fixed, unchanged here):** a per-iteration rate measured on the **public TYK2** edge was used as
    if it were the NR4A3 rate (measured: 498 vs **190 ns/day** aggregate, three independent hosts). That
    correction stands — the unit is **~13.7 ref GPU-h**, not ~5–6.
  - **Price (FIXED):** the old $12–26 used a **single** unusually cheap host's $0.122/hr; the $91–101 that
    replaced it used the **$0.35–0.39/hr actually realized**. Neither was the market — $0.35–0.39 is what
    bidding `× 1.5` on a `min_bid`-ranked offer costs. At the measured **$0.137/ref-GPU-h** the same 260 ref
    GPU-h is **~$36**. **Lane BUILT and proven to sample** (wave 1
  reached 95–99 % GPU utilisation on the real system) but **HALTED at ~$2 with 0/19 ΔΔG** once the repricing
  crossed the spend gate; everything is checkpointed, so a resume continues rather than restarts. Full record:
  [research/modalities/step1-fanout-lane.md](research/modalities/step1-fanout-lane.md).
  **Scope, if resumed:** the price covers **tranche 1 only** — the 19 edges at their charge-**conserving**
  microstate leg on the **primary frame**. The 8 charge-changing legs are *blocked* (no charge correction
  implemented) and the 6-frame conformer/paralogue axis is a **separate ~6× spend** — so tranche 1 yields a
  single-conformer **conditional** map, **not** the selectivity readout or the sensitivity ranges.
  **Gate:** Val A satisfied (cite OpenFE) AND the Step 1 pilot behaved (with its replicas + pose/state
  sensitivity). **Timestep is NOT a lever** — measured free on CPU: the protocol runs at OpenFE's default
  `constraints=hbonds` + HMR 3.0, every X-H is constrained, so all edges are 4 fs and no 2× saving exists. The
  bid/selection lever has now been **pulled** (2026-07-25): the multiplier is retired in favour of a
  floor-plus-tick bid, and offers are ranked on all-in `$/ns` rather than `min_bid` — which is where most of the
  $91–101 → ~$36 comes from, i.e. *selection*, not the multiple. See
  [research/compute/bid-strategy.md](./research/compute/bid-strategy.md).
- **`[x]` ★ NR4A paralogue-UNIQUE reactive-residue map — DONE 2026-07-24 · $0 · TIER-0 GATE PASS/GO.** Full-length
  UniProt (P22736/P43354/Q92570/Q01844) + dual-aligner agreement + matched-model geometry
  (`nr4a_paralogue_unique_residues.py`, 15 unit tests, run on CI because the sandbox proxy blocks UniProt).
  **4 NR4A3-unique cysteines** (2 exposed): **C397** — NR4A1 N363 / NR4A2 S363, RSA 0.395, **10.9 Å** from the
  cryptic pocket (exit-vector reach) — plus C420 (18.3 Å), C559 (12.8 Å, RSA 0.095 in this conformer), C166
  (outside the LBD). **4 NR4A3-unique lysines** (3 exposed in the LBD): **K572** (RSA 0.879, 11.5 Å), **K518**
  (0.413, 13.4 Å), **K592** (0.506, 16.2 Å), K178 (outside). Reciprocal check reproduces the NR-V04 Leg-0 exactly
  (NR4A1 C551 → NR4A3 T579) and completes it: NR4A1 has 5 cysteines NR4A3 lacks. K85/K194 excluded on aligner
  disagreement. EWSR1 fusion moiety contributes only 1–2 lysines → **fusion-lysine axis is thin, not a design
  axis**. This is now the FIRST gate in the ladder — it costs nothing and it decides what 5a optimises.
  *(Open, cheap: the matched NR4A1/2 MD-ensemble add-on should report the **distribution** of C397 exposure, not
  one frame's 0.395.)*
- **`[x]` NR4A differential surface atlas — DONE · $0 · GATE PASS/GO.** Matched Shrake–Rupley SASA + BLOSUM62
  alignment over NR4A{3,1,2} opened models → **46 differential-surface handles** (exposed × divergent ×
  character-changing), 15/15 LBD lysines exposed; per-residue identities reproduce the canonical map 148/148. A
  differential surface exists to steer an E3 against (distinct from the ~70% pocket hotspot), so the 5a
  orientation-basin search is warranted. *(Optional add-on: matched NR4A1/2 MD ensembles ~$10–40 to test which
  handles survive dynamics.)*
- **`[ ]` NR-V04 retrospective — preregistered holdout** — **~$21 ($4.8–67) · Cum. ~$104.**
  *(Repriced 2026-07-25 from ~$15–40; the 84–216 ref-GPU-h estimate is unchanged, revised 2026-07-24 by cost
  levers 1+2: a 3-paralogue panel is 3 ternary legs + 1 shared binary + 1 shared solvent, not 3 edges, and 4 fs
  halves each leg.)* Full ensembles through the pipeline, no tuning, epimer
  control; report directional concordance only. **Gate:** Val B-full + NR-V04 feasibility + Step 1 fan-out.
  **★ It no longer gates the causal kill-switch** (lever 4): the wedge's validation need is a matched-pair
  control, not a cooperativity cube, so 5a-KS is decoupled and can fire before this is bought.
  **GO/NO-GO:** at least directionally concordant with the NR4A1-degraded / NR4A2·3-spared outcome → GO to the
  prospective ladder; discordant → the ladder is not justified, publish the honest negative. **Interpret with the
  covalent confound explicit:** NR4A1 Cys551 is unique to NR4A1 (NR4A3 T579), so a concordant result may be
  recovering *target engagement*, not ternary cooperativity — which is why this is a biological holdout and
  SMARCA2/4 is the method calibrator.
  **★ STATE (2026-07-24 night): fully built + preregistered + unlaunched.** Because the covalent confound is
  *measured*, the panel **decomposes** — **R1** (primary, all-non-covalent NR4A1/2/3) tests whether the workflow
  discriminates paralogues with the warhead held off; **R2** isolates warhead chemistry; **R3** (epimer) is
  conditional. **A null R1 is a registered, publishable outcome**, not a method failure.
  **Resume here: [research/modalities/nrv04-retrospective-handoff-2026-07-24.md](research/modalities/nrv04-retrospective-handoff-2026-07-24.md)**
  (exact commands, cost ledger, traps) · prereg
  [research/modalities/nr4a3-nrv04-retrospective-prereg.md](research/modalities/nr4a3-nrv04-retrospective-prereg.md).

### RUNG 5 — orientation-first prospective ladder *(the flagship, gated mid-ladder by the causal kill-switch)*

- **`[ ]` 5a · Orientation-basin search — ★ now MECHANISM-FIRST** — **~$0–50 (CPU $0 + optional MM-GBSA rescore)
  · Cum. ~$129.** Broad transform sampling across the **widened ligandable E3 set** (VHL, CRBN, cIAP1/BIRC2,
  DCAF1, DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2 — free at CPU, **downselect to ≤2 before any GPU leg and log
  the dropped set**). **★ Availability answered $0 and it does NOT constrain the choice (CI run 30125742542,
  2026-07-24):** all 8 widened arms are broadly expressed and record-complete on HPA, every symbol resolved
  through HPA's own search with an exact-match guard — same verdict as the original VHL/CRBN check. So the
  downselect must be made on **ligandability + interface geometry**, never on availability; and no recruiter may
  be dropped with "not expressed" as the reason. Matched 3-paralogue scoring **over the warhead-pose ensemble**;
  cluster into ~3–8 basins/ligase;
  score with the two new **categorical** terms — (a) does the linker path reach C397/C420/C559 at an
  electrophile-compatible geometry, (b) does the E2~Ub transfer zone cover a **unique** lysine (K572/K518/K592)
  rather than a conserved one — then the cheap counterfactual screen to nominate marginal wedges. The categorical
  terms are **geometric set-membership questions**, which cheap scoring answers far more reliably than a
  ~1 kcal/mol energy difference.
- **`[ ]` 5a-KS · Wedge confirmation — ★ pilot-first KILL-SWITCH + causal RESULT** — **~$12 ($1.6–45; PRIMARY: the
  ligand-side double difference) · Cum. ~$141.** *(Repriced 2026-07-25 from ~$5–25.)* Pilot ONE matched pair first: `S = ΔΔG_coop(d₀→d | NR4A3) −
  ΔΔG_coop(d₀→d | NR4A1)`, ternary legs only (lever 2), on the lane Val B calibrates. **No discrimination ⇒
  STOP** — publish the honest causal negative, skip the refinement tail. Discrimination ⇒ extend to NR4A2 and to
  a second design element.
  **CONFIRMATORY second line — the reciprocal PROTEIN-mutation cycle — ⚠ pmx + GROMACS ENGINE BUILT (perses
  retired same-day as OpenEye-gated), BENCHMARK STAGED, NO LEG RUN · STILL UNPRICED** *(was "Decision ~$5–10 · full cycle if GO ~$15–30").* Pilot ONE direction (3→1); loss ⇒ complete
  the reciprocal cycle (3→2 + reciprocal 1/2→3). Kept because two independent causal lines are worth more than
  one — but it is no longer the result the paper depends on.

  **This rung had TWO independent blockers. Both are now addressed in code — but "addressed" is not
  "validated", and the rung stays UNPRICED until a known-answer benchmark says the engine works.**

  **Engine (built 2026-07-24, trimcrae decision: build rather than descope or substitute a proxy).**
  [`research/modalities/nr4a3_protein_fep.py`](research/modalities/nr4a3_protein_fep.py) —
  perses `PointMutationExecutor` for the protein hybrid topology, openmmtools `MultiStateSampler` for the
  alchemical sampling, MBAR for the reduction; conda env
  [`sagemaker_src/environment-protfep.yml`](research/modalities/sagemaker_src/environment-protfep.yml), kept
  separate from `rbfe` so a perses solve can never break the proven binary lane. The wedge subtraction reuses
  `ternary_coop.ddg_coop`, so there is one definition of the cycle in the repo, not two.
  - **Blocker 1 (cross-lane charge mismatch) — CLEARED IN CODE.** `assert_charge_consistency` hard-fails any
    wedge whose ternary and binary legs charge the ligand differently (the am1bcc-vs-NAGL split
    `md_settings.py` registers as a DOCUMENTED DEVIATION), and both result JSONs record the pinned method. An
    un-pinned wedge is not a thermodynamic cycle, so this is a refusal, not a warning.
  - **Blocker 2 (net-charge-changing mutations) — CLEARED IN CODE, and it bites immediately.** **R412 is one
    of our own seven selectivity handles, and R→A is charge-changing**, so the most obvious wedge to reach for
    is exactly the one PME cannot do naively (the neutralising background plasma shifts the electrostatic free
    energy by a system-size-dependent amount that does not cancel between the differently-sized ternary and
    binary boxes). `plan_wedge` refuses a charge-changing mutation unless an explicit correction strategy is
    chosen. **Prefer a charge-conserving handle (L406/T410/I484/I531/L534) for the FIRST causal test.**
  - **⛔ BLOCKED ON A COMMERCIAL LICENCE — perses is not usable here (established 2026-07-24 PM, by
    running it).** The benchmark lane was built and launched, and the first real leg failed in
    perses' *core protein-mutation path*, not its ligand branch:

    ```
    PointMutationEngine.propose
      -> _construct_atom_map                  (topology_proposal.py:634)
      -> PolymerProposalEngine.generate_oemol_from_pdb_template  (:1179, :1180)
      -> createOEMolFromSDF                   (:487)
      -> oechem.oemolistream()                (perses/utils/openeye.py:346)
    ```

    perses 0.10.3 builds the **old→new residue atom map** — which *is* the alchemical transformation
    — by round-tripping each residue template through an OpenEye OEMol. **OpenEye is commercial and
    licence-gated.** Probed on free CI: `generate_oemol_from_pdb_template` has no conditional and no
    RDKit alternative (perses' only RDKit-backed mapper, `rjmc/atom_mapping.py`, is the *ligand*
    mapper and is not on this path). An import shim satisfies the import but correctly REFUSES the
    call rather than fabricating a map.
    **Cost of learning this: ~$0.05 of Vast time** — the smoke plus two free CI probes.
    **Everything except the perses-specific `build_htf` is engine-agnostic and stands:** staging with
    a mutation-site check, the SKEMPI-verified references, scoring, the qualification verdict, the
    price reduction, the Vast lane, the reap.
    **Alternatives, priced on free CI:** `pmx` (the published GROMACS-based protein-mutation FEP
    engine) is **not on conda-forge** — pip/GitHub install — while **GROMACS is** (2025.4). So the
    free route exists but means a second MD stack. **This is a trimcrae fork** (licence vs second MD
    stack vs descope) and is recorded as open.

  - **✅ ENGINE DECIDED — pmx + GROMACS (trimcrae, 2026-07-24).** Rather than buy an OpenEye licence,
    descope the wedge, or fall back to the MM-GBSA proxy, the lane switches to **pmx** (Gapsys & de
    Groot) — the published, field-standard *free* engine for protein-mutation FEP, arguably better
    validated for this quantity than perses. The price is a second MD stack (GROMACS rather than
    OpenMM), which is engineering, and engineering is free here; a licence is not. Route confirmed on
    free CI before any build: **CUDA GROMACS solves** from conda-forge (165 packages) and **pmx
    `develop` installs on Python 3.11** with `alchemy`/`estimators`/`forcefield`/`gmx`/`mutdb`
    present. Built: [`Dockerfile.pmxfep`](research/compute/Dockerfile.pmxfep),
    [`protfep_pmx.py`](research/modalities/protfep_pmx.py), and the full ladder in
    `gpu-protfep-vast.yml`. Plan + the two probe gotchas that produced false negatives:
    [protfep-pmx-plan.md](research/modalities/protfep-pmx-plan.md).
    **Everything around the engine was unchanged** — staging with its mutation-site refusal, the
    SKEMPI-verified references, scoring, the verdict, the price reduction and the Vast lane are all
    engine-agnostic. **Most of the ladder is now $0:** stage-test, refcheck, bake, and a build-test
    that runs the ENTIRE hybrid construction on a CPU runner, because only the alchemical sampling
    needs a GPU. A host is rented only once a hybrid demonstrably builds.

  - **⛔ NOT YET CLEARED — validation.** No leg has run. The engine must recover the known-answer
    protein-mutation benchmarks (barnase–barstar Y29A/Y29F; both charge-conserving so engine error is not
    confounded with the charge artifact) **within ~1.5 kcal/mol AND in the right order** before
    5a-KS contributes any number to the manuscript. That benchmark is what prices this rung; until it runs,
    UNPRICED remains the honest label.

  **EXECUTION LAYER BUILT + BENCHMARK LANE LAUNCHED (2026-07-24 PM, this branch).** "Engine built" that
  morning covered only the *planning* layer — guards, wedge arithmetic, a `PointMutationExecutor`
  constructor. Nothing could run a leg, which is precisely why there was no rate to price from. Now built
  and pushed:
  [`protfep_run.py`](research/modalities/protfep_run.py) (perses hybrid → replica-exchange sampling →
  MBAR, per-chunk checkpoint/resume, partial leg JSON as the deliverable on a timeout),
  [`protfep_bench.py`](research/modalities/protfep_bench.py) (benchmark systems, RCSB staging with a
  mutation-site check that **refuses** to stage if the residue at the site is not the one named, scoring +
  the qualification verdict), [`protfep_reduce.py`](research/modalities/protfep_reduce.py) (legs → ΔΔG →
  verdict **and** the first measured per-leg rate), [`protfep_refcheck.py`](research/modalities/protfep_refcheck.py)
  (recomputes the reference ΔΔG from SKEMPI 2.0's deposited Kd values, because the pass criterion is
  computed against those numbers), plus the Vast image + launcher + workflow.
  - **Latent error caught in the build:** the engine's hand-written benchmark list put barstar's Y29 on
    **chain A**, which in 1BRS is *barnase*. The list is now derived from `protfep_bench` rather than
    duplicated, and CI verifies the staged site against the deposited structure (confirmed 2026-07-24:
    chain D = barstar, 87 residues, **TYR at 29**; chain A = barnase, 108 residues).
  - **Ladder position unchanged.** The engine is still **UNVALIDATED** and the rung still **UNPRICED**. A
    built execution layer is not a passed benchmark. `plan_wedge` continues to stamp `validated: false`
    into every plan, and the reducer's verdict cannot go green on a partial set or a wrong ordering.
  - **Sequence, cheapest-decisive-first:** smoke (~$0.10, proves image+perses+sampler+MBAR+S3) → pilot
    (both legs of Y29A, ~$1–3 — **the abort gate**: no recovery of the canonical hot spot ⇒ the wedge is
    not deliverable and the set is not worth paying for) → full set (~$5–10) only if the pilot sees it.
  - **Declared physics deviation:** 2 fs with a 1 fs warmup, not the canonical 4 fs+HMR. Softcore regions
    are where the ternary lane NaN'd, the timestep is empirical with no static predictor, and on a
    brand-new engine's first leg a NaN costs the whole rental while 2 fs costs ~2× the iterations of a
    sub-dollar leg. Escalate only after this lane survives a full leg — and record it; do not assume it
    transfers from another lane.

  **⚠ BLOCKER 1 — NO PROTEIN-MUTATION FEP ENGINE EXISTS IN THIS REPO (added 2026-07-24).** The old price
  ("3→1 = one binary RBFE + one ternary edge") assumed a paralogue swap runs on the same machinery as a ligand
  edge. It does not: OpenFE's `RelativeHybridTopologyProtocol` maps **ligand** atoms only, every "mutation" in
  the alchemical code is a ligand substituent (`nr4a3_rbfe.py:221`, `rbfe_map.py:30,464`), and the repo's sole
  protein-mutation path is `nr4a3_resistance_ddg.py:53` (PDBFixer + MM-GBSA endpoint ΔG — non-alchemical).
  **Required $0 step:** scope a protein-mutation free-energy engine, or redefine the wedge in terms of a quantity
  the existing engines can actually produce, then measure one direction to establish a real price. See the
  expanded note under "The hard kill-switch" above and `research/compute/pricing.md` §B.3.

  **⚠ BLOCKER 2 — pin the charge model across both legs (added 2026-07-24).** The wedge quantity
  `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` is the repo's one **cross-lane** subtraction, and as the
  lanes are configured today it would mix a **NAGL** ternary leg against an **am1bcc** binary leg. Unlike the
  timestep, the charge model changes the potential energy surface, so it does **not** cancel — the residual would
  be indistinguishable from the very interface effect the kill-switch is built to detect, and it would
  contaminate the paper's *primary causal result*. Before any 5a-KS leg launches: run **both** legs with an
  explicit, identical `CHARGE_METHOD` (NAGL is the only choice that can charge both a small mutation edge and a
  PROTAC-scale assembly), stamp it into both result JSONs, and add a test that refuses to compute a wedge from two
  legs whose recorded `charge_method` differ. Cost: $0 — it is a config pin plus an assertion.
- **`[ ]` 5b · Inverse linker design** — **~$0–20 (mostly $0 CPU) · Cum. ~$151.** For each confirmed basin, derive
  linker requirements (endpoint distance, exit-vector dihedral, strain, reach), enumerate a virtual library,
  filter by basin fidelity, annotate exact structures + synthetic feasibility → **~12–20 virtual constructs** (the
  "24–36" now bounds this virtual set, not a hand-built grid). ★ For basins carrying the covalent handle, the
  library enumerates the **electrophile position on the linker** as a design variable, and **prefers
  reversible-covalent** chemistry (an irreversible adduct forfeits catalytic turnover).
- **`[ ]` 5c · Explicit ternary-ensemble refinement** — **~$21 ($1.9–85; endpoint MD, 24–~200 legs at
  ~1.38 ref GPU-h each) · Cum. ~$172.** *(Repriced 2026-07-25 from ~$15–100. Still the biggest swing item —
  the leg COUNT, not the rate, now dominates its uncertainty.)* Replicated ternary + full CRL/E2~Ub MD across target states,
  linker conformers, and in-basin poses; matched NR4A1/2/3; separate accessibility from stability; robust
  constraint-satisfaction filtering → **~4–8 constructs** nondominated under scenario + model uncertainty.
  ★ Add a constraint: **which lysine the ubiquitin actually reaches**, reported per construct as a distribution
  over unique-vs-conserved sites, not just "a lysine is near".
- **`[ ]` 5d · Local ternary FEP** — **~$22 ($3.2–80; 3–6 ternary comparisons) · Cum. ~$194.** *(Repriced 2026-07-25 from ~$10–45; ref-GPU-h
  unchanged, revised by levers 1+2 from ~$21–90.)* Alchemy **only** within a
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

## Spend summary — running total (bottom-up estimate, NOT a measured total)

**Honesty note on the bases (rewritten 2026-07-24, second correction).** An earlier version read "every per-edge
base is measured, so the ladder totals cleanly." It does not, for two separate reasons — the second of which was
only established today and moved the total by more than the first.

1. **No base is a completed end-to-end run on the card it is quoted for.** The RBFE edge is an extrapolated
   per-iteration rate (timing run preempted before a clean ΔG); the ternary edge is an L4 wall-clock ÷ a
   spec-based card ratio; the endpoint leg is a 3090 measurement ÷ the same ratio.
2. **⚠ The ternary base was ~2.6× too low, because it was extrapolated from a PARTIAL leg.** The L4 wall-clock it
   came from covered **920 of the 2,400 iterations** a complete leg requires (400 equil + 2,000 prod at 2.5 ps per
   iteration — a figure that is *timestep-independent*, see `rbfe_spot_driver._iters_from_time`), i.e. ~38 % of a
   leg. Corrected, one ternary edge is **~$7–15 on a Vast 4090** (~132 L4-GPU-h ≈ ~57 4090-GPU-h; ~$94 at the
   L4 on-demand rate it was actually run at). **No ternary leg has ever run to completion**, so this remains a
   PROJECTION, not a measured base.

3. **⚠ The 5a-KS kill-switch is UNPRICED, not cheap.** Its previous "~$5–60" was priced as if protein-mutation FEP
   were a variant of the ligand RBFE the repo already runs. It is not: OpenFE's `RelativeHybridTopologyProtocol`
   is a **small-molecule** protocol built from a ligand-to-ligand atom mapping, and the repo's only
   protein-mutation path (`nr4a3_resistance_ddg.py:53`, PDBFixer rebuild → MM-GBSA endpoint scoring) is not
   alchemical. **There is no implementing engine for the wedge in this repo.** It is therefore excluded from the
   totals below rather than carried at a fake price. See the 🛑 blocks at Tier 3 and RUNG 5a.

4. **★ REVISED DOWNWARD 2026-07-24 by the six cost levers** (§GPU economics). The two that move the totals are
   the **exact cancellation of the binary/solvent legs in any paralogue comparison** (a paralogue panel is N
   ternary legs + one shared pair, not N edges) and **4 fs ternary production** (2× per leg, PROPOSED, settled by
   one ~$4.4 matched re-calibration edge). Neither adds or removes science; both were mis-priced.

**★ REPRICED 2026-07-25 → ~$128 mid-range (~$36–381).** The `$/hr` half of the correction below is now fixed
at source: the bid policy was rebuilt from measurement (`charged = min(bid, on-demand)`, verified by renting one
offer at three bid multiples) and offers are ranked on all-in `$/ns` instead of `min_bid`, giving **$0.137 per
reference GPU-hour** against the $0.35–0.39/hr quoted below. **The GPU-hour half is NOT fixed** — see the
transferability warning at the end of this section. Table + regeneration:
[research/compute/pricing.md](./research/compute/pricing.md) §C.

**⚠⚠ THE ~$240 TOTAL IS WITHDRAWN (2026-07-24 ~5:15 PM ET) — the per-edge BASES under it were measured and
found ~3× low.** The `step1_fanout` session measured the real system on three independent Vast 4090 hosts and
halted the tranche on the result (branch `claude/step1-fanout-cmpd19-congeneric-jfwg0j`, commits 71b0f951 /
c26eb5a7). **Two errors compounded, and both hit every GPU line in this file, not just theirs:**

1. **System transferability.** The RBFE edge was priced on a rate measured on the **public TYK2** system
   (~5.2 s/iter). The **real cmpd19/NR4A3 cryptic-pocket complex samples at ~13.6 s/iter** (14.42 / 12.76 /
   13.70 on three hosts, 16 samples each — a tight enough spread to rule out host variance): a **~2.6× heavier
   system**. Complex leg ~9.1 GPU-h, not 3.6; unit ≈ 13.7 GPU-h.
2. **Bid basis.** The $/hr came from a **$0.122/hr** instance; the realized current 4090 market at
   `min_bid × 1.5` is **$0.35–0.39/hr** — ~3×. **⚠ SUPERSEDED 2026-07-25: that $0.35–0.39 was a consequence of
   the policy, not of the market.** It came from bidding `× 1.5` on an offer chosen by ranking `min_bid`. Under
   the measured policy (floor + tick, ranked on all-in `$/ns`) the same work costs **$0.137/reference GPU-hour**
   — the market was never the problem, the bid rule and the ranking were.

Net for their rung: `step1_fanout` is **~$91–101, not ~$12–26** — measured, and past the >$50 gate, which is why
trimcrae halted it (~$2 realized, fleet torn down, `live_instances=0`, **0/19 units produced a ΔΔG**, partial
checkpoints in S3 so a re-dispatch resumes rather than restarts).

*Housekeeping:* `lint_claims.py`'s R5 rule ("no per-edge alchemical dollar figure is a completed run on the
card quoted") had its premise **falsified for the binary lane** by this measurement — the NR4A3 rate was taken
on the real system, on the quoted card, across three hosts. The rule should be re-scoped when the step1 branch
merges; it is left alone here rather than raced.

**★ THE SAME TWO ERRORS ARE LIVE IN THE TERNARY BASE, AND ONE OF THEM IS STILL UNMEASURED.**
- *Bid basis — RESOLVED 2026-07-25, and it moved the other way:* every ternary figure in this file used
  **$0.15–0.25/hr**, and the realized **$0.35–0.39/hr** made the 56–72 GPU-h edge **~$20–28**. Under the
  measured policy it is **$0.137/reference GPU-hour → ~$8.8**, i.e. below the original estimate. The realized
  rate was an artifact of bidding `× 1.5` on a `min_bid`-ranked offer.
- *System transferability — UNMEASURED, and it is exactly the error above:* the ~16 s/iter ternary rate was
  measured on the **SMARCA2/VHL 8G1Q** assembly. It is being used to price **NR4A** ternaries. That is the same
  move that just cost 2.6× on the binary lane. **Do not treat the ternary base as transferable until an NR4A
  ternary leg has been timed** — and expect it to be heavier, not lighter.
- *Card choice is NOT the lever — but the OFFER is (revised 2026-07-25):* the old form of this line ("a 4090
  and a 3090 cost the same per iteration") was true of the two *specific* prices then in hand, not of the
  market. Across the live board the spread **within** the 4090 class alone is 2.3×, and best-to-median across
  all qualifying offers is **5.43×**. Do not pick a card; rank offers on all-in `$/ns`.

**What survives, and what does not.** The six cost levers are **ratios** — 4 fs halving force evaluations, the
exact binary/solvent cancellation, sequential stopping — so they are independent of $/hr and of system
heaviness and all still hold. What does not survive is the **absolute total**: it was built on bases that have
now been measured low. That correction stands on the **work** axis; the **price** axis has since been
rebuilt from measurement and moves the total the other way (below).

**PINNED TOTAL: ~$194 mid-range (~$46–544)**, GO at every gate, priceable stages only. Excludes (a) the 5a-KS
protein-mutation wedge + reciprocal cycle (UNPRICED/BLOCKED) and (b) Optional/HELD ΔG_open + ABFE (~$200–500
more). Dominant uncertainties, in order: the unpriced wedge, the **ensemble-MD leg count** (5c + retrospective),
and the ternary transferability risk above — which is still unmeasured.

**★ THE DEFERRED REPRICING IS DONE (2026-07-25), AND THE DEFERRED ESTIMATE WAS WRONG.** This block previously
read: *"Not yet folded in: the bid multiple went 1.9 → 1.25 … the fan-out alone goes ~$91–101 → ~$57–66, but the
total is left at $467 rather than re-derived on the spot — a repricing gets measured, not estimated twice in one
day."* That was the right instinct, and the measurement has now been taken. It says two things:
1. **The fan-out is ~$36, not ~$57–66.** The estimate only counted the bid multiple. Measurement showed
   **selection** — ranking offers on all-in `$/ns` instead of `min_bid` — is the larger lever by several times
   (5.43× best-to-median spread on the live board, against 1.48× for the whole `×1.9 →` floor bid change).
2. **The total is ~$194, not ~$467** — a **2.4× reduction**, entirely on the `$/hr` axis.
The `$0.35–0.39/hr` that the fan-out actually paid was never "the 4090 market": it is what bidding `× 1.5` on a
`min_bid`-ranked offer costs. Derivation and evidence:
[research/compute/bid-strategy.md](./research/compute/bid-strategy.md).

**This does NOT weaken the mechanism-first case.** The argument was never that GPU work is expensive in the
absolute — it is that spending it on an axis needing ~2.0 kcal/mol when the method resolves 1.12 is a bad
trade at *any* price, and the $0 categorical screens dominate either way.

*(Superseded, retained for the record: "~$467 (~$249–685)", "~$240 (~$90–390)", "~$390 (~$170–610)".)*
⚠ **A rate measured on one molecular system is not a price for another** — the single largest correction to
date (~4× on the fan-out) came from applying a public-TYK2 per-iteration rate to the NR4A3 complex, which is
~2.6× heavier in aggregate throughput. Treat any cross-system rate as a routing hint, never a price. This table
and `pricing.md` §C carry the same chain and must agree.

| Rung | GPU work | Step $ (low–high) | Cum. (mid) |
|---|---|---|---|
| 0 · infra + free CPU (DONE) | step0 + emc_e3 + pocket | ~$1–2 | ~$2 |
| 1 · Val A smoke (DONE, realized ~$0 on GCP credit) | 1 public RBFE edge | ~$0–15 | ~$2 |
| 2 · pilot (DONE) + Val B-mini | 1–2 RBFE edges + 1 ternary edge | ~$2.8 + ~$8.8 (range $4–31) | ~$13 |
| **2b · 4 fs adoption + matched re-calibration** | 1 ternary edge @4 fs | **~$4.4** ($1.6–11) | ~$17 |
| 3 · Val B cube (SMARCA2/4 module) + NR-V04 feas. (DONE) | 2–3 ternary edges + CRL-MD; covalent panel | ~$22.5 + ~$8 (range $14–75) | ~$48 |
| 4 · fan-out + atlas + **unique-residue map** (both $0) + NR-V04 retro | ≈19 RBFE edges + NR4A1/2/3 ternary **legs** | **~$36** + ~$21 (range $20–147) | ~$104 |
| 5a · mechanism-first basin search + **KILL-SWITCH** | basin ($0–50, multi-E3, CPU) + ligand-side double difference | ~$0–50 + ~$12 (range $2–95) | ~$141 |
| 5 (if GO) · linker + ensemble refine + local FEP | inverse-linker ($0–20) + ensemble MD (~$21) + within-basin FEP (~$22) | ~$53 (range $5–185) | ~$194 |
| Confirmatory protein-mutation cycle (optional) | — | **UNPRICED** | *(excl.)* |
| Optional ΔG_open / ABFE (HELD) | — | +$200–500 | *(excl.)* |

Notes: the restructuring buys **causal evidence** (matched-pair cycles + ensemble MD + local FEP) over
co-fold-and-score — higher information per dollar, not lower. A non-viable paper still dies for ~$2 at Val A, or
**free** at the Tier-0 unique-residue map and the atlas (both passed) — and the ladder's cheapest decisive gate is
restored: the kill-switch is a **~$12 ($1.6–45) ligand-side double difference** on the lane Val B calibrates, no longer a
gate blocked behind an unbuilt engine and ~$80–215 of prerequisite ternary work. The *expected* cost is lower
than the totals suggest, because the leading gates are now $0.

## Dependency spine

```
TIER-0 unique_residue_map [x]($0) + atlas [x]($0)  ──[BOTH PASS]──►    ★ leads everything priced
          │        (C397 exit-vector reach; K572/K518/K592 exposed; EWSR1-lysine axis thin)
          │
RUNG0  step0 [x] + emc_e3 [x] + pocket [x]                              (CPU/$0, done)
          │
RUNG1  valA_mini [x] ──[GO]──►                                         (cite OpenFE; Cum ~$2)
          │
RUNG2  step1_pilot [x] ∥ valB_mini [~ 2 fs]  ──[GO?]──►                (Cum ~$15)
          │
RUNG2b 4 fs adoption + MATCHED re-calibration (~$4.4) ──[no NaN & ΔΔG consistent?]──►
          │      └── YES ⇒ every downstream ternary leg ≈2× cheaper
          │      └── NO  ⇒ stay at 2 fs, carry the 2 fs base
          │
RUNG3  valB_full cube (module 3 = SMARCA2-vs-SMARCA4) + nrv04_feasibility [!] ──[GO?]──►   (Cum ~$97)
          │            ([!] = feasibility's GO is WITHDRAWN pending a corrected re-run: its readouts
          │             measured the Elongin C interface, not VHL<->NR4A1. It gates nothing until then.)
          │
RUNG4  step1_fanout ∥ atlas [x]($0) ──► nrv04_retrospective ──[concordant?]──►  (Cum ~$273)
          │      (holdout, NOT the calibrator; read WITH the Cys551 covalent confound)
          │
RUNG5  basin_search($0–50, multi-E3, pose-marginalised, CATEGORICAL terms)
          │        ──► ★ KILL-SWITCH = ligand-side double difference (~$12)
          │      └── no discrimination ⇒ STOP: publish honest causal negative
          │      └── discrimination    ⇒ extend + tail
          │      └── CONFIRMATORY 2nd line: the protein-mutation cycle — pmx + GROMACS
          │           lane (perses retired: OpenEye-gated), UNPRICED, gated on its own
          │           SKEMPI-referenced known-answer benchmark. Its branches are unchanged:
          │           benchmark FAILS ⇒ not deliverable, fall back to the labelled MM-GBSA
          │           proxy or descope and SAY SO; passes & no loss ⇒ honest causal negative;
          │           passes & loss ⇒ full reciprocal cycle. It no longer GATES the ladder —
          │           the ligand-side double difference above does.
          │
       inverse_linker($0) ──► ternary_ensemble_refine ──► local_ternary_fep   (Cum ~$252)
          │
RUNG6  fold ──► redteam ──► post/submit                                ($0)

OPTIONAL/HELD (explicit nod only): dg_open_paralogue, abfe_conditional
```

**⚠ CORRECTION IN FLIGHT (2026-07-24):** the NR-V04 covalent feasibility panel's result is **under
correction** — its readouts describe the Elongin C interface rather than VHL↔NR4A1, so **it currently supplies
no GO** (details at its RUNG 3 entry). A corrected 14-leg re-run is built and unlaunched. Separately, the
`nrv04-descriptive-v3` co-folds were found to contain 14-3-3 epsilon where Elongin B belongs and have been
regenerated as `nrv04-descriptive-v4`. Evidence:
[research/modalities/nrv04-cofold-chain-forensics-2026-07-24.md](research/modalities/nrv04-cofold-chain-forensics-2026-07-24.md).

**Current front:** Rungs 0–1 done; the NR-V04 covalent feasibility panel (⚠ under correction), the NR4A differential surface atlas and
the **Tier-0 paralogue-unique reactive-residue map** are done ($0). **THREE lanes are live in parallel
(2026-07-24 PM)** — disjoint engines, providers and rungs, so none blocks another:
1. **valB_mini** on GCP L4 (free trial credit) — OpenFE ligand RBFE, 1 fs warmup → **2 fs production**, binary
   arm past production iteration 1680, no NaN.
2. **The 5a-KS known-answer benchmark** on Vast 4090 — **pmx + GROMACS** protein-mutation FEP (perses was
   retired the same day: its protein-mutation path is OpenEye-gated). Benchmark legs staged from RCSB with
   mutation-site verification and reference ΔΔG checked against **SKEMPI 2.0**. This lane can move the ladder's
   only *unscoped* rung from UNPRICED to priced.
3. **The NR-V04 retrospective** — **built, preregistered, and NOT launched (2026-07-24 night).** Its co-folds
   are regenerated clean (`nrv04-descriptive-v4`) and staging passes, but **no retrospective leg has produced a
   result yet**; three infrastructure defects (kernel OOM, error-swallowing monitoring, the 25-input dispatch
   cap) are fixed in code and **unproven on hardware**, so the next launch is a **pilot, not a fan-out**.
   ★ **Picking this up? Read
   [research/modalities/nrv04-retrospective-handoff-2026-07-24.md](research/modalities/nrv04-retrospective-handoff-2026-07-24.md)
   first** — state of play, exact dispatch commands for every resume path, cost ledger, and the traps.
   *(Its co-folding moved off SageMaker onto the Vast lane — see
   [research/compute/provider-deviation-2026-07-24.md](research/compute/provider-deviation-2026-07-24.md).)*
**Cross-session note (2026-07-24):** the 2026-07-24 ternary-selectivity revision demotes lane 2 from the paper's
*primary* causal result to its *confirmatory* second line. That does **not** cancel it and does not change what
lane 2 should be doing now — the known-answer benchmark is required under either framing, and this file gates
the confirmatory line on exactly that benchmark. What changes is downstream: the ladder no longer stalls if the
benchmark fails, because the ligand-side double difference carries the causal claim. Nothing with a GPU price
launches without an explicit go.

### ★ Bid policy — treat it as an optimisation; the interruptible discount is REAL (2026-07-24)

**⚠ A "there is no interruptible discount" claim was posted here earlier the same day and is RETRACTED.** It
rested on `min_bid == dph_base` across 7 card classes, which is a **tautology of the query type**: `_live_offers`
defaults to `interruptible=True`, so the search runs `"type": "bid"`, and in a bid-type search Vast reports
`dph_base` as your rate *at the floor*. Measured properly — a genuine on-demand query matched on `machine_id` —
machine 26385 prices on-demand compute at **$0.4533/hr against a $0.3733/hr floor, an 18 % discount**, with an
identical $0.003/hr surcharge on both sides. Bidding therefore has real upside and the limit-order policy below
stands.

**Now measured properly across 63 machines / 12 card classes:** the interruptible discount is **universal** —
median on-demand = **1.25× the floor**, IQR 1.14–1.68, and **zero hosts at parity**.

**THE NUMBER: `floor × 1.25`** on the cheapest host by measured $/ns, capped at that host's on-demand price —
$0.1667/hr on today's cheapest live 4090, vs $0.2533 under `×1.9` (**34 % cut, same box**). The earlier
"$0.30/hr reservation price" is retracted: it was a duty-cycle quantile, right for ONE price process, and Vast is
~23 independently-priced hosts you can see at once — you pick a host, you do not wait for a price.

**The bigger find was a bug, not a bid.** [Vast's docs](https://vast.ai/article/Rental-Types) say being outbid
**pauses** an instance with its data preserved and resumes it automatically; our reaper treated `"stopped"` as
terminal and DELETEd it, forcing a fresh ~6 GiB image pull. That self-inflicted ~20-min reload was the sole
justification for `×1.9` (*"re-bought+reloading repeatedly"*). Fixed via
`nrv04_vast_launch.instance_outbid`, which discriminates on `is_bid` / `intended_status` / `min_bid > price`
rather than on a status string; `exited` containers are still reaped, so the anti-idle guarantee holds.

**Selection dominates bidding**: cheapest 4090 floor $0.1333 vs median $0.3550 is a 2.7× host-to-host spread,
far larger than the ~1.20× discount available within a host. Full derivation in
[research/compute/bid-strategy.md](research/compute/bid-strategy.md).

**Policy (corrected same day — the snapshot answer optimised the wrong variable):** stand a **limit order at an
absolute reservation price `P*` and wait.** On Vast an interruptible bid **is** a limit order: it acquires when
the clearing price falls to `P*` and is preempted when it rises, so with per-unit checkpointing the job advances
during cheap periods, parks during expensive ones, and cost per unit of **work** is bounded by `P*`. Since this
program is never a race, waiting is close to free.

```
P* = clamp( max( no-churn floor(R),  economic threshold ),  ≤ on-demand )

economic threshold = √(m̂·d)                  if n < 12    cold start, distribution-free, worst-case optimal
                     UCB_q(observations, ρ)   otherwise    converges to the empirical quantile
                     d                        if ρ ≥ 1     deadline binding
ρ = W / (T·c)   the DUTY CYCLE we must sustain — the acceptance quantile is DERIVED from the deadline, not tuned
R = reload + ½·ckpt_interval·sec_per_iter
```

**⚠ Where the money is, corrected 2026-07-24 (trimcrae).** An earlier version of this section ranked "card
choice, up to ~3.6×" first, computed as if the L4 were a paid default. **It never was** — every L4 hour ran on
free GCP trial credit or Modal's free tier, and on Vast (the only cash lane) we have always used a 4090 or 3090
per job. A 3.6× gap on a $0 lane is **not a saving**; switching off it would *raise* cash spend. Ranked properly:
**(1) spend the expiring free credit** — ~$292 left, dies **2026-10-10**, but bounded (~$94/ternary edge as-run
on GCP L4 vs ~$13 on Vast 4090, so ≈**3 ternary edges**, not the ladder); **(2) bound the bid on
Vast** — `×1.9` is fine today but exceeds on-demand on 20/23 hosts and is unbounded as the floor drifts;
**(3) card choice *within Vast*** —
4090-vs-3090 already settled, 4080/A10 open pending the bench; **(4) bid level** — a real ~18 % interruptible
discount exists to capture, sized properly once the distribution lands.

**It needs no price history to start.** Backtested from a cold start on a seeded synthetic market
(`vast_bid_backtest.py`): **1.11× a clairvoyant policy that knows the whole price path**, versus 1.32× for the
best *fixed* threshold that knows the true distribution, and **3.51× for both `min_bid × 1.9` and
always-on-demand**. It beats the perfectly-informed fixed threshold because it relaxes as the deadline nears,
which no fixed rule can. *(Synthetic price process — this validates the algorithm, not the size of the saving.)*

The churn floor is the legitimate core of the old ×1.9 — expressed as a job property instead of a market
multiple. If it binds, **tighten checkpointing rather than pay more**; they are substitutes. Take on-demand only
when waiting is genuinely unavailable (hard deadline, or a leg that cannot tolerate preemption at all). Rank
offers by expected **$ per completed unit**, never by the floor. The hourly sampler (`.github/workflows/vast-price-sample.yml`, read-only, $0) builds the real series and only
improves the policy — it is no longer a blocker. `gpu_backend` stays unchanged until the policy is exercised on
a real launch.

**Decision status (2026-07-24)** — detail + evidence in the [revision
doc](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md) §8:

1. **`[x]` ADOPTED — method calibrator swapped from NR-V04 to SMARCA2-vs-SMARCA4** (valB_full module 3). NR-V04
   stays the biological holdout; its selectivity is most plausibly covalent target engagement, and SMARCA2/4 is
   already staged in-repo.
2. **`[x]` ADOPTED — the protein-mutation wedge is demoted from primary to confirmatory.** The ligand-side double
   difference is the paper's headline causal evidence and runs on the lane Val B already has an accuracy control
   for. The mutation cycle is kept, not deleted: if its known-answer benchmark passes, the paper gets two
   independent causal lines.
3. **`[x]` DECIDED (trimcrae delegated judgement, 2026-07-24) — adopt 4 fs, but TWO-STAGE.** Production really
   is at 2 fs (1 fs warmup), verified on the live lane, so the ~2× lever is live. Rather than buy the full
   matched calibration up front, apply cheapest-decisive-first *within* the rung: **stage 1 — a ~$1–2 survival
   probe** (`prod_iters≈200`, `use_preequil=1`, `timestep_fs=4.0`, `warmup_timestep_fs=1.0`, `reset_commits=1`)
   asking only "does 4 fs survive well past the 40 iterations the runbook demonstrated?"; **stage 2 — the full
   matched re-calibration edge**, only on a passing probe. A NO at stage 1 costs ~$1–2 instead of a full edge.
   **Sequenced after valB_mini's 2 fs result lands** — both because the calibration needs something to compare
   against, and because dispatching into that lane now risks cancelling another session's run.
4. **`[x]` DECIDED — HOLD the step1 fan-out; do NOT resume the 19-edge tranche.** *(Price updated 2026-07-25:
   the tranche is **~$36, not ~$91–101**, so it **no longer crosses the >$50 review gate** that was one reason
   it was halted. **The decision stands on the scientific reason below, which is independent of price** — a
   cheaper way to optimise the wrong objective is still the wrong objective. Un-halting is trimcrae's call, and
   it is now a cheaper call than it was.)* Nothing is lost by
   re-scoping: **0/19 units produced a ΔΔG**. And under mechanism-first the fan-out's *selection criterion* has
   changed — the exit vector must now be able to carry a linker toward **C397** (10.9 Å) and orient the E3 so the
   transfer zone covers **K572/K518/K592**, which is not the same as ranking substituents by affinity. Resuming
   the old edge list would spend ~$36 optimising the wrong objective. **Order: run 5a's $0 basin search
   first** (it tells us which exit vectors matter), **then** a re-scoped, smaller fan-out — with a cycle-closure
   edge moved early, per that session's own note that all three cycles currently close only in the last wave.
