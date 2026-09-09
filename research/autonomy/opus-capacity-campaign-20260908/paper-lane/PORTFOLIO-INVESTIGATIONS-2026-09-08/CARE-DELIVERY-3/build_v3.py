#!/usr/bin/env python3
"""CARE-DELIVERY-3: rebuild the care-delivery element-coverage matrix at v3.

Reads CARE-DELIVERY-2's v2 matrix (READ ONLY -- never written) and replaces the three
systemic-therapy trial rows with an actual reading of their PMC full texts, retrieved through
the PubMed MCP server this session (checks/01-, 02-, 03-).

The one structural addition at v3 is a PER-SERIES `retrieval_completeness` field. The three
retrievals did NOT return the same thing: two came back with every table, one came back with the
narrative only. Collapsing that into a single global "tables were not returned" caveat, as v2 had
to, would either (a) throw away two complete table readings, or (b) silently convert a retrieval
limit into a reported absence for the third. Neither is acceptable, so completeness is recorded
per series and every EXAMINED_NOT_PRINTED status is scoped to what that series' own retrieval
actually returned.
"""
import json, os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.normpath(os.path.join(HERE, "..", "CARE-DELIVERY-2",
                                   "care-delivery-element-coverage-v2.json"))
OUT = os.path.join(HERE, "care-delivery-element-coverage-v3.json")

with open(V2, encoding="utf-8") as fh:
    v2_bytes = fh.read()
d = json.loads(v2_bytes)

NEW = ["martinbroto2020immunosarc1", "stacchiotti2013anthracycline", "morioka2016trabectedin"]

# ---------------------------------------------------------------- completeness, per series
COMPLETENESS = {
    "martinbroto2020immunosarc1": {
        "verdict": "NARRATIVE + ALL TABLES + ALL FIGURE LEGENDS",
        "returned": ["abstract", "Introduction", "Methods (Study design and subjects; Procedures; "
                     "Outcomes; Statistical analysis)", "Results", "Discussion",
                     "TABLE 1 Baseline characteristics (in full)",
                     "TABLE 2 Toxicity profile in phase Ib (in full)",
                     "TABLE 3 Univariate analysis (in full)",
                     "FIGURE LEGENDS 1, 2 and 3 (in full)"],
        "not_returned": ["the supplementary appendix (referenced in-text as supp1; several in-text "
                         "pointers are stripped to bare punctuation)", "figure images"],
        "⭐_why_this_matters": "Table 1 is the paper's baseline-characteristics table -- the exact "
                              "place a margin or prior-surgery variable would be printed -- and it "
                              "came back in full. An EXAMINED_NOT_PRINTED verdict for this series "
                              "therefore rests on having read that table, not on narrative silence.",
        "⛔_residual_scope": "Absence statements are scoped to abstract + narrative + Tables 1-3 + "
                            "figure legends. They are NOT claims about the supplementary appendix.",
    },
    "stacchiotti2013anthracycline": {
        "verdict": "NARRATIVE + ALL THREE TABLES + FIGURE LEGENDS (the most complete of the three)",
        "returned": ["abstract", "Background",
                     "Methods (Patients selection; Pathology and molecular analysis; Treatment; "
                     "Clinical assessment; Statistical analysis)",
                     "Results (Treatment; Pathology and molecular analysis; Response)",
                     "Discussion", "Conclusions",
                     "TABLE 1 Immunohistochemistry conditions (in full)",
                     "TABLE 2 Patient clinical characteristics and response evaluation "
                     "(in full: all 11 patient rows, all columns, plus its footnote)",
                     "TABLE 3 Immunohistochemistry and FISH results (in full)",
                     "FIGURE LEGENDS 1 and 2"],
        "not_returned": ["figure images -- Figure 2 is the Kaplan-Meier PFS curve, so any "
                         "numbers-at-risk row printed beneath it did NOT come through this route",
                         "no supplementary file is referenced by this paper"],
        "⭐_why_this_matters": "Table 2 is a PER-PATIENT baseline table covering the whole 11-patient "
                              "cohort and it came back in full, so the read covers essentially the "
                              "whole paper apart from figure images.",
        "⛔_residual_scope": "Absence statements are scoped to abstract + narrative + Tables 1-3 + "
                            "figure legends.",
    },
    "morioka2016trabectedin": {
        "verdict": "⚠ NARRATIVE ONLY -- NO TABLES, NO FIGURE LEGENDS (INCOMPLETE)",
        "returned": ["abstract", "Background", "Methods (Patients; Treatment and assessments)",
                     "Results", "Discussion", "Conclusions", "Abbreviations"],
        "not_returned": ["ALL TABLES -- in-text citations stripped to bare punctuation "
                         "('Clinical information of these subjects is presented in Table.', "
                         "'(Table, Fig.)', 'Adverse drug reactions ... are shown in Table.')",
                         "ALL FIGURES AND ALL FIGURE LEGENDS -- even the figure numbers are gone "
                         "('are shown in Figs.and.')"],
        "⛔_why_this_matters": "The un-returned 'Clinical information of these subjects' table is "
                              "precisely where primary site, stage, prior treatment and any "
                              "prior-surgery field for these five subjects would live. IT WAS NOT "
                              "RETRIEVED, so NO ABSENCE IS ASSERTED for this series for any element "
                              "that could live in it: those elements stay NOT_EXAMINED / UNKNOWN. "
                              "This is not a formality -- the repository's own receipt "
                              "research/autonomy/receipts/CYC-0028-moriokat.json records that this "
                              "paper's Table 2 was previously read from the PDF page raster and "
                              "carries per-subject PFS/OS with censoring flags, so a 'not printed' "
                              "verdict drawn from the narrative alone would have been demonstrably "
                              "wrong.",
        "⛔_residual_scope": "Only elements this lane found PRINTED in the narrative move. Nothing "
                            "moves to EXAMINED_NOT_PRINTED for this series.",
    },
}

