#!/usr/bin/env python3
"""Pooled synthesis of published SYSTEMIC-THERAPY outcomes in advanced extraskeletal myxoid
chondrosarcoma (EMC), built only from integer counts printed in the sources.

WHY THIS EXISTS
---------------
"What does systemic therapy actually do in advanced EMC?" is the question a sarcoma clinician asks
about this disease, and no single publication answers it. The evidence is two prospective single-arm
cohorts, one arm of a randomised trial that mixed EMC with a different sarcoma, three retrospective
EMC series, one chondrosarcoma-wide TKI study whose EMC subgroup is three patients, and one
mixed-histology trial that shares its registration with one of the prospective cohorts. This script
puts every reported datapoint in one table, pools only what the repository's evidence contract
permits, and RECORDS EVERY EXCLUSION WITH ITS REASON.

Assembling it surfaced four figures that circulate as EMC results and are not: see
`corrections_to_the_repository_registry` in the output, and the superseded values registered in
research/data/emc-clinical-registry.json -> treatments.systemicEvidenceCorrections.

METHOD IS NOT NEGOTIABLE: systems/POLICY-evidence.md 2.1-2.4.
  * crude denominator-weighted proportions,
  * Wilson score 95% intervals,
  * explicit integer {events, denom} only - never counts back-derived from a published percentage,
  * non-overlapping populations only,
  * time-to-event endpoints (median PFS, median OS) are NEVER merged; they are carried per row.

WHAT THIS FILE IS NOT
---------------------
Not a treatment recommendation, and not capable of being one. Every pooled proportion here rests on
double-digit denominators at best; several rest on single digits. Where the interval is too wide to
exclude anything, the finding IS the width. See `where_the_evidence_is_too_thin`.

Regenerate:  python3 research/manuscripts/emc_systemic_therapy_pooling.py
Verify:      python3 research/manuscripts/emc_systemic_therapy_pooling.py --check
Output:      research/manuscripts/emc-systemic-therapy-pooling.json

⛔ `--check` WAS A PROMISE THIS FILE COULD NOT KEEP (found 2026-08-08). Until that day this module
parsed NO arguments at all: `--check` was accepted by the shell, ignored by the script, and the
artifact was OVERWRITTEN and the process exited 0 regardless. So the `_do_not_hand_edit` note below
-- "a hand edit will be silently overwritten" -- was false in the only direction that matters: a
hand edit to a POOLED CLINICAL PROPORTION persisted undetected until somebody happened to
regenerate, and nothing in CI ever did. A verify mode that regenerates its own reference and exits 0
is not a guard; it is the previous behaviour wearing a flag. `main()` now re-derives to memory,
compares against the committed artifact, and exits NON-ZERO on any difference -- and
`research/manuscripts/tests/test_emc_systemic_therapy_pooling_check.py` perturbs the REAL committed
artifact on disk and asserts the REAL `main(["--check"])` refuses it, because a guard exercised only
through a mock tests the mock (CLAUDE.md 6).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emc-systemic-therapy-pooling.json")

# --------------------------------------------------------------------------------------------
# Citations. Every entry carries >= 1 resolvable identifier and the ROUTE it was retrieved by,
# because two of them are not reachable from this sandbox at all (POLICY-evidence 1.2).
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# RETRIEVAL PROVENANCE. Every route tried for the one datapoint that had been recorded in this
# repository as "[unverified] - could not be retrieved", with the HTTP status each returned.
# Recorded as MEASUREMENTS rather than as prose, so a future session can see which doors are shut
# and which worked, instead of re-discovering it. Measured 2026-08-07 from a GitHub Actions runner
# (the dev sandbox egress proxy 403s these hosts at CONNECT, so none of this is reachable locally).
# --------------------------------------------------------------------------------------------
RETRIEVAL = {
    "target": ("IMMUNOSARC II EMC cohort effect size, J Clin Oncol 2025;43(16_suppl):11513, "
               "doi 10.1200/JCO.2025.43.16_suppl.11513"),
    "outcome": ("RETRIEVED IN FULL. Two independent aggregators served the abstract VERBATIM and "
                "agree token-for-token; a third indexed the same record and corroborates its "
                "existence, type and authorship without being used as a source of counts."),
    "measured_utc": "2026-08-07T16:39Z",
    "routes": [
        {"route": "https://ascopubs.org/doi/10.1200/JCO.2025.43.16_suppl.11513",
         "http": 403, "bytes": 16, "result": "refused"},
        {"route": "https://ascopubs.org/doi/full/10.1200/JCO.2025.43.16_suppl.11513",
         "http": 403, "bytes": 16, "result": "refused"},
        {"route": "https://ascopubs.org/doi/abs/10.1200/JCO.2025.43.16_suppl.11513",
         "http": 403, "bytes": 16, "result": "refused"},
        {"route": "https://doi.org/10.1200/JCO.2025.43.16_suppl.11513",
         "http": 403, "bytes": 16, "result": "refused - resolves to ascopubs and inherits its 403"},
        {"route": "Europe PMC REST search, DOI query", "http": 200,
         "result": "hitCount 0 - Europe PMC does not index this abstract"},
        {"route": "Europe PMC REST search, term IMMUNOSARC", "http": 200,
         "result": ("hitCount 67, none of which is the EMC cohort. The master trial's BONE "
                    "SARCOMA cohort (PMID 39540661) and CLEAR CELL SARCOMA cohort (PMID "
                    "41836677) are indexed as full papers; the EMC cohort is not.")},
        {"route": "NCBI eutils esearch, term IMMUNOSARC", "http": 200,
         "result": "3 PMIDs, none the EMC cohort"},
        {"route": "ClinicalTrials.gov API v2, NCT03277924", "http": 200,
         "result": ("record retrieved and confirms the trial's two-stage structure and the EMC "
                    "cohort's 6-month PFS primary endpoint, but hasResults: false - no effect "
                    "size is posted")},
        {"route": "EU Clinical Trials Register search", "http": 200,
         "result": "generic register page returned; no trial record extracted"},
        {"route": "https://meetings.asco.org/abstracts-presentations?query=IMMUNOSARC",
         "http": 200,
         "result": ("redirects to a JavaScript search shell with the query dropped; no abstract "
                    "content in the response")},
        {"route": "OpenAlex works?search=IMMUNOSARC", "http": 429, "result": "rate limited"},
        {"route": "Semantic Scholar paper/search?query=IMMUNOSARC", "http": 429,
         "result": "rate limited"},
        {"route": "https://api.crossref.org/works/10.1200/JCO.2025.43.16_suppl.11513",
         "http": 200, "bytes": 9397,
         "result": "SUCCESS - full publisher abstract in JATS, 2375 characters"},
        {"route": ("https://api.semanticscholar.org/graph/v1/paper/"
                   "DOI:10.1200/JCO.2025.43.16_suppl.11513"),
         "http": 200, "bytes": 4403,
         "result": "SUCCESS - same abstract, independently, plus the author list"},
        {"route": "https://api.openalex.org/works/doi:10.1200/...11513", "http": 200,
         "bytes": 27324,
         "result": ("SUCCESS - indexed as OpenAlex W4410800335, type 'conference-abstract', "
                    "venue Journal of Clinical Oncology, with an abstract_inverted_index present. "
                    "Corroborates the record; NOT used as a source of any count in this file, "
                    "because an inverted index has to be reconstructed and a reconstruction is "
                    "not a quotation.")},
    ],
    "raw_corpora": {
        "branch": "literature-cache",
        "slugs": [
            "literature/emc-systemic-therapy-2026-08-07 - 28 targets: the IMMUNOSARC II route "
            "sweep above plus the Europe PMC regimen searches; _manifest.json carries the HTTP "
            "status and byte count of every one",
            "literature/emc-systemic-p2b - open-access FULL TEXTS whose abstracts omit the "
            "counts: Chiusole 2020 (PMC7308468), Morioka 2016 (PMC4946242), the apatinib study "
            "(PMC7237692), plus the Drilon record",
            "literature/emc-systemic-p3 - the two primaries that had no identifier anywhere in "
            "this repository, resolved from Chiusole 2020's reference list and then confirmed "
            "against their own Europe PMC records",
        ],
        "why_kept": ("Every quote in this file's `quote` fields can be checked against these "
                     "without re-fetching anything, and three of the sources are behind "
                     "paywalls or hosts the dev sandbox cannot reach at all."),
    },
    "corroboration": (
        "The Crossref and Semantic Scholar abstracts are identical after whitespace "
        "normalisation apart from one HTML entity ('&gt;' vs '>'), 2375 vs 2372 characters. Two "
        "independent aggregators serving the same publisher deposit is the strongest "
        "verification available for a record whose publisher refuses direct access."),
    "lesson_for_future_lanes": (
        "A publisher 403 is not the end of a retrieval. Crossref carries deposited JATS abstracts "
        "for a large share of conference supplements, and Semantic Scholar and OpenAlex both "
        "mirror them - none of the three is blocked. This datapoint had been filed in this "
        "repository as '[unverified], the effect size could not be retrieved (ascopubs 403s; not "
        "indexed in Europe PMC)'. Both halves of that were true and the conclusion did not follow: "
        "the search had stopped at the two obvious doors."),
}

CITATIONS = {
    "stacchiotti2019pazopanib": {
        "short": "Stacchiotti 2019",
        "type": "journal-article",
        "title": ("Pazopanib for treatment of advanced extraskeletal myxoid chondrosarcoma: "
                  "a multicentre, single-arm, phase 2 trial"),
        "journal": "The Lancet Oncology",
        "year": 2019,
        "pmid": "31331701",
        "doi": "10.1016/S1470-2045(19)30319-5",
        "url": "https://europepmc.org/article/MED/31331701",
        "design": "single-arm, open-label, multicentre phase 2 trial",
        "registration": "NCT02066285",
        "studyPeriod": [2014, 2017],
        "population": ("adults with NR4A3-translocated, centrally confirmed, metastatic or "
                       "unresectable EMC with RECIST progression in the previous 6 months; "
                       "11 sites of the Spanish, Italian and French sarcoma groups"),
        "openAccess": False,
        "retrieved_via": "Europe PMC REST search (resultType=core) from a GitHub Actions runner",
        "verified": True,
    },
    "immunosarc2emc2025": {
        "short": "Hindi 2025 (ASCO abstract)",
        "type": "conference-abstract",
        "title": ("Phase II of sunitinib plus nivolumab in extraskeletal myxoid chondrosarcoma: "
                  "Results from the GEIS, ISG, and UCL IMMUNOSARC II Study"),
        "journal": "Journal of Clinical Oncology",
        "year": 2025,
        "volume": "43",
        "issue": "16_suppl",
        "page": "11513",
        "doi": "10.1200/JCO.2025.43.16_suppl.11513",
        "url": "https://doi.org/10.1200/JCO.2025.43.16_suppl.11513",
        "design": ("phase 2 histology-specific cohort inside a master trial "
                   "(IMMUNOSARC II, stage 2, EMC cohort)"),
        "registration": "NCT03277924",
        "studyPeriod": [2020, 2024],
        "population": ("adults with advanced, progressing, measurable, centrally confirmed EMC; "
                       "9 centres in Spain, Italy and the UK"),
        "openAccess": False,
        "retrieved_via": ("Crossref REST (JATS abstract) AND Semantic Scholar Graph API, "
                          "independently, after ascopubs.org returned HTTP 403 on all three "
                          "article routes and Europe PMC returned hitCount 0 for the DOI"),
        "evidence_tier": ("CONFERENCE ABSTRACT - not peer-reviewed in full, no published tables, "
                          "no supplementary data, and no results posted at ClinicalTrials.gov "
                          "(hasResults: false as read 2026-08-07). The sibling cohorts of the same "
                          "master trial (bone sarcoma, clear cell sarcoma) HAVE full papers; the "
                          "EMC cohort does not, and Europe PMC indexes no such paper."),
        "verified": True,
    },
    "morioka2016trabectedin": {
        "short": "Morioka 2016",
        "type": "journal-article",
        "title": ("Results of sub-analysis of a phase 2 study on trabectedin treatment for "
                  "extraskeletal myxoid chondrosarcoma and mesenchymal chondrosarcoma"),
        "journal": "BMC Cancer",
        "year": 2016,
        "pmid": "27418251",
        "pmcid": "PMC4946242",
        "doi": "10.1186/s12885-016-2511-y",
        "url": "https://europepmc.org/article/MED/27418251",
        "design": "sub-analysis of a randomised phase 2 trial (trabectedin vs best supportive care)",
        "registration": "JapicCTI-121850",
        "population": "subjects with EMCS OR MCS inside a translocation-related-sarcoma trial",
        "openAccess": True,
        "retrieved_via": "Europe PMC REST search (resultType=core)",
        "verified": True,
    },
    "chiusole2020": {
        "short": "Chiusole 2020",
        "type": "journal-article",
        "title": ("Extraskeletal Myxoid Chondrosarcoma: Clinical and Molecular Characteristics and "
                  "Outcomes of Patients Treated at Two Institutions"),
        "journal": "Frontiers in Oncology",
        "year": 2020,
        "pmid": "32612944",
        "pmcid": "PMC7308468",
        "doi": "10.3389/fonc.2020.00828",
        "url": "https://europepmc.org/article/MED/32612944",
        "design": "retrospective two-institution series (Istituto Oncologico Veneto; Gustave Roussy)",
        "studyPeriod": [1980, 2018],
        "openAccess": True,
        "retrieved_via": "Europe PMC REST search + fullTextXML",
        "verified": True,
    },
    "drilon2008": {
        "short": "Drilon 2008",
        "type": "journal-article",
        "title": ("Extraskeletal myxoid chondrosarcoma: a retrospective review from 2 referral "
                  "centers emphasizing long-term outcomes with surgery and chemotherapy"),
        "journal": "Cancer",
        "year": 2008,
        "pmid": "18951519",
        "pmcid": "PMC2779719",
        "doi": "10.1002/cncr.23978",
        "url": "https://europepmc.org/article/MED/18951519",
        "design": "retrospective two-referral-centre series",
        "studyPeriod": [1975, 2008],
        "openAccess": False,
        "retrieved_via": "Europe PMC REST search (resultType=core)",
        "verified": True,
    },
    "stacchiotti2014sunitinib": {
        "short": "Stacchiotti 2014 (sunitinib)",
        "type": "journal-article",
        "title": "Activity of sunitinib in extraskeletal myxoid chondrosarcoma",
        "journal": "European Journal of Cancer",
        "year": 2014,
        "volume": "50",
        "page": "1657-1664",
        "doi": "10.1016/j.ejca.2014.03.013",
        "url": "https://doi.org/10.1016/j.ejca.2014.03.013",
        "design": "retrospective series of consecutive patients treated with sunitinib 37.5 mg/day",
        "openAccess": False,
        "retrieved_via": ("IDENTIFIED from the reference list of Chiusole 2020's full text "
                          "(reference 13), which is also where its counts are read from. Until "
                          "2026-08-07 this study had NO identifier anywhere in this repository: "
                          "the registry row carrying its numbers named only 'sunitinib "
                          "retrospective series' and pointed at a review whose full text does not "
                          "contain the word 'sunitinib'."),
        "verified": False,
        "verified_note": ("The identifier and the bibliographic record are confirmed; the counts "
                          "below are read from Chiusole 2020's description of this study, not "
                          "from this paper itself, and are therefore marked provenance: "
                          "secondary (POLICY-evidence 1.3)."),
    },
    "stacchiotti2013anthracycline": {
        "short": "Stacchiotti 2013 (anthracycline)",
        "type": "journal-article",
        "title": ("Anthracycline-based chemotherapy in extraskeletal myxoid chondrosarcoma: "
                  "a retrospective study"),
        "journal": "Clinical Sarcoma Research",
        "year": 2013,
        "volume": "3",
        "page": "16",
        "doi": "10.1186/2045-3329-3-16",
        "url": "https://doi.org/10.1186/2045-3329-3-16",
        "design": "retrospective series of molecularly confirmed EMC",
        "openAccess": True,
        "retrieved_via": ("IDENTIFIED from the reference list of Chiusole 2020's full text "
                          "(reference 12). The registry row carrying its numbers previously named "
                          "only 'Stacchiotti et al. (Italian Rare Cancer Network)' - a phrase "
                          "that appears nowhere in the review it cited."),
        "verified": False,
        "verified_note": ("Bibliographic record confirmed; the counts below are read from the "
                          "Remiszewski 2025 review's description of this study, so the row is "
                          "provenance: secondary."),
    },
    "apatinib2020": {
        "short": "Liu 2020 (apatinib)",
        "type": "journal-article",
        "title": ("Apatinib for Treatment of Inoperable Metastatic or Locally Advanced "
                  "Chondrosarcoma: What We Can Learn About the Biological Behavior of "
                  "Chondrosarcoma from a Two-Center Study"),
        "journal": "Cancer Management and Research",
        "year": 2020,
        "pmid": "32547189",
        "pmcid": "PMC7237692",
        "doi": "10.2147/CMAR.S253201",
        "url": "https://europepmc.org/article/MED/32547189",
        "design": "retrospective two-centre study, ALL chondrosarcoma subtypes",
        "studyPeriod": [2009, 2019],
        "openAccess": True,
        "retrieved_via": "Europe PMC REST search + fullTextXML",
        "verified": True,
    },
    "martinbroto2020immunosarc1": {
        "short": "Martin-Broto 2020 (IMMUNOSARC I)",
        "type": "journal-article",
        "title": ("Nivolumab and sunitinib combination in advanced soft tissue sarcomas: "
                  "a multicenter, single-arm, phase Ib/II trial"),
        "journal": "Journal for ImmunoTherapy of Cancer",
        "year": 2020,
        "pmid": "33203665",
        "pmcid": "PMC7674086",
        "doi": "10.1136/jitc-2020-001561",
        "url": "https://europepmc.org/article/MED/33203665",
        "design": "single-arm phase Ib/II trial, mixed soft-tissue-sarcoma histologies",
        "registration": "NCT03277924",
        "studyPeriod": [2017, 2019],
        "openAccess": True,
        "retrieved_via": "Europe PMC REST search + fullTextXML",
        "verified": True,
    },
    "remiszewski2025": {
        "short": "Remiszewski 2025 (review)",
        "type": "journal-article",
        "title": ("From pathogenesis to the patient's bedside: a comprehensive review of "
                  "extraskeletal myxoid chondrosarcoma"),
        "journal": "Journal of Cancer Research and Clinical Oncology",
        "year": 2025,
        "pmid": "41055792",
        "pmcid": "PMC12504171",
        "doi": "10.1007/s00432-025-06316-5",
        "url": "https://europepmc.org/article/MED/41055792",
        "design": "narrative review",
        "openAccess": True,
        "retrieved_via": "Europe PMC full text already in the repository literature cache",
        "verified": True,
    },
}

# --------------------------------------------------------------------------------------------
# THE TABLE. One row per reported systemic-therapy experience in EMC.
#
# `orr_events` / `orr_denom` are RECIST objective responses (CR+PR) over the population the source
# says was evaluated for response. `dc_events` is CR+PR+SD over the same denominator.
# `pool_orr` decides membership of the pooled ORR; `pool_reason` is mandatory when it is False.
# `quote` is the sentence the counts were read from, so a future reader can check the extraction
# without re-fetching anything.
# --------------------------------------------------------------------------------------------
COHORTS = [
    # ---------------------------------------------------------------- prospective, central review
    {
        "key": "pazopanib_phase2",
        "regimen": "Pazopanib 800 mg/day",
        "regimen_class": "VEGFR-directed TKI",
        "design_tier": "prospective trial, central molecular confirmation",
        "line": "after anthracycline in most patients (progressive advanced disease)",
        "sourceId": "stacchiotti2019pazopanib",
        "provenance": "primary",
        "prospective": True,
        "n_started": 26,
        "n_mitt": 23,
        "orr_events": 4,
        "orr_denom": 22,
        "sd_events": 16,
        "pd_events": 2,
        "dc_events": 20,
        "median_pfs_months": 19.0,
        "median_pfs_ci": [11.0, 27.0],
        "median_pfs_is_emc_specific": True,
        "other_timepoints": {"PFS_12mo_pct": 74.0, "PFS_24mo_pct": 40.0,
                             "OS_12mo_pct": 96.0, "OS_24mo_pct": 90.0,
                             "median_followup_months": 27.0},
        "grade3_ae": {"hypertension": [9, 26], "ALT_increase": [6, 26], "AST_increase": [5, 26]},
        "pool_orr": True,
        "pool_dc": True,
        "quote": ("'26 patients entered the study and started pazopanib. Of these, 23 met the "
                  "eligibility criteria for the modified intention-to-treat analysis... 22 "
                  "patients (one patient died before the primary analysis) were evaluable for the "
                  "primary endpoint: four (18% [95% CI 1-36]) had a RECIST objective response.' "
                  "The 16 SD / 2 PD split and the median PFS of 19 months (95% CI 11-27) are read "
                  "from the Remiszewski 2025 review's account of the same trial; 4+16+2 = 22 "
                  "reproduces the trial's own denominator."),
        "correction_this_row_carries": (
            "THE RESPONSE DENOMINATOR IS 22, NOT 26. This trial has three different patient counts "
            "and the registry had attached the 18% response rate to the largest of them. 26 "
            "started pazopanib, 23 met modified-intention-to-treat criteria, and 22 were evaluable "
            "for the primary endpoint after one patient died before the analysis. 18% is 4 of 22. "
            "Quoting '18% of 26' understates the response rate and overstates the evidence base "
            "at the same time."),
    },
    {
        "key": "sunitinib_nivolumab_immunosarc2",
        "regimen": "Sunitinib 37.5 mg/day x14d then 25 mg/day + nivolumab 240 mg q2w",
        "regimen_class": "VEGFR-directed TKI + PD-1 inhibitor",
        "design_tier": "prospective trial, central pathology; CONFERENCE ABSTRACT ONLY",
        "line": "mixed; 13/24 (54%) treatment-naive",
        "sourceId": "immunosarc2emc2025",
        "provenance": "primary",
        "prospective": True,
        "n_started": 24,
        "orr_events": 2,
        "orr_denom": 23,
        "sd_events": 18,
        "pd_events": 2,
        "dc_events": 20,
        "pfs6_events": 16,
        "pfs6_denom": 23,
        "pfs6_km_pct": 77.0,
        "median_pfs_months": 13.2,
        "median_pfs_ci": [5.7, 20.7],
        "median_pfs_is_emc_specific": True,
        "other_timepoints": {"OS_12mo_pct": 90.0, "OS_12mo_ci": [77.0, 100.0],
                             "median_OS": "not reached", "median_followup_months": 18.0,
                             "metastatic_at_baseline": [22, 24], "treatment_naive": [13, 24]},
        "grade3_4_ae_pct": {"hypertension": 29.2, "ALT_increase": 16.7, "AST_increase": 12.5,
                            "bilirubin_increase": 12.5, "lymphocytopenia": 12.5},
        "pool_orr": True,
        "pool_dc": True,
        "quote": ("'Twenty-four pts were accrued from May 2020 to July 2024 in 9 centres... among "
                  "the 23 evaluable pts, 6m-PFSR was 77% with 16/23 pts free of progression at 6 "
                  "mos, and a median PFS of 13.2 mos (95%CI 5.7-20.7)... Two (9%) pts achieved a "
                  "RECIST 1.1 partial response while 18 (82%) and 2 pts (9%) showed a stable "
                  "disease and progresion as the best response respectively.'"),
        "internal_inconsistencies": [
            ("The primary endpoint is given BOTH as 77% and as 16/23 (= 69.6%). The likely "
             "reconciliation is a Kaplan-Meier estimate against a crude proportion, but the "
             "abstract does not say so and no full paper exists to check. POLICY-evidence 2.1 "
             "forbids pooling a count back-derived from a percentage, so the explicit 16/23 is "
             "what enters this file and the 77% is carried beside it."),
            ("The best-response counts sum to 22 (2 PR + 18 SD + 2 PD), not to the 23 evaluable "
             "patients, and the printed percentages (9%, 82%, 9%) are internally consistent ONLY "
             "with a denominator of 22 (18/22 = 82%; 18/23 = 78%). This file pools on the stated "
             "evaluable count of 23, the conservative choice, and reports n=22 as a sensitivity."),
        ],
    },
    {
        "key": "trabectedin_emc_subset",
        "regimen": "Trabectedin 1.5 mg/m2 q3w",
        "regimen_class": "cytotoxic chemotherapy",
        "design_tier": "randomised phase 2 trial arm, CENTRAL RADIOLOGY REVIEW",
        "line": "after failure of / intolerance to standard chemotherapy",
        "sourceId": "morioka2016trabectedin",
        "provenance": "primary",
        "prospective": True,
        "n_started": 2,
        "orr_events": 0,
        "orr_denom": 2,
        "sd_events": 2,
        "pd_events": 0,
        "dc_events": 2,
        "per_patient_emc": [
            {"subject": 1, "pfs_months": 13.0, "best_response": "SD",
             "change_in_sum_of_diameters_pct": -1, "os_months": 26.4, "off_for": "progression"},
            {"subject": 2, "pfs_months": 7.4, "best_response": "SD",
             "change_in_sum_of_diameters_pct": -27, "os_months": 10.4, "off_for": "progression"},
        ],
        "median_pfs_months": None,
        "median_pfs_is_emc_specific": False,
        "arm_wide_median_pfs_months": 12.5,
        "pool_orr": True,
        "pool_dc": True,
        "quote": ("Full text, Methods: 'we adopted TWO EMCS SUBJECTS and three MCS subjects who "
                  "had been allocated to the trabectedin group and three MCS subjects who had "
                  "been allocated to the BSC group.' Results: 'One subject with MCS (subject No. "
                  "3)... showed partial response (PR). The other subjects in the trabectedin "
                  "group (two with EMCS and two with MCS) showed stable disease (SD).' Table 2 "
                  "gives both EMC subjects individually: PFS 13.0 and 7.4 months, best response "
                  "SD and SD, overall survival 26.4 and 10.4 months."),
        "correction_this_row_carries": (
            "THE ARM IS NOT 5 EMC PATIENTS. It is 2 EMC and 3 mesenchymal chondrosarcoma, and the "
            "abstract's phrase 'five subjects with EMCS and MCS' has been read across this "
            "literature as five EMC patients. The full text's Methods section states the split "
            "explicitly, and Table 2 labels every subject. The single objective response in the "
            "arm was subject 3, an MCS patient, so the EMC-specific objective response count is "
            "0 of 2. "
            "AND THE ARM'S HEADLINE NUMBER COINCIDES WITH ONE MCS PATIENT'S OWN RESULT. The "
            "published 12.5 months (95% CI 7.4 to not reached) is the arm's Kaplan-Meier median "
            "over all five subjects. Table 2's five individual PFS values are 13.0, 7.4, 22.2, "
            "7.5 and 12.5 months - so the ordinary median of the five is also 12.5, and 12.5 is "
            "subject 5's own value, a mesenchymal chondrosarcoma patient. Either way the figure "
            "is a property of the mixed arm and not of its EMC patients, whose values are 13.0 "
            "and 7.4 months. It should not be quoted as trabectedin's median PFS in EMC."),
    },
    # ---------------------------------------------------------------- retrospective series
    {
        "key": "sunitinib_italian_named_use",
        "regimen": "Sunitinib 37.5 mg/day",
        "regimen_class": "VEGFR-directed TKI",
        "design_tier": "retrospective consecutive series, named-patient use",
        "line": "progressive metastatic disease",
        "sourceId": "stacchiotti2014sunitinib",
        "provenance": "secondary",
        "primaryRef": ("Stacchiotti S et al., Activity of sunitinib in extraskeletal myxoid "
                       "chondrosarcoma. Eur J Cancer 2014;50:1657-64, doi "
                       "10.1016/j.ejca.2014.03.013, PMID 24703573 - identified 2026-08-07 from "
                       "Chiusole 2020's reference list and confirmed against the Europe PMC "
                       "record"),
        "prospective": False,
        "n_started": 10,
        "orr_events": 6,
        "orr_denom": 10,
        "sd_events": 2,
        "pd_events": 2,
        "dc_events": 8,
        "median_pfs_months": None,
        "median_pfs_is_emc_specific": None,
        "median_followup_months": 8.5,
        "pool_orr": True,
        "pool_dc": True,
        "quote": ("'From July 2011, 10 patients with progressive metastatic translocated EMC have "
                  "been consecutively treated with sunitinib 37.5mg/day, on a named-use basis... "
                  "Eight of 10 patients are still on therapy. Six patients had a Response "
                  "Evaluation Criteria in Solid Tumours (RECIST) partial response (PR), two were "
                  "stable, two progressed... At a median follow-up of 8.5 months (range 2-28), no "
                  "secondary resistance was detected. Median progression free survival (PFS) has "
                  "not been reached.'"),
        "correction_this_row_carries": (
            "TWO DEFECTS, AND THE SECOND ONE HID THE FIRST. (1) THE 8.5 MONTHS IS THE MEDIAN "
            "FOLLOW-UP, NOT A MEDIAN PFS - this study's own words are 'Median progression free "
            "survival (PFS) has not been reached', so a follow-up duration was carried in this "
            "repository's registry as this regimen's progression-free survival, understating it "
            "by an unknown amount. (2) THE STUDY WAS CITED TO A REVIEW THAT NEVER MENTIONS IT: "
            "the registry pointed this row at Remiszewski 2025, whose full text contains the "
            "string 'sunitinib' ZERO times, with the primary named only as 'sunitinib "
            "retrospective series'. Because the pointer led nowhere, the median-PFS error could "
            "not be caught by following it - the study had to be found first, through reference "
            "13 of Chiusole 2020's full text, and then confirmed against its own Europe PMC "
            "record (Eur J Cancer 2014;50:1657-64, PMID 24703573). The RESPONSE figures were "
            "correct all along: 6 partial responses, 2 stable, 2 progressive in 10 patients."),
        "notable": ("'all responsive cases turned out to express the typical EWSR1-NR4A3 fusion, "
                    "while refractory cases carried the alternative TAF15-NR4A3 fusion... Among "
                    "putative sunitinib targets, only RET was expressed and activated in analysed "
                    "samples.' This is the highest response rate any regimen has recorded in EMC "
                    "and it is 6 responses in 10 patients on named-patient use without central "
                    "radiology review."),
    },
    {
        "key": "anthracycline_italian_rcn",
        "regimen": "Anthracycline-based chemotherapy (10/11 combined with ifosfamide)",
        "regimen_class": "cytotoxic chemotherapy",
        "design_tier": "retrospective series, central pathology review + molecular confirmation",
        "line": "front line in 10 of 11",
        "sourceId": "stacchiotti2013anthracycline",
        "provenance": "secondary",
        "primaryRef": ("Stacchiotti S et al., Anthracycline-based chemotherapy in extraskeletal "
                       "myxoid chondrosarcoma: a retrospective study. Clin Sarcoma Res 2013;3:16, "
                       "doi 10.1186/2045-3329-3-16, PMID 24345066, PMCID PMC3879193 - identified "
                       "2026-08-07 from Chiusole 2020's reference list and confirmed against the "
                       "Europe PMC record"),
        "prospective": False,
        "n_started": 11,
        "orr_events": 4,
        "orr_denom": 10,
        "sd_events": 3,
        "pd_events": 3,
        "dc_events": 7,
        "median_pfs_months": 8.0,
        "median_pfs_range": [2.0, 10.0],
        "median_pfs_is_emc_specific": True,
        "pool_orr": True,
        "pool_dc": True,
        "quote": ("'We retrospectively reviewed a series of 11 EMC patients treated as from 2001 "
                  "within the Italian Rare Cancer Network (RCN) with anthracycline-based "
                  "chemotherapy. Pathologic diagnosis was centrally reviewed in all cases and "
                  "confirmed by the presence of the specific chromosomal rearrangements... Ten "
                  "patients are evaluable for response. Overall, best response according to "
                  "RECIST was: partial response (PR) = 4 (40 %), stable disease (SD) = 3, "
                  "progressive disease (PD) = 3 cases. Median PFS was 8 (range 2-10) months.'"),
        "correction_this_row_carries": (
            "THE STUDY HAD NO IDENTIFIER IN THIS REPOSITORY AND NOW DOES. The registry row "
            "carrying these counts pointed at a review and named its primary only as 'Stacchiotti "
            "et al. (Italian Rare Cancer Network)' - a phrase that appears nowhere in that "
            "review. Following reference 12 of Chiusole 2020's full text resolves it to Clin "
            "Sarcoma Res 2013;3:16, PMID 24345066, PMCID PMC3879193, and the primary's own "
            "abstract confirms every figure. The old free-text reference was also right about the "
            "network, which this paper's Methods states directly. THE COUNTS WERE NEVER WRONG; "
            "THE POINTER WAS MISSING - and a number with no resolvable source is unauditable "
            "even when it is correct."),
    },
    {
        "key": "drilon_chemotherapy",
        "regimen": "Cytotoxic chemotherapy (mixed regimens, 32 evaluable courses)",
        "regimen_class": "cytotoxic chemotherapy",
        "design_tier": "retrospective two-referral-centre series, PHYSICIAN-ASSESSED response",
        "line": "unresectable disease, mixed lines",
        "sourceId": "drilon2008",
        "provenance": "primary",
        "prospective": False,
        "orr_events": 0,
        "orr_denom": 21,
        "dc_events": None,
        "median_ttp_on_chemo_months": 5.2,
        "median_pfs_months": None,
        "median_pfs_is_emc_specific": None,
        "pfs_rates_pct": {"3mo": 69.0, "4mo": 65.0, "6mo": 40.0, "9mo": 26.0},
        "pool_orr": True,
        "pool_dc": False,
        "pool_dc_reason": ("best-response categories are given only as percentages (SD >=6 months "
                           "in 25%, SD <6 months in 41%, progression in 34%) and none of the "
                           "three converts to an integer on either candidate denominator"),
        "quote": ("'Twenty-one patients received 32 evaluable courses of chemotherapy. No "
                  "significant radiologic or clinical responses were noted. The median time to "
                  "disease progression while receiving chemotherapy was 5.2 months. The best "
                  "physician-assessed response to chemotherapy was stable disease for at least 6 "
                  "months in 25% of patients, stable disease for <6 months in 41% of patients, "
                  "and disease progression in 34% of patients.'"),
        "caveat": ("Response here is PHYSICIAN-ASSESSED over patients treated between 1975 and "
                   "2008, not central RECIST review. It is included because a categorical "
                   "statement that no responses occurred, with a stated denominator, is an "
                   "extractable {0, 21} - but it is the weakest row in the table and it carries "
                   "the largest chemotherapy denominator, so it dominates the cytotoxic pool."),
        "correction_this_row_carries": (
            "THE 5.2 MONTHS BELONGS TO THIS STUDY, NOT TO CHIUSOLE 2020. This repository's "
            "registry carried 'median PFS 5.2 months' on its Chiusole row, and 5.2 months is "
            "Drilon's median time to disease progression on chemotherapy - Chiusole's own "
            "Discussion attributes it to Drilon by name. Two retrospective chemotherapy series "
            "had been merged into one row. ⚠ SUPERSEDED CLAUSE, RETAINED: this correction used to "
            "add 'Chiusole 2020 reports no such figure anywhere'. That was FALSE and it was the "
            "more damaging half of the sentence: Chiusole 2020 reports a median PFS of 9 months "
            "for first-line chemotherapy, twice (Results and Discussion), verified 2026-08-08 by "
            "Actions run 31276131242 across three independent acquisitions. The misattribution "
            "being corrected here was real; the null appended to it was not, and it removed the "
            "largest published EMC chemotherapy series' own median from this file for a year. See "
            "A5 -> ⛔_a_null_this_file_asserted_and_that_was_wrong."),
    },
    {
        "key": "apatinib_emc_subset",
        "regimen": "Apatinib",
        "regimen_class": "VEGFR-directed TKI",
        "design_tier": "retrospective two-centre study of ALL chondrosarcoma subtypes",
        "line": "inoperable metastatic or locally advanced, mixed lines",
        "sourceId": "apatinib2020",
        "provenance": "primary",
        "prospective": False,
        "n_emc": 3,
        "n_cohort_all_chondrosarcoma": 33,
        "orr_events": 1,
        "orr_denom": 3,
        "dc_events": None,
        "cohort_wide_orr": [6, 33],
        "cohort_wide_median_pfs_months": 12.4,
        "median_pfs_months": None,
        "median_pfs_is_emc_specific": False,
        "pool_orr": True,
        "pool_dc": False,
        "pool_dc_reason": "the per-subtype breakdown gives responses but not stable disease",
        "quote": ("'the ORR was significantly different according to histological subtype: 15.0% "
                  "for conventional CS (3/20), 25.0% for mesenchymal CS (1/4), 20.0% for "
                  "dedifferentiated CS (1/5), 0.0% for clear-cell CS (0/1), and 33.4% for myxoid "
                  "CS (1/3).'"),
        "correction_this_row_carries": (
            "THE EMC NUMBER IS 1 OF 3, NOT 6 OF 33. The registry carried this study's "
            "cohort-wide 18.2% response rate and 12.4-month median PFS as EMC evidence. Both "
            "describe 33 patients across five chondrosarcoma subtypes. The full text does give "
            "the EMC subgroup separately - 1 response in 3 patients - and that is the only EMC "
            "figure this study contains."),
    },
    # ---------------------------------------------------------------- excluded outright
    {
        "key": "immunosarc1_sts_cohort",
        "regimen": "Sunitinib + nivolumab",
        "regimen_class": "VEGFR-directed TKI + PD-1 inhibitor",
        "design_tier": "prospective phase Ib/II, MIXED soft-tissue-sarcoma histologies",
        "sourceId": "martinbroto2020immunosarc1",
        "provenance": "primary",
        "prospective": True,
        "n_cohort_all_sts": 68,
        "pfs6_km_pct": 48.0,
        "pfs6_ci": [41.0, 55.0],
        "orr_events": None,
        "orr_denom": None,
        "median_pfs_months": None,
        "median_pfs_is_emc_specific": False,
        "pool_orr": False,
        "pool_reason": "same_registration_as_immunosarc2_and_emc_subset_not_separately_reported",
        "pool_dc": False,
        "quote": ("'From May 2017 to April 2019, 68 patients were enrolled: 16 in phase Ib and 52 "
                  "in phase II... the 6-month progression-free survival rate was 48% (95% CI 41% "
                  "to 55%).' Trial registration number NCT03277924."),
        "why_excluded": (
            "IMMUNOSARC I and the IMMUNOSARC II EMC cohort are stage 1 and stage 2 of the SAME "
            "REGISTERED TRIAL, NCT03277924 - visible only in the registry record, whose brief "
            "summary reads 'Stage one has two cohorts (soft tissue sarcoma and bone sarcoma) and "
            "stage two has eight cohorts (DDCS, EMC, VS, SFT, CCS, ASPS, UPS, LMS and OS)'. The "
            "published 48% is the whole mixed-histology stage-1 cohort, not its EMC patients. "
            "The accrual windows (2017-2019 vs 2020-2024) do not overlap, so the two do not "
            "double-count patients - but a mixed-histology rate cannot enter an EMC pool."),
    },
]

# Series that report an EMC chemotherapy experience but no extractable {events, denom}.
# Kept visible: an unextractable count is a real limitation of the literature, not an absent study.
CONTEXT_ONLY = [
    {
        "key": "chiusole_metastatic_chemo",
        "sourceId": "chiusole2020",
        "regimen": "chemotherapy for metastatic disease",
        "n_treated_first_line": 20,
        "n_treated_second_line": 14,
        "disease_control_rates_as_published": {
            "first_line_all": [20, "50%"],
            "first_line_anthracycline_based": [11, "60%"],
            "first_line_oral_cyclophosphamide": [4, "25%"],
            "first_line_other": [5, "50%"],
            "second_line_all": [14, "46.1%"],
            "second_line_anthracycline_based": [3, "0%"],
            "second_line_trabectedin": [3, "66%"],
            "second_line_other": [7, "28.5%"],
            "second_line_pazopanib": [1, "100%"],
        },
        "reported": ("'Twenty patients received chemotherapy for metastatic disease; best "
                     "response was partial response with clinical benefit in 50% of patients. "
                     "Fourteen patients received a second line of chemotherapy, with 46.1% "
                     "disease control rate.' Table 3 gives disease-control rate by line and "
                     "regimen, with denominators."),
        "why_context_only": (
            "Table 3 reports DISEASE CONTROL RATES, not response counts, and several of them do "
            "not convert to integers on their stated denominators (60% of 11 = 6.6; 46.1% of 14 "
            "= 6.5, though 46.1% of 13 assessable = 6). POLICY-evidence 2.1 forbids "
            "reconstructing counts from percentages, so this series contributes context and not "
            "a pooled count - which is a pity, because it is the largest EMC chemotherapy "
            "experience published and it is the one that reports outcome by regimen."),
        "what_it_does_establish": (
            "Within one series, first-line disease control was 60% with anthracyclines and 25% "
            "with oral cyclophosphamide, and second-line anthracycline rechallenge controlled "
            "disease in none of 3. The authors' own conclusion is that 'chemotherapy did not "
            "impact survival in unselected patients' and that its apparent negative association "
            "with survival is confounded by indication."),
        # ⛔ ADDED 2026-08-08, CORRECTING A NULL THIS FILE ASSERTED TWICE. Until today this row --
        # and A5 below, and the registry -- stated that Chiusole 2020 reports NO median PFS for its
        # chemotherapy patients. It reports one, in two places, and it is EMC-specific. The counts
        # above are still not poolable (they are rates, POLICY-evidence 2.1); a median PFS is a
        # separate object that this series DOES print, so it belongs in A5.
        "median_pfs_months": 9.0,
        "median_pfs_is_emc_specific": True,
        "median_pfs_ci": None,
        "median_pfs_range": None,
        "median_pfs_population": ("patients receiving FIRST-LINE chemotherapy for metastatic "
                                  "disease (20 patients received first-line chemotherapy in this "
                                  "series). The paper does not print a confidence interval, a "
                                  "range, or the number at risk for this median."),
        "median_pfs_quote": (
            "Results, Survival Analysis: 'Median progression-free survival for patients receiving "
            "first-line chemotherapy was 9 months.' And again in the Discussion: 'In our study, we "
            "observed a progression-free survival time of 9 months, which is higher than what was "
            "reported by Drillon et al. in 2008 in 21 patients (5.2 months) and consistent with "
            "data reported in 2013 on the use of anthracyclines in 11 patients in the series by "
            "Stacchiotti et al. (12, 14) (8 months), but shorter than median progression-free "
            "survival achieved with Pazopanib in a recent phase II trial that enrolled 23 "
            "patients (19 months) (1).'"),
        "median_pfs_retrieved_via": (
            "Europe PMC full-text XML for PMC7308468 (HTTP 200), the PMC article HTML (HTTP 200) "
            "and the Frontiers publisher landing page for doi 10.3389/fonc.2020.00828 (HTTP 200) "
            "-- three independent acquisitions, each carrying both sentences. GitHub Actions run "
            "31276131242, corpus literature/chiusole2020-pfs-verify on the literature-cache "
            "branch, targets research/manuscripts/lit-targets-chiusole2020-pfs.json."),
        "⛔_why_this_was_missed_for_a_year": (
            "THE ABSTRACT DOES NOT CONTAIN IT. The PubMed record for PMID 32612944 was fetched in "
            "the same run (HTTP 200) and carries the abstract only; the string does not appear in "
            "it. The abstract reports median OVERALL survival (180 months overall, 76 months "
            "metastatic) and disease-control rates, and no PFS at all. A reading of the abstract "
            "therefore supports 'this paper reports no median PFS' exactly as strongly as the "
            "truth supports the opposite -- which is why an ABSENCE claim about a full text may "
            "never be made from an abstract. An absent reading is not a reading of absence."),
    },
]

# Single-patient reports. Excluded from every pool AS A CLASS, and named here so the exclusion is a
# recorded decision rather than a silence - several of these are the ONLY EMC evidence that exists
# for the agent involved, and a reader who does not find them here will assume they were missed.
SINGLE_PATIENT_REPORTS = {
    "policy": "excluded from every pooled proportion in this file",
    "reason": (
        "POLICY-evidence 2.5 names publication bias first among the stated limitations, and "
        "single-patient reports are where it bites hardest: a case report of an EMC patient who "
        "did NOT respond to a drug is almost never written, so pooling case reports would add "
        "numerators without their true denominators and would push every rate upward by an "
        "amount that cannot be estimated. This is a structural argument, not a judgement about "
        "any individual report."),
    "why_they_still_matter": (
        "For interferon-alpha and imatinib these ARE the entire EMC evidence base. Excluding "
        "them from a pool is correct; treating their absence from the pool as evidence of "
        "inactivity would be wrong, and it is the reading this note exists to block."),
    "examples_seen_in_this_retrieval": [
        {"agent": "Imatinib", "n": 1, "sourceHint": "PMID 34446510",
         "reported": ("a patient with EMC and a KIT exon 11 mutation 'has been on imatinib... for "
                      "3 years with stable disease' - stable disease, not an objective response, "
                      "despite the report's title")},
        {"agent": "Interferon-alpha-2b", "n": 1,
         "sourceHint": "Rubinger et al., via the Remiszewski 2025 review",
         "reported": ("'a significant and durable response... with disease control maintained for "
                      "16 months'; the review states this 'remains an isolated observation and no "
                      "consistent objective response rates have been reported in larger cohorts'")},
        {"agent": "Eribulin, doxorubicin, trabectedin in sequence", "n": 1,
         "sourceHint": "PMID 36636521",
         "reported": "a vulvar EMC treated through four sequential systemic lines"},
    ],
}



# --------------------------------------------------------------------------------------------
# Statistics. Wilson only - the repository's standard interval for a simple proportion
# (POLICY-evidence 2.2), matching research/modalities/hla_coverage.py::wilson.
# --------------------------------------------------------------------------------------------
def wilson(events: int, n: int, z: float = 1.96):
    """Wilson score 95% interval for a binomial proportion (events out of n)."""
    if n <= 0:
        return (None, None)
    p = events / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = p + z2 / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return (round((centre - half) / denom, 4), round((centre + half) / denom, 4))


def pct(x):
    return None if x is None else round(100.0 * x, 1)


def pooled(rows, ev_key, dn_key):
    """Crude denominator-weighted pool + Wilson CI + the per-row spread (POLICY-evidence 2.2)."""
    use = [r for r in rows if r.get(ev_key) is not None and r.get(dn_key)]
    if not use:
        return None
    ev = sum(r[ev_key] for r in use)
    dn = sum(r[dn_key] for r in use)
    lo, hi = wilson(ev, dn)
    per = {r["key"]: {"events": r[ev_key], "denom": r[dn_key],
                      "pct": pct(r[ev_key] / r[dn_key]),
                      "wilson_pct": [pct(v) for v in wilson(r[ev_key], r[dn_key])]}
           for r in use}
    rates = [r[ev_key] / r[dn_key] for r in use]
    return {
        "cohorts": [r["key"] for r in use],
        "n_cohorts": len(use),
        "events": ev,
        "denom": dn,
        "proportion_pct": pct(ev / dn),
        "wilson95_pct": [pct(lo), pct(hi)],
        "per_cohort": per,
        "between_cohort_range_pct": [pct(min(rates)), pct(max(rates))],
        "largest_cohort_share_of_denominator_pct": round(
            100.0 * max(r[dn_key] for r in use) / dn, 1),
    }


def _fourth_median_consequence(rows):
    """What admitting Chiusole's 9 months changes for the one modern prospective median.

    ⛔ THIS IS AN INTERVAL-CONTAINMENT READING, NOT A HYPOTHESIS TEST, AND THE DIFFERENCE IS THE
    POINT. No p-value is computed here, no p-value has ever been computed anywhere in this
    repository for this comparison, and none may be: POLICY-evidence 2.4 forbids merging
    time-anchored endpoints, and three of the four medians come with no dispersion the arithmetic
    of a test would need (Chiusole prints none at all; Stacchiotti 2013 prints an observed range,
    which is not a confidence interval). What CAN be said honestly is where each chemotherapy
    median falls relative to the interval the one modern prospective cohort actually published --
    so that is all that is said, and it is DERIVED from the rows rather than typed.

    ⚠ The direction matters and is easy to get backwards: admitting the fourth median does NOT
    flip anything. The comparator that was already there (8 months) was already inside the
    interval; the new one (9 months) is inside it too, and is the LARGER series. The change is
    that the chemotherapy side is now two concordant medians from 31 first-line patients instead
    of one from 11 -- which makes the modern cohort's separation from chemotherapy look LESS
    established, not more, and it was never established to begin with.
    """
    idx = {r["key"]: r for r in rows}
    ref = idx["sunitinib_nivolumab_immunosarc2"]
    lo, hi = ref["median_pfs_ci"]
    chemo = [r for r in rows
             if r.get("median_pfs_months") is not None and r.get("median_pfs_is_emc_specific")
             and r["key"] != ref["key"] and "chemo" in (r.get("regimen", "") + r["key"]).lower()]
    return {
        "reference": {
            "cohort": ref["key"], "median_pfs_months": ref["median_pfs_months"],
            "ci95": [lo, hi],
            "note": "the only EMC median PFS in this file that comes with a published 95% CI",
        },
        "chemotherapy_medians_read_against_that_interval": [
            {"cohort": r["key"], "median_pfs_months": r["median_pfs_months"],
             "inside_the_reference_ci95": bool(lo <= r["median_pfs_months"] <= hi),
             # ⚠ NAMED AS AN ARITHMETIC DIFFERENCE, NOT A "gap" OR AN "effect", because it is one:
             # a subtraction of two medians from unrandomised single-arm cohorts is not an effect
             # size and must never be quoted as one.
             "arithmetic_difference_of_the_two_medians_months": round(
                 ref["median_pfs_months"] - r["median_pfs_months"], 1),
             "dispersion_this_source_reports": (
                 "95% CI" if r.get("median_pfs_ci") else
                 "observed range only" if r.get("median_pfs_range") else "none")}
            for r in sorted(chemo, key=lambda x: x["median_pfs_months"])
        ],
        "⚠_a_5_point_2_appears_here_and_it_is_NOT_drilons": (
            "13.2 - 8.0 = 5.2, which collides numerically with Drilon 2008's median time to "
            "disease progression (5.2 months) named elsewhere in this file. They are unrelated "
            "quantities and the coincidence is exactly the kind of thing this file exists to stop: "
            "the subtraction below is an arithmetic difference between two cohorts' medians; "
            "Drilon's 5.2 is one cohort's own measured time-to-progression. Neither may be "
            "substituted for the other."),
        "⛔_this_is_not_a_significance_verdict": (
            "No test statistic and no p-value is produced here or anywhere else in this "
            "repository for this comparison. A reader looking for one should read this entry as "
            "the reason there is none: the endpoints are not mergeable under POLICY-evidence 2.4, "
            "two of the four medians carry no interval at all, the cohorts are single-arm and "
            "separated by two decades and two response-assessment standards, and Chiusole's own "
            "authors name restaging-interval bias in the paragraph the figure appears in."),
        "what_changed_on_2026_08_08": (
            "The chemotherapy side of this reading went from ONE median (8 months, 11 patients) "
            "to TWO (8 months in 11 patients, and 9 months in the 20 first-line patients of the "
            "largest published EMC chemotherapy series). Both sit inside the modern cohort's "
            "published interval, as the first one already did, so nothing that was significant "
            "becomes non-significant and nothing that was non-significant becomes significant - "
            "there was no verdict to flip. What is genuinely different is the WEIGHT on the "
            "chemotherapy side, which had been understated by the largest series in the "
            "literature because this file wrongly recorded that series as reporting no median."),
    }


def build():
    by_key = {c["key"]: c for c in COHORTS}

    def rows(*keys):
        return [by_key[k] for k in keys]

    # --- membership sets, each with a stated reason for its boundary --------------------------
    prospective = rows("pazopanib_phase2", "sunitinib_nivolumab_immunosarc2",
                       "trabectedin_emc_subset")
    cytotoxic = rows("drilon_chemotherapy", "anthracycline_italian_rcn",
                     "trabectedin_emc_subset")
    vegfr = rows("pazopanib_phase2", "sunitinib_italian_named_use",
                 "apatinib_emc_subset", "sunitinib_nivolumab_immunosarc2")
    dc_rows = rows("pazopanib_phase2", "sunitinib_nivolumab_immunosarc2",
                   "trabectedin_emc_subset")

    # Sensitivity: the IMMUNOSARC II best-response denominator read as 22 instead of 23.
    alt = json.loads(json.dumps(by_key["sunitinib_nivolumab_immunosarc2"]))
    alt["orr_denom"] = 22
    sens_rows = [by_key["pazopanib_phase2"], alt, by_key["trabectedin_emc_subset"]]

    analyses = {
        "_how_to_read_these": (
            "A1-A4 are FOUR VIEWS OF ONE TABLE, not four independent studies, and they must never "
            "be summed or averaged. Each pool is internally clean - within any one of them no "
            "patient can appear twice - but the same cohort appears in more than one: the "
            "pazopanib trial is in both the prospective view (A1) and the VEGFR-directed view "
            "(A3), and the trabectedin EMC subset is in both A1 and the cytotoxic view (A2). "
            "A1 answers 'what happens under a protocol', A2 and A3 answer 'what happens with this "
            "class of drug'. A7 states the one pool this file refuses to compute and why."),
        "A1_objective_response_prospective": {
            "headline": True,
            "question": ("Across every advanced-EMC patient ever evaluated for RECIST response "
                         "inside a PROSPECTIVE trial with central review, how often does the "
                         "tumour actually shrink enough to count as an objective response?"),
            "estimand": ("crude proportion of RECIST objective responses (CR+PR) per "
                         "response-evaluated patient, pooled across the three prospective EMC "
                         "cohorts that exist"),
            "pool": pooled(prospective, "orr_events", "orr_denom"),
            "why_these_three_may_be_pooled": (
                "Three different regimens, three different trials, three different accrual eras "
                "and three different countries or networks (Europe 2014-2017; Europe 2020-2024; "
                "Japan). Each patient contributes exactly one response evaluation to exactly one "
                "of them. All three used protocol-defined response assessment - the pazopanib "
                "trial with central molecular confirmation of diagnosis, the trabectedin arm with "
                "central radiology imaging review, IMMUNOSARC II with central pathology."),
            "residual_overlap_risk": (
                "NOT ZERO between the two European trials. Both recruited through the Spanish and "
                "Italian sarcoma groups, and the IMMUNOSARC II abstract states that 6 of 23 "
                "patients had received a prior antiangiogenic - a group that may include patients "
                "from the pazopanib trial. Such a patient would contribute two evaluations of two "
                "different drugs, which does not double-count an observation but does violate "
                "independence, so the interval below is very slightly narrower than it should be. "
                "No patient-level data is published with which to size the overlap."),
            "sensitivity_immunosarc2_denominator_22": pooled(sens_rows, "orr_events", "orr_denom"),
        },
        "A2_objective_response_cytotoxic_chemotherapy": {
            "question": "What does cytotoxic chemotherapy do to advanced EMC?",
            "pool": pooled(cytotoxic, "orr_events", "orr_denom"),
            "composition": (
                "Two retrospective series and one randomised-trial arm, on three continents: "
                "Drilon's 21 chemotherapy-treated patients at two US referral centres 1975-2008 "
                "(no responses), the Italian Rare Cancer Network's 10 evaluable "
                "anthracycline-treated patients (4 responses), and the 2 EMC subjects of the "
                "Japanese trabectedin arm (no responses)."),
            "the_pool_hides_a_real_disagreement": (
                "0 of 21, 4 of 10, 0 of 2. The Italian series is the only one of the three that "
                "recorded a single response, and it recorded four. It is also the only one with "
                "central pathology review AND molecular confirmation of every case, and the only "
                "one in which nearly every patient received anthracycline WITH ifosfamide (10 of "
                "11). Drilon's series spans 1975-2008 with physician-assessed response and mixed "
                "regimens. Whether the difference is the drug combination, the era, the response "
                "assessment or the case mix cannot be determined from published data."),
            "dominance": (
                "Drilon's 21 patients are two thirds of this pooled denominator, and they are the "
                "weakest-assessed row in the table. A pooled proportion that one row can move "
                "this far is a description of that row as much as of the disease."),
        },
        "A3_objective_response_vegfr_directed": {
            "question": ("What do VEGFR-directed tyrosine kinase inhibitors - the class this "
                         "disease's literature calls its most consistently active - actually "
                         "achieve?"),
            "pool": pooled(vegfr, "orr_events", "orr_denom"),
            "the_pool_hides_a_larger_disagreement": (
                "6 of 10 on sunitinib, 4 of 22 on pazopanib, 1 of 3 on apatinib, 2 of 23 on "
                "sunitinib plus nivolumab. The single highest response rate ever recorded in EMC "
                "and one of the lowest are both in this pool, and the highest comes from the "
                "smallest and least formally assessed series - 10 consecutive patients on "
                "named-patient use, no central radiology review, no protocol."),
            "population_overlap_warning": (
                "THE TWO ITALIAN SERIES MAY BE THE SAME PATIENTS. The anthracycline series (11 "
                "patients, Italian Rare Cancer Network, from 2001, all metastatic) sits in A2 and "
                "the sunitinib series (10 patients, from July 2011, progressive metastatic, "
                "named-patient use) sits here. They share a first author and a national network, "
                "and sunitinib is given in this disease AFTER chemotherapy fails - which is "
                "exactly the sequence that would put the same patient in both. Neither paper says "
                "whether any patient appears in the other. This is why A2 and A3 are reported "
                "separately and never summed: within each pool no patient can appear twice, but "
                "across them the same patient may appear once in each."),
        },
        "A4_disease_control": {
            "question": ("How often does systemic therapy at least HOLD advanced EMC still "
                         "(CR+PR+SD as best response)? In a disease this indolent this is the "
                         "endpoint that matters, and it is the one both modern trials were "
                         "designed around."),
            "pool": pooled(dc_rows, "dc_events", "orr_denom"),
            "by_class_where_the_source_reports_stable_disease": {
                "cytotoxic_chemotherapy": pooled(
                    [c for c in cytotoxic if c.get("pool_dc")], "dc_events", "orr_denom"),
                "vegfr_directed": pooled(
                    [c for c in vegfr if c.get("pool_dc")], "dc_events", "orr_denom"),
                "note": ("Two rows report responses but not stable disease and so appear in the "
                         "response pools and not here: Drilon's 21 chemotherapy patients (best "
                         "response is given only as percentages) and the apatinib EMC subgroup "
                         "(the per-subtype breakdown gives responses only). Dropping Drilon "
                         "removes the single largest cytotoxic denominator, so the cytotoxic "
                         "disease-control figure below rests on 12 patients and is not "
                         "comparable in weight to the response pool in A2."),
            },
            "interpretation_limit": (
                "Disease control as a best-response category has no comparator here. EMC is "
                "described throughout its own literature as indolent, so an unknown share of "
                "these stable diseases would have been stable untreated. All three trials "
                "required documented progression before entry, which is the design feature that "
                "partially protects against that reading - 'partially' being the honest word, "
                "since none of the three was randomised against no treatment."),
            "the_one_randomised_comparison_that_exists": (
                "In the Japanese trial, median PFS was 12.5 months in the trabectedin arm against "
                "1.0 months (95% CI 0.3-1.0) in the best-supportive-care arm - but the BSC arm "
                "was three MESENCHYMAL chondrosarcoma patients and contained no EMC at all, so it "
                "is not a comparator for anything in this file."),
        },
        "A5_time_to_event_never_pooled": {
            "policy": "systems/POLICY-evidence.md 2.4 - time-anchored endpoints are never merged.",
            "emc_specific_medians": [
                {"cohort": c["key"], "regimen": c["regimen"],
                 "median_pfs_months": c.get("median_pfs_months"),
                 # A 95% CI and an observed range are different objects and the sources report
                 # different ones; emitting both under one key would invent precision the
                 # retrospective row does not have.
                 "median_pfs_ci95": c.get("median_pfs_ci"),
                 "median_pfs_observed_range": c.get("median_pfs_range"),
                 # ⛔ THREE STATES, NOT TWO (2026-08-08). This used to be a binary: a CI, or
                 # "observed range". Adding the Chiusole median -- which the paper prints with NO
                 # dispersion at all -- would have made it read as an observed range that does not
                 # exist, i.e. this file inventing precision in the very field whose purpose is to
                 # stop that. `median_pfs_observed_range` is null beside it, so the two disagreed.
                 "dispersion_reported_as": ("95% confidence interval" if c.get("median_pfs_ci")
                                            else "observed range, not a confidence interval"
                                            if c.get("median_pfs_range")
                                            else "NONE REPORTED - the source prints this median "
                                                 "with no interval, no range and no number at "
                                                 "risk")}
                # ⛔ `COHORTS + CONTEXT_ONLY`, NOT `COHORTS` (2026-08-08). A row can be
                # context-only for its RESPONSE counts and still print a perfectly extractable
                # median PFS -- those are different objects with different extraction rules, and
                # reading over COHORTS alone silently dropped the largest published EMC
                # chemotherapy series' median from the one table that lists EMC medians.
                for c in COHORTS + CONTEXT_ONLY
                if c.get("median_pfs_months") is not None and c.get("median_pfs_is_emc_specific")
            ],
            "figures_that_are_NOT_emc_medians_but_circulate_as_such": [
                {"figure": "12.5 months", "attributed_to": "trabectedin in EMC",
                 "actually": ("the Kaplan-Meier median of a mixed EMC/mesenchymal-chondrosarcoma "
                              "arm of five, coinciding with the individual PFS of subject 5, who "
                              "has mesenchymal chondrosarcoma. The two EMC subjects' own values "
                              "are 13.0 and 7.4 months.")},
                {"figure": "12.4 months", "attributed_to": "apatinib in EMC",
                 "actually": "all 33 patients of a five-subtype chondrosarcoma cohort"},
                {"figure": "8.5 months", "attributed_to": "sunitinib in EMC",
                 "actually": ("the median FOLLOW-UP of the sunitinib series. That paper states "
                              "'Median progression free survival (PFS) has not been reached.'")},
                {"figure": "5.2 months", "attributed_to": "anthracycline +/- ifosfamide (Chiusole)",
                 "actually": ("Drilon's median time to disease progression on chemotherapy, which "
                              "Chiusole's own Discussion attributes to Drilon by name. Chiusole "
                              "2020's chemotherapy median PFS is 9 months, not 5.2 - it is listed "
                              "in emc_specific_medians above.")},
                {"figure": "48% 6-month PFS", "attributed_to": "sunitinib+nivolumab context",
                 "actually": "IMMUNOSARC I's whole mixed soft-tissue-sarcoma cohort"},
            ],
            "⛔_a_null_this_file_asserted_and_that_was_wrong": {
                "superseded_claim": ("'Chiusole 2020 reports no median PFS for its chemotherapy "
                                     "patients.' Carried here, in the Drilon correction row, and "
                                     "in research/data/emc-clinical-registry.json until "
                                     "2026-08-08."),
                "what_is_true": ("Chiusole 2020 reports a median progression-free survival of 9 "
                                 "months for patients receiving first-line chemotherapy, stated "
                                 "twice - once in Results (Survival Analysis) and once in the "
                                 "Discussion, where it is compared against Drilon's 5.2, "
                                 "Stacchiotti 2013's 8 and pazopanib's 19."),
                "how_it_was_verified": ("GitHub Actions run 31276131242: Europe PMC full-text "
                                        "XML, the PMC HTML and the Frontiers publisher landing "
                                        "page, three independent acquisitions at HTTP 200, each "
                                        "carrying both sentences. Corpus "
                                        "literature/chiusole2020-pfs-verify."),
                "how_it_happened": ("The abstract does not contain the figure. The PubMed record "
                                    "(PMID 32612944) was fetched in the same run and reports "
                                    "median OVERALL survival and disease-control rates only. The "
                                    "null was an abstract-level reading asserted about a full "
                                    "text."),
                "what_did_NOT_change": ("The 5.2-months correction stands and is unaffected: 5.2 "
                                        "is Drilon's median time to progression, this repository's "
                                        "registry had it on the Chiusole row, and Chiusole's own "
                                        "Discussion attributes it to Drilon. Two retrospective "
                                        "series had been merged into one row, and they still had "
                                        "been. Nothing pooled anywhere in this file moves: A5 "
                                        "merges no time-to-event endpoint, by policy."),
            },
            "note": (
                "The five figures listed immediately above are quoted in the EMC literature and "
                "in this repository's own registry as EMC results, and none of them is one. FOUR "
                "EMC median-PFS figures exist: 19 months on pazopanib, 13.2 months on sunitinib "
                "plus nivolumab, 9 months on first-line chemotherapy in the Chiusole series and 8 "
                "months on anthracycline-based chemotherapy - different lines of therapy in "
                "different eras, which is why they are listed here and not compared. (Superseded, "
                "retained: 'Only three EMC median-PFS figures exist', which omitted the Chiusole "
                "median on the strength of a null this file itself asserted wrongly.)"),
            "⚠_what_the_fourth_median_does_and_does_not_move": _fourth_median_consequence(
                COHORTS + CONTEXT_ONLY),
            "⚠_and_four_is_still_not_a_comparison": (
                "Adding a fourth median does not license ranking them. Two are single-arm "
                "prospective trials with central review, two are retrospective series in "
                "different eras with no central review and no stated interval; Chiusole's 9 "
                "months carries no confidence interval, no range and no number at risk, and its "
                "own authors describe restaging-interval bias in the same paragraph. POLICY-"
                "evidence 2.4 forbids merging them and nothing here compares them."),
        },
        "A6_six_month_progression_free": {
            "question": "The endpoint both modern EMC trials chose. Can it be pooled?",
            "answer": "No - there is only one EMC cohort that reports it as an integer count.",
            "why": (
                "The trabectedin arm's 100% 6-month progression-free rate is computed on the "
                "mixed EMC/MCS population; IMMUNOSARC I's 48% is all soft-tissue sarcoma; "
                "Drilon's 40% is a Kaplan-Meier rate with no count. A pool of one is not a pool."),
            "the_single_extractable_row": {
                "cohort": "sunitinib_nivolumab_immunosarc2",
                "events": 16, "denom": 23,
                "crude_pct": pct(16 / 23),
                "wilson95_pct": [pct(v) for v in wilson(16, 23)],
                "as_published_km_pct": 77.0,
                "trial_success_threshold": (
                    "the design required at least 15 of 22 patients progression-free at 6 months "
                    "(H0 = 50%, H1 = 80%, alpha 0.05, beta 0.10); 16 of 23 were"),
                "note": ("The crude proportion and the published rate differ by 7.4 percentage "
                         "points and the abstract does not reconcile them. Both are reported "
                         "here; only the count is pooled anywhere."),
            },
        },
        "A7_the_pool_that_is_refused": {
            "refused": "a single all-regimen 'systemic therapy in EMC' objective response rate",
            "arithmetic_if_taken": pooled(
                rows("pazopanib_phase2", "sunitinib_nivolumab_immunosarc2",
                     "trabectedin_emc_subset", "sunitinib_italian_named_use",
                     "anthracycline_italian_rcn", "drilon_chemotherapy",
                     "apatinib_emc_subset"), "orr_events", "orr_denom"),
            "why_it_is_refused": (
                "It would place the Italian anthracycline series and the Italian sunitinib series "
                "in the same denominator. Same first author, same national network, overlapping "
                "years, and a clinical sequence - chemotherapy first, then sunitinib on named use "
                "- that makes it likely rather than merely possible that patients appear in both. "
                "POLICY-evidence 2.3 calls counting the same patient twice the cardinal sin of "
                "pooling, and this is exactly the shape of it. The number is printed here so that "
                "nobody has to recompute it to see why it was not used, and it must not be "
                "quoted as an estimate."),
            "status": "context only - do not quote",
        },
    }

    findings = [
        ("OBJECTIVE RESPONSE IS RARE IN EMC UNDER EVERY PROSPECTIVE PROTOCOL EVER RUN, AND THIS "
         "IS THE FIRST POOLED ESTIMATE OF IT. Six objective responses across the 47 advanced-EMC "
         "patients ever evaluated inside a prospective trial with central review. No publication "
         "states this figure, because no publication combines the three trials."),
        ("BUT THOSE SAME PATIENTS ALMOST NEVER PROGRESS EITHER. Disease control was the best "
         "response in 42 of the same 47. The clinically meaningful signal in EMC is not tumour "
         "shrinkage but how long the disease sits still. THE TWO MODERN PROSPECTIVE TRIALS CHOSE "
         "DIFFERENT PRIMARY ENDPOINTS, SIX YEARS APART: the 2019 pazopanib trial's primary "
         "endpoint was the RECIST objective-response rate - its own verbatim quote in this file "
         "reads '22 patients (one patient died before the primary analysis) were evaluable for "
         "the primary endpoint: four (18% [95% CI 1-36]) had a RECIST objective response' (PMID "
         "31331701) - while the 2025 IMMUNOSARC II EMC cohort's was the 6-month progression-free "
         "rate (NCT03277924). The field did not settle on a progression-free endpoint; it "
         "CHANGED endpoints, with no argument written down in the literature for why. "
         "SUPERSEDED, RETAINED: 'which is why both modern trials chose 6-month PFS rather than "
         "response rate as their primary endpoint' - contradicted by this file's own quote of the "
         "2019 trial, and detected rather than remembered by "
         "emc_endpoint_discordance.D5_primary_endpoint_correction."),
        ("THE '12.5-MONTH MEDIAN PFS FOR TRABECTEDIN IN EMC' IS NOT AN EMC FIGURE, AND IT LANDS "
         "ON A PATIENT WHO DID NOT HAVE EMC. The trabectedin arm was 2 EMC and 3 mesenchymal "
         "chondrosarcoma, not 5 EMC - stated in the paper's own Methods, with Table 2 labelling "
         "every subject, so this required no inference, only reading past the abstract. Both EMC "
         "subjects had stable disease, with PFS of 13.0 and 7.4 months, and the arm's single "
         "objective response was an MCS patient. The published 12.5 months is the arm's "
         "Kaplan-Meier median across all five subjects and it coincides with subject 5's own PFS "
         "- also mesenchymal chondrosarcoma."),
        ("AND IT IS NOT AN ISOLATED SLIP - FIVE NAMED TIME-TO-EVENT FIGURES IN CIRCULATION FOR "
         "SYSTEMIC THERAPY IN EMC DESCRIBE A DIFFERENT POPULATION OR A DIFFERENT QUANTITY. "
         "Beyond the trabectedin median: the apatinib 12.4 months is 33 patients across five "
         "chondrosarcoma subtypes of whom 3 had EMC; the sunitinib '8.5 months median PFS' is "
         "that study's median FOLLOW-UP, in a paper whose own words are 'Median progression free "
         "survival (PFS) has not been reached'; the 5.2 months attached to one chemotherapy "
         "series is a different series' median time to progression; and IMMUNOSARC I's 48% "
         "6-month PFS is its whole mixed soft-tissue-sarcoma cohort. FOUR median-PFS "
         "figures in this literature are EMC medians: 19 months on pazopanib, 13.2 on sunitinib "
         "plus nivolumab, 9 on first-line chemotherapy in the Chiusole series and 8 on "
         "anthracycline-based chemotherapy - and those four are different lines of therapy in "
         "different eras, which is why this file lists them and does not compare them. "
         "⚠ SUPERSEDED, RETAINED: 'Only THREE median-PFS figures ... 19, 13.2, 8'. The fourth was "
         "missing because THIS FILE asserted that Chiusole 2020 reports no median PFS, an "
         "abstract-level null about a full text that the full text refutes twice over (verified "
         "2026-08-08, Actions run 31276131242). A sweep whose whole subject is figures that "
         "describe a different quantity than they are quoted for had itself produced one - which "
         "is the reason this correction is recorded here and not quietly folded in."),
        ("THE TWO HIGHEST-PROFILE EMC TKI RESULTS DISAGREE BY A FACTOR OF SEVEN AND NOTHING "
         "PUBLISHED CAN SETTLE IT. Sunitinib 6 of 10 versus sunitinib plus nivolumab 2 of 23, "
         "with pazopanib's 4 of 22 in between. The 6 of 10 comes from consecutive named-patient "
         "use without central radiology review; the 2 of 23 from a protocol trial with central "
         "pathology. Adding a PD-1 inhibitor to sunitinib is the one comparison the field would "
         "most want, and it is confounded with two decades, two designs and two response-"
         "assessment standards."),
        ("THE NEWEST PROSPECTIVE DATAPOINT IN THIS DISEASE IS A CONFERENCE ABSTRACT WITH TWO "
         "UNRECONCILED ARITHMETIC INCONSISTENCIES AND NO FULL PAPER. IMMUNOSARC II's EMC cohort "
         "reports its primary endpoint as both 77% and 16/23 (= 69.6%), and its best-response "
         "counts sum to 22 rather than the 23 patients it says were evaluable. Its sibling "
         "cohorts in the same master trial have full papers in Cancer and Cancer Communications; "
         "this one does not, Europe PMC indexes no such paper, and ClinicalTrials.gov has no "
         "posted results for NCT03277924."),
        ("THE LARGEST PUBLISHED EMC CHEMOTHERAPY EXPERIENCE CANNOT ENTER ANY POOL. Chiusole's 20 "
         "first-line and 14 second-line patients are reported as disease-control RATES by "
         "regimen, several of which do not convert to integers on their own denominators. It is "
         "the only series that reports outcome by regimen and line, and the evidence contract "
         "correctly refuses to reconstruct its counts."),
    ]

    thin = [
        ("NO RANDOMISED EVIDENCE EXISTS FOR ANY SYSTEMIC THERAPY IN EMC. All three prospective "
         "cohorts are single-arm or single-arm within a master protocol. The one randomised "
         "dataset that touches EMC randomised translocation-related sarcomas as a class, and its "
         "control arm contained three mesenchymal chondrosarcoma patients and no EMC. Nothing "
         "here can support a statement that any drug is better than another, or than none."),
        ("EVERY POOLED DENOMINATOR IN THIS FILE IS UNDER 60 PATIENTS, WORLDWIDE, EVER. The "
         "prospective objective-response interval spans a range that contains both 'this "
         "essentially does not happen' and 'this happens in a quarter of patients'. THAT WIDTH IS "
         "THE FINDING. It is not a provisional estimate awaiting a larger series; EMC's incidence "
         "is well under one per million and there is no larger series coming."),
        ("SINGLE-DIGIT DENOMINATORS CARRY REAL WEIGHT IN TWO OF THE POOLS. The EMC subset of the "
         "trabectedin arm is 2 patients and of the apatinib study is 3. Their Wilson intervals "
         "individually span almost the entire 0-100% range and say nothing on their own. They are "
         "included because excluding a real EMC observation for being small is its own bias, and "
         "flagged because a reader scanning the table will otherwise weigh them as rows."),
        ("ONE ROW DOMINATES THE CYTOTOXIC POOL AND IT IS THE WEAKEST-ASSESSED ROW IN THE TABLE. "
         "Drilon's 21 patients are two thirds of that denominator, their responses were "
         "physician-assessed rather than centrally reviewed, and they were treated between 1975 "
         "and 2008 with regimens that are not today's."),
        ("THE TWO ITALIAN SERIES MAY BE THE SAME PATIENTS AND NOTHING PUBLISHED SAYS. This is why "
         "no all-regimen pool is offered. It also means the field's two most-quoted "
         "single-institution EMC systemic-therapy results may not be independent evidence."),
        ("DISEASE CONTROL IN AN INDOLENT SARCOMA IS AN UNCALIBRATED ENDPOINT. 42 of 47 patients "
         "had disease control as best response, but with no randomised comparator and a natural "
         "history that includes years of stability, the share attributable to the drug is "
         "unknown. Requiring documented progression before entry helps and does not settle it."),
        ("THE ENDPOINT BOTH MODERN TRIALS CHOSE HAS EXACTLY ONE EXTRACTABLE EMC DATAPOINT. "
         "Everything else published under the name '6-month progression-free rate' in the EMC "
         "literature is computed on a population that is not EMC."),
        ("FUSION-PARTNER STRATIFICATION IS OBSERVED BUT NOT ESTABLISHED. The sunitinib series "
         "reports that all responders carried EWSR1::NR4A3 and refractory cases carried "
         "TAF15::NR4A3, and the pazopanib trial carried a prespecified exploratory signal in the "
         "same direction. Both are exploratory analyses in cohorts of 10 and 22. Nothing here "
         "supports selecting or excluding a patient from treatment by fusion partner."),
        ("NOTHING IN THIS FILE SUPPORTS A TREATMENT RECOMMENDATION, INCLUDING A NEGATIVE ONE. "
         "Sequencing, patient selection, and whether to treat an asymptomatic indolent metastatic "
         "EMC at all are decisions this evidence base cannot inform. It can say only what has "
         "been observed, in how many people, and with how much uncertainty."),
    ]

    corrections = [
        {"correction": c["key"], "regimen": c["regimen"], "sourceId": c["sourceId"],
         "detail": c["correction_this_row_carries"]}
        for c in COHORTS if c.get("correction_this_row_carries")
    ]

    doc = {
        "_schema": "emc-systemic-therapy-pooling/1",
        "_generated_by": "research/manuscripts/emc_systemic_therapy_pooling.py",
        "_generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_do_not_hand_edit": (
            "Every proportion and interval here is computed by the generator from the integer "
            "counts in its COHORTS table. To change a number, change the count in the script and "
            "regenerate - a hand edit will be silently overwritten and will not carry the quote "
            "the count was read from."),
        "title": ("What systemic therapy does in advanced extraskeletal myxoid chondrosarcoma: "
                  "a pooled synthesis of every published cohort with extractable counts"),
        "method": {
            "policy": "systems/POLICY-evidence.md sections 2.1-2.4",
            "pooling": "crude denominator-weighted proportions",
            "interval": "Wilson score 95%",
            "counts": "explicit integers only; never back-derived from a published percentage",
            "populations": "non-overlapping only; every exclusion recorded with its reason",
            "time_to_event": "never merged; carried per row",
            "heterogeneity": ("per-cohort rates and their range are reported beside every pool; "
                              "I-squared is deliberately not computed (POLICY-evidence 2.2)"),
        },
        "retrieval_provenance": RETRIEVAL,
        "citations": CITATIONS,
        "cohorts": COHORTS,
        "context_only_no_extractable_counts": CONTEXT_ONLY,
        "single_patient_reports_excluded_as_a_class": SINGLE_PATIENT_REPORTS,
        "analyses": analyses,
        "findings_no_source_states": findings,
        "where_the_evidence_is_too_thin": thin,
        "corrections_to_the_repository_registry": {
            "target": "research/data/emc-clinical-registry.json -> treatments.systemicEvidence",
            "superseded_values_are_registered_at":
                "research/data/emc-clinical-registry.json -> treatments.systemicEvidenceCorrections",
            "items": corrections,
        },
        "exclusions_ledger": [
            {"cohort": c["key"], "regimen": c["regimen"], "reason": c["pool_reason"],
             "explanation": c.get("why_excluded")}
            for c in COHORTS if not c.get("pool_orr")
        ] + [
            {"cohort": c["key"], "regimen": c["regimen"], "reason": "no_extractable_counts",
             "explanation": c["why_context_only"]}
            for c in CONTEXT_ONLY
        ] + [
            {"cohort": c["key"], "regimen": c["regimen"],
             "reason": "excluded_from_disease_control_pool_only",
             "explanation": c["pool_dc_reason"]}
            for c in COHORTS if c.get("pool_orr") and not c.get("pool_dc")
        ] + [
            {"cohort": "single_patient_reports", "regimen": "imatinib, interferon-alpha, eribulin",
             "reason": "case_report_publication_bias",
             "explanation": SINGLE_PATIENT_REPORTS["reason"],
             "see": "single_patient_reports_excluded_as_a_class"},
        ],
        "not_a_recommendation": (
            "This is a description of published observations and their uncertainty. It is not "
            "clinical advice, it does not rank treatments, and it must not be read as endorsing "
            "or discouraging any therapy. EMC care belongs with a specialist sarcoma centre."),
    }
    return doc


#: Keys whose value changes on every run and therefore cannot participate in a difference test.
#: Deliberately a NAMED SET rather than a prefix rule: `_schema`, `_generated_by` and
#: `_do_not_hand_edit` all start with an underscore and all MUST be compared, because editing them
#: is exactly the kind of drift this guard exists to catch.
_VOLATILE_TOP_LEVEL_KEYS = ("_generated_utc",)


def _comparable(doc):
    """`doc` minus the fields that differ between two correct runs. Everything else is compared."""
    return {k: v for k, v in doc.items() if k not in _VOLATILE_TOP_LEVEL_KEYS}


def check():
    """`0` if the committed artifact re-derives exactly, `1` otherwise. Never writes.

    ⛔ THE RE-DERIVATION GOES TO MEMORY, NOT TO `OUT`. The whole defect this replaces was a mode
    that regenerated the artifact and then found it identical -- a comparison of the generator
    against itself, which cannot fail. `build()` is pure over the module's COHORTS table, so the
    reference here never touches the file being judged.
    """
    if not os.path.exists(OUT):
        print(f"FAIL: {OUT} does not exist -- run the generator", file=sys.stderr)
        return 1
    try:
        with open(OUT, encoding="utf-8") as fh:
            committed = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {OUT} is not readable JSON ({exc})", file=sys.stderr)
        return 1

    built = build()
    if _comparable(committed) == _comparable(built):
        print("emc_systemic_therapy_pooling --check: OK "
              "(committed artifact reproduces from the generator's counts)")
        return 0

    # ⛔ A REFUSAL THAT CANNOT SAY WHAT IT REFUSED SENDS THE READER TO A 1,300-LINE DIFF. Name the
    # top-level sections that disagree; a pooled clinical proportion drifting is worth a pointer.
    c, b = _comparable(committed), _comparable(built)
    differing = sorted(set(c) ^ set(b)) + sorted(k for k in set(c) & set(b) if c[k] != b[k])
    print(f"FAIL: {OUT} differs from a fresh derivation. Regenerate it "
          f"(python3 research/manuscripts/emc_systemic_therapy_pooling.py).", file=sys.stderr)
    print("  differing top-level keys: %s" % ", ".join(differing), file=sys.stderr)
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pooled synthesis of published systemic-therapy "
                                             "outcomes in advanced EMC.")
    ap.add_argument("--check", action="store_true",
                    help="re-derive in memory and compare against the committed artifact; "
                         "exit 1 on any difference. Writes nothing.")
    args = ap.parse_args(argv)

    if args.check:
        return check()

    doc = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=True)
        fh.write("\n")
    a = doc["analyses"]
    print(f"wrote {OUT}")
    for name in ("A1_objective_response_prospective",
                 "A2_objective_response_cytotoxic_chemotherapy",
                 "A3_objective_response_vegfr_directed",
                 "A4_disease_control"):
        p = a[name].get("pool")
        print(f"  {name}: {p['events']}/{p['denom']} = {p['proportion_pct']}% "
              f"(Wilson 95% CI {p['wilson95_pct'][0]}-{p['wilson95_pct'][1]}%), "
              f"{p['n_cohorts']} cohorts, per-cohort range {p['between_cohort_range_pct']}%, "
              f"largest cohort = {p['largest_cohort_share_of_denominator_pct']}% of denominator")
    s = a["A1_objective_response_prospective"]["sensitivity_immunosarc2_denominator_22"]
    print(f"  A1 sensitivity (IMMUNOSARC II n=22): {s['events']}/{s['denom']} = "
          f"{s['proportion_pct']}% (Wilson {s['wilson95_pct']})")
    r = a["A6_six_month_progression_free"]["the_single_extractable_row"]
    print(f"  A6 6-month PFS: {r['events']}/{r['denom']} = {r['crude_pct']}% "
          f"(Wilson {r['wilson95_pct']}); published KM {r['as_published_km_pct']}%")
    ref = a["A7_the_pool_that_is_refused"]["arithmetic_if_taken"]
    print(f"  A7 REFUSED all-regimen pool (do not quote): {ref['events']}/{ref['denom']}")
    print(f"  registry corrections carried: "
          f"{len(doc['corrections_to_the_repository_registry']['items'])}")
    print(f"  exclusions recorded: {len(doc['exclusions_ledger'])}")
    return 0


if __name__ == "__main__":
    # ⛔ `sys.exit(main())`, never a bare `main()`. A verify mode whose failure cannot reach the
    # shell's exit status is not wired into anything, however correct its comparison is.
    sys.exit(main())
