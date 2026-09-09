---
id: DOC-PORTFOLIO-INVESTIGATION-FUSION-OUTPUT-3-COVERAGE-20260909
title: "Platform readability of the pre-registered NR4A3-program sets: GPL6244 settled, GPL3290 undeterminable offline because the EST-accession bridge is not in this checkout"
level: L4
kind: feasibility-determination
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# FUSION-OUTPUT-3 — do the frozen sets clear the readability floors on each platform?

**This is a coverage and feasibility determination. No expression value was read, no contrast was
computed, and no biological claim is made anywhere in this lane.** The executable outcome protocol
remains a coordinator-owned frozen gate; nothing here opens it, pre-empts it or confers authority to
run anything.

## 1 · The question

FUSION-OUTPUT-2 froze six gene sets (contrast A and contrast B at the 1000 / 2000 / 5000 bp promoter
windows) and declared, as prerequisite §6.1 and stop condition **S2**, that a set may be scored on a
platform only if it clears **both** of the manuscript's own floors: **coverage ≥ 0.4** and **≥ 4
readable genes**. It recorded GPL6244 as covered by construction and GPL3290 as *"unknown offline"*.

For each of the six cells and each of the two platforms: **how many members are actually readable, and
does the cell clear both floors?**

## 2 · Merit

The pre-registration's own S2 is the only prerequisite standing between it and a scoring run whose
cohort — GSE4303 — is graded circular and is the weaker-powered of the two. If GPL3290 cannot in fact
read the sets, the design collapses to a single-cohort test on GSE24369, and the pre-registration's
own §3.1 rule ("a result carried by GSE4303 alone is uninterpretable") is not the binding constraint
— the reverse is. Settling readability costs nothing, spends no gated run, and either removes a
declared unknown or converts it into a named dependency. It is directly patient-relevant only in the
indirect sense that it protects a scarce EMC-tumour dataset from being spent on an unreadable test.

## 3 · The evidence gap, and what distinguishes it

The pre-registration named the gap precisely: GPL3290 probes carry **EST accessions only**, so the
read depends on an accession→symbol bridge that resolves roughly **14,9xx** symbols. The gap is not
"we have not looked" — it is "does the bridge artifact exist offline". It differs from the completed
membership lane, which worked entirely inside the GPL6244 ∩ TPM universe and never needed GPL3290.

**Answer: the bridge artifact does not exist in this checkout.** The bridge is *constructed at run
time* by `_gpl_symbols()` in `research/modalities/emc_atr_vulnerability.py` (lines 1446–1516), which
fetches, in order, GEO `acc.cgi?acc=GPL3290&targ=self&form=text&view=full`, then
`GPL3290.annot.gz`, then `GPL3290_family.soft.gz`, and then resolves GenBank/EST accessions to
symbols. **Where I looked, all of it offline and none of it fetched:**

* `research/modalities/` — every `*.json` and `*.py`; the only GPL3290 material is *derived per-gene
  readability* from earlier committed runs, never the platform table.
* `research/manuscripts/` — the 14,932 figure appears only as prose in the MTAP/PRMT5 manuscript and
  its reviews; no symbol list accompanies it.
* `systems/` — nothing.
* the frozen corpus `/tmp/claude-0/frozen-corpus/extracted/corpus/` (244 MB, all of it) — the
  coordinator packet `research/autonomy/nr4a3-program-source-2026-09-07/sources/` holds
  **`GPL6244-gene-to-probes.json` and nothing for GPL3290**.
* a filesystem-wide search for `*GPL3290*`, `*.soft*`, `*.annot*` and `*series_matrix*` — the only
  SOFT files present belong to GSE11185 and GSE6481, unrelated series.

**No network access was attempted.** That the artifact is missing is itself part of the finding.

## 4 · The step taken

`platform_coverage.py` (stdlib only, deterministic, no network) reads the frozen sets and grades every
cell on both platforms, and writes `platform-coverage.json`.

* **GPL6244 — EXACT.** Membership in the frozen source packet's own symbol→probe map (21,407
  symbols), the same file that packet's `array_coverage.py` used.
* **GPL3290 — BOUNDED.** Every offline record of a symbol's GPL3290 readability written by an earlier
  committed run of the bridge is harvested (3,014 distinct symbols: 3,000 from the seeded background
  draw plus the biology-selected panels). A member is *known readable*, *known unreadable*, or
  *unknown*. Coverage is then an interval — lower bound assumes every unknown is unreadable, upper
  bound assumes every unknown is readable — and a cell is called only when the interval lies wholly
  on one side of a floor.

