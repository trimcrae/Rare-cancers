# De-novo NR4A3 warhead — design campaign, screen, and the candidate (matrix step 3)

**Status: pipeline BUILT, idle pending the pocket gate (2026-06-29).** This is the route's one genuinely
missing piece — a *designed*, NR4A3-selective warhead rather than a repurposed tool compound. The matrix
(`nr4a3-matrix-result.md`) showed the specific repurposing leads are within docking noise and the headline
hit (cytosporone B) reverses under MM-GBSA; a bona-fide selective candidate has to be *designed* against
the opened pocket. This doc is the design-campaign spec + result home (mirrors `nr4a3-matrix-result.md`).

## The minimal-compute funnel (why it is cheap)
Generation is cheap; FEP is what's expensive, and candidates do not come from FEP. So the path to the
first candidate spends GPU only **twice**, keeps the whole middle on free CPU, and keeps FEP out entirely.

| Stage | Where | ~Cost | Tool / script |
|---|---|---|---|
| 1. Generate | **GPU** (1 short run, post-gate) | ~$1–3 | DiffSBDD on the opened NR4A3 pocket; `nr4a3_denovo.py MODE=generate` (`gpu-denovo-aws.yml`) |
| 2. Screen | **GitHub CPU** (free) | $0 | novelty (ECFP) → developability (RDKit) → smina dock into 3 opened pockets → `selectivity_fingerprint` → PROTAC handle; `nr4a3_denovo.py MODE=screen` (`denovo-screen.yml`) |
| 3. Confirm | **GPU** (1 × ~25 min, post-gate) | ~$0.5–0.7 | the **existing** MM-GBSA tier, unchanged, on the shortlist; `mmgbsa-aws.yml` with `input_prefix=nr4a3-denovo` |
| 4. (deferred) | GPU, optional | — | ternary geometry (`nr4a3_ternary.py`) + single-ligand selectivity FEP on the one confirmed lead |

**The candidate** = a generated molecule that is `confirmed_selective` (MM-GBSA) ∧ developable ∧
PROTAC-assemblable. Two campaigns, **selective-first** (the EMC lead): the `selective` campaign conditions
DiffSBDD on the 5 engageable divergent handles (L406/T410/I484/I531/L534); the `pan` campaign conditions
on the conserved Pocket-5 CV residues. Both come from one generation job; the screen costs the same either
way (free CPU), so both are run.

## Two unavoidable GPU runs, gated
- **Generation** and **MM-GBSA** are the only GPU spends; both are **gated behind the unbiased release run**
  (`gpu-release-aws.yml`) — designing/quantifying against a confirmed-metastable pocket, not a biased-MD
  artifact (the design spec's rule; the release run is in flight in a separate thread as of 2026-06-29).
- Per the standing rule, each GPU dispatch goes through an `AskUserQuestion` cost/payoff pop-up first.

## How to run (once the gate clears)
1. **Generate (GPU, ask first):** dispatch `gpu-denovo-aws.yml` with `diffsbdd_repo` + `diffsbdd_ckpt_url`
   set (DiffSBDD is operator-provided — no model URL is committed; absent → generation skips gracefully).
   Writes `s3://<bucket>/nr4a3-denovo/nr4a3-denovo-pool.json` (+ generated SDFs).
2. **Screen (free CPU):** dispatch `denovo-screen.yml`. It stages the pool + the three `<tag>-opened.pdb`
   + the metad manifests from S3, docks with smina, gates with RDKit + `denovo_select`, then uploads
   `nr4a3-denovo.json` + the shortlist-only MM-GBSA handoff (`<tag>-opened.pdb`, `docked_<tag>.sdf`,
   matrix-shaped `nr4a3-matrix.json`) back to `s3://<bucket>/nr4a3-denovo/`, and publishes
   `nr4a3-denovo.json` to the `modalities-cache` branch. Read it any time via `report-denovo-aws.yml`.
3. **Confirm (GPU, ask first):** dispatch `mmgbsa-aws.yml` with `input_prefix=nr4a3-denovo` (the handoff is
   in the schema the MM-GBSA job already reads). A shortlist molecule returning `confirmed_selective` is
   the designed candidate. Read via `report-mmgbsa-aws.yml`.

## What the code is (built + unit-tested now, CPU-only)
- `denovo_select.py` — **pure** novelty/developability gates + screen-pass verdict + ranking (no deps;
  10+ tests in `tests/test_denovo_select.py`). Reuses `selectivity_fingerprint.classify`.
- `nr4a3_denovo.py` — the two-mode driver. `generate` wires DiffSBDD (guarded, lazy); `screen` reuses the
  proven matrix machinery (`nr4a3_matrix.box_for`, `nr4a3_warhead.dock_into/handle_contacts`,
  `warhead_chem_profile.profile`) and emits the MM-GBSA handoff. The old `nr4a3_warhead.generate_denovo()`
  stub now delegates here.
- SageMaker glue `nr4a3_denovo_sagemaker.py` + `sagemaker_src/entry_denovo.py` (DiffSBDD env pinned, conda
  lock captured, heartbeat/timeout/fail-fast hardening from the MM-GBSA run-7 incident).
- Workflows `gpu-denovo-aws.yml` (GPU generate), `denovo-screen.yml` (free CPU screen), `report-denovo-aws.yml`.

## Honest bounds (red-team standard)
- Generated SMILES are **model-generated, novel** structures (the screen rejects anything with ECFP4
  Tanimoto > 0.40 to a known NR4A active) — never presented as literature compounds.
- The candidate is an **in-silico design hypothesis**, not a validated warhead: docking dG is a screening
  prior; the MM-GBSA verdict is direction-only (single-snapshot, no entropy — inflated magnitudes); the
  pocket is biased-MD-opened (Gate 1 basin-breathing only, Gate 3 provisional). The full quantitative tier
  is FEP, deferred to the one confirmed lead.
- **Binding selectivity ≠ degradation selectivity** — the ternary step (`nr4a3_ternary.py`) is where
  degradation selectivity is set. Terminal blockers stay wet-lab: synthesise; prove binding/degradation;
  prove EMC fusion-addiction via dTAG. See the consolidated roadmap in `nr4a3-degrader-design-spec.md`
  → "Remaining in-silico roadmap → wet-lab handoff".
