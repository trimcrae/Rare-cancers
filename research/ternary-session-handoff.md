# HANDOFF — NR4A3 degrader **TERNARY-path** session (start here)

**You are the TERNARY session.** Continue the induced-proximity / degrader-**ternary-selectivity** path of the
NR4A3-selective degrader program for EMC (EWSR1::NR4A3 fusion cancer). A **separate "binder" session owns the
in-flight ABFE** (denovo_401 warhead qualification, Track A) — **do NOT touch Track A / ABFE / the λ-repair**;
it is being handled there. (The reviewer-AI's response to my decision block is included alongside this handoff
in the start prompt — fold it in before spending any GPU.)

## Read first (in order)
1. **CLAUDE.md** + **AGENTS.md** — project rules. Non-negotiables: times ALWAYS **ET, 12-hour AM/PM**; the
   end-of-turn **"In flight" board** (actual jobs only, not self-timers); **no wet lab**; the honesty golden
   rule; **spot-GPU default** + pilot-one-leg-first + wait-out-spot-capacity; engineering-is-free;
   exhaust-self-doable-before-surfacing; and **every hand-off / outward step starts with a copyable
   reviewer-AI review block**.
2. **research/manuscripts/nr4a3-degrader-strategy-ternary-first.md** — THE adopted strategy (ternary-first,
   congeneric Zaienne-19 warheads, RBFE primary, ternary the central selectivity variable, two-tier promotion,
   de-prioritized routes).
3. **research/manuscripts/nr4a3-congeneric-rbfe-plan.md** + **research/modalities/congeneric-rbfe-map.json** —
   the binary RBFE perturbation map (pilot edge + pre-registered abort criteria).
4. **research/modalities/nrv04-ternary-benchmark.json** → keys `descriptive_v3_result`, `review_v3_final`,
   `real_cif_smoke_result` — the NR-V04 retrospective control result + the analyzer's honest limits.
5. **research/modalities/nr4a3-abfe-repair-prereg.md** — the *pattern* to mirror when you preregister the
   ternary-cooperativity method (technical criteria + accept/abort + control, decided up front).

## Where the ternary path stands (dependency chain)
1. **Architecture triage (co-fold): VALIDATED.** The NR-V04 control passed — the workflow recovers "degrades
   NR4A1 / spares NR4A2-NR4A3" (NR4A1 seed-bridged **0.67** vs NR4A2 **0.00** / NR4A3 **0.00**, robust across
   4.0/4.5/5.0 Å, survives leave-one-seed-out). **BUT** the VHL-inactive hydroxyproline **epimer** bridged
   **1.00 ≥ active 0.67** → the co-fold is **ARCHITECTURE-TRIAGE-ONLY, with ZERO authority over affinity,
   cooperativity, or degradation-selectivity ranking.** Never rank a prospective construct on the co-fold.
2. **Warhead inputs (binary RBFE):** congeneric Zaienne-19 series **BUILT** —
   `research/modalities/congeneric-warhead-series.json` (19 compounds: 8 exit-vector 5-substitutions, 5
   SAR-preserving carboxylate bioisosteres, 3 microstate variants, 3 denovo_401 comparators); RBFE map
   **DESIGNED** (pilot edge 5-Br→5-NH₂ + abort criteria). **NOT RUN** (expensive fleet, needs budget go).
   Compound 19 has **no cocrystal** — its pose/exit-vector are hypotheses; the bioisostere edges are flagged
   `needs_pose_revalidation`.
3. **Ternary affinity/cooperativity ranking: GAP.** The co-fold can't do it; you need a **separate physics
   method**. **NOT built.** This is the highest-value, open contribution.
4. **The matrix** {warheads × exit-vectors × VHL/CRBN × linkers}: downstream of 2+3. **NOT built.**

## Your immediate next step (self-doable, free — do it before any GPU) — ✅ DONE 2026-07-11
**Preregister a physics-based ternary-cooperativity method + its NR-V04 cooperativity control**, mirroring
`nr4a3-abfe-repair-prereg.md`. **COMPLETE** — the reviewer's "APPROVED WITH SCOPE CHANGES" decision is folded
in. Deliverables (branch `claude/nr4a3-ternary-coop-prereg-51wqw9`, commit `3b1920b`):
- **`research/modalities/nr4a3-ternary-coop-prereg.md`** — the prose prereg (method = thermodynamic-cycle
  cooperativity `ΔG_coop=−RT ln α` via matched binary-vs-ternary relative alchemical calcs [option ii
  implementing iii]; MM-GBSA demoted to descriptive-only; **two-layer calibration** [quantitative VHL panel
  FIRST, then NR-V04 as a family-transfer test]; the full §3 retrospective bar; parallel-pilots/staged-fleet
  sequencing; VHL-first / CRBN-held; +4 architecture layers [ensemble+linker-strain, Cullin-RING/E2~Ub
  lysine-presentation, fusion-context]).
