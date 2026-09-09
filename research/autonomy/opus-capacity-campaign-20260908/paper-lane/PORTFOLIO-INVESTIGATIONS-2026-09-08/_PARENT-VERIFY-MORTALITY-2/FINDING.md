---
id: DOC-PORTFOLIO-INVESTIGATION-MORTALITY-2-2026-09-08
title: "MORTALITY-2 — is the EMC terminal-event cue excess a reporting difference, or a study-type composition effect?"
level: L4
kind: investigation
status: live
date: 2026-09-08
last_verified: 2026-09-09
---

# MORTALITY-2 — the genre confound the previous lane named, tested

Follow-through on `../PUB-MORTALITY-MECHANISM/FINDING.md`. That lane found that, within one
Europe PMC retrieval, death-cue sentences in EMC-titled papers name a physiological terminal
event **more** often than those in the 128 same-retrieval papers that are not about this
disease (strict lexicon **4/116 = 3.45 %** vs **3/461 = 0.65 %**, Fisher two-sided
**p = 0.033**). It named its own decisive limitation: **the comparator is unmatched on study
type.** Case reports narrate a death; cohort studies and reviews tabulate deaths. That lane
could not separate a genre effect from a reporting difference. This lane does.

## 1. The question

**Does the EMC terminal-event cue excess survive matching on study type, or is it explained by
the composition of the two corpora?**

This is a question about **text and about an instrument**, exactly as before. It assigns no
cause of death, reads no survival curve, makes no clinical claim and gives no patient-specific
advice. **The unit is a sentence, not a patient** — a regex-matched sentence is not a death,
and a death is not a patient. The crude causal and survival-mechanism readings rejected earlier
remain rejected and are not revived here in any wording.

## 2. Merit

The manuscript's §4.2 generalises §3.1 into a claim about how ultra-rare cancer literatures
record cause of death. The previous lane showed the only available comparator does not support
the implied contrast. If that comparator result is itself an artefact of genre, then **neither**
direction is established and the §4.2 scope narrowing must say so on those terms. Which of the
two it is decides what a reviewer is owed. The corpus is committed, so the question is settleable
offline at no cost and with no new retrieval.

## 3. The evidence gap this closes

`research/literature/emc-mortality-probe.json` records **162 papers / 577 death-cue sentences**
with title, journal and year — and no study-type field anywhere. No study-type classification of
this corpus existed in the repository before this lane. Without one, the 3.45 % vs 0.65 % contrast
cannot be read at all, because the two corpora were never shown to be comparable populations of
documents.

## 4. What was done, and the ordering that makes it worth anything

**The classifier was pre-specified in code and frozen before any rate was computed.** The
ordering is evidenced by the check sequence, not merely asserted:

| check | what ran | what it could see |
|---|---|---|
| `checks/01` | `dump_corpus_metadata.py` | titles, journals, years only — sentence text and `has_mechanism_cue` deliberately excluded from the dump |
| `checks/02` | `genre_classifier.py` — **the frozen rule**, sha256 `9f00b724…be5be3a3` | the same metadata; **prints the genre distribution and no rate of any kind** |
| `checks/03` | `draw_handcheck_sample.py` | 40 of 162 papers, simple random, seed 20260908 |
| `checks/04` | `handcheck_agreement.py` against hand labels written in `handcheck-labels.json` | machine label vs hand label; still no cue field |
| `checks/05` | `genre_stratified_rates.py` — **the first script in this lane that reads a cue field**; re-prints the identical classifier sha256 | everything |
| `checks/06` | `reclassification_sensitivity.py` | single-paper adversarial reclassification |
| `checks/07`, `checks/08` | blindness audit of the frozen rule | 07's grep matched one line **inside the docstring**; 08 re-runs it over code with docstrings and comments stripped — **0 matches, PASS** |

The rule (first match wins; the precedence is part of the pre-specification) assigns each paper
to **case_report_or_series** (case-report journal, or a case-report phrase in the title),
**review_or_synthesis**, **clinical_study**, **laboratory_or_methods**, or **unclassified** —
the last kept as its own stratum and never silently folded into another. Its accepted failure
modes were written down in advance in the module docstring. Both cue instruments — the shipped
`has_mechanism_cue` regex and the strict terminal-event lexicon — are reused **verbatim** from
the completed lane. Nothing was re-tuned.

