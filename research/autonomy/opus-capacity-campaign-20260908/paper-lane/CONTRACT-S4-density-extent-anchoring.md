# S4 — finite contract, recorded BEFORE dispatch

Coordinator, 2026-09-08 ~05:50Z. One bounded Opus 5 (`claude-opus-5`, medium) successor on the existing
first-party subscription. Same session, one parent collector, disjoint scratch ownership, deadline
2026-09-09T02:37:19Z, no paid fallback, no new controller and no per-child approval loop.

## Continuity, stated so the prior result is not overwritten

S2 is **complete** and stopped at its acceptance branch (b). Its finding stands as recorded: `risk_times` is
hard-coded at `research/modalities/km_digitize.py:1429`; the retained control has **no density, extent or
risk-table-anchoring arm**; **no computation and no patch were executed** by S2. Every number S2 reported is
**quoted from the committed artifact, not newly measured**, and is preserved that way — including the
exact-coordinates baseline's `censored_delta_vs_truth: -7`. S4 continues the **same** synthetic instrument
study; it does not re-derive, restate or re-grade S2's quoted figures.

## Task

Implement and run S2's already-named next action: the **density / extent** sweep and the **printed-versus-
anchored** first-row contrast, at **fixed clean rendering**, over the **synthetic** cohort whose ground truth
is known by construction.

- **Inputs:** the existing generator `research/modalities/km_digitize.py` plus its synthetic cohort. **No new
  patient cohort, no held or closed source, no real published figure.**
- **Where:** a private scratch copy/adapter under `/tmp/claude-0/s4/` that exposes `risk_times` and the
  synthetic scenario settings. **Repository files remain unchanged**; no manuscript or shared-graph edit, no
  ownership transfer, no publication.
- **Design:** finite and consistent with the existing generator. The three axes are distinct and **must not be
  silently conflated** — *density* (number of printed rows), *extent* (time of the last printed row as a
  fraction of `t_max`), *anchoring* (first row taken at the printed time versus immediately before it). Any
  cell that varies more than one axis must say so.
- **Retain:** exact executed code, input parameters and their hashes, per-cell outputs, runtime, and every
  observed failure. Failures are part of the result, not noise to be dropped.

## Bounds

Runtime **≤ 20 minutes** of experiment wall-clock initially. Bound scratch output and disk; **preserve ≥ 10 GiB
free** and check before and after. If the generator lacks a required working capability or installed
dependency, **name it exactly and stop that dependent branch** — do not install broadly, do not download, and
do not invent a result in its place.

## Prohibited

No real-curve inversion. No clinical IPD, no patient-level data production or pooling. No closed-gate replay
(IPD, recurrence, care-delivery, RT). No substitution of a different task if this one proves hard. No record or
artifact census — S1 and S3 remain **stopped** and are not revived in any form, under any label. W25 /
primary-article / Results / novelty hold and the NR4A Perspective exclusion remain exact.

## Interpretation limits, binding on the report

Original thresholds are unchanged. **A passing synthetic cell creates no reporting requirement and no clinical
claim.** Results describe **this control** under **these settings**; a single control result — the seven lost
censorings included — is **not** a universal lower bound for all real 8-row tables and must not be written as
one. A general requirement stays **UNKNOWN** unless the experiment supports it within clearly stated limits.

## Acceptance and stop

Accepted on **measured per-cell output** from an executed run, with the code, parameters, hashes, runtimes and
failures retained; or on a **named missing capability/dependency** with the dependent branch stopped there. A
code draft alone is **not** acceptance if the experiment is runnable. Proposed work stays labelled PROPOSED
until it runs. Stop at the runtime bound, at acceptance, or at ~40 tool calls.

Child model is verified by this collector from the child transcript, not from the dispatch.

---

# S4 — EXECUTED. Acceptance met on measured per-cell output.

Collected to `paper-lane/S4-density-extent-anchoring-EXECUTED.md`. Child model verified by this collector from
the transcript: observed model set is exactly `["claude-opus-5"]`. Repository untouched — HEAD `81c077ea`
unchanged and `git status --porcelain` empty at the child's start and end; scratch deleted; ≥10 GiB free
preserved at both ends (20 GiB, peak scratch 300 K).

**25 cells × 2 arms = 50 reconstructions, exit 0, executed experiment wall-clock 0.229 s** against a 20-minute
bound. No guard, threshold or repository file was modified anywhere: `MAX_KM_DEVIATION = 0.05` and
`REQUIRE_RISK_TABLE = True` were imported and echoed back unchanged.

