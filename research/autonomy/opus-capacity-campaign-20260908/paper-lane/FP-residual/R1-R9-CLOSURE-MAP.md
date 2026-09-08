---
id: DOC-FP-RESIDUAL-R1-R9-CLOSURE-MAP
title: "R1–R9 closure map — FP post-focused residual batch"
level: L4
kind: evidence
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# R1–R9 closure map

**Files.** M = `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md`;
J = `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` (**generated**, never hand-edited);
P = `research/manuscripts/emc_fusion_partner_pooling.py` (the producer — every J change was made here);
C = `research/manuscripts/fusion-partner/emc-fusion-partner-correction-register.md`;
G = `systems/graph/publications.json` (**parent-owned; patch prepared, NOT applied**).

Applied as ONE batch over the existing records, followed by **one** deterministic regeneration
(`checks/03-the-one-regeneration/`, exit 0).

---

## R1 — Huang provenance synchronised with the numerical quarantine

**Finding.** The numerical quarantine was real, but live fields still certified a human full-text read, 53
followed, a two-cohort pool, a `strata` node that no longer exists, a seven-death pool, and told future
readers not to treat the recurring 403 as the counts being unavailable.

**Edits.** P `citations.huang2023`: `population` loses the 53-followed clause and names the followed count
unknown; **new `verified_scope` field** marks verification as *identity and specified abstract content only*;
`verification_note` withdraws the human-read/second-cohort-ever certification outright and keeps the
2026-08-08 access measurement as dated history. P `cohorts[agaram-2014-outcome].pool_note` rewritten — one
cohort in the main event analysis, no "smaller of two". P `cohorts[suemitsu-2025-outcome].context_note` —
"3 of the 7 pooled TAF15 deaths" withdrawn; there is no seven-death pool. P `resolved_2026_08_08
.huang2023_full_text.now` moved back to **NOT RESOLVED**, retaining only the bot-block-versus-paywall access
diagnosis. P `retrieval_provenance`: key renamed from `the_one_source_not_read_from_the_cache` to
`every_count_on_this_page_is_read_from_a_retained_source`, and its instruction **reversed**. M §2 Methods:
verification scope qualified (primary full text for some series, primary abstract for others). C row **A54**.

**WITHDRAWN outright:** the human-fulltext-read certification; the 53-followed current metadata; the
two-cohort-now-pooled certification; the "second cohort ever" superlative; the instruction not to read a 403
as unavailability. **Qualified:** the 2026-08-08 Unpaywall/OpenAlex/403 measurement, retained as dated
history. **No withdrawn Huang cell was restored.**

**Open.** The full text and Table 1 remain unheld. Reopening requires an authentic retained original verified
at cell, endpoint, denominator, follow-up and cause-of-death level. No source hunt was performed.

---

## R2 — pazopanib 0/3 vs 4/19 labelled CONDITIONAL everywhere; Davis restored; truth-bounds withdrawn

**Finding.** The conditionality was explained in one §3.1 bullet and absent from the abstract, the table, the
artifact's contrast definitions and the verdict; live J fields denied Davis's eight-case typing; a
truth-bounds claim and a same-label-poolability claim stood.

**Edits — conditional label at every live site.** M Abstract (0/3 vs 4/19 named conditional at first
appearance, mixture inherits it); M §1.3 two-questions table; M §3.1 opening paragraph; M §3.1 **table
rebuilt with a per-row "what it is conditional on" column and drug-specific rows first**; M §5 claims.
P `analyses.A_tki_objective_response.primary_non_overlapping.definition`,
`.secondary_assume_independent.definition` and `.contrast` note, and `.verdict`.

**Edits — Davis.** P `citations.davis2017.verification_note` and
`cohorts[sunitinib-2012-two-cases].overlap_note` now record **eight EWSR1::NR4A3 cases as reported by a
secondary source**, with the 2012 report supplying the only primary typing (two of the eight). C row **A56**.

**WITHDRAWN outright:** "the truth lies between the two analyses" (P `overlap_sensitivity_bounds
.explanation`, M §3.1); "both comparator arms are non-TAF15 arms, **which is what makes them poolable**"
(P contrast note); "the magnitude is not established" (P verdict), replaced by the observed-versus-population
distinction; the claim that Davis does not type the eight. **Qualified:** the 0/2 vs 4/20 illustration now
states it addresses **one excluded death under further assumptions** and does not enumerate the other three
exclusions between 26 treated and 22 evaluable — M §3.1 and P `sensitivity_analyses...conclusion`. The stale
"NOT ACTED ON IN THIS FILE" registry note is corrected to **applied**. C row **A55**.

