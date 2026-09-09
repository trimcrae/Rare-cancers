---
id: DOC-PORTFOLIO-INVESTIGATION-PARKED-MODALITIES-2
title: "PARKED-MODALITIES-2 — the RT-RIBOZYME gate-2 clause now has a locator, and the locator contradicts it: one 2018 phase I solid-tumour trial, retrieved under a closed query"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: PARKED-MODALITIES-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
target_endpoint: PUB-PARKED-MODALITIES
repo_head: 65328136ec847a2ae4192cc8274cb6d5a12a6de2
predecessor: PARKED-MODALITIES-1
---

# PARKED-MODALITIES-2

Worker lane under `SHARED-CONTRACT.md`. Read-only outside this directory (proved in `checks/12`).
No `git add`, commit, push, `preflight.sh`, subagent, worktree, repo copy, GPU or paid API. The
diff is **unapplied**. Bibliographic data in this finding is from **PubMed**, retrieved through the
PubMed MCP route only; DOI links are given for the one record cited.

⛔ **NOTHING IS UN-PARKED HERE.** `RT-RIBOZYME` remains parked on gate 1
(`BLK-VECTOR-DELIVERY`), which this lane does not touch and which keeps the route parked
regardless of anything below. **No efficacy, safety, selectivity, therapeutic-window or
clinical-readiness claim is made or implied**, and where a retrieved trial reports outcomes they
are quoted, not endorsed or extrapolated.

## 1 · The question

`PARKED-MODALITIES-1` graded `RT-RIBOZYME`'s **gate 2** — "a 2000s-era technique with no modern
solid-tumour clinical footing" — **REASON-UNEVIDENCED**: no locator in the route
(`artifacts []`, `evidence []`), no blocker (only `BLK-VECTOR-DELIVERY` is inherited, and it is
gate 1), no technology record, no `TR-`/`TRG-` scan trigger, and uncited in the owner memo. It
named the next step and deliberately did not take it.

> **Does the gate-2 clause assert a checkable empirical proposition, and can a dated, closed
> PubMed/PMC retrieval give it a real evidence locator?**

## 2 · Paper-level merit

An unevidenced clause in a parked register is worse than a wrong one: it decides what is never
looked at again, and nothing watches it. The clause is also the entire basis for the endpoint's
claim that this route is *"gated twice over"* — the distinction the register uses to separate it
from every other parked row. Patient relevance is indirect and stated as such: which modality
classes stay off the EMC board is decided by exactly these sentences. **Auditing the wording of a
register is not a therapeutic claim and nothing here becomes one.**

The non-trivial contribution is methodological as much as factual: this is the first lane in the
campaign to test whether the admitted retrieval route can *close* — and it found a silent tool
defect that would have manufactured a false absence (§5.2). That is reusable by every later lane.

## 3 · What the clause actually asserts (task item 1)

The clause appears in **five** places in `systems/graph/routes.json` under `RT-RIBOZYME`, quoted
verbatim in `RETRIEVAL-DESIGN.md` §1, and once in prose at
`research/manuscripts/program/emc-post-degrader-options.md:958-960`, where it is asserted bare
while its two neighbouring route claims carry links.

Decomposed **before** retrieval (`RETRIEVAL-DESIGN.md` §2):

| # | proposition | checkable? |
|---|---|---|
| P1 | the literature is **largely 2000s-era** | yes — a year distribution over a fixed query is a countable property of the index |
| P2 | **no modern solid-tumour clinical footing** | partly — as "no such record in the retrieved public record"; an unpublished or unindexed trial is out of reach, and ClinicalTrials.gov is not the admitted route |
| P3 | "**modern**" and "**footing**" as thresholds | **NO** |
| P4 | "has real literature behind it" (memo) | yes — a non-zero count |

**P3 is a finding in its own right, pre-registered as such.** Neither "modern" nor "footing" is
defined anywhere — not in the route, the `closure_note`, the `readiness` block, the memo, or any
blocker. There is no year boundary and no criterion for what would count as footing. **No
retrieval can ever return "the clause is satisfied" or "violated"; it can only return the counts
underneath.** This was written down before the first call so it could not become a post-hoc excuse.

## 4 · The pre-registered design (task item 2)

