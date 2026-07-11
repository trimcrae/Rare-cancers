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

### ⚠ Material finding for the NEXT builder — NEITHER authorized pilot is wired to launch yet
The reviewer *authorized* both pilots (binary RBFE ~$5–15; ternary feasibility capped $200), but **neither is
runnable as-is** — do NOT dispatch a GPU spend until these are built (all free engineering):
1. **Binary RBFE pilot edge is NOT wired.** `nr4a3_rbfe_sagemaker.py` + `rbfe_edges.py` are hardcoded for the
   OLD lead-opt edge (`denovo_401 → lo_m0_NCCO`, 3 fixed SMILES, `nr4a3-leadopt-species` receptor prefix). The
   authorized pilot edge is the **congeneric `zaienne_cmpd19` 5-Br → `cw_ev_5nh2` 5-NH₂** on one `nr4a3_design`
   frame. Needs: add the two congeneric SMILES + point at a design-frame receptor prefix with docked poses for
   both endpoints, then `MODE=plan` for the forecast, then the single-edge real run.
2. **The physics ternary-cooperativity harness does NOT exist.** Every `*ternary*` script (`nr4a3_ternary.py`,
   `nrv04_ternary.py`, `nr4a3_ternary_sagemaker.py`) is **Boltz co-fold only** (architecture) — there is no
   alchemical ternary/binary-vs-ternary FEP engine. Build one (mirror the spot-Training + per-window-checkpoint
   plumbing of `nr4a3_fep_sagemaker.py`/`nr4a3_rbfe_sagemaker.py`), then `MODE=plan` the $200-capped feasibility
   bundle (§5b of the prereg) for the required dry-run GPU-hour forecast BEFORE any production spend.
3. **Layer-1 VHL calibration panel provenance is an unfilled Stage-0 blocker.** `prereg.json →
   calibration.layer1_vhl_panel.systems: []` — the SMARCA2-VHL / MZ1 compound identities + PDB IDs + *measured*
   α must be curated from primary sources (via a CI-runner fetch, egress rule) and each marked `verified` before
   entering the scored panel. Do NOT fabricate α/PDB IDs.

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
