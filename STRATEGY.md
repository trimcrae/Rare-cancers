# STRATEGY — the NR4A3-selective degrader paper

> # ★ GOLD-STANDARD SINGLE SOURCE OF TRUTH FOR THE RESEARCH STRATEGY ★
> **This file is THE strategy** — the authoritative plan for the repo's #1 research program, the
> **NR4A3-selective degrader paper**, and what CLAUDE.md and README.md point to for "what's the plan / what's
> next / what does each step cost." If any other doc (the schedule JSON, a strategy note, a manuscript section, a
> commit message) conflicts with this file, **this file wins** — reconcile the other doc to it.
>
> **Keep it current.** When work lands: update the stage's `[ ]/[~]/[x]` status here AND the mirrored `status` in
> [degrader-paper-schedule.json](research/manuscripts/degrader-paper-schedule.json) (its milestone `id`s match the
> stage tags below one-for-one; that JSON is a machine MIRROR of this file, not a competing source).
>
> **Three editing rules that keep this file from rotting** (it has been re-corrected three times; the failure
> was always the same — a number lived in four places and a fix reached one):
> 1. **One fact, one place.** Every number, gate and decision has exactly one home section. Everywhere else
>    points at it. If you find yourself restating a cost, delete the restatement.
> 2. **Corrections go in [§Appendix A](#appendix-a--superseded-numbers-and-retracted-claims), not inline.** Never
>    quietly drop a superseded number — but never leave the retraction narrative in the live plan either. One
>    line in the appendix, then the live text carries only the current value.
> 3. **Register the old value when you change a pinned one**, in the same commit, in
>    [`pinned-figures.json`](research/manuscripts/pinned-figures.json). Rules 1–2 are *enforced* by
>    [`lint_consistency.py`](research/manuscripts/lint_consistency.py) in CI — it fails the build when a total
>    does not equal its parts or a superseded value is restated unmarked. Run it before you commit:
>    `python3 research/manuscripts/lint_consistency.py`.
>
> **Companion docs (detail only, subordinate to this file):**
> [research/compute/pricing.md](research/compute/pricing.md) — ★ PRICING single source of truth, every cost line
> linked to its justifying test · [research/compute/bid-strategy.md](research/compute/bid-strategy.md) — host
> selection and bidding · [reviewer verdict](research/manuscripts/nr4a3-degrader-reviewer-revisions-2026-07-15.md)
> (verbatim) · [ternary-first strategy note](research/manuscripts/nr4a3-degrader-strategy-ternary-first.md)
> (biological/chemotype rationale) · [**ternary-selectivity strategy revision
> 2026-07-24**](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md) (evidence behind
> the mechanism-first search and the six cost levers) ·
> [the manuscript](research/manuscripts/nr4a3-degrader-paper.md) itself.

---

## ⏱️ IN FLIGHT — what is actually running right now (as of **2026-07-25 1:20 PM ET**)

*Keep this section current. It is the first thing a fresh session should read to know what is executing, what
is blocked, and what a returning result will decide. Delete a row when it lands and fold the result into the
relevant rung below.*

> ### ★★ STANDING DIRECTIVE (trimcrae, 2026-07-25 1:15 PM ET): **ALL TESTS RUN ON VAST.**
> Every new GPU run goes on **Vast** under the existing pricing strategy — RTX 4090 default, RTX 3090 fallback,
> offers ranked by all-in **`$/ns`** (never headline `$/hr`), bid = market floor + a staleness tick **capped at
> that machine's on-demand price** (the `×1.5` / `×1.9` multipliers are retired). Provenance:
> [pricing.md](research/compute/pricing.md) · [bid-strategy.md](research/compute/bid-strategy.md).
> **This supersedes the "spend the expiring GCP free credit first" preference** recorded in §GPU economics and
> §Bid policy for *new* work. It does **not** retroactively kill the valB_mini reverse leg already running on
> GCP L4 — killing a leg mid-flight to change provider would forfeit its progress for nothing — but **no new
> GCP / SageMaker / Modal run may be started.** The GCP trial (closes 2026-10-10) is now a stranded asset, not
> a routing preference; if that trade is to be revisited it is a trimcrae call, not a session's.
>
> **⚠ CONSEQUENCE FOUND IMMEDIATELY — THE SESSION-INDEPENDENT WATCHDOG DOES NOT COVER VAST (2026-07-25 1:30 PM ET).**
> [`ternary-leg-watchdog.yml`](.github/workflows/ternary-leg-watchdog.yml) is **GCP-only by construction**: it
> authenticates to GCP via WIF, reads its state from **GCS**, asks "is a `gcp-ternary` **VM** up?", and its sole
> recovery action is to re-dispatch **`gpu-ternary-fep-gcp.yml`**. Registering a Vast leg with it yields
> monitoring that *silently watches nothing* — the exact defect class that produced seven false-success
> diagnostics on this lane earlier the same day. So the directive above creates a real gap: **as of now no
> GPU run the program makes has durable, out-of-session monitoring.** A Vast-capable watchdog is being built
> alongside the Vast ternary lane. Two things the GCP version has no analogue for and which must not be
> dropped: (1) on Vast **"alive" is not "advancing"** — a rented box can sit up with a dead container or an idle
> GPU, so the check must require the committed-iteration count to have *increased* since the previous tick;
> (2) a **capacity refusal is not a preemption** — `resources_unavailable` means destroy, exclude the machine
> id, and pick another host, never wait and never raise the bid. Note a `schedule:` trigger only fires from the
> **default branch**, so any such watchdog is inert until merged to `main`.

| what | state | ETA | what its result decides |
|---|---|---|---|
| **valB_mini rev ternary leg r0** (GPU L4 spot, VM `gcp-ternary-30165768667`, us-central1-a) | **RUNNING** since **12:34 PM ET**, `live_vms=1`, `NaN=no`, `charge=nagl`. **This is the second attempt** — the 11:57 AM ET launch (VM `gcp-ternary-30164631671`) is no longer live. ⚠ Its committed-iteration counter is **not readable**: the `[PROGRESS-SUMMARY]` numbers are leg-wide across salts and are currently reporting the **forward** leg (trap 1 below) | ~10–20 h detached → **result 2026-07-26 AM ET** | **\|ΔG_fwd + ΔG_rev\| — the preregistered antisymmetry/hysteresis check, still `null` on all three legs.** ≈0 ⇒ the r0 systematic is in the MODEL or the REFERENCE DATA ⇒ rescope the calibrator. Large ⇒ interface substates / alchemical path ⇒ the rescope design itself must change first |

| **LANE 1 · RUNG 5a — E3 recruiter staging + ligandability downselect** (CPU/CI, $0) | running — staging the widened ligandable set (VHL, CRBN, cIAP1/BIRC2, DCAF1, DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2) from RCSB via a CI runner | ~1–3 h → **this afternoon ET** | Which **≤2 recruiters** 5a carries into any GPU leg, and the logged dropped set. Availability is already answered and may **not** be a drop reason — the downselect is on ligandability + interface geometry |
| **LANE 2 · RUNG 5a — Mechanism-first orientation-basin search** (CPU, $0) | running — building the transform search + the two **categorical** terms (electrophile reach to C397/C420/C559; E2~Ub transfer zone over K572/K518/K592), pose-marginalised | ~3–6 h → **this evening ET** | **The Tier-2 gate.** No basin exploiting a categorical handle *and* none nominally discriminating NR4A3 ⇒ STOP cheaply. Also tells the program which **exit vectors** matter, which a re-scoped fan-out depends on |
| **LANE 3 · RUNG 3 — NR-V04 covalent chain-fix recovery** ($0 first, Vast ≤$15 only if forced) | running — testing whether the corrected R1/R2/R3 can be recomputed from the **already-committed** trajectories, since the defect is in the analysis (which chain is "target"), not the physics | ~1–2 h for the $0 verdict | Whether RUNG 3's **withdrawn GO** is recoverable for **$0**. If yes, ~$6–8 of re-run is avoided outright; if no, one pilot leg proves the chain split before any fan-out |
| **LANE 4 · RUNG 2b — 4 fs ternary probe** (**Vast**, ≤$25) | running — building the **Vast** ternary lane (none existed; only `-gcp.yml`/`-aws.yml`), then stage 1 = the ~$1–2 survival probe | probe ~2–4 h → **this evening ET**; full edge next if it passes | **≈2× on every downstream ternary leg** (~$8.8 → ~$4.4/edge, ladder has ≥6). Also the **first NR4A-adjacent ternary leg timed on Vast** — closes the named transferability gap where an 8G1Q rate is pricing NR4A ternaries |
| **LANE 5 · RUNG 2 — valB_mini calibrator rescope + gate defect + r0 ligand RMSD** (CPU, $0) | running — closing `diagnostics_complete: false`, preparing the admits-zero defect-fix for approval, designing both rescope options | ~2–5 h → **this evening ET** | The **next step the moment the rev leg lands** — designed for *both* branches of it, so the decision is not serialized behind the result |

> **⚠ NAMING CORRECTED (2026-07-25 1:50 PM ET) — these were first written as "5a-1…5a-5", which was wrong and
> actively misleading: it read as though all five were sub-parts of RUNG 5a, and it invited the reasonable
> question "didn't 5a-KS already run?". Only LANES 1–2 are RUNG 5a. The five span rungs 2, 2b, 3 and 5a, which
> is exactly *why* they parallelise.**
>
> **And 5a-KS has NOT run.** What ran on 2026-07-25 is the **known-answer qualification benchmark for its
> CONFIRMATORY second line** (pmx + GROMACS on barnase–barstar Y29A/Y29F — both within ±1.5, ordering correct).
> That validates the **engine**, not the wedge: it is barnase–barstar, not NR4A. The rung's **PRIMARY** test —
> the ligand-side double difference `S = ΔΔG_coop(d₀→d|NR4A3) − ΔΔG_coop(d₀→d|NR4A1)` — **has never run and
> cannot yet**, because it needs a candidate *d* and matched control *d₀*, and those molecules do not exist
> until 5b enumerates them from the basins LANE 2 is nominating now. 5a-KS is therefore **downstream** of
> LANES 1–2, not a blocker on them. Its confirmatory line is now **PROJECTED at ~$4.6 (3 rep)** rather than
> unpriced — but that figure is **particle-count-scaled** from the ~25.7k-particle benchmark to NR4A sizes, an
> assumption and not a measurement, so it may not be quoted as a rate and stays excluded from the ladder total.

**The five LANES above are this session's, and are disjoint from the reverse leg by construction** — four
are $0 CPU/CI and the one GPU lane runs on **Vast**, so none can dispatch into, cancel, or share checkpoints
with the GCP lane the reverse leg owns. The rescope-vs-continue decision on valB_mini is still deliberately
**held** until the reverse leg reads out — it is the one cheap test that can falsify the "systematic, not
sampling" conclusion the current recommendation rests on — but the *design* for both of its outcomes is being
built in parallel (lane 5) rather than after it.

*Landed 11:55 AM ET, hence off the board:* the **rev setup prime** (CPU, `ternary-setup-prime-cpu.yml`, run
30163606577) **succeeded** — the first primer run since the `setupcache/` IAM 403 was granted, so the write half
of that fix is proven end-to-end. **Not yet verified:** that a leg actually *restored* from that cache rather
than rebuilding — the restore happens inside the detached VM, and the discriminator is step duration, not status
(trap 2). Confirm it on the next tail; it matters because the unprotected rebuild window is what killed the
*first* rev attempt (VM `gcp-ternary-30162403453`, spot-preempted 11:02 AM ET, 12 min in, mid-build).

**⚠ The rev leg has now been launched three times (11:57 AM, then 12:30 PM ET), and WHY the second attempt
ended is not established here — do not assume preemption.** A concurrent session landed a fix on
`claude/max-effort-3hgq45` for a **direction-blind idempotent skip** — *"the rev leg found the FWD result and
reported success"* — which would make a rev launch exit early having matched the forward leg's output. That is
a **candidate** explanation with the right shape, not a diagnosis: it has not been checked against this leg's
log. Whoever picks this up owns that check before reading any rev result, because a rev leg that silently
reported the forward answer would make the antisymmetry test meaningless rather than merely absent.

### ⚠ Reading the ternary lane's monitoring output — two traps

1. **`warmup_committed_iter` / `production_committed_iter` in `[PROGRESS-SUMMARY]` are LEG-WIDE ACROSS SALTS.**
   They can report a *different direction's* legs. A rev-leg check showing `production_committed_iter=2000` was
   the **forward** leg's count, not progress. Misread three times on 2026-07-25.
2. **Step DURATION, not status, is what distinguishes these outcomes** — all at the same step, all "step 7":
   `~0.4 min + success` = a **cache restore that ran no build** (a hypothesis test built on this was silently
   void); `~0.5 min + failure` = the endpoint-construction radical; `~11.5 min + failure` = a real, complete
   build that failed only on the cache upload.

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

### MECHANISM-FIRST is the search order (the thesis above is unchanged)

Selectivity mechanisms are not interchangeable, and the program was pursuing the hardest one exclusively. Two
classes:

- **MARGINAL** — the paralogue is thermodynamically disfavoured. This is the induced-interface wedge. A useful
  degradation window needs **~2.0 kcal/mol** of true margin (median over 27 potency scenarios, range 1.75–2.25;
  [`selectivity_margin_model.py`](research/modalities/selectivity_margin_model.py)), against a best-case
  **resolvable** difference of **1.12 kcal/mol** (replicate SD 0.7, n = 3) and a method accuracy of ~1.7 kcal/mol
  RMSE — which does not even cover the NAGL ternary lane. Replicates shrink precision, not accuracy. **This axis
  is a confirmation tool operating near its limit, not a discovery tool.**
- **CATEGORICAL** — the paralogue is structurally *incapable*. NR4A3 carries reactive residues that BOTH
  paralogues lack, verified from full-length UniProt with two independent aligners
  ([`nr4a_paralogue_unique_residues.py`](research/modalities/nr4a_paralogue_unique_residues.py) →
  [`nr4a-paralogue-unique-residues.json`](research/modalities/nr4a-paralogue-unique-residues.json)):
  **C397** (NR4A1 N363 / NR4A2 S363; RSA 0.395, 10.9 Å from the cryptic pocket — exit-vector reach), C420
  (18.3 Å, exposed), C559 (12.8 Å but RSA 0.095 — buried in this conformer, so not currently tether-reachable);
  and exposed unique lysines **K572** (RSA 0.879, 11.5 Å), **K518** (0.413, 13.4 Å), **K592** (0.506, 16.2 Å),
  all in the same 11–16 Å band as the conserved ones — so an E3 can be steered onto a unique lysine instead of a
  shared one. At **zero** thermodynamic margin these give 0.82 (unique lysine) and 0.92 (covalent capture,
  time-integrating form) on the window metric where the interface-only null gives 0.185. **Precedent: the
  field's one demonstrated case of NR4A-family-selective degradation, NR-V04, is most parsimoniously explained
  by a paralogue-unique cysteine — NR4A1 Cys551, which NR4A3 lacks (T579).** That covalency remains a genuine
  confound for the retrospective (RUNG 4); it is *also* the reciprocal handle this program should use.

The program is therefore **mechanism-first, then orientation**: rank basins by whether they place an electrophile
at an NR4A3-unique cysteine and whether their E2~Ub transfer zone covers a unique lysine rather than a conserved
one; use interface thermodynamics to **rank within** the surviving set, never to create selectivity on its own;
test causality with a matched-pair cycle; and **STOP before the flagship spend if no mechanism survives** —
publishing the honest negative, now stronger because it rules out three mechanisms instead of one. The final
deliverable is a **computationally prioritized, structure-defined, retrosynthetically annotated candidate set
with an identified causal selectivity mechanism — degradation experimentally unvalidated.**

*Checked and reported weak, not quietly dropped:* the EWSR1 moiety of the fusion contributes only **1 lysine**
(residues 1–264, K144) or 2 (1–349) — the low-complexity domain is Lys-poor — so fusion-lysine-directed
ubiquitination is a thin handle and is **not** a design axis. It stays a modelling scenario only.

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

Enforcement: [`lint_claims.py`](research/manuscripts/lint_claims.py) implements rules R1–R5 from this section
against the paper + SI and runs in CI on every push. It is sentence-scoped — a disclaimed use of a regulated
word passes; asserting the regulated claim does not.

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
   attachment alters the bound ensemble, so free-cmpd19 ABFE ≠ each degrader's binary affinity. **HELD also means
   the λ-overlap repair of the existing ABFE block is parked, not in flight** — the manuscript must say so.

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

**Val A (binary RBFE accuracy) — a citation, not a paid benchmark, FOR THE BINARY LANE ONLY.** We run OpenFE's
*standard* RelativeHybridTopology protocol, already benchmarked (~1.7 kcal/mol over 58 public systems). The only
thing that had made it non-citeable was a self-inflicted deviation — the RBFE env shipped without AmberTools, so
am1bcc charging failed and fell back to the NAGL surrogate. With AmberTools added and `am1bcc` restored, the
**binary RBFE lane** is on the documented reference method → we **cite OpenFE** and run only a ~$0–15
build-consistency smoke (valA_mini, done).

**The charge model is NOT shared across lanes.** The lanes split:

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
2. **Any CROSS-LANE subtraction is NOT safe.** A quantity built as `(ternary-lane leg) − (binary-lane leg)`
   mixes NAGL against am1bcc, and a charge-model difference is a real potential-energy-surface difference that
   does **not** cancel. Such cycles must pin one `CHARGE_METHOD` across **both** legs — this is why the
   protein-mutation wedge (RUNG 5a-KS confirmatory) carries a hard `assert_charge_consistency` refusal.
   (Timestep differs across lanes too — 2 fs ternary vs 4 fs+HMR binary — but HMR changes only masses, so that
   is a *sampling/precision* difference, not a bias in ΔG.)
3. **Val A's citation does not cover the NAGL lanes.** OpenFE's published ~1.7 kcal/mol accuracy was measured on
   the am1bcc method; valA_mini reproduced a known ΔΔG on am1bcc. Neither transfers to a NAGL ternary lane. The
   accuracy control for the NAGL lane is **Val B** (its own known-answer PROTAC) — which is why valA_full's
   "re-open if am1bcc is forced onto NAGL" trigger is satisfied *by Val B* and not by a separate paid NAGL
   binary benchmark. Say this in the paper; do not let a reader infer the OpenFE citation covers the ternary
   numbers.

**Val B (ternary cooperativity) — genuinely needed, for pipeline-validation.** The general approach is citeable
(prior art above), but you never certify your own container / force field / charge model / ternary wiring by
pointing at someone else's engine's benchmark. NR-V04 cannot calibrate it (no solved ternary; celastrol is
covalent, so it doesn't even exercise the noncovalent morph). The only way to know our cooperativity numbers
mean anything is to run a known-answer PROTAC (VHL–BRD4 / VHL–SMARCA2) through our own pipeline. **Val B-mini is
the highest-value dollar in the plan** — the cheapest gate on the entire prospective ladder.

---

## The prospective stage: mechanism-first, then orientation-first inverse design

The molecule-first approach — enumerate a fixed {warhead×exit×ligase×linker} matrix, model each ternary, score,
and hope the Pareto front contains a selective degrader — is a well-controlled lottery: it *verifies* selectivity
if already present but never asks the design question. Orientation-first fixed that. Putting the **mechanism**
above the orientation fixes what the orientation search is optimising:

```
paralogue-unique CHEMISTRY (nucleophile) + paralogue-unique GEOMETRY (lysine)
    → basins that exploit ONE of them → productive CRL geometry
    → interface thermodynamics used to RANK within the survivors
    → linker requirements → candidate molecules
```

This removes blind linker guessing and preserves everything requirement 5 mandates (Pareto/uncertainty,
EWSR1::NR4A3 fusion context, lysines beyond the LBD, full CRL/E2~Ub ensembles). Four additions to the basin
search, all **$0 CPU** (rationale and evidence: the [2026-07-24
revision](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md)):

- **(a) Electrophile-reach term** — does the basin's linker path pass within tethering distance of C397 / C420 at
  a geometry a mild electrophile could adopt? Neither sits *inside* the pocket, so this is an electrophile on the
  **exit vector or the linker**, which in a degrader is architecturally free — the linker already leaves the
  pocket and travels 10–20 Å. **Prefer a REVERSIBLE-covalent handle** (cyanoacrylamide-type): an irreversible
  adduct makes the degrader stoichiometric and forfeits catalytic turnover, the property that makes PROTACs
  attractive. Electrophile promiscuity is an unresolved liability with no wet lab to check it, and must be
  reported alongside the parent warhead's MYC induction, not buried. *(C559 is unique and 12.8 Å out but buried
  at RSA 0.095 in this conformer — carried only as a candidate the MD-ensemble add-on could reopen.)*
- **(b) Transfer-zone lysine-identity term** — which lysine does the modelled E2~Ub transfer zone cover? Score
  *unique-only* highest, *unique + conserved* next, *conserved-only* lowest. This is set membership, not energy.
  Honest limit: real degraders often ubiquitinate several lysines and lysine-less substrates can still be
  degraded (N-terminal / Ser / Thr / Cys ubiquitination), so this **raises the odds; it does not guarantee** the
  paralogue is spared.
- **(c) E3 breadth, free at the search stage** — widen beyond VHL/CRBN to the ligandable set with public
  ligand-bound structures (cIAP1/BIRC2, DCAF1, DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2). Since basin search is
  CPU this costs ~nothing and multiplies the chance that *some* E3 surface complements NR4A3's differential
  surface. **Downselect to ≤2 recruiters before any GPU leg, and log what was dropped** — a silent top-N reads as
  "we covered everything". Availability is already answered and does **not** constrain the choice (RUNG 5a).
- **(d) Pose-marginalisation, free** — run the basin search over the warhead-**pose ensemble** and carry only
  basins that persist, reporting the surviving fraction. Sequence-level uniqueness of C397/K572 is
  pose-independent; only the *reach* estimate is conditional, which is a far smaller conditional surface than the
  stage currently carries.

Five load-bearing pieces:

1. **A paralogue-differential surface atlas (free, CPU).** NR4A1/2/3 in a **matched** ensemble — homologous
   frames, identical pose hypotheses, protonation, target–E3 transforms, and sampling — mapping E3-reachable,
   solvent-exposed, divergent residues and lysines (LBD / hinge / DBD / fusion partner, separately). Output is a
   discrimination **map**, not three receptor models; states are explicit scenarios unless populations are
   defensibly estimable. **Done** (RUNG 4).
2. **Orientation-space search before real linkers.** For each ligase, sample many relative transforms of
   VHL/CRBN around the warhead-bound target under a flexible linker-reach restraint; keep only interfaces that are
   favorable on NR4A3 and systematically weaker/frustrated on NR4A1/2, bridgeable, clash-free, ensemble-compatible,
   and place an accessible lysine in a productive transfer region. Cluster into **~3–8 basins per ligase**.
3. **Wedges proven by a matched-pair causal cycle — the primary causal test.**
   **PRIMARY: the LIGAND-side double difference, on the lane Val B calibrates.** For a candidate *d* and a
   matched control *d₀* differing only in the element that engages the wedge,
   `S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)`. Each term is an ordinary relative alchemical quantity
   *inside one protein*; the difference asks the **design** question — does this structural element create
   paralogue discrimination? It needs **no protein-mutation engine**, makes **no cross-lane subtraction**, and by
   the cancellation identity (cost lever 2) needs **only ternary legs**. This is far stronger than observing
   ΔG_ternary,3 < ΔG_ternary,1.
   **CONFIRMATORY: the reciprocal PROTEIN-mutation cycle.** For a target-surface mutation *m*,
   `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` (the binary leg subtracts mutation effects from the
   target–warhead complex, isolating the recruited-interface effect). A strong wedge shows a favorable NR4A3
   interface, **loss** on NR4A3→NR4A1/2 mutations, **partial gain** on reciprocal NR4A1/2→NR4A3 mutations,
   persistence across frames, and a recognizable steric/electrostatic/H-bond mechanism. Its engine is built and
   its known-answer benchmark **passed 2026-07-25** (RUNG 5a-KS), so it gives a second, independent causal line —
   but the paper's headline causal result is not hostage to it. **ADOPTED 2026-07-24 (trimcrae go).**
4. **Separate ACCESSIBILITY from STABILITY.** Estimate `P(B_k | d, s)` (can the linker reach and hold basin *k*?)
   separately from `ΔG_coop(d, B_k, s)` (is the orientation plausible?). A favorable basin the linker rarely
   accesses is irrelevant.
5. **Robust constraint-satisfaction selection.** A candidate advances only if it satisfies preregistered
   constraints across a required fraction of scenarios (binary non-destabilization; basin populated in replicated
   MD; NR4A3 advantage over **both** paralogues under perturbation; ≥1 NR4A3-specific contact survives
   counterfactual mutation; ubiquitin near an accessible NR4A3 lysine in a meaningful CRL-conformer fraction;
   credible unstrained linker). Rank by `P_d = P(all constraints hold)`, robust to dropping any one favorable
   scenario — this kills the best-of-N winner's-curse artifact a raw Pareto set still admits.

### The hard kill-switch — tiered, cheapest-decisive-first

No causally-confirmed NR4A3 wedge ⇒ **STOP**: no linker matrix, no ensemble refinement, no flagship spend;
publish *"we mapped orientation space and no robust NR4A3-discriminating, ubiquitination-compatible basin
survives causal testing."* The *decision* to commit the flagship is cheap, not a gate on the whole tail:

| tier | test | cost | status |
|---|---|---|---|
| **0** | **Categorical-axis screen.** No paralogue-unique nucleophile within tether range AND no paralogue-unique exposed lysine ⇒ selectivity must come from the marginal axis alone, which sits at the method's resolution limit ⇒ say so and expect a negative | **$0 CPU** | **PASSED — GO on both axes** (C397 at 10.9 Å exit-vector reach; K572/K518/K592 exposed) |
| **1** | **Differential surface atlas.** No E3-reachable divergent surface ⇒ STOP for free | **$0 CPU** | **PASSED** (46 handles) |
| **2** | **Basin nomination.** No basin exploits a categorical handle *and* none even nominally discriminates NR4A3 ⇒ STOP cheaply | **$0–50** | pending (RUNG 5a) |
| **3** | **Pilot ONE causal direction** — the ligand-side double difference `S`, one matched pair, ternary legs in NR4A3 and NR4A1. No discrimination ⇒ STOP | **~$12 ($1.6–45)** | pending (RUNG 5a-KS) |

Tier 2's asymmetry is what makes it usable: cheap scoring has poor S/N for a ~1 kcal/mol *energy* difference, so
it only **nominates** — but "does this basin place an electrophile at C397 / cover K572?" is a **geometric**
set-membership question, which cheap scoring answers reliably. A gross absence of signal is an informative
NO-GO; it is not trusted to kill a real small wedge.

---

## Spending rules

1. **No pre-authorization, no pre-staging.** Nothing is ever queued to auto-fire. Every GPU run is presented at
   its gate with (a) the prior step's result, (b) a pinned cost (from realized GPU-h, not a guess), and (c) a wait
   for an explicit trimcrae "go." Only $0 CPU/CI work runs without a nod.
2. **Spend-gated ladder, cheapest-decisive-first.** The cheapest run that could kill the paper comes first; each
   rung's bigger spend unlocks only if the previous, cheaper rung looks promising. Never pay for an expensive
   stage on a hypothesis a cheap stage could have falsified.
3. **GO/NO-GO after every priced rung.** Each rung ends with an explicit test; NO-GO = stop or pivot.
4. **Every step is priced bottom-up per edge** on the Vast-4090 bases below; provenance in
   [pricing.md](research/compute/pricing.md). A step whose engine has no completed benchmark leg is carried as
   **PROJECTED and excluded from the pinned total**, never at a fake number.

## GPU economics (full provenance in [pricing.md](research/compute/pricing.md))

**All production runs go on Vast.** GCP L4 / SageMaker / Modal are not the go-forward basis. **The card is not
the decision — the OFFER is.** Rank live offers by all-in **`$/ns`** (bid + storage ÷ measured throughput) and
take whatever wins; the top 10 routinely contain both 4090s and 3090s. Validated throughput @84,534 particles is
**4090 755.36 / 4080 703.51 / 3090 359.36 ns/day** (4090/3090 = **2.10×**), while the cheapest 3090 floor was
**$0.0147/hr** against **$0.1310** for the cheapest 4090 — an **8.8×** price spread that more than covers being
2.10× slower. VRAM is never the constraint (≥24 GB is ample). A 3090 does need 2.10× the wall clock, so a leg
with a hard continuity requirement is 2.10× more exposed on it — scaled and flagged per card, not ignored.

- **★ PLANNING RATE: $0.137 per reference (4090) GPU-hour** — best-10-offer mean on the live board; range
  $0.057 (best offer) to $0.309 (median). Against the **$0.35–0.39/hr `step1_fanout` actually paid**, that is
  **2.6–2.8×**. Best-to-median spread is **5.43×**, so *selection* is the dominant lever — worth several times
  the bid policy.
- **Bid = the market floor plus a staleness tick** (`min_bid × 1.02`, min +$0.0005), **capped at that machine's
  on-demand price**, never at or below the floor. Measured 2026-07-25 by renting one offer at three bid
  multiples: **`charged = min(your bid, the machine's on-demand price)`** — so a premium is paid on *every*
  hour and cannot buy safety from on-demand renters. Retention is bought with **checkpoint frequency**, which is
  free. Every multiplier this repo has used (`×1.1`, `×1.5`, `×1.9`, `×1.25`) is retired; derivation, the
  measured bid ladder, and what retired each one are in
  [bid-strategy.md](research/compute/bid-strategy.md). `VAST_BID_FLOOR_MULT` survives only as an unset escape
  hatch for a leg that genuinely cannot be paused.
- **Storage is a real line, not a rounding error** — ~$0.011/hr at the 40 GB the launcher requests, which on the
  *best* offer is 42 % of all-in cost. Ask for the disk the job needs.
- **On a `resources_unavailable` refusal, pick another host — do not wait it out.** Vast is a market of ~23
  independently-priced machines you can see at once, not a pool; the floor is flat day-to-day, so a different
  host today costs what this one will cost tomorrow. `protfep_vast_launch.collect` records and destroys the
  machine and `ResourceSpec.exclude_machine_ids` keeps selection off it — a host that never starts has infinite
  realised $/ns, which the ranking cannot otherwise see.

### Per-edge bases — one extrapolated, one rate-measured, one converted

**None is a completed end-to-end edge on a 4090.** That caveat is the reason every stage cost below is a
bottom-up estimate rather than a total.

| basis | value | how it was obtained |
|---|---|---|
| **RBFE binary edge** (complex+solvent, ~35k atoms) | **~13.7 ref GPU-h ≈ ~$1.9** | Live-diagnosed per-iteration rate on the **real cmpd19/NR4A3** complex — 12.76 / 13.70 / 14.42 s/iter on three independent Vast 4090 hosts (16 samples each) — × the hardcoded 2400-iteration leg. A clean end-to-end ΔG was **not** captured (both spot instances preempted), so this is an extrapolated rate, not a completed-edge measurement |
| **Ternary cooperativity edge** (3 replicas, ~146k particles, 12 windows) | **~$8.8 ($3.2–22)**, 56–72 ref GPU-h | Rate **measured directly on a Vast 4090** (firm leg via `run_ternary_leg.sh`, self-staged 8G1Q, 146,284 particles): warmup clean, production steady at **~14–18 s/iter (median ~16)**. Leg length **confirmed at 2400 iterations** (400 equil + 2000 production at 2.5 ps/iter, `nr4a3_ternary_fep.py:343-344`) — and now *observed*: valB_mini's ternary seed 0 reached **2000/2000** production iterations. 2400 × 16 s ≈ **~10.7 GPU-h/leg** × 2 legs × 3 replicas ≈ **~64 GPU-h/edge** |
| **Endpoint-MD leg** (~466k atoms) | **~$0.19**, ~1.38 ref GPU-h | Backed out of the **completed** 18-leg NR-V04 covalent panel: ~$0.43/leg realized on a 3090 at ~$0.10–0.21/hr ÷ the validated 2.102× card ratio. The one basis resting on a completed multi-leg ledger; the 4090 conversion itself is inferred |

**Two live transferability warnings.** (i) The ternary rate was measured on the **SMARCA2/VHL 8G1Q** assembly
and is being used to price **NR4A** ternaries — the *same* move that cost 2.6× on the binary lane when the real
cmpd19/NR4A3 complex turned out to sample at ~13.6 s/iter against TYK2's ~5.2. Expect an NR4A ternary leg to be
heavier, not lighter; time one before treating these rows as firm. (ii) The **L4→4090 card ratio is validated at
~2.06×** (33 → 16 s/iter) — a ratio of rates is count-independent, so that conclusion is solid.

**Provider reality check.** The ladder is *priced* in Vast-4090 dollars, but `valB_mini` is *actually running* on
**GCP L4 on-demand**, a lane pricing.md bills at ~$94/edge. That is a deliberate use of the **expiring GCP free
trial** (~$292 left of $300, window closes **2026-10-10**; Modal's $30/mo is already $27.54 spent and does not
carry over) — free credit beats cheap cash, and it buys ≈3 ternary edges, not the ladder. But it means
**realized spend and ladder spend are two different ledgers**: `credit-status.json` records GCP `spent: 8.0`
from a **manual** source not yet reconciled against the ~8 dispatched L4 legs. Track GCP burn separately, and do
not let "we spent ~$2 so far" imply the L4 lane was free.

### Cost levers adopted 2026-07-24 ([evidence](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md))

1. **4 fs ternary production ≈ 2× cheaper per leg — PROPOSED, one paid step settles it.** Iterations are
   timestep-independent (2.5 ps/iter), so 4 fs is exactly half the force evaluations → **~$8.8/edge → ~$4.4**.
   **The as-run lane is 1 fs warmup → 2 fs production**, verified against the live VM, not the doc (GH run
   30123894814 `mode=tail` on VM `gcp-ternary-30112102294`: `[tfep] timestep=2.0 fs`,
   `warmup_dt_override="WARMUP timestep overridden to 1.0 fs"`, `NaN_seen=no`; `gpu-ternary-fep-gcp.yml` defaults
   `timestep_fs: 2.0`, `use_preequil: 0`). The "4 fs" people remember is the runbook §1c *pre-equilibration
   demonstration* — after plain-MD pre-equilibration the calib leg ran warmup 48/48 @1 fs → production 40/40
   @4 fs, zero NaN, ΔG_morph 47.28 ± 0.53, where every prior attempt died at warmup iteration 1 — i.e. 40
   production iterations, not 2000, and it held **only because** pre-equilibration was on. Settling step: RUNG 2b.
2. **The binary and solvent legs cancel EXACTLY in any paralogue comparison — up to 2×.**
   `nr4a3_ternary_fep.py` defines `binary_<e3>` as **E3 machinery + PROTAC with NO target**, and solvent as
   ligand-in-water. Both are **paralogue-independent**, so for any morph
   `ΔΔG_coop(P) − ΔΔG_coop(P′) = ΔG_ternary,P − ΔG_ternary,P′` **exactly.** A 3-paralogue comparison therefore
   needs **3 ternary legs + 1 shared binary + 1 shared solvent — NOT 3 edges** (18 legs vs 12, −33 %; 9 if only
   the selectivity contrast is needed, −50 %). **Never price a paralogue panel as N edges again.** And the
   saving is *larger* than the leg count suggests: the `binary_vhl` leg ran at **~28.6–38.2 s/iter (median ≈33)**
   on L4, the *same* rate as the ternary leg — a shared binary leg is a full-price leg paid for once instead of
   N times.
3. **Sequential (anytime-valid) stopping instead of a fixed 3 replicas — ~20–25 %.** `adaptive_certify.py` and
   `adaptive_allocator.py` are already built and unit-tested and are **not wired into the ternary ladder**. Run 2
   replicas; add the 3rd only where the decision is not yet determined at the preregistered margin.
4. **Free gates lead.** `selectivity_wedge_confirm` depended on `valB_full` + `nrv04_retrospective` (~$43) even
   though its validation need is matched-pair, not cooperativity-cube. Decoupled.
5. **Ligand-side double difference replaces the protein-mutation campaign** as the primary causal test — which
   at the time had no engine at all, and still has no NR4A-scale rate.
6. **E3 breadth is free at search, capped before GPU** (≤2 recruiters, dropped set logged).

*Operational Vast setup — image `triskit23/nr4a3fep:latest` (openfe ≥1.12 + ambertools + lomap/kartograf +
OpenMM pinned to CUDA 12.6), the `probe_offers` / `bench` / `firm` tooling in
[`nrv04_vast_launch.py`](research/modalities/nrv04_vast_launch.py), and the bid/ranking code of record in
[`gpu_backend.py`](research/modalities/gpu_backend.py) + `vast_cost_model.recommended_bid` — is documented in
[pricing.md §E](research/compute/pricing.md); not repeated here. The hourly read-only price sampler is
`.github/workflows/vast-price-sample.yml`.*

---

## THE ORDERED PLAN (spend-gated) — read top-to-bottom for "what's next"

Legend: `[ ]` pending · `[~]` in progress · `[x]` done · `[–]` skipped · `[!]` result under correction.
**Price** = spot $ for that step on Vast 4090; **Cum.** = running total if GO at every gate to here (mid-range).

### RUNG 0 — free / already done (~$0)

- **`[x]` Charge-model fix — am1bcc on the BINARY path** — **$0.** Added `ambertools>=23` +
  `partial_charge_method="am1bcc"`; the **binary RBFE lane** is on the documented reference method → cite OpenFE.
  The ternary and endpoint-MD lanes run NAGL — a *lane split*, not a shared charge model (see §Val A above).
- **`[x]` Step 0 — RBFE infra shakeout** — **~$1–2 · PASSED.** One OpenFE edge ran end-to-end via the spot-safe
  split and returned a converged **ΔG_morph = −48.75 ± 0.57 kcal/mol** (MBAR); am1bcc charging and the
  warmup→production→commit/restore driver are GPU-validated. **GO.**
- **`[x]` EMC E3-ligase expression** — **$0.** All 10 components of both CRL2^VHL and CRL4^CRBN are broadly
  expressed (HPA), so the VHL-vs-CRBN choice is **not** constrained by machinery availability — decide on
  geometry/selectivity. (No EMC line in HPA — general mesenchymal availability.)
- **`[x]` Pocket-tracking re-analysis** — **$0.** Harmonized detection folded into the paper's Gate-2 wording:
  8XTT **19/20 frames detected, 3 ≥ D\*=0.53** (= 3/19 among detected, 3/20 across all deposited); release
  continuations druggable in 56/40/80 % of frames per replica, **44/75 = 59 % pooled**
  (`nr4a3-pocket-reharmonize-summary.json`).

### RUNG 1 — reference-reproduction smoke (mostly a citation)

- **`[x]` Validation A-mini — build-consistency smoke + cite OpenFE** — **~$0 · Cum. ~$2 · PASS/GO.** The public
  TYK2 `ejm31→ejm42` edge (both legs, 5 ns × 12 windows) gave **ΔΔG_bind = +0.366 vs exp −0.24 → abs err 0.61
  kcal/mol**, inside the 2.0 tolerance. Our container reproduces a known ΔΔG on the standard am1bcc method → cite
  OpenFE's published ~1.7 kcal/mol accuracy. Does not touch NR4A. **GO to Rung 2.**
  *(Scope: this covers the **am1bcc binary lane only**. The old rider "if am1bcc is ever forced to NAGL, Val A
  reverts to a paid ~$25 NAGL benchmark" has in fact **already fired** — every ternary and endpoint lane runs
  NAGL because sqm cannot charge PROTAC-sized ligands. Resolution: **Val B is the NAGL lane's known-answer
  accuracy control**, already on the ladder. What this costs us is the *citation*: OpenFE's accuracy number may
  not be quoted for any ternary result.)*

### RUNG 2 — cheap precision + cheap probes *(only if Rung 1 = GO)*

- **`[x]` Step 1 pilot — cmpd19 conditional RBFE** — **~$2.8 ($0.8–8.5; 1–2 RBFE edges) · Cum. ~$4.** First edge
  `zaienne_cmpd19 → cw_ev_5nh2` (5-Br→5-NH₂) converged: complex ΔG_morph −29.68 ± 0.24, solvent −31.52 ± 0.26 →
  **ΔΔG_bind = +1.84 kcal/mol** (the 5-NH₂ analogue ~1.8 kcal/mol weaker *in the modeled opened pocket*). Proves
  the congeneric-RBFE pipeline converges on the real NR4A3 system without pocket collapse — the pilot's crux is
  cleared. Reproducibility replicas + pose/state sensitivity are carried forward as **fan-out inputs** (they
  refine per-edge `n_windows` and the conditional caveat, and gate the fleet). This is statistical convergence on
  a *hypothesized* pose, **not** an accuracy claim.

- **`[~]` Validation B-mini — all-binding graded cooperativity edge** — **~$8.8 ($3.2–22) · Cum. ~$13.** The Wurz
  SMARCA2–VHL **cmpd 1→4** all-binding graded edge (α 12.8→2.6 ≈ +0.94 kcal/mol; both endpoints are productive
  binders — the cleanest first calibration). Exercises the bespoke `ΔΔG_coop = ternary − binary` cycle that
  cannot be cited away. **GO/NO-GO (verbatim from the prereg in `degrader-paper-schedule.json`; the
  ±1.0 kcal/mol band was deliberately REMOVED on 2026-07-17 because a separation <1 kcal/mol makes a noisy
  positive point estimate INDETERMINATE — do not re-introduce it):** PASS requires **positive sign + CI excludes
  zero + no fwd/rev disagreement + no collapse/escape/restraint-dominated leg + broad consistency with the
  measured +0.94**. valB_mini gates valB_full only — it does **not** authorize the NR4A matrix; until valB_full
  passes, NR4A ternary scores are **exploratory**. *(The cis-epimer PROTAC-2 edge is demoted to the
  negative-endpoint stress module of the cube below — a pass forced by holding an unstable pose is not a pass.)*

  **As-run protocol** (this is what the cost basis and the paper must describe): `NWIN=12` λ-windows ·
  `CHARGE_METHOD=nagl` · `TIMESTEP_FS=2.0` (warmup 1.0 fs) · `TEMPLATE_PDB=8G1Q` · GCP **L4 on-demand**. Both of
  this lane's deviations — timestep and NAGL-vs-am1bcc — are registered in `md_settings.py`'s docstring. The 2 fs
  step is empirical: the cause of the earlier warmup NaN is the **softcore alchemical region in a large, rough
  homology-built assembly**, there is no static predictor, and the fix that works is **plain-MD
  pre-equilibration** (`ternary_preequil.py`), not a smaller timestep. Authority: `ternary-rbfe-runbook.md`
  §1b/§1c.

  **★ r0 IS IN, IT IS THE WRONG SIGN, AND MORE REPLICATES CANNOT FIX IT (2026-07-25). Full analysis +
  recommendation: [valB-mini-r0-verdict-2026-07-25.md](research/manuscripts/valB-mini-r0-verdict-2026-07-25.md).**
  The first complete cycle (CI 30148463967, re-dumped 30155238348) gives **ΔΔG_coop(r0) = −0.534 kcal/mol**
  against the +0.944 target — wrong sign, 1.478 off — from legs binary **48.0046** / ternary **47.4701** /
  solvent **47.8060**, i.e. the answer is **1.1 % of the numbers being subtracted** (the reduction's own
  `cancellation_ratio` = 0.0111). Protocol hashes are
  **consistent** across the three legs, so the cycle is *not* contaminated by a protocol mismatch; the record's
  `converged: false` is only `n_replicas >= 3` failing at n=1, **not** an MD-convergence finding. Four
  consequences, each verified against the frozen gate rather than asserted:
  - **r1+r2 cannot PASS.** Exhaustive scan of every (r1,r2) over [−4,+8]² through `calibration_gate`: 0 PASS,
    17,276 BORDERLINE, 11,885 FAIL. Condition 3's boundary rule needs a first-round PASS to carry cycle
    SD ≤ 0.25, while one replicate pinned at −0.534 forces SD ≥ 0.69. Buying r1+r2 buys a
    *BORDERLINE-extend-to-5* or a FAIL — neither authorizes NR-V04.
  - **The n=3 round was never decisive.** A *perfectly accurate* method passes first-round only 9 % of the time
    at the repo's own assumed replicate SD of 0.7 (50 % at SD 0.3, 20 % at 0.5, 4 % at 1.0).
  - **The gate admits the null.** `|mean − 0.944| ≤ 1.0` accepts mean = 0.0, so at n ≥ 5 a method predicting **no
    cooperativity change** PASSES (verified: five replicates at +0.05 → PASS). Monte Carlo: PASS 22 % for μ=0 vs
    23 % for a method that is exactly right. **A gate you can pass by predicting nothing cannot validate
    anything.** ⚠ Recorded, deliberately **NOT applied** — amending a preregistered rule after a failing result
    needs an explicit, dated, reviewer-approved defect-fix, not a quiet retune.
  - **Two of three systematic-error detectors were never run; one *could not* run.** No reverse legs exist
    (`antisymmetry_fwd_plus_rev_kcal: null` on all three), there is no redundant edge so no cycle closure, and
    the reviewer's required change #1 (convergence analysis of the committed `.nc`) was **built but never wired
    to any dispatch path** — while `_diagnostics_ok()` returns True when the report is *absent*, so the gate's
    "all diagnostics pass" requirement was satisfied by never measuring it.

  **★ CONVERGENCE READ OUT (2026-07-25, run 30157501491) — r0 IS A MEASUREMENT, NOT A BROKEN RUN, WHICH SETTLES
  THE REPLICATE QUESTION.** Leg `calib_hi_to_lo__ternary_vhl`, seed 0: **2000/2000** production iterations ·
  MBAR ΔG **47.511 ± 0.045** ·
  overlap connected, min-adjacent **0.109** (floor 0.03) · equilibration fraction **0.381** · N_eff **676** ·
  12/12 replicas visiting both ends · **ΔG(t) full-vs-final-half 0.0023**, q3-vs-q4 **0.1255** · **fwd/rev gap
  0.0255** at f=0.875. Replica mixing **0.8915** against a 0.90 ceiling — passes, but **record as marginal**.
  Structurally stable: the alarming 78.9 Å → 14.97 Å solute RMSD is **periodic wrapping** (p50 2.50 Å, p90
  5.91 Å, ~2 % of atoms at ~1 box edge of 126.3 Å; √(0.02·100²+0.98·3²) ≈ 14.4 reproduces it), so the *ternary
  assembly did not rearrange* and the systematic does **not** implicate the SMARCA4→SMARCA2 starting model.
  **Consequence: the statistical error (0.045) is ~33× smaller than the miss (1.478), so the wrong sign is
  SYSTEMATIC — and replicates shrink variance, not bias.** Made worse for the replicate case, not better:
  ternary seed *s* uses the *s%n*-th relaxed SMARCA2 model, so r1/r2 are partly *different structures* and their
  spread would conflate sampling noise with homology-model sensitivity. Still unmeasured: the **ligand-only**
  pose RMSD (needs ligand indices from the OpenFE hybrid topology) — `diagnostics_complete: false` says so.
  ⚠ **Seven defects were found in this gating diagnostic on 2026-07-25, every one reporting success while
  measuring nothing** (never wired · missing `openfe` · an unguarded lazy `mbar` that deleted six other metrics ·
  slice-MBAR never converging · a fwd/rev gap taken where it is identically zero · the checkpoint never opened
  because openmmtools wants `checkpoint.nc` and the driver writes `checkpoint.chk` · a ligand-pose threshold
  applied first to bulk solvent then to a four-chain assembly). Two produced *wrong verdicts*: a silent
  `diagnostics_ok=True`, then a fabricated hard FAIL. **This is an argument for spending the next dollar on
  INDEPENDENT checks — reverse legs, cycle closure — not more replicates through the same machinery.**

  **★ THE REVERSE LEG WAS UNREACHABLE — FOUR CALLERS PINNED IT SHUT (2026-07-25, all fixed).** The preregistered
  forward/reverse antisymmetry check (`hysteresis <= 1.0`, still `null` on all three legs) could not be run at
  all, and each blocker was the same shape — *capability present in the engine, unreachable from outside*:
  (a) `MODE=converge` existed in `nr4a3_ternary_fep.main()` but no workflow could dispatch it; (b) the run
  invocation hardcoded `DIRECTION=fwd`; (c) there was no `direction` dispatch input (adding one hit GitHub's
  25-input cap → retired the confirmed-no-op `constrain_ligand_ch`, pinning `CONSTRAIN_LIG='0'` so every existing
  `clig0` commit prefix stays resumable); (d) `ternary-setup-prime-cpu.yml` pinned `DIRECTION: fwd`, and since
  the setup-cache key is `tag=<leg>_<dir>_r<seed>` a rev leg needed its own prime and could never get one while
  the GPU lane fails fast on `RBFE_REQUIRE_PRIMED_SETUP=1`. A `direction`-keyed commit prefix (`_dirrev`, applied
  only when direction≠fwd) now makes it impossible for a rev leg to silently resume the fwd trajectory.
  **Root cause of the rev-only failure (fixed):** `_build_components` passed `base_smiles=sa` to `_endpoint_pose`,
  where that argument means *"the identity of the molecule in the staged crystal SDF."* `sa` is the crystal ligand
  only in the FORWARD direction (calib_hi = cmpd1 = 8G1Q CCD `YHB`); cmpd4 is derived and in no crystal. With A/B
  swapped, the rev leg claimed the crystal held **cmpd4**, `_repair_pose` assigned bond orders against a template
  differing by N→CH, the thiazole lost its aromatic C–H, and NAGL rejected the molecule
  (`RadicalsNotSupportedError`). `CRYSTAL_SMILES` is now captured from the *unswapped* endpoint A; forward
  behaviour is byte-identical; 4 pure-stdlib regression checks added (`tests/test_ternary_crystal_identity.py`),
  one asserting that in rev the crystal must NOT equal endpoint A so the test discriminates the fix from the bug.
  **The forward r0 result is unaffected** — in fwd the argument was correct, `_endpoint_pose` fails closed on a
  SMILES mismatch, and the $0 5-part pre-spend gate's `endpoints_match` check passed.
  **Infrastructure finding worth keeping (fixed):** the setup-cache upload failure was **not** the "transient
  GcsApiError" the code called it — `gcloud storage cp` renders a permission denial as `GcsApiError('')` with an
  empty message, and only the python client showed the truth: **403, `gpu-runner@` lacked
  `storage.objects.create` on the `setupcache/` prefix** while succeeding on `stagecache/` in the same job. Two
  fresh builds died there (fwd 11.5 min, rev 11.7 min, same file) so it was systematic, and retries could never
  help; a 403 now aborts immediately with the real reason. **trimcrae granted the permission 2026-07-25 and a
  per-prefix write probe (`gcp-quota-check.yml`) confirms all four prefixes writable.**

  **Recommended next steps (spend order):** (1) ✅ *done, free* — the convergence analysis above; (2) *free* —
  route the admits-zero gate defect for approval; (3) *one replicate's cost, strictly more informative than a
  replicate* — run the **reverse** ternary+binary legs and test |ΔG_fwd + ΔG_rev| **← in flight**; (4) **the real
  decision** — rescope the calibrator to a **≳2 kcal/mol** signal, the same margin this file says a useful
  degradation window needs, via a multi-edge congeneric path (which also finally supplies cycle closure) or the
  high-contrast P1→P4/P5 pair (+2.53 / +2.99) reached through intermediate hops. Calibrating at 0.944 demands
  resolution the program does not need — this file's own mechanism-first revision already demoted the
  marginal/induced-interface axis to "a confirmation tool operating near its limit." The honest deliverable is a
  **measured resolution floor** for the ΔΔG_coop cycle, not a 23 %-odds PASS on a benchmark a null method passes
  22 % of the time.

- **`[ ]` Rung 2b — 4 fs adoption + matched re-calibration** — **~$4.4 ($1.6–11) · Cum. ~$17 · PROPOSED, needs a
  go.** **Exact invocation** (three flags, all load-bearing): `mode=preequil` once (cached), then
  `mode=run use_preequil=1 timestep_fs=4.0 warmup_timestep_fs=1.0 reset_commits=1`. `use_preequil=1` because 4 fs
  only held *with* pre-equilibration; `reset_commits=1` because OpenFE refuses to resume a checkpoint whose
  protocol timestep differs ("Sampler in checkpoint does not match Protocol settings"), so a dt change **starts
  clean** — a fresh edge, not a continuation, which is what the ~$4.4 already prices. One edge, three jobs:
  (a) exercises 4 fs over a **full** 2000-iteration production leg (the existing evidence is 40 iterations);
  (b) supplies the **matched-timestep** calibration the runbook requires before any 4 fs production result may be
  quoted; (c) is an independent reproducibility replicate of the 2 fs ΔΔG_coop. **GO/NO-GO:** no NaN across the
  full leg AND ΔΔG_coop consistent with the 2 fs run within replicate SD → adopt 4 fs for every downstream
  ternary leg (≈2× cheaper, and the ladder has ≥6 of them). NaN or a shifted ΔΔG → stay at 2 fs.
  **Two-stage, per the 2026-07-24 decision:** stage 1 is a **~$1–2 survival probe** (`prod_iters≈200`) asking
  only "does 4 fs survive well past the 40 iterations the runbook demonstrated?"; stage 2 is the full matched
  edge, only on a passing probe. Sequenced **after** valB_mini's 2 fs result, both because the calibration needs
  something to compare against and because dispatching into that lane now risks cancelling another session's run.

### RUNG 3 — expand the benchmarks *(only if Rung 2 probes look promising)*

- **`[–]` Validation A-full (10–20 edges) — SKIPPED · saves ~$50–140.** valA_mini reproduced the known ΔΔG cleanly
  on the standard am1bcc method, so a full re-derivation is redundant with OpenFE's published benchmark. Framing
  that must hold: cite OpenFE for accuracy; present valA_mini as a single-edge build-consistency confirmation, not
  a standalone benchmark.
- **`[ ]` Validation B-full — component-calibration cube** — **~$22.5 ($6–67) · Cum. ~$40.** ★ **Module 3
  (paralogue discrimination) runs on SMARCA2-vs-SMARCA4, not NR-V04** — **ADOPTED 2026-07-24 (trimcrae go)**: a
  close paralogue pair with degrader-level selectivity, solved structures, a **non-covalent** mechanism, and —
  decisively — **already staged in this repo** (8G1Q, `smarca2_model.py`, the frozen Wurz calibration), so it is
  a marginal add-on to the lane valB_mini already runs rather than a new campaign. NR-V04's selectivity is, by
  the repo's own UniProt result, most plausibly **covalent target-engagement**, which makes it a weak calibrator
  for a noncovalent ternary pipeline — exactly why the reviewer demoted it to a biological holdout. It stays the
  holdout. Apply cost lever 2: the paralogue module needs **N ternary legs + 1 shared binary + 1 shared
  solvent**, not N edges. Four separately-calibrated modules, each with its own pass/fail (a failed module →
  qualitative-only; no blanket "validated"): (1) a second all-binding graded cooperativity edge; (2) ternary pose
  recovery (co-fold, ~$0); (3) paralogue discrimination on a public system (the direct analogue of the NR4A ask);
  (4) productive-vs-unproductive ubiquitination geometry (full-CRL MD). Plus the cis-epimer negative-endpoint
  stress module. **GATE:** the prospective ladder never runs unless the **cooperativity + paralogue-discrimination**
  modules pass.
- **`[!]` NR-V04 covalent feasibility panel — ⚠ RESULT UNDER CORRECTION; ITS **GO** DOES NOT STAND** —
  **~$8 (MEASURED as-run, 18 legs) · Cum. ~$48.** Covalent celastrol–NR4A1 (C551) adduct + C551A + noncov/cov
  sensitivity + warhead/recruiter controls; 18 legs (6 systems × 3 seeds), 6 ns each, ~466k atoms; 17/18
  completed, no blow-ups.
  **⚠ THE READOUTS DESCRIBE THE WRONG INTERFACE.** `nrv04_covalent_md._topology_indices` split E3 from target
  POSITIONALLY ("target = last sorted protein chain"), while the co-fold YAML builder writes the target FIRST
  (`proteins = [("A", lbd)] + e3`). The chains are A=254 (NR4A LBD), E=213 (VHL), F=118 (EloB), G=112 (EloC), so
  the rule selected **Elongin C** as the degradation target: R1/R2 measured the **EloC↔rest** interface and R3
  counted **Elongin C's** lysines, not NR4A1's. Proof from the panel's own committed legs — the reactive Cys,
  resolved independently by geometry and sitting on the NR4A1 LBD, is recorded on chain **A** in 12 of 14 legs
  while the positional rule pointed at **G** (CI run 30122828434). The arithmetic reproduces the reported numbers
  exactly; the *interface* is wrong. The superseded science numbers are listed in
  [§Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) and **must not be cited**; the
  infrastructure/pricing record (~$0.43/leg, ~$8/panel) is unaffected.
  **★ STATUS (2026-07-25, LANE 3) — THE WITHDRAWN GO CANNOT BE RECOVERED AT $0, AND IT WAS NEVER AVAILABLE TO
  RECOVER. THE RE-RUN IS `[HELD]`, NOT MERELY UNLAUNCHED.** Four findings, each measured, not argued:
  1. **No trajectory was ever persisted**, so recomputation against the correct chain pair is impossible. A
     read-only S3 census (`nrv04_result_forensics.py`, CI run 30167457977 → `nrv04-result-forensics.json`) finds
     **72 objects / 19 units and `trajectory_objects_found: 0`** — 796 MB of `built_cif` (solvated topology +
     **pre-minimisation** coordinates = one frame), 1.35 GB of `built_system` (forces/parameters, no coordinates
     over time), and 27 kB of `leg_result` scalars **already reduced against the wrong split**. The driver
     reduces each frame in-loop and discards positions, and `_rm_ckpt` deletes the single checkpoint frame on
     clean completion (17/18 legs). The MD must be re-run or nothing.
  2. **The prereg's own frozen `panel_verdict()` returns `go: false` on the panel's own committed legs** —
     *"warhead_only recruited despite no E3 moiety"* and *"inactive epimer engaged VHL"*, i.e. **both negative
     controls came back positive**. All 17 legs returned `frac_frames_in_contact = 1.0`, and R2's frozen rule
     (any contact in >50 % of frames) **cannot be failed by a system started from a co-folded complex** — the one
     leg ever run with the *corrected* split returns `recruited=true` too. The recorded GO ("active 3/3 vs epimer
     1/3") is an **R1 narrative that §5 does not score.** So the chain split changed which interface the numbers
     described; it did **not** manufacture a GO that the frozen rule would otherwise have given.
  3. **The panel's INPUTS were contaminated as well — a third, independent data-invalidating defect.** A census
     of all 12 persisted systems gives `A=254 E=213 F=255 G=112`; a CA-geometry Kabsch match identifies the
     source as `nrv04-descriptive-v3/nr4a1/seed_1` at **RMSD 0.000 Å**, with the clean `nrv04-covalent-cofold`
     **5.884 Å** away. So the panel **simulated 14-3-3 epsilon where Elongin B belongs.** Mechanism:
     `fusion-cpu-extras.yml@786759a9` set `cofold_prefix` default `"nrv04-descriptive-v3"`, so the launcher's
     clean fallback never fired. **⚠ The 2026-07-24 forensics' "the panel is clean on this defect" is RETRACTED**
     — it audited the prefix the *code names*, not the artifact that *ran*.
  4. **A free pre-spend staging check shows the re-run cannot reach the frozen GO on any co-fold in the bucket.**
     All 6 legs stage cleanly with `target=A e3=[E,F,G]` (so the chain fix itself is proven end-to-end for $0),
     but `warhead_only`'s nearest **target-chain** Cys Sγ is **16.39 Å** and `cov_nr4a1`'s is **8.99 Å** — Boltz
     does not seat celastrol against an NR4A1 cysteine in *either* co-fold, so criterion 3 is **unevaluable** on
     every available input. Staged epimer interface 369 contacts vs active 381 (**3 %**) is noise.

  **Consequence: do not pay for the re-run as built.** It is `[HELD]` pending (a) a prereg amendment giving R2 a
  threshold that *can* fail and restating `recruiter_epimer` as a matched-ternary **ligand-level** control (it
  runs as a full ternary, not the binary §3 specifies), and (b) a re-folded `neg_celastrol`, or dropping
  `warhead_only`. Amending a preregistered rule requires an explicit, dated, reviewer-approved defect-fix — not a
  session's retune. Full evidence:
  [nrv04-covalent-panel-recovery-2026-07-25.md](research/modalities/nrv04-covalent-panel-recovery-2026-07-25.md)
  · prior chain forensics
  [nrv04-cofold-chain-forensics-2026-07-24.md](research/modalities/nrv04-cofold-chain-forensics-2026-07-24.md).

  **★ TWO BUGS FOUND HERE PROPAGATE TO THE UNLAUNCHED NR-V04 RETROSPECTIVE (RUNG 4), WHICH SHARES THIS DRIVER —
  both are fixed with regression tests, and the retrospective must not launch on the old code.**
  (i) **`_reactive_cys_by_geometry` was chain-blind** — a second live instance of the *same* defect class as the
  chain split; it is now restricted to the identified target chain, raises above an 8 Å preformed-adduct limit on
  covalent legs, and records its search diagnostics. (ii) **R3 reported NANOMETRES under an Ångström label.**
  OpenMM positions are nm; R1 converted (`* 10.0`), R3 did not, so **every committed R3 is ~10× too small** —
  reading as ubiquitination-competent (~2–4 Å) when the true separation is **~30–49 Å**. Independently
  cross-checked: `warhead_only` reported `min_A` 2.34/2.44 against a t=0 distance of **25.21 Å**.

  **★ HIGHEST-LEVERAGE INFRASTRUCTURE CHANGE FOR THE WHOLE TERNARY PROGRAM (adopted as a requirement, 2026-07-25):
  every MD driver must persist a strided heavy-atom TRAJECTORY.** Tens of MB against the ~112 MB System XML the
  driver *already* uploads — and every analysis defect above (wrong chain split, chain-blind cysteine search, the
  R3 unit error) would then have been correctable for **$0** instead of costing a re-run. This is the concrete,
  general lesson from a panel that produced three data-invalidating defects and left nothing to re-derive from.

### RUNG 4 — warhead map, differential atlas, retrospective gate

- **`[ ]` Step 1 fan-out — cmpd19 congeneric map, 8-wide** — **~$36 ($15–80; ≈19 RBFE edges × ~13.7 ref GPU-h) ·
  Cum. ~$84.** **Lane BUILT and proven to sample** (wave 1 reached 95–99 % GPU utilisation on the real system)
  but **HALTED at ~$2 with 0/19 ΔΔG**; everything is checkpointed, so a resume continues rather than restarts.
  Full record: [step1-fanout-lane.md](research/modalities/step1-fanout-lane.md).
  **Scope, if resumed:** the price covers **tranche 1 only** — the 19 edges at their charge-**conserving**
  microstate leg on the **primary frame**. The 8 charge-changing legs are *blocked* (no charge correction
  implemented) and the 6-frame conformer/paralogue axis is a **separate ~6× spend** — so tranche 1 yields a
  single-conformer **conditional** map, **not** the selectivity readout and **not** the sensitivity ranges.
  **Gate:** Val A satisfied (cite OpenFE) AND the Step 1 pilot behaved.
  **Timestep is NOT a lever** — measured free on CPU: the protocol runs at OpenFE's default `constraints=hbonds`
  + HMR 3.0, every X–H is constrained, so all edges are already 4 fs and no 2× saving exists.
  **HELD by decision, and the hold does not rest on price** — see §Open decisions.
- **`[x]` TIER-0 · NR4A paralogue-UNIQUE reactive-residue map — DONE 2026-07-24 · $0 · GATE PASS/GO.** Full-length
  UniProt (P22736/P43354/Q92570/Q01844) + dual-aligner agreement + matched-model geometry
  (`nr4a_paralogue_unique_residues.py`, 15 unit tests, run on CI because the sandbox proxy blocks UniProt).
  **4 NR4A3-unique cysteines** (2 exposed): **C397** — NR4A1 N363 / NR4A2 S363, RSA 0.395, **10.9 Å** from the
  cryptic pocket (exit-vector reach) — plus C420 (18.3 Å, RSA 0.311), C559 (12.8 Å but RSA 0.095, buried in this
  conformer), C166 (outside the LBD). **4 NR4A3-unique lysines** (3 exposed in the LBD): **K572** (RSA 0.879,
  11.5 Å), **K518** (0.413, 13.4 Å), **K592** (0.506, 16.2 Å), K178 (outside). Reciprocal check reproduces the
  NR-V04 Leg-0 exactly (NR4A1 C551 → NR4A3 T579) and completes it: NR4A1 has 5 cysteines NR4A3 lacks. K85/K194
  excluded on aligner disagreement. EWSR1 fusion moiety contributes only 1–2 lysines → **fusion-lysine axis is
  thin, not a design axis**. This is the FIRST gate in the ladder — it costs nothing and it decides what 5a
  optimises. *(Open, cheap: the matched NR4A1/2 MD-ensemble add-on should report the **distribution** of C397
  exposure, not one frame's 0.395 — and could reopen C559.)*
- **`[x]` NR4A differential surface atlas — DONE · $0 · GATE PASS/GO.** Matched Shrake–Rupley SASA + BLOSUM62
  alignment over NR4A{3,1,2} opened models → **46 differential-surface handles** (exposed × divergent ×
  character-changing), 15/15 LBD lysines exposed; per-residue identities reproduce the canonical map 148/148. A
  differential surface exists to steer an E3 against (distinct from the ~70 % pocket hotspot), so the 5a
  orientation-basin search is warranted. *(Optional add-on: matched NR4A1/2 MD ensembles ~$10–40 to test which
  handles survive dynamics.)*
- **`[ ]` NR-V04 retrospective — preregistered holdout** — **~$21 ($4.8–67) · Cum. ~$104.** Full ensembles
  through the pipeline, no tuning, epimer control; report directional concordance only. **Gate:** Val B-full +
  NR-V04 feasibility + Step 1 fan-out. **It no longer gates the causal kill-switch** (lever 4).
  **GO/NO-GO:** at least directionally concordant with the NR4A1-degraded / NR4A2·3-spared outcome → GO to the
  prospective ladder; discordant → the ladder is not justified, publish the honest negative. **Interpret with the
  covalent confound explicit:** NR4A1 Cys551 is unique to NR4A1 (NR4A3 T579), so a concordant result may be
  recovering *target engagement*, not ternary cooperativity — which is why this is a biological holdout and
  SMARCA2/4 is the method calibrator.
  **State: fully built + preregistered + unlaunched.** Because the covalent confound is *measured*, the panel
  **decomposes** — **R1** (primary, all-non-covalent NR4A1/2/3) tests whether the workflow discriminates
  paralogues with the warhead held off; **R2** isolates warhead chemistry; **R3** (epimer) is conditional. **A
  null R1 is a registered, publishable outcome**, not a method failure. Three infrastructure defects (kernel OOM,
  error-swallowing monitoring, the 25-input dispatch cap) are fixed in code and **unproven on hardware**, so the
  next launch is a **pilot, not a fan-out**.
  **Resume here: [nrv04-retrospective-handoff-2026-07-24.md](research/modalities/nrv04-retrospective-handoff-2026-07-24.md)**
  (exact commands, cost ledger, traps) · prereg
  [nr4a3-nrv04-retrospective-prereg.md](research/modalities/nr4a3-nrv04-retrospective-prereg.md) · its co-folding
  moved off SageMaker onto the Vast lane
  ([provider-deviation-2026-07-24.md](research/compute/provider-deviation-2026-07-24.md)).

### RUNG 5 — mechanism-first prospective ladder *(the flagship, gated mid-ladder by the causal kill-switch)*

- **`[ ]` 5a · Orientation-basin search, mechanism-first** — **~$0–50 (CPU $0 + optional MM-GBSA rescore) ·
  Cum. ~$129.** Broad transform sampling across the **widened ligandable E3 set** (VHL, CRBN, cIAP1/BIRC2, DCAF1,
  DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2 — free at CPU, **downselect to ≤2 before any GPU leg and log the
  dropped set**). **★ Availability answered $0 and it does NOT constrain the choice** (CI run 30125742542): all 8
  widened arms are broadly expressed and record-complete on HPA (`nr4a3_e3_expression.py`, extendable to any
  further candidate), every symbol resolved through HPA's own search with an exact-match guard — same verdict as
  the original VHL/CRBN check. So the downselect must be made on
  **ligandability + interface geometry**, never on availability, and **no recruiter may be dropped with "not
  expressed" as the reason.** Matched 3-paralogue scoring **over the warhead-pose ensemble**; cluster into ~3–8
  basins/ligase; score with the two **categorical** terms (a) and (b) above, then the cheap counterfactual screen
  to nominate marginal wedges.
- **`[ ]` 5a-KS · Wedge confirmation — pilot-first KILL-SWITCH + causal RESULT** — **~$12 ($1.6–45) · Cum. ~$141.**
  **PRIMARY: the ligand-side double difference.** Pilot ONE matched pair first:
  `S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)`, ternary legs only (lever 2), on the lane Val B
  calibrates. **No discrimination ⇒ STOP** — publish the honest causal negative, skip the refinement tail.
  Discrimination ⇒ extend to NR4A2 and to a second design element. **Evidence grade:** a NO-GO may be taken on
  valB_mini-grade evidence (stopping is the conservative action), but a POSITIVE result stays **exploratory**
  until valB_full passes.

  **CONFIRMATORY second line — the reciprocal PROTEIN-mutation cycle. ENGINE QUALIFIED 2026-07-25; cost
  PROJECTED, not measured on NR4A.** Pilot ONE direction (3→1); loss ⇒ complete the reciprocal cycle
  (3→2 + reciprocal 1/2→3).

  *Engine:* **pmx + GROMACS** (Gapsys & de Groot) — the published, field-standard *free* engine for
  protein-mutation FEP. perses was retired the same day it was tried: its core protein-mutation path builds the
  old→new residue atom map by round-tripping each residue template through an **OpenEye OEMol**
  (`PolymerProposalEngine.generate_oemol_from_pdb_template` → `oechem.oemolistream`), which is commercial and
  licence-gated, with no conditional and no RDKit alternative on that path. Cost of establishing that dead end:
  **~$0.05.** Everything around the engine was engine-agnostic and survived the swap: staging with a
  mutation-site refusal, the SKEMPI-verified references, scoring, the verdict, and the Vast lane. Code:
  [`Dockerfile.pmxfep`](research/compute/Dockerfile.pmxfep),
  [`protfep_pmx.py`](research/modalities/protfep_pmx.py),
  [`protfep_run.py`](research/modalities/protfep_run.py),
  [`protfep_bench.py`](research/modalities/protfep_bench.py),
  [`protfep_reduce.py`](research/modalities/protfep_reduce.py),
  [`protfep_refcheck.py`](research/modalities/protfep_refcheck.py), `gpu-protfep-vast.yml`; plan in
  [protfep-pmx-plan.md](research/modalities/protfep-pmx-plan.md). **Most of the ladder is $0** — stage-test,
  refcheck, bake and a build-test that runs the ENTIRE hybrid construction on a CPU runner; a host is rented only
  once a hybrid demonstrably builds.

  *Known-answer benchmark — PASSED* (full set on Vast, equilibrium λ windows + BAR, scored by `protfep_reduce`
  against SKEMPI 2.0-verified references; artifact
  [`protfep-benchmark-result.json`](research/modalities/protfep-benchmark-result.json)):

  | benchmark | computed ΔΔG_bind | reference | abs err | within ±1.5 |
  |---|---|---|---|---|
  | barnase–barstar **Y29A** (hot spot) | **+4.424 ± 1.077** (3 complex × 3 apo) | +3.40 | 1.024 | ✔ |
  | barnase–barstar **Y29F** (near-null control) | **−0.370 ± 0.175** (3 complex × 3 apo) | −0.13 | 0.240 | ✔ |

  **Ordering correct** (Y29A ≫ Y29F), which is the test that matters — a wedge is read as a ranking, so a
  magnitude pass with the ordering wrong is a fail. The near-null control did its job: the engine returned
  ≈−0.37 where the experiment sees ≈0, rather than inventing an effect. Both mutations are charge-conserving, so
  engine error is not confounded with the net-charge artifact. `plan_wedge` may now stamp `validated: true`.

  **★ THE MOST DECISION-RELEVANT RESULT IS THE NOISE STRUCTURE, NOT THE AGREEMENT.** At full replication the
  between-setup scatter differs by **6.2×** between the two benchmarks (±1.077 on the +4.4 hot-spot knockout vs
  ±0.175 on the near-null), while *within*-leg MBAR standard errors are 0.05–0.13 kcal/mol in both — an order of
  magnitude smaller. So this is **setup/equilibration variance, NOT insufficient sampling**: running each leg
  longer would not fix it; running more legs would. Two consequences:
  1. **A single leg does not determine a number.** Y29A's mean walked 2.851 → 3.951 → 4.025 → 4.424 as
     replicates landed, and its error against the reference *grew* (0.549 → 1.024). Replicates are mandatory.
  2. **The wedge's own regime is the well-determined one.** The wedge measures a *small* induced-interface
     difference (~1.12 kcal/mol best-case resolvable) — exactly where this engine reproduces to ±0.18, not the
     ±1.08 the hot spot suggests. Encouraging for the wedge, and it means **the right validation for 5a-KS is a
     benchmark sized like the wedge**, not a hot-spot knockout. **That benchmark does not exist yet**, and until
     it does the confirmatory line may not claim to resolve a paralogue-scale difference.

  *Price:* **measured 1.058 ± 0.432 GPU-h/leg** over 11 legs (range 0.379–1.8) at a 25,187-particle mean,
  **$0.212/leg** at the $0.20/hr assumed in the reducer → a **PROJECTED** wedge of **~$4.6 (3 replicates)** /
  ~$3.1 (2 replicates). The projection is a **linear particle-count scaling** from 25,187 to the NR4A sizes — an
  assumption, not a measurement, so it may not be quoted as a rate and the confirmatory line stays **excluded
  from the pinned ladder total**. The per-leg GPU-h SD (0.432 on a mean of 1.058) is **host variance, not
  physics** — two hosts rented minutes apart differed ~10× in throughput per particle.

  *Two blockers, both cleared in code before any leg runs*
  (planning layer: [`nr4a3_protein_fep.py`](research/modalities/nr4a3_protein_fep.py), whose wedge subtraction
  delegates to `ternary_coop.ddg_coop` so there is **one** definition of the cycle in the repo, not two):
  - **Cross-lane charge mismatch.** `assert_charge_consistency` hard-fails any wedge whose ternary and binary
    legs charge the ligand differently. An un-pinned wedge is not a thermodynamic cycle, so this is a refusal,
    not a warning. Pin NAGL across both legs (the only method that can charge both a small mutation edge and a
    PROTAC-scale assembly) and stamp it into both result JSONs. Cost: $0.
  - **Net-charge-changing mutations, and it bites immediately.** **R412 is one of our own seven selectivity
    handles, and R→A is charge-changing** — exactly what PME cannot do naively (the neutralising background
    plasma shifts the electrostatic free energy by a system-size-dependent amount that does not cancel between
    the differently-sized ternary and binary boxes). `plan_wedge` refuses a charge-changing mutation unless an
    explicit correction strategy is chosen. **Prefer a charge-conserving handle (L406/T410/I484/I531/L534) for
    the FIRST causal test.**

  *Declared physics deviation:* 2 fs with a 1 fs warmup, not the canonical 4 fs+HMR. Softcore regions are where
  the ternary lane NaN'd, the timestep is empirical with no static predictor, and on a new engine's first leg a
  NaN costs the whole rental while 2 fs costs ~2× the iterations of a sub-dollar leg. Escalate only after this
  lane survives a full NR4A-scale leg — and record it; do not assume it transfers.

  *Sequence, cheapest-decisive-first:* smoke (~$0.10) → pilot (both legs of one direction, ~$1–3 — **the abort
  gate**) → full set (~$5–10) only if the pilot sees it.

- **`[ ]` 5b · Inverse linker design** — **~$0–20 (mostly $0 CPU) · Cum. ~$151.** For each confirmed basin, derive
  linker requirements (endpoint distance, exit-vector dihedral, strain, reach), enumerate a virtual library,
  filter by basin fidelity, annotate exact structures + synthetic feasibility → **~12–20 virtual constructs** (the
  reviewer's "24–36" now bounds this virtual set, not a hand-built grid). For basins carrying the covalent handle,
  the library enumerates the **electrophile position on the linker** as a design variable, and **prefers
  reversible-covalent** chemistry.
- **`[ ]` 5c · Explicit ternary-ensemble refinement** — **~$21 ($1.9–85; endpoint MD, 24–~200 legs at ~1.38 ref
  GPU-h each) · Cum. ~$172.** *(The biggest swing item — the leg COUNT, not the rate, dominates its uncertainty.)*
  Replicated ternary + full CRL/E2~Ub MD across target states, linker conformers, and in-basin poses; matched
  NR4A1/2/3; separate accessibility from stability; robust constraint-satisfaction filtering → **~4–8 constructs**
  nondominated under scenario + model uncertainty. Add a constraint: **which lysine the ubiquitin actually
  reaches**, reported per construct as a distribution over unique-vs-conserved sites, not just "a lysine is near".
- **`[ ]` 5d · Local ternary FEP** — **~$22 ($3.2–80; 3–6 ternary comparisons) · Cum. ~$194.** Alchemy **only**
  within a retained basin (both endpoints plausibly bound, modest congeneric change). Refines the matched final
  series → **~6–12** with ≥2 mechanistic wedges, ≥2 linker architectures, VHL/CRBN only where both survive,
  explicit negative controls. **Deliverable** = the prioritized, structure-defined, retrosynthetically annotated
  candidate set with an identified causal selectivity mechanism — degradation experimentally unvalidated.

### OPTIONAL / HELD — only if a specific claim needs them AND a budget nod is given

- **`[ ]` ΔG_open per paralogue** — **~$120–300.** Only to make affinity/selectivity *unconditional*; otherwise
  report conditional on the open state ($0, fully defensible).
- **`[ ]` Conditional ABFE (pose-plausibility)** — **~$80–200.** Raw values, T4L discrepancy separate, no offset,
  does not prove binding. **This hold covers the existing ABFE block's λ-overlap repair too** — it is parked, not
  in flight. Launch only with an explicit nod after everything above.

### RUNG 6 — write & ship (~$0)

- **`[ ]` Fold results into paper** — language discipline; QM/torsion validation at linker junctions;
  physicochemical + retrosynthetic assessment; re-render figures.
- **`[ ]` Final red-team + review-response.**
- **`[ ]` Post + submit** — OUTWARD-FACING, needs trimcrae sign-off.

---

## Spend summary

**PINNED TOTAL: ~$194 mid-range (~$47–561)**, GO at every gate, priceable stages only.

**How it is built** — regenerate the alchemical/MD stages with `python research/modalities/vast_cost_model.py`
(JSON: [`vast-ladder-repricing.json`](research/modalities/vast-ladder-repricing.json)); the tool prices 9 stages
at **$149.4 ($38.2–466.4)** on the measured **$0.137/ref-GPU-h** policy. The ladder figure adds the stages the
tool does not cover: step0 ~$1–2 (mid $1.5), valA_mini ~$0–15 (**realized ~$0** on GCP credit), the ~$8 measured
covalent panel, 5a basin ~$0–50 (mid $25), 5b linker ~$0–20 (mid $10). `149.4 + 1.5 + 0 + 8 + 25 + 10 ≈ 194`;
low `38.2 + 1 + 0 + 8 + 0 + 0 ≈ 47`; high `466.4 + 2 + 15 + 8 + 50 + 20 ≈ 561`. The per-step `Cum.` chain above
ends on the same ~$194, and [pricing.md §C](research/compute/pricing.md) carries the same chain — all three must
agree.

**Excluded from the total:** (a) the 5a-KS **confirmatory** protein-mutation wedge and its reciprocal cycle —
engine qualified, but the NR4A cost is a particle-count projection, not a measured rate; (b) Optional/HELD
ΔG_open + ABFE (~$200–500 more).

**⚠⚠ THE `$/hr` AXIS IS MEASURED; THE GPU-HOUR AXIS IS NOT.** The reference GPU-hours are the repo's own work
estimates; this multiplies them by a measured rate, it does not re-derive them. **A rate measured on one
molecular system is not a price for another** — the single largest correction to date (~4× on the fan-out) came
from applying a public-TYK2 per-iteration rate to the NR4A3 complex, which is ~2.6× heavier. The ternary base is
*still* a SMARCA2/VHL rate pricing NR4A ternaries. If the GPU-hours are 2.6× low, these costs are 2.6× low no
matter what we bid. Dominant uncertainties, in order: the **ensemble-MD leg count** (5c + retrospective), the
**ternary transferability risk**, then the confirmatory wedge's particle-count projection.

**What survives every reprice.** The six cost levers are **ratios** — 4 fs halving force evaluations, the exact
binary/solvent cancellation, sequential stopping — so they are independent of $/hr and of system heaviness. And
**none of this weakens the mechanism-first case**: the argument was never that GPU work is expensive in the
absolute, but that spending it on an axis needing ~2.0 kcal/mol when the method resolves 1.12 is a bad trade at
*any* price, and the $0 categorical screens dominate either way.

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
| Confirmatory protein-mutation cycle (optional) | 1–3 mutation directions | **~$4.6 PROJECTED** | *(excl.)* |
| Optional ΔG_open / ABFE (HELD) | — | +$200–500 | *(excl.)* |

Notes: the restructuring buys **causal evidence** (matched-pair cycles + ensemble MD + local FEP) over
co-fold-and-score — higher information per dollar, not lower. A non-viable paper still dies for ~$2 at Val A, or
**free** at the Tier-0 unique-residue map and the atlas (both passed). The *expected* cost is lower than the
totals suggest, because the leading gates are now $0.

## Dependency spine

```
TIER-0 unique_residue_map [x]($0) + atlas [x]($0)  ──[BOTH PASS]──►    ★ leads everything priced
          │        (C397 exit-vector reach; K572/K518/K592 exposed; EWSR1-lysine axis thin)
          │
RUNG0  step0 [x] + emc_e3 [x] + pocket [x]                              (CPU/$0, done; Cum ~$2)
          │
RUNG1  valA_mini [x] ──[GO]──►                                          (cite OpenFE; Cum ~$2)
          │
RUNG2  step1_pilot [x] ∥ valB_mini [~ 2 fs, r0 wrong sign]  ──[GO?]──►  (Cum ~$13)
          │
RUNG2b 4 fs adoption + MATCHED re-calibration (~$4.4) ──[no NaN & ΔΔG consistent?]──►   (Cum ~$17)
          │      └── YES ⇒ every downstream ternary leg ≈2× cheaper
          │      └── NO  ⇒ stay at 2 fs, carry the 2 fs base
          │
RUNG3  valB_full cube (module 3 = SMARCA2-vs-SMARCA4) + nrv04_feasibility [!] ──[GO?]──►   (Cum ~$48)
          │            ([!] = feasibility's GO is WITHDRAWN pending a corrected re-run: its readouts
          │             measured the Elongin C interface, not VHL<->NR4A1. It gates nothing until then.)
          │
RUNG4  step1_fanout ∥ atlas [x]($0) ──► nrv04_retrospective ──[concordant?]──►   (Cum ~$104)
          │      (holdout, NOT the calibrator; read WITH the Cys551 covalent confound)
          │
RUNG5  basin_search($0–50, multi-E3, pose-marginalised, CATEGORICAL terms)        (Cum ~$129)
          │        ──► ★ KILL-SWITCH = ligand-side double difference (~$12)       (Cum ~$141)
          │      └── no discrimination ⇒ STOP: publish honest causal negative
          │      └── discrimination    ⇒ extend + tail
          │      └── CONFIRMATORY 2nd line: the protein-mutation cycle — pmx + GROMACS
          │           (perses retired: OpenEye-gated). Known-answer benchmark PASSED
          │           2026-07-25; NR4A cost PROJECTED (~$4.6), so it is excluded from
          │           the total and still owes a WEDGE-SIZED benchmark before it may
          │           claim to resolve a paralogue-scale difference. It does NOT gate
          │           the ladder — the ligand-side double difference does.
          │
       inverse_linker($0) ──► ternary_ensemble_refine ──► local_ternary_fep         (Cum ~$194)
          │
RUNG6  fold ──► redteam ──► post/submit                                             ($0)

OPTIONAL/HELD (explicit nod only): dg_open_paralogue, abfe_conditional (incl. the λ-repair)
```

## Current front

Rungs 0–1 are done. The Tier-0 unique-residue map and the differential atlas are done ($0, both PASS). The
NR-V04 covalent feasibility panel is **WITHDRAWN** — not merely "under correction". Its GO was never
produced by the frozen scoring rule, its inputs were contaminated, and no trajectory survives to re-derive from,
so its re-run is **`[HELD]`** pending a prereg amendment. It gates nothing.

**One lane is live:** valB_mini's **reverse** ternary+binary legs on GCP L4 (free trial credit), launched
11:57 AM ET — see the **IN FLIGHT** board at the top of this file.

**Two lanes are built and idle, awaiting a go or a decision:**
- **The NR-V04 retrospective** — built, preregistered, never launched; next launch is a pilot, not a fan-out.
- **The step1 fan-out** — built and proven to sample, halted at ~$2 with 0/19 ΔΔG.

**One lane closed this session:** the 5a-KS confirmatory protein-mutation benchmark **qualified** (RUNG 5a-KS),
moving the ladder's only unscoped rung from UNPRICED to *projected*. Nothing with a GPU price launches without an
explicit go.

## Open decisions

1. **`[x]` ADOPTED — method calibrator swapped from NR-V04 to SMARCA2-vs-SMARCA4** (valB_full module 3). NR-V04
   stays the biological holdout; its selectivity is most plausibly covalent target engagement, and SMARCA2/4 is
   already staged in-repo.
2. **`[x]` ADOPTED — the protein-mutation wedge is demoted from primary to confirmatory.** The ligand-side double
   difference is the paper's headline causal evidence and runs on the lane Val B already has an accuracy control
   for. The mutation cycle is kept, not deleted: its benchmark has now passed, so the paper can have two
   independent causal lines.
3. **`[x]` DECIDED — adopt 4 fs, but TWO-STAGE**, sequenced after valB_mini's 2 fs result (RUNG 2b).
4. **`[x]` DECIDED — HOLD the step1 fan-out; do NOT resume the 19-edge tranche.** The decision stands on a
   *scientific* reason that is independent of price: under mechanism-first the fan-out's **selection criterion**
   has changed — the exit vector must now be able to carry a linker toward **C397** (10.9 Å) and orient the E3 so
   the transfer zone covers **K572/K518/K592**, which is not the same as ranking substituents by affinity.
   Resuming the old edge list would spend ~$36 optimising the wrong objective, and a cheaper way to optimise the
   wrong objective is still the wrong objective. Nothing is lost by re-scoping: **0/19 units produced a ΔΔG**.
   **Order: run 5a's $0 basin search first** (it tells us which exit vectors matter), **then** a re-scoped,
   smaller fan-out — with a cycle-closure edge moved early, since all three cycles currently close only in the
   last wave. *(Note the price has since fallen to ~$36, so un-halting no longer crosses the >$50 review gate.
   That makes it a cheaper call, not a different one; it is trimcrae's.)*
5. **`[ ]` OPEN — the valB_mini rescope.** Held until the reverse leg reads out. See RUNG 2, "Recommended next
   steps".
6. **`[ ]` OPEN — route the admits-zero gate defect for approval.** The frozen gate accepts a method that
   predicts no cooperativity change (22 % vs 23 %). Amending a preregistered rule after a failing result needs an
   explicit, dated, reviewer-approved defect-fix. $0.

---

## Appendix A — superseded numbers and retracted claims

*Kept so a correction is never silently dropped, and out of the live plan so it stops competing with it. Each
line: what was believed, and what retired it. Do not cite anything in this table.*

| # | superseded claim | what retired it |
|---|---|---|
| 1 | Ladder total **~$390 (~$170–610)**, then **~$240 (~$90–390)**, then **~$467 (~$249–685)**, then a stray **~$128 (~$36–381)** | Successively: the six cost levers; the measured per-edge work correction; the measured bid/selection policy. The **$128** was `bid-strategy.md` §6's table with the **5c row missing** — fixed there; the pinned total is **~$194 (~$47–561)** |
| 2 | "The 4090 wins $/ns at every size (1549 / 669 / 175.6 vs 3090 72.5 @444k; 2.42× for ~9 % more $/hr)" — a **card** rule | The 23:08 2026-07-24 bench was **withdrawn** (single 0.9–4.5 s windows; it also ranked a 4080 SUPER above a 4090). Validated grid: 4090 755.36 / 4080 703.51 / 3090 359.36 ns/day → **2.10×**, and the cheapest 3090 floor is **8.8×** below the cheapest 4090. **Rank offers on all-in `$/ns`; the card is not the decision** |
| 3 | Bid = `min_bid × 1.1` / `× 1.5` / `× 1.9` / `× 1.25`; and a `P* = clamp(max(no-churn floor, √(m̂·d) or UCB_q), ≤ on-demand)` reservation-price/adaptive-UCB scheme | All four multipliers were live at once. The measured bid ladder showed `charged = min(bid, on-demand)`, so a premium is paid on **every** hour and cannot buy safety from on-demand renters; the ~20-min reload that justified `×1.9` was **self-inflicted** (our reaper DELETEd paused instances). The UCB scheme never reached the launch path. Current rule: **floor + staleness tick, capped at on-demand** ([bid-strategy.md](research/compute/bid-strategy.md) §7) |
| 4 | RBFE binary edge ≈ **5–6 GPU-h ≈ $0.6–1.4**; `step1_fanout` **$12–26**, then **$91–101** | The 5–6 GPU-h was a **public TYK2** rate (~5.2 s/iter) applied to the ~2.6× heavier cmpd19/NR4A3 complex (~13.6 s/iter on three hosts). Unit is **~13.7 ref GPU-h**. The $91–101 then used the **$0.35–0.39/hr** realized, which was a consequence of bidding `×1.5` on a `min_bid`-ranked offer, not the market. Current: **~$1.9/edge, ~$36 fan-out** |
| 5 | Ternary edge ≈ **$3–6**, then **$4–7**, then **$65–110**, then **$7–15** | Each of the first two treated **920 iterations as a full leg**; 920 = 23 × 40 is a **checkpoint boundary**, and that line was the **binary** arm. A leg is 400 equil + 2000 production = **2400 iterations**. The $65–110 came off a refuted 55-GPU-h AWS anchor (a leg that was ~65 % GPU-idle from 12× per-window am1bcc re-charging). Current: **~$8.8 ($3.2–22)** |
| 6 | Endpoint-MD leg **~$0.6/leg**, then **~$0.45**, then **~$0.26 on a 4090** (via the 2.42× ratio) | Completed 18-leg ledger gives ~$0.43/leg on a 3090; converted by the *validated* 2.102× ratio → **~1.38 ref GPU-h ≈ ~$0.19** |
| 7 | "**No ternary leg has ever run to completion**, so even the leg length is unverified" | valB_mini's ternary seed 0 reached **2000/2000** production iterations (convergence run 30157501491). The leg length is now observed. *Still true and still load-bearing:* **no ternary edge has completed end-to-end on a 4090**, so the Vast cost basis remains rate × leg length |
| 8 | "5a-KS is **UNPRICED and BLOCKED** — no protein-mutation FEP engine exists in this repo; scope one before RUNG 5 can be planned or priced" | True when written (OpenFE's RHTP maps **ligand** atoms only; the sole protein-mutation path, `nr4a3_resistance_ddg.py:53`, is PDBFixer + MM-GBSA, non-alchemical). The engine was then built (perses → retired as OpenEye-gated → pmx + GROMACS) and **passed its known-answer benchmark 2026-07-25**. The **primary** kill-switch never needed it — it is the ligand-side double difference at ~$12 |
| 9 | NR-V04 covalent panel science: recruiter_active **3/3** stable vs epimer **1/3**; covalent NR4A1 **2/3** = noncovalent **2/3**; C551A **1/3** | Retired **three times over** (2026-07-25): the split was **positional** and selected Elongin C, so the numbers describe the wrong interface; the **inputs were contaminated** (14-3-3 epsilon in place of Elongin B, source pinned to `nrv04-descriptive-v3/nr4a1/seed_1` at CA-Kabsch **RMSD 0.000 Å**); and the prereg's frozen `panel_verdict()` returns **`go: false`** on these very legs, both negative controls positive. The GO was an **R1 narrative §5 does not score**. The **cost** record (~$0.43/leg, ~$8/panel) is unaffected |
| 10 | 5a-KS benchmark: Y29A **4.025 ± 1.100** (2 × 3); Y29F **−0.552** (single replicate) | Superseded by the full 3 × 3 set: **+4.424 ± 1.077** and **−0.370 ± 0.175**. Y29A's error against the reference *grew* as replicates landed (0.549 → 1.024) — the scatter showing itself, not a drift to explain away |
| 11 | The warmup NaN was "an alchemical C–H whose constraint changes between endpoints", then "the whole ligand's C–H are unconstrained" | **Both** were artifacts of a `[hmr-diag]` counter that mistook alchemical *nonbonded-exception* pairs for X–H bonds. A perses force-layout dump showed **0 unconstrained valence X–H** on both anchors, and calib NaN'd at 4 fs anyway. Real cause: the **softcore region in a rough homology-built assembly**; the fix is plain-MD pre-equilibration |
| 12 | 8XTT: **4/20** conformers above D\* | The harmonized rerun (pinned fpocket + score-independent matcher) reports **19/20 detected, 3 ≥ D\*** = 3/19 among detected, **3/20** across all deposited |
| 13 | "There is no interruptible discount on Vast" | A tautology of the query type — `_live_offers` defaults to `interruptible=True`, and a bid-type search reports `dph_base` as your rate *at the floor*. Measured across 63 machines / 12 card classes: median on-demand = **1.25× the floor**, IQR 1.14–1.68, zero hosts at parity |
| 14 | `lint_claims.py` R5's premise, "no per-edge alchemical dollar figure is a completed run on the card quoted" | Falsified **for the binary lane only** — the NR4A3 rate was taken on the real system, on the quoted card, across three hosts. The rule should be re-scoped to the ternary lane when the step1 branch merges; left alone rather than raced |
| 15 | Every committed NR-V04 **R3 `min_A`** (2.34–4.48, read as ubiquitination-competent) | The value was in **NANOMETRES under an Ångström label** — OpenMM positions are nm, R1 converted (`* 10.0`), R3 did not. True separations are **~30–49 Å**. Cross-checked independently: `warhead_only` reported 2.34/2.44 against a t=0 distance of **25.21 Å**. Fixed with a regression test |

---

## Appendix B — superseded strategy framings

*Moved out of CLAUDE.md 2026-07-25, where 168 lines of plan mirror had accreted (including two blocks already
labelled superseded) in the file that loads into every session. Plan history belongs with the plan. Same rule as
Appendix A: kept so a decision is never silently dropped, out of the live text so it stops competing with it.*

| framing | status |
|---|---|
| **Atlas-anchor reframe** (2026-07-11 AM) — the repo's #1 priority is an EMC treatment anchored by the **EMC Open Target & Drug Atlas** (`research/atlas/`: proteostasis-chromatin; fusion-subtype antiangiogenic biomarker; fusion-junction + lineage antigens; direct fusion targeting) + collaborator outreach | **Superseded the same day** by the degrader-primary decision (trimcrae + gate-AI). The atlas *work* stays valuable as **support** — biological rationale, fusion-vs-WT biology, anti-target liabilities, an assay roadmap for collaborators, and the **backup route** if degrader design fails — but it must not absorb most effort via indefinite evidence aggregation. Its own state: `research/atlas/README.md` + `STATUS.md` |
| **Two-papers-first plan** (2026-06-26) — publish (1) the NR4A3-degrader result paper and (2) the fusion-junction ASO paper, with the EMC-program roadmap and the fusion-exclusivity framework in the next tier | Still the portfolio shape, but the degrader paper is now the ≈70–80% program and the ASO paper is support. Route board: [IDEAS.md](research/IDEAS.md); capstone ranking: [emc-treatment-strategy.md](research/manuscripts/emc-treatment-strategy.md); why splitting the degrader paper out serves rather than replaces the EMC goal: [nr4a3-degrader-paper-positioning.md](research/manuscripts/nr4a3-degrader-paper-positioning.md). The ASO route's one remaining gate is **delivery** |
| **Three-step spine** — (1) FEP converges on cmpd19 → (2) replicate NR-V04's selectivity in silico → (3) design + ternary-test on the cmpd19 anchor | **Superseded as the ORDERING** by the 2026-07-15 reviewer verdict (the thesis is unchanged). NR-V04 is a *holdout*, not the calibrator, and runs *after* the known-answer SMARCA2/VHL control. The ordered plan above is authoritative |
| **Track A** — qualify an NR4A3-engaging warhead via repaired ABFE (`denovo_401` as a credible design input) | **SHELVED 2026-07-15** — parked, not deleted. `denovo_401` is a **side comparator / benchmark, not a lead**. Revisit only if the ternary workflow needs an absolute-affinity anchor that a coming method makes cheap |
| **Orientation-first** prospective search | **Superseded 2026-07-24** by mechanism-first (§Program and thesis). Orientation is still the second stage; it is no longer the first |
| **PR #3 coordination note** (`claude/emc-research-strategy-kdz9kn` set atlas-primacy) | Resolved — merged and reconciled to degrader-primary |

**One inference discipline worth keeping from that history, because it is easy to overclaim:** NR-V04 is
event-level proof that family-selective NR4A degradation is *achievable*, which is what makes this program
credible and rebuts "the family is too homologous." It is **not** proof that the structural mechanism of that
selectivity is known, solved, or transferable — there is no solved ternary and no matched cross-paralogue
cooperativity measurement. Never claim the latter.
