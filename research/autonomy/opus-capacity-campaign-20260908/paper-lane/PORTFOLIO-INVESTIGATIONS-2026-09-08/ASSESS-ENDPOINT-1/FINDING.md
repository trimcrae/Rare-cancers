---
id: DOC-ASSESS-ENDPOINT-1
title: "ASSESS-ENDPOINT-1 — independent methods and evidence assessment of the ENDPOINT-1 claim-re-derivation ledger"
level: L4
kind: assessment-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ASSESS-ENDPOINT-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
subject: research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/ENDPOINT-1
---

# ASSESS-ENDPOINT-1 — assessment of ENDPOINT-1

Independent assessment of ONE unadjudicated result: the ENDPOINT-1 claim-re-derivation ledger for
PUB-ENDPOINT. Nothing in the subject lane was modified; every execution below ran on copies, on the
manuscript artifacts read in place, or against a mutated copy of the harness with its output
redirected outside `ENDPOINT-1/`. No `git add`, commit, push or preflight; no network; no subagent.

## Verdicts

| # | question | verdict |
|---|---|---|
| 1 | is the "recomputed, not read back" distinction real? | **SUPPORTED-WITH-QUALIFICATION** |
| 2 | do the six known-answer controls control? | **SUPPORTED** |
| 3 | is the MISMATCH correctly diagnosed and bounded? | **SUPPORTED** |
| 4 | are the three NOT-RE-DERIVABLE rows honestly scoped? | **OVERSTATED** |
| 5 | what would falsify the ledger? | concrete test given below |

---

## 1 · The RECOMPUTED / READ-BACK distinction — SUPPORTED-WITH-QUALIFICATION

**The distinction is real, and it is the ledger's principal strength.** Two independent lines of
evidence.

*(a) I recomputed 40 quantities myself, from the raw rows, with code that neither imports nor copies
`rederive_claims.py`* (`checks/02-independent-recompute`, exit 0, **40 of 40 agree**). These span
every artifact family the ledger touches: arm and trial counts (552 / 138); the four-cell identity
and the gap identity across all 552 arms (0 violations each); median gap 39.4, type-7 IQR 20.0–54.3,
range 0–100, 194 / 396 / 72 arms at 50 / 25 / 75 points; the 71-arm low-response corner; the
patient-weighted 18,318 / 7,213 / 39.4; all five Figure-3 bands' arms, median n, zero-response counts
and observed shares; the accrual record total (1,837); Wilson intervals for 6/47, 42/47 and the
46-denominator sensitivity computed from my own closed form; the 88.9th-percentile placement
(491/552); the exact single-stage design N = 79 and the 90%-power n = 17 from my own binomial; the
single NO_INTERVENTION arm's 48.4%; the 19 `control_arm_candidate` flags; and the 1998 earliest
prior-art year. These are values a read-back ledger could not have produced correctly by accident.

*(b) An AST scan of the harness* (`checks/08-recomputed-label-scan`) checked, for every row labelled
RECOMPUTED, whether its derived expression contains any computation at all rather than a bare key
lookup. **56 rows carry computation inline; 7 were flagged; on inspection 5 of the 7 are locals
computed upstream** (`sums_ok`, `median_orr`, `lowmix`/`restmix` from `phase_mix()`, and `V-484`,
which is recorded, `ROWS.pop()`ed and re-recorded with a real recomputation).

Three qualifications, all real:

* **The headline number in ENDPOINT-1's FINDING does not match its own ledger.** The FINDING says
  "Of the 95 that reproduce, **72** are RECOMPUTED". The ledger's own rows give
  **78** REPRODUCES+RECOMPUTED and 17 REPRODUCES+READ-BACK (`checks/01-ledger-class-counts`). 72 is
  the value of a different claim in the same document (`M-GE75`, 72 arms at or above 75 points). The
  error is conservative — it understates the artifact — but it is a transcription error in the
  document's single most load-bearing summary figure.
