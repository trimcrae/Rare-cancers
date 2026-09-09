---
id: DOC-PORTFOLIO-EXPOSURE-INDEX-FINDING
title: "EXPOSURE-INDEX — the portfolio's EMC-patient exposure index, with a retrieval-completeness column"
level: L4
kind: evidence-index
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# EXPOSURE-INDEX — FINDING

Lane: `…/PORTFOLIO-INVESTIGATIONS-2026-09-08/EXPOSURE-INDEX/`.
Executes **P10 (rank 10)** of `../FOLLOWTHROUGH-DISCOVERY/PROPOSALS.md`, as specified.

⛔ **This is a provenance index, not evidence synthesis.** Nothing here asserts or implies efficacy,
safety, selectivity, a therapeutic window, prognosis or any treatment recommendation, and nothing
here is patient-specific advice. No wet lab. Counting who has been counted is not a statement about
what happened to them.

## 1 · Question

**How many distinct EMC patients does this portfolio's cited evidence actually rest on, and how much
of that is UNREAD rather than absent?**

## 2 · Merit

*Patient relevance.* This portfolio's manuscripts describe a disease whose entire published clinical
record is a few hundred patients spread across overlapping registries, referral-centre series and
mixed-histology trials. Whether a claim rests on 200 patients or on 40 seen four times is the
difference between a defensible statement and an accidental one, and no artifact in the repository
recorded it.

*Non-trivial contribution.* The index separates three things the portfolio had been conflating: a
series' **headline denominator**, its **EMC denominator**, and whether the paper that would settle
either was **actually read**. Two independent lanes had already arrived at the second and third
separately — CARE-DELIVERY-3 invented `retrieval_completeness` for its coverage rows; REPURPOSING-3
established unread-is-not-absent for references [8] and [14]. This unifies them on one row schema.

*Attainable evidence.* Entirely from files already in the repository. **No retrieval was performed by
this lane** — no PubMed/PMC call, no HTTP request. Every figure is copied from a named file, and the
retrieval attribution stays with the lane that made the call.

## 3 · The evidence gap this closes, and the one it does not

**Closed.** Nobody had asked, across the portfolio, *which* patients the citations rest on. Series
were curated per-paper (`emc-ipd-survival.json`), per-element (CARE-DELIVERY-2/3), per-contrast
(LOCOREGIONAL-2) and per-reference (REPURPOSING-2/3) — never on one axis, and never with the
unread/absent distinction carried through.

**Not closed, and deliberately.** The *first* half of the question — the distinct-patient count —
is **not answerable and is not answered**. See §6.

## 4 · Step taken

Built `emc-patient-exposure-index.json`: **28 rows**, one per cited series, each carrying
`identifier`, `n_headline_as_reported`, `n_emc_patients_as_reported`, `n_emc_status`,
`citing_papers`, `retrieval_completeness ∈ {complete, partial, unread}`, and `overlap_unknown` —
every one of those with a **verbatim quote and a named file-plus-pointer it was quoted from**.

Rows: the 17 EMC clinical series carried by `research/modalities/emc-ipd-survival.json` (the source
CARE-DELIVERY-2/3 and IPD-SURVIVAL-2 both work from), plus the 11 cited references of the repurposing
manuscript that are not among them.

### What the index shows

| | count of **rows** (never of patients) |
|---|---|
| rows | **28** |
| `retrieval_completeness = unread` | **18** |
| `= partial` | 7 |
| `= complete` | **3** |
| EMC denominator **reported** | 9 |
| EMC denominator **UNKNOWN** | **19** |
| `overlap_unknown = true` | **24** |
| `overlap_unknown = false` | 4 |
| headline n **demonstrated not to be** the EMC n | 3 |
| headline-vs-EMC relation **unknown** | 20 |

**The answer to the half that is answerable: most of it is unread, not absent.** Eighteen of
twenty-eight rows have no retrievable body text of any kind; nineteen have no known EMC denominator.
Only **three** series in this entire portfolio have been read narrative-plus-all-tables:
`martinbroto2020immunosarc1`, `stacchiotti2013anthracycline` and `osullivanCoyne2022`.

**Carried forward from CARE-DELIVERY-3, and extended.** A series' headline n is frequently not its
EMC n, and the index now records both wherever both are known:

* `martinbroto2020immunosarc1` — headline **68**, EMC **4** (*"4 patients have EMC (Table 1,
  'Diagnosis (central)')"*).
