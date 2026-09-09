---
id: DOC-PORTFOLIO-INVESTIGATION-MORTALITY-4-2026-09-09
title: "MORTALITY-4 — the §6 restatement MORTALITY-3 left out, an independent re-derivation from first principles, and the exact regeneration cost of claim-coverage.json"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# MORTALITY-4 — finishing the correction MORTALITY-3 scoped out, and pricing what applying it costs

## 1. The question

**Does §6 of `research/manuscripts/emc-mortality-mechanisms-paper.md` restate, without numbers, the
generalisation MORTALITY-3's §4.2 diff withdraws — and if so, what exact unapplied §6 diff removes it
while remaining consistent with that diff, and what precisely does regenerating
`research/manuscripts/claim-coverage.json` afterwards involve?**

## 2. Merit

A number-free restatement of an unsupported claim is the harder half of the correction: it survives
every numeric consistency check in this repository precisely because it carries no figure to check.
MORTALITY-3 named the §6 site for the owner and deliberately left it out of its own diff, so the
manuscript, with MORTALITY-3's diff applied, would say in §4.2 that the cross-literature comparison
is not established and then in §6 assert the generalisation anyway. Closing that gap costs two
sentences. Pricing the downstream census cost means whoever applies owns it knowingly rather than
discovering it as a CI failure. Nothing here touches a patient, a cause of death, a survival curve,
a treatment or a clinical decision; the unit throughout remains a sentence, never a patient.

## 3. The evidence gap this closes

Three, all concrete and all left open by the sibling lanes:

1. **MORTALITY-2's numbers had been re-run, but never re-derived independently.** MORTALITY-3 re-ran
   MORTALITY-2's own scripts. Re-running the same code proves reproducibility, not arithmetic. Nobody
   had recomputed the Fisher test, the exact stratified conditional test, the Mantel-Haenszel odds
   ratio or the two standardisations from the stratum counts with independent arithmetic.
2. **No §6 diff existed** — MORTALITY-3 §7 item 1 says so explicitly.
3. **The claim-coverage cost was named but never quantified.** MORTALITY-3 said the artifact would go
   stale. It did not say by how much, nor that it is **already stale for eight other documents**,
   which changes what "regenerate it" actually means (§6 below).

## 4. Step 1 — re-derivation. Every load-bearing number reproduces, and two are explained

### 4a. Byte-identity re-run (`checks/01`–`07`)

The six MORTALITY-2 scripts and `handcheck-labels.json` were copied into this lane and hashed
**before** running; `my-source-hashes.txt` is identical line for line to MORTALITY-3's
`frozen-source-hashes.txt` (the classifier is
`9f00b7243bfb43fd4cba126144da712d93e143a62a7fba6ab3ad82cceb5be3a3`). All six regenerated JSON
artifacts are **byte-identical to both MORTALITY-2's and MORTALITY-3's** — twelve comparisons, all
`IDENTICAL`, `checks/07` exit 0. No sibling lane's file was written to; `compare_artifacts.sh`
compares and never replaces.

### 4b. Independent arithmetic from the stratum counts alone (`checks/09`)

`independent_arithmetic.py` imports no MORTALITY-2 code. It reads only the per-stratum
flagged/sentence counts and recomputes each quantity with exact rational arithmetic
(`fractions.Fraction`, `math.comb`), including its own hypergeometric convolution for the stratified
exact test.

