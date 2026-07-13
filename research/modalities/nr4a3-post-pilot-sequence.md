# NR4A3 degrader — post-RBFE-pilot execution sequence (2026-07-13)

Ordered plan for what fires once the binary RBFE convergence pilot (`nr4a3-congeneric-rbfe`,
`zaienne_cmpd19` 5-Br → `cw_ev_5nh2` 5-NH₂, NR4A3, single design frame) lands its `reduce`. Two tracks run
in **parallel**: **A (binary warhead)** needs our compounds; **B (ternary method validation)** uses *known*
PROTACs and needs nothing from us. They converge only at prospective design (Step C).

**Framing note (recurring):** NR-V04 (Wang 2024, degrades NR4A1, spares NR4A2/NR4A3) is the **retrospective
positive CONTROL**, not the target. We recover its NR4A1-over-NR4A2/3 *degradation outcome* (no solved ternary
structure → functional recovery, not structural replication) to **validate** the ternary method, then design
NR4A3-selective degraders. NR4A2 = primary anti-target gate; NR4A1 provisional.

**★ PROVIDER POLICY (trimcrae, 2026-07-13 — no exceptions).** Wiring any harness to any provider via
`gpu_backend` is FREE engineering; real cloud $ is the only cost. **Burn free credits FIRST for EVERY GPU run
regardless of size — no "saving" for later (holding free credits while paying is pure waste).** AWS is used
ONLY to (a) finish a job already checkpointed there, or (b) a genuine AWS-only capability. The in-flight pilot
finishes on AWS spot because it is already running + checkpointed.