## 5. Result

### A. The confound is real and large

| stratum | EMC papers (share) | EMC sentences | other papers (share) | other sentences |
|---|---|---|---|---|
| case_report_or_series | **18 (53 %)** | 56 | **26 (20 %)** | 60 |
| review_or_synthesis | 2 (6 %) | 8 | 23 (18 %) | 66 |
| clinical_study | 4 (12 %) | 12 | 33 (26 %) | 169 |
| laboratory_or_methods | 5 (15 %) | 16 | 19 (15 %) | 83 |
| unclassified | 5 (15 %) | 24 | 27 (21 %) | 83 |

**48 % of EMC death-cue sentences sit in case reports against 13 % of the comparator's.** The two
corpora were never comparable populations of documents, and the previous lane's crude contrast
was computed across that difference.

### B. The excess does not survive genre matching

**Strict terminal-event lexicon** (the pre-specified tier-1 instrument):

| contrast | EMC | other | test |
|---|---|---|---|
| crude, unstratified (reproduces the previous lane exactly) | 4/116 = 3.45 % | 3/461 = 0.65 % | Fisher **p = 0.033** |
| within case reports | 4/56 = 7.14 % | 2/60 = 3.33 % | Fisher **p = 0.43** |
| within all other genres combined | 0/60 = 0 % | 1/401 = 0.25 % | Fisher p = 1.0 |
| **five-stratum exact conditional (CMH) test** | T = 4, E[T] = 3.12 | | **p = 0.70** two-sided (one-sided 0.38), MH OR 1.78 |
| collapsed case vs non-case, exact conditional | T = 4, E[T] = 3.03 | | **p = 0.46** two-sided, MH OR 1.95 |

**Direct standardisation** makes the composition effect a number: the EMC rate reweighted to the
comparator's genre mix falls from **3.45 % to 0.93 %** (comparator crude 0.65 %); the comparator
rate reweighted to EMC's mix rises from **0.65 % to 1.86 %**. The crude 5.3-fold gap becomes
roughly **1.4- to 1.9-fold**, with no statistical support at these counts.

**Shipped `has_mechanism_cue`** behaves the same way: crude 10.34 % vs 3.47 % (p = 0.0057)
becomes **p = 0.102** on the five-stratum exact test (MH OR 2.22), 0.160 collapsed; within case
reports 17.9 % vs 6.7 %, Fisher p = 0.088. Standardised to the comparator's mix, EMC falls from
10.3 % to 6.1 %.

### C. The descriptive fact underneath, which is the cleanest statement of the genre effect

**Every patient-narrative terminal-event flag in the entire 162-paper corpus, on both sides of
the split, occurs in a case report** — 4 EMC (PMIDs 41799218, 35775709, 35910216 ×2) and 2
comparator (35399302 sinonasal carcinoma, cardiac arrest; 38264746 NUT midline carcinoma,
respiratory failure). The one strict flag outside the case-report stratum, in the whole corpus, is
a **pooled adverse-event statement** (33946310, trastuzumab-deruxtecan), which is not a patient
narrative at all. Terminal events are named where deaths are narrated; both corpora are silent
where deaths are tabulated.

**The reading, at the strength the data support and no further: the previously reported excess is
explained by composition. Once study type is held fixed, the direction persists as a point
estimate (MH OR ≈ 1.8–2.2) but there is no statistical support for it, and the standardised gap
is a fraction of the crude one. This is a null, and it is reported as a null.** §3.1 of the
manuscript is untouched and still stands; what has now failed twice — once for the implied
contrast, once for its reversal — is any claim that this disease's record differs from its
comparator in either direction.

## 6. The classifier is an instrument with error, and here is how much

Hand-checked, 40 of 162 papers, single reader, drawn by fixed seed **before** any rate was
computed (`handcheck-labels.json`, `handcheck-agreement.json`):

* **Overall agreement 70 % (28/40)**, Wilson 95 % CI **54.6–81.9 %**. This is not a good rule and
  is not presented as one.
* **The one boundary the result depends on is the one it measures well:**
  `case_report_or_series` **precision 1.00** (9/9, CI 0.70–1.00) and **recall 0.90** (9/10,
  CI 0.60–0.98). One case report was missed — 39965625, "An 11-year-old boy with a posterior
  fossa tumor", which carries no cue flag.
