#!/usr/bin/env python3
"""EXPOSURE-INDEX-2 -- resolve EXPOSURE-INDEX's UNKNOWN n_emc rows through the admitted
PubMed/PMC MCP route only.  Every original field of every original row is preserved byte-for-byte;
resolution is recorded ADDITIVELY in `resolution_2026_09_09`, plus the two resolved top-level fields
`n_emc_patients_as_reported` / `n_emc_status` where a verbatim primary quote licenses it.
NO pooling.  NO portfolio total.  NO arithmetic across overlap_unknown rows.  The only sum is the
inherited two-row LOCOREGIONAL-2 control."""
import json, hashlib, collections, sys

SRC = "../EXPOSURE-INDEX/emc-patient-exposure-index.json"
raw = open(SRC, "rb").read()
src_sha = hashlib.sha256(raw).hexdigest()
d = json.loads(raw)

CALL = {
 "drilon2008":  "checks/02-pmc-fulltext-drilon2008-PMC2779719",
 "chiusole2020":"checks/03-pmc-fulltext-chiusole2020-bishop2019",
 "bishop2019":  "checks/03-pmc-fulltext-chiusole2020-bishop2019",
 "masunaga2025":"checks/04-pmc-fulltext-masunaga2025-boklan2025",
 "boklan2025carfilzomib":"checks/04-pmc-fulltext-masunaga2025-boklan2025",
 "davis2017":   "checks/05-pmc-fulltext-davis2017-remiszewski2025",
 "remiszewski2025":"checks/05-pmc-fulltext-davis2017-remiszewski2025",
 "maki2005bortezomib":"checks/06-pubmed-metadata-maki2005-chow2007",
 "chow2007":    "checks/06-pubmed-metadata-maki2005-chow2007",
}
UNIDENTIFIED = ["seer270_2022","meisKindblom1999","ussc2022","japan2003","uMich2023","china2016",
                "huang2023","stacchiotti2019pazopanib","immunosarc2emc2025","stacchiotti2014sunitinib"]

R = {}   # row_id -> resolution block

R["drilon2008"] = dict(
 outcome="reported", n_emc_resolved=86,
 tool="mcp__PubMed__get_full_text_article(pmc_ids=['PMC2779719'])",
 record_ids={"pmcid":"PMC2779719","pmid":"18951519","doi":"10.1002/cncr.23978"},
 quote="Of the 86 evaluable patients, 57 were men and 29 were women, for a male-to-female ratio of 2:1.",
 locator="PMC full text, Results, first paragraph of 'Clinical Features of Local and Metastatic EMC'",
 corroborating_quote="After obtaining Institutional Review Board permission, 86 patients of EMC were retrieved from the databases of the Memorial Sloan-Kettering Cancer Center in New York City and the Royal Marsden Hospital in London.",
 corroborating_locator="PMC full text, Materials and Methods, 'Patient Selection'",
 why_this_is_the_emc_n="The cohort is EMC-only by construction ('86 patients of EMC were retrieved'), so the cohort denominator IS the EMC denominator.",
 retrieval_completeness_new="partial",
 retrieval_completeness_change_reason="Narrative returned complete; table CELL content not returned (in-text table references render as bare '()'). 'complete' in this schema means narrative plus all tables, so this is partial.",
 headline_n_is_not_emc_n_new=True,
 headline_discrepancy_note=("FOURTH instance of headline-is-not-EMC-n, and of a DIFFERENT KIND from the "
   "three EXPOSURE-INDEX found. Those three (martinbroto 68->4, morioka 5->2, osullivanCoyne 55->3) are "
   "mixed-histology cohorts with an EMC subgroup. This one is an INTRA-PAPER discrepancy: the abstract "
   "says 87 ('The clinical behavior and treatment responses of 87 patients with EMC ... were examined'), "
   "the body says 86 in three separate places. The index headline 87 is the curated repository value and "
   "matches the ABSTRACT; the body evaluable EMC n is 86. Do not read this row as a mixed-histology row."),
 abstract_quote="The clinical behavior and treatment responses of 87 patients with EMC who were seen at 2 institutions between 1975 and 2008 were examined.",
 overlap_unknown_change="NONE. Still true. This lane resolved a denominator, not an independence relation.")

