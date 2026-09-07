---
id: DOC-ZURICH-ORDINAL-PROPOSAL-20260906
title: Proposed descriptive ordinal comparison
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Preserve source evidence, exact execution scope and limitations for the current research checkpoint.
scope: Reader metadata added at integration; scientific source body unchanged.
audience: [maintainers, autonomous research agents]
---

# Proposed ordinal compatibility pilot, frozen before NCC outcome matching

Date: 2026-09-06. Status: proposed bounded experiment, not a manuscript claim or completed analysis.

## New evidence

A previously untried, legitimate Europe PMC asset endpoint returned a 1,095,678-byte ZIP containing the actual Zurich 2023 figures and supplements:
https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/supplementaryFiles

Figure 5 is now visually inspected and transcribed in full: 17 chemotherapy-labelled rows and 23 targeted-agent rows, all in USZ20-EMC1. Forty ordinal response labels are retained, including 17 'none' labels. The image and Methods have explicit DOI provenance. Figure 6 is also preserved and visually inspected; no numeric point estimates were extracted. Source digests and the roster are frozen in zurich2023-ordinal-freeze.json. The roster remains single-reader pending independent validation. Neither this task's transcription script nor this proposed design opened NCC outcome values.

## Exact question and estimand

Do the published relative drug-response orderings agree between the USZ20-EMC1 screening figure and the independent NCC-EMC1-C1 screening table, across the complete identifiable common drug set?

Primary descriptive estimand: Kendall tau-b between Zurich's ordered source bands (none < low < moderate < good < high) and NCC's negative reported viability mean, retaining source ties. This estimates agreement of reported endpoint orderings only. It does not estimate a common-dose treatment effect, fusion-partner effect, clinical activity or causal reproducibility of resistance. No new numerical analysis has been run.

## What can run without correspondence

An independent reader can validate all 40 source labels and bands against the preserved image now. A second step can freeze a chemical-identity crosswalk against the NCC drug catalogue without opening outcomes: exact identity first, explicit salt-form handling, and unresolved labels left unresolved. These steps make a fully specified pilot reviewable without depending on replies.

The ordinal statistic is arithmetically computable after identity/label validation, but its interpretation must remain a reported-ranking comparison unless assay compatibility is established. The larger biological reproducibility question still requires the missing NCC assay details and clarification of Zurich's AUC-versus-viability description. This design is not permission to sidestep that restriction.

## Validation and sensitivity plan

- Independent transcription check of every row, five colour classes and boundaries. Flag AZD5153 at the yellow/orange transition for focused verification.
- Preserve source labels 'Abmaciclib' and 'WE-822' as printed/apparent; do not silently identify them as Abemaciclib or VE-822. Record any resolution before opening NCC outcomes.
- Freeze the complete common set before calculating agreement. Do not choose positive drugs or omit negative labels.
- Report the complete paired table with endpoint provenance and ties. Do not turn category boundaries into numeric AUC or viability point estimates.
- Report sensitivity to unresolved mappings/transcription states as a range of the descriptive statistic, not as biological uncertainty. No patient-level significance test or population generalization from one model per laboratory.
- If inferential uncertainty is later proposed, justify its unit: drugs are correlated by mechanism and are not independent EMC patients. A naive drug-wise bootstrap cannot support disease-level inference.

## Main scientific limitation and stop condition

The Zurich Methods use dose-response AUC across a drug-dependent dose grid, while Figure 5 labels five bands with viability percentages. NCC's fixed-assay conditions remain unrecovered. A drug ordering might therefore differ because of dose range, exposure, culture, processing, or patient biology. The source cannot presently separate those causes.

Stop the biological-concordance experiment if endpoint identity/assay compatibility cannot be resolved; retain the recovered dataset. Stop even the descriptive ranking pilot if independent source reading or chemical identity does not establish a common set spanning distinct response bands. Do not seek a new favourable overlap definition after seeing the statistic.

## Novelty and utility judgement

Recovering the full independent EMC response roster, including negatives, repairs an actual evidence gap and can identify which purportedly general model findings deserve matched follow-up. However, a single-model-per-study ordinal correlation alone is unlikely to justify a strong standalone paper. This is a concrete direct-EMC pilot with now-accessible source validation, not a promotion above the atlas or a claim that correspondence is unnecessary for the biological question.

## Retrieval note

The legacy NCBI oa.fcgi endpoint returned 404. Official documentation now states that the OA Web Service ended in August 2026: https://pmc.ncbi.nlm.nih.gov/tools/oa-service/ . No further retry is useful. The Europe PMC ZIP retrieval succeeded independently and did not bypass the publisher CAPTCHA.