# ---------------------------------------------------------------- the readings
R = "REPORTED"; E = "EXAMINED_NOT_PRINTED"; N = "NOT_EXAMINED"

readings = {}

readings["martinbroto2020immunosarc1"] = {
    "surgical_margin_distribution": (E,
        "Table 1 'Baseline characteristics' was returned in full and prints no margin status. What "
        "it prints in that neighbourhood is resectability, not margin: 'Resectable at diagnosis, "
        "n (%): Resectable 10 (63) [phase Ib] / 38 (73) [phase II]; Unresectable 6 (37) / 14 (27)'.",
        "Table 1 (Baseline characteristics)"),
    "margin_definition_printed": (E,
        "No margin scale, R0/R1/R2 wording or margin definition anywhere in the abstract, narrative "
        "or Tables 1-3.", "abstract; Methods; Results; Tables 1-3"),
    "stage_at_diagnosis_split": (R,
        "Table 1: 'Extension at diagnosis, n (%): Localized 9 (56) [phase Ib] / 25 (48) [phase II]; "
        "Locally advanced 2 (13) / 15 (29); Metastatic 5 (31) / 12 (23)'. ⚠ This is the WHOLE "
        "68-patient all-histology STS trial, not the 4 EMC patients.",
        "Table 1 (Baseline characteristics)"),
    "primary_site_distribution": (R,
        "Table 1: 'Primary tumor localization, n (%): Somatic 15 (94) / 44 (85); Visceral 1 (6) / "
        "8 (15)'. ⚠ A two-level somatic/visceral split for the whole 68-patient trial, not an "
        "anatomical site distribution and not EMC-specific. It is NOT commensurable with the "
        "thigh/leg/trunk site distributions the retrospective EMC series print.",
        "Table 1 (Baseline characteristics)"),
    "median_follow_up": (R,
        "Results: 'At a median follow-up of 17 months (4-26), 37 of 49 (76%) per-protocol evaluable "
        "patients experienced progression according to central assessment'. ⚠ Whole trial; time "
        "zero is enrolment on a systemic-therapy protocol for advanced disease, not diagnosis or "
        "completion of local therapy.", "Results"),
    "time_to_event_median": (R,
        "Results: 'The mPFS for central and local assessments was 5.6 months (3.0-8.1) and 6.0 "
        "months (3.1-9.0), respectively' and 'the mOS was 24 months (95% CI NA)'. ⚠ Whole trial, "
        "measured from enrolment. Not an EMC natural-history figure.", "Results"),
    "fitted_cox_coefficients": (E,
        "Table 3 'Univariate analysis' was returned in full: it prints medians, rates and log-rank "
        "p values by subgroup. No multivariable model, no hazard ratio and no fitted coefficient "
        "appears in the paper.", "Table 3 (Univariate analysis); Statistical analysis"),
    "numbers_at_risk_row": (E,
        "All three figure legends were returned in full and NONE is a Kaplan-Meier curve: Figure 1 "
        "'CONSORT diagram'; Figure 2 'Response to treatment by patient according to RECIST ... "
        "(N=60)' (a waterfall plot); Figure 3 'Progression-free survival to treatment by patient "
        "... Each patient in the efficacy population in phase II is represented as bars (n=49)' (a "
        "per-patient swimmer plot). No KM curve exists, so there is no numbers-at-risk row to read. "
        "This matches the repository's own independent screen, which recorded this source as 'NOT A "
        "PAIR - no KM curve exists' (S6-executed-artifacts/screened-identifiers.json). ⛔ No curve "
        "was digitised and the closed KM/IPD pilot is not reopened.",
        "figure legends 1-3"),
    "treatment_setting_or_referral": (R,
        "Reported as a COHORT-LEVEL CONSTANT, not per patient. Methods/Study design and subjects: "
        "'patients ... were considered for eligibility and enrolled in eight centers in Spain and "
        "Italy with expertise in sarcoma care. Central pathology review was mandatory before "
        "accrual.' Table 1 was returned in full and carries no per-patient centre, centre-volume or "
        "referral column. Same shape as chiusole2020 and drilon2008: the exposure is held constant, "
        "so this series cannot answer the referral question.",
        "Methods (Study design and subjects); Table 1"),
    "unplanned_excision_defined": (E,
        "Not printed, and Table 1 -- the baseline-characteristics table where it would be printed -- "
        "was returned in full. The words 'unplanned', 'inadvertent' and 'whoops' appear nowhere in "
        "the abstract, narrative or Tables 1-3. What Table 1 records of prior treatment is SYSTEMIC: "
        "'Median previous lines (range) 1.5 (0-5) / 1 (0-4)' and 'Previous antiangiogenic lines'. "
        "⭐ This is absence BY TRIAL DESIGN, not a curation gap: eligibility is advanced STS "
        "progressing within 6 months, the baseline set is built to characterise systemic-therapy "
        "exposure and tumour burden, and the quality of a prior local excision is not a variable the "
        "protocol collects. ⛔ Not a claim about the supplementary appendix, which was not returned.",
        "Table 1 (Baseline characteristics); Methods; Results"),
}