**No floor was lowered, softened or reinterpreted.** 0.4 and 4 are used exactly as the manuscript and
the pre-registration state them. An interval that straddles a floor is reported as undetermined.

## 5 · Result — plainly, cell by cell

### GPL6244 (GSE24369), exact

| window | contrast | n | readable | coverage | verdict |
|---|---|---:|---:|---:|---|
| 1000 | A | 23 | 23 | 1.000 | **PASSES BOTH FLOORS** |
| 1000 | B | 4 | 4 | 1.000 | **PASSES BOTH FLOORS** |
| 2000 | A | 40 | 40 | 1.000 | **PASSES BOTH FLOORS** |
| 2000 | B | 7 | 7 | 1.000 | **PASSES BOTH FLOORS** |
| 5000 | A | 57 | 57 | 1.000 | **PASSES BOTH FLOORS** |
| 5000 | B | 6 | 6 | 1.000 | **PASSES BOTH FLOORS** |

This **confirms** the pre-registration's "coverage 1 by construction" claim rather than assuming it:
all 6/6 cells verified against the map itself, zero members missing. Note that at 1000/B coverage 1.0
means exactly 4 readable genes — the set sits *on* the 4-gene floor with **zero dropout tolerance**,
as the pre-registration already stated.

### GPL3290 (GSE4303), bounded

| window | contrast | n | known readable | known unreadable | unknown | coverage interval | verdict |
|---|---|---:|---:|---:|---:|---|---|
| 1000 | A | 23 | 7 | 0 | 16 | [0.304, 1.000] | **UNDETERMINABLE OFFLINE** |
| 1000 | B | 4 | 0 | 0 | 4 | [0.000, 1.000] | **UNDETERMINABLE OFFLINE** |
| 2000 | A | 40 | 10 | 0 | 30 | [0.250, 1.000] | **UNDETERMINABLE OFFLINE** |
| 2000 | B | 7 | 1 | 0 | 6 | [0.143, 1.000] | **UNDETERMINABLE OFFLINE** |
| 5000 | A | 57 | 17 | 0 | 40 | [0.298, 1.000] | **UNDETERMINABLE OFFLINE** |
| 5000 | B | 6 | 1 | 0 | 5 | [0.167, 1.000] | **UNDETERMINABLE OFFLINE** |

**The two floors separate, and one of them is settled for contrast A.** The 4-readable-gene floor is
cleared by *named positive evidence alone*, whatever the unknowns turn out to be:

* **1000/A — 4-gene floor MET**, settled: *CENPI, OAS1, RNF130, SEMG2, SH3D19, SLC2A13, TMEM67* (7).
* **2000/A — 4-gene floor MET**, settled: *CDC14A, CENPI, OAS1, PIKFYVE, RNF130, RNF220, SEMG2,
  SLC2A13, ST3GAL6, TMEM67* (10).
* **5000/A — 4-gene floor MET**, settled: *ANKRA2, AXIN1, CDC14A, CENPI, CPNE3, FBXO38, NDUFAF4,
  NUP210L, OAS1, PIKFYVE, PPTC7, RARRES1, RNF220, RPN2, SEMG2, ST3GAL6, TMEM67* (17).
* **1000/B, 2000/B, 5000/B — 4-gene floor UNSETTLED.** Only *PIKFYVE* (2000/B, 5000/B) has any
  offline GPL3290 record at all; 1000/B has none. **The genes whose GPL3290 readability is unknown
  and on which contrast B entirely depends are: *BAZ2A, FAXC, FBXO21, FOXA1, HAP1, IDH1, TBX21*.**
  Four of these — *FAXC, FOXA1, HAP1, TBX21* — are the whole of the 1000/B set, so **one single
  unresolved symbol there is the difference between a set and no set.**

The **0.4 coverage floor is UNSETTLED for all six cells**: no member of any set is on record as
*unreadable*, so no upper bound falls below 0.4, and the lower bounds (0.14–0.30) are below it.

**Not a single gene in any of the six sets is known to be unreadable on GPL3290.** The failure mode
is missing information, not observed absence.

### A separate estimate that does not change any verdict

The 3,000-symbol background draw is a *seeded uniform random* sample of the 14,928-symbol GPL3290
frame, so a gene in the frame appears in it with p = 0.2010. Under H₀ "this set's frame coverage is
exactly the 0.4 floor", the exact binomial one-sided tail is:

