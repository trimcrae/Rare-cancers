---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-MORTALITY-MECHANISM-2026-09-08
title: "Portfolio investigation — PUB-MORTALITY-MECHANISM: is the mechanism-of-death silence a property of this disease's literature, or the base rate of its retrieval?"
level: L4
kind: investigation
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# PUB-MORTALITY-MECHANISM — portfolio investigation

## 1. The question

**Of the death-cue sentences retrieved by one Europe PMC pass, does the rate at which a
sentence names a physiological terminal event differ between the 34 papers whose title names
this disease and the 128 same-retrieval papers that do not — and does the only automatic
mechanism detector this repository owns (`has_mechanism_cue`) measure that at all, judged
against the hand-read gold standard?**

This is a question about **text and about an instrument**. It asks nothing about what any
patient died of, assigns no cause, uses no survival curve, and makes no clinical claim.

**Explicitly not this question, because these readings are rejected and stay rejected:** what
EMC patients die of; any causal attribution from the decomposition; any re-reading of a
survival curve as a mechanism; any restatement of the competing-share or ceiling figures.
None of `emc-mortality-decomposition.json`, `emc-relative-survival.json` or the ceiling
arithmetic is touched, re-run, re-derived or re-interpreted here.

## 2. Paper-level merit

The manuscript's **first** result (§3.1) is a negative about a literature: 27 of 50
documented-death instances state no cause, only 14 carry a stored mechanism label, only 3
name a terminal event. §4.2 then generalises it — *"for ultra-rare cancers generally, the
implication is that cause-of-death recording … determines whether a disease's evidence base
can support the questions its research programme asks."*

**That claim has no comparator anywhere in the package.** The obvious reviewer question —
*28 per cent against what?* — is unanswered, and a rare-disease literature that merely shares
the base rate of all case-report writing would not support the §4.2 generalisation. The
comparator matters to patients only indirectly, but it decides whether the paper's second
half is a finding about this disease or a restatement of how oncology case reports are
written. It is attainable: the comparator corpus is **already retrieved and committed**.

## 3. The exact evidence gap, and what makes it different

`research/literature/emc-mortality-probe.json` holds **162 papers with 577 death-cue
sentences**. The classification pipeline discards **128 of those papers (461 sentences)** at
the title screen because their deaths belong to other diseases' patients — a correct
inclusion rule for a study of *this* disease, which leaves the entire comparator unanalysed.
Nothing in the repository has ever measured those 461 sentences.

Distinct from prior completed work on this family: W06b measured misclassification
sensitivity of the relative-survival convergence; W06h/W06i audited the "share no input"
independence wording; W14 added drift guards to the three generators; W30 checked registry
conformance. **All concern the decomposition/relative-survival half or its prose. None
touches the corpus result, its instrument, or the discarded comparator.** No cohort is
reused, no independent validation is manufactured, and no closed route (B1/B2/B4, R1–R4) is
approached — this is a read of two committed files.

## 4. The bounded step taken

`cue_instrument_check.py` (this directory) — no network, two committed artifacts read
read-only, one JSON written here.

**Q1, the instrument, against the hand-read gold standard.**

* **Integrity.** All **577/577** stored `has_mechanism_cue` values reproduce exactly when the
  shipped regex (`scripts/lit_mortality_probe.py:145`) is re-run on the stored sentences —
  **0 mismatches**. Nothing previously checked this.
* **The shipped cue is not a mechanism measure, and now there are numbers.** On the 18 gold
  rows it flags 2/2 rows tiered *named terminal event*, but also **3 of 8** rows tiered
  *assigned broad cause category*, **1 of 2** rows that document **no death at all**, and
  **4 further EMC death sentences that no gold row cites**. It is a recall-oriented retrieval
  hint, exactly as the probe README says — confirmed rather than assumed.
* **A pre-specified strict lexicon does work here.** Written to the gold standard's own
  tier-1 definition (named physiological terminal event only; organ sites, treatment
  settings, relatedness judgements and bare "complication" excluded), fixed before any result
  was seen. It flags **exactly 4 EMC death sentences**, which are **exactly the 3 gold
  patient instances with a named terminal event** (one patient narrated in two sentences):
  0 of the 8 broad-category rows, 0 of the 4 no-cause rows, 0 uncited sentences.

**Q2, the comparator — the substantive result, and it does not favour the manuscript's
implied contrast.**

