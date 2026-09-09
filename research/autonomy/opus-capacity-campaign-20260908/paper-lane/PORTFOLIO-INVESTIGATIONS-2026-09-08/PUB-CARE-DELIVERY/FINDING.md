---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-CARE-DELIVERY-2026-09-08
title: "What can be compared across EMC series at all — a care-delivery data-element coverage matrix, and an over-scoped absence claim it exposes"
level: L4
kind: investigation
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# PUB-CARE-DELIVERY — portfolio investigation

> ⛔ Nothing here is medical advice and nothing here asserts efficacy, safety, selectivity, a
> therapeutic window or clinical readiness. No patient was studied; no wet-lab work exists.

## 1 · The question

**Across the candidate EMC clinical series this repository has already identified, which
care-delivery data elements are actually reported — and for the elements reported by nobody, is
that a reading of the papers or the shadow of a series that was never examined?** Concretely: build
the series × element coverage matrix, and test whether the universal absence claims already written
into the care-delivery artifacts are true over the set they quantify over.

## 2 · Paper-level merit

* **Patient relevance.** Every care-delivery recommendation in a rare cancer is a comparison across
  small series. What can be compared is fixed entirely by what the series print. Naming the element
  set that two or more EMC series report — and the elements no reachable series reports — is the
  precondition for any future EMC care-delivery guidance, and is directly actionable as a reporting
  requirement for the next series, which is a lever that does not need a trial.
* **Non-trivial contribution.** The repository already holds an ACCESS census
  (`emc-km-reachability-census-2026-08-25.json`) and a one-element REPORTING census
  (`emc-km-admissibility-2026-08-27.json`, numbers-at-risk only, for curve reconstruction). Neither
  crosses access with the *care-delivery* elements — margin, margin definition, stage split, site,
  follow-up, event timing, treatment setting, unplanned excision — and neither states the denominator
  under which an element counts as unreported.
* **Attainable evidence.** Entirely from files already committed. It needs no new curation, no
  network, and no reopening of the closed IPD/KM reconstruction pilot.

## 3 · The exact evidence gap, and how it differs from completed or held work

| prior work | what it settled | why this is not it |
|---|---|---|
| Ledger **AUT-064** / `emc-care-delivery-endpoint-decision.md` §6 | The *margin finding* is not a paper — it restates PMID 40885991's own abstract. Publish decision answered "no". | This asks nothing about margin effect. It asks what any series reports, and it does not propose publishing the margin result. |
| **BLK-NO-FIELD-ATTENTION-MEASUREMENT** (term census over 554 records on `literature-cache`) | Held; the corpus does not resolve in this checkout (confirmed by campaign worker P2). | Different measurement, different corpus. This uses only committed artifacts, so it is not blocked by that ref. |
| **RT-IPD-SURVIVAL / KM admissibility pilot** (closed) | 16 series triaged for one element, the numbers-at-risk row; 1 admissible curve. | Not reopened. The risk-row column here is **copied verbatim** from that pilot's recorded verdicts — no figure re-read, no curve digitised, nothing re-run. |
| `portfolio-2026-09-05/recommendation.md` line 20 | Asked for "one bounded source-accounting contract **only if the existing artifact lacks a useful reusable table**". | The existing artifacts hold per-series values but **no cross-series element table and no claim denominators**. That gap is what this fills. |

## 4 · The bounded step taken, and what it found

Built `care-delivery-element-coverage.json` — a 17-series × 10-element matrix with a three-valued
status (`REPORTED` / `EXAMINED_NOT_PRINTED` / `NOT_EXAMINED`, the last sub-tagged `UNRETRIEVED`),
derived programmatically from six committed artifacts, plus a denominator audit of the two universal
absence claims in `emc-surgical-quality.json`.

**Result 1 — the comparable element set is two series wide, and one element wide beyond that.**
Of 17 candidate series (denominators summing to 1,133, **not additive** — they overlap):

| element | REPORTED | EXAMINED, NOT PRINTED | NOT EXAMINED |
|---|---|---|---|
| surgical margin distribution | 2 (230) | 0 | 15 (903) |
| margin definition printed | 2 (230) | 0 | 15 (903) |
| stage-at-diagnosis split | 1 (171) | 1 (59) | 15 (903) |
| primary site distribution | **3 (271)** | 0 | 14 (862) |
| median follow-up | 2 (230) | 0 | 15 (903) |
| time-to-event median | 2 (230) | 0 | 15 (903) |
| fitted Cox coefficients | 2 (230) | 0 | 15 (903) |
| numbers-at-risk row | 2 (16) | 3 (298) | 12 (819) |
| treatment setting / referral | **0** | 2 (230) | 15 (903) |
| unplanned excision defined | **0** | 2 (230) | 15 (903) |

Every care-delivery element except primary site rests on the **same two series** (masunaga2025,
chiusole2020). Nothing in EMC is comparable across three series except where the tumour arose.

