---
id: DOC-CISTROME-MOTIF-1-FINDING
title: "Does the NBRE motif scan predict measured NR4A occupancy? — a benchmark, and it FAILS"
level: L4
kind: finding
status: live
date: 2026-09-08
lane: CISTROME-MOTIF-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# CISTROME-MOTIF-1 — motif score against measured occupancy

## The question

Several arguments in this repository use an NBRE motif scan as a stand-in for NR4A occupancy.
**Does the motif score actually predict measured promoter-window peak presence?** One pass, one
panel, pre-specified statistics, no transformation search.

## Merit

Patient relevance is indirect but real: every EMC target-gene and response-element-degrader
argument that runs from *sequence* to *the fusion reads this gene* depends on the substitution
holding. Nobody in this repository had tested it against the occupancy measurements the repository
already owns. The contribution is non-trivial because it is a **falsification test of an inferential
step**, not another prediction; and it is attainable entirely from committed inputs, offline.

## Boundary against the sibling lane (CISTROME-1)

CISTROME-1 asks *is this locus occupied more than a background null?* — its unit is
**occupancy-versus-background per locus**. This lane asks *does the sequence predictor rank the
measured outcome?* — its unit is **motif-score-versus-measured-occupancy concordance across loci**.
No background null is computed here, and **no occupancy call is made about any locus**. Both lanes
read `emc-ret-cistrome.json` read-only; nothing was copied.

## The evidence gap this closes

`emc-ret-target-scan.json` produced motif counts with composition nulls; `emc-ret-cistrome.json`
produced measured peak intersections. **The two had never been put on the same axis.** The gap was
not more motif scanning and not more peak retrieval — it was the missing *join*.

## Step taken

`benchmark.py` (in this directory) joins the frozen 25,001 bp promoter windows
(`emc-ret-target-scan-inputs.json:gene_windows`, −10 k/+15 k strand-aware) to the measured
promoter-window peak counts (`emc-ret-cistrome.json:part_2_intersection.per_peakset`, 103 read
peaksets of 110) at every locus present in both. Motif scores are computed with this repository's own
`scan_nbre` / `scan_nurre` from `emc_ret_target_scan.py`, imported in place.

**Pre-specified before any concordance number was seen:** primary score = exact-NBRE count;
secondary = one-mismatch NBRE count; outcome = fraction of peaksets with ≥1 promoter-window peak;
label = occupancy_fraction ≥ 0.5; statistic = Mann-Whitney AUC with a 20,000-draw permutation p;
concordance = concordant-pair fraction and Spearman rho; positive controls = **ENO3, PPARG, SEMA3C**,
the three published class-A direct EWSR1::NR4A3 targets already named in `emc_ret_target_scan.py`
`FOCUS_GENES` (PMID 26310886, PMID 31020999) — not chosen by this lane.

### Result — the benchmark FAILS

n = 8 loci (ENO3, KDR, NR4A1, NR4A3, PPARG, RET, SEMA3C, VEGFA); 28 informative pairs.

| locus | exact NBRE | 1-mm NBRE | measured occupancy fraction |
|---|---|---|---|
| ENO3 | 4 | 28 | 0.243 |
| KDR | 2 | 34 | 0.107 |
| NR4A1 | 0 | 15 | 0.214 |
| NR4A3 | 0 | 26 | 0.214 |
| PPARG | 3 | 32 | 0.107 |
| RET | 1 | 22 | 0.165 |
| SEMA3C | 0 | 39 | 0.117 |
| VEGFA | 2 | 28 | 0.262 |

* **Exact-NBRE score: AUC = 0.469, permutation p = 0.59, Spearman rho = 0.019, concordant-pair
  fraction = 0.482.** Chance.
* **One-mismatch score: AUC = 0.188, Spearman rho = −0.509.** If anything it runs the *wrong* way.
* **NurRE count: identical at every locus — zero discrimination by construction.**
* **Check 0 (added, reported as a failure): the pre-specified label is degenerate.** No locus reaches
  0.5 occupancy (range 0.107–0.262), so the AUC against the primary label is **undefined, not zero**.
  One declared fallback label — the median split of the same measured quantity — was used so a
  discrimination statistic exists at all, and is reported whatever it gives. No further threshold,
  transformation or subset was tried.
