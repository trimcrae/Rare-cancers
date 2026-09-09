#!/usr/bin/env python3
"""EXPOSURE-INDEX -- build emc-patient-exposure-index.json.

One row per cited series. Counts and provenance ONLY.
No pooling. No denominator arithmetic across overlap-unknown rows.
Reads only; writes only into this lane's directory.
"""
import hashlib
import json
import os
import sys

REPO = "/home/user/Rare-cancers"
LANES = os.path.join(
    REPO,
    "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
    "PORTFOLIO-INVESTIGATIONS-2026-09-08",
)
HERE = os.path.join(LANES, "EXPOSURE-INDEX")

SRC = {
    "ipd": "research/modalities/emc-ipd-survival.json",
    "cd3": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
            "PORTFOLIO-INVESTIGATIONS-2026-09-08/CARE-DELIVERY-3/"
            "care-delivery-element-coverage-v3.json"),
    "cd2": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
            "PORTFOLIO-INVESTIGATIONS-2026-09-08/CARE-DELIVERY-2/"
            "care-delivery-element-coverage-v2.json"),
    "loco": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
             "PORTFOLIO-INVESTIGATIONS-2026-09-08/LOCOREGIONAL-2/"
             "rt-local-control-contrast-ledger-k2.json"),
    "rep2": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
             "PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-2/"
             "CITED-REFERENCE-SWEEP.md"),
    "rep3": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
             "PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-3/"
             "FIVE-REFERENCE-TABLE.md"),
    "cabo": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
             "PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-REPURPOSING/"
             "EVIDENCE-cabozantinib-emc.md"),
    "ms_rep": "research/manuscripts/repurposing/repurposing-hypotheses.md",
}


def sha(rel):
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


ipd = json.load(open(os.path.join(REPO, SRC["ipd"])))
cd3 = json.load(open(os.path.join(REPO, SRC["cd3"])))
loco = json.load(open(os.path.join(REPO, SRC["loco"])))

ipd_by_id = {c["source_id"]: c for c in ipd["candidate_sources"]}

# ---------------------------------------------------------------- overlap
# A row is overlap_unknown TRUE unless a named source file states, in words,
# that its population is distinct from every other row in this index.
OVERLAP_CLEAR = {
    # source_id: (verdict, quoted justification, quoted_from)
    "masunaga2025": (
        False,
        '"none with institutional series"',
        SRC["ipd"] + " -> candidate_sources[masunaga2025].overlap_risk",
    ),
    "china2016": (False, '"none known"',
                  SRC["ipd"] + " -> candidate_sources[china2016].overlap_risk"),
    "huang2023": (False, '"none known"',
                  SRC["ipd"] + " -> candidate_sources[huang2023].overlap_risk"),
}

# EMC-specific denominators, each with the verbatim figure and its named file.
EMC_N = {
    "martinbroto2020immunosarc1": {
        "n_emc": 4,
        "quote": ('"n = 68 in this matrix is the whole all-histology STS trial; '
                  '4 patients have EMC (Table 1, \'Diagnosis (central)\')."'),
        "quoted_from": (SRC["cd3"] +
                        " -> ⭐_what_the_trial_series_can_and_cannot_contribute"
                        ".denominators.martinbroto2020immunosarc1"),
        "headline_is_not_emc": True,
    },
    "morioka2016trabectedin": {
        "n_emc": 2,
        "quote": ('"n = 5 is the trabectedin EMCS+MCS arm; 2 have EMC, '
                  '3 have mesenchymal chondrosarcoma."'),
        "quoted_from": (SRC["cd3"] +
                        " -> ⭐_what_the_trial_series_can_and_cannot_contribute"
                        ".denominators.morioka2016trabectedin"),
        "headline_is_not_emc": True,
    },
    "stacchiotti2013anthracycline": {
        "n_emc": 11,
        "quote": ('"n = 11 is entirely EMC, all NR4A3-confirmed -- the only one '
                  'of the three with a pure EMC denominator."'),
        "quoted_from": (SRC["cd3"] +
                        " -> ⭐_what_the_trial_series_can_and_cannot_contribute"
                        ".denominators.stacchiotti2013anthracycline"),
        "headline_is_not_emc": False,
    },
}

