# Adaptive compute allocation for the NR4A3 selective-degrader screen

**Status:** DESIGN + OFFLINE PROTOTYPE (2026-07-12; revised after an external methodology review — see §13).
A spend-minimizing resource allocator over the existing staged pipeline (binary RBFE → paralogue RBFE →
ternary) and the `submit_spot` fleet. Goal: **maximize P(find a computationally qualified NR4A3-selectivity
candidate) per dollar**, with granular, well-timed kills and PRE-DECLARED campaign-wide error control.
Two-module split: `adaptive_allocator.py` = **scheduling only** (Thompson / lock / futility — never declares);
`adaptive_certify.py` = the **only** PASS authority (anytime-valid bounds, noncompensatory per-paralogue
margins, terminal-rung evidence, campaign δ). 38 tests (`test_adaptive_allocator.py` +
`test_adaptive_certify.py`). **KEEP OFFLINE.** The review's disposition: sound for an *offline shadow pilot*
after fixes 1–6; **fleet wiring requires a separate code-level review + a completed multi-scenario stress
suite + a real retrospective calibration** (§13). It changes nothing currently running.

**Claim ceiling (non-negotiable):** a candidate that PASSES here is a **"computationally qualified
NR4A3-selectivity candidate"** — NOT a "selective hit" or "selective degrader." Numerical convergence
(overlap/hysteresis/cycle/pocket) is not physical correctness: force-field/charge bias, wrong
protonation/tautomer/pose, hidden slow modes, shared cross-paralogue systematic error, and the terminal
score being only a *surrogate* for cellular degradation all survive convergence. Only wet-lab data upgrades
the label.

## 0. Operating modes (read this first)

Three modes on one shared machinery; pick by how much you trust the prior and how thorough you must be.
Validated costs are from the synthetic screen (§11), illustrative not literal.

| Mode | When to use | Behavior | Sim cost / recovery |
|---|---|---|---|
| **Cheap-first champion** (default; §7c) | good-arm ID with abstention: you want *a* qualified candidate cheaply | near-free CPU prior ranks all → confirm the top candidate depth-first → **stop at the first that CERTIFIES; touch nothing else**; hard ~$350 gate → abstain/escalate | **~$232/run**, 63% one-touch wins, 22% escalate (illustrative sim; certification via §3 error control) |
| **Interruptible champion** (§7c) | same, but don't sunk-cost a slipping #1 | re-rank after every increment; Thompson leader + confirmation-lock (lock a promising one, **pause it if it slips**) + switch hysteresis ~ env cost | **~$105/run**, matches commit-first recovery, ⅓ the waste on a slipping decoy |
| **Full adaptive fleet** (fallback; §3–7) | champion escalated, OR you must find *THE* best (thorough) | successive-halving rungs + top-two Thompson + sequential futility + env-aware batching | **~$1,681/run** (12/12), ~35% under static halving |

**Default path:** champion (interruptible) under the hard gate → escalate to the full fleet only on failure.
Blended expected cost to a decision ≈ **$600**, with a **hard ~$350 ceiling before any >$50 sign-off**.
Everything below is the detail behind this table. **Honesty spine:** the cheap prior only *orders* the
search; certification is a **separate** authority (`adaptive_certify.py`, §3) using anytime-valid bounds on a
noncompensatory vector of per-paralogue margins under a pre-declared campaign-wide error budget δ. The
defensible guarantee is **not** "zero false declarations" — it is: *no candidate is declared from cheap-prior
evidence or from numerically invalid calculations, and the campaign-wide false-declaration rate from the
statistical procedure is controlled to δ under optional stopping* (validated: 0/200 no-hit campaigns, ~95%
upper bound 0.015, δ=0.05). Converged-but-biased physics can still be wrong — hence the claim ceiling above.

## 1. Framing — this is best-arm identification, not regret-minimization

The instinct is "multi-armed bandit," but the classic MAB objective (minimize cumulative regret) is the wrong
one: we don't accrue value from every candidate we test — we want to **identify the selective winner(s) and
stop paying for everything else as early as defensibly possible.** That is **fixed/soft-budget best-arm
identification (BAI)** with **multi-fidelity** evaluation. The correct, well-established backbone:

- **Successive Halving / Hyperband** (Karnin 2013; Li 2017) — evaluate all candidates cheaply, promote the
  survivors to progressively more expensive/accurate rungs. This is literally "increase the increment each
  survivor gets as results come in."
- **Top-two Thompson sampling / LUCB** (Russo 2016; Jamieson 2014) — the exploration/exploitation allocation:
  spend the next increment where it most changes *which candidate we'd pick*, not just on the current leader.
- **Sequential futility/efficacy tests (SPRT / GLR / Bayesian posterior boundaries)** — the *granular* early
  kills. Because every leg checkpoints per replica/λ-window (continuous S3 upload — already in place), we can
  update belief mid-rung and stop a hopeless candidate without finishing its remaining replicas.

We have ~18 binary candidates collapsing to ~6–12 degraders — **small N** — so the design is right-sized:
a Bayesian successive-halving ladder with sequential kills and a light top-two allocation, **not** a heavy
asymptotic-MAB apparatus whose guarantees are vacuous at N≈15.

## 2. The terminal objective (what "reward" actually is)

For each candidate *i* we maintain a posterior over a scalar **selective-hit score**
`S_i = P(i is a paralogue-selective, ubiquitination-competent degrader)`, decomposed into the axes the
pipeline actually measures:

- **validity** (hard gate): convergence — hysteresis ≤ 0.5, adjacent-λ MBAR overlap ≥ 0.03, cycle closure
  ≤ 1.0, Pocket-5 survival ≥ 50%. **A validity fail kills the candidate regardless of its point estimate** —
  you cannot rank on a number you cannot trust. Orthogonal to promise.
- **binary engagement** (NR4A3 ΔΔG_bind vs anchor + clean linker exit vector);
- **binary paralogue preference** (NR4A3 − NR4A1/NR4A2 ΔΔG, worst-conformer);
- **ternary cooperativity advantage** (ΔΔG_coop NR4A3 vs paralogues) — *the dominant term*;
- **ubiquitination geometry** (Lys-presentation / linker-strain feasibility).

`S_i` is what we allocate against. The cheap axes are **weak, imperfectly-correlated predictors** of the
terminal (ternary) axes — §6 is entirely about not letting that fool us.

## 3. The fidelity ladder (successive-halving rungs)

Each rung costs more per candidate and measures a new, more terminal-relevant axis. Costs are per candidate,
spot GPU, grounded in the prereg (binary pilot ~$5–15; ternary $200 cap for the 4-leg feasibility set).

| Rung | Evaluation | New signal | ~$/cand | Kill basis at this rung |
|---|---|---|---|---|
| **R0** | CPU: dock + pose + exit-vector + microstate + linker feasibility | gross geometry | ~$0 | no viable exit vector / garbage pose / ambiguous microstate unresolved |
| **R1** | Binary RBFE, **1 replica**, NR4A3, 1 druggable conformer | validity + rough ΔΔG_bind | ~$5–15 | **validity fail**, or ΔΔG_bind grossly worse than anchor beyond margin |
| **R2** | Binary RBFE, **+2 replicas + conformer panel**, NR4A3 | tightened ΔΔG_bind, worst-conformer, receptor>conformer | ~$20–45 | wide/inconsistent ΔΔG; conformer-fragile engagement |
| **R3** | **Paralogue** binary RBFE (NR4A1+NR4A2, matched conformers) | **binary selectivity signal** (first appears) | ~$40–120 | strongly anti-selective (favors a paralogue) with tight CI |
| **R4** | **Ternary feasibility** (1 replica, NR4A3 + key paralogue, VHL) | first ΔΔG_coop | ~$60–150 | no cooperativity / anti-cooperative NR4A3; paralogue ternary favored |
| **R5** | **Ternary full** (≥3 replicas × 3 paralogues + geometry) | terminal S_i | ~$300–800 | terminal — only top-k arrive; ranked, not killed |

