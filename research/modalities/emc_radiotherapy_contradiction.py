"""The EMC radiotherapy "contradiction", re-examined against both primary sources.

WHY THIS EXISTS
---------------
`systems/graph/routes.json` -> RT-RT-INTENSIFY is built on a stated contradiction: *"This
repository's own record contains a live contradiction about whether radiotherapy does anything in
this disease -- two registries and the largest series disagree."* Its grade adds that no dose or
modality data is curated anywhere, and its readiness lists as missing *"per-patient dose and
modality data, which none of the curated series publishes"* and *"a particle-registry search by
histology"*.

Both halves turned out to be wrong, and the second one changes the route's premise.

⭐⭐ THE TWO SERIES DO NOT CONTRADICT EACH OTHER. THEIR CONFIDENCE INTERVALS OVERLAP.
Bishop 2019 (n = 41, MD Anderson) reports surgery ALONE as the only factor significant for poorer
local control on multivariable analysis: HR 12.7 (95 % CI 1.4-115.3), p = 0.02, with 10-year local
control 63 % against 100 % for combined-modality therapy. Masunaga 2025 (n = 134, Japanese national
registry) reports (neo)adjuvant radiotherapy against local recurrence at HR 0.50 (95 % CI
0.11-2.25), p = 0.365, and its abstract says "no association was found".

Those are near-inverse contrasts, so put them on one scale. Bishop's surgery-alone hazard of 12.7
inverts to a radiotherapy hazard of about 0.079 (0.0087-0.71). Masunaga's is 0.50 (0.11-2.25).
**The intervals overlap across 0.11-0.71.** Both point estimates are protective. What differs is
which side of p = 0.05 each landed on -- and Bishop's own interval spans two orders of magnitude on
five local relapses, so it is not the well-powered study either. **The contradiction is
manufactured by dichotomising p-values across two small underpowered studies whose estimates
agree in direction.**

⚠ AND THE CONFOUNDING RUNS IN OPPOSITE DIRECTIONS, WHICH MAKES THE AGREEMENT MORE STRIKING, NOT
LESS. Masunaga states that radiotherapy "is administered to prevent local recurrence in patients
with close surgical margins", and 41.7 % of its irradiated patients had R1/R2 margins against
18.2 % of the unirradiated -- so its treated arm was at HIGHER baseline risk of the very event
being measured, and 0.50 UNDERSTATES whatever protection exists. Bishop's confounding is not
characterised in what its text states about how its 8 surgery-alone patients were selected, so its
direction is unknown rather than absent.

⛔ THIS IS NOT A CLAIM THAT RADIOTHERAPY WORKS. Two retrospective series with overlapping intervals
and opposite selection pressures do not establish an effect; they fail to establish a
disagreement. The honest statement is that the reachable evidence is UNDERPOWERED and CONSISTENT,
not that it is positive. No efficacy, no safety, no clinical readiness is asserted anywhere here,
and nothing here is medical advice.

⛔ THE ROUTE'S "NO CURATED DOSE OR MODALITY DATA" IS FALSE. Bishop publishes treatment approach
(preoperative 23, postoperative 10, surgery alone 8) and radiation dose (median 50 Gy, range
50-65). Masunaga publishes modality and fractionation (neoadjuvant 40-50 Gy in 2 Gy fractions in
4 patients; adjuvant 50-66 Gy in 2 Gy fractions in 20). Neither is PER-PATIENT, which is what a
dose-response regression would need -- so the route's regression is still unbuildable, but for a
narrower reason than "nobody publishes dose".

⭐ THE PARTICLE SEARCH, RUN AND ANSWERED. Brachytherapy and proton arms DO exist in this histology
and carbon ion does not appear in it at all -- but every one of them is a single case report, not a
registry arm. That is the honest answer to a question the route had never asked of the literature.

⛔ PROVENANCE IS SEPARATED THROUGHOUT, because half of what is known here came through a review.
Every record carries `provenance: "primary"` or `"secondary"`. POLICY-evidence 1.3 forbids
laundering a citation, so a figure this program has only read in someone else's summary says so,
and a test fails if a secondary record loses that label.

Run:     python3 research/modalities/emc_radiotherapy_contradiction.py
Verify:  python3 research/modalities/emc_radiotherapy_contradiction.py --check
Writes:  research/modalities/emc-radiotherapy-contradiction.json
"""

from __future__ import annotations

import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-radiotherapy-contradiction.json")

# ---------------------------------------------------------------------------
# the two comparable estimates
# ---------------------------------------------------------------------------