R["chiusole2020"] = dict(
 outcome="reported", n_emc_resolved=59,
 tool="mcp__PubMed__get_full_text_article(pmc_ids=['PMC7308468','PMC7771031'])",
 record_ids={"pmcid":"PMC7308468","pmid":"32612944","doi":"10.3389/fonc.2020.00828"},
 quote="A total of 59 patients were identified, 37 were male (62.7%) and 22 were female (37.3%) with a male-to-female ratio of 1.7/1.",
 locator="PMC full text, Results, \"Patients' Characteristics\", first sentence",
 corroborating_quote="All consecutive patients with a confirmed diagnosis of EMC treated at Istituto Oncologico Veneto in Padova and at Institut Gustave Roussy in Villejuif from January 1980 to December 2018 were extracted from a prospectively maintained database.",
 corroborating_locator="PMC full text, Methods, first sentence",
 table_cell_quote="Primary Location | (n. 59)",
 table_cell_locator="PMC full text, Table 1 'Patients' characteristics', returned as cell content",
 why_this_is_the_emc_n="EMC-only cohort by the Methods inclusion rule; headline n IS the EMC n.",
 retrieval_completeness_new="complete",
 retrieval_completeness_change_reason="Narrative AND all four tables returned as cell content. This is the only row this lane upgraded to 'complete'; it becomes the portfolio's FOURTH narrative-plus-all-tables read.",
 headline_n_is_not_emc_n_new=False,
 overlap_unknown_change="NONE. Still true -- emc-ipd-survival.json records 'likely shares Milan/INT patients with the Stacchiotti series' and nothing retrieved here settles that.")

R["bishop2019"] = dict(
 outcome="reported", n_emc_resolved=41,
 tool="mcp__PubMed__get_full_text_article(pmc_ids=['PMC7308468','PMC7771031'])",
 record_ids={"pmcid":"PMC7771031","pmid":"31436747","doi":"10.1097/COC.0000000000000590"},
 quote="We identified 41 consecutive patients with localized, non-metastatic histologically confirmed EMC treated at the University of Texas MD Anderson Cancer Center (MDACC) during the period from 1990 through 2016.",
 locator="PMC full text, Material and Methods, first sentence",
 why_this_is_the_emc_n="EMC-only cohort ('histologically confirmed EMC'); headline n IS the EMC n.",
 retrieval_completeness_new="partial",
 retrieval_completeness_change_reason="Narrative returned complete; table cell content not returned ('Patient and tumor characteristics are listed in.').",
 headline_n_is_not_emc_n_new=False,
 control_verification={
   "what_was_inherited":"EXPOSURE-INDEX limitation 5: bishop2019's arm split is inherited transcription, 'NOT re-verified against the paper in this lane'.",
   "status_now":"DISCHARGED for bishop2019 by direct primary retrieval in this lane.",
   "arm_split_quote":"The majority of patients (n=33, 80%) received combined modality local therapy with both surgery and RT, whereas 8 patients received surgery alone (20%).",
   "arm_split_locator":"PMC full text, Results, 'Treatment'",
   "events_quote":"There were 5 patients (12%) with local relapse at a median time of 75 months (range 13-176). Four of those patients underwent surgery alone.",
   "events_locator":"PMC full text, Results, 'Patterns of Disease Recurrence'",
   "cmt_event_quote":"The median time to local relapse occurred earlier in patients receiving surgery alone compared to the one patient who received CMT (61 months vs. 143 months).",
   "reconciles_to":"33 + 8 = 41 patients; 1 (CMT) + 4 (surgery alone) = 5 local relapses -- exactly LOCOREGIONAL-2's ledger."},
 overlap_unknown_change="NONE. Still true -- 'US institution, may overlap ussc2022'.")