readings["stacchiotti2013anthracycline"] = {
    "surgical_margin_distribution": (E,
        "Table 2 'Patient clinical characteristics and response evaluation' was returned in full -- "
        "all 11 patient rows, all columns -- and has no margin column. The columns as printed are: "
        "Patient ID | Gender | Age | Diagnosis | NR4A3 rearrangement | Site of primary tumor | "
        "Staging at time of initial diagnosis | Site of relapse at the time of chemotherapy | RECIST "
        "evaluation | PFS. The only resection-quality wording in the paper is 'macroscopic complete "
        "surgery' / 'complete surgical resection', and it describes the POST-chemotherapy resection "
        "of 3 patients, not the primary operation, on no margin scale.",
        "Table 2; Results; Results/Response"),
    "margin_definition_printed": (E,
        "No R0/R1/R2 scale and no margin definition anywhere in the abstract, narrative or Tables "
        "1-3.", "abstract; Methods; Results; Tables 1-3"),
    "stage_at_diagnosis_split": (R,
        "Table 2 prints it PER PATIENT under 'Staging at time of initial diagnosis': localized "
        "disease for patients 1,2,4,5,6,9,10 (7) and 'local + lung' for patients 3,7,8,11 (4). "
        "7 + 4 = 11. ⚠ A two-level split of an already-advanced salvage cohort; it is not the "
        "localized/metastatic-at-diagnosis split the population series print.",
        "Table 2 (Patient clinical characteristics and response evaluation)"),
    "primary_site_distribution": (R,
        "Table 2 prints it PER PATIENT under 'Site of primary tumor': thigh 5 (patients 1,2,3,6,9), "
        "leg 3 (4,5,10), buttock 1 (7), arm 1 (8), sacrum 1 (11). 5+3+1+1+1 = 11. Consistent with "
        "the paper's own abstract summary 'site of primary: lower limb/other = 9/2' (thigh 5 + leg 3 "
        "+ buttock 1 = 9 lower limb; arm 1 + sacrum 1 = 2 other) and with the narrative 'primary "
        "arising from soft tissue/bone 10/1'.",
        "Table 2 (Patient clinical characteristics and response evaluation); abstract; Results"),
    "median_follow_up": (R,
        "Results/Response: 'At a median follow-up of 30 months, the estimated OS at 10-year was 50%, "
        "with 2 patients dead at the time of the present analysis and one lost to follow-up.' ⚠ "
        "n = 11, and time zero is the start of anthracycline chemotherapy for advanced disease, not "
        "diagnosis. Not interchangeable with any from-diagnosis median.",
        "Results / Response"),
    "time_to_event_median": (R,
        "Results/Response: 'Median OS was 30 months (range 10 mos-13 years)' and 'The median PFS for "
        "the entire group was 8 months (range 2-10), with 50% patients progression-free at 6 "
        "months'. ⚠ From the start of chemotherapy in advanced disease; n = 11.",
        "Results / Response"),
    "fitted_cox_coefficients": (E,
        "Statistical analysis prints Kaplan-Meier estimation and censoring rules only: 'Progression-"
        "free survival (PFS) and overall survival (OS) were estimated with Kaplan-Meyer method'. No "
        "regression model, no hazard ratio and no fitted coefficient appears in the paper.",
        "Methods / Statistical analysis; Results; Tables 1-3"),
    "numbers_at_risk_row": (None,
        "UNCHANGED from v2 (REPORTED, on the authority of "
        "research/literature/emc-km-admissibility-2026-08-27.json, which examined the figure "
        "itself). ⚠ THIS LANE DID NOT SEE IT: Figure 2 is the Kaplan-Meier PFS curve and only its "
        "legend came through this route ('Median PFS 8 months') -- the figure IMAGE, and therefore "
        "any risk row beneath it, was not returned. This lane neither confirms nor disturbs the v2 "
        "status. ⛔ No curve was digitised; the closed KM/IPD pilot is not reopened.",
        "figure legend 2 only -- image not returned"),
    "treatment_setting_or_referral": (R,
        "Reported as a COHORT-LEVEL CONSTANT, not per patient. Methods/Patients selection: patients "
        "were 'treated with anthracycline-based chemotherapy at Fondazione IRCCS Istituto Nazionale "
        "Tumori, Milano and those included in the data-base of the Italian Rare Cancer Network, "
        "registered by other Italian institutions'. ⚠ That names two strata -- the Milan institute "
        "and other Italian institutions reporting through the network -- but Table 2 was returned in "
        "full and carries NO institution column, so no patient is attributable to either. The "
        "Discussion treats the network as a case-collection instrument ('rare cancer networks "
        "represent a valuable tool in order to collect case series'), not as an exposure.",
        "Methods / Patients selection; Table 2; Discussion"),
    "unplanned_excision_defined": (E,
        "Not printed, and Table 2 -- the per-patient baseline table -- was returned in full. The "
        "words 'unplanned', 'inadvertent' and 'whoops' appear nowhere in the abstract, narrative or "
        "Tables 1-3. ⭐ The omission is visible in the table's own structure: Table 2 runs straight "
        "from 'Staging at time of initial diagnosis' to 'Site of relapse at the time of "
        "chemotherapy', so the primary surgical episode that each of the 7 patients staged "
        "'localized disease' must have had is never described -- not its margin, not its planning, "
        "not where it happened. ⚠ Unlike martinbroto2020immunosarc1, this is a RETROSPECTIVE series "
        "of patients whose primary treatment its own institutions may well have recorded, so the "
        "absence here is closer to a reporting choice than to a design-inherent one -- but it is "
        "still only an absence in the paper, and this lane makes no claim about what its source "
        "records hold.",
        "Table 2; Methods; Results; Discussion"),
}

