---
id: DOC-ENDPOINT-1-CLAIM-REDERIVATION
title: "ENDPOINT-1 — which quantitative claims of PUB-ENDPOINT re-derive from its own artifacts, and what exactly is missing for the rest"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ENDPOINT-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
endpoint: PUB-ENDPOINT
route: RT-ENDPOINT-CHOICE
---

# ENDPOINT-1 — first pass claim re-derivation for PUB-ENDPOINT

## Question

Which of the quantitative claims in `response-endpoint-indolent-tumours.md` can be re-derived today
from the six artifacts `RT-ENDPOINT-CHOICE` names — and, where a claim can be rebuilt from the
corpus's own raw rows rather than only read back from a summary key, does the rebuilt value equal the
printed one? For anything that cannot be re-derived here, what exactly is the missing input?

## Merit rationale

PUB-ENDPOINT is one of the 33 endpoints in `systems/graph/publications.json` and had **never** had a
lane in either campaign round, while its route's `next.best_next_action` reads "Review the manuscript
for external posting to medRxiv. Nothing else in the route is unrun." A paper whose entire content is
a measurement claim about how trials are summarised is checkable in exactly one way: by recomputing
its numbers from the counts it committed. That is unusually favourable here, because the corpus
artifact retains **every raw input** — 552 four-cell arm tables and 1,837 accrual records — so most
of the paper is re-derivable from first principles rather than merely readable back. Patient
relevance is indirect and the endpoint itself says so (`patient_path: none`); the paper reaches a
patient only through how a future trial is read, which makes the arithmetic the whole of its
credibility. A reader who cannot re-derive these numbers has nothing else to check.

## Exact evidence gap addressed

Not "is the argument sound" — the manuscript's own §9 states its limitations, and its Appendix A
already registers seven superseded values. The unaddressed gap is narrower: **no lane, review or test
had ever checked claim by claim that the printed quantities are recoverable from the artifacts they
name.** The distinguishing inputs are the six route artifacts (`endpoint-corpus.json`,
`orr-dcr-reread.json`, `endpoint-regime-map.json`, `placebo-arm-calibration.json`,
`endpoint-prior-art-audit.json`, `emc-endpoint-discordance.json`). The seven producers' own `--check`
modes do **not** close this gap: each re-derives its artifact from its inputs with the same code, so a
selector or convention baked into a producer reproduces itself. This lane recomputes independently.

## Step taken

One pass over every quantitative claim in the manuscript, at two derivation levels — **RECOMPUTED**
(rebuilt here from `C2_arms[].cells`, `C7_accrual_records`, `R2_per_arm_rows`, or from the binomial
and Wilson definitions, by code that does not import the producers) and **READ-BACK** (the value is
stored in the named key) — plus explicit **NOT-RE-DERIVABLE-LOCALLY** rows naming the missing input.

## Artifact

`claim-rederivation-ledger.json` — **99 rows**, each with the quoted value, the source artifact and
key, the re-derived value, the derivation level and a verdict.

| verdict | rows |
|---|---|
| REPRODUCES | 95 |
| MISMATCH | 1 |
| NOT-RE-DERIVABLE-LOCALLY | 3 |

Of the 95 that reproduce, **72 are RECOMPUTED** rather than read back.

### The one MISMATCH, digit for digit

| where | manuscript / artifact states | re-derived here |
|---|---|---|
| §4.3, Figure 3 caption ("the binomial expectation at the corpus median response rate of **7.7%**"); `orr-dcr-reread.json` → `R8_zero_response_readouts.disjoint_bins_observed_against_binomial._corpus_median_objective_response_pct` | **7.7** | **7.2** |

The 552 per-arm objective-response percentages have two middle order statistics, **6.7** and **7.7**;
their mean — the median — is **7.2**. `research/manuscripts/orr_dcr_reread.py` line 107–108 computes
`orrs[len(orrs) // 2]`, the **upper** of the two, i.e. the 277th of 552 sorted values, and labels it
`_corpus_median_objective_response_pct`. The manuscript prints it as "the corpus median response
rate". **Reported, not repaired**: no prose was edited, no producer was touched, no diff was prepared,
and no alternative reading was sought under which 7.7 would be the median.