| cell | k observed | expected k at coverage 0.4 | p vs H₀ |
|---|---:|---:|---:|
| 1000/A | 6 | 1.77 | 0.0065 |
| 2000/A | 9 | 3.14 | 0.0032 |
| 5000/A | 17 | 4.58 | <0.0001 |
| 1000/B | 0 | 0.32 | 1.00 |
| 2000/B | 1 | 0.56 | 0.44 |
| 5000/B | 1 | 0.48 | 0.40 |

Contrast A's three cells are **inconsistent with sitting at the 0.4 floor** and their point estimates
of frame coverage are at the 1.0 cap. **This is a sampling-hypothesis test, not a coverage
measurement.** It does not settle S2, does not open the gate, and I do not report contrast A as
passing. Contrast B's three cells carry essentially no information either way — with 4–7 genes and a
20% sampling rate, the draw could not have distinguished full coverage from none.

## 6 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `platform-coverage.json`; generator `platform_coverage.py`; execution evidence in
`checks/01`–`checks/04`, including the silently-wrong first attempt (exit 0, all three GPL3290
evidence paths resolved to non-existent files because `REPO` was `HERE.parents[4]`), preserved with
its output and a note.

**Validation.** The GPL6244 arm is a positive control with a known answer: the sets were built inside
the GPL6244 ∩ TPM universe, so coverage must be 1.000 in all six cells, and it is — a discrepancy
would have indicted the harvester. The GPL3290 arm is internally consistent (readable + unreadable +
unknown = n in every cell) and no symbol carried conflicting records.

**Provenance** (exact path · sha256, all recorded in the artifact's `inputs`):

| input | sha256 |
|---|---|
| `.../FUSION-OUTPUT-2/fusion-program-testsets.json` | `e1add70fc53fcc06…` |
| `/tmp/claude-0/frozen-corpus/extracted/corpus/research/autonomy/nr4a3-program-source-2026-09-07/sources/GPL6244-gene-to-probes.json` | `00754d6d3e43f83b…` |
| `research/modalities/emc-expression-panels.json` | `59bccb553148c710…` |
| `research/modalities/nr4a3-fusion-targets.json` | `0c338c169678f475…` |
| `research/modalities/census-route-expression-grading.json` | `2dbd21cc811c150c…` |

Full 64-character digests are in `platform-coverage.json#inputs`.

**Limitations.** The GPL3290 determination is bounded, not exact, and cannot become exact without the
platform table. The evidence base is 3,014 of ~14,928 frame symbols, so absence of a record is
uninformative about a single gene. The binomial estimate assumes the seeded draw is uniform over the
frame and independent of promoter accessibility; if the bridge's symbol resolution is itself biased
toward well-annotated genes, our accessibility-selected genes are not exchangeable with the frame and
the estimate is optimistic. Symbols were matched case-insensitively and exactly — **no alias or
previous-symbol resolution was attempted**, so a gene the old cDNA array annotates under a superseded
spelling would be scored unknown here even if the bridge would find it. Coverage is not
interpretability: GSE4303 remains graded circular and two-colour, and clearing a floor would not
change that.

**Stop condition — reached.** The question is answered as far as offline evidence permits, and the
remaining half is a single named missing artifact, not an open-ended search. I stopped rather than
attempt any network retrieval.

## 7 · What this means for the pre-registration's S2, and the next credible step

S2 ("GPL3290 coverage or readable-member count fails a floor → that platform is dropped") **cannot be
evaluated offline for any of the six cells.** It is not satisfied and it is not violated; it is
pending on one artifact.

**The concrete dependency, named exactly:** the GPL3290 platform probe table with its accession
column — GEO `acc.cgi?acc=GPL3290&targ=self&form=text&view=full`, or
`ftp.ncbi.nlm.nih.gov/geo/platforms/GPL3nnn/GPL3290/soft/GPL3290_family.soft.gz` — plus the
accession→symbol resolution step `_gpl_symbols()` already implements. Retrieving it is a networked
step this lane is fenced from and does not attempt; it is for the coordinator to schedule through the
ordinary permitted route, if the frozen gate is ever opened. **The one-line deliverable such a run
should emit and commit is the list of bridged symbols itself** — its absence is why this question was
open at all, and committing it would close it permanently for every future lane.

Until then, and independently of it, one thing is already settled and worth carrying forward: **on
GSE24369/GPL6244 all six cells clear both floors exactly**, so the design's better-powered arm is
readable in full, and **contrast B's dependence on seven specific symbols — *BAZ2A, FAXC, FBXO21,
FOXA1, HAP1, IDH1, TBX21* — is now named**, which sharpens rather than softens the
pre-registration's own §4.3 recommendation not to run contrast B.