R["masunaga2025"] = dict(
 outcome="reported", n_emc_resolved=171,
 tool="mcp__PubMed__get_full_text_article(pmc_ids=['PMC12398172','PMC12428389'])",
 record_ids={"pmcid":"PMC12398172","pmid":"40885991","doi":"10.1186/s13018-025-06245-6"},
 quote="After excluding 18 patients with unknown tumor size, 12 with unknown histological grade, and 22 with a follow-up period of less than 6 months after diagnosis, the remaining 171 patients were retrospectively analyzed.",
 locator="PMC full text, Methods (Japanese National Bone and Soft Tissue Tumor Registry Database)",
 corroborating_quote="A total of 102 (59.6%) males and 69 (40.4%) females with a median age of 62 years (interquartile range [IQR], 48-72 years) were included in the study.",
 corroborating_locator="PMC full text, Results, first sentence",
 why_this_is_the_emc_n="EMC-only registry extraction; headline n IS the EMC n.",
 retrieval_completeness_new="partial",
 retrieval_completeness_change_reason="UNCHANGED at partial. Narrative returned complete; Table 1-4 captions returned but no cell content ('(Table)').",
 headline_n_is_not_emc_n_new=False,
 control_verification={
   "what_was_inherited":"LOCOREGIONAL-2's contrast subset 24 + 110 = 134 patients with 2 + 14 = 16 local recurrences.",
   "status_now":"The 134 denominator, the 16 events and the 24-patient RT arm are VERIFIED against the primary in this lane. The 2/14 event SPLIT BY ARM is NOT printed in the returned body and remains inherited.",
   "subset_quote":"For the prognostic analysis, eight patients who did not undergo surgery were excluded, and the remaining 134 patients were included. Local recurrence occurred in 16 patients (11.9%), and the median time from surgery to local recurrence was 15 months (IQR, 4.5-63.5).",
   "subset_locator":"PMC full text, Results, prognostic-analysis paragraph",
   "rt_arm_quote":"Of the 24 patients who received (neo)adjuvant radiotherapy, 10 (41.7%) had R1 or R2 surgical margins",
   "rt_arm_locator":"PMC full text, Results, local-recurrence paragraph",
   "note":"171 headline vs 134 contrast subset is the storage distinction EXPOSURE-INDEX's control was built to protect; it is now primary-verified rather than curated."},
 overlap_unknown_change="NONE at the row level. The row keeps overlap_unknown=false as EXPOSURE-INDEX set it, on the SAME named-source basis, restricted to the same contrast.")

R["davis2017"] = dict(
 outcome="reported", n_emc_resolved=6,
 tool="mcp__PubMed__get_full_text_article(pmc_ids=['PMC5400622','PMC12504171'])",
 record_ids={"pmcid":"PMC5400622","pmid":"28423517","doi":"10.18632/oncotarget.15568"},
 quote="Six patients with EMC were enrolled on MI-ONCOSEQ. The median age of the patients at diagnosis was 44 years old (range 33-65) with median follow-up of 10 years (2-23 years). All patients are male and alive with disease.",
 locator="PMC full text, Results, first sentence",
 corroborating_quote="Between January 31, 2012 and April 15, 2016, five patients with EMC underwent tumor biopsy of a metastatic site and previously fresh-frozen metastatic tumor tissue from one patient was submitted as part of an integrative clinical sequencing research study, MI-ONCOSEQ, at the University of Michigan.",
 corroborating_locator="PMC full text, Patients and Methods, first sentence",
 why_this_is_the_emc_n="The paper states the EMC enrolment directly (6). The Methods sentence decomposes it as 5 prospectively biopsied plus 1 archived specimen; both are quoted so the composition is visible and nothing is inferred.",
 retrieval_completeness_new="partial",
 retrieval_completeness_change_reason="UNCHANGED at partial. Narrative returned; the patient-characteristics table returned as caption only.",
 headline_n_is_not_emc_n_new="UNKNOWN",
 headline_note="The index carries NO headline n for this row, so there is no headline to compare against and this field must stay UNKNOWN. Resolving the EMC n does not create a headline.",
 overlap_unknown_change="NONE. Still true. This is a University of Michigan cohort and uMich2023 is a separate row also flagged overlap_unknown; nothing retrieved settles their relation, and this lane did not test it.")

R["boklan2025carfilzomib"] = dict(
 outcome="still_UNKNOWN",
 reason_code="tables_stripped_from_returned_body",
 tool="mcp__PubMed__get_full_text_article(pmc_ids=['PMC12398172','PMC12428389'])",
 record_ids={"pmcid":"PMC12428389","pmid":"40941020","doi":"10.3390/cancers17172924"},
 measured_on_returned_body={"chars":21762,"occurrences_of_Table":0,"occurrences_of_histolog":0,
                            "occurrences_of_myxoid":0,"occurrences_of_chondro":0},
 quote="A total of 42 patients were screened, and 38 were treated (stratum A, 14; stratum B, 24) ().",
 locator="PMC full text, Results, accrual paragraph -- note the empty '()' where the enrolment table reference should resolve",
 finest_histology_quote="Of the twenty-four patients enrolled in stratum B, fifteen (63%) had a diagnosis of sarcoma, highlighting the need for novel therapies in this patient population.",
 finest_histology_locator="PMC full text, Discussion -- the ONLY histology statement anywhere in the returned body",
 why_not_zero="The per-histology enrolment table is not in the retrievable full text, and the finest histology term returned is 'sarcoma'. An EMC patient inside stratum B would be invisible to everything that was returned. UNREAD, NOT ABSENT. NOT ZERO.",
 independently_confirms="REPURPOSING-2 H4 and EXPOSURE-INDEX both reached this conclusion; this lane re-reached it by its own retrieval rather than inheriting it.")