readings["morioka2016trabectedin"] = {
    "median_follow_up": (R,
        "Results: 'Median follow-up time of the randomized phase 2 study was 22.7 months, and 1 "
        "subject with MCS was still receiving treatment at the final data cutoff.' ⚠ THIS IS THE "
        "WHOLE 73-SUBJECT PHASE 2 STUDY, not the 5-subject EMCS+MCS subset and not the 2 EMC "
        "subjects. No subset-specific follow-up is printed in the narrative.", "Results"),
    "time_to_event_median": (R,
        "Results: 'The median PFS of the subjects with EMCS and MCS was 12.5 months (95 % CI: "
        "7.4-not reached) in the trabectedin group' and 'Median overall survival (OS) of EMCS and "
        "MCS subjects in the trabectedin group was 26.4 months (range, 10.4-26.4 months)'. ⚠ These "
        "MIX 2 EMC subjects with 3 mesenchymal-chondrosarcoma subjects -- a different disease. "
        "There is no EMC-only time-to-event median in the narrative.", "Results"),
}

# elements left UNKNOWN for morioka, with the reason
MORIOKA_UNKNOWN = (
    "STILL NOT_EXAMINED. The PMC response for this paper returned the NARRATIVE ONLY: all tables "
    "and all figure legends were dropped, and the in-text pointer to the table that would carry "
    "this element comes through as bare punctuation ('Clinical information of these subjects is "
    "presented in Table.'). ⛔ This lane therefore asserts NO absence for this element. A retrieval "
    "limit is not a reporting absence. What is now recorded, and was not before, is that the "
    "narrative alone does not print it -- which is a statement about this retrieval, not about the "
    "paper.")

