---
id: DOC-ASSESS-EPITOPE-BENCHMARK-3-FINDING
title: "Independent assessment of EPITOPE-BENCHMARK-3: the 37 -> 34 pin correction re-derived from scratch, its guard re-tested, its minimality proved exhaustively"
level: L4
kind: assessment
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# ASSESS-EPITOPE-BENCHMARK-3 — five verdicts on a correction that changes a guard

Writes confined to this directory. **I applied no diff, changed no pin, guard or test, and touched
no file in EPITOPE-BENCHMARK, EPITOPE-BENCHMARK-2, EPITOPE-BENCHMARK-3, VACCINE-PATH-2 or
NEOANTIGEN-3.** All work is on copies under `sandbox/`. `git status --porcelain` over all five
subject directories is **empty** after every run, and the three subject files still carry their
original sha256 (`checks/13`), including `tabulate_epitopes.py` = `477dbfac…9ee7f`, the hash the
subject cites. `n = 15` and NEOANTIGEN-3's `assert len(VALIDATED) == 15` were not reopened.
No `git add/commit/push`, no `scripts/preflight.sh`, no subagent, no network (none attempted, so no
refusal was met or circumvented), no GPU, no paid API, no publication, no outreach. Cost $0.

⛔ Nothing here is an immunogenicity, presentation, efficacy, safety, selectivity,
therapeutic-window or clinical-readiness claim. Every number below is the width of a binomial
confidence interval, or the exit code of a test file.

## Verdicts at a glance

| # | question | verdict |
|---|---|---|
| 1 | ladder re-derived independently; 37 uniquely p-exact; 34 from attainability | **SUPPORTED-WITH-QUALIFICATION** |
| 2 | the guard is genuinely no weaker | **SUPPORTED** |
| 3 | minimality (one line, nothing else moved) | **SUPPORTED** |
| 4 | leaving `achieved_ci_width…` at 0.4515 is correctly scoped, and the two changes are independent | **SUPPORTED-WITH-QUALIFICATION** |
| 5 | the correction is falsifiable, and survives a concrete falsifier | **SUPPORTED** |

**Overall: the correction is sound and I would hand it to the owner as-is.** The two qualifications
are about how the subject *describes* its result, not about the number 34, the diff, or the guard.

---

## 1 · Independent re-derivation — SUPPORTED-WITH-QUALIFICATION

`indep_wilson.py` (`checks/01`, exit 0) implements the Wilson score interval from the closed form,
importing nothing from either lane. Two deliberate independences: **z was not copied** — it is
recovered by bisection on the erf-based normal CDF and lands on `1.959963984540054`, digit for digit
the lane's constant — and the width comparison against 0.20 is done in **50-digit `Decimal` with
exact `Fraction` k/n**, so no boundary result turns on float noise.

```
p-exact   -> 93 / 78 / 60 / 37
k=round   -> 93 / 78 / 60 / 34
k=ceil    -> 93 / 76 / 58 / 34
k=floor   -> 93 / 79 / 60 / 38
k=halfup  -> 93 / 78 / 60 / 34      (a fifth convention the subject did not enumerate)

ladders matching 93/78/60/37 : ['p-exact']
ladders matching 93/78/60/34 : ['k=round', 'k=halfup']
```

**Confirmed, and it is the load-bearing claim: 93/78/60/37 is p-exact and nothing else.** `k=ceil`
is excluded by the 0.7 and 0.8 rows (76, 58), `k=floor` by 0.7 and 0.9 (79, 38). So the retired 37 is
a coherent value from an abandoned convention, not a typo and not `k=floor` — the subject's central
diagnosis holds, and its correction of the parent adjudication ("Neither convention yields 37") is
right.

**Confirmed digit for digit, the attainability argument.** At n = 37 the attainable
`k = round(0.9 × 37) = 33` gives width **0.204233 > 0.20**; at n = 34, `k = 31` gives **0.199139 ≤
0.20**; p-exact at n = 37 gives **0.198803**. All three match the subject's printed digits exactly.