Two things bound how far it reaches, and both are stated because the honest report is neither
"harmless" nor "load-bearing" without evidence:

* **It is the p that draws Figure 3's expected curve.** Recomputing the expected zero-response share
  in each band at the true median 7.2% instead: 1–4 → 82.1% (printed 81.0), 5–9 → 63.1% (61.0),
  10–19 → 35.3% (32.8), 20–39 → 13.3% (11.5), 40+ → 0.7% (0.5). Every band's expectation moves up by
  1.1 to 2.5 points.
* **The qualitative claim built on it survives.** Observed remains below expected in all five bands
  (77.0/57.8/30.1/8.3/0.0), so §4.3's "observed sits a little below expected in every band" and the
  substantive "largely a function of arm size" reading are unchanged in direction, and the gap is
  slightly larger, not smaller. The *fitted curve* is what is wrong, not the finding it supports.
  This lane makes no recommendation about what the paper should do.

Every other band quantity — arms, median n, zero-response arms, observed % — reproduces exactly, and
each band row is recomputed with the artifact's own stored p so that the band arithmetic is tested
separately from the choice of p.

⚠ **Nothing pins this value.** `research/manuscripts/tests/test_endpoint_manuscript_figures.py`
contains no assertion on 7.7 or on `_corpus_median_objective_response_pct`, and each producer's
`--check` re-derives the same selector, so no existing gate would report this. No guard, test, floor
or matcher was changed, weakened or inspected for weakening by this lane.

### The three NOT-RE-DERIVABLE-LOCALLY rows, with the missing input named

| row | claim | exact missing input |
|---|---|---|
| `A-CAPS` | §3.4: both accrual queries "were capped at 1,000 returned records against reported totals of **2,027** terminated trials and **16,035** completed phase 2 trials" — the fact that makes the pooled 50.0% an artefact of retrieval | the ClinicalTrials.gov query responses' **`totalCount` headers** for the two frozen accrual queries. `C5_retrieval_provenance` in the committed corpus retains no per-query reported-total field, and the raw payloads live on the `literature-cache` branch, which is not checked out here. Re-querying the registry is direct HTTP egress and was **not attempted**. |
| `V-OVERLAP` | §6.1: whether the French cohort inside the 282-patient pooled analysis (PMID 39620931) overlaps the 100 patients of PMID 37777684 is "stated in neither report and is unknown here" | centre- or patient-level enrolment rosters for those two studies. Neither report states it. The PubMed/PMC route returns metadata and full text, not enrolment rosters, and no retrieval was attempted for this row. **UNKNOWN, not zero** — the manuscript states it as unknown and this lane confirms only that the artifact carries no basis for resolving it. |
| `V-PLACEBO20` | §6.1: "the placebo arm of a controlled trial recorded a **20%** objective response rate before crossover" | `emc-endpoint-alternatives.json` → `E10`. That file is a **companion**, not one of the six artifacts `RT-ENDPOINT-CHOICE` lists, and the manuscript explicitly delegates the figure to the companion note. This lane did not open it, so the value is carried, not re-derived. Closing this row is one file read, deliberately left outside this pass's scope. |

### Known-answer controls — six, all passed, and two caught real harness defects

| control | what it detects | result |
|---|---|---|
| Wilson interval for 6/47 by closed form vs. bisection on the score equation | wrong Wilson algebra | 6.0–25.2 both ways |
| binomial upper-tail against three hand-checkable values | a broken tail would break every contour row | pass |
| type-7 quantile on `[1,2,3,4]` | the IQR row depends on the quantile convention | 1.75 / 2.5 / 3.25 |
| **cross-artifact**: all 552 `R2_per_arm_rows` recomputed from `C2_arms[].cells` | the analysis file must equal what this harness computes from the corpus | 0 disagreements |
| **mutation**: corrupt one arm's SD, median gap must move | a vacuous comparison | pass |
| **mutation**: corrupt one arm's SD, the four-cell identity must fail | an assertion that cannot fail | pass |

