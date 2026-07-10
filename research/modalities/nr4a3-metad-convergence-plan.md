# NR4A3 metadynamics convergence — data verification + in-silico re-strengthening plan (2026-07-10)

## 0. Numbers verified against the actual data (not the paper text)

The round-6 reviewer's convergence numbers were checked against the source files, and they are **all faithful**:

| Quantity | Reviewer / paper | Source file | Verdict |
|---|---|---|---|
| basins Rg (r1/r2/r3) | 0.87 / 0.73 / 0.74 nm | `nr4a3-metad-crossreplica.json` | ✓ |
| ΔF at ref Rg≈0.72 (r1/r2/r3) | 16.03 / 0.06 / 0.83 kcal/mol | `nr4a3-metad-crossreplica.json` | ✓ |
| block drift 10→20 / 20→30 ns | r1 29.1→13.9, r2 31.3→15.2, r3 16.5→17.6 kJ/mol | `metad-analysis-r*/…summary.json` | ✓ (paper "29→14/31→15/16→18") |
| late-block drift → kcal | 14–18 kJ/mol ≈ 3.3–4.3 kcal/mol | derived | ✓ |
| corr(Rg, gate) | 0.943 / 0.96 / 0.94 | `…summary.json orthogonal` | ✓ |
| recrossings | r1=3 (41 visits), r3=0 (360 visits), r2 n=1 → not reported | `…summary.json recrossings` | ✓ (r2 really is 1 sample) |
| production length | 30 ns/replica (×3) | `block_end_ns` | ✓ |
| ABFE ΔG_bind (3/1/2) | 3.5 / 8.3 / 8.5 kcal/mol | `nr4a3-abfe-diagnostics.json` | ✓ |
| ABFE ΔΔG (3−1 / 3−2) | −4.76 ± 2.03 / −4.98 ± 0.68 | `nr4a3-abfe-diagnostics.json` | ✓ |
| release persistence | 3/3 held 5 ns, drift 0.025 nm, ~24 % druggable | `nr4a3-degrader-next-steps.md` | ✓ |

**One paper error found in the check (now fixed, commit 041ba57):** the recrossing event *definition* does
exist in the data (boundary Rg = 0.9 nm, **5σ hysteresis deadband**, window [0.7, 1.1]); the round-6 text had
said thresholds were "not yet specified."

**Bottom line on the science (agreeing with the reviewer):** the ~0.6 kcal/mol opening-cost claim is
**falsified, not merely uncertain** — three seeds assign 16.03 / 0.06 / 0.83 kcal/mol to the same reference
Rg, and late-block drift (3.3–4.3 kcal/mol) alone dwarfs the original 0.6. `denovo_401` is **not killed** by
this: its evidence (design-frame endpoint scores, decoy-null clearance, conditional ABFE ≈ −5 kcal/mol) does
not require the 0.6 number. What dies is the *equilibrium-accessibility* claim.

## 1. Can it be re-strengthened in silico? — Yes, but re-target the question

Do **not** aim to "converge the 0.6 kcal/mol opening cost." That quantity is (a) dead and (b) not the
decision-relevant one for a *selectivity* paper. The decision-relevant quantity is the **paralogue-differential
opening free energy**, because the honest full selectivity is

  ΔΔG_full(3−2) ≈ ΔΔG_bind^open(3−2) + [ΔG_open,3 − ΔG_open,2]

Our conditional term is ΔΔG_bind^open(3−2) ≈ **−4.98 kcal/mol**. If NR4A3's opening penalty exceeds NR4A2's by
≈ +5 kcal/mol, the selectivity vanishes; larger, it reverses; smaller/favourable, it survives or improves. We
currently do not know the sign of that bracket. **Estimating that differential (not a single absolute opening
cost) is the win.** This is also why the fix is a *new axis of evidence* (breadth-first default-yes), not
"more of the same Rg-metad" (depth, default-no).

