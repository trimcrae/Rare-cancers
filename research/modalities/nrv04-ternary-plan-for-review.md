# NR-V04 ternary workflow — plan for external review (2026-07-11)

Status snapshot for the reviewer AI before any further GPU spend. All work below is committed to `main`.

## 1. Where Track B actually stands (after applying the previous review's fixes)
- The retrospective NR-V04 benchmark (degrades NR4A1; spares NR4A2/NR4A3) is now read with a **moiety-specific**
  contact test (celastrol end→NR4A **and** VH032 end→VHL, split by the ligand's single sulfur), not the earlier
  whole-ligand min-distance test.
- **Corrected result (n=3 seeds, 1 model each):** NR4A1 moiety-bridges **2/3** (the whole-ligand test's 3/3
  over-counted one **wrong-end artefact**); NR4A2/NR4A3 **0/3**. Separation is robust across 4.0/4.5/5.0 Å and
  survives leave-one-seed-out. ligand-iPTM does NOT reproduce the ordering (higher for spared NR4A2). Verdict:
  **exploratory concordance, thin (n=3)** — NOT validation.
- **Negative-control shakeout (n=4; the decisive new finding):** free celastrol (no VHL handle) correctly fails
  to bridge (0.0); but the **VHL-inactive hydroxyproline-epimer PROTAC bridges NR4A1 exactly like active NR-V04
  (0.75 vs 0.75)**. A co-fold predicts a *structure*, not affinity, so the geometry readout **captures gross
  productive-geometry specificity but is blind to a fine stereochemical binding-affinity knockout**.
  `negative_controls_pass = False`.

## 2. The implication I want reviewed
The negative control means the ternary geometry readout is usable for **architecture triage** ("can this linker
geometry bridge the two proteins at all?") but **NOT for affinity/binding ranking** of prospective linkers — a
well-placed non-binder scores the same as a real binder. Under the frozen criteria this **blocks a geometry-only
prospective NR4A3 linker-ranking campaign**. Binding would have to come from a separate method (recruiter
FEP/ABFE, or docking), not the co-fold.

## 3. Infra correction (independent of the science)
`nr4a3_ternary_sagemaker.py` runs Boltz as an **on-demand `FrameworkProcessor` (Processing) job**, which
violates the standing "default every GPU run to managed spot" directive. It is convertible to a **spot Training**
job (like `nr4a3_md_release_sagemaker.py`; per-seed continuous S3 upload already makes it interruption-safe),
saving ~60–70% real $ and freeing the on-demand slot. **This should be done before any re-run.** (Track A's ABFE
is already spot-correct.)

## 4. Proposed plan (nothing runs until you/the reviewer approve the GPU items)
1. **[engineering, $0] Convert the ternary job to spot Training** (`use_spot_instances`, `max_wait ≥ max_run`,
   `checkpoint_s3_uri` = the per-seed output prefix). Validate plumbing with a smoke shard.
2. **[GPU, ~$3–5 on spot] Re-run the corrected NR-V04 benchmark on spot** at expanded sampling (≥5 seeds ×
   ≥3 poses) with the two negative controls, frozen criteria. Confirms (a) the paralogue separation at robust n
   and (b) the epimer-blindness finding is not a small-sample fluke.
3. **[decision, not spend] Resolve the strategic fork below**, then — only if approved —
4. **[GPU, capped] a small prospective pilot**: 2–3 chemically diverse candidate NR4A3 linkers × 3 paralogues,
   scoring rule frozen before opening NR4A3 results, **geometry triage paired with a separate recruiter-affinity
   check** (per the fork).

## 5. Strategic fork for the reviewer to advise on
Given geometry can't see affinity, how should prospective NR4A3 linker evaluation proceed?
- **(A) Two-stage:** geometry triage (ternary can-it-bridge) → then recruiter/warhead **affinity** by a separate
  method (FEP/ABFE or docking) on survivors. More defensible; more compute.
- **(B) Geometry-triage only, explicitly labeled** as architecture screening, no affinity claim. Cheap; weaker.
- **(C) Hold prospective work** until an affinity-capable ternary method is available; keep the benchmark as a
  documented negative/limitation only.

## 6. Specific questions
1. Is the exploratory-concordance framing + the epimer-blindness limitation now stated correctly and
   conservatively enough for the manuscript?
2. Is re-running the corrected benchmark on spot (item 2, ~$3–5) worth it, or is the shakeout finding already
   sufficient to record without a robust-n confirmation?
3. Which fork (A/B/C) for prospective work?
4. Should Track A's ABFE r1 (already spot, ~15 h left, ~$-authorized) keep running, or pause it too while this is
   reviewed? (It is unrelated to the ternary spend and would lose ~4 h of checkpointed progress if killed.)