# retrieval_completeness, taken from the reading lane's own recorded verdict.
RETRIEVAL = {
    "martinbroto2020immunosarc1": (
        "complete",
        '"NARRATIVE + ALL TABLES + ALL FIGURE LEGENDS"',
        SRC["cd3"] + " -> coverage_matrix.martinbroto2020immunosarc1"
                     ".retrieval_completeness.verdict",
        "CARE-DELIVERY-3"),
    "stacchiotti2013anthracycline": (
        "complete",
        '"NARRATIVE + ALL THREE TABLES + FIGURE LEGENDS (the most complete of '
        'the three)"',
        SRC["cd3"] + " -> coverage_matrix.stacchiotti2013anthracycline"
                     ".retrieval_completeness.verdict",
        "CARE-DELIVERY-3"),
    "morioka2016trabectedin": (
        "partial",
        '"⚠ NARRATIVE ONLY -- NO TABLES, NO FIGURE LEGENDS (INCOMPLETE)"',
        SRC["cd3"] + " -> coverage_matrix.morioka2016trabectedin"
                     ".retrieval_completeness.verdict",
        "CARE-DELIVERY-3"),
}

ROWS = []


def row(**kw):
    ROWS.append(kw)


# ------------------------------------------------------- A. the 17 series
CITE_ALL17 = [
    {"paper": "PUB-IPD-SURVIVAL",
     "evidence": SRC["ipd"] + " -> candidate_sources[]"},
    {"paper": "PUB-CARE-DELIVERY",
     "evidence": SRC["cd3"] + " -> coverage_matrix (17 keys)"},
]
CITE_EXTRA = {
    "bishop2019": [{"paper": "PUB-LOCOREGIONAL",
                    "evidence": SRC["loco"] + " -> arm_level_event_ledger[0]"}],
    "masunaga2025": [
        {"paper": "PUB-LOCOREGIONAL",
         "evidence": SRC["loco"] + " -> arm_level_event_ledger[1]"},
        {"paper": "PUB-REPURPOSING (reference [4])",
         "evidence": SRC["rep2"] + " -> §1 sweep table, row [4]"}],
    "huang2023": [
        {"paper": "PUB-REPURPOSING (reference [2])",
         "evidence": SRC["rep3"] + " -> §2, row [2]"}],
}

# Rows whose EMC n is additionally traceable to a verbatim primary-text quote.
PRIMARY_QUOTE = {
    "huang2023": (
        58,
        '"fluorescence in situ hybridization was performed to confirm 58 EMCs, '
        'with 48 available for pan-Trk immunostaining and KIT sequencing."',
        SRC["rep3"] + " -> §2, row [2], quoting the PubMed abstract of "
                      "PMID 36948401",
        "abstract of the primary (no PMC body text exists)"),
    "masunaga2025": (
        134,
        '"Of the 24 patients who received (neo)adjuvant radiotherapy, two '
        '(8.3%) experienced local recurrence, and of the 110 patients who did '
        'not receive (neo)adjuvant radiotherapy, 14 (12.7%) experienced local '
        'recurrence."',
        SRC["loco"] + " -> arm_level_event_ledger[1].how_the_split_is_known",
        "PMC12398172 Results body text, read by LOCOREGIONAL-2 "
        "(this is the 134-patient non-metastatic analysed subset, "
        "NOT the 171 headline)"),
}