- **`research/modalities/nr4a3-ternary-coop-prereg.json`** — machine-readable frozen criteria (single source
  of truth).
- **`research/modalities/ternary_coop_gate.py`** + **`tests/test_ternary_coop_gate.py`** (27 passing) — the
  pure-stdlib gate enforcing §3 against a future results dict, so no criterion is re-decided post-hoc.

### Reviewer round 2 ("RETURN FOR FIXES") — ALL 8 FIXES LANDED ✅ (commit `6b579a8`)
The reviewer confirmed the science/sequencing were faithfully captured but the gate could PASS prose-violating
inputs. All 8 required fixes are implemented + verified (**49 passing tests**, up from 27; CLI end-to-end pass;
validator clean): (1) `_num()` rejects NaN/inf/bool + safety booleans fail closed; (2) frozen expected-leg +
expected-system manifests, panel n≥6/all-verified/keyed-by-ID/composition; (3) class-correctness + LOO computed
**in-gate** from per-system records (frozen α bands 2.0/0.5); (4) Kendall **τ-b** with tie handling; (5)
corrected intervals (favored side ⇒ entire interval > 0, `ci_lo>0`; prob∈[0,1]); (6) 95% CI half-width over
**every** decision quantity via a frozen `decision_quantities` manifest; (7) formal reproducible **S_d**
definition frozen in JSON (sign/`c`/replicate-SD/counterexample/units/missing-data/tie/top-3 ±50% robustness);
(8) test suite expanded to all required failure modes. **Reviewer post-fix authorization:** approve (a)/(b)/(c)
below as **no-spend engineering**; binary `MODE=plan` approved after the congeneric edge + design-frame inputs
are wired; ternary `MODE=plan` approved only after the exact high/low Layer-1 pair + all pilot identities/
structures/microstates/transformations/replica-count/λ-schedule are frozen (must be the ACTUAL bundle, not a
placeholder); **no production GPU authorized**; **no further scientific check-in required** for these no-spend
steps once the fixes pass (they do).

### Reviewer round 3 (conditional approval, 2026-07-12) — ALL 7 REQUIREMENTS APPLIED ✅
The reviewer conditionally approved A′/B/C and required 7 changes; all applied + tested (**652-test suite,
0 failures**):
- **Req 1 (numeric α frozen):** Supplementary Table 1 values from Nat Commun 2025 (PMC12480974) frozen in
  `candidate_systems` — P1 93±41 (9HYN), P2 4.1±1.8 (**7Z77**), P3 5.0±3.5 (9HYB), P4 1.3±0.4 (9HYO),
  P5 0.6±0.3 (9HYP); SI PDF checksummed; a test recomputes P5 α from its 98/160 nM IC50s.
- **Req 2:** exact-permutation τ-b reporter + prespecified ordinal tiers P1>{P2,P3}>P4>P5 (robustness only;
  numeric α stays primary; gate NOT amended to ordinal-only).
- **Req 3 (sign convention, critical):** gate converts predicted ΔG_coop→α via −RT ln α before τ-b; sign-flip
  fails; predicted_alpha/ΔG_coop sign disagreement flagged — hard invariant tests.
- **Req 4:** observable labeled apparent α_TR-FRET = IC50(binary)/IC50(ternary) (not Kd-derived); P5 text
  (~0.2) vs table (0.6) discrepancy recorded; MM-GBSA-no-correlation narrowed to this dataset+protocol;
  bands NOT retuned post-hoc.
- **Req 5 (Plan B):** `ternary_coop_io.py` integration boundary (schemas + env/FF lock + system/ligand hashes
  + artifact manifest + sign/unit validation + mocked artifact test + STUB-fails-in-execution); production MD
  engine + submitter DEFERRED until an executable MD env exists.
- **Req 6 (Plan C):** `rbfe_pilot.docking_preflight()` — the pre-registered pose/microstate preflight
  (construct frozen, repairs/protonation documented, ligand states enumerated, identical grid, MCS≥0.70,
  atom-map/param ok, no unresolved net-charge change, minimization without severe strain); output = INPUT
  STAGING only; 5-Br→5-NH2 flagged NOT gentle.
- **Req 7:** `cycle_closure_stance` — per-compound ddG_coop computed independently (not a P1-P5 edge tree);
  pilot hi-vs-lo preregistered nonredundant (no cycle-closure claim); redundant edge required before any
  relative-edge calibration network.
