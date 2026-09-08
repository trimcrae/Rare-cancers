# Material decisions and reopening requirements — for root adjudication

**Date 2026-09-08. Parent-filed at normal collection. Nothing below is applied.**
⛔ Per root's standing instruction the parent has **not** amended any selection rule, denominator
rule or control rule because a leaf reported a finding. Every item here is a decision, not a change.

## 0 · What is finished and where it is

| Work | State | Location |
|---|---|---|
| Backlog planner proposal (4 ready items, ranked) | committed | `PROPOSAL-next-work-backlog.md` |
| Job 1 measurement contract, 552 rows / 138 trials | committed | `CURATION-endpoint-measurement-contract*` |
| Job 2 identity and overlap, rule hashed before use | committed | `CURATION-endpoint-identity-and-overlap*` |
| Job 3 arm attribution, 552 groups | committed | `CURATION-endpoint-arm-attribution*` |
| Job 1 independently re-derived, 7/7 confirmed | committed | `VERIFY-job1-arithmetic.md` |
| Q-A 4 groups · Q-B 4 groups · Q-C 4 groups · Q-D 4 groups | committed | `LEAF-OUT/` |
| Mortality curation pair, verified, 3 corrections applied | committed | `VERIFY-mortality-curation.md` |
| Citation ledger repair, verified ACCEPT | committed | `VERIFY-citation-ledger-repair.md` |
| Surface-target batch, verified, **NOT integrated** | committed as evidence | `NOT-ACCEPTED-surface-targets/` |
| FP frozen handoff | collector still running | — |

**Jobs 2 and 3 have NOT been independently re-derived.** Only Job 1 has. Job 4 stays
dependency-gated on all three and was not launched speculatively.

## 1 · Decisions on the endpoint selection rule — D-SEL

**D-SEL-1 · The step-f ties are not metadata-free.** All 1,590 ties adjudicated exactly once by four
leaves on disjoint NCTs: **1,589 BASIS_EXISTS, 1 NO_BASIS.** Job 2's global claim is refuted. The
dominant cause is that R1's title regex admits ORR, DCR, CBR and best-overall-response distributions
into one candidate pool, so registration order chooses between **different endpoints**, not between
two encodings of one quantity. Assessment criteria (RECIST 1.1 / mRECIST / iRECIST / irRC / Cheson /
Lugano), `timeFrame`, `populationDescription`, `paramType` and unit also separate competitors the
ladder never compares.
⛔ **Not amended.** Every consequence the leaves report is explicitly conditional. Root decides
whether R1 narrows its construct, and whether any preference is preregistered over criteria version,
timeframe, population or unit — for which the records supply no internal ordering.

**D-SEL-2 · A `Participants` denominator of 0 satisfies the candidate filter.** Multiple leaves found
ties in which every competitor reports 0, so step f selects a measurement over zero participants; one
record's own population text says data collection was not conducted. Root decides whether zero-denominator
candidates are excluded at R1.

**D-SEL-3 · One under-specified normaliser, found from two directions.** Three Q-C leaves recovered
that the group-key normaliser strips trailing punctuation but not brackets; three Q-B groups
independently found the same normaliser splitting one cohort in two over an internal hyphen, a
transposed unit (`3.2 mg/kg` vs `3.2 kg/mg`) or a misspelling. Different symptom, one cause.

## 2 · Decisions on the denominator — D-DEN

**D-DEN-1 · The corrected readings exist and are now produced.** Across Q-A, every in-scope row
carries exactly one reported participant denominator the producer never reads, and the full category
vector sums to it in almost every case. Job 1's untested recoverability assertion holds, with named
exceptions: rows whose class categories sum to a **multiple** of the denominator (landmark timepoint
tabulations, therapy-line tables over one population) and one trial with four overlapping
stratifications and no stated selection basis. Those are UNRESOLVED and stay so.
⛔ **No rate recomputed and none proposed.** Root decides whether the extraction contract is adopted.

**D-DEN-2 · Dropped content is not all non-evaluable.** sCR, VGPR, CRh, CRi and reported PD counts
are among the dropped categories, not only Unknown / NE / Missing.

**D-DEN-3 · Job 1's shipped column 26 is mislabelled.** Header reads
`sum_minus_reported_denominator`; it holds `evaluable_n` minus the denominator in all 552 rows. A
label defect in a delivered table, not a numeric error.

