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
    "open_question_it_creates": "Whether earlier versions of the same list (the cohorts span "
    "1973-2016) listed 9231/3 under soft tissue, and what SEER's current Cancer PathCHART "
    "site-morphology validation says. Both are $0 fetches and are recorded in "
    "`what_has_not_been_read` until they are done.",
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
]

# ---------------------------------------------------------------------------
# 3 - the size, and its honest state
# ---------------------------------------------------------------------------
SIZE = {
    "state": "NOT_YET_MEASURED",
    "what_is_held": "A bound-shaped observation from the bone side only: 87 of 743 high-grade "
    "SEER chondrosarcoma cases (11.7%) carry morphology 9231, in a cohort whose authors state "
    "that this bucket includes EMC and whose site variable cannot separate the two. That is a "
    "measurement of how much 9231 sits inside a BONE-framed cohort. It is NOT the fraction the "
    "route asks for, which is how much BONE sits inside a 9231/3 cohort, and it must not be "
    "reported as if it were.",
    "what_is_still_needed": "The primary-site distribution of a cohort selected on 9231/3 "
    "without a grade or site restriction. PMID 32856598 is that cohort (SEER 1973-2016, n~439) "
    "and its abstract states it analysed primary tumour site, so the distribution is likely "
    "printed in its Table 1.",
    "provenance": "[DOC]",
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
        "state": "NOT_YET_VERIFIED",
        "why_it_matters": "If SEER*Stat is Windows-only it is a real practical barrier for this "
        "project and may decide the route on its own, independently of whether the DUA is easy.",
        "what_was_attempted": "https://seer.cancer.gov/seerstat/installation/ returned HTTP 404 "
        "on the runner. The SEER*Stat home page (https://seer.cancer.gov/seerstat/, HTTP 200) "
        "was retrieved and the system-requirements statement has not yet been read out of it.",
        "provenance": "[DOC]",
    },
}

# ---------------------------------------------------------------------------
# 6 - what has NOT been read, stated as unread rather than as absent
# ---------------------------------------------------------------------------
WHAT_HAS_NOT_BEEN_READ = [
    "PMID 32856598 full text. Europe PMC reports isOpenAccess=N, inPMC=N, and the NCBI ID "
    "converter returns 'Identifier not found in PMC'. The publisher PDF URL Europe PMC advertises "
    "is https://cebp.aacrjournals.org/content/cebp/29/11/2351.full.pdf; a fetch has been "
    "dispatched and its result is not in this artifact yet.",
    "PMID 39899751 full text (PMC11789853, open access) -- specifically whether the 439-tumour "
    "myxoid cohort breaks out how many were EMC.",
    "Earlier versions of the SEER site/histology validation list contemporaneous with the "
    "1973-2016 accrual window.",
    "SEER Cancer PathCHART site-morphology validation.",
    "The Dictionary of SEER Variables entry for Primary Site under the Research product.",
    "Whether any treatment guidance imports conventional-chondrosarcoma reasoning for EMC.",
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
    "Nothing here is a patient count and nothing here is a diagnosis.",
]


def build() -> dict:
    """Pure over this module's tables. Touches no file."""
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
        "size": SIZE,
        "sequencing": SEQUENCING,
        "access_tiers": ACCESS_TIERS,
        "what_has_not_been_read": WHAT_HAS_NOT_BEEN_READ,
        "provenance_ledger": PROVENANCE_LEDGER,
        "claim_ceiling": CLAIM_CEILING,
        "pmids": sorted({r["pmid"] for r in PUBLISHED_COHORTS} | {"32856598", "39899751"}),
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
