---
id: DOC-FP-RESIDUAL-LIMITATIONS
title: "Residual limitations — what the narrowed FP paper still cannot support"
level: L4
kind: evidence
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Residual limitations

## 1 · Scientific claims the narrowed paper still cannot support

- **No predictive treatment interaction.** Every response contrast is confined to treated patients. There is
  no untreated comparator anywhere in this record, so the partner cannot be shown to modify treatment
  benefit at any denominator.
- **No unconditional response partition.** 0/3 versus 4/19 is conditional on all three reported TAF15
  patients sitting inside the 22 primary-endpoint-evaluable set; three of the exclusions between the 26
  treated and the 22 evaluable are unaccounted for in every retained source. The 0/2 versus 4/20 illustration
  addresses **one** of those exclusions under further assumptions and bounds nothing.
- **No response rate in verified EWSR1::NR4A3 patients.** Both comparator arms are labelled `non-TAF15`. A
  contrast against a trial-level verified EWSR1 arm does not exist in this synthesis.
- **No independent prognostic effect of the partner — and no absence of one.** The reported analyses
  establish neither. No partner coefficient, interval, event count, model specification or missing-data rule
  is available in any retained source, so model adequacy, precision and overfitting cannot be assessed at all.
- **No pooled prognostic magnitude.** The two-cohort pool is withdrawn as source-unverified. This is scoped
  absence, not a finding that Huang's published counts are wrong.
- **No equivalence and no null** on any endpoint. Non-significant post-hoc Fisher values on these
  denominators leave clinically substantial differences in either direction open.
- **No signed bias, of any kind.** Not follow-up bias, not competing-risk bias, not publication or referral
  selection, not molecular-ascertainment missingness. Mechanisms are stated as hypotheses; no net direction is
  identified.
- **No population prevalence.** 28/154 = 18.2 % is a conditional share among named-partner-assigned cases in
  four selected series. It is not an estimate for all EMC and does not size any clinical population.
- **No time-to-event quantity.** No hazard ratio, survival curve, common-horizon comparison or individual
  prognosis is derived, and none should be derived from this work.
- **No general partner independence of drug response.** Two models from two different patients and three
  validated agents bound an observation; they do not test partner dependence.
- **No clinical replication of the mechanism.** Brenca's engineered-construct and profiling results support a
  mechanistic hypothesis in the systems measured; the binding limitation is endpoint and design, not
  authorship.
- **Nothing is a census.** No systematic search was run, so every "only", "no source" and "first" reads
  within the reports this synthesis examined.
- **No wet-lab evidence exists. There is no wet lab.** No efficacy, safety, selectivity, therapeutic-window or
  clinical-readiness claim is made or implied for any agent, in any patient group, at any line of therapy.

## 2 · Source-level gaps that remain open

- **Huang 2023 full text and Table 1.** Unheld. Reopens only on an authentic retained original verified at
  cell, endpoint, denominator, follow-up and cause-of-death level. No source hunt was performed or admitted.
- **Stacchiotti 2019 (pazopanib) and Stacchiotti 2014 (sunitinib) full texts.** Unread; the response
  denominators rest on secondary provenance.
- **Paioli 2021 full text.** Unread; per-partner event counts and adjustment structure unknown.
- **Follow-up denominators for Huang, Lenz and Paioli.** UNKNOWN, and recorded as unknown rather than filled.
- **Paioli's five partner-unassigned cases of 67.** Unexplained by the abstract.
- **MSK / MSKCC overlap between Suemitsu 2025 and Agaram 2014.** Unresolved; nobody has checked.
- **Sjögren 2003's recruitment rule.** Not documented by the source. The partner-enrichment reading is an
  inference.
- **Bangerter's 40-compound inventory.** In a figure not retained here; its contents are unknown.

## 3 · Preserved historical limits — NOT reconstructed, NOT re-run, NOT declared stale

These four are preserved exactly as they stand. **Nothing in this batch reconstructs, repeats or supersedes
them, and none of them is characterised as stale.**

1. **The original test run: 107 failed / 75 passed** (`pytest-fp-checks-stdout.txt`, 350,742 bytes, complete
   output ending at line 4063). The returned five-module suite is **not green**. Its failure prefix is
   deleted-key errors raised before several mutations reach `--check`; that prefix does **not** establish that
   all 107 failures are stale bindings, and it does **not** establish that 107 independent scientific findings
   exist. This limit is now disclosed in the manuscript (§7) and the producer docstring, and **the FP guards
   were not rewritten** — that remains unadmitted.
2. **The non-zero tracked-tree result** (`pytest-fp-checks-summary.txt`, 4,451 bytes): a session-finish
   traceback from the tracked-tree guard naming
   `FO-pdf-production/evidence/76-FINAL-squashed-content-diff.txt`, ending `recorded PYTEST_EXIT=1`. The
   non-zero exit and the separate tracked-file-change observation both stand. That record alone does not
   attribute the change to a particular test or writer, and the unrelated tracked-file history is not reopened.
3. **The incomplete intermediate-hash demonstration** (`check-writes-nothing-demonstration.txt`, 792 bytes).
   It supports the recorded refusal (baseline OK/exit 0; after a stated prevalence-event perturbation,
   differing `analyses` and exit 1). It **does not print a pre-check hash of the already perturbed file**, so
   the two displayed hashes cannot by themselves demonstrate that check left the perturbed bytes unchanged,
   and no restoration command or hash is shown. **No such hash was invented, and the demonstration was not
   re-run.**
4. **The absent raw producer-exit sidecar.** No separate raw exit-status sidecar for the original author
   regeneration was present in the package. Its absence is recorded and **no sidecar was manufactured**. The
   one regeneration performed by *this* batch has its own separately measured exit, which is a **new**
   execution record and is never presented as a record of that earlier one.

## 4 · Process residuals from this batch

- **R8 is prepared and NOT applied.** The parent-owned `PUB-FUSION-PARTNER` entry still carries the withdrawn
  pool, magnitude, causal and novelty story. Until the patch lands, that shared claim **disagrees with this
  paper**. `systems/views/` regeneration follows the owner's application, not this author.
- **The candidate remains on scientific HOLD** as adjudicated; this batch implements the narrowing, it does
  not lift the hold. The original stronger prognostic/predictive formulation stays **PARKED**.
- **Guard maintenance is untouched and unadmitted.** The FP guards may now disagree with the corrected prose
  in ways this batch did not test and did not fix; no guard, floor, gate, matcher, pin or test was weakened,
  and no test sweep was run.
- **No new source acquisition, no network fetch, no denied-route retry, no new clinical statistic, no
  simulation, no biological producer run, no new baseline or independent review** was performed.
- **No pinned quantity changed, and `research/manuscripts/pinned-figures.json` was NOT edited.** The numeric
  comparison shows 0 changed and 0 removed numeric leaves, so nothing this batch did moves a pinned figure.
  ⚠ **Observed in passing, pre-existing, and NOT caused by this batch:** the three FP entries in that file
  (`fusion_partner_dod_fisher_p`, `fusion_partner_dod_taf15_percent`,
  `fusion_partner_dod_comparator_percent`) address
  `analyses.B_outcome_by_partner.disease_specific_death.*`, a path that resolves to MISSING in the artifact
  **both before and after** this batch — analysis B was restructured by the earlier F01–F12 repair and the
  live cells now sit under `.source_verified_recorded_outcomes.disease_specific_death`. The values themselves
  (42.9 % and 6.2 %) are unchanged. That file is outside this author's named files and was left untouched;
  it is reported here for the owner.
