---
id: DOC-CHECKPOINT04-REGISTRY-PROSPECTIVE-SELECTION
title: Small independently selected registry outcome evaluation acquisition
level: cross-cutting
kind: memo
status: live
purpose: Freeze a source selection procedure before inspecting new outcome contexts or applying the family companion.
scope: One public API query capped at ten cancer studies with first results posted during September 2026; blinded outcome review preparation only.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

This plan is frozen before the source query. It is a post-development, prospectively selected small evaluation set, not a clinical validation study or independent clinical adjudication. The companion code is frozen at repository revision 52d63c2352d51181453049246ca306e9815f6e74. No companion predictions will be generated during acquisition.

Selection: make exactly one ClinicalTrials.gov v2 studies query with condition cancer, ResultsFirstPostDate RANGE[2026-09-01,2026-09-30], pageSize=10, sort NCTId:asc, JSON output. Request only IdentificationModule, StatusModule, ConditionsModule and OutcomeMeasuresModule. Save the raw response bytes with timestamp, URL and SHA256. Do not follow pagination, broaden dates, substitute trials or search by response criteria labels. Ascending NCT identifiers define the bounded order; this is a date-defined capped slice, not a claim to represent all oncology studies. Invalid query/access failure or a response exceeding 1 MiB terminates acquisition and is reported without an alternate outcome-driven search.

Compare selected study identifiers to all identifiers in the accepted 575-unit comparison (SHA256 f32fc2197608547889312264155dcc8ed77a4587feeb5a2d06413a297b6cc3a1). Retain overlapping records in the acquisition receipt but exclude them from independent evaluation, without replacement. Nonoverlap establishes study-level separation from those 575 units only, not proof that the study was absent from every historical raw retrieval pool or model development exposure.

Freeze all outcome indices of every remaining study before screening. Supply complete returned outcome objects, including groups, classes, categories, measurements, denominator and analysis fields, to a separate reviewer blind to companion output. Selection for response relevance is the reviewer's task: include outcomes reporting tumor/disease response or its categorical distribution; exclude unrelated symptom, laboratory or behavioral response measures, retaining an exclusion reason. Record absent outcomes and zero eligible response outcomes. Do not require an explicit criteria name, familiar vocabulary, complete category vector or likely classifier success.

Before running the companion, the separate reviewer must freeze an outcome-indexed oracle: eligible/excluded/uncertain with reasons; explicit family and version, modification and certainty (including absent/conflicting), exact supporting source spans; category literal roles only where justified; confirmation context; scope and denominator references. Unknown and ambiguity are valid oracle states. Reviewer source interpretation is not independent clinical adjudication, and no clinical response reconstruction is requested. Do not reveal companion outputs before this oracle is locked. Any disagreement resolution must preserve initial oracle and prediction versions.

Only after root accepts both this frozen source set and the independent oracle may a separate execution compare family attribution and exact literal/pointer/denominator preservation. Report each outcome and study, missing outcomes and exclusions, and agreement denominators explicitly. With at most ten studies and possibly no usable response outcomes, this is an exploratory external-to-575 check, not a stable accuracy estimate, held-out clinical validation or evidence of clinical safety. No new thresholds or classifier fixes are part of this checkpoint.

Primary documentation: https://clinicaltrials.gov/data-api/api and https://clinicaltrials.gov/data-api/about-api/study-data-structure (JavaScript shells in web text retrieval); https://clinicaltrials.gov/data-about-studies/csv-download documents ResultsFirstPostDate and LastUpdatePostDate names. NLM's March 19, 2024 API announcement https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html specifies REST/OpenAPI 3, JSON, ISO dates and CommonMark text. Query validity will be confirmed only by actual API response, not inferred from the inaccessible interactive reference. No browser automation or access-challenge bypass is used.
