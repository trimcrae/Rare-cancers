# NR4A3 congeneric-warhead RBFE perturbation map — design spec

**Status: DESIGN ONLY (2026-07-11).** No MD/FEP/GPU/AWS/network was run. No affinity, ΔΔG, GPU-hour, or
convergence is asserted here — every energetic and cost quantity is a placeholder marked *TBD — calibrate from
the pilot*, and the abort thresholds are **pre-registered** design parameters (decided a priori), not results.

- **Generator:** [`research/modalities/rbfe_map.py`](../modalities/rbfe_map.py) (pure stdlib) → emits
  [`research/modalities/congeneric-rbfe-map.json`](../modalities/congeneric-rbfe-map.json). Tests:
  `research/modalities/tests/test_rbfe_map.py` (17 passing).
- **Inputs (read, not re-derived):** `congeneric-warhead-series.json` (the 19 congeneric NODES) +
  `nr4a3-conformer-panel.json` (the frozen receptor-state AXIS).
- **Strategy context:** `nr4a3-degrader-strategy-ternary-first.md` §2 — congeneric **relative** binding free
  energy is the primary quantitative tool; ABFE is demoted to secondary calibration; the deliverable is a
  synthesis-ready matrix that feeds the existing ensemble scorer.

## Why RBFE, and why a graph
Within a congeneric series the affinity *difference* between two analogues that share a binding-mode-preserving
core is a small alchemical morph in which the shared scaffold cancels by construction — far more tractable and
lower-variance than the absolute binding of unrelated scaffolds (the denovo_401 ABFE problem). So the map is a
**graph**: nodes are congeneric analogues, edges are single-site perturbations that preserve the common binding
mode. The map does **not** introduce a new scorer — its per-(receptor, conformer) ΔΔG endpoints feed
`ensemble_robust_score.py` (`robust_score` / `beats_benchmark` / `advancement_verdict`), reusing the frozen
worst-conformer objective and the `|receptor effect| > |conformer effect|` criterion.

## Topology — two anchor-rooted stars + cycle closures (19 edges over 17 in-map nodes)
Anchor = `zaienne_cmpd19` (methyl 5-bromoindole-3-carboxylate; functional target engagement only).

- **5-position star (`star_5position`, well-behaved backbone).** Anchor → each 5-substituent. Small single-site
  swaps at the hypothesized linker exit vector. **9 spokes** = 8 `exit_vector_sub` + the neutral `5-NHAc`
  `microstate_variant`. `common_mode_risk` low (larger/charged handles — propargyl-ether, piperazine,
  PEG-amine — flagged medium). `needs_pose_revalidation=false`.
- **3-position star (`star_3position`, higher-risk).** Anchor → each replacement of the SAR-critical
  3-carboxylate H-bond. **7 spokes** = 5 `bioisostere` + the `3-CO2H` and `3-CH2OH` `microstate_variant`s.
  A carboxylate→tetrazole/amide swap can shift the pose, so **every** edge in this star is
  `needs_pose_revalidation=true` (an endpoint pose check gates trusting the ΔΔG — RBFE alone is not enough);
  8 edges total carry this flag.
- **No cross-class double-mutation edges** (two simultaneous changes break the common-mode assumption). Every
  edge is `single_site=true`.
- **Comparators are a separate, non-congeneric node set.** The 3 `denovo_401` comparators get **ABFE (absolute)**
  as secondary calibration (anchored on `nr4a3_rbfe.py` `ANCHOR_401_ABFE`), **not** RBFE edges into the indole
  series — the common-mode assumption is invalid across scaffolds. Recorded as `denovo401_gets_abfe_not_rbfe:
  true`; the validator rejects any RBFE edge touching a comparator.

**Cycle closure (internal consistency / convergence check).** Three closed triangles, each a spoke pair plus one
extra **single-site** closing edge between two non-anchor analogues (so still no double mutation):
`cycle_exitvector_aniline` (5-NH₂ → 5-NHAc, acetylation), `cycle_exitvector_ether` (5-OH → 5-O-propargyl),
and `cycle_3carbonyl` (3-CO₂H → 3-CONH₂, in the risky 3-position region on purpose). Constraint: the signed
ΔΔG around each loop must sum to ~0 within `cycle_closure_kcal_max` (1.0 kcal/mol) — a convergence/consistency
diagnostic independent of any absolute reference.