* **Check 1 (must be able to fail) PASSES:** the score-label shuffle gives chance — mean null
  AUC 0.5023, mean null concordance ≈ 0.50. The instrument is not broken; it is measuring nothing.
* **Check 2 (must be able to fail) FAILS:** the positive controls do **not** sit above the median.
  **SEMA3C — the single best-assayed direct target, the only one assayed with the EWSR1::NR4A3
  chimera in human cells with a chromatin assay against a predicted NBRE-*like* site — contains ZERO
  exact NBRE octamers in its 25 kb window**, while carrying the panel's **highest** one-mismatch
  count (39) and near-lowest measured occupancy (0.117). On the one-mismatch score ENO3 ties the
  median and also fails.

**Verdict: `benchmark_verdict.passes = false`.** On this panel the NBRE motif score carries no
information about measured NR4A promoter occupancy. This is the reported result, not an error.

## Repository arguments that lean on the substitution

Named so they can be re-read against this, **not** edited by this lane:

1. `research/manuscripts/program/emc-unexplored-treatment-lanes.md` §3.1 (lines 138–140) — proposes
   an NBRE-motif scan as the test of whether *RET* is a fusion target gene, and makes **"no NBRE at
   RET"** one half of the stated falsifier. Both directions of that inference are what this
   benchmark finds unsupported: on this panel an NBRE neither predicts occupancy nor does its
   absence predict non-occupancy (NR4A1, NR4A3 and SEMA3C have zero exact NBREs at mid-panel
   occupancy).
2. `research/modalities/nr4a3-re-reach.md` — the response-element-anchored degrader route, whose
   premise is that the NBRE octamer is the address the fusion reads. Its own selectivity caveat
   already limits it; this adds that the octamer does not track measured occupancy either.
3. `research/manuscripts/program/target-route-options.md` line 704 — "the whole family also binds
   the same NBRE/NurRE elements", used in a selectivity argument.
4. **Counter-example, and the standard to hold:** `research/modalities/emc-ret-lane.md` lines 78,
   104 and 148 already state that a scan can produce a prioritisation and never a target-gene
   claim, and `emc-ret-target-scan.json` already returned
   `ELEMENT_PRESENT_BUT_NOT_ABOVE_CHANCE` for RET. Those two do **not** lean on the substitution and
   need no change. The finding here strengthens, rather than contradicts, them.

## Artifact · validation · provenance · limitations · stop condition

* **Artifact:** `motif-vs-occupancy-benchmark.json` (per-locus rows, three scores, concordance,
  discrimination statistic, permutation null, both must-fail checks, verdict) and `benchmark.py`.
* **Validation / baseline:** the score-label shuffle (20,000 draws, seed 20260908) returns chance —
  so the pipeline can detect signal and reports none. Windows were cross-checked: every cistrome
  `promoter_window_bed` equals the scanned `gene_windows[...].window` (recorded in
  `_scope.window_agreement_between_inputs`).
* **Provenance:** inputs re-hashed at use and recorded in the artifact and in
  `checks/input-hashes.txt`:
  `emc-ret-target-scan-inputs.json` `dcaa23a6…c68b9`,
  `emc_ret_target_scan.py` `c8fd3032…6338e`,
  `emc-ret-cistrome.json` `08b249eb…015da1`. Full digests in the artifact.
* **Limitations.** **n = 8 loci is very small** — only loci present in *both* the cistrome
  intersection and the sequence windows can enter, and the 200-gene background panel has sequence
  but **no measured occupancy**, so it cannot be benchmarked. A negative at n = 8 is *absence of
  evidence for the substitution on this panel*, and it does not prove absence genome-wide; equally
  it would not have established the substitution had it passed. The peaksets are **wild-type
  NR4A1/2/3 ChIP in their own cell types — not EMC tumour cells and not the EWSR1::NR4A3 chimera**.
  A motif is not a binding site and a peak is not a function. **No efficacy, safety, selectivity,
  therapeutic-window, target-validation or clinical-readiness claim is made or supported.**
* **Stop condition:** met — one pass, both must-fail checks evaluated, verdict recorded. No
  transformation, subset or threshold was sought under which the benchmark would pass, and none
  should be. The next credible independent work is **not** re-scanning: it is obtaining measured
  occupancy for more of the loci that already have frozen sequence windows, which would give the
  benchmark power it does not currently have.