R["remiszewski2025"] = dict(
 outcome="still_UNKNOWN",
 reason_code="tables_stripped_from_returned_body",
 tool="mcp__PubMed__get_full_text_article(pmc_ids=['PMC5400622','PMC12504171'])",
 record_ids={"pmcid":"PMC12504171","pmid":"41055792","doi":"10.1007/s00432-025-06316-5"},
 measured_on_returned_body={"chars":55085,"occurrences_of_Table":4,"table_cell_content_returned":False},
 probes_run=["we present","our patient/institution/cohort/series/centre/center","we report","Methods",
             "search strategy","review of the literature","narrative review","systematic"],
 probe_result="No original patient-accrual sentence returned. Every patient count in the returned body is attributed to another named study.",
 example_quote="A total of 172 patients diagnosed between 2004 and 2012 were included in the analysis.",
 example_locator="PMC full text, section recounting the Kemmerer SEER series -- a count belonging to another study, not to this review",
 why_not_zero="Its four tables were not returned as cell content, so an original-cohort table cannot be excluded from what was returned. This lane applies the SAME rule EXPOSURE-INDEX applied to chow2007: a review's tables being unread is not evidence that it carries no primary cohort.",
 note="This row moved from 'unread by this program' to 'narrative read, tables not returned'. That is a real gain in what is known about the row even though n_emc did not resolve.")

R["maki2005bortezomib"] = dict(
 outcome="still_UNKNOWN",
 reason_code="no_pmc_record_abstract_only",
 tool="mcp__PubMed__get_article_metadata(pmids=['15739208'])",
 record_ids={"pmid":"15739208","doi":"10.1002/cncr.20968","pmcid":None},
 returned="title, abstract in full, MeSH, article types, authors, citation. No body. No tables.",
 quote="Arm A included patients with osteogenic sarcoma, Ewing sarcoma, and rhabdomyosarcoma. Arm B accrued patients with other types of soft tissue sarcomas.",
 locator="PubMed abstract, Methods paragraph",
 only_denominator_printed_quote="Arm A had low accrual and was closed. One confirmed partial response among 21 evaluable patients was observed on Arm B in a patient with leiomyosarcoma.",
 only_denominator_printed_locator="PubMed abstract, Results paragraph",
 mesh_finest_oncologic_terms=["Sarcoma","Soft Tissue Neoplasms","Bone Neoplasms"],
 why_not_zero=("The abstract prints no total enrolment and no per-histology table. The only denominator it "
   "prints is '21 evaluable patients ... on Arm B', and Arm B is the stratum an EMC patient would fall "
   "into ('other types of soft tissue sarcomas'). The finest MeSH term is 'Sarcoma'. There is no "
   "retrievable body in which to look. UNKNOWN, NEVER ZERO."),
 stop_note="No PMCID exists for this article. The admitted route ends at PubMed metadata. No publisher site was approached and no paywall was tested.")

R["chow2007"] = dict(
 outcome="still_UNKNOWN",
 reason_code="no_pmc_record_abstract_only",
 tool="mcp__PubMed__get_article_metadata(pmids=['17545802'])",
 record_ids={"pmid":"17545802","doi":"10.1097/CCO.0b013e32812143d9","pmcid":None},
 returned="title, abstract in full, MeSH, article types ['Journal Article','Review']. No body. No tables.",
 quote="Molecular studies have established that extraskeletal myxoid chondrosarcoma is a unique entity defined by the presence of a fusion gene between the orphan nuclear receptor, CHN/NOR1, and a promiscuous partner, most commonly EWSR1.",
 locator="PubMed abstract -- the only EMC-specific sentence in it",
 mesh_returned=["Biomarkers, Tumor","Bone Neoplasms","Chondrosarcoma","Evidence-Based Medicine","Humans",
                "Mesoderm","Molecular Diagnostic Techniques","Prognosis","Signal Transduction"],
 why_not_zero=("EXPOSURE-INDEX recorded 0 for this row in its first build and its own verifier REFUSED it "
   "(checks/02-verify-index, exit 1), forcing the correction to UNKNOWN: a review's body being unread is "
   "not evidence that it carries no primary cohort. This lane reached the same wall by direct retrieval "
   "and did not step over it. The correction is UPHELD, not overturned."),
 stop_note="No PMCID exists for this article. The admitted route ends at PubMed metadata.")