for sid, c in ipd_by_id.items():
    ovr = OVERLAP_CLEAR.get(sid)
    if ovr is None:
        overlap_unknown = True
        ovr_quote = json.dumps(c.get("overlap_risk"), ensure_ascii=False)
        ovr_from = SRC["ipd"] + f" -> candidate_sources[{sid}].overlap_risk"
        if c.get("overlap_risk") is None:
            ovr_quote = "null (no overlap_risk field value)"
    else:
        overlap_unknown, ovr_quote, ovr_from = ovr

    emc = EMC_N.get(sid)
    if emc:
        n_emc = emc["n_emc"]
        n_emc_status = "reported"
        n_emc_quote = emc["quote"]
        n_emc_from = emc["quoted_from"]
        headline_not_emc = emc["headline_is_not_emc"]
    else:
        n_emc = None
        n_emc_status = "UNKNOWN"
        n_emc_quote = None
        n_emc_from = None
        headline_not_emc = "UNKNOWN"

    rc = RETRIEVAL.get(sid)
    if rc:
        rcv, rcq, rcf, rcl = rc
    else:
        ft = c.get("full_text_reachable")
        rcv = "unread"
        rcq = ('"full_text_reachable": ' + json.dumps(ft, ensure_ascii=False)
               + " -- no lane in this campaign recorded reading its body text")
        rcf = SRC["ipd"] + f" -> candidate_sources[{sid}].full_text_reachable"
        rcl = None
    if sid == "masunaga2025":
        rcv = "partial"
        rcq = ('LOCOREGIONAL-2 read the PMC12398172 full text and quotes its '
               'Results body text; "Figure 2 was not read for numbers and '
               'carries no numbers-at-risk table in the retrieved text."')
        rcf = SRC["loco"] + " -> _forbidden_move_not_made / _retrieval_provenance"
        rcl = "LOCOREGIONAL-2"
    if sid == "bishop2019":
        rcv = "unread"
        rcq = ('"NOT re-verified against the paper in this lane; transcription '
               'fidelity is inherited."')
        rcf = (SRC["loco"] +
               " -> arm_level_event_ledger[0].how_the_split_is_known")
        rcl = None

    pq = PRIMARY_QUOTE.get(sid)
    row(
        row_id=sid,
        identifier={
            "source_id": sid,
            "pmcid": c.get("full_text_reachable"),
            "kind": "EMC clinical series (portfolio candidate source)",
        },
        n_headline_as_reported=c.get("n"),
        n_headline_quote=(f'"n": {c.get("n")}'),
        n_headline_quoted_from=SRC["ipd"] + f" -> candidate_sources[{sid}].n",
        n_headline_provenance_depth=(
            "curated field in a repository artifact; NOT re-quoted from the "
            "primary in this index"),
        n_emc_patients_as_reported=n_emc,
        n_emc_status=n_emc_status,
        n_emc_quote=n_emc_quote,
        n_emc_quoted_from=n_emc_from,
        headline_n_is_not_emc_n=headline_not_emc,
        n_verbatim_primary_quote=(
            None if pq is None else
            {"n": pq[0], "quote": pq[1], "quoted_from": pq[2], "scope": pq[3]}),
        citing_papers=CITE_ALL17 + CITE_EXTRA.get(sid, []),
        retrieval_completeness=rcv,
        retrieval_completeness_quote=rcq,
        retrieval_completeness_quoted_from=rcf,
        read_by_lane=rcl,
        overlap_unknown=overlap_unknown,
        overlap_quote=ovr_quote,
        overlap_quoted_from=ovr_from,
    )

# --------------------------- B. cited references not in the 17-series list
def refrow(rid, ref, cite_ev, n_head, n_head_q, n_head_f, n_emc, n_emc_st,
           n_emc_q, n_emc_f, rc, rc_q, rc_f, lane, ovr, ovr_q, ovr_f,
           headline_not_emc, pmcid=None, note=None):
    row(
        row_id=rid,
        identifier={"source_id": rid, "pmcid": pmcid,
                    "kind": "cited reference of the repurposing manuscript"
                            f" (reference {ref})"},
        n_headline_as_reported=n_head,
        n_headline_quote=n_head_q,
        n_headline_quoted_from=n_head_f,
        n_headline_provenance_depth="verbatim quote in a named lane artifact",
        n_emc_patients_as_reported=n_emc,
        n_emc_status=n_emc_st,
        n_emc_quote=n_emc_q,
        n_emc_quoted_from=n_emc_f,
        headline_n_is_not_emc_n=headline_not_emc,
        n_verbatim_primary_quote=None,
        citing_papers=[{"paper": "PUB-REPURPOSING (reference %s)" % ref,
                        "evidence": cite_ev}],
        retrieval_completeness=rc,
        retrieval_completeness_quote=rc_q,
        retrieval_completeness_quoted_from=rc_f,
        read_by_lane=lane,
        overlap_unknown=ovr,
        overlap_quote=ovr_q,
        overlap_quoted_from=ovr_f,
        note=note,
    )


