---
id: "DOC-DATA-OPPORTUNITIES-2026-09-30-DRAFTS-CLINICAL-AGGREGATE-AND-LOCAL-TREATMENT-SOURCE-APPENDIX"
title: "Clinical aggregate endpoints and local-treatment units: source qualification"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: Clinical aggregate endpoints and local-treatment units: source qualification."
scope: "September 30 measured-data campaign; retain the source qualifications, execution boundaries and historical status stated in the body."
audience: ["maintainers","external reviewers"]
date: "2026-09-30"
last_verified: "unverified"
_backfilled: "true"
---

# Clinical aggregate endpoints and local-treatment units: source qualification

This supporting note covers the locoregional-treatment and mortality-mechanism routes. The completed source calculations do not supply comparative treatment efficacy or a new cause-of-death mechanism.

The audited mortality report describes a full cohort of 171 patients. Its printed terminal-status groups represent 163 of those patients: 134 operated patients with localized disease and 29 patients metastatic at diagnosis. Eight localized patients who did not undergo surgery are outside those represented status groups. The 171 and 163 denominators therefore describe a full cohort and a reported subset within the same study, rather than independent cohorts. We retain that distinction and the source's endpoint definitions. Descriptive proportions or bounds from these totals do not identify event times, competing-risk incidence or a causal chain from primary treatment to disease death. No patient-level cumulative-incidence function or partner-adjusted survival estimate can be reconstructed from totals alone.

The identified stereotactic ablative radiotherapy (SABR) report describes one woman with metastatic EMC treated on several occasions with surgery or stereotactic radiotherapy; the high-dose-rate (HDR) brachytherapy report describes one 87-year-old woman treated with palliative interstitial brachytherapy. Their complete primary texts were acquired as SHA-verified XMLs. Multiple lesions, treatment fractions or repeated response observations do not create independent patients. These reports document clinical observations but provide no randomized or matched comparator, transferable selection rule or population treatment-effect estimate. A whole-lung-radiotherapy source returned only a short publisher landing page, so it was not treated as acquired full primary evidence.

The printed first-line anthracycline and trabectedin records were analyzed separately in the [patient-table/curve-concordance correspondence](printed-patient-tables-and-survival-reconstruction-correspondence.md), preserving histology and censoring distinctions. Mixed EMC and mesenchymal-chondrosarcoma records were not merged into a comparative EMC treatment cohort. The unavailable individual records for the mortality question are a source limitation; requesting them or obtaining a qualified new release would be new work.

The [primary mortality/anthracycline/trabectedin source audit](../deep-analysis/results/clinical-and-ASO-primary-supplements.json) preserves source receipts, extracted tables, availability statements and access failures. The [complete clinical-case and primary-source follow-up](../deep-analysis/results/clinical-case-and-primary-source-followup-final.json) retains the SABR and HDR texts, hashes, paragraphs and source qualification recovered from the original successful [run 36880897541, job 110432170246](https://github.com/trimcrae/Rare-cancers/actions/runs/36880897541/job/110432170246). These completed checks support source qualification, not a new treatment ceiling, mortality mechanism or independently publishable local-treatment efficacy analysis.

Primary case sources: [Timon et al., doi:10.1159/000548238](https://doi.org/10.1159/000548238) ([PMC12659415](https://pmc.ncbi.nlm.nih.gov/articles/PMC12659415/)); [Takagawa et al., doi:10.5114/jcb.2022.115161](https://doi.org/10.5114/jcb.2022.115161) ([PMC9044308](https://pmc.ncbi.nlm.nih.gov/articles/PMC9044308/)).
