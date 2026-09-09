---
id: DOC-TXN-DEPENDENCY-CLAIM-REDERIVATION
title: "TXN-DEPENDENCY — which quantitative claims of PUB-TXN-DEPENDENCY re-derive today, and what exactly is missing for the rest"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: TXN-DEPENDENCY
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
endpoint: PUB-TXN-DEPENDENCY
---

# TXN-DEPENDENCY — first pass claim re-derivation

## Question

Which of PUB-TXN-DEPENDENCY's quantitative claims can be re-derived today from committed
artifacts, and which cannot — and for those, what exactly is the missing input?

## Merit rationale

This is one of the 33 endpoints in `systems/graph/publications.json` and the only one of the
dependency family that had **never** had a lane in either campaign round. Its sibling lanes
(PUB-BIOMARKER-DEP, DEP-THRESHOLD, BIOMARKER-DEP-2, PUB-SYNLETH, PUB-MTAP-PRMT5, SYNLETH-2)
converged on one shared producer defect — `depmap_sarcoma_dependency.py` retains **no dispersion and
no per-line value**, so a route-decision statistic cannot be checked at any cut other than the one it
was published at (DEP-THRESHOLD finding C1). This manuscript reads the same producer's output for
five genes. Whether that defect reaches its printed numbers was unknown. Patient relevance is
indirect but real: this is the paper that states, for an ultra-rare fusion sarcoma with no cell-line
model, what a public dependency release does and does not contain — a reader who cannot re-derive
those numbers cannot check that statement.

## Evidence gap addressed

Not "is the paper right about the biology" — that is settled by the TD1 review and root
adjudication already recorded in the endpoint. The gap is narrower and unaddressed: **no lane had
ever checked, claim by claim, that the manuscript's printed quantities are recoverable from the
artifacts it names.** The distinguishing inputs are `research/modalities/emc-expression-panels.json`
(Stream A) and `research/modalities/depmap-sarcoma-dependency.json` (Stream B) plus
`fet-ddr-axis-scan.json`, and the ten Git blob identities pinned in the manuscript's §8.

## Step taken

One pass over every quantitative claim in the manuscript, re-deriving each from the committed
artifact it names, at three derivation levels: **READ-BACK** (the value is stored), **RECOMPUTED**
(the value is arithmetic on stored values — group Δ/t/df rebuilt from the retained per-sample
`z_vs_array`, conditional p and intervals, the MYC algebra, the unique-integer dependent counts, the
Bonferroni illustration, the cohort split, the ten blob identities), and explicit
**NOT-RE-DERIVABLE-LOCALLY** rows naming the exact missing input.

## Artifact

`claim-rederivation-ledger.json` — **83 rows**, one per quantitative claim, each carrying the quoted
value, the source artifact and key, the re-derived value, a verdict, the derivation level, and for
the third verdict the exact missing input.

| verdict | rows |
|---|---|
| REPRODUCES | 75 |
| NOT-RE-DERIVABLE-LOCALLY | 5 |
| MISMATCH | 3 |

### The three MISMATCHes, digit for digit

All three are in the manuscript's §8 **"Fixed identities"** table — the Git blob SHA-1s it offers as
path-independent identities for the objects it was read against. Every one is reported as found and
**none is repaired here**; no manuscript line was edited, reverted or diffed.

| object | §8 states | working tree at use time (`git hash-object`) |
|---|---|---|
| `research/modalities/census-route-expression-grading.json` | `b45a35a4ee2636993e42e897c3be6d7705ccae8a` | `ee552394935792ed2e76bce926146b77907c5694` |
| `research/modalities/census_route_expression_grading.py` | `18625608b378122adbe9dbcca16de370c357367b` | `fe00fe381957bf248d774d0ed68cbf93c6674487` |
| `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json` | `8728c34de793da848ccae012e808e668b69b24bd` | `9328cecebdffdb53921f82805b47fd0943d30c1f` |

**Two of the three are predicted by the manuscript itself.** §8 warns that
`census-route-expression-grading.json` and `fet-fusion-chaperone-clientship-2026-08-27.json` have
"a dated annotation-only correction prepared but not yet integrated at the time of writing; when it
is applied their blob identities change and no reported number, membership or quotation does."
That integration landed during this lane's run (commit `6466168`, "TD1 R1-R4 integrated"). For those
two, the mismatch is a **stale identity table**, exactly as forecast — this lane did not verify the
annotation-only / leaf-invariance property itself and makes no claim about it.