* **Two rows are mislabelled RECOMPUTED when they are read-backs**: `V-19`
  (`p3["control_arms_found"]`) and `V-PROG` (four direct `P4_progression_at_entry_strata` lookups).
  `V-19`'s substance is separately recomputed by `V-19C` from `C2_arms[].control_arm_candidate`, so
  no claim is left unchecked; `V-PROG` is a genuine read-back with no recomputing sibling. The honest
  count of genuinely recomputed REPRODUCES rows is therefore **76**, not 78 and not 72.
* **`Z-MEDORR-SELECTOR` is counted as a REPRODUCES row.** It is a diagnostic that the producer's
  selector reproduces 7.7 — i.e. part of the MISMATCH's explanation. Counting it in the REPRODUCES
  column is defensible but mildly flattering; the FINDING does not flag it.

Verdict: the instrument really recomputes and is much stronger than a read-back ledger; the specific
count quoted for it is wrong in the document, and two labels are wrong in the artifact.

## 2 · The six known-answer controls — SUPPORTED

Every one of the six was **shown to fail** under a mutation aimed at it, on copies
(`checks/03-control-falsifiability`, `checks/04-control-falsifiability-rerun`). None is vacuous.

| control | mutation applied | result |
|---|---|---|
| Wilson closed form vs. score bisection | `wilson(z=1.959…)` → `z=1.0` | **FAIL** `[8.7,18.4]` vs `[6.0,25.2]`, harness exit 2 |
| binomial known answers | drop the last term of the upper tail | **FAIL** `[0.0,0.0,0.99757]`, exit 2 |
| type-7 quantile | return the lower order statistic | **FAIL** `[2.0,1.0,3.0]`, exit 2 |
| cross-artifact `R2` vs `C2` cells | corrupt one `R2_per_arm_rows[].gap_pp` by +9.0 | **FAIL** 1 mismatched row, exit 2 |
| mutation control: median gap must move | make the mutation vacuous (`SD += 0`) | **FAIL**, exit 2 |
| mutation control: identity must break | (a) vacuous `SD += 0`; (b) identity-preserving `SD` **and** `evaluable_n` both `+40` | **FAIL** in both, exit 2 — (b) fails this control alone while the median-gap control still passes, so the two are not redundant |

Two methodological notes rather than defects. First, `checks/03` contains three mutations whose `sed`
patterns did not match the harness source, so those mutations were silently not applied and the run
reported all-PASS; that was **my** harness error, is preserved as it ran, and is corrected in
`checks/04`. It is itself a demonstration of the failure mode ENDPOINT-1 caught in its own
`checks/01` — a control that cannot fire looks identical to a control that passes. Second, controls 5
and 6 mutate a `deepcopy` and assert that a corruption *would* be visible; they do not drive a
corrupted corpus through the 99 claim rows. That is a weaker guarantee than an end-to-end mutant, but
it is not vacuous, and my mutation M4 supplies the end-to-end case for the cross-artifact control.

The float comparator `_eq` uses an absolute tolerance of `5e-2` on values printed to one decimal.
A genuine discrepancy of exactly 0.05 would pass. Nothing in this ledger sits at that boundary
(the one MISMATCH is 0.5), but the tolerance is wide enough to be worth pinning if the harness is
reused.

## 3 · The single MISMATCH — SUPPORTED, in both directions

Re-derived independently (`checks/02-independent-recompute`):

* The 552 per-arm objective-response percentages have middles **6.666666666666667** and
  **7.6923076923076925**; their mean is **7.17948717948718 → 7.2**. `orrs[len(orrs)//2]` returns the
  **upper**, 7.6923… → **7.7**. The diagnosis is exactly right, including the mechanism.
* **The printed band expectations are the p = 7.7% curve, digit for digit.** Recomputing
  `mean over arms of (1-p)^n` per band at p = 0.077 returns **81.0 / 61.0 / 32.8 / 11.5 / 0.5** — the
  five printed values. That confirms the mismatched value is the p actually drawing Figure 3, not an
  incidental number.
* **The claimed bound at the true median reproduces exactly**: at p = 0.072 the expectations are
  **82.1 / 63.1 / 35.3 / 13.3 / 0.7**, the five values ENDPOINT-1 states.