**Qualification (a) — a uniqueness claim over an unenumerated space.** "Exactly and only `k=round`"
for the corrected ladder is one convention too strong: `k=halfup` (round-half-up rather than Python's
banker's rounding) produces the identical ladder, because no `p·n` tie arises at the relevant n.
This is a distinction without a difference — the two rules are the same convention modulo
tie-breaking — but the *37* side of the claim is the one that carries weight and it survived a wider
search than the subject ran, while the *34* side is unique only up to tie-breaking.

**Qualification (b) — the corrected convention loses monotonicity, and the subject does not say so.**
Under `p-exact` the width is monotone decreasing in n, so 37 is a genuine **threshold**: every
n ≥ 37 meets the criterion. Under `k=round` it is not. `checks/01` and `checks/12`:

```
k=round at p=0.9: n in [34,400) that FAIL width<=0.20 -> [36, 37]
smallest n such that ALL m >= n meet the criterion under k=round -> 38
```

So after the correction the "n required" column means *the smallest n at which a real sample can
meet the criterion*, not *the sample size above which it is met*. A reader who takes 34 as a
threshold would be wrong at n = 36 and n = 37. This does not disturb 34 as the answer to the
question the lanes are asking, and it changes nothing about the verdict (n = 15 is short of every
candidate), but it is a real property of the adopted convention that the diff's notes and the
subject's §5 do not mention. Recommendation to the owner: one clause in the `n_for_width` note.

## 2 · Is the guard no weaker? — SUPPORTED

**Structural inventory (`checks/07`).** Assertion count **15 before, 15 after**. Diffing the two
files with comments and blank lines stripped leaves exactly two changed executable lines: the
literal `"0.9":37` → `"0.9":34` inside the same exact dict-equality assertion, and the printed
banner. `def ck`, the `fails` accumulator, `if fails: … sys.exit(1)` are unchanged. **Nothing was
removed, loosened, made conditional, wrapped in a try, or moved behind a condition** — there is no
new condition anywhere. The equality is still a full dict comparison over all four rows, so it also
still rejects extra or missing rows.

**Do the eleven fixtures discriminate, or trip for unrelated reasons?** The subject's battery records
only the exit code. I re-ran the battery independently (`indep_guard_battery.py`, `checks/08`,
exit 0), written here, and additionally **parsed the FAIL reason of every case**:

* All **11** claimed fixtures exit 1 with the reason list exactly `['Wilson n table changed']` — one
  reason, the right one. None trips a different assertion.
* Both controls exit 0 (correct ladder; `34.0` as a float, which `==` treats as the same value).
* **Two fixtures I added**: a spurious extra row `0.95: 20`, and `"0.9": "34"` as a string — both
  rejected, both for the Wilson reason. The dict equality is type-strict.
* **Three liveness fixtures I added** to confirm the *rest* of the guard survived the patch:
  `verdict → SUFFICIENT`, `achieved_ci_width → 0.4507`, `BENCHMARK_ELIGIBLE.n → 16` each exit 1 with
  their own distinct reason. The patch did not collaterally disable anything.

**Counterfactual (`checks/10`), reproduced independently of the subject's `sandbox-pinonly`:**
patching *only* the pin to 34 and leaving the artifact at 37 gives exit **1**,
`FAIL: - Wilson n table changed`. The producer change is necessary; the subject is right that the
tempting one-line fix breaks the guard.

**Where the subject slightly overstates.** It says the corrected pin's discriminating power is
"strictly greater on one axis (it rejects 37)". Before the patch the guard rejected 34 and accepted
37; after, the reverse. The *accepted point moved*; the power is the same shape. That is a
rhetorical flourish, not a defect in the change, and it is why I graded item 2 on the structural and
fixture evidence rather than on that sentence.

**One gap, pre-existing and unchanged by the patch (so not a weakening).** The guard checks the
FINDING.md prose only for the 0.5 row (`|\s*0\.5\s*\|\s*93\s*\|`), n = 15, n = 6 and `0.4515`. The
**0.9 prose row is unguarded before and after** — the patch's prose edit `| 0.9 | 34 | 15 | 19 |`
(arithmetically correct: 34 − 15 = 19) would not be caught if it drifted. Strengthening it is out of
this correction's scope and I do not propose it here; I record it so the owner is not left thinking
the prose is pinned at 0.9 when only the JSON is.

## 3 · Minimality — SUPPORTED

Verified on my own copies, not on the subject's `sandbox/`.

* `checks/03`: the unapplied patch applies cleanly to a fresh copy (`patch -p1`, exit 0, four files).
* `checks/04`: running the **patched producer** over `epitope-records.json` regenerates the artifact
  **byte-identical** to the diff's hand edit — sha256 `2bb573ff…46c9` both ways. The diff is what
  the code emits, not a typed number.
* `checks/05`: regenerated vs the **original committed** artifact — `diff` exit 1 with exactly
  **one changed line** (`"0.9": 37` → `"0.9": 34`), 2 diff lines out of **585**.
* `checks/06`, the check the subject did not run: an **exhaustive leaf-by-leaf** comparison of the
  two JSON documents. **416 leaves each; the differing path set is exactly
  `['/sufficiency/n_required/0.9']`.** Explicitly confirmed unchanged: `0.4515`, `INSUFFICIENT`,
  `shortfall_vs_sens_0.5` = 78, `shortfall_vs_sens_0.8` = 45, `shortfall_vs_prereg_floor` = 15,
  `preregistered_floor` = 30, `n_available_benchmark_eligible` = 15, `n_available_ms_eluted_only` = 6,
  the criterion string, **all 40 record ids and every stratum's id list**,
  `benchmark_eligible_detail`, `distinct_fusions_in_benchmark`, `per_allele_depth`,
  `quantitative_observations`, and the top-level key set.
* `checks/09`: the patched tree's guard exits **0**, and its stdout differs from the baseline stdout
  on **one line**, only in `37` → `34`.
* `checks/11`: no *stale* 37 is left anywhere in the patched EPITOPE-BENCHMARK tree.
  `VALIDATED-EPITOPE-TABLE.md` does not print the sufficiency ladder at all (the `37`/`22` hits in
  the tree are a peptide length and a peptide length column, unrelated), so the diff does not leave a
  sibling artifact quoting the superseded value. Every surviving `37` is a dated
  "SUPERSEDED VALUE, PRESERVED" note or the adjudication record.

Minimality is not merely claimed here; it is the strongest-evidenced item in the package.

## 4 · The left-open `0.4515` — SUPPORTED-WITH-QUALIFICATION

**Mechanically independent: confirmed.** The producer computes the achieved width at a *different
call site* — `wilson_width(0.5, n_bench)` — which the patch does not touch, and the exhaustive leaf
diff (`checks/06`) shows `achieved_ci_width_at_sens_0.5_with_n_available` still 0.4515 after
regeneration. Applying this diff cannot move that field. Leaving it alone is also the *safe* choice:
that value is pinned in two places (the JSON assertion and a literal `"0.4515" in FINDING.md` prose
check), so moving it is a wider edit than this one.

**Conceptually independent: no — and this is the qualification.** `checks/12` computes both digits
from scratch: at n = 15, `phat = 0.5` gives **0.451534 → 0.4515**, while the attainable
`k = 7` or `k = 8` (7.5 is an exact tie; both sides are symmetric) gives **0.450735 → 0.4507**.
**0.4515 vs 0.4507 is the same p-exact-versus-integer-k question as 37 vs 34, at a second call
site.** The subject's §5 calls it "a *separate* pinned quantity on a *separate* line"; that is true
of the code but not of the substance. Its §10 does concede the dependency, so the package is not
self-contradictory — but the two framings pull in different directions and §5 is the one a reader
meets first.

**Consequence the owner should be told, which neither lane states.** Applying this diff *alone*
leaves a single JSON object in which the requirement column follows the integer-k convention while
the achieved-width figure in the same object follows the p-exact convention it just abandoned. That
is a smaller defect than the one being fixed, and it is a defensible staging decision — but it is an
internal convention inconsistency, not merely an "OPEN" separate item, and it should be recorded as
such so the second half is not forgotten. **Leaving it out of this diff is right; describing it as
independent is half right.**

## 5 · What would falsify the correction — SUPPORTED

Concrete and runnable: `falsifier.py` (`checks/14`, exit **0**), which composes five conditions each
of which would sink the correction on its own.

```
cd <this lane> && patch -p1 -d sandbox/patched < ../EPITOPE-BENCHMARK-3/0001-correct-wilson-0.9-pin-37-to-34.patch
python3 falsifier.py     # exit 0 = correction survives; exit 1 = falsified, with reasons
```

| condition | what its failure would mean | observed |
|---|---|---|
| **F1** smallest n with `k=round(0.9n)` meeting width ≤ 0.20 is 34 | 34 is not the attainable minimum — the target is wrong | 34 ✓ |
| **F2** width at n = 37, k = 33 is > 0.20 | 37 *is* attainable; the whole case against it collapses | 0.204233 ✓ |
| **F3** patched producer regenerates the artifact byte-identically | the artifact was hand-edited to a value the code does not emit | sha stable ✓ |
| **F4** the committed-vs-patched leaf difference set is exactly `{/sufficiency/n_required/0.9}` | the change is not minimal; something else moved | exactly that ✓ |
| **F5** corrected guard: correct ladder → 0, stale 37 → 1 | the pin no longer discriminates | 0 / 1 ✓ |

The sharpest single falsifier is **F2**: it is one line of interval arithmetic, it needs no code from
either lane, and if `wilson_width(33/37, 37) ≤ 0.20` then 37 would be attainable and the correction
would have no case. It is not.

A sixth condition I deliberately did **not** put in the falsifier, because failing it would not
falsify the correction: "every n ≥ 34 meets the criterion". That is **false** (n = 36, 37 fail) — see
§1 qualification (b). It falsifies a *threshold reading* of the corrected table, not the value 34.

---

## What I checked, and what I did not

**Checked** — re-derivation of z and of five convention ladders in exact arithmetic; the three
attainability digits; monotonicity of both candidate conventions; the patch applying cleanly to a
fresh copy; producer-regenerated == hand-edited (sha); regenerated vs committed at line and at leaf
granularity (416 leaves); assertion inventory and normalised code diff of the guard; 18 guard
fixtures with parsed failure reasons, including 5 of my own; the pin-only counterfactual; residual
stale values across the patched tree; both achieved-width digits; the subject's cited provenance
hash; and that the subject lanes are byte-unchanged.

**Not checked, and outside this assessment.** (i) Whether a sufficiency table *should* use an
integer-k convention at all — I assess the correction against the convention the lanes settled on,
and I record that the alternative is coherent, not that it is wrong. (ii) `n = 15`, the
`INSUFFICIENT` verdict, the ~6× shortfall, and NEOANTIGEN-3's count — untouched, unexamined, out of
scope by instruction. (iii) The criterion's attribution to PUB-VACCINE-PATH (the manuscript no longer
prints the ladder), which the subject already records as unverified attribution — I did not
re-verify it either. (iv) The site census in `SITE-LIST-34-vs-37.md` beyond the EPITOPE-BENCHMARK
tree. (v) Whether the owner should apply the diff — that is the owner's call, not mine.

**Limitations.** Convention uniqueness is over the **five** rules I enumerated, not over all
conceivable rules; a sixth rule producing 93/78/60/37 cannot be excluded by search, only by the
observation that p-exact is what the code demonstrably runs. All guard evidence is about
`check_consistency.py` in isolation; I did not run any repository-wide gate (`scripts/preflight.sh`
is fenced), so I cannot speak to whether some other check elsewhere reads this artifact.

**Stop condition — reached.** Five verdicts returned with executed evidence; the two qualifications
are recorded rather than smoothed and neither requires the diff to change. No further work is
authorised in this lane, and the diff remains the owner's to apply.

## Artifacts

`indep_wilson.py`, `indep_guard_battery.py`, `field_invariance.py`, `indep_width_and_falsifier.py`,
`falsifier.py`, `sandbox/{base,patched,pinonly}` (my own copies), and `checks/01`–`checks/14` —
**every attempt preserved, real exit codes, no pipes**, including the two deliberate non-zero exits
(`checks/05` exit 1, a `diff` that found the intended one-line change; `checks/10` exit 1, the
pin-only counterfactual that must fail).