**The third is not covered by that warning.** `census_route_expression_grading.py` is a **producer
script**, not one of the two objects §8 names, and the same commit changed it from
`18625608…` to `fe00fe38…`. At this lane's starting HEAD (`1e35538`) all ten §8 identities matched
(check 04); after `6466168` three do not. Reported, not fixed.

### The five NOT-RE-DERIVABLE-LOCALLY rows, with the missing input named

| row | claim | exact missing input |
|---|---|---|
| `B-NRD-1` | the dependent fractions (5/91, 17/91, 89/91, 91/91) and the five mean differences as per-line Chronos observations | **DepMap 24Q4 `CRISPRGeneEffect.csv` + `Model.csv`.** Neither file is in this repository. The producer retains only per-gene mean/fraction summaries — no SD, no quantile, no order statistic, no per-line value (DEP-THRESHOLD C1). The per-line fetch is the parents' open gap and outside worker authority; it was **not attempted**. |
| `B-NRD-2` | the non-sarcoma arm's non-missing sample size behind 99.9 %, 99.4 %, 5.2 %, 11.9 %, 98.7 % | a retained `n_rest` per gene. The producer emits only `n_sarcoma`. Same two CSVs. ⚠ The manuscript makes **no** claim that fails here — §1.2 already states the artifact supplies no comparator sample size. |
| `A-NRD-1` | that the standardized scores were formed against each array's all-probe reference distribution | the original **GEO series matrices** `GSE24369_series_matrix.txt.gz` (GPL6244) and `GSE4303-GPL3290_series_matrix.txt.gz`, plus the probe-to-symbol mapping tables. Not held; §8 claims no hash for them. No retrieval attempted (direct HTTP egress is refused here). |
| `A-NRD-2` | whether GPL3290's deposited values were harmonized across the reference labels `CRH`, `CRH-mRNA`, `UHR` | authentic deposited processing/reference documentation for GSE4303. The manuscript states this as *not established* and holds the platform; the missing input is named because the hold rests on it. |
| `L-NRD-1` | fifteen dated PubMed queries run 2026-08-27, Q15 returning 25 unscreened hits | a live PubMed/E-utilities query at that date. The counts **read back** from the committed clientship artifact but are a record of a dated network retrieval, not a locally recomputable quantity. |

### Known-answer control — passed

The proposal requires at least one claim a sibling lane already re-derived, and requires it to
reproduce that lane's value.

* **CDK7 / CDK9 (rows `B-CDK7`, `B-CDK9`).** DEP-THRESHOLD `CLAIMS-AT-RISK.md` row A3 independently
  re-derived CDK7 = **−1.847** with selectivity **+0.085** and `rest_frac_dependent` **0.999**, and
  CDK9 = **−1.464** with selectivity **+0.017** and `rest_frac_dependent` **0.994**. This harness
  returns exactly those values from the same artifact.
* **The 91/176 denominator (row `B-DENOM`).** SYNLETH-2 and DEP-THRESHOLD both re-derived 91 as the
  per-gene screened denominator against 176 catalogued Soft Tissue/Bone models. Reproduced, and this
  lane additionally verified that **all** gene records in the artifact carry `n_sarcoma = 91`.

The harness is therefore not reporting from a broken instrument, and the three MISMATCHes above
stand as findings rather than as harness artefacts.

### What did reproduce that was worth testing

* All 14 Stream A group readings (Δ, Welch *t*, df, coverage) on both platforms — read back exactly.
* All 14 approximate *p* values and 95 % intervals, recomputed under the manuscript's own stated rule
  (SE = Δ ÷ *t*, printed rounded df) — every one lands on the printed digits.
* All 14 group Δ/*t*/df **independently rebuilt from the retained per-sample `z_vs_array` values**
  (unweighted gene mean per specimen, Welch two-sample) — all 14 reproduce the stored score to the
  printed precision, so §8's "level 2 replayable" claim holds for the group statistics and the
  4-dp rounding bound it discloses did not bite at this precision.
* The MYC bookkeeping (+1.0625 / +1.863) and the derived other-three means (−0.090 / +0.007).
* The Bonferroni illustration: α = 0.0036 cleared by exactly the three named readings, none on both
  platforms.
