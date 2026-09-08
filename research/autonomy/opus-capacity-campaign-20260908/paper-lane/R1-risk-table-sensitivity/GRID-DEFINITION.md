# R1 — grid resolved mathematically BEFORE any measurement

Written and fixed before the harness was run. No number below was chosen after seeing a result.

## Why the proposal's row-count/spacing pairs are wrong

S2's successor sketch named "rows ∈ {2,3,5,8,13,19} crossed with extent ∈ {0.25,0.5,0.75,0.933,1.0}"
and S4 executed the two axes MARGINALLY (density at one extent, extent at one density, plus a
deliberately confounded fixed-spacing block). A row count paired with a spacing does NOT determine a
crossed extent: with `R` rows at spacing `d` starting at 0, the last time is `d·(R−1)`, so fixing
(R, d) fixes the extent too — the three quantities have only two degrees of freedom. Naming a
row-count/spacing pair therefore silently selects an extent and cannot express the crossing.

## The parameterisation actually used

Two free parameters, one derived:

1. **Row count `R`** — the number of PRINTED rows, INCLUDING the first row and the last row.
   `R ≥ 2`. `R = 1` is not a table and is excluded by definition, not by failure.
2. **Last risk-table time `L`** — an ABSOLUTE time in the figure's units, defined SEPARATELY from
   `R`. Not a rounded fraction of `t_max`.
3. **Interior times, derived** — `t_i = L · i / (R − 1)` for `i = 0 … R−1`, so `t_0 = 0` and
   `t_{R−1} = L` exactly. Uniform placement; implied spacing `d = L/(R−1)` is a CONSEQUENCE, never
   an input. Number at risk per row is the generator's own definition,
   `#{r : r.time ≥ t}` (`km_digitize.py:1290`).

## The resulting grid, stated explicitly

- `R ∈ {2, 3, 4, 5, 6, 8, 10, 13, 19, 25}`  (10 levels)
- `L ∈ {45.0, 90.0, 135.0, 168.0, 180.0}`   (5 levels, absolute months; `t_max = 180.0`)
- **Primary design: the full 10 × 5 = 50-cell crossing** of row count × last time. This is what S4
  did not run: S4 measured R at L = 168 and L at R = 8 only, so no interaction between the two was
  observable.
- Each cell is reconstructed under TWO SEPARATE arms, never pooled:
  **(a) exact-coordinate arm** (truth coordinates, never rendered, never read) — reconstruction
  behaviour; **(b) clean-render arm** — the `clean` render read once by `dark_matcher()`, reused
  across cells because the printed risk table cannot change pixels. Density is swept ONLY at the
  clean render; no degraded render enters this experiment.

## The rounding trap, handled explicitly

`168 / 180 = 0.93333…`. **The rounded value 0.933 is NOT that fraction**: `0.933 · 180 = 167.94`.
The grid therefore carries `L` as the absolute time `168.0`, and a separate labelled **probe pair**
at `R = 8` compares `L = 168.0` against `L = 167.94` so the rounding difference is measured rather
than assumed away. The sentinel is only ever asserted against `L = 168.0`.

## Sentinel (the one instrumentation check)

`R = 8`, `L = 168.0` derives `0, 24, 48, 72, 96, 120, 144, 168` exactly — the historical
`run_control()` list (`km_digitize.py:1429`). The exact-coordinate arm of that cell MUST reproduce
the committed `control.exact_coordinates_baseline`:
`events_delta_vs_truth = 0`, `censored_delta_vs_truth = −7`, `internal_max_abs_km_deviation = 0.0009`.
The harness asserts these programmatically and prints PASS/FAIL. A FAIL is labelled before any new
result is quoted; no committed value, artifact or threshold may be adjusted to force agreement.
