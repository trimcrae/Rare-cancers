# TD1 F10 — dated exact changed-field / changed-code map

**Date of correction: 2026-09-08.** Every edit below is **annotation-only**. ⛔ No producer was executed,
no artifact regenerated, no raw input read, and **no numeric value, cohort member, membership list,
measured state or original source byte was changed**. Original historical output, check logs and failed
attempts are preserved untouched, including the author's failed preflight, the three historical CLI
exit-2 attempts and the reviewer's attempt-1 exit 1.

The manuscript itself is edited in place (owner-owned). **All six shared files below are parent-owned:
they are delivered as unified diffs in `patches/` and are NOT applied to the working tree.** Apply from
the repository root with `git apply patches/<name>.patch`.

## Method, and why it is provable

JSON files were edited **structurally**: parsed, the named field replaced by path, and re-serialised with
the settings verified — *before* any edit — to reproduce the original file byte-for-byte
(`indent=2, ensure_ascii=False` for G, C and `publications.json`; `indent=2, ensure_ascii=True` for E).
Generator sources were edited by replacing exactly one bounded `"key": <literal>` entry inside the
identified route/panel block, then guarded by an AST comparison asserting that **only** the named string
constants changed and that **no non-string constant** changed. Builder: `checks/build_shared_patches.py`
(attempt 7 exit 0; the four earlier attempts, including two that mis-anchored and were rejected by the
guard, are retained in `checks/`). Verifier: `checks/verify_invariance.py` (attempt 4 exit 0).

**Invariance evidence — `INVARIANCE-EVIDENCE.json`: 441,602 checks, 0 failures.**

| category | n | failed |
|---|---|---|
| non-string leaf unchanged (every measured value) | 393,752 | 0 |
| key set preserved | 34,675 | 0 |
| list length preserved | 13,114 | 0 |
| string change is a declared edit | 22 | 0 |

Plus named spot-invariants, all passing: G's `genes`, `panel_groups` and `sarcoma_dependency_prior`
blocks byte-identical for both routes; E's `transcriptional_cdk` and `chaperone_dependency` group blocks
and **both platform records** byte-identical; C's `evidence` records (every verbatim quotation), every
query string and hit count, the `retrieval` record, `open_questions_stated_as_unknown` and the
`_supersedes` historical record all byte-identical; and each patch shown to apply cleanly to a pristine
copy taken **outside** the repository.

## G — `research/modalities/census-route-expression-grading.json`

`5bc3c80c034dde77…` 92,757 B → `2dbd21cc811c150c…` 94,931 B · patch
`research__modalities__census-route-expression-grading.json.patch`

| field path | finding | old → new bytes | what changed |
|---|---|---|---|
| `routes.RT-TXN-CDK.observed` | F7, F2 | 239 → 668 | "both with the largest t-statistics in this pass" **withdrawn** as an undefined census-wide rank; the GPL3290 interpretation hold and its three reference labels added |
| `routes.RT-TXN-CDK.verdict` | F7, F2 | 75 → 324 | "the most concordant elevation in the census" **withdrawn**; verdict restated as supported-on-abundance and exploratory, with the hold |
| `routes.RT-TXN-CDK.the_dependency_screen_ran_and_it_closed_the_window` | F1, F3 | 499 → 1142 | text now states the screen **did not** close the window. ⚠ The **key name is deliberately retained unchanged** for consumer stability, and the value says so; the measured 91/176, 100 %, −1.85/−1.46 and +0.085/+0.017 are restated verbatim, followed by what a binary threshold cannot establish and the statement that the two readings are unpaired |
| `routes.RT-TXN-CDK.route_action` | F1, F3 | 67 → 268 | "closed on the axis that matters" **withdrawn**; action is now `hold` with the unpaired/unmeasured-in-EMC reason |
| `routes.RT-CHAPERONE.observed` | F4 | 207 → 671 | "go the OTHER way on both, which is not what a general stress response looks like" **withdrawn**; replaced by not-distinguishable-from-zero with intervals including positive differences |
| `routes.RT-CHAPERONE.verdict` | F4 | 82 → 240 | "the stress-response arm contradicts it" **withdrawn**; verdict restated as partly supported and exploratory |

## GP — `research/modalities/census_route_expression_grading.py`

`99888ede672f1d45…` 51,333 B → `42ffb5a9fc85c93d…` 54,778 B · patch
`research__modalities__census_route_expression_grading.py.patch`

Six literal entries inside `build()` — `routes["RT-TXN-CDK"]` (`observed`, `verdict`,
`the_dependency_screen_ran_and_it_closed_the_window`, `route_action`) and `routes["RT-CHAPERONE"]`
(`observed`, `verdict`) — rewritten so the generating text **agrees byte-for-byte with the corrected
displayed annotation** in G. AST guard: **6 string constants added, 6 removed, non-string constants
unchanged: true**. ⛔ This is a prose correction to the generator; it does not claim the generator was
executed, and it was not.

## E — `research/modalities/emc-expression-panels.json`

`123bd05a9f9f5d08…` 13,253,561 B → `59bccb553148c710…` 13,254,759 B · patch
`research__modalities__emc-expression-panels.json.patch`

| field path | finding | old → new bytes | what changed |
|---|---|---|---|
| `panels.transcriptional_cdk.question` | F8 | 224 → 409 | "the class the census found no prior search had ever named" **withdrawn** — dated searches bound what was inspected, not what exists |
| `panels.transcriptional_cdk.what_it_cannot_settle` | F1, F3 | 361 → 660 | "only a dependency screen would" **withdrawn** — a dependency screen in non-EMC lines does not exclude the class for EMC either; the unpaired status is stated |
| `reads.read_13_TXN_CDK.question` | F8 | 224 → 409 | same string, second copy |
| `reads.read_13_TXN_CDK.what_it_cannot_settle` | F1, F3 | 361 → 660 | same string, second copy |
| `reads.read_13_TXN_CDK.panels.transcriptional_cdk.question` | F8 | 224 → 409 | same string, third copy |

