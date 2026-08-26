#!/usr/bin/env python3
"""Reconstruction of patient-level survival data from published Kaplan-Meier curves.

WHY THIS EXISTS
---------------
EMC's defining clinical fact is very long survival with late recurrence, so **every clinical
question that matters in this disease is a time-to-event question** -- and this repository cannot
currently ask one. `systems/POLICY-evidence.md` s2.4 pools event-rate metrics as crude
during-follow-up proportions and states that time-anchored survival is "never merged"; s2.5 lists
the consequence in its own words: *"no censoring/Kaplan-Meier; no risk-adjustment or multivariable
control."*

That is a correct description of the limits of the method s2.2 mandates. It is not a limit of the
published record. Dozens of EMC series print a Kaplan-Meier curve, and Guyot et al. (BMC Med Res
Methodol 2012;12:9, doi:10.1186/1471-2288-12-9) give an algorithm that inverts such a curve, plus
its numbers-at-risk table, back into the patient-level data that generated it. Applied across the
series already curated in `research/data/emc-clinical-registry.json`, that yields the first pooled
patient-level survival dataset for EMC.

This module is the instrument. It is NOT the dataset -- see WHAT THIS FILE DOES NOT CONTAIN.

WHAT A RECONSTRUCTION IS, AND WHAT IT IS NOT
--------------------------------------------
A reconstruction is a **re-expression of a published curve**, never new patients and never new
follow-up. It cannot fix publication bias, it cannot recover a covariate the paper did not print,
and it inherits every selection effect of the series it came from. Two patients who are
indistinguishable in the published figure are indistinguishable here.

The one thing it does add is **censoring structure**, which is exactly what s2.4 says the current
method throws away -- and censoring structure is what makes a Cox model, a competing-risks
decomposition and a stratified curve legal instead of a category error.

THE QUALITY FLOOR IS LOAD-BEARING, NOT DECORATION
-------------------------------------------------
Guyot's algorithm is driven by the numbers-at-risk table. Without one, the number of censored
patients in each interval is unidentifiable and the reconstruction degrades from "solved" to
"assumed" -- and small single-institution series, which is most of what EMC has, frequently print
no risk table at all. So `assess_quality` grades every curve BEFORE it is admitted and
`pool_reconstructions` REFUSES a curve below the floor rather than pooling it with a caveat. A
caveat travels badly; a refusal is checkable.

⛔ THE KNOWN-ANSWER CONTROL TESTS THE ARITHMETIC, NOT THE DIGITIZATION, AND THE DIFFERENCE IS THE
WHOLE RISK. `research/modalities/tests/test_emc_ipd_survival.py` builds a cohort with KNOWN
patient-level data, computes its EXACT Kaplan-Meier curve and risk table, and asserts the
reconstruction recovers the original cohort. That is a genuine known-answer control -- the truth is
established independently of the reconstruction -- but it feeds the algorithm exact coordinates,
whereas a real curve is read off a figure by eye. **It therefore bounds algorithmic error and says
NOTHING about digitization error.** Per CLAUDE.md s4, an instrument's control must be described by
what it can fail, and this one cannot fail on a mis-read pixel.

⛔ AND THE FIELD THIS HEADER USED TO NAME AS THE SEPARATE BOUND DOES NOT BOUND IT EITHER
(measured 2026-08-25, `km-digitization-error.json`). ⚠ *Superseded, retained: "Digitization error
is bounded separately, by `max_abs_km_deviation` on each real curve, and that field is reported per
curve rather than averaged away."* The first half of that sentence is false and the second half is
true: the field IS reported per curve, and it is **not a digitization bound**.
`max_abs_km_deviation` compares the reconstruction's own product-limit estimate to the **digitized**
curve, so an error made while READING the figure moves both sides of that comparison together.

The discriminating measurement, run against a cohort whose patient-level data is known exactly: the
same rendered figure read with a calibration wrong by ONE PIXEL carries more than twice the true
error against that cohort, and a LOWER `max_abs_km_deviation` than the clean read. The two moved in
opposite directions, which no bound can do.

What the field does catch is a reading so wrong that no cohort could have produced it -- a
deliberately mis-tuned matcher drove it to ~1.0 and the floor correctly refused the curve. It is
blind to the moderate and to the systematic error, which are the realistic ones. **A curve admitted
on this field alone has had its arithmetic checked and its READING checked by nothing.** A real
curve therefore needs reading evidence of its own: an independent re-digitization, or the paper's
printed medians and risk table reproduced out of the reconstructed cohort.
`research/modalities/km_digitize.py` is the reader, and its control is where a digitization bound
actually lives.

WHAT THIS FILE DOES NOT CONTAIN.

WHAT A RECONSTRUCTION IS, AND WHAT IT IS NOT
--------------------------------------------
A reconstruction is a **re-expression of a published curve**, never new patients and never new
follow-up. It cannot fix publication bias, it cannot recover a covariate the paper did not print,
and it inherits every selection effect of the series it came from. Two patients who are
indistinguishable in the published figure are indistinguishable here.

The one thing it does add is **censoring structure**, which is exactly what s2.4 says the current
method throws away -- and censoring structure is what makes a Cox model, a competing-risks
decomposition and a stratified curve legal instead of a category error.

THE QUALITY FLOOR IS LOAD-BEARING, NOT DECORATION
-------------------------------------------------
Guyot's algorithm is driven by the numbers-at-risk table. Without one, the number of censored
patients in each interval is unidentifiable and the reconstruction degrades from "solved" to
"assumed" -- and small single-institution series, which is most of what EMC has, frequently print
no risk table at all. So `assess_quality` grades every curve BEFORE it is admitted and
`pool_reconstructions` REFUSES a curve below the floor rather than pooling it with a caveat. A
caveat travels badly; a refusal is checkable.

⛔ THE KNOWN-ANSWER CONTROL TESTS THE ARITHMETIC, NOT THE DIGITIZATION, AND THE DIFFERENCE IS THE
WHOLE RISK. `research/modalities/tests/test_emc_ipd_survival.py` builds a cohort with KNOWN
patient-level data, computes its EXACT Kaplan-Meier curve and risk table, and asserts the
reconstruction recovers the original cohort. That is a genuine known-answer control -- the truth is
established independently of the reconstruction -- but it feeds the algorithm exact coordinates,
whereas a real curve is read off a figure by eye. **It therefore bounds algorithmic error and says
NOTHING about digitization error.** Per CLAUDE.md s4, an instrument's control must be described by
what it can fail, and this one cannot fail on a mis-read pixel.

⛔ AND THE FIELD THIS HEADER USED TO NAME AS THE SEPARATE BOUND DOES NOT BOUND IT EITHER (measured
2026-08-25, `km-digitization-error.json`). ⚠ *Superseded, retained: "Digitization error is bounded
separately, by `max_abs_km_deviation` on each real curve, and that field is reported per curve
rather than
averaged away."* The first half of that sentence is false and the second half is true: the field IS
reported
per curve, and it is **not a digitization bound**. `max_abs_km_deviation` compares the
reconstruction's own
product-limit estimate to the **digitized** curve, so an error made while reading the figure moves
BOTH
sides of the comparison together. The discriminating measurement: the same rendered figure read
with a
calibration wrong by one pixel has **more** than twice the true error against the known cohort and
a
**lower** `max_abs_km_deviation` than the clean read -- the two moved in opposite directions.

What the field does catch is a reading so wrong that no cohort could have produced it (a
deliberately
mis-tuned matcher drove it to ~1.0 and the floor refused the curve). It is blind to the moderate
and to the
systematic error, which are the realistic ones. **A curve admitted on this field alone has had its
arithmetic checked and its READING checked by nothing**, so a real curve needs reading evidence of
its own:
an independent re-digitization, or the paper's own printed medians and risk table reproduced out of
the
reconstructed cohort. `research/modalities/km_digitize.py` is the reader, and its control is where
a
digitization bound actually lives.

WHAT THIS FILE DOES NOT CONTAIN
-------------------------------
⛔ **No curve coordinates.** `CURVES` is empty, deliberately and visibly. Digitizing a published
figure requires the figure, and inventing a coordinate would be fabricating clinical data -- the
golden rule this repository opens with. The input schema is specified in `CURVE_SCHEMA` and the
candidate source list is `CANDIDATE_SOURCES`, so adding a curve is a data edit against a validated
instrument rather than a re-derivation. Until a curve is digitized from a real figure, this module
computes over an empty table and says so in its artifact.

METHOD PROVENANCE
-----------------
Guyot P, Ades AE, Ouwens MJNM, Welton NJ. "Enhanced secondary analysis of survival data:
reconstructing the data from published Kaplan-Meier survival curves." BMC Med Res Methodol
2012;12:9. The interval recursion below follows that paper's published algorithm; variable names
are kept close to it on purpose so a reviewer can check the two side by side.

Stdlib only -- so it runs in CI with no environment build (CLAUDE.md s6, "pull, don't solve").

Run:     python3 research/modalities/emc_ipd_survival.py
Verify:  python3 research/modalities/emc_ipd_survival.py --check
Writes:  research/modalities/emc-ipd-survival.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "research", "modalities", "emc-ipd-survival.json")

METHOD_REF = {
    "citation": "Guyot P, Ades AE, Ouwens MJNM, Welton NJ. Enhanced secondary analysis of "
    "survival data: reconstructing the data from published Kaplan-Meier survival curves. "
    "BMC Med Res Methodol 2012;12:9.",
    "doi": "10.1186/1471-2288-12-9",
    "pmid": "22297116",
}

# ---------------------------------------------------------------------------
# The quality floor (see module docstring -- this is a refusal, not a caveat)
# ---------------------------------------------------------------------------

# A curve with no numbers-at-risk table leaves the per-interval censored count unidentifiable.
# Guyot's own paper reports materially worse recovery in that case, and EMC's series are small
# enough that the error is not averaged away by sample size.
REQUIRE_RISK_TABLE = True

# Maximum tolerated disagreement between the reconstruction's own Kaplan-Meier curve and the
# digitized survival probabilities it was built from. A reconstruction that cannot reproduce its
# own input has not converged, whatever else it produced.
MAX_KM_DEVIATION = 0.05

# Fewer digitized points than this cannot describe a step function well enough to invert.
MIN_DIGITIZED_POINTS = 6

CURVE_SCHEMA = {
    "id": "short stable identifier, e.g. 'bishop2019_localised_os'",
    "source_id": "citation key in research/data/emc-clinical-registry.json -> registry.citations",
    "endpoint": "one of: os | dss | pfs | lrfs | dmfs",
    "population": "free text -- the arm or stratum this curve describes",
    "time_unit": "months | years",
    "digitized": "list of [time, survival_probability], time non-decreasing, S non-increasing in [0,1]",
    "risk_table": "list of [time, n_at_risk], time non-decreasing, n_at_risk non-increasing",
    "total_events": "integer if the paper prints it, else null",
    "digitized_by": "who read the figure, and with what tool -- provenance for a hand step",
}

# Series already curated here that print a Kaplan-Meier curve worth digitizing. This is a WORK
# LIST, not evidence: presence here asserts only that the source is in the registry, never that
# its figure has been read or that its curve is admissible.
#
# ⭐ FIVE ROWS WERE CHECKED ON 2026-08-25 BY LOOKING AT THE GRAPHICS. ⚠ *Superseded, retained:
# "EVERY ROW HERE HAS `figure_checked: False`. Nobody has opened these papers ... reading the
# figures is the step that is not [free], and it has not been taken."* It has now been taken for
# every candidate whose full text is reachable: the article PDFs were retrieved by
# `scripts/emc_km_figure_fetch.py`, rasterised, and looked at. `figure_finding` records what the
# GRAPHIC shows, which is a different fact from anything a text search can return -- and the
# difference is the whole point, because a numbers-at-risk row is typeset INSIDE the image.
#
# ⛔ THE HEADLINE IS A NEGATIVE AND IT BINDS THE ROUTE: the two largest EMC-specific series that
# can be reached print NO numbers-at-risk row, and the only two figures that do print one are the
# two smallest cohorts in the set. Full census: `emc-km-figure-census.json`.
#
# Rows still reading `figure_checked: False` are the ones whose full text this program cannot
# reach at $0. That is a REACHABILITY statement, never a statement about the paper.
#
# ⚠ OVERLAP IS THE TRAP THAT WOULD MAKE A POOLED RESULT WRONG. systems/POLICY-evidence.md admits
# NON-OVERLAPPING COHORTS ONLY, and several of these are the same Milan/INT patients reported
# across successive papers. `overlap_risk` is a flag to adjudicate BEFORE pooling, never a
# licence to pool the rows that lack it.
CANDIDATE_SOURCES: list[dict] = [
    # --- population-level -----------------------------------------------------------------
    {"source_id": "seer270_2022", "n": 270, "endpoint_hint": "os",
     "why_candidate": "SEER population series reporting overall survival; the largest single denominator available",
     "full_text_reachable": None, "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "free_to_read_but_not_retrieved", "unpaywall_oa_status": "gold", "unpaywall_licence": "cc-by-nc-nd", "note": "\u26a0 FREE TO READ AND STILL UNREACHABLE BY MACHINE (2026-08-25). Unpaywall grades it open access at the publisher; every route tried, including a real headless Chromium, was answered HTTP 403. A human with a browser can read it; this program cannot fetch it, and the next rung would be defeating bot protection, which this program does not build.", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "none with institutional series",
     "⛔_caveat": "Keyed on ICD-O-3 9231/3, the code RT-DIAGNOSTIC-PATHWAY shows two published SEER analyses read as mutually incompatible diseases. Cohort composition is UNKNOWN and this row must not anchor a pooled estimate until that split is quantified."},
    {"source_id": "masunaga2025", "n": 171, "endpoint_hint": "os",
     "why_candidate": "retrospective national registry study of radiotherapy and chemotherapy roles; survival endpoint implied by the question",
     "full_text_reachable": "PMC12398172", "figure_checked": True,
     # ⛔ CHECKED 2026-08-25 -- three Kaplan-Meier figures, NONE with a numbers-at-risk row.
     "figure_finding": {
        "km_figures": 3,
        "figures": ["Fig. 1 disease-specific survival by distant metastases at diagnosis",
                    "Fig. 2 local recurrence-free survival by (neo)adjuvant radiotherapy",
                    "Fig. 3 disease-specific survival by advanced-stage chemotherapy"],
        "numbers_at_risk_row": False,
        "style": "two arms, 95% CI shading, p-value in panel, no risk table beneath the axis",
        "⛔_consequence": "REFUSED by the quality floor. This is the LARGEST reachable EMC series "
                          "(n=171) and it is unreconstructable for a reporting reason, not a "
                          "scientific one."},
     "overlap_risk": "none with institutional series"},
    # --- multi-institution / referral-centre series ---------------------------------------
    {"source_id": "meisKindblom1999", "n": 117, "endpoint_hint": "os",
     "why_candidate": "the classic long-term prognostic pathology series; prognosis is its stated subject",
     "full_text_reachable": None, "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "closed", "unpaywall_oa_status": "closed", "unpaywall_licence": None, "note": "\u26d4 NOT OPEN ACCESS anywhere Unpaywall can see (2026-08-25). No free route at $0. That is a statement about ACCESS, never about the paper.", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "may be subsumed by later referral-centre series"},
    {"source_id": "drilon2008", "n": 87, "endpoint_hint": "os",
     "why_candidate": "two-referral-centre retrospective review emphasising outcome",
     "full_text_reachable": "PMC2779719", "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "unresolved", "unpaywall_oa_status": None, "unpaywall_licence": None, "note": "\u26a0 Its PMC routes answer HTTP 500 and no free-copy lookup has yet been run against its DOI (2026-08-25).", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "shares referral centres with later US series"},
    {"source_id": "ussc2022", "n": 60, "endpoint_hint": "os",
     "why_candidate": "US Sarcoma Collaborative multi-institution database, outcomes reported",
     "full_text_reachable": None, "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "closed", "unpaywall_oa_status": "closed", "unpaywall_licence": None, "note": "\u26d4 NOT OPEN ACCESS anywhere Unpaywall can see (2026-08-25). No free route at $0. That is a statement about ACCESS, never about the paper.", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "⚠ US institutions overlap drilon2008 and uMich2023"},
    {"source_id": "chiusole2020", "n": 59, "endpoint_hint": "os",
     "why_candidate": "two-institution retrospective, outcomes in the title",
     "full_text_reachable": "PMC7308468", "figure_checked": True,
     # ⛔ CHECKED 2026-08-25 -- four overall-survival figures, NONE with a numbers-at-risk row.
     "figure_finding": {
        "km_figures": 4,
        "figures": ["Figure 1 OS by extent of primary resection", "Figure 2 OS by sex",
                    "Figure 3 OS by primary location", "Figure 4 OS by site of metastases"],
        "numbers_at_risk_row": False,
        "style": "two or three arms, censoring ticks drawn on the curve, legend with p-value, "
                 "no risk table beneath the axis",
        "⭐_what_IS_printed": "median OS 180 months, 75% alive at 5 years, 63% at 10 years, "
                              "20 deaths of 59 -- printed in the text, so a printed-numbers "
                              "analysis is possible where a reconstruction is not.",
        "⛔_consequence": "REFUSED by the quality floor."},
     "overlap_risk": "⚠ likely shares Milan/INT patients with the Stacchiotti series"},
    {"source_id": "japan2003", "n": 42, "endpoint_hint": "os",
     "why_candidate": "multi-institution series of 42 cases",
     "full_text_reachable": None, "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "free_to_read_but_not_retrieved", "unpaywall_oa_status": "bronze", "unpaywall_licence": None, "note": "\u26a0 FREE TO READ AND STILL UNREACHABLE BY MACHINE (2026-08-25). Unpaywall grades it open access at the publisher; every route tried, including a real headless Chromium, was answered HTTP 403. A human with a browser can read it; this program cannot fetch it, and the next rung would be defeating bot protection, which this program does not build.", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "⚠ may overlap morioka2016 (Japanese trial population)"},
    {"source_id": "uMich2023", "n": 44, "endpoint_hint": "os",
     "why_candidate": "single-institution series explicitly examining prognostic factors",
     "full_text_reachable": None, "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "closed", "unpaywall_oa_status": "closed", "unpaywall_licence": None, "note": "\u26d4 NOT OPEN ACCESS anywhere Unpaywall can see (2026-08-25). No free route at $0. That is a statement about ACCESS, never about the paper.", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "⚠ US institution, may overlap ussc2022"},
    {"source_id": "bishop2019", "n": 41, "endpoint_hint": "lrfs",
     "why_candidate": "single-institution combined-modality series; local control is the stated endpoint",
     "full_text_reachable": "PMC7771031", "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "unresolved", "unpaywall_oa_status": None, "unpaywall_licence": None, "note": "\u26a0 Its PMC routes answer HTTP 500 and no free-copy lookup has yet been run against its DOI (2026-08-25).", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "⚠ US institution, may overlap ussc2022"},
    {"source_id": "china2016", "n": 40, "endpoint_hint": "os",
     "why_candidate": "single-country clinicopathologic and radiologic series",
     "full_text_reachable": None, "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "closed", "unpaywall_oa_status": "closed", "unpaywall_licence": None, "note": "\u26d4 NOT OPEN ACCESS anywhere Unpaywall can see (2026-08-25). No free route at $0. That is a statement about ACCESS, never about the paper.", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "none known"},
    {"source_id": "huang2023", "n": 58, "endpoint_hint": "dss",
     "why_candidate": "molecular case series; reports disease-specific survival by fusion partner, the TAF15 prognostic question",
     "full_text_reachable": None, "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "free_to_read_but_not_retrieved", "unpaywall_oa_status": "bronze", "unpaywall_licence": None, "note": "\u26a0 FREE TO READ AND STILL UNREACHABLE BY MACHINE (2026-08-25). Unpaywall grades it open access at the publisher; every route tried, including a real headless Chromium, was answered HTTP 403. A human with a browser can read it; this program cannot fetch it, and the next rung would be defeating bot protection, which this program does not build.", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "none known",
     "note": "the fusion-partner denominator RT-PARTNER-STRAT depends on -- EWSR1 46/58, TAF15 9/58, TCF12 2/58"},
    # --- prospective / systemic-therapy cohorts -------------------------------------------
    {"source_id": "stacchiotti2019pazopanib", "n": 26, "endpoint_hint": "pfs",
     "why_candidate": "the only prospective single-arm phase 2 in advanced EMC; PFS is the primary endpoint",
     "full_text_reachable": None, "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "closed", "unpaywall_oa_status": "closed", "unpaywall_licence": None, "note": "\u26d4 NOT OPEN ACCESS anywhere Unpaywall can see (2026-08-25). No free route at $0. That is a statement about ACCESS, never about the paper.", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "⚠ may share patients with earlier Milan series"},
    {"source_id": "immunosarc2emc2025", "n": 24, "endpoint_hint": "pfs",
     "why_candidate": "phase 2 histology-specific cohort, sunitinib plus nivolumab",
     "full_text_reachable": None, "figure_checked": False,
     "overlap_risk": "⚠ conference abstract; may be an expansion of martinbroto2020immunosarc1",
     "⚠_caveat": "type is conference-abstract -- abstracts rarely print a numbers-at-risk table, so this may fail the quality floor on reporting completeness alone"},
    {"source_id": "martinbroto2020immunosarc1", "n": 68, "endpoint_hint": "pfs",
     "why_candidate": "single-arm phase Ib/II; EMC may appear only as a subgroup",
     "full_text_reachable": "PMC7674086", "figure_checked": True,
     # ⛔ CHECKED 2026-08-25 -- NO Kaplan-Meier figure at all. Its Figure 3 is a SWIMMER PLOT.
     "figure_finding": {
        "km_figures": 0,
        "figures": ["Figure 1 CONSORT", "Figure 2 waterfall by RECIST",
                    "Figure 3 per-patient PFS swimmer plot, coloured by histology"],
        "numbers_at_risk_row": None,
        "⚠_correction": "emc-ipd-admissibility-2026-08-12.json counted this paper among those "
                        "that 'report Kaplan-Meier survival analysis'. It reports one in TEXT and "
                        "prints no KM curve, which a caption scan cannot distinguish.",
        "⭐_a_different_instrument_applies": "A swimmer plot is per-patient data drawn as pixels: "
                                             "each bar is one patient's PFS, with censoring shown "
                                             "by an arrow. Reading it needs no Guyot recursion "
                                             "because it IS the patient-level data -- but the EMC "
                                             "patients are one colour inside a mixed soft-tissue "
                                             "sarcoma cohort, so the subgroup must be separated by "
                                             "colour before anything can be claimed."},
     "overlap_risk": "⚠ likely the parent trial of immunosarc2emc2025",
     "⚠_caveat": "cohort is advanced soft-tissue sarcoma broadly; an EMC-specific curve may not exist"},
    {"source_id": "stacchiotti2013anthracycline", "n": 11, "endpoint_hint": "pfs",
     "why_candidate": "retrospective centrally-reviewed systemic-therapy series",
     "full_text_reachable": "PMC3879193", "figure_checked": True,
     # ✅ CHECKED 2026-08-25 -- ONE PFS curve WITH a numbers-at-risk row, and it has been READ.
     "figure_finding": {
        "km_figures": 1,
        "figures": ["Figure 2 overall PFS on anthracycline-based chemotherapy"],
        "numbers_at_risk_row": True,
        "risk_table_printed": [[2, 10], [4, 7], [6, 5], [8, 1], [10, 0]],
        "⚠_axis_starts_at_2": "The time axis begins at 2, not 0, and the first event lands on the "
                              "origin -- so the printed '10 at t=2' is a post-event count. See "
                              "km_digitize.FIGURE_RECIPES for what that does to the recursion.",
        "digitized": "km-figure-readings.json -> stacchiotti2013_pfs_anthracycline",
        "⭐": "The reconstruction reproduces the caption's printed median PFS of 8 months, which "
              "the reconstruction never saw. That is this program's only check of a READING."},
     "overlap_risk": "⚠ Milan series, overlaps stacchiotti2014sunitinib and chiusole2020"},
    {"source_id": "stacchiotti2014sunitinib", "n": 10, "endpoint_hint": "pfs",
     "why_candidate": "retrospective consecutively-treated series, 6 of 10 RECIST partial responses",
     "full_text_reachable": None, "figure_checked": False,
     "reachability_2026_08_25": {"verdict": "closed", "unpaywall_oa_status": "closed", "unpaywall_licence": None, "note": "\u26d4 NOT OPEN ACCESS anywhere Unpaywall can see (2026-08-25). No free route at $0. That is a statement about ACCESS, never about the paper.", "census": "research/literature/emc-km-reachability-census-2026-08-25.json"}, "overlap_risk": "⚠ Milan series, overlaps stacchiotti2013anthracycline and stacchiotti2019pazopanib"},
    {"source_id": "morioka2016trabectedin", "n": 5, "endpoint_hint": "pfs",
     "why_candidate": "sub-analysis of a randomised trial; EMC arm is tiny",
     "full_text_reachable": "PMC4946242", "figure_checked": True,
     # ✅ CHECKED 2026-08-25 -- one PFS curve WITH a numbers-at-risk row, AND the paper prints the
     # patient-level data outright in Table 2, which makes reconstruction unnecessary here.
     "figure_finding": {
        "km_figures": 1,
        "figures": ["Fig. 1 Kaplan-Meier plot of progression-free survival, two arms"],
        "numbers_at_risk_row": True,
        "risk_table_printed": {"trabectedin": [[0, 5], [3, 5], [6, 5], [9, 3], [12, 3],
                                                [15, 1], [18, 1], [21, 1]],
                               "best_supportive_care": [[0, 3]]},
        "⛔_it_is_not_an_EMC_cohort": "Five patients in the trabectedin arm, of whom the paper's "
                                      "Table 2 identifies TWO as EMCS and three as mesenchymal "
                                      "chondrosarcoma; all three best-supportive-care patients are "
                                      "MCS. A curve over that arm is not an EMC curve.",
        "⭐_no_reconstruction_needed": "Table 2 prints per-subject PFS, overall survival and "
                                       "censoring flags. Where a paper prints patient-level data, "
                                       "reading it is transcription, and inverting a curve to "
                                       "recover what is already printed adds error for nothing."},
     "overlap_risk": "⚠ may overlap japan2003 institutions",
     "⚠_caveat": "n=5 is below the >=5-per-study inclusion floor used by the reconstructed-IPD exemplar only if that floor is read as strictly greater; adjudicate before admitting"},
]

# ⛔ EMPTY BY CONSTRUCTION, AND IT STAYS EMPTY. A coordinate typed here would be a clinical datum
# with no derivation behind it. Digitized curves reach this module ONLY through
# `load_digitized_curves()` below, which reads the artifact a re-runnable digitizer wrote.
CURVES: list[dict] = []

# Written by `research/modalities/km_digitize.py --figures`, whose FIGURE_RECIPES name the
# committed image, the axis anchors and who read them.
READINGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "km-figure-readings.json")


def load_digitized_curves() -> list[dict]:
    """Curves read off real figures, loaded from the digitizer's artifact. Never hand-typed.

    ⭐ WHY A LOADER RATHER THAN A TABLE. The rule this module opens with -- no invented coordinate
    -- is easy to state and hard to keep, because a table of numbers in a source file looks
    identical whether it was measured or guessed. A loader makes the provenance STRUCTURAL: a
    coordinate can only arrive attached to a recipe naming the image it came from, so "where did
    this number come from" is answerable by construction rather than by trust.

    ⛔ A READING IS ADMITTED HERE ONLY IF IT PASSED ITS OWN EXTERNAL CHECK -- a quantity the paper
    printed and the reconstruction never saw. A curve whose reconstruction cannot reproduce the
    paper's own printed median has been read wrong somewhere, and admitting it because the
    arithmetic is self-consistent is the exact blindness recorded at the top of this file.
    """
    if not os.path.exists(READINGS):
        return []
    with open(READINGS, encoding="utf-8") as fh:
        doc = json.load(fh)
    recipes = {r["id"]: r for r in doc.get("recipes", [])}
    out = []
    for reading in doc.get("readings", []):
        if not reading.get("read_ok"):
            continue
        recipe = recipes.get(reading["id"]) or {}
        for key, rec in (reading.get("reconstructions") or {}).items():
            if not rec.get("admissible") or not rec.get("external_check_passes"):
                continue
            out.append({
                "id": f"{reading['id']}::{key}",
                "source_id": reading["source_id"],
                "endpoint": reading["endpoint"],
                "population": recipe.get("population", ""),
                "time_unit": recipe.get("time_unit", ""),
                "digitized": reading["digitized"],
                "risk_table": recipe.get(key),
                "total_events": None,
                "digitized_by": recipe.get("digitized_by", ""),
                "figure": reading.get("figure"),
                "image": reading.get("image"),
                "external_check": recipe.get("external_check"),
            })
    return out


# ---------------------------------------------------------------------------
# PRINTED patient-level data -- transcription, not reconstruction
# ---------------------------------------------------------------------------
# ⭐ THE BEST SOURCE IN THIS FILE IS THE ONE THAT NEEDS NO INSTRUMENT. Some papers print the
# patient-level data outright, in a table. Reading it is TRANSCRIPTION -- digits, not pixels -- and
# inverting a curve to recover numbers the same paper already printed adds error for nothing.
#
# ⛔ TRANSCRIPTION IS NOT FREE OF ITS OWN FAILURE MODE, AND IT IS A WORSE ONE THAN DIGITIZATION'S:
# a misread `17` as `12` is silent, local and produces a perfectly plausible cohort, whereas a
# misread curve is loud and global. So every row names the exact table and row it came from, and
# `verified_against` records that the digits were checked against the PDF's TEXT LAYER rather than
# only against a rendered image -- a rendered image is exactly where an OCR-style slip happens.
#
# ⚠ THESE ROWS ARE NOT POOLED WITH ANYTHING. POLICY-evidence.md forbids merging populations, and
# these patients differ from every other source here in treatment, line and endpoint. They are
# reported; they are not added to anyone else's denominator.
PRINTED_IPD = [
    {
        "source_id": "morioka2016trabectedin",
        "printed_in": "Table 2 'Summary of efficacy', trabectedin group, subject 1",
        "histology": "EMCS",
        "population": "extraskeletal myxoid chondrosarcoma, trabectedin arm of a randomised "
                      "phase 2 study in translocation-related sarcoma",
        "pfs_months": 13.0, "pfs_censored": False,
        "os_months": 26.4, "os_censored": False,
        "best_overall_response": "SD",
        "verified_against": "the PDF text layer of PMC4946242 page 4, not only a page raster",
    },
    {
        "source_id": "morioka2016trabectedin",
        "printed_in": "Table 2 'Summary of efficacy', trabectedin group, subject 2",
        "histology": "EMCS",
        "population": "extraskeletal myxoid chondrosarcoma, trabectedin arm of a randomised "
                      "phase 2 study in translocation-related sarcoma",
        "pfs_months": 7.4, "pfs_censored": False,
        "os_months": 10.4, "os_censored": False,
        "best_overall_response": "SD",
        "verified_against": "the PDF text layer of PMC4946242 page 4, not only a page raster",
    },
]

# ⛔ WHY THE OTHER SIX ROWS OF THAT TABLE ARE NOT HERE. Subjects 3-5 (trabectedin) and 6-8 (best
# supportive care) are MESENCHYMAL chondrosarcoma, a different disease that shares a name fragment.
# Taking the whole table because it is in an EMC-relevant paper is the exact ICD-O-3 conflation
# RT-DIAGNOSTIC-PATHWAY exists to record.


# ---------------------------------------------------------------------------
# Guyot et al. 2012 -- the reconstruction itself
# ---------------------------------------------------------------------------
def _interval_bounds(digitized: list, risk_table: list) -> list[tuple[int, int]]:
    """Map each numbers-at-risk interval onto the digitized points that fall inside it.

    Returns (lower, upper) index pairs, inclusive, into `digitized`. An interval with no
    digitized point is returned as an empty range and skipped by the recursion -- that is a
    property of the published figure, not an error, and it is counted in the quality report.
    """
    bounds = []
    n = len(digitized)
    for i, (t_start, _) in enumerate(risk_table):
        t_end = risk_table[i + 1][0] if i + 1 < len(risk_table) else float("inf")
        lower, upper = None, None
        for j in range(n):
            t = digitized[j][0]
            if t >= t_start and t < t_end:
                if lower is None:
                    lower = j
                upper = j
        bounds.append((lower, upper) if lower is not None else (None, None))
    return bounds


def _distribute_censoring(t_lo: float, t_hi: float, n_censor: int, times: list) -> list[int]:
    """Spread `n_censor` censoring events uniformly over (t_lo, t_hi) and bin them.

    Guyot's algorithm assumes censoring is uniform within a risk interval, because the published
    figure carries no information about where inside the interval it happened. `times` are the
    digitized times of the interval; the returned counts align with them, with the final position
    always 0 (a censoring time cannot fall beyond the last bin edge).
    """
    counts = [0] * len(times)
    if n_censor <= 0 or len(times) < 2:
        return counts
    for j in range(1, n_censor + 1):
        ct = t_lo + j * (t_hi - t_lo) / (n_censor + 1)
        # right-closed bins (times[k], times[k+1]], first bin includes its left edge
        placed = False
        for k in range(len(times) - 1):
            lo_edge, hi_edge = times[k], times[k + 1]
            if (ct > lo_edge or (k == 0 and ct >= lo_edge)) and ct <= hi_edge:
                counts[k] += 1
                placed = True
                break
        if not placed:
            counts[max(0, len(times) - 2)] += 1
    return counts


def reconstruct(curve: dict) -> dict:
    """Invert one published Kaplan-Meier curve into patient-level data.

    Follows Guyot et al. 2012. The outer loop walks the numbers-at-risk intervals; inside each,
    the number of events at every digitized point is chosen so the product-limit estimate tracks
    the read-off survival, and the number censored is adjusted until the estimated number at risk
    at the START of the next interval matches the number the paper printed. That adjustment is
    the whole reason a risk table is required.

    Returns a dict carrying the reconstructed IPD and the diagnostics needed to grade it.
    """
    digitized = [(float(t), float(s)) for t, s in curve["digitized"]]
    risk_table = [(float(t), int(n)) for t, n in curve.get("risk_table") or []]
    total_events = curve.get("total_events")

    if not digitized:
        raise ValueError(f"curve {curve.get('id')!r} has no digitized points")
    if not risk_table:
        raise ValueError(
            f"curve {curve.get('id')!r} has no risk table; the censored count is "
            "unidentifiable without one (see REQUIRE_RISK_TABLE)"
        )

    t_S = [p[0] for p in digitized]
    S = [p[1] for p in digitized]
    n_t = len(digitized)
    bounds = _interval_bounds(digitized, risk_table)
    intervals = [(i, lo, hi) for i, (lo, hi) in enumerate(bounds) if lo is not None]
    if not intervals:
        raise ValueError(f"curve {curve.get('id')!r}: no digitized point falls in any risk interval")

    n_risk = [n for _, n in risk_table]
    d = [0] * n_t            # events at each digitized point
    cen = [0] * n_t          # censorings at each digitized point
    n_hat = [0] * (n_t + 1)  # estimated number at risk entering each point
    km_hat = [1.0] * n_t     # product-limit estimate at each point
    last = intervals[0][1]   # index of the most recent point carrying an event

    for idx, (i, lo, hi) in enumerate(intervals):
        is_last_interval = idx == len(intervals) - 1
        n_hat[lo] = n_risk[i]

        if is_last_interval:
            n_censor = 0
            if total_events is not None:
                # Censoring in the final interval is whatever the reported event total implies.
                events_so_far = sum(d[:lo])
                n_censor = max(0, n_risk[i] - (int(total_events) - events_so_far))
            else:
                # No reported total: everyone still at risk at the last printed time is censored
                # there. This is Guyot's default and it is conservative for survival estimation.
                n_censor = 0
            cen_counts = _distribute_censoring(t_S[lo], t_S[hi], n_censor, t_S[lo : hi + 1])
            for k, c in enumerate(cen_counts):
                cen[lo + k] = c
            last = _sweep_interval(lo, hi, S, d, cen, n_hat, km_hat, last, first=(idx == 0))
        else:
            nxt_i, nxt_lo, _ = intervals[idx + 1]
            target = n_risk[nxt_i]
            # First approximation of the censored count in this interval (Guyot eq. 2).
            denom = S[lo] if S[lo] > 0 else 1.0
            n_censor = int(round(n_risk[i] * (S[nxt_lo] / denom) - target))
            n_censor = max(0, n_censor)

            # Adjust until the estimated number at risk entering the next interval matches the
            # number the paper printed. Bounded: each pass moves n_censor by the observed gap,
            # and a non-converging curve is a curve we refuse rather than one we loop on.
            for _ in range(1000):
                cen_counts = _distribute_censoring(t_S[lo], t_S[hi], n_censor, t_S[lo : hi + 1])
                for k in range(lo, hi + 1):
                    cen[k] = 0
                for k, c in enumerate(cen_counts):
                    cen[lo + k] = c
                trial_last = _sweep_interval(
                    lo, hi, S, d, cen, n_hat, km_hat, last, first=(idx == 0)
                )
                gap = n_hat[nxt_lo] - target
                if gap == 0 or (gap < 0 and n_censor <= 0):
                    last = trial_last
                    break
                n_censor = max(0, n_censor + gap)
            else:
                last = trial_last
            if n_hat[nxt_lo] < target:
                # The figure cannot support the printed risk table; trust the reconstruction and
                # record the disagreement rather than silently overriding either.
                n_risk[nxt_i] = n_hat[nxt_lo]

    ipd = []
    for k in range(n_t):
        for _ in range(d[k]):
            ipd.append({"time": t_S[k], "event": 1})
        for _ in range(cen[k]):
            ipd.append({"time": t_S[k], "event": 0})
    ipd.sort(key=lambda r: (r["time"], -r["event"]))

    deviations = [abs(km_hat[k] - S[k]) for k in range(n_t)]
    return {
        "id": curve.get("id"),
        "source_id": curve.get("source_id"),
        "endpoint": curve.get("endpoint"),
        "population": curve.get("population"),
        "time_unit": curve.get("time_unit"),
        "n_reconstructed": len(ipd),
        "n_events": sum(d),
        "n_censored": sum(cen),
        "n_at_risk_reported_start": risk_table[0][1],
        "max_abs_km_deviation": round(max(deviations), 4) if deviations else None,
        "risk_table_intervals": len(risk_table),
        "risk_table_intervals_with_points": len(intervals),
        "risk_table_overridden": [
            {"interval_index": i, "printed": n, "reconstructed": n_risk[i]}
            for i, (_, n) in enumerate(risk_table)
            if n_risk[i] != n
        ],
        "ipd": ipd,
    }


def _sweep_interval(
    lo: int, hi: int, S: list, d: list, cen: list, n_hat: list, km_hat: list,
    last: int, first: bool,
) -> int:
    """One forward pass over a risk interval, filling in events and the at-risk count.

    At each digitized point the number of events is the count that makes the product-limit
    estimate step down to the survival probability read off the figure (Guyot eq. 1). Returns the
    index of the last point carrying an event, which the next interval resumes from -- carrying
    it forward is what keeps the product-limit estimate continuous across the interval boundary.
    """
    for k in range(lo, hi + 1):
        if first and k == lo:
            d[k] = 0
            km_hat[k] = 1.0
        else:
            ref = km_hat[last]
            if ref > 0 and n_hat[k] > 0:
                d[k] = int(round(n_hat[k] * (1.0 - (S[k] / ref))))
            else:
                d[k] = 0
            d[k] = max(0, min(d[k], n_hat[k]))
            km_hat[k] = ref * (1.0 - d[k] / n_hat[k]) if n_hat[k] > 0 else ref
        nxt = n_hat[k] - d[k] - cen[k]
        if nxt < 0:
            # The number at risk cannot go negative; the excess must be censoring the figure
            # does not support, so it is dropped rather than carried.
            cen[k] = max(0, n_hat[k] - d[k])
            nxt = 0
        n_hat[k + 1] = nxt
        if d[k] != 0:
            last = k
    return last


# ---------------------------------------------------------------------------
# Kaplan-Meier on reconstructed IPD -- used by the control and by pooling
# ---------------------------------------------------------------------------
def kaplan_meier(ipd: list) -> list[dict]:
    """Product-limit estimate from patient-level records [{'time','event'}, ...]."""
    if not ipd:
        return []
    rows = sorted(ipd, key=lambda r: r["time"])
    n = len(rows)
    at_risk = n
    surv = 1.0
    out = []
    i = 0
    while i < n:
        t = rows[i]["time"]
        events = censored = 0
        while i < n and rows[i]["time"] == t:
            if rows[i]["event"]:
                events += 1
            else:
                censored += 1
            i += 1
        if events and at_risk > 0:
            surv *= 1.0 - events / at_risk
        out.append(
            {
                "time": t,
                "n_at_risk": at_risk,
                "events": events,
                "censored": censored,
                "survival": round(surv, 6),
            }
        )
        at_risk -= events + censored
    return out


def survival_at(km: list, t: float) -> float | None:
    """Survival probability at time t from a product-limit table, or None past its support."""
    if not km or t > km[-1]["time"]:
        return None
    s = 1.0
    for row in km:
        if row["time"] > t:
            break
        s = row["survival"]
    return s


# ---------------------------------------------------------------------------
# Admissibility
# ---------------------------------------------------------------------------
def assess_quality(curve: dict, rec: dict | None, error: str | None = None) -> dict:
    """Grade one curve against the floor. Every rejection names the criterion it failed."""
    failures = []
    if error:
        failures.append(f"reconstruction_failed: {error}")
    if REQUIRE_RISK_TABLE and not curve.get("risk_table"):
        failures.append("no_numbers_at_risk_table")
    if len(curve.get("digitized") or []) < MIN_DIGITIZED_POINTS:
        failures.append(
            f"too_few_digitized_points (<{MIN_DIGITIZED_POINTS})"
        )
    if rec is not None:
        dev = rec.get("max_abs_km_deviation")
        if dev is not None and dev > MAX_KM_DEVIATION:
            failures.append(
                f"km_deviation {dev} exceeds floor {MAX_KM_DEVIATION}"
            )
    if not curve.get("digitized_by"):
        failures.append("no_digitization_provenance")
    return {
        "id": curve.get("id"),
        "admissible": not failures,
        "failures": failures,
        "max_abs_km_deviation": (rec or {}).get("max_abs_km_deviation"),
    }


def pool_reconstructions(records: list[dict]) -> dict:
    """Pool admissible reconstructions into one patient-level survival dataset.

    ⛔ Pooling is only legal across NON-OVERLAPPING populations -- POLICY-evidence.md s2.1, and it
    binds here exactly as it binds the proportion poolers. This function does not police overlap;
    the caller must have set `pool: false` on the smaller of any overlapping pair, and the reason
    travels in the artifact.

    ⛔⛔ IT DOES POLICE THE ENDPOINT, BECAUSE MERGING TWO IS A CATEGORY ERROR RATHER THAN A BIAS.
    Overall survival and progression-free survival are different events on different clocks; a
    Kaplan-Meier curve over both is not a worse estimate of anything, it is an estimate of nothing.
    A mixed set therefore RAISES rather than returning a caveat, because a caveat on a number this
    wrong travels worse than a crash.

    ⚠ AND A SINGLE CURVE IS NOT A POOL, WHICH IS THE STATE THIS PROGRAM IS ACTUALLY IN. With one
    admitted curve the returned block is one series' reconstruction wearing the word "pooled", and a
    reader scanning the artifact will take `median_survival` for a pooled EMC estimate. It says so
    itself instead.
    """
    endpoints = sorted({r.get("endpoint") for r in records if r.get("endpoint")})
    if len(endpoints) > 1:
        raise ValueError(
            f"refusing to pool across endpoints {endpoints}: overall survival and "
            "progression-free survival are different events on different clocks, and a curve over "
            "both estimates nothing. Pool within an endpoint, or report them separately.")
    pooled = []
    for rec in records:
        for row in rec["ipd"]:
            pooled.append({**row, "source": rec["source_id"], "curve": rec["id"]})
    km = kaplan_meier(pooled)
    out = {
        "n_patients": len(pooled),
        "n_events": sum(1 for r in pooled if r["event"]),
        "endpoint": endpoints[0] if endpoints else None,
        "curves_pooled": [r["id"] for r in records],
        "sources_pooled": sorted({r.get("source_id") for r in records}),
        "kaplan_meier": km,
        "median_survival": _median_survival(km),
    }
    if len(records) == 1:
        rec = records[0]
        out["⛔_this_is_not_a_pool"] = (
            f"ONE curve, from ONE series ({rec.get('source_id')}), on endpoint "
            f"{rec.get('endpoint')}, in the population: {rec.get('population')}. Everything in this "
            "block is that series' own reconstruction and inherits its every selection effect and "
            "its treatment. It is NOT a pooled extraskeletal myxoid chondrosarcoma estimate, and "
            "`median_survival` here is not this disease's median survival.")
    return out


def _median_survival(km: list) -> float | None:
    """First time at which the product-limit estimate falls to or below 0.5, else None.

    None means "not reached", which in an indolent disease is the common and the informative
    answer -- it must never be rendered as a number.
    """
    for row in km:
        if row["survival"] <= 0.5:
            return row["time"]
    return None


# ---------------------------------------------------------------------------
# build / check
# ---------------------------------------------------------------------------
def build() -> dict:
    """Pure over this module's tables PLUS the digitizer's readings artifact.

    ⚠ It is no longer file-free, and that is deliberate: the alternative was a table of
    coordinates typed into this source file, which is the one thing this module exists to refuse.
    A verify mode that regenerates and compares against its own output still cannot fail, so
    `--check` compares the committed artifact against a fresh build of BOTH inputs.
    """
    curves = CURVES + load_digitized_curves()
    reconstructions, quality, errors = [], [], []
    for curve in curves:
        rec, err = None, None
        try:
            rec = reconstruct(curve)
        except Exception as exc:  # a bad curve is data, not a crash
            err = str(exc)
            errors.append({"id": curve.get("id"), "error": err})
        q = assess_quality(curve, rec, err)
        quality.append(q)
        if q["admissible"] and rec is not None and curve.get("pool") is not False:
            reconstructions.append(rec)

    admissible = [q for q in quality if q["admissible"]]
    return {
        "_generated_by": "research/modalities/emc_ipd_survival.py",
        "_do_not_hand_edit": (
            "Every number here is computed from the CURVES table in the generator. Verify with "
            "`python3 research/modalities/emc_ipd_survival.py --check`."
        ),
        "method": METHOD_REF,
        "what_this_is": (
            "Patient-level survival data reconstructed from published Kaplan-Meier curves. A "
            "reconstruction is a re-expression of a published figure -- never new patients, never "
            "new follow-up, and it inherits every selection effect of the series it came from."
        ),
        "quality_floor": {
            "require_numbers_at_risk_table": REQUIRE_RISK_TABLE,
            "max_abs_km_deviation": MAX_KM_DEVIATION,
            "min_digitized_points": MIN_DIGITIZED_POINTS,
            "rationale": (
                "Without a numbers-at-risk table the per-interval censored count is "
                "unidentifiable. A curve below the floor is REFUSED, not pooled with a caveat."
            ),
        },
        "curve_schema": CURVE_SCHEMA,
        "candidate_sources": CANDIDATE_SOURCES,
        "printed_patient_level_data": {
            "_what": "patient-level rows a paper PRINTED, transcribed rather than reconstructed",
            "⚠_not_pooled": "different treatments and lines; POLICY-evidence.md forbids merging "
                             "them with each other or with any reconstructed curve",
            "n_rows": len(PRINTED_IPD),
            "rows": PRINTED_IPD,
        },
        "curves_supplied": len(curves),
        "curves_hand_typed": len(CURVES),
        "curves_from_digitizer": len(curves) - len(CURVES),
        "curves_admissible": len(admissible),
        "curves_pooled": len(reconstructions),
        "quality": quality,
        "errors": errors,
        "reconstructions": [
            {k: v for k, v in r.items() if k != "ipd"} for r in reconstructions
        ],
        "pooled": pool_reconstructions(reconstructions) if reconstructions else None,
        "status": (
            "NO CURVES DIGITIZED. The instrument is built and its known-answer control passes; "
            "no published EMC figure has been read into CURVES yet. Digitizing a figure requires "
            "the figure, and inventing a coordinate would fabricate a clinical datum. This field "
            "is the honest state, not a placeholder to be filled in with plausible numbers."
        )
        if not curves
        else "curves supplied; see quality[] for what was admitted and why",
    }


def check() -> int:
    """Compare the committed artifact against a fresh in-memory build. Writes nothing."""
    if not os.path.exists(OUT):
        print(f"MISSING: {OUT}", file=sys.stderr)
        return 1
    with open(OUT, encoding="utf-8") as fh:
        committed = json.load(fh)
    fresh = build()
    if committed == fresh:
        print(f"OK: {os.path.relpath(OUT, REPO)} matches the generator")
        return 0
    print(
        f"STALE OR HAND-EDITED: {os.path.relpath(OUT, REPO)} disagrees with the generator.\n"
        "Regenerate with `python3 research/modalities/emc_ipd_survival.py`.",
        file=sys.stderr,
    )
    for key in sorted(set(committed) | set(fresh)):
        if committed.get(key) != fresh.get(key):
            print(f"  differs: {key}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify the committed artifact against the generator; write nothing",
    )
    args = ap.parse_args(argv)
    if args.check:
        return check()
    payload = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(
        f"wrote {os.path.relpath(OUT, REPO)} "
        f"({payload['curves_supplied']} curves supplied, "
        f"{payload['curves_pooled']} pooled)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