R2 = SRC["rep2"]
R3 = SRC["rep3"]
CB = SRC["cabo"]

refrow("osullivanCoyne2022", "[19]", CB + " -> §3",
       55, '"Extraskeletal myxoid chondrosarcoma  3" (of 54 evaluable, '
           '55 enrolled)', CB + " -> §3, quoting PMC8776602 Table 1",
       3, "reported",
       '"Extraskeletal myxoid chondrosarcoma  3"',
       CB + " -> §3, quoting PMC8776602 Table 1 Diagnosis",
       "complete",
       'Table 1 and Results both returned and quoted verbatim from the PMC '
       'full text (PMC8776602).',
       CB + " -> §3", "PUB-REPURPOSING",
       True,
       'phase II refractory soft-tissue sarcoma trial; whether its 3 EMC '
       'patients also appear in any other row of this index is not stated in '
       'any source file read here',
       "not stated in any named source file",
       True, pmcid="PMC8776602")

refrow("davis2017", "[5]", R2 + " -> §2 H1",
       None, "UNKNOWN -- no cohort size is quoted in any source file read here",
       "n/a",
       None, "UNKNOWN",
       'the only patient-level figure quoted is n=1: "In our EMC cohort, one '
       'patient with diabetes mellitus was treated with an antidiabetic agent, '
       'pioglitazone..."; separately "Of 10 patients treated, 8 patients who '
       'showed clinical benefit ... harbored the [EWSR1-NR4A3] translocation"',
       R2 + " -> §2 H1 and §2 H3",
       "partial",
       '"[5] Davis 2017, NGS of EMC | **yes**, PMC5400622"',
       R2 + " -> §1 sweep table, row [5]", "REPURPOSING-2",
       True,
       'the "10 patients treated" sunitinib figure is quoted from [4], [5] and '
       '[6] alike in REPURPOSING-2 §2 H3 -- the same 10 patients may be the '
       'stacchiotti2014sunitinib row',
       R2 + " -> §2 H3", "UNKNOWN", pmcid="PMC5400622")

refrow("urbini2018", "[6]", R2 + " -> §2 H2",
       None,
       'the citing manuscript characterises it as "1 of 20 EMCs in one series"; '
       'that 20 is the CITING paper\'s wording, not a figure quoted from the '
       'primary in any source file read here',
       SRC["ms_rep"] + " §1.1 line 163, as quoted in " + R2 + " -> §2 H2",
       1, "reported",
       '"The EMC patient with a [KIT] exon 11 mutation described here never '
       'received imatinib. ... Interestingly the same patient had been treated '
       'with sunitinib with a prolonged response."',
       R2 + " -> §2 H2, quoting PMC6073125",
       "partial",
       '"[6] Urbini 2018 ... | **yes**, PMC6073125"',
       R2 + " -> §1 sweep table, row [6]", "REPURPOSING-2",
       True,
       '"we reported the therapeutic activity of sunitinib in a cohort of 10 '
       'EMC patients with 6 partial responses, 2 stable disease, and 2 showed '
       'progression." -- the same 10-patient sunitinib cohort is quoted from '
       '[4], [5] and [6]',
       R2 + " -> §2 H3", "UNKNOWN", pmcid="PMC6073125")