Provider facts + budgets (2026-07-13):
- **Modal** — wired + validated, but **NO spot tier** (per-second ON-DEMAND, ~3× AWS-spot/hr) and only **$30
  free credit**. → **Reserve Modal for cheap validation/smokes + single small legs.** RULE: **never launch a run
  on Modal projected to exceed $30** (forecast from the pilot `reduce`'s calibrated `unit_gpu_h` BEFORE launch).
- **GCP preemptible/spot L4** — the **cheapest** option AND the big **$300** credit → the right home for the
  actual RBFE legs + fleets. **Quota PENDING approval** (4× L4 + 4× T4 spot, us-central1).
- **Vast** (key staged) / **Salad** (cheapest bulk) — spot-like, for bulk once needed.
- **Oracle $300** — later in the waterfall.

**Effective routing:** cheap smokes/single-shard shakeouts → **Modal** ($30, don't exceed). Real RBFE legs +
all fleets → **GCP spot L4** when quota lands (cheapest + $300); until then, at most ONE RBFE leg fits Modal's
$30, so run the pilot-first leg (NR4A2) there only if its calibrated forecast is < $30, and hold the rest for
GCP/Vast rather than blowing the cap or silently paying AWS. Confirm-before-launch still applies to the
EXPENSIVE fleets (A3, B3).

## Step 0 — read the pilot verdict (when both legs Complete) — AUTONOMOUS
`gpu-rbfe-aws.yml mode=reduce` (tag=nr4a3-congeneric-rbfe, ligand_a=zaienne_cmpd19, ligand_b=cw_ev_5nh2,
only_legs=solvent,complex-nr4a3, receptor_prefix=nr4a3-congeneric-dock/congeneric-poses2-ckpt).
→ ΔΔG_bind + 4 frozen abort checks (hysteresis ≤0.5, adjacent-λ MBAR overlap ≥0.03, cycle closure ≤1.0,
Pocket-5 survival ≥50%) + the **real `unit_gpu_h`**.
- **GATE:** any abort check fails → rework binary RBFE for this rigid indole series (more windows / soft-core
  tail / alt frame) before ANY wider spend. Pass → proceed.
- `unit_gpu_h` here **recalibrates every downstream cost forecast** (fixes the ~$288 ternary over-forecast).

## Track A — binary warhead qualification (needs our compounds)
- **A1. Paralogue counter-screen on the qualified edge.** Same 5-Br→5-NH₂ edge on **NR4A2 first** (primary
  anti-target), then **NR4A1**, in matched LBD frames. Solvent leg is ligand-only → **reused** from the pilot,
  so each paralogue = ONE complex leg. NR4A2 first = highest abort info. → per-edge relative paralogue signal
  (ΔΔΔG). Cheap; autonomous if `unit_gpu_h` confirms small.
- **A2. Frame robustness.** Repeat the edge on ≥1 more defensible NR4A3 frame (conclusions must survive >1
  frame). Cheap.
- **A3. Warhead matrix.** RBFE across the congeneric Zaienne-19 series (8 exit-vector 5-subs + 5 carboxylate
  bioisosteres; `needs_pose_revalidation` edges re-docked first), NR4A3 primary, survivors counter-screened on
  NR4A2/NR4A1. → warhead set retaining NR4A3 affinity without strong paralogue preference.
  **EXPENSIVE FLEET → trimcrae go-ahead + provider named in advance.**
  Honest caveat: RBFE gives *relative* per-edge selectivity; *absolute* warhead paralogue selectivity needs the
  ABFE anchor (separate binder-session ABFE-repair track). A1–A3 = coarse counter-screen, not the final verdict
  (by design — real selectivity lives in ternary).

## Track B — ternary method validation (known PROTACs; parallel to A)
- **B1. Harness smoke.** GPU `MODE=smoke` on `nr4a3_ternary_fep` (openfe env + ternary assembly + hybrid
  topology); stage inputs via `ternary_fep_stage.stage_from_cofold` on real co-fold outputs (CPU/CI). Cheap;
  autonomous.
- **B2. Quantitative VHL calibration FIRST (the real pilot leg).** Freeze the Layer-1 hi/lo pair (SMARCA2 PROTAC
  **P1 α≈93 vs P5 α≈0.6**, crystallographic 9HYN/9HYP) and run that ONE ΔG_coop leg.
  **GATE (highest abort information in the program):** if the method can't reproduce the sign/ordering of a
  *measured* cooperativity gap (93 vs 0.6), the ternary thesis is in doubt → STOP before NR-V04/NR4A3.
- **B3. NR-V04 retrospective control.** Only if B2 passes. NR-V04 ternary arm (endpoints from `nrv04_ternary`):
  does ΔG_coop recover **NR4A1 > NR4A2/NR4A3**? Include the **VHL-inactive hydroxyproline epimer as the negative
  functional control**. Run the single most decisive leg first (NR4A1 positive or epimer negative).
  **GATE:** `ternary_coop_gate.py` enforces frozen §3. Recover NR-V04 selectivity → method trusted; fail to
  recover → honest refutation, recorded. **EXPENSIVE FLEET (~$200-cap, recalibrated by Step 0) → trimcrae
  go-ahead + provider named** (propose Modal free-credit legs for validation, cheapest bulk provider after).

## Step C — prospective NR4A3 designs (GATED on B3 passing)
Build the **warhead × linker × E3 matrix** (VHL-first, CRBN held); rank by the *validated* ternary method + the
4 architecture layers (ensemble/linker-strain; Cullin-RING/E2~Ub lysine presentation; fusion-context;
ensemble-vs-single-pose). **Boltz + DeepTernary** (Step-3 qualification running now) feed *architecture
proposals* (union of clusters), never the ranker. → synthesis-ready ~6–12-compound matrix (the deliverable).

## Critical path
`pilot reduce (0) → [ A1 NR4A2 counter-screen ‖ B1 smoke → B2 VHL-calib gate → B3 NR-V04 gate ] → C matrix`
NR-V04 recovery = **B3**, a validation gate, not the endpoint.

## trimcrae confirmation points (expensive; provider named in advance)
- **A3** warhead RBFE fleet.
- **B3** NR-V04 ternary fleet.
Everything through the **B2 single calibration leg** is autonomous (cheap / single-leg-first).