The controls did their job. In `checks/01` two of them **failed** (exit 2, preserved) and their
failure was correct: the R2 control exposed that `(nct_id, arm_title)` is **not unique** in this
corpus — 87 collisions — so the first harness silently keyed 63 arms onto the wrong row, and the
second exposed that the first mutation control had been written so it could not fail. Both were
harness defects, fixed in `checks/02`; `checks/01` also carried five apparent "mismatches" that were
mine, not the paper's (a phase-mix summed over conditions, double-counting arms listed under two
placed conditions; an `EARLY_PHASE1` arm miscounted as no-phase; two wrong artifact key names; and a
median-of-medians reported without the producer's integer truncation). **All five disappeared once
the harness was correct, which is exactly why the single surviving MISMATCH is reported as a
finding.**

### What reproduced that was worth testing

* **The whole of §4** rebuilt from raw cells: 552 arms, 138 distinct trials, median gap 39.4, IQR
  20.0–54.3, range 0–100, 194 arms ≥ 50 points, 396 ≥ 25, 72 ≥ 75, and the 71-arm low-response /
  high-stability corner.
* **The two identities §2.3 asserts for every row** — CR+PR+SD+PD equals the evaluable denominator,
  and disease control minus objective response equals the stable-disease proportion — hold for all
  552 arms with no exception.
* **All ten strata of §4.2** (arms and median gap each), including the exhaustiveness claim that the
  gap runs 27.2 to 43.6 across them.
* The patient-weighted sensitivity (18,318 patients, 7,213 stable-disease events, 39.4 pp).
* **§4.3's three size thresholds** (552/251/45.5%/105; 231/32/13.9%/11; 138/4/2.9%/2) and all five
  Figure 3 bands' arms, median n, zero-response counts and observed shares.
* **The census**, recomputed as arithmetic: 2,851 → 2,715 = 95.2%; 1,563 → 1,561 = 99.9%;
  4,414 → 4,276 = 96.9%; 4,235 distinct trials → 96.7%; and the record/trial difference is exactly
  the 179 trials matching both queries.
* **The regime map**: 44 conditions placed (each ≥ 3 arms and ≥ 3 accrual records), 16 at or below the
  5% null with exactly one non-zero at 4.2%, 28 defined → 14 → 50.0%, 7 of 29 → 24.1%, the
  31.8%/73.9% bound recomputed from each variant's own counts, the 0.0–47.8% zero-event interval, and
  "20 of 35 to 30 of 36" as design-contour count plus past-the-null count.
* **The accrual axis** rebuilt from the 1,837 raw records: 875 completed / 962 terminated, and the
  per-condition median enrolments 54 / 8 / 23 (exactly 54.5 / 8.75 / 23.75 before the producer's
  integer truncation, noted in the row).
* **§3.3's phase composition** — 197 phase 1 / 147 phase 2 / 9 phase 3 at the bottom of the axis
  against 133 / 96 / 37 elsewhere — reproduces **only** when contributing arms are counted once
  each; it is a hard-coded prose string in `endpoint_regime_map.py`, not a computed key, and this is
  the first check that it matches the data.
* **Both contours from first principles**: 17 patients for a 90% chance of one response at 12.8%, and
  79 for an exact single-stage design against a 5% null at α 0.05 / power 0.80, plus four grid points.