ESTIMATES = [
    {
        "source_id": "bishop2019",
        "pmcid": "PMC7771031",
        "provenance": "primary",
        "read_from": "literature-cache: icdo-9231-size-round5/"
                     "pmc_page_PMC7771031_emc_combined_modality.txt (PMC full text, HTTP 200)",
        "cohort": "41 consecutive patients with localized EMC, MD Anderson, 1990-2016",
        "n": 41,
        "median_followup_months": 94,
        "followup_range_months": [8, 316],
        "endpoint": "local control",
        "exposure_as_printed": "surgery alone (the ADVERSE exposure)",
        "hr": 12.7, "ci": [1.4, 115.3], "p": 0.02,
        "analysis": "multivariable",
        "events": 5,
        "events_note": "5 patients (12 %) with local relapse at a median 75 months (range 13-176); "
                       "4 of the 5 had surgery alone",
        "printed_in": "Abstract and Results: 'the only significant factor associated with poorer LC "
                      "was the use of surgery alone (10-year LC 63% vs. 100% for CMT, P = 0.004), "
                      "which remained the only factor also significant on multivariable analysis "
                      "(P = 0.02, HR 12.7, 95% CI 1.4-115.3)'",
        "arms": {"preoperative_RT": 23, "postoperative_RT": 10, "surgery_alone": 8},
        "dose_gy": {"median": 50, "range": [50, 65], "per_arm": None},
        "ten_year_local_control_percent": {"surgery_alone": 63, "combined_modality": 100},
        "⚠_the_univariate_table_could_not_be_parsed_reliably": (
            "The cached copy is an HTML page and its univariate table survives tag-stripping as a "
            "run of bare numbers whose column headers cannot be recovered. One reading of it puts "
            "tumour size > 5 cm at p = 0.02 for local control, which would sit awkwardly beside the "
            "abstract's 'the only significant factor'. ⛔ THAT IS NOT REPORTED AS A DISCREPANCY, "
            "because a garbled table is not evidence of one -- it is recorded as a thing to check "
            "against a clean copy of the paper, and nothing in this module depends on it."),
    },
    {
        "source_id": "masunaga2025",
        "pmcid": "PMC12398172",
        "provenance": "primary",
        "read_from": "emc-prognostic-coefficients.json, transcribed from Table 2 and verified "
                     "against the article text",
        "cohort": "134 patients localized at diagnosis who underwent surgery, Japanese National "
                  "Bone and Soft Tissue Tumor Registry, 2002-2022",
        "n": 134,
        "median_followup_months": 38,
        "followup_range_months": None,
        "endpoint": "local recurrence-free survival",
        "exposure_as_printed": "(neo)adjuvant radiotherapy (the PROTECTIVE exposure)",
        "hr": 0.50, "ci": [0.11, 2.25], "p": 0.365,
        "analysis": "univariate",
        "events": 16,
        "events_note": "16 patients (11.9 %) with local recurrence at a median 15 months "
                       "(IQR 4.5-63.5). ⚠ Radiotherapy was NOT retained by the stepwise "
                       "multivariable model, which kept surgical margin alone -- so no adjusted "
                       "radiotherapy estimate exists in this series.",
        "printed_in": "Table 2, univariate block, '(Neo)adjuvant radiotherapy / Yes / 24 / "
                      "0.50 (0.11-2.25) / 0.365'",
        "arms": {"neoadjuvant_RT": 4, "adjuvant_RT": 20, "no_perioperative_RT": 110},
        "dose_gy": {"neoadjuvant": [40, 50], "adjuvant": [50, 66],
                    "fractionation": "2 Gy fractions", "per_arm": "ranges only, not per patient"},
        "ten_year_local_control_percent": None,
        "⚠_confounded_against_radiotherapy": (
            "The paper states radiotherapy 'is administered to prevent local recurrence in patients "
            "with close surgical margins', and reports 10 of 24 irradiated patients (41.7 %) with "
            "R1/R2 margins against 20 of 110 (18.2 %) unirradiated. Margin is this paper's "
            "strongest local-recurrence covariate (HR 4.76, 1.72-13.15). The treated arm was "
            "therefore at higher baseline risk of local recurrence, so 0.50 is a CONSERVATIVE "
            "estimate of any protection -- the bias runs against radiotherapy, not for it."),
    },
]