* `morioka2016trabectedin` — headline **5**, EMC **2** (*"2 have EMC, 3 have mesenchymal
  chondrosarcoma"*).
* `osullivanCoyne2022` — headline **55 enrolled / 54 evaluable**, EMC **3** (*"Extraskeletal myxoid
  chondrosarcoma  3"*, Table 1). **A third instance of the same shape, found by this lane**, in the
  reference whose EMC content produced the cabozantinib falsification.
* `stacchiotti2013anthracycline` — headline **11**, EMC **11**; the pure denominator.

For the other 20 rows the relation is **UNKNOWN**, because the table that would state it was not
returned.

### The rows the index exists to protect

* `maki2005bortezomib` ([21]) — no PMCID, MeSH no finer than "Sarcoma". n is **UNKNOWN, never zero**.
* `boklan2025carfilzomib` ([22]) — full text retrieved, narrative names no EMC patient, **but** *"the
  per-histology enrolment table is not carried in the retrievable full text"*. `n_emc` = **UNKNOWN**,
  not 0. This is the clearest unread-not-absent row in the portfolio.
* `giner2023` ([8]) and `iwata2025` ([14]) — REPURPOSING-3's originating cases. EMC n known from the
  abstract (**31**, **1**); everything below the abstract unread.
* `higuchi2023zaltoprofen` ([12]) — the **only 0** in the index, and it is a **measured** zero
  (*"No human patient of any kind. Preclinical throughout."*), not an untraced one.
* `chow2007` ([9]) — recorded 0 in the first build and **corrected to UNKNOWN** when the verifier
  refused it: a review's body being unread is not evidence that it carries no primary cohort. The
  failed build is preserved at `checks/02-verify-index`, exit 1.

## 5 · Validation — the control reproduces

`checks/04`, exit **0**. Re-derived **from the index rows** by a verifier that reads only the emitted
JSON and LOCOREGIONAL-2's ledger:

* `bishop2019`: 33 + 8 = **41** patients, 1 + 4 = **5** events.
* `masunaga2025`: 24 + 110 = **134** patients, 2 + 14 = **16** events.
* **175 patients, 21 local recurrences — matches LOCOREGIONAL-2 exactly.** ✅

⚠ **It only reproduces because the index stores the contrast subset separately from the headline
denominator.** `masunaga2025`'s headline is **171**; the two-series contrast rests on **134**. An
index that had stored only headline n would have produced 41 + 171 = 212 and failed this control.
That is the control earning its place.

⛔ **Why this one addition is permitted where the index forbids totals.** It sums exactly two rows a
named source file rules non-overlapping *for this contrast* (`POLICY-evidence.md` 2.3, quoted in the
artifact with its binding restriction). It is a control on the index, and it is the **only** addition
performed anywhere in the artifact.

The verifier also enforces, mechanically: every non-null n names a source file; no zero without a
measured-zero justification; `retrieval_completeness` three-valued on every row; `overlap_unknown`
present on every row; and no total-shaped key anywhere in the file.

## 6 · ⛔ Stop condition — reached, and the total is refused

**Stop at the index.** No pooling. **No denominator arithmetic across any rows carrying
`overlap_unknown`** — and 24 of 28 rows carry it.

**No portfolio-wide patient total is computed here, not even as an aside or an approximate upper
bound.** Such a total would be wrong in **two directions at once**: the series overlap (the Milan
cluster, the US institutional/SEER cluster, the Japanese registry/trial cluster), *and* at least two
denominators are not EMC at all. The artifact refuses total-shaped keys by test.

The honest statement of the first half is therefore: **the distinct-EMC-patient count on which this
portfolio's cited evidence rests is UNKNOWN, and this index says precisely why** — 24 rows whose
independence is unestablished and 20 whose EMC denominator is unread.

## 7 · Provenance

* **No new retrieval.** No PubMed/PMC call, no HTTP request, no download. Routes B1/B2/B4/B8/B9
  untouched; R1–R4 not restarted.
* Eight input files recorded with **sha256** in `_reads_only`. All read-only; no file outside this
  lane was written, and nothing was staged, committed or pushed.
* Sources: `research/modalities/emc-ipd-survival.json`;
  `../CARE-DELIVERY-3/care-delivery-element-coverage-v3.json`;
  `../CARE-DELIVERY-2/care-delivery-element-coverage-v2.json`;
  `../LOCOREGIONAL-2/rt-local-control-contrast-ledger-k2.json`;
  `../REPURPOSING-2/CITED-REFERENCE-SWEEP.md`; `../REPURPOSING-3/FIVE-REFERENCE-TABLE.md`;
  `../PUB-REPURPOSING/EVIDENCE-cabozantinib-emc.md`;
  `research/manuscripts/repurposing/repurposing-hypotheses.md`.
* Primary-text figures were retrieved from **PubMed / PubMed Central** by the lanes named in each
  row's `retrieval_completeness_quoted_from`, on 2026-09-09. Attribution stays with them.

## 8 · Limitations

1. **This index is one level of indirection from the papers.** For the 17 clinical series the
   headline n is a **curated field** in a repository artifact, not a figure re-quoted from the
   primary; every row says so in `n_headline_provenance_depth`. Two rows (`huang2023`,
   `masunaga2025`) additionally carry a verbatim primary quote.
2. **`overlap_unknown` is a statement about the source files, not about the patients.** It is `false`
   on only 4 rows, and only where a named file says so in words. Absence of a recorded overlap is
   recorded as unknown, not as independence.
3. **`retrieval_completeness = unread` is a statement about *this program's* reach**, not about the
   papers. Several are readable by a human in a browser (`seer270_2022` is the standing example).
4. **`complete` means what CARE-DELIVERY-3 meant by it** — narrative plus all tables — and still
   excludes supplementary appendices and figure images.
5. `bishop2019`'s split is inherited transcription, *"NOT re-verified against the paper in this
   lane"*, and the index records it as `unread` for that reason even though its numbers are used in
   the control. The control therefore tests the index's arithmetic and storage, not that transcript.
6. **The index cannot detect overlap it was not told about.** It flags unknown independence; it does
   not resolve any.
7. Nothing here changes any pool flag, guard, gate, matcher, pin or test, and no shared file was
   modified. No unapplied diff was needed — this lane adds an artifact and alters nothing shared.

## 9 · Next credible independent step (not taken here)

Resolving `overlap_unknown` for the **Milan cluster** (`stacchiotti2013anthracycline`,
`stacchiotti2014sunitinib`, `stacchiotti2019pazopanib`, `chiusole2020`) would collapse four rows
into a stated relation and is the single highest-yield unknown in the file. It requires reading
per-patient tables that are `unread` by the permitted route today; it is **not** a task this lane
opens.

## 10 · Files

* `emc-patient-exposure-index.json` — the artifact.
* `build_exposure_index.py`, `verify_index.py`.
* `checks/01-build-exposure-index` (0) · `checks/02-verify-index` (**1**, preserved — the chow2007
  defect) · `checks/03-rebuild-after-chow2007-fix` (0) · `checks/04-verify-index-rerun` (0).