| quantity | reported | my independent arithmetic | verdict |
|---|---|---|---|
| crude EMC | 4/116 = 3.45 % | `4/116 = 0.034483` | ✅ |
| crude comparator | 3/461 = 0.65 % | `3/461 = 0.006508` | ✅ |
| crude Fisher two-sided | 0.03304 | `0.0330400628` → 0.03304 | ✅ digit for digit |
| exact stratified two-sided | 0.695251 | `0.6952512059` → 0.695251 | ✅ digit for digit |
| exact stratified one-sided | 0.378985 | `0.3789848509` → 0.378985 | ✅ digit for digit |
| Mantel-Haenszel OR | 1.7844 | `1.7843588269` → 1.7844 | ✅ digit for digit |
| E[T] under the null | 3.1209 | `3.120851` | ✅ |
| collapsed case-vs-non-case | 0.455419, MH OR 1.948 | reproduced by the same routine | ✅ |
| standardisation, EMC → comparator mix | **0.00929** | **0.0092966 → 0.00930** | ⚠ **see 4c** |
| standardisation, comparator → EMC mix | **0.01856** | **0.0185847 → 0.01858** | ⚠ **see 4c** |

The three informative-stratum facts the diffs rest on also re-derive: the only informative strata are
`case_report_or_series` (EMC 4/56 vs other 2/60) and `unclassified` (EMC 0/24 vs other 1/83); the
other three are dropped as carrying no information, which is the `"strata_used": 2` label MORTALITY-3
already recorded.

### 4c. The one place two digits did not match, chased to its cause and closed (`checks/10`)

**This is a real finding and it is recorded rather than smoothed over.** Both standardisation values
disagree with my exact recomputation in the fifth decimal place. The cause is not a discrepancy in
the analysis: `genre_stratified_rates.py:224` standardises the **per-stratum rates after they have
already been rounded to four decimal places for the JSON**, so the rounding propagates into the
weighted sum. `standardisation_rounding_probe.py` computes both routes side by side:

| | from rounded stratum rates (what ships) | from exact stratum rates | delta |
|---|---|---|---|
| EMC → comparator mix | 0.0092928416 → **0.00929** | 0.0092965603 → 0.00930 | 3.7e-06 |
| comparator → EMC mix | 0.0185586207 → **0.01856** | 0.0185846836 → 0.01858 | 2.6e-05 |

The shipped values are exactly what the rounded route produces, so the artifact is internally
consistent and reproduces byte-for-byte; the disagreement is a rounding-propagation artefact of order
1e-5, four orders of magnitude below the effect being discussed. **It changes no prose**: to the two
significant figures both §4.2 diff and this lane quote, both routes give **0.93 per cent** and
**1.86 per cent**. It is named here because "all six reproduce" was the bar and a silent fifth-decimal
gap is exactly the kind of thing a later reader would find and mistrust. It warrants no code change
and none is proposed — that would be re-tuning a frozen instrument for cosmetics.

**Nothing failed to reproduce. No lexicon, classifier, threshold or matcher was touched.**

## 5. Step 2 — §6, read sentence by sentence