for el in ["surgical_margin_distribution", "margin_definition_printed", "stage_at_diagnosis_split",
           "primary_site_distribution", "fitted_cox_coefficients", "treatment_setting_or_referral",
           "unplanned_excision_defined"]:
    readings["morioka2016trabectedin"][el] = (N, MORIOKA_UNKNOWN, "narrative only")

# ---------------------------------------------------------------- apply
cm = d["coverage_matrix"]
changed = []
for sid in NEW:
    row = cm[sid]
    v1_verdict = row.get("retrieval_verdict")
    row["retrieval_verdict"] = ("RETRIEVED AND READ by CARE-DELIVERY-3 (PMC full text via PubMed "
                                "MCP); v2 verdict was: %s" % v1_verdict)
    row["retrieval_completeness"] = COMPLETENESS[sid]
    for el, spec in readings[sid].items():
        status, evidence, section = spec
        cell = row["elements"][el]
        v2_status = cell.get("status")
        if status is None:                       # numbers_at_risk_row for stacchiotti: keep v2
            cell["⚠_care_delivery_3_note"] = evidence
            cell["read_scope_care_delivery_3"] = section
            continue
        if v2_status != status:
            changed.append((sid, el, v2_status, status))
        cell["status"] = status
        cell["evidence"] = evidence
        cell["read_section"] = section
        cell["v2_status"] = v2_status
        cell["read_by"] = "CARE-DELIVERY-3"

# EMC dilution note, per series
cm["martinbroto2020immunosarc1"]["⚠_n_is_a_trial_denominator_not_an_emc_denominator"] = (
    "n = 68 counts the whole all-histology STS trial (16 phase Ib + 52 phase II). Table 1 "
    "'Diagnosis (central)' prints 'Extraskeletal myxoid chondrosarcoma 0 [phase Ib] 4 (7) [phase "
    "II]' -- FOUR EMC PATIENTS. Every element marked REPORTED for this series is a whole-trial "
    "value covering 12+ histologies, and the ONLY EMC-specific statement in the paper is 'partial "
    "response in patients diagnosed with ... extraskeletal myxoid chondrosarcoma (n=1)'. ⛔ None of "
    "these values may be placed in an EMC element pool.")