# Case-level modality reports. Existence proofs, never efficacy.
MODALITY_CASE_REPORTS = [
    {
        "modality": "high_dose_rate_interstitial_brachytherapy",
        "source": "Takagawa et al., J Contemp Brachytherapy",
        "pmcid": "PMC9044308",
        "doi": "10.5114/jcb.2022.115161",
        "provenance": "primary",
        "read_from": "literature-cache: emc-radiotherapy-2026-08-26/PMC9044308.txt",
        "n": 1,
        "detail": "Metastatic EMC in an 87-year-old woman; 30 Gy in 2 fractions over 1 day per "
                  "metastatic site, to inguinal nodes, breast and popliteal fossa. Chosen because "
                  "the patient could not undergo prolonged external-beam treatment.",
    },
    {
        "modality": "proton_beam",
        "source": "Honda et al., as described by Remiszewski et al. 2025",
        "pmcid": None,
        "doi": None,
        "provenance": "secondary",
        "read_from": "literature-cache: emc-radiotherapy-2026-08-26/PMC12504171.txt (review)",
        "n": 1,
        "detail": "EMC of the pelvis, 11 x 6 x 13 cm, treated instead of wide resection with "
                  "three-dimensional conformal radiotherapy 36 Gy in 10 fractions followed by "
                  "proton beam radiotherapy 30.8 Gy in 11 fractions, with intra-arterial "
                  "cisplatin.",
        "⛔_not_read_directly": "The primary report has not been retrieved; these figures are as "
                                "the review states them and must not be quoted as read.",
    },
    {
        "modality": "preoperative_external_beam",
        "source": "Improta et al., as described by Remiszewski et al. 2025",
        "pmcid": "PMC7731621",
        "doi": None,
        "provenance": "secondary",
        "read_from": "literature-cache: emc-radiotherapy-2026-08-26/PMC12504171.txt (review)",
        "n": 1,
        "detail": "Locally recurrent EMC of the shoulder; preoperative radiotherapy 50 Gy in 25 "
                  "fractions over 5 weeks, with no viable tumour cells at resection.",
        "⛔_not_read_directly": "Its PMCID is known and the full text was not retrieved for this "
                                "curation; the figures are the review's.",
    },
]

CARBON_ION = {
    "found_in_this_histology": False,
    "how_searched": (
        "354 open-access full texts retrieved for a radiotherapy-scoped EMC query "
        "(literature-cache: emc-radiotherapy-2026-08-26); 228 mention extraskeletal myxoid "
        "chondrosarcoma. The 2025 comprehensive EMC review in that corpus (Remiszewski et al., "
        "PMC12504171) contains no occurrence of 'carbon' at all."),
    "⚠_a_search_summary_suggested_otherwise_and_was_not_used": (
        "A web-search synthesis reported that 'two received carbon ion therapy, one received proton "
        "beam therapy' in a large clinical series. Read against the sources, that belongs to "
        "EXTRACRANIAL CHONDROSARCOMA generally, not to this histology, and it was not carried into "
        "this record. An AI search summary is a lead, never a citation."),
    "⛔_absence_of_evidence": (
        "This is a reading of the reachable open-access corpus, not of the particle registries "
        "themselves, which are not open. Carbon-ion treatment of EMC may exist and be unpublished "
        "or published behind a paywall. The honest statement is that it does not appear in what "
        "this program can read."),
}


# ---------------------------------------------------------------------------
# derivations
# ---------------------------------------------------------------------------


def invert(hr: float, ci: list) -> dict:
    """Put an adverse-exposure hazard on the protective-exposure scale.

    ⚠ INVERTING AN HR IS EXACT ARITHMETIC AND AN INEXACT COMPARISON. 1/HR is the hazard of the
    complementary exposure ONLY when the contrast is a clean two-way split, which "surgery alone vs
    combined modality" is and "(neo)adjuvant RT vs none" nearly is. The bounds swap, because
    inversion reverses order. What it does NOT fix is that the two studies measure different
    endpoints over different follow-ups; this is a direction-and-overlap device, not a conversion.
    """
    return {"hr": round(1.0 / hr, 4), "ci": [round(1.0 / ci[1], 4), round(1.0 / ci[0], 4)]}


def _overlap(a: list, b: list):
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    return (lo, hi) if lo <= hi else None


