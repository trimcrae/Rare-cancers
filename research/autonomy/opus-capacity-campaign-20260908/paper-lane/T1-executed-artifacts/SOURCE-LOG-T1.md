# T1 source action log — verbatim results

Worker T1, 2026-09-08. Every source action taken in this lane, with the exact URL or query and the
response as returned. Nothing deleted.

## Inherited from parent (NOT repeated by T1)

1. `WebFetch https://clinicaltrials.gov/data-api/about-api/search-areas`
   -> `EGRESS_BLOCKED` — "Access to clinicaltrials.gov is blocked by the network egress proxy."
   MEASURED. T1 did not retry this host in any path or subdomain.
2. `WebSearch` for the API's search areas -> secondary sources stating `query.term` is a free-text
   search across all study fields including eligibility criteria.

## T1's own source actions

### S1 — WebSearch
Query: `ClinicalTrials.gov API v2 query.term search areas EligibilityCriteria free text fields covered`
Returned (result links): medium.com/@unicodeveloper/5-things-you-can-build-on-clinicaltrials-gov-in-an-afternoon-2cdd98eb2148;
apify.com/crawlerbros/clinicaltrialsgov-scraper; apify.com/pink_comic/clinicaltrials-gov-search;
dev.to/avabuildsdata/how-to-search-clinicaltrialsgov-programmatically-the-v2-api-is-actually-good-now-2i2a;
github.com/davila7/claude-code-templates/.../clinicaltrials-database/references/api_reference.md;
clinicaltrials.gov/data-api/api; arxiv.org/pdf/2309.07812; ncbi.nlm.nih.gov/pmc/articles/PMC6799800/
Search-engine summary, verbatim excerpts: "The query.term field searches everything, providing a
comprehensive free-text search across the ClinicalTrials.gov database." / "You can search by keyword
across all fields (drug names, conditions, descriptions). Additionally, the ClinicalTrials.gov API
lets developers access protocol data, trial status, locations, eligibility criteria, sponsor fields,
and posted results." / "For official API documentation with complete search area details, refer to
the ClinicalTrials.gov API documentation on Search Areas at
clinicaltrials.gov/data-api/about-api/search-areas."
GRADE: search-index level. The engine's own summary, not a document T1 read.

### S2 — WebFetch dev.to article
URL: `https://dev.to/avabuildsdata/how-to-search-clinicaltrialsgov-programmatically-the-v2-api-is-actually-good-now-2i2a`
Result VERBATIM: `{"error_type":"EGRESS_BLOCKED","domain":"dev.to","message":"Access to dev.to is blocked by the network egress proxy."}`
Branch stopped. Not routed around.

### S3 — WebFetch third-party API reference (reachable, secondary)
URL: `https://github.com/davila7/claude-code-templates/blob/main/cli-tool/components/skills/scientific/clinicaltrials-database/references/api_reference.md?plain=1`
Prompt: quote verbatim what it says about query.term, query.cond, search areas, eligibility criteria, `fields`.
Returned: `query.term` — "'General full-text search' is the only description provided for this
parameter." `query.cond` — "Disease or condition search". Search areas — "The document specifies
three distinct search parameters: query.cond (conditions), query.intr (interventions), and
query.term (general full-text). However, it does not explicitly state which text fields each
parameter searches or whether eligibility criteria text is included." Eligibility criteria — "The
file does not indicate whether eligibility criteria text is searchable via query.term or any other
parameter." `fields` — "This document contains no mention of a fields parameter."
GRADE: SECONDARY. A third-party skill-pack reference, not registry documentation. It is a NEGATIVE
result on the specific question.

### S4 — WebSearch
Query: `"BasicSearch" search area clinicaltrials.gov API v2 "EligibilityCriteria" weight area list query.term`
Search-engine summary, verbatim excerpts: "The ClinicalTrials API includes a 'get_search_areas'
endpoint that retrieves the mapping between search query parameters and their underlying data fields
with weights. Search area groups contain named areas (e.g. BasicSearch, ConditionSearch) that define
which data pieces are searched and their relative weight." / "The API exposes protocol data, trial
status, locations, eligibility criteria, sponsor fields, and posted results."
GRADE: search-index level. It names the MECHANISM that would settle the question (a search-areas
mapping, with BasicSearch as an area) but does NOT state BasicSearch's membership.

### S5 — WebFetch themineworks.com
URL: `https://themineworks.com/blog/clinicaltrials-scraper-tutorial/`
Result VERBATIM: `{"error_type":"EGRESS_BLOCKED","domain":"themineworks.com","message":"Access to themineworks.com is blocked by the network egress proxy."}`
Branch stopped.

### S6 — WebFetch medium.com
URL: `https://medium.com/@unicodeveloper/5-things-you-can-build-on-clinicaltrials-gov-in-an-afternoon-2cdd98eb2148`
Result VERBATIM: `{"error_type":"EGRESS_BLOCKED","domain":"medium.com","message":"Access to medium.com is blocked by the network egress proxy."}`
Branch stopped.

### S7 — PubMed (independent scholarship, not a mirror)
Query: `ClinicalTrials.gov API version 2 search retrieval query.term keyword search fields eligibility criteria`
Result VERBATIM: `{"pmids":[],"total_count":0,"returned_count":0,...,"has_more":false}`
A clean null: no indexed peer-reviewed description of this parameter's field coverage was found.

### R1 — route identified and DECLINED, not attempted
Third-party repositories and scraper products very likely hold a cached or re-published copy of the
blocked `search-areas` page or of the v2 OpenAPI specification. Reading such a copy to establish the
fact would be an alternative mirror chosen to evade a measured block, which this contract forbids.
T1 did not search for one and did not fetch one. Recorded as a deliberate non-action.

## Repository (read-only) actions
- read `research/manuscripts/care-delivery/emc-trial-reachability.md` (§2 table, §4, §5, §7)
- read `research/literature/emc-clinical-sweep-targets.json`, `-c3.json`, `-c4.json` (URL manifests)
- read `research/literature/emc-clinical-sweep-fulltext.json` (also a URL manifest, not payloads)
- grep for retained registry response payloads containing eligibility text: none retained.