cm["morioka2016trabectedin"]["⚠_n_is_not_an_emc_denominator"] = (
    "n = 5 counts the trabectedin arm's EMCS+MCS subjects: 'we adopted two EMCS subjects and three "
    "MCS subjects who had been allocated to the trabectedin group'. ONLY 2 HAVE EMC; the other 3 "
    "have mesenchymal chondrosarcoma, a different disease. Every value marked REPORTED for this "
    "series mixes the two. ⛔ Not placeable in an EMC element pool.")
cm["stacchiotti2013anthracycline"]["✔_n_is_a_pure_emc_denominator"] = (
    "n = 11, all EMC, all NR4A3-rearrangement-confirmed: 'Cases with a morphology consistent with "
    "EMC but without the evidence of [NR4A3] rearrangement were excluded from this series.' This is "
    "the only one of the three trial-treated series whose denominator is entirely EMC. ⚠ It is "
    "nevertheless a salvage cohort of advanced, progressing disease, not a population series.")

# ---------------------------------------------------------------- recompute counts
N_BY_SERIES = {sid: cm[sid]["n"] for sid in cm}
counts = {}
for el in d["element_counts"]:
    buckets = {"REPORTED": [], "EXAMINED_NOT_PRINTED": [], "NOT_EXAMINED": []}
    for sid, row in cm.items():
        st = row["elements"][el].get("status")
        if st is None:
            print("FATAL: %s/%s has no status" % (sid, el), file=sys.stderr); sys.exit(2)
        buckets[st].append(sid)
    counts[el] = {b: {"n_series": len(s), "series": s,
                      "patients": sum(N_BY_SERIES[x] for x in s)}
                  for b, s in buckets.items()}
d["element_counts"] = counts
d["elements_reported_by_two_or_more_series"] = {
    el: counts[el]["REPORTED"]["series"] for el in counts
    if counts[el]["REPORTED"]["n_series"] >= 2}

# ---------------------------------------------------------------- headers
d["_what"] = ("CARE-DELIVERY-3 v3 of the care-delivery data-element coverage matrix: v2 with the "
              "THREE systemic-therapy trial series (martinbroto2020immunosarc1, "
              "stacchiotti2013anthracycline, morioka2016trabectedin) replaced by an ACTUAL READING "
              "of their PMC full texts, each row carrying its own retrieval_completeness because "
              "the three retrievals returned materially different amounts of the paper.")
d["_lane"] = ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
              "PORTFOLIO-INVESTIGATIONS-2026-09-08/CARE-DELIVERY-3")
d["_generated_by"] = "build_v3.py (this lane)"
d["_supersedes"] = ("…/CARE-DELIVERY-2/care-delivery-element-coverage-v2.json for the three trial "
                    "rows only. That file is another lane's artifact and was READ, NOT WRITTEN. The "
                    "bishop2019 and drilon2008 rows are carried through from v2 unchanged and were "
                    "NOT re-read here.")
d["_reads_only"] = [
    "…/CARE-DELIVERY-2/care-delivery-element-coverage-v2.json",
    "three PMC full texts retrieved in session (see checks/01-, 02-, 03-)"]
d["_source_attribution"] = (
    "Full texts retrieved from PubMed Central through the PubMed MCP server, 2026-09-09. "
    "martinbroto2020immunosarc1 DOI https://doi.org/10.1136/jitc-2020-001561 ; "
    "stacchiotti2013anthracycline DOI https://doi.org/10.1186/2045-3329-3-16 ; "
    "morioka2016trabectedin DOI https://doi.org/10.1186/s12885-016-2511-y . Carried through from "
    "v2: bishop2019 DOI https://doi.org/10.1097/COC.0000000000000590 ; drilon2008 DOI "
    "https://doi.org/10.1002/cncr.23978")