* **§6**: 19 control-token arms (agreeing with the corpus's own flag), the 8/8/3 registered-type
  composition, the 16/2/1 classification summing to 552 with the non-control arms, the 12-trial
  progression-at-entry strata (1 REQUIRED / 5 mentioned / 6 not), the 48.4% objective response of the
  single no-intervention arm recomputed from its own cells, and the 25-condition low-response corner
  with 4 carrying any control arm.
* **§7**: 18 documents, families 4/4/3/7 summing to 18 with matching identifier lists, 12 domains,
  7 consensus guidelines, earliest document 1998.
* **§8**: 12.8% (6/47, Wilson 6.0–25.2), 89.4% (42/47, 77.4–95.4), the 36-patient / 76.6-point gap,
  the fixed-event sensitivity on 46 (13.0%, 6.1–25.7; 91.3%, 79.7–96.6; 78.3) and its 1.7-point shift,
  the IMMUNOSARC II 23-vs-22 discrepancy, and the 88.9th percentile recomputed as 491 of 552 corpus
  arms with a smaller gap.

## Validation / baseline

The six known-answer controls above are the baseline, two of them cross-artifact or mutation-based
rather than self-referential. Two controls failed on the first run and caught real defects in this
lane's own harness; `checks/01` preserves that failing run (exit 2) with its five spurious mismatches
intact. `checks/02` is the corrected run (exit 0), `checks/03` the final run with the open-ended 40+
band added, and `checks/04` records the tree state and re-hashes every input at the moment of use.

## Provenance

* Lane start HEAD `673d330446ee07a8db3e83b817d9e619834d4d1f`; HEAD moved to
  `9a0ee12226deef23fabc72011c64bab9fee18763` during the run (other lanes share this checkout). All
  seven endpoint files were **unmodified and clean** in the working tree at start and at finish, and
  their sha256 digests are identical before and after (check 04) and are recorded inside the ledger.
* Manuscript read: sha256 `bae48dbd23966cc247d428448ea81116fef7aeabf718e5f2da74103014f30408`.
  Artifacts: corpus `1675e8d5…`, re-read `95ac62e8…`, regime map `3e1e4489…`, placebo calibration
  `3823ca78…`, prior-art audit `4bb09c63…`, discordance `6538ab26…`.
* Route followed from `systems/graph/publications.json` → `PUB-ENDPOINT.document.file` and
  `systems/graph/routes.json` → `RT-ENDPOINT-CHOICE.artifacts` → `systems/graph/artifacts.json` paths.
* Producer sources were **read** (`orr_dcr_reread.py`, `endpoint_regime_map.py`) to locate the cause of
  the one MISMATCH and to confirm a hard-coded prose string; none was executed, imported or edited.
* Harness: `rederive_claims.py`, Python 3 standard library only — no scipy, no numpy, no network, no
  paid API, no GPU. Runtime under 20 s wall clock, single CPU. Storage written by this lane:
  **184 KB total**, all inside the lane directory (ledger 46 KB / 99 rows, harness 42 KB / 616 lines,
  four check directories 68 KB, this file 17 KB). No repo copy, no worktree, no download, no corpus
  fetch, and no write to any tracked file.

## Limitations

* ⛔ This is a **re-derivation of printed numbers against committed artifacts**. It is not a review of
  the paper, not a check of the artifacts against the raw ClinicalTrials.gov payloads (those live on
  the `literature-cache` branch and were not fetched), and not a judgement on the corpus's inclusion
  rule, its retrieval protocol or its bias arguments.
* ⛔ Nothing here bears on efficacy, safety, selectivity, therapeutic window or clinical readiness for
  any agent in any disease, and nothing here is patient-specific advice. A gap between two endpoints
  is a fact about summarisation, never evidence that a treatment did anything. No wet-lab claim is
  made or implied.
* The one MISMATCH is an **order-statistic selector**, located in a producer line and traced to its
  effect on one figure's expected curve. This lane did **not** determine what the paper should do
  about it, did not prepare a diff, and did not check whether the same selector appears elsewhere in
  the repository.
* Coverage is the manuscript's **quantitative** claims. Prose readings, hedges, the §7 family
  transferability judgements, the §12 reference list and the Appendix A superseded-value table were
  not graded beyond the numbers they carry. Figure SVG contents were not opened.
* Three rows are UNKNOWN by construction, not zero, and each names its missing input above.

## Stop condition — met

Stopped at the **first pass** over the claims, with the controls green. No second pass, no repair, no
manuscript or producer edit, no diff, no gate run, no alternative reading sought for the MISMATCH.
Nothing was `git add`ed, committed or pushed; `scripts/preflight.sh` was not run; no subagent was
spawned; no network call was made; no write left this lane directory.

## Suggested next work (for the parent, not done here)

1. The 7.7 / 7.2 selector is a **manuscript-and-producer** question and belongs to the paper's owner.
   It is unpinned by any test, so whatever is decided, a pin on
   `_corpus_median_objective_response_pct` would keep it decided.
2. `V-PLACEBO20` closes with one read of `emc-endpoint-alternatives.json` → `E10`.
3. `A-CAPS` is the only row needing an input this repository does not hold; it would close if a
   producer retained the two queries' reported `totalCount` alongside the records it kept.