`RETRIEVAL-DESIGN.md` was written and saved **before** the first `mcp__PubMed__*` call and is not
edited afterwards. It fixes: the seven queries verbatim (Q1-Q7), the route (`search_articles` plus
`get_article_metadata`, nothing else), the four closure criteria **C1-C4**, an enumeration ceiling
of **200**, and — critically — **what each possible outcome licenses**, so the diff could not be
chosen after seeing the result.

Closure criteria, in brief: **C1** an explicit `total_count`; **C2** `total_count` = 0 or
enumerable within the ceiling with every hit actually returned; **C3** the page count reconciles
(`has_more=false`); **C4** every identifier, journal, year, title and article type copied verbatim
from a returned record, never from memory. **Failure of C1-C3 ⇒ report UNCLOSED, not absence** —
following `PUB-TCIP` (`publications.json`, corrections 2026-09-08/09): *an unclosed literature
index cannot establish an absence in the field.* ANDGATE-2's lesson was pre-applied: **PubMed ANDs
every term, so a 0 on a long query is a parser artefact, not a fact about the world** — queries
were kept short and no 0 from a long query would have been read as absence.

## 5 · Execution and result (task items 3, 4)

Nine PubMed calls, all in `checks/01`-`checks/09` with their full results.

### 5.1 · Counts, verbatim

| id | query (exact) | total_count | returned | closure |
|---|---|---|---|---|
| Q1 | `trans-splicing ribozyme` | **272** | 100 | **not enumerable** (272 > 200 ceiling) — used as a denominator only |
| Q2 | `trans-splicing ribozyme cancer` | **55** | 55 | **CLOSED** |
| Q3 | `trans-splicing ribozyme AND Clinical Trial[Publication Type]` | **1** | 1 | **CLOSED** |
| Q6 | `ribozyme suicide gene tumor` | **27** | 27 | **CLOSED** |
| Q7 | `trans-splicing ribozyme hepatocellular carcinoma` | **11** | 11 | **CLOSED** |
| — | Q1, 2000-2009 | **97** | count only | C1 met |
| — | Q1, 2015-2026 | **55** | count only | C1 met |
| — | Q2, 2015-2026 | **19** | 19 | **CLOSED** |

### 5.2 · The tool defect that would have manufactured a false absence

`date_from` supplied **without** `date_to` is **silently dropped**. Q4 (`date_from=2015`) and Q5
(`date_from=2020`) each returned `total_count=272` and a PMID list byte-identical to the
*unfiltered* anchor, and their `query_translation` contained **no** `[Date - Publication]` clause.
No error was raised. Reading those as filtered counts would have said "272 papers since 2020" —
wrong in the permissive direction here, but wrong in the *absence-manufacturing* direction for any
lane whose filter should have narrowed a set toward zero. Both uninformative calls are preserved in
`checks/04`; the control in `checks/05` (`date_from=2024`+`date_to=2026` → 13, with the date clause
present in `query_translation`) confirms the defect is `date_from`-alone. **Every dated count in
§5.1 was accepted only after inspecting `query_translation` for the date clause.** Recommendation
for later lanes: always pass both bounds, and always read `query_translation`.

### 5.3 · The result — a hit, not an absence

Q3 is **closed** (`total_count=1`, fully enumerated, `has_more=false`) and returns one record.
Fields copied verbatim from the returned record (`checks/09`), according to PubMed:

> **PMID 30393375** · [DOI](https://doi.org/10.1038/s41417-018-0055-9) ·
> *"Phase I trial of intravenous Ad5CRT in patients with liver metastasis of gastrointestinal
> cancers."* · **Cancer Gene Ther** 2018;26(5-6):174-178 ·
> article types **"Clinical Trial, Phase I"**, "Journal Article", "Research Support, Non-U.S.
> Gov't" · MeSH includes *Gastrointestinal Neoplasms*, *Liver Neoplasms*, *Genetic Vectors*,
> *Telomerase*, *Thymidine Kinase*, *Humans*.

Its abstract states, verbatim, that Ad5CRT is *"a replication-defective adenovirus vector
expressing HSVtk … modulated by a specific **trans-splicing ribozyme** that targets human
telomerase reverse transcriptase (hTERT)-encoding RNAs"*, that treatment was *"feasible and well
tolerated in patients with gastrointestinal cancer liver metastasis"*, and that it
*"did not provide meaningful clinical benefit"*. **These are the trial's own reported statements,
quoted; this repository asserts nothing about them and derives no efficacy, safety or window claim
from them.**

**Bounded statement of the outcome, in the required form:**

* A **human clinical trial of a trans-splicing ribozyme in a solid-tumour indication, published
  2018, is in the retrieved public record** — under query Q3, on **2026-09-09**, with closure
  `total_count=1`, `returned_count=1`, `has_more=false`.
* **No other clinical-trial-typed record**, and **no post-2018 clinical record**, is in the
  retrieved public record **under these queries, on this date, with this closure.**
* Publication activity is **not** extinct: 272 all years, 97 in 2000-2009, 55 in 2015-2026, 19
  cancer-tagged since 2015 (closed).
* ⛔ This is **NOT** a statement that the field has or has not solved anything. Q1 is unclosed for
  enumeration and no absence is asserted from it.

### 5.4 · Verdict on the clause

**Gate 2 is no longer REASON-UNEVIDENCED — it now has a locator, and the locator does not support
the clause as written.**

* *"no modern solid-tumour clinical footing"* — **contradicted in its literal form** by one
  retrieved 2018 phase I solid-tumour trial. Whether one phase I trial that reported no benefit
  constitutes "footing" is **undecidable, because the clause never defined the term** (P3).
* *"largely a 2000s-era approach"* — **directionally supported but overstated**: 97 of 272 in
  2000-2009 is the densest decade, but 55 since 2015 is not a dead literature.
* The memo's *"has real literature behind it"* — **supported** (272 > 0).

**UNEVIDENCED WAS NOT FALSE, AND CONTRADICTED-AS-WRITTEN IS NOT UN-PARKING.** Gate 1 stands
untouched. Note also that the single retrieved trial is itself **vector-delivered adenovirus** —
i.e. it sits *inside* gate 1, not outside it.

## 6 · Artifact · validation · provenance · limitations · stop condition (task item 5)

* **Artifact** — `RETRIEVAL-DESIGN.md` (pre-registration); `UNAPPLIED-rt-ribozyme-gate2-locator.patch`;
  `build_diff.py`; `checks/01`-`checks/12`.
* **Validation / baseline** — the baseline is the **pre-registered** closure criteria, fixed before
  any call, plus the `checks/05` date-filter control and the `checks/04` preserved negative. The
  diff build asserts, before emitting: route count unchanged (83 → 83), `remaining_unknowns` and
  `readiness.missing` lengths unchanged, `blockers_inherited == ["BLK-VECTOR-DELIVERY"]`,
  `state.status == "parked"`. `git apply --check` → **exit 0** (`checks/11`, no pipes).
* **Provenance** — repo HEAD `65328136ec847a2ae4192cc8274cb6d5a12a6de2`;
  `systems/graph/routes.json` sha256 `17d208e4…5f3d3b`, identical before and after
  (`checks/10`, `checks/12`); `git status --porcelain systems/graph/` → 0 paths. Retrieval date
  **2026-09-09**, PubMed MCP route only — no direct HTTP, no other index, no closed route
  (B1/B2/B4) touched, retried, proxied around or relabelled; R1-R4 not restarted.
* **Limitations.**
  1. **PubMed/PMC only, title/abstract/MeSH indexing only.** "Not in the retrieved public record"
     means exactly that. A trial registered but unpublished, published outside PubMed's index, or
     described without the retrieved vocabulary would not appear. **ClinicalTrials.gov was not
     searched — it is not the admitted route for this lane.**
  2. **Q1 is UNCLOSED for enumeration** (272 > the pre-registered ceiling of 200). Its counts are
     used only as denominators; no absence rests on it.
  3. **P3 is unresolvable by any retrieval.** "Modern" and "footing" have no definition, so the
     clause cannot be adjudicated true or false — only replaced by counts. The diff does exactly
     that and no more.
  4. **Only the one decisive record's full metadata was pulled.** The other 54 cancer-set and 27
     adjacent-set records were enumerated by PMID but **not read**; their article types and years
     are **UNKNOWN to this lane** and are recorded as unknown, not as absent-of-trials. Q3's
     publication-type filter is what carries the trial claim, not my reading of that list.
  5. **No full text was retrieved** for PMID 30393375; every quotation is from the returned
     PubMed abstract and metadata fields.
  6. **Diff interaction, flagged not resolved.** `PARKED-MODALITIES-1`'s unapplied patch edits the
     *same* field `RT-RIBOZYME.remaining_unknowns[1]` (to flag it UNEVIDENCED). Both patches are
     built against the same unmodified HEAD and **will conflict if applied in sequence.** Mine
     supersedes the intent of that hunk — the clause is no longer unevidenced. **The parent must
     apply at most one, and should prefer this one for that field**; PARKED-MODALITIES-1's other
     five hunks are unaffected. I did not modify another lane's artifact.
* **Stop condition — reached and honoured.** The design fixed Q1-Q7 plus at most one metadata call
  per query, and **no query was added after seeing results**. All seven ran; the decisive one
  closed; the record's fields were copied verbatim; the diff proves clean. **Stop here.**

## 7 · The diff — `UNAPPLIED-rt-ribozyme-gate2-locator.patch`

**Five string edits, all inside `RT-RIBOZYME` in `systems/graph/routes.json`.** Prepared, proved,
**not applied** — the parent alone records shared state.

| field | change |
|---|---|
| `remaining_unknowns[1]` | replaces the uncited gate-2 clause with the dated closed retrieval, its counts, and the bounded residual unknown |
| `grade.value` | "a 2000s-era technique with no modern solid-tumour clinical footing" → the single retrieved 2018 phase I record |
| `closure_note` | same, short form |
| `readiness.why_not_higher` | "a technique with no modern clinical footing" → the retrieved clinical base |
| `readiness.missing[1]` | "a modern demonstration" → "a solid-tumour clinical demonstration later than the single retrieved 2018 phase I trial" |

Every replacement **preserves the superseded wording verbatim** in a dated
`⚠ CORRECTED 2026-09-09 (PARKED-MODALITIES-2 …; SUPERSEDED, RETAINED VERBATIM: "…")` correction, in
this repository's established form, and **every one restates that the route remains parked on
BLK-VECTOR-DELIVERY** and that no efficacy, safety, selectivity, therapeutic-window or
clinical-readiness claim is made — so no correction can be read as an un-parking. No guard, floor,
gate, matcher, pin or test is touched. No blocker, trigger, technology state, `blocked_by` edge,
`revival_trigger`, `state.status` or element count is changed. The file remains valid JSON.

**Proof:** `git apply --check --verbose` → **exit 0** (`checks/11`, real exit code, no pipes).
The build's `git diff --no-index` exit **1** is preserved in `checks/10` — 1 means *differences
present*, the expected value for that command.

## 8 · Checks

| dir | what | exit |
|---|---|---|
| `01-pubmed-Q1-anchor` | anchor, total 272 — **not enumerable**, denominator only | 0 |
| `02-pubmed-Q2-cancer` | 55/55, CLOSED | 0 |
| `03-pubmed-Q3-clinical-trial-pubtype` | 1/1, CLOSED — **the decisive call** | 0 |
| `04-pubmed-Q4Q5-date_from-only-SILENTLY-DROPPED` | **preserved uninformative calls**: `date_from` alone is dropped; no number used | 0 |
| `05-pubmed-date-filter-control` | control proving the defect is `date_from`-alone | 0 |
| `06-pubmed-Q6-adjacent-phrasing` | 27/27, CLOSED | 0 |
| `07-pubmed-Q7-hepatocellular` | 11/11, CLOSED | 0 |
| `08-pubmed-era-split` | 97 (2000-2009), 55 (2015-2026), 19 cancer since 2015 CLOSED | 0 |
| `09-pubmed-metadata-PMID30393375` | verbatim record fields | 0 |
| `10-build-diff` | patch built; input sha recorded | 1 *(differences present — expected)* |
| `11-apply-check` | `git apply --check --verbose` | **0** |
| `12-tree-untouched` | routes.json sha identical to input; `git status` 0 paths | 0 |
