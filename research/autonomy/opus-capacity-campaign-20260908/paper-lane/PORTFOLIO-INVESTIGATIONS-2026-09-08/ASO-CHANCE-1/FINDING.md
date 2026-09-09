---
id: DOC-OPUS-CAMPAIGN-ASO-CHANCE-1
title: "ASO-CHANCE-1 — how much of the junction ASO's off-target specificity exceeds chance"
level: L4
kind: investigation
status: complete
date: 2026-09-08
last_verified: 2026-09-08
---

# ASO-CHANCE-1 — junction-ASO off-target counts against a dinucleotide-preserving shuffle baseline

**The ASO package was read only.** No manuscript, artifact, design, control file or
`pinned-figures.json` was touched; nothing was regenerated; `regenerate_aso_chain.sh` was not run.
`git status` shows this lane directory as the only path this worker created. This document is a
**note for the frozen package's owner**, not an edit to it.

## 1 · Question

The committed null (`research/modalities/offtarget_chance_baseline.py`) grades every design against a
**uniform i.i.d. 16-mer**, so a design's expectation is a function of its LENGTH alone. That null
cannot separate "this sequence is unusually promiscuous" from "this sequence is GC-poor". So: **how
many of a junction ASO's off-target near-matches survive a null that holds base AND dinucleotide
composition fixed and varies only sequence order?**

## 2 · Merit

The ASO manuscript's specificity statement rests on off-target counts. If a composition-matched
random-order oligo would return the same counts, the counts describe the design's base composition
rather than its junction selection, and the specificity claim is weaker than it reads. Patients are
downstream of which of those two is true. The evidence needed is already on disk, and the answer is
falsifiable in one direction by the package's own committed scramble controls.

## 3 · Evidence gap, and what distinguishes it

Prior completed work established the *uniform* null and used it to retire the "0 of 58 designs is
off-target-clean" headline. The dinucleotide arm was never built: the committed controls
(`aso-control-oligos.json`) ARE dinucleotide-preserving Altschul–Erikson shuffles, but they were
screened only against six **mature parent transcripts** by a local duplex rule — never
transcriptome-wide. Inputs actually used: the 30 held
`junction-aso-offtarget-*-deep500-b{1,2}.json` screens (160 oligo rows, 157 screened, **145 unique
sequences**, lengths 16/18/20), `offtarget_chance_baseline.py`, `aso-control-oligos.json`, and
`aso-premrna-sequences.json` for background composition. Every input is re-hashed at use inside the
artifact.

## 4 · Step taken

`chance_baseline_dinuc.py` (this directory) computes, per design, the exact first-order-Markov
probability that an arbitrary background position matches at the panel's own threshold
(`>= ident/L`), by dynamic program over (last base, mismatches used) — no sampling of the 1,129-word
neighbourhood. It then draws **400 dinucleotide-preserving shuffles per design** using the
repository's own shuffler (`aso_parent_null.scramble_dinucleotide`, splitmix64 `Rng`, seed
20260908, **1 mononucleotide fallback in 58,800 draws (145 designs + 2 control reagents, 400 each)**) and reports the observed count against that ensemble.

### Artifact
`aso-offtarget-chance-baseline.json` — per-design observed counts, uniform / Markov(exonic) /
Markov(pre-mRNA) expectations, the 400-shuffle baseline with its 95% interval, both ratios, the
control check, and full input hashes.

### Validation
* The uniform DP reproduces `n_within(L,2)/4**L` **exactly** (rel. err 0.0) at L = 16, 18, 20 —
  it recovers the committed module's 2.6287e-07 at 16.
* **The failable check — the committed scramble controls must land at the baseline: PASS on the
  arm that could be run.** control-1 sits at percentile 26.3 and control-2 at 86.8 of their own
  reagent's 400-shuffle ensemble; both inside the central 95%. The baseline is therefore not
  mis-specified with respect to the package's own controls.
