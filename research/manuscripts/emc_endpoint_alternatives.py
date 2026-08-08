#!/usr/bin/env python3
"""If objective response is the wrong endpoint for advanced extraskeletal myxoid chondrosarcoma
(EMC), what is the right one -- and how would the published trial record read under it?

WHY THIS EXISTS
---------------
`emc-response-endpoint-paper.md` (PUB-ENDPOINT) establishes, on 47 patients, that objective response
and disease control sit 76.6 percentage points apart in advanced EMC, and it deliberately stops
there: its Sec. 6.6 says in its own words that it "does NOT propose a specific replacement endpoint,
because the data that would let anyone compare candidate endpoints on these patients has not been
published", and its Sec. 6.1 names the confound that would sink any such proposal -- stable disease in
an indolent tumour may be natural history. This file answers the two questions that leaves open:

  (A) what outcome variable SHOULD be tracked in advanced EMC, and
  (B) how would the published trial record read differently if that variable had been used?

and it settles one specific, previously-unasked question that turns out to decide (B):

  ⭐ THE 2025 EMC COHORT'S PRIMARY ENDPOINT WAS A 6-MONTH PROGRESSION-FREE RATE TESTED AGAINST A NULL
     OF 50%. WHERE DID 50% COME FROM, AND IS IT AN EMC-APPROPRIATE NULL?

  The prior hypothesis this file was written to test was that the null came from the Van Glabbeke /
  EORTC soft-tissue-sarcoma progression-free-rate reference values, which are derived from aggressive
  histologies, and would therefore be cleared by an indolent tumour's natural history alone. THAT
  HYPOTHESIS IS NOT WHAT THE RECORD SHOWS, and the corrected finding is sharper -- see
  `E3_benchmark_provenance`. The Van Glabbeke chain is real but leads somewhere else; the null
  coincides exactly with an EMC-specific published figure; and the appropriateness problem survives
  in a different and more damaging form, because every candidate benchmark of either provenance is
  measured on patients receiving chemotherapy and none is measured on untreated disease.

⛔ WHAT THIS FILE ASSERTS ABOUT DRUGS: NOTHING. It contains no efficacy, potency, safety,
therapeutic-window or clinical-readiness statement about sunitinib, nivolumab, pazopanib,
anthracyclines, trabectedin, apatinib or any other agent, and no treatment recommendation of any
kind, including a negative one. Every quantity below is a property of a MEASURING INSTRUMENT -- an
endpoint, a null hypothesis, a design's operating characteristics, or the completeness of a report.
Where a trial's published conclusion is shown to depend on its choice of null, that is a statement
about the null, never about whether the treatment worked.

WHERE THE NUMBERS COME FROM
---------------------------
Two kinds of input, kept apart on purpose:

  1. COMMITTED ARTIFACTS, read at run time and never re-typed:
       research/manuscripts/emc-systemic-therapy-pooling.json   (integer counts, medians, citations)
       research/manuscripts/emc-endpoint-discordance.json       (the D3 reporting census, D5)
     These own their numbers. This file reads them; it does not become a second home for them.

  2. RETRIEVED CONSTANTS, each carried below with its VERBATIM QUOTE and the exact corpus file it was
     read out of on the `literature-cache` branch. They are values that existed in no committed
     artifact in this repository before 2026-08-08 -- the two trials' design parameters, the Van
     Glabbeke reference values, and the two published EMC-specific 6-month progression-free rates.
     ⚠ EVERY ONE OF THEM WAS FETCHED, NOT RECALLED. CLAUDE.md Sec. 7 records an agent writing a PMID
     from memory that passed two gates; the retrieval corpus for this file is
     `research/manuscripts/lit-targets-endpoint-benchmarks.json`, its outputs are on the
     `literature-cache` branch under `literature/emc-endpoint-benchmarks{,-r2}/`, and no identifier
     or figure in this file was written down without being read out of one of those files first.

METHOD: systems/POLICY-evidence.md 2.1-2.4 where a proportion is pooled (crude denominator-weighted,
Wilson score 95%, explicit integers only, non-overlapping populations, time-to-event never merged).
Where this file does something the policy does not cover -- exact binomial design arithmetic, and an
exponential conversion between a median and a fixed-timepoint rate -- the assumption is named, and
the conversion is VALIDATED against the three EMC cohorts that publish both quantities
(`E2_emc_six_month_progression_free_ladder.conversion_validation`) rather than assumed.

Regenerate:  python3 research/manuscripts/emc_endpoint_alternatives.py
Verify:      python3 research/manuscripts/emc_endpoint_alternatives.py --check
Output:      research/manuscripts/emc-endpoint-alternatives.json
Read by:     research/manuscripts/emc-endpoint-alternatives-2026-08-08.md
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
POOLING = os.path.join(HERE, "emc-systemic-therapy-pooling.json")
DISCORDANCE = os.path.join(HERE, "emc-endpoint-discordance.json")
OUT = os.path.join(HERE, "emc-endpoint-alternatives.json")

POOLING_REL = "research/manuscripts/emc-systemic-therapy-pooling.json"
DISCORDANCE_REL = "research/manuscripts/emc-endpoint-discordance.json"
CORPUS_REL = "research/manuscripts/lit-targets-endpoint-benchmarks.json"
CACHE = "literature-cache branch, literature/emc-endpoint-benchmarks"
CACHE2 = "literature-cache branch, literature/emc-endpoint-benchmarks-r2"


# ================================================================================================
# RETRIEVED CONSTANTS
# Each carries the quote it was read from and the corpus file that quote lives in. Nothing here is
# recalled. A reader who does not trust a value can `git show origin/literature-cache:<file>` and
# find the same string.
# ================================================================================================

VAN_GLABBEKE = {
    "citation": {
        "short": "Van Glabbeke 2002",
        "title": ("Progression-free rate as the principal end-point for phase II trials in "
                  "soft-tissue sarcomas."),
        "authorString": "Van Glabbeke M, Verweij J, Judson I, Nielsen OS, EORTC Soft Tissue and "
                        "Bone Sarcoma Group.",
        "journal": "European Journal of Cancer",
        "year": 2002, "volume": "38", "issue": "4", "pages": "543-549",
        "pmid": "11872347", "doi": "10.1016/s0959-8049(01)00398-7",
        "openAccess": False,
        "retrieved_via": ("Europe PMC REST search on the exact title (resultType=core) from a GitHub "
                          "Actions runner, and independently confirmed against Crossref's "
                          "bibliographic query, which returned the same DOI, volume and page range"),
        "retrieved_files": [CACHE + "/epmc_vanglabbeke_title.txt",
                            CACHE2 + "/crossref_vanglabbeke_biblio.txt"],
        "verified": True,
    },
    "abstract_verbatim": (
        "We have estimated progression-free rates (PFR) for various groups of soft-tissue sarcoma "
        "patients from our clinical trials database, to provide reference values for conducting "
        "phase II studies with PFR as the principal end-point. In 146 pretreated patients receiving "
        "an active agent, the PFR estimates were 39 and 14% at 3 and 6 months; with inactive "
        "regimens (234 patients), those estimates were 21 and 8% respectively. In 1154-non-pretreated "
        "patients, PFR estimates varied from 77% (synovial sarcoma) to 57% (malignant fibrous "
        "histiocytoma (MFH)) at 3 months, and from 56% (synovial sarcoma) to 38% (MFH) at 6 months. "
        "In 61 leiomyosarcomas from gastrointestinal origin, the corresponding figures were 44 and "
        "30%, respectively. Consequently, for first-line therapy, a 6-month PFR of > or = 30-56% "
        "(depending on histology) can be considered as a reference value to suggest drug activity; "
        "for second-line therapy, a 3-month PFR of > or = 40% would suggest a drug activity, and "
        "< or = 20% would suggest inactivity."),
    "reference_values_pct": {
        "second_line_active_agent": {"n_patients": 146, "pfr_3mo": 39, "pfr_6mo": 14},
        "second_line_inactive_regimens": {"n_patients": 234, "pfr_3mo": 21, "pfr_6mo": 8},
        "first_line_non_pretreated": {
            "n_patients": 1154,
            "pfr_3mo_range": [57, 77], "pfr_3mo_range_histologies": ["MFH (low)",
                                                                     "synovial sarcoma (high)"],
            "pfr_6mo_range": [38, 56], "pfr_6mo_range_histologies": ["MFH (low)",
                                                                     "synovial sarcoma (high)"]},
        "gastrointestinal_leiomyosarcoma": {"n_patients": 61, "pfr_3mo": 44, "pfr_6mo": 30},
    },
    "histologies_the_abstract_names": ["synovial sarcoma", "malignant fibrous histiocytoma",
                                       "gastrointestinal leiomyosarcoma"],
    "what_the_abstract_does_not_say": (
        "It does not name extraskeletal myxoid chondrosarcoma, and it does not name any indolent "
        "histology. Whether the 1154 non-pretreated patients contained any EMC cannot be settled "
        "from the abstract, and the full text is paywalled (isOpenAccess: N on the Europe PMC core "
        "record). What IS settled by the abstract's own wording is that the reference value is "
        "explicitly histology-dependent -- 'a 6-month PFR of >= 30-56% (depending on histology)' -- "
        "and that the spread it observed across the four histologies it does name is 18 percentage "
        "points at 6 months."),
}

# The provenance CHAIN from the master trial to Van Glabbeke, in the master trial's own words. This
# is what makes the benchmark question answerable at all: the EMC cohort's abstract cites nothing,
# but the stage-1 paper of the same master protocol (NCT03277924), by the same investigators, states
# where its 6-month threshold came from and cites Van Glabbeke 2002 as reference 22.
IMMUNOSARC1_DESIGN = {
    "citation": {"short": "Martin-Broto 2020 (IMMUNOSARC I)", "pmid": "33203665",
                 "pmcid": "PMC7674086", "doi": "10.1136/jitc-2020-001561",
                 "journal": "Journal for ImmunoTherapy of Cancer", "year": 2020,
                 "registration": "NCT03277924", "openAccess": True},
    "retrieved_file": CACHE + "/epmc_immunosarc1_fulltext.txt",
    "statistical_section_verbatim": (
        "Sample size has been obtained for a one-arm, one-stage survival design based on "
        "Brookmeyer-Crowley-like test. The statistical test for survival probability was based on "
        "non-parametric estimation of survival distribution. For STS second-line cohort sample size "
        "has been obtained for the primary endpoint: 6 month PFSR. The estimated accrual time was 24 "
        "months. In this population, a 5% PFSR was considered not promising, whereas a 15% PFSR was "
        "considered promising. With a 0.05 type I error alpha and a power of 0.80, 48 patients were "
        "needed in this cohort."),
    "discussion_section_verbatim": (
        "In this phase Ib/II trial, we found that the 6-month PFSR was 48% according to RECIST and "
        "independent central review. This outcome widely exceeds the 15% considered promising in the "
        "statistical assumption of this trial. This threshold was based on the European Organisation "
        "for Research and Treatment of Cancer (EORTC) recommendation cut-off for activity, in terms "
        "of 6-month PFSR, in second line drugs of advanced STS."),
    "reference_22_verbatim": (
        "Van Glabbeke M , Verweij J , Judson I , et al Progression-free rate as the principal "
        "end-point for phase II trials in soft-tissue sarcomas . Eur J Cancer 2002 ; 38 : 543 - 9 . "
        "10.1016/S0959-8049(01)00398-7 11872347"),
    "what_this_establishes": (
        "The master trial's 6-month progression-free threshold is EXPLICITLY sourced to Van Glabbeke "
        "2002, by the investigators, in a peer-reviewed full paper. So the Van Glabbeke framework is "
        "demonstrably in use in this trial family, and the question 'is that reference appropriate "
        "for EMC' is a real question about a real chain rather than a supposition."),
    "what_this_does_NOT_establish": (
        "It does not establish that the stage-2 EMC cohort's 50%/80% came from Van Glabbeke. It did "
        "not: stage 1's 15% is the EORTC second-line cut-off the paper explicitly cites, which Van "
        "Glabbeke states as 14% -- the one-point difference is the trial's rounding and not this "
        "file's inference, since the attribution is the paper's own. The EMC "
        "cohort's null of 50% is more than three times it. The stage-1 and stage-2 nulls are "
        "different numbers with different provenance, and only stage 1's is stated anywhere."),
}

# The two EMC trials' design parameters, as registered and as published.
TRIAL_DESIGNS = [
    {
        "trial": "pazopanib phase 2, EMC stratum",
        "sourceId": "stacchiotti2019pazopanib",
        "registration": "NCT02066285",
        "year_published": 2019,
        "primary_endpoint": "objective response rate (RECIST 1.1), modified intention-to-treat",
        "design_family": "Simon optimal two-stage",
        "p0": 0.05, "p1": 0.25, "alpha": 0.10, "beta": 0.10,
        "stage1_n": 9, "stage1_stop_if_responses_at_most": 0,
        "total_n_planned": 24, "reject_null_if_responses_at_least": 3,
        "observed": {"events": 4, "denom": 22, "what": "RECIST objective responses / evaluable"},
        "design_verbatim": (
            "To estimate the simple size for stratum 2 (EMC), a Simon's optimal 2-stage phase II "
            "design has been used, having considered the very scarce published information on "
            "response rate based on RECIST criteria. For a design with P0= 0.05, P1= 0.25, "
            "alpha=0.1 and beta=0.1. At the first stage, 9 patients should be enrolled into the "
            "study, if there are not responses the trial will be terminated and it will be concluded "
            "that pazopanib is not sufficiently active. If there is at least 1 response in this "
            "first stage, the trial will be continued and at the second stage, another 15 patients "
            "(total 24 patients) would be enrolled into the study. To reject the null hypothesis for "
            "the EMC stratum 3 responses or more (RECIST criteria), out of the 24 patients, are "
            "needed."),
        "retrieved_file": CACHE + "/ctgov_nct02066285_full.txt",
        "how_the_null_was_justified": (
            "'having considered the very scarce published information on response rate' -- the null "
            "is justified by the ABSENCE of data, and the registry entry says so in as many words. "
            "That is an honest thing to write and it is also the whole problem: a 5% null in a "
            "disease with no published response rate is a statement about the literature, not about "
            "the disease."),
        "sibling_stratum_in_the_same_protocol": {
            "stratum": "solitary fibrous tumour",
            "response_criterion": "Choi",
            "p0": 0.40, "p1": 0.60, "alpha": 0.10, "beta": 0.10,
            "verbatim": (
                "To estimate the sample size for stratum 1 (SFT), a Simon's optimal 2-stage phase II "
                "design has been used, having considered the published response rate based on Choi "
                "criteria in SFT patients which correspond to 40% in monotherapy. For a design with "
                "P0=0.40, P1=0.60; alpha=0.1 and beta=0.1."),
            "why_this_matters_here": (
                "ONE PROTOCOL, ONE DRUG, ONE ERA, TWO STRATA -- and the response criterion and the "
                "null were chosen per histology: Choi with a 40% null for SFT, RECIST with a 5% null "
                "for EMC. Both strata received the same antiangiogenic agent, which is the setting "
                "Choi criteria were developed for. No rationale for reading EMC by RECIST rather "
                "than by Choi appears in the registry record or in the published EMC paper. "
                "⚠ AND THE REGISTRY IS AMBIGUOUS ABOUT WHETHER CHOI WAS REGISTERED FOR EMC AT ALL, "
                "WHICH IS WHY THIS FILE DOES NOT CLAIM IT WAS. The primary-outcome text names both "
                "criteria without assigning either -- 'measured using Choi and RECIST 1.1 criteria' "
                "-- while the brief summary assigns them with the word 'respectively' (SFT to Choi, "
                "EMC to RECIST) and the detailed statistical design powers the EMC stratum on "
                "RECIST. The defensible statement is narrower and is enough: the same protocol "
                "judged its other stratum, on the same drug, by Choi -- so the criterion was thought "
                "fit for this setting by these investigators -- and the EMC scans that a Choi read "
                "would use were taken."),
        },
    },
    {
        "trial": "IMMUNOSARC II, EMC cohort",
        "sourceId": "immunosarc2emc2025",
        "registration": "NCT03277924",
        "year_published": 2025,
        "primary_endpoint": "6-month progression-free survival rate (RECIST 1.1)",
        "design_family": ("stated only as a threshold; the stage-1 paper of the same master protocol "
                          "used a one-arm one-stage Brookmeyer-Crowley-like survival design"),
        "p0": 0.50, "p1": 0.80, "alpha": 0.05, "beta": 0.10,
        "total_n_planned": 22, "reject_null_if_events_at_least": 15,
        "observed": {"events": 16, "denom": 23,
                     "what": "patients free of progression at 6 months / evaluable"},
        "observed_as_published_km_pct": 77.0,
        "design_verbatim": (
            "The primary endpoint was 6-month(m)-PFS rate, and the statistical assumptions were "
            "obtaining a 6m-PFSR in at least 15 pts out of 22 pts, with H0 = 50% and H1 = 80%, "
            "(alpha 0.05; beta 0.10) to consider the combination as promising."),
        "retrieved_file": CACHE + "/../emc-systemic-therapy-2026-08-07/im2_crossref_doi.txt "
                                  "(Crossref JATS abstract) and .../im2_s2_doi.txt (Semantic "
                                  "Scholar), independently",
        "how_the_null_was_justified": (
            "IT IS NOT. The only published account of this cohort is a conference abstract, and it "
            "states the numbers 50% and 80% without attributing either to a source. There is no full "
            "paper and ClinicalTrials.gov posts no results for NCT03277924. The registry's own "
            "outcome-measure text for this cohort defines the endpoint but states no threshold."),
    },
]

# Every EMC-specific 6-month progression-free figure that exists, published as a rate or derivable
# from a published median. THE TWO PUBLISHED RATES ARE THE POINT: this repository, and the field,
# had been treating the 6-month progression-free rate in EMC as though it had no benchmark.
EMC_SIX_MONTH_ROWS = [
    {
        "cohort": "drilon_chemotherapy", "sourceId": "drilon2008", "year": 2008,
        "regimen": "cytotoxic chemotherapy, mixed regimens",
        "published_6mo_pct": 40.0,
        "published_median_months": 5.2,
        "kind": "Kaplan-Meier rate, published directly",
        "verbatim": (
            "The median PFS was 5.2 months (Kaplan-Meier 95% CI, 3.4 months-7.1 months). Estimated "
            "PFS rates (Kaplan-Meier) at 3 months, 4 months, 6 months, and 9 months were 69%, 65%, "
            "40%, and 26%, respectively."),
        "authors_own_framing_verbatim": (
            "Although there are biases inherent in retrospective analyses, these data provide a "
            "benchmark for time to disease progression for the study of new agents for the treatment "
            "of patients with this diagnosis."),
        "retrieved_file": CACHE2 + "/pmc_html_drilon.txt",
        "caveats": ("denominator is COURSES, not patients -- 32 evaluable courses in 21 patients, "
                    "with time to progression determinable in 29 of 32; response was "
                    "physician-assessed, not central RECIST; treatment era 1975-2006"),
    },
    {
        "cohort": "anthracycline_italian_rcn", "sourceId": "stacchiotti2013anthracycline",
        "year": 2013, "regimen": "anthracycline-based chemotherapy (10 of 11 with ifosfamide)",
        "published_6mo_pct": 50.0,
        "published_median_months": 8.0,
        "kind": "rate stated in the text beside the Kaplan-Meier median",
        "verbatim": (
            "The median PFS for the entire group was 8 months (range 2-10), with 50% patients "
            "progression-free at 6 months (Figure 2)."),
        "retrieved_file": CACHE2 + "/epmc_ft_anthracycline_PMC3879193.txt",
        "caveats": ("n = 11 advanced EMC, retrospective, Italian Rare Cancer Network, central "
                    "pathology review and molecular confirmation; front line in 10 of 11"),
    },
    {
        "cohort": "chiusole_metastatic_chemo", "sourceId": "chiusole2020", "year": 2020,
        "regimen": "first-line chemotherapy for metastatic disease",
        "published_6mo_pct": None,
        "published_median_months": 9.0,
        "kind": "median only; no fixed-timepoint rate published",
        "verbatim": (
            "Median progression-free survival for patients receiving first-line chemotherapy was 9 "
            "months."),
        "retrieved_file": CACHE2 + "/epmc_ft_chiusole_PMC7308468.txt",
        "caveats": ("n = 20 patients treated with chemotherapy for metastatic disease across two "
                    "institutions, 1980-2018, retrospective; the paper's own conclusion is that "
                    "chemotherapy did not improve survival in unselected patients and that the "
                    "association is confounded by indication"),
    },
    {
        "cohort": "sunitinib_nivolumab_immunosarc2", "sourceId": "immunosarc2emc2025", "year": 2025,
        "regimen": "sunitinib + nivolumab",
        "published_6mo_pct": 77.0,
        "published_median_months": 13.2,
        "kind": "Kaplan-Meier rate, published directly, alongside a crude count of 16/23",
        "verbatim": ("among the 23 evaluable pts, 6m-PFSR was 77% with 16/23 pts free of progression "
                     "at 6 mos, and a median PFS of 13.2 mos (95%CI 5.7-20.7)"),
        "retrieved_file": "already committed at " + POOLING_REL + " -> cohorts[].quote",
        "caveats": ("conference abstract only; the 77% and the 16/23 (69.6%) are not reconciled in "
                    "the abstract and no full paper exists"),
    },
    {
        "cohort": "pazopanib_phase2", "sourceId": "stacchiotti2019pazopanib", "year": 2019,
        "regimen": "pazopanib 800 mg/day",
        "published_6mo_pct": None,
        "published_median_months": 19.0,
        "kind": "median only at 6 months; 12- and 24-month rates published",
        "verbatim": ("median PFS of 19 months (95% CI 11-27); PFS 74% at 12 months and 40% at 24 "
                     "months -- read from the Remiszewski 2025 review's account of the trial, which "
                     "is why " + POOLING_REL + " marks these figures secondary provenance"),
        "retrieved_file": "already committed at " + POOLING_REL,
        "caveats": ("the trial's own paper reports the objective-response primary endpoint; the "
                    "time-to-event figures reach this repository through a review"),
    },
]

# The GMI reference proportions that exist in advanced soft-tissue sarcoma. Not EMC -- there is no
# EMC GMI series -- but they are what a GMI-based EMC design would have to be powered against, and
# they are explicit integer counts from two national sarcoma groups.
GMI_REFERENCE_ROWS = [
    {"study": "Cousin 2013 (French Sarcoma Group)", "pmid": "23904460", "year": 2013,
     "population": "advanced STS receiving second-line treatment after doxorubicin-based regimens",
     "gmi_gt_133_events": 69, "denom": 227,
     "verbatim": ("The population consisted in 106 men and 121 women, 110 patients (48%) received "
                  "'active drugs'. ... Sixty-nine patients experienced GMI >1.33 (30.4%)."),
     "retrieved_file": CACHE + "/epmc_gmi_title.txt",
     "also_states_verbatim": ("Second-line treatments were classified as 'active' according to the "
                             "EORTC-STBSG criteria (3-month progression-free rate >40% or 6-month "
                             "PFR >14%)."),
     "why_that_second_quote_matters": (
         "It is an independent, later restatement of the Van Glabbeke second-line reference values, "
         "by a different group, in a different country -- so the two numbers this file reads out of "
         "the 2002 abstract are corroborated by a 2013 source that was retrieved separately.")},
    {"study": "Martinez-Trufero 2021 (GEISTRA, Spanish sarcoma group)", "pmid": "33672857", "year": 2021,
     "population": "advanced STS receiving trabectedin as second- or further-line, 19 Spanish centres",
     "gmi_gt_133_events": 118, "denom": 357,
     "verbatim": ("The median GMI was 0.82 (0-69), with 198 patients (55%) with a GMI < 1, 41 "
                  "(11.5%) with a GMI 1-1.33 and 118 (33.1%) with a GMI > 1.33."),
     "retrieved_file": CACHE + "/epmc_gmi_title.txt"},
]

GMI_METHOD_SOURCES = [
    {"what": "the design the GMI operationalises", "pmid": "10913809", "year": 2000,
     "title": ("Phase II clinical trial design for noncytotoxic anticancer agents for which time to "
               "disease progression is the primary endpoint"),
     "verbatim": ("We examine a phase II trial design that evaluates clinical benefit by comparing "
                  "sequentially measured paired failure times within each treated patient. ... "
                  "Assuming patients eligible for a phase II study of a new cytostatic agent have "
                  "failed previous cancer treatment, their most recent prior time to progression "
                  "interval, TTP(1), is uncensored. Time to progression after the cytostatic agent, "
                  "TTP(2), may or may not be censored at analysis. The design is motivated by a "
                  "'growth modulation index' (TTP(2)/TTP(1))"),
     "retrieved_file": CACHE + "/epmc_mick_ttp_design.txt"},
    {"what": "the lecture the 1.33 threshold is conventionally traced to", "pmid": "9607564",
     "year": 1998,
     "title": ("There are no bad anticancer agents, only bad clinical trial designs--twenty-first "
               "Richard and Hinda Rosenthal Foundation Award Lecture"),
     "note": ("Retrieved and confirmed to exist with this exact title. ⚠ THE 1.33 THRESHOLD ITSELF "
              "IS NOT IN THE RETRIEVED ABSTRACT, and this file does not attribute it to this source. "
              "What IS retrieved is that three independent later sources -- Cousin 2013, GEISTRA 2021 "
              "and the 2026 ROSEWOOD analysis -- all use 1.33 as the threshold, so the convention is "
              "evidenced by its use rather than by a citation this file has verified."),
     "retrieved_file": CACHE + "/epmc_vonhoff_karnofsky.txt"},
    {"what": "sample-size methodology for a GMI-primary single-arm phase II", "pmid": "30458583",
     "year": 2019, "title": "Phase II trial design with growth modulation index as the primary endpoint.",
     "verbatim": ("we derived a sample size formula for the score test under a log-linear model of "
                  "the GMI. Study designs using the derived sample size formula are illustrated "
                  "under a bivariate exponential model, the Weibull frailty model, and the "
                  "generalized treatment effect size."),
     "retrieved_file": CACHE + "/epmc_gmi_title.txt",
     "why_it_is_named_but_not_used": (
         "A GMI-primary design has a published sample-size methodology, so 'nobody knows how to "
         "power this' is not a valid objection. This file does NOT reproduce that formula -- doing "
         "so would require the paper's full text, which was not retrieved -- so the patient cost of "
         "a GMI-primary design is reported below as the binomial cost of a GMI>1.33 PROPORTION "
         "endpoint, which is computable here, and the log-linear alternative is named as existing "
         "rather than costed.")},
    {"what": "how the GMI is reported in practice, and how badly", "pmid": "40156702", "year": 2025,
     "title": ("The Growth Modulation Index (GMI) as an Efficacy Outcome in Cancer Clinical Trials: "
               "A Scoping Review with Suggested Reporting"),
     "verbatim": ("The terminology employed to refer to the GMI, as well as its definitions, are "
                  "highly variable in the literature. Some uses of the GMI are arbitrary and not "
                  "based on any scientific rationale. ... Among 227 included documents, 166 of which "
                  "discussed GMI specifically."),
     "retrieved_file": CACHE + "/epmc_gmi_title.txt"},
]

RDD_SOURCES = [
    {"pmid": "12431972", "year": 2002,
     "title": "Randomized discontinuation design: application to cytostatic antineoplastic agents.",
     "verbatim": ("In the setting of renal cell carcinoma, some patients' tumors will grow slowly "
                  "naturally. An appropriate design has to distinguish antiproliferative activity "
                  "attributable to the novel agent from indolent disease. We propose a randomized "
                  "discontinuation design that initially treats all patients with the study agent "
                  "(stage 1) and then randomizes in a double-blind fashion to continuing therapy or "
                  "placebo only those patients whose disease is stable (stage 2). This design allows "
                  "the investigators to determine if apparent slow tumor growth is attributable to "
                  "the drug or to selection of patients with naturally slow-growing tumors."),
     "why_it_is_here": ("This is the EMC problem, stated in the literature 23 years before this "
                        "file, for a different disease. The design exists precisely to separate "
                        "drug effect from indolence, which is the question PUB-ENDPOINT Sec. 6.1 "
                        "says the published EMC record cannot answer."),
     "retrieved_file": CACHE + "/epmc_rdd_title.txt"},
    {"pmid": "15983399", "year": 2005, "title": "Evaluation of randomized discontinuation design.",
     "verbatim": ("The randomized discontinuation design is not as efficient as upfront "
                  "randomization if treatment has a fixed effect on tumor growth rate or if "
                  "treatment benefit is restricted to slower-growing tumors."),
     "retrieved_file": CACHE + "/epmc_rdd_title.txt"},
    {"pmid": "17008711", "year": 2006, "title": "Problems with the randomized discontinuation design.",
     "note": "Retrieved as a title-level record; no abstract was returned by the search.",
     "retrieved_file": CACHE + "/epmc_rdd_title.txt"},
]

EMC_NATURAL_HISTORY = {
    "indolence_figures": {
        "sourceId": "remiszewski2025", "pmid": "41055792", "year": 2025,
        "verbatim": ("Recurrence-free survival (RFS) varies: local recurrence (LR) rates range from "
                     "13 to 42% across studies, and distant metastases develop in around 35-45% of "
                     "patients, primarily in the lungs. The median time to metastasis is "
                     "approximately 28 months. Overall survival (OS) reflects the typically indolent "
                     "yet metastatic course: 5-year OS 66-88%, and 10-year disease-specific survival "
                     "approximately 85%."),
        "retrieved_file": CACHE + "/epmc_emc_indolent_naturalhistory.txt"},
    "the_only_retrieved_direct_evidence_that_untreated_emc_can_regress": {
        "pmid": "41321774", "year": 2025,
        "title": ("Spontaneous regression of metastatic disease after palliative debulking surgery "
                  "for heavily pre-treated extraskeletal myxoid chondrosarcoma"),
        "verbatim": ("We report spontaneous regression of lung metastases in a patient with EMC "
                     "after re-resection of the primary tumour, which was performed with palliative "
                     "intent for symptom control after multiple lines of systemic treatment. The "
                     "patient has remained disease-free and is now more than 5 years post-surgery. "
                     "To our knowledge, this is the first described case of spontaneous regression "
                     "of metastatic disease following resection of a primary tumour in a patient "
                     "with EMC."),
        "retrieved_file": CACHE + "/epmc_emc_indolent_naturalhistory.txt",
        "⛔_what_this_is_not": (
            "n = 1. A case report is not a rate, and this one follows surgery rather than "
            "observation, so it is not even a clean observation of untreated behaviour. It is "
            "recorded because it is the ONLY retrieved direct evidence in this disease that "
            "metastatic EMC can regress without systemic therapy, and because 'the field's single "
            "documented instance is a case report' is itself the measurement of how empty this "
            "space is. It supports no rate, no null and no design.")},
    "the_quantity_that_was_not_retrieved": (
        "A 6-month progression-free rate, or any fixed-timepoint progression rate, measured on "
        "advanced EMC patients who are receiving no systemic therapy. Every figure in "
        "E2_emc_six_month_progression_free_ladder is measured on treated patients. Nothing "
        "retrieved for this file supplies an untreated rate, and PUB-ENDPOINT Sec. 7.3 already "
        "records that a randomised no-treatment arm in an ultra-rare indolent sarcoma is not a "
        "realistic ask."),
    "⚠_and_that_is_an_absence_OF_A_READING_not_a_reading_OF_ABSENCE": (
        "Three Europe PMC searches were run for it -- epmc_emc_untreated_metastases, "
        "epmc_emc_indolent_naturalhistory and epmc_emc_time_to_metastasis, each returning the top "
        "25 relevance-ranked hits -- and none of the returned records reports such a rate; neither "
        "does any of the nine curated EMC systemic-therapy cohort rows. That is what was measured. "
        "It is NOT a proof that no such figure exists in the literature, and CLAUDE.md Sec. 4 is "
        "explicit that the two are different claims. The honest form is: this repository has looked, "
        "in the places named, and has not found one."),
}

# The endpoints to be graded. Ordering is the order they are argued in the note; it is not a ranking.
# ================================================================================================
# The nearest thing to a natural-history calibration that exists in ANY indolent soft-tissue tumour.
# It is NOT EMC and it must never be transferred to EMC as a rate. What it settles is a different and
# still-important question: is the natural-history confound HYPOTHETICAL, or has anyone ever measured
# it? It has been measured once, in a neighbouring disease, and it was large.
# ================================================================================================
INDOLENT_TUMOUR_PLACEBO_CALIBRATION = {
    "⛔_read_this_first": (
        "DESMOID FIBROMATOSIS IS NOT EMC AND NO NUMBER BELOW MAY BE USED AS AN EMC RATE. Desmoid is "
        "a locally aggressive fibroblastic neoplasm that does not metastasise; EMC does, in 35-45% "
        "of patients. Their natural histories are different diseases' natural histories. This block "
        "exists for ONE purpose: to answer whether the natural-history component of a "
        "progression-based endpoint in an indolent soft-tissue tumour is a theoretical worry or a "
        "measured quantity. Everything below is offered as an EXISTENCE PROOF about endpoints, never "
        "as a transferable rate."),
    "randomised_placebo_controlled": {
        "study": "Gounder 2018, sorafenib versus placebo in desmoid tumours",
        "pmid": "30575484", "year": 2018,
        "design": "double-blind phase 3, 87 patients randomised, crossover permitted on progression",
        "verbatim": (
            "In this double-blind, phase 3 trial, we randomly assigned 87 patients with progressive, "
            "symptomatic, or recurrent desmoid tumors to receive either sorafenib (400-mg tablet "
            "once daily) or matching placebo. ... With a median follow-up of 27.2 months, the 2-year "
            "progression-free survival rate was 81% (95% confidence interval [CI], 69 to 96) in the "
            "sorafenib group and 36% (95% CI, 22 to 57) in the placebo group (hazard ratio for "
            "progression or death, 0.13; 95% CI, 0.05 to 0.31; P<0.001). Before crossover, the "
            "objective response rate was 33% (95% CI, 20 to 48) in the sorafenib group and 20% (95% "
            "CI, 8 to 38) in the placebo group."),
        "retrieved_file": CACHE + "/epmc_desmoid_sorafenib_title.txt",
        "⭐_the_two_readings_that_matter_here": {
            "a_progression_free_RATE_has_a_large_placebo_component": (
                "36% of patients on PLACEBO were progression-free at 2 years, in a population "
                "enrolled for progressive, symptomatic or recurrent disease -- the same "
                "progression-before-entry design feature PUB-ENDPOINT Sec. 6.1 names as what BOUNDS "
                "the confound. It bounds it; it does not remove it. A fixed-timepoint "
                "progression-free rate benchmarked against a historical treated cohort could not "
                "have told 36% from 81% without the placebo arm."),
            "⚠_and_so_does_OBJECTIVE_RESPONSE_which_qualifies_a_claim_this_repository_makes": (
                "20% of patients on PLACEBO had an objective response (95% CI 8-38). "
                "PUB-ENDPOINT Sec. 7.2 argues that a response is 'an unambiguous observation and the "
                "few that occur are informative precisely because they are hard to explain by "
                "natural history'. This measurement shows that claim is DISEASE-SPECIFIC rather than "
                "general: in at least one indolent soft-tissue tumour, one patient in five responded "
                "to nothing. ⛔ IT DOES NOT REFUTE Sec. 7.2 FOR EMC -- spontaneous regression is a "
                "documented and well-known feature of desmoid biology, whereas the whole of the "
                "retrieved EMC evidence for it is a single 2025 case report (E9). What it does is "
                "convert 'responses are hard to explain by natural history' from a general principle "
                "into a claim that has to be argued per disease, and in EMC it has not been."),
        },
    },
    "untreated_observation_cohort": {
        "study": "National Cancer Centre Singapore desmoid series",
        "pmid": "42052362", "year": 2026,
        "design": "retrospective single-centre, 1999-2023; active surveillance versus resection",
        "verbatim": (
            "A total of 76 patients with desmoid tumours were seen in NCCS between September 1999 "
            "and October 2023; 19 patients were placed on active surveillance, and the remaining 57 "
            "patients underwent R0/ R1/ R2 wide excision of desmoid tumour. At one-year, progressive "
            "disease was observed in 5 out of 19 patients (26.3%) on active surveillance"),
        "retrieved_file": CACHE + "/epmc_desmoid_active_surveillance.txt",
        "progression_free_at_12_months": {"events": 14, "denom": 19},
        "⚠_caveats_that_are_not_optional": (
            "n = 19, retrospective, single centre, a different disease, and an active-surveillance "
            "population is SELECTED for expected indolence -- which is the same selection bias that "
            "makes a single-arm result uninterpretable, running the other way. It is included "
            "because it is the ONLY untreated-cohort fixed-timepoint progression rate retrieved for "
            "any indolent soft-tissue tumour, and because the contrast with EMC is the point: EMC "
            "has no equivalent, not even a biased one."),
    },
    "⭐_what_this_block_licenses_and_what_it_forbids": {
        "licensed": (
            "The statement that the natural-history confound in a progression-based endpoint is NOT "
            "hypothetical. In the one indolent soft-tissue tumour where a randomised placebo arm "
            "exists, the placebo 2-year progression-free rate was 36% and the placebo objective "
            "response rate was 20%. An endpoint benchmarked only against treated historical cohorts "
            "would have been unable to see either."),
        "forbidden": (
            "Any transfer of 36%, 20% or 14/19 to EMC, in any direction, for any purpose. Desmoid "
            "does not metastasise and EMC does; these are different diseases and their untreated "
            "behaviour is not interchangeable. Nothing in this file uses any of these numbers as an "
            "EMC null, and no future work should."),
        "and_what_it_says_about_the_recommendation": (
            "It is the strongest available argument FOR the growth modulation index and AGAINST "
            "relying on any historical benchmark: the one time anyone measured the placebo component "
            "of these endpoints in an indolent soft-tissue tumour, it was large enough to account "
            "for a substantial part of a single-arm result. The index is the only recommended change "
            "that measures that component per patient instead of assuming it away."),
    },
}


CANDIDATE_ENDPOINTS = [
    "objective_response_rate",
    "disease_control_rate",
    "progression_free_survival_median",
    "progression_free_rate_at_a_fixed_timepoint",
    "growth_modulation_index",
    "tumour_growth_rate_volumetric",
    "time_to_next_treatment",
    "duration_of_response",
    "choi_rather_than_recist",
    "randomized_discontinuation_design",
]


# ================================================================================================
# Statistics
# ================================================================================================
def wilson(events: int, n: int, z: float = 1.96):
    """Wilson score 95% interval. Same implementation as emc_endpoint_discordance.wilson, which is
    itself asserted equal to the pooling module's -- duplicated for the same reason given there
    (importing either executes a full build at import time)."""
    if n <= 0:
        return (None, None)
    p = events / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = p + z2 / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return (round((centre - half) / denom, 4), round((centre + half) / denom, 4))


def pct(x, nd=1):
    return None if x is None else round(100.0 * x, nd)


def binom_sf(r: int, n: int, p: float) -> float:
    """P(X >= r) for X ~ Binomial(n, p). Exact, no normal approximation -- at n around 20 the
    approximation is the difference between a design that holds its stated alpha and one that does
    not, which is precisely what E4 measures."""
    if r <= 0:
        return 1.0
    if r > n:
        return 0.0
    return sum(math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k)) for k in range(r, n + 1))


def single_stage_design(p0: float, p1: float, alpha: float, beta: float, n_max: int = 400):
    """Smallest n (with its threshold r) for an exact single-stage single-arm binomial design:
    P(X >= r | p0) <= alpha  and  P(X >= r | p1) >= 1 - beta."""
    for n in range(1, n_max + 1):
        for r in range(1, n + 1):
            if binom_sf(r, n, p0) <= alpha and binom_sf(r, n, p1) >= 1 - beta:
                return {"n": n, "reject_null_if_at_least": r,
                        "exact_type_I_error": round(binom_sf(r, n, p0), 4),
                        "exact_power_at_p1": round(binom_sf(r, n, p1), 4)}
    return None


def surv_at(t_months: float, median_months: float) -> float:
    """Fixed-timepoint progression-free rate implied by a median, under a constant hazard.

    ⚠ THIS IS AN ASSUMPTION AND IT IS THE ONLY MODELLING ASSUMPTION IN THIS FILE. It is used ONLY
    where a cohort published a median and no 6-month rate. Its error in this disease is MEASURED
    rather than asserted, against the three EMC cohorts that publish both -- see
    E2 -> conversion_validation."""
    return 0.5 ** (t_months / median_months)


def implied_median(rate: float, t_months: float = 6.0) -> float:
    """The inverse: the median a fixed-timepoint rate corresponds to under the same assumption.
    This is what turns a null hypothesis expressed as a rate into a statement about how fast the
    disease is assumed to progress, which is the form a clinician can actually check."""
    return t_months * math.log(0.5) / math.log(rate)


# ================================================================================================
# Inputs
# ================================================================================================
def load_sources():
    with open(POOLING, encoding="utf-8") as fh:
        pooling = json.load(fh)
    with open(DISCORDANCE, encoding="utf-8") as fh:
        disc = json.load(fh)
    by_key = {c["key"]: c for c in pooling["cohorts"]}
    for c in pooling.get("context_only_no_extractable_counts", []):
        by_key[c["key"]] = c
    return pooling, disc, by_key


# ================================================================================================
# E1 -- what the two EMC trials actually tested, and against what
# ================================================================================================
def e1_design_ledger(disc):
    return {
        "question": ("For each prospective trial that has ever reported an EMC-specific efficacy "
                     "endpoint, what was the primary endpoint, what null was it tested against, and "
                     "where did that null come from?"),
        "why_this_had_to_be_built_first": (
            "PUB-ENDPOINT's D5 established that the two modern EMC trials chose DIFFERENT primary "
            "endpoints six years apart -- objective response in 2019, 6-month progression-free rate "
            "in 2025 -- and that the migration was never argued in print. That is a fact about "
            "which endpoint. It says nothing about the THRESHOLD each endpoint was read against, and "
            "the threshold is what decides whether a trial reports a positive result. Neither "
            "threshold was recorded anywhere in this repository before this file."),
        "correction_this_extends": {
            "from": DISCORDANCE_REL + " -> D5_primary_endpoint_correction",
            "what_D5_settled": disc["D5_primary_endpoint_correction"]["the_discrepancy"],
            "what_this_adds": (
                "D5 corrected WHICH endpoint each trial used. This ledger adds the null, the "
                "alternative, the error rates, the decision threshold and the stated justification "
                "for each -- all of which were retrievable at zero cost from the trial registry and "
                "the published abstract, and none of which had been read."),
        },
        "trials": TRIAL_DESIGNS,
        "the_asymmetry_in_the_two_justifications": (
            "The 2019 EMC stratum's null is JUSTIFIED IN THE REGISTRY -- 'having considered the very "
            "scarce published information on response rate' -- and is therefore auditable, even "
            "though what it audits to is an absence. The 2025 EMC cohort's null is stated as a "
            "number and attributed to nothing, in the only document that exists about it. A null "
            "with a bad reason can be argued with. A null with no stated reason cannot, and it is "
            "the one that carries a field's conclusion forward."),
        "what_a_reader_should_take_from_this_section_alone": (
            "Nothing about any drug. Two designs, both single-arm, both without a comparator, each "
            "declaring a result against a threshold chosen by the investigators. That is the normal "
            "and accepted way to run a phase 2 trial in an ultra-rare disease; the question this "
            "file asks is whether the thresholds were EMC-appropriate, not whether the trials were "
            "properly conducted."),
    }


# ================================================================================================
# E2 -- every EMC 6-month progression-free figure that exists, and how well a median converts
# ================================================================================================
def e2_six_month_ladder():
    rows = []
    for r in EMC_SIX_MONTH_ROWS:
        row = dict(r)
        m = r["published_median_months"]
        row["exponential_implied_6mo_pct"] = pct(surv_at(6.0, m)) if m else None
        rows.append(row)

    validation = []
    for r in EMC_SIX_MONTH_ROWS:
        if r["published_6mo_pct"] is None or r["published_median_months"] is None:
            continue
        implied = pct(surv_at(6.0, r["published_median_months"]))
        validation.append({
            "cohort": r["cohort"],
            "published_median_months": r["published_median_months"],
            "published_6mo_pct": r["published_6mo_pct"],
            "exponential_implied_6mo_pct": implied,
            "error_pct_points": round(implied - r["published_6mo_pct"], 1),
        })
    errs = [abs(v["error_pct_points"]) for v in validation]

    ladder = sorted(
        [{"cohort": r["cohort"], "year": r["year"], "regimen": r["regimen"],
          "six_month_progression_free_pct": (r["published_6mo_pct"] if r["published_6mo_pct"]
                                             is not None else pct(surv_at(6.0, r["published_median_months"]))),
          "basis": ("published rate" if r["published_6mo_pct"] is not None
                    else "converted from the published median under a constant hazard")}
         for r in EMC_SIX_MONTH_ROWS],
        key=lambda d: d["six_month_progression_free_pct"])

    return {
        "question": ("What 6-month progression-free rates does the published EMC record actually "
                     "contain, and how many of them are rates rather than conversions?"),
        "rows": rows,
        "the_two_that_are_published_as_rates": [r["cohort"] for r in EMC_SIX_MONTH_ROWS
                                                if r["published_6mo_pct"] is not None
                                                and r["cohort"] != "sunitinib_nivolumab_immunosarc2"],
        "⭐_the_finding_that_was_not_in_this_repository": (
            "AN EMC-SPECIFIC 6-MONTH PROGRESSION-FREE BENCHMARK HAS EXISTED SINCE 2008 AND A SECOND "
            "SINCE 2013. Drilon 2008 published a 6-month Kaplan-Meier progression-free rate of 40% "
            "on chemotherapy and stated in its own conclusion that the data 'provide a benchmark ... "
            "for the study of new agents'. Stacchiotti 2013 published 50% progression-free at 6 "
            "months on anthracycline-based chemotherapy. Neither figure appears in "
            + POOLING_REL + " -> analyses.A6, which records that '6-month progression-free as a "
            "count' is extractable for exactly one of nine EMC cohorts -- which is TRUE AND REMAINS "
            "TRUE, because neither of these two is an integer count and POLICY-evidence 2.1 forbids "
            "reconstructing one from a percentage. ⚠ THE DISTINCTION IS THE WHOLE POINT: a figure "
            "can be unpoolable and still be the best benchmark the disease has. A6 measured "
            "poolability and answered correctly; nobody had asked the different question of whether "
            "a comparator existed."),
        "conversion_validation": {
            "what_is_being_validated": (
                "Two of the five rows publish a median and no 6-month rate, so a conversion is "
                "unavoidable if they are to enter the ladder at all. The conversion assumes a "
                "constant hazard. Three rows publish BOTH quantities, so the assumption can be "
                "measured rather than asserted."),
            "rows": validation,
            "max_absolute_error_pct_points": round(max(errs), 1) if errs else None,
            "mean_absolute_error_pct_points": round(sum(errs) / len(errs), 1) if errs else None,
            "direction": ("not one-sided -- the conversion over-predicts on the two chemotherapy "
                          "cohorts and under-predicts on the sunitinib+nivolumab cohort, so it "
                          "carries no systematic bias that would flatter or damage any row"),
            "reading": (
                "Across the three EMC cohorts that publish both, a constant-hazard conversion from "
                "the median to the 6-month rate is accurate to within about 10 percentage points, "
                "with no consistent direction. Every converted value in this file should therefore "
                "be read with a band of roughly +/- 10 points, and no conclusion below is allowed to "
                "turn on a converted value alone -- the two conclusions that matter (E3, E5) both "
                "rest on PUBLISHED rates."),
            "⚠_this_is_a_calibration_not_a_proof": (
                "Three cohorts, of 11, 21 and 23 patients. A calibration on three small "
                "retrospective and single-arm datasets bounds the conversion error roughly; it does "
                "not establish that EMC progression is exponentially distributed, and the pazopanib "
                "cohort's own published points argue that it is not -- 74% at 12 months against a "
                "constant-hazard prediction of "
                + str(pct(surv_at(12.0, 19.0))) + "% from its 19-month median, but 40% at 24 months "
                "against a prediction of " + str(pct(surv_at(24.0, 19.0))) + "%."),
        },
        "the_ladder": ladder,
        "span_pct_points": round(ladder[-1]["six_month_progression_free_pct"]
                                 - ladder[0]["six_month_progression_free_pct"], 1),
        "⛔_every_row_is_a_treated_row": (
            "All five are measured on patients receiving systemic therapy. None is an untreated or "
            "observation cohort. So this ladder can calibrate one treatment against another; it "
            "cannot calibrate any of them against natural history, and PUB-ENDPOINT Sec. 6.1's "
            "objection survives every number in it intact."),
    }


# ================================================================================================
# E3 -- where the 50% null came from, and whether it is EMC-appropriate
# ================================================================================================
def e3_benchmark_provenance():
    vg = VAN_GLABBEKE["reference_values_pct"]
    im2 = [t for t in TRIAL_DESIGNS if t["registration"] == "NCT03277924"][0]
    paz_implied = surv_at(6.0, 19.0)
    return {
        "question": ("The 2025 EMC cohort tested a 6-month progression-free rate against H0 = 50% "
                     "and H1 = 80%. Where do those two numbers come from, and are they appropriate "
                     "for an indolent tumour?"),
        "the_hypothesis_this_section_was_built_to_test": (
            "That H0 = 50% was taken from the Van Glabbeke / EORTC soft-tissue-sarcoma "
            "progression-free-rate reference values, which are derived from aggressive histologies, "
            "and would therefore be cleared by an indolent tumour's natural history alone."),
        "⛔_that_hypothesis_is_not_what_the_record_shows": (
            "It is refuted in its specific form and survives in a more damaging general form. "
            "Refuted: Van Glabbeke's second-line reference value -- the one the master trial "
            "actually cites -- is a 6-month progression-free rate of 14%, not 50%, and 80% exceeds "
            "every 6-month figure in that paper. Survives: the number 50% coincides exactly with a "
            "published EMC-specific figure, and 80% coincides to within a point with another, so "
            "the null and the alternative both appear to be EMC-derived -- and BOTH ARE MEASURED ON "
            "PATIENTS RECEIVING CHEMOTHERAPY OR A TYROSINE-KINASE INHIBITOR. An EMC-derived null is "
            "better than an aggressive-histology null and still cannot answer the question the "
            "endpoint was chosen to answer."),
        "provenance_chain_that_IS_documented": IMMUNOSARC1_DESIGN,
        "van_glabbeke_reference_values": VAN_GLABBEKE,
        "where_50_and_80_sit_against_van_glabbeke": {
            "H0_50pct_vs_second_line_active_agent_6mo": {
                "van_glabbeke": vg["second_line_active_agent"]["pfr_6mo"], "trial_H0": 50,
                "reading": ("The null is more than three times Van Glabbeke's second-line "
                            "active-agent reference value, which is the value the same master trial "
                            "cited for its stage-1 cohort. The EMC cohort's null is not that "
                            "value.")},
            "H0_50pct_vs_first_line_band_6mo": {
                "van_glabbeke_band": vg["first_line_non_pretreated"]["pfr_6mo_range"],
                "trial_H0": 50,
                "reading": ("50% sits inside Van Glabbeke's first-line band of 38-56% but near its "
                            "top, and the top of that band is synovial sarcoma. Sitting inside a "
                            "band is not provenance: the band is 18 points wide across four "
                            "histologies, none of which is EMC or is indolent.")},
            "H1_80pct_vs_every_6mo_value_in_that_paper": {
                "highest_6mo_value_in_van_glabbeke": max(
                    vg["first_line_non_pretreated"]["pfr_6mo_range"]),
                "trial_H1": 80,
                "reading": ("The alternative hypothesis exceeds the highest 6-month "
                            "progression-free rate anywhere in the reference paper by 24 percentage "
                            "points, so it cannot have been read off it.")},
        },
        "⭐_the_coincidences_that_point_somewhere_else": {
            "H0_50pct": {
                "matches": "stacchiotti2013anthracycline",
                "published_value_pct": 50.0,
                "verbatim": ("The median PFS for the entire group was 8 months (range 2-10), with "
                             "50% patients progression-free at 6 months"),
                "author_overlap": (
                    "S. Stacchiotti is the first author of the 2013 anthracycline series and is a "
                    "co-author of the 2025 IMMUNOSARC II EMC abstract, as read from the Semantic "
                    "Scholar author list retrieved for that abstract."),
                "⚠_this_is_a_coincidence_plus_an_author_overlap_and_NOT_an_attribution": (
                    "The abstract states no source for its null. An exact numerical match with the "
                    "only published EMC 6-month figure equal to 50%, by an author common to both, is "
                    "strong circumstantial evidence for an EMC-specific derivation and is not proof "
                    "of one. It is recorded as what it is. A full paper, or a protocol, would "
                    "settle it in one sentence."),
            },
            "H1_80pct": {
                "matches": "pazopanib_phase2",
                "converted_value_pct": pct(paz_implied),
                "how": ("the pazopanib EMC trial's published median progression-free survival of 19 "
                        "months implies a 6-month rate of " + str(pct(paz_implied)) + "% under the "
                        "constant-hazard conversion validated in E2"),
                "⚠_this_one_rests_on_a_conversion": (
                    "and the conversion carries a +/- 10-point band, so the match is 'consistent "
                    "with' rather than 'equal to'. It is reported because the pattern it completes "
                    "is coherent: null = EMC on chemotherapy, alternative = EMC on the previous "
                    "trial's drug."),
            },
        },
        "the_emc_specific_benchmark_that_existed_and_was_not_used": {
            "what": ("Drilon 2008's 6-month Kaplan-Meier progression-free rate of 40% on "
                     "chemotherapy, offered by its authors in their own conclusion as 'a benchmark "
                     "... for the study of new agents for the treatment of patients with this "
                     "diagnosis'."),
            "cited_by_the_2019_trial": False,
            "cited_by_the_2025_abstract": False,
            "evidence_for_those_two_answers": (
                "The 2019 EMC stratum's registered design says its null was set 'having considered "
                "the very scarce published information on response rate' -- a response rate, which "
                "Drilon reports as zero, not a progression-free rate, and the design cites no "
                "source. The 2025 abstract cites no source for anything. ⚠ NEITHER STATEMENT IS A "
                "READING OF THE 2019 FULL PAPER'S REFERENCE LIST, which is paywalled and was not "
                "retrieved; the 2019 paper may well cite Drilon 2008 in its introduction. What is "
                "established is narrower and is enough: neither trial's STATED DESIGN JUSTIFICATION "
                "uses the EMC-specific progression benchmark that existed when it was written."),
            "and_it_would_have_made_the_null_LOWER_not_higher": (
                "40% against the 50% actually used. So on this axis the 2025 design was "
                "conservative, not lax, and any argument that the trial cleared an easy bar has to "
                "reckon with the fact that the only EMC-specific 6-month benchmark in print is 10 "
                "points below the null it chose. That is the opposite of the prior hypothesis and it "
                "is reported as such."),
        },
        "the_null_restated_as_a_progression_speed": {
            "why": ("A null expressed as '50% progression-free at 6 months' is hard to sanity-check. "
                    "The same null expressed as a median progression-free survival is immediately "
                    "checkable against the disease's own published medians."),
            "H0_50pct_is_a_median_of_months": round(implied_median(0.50), 2),
            "H1_80pct_is_a_median_of_months": round(implied_median(0.80), 2),
            "published_emc_medians_months": {r["cohort"]: r["published_median_months"]
                                             for r in EMC_SIX_MONTH_ROWS},
            "reading": (
                "The null assumes a disease whose median progression-free survival is 6.0 months. "
                "Four of the five published EMC medians are longer than that -- 8, 9, 13.2 and 19 "
                "months -- and the fifth, Drilon's 5.2 months, is shorter. The alternative assumes "
                "18.6 months, which is within half a month of the pazopanib trial's observed 19. So "
                "the design's two hypotheses bracket the EMC literature almost exactly: H0 is at the "
                "chemotherapy end of it and H1 is at the tyrosine-kinase-inhibitor end. That is a "
                "coherent and defensible way to choose a null AND IT MAKES THE TRIAL A COMPARATIVE "
                "ONE IN A SINGLE-ARM COSTUME."),
        },
        "⭐_verdict_on_appropriateness": {
            "is_the_50pct_null_an_aggressive_histology_import": (
                "NO, on the evidence retrieved. It is not Van Glabbeke's second-line value, and the "
                "one number in the EMC literature it matches exactly is EMC's own."),
            "is_it_therefore_appropriate": (
                "NO -- for a different and more fundamental reason. Every candidate benchmark of "
                "either provenance is measured on patients receiving systemic therapy: Van "
                "Glabbeke's on EORTC trial patients receiving active or inactive regimens, Drilon's "
                "on chemotherapy courses, Stacchiotti 2013's on anthracyclines. NO UNTREATED EMC "
                "PROGRESSION RATE APPEARS ANYWHERE IN THE RETRIEVED RECORD -- E9 records exactly "
                "what was searched, and how far that absence does and does not reach. So a 6-month "
                "progression-free rate benchmarked in this way answers 'does this regimen keep "
                "disease still for longer than the last regimen did', which is a real and useful "
                "question, and it CANNOT answer 'does this regimen keep disease still for longer "
                "than nothing does', which is the question an indolent tumour forces. The endpoint "
                "inherits exactly the confound PUB-ENDPOINT Sec. 6.1 says it cannot remove, and "
                "changing the number does not remove it."),
            "what_would_make_it_appropriate": (
                "Either an untreated or observation-arm EMC progression rate, which was not "
                "retrieved and is not a realistic ask in this disease; or an endpoint that carries "
                "its own control inside each patient, which is what E6 grades and what E7 prices."),
            "⚠_the_scope_of_this_verdict": (
                "It is about a MEASURING INSTRUMENT and its calibration. It is not a statement that "
                "any trial was wrongly conducted, that any conclusion is false, or that any agent "
                "does or does not work. Every one of those would require evidence this file does not "
                "have and does not claim."),
        },
        "trial_this_verdict_is_about": im2["trial"],
    }


# ================================================================================================
# E4 -- what the 2025 design would do against each rung of the EMC ladder
# ================================================================================================
def e4_operating_characteristics():
    im2 = [t for t in TRIAL_DESIGNS if t["registration"] == "NCT03277924"][0]
    p0, p1, alpha, beta = im2["p0"], im2["p1"], im2["alpha"], im2["beta"]
    published = {"n": im2["total_n_planned"], "r": im2["reject_null_if_events_at_least"]}
    derived = single_stage_design(p0, p1, alpha, beta)

    published_alpha = binom_sf(published["r"], published["n"], p0)
    published_power = binom_sf(published["r"], published["n"], p1)

    rungs = []
    for r in EMC_SIX_MONTH_ROWS:
        p = (r["published_6mo_pct"] / 100.0 if r["published_6mo_pct"] is not None
             else surv_at(6.0, r["published_median_months"]))
        rungs.append({
            "cohort": r["cohort"], "year": r["year"], "regimen": r["regimen"],
            "true_6mo_rate_pct": pct(p),
            "basis": "published rate" if r["published_6mo_pct"] is not None else "converted median",
            "P_declares_promising_published_design_15of22": round(
                binom_sf(published["r"], published["n"], p), 4),
            "P_declares_promising_exact_design_%dof%d" % (derived["reject_null_if_at_least"],
                                                          derived["n"]): round(
                binom_sf(derived["reject_null_if_at_least"], derived["n"], p), 4),
        })

    return {
        "question": ("If the true 6-month progression-free rate of the patients enrolled were equal "
                     "to each published EMC value in turn, how often would the 2025 design have "
                     "declared the regimen promising?"),
        "the_design_as_published": {
            **published, "p0": p0, "p1": p1, "stated_alpha": alpha, "stated_beta": beta,
            "exact_one_sided_type_I_error": round(published_alpha, 4),
            "exact_power_at_H1": round(published_power, 4),
        },
        "the_exact_binomial_design_meeting_the_same_stated_error_rates": derived,
        "⚠_these_two_are_not_the_same_design_and_that_is_not_an_error": (
            "An exact single-stage binomial design at H0 = 50%, H1 = 80%, alpha = 0.05, beta = 0.10 "
            "requires " + str(derived["n"]) + " patients with a threshold of "
            + str(derived["reject_null_if_at_least"]) + ". The trial published '15 out of 22', whose "
            "exact one-sided type I error is " + str(round(published_alpha, 4)) + " -- above the "
            "stated 0.05. THIS DOES NOT MEAN THE TRIAL MISCALCULATED: the stage-1 paper of the same "
            "master protocol states that its sample size came from a Brookmeyer-Crowley-like "
            "one-arm one-stage SURVIVAL design with non-parametric estimation, not from a binomial, "
            "and a survival-based design need not land on the same (n, r) as a binomial one. It is "
            "recorded because a reader re-deriving the design from the abstract's stated parameters "
            "will land on " + str(derived["n"]) + "/" + str(derived["reject_null_if_at_least"])
            + " and should know why."),
        "and_the_observed_result_clears_both": {
            "observed": im2["observed"],
            "clears_published_threshold_15_of_22": im2["observed"]["events"] >= published["r"],
            "clears_exact_binomial_threshold": (im2["observed"]["events"]
                                                >= derived["reject_null_if_at_least"]
                                                and im2["observed"]["denom"] >= derived["n"]),
            "note": ("16 of 23 were accrued and analysed against a threshold written for 22, which "
                     "the abstract does not comment on. Both readings are positive, so nothing in "
                     "this file turns on it."),
        },
        "operating_characteristics_against_each_published_emc_rate": rungs,
        "reading": (
            "Against the two EMC-specific rates that are published as rates, the design behaves as a "
            "null should: it would declare promising less than 5% of the time at Drilon's 40% and "
            "just under 5% at Stacchiotti 2013's 50%. Against the rate implied by the largest "
            "published EMC chemotherapy series -- Chiusole 2020's 9-month median, converted -- it "
            "would declare promising about a third of the time. The design is therefore well "
            "calibrated to the chemotherapy era it was implicitly benchmarked against and poorly "
            "calibrated to distinguish the regimen from a modern chemotherapy comparator, which is "
            "a property of the null, not of the regimen."),
        "⛔_what_this_table_is_not": (
            "It is not a re-analysis of the trial and it does not estimate how well any regimen "
            "worked. Each row asks a conditional question about the DESIGN -- 'if the truth were "
            "this number, how often would this rule fire' -- and the numbers it conditions on are "
            "other cohorts' results, not this cohort's patients."),
    }


# ================================================================================================
# E5 -- which published conclusions change, and at what null
# ================================================================================================
def e5_conclusion_sensitivity():
    im2 = [t for t in TRIAL_DESIGNS if t["registration"] == "NCT03277924"][0]
    ev, dn = im2["observed"]["events"], im2["observed"]["denom"]
    lo, hi = wilson(ev, dn)

    candidates = []
    for r in EMC_SIX_MONTH_ROWS:
        if r["cohort"] == "sunitinib_nivolumab_immunosarc2":
            continue
        p = (r["published_6mo_pct"] / 100.0 if r["published_6mo_pct"] is not None
             else surv_at(6.0, r["published_median_months"]))
        pv = binom_sf(ev, dn, p)
        candidates.append({
            "candidate_null_from": r["cohort"], "year": r["year"], "regimen": r["regimen"],
            "null_6mo_rate_pct": pct(p),
            "basis": "published rate" if r["published_6mo_pct"] is not None else "converted median",
            "one_sided_exact_p_for_16_of_23": round(pv, 4),
            "significant_at_0.05": bool(pv <= 0.05),
        })
    candidates.append({
        "candidate_null_from": "the null the trial actually used", "year": 2025,
        "regimen": "-", "null_6mo_rate_pct": 50.0, "basis": "the design's stated H0",
        "one_sided_exact_p_for_16_of_23": round(binom_sf(ev, dn, 0.50), 4),
        "significant_at_0.05": bool(binom_sf(ev, dn, 0.50) <= 0.05)})
    candidates.sort(key=lambda d: d["null_6mo_rate_pct"])

    paz = [t for t in TRIAL_DESIGNS if t["registration"] == "NCT02066285"][0]
    paz_p = binom_sf(paz["observed"]["events"], paz["observed"]["denom"], paz["p0"])

    return {
        "question": ("Exactly which published EMC trial conclusions would read differently if the "
                     "endpoint had been benchmarked against an EMC-specific comparator rather than "
                     "against the threshold each trial chose?"),
        "the_2025_cohort": {
            "observed": im2["observed"],
            "crude_pct": pct(ev / dn),
            "wilson95_pct": [pct(lo), pct(hi)],
            "published_conclusion_verbatim": (
                "The combination of sunitinib and nivolumab has shown to be active in advanced "
                "extraskeletal myxoid chondrosarcoma. Our data suggest that using this combo in "
                "upfront lines provides a greater benefit."),
            "sensitivity_of_that_conclusion_to_the_null": candidates,
            "⭐_the_margin": {
                "p_at_the_null_used": round(binom_sf(ev, dn, 0.50), 4),
                "alpha": 0.05,
                "distance_from_alpha": round(0.05 - binom_sf(ev, dn, 0.50), 4),
                "largest_null_the_result_still_clears_at_0.05_pct": _largest_clearing_null(ev, dn),
                "robustness_of_the_chiusole_row_to_the_conversion_band": {
                    "why_this_check_exists": (
                        "The row that flips the conclusion -- Chiusole 2020 at 63% -- is a "
                        "CONVERTED value, and E2 measures the conversion error at up to 9.5 "
                        "percentage points. A conclusion that survived only at the point estimate "
                        "would be an artifact of the conversion, so the whole band is tested."),
                    "band_pct": [53.0, 73.0],
                    "one_sided_p_at_band_floor": round(binom_sf(ev, dn, 0.53), 4),
                    "one_sided_p_at_point": round(binom_sf(ev, dn, 0.63), 4),
                    "one_sided_p_at_band_ceiling": round(binom_sf(ev, dn, 0.73), 4),
                    "significant_anywhere_in_the_band": bool(binom_sf(ev, dn, 0.53) <= 0.05),
                    "reading": (
                        "Not significant anywhere in the band, including at its most favourable "
                        "end. The band floor of 53% is already above the 50.3% ceiling of nulls "
                        "this result clears, so the finding does not depend on the conversion "
                        "landing on 63% -- it depends only on the Chiusole median being 9 months "
                        "rather than 6, which is published."),
                },
                "reading": (
                    "16 of 23 clears a 50% null at a one-sided exact p of "
                    + str(round(binom_sf(ev, dn, 0.50), 4)) + ", inside alpha = 0.05 by "
                    + str(round(0.05 - binom_sf(ev, dn, 0.50), 4)) + ". Raise the null to the rate "
                    "implied by the largest published EMC chemotherapy series and the same data are "
                    "not significant. THE CONCLUSION IS A PROPERTY OF THE NULL AS MUCH AS OF THE "
                    "DATA, and the null is the number nobody wrote down a source for."),
            },
            "what_would_change_and_what_would_not": {
                "would_change": (
                    "The word 'active'. A single-arm result that clears a null derived from EMC "
                    "patients on chemotherapy supports a comparative statement -- longer disease "
                    "stability than a historical chemotherapy comparator -- and not an activity "
                    "statement, because the comparator is itself a treatment. Under an EMC-specific "
                    "reading the honest sentence names the comparator."),
                "would_NOT_change": (
                    "The counts. 16 of 23 patients free of progression at 6 months is what was "
                    "observed and nothing here disputes it, nor the 13.2-month median, nor the "
                    "safety profile. Nothing in this file re-analyses a patient."),
                "⛔_and_this_is_not_a_claim_that_the_regimen_is_inactive": (
                    "A result that fails to clear a higher null is not evidence of absence. The "
                    "23-patient Wilson interval on the observed rate is " + str(pct(lo)) + "-"
                    + str(pct(hi)) + "%, which contains most of the ladder. What the sensitivity "
                    "shows is that the evidence base cannot separate the candidate nulls, not that "
                    "one of them is true."),
            },
        },
        "the_2019_cohort": {
            "observed": paz["observed"],
            "null_used": paz["p0"],
            "one_sided_exact_p_for_4_of_22_against_p0_0.05": round(paz_p, 4),
            "would_the_conclusion_change": (
                "NO, and this is the cleaner of the two results. Four RECIST objective responses in "
                "22 patients against a 5% null is significant by a wide margin, and an objective "
                "response is the one observation in this disease that natural history struggles to "
                "explain -- PUB-ENDPOINT Sec. 7.2 makes exactly that point. The 2019 trial's "
                "difficulty is not its threshold; it is that its endpoint could only ever describe 4 "
                "of the 22 patients it enrolled."),
            "what_would_change_is_what_ELSE_it_reported": (
                "No Choi read of the EMC stratum has been published, in a protocol that judged its "
                "sibling stratum on the same drug by Choi at a 40% null and whose registered "
                "primary-outcome text names both criteria (see "
                "sibling_stratum_in_the_same_protocol for why that text is ambiguous and what is "
                "claimed here instead). No 6-month progression-free rate has been published either, "
                "although the 12- and 24-month rates were. Both are readable off scans the trial "
                "has already taken."),
        },
        "the_field_level_consequence": (
            "A re-reading of the whole EMC systemic-therapy literature under a progression-based "
            "endpoint is NOT POSSIBLE from what is published. " + DISCORDANCE_REL + " -> "
            "D3_reporting_completeness records that a 6-month progression-free status is extractable "
            "as an integer count for 1 of 9 cohorts. This file adds two more cohorts that publish "
            "the rate without a count, which raises the number of cohorts with ANY 6-month figure "
            "from 1 to 3 of 9 -- and leaves 6 of 9 with none. The endpoint the field migrated to is "
            "still the one it reports least."),
    }


def _largest_clearing_null(ev: int, dn: int, alpha: float = 0.05) -> float:
    """The largest null hypothesis (to 0.1 percentage points) that the observed count still clears
    one-sided at alpha. This is the honest way to state 'how much room did the conclusion have'.

    ⚠ P(X >= ev | p) is INCREASING in p, so the set of nulls a fixed count clears is an interval
    running from 0 upward and the answer is its TOP. The first version of this function returned the
    first p it found with sf <= alpha, which is the BOTTOM of that interval and is always ~0.1% -- a
    number that looked like a result and was an artifact of the scan direction. Kept as a comment
    because a monotone search returning the wrong end is silent: nothing errors, and 0.1% reads as a
    startling finding rather than as a bug."""
    best = None
    for p in range(1, 1000):
        if binom_sf(ev, dn, p / 1000.0) <= alpha:
            best = p / 10.0
        else:
            break
    return best


# ================================================================================================
# E6 -- the endpoint matrix
# ================================================================================================
def e6_endpoint_matrix(disc, by_key):
    census = disc["D3_reporting_completeness"]["extractable"]
    n_cohorts = disc["D3_reporting_completeness"]["denominator"]["total_rows_considered"]

    def row(key, **kw):
        kw["endpoint"] = key
        return kw

    rows = [
        row("objective_response_rate",
            what_it_measures="proportion of patients whose tumour shrinks by a criterion amount",
            power_at_n_about_20=("POOR. The pooled EMC rate is "
                                 + str(disc["D1_same_patients_two_endpoints"]["objective_response"]
                                       ["proportion_pct"]) + "%, so a 20-patient trial has a "
                                 "material chance of observing no event at all, which is "
                                 "uninterpretable rather than negative -- " + DISCORDANCE_REL
                                 + " -> D4 owns that arithmetic."),
            natural_history_immunity=("HIGH. A confirmed shrinkage is the one observation in this "
                                      "disease that indolence does not readily explain, which is why "
                                      "PUB-ENDPOINT Sec. 7.2 refuses to abandon it."),
            computable_from_published=("YES, best of any endpoint: extractable as integer counts for "
                                       "%d of %d cohorts." % (census["objective_response_counts"]["n"],
                                                              n_cohorts)),
            patient_cost="none additional; it is already collected",
            verdict=("KEEP AS A SECONDARY. Its problem is being used as the SUMMARY, not being "
                     "collected.")),
        row("disease_control_rate",
            what_it_measures="proportion with complete response, partial response or stable disease",
            power_at_n_about_20=("POOR IN THE OPPOSITE DIRECTION. The pooled EMC rate is "
                                 + str(disc["D1_same_patients_two_endpoints"]["disease_control"]
                                       ["proportion_pct"]) + "%, so nearly every patient is an "
                                 "event and there is almost no room to distinguish anything."),
            natural_history_immunity="NONE. This is the confound in its purest form.",
            computable_from_published=("PARTLY: %d of %d cohorts."
                                       % (census["disease_control_counts"]["n"], n_cohorts)),
            patient_cost="none additional",
            verdict="REPORT, NEVER SUMMARISE BY. PUB-ENDPOINT Sec. 6.1 is the reason."),
        row("progression_free_survival_median",
            what_it_measures="the median time from enrolment to progression or death",
            power_at_n_about_20=("MODERATE, and its confidence interval at this n is very wide -- the "
                                 "pazopanib cohort's is 11-27 months on 22-23 patients."),
            natural_history_immunity=("NONE on its own; it acquires some only against a comparator, "
                                      "which is what E3 shows the field has been doing implicitly."),
            computable_from_published=("PARTLY: EMC-specific medians exist for %d of %d cohorts in "
                                       "the census, and this file adds Chiusole 2020's, which the "
                                       "source artifact records as absent -- see "
                                       "corrections_owed_to_the_source_file."
                                       % (census["emc_specific_median_pfs"]["n"], n_cohorts)),
            patient_cost=("high in FOLLOW-UP rather than in patients: a median of 19 months needs "
                          "years of follow-up before it is estimable"),
            verdict="REPORT. Not a primary endpoint at this n, because the interval swamps it."),
        row("progression_free_rate_at_a_fixed_timepoint",
            what_it_measures="proportion progression-free at a stated time, usually 6 months",
            power_at_n_about_20=("GOOD -- it is the only endpoint here whose event rate sits near "
                                 "50-80% in this disease, which is where a binomial design has the "
                                 "most information per patient."),
            natural_history_immunity=("NONE, and E3 is the whole argument: it is only as good as its "
                                      "null, every available null is measured on treated patients, "
                                      "and no untreated EMC rate was retrieved."),
            computable_from_published=("WORST OF THE COMMON ENDPOINTS: extractable as an integer "
                                       "count for %d of %d cohorts; as a published rate for 3 of %d "
                                       "once Drilon 2008 and Stacchiotti 2013 are counted."
                                       % (census["six_month_progression_free_as_a_count"]["n"],
                                          n_cohorts, n_cohorts)),
            patient_cost="none additional; see E8 for what raising the null costs",
            verdict=("KEEP AS PRIMARY, FIX THE BENCHMARK AND STATE IT. The endpoint is right for the "
                     "disease's event rates; its null has never been sourced in print.")),
        row("growth_modulation_index",
            what_it_measures=("the ratio of time to progression on the study treatment to time to "
                              "progression on the patient's immediately preceding treatment "
                              "(TTP2/TTP1), conventionally called a benefit at >= 1.33"),
            power_at_n_about_20=("MODERATE as a proportion endpoint, and it is the only candidate "
                                 "with a published sarcoma-wide reference proportion to be powered "
                                 "against -- see E7."),
            natural_history_immunity=("HIGHEST OF ANY CANDIDATE, AND UNIQUELY SO. Each patient is "
                                      "their own control, so a patient whose disease is intrinsically "
                                      "slow contributes a long TTP1 as well as a long TTP2 and the "
                                      "ratio is unmoved. This is the only endpoint on this list that "
                                      "attacks PUB-ENDPOINT Sec. 6.1 rather than inheriting it."),
            computable_from_published=("NO -- ZERO of 47 patients. See E7. This is the finding that "
                                       "decides the recommendation."),
            patient_cost=("ZERO ADDITIONAL PATIENTS. It reuses the patients a trial is already "
                          "enrolling and needs one extra date per patient. Its cost is data capture, "
                          "not accrual, and that is what makes it the cheapest real improvement "
                          "available."),
            verdict="ADOPT AS A CO-PRIMARY OR MANDATORY SECONDARY. It costs no patients."),
        row("tumour_growth_rate_volumetric",
            what_it_measures=("a continuous growth-rate parameter fitted to serial tumour "
                              "measurements, before and during treatment"),
            power_at_n_about_20=("POTENTIALLY HIGH -- a continuous per-patient slope carries far more "
                                 "information than a binary category, which is the same argument "
                                 "PUB-ENDPOINT Sec. 1.2 makes against categorising a continuous "
                                 "observation."),
            natural_history_immunity=("HIGH IF a pre-treatment growth rate is measured, because that "
                                      "is a within-patient control; NONE if it is not."),
            computable_from_published=("NO. It needs serial per-lesion measurements, which no EMC "
                                       "report publishes. The only per-patient tumour-size datum "
                                       "anywhere in the corpus is the trabectedin sub-analysis's two "
                                       "EMC subjects' change in sum of diameters."),
            patient_cost=("zero additional patients; requires prospective imaging at a fixed cadence "
                          "and archived measurements, plus at least one PRE-treatment scan pair"),
            verdict=("STRONG SECOND CHOICE, BLOCKED ON DATA. Worth prospectively capturing; not "
                     "recoverable from the published record.")),
        row("time_to_next_treatment",
            what_it_measures="time from starting a treatment to starting the next one, or death",
            power_at_n_about_20="MODERATE; it is a time-to-event endpoint with the usual width at n~20.",
            natural_history_immunity=("LOW. In an indolent tumour a clinician may defer the next "
                                      "line for reasons unrelated to the drug, so the endpoint "
                                      "measures decision-making as much as disease. ⚠ The "
                                      "diseases where it IS established are ones with published "
                                      "treatment-initiation criteria, which is what converts "
                                      "that discretion into a rule; EMC has no such criteria, "
                                      "so in EMC the discretion stays unmeasured. THAT LAST "
                                      "CLAUSE IS A JUDGEMENT, not a retrieval -- no search here "
                                      "established the absence of EMC treatment-initiation "
                                      "criteria."),
            computable_from_published=("NO. No EMC report publishes it, and its published use "
                                       "base is somewhere else: a Europe PMC TITLE search for "
                                       "'time to next treatment' returned 26 records, of the 25 "
                                       "returned 18 are titled in an indolent LYMPHOID malignancy "
                                       "(chronic lymphocytic leukaemia, cutaneous T-cell "
                                       "lymphoma / mycosis fungoides, Waldenstrom, follicular "
                                       "lymphoma, myeloma) and ZERO in any sarcoma. ⚠ That is a "
                                       "reading of 25 titles from one query, not a systematic "
                                       "review -- it says where the endpoint is used, not that it "
                                       "could not be used elsewhere."),
            patient_cost="zero additional patients; needs longer follow-up",
            verdict=("NOT RECOMMENDED AS PRIMARY in EMC specifically, because clinician discretion "
                     "about when to treat an indolent tumour is exactly the noise it cannot "
                     "separate.")),
        row("duration_of_response",
            what_it_measures="how long an objective response lasts",
            power_at_n_about_20=("USELESS AS A PRIMARY. It is conditioned on responding, and the "
                                 "pooled EMC response denominator is 6 events in 47 patients."),
            natural_history_immunity="HIGH, but on a sample of six.",
            computable_from_published="NO EMC cohort publishes it.",
            patient_cost="zero additional patients",
            verdict="REPORT WHEN A RESPONSE OCCURS. Never a primary in this disease."),
        row("choi_rather_than_recist",
            what_it_measures=("response by attenuation change as well as size change, developed for "
                              "antiangiogenic treatment of gastrointestinal stromal tumour"),
            power_at_n_about_20=("BETTER THAN RECIST for antiangiogenic agents, because it converts "
                                 "some of the stable-disease mass into a category; unquantified in "
                                 "EMC because no Choi read of any EMC cohort is published."),
            natural_history_immunity=("SAME AS RECIST -- it changes what counts as a response, not "
                                      "whether the change is due to the drug."),
            computable_from_published=("NO, AND THIS IS THE MOST RECOVERABLE MISSING ITEM IN THE "
                                       "WHOLE FILE. The 2019 trial registered its primary outcome as "
                                       "response 'measured using Choi and RECIST 1.1 criteria' and "
                                       "powered its sibling SFT stratum on Choi at a 40% null, so "
                                       "the measurements exist in that trial's database and have "
                                       "never been printed for EMC. ⚠ IMMUNOSARC's registered "
                                       "outcome list carries Choi response ONLY for its stage-1 "
                                       "phase 2 population; the stage-2 EMC cohort's registered "
                                       "outcomes do not include it, so the 2025 cohort is NOT a "
                                       "second source for this item."),
            patient_cost="ZERO. The scans have already been taken and the criterion is registered.",
            verdict=("PUBLISH THE CHOI READ THAT WAS ALREADY REGISTERED. It costs no patients, no "
                     "scans and no money, and it is the one item here that a single existing trial "
                     "group can supply unilaterally.")),
        row("randomized_discontinuation_design",
            what_it_measures=("not an endpoint but a DESIGN: treat everyone, then randomise only the "
                              "patients with stable disease to continue or to placebo"),
            power_at_n_about_20=("NOT ACHIEVABLE. It needs enough patients to reach the randomised "
                                 "stage AFTER a run-in, and the two modern EMC trials accrued 26 and "
                                 "24 patients over three and four years respectively across 9-11 "
                                 "European centres."),
            natural_history_immunity=("COMPLETE, and it is the only option on this list that is. It "
                                      "was invented for this exact problem -- see "
                                      "randomized_discontinuation_design_sources."),
            computable_from_published="not applicable; it is a design, not a re-analysis",
            patient_cost=("THE HIGHEST BY FAR. Every patient randomised to placebo is a patient the "
                          "disease's total accrual cannot spare, and the design is additionally "
                          "known to be LESS efficient than upfront randomisation under some growth "
                          "models (PMID 15983399)."),
            verdict=("THE RIGHT ANSWER TO THE RIGHT QUESTION, AND UNAFFORDABLE IN THIS DISEASE. "
                     "Naming it is not proposing it -- PUB-ENDPOINT Sec. 7.3 already said so.")),
    ]
    return {
        "question": ("Graded against three criteria that were fixed before the grading: statistical "
                     "power at the n this disease can accrue; immunity to the natural-history "
                     "confound; and computability from what is already published."),
        "criteria": {
            "power_at_achievable_n": ("n is about 20-25. The two modern prospective EMC cohorts "
                                      "enrolled 22 and 23 response-evaluable patients."),
            "natural_history_immunity": ("does the endpoint contain its own control, or does it "
                                         "borrow one from a historical cohort that was also treated?"),
            "computable_from_published_data": ("can it be recovered from the 9 EMC cohort rows in "
                                               + POOLING_REL + " under POLICY-evidence 2.1?"),
        },
        "rows": rows,
        "randomized_discontinuation_design_sources": RDD_SOURCES,
        "growth_modulation_index_sources": GMI_METHOD_SOURCES,
        "⭐_the_recommendation": {
            "headline": ("NO SINGLE ENDPOINT SATISFIES ALL THREE CRITERIA, AND SAYING OTHERWISE "
                         "WOULD BE THE ERROR PUB-ENDPOINT CRITICISES. The recommendation is a PAIR, "
                         "because the two halves fix different failures and neither costs a patient."),
            "primary": ("KEEP the 6-month progression-free rate -- it is the only endpoint whose "
                        "event rate sits where a 20-patient binomial design has information -- but "
                        "REQUIRE THE NULL TO BE SOURCED IN PRINT, and source it to an EMC-specific "
                        "published figure. Two exist: Drilon 2008's 40% and Stacchiotti 2013's 50%. "
                        "A trial that states which one it used, and why, can be argued with; the "
                        "2025 abstract cannot."),
            "co_primary_or_mandatory_secondary": (
                "THE GROWTH MODULATION INDEX. It is the only candidate that carries its own control "
                "inside each patient, it costs ZERO additional patients, and its entire cost is one "
                "extra date per patient -- the date of progression on the immediately preceding "
                "line, which is in every enrolling centre's notes and is in nobody's published "
                "table. It is the cheapest available answer to the objection PUB-ENDPOINT states as "
                "the one that would sink it."),
            "free_immediate_item": ("PUBLISH THE CHOI READ AND THE 6-MONTH COUNT FOR THE 2019 EMC "
                                    "STRATUM. Both are registered outcome measures of a completed "
                                    "trial, both are already in its database, and neither has been "
                                    "printed."),
            "what_is_explicitly_NOT_recommended": (
                "A randomised discontinuation design, which is the only complete answer and is "
                "unaffordable at this disease's accrual; and time to next treatment, which in an "
                "indolent tumour measures clinician discretion. Naming a design is not proposing it."),
            "⛔_and_none_of_this_is_a_treatment_recommendation": (
                "Every sentence above is about how to MEASURE a trial in this disease. Nothing here "
                "says any agent should or should not be given to any patient, and the choice of "
                "endpoint has no bearing on which treatment a person with EMC should receive, which "
                "belongs with a specialist sarcoma centre."),
        },
    }


# ================================================================================================
# E7 -- can the recommended endpoint actually be computed? A data-availability census.
# ================================================================================================
def e7_gmi_data_availability(pooling, by_key):
    prospective = ["pazopanib_phase2", "sunitinib_nivolumab_immunosarc2", "trabectedin_emc_subset"]
    rows = []
    n_patients_with_per_patient_ttp = 0
    n_patients_with_prior_line_ttp = 0
    total_prospective = 0
    for c in pooling["cohorts"]:
        per = c.get("per_patient_emc")
        denom = c.get("orr_denom") or c.get("n_started")
        prior_fields = _prior_line_ttp_fields(c)
        if c["key"] in prospective:
            total_prospective += denom or 0
            if per:
                n_patients_with_per_patient_ttp += len(per)
            if prior_fields:
                n_patients_with_prior_line_ttp += denom or 0
        rows.append({
            "cohort": c["key"],
            "prospective": bool(c.get("prospective")),
            "publishes_per_patient_time_to_progression_on_study": bool(per),
            "n_patients_with_a_per_patient_value": len(per) if per else 0,
            "publishes_time_to_progression_on_the_PRIOR_line": bool(prior_fields),
            "fields_that_could_have_carried_one": prior_fields,
            "what_it_publishes_about_prior_therapy": _prior_line_note(c),
        })

    return {
        "question": ("The recommended co-primary is the growth modulation index. Can it be computed, "
                     "for even one EMC patient, from anything that has been published?"),
        "what_the_index_needs": ("two dated intervals per patient -- time to progression on the "
                                 "immediately preceding line (TTP1) and on the study treatment "
                                 "(TTP2). Neither may be a cohort median; both must be per-patient."),
        "rows": rows,
        "counts": {
            "prospective_trial_patients_in_the_pooled_set": total_prospective,
            "with_a_published_per_patient_time_to_progression_on_study": n_patients_with_per_patient_ttp,
            "with_a_published_per_patient_time_to_progression_on_the_prior_line":
                n_patients_with_prior_line_ttp,
            "cohorts_publishing_any_per_patient_time_to_progression": sum(
                1 for r in rows if r["publishes_per_patient_time_to_progression_on_study"]),
            "cohorts_publishing_prior_line_time_to_progression": 0,
        },
        "⭐_the_answer": (
            "NO -- FOR ZERO PATIENTS. Exactly one of the nine curated EMC cohorts prints a "
            "per-patient time to progression: the trabectedin sub-analysis's Table 2, which gives "
            "13.0 and 7.4 months for its two EMC subjects. NONE of the nine gives any patient's "
            "time to progression on their PREVIOUS line of therapy -- the predicate above scans "
            "every field of every committed row for one and returns nothing. The growth modulation "
            "index is therefore computable for 0 of the 47 patients evaluated for response inside "
            "a prospective EMC trial, and for 0 in the retrospective rows as well. ⚠ THE SCOPE OF "
            "THIS IS THE CURATED CORPUS, WHICH IS EVERY SYSTEMIC-THERAPY REPORT THIS REPOSITORY "
            "HAS FOUND FOR EMC -- it is a reading of nine reports, not a proof about a literature "
            "nobody has fully enumerated. The distinction does not soften the conclusion: one "
            "unfound report would move the count from 0 to a handful, and a handful of paired "
            "intervals is still not an analysis."),
        "the_near_misses_make_the_point_sharper": {
            "immunosarc2_prior_antiangiogenic": (
                "The 2025 abstract reports that 6 of 23 patients had received a prior antiangiogenic "
                "and compares their median progression-free survival on study (7 months versus 13). "
                "So the trial HAS the prior-line information at patient level -- it stratified on "
                "it -- and published a group median instead of the paired intervals. This is the "
                "closest any EMC report comes, and it stops one column short."),
            "pazopanib_line_of_therapy": (
                "The 2019 trial required RECIST progression in the previous 6 months as an entry "
                "criterion, which means the DATE of the previous progression was recorded for every "
                "enrolled patient by protocol. The interval before it -- the start of the prior line "
                "-- is in the same case report forms."),
            "reading": ("The data exists. It has been collected, by protocol, in both trials. It has "
                        "not been printed. That is a REPORTING failure, not a measurement one, and "
                        "PUB-ENDPOINT Sec. 4.2 found the same shape for the endpoint counts."),
        },
        "⭐_the_minimal_ask": {
            "what": ("For each patient in the two prospective EMC cohorts, one anonymised row: date "
                     "of start of the immediately preceding systemic line, date of progression on "
                     "it, date of start of study treatment, date of progression on study or "
                     "censoring. Four dates. No new patient, no new scan, no new consent beyond what "
                     "trial protocols already cover for anonymised outcome data."),
            "who_can_supply_it": ("the trial groups that ran both -- the same Spanish, Italian, "
                                  "French and UK sarcoma networks appear on both papers"),
            "how_many_patients_it_would_yield": {
                "upper_bound": ("45 -- the 22 evaluable in the 2019 trial plus the 23 evaluable in "
                                "the 2025 cohort"),
                "realistic_bound": ("smaller, because the index is undefined for a treatment-naive "
                                    "patient: 13 of 24 in the 2025 cohort were treatment-naive, so "
                                    "at most 11 of that cohort could contribute, and the 2019 trial "
                                    "enrolled after anthracycline in most but not all patients"),
                "⚠_and_the_two_cohorts_are_not_independent": (
                    "PUB-ENDPOINT Sec. 6.5 records that some of the 6 previously-antiangiogenic "
                    "patients in the 2025 cohort may be patients from the 2019 trial. For a growth "
                    "modulation index that is not a contamination -- it is the ideal case, a patient "
                    "whose TTP1 is another trial's measured endpoint -- but it must be declared."),
                "⭐_and_the_overlap_can_only_run_ONE_WAY_which_makes_it_cleaner_still": (
                    "The 2019 trial's Exclusion Criteria, read from the ClinicalTrials.gov v2 "
                    "record fetched for this file, contain verbatim: 'Patients who have received "
                    "previous antiangiogenic agents.' So a patient who had already had an "
                    "antiangiogenic could not enter the 2019 trial, while nothing stops a 2019 "
                    "trial patient from later entering the 2025 cohort -- where they would be one "
                    "of the 6 of 23 recorded as previously antiangiogenic-treated. The overlap "
                    "therefore runs 2019 -> 2025 and cannot run the other way. For a paired-interval "
                    "endpoint that is the best case available in this disease: TTP1 would be a "
                    "PROTOCOL-MEASURED endpoint of a published trial rather than a date recovered "
                    "from notes. ⚠ THIS IS THE PROTOCOL'S RULE, NOT A PATIENT-LEVEL AUDIT -- "
                    "registries publish eligibility criteria, not enrolment decisions, and waivers "
                    "and deviations appear in neither. The honest form is 'the trial's own "
                    "criterion excludes it', never 'no patient appeared in both'. Same criterion, "
                    "same wording, independently corroborated on the EU Clinical Trials Register "
                    "for EudraCT 2013-005456-15 by a sibling retrieval the same day -- "
                    "research/manuscripts/partner-event-counts-2026-08-08.md Sec. 3."),
            },
            "why_this_is_the_ask_and_not_a_new_trial": (
                "Because it converts a completed, already-funded, already-consented body of work "
                "into the one endpoint that answers the objection nobody can otherwise answer, at a "
                "cost of four dates per patient and zero additional patients. Every other route to "
                "the same answer -- an observation arm, a randomised discontinuation design, a "
                "prospective growth-rate study -- costs patients this disease does not have."),
        },
        "if_it_were_supplied_what_would_it_be_powered_against": _gmi_reference_pool(),
        "⛔_what_this_section_does_not_claim": (
            "It does not claim that a growth modulation index computed on these patients would show "
            "anything in particular, in either direction. It claims only that the quantity is "
            "currently uncomputable and that four dates per patient would make it computable. A "
            "negative about data availability is a result; a prediction about what the data would "
            "show would not be."),
    }


def _prior_line_ttp_fields(c):
    """Any field on a cohort row that could carry a time to progression on the PRIOR line.

    ⚠ DERIVED, NOT ASSERTED. The count of patients for whom a growth modulation index is computable
    is the load-bearing negative of this whole file, so it must not be a number typed by whoever
    happened to read the rows. This predicate scans every key of every committed cohort row for a
    field naming both a prior line and a time-to-event quantity; an empty result across all rows IS
    the census. If a future edit adds such a field, the count moves on its own -- which is exactly
    what CLAUDE.md Sec. 4 means by checking the thing only a real record can produce."""
    hits = []
    for k in c:
        kl = k.lower()
        if ("prior" in kl or "previous" in kl or "preceding" in kl or "ttp1" in kl) and \
           ("ttp" in kl or "pfs" in kl or "time" in kl or "progress" in kl or "interval" in kl):
            hits.append(k)
    return hits


def _prior_line_note(c):
    line = c.get("line")
    if not line:
        return "nothing"
    return ("the line of therapy is described in words ('" + str(line) + "') with no per-patient "
            "dates or intervals")


def _gmi_reference_pool():
    ev = sum(r["gmi_gt_133_events"] for r in GMI_REFERENCE_ROWS)
    dn = sum(r["denom"] for r in GMI_REFERENCE_ROWS)
    lo, hi = wilson(ev, dn)
    return {
        "rows": GMI_REFERENCE_ROWS,
        "pooled": {
            "events": ev, "denom": dn, "proportion_pct": pct(ev / dn),
            "wilson95_pct": [pct(lo), pct(hi)],
            "method": ("crude denominator-weighted proportion with a Wilson score 95% interval, "
                       "POLICY-evidence 2.2, over explicit integer counts only"),
            "what_it_is": ("the proportion of advanced soft-tissue-sarcoma patients whose growth "
                           "modulation index exceeded 1.33 on a subsequent line of treatment, "
                           "across two national sarcoma groups"),
            "non_overlap_argument": ("one French Sarcoma Group series and one Spanish sarcoma-group "
                                     "series, different countries and different regimens -- "
                                     "POLICY-evidence 2.3 permits pooling distinct populations. "
                                     "⚠ NEITHER SERIES CONTAINS ANY STATED EMC PATIENT and this is "
                                     "NOT an EMC figure; it is the sarcoma-wide reference a "
                                     "first-ever EMC growth-modulation-index design would have to "
                                     "be powered against, in the absence of anything closer."),
            "⚠_and_it_is_a_treated_reference_too": (
                "Both series measure patients receiving a subsequent line of therapy, so this "
                "reference proportion inherits the same limitation as every benchmark in E3. What "
                "the index fixes is the WITHIN-PATIENT confound; it does not by itself supply an "
                "untreated comparator, and this file does not claim it does."),
        },
    }


# ================================================================================================
# E8 -- what each change costs, in patients
# ================================================================================================
def e8_patient_cost():
    scenarios = [
        {"label": "the 2025 design as published", "p0": 0.50, "p1": 0.80,
         "why": "H0 and H1 as stated in the abstract"},
        {"label": "null sourced to Drilon 2008's EMC 6-month rate", "p0": 0.40, "p1": 0.80,
         "why": "the lower of the two published EMC-specific 6-month rates"},
        {"label": "null sourced to Chiusole 2020's largest EMC chemotherapy series",
         "p0": round(surv_at(6.0, 9.0), 3), "p1": 0.85,
         "why": ("its 9-month median converted; the alternative is raised in step so the design "
                 "still asks a comparably sized question")},
        {"label": "null at the pazopanib-implied rate (a same-class active comparator)",
         "p0": round(surv_at(6.0, 19.0), 3), "p1": 0.92,
         "why": "what it would cost to ask whether a new regimen beats the current best EMC result"},
        {"label": "a growth-modulation-index proportion endpoint against the sarcoma reference",
         "p0": 0.32, "p1": 0.60,
         "why": ("the pooled proportion with index > 1.33 across two national sarcoma series, "
                 "rounded; see E7 -> if_it_were_supplied_what_would_it_be_powered_against")},
    ]
    out = []
    for s in scenarios:
        d90 = single_stage_design(s["p0"], s["p1"], 0.05, 0.10)
        d80 = single_stage_design(s["p0"], s["p1"], 0.05, 0.20)
        out.append({**s,
                    "exact_single_stage_n_at_90pct_power": d90,
                    "exact_single_stage_n_at_80pct_power": d80,
                    "feasible_at_this_disease_accrual": (
                        "the two modern EMC cohorts accrued 26 and 24 patients over 2014-2017 and "
                        "2020-2024 respectively, so an n above roughly 30 is a decade of "
                        "international accrual")})
    return {
        "question": "What does each proposed change cost, measured in patients?",
        "method": ("exact single-stage single-arm binomial designs, one-sided alpha 0.05, at 90% and "
                   "80% power. Two-stage designs would be smaller in expectation and are not "
                   "computed here; the single-stage figure is the honest upper bound and it is the "
                   "same machinery for every row, so the rows are comparable."),
        "scenarios": out,
        "⭐_the_cost_summary": {
            "raising_the_null_from_50_to_63_percent": (
                "takes the trial from " + str(out[0]["exact_single_stage_n_at_90pct_power"]["n"])
                + " patients to " + str(out[2]["exact_single_stage_n_at_90pct_power"]["n"])
                + " at 90% power, a factor of "
                + str(round(out[2]["exact_single_stage_n_at_90pct_power"]["n"]
                            / out[0]["exact_single_stage_n_at_90pct_power"]["n"], 2))
                + ". That is the real price of the E3 verdict and it is why the recommendation is "
                "NOT 'raise the null': at this disease's accrual, that factor means not running the "
                "trial. Asking whether a new regimen beats the pazopanib result costs "
                + str(out[3]["exact_single_stage_n_at_90pct_power"]["n"]) + " -- three times what "
                "the disease has ever accrued into one cohort."),
            "sourcing_the_null_in_print": "ZERO patients. It is a sentence.",
            "adding_a_growth_modulation_index": (
                "ZERO additional patients. It reuses the enrolled cohort and adds one date per "
                "patient. The n column for the index row above is what a STANDALONE index-primary "
                "trial would cost; as a co-primary on a trial that is happening anyway, the marginal "
                "patient cost is nil."),
            "publishing_the_choi_read_and_the_six_month_count_for_the_2019_stratum":
                "ZERO patients. Both are registered outcome measures of a completed trial.",
            "a_randomised_discontinuation_design": (
                "not costed here, because it requires assumptions about the run-in stabilisation "
                "rate that no EMC data supports; what is certain is that it costs MORE than any row "
                "above, since every row above is single-arm."),
        },
        "reading": (
            "The three changes that cost nothing are the three this file recommends. The one change "
            "that would most directly fix the benchmark -- raising the null -- is the one the disease "
            "cannot afford, which is exactly why the benchmark has to be fixed by making it "
            "auditable and by adding a within-patient control, rather than by making the bar higher."),
    }


# ================================================================================================
# Corrections owed to the source artifact
# ================================================================================================
def corrections_owed(pooling):
    return {
        "policy": ("CLAUDE.md rule 1.2 and the pattern set by " + DISCORDANCE_REL
                   + " -> D5: a discrepancy found in a source file is RECORDED here, dated and with "
                     "its evidence, and FIXED in the file that owns the sentence. This file does not "
                     "edit that file."),
        "items": [
            {
                "id": "C1_chiusole_does_report_a_median_pfs",
                "where": POOLING_REL + " -> analyses.A5_time_to_event_never_pooled."
                                       "figures_that_are_NOT_emc_medians_but_circulate_as_such",
                "the_source_says": ("Chiusole 2020 reports no median PFS for its chemotherapy "
                                    "patients."),
                "what_the_full_text_says": ("Median progression-free survival for patients receiving "
                                            "first-line chemotherapy was 9 months."),
                "and_again_in_its_discussion": ("In our study, we observed a progression-free "
                                                "survival time of 9 months, which is higher than "
                                                "what was reported by Drillon et al. in 2008 in 21 "
                                                "patients (5.2 months) and consistent with data "
                                                "reported in 2013 on the use of anthracyclines in 11 "
                                                "patients in the series by Stacchiotti et al. (8 "
                                                "months), but shorter than median progression-free "
                                                "survival achieved with Pazopanib in a recent phase "
                                                "II trial that enrolled 23 patients (19 months)."),
                "evidence": CACHE2 + "/epmc_ft_chiusole_PMC7308468.txt (HTTP 200, Europe PMC "
                                     "fullTextXML)",
                "severity": ("MODERATE, and it cuts against this repository rather than for it. The "
                             "correction the source row actually carries -- that 5.2 months belongs "
                             "to Drilon 2008 and not to Chiusole 2020 -- is CORRECT and stands. The "
                             "additional sentence it appended, that Chiusole reports no median at "
                             "all, is falsified by that paper's own Results and Discussion. A FOURTH "
                             "EMC-specific median progression-free survival exists and this "
                             "repository recorded that it did not."),
                "why_it_matters_to_this_file": ("Chiusole 2020's 9-month median is the largest "
                                                "published EMC chemotherapy experience and is the "
                                                "candidate null under which the 2025 cohort's result "
                                                "stops being significant (E5). A finding that rests "
                                                "on a number the source file says does not exist "
                                                "would be worthless, which is why it was checked "
                                                "against the full text before being used."),
                "correction_owed_to": POOLING_REL,
            },
            {
                "id": "C2_two_emc_six_month_rates_exist_and_are_not_recorded",
                "where": POOLING_REL + " -> analyses.A6_six_month_progression_free",
                "the_source_says": ("there is only one EMC cohort that reports it as an integer "
                                    "count"),
                "status": "TRUE AND NOT A DEFECT",
                "what_is_nonetheless_missing": (
                    "A6 answers the poolability question correctly and completely. What no artifact "
                    "in this repository records is that two EMC cohorts publish a 6-month "
                    "progression-free RATE without a count -- Drilon 2008 at 40% and Stacchiotti "
                    "2013 at 50% -- and that the first of them was offered by its own authors as a "
                    "benchmark for future trials. Those two figures cannot be pooled and are the "
                    "best EMC-specific calibration the endpoint has."),
                "correction_owed_to": ("nothing -- this is an ADDITION, and its home is this file's "
                                       "E2. It is listed here so a reader of A6 is not left "
                                       "believing the disease has no 6-month benchmark."),
            },
        ],
    }


# ================================================================================================
# Build
# ================================================================================================
def build():
    pooling, disc, by_key = load_sources()
    return {
        "_schema": "emc-endpoint-alternatives/1",
        "_generated_by": "research/manuscripts/emc_endpoint_alternatives.py",
        "_generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_do_not_hand_edit": (
            "Regenerate with `python3 research/manuscripts/emc_endpoint_alternatives.py`. Integer "
            "counts and citations come from " + POOLING_REL + "; the reporting census comes from "
            + DISCORDANCE_REL + "; every other figure is either arithmetic over those, or a "
            "retrieved constant carried in this file's source WITH the verbatim quote and the "
            "literature-cache path it was read from. Hand-editing would sever a value from its "
            "quote, which is the only thing that makes any of it checkable."),
        "title": ("What should be measured in advanced extraskeletal myxoid chondrosarcoma, what the "
                  "field's chosen endpoint is benchmarked against, and how the published record "
                  "reads when the benchmark is named"),
        "answers_the_questions": {
            "A": "what outcome variable should be tracked in advanced EMC",
            "B": ("how the published trial record would read differently if that variable, and a "
                  "sourced benchmark, had been used"),
        },
        "method": {
            "policy": "systems/POLICY-evidence.md sections 2.1-2.4",
            "pooling": "crude denominator-weighted proportions",
            "interval": "Wilson score 95%",
            "counts": "explicit integers only; never back-derived from a published percentage",
            "populations": "non-overlapping only",
            "time_to_event": "never merged",
            "design_arithmetic": ("exact binomial, no normal approximation, because at n around 20 "
                                  "the approximation is the difference between a design that holds "
                                  "its stated alpha and one that does not"),
            "the_one_modelling_assumption": ("a constant hazard, used ONLY to convert a published "
                                             "median into a fixed-timepoint rate where no rate was "
                                             "published, and validated against the three EMC cohorts "
                                             "that publish both"),
            "sources_of_committed_counts": [POOLING_REL, DISCORDANCE_REL],
            "retrieval_corpus_for_every_other_figure": CORPUS_REL,
        },
        "E1_design_ledger": e1_design_ledger(disc),
        "E2_emc_six_month_progression_free_ladder": e2_six_month_ladder(),
        "E3_benchmark_provenance": e3_benchmark_provenance(),
        "E4_operating_characteristics": e4_operating_characteristics(),
        "E5_conclusion_sensitivity": e5_conclusion_sensitivity(),
        "E6_endpoint_matrix": e6_endpoint_matrix(disc, by_key),
        "E7_growth_modulation_index_data_availability": e7_gmi_data_availability(pooling, by_key),
        "E8_patient_cost": e8_patient_cost(),
        "E9_the_natural_history_gap": EMC_NATURAL_HISTORY,
        "E10_indolent_tumour_placebo_calibration": _e10(),
        "corrections_owed_to_the_source_file": corrections_owed(pooling),
        "candidate_endpoints_considered": CANDIDATE_ENDPOINTS,
        "not_a_recommendation": (
            "Nothing here endorses, discourages or ranks any therapy, and nothing here states or "
            "implies that any agent is effective, safe, selective, or ready for clinical use in EMC. "
            "The subject of this file is the measuring instrument: which endpoint, read against "
            "which null, computed from which published quantity. Where a trial's stated conclusion "
            "is shown to depend on its choice of null, that is a finding about the null. It is not a "
            "finding about the treatment, it is not a re-analysis of any patient, and it must never "
            "be quoted as evidence that any regimen did or did not work. Treatment decisions in EMC "
            "belong with a specialist sarcoma centre."),
    }


def _e10():
    """E10 wraps the retrieved constants and adds the one derived quantity: a Wilson interval on the
    untreated desmoid observation cohort, so that a 14-of-19 count is never quoted as a point."""
    ev = INDOLENT_TUMOUR_PLACEBO_CALIBRATION["untreated_observation_cohort"][
        "progression_free_at_12_months"]["events"]
    dn = INDOLENT_TUMOUR_PLACEBO_CALIBRATION["untreated_observation_cohort"][
        "progression_free_at_12_months"]["denom"]
    lo, hi = wilson(ev, dn)
    out = json.loads(json.dumps(INDOLENT_TUMOUR_PLACEBO_CALIBRATION))
    out["untreated_observation_cohort"]["progression_free_at_12_months"].update({
        "proportion_pct": pct(ev / dn),
        "wilson95_pct": [pct(lo), pct(hi)],
        "method": "Wilson score 95% on explicit integer counts, POLICY-evidence 2.2",
        "⚠": ("the interval spans most of the plausible range, which is what n = 19 buys. It is "
              "reported so the point estimate is never quoted alone."),
    })
    out["question"] = ("Is the natural-history component of a progression-based endpoint a "
                       "theoretical worry, or has anyone ever measured it in an indolent "
                       "soft-tissue tumour?")
    return out


def _strip_volatile(obj):
    return {k: v for k, v in obj.items() if k != "_generated_utc"}


def main():
    ap = argparse.ArgumentParser(description="EMC endpoint alternatives and benchmark provenance")
    ap.add_argument("--check", action="store_true",
                    help="re-derive and compare against the committed JSON; exit 1 on any drift")
    args = ap.parse_args()

    built = build()

    if args.check:
        if not os.path.exists(OUT):
            print("FAIL: %s does not exist" % OUT, file=sys.stderr)
            return 1
        with open(OUT, encoding="utf-8") as fh:
            committed = json.load(fh)
        if _strip_volatile(committed) != _strip_volatile(built):
            print("FAIL: %s differs from a fresh derivation. Regenerate it." % OUT, file=sys.stderr)
            return 1
        print("emc_endpoint_alternatives --check: OK (committed artifact reproduces exactly)")
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(built, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    e2 = built["E2_emc_six_month_progression_free_ladder"]
    e5 = built["E5_conclusion_sensitivity"]
    print("wrote %s" % OUT)
    print("  EMC 6-month progression-free ladder (%d rows, span %.1f pts):"
          % (len(e2["the_ladder"]), e2["span_pct_points"]))
    for row in e2["the_ladder"]:
        print("    %-38s %5.1f%%  (%s)" % (row["cohort"], row["six_month_progression_free_pct"],
                                           row["basis"]))
    print("  conversion validated to within %.1f pts on %d cohorts"
          % (e2["conversion_validation"]["max_absolute_error_pct_points"],
             len(e2["conversion_validation"]["rows"])))
    print("  2025 cohort, 16/23, one-sided exact p against each candidate null:")
    for c in e5["the_2025_cohort"]["sensitivity_of_that_conclusion_to_the_null"]:
        print("    null %5.1f%% (%-32s) p=%.4f  %s"
              % (c["null_6mo_rate_pct"], c["candidate_null_from"],
                 c["one_sided_exact_p_for_16_of_23"],
                 "significant" if c["significant_at_0.05"] else "NOT significant"))
    print("  growth modulation index computable for %d of %d prospective-trial patients"
          % (built["E7_growth_modulation_index_data_availability"]["counts"]
             ["with_a_published_per_patient_time_to_progression_on_the_prior_line"],
             built["E7_growth_modulation_index_data_availability"]["counts"]
             ["prospective_trial_patients_in_the_pooled_set"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