def comparison() -> dict:
    bishop = next(e for e in ESTIMATES if e["source_id"] == "bishop2019")
    mas = next(e for e in ESTIMATES if e["source_id"] == "masunaga2025")
    inv = invert(bishop["hr"], bishop["ci"])
    ov = _overlap(inv["ci"], mas["ci"])
    return {
        "bishop2019_as_printed": {"exposure": bishop["exposure_as_printed"],
                                  "hr": bishop["hr"], "ci": bishop["ci"], "p": bishop["p"],
                                  "endpoint": bishop["endpoint"], "analysis": bishop["analysis"]},
        "bishop2019_inverted_to_a_radiotherapy_effect": inv,
        "masunaga2025_as_printed": {"exposure": mas["exposure_as_printed"],
                                    "hr": mas["hr"], "ci": mas["ci"], "p": mas["p"],
                                    "endpoint": mas["endpoint"], "analysis": mas["analysis"]},
        "both_point_estimates_protective": inv["hr"] < 1.0 and mas["hr"] < 1.0,
        "intervals_overlap": ov is not None,
        "overlap_interval": [round(ov[0], 4), round(ov[1], 4)] if ov else None,
        "⭐_the_reading": (
            "Two estimates of the same direction whose intervals overlap. What separates them is "
            "which side of p = 0.05 each fell on, and neither is well powered -- 5 local relapses "
            "in one, 16 in the other, and an interval spanning two orders of magnitude in the one "
            "that reached significance. ⛔ THIS DOES NOT SHOW RADIOTHERAPY WORKS. It shows the "
            "reachable evidence fails to establish the disagreement the route was built on."),
        "⛔_what_this_comparison_is_not": [
            "Not a meta-analysis. No pooled hazard ratio is computed and none should be quoted.",
            "Not a like-for-like conversion: Bishop's endpoint is 10-year local control and "
            "Masunaga's is local recurrence-free survival, over 94 and 38 months of median "
            "follow-up respectively.",
            "Not adjusted-vs-adjusted: Bishop's figure is multivariable and Masunaga's is "
            "univariate, because its stepwise model dropped radiotherapy entirely.",
            "Not a claim the two cohorts are comparable: 80 % of Bishop's patients received "
            "radiotherapy against 18 % of Masunaga's, which is a difference in practice large "
            "enough that the two are describing different treatment cultures.",
        ],
    }


def build() -> dict:
    comp = comparison()
    return {
        "_what": ("Whether the two EMC series that disagree about radiotherapy actually disagree, "
                  "and what modalities beyond external-beam have been reported in this histology."),
        "_not_medical_advice": (
            "Nothing here is medical advice, and nothing here asserts efficacy, safety, a "
            "therapeutic window or clinical readiness. Two retrospective series with overlapping "
            "intervals do not establish that a treatment works."),
        "_generated_by": "research/modalities/emc_radiotherapy_contradiction.py",
        "⭐_the_headline": (
            "RT-RT-INTENSIFY is built on a 'live contradiction' about whether radiotherapy does "
            "anything in EMC. Put on one scale, the two series do not contradict each other: "
            f"Bishop's surgery-alone HR of 12.7 inverts to a radiotherapy effect of "
            f"{comp['bishop2019_inverted_to_a_radiotherapy_effect']['hr']} "
            f"({comp['bishop2019_inverted_to_a_radiotherapy_effect']['ci'][0]}-"
            f"{comp['bishop2019_inverted_to_a_radiotherapy_effect']['ci'][1]}) and Masunaga's is "
            f"0.5 (0.11-2.25) -- both protective, intervals overlapping across "
            f"{comp['overlap_interval'][0]}-{comp['overlap_interval'][1]}. The disagreement is in "
            "significance, not direction, between two underpowered studies."),
        "estimates": ESTIMATES,
        "comparison": comp,
        "modality_case_reports": MODALITY_CASE_REPORTS,
        "carbon_ion": CARBON_ION,
        "⛔_case_reports_are_existence_proofs": (
            "Brachytherapy and proton beam have each been reported once in this histology, and a "
            "preoperative external-beam complete pathological response once. A case report "
            "establishes that a thing was DONE and that someone chose to publish it. It carries no "
            "denominator, no comparator and a publication bias toward success, so it can answer "
            "'does an arm exist' and can never answer 'does it work'."),
        "⛔_the_dose_response_is_still_unbuildable": (
            "Both series publish dose at the ARM level -- Bishop a median of 50 Gy over a 50-65 "
            "range, Masunaga 40-50 Gy neoadjuvant and 50-66 Gy adjuvant in 2 Gy fractions. A "
            "dose-response regression needs dose PER PATIENT against outcome per patient, and "
            "neither publishes that. ⚠ So the route's regression remains unbuildable, but the "
            "reason is narrower than its readiness states: dose and modality ARE published, just "
            "not per patient."),
        "provenance_split": {
            "primary": sorted({e["source_id"] for e in ESTIMATES if e["provenance"] == "primary"}
                              | {c["modality"] for c in MODALITY_CASE_REPORTS
                                 if c["provenance"] == "primary"}),
            "secondary": sorted({c["modality"] for c in MODALITY_CASE_REPORTS
                                 if c["provenance"] == "secondary"}),
            "⛔_rule": ("POLICY-evidence 1.3 forbids laundering a citation. A record read only in "
                        "someone else's review says so and may not be quoted as read."),
        },
        "counts": {
            "comparable_estimates": len(ESTIMATES),
            "case_reports": len(MODALITY_CASE_REPORTS),
            "primary_records": sum(1 for x in ESTIMATES + MODALITY_CASE_REPORTS
                                   if x["provenance"] == "primary"),
            "secondary_records": sum(1 for x in ESTIMATES + MODALITY_CASE_REPORTS
                                     if x["provenance"] == "secondary"),
        },
    }