**SCORED PANEL NOW COMPLETE + FROZEN (2026-07-12).** MZ1's α was found **independently** in the primary OA
full text (Gadd 2017, PMC5392356 Table 1: *"the strongest cooperativity was observed for Brd4 BD2 (α = 18)"*)
— the independent VHL control, no reviewer transcription needed; the standard cis-Hyp inactive control was
added (VHL-binding knockout, no measured α). `expected_system_ids` populated with the 7 verified systems
(P1-P5 + MZ1 + inactive control); composition-valid; a gate test proves the real panel passes coverage.
Residual caveat recorded: MZ1 = Kd-derived ITC α vs SMARCA2 apparent α_TR-FRET → rank calibration only, no
cross-assay absolute-thermo claim; MZ1 PDB 5T35 RCSB auto-confirmation pending (transient RCSB error).
**Next execution steps** (not no-spend/testable, so not done this session): the **Plan-C docking job**
(authorized ~$5-15; needs an NR4A3 design-frame receptor staged + the preflight run) and the **Plan-B MD
engine** (deferred until an executable OpenFE/OpenMM env exists — the integration boundary is already built).

### Session progress on the 3 approved no-spend builds (2026-07-12)
**Testable pure cores for all three tracks are BUILT + committed** (81 tests across the ternary-coop modules;
full modalities suite 607+ passing):
- **Ternary harness core — `ternary_coop.py`** (13 tests): thermodynamic-cycle bookkeeping (`ΔΔG_coop =
  ΔΔG_ternary − ΔΔG_binary`, `α↔ΔG_coop`), the two SEPARATE read-outs (recruitment vs coupling), the frozen
  4-morph-leg PILOT_LEG_MAP, and `MODE=plan` (real GPU-h/cost forecast + $200-cap preflight; unit_gpu_h a
  labeled STUB). **Remaining:** the heavy OpenFE ternary FEP engine + spot-Training submitter (untestable in
  sandbox — build against staged inputs + the frozen calib pair).
- **Binary pilot core — `rbfe_pilot.py`** (14 tests): pilot edge resolution (5-Br→5-NH₂ + SMILES + design
  frame, from the frozen map), the pre-registered abort gate, and `MODE=plan`. **Remaining:** stage a
  design-frame receptor PDB + docked endpoint poses, + a single-frame engine/submitter path.
- **Layer-1 curation — `layer1_vhl_fetch.py`** (7 tests) + 3 CI fetch cycles (RCSB + Europe PMC, off-branch via
  `fusion-cpu-extras.yml`): **VERIFIED** a real SMARCA2-VHL PROTAC series (P1-P5; PDB 9HYN/9HYB/9HYO/9HYP;
  ordinal classes P1-P3 cooperative / P4 low / P5 negative; Nat Commun 2025 PMC12480974) + that paper's
  **MM-GBSA-no-correlation** result (the basis of the prereg's MM-GBSA-not-a-gate rule). Recorded in the
  prereg's `candidate_systems` workspace (scored `systems` stays EMPTY — no fabrication). **Remaining (well
  scoped):** exact NUMERIC α per compound lives in Fig 1A / Supplementary (resisted automated text+table
  extraction across 3 cycles → needs an SI-data-file parse or a figure read), + MZ1 numeric α + a verified
  inactive stereo control. This gates PRODUCTION ternary runs only (far downstream), NOT the harness build.

### ⚠ NEITHER authorized pilot is wired to launch yet — the 3 approved no-spend builds (turnkey detail)
The reviewer *authorized* both pilots (binary RBFE ~$5–15; ternary feasibility capped $200), but **neither is
runnable as-is** — all three are free engineering; **do NOT dispatch a GPU spend** until built:
1. **Binary RBFE pilot needs a small harness ADAPTATION, not just SMILES.** Endpoint SMILES are in hand:
   `zaienne_cmpd19` (A) = `COC(=O)c1c[nH]c2ccc(Br)cc12`; `cw_ev_5nh2` (B) = `COC(=O)c1c[nH]c2ccc(N)cc12`; edge id
   `e_zaienne_cmpd19__cw_ev_5nh2` (both neutral, 5-Br→5-NH₂, single-site). BUT `nr4a3_rbfe_sagemaker.py` +
   `rbfe_edges.py` are shaped for the OLD lead-opt readout (`denovo_401→lo_m0_NCCO`, 3-receptor selectivity,
   **401-ABFE anchoring**, `nr4a3-leadopt-species` prefix). The **pilot** per the RBFE-map plan is deliberately
   *different*: ONE `nr4a3_design` frame, the single edge, a **convergence/pocket-stability** test (NOT a
   selectivity readout, NOT 401-anchored). So: register the two SMILES + add a single-frame/single-edge pilot
   path (reuse the spot-Training + per-window-checkpoint plumbing), stage a design-frame receptor + docked
   endpoint poses, then `MODE=plan` (pure-local, no spend — calls `rb.edge_plan(...)` + `_cost_note()`), then
   the single-edge real run. Abort criteria already frozen (hysteresis ≤0.5; overlap ≥0.03; cycle closure ≤1.0;
   Pocket-5 survival ≥50%).