⚠ The artifact carries these two strings in **three and two places respectively**; all copies move
together, and a dedicated check asserts no stale copy of the old text survives anywhere in the file.

## EP — `research/modalities/emc_expression_panels.py`

`05c343aa29162ec6…` 193,150 B → `cbbed08c0b02c7b5…` 193,814 B · patch
`research__modalities__emc_expression_panels.py.patch`

The two `PANELS["transcriptional_cdk"]` literals (`question`, `what_it_cannot_settle`) rewritten to agree
with the corrected E annotation. AST guard: **2 string constants added, 2 removed, non-string constants
unchanged: true**.

## C — `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json`

`4603641f2d342d49…` 30,301 B → `7ba3ed7a39054b52…` 32,858 B · patch
`research__literature__fet-fusion-chaperone-clientship-2026-08-27.json.patch`

| field path | finding | old → new bytes | what changed |
|---|---|---|---|
| `verdict.answer` | F8 | 77 → 261 | bare "NO" → "NOT IDENTIFIED IN THE ITEMS INSPECTED BY THIS DATED SEARCH", with the two-sided warning against inflating it either way |
| `verdict.one_sentence` | F8 | 458 → 954 | "No FET-family fusion protein has been shown to BIND a chaperone in any published assay" and "the chaperone literature is empty" **withdrawn**; the four search limits (Q15's 25 unscreened hits, Q13's unretrieved supplement, abstract-only/inaccessible records, unsearched preprints and non-PubMed sources) stated inline |
| `verdict.by_category.b_the_FUSION_as_client` | F8 | 469 → 786 | "Zero co-immunoprecipitation, zero pull-down, zero chemical-affinity capture, zero client-screen appearance" **withdrawn** in favour of not-found-among-records-inspected; the SGT1 leucine-rich-repeat preference retained with the note that a preference does not exclude other interactions |
| `verdict.by_category.c_the_PARTNER_as_client` | F8 | 221 → 374 | "NULL … no chaperone literature at all" → "NOT FOUND BY THESE QUERIES", with the note that a title/abstract co-occurrence search cannot establish absence |
| `verdict.why_this_is_not_a_null_result_about_the_assay` | F8 | 397 → 636 | "the absence of such a demonstration … is a genuine gap in the literature" narrowed to a gap in what this search retrieved, noting that a negative or unpublished experiment would not appear either |
| `definitions.documented_chaperone_client` | F5 | 511 → 876 | the inconsistency is resolved: **clientship requires binding**; loss-on-inhibition is **dependence** and is explicitly not counted as clientship; the four distinct claims are named |
| `what_this_changes.for_RT_CHAPERONE` | F8 | 439 → 778 | "it comes back NEGATIVE ON THE PREMISE" and "the literature now says it is open for EVERY FET fusion" **withdrawn**; scoped to the bounded search |
| `searches_that_returned_nothing_relevant.queries[2] (Q3).outcome` | F8 | 220 → 409 | "There is no … study … in PubMed" → "This query retrieved no …", with the note that it is one query string on one date |
| `searches_that_returned_nothing_relevant.queries[14] (Q15).outcome` | F8 | 230 → 469 | the unsupported inference "it cannot contain a fusion-clientship result that Q1, Q2, Q7, Q8 and Q12 all missed" **withdrawn**; 25 hits recorded as an open gap. ⚠ "Not individually screened" is retained verbatim |

⛔ Every query string, every hit count, every `evidence` record and verbatim quotation, the `retrieval`
record and `open_questions_stated_as_unknown` are **byte-identical** — verified.

## `systems/graph/publications.json` — PUB-TXN-DEPENDENCY

`11b8a785ac95809d…` 63,825 B → `57762dd5b7e961a8…` 64,078 B · patch `systems__graph__publications.json.patch`

| field path | finding | old → new bytes | what changed |
|---|---|---|---|
| `[30] PUB-TXN-DEPENDENCY.what_it_would_claim` | F1 | 696 → 800 | "ABUNDANCE AND DEPENDENCY DISAGREE IN OPPOSITE DIRECTIONS", "the most concordant elevation in the census", "closes completely on dependency, being pan-essential with no selectivity" and "internally contradictory elevation" **withdrawn and marked PARKED**; replaced by the two unpaired streams at their actual scope |
| `[30] PUB-TXN-DEPENDENCY.outcome_potential_why` | F1 | 127 → 270 | the "disagree in opposite directions" framing **withdrawn** |

⚠ **This file is outside the literal F10 list (E/EP, G/GP, C).** It is included because it is the live
model-state record of the paper and carried the parked central claim verbatim; leaving it would reproduce
exactly the F10 defect. It is parent-owned graph state — flagged for the parent's decision, not applied.
`systems/views/L3-publications.md` and `systems/views/L2-rt-chaperone.md` are **generated** from it and
were deliberately **not** touched; they will need the parent's normal regeneration after integration.

## Not changed, and why

- **`systems/graph/routes.json`** and other route records were not inspected for this batch and are not
  patched; F10 named E/EP, G/GP and C.
- **`research/manuscripts/modality-census/cancer-modality-census.md:186`** still reads "the most
  concordant elevation the whole census found". It belongs to another paper and another owner; reported
  in `FINDING-MAP.md` §Residual rather than edited here, to avoid P-ST/FP/MF1 overlap.
- **`research/manuscripts/pinned-figures.json`** contains no pinned quantity for this manuscript
  (checked: no entry for the file, and none of its figures appear), so no pinned-quantity record change
  is required by this repair.
