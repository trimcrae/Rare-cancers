---
id: DOC-PORTFOLIO-REPURPOSING3-LEDGER-FINDING
title: "REPURPOSING-3-LEDGER — the four gate errors that lane introduced, retrieved and prepared as an unapplied ledger diff"
level: L4
kind: evidence
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# REPURPOSING-3-LEDGER — finding

## Question

Exactly which prose identifiers did REPURPOSING-3 introduce into `lint_citations.py`'s provenance
gate, does each one resolve to a real PubMed record retrieved through the admitted connector, and
can the ledger rows that would close those four errors be prepared as a diff that applies cleanly to
current HEAD without touching the linter, its matcher, its baseline or any allowlist?

## Merit

The gate exists because, on 2026-08-07, an agent wrote a PMID **from recollection** into a
manuscript and it passed `lint_claims.py` twice. Its rule is deliberately narrow and deliberately
unforgiving: a prose identifier that no fetch product carries and no ledger row names is an error
*the moment it is written*. A lane that leaves four such errors standing has, from the gate's point
of view, done the thing the gate was built to catch — even though (as it turns out here) all four
identifiers are real. Closing them **by retrieval** rather than by baselining is the only move that
keeps the gate's meaning intact, and it is directly patient-relevant in the weak-but-real sense the
ledger itself claims: the count of citations nobody has ever checked falls by four, honestly.

## Evidence gap addressed

Re-derived, not taken on faith. `python3 research/manuscripts/lint_citations.py` (check `01`) exits
**1**, writes its `::error::` lines to **stderr** (the parent's "459 → 463" was read from the stderr
stream; check `01` reproduced **463** total `::error::` lines at that moment), and exactly **four**
of them name a `.../REPURPOSING-3/` prose file.

⚠ **One correction to the dispatch.** The parent described all four as `UNANCHORED DOI`. They are
not: two are DOIs, one is a PMCID and one is a PMID.

⚠ **The count is not stable and that is not this lane's doing.** Other campaign lanes are writing
into the same checkout while the gate runs, and `_tracked()` scans untracked-but-not-ignored files,
so the repo-wide error total moved from **463** (check `01`) to **450** (check `16`) inside this
lane's own session. The paired control in check `16` therefore shares **one** `survey()` between
both arms, so the concurrent churn cannot confound the measured delta.

### 1 · The exact, complete list — with the line each appears on

Line numbers are of the two REPURPOSING-3 prose files as they stood at measurement (check `01`).
All four are unanchored *only* because they appear in prose and in no `.json`/`.jsonl` fetch product.

| # | Kind | Identifier | `FIVE-REFERENCE-TABLE.md` | `FINDING.md` (REPURPOSING-3) |
|---|---|---|---|---|
| 1 | DOI | `10.1002/cam4.1438` | line **59** | line **141** |
| 2 | DOI | `10.1097/CCO.0b013e32812143d9` | line **46** | line **138** |
| 3 | PMCID | `PMC5943440` | line **58** | line **84** |
| 4 | PMID | `29573200` | line **58** | lines **84**, **134** |

⭐ **They are three forms of two papers, not four independent citations.** Items 1, 3 and 4 are the
DOI, PMCID and PMID of one 2018 *Cancer Med* record. Item 2 is a second, separate paper. The gate
counts identifier forms; the ledger rows say so explicitly so a reader cannot mistake three forms
for three checks.

⚠ Note that PMID `17545802` — the PMID of item 2 — is **not** in the error list: it is already
anchored elsewhere in the tree. Only its DOI form was new.

### 2 · Retrieved metadata — verbatim from the PubMed MCP connector, the admitted route

According to PubMed. Every string below is copied from the tool response; nothing is typed from
memory. Full transcripts in `checks/02`–`checks/05`.