## Receptor-state axis (per edge)
Frames are referenced by **panel role**, not fixed indices — indices resolve at panel-build time from the
conformer panel's `selection_rules` / `pocket_tracking.py`.
- **Pilot:** one `nr4a3_design` frame only.
- **Fleet:** `nr4a3_validation` (held-out druggable 8XTT models — the compelling test — plus release held-out
  ranks 4–6) + matched `nr4a1_antitarget` + `nr4a2_antitarget` frames (NR4A2 is the hardest paralogue to
  spare; I531 conserved).
- **Selectivity readout per edge, per conformer:** ΔΔG_bind(NR4A3 frame) − ΔΔG_bind(paralogue frame). Rank by
  the **worst conformer**; trust a preference only when `|receptor effect| > |conformer effect|`.

## Microstates
The 7 `microstate_ambiguous` compounds each carry **both** dominant pH-7.4 species as separate legs, so a
protonation flip cannot silently move ΔΔG. Legs are the cartesian product of the two endpoints' species (27
legs total across the map); a leg whose net charge changes (e.g. neutral acid → anionic carboxylate) is
**flagged** so the pipeline applies the co-alchemical / analytical charge correction.

## Pose uncertainty (first-class caveat)
Compound 19 has **no solved NR4A3 pose** (functional engagement only), so the 5-position exit-vector assignment
is a **hypothesis**. The map treats the binding pose as an **ensemble input** — every edge is scored across the
conformer panel and never against a single fixed pose; a result that survives in only one frame is treated as a
geometry artefact by the worst-conformer objective.

## The pilot edge (highest abort information)
**`e_zaienne_cmpd19__cw_ev_5nh2` — 5-Br → 5-NH₂**, both endpoints neutral, a small single-site perturbation on
**one** `nr4a3_design` frame. The crux question the pilot answers is **not** "is compound X selective" but
**"can a congeneric RBFE even converge on this dynamic, low-population cryptic pocket without the pocket
collapsing during the alchemical MD?"** — so the pilot is deliberately the *most well-behaved* perturbation, to
isolate the convergence/pocket-stability question from chemistry difficulty.

**Pre-registered ABORT criteria** (all TBD-tunable design parameters; the pilot must pass **all** before any
fleet edge is scheduled):
- **Hysteresis** `|ΔG_forward − ΔG_reverse| ≤ 0.5 kcal/mol` per leg (else not converged).
- **Overlap** min adjacent-λ MBAR phase-space overlap `≥ 0.03` (else window spacing insufficient).
- **Cycle closure** `|Σ ΔΔG| ≤ 1.0 kcal/mol` around any closed loop.
- **Pocket survival** the harmonized Pocket-5 lining (fixed lining set; fpocket 4.0; D*=0.53;
  `pocket_tracking.py`) remains detected in `≥ 50%` of alchemical windows, and the Pocket-5 volume does not
  fall below the apo-open reference across >half the windows.

**If the pilot fails to converge or the pocket collapses, the RBFE-primary strategy is called into question**
on this cryptic pocket — halt, do **not** fan out the fleet, and escalate as a strategy fork. On success,
calibrate per-edge `n_windows` / GPU-h from the pilot (they are `null`/TBD in the JSON until then) and schedule
the fleet.

## Design decisions I was unsure about
- **Folding `microstate_variant` compounds into the two stars by perturbation SITE** (5-NHAc → 5-position star;
  3-CO₂H / 3-CH₂OH → 3-position star) rather than giving them a separate graph. They are genuine single-site
  changes off the anchor, so this keeps the map a clean two-hub topology; the edges retain
  `class: "microstate_variant"` so the by-class counts stay honest. An alternative was a third isolated star.
- **`n_atoms_changed` is a curated approximate heavy-atom count of the alchemical region**, explicitly labeled
  as such — the authoritative value is the RDKit/LOMAP MCS at map-build time (this generator is stdlib-only, so
  it cannot compute an MCS). Emitted alongside a coarse `heavy_atoms` sanity metric per node.
- **Charge-changing microstate legs are kept but flagged** rather than dropped; whether to run them as
  co-alchemical (counterion) or analytical-correction legs is left to the pipeline, since that is an engine
  choice, not a map-topology choice.
