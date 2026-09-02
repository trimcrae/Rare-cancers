---
id: DOC-SPRINT-S33-DEPOSIT
title: "S33-DEPOSIT — AUT-PD-083 and AUT-PD-084: neither defect is in any published Zenodo deposit"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S33-DEPOSIT — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S33-DEPOSIT — the two "defects inside the released deposit", refuted at the manifest

**Item(s):** `AUT-PD-083`, `AUT-PD-084`
**Owned paths:** `research/autonomy/sprint-2026-09-01/S33-DEPOSIT.md`; analysis script
`<scratchpad>/s33_pmid_title_coverage.py` — a scratchpad one-off that does not exist in this
repository and was not committed; read-only, writes nothing, contents reproduced verbatim in §4 so a
reader can rebuild it
**Read at:** `git rev-parse HEAD` = `b6397c5666efbf7d6755dfaedabc6a4bef24a8ee`
**Started/Finished (UTC):** 2026-09-01T19:48Z / 2026-09-01T19:58Z

## Verdict

**REFUTED — both rows.** Neither defect is, or ever was, inside a published Zenodo version.

- **AUT-PD-083 is refuted twice over.** The inverted wording was real in the repository from
  2026-08-24 to 2026-08-30, but `research/modalities/aso-control-oligos.json` **entered the deposit
  only at version 22180100 (published 2026-08-30), by which commit the field already read CLEARS.**
  Every Zenodo version published while the file said FAILS did not contain the file.
- **AUT-PD-084's first half rests on a false premise.** It is not one fact with two sources. It is
  **two different reported quantities that share the numerals 7 and 10**, each verbatim-anchored to
  its own PMID inside a file that is itself in the deposit. Its second half — the empty citation
  record — was closed on 2026-08-31, three days after the row was filed.

**Nothing here needs trimcrae.** No published artifact is wrong, so there is no correction to issue,
so there is no outward-facing act in scope. §3 is not triggered. Details in §5.

---

## 1 · The published record, read from the committed state rather than remembered

`research/manuscripts/aso/deposit-state.json` at HEAD, and every version's manifest digest
**re-derived from the manifest committed at that version's `git_revision` and byte-compared** to the
digest `deposit-state.json` records:

| Zenodo version DOI | published | `git_revision` | recorded `manifest_digest` | digest recomputed from that revision's manifest | files |
|---|---|---|---|---|---|
| `10.5281/zenodo.22182180` | 2026-08-31 (**current published**) | `866594627ab0` | `a4d4ad6f1ca0…` | `a4d4ad6f1ca0…` ✅ **match** | 515 |
| `10.5281/zenodo.22180100` | 2026-08-30 | `fbb473bce3ac` | `53d793d4c29d…` | `53d793d4c29d…` ✅ **match** | 484 |
| `10.5281/zenodo.22166420` | 2026-08-30 | `c84bc23d251a` | `1ddbb1e8a036…` | `1ddbb1e8a036…` ✅ **match** | 483 |
| `10.5281/zenodo.22061075` | 2026-08-23 | `091721519a7a` | `989d462e101c…` | `23f3d16ee408…` ⚠ **mismatch — see note** | 483 recorded / 482 in that manifest |
| `10.5281/zenodo.22229096` | **DRAFTED 2026-09-01, NOT PUBLISHED** | `850edb3358ba` | `f59a02acd74e…` | `f59a02acd74e…` ✅ **match** | 515 |

Concept DOI for all of them: `10.5281/zenodo.22028915`.

⚠ **The one mismatch, reported rather than smoothed over.** For `22061075` the manifest committed at
the revision `deposit-state.json` names carries a different digest and one fewer file than the record
states. **It does not touch either row** — the file AUT-PD-083 is about did not exist in the
repository at all on 2026-08-23 (created 2026-08-24, `5e24cccf`), so no reading of that manifest can
put it inside `22061075`. I did not chase the mismatch further: it is outside both rows and outside my
owned paths. It is proposed as its own ledger row in §7 rather than absorbed silently.

⛔ **`22229096` is a DRAFT, not a publication**, and both manuscripts cite it. That is the deliberate
PENDING window `deposit-state.json` exists to make legible, it is another seat's subject tonight, and
**I have kept it strictly separate from "published" everywhere below.**