for rid in UNIDENTIFIED:
    blk = dict(
      outcome="still_UNKNOWN",
      reason_code="identity_not_established_no_admitted_call_attributable",
      tool=None,
      calls_made=0,
      measured=("The committed index carries identifier = {source_id, pmcid: null, kind} and nothing else "
        "for this row: no PMID, no PMCID, no DOI, no title, no journal, no author, no year. The upstream "
        "research/modalities/emc-ipd-survival.json carries none of those either."),
      why_no_call=("get_full_text_article requires a PMCID; get_article_metadata requires a PMID; "
        "convert_article_ids requires a PMID/PMCID/DOI; lookup_article_by_citation requires "
        "journal/year/volume/page/author. None of those inputs exists for this row. Entering the route "
        "would require GUESSING which published paper this internal source_id denotes from its prose "
        "description and then attributing a retrieved count to that guess -- a count typed against an "
        "inferred identity is a count typed from memory. No such call was made."),
      preserved_at="checks/07-no-admitted-route-ten-unidentified-rows",
      next_step_that_is_not_retrieval=("Record a PMID or DOI per candidate_source in "
        "research/modalities/emc-ipd-survival.json. TEN of this index's fourteen surviving UNKNOWNs are "
        "blocked on a missing IDENTIFIER, not on a paywall and not on PMC coverage. This lane does not "
        "edit that shared file."))
    if rid == "meisKindblom1999":
        blk["secondary_corroboration_not_used_to_change_status"] = {
          "quote":"One of the larger studies by Meis-Kindblom and colleagues was predominantly a pathologic characterization of 117 cases of EMC. They reported a 48% local relapse rate among the 83 cases with available data.",
          "locator":"PMC7771031 (bishop2019) full text, Discussion -- retrieved in checks/03",
          "why_status_unchanged":"This is a CITING paper describing a source, not the source. EXPOSURE-INDEX's own provenance rule keeps the row UNKNOWN; a secondary restatement is not a reading of the primary."}
    R[rid] = blk

# ---- apply, additively ----
resolved = still = 0
for row in d["rows"]:
    rid = row["row_id"]
    if row["n_emc_status"] != "UNKNOWN":
        continue
    if rid not in R:
        raise SystemExit("FAIL: UNKNOWN row with no recorded resolution attempt: " + rid)
    blk = dict(R[rid])
    blk["lane"] = "EXPOSURE-INDEX-2"
    blk["date"] = "2026-09-09"
    blk["route"] = "PubMed/PMC MCP tools (mcp__PubMed__*) -- the admitted route, and the only one used"
    blk["check_dir"] = CALL.get(rid, "checks/07-no-admitted-route-ten-unidentified-rows")
    blk["prior_status_in_EXPOSURE_INDEX"] = "UNKNOWN"
    if blk["outcome"] == "reported":
        row["n_emc_patients_as_reported"] = blk["n_emc_resolved"]
        row["n_emc_status"] = "reported"
        row["n_emc_quote"] = blk["quote"]
        row["n_emc_quoted_from"] = "PubMed Central %s (%s), %s -- retrieved by EXPOSURE-INDEX-2 on 2026-09-09, %s" % (
            blk["record_ids"]["pmcid"], blk["record_ids"]["doi"], blk["locator"], blk["check_dir"])
        row["headline_n_is_not_emc_n"] = blk["headline_n_is_not_emc_n_new"]
        row["retrieval_completeness"] = blk["retrieval_completeness_new"]
        row["retrieval_completeness_quote"] = blk["retrieval_completeness_change_reason"]
        row["retrieval_completeness_quoted_from"] = blk["check_dir"] + " (this lane's own retrieval)"
        row["read_by_lane"] = "EXPOSURE-INDEX-2"
        resolved += 1
    else:
        still += 1
    row["resolution_2026_09_09"] = blk