2. **The physics ternary-cooperativity harness does NOT exist.** Every `*ternary*` script (`nr4a3_ternary.py`,
   `nrv04_ternary.py`, `nr4a3_ternary_sagemaker.py`) is **Boltz co-fold only** (architecture) — no alchemical
   binary-vs-ternary FEP engine. Build one (mirror `nr4a3_fep_sagemaker.py`/`nr4a3_rbfe_sagemaker.py` spot +
   per-window-checkpoint plumbing) implementing `ΔΔG_coop = ΔΔG_alch,ternary − ΔΔG_alch,binary`. The ternary
   `MODE=plan` for the $200 bundle (prereg §5b; frozen legs `vhl_calib_hi_coop`/`vhl_calib_lo_coop`/
   `nrv04_active_binary_vhl`/`nrv04_epimer_binary_vhl`/`nrv04_active_nr4a1_ternary`/`nrv04_epimer_nr4a1_ternary`)
   is gated on freezing the exact Layer-1 pair (item 3) — so item 3 is its critical path.
3. **Layer-1 VHL calibration panel provenance = unfilled Stage-0 blocker AND the ternary-plan critical path.**
   `prereg.json → calibration.layer1_vhl_panel.{systems,expected_system_ids}: []`. Curate the SMARCA2-VHL series
   (+ an independent VHL system, **MZ1/BRD4 preferred**) compound IDs + PDB IDs + **measured α** from primary
   sources **via a CI-runner fetch** (egress proxy blocks PMC/EuropePMC/RCSB in-sandbox; use the
   `atlas-data.yml`/`fulltext_verify.py` pattern → commit raw text to a cache branch → curate). Candidate primary
   leads to VERIFY (do **NOT** enter unverified): Farnaby et al. 2019 *Nat Chem Biol* (SMARCA2 PROTAC ternary
   structures + cooperativity), Gadd et al. 2017 *Nat Chem Biol* (MZ1–BRD4–VHL, cooperative ternary). Flip each
   record's `verified` flag only from the fetched source; **do NOT fabricate α/PDB IDs.** The in-gate composition
   check (≥2 strong-coop, ≥2 weak/neg, ≥1 inactive control, ≥1 independent VHL) enforces the panel shape once
   filled.

## Pending the reviewer AI (fold its answer in first)
The decision block I sent asks: **Q1** which physics method + the minimum NR-V04 bar; **Q2** sequencing (binary
RBFE warheads first, or validate the ternary method against NR-V04 first — if it can't recover NR-V04
cooperativity, the whole thesis is in doubt); **Q3** budget (authorize the two pilots now — binary RBFE edge
~$5–15 and the NR-V04 cooperativity control pilot — and hold the full fleets for a second decision); **Q4**
whether "co-fold triage + a separate NR-V04-validated physics method → ordinal paralogue ranking" is a
sufficient architecture or is missing E3/Cullin-RING geometry, Lys-presentation/ubiquitination-compatibility,
linker-strain, or ensemble-vs-single-pose treatment.

## Hard constraints
- **No wet lab.** Every step is publish-to-convince or in-silico.
- **Spot GPU only**; real AWS $ is the only cost; **pilot one leg first**, wait out spot capacity, checkpoint
  continuously.
- **Honesty:** no fabricated data/affinities/numbers; co-fold stays triage-only; **denovo_401 is a benchmark**,
  promotable at most to "computational warhead candidate," **never "lead"**; **NR4A2 is the primary anti-target
  gate, NR4A1 provisional** (not statistically resolved).
- **Do NOT touch Track A / ABFE / the binder session's branch or S3 tags.**

## Infra quick-reference
- GPU ternary co-fold: `gpu-ternary-aws.yml` (inputs `git_ref=<your branch>`, `ternary_script`,
  `ternary_extra_args`, `seeds`, `output_prefix`); analyzer `report-nrv04-aws.yml` (reads an S3 prefix, commits
  the report to your branch). Monitor via `tail-cloudwatch-aws.yml` / `list-sagemaker-aws.yml`.
- **Run a new/edited CI off your feature branch WITHOUT merging to main:** dispatch an already-on-main
  `workflow_dispatch` with `ref=<your branch>` (and pass `git_ref=<your branch>` to SageMaker jobs so the
  container clones your code). Self-wake with a `run_in_background` bash poller on the public Actions API.
- Develop on your own feature branch off `main`; merge to main only when the user asks. `main` currently
  (commit `182dfec`) has the full session's work.
