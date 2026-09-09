---
id: DOC-PUB-SYNLETH-PORTFOLIO-INVESTIGATION-20260909
title: "PUB-SYNLETH investigation — what the pan-sarcoma dependency statistic can and cannot resolve"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: PUB-SYNLETH
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# PUB-SYNLETH — portfolio investigation finding

Target document: `research/manuscripts/dependency/degrader-vs-synthetic-lethal.md` (PUB-SYNLETH,
`target_venue: internal_note`). All numbers below are reads of retained artifacts; no producer was
re-run and no external data was fetched.

## 1. The concrete question

The memo's §2b turns a public CRISPR panel into a route decision using one statistic,
`selectivity = mean(non-sarcoma lines) − mean(91 screened sarcoma lines)`. **At what subtype size
can that statistic resolve a dependency at all, and does its BRD9 null therefore mean "ncBAF is not
a dependency" or "this statistic cannot see a dependency of that shape"?**

## 2. Paper-level merit

Patient relevance is indirect but real: §3 of the memo re-weights this program's route choice —
which decisive experiment gets a slot in the scarce patient-derived EMC lines — partly on the
strength of that null. If the null is uninformative, a scarce-resource decision is resting on it.
The contribution is non-trivial and general: every rare-disease program that has no cell line of its
own reaches for exactly this transfer-prior move, and the resolution limit of the move is a
reusable, checkable quantity rather than an opinion. The evidence is fully attainable — it is
arithmetic on a committed artifact.

⛔ This is **not** a paper-shaped claim on its own and I am not proposing one. §4 of the memo
already decided the memo is not a preprint, and nothing here changes that. It is a correction and a
strengthening of a retained internal result.

## 3. The exact evidence gap, and what makes it different from completed/held work

§2b states its own gap in plain words: its headline is a claim about *selectivity*, and the one
self-check that could have shown selectivity detection works — BRD9 in synovial sarcoma — came back
weak (n=5, −0.130, 20% dependent). §2b therefore downgrades itself to "a weak prior against BRD9
rather than a settled negative" **without knowing whether the weakness is biology or instrument**.
That distinction was never resolved, in this memo or in the sibling `PUB-TXN-DEPENDENCY`, where a
"no selectivity" reading from the same pipeline was parked on 2026-09-08 for a different reason
(unpaired streams), not for this one.

Named inputs: `research/modalities/depmap-sarcoma-dependency.json` (DepMap 24Q4; 2105 models, 176
sarcoma models, `n_sarcoma = 91` on every gene record) and `depmap_sarcoma_dependency.py:246-258` (`stats()`; the statistic itself is line 256)
(the `stats()` definition of `selectivity`). Distinct from held work because it asks nothing about
EMC biology and adds no data: it asks what the retained instrument's resolution is.

## 4. The bounded step taken, and the result

`selectivity_detectability.py` — exact dilution arithmetic plus three checks on the retained
summaries. **A dependency present in k of N=91 sarcoma lines with per-line effect δ contributes
exactly (k/N)·|δ| to the pan-sarcoma statistic.** Findings:

**(a) The detector is validated — by a positive control the same run already produced and §2b never
used.** `FLI1` in Ewing sarcoma (k=27) is a textbook subtype-restricted selective dependency: 74.1%
of Ewing lines dependent against 1.9% of the rest of the panel. The pan-sarcoma statistic **does**
recover it, at +0.242, above this run's p90 background |selectivity| of 0.152. The dilution model
predicts the magnitude: 0.29 predicted against 0.242 observed. **§2b's stated validation gap is
closed, in the affirmative, from data already committed.**

**(b) And the same model says why the BRD9 control failed — k, not biology.** At k=5, a per-line
effect of the canonical common-essential size (−1.0) produces a pan-sarcoma statistic of only
0.055, against a run background whose median |selectivity| is 0.038 and whose p90 is 0.152. Clearing
p90 at k=5 would need a per-line effect of −2.77, beyond the strongest effect anywhere in the panel
(CDK7, −1.847). Closed loop on measured numbers: the actual synovial BRD9 signal (δ = −0.235 vs the
sarcoma baseline) contributes **0.0129**, about a third of the run's own median background. The
statistic could not have reported that signal even though the run measured it directly. Same
verdict for any subtype at k ≤ 13 (alveolar RMS k=8, rhabdoid k=13). At k=0 — EMC — the statistic is
identically blind at any effect size.