---

## 2 · AUT-PD-083 — the control-oligo artifact. REFUTED.

### 2a · The wording is already corrected in the working tree, and was corrected before the current published version

```
$ git log --format='%H %ad %s' --date=iso -- research/modalities/aso-control-oligos.json
65eccd59f842… 2026-08-30 18:44:09 +0000  round 22: four blockers fixed, and four of five seats found the same one
5e24cccf288e… 2026-08-24 17:50:22 +0000  ASO article: two named controls, a floor on ΔTm, and the exon-2 argument
```

The field at HEAD, and at both deposit revisions that matter:

```
$ for rev in 866594627ab0… 850edb3358ba…; do git show $rev:research/modalities/aso-control-oligos.json | …; done
866594627ab0 : FIX PRESENT   "A control here is a sequence that CLEARS the same specificity screen the reagent clears…"
850edb3358ba : FIX PRESENT   "A control here is a sequence that CLEARS the same specificity screen the reagent clears…"
```

The old text is retained under `_superseded_not_a_claim_of_inertness` (rule 1.2), and the live field
carries its own correction note naming the date and the discriminating evidence (both controls'
`control_longest_parent_duplex_through_gap_bp` = 6 and 7 against a cut of 10, i.e. clearing).

### 2b · ⭐ The finding that actually settles it: the file was never in a deposit that said FAILS

The row's load-bearing sentence is *"Both fields ship in the released deposit, so a reviewer reads
both."* **That was already false on the day the row was filed.** Reading each version's own manifest:

| deposit version | published | `aso-control-oligos.json` in its manifest? | what the field said at that revision |
|---|---|---|---|
| `22061075` | 2026-08-23 | **NO** (482-file manifest; file did not yet exist) | — |
| `22166420` | 2026-08-30 | **NO** — verified against the manifest whose digest matches the record exactly | FAILS |
| `22180100` | 2026-08-30 | **YES** — it is one of exactly two files added over `22166420` | **CLEARS** |
| `22182180` | 2026-08-31 (current) | YES | **CLEARS** |

```
added in 22180100 over 22166420: ['research/modalities/aso-control-oligos.json',
                                  'research/modalities/aso_control_oligos.py']
removed:                         ['research/manuscripts/aso/fusion-junction-aso-cover-letter.md']
any 'control-oligos' string anywhere in the 22166420 manifest: False
```

**The artifact and its corrected wording entered the public record in the same version.** A reader
following any DOI this project has ever minted has never been able to read the FAILS sentence as a
live claim.

### 2c · What a reader following the DOI encounters today

The current field, which is correct, plus a `_superseded_` sibling holding the retired wording under a
name that says it is retired, plus an inline note stating what changed, when, and on what evidence.
That is the repository's own rule-1.2 retraction pattern, and `lint_consistency.py` is written to
clear exactly this shape. **No published sentence is wrong and no correction is owed.**

---

## 3 · AUT-PD-084, first half — "one fact, two sources". PREMISE REFUTED.

The row asserts the seven-to-ten RNase-H1 range is credited to `PMID 35664704` in the artifact and to
`PMID 24981949` in the journal article, and asks which is the source. **The question does not arise:
they are two different reported quantities.** Both quotes are committed verbatim, with surrounding
context, in `research/manuscripts/aso/lit-targets-aso-gap-length.json` — **which is itself one of the
515 files in the current published deposit**, so a reader following the DOI can settle this from
inside the deposit:

| | `PMID 24981949` (Kauppinen 2005, LNA review) | `PMID 35664704` (RNA modifications can affect RNase H1-mediated PS-ASO activity) |
|---|---|---|
| verbatim fragment | *"DNA gap size between 7 and 10 nucleotides is optimal"* | *"minimum length of 7 to 10 RNA:DNA hybridized nucleotides"* |
| unit | **DNA gap nucleotides** | **RNA:DNA hybridised nucleotides** (whole-duplex) |
| quantifier | **optimal** | **minimum**, for hybrid-binding-domain engagement |
| cited by | the journal article, ref 13, line 88 and line 219 | `aso-parent-gap-pairing*.json`, the `MIN_DUPLEX_BP` rationale |