**Open.** The partner-by-analysis-population flow; patient-level enrolment evidence; primary sunitinib
patient-level typing. None was sought.

---

## R3 — size causation and the independent-negative-test story withdrawn

**Edits.** P `the_two_questions_this_page_answers.why_this_block_exists`; P
`cohorts[paioli-2021-outcome].published_p_values.note` and `.context_note`; P
`analyses.B_outcome_by_partner.separate_descriptive_context_not_pooled.huang-2023`; M §3.4 **retitled "The
reported prognostic analyses"** with its opening sentences replaced.

**WITHDRAWN outright:** "TAF15 patients die more often ... **probably because their tumours are bigger**";
"THE THIRD INDEPENDENT TEST OF THE PARTNER ... AND IT IS NEGATIVE AT THE CONVENTIONAL THRESHOLD"; "the same
pattern huang-2023-outcome's multivariable model shows"; the §3.4 opening claim that both series tested the
partner against size and neither reached significance; "at the death count a series of this size implies".

**Qualified:** Huang's **univariate** partner association and its **multivariable** result are now stated
separately; Paioli's DMFS endpoint is distinguished from Huang's disease-specific survival and its adjustment
structure is stated as unrecorded; model adequacy/precision/overfitting are stated as **unassessable** rather
than as inferred concerns. C row **A57**.

---

## R4 — signed bias, the two-cohort null and the random-effects impossibility withdrawn

**Edits.** P `cohorts[agaram-2014-outcome].follow_up_warning` **rewritten** to the bounded interpretation
already used in the repaired result block; P `cohorts[suemitsu-2025-outcome].context_note`; P
`method.not_used`; P `the_two_questions_this_page_answers.a_prognosis_by_partner`.

**WITHDRAWN outright:** the DOWNWARD-signed competing-risk bias on the recurrence and metastasis rows; "the
two-cohort null" and the reading built on it; "AND IT IS NULL" for Suemitsu; "a between-study variance is
**not estimable** at that scale, a tau-squared from these counts would be an **artefact**" — the categorical
assertion that stood beside its own disclaimer.

**Replaced with:** neither mechanism identifies a net direction or amount without event ordering and
comparable risk sets; there is no second numerical cohort and therefore no two-cohort null; Suemitsu is a
series **failing to establish** an association on its own endpoint; and the random-effects refusal is stated
as a descriptive-heterogeneity / interpretability judgement — the estimator is uninformative at this scale,
not impossible. The dangling pointer to the removed `metastasis_reading` node is redirected. C row **A58**.

**No additional Fisher, Wilson, survival or competing-risk calculation was performed.**

---

## R5 — molecular confirmation separated from named-partner identification

**Edits.** M §3.5 flow table rebuilt: confirmation column corrected to **26 / 58 / 12 / 67**, a
**followed-for-outcome column added and printed as *unknown*** for three series, per-series assay and result
definitions stated. P: **new `analyses.C_partner_prevalence.ascertainment_stages` block** carrying all four
stages, their definitions and per-series notes. P `analyses.C_partner_prevalence.verdict` and `.outlier_note`
narrowed. M §3.5 missingness paragraph and M §4.9 heading unsigned.

**WITHDRAWN outright:** the "molecularly characterised" column of 24/57/12/62; "that is the size of the
population any partner-stratified decision would move"; the §4.9 heading asserting that publication and
referral bias run in a direction favouring the hypothesis.

**Qualified:** "variant partners" made specific (missing TAF15 pushes the share down, missing other rare
partners pushes it up); selection mechanisms labelled **hypotheses**. **Preserved:** the named-partner
arithmetic 24/57/11/62 → 28/154 = 18.2 % (12.9–25.0), unchanged. **Huang's 53 was not reinstated.** Lenz's
closure is scoped to the count source only. C row **A59**; full mapping in `COUNT-MAP.md`.

**Structural/numeric-field change, documented:** 13 new numeric leaves, all inside `ascertainment_stages`.

---

## R6 — one series in the main event analysis, plus separately verified Sjögren context

**Edits.** M §3.3 **section title corrected** with an explicit supersession; M §3.2 rows for Agaram, Sjögren
and Llombart-Bosch; M §3.3 Sjögren bullet; M §3.5 exclusion paragraph; M §5; M Abstract. P
`analyses.B_outcome_by_partner._what_this_is`, `.what_is_not_established`, and a **new `⚠_roster_scope`
field** stating that the derived roster counts only objects carrying `endpoint: outcome_by_partner`, so
Sjögren's verified outcomes are outside that count by **schema**, not by evidence. P
`cohorts[sjogren-2003-prevalence].entry_route_per_patient` (both halves) and `.context_note`.

