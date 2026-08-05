---
id: DOC-VIEW-PLAN
title: THE ORDERED PLAN, the spend ladder and the dependency spine
level: cross-cutting
kind: generated
status: generated
generator: systems/systems_check.py
purpose: What to do next, in order, with each step's gate and cost — and the money rules and cumulative chain the order depends on.
scope: The near-term spend-gated plan. The multi-year horizon is views/roadmap-5yr.md.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

<!-- ⛔ TICKING AN ITEM HAPPENS IN systems/graph/plan.json, NOT HERE.
     A hand-edit to this file fails the build. That is the cost of one-fact-one-home,
     and it is deliberate: `marker` is a field precisely so it can be set by machine.

     38 items · 20 still open.

     ⚠ THE SKIPPED MARKER IS AN EN DASH (U+2013), NOT AN ASCII HYPHEN.
     ⚠ `Cum. ~$N` (the plan) and `Cum ~$N` (the spine) are DELIBERATELY different and must
        both stay in THIS file — pinned-figures.json subset_checks/strategy_spine_cum
        asserts one is a subset of the other WITHIN A SINGLE FILE. -->

## THE ORDERED PLAN (spend-gated) — read top-to-bottom for "what's next"

*★ **THE ITEM LAYER, AND THE MOST FRAGILE OBJECT IN THE REPO.** ⚠ **Parsed by [`work_ledger.scan_plan_items`](../../research/modalities/work_ledger.py)** on this heading string, the bullet regex and the `###` rung sub-headings; the skipped marker is an **en dash**, not a hyphen, and the scan ends at the next `##`. Renaming the heading makes the plan invisible with no error; reformatting a bullet makes an open item vanish from the work board. [`degrader-paper-schedule.json`](../../research/manuscripts/degrader-paper-schedule.json) is its declared one-for-one machine mirror. [§10](../../research/manuscripts/nr4a3-program-map.md#10--the-roadmap--one-ordered-list) is the ordered view over this layer and never restates a price.*

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
- **`[x]` Steric-exclusion DESIGN RULE (`S3`) — the measurement turned into something a designer runs** — **$0, CPU, no nod, [§10.1 row 24](../../research/manuscripts/nr4a3-program-map.md#101--open-rows-ordered-by-what-unblocks-the-most).** Serves `R7` `R15`. Two substituent vectors, a shape spec and a per-candidate scorer, in [`steric-design-rule.json`](../../research/modalities/steric-design-rule.json) (`python3 research/modalities/steric_design_rule.py --check`; the scorer **reproduces `M3`'s own 0.923-vs-0.173 over `M3`'s own 13 poses**, which is the check that would catch the rule and the measurement having become different objects). ⛔ **AND ITS CONTROL IS ATTACHED TO EVERY RECORD IT EMITS, WHICH IS THE POINT:** the paralogue's own docking **RELOCATES** these molecules by a median **5.31 Å (NR4A1) / 5.26 Å (NR4A2)**, so a high score means ***"this POSE is denied in the paralogue"* and NEVER *"the paralogue cannot bind this molecule"*** — it binds it somewhere else. Also carried on every record: the transfer is **RIGID** (the paralogue side chain is held in its own opened conformer and could rotate away), and **NR4A3's absence of clash is guaranteed by construction** and carries zero information, so only the between-class contrast is gradeable — which is why the scorer refuses to emit a signal without its matched null.
- **`[x]` Pocket-tracking re-analysis** — **$0.** Harmonized detection folded into the paper's Gate-2 wording:
  8XTT **19/20 frames detected, 3 ≥ D\*=0.53** (`C1`–`C5`) (= 3/19 among detected, 3/20 across all deposited); release
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
  recommendation: [valB-mini-r0-verdict-2026-07-25.md](../../research/manuscripts/valB-mini-r0-verdict-2026-07-25.md).**
  The first complete cycle (CI 30148463967, re-dumped 30155238348) gives **ΔΔG_coop(r0) = −0.534 kcal/mol**
  against the +0.944 target — wrong sign, 1.478 off, **both of which are r0's own superseded reading and NOT
  the lane's headline** ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 44 and 51; the
  current values are the n=3 mean −0.599 / abs error 1.543 in the scoreboard) — from legs binary **48.0046** / ternary **47.4701** /
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
  **Consequence: the statistical error (0.045) is far smaller than the miss — ~34× against the landed n=3 miss
  of 1.543, and ~33× against the superseded 1.478 r0 read that day — so the wrong sign is
  SYSTEMATIC, and replicates shrink variance, not bias.** *(1.478 is r0's reading and is superseded twice over,
  [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 44 and 51; the conclusion is unchanged by
  either correction, which is why it survives being restated at both values.)* Made worse for the replicate case, not better:
  ternary seed *s* uses the *s%n*-th relaxed SMARCA2 model, so r1/r2 are partly *different structures* and their
  spread would conflate sampling noise with homology-model sensitivity.
  **★ THE LAST OPEN DIAGNOSTIC IS NOW CLOSED — `diagnostics_complete: TRUE` (2026-07-25, run 30169056960).** The
  **ligand-only** pose RMSD was the one mandatory metric never measured. No committed artifact is a topology
  file, so the ligand was *derived*: bonded connectivity read from the hybrid System inside the `.nc`
  (HarmonicBondForce + the softcore CustomBondForce + **constraints**, where X–H bonds live) partitions 141,968
  particles into 4 protein chains, 44,860 waters, 248 ions and **exactly one** ligand-sized molecule — a
  fail-closed identification with a single candidate, not a ranked guess. Result: `n=110, heavy=59` · **pose RMSD
  max 2.765 Å, median 1.644 Å** against a 4.0 Å threshold · `ligand_stable_ok: true` · `mandatory_unmeasured: []`.
  Two *independent* corroborations, both consistent: 59 heavy atoms equals `wurz-calib-frozen.json`'s
  `validation.heavy_1 = heavy_4 = 59` (an RDKit count from freeze time, unrelated to this trajectory), and the
  ligand identified separately in the 5k-particle solvent box matches the one found in the 142k-particle assembly.
  **So the ligand did not drift — which removes the last benign explanation for the wrong sign and leaves the
  systematic where the convergence analysis put it: in the model or the reference data, not in the sampling.**
  ⚠ **Seven defects were found in this gating diagnostic on 2026-07-25, every one reporting success while
  measuring nothing** (never wired · missing `openfe` · an unguarded lazy `mbar` that deleted six other metrics ·
  slice-MBAR never converging · a fwd/rev gap taken where it is identically zero · the checkpoint never opened
  because openmmtools wants `checkpoint.nc` and the driver writes `checkpoint.chk` · a ligand-pose threshold
  applied first to bulk solvent then to a four-chain assembly). Two produced *wrong verdicts*: a silent
  `diagnostics_ok=True`, then a fabricated hard FAIL. **This is an argument for spending the next dollar on
  INDEPENDENT checks — reverse legs, cycle closure — not more replicates through the same machinery.**

  **★ THE REVERSE LEG WAS UNREACHABLE — FOUR CALLERS PINNED IT SHUT (2026-07-25, all fixed).** The preregistered
  forward/reverse antisymmetry check (`hysteresis <= 1.0` — **now MEASURED, see the ★★ result immediately
  below; the `null` this block was written against is superseded**) could not be run at
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

  **★★ THE REVERSE LEG LANDED AND THE ANTISYMMETRY CHECK PASSES — the detector that "could not be run" is now
  a MEASUREMENT (2026-07-28, reduce [run 30353349373](https://github.com/trimcrae/Rare-cancers/actions/runs/30353349373)).**
  `calib_hi_to_lo__ternary_vhl` dir=rev seed 0 reached its result on GCP L4 (free trial credit) at 4:03 PM ET
  2026-07-27, and the reducer reports **`MEASURED |ΔG_fwd + ΔG_rev| = 0.325 ≤ 1.000 (PASS)`**. One home for the
  number: the reduction JSON in `gs://…-rbfe-ckpt/valB-6hax/results/` and that run's `[REDUCE-VERDICT]`
  annotation — never re-typed elsewhere.
  **What it does and does not buy.** It is an *internal-consistency* detector, and it is the first of the three
  systematic-error detectors to return anything at all: the forward and reverse alchemical paths agree to
  0.325 kcal/mol, so the wrong sign on this calibrator is **not** a path/hysteresis artifact. That is a genuine
  narrowing — it removes one of the two remaining benign explanations, exactly as the ligand-pose RMSD removed
  drift — and it leaves the systematic where the convergence analysis put it: **in the model or the reference
  data.** It is emphatically **not** evidence that ΔΔG_coop is right; antisymmetry is a check the sampling can
  pass while the answer stays wrong.
  **The calibrator verdict itself is still `INDETERMINATE`, and for a different reason than before:**
  `n_replicates=1`, `per_replicate_ddG_coop=[-0.522]` against `target=0.944`, so there is no replicate SD and
  the cycle cannot be graded. Cycle closure (the redundant edge) is **RUNNING as of 2026-07-29, 11:24 AM ET** —
  see step 5 below for its status and gate reading; it was the last unrun systematic-error detector.
  ⚠ **−0.522 here, −0.534 in the RUNG 2b timestep rows above, and BOTH are correct — do not "reconcile" them.**
  This line is the calibrator's CURRENT reading, which uses the restrained binary arm (Appendix A 44). RUNG 2b
  compares a 4 fs cycle against the *unrestrained* 2 fs one, so its comparator must stay **−0.534**: swapping
  in −0.522 would measure the restraint rather than the timestep, which is the whole quantity that gate exists
  to isolate. Changing either number in isolation silently breaks the other.
  **The blocker is still r1+r2, but they are no longer blocked — both are RUNNING** (2026-07-29, 11:10 AM ET).
  The partial-charge defect that had them dying on dozens of hosts is fixed and merged to `main`; each arm
  holds an RTX 5090 at **$0.005119/ns · 1.50× basis**, under the buy line. It was never held on price, never
  on capability, and never on anything GCP can supply (`GPUS_ALL_REGIONS = 1` makes GCP strictly serial) —
  that last clause still stands and is why the closure triangle went to Vast too.
  **Superseded, retained** (per rule 1, because the old status is quotable): "withheld by the failure breaker
  … its fix is on `fix/ternary-vast-deaths` and unmerged as of this writing." The branch is merged; the
  breaker's withholding of *these* units ended when the fix landed, and the four TRIANGLE units it was still
  withholding were cleared by `task=supersede-failed leg_only=to_lo2` at 11:18 AM ET — a deliberate gesture
  after the cause was fixed, not a loosening of the breaker, which re-arms on the next fresh `status=failed`.

  **Recommended next steps (spend order) — REVISED 2026-07-25 (LANE 5); steps 1, 2 and the ligand diagnostic are
  DONE, and step 4's named design was REFUTED for $0 before any spend:**
  1. ✅ *done, free* — the convergence analysis above, and now the **ligand-only pose RMSD** (`diagnostics_complete: TRUE`).
  2. ✅ *done, free* — **the admits-zero gate defect fix was already APPLIED in place at 8:25 AM ET**
     (commit `3f11cbf5`, delegated reviewer authority) — not merely proposed. It has since been **independently
     audited** (`valb_gate_audit.py`, calling the shipped gate): **strictly stricter across 20,468/20,468 grid
     points with 0 counterexamples**; **conditioned on r0 the corrected PASS rate is 0.0 % in every cell**
     (superseded rule: up to 71.6 %); an exhaustive 58,081-cell (r1,r2) scan gives **0 PASS under both**, so it
     demonstrably **does not rescue the failing result**; discrimination improves 2.0× → 10–3330×. Ratification
     block: §8 of [valb-gate-defect-fix-audit-2026-07-25.md](../../research/manuscripts/valb-gate-defect-fix-audit-2026-07-25.md),
     which states the "applied after an unfavourable result" optic plainly as the risk.
  3. *in flight* — the **reverse** ternary+binary legs, testing |ΔG_fwd + ΔG_rev|.
  4. **⚠ THE NAMED RESCOPE IS DEAD — the P-series cannot carry this calibrator, established for $0 on real data**
     (`valb_pseries_chem.py` → `valb-pseries-chem.json`; RCSB REST + RDKit MCS in the production mapper's own
     container). **6 of 10 pairs change formal charge** — including **P1→P4 (+2.53), which is `charge_change: -1`
     and therefore blocked by the same missing charge correction that blocks 8 legs of `step1_fanout`** — and the
     4 charge-neutral pairs perturb **58–80 heavy atoms** against the **2** of the edge already running. P4's
     structure (9HYO) is also only **3.74 Å**, so it would not have fixed the resolution problem either.
     **General conclusion worth stating in the paper: a ≥2 kcal/mol ternary calibrator that is simultaneously
     small, charge-neutral and mappable may not exist in the public literature** — large cooperativity
     differences are *produced by* large chemical changes.
  5. **★ RECOMMENDED INSTEAD — a synthetic closure TRIANGLE, RE-SCOPED BY ITS OWN $0 PRE-GATE.**
     **`[~]` RUNNING — AND THE FIX IS PROVEN ON THIS LANE, not merely deployed to it (2026-07-29, 12:12 PM
     ET).** Both binary legs have written committed checkpoints (`warmup/64` → `192`), and these are the exact
     units that died 15 and 7 times at `proto.create` on the partial-charge defect. Passing setup and
     committing is the first direct evidence the fix holds for the triangle's own endpoints — the earlier
     evidence was from the 4 fs replicate arms, a different morph. Progress since has been by COMMITTED
     CENSUS, never a watchdog verdict.
     **`[~]` RUNNING 2026-07-29, 11:24 AM ET — all four legs rented in parallel on Vast.** The gate cleared at
     **1.36× basis** (`$0.004637/ns` mean, against the `$0.006539/ns` buy line) on a deep board — 163 offers,
     159 qualifying, 100 priceable — projecting **$7.73 against this rung's $15.40 ceiling**. It had been
     stalled since 2026-07-28 not on price but on the partial-charge defect, which killed the four units on
     15, 15, 7 and 21 separate hosts and left them withheld by `leg_failure_breaker`; the fix landed 10:53 AM
     ET and the stale failed records were superseded at 11:18 AM ET. Cost of that stall being *legible*: the
     triangle gate had no branch for the breaker's exit code, so it printed the block as `HELD on price` —
     fixed in the same session and pinned by `tests/test_gate_exit_codes_render_distinctly.py`.
     **`[x]` BUILT AND RUNNABLE 2026-07-27 (LANE 19).** It was fully costed and fully argued and could not be
     *run*: no leg id, no third endpoint, no launcher mode, no reducer. It now has all four —
     [`valb_triangle_legs.py`](../../research/modalities/valb_triangle_legs.py) (the 4 new legs plus the derived
     third vertex, frozen in [`valb-triangle-frozen.json`](../../research/modalities/valb-triangle-frozen.json)),
     `MODES['triangle']` in [`ternary_vast_launch.py`](../../research/modalities/ternary_vast_launch.py), and
     [`valb_triangle_reduce.py`](../../research/modalities/valb_triangle_reduce.py) → `R`. Venue **Vast**; GCP was
     declined deliberately — its scarce quantity is **GPU-days, not dollars**, and this rung would cost
     ~7.3 SERIAL days of the only GPU to save the plan figure below.
     **Three invariants are enforced in code, not remembered**, because each silently turns `R` from a
     path-error detector into a *protocol-difference* detector: **2 fs** (a mode-level pin that beats the
     lane-wide 4 fs export — r0 is 2 fs and r0 *is* T1), **seed 0** on every leg, and **UNRESTRAINED** binary
     legs matching r0. *(The restrained binary re-run is a DIFFERENT experiment; the two must never be
     conflated or their legs mixed in one reduction.)*
     T1 = cmpd1→cmpd4 **is r0, reused** at coefficient +1 (verified: the triangle closes in T1's as-run
     direction, no sign flip). Evidence:
     [valb-closure-triangle-pregate-2026-07-25.md](../../research/manuscripts/valb-closure-triangle-pregate-2026-07-25.md)
     (`valb_triangle_chem.py` in the production mapper's own container + `valb_triangle_closure.py`, 19 tests).
     **Three corrections to the design as originally proposed:**
     - **(i) T3 is a DOUBLE perturbation for all four named cmpd4′ candidates** — X and Y act at different
       sites, so the closing edge carries both, which `rbfe_map.py` forbids *specifically for closing edges*
       (*"Each closing edge is itself a SINGLE-site change (not a double mutation)"*). **Use an AZA-SCAN at the
       linker ring instead:** cmpd1 (aza) → cmpd4 (all-carbon) → cmpd4″ (aza moved) — three vertices at **one**
       site, every edge **single-site, charge-neutral, a pure element change with ZERO heavy dummies**, and
       entirely inside the linker so it touches **no pharmacophore** (all four named candidates land on one).
       Hand-verified from the SMILES: the linker ring is `c4ccnc(c4)` with a carbonyl and a piperazine at the
       substituted positions, leaving **exactly 3 free CH** vertices.
     - **(ii) Price is ~$6.83 at n=1 and ~$27.32 at n=3, not $5.9/$17.6.** Three corrections, and **the largest
       is NOT the iteration basis**: (a) the 2800-iteration/3.5e6-step basis is +16.7 %; (b) solvent legs add
       ~$1.31 if run by default; **(c) T1 has only r0, so an n=3 triangle is 16 legs, not 12 (+33 %) — and it
       silently re-includes the r1/r2 spend the r0 verdict argued against.** At 4 fs everything scales by
       **0.643, not 0.5** → n=1 ≈ $4.39. Every figure is a **ceiling** (the binary leg is charged at the
       ternary rate despite lacking the SMARCA2 bromodomain).
     - **(iii) `_endpoint_pose` cannot build any cmpd4′ today** — it has exactly one mutation path
       (`_pyridine_to_benzene_pose`) and raises `SystemExit("refusing a wrong-molecule leg")` otherwise. The
       claim that "the machinery carries over unchanged" is false; the aza-scan needs a one-line generalisation.
     **Reporting rules that fall out of the algebra:** report **`R_ternary` and `R_binary` SEPARATELY** — since
     `R = R_ternary − R_binary`, a clean `R` can be two large closures cancelling, and both come from the same
     six legs. And **run all three edges at seed 0**: seed *s* selects the *s%n*-th relaxed SMARCA2 model, so
     mixed seeds mean different Hamiltonians, unshared endpoints, and `R` stops being a closure residual at all.
     **★ HONEST LIMIT, SHARPENED FROM "consistency, not accuracy" TO SOMETHING MUCH STRONGER: closure is
     IDENTICALLY ZERO for ANY per-endpoint state-function error.** Writing `ΔΔG_calc = ΔΔG_true + e`, the true
     terms telescope around a cycle so `R = Σe`; and if `e(A→B) = ε(B) − ε(A)` — which is what a *state*
     property gives — that telescopes too. **So closure sees only the NON-CONSERVATIVE part of the error.**
     Invisible to it: **force field, the SMARCA4→SMARCA2 homology model, NAGL charges, protonation, and the
     reference data**. Visible: λ-sampling/hysteresis, endpoint-state inconsistency, inconsistent atom maps.
     *(Verified numerically two ways: max |R| ≈ 1e-14 over 20,000 random state-function draws, non-zero the
     moment a path error is added.)* The known-answer **accuracy** requirement therefore stays **OPEN**.
  6. **⚠ Rev-leg decision tree — and "the triangle is worth buying under either branch" is RETRACTED. It was
     recorded here on 2026-07-25 afternoon and its own pre-gate refuted it the same evening.**
     - **Branch A** (|ΔG_fwd + ΔG_rev| ≈ 0 ⇒ the systematic is in the **model or the reference data**): closure
       is **provably blind to both** by the telescoping identity above. It would return a clean `R` and diagnose
       **nothing**. *Refuted for diagnosis.*
     - **Branch B** (large ⇒ path error): closure is the right *class*, but the reverse leg already establishes
       it for those 2 legs, and the design's own instruction is **"fix the protocol first"** — so a triangle
       bought before the fix measures the **old** protocol. *Redundant, then stale.* Replica mixing **0.8915**
       against the 0.90 ceiling leans toward this branch, i.e. **the worst branch to buy into.**
     - **★ The real reason to buy is narrower and specific.** The fwd/rev pair already in flight **is** a closed
       2-cycle, so the triangle only earns its keep where a 2-cycle cannot reach. Over 4000 draws — state-function
       error: 2-cycle 0.00 / 3-cycle 0.00; symmetric path bias: both 1.00; **antisymmetric per-edge bias:
       2-cycle 0.00, 3-cycle 1.00.** That last row is the triangle's **exclusive** territory, and on an
       equal-cost 4-leg comparison it still beats both alternatives.
     - **Order:** read the rev leg → **Branch B ⇒ fix the protocol, do NOT buy** → **Branch A ⇒ buy the ~$1.31
       SOLVENT-ONLY closure pre-scout first** (2 new legs; T1's solvent leg already ran; a full machinery closure
       — atom maps, endpoint identity, λ schedule, charges — in a ~5k-particle box at **19 %** of the scout
       price, able to falsify the triangle before any 142k-particle leg), then the **~$6.83 n=1 scout**.
       **Do not buy n=3 at ~$27.3 without a separate decision.**

  **★ THREE MEASUREMENTS THAT REORDER THE PROBLEM (LANE 5, $0):** (i) even the *corrected* gate certifies only to
  a **factor of 4.1** (accept band [+0.472, +1.944] on a +0.944 target); (ii) **P(PASS) has a hard ceiling of
  `P(sample SD ≤ 0.75)` = 66.8 % at σ = 0.7, independent of the target** (analytic and MC agree to 0.15 %) — so
  above ~2 kcal/mol **only precision buys anything**; (iii) sweeping the target shows **2.0 kcal/mol is the
  knee**, which *derives* this file's "≳2" from the gate's own arithmetic instead of asserting it. Consequence:
  **redesigning for a tighter cycle SD beats hunting a bigger signal.**

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
  ternary leg (**1.56×** cheaper — *not* 2×, see cost lever 1 — and the ladder has ≥6 of them). NaN or a shifted
  ΔΔG → stay at 2 fs.

  **★ THRESHOLD RATIFIED 2026-07-25 (trimcrae delegated judgement): |ΔΔG_coop(4 fs) − (−0.534)| ≤ 0.7 kcal/mol.**
  The frozen wording says "within replicate SD" and **there is no replicate SD** — the 2 fs arm is a single
  cycle. Lane 4 pre-specified **0.7**, the repo's own assumed replicate SD, **before any number existed**.
  Ratified as written, for one reason that outranks the others: **pre-specification is the property that
  matters, and revising a threshold now — after the probe survived — would be precisely the retune this program
  forbids.** Both arms are seed 0, hence the same homology model *index* — and the two lanes each built their
  own copy of it, so what is established is that the two builds have an identical atom set (measured:
  [ternary-4fs-vast-findings.md §2d](../../research/compute/ternary-4fs-vast-findings.md)), not that they started
  from bit-identical coordinates.
  **⚠ AND THE COMPARATOR STAYS THE UNRESTRAINED r0 VALUE.** The r0 cycle now also has a **restrained** binary
  arm ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 44), and swapping that reading in here
  would pair a restrained arm against the 4 fs cycle's unrestrained one — measuring the restraint, not the
  timestep. The restraint is deliberately a different Hamiltonian and is invisible to a composition census
  (it adds a force, not atoms), so this is the one place the like-for-like pairing has to be stated rather
  than inferred.
  **Recorded honestly: 0.7 is LENIENT, and the leniency runs in the unsafe direction.** It is an *assumption*,
  not a measurement, and today's protein-mutation benchmark showed between-setup SD is strongly regime-dependent
  (**±0.175** on a near-null perturbation vs **±1.077** on a hot spot, a 6.2× spread). A 4 fs-vs-2 fs comparison
  on the *same system with only the timestep changed* is a **small**-perturbation regime, so the honest expected
  SD sits near the ±0.175 end — which makes 0.7 roughly 4× wider than the physics warrants. Since a PASS *buys*
  a protocol change, a too-wide band errs toward adopting 4 fs on weak evidence. **Therefore, reporting rule
  (additive, not a loosening): report the actual |Δ|, and a pass landing in the 0.35–0.7 band is
  "consistent but WEAKLY DISCRIMINATING" — adopt provisionally and require the next ternary replicate to
  confirm it, rather than treating 4 fs as settled.**
  **✅ THE PRE-EQUILIBRATION CONFOUND IS RESOLVED (2026-07-25, $0) — the 2 fs baseline WAS pre-equilibrated.**
  The caveat this replaces read: *"`use_preequil` for the 2 fs baseline was never verified — only the workflow
  default of 0 is recorded"*, and it would have made a NO-GO uninterpretable.
  **⚠ BUT THAT DOES NOT MAKE THE TIMESTEP THE ONLY DIFFERENCE, AND THIS ENTRY USED TO SAY IT DID
  ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 45).** Measured 2026-07-28, $0, from the
  committed trajectories themselves: the two arms run the **same alchemical system** — solute identical
  atom-for-atom in every arm, and the neutralising ion excess (i.e. the solute's formal charge) invariant across
  every build — but they are **two independently constructed builds of it**, on different lanes, providers and
  GPUs, each with its own staging, solvation and pre-equilibration. Their ternary boxes differ by 675 bulk
  waters and 4 ions. **A disagreement would therefore still not have been attributable to the timestep alone**;
  the agreement is a cross-lane independent reproduction, which is a different and in one respect stronger
  claim. Evidence, the full composition census and the ΔΔG sizing:
  [ternary-4fs-vast-findings.md §2d](../../research/compute/ternary-4fs-vast-findings.md).
  **How it was settled, and why a cache listing could not do it.** A read-only setup-cache probe (added to
  `gcp-quota-check.yml`, dispatched against this branch — it writes nothing and cannot perturb the concurrent
  GCP leg) shows **three** versions coexisting for the forward leg: `v1`, `v1pe`, **`v2pe`**. So *presence* is
  not the discriminator — several caches legitimately exist and a listing cannot say which one a leg
  **restored**. The decisive field is the leg's own `setup_cache_version`, whose physical fingerprint is the
  **particle count**: `v2pe` (alchemy from the plain-MD-relaxed complex) = **141,968**; `v1` (raw) = **146,020**
  (`ternary_fep_reduce._SYSTEM_IDENTITY_FIELDS`). **The committed r0 forward `.nc` holds 141,968 particles** —
  measured independently by the ligand-identification work, which partitioned exactly that many particles into
  4 chains, 44,860 waters and 248 ions — and `nr4a3_ternary_fep.py:682` records the same fingerprint verbatim
  (*"fwd's 141,968-particle v2pe"*). **⇒ r0 is `v2pe`, pre-equilibrated.**
  *(This is also the fingerprint that caught the four failed reverse attempts, which ran a 146,020-particle `v1`
  build against the forward leg's 141,968-particle `v2pe` — a mismatch `protocol_hash` cannot see.)*
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
  [§Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) and **must not be cited**; the
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

  **Consequence: do not pay for the re-run as built.** It is `[HELD]`.

  **★ THE PREREG AMENDMENT IS DONE (2026-07-25, trimcrae-delegated) — and it does NOT authorise the re-run.**
  [AMENDMENT 1](../../research/modalities/nr4a3-nrv04-covalent-feasibility-prereg.md#amendment-1--2026-07-25-dated-defect-fix-trimcrae-delegated)
  is appended to the prereg with the frozen text left **unedited**. The standard applied: a rule may be amended
  only if its *statistic is shown to lack discriminating power*, demonstrated independently of whether we liked
  its answer. Four rulings:
  - **R2 retired as a gating criterion** → descriptive only. `frac_frames_in_contact` took **18 values and one
    distinct value, 1.0**, including `warhead_only` (no E3-binding moiety) and `recruiter_epimer` (inactive
    stereoisomer). Zero variance across the contrast ⇒ cannot score the contrast.
  - **Frozen criterion 3 removed from the GO condition** — it depended entirely on R2 discriminating, so it was
    **unsatisfiable**, and the gate returned NO-GO regardless of the science. Uninformative, not conservative.
  - **`recruiter_epimer` demoted** to a descriptive sensitivity leg — it runs as a full ternary, not the binary
    §3 specifies, and 6 ns from a co-folded pose cannot resolve a binding-affinity difference anyway.
  - **★ NEW BINDING CRITERION A1 — input admissibility, and it FAILS NOW.** A covalent leg must stage its
    electrophilic carbon within bonding distance of the **target-chain** Cys Sγ.
    ⚠ **CORRECTED SAME DAY BY [AMENDMENT 2](../../research/modalities/nr4a3-nrv04-covalent-feasibility-prereg.md):
    A1 was measuring the WRONG CYSTEINE.** It resolved the *nearest* of the construct's **six**, which is
    **C566**, not the preregistered site **C551** (offset 344: co-fold resid 222 = C566, 207 = C551; the panel's
    legs record resid **222** throughout). **At C551 the real distances are 28.46 Å (`cov_nr4a1`) and 36.43 Å
    (`warhead_only`), and 28.42–39.11 Å across ALL 34 co-fold models** — against a ~1.8 Å C–S bond.
    *(Superseded, do not cite: 8.99 / 16.39 Å.)* **This makes A1 more binding, not less: at ~9 Å it was NEARLY
    PASSING an 8.0 Å limit, so a co-fold seating celastrol 7 Å from C566 would have PASSED while the real site
    sat ~28 Å away.** Two further defects shared the root cause and are fixed: the covalent **restraint would
    have been built onto C566**, and **`cov_c551a` was mutating C566** — the control named for removing C551
    engagement was not touching C551 at all. Boltz seats
    celastrol against no NR4A1 cysteine in any co-fold in the bucket, so §5 criterion 2 (*does covalency swamp
    the ternary signal* — the panel's stated crux) is **unevaluable on these inputs**, not merely unmeasured.
    Enforced in code (`nrv04_covalent_md`, `MAX_COVALENT_TETHER_A` default 8.0 Å, override only with a recorded
    deviation) and **retrospective in force** — it binds the NR-V04 retrospective's covalent legs too.

  **Non-rescue, stated as the integrity test:** the amended gate leaves the panel exactly where the unamended one
  did — **`[HELD]`** — because A1 fails on every available input. What changed is *why*: from "a gate that can
  never pass" to "inputs that do not instantiate the contrast." **It converts no NO-GO into a GO.** Stated
  plainly: removing an unsatisfiable criterion *is* a loosening, since GO becomes reachable where it was not;
  the justification is the measured absence of discriminating power, not the unwelcome verdict. Same degenerate
  class as valB_mini's gate that **admits the null** — one always fails, one passes anything.
  **★ SAID, 2026-07-25: the covalent legs are DROPPED and the panel is re-scoped to NONCOVALENT.** The re-fold
  route was **run and refuted** for **$0.05** on Vast (2 systems × 3 seeds), not argued away: deleting the E3
  makes seating *worse* (33.6/36.6/44.7 Å vs ~28 Å ternary, so the ternary arrangement is not the cause), and a
  **steered** co-fold that demonstrably honoured an explicit `max_distance: 6.0` restraint to residue 207
  (~37 → ~15 Å, contacts doubled) **still never satisfied its own 6 Å bound on any of three seeds**, parking
  celastrol near the buried C505. **One predictor** (Boltz-2) fails to produce the pose across 7/7 clean models, 4 seeds and 3 prefixes *(the "2 providers" are compute hosts, not two independent predictors — so this is a Boltz-2 result, not a statement about structure prediction in general)* and no deposited celastrol–NR4A1 structure constrains it, so the only route left is a **hand-placed
  pose** — which fixes the *comparison* without supplying the *evidence*. **This is a statement about the
  predictor, not about whether celastrol binds C551**, which is literature-anchored (Zhang 2018,
  doi:10.1039/C8CC06140H). **Retiring them costs little: Leg 0 already did their job for $0** — the reactive Cys
  is unique to NR4A1 (NR4A2 Tyr, NR4A3 Thr579), which is the covalent confound's actual content — and NR-V04 is
  already a demoted *biological holdout*, so modelling its covalency inverts the ladder.
  *Hypothesis the amendment raises and the re-run can test (not asserted): the superseded covalent-vs-noncovalent
  null (2/3 = 2/3) is what one predicts if the "covalent" leg never carried a bond.* Full evidence:
  [nrv04-covalent-panel-recovery-2026-07-25.md](../../research/modalities/nrv04-covalent-panel-recovery-2026-07-25.md)
  · prior chain forensics
  [nrv04-cofold-chain-forensics-2026-07-24.md](../../research/modalities/nrv04-cofold-chain-forensics-2026-07-24.md).

  **★ FOUR BUGS FOUND HERE PROPAGATE TO THE UNLAUNCHED NR-V04 RETROSPECTIVE (RUNG 4), WHICH SHARES THIS DRIVER —
  both are fixed with regression tests, and the retrospective must not launch on the old code.**
  (i) **`_reactive_cys_by_geometry` was chain-blind** — a second live instance of the *same* defect class as the
  chain split; it is now restricted to the identified target chain, raises above an 8 Å preformed-adduct limit on
  covalent legs, and records its search diagnostics. (ii) **R3 reported NANOMETRES under an Ångström label.**
  OpenMM positions are nm; R1 converted (`* 10.0`), R3 did not, so **every committed R3 is ~10× too small** —
  reading as ubiquitination-competent (~2–4 Å) when the true separation is **~30–49 Å**. Independently
  cross-checked: `warhead_only` reported `min_A` 2.34/2.44 against a t=0 distance of **25.21 Å**.

  **★ HIGHEST-LEVERAGE INFRASTRUCTURE CHANGE FOR THE WHOLE TERNARY PROGRAM (adopted as a requirement, 2026-07-25;
  ✅ IMPLEMENTED 2026-07-30): every MD driver must persist a strided TRAJECTORY.** Tens of MB against the ~112 MB
  System XML the driver *already* uploads — and every analysis defect above (wrong chain split, chain-blind
  cysteine search, the R3 unit error) would then have been correctable for **$0** instead of costing a re-run.
  This is the concrete, general lesson from a panel that produced three data-invalidating defects and left
  nothing to re-derive from. **The requirement stood unimplemented for the whole of that period and the
  retrospective would have inherited the gap** — what shipped, why it is an *analysis-atom* closure rather than
  every heavy atom, and what that does and does not buy, is in
  [§WHAT THE LANDED RESULTS CHANGE](../../research/manuscripts/nr4a3-program-map.md#-what-the-landed-results-change-about-the-remaining-plan) 4,
  which is the one home; code: [`md_analysis_traj.py`](../../research/modalities/md_analysis_traj.py).

### RUNG 4 — warhead map, differential atlas, retrospective gate

- **`[~]` Step 1 fan-out — cmpd19 congeneric map** — **~$36 ($15–80; ≈19 RBFE edges × ~13.7 ref GPU-h) ·
  Cum. ~$84.** **RESUMED and RUNNING as of 2026-07-27** — the old *"HALTED at ~$2 with 0/19 ΔΔG"* framing is
  retired. **1 edge complete** (`cw_ev_5cooh`, ΔΔG_bind **0.688 ± 0.197** kcal/mol — a within-run MBAR
  uncertainty, **not** a replicate SD), **1 edge permanently BLOCKED** (`cw_bio_nmethyl_amide`: no available
  mapper reaches the **20-atom provable floor** — LOMAP 17/19, Kartograf 18, against a complete 22-atom map
  that exists as a graph fact, and both LOMAP budgets returned in **0.01 s**, so the MCS timeout is measured
  *not* to be the mechanism. A relaunch aborts identically and buys nothing), **17 remaining and being placed
  as the market allows.** Spend, live state and `$/ns` are on the IN FLIGHT board and in
  [`realised-spend.json`](../../research/modalities/realised-spend.json) — not restated here.
  Full record: [step1-fanout-lane.md](../../research/modalities/step1-fanout-lane.md).
  **Scope, if resumed:** the price covers **tranche 1 only** — the 19 edges at their charge-**conserving**
  microstate leg on the **primary frame**. The 8 charge-changing legs are *blocked* (no charge correction
  implemented) and the 6-frame conformer/paralogue axis is a **separate ~6× spend** — so tranche 1 yields a
  single-conformer **conditional** map, **not** the selectivity readout and **not** the sensitivity ranges.
  **Gate:** Val A satisfied (cite OpenFE) AND the Step 1 pilot behaved.
  **Timestep is NOT a lever** — measured free on CPU: the protocol runs at OpenFE's default `constraints=hbonds`
  + HMR 3.0, every X–H is constrained, so all edges are already 4 fs and no 2× saving exists.
  **The "HELD by decision" line that stood here is SUPERSEDED** — the hold was reversed on 2026-07-26 and the
  lane is running; §Open decisions 4 records what retired it.
- **`[ ]` Step 1 fan-out · REPLICATES ON THE OPEN CYCLE — the map's two open caveats share ONE fix** —
  **~$25 (3 edges × 2 further replicates)** · Cum. ~$109. **Added 2026-07-30.** The fan-out delivered 18 edges
  at **one replicate each**, and that single fact is what leaves two separate things unresolvable:
  1. **`cycle_3carbonyl` does not close** (R = +1.307 against a ±1.0 tolerance). The residual is a property of
     the LOOP, so it cannot name the guilty edge — and at n = 1 it also cannot be separated from three unlucky
     single draws. **Its three edges therefore carry a reservation wherever they are quoted**, which is a live
     tax on the paper's §2.9.
  2. **The pilot and the fan-out disagree by ≈0.78 kcal/mol on the SAME nominal perturbation**
     (`cw_ev_5nh2`: +1.84 ± 0.36 vs +1.064 ± 0.118) — several times either stated error. Different lanes and
     settings, so it is not a like-for-like replicate and licenses no reproducibility statistic in either
     direction; it is currently reported as an unreconciled discrepancy.
  **What replicating the three edges of that cycle buys, and why it is one purchase not two:** it attributes
  or dissolves the closure violation, *and* it delivers **the binary lane's first measured replicate SD**. The
  program owns exactly one replicate SD today (0.375, on the **ternary** lane) and transfers it everywhere —
  including into the resolvable-margin figure in §MECHANISM-FIRST and into `S`'s power. A binary-lane number
  would stop that being a transfer.
  **★ THIS IS BRINGING A TEST *TO* ITS FIELD STANDARD, NOT PAST IT** — the distinction CLAUDE.md §5 draws, and
  it matters because "more replicates" is otherwise the thing that rule defaults **NO** to. The repo's own
  stated RBFE/ABFE standard is *"converged fwd/rev + ~3 independent replicates + honest replicate-SD, not
  MBAR-SE error bars"*; this lane shipped at **one**, and the paper says so in three places. Scope is
  deliberately **3 edges of 18**, not the map — the open cycle is the decision-relevant subset.
  **Price, DERIVED not typed:** `realised_usd` **$73.79** over `n_computable` **18** edges
  ([`realised-spend.json`](../../research/modalities/realised-spend.json) →
  [`step1-fanout-map.json`](../../research/modalities/step1-fanout-map.json)) ⇒ ~$4.10/edge × 6 edge-replicates.
  **Gate:** the market, on the same buy line as everything else. **NO-GO reading:** if the replicated cycle
  still fails to close, the defect is mapping or setup rather than sampling, and the three edges are
  **withdrawn from the ranked table** rather than carried with a caveat.
- **`[ ]` The generation-matched null's GENERATIVE arm — control (c), the one that addresses the confound
  actually raised** — **$0 prep + PROJECTED GPU (excluded from the pinned total)** · **Added 2026-07-30.**
  The committed control is the **scrambled-objective** arm, which isolates the winner's curse in the
  **SELECTION** step. The reviewer's confound is the **GENERATIVE** one: `denovo_401` was generated
  *conditioned on the NR4A3 pocket*, and the decoy null it beats was generated for no pocket at all.
  ⚠ **The arm that ran cannot exclude it, and the arithmetic says so out loud:** 0 survivors of 191 bounds
  the manufactured rate at **≤0.0157** (rule of three, 95 %) against the real campaign's own **0.0052** —
  **3×** — with Fisher p = 0.5. **Narrowed, not excluded**, and the deliverable table is the one home for that.
  **What control (c) is:** a *fresh* generation into the **NR4A1** metad-opened pocket, then the identical
  generate → developability → dock → multi-snapshot MM-GBSA → best-of-N funnel. Any NR4A3-selective survivor
  it produces is a manufactured false positive by construction, because the molecules were designed for a
  different pocket. **The driver already supports it** (`nr4a3_generation_matched_null.py MODE=prep-manifest`
  → control receptor manifest; `MODE=reduce` folds the result into the same artifact), and the control
  receptor **exists** — `results/nr4a3-matrix/nr4a1-opened.pdb`, the criterion-matched opened NR4A1 conformer
  §2.5 already uses.
  ✅ **THE $0 HALF IS DONE (2026-07-30): the control receptor and its manifest are staged and committed** —
  `results/nr4a3-genmatched-control-c/`, built by `MODE=prep-manifest`. **The paid half is one generation +
  one funnel pass**, and the lane is launch-ready rather than needing a build first.
  ⚠ **AND STAGING IT SURFACED A TRAP THAT WOULD HAVE INVALIDATED THE CONTROL SILENTLY.** The two committed
  NR4A1 artifacts describing this pocket **do not share a residue numbering** — the LANE-13 release ensemble
  carries `cv_residues` in UniProt numbering, the matrix's opened conformer is renumbered — so handing one
  artifact's numbers to the other boxes **ten wrong residues and reports success**, the same shape as the
  positional chain split that cost the NR-V04 covalent panel its entire spend. The box is therefore **not a
  remembered list**: it is re-derived by matching residue **IDENTITIES**, and **exactly one** alignment of 400
  candidates reproduces all ten. One hit is a resolution; several would have been a fit, and a test fails if
  that ever becomes true.
  ⚠ **Priced PROJECTED and excluded from the pinned total**, per §Spending rules 4: the real campaign ran this
  exact funnel, but its cost was never broken out as a ladder line, so there is no completed benchmark leg to
  quote. Price it off the real campaign's ledger before buying it, not off this entry.
  **Gate:** none upstream — it is a control on work already in the paper. **Reading, pre-registered here:** a
  manufactured rate at or above the real campaign's own survival rate means the confound is **not** excluded
  and §2.6/§2.7 keep their current hedges; materially below it means the survival is not a generic funnel
  artifact. **Either outcome is publishable and neither unlocks anything downstream.**
- **`[x]` TIER-0 · NR4A paralogue-UNIQUE reactive-residue map — DONE 2026-07-24 · $0 · GATE PASS/GO.** Full-length
  UniProt (P22736/P43354/Q92570/Q01844) + dual-aligner agreement + matched-model geometry
  (`nr4a_paralogue_unique_residues.py`, 15 unit tests, run on CI because the sandbox proxy blocks UniProt).
  **4 NR4A3-unique cysteines** (2 exposed) ⚠ *out of **20** enumerated — the other 16 are SHARED, and uniqueness here is enumerated **ONE-WAY only**: the reciprocal handles (both paralogues carry C534 where NR4A3 has S565; NR4A1 carries C551) are absent from the JSON*: **C397** — NR4A1 N363 / NR4A2 S363, RSA 0.395, **10.9 Å** from the
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
- **`[!]` NR-V04 retrospective — preregistered holdout — ★ HELD 2026-07-25: IT COULD NOT HAVE RETURNED A
  VERDICT UNDER ANY PHYSICS, TWICE OVER** — **~$24 ($5.6–78; repriced from ~$21 onto the 2800-iteration basis)
  · Cum. ~$107.**
  A **$0** pre-spend audit (`nrv04-retrospective-prespend-audit-2026-07-25.md`) found **two independent, silent
  blockers**, each of which would have consumed the whole spend and read post-hoc as a result:
  - **(1) The collector read keys the driver never writes.** `retro_collect` read `d["R1"]`/`d["R2"]`; the
    driver writes **`R1_interface` / `R2_recruitment` / `R3_lys`**. Controlled reproduction through the *real*
    collector: **24 flawless legs → every `e1_plateau_A` None → every leg `technical_failure` → every arm
    underpowered → `tier: INDETERMINATE`.** Corroborated on real artifacts — **19/19 leg JSONs carry
    `R1_interface`, 0/19 carry `R1`**, and two other in-repo consumers read the correct key. **The existing
    tests could not catch it**: they feed the gate `e1_plateau_A` directly, so the driver→collector boundary was
    never crossed. Fixed, with a schema guard that refuses a verdict when legs land, none blow up, and none
    yield an endpoint.
  - **(2) The covalent R2 arm is unbuildable — and it BLOCKS R1 rather than merely costing an arm.** AMENDMENT
    2's finding reproduces on *independent* models: at the preregistered C551, `retro_cov_nr4a1`'s three pinned
    models measure **34.42 / 29.87 / 39.11 Å** against the 8.0 Å limit, so `build_system` **raises**. The raise
    happens *before a leg JSON is written*, so those 6 units never land, **`panel_complete` stays False and §4f
    suppresses the R1 contrast permanently.** The two blockers are **sequential, not alternatives**.
  **Cleared, and verified rather than assumed:** the nm/Å unit error, the positional chain split and the input
  contamination are **NOT** inherited — confirmed on **all 9 models**, including the **6 NR4A2/NR4A3 co-folds no
  prior audit had ever measured** (the earlier allowlist skipped them) which feed **12 of the 18 primary legs**.
  **★ AMENDMENT 3 APPLIED (trimcrae-delegated):** R2 **retired** (authorized panel = **R1 only, 18 legs**); the
  §4d extension window corrected from an unreachable `(0.012, 0.05]` to `(0.05, 0.12]`; the **inert** LOMO
  clause demoted to a reported diagnostic (228,543 configurations reached p ≤ α with correct ordering and
  **zero** then failed LOMO); and an **MDE registered** — measured leg-to-leg σ **0.855 Å**, 80 % power only at
  **1.5–2.0 Å**. Non-rescue: **no result exists to flip**, and defects 1/3/4 all tighten while 2 can only add
  work to already-non-concordant results. **Net, the retrospective can claim LESS than before.**
  ⚠ **And a limitation that is not a bug:** R1's arms are **not matched in ligand placement, with the asymmetry
  running against the hypothesis** — warhead↔target contacts at t=0 are NR4A1 **47** vs NR4A2 **106** / NR4A3
  **73**, i.e. *the spared paralogues start better engaged with their target*, and the designated **pilot leg**
  (`nrv04-descriptive-v4/nr4a2/seed_1`) starts with a **1.05 Å heavy-atom overlap**. A null R1 remains a
  registered outcome, but it licenses *"did not resolve a difference of the size this design can detect"* — **not**
  "selectivity is localised to warhead reactivity", which stands on Leg 0 + Zhang 2018 alone.
  **Price, two different objects wearing one name:** the ~$21 line was **Arm F (alchemical)**, which the prereg
  does not authorise and which is blocked — repriced **~$24 ($5.6–78)**. What a GO would actually spend is
  **Arm E: 18 legs ≈ $7.7** at the measured $0.43/leg.
  *(Original entry retained below for the frozen gate wording.)*
- **`[ ]` NR-V04 retrospective — preregistered holdout** — **~$21 ($4.8–67) · Cum. ~$104.** Full ensembles
  through the pipeline, no tuning, epimer control; report directional concordance only.
  **★ GATE RECONCILED TO THE PREREG, 2026-07-30 (trimcrae go; [Open decisions 12](../../research/manuscripts/nr4a3-program-map.md#open-decisions)) — ARM E
  RUNS, ARM F STAYS BLOCKED.** ⚠ *Superseded, retained: **"Gate: Val B-full + NR-V04 feasibility + Step 1
  fan-out"**, applied to the WHOLE item.* That wording was **this file's, not the prereg's**, and the two had
  disagreed since 2026-07-24: the prereg blocks only **Arm F** (the free-energy arm) on the valB PASS, prices
  **Arm E** (R1, 18 legs — *(count SUPERSEDED by prereg AMENDMENT 4, 2026-07-31: **16 legs** — `nr4a3` co-fold seed 3 excluded by measured input fault)*, ≈$8) inside the standing ≲$50 autonomy threshold, and its **§9 "Dependency honesty"**
  had already argued — before any leg ran — that running Arm E is a *narrowing* rather than a gate jump,
  leaving the judgement explicitly open. **The prereg got there first; this is that judgement being taken**, and
  it is recorded as a dated addition in the prereg itself, amending no criterion. What changed since is only the
  premise: `step1_fanout` **completed** and the feasibility panel was **WITHDRAWN**, so two of the three listed
  gates stopped being pending and became unreachable. **HARD PRECONDITION, met:** the shared driver now persists
  a durable trajectory (`md_analysis_traj.py`) — do not launch 18 legs on a build without it.
  **It no longer gates the causal kill-switch** (lever 4).
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
  **Resume here: [nrv04-retrospective-handoff-2026-07-24.md](../../research/modalities/nrv04-retrospective-handoff-2026-07-24.md)**
  (exact commands, cost ledger, traps) · prereg
  [nr4a3-nrv04-retrospective-prereg.md](../../research/modalities/nr4a3-nrv04-retrospective-prereg.md) · its co-folding
  moved off SageMaker onto the Vast lane
  ([provider-deviation-2026-07-24.md](../../research/compute/provider-deviation-2026-07-24.md)).

### RUNG 5 — mechanism-first prospective ladder *(the flagship, gated mid-ladder by the causal kill-switch)*

- **`[x]` 5a · Orientation-basin search, mechanism-first — DONE 2026-07-25, $0 REALIZED · TIER-2 GO (CATEGORICAL)** — **~$0 realized (budget was $0–50; the optional MM-GBSA rescore was NOT run and is recommended against — it refines the axis mechanism-first demoted) ·
  Cum. ~$129.** Broad transform sampling across the **widened ligandable E3 set** (VHL, CRBN, cIAP1/BIRC2, DCAF1,
  DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2 — free at CPU. **★ RECRUITER STAGING + THE MANDATORY ≤2 DOWNSELECT
  ARE DONE, $0 (2026-07-25): CRBN (9CUO) + VHL (9GIO) advance — VHL as a labelled *backfill*, not a co-winner —
  and the full dropped set is logged with reasons**, none of them availability. Engine
  `e3_recruiter_staging.py` → [`e3-recruiter-staging.json`](../../research/modalities/e3-recruiter-staging.json);
  consumer API `load_advanced()`, whose `anchor_xyz` / `exit_direction` / `caveats` fields are the contract the
  basin search consumes. **The remaining 5a work is the orientation-basin search itself.** Two constraints it
  inherits: the E3-breadth widening **confirmed the incumbents rather than displacing them** (structural
  stageability, not availability, is the binding limit — see item (c) above), and the downselect is **blind to
  recruiter-intrinsic pharmacology**, which is a required input to the next gate). **★ Availability answered $0 and it does NOT constrain the choice** (CI run 30125742542): all 8
  widened arms are broadly expressed and record-complete on HPA (`nr4a3_e3_expression.py`, extendable to any
  further candidate), every symbol resolved through HPA's own search with an exact-match guard — same verdict as
  the original VHL/CRBN check. So the downselect must be made on
  **ligandability + interface geometry**, never on availability, and **no recruiter may be dropped with "not
  expressed" as the reason.** Matched 3-paralogue scoring **over the warhead-pose ensemble**; cluster into ~3–8
  basins/ligase; score with the two **categorical** terms (a) and (b) above, then the cheap counterfactual screen
  to nominate marginal wedges.
- **`[~]` 5a-KS · Wedge confirmation — pilot-first KILL-SWITCH + causal RESULT** — **~$23 ($3.1–97) · Cum. ~$152.**
  ★ **FOUR ternary legs — n = 2 SEEDS PER ARM (trimcrae go, 2026-07-30; [Open decisions 11](../../research/manuscripts/nr4a3-program-map.md#open-decisions)).**
  ⚠ *Superseded, retained: **~$12 ($1.6–45) · Cum. ~$141**, which was the TWO-leg configuration — at one seed
  per arm `S` has no replicate SD and cannot report a null, which is its own pre-registered likely outcome.*
  **`[~]`, not `[ ]`: both ternary legs HAVE run and their checkpoints are durable** (NR4A3 `production/800` of
  2000, NR4A1 `warmup/640` of 1600). They are **PARKED, not finished** — see the IN FLIGHT board for why, and
  for the price condition that re-enables them. `[ ]` would say no work exists; it does, and it is banked.
  **PRIMARY: the ligand-side double difference.** Pilot ONE matched pair first:
  `S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)`, ternary legs only (lever 2), on the lane Val B
  calibrates. ⚠ **"No discrimination ⇒ STOP" is SUPERSEDED — see the Tier-3 semantics box under §The hard
  kill-switch.** `S` is **non-covalent**, so it tests the **marginal** wedge only and is structurally incapable
  of testing the **categorical** mechanism Tier 2 actually passed on. **`S` ≈ 0 ⇒ the marginal wedge is absent
  and the claim rests on the categorical axis alone; STOP only if the categorical axis has ALSO failed.**
  Discrimination ⇒ extend to NR4A2 and to a second design element.

  **★ THE MATCHED PAIR IS DESIGNED (RUNG 5b, 2026-07-25, $0) — 5a-KS is now buildable.**
  **`crbn|M0` at its term-(a) exemplar**, wedge **3-(3-pyridyl)-L-Ala (*d*) vs
  L-Phe (*d₀*)** at **Thr407** — Leu in NR4A1, Val in NR4A2, so the H-bond **donor is removed in BOTH**
  paralogues. Backbone length, chain strain, E3 clearance and heavy-atom count are stated **once**, in the
  §WHERE WE ARE 5b block above ("The pair stands; the shared-LENGTH reading does not"); the mechanical point
  here is only that the clearance keeps the wedge **off the E3 interface**, so the shared **binary and solvent
  legs still cancel exactly** and only **ternary** legs are needed. ⚠ **The wedge pair and the covalent series
  do NOT share one molecule** — the placement hosts both, but the covalent series sits at 14 backbone atoms and
  the wedge pair at 19. ⚠ *The reason this block **originally** gave — "a single chain carrying both needs 16,
  which the segment grid cannot build (LANE 14 delta L14-7)" — is superseded; the measured blocker is the
  one-pendant chain template, and the §WHERE WE ARE 5b block is its one home.*
  *Differs only in the wedge element:* one atom (C–H→N), identical formal charge, heavy-atom count, rotatable
  bonds and (S) centre.
  **A geometry-only pick would have been wrong**, and the preregistered rule that replaced it is worth keeping:
  geometry alone selected I396 (12.6 Å) — but a pyridyl N against **isoleucine** is desolvation with no
  compensation *in any paralogue*, so `S` would have been ≈0 **by construction**. Rule now: **NR4A3 must present
  a donor and both paralogues must not.**
  **Honest expectation, recorded BEFORE the run:** NR4A1 offers *absence*, not a penalty, so the expected effect
  is an **NR4A3 gain bounded by roughly one partly-buried H-bond (~0.5–1.5 kcal/mol)** — an effect that
  **straddles** the resolvable difference now carried in §MECHANISM-FIRST instead of sitting under it, so **a
  null is PLAUSIBLE and, at an adequate replicate count, INFORMATIVE.** ⚠ *The clause that stood here —
  "against 1.12 resolvable — i.e. A NULL IS LIKELY" — quoted a resolvable figure that has since been measured,
  and is superseded ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 53). The pre-registered
  READING of a null is unchanged; only its informativeness moved.* ⚠ **And the replicate count is now the
  binding design question, not the price:** as parked, the lane is **one seed per arm**, at which `S` resolves
  only the TOP of its own expected range — see [§WHAT THE LANDED RESULTS
  CHANGE](../../research/manuscripts/nr4a3-program-map.md#-what-the-landed-results-change-about-the-remaining-plan) 3 and [§Open
  decisions 11](../../research/manuscripts/nr4a3-program-map.md#open-decisions).
  Fallback fully enumerated and RDKit-verified: `vhl|M3` representative, 11 atoms,
  T407, 10.3 Å — **C52H65N9O9S vs C53H66N8O9S** *(per `nr4a3-linker-library-chem.json`; an earlier C₄₇H₅₅N₉O₉S / C₄₈H₅₆N₈O₉S with "66 heavy atoms" disagreed with the artifact and is superseded — the equal-heavy-atom property holds, the formulae were wrong).*
  *Remaining confounds:* modelled rotamer; double conditionality; unmeasured linker-conformer populations. **Evidence grade:** a NO-GO may be taken on
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
  [`Dockerfile.pmxfep`](../../research/compute/Dockerfile.pmxfep),
  [`protfep_pmx.py`](../../research/modalities/protfep_pmx.py),
  [`protfep_run.py`](../../research/modalities/protfep_run.py),
  [`protfep_bench.py`](../../research/modalities/protfep_bench.py),
  [`protfep_reduce.py`](../../research/modalities/protfep_reduce.py),
  [`protfep_refcheck.py`](../../research/modalities/protfep_refcheck.py), `gpu-protfep-vast.yml`; plan in
  [protfep-pmx-plan.md](../../research/modalities/protfep-pmx-plan.md). **Most of the ladder is $0** — stage-test,
  refcheck, bake and a build-test that runs the ENTIRE hybrid construction on a CPU runner; a host is rented only
  once a hybrid demonstrably builds.

  *Known-answer benchmark — PASSED* (full set on Vast, equilibrium λ windows + BAR, scored by `protfep_reduce`
  against SKEMPI 2.0-verified references; artifact
  [`protfep-benchmark-result.json`](../../research/modalities/protfep-benchmark-result.json)):

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
     difference (the best-case resolvable figure lives once, in §MECHANISM-FIRST — this line deliberately does
     not restate it, and the value it **originally** carried is retired there) — exactly where this engine reproduces to ±0.18, not the
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
  (planning layer: [`nr4a3_protein_fep.py`](../../research/modalities/nr4a3_protein_fep.py), whose wedge subtraction
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

- **`[x]` 5b · TWO-MECHANISM REACH — DIAGNOSED 2026-07-30, $0, AND THE ANSWER REFUTES THE QUESTION.**
  Added and closed the same day. The item asked whether a finer segment grid could build one chain carrying
  both the covalent electrophile (→C397) and the causal wedge (→T407). **It cannot, and a finer grid was never
  the issue.** Numbers and the refutation live once, in the §WHERE WE ARE 5b block above; the plan-level
  consequences are here:
  1. **The blocker is the chain TEMPLATE, not the grid** — one `pendant` slot, one branch residue. **That is a
     one-line signature, and it means every sweep over segments and lengths was searching a space that
     structurally cannot contain the answer.**
  2. **A two-branch template is constructible at n = 18 with the segments already in the grid**, so the fix
     costs no new chemistry — but it is a **DESIGN change to a preregistered enumeration**, not a defect fix,
     so it does **not** qualify under the amendment standard that covers a statistic shown to lack
     discriminating power. **It needs an explicit decision, and it is not taken here.**
  3. **The pre-registered NO-GO reading half-fires, and the honest report is the half that did.** It said: *if
     no admissible branch exists either, the limit IS geometric and that is the finding.* One exists in
     principle; what does not exist is a template to hold it. **So the paper's statement is neither "a grid
     limit" nor "geometry" — it is that the enumerated architecture carries one mechanism per molecule**, which
     is a real and reportable constraint on the design as enumerated.
  ⚠ **The existing library is untouched and nothing in it is invalidated** — the diagnostic re-enumerates
  nothing, and a test asserts that.
- **`[x]` 5b · THE TWO-BRANCH TEMPLATE — BUILT 2026-07-30, $0 (trimcrae: *"use your judgement"*). ONE molecule
  CAN carry both mechanisms, there is EXACTLY ONE way to do it, and it is not free.**
  [`linker_twobranch.py`](../../research/modalities/linker_twobranch.py) →
  [`nr4a3-linker-twobranch.json`](../../research/modalities/nr4a3-linker-twobranch.json), 10 tests, RDKit-verified
  **16/16**. **The preregistered enumeration is UNTOUCHED and a test asserts it is byte-identical after a full
  run** — this is a SEPARATE artifact and an additive extension, not an amendment. **It unlocks nothing
  downstream** and no gate, verdict or existing construct changes.
  - **★ THE SOLUTION IS A POINT, NOT A REGION — and that is as much the finding as the molecule.** Scanning
    every (SEG1, SEG2, SEG3, warhead) against the windows the committed library actually recorded, **exactly
    one chain** satisfies both at the same length and placement: **n = 18, term-(a) exemplar, a2–a2–a2, the
    5-amide warhead**, electrophile at **k = 13**, wedge at **k = 6**. Change any one segment and one of the
    two windows breaks. A two-mechanism design here has no room to be optimised.
  - **⚠ AND IT COSTS REAL PROPERTY SPACE — reported because it is the honest half.** Against the committed
    single-mechanism library (same chemistry, same handles): **median +10 heavy atoms and +120 Da**, with the
    top of the set at **1248 Da**, *above the entire committed range* (698–1099). That is well into where
    permeability rather than affinity is the binding problem. **So this is a demonstration that the two
    mechanisms CAN be carried on one chain — NOT a claim that the molecule is developable**, and the paper
    must frame it that way.
  - **Claim ceiling, in the artifact:** *constructible and window-admissible against TRANSFERRED windows*. The
    windows come from **single**-branch records; `branch_position_window` is a function of (endpoints, target,
    length, reach) and **not** of branch count, so the transfer is sound — **but no two-branch chain has had
    its own window computed**, and this may never be reported as though one had. No docked pose, no strain, no
    basin-fidelity filtering, no energetic or selectivity quantity of any kind.
  - **Why building it was the right call rather than scope creep:** $0, additive, and the *existing* filters
    and windows decided the outcome rather than my judgement — I put no thumb on the scale. It converts
    *"unknown because inexpressible"* into a measured answer with a stated cost, which is what the deliverable
    (a candidate set with an identified causal mechanism) needs in order to say whether one molecule can carry
    both. **What it does NOT do is make the 5a-KS matched pair two-mechanism** — `S` must isolate a single
    structural element, so the causal test article stays exactly as designed.
- **`[x]` 5b · Inverse linker design — DONE 2026-07-25, $0 REALIZED (1,995 enumerated → 21 retained, RDKit-verified 21/21)** — **~$0–20 (mostly $0 CPU) · Cum. ~$162.** For each confirmed basin, derive
  linker requirements (endpoint distance, exit-vector dihedral, strain, reach), enumerate a virtual library,
  filter by basin fidelity, annotate exact structures + synthetic feasibility → **~12–20 virtual constructs** (the
  reviewer's "24–36" now bounds this virtual set, not a hand-built grid). For basins carrying the covalent handle,
  the library enumerates the **electrophile position on the linker** as a design variable, and **prefers
  reversible-covalent** chemistry.
- **`[x]` 5b-T · Rebuild the NR4A1/2/3 ternaries by the ASSEMBLY route, from a SMILES-recorded degrader, then
  read them with `V1`** — **$0 · Cum. ~$162 (unchanged).** **Added 2026-08-02.** Serves `R9` → `R10` `R11`;
  runs `V2` (assembly route) then `V1` (descriptor) — **each recovered its own known answer in scope, and
  neither is validated on this system** — and **inherits `R5`, which is unresolved.** ⛔ **This closes the program's largest unpriced gap** — the rebuild was prose only,
  in no rung, no spine row and no decision-value rank, and an item with no rung cannot be scheduled, refused
  or costed.
  **Price, DERIVED not typed — one home:** [`ternary-rebuild-cost.json`](../../research/modalities/ternary-rebuild-cost.json),
  regenerated by [`ternary_rebuild_cost.py`](../../research/modalities/ternary_rebuild_cost.py) and checked by
  `--check` + `tests/test_ternary_rebuild_cost.py`. **It buys 0.0 reference GPU-hours**, so it is $0 at any
  planning rate and **the pinned ladder total does not move**; the rate is read from
  [`vast-ladder-repricing.json`](../../research/modalities/vast-ladder-repricing.json) rather than retyped. The wall-clock
  figure it derives is a **floor**, not an estimate — the per-arm seconds come from a bromodomain+VCB system
  and this one is larger.
  **What runs:** DeepTernary at the frozen commit, patched to CPU at 16 seeds, over **5 arms** — two harness
  positive controls (6HAX VHL, **and 6BN7 CRBN, because this rung's E3 is CRBN and a VHL-only control does
  not cover it**; both are inside the model's data horizon and so control the harness and never
  generalisation) and the three paralogue arms — then `nr4a_ternary_signature.py` over **all 16 models per
  arm**. Inputs, artifacts and the pre-flight snap-mask assertion that stops the empty-mask failure two dead
  runs already paid for: the `spec` block of the cost artifact.
  ⛔ **The degrader's SMILES is recorded this time.** It is taken from
  [`nr4a3-linker-library-chem.json`](../../research/modalities/nr4a3-linker-library-chem.json), which carries a
  `canonical_smiles` and an `inchikey` per construct. The existing ternaries are unusable as evidence for
  exactly this reason: their molecule cannot be recovered from any of the three models, so no replicate can
  ever be matched to them.
  **GO/NO-GO — PRE-REGISTERED, three arms, all three needed. Full criteria and their nulls: the `gate` block
  of the cost artifact.** **(A)** at least one discriminating position whose **aligned residue itself
  differs** in both comparators — same-residue positions are placement artifacts and count for nothing, which
  is what five of the earlier six were. **(B)** that position present in **≥12 of 16** models (`C17`; floor `C18`) on the NR4A3 arm
  and **≤4 of 16** on **each** comparator; under a per-model coin-flip null each tail is one-sided binomial
  *p* = 0.0384. Anything between is **INDETERMINATE**, a third outcome and not a pass. **(C)** the assembled
  ternary must **preserve the tether geometry the categorical axis depends on** — a ternary that only
  assembles by lengthening the effective tether past the paralogue-collision knee has traded away the
  property it exists to exploit, and that is **NO-GO, not a caveat**. ⚠ **Arm (C) is registered as AT RISK
  before the rung runs:** no committed construct sits at or below 12 backbone atoms (the shortest is 14), and
  the only CRBN basin in the confirmed set misses the 12-atom gate by construction. A $0 RDKit re-enumeration
  is the named way out; if it returns nothing buildable the rung runs at the shortest committed length and
  **carries the measured collision bracket** instead of claiming the 12-atom figure.
  ✅ **THE NAMED WAY OUT WAS TAKEN, 2026-08-03, AND IT ANSWERS ARM (C) PARTLY IN THIS RUNG'S FAVOUR AND PARTLY
  AGAINST IT** ([`nr4a3-short-linker-probe.json`](../../research/modalities/nr4a3-short-linker-probe.json)). **(i)** The
  premise *"nothing exists at 12"* is false — a construct exists, is named, has a SMILES and an InChIKey, and
  clears the gate under both reach conventions; the library's floor of 14 turned out to be a basin-**breadth
  policy** rather than geometry or chemistry ([§8 Route B](../../research/manuscripts/nr4a3-program-map.md#route-b--a-linker-borne-covalent-handle-at-an-nr4a3-unique-cysteine---blocked-on-r5-nothing-running--serves-r8-r15)).
  ⛔ **(ii) But it is a VHL construct and THIS RUNG'S E3 IS CRBN.** The best CRBN construct at the gate reaches
  C397 **through-space only**; under the corridor convention its floor is **14**, above the gate. ⛔ **That is `C9`,
  ⚠ CONTESTED — two frozen conventions that disagree, and quoting whichever one passes would be choosing the
  convention on the outcome** ([§3b.2](../../research/manuscripts/nr4a3-program-map.md#3b2--contested-and-known-defective--the-four-that-are-not-merely-frozen)). So arm (C)
  stays AT RISK for CRBN, and the fallback stands as written — run at the shortest committed length and carry
  the measured bracket. ⛔ **(iii) And before either, the SMILES provenance has to be settled:** this rung
  takes its degrader from `nr4a3-linker-library-chem.json`, which is generated from
  `nr4a3-linker-design.json`, **which no longer reproduces from its own generator** —
  [§10.1 row 25](../../research/manuscripts/nr4a3-program-map.md#101--open-rows-ordered-by-what-unblocks-the-most). That is a $0 decision and it belongs
  *before* the run, not after it.
  **Refusals, not results:** an empty snap mask or an infeasible embed is **REFUSED**, never reported as a
  zero; a failed positive control makes the whole run uninterpretable; fewer than 3 models on any arm and no
  reproducibility statement is made in either direction.
  ⛔ **Scope, up front:** this yields **structural** evidence — *these modelled interface contacts differ
  between paralogues* — and never thermodynamic. It computes no free energy, so it cannot say anything binds
  more tightly, and it does **not** discharge `R12` or the free-energy requirement. `V1` recovered one contact
  in one pair and no more; `V2`'s post-horizon pass is one arm on a VHL/bromodomain system, and nothing at all
  covers a CRBN ternary with a nuclear receptor, which is what this rung assembles; every model here is an
  isolated LBD, so `R13` is untouched.
- **`[ ]` 5c · Explicit ternary-ensemble refinement** — **~$21 ($1.9–85; endpoint MD, 24–~200 legs at ~1.38 ref
  GPU-h each) · Cum. ~$183.** *(The biggest swing item — the leg COUNT, not the rate, dominates its uncertainty.)*
  Replicated ternary + full CRL/E2~Ub MD across target states, linker conformers, and in-basin poses; matched
  NR4A1/2/3; separate accessibility from stability; robust constraint-satisfaction filtering → **~4–8 constructs**
  nondominated under scenario + model uncertainty. Add a constraint: **which lysine the ubiquitin actually
  reaches**, reported per construct as a distribution over unique-vs-conserved sites, not just "a lysine is near".
- **`[ ]` 5d · Local ternary FEP** — **~$21 ($3.1–87; 3–6 ternary comparisons) · Cum. ~$169.** Alchemy **only**
  within a retained basin (both endpoints plausibly bound, modest congeneric change). Refines the matched final
  series → **~6–12** with ≥2 mechanistic wedges, ≥2 linker architectures, VHL/CRBN only where both survive,
  explicit negative controls. **Deliverable** = the prioritized, structure-defined, retrosynthetically annotated
  candidate set with an identified causal selectivity mechanism — degradation experimentally unvalidated.

### RUNG S — the two SCOPE rungs (`R13`, `R14`): claim-ceiling conditions, deliberately OFF the `Cum.` chain

*★ **Added 2026-08-03, closing [§10.1](../../research/manuscripts/nr4a3-program-map.md#101--open-rows-ordered-by-what-unblocks-the-most) rows 9 and 10** — two of the five rows that had **no rung, no gate and no price anywhere in the program.** ⛔ **All four items below are EXCLUDED from the pinned ladder total**, in exactly the way [pricing.md §C](../../research/compute/pricing.md) excludes the 5a-KS confirmatory wedge and the reciprocal mutation cycle: they are **claim-ceiling conditions**, not steps of the gated 5a→5d spine, and **no rung's GO gates them.** So each carries a **Price** and deliberately **no `Cum.`** — folding them into the chain would silently move a total `vast_cost_model.py` derives. Every figure here is **DERIVED, never typed**, and its one home is [`scope-rung-cost.json`](../../research/modalities/scope-rung-cost.json) (`python3 research/modalities/scope_rung_cost.py --check`), priced off the **live** market rate in [`vast-ladder-repricing.json`](../../research/modalities/vast-ladder-repricing.json) so these rungs move with the ladder instead of freezing a rate.*

- **`[x]` `R13-a` · Fusion-junction SEQUENCE inventory, at the CORRECTED junction — RAN 2026-08-03, $0, gate REPRODUCED** — **$0 (0.0 ref-GPU-h) · needs no nod · CI/CPU.** Serves `R13`. Extend the uniqueness + lysine/cysteine sweep **across the junction** and state explicitly which real residues the modelled LBD construct (373–626) excludes from every geometry claim in the program. ⚠ **Price the CORRECTED object, never the old one:** the exon→residue map was re-derived on 2026-08-03 and NR4A3's first two *transcript* exons are non-coding, so all **7** previously committed junctions deleted the AF1 **and** the first zinc finger of the C4 DBD; the corrected canonical junction is **EWSR1 exon 7 ending at residue 264 :: NR4A3 exon 3 beginning at residue 1** ([`nr4a3-exon-audit.json`](../../research/modalities/nr4a3-exon-audit.json); the guard that makes a repeat loud is `fusion_breakpoints.resume_offset`, which now **raises** on a non-coding exon instead of sliding to a neighbour). **GATE:** a re-derivation that does **not** reproduce `EWSR1(1-264)::NR4A3(1-626)` from exon structure alone is a REFUSAL, not a result. ⛔ It settles **scope, not geometry** — the deliverable is one sentence the paper currently cannot write, plus the confirmation that **C166** is present in the disease protein and absent from every structure here.
- **`[ ]` `R13-b` · Apo co-fold of the two corrected fusion constructs** — **~$0.66 ($0.28–1.67; 5.81 ref-GPU-h, 12 models = 2 constructs × 6 seeds) · 🔒 needs a nod · Vast, baked image.** Serves `R13`. The `seam` and `composite` constructs of [`fusion_cofold.py`](../../research/modalities/fusion_cofold.py), re-cut to the corrected junction. **Basis is MEASURED, not estimated:** the one completed co-fold panel in this repo billed **5.808 ref-GPU-h / $1.0723 over 8 rentals, all on the reference card, for 12 models** ([`selcal-price-ledger.json`](../../research/modalities/selcal-price-ledger.json) → `scope-rung-cost.json` `bases.cofold_per_model`), and that basis is an **upper bound twice over** — its system is *larger* (~570 residues vs 380/486, and the co-fold cost is ~N²), and its hours include an environment build on the billing host that [CLAUDE.md §6](../../CLAUDE.md) has since forbidden. **`$/ns` = `—`, and that is an honest refusal, not a missing field:** a co-fold integrates no dynamics, so there is no ns denominator (`inflight_board.unpriceable_usd_cell`); this rung is gated on its **dollar** ceiling alone and a refusal must say which ceiling it hit. **PRE-REGISTERED GATE, written before the run because a null here is the expected outcome:** `fusion_cofold.py`'s own prior is that the EWSR1 side is a prion-like IDR (mean pLDDT 38.8, 98 % of residues < 50) with **no cross-seam coevolution** for an MSA-based predictor to use — so **absence of an ordered composite interface is a FEASIBILITY READ, not evidence that no pocket can form**, and it may not be reported as a refutation. A GO is: an interface cavity present in **≥4 of 6 seeds** on the `composite` construct that is **absent from both parent AlphaFold models** — anything less is INDETERMINATE, a third outcome.
- **`[x]` `R14-a` · Complete the anti-target panel, and run the self-control it has never run — RAN 2026-08-03, $0** — **$0 (0.0 ref-GPU-h) · needs no nod · CI/CPU (smina, the identical 24 Å box / exhaustiveness 8).** Serves `R14`. ⚠ **This is an ASSEMBLY job, not a build:** the 47-receptor sequence screen has run and flagged exactly **NR3C2 (MR)** and **AR**, the docking harness has run at panel scale (SI §S1), **AR is already a panel target**, and `denovo_401` is already staged. What is missing is that **MR/NR3C2 is not in [`antitarget_panel.json`](../../research/modalities/antitarget_panel.json)** (a data row; `antitarget_prep.py` **drops** a target whose ligand/chain cannot be resolved, loudly, so a bad PDB pick fails rather than emits a bad receptor) and that the panel has a cognate-ligand self-control **which has now RUN (2026-08-03, $0): the self-control **FAILS on CYP3A4, PPARG, PXR**, so no anti-target margin from this panel may be read — including SI §S1's** ([`antitarget-selfcontrol.json`](../../research/modalities/antitarget-selfcontrol.json)). **GATE, and it is ordered deliberately:** the self-control runs **FIRST** — each target's own cognate ligand re-docked through the identical protocol — and **until it passes, no anti-target margin from this panel may be read, including the one already published in SI §S1.** ⭑ That is what makes this the higher-value half: a failure would reach a result the paper already carries.
- **`[ ]` `R14-a2` · REPAIR the anti-target receptor PREPARATION, then re-run the self-control** — **$0 (0.0 ref-GPU-h) · needs no nod · CI/CPU.** Serves `R14`. ⭑ **Created 2026-08-03 because `R14-a` closed with a FAIL and the work it created must not close with it.** 3 of 10 receptors do not recover their own cognate ligand, so `panel_readable: false` and four SI §S1 clauses are unreadable ([`antitarget-selfcontrol.json`](../../research/modalities/antitarget-selfcontrol.json); instrument row [`V21`](../../research/manuscripts/nr4a3-program-map.md#31--the-instrument-table)). **GATE — fix the PREPARATION, never the criterion:** the frozen rule is that a failing target **may not be dropped**, its box **may not be re-centred**, and **no band may be lowered**; the panel's own stated limit is that its receptors are protein-only by construction, so any cofactor-dependent binding mode is outside what it can model today. ⛔ **A pass here still does not restore the published margins on its own** — the NR4A3 ΔG column they subtract is **not committed anywhere in this repo**, which is a separate, independent block (`flagged.margin_refusal`).
- **`[ ]` `R14-b` · Matched AR/MR cryptic-pocket ensembles (+ the $0 detector)** — **~$3.41 ($1.10–18.65; 29.87 ref-GPU-h, band 23.2–64.7) · 🔒 needs a nod · ⛔ AND CURRENTLY BLOCKED BY THE RATE LINE — see the gate.** Serves `R14`. The SI's *second* requirement: 2 species × (60 ns well-tempered metadynamics + 3 × 5 ns release), the workflow's own declared recipe, then the harmonized detector — which is **$0 CPU once frames exist**, the same $0 re-read that `paralogue-pocket-contrast.json` already performed on the paralogues. **⚠ Its dominant uncertainty is GPU-HOURS, not $/hr:** the measured host spread on this exact workload is **3.1× (146 → 47 ns/day)** and is **host-CPU-bound**, because PLUMED does per-step host-side work — caught on one instance jumping 24–33 % → 74 % `gpu_util` at the metad→release boundary, same card, minutes apart ([pricing.md §A.1](../../research/compute/pricing.md)). So host CPU must enter selection for this rung. **⛔ REGISTERED GATE 1 — DO NOT LAUNCH:** its derived `$0.022758/ns` is **6.67× the ladder basis and 3.48× the approved buy line**, i.e. a row the standing gate **refuses**. ⚠ **That is NOT a drift finding and must not be quoted as one** — the line's basis is the 84,534-particle *unbiased* RBFE benchmark and this is a *biased* leg, so the two `$/ns` have different denominators. **There is no metadynamics-anchored basis in this repo, and until one exists this rung cannot be graded by the rate line at all.** Surfaced now rather than discovered at launch; it is a decision for trimcrae, not a rule to loosen. **⛔ REGISTERED GATE 2 — a $0 precheck that can refuse the spend on evidence, exactly like [§10.1 row 12](../../research/manuscripts/nr4a3-program-map.md#101--open-rows-ordered-by-what-unblocks-the-most)'s did:** the CV is the Rg of **NR4A3's** ten Pocket-5 lining residues, mapped onto the target by BLOSUM62 at runtime. That ran on the paralogues at overall identity **0.51 / 0.58**; **AR and MR sit at ~0.32**, only marginally above the SI's own confidence floor, and the SI itself warns that *"a distant global alignment can mis-register a two-residue run"*. If the aligner does not map all ten CV residues at a stated confidence, **R14-b is REFUSED and $0 is spent.**
- **`[x]` `R14-c` · The ENERGETIC (FEP) half — RULED OUT OF THIS RUNG, on the claim-ceiling rule** — **$0 (a decision).** The SI asks for *"docking/FEP into their LBDs"*. The FEP half **is `V4`'s instrument** — the selectivity ABFE that has never recovered a known selectivity answer across two pockets — so under [§2.3](../../research/manuscripts/nr4a3-program-map.md#23--the-claim-ceiling-rule-stated-so-it-can-be-checked) a number from it could not raise `R14` above *unvalidated prediction*. Pricing it here would create a **second home** for a decision that already has one: [§10.1 row 2](../../research/manuscripts/nr4a3-program-map.md#101--open-rows-ordered-by-what-unblocks-the-most), `V4`'s missing rung. **It is downstream of row 2, not parallel to it**, and that is why this rung is closed rather than costed.

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

## 11 · Money, authorization and gates

*Navigation, not content. Every figure below has exactly one home and this section states none of them.*

**The four spending rules are immediately below, in [§Spending rules](../../research/manuscripts/nr4a3-program-map.md#spending-rules)** — no
pre-authorization · spend-gated, cheapest-decisive-first · GO/NO-GO after every priced rung · a step whose
engine has no completed benchmark leg is **PROJECTED** and excluded from the pinned total. ⭑ That last rule
is why [§10](../../research/manuscripts/nr4a3-program-map.md#10--the-roadmap--one-ordered-list)'s price column distinguishes *priced* from *PROJECTED* from
*unpriced*, and why an honest **unpriced** beats a plausible figure. ⚠ **Superseded, retained:** this section
used to restate all four rules in full, which was a second copy of a fact with one home — legitimate while
the rules lived in another file, a rule-1 violation the moment the merge put them on this page.

**Where the numbers live** — and per invariant 6 this section holds none of them:

| | one home |
|---|---|
| the pinned ladder total and its derivation | [§Spend summary](../../research/manuscripts/nr4a3-program-map.md#spend-summary), regenerated by `vast_cost_model.py` and CI-checked against [`vast-ladder-repricing.json`](../../research/modalities/vast-ladder-repricing.json) |
| per-rung authorisation and cumulative cost | [§Dependency spine](../../research/manuscripts/nr4a3-program-map.md#dependency-spine) |
| per-item price and gate | [§THE ORDERED PLAN](../../research/manuscripts/nr4a3-program-map.md#the-ordered-plan-spend-gated--read-top-to-bottom-for-whats-next) |
| the cost evidence behind every rate | [pricing.md](../../research/compute/pricing.md) · [bid-strategy.md](../../research/compute/bid-strategy.md) |
| realised spend | [`realised-spend.json`](../../research/modalities/realised-spend.json), summed from each lane's own rental ledger — a **floor**, with an attested block the machine ledgers cannot see |
| the buy line (`$/ns`) | [`inflight_usd_per_ns.APPROVED_USD_PER_NS`](../../research/modalities/inflight_usd_per_ns.py) — **the drift line IS the buy line**; a row that prints `⚠ DRIFT` is a row we do not buy |
| live in-flight state | [`inflight_usd_per_ns.py`](../../research/modalities/inflight_usd_per_ns.py) / `inflight-board-all.md` — ⚠ **not** the [⏱️ IN FLIGHT](../../research/manuscripts/nr4a3-program-map.md#in-flight-superseded) block on this page, which is superseded ([§12](../../research/manuscripts/nr4a3-program-map.md#12--findings-that-belong-to-other-documents) finding 6) |

⚠ **Two ledgers, never summed.** GCP trial credit buys wall clock, not headroom; it is tracked separately from
realised and ladder spend.

⚠ **The dependency spine is a SPEND graph, not this page's claim graph.** Its edges are authorisations; the
edges in [§4](../../research/manuscripts/nr4a3-program-map.md#4--the-dependency-graph) are entailments. They must never be merged — collapsing them loses
either the money or the epistemics.

⚠ **The plan's cumulative chain is non-monotonic and this page does not repair it**: it steps
$109 → $107 → $104 across the three RUNG-4 entries and $162 → $183 → $169 across 5b → 5c → 5d. The CI subset
check verifies that the spine's cumulative values are a *subset* of the plan's; it does **not** check the
plan's own ordering. Recorded in [§12](../../research/manuscripts/nr4a3-program-map.md#12--findings-that-belong-to-other-documents).

---

## Spending rules

*★ **THE ONE HOME** for the four spending rules. Zero history. [§11](../../research/manuscripts/nr4a3-program-map.md#11--money-authorization-and-gates) links here and restates nothing. Rule 4 is why [§10](../../research/manuscripts/nr4a3-program-map.md#10--the-roadmap--one-ordered-list)'s price column distinguishes priced / PROJECTED / **unpriced**.*

1. **No pre-authorization, no pre-staging.** Nothing is ever queued to auto-fire. Every GPU run is presented at
   its gate with (a) the prior step's result, (b) a pinned cost (from realized GPU-h, not a guess), and (c) a wait
   for an explicit trimcrae "go." Only $0 CPU/CI work runs without a nod.
2. **Spend-gated ladder, cheapest-decisive-first.** The cheapest run that could kill the paper comes first; each
   rung's bigger spend unlocks only if the previous, cheaper rung looks promising. Never pay for an expensive
   stage on a hypothesis a cheap stage could have falsified.
3. **GO/NO-GO after every priced rung.** Each rung ends with an explicit test; NO-GO = stop or pivot.
4. **Every step is priced bottom-up per edge** on the Vast-4090 bases below; provenance in
   [pricing.md](../../research/compute/pricing.md). A step whose engine has no completed benchmark leg is carried as
   **PROJECTED and excluded from the pinned total**, never at a fake number.

## GPU economics (full provenance in [pricing.md](../../research/compute/pricing.md))

*★ **LARGELY A POINTER**, deliberately: the throughput table's home is `vast_cost_model.MEASURED_NS_PER_DAY_84K`, the bid rule's is `bid-strategy.md §7`, the per-edge bases' is [pricing.md](../../research/compute/pricing.md). What genuinely lives here is the **six cost levers**, which are ratios and survive any reprice.*

**All production runs go on Vast.** GCP L4 / SageMaker / Modal are not the go-forward basis. **The card is not
the decision — the OFFER is.** Rank live offers by all-in **`$/ns`** (bid + storage ÷ measured throughput) and
take whatever wins; the top 10 routinely contain both 4090s and 3090s. Measured throughput @84,534 particles is
**4090 804.06 / 4080 693.35 / 3090 460.91 ns/day** (4090/3090 = **1.745×**) — table of record
`vast_cost_model.MEASURED_NS_PER_DAY_84K`, re-anchored 2026-07-27 onto a median over N≥3 independent hosts
(pricing.md → Appendix T). The cheapest 3090 floor was **$0.0147/hr** against **$0.1310** for the cheapest 4090
— an **8.8×** price spread that more than covers the throughput gap. VRAM is never the constraint (≥24 GB is
ample). A 3090 does need **1.745×** the wall clock, so a leg with a hard continuity requirement is
proportionally more exposed on it — scaled and flagged per card, not ignored.
*(Superseded, retained: the single-host figures **4090 755.36 / 4080 703.51 / 3090 359.36** and the
**2.10×** ratio derived from them. Appendix T says what retired them.)*

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
  [bid-strategy.md](../../research/compute/bid-strategy.md). `VAST_BID_FLOOR_MULT` survives only as an unset escape
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
| **Endpoint-MD leg** (~466k atoms) | **~$0.19**, ~1.38 ref GPU-h | Backed out of the **completed** 18-leg NR-V04 covalent panel: ~$0.43/leg realized on a 3090 at ~$0.10–0.21/hr ÷ the card ratio *(computed with the then-current **2.102×**, superseded 2026-07-27 — pricing.md Appendix T; the conversion is due a refresh at the next reprice)*. The one basis resting on a completed multi-leg ledger; the 4090 conversion itself is inferred |

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

### Cost levers adopted 2026-07-24 ([evidence](../../research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md))

1. **~~4 fs ternary production ≈ 2× cheaper per leg.~~ ⚠ CORRECTED 2026-07-25 — the saving is **1.56×**, not
   2×, and the leg is **2800 iterations**, not 2400. Both verified against `rbfe_spot_driver` source, both pure
   arithmetic on the existing measured rate.**
   - **Why not 2×:** halving the timestep halves the force evaluations only in the phase whose dt *changed*.
     The warmup is pinned at **1 fs either way**. Per replica: 2 fs = 1.0e6 (warmup) + 2.5e6 (production)
     = **3.5e6 steps**; 4 fs = 1.0e6 + 1.25e6 = **2.25e6**. Ratio **0.643×** ⇒ a **1.56×** saving. The old
     "2×" overstated it by ~36 %.
   - **Why 2800, not 2400:** "400 equil + 2000 production at 2.5 ps/iter" assumes the warmup runs at the
     *production* timestep. It does not — `_iters_from_time` derives warmup iterations from the **WARMUP**
     integrator, and the source comment says so outright (*"more iters at a smaller dt"*). At the as-run
     `warmup_timestep_fs=1.0`, 1 ns of equilibration is 1e6 steps ÷ 1250 steps-per-iteration = **800**
     iterations, each costing the **same 1250 force evaluations** as a production iteration. So the as-run 2 fs
     leg is **2800 equal-cost iterations**, and pricing it at 2400 understated **every 2 fs ternary stage by
     ~17 %**.
   - **⚠ The claim "iterations are timestep-independent (2.5 ps/iter)" is FALSE and is retired.** Iterations are
     `steps ÷ steps_per_iteration`, and steps depend on dt; 2.5 ps/iter holds only *at 2 fs*. **Price in STEPS,
     not iterations** — iteration counts are not comparable across protocols.
   - Net effect on the edge: **~$8.8 → ~$10.2 at 2 fs**, and the 4 fs edge is **~$6.6, not ~$4.4**.
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
3. **~~Sequential (anytime-valid) stopping instead of a fixed 3 replicas — ~20–25 %.~~ ⚠ REFUTED BY MEASUREMENT
   2026-07-25 — it saves ~0.8–2.6 % on THIS ladder, and should NOT be wired.** `adaptive_certify.py` /
   `adaptive_allocator.py` are built and unit-tested but were never wired to the ternary ladder, and the
   ~20–25 % was an allocation-design figure that was never checked against this ladder's actual shape. Measured
   as a futility stop (`valb_rescope_design.py`): at σ = 0.5 it stops after **4.87 of 5** replicates (**2.6 %**);
   at σ = 0.7, **4.96 of 5** (**0.8 %**). **Mechanism, not a fitting artifact:** an anytime-valid bound must be
   wide enough to remain valid under *every* stopping time, so at n = 2–4 with σ ≈ 0.7 it is simply never tight
   enough to fire. The saving is real for long horizons; **a 5-replicate ladder is too short to pay for it.**
   Do not carry the 20–25 % in any total.
4. **Free gates lead.** `selectivity_wedge_confirm` depended on `valB_full` + `nrv04_retrospective` (~$43) even
   though its validation need is matched-pair, not cooperativity-cube. Decoupled.
5. **Ligand-side double difference replaces the protein-mutation campaign** as the primary causal test — which
   at the time had no engine at all, and still has no NR4A-scale rate.
6. **E3 breadth is free at search, capped before GPU** (≤2 recruiters, dropped set logged).

*Operational Vast setup — image `triskit23/nr4a3fep:latest` (openfe ≥1.12 + ambertools + lomap/kartograf +
OpenMM pinned to CUDA 12.6), the `probe_offers` / `bench` / `firm` tooling in
[`nrv04_vast_launch.py`](../../research/modalities/nrv04_vast_launch.py), and the bid/ranking code of record in
[`gpu_backend.py`](../../research/modalities/gpu_backend.py) + `vast_cost_model.recommended_bid` — is documented in
[pricing.md §E](../../research/compute/pricing.md); not repeated here. The hourly read-only price sampler is
`.github/workflows/vast-price-sample.yml`.*

---

## Spend summary

*★ **THE SPEND LADDER'S ARITHMETIC.** The pinned total is **DERIVED** (`vast_cost_model.py` → [`vast-ladder-repricing.json`](../../research/modalities/vast-ladder-repricing.json)) and `lint_consistency.check_derivations` fails the build if this file, [pricing.md](../../research/compute/pricing.md) or [bid-strategy.md](../../research/compute/bid-strategy.md) drifts from it. Never hand-carry it.*

**PINNED TOTAL: ~$169 mid-range (~$46–626)**, GO at every gate, priceable stages only.
*(Superseded, retained: **~$158 mid (~$44–578)** — retired 2026-07-30 when RUNG 5a-KS went from **2 ternary legs
to 4** (n = 2 seeds per arm; [Open decisions 11](../../research/manuscripts/nr4a3-program-map.md#open-decisions)). ⚠ **That reprice is the cleanest in this
file's history and it is worth saying why: the market snapshot, the `$/reference-GPU-hour` rate and every other
stage's GPU-hours are BYTE-IDENTICAL across it**, so the entire **+$11 mid** is the second seed per arm and
nothing else — the opposite of the 2026-07-27 reprice, where no price moved and only the yardstick did. And
that earlier one is retained too: **~$185 mid (~$51–614)**, retired 2026-07-27 when the throughput table was
re-anchored; the GPU-hours did not change, the `$/reference-GPU-hour` did. pricing.md Appendix T.)*

**How it is built** — regenerate the alchemical/MD stages with
`python research/modalities/vast_cost_model.py --json-out vast-ladder-repricing.json`
(JSON: [`vast-ladder-repricing.json`](../../research/modalities/vast-ladder-repricing.json)); the tool prices 9 stages
at **$149.63 ($36.58–531.46)** at the committed snapshot's **$0.1143/ref-GPU-h**. The ladder figure adds the
stages the tool does not cover, at the **[low, mid, high] the machine registry uses** — step0 ~$1–2 (mid
**$1.5**), valA_mini ~$0–15 (mid **$0**, its *realized* cost on GCP credit rather than the band's midpoint), the
~$8 measured covalent panel, 5a basin ~$0–50 (mid **$0**, realized), 5b linker ~$0–20 (mid **$10**):
`149.63 + 1.5 + 0 + 8 + 0 + 10 ≈ 169`; low `36.58 + 1 + 0 + 8 + 0 + 0 ≈ 46`; high
`531.46 + 2 + 15 + 8 + 50 + 20 ≈ 626`. [pricing.md §C](../../research/compute/pricing.md) and
[bid-strategy.md §6](../../research/compute/bid-strategy.md) carry the same total — all three must agree, and
[`lint_consistency.py`](../../research/manuscripts/lint_consistency.py) recomputes it from
[`pinned-figures.json`](../../research/manuscripts/pinned-figures.json) → `derivations.ladder_total` rather than
trusting any of them.

⚠ **TWO THINGS THIS PARAGRAPH GOT WRONG UNTIL 2026-07-30, both found by regenerating rather than reading.**
**(a)** It stated the 5a basin stage at **mid $25** while the machine registry has always used **$0** — so its
own printed arithmetic came out at **`≈ 194`** — *superseded, retained* — beside a pinned total of `~$158`, and the sentence that followed
asserted the chain *"ends on the same ~$158"*. A doc contradicting itself inside four lines, which is precisely
what rule 1 exists to catch; the registry was right and the prose was wrong. **(b)** The tool figures quoted
here (**$149.4 at $0.137/ref-GPU-h**) were from an older market snapshot than the committed artifact, which
carried **$138.16 at $0.1143**. ⚠ **Beware a near-collision when reading old copies of this file: the tool total
is NOW $149.63, which is within $0.25 of the stale $149.4 it replaces, and the two have nothing to do with each
other** — the old one was 2 legs at a higher rate, the new one is 4 legs at a lower one.

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
**none of this weakens the mechanism-first case** — but ⚠ **one of the two arguments that used to carry it has
been retired by measurement and must not be re-quoted.** The *precision* argument — *"spending on an axis
needing ~2.0 kcal/mol when the method resolves 1.12 is a bad trade at any price"* — **no longer holds**, because
the resolvable difference was assumed and is now measured (§MECHANISM-FIRST; [Appendix
A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 53). **Two arguments survive intact and they are
sufficient on their own:** (i) a **categorical** handle needs *no* margin at all, so it is not competing with
the marginal axis for resolution; and (ii) the categorical screens are **$0 CPU** and therefore dominate on
cost at any noise floor. What the correction does change is the marginal axis's **rank**, not its **order** —
it is worth confirming, and §MECHANISM-FIRST says on what condition.

| Rung | GPU work | Step $ (low–high) | Cum. (mid) |
|---|---|---|---|
| 0 · infra + free CPU (DONE) | step0 + emc_e3 + pocket | ~$1–2 | ~$2 |
| 1 · Val A smoke (DONE, realized ~$0 on GCP credit) | 1 public RBFE edge | ~$0–15 | ~$2 |
| 2 · pilot (DONE) + Val B-mini | 1–2 RBFE edges + 1 ternary edge | ~$2.8 + ~$8.8 (range $4–31) | ~$13 |
| **2b · 4 fs adoption + matched re-calibration** | 1 ternary edge @4 fs | **~$4.4** ($1.6–11) | ~$17 |
| 3 · Val B cube (SMARCA2/4 module) + NR-V04 feas. (DONE) | 2–3 ternary edges + CRL-MD; covalent panel | ~$22.5 + ~$8 (range $14–75) | ~$48 |
| 4 · fan-out + atlas + **unique-residue map** (both $0) + NR-V04 retro | ≈19 RBFE edges + NR4A1/2/3 ternary **legs** | **~$36** + ~$21 (range $20–147) | ~$104 |
| 5a · mechanism-first basin search + **KILL-SWITCH** | basin ($0–50, multi-E3, CPU) + ligand-side double difference, **4 ternary legs (n = 2 seeds × 2 arms)** | ~$0–50 + **~$23** ($3.1–97) | ~$152 |
| 5 (if GO) · linker + ensemble refine + local FEP | inverse-linker ($0–20) + ensemble MD (~$18) + within-basin FEP (~$21) | ~$49 (range $5–187) | ~$169 |
| Confirmatory protein-mutation cycle (optional) | 1–3 mutation directions | **~$4.6 PROJECTED** | *(excl.)* |
| Optional ΔG_open / ABFE (HELD) | — | +$200–500 | *(excl.)* |

Notes: the restructuring buys **causal evidence** (matched-pair cycles + ensemble MD + local FEP) over
co-fold-and-score — higher information per dollar, not lower. A non-viable paper still dies for ~$2 at Val A, or
**free** at the Tier-0 unique-residue map and the atlas (both passed). The *expected* cost is lower than the
totals suggest, because the leading gates are now $0.

## Dependency spine

*★ **THE AUTHORISATION GRAPH.** ⚠ **This is a SPEND graph: its edges are authorisations, not entailments.** [§4](../../research/manuscripts/nr4a3-program-map.md#4--the-dependency-graph)'s graph is the claim graph, and the two must never be merged — collapsing them loses either the money or the epistemics. ⚠ Its cumulative notation (`Cum ~$N`) is **deliberately distinct** from the plan's (`Cum. ~$N`) and `lint_consistency.check_subsets` raises an ERROR if the two are unified.*

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
       inverse_linker($0) ──► ternary_ensemble_refine ──► local_ternary_fep         (Cum ~$169)
          │
RUNG6  fold ──► redteam ──► post/submit                                             ($0)

OPTIONAL/HELD (explicit nod only): dg_open_paralogue, abfe_conditional (incl. the λ-repair)
```

## Current front

*★ **SUPERSEDED BY [§10](../../research/manuscripts/nr4a3-program-map.md#10--the-roadmap--one-ordered-list), retained for one statement.** ⚠ This section has **zero** inbound references and names its own homes for everything it says. The one thing it owns is the sharpest statement of the feasibility panel's status — **WITHDRAWN**, not merely "under correction" — which contradicts the ordered plan's `[!]` marker and the schedule JSON, and is recorded as [§12 finding 12](../../research/manuscripts/nr4a3-program-map.md#12--findings-that-belong-to-other-documents).*

Rungs 0–1 are done. The Tier-0 unique-residue map and the differential atlas are done ($0, both PASS). The
NR-V04 covalent feasibility panel is **WITHDRAWN** — not merely "under correction". Its GO was never
produced by the frozen scoring rule, its inputs were contaminated, and no trajectory survives to re-derive from,
so its re-run is **`[HELD]`** pending a prereg amendment. It gates nothing.

**NOTHING IS BILLING.** All three lanes that were running closed on 2026-07-30 — the **Step 1 fan-out** (19
congeneric RBFE edges), the **valB_mini replicates** (4 legs) and the **closure triangle**, whose `R` landed at
5:11 PM ET and was the last owed GPU work in the fixed scope. **Two lanes remain held, deliberately and for
stated reasons**: RUNG **5a-KS** behind the relaunch price gate, and the **restrained binary re-run** behind
the triangle's `R` — which has now landed, so what that leg is waiting on is a *reading*, not a run. Live
state, cost and `$/ns` for every one of them: the [**⏱️ IN FLIGHT**](../../research/manuscripts/nr4a3-program-map.md#in-flight-superseded) block on this page, which is their
one home — ⚠ **and this paragraph must never restate it.** It said *"three lanes are billing"* for a day after
the board said nothing was, which is a rule-1 defect in the one direction that matters, since a stale
"currently spending" line is what an unattended fleet looks like when it is *not* being supervised.

**Built and idle, awaiting a go or a decision:**
- **The NR-V04 retrospective** — built, preregistered, never launched; next launch is a pilot, not a fan-out.
  ⚠ **"Awaiting a go" overstates it, and the correction is the point:** its own gate names two preconditions
  that are **unreachable**, and its driver does not meet a requirement this file adopted. Both are in
  [§WHAT THE LANDED RESULTS CHANGE](../../research/manuscripts/nr4a3-program-map.md#-what-the-landed-results-change-about-the-remaining-plan) 4–5;
  the decision is [§Open decisions 12](../../research/manuscripts/nr4a3-program-map.md#open-decisions).

**★ WHAT IS ACTUALLY NEXT is not on this page.** This section says what is *idle*; it has never said what to do
first, and while the fixed scope was closing that gap did not matter. It does now — nothing is billing, so the
next thing to happen is a *choice* rather than a result landing. The ranked list, the reasoning and the prices
are in [§WHAT THE LANDED RESULTS CHANGE](../../research/manuscripts/nr4a3-program-map.md#-what-the-landed-results-change-about-the-remaining-plan) 6,
which is their one home; **this paragraph deliberately does not restate the order.**

**Closed earlier:** the 5a-KS confirmatory protein-mutation benchmark **qualified** (RUNG 5a-KS), moving the
ladder's only unscoped rung from UNPRICED to *projected*. Nothing with a GPU price launches without an explicit
go, and every rental — fan-out, resume or single cold unit — now faces the buy line as well as its rung's
dollar ceiling.

## Open decisions

- ⛔ **NEW 2026-08-03 — the anti-target self-control's criterion is UNDER-SPECIFIED for a multi-copy deposit, and it is currently deciding a FAIL.** CYP3A4: scored 12.337 Å against copy KLNA1501, but 1.108 Å from copy KLNA1500 (8 copies in the deposit). The pre-registered criterion reads *"the crystallographic copy of the same ligand"*, which has no referent when a deposit places several copies of the cognate in one site. ⚠ **The verdict was left FAIL and must stay there until this is ruled on**, because choosing the copy after seeing which one passes is the tuning the rung's own frozen rule forbids. The decision is one sentence — score against *any* deposited copy, or against a *named* one — and it must be written down BEFORE it is applied. Evidence: [`antitarget-selfcontrol.json`](../../research/modalities/antitarget-selfcontrol.json) → `repair_delta`.


*★ **THE DECISION REGISTER.** 15 numbered rulings, all closed. ⚠ **Cited by number in 30 files and nothing resolves a decision number** — the numbering is **frozen** and survived this file's merge unchanged. [§10](../../research/manuscripts/nr4a3-program-map.md#10--the-roadmap--one-ordered-list) rows cite these by number.*

1. **`[x]` ADOPTED — method calibrator swapped from NR-V04 to SMARCA2-vs-SMARCA4** (valB_full module 3). NR-V04
   stays the biological holdout; its selectivity is most plausibly covalent target engagement, and SMARCA2/4 is
   already staged in-repo.
2. **`[x]` ADOPTED — the protein-mutation wedge is demoted from primary to confirmatory.** The ligand-side double
   difference is the paper's headline causal evidence and runs on the lane Val B already has an accuracy control
   for. The mutation cycle is kept, not deleted: its benchmark has now passed. ⚠ **The clause that stood here —
   *"so the paper can have two independent causal lines"* — is WITHDRAWN (2026-07-30):** the mutation cycle is
   a **ternary-minus-binary contrast, structurally the quantity that failed**, so it is a second line but not an
   independent one. Algebra and consequences: [Open decisions 10](../../research/manuscripts/nr4a3-program-map.md#open-decisions).
3. **`[x]` DECIDED — adopt 4 fs, but TWO-STAGE**, sequenced after valB_mini's 2 fs result (RUNG 2b).
4. **`[x]` REVERSED — the step1 fan-out was RESUMED on 2026-07-26 and is running.** The hold below is
   **superseded**; it is kept because its reasoning is still the right reasoning and would apply again to any
   *new* edge list.
   *Superseded text, do not cite as current:* **"HOLD the step1 fan-out; do NOT resume the 19-edge tranche"**,
   on a *scientific* reason independent of price — under mechanism-first the fan-out's **selection criterion**
   had changed, the exit vector must now carry a linker toward **C397** (10.9 Å) and orient the E3 so the
   transfer zone covers **K572/K518/K592**, which is not the same as ranking substituents by affinity, so
   resuming the old edge list would spend ~$36 optimising the wrong objective; and nothing was lost by
   re-scoping because **0/19 units had produced a ΔΔG**.
   **What retired it:** the 5a basin search — the $0 step the hold was waiting on — **completed**, and the two
   preconditions it was protecting are now met. The lane also ceased to be a $36 all-or-nothing bet: placement
   is **per unit** and gated on `$/ns`, so it buys only what the market sells inside the buy line and holds the
   rest, and the cycle-closure edges are in the queue rather than stranded in a last wave. The rung entry under
   RUNG 4 carries the live status.
5. **`[x]` CLOSED — raising `GPUS_ALL_REGIONS` is NOT available to us.** trimcrae, 2026-07-26: *"We've tried
   over and over for more quota. They won't give it to a small account like ours."* Repeatedly requested,
   repeatedly refused. **Do not re-file it, and do not plan around a quota that is not coming.** (I raised it as
   an ask the same day, quantified at 1→4; withdrawn — see [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 20.)

   **AND A FASTER GPU WOULD NOT HELP EITHER — because the GCP lane is DOLLAR-bound, not time-bound.** Asked and
   answered 2026-07-26 rather than assumed. From [credit-status.json](../../research/compute/credit-status.json): cap
   **$300**, spent **$8**, so **~$292 remains** against a 2026-10-10 expiry.

   | | value |
   |---|---|
   | one full ternary leg (2800 iters × 56.5 s) | **43.9 L4-h ≈ $31** |
   | credit runway | **~411 L4-h ≈ 17 days continuous ≈ 9.4 full legs** |
   | calendar available | 76 days ≈ 1,824 h of single-GPU wall clock |

   The credit is exhausted after ~17 days of continuous running inside a 76-day window, so **calendar is not
   scarce — money is.** And science-per-dollar is `speed / rate`, which is flat-to-worse on faster cards
   *(non-L4 rates are list-price approximations, not repo-measured)*:

   ⛔ **SUPERSEDED 2026-07-31 — the non-L4 rows of BOTH tables below are WITHDRAWN, do not cite them as
   current; the correction is beneath them and in [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 56.**

   | card | rel. speed | ~$/h | units/$ | leg-equivalents on $292 |
   |---|---|---|---|---|
   | **L4 (current)** | 1.0× | 0.71 | **1.41** | **9.4** |
   | A100 40 GB | ~5.2× | 3.67 | 1.41 | 9.4 |
   | V100 ⛔ *superseded* | ~3.0× | 2.48 | 1.21 | 8.0 |
   | H100 80 GB | ~11× | 11.0 | 1.02 | 6.7 |

   **★ BUT THE CENSUS CHANGED THE ANSWER, AND NO REQUEST IS NEEDED FOR ANY OF IT.** `GPUS_ALL_REGIONS = 1` caps
   the **count**; the **per-type** quotas say which card, and several are **already granted at limit 1** —
   `NVIDIA_V100_GPUS`, `NVIDIA_P100_GPUS`, `NVIDIA_T4_GPUS`, `NVIDIA_P4_GPUS`, `NVIDIA_K80_GPUS` alongside
   `NVIDIA_L4_GPUS` (A100/H100 are the only ones at 0). Nobody had looked, because the quota check only grepped
   `L4|G2|GPU` and printed the rows mid-log. Spec-derived against the ~$292:

   ⛔ **SUPERSEDED 2026-07-31 — WITHDRAWN, do not cite; see beneath the table.**

   | card | quota | ~×L4 | ~$/h | ~$/leg | legs on $292 | science/$ |
   |---|---|---|---|---|---|---|
   | L4 (current) | 1 | 1.00 | 0.71 | 31 | 9.4 | 1.41 |
   | **P100** ⛔ *superseded* | **1** | ~2.4 | 1.46 | **26** | **11.1** | **1.67** |
   | V100 ⛔ *superseded* | 1 | ~3.0 | 2.48 | 36 | 8.0 | 1.21 |
   | T4 ⛔ *superseded* | 1 | ~1.1 | 0.35 | 14 | 20.3 | 3.05 |

   ⛔ **SUPERSEDED BY MEASUREMENT, 2026-07-31 — DO NOT CITE EITHER TABLE ABOVE AS CURRENT.** The reading they
   supported — *"P100 looks better than L4 on BOTH axes, faster and more science per dollar, i.e. **+18 % more
   legs from the same money**"*, and the T4 at **2.2×** the L4's science-per-dollar — is **WITHDRAWN**. It was
   never measured, it was flagged as unmeasured, and the measurement has now refuted the heuristic that
   produced it. Retained above because it is what the plan carried for five days;
   [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 56 has the correction.

   **★★ WHAT THE PROBE MEASURED, AND WHY IT INVERTS THE TABLE.** Built and run 2026-07-31 on free trial credit
   (`gpu-bench-gcp.yml` + [`gcp_card_bench.py`](../../research/modalities/gcp_card_bench.py)); one home for every
   number is [`gcp-card-bench.json`](../../research/modalities/gcp-card-bench.json), and the readable table with its
   full caveats is **[gcp-gpu-facts.md §1c](../../research/compute/gcp-gpu-facts.md)**. Do not copy figures here —
   point at those.

   1. **THE WORKLOAD IS COMPUTE-BOUND, NOT BANDWIDTH-BOUND — and that is the whole ballgame.** The T4 is the
      discriminating card precisely because its two specs point opposite ways (bandwidth 320 vs the L4's 300,
      FP32 8.1 vs 30.3 TFLOPS). Bandwidth predicts **1.07× L4**; FP32 predicts **0.27×**. **Measured: ~0.31×**
      at the ternary system size. So every row generated by the bandwidth heuristic — P100 and V100 included —
      rests on a premise the measurement rejects.
   2. **THE SPEC TABLE ALSO HAD A PRICE ERROR THAT NEEDED NO MEASUREMENT AT ALL.** Its `$/h` column compares
      the L4's **whole-VM** rate (0.71 = a g2-standard-4, which *bundles* the L4) against **bare GPU** rates
      for the others (1.46 / 2.48 / 0.35). A P100 cannot run without a host. Adding the n1-standard-4 it needs
      (**$0.190/h**) to the same table, with its own speed assumptions untouched, already collapses P100's
      advantage from **+18 % to +3 %** and the T4's from **2.16× to 1.44×**. Two independent errors, both in
      the direction that made the alternatives look good.
   3. **THE PRACTICAL ANSWER: STAY ON THE L4.** Combining the two, the T4 delivers **~0.41×** the L4's
      science-per-dollar where the table promised 2.2× — wrong by **~5×**, and in the direction that would have
      sent the next GCP leg to the worst card available. The original framing of this decision — *"a faster GPU
      would not help either, because the GCP lane is DOLLAR-bound"* — **survives, and is now measured rather
      than assumed.**

   ⚠ **WHAT IS STILL NOT MEASURED, stated so nobody over-reads this.** The T4 figure was **REFUSED by the
   probe's own admission gate** (CV 5.6 % against a 5 % ceiling) and is reported as a *ranking*, not a rate —
   a 3.5× discrepancy cannot be manufactured by 5.6 % of block scatter, but the number itself is provisional.
   Capacity also intervened: `NVIDIA_T4_GPUS` on-demand returned **`ZONE_RESOURCE_POOL_EXHAUSTED` in all four
   us-central1 zones**, so the T4 arm had to run on spot ([facts §1d](../../research/compute/gcp-gpu-facts.md)).
   **A granted per-type quota is not capacity** — that is new, and it is the one respect in which "we already
   hold quota for several GPU types" oversold itself.

   **What no longer holds: "buy the probe together with the first GCP leg that is actually queued."** That was
   right while the probe was hypothetical and the answer had no consumer. It is now bought and the answer
   exists, so the sequencing question is closed rather than deferred.

   **What stands regardless: no GPU quota REQUEST is worth filing** — not more count (refused, and wouldn't have
   helped), and not a faster type (we already hold several). ⚠ This also means the quota increase I
   proposed would not have helped **even if Google had granted it**: at 4 GPUs the same $292 is spent 4× faster,
   not turned into 4× the science. That table's central claim was wrong independently of the refusal — see
   [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 20.

   **THE REAL BUDGET, and the number to plan the rescope against: ~$292 ≈ 9 more full ternary legs on GCP.**
   The lane split still holds and is still not a cost question — GCP free/serial/1-GPU at ~56.5 s/iter, Vast paid/
   parallel at ~16 s/iter (**3.53×**, corrected from the 2.06× in pricing.md, which compared an L4 *warmup* rate
   against a 4090 *production* rate). Every idle GCP-GPU minute is still expiring credit lost, so keeping that one
   GPU fed still matters — it just cannot be fed for more than ~411 hours in total.

6. **`[x]` CLOSED 2026-07-30 — the valB_mini rescope. `R` answered it, and the answer is that no rescope of
   this calibrator's EDGE can help.** *(It was held until the reverse leg read out; that landed 2026-07-28, and
   the closure triangle then produced `R`.)* Every rescope variant was a search for a better **edge** — a bigger
   signal, a cleaner replicate SD, the P-series network. **`R ≈ 0` says the miss is an ENDPOINT-STATE error**,
   which telescopes out of any cycle and is a property of the **model or the reference data**, not of which edge
   sits on top of them. Changing the edge changes neither. The live successor is a **system** question, not an
   edge question — [decision 9](../../research/manuscripts/nr4a3-program-map.md#open-decisions) and its $0 survey of paralogue-selective systems with a solved
   structure on **both** arms. *(Superseded framings retained: the P-series congeneric network, refuted for $0
   on charge/heavy-atom grounds; and the synthetic closure triangle, which was not a rescope in the end but the
   diagnostic that closed this item.)*
7. **`[x]` RESOLVED 2026-07-30 — the admits-zero gate defect. It never touched valB's verdict, and it is now a
   BINDING REQUIREMENT ON THE NEXT CALIBRATOR rather than a retrospective amendment. $0.** The frozen gate
   accepts a method that predicts no cooperativity change (**22 % vs 23 %** — a gate you can pass by predicting
   nothing). Two things settle it. **(a) It is moot for valB_mini**, which failed on **SIGN**, before the
   `|mean − target| ≤ 1.0` band was ever consulted — so no amendment could change that verdict and none is
   sought, which is exactly why this is not the forbidden retune. **(b) It is NOT moot going forward**, because
   any future calibrator reusing this gate design inherits it. **It therefore binds the S-calibrator spec
   ([decision 9](../../research/manuscripts/nr4a3-program-map.md#open-decisions)): no accuracy band wider than the signal being calibrated, and a stated
   null-rejection rate up front.** The 22 %/23 % measurement is the evidence for that requirement; the frozen
   valB gate itself is left **unamended**, on the record, failed on sign.
8. **`[x]` RESOLVED 2026-07-30 — the `UNDERPOWERED` proxy. $0, LOW STAKES, and it is low-stakes because the measurement says
   so.** `binary_departure_prereg` demotes a null closure to `UNDERPOWERED` whenever `sigma_leg > 0.2` — a
   threshold hand-set when `sigma_leg` was unknown to a factor of 15.6, i.e. a proxy chosen because the power
   itself was not computable. **It is computable now, and it VINDICATES the proxy:** bisecting the design's own
   power curve puts a conventional 0.80-power threshold at `sigma_leg ≈ 0.216` against the frozen **0.200** —
   agreement to ~7 %. ⚠ **So amending it would NOT rescue a null `R`**: at the measured upper bound the power
   is ~0.63, which a conventional threshold demotes anyway. **Proposed fix is therefore transparency, not
   correction** — report the computed power *beside* the verdict, keeping the demotion rule, because
   "UNDERPOWERED" currently cannot distinguish power 0.63 from 0.05 and those warrant different responses.
   Evidence: [`valb_failure_propagation.frozen_rule_vs_measured_power`](../../research/modalities/valb_failure_propagation.py).
   **Same standard as item 6 and it is why nothing was changed:** a rule may be amended only if its statistic
   is shown to lack discriminating power, demonstrated independently of whether we like its answer — and here
   the statistic turned out **not** to lack it. Written down **before `R` landed**.
   **★ THE LIVE QUESTION IS NOT THIS RULE — IT IS WHERE `sigma_leg` ACTUALLY SITS.** The crossing (≈0.216) lies
   *inside* the bounded interval [0.045, 0.265], so a null `R` is readable or not depending on the true value,
   and the bound is an UPPER bound. **That is settleable for $0 from the triangle's OWN legs when they land** —
   `valb_failure_propagation.narrow_sigma_leg_from_triangle_legs` applies the n=3-measured replicate-SD/MBAR-SE
   ratio to the triangle's own per-leg MBAR SEs, giving an estimate with no homology-model and no cross-seed
   solvation term. ⚠ The ratio is **transferred, not measured on the triangle** (which has no replicates), so
   this narrows the interval and must never be reported as though the triangle had replicates.
9b. **`[x]` DONE 2026-07-30 — decision 9's $0 survey RAN, and it answered more than it was asked.
   Artifact: [`s-calibrator-survey.json`](../../research/modalities/s-calibrator-survey.json)
   (generator [`s_calibrator_survey.py`](../../research/modalities/s_calibrator_survey.py)); every PDB ID is fetched
   from RCSB, never typed.** Ten candidate paralogue pairs screened on whether a deposited **ternary** exists
   on **both** arms. **2 of 10 are symmetric: SMARCA2/SMARCA4 and IKZF1/IKZF3.** The incumbent therefore
   **survives its own screen** and decision 9 forces no system change. Two pairs would have been traps —
   **BRD4 has 24 ternary structures while BRD2 and BRD3 have zero**, so either BET pairing puts a modelled arm
   opposite a real one, the exact configuration decision 9 exists to avoid.
   **★ THE FINDING THAT MATTERS MOST WAS NOT THE QUESTION ASKED, AND IT IS A CORRECTION.** A first reading of
   this survey said the lane's SMARCA4→SMARCA2 homology substitution "was avoidable". ⚠ **It was not — not for
   this ligand.** 8G1Q's own deposition title is *"Compound 1 … bromodomain of human **SMARCA4** and
   pVHL:ElonginC:ElonginB"*: Wurz **compound 1**, the calibrator's `calib_hi`, was co-crystallised **only** with
   SMARCA4. Every deposited SMARCA2 ternary carries a **different ligand** (8G1P = Compound 11, 6HAX = PROTAC 2,
   6HAY = PROTAC 1, 9HYB = P-series P3). Keeping the ligand whose SPR α values **are** the reference data
   therefore *forced* the substitution.
   **What the choice cost is the real result: the calibrator is built on the LOWEST-RESOLUTION structure in the
   family — 3.73 Å — AND on the wrong paralogue, while SMARCA2 ternaries exist at 2.24–2.84 Å.**
   Ligand-identity and protein-identity are **coupled** here, and the lane resolved that coupling in favour of
   the ligand. **`R` has since localised the valB miss to the model or the reference data — and both candidate
   causes trace to that one coupled choice.** Binding consequence for the S-calibrator spec: **pick a pair
   whose reference data and structure sit on the SAME protein**, rather than buying reference data at the price
   of a modelled arm. *(Not established and not claimed: that a different template would change the
   calibrator's answer. A shared deposition series does not make two entries interchangeable.)*

9. **`[x]` DECIDED 2026-07-30 (trimcrae delegated: *"You make an educated call yourself"*) — the valB_full gate
   is NOT amended, and module 3 is NOT decoupled to unlock it.** The question was whether module 3 (paralogue
   discrimination, SMARCA2-vs-SMARCA4) should be freed from behind the failed cooperativity gate now that `R`
   says the ternary environment is internally clean. **It should not.** Module 1's statistic did not *lack
   discriminating power* — it discriminated perfectly well and returned NO — so the repo's own amendment
   standard ([AMENDMENT 1](../../research/modalities/nr4a3-nrv04-covalent-feasibility-prereg.md#amendment-1--2026-07-25-dated-defect-fix-trimcrae-delegated))
   does not reach it; and `R` supplies no licence either, because `R` is **blind to the endpoint-state class
   that broke valB**. Unlocking the prospective ladder here would be the retune this program forbids, wearing
   a diagnosis as cover. **The prospective NR4A ternary matrix stays unrun and cooperativity claims stay
   exploratory.**
   **★ THE REAL FINDING IS A GAP, NOT A GATE IN THE WAY.** `S` — the flagship kill-switch the whole prospective
   stage turns on — **has never had a known-answer calibrator**, because valB_mini calibrated `ΔΔG_coop`, a
   quantity `S` does not contain (its binary leg cancels algebraically). The failure *exposed* that; it did not
   cause it. Closing it is a **new item**, not a gate amendment, and it unlocks **nothing** beyond whether `S`
   may be read as calibrated rather than exploratory. Reasoning + what must be preregistered first:
   [`valb_failure_propagation.module3_decision`](../../research/modalities/valb_failure_propagation.py).
   ⚠ **The strongest argument against, recorded because it must be preregistered rather than discovered:** an
   S-calibrator on SMARCA2-vs-SMARCA4 runs on the **same system family carrying the suspected error**, and a
   known-answer accuracy test does *not* telescope an endpoint-state error the way a cycle does — which is
   precisely why valB_mini caught it. The arms are also **asymmetric**: 8G1Q is a *SMARCA4* structure and
   SMARCA2 is the homology-substituted arm, so a homology-model error sits on **one arm and does not cancel**.
   A failure would then be ambiguous between *"the S-class quantity does not work"* and *"this benchmark
   inherited the same model defect."* **So the system must be chosen on which arm is REAL, not on what is
   already staged** — and the $0 survey of paralogue-selective systems with a solved structure on *both* arms
   leads, before any spend.
10. **`[x]` RESOLVED 2026-07-30 — the protein-mutation cycle is no longer called an independent second causal line.
   $0.** RUNG 5's CONFIRMATORY cycle is `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` — a
   **ternary-minus-binary contrast, structurally identical to the quantity that failed** (the PRIMARY `S`
   escapes this only because its binary leg cancels *algebraically*; a protein mutation changes the target,
   which is exactly what the two environments differ by). Its known-answer benchmark passed on a
   *protein-mutation* quantity, **not** on a ternary-minus-binary one, so that pass does not cover this
   exposure. Consequence: a concordance between `S` and this cycle is **not two independent lines agreeing**,
   and a discordance would be uninterpretable. Derived in
   [`valb_failure_propagation.error_algebra`](../../research/modalities/valb_failure_propagation.py). *Not
   load-bearing* — the paper's headline causal result is already stated as not hostage to it.
11. **`[x]` DECIDED 2026-07-30 (trimcrae go) — `S` GETS n = 2 SEEDS PER ARM (4 ternary legs).**
    The lane is re-specified and the ladder regenerated: `ternary_vast_launch.MODES['5aks']` declares four
    legs, `vast_cost_model` prices four, the stage-cache seeder now seeds **every declared seed** (it seeded
    only seed 0, and `5aks` sets `stage_required: True`, so a seed-1 leg would have died on a cache MISS on a
    rented host), and both new units are on the watch list rather than launching unwatched. **Nothing is
    bought yet** — all four stay `enabled: false` behind the relaunch price gate and re-enable **together**,
    because a partial re-enable buys a number that still cannot report a null.
    ⚠ *The two parked seed-0 legs are untouched and resume byte-identically from `production/800` and
    `warmup/640`; the seed-1 legs are cold starts.* The question, as it stood:

    **`[~]` HOW MANY SEEDS PER ARM DOES `S` GET? This is trimcrae's, because it is a multi-leg GPU
    spend; everything else about it is settled and free.** ⚠ **It must be settled BEFORE the market re-opens,
    not after**: the relaunch price gate is the only thing currently holding the lane, and `R_ternary` already
    reads **ADMIT** on the science gate — so the next cheap offer resumes 5a-KS in the **n = 1 per arm**
    configuration that
    [§WHAT THE LANDED RESULTS CHANGE](../../research/manuscripts/nr4a3-program-map.md#-what-the-landed-results-change-about-the-remaining-plan) 3
    shows cannot report its own likely answer.
    **RECOMMENDED — n = 2 per arm (4 legs; the 2 parked legs plus 2 more), for roughly double the parked
    ladder figure.** The reasoning is this repo's own litmus test, applied to the *design* instead of the
    sequence: *is there a result the extra pair could return that changes what we do?* **Yes — a readable
    null.** The pre-registered expectation is that the effect sits inside the range `S` can only half-resolve
    at n = 1, so the increment is what converts the **likely** outcome from an uninterpretable non-result into
    a **publishable bounded negative** — the same argument that made valB-mini "the highest-value dollar in
    the plan", now applied to the test valB-mini was supposed to certify. The $0 machinery check is **done**
    and favourable (item 3); the seeds are genuinely independent.
    **The alternatives, stated fairly.** *(a) Finish as parked (n = 1, ~$12 total, ~$1.5 already banked):*
    cheapest, retires the paper's *"the causal test has not been run"*, and is enough **if** `S` comes back
    large. Its failure mode is the likely case. *(b) n = 3 per arm (6 legs):* the repo's stated replicate
    standard, and it brings the resolvable difference down to the figure in §MECHANISM-FIRST — but the second
    seed buys most of the readability and the third is the shallow part of a `1/√n` curve, so it is the
    "deepening past field standard" CLAUDE.md §5 defaults against. *(c) Don't buy:* defensible only if the
    paper is content to ship with its headline causal test unrun, which contradicts the North Star.
    **What I would do, and would not do without a nod:** buy (b)-minus — the 2 parked legs plus 2 more, at
    n = 2 — and read a null as a bound rather than an absence. **Not proposed:** re-running the parked legs
    from scratch (their checkpoints are intact and durable) or extending them (more sampling on one seed buys
    precision that `S` does not lack).
12. **`[x]` DECIDED 2026-07-30 (trimcrae go) — THE NR-V04 RETROSPECTIVE RUNS: ARM E (R1, 18 legs, ≈$8). *(count SUPERSEDED by prereg AMENDMENT 4, 2026-07-31: **16 legs** — `nr4a3` co-fold seed 3 excluded by measured input fault)*.
    Arm F stays blocked on the valB PASS.** ⚠ **AND MY FRAMING OF THIS WAS WRONG IN A WAY WORTH
    CORRECTING: I proposed it as a scope correction I had derived, and the prereg had already made the
    same argument on 2026-07-24.** Its **§9 "Dependency honesty"** states that the gates govern the
    free-energy arm, that Arm E asserts no free energy, and that running Arm E is a *narrowing* rather
    than a gate jump — then names the alternative (hold Arm E until valB passes) and leaves the
    judgement open. So no criterion is amended and no amendment was needed; the decision is recorded as
    a **dated addition** in the prereg, which is what §9 itself asks for. The gate wording that
    conflicted was **this file's**, and it is reconciled in the RUNG 4 entry. What genuinely changed
    since 2026-07-24 is the premise: `step1_fanout` completed and the feasibility panel was WITHDRAWN,
    so two of three gates became **unreachable** rather than pending. **Integrity test, checkable
    rather than rhetorical: the panel has never run, so no result exists that this could have been
    motivated by disliking** — the distinction from [decision 9](../../research/manuscripts/nr4a3-program-map.md#open-decisions), where a real NO
    existed and the gate was correctly left standing. **Precondition met** (durable trajectory).
    The question, as it stood:

    **`[~]` DOES THE NR-V04 RETROSPECTIVE RUN, OR IS IT FORMALLY RETIRED? It cannot stay "idle".**
    Its gate names **valB_full** and the **NR-V04 feasibility panel**; the first is behind a module-1 gate
    [decision 9](../../research/manuscripts/nr4a3-program-map.md#open-decisions) has just declined to amend, and the second is **WITHDRAWN**. Neither is
    coming. Leaving it listed as built-and-awaiting-a-go is the *appearance* of a plan for ~$7.7 of work that
    nothing can authorise.
    **RECOMMENDED — a SCOPE correction to the gate, not an amendment to a rule, and only after the $0
    precondition below.** The argument, and it is deliberately narrow: **valB calibrates the ternary-FEP
    cooperativity lane, and the retrospective's authorised readout (`R1`, Arm E, 18 legs — *(count SUPERSEDED by prereg AMENDMENT 4, 2026-07-31: **16 legs** — `nr4a3` co-fold seed 3 excluded by measured input fault)*) is not in that
    lane** — it is an **endpoint-MD geometric contrast reported in Ångström**, with its own registered MDE
    (leg-to-leg σ 0.855 Å, 80 % power at 1.5–2.0 Å) and its own preregistered *directional-concordance-only*
    claim ceiling. A gate that names a control which does not cover the quantity is a **scope** defect, and it
    reads as one in the direction that matters: this is a *biological holdout*, i.e. exactly the kind of **new
    axis of evidence** CLAUDE.md §5 defaults YES to. ⚠ **The integrity test it must pass, stated because the
    repo forbids the retune this could be mistaken for:** amending a gate after a failing result is forbidden
    — **but there is no result here to rescue.** The retrospective has never run, so no verdict exists that
    this correction could be motivated by disliking. That is the difference between this and
    [decision 9](../../research/manuscripts/nr4a3-program-map.md#open-decisions), where a real NO existed and the gate was correctly left standing.
    **HARD PRECONDITION — ✅ NOW MET, $0.** The shared driver had to persist a durable trajectory first, because
    launching 18 legs on a driver that discards positions repeats, exactly, what made the parent panel
    unrecoverable. Built and wired 2026-07-30 (item 4 above), so **this decision is no longer blocked on
    engineering — only on the call.** **If the decision is no, retire it explicitly** with the reason on the
    record — a named retirement is a result; an indefinite hold is not.
13. **`[x]` SPLIT 2026-07-30 — the "`S` has no calibrator" gap is TWO items, and the free half is now DONE.**
    [Decision 9](../../research/manuscripts/nr4a3-program-map.md#open-decisions) recorded the gap as one thing and left it unsequenced, which is why it never
    acquired a rung. It separates cleanly:
    - **(a) Can a null `S` be READ? — a power/MDE question, $0, and it needs no known answer at all.** It is
      arithmetic on measurements this program already owns, and it is what item 3 above just did. **Done.**
      This is the half that actually gates the 5a-KS spend, and it was never the expensive half.
    - **(b) Can a non-null `S` be called CALIBRATED? — a known-answer question, and it is the paid one.** It
      stays deferred, behind [decision 9b](../../research/manuscripts/nr4a3-program-map.md#open-decisions)'s binding requirement (pick a pair whose reference
      data and structure sit on the **same** protein) and [decision 7](../../research/manuscripts/nr4a3-program-map.md#open-decisions)'s (no accuracy band
      wider than the signal being calibrated). ⚠ **It does not gate item 11**, and conflating the two is what
      made the gap look unaffordable: a *bounded null* needs (a) only, and a bounded null is the
      pre-registered likely outcome.
    **Consequence for the ladder:** `S` may be bought and read as a **bound** now; it may not be reported as
    calibrated until (b) exists. Both statements can be true in the same paper, and saying so is cheaper and
    more honest than waiting for (b) to buy (a)'s answer.

---