**Result 2 — an over-scoped absence claim, which is the decisive finding.**
`emc-surgical-quality.json` states `treatment_setting.recorded_in_any_reachable_series: false` and
the same for `unplanned_excision`. The artifact's own `counts.series` is **2**. By the repository's
own two definitions of reachable — retrieved at least once in the admissibility census, or carrying a
full-text id in `emc-ipd-survival.json` — **five further series are reachable and carry no committed
reading of either field**: `bishop2019`, `drilon2008`, `martinbroto2020immunosarc1`,
`morioka2016trabectedin`, `stacchiotti2013anthracycline`. For those, both fields are **UNKNOWN, not
absent** (CLAUDE.md §4). The claim as written is a universal quantifier over an examined set of two.

The decision-relevant residue is narrower than five: `martinbroto2020immunosarc1`,
`morioka2016trabectedin` and `stacchiotti2013anthracycline` are systemic-therapy trial reports in
which treatment setting and unplanned excision are close to inapplicable. **`bishop2019` (n=41) and
`drilon2008` (n=87) are retrospective institutional series of operated patients, and they are the
two that could genuinely carry these fields.** `bishop2019` is the sharp case: its full text
*was already retrieved and read once* — `emc-site-curation.json` records its site counts as
`verified_against` "the PMC full-text record PMC7771031 … retrieved through the NCBI PMC full-text
API" — and it was **never read for margin, follow-up, treatment setting or unplanned excision**.

A proposed, **unapplied** narrowing of the two claims is in
`PROPOSED-UNAPPLIED-emc-surgical-quality-scope.diff` (that artifact is outside this lane's write
scope). It changes no measured value.

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `care-delivery-element-coverage.json` (the matrix, element counts, comparable-element
set, and the denominator audit), generated by `care_delivery_element_coverage.py`; plus the unapplied
diff above.

**Validation.** `validate_coverage.py` re-derives eight numbers and compares each against a number a
source artifact states independently: margin series count vs `emc-surgical-quality.counts.series`
(2=2); primary-site patients vs `emc-site-curation.pooled_extremity_fraction…denom` (271=271); the
risk-row column vs `emc-km-admissibility` `by_verdict` and `totals` (2=2, 3=3, 314=314, 16=16);
candidate count vs `emc-ipd-survival.candidate_sources` (17=17); and the deliberate 17−16 offset
(`immunosarc2emc2025`, a conference abstract absent from the admissibility census). **8/8 pass**,
exit 0 — `checks/02-validate-against-source-artifacts/`.

**Provenance.** Inputs, all committed: `research/modalities/emc-ipd-survival.json`,
`emc-surgical-quality.json`, `emc-site-curation.json`, `emc-recurrence-timing.json`,
`emc-prognostic-coefficients.json`, and `research/literature/emc-km-admissibility-2026-08-27.json`.
Repo `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`. No repo copy, no worktree,
no shared-state write, no `git add`/`commit`/`push`, no preflight, no subagent. One network act was
attempted and is recorded as a failure: `checks/03-pmc-fulltext-probe-bishop2019/` — a single $0 GET
of the Europe PMC full-text endpoint for PMC7771031 (an ordinary permitted public source, previously
used by this repository, not a denied route), answered **CONNECT tunnel failed, response 403**,
curl exit 56. No retry, no proxy around it, no substitute source.

**Limitations.** The matrix records what a *committed artifact* says a paper prints; for the 15
`NOT_EXAMINED` cells it is a statement about this repository's curation, **never about the papers**.
Series denominators overlap (Milan/INT, US institutions, Japanese populations) and are summed only to
weight the accounting. The element list is the one these artifacts support, not a validated reporting
checklist such as STROBE. `EXAMINED_NOT_PRINTED` for treatment setting and unplanned excision in
masunaga2025/chiusole2020 is trusted from `emc-surgical-quality.json`; those two source texts were
not re-read here. Nothing in this matrix bears on any clinical question, and the reporting-quality
framing is **not** a criticism of any study's conclusions.

**Stop condition.** Reached, and this lane stops here. Resolving the residue requires **one named
retrieval**: the full texts of `bishop2019` (PMC7771031) and `drilon2008` (PMC2779719) read for
margin, follow-up, treatment setting and unplanned excision, by the same PMC/Europe PMC full-text
route already used for `bishop2019`'s site counts. That route is blocked from this container (the 403
above) and dispatching the Actions fetch route is a network act outside this lane's authority under
the shared contract. Until it is done, the two fields stay UNKNOWN for those series, and this
investigation makes **no** claim that EMC series do not report treatment setting.

**Honest outcome.** This is a positive but small result plus a correction: a reusable table and a
demonstrated over-scoped absence claim. It does **not** make `PUB-CARE-DELIVERY` writable — that
endpoint is held by ledger row AUT-064's recorded publish decision ("no") and by
`BLK-NO-FIELD-ATTENTION-MEASUREMENT`, neither of which this work touches or reopens.