**WITHDRAWN outright:** "one source-verified series"; "the one cohort in this synthesis whose per-partner
outcome event counts are verified against a retained primary source"; "these four are in **because** their
fusion transcript had been reported"; "the five **freely admitted**"; "the same rule is applied to every
series in the table"; the unexplained-residue ground for excluding Llombart-Bosch (replaced by
congress-abstract-versus-peer-reviewed-report, since Paioli's residue is equally unexplained).

**Qualified:** partner-enrichment is labelled an **inference**; the roster count is a schema scope. **No
forced pooling or new sensitivity analysis.** C row **A60**.

---

## R7 — bounded Brenca/Bangerter reading carried into J and P

**Edits.** P `cohorts[bangerter-2022-exvivo]`: label corrected to *two patient-derived ex vivo models from
two **different** patients*, **new `⛔_not_a_matched_pair` field**, and the context note rewritten. P
`cohorts[brenca-2019-mechanism].context_note` rewritten. M §3.6, §3.7, §4.10 and the §3.2 mechanism/preclinical
rows.

**WITHDRAWN outright:** the "Matched patient-derived ex vivo pair" label; "NEITHER MODEL WAS TESTED AGAINST AN
ANTIANGIOGENIC TKI"; the general partner-independence conclusion; "context, not corroboration" and "the
mechanism is not an independent replication ... the same investigators explaining their own observation" as
grounds for dismissal.

**Replaced with:** two different patient models; a specified three-agent validation (carfilzomib, doxorubicin,
venetoclax), none an antiangiogenic TKI; four distinct issues kept apart — investigator independence,
patient/sample overlap, experimental replication (the source reports independent biological replicates), and
endpoint relevance, which is the binding limitation. **Author overlap alone no longer negates experimental
evidence.** **F07's live-analysis repair and the bounded GSE28866 score reading were not touched.** C row
**A61**.

---

## R8 — PUB-FUSION-PARTNER replacement PREPARED, NOT APPLIED

**Finding.** `systems/graph/publications.json` entry `PUB-FUSION-PARTNER` (line ~231) still carries the
withdrawn two-cohort 73-patient pool, the no-magnitude-at-any-denominator proposition, the
size-versus-biology explanation, "entire published experience" and the refutation of the 2020 review's
metastasis statement.

**Prepared, unapplied:** `patches/PUB-FUSION-PARTNER-current-claim-replacement.patch` (with
`patches/NOTE-PUB-FUSION-PARTNER.md`). It replaces `what_it_would_claim` and `outcome_potential_why` only, and
touches no other entry. Verified with `git apply --check`, exit 0 — `checks/05-r8-patch-apply-check/`.
`systems/graph/publications.json` is **byte-unchanged** (see `IDENTITIES.md`).

**⛔ NOT DONE BY THIS AUTHOR, BY INSTRUCTION:** applying the patch; the concurrent-ownership check; the
`systems/views/` regeneration that follows it. **No unrelated graph audit was performed.** C preamble records
that the shared entry still disagrees with the paper until the patch lands.

---

## R9 — references, dates, scopes, guard limitations, inactive falsifier

**Edits.** M references **[16]** and **[17]** rewritten from the retained primary metadata, with the
superseded entries retained inline. M §4.11: Agaram's **2000–2013 case-identification window** recorded and
the vintage-absent marking withdrawn; Paioli distinguished as *reported in the outcome section but not
numerically pooled*. M §4.2: "the entire response analysis" corrected. M §7: guard paragraph now discloses the
last retained run's **107 failed / 75 passed** and non-zero exit and that several mutations do not reach
`--check` in it; the "verified this session" reproduction claim is redated and bound to `checks/`. M §4.5:
"primary reports remain unread" → primary **full texts**. M §6 unread-documents table: column heading changed
from "what it holds" to the evidence that would resolve each question. P `retrieval_provenance
.not_retrievable` for Stacchiotti 2019 and Paioli 2021 likewise. P
`zero_death_patients_to_reconcile()` marked **INACTIVE / SUPERSEDED** at the function, historical docstring
retained verbatim beneath. P module docstring: the "nobody has pooled them" novelty claim withdrawn, and the
guard-scope disclosure added.

**⛔ No new threshold was calculated. The FP guards were not rewritten. The failing run was not
reconstructed, re-run or declared stale.** C row **A62**.

---

## Regeneration

ONE deterministic regeneration, after all M/P/C changes were in place:
`python3 research/manuscripts/emc_fusion_partner_pooling.py`, **measured exit 0**, empty stderr, full stdout
retained. Before/after identities in `IDENTITIES.md`; every attempt in `CHECK-RUN-RECORD.txt`.
