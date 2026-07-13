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
- **GCP preemptible/spot L4** — the **cheapest** option AND the big **$300** credit → intended **PRIMARY
  workhorse** for the RBFE legs + fleets. **OUR SIDE FULLY VALIDATED 2026-07-13:** keyless **Workload Identity
  Federation** auth (the org policy `iam.disableServiceAccountKeyCreation` blocks SA JSON keys, so WIF, not a
  key), `gcp-smoke.yml`, dynamic DLVM image lookup, VM provision command + teardown all pass. **BLOCKED on GCP
  quota:** the global `GPUS_ALL_REGIONS` quota is **0** and Google **DENIED** the increase (2026-07-13) because
  the project/billing account is brand-new — "wait 48h and resubmit, or until the billing account has history."
  → **Action: resubmit the `GPUS_ALL_REGIONS` request ~2026-07-15.** Until granted, GCP GPU is unavailable; the
  moment it lands, GCP just runs (everything else is ready). WIF provider = `projects/878095411563/locations/
  global/workloadIdentityPools/github-pool/providers/github-provider`; SA = `gpu-runner@project-a7ebde30-e2ed-
  4b8d-9a9.iam.gserviceaccount.com` (both non-secret, hardcoded in `gcp-smoke.yml`).
- **Vast** (key staged) / **Salad** (cheapest bulk) — spot-like, for bulk once needed.
- **Oracle $300** — later in the waterfall.

**★ REAL COST BASELINE (from the pilot's billing data, 2026-07-13 — supersedes the optimistic estimate).** The
pilot complex leg trained **30.0 GPU-h for ~6–7 of 12 windows** (`training_h`≈`wall-clock`, so it was genuinely
computing the whole time — **NOT a spot outage**; `billable_h`=10.0≈$10; the ~67% "savings" is just the flat
managed-spot discount, present on every job). So an alchemical RBFE **complex leg ≈ ~55 GPU-h** (~4.5 GPU-h/
window, ~2–3× the old "15–25 GPU-h/12-window" guess). Per-leg cost ≈ **~$11 GCP-L4-spot / ~$18 AWS-spot /
~$44 Modal**. **Consequence: a full complex leg does NOT fit Modal's $30 cap** — A1/A3 legs must go on GCP (or
Vast), not Modal. Bake this ~3× pace into the A3 fleet budget.

**Effective routing (2026-07-13):** tiny smokes only → **Modal** (<$1; a full RBFE leg is too big for $30). **A1
(both legs) → GCP spot L4** once quota lands (~$11/leg of the $300; quota resubmit ~07-15) — else **Vast**. **B1
smoke → Modal.** GCP is the primary workhorse for A3/B3. Confirm-before-launch still applies to A3/B3, now with
the corrected ~$18-AWS / ~$11-GCP per-complex-leg baseline.

**★ DIAGNOSED (2026-07-13, live CloudWatch probe `sm_gpu_util.py` on the running leg): the ~3× slowness is a
CPU BOTTLENECK, not heavy MD — the A10G is IDLE ~65% of the run.** 90-min window: **GPU util avg 29%** (0% for
~53 of 82 min, then 90-100%); **GPU mem 2-8%**; **CPU pegged ~100% (ONE core), occasionally 200%.** The long
0%-GPU / 100%-CPU stretch = **per-window single-threaded setup** (OpenFF ligand parameterization / charge gen /
hybrid-system build — the tracelog's "Generating residue template using openff-2.1.1"), repeated for each of 12
windows. **Consequences:** (1) we're paying for a mostly-idle GPU; (2) `g5.2xlarge` will NOT help — the bottleneck
is SINGLE-THREADED, so more vCPUs at the same per-core speed do nothing. **MECHANISM (confirmed in `nr4a3_rbfe.py`
`_protocol`):** OpenFE `RelativeHybridTopologyProtocol` makes each of the 12 λ-windows an independent ProtocolUnit
that RE-charges (NAGL) + RE-builds the hybrid system → 12× the CPU setup. **FIX (before A3; est. ~2-3× cheaper/
faster legs):** (a) compute the two ligands' partial charges ONCE and attach them to the `SmallMoleculeComponent`s
so every window reuses them (OpenFE skips regen when charges are present) — kills the repeated NAGL cost; (b) check
whether the per-window hybrid-system build / minimization is the residual CPU hog and whether it's cacheable / on
GPU. **Validate with a 1-window GPU smoke re-running `sm_gpu_util.py` (GPU-idle fraction should drop) BEFORE the A3
fleet.** Not blocking: the current leg finishes as-is (gives the `reduce`); A1 can run unoptimized (~$11-18/leg) or
wait for the fix; the fix's payoff is at A3 scale, so land + validate it before fanning out A3.

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