* The errors are concentrated elsewhere: **7 of the 12 disagreements are machine `unclassified`**
  (32 papers, 20 % of the corpus, fire no trigger), and `review_or_synthesis` recall is only 0.50
  because review-ish titles are pulled to `laboratory_or_methods`. Both failures move papers
  *among non-case strata*, which the collapsed contrast is insensitive to.
* **What a misclassification rate does to the result** — measured, not asserted, two ways:
  * *Aggregate simulation* (2000 draws each, papers randomly reassigned across the case/non-case
    boundary at the measured error rates): at **e = 0.10** the median stratified two-sided p is
    0.21; at **e = 0.30** it is 0.044. Note the direction of that movement carefully: **random
    misclassification erodes the stratification and drags the test back toward the unstratified
    crude result.** A noisier classifier does not threaten this null — it *under-corrects* for the
    confound and would spuriously restore the crude significance. The reported null is therefore
    the conservative side of classifier error, and a *better* classifier would correct more.
  * *Adversarial single-paper reclassification*, all 162 papers flipped one at a time: the
    stratified two-sided p ranges **0.19–0.71** (strict) and **0.060–0.25** (shipped).
    **No single reclassification anywhere in the corpus brings either instrument back below
    p = 0.05.**

## 7. Limitations — these bound the result

* **A null is not equality.** Within case reports the counts are 4 vs 2 events. The comparison has
  almost no power; a real two-fold difference in either direction is entirely compatible with
  these data. The correct statement is *unsupported*, never *absent*.
* **Sentence unit, not patient unit.** Unchanged from the previous lane and restated deliberately:
  no count here is a patient count, a death count or a cause.
* **Study type is inferred from titles and journal names**, not from MeSH publication types or
  full text — neither is in the committed artifact and no retrieval was permitted. 20 % of papers
  fire no trigger at all.
* **Single unblinded reader** for the hand check: the disease name is in the title and cannot be
  blinded, and there is no second reader, so no inter-rater kappa exists.
* **All the ascertainment limits of the previous lane still apply**: open-access convenience
  sample, no denominator on either side, no distinct-patient guarantee, and comparator sentences
  not verified to describe patient deaths beyond the ones read verbatim.
* **No claim is made about any other disease's literature**, and none may be made from this.

## 8. Stop condition

**Met.** The pre-specified question is answered in both instruments, with the confound quantified,
the classifier's error measured, and the result shown robust to single-paper reclassification.

**Forward stop:** do not convert this into a claim that reporting practice is *equal* across
genres or diseases — the power is not there. Advancing further requires a study-type-matched
comparator drawn at the design stage and hand reading at the patient unit, neither of which is
obtainable without new retrieval.

## 9. For the paper owner — suggested, NOT applied

No file outside this directory was modified; nothing is proposed for `systems/graph/*.json`; no
diff to the manuscript was written; nothing was staged, committed or pushed. The suggestion, for
the owner to accept or reject, **supersedes** the previous lane's suggested wording: §4.2 should
record that **no comparator literature was measured, and that the one comparator obtainable within
this retrieval yields no supported contrast in either direction once study type is held fixed —
because both corpora name terminal events almost exclusively in case reports.** That is a scope
narrowing of an implication, not a change to any number; no pinned figure and no artifact is
affected.

## 10. Artifacts in this directory

| file | what it is |
|---|---|
| `dump_corpus_metadata.py` → `corpus-metadata.json` | outcome-free metadata dump (step 0) |
| `genre_classifier.py` → `genre-classification.json` | **the pre-specified frozen rule**, sha256 `9f00b724…be5be3a3`, and its assignment of all 162 papers |
| `draw_handcheck_sample.py` → `handcheck-sample-skeleton.json` | seeded 40-paper draw |
| `handcheck-labels.json`, `handcheck_agreement.py` → `handcheck-agreement.json` | hand adjudication, confusion matrix, per-stratum precision/recall |
| `genre_stratified_rates.py` → `genre-stratified-rates.json` | **the stratified artifact**: composition, within-stratum rates, exact conditional tests, standardisation, misclassification simulation |
| `reclassification_sensitivity.py` → `reclassification-sensitivity.json` | all 162 single-paper flips |
| `checks/00`–`checks/08` | every execution attempt with real exit codes, the failed one included |