refrow("giner2023", "[8]", R3 + " -> §2, row [8]",
       31, '"We studied 31 cases confirmed as EMC. Clinical and follow-up data '
           'were recorded."',
       R3 + " -> §2, row [8], quoting the PubMed abstract of PMID 36376703",
       31, "reported",
       '"We studied 31 cases confirmed as EMC."',
       R3 + " -> §2, row [8]",
       "unread",
       '"Abstract only. No PMC record by either mode. The per-case '
       'clinicopathological table ... is unread."',
       R3 + " -> §2, row [8], retrieval completeness column", "REPURPOSING-3",
       True,
       'a 31-case Spanish EMC series; no source file read here states whether '
       'its cases are distinct from any other row',
       "not stated in any named source file", False,
       note="REPURPOSING-3 §1: this reference has NO PubMed Central record at "
            "all, so its per-patient table is UNREAD, not absent. Its EMC n is "
            "known from the abstract; everything below the abstract is not.")

refrow("iwata2025", "[14]", R3 + " -> §2, row [14]",
       1, '"We successfully developed the NCC-EMC1-C1 cell line using '
          'surgically resected tumor tissue from a patient with EMC."',
       R3 + " -> §2, row [14], quoting the PubMed abstract of PMID 40580361",
       1, "reported",
       '"...tumor tissue from a patient with EMC."',
       R3 + " -> §2, row [14]",
       "unread",
       '"Abstract only. No PMC record by either mode. All IC50 values, the '
       'drug roster and the donor patient\'s clinical record are in '
       'tables/figures and are unread."',
       R3 + " -> §2, row [14]", "REPURPOSING-3",
       True,
       'one tissue donor; no source file read here states whether that donor '
       'is also counted in another series',
       "not stated in any named source file", False,
       note="One EMC patient, as a tissue donor. Enters the index as a "
            "patient the evidence rests on, with UNKNOWN body text.")

refrow("bangerter2023", "[13]", R2 + " -> §1 sweep table, row [13]",
       2, '"[13] Bangerter 2023, two ex-vivo EMC models"',
       R2 + " -> §1 sweep table, row [13]",
       2, "reported",
       '"Donors of both ex-vivo EMC models received surgery, radiotherapy and '
       'cryoablation only -- no systemic candidate agent"',
       R2 + " -> §3, adjacent-records table",
       "partial",
       '"**yes**, PMC9813045"',
       R2 + " -> §1 sweep table, row [13]", "REPURPOSING-2",
       True,
       'two model donors; no source file read here states whether either donor '
       'appears in another series',
       "not stated in any named source file", False)

refrow("higuchi2023zaltoprofen", "[12]", R3 + " -> §2, row [12]",
       0, '"No human patient of any kind. Preclinical throughout."',
       R3 + " -> §2, row [12]",
       0, "reported",
       '"No human patient of any kind. Preclinical throughout."',
       R3 + " -> §2, row [12]",
       "unread",
       '"Abstract only, despite a PMC record existing. full_text: \\"\\" '
       'reproducibly, in two id forms."',
       R3 + " -> §2, row [12]", "REPURPOSING-3",
       False,
       'no patients, so no patient can overlap',
       R3 + " -> §2, row [12]", False, pmcid="PMC10054153",
       note="A ZERO that is a MEASURED zero: the source is preclinical by "
            "design. This is the only zero in the index and it is not an "
            "untraceable row recorded as zero.")

refrow("chow2007", "[9]", R3 + " -> §2, row [9]",
       None, 'UNKNOWN. The abstract carries no cohort: "No EMC patient, no EMC '
             'treatment, no EMC outcome in the abstract. As a 2007 narrative '
             'review its body would carry no primary EMC patient data of its '
             'own in any case." ⛔ That is an expectation about a review, not a '
             'reading of its body, which is unread -- so this row is UNKNOWN, '
             'not zero.',
       R3 + " -> §2, row [9]",
       None, "UNKNOWN",
       'narrative review; carries no primary cohort of its own. Its body was '
       'not retrieved, so a primary cohort is not affirmatively excluded by '
       'reading.',
       R3 + " -> §2, row [9]",
       "unread",
       '"Abstract only. No PMC record by either mode."',
       R3 + " -> §2, row [9]", "REPURPOSING-3",
       True,
       'a review; any EMC patient it describes is another row\'s patient',
       R3 + " -> §2, row [9]", "UNKNOWN",
       note="Review article. Contributes no independent patients; if its body "
            "recounts EMC cases they are secondary reports of other rows.")

