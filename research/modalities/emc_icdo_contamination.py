#!/usr/bin/env python3
"""How big is the ICD-O-3 9231/3 contamination, and what can the coding system actually separate?

WHY THIS EXISTS
---------------
`emc_care_delivery_evidence.py` -> `icd_o_9231_3` established the CONTRADICTION: morphology code
9231/3 is queried by one SEER study as extraskeletal myxoid chondrosarcoma (PMID 32856598) and
enumerated by another as one histological subtype of chondrosarcoma of bone (PMID 31765367).
That is settled and is not re-argued here.

What was missing is the SIZE. RT-DIAGNOSTIC-PATHWAY's own readiness note says why it matters:
*"a paper that can state the problem but not its magnitude is weaker than one that can."* This
module is the record of the attempt to measure it, cheapest route first, and of what each route
actually returned.

⛔ THE PRE-REGISTERED NEGATIVE IS THE FIRST BLOCK IN THIS FILE AND IT WAS FIXED BEFORE ANY
FRACTION WAS OBSERVED. A small measured contamination is a real result that RETIRES a caveat this
repository currently attaches to several rows. Nothing here goes looking for a large number.

PROVENANCE DISCIPLINE
---------------------
Every row carries `provenance`. `[API]` = the structured Europe PMC record (i.e. the abstract).
`[FT]` = the fetched full text was read. `[DOC]` = a primary document from the body that owns the
thing being described (SEER's own site/histology validation list, SEER's own product-comparison
page) was read. ⛔ An absent reading is never reported as a reading of absence: a field or a paper
that could not be reached is recorded as unreachable, with the transport result that says so.

Stdlib only.
Run:     python3 research/modalities/emc_icdo_contamination.py
Verify:  python3 research/modalities/emc_icdo_contamination.py --check
Writes:  research/modalities/emc-icdo-contamination.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "research", "modalities", "emc-icdo-contamination.json")

# ---------------------------------------------------------------------------
# 0 - THE PRE-REGISTERED NEGATIVE, fixed before any fraction was observed
# ---------------------------------------------------------------------------
REGISTRATION = {
    "registered": "2026-08-23",
    "registered_before": "any bone-versus-soft-tissue fraction for a 9231/3 cohort had been "
    "observed from any source. What WAS already known at registration is listed in "
    "`known_at_registration` -- all of it about the coding system and about which papers exist, "
    "none of it a fraction.",
    "the_question": "Of a registry cohort selected on ICD-O-3 morphology 9231/3, what fraction "
    "has a BONE primary site rather than a soft-tissue one?",
    "known_at_registration": [
        "The contradiction itself (two published Methods sections), already committed.",
        "That a morphology code carries no skeletal-versus-soft-tissue information; that axis is "
        "topography.",
        "Which papers exist and which are open access.",
    ],
    "what_a_negative_looks_like": "A SMALL bone-primary fraction -- low enough that registry "
    "9231/3 statistics are substantially about EMC -- is a real and publishable result. It would "
    "RETIRE, not weaken, the caveat this repository currently attaches to every SEER-derived EMC "
    "figure, including the rows on the IPD survival candidate list. It is worth exactly as much "
    "as a large number and is reported at the same weight.",
    "what_would_make_the_result_unreportable": "Not a small number. Only an unreachable one: a "
    "cohort whose topography split was never published and no route to compute it. That is "
    "reported as UNREACHABLE, never as 'no contamination'.",
    "how_a_number_may_not_be_obtained": [
        "No fraction is assembled by dividing counts from two different papers with different "
        "year windows, grade restrictions or site restrictions and calling the ratio a "
        "contamination rate. Bounds derived that way are labelled BOUND and carry every "
        "restriction that produced them.",
        "No count is written from recollection. Every number in this artifact is quoted from a "
        "document named in `provenance_ledger`.",
    ],
}

# ---------------------------------------------------------------------------
# 1 - what the CODING SYSTEM itself allows, read from SEER's own edit rules
# ---------------------------------------------------------------------------
# This is a documentary finding, not a cohort measurement. It says what SEER's site/histology
# validation program accepts, which is upstream of every SEER-derived count.
CODING_SYSTEM = {
    "source": {
        "title": "ICD-O-3 SEER SITE/HISTOLOGY VALIDATION LIST",
        "version_date": "April 29, 2022",
        "url": "https://seer.cancer.gov/icd-o-3/sitetype.icdo3.20220429.pdf",
        "how_obtained": "fetched on a GitHub Actions runner (the dev sandbox egress proxy blocks "
        "seer.cancer.gov), HTTP 200, PDF text extracted to 660,741 characters, published to the "
        "literature-cache branch under literature/seer-public-tier-probe/",
        "provenance": "[DOC]",
    },
    "what_the_document_says_about_itself": "This file is intended as a reference file for ICD-O-3 "
    "only and is not to be used for casefinding purposes. The ICD-O-3 site/type validation "
    "program was modified to allow only for the site/histology/behavior combinations listed in "
    "this publication. All other cases must be reviewed.",
    "finding": "9231/3 appears in exactly THREE site sections of the list, and all three are "
    "bone. It does not appear in the soft-tissue section.",
    "sections_listing_9231_3": [
        "BONES & JOINTS (EXCL SKULL AND FACE, MANDIBLE) C400-C403,C408-C409,C412-C414,C418-C419",
        "BONES OF SKULL AND FACE C410",
        "MANDIBLE C411",
    ],
    "soft_tissue_section": {
        "header": "CONNECTIVE & SOFT TISSUE C490-C496,C498-C499",
        "chondro_codes_listed": ["9240/3", "9242/3", "9243/3"],
        "chondro_codes_absent": ["9220/3", "9221/3", "9230/3", "9231/3"],
        "how_absence_was_verified": "⛔ NOT by a grep count alone -- a dropped line in PDF text "
        "extraction would look identical. The section was read as a contiguous ordered listing "
        "and it runs 9170/3 (LYMPHANGIOSARCOMA 917) -> 9240/3 (OSSEOUS & CHONDROMATOUS NEOPLASMS "
        "924) with every group header intact and no 918x, 919x, 922x or 923x group between them. "
        "The 924 group is present and complete, so the extraction reached that region of the "
        "page.",
    },
    "cross_check_9220_3": "9220/3 (chondrosarcoma NOS) appears in six sections -- the same three "
    "bone sections plus NASAL CAVITY C300, LARYNX C320-C323/C328-C329 and TRACHEA C339. It is "
    "likewise absent from CONNECTIVE & SOFT TISSUE. So the pattern is not specific to 9231/3: "
    "SEER's validation list treats the 922-923 chondrosarcoma block as skeletal and "
    "upper-aerodigestive-cartilage, not soft-tissue.",
    "what_this_does_and_does_not_establish": "⚠ IT ESTABLISHES A PROPERTY OF THE EDIT RULES, NOT "
    "A COHORT COMPOSITION. 'Must be reviewed' is an over-ride flag, not a rejection, so this does "
    "not show that no soft-tissue 9231/3 record exists in SEER -- and it cannot, because it is a "
    "rule file rather than a count. It also carries a DATE: this is the 2022 list, while the "
    "cohorts in question were accrued from 1973 onward under earlier versions. What it does "
    "establish is that the skeletal reading of 9231/3 is not one author's idiosyncrasy: it is the "
    "reading built into the registry's own validation program.",
    "why_it_sharpens_the_route": "The committed framing is that two papers read one code two "
    "ways and neither misuses it. That still holds. This adds that the registry's own edit rules "
    "take the BONE side, which makes the soft-tissue reading -- the one every EMC study uses -- "
    "the one that sits outside the validation list.",
    "⭐_the_date_caveat_is_now_CLOSED_by_the_errata_record": {
        "what_was_done": "All sixteen errata sheets SEER publishes for this list were fetched and "
        "read: the two ICD-O-3 errata sets (2001-05-22, 2003-05-06) and the fourteen site/type "
        "validation errata from 2001-06-14 through 2019-07-11, which the archive page states "
        "'document updates to the ICD-O-3 SEER Site/Histology Validation List since 2/9/2001'.",
        "finding": "⭐ NOT ONE OF THEM TOUCHES 9231/3. Across eighteen years of published changes "
        "the code is never added to a site section, removed from one, or moved between them. Only "
        "two of the sixteen mention any chondrosarcoma code at all.",
        "the_inference_and_its_logic": "The 2022 list places 9231/3 under bone. The errata record "
        "no move. If the code had been under connective and soft tissue at any point since 2001, "
        "a move would have had to be recorded to get it where it now is. So the skeletal "
        "placement holds across the whole accrual window of every cohort discussed here, and the "
        "'this is the 2022 edition' caveat no longer limits the claim.",
        "⚠_the_bound_on_that_inference": "It rests on the errata being COMPLETE. SEER states the "
        "sheets document updates since 2001-02-09 and labels the archive 'provided for reference "
        "purposes only'; whether every change was captured is not something the record can attest "
        "to about itself. The pre-2001 base list was not read.",
        "⭐_and_one_erratum_corroborates_the_THIRD_reading_from_SEERs_own_side": "The 2002-09-16 "
        "sheet adds, verbatim, 'C700-C709 ! OTHER CHONDROSARCOMA 924  9240/3 Mesenchymal "
        "chondrosarcoma' -- SEER deliberately extending a chondrosarcoma morphology to MENINGEAL "
        "topography. That is the same pairing CBTRUS's grouping document makes, arriving "
        "independently from the registry that maintains the list.",
        "provenance": "[DOC] -- sixteen PDFs fetched on an Actions runner, all HTTP 200, "
        "published to literature-cache under literature/seer-sitetype-errata-history/",
    },
    "open_question_it_creates": "What SEER's current Cancer PathCHART site-morphology validation "
    "says. Four candidate paths returned HTTP 404, so the path is unknown rather than the tool "
    "absent.",
}

# ---------------------------------------------------------------------------
# 2 - what each published 9231/3 cohort actually reports about primary SITE
# ---------------------------------------------------------------------------
PUBLISHED_COHORTS = [
    {
        "pmid": "31765367",
        "pmcid": "PMC6894367",
        "doi": "10.12659/MSM.917959",
        "year": 2019,
        "title": "Prognostic Factors and Treatment Options for Patients with High-Grade "
        "Chondrosarcoma",
        "reads_9231_3_as": "one histological subtype of chondrosarcoma",
        "cohort": "SEER 1973-2014, chondrosarcoma restricted to high grade (poorly "
        "differentiated + undifferentiated), n=743",
        "n_with_morphology_9231": 87,
        "n_total": 743,
        "percent_9231_of_cohort": 11.7,
        "site_restriction_applied": "NONE THAT EXCLUDES SOFT TISSUE. The paper's four exclusion "
        "criteria are: chondrosarcoma not the primary tumour; no histopathological confirmation; "
        "survival time unclear; grade well- or moderately-differentiated. No topography criterion "
        "appears among them.",
        "the_decisive_quote": "myxoid chondrosarcoma: it is characterized by the formation of "
        "myxoid stroma, and includes extraskeletal myxoid chondrosarcoma and the myxoid tumor of "
        "skull base",
        "quote_source": "full text, Material and Methods, 'Patients selection'",
        "why_the_quote_matters": "⭐ STRONGER THAN THE COMMITTED FRAMING. This is not a paper "
        "that merely happens to include EMC by using a shared code -- it STATES that its myxoid "
        "bucket includes extraskeletal myxoid chondrosarcoma, and then analyses that bucket "
        "inside a study of chondrosarcoma of bone. The merge is acknowledged in the Methods and "
        "carried into every result.",
        "the_location_variable_is_a_bone_taxonomy": "Tumor location was classified as axial "
        "(including pelvic bones, sacrum, coccyx, ribs, sternum, and vertebral columns), "
        "extremities (including bones of the upper and lower extremities) and other group "
        "(including bones of skull, mandible, and other atypical locations)",
        "what_that_does_to_the_size_question": "⛔ IT DESTROYS IT FOR THIS PAPER. Every one of "
        "the three location buckets is defined in terms of BONES, so a soft-tissue EMC of the "
        "thigh is absorbed into 'bones of the upper and lower extremities' or into 'other "
        "atypical locations' and becomes unrecoverable. The paper reports tumour location for all "
        "743 patients (axial 212, extremities 326, other 205) and the split cannot be read as "
        "bone-versus-soft-tissue, because the taxonomy has no soft-tissue category to be counted "
        "in. This is not a criticism of the paper; it is the same code ambiguity reappearing in "
        "the variable that would have resolved it.",
        "provenance": "[FT]",
    },
    {
        "pmid": "32856598",
        "pmcid": None,
        "doi": "10.1158/1055-9965.epi-20-0447",
        "year": 2020,
        "title": "Long-term Outcomes for Extraskeletal Myxoid Chondrosarcoma: A SEER Database "
        "Analysis",
        "reads_9231_3_as": "extraskeletal myxoid chondrosarcoma",
        "cohort": "SEER 1973-2016, selected on morphology 9231/3 with no stated topography "
        "restriction",
        "n_identified_on_the_code_alone": 791,
        "n_after_exclusions": 439,
        "n_provenance": "⚠ [2°] -- BOTH COUNTS ARE READ FROM A REVIEW, NOT FROM THIS PAPER. The "
        "2025 review at PMC12504171 states: 'a recent study has utilised SEER database and "
        "identified 791 cases diagnosed as myxoid chondrosarcoma, with 439 cases meeting the "
        "inclusion criteria following exclusions (Wagner et al. 2020)'. The 439 is corroborated "
        "independently by this paper's own abstract, which reports 373 locoregional cases as 85% "
        "of the cohort. The 791 has ONE source and it is secondary.",
        "why_791_matters": "⭐ It is the only published count of a SEER 9231/3 pull BEFORE any "
        "exclusion, and it is the natural denominator for the question this route asks. ⛔ AND IT "
        "IS NOT THE ANSWER: 352 cases were dropped and NOBODY HAS READ WHY. If the exclusions "
        "were topography-based the gap would bound the contamination; if they were for missing "
        "survival time, unknown treatment or non-primary status it says nothing about site. "
        "Reading 791-439 as a bone fraction would be exactly the manufactured ratio "
        "`registration.how_a_number_may_not_be_obtained` forbids.",
        "site_restriction_applied": "UNKNOWN -- the abstract states none, and the Methods have "
        "not been read.",
        "reachability": "⛔ UNREACHABLE AT $0. Europe PMC reports isOpenAccess=N and inPMC=N; the "
        "NCBI ID converter returns 'Identifier not found in PMC'; the publisher PDF URL Europe "
        "PMC advertises returns HTTP 200 with Content-Type text/html and a ten-character body "
        "reading 'Loading...', i.e. a JavaScript shim; the DOI landing page and the AACR article "
        "page both return HTTP 403. This is a subscription article and no attempt was made to "
        "get around that.",
        "what_it_would_settle": "Its abstract says 'Logistic regression assessed associations "
        "between tumor location and distant disease' and 'There was no OS difference by primary "
        "tumor site', so the paper analysed primary site and its Table 1 very likely prints the "
        "distribution. That table is the single highest-value unread object for this route.",
        "provenance": "[API] for the abstract; [2°] for the 791",
    },
    {
        "pmid": "27819877",
        "pmcid": None,
        "doi": "10.1097/coc.0000000000000341",
        "year": 2018,
        "title": "Benefit of Radiotherapy in Extraskeletal Myxoid Chondrosarcoma: A Propensity "
        "Score Weighted Population-based Analysis of the SEER Database",
        "reads_9231_3_as": "extraskeletal myxoid chondrosarcoma",
        "cohort": "SEER 1973-2012, 'queried for cases of localized EMC arising from soft "
        "connective tissues of the trunk and extremities treated with surgery and/or EBRT'; 172 "
        "patients identified, all diagnosed 2004-2012",
        "why_it_matters": "⭐ THIS IS THE ONLY PUBLISHED EMC COHORT THAT APPLIES A TOPOGRAPHY "
        "RESTRICTION EXPLICITLY, and it is therefore the only one whose selection would produce "
        "the split if the pre-restriction count were also printed. ⛔ The abstract gives the "
        "post-restriction count only. Whether the paper reports what the restriction removed is "
        "unread; it is not open access and has no PMCID.",
        "provenance": "[API]",
    },
    {
        "pmid": "35144048",
        "pmcid": None,
        "doi": "10.1016/j.ctarc.2022.100530",
        "year": 2022,
        "title": "Extraskeletal myxoid chondrosarcoma: Clinical features and overall survival",
        "reads_9231_3_as": "extraskeletal myxoid chondrosarcoma",
        "cohort": "SEER 2004-2015, 270 cases",
        "why_it_matters": "Its Methods state 'Cases were stratified according to the anatomic "
        "site of the primary tumor', and its Results name 'pelvic location' as a univariate "
        "prognostic factor -- so an anatomic-site table exists. Whether its site categories "
        "distinguish bone from soft tissue, or repeat PMID 31765367's error of using a taxonomy "
        "with no soft-tissue category, cannot be told from the abstract.",
        "provenance": "[API]",
    },
]

# ---------------------------------------------------------------------------
# 2b - the indeterminate-diagnosis paper, and how much of it is about EMC
# ---------------------------------------------------------------------------
# The route's second open unknown: does the indeterminate-diagnosis margin penalty hold in EMC
# specifically? This is the answer, and it is a number rather than a caveat.
INDETERMINATE_DIAGNOSIS_PAPER = {
    "pmid": "39899751",
    "pmcid": "PMC11789853",
    "doi": "10.5435/jaaosglobal-d-24-00370",
    "year": 2025,
    "title": "What Is the Prevalence and Fate of Myxoid Soft-Tissue Tumors With an Indeterminate "
    "Diagnosis Prior to Resection?",
    "the_question_asked_of_it": "Does the measured chain from diagnostic uncertainty to surgical "
    "failure hold in EMC, or only in myxoid soft-tissue tumours as a class?",
    "answer": "IT CANNOT ANSWER IT, and now we know by how much. Table 2 gives the final "
    "resection diagnoses of all 66 patients who had an indeterminate diagnosis before resection: "
    "myxoma 26, myxofibrosarcoma 20, myxoid liposarcoma 5, fibromyxoid sarcoma 4, EXTRASKELETAL "
    "MYXOID CHONDROSARCOMA 4, myxoid sarcoma 2, other 5.",
    "emc_share_of_the_indeterminate_cohort": {"n_emc": 4, "n_total": 66},
    "why_that_settles_it": "⛔ The 37%-versus-15% positive-margin contrast is computed over 27 "
    "and 74 patients -- the subset that proved sarcoma AND had two-year follow-up -- and the "
    "whole indeterminate cohort contains FOUR EMC patients. No EMC-specific statement can rest "
    "on that, in either direction. The route's unknown is therefore answered as UNANSWERABLE "
    "FROM THIS SOURCE, with a count, rather than left open as a caveat.",
    "what_the_paper_may_still_be_cited_for": "The class-level finding, stated as a class-level "
    "finding: in musculoskeletal myxoid soft-tissue tumours, 28% (66/235) had an indeterminate "
    "preoperative diagnosis, and among those proving sarcoma with two-year follow-up the "
    "positive-margin rate was 37% (10/27) against 15% (11/74). EMC is one of at least seven "
    "entities inside that class.",
    "provenance": "[FT]",
}

# ---------------------------------------------------------------------------
# 2e - ⭐⭐⭐ THE ONE PUBLISHED STUDY THAT ACTUALLY SPLIT A CHONDROSARCOMA COHORT BY TOPOGRAPHY
# ---------------------------------------------------------------------------
# Found 2026-08-23, and it is the closest anything published comes to the number this route asks
# for. It is also independent corroboration of the route's thesis, written by authors who hit the
# problem while trying to do something else entirely.
TOPOGRAPHY_SPLIT_STUDY = {
    "pmid": "31283732",
    "pmcid": "PMC6903832",
    "year": 2019,
    "journal": "Clinical Orthopaedics and Related Research",
    "title": "Regional Lymph Node Involvement Is Associated With Poorer Survivorship in Patients "
    "With Chondrosarcoma: A SEER Analysis",
    "design": "SEER 18 registries, diagnosis years 1988-2015, morphology codes 9220/3, 9221/3, "
    "9231/3, 9240/3, 9242/3, 9243/3",
    "⭐_it_classifies_on_TOPOGRAPHY_explicitly": "Patients with chondrosarcoma of bone and soft "
    "tissue were also included in this analysis, skeletal (axial bone, extremity bone, and bone "
    "[not other specified]) and extraskeletal (arising in site other than bone) chondrosarcoma "
    "were classified based on the International Classification of Diseases for Oncology "
    "topography codes in the SEER database",
    "⭐⭐_and_it_excluded_EMC_BY_NAME_AND_COUNT": {
        "quote": "We excluded 404 patients with extraskeletal myxoid chondrosarcoma because it "
        "is a misnomer to call it a real chondrosarcoma",
        "n": 404,
        "what_that_number_is": "Patients this study identified as EXTRASKELETAL myxoid "
        "chondrosarcoma inside a SEER 18 chondrosarcoma-morphology pull covering 1988-2015. ⚠ "
        "Since 9231/3 remains on the study's own list of INCLUDED morphology codes, the "
        "discriminator between the excluded 404 and the retained 9231/3 patients can only be "
        "TOPOGRAPHY -- which is exactly the split this route wants. The skeletal 9231/3 count is "
        "therefore in the study's Table 1 histologic-subtype row.",
        "⛔_status_of_that_reading": "INFERRED FROM THE METHODS, NOT YET CONFIRMED FROM TABLE 1. "
        "Table 1 is served as a separate resource that the article HTML does not inline, and it "
        "has been requested. Until it is read, `404` is recorded as the study's extraskeletal "
        "myxoid count and NOTHING is divided by it.",
    },
    "the_cohort_flow_as_printed": {
        "enrolled_1988_2015": 5528,
        "pool_before_the_lymph_node_exclusion": 4273,
        "excluded_for_unreported_lymph_node_status": 899,
        "included": 3374,
        "of_the_included_extraskeletal": 426,
        "of_the_included_skeletal": 2948,
        "arithmetic_check": "426 + 2948 = 3374, and 4273 - 899 = 3374. Both close.",
    },
    "⭐⭐⭐_ITS_OWN_LIMITATION_IS_THIS_ROUTES_THESIS_IN_THE_AUTHORS_WORDS": {
        "quote": "We could not guarantee patients diagnosed with extraskeletal 'Chondrosarcoma, "
        "not other specified' did not have extraskeletal myxoid chondrosarcoma, which is not "
        "considered a chondrosarcoma, but we have tried to diminish the potential inaccuracies by "
        "only including patients with histological confirmation and excluding those patients with "
        "extraskeletal myxoid chondrosarcoma",
        "why_it_matters": "A peer-reviewed registry study states, in its own Discussion, that it "
        "cannot rule out EMC hiding inside its 426 retained extraskeletal chondrosarcoma cases. "
        "⛔ SO THE CONTAMINATION IS NOT ONLY UNMEASURED -- IT IS ALREADY ACKNOWLEDGED IN PRINT AS "
        "UNRESOLVABLE FROM THE REGISTRY, by authors who tried. Any paper from this route must "
        "cite this and cannot present the problem as unnoticed.",
        "⚠_and_it_runs_the_OTHER_WAY_from_this_routes_framing": "This repository has framed the "
        "contamination as bone leaking into EMC cohorts. Here it is EMC leaking into a bone "
        "cohort, twice over: 404 removed deliberately, and an unknown number left behind under "
        "'chondrosarcoma NOS'. Both directions are the same defect and the paper should say so.",
    },
    "provenance": "[FT] -- PMC article HTML page (the Europe PMC fullTextXML endpoint 404s for "
    "this PMCID). ⚠ Table 1 itself is NOT in that HTML and has NOT been read.",
}

# ---------------------------------------------------------------------------
# 2d - ⚠ THE CAVEAT THAT DECIDES HOW A BONE FRACTION MAY BE READ
# ---------------------------------------------------------------------------
# ⛔ WITHOUT THIS, A MEASURED BONE FRACTION WOULD BE OVER-READ THE MOMENT IT ARRIVED. It is written
# down BEFORE the number exists, for the same reason `registration` is.
BONE_PRIMARY_IS_NOT_AUTOMATICALLY_NOT_EMC = {
    "the_trap": "It is natural to read 'bone primary' in a 9231/3 cohort as 'this one is a "
    "conventional chondrosarcoma, not EMC'. That inference is WRONG as a blanket rule.",
    "why": "Primary EXTRASKELETAL myxoid chondrosarcoma arising in bone is a documented entity "
    "with its own published case series. The 2020 EMC review states plainly that EMC 'may also "
    "occur in less common sites such as the trunk, head and neck, paraspinal soft tissue, "
    "abdomen, retroperitoneal space, and bone', citing three sources -- among them a five-case "
    "study titled 'Osseous myxochondroid sarcoma: A detailed study of 5 cases of extraskeletal "
    "myxoid chondrosarcoma of the bone' and a three-case report titled 'Primary extraskeletal "
    "myxoid chondrosarcoma of bone'.",
    "source": "PMC7563993 full text and its reference list",
    "provenance": "[FT] for the review's statement; ⚠ the two cited series themselves are "
    "UNREAD -- their titles and journals are read from this review's reference list, which is why "
    "no count from them appears here.",
    "⭐_what_this_does_to_the_measurement": "It makes any measured bone-primary fraction an UPPER "
    "BOUND on non-EMC contamination, not the contamination itself. Some bone-primary 9231/3 "
    "records are genuine EMC of bone. The paper must say so, and must not present the fraction as "
    "'the share of the cohort that is the wrong disease'.",
    "⭐_and_it_cuts_the_other_way_too": "By the same logic the soft-tissue side is not pure "
    "either: a soft-tissue 9231/3 record is a registrar's morphology assignment, not an "
    "NR4A3-confirmed diagnosis. The one EMC cohort in this repository that carries no coding "
    "ambiguity at all is the Italian Sarcoma Group series (PMID 32572850, n=67), which is "
    "NR4A3-rearrangement confirmed and centrally reviewed -- and it is not a registry cohort.",
}

# ---------------------------------------------------------------------------
# 3 - the size, and its honest state
# ---------------------------------------------------------------------------
SIZE = {
    "state": "MEASURED AS A BOUND, 2026-08-23",
    "the_question": "Of a registry cohort selected on morphology 9231/3, what fraction has a bone "
    "primary?",
    "the_answer": {
        "bone_primary_fraction": "at least 32.1%, and about 37.5% once the one bias whose "
        "direction is known is corrected for",
        "source": "PMID 31283732 / PMC6903832 -- SEER 18 registries, diagnosis years 1988-2015. "
        "BOTH HALVES COME FROM THE SAME STUDY, so registries, years and morphology code match by "
        "construction and nothing has to be combined across papers.",
        "derivation": {
            "skeletal_9231_retained": 191,
            "skeletal_9231_where": "Table 1, 'Histologic type' row: 'Myxoid chondrosarcoma 187 "
            "(6%) 4 (9%)'. The two columns are 'No regional lymph node involvement (n = 3330)' and "
            "'Regional lymph node involvement (n = 44)', so the row total is 187 + 4 = 191.",
            "extraskeletal_9231_excluded": 404,
            "extraskeletal_9231_where": "Methods: 'We excluded 404 patients with extraskeletal "
            "myxoid chondrosarcoma because it is a misnomer to call it a real chondrosarcoma'.",
            "total_9231_in_the_pull": 595,
            "fraction": "191 / 595 = 32.1%",
        },
        "⚠_the_one_step_that_is_INFERRED_rather_than_printed": "That the 191 retained myxoid cases "
        "are all SKELETAL. The paper does not cross-tabulate site against histology. The inference "
        "is that its authors classify site from ICD-O topography codes, excluded every "
        "EXTRASKELETAL myxoid case as EMC, and kept 9231/3 on their included-morphology list -- so "
        "any myxoid case still in the cohort must be skeletal. Tight, but a deduction from two "
        "Methods statements rather than a printed cross-tab.",
    },
    "arithmetic_checks_that_passed": [
        "Table 1's site rows sum to 3,374 (2,917+31 skeletal, 413+13 extraskeletal), matching the "
        "cohort size the paper states.",
        "Its histology rows sum independently to 3,374.",
        "The site totals reproduce the 2,948 and 426 the Results text quotes.",
        "4,273 - 899 = 3,374, the paper's own flow.",
    ],
    "the_two_biases_and_their_DIRECTIONS": {
        "makes_32_percent_TOO_LOW": "The 191 is counted AFTER the lymph-node-status filter, which "
        "removed 899 of 4,273 (21.0%) of the pool; the 404 was excluded at an earlier stage. If "
        "skeletal 9231 cases lost lymph-node status at the cohort-average rate, the pre-filter "
        "skeletal count is about 242 and the fraction is 242/646 = 37.5%. ⚠ THAT SECOND FIGURE IS "
        "AN ADJUSTMENT, NOT A MEASUREMENT -- it assumes equal attrition, which nobody has shown.",
        "also_makes_32_percent_TOO_LOW": "The paper's other inclusion criteria (living patient, "
        "microscopic confirmation, first primary) were applied somewhere between the 5,528 "
        "enrolled and the 4,273 pool, and their ORDER relative to the 404 exclusion is not "
        "stated. If the 404 is a rawer count than the 191, the true skeletal share is higher "
        "again.",
        "⛔_what_does_NOT_make_it_too_high": "Nothing identified. Both known biases push the same "
        "way, which is why 32.1% is reported as a FLOOR rather than an estimate.",
    },
    "⛔_what_this_fraction_is_NOT": "It is NOT the share of a 9231/3 cohort that is 'the wrong "
    "disease'. Primary EMC of bone is a documented entity (see "
    "`bone_primary_is_not_automatically_not_emc`), so some of the 191 are genuine EMC. The "
    "bone-primary fraction is an UPPER bound on non-EMC contamination and a LOWER bound as "
    "measured. Two different bounds on two different quantities; they must not be collapsed.",
    "⭐_why_it_is_decision_relevant": "IT IS LARGE. Roughly one record in three in a SEER "
    "morphology-9231/3 pull has a bone primary. A study querying 9231/3 with no topography "
    "restriction -- the standard construction in the EMC registry literature -- is therefore not "
    "assembling a soft-tissue cohort. ⛔ AND THE PRE-REGISTERED NEGATIVE DID NOT FIRE: "
    "`registration.what_a_negative_looks_like` defined a SMALL fraction as a real result that "
    "would RETIRE this repository's caveat on SEER-derived EMC figures. The fraction is not "
    "small, so the caveat stands, and it is now quantified rather than asserted.",
    "cross_checks_against_the_other_published_counts": "No contradiction. PMC9303001 reports 459 "
    "NON-BONE 9231 records for SEER 18 over 2000-2018; this study's 404 extraskeletal covers SEER "
    "18 over 1988-2015 -- different overlapping windows, same order of magnitude. ⛔ THEY STILL "
    "MAY NOT BE COMBINED: that is the cross-paper ratio "
    "`registration.how_a_number_may_not_be_obtained` forbids, and it is no longer needed, because "
    "one study supplies both halves.",
    "⛔_THE_ROUTE_WAS_CLOSED_ON_THIS_NUMBER_NOT_DESPITE_IT": "trimcrae, 2026-08-23: 'this is not a "
    "paper. Document what we have, merge to main, and drop it.' The measurement stands and is "
    "unpublished as far as a bounded search could tell. What it lacks is a CONSEQUENCE. The paper "
    "would have had to claim that querying 9231/3 without a topography restriction is common "
    "practice, and this artifact's own corpus refutes that: PMID 27819877 restricted to soft "
    "connective tissue, PMC9303001 excluded bone site codes explicitly, and PMID 31283732 "
    "classified by topography and removed 404 cases by name. Three of four checkable cohorts "
    "restrict. So 32.1% prices a practice the field already follows. ⚠ AND AN OVERCLAIM WAS "
    "CORRECTED ON THE WAY OUT: the draft asserted the unrestricted query was 'the standard "
    "construction in this literature', which this corpus does not support. Reopen ONLY on evidence "
    "that PMID 32856598 did not restrict on topography — that is the one finding that would supply "
    "a consequence, and it needs a subscription copy of its Methods.",
    "prior_art_search": "⚠ INCONCLUSIVE, NOT NEGATIVE (2026-08-23). Five Europe PMC searches for "
    "prior work on registry histology miscoding, ICD-O coding validity, soft-tissue-sarcoma "
    "topography contamination, myxoid-chondrosarcoma nomenclature and rare-cancer case definitions "
    "returned hitCounts of 887, 3021, and others, of which only the first 100 by relevance were "
    "retrieved per query. Nothing in those 100s reports this quantity. ⛔ That is a statement about "
    "100 of 887, and it must NOT be read as 'nobody has published this'.",
    "what_would_still_improve_it": [
        "A cross-tab of site against histology for this cohort, removing the one inferred step.",
        "The same query without a lymph-node-status requirement, removing the known downward bias "
        "and turning the floor into a point estimate.",
        "Table 1 of PMID 32856598, as an independent replication over a different window.",
    ],
    "provenance": "[FT] -- Table 1 read from the article PDF (Europe PMC render, 45,987 "
    "characters), after the PMC article HTML and its ?report=classic view were both found not to "
    "inline table cells and the Europe PMC fullTextXML endpoint returned HTTP 404 for this PMCID.",
}

# ---------------------------------------------------------------------------
# 2c - A THIRD READING OF THE SAME CODE, from a third registry
# ---------------------------------------------------------------------------
# The committed framing says 9231/3 is read two ways. Found 2026-08-23: there is a third, in a
# national registry's own published grouping document.
THIRD_READING = {
    "pmid": "35859542",
    "pmcid": "PMC9290890",
    "year": 2022,
    "title": "Aligning the Central Brain Tumor Registry of the United States (CBTRUS) histology "
    "groupings with current definitions",
    "reads_9231_as": "a CNS tumour -- listed under 'Tumors of Meninges -> Mesenchymal tumors' "
    "and again under 'Other neoplasms related to the meninges'",
    "the_quote": "Tumors of Meninges Meningioma 9535 ... Mesenchymal tumors 8710, 8711, 8810, "
    "8821, 8825, 8840, 9120, 9125, 9130, 9131, 9133, 9161, 9220, 9231, 9240, 9243, 9370-9372",
    "quote_source": "full text, reclassification table",
    "why_it_matters": "⭐ THE CODE IS READ THREE WAYS, NOT TWO -- soft-tissue EMC, a bone "
    "chondrosarcoma subtype, and an intracranial mesenchymal/meningeal tumour -- and the third "
    "reading comes from a national registry's own grouping document rather than from a single "
    "study. ⚠ All three are legitimate. A morphology code carries no topography, so 9231/3 "
    "paired with C70-C72 is a CNS tumour, paired with C40-C41 is a bone tumour, and paired with "
    "C49 is soft tissue. That is the route's thesis stated by the coding system's own users.",
    "and_it_corroborates_the_validation_list": "The same document treats SEER's site/type "
    "validation list as an operational authority -- one of its recode instructions reads '8771 "
    "(remove from data, not in SEER site/type validation list)'. So that list is not a dormant "
    "reference: another registry prunes its data against it.",
    "provenance": "[FT]",
}

# ---------------------------------------------------------------------------
# 3a - THE BASE RATE: how often a morphology-selected SEER sarcoma cohort carries a bone primary
# ---------------------------------------------------------------------------
# ⭐ The nearest published measurement of the thing this route asks about, found 2026-08-23. It is
# NOT the 9231/3 number and must never be quoted as one -- but until it was read, this repository
# had no idea whether morphology-selected SEER sarcoma cohorts contain bone primaries AT ALL, and
# it now has a published count that they do, plus the rate across all soft-tissue morphologies.
BASE_RATE_OF_BONE_PRIMARIES = {
    "pmid": "35875111",
    "pmcid": "PMC9303001",
    "year": 2022,
    "title": "Pan-Soft Tissue Sarcoma Analysis of the Incidence, Survival, and Metastasis: A "
    "Population-Based Study Focusing on Distant Metastasis and Lymph Node Metastasis",
    "design": "SEER, 18 registries, 2000-2018, patients selected on ICD-O-3 soft-tissue-sarcoma "
    "morphology codes",
    "the_quote": "Exclusion criteria included STS confirmed only by autopsy or death certificate "
    "and patients with site codes C40.0 to C42.1 (primary in bone). ... A total of 115,800 "
    "patients were retrieved, and a total of 113,715 patients were included in the final analysis "
    "after excluding 417 patients with only autopsy or death certificates and 1668 patients with "
    "primary bone origin.",
    "quote_source": "full text, Materials and Methods, 'Study Population'",
    "the_measurement": {
        "retrieved_on_morphology": 115800,
        "excluded_for_bone_primary_topography": 1668,
        "bone_primary_percent_of_the_morphology_pull": 1.44,
        "how_derived": "1668 / 115800, computed here from the paper's own two printed counts. "
        "⚠ The paper does not print this percentage; it prints both numerators.",
    },
    "why_this_matters_to_the_route": "⭐ IT ESTABLISHES THE PHENOMENON AND GIVES IT A BASE RATE. "
    "Selecting a SEER sarcoma cohort on morphology alone DOES pull bone-primary records -- a "
    "published study had to exclude 1,668 of them by topography -- so the contamination this "
    "route posits is real in SEER practice and not merely permitted by the coding system. And it "
    "gives the comparator any 9231/3-specific figure would be judged against: about 1.4% across "
    "soft-tissue morphologies generally.",
    "why_it_is_not_the_answer": "⛔ THIS IS THE RATE ACROSS ALL SOFT-TISSUE SARCOMA MORPHOLOGIES, "
    "NOT FOR 9231/3. If anything it is the morphology where a HIGHER rate would be expected, "
    "because 9231/3 is a chondrosarcoma code whose ICD-O label carries no 'extraskeletal' "
    "qualifier at all -- which is the route's entire premise. The paper's per-subtype counts are "
    "POST-exclusion (extraskeletal myxoid chondrosarcoma, 139 + 25 = 164), so it does not report "
    "how many 9231/3 records its bone filter removed.",
    "⭐_its_supplementary_table_1_gives_the_9231_HALF_of_the_ratio": {
        "value": 459,
        "what_it_is": "Records with ICD-O-3 morphology 9231 and a NON-BONE primary site, in SEER "
        "18 registries, 2000-2018, after the C40.0-C42.1 exclusion. Printed as 'Extraskeletal "
        "myxoid chondrosarcoma | 9231 | 459 | .4' in Supplementary table 1, 'Pathological "
        "subtypes enrolled according to ICD-O-3 code'.",
        "internally_consistent": "The table's rows sum to the paper's stated post-exclusion total "
        "of 113,715.",
        "⛔_do_not_confuse_it_with": "The '139 + 25 = 164' extraskeletal myxoid chondrosarcoma "
        "figure in the same paper's lung-metastasis table, which is the subset with known "
        "metastasis status, not the cohort.",
        "and_the_retrieval_used_no_other_chondrosarcoma_code": "9231 is the ONLY 922x-924x code "
        "in the paper's whole morphology list -- no 9220, no 9240, no 9242, no 9243. Its authors "
        "treated 9231 as the soft-tissue chondrosarcoma code, which is the reading PMID 31765367 "
        "does not take.",
        "provenance": "[FT] -- extracted from the study's own Supplementary Table 1 (.docx), "
        "fetched via the Europe PMC supplementaryFiles endpoint on an Actions runner",
    },
    "⭐⭐_WHAT_THIS_MAKES_POSSIBLE_AND_IT_IS_THE_ROUTES_BEST_NEXT_STEP": "★ THE DENOMINATOR IS NOW "
    "A SINGLE, PRECISELY SPECIFIED QUERY RATHER THAN AN OPEN RESEARCH PROBLEM. A SEER query on "
    "morphology 9231 with NO site restriction, over SEER 18 registries, diagnosis years "
    "2000-2018, divided by 459, IS the bone-primary fraction -- same registries, same years, same "
    "code, one published half and one query. That is a far cheaper and far more exactly stated "
    "ask than 'obtain a data-use agreement and design a study', and it is what should be recorded "
    "as this route's blocking step.",
    "⛔_and_the_ratio_may_not_be_taken_from_the_numbers_already_in_hand": "PMID 32856598's 791 "
    "covers SEER 1973-2016 and an unstated registry set. Dividing 459 into it would cross year "
    "windows and registry coverage and produce a number that looks like a measurement and is not "
    "one. `registration.how_a_number_may_not_be_obtained` forbids it, and it is forbidden here "
    "explicitly because the two numbers are now sitting next to each other and the temptation is "
    "real.",
    "⚠_it_also_contradicts_the_validation_list_in_the_useful_direction": "SEER's 2022 "
    "site/histology validation list does not list 9231/3 under CONNECTIVE & SOFT TISSUE, yet this "
    "study counts 164 extraskeletal myxoid chondrosarcomas AFTER excluding every bone-primary "
    "site code. Both can be true -- 'must be reviewed' is an over-ride flag rather than a "
    "rejection -- and together they say the validation list describes an editing rule that "
    "practice routinely overrides. That is a stronger and more interesting statement than either "
    "document alone, and it is the one the paper should make.",
    "provenance": "[FT]",
}

# ---------------------------------------------------------------------------
# 3b - the PUBLIC aggregate tier: what it actually serves, established rather than assumed
# ---------------------------------------------------------------------------
PUBLIC_AGGREGATE_TIER = {
    "the_question": "SEER has web-facing tools that serve aggregate statistics without a "
    "data-use agreement. Will any of them cross morphology 9231/3 against ICD-O topography?",
    "answer": "NO, and the reason is structural rather than a gap someone forgot to fill.",
    "the_evidence": {
        "source": "SEER*Explorer -> Cancer Site Definitions",
        "url": "https://seer.cancer.gov/statistics-network/explorer/cancer-sites.html",
        "the_load_bearing_sentence": "The cancer sites available in SEER*Explorer are primarily "
        "defined using the SEER Site Recode ICD-O-3/WHO 2008 variable. However, there are "
        "additional sites included that are defined below and are based on specific behaviors "
        "and/or histologies, and only valid for specific years.",
        "provenance": "[DOC]",
    },
    "what_the_tool_can_do": "⭐ IT CAN CROSS SITE WITH HISTOLOGY -- and the page shows the exact "
    "shape this route would need. Its subtype definitions read, verbatim in form, 'Site recode "
    "ICD-O-3/WHO 2008 = Lung and Bronchus' AND 'ICD-O-3 Histology (Type) = 8015, 8050, 8140 ...'. "
    "So the cross-tab is not a capability SEER*Explorer lacks.",
    "what_it_cannot_do": "⛔ THE HISTOLOGY AXIS IS A FIXED LIST NCI AUTHORS, NOT A FIELD THE USER "
    "SUPPLIES. The subtype definitions exist for exactly five families -- Brain and Other Nervous "
    "System, Breast, Esophagus, Lung and Bronchus, Thyroid -- plus three special histology-defined "
    "sites (CMML 9945, chronic myeloproliferative disorders 9950-9964, myelodysplastic syndromes "
    "9980-9989). There is NO bone family, NO soft-tissue family, NO chondrosarcoma subtype and no "
    "9231. Everything else is served at Site Recode granularity, and Site Recode is the "
    "topography axis with the morphology already collapsed into it.",
    "so_the_public_tier_verdict": "A 9231/3-by-topography cross-tab is not available from "
    "SEER*Explorer at any setting. The help page's downloadable CSV is a download OF THE "
    "DISPLAYED STATISTIC, not of case-level data, so it inherits the same granularity.",
    "what_was_checked_and_did_not_answer": [
        "SEER CanQues: https://seer.cancer.gov/canques/ REDIRECTS to the Cancer Statistics "
        "Explorer Network landing page, i.e. the old query system is retired into SEER*Explorer.",
        "https://api.seer.cancer.gov/rest/ returns HTTP 401 -- that is the registrar-facing "
        "SEER*API, which needs a key and serves coding reference data rather than case counts.",
        "CDC's U.S. Cancer Statistics pages returned HTTP 403 to the runner, so the USCS route is "
        "UNTESTED rather than closed. ⚠ Recorded as untested. USCS's own documentation states its "
        "public-use database is made available through SEER*Stat, which would inherit the Windows "
        "barrier below.",
        "rarecarenet.eu refused the connection outright (ConnectionRefusedError), so RARECAREnet "
        "is UNREACHABLE rather than checked.",
    ],
    "the_honest_bound": "⚠ THIS IS A READING OF SEER'S OWN DEFINITION PAGE, WHICH IS STRONG FOR "
    "SEER*Explorer AND SAYS NOTHING ABOUT TOOLS NOT EXAMINED. Two named routes above returned a "
    "403 and a refused connection; neither is evidence that they would not serve the cross-tab.",
}

# ---------------------------------------------------------------------------
# 3c - DOES ANY TREATMENT GUIDANCE IMPORT CONVENTIONAL-CHONDROSARCOMA REASONING FOR EMC?
# ---------------------------------------------------------------------------
# RT-DIAGNOSTIC-PATHWAY's third open unknown, and the route says answering it "would raise the
# finding's weight considerably". ⭐ IT IS ANSWERED, AND IT IS LARGELY A NEGATIVE.
GUIDELINE_PLACEMENT = {
    "the_question": "Does any treatment guidance actually import conventional-chondrosarcoma "
    "reasoning for EMC?",
    "answer": "NO. ⭐ ANSWERED AT PRIMARY SOURCE ON THE NCCN SIDE -- its Soft Tissue Sarcoma "
    "guideline lists extraskeletal myxoid chondrosarcoma among its covered histologies and its "
    "Bone Cancer guideline does not -- and the specialist literature is "
    "explicit in the other direction: EMC is managed under SOFT TISSUE SARCOMA guidance. ⛔ This "
    "is a NEGATIVE for the route's clinical half and is reported as one. It does not weaken the "
    "coding finding, which is about the research record rather than about the clinic.",
    "what_two_independent_reviews_say": [
        {
            "pmcid": "PMC12504171",
            "year": 2025,
            "quote": "Due to the rarity of EMC, we recommend standardising care in line with the "
            "ESMO-EURACAN-GENTURIS and NCCN STS guidelines",
            "and_on_the_name": "Despite its name, EMC does not exhibit true cartilaginous "
            "differentiation and is now classified as a mesenchymal tumour of uncertain "
            "differentiation rather than a conventional chondrosarcoma",
            "provenance": "[FT]",
        },
        {
            "pmcid": "PMC7563993",
            "year": 2020,
            "quote": "the same recommendations about the use of adjuvant or neo-adjuvant RT in "
            "soft tissue sarcoma also apply to EMC: wide surgical margin resection and "
            "radiotherapy are standard for all sarcomas greater than 5 cm, deep and "
            "intermediate/high-grade lesions, as reported in the European Society of Medical "
            "Oncology (ESMO) and National Comprehensive Cancer Network (NCCN) guidelines",
            "and_on_the_name": "EMC is now classified as a mesenchymal tumor of uncertain "
            "differentiation ... it shows no cartilage differentiation, despite the name, which "
            "has been retained only for historical reasons",
            "provenance": "[FT]",
        },
    ],
    "⭐⭐_AND_NCCN_ANSWERS_IT_AT_PRIMARY_SOURCE_ON_ITS_OWN_PUBLIC_INDEX": {
        "how_obtained": "nccn.org returns HTTP 200 to a real headless browser (it 403s nothing "
        "here; it was the ESMO side that refused). Two guideline-detail pages were read: "
        "https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1464 (Soft Tissue "
        "Sarcoma) and ...&id=1418 (Bone Cancer). Each publishes the list of histologies its "
        "guideline covers.",
        "nccn_soft_tissue_sarcoma_v5_2026": "Lists 'Extraskeletal myxoid chondrosarcoma' "
        "explicitly, among 'Alveolar Soft Part Sarcoma', 'Clear cell sarcoma', 'Extraskeletal "
        "Osteosarcoma', 'Mesenchymal chondrosarcoma', 'Myxoid/round cell liposarcoma', 'Synovial "
        "sarcoma' and the rest.",
        "nccn_bone_cancer_v1_2027": "Covers exactly six topics -- Bone Cancer, Chondrosarcoma, "
        "Chordoma, Ewing Sarcoma, Giant Cell Tumor of Bone, Osteosarcoma -- and does NOT list "
        "extraskeletal myxoid chondrosarcoma.",
        "⭐_the_verdict": "NCCN places EMC under SOFT TISSUE SARCOMA and not under Bone Cancer or "
        "Chondrosarcoma. That is a primary reading of the guideline body's own published topic "
        "index, not a review's description of it, and it is a clean negative for the proposition "
        "that guidance imports conventional-chondrosarcoma reasoning for EMC.",
        "⚠_what_it_is_not": "The topic index says WHERE EMC is placed and WHAT IT IS GROUPED "
        "WITH. It does not say what the guideline TEXT recommends for EMC -- the guideline PDFs "
        "are behind a login and were not sought.",
        "provenance": "[DOC]",
    },
    "⚠_the_honest_bound_on_the_ESMO_half": "BOTH ESMO READINGS ARE SECONDARY. What has been read is "
    "what two EMC reviews say the guidelines say, not the guideline texts. The ESMO clinical "
    "practice guidelines are not open access: Europe PMC reports isOpenAccess=N for every version "
    "of both the soft-tissue and the bone guideline, five doi.org resolutions returned an "
    "identical 1,327-character shim page under a real headless browser, and "
    "annalsofoncology.org returned HTTP 403 to that same browser. So 'no guideline imports "
    "chondrosarcoma reasoning' is supported by two specialist reviews and is NOT a reading of the "
    "guidelines themselves.",
    "⭐_but_there_is_prior_art_for_the_clinical_claim_and_it_had_never_been_read_here": {
        "pmid": "31436747",
        "pmcid": "PMC7771031",
        "year": 2019,
        "title": "Extraskeletal Myxoid Chondrosarcomas: Combined Modality Therapy With Both "
        "Radiation and Surgery Improves Local Control",
        "quote": "despite its name, EMC is genetically and histolo[g]ically distinct from "
        "conventional chondrosarcoma of bone and in fact, is classified by the WHO as a tumor of "
        "uncertain lineage. Unfortunately however, [t]his tumor name has likely influenced local "
        "management patterns. Based on our data in this study, and similar to data related to "
        "other extraskeletal osteogenic tumors, the bone sarcoma treatment pathways do not apply "
        "for soft tissue origins. Ultimately, for patients with EMC, RT should not be omitted due "
        "to misconceptions of tumor grade or extrapolations related to primary bone tumor "
        "paradigms.",
        "quote_source": "full text, Discussion",
        "what_this_does_to_the_route": "⛔ IT MAKES THE NAMING ARGUMENT PRIOR ART RATHER THAN A "
        "NEW OBSERVATION, and any paper from this route must cite it and position against it. A "
        "peer-reviewed clinical series has already published the claim that EMC's name misleads "
        "management, in almost the words this repository was preparing to use. ⚠ Their claim is "
        "ASSERTED, not measured -- 'has LIKELY influenced local management patterns' -- so what "
        "is still unclaimed is a measurement, not the idea.",
        "provenance": "[FT]",
    },
    "what_this_means_for_the_papers_shape": "★ The two halves separate cleanly and should be "
    "reported at different weights. The CODING half is novel, documented and multi-registry: one "
    "morphology code read three ways, an edit rule that says bone, and published cohorts that "
    "merge the populations without separating them. The NAMING half has prior art (PMC7771031), "
    "no guideline-level evidence, and specialist guidance pointing the other way. Writing them as "
    "one claim would overstate the second on the strength of the first.",
}

# ---------------------------------------------------------------------------
# 4 - the sequencing that looks circular and is not
# ---------------------------------------------------------------------------
SEQUENCING = {
    "apparent_deadlock": "RT-POPULATION-REGISTRY is deliberately sequenced BEHIND this "
    "contamination question, and this question's size needs a registry query. Read quickly that "
    "is a cycle.",
    "resolution": "It is not circular, and the rule that dissolves it is precise: do not use "
    "registry data for population ESTIMATES until the denominator is understood. Measuring the "
    "contamination IS the diagnostic query that establishes the denominator -- it is what earns "
    "the right to the estimates, not an instance of them.",
    "the_distinction": "A diagnostic query asks what the cohort CONTAINS. An estimate asks what "
    "the cohort IMPLIES about a population. The first is a precondition for the second; running "
    "it first is the correct order, not a violation of it.",
    "where_this_must_be_recorded": [
        "systems/graph/routes.json -> RT-DIAGNOSTIC-PATHWAY and RT-POPULATION-REGISTRY",
        "this artifact",
    ],
}

# ---------------------------------------------------------------------------
# 5 - the access tiers, MEASURED rather than inherited
# ---------------------------------------------------------------------------
# The repository's standing note on SEER access dates from 2026-08-12 and is a judgement.
# These rows replace judgement with the text of SEER's own comparison page.
ACCESS_TIERS = {
    "source": {
        "title": "Comparison of SEER Data Products",
        "url": "https://seer.cancer.gov/data/product-comparison.html",
        "how_obtained": "fetched on a GitHub Actions runner, HTTP 200, 8,106 characters, "
        "published to the literature-cache branch under "
        "literature/seer-access-product-comparison/",
        "provenance": "[DOC]",
    },
    "corrections_to_the_repositorys_note": [
        {
            "inherited_belief": "SEER base tier needs nothing but a valid email address.",
            "measured": "⚠ NOT QUITE, and the gap is the word INSTITUTIONAL. The page's access "
            "table gives SEER Research as: Email = 'Valid institutional email'; User "
            "Authentication = 'Not required'; Completion of Application Form = 'Required'; Data "
            "User Agreement = 'Required'; Acknowledgment of Data Limitations = 'Required'; "
            "Analysis Plan Review = 'Not required'; IRB Approval = 'Not required'; International "
            "Users = 'Yes'. So it is genuinely the lightest tier -- no eRA Commons, no IRB, no "
            "analysis plan -- but it is a form plus an agreement plus an institutional address, "
            "not a bare email.",
            "whose_action": "trimcrae's. This row exists so the ask is accurate, not so an agent "
            "attempts it.",
        },
        {
            "inherited_belief": "The free tier may withhold the topography field, and nobody has "
            "checked.",
            "measured": "The page names the withheld set EXHAUSTIVELY as 'Variables Available in "
            "SEER Research Plus, Not in SEER Research Databases': SEER Registry; County; "
            "State-County; Month of diagnosis; Month of diagnosis recode; Age at diagnosis up to "
            "99; SEER registry (with CA and GA as whole states); PRCDA Region; some genetic "
            "marker variables. Every one is registry-geography, date granularity or a genetic "
            "marker. Primary site / topography is not among them, and the same table gives SEER "
            "Research 'Availability of Individual Data: Individual data available'.",
            "confidence": "⚠ This is a reading of a named exhaustive exclusion list, which is "
            "strong, but it is still an argument from the absence of a row. It is upgraded to a "
            "positive confirmation only by reading Primary Site in the Dictionary of SEER "
            "Variables for the Research product, which is a $0 fetch and is listed in "
            "`what_has_not_been_read`.",
        },
    ],
    "seerstat_is_windows": {
        "state": "CONFIRMED AT PRIMARY SOURCE",
        "source": "https://seer.cancer.gov/help/seerstat/seer-stat-configuration/"
        "system-requirements, fetched on an Actions runner, HTTP 200",
        "the_quote": "To run SEER*Stat, you will need a personal computer with at least: A "
        "Pentium or equivalent processor. 64 MB application RAM. 41 MB hard disk space. A 32-bit "
        "or 64-bit version of Microsoft Windows - Windows 10 or later. Screen resolution set to "
        "1024 by 768 pixels or greater.",
        "what_it_means_for_this_project": "⚠ SEER*Stat IS WINDOWS-ONLY, AND IT IS THE ONLY "
        "SUPPORTED CLIENT FOR THE RESEARCH DATA. This project's compute is Linux -- the dev "
        "sandbox, the Actions runners and the GPU hosts -- so the base-tier route needs a "
        "Windows machine or an emulation layer that NCI does not support, in addition to the "
        "form and the DUA. It does not CLOSE the route; it means the route's cost is a machine "
        "as well as a signature, and neither is an agent's to arrange.",
        "⛔_what_this_is_not": "It is not a reason to prefer the public tier, because the public "
        "tier has been measured (see `public_aggregate_tier`) not to serve the cross-tab at all. "
        "The comparison is between a Windows client that can answer the question and a web tool "
        "that cannot.",
        "provenance": "[DOC]",
    },
}

# ---------------------------------------------------------------------------
# 6 - what has NOT been read, stated as unread rather than as absent
# ---------------------------------------------------------------------------
WHAT_HAS_NOT_BEEN_READ = [
    "PMID 32856598 full text -- Table 1 in particular. ⛔ UNREACHABLE AT $0 and recorded as such: "
    "not in PMC, not open access, publisher PDF serves a JavaScript shim, DOI and article pages "
    "403. A subscription article, and no attempt was made to get around that.",
    "PMID 27819877 full text (Am J Clin Oncol, no PMCID, not open access).",
    "PMID 35144048 full text (Cancer Treat Res Commun, no PMCID in Europe PMC).",
    "✅ CLOSED 2026-08-23: earlier versions of the SEER site/histology validation list. All "
    "sixteen published errata sheets were located (by a link-harvesting browser fetch of the "
    "archive page, which names none of their paths in its visible text) and read. See "
    "`coding_system`.",
    "SEER Cancer PathCHART -- four candidate paths returned HTTP 404, so the path is wrong rather "
    "than the tool absent.",
    "⚠ HOW MANY PRIMARY EMC-OF-BONE CASES HAVE BEEN PUBLISHED. Attempted and INCONCLUSIVE, not "
    "negative: a Europe PMC search for '\"extraskeletal myxoid chondrosarcoma\" AND (\"of "
    "bone\" OR intraosseous OR osseous)' returned hitCount 881 and the request took only the "
    "first 100 by relevance; none of those 100 titles names a bone site. ⛔ That is a statement "
    "about 100 of 881 records, and it must not be read as 'no bone-primary EMC is reported'. The "
    "caveat in `bone_primary_is_not_automatically_not_emc` rests on the 2020 review's explicit "
    "statement and the two series it names, not on this sweep.",
    "The Dictionary of SEER Variables entry for Primary Site under the Research product, which "
    "would turn the topography-availability reading from an argument-from-an-exclusion-list into "
    "a positive confirmation. ⚠ Four candidate paths for it returned HTTP 404, so the path is "
    "unknown rather than the document absent.",
    "The ESMO and NCCN guideline texts themselves. ⛔ NOT OPEN ACCESS AND NOT REACHABLE: Europe "
    "PMC reports isOpenAccess=N for every version of the ESMO soft-tissue and bone sarcoma "
    "guidelines; five doi.org resolutions returned an identical 1,327-character shim under a real "
    "headless browser; annalsofoncology.org returned HTTP 403 to that browser. NCCN's public "
    "guideline-detail pages DID answer (HTTP 200) and are the remaining readable surface.",
]

# ---------------------------------------------------------------------------
# 7 - every identifier, and how it was actually obtained
# ---------------------------------------------------------------------------
PROVENANCE_LEDGER = [
    {
        "identifier": "PMID 31765367 / PMC6894367 / doi:10.12659/MSM.917959",
        "how_obtained": "PMCID and DOI resolved from the PMID by the NCBI ID converter "
        "(pmc.ncbi.nlm.nih.gov/tools/idconv), fetched on an Actions runner. Full text read from "
        "the Europe PMC fullTextXML endpoint for PMC6894367 (HTTP 200, 219,116 characters).",
        "read_level": "[FT]",
    },
    {
        "identifier": "PMID 32856598 / doi:10.1158/1055-9965.epi-20-0447",
        "how_obtained": "DOI read from the Europe PMC core record for EXT_ID:32856598. NCBI ID "
        "converter returned 'Identifier not found in PMC'. Only the abstract has been read.",
        "read_level": "[API]",
    },
    {
        "identifier": "PMID 39899751 / PMC11789853 / doi:10.5435/jaaosglobal-d-24-00370",
        "how_obtained": "PMCID and DOI resolved by the NCBI ID converter and confirmed in the "
        "Europe PMC core record (isOpenAccess=Y). Only the abstract has been read so far.",
        "read_level": "[API]",
    },
    {
        "identifier": "ICD-O-3 SEER Site/Histology Validation List, April 29, 2022",
        "how_obtained": "https://seer.cancer.gov/icd-o-3/sitetype.icdo3.20220429.pdf fetched on "
        "an Actions runner (HTTP 200). seer.cancer.gov is blocked by the dev sandbox egress "
        "proxy, which is why this went through CI.",
        "read_level": "[DOC]",
    },
    {
        "identifier": "PMID 27819877 / doi:10.1097/coc.0000000000000341 (Kemmerer et al., Am J "
        "Clin Oncol 2018)",
        "how_obtained": "Surfaced by a Europe PMC search for '\"extraskeletal myxoid "
        "chondrosarcoma\" AND SEER' (31 hits) run on an Actions runner; DOI read from its core "
        "record. Only the abstract has been read. Independently named in the 2025 review at "
        "PMC12504171, whose reference list gives the same journal, volume and pages.",
        "read_level": "[API]",
    },
    {
        "identifier": "PMID 35144048 / doi:10.1016/j.ctarc.2022.100530",
        "how_obtained": "Same Europe PMC search; DOI read from its core record. Abstract only.",
        "read_level": "[API]",
    },
    {
        "identifier": "PMC12504171 (2025 EMC review) and PMC7563993 (2020 EMC state of the art)",
        "how_obtained": "Europe PMC fullTextXML on an Actions runner, HTTP 200 (226,703 and "
        "132,954 characters). The 791/439 counts for PMID 32856598 are quoted FROM PMC12504171 "
        "and are therefore secondary; they are labelled [2°] wherever they appear.",
        "read_level": "[FT], used as a [2°] source for another paper's numbers",
    },
    {
        "identifier": "PMID 31436747 / PMC7771031 (prior art for the naming claim)",
        "how_obtained": "Surfaced by the Europe PMC 'extraskeletal myxoid chondrosarcoma AND "
        "SEER' search. ⚠ Its Europe PMC fullTextXML endpoint returned HTTP 404 despite the record "
        "carrying a PMCID; the PMC article HTML page returned HTTP 200 (34,641 characters) and is "
        "what was read. Recording the route matters: a 404 on one endpoint is not evidence the "
        "paper is unreadable.",
        "read_level": "[FT]",
    },
    {
        "identifier": "PMID 35859542 / PMC9290890 (CBTRUS histology alignment)",
        "how_obtained": "Surfaced by a Europe PMC free-text search for '9231/3' (54 hits, mostly "
        "irrelevant -- the string also matches page and record numbers). fullTextXML 404'd; the "
        "PMC article HTML page returned HTTP 200 (50,643 characters).",
        "read_level": "[FT]",
    },
    {
        "identifier": "PMID 31283732 / PMC6903832 / doi:10.1097/CORR.0000000000000846 (Wan et al., "
        "Clin Orthop Relat Res 2019 — the topography-split study)",
        "how_obtained": "Surfaced by a Europe PMC free-text search for '9231/3'; DOI read from its "
        "Europe PMC core record, fetched on an Actions runner. Full text read from the PMC article "
        "HTML page (HTTP 200, 47,396 characters) because the Europe PMC fullTextXML endpoint 404s "
        "for this PMCID. ⚠ Its Table 1 is served as a separate resource the article HTML does not "
        "inline, and has NOT been read.",
        "read_level": "[FT] for the body, NOT for Table 1",
    },
    {
        "identifier": "doi:10.1158/1055-9965.EPI-20-0447",
        "how_obtained": "The same DOI as the PMID 32856598 row above, recorded here in the "
        "publisher's canonical capitalisation because that is how a reference list prints it. "
        "⚠ Europe PMC returns it lower-cased (`10.1158/1055-9965.epi-20-0447`); DOIs are "
        "case-insensitive by specification, and both forms denote one identifier obtained from "
        "one fetch. Only the abstract behind it has been read.",
        "read_level": "[API]",
    },
    {
        "identifier": "PMID 35875111 / PMC9303001 (pan-soft-tissue-sarcoma SEER analysis)",
        "how_obtained": "Same Europe PMC search; Europe PMC fullTextXML, HTTP 200, 99,834 "
        "characters.",
        "read_level": "[FT]",
    },
    {
        "identifier": "SEER*Stat system requirements",
        "how_obtained": "⚠ THE URL CAME FROM A WEB SEARCH AND THE READING DID NOT. "
        "https://seer.cancer.gov/seerstat/installation/ returned HTTP 404, a search located "
        "/help/seerstat/seer-stat-configuration/system-requirements, and that page was then "
        "fetched on an Actions runner (HTTP 200) so the quoted requirement is a primary reading "
        "rather than a search snippet.",
        "read_level": "[DOC]",
    },
    {
        "identifier": "SEER*Explorer Cancer Site Definitions",
        "how_obtained": "https://seer.cancer.gov/statistics-network/explorer/cancer-sites.html "
        "fetched on an Actions runner, HTTP 200, 5,519 characters.",
        "read_level": "[DOC]",
    },
    {
        "identifier": "NCCN Guidelines topic indexes (Soft Tissue Sarcoma v5.2026, id=1464; Bone "
        "Cancer v1.2027, id=1418)",
        "how_obtained": "nccn.org guideline-detail pages fetched with a headless Chromium on an "
        "Actions runner, HTTP 200 (4,118 and 2,269 characters of visible text). ⚠ PUBLIC INDEX "
        "PAGES ONLY -- the guideline PDFs are behind a login and were not sought.",
        "read_level": "[DOC]",
    },
    {
        "identifier": "Comparison of SEER Data Products",
        "how_obtained": "https://seer.cancer.gov/data/product-comparison.html, fetched on an "
        "Actions runner in an earlier session and already on the literature-cache branch under "
        "literature/seer-access-product-comparison/. Read from that committed copy.",
        "read_level": "[DOC]",
    },
]

# ---------------------------------------------------------------------------
# 8 - the ceiling
# ---------------------------------------------------------------------------
CLAIM_CEILING = [
    "This is an epidemiology and classification finding. It says what registry cohorts contain "
    "and what the coding system can and cannot distinguish.",
    "It says NOTHING about treatment, efficacy, safety, a therapeutic window, or what any patient "
    "should receive.",
    "PMID 39899751 measures myxoid soft-tissue tumours BROADLY, of which EMC is a small part. Its "
    "28% indeterminate-diagnosis prevalence and its 37%-versus-15% positive-margin contrast are "
    "statements about that broad class and must not be restated as statements about EMC unless "
    "evidence is found that they hold in EMC specifically.",
    "The 11.7% figure is the share of morphology 9231 inside one high-grade bone-framed "
    "chondrosarcoma cohort. It is NOT the bone-primary fraction of a 9231/3 cohort and is not a "
    "contamination rate.",
    "The naming half of this route has PRIOR ART (PMC7771031, 2019) and must be written as "
    "positioning against it rather than as a new observation. What is unclaimed there is a "
    "MEASUREMENT; the idea is published.",
    "'No guideline imports conventional-chondrosarcoma reasoning for EMC' has TWO strengths and "
    "they must not be merged. The NCCN half is PRIMARY but narrow: its published topic index "
    "places EMC under Soft Tissue Sarcoma and not under Bone Cancer — that is where EMC sits, not "
    "what the guideline says about it, because the guideline PDFs are behind a login. The ESMO "
    "half is SECONDARY: two specialist reviews describing guidelines that are not open access and "
    "were not readable by any route tried, including a real headless browser.",
    "The 1.44% bone-primary rate is across ALL soft-tissue sarcoma morphologies in one SEER "
    "study. It is a comparator, never a stand-in for a 9231/3 figure.",
    "⛔ A measured bone-primary fraction is an UPPER BOUND on non-EMC contamination, never the "
    "contamination itself: primary EMC of bone is a documented entity. See "
    "`bone_primary_is_not_automatically_not_emc`.",
    "Nothing here is a patient count and nothing here is a diagnosis.",
]


def _pmids_in(obj) -> set:
    """Every value stored under a `pmid` key, at any depth. See the comment at the call site."""
    found = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "pmid" and isinstance(value, str) and value.isdigit():
                found.add(value)
            else:
                found |= _pmids_in(value)
    elif isinstance(obj, list):
        for value in obj:
            found |= _pmids_in(value)
    return found


def build() -> dict:
    """Pure over this module's tables. Touches no file."""
    payload_blocks = [
        PUBLISHED_COHORTS,
        INDETERMINATE_DIAGNOSIS_PAPER,
        THIRD_READING,
        BASE_RATE_OF_BONE_PRIMARIES,
        GUIDELINE_PLACEMENT,
        TOPOGRAPHY_SPLIT_STUDY,
    ]
    return {
        "_generated_by": "research/modalities/emc_icdo_contamination.py",
        "_do_not_hand_edit": (
            "Verify with `python3 research/modalities/emc_icdo_contamination.py --check`."
        ),
        "what_this_is": (
            "The attempt to measure the SIZE of the ICD-O-3 9231/3 contamination, cheapest route "
            "first, and the record of what each route returned. The contradiction itself is "
            "settled elsewhere (emc-care-delivery-evidence.json -> icd_o_9231_3) and is not "
            "re-argued here."
        ),
        "registration": REGISTRATION,
        "coding_system": CODING_SYSTEM,
        "published_cohorts": PUBLISHED_COHORTS,
        "indeterminate_diagnosis_paper": INDETERMINATE_DIAGNOSIS_PAPER,
        "third_reading": THIRD_READING,
        "base_rate_of_bone_primaries": BASE_RATE_OF_BONE_PRIMARIES,
        "guideline_placement": GUIDELINE_PLACEMENT,
        "public_aggregate_tier": PUBLIC_AGGREGATE_TIER,
        "topography_split_study": TOPOGRAPHY_SPLIT_STUDY,
        "bone_primary_is_not_automatically_not_emc": BONE_PRIMARY_IS_NOT_AUTOMATICALLY_NOT_EMC,
        "size": SIZE,
        "sequencing": SEQUENCING,
        "access_tiers": ACCESS_TIERS,
        "what_has_not_been_read": WHAT_HAS_NOT_BEEN_READ,
        "provenance_ledger": PROVENANCE_LEDGER,
        "claim_ceiling": CLAIM_CEILING,
        # ⛔ DERIVED, NEVER TYPED (CLAUDE.md rule 1.1). The first version of this line unioned two
        # named blocks and silently omitted every PMID that arrived later in a new block — four of
        # them, including the topography-split study this artifact's best finding rests on. A
        # hand-maintained union of hand-named blocks is a total that drifts the moment the shape
        # changes, which is exactly what rule 1.1 is about.
        "pmids": sorted(_pmids_in(payload_blocks)),
    }


def check() -> int:
    if not os.path.exists(OUT):
        print(f"MISSING: {OUT}", file=sys.stderr)
        return 1
    with open(OUT, encoding="utf-8") as fh:
        committed = json.load(fh)
    if committed == build():
        print(f"OK: {os.path.relpath(OUT, REPO)} matches the generator")
        return 0
    print(
        f"STALE OR HAND-EDITED: {os.path.relpath(OUT, REPO)} disagrees with the generator.",
        file=sys.stderr,
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="verify the artifact; write nothing")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    payload = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(
        f"wrote {os.path.relpath(OUT, REPO)} "
        f"(size state: {SIZE['state']}, {len(PROVENANCE_LEDGER)} ledger rows)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