Each attribution is correct against its own anchored quote. **No number is credited to two works.**
The journal article itself prints the unit distinction one clause later — *"a length of hybrid rather
than a count of gap nucleotides"* (line 89–90) — and again in Results, *"These are whole-duplex run
lengths rather than the enzyme's own unit."*

### ⚠ The residual that IS real, and it is smaller and different

The journal article's ten-base-pair criterion is a **hybrid** length. Inside the deposit, the file
that produces it says where ten comes from: *"10 is the strict end of the 7-to-10 hybridised
nucleotides PMID 35664704 reports as the minimum…"*. **`PMID 35664704` is cited nowhere in the
article and appears in none of its 24 references** (`grep -c 35664704` on the article = 0; on
`fusion-junction-aso-journal-references.md` = 0). So the article's criterion is sized, in the
deposit's own producing artifact, by a source the article does not name — while the source the
article *does* name at that sentence, `24981949`, reports a different unit.

**This is a provenance gap, not a contradiction, and it is not new.** Round 28's regression seat
already found it and already prescribed the remedy, in
`research/autonomy/review-seats/PUB-ASO-f6cdb93605e3bec780c1750a10887d939ebed554-seat-regression.json`:
*"Do not repair it by citing PMID 35664704 without also adding it to the reference list and stating
that its seven-to-ten is a count of hybridised nucleotides rather than of gap nucleotides."*
⛔ It is a manuscript edit, the ASO manuscript is explicitly not mine, and it is filed in §7 rather
than taken. It is **not** a defect in a published artifact: everything the deposit says is true; the
article simply does not name one of its inputs.

---

## 4 · AUT-PD-084, second half — the empty citation record. CLOSED 2026-08-31, three days after filing.

The row: *"the journal article has NO committed PMID→title artifact … so any tool resolving that
manuscript's citations gets an empty record — PMID 39912803 did."*

Measured tonight with `<scratchpad>/s33_pmid_title_coverage.py` (does not exist in this repository;
its source is in §4), which extracts every PMID from
`fusion-junction-aso-journal-references.md` and every inline `<!--PMID:…-->` from
`fusion-junction-aso-journal-article.md`, then scans every JSON under `research/` outside
`research/autonomy/` for an object keyed by that PMID carrying a non-empty `title`:

```
references.md PMIDs : 24 unique 24
article inline PMIDs: 22 unique 17
in article not in ref list: []
PMIDs with NO title in any committed research/*.json (excl. research/autonomy): 0
```

**All 24 resolve.** `39912803` specifically now resolves to *"Assessing Hybridization-Dependent
Off-Target Risk for Therapeutic Oligonucleotides: Updated Industry Recommendations"*, Nucleic Acid
Ther, 2025 — committed in `research/manuscripts/aso/lit-targets-aso-instruments.json` under
`supplementary_record_2026_08_31_…`, i.e. **added 2026-08-31**, and independently in
`research/manuscripts/aso/nat-scope-census.json`.

`claim_audit.py` already carries the finding as a documented comment above `REFERENCE_SOURCES` and
already carries the fix: the missing title is reported as `title: null` **with `record_source`
naming where the record did come from**, rather than silently blank. Read back from the committed
verdicts artifact:

```
research/manuscripts/aso/fusion-junction-aso-claim-audit-verdicts.json → sample[24].evidence.sources[0]
  {"pmid":"39912803","title":null,"journal":null,"year":null,
   "record_source":"research/manuscripts/aso/journal-reference-authors.json",
   "resolved_from_committed_record": true}
```

⭐ **What remains is a build request, not a defect.** No single artifact covers all 24 — the titles
are spread over seven files (`lit-targets-aso-round7-precedents.json`,
`lit-targets-aso-bibliography-completion.json`, `fusion-consensus-probe.json`,
`fusion-junction-aso-submission-references.json`, `lit-targets-aso-delivery-routes.json`,
`lit-targets-aso-instruments.json`, `fusion-junction-aso-claim-audit-verdicts.json`,
`remaining-reference-metadata-2026-08-09.json`). The row's ask — *emit
`fusion-junction-aso-journal-references.json` alongside the markdown* — is still unbuilt (no such
file exists) and is worth building, but **it is a tooling convenience with no reader-facing harm**:
the deposit already contains `fusion-junction-aso-journal-references.md`, a complete 24-entry list
with full titles (`grep -c '^[0-9]*\. '` = 24, `grep -c 'PMID:'` = 24). It is filed in §7 at the
weight it actually carries.