d["_read_scope"] = (
    "⚠ RETRIEVAL COMPLETENESS IS NOT UNIFORM AND IS RECORDED PER SERIES in each row's "
    "`retrieval_completeness`. v2 could state one global caveat because both of its retrievals came "
    "back narrative-only; v3 cannot. Of this lane's three: martinbroto2020immunosarc1 and "
    "stacchiotti2013anthracycline returned ALL TABLES and figure legends, so their "
    "EXAMINED_NOT_PRINTED verdicts rest on having read the baseline tables; "
    "morioka2016trabectedin returned the NARRATIVE ONLY, so NOTHING moves to EXAMINED_NOT_PRINTED "
    "for it and every element that could live in its dropped table stays NOT_EXAMINED. ⛔ A "
    "retrieval limit is never recorded as a reporting absence.")
d["series_newly_read_by_this_lane"] = NEW
d["series_read_across_v2_and_v3"] = ["bishop2019", "drilon2008"] + NEW
d["_v2_input_sha256"] = hashlib.sha256(v2_bytes.encode("utf-8")).hexdigest()
d["_status_changes_made_by_v3"] = [
    {"series": s, "element": e, "from": a, "to": b} for (s, e, a, b) in changed]

# ---------------------------------------------------------------- the audit, at v3
d["absence_claim_denominator_audit_v3"] = {
  "claim_under_test": ("emc-surgical-quality.json: treatment_setting.recorded_in_any_reachable_"
                       "series == false and unplanned_excision.recorded_in_any_reachable_series "
                       "== false"),
  "v2_verdict": {
    "treatment_setting": "FALSE -- refuted by bishop2019, which reports it per patient",
    "unplanned_excision": "CONFIRMED at four examined series (masunaga2025, chiusole2020, "
                          "bishop2019, drilon2008); still a claim about an examined set",
    "residue": "three systemic-therapy trial series UNKNOWN for both fields"},
  "v3_verdict": {
    "treatment_setting": {
      "verdict": "UNCHANGED -- still FALSE. Nothing in this lane could have rescued it and nothing "
                 "did. One refuting series is enough; three more were read and none of them "
                 "reports the field per patient either.",
      "what_v3_adds": "The examined set for this field rises from 4 series to 6. All three trial "
                      "series print treatment setting as a COHORT-LEVEL CONSTANT: "
                      "martinbroto2020immunosarc1 'enrolled in eight centers in Spain and Italy "
                      "with expertise in sarcoma care'; stacchiotti2013anthracycline 'at "
                      "Fondazione IRCCS Istituto Nazionale Tumori, Milano and those included in "
                      "the data-base of the Italian Rare Cancer Network'; "
                      "morioka2016trabectedin 'approved by the institutional review board at each "
                      "institution' (institutions unnamed). ⭐ The structural finding is now sharp: "
                      "of 6 examined series, FIVE hold the setting constant or omit it and exactly "
                      "ONE (bishop2019) resolves it per patient.",
      "series_examined_after_v3": ["masunaga2025", "chiusole2020", "bishop2019", "drilon2008",
                                   "martinbroto2020immunosarc1", "stacchiotti2013anthracycline"],
      "⚠_morioka_excluded_from_the_examined_set": "morioka2016trabectedin's tables were not "
                                                  "returned; it stays UNKNOWN, not absent."},
    "unplanned_excision": {
      "verdict": "CONFIRMED AT A WIDER DENOMINATOR AGAIN -- six examined series, not four. Still a "
                 "claim about the examined set, never about every reachable series.",
      "what_v3_adds": "Two more series examined INCLUDING THEIR BASELINE TABLES. "
                      "martinbroto2020immunosarc1's Table 1 and stacchiotti2013anthracycline's "
                      "per-patient Table 2 both came back in full and neither defines, names or "
                      "counts an unplanned, inadvertent or prior excision. No new proxy was found: "
                      "bishop2019's 14/41 outside excisions with the margin at referral remains the "
                      "best available proxy, and it is still only a proxy.",
      "⭐_and_the_reason_differs_by_series_type": (
          "For martinbroto2020immunosarc1 the absence is DESIGN-INHERENT, not a curation gap: the "
          "protocol enrols advanced STS progressing within 6 months, and its baseline set records "
          "prior SYSTEMIC exposure ('Median previous lines', 'Previous antiangiogenic lines') and "
          "resectability at diagnosis. The quality of a prior local excision is not a variable a "
          "second-line systemic-therapy trial collects. For stacchiotti2013anthracycline -- a "
          "RETROSPECTIVE institutional/network series whose Table 2 runs straight from 'Staging at "
          "time of initial diagnosis' to 'Site of relapse at the time of chemotherapy' -- the "
          "absence is closer to a reporting choice, and its 7 patients staged 'localized disease' "
          "each had a primary operation the paper never describes."),
      "series_examined_after_v3": ["masunaga2025", "chiusole2020", "bishop2019", "drilon2008",
                                   "martinbroto2020immunosarc1", "stacchiotti2013anthracycline"],
      "⚠_morioka_excluded_from_the_examined_set": "morioka2016trabectedin's tables were not "
                                                  "returned; it stays UNKNOWN, not absent."},
    "residue_after_v3": {
      "for_both_fields": ["morioka2016trabectedin (tables not returned by this route)"],
      "plus_the_11_series_never_retrieved": ("seer270_2022, meisKindblom1999, ussc2022, huang2023, "
                                             "uMich2023, japan2003, china2016, "
                                             "stacchiotti2019pazopanib, immunosarc2emc2025, "
                                             "stacchiotti2014sunitinib, and any series outside the "
                                             "17-series candidate list"),
      "⛔": "For all of these every element is UNKNOWN. Neither absence claim is a statement about "
           "them."}},
  "⛔_what_none_of_this_shows": ("No association between treatment setting, referral, excision "
                                "planning and any EMC outcome is asserted here or anywhere in the "
                                "proposed diff. No clinical, efficacy or safety claim is made. "
                                "Recording a field is not measuring an effect.")}