* All five Stream B rows and the **unique-integer** claim behind 5/91, 17/91, 89/91, 91/91 — each
  stored rounded fraction is compatible with exactly one integer over 91.
* The `self_validation` block (BRD9 in 5 synovial: −0.13, 20 %; SMARCB1 in 13 rhabdoid: −0.025,
  7.7 % against rest-of-panel −0.832 / 83.9 %) — the failing control the manuscript declines to
  credit is exactly as stored.
* `ACH-001519`, `has_crispr_gene_effect = false`.

**Reach of the sibling lanes' shared producer defect into this manuscript:** the defect does **not**
break any printed number here. It bounds them — every Stream B quantity in this paper is checkable
only at the single published −0.5 cut and only as a pooled mean or fraction, which is precisely what
rows `B-NRD-1` and `B-NRD-2` name. The manuscript already discloses this in §1.2 and §8.

## Validation / baseline

The known-answer control above is the baseline: sibling-lane values re-derived independently by
another owner from the same artifact. `checks/01` preserves the first execution, which **failed**
(exit 1, `TypeError` on a null `z_vs_array`); `checks/02` is the null-safe run (exit 0) that produced
the ledger; `checks/03` pins the mismatching identities and the tree state; `checks/04` shows HEAD
moved during the run.

## Provenance

* Lane start HEAD `1e35538daee86e1a34345340f7562d1e91147fa0`; the parent committed `6466168` and then
  `7a62238` **during** this run.
* ⚠ At lane start the manuscript was **modified and uncommitted** in the working tree. Every quoted
  value in the ledger is transcribed from the **working-tree** file, re-hashed at the moment of use:
  sha256 `9523555483f00cfee00b6cd4cf64f5615f57c011f1640297bf952399e742b3ba`. The lane-start committed
  version was a different object (sha256 `12c082b3d4dc…`). Commit `6466168` integrated the working
  tree, so the version read is now the committed version and the two hashes agree (check 03/04).
  The manuscript was **not** edited, reverted or diffed by this lane.
* Artifacts read: `research/modalities/emc-expression-panels.json`,
  `research/modalities/depmap-sarcoma-dependency.json`, `research/modalities/fet-ddr-axis-scan.json`,
  `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json`.
* Sibling lanes read: DEP-THRESHOLD (`CLAIMS-AT-RISK.md`, `threshold-sensitivity.json`),
  BIOMARKER-DEP-2, BIOMARKER-DEP-3, PUB-BIOMARKER-DEP, PUB-SYNLETH, SYNLETH-2, PUB-MTAP-PRMT5.
* Harness: `rederive_claims.py`, Python stdlib + scipy 1.17.1, no network, under one minute.

## Limitations

* ⛔ This is a **re-derivation of printed numbers against committed artifacts**. It is not a review of
  the paper, not a check of the biology, not a gate sweep, and not an assessment of whether the
  artifacts themselves are correct against their raw inputs — which cannot be done here at all
  (`A-NRD-1`).
* ⛔ Nothing here bears on EMC efficacy, safety, selectivity, therapeutic window or clinical
  readiness. A dependency score is a screen statistic. No line in the release supplies a CRISPR
  observation for this disease, and an unmeasured EMC dependency is **unknown, not zero**.
* The three MISMATCHes are **identity** mismatches, not number mismatches: no reported quantity,
  membership or quotation was found to disagree with its artifact. Whether the two flagged changes
  really are annotation-only was **not** verified by this lane.
* `census_route_expression_grading.py`'s changed identity is reported as a fact about the tree. This
  lane did **not** inspect what changed in it and draws no conclusion about whether any number moved.
* Coverage is the manuscript's quantitative claims. Qualitative statements, hedges and the §4
  literature readings were not graded beyond the numbers they carry.

## Stop condition — met

Stopped at the **first pass** over the claims. No second pass, no repair attempt, no diff to the
manuscript, no alternative reading sought for any MISMATCH. Nothing was `git add`ed, committed or
pushed; `scripts/preflight.sh` was not run; no subagent was spawned; no write left this lane
directory.

## Suggested next work (for the parent, not done here)

The §8 identity table is now stale for three objects. Correcting it is a **manuscript edit** and
belongs to the paper's owner, not to this lane. The unflagged one —
`census_route_expression_grading.py` — should be looked at first, because unlike the other two it was
not covered by §8's own annotation-only forecast.