Root-cause triage (reviewer's A/B/C), with our data:
- **B — Rg is an incomplete CV — is the leading suspect.** The only orthogonality check (gate distance) is
  0.94–0.96 correlated with Rg, i.e. nearly redundant; it cannot detect a hidden slow mode. Just adding ns to
  the 1-D Rg metad (cause A) may not fix a projection problem.
- **C — heterogeneous opening** is plausible (basins at 0.73/0.74 vs 0.87 nm are materially different
  geometries). A single 1-D coordinate then projects poorly.

## 2. Staged plan (breadth-first; each stage gates the next; acceptance criteria fixed up front)

### Phase 0 — CHEAP / CPU / prerequisite (fold into the already-gated harmonized rerun)
**Per-replica harmonized pocket scoring on the 3 metad replicas + 3 release replicas.** For each replica,
apply the score-independent orthosteric matcher per frame and ask: does a *matched, ≥D\** cavity-bearing
sub-ensemble exist, and at what CV values? Deliverables: (i) whether the "druggable state" exists independently
in each replica (tests the reviewer's "same physical state?" doubt), and (ii) a **structure-defined druggable
region** to measure free energies *to*, replacing the fixed-Rg proxy. Cost: ~0 extra (fpocket; part of the
reharmonize job). **Gate:** if a matched druggable cavity is *not* found per replica, the pocket claim weakens
independently of convergence — report honestly.

### Phase 1 — CHEAP / analysis of EXISTING trajectories: find the true slow CV
Run **TICA / deep-TICA (and/or SGOOP)** on the pooled existing metad + release trajectories (features: pocket
Rg, lining-residue pairwise distances, gate-residue χ1/χ2, pocket SASA, cavity hydration count). Deliverable:
the actual slow coordinate(s) of opening, and whether Rg is a faithful projection or a lagging one. Cost:
single-digit GPU-h / CPU (no new MD). **Gate:** if a non-redundant slow mode dominates, Phase 2 biases *it*;
if Rg turns out adequate, Phase 2 is just better-sampled Rg-metad.

### Phase 2 — THE CORE / GPU (needs sign-off; this is the expensive leg): opening FE on the improved CV, all 3 paralogues
Compute the **opening free energy** along the Phase-1 CV with a method chosen for a clean, checkable PMF —
**well-tempered metad OR umbrella sampling + MBAR/WHAM** — ≥3 independent seeds, run to the **field-standard
convergence criterion fixed here in advance**:
  (a) last-third block-to-block drift < ~1 kcal/mol, AND
  (b) independent replicas agree within ~1–2 kcal/mol on the basin→druggable-region ΔF, AND
  (c) recrossing on the improved CV (diffusive sampling).
Run the **identical protocol on NR4A1 and NR4A2** so the **differential** ΔG_open,3 − ΔG_open,{1,2} is obtained
on a matched footing. This is the state-of-the-art move (a new evidence axis: paralogue opening thermodynamics).

**Concrete Phase-2 design + cost (for sign-off):**
- **CV:** the Phase-1 TICA IC1 (data-derived), exported as a PLUMED-biasable linear combination of the same
  features (lining Cα distances + gate χ1 sin/cos + SASA), NOT Rg. Well-tempered metad (bias factor ~10–15).
- **Fleet:** 3 seeds × 3 paralogues (NR4A1/2/3) = **9 enhanced-sampling runs**, ~50 ns each (longer than the
  30 ns Rg runs, to buy recrossing on the better CV given the ~17 ns slow timescale).
- **Hardware/cost:** `ml.g5.xlarge` **managed spot Training** (checkpoint/resume per the compute rules), which
  draws on the spot-Training quota (8), so up to 8 legs run concurrently. ~50 ns of OpenMM+PLUMED on an A10G
  for this ~88k-atom box ≈ ~1 GPU-day/run → ~9 × ~24 GPU-h ≈ **~215 GPU-h**. Spot ≈ **$100–200** total;
  wall-clock **~2–3 days** on the K≤8 fleet. (On-demand would be ~3× and serial — do NOT.)
- **Shard-first gate (mandatory, per the fan-out rule):** run **one seed of NR4A3 only** first (~$15–25,
  ~1 day) to prove the TICA CV is correctly PLUMED-wired and actually drives opening/recrossing, THEN launch
  the remaining 8. The shakeout's completed windows are not wasted (continuous checkpoint → the fleet resumes).

**Serialize/spot per the compute rules; the full 9-run fleet is the expensive, multi-leg leg → bring this cost
estimate back for sign-off before launching (the single-shard shakeout is inside the cheap-autonomy band).**

### Phase 3 — state-correct the selectivity (decisive, either way)
Combine: **ΔΔG_full(3−2) ≈ ΔΔG_bind^open(3−2) + [ΔG_open,3 − ΔG_open,2]** (and 3−1). Outcomes are all
publishable: differential small/favourable → conditional selectivity survives and the paper is materially
stronger (no converged-0.6 needed); differential large/unfavourable → selectivity is state-limited, stated
honestly. Optional robustness: **ensemble ABFE** for `denovo_401` across several independently-justified
cavity-bearing frames per receptor (does the sign hold, or is it a single-snapshot artifact?).

## 2b. Phase 0 + Phase 1 RESULTS (2026-07-10, both complete; numbers verified from job logs)

**Phase 0 — per-replica harmonized pocket scoring (WTMetaD r1/r2/r3; fpocket 4.2.3 pinned, harmonized
matcher, D\*=0.53).** Run 29113366857 (job 86430750933), `metad-replica-pocket-summary.json`.

| Replica | detfrac | druggability max / mean | frac≥0.5 / frac≥D\*(0.53) | crosses 0.5? | cheapest druggable frame (Rg, drug, F(Rg)) |
|---|---|---|---|---|---|
| r1 | 1.0 | 0.921 / 0.362 | 0.36 / 0.36 | yes | Rg=0.753 nm, drug=0.863, **F=11.72 kcal/mol** |
| r2 | 1.0 | 0.961 / 0.278 | 0.28 / 0.24 | yes | Rg=0.659 nm, drug=0.913, **F≈ref (~0)** |
| r3 | 1.0 | 0.858 / 0.399 | 0.40 / 0.40 | yes | Rg=0.699 nm, drug=0.786, **F=3.29 kcal/mol** |

**Verdict — a genuine strengthener, and a clean separation of what survives from what dies:** a *matched,
≥D\* druggable cavity exists independently in all three seeds* (detfrac 1.0; frac≥D\* 0.24–0.40; druggability
crosses 0.5 in every replica; peak 0.86–0.96). So the **structural** claim — a druggable cryptic cavity is
reachable by the pocket-lining residues — is **robust across independent replicas**. What is NOT robust is the
**energetic** cost of reaching it: the free energy at each replica's cheapest druggable frame is 11.72 / ~0 /
3.29 kcal/mol, and the gate-3 FES fully-open cost is 39.39 kcal/mol (r1) vs undefined (r2/r3, the open edge is
never populated). This is the same energetic divergence the cross-replica ΔF already showed — now confirmed at
the level of the *druggable state itself*, not just a fixed Rg. Caveat carried forward honestly: the
whole-surface OFFSITE scan finds comparably-druggable cavities elsewhere in r1/r2 (max off-site drug 0.90/0.93)
though not r3 (0.46) — druggability alone does not localise to the target pocket; the *matched* detection is
what ties it to the orthosteric site.

**Phase 1 — TICA slow-CV discovery (metad r1+r2+r3 pooled, 600 frames each, 57 features; lag 0.5 ns).**
Run 29114498495 (job 86434471595), `slow-cv-summary.json`.

- **corr(IC1, Rg) = 0.680 → verdict = `hidden_mode`.** (Bands: ≥0.9 redundant, ≤0.7 hidden_mode.)
- Slowest implied timescales: **17.1, 11.1, 5.5, 2.9, 2.9 ns** (the slow process is ~17 ns — comparable to the
  30 ns production, i.e. only ~2 relaxations sampled per replica, consistent with the un-converged energetics).

**Verdict — this confirms the reviewer's leading hypothesis (root-cause B).** Rg captures much of the slow mode
but **not all of it**: at |r|=0.68 there is a slow coordinate that Rg does not see. Biasing 1-D Rg harder
(cause A alone) would not fix a projection problem. Two consequences: (i) it explains *why* three Rg-metad
seeds disagree — they are each projecting a ≥2-D opening process onto one lagging coordinate; (ii) it tells
Phase 2 to bias the **data-derived TICA coordinate**, not more Rg. Honest nuance: 0.68 sits just below the 0.70
boundary — the hidden component is real but IC1 is "Rg + something," not an unrelated coordinate, so the
expected gain from re-biasing is *material but not guaranteed dramatic*; Phase 2 must be validated on one
shard before the full fleet.

## 3. If convergence still can't be reached
Report the opening/differential FE as **bounded or unresolved** and rest the paper on the three claims that do
NOT need it: (i) experimental structural heterogeneity (8XTT), (ii) short-timescale persistence after seeding,
(iii) conditional-on-opened-conformer ABFE. This is the reviewer's own "respectable, narrower, stronger" paper
— explicitly *not* claiming equilibrium accessibility.

## 4. Recommended immediate action (cheap, no new sign-off)
Do **Phase 0 + Phase 1** now (both ride on existing data / the already-gated rerun). They (a) settle whether
the druggable state is per-replica real and (b) tell us whether a better CV even exists — which determines
whether Phase 2 is worth the GPU $. **Bring Phase 2's cost estimate back for approval before launching the
enhanced-sampling fleet** (expensive, multi-leg → autonomy threshold).
