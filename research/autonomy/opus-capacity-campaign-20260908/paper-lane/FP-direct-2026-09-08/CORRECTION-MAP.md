# CORRECTION MAP — FP direct current-field correction, 2026-09-08

Five edits: the four the root disposition memo names, plus one author-flagged extension of correction 1 at a
second live site of the same assertion (row 1b), which the parent can accept or revert on its own.
Every row states the exact old text, the exact new text, the file and anchor, and why the old form was
affirmative-before-caveat. Producer strings were corrected first; the artifact was propagated afterwards.

---

## 1 — Sjögren 2003 `context_note`: recruitment / uniform-rule claims

* **File / anchor (producer, corrected first):** `research/manuscripts/emc_fusion_partner_pooling.py`,
  the `sjogren-2003-prevalence` cohort dict, key `context_note`.
* **File / anchor (generated):** `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json`,
  `$.cohorts[13].context_note`.

**OLD (exact, removed from the current field):**

> The reproducible rule actually applied is narrower and is applied to every series: a cohort is out of the
> PREVALENCE pool when a documented share of its patients entered on an already-known partner assignment,
> because the partner share is then partly an entry criterion. Four of these nine patients entered on a
> fusion transcript the same group had already published (refs 7, 12, 15 above); those four are 3/4
> variant-partner against 1/5 among the five not previously reported, and the partner-unassigned residue of
> zero on that half of the cohort follows from their already-known assignment.

**NEW (exact):**

> ⛔ CORRECTED 2026-09-08 (direct current-field correction). WHAT THE SOURCE DOCUMENTS, AND ALL IT DOCUMENTS:
> the fusion transcripts of four of these nine patients had been PREVIOUSLY PUBLISHED by the same group
> (refs 7, 12, 15 above), and the retained Materials and Methods describe this work as an EXTENSION OF THOSE
> PRIOR STUDIES. NO RECRUITMENT MECHANISM IS RECORDED FOR ANY PATIENT IN THIS SERIES. Holding the series out
> of the PREVALENCE pool is a SELECTION JUDGEMENT OF THIS SYNTHESIS under its own stated criterion, and the
> partner-enrichment reading behind that judgement is an INFERENCE from the entry routes recorded in
> `entry_route_per_patient` -- not a documented entry criterion, and not a rule shown to have been applied by
> any source. ⛔ *Superseded, retained (2026-09-08, direct): '<the OLD text above, quoted in full>'* THAT PUT
> AN INFERRED RECRUITMENT RULE, AND A UNIFORM CROSS-SERIES RULE, AS AFFIRMATIVE STATEMENTS AHEAD OF THE
> CAVEATS THAT FOLLOWED THEM; an appended caveat does not narrow an assertion made before it.

