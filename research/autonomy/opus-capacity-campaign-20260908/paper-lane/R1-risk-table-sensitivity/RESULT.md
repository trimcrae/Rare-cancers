# R1 — risk-table row-count × last-time sensitivity on the retained synthetic control

**New sibling result block. It overwrites nothing.** `research/modalities/km-digitization-error.json`,
`research/modalities/km_digitize.py`, `research/modalities/emc_ipd_survival.py`, the S2 report and the
S4 report are byte-unchanged; verified hashes below. This is a NEW parameter axis of the retained
synthetic control, not a retry of the closed real-patient IPD retrieval and not a clinical
reconstruction. No network, no new data, no real published curve, no repository module edited.

Run 2026-09-08T19:22:44Z, repo HEAD `3e833d982f0c057804ec6a67cea64dfb1a68bfdf`,
Python 3.11.15 (`/usr/local/bin/python3`).

## S2's disposition, preserved and not re-answered

S2 (`paper-lane/S2-reconstructability-requirement.md`) terminated at acceptance branch (b): the
retained control **carries no density, extent or risk-table-anchoring arm**, `risk_times` is a
hard-coded local at `km_digitize.py:1429`, and S2 executed nothing — every figure it reported is
quoted from the committed artifact. That feasibility finding **stands as recorded and is not
re-derived, re-graded or restated as new here.** R1 executes the successor measurement S2 named;
it does not revisit S2's question.

R1 is also distinct from S4 (`paper-lane/S4-density-extent-anchoring-EXECUTED.md`), which measured
the two axes **marginally** — row count at one extent, extent at one row count, plus a deliberately
confounded fixed-spacing block — and therefore could observe **no interaction** between them.
R1's primary design is the **full crossing**. S4's numbers are not re-quoted as R1 results.

## Design (fixed before measuring — full statement in `GRID-DEFINITION.md`)

- **`R` = printed row count, INCLUDING the first and the last printed row**, `R ≥ 2`.
- **`L` = last risk-table time, an ABSOLUTE time defined separately from `R`** (not a rounded
  fraction of `t_max`).
- **Interior times derived consistently:** `t_i = L·i/(R−1)`, `i = 0 … R−1`; `t_0 = 0`,
  `t_{R−1} = L`. Spacing `L/(R−1)` is a **consequence**, never an input — which is exactly why the
  proposal's row-count/spacing pairs cannot express a crossed extent (fixing R and d fixes L too).
- **Primary design: the full crossing** `R ∈ {2,3,4,5,6,8,10,13,19,25}` × `L ∈ {45, 90, 135, 168,
  180}` = **50 cells**, plus the sentinel cell and one rounding probe = **52 cells**.
- **Two arms kept separate, never pooled (Step 2):** an **exact-coordinate arm** (truth coordinates,
  never rendered, never read — reconstruction behaviour) and a **clean-render arm** (the `clean`
  render read once by `dark_matcher()` — reading behaviour). Density is swept **only at the clean
  render**; no degraded render enters this experiment, so nothing here is confounded with the
  pixel-reading error the committed 16 scenarios already measure. Those 16 scenarios were **not
  re-run**.
- The clean figure is rendered and read **once** and reused across cells: the printed risk table
  cannot change pixels, so a single reading *is* the fixed-render condition. Its reading is
  identical to S4's (`digitized` sha256 `48af484b67124d1553ed0ec98ea175657c6239fa6b32d000572b2813bd5ed773`
  under S4's serialization; `61032c8c924e0d2024ec4f9d45e3cc872882ecbc93f656c9b478a161ef99580a`
  under this harness's compact serialization — same bytes of data, two hashing conventions).

Cohort: `_emc_shaped_cohort()`, n = 59, canonical sha256
`7deb0b9f61a765f83d8b3585b9d0e47f04da9c0788205f73b1caf71cb94deea9` (identical to the cohort S4
hashed). Truth by construction: 18 events, 41 censored, median 168.0, `t_max` 180.0.
**Synthetic arithmetic — no row is a patient.**

## Sentinel: PASS on the first run, no correction made

