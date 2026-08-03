# C02 — the cross-system decoy null for the categorical covalent axis

> **$0 CPU/CI. No GPU, no rental.** Nothing here is a claim about binding, reactivity, degradation,
> selectivity in vivo, efficacy, safety, a therapeutic window or clinical readiness.
>
> **★ ONE FACT, ONE PLACE.** The design and every number live in
> [`categorical-decoy-null.json`](./categorical-decoy-null.json) (results) and
> [`categorical-decoy-null-plan.json`](./categorical-decoy-null-plan.json) (the pre-registration + the
> selected pairs), produced by [`categorical_decoy_null.py`](./categorical_decoy_null.py). The NR4A3 figures
> this calibrates keep their home in
> [`nr4a-paralogue-dynamics.json`](./nr4a-paralogue-dynamics.json) → `categorical_verdict`. This file carries
> the reasoning and points at those; it is not a second home for any figure.

---

## 1 · The problem, stated exactly

The categorical covalent axis reports `P(paralogue also labelled | NR4A3 labelled)` at the 12-backbone-atom
design gate over 73,867 matched E3 placements, and the audit
([`categorical-axis-audit.json`](./categorical-axis-audit.json)) establishes that **at that gate the
reach-only numbers already carry the result** — the exposure filter is not what produces it.

**Every null in this repo is WITHIN-system.** `term_b_background_null` is a placement null; `V19` is a
generation-matched null. Neither asks how often a *random close paralogue pair* presents the same
configuration. So the categorical result is, as it stands, **an enrichment over an unmeasured background** —
and this program has already paid for exactly that shape once.

> **⛔ The precedent, and it is exact.** `V20` — single-snapshot MM-GBSA `margin > 0` — looked like a clean
> selectivity signal until 38 unrelated marketed drugs went through the identical funnel and **22 of them
> (57.9 %) scored a positive margin** (`selectivity_calibration.DECOY_2026_06_30`), replicated at 39 % on a
> ~6,000-compound library. That retracted a headline. The categorical axis has never had its equivalent test.

## 2 · The design, and why it is pre-registered

The whole value of a percentile is that the rules were fixed **before** the answers were visible, so the
design is a frozen constant (`PREREG` in the module), `plan` mode emits it with **no results at all**, and
git history therefore carries the design ahead of the numbers. Verbatim in
[`categorical-decoy-null-plan.json`](./categorical-decoy-null-plan.json) → `preregistration`. In brief:

| decision | rule | why it is answer-blind |
|---|---|---|
| **universe** | the 47 human nuclear receptors already committed in [`nr4a-superfamily-selectivity.json`](./nr4a-superfamily-selectivity.json) → `ranking[]`, minus the NR4A family | an on-disk artifact generated months earlier for a different purpose — not a list curated for this test |
| **structures** | one AlphaFold DB model per accession, URL resolved through the prediction API, SHA-256 recorded | uniform coverage; nothing chosen per protein |
| **domain trim** | largest contiguous pLDDT ≥ 70 run, ≥ 120 residues | mechanical and identical for every protein |
| **pairs** | identity in **[0.35, 0.90]**, alignment coverage ≥ 0.60, ranked by \|identity − NR4A3's own paralogue identity\|, greedy, ≤ 2 pairs per protein, ≤ 10 pairs | identity is a property of the sequences, computed before any reach statistic exists |
| **orientations** | every pair contributes **both** ordered decoys | neither direction is chosen |
| **pocket** | fpocket's highest-druggability cavity on the target's trimmed domain | family-agnostic; no per-protein judgement |
| **statistic** | `P(any paralogue Cys in budget \| the same placement puts the electrophile on a target-unique Cys)` at 12 atoms, **both** reach-only and RSA ≥ 0.25 | the audit shows reach-only carries the 12-atom result, so an exposure-only null would miss the load-bearing case |
| **gradeability** | ≥ 20 conditioning events, else `UNDERPOWERED` and excluded | a conditional on a handful of events is not a measurement |

**"Close pairs, not random proteins" is the point.** A random-protein null would confound *no collision* with
*wrong fold*. Nuclear-receptor paralogue pairs share the fold class, the domain size and the kind of buried
ligand pocket, so the null isolates the thing under test. ⚠ **The price:** the background measured here is a
**nuclear-receptor** background, not a proteome background. That is a limit, and it is in the artifact.

## 3 · It is the same pipeline, not a re-implementation

Every scientific step is **imported**:

| step | function |
|---|---|
| reach rule | `nr4a_paralogue_dynamics.matched_reach_hits_multi` → `nr4a3_basin_search.electrophile_reach` (the committed prolate-spheroid criterion) |
| placement sampling | `nr4a3_basin_search.sample_placements` |
| pose ensemble | `nr4a3_basin_search.build_pose_ensemble` |
| superposition | `nr4a3_basin_search.superpose_paralogue` |
| SASA / RSA | `nr4a_differential_atlas.shrake_rupley` / `residue_rsa` |
| aligner | `nr4a_differential_atlas.nw_align` (BLOSUM62 Needleman-Wunsch) |
| E3 arms | [`nr4a3-e3-arm-registry-native.json`](./nr4a3-e3-arm-registry-native.json) — same VHL + CRBN, same observed 9UUM E2 geometry |

What is new is only the **driver**: which pairs, which pocket, and the background arithmetic.

### 3.1 · The driver has its own known-answer test, and it passes

A background measured by a broken harness would be **worse than no background**, so
`categorical_decoy_null.py selfcheck` re-runs *this driver* on the committed NR4A3 / NR4A1 / NR4A2 opened
models with the committed Pocket-5 lining, and compares against
[`nr4a-paralogue-dynamics.json`](./nr4a-paralogue-dynamics.json) → `categorical_verdict.by_scope.static_opened_model`.
It runs in the same CI job that publishes the background, and its output is folded into the artifact at
`harness_known_answer_check`.

⚠ **The 12-atom cell is deliberately not the discriminating comparison.** The committed run has 77
conditioning events in 73,867 placements, so a cheap re-run has a handful and can only agree trivially at 0.
**The 20-atom cell has thousands of conditioning events on both sides** and is where a real disagreement
would show — so that is the number to read, and a comparison this run could not make records `None` rather
than passing silently.

## 4 · How to read the result

- **`background_at_gate_12`** — the distribution of the decoy collision probability, reach-only and
  exposure-filtered, with `n_exactly_zero` and `frac_exactly_zero` beside it. **`frac_exactly_zero` is the
  headline of this whole exercise**: it is the answer to *"how often does an arbitrary close paralogue pair
  produce the same 0-collision result?"*
- **`nr4a3_harness_matched`** — NR4A3 vs NR4A1 and vs NR4A2, run through **this** harness under **this**
  pocket rule on **this** kind of input, with its percentile against the graded decoys. ⚠ **The percentile is
  taken against this row, not against the committed one**, because the committed verdict uses a different
  pocket rule (prespecified Pocket-5), a different structure source and hydrogens; comparing across those
  would be comparing pipelines rather than proteins.
- **`nr4a3_committed_for_reference`** — the committed figures, quoted so the two can be seen side by side.
  Their one home stays `nr4a-paralogue-dynamics.json`.

**A pass is not the goal; a measured background is.** If few decoys reach 0, the categorical GO carries
information and becomes quotable **with this background beside it**. If most decoys reach 0, the categorical
GO is a property of the **method** and the axis must be re-graded — which is worth far more found here than
found in review.

## 5 · Limits, all of them

1. The background is a **nuclear-receptor** background, not a proteome background.
2. **One static conformer per protein.** Only the committed verdict's `static_opened_model` scope is
   comparable to these rows, which is why the harness-matched NR4A3 row exists.
3. The **pocket rule differs** from NR4A3's prespecified Pocket-5 — hence NR4A3 is run under the same rule
   here rather than compared across rules.
4. AlphaFold models are **heavy-atom only**; the committed NR4A3 opened models carry hydrogens, so the
   Shrake-Rupley RSA is not numerically identical between the two arms. This affects the **exposure-filtered**
   column; the reach-only column, which the audit shows carries the 12-atom result, is unaffected.
5. **Reach and exposure are necessary, not sufficient** — no thiol pKa, nucleophilicity, adduct stability or
   promiscuity is modelled, for the decoys exactly as for NR4A3 (limit `L6` of the categorical audit).
6. **Underpowered and undefined rows are excluded from the percentile and counted separately.** That
   exclusion biases the graded background toward pairs whose unique cysteines are reachable at all — i.e.
   toward **more** collision opportunity, which makes the background *harder* for NR4A3 to beat, not easier.
7. This calibrates the **screen**, not the target. It says nothing about NR4A3 that the screen does not.

---

*Produced by [`categorical_decoy_null.py`](./categorical_decoy_null.py) via
[`.github/workflows/categorical-decoy-null.yml`](../../.github/workflows/categorical-decoy-null.yml).
Driver logic is unit-tested in [`tests/test_categorical_decoy_null.py`](./tests/test_categorical_decoy_null.py).
Candidate `C02` in [`instrument-options.md`](./instrument-options.md).*