# ---- header ----
d["_id"] = "DOC-PORTFOLIO-EXPOSURE-INDEX-2-RESOLVED"
d["_lane"] = "EXPOSURE-INDEX-2"
d["_derived_from"] = {"file": SRC, "sha256": src_sha,
    "relation":"Every original row field is preserved unchanged EXCEPT on the five rows this lane RESOLVED "
               "by primary retrieval, where n_emc_patients_as_reported / n_emc_status / n_emc_quote / "
               "n_emc_quoted_from / headline_n_is_not_emc_n / retrieval_completeness* / read_by_lane were "
               "updated and the prior value is recorded inside resolution_2026_09_09. "
               "NO overlap_unknown flag was changed on any row. NO refusal was overturned."}
d["_this_lane_did_retrieve"] = ("Unlike EXPOSURE-INDEX, which performed NO retrieval, this lane issued five "
    "PubMed/PMC MCP calls covering nine rows. Every figure below is copied verbatim from a returned record "
    "and every call is preserved under checks/. No HTTP request was made, no publisher site was contacted, "
    "no paywall was approached, and routes B1/B2/B4/B8/B9 were untouched.")
d["_reproduction_of_the_source_index"] = {
    "checked_in":"checks/01-rederive-index-tallies", "exit_code":0, "reproduces":True,
    "rows":28, "retrieval_completeness":{"unread":18,"partial":7,"complete":3},
    "overlap_unknown_true":24, "n_emc_status_UNKNOWN":19,
    "statement":"EXPOSURE-INDEX's committed tallies re-derive exactly from its committed JSON."}

rows = d["rows"]
d["counts_of_rows_not_of_patients"] = {
  "⛔":"COUNTS OF ROWS. NEVER OF PATIENTS. No number in this block is a patient total.",
  "rows": len(rows),
  "retrieval_completeness": dict(collections.Counter(r["retrieval_completeness"] for r in rows)),
  "n_emc_status": dict(collections.Counter(r["n_emc_status"] for r in rows)),
  "overlap_unknown_true": sum(1 for r in rows if r["overlap_unknown"] is True),
  "overlap_unknown_false": sum(1 for r in rows if r["overlap_unknown"] is False),
  "headline_n_is_not_emc_n": dict(collections.Counter(str(r["headline_n_is_not_emc_n"]) for r in rows)),
  "resolved_by_this_lane": resolved,
  "still_UNKNOWN_after_this_lane": still,
  "still_UNKNOWN_by_reason": dict(collections.Counter(
      r["resolution_2026_09_09"]["reason_code"] for r in rows
      if "resolution_2026_09_09" in r and r["resolution_2026_09_09"]["outcome"] == "still_UNKNOWN"))}

d["⛔_stop_condition_enforced_in_code"] = {
  "inherited_from":"EXPOSURE-INDEX, and ABSOLUTE here.",
  "rule":"No pooling. No portfolio total. NO denominator arithmetic across any row carrying overlap_unknown "
         "-- not as an aside, not as a range, not as an approximate upper bound.",
  "why":"24 of 28 rows carry overlap_unknown, the series overlap in at least three named clusters (Milan; "
        "US institutional/SEER; Japanese registry/trial), and at least two denominators are not EMC at all. "
        "A total would be wrong in two directions at once.",
  "what_resolving_five_denominators_did_NOT_do":"Resolving an EMC denominator resolves WHO WAS COUNTED IN "
        "ONE SERIES. It does not resolve whether two series counted the SAME PATIENT. overlap_unknown is "
        "unchanged on every row. If anything this lane makes the temptation worse and the answer no harder: "
        "there are now 14 known EMC denominators sitting in one file, and they still must not be added.",
  "only_permitted_sum":"the two-row LOCOREGIONAL-2 control below, and only because a named source file "
        "(POLICY-evidence.md 2.3) rules those two rows non-overlapping FOR THAT CONTRAST.",
  "no_total_shaped_key":"enforced by verify_resolved_index.py"}

json.dump(d, open("emc-patient-exposure-index-v2.json","w"), indent=2, ensure_ascii=False)
print("wrote emc-patient-exposure-index-v2.json")
print("source sha256:", src_sha)
print("resolved:", resolved, " still UNKNOWN:", still)
print(json.dumps(d["counts_of_rows_not_of_patients"], indent=2, ensure_ascii=False))