`R = 8`, `L = 168.0` derives `[0, 24, 48, 72, 96, 120, 144, 168]` — `times_match_exactly: true`
against the historical `run_control()` list. The exact-coordinate arm returned

| quantity | committed `exact_coordinates_baseline` | R1 observed |
|---|---|---|
| `events_delta_vs_truth` | 0 | **0** |
| `censored_delta_vs_truth` | −7 | **−7** |
| `internal_max_abs_km_deviation` | 0.0009 | **0.0009** |

`reproduces_committed_baseline: true`. **No mismatch occurred, so no correction to the harness was
made and none was needed.** No committed value, artifact or threshold was touched.

**Rounding trap, measured not assumed.** `0.933 · 180 = 167.94 ≠ 168`. The probe cell at
`R = 8, L = 167.94` returned deltas identical to `L = 168.0` in both arms. The reason is specific to
this cohort and is **not** a licence to round: exactly one cohort member sits at `t = 168.0` and none
in `(167.94, 168.0)`, and the row count is `#{t_i ≥ t}` with a weak inequality, so both extents
count the same patients. In a cohort with a member in that open interval the two extents would
differ. The sentinel is asserted only against `L = 168.0`.

## Results

Full per-cell parameters and truth comparisons: `CELLS-TABLE.md`. Pivots by arm and quantity:
`PIVOTS.md`. Raw run output: `RUN-01.stdout.json` (52 cells × 2 arms = 104 reconstructions).

### Exact-coordinate arm — `censored_delta_vs_truth` (rows down, last time across)

| R \ L | 45 | 90 | 135 | 168 | 180 |
|---|---|---|---|---|---|
| 2 | −25 | −17 | −12 | −10 | −8 |
| 3 | −25 | −16 | −10 | −7 | −6 |
| 4 | −25 | −16 | −10 | −7 | −5 |
| 5 | −25 | −16 | −10 | −7 | −5 |
| 6 | −25 | −16 | −10 | −7 | −5 |
| 8 | −25 | −16 | −10 | **−7** | −5 |
| 10 | −25 | −16 | −10 | −7 | −5 |
| 13 | −25 | −16 | −10 | −7 | −6 |
| 19 | −30 | −19 | −13 | −11 | −7 |
| 25 | −36 | −23 | −15 | −12 | −11 |

### Clean-render arm — `censored_delta_vs_truth`

| R \ L | 45 | 90 | 135 | 168 | 180 |
|---|---|---|---|---|---|
| 2 | −25 | −17 | −12 | −12 | **−41** |
| 3 | −25 | −16 | −10 | −10 | −17 |
| 4 | −25 | −16 | −10 | **−8** | −12 |
| 5 | −25 | −16 | −10 | **−8** | −10 |
| 6 | −25 | −19 | −10 | **−8** | −9 |
| 8 | −34 | −20 | −15 | −15 | −11 |
| 10 | −40 | −23 | −22 | −15 | −15 |
| 13 | −41 | −32 | −25 | −20 | −22 |
| 19 | −41 | −40 | −32 | −29 | −23 |
| 25 | −41 | **−41** | −37 | −35 | −32 |

### What the crossing shows that the marginal axes could not

1. **Row count is flat over a wide interior band, then reverses.** In the exact arm, at *every* value
   of `L`, `censored_delta_vs_truth` is **identical for R = 3 … 13** (−25 / −16 / −10 / −7 / −5 down
   the columns) and then gets **worse** at R = 19 and R = 25. Adding printed rows between 4 and 13
   bought **exactly nothing** at any extent; adding more than 13 actively cost accuracy.
   **This is a flat-then-non-monotone curve, and it refutes the "denser table ⇒ smaller error"
   requirement framing on this cohort.** It is a result, not a failure of the run.
2. **The interaction is real, and it is where the two axes disagree.** The best clean-render cells
   are `R = 4–6, L = 168` (censored Δ −8), **not** the committed control's `R = 8` (−15); yet the
   best exact-arm cells are `R = 4–10, L = 180` (−5), where the clean-render arm is worse (−9 to
   −12). The configuration that best serves the reconstruction algorithm is **not** the one that
   best serves a reader of the rendered figure. A marginal sweep along either axis alone cannot see
   this.
