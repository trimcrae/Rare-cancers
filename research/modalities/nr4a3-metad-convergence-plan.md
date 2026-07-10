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
Cost: a multi-seed × 3-receptor enhanced-sampling fleet — real GPU $, multi-day. **Serialize/spot per the
compute rules; bring the cost estimate back before launching.**

### Phase 3 — state-correct the selectivity (decisive, either way)
Combine: **ΔΔG_full(3−2) ≈ ΔΔG_bind^open(3−2) + [ΔG_open,3 − ΔG_open,2]** (and 3−1). Outcomes are all
publishable: differential small/favourable → conditional selectivity survives and the paper is materially
stronger (no converged-0.6 needed); differential large/unfavourable → selectivity is state-limited, stated
honestly. Optional robustness: **ensemble ABFE** for `denovo_401` across several independently-justified
cavity-bearing frames per receptor (does the sign hold, or is it a single-snapshot artifact?).

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
