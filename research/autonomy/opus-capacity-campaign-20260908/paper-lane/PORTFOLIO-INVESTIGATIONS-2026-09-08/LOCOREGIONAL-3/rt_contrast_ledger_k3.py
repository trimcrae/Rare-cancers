#!/usr/bin/env python3
"""LOCOREGIONAL-3 -- build rt-local-control-contrast-ledger-k3.json.

k=2 -> k=3 was ATTEMPTED and NOT ACHIEVED. This script:

  1. GATE. Loads the LOCOREGIONAL-2 ledger and re-derives the k=2 rows BYTE FOR BYTE
     (canonical JSON of `arm_level_event_ledger`, `per_series_2x2_reported_as_sizes` and
     `crude_pooled_per_arm_proportions` must equal the bytes in the committed k2 file).
     If they do not match, the script exits non-zero and writes nothing.
  2. Re-runs the FOUR internal arithmetic consistency checks from printed integers.
  3. Emits the k=3 ledger: k UNCHANGED at 2, with a per-candidate record of why.

⛔ No clinical efficacy, safety, selectivity, therapeutic-window, prognosis or treatment
recommendation is asserted anywhere in this artifact. It is a curation ledger.

Usage:  python3 rt_contrast_ledger_k3.py [--check]
        --check re-derives and compares byte-for-byte against the committed artifact.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
K2 = os.path.normpath(os.path.join(HERE, "..", "LOCOREGIONAL-2",
                                   "rt-local-control-contrast-ledger-k2.json"))
OUT = os.path.join(HERE, "rt-local-control-contrast-ledger-k3.json")

CARRIED = ["arm_level_event_ledger",
           "per_series_2x2_reported_as_sizes",
           "crude_pooled_per_arm_proportions"]


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def gate(k2):
    """The k=2 rows must re-derive byte for byte before any new row is added."""
    # Re-derive the carried blocks from the committed file's own raw text, then compare
    # canonical bytes. Any in-memory mutation of a carried row breaks this.
    raw = json.loads(open(K2, "rb").read().decode())
    report = {}
    for key in CARRIED:
        a, b = canon(k2[key]), canon(raw[key])
        report[key] = {"bytes": len(a), "byte_for_byte_identical_to_k2_file": a == b}
        if a != b:
            return False, report
    return True, report


def consistency(k2):
    """The four internal arithmetic checks, recomputed from PRINTED integers."""
    rows = {r["source_id"]: r for r in k2["arm_level_event_ledger"]}
    m, b = rows["masunaga2025"], rows["bishop2019"]
    ms, me = m["arm_sizes"], m["arm_events"]
    bs, be = b["arm_sizes"], b["arm_events"]
    # masunaga2025 uses its own printed arm labels; bishop2019 uses surgery_plus_RT/alone.
    mrt, mno = "neoadjuvant_or_adjuvant_RT", "no_perioperative_RT"
    c = {}
    c["1_masunaga_arm_events_sum_equals_printed_total_16"] = (
        me[mrt] + me[mno] == m["events_total_printed"] == 16)
    c["2_masunaga_arm_sizes_sum_equals_analysed_cohort_134"] = (
        ms[mrt] + ms[mno] == 134)
    c["3_masunaga_printed_percentages_match_printed_integers"] = (
        round(100 * me[mrt] / ms[mrt], 1) == 8.3 and
        round(100 * me[mno] / ms[mno], 1) == 12.7 and
        round(100 * (me[mrt] + me[mno]) / 134, 1) == 11.9)
    c["4_bishop_arm_events_and_sizes_sum_to_printed_5_and_41"] = (
        be["surgery_plus_RT"] + be["surgery_alone"] == b["events_total_printed"] == 5 and
        bs["surgery_plus_RT"] + bs["surgery_alone"] == 41)
    c["all_green"] = all(v for k, v in c.items() if k != "all_green")
    return c


def build():
    k2 = json.loads(open(K2, "rb").read().decode())
    ok, gate_report = gate(k2)
    if not ok:
        sys.stderr.write("GATE FAILED: k=2 rows did not re-derive byte for byte.\n"
                         + json.dumps(gate_report, indent=2) + "\n")
        sys.exit(2)
    cons = consistency(k2)
    if not cons["all_green"]:
        sys.stderr.write("GATE FAILED: internal arithmetic consistency checks not green.\n"
                         + json.dumps(cons, indent=2) + "\n")
        sys.exit(3)

    led = {
      "_id": "LOCOREGIONAL-3-RT-CONTRAST-LEDGER-K3-2026-09-09",
      "_continues": "LOCOREGIONAL-2-RT-CONTRAST-LEDGER-K2-2026-09-09",
      "_question": ("Which primary reports the 1/10 vs 7/17 multicenter local-recurrence "
                    "split quoted in masunaga2025's Discussion, and do bishop2019's 1/33 "
                    "and 4/8 hold at source?"),
      "_answer": ("SPLIT ANSWER. (a) bishop2019 HOLDS AT SOURCE and its transcription is now "
                  "FIRST-HAND. (b) The multicenter primary is IDENTIFIED ON DESCRIPTOR as "
                  "Paioli 2020 (Italian Sarcoma Group), but its per-arm counts are NOT IN THE "
                  "ABSTRACT and it has no PubMed Central full text, so the 1/10 vs 7/17 split "
                  "CANNOT be verified through the admitted route. k STAYS AT 2. The ledger is "
                  "explicitly NOT EXTENDED."),
      "_direction_of_evidence_carried_forward": (
          "LOCOREGIONAL-2 moved k from 1 to 2 and that move WEAKENED the radiotherapy case: "
          "the larger of the two series reports 8.3% (2/24) vs 12.7% (14/110), p = 0.74, with "
          "the measured confounding running AGAINST radiotherapy (41.7% vs 18.2% R1/R2 margins "
          "in the irradiated arm). This lane adds no series and does not soften that. Nothing "
          "here is framed as strengthening a case the second series weakened."),
      "_not_medical_advice": ("No claim is made or supported here that radiotherapy does, or "
                              "does not, improve local control in extraskeletal myxoid "
                              "chondrosarcoma. No efficacy, safety, selectivity, "
                              "therapeutic-window, prognosis or treatment-recommendation claim; "
                              "no patient-specific advice. This is a curation ledger, not a "
                              "treatment comparison."),

      "k_counted_event_series": {
        "before_this_lane": 2, "after_this_lane": 2, "moved": False,
        "why_not_moved": ("The only candidate third series with printed per-arm integers is "
                          "unverifiable at source through the admitted route.")
      },

      "gate": {
        "rule": ("--check must re-derive the k=2 rows BYTE FOR BYTE before any new row is "
                 "added, and the four internal arithmetic consistency checks must stay green."),
        "k2_source_file": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                           "PORTFOLIO-INVESTIGATIONS-2026-09-08/LOCOREGIONAL-2/"
                           "rt-local-control-contrast-ledger-k2.json"),
        "k2_own_check_path_rerun_here": ("python3 ../LOCOREGIONAL-2/rt_contrast_ledger_k2.py "
                                         "--check -> 'CHECK MATCH', exit 0 "
                                         "(checks/01-gate-k2-check/)"),
        "carried_blocks_byte_identity": gate_report,
        "four_internal_arithmetic_consistency_checks": cons,
        "gate_status": "GREEN -- and no new row was added anyway"
      },

      "candidate_1_bishop2019_reverification": {
        "goal": ("LOCOREGIONAL-2 limitation: bishop2019's 1/33 and 4/8 were second-hand, "
                 "transcribed from emc-radiotherapy-contradiction.json and never re-read."),
        "outcome": "VERIFIED AT SOURCE. Transcription upgraded second-hand -> FIRST-HAND.",
        "retrieval": {
          "route": "PubMed / PubMed Central MCP (mcp__PubMed__convert_article_ids, "
                   "mcp__PubMed__get_full_text_article)",
          "pmid": "31436747", "pmcid": "PMC7771031",
          "doi": "10.1097/COC.0000000000000590",
          "doi_url": "https://doi.org/10.1097/COC.0000000000000590",
          "citation": "Bishop AJ, Bird JE, Conley AP, et al. Extraskeletal Myxoid "
                      "Chondrosarcomas: Combined Modality Therapy With Both Radiation and "
                      "Surgery Improves Local Control. Am J Clin Oncol 2019;42(10):744-748.",
          "retrieved": "2026-09-09",
          "attribution_required_by_tool": ("Information from this article is retrieved from "
                                           "PubMed and must be cited to PubMed with the DOI."),
          "no_direct_http_fetch_attempted": True,
          "check_record": "checks/03-mcp-convert-doi-bishop2019/, "
                          "checks/05-mcp-fulltext-PMC7771031-bishop2019/"
        },
        "verbatim_arm_sizes": ("\"The majority of patients (n=33, 80%) received combined "
                               "modality local therapy with both surgery and RT, whereas 8 "
                               "patients received surgery alone (20%).\""),
        "verbatim_arm_events": ("\"There were 5 patients (12%) with local relapse at a median "
                                "time of 75 months (range 13-176 months). Four of those "
                                "patients underwent surgery alone. The median time to local "
                                "relapse occurred earlier in patients receiving surgery alone "
                                "compared to the one patient who received CMT (61 months vs. "
                                "143 months).\""),
        "how_each_integer_is_known": {
          "surgery_alone_n_8": "printed integer",
          "surgery_plus_RT_n_33": "printed integer",
          "surgery_alone_events_4": "printed as the word \"Four\"",
          "surgery_plus_RT_events_1": ("printed TWICE and independently: (i) 5 total local "
                                       "relapses minus the four in the surgery-alone arm; "
                                       "(ii) the words \"the one patient who received CMT\". "
                                       "Arithmetic on printed integers only -- no count is "
                                       "reconstructed from a hazard ratio, a percentage, a "
                                       "p-value, a confidence interval or a KM curve."),
          "total_events_5": "printed integer", "cohort_n_41": "printed integer"
        },
        "k2_values_reproduced_exactly": {"surgery_plus_RT": "1/33", "surgery_alone": "4/8",
                                         "match": True},
        "corrections_to_k2": "NONE. No figure in the k=2 ledger changes.",
        "newly_confirmed_at_source_caveat": (
          "The paper's own headline is \"10-year LC 63% vs. 100% in patients receiving "
          "combined modality therapy\" while the SAME paper counts one local relapse in the "
          "combined-modality arm at 143 months. 100% is a censored-horizon actuarial "
          "statement, not zero relapses. LOCOREGIONAL-2 recorded this caveat second-hand; it "
          "is now confirmed at source."),
        "cohort_confirmation_basis_at_source": (
          "\"41 consecutive patients with localized, non-metastatic histologically confirmed "
          "EMC\" -- HISTOLOGICALLY confirmed. The article states no molecular confirmation. "
          "This is recorded because the unresolved third series is described as MOLECULARLY "
          "confirmed; the two cohorts are not defined the same way."),
        "overlap_status_unchanged": ("bishop2019 keeps registry pool:false for "
                                     "population-overlap with SEER / the US Sarcoma "
                                     "Collaborative. This lane changed no registry pool flag.")
      },

      "candidate_2_the_multicenter_1_10_vs_7_17_split": {
        "the_lead_as_quoted_in_masunaga2025": (
          "Discussion, \"Localized extraskeletal myxoid chondrosarcoma\": \"Another multicenter "
          "retrospective study involving only localized and molecularly confirmed cases showed "
          "a trend toward better local control in the group that underwent surgery and "
          "(neo)adjuvant radiotherapy than in the surgery-alone group (local recurrence rate: "
          "1/10 (10%) vs. 7/17 (41%), = 0.08) [].\" -- reference number stripped by the "
          "full-text extraction (LOCOREGIONAL-2 checks/01)."),
        "outcome": "NOT ADMITTED. k is NOT raised. The ledger is NOT extended.",
        "best_descriptor_match_identified": {
          "citation": ("Paioli A, Stacchiotti S, Campanacci D, et al. Extraskeletal Myxoid "
                       "Chondrosarcoma with Molecularly Confirmed Diagnosis: A Multicenter "
                       "Retrospective Study Within the Italian Sarcoma Group. Ann Surg Oncol "
                       "2020;28(2):1142-1150."),
          "pmid": "32572850", "pmcid": None, "doi": "10.1245/s10434-020-08737-7",
          "doi_url": "https://doi.org/10.1245/s10434-020-08737-7",
          "why_it_matches_the_descriptor": [
            "title carries \"Molecularly Confirmed Diagnosis: A Multicenter Retrospective Study\"",
            "abstract VERBATIM: \"a retrospective pooled analysis of patients with EMC treated "
            "at three Italian Sarcoma Group (ISG) referral centers was carried out.\"",
            "abstract VERBATIM: \"All patients with localized EMC surgically treated from 1989 "
            "to 2016 were identified.\"",
            "abstract VERBATIM: \"Only patients with NR4A3 rearrangement were included.\"",
            "PubMed article_types include \"Multicenter Study\"",
            "published 2020, i.e. available to be cited by masunaga2025 (2025)"
          ],
          "identification_confidence": "DESCRIPTOR MATCH ONLY, NOT CONFIRMED.",
          "what_would_confirm_it": ("masunaga2025's numbered reference list, which the PMC "
                                    "full-text extraction strips (the same tool returned no "
                                    "reference list for bishop2019 either), or Paioli 2020's "
                                    "own text showing a 10 vs 17 radiotherapy split.")
        },
        "why_the_counts_are_not_admitted": [
          {"reason": "NO FULL TEXT THROUGH THE ADMITTED ROUTE",
           "detail": ("mcp__PubMed__convert_article_ids(pmid 32572850) returns no pmcid, and "
                      "mcp__PubMed__find_related_articles(link_type='pubmed_pmc') returns an "
                      "EMPTY linkset. Paioli 2020 is not in PubMed Central."),
           "check_record": "checks/06-mcp-convert-pmid-32572850-paioli/, "
                           "checks/11-mcp-related-pmc-32572850-paioli/"},
          {"reason": "THE SPLIT IS NOT IN THE ABSTRACT",
           "detail": ("The retrieved abstract contains no 1/10, no 7/17 and no p = 0.08, and "
                      "reports no radiotherapy-stratified local-recurrence counts at all. "
                      "Stated precisely: NOT IN THE ABSTRACT. This lane does NOT claim the "
                      "counts are absent from the paper -- the paper's body was never read."),
           "check_record": "checks/04-mcp-metadata-32572850-31436747/"},
          {"reason": "THE ARITHMETIC DOES NOT OBVIOUSLY RECONCILE",
           "detail": ("Paioli 2020's abstract prints 67 localized patients and, VERBATIM, "
                      "\"Thirty-five (52%) patients relapsed: 9 had local recurrence (LR) and "
                      "26 had distant metastasis (5 with concomitant LR)\" -- i.e. 14 patients "
                      "with local recurrence among 67. The quoted split is 8 local recurrences "
                      "among 27 (1/10 + 7/17). 27 != 67 and 8 != 14. A 27-patient "
                      "radiotherapy-status-known subgroup is CONCEIVABLE but is NOT EVIDENCED "
                      "by anything retrieved. This unreconciled arithmetic is recorded as a "
                      "reason for caution, not as a refutation."),
           "check_record": "checks/04-mcp-metadata-32572850-31436747/"},
          {"reason": "POLICY-evidence 1.3 -- SECONDARY PROVENANCE",
           "detail": ("A count read out of another paper's Discussion is not a primary read. "
                      "Admitting 1/10 vs 7/17 on masunaga2025's authority would be laundering "
                      "a citation. The k=2 refusal therefore stands unchanged.")}
        ],
        "prior_lane_guess_tested_and_refuted": {
          "guess": ("LOCOREGIONAL-2 sec.4 recorded, explicitly as a guess, that chiusole2020 "
                    "(European two-institution series) was a plausible candidate."),
          "verdict": "REFUTED AS THE DESCRIPTOR MATCH.",
          "evidence": ("Chiusole B, Le Cesne A, Rastrelli M, et al. Extraskeletal Myxoid "
                       "Chondrosarcoma: Clinical and Molecular Characteristics and Outcomes of "
                       "Patients Treated at Two Institutions. Front Oncol 2020;10:828, PMID "
                       "32612944, DOI 10.3389/fonc.2020.00828. Abstract VERBATIM: \"This is a "
                       "retrospective study conducted at Istituto Oncologico Veneto and at "
                       "Institut Gustave Roussy.\" / \"59 patients were identified\" / \"We "
                       "performed molecular analysis in 23 cases\" / \"Out of 49 patients "
                       "treated with curative intent, 28.6% developed local recurrence\". It is "
                       "TWO institutions, not \"only molecularly confirmed\" (23 of 59), and "
                       "its local-recurrence figure is a percentage on a denominator of 49."),
          "check_record": "checks/09-mcp-search-two-institutions/, "
                          "checks/10-mcp-metadata-33308312-32612944/"
        },
        "other_candidates_searched_and_excluded": [
          {"pmid": "31331701",
           "citation": "Stacchiotti S, et al. Pazopanib for treatment of advanced "
                       "extraskeletal myxoid chondrosarcoma: a multicentre, single-arm, phase "
                       "2 trial. Lancet Oncol 2019;20(9):1252-1262.",
           "doi": "10.1016/S1470-2045(19)30319-5",
           "excluded_because": "advanced/metastatic or unresectable disease, not localized; a "
                               "pazopanib trial, not a surgery+RT local-control series."},
          {"pmid": "42465974",
           "citation": "Chaiboonchoe A, et al. Prognostic biomarkers for enhanced risk "
                       "stratification in extraskeletal myxoid chondrosarcoma: a retrospective "
                       "cohort study. PeerJ 2026;14:e21497.",
           "doi": "10.7717/peerj.21497",
           "excluded_because": "12-case transcriptomic biomarker study, and published 2026 -- "
                               "AFTER masunaga2025, so it cannot be its reference."},
          {"pmid": "33308312",
           "citation": "Improta L, et al. Locally recurrent extraskeletal myxoid "
                       "chondrosarcoma of the shoulder: a case of complete neoadjuvant "
                       "radiotherapy response. Clin Sarcoma Res 2020;10(1):27.",
           "doi": "10.1186/s13569-020-00150-8",
           "excluded_because": "single case report."}
        ],
        "overlap_flag_if_it_were_ever_admitted": (
          "OVERLAP-UNKNOWN. Paioli 2020 draws on three Italian Sarcoma Group referral centres "
          "over 1989-2016; chiusole2020 (Istituto Oncologico Veneto + Institut Gustave Roussy, "
          "1980-2018) and the ISG-participating centres in Stacchiotti 2019 cover overlapping "
          "European sarcoma referral networks and overlapping calendar periods, and several "
          "authors are shared (Stacchiotti, Palmerini, Frezza, Gronchi, Le Cesne). No "
          "patient-level overlap has been established or excluded. Were this row ever "
          "admitted, it MUST be flagged overlap-unknown and MUST NOT be pooled with any other "
          "European series until non-overlap is demonstrated."),
        "k_if_ever_admitted_after_a_primary_read": 3
      },

      "what_this_lane_did_NOT_do": [
        "Did not add a third series to the pool.",
        "Did not recompute, restate or alter any k=2 pooled proportion, Wilson interval, "
        "Fisher p-value or fragility count.",
        "Did not compute any pooled odds ratio, risk ratio, hazard ratio, risk difference, "
        "cross-study p-value, I-squared or random-effects estimate.",
        "Did not attempt any direct HTTP fetch, publisher site, DOI resolver or paywalled "
        "route. The PubMed/PMC MCP server was the only route used.",
        "Did not reopen any closed route (B1/B2, B4, B8, B9) and did not target PMID 22592656.",
        "Did not edit anything outside this lane directory.",
        "Did not soften LOCOREGIONAL-2's finding that moving k from 1 to 2 weakened the "
        "radiotherapy case."
      ],

      "standing_status_unchanged": {
        "RT-RT-INTENSIFY": "REFUTED",
        "RT-METASTASECTOMY": "DO-NOT-WRITE",
        "note": "Nothing in this lane reopens either."
      },

      "residual_gap": (
        "The 1/10 vs 7/17 multicenter split remains a real, printed, directly reported per-arm "
        "count whose primary this lane identified only on descriptor and could not read. The "
        "remaining bounded step needs a route this campaign does not have: the reference list "
        "of PMC12398172 (stripped by the extraction tool) or the body of Ann Surg Oncol "
        "2020;28(2):1142-1150 (not in PubMed Central). Both are outside the admitted route."),

      "_inputs": {
        "k2_ledger": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                      "PORTFOLIO-INVESTIGATIONS-2026-09-08/LOCOREGIONAL-2/"
                      "rt-local-control-contrast-ledger-k2.json"),
        "k2_builder": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                       "PORTFOLIO-INVESTIGATIONS-2026-09-08/LOCOREGIONAL-2/"
                       "rt_contrast_ledger_k2.py"),
        "policy": "systems/POLICY-evidence.md",
        "new_primary_reads": ["PMC7771031 full text (bishop2019) -- PubMed/PMC MCP"],
        "abstract_only_reads": ["PMID 32572850 (Paioli 2020)", "PMID 32612944 (chiusole2020)",
                                "PMID 31331701", "PMID 42465974", "PMID 33308312"]
      },

      "_carried_forward_unchanged_from_k2": {k: k2[k] for k in CARRIED}
    }
    return json.dumps(led, indent=2, ensure_ascii=False) + "\n"


def main():
    text = build()
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            sys.stderr.write("CHECK FAILED: %s does not exist.\n" % OUT)
            sys.exit(1)
        have = open(OUT, "rb").read()
        if have == text.encode():
            print("CHECK MATCH: re-derived artifact is byte-identical to the committed one.")
            sys.exit(0)
        sys.stderr.write("CHECK MISMATCH: re-derived artifact differs.\n")
        sys.exit(1)
    with open(OUT, "wb") as fh:
        fh.write(text.encode())
    print("WROTE %s (%d bytes)" % (OUT, len(text.encode())))
    print("k before = 2 ; k after = 2 ; moved = False")


if __name__ == "__main__":
    main()
