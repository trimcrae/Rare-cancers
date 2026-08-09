#!/usr/bin/env python3
"""The published evidence on what actually determines survival in EMC today.

WHY THIS EXISTS
---------------
This repository's route board asks one question 68 times -- *what should we give an EMC patient?*
-- and never asks *what determines how long an EMC patient lives now*. The modality census makes
the omission structural rather than accidental: its four bands are all intervention taxonomies,
and `MOD-SURGERY` ("Wide local excision and metastasectomy") is graded `in_clinical_use`, i.e.
filed as incumbent arsenal and excluded from grading. A census built to find NEW modalities cannot
see variance inside the existing one -- and in a disease where no systemic agent has a
demonstrated survival benefit, that is where the realised survival is.

This module records what the published record already says about that, so the routes in
`ST-CARE-DELIVERY` rest on citable evidence rather than on plausibility.

⭐ THE LOAD-BEARING FINDING IS THE ICD-O ONE, AND IT IS A CONTRADICTION BETWEEN TWO PUBLISHED
METHODS SECTIONS RATHER THAN AN OPINION ABOUT CODING. Morphology code `9231/3` is queried by one
SEER study as *extraskeletal* myxoid chondrosarcoma and enumerated by another as one histological
subtype of *chondrosarcoma of bone*. Both are in `findings`, quoted. A morphology code carries no
skeletal-versus-extraskeletal information -- that lives in the separate topography axis -- so a
query on morphology alone cannot separate them, and neither paper is misusing the code. The defect
is in the code, and it lands on every SEER-based EMC number this repository cites.

PROVENANCE DISCIPLINE
---------------------
Every row carries `provenance`. `[API]` means the structured Europe PMC record (title, abstract,
identifiers) was read; `[FT]` means the fetched full text was read. ⛔ Nothing here is `[FT]`
beyond the passages quoted, and an abstract is not a paper: a number read from an abstract has not
been checked against the paper's own tables, and several of these will move when it is. That is a
statement about THIS artifact's verification level, not about the sources.

⛔ WHAT THIS IS NOT. Not a pooled analysis and not an estimate of anything. Every number is quoted
as its source printed it, one row per source, with NO combination across rows -- combining these
would need `systems/POLICY-evidence.md` s2, and several rows are the population-overlapping
SEER analyses that s2.3 excludes from pooling by construction.

Corpus: dispatched via `.github/workflows/fetch-literature.yml` on 2026-08-09 (run 31341462928,
554 open-access records, known-positive control PMID 32856598 passed), published to the
`literature-cache` branch under `literature/emc-care-delivery-and-classification/`.

Stdlib only.
Run:     python3 research/modalities/emc_care_delivery_evidence.py
Verify:  python3 research/modalities/emc_care_delivery_evidence.py --check
Writes:  research/modalities/emc-care-delivery-evidence.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "research", "modalities", "emc-care-delivery-evidence.json")

CORPUS = {
    "workflow": ".github/workflows/fetch-literature.yml",
    "run_id": 31341462928,
    "dispatched": "2026-08-09",
    "records": 554,
    "branch": "literature-cache",
    "path": "literature/emc-care-delivery-and-classification/",
    "known_positive_control": {
        "pmid": "32856598",
        "passed": True,
        "note": "The workflow fails the run when a declared expect_pmids control is absent, so a "
        "green run is evidence the query returned the paper it was required to return.",
    },
}

# ---------------------------------------------------------------------------
# 1 - the ICD-O finding: one code, two incompatible disease definitions
# ---------------------------------------------------------------------------
ICD_O = {
    "code": "9231/3",
    "label_in_icd_o_3": "myxoid chondrosarcoma",
    "question": "Does ICD-O-3 morphology code 9231/3 separate EMC from skeletal myxoid "
    "chondrosarcoma, and is a SEER-based EMC cohort therefore a cohort of EMC?",
    "answer": "NO on the first, and the second does not follow. The two published SEER studies "
    "below use the same morphology code for mutually incompatible populations. A morphology code "
    "carries no information about whether a tumour arose in bone or soft tissue -- ICD-O keeps "
    "that on the separate topography axis -- so neither study is misusing the code, and the "
    "ambiguity cannot be resolved from the morphology field alone.",
    "sides": [
        {
            "reads_the_code_as": "extraskeletal myxoid chondrosarcoma",
            "pmid": "32856598",
            "year": 2020,
            "title": "Long-term Outcomes for Extraskeletal Myxoid Chondrosarcoma: A SEER "
            "Database Analysis",
            "quote": "We queried the SEER 1973-2016 database for patients with myxoid "
            "chondrosarcoma (ICD-O-3: 9231/3).",
            "quote_source": "abstract, Methods",
            "provenance": "[API]",
        },
        {
            "reads_the_code_as": "one histological subtype of chondrosarcoma (a bone tumour "
            "study; the code sits beside 9220 chondrosarcoma NOS and 9221 juxtacortical)",
            "pmid": "31765367",
            "pmcid": "PMC6894367",
            "year": 2019,
            "title": "Prognostic Factors and Treatment Options for Patients with High-Grade "
            "Chondrosarcoma",
            "quote": "The following histologic ICD-O-3 codes ... were included: code 9220 "
            "(chondrosarcoma not otherwise specified), code 9221 (juxtacortical "
            "chondrosarcoma), code 9231 (myxoid chondrosarcoma), code 9240 (mesenchymal "
            "chondrosarcoma), code 9242 (clear cell chondrosarcoma) and code 9243 "
            "(dedifferentiated chondrosarcoma).",
            "quote_source": "full text, Materials and Methods",
            "provenance": "[FT]",
        },
    ],
    "consequence_for_this_repository": "Every SEER-derived EMC figure cited here inherits an "
    "unquantified contamination whose size nobody has measured. This does not retract any of "
    "them; it means the question 'how much of that cohort is EMC?' has never been asked, and it "
    "is answerable from the topography field the same databases carry.",
    "consequence_for_the_clinic": "Separate from the registry problem and possibly larger: the "
    "disease's NAME places it inside a tumour class it does not belong to. EMC is not "
    "cartilaginous and is classed by WHO as a tumour of uncertain differentiation, so a clinician "
    "reasoning from the name may import conventional-chondrosarcoma expectations. This "
    "repository already noticed one instance of that -- the IDH/ivosidenib row in "
    "emc-unexplored-treatment-lanes.md s6, closed as a 'nominal name-match only' -- and filed it "
    "as a one-paragraph curiosity rather than as an instance of a general problem.",
    "what_would_close_it": "Re-run a SEER 9231/3 query split by ICD-O topography (soft tissue vs "
    "bone primary sites) and report the split. That is the measurement nobody has published, and "
    "it needs a SEER data-use agreement rather than a fetch.",
}

# ---------------------------------------------------------------------------
# 2 - what the record says about the care that is actually delivered
# ---------------------------------------------------------------------------
# One row per source. NOTHING here is combined across rows -- see the docstring.
FINDINGS = [
    {
        "id": "surgery-is-the-lever",
        "route": "RT-SURGICAL-QUALITY",
        "pmid": "32856598",
        "year": 2020,
        "design": "SEER 1973-2016, n=439 (373 locoregional)",
        "what_it_says": "In locoregional disease, surgery was associated with superior overall "
        "survival (HR 0.27, 95% CI 0.16-0.47 univariate; HR 0.36, 95% CI 0.19-0.69 in the "
        "adjusted sensitivity analysis). Chemotherapy (HR 1.90, 95% CI 1.11-3.27) and "
        "radiotherapy (HR 1.45, 95% CI 1.03-2.06) were associated with INFERIOR survival. "
        "10-year OS with distant disease was 10% (95% CI 2%-25%).",
        "why_it_matters": "The single largest published survival association in this disease is "
        "an operation, and no route on this board covered it. ⚠ The inferior chemo/RT hazards "
        "are textbook confounding by indication -- sicker patients receive them -- and must not "
        "be read as harm; the same paper's own adjusted model dissolves most of the effect.",
        "carries_the_icd_o_caveat": True,
        "provenance": "[API]",
    },
    {
        "id": "indeterminate-diagnosis-costs-the-margin",
        "route": "RT-DIAGNOSTIC-PATHWAY",
        "pmid": "39899751",
        "year": 2025,
        "design": "retrospective, 439 myxoid soft-tissue tumours; 235 with biopsy data",
        "what_it_says": "28% (66/235) of musculoskeletal myxoid soft-tissue tumours had an "
        "INDETERMINATE diagnosis before resection. Among those that proved sarcoma with 2-year "
        "follow-up, the positive-margin rate was 37% (10/27) versus 15% (11/74) when malignancy "
        "was known preoperatively.",
        "why_it_matters": "⭐ This is the causal chain the portfolio has no route for, MEASURED, "
        "and in myxoid tumours specifically: diagnostic uncertainty before the operation more "
        "than doubles the positive-margin rate at it. It links avenue 5 (diagnosis) to avenue 2 "
        "(the first operation) with a number rather than an argument.",
        "carries_the_icd_o_caveat": False,
        "provenance": "[API]",
    },
    {
        "id": "the-disease-outruns-its-follow-up",
        "route": "RT-SURVEILLANCE",
        "pmid": "32572850",
        "year": 2021,
        "design": "Italian Sarcoma Group, 3 referral centres, n=67 localised, NR4A3-rearrangement "
        "confirmed, centrally reviewed to WHO 2013, median follow-up 55 months",
        "what_it_says": "5-year OS 94% (86-100) and 10-year OS 84% (69-98), against 5-year "
        "disease-free survival 51% (38-65) and 10-year DFS 20% (7-33). 35/67 (52%) relapsed -- 9 "
        "local, 26 distant.",
        "why_it_matters": "The gap between an 84% 10-year OS and a 20% 10-year DFS is the whole "
        "case for the surveillance route: most patients relapse, most are alive years later, and "
        "the interval between those two facts is where a resectable recurrence either is or is "
        "not found. It is also the cleanest EMC cohort in the corpus -- molecularly confirmed and "
        "centrally reviewed, so it carries no ICD-O contamination.",
        "carries_the_icd_o_caveat": False,
        "provenance": "[API]",
    },
    {
        "id": "single-centre-surgical-series",
        "route": "RT-SURGICAL-QUALITY",
        "pmid": "36326382",
        "year": 2022,
        "design": "single reference centre, n=13, 2006-2018",
        "what_it_says": "All 13 underwent wide resection with one positive margin; 38.5% "
        "recurred, 46.2% developed lung metastasis, 53.8% died. Median survival 61 months, "
        "5-year survival 51.8%. No significant survival difference by age, sex, side, limb "
        "location, postoperative radiotherapy, recurrence or lung metastasis.",
        "why_it_matters": "The only EMC paper in the corpus whose subject IS the operation. ⚠ At "
        "n=13 with 7 deaths every one of its null findings is underpowered, and the absence of a "
        "radiotherapy effect here must not be read against the two series that disagree.",
        "carries_the_icd_o_caveat": False,
        "provenance": "[API]",
    },
]

# ---------------------------------------------------------------------------
# 3 - an absence, reported as a result
# ---------------------------------------------------------------------------
ABSENCES = [
    {
        "id": "no-emc-metastasectomy-literature",
        "route": "RT-METASTASECTOMY",
        "query": "metastasectom* within the EMC-matching subset of a 554-record open-access "
        "corpus retrieved 2026-08-09",
        "result": "ZERO records.",
        "reading": "⭐ The absence is the finding and it is the route's justification, not an "
        "obstacle to it. EMC is indolent, lung-metastasis-dominant and measured in decades -- the "
        "profile for which pulmonary metastasectomy is standard practice in sarcoma generally -- "
        "and no paper in this corpus asks the question in EMC. ⚠ An open-access corpus is not the "
        "literature: this bounds what a 554-record open-access sweep contains, and a closed-access "
        "series or a chapter could exist. The claim is 'not found here', never 'does not exist'.",
        "provenance": "[API]",
    },
]


def build() -> dict:
    """Pure over this module's tables. Touches no file."""
    by_route: dict[str, list[str]] = {}
    for row in FINDINGS + ABSENCES:
        by_route.setdefault(row["route"], []).append(row["id"])
    return {
        "_generated_by": "research/modalities/emc_care_delivery_evidence.py",
        "_do_not_hand_edit": (
            "Verify with `python3 research/modalities/emc_care_delivery_evidence.py --check`."
        ),
        "what_this_is": (
            "What the published record already says about the determinants of EMC survival that "
            "are not a new agent. One row per source; NOTHING is combined across rows."
        ),
        "corpus": CORPUS,
        "icd_o_9231_3": ICD_O,
        "findings": FINDINGS,
        "absences": ABSENCES,
        "rows_by_route": by_route,
        "pmids": sorted({r["pmid"] for r in FINDINGS} | {s["pmid"] for s in ICD_O["sides"]}),
        "verification_level": (
            "Mixed and labelled per row. Most rows are [API] -- the structured Europe PMC record, "
            "i.e. the abstract. An abstract is not a paper and a number read from one has not "
            "been checked against the source's own tables. Upgrading the four FINDINGS rows to "
            "[FT] is the next $0 step and is a precondition for quoting any of these in a "
            "manuscript."
        ),
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
        f"({len(FINDINGS)} findings, {len(ABSENCES)} absences, "
        f"{len(payload['pmids'])} PMIDs)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