# ---------------------------------------------------------------------------
# guards
# ---------------------------------------------------------------------------


def _check_structure() -> list[str]:
    errs: list[str] = []
    for e in ESTIMATES:
        lo, hi = e["ci"]
        if not (lo <= e["hr"] <= hi):
            errs.append(f"{e['source_id']}: HR {e['hr']} outside its interval {e['ci']}")
        excludes_one = lo > 1.0 or hi < 1.0
        if excludes_one != (e["p"] < 0.05):
            errs.append(f"{e['source_id']}: interval {e['ci']} and p = {e['p']} disagree on "
                        f"significance")
        if e["provenance"] not in ("primary", "secondary"):
            errs.append(f"{e['source_id']}: provenance is neither primary nor secondary")
        if not e.get("read_from"):
            errs.append(f"{e['source_id']}: no read_from -- provenance is unverifiable")
    for c in MODALITY_CASE_REPORTS:
        if c["provenance"] == "secondary" and "⛔_not_read_directly" not in c:
            errs.append(f"{c['modality']}: secondary record with no not-read-directly marker")
        if c["provenance"] == "primary" and "⛔_not_read_directly" in c:
            errs.append(f"{c['modality']}: primary record carries a not-read-directly marker")
        if c["n"] != 1:
            errs.append(f"{c['modality']}: recorded under case reports with n = {c['n']}")
    if CARBON_ION["found_in_this_histology"] is not False:
        errs.append("the carbon-ion finding has flipped without its search being redone")
    return errs


def _check_inversion() -> list[str]:
    """The inversion is the load-bearing arithmetic; verify it round-trips."""
    errs: list[str] = []
    b = next(e for e in ESTIMATES if e["source_id"] == "bishop2019")
    inv = invert(b["hr"], b["ci"])
    if abs(1.0 / inv["hr"] - b["hr"]) > 0.05:
        errs.append("inverting the inverted HR does not return the printed one")
    if inv["ci"][0] > inv["ci"][1]:
        errs.append("the inverted interval bounds were not swapped")
    if not (inv["ci"][0] <= inv["hr"] <= inv["ci"][1]):
        errs.append("the inverted HR falls outside its own inverted interval")
    return errs


def check() -> int:
    errs = _check_structure() + _check_inversion()
    doc = build()
    if not os.path.exists(OUT):
        errs.append(f"{os.path.basename(OUT)} is missing; run without --check to build it")
    else:
        with open(OUT, encoding="utf-8") as fh:
            if json.load(fh) != doc:
                errs.append(f"{os.path.basename(OUT)} does not reproduce from its generator")
    for e in errs:
        print(f"ERROR: {e}")
    if errs:
        return 1
    c = doc["counts"]
    print(f"emc_radiotherapy_contradiction --check OK "
          f"({c['comparable_estimates']} estimates, {c['case_reports']} case reports, "
          f"{c['primary_records']} primary / {c['secondary_records']} secondary)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the artifact reproduces and every guard holds")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    errs = _check_structure() + _check_inversion()
    for e in errs:
        print(f"ERROR: {e}")
    if errs:
        return 1
    doc = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    c = doc["comparison"]
    inv = c["bishop2019_inverted_to_a_radiotherapy_effect"]
    m = c["masunaga2025_as_printed"]
    print(f"  bishop2019 inverted : {inv['hr']} {inv['ci']}")
    print(f"  masunaga2025        : {m['hr']} {m['ci']}")
    print(f"  intervals overlap   : {c['intervals_overlap']}  over {c['overlap_interval']}")
    print(f"  carbon ion in EMC   : {doc['carbon_ion']['found_in_this_histology']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
