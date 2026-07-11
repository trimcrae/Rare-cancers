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

## Your immediate next step (self-doable, free — do it before any GPU)
**Preregister a physics-based ternary-cooperativity method + its NR-V04 cooperativity control**, mirroring
`nr4a3-abfe-repair-prereg.md`. Candidate methods to choose among (see the reviewer's answer): (i) ternary-complex
MD stability + interface MM-GBSA; (ii) relative ternary binding free energy on the interface; (iii) cooperativity
α via a binary-vs-ternary thermodynamic cycle. **Retrospective bar it must clear before ANY prospective NR4A3
run:** recover NR-V04's *cooperativity* ordering (NR4A1 productive, NR4A2/NR4A3 not) AND **reject the inactive
epimer** — the two things the co-fold could not do.

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