The script, verbatim (read-only; it writes nothing and touches no tracked file):

```python
ref_pmids = re.findall(r"PMID:\s*(\d+)", open(refs_md).read())
art_pmids = re.findall(r"<!--PMID:(\d+)-->", open(art_md).read())
want = set(ref_pmids) | set(art_pmids)
# scan every research/**/*.json outside research/autonomy for {pmid|id} in want with a non-empty title
```

---

## 5 · Does this need trimcrae? **No.**

The seat prompt asks for a clear answer and a drafted question if one is owed. **None is owed.**

- §3's outward-facing trigger fires on *publishing a new version, editing a Zenodo record, issuing a
  public correction*. All three presuppose that something published is wrong.
- **Nothing published is wrong.** AUT-PD-083's wording never reached a published version; AUT-PD-084's
  two attributions are each correct against verbatim quotes that ship in the same deposit; the empty
  citation record is closed.
- The only in-repo work either row leaves is a manuscript-side provenance sentence (§3's residual) and
  a guard (§7) — both are ours under §3's *"a gate you could resolve is never an escalation."*

⛔ **The one thing that would need him, and is NOT in scope here:** re-depositing to Zenodo or
amending a DOI record. Both rows' own `requires_trimcrae_why` already scopes that out, and PUB-ASO is
additionally excluded by name from the standing aiXiv grant (`scope.excluded_papers` in
`publication-authority.json`). **Prepared nothing to post; posted nothing; there is nothing to post.**

---

## 6 · Blast radius

**Which manuscripts cite the deposit:** two, plus supporting documents.

| document | cites | affected by either defect? |
|---|---|---|
| `fusion-junction-aso-research-article.md` | `10.5281/zenodo.22229096` (lines 2601, 2756) | **No** |
| `fusion-junction-aso-journal-article.md` | `10.5281/zenodo.22229096` (line 411) | **No** — see below |
| `fusion-junction-aso-cover-letter.md` | `22180100`, `22166420` | No |
| `fusion-junction-aso-preprint-checklist.md`, `-submission-plan.md` | version DOIs | No |

**Does any sentence depend on the defective content? No, in both directions:**

- **AUT-PD-083.** The journal article's controls paragraph reads *"drawn and then put through the same
  mature-parent screen the reagent passed … Clearing the screen is not a claim of inertness; it is the
  property a negative control has to have."* That is the **corrected** direction, and it was correct
  throughout — the row itself concedes *"The manuscript sentence resting on it is CORRECT."* Confirmed
  at HEAD, line 304–308.
- **AUT-PD-084.** No manuscript sentence cites `35664704` at all, so nothing in either paper rests on
  the attribution the row disputes. The article's `24981949` citations (lines 88, 219) are supported
  verbatim by `lit-targets-aso-gap-length.json`, which is in the deposit.

⛔ **A guard gap, found while looking:** `grep -rn "35664704\|24981949" research/*/tests/*.py` returns
**nothing**, and no test pins the direction of `⛔_not_a_claim_of_inertness`. The field that was
inverted for six days, and the attribution these two rows are about, are both **unguarded**. That is
the CLAUDE.md §6 caveat-to-overclaim inversion shape sitting in an artifact where `lint_claims`
cannot reach it. Filed in §7.

---

## 7 · Ledger rows the driver should write

⛔ I may not write these. Proposed `what` / `kind` / `state`, in priority order.

1. **`AUT-PD-083` → `state: done`, no score.** Add to `what`: *"⛔ REFUTED 2026-09-01 by seat
   S33-DEPOSIT at `b6397c5666ef`. Two independent refutations. (a) The wording was corrected
   2026-08-30 in `65eccd59f842` (round 22) and reads CLEARS at both the published revision
   `866594627ab0` and the pending-draft revision `850edb3358ba`. (b) ⭐ THE ROW'S LOAD-BEARING CLAIM
   — 'both fields ship in the released deposit' — WAS FALSE WHEN FILED: `aso-control-oligos.json`
   is absent from the manifest of `22061075` (482 files) and of `22166420` (483 files, manifest digest
   `1ddbb1e8a036…` byte-matching `deposit-state.json`), and enters the deposit only at `22180100`, as
   one of exactly two files added over `22166420`, at a revision where the field already read CLEARS.
   No Zenodo version has ever carried the inverted sentence."*
2. **`AUT-PD-084` → `state: done`, no score.** Add to `what`: *"⛔ PREMISE REFUTED 2026-09-01 by seat
   S33-DEPOSIT. Not one fact with two sources: two different reported quantities sharing the numerals
   7 and 10, each verbatim-anchored in `lit-targets-aso-gap-length.json` (itself one of the deposit's
   515 files). PMID 24981949 = 'DNA gap size between 7 and 10 nucleotides is optimal' (gap
   nucleotides, OPTIMAL); PMID 35664704 = 'minimum length of 7 to 10 RNA:DNA hybridized nucleotides'
   (whole-duplex hybrid, MINIMUM). Both attributions are correct; no number is double-credited. The
   second half — the empty citation record for PMID 39912803 — closed 2026-08-31 via
   `lit-targets-aso-instruments.json`; all 24 of the journal article's PMIDs now resolve to a title in
   committed JSON (0 missing, measured), and `claim_audit.py` reports `record_source` with
   `resolved_from_committed_record: true` rather than a blank."*
3. **NEW — `what`: ⛔ THE JOURNAL ARTICLE'S TEN-BASE-PAIR CRITERION IS SIZED, IN THE DEPOSIT'S OWN
   PRODUCING ARTIFACT, BY A PMID THE ARTICLE NEVER CITES.** `aso-parent-gap-pairing.json` derives
   `MIN_DUPLEX_BP = 10` from PMID 35664704's 7-to-10 **hybridised**-nucleotide minimum; the article
   sizes the same criterion at line 88 against PMID 24981949's 7-to-10 **gap**-nucleotide optimum,
   and `grep -c 35664704` on the article and on its 24-entry reference list both return 0. Not a
   contradiction and not a published error — a provenance gap, in the direction that leaves the
   criterion's real source unnamed to a reader of the paper alone. ⭐ THE REMEDY IS ALREADY WRITTEN,
   by round 28's regression seat: add 35664704 to the reference list *and* state that its seven-to-ten
   counts hybridised nucleotides rather than gap nucleotides — the article already draws that unit
   distinction twice, so this is one clause plus one reference, not an argument.
   ⚠ Word-budget: a correction REPLACES; the ASO article is venue-capped (3,803 against 3,819 at
   CYC-0090). `kind`: `process_defect` · `state`: `queued` · `serves`: route `RT-AUTONOMY`,
   publication `PUB-ASO` · `cost_class`: `free`.
4. **NEW — `what`: ⛔ THE TWO ARTIFACT FIELDS THESE ROWS ARE ABOUT ARE PINNED BY NO TEST.**
   `grep -rn "35664704\|24981949" research/manuscripts/tests/*.py research/modalities/tests/*.py`
   returns nothing, and nothing asserts the DIRECTION of
   `aso-control-oligos.json:⛔_not_a_claim_of_inertness` (CLEARS, not FAILS) — the exact field that
   sat inverted for six days and that `lint_claims` structurally cannot read, claim strength being
   orthogonal to claim direction (CLAUDE.md §6). ★ FIX: one test asserting (a) the field says CLEARS
   and the two controls' `control_longest_parent_duplex_through_gap_bp` are below `min_duplex_bp`,
   and (b) `aso-parent-gap-pairing*.json`'s `MIN_DUPLEX_BP` rationale names 35664704 **and** that
   PMID's quote is present in `lit-targets-aso-gap-length.json`. ⚠ Mutation-test both halves on a
   scratch copy. `kind`: `process_defect` · `state`: `queued` · `serves`: route `RT-AUTONOMY`,
   publication `PUB-ASO` · `cost_class`: `free`.
5. **NEW, small — `what`: ⚠ `deposit-state.json`'s SUPERSEDED ENTRY FOR `22061075` DOES NOT MATCH THE
   MANIFEST AT THE REVISION IT NAMES.** Recorded `manifest_digest 989d462e101c…` / `n_files 483`;
   the manifest committed at `091721519a7a` carries `23f3d16ee408…` / 482 files. Every other version
   (`22166420`, `22180100`, `22182180`, pending `22229096`) matches its recorded digest byte-for-byte,
   so this is one entry, not a systematic defect, and it changed no conclusion in S33-DEPOSIT.
   ⚠ Read-only diagnosis: the correct remedy may be to name a different revision, not to retype the
   digest — a superseded entry records an immutable published version and rule 1.2 keeps it verbatim.
   `kind`: `process_defect` · `state`: `queued` · `serves`: route `RT-AUTONOMY`, publication `PUB-ASO`
   · `cost_class`: `free`.
6. **NEW, lowest — `what`: EMIT `fusion-junction-aso-journal-references.json` ALONGSIDE THE MARKDOWN.**
   Carried over from AUT-PD-084's second half as a BUILD REQUEST at its true weight, not a defect: all
   24 PMIDs already resolve, but from seven scattered files, so `claim_audit.py`'s
   `REFERENCE_SOURCES` still has no single list for this manuscript and reports `title: null` for
   `39912803`. `kind`: `proposal` · `state`: `queued` · `cost_class`: `free`.

---

## 8 · What I measured, in order

1. `git rev-parse HEAD` → `b6397c5666efbf7d6755dfaedabc6a4bef24a8ee`.
2. Both ledger rows read in full from `research/autonomy/research-ledger.json`.
3. `deposit-state.json`: published `22182180` @ `866594627ab0`; pending draft `22229096` @
   `850edb3358ba`; three superseded versions.
4. Every version's `archive_content_digest` recomputed from the manifest committed at its own
   `git_revision` and compared to the recorded digest — 4 of 5 match exactly (§1).
5. `git log` on `aso-control-oligos.json` → created `5e24cccf` 2026-08-24, corrected `65eccd59`
   2026-08-30 18:44.
6. The field's text read at `866594627ab0` and `850edb3358ba` → CLEARS at both.
7. Manifest membership of `aso-control-oligos.json` across all four published versions and the draft →
   absent before `22180100`, present from `22180100` on.
8. Set-difference of the `22166420` and `22180100` manifests → the file is one of exactly two additions.
9. `lit-targets-aso-gap-length.json` records[4] and records[0] read at HEAD **and at the published
   revision** → the two verbatim quotes in §3.
10. `grep -c 35664704` on the article and its reference list → 0 and 0.
11. `s33_pmid_title_coverage.py` (does not exist in this repository — source in §4) → 24/24
    reference PMIDs resolve to a committed title; 0 missing.
12. `fusion-junction-aso-claim-audit-verdicts.json` sample[24] → `record_source` present,
    `resolved_from_committed_record: true`.
13. Manuscript sentences that could depend on either defect read at HEAD (article lines 88–90, 219–220,
    304–308).
14. `python3 -m pytest research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py -q`
    → **8 passed in 0.10s** (a read; I did not edit that file or any of the four the prompt fences off).
15. `grep -rn "35664704\|24981949" research/manuscripts/tests/*.py research/modalities/tests/*.py` →
    no output.

## 9 · What I changed

- `research/autonomy/sprint-2026-09-01/S33-DEPOSIT.md` — this file.

**Nothing else.** No tracked file outside my owned path was edited; no git write command was run;
`deposit-state.json`, the archive manifest, `scripts/regenerate_aso_chain.sh`,
`test_the_deposit_the_papers_cite_is_current.py` and the ASO manuscript were **read only**. The one
script I wrote lives in the scratchpad and is read-only by construction.

## 10 · What I could not do, and what it is actually waiting on

- **Adding PMID 35664704 to the journal article's references** (§3 residual, §7 row 3) — waiting on a
  seat that owns the ASO manuscript. Explicitly fenced off by my prompt. Not blocked on anything else:
  the source is committed, quoted verbatim, and in the deposit.
- **Writing the guard** (§7 row 4) — waiting on ownership of `research/modalities/tests/`. Free,
  offline, ready to write.
- **Writing the ledger rows** — waiting on the driver; `research-ledger.json` is unowned this sprint.
- ⛔ **Nothing here is waiting on compute, network, Zenodo, or trimcrae.** Every observation above is a
  $0 read taken tonight from committed state. I made no network call and needed none: both rows'
  questions are answered by manifests and quotes already inside the repository.