refrow("remiszewski2025", "[1]", R2 + " -> §1 sweep table, row [1]",
       None, "UNKNOWN -- a review; no cohort of its own is quoted anywhere "
             "read here",
       R2 + " -> §1 sweep table, row [1]",
       None, "UNKNOWN",
       'the pazopanib figures it carries are its own recount: "26 patients, 23 '
       'of whom met modified intention-to-treat criteria... Four patients '
       '(18% ...)"',
       R2 + " -> §2 H6",
       "partial",
       '"**yes**, PMC12504171"; but "that extraction demonstrably drops table '
       'contents and italic-marked gene tokens"',
       R2 + " -> §1 sweep table and §2 H3", "REPURPOSING-2",
       True,
       'a review recounting stacchiotti2019pazopanib (26/23) and the '
       '10-patient sunitinib series -- those are other rows\' patients',
       R2 + " -> §2 H3 and H6", "UNKNOWN", pmcid="PMC12504171",
       note="Review. Its quoted 26/23 pazopanib denominator is the "
            "stacchiotti2019pazopanib row (n=26) seen second-hand; it must "
            "not be counted as additional patients.")

refrow("maki2005bortezomib", "[21]", R2 + " -> §2 H5",
       None, "UNKNOWN -- no enrolment figure is quoted in any source file "
             "read here",
       R2 + " -> §2 H5",
       None, "UNKNOWN",
       '"Whether it enrolled an EMC patient stays unread"',
       R2 + " -> §2 H5",
       "unread",
       '"[21] Maki 2005 (PMID 15739208) has no PMCID. Its MeSH indexing goes '
       'no finer than \'Sarcoma\' / \'Soft Tissue Neoplasms\'."',
       R2 + " -> §2 H5", "REPURPOSING-2",
       True, 'unknown enrolment, so overlap is unknowable',
       R2 + " -> §2 H5", "UNKNOWN",
       note="⛔ THE ARCHETYPAL UNREAD ROW. n is UNKNOWN, never zero. "
            "CLAUDE.md §4.")

refrow("boklan2025carfilzomib", "[22]", R2 + " -> §2 H4",
       38, '"A total of 42 patients were screened, and 38 were treated '
           '(stratum A, 14; stratum B, 24)"',
       R2 + " -> §2 H4, quoting PMC12428389",
       None, "UNKNOWN",
       '"No occurrence of \'extraskeletal\', \'myxoid\', \'chondrosarcoma\' or '
       '\'EMC\' anywhere in the retrieved text." BUT: "the per-histology '
       'enrolment table is not carried in the retrievable full text, so this '
       'is a reading of the narrative, not of the diagnosis table."',
       R2 + " -> §2 H4",
       "partial",
       '"[22] full text retrieved" but "the per-histology enrolment table is '
       'not carried in the retrievable full text"',
       R2 + " -> §2 H4", "REPURPOSING-2",
       True,
       'its per-histology table is unread, so whether any of its 38 treated '
       'patients has EMC -- and whether such a patient appears elsewhere -- is '
       'unknown',
       R2 + " -> §2 H4", "UNKNOWN", pmcid="PMC12428389",
       note="⭐ The clearest UNREAD-not-absent row in the index: the narrative "
            "names no EMC patient, but the table that would say so was not "
            "returned. n_emc is UNKNOWN, not 0.")

# --------------------------------------------------------------- control
loco_led = {r["source_id"]: r for r in loco["arm_level_event_ledger"]}
control_rows = ["bishop2019", "masunaga2025"]
contrast_subsets = {}
for sid in control_rows:
    L = loco_led[sid]
    arms = L["arm_sizes"]
    evs = L["arm_events"]
    contrast_subsets[sid] = {
        "arm_sizes": arms,
        "arm_events": evs,
        "n_in_contrast": sum(arms.values()),
        "events_in_contrast": sum(evs.values()),
        "quoted_from": SRC["loco"] + " -> arm_level_event_ledger",
    }
    # attach to the row
    for r in ROWS:
        if r["row_id"] == sid:
            r["locoregional_contrast_subset"] = contrast_subsets[sid]

