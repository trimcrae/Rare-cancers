---
id: DOC-MF1-RESIDUAL-LIMITATIONS
title: "MF1 residual — what the narrowed audit still cannot support"
level: L4
kind: memo
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# What the narrowed audit still cannot support

⛔ **Completing R1–R5 does not clear MF1, does not open a gate and does not confer scientific validity on
any record it describes.** The scientific proposition remains the **narrow retrospective audit of one
program's retained instrument records**. Everything below is unchanged by this batch.

## 1 · Scientific limits that stand exactly where they stood

- ⛔ **There is no wet lab.** No claim of binding, potency, selectivity, efficacy, safety, therapeutic
  window or clinical readiness is made or implied by anything in this batch, and none could be.
- **The cause of the wrong-sign valB calibration failure is not identified.** Closure is blind to
  endpoint-state error rather than diagnostic of it. Repetition strengthens the observed failure and
  identifies nothing.
- **No effect size is established for the E1 observable**, so no sensitivity statement about that readout
  is available at any sample size in this record. The 1/462 floor is discreteness, not power.
- **`S` has no known-answer calibrator**, so its value is evidence about the physical wedge in neither
  direction. `S ≈ 0` cannot separate *no effect* from *cannot resolve*.
- **The corrected-interface readouts of the covalent panel cannot be recomputed** from what was retained
  under the two surveyed prefixes, and two legs simulated the wrong physical system, which no retained
  data repairs.
- **Whole-program ascertainment is not established**, so no failure *rate* over the program exists.
- **`V4` is unrun and unauthorised**; the selectivity free-energy axis has never been graded directly.
- **No external publication is assessed.** The withdrawal at §9.5 stands, and the absence of the
  comparison it would need is scoped to the evidence actually inspected — not asserted repository-wide.
- **The chronology of prespecification is unestablished.** What the record supports is the attribution.
- ⛔ **Stronger accuracy, physical-mechanism, calibrated-absence and pre-registration claims remain on
  their original evidence conditions.** Nothing here relaxes one.

## 2 · What this batch specifically did NOT establish

- **The benchmark values in §4.2 are retained register values, not independent verification.** No
  benchmark was rerun and no primary benchmark publication was retrieved; the primary literature
  identifiers for `V6`, `V7`, `V8` and `V10` are still not asserted.
- **Several uncertainty types are UNKNOWN** and are marked so. A ± quoted by the register without its kind
  is not a standard error, a standard deviation or a confidence interval here.
- **The `V5` "~34×" ratio and the `3.28` SD-over-SE multiplier are withdrawn with no substitute.**
- **The E1 exclusion account adds an exclusion the record already held.** It is not a new eligibility
  decision, and no faux all-identical structure set was constructed.
- **An identity or hash check is not a scientific reading.** The intake's honest categories stand and are
  not collapsed: **13 full-read, 13 identity, 44 execution-metadata, 44 execution-stream, 10
  bounded-read.** Not every retained byte received a scientific read.
- **`bytes_match_head_blob: 18/18` is a binding fact, not a validity fact.** It says the display was built
  from the bytes it names; it says nothing about whether those records are scientifically sound.

## 3 · Open items this author could not close, and why

| open item | why it could not be closed here |
|---|---|
| census `V16.scope_limit`, census `V20.scope_limit`, census `V11.result`, roadmap `:3246` | **Parent-owned shared files.** The exact patch is prepared and verified (`git apply --check` exit 0) and deliberately **not applied**. The SI is nevertheless correct today, because its claim-scope column is now the author-current scope and the census string is demoted to a labelled superseded historical annotation. |
| the **one admitted instrument-census metadata update** | **Not spent.** The census is generated from the roadmap; with the roadmap patch unapplied, `instrument_census.py --check` returns exit 0, so a regeneration would change nothing. Spending the single admitted operation on a no-op would leave nothing for the sequence that actually needs it. |
| census `V16.result` still reading *"registered in advance as the LIKELY outcome"* | A **shared** cell. It appears in the SI only under a column explicitly headed *result as recorded (census)*, and patch **Q2** corrects it at source. The manuscript's own chronology claims are all corrected. |
| the exact literal invocation of the earlier final extraction (attempt 22) | **It was never recorded.** Its `.cmd` is shorthand. ⛔ It is not reconstructed, and no re-run is presented as an earlier execution. |
| the 13-edit uniqueness stream and the three view-command streams from the b577 integration | **They do not exist** — the first ran inline, the other three were redirected to `/dev/null`. ⛔ Named as missing, not recreated. |
| whether MF1 passes its repository gates | ⛔ **Not assessed and not claimed.** The retained streams include `systems_check` exit 1 at 2,695 / 2,667 / 2,666 errors, `lint_citations` exit 1 with 13 type errors, `systems-map` exit 1 with 6, two claims checks that pass **with warnings** and do not establish semantic closure, a prose check that saw **zero changed passages**, and a readability report that **did not assess MF1**. No broad suite was run in this batch and none was authorised. |

## 4 · The stopping condition

⛔ **No completion here grants a broader gate, a submission decision or science clearance.** What this
batch delivers is a corrected main, a regenerated supplement that no longer republishes a withdrawn claim
as a current limit, a dated erratum, an exposed benchmark and exclusion account, an attributed chronology,
a scoped mechanism sentence, and one exact unapplied patch for the four cells that remain in shared state.
MF1's scientific hold is unchanged.
