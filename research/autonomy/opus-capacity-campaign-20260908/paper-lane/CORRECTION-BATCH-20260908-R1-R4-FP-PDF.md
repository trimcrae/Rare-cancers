# Batched interpretation correction — R1, R4, FP commissioning, PDF equivalence

**2026-09-08, parent. ONE batched correction. ⛔ No new worker, no auditor, no simulation, no test,
no source request, no algorithm repair, no rerender, no re-audit.** Originals, code, raw data and
exit records are preserved unchanged; this appends dispositions beside them.

---

## 1 · R1 — the flat-band assertion is wrong, including in my own earlier correction

**Withdrawn:** "the censored delta is identical for R = 3–13 at every extent" and "extra rows bought
nothing between 4 and 13".
**Also withdrawn:** my own first correction, which narrowed it to "R = 3–10 at L = 180". That was
still wrong — R3 = −6 there, not −5.

Re-derived by the parent from `RUN-01.stdout.json`, exact-coordinate arm, censored delta vs truth:

| last time L | flat band at the best value | best | values outside it |
|---|---|---|---|
| 45.0 | **R = 2–13** | −25 | R19 −30, R25 −36 |
| 90.0 | R = 3–13 | −16 | R2 −17, R19 −19, R25 −23 |
| 135.0 | R = 3–13 | −10 | R2 −12, R19 −13, R25 −15 |
| 168.0 | R = 3–13 | −7 | R2 −10, R19 −11, R25 −12 |
| 180.0 | **R = 4–10** | −5 | R3 −6, R13 −6, R19 −7, R25 −11 |

So the claim fails at **both** ends: at L = 45 the band is *wider* than R3–13 (R2 is also flat), and
at L = 180 it is *narrower* (R4–R10, with R3 and R13 both at −6). "No gain between 4 and 13" is
contradicted at L = 180, where R13 is worse than R4–R10.

### Scope corrections carried with it
- ⚠ **These are failures and sensitivities of THIS reconstruction implementation on ONE synthetic
  cohort.** They are **not** evidence of information-theoretic unreconstructability, and **not** a
  journal-wide density requirement. No reporting standard follows.
- ⚠ **Changing uniformly spaced R also moves the interior row locations.** That is a different
  manipulation from adding rows while holding the existing locations fixed: some comparisons across
  this grid are nested and others are not, and the table does not separate the two.
- ⚠ **The internal 0.05 criterion alone is not full clinical eligibility.** That all 104 arms were
  admissible under `MAX_KM_DEVIATION` says what that guard does not catch, not that the
  reconstructions are fit for use.
- ⚠ **Actual executed scope is 50 crossed cells plus the sentinel and the rounding probe = 52 cells
  × 2 arms = 104 reconstructions**, not any smaller sketched grid.
- ⛔ **The anchoring contrast was NOT performed.** The anchoring contract must not be described as
  complete.
- ⛔ Closed S4 and deleted raw evidence are **not** recreated.

**Disposition: R1 is CLOSED as the bounded cross-grid diagnostic that was actually executed.** Not a
new paper, not a reporting-standard promotion.

---

## 2 · R4 — one general sentence withdrawn, and a rank arithmetic slip

**Withdrawn: "A and C bracket the admissible range" / "bracket the convention space."** That is not
what they do:
- **A deletes observations, with no guaranteed ordering** relative to B or C.
- **B and C are extremal imputation scenarios for a specified missing-probe count under fixed
  normalisation.** They are not general bounds on the between-arm delta, and not bounds over all
  plausible missingness models.

**The structural reading stands and is the point:** all 906 assigned probes are persisted in 12/12
runs, so A, B and C coincide **structurally** across the 862 genes. ⚠ Therefore this result
**cannot validate missing-data handling and cannot demonstrate fair calibration** — the zero-free
block never exercises the imputation or deletion branches at all. ⚠ And **two sentinel matches
(TAF15, FUS) do not prove every implementation path**; they check the two paths they touch.

⚠ **Rank arithmetic corrected:** "9.05 % of 862 = rank 78 exactly" is wrong as written. 9.05 is a
**rounded** percentage; rank 78 comes from the underlying unrounded count, not from multiplying the
rounded figure. The rank is right; the derivation quoted for it was not.

**No live manuscript quantity consumes this result**, so **no paper correction and no promotion is
needed.** The tables, the real exit codes and the W20e EWSR1 NULL are preserved unchanged.

⚠ **The B1/B2 denial closes expanded-panel continuation under current inputs.** No retry, no
threshold or default change, no endpoint change, no new planner, no unchanged whole-paper review.

---

## 3 · FP — unmeasured evidence is not a commissioning gate

⚠ My FP commit listed the frozen handoff's §5 items — no clause-1 blind seat, 25 P1s
undispositioned, no preflight, no ablation, no source-to-generator check — in a way that could read
as preconditions.

**They are NOT root-required gates on the one final ultra review.** Root is explicit: do not add the
optional clause-1 seat, the 25-P1 prepass, a broad review, an ablation or a full preflight as a
commissioning condition. The unmeasured evidence stays **truthful and visible** — it is genuinely
unmeasured — but it is a description of what has not been done, **not** a checklist standing between
the frozen package and its review. The old missing 18:19:19Z pytest exit likewise stays unmeasured
and is not a gate.

---

## 4 · PDF rebuild — page counts do not prove content equivalence

⚠ **Withdrawn:** "page counts are identical across the two builds, which is the check that content
did not move."

Equal page counts do **not** establish that only the stamps changed. What actually supports content
equivalence is a **text/semantic comparison** — and that was performed on the **first** build, whose
record extracted text and verified the three vaccine-path corrections, absence of truncation and
surviving figure captions. For the **second, corrective** build I read page counts and the stamp
lines only.

So the honest statement is: the second build's sources were untouched between builds and its stamps
are now consistent and unqualified; page-count equality is **consistent with** content equivalence
and is not a proof of it. ⛔ No rerender and no new audit is being run to upgrade this wording.

---

## 5 · Status of these artifacts

⚠ The four PDF pairs, the I1 fix, the provenance equivalence entry and the graph bytes remain
**collected, not root-accepted.** Files existing is not acceptance.