**Why the old form was affirmative-before-caveat.** It asserted, in the indicative and with no qualifier,
(i) that a reproducible rule "is applied to every series" — a uniform cross-study recruitment claim no source
supports — and (ii) that "four of these nine patients entered on" a known assignment and that the zero
unassigned residue "follows from" it — a recorded recruitment mechanism. The two ⚠ sentences that call the
enrichment an inference and the rule this synthesis's own judgement stood LATER in the same field, so a
reader met the assertion first. The new text puts the supported account (prior publication; an extension of
prior studies; no recorded recruitment mechanism; this synthesis's selection judgement) first and keeps the
withdrawn wording only inside a dated, delimited superseded quote. The following R6 supersession, both ⚠
caveats, the direction check and the `aso_coverage_ladder.py` pointer are all preserved unchanged.
No source cell, count, membership or separate Sjögren outcome was touched; no new pooling.

---

## 1b — SAME assertion, second live site (AUTHOR-FLAGGED EXTENSION, not named in the memo)

* **Anchor:** producer `analyses.C_partner_prevalence.cohorts_excluded["sjogren-2003-prevalence"]`;
  generated `$.analyses.C_partner_prevalence.cohorts_excluded.sjogren-2003-prevalence`.

**OLD (exact):**

> partner-ascertainment-enrichment: four of its nine patients are in the series because the same group had
> already published their fusion transcript, so for those four the partner assignment is the entry ticket and
> the partner-unassigned residue of zero is structural on that half of the cohort. This is selection on
> PARTNER ASCERTAINMENT and is not a claim that the mortality outcome was the inclusion criterion

**NEW (exact):**

> partner-ascertainment-enrichment. ⛔ CORRECTED 2026-09-08 (direct current-field correction), to what the
> source documents: the fusion transcripts of four of its nine patients had been previously published by the
> same group, and the retained Materials and Methods describe this work as an extension of those prior
> studies. The source does not record how any patient entered the series. Holding it out is a SELECTION
> JUDGEMENT OF THIS SYNTHESIS on partner ascertainment, and the partner-enrichment reading behind it is an
> INFERENCE, not a recorded recruitment rule. It is not a claim that the mortality outcome was the inclusion
> criterion. ⛔ *Superseded, retained: '<the OLD clause above>'* See cohorts[sjogren-2003-prevalence].context_note

**Why it was corrected here too.** This field carried the withdrawn recruitment rule — "are in the series
because ...", "the entry ticket", "is structural" — in the indicative WITH NO CAVEAT AT ALL, not even an
appended one. Leaving it would have left the artifact asserting, as its stated exclusion rationale, exactly
the counterfactual recruitment mechanism correction 1 withdraws. It is the same correction at a second live
site, not a new claim; it is flagged separately because the memo named only the `context_note`.

---

## 2 — Suemitsu 2025 `context_note`: "CUTS TOWARD THE NULL" and the obsolete pooled contrast

* **Anchor:** producer `suemitsu-2025-outcome` cohort dict, key `context_note`; generated
  `$.cohorts[5].context_note`.

**OLD (exact, two places in the same field):**

> ⭐ IT IS RECORDED HERE BECAUSE IT CUTS TOWARD THE NULL AND WAS NOT DISCLOSED. An undisclosed exclusion that
> weakens the paper's own headline is the worst kind, and this one sat …

> ⚠ AND IT IS NOT EVIDENCE AGAINST THE PARTNER EITHER: 2 TAF15 patients of 18 cannot exclude an effect of the
> size the pooled contrast reports, so this is a series FAILING TO ESTABLISH the partner, not one refuting it.

**NEW (exact):**

> ⭐ IT IS RECORDED HERE BECAUSE IT WAS NOT DISCLOSED. ⛔ *Superseded, retained (2026-09-08, direct
> current-field correction): 'IT IS RECORDED HERE BECAUSE IT CUTS TOWARD THE NULL AND WAS NOT DISCLOSED.'*
> THIS SERIES DOES NOT CUT TOWARD A NULL. It reports a FAILURE TO ESTABLISH an association between overall
> survival and fusion subtype, which is not a result in either direction. An undisclosed exclusion is the
> worst kind, and this one sat …

> ⛔ *Superseded, retained (2026-09-08, direct current-field correction): '<the second OLD sentence above>'*
> THAT READING INVOKED A POOLED CONTRAST THAT NO LONGER EXISTS. THE CURRENT STATEMENT: this series reports a
> FAILURE TO ESTABLISH an association between overall survival and fusion subtype, and it retains no
> per-partner event cells and no model specification, so THIS SYNTHESIS CANNOT ASSESS THE MAGNITUDE OR THE
> PRECISION of what it reports. An UNESTABLISHED association is not a null and is not evidence against the
> partner.

**Why the old form was affirmative-before-caveat.** "IT CUTS TOWARD THE NULL" is a directional reading of a
result the same field elsewhere says is not a null — an affirmative interpretation standing ahead of the R4
supersession that withdrew "AND IT IS NULL". And the closing sentence sized the undetectable effect against
"the pooled contrast", a contrast withdrawn as source-unverified earlier in this very field: it reasoned from
a quantity that no longer exists, and the reader met it as the field's last word. The replacement states the
unestablished association and the missing per-partner event cells and model specification, and says why the
magnitude and precision cannot be assessed here. The verbatim abstract quotation, the explicit partner
integers (EWSR1 14/18, TAF15 2, TCF12 1, FUS 1), the OS-endpoint limitation, the unresolved MSK/MSKCC overlap
and the full disclosure history are all preserved unchanged.

---

## 3 — §3.5 heading and `analyses.C_partner_prevalence.question`: a conditional named-partner share

* **Anchors:** `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md` line 535 (section
  heading); producer `analyses.C_partner_prevalence["question"]`; generated
  `$.analyses.C_partner_prevalence.question`.

**OLD (exact):**

> ### 3.5 · Partner prevalence — how many patients this would touch

> How many EMC patients would a TAF15-vs-EWSR1 stratification actually touch?

**NEW (exact):**

> ### 3.5 · The conditional named-partner share in the selected series

> What is the conditional named-partner share -- TAF15::NR4A3 against the other named 5' partners -- among
> partner-assigned cases in the four selected series? ⛔ This is a conditional share in selected series, NOT a
> prevalence in any EMC population and NOT the size of a clinical group.

**Why the old form was affirmative-before-caveat.** Both labels framed the section as a population figure —
"prevalence", and "how many patients this would touch" — while the corrected table, verdict and body text
below them say the opposite: 28/154 is a conditional share among named-partner-assigned cases in four
selected series and sizes no clinical group. A heading is read before the paragraph that qualifies it, so the
display label was carrying the withdrawn claim on its own. This is a label correction only: no number,
denominator, interval or cohort membership changed, and no new clinical estimate is introduced. The analysis
KEY `C_partner_prevalence` is deliberately left alone — renaming it would move JSON structure, which this
correction is not authorised to do.

---

## 4 — "No wet-lab evidence exists": no NEW wet-lab work by this synthesis

* **File / anchor:** `research/autonomy/opus-capacity-campaign-20260908/paper-lane/FP-residual/RESIDUAL-LIMITATIONS.md`,
  §1 residual-limitations list, final bullet.

**OLD (exact):**

> - **No wet-lab evidence exists. There is no wet lab.** No efficacy, safety, selectivity, therapeutic-window
>   or clinical-readiness claim is made or implied for any agent, in any patient group, at any line of therapy.

**NEW (exact):**

> - **No new wet-lab work was performed by this synthesis.** There is no wet lab here, and this document holds
>   no experimental result of its own. ⛔ *Superseded, retained (2026-09-08, direct current-field correction):
>   "No wet-lab evidence exists. There is no wet lab."* The first clause was wrong as written and is
>   withdrawn: the primary sources discussed above ran their own experiments and report them, and nothing
>   here denies that evidence or its existence. What is true is narrower — this synthesis generated none of
>   it. No efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim is made or implied
>   for any agent, in any patient group, at any line of therapy.

**Why the old form was affirmative-before-caveat.** "No wet-lab evidence exists" is a categorical statement
about the world, placed ahead of the clause that was actually meant ("there is no wet lab" — here). Taken at
face value it denies the experiments in the primary sources this synthesis discusses and cites — Brenca
2019's engineered-construct and profiling work, Bangerter 2022's patient-derived models and drug validation —
which is both false and an over-claim in the opposite direction from the one the paper guards against. The
replacement makes the subject this synthesis, keeps the no-wet-lab-here fact, and does not overclaim in
either direction. The unchanged second sentence still forbids every efficacy, safety, selectivity and
clinical-readiness claim. The manuscript's own front-matter line ("**Preprint draft. No wet-lab work was
performed.**", stratification.md line 33) was already in the correct form and was not touched.

---

## What was NOT done

* No pinned key was repointed, restored or edited; the lint_consistency failure stands (see report).
* No new clinical statistic, source, figure, review, baseline, guard change or broad suite.
* `research/manuscripts/fusion-partner/emc-fusion-partner-correction-register.md` was NOT edited. Its entry
  **N14** is titled "from §3.5 · Partner prevalence — how many patients this would touch" and now names a
  section heading that no longer exists. That stale pointer is reported rather than repaired, because the
  register is a dated historical record and repairing it was not in this correction's scope.