## 3 · Decisions on control status and the arm map — D-ARM

**D-ARM-1 · "Unreachable" does not survive.** Across Q-D's 61 trials, the great majority of in-scope
rows are recoverable through `armGroups[].description`, `interventionNames`, arm cardinality and
ordinal tokens — fields Job 3's label-only matcher never read. ⚠ **Honest qualification:** recovery
mostly removes UNKNOWNs rather than finding comparators; the large majority of recovered rows land on
EXPERIMENTAL or OTHER, and **no placebo or no-intervention comparator was recovered anywhere.**

**D-ARM-2 · `NOT_CONTROL` is asserted from ZERO registered arms in 6 rows / 3 trials.** Parent
re-derived; all three now read; all three have an empty arms module and one still reports two results
groups. The defensible value is UNKNOWN. See `PARENT-NOTE-zero-arm-not-control.md`.
⛔ UNKNOWN was never read as NOT_CONTROL anywhere, and no denominator was built from a recovery.

**D-ARM-3 · A CONTAINMENT match puts 3 of one trial's 5 groups on the wrong arm** (because "chemo" is
a substring); control status was safely UNKNOWN_WEAK_MATCH_ONLY but those rows'
`registry_arm_label`/`registry_arm_type` are wrong. The same trial's placebo arm **is** registered yet
typed EXPERIMENTAL — recorded CONTESTED, countable as neither. A leaf recommends against a blanket
"recovered type beats group text" rule, and the parent agrees: that record's own typing is internally
inconsistent.

## 4 · Overlap — D-OVL

**D-OVL-1 · 180 of 180 over-enrollment trials record `ACTUAL` enrollment. Zero ESTIMATED.** The one
category that would have made the excess a non-finding does not occur.

**D-OVL-2 · A pooled parent summed with its own components leads every group, and `pooled_label`
misses most of them** — "Part 2 - total", "Cohorts 2 + 3", "Phase 1b + Phase 2",
"Doxorubicin Transdrug Pooled" all fall outside its vocabulary, so the flag understates the effect.

**D-OVL-3 · Some excesses are NOT overlap and must not be folded in.** A number of trials have
already-disjoint cohorts yet still exceed enrollment — one with a single selected cohort of 41 against
an enrollment of 34, where overlap is arithmetically impossible. Internal registry inconsistencies. No
leaf adjudicated which field is wrong, and the parent has not either.

## 5 · Reopening requirements NOT met

- **Endpoint** stays parked. Route 1's reopening condition also needs a reviewed selection rule and
  recomputed outputs; neither exists. D-SEL and D-DEN are inputs to that decision, not the decision.
- **Mortality** stays parked. The curation pair is verified and its three presentational defects are
  corrected, but the hold's open item — the evidence tier of "14 with a stated mechanism" — is
  untouched.
- **Biomarker, HLA, CR1 / PUB-CLOSED-ROUTES, ASO, W25, P6, ICD-O** unchanged. Documented and skipped.
- **ATR release** stays HELD: `e218` PDF accepted, `618` release gate FAILED, both now current in
  `HOLD-atr-release-path.md`.

## 6 · New proposals needing root admission, with concrete scope

| id | scope | evidence |
|---|---|---|
| **P-ST** | Bounded surface-target repair: keep 21 confirmed corrections, fix 4 editorial defects, resolve the sibling-document conflict FIRST, treat the 5 artifact contradictions as a separate owner decision | `PROPOSAL-surface-targets-adjudication.md` |
| **P-CI** | Split `lint_citations.check()` so five tests can isolate the provenance axis; two negative controls currently pass whenever the type guard is non-green. Patch measured, **not applied** — touches a file outside the repairing lane's ownership | `VERIFY-citation-ledger-repair.md` |
| **P-AB** | Endpoint ablation: strengthen an unwitnessed guard; the raised-but-not-taken systemic fix would drop endpoint coverage 9/5 → 6/4, below its floor of 7 | `PROPOSAL-ablation-unwitnessed-cases.md` |
| **P-R1..R4** | Planner's four ready items, ranked, all offline except R2 | `PROPOSAL-next-work-backlog.md` |

⛔ Not proposed and not wanted: a cache re-fetch. Q-D leaves found `participantFlowModule` and the
`interventions[].armGroupLabels` back-pointer absent from the delivered payloads. That is a
cache-scope gap, not a registry gap, and it bounds several UNRESOLVEDs honestly.