* ⚠ **The strong form of that check is NOT RUNNABLE and is recorded as such.** The controls have no
  transcriptome-wide observed count to land at — they were never BLASTed. Producing one is
  impossible here: the deep500 screens are **remote NCBI BLAST** runs (a `blast_rid` per oligo) and
  this lane has no network and no local RefSeq RNA corpus. The check passed on expectations, not on
  observations, and the two must not be quoted as one.

### Result

**Sequence order buys almost nothing at the level of chance expectation.** A design's chance
expectation divided by the mean of its own dinucleotide-preserving shuffles is **0.964–1.066
(median 1.004)** across all 145 designs. Holding dinucleotide composition fixed pins the expectation
to within about ±7%; the shuffle null is nearly degenerate by construction, which is itself the
finding — under any composition-matched background model, **essentially all of a design's modelled
chance load is its composition, not its junction.**

**Observed against that baseline** (median observed near-matches 126 for the 122 16-mers, max 374,
no evidence of a hitlist ceiling — maximum hitlist length 374 < 500): median
observed / shuffle-baseline = **0.49** overall (0.52 for 16-mers), with **126 of 145** designs below
1.0 and a maximum of 2.72. Read naively that says the designs carry about half the near-match load
of a composition-matched random-order oligo. ⛔ **Do not read it naively** — see limitations; the two
sides of that ratio were counted over different search spaces.

**The denominator-free reading, which does survive that problem.** Among same-length (16-mer)
designs, the composition-only chance model accounts for **r² = 0.27** of the spread in
log(observed+1) (Spearman 0.30); observed counts anticorrelate with GC (Spearman −0.48). So roughly
a quarter of the between-design variation in real off-target load is chance composition, and about
three quarters is sequence order and real transcriptome structure — repeats, paralogues and
transcript variants that no shuffle null can represent. That fraction is scale-invariant and does
not depend on the unknown BLAST database span.

**Honest bound for the package's owner:** the designs are **not** shown here to be specific beyond
chance. What is shown is (i) their modelled chance load is fixed by composition to within ±7%, so a
composition-matched control is the right comparator and the uniform null flatters or penalises by
composition alone; and (ii) most of the real variation between designs is not explained by
composition, so the observed counts do carry design-specific information — but this lane cannot say
whether that information is *favourable*, because the favourable-looking 0.49 ratio is not a
defensible number.

### Provenance
All inputs hashed in `inputs` of the artifact at the moment of use. Background: 20,011 nt of mature
exonic and 537,168 nt of pre-mRNA sequence from `aso-premrna-sequences.json` (EWSR1, FUS, NR4A3,
TAF15, TCF12, TFG). Transcriptome span 718,571,139 nt read from the committed
`offtarget-chance-baseline.json` null model. Checks in `checks/01-*`, `checks/02-*`.

### Limitations
* ⛔ **No efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim.** These are
  sequence statistics over a transcript database.
* ⛔ **The absolute observed/expected ratio is not trustworthy.** Observed counts come from remote
  blastn against `refseq_rna`; the expectation uses the 718.6 Mnt span counted by a *different*
  (local) scan. A factor-of-two discrepancy in the searched span would move the median ratio from
  0.49 to 1.0. Only the denominator-free statistics (order ratio, r², Spearman) are safe to quote.
* The background is a **first-order Markov model fitted to six genes**, and a real transcriptome is
  not Markov: it is repetitive and paralogous. This is an order-of-magnitude reference, never a
  p-value, and no threshold on any ratio is proposed.
* 18-mers (n=6) and 20-mers (n=17) are too few to read; the 20-mers' median observed count is 0,
  consistent with the 26x drop in neighbourhood probability from 16 to 18 to 20.
* 3 rows are `screen_failed` and are excluded, listed by sequence in the artifact.

### Stop condition
Reached. The bounded question is answered on held inputs and the failable check ran and passed on
the only arm that has data. **The next credible independent step is not available in this lane**: it
is a transcriptome-wide screen of the two committed scramble controls (and ideally ~50 dinucleotide
shuffles per design) under the *same* blastn parameters, which needs network access to NCBI or a
local RefSeq RNA FASTA. Until that exists, the observed arm of the control check stays unrun, and
that is the honest state.