Per-rung *total* spend stays roughly bounded because as $/candidate rises, the surviving count falls — the
successive-halving invariant. **Crucial ordering choice:** the retrospective **NR-V04 control gates R4/R5
entry for the whole program** (per the prereg) — no prospective ternary rung runs until the method reproduces
NR-V04's known selectivity. The ladder is candidate-level; the NR-V04 gate is program-level and sits in front
of R4.

## 4. The allocation policy (exploration ↔ exploitation)

Each **allocation cycle** (when GPU slots free up, up to the 8-wide spot cap):

1. **Posterior update.** For every alive candidate, update `S_i ~ (μ_i, σ_i)` from all completed legs.
2. **Top-two Thompson draw.** Draw sample vectors from the posteriors; for each candidate estimate
   `p_i = P(i ∈ top-k at terminal)` by Monte-Carlo over draws. This is the **exploitation** signal.
3. **Uncertainty reserve (exploration).** Force a fraction **ρ of slots** to the highest-**σ** alive
   candidates even if their μ is middling — a wide posterior at a cheap rung can hide a winner.
   **ρ decays with rung:** high exploration where compute is cheap and signal is weak (R1–R2), aggressive
   exploitation where compute is precious and signal is terminal-relevant (R4–R5). Default ρ: 0.5 → 0.33 →
   0.2 → 0.1 → 0.0 across R1…R5.
4. **Value-of-information gate.** Fund the candidate×next-rung moves with the highest **expected reduction in
   uncertainty-about-the-winner per dollar** (`ΔH(top-k)/$`). A candidate whose further testing cannot change
   which arms we'd promote is not funded even if its μ is high — that's the principled "well-timed kill."
5. **Promote / kill / hold.** Promote funded survivors to the next rung; kill candidates with
   `p_i < kill_threshold` **and** low VOI/$; hold the rest.

This is Hyperband's ladder with a Bayesian, VOI-weighted promotion rule instead of a fixed top-fraction — it
concentrates compute on whichever candidate currently looks most likely to be the winner **while**
protecting cheap long-shots until they're cheaply ruled out.

## 5. Sequential within-rung early kills (the granular part)

Every leg streams per-replica / per-λ checkpoints to S3. After each new checkpoint for candidate *i* at rung
*k*:

- **Futility boundary:** if `P(i clears the rung-k promotion bar | data so far) < ε_fut`, **stop the
  remaining replicas** and kill/demote — reclaim the unspent budget immediately for other arms.
- **Efficacy boundary:** if `P(i clears the bar) > 1 − ε_eff` well before all replicas finish, **promote
  early** and stop spending on confirming an already-clear pass.