**(c) A pan-essential trap is sitting in the panel, unflagged.** `EWSR1` carries the **largest**
|selectivity| of all 64 gene records (+0.373) while being a dependency in 96.7% of sarcoma lines
**and 91.5% of everything else**. That is the CDK7/CDK9 error in a new guise: the statistic is
measuring a shift in the depth of a near-universal essentiality, not a margin. Any selectivity
number in this panel must be read beside `rest_frac_dependent` or it manufactures a false window.

**(d) Which §2b claims survive.** Supported: the pan-essentiality of CDK7/CDK9/BRD4 (a k=N claim,
high power) and the broad non-dependence of NR4A3/NR4A1/NR4A2 (also k=N). Not supported: the
pan-sarcoma BRD9 selectivity null as a negative transfer prior. **Unaffected and still standing: the
Ewing BRD9 subtype read (n=27, +0.134, 0% dependent)** — that is a direct subtype measurement, not
the diluted statistic, and it remains the real retained argument against the BRD9 hypothesis. So
§3's re-weighting toward the degrader route is **weakened, not erased**, and the memo's own hedge is
the right reading for a reason it does not state.

## 5. Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `selectivity_detectability.py` and `selectivity-detectability.json` in this
  directory. `checks/01`–`03` hold every execution attempt with command, stdout, stderr and exit
  code, including the run whose over-stated wording I corrected (`01` → `02`).
* **Validation** — the dilution model is checked against a real measured positive control it did not
  fit (FLI1/Ewing: 0.29 predicted, 0.242 observed) and against a real measured negative (BRD9/
  synovial: 0.0129, below background). Both directions come from the same committed run.
* **Provenance** — `research/modalities/depmap-sarcoma-dependency.json` (DepMap public release
  24Q4, figshare, CRISPR Chronos gene effect + Model.csv), read-only; statistic definition from
  `depmap_sarcoma_dependency.py`. No network, no new data, no re-run of the producer.
* **Limitations** — group summaries only: the retained artifact holds no per-line matrix, so this is
  exact dilution arithmetic plus an order-of-magnitude background scale, **not** a variance-based
  power curve. The background scale comes from hypothesis-selected genes, not a random null set.
  The FLI1 control validates detection at k=27 only. Back-computed non-Ewing means are not
  meaningful to three decimals. **Nothing here is an EMC measurement** — no EMC line in the panel
  has CRISPR data — and nothing here says whether BRD9 is or is not an EMC dependency; it says the
  pan-sarcoma statistic cannot answer that. No efficacy, potency, selectivity, safety,
  therapeutic-window or clinical claim is made for either route.
* **Stop condition** — reached. The question was "what can this statistic resolve", it is answered
  quantitatively in both directions, and the answer is stable without new data. Do **not** spend
  further cycles re-litigating the BRD9 prior on this panel; the informative read (Ewing, n=27)
  already exists and the diluted one cannot be improved by more analysis of the same summaries.

## 6. Honest outcome and the next credible independent step

This is a **partial no-go with a repair**. No-go: the pan-sarcoma BRD9 null cannot carry the weight
§3 puts on it, and no further computation on this panel will change that. Repair: §2b's validation
gap is genuinely closed in the affirmative, so the panel's k=N conclusions (the pan-essential
verdicts, the NR4A3 non-dependence) are stronger than §2b was willing to claim for them.

The dependency this exposes is concrete and is **not** a generic "we need EMC models": the missing
input is the **per-line CRISPR gene-effect matrix**, which would replace this arithmetic with a real
power curve and permit subtype-level tests at their own k instead of the diluted pan-sarcoma
statistic. That is a public file, and re-running the existing producer with subtype-level output
would be the next bounded step. It requires network egress and is out of scope for this lane.

## 7. Unapplied change proposed for a shared file

I made **no edit** outside this directory. The memo `degrader-vs-synthetic-lethal.md` §2b/§3 would
be improved by recording (a) that FLI1-in-Ewing closes its selectivity-validation gap, (b) that the
BRD9 pan-sarcoma null is dilution-limited at k=5 while the Ewing subtype null is not, and (c) the
EWSR1 pan-essential-trap warning. A concrete diff was **not** prepared because the memo is another
paper's current manuscript; the parent should decide whether to commission it.