**Paper A — items 1, 3, 4.** [DOI](https://doi.org/10.1002/cam4.1438)

* `identifiers`: `{"pmid": "29573200", "pmc": "PMC5943440", "doi": "10.1002/cam4.1438"}`
* `journal.iso_abbreviation`: **`Cancer Med`** (`journal.title`: `Cancer medicine`)
* `publication_date.year`: **`2018`** (`month` `03`, `day` `23`)
* `title`: *Anti-tumor effects of a nonsteroidal anti-inflammatory drug zaltoprofen on
  chondrosarcoma via activating peroxisome proliferator-activated receptor gamma and suppressing
  matrix metalloproteinase-2 expression.*
* `article_types`: `["Case Reports", "Journal Article", "Research Support, Non-U.S. Gov't"]`
* `citation`: `{"volume": "7", "issue": "5", "pages": "1944-1954"}`

Retrieved by two independent calls that agree: `convert_article_ids(id_type="doi",
ids=["10.1002/cam4.1438"])` → `{pmcid PMC5943440, pmid 29573200, doi 10.1002/cam4.1438}`;
`convert_article_ids(id_type="pmcid", ids=["PMC5943440"])` → the same triple from the other
direction; then `get_article_metadata(pmids=["29573200"])` returned the record itself.

✅ This **confirms** REPURPOSING-3's own characterisation of the record on every checkable point:
the journal, the year, the volume/issue/pages, and the article type **Case Reports**.

**Paper B — item 2.** [DOI](https://doi.org/10.1097/CCO.0b013e32812143d9)

* `identifiers`: `{"pmid": "17545802", "doi": "10.1097/CCO.0b013e32812143d9", "pii":
  "00001622-200707000-00015"}` — **no `pmc` field**
* `journal.iso_abbreviation`: **`Curr Opin Oncol`** (`journal.title`: `Current opinion in oncology`)
* `publication_date.year`: **`2007`** (`month` `Jul`)
* `title`: *Update on chondrosarcomas.*
* `article_types`: `["Journal Article", "Review"]`
* `citation`: `{"volume": "19", "issue": "4", "pages": "371-6"}`

⚠ **The converter did not resolve this DOI.** `convert_article_ids(id_type="doi", ...)` returned the
bare echo `{"doi": "10.1097/CCO.0b013e32812143d9", "requested-id": "10.1097/CCO.0b013e32812143d9"}` —
no PMID, no PMCID. **That response is indistinguishable from the response for a DOI that does not
exist**, and it is the same shape this ledger already records for
`DOI:10.1016/j.jclinepi.2017.08.010` on 2026-08-27. It was therefore resolved by a second route:
`lookup_article_by_citation(journal="Curr Opin Oncol", year=2007, volume="19", first_page="371",
author="Chow")` returned PMID `17545802`, and `get_article_metadata(pmids=["17545802"])` returned a
record whose `identifiers.doi` **is** `10.1097/CCO.0b013e32812143d9`. **That DOI match inside the
fetched record — not the converter — is what anchors this row.**

✅ Also confirms two things REPURPOSING-3 asserted: the article type is **Review**, as its prose
calls it, and PubMed returns **no PMC identifier**, consistent with its "no PMC record" finding.

**Nothing failed to retrieve.** All four identifiers resolved. The §4 disposition (remove the
citation, or leave the error standing) is therefore **not** needed, and no such claim is made.

### 3 · The artifact — an unapplied diff

`ledger-entries.diff` adds four `entries` rows and one top-level class note to
`research/manuscripts/citation-provenance-ledger.json`, in that file's own existing schema
(`files` / `id` / `key` / `kind` / `note` / `status` / `checked_on` / `checked_by` / `verified_on` /
`verified_by` / `verified_source` / `verified_title` / `verified_journal` / `verified_year` /
`verified_pmid` / `verified_pmcid`), following the precedent of the two non-baseline classes already
in the file (`_arxiv_class_added_2026_08_28`, `_pmcid_crossform_class_added_2026_09_08`): appended as
a labelled block, never mixed into the 2026-08-07 baseline.

**It is NOT applied.** `research/manuscripts/citation-provenance-ledger.json` is byte-identical to
HEAD (`git diff HEAD` on it: 0 lines). The diff is generated by `build_ledger_entries.py`, which
writes its candidate **outside the checkout** — see the measured reason below — and is reproducible.

## Validation

| Check | What | Exit |
|---|---|---|
| `01` | `lint_citations.py` full run, the measurement of record | **1** (463 `::error::`, 4 from REPURPOSING-3) |
| `02`–`05` | PubMed MCP retrievals (converter ×2, `get_article_metadata` ×2, `lookup_article_by_citation`) | tool responses retained verbatim |
| `06` | first build attempt — **FAILED**, `FileNotFoundError`, repo-root walk one level short | **1** (retained, not overwritten) |
| `07` | build after the path fix (candidate still inside the tree) | 0 |
| `08` | first diff generation | 1 (= differences found) |
| `09` | `git apply --check` on that first diff | **0** |
| `10` | dry run against the candidate ledger — **contaminated**, see below | 0 |
| `11` | self-anchoring measurement, real ledger, copy present | 1 |
| `12` | rebuild with the candidate written outside the checkout | 0 |
| `13` | final diff generation | 1 (= differences found) |
| `14` | **`git apply --check -v ledger-entries.diff`** | **0** |
| `15` | provenance dry run, candidate outside the tree | 0 |
| `16` | **paired control, one shared `survey()`** | 0 |

**The decisive result is check `16`.** One `survey()` scan, two ledgers:

```
unanchored identifiers (shared survey): 548
ARM A  real ledger      : 450 new-unanchored errors, 4 of them from REPURPOSING-3 prose
ARM B  candidate ledger : 446 new-unanchored errors, 0 of them from REPURPOSING-3 prose
DELTA A-B = 4
resolved by the diff: ['DOI:10.1002/cam4.1438', 'DOI:10.1097/CCO.0b013e32812143d9',
                       'PMCID:PMC5943440', 'PMID:29573200']
```

The diff removes **exactly** those four errors and **nothing else**. `git apply --check` exits **0**
against current HEAD (check `14`).

### ⛔ An incidental finding worth more than this lane's own task

While validating, this lane wrote its candidate ledger as a `.json` file **inside** the checkout.
`lint_citations._tracked()` scans committed *and* untracked-not-ignored files, and `ANCHOR_SUFFIXES`
is `.json`/`.jsonl` — so a copy of the ledger sitting in the tree **anchors every identifier the
ledger names**. Measured (checks `10`, `11`), with the **real** ledger otherwise untouched and not
one row added: unanchored fell **548 → 446**, and **all four REPURPOSING-3 errors disappeared**.

That is the 2026-08-07 self-anchoring incident exactly — a gate turned green by *adding a file* —
and it reaches further than the two named exclusions (`citation-article-types.json`,
`citation-retraction-sweep.json`) already cover, because the ledger's own path is excluded only as
`LEDGER`, not as a class. **No fix is proposed here** (this lane may not touch the linter, and the
honest repair is a scanner-side or convention-side decision, not a one-line exclusion). It is
recorded, with its measurement, so a reader finds it before a reviewer does. The candidate is now
built to the scratchpad and only the `.diff` is retained — a `.diff` is neither an anchor suffix nor
a prose suffix, so this lane's own artifacts cannot anchor anything.

## Provenance

* Gate output: `research/manuscripts/lint_citations.py`, run in-place at
  `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`.
* Citation metadata: PubMed, via the PubMed MCP connector (`convert_article_ids`,
  `get_article_metadata`, `lookup_article_by_citation`), tool `response-date` **2026-09-08
  20:42 UTC**. The session clock rolled to 2026-09-09 mid-task; the ledger rows carry the date the
  **tool** returned, and say so.
* Ledger schema and the two non-baseline-class precedents: read from
  `research/manuscripts/citation-provenance-ledger.json` at HEAD before writing anything.
* Cited prose: `.../REPURPOSING-3/FIVE-REFERENCE-TABLE.md` and `.../REPURPOSING-3/FINDING.md`,
  unmodified by this lane.

## Limitations

* ⛔ **`verified` here means what it means everywhere else in this file — the identifier was fetched
  and PubMed answered.** It is not a claim that the citing sentence characterises the paper
  correctly beyond the fields actually compared (journal, year, volume/issue/pages, article type),
  and it is not a retraction check: `lint_citation_types` still reports all four as **NOT SWEPT**,
  i.e. retraction status **UNKNOWN**, which is not the same as clean. Closing that needs the
  retraction sweep to run, not a ledger row.
* No fetch product in this repository carries these four identifiers. The ledger count falls the
  fully honest way only when a CI job with real egress writes a committed record for them; that is
  named in the class note rather than papered over.
* ⛔ **No clinical claim is made or implied.** Paper A's n=1 case is a **grade 2 cervical
  chondrosarcoma**, not EMC, and no efficacy, safety, selectivity or therapeutic-window conclusion
  is drawn from it here — the ledger rows say so in their own `note` field so the caveat travels
  with the record.
* The repo-wide error total is a moving number while sibling lanes write; only the paired-control
  delta (check `16`) is a stable measurement.
* Nothing in `lint_citations.py`, its matcher, its baseline, `citation-retraction-sweep.json` or any
  allowlist was changed, proposed for change, or weakened. Nothing was committed, staged or pushed;
  `scripts/preflight.sh` was not run.

## Stop condition

Reached. The four identifiers are enumerated with their lines, all four were retrieved through the
admitted route (none failed), the diff exists and `git apply --check` returns **0**, and a paired
control shows it resolves exactly those four gate errors and no others. **The remaining act —
applying the diff — is the parent's**, since only the parent records shared state.
