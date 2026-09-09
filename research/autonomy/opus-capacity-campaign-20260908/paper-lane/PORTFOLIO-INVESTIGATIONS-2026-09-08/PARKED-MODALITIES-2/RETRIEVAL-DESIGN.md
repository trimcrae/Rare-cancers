---
id: DOC-PORTFOLIO-INVESTIGATION-PARKED-MODALITIES-2-DESIGN
title: "PARKED-MODALITIES-2 — pre-registered retrieval design for the RT-RIBOZYME gate-2 clause"
level: L4
kind: preregistration
status: live
date: 2026-09-09
lane: PARKED-MODALITIES-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
written_before_execution: true
---

# Pre-registered retrieval design — written BEFORE any PubMed/PMC call

This file was written and saved before the first `mcp__PubMed__*` call of this lane. Nothing in it
is edited after execution begins; results go in `FINDING.md` and `checks/`.

## 1 · The clause under test, verbatim

From `systems/graph/routes.json`, route `RT-RIBOZYME`, four places:

* `grade.value` — "Tier 3 — vector delivery; **a 2000s-era technique with no modern solid-tumour
  clinical footing**"
* `closure_note` — "Vector delivery, and **a technique with no modern solid-tumour clinical
  footing**."
* `remaining_unknowns[1]` — "**Whether the technique has any modern solid-tumour footing at all —
  it is largely a 2000s-era approach.**"
* `readiness.why_not_higher` — "Two independent gates — delivery and **a technique with no modern
  clinical footing** — and no computation addresses either."
* `readiness.missing[1]` — "**a modern demonstration of trans-splicing ribozymes**"

Upstream prose, `research/manuscripts/program/emc-post-degrader-options.md:958-960`:
"**Trans-splicing ribozyme → suicide gene** triggered by the fusion transcript is the most elegant
fusion-exclusive idea in the list and **has real literature behind it**, but it is vector-delivered
and **has no modern solid-tumour clinical footing**." — asserted bare, no citation.

## 2 · What empirical proposition this asserts

Decomposed into the parts a retrieval can and cannot touch.

| # | proposition | testable by a bounded PubMed/PMC retrieval? |
|---|---|---|
| P1 | Trans-splicing ribozymes applied to cancer are **largely a 2000s-era** literature | **Yes** — a publication-year distribution over a defined query is a countable property of the index. |
| P2 | There is **no modern clinical footing in solid tumours** — i.e. no recent human clinical study of a trans-splicing ribozyme in a solid tumour | **Partly** — retrievable as "no record of publication type Clinical Trial etc. in the retrieved set". A trial that exists but is unpublished/PubMed-unindexed is out of reach; ClinicalTrials.gov is NOT the admitted route here. |
| P3 | "**footing**" / "**modern**" as thresholds | **No.** Neither term is defined anywhere in the route, the closure note, the memo, or any blocker. There is no year boundary and no criterion for what would count as footing. |
| P4 | "has real literature behind it" (memo) | **Yes**, as a non-zero hit count. |

**P3 is itself a finding and is reported as one:** the clause has no stated threshold, so no
retrieval can ever return "the clause is satisfied/violated" — only the underlying counts. This is
recorded before seeing any result so it cannot be a post-hoc excuse.

## 3 · The queries (fixed in advance)

Route: `mcp__PubMed__search_articles` only, plus `mcp__PubMed__get_article_metadata` for verbatim
record fields. No direct HTTP; no other index. ANDGATE-2's lesson is pre-applied: **PubMed ANDs
every term, so over-specified queries return 0 for a parser reason, not a world reason.** Queries
are therefore kept short, and a 0 on a long query is treated as uninformative, never as an absence.

| id | query string (exact) | purpose |
|---|---|---|
| Q1 | `trans-splicing ribozyme` | the anchor set; total_count = the denominator for P1/P4 |
| Q2 | `trans-splicing ribozyme cancer` | cancer subset |
| Q3 | `trans-splicing ribozyme AND Clinical Trial[Publication Type]` | P2, direct |
| Q4 | `trans-splicing ribozyme` with `date_from=2015` | P1 modern-era count |
| Q5 | `trans-splicing ribozyme` with `date_from=2020` | P1 recent count |
| Q6 | `ribozyme suicide gene tumor` | adjacent-phrasing sweep (guards against a vocabulary miss) |
| Q7 | `trans-splicing ribozyme hepatocellular carcinoma` | the best-known solid-tumour application line |

Q4/Q5 are the same anchor query with a date filter, so their counts are directly comparable to Q1 —
that comparability is the whole point and is why the query string is held constant.

## 4 · Closure criteria — declared in advance

A result may be reported as a **bounded absence** only if ALL of:

* **C1** — the tool returns an explicit `total_count` for the query.
* **C2** — `total_count` is small enough to enumerate in full (**ceiling: 200**), and records are
  actually retrieved for **every** hit via paging (`retstart` in steps of `max_results`), OR the
  query's total_count is 0.
* **C3** — the returned page count reconciles with `total_count` (last page short or empty; no
  silent truncation).
* **C4** — every identifier, journal, year, title and publication type quoted is copied verbatim
  from a returned record. No citation from memory. Any record I cannot retrieve is listed as
  unretrieved, not summarised.

If C1 fails (no total_count) or C2/C3 cannot be satisfied, the outcome is **UNCLOSED** and is
reported as UNCLOSED. Per `PUB-TCIP` (`publications.json`, corrections 2026-09-08/09): *an unclosed
literature index cannot establish a field-wide absence.* An UNCLOSED result still supports the
diff in §5 — because it still shows the clause has no locator.

## 5 · What each outcome licenses — fixed in advance

| outcome | what the diff does |
|---|---|
| **A.** Closed, and modern solid-tumour clinical records found | clause is wrong as written → diff scopes it to what is evidenced, citing the found records, superseded wording retained verbatim |
| **B.** Closed, and none found | clause gets a **real locator**: the dated bounded retrieval, quoted in the bounded form |
| **C.** UNCLOSED | clause is scoped to what is actually evidenced (i.e. to nothing in this repository), with the attempted retrieval recorded as attempted-and-unclosed |

In **every** branch: **the route stays parked on gate 1 (`BLK-VECTOR-DELIVERY`), the clause is
never withdrawn, and no efficacy, safety, selectivity, therapeutic-window or clinical-readiness
claim is made.** Reported wording is always "not in the retrieved public record, under these
queries, on this date, with this closure" — never "the field has not solved it".

## 6 · Stop condition, fixed in advance

Stop when Q1-Q7 have each been executed once and their results recorded, plus at most one metadata
call per query needed to copy record fields verbatim. **No query is added after seeing results.**
No full-text retrieval unless a specific record's publication type is ambiguous from metadata.