* **The qualitative reading survives, as claimed.** Observed 77.0 / 57.8 / 30.1 / 8.3 / 0.0 is below
  expected in **all five** bands at both p, and the gap widens at 7.2. All band arms, median n,
  zero-response counts and observed shares reproduce from the raw cells.
* The band rows are scored against the artifact's own stored p, which is why four rows that were
  MISMATCH in ENDPOINT-1's `checks/01` are REPRODUCES in `checks/03`. That decomposition — band
  arithmetic tested separately from the choice of p — is legitimate and is disclosed in the FINDING,
  but a reader comparing the two runs should know that the drop from 12 mismatches to 1 is partly a
  scoring change and not only defect repair. ENDPOINT-1 also describes its `checks/01` spurious
  mismatches as "five"; there were **seven rows** arising from five distinct harness causes.

I did not attempt any reading under which 7.7 is a median, and this lane proposes no repair.

## 4 · The three NOT-RE-DERIVABLE-LOCALLY rows — OVERSTATED

**Two of the three are derivable from files already committed in this checkout.** One is a genuine
unknown.

* **`A-CAPS` — not a missing input.** ENDPOINT-1's FINDING states that "`C5_retrieval_provenance`
  in the committed corpus retains no per-query reported-total field". It does
  (`checks/06-acaps-accrual-provenance`). `endpoint-corpus.json` →
  `C5_retrieval_provenance.accrual` contains, verbatim:
  `ctg_accrual_terminated_onc: {total_count_reported_by_the_api: 2027, records_returned: 1000}` and
  `ctg_accrual_completed_onc_phase2: {total_count_reported_by_the_api: 16035, records_returned: 1000}`.
  That is the entire claim — both caps at 1,000 and both reported totals — inside the very artifact
  the row names, and the same section carries the equivalent field for all ten arm queries. This row
  is an **unrun check, not a missing input**, and the stated justification for it is factually
  incorrect. It should be a REPRODUCES row.
* **`V-PLACEBO20` — derivable, and ENDPOINT-1 says so.** The 20% placebo objective response is in the
  committed `research/manuscripts/endpoint/emc-endpoint-alternatives.json` →
  `E10_indolent_tumour_placebo_calibration` (Gounder 2018, PMID 30575484), which I read
  (`checks/05-not-rederivable-rows`). ENDPOINT-1 states plainly that the file is a companion outside
  the six route artifacts and that it chose not to open it. The scoping is honest; the **verdict
  label is wrong** — "NOT-RE-DERIVABLE-LOCALLY" and `exact_missing_input` claim a missing input where
  there is only an unrun read. It is one `json.load` from closing.
* **`V-OVERLAP` — genuinely unknown, correctly scoped.** Whether the 282-patient pooled French
  cohort overlaps the 100 patients of PMID 37777684 requires centre- or patient-level rosters. The
  repository files mentioning those PMIDs are the manuscript, the producer, the calibration artifact,
  a retraction sweep and a test — none holds enrolment rosters. UNKNOWN, not zero, is right.

So the true tally is closer to **97 REPRODUCES / 1 MISMATCH / 1 NOT-RE-DERIVABLE**, and the ledger's
own headline understates what it could have established while overstating what is unavailable. The
direction of the error is unusual and worth saying plainly: this lane's scoping error made its result
look *weaker*, not stronger. But an "exact missing input" that is present in the named artifact is
the one kind of scoping error that matters, because it is what a reader would otherwise trust.

## 5 · What would falsify the ledger — a concrete runnable test

The ledger's core claim is: *these printed values are recoverable from the committed artifacts, and
the harness that says so can fail.* Three tests falsify it, in decreasing strength.

1. **End-to-end mutant, the decisive one.** Copy the six artifacts; perturb one `C2_arms[i].cells`
   cell in the copy without touching `evaluable_n`; run the harness with `END` pointed at the copy.
   A sound ledger must (a) fail the four-cell identity control and exit 2, and (b) turn at least the
   `M-IDENTITY`, `M-MEDGAP` and band rows to MISMATCH. If the summary still reads 95/1/3, the ledger
   is measuring the harness's constants rather than the artifacts. This runs in seconds and is the
   test I would hand to the parent. Its scaffolding already exists at
   `ASSESS-ENDPOINT-1/work/run_mutations2.sh`, which mutates the harness copy; redirecting `MUT_END`
   at a perturbed artifact copy is a one-line change.
