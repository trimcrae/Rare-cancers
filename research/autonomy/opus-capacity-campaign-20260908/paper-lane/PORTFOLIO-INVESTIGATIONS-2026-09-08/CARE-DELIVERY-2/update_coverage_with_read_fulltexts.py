#!/usr/bin/env python3
"""CARE-DELIVERY-2: fold two ACTUALLY-READ full texts into the PUB-CARE-DELIVERY coverage matrix.

Reads the v1 matrix (unchanged, another lane's artifact) plus a readings block written here from
the PMC full texts retrieved in this session through the PubMed MCP server, and emits
care-delivery-element-coverage-v2.json.

No network. No write outside this lane's directory.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "PUB-CARE-DELIVERY", "care-delivery-element-coverage.json")

READ_SCOPE = ("NCBI PMC full-text API via the PubMed MCP server, 2026-09-08/09. The response carried "
              "the abstract and the narrative sections only. TABLES, FIGURES AND LEGENDS WERE NOT "
              "RETURNED. Every NOT-PRINTED status below is scoped to the narrative sections named in "
              "its `read_sections`, and is NEVER a claim about the paper's tables.")

R = "REPORTED"; E = "EXAMINED_NOT_PRINTED"; N = "NOT_EXAMINED"

READINGS = {
 "bishop2019": {
  "pmcid": "PMC7771031", "pmid": "31436747", "doi": "10.1097/COC.0000000000000590",
  "n": 41,
  "read_sections": ["Abstract", "INTRODUCTION", "MATERIAL AND METHODS (incl. Follow-up and "
                    "Statistical Analysis)", "RESULTS (Patient and Tumor Characteristics; Treatment; "
                    "Survival; Patterns of Disease Recurrence; Outcomes After Relapse)", "DISCUSSION"],
  "not_read": ["all tables", "all figures", "all legends", "supplementary material"],
  "elements": {
   "surgical_margin_distribution": {"status": R,
     "verbatim": "Final margin status was negative in 35 patients (85%) and positive/uncertain in 6 patients (15%).",
     "section": "RESULTS / Treatment",
     "note": "A two-level distribution (negative vs positive/uncertain), not an R0/R1/R2 split, so it is NOT directly poolable with masunaga2025, chiusole2020 or drilon2008."},
   "margin_definition_printed": {"status": E,
     "section": "read across Methods and Results",
     "note": "No definition of 'negative' or of 'positive/uncertain' appears in the narrative text read, and the R0/R1/R2 scale is not used anywhere in it."},
   "stage_at_diagnosis_split": {"status": E,
     "verbatim": "We identified 41 consecutive patients with localized, non-metastatic histologically confirmed EMC",
     "section": "MATERIAL AND METHODS",
     "note": "There is no split to report: the cohort is restricted to localized non-metastatic disease by design, so stage at diagnosis is constant by construction."},
   "primary_site_distribution": {"status": R,
     "verbatim": "most tumors were located in the lower extremity (n=22, 54%) ... or upper extremity (n=10, 24%) ... with a limited number in the trunk (n=8, 20%) ... or neck (2%, n=1)",
     "section": "RESULTS / Patient and Tumor Characteristics",
     "note": "Already REPORTED in v1 from research/modalities/emc-site-curation.json; independently re-read here and consistent."},
   "median_follow_up": {"status": R,
     "verbatim": "The median follow-up time from the completion of local therapy for patients alive at last follow-up was 94 months (range, 8-316 months).",
     "section": "RESULTS / Survival",
     "note": "Time zero is completion of local therapy, and the median is over patients alive at last follow-up -- both differ from a from-diagnosis median, so it is not interchangeable with drilon2008's 3.6 years."},
   "time_to_event_median": {"status": R,
     "verbatim": "The median time to any failure was 15 months (range, 3-176 months). ... 5 patients (12%) with local relapse at a median time of 75 months (range 13-176 months). ... Thirteen patients (32%) developed distant metastases ... at a median time of 28 months (range 3-154 months).",
     "section": "RESULTS / Patterns of Disease Recurrence"},
   "fitted_cox_coefficients": {"status": R,
     "verbatim": "The only factor that emerged as significantly associated with poorer LC was use of surgery alone (=0.02, HR 12.7, 95% CI 1.4 -115.3) compared to combined modality therapy. ... local recurrence was the only factor associated with poorer DMFS (=0.04, HR 3.9, 95% CI 1.1-14.7).",
     "section": "RESULTS / Patterns of Disease Recurrence",
     "note": "Two multivariable HRs with CIs are printed in the narrative text. The LC interval 1.4-115.3 spans two orders of magnitude on 5 events; recorded as printed, not treated as an estimate anyone should pool."},
   "numbers_at_risk_row": {"status": N, "evidence": "FIGURES_NOT_RETURNED",
     "note": "The KM figures were not in the MCP response, so the risk row is unexamined. ⛔ The closed KM/IPD reconstruction pilot is NOT reopened here and no curve was digitised."},
   "treatment_setting_or_referral": {"status": R,
     "verbatim": "Twenty-seven patients (66%) presented to MDACC with gross disease, whereas 14 patients (34%) presented after an outside excision had already been performed, of which 12 patients had a positive/uncertain margins and 2 had negative margins.",
     "also": "41 consecutive patients ... treated at the University of Texas MD Anderson Cancer Center (MDACC) ... All diagnoses were confirmed at the time of presentation by sarcoma pathologists at MDACC. ... Patients are typically presented at a multidisciplinary tumor board for treatment discussion.",
     "section": "RESULTS / Treatment (per-patient split); MATERIAL AND METHODS (cohort setting)",
     "⭐_why_this_is_decisive": "This is a per-patient record of WHERE THE PATIENT WAS FIRST OPERATED -- inside the specialist sarcoma centre (n=27) or outside it before referral (n=14) -- which is exactly the field emc-surgical-quality.json's `what_would_answer_it` asks for ('A series that reports where each patient was first operated'). It is reported, in a reachable series.",
     "⛔_what_it_still_is_not": "It is a two-level in/out-of-centre split within one institution's referred population, with no comparator arm and no centre-volume variable. It cannot show that referral-centre care changes EMC outcomes, and this lane makes no such claim."},
   "unplanned_excision_defined": {"status": E,
     "section": "read across Abstract, Methods, Results, Discussion",
     "note": "The terms 'unplanned', 'inadvertent' and 'whoops' do not appear in the narrative text read, and the paper never states whether the 14 outside excisions were planned or unplanned.",
     "proxy_reported": {
       "field": "presented after an outside excision had already been performed",
       "n": 14, "of": 41, "pct": 34,
       "margin_at_referral": {"positive_or_uncertain": 12, "negative": 2},
       "section": "RESULTS / Treatment",
       "is_the_thing": False,
       "⛔_why_not": "'Outside excision' is an institutional-origin fact, not a statement that the operation was unplanned; an outside excision can be a correctly planned oncological resection. But it is anchored to a named institution and comes with the margin found at referral, which makes it a STRONGER proxy than masunaga2025's undefined 'previous surgery' field. Recorded as a proxy; no unplanned-excision rate is computed from it."}},
  }},
 "drilon2008": {
  "pmcid": "PMC2779719", "pmid": "18951519", "doi": "10.1002/cncr.23978",
  "n": 87,
  "⚠_n_discrepancy": "The abstract says 87 patients; Methods say '86 patients ... were retrieved' and Results say 'Of the 86 evaluable patients'. The repository's candidate list carries 87. Recorded, not resolved; nothing here depends on it.",
  "read_sections": ["Abstract", "untitled Introduction", "MATERIALS AND METHODS (Patient Selection; "
                    "Demographics and Statistical Methods)", "RESULTS (Clinical Features of Local and "
                    "Metastatic EMC; Treatment Outcomes for Localized Disease; Follow-up and OS; "
                    "Chemotherapy Outcomes)", "DISCUSSION"],
  "not_read": ["all tables", "all figures", "all legends", "supplementary material"],
  "elements": {
   "surgical_margin_distribution": {"status": R,
     "verbatim": "In a subset of 43 patients in whom there were data regarding quality of the resection (R0, R1, and R2), only 2 of 24 patients who underwent an R0 resection developed local disease recurrence, whereas 3 of 12 patients with an R1 resection and 5 of 7 with an R2 resection experienced local disease recurrence (< .01, Fisher exact test).",
     "section": "RESULTS / Treatment Outcomes for Localized Disease",
     "derived": {"R0": 24, "R1": 12, "R2": 7, "denominator": 43},
     "⚠_informative_missingness": "43 of 73 curative-intent patients have a margin value; 30 (41 %) do not. The paper does not say who they are. As in chiusole2020, missingness in a margin field over a series reaching back to 1975 is not plausibly random, so this is a distribution over 43, NOT a margin rate for the cohort."},
   "margin_definition_printed": {"status": R,
     "verbatim": "Pathology and surgical reports were used to determine the completeness of resection (R0: complete resection, negative margins; R1, complete macroscopic resection, positive microscopic margins; and R2, incomplete resection).",
     "section": "MATERIALS AND METHODS / Demographics and Statistical Methods",
     "note": "Compatible with masunaga2025's printed definition (microscopically negative / microscopically positive / macroscopically positive), so these two margin distributions are on the same scale."},
   "stage_at_diagnosis_split": {"status": R,
     "verbatim": "Approximately 87% (76 of 86 patients) of patients presented with primary localized disease.",
     "section": "RESULTS / Clinical Features of Local and Metastatic EMC",
     "note": "The abstract states the complement as 'Approximately 13% of patients presented with metastases'."},
   "primary_site_distribution": {"status": R,
     "verbatim": "Approximately 62% had a primary site in the lower extremities; 17% in the upper extremities; 13% in the abdomen, retroperitoneum, or pelvis; and 8% in other areas.",
     "section": "RESULTS / Clinical Features of Local and Metastatic EMC",
     "note": "Printed as percentages only in the narrative text; the counts, if any, would be in the table, which was not returned."},
   "median_follow_up": {"status": R,
     "verbatim": "Follow-up data were available for all 86 patients studied, with a median follow-up time of 3.6 years (range, 0.2 years-24.6 years).",
     "section": "RESULTS / Follow-up and OS",
     "note": "From the initial date of diagnosis. The authors themselves flag it: 'Our follow-up was relatively short compared with other series' (DISCUSSION)."},
   "time_to_event_median": {"status": R,
     "verbatim": "Local disease recurrence was noted in 37% of patients (n = 27) ... with a median time to disease recurrence of 3.3 years. ... Distant disease recurrence was observed in 26% of patients (n = 19), with a median time of 3.2 years. ... The median time to any disease recurrence was 4.7 years (95% CI, 4.4 years-5.0 years).",
     "section": "RESULTS / Treatment Outcomes for Localized Disease"},
   "fitted_cox_coefficients": {"status": E,
     "verbatim": "A multivariate analysis of local recurrence and metastatic disease in addition to the above factors affecting OS was performed using the Cox proportional hazards model after a similar univariate analysis.",
     "section": "MATERIALS AND METHODS / Demographics and Statistical Methods; RESULTS / Follow-up and OS",
     "note": "A Cox model is stated to have been fitted, but the narrative text prints only p values ('only presentation with metastatic disease was found to affect OS (=.005)') -- no hazard ratio and no confidence interval. Coefficients may be in the tables, which were NOT returned; so this is not-printed IN THE NARRATIVE, not absent from the paper."},
   "numbers_at_risk_row": {"status": N, "evidence": "FIGURES_NOT_RETURNED",
     "note": "Same as bishop2019. ⛔ The closed KM/IPD pilot is not reopened."},
   "treatment_setting_or_referral": {"status": E,
     "verbatim": "we assembled a retrospective series of patients from 2 large referral centers",
     "also": "86 patients of EMC were retrieved from the databases of the Memorial Sloan-Kettering Cancer Center in New York City and the Royal Marsden Hospital in London.",
     "section": "Introduction (final paragraph); MATERIALS AND METHODS / Patient Selection",
     "note": "Setting is stated, but only as a COHORT-LEVEL CONSTANT: the whole series is referral-centre care. No per-patient referral status, no first-operating-hospital field, no centre-volume variable appears in the narrative text read. This is the same shape as chiusole2020 -- the exposure is held constant, so the series cannot answer the referral question -- and it is exactly what bishop2019 does differently."},
   "unplanned_excision_defined": {"status": E,
     "verbatim": "using the date of wide local excision (WLE) as Time 0, irrespective of previous procedures",
     "also": "In a recent multi-institutional study by Kawaguchi et al, the role of WLE despite previous procedures or disease recurrence was emphasized",
     "section": "MATERIALS AND METHODS / Demographics and Statistical Methods; DISCUSSION",
     "note": "'Previous procedures' is acknowledged twice and counted zero times. The paper never defines them, never reports how many patients had one, and never calls any of them unplanned. The terms 'unplanned', 'inadvertent' and 'whoops' do not appear in the narrative text read. ⛔ This is a visible omission -- the analysis explicitly conditions on prior procedures existing -- not an inference from silence."},
  }},
}

def main():
    v1 = json.load(open(V1))
    m = json.loads(json.dumps(v1["coverage_matrix"]))   # deep copy; v1 file is never written
    for sid, rd in READINGS.items():
        assert sid in m, sid
        assert m[sid]["n"] == rd["n"], (sid, m[sid]["n"], rd["n"])
        cell = m[sid]
        cell["retrieval_verdict"] = "RETRIEVED AND READ by CARE-DELIVERY-2 (PMC full text via PubMed MCP)"
        cell["pmcid"] = rd["pmcid"]; cell["pmid"] = rd["pmid"]; cell["doi"] = rd["doi"]
        cell["read_sections"] = rd["read_sections"]
        cell["not_read"] = rd["not_read"]
        if "⚠_n_discrepancy" in rd:
            cell["⚠_n_discrepancy"] = rd["⚠_n_discrepancy"]
        for el, val in rd["elements"].items():
            assert el in cell["elements"], (sid, el)
            new = {"status": val["status"]}
            new.update({k: v for k, v in val.items() if k != "status"})
            new["evidence"] = new.get("evidence", "read directly from the PMC full text, "
                                                 + rd["pmcid"])
            new["_was_in_v1"] = v1["coverage_matrix"][sid]["elements"][el]["status"]
            cell["elements"][el] = new

    elements = list(next(iter(m.values()))["elements"].keys())
    counts = {}
    for el in elements:
        b = {R: {"n_series": 0, "series": [], "patients": 0},
             E: {"n_series": 0, "series": [], "patients": 0},
             N: {"n_series": 0, "series": [], "patients": 0}}
        for sid, cell in m.items():
            st = cell["elements"][el]["status"]
            b[st]["n_series"] += 1; b[st]["series"].append(sid); b[st]["patients"] += cell["n"]
        counts[el] = b

    two_plus = {el: counts[el][R]["series"] for el in elements if counts[el][R]["n_series"] >= 2}

    out = {
     "_what": "CARE-DELIVERY-2 v2 of the care-delivery data-element coverage matrix: the v1 matrix with bishop2019 (PMC7771031) and drilon2008 (PMC2779719) replaced by an ACTUAL READING of their PMC full texts, and the emc-surgical-quality.json absence-claim audit re-decided on that evidence.",
     "_not_medical_advice": "Nothing here is medical advice and nothing here asserts efficacy, safety, selectivity, a therapeutic window or clinical readiness. No patient was studied; no wet-lab work exists. Nothing here says referral-centre care changes EMC outcomes.",
     "_lane": "research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/CARE-DELIVERY-2",
     "_generated_by": "update_coverage_with_read_fulltexts.py (this lane)",
     "_supersedes": "…/PUB-CARE-DELIVERY/care-delivery-element-coverage.json for the bishop2019 and drilon2008 rows only. That file is another lane's artifact and was READ, NOT WRITTEN.",
     "_reads_only": [os.path.relpath(V1, "/home/user/Rare-cancers"),
                     "two PMC full texts retrieved in session (see checks/)"],
     "_source_attribution": "Full texts retrieved from PubMed Central through the PubMed MCP server. bishop2019 DOI https://doi.org/10.1097/COC.0000000000000590 ; drilon2008 DOI https://doi.org/10.1002/cncr.23978",
     "_read_scope": READ_SCOPE,
     "_three_valued": {"REPORTED": "the paper prints the element in a section this lane read",
                       "EXAMINED_NOT_PRINTED": "this lane read the sections named in the row's read_sections and the element is not there; NOT a claim about the paper's tables or figures",
                       "NOT_EXAMINED": "no committed reading exists; the element is UNKNOWN, never absent"},
     "candidate_series": v1["candidate_series"],
     "candidate_patients_sum": v1["candidate_patients_sum"],
     "⛔_patients_are_not_additive": v1["⛔_patients_are_not_additive"],
     "series_newly_read_by_this_lane": sorted(READINGS),
     "coverage_matrix": m,
     "element_counts": counts,
     "elements_reported_by_two_or_more_series": two_plus,
     "⭐_margin_distributions_are_not_all_on_one_scale": {
       "on_the_printed_R0_R1_R2_scale": {
         "series": ["masunaga2025", "chiusole2020", "drilon2008"],
         "patients_with_a_margin_value": {"masunaga2025": 156, "chiusole2020": 40, "drilon2008": 43},
         "note": "All three print or state a definition compatible with microscopically-negative / microscopically-positive / macroscopically-positive. This is the largest set of EMC series whose margin distributions can actually be put side by side -- three, up from two before this lane."},
       "not_on_that_scale": {
         "series": ["bishop2019"],
         "note": "bishop2019 reports margin as negative (35) vs positive/uncertain (6) and prints no definition in the narrative text read. It raises the margin-REPORTED count to 4 but CANNOT be pooled with the other three, because 'uncertain' is collapsed into 'positive' and R1 and R2 are not separated."},
       "⛔_still_not_a_pooled_rate": "Nothing here computes a pooled EMC positive-margin rate. emc-surgical-quality.json already records that the denominator choice moves that rate more than the width of any interval, and all four series have informative missingness or a restricted cohort."},
    }
    out["absence_claim_denominator_audit_v2"] = build_audit(v1, counts)
    p = os.path.join(HERE, "care-delivery-element-coverage-v2.json")
    json.dump(out, open(p, "w"), indent=1, ensure_ascii=False)
    open(p, "a").write("\n")
    print("wrote", p)
    for el in elements:
        c = counts[el]
        print(f"  {el:32s} REPORTED={c[R]['n_series']:2d} ({c[R]['patients']:4d})  "
              f"NOT_PRINTED={c[E]['n_series']:2d} ({c[E]['patients']:4d})  "
              f"NOT_EXAMINED={c[N]['n_series']:2d} ({c[N]['patients']:4d})")
    return 0


def build_audit(v1, counts):
    a1 = v1["absence_claim_denominator_audit"]
    examined = sorted(set(a1["series_actually_examined_for_these_two_fields"]) | set(READINGS))
    residue = [s for s in a1["series_reachable_by_at_least_one_of_those_two_definitions_and_NOT_examined_for_these_fields"]
               if s not in READINGS]
    return {
     "claim_under_test": a1["claim"],
     "claim_values_as_written": a1["claim_values_read"],
     "v1_verdict": a1["verdict"],
     "series_examined_for_these_two_fields_now": examined,
     "n_examined_now": len(examined),
     "candidate_series_total": a1["candidate_series_total"],
     "still_reachable_and_unexamined_for_these_fields": residue,
     "⛔_what_the_residue_is": "martinbroto2020immunosarc1, morioka2016trabectedin and stacchiotti2013anthracycline are systemic-therapy trial reports of advanced disease, in which treatment setting and unplanned excision are close to inapplicable. For them these two fields remain UNKNOWN, not absent.",

     "treatment_setting": {
       "verdict": "FALSE",
       "why": "bishop2019 (n=41, PMC7771031), a reachable series, prints a per-patient record of where each patient was first operated: 27 (66 %) presented to MDACC with gross disease and 14 (34 %) presented after an outside excision. That is the field emc-surgical-quality.json's own `what_would_answer_it` names ('A series that reports where each patient was first operated'). The universal claim `recorded_in_any_reachable_series: false` is therefore contradicted by evidence, not merely over-scoped.",
       "the_reading": "RESULTS / Treatment, first paragraph; cohort setting from MATERIAL AND METHODS.",
       "⛔_but": "The exposure is two-level and within one specialist centre's referred population, with no comparator and no centre-volume variable. The field being REPORTED does not make the referral question answerable, and this lane asserts no association between setting and outcome.",
       "drilon2008": "EXAMINED_NOT_PRINTED, cohort-level constant only (two large referral centres). Same shape as chiusole2020; it does not contradict the claim and does not answer the question either."},

     "unplanned_excision": {
       "verdict": "CONFIRMED AT A WIDER DENOMINATOR, with a proxy finding that changes what is available",
       "why": "Neither bishop2019 nor drilon2008 defines, names or counts an unplanned/inadvertent excision anywhere in the narrative sections read. The terms 'unplanned', 'inadvertent' and 'whoops' appear in neither. So `recorded_in_any_reachable_series: false` survives, now over 4 examined series (masunaga2025, chiusole2020, bishop2019, drilon2008) instead of 2 -- but it is still a claim about an examined set of four, not about 'any reachable series'.",
       "⭐_what_changed_anyway": "bishop2019 prints n = 14/41 (34 %) 'presented after an outside excision had already been performed', with the margin found at referral (12 positive/uncertain, 2 negative). That is the strongest prior-resection proxy in the reachable EMC literature -- anchored to a named institution and carrying an outcome-relevant covariate -- and it is strictly better than masunaga2025's undefined 'previous surgery' field, which emc-surgical-quality.json already rejected. It is still a proxy: an outside excision may have been a correctly planned resection.",
       "drilon2008": "EXAMINED_NOT_PRINTED. 'Previous procedures' is acknowledged twice ('using the date of wide local excision (WLE) as Time 0, irrespective of previous procedures'; and the Kawaguchi sentence in the Discussion) and counted zero times. A visible omission, not an inference from silence."},

     "⛔_scope_of_every_absence_statement_here": "Scoped to the narrative sections listed in each series' read_sections. TABLES, FIGURES AND LEGENDS WERE NOT RETURNED by the PMC full-text API for either paper and were NOT read. If either paper tabulates an unplanned-excision or referral field, this lane would not have seen it.",
    }

if __name__ == "__main__":
    sys.exit(main())
