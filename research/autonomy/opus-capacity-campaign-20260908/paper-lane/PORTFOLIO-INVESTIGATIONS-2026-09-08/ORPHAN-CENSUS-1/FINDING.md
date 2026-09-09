---
id: DOC-ORPHAN-CENSUS-1-FINDING
title: "ORPHAN-CENSUS-1 — is EWSR1::NR4A3's orphan status real, or a retrieval artefact?"
level: L4
kind: investigation-finding
status: complete
date: 2026-09-08
lane: ORPHAN-CENSUS-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# ORPHAN-CENSUS-1 — EWSR1::NR4A3's "orphan" status, benchmarked against 197 other fusions

## 1 · The question

In `research/modalities/fusion-junction-orphan-census.json` — 198 fusion pairs already fetched from
Europe PMC on 2026-08-13, never used by any lane — **where does EWSR1::NR4A3 actually sit, and does
its position survive stratification by gene-symbol length**, the confounder the file's own
`⚠_short_symbols_stay_noisy` caveat names?

## 2 · Merit

The portfolio contains at least one load-bearing novelty claim built on this fusion being untouched
(§6). If the fusion is genuinely under-served, that is a real fact about the field and the claim
stands with its bound. If its apparent neglect is an artefact of how short gene symbols retrieve,
every argument leaning on it inherits the artefact. Either answer changes what this portfolio may
assert, at zero cost, from rows already paid for.

## 3 · The evidence gap this closes

DISCOVERY-2 fetched the census and **computed no hashes and no cross-pair comparison**. The file
reports per-row verdicts and a global verdict tally, but never asks the comparative question: is any
one fusion's verdict distinguishable from the retrieval behaviour of its symbols? Nothing downstream
had re-read it. The inputs are that one file's 198 rows and their stored hit counts — no new query.

## 4 · Step taken

`build_benchmark.py` re-hashes the census at use, recomputes coverage across all 198 pairs, ranks
EWSR1::NR4A3 on four retrieval metrics both universe-wide and within a like-with-like comparator
(fully screened pairs whose **both** symbols are ≥4 characters), and stratifies orphan rate by
symbol length. `verify_benchmark.py` re-checks the artifact and carries a negative-control mode.

**⛔ No network call of any kind was made. Every count is re-read from rows fetched on 2026-08-13.**

### 4.1 Positive controls — PASS

| control | verdict | denominator | modality | junction-directed |
|---|---|---|---|---|
| BCR::ABL1 | attempted (non-orphan) | 11891 | 1828 | 863 |
| EWSR1::FLI1 | attempted (non-orphan) | 1599 | 386 | 250 |
| PAX3::FOXO1 | attempted (non-orphan) | 1355 | 460 | 231 |

All three come back non-orphan, so the instrument is not simply failing to retrieve. Check 04 proves
the control assertion can fail: forcing EWSR1::FLI1 to `orphan` exits 1.

### 4.2 The benchmark table

Universe: 198 pairs; 175 fully screened (every query HTTP 200 with a count), 23 not — the 23
`screen_failed` rows are Europe PMC 502s on one query, not evidence about those fusions.

| stratum (min symbol length) | pairs | fully screened | orphan | **orphan rate** | median denominator | median junction-directed |
|---|---|---|---|---|---|---|
| **≤3 chars** (ACT, BCR, WT1, ERG …) | 50 | 44 | 3 | **6.8 %** | 215.0 | 17.5 |
| **≥4 chars** | 148 | 131 | 30 | **22.9 %** | 66 | 5 |

**The caveat's direction is confirmed and it runs the way that matters here.** Short symbols are
*less* likely to be called orphan — 6.8 % vs 22.9 % — because an English-word symbol collects
unrelated records and suppresses the orphan call. Symbol length inflates apparent attention; it does
not manufacture neglect. Pooling the two strata would understate the orphan rate for ordinary
symbols by more than a factor of three.

### 4.3 Where EWSR1::NR4A3 sits

**It is not an orphan in this census.** Verdict `attempted`; both symbols ≥4 characters, so it sits
in the clean stratum and its position is not a short-symbol artefact in either direction.

| metric | value | rank of 198 (all) | rank of 131 (≥4-char, fully screened) | comparator median |
|---|---|---|---|---|
| denominator hits | 207 | 59 / 176 | **37 / 131** | 66 |
| modality hits | 23 | 64 / 176 | **42 / 131** | 7 |
| junction-directed hits | 19 | 56 / 176 | **35 / 131** | 5 |
| junction share of own literature | 0.092 | 64 / 171 | **44 / 128** | 0.077 |