| instrument | EMC-titled (34 papers) | not EMC-titled (128 papers) | Fisher 2-sided | direction |
|---|---|---|---|---|
| strict terminal event | **4/116 = 3.45 %** [1.4–8.5] | **3/461 = 0.65 %** [0.2–1.9] | **p = 0.033** | **EMC higher** |
| shipped `has_mechanism_cue` | 12/116 = 10.3 % [6.0–17.2] | 16/461 = 3.5 % [2.2–5.6] | p = 0.0057 | EMC higher |

Paper-level: 3/34 EMC-titled papers carry ≥1 strict flag against 3/128 others.

**Reading, stated at the strength the data support:** within this single retrieval, death-cue
sentences in this disease's own papers name a terminal event **more** often than death-cue
sentences in the papers that merely mention it — not less. The manuscript's §3.1 finding
(most deaths carry no stated mechanism) is **unaffected and stands**; what is *not* supported
by the only comparator now available is the further, implied contrast that this disease's
record is distinctively silent. The three flagged comparator sentences were read verbatim
(sinonasal carcinoma, cardiac arrest; NUT midline carcinoma, respiratory failure; a
trastuzumab-deruxtecan safety aggregate) — two are patient narratives, one is a pooled
adverse-event statement, which is itself a genre difference and is reported as such.

**Artifact** · `cue-instrument-check.json` + `cue_instrument_check.py` (this directory).
**Validation / baseline** · the 18 hand-read gold rows of
`research/manuscripts/emc-terminal-events-classified.json` are the baseline for Q1; the
577-sentence re-derivation is an integrity check with a real failure mode (0 found); the
strict lexicon was pre-specified in code before any Q2 number was computed.
**Provenance** · `research/literature/emc-mortality-probe.json` (committed, 2026-09-04) and
`research/manuscripts/emc-terminal-events-classified.json`; corpus split uses `EMC_TITLE`
copied verbatim from `research/manuscripts/emc_terminal_events.py:56`, reproducing the
manuscript's own 34/128 split. No retrieval, no network, no cohort.

## 5. Limitations — these bound the result, they are not decoration

* **Unit is a sentence, not a patient.** The manuscript's unit is a patient instance for good
  reason; the comparator has no hand reading, so only a sentence-level automatic instrument
  is comparable across both corpora. The EMC-side patient counts are unchanged and are not
  recomputed here.
* **The comparator is unmatched on study type.** The 128 papers mention this disease in a
  differential or a citation; their death sentences skew to survival methods, other diseases'
  cohorts and safety tables. A higher EMC rate is therefore **as consistent with a case-report
  genre effect as with better reporting**, and this step does not separate them.
* **Ascertainment limits are real and unresolved:** open-access convenience sample (328 of 600
  enumerated retrieved), no denominator on either side, no distinct-patient guarantee, and a
  sentence flagged in the comparator has **not** been verified to describe a patient death
  except for the three read here.
* **Lexicon dependence.** Recall of the strict instrument is validated against **3** gold
  positives. A different but defensible lexicon could move the EMC numerator by ±1–2, which
  is a large relative move on these counts. The Fisher p is not robust to that and is
  reported as a descriptive contrast, not a test result to lean on.
* **No claim is made about other diseases' literatures**, and none may be made from this.

## 6. Stop condition

**Pre-specified and met:** if the strict instrument had flagged any EMC death sentence that
the gold reading tiers below *named terminal event*, the comparator would have been
uninterpretable and this lane would have stopped as a no-go. It flagged none.

**Forward stop:** do **not** convert this into a claim about cause-of-death reporting in
rare-cancer literature generally without (a) a study-type-matched comparator sample and
(b) hand reading of the comparator sentences at the patient unit. Until both exist, the
result is a bounded internal measurement: *the manuscript's implied contrast has no
supporting comparator, and the one comparator obtainable without new retrieval points the
other way.*

## 7. For the paper owner — suggested, NOT applied

No file outside this directory was modified. Nothing is proposed for
`systems/graph/*.json`. The suggestion, for the owner to accept or reject, is a single
sentence of scope in §4.2 recording that no comparator literature was measured and that the
one available within this retrieval does not show this disease's record to be distinctively
silent. Because that is a scope narrowing of an implication and not a change to any number,
no pinned figure and no artifact is affected. **This lane wrote no diff to the manuscript.**