2. **Second-implementation disagreement.** Recompute the same quantities with a different toolchain
   (e.g. `statistics.median` vs. type-7 quantile at q=0.5; `scipy.stats.binom.sf` if it were
   available) and require agreement to 0.05. My `work/independent_recompute.py` is that test at
   n = 40 and found no disagreement; extending it to all 76 recomputed rows would either confirm the
   ledger or find the next `Z-MEDORR`.
3. **The specific unclosed rows.** `A-CAPS` falsifies as written: assert
   `C5_retrieval_provenance.accrual[q]["total_count_reported_by_the_api"] == (2027, 16035)` and
   `records_returned == 1000`; it passes, so the NOT-RE-DERIVABLE verdict is false. Likewise assert
   the 20% in `emc-endpoint-alternatives.json → E10` for `V-PLACEBO20`.

A fourth, cheap and worth running once: an assertion that pins
`_corpus_median_objective_response_pct`. ENDPOINT-1's claim that **nothing pins 7.7** is consistent
with everything I saw, and it is the reason this defect survived to a route whose next action reads
"review the manuscript for external posting".

## What I checked, and what I did not

Checked: the ledger's class counts against its own rows; 40 quantities recomputed independently from
raw cells, accrual records and closed-form statistics; every RECOMPUTED label by AST scan plus manual
inspection of the 7 flagged; all six controls under targeted mutation; the median and both band
curves; all three NOT-RE-DERIVABLE rows against committed files; reproduction of the whole ledger
from a patched copy of the harness (`95/1/3`, controls green, identical to `checks/03`).

Not checked: the remaining ~36 recomputed rows I did not independently duplicate (regime map,
prior-art audit and census families were spot-checked only, via ledger reproduction rather than a
second implementation); the artifacts against the raw ClinicalTrials.gov payloads on
`literature-cache` (not fetched — that is direct egress and out of fence); whether the manuscript
quotes any number the ledger omits entirely — **the ledger's coverage of the manuscript was not
audited**, only the rows it contains, so a claim absent from all 99 rows would not have been caught
here; figure SVG contents; and any scientific question about the paper's argument.

⛔ Nothing here bears on efficacy, safety, selectivity, therapeutic window or clinical readiness of
any agent, and nothing here is patient-specific advice. No wet-lab claim is made or implied.

## Environment problem encountered — reported, not worked around

Mid-run the container's root filesystem reached **100% full** (`/dev/vda` 252G, 0 bytes available;
after freeing my own working copies, 1.7 MB). Command stdout began failing with ENOSPC. I deleted
**only files this lane created** (`work/mut/run`, one temp script) and completed the remaining checks
by pointing the mutated harness at the artifacts in place and redirecting output to files. **No
campaign evidence directory was touched**, no wildcard delete was used, and the session scratchpad
(4.4 GB) was left intact. This is reported as a resource problem for the parent, per the campaign
evidence-retention rule; it is not a cleanup authorisation.

## Limitations

* Assessment of ONE lane's methods and evidence. Not a review of PUB-ENDPOINT, not an adjudication,
  not a check of ENDPOINT-1 against any other lane.
* My mutation battery proves each control **can** fail; it does not prove the control set is
  sufficient. A defect that leaves all six controls green and every recomputed row equal would pass
  both ENDPOINT-1's harness and mine.
* `checks/03` contains three mutations that did not apply. Preserved as run; superseded by
  `checks/04`. Both are in the record.
* The count "76 genuinely recomputed" is my reading of two mislabelled rows; the parent may score
  `V-19` differently since its sibling row does recompute the same quantity.

## Stop condition — met

Stopped after answering all five questions with executed evidence, at the 20–25 minute checkpoint.
No repair, no diff, no edit to the subject lane, no manuscript or producer change, no gate run, no
pin added, no second assessment pass.