3. **Extent moves the error more than density does, and is still not sufficient.** At fixed R = 8 the
   exact arm improves −25 → −16 → −10 → −7 → −5 as L goes 45 → 180. But **no cell anywhere in the
   50-cell crossing recovered the truth in either arm**: the smallest exact-arm censored deficit was
   −5 of 41 (printing the risk table to the full axis), the smallest clean-render deficit −8, and no
   cell reached `censored_delta_vs_truth = 0` with `events_delta_vs_truth = 0`. The best median error
   in the entire grid was −18.0 time units.
4. **Two extreme reading pathologies, recorded as measured.** `R = 2, L = 180` in the clean-render
   arm lost **all 41 censorings** and gained **+14 spurious events** while its exact-arm twin lost
   only 8 and gained 3; `R = 25, L = 90` in the clean-render arm likewise lost all 41. Both are
   reading × row-placement interactions, and both are reported rather than trimmed.
5. **The internal deviation gate saw none of it.** `internal_max_abs_km_deviation` never exceeded
   **0.0254** anywhere in the 104 arms, so **all 104 were `admissible` under the unmodified
   `MAX_KM_DEVIATION = 0.05`** — including the arms that lost every censoring and put the median
   116 time units low. No guard was changed; this is the committed artifact's own
   `⛔_defect_found_in_the_instrument_this_feeds` showing up on the risk-table axis.

## What may and may not be concluded

**May.** This is a statement of **conditional error on one known synthetic cohort under one clean
render and one matcher**, and it supplies **counterexamples to a proposed universal reporting rule**:
on this cohort, "print more risk-table rows" bought no accuracy between 4 and 13 rows at any extent,
and beyond 13 rows made both arms worse — so a rule of the form "denser is safer" has explicit
counterexamples here, and a rule of the form "printing the table to the full axis makes a curve
recoverable" has one too (−5 censorings remained lost at `L = 180` under exact coordinates).

**May not.** This experiment does **not** establish a sufficient journal reporting standard, and it
does **not** establish a universal mathematical lower bound for error on real figures. The
committed artifact's warning is carried as **quoted historical wording**, and is quoted, not endorsed
as a universal bound:

> "A SYNTHETIC RENDER IS EASIER THAN A JOURNAL FIGURE. This control can REFUTE the reader and cannot
> certify it: an error measured here is a LOWER bound on the error of reading a real published curve."
> — `research/modalities/km-digitization-error.json`, `⛔_direction_of_the_bound`

R1 measured one synthetic cohort and proves nothing about the population of real figures; whether
that quoted lower-bound relation holds generally is outside what this experiment can show, and is
**UNKNOWN** here.

**Empirical tendency vs monotonicity assumed by construction.** Two things in these tables are true
by construction and must not be read as findings: censored patients later than `L` are unidentifiable
because the table stops (so the deficit shrinking as `L` grows is arithmetic, not discovery), and
`t_0 = 0` with `t_{R−1} = L` is imposed by the parameterisation. What is **empirical** is the shape
in `R`: the flat band at R = 3–13, the reversal at R ≥ 19 in both arms, the earlier and steeper
reversal in the clean-render arm (from R = 8), and the interaction in item 2. Those are observed
tendencies on one cohort with a fixed reading draw, not laws.

## Sample and design limitations

One synthetic cohort (n = 59, 18 events, heavy terminal censoring, five members at t = 180), one
renderer at `render_km` defaults, one matcher at `dark_matcher()` defaults, **uniform** row placement
only, and a **single** clean render reused across all cells — so the clean-render numbers are one
fixed reading draw and their between-render variability is **UNKNOWN**. Anchoring (printed vs
anchored first row) was **not** an axis of R1 and was not re-measured. `R = 1` is excluded by
definition. `L < 45` was not run. Degraded renders were not run. `PIL`/Pillow is absent in this
container, so `km_digitize.jpeg_roundtrip` is unavailable — no cell of this grid needed it and
nothing was installed. `run_control()` was not re-run end to end, so the committed artifact as a
whole was not re-verified: only its `exact_coordinates_baseline` triple was reproduced, exactly.
No clinical, prognostic, efficacy, safety or survival claim about EMC or any disease follows from
anything here.