ctrl_n = sum(v["n_in_contrast"] for v in contrast_subsets.values())
ctrl_e = sum(v["events_in_contrast"] for v in contrast_subsets.values())
tgt_n = loco["crude_pooled_per_arm_proportions"]["total_patients_carrying_the_contrast"]
tgt_e = loco["crude_pooled_per_arm_proportions"][
    "total_counted_local_recurrence_events_carrying_the_contrast"]

control = {
    "_what": "LOCOREGIONAL-2's 21 local recurrences among 175 patients in two "
             "series, reproduced FROM THIS INDEX's rows.",
    "⛔_why_this_arithmetic_is_permitted_when_the_index_forbids_totals": (
        "It sums exactly two rows that a named source file rules "
        "non-overlapping FOR THIS CONTRAST: "
        + json.dumps(loco["pool_admissibility"]
                     ["2_1_4_and_2_3_non_overlapping_population"]["verdict"])
        + " -- " + json.dumps(loco["pool_admissibility"]
                              ["2_1_4_and_2_3_non_overlapping_population"]
                              ["binding_restriction"])
        + " It is a control on the index, not a portfolio patient count, and "
          "it is the ONLY addition performed anywhere in this artifact."),
    "rows_used": control_rows,
    "per_row": contrast_subsets,
    "reproduced_patients": ctrl_n,
    "reproduced_events": ctrl_e,
    "target_patients": tgt_n,
    "target_events": tgt_e,
    "patients_match": ctrl_n == tgt_n,
    "events_match": ctrl_e == tgt_e,
    "PASS": (ctrl_n == tgt_n and ctrl_e == tgt_e),
    "⚠_note": ("bishop2019's contrast n (41) equals its headline n; "
               "masunaga2025's contrast n (134) does NOT equal its headline n "
               "(171). The control reproduces because the index stores the "
               "contrast subset separately from the headline denominator."),
}

# ------------------------------------------------------------- accounting
counts = {
    "n_rows": len(ROWS),
    "by_retrieval_completeness": {},
    "by_n_emc_status": {},
    "rows_with_overlap_unknown_true": 0,
    "rows_with_overlap_unknown_false": 0,
    "rows_where_headline_n_is_not_emc_n": [],
    "rows_where_headline_vs_emc_relation_is_unknown": [],
}
for r in ROWS:
    counts["by_retrieval_completeness"][r["retrieval_completeness"]] = \
        counts["by_retrieval_completeness"].get(r["retrieval_completeness"], 0) + 1
    counts["by_n_emc_status"][r["n_emc_status"]] = \
        counts["by_n_emc_status"].get(r["n_emc_status"], 0) + 1
    if r["overlap_unknown"] is True:
        counts["rows_with_overlap_unknown_true"] += 1
    elif r["overlap_unknown"] is False:
        counts["rows_with_overlap_unknown_false"] += 1
    if r["headline_n_is_not_emc_n"] is True:
        counts["rows_where_headline_n_is_not_emc_n"].append(r["row_id"])
    elif r["headline_n_is_not_emc_n"] == "UNKNOWN":
        counts["rows_where_headline_vs_emc_relation_is_unknown"].append(r["row_id"])

# traceability gate: every row must name a source file for its n.
untraceable = [r["row_id"] for r in ROWS
               if not (r.get("n_emc_quoted_from") or r.get("n_headline_quoted_from"))]

