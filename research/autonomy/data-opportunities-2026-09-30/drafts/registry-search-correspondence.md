# Finding posted EMC outcomes beyond a condition query

A condition query can leave posted subtype results out of view. In two archived ClinicalTrials.gov responses, a query for extraskeletal myxoid chondrosarcoma (EMC) did not return a sarcoma trial that explicitly reports EMC outcomes. A shorter phrase entered through a different query parameter returned that trial. This example concerns the findability of existing evidence; it does not establish patient eligibility or treatment benefit.

We reanalysed two API responses retained in an EMC literature census.[1] Their retrieval is documented as 12 September 2026; all returned studies carry a versionHolder value of 11 September 2026. The queries were query.cond=extraskeletal myxoid chondrosarcoma and query.term="extraskeletal myxoid". We counted unique NCT identifiers, compared the returned study objects, and searched every string within each resultsSection for the case-insensitive phrase “extraskeletal myxoid”. We then read the additional record’s protocol and results, resolving cohort identifiers within each results module. No fresh registry search was performed.

| Archived query | Unique studies | hasResults=true | Studies with phrase in results |
|---|---:|---:|---:|
| query.cond=extraskeletal myxoid chondrosarcoma | 23 | 8 | 0 |
| query.term="extraskeletal myxoid" | 24 | 9 | 1 |

The condition-query set was a strict subset of the phrase-query set. All 23 shared study objects were identical. The sole additional record was NCT00642941, a phase II study of R1507 in recurrent or refractory sarcoma.[2] Its listed condition was only “Sarcoma”, whereas its study description, eligibility criteria, and posted results explicitly named EMC. This is a concrete discrepancy between the search result and the subtype evidence within the record.

The added record contains an explicitly labelled EMC cohort. Participant-flow group FG008, “Cohort 7c: Extraskeletal Myxoid Chondrosarcoma”, records 11 participants starting treatment. In the primary outcome, the same named cohort is group OG007. Its posted complete-or-partial response rate under World Health Organization criteria is 0%, with a denominator of 11 participants. These identifiers are local to their respective modules: linking FG008 to OG007 requires the cohort labels, rather than identical identifiers. The result is an existing clinical observation, not a therapeutic discovery from this audit. The registry posting and the related 2014 trial publication belong to the same trial family and must not be counted as independent evidence.[3]

The phrase scan returned 26 occurrences, all within R1507’s results. Repeated group titles and descriptions account for these occurrences; they are not 26 independent findings. The eight results-bearing records shared by both queries had no occurrence of the searched phrase in their results sections. That narrow string absence does not exclude EMC outcomes recorded through abbreviations, alternative labels, or unstratified results. Likewise, a trial’s eligibility mention alone cannot demonstrate that participants with EMC enrolled or contributed outcome data.

The comparison has a further limitation: both the query parameter and the wording changed. It therefore cannot isolate an effect of searching the condition field, quantify sensitivity or recall, or establish exhaustive registry coverage. The archived counts describe these two responses at one time. They do not show how either query performs today or across other rare cancers.

This case supports a practical safeguard for evidence synthesis: supplement a condition query with documented phrase and spelling searches, then inspect the retrieved records for actual subtype enrollment and outcomes. Sponsors and registries could also make explicitly reported subtype cohorts easier to find through consistent disease labels. The proposed remedy concerns the visibility of existing evidence. A broader, controlled query comparison would be needed to determine how often this discrepancy occurs and which search strategy resolves it.

## Data and code availability

The archived responses are cited below. Source hashes, record comparisons, phrase counts, and the cohort extraction are documented by the [reproduction script](../analysis/registry_search.mjs) and [machine-readable audit](../results/registry-search.json).

## References

1. ClinicalTrials.gov API. Archived discovery responses: [condition query](https://github.com/trimcrae/Rare-cancers/blob/af7211708205b5189d8c537c1ce2a23aa4bea076/research/literature/emc-census-2026-09-12/sources/clinicaltrials-discovery.json) and [phrase query](https://github.com/trimcrae/Rare-cancers/blob/af7211708205b5189d8c537c1ce2a23aa4bea076/research/literature/emc-census-2026-09-12/sources/clinicaltrials-fulltext-discovery.json). Retrieval documented as 12 September 2026.
2. ClinicalTrials.gov. A Study of R1507 in Participants With Recurrent or Refractory Sarcoma. [NCT00642941, posted results](https://clinicaltrials.gov/study/NCT00642941?tab=results). Numerical extraction uses the archived response in reference 1.
3. Related R1507 trial publication, 2014. [doi:10.1002/cncr.28728](https://doi.org/10.1002/cncr.28728).