d["⭐_what_the_trial_series_can_and_cannot_contribute"] = {
  "the_finding": ("The three systemic-therapy trial series are NOT a curation gap for the "
                  "care-delivery elements -- for two of the three the fields are genuinely absent "
                  "by design, and the reading proves it against their full baseline tables rather "
                  "than inferring it from silence. But neither are they a source of poolable EMC "
                  "values, for a reason that is separate from field coverage: their DENOMINATORS "
                  "ARE NOT EMC."),
  "denominators": {
    "martinbroto2020immunosarc1": "n = 68 in this matrix is the whole all-histology STS trial; "
                                  "4 patients have EMC (Table 1, 'Diagnosis (central)').",
    "morioka2016trabectedin": "n = 5 is the trabectedin EMCS+MCS arm; 2 have EMC, 3 have "
                              "mesenchymal chondrosarcoma.",
    "stacchiotti2013anthracycline": "n = 11 is entirely EMC, all NR4A3-confirmed -- the only one of "
                                    "the three with a pure EMC denominator."},
  "⛔_consequence": ("Every element newly marked REPORTED for martinbroto2020immunosarc1 and "
                    "morioka2016trabectedin is a value for a mixed-histology population. The "
                    "matrix's `candidate_patients_sum` of 1,133 is a WEIGHTING DEVICE over "
                    "candidate series, and this lane's reading shows it also over-counts EMC "
                    "patients for a second, independent reason beyond the overlap already recorded. "
                    "No count in this artifact was altered to reflect that; it is recorded as a "
                    "caveat so no later session reads 1,133 as an EMC patient count."),
  "✔_what_they_do_contribute": ("Three more series examined for the absence-claim audit, two of "
                                "them with complete baseline tables; a design-based rather than "
                                "silence-based explanation for why the surgical-quality fields are "
                                "missing from trial reports; and one clean per-patient EMC site and "
                                "stage table (stacchiotti2013anthracycline, n = 11).")}

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

print("wrote %s" % OUT)
print("status changes made by v3: %d" % len(changed))
for c in changed:
    print("   %-30s %-32s %s -> %s" % c)