out = {
    "_id": "EXPOSURE-INDEX-EMC-PATIENT-EXPOSURE-INDEX-2026-09-09",
    "_question": ("How many distinct EMC patients does this portfolio's cited "
                  "evidence actually rest on, and how much of that is UNREAD "
                  "rather than absent?"),
    "_what_this_answers_and_what_it_refuses": (
        "It answers the SECOND half and deliberately refuses the first. Every "
        "row carries its own n, its provenance and its retrieval state. NO "
        "TOTAL IS COMPUTED, because "
        f"{counts['rows_with_overlap_unknown_true']} of {len(ROWS)} rows carry "
        "overlap_unknown = true and a sum across them would be exactly the "
        "error this artifact exists to prevent."),
    "_not_medical_advice": (
        "This is a PROVENANCE INDEX, not evidence synthesis. Nothing here "
        "asserts or implies efficacy, safety, selectivity, a therapeutic "
        "window, prognosis, or any treatment recommendation, and nothing here "
        "is patient-specific advice. Counting who has been counted is not a "
        "statement about what happened to them."),
    "_lane": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
              "PORTFOLIO-INVESTIGATIONS-2026-09-08/EXPOSURE-INDEX"),
    "_generated_by": "build_exposure_index.py (this lane)",
    "_proposal": ("FOLLOWTHROUGH-DISCOVERY PROPOSALS.md P10 (rank 10), "
                  "proposed by REPURPOSING-2, refined by REPURPOSING-3 §6.4"),
    "_reads_only": {k: {"path": v, "sha256": sha(v)} for k, v in SRC.items()},
    "_no_new_retrieval": ("No PubMed/PMC call and no HTTP request was made by "
                          "this lane. Every quoted figure is copied from a "
                          "named file already in the repository; the retrieval "
                          "attribution belongs to the lane that made the call, "
                          "recorded per row in retrieval_completeness_quoted_from."),
    "_provenance_rule": (
        "CLAUDE.md §4. Every row's n names the file and pointer it was quoted "
        "from. A row whose n could not be traced is recorded UNKNOWN. "
        f"Untraceable rows recorded as zero: {len(untraceable)} "
        f"({untraceable}). The only 0 in the index is "
        "higuchi2023zaltoprofen, and it is a MEASURED zero (preclinical by "
        "design), not an untraced one."),
    "_three_valued_retrieval_completeness": {
        "complete": "a lane recorded narrative PLUS all tables returned",
        "partial": "body text returned, but tables, figures or the specific "
                   "table carrying the EMC denominator were not",
        "unread": "no body text of any kind was retrieved by any lane -- "
                  "abstract, MeSH and curated fields only. ⛔ UNREAD IS NOT "
                  "ABSENT.",
        "_field_origin": ("CARE-DELIVERY-3 invented retrieval_completeness "
                          "independently for its own coverage rows; "
                          "REPURPOSING-3 established the unread-vs-absent "
                          "distinction. This index unifies both."),
    },
    "⛔_stop_condition_enforced_in_code": {
        "no_pooling": True,
        "no_denominator_arithmetic_across_overlap_unknown_rows": True,
        "the_only_addition_performed": "the two-row LOCOREGIONAL-2 control, "
                                       "justified in control.⛔_why...",
        "⛔_do_not_add_these_rows": (
            "Do not sum n_headline_as_reported or n_emc_patients_as_reported "
            "across rows. The series overlap (Milan, US institutional/SEER, "
            "Japanese registry/trial clusters) AND two independent "
            "denominators are not EMC. A portfolio-wide patient total computed "
            "from this file would be wrong in both directions at once."),
    },
    "counts_of_rows_not_of_patients": counts,
    "control_locoregional2": control,
    "rows": ROWS,
}

with open(os.path.join(HERE, "emc-patient-exposure-index.json"), "w") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
    fh.write("\n")

print("rows:", len(ROWS))
print("retrieval_completeness:", counts["by_retrieval_completeness"])
print("n_emc_status:", counts["by_n_emc_status"])
print("overlap_unknown true:", counts["rows_with_overlap_unknown_true"],
      "false:", counts["rows_with_overlap_unknown_false"])
print("headline_n != emc_n:", counts["rows_where_headline_n_is_not_emc_n"])
print("headline-vs-emc UNKNOWN:", len(counts["rows_where_headline_vs_emc_relation_is_unknown"]))
print("untraceable rows recorded as zero:", untraceable)
print("CONTROL reproduced patients:", ctrl_n, "target", tgt_n,
      "| events:", ctrl_e, "target", tgt_e, "| PASS:", control["PASS"])
sys.exit(0 if control["PASS"] and not untraceable else 1)