- Implemented as a Bayesian analogue of a **group-sequential design** (O'Brien-Fleming-style spending) or a
  GLR/SPRT test on the running ΔΔG estimate. Because replicas are independent and checkpointed, stopping is
  clean and loses ≤ the in-flight replica.

This is the "as granular as makes sense" lever: the kill decision is re-evaluated at every checkpoint, not
only at rung boundaries.

## 6. The honesty constraints (why naive bandit pruning would sabotage us)

The single biggest failure mode: **killing a candidate whose selectivity only emerges in the ternary,
because its cheap binary numbers were middling.** By our own thesis the warhead axis is *expected* to be
only weakly selective — selectivity lives in R4–R5. So:

- **Early rungs kill on VALIDITY and GROSS failure, not on modest promise gaps.** R1–R2 prune non-converged
  or clearly-non-binding candidates; they do **not** aggressively rank-cut on small ΔΔG differences.
  Promise-based exploitation only sharpens once the *terminal-correlated* signal (R3 paralogue, R4 ternary)
  is actually measured.
- **Correlation-aware uncertainty inflation.** When propagating a low-fidelity score to the terminal `S_i`,
  inflate σ by an amount reflecting the (initially unknown) rung→terminal correlation. Cheap evidence moves
  the posterior *little* until we've learned it predicts.
- **Learn the rung correlations online.** Track how R_k scores predicted R_{k+1}/terminal outcomes; start
  **conservative** (assume weak correlation → prune gently) and let the promotion aggressiveness *earn* its
  way up as calibration data accrue. Cold-start must not over-prune.
- **Hedge on unknown fidelity-value with Hyperband brackets.** If we genuinely don't know how predictive the
  cheap rungs are, run ≥2 brackets of differing aggressiveness (one prunes hard early, one keeps more arms
  alive longer) and take the union of finalists. For N≈15 one moderate bracket usually suffices; the second
  bracket is the insurance policy against a mis-estimated correlation.

## 7. Exploit the correlated congeneric structure (compute savings)

The candidates are congeneric — their ΔΔGs are **correlated** through the shared scaffold. Model `S` with a
**hierarchical / Gaussian-process prior over the analog series** (kernel on chemical distance / shared
substituent). Then a completed leg on one analog **sharpens the posterior on its neighbors for free**, so the
allocator can skip or shorten redundant tests. This is the highest-leverage enhancement for real-dollar
savings and is unique to a congeneric (vs. unrelated) library.

## 7b. Env-load economics — the hidden cost of granularity (and how to beat it)

Every SageMaker job pays a **fixed overhead before any science happens**: spot acquisition + container pull +
conda/heavy-import activation (the openfe/openmm/amber env — the smoke test skips it precisely because it is
heavy) + S3 input staging + the **system build** (solvate → parameterize → minimize → equilibrate the
complex). A naive reading of §4–5 ("kill at the finest granularity, run one replica at a time") is a **trap**:
each atomic job re-pays all of that, so finer granularity silently *increases* cost. The fix is three levers,
all pure engineering (free):

1. **Batch within a shared env.** Promote a whole rung-cohort (same rung + same receptor/system) in **one
   job**, looping over units internally — one container pull + one conda load amortized across the batch.
   Sequential futility still applies *inside* the warm job (skip a unit's remaining replicas), so batching
   does **not** cost us the early kills — it only stops us re-paying env load to get them.
2. **Warm-worker queue.** Keep a few (≤ the 8-wide spot cap) long-lived workers that pull work-items from an
   S3 manifest; the env loads **once per worker lifetime**, not once per unit. The allocator updates the
   queue each cycle instead of launching a fresh job per promotion.
3. **Cache the shared system build.** Solvate/parameterize/equilibrate each receptor (and each ternary
   architecture) **once**, cache to S3 (the ABFE "cached reference system" pattern), and every edge/replica
   on that system mounts it. This converts a per-job O(system-build) — often the *largest* slice of "env"
   time — into a one-time cost per receptor.

**Cost model.** Total \$ = Σ_jobs [ `env_overhead` + (`build_cost` if the system isn't cached yet) + Σ_units
compute ]. `plan_jobs()` packs units sharing an env key into one job; `batch_cost()` charges `build_cost` only
for not-yet-cached systems. This overhead-aware cost is what the VOI/\$ ranking (§4.4) and the
granularity floor should optimize against — **the optimal increment size is where marginal VOI ≈ env_overhead**
(don't split work so fine that env load dominates; don't batch so coarse that you can't kill early).

## 7c. Cheap-first champion mode (good-arm identification with abstention) — the "few hundred $" gate

**Objective shift.** Best-arm ID ("find THE best of N") is expensive; often all we want is **"return the first
arm PROVEN to exceed the threshold, as cheaply as possible; if the top-ranked one clears it, touch nothing
else — else abstain."** Formally this is **fixed-confidence good-arm identification with abstention** (not
"satisficing BAI"); it is far cheaper because you **stop at the first CERTIFIED candidate** (certification =
§3, terminal-rung + anytime-valid + noncompensatory), and it can honestly ABSTAIN rather than force a pick.

**Tier 0 — near-free prior ranking (~$0–20 total, CPU / cheap-inference only).** Before any alchemy, rank
candidates with a **consensus of decorrelated cheap methods**. The menu, cheapest first:

*Binary-affinity priors (weak for selectivity alone):*
- **Ensemble / consensus docking** into NR4A3 + NR4A1 + NR4A2 (smina + vina + gnina-CNN; multiple conformers)
  — cheap, but docking *selectivity* is notoriously unreliable (the repo already caught a docking-artifact
  "selective" hit), so never a decider.
- **Endpoint free-energy rescoring:** MM-GBSA / MM-PBSA; **WaterMap-style hydration** analysis (a candidate
  that displaces an *unhappy* water in NR4A3 but not the paralogue is a real selectivity signal).
- **ML affinity/scoring:** gnina CNN, graph-net affinity models, Boltz-2 affinity head.

*Selectivity-NATIVE priors (score the ΔΔ, not the affinity — much higher value):*
- **Interaction-fingerprint (IFP/PLIF) divergence** computed *only over the paralogue-divergent pocket
  residues* (`selectivity_fingerprint.py`): a candidate whose predicted advantage comes from contacts with
  **divergent** residues is a far better bet than one leaning on **conserved** residues (likely noise).
- **Per-residue energy decomposition** (MM-GBSA attributed to divergent vs conserved residues).
- **Electrostatic / shape-complementarity difference maps** across the three paralogue pockets.

*Ternary-NATIVE priors (where selectivity actually lives — the highest-value axis):*
- **Cheap co-fold ternary-architecture triage** (Boltz / AF3): geometry + confidence (ipTM/PAE) as a triage
  prior — **triage-only** per the prereg (the epimer control forbids affinity/cooperativity ranking).
- **Rigid-body / FFT protein–protein docking** of E3+target with the warhead as a restraint (PRosettaC /
  Megadock-style): accessible ternary populations + interface complementarity, no MD.
- **Linker conformational sampling / strain** (RDKit ETKDG ensembles): is a productive ternary geometry
  reachable without strain?
- **Lys-presentation / ubiquitination-zone scan**: is a substrate Lys presented to the E2~Ub in the modeled
  ternary?

*Physics-lite bridge (medium cost, much more predictive than docking):*
- **Fast/approximate FEP** — non-equilibrium switching (Jarzynski/Crooks fast pulling) or reduced-sampling
  RBFE — a cheaper prior that correlates strongly with the eventual full RBFE ranking.

**Combine, don't pick.** Fuse the decorrelated signals by **rank aggregation** (Borda / Bayesian rank fusion)
rather than trusting any one; decorrelated errors cancel. Then **improve the prior online** with a
**hierarchical / GP surrogate over the congeneric series** (§7): each real RBFE point sharpens the predicted
ranking of the un-run neighbors. A better prior's payoff is concrete — **higher precision@1 → fewer touches,
fewer escalations, cheaper champion race.** Still buys the *order* only; the PASS decision stays on the
trustworthy readout.

**The champion race (depth-first + hard gate).** Walk candidates in prior order; take the #1 depth-first
through its cheap-first confirm path (binary pre-filter → ternary-pilot), and **STOP + DECLARE the moment it
clears the bar — never touch #2..N.** Fall back to #2 only if #1 fails. A **hard budget gate (~$300–350)**:
if no champion clears the bar under the gate, **STOP + ESCALATE (come-ask)** rather than entering the
expensive tier. (`seed_prior` / `champion_order` / `run_champion_race`.)

**Non-negotiable honesty guardrail.** The cheap prior is a **weak, biased predictor** — docking selectivity
is notoriously unreliable (the repo already caught a docking-artifact "selective" hit). So the prior **only
orders the search**; a champion must *earn* certification (§3) on **terminal-rung** evidence, never on its
rank OR on a single pilot rung (the ternary-pilot may PROMOTE but not DECLARE — only the full three-paralogue,
multi-replica terminal rung certifies). Consequence: no declaration ever rests on the prior or on invalid
numerics; the failure mode is *abstention/escalation*, not a wrong winner — but "converged" ≠ "physically
correct," so a passing candidate is a *computationally qualified* candidate, not a proven selective degrader.

**Validated** (`test_adaptive_allocator.py`, imperfect docking-grade prior, 40 seeds, $350 gate):
mean **~$232/run** to a confirmed bar-clearing candidate (vs ~$1,681 full fleet, ~86% cheaper); mean **~2.0**
candidates touched; **25/40 (63%) one-touch wins** (#1 was the hit, nothing else touched); **31/40 (78%)**
declared a genuine bar-clearer in that idealized model; **9/40 (22%) escalated** (gate hit without a pass →
come-ask). Blended expected cost to a decision ≈ **$600** with a **hard ~$350 ceiling before any sign-off**.
(This sim uses an idealized unbiased-Gaussian model and is a SOFTWARE/LOGIC demonstration only — it does not
establish the dollar or hit-rate figures for real chemistry; the authoritative error control is the
anytime-valid procedure of §3, validated separately by the no-hit campaign test. See §5/§13 for the honest
limits and the required multi-scenario stress suite.)

**Interruptible (preemptive) champion — never overcommit to a slipping #1.** The race is NOT depth-first
commit. `interruptible_champion_race` re-ranks after **every cheap increment** so a champion whose early
returns are worsening is **paused** (its posterior + checkpoints preserved, resumable) rather than run to a
verdict out of sunk cost. Mechanics: leader = **Thompson-sampled** best alive candidate (a tight observed-good
posterior wins consistently → concentrate; an inflated-but-uncertain prior wins only occasionally → probe then
drop, no chasing); a **confirmation lock** — once a candidate's P(clears bar) ≥ `lock_conf` (0.5) we lock on
and drive it to a verdict, **releasing (pausing) it if it slips below `release_conf` (0.3)**; a **switch
hysteresis** (`switch_margin` ~ the env/reload cost) so physical champion switches only happen when the
posterior gap justifies a warm-worker reload (no thrashing env load). Validated (40 seeds, prior deliberately
mis-ranks an ambiguous near-bar decoy to #1): interruptible **matched** commit-first on winner-recovery
(32/40 = 32/40) at **~$105 vs ~$233/run (~55% cheaper)** and **1.8 vs 6.3** wasted increments on the slipping
decoy. This is the "pause the top candidate if early returns say it won't pan out" behavior, quantified.

**Calibrate the prior on NR-V04.** Whether champion-first is trustworthy depends on the prior's precision@1.
Test it on the retrospective control: **does the cheap prior rank NR-V04's selective NR4A1/VHL assembly #1
among the paralogues?** If the cheap prior can't order the *known* answer, widen how many champions get
confirmed (raise the gate / confirm top-2–3) and expect more escalations. Champion-first is the **default
cheap path**; the full adaptive fleet (§3–7) is the **fallback** invoked only on escalation.

## 8. Budget controller

- **Global soft cap** (the program's ~$1–5k envelope) + **per-rung soft caps** derived from the
  successive-halving invariant.
- **Hard gates preserved:** the $200 ternary feasibility cap; `MODE=plan` dry-run GPU-hour forecast before
  any production rung; the >$50 come-ask-first rule fires before R4/R5 fleets.
- **Spend accounting** in real spot-$ per converged leg (from `list-sagemaker savings`), fed back into the
  VOI/$ ranking so the allocator sees *realized* not nominal cost.

## 9. Default parameters (right-sized for N≈12–18)

| Knob | Default | Rationale |
|---|---|---|
| top-k finalists | 3 (±50% robustness, per prereg) | matches the frozen combination rule |
| exploration reserve ρ | 0.5→0.33→0.2→0.1→0.0 (R1→R5) | explore cheap, exploit expensive |
| kill_threshold (p_i) | 0.05 | kill only when clearly not top-k |
| ε_fut / ε_eff | 0.05 / 0.05 | group-sequential futility/efficacy |
| replicas | 1 (R1) → 3 (R2,R5) | prereg standard-depth |
| correlation prior | conservative (ρ_rung=0.3 cold) | learn upward; don't over-prune |
| Hyperband brackets | 1 moderate (+1 conservative hedge if fidelity-value uncertain) | small N |

## 10. Implementation sketch

- **Pure-function allocator** `adaptive_allocator.py`: input = current posterior state (JSON in repo/S3) +
  free-slot count + realized-cost table; output = the next batch of (candidate, rung, replica-count) jobs +
  the kill list. Deterministic given a seed; unit-testable with synthetic posteriors.
- **Orchestrator loop** (the existing background-poller pattern): on each freed slot, run the allocator,
  `submit_spot` the chosen jobs (`git_ref=<branch>`), and on each streamed checkpoint re-run the
  sequential-kill test. State lives in the repo/S3 (restart-resilient).
- **Reuses everything:** the RBFE/ternary drivers, per-unit checkpointing, `MODE=plan` forecasting, the
  convergence-diagnostic gate, the frozen prereg thresholds.
- **Validation-first:** unit-test the allocator on synthetic candidates (known winner) → confirm it finds it
  under budget in simulation → only then wire to real jobs.

## 11. What this buys vs. static successive-halving

**Validated in simulation** (`tests/test_adaptive_allocator.py`, synthetic screen: 15 candidates, one hidden
selective winner, noisier-at-cheap-rungs observations, seeds 0–11): adaptive recovered the winner **12/12**
vs. static halving **11/12**, at **~$1,564/run vs. ~$2,460/run — ≈36% cheaper AND better recovery.** The
saving comes specifically from (a) **sequential futility kills** pruning survivors before the expensive rungs
and (b) **terminal early-stop** — not running all top-k finalists at the ~$500 rung once the leader is
decisive (the terminal rung dominates cost). NOTE the honest scope: this is one synthetic regime; the cost
win is regime-dependent (largest when the terminal rung dominates cost and a winner becomes decisive before
it). The robust, always-present benefit is a **better winner-recovery-per-dollar**, not a guaranteed
lower absolute cost in every regime.

**Env-load-aware validation** (same test, now charging per-job env_overhead + one-time-per-receptor
build_cost): static 11/12 @ ~\$2,571; **adaptive naive-atomic** (one job per unit) 12/12 @ **~\$2,226** — env
overhead erased much of the compute saving; **adaptive batched + cached build** 12/12 @ **~\$1,681** (~35%
under static, ~24% under naive-atomic). This is the concrete proof of §7b: **granularity has a hidden env
cost, and batching + build-caching is what lets you keep the fine-grained kills without paying for them.**

- **~30–50% fewer wasted GPU-$** vs. fixed-fraction halving in the regime where a few candidates are clearly
  hopeless and one is clearly promising (the sequential kills + VOI ranking harvest that early) — the ~36%
  simulated above sits in this band.
- **Lower risk of discarding the true winner** than aggressive static pruning, because promise-based cuts are
  deferred to the rungs where selectivity is actually measured (§6).
- **Graceful budget scaling:** hand it $1k and it returns the best-supported finalist(s) it can; hand it $5k
  and it deepens the survivors — same policy, different stopping point.

## 12. Honest limitations

- BAI guarantees are asymptotic; at N≈15 this is "principled heuristic," not a theorem. The value is in the
  *structure* (validity-first kills, deferred promise-pruning, sequential futility, congeneric sharing), not
  in an optimality proof.
- Everything rests on the rung→terminal correlations, which are **unknown a priori** and learned from few
  data. Conservative cold-start is a mitigation, not a cure.
- The allocator cannot rescue a bad *terminal* metric: if the ternary method fails the NR-V04 control, no
  amount of clever allocation produces a trustworthy result — it just fails cheaply, which is the point.

## 13. Methodology-review response (2026-07-12) — fixes applied + what remains before adoption

An external methodology reviewer returned "**not sound to adopt as specified; itemized fix list; keep the
allocator offline**; after fixes 1–6 it would be sound for an offline shadow pilot; fleet wiring follows a
separate code-level review + successful no-hit/retrospective calibration." Applied this round:

**Reframed the formalism (fix 1).** Full mode = constrained multi-fidelity **best-arm identification**;
champion modes = fixed-confidence **good-arm identification with abstention** (not "satisficing BAI"). Top-two
Thompson is an *allocator*, not a certifier.

**Separated allocation from certification (fix 1.2).** New module `adaptive_certify.py` is the ONLY PASS
authority; `adaptive_allocator.py` is scheduling-only and its old "declare on P(clears bar)" shortcut is
explicitly demoted to a scheduling demonstration.

**Noncompensatory vector pass (fix 1.3).** Certification requires BOTH the NR4A3−NR4A1 and NR4A3−NR4A2 margins
to clear simultaneously (min of anytime lower bounds ≥ bar + robustness) — a strong margin cannot average
away a weak one.

**Pilot promotes, terminal certifies (fix 1.4).** Only terminal-rung evidence can certify; the ternary-pilot
may PROMOTE but never DECLARE.

**Deleted "ZERO false declarations" (fix 2).** Replaced with the defensible claim + the **claim ceiling**
("computationally qualified NR4A3-selectivity candidate"), and the explicit list of why converged ≠ correct.

**Anytime-valid, campaign-wide error control (fix 3).** `anytime_lower_bound` (sub-Gaussian normal-mixture
confidence sequence, valid under optional stopping), `campaign_delta_split` (union bound over candidates ×
margins), a robustness margin above the nominal bar, and the 6-state machine (ORDER / PROMOTE / TECHNICAL_STOP
/ FUTILITY_STOP / PASS_CANDIDATE / ABSTAIN_ESCALATE). The 0.5/0.3 lock/release are labelled **scheduling
parameters only**. **Validated:** 0/200 no-hit campaigns declared falsely under repeated looks (~95% upper
0.015; δ=0.05).

**Invalidity ≠ failure (fix 4).** Result-status taxonomy (TECHNICAL_FAIL / GROSS_FAIL / FUTILITY /
VALID_UNFAVORABLE / VALID_FAVORABLE); technical failure ⇒ abstain/retry, not a chemistry verdict; pocket loss
recorded as a GROSS scientific outcome separate from estimator failure; a KNOWN fixed σ for the confidence
sequence (a data-estimated σ would break anytime-validity); replica-independence discounting (distinct
seed + starting state, not one parent trajectory); **content-addressed** system hash over all scientific
inputs (structure/protonation/params/restraints/mapping/coords + env), not just the software env.

**Tests added (subset of the required 14):** prior-cannot-enter-pass, pass-requires-terminal-rung,
noncompensatory, futility-on-upper-bound, technical-fail-abstains, gross-fail-is-futility, correlated-replica
discount, content-hash distinguishes scientific systems, campaign-δ union bound, permutation invariance,
anytime coverage under repeated looks, and the **no-hit false-declaration campaign**.

**STILL REQUIRED before fleet wiring (honestly not yet done):**
1. **The full multi-scenario stress suite (fix 5):** no-hit (done) + multiple-hits, at/just-below threshold,
   zero/negative and chemotype-specific rung correlation, shared paralogue/FF bias, heavy-tailed/outlier
   errors, correlated replicas, non-monotonic fidelity, difficulty-correlated failures, prior precision@1 from
   excellent to adversarial, variable spot cost/preemption/stale-batch, near-tied candidates. Report
   campaign-wide false-declaration + false-elimination + escalation + recovery + cost distribution +
   posterior calibration, all with binomial CIs (the 12/12-vs-11/12 "better recovery" is NOT statistically
   established and must be re-run paired with CIs).
2. **Real retrospective calibration (fix 6):** freeze the prior formula + weights before unmasking; NR-V04
   active + inactive Hyp epimer + matched null/nonselective controls + near-negatives; paralogue-label swaps +
   shuffled divergent-residue masks; leave-one-control-out; evaluate the COMBINED prior; co-fold as an
   architecture-feasibility FILTER only (not a favorable score contribution), given the epimer result.
3. **Allocation-robustness tests (fix 8):** arm starvation, stale-posterior updates, double-counted
   checkpoints, restart/serialization determinism, cache collisions, budget-gate breach via queued/retried
   jobs, forced-exploration floor, max unreviewed spend per batch.
4. **The GP surrogate** stays OUT of the claimed methodology until implemented + replay-tested without leakage.
5. A separate **code-level review** + an **independent terminal confirmation block** (or fully anytime-valid
   terminal evidence) before any result is reported as a qualified candidate.

**Disposition:** allocator + certifier stay OFFLINE. This round completed fixes 1–4 and part of 5–6; the items
above gate an offline shadow pilot and, after that, fleet wiring.