**Method note that makes the result stronger than the contract required.** Exposing `risk_times` needed **no
edit to the generator at all**: the scratch copy is byte-identical to the repository file
(`sha256 05aeeb4b…`, same hash both sides), and the adapter supplies the risk table from outside by calling
`_cohort_to_figure_inputs` / `render_km` / `extract_series` / `reconstruct` directly. Every guard is provably
as-imported. The clean render was executed **once** and reused across all cells — the risk table cannot change
pixels, so that *is* the fixed-rendering condition rather than an approximation of it. Two arms per cell
(exact coordinates, and the one clean render) keep risk-table effect and reading error unconflated.

## Independent recomputation of the one figure S2 could only quote

The exact arm at **rows 8, extent 0.933** reproduces the committed artifact's `exact_coordinates_baseline`
exactly: `events_delta_vs_truth 0`, `censored_delta_vs_truth −7`, `internal_max_abs_km_deviation 0.0009`.
That figure is therefore **now measured under this campaign**, not only quoted — and it is the anchor that
makes the rest of the grid comparable to the artifact.

## Measured, scoped to this control under these settings

- **Extent dominates the censored count** (exact arm, 8 rows fixed): −25 → −16 → −10 → −7 → −5 as the last
  printed row moves 0.25 → 1.0 of `t_max`. Printing to the full axis still loses 5 — **necessary, not
  sufficient.**
- ⭐ **Density is not monotone, and denser is not safer.** Exact arm: 2→3 rows removes an events error
  (+3 → 0), 3–13 rows sit flat at −7, then 19 and 25 rows get *worse* (−11, −12). The clean-render arm degrades
  severely and monotonically beyond 5 rows: censored delta −8 → −15 → −20 → −29 → −35, median error −40 →
  −116. More printed rows means more intervals the recursion must force the read curve through, and small
  reading error inside a short interval is not absorbed.
- **Anchoring is a one-patient effect here, in the direction the real-figure rationale predicts.** Anchoring the
  first row immediately before its printed time recovered **exactly one** censored patient (−10 → −9 at t₁=6;
  −13 → −12 at t₁=11) in both arms, changing events, median and deviation **not at all**. The effect size
  equals the number of cohort members whose observed time is exactly t₁ — one, in both cells.
- ⛔ **The internal deviation does not police this error class.** In **44 of 50 cells** the deviation stayed
  under the 0.05 floor and `admissible` was **True** while the reconstruction lost up to **35 of 41**
  censorings and put the median **116 units low**. That is the same failure mode the artifact already records
  for axis calibration, now measured on a second, independent axis — the risk table.

## Failures retained, not dropped

Six of 50 reconstructions were **refused** by `assess_quality` on the unchanged floor (four t₁=24 cells at
0.0941/0.1155; two t₁=11 clean-render cells at 0.0536). **No guard was touched to make them pass.**
**Pillow (`PIL`) is not installed** (`ModuleNotFoundError`), so `km_digitize.jpeg_roundtrip`
(`km_digitize.py:1495-1501`) is unavailable — named, no cell of this grid depended on it, nothing installed.
No cell crashed. A re-run differed only in recorded `seconds`; with timings stripped the two runs are
identical, recorded because it is an observed discrepancy rather than a real one.

## Interpretation limits, binding and restated

**No clinical claim of any kind** — the cohort is generated arithmetic and no row is a patient. **A passing
synthetic cell creates no reporting requirement.** `⛔_direction_of_the_bound` applies to every figure above:
a synthetic render is easier than a journal figure, so each bounds reading error **from below**. **This is not
a universal statement about journal figures and not a universal lower bound for all real 8-row tables** — the
seven lost censorings describe this cohort's censoring pattern against this row placement, and a different
late-censoring pattern would move every number. **A general reporting requirement remains UNKNOWN.** The most
that holds inside stated limits: *for this synthetic 59-patient cohort at clean rendering, no number of printed
rows recovered the censored count when the table stopped at 0.933·t_max, and increasing rows beyond 5 made the
read arm's censored count worse.* A statement about this instrument, not a rule for journals.

## Named successor — PROPOSED, NOT RUN, not authorized by this record

Repeat the density and extent axes with the render **repeated** per cell and across ≥2 cohort shapes with
different late-censoring patterns, converting the clean-render arm's single fixed reading draw into a
distribution. Until that runs, "denser tables make the read arm worse beyond 5 rows" is a **single-draw
observation on one cohort**.

Holds unchanged: W25 / primary-article / Results / novelty, the NR4A Perspective exclusion, the S1 and S3
stops, and every closed route. Same session, collector, deadline, subscription; no publication, no merge, no
graph or manuscript edit.