Against the fusions it is most comparable to, EWSR1::NR4A3 is in the **upper third on every metric**
and above the median on all four, including the retrieval-normalised share. Among the twelve
EWSR1-family pairs in the universe it is mid-pack: below EWSR1::FLI1 (250), EWSR1::ERG (73),
EWSR1::WT1 (64) and EWSR1::ATF1 (53); above EWSR1::CREB1 (18), EWSR1::DDIT3 (13), EWSR1::PATZ1 (11),
EWSR1::CREB3L1 (10), EWSR1::TFCP2 (4), EWSR1::KLF15 (2).

## 5 · The answer

**The "orphan" framing is not supported by the one fetched index we can check it against.** Under
the census's own operationalisation EWSR1::NR4A3 is `attempted`, not `orphan`, and its coverage sits
above the median of comparable fusions. That is the second of the two outcomes the lane was set up
to distinguish, and it is the more consequential one.

⛔ **What this does NOT establish.** The `attempted` verdict is keyword **co-occurrence within one
retrieved record** — modality terms and junction terms appearing alongside both gene symbols. It is
**not** a read confirmation that anyone aimed an oligonucleotide at the EWSR1::NR4A3 junction. So
this benchmark refutes *under-retrieval*, and is silent on *whether the experiment was done*. The 19
junction-directed identifiers are stored in the artifact precisely so a human can settle that by
reading them.

## 6 · Portfolio arguments that lean on the fusion being neglected

1. **`research/manuscripts/aso/aso-citations-priorart-2026-08-08.md:371`** — *"EMC / EWSR1::NR4A3 has
   never been attempted. No junction-directed oligonucleotide against any NR4A3 fusion appears in
   5,385 records. Genuinely first — an indication-level first."* This is the load-bearing one: it is
   the ASO paper's stated novelty. **QUALIFIED, not refuted.** A second, independently fetched index
   returns 19 junction-directed records for this pair — above the comparator median — so a flat
   "never been attempted" now rests on one sweep's negative where another sweep is not empty. The
   honest form carries the sweep's bound and, ideally, a hand-read of the 19 identifiers.
2. **`research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md:87`** — *"for which no targeted
   agent exists."* **Not reached** by this benchmark: an agent-availability claim, not a
   literature-coverage one. Recorded because that paper's own peer review (item 36, 2026-08-10)
   already asked for the phrase to be bounded.
3. **`research/manuscripts/dependency/emc-biomarker-selected-classes.md:46`** — *"It has no targeted
   agent, and its systemic options are few."* **Not reached**, same reason.

The scan was a grep over `research/manuscripts` for neglect-shaped phrasings tied to this fusion or
this modality, excluding the unrelated senses "orphan nuclear receptor" and "orphan disease". It is
**not** an exhaustive portfolio audit.

## 7 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `junction-modality-coverage-benchmark.json` (24,662 B) in this directory, plus
  `build_benchmark.py` and `verify_benchmark.py`.
* **Validation** — `checks/01`–`04`. Check 03 verifies the recorded source hash still matches disk,
  the three controls are non-orphan, the recomputed verdict counts reconcile **exactly** with the
  census's own published summary (`attempted` 139 / `orphan` 33 / `modality_touched` 3 /
  `screen_failed` 23), and the two strata partition all 198 pairs. Check 04 is the negative control
  and **exits 1** as required.
* **Provenance** — `research/modalities/fusion-junction-orphan-census.json`, 705,801 B, sha256
  `5793da5db4914c2917bea20ae522124a682e9ee3f0c62023372635cc6b4dc01a`, computed here at use because
  DISCOVERY-2 recorded none. Census `_utc` 2026-08-13T20:44:47Z, status `ok`, universe from CIViC.
* **Limitations** — (i) **One index, one date, one query string.** An unclosed literature index
  cannot establish a field-wide absence; PUB-TCIP's precedent binds, and nothing here says "the field
  has not done X". Every number is a rank or a coverage count. (ii) Verdicts are co-occurrence, not
  read (§5). (iii) 23 pairs are incompletely screened on a 502 and are excluded from rates, not
  counted as anything. (iv) The universe is CIViC-derived and therefore skewed toward clinically
  annotated, mostly kinase-druggable fusions — the comparator is "fusions CIViC records", not "all
  fusions". (v) Symbol length is a proxy for retrieval noise, not a measurement of it. (vi) Nothing
  here bears on EMC efficacy, safety, selectivity, therapeutic window or clinical readiness.
* **Stop condition** — **stopped at the benchmark table**, as scoped. No re-query, no new fetch, no
  edit to any manuscript. The next credible independent step is a **hand read of the 19 stored
  junction-directed identifiers** for EWSR1::NR4A3, which is the only thing that can convert a
  co-occurrence count into a statement about whether the experiment was attempted — and that is the
  step the ASO paper's novelty sentence actually depends on.