`## 6. Conclusion` is lines **488–500**; every line reference below is against the **unpatched** live
file (MORTALITY-3's diff shifts §6 down by 26 lines when applied first).

| lines | sentence | scope | verdict |
|---|---|---|---|
| 490–493 | "The published record of extraskeletal myxoid chondrosarcoma does not say how most of its patients die… names a disease entity without naming the event." | **this disease**, from §3.1 | **stands** — a description of this corpus, which the composition result does not touch |
| 493–495 | "Among the instances it does label, competing causes and second malignancies are the largest category, and respiratory failure, though present, is not dominant." | **this disease** | **stands** |
| 495–497 | "Between a tenth and a third of deaths after diagnosis are not caused by the sarcoma… at approximately background rate." | registry cohort, **this disease** | **stands** |
| 497–498 | "The survival available to antitumour therapy is 6.7 percentage points… at three years." | **this disease** | **stands** |
| 498–500 | "Research prioritisation in this disease should reflect that difference, **and cause-of-death recording should be treated as a measurement that determines what its evidence base can answer.**" | first clause **this disease**; **second clause unscoped** | **the site** |

**Exactly one site, and it is the second clause of the final sentence — lines 499–500.** The
distinction that matters: the clause is a *general normative prescription* ("cause-of-death recording
should be treated as a measurement"), and the possessive "**its** evidence base" has no antecedent
inside the clause, so it reads as *any* disease's, which is precisely the reading §4.2 stated outright
("For ultra-rare cancers generally") and which MORTALITY-3's diff withdraws. **A claim about this
disease's corpus may still stand and every other §6 sentence is one; a claim about ultra-rare cancer
literatures generally is what the composition-effect result cannot support in either direction.**

**Nothing else in the manuscript carries it.** A sweep of `ultra-rare`, `generally`, `other diseases`,
`evidence base`, `any disease`, `cause-of-death recording` returns nine hits: lines 13, 55, 104 use
"ultra-rare" descriptively of this disease; line 142 excludes other diseases' patients; line 286 is a
§3.1 count; line 394 is the §4.2 heading; lines 403–404 are MORTALITY-3's target; lines 499–500 are
mine. **The abstract's Conclusions paragraph (lines 94–99) is scoped to "this disease" throughout and
needs no change.**

## 6. Step 3 — the diff. `section-6-conclusion-scope.diff`, **UNAPPLIED**

Built by `make_diff.py` (`checks/11`), which asserts its anchor occurs exactly once and writes only
inside this lane; `git status` confirms the manuscript is unmodified. One hunk, `@@ -496,8 +496,13 @@`.
It keeps the whole first clause, scopes the second, and adds the null.

How it meets each required property, and how it stays consistent with MORTALITY-3's §4.2 diff:

* **Scoped, not deleted** — "in this disease cause-of-death recording should be treated as a
  measurement that determines what **its own** evidence base can answer" retains the finding §3.1
  actually supports and closes the dangling possessive. This is the same retained half MORTALITY-3
  keeps in §4.2 ("determines what this disease's evidence base can answer"), phrased so the two do
  not read as a repetition.
* **Null is not equality** — "that is a **null rather than a demonstration of equality**… too little
  to establish sameness as well as too little to establish a difference", with the **4 events against
  2** within case reports named explicitly, matching §4.2's "a genuine two-fold difference in either
  direction is entirely compatible with them".
* **Sentence unit is not patient unit** — "with a sentence and not a patient as the unit", carried
  into §6 rather than left only in §4.2, because §6 is where a reader stops.
* **Consistent with, and not a duplicate of, the §4.2 diff** — §6 quotes **no** figure except the 4
  and the 2 that carry the power argument; the crude rates, the p-values, the MH odds ratio, the
  standardisation and the hand-check error rates stay in §4.2 where the instrument is described. A
  conclusion that re-derives its evidence is a worse conclusion.
* **Revives nothing rejected** — no cause of death is assigned, no survival curve is read, no
  competing-share or ceiling figure is restated, no claim is made about any other disease's
  literature, and no clinical, efficacy, safety, prognostic or treatment statement appears.
* **§3.1 untouched, §4.2 untouched** — the single hunk spans lines 496–503 only. §3.1 ends at line
  282; §4.2's paragraph is at 400–408.

### The cumulative apply is real, not `--check` (`checks/12`)

`git apply --check` tests each patch against the tree independently and would prove nothing about the
two coexisting. `cumulative_apply_test.sh` therefore does a **real `git apply`** of both diffs, in
**both orders**, into a throwaway git repository **outside** `/home/user/Rare-cancers`, and prints
the resulting §4.2 and §6. **Exit 0.**

| order | first | second | residual generalisation |
|---|---|---|---|
| §4.2 then §6 | exit 0, "Applied cleanly" | exit 0, "Applied cleanly" | none — `OK: no residual 'For ultra-rare cancers generally'` |
| §6 then §4.2 | exit 0, "Applied cleanly" | exit 0, `Hunk #1 succeeded at 522 (offset 26 lines)` | none |

The offset-26 line is the expected consequence of §6's diff landing first; both orders converge on
the same text, which the check prints in full. **Neither diff was applied to the repository.**

## 7. Step 4 — exactly what regenerating `claim-coverage.json` involves

**The command** — `python3 research/manuscripts/claim_coverage.py --write`, run from the repository
root, and the result committed *in the same change* as the two diffs. `--write` and `--check` may not
be combined (the script exits 2: a write would produce the reference the check then reads).

**The guard** — `claim_coverage.py:937` `STALE_HEADER`, printed by `--check` at `:975`, exit 1. It
compares **both ways** field by field and then compares the **bytes** as a backstop, so a hand edit
cannot satisfy it. It is wired in three places: `scripts/preflight.sh:848`, `.github/workflows/tests.yml:243`,
and `scripts/regenerate_aso_chain.sh:311`. The census/guard-corpus pair is additionally enforced by
`research/manuscripts/tests/test_the_census_artifact_and_the_guard_corpus_are_a_pair.py`. **Not
touched, not weakened, not bypassed by anything in this lane.**

**The resulting values** — measured, not estimated (`checks/13`). `claim_coverage_cost.py` imports
`claim_coverage` read-only and replays **its own** `sentences` / `_pin_patterns` / `_test_patterns` /
`is_selective` against a patched copy held outside the repository. **Control first**: the same replay
against the live manuscript reproduces the committed row exactly, so the method measures what the
census measures.

| field | committed | after **both** diffs | delta |
|---|---|---|---|
| `sentences` | 182 | **196** | +14 |
| `with_a_number` | 54 | **61** | +7 |
| `uncovered` | 182 | **196** | +14 |
| `uncovered_with_a_number` | 54 | **61** | +7 |
| `covered` | 0 | **0** | 0 |
| `with_a_number_covered` | 0 | **0** | 0 |

`covered` stays 0: the new prose introduces seven numbered sentences and **no witness reads any of
them**, so the diffs make this document's uncovered-with-a-number count *worse* by 7. That is an
honest consequence of adding numbers to a document nothing binds, not a defect of the diffs, and it
is the number a reviewer of the applying change should see.

**⛔ A correction to MORTALITY-3's framing, and the real cost.** MORTALITY-3 implies applying its diff
is what makes the artifact stale. It is **already stale on the current tree**: `--check` run
unmodified (`checks/14`) exits **1** and lists **eight other documents** whose committed rows the
live census no longer reproduces — `emc-transcriptional-proteostatic-dependency.md` (58→149
sentences), `nr4a3-fusion-transcriptional-output.md` (435→465), `emc-fusion-partner-stratification.md`
(329→321, and `covered` 87→50), `degrader-methods-failure-record.md` (124→214),
`cancer-modality-census.md` (123→129), `emc-surface-target-landscape.md` (400→498),
`tcip-induced-interface-preprint.md` (123→253). **`emc-mortality-mechanisms-paper.md` is NOT among
them** — its row still reproduces, which is why the control above passes.

So the true cost of applying is: the mortality paper becomes the **ninth** stale document, and
`--write` cannot regenerate its row alone — it rewrites the whole artifact, sweeping the other eight
documents' unrelated drift into the same commit. **Whoever applies these diffs either owns that
combined regeneration or coordinates with whoever owns the other eight.** This lane did not
regenerate the artifact, did not run `--write`, and did not touch the guard or any test.

## 8. Artifact · validation · provenance · limitations · stop condition

**Artifact** · `section-6-conclusion-scope.diff` — unapplied, one hunk, applies cumulatively with
MORTALITY-3's §4.2 diff in both orders at exit 0 — plus `make_diff.py`, the independent-arithmetic
re-derivation, the rounding probe, and the measured claim-coverage cost.
**Validation** · twelve byte-identity comparisons against two sibling lanes (`checks/07`, exit 0);
exact-rational independent recomputation of every load-bearing quantity (`checks/09`); a real
cumulative two-patch apply in both orders on a scratch tree (`checks/12`, exit 0); a control-first
census replay that reproduces the committed row before measuring the patched one (`checks/13`); the
real, unmodified `--check` exit code preserved (`checks/14`, exit **1**).
**Provenance** · `research/literature/emc-mortality-probe.json` and
`research/manuscripts/emc-terminal-events-classified.json`, read read-only through MORTALITY-2's
byte-verified scripts; `research/manuscripts/emc-mortality-mechanisms-paper.md` and
`research/manuscripts/claim-coverage.json` read read-only. No network, no retrieval, no cohort, no
GPU, no paid API, no publication act, no outreach.
**Limitations** · Independent arithmetic verifies the *computation*, not the *world*: the classifier,
the lexicon, the corpus, the 20 per cent unclassified papers and the single unblinded hand reading
are the same ones, with every limit MORTALITY-2 §7 records, and all of them carry into the proposed
prose. The proposed §6 text is a **scope narrowing** and introduces no new measurement. No count
anywhere here is a patient count, a death count or a cause; no clinical, efficacy, safety,
selectivity, prognostic or treatment claim is made or implied. The claim-coverage figures are what
the census computes on a patched copy; the owner's `--write` is authoritative.
**Stop condition** · **Met.** §6 had exactly one generalising site; it was identified with file and
line, a diff was written and proved to coexist with MORTALITY-3's, and the regeneration cost was
measured rather than described.
**Forward stop** · **Do not apply either diff, do not stage them, do not run
`claim_coverage.py --write`, and do not touch the STALE_HEADER guard or the census tests.** The paper
owner and the parent decide, and the eight pre-existing stale documents are a separate owner's
problem that must not be silently absorbed. Advancing the underlying science still requires a
study-type-matched comparator drawn at design time and hand reading at the patient unit, neither
obtainable without new retrieval.

## 9. What is in this directory

| file | what it is |
|---|---|
| `section-6-conclusion-scope.diff` | **the deliverable** — unapplied unified diff, one hunk in §6 |
| `make_diff.py` | builds it from the live manuscript; asserts a unique anchor; never writes the manuscript |
| `independent_arithmetic.py` | re-derives Fisher, the exact stratified test, MH OR and both standardisations from stratum counts with exact rational arithmetic, importing no MORTALITY-2 code |
| `standardisation_rounding_probe.py` | isolates and explains the only two digits that did not match |
| `cumulative_apply_test.sh` | the REAL two-patch cumulative apply, both orders, outside the repo |
| `claim_coverage_cost.py` | control-first measurement of the post-diff census values; regenerates nothing |
| `compare_artifacts.sh` | twelve byte-identity comparisons against MORTALITY-2 and MORTALITY-3 |
| `my-source-hashes.txt` | sha256 of the six copied scripts + hand labels, identical to MORTALITY-3's frozen list |
| `*.py`, `handcheck-labels.json` | verbatim copies of MORTALITY-2's frozen scripts, re-run here |
| the six `*.json` outputs | this lane's re-derived artifacts — byte-identical to both siblings' |
| `run_check.sh` | capture harness; records the real exit code, no pipe |
| `checks/01`–`14` | every execution attempt with `command.txt` / `stdout.txt` / `stderr.txt` / `exit_code.txt` |

**Evidence-handling note, recorded rather than hidden.** One stray directory, `checks/X`, was created
at the **repository root** by my own error — a malformed invocation of `run_check.sh` with a label and
no command, left over from assembling a compound shell line — and was removed seconds later in the
same command. It contained no research evidence: the harness had no command to run, so it held only
an empty `command.txt` and an exit code for the empty invocation. Per the standing instruction not to
recreate logs it has **not** been reconstructed; the gap is recorded here instead. No MORTALITY-2,
MORTALITY-3, PUB-MORTALITY-MECHANISM or other lane's evidence was read-modified, moved or deleted, no
receipt-verified directory was involved, and `git status` confirms **nothing outside this lane's
directory changed** in the repository.
